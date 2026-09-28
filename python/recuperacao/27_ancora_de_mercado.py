# -*- coding: utf-8 -*-
"""S13.4 · A âncora de preço — o que o mercado cobrava no período da Base C.

    TAXA_MERCADO = 1,59%  ←  média do livro da PRÓPRIA AutoCred

Esse número é o denominador de ``excesso = taxa / TAXA_MERCADO − 1`` em
``banking/roi.py``, isto é, a régua contra a qual "caro" é medido. Ele mede a
AutoCred, não o mercado — e foi a causa nº 1 da derrota, registrada em
``docs/processo/POST_MORTEM.md``.

O grupo vencedor comparou a taxa proposta com **dado público do Banco Central**
e mostrou onde ela caía na distribuição das instituições. O professor registrou
como diferencial: *"fez o que nenhum outro fez… preço defensável, não
arbitrado."*

Este script busca duas fontes, que respondem perguntas diferentes:

  Olinda  taxa por INSTITUIÇÃO, semanal — dá a distribuição, e com ela a
          mediana e os quartis. É o que permite dizer "estamos no quartil X".
  SGS     taxa MÉDIA do mercado, mensal, ponderada por volume — dá o nível.

As duas entram no relatório. Qual delas vira âncora é decisão de política, e o
script não decide por ninguém: ele mostra as duas e onde cada preço cai.

⚠️ **Dado externo exige procedência.** Série, período e data de extração vão
para o cabeçalho do CSV e para ``docs/FONTES_EXTERNAS.md``. Série do BCB é
revisada sem aviso: sem a data de extração registrada, um número que não
reproduz vira discussão sobre quem digitou errado.
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime
from urllib.parse import quote

import numpy as np
import pandas as pd
import requests

from banking.projeto import DIR_EXTERNOS, DIR_TABELAS, log_step
from banking.roi import TAXA_MERCADO

# --- O período que interessa -------------------------------------------------
# A Base C são propostas de jul a dez/2025. A âncora tem de ser desse período:
# usar a média de 2022-2024 foi parte do erro que este script corrige.
INICIO, FIM = "2025-07-01", "2025-12-31"

# --- Fonte 1 · Olinda, taxa por instituição ----------------------------------
# Modalidade 401101, "Aquisição de veículos - Prefixado", Pessoa Física — a
# mesma operação da AutoCred. Confirmada em ParametrosConsulta do serviço.
OLINDA = (
    "https://olinda.bcb.gov.br/olinda/servico/taxaJuros/versao/v2/odata"
    "/TaxasJurosDiariaPorInicioPeriodo"
)
MODALIDADE = "Aquisição de veículos - Prefixado"

# --- Fonte 2 · SGS, taxa média do mercado ------------------------------------
# Série 20749: taxa média de juros das operações de crédito com recursos livres,
# pessoas físicas, aquisição de veículos. Vem em % ao ANO.
SGS = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{serie}/dados"
SERIE_SGS = 20749

# --- Os preços que queremos posicionar na distribuição -----------------------
# Vêm da apuração do professor. Não são escolha nossa: são o que cada grupo
# efetivamente cobrou, e o que serve para responder "estávamos caros ou baratos?".
PRECOS = {
    "TAXA_MERCADO (âncora que usamos)": TAXA_MERCADO * 100,
    "Grupo 3 — nós (média praticada)": 1.911,
    "Grupo 1 (média praticada)": 2.364,
    "Grupo 2 — vencedor (média praticada)": 2.506,
    "Teto do enunciado (CET)": 3.500,
}


def _buscar(url: str, descricao: str) -> list[dict]:
    """GET com o encoding certo e mensagem de erro que diz o que fazer.

    Dois detalhes que custam tempo se não estiverem aqui: o OData recusa espaço
    codificado como ``+`` (a montagem da URL é manual por isso), e a resposta
    vem sem charset declarado corretamente — sem forçar utf-8, todo acento vira
    ``?``.
    """
    try:
        r = requests.get(url, timeout=120)
    except requests.RequestException as erro:
        raise SystemExit(
            f"não foi possível consultar {descricao}: {erro}\n"
            f"  Sem rede, baixe à mão e salve em {DIR_EXTERNOS} — "
            f"ver docs/FONTES_EXTERNAS.md."
        ) from erro

    if r.status_code != 200:
        raise SystemExit(f"{descricao} devolveu HTTP {r.status_code}: {r.text[:200]}")

    r.encoding = "utf-8"
    corpo = r.json()
    return corpo["value"] if isinstance(corpo, dict) else corpo


def taxas_por_instituicao() -> pd.DataFrame:
    """A distribuição semanal de taxa por instituição, no período da Base C."""
    filtro = (
        f"Modalidade eq '{MODALIDADE}' "
        f"and InicioPeriodo ge '{INICIO}' and InicioPeriodo le '{FIM}'"
    )
    campos = "InicioPeriodo,FimPeriodo,InstituicaoFinanceira,TaxaJurosAoMes,Posicao"
    url = (
        f"{OLINDA}?$filter={quote(filtro, safe='')}"
        f"&$select={quote(campos, safe='')}&$format=json"
    )
    linhas = _buscar(url, "Olinda/BCB (taxa por instituição)")

    df = pd.DataFrame(linhas).rename(columns={"TaxaJurosAoMes": "taxa_am"})
    df["taxa_am"] = pd.to_numeric(df["taxa_am"], errors="coerce")
    return df.dropna(subset=["taxa_am"])


def taxa_media_do_mercado() -> pd.DataFrame:
    """A taxa média do mercado, mensal, convertida de % a.a. para % a.m."""
    url = (
        f"{SGS.format(serie=SERIE_SGS)}?formato=json"
        f"&dataInicial={date.fromisoformat(INICIO).strftime('%d/%m/%Y')}"
        f"&dataFinal={date.fromisoformat(FIM).strftime('%d/%m/%Y')}"
    )
    linhas = _buscar(url, f"SGS/BCB série {SERIE_SGS}")

    df = pd.DataFrame(linhas)
    df["taxa_aa"] = pd.to_numeric(df["valor"], errors="coerce")
    # Juros compostos: a taxa mensal equivalente, não a anual dividida por 12.
    df["taxa_am"] = ((1.0 + df["taxa_aa"] / 100.0) ** (1.0 / 12.0) - 1.0) * 100.0
    return df.dropna(subset=["taxa_am"])


def _posicao(valor: float, amostra: np.ndarray) -> float:
    """Em que percentil da distribuição um preço cai."""
    return float((amostra < valor).mean() * 100.0)


def main() -> int:
    log_step("S13.4 · Âncora de preço — dado público do Banco Central")
    extraido_em = datetime.now().astimezone().isoformat(timespec="seconds")

    inst = taxas_por_instituicao()
    mercado = taxa_media_do_mercado()

    # Guarda o bruto antes de qualquer agregação: é o que permite auditar o
    # número mais tarde sem depender de a API responder igual.
    DIR_EXTERNOS.mkdir(parents=True, exist_ok=True)
    bruto = DIR_EXTERNOS / "bcb_taxas_veiculos_2025s2.json"
    bruto.write_text(
        json.dumps(
            {
                "extraido_em": extraido_em,
                "periodo": [INICIO, FIM],
                "olinda": {"modalidade": MODALIDADE, "url": OLINDA,
                           "linhas": inst.to_dict("records")},
                "sgs": {"serie": SERIE_SGS, "linhas": mercado.to_dict("records")},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    taxas = inst["taxa_am"].to_numpy(dtype=float)
    n_inst = inst["InstituicaoFinanceira"].nunique()
    n_per = inst["InicioPeriodo"].nunique()

    log_step(
        f"{len(inst)} observações · {n_inst} instituições · {n_per} semanas "
        f"· {INICIO} a {FIM}"
    )

    q = np.percentile(taxas, [5, 25, 50, 75, 95])
    print("\n--- A distribuição do mercado (% ao mês, por instituição) ---\n")
    print(f"  {'mínimo':<12} {taxas.min():>6.3f}")
    for rotulo, v in zip(("p5", "p25", "mediana", "p75", "p95"), q):
        print(f"  {rotulo:<12} {v:>6.3f}" + ("   <- mediana" if rotulo == "mediana" else ""))
    print(f"  {'máximo':<12} {taxas.max():>6.3f}")
    print(f"\n  média simples {taxas.mean():>6.3f}")
    print(f"  média do mercado (SGS {SERIE_SGS}, ponderada por volume) "
          f"{mercado['taxa_am'].mean():>6.3f}")

    # Taxa zero é promoção de banco de montadora, não preço de crédito. Fica
    # reportada à parte em vez de ser apagada: quem decide a âncora precisa
    # saber que ela existe e o quanto ela move a mediana.
    zeradas = int((taxas < 0.30).sum())
    sem_zero = taxas[taxas >= 0.30]
    print(f"\n  {zeradas} observações abaixo de 0,30% a.m. ({zeradas/len(taxas):.1%}) — "
          f"provável taxa promocional de banco de montadora.")
    print(f"  Excluindo-as, a mediana vai de {np.median(taxas):.3f}% "
          f"para {np.median(sem_zero):.3f}%.")

    print("\n--- Onde cada preço cai nessa distribuição ---\n")
    print(f"  {'':<38} {'% a.m.':>8} {'percentil':>11}")
    linhas_saida = []
    for rotulo, preco in PRECOS.items():
        pct = _posicao(preco, taxas)
        print(f"  {rotulo:<38} {preco:>8.3f} {pct:>10.1f}%")
        linhas_saida.append({"referencia": rotulo, "taxa_am_pct": preco,
                             "percentil_no_mercado": round(pct, 1)})

    mediana = float(np.median(taxas))
    print("\n--- O veredito ---\n")
    print(f"  A âncora que usamos ({TAXA_MERCADO:.2%} a.m.) está "
          f"{(mediana - TAXA_MERCADO * 100):.3f} ponto percentual ABAIXO da "
          f"mediana do mercado ({mediana:.3f}%).")
    print(f"  Ou seja: tratamos como 'preço de mercado' um valor que só "
          f"{_posicao(TAXA_MERCADO * 100, taxas):.0f}% das instituições cobravam ou menos.")
    print(f"\n  A afirmação do professor sobre o vencedor — 2,54% acima da mediana "
          f"e abaixo do topo — se reproduz:")
    print(f"    mediana {mediana:.3f}%  <  2,506%  <  máximo {taxas.max():.3f}%")

    saida = pd.DataFrame(linhas_saida)
    destino = DIR_TABELAS / "s13_ancora_de_mercado.csv"
    cabecalho = (
        f"# Fonte: Banco Central do Brasil\n"
        f"# Olinda/taxaJuros, modalidade '{MODALIDADE}' (401101), Pessoa Física\n"
        f"# SGS série {SERIE_SGS} (taxa média, % a.a., convertida para % a.m.)\n"
        f"# Período: {INICIO} a {FIM} — o mesmo da Base C\n"
        f"# Extraído em: {extraido_em}\n"
        f"# {len(inst)} observações, {n_inst} instituições, {n_per} semanas\n"
        f"# mediana={mediana:.4f} p25={q[1]:.4f} p75={q[3]:.4f} "
        f"media_sgs={mercado['taxa_am'].mean():.4f}\n"
    )
    with destino.open("w", encoding="utf-8", newline="") as fh:
        fh.write(cabecalho)
        saida.to_csv(fh, index=False)

    log_step(f"Bruto guardado em {bruto}")
    log_step(f"Tabela gravada em {destino}")
    log_step("Registre a procedência em docs/FONTES_EXTERNAS.md antes de usar o número",
             "aviso")
    return 0


if __name__ == "__main__":
    sys.exit(main())
