# -*- coding: utf-8 -*-
"""O capital nao fica parado: na Price ele volta em parcelas e pode girar.

A formula do professor divide pelo VOLUME ORIGINADO e pelo prazo inteiro,
como se os R$ 66,7 mi ficassem imobilizados 4 anos. Nao ficam — e isso tem
duas consequencias opostas, que so fazem sentido juntas.
"""
import sys

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from banking.dados import carregar_processada, preparar_base_c
from banking.modelo import treinar_modelo_final
from banking.perda import fator_ead, lgd
from banking.politica import POLITICA_ESCOLHIDA, gerar_politica
from banking.price import saldo_devedor
from banking.roi import CENARIOS, aplicar_politica, simular
from banking.score import score_de_pd

base_a = carregar_processada("A")
base_c = carregar_processada("C")
modelo = treinar_modelo_final(base_a)
escorar = lambda df: modelo.predict_proba(df)[:, 1]
p = preparar_base_c(base_c).reset_index(drop=True)
p["pd"] = escorar(p)
el = (p["pd"] * fator_ead(p["prazo_meses"], p["ltv"])
      * lgd(p["idade_veiculo_anos"], p["ltv"], p["possui_avalista"]))
perda = (pd.DataFrame({"score": score_de_pd(p["pd"]), "el": el})
         .groupby("score")["el"].mean().to_dict())
pol = gerar_politica(**POLITICA_ESCOLHIDA, perda_por_faixa=perda)
of = aplicar_politica(p, pol, escorar=escorar)
r = simular(of, "central")

ap = of[of["aprovada"]]
P = ap["valor_financiado_ofertado"].to_numpy()
i = ap["taxa_am"].to_numpy()
N = ap["prazo_meses"].to_numpy()
c = CENARIOS["central"]
excesso = np.maximum(i / 0.0159 - 1.0, 0.0)
aceite = np.clip(
    c.a0 * np.exp(-c.beta_taxa * excesso)
    * np.exp(-c.beta_entrada * ap["entrada_extra"].to_numpy())
    * np.exp(-c.beta_prazo * np.clip(1 - N / ap["prazo_desejado_meses"].to_numpy(), 0, 1)),
    0, 1)

vol = float(np.sum(aceite * P))
saldo = np.zeros(61)
for m in range(1, 61):
    ativo = N >= m
    if ativo.any():
        s = saldo_devedor(P[ativo], i[ativo], N[ativo], np.full(int(ativo.sum()), float(m)))
        saldo[m] = float(np.sum(aceite[ativo] * s))
vivos = saldo[1:][saldo[1:] > 0]
saldo_medio = vivos.mean()
ocioso_medio = vol - saldo_medio
anos = float(N.mean()) / 12

print("=" * 78)
print("1. O CAPITAL FICA MESMO IMOBILIZADO OS 4 ANOS?")
print("=" * 78)
print(f"\n  volume originado (denominador da fórmula) : R$ {vol/1e6:>6.1f} mi")
print(f"  saldo devedor médio ao longo da vida      : R$ {saldo_medio/1e6:>6.1f} mi")
print(f"  capital que volta e fica ocioso, em média : R$ {ocioso_medio/1e6:>6.1f} mi")
print(f"\n  O capital realmente empregado é {saldo_medio/vol:.0%} do originado.")
print(f"  No mês 24 o saldo já caiu para R$ {saldo[24]/1e6:.1f} mi — "
      f"R$ {(vol - saldo[24])/1e6:.1f} mi voltaram ao caixa.")

print("\n" + "=" * 78)
print("2. O MESMO RESULTADO, SOBRE O CAPITAL QUE FICOU DE FATO EMPREGADO")
print("=" * 78)
print(f"\n  ROI pela régua do conselho      : {r.roi_anual:>6.2%}"
      f"   (÷ volume originado)")
print(f"  Retorno sobre capital empregado : {r.roi_anual * vol / saldo_medio:>6.2%}"
      f"   (÷ saldo médio)")
print("\n  Não é receita nova: é a mesma receita sobre uma base menor.")

print("\n" + "=" * 78)
print("3. E SE O QUE VOLTA FOSSE APLICADO NO CDI?")
print("=" * 78)
print(f"\n  {'CDI':>6}  {'ganho no ocioso':>16}  {'custo de captação':>18}  "
      f"{'líquido':>9}   ROI final")
print("  " + "-" * 68)
for cdi_aa in (0.09, 0.105, 0.12):
    cdi_am = (1 + cdi_aa) ** (1 / 12) - 1
    ganho = sum((vol - saldo[m]) * cdi_am for m in range(1, 61) if saldo[m] > 0)
    custo = sum(saldo[m] * cdi_am for m in range(1, 61) if saldo[m] > 0)
    g = ganho / vol / anos
    k = custo / vol / anos
    print(f"  {cdi_aa:>5.1%}  {g*100:>+14.2f} pp  {-k*100:>+16.2f} pp  "
          f"{(g-k)*100:>+7.2f} pp   {r.roi_anual + g - k:>8.2%}")

print(f"\n  O saldo médio (R$ {saldo_medio/1e6:.1f} mi) é maior que o ocioso médio "
      f"(R$ {ocioso_medio/1e6:.1f} mi),")
print("  então o custo supera o ganho em qualquer CDI. Aplicar o que volta não")
print("  fecha a conta: traz junto o custo de ter captado o dinheiro.")
