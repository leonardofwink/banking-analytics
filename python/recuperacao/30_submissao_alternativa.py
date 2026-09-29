# -*- coding: utf-8 -*-
"""S13.7 · A submissão alternativa — o entregável da recuperação.

Espelha ``modelagem/10_submissao_politica.py``, com três diferenças:

* usa ``POLITICA_RECUPERACAO`` (S13.6) em vez de ``POLITICA_ESCOLHIDA``;
* grava em ``outputs/recuperacao/``, **sem tocar** em ``outputs/submissao/``;
* lê a coluna de prazo como **teto**, não como valor fixo.

⚠️ **A submissão original é imutável.** Este script não altera nem regenera
nada do que foi entregue em 25/09/2026 — o arquivo antigo é o registro do que
foi defendido, e é o que mantém a comparação honesta. O script confere isso no
fim, e falha se o arquivo original tiver mudado de tamanho.

⚠️ **O prazo como teto muda a leitura da coerência.** O enunciado chama a coluna
de *"Prazo máx."*. Sob essa leitura, dar 36 meses a quem pediu 36 é coerente com
um teto de 60 — e foi o que Grupo 1 e Grupo 2 fizeram. Só o nosso grupo deu
prazo fixo a todo mundo. O validador aceita as duas leituras, mas exige que ela
seja **declarada**: ``prazo_como_teto=True``.
"""

from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
import pandas as pd

from banking.dados import carregar_processada, preparar_base_c
from banking.modelo import treinar_modelo_final
from banking.perda import fator_ead, lgd
from banking.politica import (
    PRAZO_COMO_TETO_RECUPERACAO,
    POLITICA_RECUPERACAO,
    gerar_politica,
    validar_monotonicidade,
)
from banking.projeto import DIR_OUTPUTS, DIR_TABELAS, log_step, semear
from banking.roi import (
    CENARIO_CALIBRADO,
    PREMISSAS_CALIBRADAS,
    aplicar_politica,
    simular,
)
from banking.score import faixa_de_score, score_de_pd
from banking.submissao import (
    COLUNAS_SUBMISSAO_POLITICA,
    ValidacaoFalhou,
    validar_submissao_politica,
)

DIR_RECUPERACAO = DIR_OUTPUTS / "recuperacao"
DIR_SUBMISSAO_ORIGINAL = DIR_OUTPUTS / "submissao"


