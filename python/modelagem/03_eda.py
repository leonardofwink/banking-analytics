"""S03 · Exploratória e split temporal.

Três perguntas, nesta ordem:

1. **Como fica o split?** Treino 2022–2023, validação 2024 — fixado antes de
   qualquer modelo ser treinado.
2. **Quais variáveis discriminam?** IV univariado, calculado **só no treino**.
3. **Quanto o modelo vai extrapolar?** PSI da base A contra B e contra C.

A terceira é a que dimensiona o risco central do desafio: sabemos que a base C
é mar aberto, mas o PSI diz *em quais variáveis* e *quanto*.

Rodar::

    .\\scripts\\py.cmd python\\modelagem\\03_eda.py

Spec: ``docs/specs/S03_EDA_E_SPLIT.md``.
"""

from __future__ import annotations

import sys

import pandas as pd

from banking.dados import (
    ALVO,
    PREDITORAS_CATEGORICAS,
    PREDITORAS_NUMERICAS,
    carregar_processada,
)
from banking.metricas import classificar_iv, classificar_psi, iv, psi
from banking.projeto import DIR_TABELAS, log_step
from banking.split import dividir_temporal, resumo_split

# Variáveis de A/B e o nome equivalente em C. A base C traz o que o cliente
# PEDIU, não o que foi contratado — por isso os nomes mudam (ver S10).
EQUIVALENTES_EM_C = {
    "ltv": "ltv_desejado",
    "prazo_meses": "prazo_desejado_meses",
    "valor_financiado": "valor_financiado_desejado",
    "comprometimento_renda": None,  # não existe em C: depende da taxa que ofertarmos
}


def analisar_nulos(treino: pd.DataFrame) -> pd.DataFrame:
    """Mapa de ausência por variável, com a taxa de default de quem tem nulo.

    A pergunta não é só *quantos* nulos, e sim **se o nulo carrega risco**. Se
    quem não tem score de bureau quebra mais que a média, a ausência é
    informação — e imputar pela mediana joga esse sinal fora.
    """
    linhas = []
    for coluna in treino.columns:
        n_nulos = int(treino[coluna].isna().sum())
        if n_nulos == 0:
            continue
        ausente = treino[coluna].isna()
        linhas.append(
            {
                "variavel": coluna,
                "nulos": n_nulos,
                "pct": n_nulos / len(treino),
                "default_com_nulo": float(treino.loc[ausente, ALVO].mean()),
                "default_sem_nulo": float(treino.loc[~ausente, ALVO].mean()),
            }
        )
    tabela = pd.DataFrame(linhas)
    if not tabela.empty:
        tabela["diferenca"] = tabela["default_com_nulo"] - tabela["default_sem_nulo"]
        tabela = tabela.sort_values("diferenca", key=abs, ascending=False)
    return tabela


def analisar_iv(treino: pd.DataFrame) -> pd.DataFrame:
    """IV de cada preditora, calculado **só no treino**.

    Calcular no conjunto inteiro seria espiar a validação: a variável passaria
    a parecer boa porque viu a resposta.
    """
    linhas = []
    for coluna in (*PREDITORAS_NUMERICAS, *PREDITORAS_CATEGORICAS):
        if coluna not in treino.columns:
            continue
        valor = iv(treino[coluna], treino[ALVO])
        linhas.append({"variavel": coluna, "iv": valor, "leitura": classificar_iv(valor)})
    return pd.DataFrame(linhas).sort_values("iv", ascending=False).reset_index(drop=True)


def analisar_psi(base_a: pd.DataFrame, base_b: pd.DataFrame, base_c: pd.DataFrame) -> pd.DataFrame:
    """PSI da base A contra B e contra C, variável a variável."""
    linhas = []
    for coluna in (*PREDITORAS_NUMERICAS, *PREDITORAS_CATEGORICAS):
        if coluna not in base_a.columns:
            continue

        psi_b = psi(base_a[coluna], base_b[coluna]) if coluna in base_b.columns else None

        coluna_c = EQUIVALENTES_EM_C.get(coluna, coluna)
        psi_c = (
            psi(base_a[coluna], base_c[coluna_c])
            if coluna_c and coluna_c in base_c.columns
            else None
        )

        linhas.append(
            {
                "variavel": coluna,
                "coluna_em_C": coluna_c,
                "psi_A_para_B": psi_b,
                "psi_A_para_C": psi_c,
                "leitura_C": classificar_psi(psi_c) if psi_c is not None else "não existe em C",
            }
        )
    return (
        pd.DataFrame(linhas)
        .sort_values("psi_A_para_C", ascending=False, na_position="last")
        .reset_index(drop=True)
    )


def main() -> int:
    log_step("S03 · Exploratória e split temporal")

    try:
        base_a = carregar_processada("A")
        base_b = carregar_processada("B")
        base_c = carregar_processada("C")
    except FileNotFoundError as erro:
        log_step(str(erro), "erro")
        return 1

    # --- S03.1 · o split ----------------------------------------------------
    treino, validacao = dividir_temporal(base_a)
    resumo = resumo_split(treino, validacao)
    log_step("Split temporal (fixado ANTES de qualquer modelo):", "ok")
    print(resumo.to_string(index=False))

    # --- S03.3 · nulos ------------------------------------------------------
    nulos = analisar_nulos(treino)
    print("\n--- Nulos no treino (o nulo carrega risco?) ---")
    print(nulos.to_string(index=False, float_format=lambda v: f"{v:.4f}"))

    # --- S03.4 · IV ---------------------------------------------------------
    tabela_iv = analisar_iv(treino)
    print("\n--- Poder preditivo univariado (IV, só no treino) ---")
    print(tabela_iv.to_string(index=False, float_format=lambda v: f"{v:.4f}"))

    suspeitas = tabela_iv[tabela_iv["iv"] > 0.5]
    if not suspeitas.empty:
        log_step(
            f"IV > 0,5 em {list(suspeitas['variavel'])} — suspeita de vazamento, investigar",
            "erro",
        )
    else:
        log_step("Nenhuma variável com IV suspeito (> 0,5).", "ok")

    # --- S03.5 · PSI --------------------------------------------------------
    tabela_psi = analisar_psi(base_a, base_b, base_c)
    print("\n--- Estabilidade da população (PSI) ---")
    print(tabela_psi.to_string(index=False, float_format=lambda v: f"{v:.4f}"))

    instaveis = tabela_psi[tabela_psi["psi_A_para_C"] > 0.25]["variavel"].tolist()
    if instaveis:
        log_step(
            f"Instáveis em C (PSI > 0,25): {instaveis} — é aqui que o modelo extrapola",
            "aviso",
        )

    # --- relatórios ---------------------------------------------------------
    DIR_TABELAS.mkdir(parents=True, exist_ok=True)
    for nome, tabela in (
        ("s03_split", resumo),
        ("s03_nulos", nulos),
        ("s03_iv", tabela_iv),
        ("s03_psi", tabela_psi),
    ):
        destino = DIR_TABELAS / f"{nome}.csv"
        tabela.to_csv(destino, index=False)
    log_step(f"Relatórios gravados em {DIR_TABELAS}", "ok")

    return 0


if __name__ == "__main__":
    sys.exit(main())
