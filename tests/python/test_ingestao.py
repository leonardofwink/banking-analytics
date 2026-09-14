"""S01.6 · Testes da ingestão — as garantias do contrato de dados.

Estes testes não verificam "se o código roda". Verificam as promessas que o
resto do projeto assume como verdadeiras: que nenhuma coluna proibida escapou,
que nenhuma linha se perdeu e que as datas não deslocaram.

A razão de existirem é que **nenhum desses erros levanta exceção sozinho**.
Uma coluna proibida que sobrevive produz um modelo aparentemente excelente;
uma data deslocada por fuso move o contrato de safra. Os dois passam
despercebidos até a apuração — onde já não dá para consertar.

Rodar::

    .\\scripts\\py.cmd -m pytest -q
"""

from __future__ import annotations

import pandas as pd
import pyarrow.parquet as pq
import pytest

from banking.dados import (
    ALVO,
    ARQUIVO_PROCESSADO,
    ARQUIVO_REALIZADOS,
    COLUNAS_PROIBIDAS,
    COLUNAS_REALIZADO,
    ESQUEMAS,
    carregar,
    carregar_bruto,
    carregar_realizados,
    validar,
)
from banking.projeto import DIR_PROCESSADOS

BASES = ("A", "B", "C")

# Contagens conferidas na inspeção de 2026-09-13, direto nos arquivos do professor.
LINHAS_ESPERADAS = {"A": 10_000, "B": 3_000, "C": 5_000}
COLUNAS_ESPERADAS = {"A": 23, "B": 22, "C": 20}
NULOS_ESPERADOS_A = {
    "renda_mensal_declarada": 770,
    "tempo_emprego_meses": 1_207,
    "score_bureau": 327,
}
INADIMPLENTES_A = 826


@pytest.fixture(scope="module")
def bases() -> dict[str, pd.DataFrame]:
    """Carrega as três bases uma vez só, para o módulo inteiro."""
    try:
        return {b: carregar(b) for b in BASES}
    except FileNotFoundError as erro:
        pytest.skip(f"Bases do professor ausentes: {erro}")


# --- A garantia que vale 30 pontos -------------------------------------------
def test_armadilha_qtd_parcelas_em_atraso_nunca_sobrevive(bases) -> None:
    """`qtd_parcelas_em_atraso_12m` não pode estar em nenhuma base carregada.

    ⚠️ NÃO REMOVA ESTE TESTE por achá-lo redundante com
    `test_nenhuma_coluna_proibida_sobrevive`. Ele é dedicado porque esta
    coluna específica é uma armadilha plantada: correlação 0,74 com o alvo na
    base A e **constante zero** nas bases B e C.

    Quem a usa treina um modelo em que ela domina, e ao escorar a base B o
    termo dominante vira constante — o modelo colapsa e o AuROC cai para ~0,5.
    Nenhum passo dá erro. Este teste é a única coisa entre esse cenário e nós.
    """
    for nome, df in bases.items():
        assert "qtd_parcelas_em_atraso_12m" not in df.columns, (
            f"A ARMADILHA ESCAPOU na base {nome}. "
            "Ver docs/DICIONARIO_DADOS.md § A armadilha."
        )


def test_nenhuma_coluna_proibida_sobrevive(bases) -> None:
    """Nenhuma coluna pós-concessão pode chegar às bases de modelagem."""
    for nome, df in bases.items():
        infiltradas = sorted(set(df.columns) & COLUNAS_PROIBIDAS)
        assert not infiltradas, f"base {nome} com colunas proibidas: {infiltradas}"


# --- Integridade das bases ---------------------------------------------------
def test_contagem_de_linhas_e_colunas(bases) -> None:
    """Nenhuma linha pode se perder: o professor cruza a submissão por id."""
    for nome, df in bases.items():
        assert len(df) == LINHAS_ESPERADAS[nome], f"base {nome}: {len(df)} linhas"
        assert df.shape[1] == COLUNAS_ESPERADAS[nome], f"base {nome}: {df.shape[1]} colunas"


