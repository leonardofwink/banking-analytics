"""S04 · Baseline — regressão logística.

O primeiro número de verdade do projeto. Treina no treino 2022–2023, mede na
validação 2024, e compara duas variantes:

- **completa** — todas as preditoras do dicionário;
- **independente de política** — sem ``comprometimento_renda``, que em C só
  existiria depois de a política decidir taxa e prazo.

A regra de escolha foi declarada **antes** de ver o resultado (spec S04.4):
diferença de AuROC menor que 0,01 → fica a independente, porque simplicidade e
ausência de circularidade valem mais que ganho dentro do ruído.

Rodar::

    .\\scripts\\py.cmd python\\modelagem\\04_baseline_logistica.py
"""

from __future__ import annotations

import sys

import pandas as pd

from banking.dados import carregar_processada
from banking.modelo import avaliar, coeficientes, construir_pipeline, preditoras
from banking.projeto import DIR_TABELAS, log_step, semear
from banking.split import dividir_temporal

# Declarado na spec, antes de qualquer resultado: abaixo disso a diferença é
# ruído, e a variante mais simples vence.
LIMIAR_DIFERENCA_AUROC = 0.01


def treinar_e_avaliar(treino: pd.DataFrame, validacao: pd.DataFrame, incluir: bool, nome: str):
    """Treina uma variante e devolve ``(modelo, resultado_treino, resultado_validacao)``."""
    semear()  # reprodutibilidade: mesma semente para as duas variantes
    modelo = construir_pipeline("logistica", incluir_dependentes_de_politica=incluir)
    modelo.fit(treino, treino["default_90_12"])
    return (
        modelo,
        avaliar(modelo, treino, nome, "treino"),
        avaliar(modelo, validacao, nome, "validação"),
    )


def main() -> int:
    log_step("S04 · Baseline — regressão logística")

    try:
        base_a = carregar_processada("A")
    except FileNotFoundError as erro:
        log_step(str(erro), "erro")
        return 1

    treino, validacao = dividir_temporal(base_a)
    num, cat = preditoras(True)
    log_step(f"{len(treino):,} de treino · {len(validacao):,} de validação")
    log_step(f"{len(num)} preditoras numéricas + {len(cat)} categóricas")

    modelo_completo, tr_c, val_c = treinar_e_avaliar(treino, validacao, True, "completa")
    modelo_simples, tr_s, val_s = treinar_e_avaliar(
        treino, validacao, False, "independente de política"
    )

    tabela = pd.DataFrame(
        [r.como_linha() for r in (tr_c, val_c, tr_s, val_s)]
    )
    print("\n--- Desempenho ---")
    print(tabela.to_string(index=False, float_format=lambda v: f"{v:.4f}"))

    # --- a escolha, pela regra declarada antes ------------------------------
    diferenca = val_c.auroc - val_s.auroc
    log_step(
        f"AuROC na validação — completa {val_c.auroc:.4f} · independente {val_s.auroc:.4f} "
        f"(diferença {diferenca:+.4f})"
    )

    if abs(diferenca) < LIMIAR_DIFERENCA_AUROC:
        escolhido, nome = modelo_simples, "independente de política"
        log_step(
            f"Diferença < {LIMIAR_DIFERENCA_AUROC}: fica a variante INDEPENDENTE DE POLÍTICA. "
            "Sem circularidade na escoragem da base C.",
            "ok",
        )
    else:
        escolhido, nome = modelo_completo, "completa"
        log_step(
            f"Diferença >= {LIMIAR_DIFERENCA_AUROC}: fica a variante COMPLETA. "
            "A escoragem da base C precisará das duas passagens.",
            "aviso",
        )

    melhor = val_c if nome == "completa" else val_s

    # --- sobreajuste --------------------------------------------------------
    treino_escolhido = tr_c if nome == "completa" else tr_s
    folga = treino_escolhido.auroc - melhor.auroc
    log_step(
        f"AuROC treino {treino_escolhido.auroc:.4f} vs validação {melhor.auroc:.4f} "
        f"(folga {folga:+.4f}) — folga grande indicaria sobreajuste",
        "ok" if folga < 0.05 else "aviso",
    )

    # --- calibração ---------------------------------------------------------
    log_step(
        f"Calibração: PD média prevista {melhor.pd_media:.4f} contra taxa observada "
        f"{melhor.taxa_observada:.4f} (erro {melhor.erro_de_calibracao:+.4f})",
        "ok" if abs(melhor.erro_de_calibracao) < 0.01 else "aviso",
    )

    # --- coeficientes: o insumo da defesa -----------------------------------
    coefs = coeficientes(escolhido)
    print("\n--- Coeficientes (10 maiores em módulo) ---")
    print(coefs.head(10).to_string(index=False, float_format=lambda v: f"{v:+.4f}"))

    DIR_TABELAS.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(DIR_TABELAS / "s04_desempenho.csv", index=False)
    coefs.to_csv(DIR_TABELAS / "s04_coeficientes.csv", index=False)
    log_step(f"Relatórios em {DIR_TABELAS}", "ok")

    log_step(
        f"Baseline: AuROC {melhor.auroc:.4f} · KS {melhor.ks:.4f} · Gini {melhor.gini:.4f} "
        f"(variante {nome})",
        "ok",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
