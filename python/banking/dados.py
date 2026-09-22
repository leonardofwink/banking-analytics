"""Contrato de dados do desafio AutoCred — a porta de entrada única das bases.

**A partir daqui, ninguém no projeto lê CSV.** Todo consumidor chama
:func:`carregar` e recebe um DataFrame já limpo das colunas que não podem ser
usadas como preditoras. Quem contornar este módulo está errado por definição.

Por que isso é uma regra e não uma preferência: a base traz
``qtd_parcelas_em_atraso_12m``, que tem correlação 0,74 com o alvo na base A e
vale **zero** nas bases B e C. Um modelo que a use fica excelente na validação e
colapsa na avaliação — sem levantar exceção em passo nenhum. Se cada script
removesse a coluna por conta própria, bastaria uma pessoa esquecer, uma vez.
Ver ``docs/DICIONARIO_DADOS.md`` e ``docs/specs/S01_INGESTAO.md``.

⚠️ Este módulo é uma das duas exceções declaradas à regra de "biblioteca não faz
IO" (a outra é :mod:`banking.projeto`): centralizar a leitura aqui é justamente
o objetivo do passo S01. Ver ``AGENTS.md``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from banking.projeto import DIR_BRUTOS, DIR_PROCESSADOS

__all__ = [
    "ALVO",
    "ARQUIVO_PROCESSADO",
    "ARQUIVO_REALIZADOS",
    "COLUNAS_PROIBIDAS",
    "COLUNAS_REALIZADO",
    "ESQUEMAS",
    "PREDITORAS_CATEGORICAS",
    "PREDITORAS_NUMERICAS",
    "carregar",
    "carregar_bruto",
    "carregar_processada",
    "carregar_realizados",
    "gravar_parquet",
    "preparar_base_c",
    "validar",
]

# --- Onde os arquivos do professor moram ------------------------------------
DIR_PROFESSOR = DIR_BRUTOS / "professor" / "bases"

# --- O alvo ------------------------------------------------------------------
# Proibido como PREDITORA (seria prever a resposta com a resposta), obrigatório
# como ALVO. Por isso não entra em COLUNAS_PROIBIDAS: quem remove o alvo fica
# sem o que treinar.
ALVO = "default_90_12"

# --- Colunas que NÃO existem no momento da concessão -------------------------
# Todas marcadas "Disponível na concessão? = NÃO" no dicionário do professor.
# Nenhuma pode ser preditora.
COLUNAS_PROIBIDAS = frozenset(
    {
        # A armadilha: presente nas três bases, mas constante zero em B e C.
        "qtd_parcelas_em_atraso_12m",
        # Realizados — só existem para quem já deu default.
        "mes_default",
        "ead_realizado",
        "lgd_realizado",
        "perda_financeira",
    }
)

# --- Realizados: proibidos como preditora, preciosos como gabarito -----------
# NÃO são descartados. O passo S02 usa ead_realizado e lgd_realizado para
# conferir se interpretamos corretamente as tabelas de EAD e LGD do professor —
# é raro ter gabarito, e seria desperdício jogar fora. Saem da base de
# modelagem e vão para um arquivo separado (ver carregar_realizados).
COLUNAS_REALIZADO = ("mes_default", "ead_realizado", "lgd_realizado", "perda_financeira")

# --- Preditoras (bases A e B) ------------------------------------------------
# A tipagem e o encoding NÃO acontecem aqui: são transformações que aprendem
# com o dado e precisam ficar dentro do Pipeline, ajustadas só no treino.
# Estas listas existem para o S03/S04 saberem o que é o quê.
PREDITORAS_NUMERICAS = (
    "valor_financiado",
    "ltv",
    "prazo_meses",
    "comprometimento_renda",
    "idade_veiculo_anos",
    "idade_cliente",
    "renda_mensal_declarada",
    "tempo_emprego_meses",
    "score_bureau",
    "qtd_restricoes_ativas",
    "qtd_consultas_bureau_3m",
)

PREDITORAS_CATEGORICAS = (
    "canal_originacao",
    "ocupacao",
    "tipo_residencia",
    "possui_avalista",
)

# Colunas presentes mas não classificadas como preditoras pelo dicionário.
# Mantidas na base: valor_bem e valor_entrada são necessários para recalcular o
# LTV sob uma entrada exigida (S10), e taxa/parcela documentam a política antiga.
APOIO = ("valor_bem", "valor_entrada", "taxa_juros_am", "parcela_mensal", "ano_modelo")


@dataclass(frozen=True)
class Esquema:
    """Descreve o que se espera de uma das três bases.

    Serve de alarme: se o professor mandar uma base corrigida com outro número
    de linhas ou outro nome de coluna, :func:`validar` falha em vez de o
    pipeline seguir silenciosamente com dado diferente do que a spec previu.
    """

    arquivo: str
    n_linhas: int
    coluna_id: str
    coluna_data: str
    coluna_prazo: str
    coluna_ltv: str
    coluna_financiado: str
    tem_alvo: bool
    periodo: tuple[str, str]
    n_colunas_apos_limpeza: int
    obrigatorias: tuple[str, ...] = field(default_factory=tuple)

    @property
    def caminho(self) -> Path:
        return DIR_PROFESSOR / self.arquivo


# Contagens e períodos conferidos na inspeção de 2026-09-13.
ESQUEMAS: dict[str, Esquema] = {
    "A": Esquema(
        arquivo="base_A_autocred_base_desenvolvimento.csv",
        n_linhas=10_000,
        coluna_id="id_contrato",
        coluna_data="data_originacao",
        coluna_prazo="prazo_meses",
        coluna_ltv="ltv",
        coluna_financiado="valor_financiado",
        tem_alvo=True,
        periodo=("2022-01-01", "2024-12-01"),
        n_colunas_apos_limpeza=23,  # 28 originais - 5 proibidas (o alvo fica)
        obrigatorias=PREDITORAS_NUMERICAS + PREDITORAS_CATEGORICAS + (ALVO,),
    ),
    "B": Esquema(
        arquivo="base_B_autocred_base_teste_modelo.csv",
        n_linhas=3_000,
        coluna_id="id_contrato",
        coluna_data="data_originacao",
        coluna_prazo="prazo_meses",
        coluna_ltv="ltv",
        coluna_financiado="valor_financiado",
        tem_alvo=False,
        periodo=("2025-01-01", "2025-06-01"),
        n_colunas_apos_limpeza=22,  # 23 originais - 1 proibida presente
        obrigatorias=PREDITORAS_NUMERICAS + PREDITORAS_CATEGORICAS,
    ),
    "C": Esquema(
        arquivo="base_C_autocred_base_politica.csv",
        n_linhas=5_000,
        coluna_id="id_proposta",
        coluna_data="data_proposta",
        # A base C traz o que o cliente PEDIU, não o que foi contratado — as
        # condições contratadas são decisão da nossa política (ver S10).
        coluna_prazo="prazo_desejado_meses",
        coluna_ltv="ltv_desejado",
        coluna_financiado="valor_financiado_desejado",
        tem_alvo=False,
        periodo=("2025-07-01", "2025-12-01"),
        n_colunas_apos_limpeza=20,  # 21 originais - 1 proibida presente
        obrigatorias=PREDITORAS_CATEGORICAS
        + (
            "score_bureau",
            "qtd_restricoes_ativas",
            "qtd_consultas_bureau_3m",
            "idade_cliente",
            "idade_veiculo_anos",
            "renda_mensal_declarada",
            "tempo_emprego_meses",
        ),
    ),
}

# Nome do Parquet gerado para cada base, em dados/processados/. Público: o
# pipeline de ingestão (S01.7) e os passos seguintes resolvem os caminhos por aqui.
ARQUIVO_PROCESSADO = {"A": "base_A.parquet", "B": "base_B.parquet", "C": "base_C.parquet"}
ARQUIVO_REALIZADOS = "base_A_realizados.parquet"

# --- Parâmetros de EAD e LGD (S02) -------------------------------------------
ARQUIVO_PARAMETROS = "AutoCred_parametros_ead_lgd.xlsx"

# Rótulos das faixas de LTV, exatamente como no Excel do professor. A ordem é
# significativa: é a ordem das colunas nas duas tabelas.
FAIXAS_LTV = ("até 60%", "60% a 70%", "70% a 80%", "80% a 90%", "acima de 90%")

# Rótulos das faixas de idade do veículo, na ordem das linhas da tabela de LGD.
FAIXAS_IDADE_VEICULO = ("0 a 2 anos", "3 a 5 anos", "6 a 8 anos", "9 anos ou mais")


@dataclass(frozen=True)
class Parametros:
    """As três tabelas de parâmetros dadas pelo professor.

    :param fator_ead: linhas = prazo (24/36/48/60), colunas = faixa de LTV.
        Multiplicado pelo valor financiado, dá o EAD em reais.
    :param lgd: linhas = faixa de idade do veículo, colunas = faixa de LTV.
        Fração perdida sobre o EAD após o workout de 24 meses.
    :param dist_mes_default: frequência do mês em que o default ocorre (1 a 12).
        É o que permite calcular quantas parcelas um contrato que quebra chega
        a pagar — insumo do motor de ROI (S08).
    """

    fator_ead: pd.DataFrame
    lgd: pd.DataFrame
    dist_mes_default: pd.Series


def carregar_parametros_ead_lgd() -> Parametros:
    """Lê `AutoCred_parametros_ead_lgd.xlsx` e devolve as três tabelas.

    As tabelas são **médias por célula** dos contratos inadimplentes da base A
    — não valores por contrato. Ver ``docs/specs/S02_PERDA_ESPERADA.md``.

    :raises FileNotFoundError: se o arquivo do professor não estiver em
        ``dados/brutos/professor/bases/``.
    """
    caminho = DIR_PROFESSOR / ARQUIVO_PARAMETROS
    if not caminho.exists():
        raise FileNotFoundError(
            f"Parâmetros de EAD/LGD não encontrados em {caminho}.\n"
            "Copie 'AutoCred_Arquivos do Desafio/bases' para dados/brutos/professor/."
        )

    excel = pd.ExcelFile(caminho)

    fator = excel.parse("Fator_EAD").set_index(excel.parse("Fator_EAD").columns[0])
    fator.columns = list(FAIXAS_LTV)
    fator.index.name = "prazo_meses"

    lgd = excel.parse("LGD").set_index(excel.parse("LGD").columns[0])
    lgd.columns = list(FAIXAS_LTV)
    lgd.index = list(FAIXAS_IDADE_VEICULO)
    lgd.index.name = "faixa_idade_veiculo"

    dist = excel.parse("Distribuicao_Mes_Default")
    dist = pd.Series(dist.iloc[:, 1].to_numpy(), index=dist.iloc[:, 0].to_numpy(), name="frequencia")
    dist.index.name = "mes_default"

    return Parametros(fator_ead=fator, lgd=lgd, dist_mes_default=dist)


def _esquema(base: str) -> Esquema:
    """Resolve o esquema da base, aceitando 'a' ou 'A'."""
    chave = base.strip().upper()
    if chave not in ESQUEMAS:
        raise KeyError(f"Base desconhecida: {base!r}. Use uma de {sorted(ESQUEMAS)}.")
    return ESQUEMAS[chave]


# --- S01.2 · Carga e tipagem -------------------------------------------------
def carregar_bruto(base: str) -> pd.DataFrame:
    """Lê o CSV da base **como veio**, apenas convertendo a coluna de data.

    Nenhuma coluna é removida aqui — é a leitura crua. Use :func:`carregar`
    para obter a base já sem as colunas proibidas.

    A conversão da data não é cosmética: ``read_csv`` traz data como texto, e
    texto ordena errado ("2024-1-5" vem depois de "2024-12-31" em ordem
    alfabética), o que quebraria o split temporal do S03.

    :param base: ``"A"``, ``"B"`` ou ``"C"``.
    :return: DataFrame com todas as colunas originais.
    :raises FileNotFoundError: se o arquivo do professor não estiver em
        ``dados/brutos/professor/bases/``.
    """
    esq = _esquema(base)
    if not esq.caminho.exists():
        raise FileNotFoundError(
            f"Base {base.upper()} não encontrada em {esq.caminho}.\n"
            "Os arquivos do professor ficam fora do git (ver .gitignore): copie a pasta "
            "'AutoCred_Arquivos do Desafio/bases' para dados/brutos/professor/."
        )
    return pd.read_csv(esq.caminho, parse_dates=[esq.coluna_data])


# --- S01.3 · Separação: preditoras, alvo e realizados ------------------------
def carregar(base: str) -> pd.DataFrame:
    """Carrega a base **sem as colunas proibidas** — a porta de entrada oficial.

    O alvo (``default_90_12``) é preservado na base A: ele é proibido como
    preditora, mas é o que se treina. Separe-o com ``df.pop(ALVO)`` na hora de
    montar X e y.

    :param base: ``"A"``, ``"B"`` ou ``"C"``.
    :return: DataFrame limpo, com os nulos **intactos** (a imputação pertence
        ao Pipeline, ajustada só no treino — ver S01 § "o que não fazemos").
    """
    df = carregar_bruto(base)
    return df.drop(columns=[c for c in df.columns if c in COLUNAS_PROIBIDAS])


def carregar_realizados() -> pd.DataFrame:
    """Devolve os valores realizados da base A, que são o gabarito do S02.

    ``ead_realizado`` e ``lgd_realizado`` não podem ser preditoras — só existem
    depois do default. Mas permitem conferir se as tabelas de EAD e LGD do
    professor foram interpretadas corretamente, o que é um luxo raro. Por isso
    saem da base de modelagem para cá, em vez de serem descartados.

    :return: DataFrame com ``id_contrato`` + as quatro colunas de realizado.
        Nulo em tudo para os contratos adimplentes (só 826 dos 10.000 deram
        default), o que é esperado: quem não quebrou não tem EAD nem LGD.
    """
    df = carregar_bruto("A")
    return df[["id_contrato", *COLUNAS_REALIZADO]].copy()


# --- S01.4 · Validação de esquema -------------------------------------------
def validar(df: pd.DataFrame, base: str) -> None:
    """Confere que o DataFrame bate com o esquema esperado da base.

    Chamada sobre o resultado de :func:`carregar`. Não devolve nada: **levanta
    exceção** com a divergência descrita, para o pipeline parar em vez de
    seguir com dado diferente do que a spec previu.

    :param df: DataFrame já limpo (saída de :func:`carregar`).
    :param base: ``"A"``, ``"B"`` ou ``"C"``.
    :raises ValueError: com a lista de todos os problemas encontrados.
    """
    esq = _esquema(base)
    problemas: list[str] = []

    # 1. Contagem de linhas — alarme se o professor trocar a base.
    if len(df) != esq.n_linhas:
        problemas.append(f"esperava {esq.n_linhas:,} linhas, encontrou {len(df):,}")

    # 2. A regra que salva 30 pontos.
    infiltradas = sorted(set(df.columns) & COLUNAS_PROIBIDAS)
    if infiltradas:
        problemas.append(f"colunas proibidas presentes: {infiltradas}")

    # 3. Colunas obrigatórias.
    faltando = sorted(set(esq.obrigatorias) - set(df.columns))
    if faltando:
        problemas.append(f"colunas obrigatórias ausentes: {faltando}")

    # 4. O alvo existe onde deve, e só onde deve.
    tem_alvo = ALVO in df.columns
    if esq.tem_alvo and not tem_alvo:
        problemas.append(f"a base {base.upper()} deveria ter o alvo {ALVO!r}")
    if not esq.tem_alvo and tem_alvo:
        problemas.append(f"a base {base.upper()} NÃO deveria ter o alvo {ALVO!r}")

    # 5. Identificador único — o professor cruza a submissão por ele.
    if esq.coluna_id in df.columns:
        duplicados = int(df[esq.coluna_id].duplicated().sum())
        if duplicados:
            problemas.append(f"{duplicados} valores duplicados em {esq.coluna_id!r}")
        if df[esq.coluna_id].isna().any():
            problemas.append(f"{esq.coluna_id!r} tem valores nulos")
    else:
        problemas.append(f"identificador ausente: {esq.coluna_id!r}")

    # 6. Domínios — valores fora da faixa denunciam erro de leitura ou de base.
    if esq.coluna_prazo in df.columns:
        fora = sorted(set(df[esq.coluna_prazo].dropna().unique()) - {24, 36, 48, 60})
        if fora:
            problemas.append(f"{esq.coluna_prazo!r} com prazos fora de 24/36/48/60: {fora}")

    if esq.coluna_ltv in df.columns:
        ltv = df[esq.coluna_ltv]
        if ltv.notna().any() and not ltv.dropna().between(0, 1).all():
            problemas.append(
                f"{esq.coluna_ltv!r} fora de [0, 1] — "
                f"min={ltv.min():.3f}, max={ltv.max():.3f}. LTV é fração, não percentual"
            )

    if esq.coluna_financiado in df.columns:
        nao_positivos = int((df[esq.coluna_financiado] <= 0).sum())
        if nao_positivos:
            problemas.append(f"{nao_positivos} contratos com {esq.coluna_financiado!r} <= 0")

    if esq.tem_alvo and tem_alvo:
        valores = sorted(df[ALVO].dropna().unique())
        if not set(valores) <= {0, 1}:
            problemas.append(f"{ALVO!r} deveria ser binário, encontrou {valores}")

    # 7. Período — confirma que é a base certa (A é histórico, B e C são 2025).
    if esq.coluna_data in df.columns:
        datas = pd.to_datetime(df[esq.coluna_data])
        inicio, fim = pd.Timestamp(esq.periodo[0]), pd.Timestamp(esq.periodo[1])
        if datas.min() != inicio or datas.max() != fim:
            problemas.append(
                f"período esperado {inicio.date()}..{fim.date()}, "
                f"encontrou {datas.min().date()}..{datas.max().date()}"
            )

    if problemas:
        raise ValueError(
            f"Base {base.upper()} não bate com o esquema esperado:\n  - "
            + "\n  - ".join(problemas)
        )


# --- S01.5 · Gravação em Parquet --------------------------------------------
def gravar_parquet(df: pd.DataFrame, caminho: Path, coluna_data: str | None = None) -> Path:
    """Grava o DataFrame em Parquet, com a coluna de data como ``date32``.

    O ``date32`` não é preciosismo de tipo. Verificado neste repositório: o
    pandas grava ``datetime64`` sem fuso, o ``arrow`` do lado R lê como UTC e
    converte para o horário local (−3h em São Paulo), de modo que
    ``2022-01-01`` chega como ``2021-12-31``. Isso **moveria o contrato de
    safra** — e safra é a unidade de análise do S03. Ver AGENTS.md.

    :param df: DataFrame a gravar.
    :param caminho: destino ``.parquet``.
    :param coluna_data: coluna a converter para ``date32``, se houver.
    :return: o próprio ``caminho``, para encadear.
    """
    tabela = pa.Table.from_pandas(df, preserve_index=False)

    if coluna_data and coluna_data in df.columns:
        indice = tabela.schema.get_field_index(coluna_data)
        campo = tabela.schema.field(indice).with_type(pa.date32())
        tabela = tabela.cast(tabela.schema.set(indice, campo))

    caminho.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(tabela, caminho)
    return caminho


def preparar_base_c(base_c: pd.DataFrame) -> pd.DataFrame:
    """Acrescenta à base C os nomes de coluna que o modelo espera.

    A base C traz o que o cliente **pediu** (``ltv_desejado``,
    ``prazo_desejado_meses``, ``valor_financiado_desejado``), porque o
    contratado é decisão da política. O modelo foi treinado em A e B, onde as
    mesmas grandezas se chamam ``ltv``, ``prazo_meses`` e ``valor_financiado``.

    ⚠️ **Copia, não renomeia.** As colunas «desejadas» precisam sobreviver: o
    motor de ROI usa ``prazo_desejado_meses`` para medir o encurtamento que a
    política impõe, e ``pct_entrada_desejada`` para medir a entrada extra.
    Renomear destruiria os dois — e foi exatamente o bug que este comentário
    existe para não deixar voltar.

    :param base_c: base C, de ``carregar_processada("C")``.
    :return: cópia com as colunas acrescentadas.
    """
    preparada = base_c.copy()
    for destino, origem in (
        ("ltv", "ltv_desejado"),
        ("prazo_meses", "prazo_desejado_meses"),
        ("valor_financiado", "valor_financiado_desejado"),
    ):
        if origem not in preparada.columns:
            raise ValueError(f"base C sem a coluna {origem!r}")
        preparada[destino] = preparada[origem]
    return preparada


def carregar_processada(base: str) -> pd.DataFrame:
    """Lê o Parquet já gerado pelo pipeline de ingestão (S01.7).

    É por aqui que os passos seguintes (S03 em diante) leem os dados: mais
    rápido que reprocessar o CSV e com os tipos garantidos.

    :param base: ``"A"``, ``"B"`` ou ``"C"``.
    :raises FileNotFoundError: se a ingestão ainda não tiver rodado.
    """
    caminho = DIR_PROCESSADOS / ARQUIVO_PROCESSADO[base.strip().upper()]
    if not caminho.exists():
        raise FileNotFoundError(
            f"{caminho} não existe. Rode a ingestão primeiro:\n"
            "  .\\scripts\\py.cmd python\\etl\\01_ingestao.py"
        )
    return pd.read_parquet(caminho)
