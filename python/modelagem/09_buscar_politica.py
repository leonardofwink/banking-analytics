"""S09 · Busca da tabela de política.

Varre a grade de 960 políticas, simula cada uma nos três cenários e aplica o
critério declarado na spec:

1. descartar quem viola guard-rail em **qualquer** cenário;
2. entre as sobreviventes, maximizar o ROI do cenário central;
3. desempatar por **folga** até o guard-rail mais apertado.

O item 3 evita a armadilha de otimizar até a borda: uma política que entrega
0,3 ponto a mais de ROI e fica a 0,2 ponto de furar o volume é pior que a
alternativa — o ganho é pequeno e certo, o risco é grande e binário.

Rodar::

    .\\scripts\\py.cmd python\\modelagem\\09_buscar_politica.py

Spec: ``docs/specs/S09_TABELA_DE_POLITICA.md``.
"""

from __future__ import annotations

import itertools
import sys

import numpy as np
import pandas as pd

from banking.dados import carregar_processada, preparar_base_c
from banking.modelo import treinar_modelo_final
from banking.perda import fator_ead, lgd
from banking.politica import gerar_politica, validar_monotonicidade
from banking.projeto import DIR_TABELAS, log_step
from banking.roi import CENARIOS, GUARD_RAILS, aplicar_politica, simular
from banking.score import score_de_pd

# A grade. Pequena o bastante para ser auditável, grande o bastante para
# cobrir o trade-off. Ver a justificativa de cada parâmetro na spec.
GRADE = {
    "corte": [7, 6, 5, 4],  # a janela viável identificada no S07
    "taxa_base": [0.0150, 0.0175, 0.0200, 0.0225, 0.0250],
    "k_risco": [0.0, 0.10, 0.20, 0.30],  # k=0 reproduz a política antiga
    "prazo_max": [48, 60],
    "entrada_base": [0.0, 0.05, 0.10],
    "entrada_passo": [0.0, 0.04],
}

# Critério 3: políticas a menos disto de distância em ROI são consideradas
# empatadas, e o desempate vai para a folga.
EMPATE_ROI = 0.01


def folga_minima(resultados: dict) -> float:
    """Distância relativa até o guard-rail mais apertado, no pior cenário.

    Zero significa encostado no limite; 0,20 significa 20% de margem. É o
    desempate do critério 3 — e o que distingue uma política robusta de uma
    que deu certo por pouco.
    """
    folgas = []
    for r in resultados.values():
        folgas.append((r.taxa_aprovacao - GUARD_RAILS["aprovacao_minima"]) / GUARD_RAILS["aprovacao_minima"])
        folgas.append((GUARD_RAILS["inadimplencia_maxima"] - r.inadimplencia) / GUARD_RAILS["inadimplencia_maxima"])
        folgas.append((r.volume_originado - GUARD_RAILS["volume_minimo"]) / GUARD_RAILS["volume_minimo"])
    return float(min(folgas))


