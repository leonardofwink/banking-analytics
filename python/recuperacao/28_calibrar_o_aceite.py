# -*- coding: utf-8 -*-
"""S13.5 · Calibrar o aceite — a premissa deixa de ser chute e vira estimativa.

Até a apuração de 26/09/2026, a reação do cliente ao preço era **premissa**:
``DEBITO_TECNICO.md § 4`` dizia, com razão para a época, que *"não há como
calibrar"* — submissão única, sem feedback.

Agora há feedback. O professor devolveu ROI e volume realizados de cada grupo,
e a política do vencedor faixa a faixa. São cinco observações para três
parâmetros.

**O que o ajuste usa** (as cinco):

======  ==========================  ==============
 #       observação                  alvo
======  ==========================  ==============
 1       nossa política → ROI        11,21%
 2       nossa política → volume     R$ 84,4 MM
 3       Grupo 2 → ROI               16,53%
 4       Grupo 2 → volume            R$ 50,1 MM
 5       Grupo 2 → aceite médio      63,9%
======  ==========================  ==============

**O que fica reservado, e por quê.** O contrafactual do professor — *"a própria
política do Grupo 3, com 0,7 ponto a mais na taxa, teria entregue 16,27% de ROI
com R$ 62,8 milhões"* — **não entra no ajuste**. É a única verificação externa
que temos e não se repete: gastá-la na calibração destrói a chance de saber se
a calibração presta.

⚠️ **Duas aproximações declaradas.**

1. A política do Grupo 2 é reconstruída da tabela que o professor publicou, mas
   aplicada sobre a **nossa** PD — não temos o modelo deles. Os dois modelos
   ordenam parecido (AUC 0,7711 contra 0,7495), então a mesma proposta costuma
   cair na mesma faixa, mas não sempre.
2. ``beta_entrada`` e ``beta_prazo`` ficam **fixos** nos valores do cenário
   central. Com cinco observações não dá para identificar cinco parâmetros, e
   os dois que ficam são os que menos variam entre as políticas (as três exigem
   10% de entrada). A sensibilidade a eles é reportada no fim.
"""

from __future__ import annotations

import sys

# O console do Windows abre em cp1252 e derruba o script na primeira
# seta ou emoji. Reconfigurar aqui evita perder uma calibracao de minutos
# por causa de um caractere de relatorio.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
import pandas as pd
from scipy.optimize import differential_evolution

from banking.dados import carregar_processada, preparar_base_c
from banking.modelo import treinar_modelo_final
from banking.perda import fator_ead, lgd
from banking.politica import POLITICA_ESCOLHIDA, gerar_politica
from banking.projeto import DIR_TABELAS, SEMENTE, log_step, semear
from banking.roi import CENARIOS, Cenario, Premissas, aplicar_politica, simular
from banking.score import CORTES_PD, SCORE_MAXIMO, SCORE_MINIMO, score_de_pd

# --- As duas réguas em disputa (de 27_ancora_de_mercado.py) -------------------
# Nenhuma é escolhida aqui de propósito: a decisão de qual usar fica para o
# grupo, e este script existe para mostrar quanto ela muda a resposta.
ANCORAS = {
    "mediana das instituições": 0.01820,
    "média ponderada por volume": 0.02021,
}

# --- A política do Grupo 2, do quadro comparativo do professor ----------------
# Fronteiras superiores de PD das faixas 10 a 2 — "decis da Base B, por valor".
CORTES_GRUPO2 = (0.0294, 0.0354, 0.0412, 0.0478, 0.0560, 0.0651, 0.0788,
                 0.1025, 0.1479)
# Taxa por faixa, do score 10 ao 4; abaixo disso, NEGAR (PD máxima aceita 7,88%).
TAXAS_GRUPO2 = {10: 0.0230, 9: 0.0230, 8: 0.0240, 7: 0.0250,
                6: 0.0260, 5: 0.0280, 4: 0.0290}
PRAZO_TETO_GRUPO2 = 60  # "o pedido, limitado a 60 meses"
ENTRADA_GRUPO2 = 0.10   # "10% em todas as faixas"

# --- O que a apuração devolveu ------------------------------------------------
ALVOS = {
    "nossa · ROI": 0.1121,
    "nossa · volume": 84.4e6,
    "Grupo 2 · ROI": 0.1653,
    "Grupo 2 · volume": 50.1e6,
    "Grupo 2 · aceite": 0.639,
}

#: Reservado para validação fora da amostra. Não entra no ajuste.
VALIDACAO = {"roi": 0.1627, "volume": 62.8e6, "acrescimo_na_taxa": 0.007}

#: Tolerância de cada observação, para definir a região compatível em vez de um
#: ponto. Vem da precisão com que o número foi publicado, não de conveniência.
TOLERANCIA = {
    "nossa · ROI": 0.0015, "nossa · volume": 2.0e6,
    "Grupo 2 · ROI": 0.0015, "Grupo 2 · volume": 2.0e6,
    "Grupo 2 · aceite": 0.015,
}