def test_alvo_existe_apenas_na_base_a(bases) -> None:
    """O alvo é preservado em A (é o que se treina) e ausente em B e C.

    Se aparecesse em B, seria o gabarito da avaliação vazando — e a base B
    justamente não o tem, porque o professor o guardou.
    """
    assert ALVO in bases["A"].columns, "sem o alvo não há o que treinar"
    assert ALVO not in bases["B"].columns
    assert ALVO not in bases["C"].columns


def test_identificadores_unicos(bases) -> None:
    """Id duplicado quebraria o cruzamento da submissão com o gabarito."""
    for nome, df in bases.items():
        col = ESQUEMAS[nome].coluna_id
        assert df[col].is_unique, f"base {nome}: {col} tem duplicados"
        assert df[col].notna().all(), f"base {nome}: {col} tem nulos"


def test_nulos_sao_preservados(bases) -> None:
    """A ingestão NÃO imputa — e isso é deliberado.

    Imputação aprende com o dado (uma mediana, uma média). Se fosse feita
    aqui, aprenderia com as três bases juntas e a informação da validação
    vazaria para o treino. Ela pertence ao Pipeline, ajustada só no treino —
    exigência explícita do dicionário do professor e dos 10 pontos de
    qualidade técnica. Este teste trava a tentação.
    """
    nulos = bases["A"].isna().sum()
    for coluna, esperado in NULOS_ESPERADOS_A.items():
        assert int(nulos[coluna]) == esperado, (
            f"{coluna}: esperava {esperado} nulos, encontrou {nulos[coluna]}. "
            "A ingestão imputou alguma coisa? Não deveria."
        )


def test_periodos_das_bases_nao_se_sobrepoem(bases) -> None:
    """A ordem temporal é o que torna a validação out-of-time honesta.

    A é histórico (2022–2024), B é o semestre seguinte (jan–jun/2025) e C vem
    depois (jul–dez/2025). Sobreposição indicaria base trocada.
    """
    fim_a = pd.to_datetime(bases["A"]["data_originacao"]).max()
    inicio_b = pd.to_datetime(bases["B"]["data_originacao"]).min()
    fim_b = pd.to_datetime(bases["B"]["data_originacao"]).max()
    inicio_c = pd.to_datetime(bases["C"]["data_proposta"]).min()

    assert fim_a < inicio_b, "base A invade o período da B"
    assert fim_b < inicio_c, "base B invade o período da C"


# --- Realizados: o gabarito do S02 -------------------------------------------
def test_realizados_preservados_para_o_s02() -> None:
    """EAD e LGD realizados saem da modelagem mas não podem ser descartados.

    São o gabarito contra o qual o S02 confere a interpretação das tabelas de
    EAD e LGD do professor.
    """
    try:
        realizados = carregar_realizados()
    except FileNotFoundError as erro:
        pytest.skip(str(erro))

    assert len(realizados) == LINHAS_ESPERADAS["A"]
    for coluna in COLUNAS_REALIZADO:
        assert coluna in realizados.columns

    # Só quem deu default tem EAD e LGD: quem pagou não tem o que recuperar.
    assert int(realizados["ead_realizado"].notna().sum()) == INADIMPLENTES_A
    assert int(realizados["lgd_realizado"].notna().sum()) == INADIMPLENTES_A


# --- Validação de esquema ----------------------------------------------------
def test_validar_aceita_as_bases_como_estao(bases) -> None:
    """O esquema declarado tem que bater com a realidade de hoje."""
    for nome, df in bases.items():
        validar(df, nome)  # não levanta


