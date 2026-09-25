# -*- coding: utf-8 -*-
"""Pré-computa tudo que o painel interativo precisa, no motor de verdade.

O painel roda no navegador e não tem como carregar o XGBoost. A saída aqui
é o que permite que ele seja **fiel**: em vez de reimplementar o modelo em
JavaScript e torcer para bater, varremos a grade inteira de políticas com
:func:`banking.roi.simular` — o mesmo código que produziu os números do
documento — e o painel vira uma consulta a essa tabela.

Duas saídas, com propósitos diferentes:

``grade``
    Uma entrada por combinação de (corte, taxa base, k de risco, prazo, entrada),
    com as métricas nos três cenários. É o que desenha as curvas e o que o
    simulador consulta quando o usuário arrasta um controle.

``propostas`` + ``pd_grade``
    A base C proposta a proposta, com a PD **re-escorada** em cada combinação
    de (prazo, entrada) que a grade permite. Sem isso o detalhe de um contrato
    mostraria a PD do pedido em vez da PD da oferta — que é exatamente a
    distinção que o trabalho inteiro faz questão de manter.

Uso::

    .\\scripts\\py.cmd python\\relatorios\\25_dados_do_painel.py
"""

from __future__ import annotations

import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from banking.dados import carregar_processada, preparar_base_c
from banking.modelo import treinar_modelo_final
from banking.perda import fator_ead, lgd
from banking.politica import gerar_politica
from banking.projeto import DIR_OUTPUTS
from banking.roi import CENARIOS, GUARD_RAILS, aplicar_politica, simular
from banking.score import score_de_pd

# --- A grade -----------------------------------------------------------------
# Escolhida para conter a política escolhida em todos os eixos: quem abrir o
# painel e não mexer em nada vê exatamente os números do documento.
CORTES = [4, 5, 6, 7, 8]
TAXAS_BASE = [0.013, 0.015, 0.017, 0.019]
K_RISCOS = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40]
PRAZOS = [24, 36, 48, 60]
ENTRADAS = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30]

PADRAO = {"corte": 5, "taxa_base": 0.015, "k_risco": 0.10,
          "prazo_max": 48, "entrada_base": 0.10}

CENARIOS_ORDEM = ["otimista", "central", "pessimista"]


def _log(msg: str) -> None:
    print(f"  {msg}", flush=True)