def main() -> int:
    log_step("S09 · Busca da tabela de política")

    try:
        base_a = carregar_processada("A")
        base_c = carregar_processada("C")
    except FileNotFoundError as erro:
        log_step(str(erro), "erro")
        return 1

    modelo = treinar_modelo_final(base_a)
    escorar = lambda df: modelo.predict_proba(df)[:, 1]

    propostas = preparar_base_c(base_c)
    propostas["pd"] = escorar(propostas)

    # Perda esperada média de cada faixa — insumo da regra de preço.
    el = (
        propostas["pd"]
        * fator_ead(propostas["prazo_meses"], propostas["ltv"])
        * lgd(propostas["idade_veiculo_anos"], propostas["ltv"], propostas["possui_avalista"])
    )
    perda_por_faixa = (
        pd.DataFrame({"score": score_de_pd(propostas["pd"]), "el": el})
        .groupby("score")["el"]
        .mean()
        .to_dict()
    )

    combinacoes = list(itertools.product(*GRADE.values()))
    log_step(f"{len(combinacoes)} políticas × {len(CENARIOS)} cenários")

    # A PD re-escorada depende de entrada e prazo, NÃO da taxa. Cachear a
    # aplicação por (corte, prazo, entrada) corta a escoragem de 960 para 48.
    cache_ofertas: dict[tuple, pd.DataFrame] = {}
    registros = []

    for corte, taxa_base, k_risco, prazo_max, entrada_base, entrada_passo in combinacoes:
        politica = gerar_politica(
            corte, taxa_base, k_risco, prazo_max, entrada_base, entrada_passo, perda_por_faixa
        )

        problemas = validar_monotonicidade(politica)
        if problemas:
            continue  # a parametrização não deveria produzir isso, mas é barato conferir

        chave = (corte, prazo_max, entrada_base, entrada_passo)
        if chave not in cache_ofertas:
            cache_ofertas[chave] = aplicar_politica(propostas, politica, escorar=escorar)

        # A taxa entra depois do cache: ela não altera LTV, financiado nem PD
        # do modelo — só o preço e, por seleção adversa, a PD efetiva.
        ofertas = cache_ofertas[chave].copy()
        ofertas["taxa_am"] = ofertas["score"].map(politica.set_index("score")["taxa_am"])

        resultados = {nome: simular(ofertas, nome) for nome in CENARIOS}
        viola = any(r.violacoes for r in resultados.values())

        registros.append(
            {
                "corte": corte, "taxa_base": taxa_base, "k_risco": k_risco,
                "prazo_max": prazo_max, "entrada_base": entrada_base,
                "entrada_passo": entrada_passo,
                "roi_central": resultados["central"].roi_anual,
                "roi_pessimista": resultados["pessimista"].roi_anual,
                "roi_otimista": resultados["otimista"].roi_anual,
                "aprovacao": resultados["central"].taxa_aprovacao,
                "inadimplencia_pior": max(r.inadimplencia for r in resultados.values()),
                "volume_pior": min(r.volume_originado for r in resultados.values()),
                "viavel": not viola,
                "folga": folga_minima(resultados) if not viola else np.nan,
                "violacoes": " | ".join(
                    f"{n}: {', '.join(r.violacoes)}" for n, r in resultados.items() if r.violacoes
                ),
            }
        )

    busca = pd.DataFrame(registros)
    log_step(f"{len(busca)} políticas avaliadas · {int(busca['viavel'].sum())} viáveis nos 3 cenários", "ok")

    viaveis = busca[busca["viavel"]].copy()
    if viaveis.empty:
        log_step("NENHUMA política respeita os guard-rails nos três cenários.", "erro")
        print("\n--- O que mais chegou perto (menor violação) ---")
        print(busca.nlargest(10, "roi_central")[
            ["corte", "taxa_base", "k_risco", "entrada_base", "roi_central", "volume_pior", "violacoes"]
        ].to_string(index=False))
        busca.to_csv(DIR_TABELAS / "s09_busca.csv", index=False)
        return 1

    # --- critério 2: maximizar o ROI central --------------------------------
    melhor_roi = viaveis["roi_central"].max()
    empatadas = viaveis[viaveis["roi_central"] >= melhor_roi - EMPATE_ROI]

    # --- critério 3: entre as empatadas, a de maior folga -------------------
    escolhida = empatadas.sort_values(["folga", "roi_central"], ascending=False).iloc[0]

    print("\n--- 10 melhores por ROI (cenário central) ---")
    print(
        viaveis.nlargest(10, "roi_central")[
            ["corte", "taxa_base", "k_risco", "prazo_max", "entrada_base", "entrada_passo",
             "roi_central", "roi_pessimista", "aprovacao", "inadimplencia_pior", "volume_pior", "folga"]
        ]
        .assign(
            roi_central=lambda d: d.roi_central.map("{:.1%}".format),
            roi_pessimista=lambda d: d.roi_pessimista.map("{:.1%}".format),
            aprovacao=lambda d: d.aprovacao.map("{:.1%}".format),
            inadimplencia_pior=lambda d: d.inadimplencia_pior.map("{:.1%}".format),
            volume_pior=lambda d: (d.volume_pior / 1e6).map("{:.1f}".format),
            folga=lambda d: d.folga.map("{:.1%}".format),
        )
        .to_string(index=False)
    )

    log_step(
        f"Empate técnico (ROI a menos de {EMPATE_ROI:.0%} do melhor): {len(empatadas)} políticas. "
        "Desempate pela folga.",
        "ok",
    )

    # --- a tabela final -----------------------------------------------------
    final = gerar_politica(
        int(escolhida["corte"]), float(escolhida["taxa_base"]), float(escolhida["k_risco"]),
        int(escolhida["prazo_max"]), float(escolhida["entrada_base"]),
        float(escolhida["entrada_passo"]), perda_por_faixa,
    )

    print("\n=== POLÍTICA ESCOLHIDA ===")
    print(
        f"corte score >= {int(escolhida['corte'])} · taxa_base {escolhida['taxa_base']:.2%} · "
        f"k_risco {escolhida['k_risco']:.2f} · prazo máx {int(escolhida['prazo_max'])} · "
        f"entrada {escolhida['entrada_base']:.0%} + {escolhida['entrada_passo']:.0%}/faixa"
    )
    exibir = final.copy()
    exibir["perda_esperada"] = exibir["score"].map(lambda s: perda_por_faixa.get(int(s), np.nan))
    print(
        exibir.assign(
            taxa_am=lambda d: d.taxa_am.map(lambda v: "—" if pd.isna(v) else f"{v:.3%}"),
            pct_entrada_minima=lambda d: d.pct_entrada_minima.map(lambda v: "—" if pd.isna(v) else f"{v:.0%}"),
            prazo_meses=lambda d: d.prazo_meses.map(lambda v: "—" if pd.isna(v) else f"{int(v)}"),
            perda_esperada=lambda d: d.perda_esperada.map("{:.2%}".format),
        ).to_string(index=False)
    )

    chave = (int(escolhida["corte"]), int(escolhida["prazo_max"]),
             float(escolhida["entrada_base"]), float(escolhida["entrada_passo"]))
    ofertas = aplicar_politica(propostas, final, escorar=escorar)
    print("\n--- Desempenho nos três cenários ---")
    linhas = []
    for nome in CENARIOS:
        r = simular(ofertas, nome)
        linhas.append(r.como_linha())
    print(
        pd.DataFrame(linhas)
        .assign(
            roi_anual=lambda d: d.roi_anual.map("{:.1%}".format),
            inadimplencia=lambda d: d.inadimplencia.map("{:.2%}".format),
            volume_mi=lambda d: d.volume_mi.map("R$ {:.1f} mi".format),
            aprovacao=lambda d: d.aprovacao.map("{:.1%}".format),
            aceite_medio=lambda d: d.aceite_medio.map("{:.1%}".format),
            contratos=lambda d: d.contratos.map("{:.0f}".format),
            prazo_anos=lambda d: d.prazo_anos.map("{:.2f}".format),
        )
        .to_string(index=False)
    )

    log_step(f"Folga até o guard-rail mais apertado: {escolhida['folga']:.1%}", "ok")

    DIR_TABELAS.mkdir(parents=True, exist_ok=True)
    busca.to_csv(DIR_TABELAS / "s09_busca.csv", index=False)
    final.to_csv(DIR_TABELAS / "s09_politica.csv", index=False)
    log_step(f"Busca e política gravadas em {DIR_TABELAS}", "ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