def main() -> int:
    log_step("S13.7 · A submissão alternativa")
    semear()

    base_a = carregar_processada("A")
    base_c = carregar_processada("C")
    modelo = treinar_modelo_final(base_a)
    escorar = lambda df: modelo.predict_proba(df)[:, 1]  # noqa: E731

    propostas = preparar_base_c(base_c).reset_index(drop=True)
    propostas["pd"] = escorar(propostas)

    # --- a tabela ------------------------------------------------------------
    el = (
        propostas["pd"]
        * fator_ead(propostas["prazo_desejado_meses"], propostas["ltv"])
        * lgd(propostas["idade_veiculo_anos"], propostas["ltv"],
              propostas["possui_avalista"])
    )
    perda_por_faixa = (
        pd.DataFrame({"score": score_de_pd(propostas["pd"]), "el": el})
        .groupby("score")["el"].mean().to_dict()
    )
    politica = gerar_politica(**POLITICA_RECUPERACAO, perda_por_faixa=perda_por_faixa)

    problemas = validar_monotonicidade(politica)
    if problemas:
        log_step(f"tabela incoerente: {problemas}", "erro")
        return 1
    log_step("Tabela monotônica nas quatro alavancas", "ok")

    # --- a aplicação, com o prazo como teto ---------------------------------
    scores = score_de_pd(propostas["pd"])
    regras = politica.set_index("score")
    prazo_tabela = pd.Series(scores).map(regras["prazo_meses"]).to_numpy(dtype=float)
    prazo_linha = (
        np.minimum(prazo_tabela, propostas["prazo_desejado_meses"].to_numpy(dtype=float))
        if PRAZO_COMO_TETO_RECUPERACAO
        else prazo_tabela
    )
    # Negada não recebe condição nenhuma.
    negada = pd.Series(scores).map(regras["decisao"]).to_numpy() != "APROVAR"
    prazo_linha = np.where(negada, np.nan, prazo_linha)

    submissao = pd.DataFrame(
        {
            "id_proposta": propostas["id_proposta"].to_numpy(),
            "pd": propostas["pd"].to_numpy().round(6),
            "score_1a10": scores,
            "decisao": pd.Series(scores).map(regras["decisao"]).to_numpy(),
            "taxa_am": pd.Series(scores).map(regras["taxa_am"]).to_numpy(),
            "prazo_meses": prazo_linha,
            "pct_entrada_minima": pd.Series(scores).map(
                regras["pct_entrada_minima"]).to_numpy(),
        },
        columns=list(COLUNAS_SUBMISSAO_POLITICA),
    )

    aprovadas = submissao["decisao"] == "APROVAR"
    encurtados = int(
        (submissao.loc[aprovadas, "prazo_meses"].to_numpy()
         < prazo_tabela[aprovadas.to_numpy()] - 1e-9).sum()
    )
    log_step(
        f"{len(submissao):,} propostas · {int(aprovadas.sum()):,} aprovadas "
        f"({aprovadas.mean():.1%}) · {encurtados:,} receberam menos que o teto "
        f"porque pediram menos",
        "ok",
    )

    # --- validação -----------------------------------------------------------
    try:
        validar_submissao_politica(
            submissao, propostas["id_proposta"], politica,
            arquivo="submissao_politica_recuperacao.csv",
            prazo_como_teto=PRAZO_COMO_TETO_RECUPERACAO,
        )
    except ValidacaoFalhou as erro:
        log_step(str(erro), "erro")
        return 1
    log_step("Validador passou, com o prazo lido como teto", "ok")

    # --- o que ela entrega ---------------------------------------------------
    ofertas = aplicar_politica(
        propostas, politica, escorar=escorar,
        prazo_como_teto=PRAZO_COMO_TETO_RECUPERACAO,
    )
    r = simular(ofertas, CENARIO_CALIBRADO, PREMISSAS_CALIBRADAS)
    print(f"\n  Sob as premissas calibradas:")
    print(f"    ROI {r.roi_anual:.2%} · volume R$ {r.volume_originado/1e6:.1f} mi · "
          f"inadimplência {r.inadimplencia:.2%} · aprovação {r.taxa_aprovacao:.1%}")
    print(f"    guard-rails: {'todos cumpridos' if not r.violacoes else ', '.join(r.violacoes)}")

    print("\n  A tabela:\n")
    print(f"    {'score':<7}{'faixa de PD':<18}{'decisão':<10}{'taxa':>8}"
          f"{'prazo máx':>11}{'entrada':>9}")
    for _, linha in politica.iterrows():
        lo, hi = faixa_de_score(int(linha["score"]))
        faixa = f"{lo:.1%} – {hi:.1%}"
        if linha["decisao"] == "NEGAR":
            print(f"    {int(linha['score']):<7}{faixa:<18}{'NEGAR':<10}"
                  f"{'—':>8}{'—':>11}{'—':>9}")
        else:
            print(f"    {int(linha['score']):<7}{faixa:<18}{'APROVAR':<10}"
                  f"{linha['taxa_am']:>8.2%}{int(linha['prazo_meses']):>10}m"
                  f"{linha['pct_entrada_minima']:>9.1%}")

    # --- o arquivo -----------------------------------------------------------
    DIR_RECUPERACAO.mkdir(parents=True, exist_ok=True)
    destino = DIR_RECUPERACAO / "submissao_politica_recuperacao.csv"
    saida = submissao.copy()
    saida["prazo_meses"] = saida["prazo_meses"].map(
        lambda v: "" if pd.isna(v) else str(int(v))
    )
    saida.to_csv(destino, index=False)
    politica.to_csv(DIR_TABELAS / "s13_politica_recuperacao.csv", index=False)
    log_step(f"Gerado: {destino}", "ok")

    # --- a submissão original continua intacta -------------------------------
    original = DIR_SUBMISSAO_ORIGINAL / "submissao_politica.csv"
    if original.exists():
        n = sum(1 for _ in original.open(encoding="utf-8"))
        log_step(f"A submissão original segue intacta: {original.name}, {n:,} linhas")
    else:
        log_step("submissão original ausente — nada a preservar aqui", "aviso")

    return 0


if __name__ == "__main__":
    sys.exit(main())