def main() -> None:
    inicio = time.time()

    base_a = carregar_processada("A")
    base_c = carregar_processada("C")
    modelo = treinar_modelo_final(base_a)
    _log(f"modelo treinado ({time.time() - inicio:.1f}s)")

    escorar_cru = lambda df: modelo.predict_proba(df)[:, 1]
    p = preparar_base_c(base_c).reset_index(drop=True)
    p["pd"] = escorar_cru(p)
    p["score"] = score_de_pd(p["pd"])

    el = (p["pd"] * fator_ead(p["prazo_meses"], p["ltv"])
          * lgd(p["idade_veiculo_anos"], p["ltv"], p["possui_avalista"]))
    perda_por_faixa = (pd.DataFrame({"score": p["score"], "el": el})
                       .groupby("score")["el"].mean().to_dict())

    # --- A PD re-escorada em cada (prazo, entrada) ---------------------------
    # Feita aqui, sobre TODAS as propostas, independente de aprovação: uma
    # proposta negada numa política é aprovada em outra, e o painel precisa
    # mostrar a oferta certa nas duas.
    _log("re-escorando a base C em cada combinação de prazo e entrada…")
    pd_grade: dict[str, list[int]] = {}
    for prazo, entrada in itertools.product(PRAZOS, ENTRADAS):
        ajustada = p.copy()
        efetiva = np.maximum(p["pct_entrada_desejada"].to_numpy(), entrada)
        ajustada["ltv"] = 1.0 - efetiva
        ajustada["valor_financiado"] = p["valor_bem"].to_numpy() * (1.0 - efetiva)
        # O prazo ofertado é o da política, **não** o mínimo entre ele e o
        # pedido: `gerar_politica` grava `prazo_max` na linha e
        # `aplicar_politica` o usa direto. É por isso que 49% dos aprovados
        # recebem mais prazo do que pediram — e a PD tem de refletir isso.
        ajustada["prazo_meses"] = float(prazo)
        # 0,01 pp de resolução: o suficiente para exibir, e metade do tamanho
        pd_grade[f"{prazo}|{entrada:.2f}"] = np.round(
            escorar_cru(ajustada) * 10000).astype(int).tolist()
    _log(f"{len(pd_grade)} combinações ({time.time() - inicio:.1f}s)")

    # --- A varredura ---------------------------------------------------------
    # Ela custa ~10 min. Guardar o resultado assim que sai evita perdê-la por
    # um erro em qualquer passo posterior — que foi exatamente o que aconteceu
    # na primeira execução, num `astype(int)` sobre coluna com ausentes.
    total = len(CORTES) * len(TAXAS_BASE) * len(K_RISCOS) * len(PRAZOS) * len(ENTRADAS)
    cache = DIR_OUTPUTS / "painel" / "_grade.json"
    if cache.exists():
        colunas = json.loads(cache.read_text(encoding="utf-8"))
        if len(colunas.get("viavel", [])) == total:
            _log(f"grade lida do cache ({total:,} políticas) — apague "
                 f"{cache.name} para refazer")
            return _montar(colunas, p, base_c, perda_por_faixa, pd_grade, inicio)
        _log("cache com tamanho diferente da grade atual; refazendo")
    _log(f"varrendo {total:,} políticas × 3 cenários…")

    colunas: dict[str, list] = {
        "aprovacao": [], "taxa_min": [], "taxa_max": [], "viavel": [],
    }
    for c in CENARIOS_ORDEM:
        for m in ("roi", "volume", "inadimplencia", "contratos", "juros", "perda"):
            colunas[f"{m}_{c}"] = []

    feitas = 0
    for corte, prazo, entrada in itertools.product(CORTES, PRAZOS, ENTRADAS):
        # A escoragem depende de (corte, prazo, entrada) — não do preço. Vale
        # guardar: são 140 escoragens em vez de 4.480.
        for taxa_base, k_risco in itertools.product(TAXAS_BASE, K_RISCOS):
            politica = gerar_politica(
                corte=corte, taxa_base=taxa_base, k_risco=k_risco,
                prazo_max=prazo, entrada_base=entrada, entrada_passo=0.0,
                perda_por_faixa=perda_por_faixa)
            ofertas = aplicar_politica(p, politica, escorar=escorar_cru)

            aprovadas = ofertas[ofertas["aprovada"]]
            colunas["aprovacao"].append(round(len(aprovadas) / len(ofertas), 5))
            if len(aprovadas):
                colunas["taxa_min"].append(round(float(aprovadas["taxa_am"].min()), 6))
                colunas["taxa_max"].append(round(float(aprovadas["taxa_am"].max()), 6))
            else:
                colunas["taxa_min"].append(0.0)
                colunas["taxa_max"].append(0.0)

            viavel = True
            for nome in CENARIOS_ORDEM:
                r = simular(ofertas, nome)
                colunas[f"roi_{nome}"].append(round(r.roi_anual, 5))
                colunas[f"volume_{nome}"].append(round(r.volume_originado / 1e3))
                colunas[f"inadimplencia_{nome}"].append(round(r.inadimplencia, 5))
                colunas[f"contratos_{nome}"].append(round(r.contratos_esperados))
                colunas[f"juros_{nome}"].append(round(r.juros_recebidos / 1e3))
                colunas[f"perda_{nome}"].append(round(r.perda_realizada / 1e3))
                if r.violacoes:
                    viavel = False
            # "Viável" aqui é o critério do trabalho: passa nos quatro
            # guard-rails nos TRÊS cenários, não só no central.
            colunas["viavel"].append(1 if viavel else 0)

            feitas += 1
            if feitas % 400 == 0:
                _log(f"  {feitas:,}/{total:,} ({time.time() - inicio:.0f}s)")

    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(colunas, separators=(",", ":")), encoding="utf-8")
    _log(f"grade gravada em cache ({time.time() - inicio:.0f}s)")

    return _montar(colunas, p, base_c, perda_por_faixa, pd_grade, inicio)


