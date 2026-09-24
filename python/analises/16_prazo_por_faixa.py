"""O que o Deni faz que nunca testamos: prazo e entrada que VARIAM por faixa.

A nossa grade sempre deu o mesmo prazo a todas as faixas aprovadas. O Deni
da 60 meses aos scores bons e 48 aos ruins. Prazo longo em cliente bom rende
mais juros e sobe o aceite; prazo curto em cliente ruim corta exposicao.

Se isso funcionar, e a primeira alavanca nova desde o S09.
"""

import itertools

import numpy as np
import pandas as pd

from banking.dados import carregar_processada, preparar_base_c
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
p["pd"] = escorar(p)
p["score"] = score_de_pd(p["pd"])
el = (p["pd"] * fator_ead(p["prazo_meses"], p["ltv"])
      * lgd(p["idade_veiculo_anos"], p["ltv"], p["possui_avalista"]))
perda = (pd.DataFrame({"score": p["score"], "el": el})
         .groupby("score")["el"].mean().to_dict())


def aplicar(tab: pd.DataFrame) -> pd.DataFrame:
    """Mesma mecanica de aplicar_politica, com a tabela ja montada."""
    o = p.copy()
    idx = tab.set_index("score")
    for coluna in ("decisao", "taxa_am", "prazo_meses", "pct_entrada_minima"):
        o[coluna] = o["score"].map(idx[coluna])
    o["aprovada"] = o["decisao"].eq("APROVAR")
    o["pct_entrada_efetiva"] = np.maximum(
        o["pct_entrada_desejada"].to_numpy(),
        o["pct_entrada_minima"].fillna(0.0).to_numpy())
    o["entrada_extra"] = o["pct_entrada_efetiva"] - o["pct_entrada_desejada"]
    o["valor_financiado_ofertado"] = o["valor_bem"] * (1.0 - o["pct_entrada_efetiva"])
    o["ltv_ofertado"] = 1.0 - o["pct_entrada_efetiva"]
    aj = o.copy()
    aj["ltv"] = o["ltv_ofertado"]
    aj["valor_financiado"] = o["valor_financiado_ofertado"]
    aj["prazo_meses"] = o["prazo_meses"].fillna(o["prazo_desejado_meses"])
    o["pd_ofertada"] = escorar(aj)
    return o


def monta(corte, taxa_base, k, prazos: dict, entradas: dict) -> pd.DataFrame:
    """prazos e entradas sao dicionarios score -> valor."""
    linhas = []
    for s in range(10, 0, -1):
        if s >= corte:
            taxa = min(taxa_base + k * perda[s], 0.035)
            linhas.append({"score": s, "decisao": "APROVAR", "taxa_am": taxa,
                           "prazo_meses": float(prazos[s]),
                           "pct_entrada_minima": entradas[s]})
        else:
            linhas.append({"score": s, "decisao": "NEGAR", "taxa_am": np.nan,
                           "prazo_meses": np.nan, "pct_entrada_minima": np.nan})
    return pd.DataFrame(linhas)


def avalia(tab):
    of = aplicar(tab)
    res = {n: simular(of, n) for n in CENARIOS}
    c = res["central"]
    return {
        "roi": c.roi_anual,
        "aprov": c.taxa_aprovacao,
        "vol_central": c.volume_originado,
        "vol_pior": min(r.volume_originado for r in res.values()),
        "inad_pior": max(r.inadimplencia for r in res.values()),
        "viavel": not any(r.violacoes for r in res.values()),
    }


# --- referencia: a nossa politica -------------------------------------------
nossa = gerar_politica(**POLITICA_ESCOLHIDA, perda_por_faixa=perda)
base = avalia(nossa)
print("=" * 88)
print("REFERENCIA — a nossa politica (prazo 48 e entrada 10% para todas)")
print("=" * 88)
print(f"  ROI {base['roi']:.2%} · aprovacao {base['aprov']:.1%} · "
      f"volume pior R$ {base['vol_pior']/1e6:.1f} mi · inad pior {base['inad_pior']:.2%}")

