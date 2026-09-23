"""S10 · Gera o `submissao_politica.csv` — entregável 2.

Aplica a política escolhida no S09 às 5.000 propostas da base C.

⚠️ **A PD reportada é a do PEDIDO**, não a da oferta. Exigir entrada reduz o
LTV e, com ele, a PD — mas foi a PD do pedido que gerou o score, que gerou a
decisão. Reportar a PD menor ao lado do score que veio da maior deixaria a
dupla ``pd`` / ``score_1a10`` inconsistente, e essa coerência é o que vale 10
pontos da rubrica. Ver ``docs/specs/S10_SUBMISSAO_POLITICA.md``.

Rodar::

    .\\scripts\\py.cmd python\\modelagem\\10_submissao_politica.py
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from banking.dados import carregar_processada, preparar_base_c
from banking.modelo import treinar_modelo_final
from banking.perda import fator_ead, lgd
from banking.politica import POLITICA_ESCOLHIDA, gerar_politica, validar_monotonicidade
from banking.projeto import DIR_OUTPUTS, DIR_TABELAS, log_step
from banking.roi import CENARIOS, aplicar_politica, simular
from banking.score import score_de_pd
from banking.submissao import (
    COLUNAS_SUBMISSAO_POLITICA,
    ValidacaoFalhou,
    validar_submissao_politica,
)

DIR_SUBMISSAO = DIR_OUTPUTS / "submissao"


def main() -> int:
    log_step("S10 · Aplicação da política à base C")

    try:
        base_a = carregar_processada("A")
        base_c = carregar_processada("C")
    except FileNotFoundError as erro:
        log_step(str(erro), "erro")
        return 1

    modelo = treinar_modelo_final(base_a)
    escorar = lambda df: modelo.predict_proba(df)[:, 1]

    propostas = preparar_base_c(base_c)
    propostas["pd"] = escorar(propostas)  # PD do PEDIDO — é ela que vai no arquivo

    # --- a tabela do S09 ----------------------------------------------------
    el = (
        propostas["pd"]
        * fator_ead(propostas["prazo_meses"], propostas["ltv"])
        * lgd(propostas["idade_veiculo_anos"], propostas["ltv"], propostas["possui_avalista"])
    )
    perda_por_faixa = (
        pd.DataFrame({"score": score_de_pd(propostas["pd"]), "el": el})
        .groupby("score")["el"].mean().to_dict()
    )
    politica = gerar_politica(**POLITICA_ESCOLHIDA, perda_por_faixa=perda_por_faixa)

    problemas = validar_monotonicidade(politica)
    if problemas:
        log_step(f"tabela incoerente: {problemas}", "erro")
        return 1
    log_step("Tabela de política monotônica nas quatro alavancas", "ok")

    # --- S10.2 · aplicação --------------------------------------------------
    scores = score_de_pd(propostas["pd"])
    regras = politica.set_index("score")

    submissao = pd.DataFrame(
        {
            "id_proposta": propostas["id_proposta"].to_numpy(),
            "pd": propostas["pd"].to_numpy().round(6),
            "score_1a10": scores,
            "decisao": pd.Series(scores).map(regras["decisao"]).to_numpy(),
            "taxa_am": pd.Series(scores).map(regras["taxa_am"]).to_numpy(),
            "prazo_meses": pd.Series(scores).map(regras["prazo_meses"]).to_numpy(),
            "pct_entrada_minima": pd.Series(scores).map(regras["pct_entrada_minima"]).to_numpy(),
        },
        columns=list(COLUNAS_SUBMISSAO_POLITICA),
    )

    aprovadas = submissao["decisao"] == "APROVAR"
    log_step(
        f"{len(submissao):,} propostas · {int(aprovadas.sum()):,} aprovadas "
        f"({aprovadas.mean():.1%}) · {int((~aprovadas).sum()):,} negadas",
        "ok",
    )

    print("\n--- Distribuição por faixa ---")
    resumo = (
        submissao.groupby(["score_1a10", "decisao"])
        .agg(n=("pd", "size"), pd_media=("pd", "mean"), taxa=("taxa_am", "first"))
        .reset_index()
        .sort_values("score_1a10", ascending=False)
    )
    print(
        resumo.assign(
            pct=lambda d: (d.n / len(submissao)).map("{:.1%}".format),
            pd_media=lambda d: d.pd_media.map("{:.2%}".format),
            taxa=lambda d: d.taxa.map(lambda v: "—" if pd.isna(v) else f"{v:.3%}"),
        ).to_string(index=False)
    )

    # --- S10.3 · validação --------------------------------------------------
    try:
        validar_submissao_politica(submissao, propostas["id_proposta"], politica)
    except ValidacaoFalhou as erro:
        log_step(str(erro), "erro")
        return 1
    log_step("Validador passou: ids, faixas, coerência entre pd e score, e entre condições e tabela", "ok")

    # --- S10.4 · o arquivo --------------------------------------------------
    DIR_SUBMISSAO.mkdir(parents=True, exist_ok=True)
    destino = DIR_SUBMISSAO / "submissao_politica.csv"
    # prazo como inteiro no CSV, mas pandas usa float quando há NaN. Formatar
    # na escrita evita "48.0" no arquivo — o exemplo do professor mostra "60".
    saida = submissao.copy()
    saida["prazo_meses"] = saida["prazo_meses"].map(lambda v: "" if pd.isna(v) else str(int(v)))
    saida.to_csv(destino, index=False)
    log_step(f"ENTREGÁVEL 2 gerado: {destino}", "ok")

    print("\n--- Primeiras linhas ---")
    print(saida.head(8).to_string(index=False))

    # --- projeção, para a defesa --------------------------------------------
    ofertas = aplicar_politica(propostas, politica, escorar=escorar)
    print("\n--- Projeção nos três cenários ---")
    print(
        pd.DataFrame([simular(ofertas, n).como_linha() for n in CENARIOS])
        .assign(
            roi_anual=lambda d: d.roi_anual.map("{:.1%}".format),
            inadimplencia=lambda d: d.inadimplencia.map("{:.2%}".format),
            volume_mi=lambda d: d.volume_mi.map("R$ {:.1f} mi".format),
            aprovacao=lambda d: d.aprovacao.map("{:.1%}".format),
            aceite_medio=lambda d: d.aceite_medio.map("{:.1%}".format),
            contratos=lambda d: d.contratos.map("{:.0f}".format),
            prazo_anos=lambda d: d.prazo_anos.map("{:.2f}".format),
        )
        .to_string(index=False)
    )

    politica.to_csv(DIR_TABELAS / "s10_politica_submetida.csv", index=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