def _montar(colunas, p, base_c, perda_por_faixa, pd_grade, inicio) -> None:
    """Monta o JSON final a partir da grade — separado para que um erro aqui
    não custe a varredura inteira."""
    # --- As propostas --------------------------------------------------------
    bruta = base_c.reset_index(drop=True)
    propostas = {
        "id": bruta["id_proposta"].tolist(),
        "valor_bem": np.round(bruta["valor_bem"]).astype(int).tolist(),
        "entrada_desejada": np.round(bruta["pct_entrada_desejada"], 4).tolist(),
        "prazo_desejado": bruta["prazo_desejado_meses"].astype(int).tolist(),
        "idade_veiculo": bruta["idade_veiculo_anos"].astype(int).tolist(),
        "idade_cliente": bruta["idade_cliente"].astype(int).tolist(),
        "renda": np.round(bruta["renda_mensal_declarada"].fillna(-1)).astype(int).tolist(),
        "score_bureau": np.round(bruta["score_bureau"].fillna(-1)).astype(int).tolist(),
        "restricoes": bruta["qtd_restricoes_ativas"].astype(int).tolist(),
        "avalista": (bruta["possui_avalista"].astype(str).str.upper()
                     .isin(["SIM", "S", "TRUE", "1"]).astype(int).tolist()),
        "ocupacao": bruta["ocupacao"].astype(str).tolist(),
        "canal": bruta["canal_originacao"].astype(str).tolist(),
    }

    saida = {
        "gerado_em": time.strftime("%Y-%m-%d"),
        "padrao": PADRAO,
        "eixos": {"corte": CORTES, "taxa_base": TAXAS_BASE, "k_risco": K_RISCOS,
                  "prazo_max": PRAZOS, "entrada_base": ENTRADAS},
        "cenarios": CENARIOS_ORDEM,
        "elasticidades": {c: {"a0": CENARIOS[c].a0, "beta_taxa": CENARIOS[c].beta_taxa,
                              "beta_entrada": CENARIOS[c].beta_entrada,
                              "beta_prazo": CENARIOS[c].beta_prazo,
                              "gama": CENARIOS[c].gama} for c in CENARIOS_ORDEM},
        "guard_rails": GUARD_RAILS,
        "perda_por_faixa": {str(k): round(v, 6) for k, v in perda_por_faixa.items()},
        "grade": colunas,
        "propostas": propostas,
        "pd_pedido": np.round(p["pd"].to_numpy() * 10000).astype(int).tolist(),
        "pd_grade": pd_grade,
    }

    destino = DIR_OUTPUTS / "painel" / "dados.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(saida, separators=(",", ":"), ensure_ascii=False),
                       encoding="utf-8")
    mb = destino.stat().st_size / 1e6
    _log(f"gravado: {destino} ({mb:.2f} MB, {time.time() - inicio:.0f}s)")

    # --- Confere que o padrão do painel bate com o do documento --------------
    i = ((((CORTES.index(PADRAO["corte"]) * len(PRAZOS)
            + PRAZOS.index(PADRAO["prazo_max"])) * len(ENTRADAS)
           + ENTRADAS.index(PADRAO["entrada_base"])) * len(TAXAS_BASE)
          + TAXAS_BASE.index(PADRAO["taxa_base"])) * len(K_RISCOS)
         + K_RISCOS.index(PADRAO["k_risco"]))
    _log(f"conferência do padrão (índice {i}):")
    _log(f"  ROI central   {colunas['roi_central'][i]:.2%}   (documento: 11,33%)")
    _log(f"  volume pior   R$ {colunas['volume_pessimista'][i]/1e3:.1f} mi   (documento: 45,1 mi)")
    _log(f"  inadimplência {colunas['inadimplencia_central'][i]:.2%}   (documento: 6,33%)")
    _log(f"  aprovação     {colunas['aprovacao'][i]:.1%}   (documento: 59,5%)")
    _log(f"  viável        {'sim' if colunas['viavel'][i] else 'NÃO'}")


if __name__ == "__main__":
    main()
