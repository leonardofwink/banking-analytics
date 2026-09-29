# -*- coding: utf-8 -*-
"""S13.10 · Diagnóstico de política — os alarmes que não existiam.

Este script existe por causa de uma frase dita depois da apuração:

    "era esse tipo de insight que eu queria ter tido na hora da elaboração"

Os indicadores abaixo levam segundos para calcular e estavam disponíveis desde
o primeiro dia. Eles não apareceram porque **ninguém os pediu** — não porque
faltasse dado. Rodados sobre a política que submetemos, teriam acusado quatro
problemas antes da entrega:

======================  ==========  ==========================================
 indicador               submetida   o que dizia
======================  ==========  ==========================================
 inclinação do preço     0,067       metade de quem precifica risco de verdade
 subsídio cruzado        6,4×        o cliente bom paga 6× mais, pelo risco
 posição no mercado      p55         abaixo da âncora de 2,021% — estávamos
                                     baratos e nos achávamos caros
 quadrante               permissivo  o pior dos quatro
                         e barato
======================  ==========  ==========================================

**Não é análise: é instrumentação.** A diferença entre *"descobrimos depois"* e
*"o repositório avisa antes"*.

Compara a nossa política submetida, a da recuperação e as dos outros dois
grupos — estas últimas reconstruídas do quadro comparativo que o professor
publicou, para a comparação ser reproduzível em vez de lembrada.
"""

from __future__ import annotations

import json
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
import pandas as pd

from banking.dados import carregar_processada, preparar_base_c
from banking.modelo import treinar_modelo_final
from banking.perda import perda_por_faixa
from banking.politica import (
    PRAZO_COMO_TETO_RECUPERACAO,
    POLITICA_ESCOLHIDA,
    POLITICA_RECUPERACAO,
    gerar_politica,
)
from banking.projeto import DIR_EXTERNOS, DIR_TABELAS, log_step, semear
from banking.roi import (
    CENARIO_CALIBRADO,
    PREMISSAS_CALIBRADAS,
    Cenario,
    aplicar_politica,
    simular,
)
from banking.score import CORTES_PD, SCORE_MAXIMO, SCORE_MINIMO, faixa_de_score

#: Limiares do quadrante. São **convenção declarada**, não achado: servem para
#: classificar, e o relatório sempre imprime os números crus ao lado.
#:
#: O eixo de seletividade usa o teto de PD contra a **mediana da própria base**,
#: não a taxa de aprovação: cortar abaixo da mediana significa rejeitar mais da
#: metade do risco que bateu à porta, e isso não depende de quantas propostas
#: chegaram. A taxa de aprovação continua no relatório, ao lado.
#: "Caro" é acima da ÂNCORA que o projeto adotou (a média de mercado ponderada
#: por volume, PRD § Decisões de modelagem D1) — não acima da mediana das
#: instituições. Usar uma régua para decidir o preço e outra para classificá-lo
#: produz o absurdo de chamar de "cara" uma política abaixo do preço de mercado.
#: O percentil continua no relatório, porque ele responde outra pergunta:
#: "quantas portas cobram menos que a nossa?".

#: Margem para chamar de "na fronteira" em vez de forçar um dos dois lados.
MARGEM_FRONTEIRA = 0.10

#: Bordas do que a calibração sustenta (perfil do S13.5).
SEVERO = Cenario("severo", CENARIO_CALIBRADO.a0, 1.363,
                 CENARIO_CALIBRADO.beta_entrada, CENARIO_CALIBRADO.beta_prazo, 1.930)

# --- As políticas dos outros grupos, do quadro do professor ------------------
# ⚠️ Reconstruídas da tabela publicada e aplicadas sobre a NOSSA PD — não temos
# os modelos deles. Servem para comparar o **desenho** da política, não para
# reproduzir o ROI que eles tiraram.
CORTES_GRUPO1 = (0.0200, 0.0300, 0.0450, 0.0600, 0.0800, 0.1100, 0.1500,
                 0.2193, 0.3472)
