"""Quem aprovamos e quem negamos — o perfil dos dois grupos."""

import numpy as np
import pandas as pd

from banking.dados import carregar_processada, preparar_base_c
from banking.modelo import treinar_modelo_final
from banking.perda import fator_ead, lgd
from banking.politica import POLITICA_ESCOLHIDA, gerar_politica
from banking.score import score_de_pd

base_a = carregar_processada("A")
base_c = carregar_processada("C")
modelo = treinar_modelo_final(base_a)
p = preparar_base_c(base_c)
p["pd"] = modelo.predict_proba(p)[:, 1]
p["score"] = score_de_pd(p["pd"])

el = (p["pd"] * fator_ead(p["prazo_meses"], p["ltv"])
      * lgd(p["idade_veiculo_anos"], p["ltv"], p["possui_avalista"]))
perda = (pd.DataFrame({"score": p["score"], "el": el})
         .groupby("score")["el"].mean().to_dict())
politica = gerar_politica(**POLITICA_ESCOLHIDA, perda_por_faixa=perda)
regras = politica.set_index("score")
p["decisao"] = p["score"].map(regras["decisao"])
ap = p["decisao"].eq("APROVAR")

# Fora do dominio de treino: os limites reais da base A.
A = carregar_processada("A")
lim_bureau = A["score_bureau"].min()
lim_restr = A["qtd_restricoes_ativas"].max()
print(f"Limites da base A: bureau >= {lim_bureau:.0f}, restricoes <= {lim_restr:.0f}")
fora = (p["score_bureau"] < lim_bureau) | (p["qtd_restricoes_ativas"] > lim_restr)

print("\n" + "=" * 72)
print("PERFIL: APROVADOS (score >= 5) vs NEGADOS (score 1 a 4)")
print("=" * 72)

def linha(rotulo, fn, fmt="{:.1f}"):
    a, n = fn(p[ap]), fn(p[~ap])
    print(f"{rotulo:<32} {fmt.format(a):>14} {fmt.format(n):>14}")

print(f"{'indicador':<32} {'APROVADOS':>14} {'NEGADOS':>14}")
print("-" * 72)
print(f"{'Propostas':<32} {f'{int(ap.sum()):,} ({ap.mean():.0%})':>14} "
      f"{f'{int((~ap).sum()):,} ({(~ap).mean():.0%})':>14}")
linha("PD media", lambda d: d["pd"].mean(), "{:.1%}")
linha("Score de bureau medio", lambda d: d["score_bureau"].mean(), "{:.0f}")
linha("Renda mediana", lambda d: d["renda_mensal_declarada"].median(), "R$ {:,.0f}")
linha("Com restricao ativa", lambda d: (d["qtd_restricoes_ativas"] > 0).mean(), "{:.0%}")
linha("Restricoes (media)", lambda d: d["qtd_restricoes_ativas"].mean(), "{:.2f}")
linha("LTV desejado medio", lambda d: d["ltv"].mean(), "{:.0%}")
linha("Idade media do cliente", lambda d: d["idade_cliente"].mean(), "{:.0f} anos")
linha("Idade media do veiculo", lambda d: d["idade_veiculo_anos"].mean(), "{:.1f} anos")
linha("Possui avalista", lambda d: d["possui_avalista"].astype(str).str.upper().isin(["SIM","S","TRUE","1"]).mean(), "{:.0%}")
linha("Consultas ao bureau em 3m", lambda d: d["qtd_consultas_bureau_3m"].mean(), "{:.1f}")
linha("Tempo de emprego (meses)", lambda d: d["tempo_emprego_meses"].median(), "{:.0f}")
linha("Valor financiado (mediana)", lambda d: d["valor_financiado_desejado"].median(), "R$ {:,.0f}")

a_fora = fora[ap].mean(); n_fora = fora[~ap].mean()
print(f"{'Fora do dominio de treino':<32} {a_fora:>13.0%} {n_fora:>13.0%}")

print("\n--- ocupacao ---")
print(pd.crosstab(p["ocupacao"], ap.map({True: "APROVADO", False: "NEGADO"}), normalize="columns")
      .mul(100).round(1).to_string())

print("\n--- canal de originacao ---")
print(pd.crosstab(p["canal_originacao"], ap.map({True: "APROVADO", False: "NEGADO"}), normalize="columns")
      .mul(100).round(1).to_string())

print("\n" + "=" * 72)
print("AS PERGUNTAS QUE A BANCA FAZ")
print("=" * 72)

faixa4 = p["score"] == 4
print(f"\n1) Por que negar o score 4?")
print(f"   {int(faixa4.sum()):,} propostas · PD media {p.loc[faixa4,'pd'].mean():.1%} "
      f"(faixa: 13,0% a 18,0%)")
print(f"   perda esperada da faixa: {perda[4]:.2%}")
taxa_necessaria = perda[4]
print(f"   para cobrir so a perda, a taxa teria de subir muito acima do mercado (1,59%)")

print(f"\n2) Os negados sao so o perfil fora do dominio?")
neg_fora = (fora & ~ap).sum(); neg_total = (~ap).sum()
print(f"   NAO: {neg_fora/neg_total:.0%} dos negados estao fora do dominio,")
print(f"   e {1-neg_fora/neg_total:.0%} sao perfis conhecidos com PD alta.")

print(f"\n3) E os aprovados fora do dominio?")
ap_fora = (fora & ap).sum()
print(f"   {ap_fora:,} propostas ({ap_fora/ap.sum():.0%} das aprovadas) — PD media "
      f"{p.loc[fora & ap,'pd'].mean():.1%}")

print(f"\n4) A fronteira: score 5 vs score 4")
for s in [5, 4]:
    m = p["score"] == s
    print(f"   score {s}: {int(m.sum()):>4,} propostas · PD media {p.loc[m,'pd'].mean():>5.1%} "
          f"· bureau {p.loc[m,'score_bureau'].mean():>5.0f} · restricoes {p.loc[m,'qtd_restricoes_ativas'].mean():.2f}")
