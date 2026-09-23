"""S06.4 · Validação dos arquivos de submissão.

Erro de formato custa a nota inteira do bloco e é o tipo de erro que só aparece
quando já não dá para corrigir — o professor roda o parser dele depois do
prazo. Por isso **nenhum arquivo é enviado sem passar por aqui**.

O validador não conserta nada: ele **recusa** e diz o que está errado. Arquivo
consertado em silêncio esconde o problema de origem.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = [
    "COLUNAS_SUBMISSAO_MODELO",
    "COLUNAS_SUBMISSAO_POLITICA",
    "ValidacaoFalhou",
    "formatar_submissao",
    "resumo_distribuicao",
    "validar_submissao_modelo",
    "validar_submissao_politica",
]

# Nomes e ordem exatos do `submissao_modelo_EXEMPLO.csv` do professor.
COLUNAS_SUBMISSAO_MODELO = ("id_contrato", "pd")


class ValidacaoFalhou(Exception):
    """O arquivo de submissão não está conforme. Traz todos os problemas."""


def _conferir(problemas: list[str], arquivo: str) -> None:
    if problemas:
        raise ValidacaoFalhou(
            f"{arquivo} não está conforme:\n  - " + "\n  - ".join(problemas)
        )


def validar_submissao_modelo(
    submissao: pd.DataFrame,
    ids_esperados,
    arquivo: str = "submissao_modelo.csv",
) -> None:
    """Confere o arquivo do entregável 1 contra as regras do professor.

    :param submissao: DataFrame com ``id_contrato`` e ``pd``.
    :param ids_esperados: os ids da base B, na íntegra.
    :raises ValidacaoFalhou: com a lista de todos os problemas encontrados.
    """
    problemas: list[str] = []
    esperados = pd.Index(ids_esperados)

    # 1. Colunas: o parser do professor espera este cabeçalho.
    if tuple(submissao.columns) != COLUNAS_SUBMISSAO_MODELO:
        problemas.append(
            f"colunas {tuple(submissao.columns)}, esperado {COLUNAS_SUBMISSAO_MODELO}"
        )
        _conferir(problemas, arquivo)  # sem as colunas certas, o resto não faz sentido

    # 2. Contagem.
    if len(submissao) != len(esperados):
        problemas.append(f"{len(submissao)} linhas, esperado {len(esperados)}")

    # 3. Ids — é por eles que o professor cruza com o gabarito.
    faltando = esperados.difference(submissao["id_contrato"])
    sobrando = pd.Index(submissao["id_contrato"]).difference(esperados)
    if len(faltando):
        problemas.append(f"{len(faltando)} ids faltando (ex.: {list(faltando[:3])})")
    if len(sobrando):
        problemas.append(f"{len(sobrando)} ids que não existem na base (ex.: {list(sobrando[:3])})")
    if submissao["id_contrato"].duplicated().any():
        n = int(submissao["id_contrato"].duplicated().sum())
        problemas.append(f"{n} ids duplicados — id repetido quebra o cruzamento")

    # 4. A PD é probabilidade, em fração.
    pd_valores = submissao["pd"]
    if pd_valores.isna().any():
        problemas.append(f"{int(pd_valores.isna().sum())} PDs nulas")
    else:
        if not pd_valores.between(0.0, 1.0).all():
            problemas.append(
                f"PD fora de [0, 1] — min {pd_valores.min():.4f}, max {pd_valores.max():.4f}. "
                "A PD é fração, não percentual"
            )
        # 5. Distribuição degenerada: foi exatamente o sintoma da armadilha do
        # S01 — o modelo colapsa e todo mundo recebe praticamente a mesma PD.
        if pd_valores.nunique() < 10:
            problemas.append(
                f"apenas {pd_valores.nunique()} valores distintos de PD — "
                "modelo colapsado? (sintoma da armadilha do S01)"
            )
        if pd_valores.std() < 1e-4:
            problemas.append(f"PD praticamente constante (desvio {pd_valores.std():.2e})")

    _conferir(problemas, arquivo)


def formatar_submissao(submissao: pd.DataFrame, casas: int = 6) -> pd.DataFrame:
    """Devolve o DataFrame pronto para virar CSV, com a PD arredondada.

    Não grava nada: escrever arquivo é papel do pipeline, não da biblioteca.

    :param casas: casas decimais da PD. O exemplo do professor usa 4; usamos 6
        de propósito. Arredondar demais **cria empate entre contratos que o
        modelo ordenou de forma diferente**, e empate derruba o AuROC de graça.
    """
    saida = submissao.copy()
    if "pd" in saida.columns:
        saida["pd"] = saida["pd"].round(casas)
    return saida


def resumo_distribuicao(valores) -> dict[str, float]:
    """Estatísticas da PD, para inspeção antes do envio."""
    v = np.asarray(valores, dtype=float)
    return {
        "n": len(v),
        "media": float(v.mean()),
        "mediana": float(np.median(v)),
        "min": float(v.min()),
        "p05": float(np.percentile(v, 5)),
        "p95": float(np.percentile(v, 95)),
        "max": float(v.max()),
        "distintos": int(len(np.unique(v))),
    }


# --- S10 · O arquivo da política ---------------------------------------------
# Nomes e ordem exatos do `submissao_politica_EXEMPLO.csv` do professor.
COLUNAS_SUBMISSAO_POLITICA = (
    "id_proposta",
    "pd",
    "score_1a10",
    "decisao",
    "taxa_am",
    "prazo_meses",
    "pct_entrada_minima",
)

DECISOES_VALIDAS = frozenset({"APROVAR", "NEGAR"})

# Colunas que precisam estar vazias em toda linha negada, e preenchidas em toda
# linha aprovada. O exemplo do professor mostra o NEGAR com os três em branco.
COLUNAS_CONDICAO = ("taxa_am", "prazo_meses", "pct_entrada_minima")


def validar_submissao_politica(
    submissao: pd.DataFrame,
    ids_esperados,
    politica: pd.DataFrame,
    taxa_maxima: float = 0.035,
    aprovacao_minima: float = 0.35,
    arquivo: str = "submissao_politica.csv",
) -> None:
    """Confere o arquivo do entregável 2 contra as regras e contra a política.

    A verificação que dá nome ao passo é a **coerência**: o ``score_1a10`` tem
    de ser exatamente o que a ``pd`` da mesma linha produz, e as condições de
    cada linha têm de ser exatamente as da faixa correspondente na tabela.
    Divergência aqui é o que a rubrica chama de incoerência entre a tabela e o
    submetido — 10 pontos.

    :param submissao: DataFrame com as sete colunas.
    :param ids_esperados: os ``id_proposta`` da base C, na íntegra.
    :param politica: a tabela do S09, indexada por ``score``.
    :raises ValidacaoFalhou: com a lista de todos os problemas encontrados.
    """
    from banking.score import SCORE_MAXIMO, SCORE_MINIMO, score_de_pd

    problemas: list[str] = []
    esperados = pd.Index(ids_esperados)

    # 1. Cabeçalho — sem ele, o resto não faz sentido.
    if tuple(submissao.columns) != COLUNAS_SUBMISSAO_POLITICA:
        problemas.append(
            f"colunas {tuple(submissao.columns)}, esperado {COLUNAS_SUBMISSAO_POLITICA}"
        )
        _conferir(problemas, arquivo)

    # 2. Linhas e ids.
    if len(submissao) != len(esperados):
        problemas.append(f"{len(submissao)} linhas, esperado {len(esperados)}")

    faltando = esperados.difference(submissao["id_proposta"])
    sobrando = pd.Index(submissao["id_proposta"]).difference(esperados)
    if len(faltando):
        problemas.append(f"{len(faltando)} ids faltando (ex.: {list(faltando[:3])})")
    if len(sobrando):
        problemas.append(f"{len(sobrando)} ids inexistentes (ex.: {list(sobrando[:3])})")
    if submissao["id_proposta"].duplicated().any():
        problemas.append(f"{int(submissao['id_proposta'].duplicated().sum())} ids duplicados")

    # 3. A PD.
    pd_valores = submissao["pd"]
    if pd_valores.isna().any():
        problemas.append(f"{int(pd_valores.isna().sum())} PDs nulas")
    elif not pd_valores.between(0.0, 1.0).all():
        problemas.append(
            f"PD fora de [0, 1] — min {pd_valores.min():.4f}, max {pd_valores.max():.4f}"
        )

    # 4. A coerência que vale 10 pontos: o score tem de vir da PD reportada.
    scores = submissao["score_1a10"]
    if scores.isna().any():
        problemas.append(f"{int(scores.isna().sum())} scores nulos")
    else:
        fora = ~scores.between(SCORE_MINIMO, SCORE_MAXIMO)
        if fora.any():
            problemas.append(f"{int(fora.sum())} scores fora de [1, 10]")
        elif not pd_valores.isna().any():
            divergentes = int((scores.to_numpy() != score_de_pd(pd_valores)).sum())
            if divergentes:
                problemas.append(
                    f"{divergentes} linhas com score_1a10 incoerente com a pd reportada — "
                    "é a checagem de coerência da rubrica"
                )

    # 5. A decisão.
    decisoes = submissao["decisao"].astype(str)
    invalidas = sorted(set(decisoes) - DECISOES_VALIDAS)
    if invalidas:
        problemas.append(f"decisões inválidas: {invalidas} (esperado APROVAR/NEGAR maiúsculos)")

    aprovadas = decisoes == "APROVAR"
    negadas = decisoes == "NEGAR"

    # 6. Negada tem de vir vazia; aprovada, preenchida.
    for coluna in COLUNAS_CONDICAO:
        preenchida_em_negada = int(submissao.loc[negadas, coluna].notna().sum())
        if preenchida_em_negada:
            problemas.append(f"{preenchida_em_negada} linhas NEGAR com {coluna!r} preenchido")

        vazia_em_aprovada = int(submissao.loc[aprovadas, coluna].isna().sum())
        if vazia_em_aprovada:
            problemas.append(f"{vazia_em_aprovada} linhas APROVAR sem {coluna!r}")

    # 7. Guard-rails observáveis no próprio arquivo.
    taxas = submissao.loc[aprovadas, "taxa_am"]
    if taxas.notna().any() and taxas.max() > taxa_maxima + 1e-9:
        problemas.append(f"taxa {taxas.max():.4f} acima do teto de {taxa_maxima:.1%} a.m.")

    taxa_aprovacao = float(aprovadas.mean()) if len(submissao) else 0.0
    if taxa_aprovacao < aprovacao_minima:
        problemas.append(
            f"aprovação {taxa_aprovacao:.1%} abaixo do mínimo de {aprovacao_minima:.0%}"
        )

    # 8. Coerência com a tabela: mesma faixa, mesmas condições.
    regras = politica.set_index("score") if "score" in politica.columns else politica
    for score, grupo in submissao[aprovadas].groupby("score_1a10"):
        if score not in regras.index:
            problemas.append(f"score {score} aprovado, mas ausente da tabela de política")
            continue
        for coluna in COLUNAS_CONDICAO:
            esperado = regras.loc[score, coluna]
            diferentes = int((~np.isclose(grupo[coluna].to_numpy(dtype=float), float(esperado))).sum())
            if diferentes:
                problemas.append(
                    f"faixa {score}: {diferentes} linhas com {coluna!r} diferente da tabela "
                    f"(esperado {esperado})"
                )

    _conferir(problemas, arquivo)
