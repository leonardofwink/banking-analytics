# -*- coding: utf-8 -*-
"""S13.6 · A política sob o piso — maximizar ROI com os 15% como guard-rail.

O erro raiz do desafio, segundo o professor, foi varrer 5.600 combinações de
política sobre uma premissa errada e concluir que a meta era inalcançável. A
premissa agora está **calibrada contra a apuração** (S13.5), e esta varredura
refaz a busca com ela.

**O que muda em relação ao S09 e ao S12:**

* **O critério.** Antes: viável nos três cenários, desempate por folga. Agora:
  **maior ROI sujeito aos cinco limites** — os quatro do enunciado mais os 15%.
  Quando o conjunto ficou vazio, foi a exigência do cliente que cedeu; não cede
  mais. Registrado em ``PRD.md § Decisões de modelagem``, D2.
* **A premissa.** ``PREMISSAS_CALIBRADAS`` no lugar dos três cenários inventados.
* **Uma alavanca nova.** ``prazo_como_teto``: o enunciado diz *"Prazo máx."* e
  dos três grupos só o nosso tratou como valor fixo.

⚠️ **O teste de estresse mudou de natureza.** Não há mais "cenário pessimista"
inventado: a política escolhida é reportada nas **bordas do que o dado
sustenta**, que vieram do perfil de verossimilhança do S13.5. É pior caso
medido, não pior caso imaginado.

⚠️ **O que esta varredura NÃO faz.** Mantém as bordas de faixa (``CORTES_PD``) e
a forma linear do preço. A medição que descartou o redesenho de faixas — ganho
de 1,6 pontos-base — rodou sob a premissa errada e está marcada como suspeita no
post-mortem. Se o resultado aqui ficar apertado, é a primeira coisa a revisitar.
"""

from __future__ import annotations

import itertools
import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
import pandas as pd

from banking.dados import carregar_processada, preparar_base_c
from banking.modelo import treinar_modelo_final
from banking.perda import perda_por_faixa
from banking.politica import POLITICA_ESCOLHIDA, gerar_politica, validar_monotonicidade
from banking.projeto import DIR_EXTERNOS, DIR_TABELAS, log_step, semear
from banking.roi import (
    CENARIO_CALIBRADO,
    GUARD_RAILS,
    PREMISSAS_CALIBRADAS,
    PREMISSAS_SUBMETIDAS,
    Cenario,
    Premissas,
    aplicar_politica,
    simular,
)
from banking.score import CORTES_PD, faixa_de_score, score_de_pd

#: O quinto guard-rail. Declarado **uma vez**, aqui, e nunca perseguido: o
#: objetivo é o máximo ROI acima dele, não chegar nele.
PISO_DE_ROI = 0.15

#: As bordas do que a calibração sustenta (perfil do S13.5, âncora ponderada).
#: É com elas que se faz o estresse — pior caso medido, não imaginado.
FAIXA_BETA = (1.021, 1.363)
FAIXA_GAMA = (0.536, 1.930)

#: Teto de posicionamento no mercado. O professor elogiou o vencedor por cobrar
#: *"acima da mediana das 45 instituições e abaixo do topo"* — preço defensável,
#: não arbitrado. Uma política que só fecha no percentil 99 do mercado é
#: indefensável num comitê, por mais que o simulador aprove.
PERCENTIL_MAXIMO = 90.0

GRADE_LARGA = {
    "corte": [2, 3, 4, 5, 6, 7],
    "taxa_base": [0.0150, 0.0175, 0.0200, 0.0225, 0.0250, 0.0275, 0.0300],
    "k_risco": [0.0, 0.10, 0.20, 0.30, 0.50],
    "prazo_max": [36, 48, 60],
    "entrada_base": [0.0, 0.05, 0.10, 0.20],
    "entrada_passo": [0.0, 0.04],
    "prazo_como_teto": [False, True],
}


def _mercado() -> np.ndarray:
    """A distribuição de taxa do mercado, do bruto que o S13.4 guardou.

    Serve para responder *"onde esse preço cai entre os concorrentes?"* — a
    pergunta que separou o vencedor dos demais, segundo o professor.
    """
    caminho = DIR_EXTERNOS / "bcb_taxas_veiculos_2025s2.json"
    if not caminho.exists():
        raise SystemExit(
            f"falta {caminho}. Rode recuperacao/27_ancora_de_mercado.py antes — "
            "sem a distribuição do mercado não dá para dizer se o preço é defensável."
        )
    bruto = json.loads(caminho.read_text(encoding="utf-8"))
    taxas = [l["taxa_am"] for l in bruto["olinda"]["linhas"] if l["taxa_am"] is not None]
    return np.asarray(taxas, dtype=float)


