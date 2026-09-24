# -*- coding: utf-8 -*-
"""O Deni afirma passar em todos os guard-rails com ROI acima de 15%.

Onde a analise pode estar sendo injusta com ele:

A. O motor aplica o prazo da tabela como valor FIXO. O professor chama a
   coluna de "Prazo max." — e um teto. Dar 60 meses a quem pediu 36 infla
   juros que nao existiriam.
B. O volume dele so fura por causa da premissa de aceite, que e invencao
   nossa. Com aceite de 100% — a premissa dele — quanto da?
C. Qual elasticidade faria a politica dele passar?
"""

import numpy as np
import pandas as pd

from banking.dados import carregar_processada, preparar_base_c
from banking.modelo import treinar_modelo_final
from banking.perda import fator_ead, lgd
from banking.politica import POLITICA_ESCOLHIDA, gerar_politica
from banking.roi import CENARIOS, Cenario, aplicar_politica, simular
from banking.score import score_de_pd
import banking.roi as R

base_a = carregar_processada("A")
base_c = carregar_processada("C")
modelo = treinar_modelo_final(base_a)
escorar = lambda df: modelo.predict_proba(df)[:, 1]
p = preparar_base_c(base_c).reset_index(drop=True)
p["pd"] = escorar(p)

print("=" * 80)
print("A. O PRAZO E TETO OU VALOR FIXO?")
print("=" * 80)
pedido = p["prazo_desejado_meses"]
print(f"\n  prazo pedido na base C: {sorted(pedido.unique())}")
print(f"  distribuicao: {pedido.value_counts().sort_index().to_dict()}")
for teto in (48, 60):
    acima = (pedido > teto).mean()
    abaixo = (pedido < teto).mean()
    print(f"\n  com teto de {teto}m: {acima:.1%} pediram MAIS (seriam encurtados), "
          f"{abaixo:.1%} pediram MENOS")
    print(f"    -> nesses {abaixo:.1%}, o motor esta dando prazo MAIOR do que o cliente pediu")

ALAV = {10: (0.0180, 60, 0.10), 9: (0.0205, 60, 0.10), 8: (0.0230, 60, 0.10),
        7: (0.0255, 60, 0.20), 6: (0.0280, 48, 0.20), 5: (0.0305, 48, 0.20),
        4: (0.0330, 48, 0.30)}
FAIXAS = {10: (0.0074, 0.0303), 9: (0.0303, 0.0401), 8: (0.0401, 0.0492),
          7: (0.0492, 0.0577), 6: (0.0577, 0.0678), 5: (0.0678, 0.0786),
          4: (0.0786, 0.0941)}


def ofertas_deni(prazo_como_teto: bool):
    bordas = sorted(((s, lo, hi) for s, (lo, hi) in FAIXAS.items()), key=lambda b: b[1])
    pdv = p["pd"].to_numpy()
    sc = np.ones(len(p), dtype=int)
    for s_, lo, hi in bordas:
        sc = np.where((pdv > lo) & (pdv <= hi), s_, sc)
    sc = np.where(pdv <= bordas[0][2], 10, sc)
    sc = np.where(pdv > bordas[-1][2], 1, sc)

    o = p.copy()
    o["score"] = sc
    o["taxa_am"] = [ALAV.get(s, (np.nan,) * 3)[0] for s in sc]
    teto = np.array([ALAV.get(s, (np.nan, np.nan, np.nan))[1] for s in sc], dtype=float)
    o["prazo_meses"] = (np.minimum(teto, pedido.to_numpy()) if prazo_como_teto else teto)
    o["pct_entrada_minima"] = [ALAV.get(s, (np.nan,) * 3)[2] for s in sc]
    o["aprovada"] = (o["pd"] <= 0.11) & o["taxa_am"].notna()
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
    return o


def linha(rot, o, cen="central"):
    r = simular(o, cen)
    viola = sorted({v.split()[0] for v in r.violacoes})
    print(f"  {rot:<46} ROI {r.roi_anual:>6.2%} · vol R$ {r.volume_originado/1e6:>5.1f} mi · "
          f"inad {r.inadimplencia:>5.2%} · aceite {r.taxa_aceite_media:>5.1%} · "
          f"{'viável' if not viola else 'viola ' + ','.join(viola)}")
    return r


print("\n  Efeito de tratar o prazo como TETO, na politica do Deni (cenario central):")
linha("prazo fixo da tabela (como estava)", ofertas_deni(False))
linha("prazo = min(pedido, teto)  <- correto", ofertas_deni(True))

print("\n  E na politica do Leo:")
el = (p["pd"] * fator_ead(p["prazo_meses"], p["ltv"])
      * lgd(p["idade_veiculo_anos"], p["ltv"], p["possui_avalista"]))
perda = (pd.DataFrame({"score": score_de_pd(p["pd"]), "el": el})
         .groupby("score")["el"].mean().to_dict())
pol_leo = gerar_politica(**POLITICA_ESCOLHIDA, perda_por_faixa=perda)
of_leo = aplicar_politica(p, pol_leo, escorar=escorar)
linha("prazo fixo de 48 (como esta)", of_leo)

of_leo_teto = of_leo.copy()
of_leo_teto["prazo_meses"] = np.minimum(of_leo["prazo_meses"].to_numpy(),
                                        pedido.to_numpy())
linha("prazo = min(pedido, 48)", of_leo_teto)

print("\n" + "=" * 80)
print("B. COM A PREMISSA DELE — aceite de 100%, sem ninguem desistir")
print("=" * 80)
SEM_FUGA = Cenario("sem_fuga", a0=1.0, beta_taxa=0.0, beta_entrada=0.0,
                   beta_prazo=0.0, gama=0.0)
originais = R.CENARIOS
R.CENARIOS = {**originais, "sem_fuga": SEM_FUGA}
try:
    print()
    for rot, o in (("Deni, prazo como teto", ofertas_deni(True)),
                   ("Léo", of_leo)):
        r = simular(o, SEM_FUGA)
        viola = sorted({v.split()[0] for v in r.violacoes})
        print(f"  {rot:<28} ROI {r.roi_anual:>6.2%} · vol R$ {r.volume_originado/1e6:>6.1f} mi · "
              f"inad {r.inadimplencia:>5.2%} · {'VIÁVEL' if not viola else 'viola ' + ','.join(viola)}")
finally:
    R.CENARIOS = originais

print("\n" + "=" * 80)
print("C. QUANTO DE ELASTICIDADE A POLITICA DELE AGUENTA?")
print("=" * 80)
print("\n  Escalando as elasticidades do cenario central por um fator f:")
print(f"  {'f':>6} {'aceite':>8} {'volume':>12} {'ROI':>8}  passa no volume?")
o_deni = ofertas_deni(True)
for f in (0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0, 1.5):
    c = originais["central"]
    cen = Cenario(f"f{f}", a0=c.a0, beta_taxa=c.beta_taxa * f,
                  beta_entrada=c.beta_entrada * f, beta_prazo=c.beta_prazo * f,
                  gama=c.gama)
    r = simular(o_deni, cen)
    passa = r.volume_originado >= 40e6
    print(f"  {f:>6.1f} {r.taxa_aceite_media:>7.1%} R$ {r.volume_originado/1e6:>8.1f} mi "
          f"{r.roi_anual:>7.2%}  {'SIM' if passa else 'nao'}")
print("\n  (f = 1,0 e a premissa do Leo; f = 0 e a do Deni)")
