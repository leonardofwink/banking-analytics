"""S06.6 · Testes do validador de submissão.

Um validador que aceita tudo é pior que nenhum: dá falsa segurança. Cada caso
aqui simula um jeito real de o arquivo sair errado — e todos têm que ser
recusados, com mensagem dizendo o quê.

O custo de deixar passar é a nota inteira do bloco: o professor roda o parser
dele depois do prazo, e aí não há conserto.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from banking.dados import carregar_processada
from banking.submissao import (
    COLUNAS_SUBMISSAO_MODELO,
    ValidacaoFalhou,
    formatar_submissao,
    resumo_distribuicao,
    validar_submissao_modelo,
)

N = 3_000


@pytest.fixture
def ids() -> pd.Series:
    return pd.Series([f"T{i:06d}" for i in range(1, N + 1)])


@pytest.fixture
def submissao_valida(ids) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    return pd.DataFrame({"id_contrato": ids, "pd": rng.beta(2, 20, N)})


def test_submissao_valida_passa(submissao_valida, ids) -> None:
    validar_submissao_modelo(submissao_valida, ids)  # não levanta


def test_linha_faltando_e_recusada(submissao_valida, ids) -> None:
    """Uma linha a menos deixa o cruzamento incompleto."""
    with pytest.raises(ValidacaoFalhou, match="linhas"):
        validar_submissao_modelo(submissao_valida.iloc[:-1], ids)


def test_id_desconhecido_e_recusado(submissao_valida, ids) -> None:
    adulterada = submissao_valida.copy()
    adulterada.loc[0, "id_contrato"] = "T999999"
    with pytest.raises(ValidacaoFalhou, match="não existem na base"):
        validar_submissao_modelo(adulterada, ids)


def test_id_duplicado_e_recusado(submissao_valida, ids) -> None:
    """Id repetido quebra o merge com o gabarito."""
    adulterada = submissao_valida.copy()
    adulterada.loc[1, "id_contrato"] = adulterada.loc[0, "id_contrato"]
    with pytest.raises(ValidacaoFalhou, match="duplicados"):
        validar_submissao_modelo(adulterada, ids)


def test_pd_em_percentual_e_recusada(submissao_valida, ids) -> None:
    """O erro de unidade clássico: 8.5 em vez de 0.085."""
    adulterada = submissao_valida.copy()
    adulterada["pd"] = adulterada["pd"] * 100
    with pytest.raises(ValidacaoFalhou, match=r"fora de \[0, 1\]"):
        validar_submissao_modelo(adulterada, ids)


def test_pd_nula_e_recusada(submissao_valida, ids) -> None:
    adulterada = submissao_valida.copy()
    adulterada.loc[0, "pd"] = np.nan
    with pytest.raises(ValidacaoFalhou, match="nulas"):
        validar_submissao_modelo(adulterada, ids)


def test_modelo_colapsado_e_recusado(ids) -> None:
    """O sintoma exato da armadilha do S01.

    Se `qtd_parcelas_em_atraso_12m` entrasse no modelo, ela valeria zero em
    toda a base B, o termo dominante viraria constante e todo mundo receberia
    praticamente a mesma PD. O AuROC cairia para ~0,5 sem nenhum erro aparecer.

    Este validador é a última barreira antes do envio: PD quase constante é
    recusada, mesmo que tudo o mais esteja formalmente correto.
    """
    degenerada = pd.DataFrame({"id_contrato": ids, "pd": np.full(N, 0.0826)})
    with pytest.raises(ValidacaoFalhou, match="colapsado|constante"):
        validar_submissao_modelo(degenerada, ids)


def test_colunas_erradas_sao_recusadas(submissao_valida, ids) -> None:
    """O parser do professor espera exatamente este cabeçalho."""
    renomeada = submissao_valida.rename(columns={"pd": "probabilidade"})
    with pytest.raises(ValidacaoFalhou, match="colunas"):
        validar_submissao_modelo(renomeada, ids)


def test_ordem_das_colunas_importa(submissao_valida, ids) -> None:
    invertida = submissao_valida[["pd", "id_contrato"]]
    with pytest.raises(ValidacaoFalhou, match="colunas"):
        validar_submissao_modelo(invertida, ids)


def test_arredondar_demais_cria_empate_e_derruba_o_auroc(submissao_valida) -> None:
    """Por que gravamos 6 casas e não as 4 do exemplo do professor.

    Empate entre contratos que o modelo ordenou de forma diferente é perda de
    AuROC de graça: o AuROC conta pares ordenados corretamente, e par empatado
    conta meio ponto. Com 2 casas, milhares de contratos colapsam no mesmo
    valor.

    O teste compara as três precisões em vez de fixar um limiar arbitrário —
    o que importa é a direção, não um número mágico.
    """
    distintos = {
        casas: formatar_submissao(submissao_valida, casas=casas)["pd"].nunique()
        for casas in (2, 4, 6)
    }
    assert distintos[2] < distintos[4] < distintos[6]
    assert distintos[2] < N * 0.1, "com 2 casas quase todo mundo empata"
    assert distintos[6] > N * 0.98, "com 6 casas o empate é residual"


def test_formatar_preserva_colunas_e_linhas(submissao_valida) -> None:
    saida = formatar_submissao(submissao_valida)
    assert len(saida) == N
    assert tuple(saida.columns) == COLUNAS_SUBMISSAO_MODELO


def test_resumo_da_distribuicao(submissao_valida) -> None:
    r = resumo_distribuicao(submissao_valida["pd"])
    assert r["n"] == N
    assert 0 < r["min"] <= r["mediana"] <= r["max"] < 1


# --- O arquivo de verdade ----------------------------------------------------
def test_arquivo_gerado_esta_conforme() -> None:
    """Valida o `submissao_modelo.csv` que será realmente enviado."""
    from banking.projeto import DIR_OUTPUTS

    caminho = DIR_OUTPUTS / "submissao" / "submissao_modelo.csv"
    if not caminho.exists():
        pytest.skip("rode python/modelagem/06_submissao_modelo.py primeiro")

    try:
        base_b = carregar_processada("B")
    except FileNotFoundError as erro:
        pytest.skip(str(erro))

    submissao = pd.read_csv(caminho)
    validar_submissao_modelo(submissao, base_b["id_contrato"])
    assert len(submissao) == 3_000


def test_escoragem_e_reprodutivel() -> None:
    """Duas execuções do modelo final produzem exatamente as mesmas PDs.

    Reprodutibilidade é item da rubrica, e aqui ela é verificada no artefato
    que vai ser entregue, não só no processo.
    """
    from banking.modelo import treinar_modelo_final

    try:
        base_a = carregar_processada("A")
        base_b = carregar_processada("B")
    except FileNotFoundError as erro:
        pytest.skip(str(erro))

    primeira = treinar_modelo_final(base_a).predict_proba(base_b)[:, 1]
    segunda = treinar_modelo_final(base_a).predict_proba(base_b)[:, 1]
    assert np.array_equal(primeira, segunda)
