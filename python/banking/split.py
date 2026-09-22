"""S03.1 · Split temporal — a partição decidida ANTES de ver qualquer resultado.

    treino     2022–2023   ajusta o modelo
    validação  2024        escolhe o modelo e o hiperparâmetro
    base B     2025        o professor mede o AuROC (não temos o alvo)

**Por que temporal e não aleatório.** O enunciado é explícito: *"crédito tem
ordem temporal. Split aleatório é otimista por construção; o teste honesto é o
período seguinte."* Embaralhar os anos deixaria o modelo aprender com contratos
de 2024 para prever contratos de 2022 — o que nunca acontece na vida real. Como
a avaliação é out-of-time (2025 contra 2022–2024), a validação precisa imitar
exatamente essa condição.

**Por que fixar antes.** Quem testa vários splits e fica com o que deu o melhor
AuROC não escolheu o melhor modelo: escolheu o split mais sortudo. E sorte não
se repete na base B, que é onde a nota acontece.
"""

from __future__ import annotations

import pandas as pd

__all__ = ["ANO_VALIDACAO", "COLUNA_DATA", "dividir_temporal", "resumo_split"]

# O último ano da base A fica de fora do treino e serve de validação. É o
# recorte mais próximo possível da condição real: treinar no passado, medir no
# período seguinte.
ANO_VALIDACAO = 2024

COLUNA_DATA = "data_originacao"


def dividir_temporal(
    df: pd.DataFrame, ano_validacao: int = ANO_VALIDACAO, coluna_data: str = COLUNA_DATA
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separa a base A em treino (anterior) e validação (o ano indicado).

    :param df: base A carregada por ``banking.dados.carregar("A")``.
    :param ano_validacao: ano que vira validação. Padrão: 2024.
    :param coluna_data: coluna de data de originação.
    :return: ``(treino, validacao)`` — cópias, para não haver efeito colateral
        sobre o DataFrame de entrada.
    :raises ValueError: se a coluna de data não existir ou se algum dos lados
        sair vazio (sinal de que a base ou o ano mudaram).
    """
    if coluna_data not in df.columns:
        raise ValueError(
            f"coluna {coluna_data!r} ausente — o split temporal depende dela. "
            f"Colunas disponíveis: {sorted(df.columns)[:8]}..."
        )

    ano = pd.to_datetime(df[coluna_data]).dt.year
    treino = df.loc[ano < ano_validacao].copy()
    validacao = df.loc[ano == ano_validacao].copy()

    if treino.empty or validacao.empty:
        raise ValueError(
            f"split degenerado: treino={len(treino)}, validação={len(validacao)}. "
            f"A base cobre {ano.min()}–{ano.max()} e o ano de validação é {ano_validacao}."
        )

    return treino, validacao


def resumo_split(
    treino: pd.DataFrame, validacao: pd.DataFrame, alvo: str = "default_90_12"
) -> pd.DataFrame:
    """Tabela com tamanho, período e taxa de default de cada lado.

    A taxa de default costuma diferir entre treino e validação — e isso é
    esperado, não defeito. É a razão de a comparação de modelos usar AuROC e
    KS (que medem ordenação) em vez de acurácia (que depende da prevalência).
    """
    linhas = []
    for nome, parte in (("treino", treino), ("validação", validacao)):
        datas = pd.to_datetime(parte[COLUNA_DATA])
        linhas.append(
            {
                "particao": nome,
                "n": len(parte),
                "inicio": datas.min().date(),
                "fim": datas.max().date(),
                "defaults": int(parte[alvo].sum()) if alvo in parte else None,
                "taxa_default": float(parte[alvo].mean()) if alvo in parte else None,
            }
        )
    return pd.DataFrame(linhas)
