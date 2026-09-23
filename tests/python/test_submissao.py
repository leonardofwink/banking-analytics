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


# =============================================================================
# S10 · O arquivo da política
# =============================================================================
from banking.politica import POLITICA_ESCOLHIDA, gerar_politica  # noqa: E402
from banking.submissao import (  # noqa: E402
    COLUNAS_SUBMISSAO_POLITICA,
    validar_submissao_politica,
)
from banking.score import score_de_pd  # noqa: E402

N_C = 5_000
PERDA = {10: 0.0134, 9: 0.0207, 8: 0.0292, 7: 0.0407, 6: 0.0577,
         5: 0.0792, 4: 0.1118, 3: 0.1561, 2: 0.2128, 1: 0.3331}


@pytest.fixture(scope="module")
def politica_teste() -> pd.DataFrame:
    return gerar_politica(**POLITICA_ESCOLHIDA, perda_por_faixa=PERDA)


@pytest.fixture
def ids_c() -> pd.Series:
    return pd.Series([f"P{i:06d}" for i in range(1, N_C + 1)])


@pytest.fixture
def politica_valida(ids_c, politica_teste) -> pd.DataFrame:
    """Submissão coerente: o score vem da PD, as condições vêm da tabela."""
    rng = np.random.default_rng(7)
    pds = rng.beta(1.6, 9.0, N_C)  # espalha por todas as faixas
    scores = score_de_pd(pds)
    regras = politica_teste.set_index("score")
    return pd.DataFrame(
        {
            "id_proposta": ids_c,
            "pd": pds.round(6),
            "score_1a10": scores,
            "decisao": pd.Series(scores).map(regras["decisao"]).to_numpy(),
            "taxa_am": pd.Series(scores).map(regras["taxa_am"]).to_numpy(),
            "prazo_meses": pd.Series(scores).map(regras["prazo_meses"]).to_numpy(),
            "pct_entrada_minima": pd.Series(scores).map(regras["pct_entrada_minima"]).to_numpy(),
        },
        columns=list(COLUNAS_SUBMISSAO_POLITICA),
    )


def test_submissao_de_politica_valida_passa(politica_valida, ids_c, politica_teste) -> None:
    validar_submissao_politica(politica_valida, ids_c, politica_teste)


def test_score_incoerente_com_a_pd_e_recusado(politica_valida, ids_c, politica_teste) -> None:
    """A verificação que vale 10 pontos da rubrica.

    Se o score não vier da PD reportada, a tabela e o submetido contam
    histórias diferentes — e é exatamente isso que o professor confere.
    """
    adulterada = politica_valida.copy()
    adulterada.loc[0, "score_1a10"] = 1 if adulterada.loc[0, "score_1a10"] != 1 else 2
    with pytest.raises(ValidacaoFalhou, match="incoerente"):
        validar_submissao_politica(adulterada, ids_c, politica_teste)


def test_condicao_diferente_da_tabela_e_recusada(politica_valida, ids_c, politica_teste) -> None:
    """Duas linhas da mesma faixa com taxas diferentes: qual é a política?"""
    adulterada = politica_valida.copy()
    aprovada = adulterada.index[adulterada["decisao"] == "APROVAR"][0]
    adulterada.loc[aprovada, "taxa_am"] = 0.0199
    with pytest.raises(ValidacaoFalhou, match="diferente da tabela"):
        validar_submissao_politica(adulterada, ids_c, politica_teste)


def test_negar_com_campo_preenchido_e_recusado(politica_valida, ids_c, politica_teste) -> None:
    """O exemplo do professor mostra NEGAR com taxa, prazo e entrada em branco."""
    adulterada = politica_valida.copy()
    negada = adulterada.index[adulterada["decisao"] == "NEGAR"][0]
    adulterada.loc[negada, "taxa_am"] = 0.02
    with pytest.raises(ValidacaoFalhou, match="NEGAR com"):
        validar_submissao_politica(adulterada, ids_c, politica_teste)


def test_aprovar_sem_condicao_e_recusado(politica_valida, ids_c, politica_teste) -> None:
    """Linha aprovada sem taxa é proposta sem oferta."""
    adulterada = politica_valida.copy()
    aprovada = adulterada.index[adulterada["decisao"] == "APROVAR"][0]
    adulterada.loc[aprovada, "prazo_meses"] = np.nan
    with pytest.raises(ValidacaoFalhou, match="APROVAR sem"):
        validar_submissao_politica(adulterada, ids_c, politica_teste)


def test_decisao_em_minusculas_e_recusada(politica_valida, ids_c, politica_teste) -> None:
    adulterada = politica_valida.copy()
    adulterada.loc[0, "decisao"] = "aprovar"
    with pytest.raises(ValidacaoFalhou, match="decisões inválidas"):
        validar_submissao_politica(adulterada, ids_c, politica_teste)


