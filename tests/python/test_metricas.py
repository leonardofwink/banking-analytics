"""S03.6 · Testes das métricas de crédito (KS, IV/WOE, PSI).

Métrica errada não levanta exceção: devolve um número plausível e a decisão
inteira sai torta. Por isso cada uma é testada contra casos de **resposta
conhecida** — separação perfeita, separação nula, distribuições idênticas —
antes de ser usada em dado real.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from banking.metricas import classificar_iv, classificar_psi, iv, ks, psi, tabela_woe


# --- KS ----------------------------------------------------------------------
def test_ks_de_separacao_perfeita_e_um() -> None:
    """Score que separa os dois grupos sem sobreposição tem KS = 1."""
    alvo = [0] * 50 + [1] * 50
    score = list(np.linspace(0.0, 0.4, 50)) + list(np.linspace(0.6, 1.0, 50))
    assert ks(alvo, score) == pytest.approx(1.0)


def test_ks_de_score_aleatorio_e_proximo_de_zero() -> None:
    """Score sem informação não separa nada."""
    rng = np.random.default_rng(42)
    alvo = rng.integers(0, 2, 5_000)
    score = rng.random(5_000)
    assert ks(alvo, score) < 0.10


def test_ks_e_simetrico_a_inversao_do_score() -> None:
    """Inverter o sinal do score não muda o KS — ele mede separação, não direção.

    Consequência prática: o KS não avisa se você inverteu a convenção. Quem
    garante a direção é a leitura do corte, não a métrica.
    """
    alvo = [0, 0, 0, 1, 1, 1]
    score = [0.1, 0.2, 0.3, 0.7, 0.8, 0.9]
    assert ks(alvo, score) == pytest.approx(ks(alvo, [-s for s in score]))


def test_ks_exige_as_duas_classes() -> None:
    with pytest.raises(ValueError, match="duas classes"):
        ks([1, 1, 1], [0.1, 0.2, 0.3])


# --- IV / WOE ----------------------------------------------------------------
def test_iv_de_variavel_sem_relacao_e_quase_zero() -> None:
    rng = np.random.default_rng(42)
    alvo = rng.integers(0, 2, 5_000)
    ruido = rng.random(5_000)
    assert iv(ruido, alvo) < 0.02


def test_iv_de_variavel_forte_e_alto() -> None:
    """Variável que quase determina o alvo tem IV grande — e isso é suspeito.

    Em crédito, IV muito alto quase sempre significa vazamento: uma variável
    que só existe depois da concessão.
    """
    rng = np.random.default_rng(42)
    alvo = rng.integers(0, 2, 5_000)
    quase_o_alvo = alvo + rng.normal(0, 0.1, 5_000)
    assert iv(quase_o_alvo, alvo) > 0.5
    assert classificar_iv(iv(quase_o_alvo, alvo)) == "suspeito de vazamento"


def test_woe_positivo_onde_ha_menos_default() -> None:
    """WOE = ln(%bons / %maus): positivo = faixa melhor que a média."""
    variavel = ["bom"] * 100 + ["ruim"] * 100
    alvo = [0] * 95 + [1] * 5 + [0] * 50 + [1] * 50
    tab = tabela_woe(variavel, alvo).set_index("faixa")
    assert tab.loc["bom", "woe"] > 0
    assert tab.loc["ruim", "woe"] < 0


def test_nulo_vira_categoria_propria() -> None:
    """Ausência é informação de risco, não ruído.

    Quem não tem score de bureau não é um cliente médio: é alguém sem
    histórico. Imputar pela mediana apagaria esse sinal, então a tabela de WOE
    trata o nulo como faixa própria.
    """
    variavel = [1.0, 2.0, 3.0, np.nan, np.nan]
    alvo = [0, 0, 0, 1, 1]
    tab = tabela_woe(variavel, alvo)
    assert "(ausente)" in tab["faixa"].astype(str).tolist()


# --- PSI ---------------------------------------------------------------------
def test_psi_de_distribuicoes_identicas_e_zero() -> None:
    rng = np.random.default_rng(42)
    x = rng.normal(size=5_000)
    assert psi(x, x) == pytest.approx(0.0, abs=1e-6)


def test_psi_cresce_com_o_deslocamento() -> None:
    """Quanto mais a população se move, maior o PSI."""
    rng = np.random.default_rng(42)
    ref = rng.normal(0, 1, 10_000)
    pouco = rng.normal(0.1, 1, 10_000)
    muito = rng.normal(2.0, 1, 10_000)
    assert psi(ref, pouco) < psi(ref, muito)
    assert psi(ref, muito) > 0.25


def test_psi_nao_olha_o_alvo() -> None:
    """PSI compara distribuições, não performance — por isso funciona na base C,
    que não tem alvo nenhum."""
    rng = np.random.default_rng(42)
    x = rng.normal(size=1_000)
    y = rng.normal(size=1_000)
    assert psi(x, y) >= 0


def test_psi_detecta_mudanca_de_ausencia() -> None:
    """Uma base com muito mais nulo que a outra JÁ é instabilidade."""
    ref = pd.Series([1.0] * 90 + [np.nan] * 10)
    atual = pd.Series([1.0] * 50 + [np.nan] * 50)
    assert psi(ref, atual) > 0.25


def test_classificacoes() -> None:
    assert classificar_psi(0.05) == "estável"
    assert classificar_psi(0.15) == "atenção"
    assert classificar_psi(3.0).startswith("instável")
    assert classificar_iv(0.01) == "sem poder"
    assert classificar_iv(0.15) == "médio"


# --- Integração com o dado real ----------------------------------------------
def test_psi_confirma_que_a_base_c_e_outro_mundo() -> None:
    """O risco nº 1 do projeto, medido.

    As bases A e B são de contratos aprovados pela política antiga, e a C é
    mar aberto. O PSI quantifica: A→B é praticamente idêntico, A→C explode em
    `qtd_restricoes_ativas` e `score_bureau` — justamente as duas variáveis
    mais preditivas. É onde o modelo vai extrapolar.
    """
    from banking.dados import carregar_processada

    try:
        a, b, c = (carregar_processada(x) for x in "ABC")
    except FileNotFoundError as erro:
        pytest.skip(str(erro))

    for coluna in ("score_bureau", "qtd_restricoes_ativas"):
        assert psi(a[coluna], b[coluna]) < 0.1, f"{coluna}: A e B deveriam ser parecidas"
        assert psi(a[coluna], c[coluna]) > 0.25, f"{coluna}: A e C deveriam divergir"
