"""S23 · Pente fino na apresentação do Renato.

Ele não subiu CSVs — só a apresentação. Então a conferência tem duas partes:

1. **As afirmações sobre as bases**, que dá para medir direto.
2. **A política dele**, reconstruída da tabela do slide 8 e rodada no motor
   do Léo, para comparar com a mesma régua.

Rodar::

    .\\scripts\\py.cmd python\\analises\\23_conferir_renato.py
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from banking.dados import carregar_bruto, carregar_processada, preparar_base_c
from banking.metricas import psi
from banking.modelo import treinar_modelo_final
from banking.perda import fator_ead, lgd
from banking.politica import POLITICA_ESCOLHIDA, gerar_politica
from banking.dados import carregar_parametros_ead_lgd
from banking.price import juros_pagos_ate, juros_totais, parcela
from banking.projeto import log_step
from banking.roi import CENARIOS, aplicar_politica, simular
from banking.score import score_de_pd

# A tabela do slide 8. Faixas de PD, taxa, prazo e entrada por score.
RENATO = {
    10: (0.000, 0.033, 0.018, 60, 0.00),
    9:  (0.033, 0.039, 0.019, 60, 0.00),
    8:  (0.039, 0.044, 0.020, 60, 0.00),
    7:  (0.044, 0.049, 0.021, 60, 0.00),
    6:  (0.049, 0.056, 0.022, 48, 0.00),
    5:  (0.056, 0.066, 0.023, 48, 0.00),
    4:  (0.066, 0.080, 0.024, 48, 0.10),
}
CORTE = 0.080


def selo(b: bool, perto: bool = False) -> str:
    return "OK" if b else ("~ " if perto else "!!")


def conferir(rotulo, afirmado, medido, bate, perto=False):
    print(f"  {selo(bate, perto)} {rotulo:<44} diz {afirmado:>15} · achei {medido:>15}")


def main() -> int:
    log_step("S23 · Pente fino na apresentação do Renato")

    base_a = carregar_processada("A")
    base_b = carregar_processada("B")
    base_c = carregar_processada("C")
    bruta_a = carregar_bruto("A")
    modelo = treinar_modelo_final(base_a)
    escorar = lambda df: modelo.predict_proba(df)[:, 1]

    p = preparar_base_c(base_c).reset_index(drop=True)
    p["pd"] = escorar(p)
    pd_a = escorar(base_a)
    pd_b = escorar(base_b)

    # =================================================== 1
    print("\n" + "=" * 86)
    print("1. AS AFIRMAÇÕES SOBRE AS BASES")
    print("=" * 86 + "\n")

    inad_a = bruta_a["default_90_12"].mean()
    conferir("«inadimplência chegou a 8,3%» (Base A)", "8,3%", f"{inad_a:.1%}",
             abs(inad_a - 0.083) < 0.003)

    ltv_medio = bruta_a["ltv"].mean()
    conferir("«LTV médio da carteira é 74%»", "74%", f"{ltv_medio:.0%}",
             abs(ltv_medio - 0.74) < 0.015, abs(ltv_medio - 0.74) < 0.04)

    lgd_media = lgd(base_a["idade_veiculo_anos"], base_a["ltv"],
                    base_a["possui_avalista"]).mean()
    conferir("«perde cerca de 70% do valor exposto»", "~70%", f"{lgd_media:.1%}",
             abs(lgd_media - 0.70) < 0.03)

    conferir("«PD média na Base A de 8,4%»", "8,4%", f"{pd_a.mean():.1%}",
             abs(pd_a.mean() - 0.084) < 0.005)
    conferir("«PD média na Base C de 19,4%»", "19,4%", f"{p['pd'].mean():.1%}",
             abs(p["pd"].mean() - 0.194) < 0.01, abs(p["pd"].mean() - 0.194) < 0.05)

    # PSI do score, que é o que ele chama de "estabilidade"
    psi_c = psi(score_de_pd(pd_a), score_de_pd(p["pd"].to_numpy()))
    psi_b = psi(score_de_pd(pd_a), score_de_pd(pd_b))
    conferir("«estabilidade 0,44 na Base C»", "0,44", f"{psi_c:.2f}",
             abs(psi_c - 0.44) < 0.06, abs(psi_c - 0.44) < 0.2)
    conferir("«estabilidade 0,02 na Base B»", "0,02", f"{psi_b:.2f}",
             abs(psi_b - 0.02) < 0.02, abs(psi_b - 0.02) < 0.06)

    # fora do domínio de treino
    lim_bureau = base_a["score_bureau"].min()
    lim_restr = base_a["qtd_restricoes_ativas"].max()
    fora = ((p["score_bureau"] < lim_bureau) | (p["qtd_restricoes_ativas"] > lim_restr))
    conferir("«36% (1.800) fora do domínio do treino»", "36% / 1.800",
             f"{fora.mean():.1%} / {int(fora.sum()):,}",
             abs(int(fora.sum()) - 1800) <= 60, abs(int(fora.sum()) - 1800) <= 250)

    nulos = {c: bruta_a[c].isna().mean() for c in
             ("score_bureau", "renda_mensal_declarada", "tempo_emprego_meses")}
    conferir("«ausentes: bureau 3%, renda 8%, emprego 12%»", "3 / 8 / 12%",
             " / ".join(f"{v:.0%}" for v in nulos.values()),
             abs(nulos["score_bureau"] - 0.03) < 0.01
             and abs(nulos["renda_mensal_declarada"] - 0.08) < 0.01
             and abs(nulos["tempo_emprego_meses"] - 0.12) < 0.015)

    # =================================================== 2
    print("\n" + "=" * 86)
    print("2. O EXEMPLO DO SLIDE 9 — um contrato, passo a passo")
    print("=" * 86)
    print("\n  R$ 30.000 · 48 meses · veículo de 3 a 5 anos · LTV 80% · score 5\n")

    P, n, i_taxa = 30_000.0, 48.0, 0.023
    ead_fator = float(fator_ead(np.array([n]), np.array([0.80]))[0])
    lgd_ex = float(lgd(np.array([4.0]), np.array([0.80]), np.array(["Não"]))[0])
    conferir("fator de EAD", "1,032", f"{ead_fator:.3f}", abs(ead_fator - 1.032) < 0.002)
    conferir("EAD em reais", "R$ 30.960", f"R$ {P * ead_fator:,.0f}",
             abs(P * ead_fator - 30960) < 80)
    conferir("LGD da célula", "70,4%", f"{lgd_ex:.1%}", abs(lgd_ex - 0.704) < 0.01)

    pd_ex = 0.061
    perda_ex = pd_ex * P * ead_fator * lgd_ex
    conferir("perda esperada", "R$ 1.322", f"R$ {perda_ex:,.0f}", abs(perda_ex - 1322) < 40)
    parc = float(parcela(np.array([P]), np.array([i_taxa]), np.array([n]))[0])
    conferir("parcela mensal", "R$ 1.039", f"R$ {parc:,.0f}", abs(parc - 1039) < 15)
    # ⚠️ Ele declara no próprio slide que quem quebra paga só até o mês do
    # calote. Os "juros esperados" dele já são ponderados pela PD — comparar
    # com os juros integrais seria comparar coisas diferentes.
    integrais = float(juros_totais(np.array([P]), np.array([i_taxa]), np.array([n]))[0])
    dist = carregar_parametros_ead_lgd().dist_mes_default
    ate_quebra = sum(
        float(f) * float(juros_pagos_ate(np.array([P]), np.array([i_taxa]),
                                         np.array([n]), np.array([min(float(m), n)]))[0])
        for m, f in dist.items()
    )
    juros_ex = (1 - pd_ex) * integrais + pd_ex * ate_quebra
    print(f"     (juros integrais seriam R$ {integrais:,.0f}; ponderados pela PD, "
          f"R$ {juros_ex:,.0f})")
    conferir("juros esperados, com quebra no meio", "R$ 18.930", f"R$ {juros_ex:,.0f}",
             abs(juros_ex - 18930) < 250)
    roi_ex = (juros_ex - perda_ex) / P / (n / 12)
    conferir("ROI do exemplo", "14,7%", f"{roi_ex:.1%}", abs(roi_ex - 0.147) < 0.008)

    # =================================================== 3
    print("\n" + "=" * 86)
    print("3. A POLÍTICA DELE NO MOTOR DO LÉO")
    print("=" * 86)

    bordas = sorted(((s, v[0], v[1]) for s, v in RENATO.items()), key=lambda b: b[1])
    pdv = p["pd"].to_numpy()
    sc = np.ones(len(p), dtype=int)
    for s_, lo, hi in bordas:
        sc = np.where((pdv > lo) & (pdv <= hi), s_, sc)
    sc = np.where(pdv <= bordas[0][2], 10, sc)
    sc = np.where(pdv > bordas[-1][2], 1, sc)

    o = p.copy()
    o["score"] = sc
    o["taxa_am"] = [RENATO.get(s, (0,) * 5)[2] if s in RENATO else np.nan for s in sc]
    o["prazo_meses"] = [float(RENATO[s][3]) if s in RENATO else np.nan for s in sc]
    o["pct_entrada_minima"] = [RENATO[s][4] if s in RENATO else np.nan for s in sc]
    o["aprovada"] = (o["pd"] <= CORTE) & o["taxa_am"].notna()
    o["decisao"] = np.where(o["aprovada"], "APROVAR", "NEGAR")
    o["pct_entrada_efetiva"] = np.maximum(o["pct_entrada_desejada"].to_numpy(),
                                          o["pct_entrada_minima"].fillna(0).to_numpy())
    o["entrada_extra"] = o["pct_entrada_efetiva"] - o["pct_entrada_desejada"]
    o["valor_financiado_ofertado"] = o["valor_bem"] * (1 - o["pct_entrada_efetiva"])
    o["ltv_ofertado"] = 1 - o["pct_entrada_efetiva"]
    aj = o.copy()
    aj["ltv"] = o["ltv_ofertado"]
    aj["valor_financiado"] = o["valor_financiado_ofertado"]
    aj["prazo_meses"] = o["prazo_meses"].fillna(o["prazo_desejado_meses"])
    o["pd_ofertada"] = escorar(aj)

    print(f"\n  aprovação com as PDs do Léo: {o['aprovada'].mean():.1%}  "
          f"(ele reporta 45,2% com as dele)\n")
    print(f"  {'cenário':<12} {'ROI':>8} {'volume':>12} {'inadimpl.':>11} {'aceite':>8}  guard-rails")
    print("  " + "-" * 74)
    for nome in ("otimista", "central", "pessimista"):
        r = simular(o, nome)
        viola = sorted({v.split()[0] for v in r.violacoes})
        print(f"  {nome:<12} {r.roi_anual:>7.2%} R$ {r.volume_originado/1e6:>7.1f} mi "
              f"{r.inadimplencia:>10.2%} {r.taxa_aceite_media:>7.1%}  "
              f"{'todos' if not viola else 'viola ' + ','.join(viola)}")

    # a do Léo, na mesma régua
    el = (p["pd"] * fator_ead(p["prazo_meses"], p["ltv"])
          * lgd(p["idade_veiculo_anos"], p["ltv"], p["possui_avalista"]))
    perda_faixa = (pd.DataFrame({"score": score_de_pd(p["pd"]), "el": el})
                   .groupby("score")["el"].mean().to_dict())
    pol_leo = gerar_politica(**POLITICA_ESCOLHIDA, perda_por_faixa=perda_faixa)
    of_leo = aplicar_politica(p, pol_leo, escorar=escorar)
    print("\n  para comparar, a política do Léo:")
    for nome in ("otimista", "central", "pessimista"):
        r = simular(of_leo, nome)
        viola = sorted({v.split()[0] for v in r.violacoes})
        print(f"  {nome:<12} {r.roi_anual:>7.2%} R$ {r.volume_originado/1e6:>7.1f} mi "
              f"{r.inadimplencia:>10.2%} {r.taxa_aceite_media:>7.1%}  "
              f"{'todos' if not viola else 'viola ' + ','.join(viola)}")

    # =================================================== 4
    print("\n" + "=" * 86)
    print("4. O TESTE QUE ELE TEM E O LÉO NÃO: PD +30%")
    print("=" * 86)
    print("\n  Ele reporta inadimplência de 7,0% com o risco 30% acima do previsto.")
    print("  Aplicando o mesmo estresse às duas políticas, no cenário central:\n")

    for rotulo, ofertas in (("Renato", o), ("Léo", of_leo)):
        estressada = ofertas.copy()
        estressada["pd_ofertada"] = np.clip(estressada["pd_ofertada"] * 1.30, 0, 1)
        base_r = simular(ofertas, "central")
        est_r = simular(estressada, "central")
        viola = sorted({v.split()[0] for v in est_r.violacoes})
        print(f"  {rotulo:<8} inadimplência {base_r.inadimplencia:>6.2%} -> "
              f"{est_r.inadimplencia:>6.2%} · ROI {base_r.roi_anual:>6.2%} -> "
              f"{est_r.roi_anual:>6.2%} · "
              f"{'aguenta' if not viola else 'VIOLA ' + ','.join(viola)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
