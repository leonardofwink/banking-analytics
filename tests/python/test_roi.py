"""S08.5 · Testes da Tabela Price e do motor de ROI.

O motor produz o número que decide a política inteira. Um erro aqui não levanta
exceção: devolve um ROI plausível e a escolha sai errada.

Por isso cada peça é testada contra **caso de resposta conhecida** — carteira
sem default, contrato pago até o fim, saldo no último mês — antes de o
resultado agregado valer alguma coisa.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from banking.dados import carregar_processada
from banking.price import juros_pagos_ate, juros_totais, parcela, saldo_devedor
from banking.roi import (
    CENARIOS,
    CENARIO_CALIBRADO,
    PREMISSAS_CALIBRADAS,
    PREMISSAS_SUBMETIDAS,
    GUARD_RAILS,
    TAXA_MERCADO,
    aplicar_politica,
    simular,
)
from banking.score import SCORE_MAXIMO, SCORE_MINIMO, faixa_de_score, score_de_pd


# --- Tabela Price ------------------------------------------------------------
def test_parcela_reproduz_a_base_a() -> None:
    """A validação que vale mais que qualquer caso sintético.

    A base A traz `parcela_mensal` calculada pelo professor. Se a nossa Price
    bate com a dele, a aritmética do financiamento está certa — e tudo que o
    motor de ROI constrói em cima dela também.
    """
    try:
        base_a = carregar_processada("A")
    except FileNotFoundError as erro:
        pytest.skip(str(erro))

    calculada = parcela(base_a["valor_financiado"], base_a["taxa_juros_am"], base_a["prazo_meses"])
    erro_relativo = np.abs(calculada - base_a["parcela_mensal"]) / base_a["parcela_mensal"]
    assert erro_relativo.mean() < 1e-4
    assert erro_relativo.max() < 1e-3


def test_saldo_zera_na_ultima_parcela() -> None:
    assert saldo_devedor([10_000], [0.0159], [48], [48])[0] == pytest.approx(0.0, abs=1e-6)


def test_saldo_no_mes_zero_e_o_principal() -> None:
    assert saldo_devedor([10_000], [0.0159], [48], [0])[0] == pytest.approx(10_000)


def test_juros_ate_o_fim_igualam_os_juros_totais() -> None:
    """Coerência entre as duas funções: pagar n parcelas é pagar tudo."""
    a = juros_pagos_ate([10_000], [0.0159], [48], [48])[0]
    b = juros_totais([10_000], [0.0159], [48])[0]
    assert a == pytest.approx(b)


def test_juros_de_quem_quebra_sao_menores_que_o_total() -> None:
    """Quem quebra no mês 6 de um contrato de 48 não pagou 48 parcelas."""
    parcial = juros_pagos_ate([10_000], [0.0159], [48], [6])[0]
    total = juros_totais([10_000], [0.0159], [48])[0]
    assert 0 < parcial < total


def test_parcela_nao_e_toda_receita() -> None:
    """A distinção que o motor depende: parcela contém amortização.

    Contar a parcela inteira como receita superestimaria o ROI de qualquer
    carteira com inadimplência — e é o erro mais fácil de cometer aqui.
    """
    principal, taxa, prazo, mes = 10_000.0, 0.0159, 48, 6
    pago = parcela([principal], [taxa], [prazo])[0] * mes
    juros = juros_pagos_ate([principal], [taxa], [prazo], [mes])[0]
    amortizado = pago - juros

    assert juros < pago, "juros não podem igualar o total pago"
    assert amortizado > 0, "parte da parcela é devolução de principal, não receita"
    # A 1,59% a.m. em 48 meses, os juros são ~51% da parcela no início — quase
    # metade do que entra no caixa é dinheiro voltando, não ganho.
    assert 0.3 < juros / pago < 0.7


def test_taxa_zero_nao_quebra() -> None:
    """Taxa zero degenera a fórmula de Price — vira amortização simples."""
    p = parcela([12_000], [0.0], [12])[0]
    assert p == pytest.approx(1_000.0)
    assert juros_totais([12_000], [0.0], [12])[0] == pytest.approx(0.0)


def test_taxa_em_percentual_e_recusada() -> None:
    with pytest.raises(ValueError, match="percentual"):
        parcela([10_000], [1.59], [48])


# --- Fixtures do motor -------------------------------------------------------
def _propostas_sinteticas(n=200, pd_valor=0.05, prazo=48, entrada=0.2) -> pd.DataFrame:
    """Carteira controlada, para casos de resposta conhecida."""
    return pd.DataFrame(
        {
            "pd": np.full(n, pd_valor),
            "valor_bem": np.full(n, 50_000.0),
            "pct_entrada_desejada": np.full(n, entrada),
            "valor_financiado_desejado": np.full(n, 50_000.0 * (1 - entrada)),
            "prazo_desejado_meses": np.full(n, prazo),
            "idade_veiculo_anos": np.full(n, 3),
            "possui_avalista": np.array(["Não"] * n),
        }
    )


def _politica(corte=7, taxa=0.02, prazo=48, entrada=0.2) -> pd.DataFrame:
    scores = list(range(SCORE_MAXIMO, SCORE_MINIMO - 1, -1))
    return pd.DataFrame(
        {
            "score": scores,
            "decisao": ["APROVAR" if s >= corte else "NEGAR" for s in scores],
            "taxa_am": [taxa if s >= corte else np.nan for s in scores],
            "prazo_meses": [prazo if s >= corte else np.nan for s in scores],
            "pct_entrada_minima": [entrada if s >= corte else np.nan for s in scores],
        }
    )


# --- aplicar_politica --------------------------------------------------------
def test_entrada_efetiva_e_o_maximo_entre_desejada_e_exigida() -> None:
    """Ninguém é obrigado a dar MENOS entrada do que já queria dar."""
    propostas = _propostas_sinteticas(entrada=0.30)
    ofertas = aplicar_politica(propostas, _politica(entrada=0.10))
    assert (ofertas["pct_entrada_efetiva"] == 0.30).all()
    assert (ofertas["entrada_extra"] == 0.0).all()


def test_entrada_exigida_acima_da_desejada_reduz_o_financiado() -> None:
    propostas = _propostas_sinteticas(entrada=0.10)
    ofertas = aplicar_politica(propostas, _politica(entrada=0.30))
    assert (ofertas["pct_entrada_efetiva"] == 0.30).all()
    assert ofertas["entrada_extra"].to_numpy() == pytest.approx(0.20)
    assert (ofertas["valor_financiado_ofertado"] < ofertas["valor_financiado_desejado"]).all()
    assert ofertas["ltv_ofertado"].to_numpy() == pytest.approx(0.70)


def test_politica_incompleta_falha_claro() -> None:
    propostas = _propostas_sinteticas()
    with pytest.raises(ValueError, match="colunas"):
        aplicar_politica(propostas, pd.DataFrame({"score": [1], "decisao": ["NEGAR"]}))


# --- simular: casos de resposta conhecida ------------------------------------
def test_carteira_sem_default_da_juros_sobre_volume_sobre_anos() -> None:
    """O caso que fecha a fórmula oficial.

    Sem default e sem perda, ROI = juros ÷ volume ÷ anos. Se este não bater, a
    fórmula está implementada errada e nenhum outro número vale.
    """
    propostas = _propostas_sinteticas(pd_valor=0.0, prazo=48, entrada=0.2)
    ofertas = aplicar_politica(propostas, _politica(corte=1, taxa=TAXA_MERCADO, entrada=0.2))
    r = simular(ofertas, "central")

    assert r.perda_realizada == pytest.approx(0.0)
    esperado = r.juros_recebidos / r.volume_originado / r.prazo_medio_anos
    assert r.roi_anual == pytest.approx(esperado)
    assert r.inadimplencia == pytest.approx(0.0)


def test_prazo_medio_em_anos_e_o_prazo_dividido_por_doze() -> None:
    propostas = _propostas_sinteticas(prazo=60)
    ofertas = aplicar_politica(propostas, _politica(corte=1, prazo=60))
    assert simular(ofertas, "central").prazo_medio_anos == pytest.approx(5.0)


def test_negar_tudo_devolve_resultado_vazio_sem_quebrar() -> None:
    propostas = _propostas_sinteticas()
    politica = _politica(corte=11)  # ninguém alcança
    r = simular(aplicar_politica(propostas, politica), "central")
    assert r.taxa_aprovacao == 0.0
    assert "nenhuma proposta aprovada" in r.violacoes


# --- Os cenários -------------------------------------------------------------
def test_taxa_mais_alta_derruba_o_aceite() -> None:
    """A direção declarada pelo professor: preço acima do mercado afasta."""
    propostas = _propostas_sinteticas()
    barato = simular(aplicar_politica(propostas, _politica(taxa=TAXA_MERCADO)), "central")
    caro = simular(aplicar_politica(propostas, _politica(taxa=0.033)), "central")
    assert caro.taxa_aceite_media < barato.taxa_aceite_media
    assert caro.volume_originado < barato.volume_originado


def test_taxa_mais_alta_aumenta_a_pd_por_selecao_adversa() -> None:
    """Quem aceita pagar caro costuma ser quem não tem alternativa."""
    propostas = _propostas_sinteticas()
    barato = simular(aplicar_politica(propostas, _politica(taxa=TAXA_MERCADO)), "central")
    caro = simular(aplicar_politica(propostas, _politica(taxa=0.033)), "central")
    assert caro.inadimplencia > barato.inadimplencia


def test_exigir_mais_entrada_derruba_o_aceite() -> None:
    propostas = _propostas_sinteticas(entrada=0.10)
    pouca = simular(aplicar_politica(propostas, _politica(entrada=0.10)), "central")
    muita = simular(aplicar_politica(propostas, _politica(entrada=0.40)), "central")
    assert muita.taxa_aceite_media < pouca.taxa_aceite_media


def test_cenario_pessimista_aceita_menos_que_o_otimista() -> None:
    propostas = _propostas_sinteticas()
    ofertas = aplicar_politica(propostas, _politica())
    otimista = simular(ofertas, "otimista")
    pessimista = simular(ofertas, "pessimista")
    assert pessimista.taxa_aceite_media < otimista.taxa_aceite_media
    assert pessimista.volume_originado < otimista.volume_originado


def test_aceite_fica_entre_zero_e_um() -> None:
    propostas = _propostas_sinteticas()
    for nome in CENARIOS:
        for taxa in (0.005, TAXA_MERCADO, 0.035):
            r = simular(aplicar_politica(propostas, _politica(taxa=taxa)), nome)
            assert 0.0 <= r.taxa_aceite_media <= 1.0


def test_simulacao_e_deterministica() -> None:
    """Duas políticas idênticas têm de dar o mesmo número.

    O aceite entra como peso, não como sorteio — sem isso, comparar políticas
    exigiria distinguir diferença real de ruído de Monte Carlo.
    """
    propostas = _propostas_sinteticas()
    ofertas = aplicar_politica(propostas, _politica())
    assert simular(ofertas, "central").roi_anual == simular(ofertas, "central").roi_anual


# --- Guard-rails -------------------------------------------------------------
def test_violacao_de_teto_de_taxa_e_detectada() -> None:
    propostas = _propostas_sinteticas()
    r = simular(aplicar_politica(propostas, _politica(taxa=0.05)), "central")
    assert any("taxa" in v for v in r.violacoes)


def test_violacao_de_aprovacao_minima_e_detectada() -> None:
    """Aprovar pouco corta a nota de política pela metade.

    A carteira precisa ser MISTA: se ninguém for aprovado, o motor cai no
    caminho da carteira vazia e reporta outra violação.
    """
    boas = _propostas_sinteticas(n=20, pd_valor=0.01)  # score 10
    ruins = _propostas_sinteticas(n=180, pd_valor=0.20)  # score 3
    propostas = pd.concat([boas, ruins], ignore_index=True)

    r = simular(aplicar_politica(propostas, _politica(corte=10)), "central")
    assert r.taxa_aprovacao == pytest.approx(0.10)
    assert any("aprovação" in v for v in r.violacoes)


def test_guard_rails_batem_com_o_enunciado() -> None:
    assert GUARD_RAILS["aprovacao_minima"] == 0.35
    assert GUARD_RAILS["taxa_maxima"] == 0.035
    assert GUARD_RAILS["inadimplencia_maxima"] == 0.08
    assert GUARD_RAILS["volume_minimo"] == 40_000_000


def test_taxa_de_mercado_vem_da_base_a() -> None:
    """A referência de aceite não é chute: é a média praticada pela política antiga."""
    try:
        base_a = carregar_processada("A")
    except FileNotFoundError as erro:
        pytest.skip(str(erro))
    assert TAXA_MERCADO == pytest.approx(base_a["taxa_juros_am"].mean(), abs=0.0005)


# --- S13.8 · As premissas ficam fixadas por teste ----------------------------
# Foi a ausência disto que deixou `docs/specs/S08_MOTOR_DE_ROI.md` documentar
# nove elasticidades erradas por dias sem ninguém notar: os testes só conferiam
# a ORDENAÇÃO entre os cenários, nunca os valores.


def test_cenarios_submetidos_nao_mudam():
    """Os três cenários são o registro do que foi defendido na banca.

    Alterá-los faz cinco artefatos publicados mentirem de uma vez — deck,
    documento, painel, QA e specs. Premissa nova entra como `Premissas`
    separada, não editando estes números.
    """
    esperado = {
        "otimista": (0.95, 0.8, 1.2, 0.4, 0.2),
        "central": (0.85, 1.5, 2.0, 0.8, 0.5),
        "pessimista": (0.70, 2.5, 3.5, 1.5, 1.0),
    }
    assert set(CENARIOS) == set(esperado)
    for nome, (a0, bt, be, bp, g) in esperado.items():
        c = CENARIOS[nome]
        assert (c.a0, c.beta_taxa, c.beta_entrada, c.beta_prazo, c.gama) == (a0, bt, be, bp, g)


def test_premissas_calibradas_batem_com_a_apuracao():
    """Os valores calibrados em 28/09/2026, contra o que o professor apurou.

    Não são chute: saíram de `recuperacao/28_calibrar_o_aceite.py`. Mudá-los
    exige rodar a calibração de novo e atualizar o PRD § Decisões de modelagem,
    porque todo número da recuperação depende deles.
    """
    assert PREMISSAS_CALIBRADAS.taxa_mercado == pytest.approx(0.02021, abs=1e-9)
    c = CENARIO_CALIBRADO
    assert c.a0 == pytest.approx(0.837873, abs=1e-6)
    assert c.beta_taxa == pytest.approx(1.185511, abs=1e-6)
    assert c.gama == pytest.approx(1.072320, abs=1e-6)
    # beta_entrada e beta_prazo ficaram fixos no central: com cinco observações
    # não dá para identificar cinco parâmetros.
    assert (c.beta_entrada, c.beta_prazo) == (CENARIOS["central"].beta_entrada,
                                              CENARIOS["central"].beta_prazo)


def test_a_ancora_calibrada_esta_acima_da_submetida():
    """A régua antiga media a AutoCred, não o mercado — causa nº 1 do post-mortem.

    O teste trava a direção: se alguém reverter a âncora para o livro próprio,
    o número volta a cair abaixo do mercado e isto falha.
    """
    assert PREMISSAS_CALIBRADAS.taxa_mercado > PREMISSAS_SUBMETIDAS.taxa_mercado
    assert PREMISSAS_SUBMETIDAS.taxa_mercado == pytest.approx(TAXA_MERCADO)


# --- S13.8 · O elo que não tinha rede ----------------------------------------


def _propostas_em_todas_as_faixas(por_faixa=7) -> pd.DataFrame:
    """Carteira que ocupa as dez faixas, para testar o mapeamento faixa->linha.

    A carteira sintética padrão usa uma PD só, então todo mundo cai na mesma
    faixa — e um erro de mapeamento não teria como aparecer.
    """
    pds = []
    for score in range(SCORE_MAXIMO, SCORE_MINIMO - 1, -1):
        lo, hi = faixa_de_score(score)
        hi = min(hi, 0.95)
        pds.extend(np.linspace(lo + 1e-4, hi - 1e-4, por_faixa))
    n = len(pds)
    return pd.DataFrame(
        {
            "pd": np.array(pds),
            "valor_bem": np.full(n, 50_000.0),
            "pct_entrada_desejada": np.full(n, 0.10),
            "valor_financiado_desejado": np.full(n, 45_000.0),
            "prazo_desejado_meses": np.full(n, 48),
            "idade_veiculo_anos": np.full(n, 3),
            "possui_avalista": np.array(["Não"] * n),
        }
    )


def _politica_com_valores_distintos():
    """Uma tabela em que cada faixa tem taxa, prazo e entrada DIFERENTES.

    A fixture que existia antes era **plana** — mesma taxa, prazo e entrada em
    toda faixa. Com ela, um off-by-one no mapeamento faixa→linha produz saída
    idêntica e os testes passam. Era o único elo da cadeia sem rede, e é o que
    alimenta o `simular`.
    """
    linhas = []
    for score in range(10, 0, -1):
        aprovada = score >= 5
        linhas.append({
            "score": score,
            "decisao": "APROVAR" if aprovada else "NEGAR",
            # valores propositalmente distintos e crescentes com o risco
            "taxa_am": 0.010 + 0.002 * (10 - score) if aprovada else np.nan,
            "prazo_meses": float(60 - 2 * (10 - score)) if aprovada else np.nan,
            "pct_entrada_minima": 0.05 + 0.01 * (10 - score) if aprovada else np.nan,
        })
    return pd.DataFrame(linhas)


def test_aplicar_politica_mapeia_cada_faixa_na_linha_certa():
    """Cada proposta recebe as condições da SUA faixa, não das vizinhas.

    Um off-by-one no `map` por score — ou um `set_index` na coluna errada —
    atribuiria a linha vizinha e passaria despercebido com tabela plana.
    """
    politica = _politica_com_valores_distintos()
    ofertas = aplicar_politica(_propostas_em_todas_as_faixas(), politica)
    regras = politica.set_index("score")

    for score in ofertas["score"].unique():
        sel = ofertas[ofertas["score"] == score]
        for coluna in ("taxa_am", "prazo_meses", "pct_entrada_minima"):
            esperado = regras.loc[score, coluna]
            obtido = sel[coluna].to_numpy(dtype=float)
            if np.isnan(esperado):
                assert np.isnan(obtido).all(), f"faixa {score}, {coluna}"
            else:
                assert np.allclose(obtido, esperado), (
                    f"faixa {score}: {coluna} deveria ser {esperado}, veio {obtido[:3]}"
                )


def test_aplicar_politica_nao_embaralha_scores():
    """O score de cada linha continua sendo o da PD daquela linha.

    É a dobradiça entre o modelo e a política: se ela escorregar, todo o resto
    fica internamente coerente e errado em relação ao risco.
    """
    ofertas = aplicar_politica(
        _propostas_em_todas_as_faixas(), _politica_com_valores_distintos()
    )
    assert np.array_equal(
        ofertas["score"].to_numpy(), score_de_pd(ofertas["pd"])
    )
