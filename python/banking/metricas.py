"""S03.2 · Métricas de crédito — KS, IV/WOE e PSI.

Três perguntas diferentes, que é fácil confundir:

- **KS e AuROC** — *o modelo ordena bem?* Separa quem paga de quem não paga.
- **IV** — *esta variável, sozinha, tem poder preditivo?* Usada na seleção.
- **PSI** — *a população mudou?* Compara duas bases, sem olhar o alvo.

⚠️ **Convenção:** "mau" é o evento de interesse (``alvo == 1``, o default) e
"bom" é ``alvo == 0``. Inverter isso troca o sinal do WOE e inverte a leitura
de todas as tabelas.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = [
    "REFERENCIA_IV",
    "REFERENCIA_PSI",
    "classificar_iv",
    "classificar_psi",
    "iv",
    "ks",
    "psi",
    "tabela_woe",
]

# Referências de leitura usuais no mercado de crédito. São convenções, não leis.
REFERENCIA_IV = {
    0.02: "sem poder",
    0.10: "fraco",
    0.30: "médio",
    0.50: "forte",
    float("inf"): "suspeito de vazamento",
}

REFERENCIA_PSI = {
    0.10: "estável",
    0.25: "atenção",
    float("inf"): "instável — a população mudou",
}

# Evita divisão por zero e log(0) em faixas sem bons ou sem maus. Pequeno o
# bastante para não deslocar o resultado, grande o bastante para estabilizar.
_EPS = 1e-10


def ks(alvo, score) -> float:
    """Kolmogorov-Smirnov: a máxima distância entre as acumuladas de bons e maus.

    É a métrica preferida do mercado de crédito porque responde direto à
    pergunta operacional: *existe um ponto de corte que separa bem os dois
    grupos, e quão bem?*

    :param alvo: 1 = default (mau), 0 = adimplente (bom).
    :param score: probabilidade de default ou qualquer score em que **maior
        significa mais risco**. Se o seu score for invertido, o KS sai igual —
        ele é simétrico —, mas a leitura do corte não.
    :return: KS entre 0 e 1. Crédito bom costuma ficar entre 0,25 e 0,45.
    """
    y = np.asarray(alvo, dtype=float)
    s = np.asarray(score, dtype=float)
    if len(np.unique(y)) < 2:
        raise ValueError("KS exige as duas classes: só há uma no alvo recebido.")

    ordem = np.argsort(s)
    y = y[ordem]
    maus = np.cumsum(y) / max(y.sum(), _EPS)
    bons = np.cumsum(1 - y) / max((1 - y).sum(), _EPS)
    return float(np.max(np.abs(bons - maus)))


def tabela_woe(
    variavel, alvo, n_faixas: int = 10, rotulos=None
) -> pd.DataFrame:
    """Tabela de WOE por faixa — o detalhe por trás do IV.

    **WOE** (*Weight of Evidence*) é ``ln(%bons / %maus)`` na faixa. Positivo =
    a faixa tem mais bons que a média; negativo = mais maus. É a transformação
    clássica de scorecard porque lineariza a relação com o log-odds e trata
    valor ausente como uma categoria própria, em vez de exigir imputação.

    :param variavel: série numérica (será cortada em quantis) ou categórica.
    :param alvo: 1 = default.
    :param n_faixas: quantis, quando a variável é numérica.
    :return: uma linha por faixa, com contagens, taxa de default, WOE e a
        contribuição daquela faixa para o IV.
    """
    v = pd.Series(np.asarray(variavel).ravel()).reset_index(drop=True)
    y = pd.Series(np.asarray(alvo, dtype=float).ravel()).reset_index(drop=True)

    if rotulos is not None:
        faixa = pd.Series(rotulos).reset_index(drop=True)
    elif pd.api.types.is_numeric_dtype(v) and v.nunique(dropna=True) > n_faixas:
        # duplicates="drop": variáveis concentradas (muitos zeros) geram
        # bordas repetidas, e aí sobram menos faixas — o que é correto.
        faixa = pd.qcut(v, q=n_faixas, duplicates="drop")
    else:
        faixa = v

    # Nulo vira categoria própria: ausência de bureau é informação de risco,
    # não ruído. Perder isso é jogar sinal fora.
    faixa = faixa.astype(object).where(v.notna(), "(ausente)")

    grupos = pd.DataFrame({"faixa": faixa, "alvo": y}).groupby("faixa", observed=True)
    tab = grupos["alvo"].agg(n="size", maus="sum")
    tab["bons"] = tab["n"] - tab["maus"]
    tab["taxa_default"] = tab["maus"] / tab["n"]

    pct_maus = tab["maus"] / max(tab["maus"].sum(), _EPS)
    pct_bons = tab["bons"] / max(tab["bons"].sum(), _EPS)

    tab["woe"] = np.log((pct_bons + _EPS) / (pct_maus + _EPS))
    tab["iv_parcial"] = (pct_bons - pct_maus) * tab["woe"]
    return tab.reset_index()


def iv(variavel, alvo, n_faixas: int = 10) -> float:
    """Information Value: o poder preditivo da variável sozinha.

    Soma das contribuições de cada faixa. Referência usual:
    ``< 0,02`` sem poder · ``0,1–0,3`` médio · ``> 0,5`` **suspeito**.

    ⚠️ **Calcule sempre no treino.** Calcular no conjunto inteiro é espiar a
    validação: a variável passa a parecer boa porque viu a resposta.

    ⚠️ IV alto demais raramente é sorte. Em crédito, quase sempre significa
    vazamento — uma variável que só existe depois da concessão.
    """
    return float(tabela_woe(variavel, alvo, n_faixas)["iv_parcial"].sum())


def psi(referencia, atual, n_faixas: int = 10) -> float:
    """Population Stability Index: quanto a população mudou entre duas bases.

    Não olha o alvo — compara só a distribuição da variável. É o instrumento
    que dimensiona o risco central deste desafio: as bases A e B são de
    contratos aprovados pela política antiga, e a base C é mar aberto. O PSI
    diz **em quais variáveis** e **quanto** o modelo vai extrapolar.

    Referência: ``< 0,1`` estável · ``0,1–0,25`` atenção · ``> 0,25`` instável.

    :param referencia: a base em que o modelo foi treinado (A).
    :param atual: a base em que ele será aplicado (B ou C).
    :return: PSI ≥ 0. Zero significa distribuições idênticas.
    """
    ref = pd.Series(np.asarray(referencia).ravel())
    atu = pd.Series(np.asarray(atual).ravel())

    if pd.api.types.is_numeric_dtype(ref) and ref.nunique(dropna=True) > n_faixas:
        # As bordas saem da REFERÊNCIA, não do conjunto todo: o PSI mede o
        # deslocamento da base nova em relação à antiga, então a régua é a antiga.
        _, bordas = pd.qcut(ref.dropna(), q=n_faixas, retbins=True, duplicates="drop")
        bordas = np.concatenate(([-np.inf], bordas[1:-1], [np.inf]))
        cat_ref = pd.cut(ref, bins=bordas)
        cat_atu = pd.cut(atu, bins=bordas)
    else:
        cat_ref, cat_atu = ref, atu

    # Nulo é uma categoria: uma base com muito mais ausência que a outra JÁ é
    # instabilidade, e ignorar isso esconderia o problema.
    p_ref = cat_ref.astype(object).where(ref.notna(), "(ausente)").value_counts(normalize=True)
    p_atu = cat_atu.astype(object).where(atu.notna(), "(ausente)").value_counts(normalize=True)

    faixas = p_ref.index.union(p_atu.index)
    a = p_ref.reindex(faixas).fillna(0.0).to_numpy() + _EPS
    b = p_atu.reindex(faixas).fillna(0.0).to_numpy() + _EPS
    return float(np.sum((b - a) * np.log(b / a)))


def _classificar(valor: float, referencia: dict[float, str]) -> str:
    """Traduz um número em rótulo, pela primeira faixa que o contém."""
    for limite, rotulo in referencia.items():
        if valor < limite:
            return rotulo
    return list(referencia.values())[-1]


def classificar_iv(valor: float) -> str:
    """Rótulo de leitura do IV."""
    return _classificar(valor, REFERENCIA_IV)


def classificar_psi(valor: float) -> str:
    """Rótulo de leitura do PSI."""
    return _classificar(valor, REFERENCIA_PSI)
