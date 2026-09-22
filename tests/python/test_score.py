"""S07.5 · Testes das faixas de score.

A faixa é o eixo da tabela de política: toda decisão de taxa, prazo e entrada
é indexada por ela. Um erro aqui não produz exceção — produz uma tabela de
preços coerente consigo mesma e errada em relação ao risco.
"""

from __future__ import annotations

import numpy as np
import pytest

from banking.dados import carregar_processada
from banking.modelo import treinar_modelo_final
from banking.score import (
    CORTES_PD,
    SCORE_MAXIMO,
    SCORE_MINIMO,
    faixa_de_score,
    score_de_pd,
    tabela_de_faixas,
)

OCUPACAO_MINIMA = 0.03


@pytest.fixture(scope="module")
def pd_base_c() -> np.ndarray:
    """PDs reais da base C, escoradas pelo modelo final."""
    try:
        base_a = carregar_processada("A")
        base_c = carregar_processada("C")
    except FileNotFoundError as erro:
        pytest.skip(str(erro))

    modelo = treinar_modelo_final(base_a)
    c = base_c.rename(
        columns={
            "ltv_desejado": "ltv",
            "prazo_desejado_meses": "prazo_meses",
            "valor_financiado_desejado": "valor_financiado",
        }
    )
    return modelo.predict_proba(c)[:, 1]


# --- A convenção do enunciado ------------------------------------------------
def test_dez_e_o_melhor_risco() -> None:
    """10 = menor PD, 1 = maior. Inverter isso inverteria a tabela de preços inteira."""
    assert score_de_pd([0.001])[0] == SCORE_MAXIMO
    assert score_de_pd([0.90])[0] == SCORE_MINIMO


def test_score_e_monotonicamente_decrescente_na_pd() -> None:
    """PD maior nunca pode receber score melhor."""
    pds = np.linspace(0.001, 0.999, 500)
    scores = score_de_pd(pds)
    assert np.all(np.diff(scores) <= 0)


def test_todas_as_dez_faixas_sao_alcancaveis() -> None:
    pds = np.linspace(0.0, 1.0, 10_000)
    assert set(np.unique(score_de_pd(pds))) == set(range(SCORE_MINIMO, SCORE_MAXIMO + 1))


# --- Bordas ------------------------------------------------------------------
def test_intervalos_fechados_a_direita() -> None:
    """Mesma convenção das faixas de LTV do S02 — consistência importa.

    Uma PD de exatamente 2,5% é score 10; 2,51% já é score 9.
    """
    assert score_de_pd([0.025])[0] == 10
    assert score_de_pd([0.0251])[0] == 9
    assert score_de_pd([0.035])[0] == 9
    assert score_de_pd([0.070])[0] == 7
    assert score_de_pd([0.350])[0] == 2
    assert score_de_pd([0.3501])[0] == 1


def test_faixa_de_score_e_o_inverso_de_score_de_pd() -> None:
    """Toda PD dentro do intervalo declarado tem que devolver aquele score."""
    for score in range(SCORE_MINIMO, SCORE_MAXIMO + 1):
        minimo, maximo = faixa_de_score(score)
        # Um ponto seguramente dentro da faixa (evita as bordas).
        meio = (minimo + maximo) / 2
        assert score_de_pd([meio])[0] == score, f"faixa {score} não fecha em {meio:.4f}"


def test_faixas_cobrem_todo_o_intervalo_sem_buraco() -> None:
    """O topo de uma faixa é o piso da seguinte — sem lacuna, sem sobreposição."""
    limites = [faixa_de_score(s) for s in range(SCORE_MAXIMO, SCORE_MINIMO - 1, -1)]
    assert limites[0][0] == 0.0, "a melhor faixa deve começar em zero"
    assert limites[-1][1] == 1.0, "a pior faixa deve terminar em um"
    for (_, topo), (piso, _) in zip(limites, limites[1:]):
        assert topo == piso


# --- Guardas de unidade ------------------------------------------------------
def test_pd_em_percentual_e_recusada() -> None:
    """`8.5` em vez de `0.085` jogaria todo mundo no score 1."""
    with pytest.raises(ValueError, match=r"fora de \[0, 1\]"):
        score_de_pd([8.5])


def test_pd_nula_e_recusada() -> None:
    """Sem score não há decisão de política: a proposta ficaria sem linha."""
    with pytest.raises(ValueError, match="nulas"):
        score_de_pd([0.05, np.nan])


def test_score_e_deterministico() -> None:
    pds = np.linspace(0.01, 0.9, 100)
    assert np.array_equal(score_de_pd(pds), score_de_pd(pds))


# --- Os critérios declarados na spec -----------------------------------------
def test_nenhuma_faixa_e_irrelevante_na_base_c(pd_base_c) -> None:
    """Critério 2 da spec: faixa com menos de 3% não sustenta decisão de preço.

    É o teste que justifica os cortes escolhidos. Se alguém mexer em
    `CORTES_PD` e esvaziar uma faixa, aparece aqui — não na tabela de política.
    """
    tabela = tabela_de_faixas(pd_base_c)
    vazias = tabela[tabela["pct"] < OCUPACAO_MINIMA]
    assert vazias.empty, (
        f"faixas abaixo de {OCUPACAO_MINIMA:.0%} da base C: "
        f"{vazias[['score', 'pct']].to_dict('records')}"
    )


def test_pd_media_cresce_conforme_o_score_piora(pd_base_c) -> None:
    """Sanidade: a faixa 1 tem que ter PD média maior que a faixa 10."""
    tabela = tabela_de_faixas(pd_base_c).sort_values("score", ascending=False)
    assert np.all(np.diff(tabela["pd_media"].to_numpy()) > 0)


def test_cortes_estao_em_ordem_crescente() -> None:
    """Cortes fora de ordem quebrariam o searchsorted silenciosamente."""
    assert list(CORTES_PD) == sorted(CORTES_PD)
    assert len(CORTES_PD) == SCORE_MAXIMO - SCORE_MINIMO


def test_a_janela_de_aprovacao_viavel_existe(pd_base_c) -> None:
    """Tem que haver ao menos um corte que respeite aprovação e inadimplência.

    Se nenhum corte servisse, os cortes de PD estariam mal calibrados para
    esta base e a política não teria ponto de partida.
    """
    scores = score_de_pd(pd_base_c)
    viaveis = [
        corte
        for corte in range(SCORE_MINIMO, SCORE_MAXIMO + 1)
        if (scores >= corte).mean() >= 0.35 and pd_base_c[scores >= corte].mean() <= 0.08
    ]
    assert viaveis, "nenhum corte de aprovação respeita os guard-rails"