# Taxa: ponto médio da faixa publicada, porque eles precificaram contrato a
# contrato — "um algoritmo, não uma tabela de política", nas palavras do professor.
TAXAS_GRUPO1 = {10: 0.02115, 9: 0.02175, 8: 0.02330, 7: 0.02450,
                6: 0.02550, 5: 0.02745, 4: 0.02885}

CORTES_GRUPO2 = (0.0294, 0.0354, 0.0412, 0.0478, 0.0560, 0.0651, 0.0788,
                 0.1025, 0.1479)
TAXAS_GRUPO2 = {10: 0.0230, 9: 0.0230, 8: 0.0240, 7: 0.0250,
                6: 0.0260, 5: 0.0280, 4: 0.0290}


def _tabela_de(taxas: dict, prazo: int, entrada: float) -> pd.DataFrame:
    """Monta a tabela de um grupo a partir da taxa por faixa que ele publicou."""
    linhas = []
    for score in range(SCORE_MAXIMO, SCORE_MINIMO - 1, -1):
        ok = score in taxas
        linhas.append({
            "score": score,
            "decisao": "APROVAR" if ok else "NEGAR",
            "taxa_am": taxas.get(score, np.nan),
            "prazo_meses": float(prazo) if ok else np.nan,
            "pct_entrada_minima": entrada if ok else np.nan,
        })
    return pd.DataFrame(linhas)


def _mercado() -> np.ndarray:
    caminho = DIR_EXTERNOS / "bcb_taxas_veiculos_2025s2.json"
    if not caminho.exists():
        raise SystemExit(f"falta {caminho} — rode 27_ancora_de_mercado.py antes")
    bruto = json.loads(caminho.read_text(encoding="utf-8"))
    return np.asarray(
        [l["taxa_am"] for l in bruto["olinda"]["linhas"] if l["taxa_am"] is not None],
        dtype=float,
    )


