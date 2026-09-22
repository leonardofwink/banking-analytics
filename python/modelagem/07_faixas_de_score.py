"""S07 · Faixas de score — distribuição, perda esperada e acumulado de aprovação.

Verifica que os cortes do `banking/score.py` satisfazem os critérios da spec, e
produz a tabela que o S09 vai usar para escolher o corte de aprovação.

Rodar::

    .\\scripts\\py.cmd python\\modelagem\\07_faixas_de_score.py

Spec: ``docs/specs/S07_FAIXAS_DE_SCORE.md``.
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from banking.dados import carregar_processada, preparar_base_c
from banking.modelo import treinar_modelo_final
from banking.perda import fator_ead, lgd
from banking.projeto import DIR_TABELAS, log_step
from banking.score import SCORE_MAXIMO, SCORE_MINIMO, score_de_pd, tabela_de_faixas

# Critério 2 da spec: faixa com menos que isto não sustenta decisão de preço.
OCUPACAO_MINIMA = 0.03

# Guard-rails do desafio, para marcar onde cada um morde.
APROVACAO_MINIMA = 0.35
INADIMPLENCIA_MAXIMA = 0.08
VOLUME_MINIMO = 40_000_000


def main() -> int:
    log_step("S07 · Faixas de score")

    try:
        base_a = carregar_processada("A")
        base_b = carregar_processada("B")
        base_c = carregar_processada("C")
    except FileNotFoundError as erro:
        log_step(str(erro), "erro")
        return 1

    modelo = treinar_modelo_final(base_a)
    c = preparar_base_c(base_c)
    pd_c = modelo.predict_proba(c)[:, 1]
    pd_b = modelo.predict_proba(base_b)[:, 1]

    log_step(f"PD média — base B {pd_b.mean():.4f} · base C {pd_c.mean():.4f}")
    log_step(
        f"A base C é {pd_c.mean() / pd_b.mean():.1f}× mais arriscada que a B — mar aberto",
        "aviso",
    )

    # --- S07.3 · distribuição ----------------------------------------------
    tabela = tabela_de_faixas(pd_c, pesos=c["valor_financiado"])

    # --- S07.4 · perda esperada por faixa -----------------------------------
    el_fracao = (
        pd_c
        * fator_ead(c["prazo_meses"], c["ltv"])
        * lgd(c["idade_veiculo_anos"], c["ltv"], c["possui_avalista"])
    )
    por_faixa = (
        pd.DataFrame({"score": score_de_pd(pd_c), "el": el_fracao})
        .groupby("score")["el"]
        .mean()
        .rename("perda_esperada")
    )
    tabela = tabela.merge(por_faixa, on="score", how="left")

    print("\n--- Faixas de score na base C ---")
    exibicao = tabela.assign(
        faixa_pd=lambda d: d.apply(
            lambda r: f"{r.pd_minima:.1%} – {r.pd_maxima:.1%}", axis=1
        ),
        pct=lambda d: d.pct.map("{:.1%}".format),
        pd_media=lambda d: d.pd_media.map("{:.2%}".format),
        perda_esperada=lambda d: d.perda_esperada.map("{:.2%}".format),
        volume_mi=lambda d: (d.volume / 1e6).map("{:.1f}".format),
    )[["score", "faixa_pd", "n", "pct", "pd_media", "perda_esperada", "volume_mi"]]
    print(exibicao.to_string(index=False))

    # --- verificação dos critérios ------------------------------------------
    problemas = []

    irrelevantes = tabela[tabela["n"] / len(pd_c) < OCUPACAO_MINIMA]["score"].tolist()
    if irrelevantes:
        problemas.append(f"faixas abaixo de {OCUPACAO_MINIMA:.0%} da base C: {irrelevantes}")

    # Monotonicidade: score maior, perda esperada menor.
    ordenada = tabela.sort_values("score", ascending=False)["perda_esperada"].to_numpy()
    if not np.all(np.diff(ordenada) > 0):
        problemas.append("a perda esperada não é monotônica no score")

    # Faixas vizinhas precisam ser economicamente distintas.
    razoes = ordenada[1:] / ordenada[:-1]
    if razoes.min() < 1.15:
        problemas.append(
            f"faixas vizinhas quase idênticas em perda esperada (razão mínima {razoes.min():.2f})"
        )

    if problemas:
        for p in problemas:
            log_step(p, "erro")
        return 1
    log_step(
        f"Critérios atendidos: nenhuma faixa abaixo de {OCUPACAO_MINIMA:.0%}, "
        f"perda esperada monotônica, vizinhas distintas (razão mínima {razoes.min():.2f}×)",
        "ok",
    )

    # --- S07.5 · o acumulado que o S09 vai usar -----------------------------
    print("\n--- Aprovando de cima para baixo (insumo do S09) ---")
    linhas = []
    for corte in range(SCORE_MAXIMO, SCORE_MINIMO - 1, -1):
        dentro = score_de_pd(pd_c) >= corte
        n = int(dentro.sum())
        linhas.append(
            {
                "corte": corte,
                "aprovados": n,
                "taxa_aprovacao": n / len(pd_c),
                "volume_desejado": float(c.loc[dentro, "valor_financiado"].sum()),
                "pd_carteira": float(pd_c[dentro].mean()) if n else np.nan,
            }
        )
    acumulado = pd.DataFrame(linhas)

    def marcar(r):
        avisos = []
        if r.taxa_aprovacao < APROVACAO_MINIMA:
            avisos.append("aprovação < 35%")
        if r.pd_carteira > INADIMPLENCIA_MAXIMA:
            avisos.append("inadimplência > 8%")
        if r.volume_desejado < VOLUME_MINIMO:
            avisos.append("volume < R$ 40 mi")
        return " · ".join(avisos) if avisos else "dentro dos guard-rails"

    acumulado["guard_rails"] = acumulado.apply(marcar, axis=1)
    print(
        acumulado.assign(
            taxa_aprovacao=lambda d: d.taxa_aprovacao.map("{:.1%}".format),
            volume_desejado=lambda d: (d.volume_desejado / 1e6).map("R$ {:.1f} mi".format),
            pd_carteira=lambda d: d.pd_carteira.map("{:.2%}".format),
        ).to_string(index=False)
    )

    viaveis = acumulado[acumulado["guard_rails"] == "dentro dos guard-rails"]
    if not viaveis.empty:
        log_step(
            f"Cortes que respeitam os três guard-rails (sobre o desejado): "
            f"score >= {viaveis['corte'].max()} até score >= {viaveis['corte'].min()}",
            "ok",
        )
    log_step(
        "Atenção: o volume é o DESEJADO. Exigir entrada reduz o ticket e o aceite "
        "reduz a quantidade — a folga real é menor. O S08 mede isso.",
        "aviso",
    )

    DIR_TABELAS.mkdir(parents=True, exist_ok=True)
    tabela.to_csv(DIR_TABELAS / "s07_faixas.csv", index=False)
    acumulado.to_csv(DIR_TABELAS / "s07_acumulado_aprovacao.csv", index=False)
    log_step(f"Relatórios em {DIR_TABELAS}", "ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
