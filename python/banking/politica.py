"""S09 · A tabela de política — de seis parâmetros a dez linhas.

Uma política de crédito é **uma tabela de regras**, não um modelo. Dez linhas,
uma por faixa de score, dizendo aprovar ou negar, a que taxa, em que prazo e
com quanta entrada.

Deixar as 40 células livres seria espaço grande demais para buscar e impossível
de defender. Aqui, **seis parâmetros geram a tabela inteira**, e cada um tem
significado de negócio — o que também garante a monotonicidade por construção.

A regra de preço é o coração::

    taxa = taxa_base + k_risco × perda_esperada_da_faixa

Precificação baseada em risco — exatamente o que a política antiga **não**
fazia: ela cobrava 1,57% de quem tinha 0,2% de default e 1,64% de quem tinha
69,6%. Com ``k_risco = 0`` esta função reproduz aquela política, o que a torna
um contrafactual útil dentro da própria busca.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from banking.roi import GUARD_RAILS
from banking.score import SCORE_MAXIMO, SCORE_MINIMO, faixa_de_score

__all__ = [
    "COLUNAS_POLITICA",
    "POLITICA_ESCOLHIDA",
    "descrever",
    "gerar_politica",
    "validar_monotonicidade",
]

COLUNAS_POLITICA = (
    "score",
    "decisao",
    "taxa_am",
    "prazo_meses",
    "pct_entrada_minima",
)

# Piso de entrada: mesmo na melhor faixa não faz sentido financiar 100% do bem
# — o LTV iria a 1,0, que é a pior célula de todas as tabelas de LGD.
ENTRADA_MAXIMA = 0.60


def gerar_politica(
    corte: int,
    taxa_base: float,
    k_risco: float,
    prazo_max: int,
    entrada_base: float,
    entrada_passo: float,
    perda_por_faixa: dict[int, float] | pd.Series | None = None,
) -> pd.DataFrame:
    """Gera a tabela de política a partir dos seis parâmetros.

    :param corte: menor score aprovado. Faixas abaixo recebem ``NEGAR``.
    :param taxa_base: taxa mensal da melhor faixa, em fração.
    :param k_risco: quanto a taxa sobe por unidade de perda esperada da faixa.
        ``0`` reproduz a política antiga — preço igual para todo risco.
    :param prazo_max: teto de prazo. O cliente recebe o **menor** entre o que
        pediu e este valor: a alavanca do enunciado é "prazo máximo".
    :param entrada_base: entrada mínima da melhor faixa.
    :param entrada_passo: quanto a exigência sobe a cada faixa pior.
    :param perda_por_faixa: perda esperada de cada score. Sem ela, a taxa não
        varia com o risco.
    :return: DataFrame com as dez linhas e as colunas de :data:`COLUNAS_POLITICA`.
    """
    linhas = []
    for score in range(SCORE_MAXIMO, SCORE_MINIMO - 1, -1):
        aprovada = score >= corte
        degraus = SCORE_MAXIMO - score  # 0 na melhor faixa

        if not aprovada:
            linhas.append(
                {
                    "score": score,
                    "decisao": "NEGAR",
                    "taxa_am": np.nan,
                    "prazo_meses": np.nan,
                    "pct_entrada_minima": np.nan,
                }
            )
            continue

        perda = 0.0
        if perda_por_faixa is not None:
            perda = float(perda_por_faixa.get(score, 0.0))

        taxa = taxa_base + k_risco * perda
        # O teto do conselho é truncamento automático, não erro — mas uma
        # política que encosta nele está precificando acima do que o mercado
        # aceita de qualquer jeito.
        taxa = min(taxa, GUARD_RAILS["taxa_maxima"])

        entrada = min(entrada_base + entrada_passo * degraus, ENTRADA_MAXIMA)

        linhas.append(
            {
                "score": score,
                "decisao": "APROVAR",
                "taxa_am": round(taxa, 6),
                "prazo_meses": int(prazo_max),
                "pct_entrada_minima": round(entrada, 4),
            }
        )

    return pd.DataFrame(linhas, columns=list(COLUNAS_POLITICA))


def validar_monotonicidade(politica: pd.DataFrame) -> list[str]:
    """Confere que score melhor nunca recebe condição pior.

    Não é preciosismo estético: é o que torna a tabela defensável. Qualquer
    inversão exigiria explicar ao conselho por que um cliente de menor risco
    paga mais caro, ou precisa dar mais entrada, que um de risco maior.

    :return: lista de problemas. Vazia quando a tabela está coerente.
    """
    problemas: list[str] = []
    aprovadas = politica[politica["decisao"] == "APROVAR"].sort_values(
        "score", ascending=False
    )

    if aprovadas.empty:
        return ["nenhuma faixa aprovada"]

    # Aprovação tem de ser um bloco contíguo no topo: aprovar o score 8 e
    # negar o 9 seria incoerente com a própria ordenação do modelo.
    scores_aprovados = sorted(aprovadas["score"].tolist(), reverse=True)
    esperado = list(range(SCORE_MAXIMO, SCORE_MAXIMO - len(scores_aprovados), -1))
    if scores_aprovados != esperado:
        problemas.append(
            f"aprovação não é contígua no topo: {scores_aprovados} (esperado {esperado})"
        )

    taxas = aprovadas["taxa_am"].to_numpy(dtype=float)
    if np.any(np.diff(taxas) < -1e-9):
        problemas.append("a taxa cai conforme o score piora — cliente pior pagando menos")

    entradas = aprovadas["pct_entrada_minima"].to_numpy(dtype=float)
    if np.any(np.diff(entradas) < -1e-9):
        problemas.append("a entrada exigida cai conforme o score piora")

    prazos = aprovadas["prazo_meses"].to_numpy(dtype=float)
    if np.any(np.diff(prazos) > 1e-9):
        problemas.append("o prazo máximo cresce conforme o score piora")

    negadas = politica[politica["decisao"] == "NEGAR"]
    if not negadas[["taxa_am", "prazo_meses", "pct_entrada_minima"]].isna().all().all():
        problemas.append("faixa negada com taxa, prazo ou entrada preenchidos")

    return problemas


def descrever(politica: pd.DataFrame, perda_por_faixa=None) -> pd.DataFrame:
    """Acrescenta a faixa de PD e a razão de cada linha — o insumo da defesa.

    Cada decisão da tabela precisa de uma frase que a explique. Sem isso, a
    apresentação vira leitura de números.
    """
    descrita = politica.copy()
    descrita["faixa_pd"] = descrita["score"].map(
        lambda s: "{:.1%} – {:.1%}".format(*faixa_de_score(int(s)))
    )

    if perda_por_faixa is not None:
        descrita["perda_esperada"] = descrita["score"].map(
            lambda s: perda_por_faixa.get(int(s), np.nan)
        )
        # Quantas vezes a taxa cobre a perda esperada amortizada no prazo.
        with np.errstate(divide="ignore", invalid="ignore"):
            descrita["cobertura"] = descrita["taxa_am"] * descrita["prazo_meses"] / (
                descrita["perda_esperada"]
            )

    return descrita


# --- A política escolhida (S09) ----------------------------------------------
# A busca do S09 avaliou 960 combinações nos três cenários e devolveu 70
# viáveis. Entre as dez melhores, a diferença de ROI é de 0,2 ponto percentual
# — quase-empate. Nesse ponto a escolha deixa de ser técnica e vira **apetite a
# risco**, e foi tomada pelo responsável pela frente de política.
#
# Por que esta, entre as quase-empatadas:
#
#   · precifica risco (k_risco = 0,10). Duas das candidatas empatadas usavam
#     preço único, e preço único é exatamente a patologia que o conselho
#     diagnosticou — além de ser indefensável diante da pergunta "por que
#     cobrou o que cobrou".
#   · fica a 0,1 ponto do ROI máximo, com quase o dobro de folga (12,7% contra
#     7,7%) até o guard-rail mais apertado.
#   · a inadimplência no pior cenário fica em 6,6%, contra 7,4% da alternativa
#     de ROI máximo — 1,4 ponto abaixo do limite de 8%, e não 0,6.
POLITICA_ESCOLHIDA = {
    "corte": 5,
    "taxa_base": 0.0150,
    "k_risco": 0.10,
    "prazo_max": 48,
    "entrada_base": 0.10,
    "entrada_passo": 0.0,
}
