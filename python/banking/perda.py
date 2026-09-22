"""S02 · Perda esperada — o elo que transforma probabilidade em dinheiro.

    Perda esperada = PD × EAD × LGD

Neste desafio **só a PD é modelada**. EAD e LGD vêm prontos, em tabela, e este
módulo transforma essas tabelas em funções vetorizadas.

⚠️ **Convenção de unidade, válida para todo o módulo:**

- ``pd_``, ``lgd`` e o fator de EAD são **frações** (0 a 1). ``0.085``, nunca ``8.5``.
- ``valor_financiado``, ``ead`` e ``perda_esperada`` são **reais**.

O erro clássico de crédito é somar ou multiplicar tudo como se fosse percentual.
As funções aqui validam a faixa dos argumentos justamente para pegar isso.

As tabelas são **médias por célula** dos inadimplentes da base A, não valores
por contrato — o que é o certo para calcular perda *esperada*, mas esconde
dispersão real (desvio-padrão mediano da LGD dentro da célula: 0,099).
Ver ``docs/specs/S02_PERDA_ESPERADA.md``.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

import numpy as np
import pandas as pd

from banking.dados import (
    FAIXAS_IDADE_VEICULO,
    FAIXAS_LTV,
    Parametros,
    carregar_parametros_ead_lgd,
)

__all__ = [
    "AJUSTE_AVALISTA",
    "ead",
    "faixa_idade_veiculo",
    "faixa_ltv",
    "fator_ead",
    "lgd",
    "perda_esperada",
    "tabelas",
]

# Ajuste declarado pelo professor: somar isto à LGD da tabela quando o contrato
# tem avalista. O sinal é negativo — avalista reduz a perda.
AJUSTE_AVALISTA = -0.061

# Bordas das faixas de LTV, fechadas à direita: "até 60%" é ltv <= 0,60.
_BORDAS_LTV = (0.60, 0.70, 0.80, 0.90)

# Bordas das faixas de idade do veículo, em anos completos na originação.
_BORDAS_IDADE = (2, 5, 8)

ModoAvalista = Literal["oficial", "centrado"]


@lru_cache(maxsize=1)
def tabelas() -> Parametros:
    """Devolve os parâmetros do professor, lidos uma vez e memorizados.

    A leitura do arquivo vive em :mod:`banking.dados` (o módulo que concentra
    IO); este módulo só consome. O cache evita reler o Excel a cada chamada —
    as funções abaixo são usadas linha a linha em bases de milhares de registros.
    """
    return carregar_parametros_ead_lgd()


def _indice(valores, bordas) -> np.ndarray:
    """Converte valores em índice de faixa (0..len(bordas)), fechado à direita."""
    v = np.asarray(valores, dtype=float)
    # searchsorted com 'left' devolve o índice da primeira borda >= valor,
    # o que implementa exatamente o intervalo fechado à direita.
    return np.searchsorted(np.asarray(bordas, dtype=float), v, side="left")


def faixa_ltv(ltv) -> np.ndarray:
    """Classifica o LTV nas cinco faixas da tabela.

    Intervalos **fechados à direita**: ``até 60%`` é ``ltv <= 0.60``;
    ``60% a 70%`` é ``0.60 < ltv <= 0.70``. A convenção foi testada contra o
    gabarito e é indistinguível da alternativa (não há contratos na borda).

    :param ltv: fração entre 0 e 1 (``0.78``, não ``78``).
    :return: array de rótulos, iguais aos do Excel.
    """
    v = np.asarray(ltv, dtype=float)
    if np.nanmax(v, initial=0.0) > 1.5:
        raise ValueError(
            "LTV parece estar em percentual (valor > 1,5). Esta função espera "
            "fração: 0.78 para 78%."
        )
    return np.asarray(FAIXAS_LTV, dtype=object)[_indice(v, _BORDAS_LTV)]


def faixa_idade_veiculo(idade_anos) -> np.ndarray:
    """Classifica a idade do veículo na originação nas quatro faixas da tabela.

    :param idade_anos: inteiro em anos; ``0`` é zero quilômetro.
    """
    return np.asarray(FAIXAS_IDADE_VEICULO, dtype=object)[
        _indice(idade_anos, _BORDAS_IDADE)
    ]


def fator_ead(prazo_meses, ltv) -> np.ndarray:
    """Fator de EAD: quanto do valor financiado estará exposto no default.

    Passa de 1 porque o EAD soma as três parcelas vencidas que caracterizam o
    atraso de 90 dias ao saldo devedor pela Tabela Price. Varia pouco
    (0,98 a 1,04): **não é alavanca de política**.

    :param prazo_meses: 24, 36, 48 ou 60.
    :param ltv: fração entre 0 e 1.
    :return: fator (fração), a multiplicar pelo valor financiado.
    :raises KeyError: se o prazo não estiver na tabela.
    """
    tab = tabelas().fator_ead
    prazos = np.asarray(prazo_meses)
    desconhecidos = sorted(set(np.unique(prazos)) - set(tab.index))
    if desconhecidos:
        raise KeyError(
            f"Prazo(s) fora da tabela de EAD: {desconhecidos}. Esperado {list(tab.index)}."
        )
    linha = pd.Index(tab.index).get_indexer(prazos)
    coluna = _indice(ltv, _BORDAS_LTV)
    return tab.to_numpy()[linha, coluna]


def ead(valor_financiado, prazo_meses, ltv) -> np.ndarray:
    """Exposição no momento do default, **em reais**.

    :param valor_financiado: em reais.
    :return: ``fator_ead × valor_financiado``.
    """
    return fator_ead(prazo_meses, ltv) * np.asarray(valor_financiado, dtype=float)


def lgd(
    idade_veiculo_anos,
    ltv,
    possui_avalista=None,
    modo: ModoAvalista = "oficial",
) -> np.ndarray:
    """Fração do EAD que se perde após o workout de 24 meses.

    A tabela cresce com o risco: vai de **0,412** (carro de até 2 anos com LTV
    ≤ 60%) a **0,908** (9 anos ou mais com LTV > 90%). É a alavanca de verdade
    da política — 50 pontos de amplitude, contra 6 do fator de EAD.

    **Os dois modos de ajuste por avalista** (ver spec do S02):

    - ``"oficial"`` — soma ``-0,061`` quando há avalista, como manda o
      enunciado. É o padrão, porque é o parâmetro declarado. Tem viés
      conhecido de **−0,0121** (subestima a perda), porque a tabela já é a
      média de contratos com e sem avalista.
    - ``"centrado"`` — distribui o mesmo ajuste em torno da média
      (``-0,061×(1-s)`` para quem tem avalista, ``+0,061×s`` para quem não tem,
      com ``s`` = proporção de avalistas). Viés medido: −0,0001.

    :param idade_veiculo_anos: idade na originação, em anos.
    :param ltv: fração entre 0 e 1.
    :param possui_avalista: série de ``"Sim"``/``"Não"`` (ou booleano). Se
        ``None``, nenhum ajuste é aplicado.
    :param modo: ``"oficial"`` (padrão) ou ``"centrado"``.
    :return: fração em [0, 1].
    """
    tab = tabelas().lgd
    linha = _indice(idade_veiculo_anos, _BORDAS_IDADE)
    coluna = _indice(ltv, _BORDAS_LTV)
    valores = tab.to_numpy()[linha, coluna].astype(float)

    if possui_avalista is not None:
        tem = _tem_avalista(possui_avalista)
        if modo == "oficial":
            valores = valores + np.where(tem, AJUSTE_AVALISTA, 0.0)
        elif modo == "centrado":
            s = float(np.mean(tem))
            valores = valores + np.where(
                tem, AJUSTE_AVALISTA * (1.0 - s), -AJUSTE_AVALISTA * s
            )
        else:
            raise ValueError(f"modo inválido: {modo!r}. Use 'oficial' ou 'centrado'.")

    # A LGD é uma fração do EAD: não pode passar de 100% nem ficar negativa.
    return np.clip(valores, 0.0, 1.0)


def _tem_avalista(valores) -> np.ndarray:
    """Normaliza a coluna de avalista para booleano.

    A base traz ``"Sim"``/``"Não"``, mas aceitar booleano evita atrito em teste
    e em código que já converteu.
    """
    serie = pd.Series(np.asarray(valores).ravel())
    if serie.dtype == bool:
        return serie.to_numpy()
    return (
        serie.astype(str).str.strip().str.lower().isin({"sim", "s", "true", "1"}).to_numpy()
    )


def perda_esperada(
    pd_,
    valor_financiado,
    prazo_meses,
    ltv,
    idade_veiculo_anos,
    possui_avalista=None,
    modo: ModoAvalista = "oficial",
) -> np.ndarray:
    """Perda esperada do contrato, **em reais**.

    ``PD × EAD × LGD`` — a fórmula apresentada na mentoria, com a EAD já
    convertida em reais.

    Exemplo de leitura: PD 5%, valor financiado R$ 10.000, fator de EAD 1,03 e
    LGD 60% dão R$ 309. Não é o que vai acontecer com *aquele* cliente (ele
    paga tudo ou dá default): é a média esperada olhando mil contratos iguais.

    :param pd_: probabilidade de default, em **fração** (``0.085``, não ``8.5``).
    :return: perda esperada em reais.
    :raises ValueError: se a PD parecer estar em percentual.
    """
    p = np.asarray(pd_, dtype=float)
    if np.nanmax(p, initial=0.0) > 1.0:
        raise ValueError(
            "PD parece estar em percentual (valor > 1). Esta função espera "
            "fração: 0.085 para 8,5%."
        )
    return (
        p
        * ead(valor_financiado, prazo_meses, ltv)
        * lgd(idade_veiculo_anos, ltv, possui_avalista, modo=modo)
    )
