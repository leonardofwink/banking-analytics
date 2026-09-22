"""S09.5 · Testes da tabela de política.

Dois grupos: os que travam a **coerência da tabela** (monotonicidade, campos
vazios nos negados) e os que verificam que a **política escolhida** respeita os
guard-rails nos três cenários.

O segundo grupo é o que impede uma regressão silenciosa: se alguém mexer nos
cortes de score, nas tabelas de perda ou nas elasticidades, a política
escolhida pode deixar de ser viável — e isso tem de aparecer aqui, não na
apuração do dia 26.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from banking.dados import ALVO, carregar_processada, preparar_base_c
from banking.modelo import treinar_modelo_final
from banking.perda import fator_ead, lgd
from banking.politica import (
    COLUNAS_POLITICA,
    POLITICA_ESCOLHIDA,
    gerar_politica,
    validar_monotonicidade,
)
from banking.roi import CENARIOS, GUARD_RAILS, aplicar_politica, simular
from banking.score import SCORE_MAXIMO, SCORE_MINIMO, score_de_pd

PERDA_EXEMPLO = {10: 0.0134, 9: 0.0207, 8: 0.0292, 7: 0.0407, 6: 0.0577,
                 5: 0.0792, 4: 0.1118, 3: 0.1561, 2: 0.2128, 1: 0.3331}


@pytest.fixture(scope="module")
def contexto():
    """Base C escorada e perda esperada por faixa — o insumo real da política."""
    try:
        base_a = carregar_processada("A")
        base_c = carregar_processada("C")
    except FileNotFoundError as erro:
        pytest.skip(str(erro))

    modelo = treinar_modelo_final(base_a)
    escorar = lambda df: modelo.predict_proba(df)[:, 1]

    propostas = preparar_base_c(base_c)
    propostas["pd"] = escorar(propostas)
    el = (
        propostas["pd"]
        * fator_ead(propostas["prazo_meses"], propostas["ltv"])
        * lgd(propostas["idade_veiculo_anos"], propostas["ltv"], propostas["possui_avalista"])
    )
    perda = (
        pd.DataFrame({"score": score_de_pd(propostas["pd"]), "el": el})
        .groupby("score")["el"].mean().to_dict()
    )
    return propostas, perda, escorar


# --- A tabela ----------------------------------------------------------------
def test_tabela_tem_dez_linhas_e_as_colunas_do_professor() -> None:
    p = gerar_politica(7, 0.018, 0.1, 48, 0.1, 0.02, PERDA_EXEMPLO)
    assert len(p) == SCORE_MAXIMO - SCORE_MINIMO + 1
    assert tuple(p.columns) == COLUNAS_POLITICA
    assert sorted(p["score"]) == list(range(SCORE_MINIMO, SCORE_MAXIMO + 1))


def test_negados_saem_com_campos_vazios() -> None:
    """O CSV do professor exige taxa, prazo e entrada em branco no NEGAR."""
    p = gerar_politica(7, 0.018, 0.1, 48, 0.1, 0.02, PERDA_EXEMPLO)
    negados = p[p["decisao"] == "NEGAR"]
    assert len(negados) == 6
    assert negados[["taxa_am", "prazo_meses", "pct_entrada_minima"]].isna().all().all()


def test_monotonicidade_por_construcao() -> None:
    """A parametrização não consegue gerar tabela incoerente.

    Vale para toda a grade da busca — é o que permitiu varrer 960 combinações
    sem precisar filtrar inversões.
    """
    for corte in (7, 6, 5, 4):
        for k in (0.0, 0.1, 0.2, 0.3):
            for passo in (0.0, 0.04):
                p = gerar_politica(corte, 0.016, k, 48, 0.05, passo, PERDA_EXEMPLO)
                assert validar_monotonicidade(p) == [], f"corte={corte} k={k} passo={passo}"


def test_k_risco_zero_reproduz_a_politica_antiga() -> None:
    """O contrafactual: preço único para todo risco.

    É exatamente o que a AutoCred fazia — 1,57% para quem tinha 0,2% de default
    e 1,64% para quem tinha 69,6%. Manter esse caso na parametrização permitiu
    compará-lo com precificação por risco dentro da mesma busca.
    """
    p = gerar_politica(5, 0.018, 0.0, 48, 0.1, 0.0, PERDA_EXEMPLO)
    aprovadas = p[p["decisao"] == "APROVAR"]
    assert aprovadas["taxa_am"].nunique() == 1


def test_k_risco_positivo_precifica_risco() -> None:
    p = gerar_politica(5, 0.015, 0.1, 48, 0.1, 0.0, PERDA_EXEMPLO)
    aprovadas = p[p["decisao"] == "APROVAR"].sort_values("score", ascending=False)
    taxas = aprovadas["taxa_am"].to_numpy()
    assert np.all(np.diff(taxas) > 0), "a taxa deveria subir conforme o score piora"


def test_taxa_e_truncada_no_teto_do_conselho() -> None:
    """3,5% a.m. é truncamento automático, não erro."""
    p = gerar_politica(1, 0.030, 1.0, 48, 0.0, 0.0, PERDA_EXEMPLO)
    assert p["taxa_am"].max() <= GUARD_RAILS["taxa_maxima"] + 1e-9


# --- O validador de coerência ------------------------------------------------
def test_validador_pega_taxa_invertida() -> None:
    p = gerar_politica(7, 0.018, 0.1, 48, 0.1, 0.0, PERDA_EXEMPLO)
    p.loc[p["score"] == 10, "taxa_am"] = 0.030  # melhor cliente pagando mais
    problemas = validar_monotonicidade(p)
    assert any("taxa" in x for x in problemas)


def test_validador_pega_entrada_invertida() -> None:
    p = gerar_politica(7, 0.018, 0.1, 48, 0.05, 0.02, PERDA_EXEMPLO)
    p.loc[p["score"] == 10, "pct_entrada_minima"] = 0.50
    assert any("entrada" in x for x in validar_monotonicidade(p))


def test_validador_pega_aprovacao_com_buraco() -> None:
    """Aprovar o score 8 e negar o 9 seria incoerente com a própria ordenação."""
    p = gerar_politica(7, 0.018, 0.1, 48, 0.1, 0.0, PERDA_EXEMPLO)
    p.loc[p["score"] == 9, ["decisao", "taxa_am", "prazo_meses", "pct_entrada_minima"]] = [
        "NEGAR", np.nan, np.nan, np.nan
    ]
    assert any("contígua" in x for x in validar_monotonicidade(p))


def test_validador_pega_negado_com_campo_preenchido() -> None:
    p = gerar_politica(7, 0.018, 0.1, 48, 0.1, 0.0, PERDA_EXEMPLO)
    p.loc[p["score"] == 1, "taxa_am"] = 0.03
    assert any("negada" in x for x in validar_monotonicidade(p))


# --- A política escolhida ----------------------------------------------------
def test_politica_escolhida_e_coerente(contexto) -> None:
    _, perda, _ = contexto
    p = gerar_politica(**POLITICA_ESCOLHIDA, perda_por_faixa=perda)
    assert validar_monotonicidade(p) == []


def test_politica_escolhida_precifica_risco(contexto) -> None:
    """A razão de ela ter sido preferida entre as quase-empatadas.

    Preço único é indefensável diante da pergunta «por que cobrou o que
    cobrou» — e é a patologia que o conselho diagnosticou na política antiga.
    """
    _, perda, _ = contexto
    p = gerar_politica(**POLITICA_ESCOLHIDA, perda_por_faixa=perda)
    aprovadas = p[p["decisao"] == "APROVAR"]
    assert aprovadas["taxa_am"].nunique() == len(aprovadas), "cada faixa tem o seu preço"


def test_politica_escolhida_respeita_os_guard_rails_nos_tres_cenarios(contexto) -> None:
    """O teste que impede regressão silenciosa.

    Se alguém mexer nos cortes de score, nas tabelas de perda ou nas
    elasticidades, a política pode deixar de ser viável. Isso tem de aparecer
    aqui, e não na apuração do dia 26.
    """
    propostas, perda, escorar = contexto
    p = gerar_politica(**POLITICA_ESCOLHIDA, perda_por_faixa=perda)
    ofertas = aplicar_politica(propostas, p, escorar=escorar)

    for nome in CENARIOS:
        r = simular(ofertas, nome)
        assert not r.violacoes, f"cenário {nome}: {r.violacoes}"
        assert r.taxa_aprovacao >= GUARD_RAILS["aprovacao_minima"]
        assert r.inadimplencia <= GUARD_RAILS["inadimplencia_maxima"]
        assert r.volume_originado >= GUARD_RAILS["volume_minimo"]


def test_politica_escolhida_tem_folga_no_pior_cenario(contexto) -> None:
    """Não basta passar: tem de passar com margem.

    Uma política que fica a 0,1 ponto de furar o limite não é robusta — a
    intensidade real do aceite é desconhecida, e só submetemos uma vez.
    """
    propostas, perda, escorar = contexto
    p = gerar_politica(**POLITICA_ESCOLHIDA, perda_por_faixa=perda)
    pior = simular(aplicar_politica(propostas, p, escorar=escorar), "pessimista")

    assert pior.volume_originado >= GUARD_RAILS["volume_minimo"] * 1.05
    assert pior.inadimplencia <= GUARD_RAILS["inadimplencia_maxima"] * 0.95
