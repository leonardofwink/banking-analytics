"""S05 · Desafiantes — Random Forest e XGBoost contra a logística.

O ponto metodológico deste passo: **os hiperparâmetros são escolhidos por
validação cruzada temporal DENTRO do treino**, sem tocar a validação 2024.

Se testássemos 12 configurações na validação e ficássemos com a melhor, o
número que sobra não seria performance — seria o máximo de 12 sorteios. E esse
máximo não se repete na base B, que é onde a nota acontece. A validação é
medida **uma única vez**, no fim, com a configuração já escolhida.

Rodar::

    .\\scripts\\py.cmd python\\modelagem\\05_desafiantes.py

Spec: ``docs/specs/S05_DESAFIANTES.md``.
"""

from __future__ import annotations

import sys
import warnings

import pandas as pd
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit, cross_val_score

from banking.dados import ALVO, carregar_processada
from banking.modelo import avaliar, construir_pipeline
from banking.projeto import DIR_TABELAS, log_step, semear
from banking.split import COLUNA_DATA, dividir_temporal

# Declarado na spec, antes de qualquer resultado.
LIMIAR_DIFERENCA_AUROC = 0.01

N_DOBRAS = 3

# Grades pequenas de propósito: cada configuração testada é mais uma chance de
# achar um bom resultado por acaso. O treino tem 587 defaults — pouco para
# modelo complexo —, então a busca privilegia árvores rasas e regularizadas.
GRADES = {
    "random_forest": {
        "modelo__max_depth": [4, 6, 8],
        "modelo__min_samples_leaf": [20, 50],
        "modelo__class_weight": [None, "balanced"],
    },
    "xgboost": {
        "modelo__max_depth": [3, 4, 5],
        "modelo__learning_rate": [0.05, 0.1],
        "modelo__min_child_weight": [5, 20],
    },
}