def diagnosticar(politica: pd.DataFrame, ofertas: pd.DataFrame, cortes,
                 mercado: np.ndarray, pd_mediana: float) -> dict:
    """Os indicadores que dizem se uma política precifica risco ou finge que sim.

    :param politica: a tabela de faixas.
    :param ofertas: saída de :func:`aplicar_politica` para essa tabela.
    :param cortes: as fronteiras de PD usadas, para ler a largura das faixas.
    :param mercado: a distribuição de taxa do BCB, de ``27_ancora_de_mercado``.
    :param pd_mediana: a PD mediana da base, referência do eixo de seletividade.
    """
    aprovadas = politica[politica["decisao"] == "APROVAR"].sort_values(
        "score", ascending=False
    )
    scores = aprovadas["score"].astype(int).tolist()
    faixas = [faixa_de_score(s, cortes) for s in scores]
    taxas = aprovadas["taxa_am"].to_numpy(dtype=float)

    # Ponto médio de PD de cada faixa aprovada, em pontos percentuais.
    meio_pd = np.array([(lo + hi) / 2 * 100 for lo, hi in faixas])

    # 1. Inclinação: quantos pontos de TAXA a política sobe por ponto de PD.
    #    Mede se o preço acompanha o risco ou se é quase plano.
    inclinacao = float(np.polyfit(meio_pd, taxas * 100, 1)[0]) if len(scores) > 1 else 0.0

    # 2. Subsídio cruzado: quantas vezes a taxa cobre a perda da faixa, na
    #    melhor contra a pior. Razão alta = o cliente bom banca o ruim.
    prazo = float(aprovadas["prazo_meses"].iloc[0])
    perda_mes = meio_pd / 100 * 1.03 * 0.68 / prazo * 100
    cobertura = (taxas * 100) / perda_mes
    subsidio = float(cobertura[0] / cobertura[-1]) if len(cobertura) > 1 else 1.0

    # 3. Largura das faixas: quanto o risco varia DENTRO de uma faixa que cobra
    #    um preço só. Usa a MEDIANA, não a média: a melhor faixa começa em zero
    #    (ou quase), e dividir por isso produz uma razão gigante que sequestra a
    #    média — 101x contra 1,40x de mediana, na nossa política.
    largura = float(np.median([hi / max(lo, 0.005) for lo, hi in faixas]))

    r = simular(ofertas, CENARIO_CALIBRADO, PREMISSAS_CALIBRADAS)
    rs = simular(ofertas, SEVERO, PREMISSAS_CALIBRADAS)

    ap = ofertas[ofertas["aprovada"]]
    excesso = np.maximum(ap["taxa_am"].to_numpy() / PREMISSAS_CALIBRADAS.taxa_mercado - 1, 0)
    encurt = np.clip(1 - ap["prazo_meses"].to_numpy() / ap["prazo_desejado_meses"].to_numpy(), 0, 1)
    c = CENARIO_CALIBRADO
    aceite = np.clip(
        c.a0 * np.exp(-c.beta_taxa * excesso) * np.exp(-c.beta_entrada * ap["entrada_extra"].to_numpy())
        * np.exp(-c.beta_prazo * encurt), 0, 1)
    peso = aceite * ap["valor_financiado_ofertado"].to_numpy()
    taxa_media = float(np.average(ap["taxa_am"].to_numpy(), weights=peso) * 100)
    percentil = float((mercado < taxa_media).mean() * 100)

    teto = faixas[-1][1]
    if teto < pd_mediana * (1 - MARGEM_FRONTEIRA):
        eixo = "seletivo"
    elif teto > pd_mediana * (1 + MARGEM_FRONTEIRA):
        eixo = "permissivo"
    else:
        eixo = "na fronteira"
    caro = taxa_media > PREMISSAS_CALIBRADAS.taxa_mercado * 100
    return {
        "teto_pd": faixas[-1][1] * 100,
        "aprovacao": r.taxa_aprovacao,
        "taxa_media": taxa_media,
        "percentil": percentil,
        "inclinacao": inclinacao,
        "subsidio": subsidio,
        "largura": largura,
        "roi": r.roi_anual,
        "volume": r.volume_originado,
        "inadimplencia": r.inadimplencia,
        "roi_severo": rs.roi_anual,
        "aguenta_severo": (not rs.violacoes) and rs.roi_anual >= 0.15,
        "quadrante": f"{eixo} e {'caro' if caro else 'barato'}",
    }


def _alarme(d: dict) -> list[str]:
    """O que um comitê deveria perguntar antes de aprovar esta política."""
    avisos = []
    if d["inclinacao"] < 0.10:
        avisos.append(
            f"preço quase plano ({d['inclinacao']:.3f} pp por pp de PD): é a "
            "patologia que o conselho diagnosticou na política antiga"
        )
    if d["subsidio"] > 4.0:
        avisos.append(
            f"subsídio cruzado de {d['subsidio']:.1f}×: o cliente bom banca o ruim"
        )
    ancora = PREMISSAS_CALIBRADAS.taxa_mercado * 100
    if d["taxa_media"] < ancora:
        avisos.append(
            f"taxa média de {d['taxa_media']:.3f}% está ABAIXO da âncora de "
            f"mercado ({ancora:.3f}%): a política está barata, e o simulador "
            "pode estar dizendo o contrário se a âncora dele for o livro próprio"
        )
    if d["percentil"] > 90:
        avisos.append(
            f"preço no percentil {d['percentil']:.0f}: indefensável num comitê"
        )
    if not d["aguenta_severo"]:
        avisos.append("não fecha os cinco limites na borda severa do que o dado sustenta")
    if d["largura"] > 1.6:
        avisos.append(
            f"faixas largas ({d['largura']:.2f}× de risco dentro de uma faixa que "
            "cobra um preço só)"
        )
    return avisos


