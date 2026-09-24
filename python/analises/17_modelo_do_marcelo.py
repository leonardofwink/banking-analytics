"""A NOSSA politica, rodada sobre o modelo do Marcelo.

Ele submeteu a PD das 5.000 propostas da base C. Se a ordenacao dele for
melhor, a mesma tabela de precos rende mais — e essa e a unica alavanca que
sobe o ROI sem trocar volume.

Para ser justo, os dois rodam SEM re-escoragem: so temos a PD do pedido dele.
"""
import numpy as np, pandas as pd
from banking.dados import DIR_BRUTOS, carregar_processada, preparar_base_c
from banking.modelo import treinar_modelo_final
from banking.perda import fator_ead, lgd
from banking.politica import POLITICA_ESCOLHIDA, gerar_politica
from banking.roi import CENARIOS, aplicar_politica, simular
from banking.score import score_de_pd

base_a = carregar_processada("A"); base_c = carregar_processada("C")
modelo = treinar_modelo_final(base_a)
p = preparar_base_c(base_c).reset_index(drop=True)
p["pd_nossa"] = modelo.predict_proba(p)[:, 1]

m = pd.read_csv(DIR_BRUTOS / "colegas" / "marcelo" / "submissao_politica.csv")
m = m.set_index("id_proposta")["pd"]
p["pd_marcelo"] = p["id_proposta"].map(m).to_numpy()
print(f"PDs do Marcelo casadas: {p['pd_marcelo'].notna().sum():,} de {len(p):,}")
print(f"\ncorrelacao de Spearman entre os dois modelos: "
      f"{p[['pd_nossa','pd_marcelo']].corr(method='spearman').iloc[0,1]:.3f}")
print(f"PD media  — nossa {p['pd_nossa'].mean():.2%} · Marcelo {p['pd_marcelo'].mean():.2%}")

for qual in ("pd_nossa", "pd_marcelo"):
    p["pd"] = p[qual]
    el = (p["pd"] * fator_ead(p["prazo_meses"], p["ltv"])
          * lgd(p["idade_veiculo_anos"], p["ltv"], p["possui_avalista"]))
    perda = (pd.DataFrame({"score": score_de_pd(p["pd"]), "el": el})
             .groupby("score")["el"].mean().to_dict())
    faltando = [s for s in range(1, 11) if s not in perda]
    for s in faltando:
        perda[s] = max(perda.values())
    pol = gerar_politica(**POLITICA_ESCOLHIDA, perda_por_faixa=perda)
    of = aplicar_politica(p, pol, escorar=None)   # sem re-escoragem, nos dois
    res = {n: simular(of, n) for n in CENARIOS}
    c = res["central"]
    viola = [v for r in res.values() for v in r.violacoes]
    rot = "NOSSO modelo" if qual == "pd_nossa" else "modelo do MARCELO"
    print(f"\n--- nossa politica sobre o {rot} ---")
    print(f"  aprovacao {c.taxa_aprovacao:.1%} · ROI {c.roi_anual:.2%} · "
          f"volume central R$ {c.volume_originado/1e6:.1f} mi")
    print(f"  volume pior R$ {min(r.volume_originado for r in res.values())/1e6:.1f} mi · "
          f"inad pior {max(r.inadimplencia for r in res.values()):.2%} · "
          f"{'viavel' if not viola else 'VIOLA: ' + str(sorted(set(viola)))}")