def politica_do_grupo2() -> pd.DataFrame:
    """A tabela do vencedor, no formato que o motor consome."""
    linhas = []
    for score in range(SCORE_MAXIMO, SCORE_MINIMO - 1, -1):
        aprovada = score in TAXAS_GRUPO2
        linhas.append({
            "score": score,
            "decisao": "APROVAR" if aprovada else "NEGAR",
            "taxa_am": TAXAS_GRUPO2.get(score, np.nan),
            "prazo_meses": float(PRAZO_TETO_GRUPO2) if aprovada else np.nan,
            "pct_entrada_minima": ENTRADA_GRUPO2 if aprovada else np.nan,
        })
    return pd.DataFrame(linhas)


def _com_acrescimo(politica: pd.DataFrame, pp: float) -> pd.DataFrame:
    """A mesma política com ``pp`` a mais na taxa, truncada no teto do enunciado."""
    nova = politica.copy()
    nova["taxa_am"] = np.minimum(nova["taxa_am"] + pp, 0.035)
    return nova


def preparar() -> dict:
    """Escora a base C e monta as ofertas de cada política, uma única vez.

    As ofertas não dependem das elasticidades — só da política. Calculá-las
    fora do laço de otimização é o que torna a calibração viável: sobra só o
    :func:`simular`, que é barato.
    """
    semear()
    base_a = carregar_processada("A")
    base_c = carregar_processada("C")
    modelo = treinar_modelo_final(base_a)
    escorar = lambda df: modelo.predict_proba(df)[:, 1]  # noqa: E731

    p = preparar_base_c(base_c).reset_index(drop=True)
    p["pd"] = escorar(p)

    perda = (
        p.assign(
            sc=score_de_pd(p["pd"]),
            el=fator_ead(p["prazo_desejado_meses"], p["ltv"])
            * lgd(p["idade_veiculo_anos"], p["ltv"], p["possui_avalista"])
            * p["pd"],
        )
        .groupby("sc")["el"].mean().to_dict()
    )

    nossa = gerar_politica(**POLITICA_ESCOLHIDA, perda_por_faixa=perda)
    g2 = politica_do_grupo2()

    return {
        "nossa": aplicar_politica(p, nossa, escorar=escorar),
        "nossa+0,7pp": aplicar_politica(
            p, _com_acrescimo(nossa, VALIDACAO["acrescimo_na_taxa"]), escorar=escorar
        ),
        "grupo2": aplicar_politica(
            p, g2, escorar=escorar, cortes=CORTES_GRUPO2, prazo_como_teto=True
        ),
    }


def _previsto(ofertas: dict, cen: Cenario, premissas: Premissas) -> dict:
    """O que o motor prevê para cada observação, sob um conjunto de premissas."""
    r_nossa = simular(ofertas["nossa"], cen, premissas)
    r_g2 = simular(ofertas["grupo2"], cen, premissas)
    return {
        "nossa · ROI": r_nossa.roi_anual,
        "nossa · volume": r_nossa.volume_originado,
        "Grupo 2 · ROI": r_g2.roi_anual,
        "Grupo 2 · volume": r_g2.volume_originado,
        "Grupo 2 · aceite": r_g2.taxa_aceite_media,
    }


def _erro(params, ofertas, premissas_base, fixos) -> float:
    """Soma dos quadrados dos erros **relativos** — escalas diferentes, peso igual."""
    a0, beta_taxa, gama = params
    cen = Cenario("calibrado", a0, beta_taxa, fixos[0], fixos[1], gama)
    prev = _previsto(ofertas, cen, premissas_base)
    return sum(((prev[k] - v) / v) ** 2 for k, v in ALVOS.items())


def calibrar(ofertas: dict, taxa_mercado: float, fixos) -> tuple:
    """Ajusta (a0, beta_taxa, gama) às cinco observações."""
    premissas = Premissas("calibrando", taxa_mercado, CENARIOS)
    r = differential_evolution(
        _erro,
        bounds=[(0.30, 1.00), (0.0, 6.0), (0.0, 3.0)],
        args=(ofertas, premissas, fixos),
        seed=SEMENTE, tol=1e-10, polish=True, maxiter=300,
    )
    return tuple(r.x), float(r.fun)