def _percentil_no_mercado(taxa_media_pct: float, mercado: np.ndarray) -> float:
    """Que fração das instituições cobra menos que este preço."""
    return float((mercado < taxa_media_pct).mean() * 100.0)


def _taxa_media_ponderada(ofertas: pd.DataFrame, cenario, premissas) -> float:
    """A taxa média que o cliente de fato paga, em % a.m.

    Ponderada pelo que **fecha** — é o número comparável ao que o professor
    publicou para cada grupo (1,876% no nosso caso), não a média simples da
    tabela.
    """
    r = simular(ofertas, cenario, premissas)
    ap = ofertas[ofertas["aprovada"]]
    if ap.empty or r.contratos_esperados <= 0:
        return float("nan")
    excesso = np.maximum(ap["taxa_am"].to_numpy() / premissas.taxa_mercado - 1.0, 0.0)
    encurt = np.clip(
        1.0 - ap["prazo_meses"].to_numpy() / ap["prazo_desejado_meses"].to_numpy(), 0, 1
    )
    aceite = np.clip(
        cenario.a0
        * np.exp(-cenario.beta_taxa * excesso)
        * np.exp(-cenario.beta_entrada * ap["entrada_extra"].to_numpy())
        * np.exp(-cenario.beta_prazo * encurt),
        0.0, 1.0,
    )
    peso = aceite * ap["valor_financiado_ofertado"].to_numpy()
    return float(np.average(ap["taxa_am"].to_numpy(), weights=peso) * 100.0)


def _contexto():
    """Base C escorada, perda por faixa e a função de re-escoragem."""
    semear()
    base_a = carregar_processada("A")
    base_c = carregar_processada("C")
    modelo = treinar_modelo_final(base_a)
    escorar = lambda df: modelo.predict_proba(df)[:, 1]  # noqa: E731

    p = preparar_base_c(base_c).reset_index(drop=True)
    p["pd"] = escorar(p)
    perda = perda_por_faixa(p)
    return p, perda, escorar


def _avaliar(combo, ofertas, premissas, cenario, severo, mercado) -> dict | None:
    """Simula uma política e devolve a linha do relatório, ou ``None`` se inválida.

    Avalia **três** coisas, não uma:

    * o resultado sob a premissa calibrada — o número que se reporta;
    * o mesmo sob a **borda severa** do que o dado sustenta — porque política
      que só fecha no ponto central é aposta, não recomendação;
    * onde o preço cai na distribuição do mercado — porque preço que só fecha
      no topo é indefensável num comitê, por mais que o simulador aprove.
    """
    r = simular(ofertas, cenario, premissas)
    if r.contratos_esperados <= 0:
        return None
    rs = simular(ofertas, severo, premissas)
    taxa_media = _taxa_media_ponderada(ofertas, cenario, premissas)
    percentil = _percentil_no_mercado(taxa_media, mercado)

    cinco = not r.violacoes and r.roi_anual >= PISO_DE_ROI
    cinco_severo = not rs.violacoes and rs.roi_anual >= PISO_DE_ROI
    return {
        **combo,
        "roi": r.roi_anual,
        "volume": r.volume_originado,
        "inadimplencia": r.inadimplencia,
        "aprovacao": r.taxa_aprovacao,
        "aceite_medio": r.taxa_aceite_media,
        "contratos": r.contratos_esperados,
        "taxa_media_pct": taxa_media,
        "percentil_no_mercado": percentil,
        "roi_severo": rs.roi_anual,
        "volume_severo": rs.volume_originado,
        "inadimplencia_severa": rs.inadimplencia,
        "atende_os_cinco": cinco,
        "robusta": cinco and cinco_severo,
        "defensavel": cinco and percentil <= PERCENTIL_MAXIMO,
        "robusta_e_defensavel": cinco and cinco_severo and percentil <= PERCENTIL_MAXIMO,
    }


