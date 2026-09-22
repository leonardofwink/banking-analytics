"""S02.6 · Valida os parâmetros de EAD e LGD contra o gabarito da base A.

A base A traz ``ead_realizado`` e ``lgd_realizado`` dos 826 contratos que
realmente deram default. Isso permite conferir se interpretamos as tabelas do
professor corretamente **antes** de construir a política inteira em cima delas.

A comparação é **média por célula**, não linha a linha: as tabelas são a média
dos inadimplentes de cada célula, e dentro da célula a LGD real varia bastante.
Comparar contrato a contrato daria erro de 0,098 e pareceria erro de
interpretação — não é.

Rodar::

    .\\scripts\\py.cmd python\\etl\\02_parametros_ead_lgd.py

Spec: ``docs/specs/S02_PERDA_ESPERADA.md``.
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from banking.dados import ALVO, carregar_bruto
from banking.perda import faixa_idade_veiculo, faixa_ltv, fator_ead, lgd
from banking.projeto import DIR_TABELAS, log_step

# Tolerâncias do DoD: erro médio por célula acima disto significa que
# interpretamos a tabela errado, e aí nada construído em cima dela vale.
TOLERANCIA_LGD = 0.001
TOLERANCIA_EAD = 0.005


def _inadimplentes() -> pd.DataFrame:
    """Os contratos da base A que deram default, com as faixas já classificadas."""
    base = carregar_bruto("A")
    d = base[base[ALVO] == 1].copy()
    d["faixa_ltv"] = faixa_ltv(d["ltv"])
    d["faixa_idade_veiculo"] = faixa_idade_veiculo(d["idade_veiculo_anos"])
    d["fator_realizado"] = d["ead_realizado"] / d["valor_financiado"]
    return d


def validar_lgd(d: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    """Compara a LGD média observada por célula com a tabela do professor."""
    observado = d.pivot_table(
        index="faixa_idade_veiculo", columns="faixa_ltv", values="lgd_realizado", aggfunc="mean"
    )
    # Sem ajuste de avalista: a tabela é a média de todos os inadimplentes da
    # célula, com e sem avalista misturados. É essa média que queremos comparar.
    esperado = pd.DataFrame(
        {
            col: lgd(
                [_idade_representativa(idx) for idx in observado.index],
                [_ltv_representativo(col)] * len(observado.index),
            )
            for col in observado.columns
        },
        index=observado.index,
    )
    diferenca = (observado - esperado).abs()
    return diferenca, float(diferenca.to_numpy().mean())


def validar_ead(d: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    """Compara o fator de EAD médio observado por célula com a tabela."""
    observado = d.pivot_table(
        index="prazo_meses", columns="faixa_ltv", values="fator_realizado", aggfunc="mean"
    )
    esperado = pd.DataFrame(
        {
            col: fator_ead(list(observado.index), [_ltv_representativo(col)] * len(observado.index))
            for col in observado.columns
        },
        index=observado.index,
    )
    diferenca = (observado - esperado).abs()
    return diferenca, float(diferenca.to_numpy().mean())


def medir_vies_avalista(d: pd.DataFrame) -> dict[str, float]:
    """Quantifica o viés do ajuste de avalista nos dois modos.

    A regra oficial (somar −0,061 só para quem tem avalista) é aplicada sobre
    uma tabela que **já** mistura contratos com e sem avalista — o que conta o
    benefício duas vezes. Este bloco mede o tamanho do efeito.
    """
    base_tabela = lgd(d["idade_veiculo_anos"], d["ltv"])  # sem ajuste
    residuo = d["lgd_realizado"].to_numpy() - base_tabela
    tem = d["possui_avalista"].eq("Sim").to_numpy()

    oficial = lgd(d["idade_veiculo_anos"], d["ltv"], d["possui_avalista"], modo="oficial")
    centrado = lgd(d["idade_veiculo_anos"], d["ltv"], d["possui_avalista"], modo="centrado")

    return {
        "share_avalista": float(tem.mean()),
        "residuo_com_avalista": float(residuo[tem].mean()),
        "residuo_sem_avalista": float(residuo[~tem].mean()),
        "efeito_observado": float(residuo[~tem].mean() - residuo[tem].mean()),
        "vies_oficial": float((oficial - d["lgd_realizado"].to_numpy()).mean()),
        "vies_centrado": float((centrado - d["lgd_realizado"].to_numpy()).mean()),
    }


# As funções recebem valores, não rótulos — estes helpers devolvem um valor
# qualquer dentro de cada faixa, para reconstruir a tabela a partir das funções.
def _ltv_representativo(rotulo: str) -> float:
    return {
        "até 60%": 0.50,
        "60% a 70%": 0.65,
        "70% a 80%": 0.75,
        "80% a 90%": 0.85,
        "acima de 90%": 0.95,
    }[rotulo]


def _idade_representativa(rotulo: str) -> int:
    return {"0 a 2 anos": 1, "3 a 5 anos": 4, "6 a 8 anos": 7, "9 anos ou mais": 12}[rotulo]


def main() -> int:
    log_step("S02 · Validação dos parâmetros de EAD e LGD contra o gabarito")

    try:
        d = _inadimplentes()
    except FileNotFoundError as erro:
        log_step(str(erro), "erro")
        return 1

    log_step(f"{len(d):,} contratos inadimplentes na base A (o gabarito)")

    dif_lgd, erro_lgd = validar_lgd(d)
    dif_ead, erro_ead = validar_ead(d)

    nivel = "ok" if erro_lgd < TOLERANCIA_LGD else "erro"
    log_step(
        f"LGD  — erro médio por célula: {erro_lgd:.5f} (máx {dif_lgd.to_numpy().max():.5f}) "
        f"| tolerância {TOLERANCIA_LGD}",
        nivel,
    )
    nivel = "ok" if erro_ead < TOLERANCIA_EAD else "erro"
    log_step(
        f"EAD  — erro médio por célula: {erro_ead:.5f} (máx {dif_ead.to_numpy().max():.5f}) "
        f"| tolerância {TOLERANCIA_EAD}",
        nivel,
    )

    vies = medir_vies_avalista(d)
    log_step(
        f"Avalista — {vies['share_avalista']:.1%} dos inadimplentes; "
        f"efeito observado {vies['efeito_observado']:+.4f} (declarado 0,0610)",
        "aviso",
    )
    log_step(
        f"Viés da regra oficial: {vies['vies_oficial']:+.4f} (subestima a perda) | "
        f"centrada: {vies['vies_centrado']:+.4f}",
        "aviso",
    )

    # Dispersão dentro da célula: o que a média esconde.
    disp = d.groupby(["faixa_idade_veiculo", "faixa_ltv"], observed=True)["lgd_realizado"].std()
    log_step(
        f"Dispersão da LGD dentro da célula: mediana {disp.median():.4f}, máx {disp.max():.4f} "
        "— a tabela é média, não destino",
        "aviso",
    )

    destino = DIR_TABELAS / "s02_validacao_parametros.csv"
    relatorio = pd.concat(
        [
            dif_lgd.stack().rename("erro_absoluto").reset_index().assign(tabela="LGD"),
            dif_ead.stack().rename("erro_absoluto").reset_index().assign(tabela="fator_EAD"),
        ],
        ignore_index=True,
    )
    destino.parent.mkdir(parents=True, exist_ok=True)
    relatorio.to_csv(destino, index=False)
    log_step(f"Relatório gravado em {destino}", "ok")

    aprovado = erro_lgd < TOLERANCIA_LGD and erro_ead < TOLERANCIA_EAD
    log_step(
        "Parâmetros validados: as tabelas foram interpretadas corretamente."
        if aprovado
        else "VALIDAÇÃO FALHOU — não construa a política sobre estes parâmetros.",
        "ok" if aprovado else "erro",
    )
    return 0 if aprovado else 1


if __name__ == "__main__":
    sys.exit(main())