def perfil(ofertas: dict, taxa_mercado: float, fixos, centro, indice: int,
           nome: str, folga: float = 1.5) -> tuple:
    """Quanto um parâmetro pode variar sem piorar materialmente o ajuste.

    Para cada valor do parâmetro numa grade, re-otimiza os outros dois e olha o
    erro resultante. O intervalo devolvido é onde o erro fica dentro de
    ``folga`` vezes o mínimo — um perfil, não uma tolerância escolhida a dedo.

    Um ponto ótimo esconde o que o dado não determina; o intervalo responde à
    pergunta certa: *que elasticidades seriam igualmente compatíveis com o que
    o professor apurou?*
    """
    premissas = Premissas("perfil", taxa_mercado, CENARIOS)
    limites = [(0.30, 1.00), (0.0, 6.0), (0.0, 3.0)]
    lo, hi = limites[indice]
    grade = np.linspace(max(lo, centro[indice] * 0.5),
                        min(hi, centro[indice] * 1.8), 19)

    melhor, erros = np.inf, []
    for valor in grade:
        def alvo(livres):
            p = list(centro)
            p[indice] = valor
            for j, k in enumerate([i for i in range(3) if i != indice]):
                p[k] = livres[j]
            return _erro(p, ofertas, premissas, fixos)

        r = differential_evolution(
            alvo, bounds=[limites[i] for i in range(3) if i != indice],
            seed=SEMENTE, tol=1e-8, maxiter=60, polish=True,
        )
        erros.append(float(r.fun))
        melhor = min(melhor, float(r.fun))

    dentro = grade[np.array(erros) <= melhor * folga]
    return (float(dentro.min()), float(dentro.max())) if len(dentro) else (np.nan, np.nan)


def main() -> int:
    log_step("S13.5 · Calibrar o aceite contra o que o professor apurou")
    ofertas = preparar()
    central = CENARIOS["central"]
    fixos = (central.beta_entrada, central.beta_prazo)
    log_step(f"beta_entrada={fixos[0]} e beta_prazo={fixos[1]} fixos, do cenário central")

    saida = []
    for nome_ancora, taxa in ANCORAS.items():
        print("\n" + "=" * 78)
        print(f"  ÂNCORA: {nome_ancora} — {taxa:.3%} a.m.")
        print("=" * 78)

        (a0, bt, g), erro = calibrar(ofertas, taxa, fixos)
        premissas = Premissas(nome_ancora, taxa, CENARIOS)
        cen = Cenario("calibrado", a0, bt, fixos[0], fixos[1], g)
        prev = _previsto(ofertas, cen, premissas)

        print(f"\n  Parâmetros ajustados:   a0 {a0:.3f} · beta_taxa {bt:.3f} · gama {g:.3f}")
        print(f"  (o central usava:       a0 {central.a0} · beta_taxa {central.beta_taxa}"
              f" · gama {central.gama})")

        print(f"\n  {'observação':<22}{'alvo':>13}{'previsto':>13}{'erro':>12}")
        for k, alvo in ALVOS.items():
            p = prev[k]
            if "volume" in k:
                print(f"  {k:<22}{alvo/1e6:>10.1f} mi{p/1e6:>10.1f} mi"
                      f"{(p-alvo)/1e6:>+9.2f} mi")
            else:
                print(f"  {k:<22}{alvo:>12.2%}{p:>13.2%}{(p-alvo)*100:>+11.2f}pp")

        # --- a prova: o contrafactual do professor, que não entrou no ajuste ---
        r_val = simular(ofertas["nossa+0,7pp"], cen, premissas)
        d_roi = (r_val.roi_anual - VALIDACAO["roi"]) * 100
        d_vol = (r_val.volume_originado - VALIDACAO["volume"]) / 1e6
        passou = abs(d_roi) <= 0.30 and abs(d_vol) <= 3.0
        print(f"\n  VALIDAÇÃO FORA DA AMOSTRA — nossa política com +0,7 pp na taxa")
        print(f"    ROI     alvo {VALIDACAO['roi']:.2%}   previsto {r_val.roi_anual:.2%}"
              f"   erro {d_roi:+.2f} pp")
        print(f"    volume  alvo {VALIDACAO['volume']/1e6:.1f} mi  previsto "
              f"{r_val.volume_originado/1e6:.1f} mi  erro {d_vol:+.2f} mi")
        print(f"    guard-rails: {'todos' if not r_val.violacoes else ', '.join(r_val.violacoes)}")
        print(f"    -> {'PASSOU' if passou else 'NAO FECHOU'}")

        print()
        print("  Quanto o dado determina (perfil: erro até 1,5x o mínimo):")
        for i, nome in enumerate(("a0", "beta_taxa", "gama")):
            lo, hi = perfil(ofertas, taxa, fixos, (a0, bt, g), i, nome)
            print(f"    {nome:<11}{lo:.3f} a {hi:.3f}")

        saida.append({
            "ancora": nome_ancora, "taxa_mercado": taxa,
            "a0": a0, "beta_taxa": bt, "gama": g, "erro_quadratico": erro,
            **{f"previsto__{k}": prev[k] for k in ALVOS},
            "validacao_roi": r_val.roi_anual, "validacao_volume": r_val.volume_originado,
            "validacao_passou": passou,
        })

    destino = DIR_TABELAS / "s13_calibracao_do_aceite.csv"
    pd.DataFrame(saida).to_csv(destino, index=False)
    log_step(f"Tabela gravada em {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