def varrer(grade: dict, p, perda, escorar, premissas, cenario, severo,
           mercado) -> pd.DataFrame:
    """Varre a grade reaproveitando as ofertas.

    As ofertas dependem de corte, prazo, entrada e da regra de prazo — **não**
    da taxa. Calculá-las uma vez por combinação de oferta, em vez de uma vez por
    política, é o que torna a varredura viável: sobra só o ``simular``.
    """
    eixos_oferta = ["corte", "prazo_max", "entrada_base", "entrada_passo",
                    "prazo_como_teto"]
    eixos_preco = ["taxa_base", "k_risco"]

    linhas, descartadas = [], 0
    combos_oferta = list(itertools.product(*(grade[e] for e in eixos_oferta)))
    for i, valores in enumerate(combos_oferta, 1):
        base = dict(zip(eixos_oferta, valores))
        if i % 25 == 0 or i == len(combos_oferta):
            log_step(f"  ofertas {i}/{len(combos_oferta)}")

        # As ofertas saem UMA vez por combinação de oferta. A re-escoragem do
        # modelo é o passo caro (37 ms contra 9 ms do simular), e nada nela
        # depende da taxa: entrada efetiva, LTV ofertado e PD re-escorada saem
        # de corte, prazo e entrada. A taxa entra depois, como troca de coluna.
        referencia = gerar_politica(
            corte=base["corte"], taxa_base=grade[eixos_preco[0]][0], k_risco=0.0,
            prazo_max=base["prazo_max"], entrada_base=base["entrada_base"],
            entrada_passo=base["entrada_passo"], perda_por_faixa=perda,
        )
        ofertas = aplicar_politica(
            p, referencia, escorar=escorar,
            prazo_como_teto=base["prazo_como_teto"],
        )

        for vals_preco in itertools.product(*(grade[e] for e in eixos_preco)):
            combo = {**base, **dict(zip(eixos_preco, vals_preco))}
            politica = gerar_politica(
                corte=combo["corte"], taxa_base=combo["taxa_base"],
                k_risco=combo["k_risco"], prazo_max=combo["prazo_max"],
                entrada_base=combo["entrada_base"],
                entrada_passo=combo["entrada_passo"], perda_por_faixa=perda,
            )
            if validar_monotonicidade(politica):
                descartadas += 1
                continue
            ofertas["taxa_am"] = ofertas["score"].map(
                politica.set_index("score")["taxa_am"]
            )
            linha = _avaliar(combo, ofertas, premissas, cenario, severo, mercado)
            if linha:
                linhas.append(linha)

    if descartadas:
        log_step(f"  {descartadas} tabelas descartadas por monotonicidade")
    return pd.DataFrame(linhas)


def _mostrar(titulo: str, linha: pd.Series) -> None:
    print(f"\n  {titulo}")
    print(f"    corte {int(linha['corte'])} · taxa_base {linha['taxa_base']:.2%} · "
          f"k_risco {linha['k_risco']:.3f} · prazo {int(linha['prazo_max'])}m"
          f"{' (teto)' if linha['prazo_como_teto'] else ' (fixo)'} · "
          f"entrada {linha['entrada_base']:.1%}+{linha['entrada_passo']:.0%}")
    print(f"    ROI {linha['roi']:.2%} · volume R$ {linha['volume']/1e6:.1f} mi · "
          f"inad {linha['inadimplencia']:.2%} · aprov {linha['aprovacao']:.1%} · "
          f"aceite {linha['aceite_medio']:.1%}")
    if "taxa_media_pct" in linha:
        print(f"    taxa média {linha['taxa_media_pct']:.3f}% a.m. — percentil "
              f"{linha['percentil_no_mercado']:.0f} do mercado"
              f"{'  ⚠️ acima do teto de defensabilidade' if linha['percentil_no_mercado'] > PERCENTIL_MAXIMO else ''}")
        print(f"    na borda severa: ROI {linha['roi_severo']:.2%} · vol R$ "
              f"{linha['volume_severo']/1e6:.1f} mi · inad {linha['inadimplencia_severa']:.2%}"
              f"  {'aguenta' if linha['robusta'] else '⚠️ NÃO aguenta'}")


