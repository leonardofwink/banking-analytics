"""S15 · Comparação com o material dos colegas.

Três submissões do mesmo grupo, três resultados muito diferentes de ROI:
nós 11,3%, Marcelo ~12%, Deni 18,4%. Só uma dessas diferenças pode ser
real — o resto é diferença de premissa.

Este script compara o que é comparável:

1. **Formato** — o que o professor cruza. Erro aqui custa o bloco inteiro.
2. **Modelos** — as PDs na Base B, lado a lado.
3. **Políticas** — cada uma rodada no MESMO motor de ROI, o nosso. É a
   única forma de saber se 18,4% é política melhor ou conta diferente.

Rodar::

    .\\scripts\\py.cmd python\\analises\\15_comparar_colegas.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from banking.dados import DIR_BRUTOS, carregar_processada, preparar_base_c
from banking.modelo import treinar_modelo_final
from banking.perda import fator_ead, lgd
from banking.politica import POLITICA_ESCOLHIDA, gerar_politica
from banking.projeto import DIR_TABELAS, log_step
from banking.roi import CENARIOS, aplicar_politica, simular
from banking.score import score_de_pd

DIR_COLEGAS = DIR_BRUTOS / "colegas"

# A política do Deni, lida da tabela dele. Faixas por decil da PD DELE.
# corte em PD = 0,11; taxa de 1,80% a 3,30%; prazo 60m nos scores altos.
DENI = [
    # (score, pd_min, pd_max, taxa_am, prazo, entrada)
    (10, 0.0074, 0.0303, 0.0180, 60, 0.10),
    (9,  0.0303, 0.0401, 0.0205, 60, 0.10),
    (8,  0.0401, 0.0492, 0.0230, 60, 0.10),
    (7,  0.0492, 0.0577, 0.0255, 60, 0.20),
    (6,  0.0577, 0.0678, 0.0280, 48, 0.20),
    (5,  0.0678, 0.0786, 0.0305, 48, 0.20),
    (4,  0.0786, 0.0941, 0.0330, 48, 0.30),
]
DENI_CORTE_PD = 0.11

# A do Marcelo. Aprova scores 2 a 10; taxas de 1,85% a 2,18%.
MARCELO = [
    (10, 0.000, 0.034, 0.0187, 60, 0.05),
    (9,  0.034, 0.039, 0.0187, 60, 0.05),
    (8,  0.039, 0.045, 0.0185, 60, 0.05),
    (7,  0.045, 0.050, 0.0190, 60, 0.05),
    (6,  0.050, 0.057, 0.0191, 60, 0.05),
    (5,  0.057, 0.066, 0.0197, 60, 0.05),
    (4,  0.066, 0.079, 0.0199, 60, 0.10),
    (3,  0.079, 0.100, 0.0207, 48, 0.10),
    (2,  0.100, 0.145, 0.0218, 48, 0.15),
]
MARCELO_CORTE_PD = 0.145
# Regras que o Marcelo aplica ANTES da tabela.
MARCELO_REGRAS = "bureau < 460, restricoes >= 3, parcela > 45% da renda, LTV > 95%"

# Os parâmetros que o Deni usou na perda, em vez das tabelas do professor.
DENI_EAD_FIXO = 15_000.0
DENI_LGD_FIXO = 0.40


def _ler(caminho: Path, **kw) -> pd.DataFrame | None:
    if not caminho.exists():
        log_step(f"não encontrado: {caminho}", "aviso")
        return None
    return pd.read_csv(caminho, **kw)


def main() -> int:
    log_step("S15 · Comparação com os colegas")

    base_a = carregar_processada("A")
    base_b = carregar_processada("B")
    base_c = carregar_processada("C")
    modelo = treinar_modelo_final(base_a)
    escorar = lambda df: modelo.predict_proba(df)[:, 1]

    # ================================================================= 1
    print("\n" + "=" * 78)
    print("1. FORMATO — o que o professor cruza")
    print("=" * 78)

    ids_b = set(base_b["id_contrato"])
    ids_c = set(base_c["id_proposta"])

    for quem in ("deni", "marcelo"):
        print(f"\n--- {quem.upper()} ---")
        for tipo, esperado, ids_ok in (
            ("modelo", ["id_contrato", "pd"], ids_b),
            ("politica", ["id_proposta", "pd", "score_1a10", "decisao",
                          "taxa_am", "prazo_meses", "pct_entrada_minima"], ids_c),
        ):
            caminho = DIR_COLEGAS / quem / f"submissao_{tipo}.csv"
            if not caminho.exists():
                print(f"  {tipo:9}: arquivo ausente")
                continue
            # o separador varia entre eles
            bruto = caminho.read_text(encoding="utf-8", errors="replace")
            sep = ";" if bruto.split("\n")[0].count(";") > bruto.split("\n")[0].count(",") else ","
            d = pd.read_csv(caminho, sep=sep)
            n_esperado = 3000 if tipo == "modelo" else 5000
            col_id = esperado[0]
            cruzam = len(set(d[col_id]) & ids_ok) if col_id in d.columns else 0
            print(f"  {tipo:9}: {len(d):>5,} linhas (esperado {n_esperado:,}) · "
                  f"separador '{sep}' · colunas {list(d.columns)[:4]}")
            print(f"             ids que cruzam com a base: {cruzam:,} de {n_esperado:,}"
                  f"{'  <-- PROBLEMA' if cruzam < n_esperado else '  ok'}")

    # ================================================================= 2
    print("\n" + "=" * 78)
    print("2. MODELOS — as PDs na Base B, lado a lado")
    print("=" * 78)

    nosso_pd = pd.Series(escorar(base_b), index=base_b["id_contrato"], name="nos")
    series = {"nós": nosso_pd}

    for quem, col_id, col_pd, sep in (
        ("deni", "id_contrato", "probabilidade_default_pd", ";"),
        ("marcelo", "id_contrato", "pd", ","),
    ):
        caminho = DIR_COLEGAS / quem / "submissao_modelo.csv"
        if not caminho.exists():
            continue
        d = pd.read_csv(caminho, sep=sep)
        if col_pd not in d.columns or col_id not in d.columns:
            log_step(f"{quem}: colunas inesperadas {list(d.columns)}", "aviso")
            continue
        series[quem] = pd.Series(d[col_pd].to_numpy(), index=d[col_id], name=quem)

    print(f"\n{'':10} {'n':>6} {'PD média':>10} {'mediana':>9} {'mínimo':>8} {'máximo':>8}")
    for nome, s in series.items():
        print(f"{nome:10} {len(s):>6,} {s.mean():>9.2%} {s.median():>8.2%} "
              f"{s.min():>7.2%} {s.max():>7.2%}")

    comuns = set.intersection(*[set(s.index) for s in series.values()])
    print(f"\nids em comum entre as três: {len(comuns):,}")
    if len(comuns) > 100:
        juntas = pd.DataFrame({k: v for k, v in series.items()}).loc[sorted(comuns)]
        print("\ncorrelação de Spearman (ordenação — é o que importa para o score):")
        print(juntas.corr(method="spearman").round(3).to_string())
    else:
        print("  poucos ids em comum: não dá para correlacionar.")

    # ================================================================= 3
    print("\n" + "=" * 78)
    print("3. POLÍTICAS — as três no MESMO motor (o nosso)")
    print("=" * 78)
    print("\nAplicando cada tabela de preços sobre as NOSSAS PDs da base C.")
    print("Assim a diferença que sobra é de política, não de modelo.\n")

    p = preparar_base_c(base_c)
    p["pd"] = escorar(p)
    el = (p["pd"] * fator_ead(p["prazo_meses"], p["ltv"])
          * lgd(p["idade_veiculo_anos"], p["ltv"], p["possui_avalista"]))
    perda_faixa = (pd.DataFrame({"score": score_de_pd(p["pd"]), "el": el})
                   .groupby("score")["el"].mean().to_dict())

    def tabela_de(regras: list, corte_pd: float) -> pd.DataFrame:
        """Traduz a tabela de um colega no formato que o nosso motor espera."""
        linhas = []
        for score in range(10, 0, -1):
            achou = next((r for r in regras if r[0] == score), None)
            if achou and achou[2] <= corte_pd + 1e-9:
                _, _, _, taxa, prazo, entrada = achou
                linhas.append({"score": score, "decisao": "APROVAR", "taxa_am": taxa,
                               "prazo_meses": float(prazo), "pct_entrada_minima": entrada})
            else:
                linhas.append({"score": score, "decisao": "NEGAR", "taxa_am": np.nan,
                               "prazo_meses": np.nan, "pct_entrada_minima": np.nan})
        return pd.DataFrame(linhas)

    def faixas_por_pd(regras: list, corte_pd: float):
        """Mapeia cada proposta na faixa do colega, pelas bordas de PD dele.

        As bordas dos dois nao cobrem a cauda: o Deni para em 9,41% e o
        Marcelo em 14,5%. Quem cai acima da ultima borda vai para o score 1,
        que ambos negam.
        """
        bordas = sorted([(r[0], r[1], r[2]) for r in regras], key=lambda b: b[1])
        pdv = p["pd"].to_numpy()
        score = np.ones(len(pdv), dtype=int)
        for s, lo, hi in bordas:
            score = np.where((pdv > lo) & (pdv <= hi), s, score)
        # abaixo da primeira borda é o melhor score; acima da última, o pior.
        melhor = max(b[0] for b in bordas)
        score = np.where(pdv <= bordas[0][2], melhor, score)
        score = np.where(pdv > bordas[-1][2], 1, score)
        return score

    def aplicar_tabela(propostas: pd.DataFrame, regras_idx: pd.DataFrame,
                       corte_pd: float, escorar_fn) -> pd.DataFrame:
        """Aplica a tabela de um colega usando as faixas DELE.

        Replica ``aplicar_politica``, com uma diferenca que importa: nao dá
        para sobrescrever taxa e entrada depois que ela roda, porque o LTV
        ofertado e o valor financiado ja teriam sido calculados com a entrada
        de outra politica — e a PD re-escorada junto com eles.
        """
        o = propostas.copy()
        for coluna in ("decisao", "taxa_am", "prazo_meses", "pct_entrada_minima"):
            o[coluna] = o["score"].map(regras_idx[coluna])
        o.loc[o["pd"] > corte_pd, "decisao"] = "NEGAR"
        o["aprovada"] = o["decisao"].astype(str).str.upper().eq("APROVAR")

        o["pct_entrada_efetiva"] = np.maximum(
            o["pct_entrada_desejada"].to_numpy(),
            o["pct_entrada_minima"].fillna(0.0).to_numpy(),
        )
        o["entrada_extra"] = o["pct_entrada_efetiva"] - o["pct_entrada_desejada"]
        o["valor_financiado_ofertado"] = o["valor_bem"] * (1.0 - o["pct_entrada_efetiva"])
        o["ltv_ofertado"] = 1.0 - o["pct_entrada_efetiva"]

        ajustada = o.copy()
        ajustada["ltv"] = o["ltv_ofertado"]
        ajustada["valor_financiado"] = o["valor_financiado_ofertado"]
        ajustada["prazo_meses"] = o["prazo_meses"].fillna(o["prazo_desejado_meses"])
        o["pd_ofertada"] = escorar_fn(ajustada)

        faltando = o["aprovada"] & (o["taxa_am"].isna() | o["prazo_meses"].isna())
        if faltando.any():
            raise ValueError(f"{int(faltando.sum())} aprovadas sem taxa ou prazo")
        return o

    resultados = {}

    # a nossa
    nossa = gerar_politica(**POLITICA_ESCOLHIDA, perda_por_faixa=perda_faixa)
    of = aplicar_politica(p, nossa, escorar=escorar)
    resultados["nós (score >= 5)"] = {n: simular(of, n) for n in CENARIOS}

    # as deles
    # O Marcelo declara regras de exclusao aplicadas ANTES da tabela. Compara-lo
    # sem elas seria injusto — e mudaria a conclusao, porque sao elas que
    # seguram a inadimplencia dele.
    exclusao_marcelo = (
        (p["score_bureau"].reset_index(drop=True) < 460)
        | (p["qtd_restricoes_ativas"].reset_index(drop=True) >= 3)
    ).fillna(False).to_numpy()

    for nome, regras, corte, excluir in (
        ("Deni (corte PD 11%)", DENI, DENI_CORTE_PD, None),
        ("Marcelo, sem as regras", MARCELO, MARCELO_CORTE_PD, None),
        ("Marcelo, COM as regras", MARCELO, MARCELO_CORTE_PD, exclusao_marcelo),
    ):
        tab = tabela_de(regras, corte).set_index("score")
        pp = p.copy().reset_index(drop=True)
        pp["score"] = faixas_por_pd(regras, corte)
        of = aplicar_tabela(pp, tab, corte, escorar)
        if excluir is not None:
            of.loc[excluir, "decisao"] = "NEGAR"
            of.loc[excluir, "aprovada"] = False
        resultados[nome] = {n: simular(of, n) for n in CENARIOS}

    print(f"{'política':<26} {'aprov':>7} {'ROI':>8} {'vol central':>13} "
          f"{'vol pior':>10} {'inad pior':>10} {'aceite':>8}  viável")
    print("-" * 96)
    for nome, res in resultados.items():
        c = res["central"]
        vol_pior = min(r.volume_originado for r in res.values())
        inad_pior = max(r.inadimplencia for r in res.values())
        viola = [v for r in res.values() for v in r.violacoes]
        print(f"{nome:<26} {c.taxa_aprovacao:>6.1%} {c.roi_anual:>7.2%} "
              f"R$ {c.volume_originado/1e6:>8.1f} mi R$ {vol_pior/1e6:>5.1f} mi "
              f"{inad_pior:>9.2%} {c.taxa_aceite_media:>7.1%}  {'sim' if not viola else 'NÃO'}")
        if viola:
            print(f"{'':26}   viola: {sorted(set(viola))}")

    # ================================================================= 4
    print("\n" + "=" * 78)
    print("4. DE ONDE VEM O ROI DE 18,4% DO DENI")
    print("=" * 78)

    aprovadas = p[score_de_pd(p["pd"]) >= 5]
    ead_real = (fator_ead(aprovadas["prazo_meses"], aprovadas["ltv"])
                * aprovadas["valor_financiado"]).mean()
    lgd_real = lgd(aprovadas["idade_veiculo_anos"], aprovadas["ltv"],
                   aprovadas["possui_avalista"]).mean()

    print(f"\n{'':32} {'Deni':>14} {'tabelas do professor':>22}")
    print(f"{'EAD por contrato':<32} R$ {DENI_EAD_FIXO:>10,.0f} R$ {ead_real:>19,.0f}")
    print(f"{'LGD':<32} {DENI_LGD_FIXO:>13.0%} {lgd_real:>21.1%}")
    perda_deni = DENI_EAD_FIXO * DENI_LGD_FIXO
    perda_real = ead_real * lgd_real
    print(f"{'perda por unidade de PD':<32} R$ {perda_deni:>10,.0f} R$ {perda_real:>19,.0f}")
    print(f"\n  A perda dele é {perda_real/perda_deni:.1f}x menor que a dos parâmetros do desafio.")
    print(f"  EAD fixo de R$ 15.000 contra R$ {ead_real:,.0f} reais, e LGD de 40% contra {lgd_real:.0%}.")

    # ================================================================= 5
    print("\n" + "=" * 78)
    print("5. E SE NÓS USÁSSEMOS OS PARÂMETROS DELE?")
    print("=" * 78)
    print("\nMesma política nossa, só trocando EAD e LGD pelos números do Deni.\n")

    of_nosso = aplicar_politica(p, nossa, escorar=escorar)
    r_real = simular(of_nosso, "central")

    ap = of_nosso[of_nosso["aprovada"]]
    juros = None
    try:
        from banking.price import juros_totais
        principal = ap["valor_financiado_ofertado"].to_numpy()
        juros = juros_totais(principal, ap["taxa_am"].to_numpy(),
                             ap["prazo_meses"].to_numpy())
        pd_ap = ap["pd_ofertada"].to_numpy()
        prazo_anos = ap["prazo_meses"].to_numpy().mean() / 12.0

        perda_com_deni = pd_ap * DENI_EAD_FIXO * DENI_LGD_FIXO
        perda_com_real = pd_ap * fator_ead(ap["prazo_meses"], ap["ltv_ofertado"]) * principal * \
            lgd(ap["idade_veiculo_anos"], ap["ltv_ofertado"], ap["possui_avalista"])

        for rotulo, perda_v in (("parâmetros do professor", perda_com_real),
                                ("parâmetros do Deni", perda_com_deni)):
            roi = (juros.sum() - perda_v.sum()) / principal.sum() / prazo_anos
            print(f"  {rotulo:<28}: ROI {roi:>6.2%} · perda total R$ {perda_v.sum()/1e6:>5.1f} mi")
        print(f"\n  Mesma carteira, mesmas taxas. A diferença é só a conta da perda.")
    except Exception as erro:  # pragma: no cover - diagnóstico
        log_step(f"não deu para isolar os juros: {erro}", "aviso")

    # ================================================================= saída
    destino = DIR_TABELAS / "s15_comparacao_colegas.csv"
    pd.DataFrame([
        {"quem": nome,
         "roi_central": res["central"].roi_anual,
         "aprovacao": res["central"].taxa_aprovacao,
         "volume_central": res["central"].volume_originado,
         "volume_pior": min(r.volume_originado for r in res.values()),
         "inadimplencia_pior": max(r.inadimplencia for r in res.values()),
         "aceite_medio": res["central"].taxa_aceite_media,
         "viavel": not any(r.violacoes for r in res.values())}
        for nome, res in resultados.items()
    ]).to_csv(destino, index=False)
    log_step(f"tabela gravada: {destino}", "ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
