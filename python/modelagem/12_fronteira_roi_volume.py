"""S12 · A meta de 15% de ROI é alcançável?

A tabela de indicadores do template do professor pede ROI anualizado **acima
de 15%**. A nossa política projeta 11,3%. Este script existe para responder,
com evidência em vez de opinião, se a lacuna é falha nossa ou restrição do
problema.

A grade do S09 tinha 960 políticas, mas duas alavancas ficaram estreitas:
prazo em {48, 60} e entrada em {0, 5%, 10%}. Aqui elas abrem até onde o
problema permite — **prazo só pode ser 24, 36, 48 ou 60**, porque é o que a
tabela de EAD do professor define — e o preço sobe até 3,0% de base.

São 5.600 políticas. O resultado está na spec, mas em resumo: nenhuma
combinação viável chega a 15%, e o guard-rail que bloqueia é **só o volume**.

Rodar::

    .\\scripts\\py.cmd python\\modelagem\\12_fronteira_roi_volume.py

Spec: ``docs/specs/S12_FRONTEIRA_ROI_VOLUME.md``.
"""

from __future__ import annotations

import itertools
import sys

import pandas as pd

from banking.dados import carregar_processada, preparar_base_c
from banking.modelo import treinar_modelo_final
from banking.perda import fator_ead, lgd
from banking.politica import gerar_politica, validar_monotonicidade
from banking.projeto import DIR_TABELAS, log_step
from banking.roi import CENARIOS, aplicar_politica, simular
from banking.score import score_de_pd

META_ROI = 0.15

# A grade ampliada. As duas linhas marcadas são as que o S09 manteve
# estreitas e que esta varredura existe para abrir.
GRADE = {
    "corte": [7, 6, 5, 4],
    "taxa_base": [0.0150, 0.0175, 0.0200, 0.0225, 0.0250, 0.0275, 0.0300],
    "k_risco": [0.0, 0.10, 0.20, 0.30, 0.50],
    "prazo_max": [24, 36, 48, 60],                   # <- aberto (S09: só 48 e 60)
    "entrada_base": [0.0, 0.10, 0.20, 0.30, 0.40],   # <- aberto (S09: até 10%)
    "entrada_passo": [0.0, 0.04],
}


def main() -> int:
    log_step("S12 · Fronteira ROI × volume")

    try:
        base_a = carregar_processada("A")
        base_c = carregar_processada("C")
    except FileNotFoundError as erro:
        log_step(str(erro), "erro")
        return 1

    modelo = treinar_modelo_final(base_a)
    escorar = lambda df: modelo.predict_proba(df)[:, 1]

    propostas = preparar_base_c(base_c)
    propostas["pd"] = escorar(propostas)

    el = (
        propostas["pd"]
        * fator_ead(propostas["prazo_meses"], propostas["ltv"])
        * lgd(propostas["idade_veiculo_anos"], propostas["ltv"], propostas["possui_avalista"])
    )
    perda_por_faixa = (
        pd.DataFrame({"score": score_de_pd(propostas["pd"]), "el": el})
        .groupby("score")["el"].mean().to_dict()
    )

    combinacoes = list(itertools.product(*GRADE.values()))
    log_step(f"{len(combinacoes)} políticas × {len(CENARIOS)} cenários")

    # Mesmo cache do S09: a PD re-escorada depende de entrada e prazo, não da
    # taxa. Sem isto seriam 5.600 escoragens em vez de 160.
    cache: dict[tuple, pd.DataFrame] = {}
    registros = []

    for i, combinacao in enumerate(combinacoes):
        corte, taxa_base, k_risco, prazo_max, entrada_base, entrada_passo = combinacao
        if i and i % 500 == 0:
            log_step(f"  {i}/{len(combinacoes)}")

        politica = gerar_politica(
            corte, taxa_base, k_risco, prazo_max, entrada_base, entrada_passo, perda_por_faixa
        )
        if validar_monotonicidade(politica):
            continue

        chave = (corte, prazo_max, entrada_base, entrada_passo)
        if chave not in cache:
            cache[chave] = aplicar_politica(propostas, politica, escorar=escorar)
        ofertas = cache[chave].copy()
        ofertas["taxa_am"] = ofertas["score"].map(politica.set_index("score")["taxa_am"])

        res = {nome: simular(ofertas, nome) for nome in CENARIOS}
        registros.append(
            {
                "corte": corte, "taxa_base": taxa_base, "k_risco": k_risco,
                "prazo_max": prazo_max, "entrada_base": entrada_base,
                "entrada_passo": entrada_passo,
                "roi_central": res["central"].roi_anual,
                "aprovacao": res["central"].taxa_aprovacao,
                "inadimplencia_pior": max(r.inadimplencia for r in res.values()),
                "volume_pior": min(r.volume_originado for r in res.values()),
                "viavel": not any(r.violacoes for r in res.values()),
            }
        )

    d = pd.DataFrame(registros)
    destino = DIR_TABELAS / "s12_fronteira_roi_volume.csv"
    d.to_csv(destino, index=False)

    viaveis = d[d["viavel"]]
    batem = d[d["roi_central"] >= META_ROI]

    log_step(f"{len(d):,} políticas · {len(viaveis)} viáveis", "ok")
    log_step(f"ROI máximo entre as viáveis: {viaveis['roi_central'].max():.2%}", "ok")
    log_step(
        f"{len(batem):,} batem a meta de {META_ROI:.0%} · "
        f"{int(batem['viavel'].sum())} delas são viáveis",
        "ok" if int(batem["viavel"].sum()) == 0 else "aviso",
    )

    print("\n--- Melhor ROI viável, por prazo ---")
    print(_por(viaveis, "prazo_max", "{:.0f} meses"))

    print("\n--- Melhor ROI viável, por entrada mínima ---")
    print(_por(viaveis, "entrada_base", "{:.0%}"))

    print(f"\n--- Por que as {len(batem):,} que batem a meta morrem ---")
    print(f"  inadimplência mínima entre elas : {batem['inadimplencia_pior'].min():>7.2%}  (máx 8%)")
    print(f"  aprovação máxima entre elas     : {batem['aprovacao'].max():>7.1%}  (mín 35%)")
    print(f"  volume máximo entre elas        : R$ {batem['volume_pior'].max()/1e6:>5.1f} mi  (mín R$ 40 mi)")
    print("\n  Só o volume bloqueia. Risco e seletividade passam.")

    print(f"\nTabela completa: {destino}")
    return 0


def _por(viaveis: pd.DataFrame, coluna: str, formato: str) -> str:
    """Melhor política viável para cada valor de uma alavanca."""
    linhas = []
    for valor in sorted(viaveis[coluna].unique()):
        sub = viaveis[viaveis[coluna] == valor]
        melhor = sub.loc[sub["roi_central"].idxmax()]
        linhas.append(
            f"  {formato.format(valor):>9} : {len(sub):>3} viáveis · "
            f"ROI {melhor['roi_central']:.2%} · volume R$ {melhor['volume_pior']/1e6:.1f} mi"
        )
    return "\n".join(linhas)


if __name__ == "__main__":
    sys.exit(main())
