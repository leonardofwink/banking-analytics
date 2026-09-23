"""Duas perguntas do Leonardo:

1. O que move o VOLUME? Qual alavanca rende mais volume por ponto de ROI?
2. O que precisaria ser verdade para uma politica de 15% virar viavel?
"""

import copy
import itertools

import numpy as np
import pandas as pd

from banking.dados import carregar_processada, preparar_base_c
from banking.modelo import treinar_modelo_final
from banking.perda import fator_ead, lgd
from banking.politica import POLITICA_ESCOLHIDA, gerar_politica
from banking.projeto import log_step
from banking.roi import CENARIOS, Cenario, aplicar_politica, simular
from banking.score import score_de_pd

base_a = carregar_processada("A")
base_c = carregar_processada("C")
modelo = treinar_modelo_final(base_a)
escorar = lambda df: modelo.predict_proba(df)[:, 1]

p = preparar_base_c(base_c)
p["pd"] = escorar(p)
el = (p["pd"] * fator_ead(p["prazo_meses"], p["ltv"])
      * lgd(p["idade_veiculo_anos"], p["ltv"], p["possui_avalista"]))
perda = (pd.DataFrame({"score": score_de_pd(p["pd"]), "el": el})
         .groupby("score")["el"].mean().to_dict())

print("=" * 74)
print("CONTEXTO: quanto volume existe para ser tomado?")
print("=" * 74)
teto = p["valor_financiado_desejado"].sum()
print(f"  soma do financiado desejado das 5.000 propostas : R$ {teto/1e6:.1f} mi")
print(f"  se aprovassemos TODAS com aceite de 100%        : R$ {teto/1e6:.1f} mi")
print(f"  nossa politica entrega (central)                : R$ 66,7 mi  ({66.7e6/teto:.0%} do teto)")
print(f"  o guard-rail exige                              : R$ 40,0 mi  ({40e6/teto:.0%} do teto)")

# ---------------------------------------------------------------- 1
print("\n" + "=" * 74)
print("1. O QUE MOVE O VOLUME (partindo da nossa politica)")
print("=" * 74)

def rodar(**kw):
    cfg = dict(POLITICA_ESCOLHIDA)
    cfg.update(kw)
    pol = gerar_politica(**cfg, perda_por_faixa=perda)
    of = aplicar_politica(p, pol, escorar=escorar)
    res = {n: simular(of, n) for n in CENARIOS}
    return res["central"], min(r.volume_originado for r in res.values()), res

base_c_res, base_vol_pior, base_todos = rodar()
print(f"\nNOSSA POLITICA: ROI {base_c_res.roi_anual:.2%} · volume central R$ {base_c_res.volume_originado/1e6:.1f} mi "
      f"· pior cenario R$ {base_vol_pior/1e6:.1f} mi")

variacoes = [
    ("corte 5 -> 4 (aprovar 68,7%)", dict(corte=4)),
    ("corte 5 -> 6 (aprovar 50,5%)", dict(corte=6)),
    ("taxa base 1,50% -> 1,25%", dict(taxa_base=0.0125)),
    ("taxa base 1,50% -> 1,75%", dict(taxa_base=0.0175)),
    ("k de risco 0,10 -> 0,00", dict(k_risco=0.0)),
    ("k de risco 0,10 -> 0,20", dict(k_risco=0.20)),
    ("entrada 10% -> 0%", dict(entrada_base=0.0)),
    ("entrada 10% -> 20%", dict(entrada_base=0.20)),
    ("prazo 48 -> 60", dict(prazo_max=60)),
    ("prazo 48 -> 36", dict(prazo_max=36)),
]

print(f"\n{'alavanca':<32} {'ROI':>8} {'d ROI':>8} {'vol central':>13} {'d vol':>9} {'viavel':>7}")
print("-" * 74)
linhas = []
for rotulo, kw in variacoes:
    r, vol_pior, todos = rodar(**kw)
    viola = any(t.violacoes for t in todos.values())
    d_roi = (r.roi_anual - base_c_res.roi_anual) * 100
    d_vol = (r.volume_originado - base_c_res.volume_originado) / 1e6
    print(f"{rotulo:<32} {r.roi_anual:>7.2%} {d_roi:>+7.2f}pp "
          f"R$ {r.volume_originado/1e6:>8.1f} mi {d_vol:>+8.1f} {'sim' if not viola else 'NAO':>7}")
    linhas.append((rotulo, d_roi, d_vol, not viola))

print("\n--- eficiencia: milhoes de volume ganhos por ponto de ROI cedido ---")
for rotulo, d_roi, d_vol, ok in sorted(linhas, key=lambda x: -(x[2] / abs(x[1]) if x[1] else 0)):
    if d_vol > 0 and d_roi < 0:
        print(f"  {rotulo:<32} +{d_vol:>5.1f} mi por {abs(d_roi):.2f}pp = {d_vol/abs(d_roi):>6.1f} mi/pp"
              f"{'' if ok else '   (inviavel)'}")

# ---------------------------------------------------------------- 2
print("\n" + "=" * 74)
print("2. O QUE PRECISARIA SER VERDADE PARA UMA POLITICA DE 15% VIRAR VIAVEL?")
print("=" * 74)
print("\nEscalando TODAS as elasticidades por um fator f (f=1,0 e a nossa premissa).")
print("f menor = cliente menos sensivel a preco, entrada e prazo.\n")

GRADE = {
    "corte": [7, 6, 5, 4],
    "taxa_base": [0.0150, 0.0200, 0.0250, 0.0300],
    "k_risco": [0.0, 0.10, 0.20, 0.30, 0.50],
    "prazo_max": [48, 60],
    "entrada_base": [0.0, 0.10],
    "entrada_passo": [0.0],
}
combos = list(itertools.product(*GRADE.values()))

def cenarios_escalados(f):
    saida = {}
    for nome, c in CENARIOS.items():
        saida[nome] = Cenario(
            nome=c.nome, a0=c.a0,
            beta_taxa=c.beta_taxa * f, beta_entrada=c.beta_entrada * f,
            beta_prazo=c.beta_prazo * f, gama=c.gama,
        )
    return saida

import banking.roi as R

print(f"{'fator f':>8} {'viaveis':>8} {'melhor ROI viavel':>18} {'viaveis com ROI>=15%':>22}")
print("-" * 62)
for f in [1.0, 0.8, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]:
    originais = R.CENARIOS
    R.CENARIOS = cenarios_escalados(f)
    try:
        cache, melhor, n_viaveis, n_15 = {}, 0.0, 0, 0
        for corte, tb, k, pz, eb, ep in combos:
            pol = gerar_politica(corte, tb, k, pz, eb, ep, perda)
            chave = (corte, pz, eb, ep)
            if chave not in cache:
                cache[chave] = aplicar_politica(p, pol, escorar=escorar)
            of = cache[chave].copy()
            of["taxa_am"] = of["score"].map(pol.set_index("score")["taxa_am"])
            res = {n: simular(of, n) for n in R.CENARIOS}
            viavel = not any(r.violacoes for r in res.values())
            roi = res["central"].roi_anual
            if viavel:
                n_viaveis += 1
                melhor = max(melhor, roi)
                if roi >= 0.15:
                    n_15 += 1
    finally:
        R.CENARIOS = originais
    print(f"{f:>8.1f} {n_viaveis:>8} {melhor:>17.2%} {n_15:>22}")
