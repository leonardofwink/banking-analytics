# -*- coding: utf-8 -*-
"""O Marcelo submeteu tudo: PD, decisao, taxa, prazo e entrada das 5.000.

Da para rodar a submissao dele EXATAMENTE como esta, com as PDs dele — sem
reconstruir nada. E a comparacao mais fiel possivel, e a unica que isola a
politica do modelo de verdade.
"""

import numpy as np
import pandas as pd

from banking.dados import DIR_BRUTOS, carregar_processada, preparar_base_c
from banking.modelo import treinar_modelo_final
from banking.perda import fator_ead, lgd
from banking.politica import POLITICA_ESCOLHIDA, gerar_politica
from banking.roi import CENARIOS, aplicar_politica, simular
from banking.score import score_de_pd

base_a = carregar_processada("A")
base_c = carregar_processada("C")
modelo = treinar_modelo_final(base_a)
escorar = lambda df: modelo.predict_proba(df)[:, 1]
p = preparar_base_c(base_c).reset_index(drop=True)
p["pd_leo"] = escorar(p)

sub = pd.read_csv(DIR_BRUTOS / "colegas" / "marcelo" / "submissao_politica.csv")
sub = sub.set_index("id_proposta")
for col in ("pd", "decisao", "taxa_am", "prazo_meses", "pct_entrada_minima"):
    p[f"m_{col}"] = p["id_proposta"].map(sub[col]).to_numpy()

print(f"propostas casadas: {p['m_pd'].notna().sum():,} de {len(p):,}")


def montar(pd_col, decisao_col, taxa_col, prazo_col, entrada_col, reescorar):
    o = p.copy()
    o["pd"] = o[pd_col]
    o["decisao"] = o[decisao_col]
    o["taxa_am"] = o[taxa_col]
    o["prazo_meses"] = o[prazo_col]
    o["pct_entrada_minima"] = o[entrada_col]
    o["aprovada"] = o["decisao"].astype(str).str.upper().eq("APROVAR")
    o["pct_entrada_efetiva"] = np.maximum(o["pct_entrada_desejada"].to_numpy(),
                                          o["pct_entrada_minima"].fillna(0).to_numpy())
    o["entrada_extra"] = o["pct_entrada_efetiva"] - o["pct_entrada_desejada"]
    o["valor_financiado_ofertado"] = o["valor_bem"] * (1 - o["pct_entrada_efetiva"])
    o["ltv_ofertado"] = 1 - o["pct_entrada_efetiva"]
    if reescorar:
        aj = o.copy()
        aj["ltv"] = o["ltv_ofertado"]
        aj["valor_financiado"] = o["valor_financiado_ofertado"]
        aj["prazo_meses"] = o["prazo_meses"].fillna(o["prazo_desejado_meses"])
        o["pd_ofertada"] = escorar(aj)
    else:
        o["pd_ofertada"] = o["pd"]
    return o


def mostrar(rotulo, o):
    res = {n: simular(o, n) for n in CENARIOS}
    c = res["central"]
    vol_pior = min(r.volume_originado for r in res.values())
    inad_pior = max(r.inadimplencia for r in res.values())
    viola = sorted({v.split()[0] for r in res.values() for v in r.violacoes})
    print(f"  {rotulo:<44} aprov {c.taxa_aprovacao:>5.1%} · ROI {c.roi_anual:>6.2%} · "
          f"vol {c.volume_originado/1e6:>5.1f}/{vol_pior/1e6:<5.1f} mi · "
          f"inad {inad_pior:>5.2%} · {'viável' if not viola else 'viola ' + ','.join(viola)}")


print("\n" + "=" * 104)
print("A SUBMISSAO DO MARCELO, EXATAMENTE COMO ELE ENTREGOU (PDs dele, ofertas dele)")
print("=" * 104 + "\n")

mostrar("submissão dele, PD dele, sem re-escorar",
        montar("m_pd", "m_decisao", "m_taxa_am", "m_prazo_meses", "m_pct_entrada_minima", False))
mostrar("submissão dele, PD do Léo na re-escoragem",
        montar("m_pd", "m_decisao", "m_taxa_am", "m_prazo_meses", "m_pct_entrada_minima", True))

# a do Leo, para referencia, nas mesmas condicoes
el = (p["pd_leo"] * fator_ead(p["prazo_meses"], p["ltv"])
      * lgd(p["idade_veiculo_anos"], p["ltv"], p["possui_avalista"]))
perda = (pd.DataFrame({"score": score_de_pd(p["pd_leo"]), "el": el})
         .groupby("score")["el"].mean().to_dict())
pol = gerar_politica(**POLITICA_ESCOLHIDA, perda_por_faixa=perda)
pp = p.copy()
pp["pd"] = pp["pd_leo"]
of = aplicar_politica(pp, pol, escorar=escorar)
mostrar("política do Léo, PD do Léo (referência)", of)

print("\n" + "=" * 104)
print("O QUE ELE REPORTA NO DOCUMENTO")
print("=" * 104)
print("  aprovação 49,2% · ROI ~12% (11,8% a 12,3%) · volume R$ 43 a 68 mi · inadimplência ~6%")
print("\n  A aprovação bate exatamente com o CSV dele. O ROI e o volume dependem")
print("  das premissas de aceite, que são dele e diferentes das do Léo.")

print("\n" + "=" * 104)
print("OS DOIS MODELOS NA BASE C")
print("=" * 104)
j = p[["pd_leo", "m_pd"]].dropna()
print(f"\n  Spearman: {j.corr(method='spearman').iloc[0, 1]:.4f}   "
      f"Pearson: {j.corr().iloc[0, 1]:.4f}")
print(f"  PD média — Léo {j['pd_leo'].mean():.2%} · Marcelo {j['m_pd'].mean():.2%}")
print(f"  PD máx   — Léo {j['pd_leo'].max():.2%} · Marcelo {j['m_pd'].max():.2%}")
concordam = (score_de_pd(j["pd_leo"].to_numpy()) == score_de_pd(j["m_pd"].to_numpy())).mean()
print(f"  mesmo score nos cortes do Léo: {concordam:.1%} das propostas")