def buscar(tipo: str, treino: pd.DataFrame) -> tuple[object, dict, float]:
    """Escolhe hiperparâmetros por CV temporal dentro do treino.

    ``TimeSeriesSplit`` sobre o treino **ordenado por data** mantém a regra de
    ouro do projeto: sempre treinar no passado e medir no período seguinte,
    inclusive dentro da busca.

    :return: ``(melhor_pipeline, melhores_parametros, auroc_medio_na_cv)``.
    """
    semear()
    ordenado = treino.sort_values(COLUNA_DATA).reset_index(drop=True)

    busca = GridSearchCV(
        estimator=construir_pipeline(tipo, incluir_dependentes_de_politica=False),
        param_grid=GRADES[tipo],
        scoring="roc_auc",
        cv=TimeSeriesSplit(n_splits=N_DOBRAS),
        n_jobs=-1,
        refit=True,  # reajusta no treino inteiro com a melhor configuração
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        busca.fit(ordenado, ordenado[ALVO])

    return busca.best_estimator_, busca.best_params_, float(busca.best_score_)


def main() -> int:
    log_step("S05 · Desafiantes — Random Forest e XGBoost")

    try:
        base_a = carregar_processada("A")
    except FileNotFoundError as erro:
        log_step(str(erro), "erro")
        return 1

    treino, validacao = dividir_temporal(base_a)
    log_step(
        f"{len(treino):,} de treino ({int(treino[ALVO].sum())} defaults) · "
        f"{len(validacao):,} de validação ({int(validacao[ALVO].sum())} defaults)"
    )

    modelos: dict[str, object] = {}
    resultados: list[dict] = []

    # --- baseline: a régua, sem busca --------------------------------------
    # A logística também passa pela CV temporal, embora não tenha grade: sem
    # isso, o número de CV dos desafiantes não teria com o que ser comparado, e
    # sobraria só a validação — um conjunto só, medido uma vez.
    semear()
    logistica = construir_pipeline("logistica", incluir_dependentes_de_politica=False)
    ordenado = treino.sort_values(COLUNA_DATA).reset_index(drop=True)
    auroc_cv_logistica = float(
        cross_val_score(
            logistica,
            ordenado,
            ordenado[ALVO],
            scoring="roc_auc",
            cv=TimeSeriesSplit(n_splits=N_DOBRAS),
            n_jobs=-1,
        ).mean()
    )
    logistica.fit(treino, treino[ALVO])
    modelos["logistica"] = logistica
    for conjunto, dados in (("treino", treino), ("validação", validacao)):
        linha = avaliar(logistica, dados, "logistica", conjunto).como_linha()
        linha["auroc_cv"] = auroc_cv_logistica if conjunto == "validação" else None
        resultados.append(linha)
    log_step(
        f"Baseline (logística): AuROC médio na CV {auroc_cv_logistica:.4f} — sem busca", "ok"
    )

    # --- desafiantes --------------------------------------------------------
    for tipo in ("random_forest", "xgboost"):
        n_combinacoes = 1
        for valores in GRADES[tipo].values():
            n_combinacoes *= len(valores)
        log_step(
            f"{tipo}: buscando {n_combinacoes} configurações × {N_DOBRAS} dobras "
            "(CV temporal dentro do treino)"
        )

        modelo, melhores, auroc_cv = buscar(tipo, treino)
        modelos[tipo] = modelo

        limpos = {k.replace("modelo__", ""): v for k, v in melhores.items()}
        log_step(f"{tipo}: AuROC médio na CV {auroc_cv:.4f} · melhor config {limpos}", "ok")

        for conjunto, dados in (("treino", treino), ("validação", validacao)):
            linha = avaliar(modelo, dados, tipo, conjunto).como_linha()
            linha["auroc_cv"] = auroc_cv if conjunto == "validação" else None
            resultados.append(linha)

    tabela = pd.DataFrame(resultados)
    print("\n--- Comparação (validação 2024 medida UMA vez) ---")
    print(
        tabela[tabela["conjunto"] == "validação"]
        .drop(columns=["conjunto"])
        .to_string(index=False, float_format=lambda v: f"{v:.4f}")
    )

    print("\n--- Sobreajuste: folga entre treino e validação ---")
    folgas = []
    for nome in modelos:
        tr = tabela[(tabela["modelo"] == nome) & (tabela["conjunto"] == "treino")]["auroc"].iloc[0]
        val = tabela[(tabela["modelo"] == nome) & (tabela["conjunto"] == "validação")]["auroc"].iloc[0]
        folgas.append({"modelo": nome, "auroc_treino": tr, "auroc_validacao": val, "folga": tr - val})
    folga_tab = pd.DataFrame(folgas)
    print(folga_tab.to_string(index=False, float_format=lambda v: f"{v:.4f}"))

    # --- a escolha, pela regra declarada antes ------------------------------
    na_validacao = tabela[tabela["conjunto"] == "validação"].set_index("modelo")
    melhor_nome = na_validacao["auroc"].idxmax()
    melhor_auroc = na_validacao.loc[melhor_nome, "auroc"]
    auroc_logistica = na_validacao.loc["logistica", "auroc"]
    ganho = melhor_auroc - auroc_logistica

    log_step(
        f"Melhor AuROC: {melhor_nome} com {melhor_auroc:.4f} "
        f"(logística {auroc_logistica:.4f}, ganho {ganho:+.4f})"
    )

    if ganho < LIMIAR_DIFERENCA_AUROC:
        escolhido = "logistica"
        log_step(
            f"Ganho < {LIMIAR_DIFERENCA_AUROC}: fica a LOGÍSTICA. Diferença dentro do ruído "
            f"({int(validacao[ALVO].sum())} defaults na validação), e ela é explicável "
            "coeficiente a coeficiente — a defesa vale 20 pontos absolutos.",
            "ok",
        )
    else:
        escolhido = melhor_nome
        log_step(
            f"Ganho >= {LIMIAR_DIFERENCA_AUROC}: fica o {melhor_nome.upper()}. "
            "A explicabilidade terá de vir de SHAP na defesa.",
            "ok",
        )

    # Árvores produzem probabilidade pior calibrada, e a política precisa de
    # nível, não só de ordenação — por isso o Brier entra na decisão.
    brier_escolhido = na_validacao.loc[escolhido, "brier"]
    brier_logistica = na_validacao.loc["logistica", "brier"]
    log_step(
        f"Calibração (Brier, menor é melhor): {escolhido} {brier_escolhido:.5f} · "
        f"logística {brier_logistica:.5f}",
        "ok" if brier_escolhido <= brier_logistica else "aviso",
    )

    DIR_TABELAS.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(DIR_TABELAS / "s05_comparacao.csv", index=False)
    folga_tab.to_csv(DIR_TABELAS / "s05_sobreajuste.csv", index=False)
    log_step(f"Relatórios em {DIR_TABELAS}", "ok")
    log_step(f"MODELO ESCOLHIDO PARA A SUBMISSÃO: {escolhido}", "ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