# --- a grade nova ------------------------------------------------------------
# Perfis de prazo: score alto ganha prazo maior.
PERFIS_PRAZO = {
    "48 para todas (hoje)":      {s: 48 for s in range(1, 11)},
    "60 para todas":             {s: 60 for s in range(1, 11)},
    "60 nos bons, 48 nos ruins": {10: 60, 9: 60, 8: 60, 7: 60, 6: 48, 5: 48, 4: 48, 3: 48, 2: 48, 1: 48},
    "60 ate o 8, 48 abaixo":     {10: 60, 9: 60, 8: 60, 7: 48, 6: 48, 5: 48, 4: 48, 3: 48, 2: 48, 1: 48},
    "60 nos bons, 36 nos ruins": {10: 60, 9: 60, 8: 60, 7: 48, 6: 48, 5: 36, 4: 36, 3: 36, 2: 36, 1: 36},
    "48 nos bons, 36 nos ruins": {10: 48, 9: 48, 8: 48, 7: 48, 6: 36, 5: 36, 4: 36, 3: 36, 2: 36, 1: 36},
}
PERFIS_ENTRADA = {
    "10% para todas (hoje)": {s: 0.10 for s in range(1, 11)},
    "sem entrada":           {s: 0.00 for s in range(1, 11)},
    "10/20/30 como o Deni":  {10: .10, 9: .10, 8: .10, 7: .20, 6: .20, 5: .20, 4: .30, 3: .30, 2: .30, 1: .30},
    "5 a 15 como o Marcelo": {10: .05, 9: .05, 8: .05, 7: .05, 6: .05, 5: .05, 4: .10, 3: .10, 2: .15, 1: .15},
}

print("\n" + "=" * 88)
print("VARREDURA — prazo e entrada variaveis por faixa")
print("=" * 88)

melhores = []
for corte in (6, 5, 4, 3):
    for taxa_base in (0.0150, 0.0175, 0.0200, 0.0225):
        for k in (0.0, 0.10, 0.20, 0.30):
            for np_, prazos in PERFIS_PRAZO.items():
                for ne, entradas in PERFIS_ENTRADA.items():
                    tab = monta(corte, taxa_base, k, prazos, entradas)
                    r = avalia(tab)
                    r.update(corte=corte, taxa_base=taxa_base, k=k, prazo=np_, entrada=ne)
                    melhores.append(r)

d = pd.DataFrame(melhores)
viaveis = d[d["viavel"]]
print(f"\ntestadas: {len(d):,} · viaveis: {len(viaveis):,}")
print(f"ROI maximo entre as viaveis: {viaveis['roi'].max():.2%}")
print(f"   (o teto do S12, so com prazo/entrada fixos, era 11,46%)")

print("\n--- top 12 viaveis ---")
cols = ["roi", "aprov", "vol_pior", "inad_pior", "corte", "taxa_base", "k", "prazo", "entrada"]
top = viaveis.nlargest(12, "roi")[cols].copy()
top["roi"] = top["roi"].map("{:.2%}".format)
top["aprov"] = top["aprov"].map("{:.1%}".format)
top["vol_pior"] = (top["vol_pior"] / 1e6).map("R$ {:.1f} mi".format)
top["inad_pior"] = top["inad_pior"].map("{:.2%}".format)
top["taxa_base"] = top["taxa_base"].map("{:.2%}".format)
print(top.to_string(index=False))

print("\n--- melhor viavel por perfil de PRAZO ---")
for perfil in PERFIS_PRAZO:
    sub = viaveis[viaveis["prazo"] == perfil]
    if len(sub):
        m = sub.loc[sub["roi"].idxmax()]
        print(f"  {perfil:<30} ROI {m['roi']:.2%} · {len(sub):>3} viaveis · "
              f"vol pior R$ {m['vol_pior']/1e6:.1f} mi")
    else:
        print(f"  {perfil:<30} nenhuma viavel")

print("\n--- melhor viavel por perfil de ENTRADA ---")
for perfil in PERFIS_ENTRADA:
    sub = viaveis[viaveis["entrada"] == perfil]
    if len(sub):
        m = sub.loc[sub["roi"].idxmax()]
        print(f"  {perfil:<30} ROI {m['roi']:.2%} · {len(sub):>3} viaveis · "
              f"vol pior R$ {m['vol_pior']/1e6:.1f} mi")
    else:
        print(f"  {perfil:<30} nenhuma viavel")

d.to_csv("outputs/tabelas/s16_prazo_por_faixa.csv", index=False)
print("\ntabela completa: outputs/tabelas/s16_prazo_por_faixa.csv")