def main() -> int:
    log_step("S13.10 · Diagnóstico de política")
    semear()
    modelo = treinar_modelo_final(carregar_processada("A"))
    escorar = lambda df: modelo.predict_proba(df)[:, 1]  # noqa: E731
    p = preparar_base_c(carregar_processada("C")).reset_index(drop=True)
    p["pd"] = escorar(p)
    mercado = _mercado()
    pd_mediana = float(np.median(p["pd"]))
    log_step(f"PD mediana da Base C: {pd_mediana:.2%} — a régua do eixo de seletividade")

    casos = []
    for nome, tabela, cortes, teto in [
        ("Grupo 3 · submetida",
         gerar_politica(**POLITICA_ESCOLHIDA, perda_por_faixa=perda_por_faixa(p)),
         CORTES_PD, False),
        ("Grupo 3 · recuperação",
         gerar_politica(**POLITICA_RECUPERACAO, perda_por_faixa=perda_por_faixa(p)),
         CORTES_PD, PRAZO_COMO_TETO_RECUPERACAO),
        ("Grupo 1 · 2º lugar",
         _tabela_de(TAXAS_GRUPO1, 60, 0.10), CORTES_GRUPO1, True),
        ("Grupo 2 · vencedor",
         _tabela_de(TAXAS_GRUPO2, 60, 0.10), CORTES_GRUPO2, True),
    ]:
        ofertas = aplicar_politica(p, tabela, escorar=escorar, cortes=cortes,
                                   prazo_como_teto=teto)
        casos.append({"politica": nome,
                      **diagnosticar(tabela, ofertas, cortes, mercado, pd_mediana)})

    d = pd.DataFrame(casos)

    print("\n  COMO A POLÍTICA TRATA O RISCO\n")
    print(f"  {'':<24}{'teto PD':>9}{'aprova':>9}{'inclinação':>12}"
          f"{'subsídio':>10}{'largura':>9}")
    for _, l in d.iterrows():
        print(f"  {l['politica']:<24}{l['teto_pd']:>8.2f}%{l['aprovacao']:>8.1%}"
              f"{l['inclinacao']:>12.3f}{l['subsidio']:>9.1f}×{l['largura']:>8.2f}×")

    print("\n  COMO A POLÍTICA SE POSICIONA NO MERCADO\n")
    print(f"  {'':<24}{'taxa média':>12}{'percentil':>11}  quadrante")
    for _, l in d.iterrows():
        print(f"  {l['politica']:<24}{l['taxa_media']:>11.3f}%{l['percentil']:>10.0f}"
              f"  {l['quadrante']}")

    print("\n  O QUE ELA ENTREGA (premissa calibrada; a nossa PD para todos)\n")
    print(f"  {'':<24}{'ROI':>8}{'volume':>11}{'inad':>8}{'ROI severo':>12}  aguenta?")
    for _, l in d.iterrows():
        print(f"  {l['politica']:<24}{l['roi']:>8.2%}{l['volume']/1e6:>9.1f} mi"
              f"{l['inadimplencia']:>8.2%}{l['roi_severo']:>12.2%}"
              f"  {'sim' if l['aguenta_severo'] else 'NÃO'}")

    print("\n  ALARMES\n")
    for caso in casos:
        avisos = _alarme(caso)
        print(f"  {caso['politica']}")
        if not avisos:
            print("    — nenhum")
        for a in avisos:
            print(f"    🔴 {a}")
        print()

    destino = DIR_TABELAS / "s13_diagnostico_de_politica.csv"
    d.to_csv(destino, index=False)
    log_step(f"Tabela gravada em {destino}")
    log_step("As políticas dos Grupos 1 e 2 rodam sobre a NOSSA PD — comparam "
             "desenho, não reproduzem o ROI apurado deles", "aviso")
    return 0


if __name__ == "__main__":
    sys.exit(main())
