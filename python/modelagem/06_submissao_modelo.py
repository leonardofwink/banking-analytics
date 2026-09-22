"""S06 · Gera o `submissao_modelo.csv` — entregável 1.

Retreina o XGBoost escolhido no S05 na base A **inteira** (2022–2024) e escora
a base B (jan–jun/2025). O arquivo tem duas colunas — ``id_contrato`` e ``pd``
— e é o que o professor cruza com o gabarito dele para calcular o AuROC.

Rodar::

    .\\scripts\\py.cmd python\\modelagem\\06_submissao_modelo.py

Spec: ``docs/specs/S06_SUBMISSAO_MODELO.md``.
"""

from __future__ import annotations

import sys

import pandas as pd

from banking.dados import ALVO, carregar_processada
from banking.modelo import (
    HIPERPARAMETROS_ESCOLHIDOS,
    MODELO_ESCOLHIDO,
    treinar_modelo_final,
)
from banking.projeto import DIR_OUTPUTS, log_step
from banking.submissao import (
    ValidacaoFalhou,
    formatar_submissao,
    resumo_distribuicao,
    validar_submissao_modelo,
)

DIR_SUBMISSAO = DIR_OUTPUTS / "submissao"


def main() -> int:
    log_step("S06 · Escoragem da base B e geração da submissão do modelo")

    try:
        base_a = carregar_processada("A")
        base_b = carregar_processada("B")
    except FileNotFoundError as erro:
        log_step(str(erro), "erro")
        return 1

    # --- S06.2 · retreino na base A inteira ---------------------------------
    log_step(
        f"Treinando {MODELO_ESCOLHIDO} na base A inteira "
        f"({len(base_a):,} contratos, {int(base_a[ALVO].sum())} defaults) "
        f"com {HIPERPARAMETROS_ESCOLHIDOS}"
    )
    modelo = treinar_modelo_final(base_a)
    log_step("Modelo final treinado — sem conjunto de teste, por construção", "ok")

    # --- S06.3 · escoragem da base B ----------------------------------------
    pd_b = modelo.predict_proba(base_b)[:, 1]
    resumo = resumo_distribuicao(pd_b)
    log_step(
        f"Base B escorada: {resumo['n']:,} PDs · média {resumo['media']:.4f} · "
        f"mediana {resumo['mediana']:.4f} · faixa [{resumo['min']:.4f}, {resumo['max']:.4f}]",
        "ok",
    )

    # A base A tem 8,26% de default. Se a PD média da base B fugisse muito
    # disso, seria sinal de que o modelo está vendo uma população diferente —
    # e o S03 mostrou que B e A são quase idênticas (PSI ~0,002).
    taxa_a = float(base_a[ALVO].mean())
    desvio = resumo["media"] - taxa_a
    log_step(
        f"PD média {resumo['media']:.4f} contra {taxa_a:.4f} de default na base A "
        f"(desvio {desvio:+.4f})",
        "ok" if abs(desvio) < 0.02 else "aviso",
    )

    # --- S06.5 · o arquivo ---------------------------------------------------
    submissao = pd.DataFrame({"id_contrato": base_b["id_contrato"].to_numpy(), "pd": pd_b})

    try:
        validar_submissao_modelo(submissao, base_b["id_contrato"])
    except ValidacaoFalhou as erro:
        log_step(str(erro), "erro")
        return 1
    log_step("Validador passou: formato, ids, faixa e distribuição conferidos", "ok")

    DIR_SUBMISSAO.mkdir(parents=True, exist_ok=True)
    destino = DIR_SUBMISSAO / "submissao_modelo.csv"
    formatar_submissao(submissao).to_csv(destino, index=False)
    log_step(f"ENTREGÁVEL 1 gerado: {destino}", "ok")

    print("\n--- Primeiras linhas ---")
    print(submissao.head().to_string(index=False))
    print("\n--- Distribuição da PD na base B ---")
    for chave, valor in resumo.items():
        print(f"  {chave:>10}: {valor:,.4f}" if isinstance(valor, float) else f"  {chave:>10}: {valor:,}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
