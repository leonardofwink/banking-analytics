"""S08.1 · Tabela Price — a aritmética do financiamento.

Três funções, e a terceira é a que importa para o ROI: **quanto de juros a
AutoCred recebeu de um contrato que quebrou no mês m**.

A distinção é essencial. Quem quebra no mês 6 de um contrato de 48 pagou seis
parcelas — mas parcela **não é receita**: parte dela é amortização do principal,
que é devolução de dinheiro, não ganho. Só a parte de juros conta como receita,
e a perda é apurada sobre o saldo que ficou.

Convenção de unidade: ``taxa`` é a taxa **mensal em fração** (``0.0159`` para
1,59% a.m.), ``prazo`` em meses, valores em reais.
"""

from __future__ import annotations

import numpy as np

__all__ = ["juros_pagos_ate", "juros_totais", "parcela", "saldo_devedor"]


def parcela(principal, taxa, prazo) -> np.ndarray:
    """Parcela fixa pela Tabela Price.

    ``P × i / (1 − (1+i)^−n)``

    Verificado contra a base A: reproduz a coluna ``parcela_mensal`` com erro
    relativo médio de 0,0003%.

    :param principal: valor financiado, em reais.
    :param taxa: taxa mensal em fração (``0.0159``, não ``1.59``).
    :param prazo: número de parcelas.
    """
    P = np.asarray(principal, dtype=float)
    i = np.asarray(taxa, dtype=float)
    n = np.asarray(prazo, dtype=float)

    if np.nanmax(i, initial=0.0) > 1.0:
        raise ValueError(
            "taxa parece estar em percentual (valor > 1). Esta função espera "
            "fração mensal: 0.0159 para 1,59% a.m."
        )

    # Taxa zero degenera a fórmula (divisão por zero): vira amortização simples.
    with np.errstate(divide="ignore", invalid="ignore"):
        fator = np.where(i == 0, 1.0 / n, i / (1.0 - (1.0 + i) ** (-n)))
    return P * fator


def saldo_devedor(principal, taxa, prazo, mes) -> np.ndarray:
    """Saldo devedor imediatamente após a parcela do mês indicado.

    ``P × [(1+i)^n − (1+i)^m] / [(1+i)^n − 1]``

    :param mes: quantas parcelas já foram pagas. ``0`` devolve o principal;
        ``prazo`` devolve zero.
    """
    P = np.asarray(principal, dtype=float)
    i = np.asarray(taxa, dtype=float)
    n = np.asarray(prazo, dtype=float)
    m = np.clip(np.asarray(mes, dtype=float), 0, n)

    with np.errstate(divide="ignore", invalid="ignore"):
        saldo = np.where(
            i == 0,
            P * (1.0 - m / n),
            P * ((1.0 + i) ** n - (1.0 + i) ** m) / ((1.0 + i) ** n - 1.0),
        )
    return np.maximum(saldo, 0.0)


def juros_pagos_ate(principal, taxa, prazo, mes) -> np.ndarray:
    """Juros efetivamente recebidos nas primeiras ``mes`` parcelas.

    ``parcela × m − (P − saldo_m)`` — o total pago menos o principal amortizado.

    É **esta** a receita de um contrato que quebra: as parcelas pagas contêm
    amortização, e amortização é devolução de principal, não ganho. Contar a
    parcela inteira como receita superestimaria o ROI de toda carteira com
    inadimplência.

    :param mes: mês do default (ou ``prazo``, para quem pagou tudo).
    """
    P = np.asarray(principal, dtype=float)
    m = np.asarray(mes, dtype=float)
    pago = parcela(P, taxa, prazo) * m
    amortizado = P - saldo_devedor(P, taxa, prazo, m)
    return pago - amortizado


def juros_totais(principal, taxa, prazo) -> np.ndarray:
    """Juros de um contrato pago até o fim: ``parcela × n − P``."""
    P = np.asarray(principal, dtype=float)
    return parcela(P, taxa, prazo) * np.asarray(prazo, dtype=float) - P