def test_taxa_acima_do_teto_e_recusada(politica_valida, ids_c, politica_teste) -> None:
    adulterada = politica_valida.copy()
    aprovada = adulterada.index[adulterada["decisao"] == "APROVAR"][0]
    adulterada.loc[aprovada, "taxa_am"] = 0.05
    with pytest.raises(ValidacaoFalhou, match="acima do teto"):
        validar_submissao_politica(adulterada, ids_c, politica_teste)


def test_aprovacao_abaixo_do_minimo_e_recusada(ids_c, politica_teste) -> None:
    """Aprovar menos de 35% corta a nota de política pela metade."""
    pds = np.full(N_C, 0.30)  # todos no score 2 → todos negados
    scores = score_de_pd(pds)
    submissao = pd.DataFrame(
        {
            "id_proposta": ids_c, "pd": pds, "score_1a10": scores,
            "decisao": "NEGAR", "taxa_am": np.nan,
            "prazo_meses": np.nan, "pct_entrada_minima": np.nan,
        },
        columns=list(COLUNAS_SUBMISSAO_POLITICA),
    )
    with pytest.raises(ValidacaoFalhou, match="aprovação"):
        validar_submissao_politica(submissao, ids_c, politica_teste)


def test_id_faltando_e_recusado(politica_valida, ids_c, politica_teste) -> None:
    with pytest.raises(ValidacaoFalhou, match="linhas|faltando"):
        validar_submissao_politica(politica_valida.iloc[:-1], ids_c, politica_teste)


def test_colunas_fora_de_ordem_sao_recusadas(politica_valida, ids_c, politica_teste) -> None:
    trocada = politica_valida[list(reversed(COLUNAS_SUBMISSAO_POLITICA))]
    with pytest.raises(ValidacaoFalhou, match="colunas"):
        validar_submissao_politica(trocada, ids_c, politica_teste)


# --- O arquivo de verdade ----------------------------------------------------
def test_arquivo_de_politica_gerado_esta_conforme() -> None:
    """Valida o `submissao_politica.csv` que será realmente enviado.

    A política de referência é **reconstruída do zero** a partir da base C —
    o mesmo caminho do pipeline. Usar uma tabela com valores arredondados à
    mão faria o teste falhar por diferença de casa decimal, que foi
    exatamente o que aconteceu na primeira versão deste teste.

    Reconstruir também verifica que a geração é determinística: se a política
    mudasse entre execuções, o arquivo deixaria de bater com ela.
    """
    from banking.dados import preparar_base_c
    from banking.modelo import treinar_modelo_final
    from banking.perda import fator_ead, lgd
    from banking.projeto import DIR_OUTPUTS

    caminho = DIR_OUTPUTS / "submissao" / "submissao_politica.csv"
    if not caminho.exists():
        pytest.skip("rode python/modelagem/10_submissao_politica.py primeiro")

    try:
        base_a = carregar_processada("A")
        base_c = carregar_processada("C")
    except FileNotFoundError as erro:
        pytest.skip(str(erro))

    modelo = treinar_modelo_final(base_a)
    propostas = preparar_base_c(base_c)
    propostas["pd"] = modelo.predict_proba(propostas)[:, 1]
    el = (
        propostas["pd"]
        * fator_ead(propostas["prazo_meses"], propostas["ltv"])
        * lgd(propostas["idade_veiculo_anos"], propostas["ltv"], propostas["possui_avalista"])
    )
    perda = (
        pd.DataFrame({"score": score_de_pd(propostas["pd"]), "el": el})
        .groupby("score")["el"].mean().to_dict()
    )
    politica = gerar_politica(**POLITICA_ESCOLHIDA, perda_por_faixa=perda)

    submissao = pd.read_csv(caminho)
    validar_submissao_politica(submissao, base_c["id_proposta"], politica)
    assert len(submissao) == N_C


def test_arquivo_de_politica_tem_negados_com_campos_vazios() -> None:
    """Confere no CSV cru, não no DataFrame: é o arquivo que o professor lê."""
    from banking.projeto import DIR_OUTPUTS

    caminho = DIR_OUTPUTS / "submissao" / "submissao_politica.csv"
    if not caminho.exists():
        pytest.skip("rode python/modelagem/10_submissao_politica.py primeiro")

    linhas = caminho.read_text(encoding="utf-8").splitlines()
    negadas = [linha for linha in linhas[1:] if ",NEGAR," in linha]
    assert negadas, "nenhuma linha negada no arquivo"
    for linha in negadas[:50]:
        assert linha.endswith(",NEGAR,,,"), f"linha negada com campo preenchido: {linha}"