@pytest.mark.parametrize(
    "adulteracao,trecho_esperado",
    [
        ("remover_linha", "linhas"),
        ("injetar_proibida", "proibidas"),
        ("duplicar_id", "duplicados"),
        ("ltv_percentual", "fora de [0, 1]"),
        ("prazo_invalido", "prazos fora"),
    ],
)
def test_validar_rejeita_base_adulterada(bases, adulteracao, trecho_esperado) -> None:
    """`validar` precisa falhar, e a mensagem precisa dizer o que houve.

    Um validador que aceita tudo é pior que nenhum: dá falsa segurança. Cada
    caso aqui simula um jeito real de a base chegar errada.
    """
    df = bases["A"].copy()

    if adulteracao == "remover_linha":
        df = df.iloc[:-1]
    elif adulteracao == "injetar_proibida":
        df["qtd_parcelas_em_atraso_12m"] = 0
    elif adulteracao == "duplicar_id":
        df.iloc[1, df.columns.get_loc("id_contrato")] = df.iloc[0]["id_contrato"]
    elif adulteracao == "ltv_percentual":
        df["ltv"] = df["ltv"] * 100  # o erro clássico: fração virou percentual
    elif adulteracao == "prazo_invalido":
        df.iloc[0, df.columns.get_loc("prazo_meses")] = 42

    with pytest.raises(ValueError, match=r".*"):
        validar(df, "A")

    try:
        validar(df, "A")
    except ValueError as erro:
        assert trecho_esperado in str(erro), f"mensagem pouco clara: {erro}"


# --- Parquet: a fronteira com o R --------------------------------------------
@pytest.fixture(scope="module")
def parquets_gerados() -> dict[str, object]:
    """Exige que o pipeline de ingestão já tenha rodado."""
    caminhos = {b: DIR_PROCESSADOS / ARQUIVO_PROCESSADO[b] for b in BASES}
    faltando = [str(c) for c in caminhos.values() if not c.exists()]
    if faltando:
        pytest.skip(
            "Parquets ausentes — rode: .\\scripts\\py.cmd python\\etl\\01_ingestao.py"
        )
    return caminhos


def test_parquet_preserva_linhas_e_colunas(parquets_gerados, bases) -> None:
    """Round-trip: o que foi gravado é o que volta."""
    for nome, caminho in parquets_gerados.items():
        lido = pd.read_parquet(caminho)
        assert len(lido) == len(bases[nome])
        assert list(lido.columns) == list(bases[nome].columns)


def test_data_gravada_como_date32(parquets_gerados) -> None:
    """A data tem que ser `date32`, não timestamp — senão desloca no R.

    Verificado neste repositório: `datetime64` do pandas é lido como UTC pelo
    `arrow` do lado R e convertido para o fuso local (−3h em São Paulo), de
    modo que 2022-01-01 chega como 2021-12-31. Isso moveria o contrato de
    safra, e safra é a unidade de análise do S03.
    """
    for nome, caminho in parquets_gerados.items():
        esquema = pq.read_schema(caminho)
        coluna = ESQUEMAS[nome].coluna_data
        tipo = esquema.field(coluna).type
        assert str(tipo) == "date32[day]", (
            f"base {nome}: {coluna} gravada como {tipo}, não date32. "
            "Timestamp desloca a data ao ser lido no R."
        )


def test_primeira_safra_da_base_a_nao_deslocou(parquets_gerados) -> None:
    """A menor data da base A tem que ser 2022-01-01, não 2021-12-31.

    É o teste concreto do deslocamento de fuso: se a data recuou um dia, ela
    recuou de ano — e de safra.
    """
    lido = pd.read_parquet(parquets_gerados["A"])
    assert str(pd.to_datetime(lido["data_originacao"]).min().date()) == "2022-01-01"


def test_realizados_gravados(parquets_gerados) -> None:
    """O gabarito do S02 também precisa estar em disco."""
    caminho = DIR_PROCESSADOS / ARQUIVO_REALIZADOS
    assert caminho.exists(), "realizados não foram gravados pela ingestão"
    assert len(pd.read_parquet(caminho)) == LINHAS_ESPERADAS["A"]


# --- O contrato em si --------------------------------------------------------
def test_carregar_bruto_traz_as_colunas_originais() -> None:
    """`carregar_bruto` é a leitura crua: nada é removido ali.

    A distinção importa. Se `carregar_bruto` também limpasse, não haveria como
    inspecionar o dado original nem extrair os realizados.
    """
    try:
        bruto = carregar_bruto("A")
    except FileNotFoundError as erro:
        pytest.skip(str(erro))
    assert "qtd_parcelas_em_atraso_12m" in bruto.columns
    assert bruto.shape[1] == 28


def test_base_desconhecida_falha_claro() -> None:
    """Erro de digitação na base tem que dizer quais existem."""
    with pytest.raises(KeyError, match="Base desconhecida"):
        carregar("Z")