def main() -> int:
    log_step("S13.6 · A política sob o piso de 15%, com premissas calibradas")
    p, perda, escorar = _contexto()
    premissas = PREMISSAS_CALIBRADAS
    cen = CENARIO_CALIBRADO
    severo = Cenario('severo', cen.a0, FAIXA_BETA[1], cen.beta_entrada,
                     cen.beta_prazo, FAIXA_GAMA[1])
    mercado = _mercado()
    log_step(f'mercado: {len(mercado)} observações do BCB, mediana {np.median(mercado):.3f}% a.m.')

    # --- controle de regressão, antes de qualquer conclusão nova -------------
    pol_sub = gerar_politica(**POLITICA_ESCOLHIDA, perda_por_faixa=perda)
    of_sub = aplicar_politica(p, pol_sub, escorar=escorar)
    r_antigo = simular(of_sub, "central", PREMISSAS_SUBMETIDAS)
    log_step(f"controle: a submetida sob as premissas antigas dá "
             f"{r_antigo.roi_anual:.4%} (publicado: 11,3294%)")
    if abs(r_antigo.roi_anual - 0.113294) > 1e-5:
        log_step("o controle NÃO reproduz — parar e investigar", "erro")
        return 1

    r_novo = simular(of_sub, cen, premissas)
    print(f"\n  A MESMA política submetida, sob a premissa calibrada:")
    print(f"    ROI {r_novo.roi_anual:.2%} · volume R$ {r_novo.volume_originado/1e6:.1f} mi"
          f" · inad {r_novo.inadimplencia:.2%} · aceite {r_novo.taxa_aceite_media:.1%}")
    print(f"    (o professor apurou 11,21% e R$ 84,4 mi)")

    # --- a varredura ---------------------------------------------------------
    log_step("varredura larga")
    largo = varrer(GRADE_LARGA, p, perda, escorar, premissas, cen, severo, mercado)
    viaveis = largo[largo["atende_os_cinco"]]
    log_step(f"{len(largo)} políticas avaliadas · {len(viaveis)} atendem os cinco limites")

    if viaveis.empty:
        print("\n  NENHUMA política da grade larga atende os cinco limites.")
        print("  Melhores por ROI, com o limite que cada uma fura:\n")
        for _, l in largo.nlargest(5, "roi").iterrows():
            fura = []
            if l["roi"] < PISO_DE_ROI: fura.append("ROI")
            if l["volume"] < GUARD_RAILS["volume_minimo"]: fura.append("volume")
            if l["inadimplencia"] > GUARD_RAILS["inadimplencia_maxima"]: fura.append("inad")
            if l["aprovacao"] < GUARD_RAILS["aprovacao_minima"]: fura.append("aprov")
            print(f"    ROI {l['roi']:.2%} · vol {l['volume']/1e6:>5.1f} mi · "
                  f"inad {l['inadimplencia']:.2%} · fura: {', '.join(fura) or '-'}")
        largo.to_csv(DIR_TABELAS / "s13_politica_sob_piso.csv", index=False)
        return 0

    # --- refino em torno da melhor ------------------------------------------
    melhor = viaveis.loc[viaveis["roi"].idxmax()]
    log_step("refino em torno da melhor")
    fino = {
        "corte": sorted({int(melhor["corte"]) + d for d in (-1, 0, 1)} & set(range(1, 10))),
        "taxa_base": [round(melhor["taxa_base"] + d, 5)
                      for d in np.arange(-0.0025, 0.0026, 0.0005)],
        "k_risco": [round(max(0.0, melhor["k_risco"] + d), 4)
                    for d in np.arange(-0.05, 0.051, 0.025)],
        "prazo_max": [int(melhor["prazo_max"])],
        "entrada_base": [round(max(0.0, melhor["entrada_base"] + d), 4)
                         for d in np.arange(-0.05, 0.051, 0.025)],
        "entrada_passo": [melhor["entrada_passo"]],
        "prazo_como_teto": [bool(melhor["prazo_como_teto"])],
    }
    refinado = varrer(fino, p, perda, escorar, premissas, cen, severo, mercado)
    todas = pd.concat([largo, refinado], ignore_index=True)
    viaveis = todas[todas["atende_os_cinco"]]
    log_step(f"{len(todas)} avaliadas no total · {len(viaveis)} atendem os cinco")

    print(f"\n  Das {len(viaveis)} que atendem os cinco limites:")
    print(f"    {int(viaveis['robusta'].sum()):>4} aguentam a borda severa do que o dado sustenta")
    print(f"    {int(viaveis['defensavel'].sum()):>4} ficam abaixo do percentil "
          f"{PERCENTIL_MAXIMO:.0f} do mercado")
    print(f"    {int(viaveis['robusta_e_defensavel'].sum()):>4} atendem as duas coisas")

    _mostrar("Maior ROI entre as que atendem os cinco limites:",
             viaveis.loc[viaveis["roi"].idxmax()])

    # A recomendação não é o máximo ROI: é o máximo ROI que sobrevive à borda do
    # que o dado sustenta E que se explica num comitê. O professor elogiou
    # exatamente isso no vencedor — ele testou subir 0,3 ponto, viu que romperia
    # dois guard-rails no cenário severo, e desistiu.
    candidatas = viaveis[viaveis["robusta_e_defensavel"]]
    rotulo = "RECOMENDADA — maior ROI que aguenta a borda severa e se defende no mercado:"
    if candidatas.empty:
        candidatas = viaveis[viaveis["robusta"]]
        rotulo = "RECOMENDADA — maior ROI que aguenta a borda severa (nenhuma passa também no teste de mercado):"
    if candidatas.empty:
        print("\n  ⚠️  NENHUMA política aguenta a borda severa. Qualquer escolha aqui "
              "é aposta declarada, não recomendação.")
        escolhida = viaveis.loc[viaveis["roi"].idxmax()]
    else:
        escolhida = candidatas.loc[candidatas["roi"].idxmax()]
        _mostrar(rotulo, escolhida)

    # --- o que cada critério antigo teria escolhido --------------------------
    print("\n  O que cada critério escolheria, na mesma grade:")
    _mostrar("máximo ROI, ignorando o piso de 15%:", todas.loc[todas["roi"].idxmax()])
    quatro = todas[(todas["volume"] >= GUARD_RAILS["volume_minimo"])
                   & (todas["inadimplencia"] <= GUARD_RAILS["inadimplencia_maxima"])
                   & (todas["aprovacao"] >= GUARD_RAILS["aprovacao_minima"])]
    if not quatro.empty:
        janela = quatro[quatro["roi"] >= quatro["roi"].max() - 0.01]
        folga = (janela["volume"] / GUARD_RAILS["volume_minimo"] - 1.0)
        _mostrar("EMPATE_ROI de 1 pp + desempate por folga (o critério do S09):",
                 janela.loc[folga.idxmax()])

    # --- estresse nas bordas do que o dado sustenta -------------------------
    print("\n  A escolhida nas bordas do que a calibração sustenta:")
    pol = gerar_politica(
        corte=int(escolhida["corte"]), taxa_base=float(escolhida["taxa_base"]),
        k_risco=float(escolhida["k_risco"]), prazo_max=int(escolhida["prazo_max"]),
        entrada_base=float(escolhida["entrada_base"]),
        entrada_passo=float(escolhida["entrada_passo"]), perda_por_faixa=perda,
    )
    of = aplicar_politica(p, pol, escorar=escorar,
                          prazo_como_teto=bool(escolhida["prazo_como_teto"]))
    for rot, bt, gm in [("otimista (β mín, γ mín)", FAIXA_BETA[0], FAIXA_GAMA[0]),
                        ("calibrada", cen.beta_taxa, cen.gama),
                        ("severa (β máx, γ máx)", FAIXA_BETA[1], FAIXA_GAMA[1])]:
        c = Cenario(rot, cen.a0, bt, cen.beta_entrada, cen.beta_prazo, gm)
        r = simular(of, c, premissas)
        cinco = not r.violacoes and r.roi_anual >= PISO_DE_ROI
        print(f"    {rot:<24} ROI {r.roi_anual:>6.2%} · vol R$ {r.volume_originado/1e6:>5.1f} mi"
              f" · inad {r.inadimplencia:>5.2%} · {'cinco de cinco' if cinco else 'fura: ' + (', '.join(r.violacoes) or 'ROI')}")

    print("\n  A tabela da política escolhida:\n")
    print(f"    {'score':<7}{'faixa de PD':<18}{'decisão':<10}{'taxa':>8}{'prazo':>8}{'entrada':>9}")
    for _, l in pol.iterrows():
        lo, hi = faixa_de_score(int(l["score"]))
        faixa = f"{lo:.1%} – {hi:.1%}"
        if l["decisao"] == "NEGAR":
            print(f"    {int(l['score']):<7}{faixa:<18}{'NEGAR':<10}{'—':>8}{'—':>8}{'—':>9}")
        else:
            print(f"    {int(l['score']):<7}{faixa:<18}{'APROVAR':<10}{l['taxa_am']:>8.2%}"
                  f"{int(l['prazo_meses']):>7}m{l['pct_entrada_minima']:>9.0%}")

    destino = DIR_TABELAS / "s13_politica_sob_piso.csv"
    todas.to_csv(destino, index=False)
    log_step(f"Tabela gravada em {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
