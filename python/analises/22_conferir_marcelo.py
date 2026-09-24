"""S22 · Conferência do material do Marcelo.

O documento dele é o mais rico em números verificáveis dos três. Este script
testa cada afirmação contra as bases do professor e contra o CSV que ele
submeteu — o mesmo tratamento que o material do Deni recebeu.

Marca ``OK`` quando bate, ``~`` quando bate por pouco e ``!!`` quando diverge.

Rodar::

    .\\scripts\\py.cmd python\\analises\\22_conferir_marcelo.py
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from banking.dados import DIR_BRUTOS, carregar_bruto, carregar_processada, preparar_base_c
from banking.modelo import treinar_modelo_final
from banking.perda import fator_ead, lgd
from banking.price import juros_totais
from banking.projeto import log_step

SUB = DIR_BRUTOS / "colegas" / "marcelo" / "submissao_politica.csv"

# Os cortes de score do Marcelo, lidos da tabela do documento dele.
CORTES = [0.034, 0.039, 0.045, 0.050, 0.057, 0.066, 0.079, 0.100, 0.145]


def selo(bate: bool | None, perto: bool = False) -> str:
    if bate:
        return "OK"
    return "~ " if perto else "!!"


def conferir(rotulo: str, afirmado: str, medido: str, bate: bool, perto: bool = False) -> None:
    print(f"  {selo(bate, perto)} {rotulo:<46} diz {afirmado:>16} · achei {medido:>16}")


def main() -> int:
    log_step("S22 · Conferência do material do Marcelo")

    base_a = carregar_processada("A")
    base_c = carregar_processada("C")
    bruta_a = carregar_bruto("A")
    sub = pd.read_csv(SUB)
    p = preparar_base_c(base_c).reset_index(drop=True)
    pdm = p["id_proposta"].map(sub.set_index("id_proposta")["pd"]).to_numpy()
    p["pd_m"] = pdm

    # ======================================================== 1
    print("\n" + "=" * 92)
    print("1. O QUE ELE DIZ SOBRE A BASE C")
    print("=" * 92 + "\n")

    excl = ((p["score_bureau"] < 460) | (p["qtd_restricoes_ativas"] >= 3)
            | (p["ltv"] > 0.95))
    n_excl = int(excl.sum())
    conferir("«39% (1.973) têm bureau<460, 3+ restrições ou LTV>95%»",
             "39% / 1.973", f"{excl.mean():.1%} / {n_excl:,}",
             abs(n_excl - 1973) <= 30, abs(n_excl - 1973) <= 120)

    # ⚠️ O score DECRESCE com a PD: 10 é o melhor risco. np.digitize devolve
    # índice crescente, então é 10 menos o índice — não o índice mais um.
    score_m = 10 - np.digitize(pdm, CORTES)
    frac_s1 = (score_m == 1).mean()
    conferir("«38% caem no score 1»", "38%", f"{frac_s1:.1%}",
             abs(frac_s1 - 0.38) < 0.01, abs(frac_s1 - 0.38) < 0.03)

    n_2a10 = int((score_m >= 2).sum())
    conferir("«3.102 propostas nos scores 2 a 10»", "3.102", f"{n_2a10:,}",
             abs(n_2a10 - 3102) <= 30, abs(n_2a10 - 3102) <= 120)

    aprov = sub["decisao"].eq("APROVAR")
    conferir("«2.461 aprovadas depois das regras»", "2.461", f"{int(aprov.sum()):,}",
             int(aprov.sum()) == 2461)
    conferir("«49,2% de aprovação»", "49,2%", f"{aprov.mean():.1%}",
             abs(aprov.mean() - 0.492) < 0.003)

    frac_s5 = (score_m >= 5).mean()
    conferir("«aprovar do score 5 daria 35,2%»", "35,2%", f"{frac_s5:.1%}",
             abs(frac_s5 - 0.352) < 0.01, abs(frac_s5 - 0.352) < 0.03)
    frac_s2 = (score_m >= 2).mean()
    conferir("«do score 2, 62% antes das regras»", "62%", f"{frac_s2:.1%}",
             abs(frac_s2 - 0.62) < 0.01, abs(frac_s2 - 0.62) < 0.03)

    # ======================================================== 2
    print("\n" + "=" * 92)
    print("2. O QUE ELE DIZ SOBRE A BASE A")
    print("=" * 92 + "\n")

    safra = bruta_a.copy()
    safra["ano"] = pd.to_datetime(safra["data_originacao"]).dt.year
    por_ano = safra.groupby("ano")["default_90_12"].mean()
    for ano, afirmado in ((2022, 0.0867), (2023, 0.0894), (2024, 0.0718)):
        if ano in por_ano.index:
            m = por_ano[ano]
            conferir(f"«default de {afirmado:.2%} em {ano}»", f"{afirmado:.2%}",
                     f"{m:.2%}", abs(m - afirmado) < 0.0015, abs(m - afirmado) < 0.005)

    nulos_renda = bruta_a["renda_mensal_declarada"].isna().mean()
    conferir("«ausentes: renda 7,7%»", "7,7%", f"{nulos_renda:.1%}",
             abs(nulos_renda - 0.077) < 0.005, abs(nulos_renda - 0.077) < 0.015)

    # ======================================================== 3
    print("\n" + "=" * 92)
    print("3. A TABELA DE POLÍTICA DELE, CONTRA O CSV QUE ELE SUBMETEU")
    print("=" * 92 + "\n")

    ap = sub[aprov]
    conferir("«taxas de 1,85% a 2,18%»", "1,85–2,18%",
             f"{ap['taxa_am'].min():.2%}–{ap['taxa_am'].max():.2%}",
             abs(ap["taxa_am"].min() - 0.0185) < 1e-4 and abs(ap["taxa_am"].max() - 0.0218) < 1e-4)
    conferir("«taxa média ~1,95%»", "~1,95%", f"{ap['taxa_am'].mean():.2%}",
             abs(ap["taxa_am"].mean() - 0.0195) < 0.0008)
    conferir("«prazo 60, e 48 nos scores 2 e 3»", "48 e 60",
             "/".join(str(int(x)) for x in sorted(ap["prazo_meses"].unique())),
             set(ap["prazo_meses"].unique()) == {48.0, 60.0})
    conferir("«entrada de 5% a 15%»", "5/10/15%",
             "/".join(f"{x:.0%}" for x in sorted(ap["pct_entrada_minima"].unique())),
             set(ap["pct_entrada_minima"].round(2)) == {0.05, 0.10, 0.15})
    conferir("«aprovar scores 2 a 10, negar o 1»", "mín. 2",
             f"mín. {int(ap['score_1a10'].min())}", int(ap["score_1a10"].min()) == 2)

    # o score do CSV bate com os cortes que ele publicou?
    score_csv = sub["score_1a10"].to_numpy()
    igual = (score_csv == score_m).mean()
    conferir("score do CSV bate com os cortes da tabela dele", "100%", f"{igual:.1%}",
             igual > 0.995, igual > 0.95)

    # ======================================================== 4
    print("\n" + "=" * 92)
    print("4. AS AFIRMAÇÕES ECONÔMICAS")
    print("=" * 92 + "\n")

    idx = p.set_index("id_proposta")
    ap_full = sub[aprov].set_index("id_proposta").join(
        idx[["valor_bem", "pct_entrada_desejada", "idade_veiculo_anos",
             "possui_avalista"]], how="left")
    ent = np.maximum(ap_full["pct_entrada_desejada"].to_numpy(),
                     ap_full["pct_entrada_minima"].to_numpy())
    principal = ap_full["valor_bem"].to_numpy() * (1 - ent)
    ltv_of = 1 - ent
    juros = juros_totais(principal, ap_full["taxa_am"].to_numpy(),
                         ap_full["prazo_meses"].to_numpy())
    frac_juros = juros.sum() / principal.sum()
    conferir("«juros somam ~48% do volume»", "~48%", f"{frac_juros:.1%}",
             abs(frac_juros - 0.48) < 0.03, abs(frac_juros - 0.48) < 0.08)

    perda = (ap_full["pd"].to_numpy()
             * fator_ead(ap_full["prazo_meses"], pd.Series(ltv_of)) * principal
             * lgd(ap_full["idade_veiculo_anos"], pd.Series(ltv_of),
                   ap_full["possui_avalista"]))
    for score_alvo, afirmado in ((10, 0.020), (2, 0.082)):
        m = ap_full["score_1a10"].to_numpy() == score_alvo
        if m.sum():
            frac = perda[m].sum() / principal[m].sum()
            conferir(f"«perda de {afirmado:.1%} do financiado no score {score_alvo}»",
                     f"{afirmado:.1%}", f"{frac:.1%}",
                     abs(frac - afirmado) < 0.005, abs(frac - afirmado) < 0.015)

    aceite_para_40mi = 40e6 / principal.sum()
    conferir("«precisa de ~45% de aceite para R$ 40 mi»", "~45%",
             f"{aceite_para_40mi:.1%}", abs(aceite_para_40mi - 0.45) < 0.03,
             abs(aceite_para_40mi - 0.45) < 0.08)

    prazo_anos = ap_full["prazo_meses"].to_numpy().mean() / 12
    roi_sem_fuga = (juros.sum() - perda.sum()) / principal.sum() / prazo_anos
    conferir("«ROI ~12% (11,8% a 12,3%)»", "11,8–12,3%", f"{roi_sem_fuga:.2%}",
             0.118 <= roi_sem_fuga <= 0.123, 0.110 <= roi_sem_fuga <= 0.132)

    volume_total = principal.sum()
    print(f"\n  volume se todos aceitarem: R$ {volume_total/1e6:.1f} mi")
    print(f"  ele projeta R$ 43 a 68 mi conforme o aceite "
          f"({43e6/volume_total:.0%} a {68e6/volume_total:.0%} de aceite)")

    # ======================================================== 5
    print("\n" + "=" * 92)
    print("5. A VALIDAÇÃO QUE ELE FEZ — preços da V3 sobre o default REAL de 2024")
    print("=" * 92 + "\n")
    print("  Ele afirma ROI de 12,4%. Refazendo com a base A de 2024:\n")

    a24 = bruta_a[pd.to_datetime(bruta_a["data_originacao"]).dt.year == 2024].copy()
    modelo = treinar_modelo_final(base_a)
    proc24 = carregar_processada("A")
    proc24 = proc24[pd.to_datetime(proc24["data_originacao"]).dt.year == 2024]
    pd24 = modelo.predict_proba(proc24)[:, 1]
    sc24 = 10 - np.digitize(pd24, CORTES)

    TAXAS = {10: .0187, 9: .0187, 8: .0185, 7: .0190, 6: .0191,
             5: .0197, 4: .0199, 3: .0207, 2: .0218}
    PRAZOS = {s: (48 if s in (2, 3) else 60) for s in range(2, 11)}
    aprovadas24 = sc24 >= 2
    if aprovadas24.sum():
        taxa24 = np.array([TAXAS.get(s, np.nan) for s in sc24])
        prazo24 = np.array([float(PRAZOS.get(s, np.nan)) for s in sc24])
        princ24 = proc24["valor_financiado"].to_numpy()
        m = aprovadas24 & ~np.isnan(taxa24)
        j24 = juros_totais(princ24[m], taxa24[m], prazo24[m])
        default_real = proc24["default_90_12"].to_numpy()[m]
        perda24 = (default_real
                   * fator_ead(pd.Series(prazo24[m]), pd.Series(proc24["ltv"].to_numpy()[m]))
                   * princ24[m]
                   * lgd(proc24["idade_veiculo_anos"].to_numpy()[m],
                         proc24["ltv"].to_numpy()[m],
                         proc24["possui_avalista"].to_numpy()[m]))
        roi24 = (j24.sum() - perda24.sum()) / princ24[m].sum() / (prazo24[m].mean() / 12)
        conferir("«ROI de 12,4% com os defaults reais de 2024»", "12,4%", f"{roi24:.2%}",
                 abs(roi24 - 0.124) < 0.008, abs(roi24 - 0.124) < 0.02)
        print(f"\n     {int(m.sum()):,} contratos de 2024 · inadimplência real "
              f"{default_real.mean():.2%} · juros {j24.sum()/princ24[m].sum():.1%} do volume")
        print("     (aproximação: usa o modelo do Léo para o score, não o dele)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
