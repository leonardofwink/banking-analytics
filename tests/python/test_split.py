"""S03.6 · Testes do split temporal.

O split é a decisão que torna a validação honesta. Se ele vazar — um contrato
nos dois lados, ou uma data de validação anterior ao treino — o AuROC medido
não significa nada, e o erro não aparece em lugar nenhum.
"""

from __future__ import annotations

import pandas as pd
import pytest

from banking.dados import ALVO, carregar_processada
from banking.split import ANO_VALIDACAO, dividir_temporal, resumo_split


@pytest.fixture(scope="module")
def base_a() -> pd.DataFrame:
    try:
        return carregar_processada("A")
    except FileNotFoundError as erro:
        pytest.skip(str(erro))


def test_contagens_do_split(base_a) -> None:
    treino, validacao = dividir_temporal(base_a)
    assert len(treino) == 6_670
    assert len(validacao) == 3_330
    assert len(treino) + len(validacao) == len(base_a), "nenhum contrato pode se perder"


def test_nenhum_contrato_nos_dois_lados(base_a) -> None:
    """Sobreposição é vazamento: o modelo veria na validação o que treinou."""
    treino, validacao = dividir_temporal(base_a)
    assert set(treino["id_contrato"]) & set(validacao["id_contrato"]) == set()


def test_treino_e_inteiramente_anterior_a_validacao(base_a) -> None:
    """A fronteira temporal é o que torna a validação out-of-time.

    Se um contrato de 2024 caísse no treino, o modelo aprenderia com o futuro
    — que é exatamente o que o enunciado avisa para não fazer.
    """
    treino, validacao = dividir_temporal(base_a)
    assert pd.to_datetime(treino["data_originacao"]).max() < pd.to_datetime(
        validacao["data_originacao"]
    ).min()


def test_validacao_e_o_ano_declarado(base_a) -> None:
    _, validacao = dividir_temporal(base_a)
    anos = pd.to_datetime(validacao["data_originacao"]).dt.year.unique()
    assert list(anos) == [ANO_VALIDACAO]


def test_split_e_deterministico(base_a) -> None:
    """Duas chamadas produzem a mesma partição — sem isso nada é reproduzível."""
    t1, v1 = dividir_temporal(base_a)
    t2, v2 = dividir_temporal(base_a)
    assert t1["id_contrato"].tolist() == t2["id_contrato"].tolist()
    assert v1["id_contrato"].tolist() == v2["id_contrato"].tolist()


def test_split_nao_altera_a_base_original(base_a) -> None:
    """Devolve cópias: efeito colateral sobre a base do chamador é armadilha."""
    antes = len(base_a)
    treino, _ = dividir_temporal(base_a)
    treino["coluna_nova"] = 1
    assert len(base_a) == antes
    assert "coluna_nova" not in base_a.columns


def test_ano_sem_dado_falha_claro(base_a) -> None:
    """Split degenerado tem que gritar, não devolver conjunto vazio."""
    with pytest.raises(ValueError, match="degenerado"):
        dividir_temporal(base_a, ano_validacao=2030)


def test_coluna_de_data_ausente_falha_claro() -> None:
    with pytest.raises(ValueError, match="data_originacao"):
        dividir_temporal(pd.DataFrame({"x": [1, 2, 3]}))


def test_resumo_traz_as_taxas_de_default(base_a) -> None:
    """A prevalência difere entre treino e validação — e isso é esperado.

    É a razão de compararmos modelos por AuROC e KS (ordenação) e não por
    acurácia, que depende da prevalência.
    """
    treino, validacao = dividir_temporal(base_a)
    resumo = resumo_split(treino, validacao)
    assert list(resumo["particao"]) == ["treino", "validação"]
    assert resumo.loc[0, "taxa_default"] == pytest.approx(treino[ALVO].mean())
    assert resumo.loc[1, "taxa_default"] == pytest.approx(validacao[ALVO].mean())
