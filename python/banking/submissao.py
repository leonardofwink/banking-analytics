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
    "ValidacaoFalhou",
    "formatar_submissao",
    "resumo_distribuicao",
    "validar_submissao_modelo",
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
