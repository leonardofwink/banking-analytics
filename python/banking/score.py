"""S07 · Faixas de score — a tradução de PD em decisão.

    score 10 = melhor risco (menor PD)   ·   score 1 = pior

Convenção do enunciado. Toda decisão de política se apoia no **score**, não na
PD bruta: é o score que indexa a tabela de taxa, prazo e entrada mínima.

⚠️ **Os cortes são de PD absoluta, não quantis.** Quantil ("os 10% piores viram
score 1") muda de significado quando a população muda — e a base C **é** outra
população (PSI de 5,93 em ``qtd_restricoes_ativas``, medido no S03). Com corte
absoluto, "score 5" quer dizer *PD entre 9,5% e 13%* em qualquer base, e o preço
da faixa passa a ser defensável: ele cobre aquele risco, e aquele risco é o
mesmo em toda parte.

Ver ``docs/specs/S07_FAIXAS_DE_SCORE.md`` para os critérios que levaram a estes
cortes e para o que a distribuição revela sobre o corte de aprovação.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = [
    "CORTES_PD",
    "SCORE_MAXIMO",
    "SCORE_MINIMO",
    "faixa_de_score",
    "score_de_pd",
    "tabela_de_faixas",
]

SCORE_MINIMO = 1
SCORE_MAXIMO = 10

# Fronteiras superiores de PD das faixas 10 a 2, em ordem crescente. A faixa 1
# é tudo acima da última. A progressão é aproximadamente geométrica porque o
# risco de crédito cresce multiplicativamente: faixas de largura constante
# seriam finas demais em cima e grossas demais embaixo.
#
#   score 10  PD <= 2,5%        score 5   9,5% < PD <= 13%
#   score  9  2,5% < PD <= 3,5% score 4    13% < PD <= 18%
#   score  8  3,5% < PD <= 5%   score 3    18% < PD <= 25%
#   score  7    5% < PD <= 7%   score 2    25% < PD <= 35%
#   score  6    7% < PD <= 9,5% score 1    PD > 35%
CORTES_PD = (0.025, 0.035, 0.050, 0.070, 0.095, 0.130, 0.180, 0.250, 0.350)


def score_de_pd(pd_valores, cortes=CORTES_PD) -> np.ndarray:
    """Converte probabilidade de default em faixa de score (1 a 10).

    Intervalos **fechados à direita**, como as faixas de LTV do S02: uma PD de
    exatamente 2,5% é score 10; 2,51% já é score 9.

    :param pd_valores: PD em **fração** (``0.085``, não ``8.5``).
    :param cortes: as nove fronteiras de PD, em ordem crescente. O default é
        :data:`CORTES_PD`, e mantê-lo reproduz tudo o que foi submetido — a
        régua só vira argumento para que **usar outra seja uma escolha
        declarada**, nunca uma edição silenciosa da constante.
    :return: array de inteiros entre 1 e 10, com 10 = melhor risco.
    :raises ValueError: se alguma PD estiver fora de [0, 1] — sinal de erro de
        unidade, que produziria uma tabela de política inteira errada.
    """
    p = np.asarray(pd_valores, dtype=float)

    if np.isnan(p).any():
        raise ValueError(
            f"{int(np.isnan(p).sum())} PDs nulas — toda proposta precisa de faixa. "
            "Sem score não há decisão de política."
        )
    if p.min(initial=0.0) < 0.0 or p.max(initial=0.0) > 1.0:
        raise ValueError(
            f"PD fora de [0, 1] — min {p.min():.4f}, max {p.max():.4f}. "
            "Esta função espera fração: 0.085 para 8,5%."
        )

    # searchsorted devolve quantos cortes a PD já ultrapassou: 0 para a melhor
    # faixa, 9 para a pior. O score é o complemento.
    return (SCORE_MAXIMO - np.searchsorted(cortes, p, side="left")).astype(int)


def faixa_de_score(score: int, cortes=CORTES_PD) -> tuple[float, float]:
    """Devolve ``(pd_minima, pd_maxima)`` da faixa — o inverso de :func:`score_de_pd`.

    É o que a tabela de política exibe: cada linha precisa dizer que intervalo
    de risco ela cobre, senão a tabela não se explica sozinha.

    :param score: inteiro entre 1 e 10.
    :param cortes: as mesmas fronteiras passadas a :func:`score_de_pd`. Passar
        uma régua aqui e outra lá produz uma tabela que descreve faixas
        diferentes das que a política aplicou — incoerência que vale 10 pontos.
    :return: limites da faixa. A faixa 10 começa em 0,0; a faixa 1 termina em 1,0.
    """
    if not SCORE_MINIMO <= score <= SCORE_MAXIMO:
        raise ValueError(f"score {score} fora de [{SCORE_MINIMO}, {SCORE_MAXIMO}]")

    indice = SCORE_MAXIMO - score  # 0 para score 10, 9 para score 1
    minimo = 0.0 if indice == 0 else cortes[indice - 1]
    maximo = 1.0 if indice == len(cortes) else cortes[indice]
    return (minimo, maximo)


def tabela_de_faixas(pd_valores=None, pesos=None, cortes=CORTES_PD) -> pd.DataFrame:
    """Monta o esqueleto da tabela de política: uma linha por faixa.

    Sem argumentos, devolve só os limites de cada faixa. Com ``pd_valores``,
    acrescenta quantas propostas caem em cada uma e a PD média observada —
    que é como se confere se alguma faixa ficou irrelevante.

    :param pd_valores: PDs de uma base, para contar a ocupação das faixas.
    :param pesos: valor financiado de cada proposta, para somar volume por faixa.
    :param cortes: as fronteiras de PD, repassadas a :func:`faixa_de_score` e
        :func:`score_de_pd` para que a tabela descreva a mesma régua que classifica.
    """
    linhas = []
    for score in range(SCORE_MAXIMO, SCORE_MINIMO - 1, -1):
        minimo, maximo = faixa_de_score(score, cortes)
        linhas.append({"score": score, "pd_minima": minimo, "pd_maxima": maximo})
    tabela = pd.DataFrame(linhas)

    if pd_valores is None:
        return tabela

    scores = score_de_pd(pd_valores, cortes)
    p = np.asarray(pd_valores, dtype=float)
    ocupacao = (
        pd.DataFrame({"score": scores, "pd": p})
        .groupby("score")
        .agg(n=("pd", "size"), pd_media=("pd", "mean"))
    )
    tabela = tabela.merge(ocupacao, on="score", how="left")
    tabela["n"] = tabela["n"].fillna(0).astype(int)
    tabela["pct"] = tabela["n"] / max(len(p), 1)

    if pesos is not None:
        volume = (
            pd.DataFrame({"score": scores, "peso": np.asarray(pesos, dtype=float)})
            .groupby("score")["peso"]
            .sum()
        )
        tabela = tabela.merge(volume.rename("volume"), on="score", how="left")
        tabela["volume"] = tabela["volume"].fillna(0.0)

    return tabela
