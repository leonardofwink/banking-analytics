"""S01.7 · Pipeline de ingestão — CSV do professor -> Parquet validado.

Lê as três bases, remove as colunas que não existem no momento da concessão,
valida o esquema e grava em ``dados/processados/``. Preserva à parte os valores
realizados de EAD e LGD da base A, que são o gabarito do S02.

Rodar::

    .\\scripts\\py.cmd python\\etl\\01_ingestao.py

É idempotente: rodar duas vezes produz exatamente os mesmos arquivos.

Spec: ``docs/specs/S01_INGESTAO.md``.
"""

from __future__ import annotations

import sys

from banking.dados import (
    ARQUIVO_PROCESSADO,
    ARQUIVO_REALIZADOS,
    ESQUEMAS,
    carregar,
    carregar_realizados,
    gravar_parquet,
    validar,
)
from banking.projeto import DIR_PROCESSADOS, log_step


def main() -> int:
    """Executa a ingestão das três bases. Devolve 0 em sucesso, 1 em falha."""
    log_step("S01 · Ingestão das bases AutoCred")

    for base, esquema in ESQUEMAS.items():
        try:
            df = carregar(base)
        except FileNotFoundError as erro:
            log_step(str(erro), "erro")
            return 1

        # Validar ANTES de gravar: arquivo gravado a partir de base divergente
        # é pior que arquivo nenhum, porque parece bom.
        try:
            validar(df, base)
        except ValueError as erro:
            log_step(str(erro), "erro")
            return 1

        destino = gravar_parquet(
            df, DIR_PROCESSADOS / ARQUIVO_PROCESSADO[base], coluna_data=esquema.coluna_data
        )
        alvo = " (com alvo)" if esquema.tem_alvo else ""
        log_step(
            f"Base {base}: {len(df):,} linhas x {df.shape[1]} colunas{alvo} -> {destino.name}",
            "ok",
        )

    # Realizados da base A: proibidos como preditora, indispensáveis como
    # gabarito para conferir as tabelas de EAD/LGD no S02.
    realizados = carregar_realizados()
    destino = gravar_parquet(realizados, DIR_PROCESSADOS / ARQUIVO_REALIZADOS)
    com_default = int(realizados["ead_realizado"].notna().sum())
    log_step(
        f"Realizados da base A: {len(realizados):,} linhas, "
        f"{com_default:,} com default -> {destino.name}",
        "ok",
    )

    log_step(f"Ingestão concluída. Arquivos em {DIR_PROCESSADOS}", "ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
