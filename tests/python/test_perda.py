"""S02.7 · Testes da perda esperada.

Dois grupos: os que travam a **convenção de unidade** (o erro mais comum em
crédito, que não levanta exceção sozinho) e os que conferem as funções contra
o **gabarito** — os 826 contratos da base A que realmente deram default.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from banking.dados import ALVO, FAIXAS_IDADE_VEICULO, FAIXAS_LTV, carregar_bruto
from banking.perda import (
    AJUSTE_AVALISTA,
    ead,
    faixa_idade_veiculo,
    faixa_ltv,
    fator_ead,
    lgd,
    perda_esperada,
    tabelas,
)


@pytest.fixture(scope="module")
def inadimplentes() -> pd.DataFrame:
    """Os 826 contratos da base A com default — o gabarito do S02."""
    try:
        base = carregar_bruto("A")
    except FileNotFoundError as erro:
        pytest.skip(str(erro))
    d = base[base[ALVO] == 1].copy()
    d["faixa_ltv"] = faixa_ltv(d["ltv"])
    d["faixa_idade_veiculo"] = faixa_idade_veiculo(d["idade_veiculo_anos"])
    d["fator_realizado"] = d["ead_realizado"] / d["valor_financiado"]
    return d


# --- Tabelas -----------------------------------------------------------------
def test_tabelas_tem_o_formato_esperado() -> None:
    t = tabelas()
    assert t.fator_ead.shape == (4, 5), "4 prazos x 5 faixas de LTV"
    assert t.lgd.shape == (4, 5), "4 idades x 5 faixas de LTV"
    assert list(t.fator_ead.columns) == list(FAIXAS_LTV)
    assert list(t.lgd.index) == list(FAIXAS_IDADE_VEICULO)


def test_distribuicao_do_mes_de_default_soma_um() -> None:
    """É uma distribuição de probabilidade: o motor de ROI (S08) depende disso."""
    t = tabelas()
    assert t.dist_mes_default.sum() == pytest.approx(1.0, abs=1e-6)
    assert len(t.dist_mes_default) == 12


# --- Faixas ------------------------------------------------------------------
def test_faixa_ltv_e_fechada_a_direita() -> None:
    """`até 60%` inclui exatamente 0,60; 0,601 já cai na faixa seguinte."""
    assert faixa_ltv([0.60])[0] == "até 60%"
    assert faixa_ltv([0.601])[0] == "60% a 70%"
    assert faixa_ltv([0.70])[0] == "60% a 70%"
    assert faixa_ltv([0.90])[0] == "80% a 90%"
    assert faixa_ltv([0.901])[0] == "acima de 90%"


def test_faixa_ltv_rejeita_percentual() -> None:
    """LTV em 0–100 em vez de 0–1 é erro silencioso: todo mundo cairia em >90%."""
    with pytest.raises(ValueError, match="percentual"):
        faixa_ltv([78.0])


def test_faixa_idade_veiculo() -> None:
    assert faixa_idade_veiculo([0])[0] == "0 a 2 anos", "0 = zero quilômetro"
    assert faixa_idade_veiculo([2])[0] == "0 a 2 anos"
    assert faixa_idade_veiculo([3])[0] == "3 a 5 anos"
    assert faixa_idade_veiculo([9])[0] == "9 anos ou mais"
    assert faixa_idade_veiculo([25])[0] == "9 anos ou mais"


def test_faixas_classificam_toda_a_base(inadimplentes) -> None:
    assert not pd.isna(inadimplentes["faixa_ltv"]).any()
    assert not pd.isna(inadimplentes["faixa_idade_veiculo"]).any()


# --- EAD ---------------------------------------------------------------------
def test_fator_ead_fica_na_faixa_plausivel(inadimplentes) -> None:
    """Entre 0,98 e 1,05: passa de 1 porque soma as 3 parcelas vencidas."""
    f = fator_ead(inadimplentes["prazo_meses"], inadimplentes["ltv"])
    assert f.min() >= 0.97 and f.max() <= 1.05


def test_fator_ead_rejeita_prazo_fora_da_tabela() -> None:
    with pytest.raises(KeyError, match="Prazo"):
        fator_ead([42], [0.75])


def test_ead_sai_em_reais() -> None:
    """EAD é dinheiro, não fração — o erro de unidade mais caro do módulo."""
    valor = ead([10_000.0], [36], [0.75])[0]
    assert 9_500 < valor < 10_500, f"EAD de R$10k deveria ficar perto disso, veio {valor}"


def test_fator_ead_bate_com_o_gabarito_por_celula(inadimplentes) -> None:
    """Média por célula, não linha a linha: a tabela é uma média."""
    obs = inadimplentes.pivot_table(
        index="prazo_meses", columns="faixa_ltv", values="fator_realizado", aggfunc="mean"
    )
    esperado = tabelas().fator_ead.loc[obs.index, obs.columns]
    assert (obs - esperado).abs().to_numpy().mean() < 0.005


# --- LGD ---------------------------------------------------------------------
def test_lgd_fica_entre_zero_e_um(inadimplentes) -> None:
    valores = lgd(
        inadimplentes["idade_veiculo_anos"],
        inadimplentes["ltv"],
        inadimplentes["possui_avalista"],
    )
    assert valores.min() >= 0.0 and valores.max() <= 1.0


def test_lgd_cresce_com_o_risco() -> None:
    """Carro novo com LTV baixo recupera muito melhor que carro velho alavancado.

    É essa amplitude — 0,412 a 0,908 — que faz da entrada mínima a alavanca
    mais forte da política.
    """
    melhor = lgd([1], [0.50])[0]
    pior = lgd([12], [0.95])[0]
    assert melhor == pytest.approx(0.412)
    assert pior == pytest.approx(0.908)
    assert pior - melhor > 0.45


def test_lgd_bate_com_o_gabarito_por_celula(inadimplentes) -> None:
    """Sem ajuste de avalista: a tabela é a média de todos da célula."""
    obs = inadimplentes.pivot_table(
        index="faixa_idade_veiculo", columns="faixa_ltv", values="lgd_realizado", aggfunc="mean"
    )
    esperado = tabelas().lgd.loc[obs.index, obs.columns]
    assert (obs - esperado).abs().to_numpy().mean() < 0.001


def test_avalista_reduz_a_lgd() -> None:
    com = lgd([4], [0.85], ["Sim"])[0]
    sem = lgd([4], [0.85], ["Não"])[0]
    assert com == pytest.approx(sem + AJUSTE_AVALISTA)


def test_modo_oficial_e_o_padrao() -> None:
    """Coerência com o enunciado vale 10 pontos: o padrão é o parâmetro declarado."""
    padrao = lgd([4], [0.85], ["Sim"])[0]
    oficial = lgd([4], [0.85], ["Sim"], modo="oficial")[0]
    assert padrao == oficial


def test_modo_centrado_corrige_o_vies(inadimplentes) -> None:
    """A regra oficial subestima a perda; a centrada não.

    A tabela já mistura contratos com e sem avalista, então aplicar −0,061
    apenas sobre os com avalista conta o benefício duas vezes. Ver
    docs/DEBITO_TECNICO.md § 5.
    """
    real = inadimplentes["lgd_realizado"].to_numpy()
    args = (
        inadimplentes["idade_veiculo_anos"],
        inadimplentes["ltv"],
        inadimplentes["possui_avalista"],
    )
    vies_oficial = (lgd(*args, modo="oficial") - real).mean()
    vies_centrado = (lgd(*args, modo="centrado") - real).mean()

    assert vies_oficial < -0.005, "o viés conhecido da regra oficial sumiu?"
    assert abs(vies_centrado) < abs(vies_oficial), "o modo centrado deveria reduzir o viés"
    assert abs(vies_centrado) < 0.002


def test_modo_invalido_falha() -> None:
    with pytest.raises(ValueError, match="modo inválido"):
        lgd([4], [0.85], ["Sim"], modo="chute")


# --- Perda esperada ----------------------------------------------------------
def test_perda_esperada_e_pd_vezes_ead_vezes_lgd() -> None:
    p, valor, prazo, ltv, idade = 0.085, 10_000.0, 48, 0.75, 4
    esperado = p * ead([valor], [prazo], [ltv])[0] * lgd([idade], [ltv])[0]
    assert perda_esperada([p], [valor], [prazo], [ltv], [idade])[0] == pytest.approx(esperado)


def test_perda_esperada_rejeita_pd_em_percentual() -> None:
    """`8.5` em vez de `0.085` daria uma perda 100x maior, sem erro nenhum."""
    with pytest.raises(ValueError, match="percentual"):
        perda_esperada([8.5], [10_000.0], [48], [0.75], [4])


def test_perda_esperada_na_ordem_de_grandeza_do_professor() -> None:
    """A tabela ilustrativa do enunciado dá ~6% do financiado para PD de 8,5%."""
    valor = 10_000.0
    el = perda_esperada([0.085], [valor], [48], [0.75], [4], ["Não"])[0]
    assert 0.04 < el / valor < 0.08


def test_pd_zero_nao_gera_perda() -> None:
    assert perda_esperada([0.0], [10_000.0], [48], [0.75], [4])[0] == 0.0


# --- S13.8 · A receita da perda por faixa, num lugar só ----------------------


def test_perda_por_faixa_reproduz_o_que_foi_submetido():
    """Os valores que a política submetida usou para precificar.

    A receita estava replicada em **20 arquivos**. Trocar a base, a coluna de
    LTV ou o modo de avalista em um deles produzia um preço diferente sem nada
    acusar — vão G4 do post-mortem. Estes números são os publicados no deck e
    no documento de política.
    """
    from banking.dados import carregar_processada, preparar_base_c
    from banking.modelo import treinar_modelo_final
    from banking.perda import perda_por_faixa

    modelo = treinar_modelo_final(carregar_processada("A"))
    propostas = preparar_base_c(carregar_processada("C")).reset_index(drop=True)
    propostas["pd"] = modelo.predict_proba(propostas)[:, 1]

    esperado = {10: 0.013435, 9: 0.020703, 8: 0.029242, 7: 0.040740,
                6: 0.057715, 5: 0.079232, 4: 0.111836, 3: 0.156135,
                2: 0.212813, 1: 0.333055}
    obtido = perda_por_faixa(propostas)
    assert set(obtido) == set(esperado)
    for score, valor in esperado.items():
        assert obtido[score] == pytest.approx(valor, abs=1e-6), f"faixa {score}"


def test_perda_por_faixa_exige_as_colunas_que_usa():
    """Faltando coluna, erro claro — não um KeyError no meio do cálculo."""
    from banking.perda import perda_por_faixa

    with pytest.raises(ValueError, match="preparar_base_c"):
        perda_por_faixa(pd.DataFrame({"pd": [0.05, 0.10]}))


def test_perda_por_faixa_cresce_com_o_risco():
    """Faixa pior perde mais. Se isto inverter, o preço inverte junto."""
    from banking.dados import carregar_processada, preparar_base_c
    from banking.modelo import treinar_modelo_final
    from banking.perda import perda_por_faixa

    modelo = treinar_modelo_final(carregar_processada("A"))
    propostas = preparar_base_c(carregar_processada("C")).reset_index(drop=True)
    propostas["pd"] = modelo.predict_proba(propostas)[:, 1]

    por_faixa = perda_por_faixa(propostas)
    valores = [por_faixa[s] for s in sorted(por_faixa, reverse=True)]
    assert valores == sorted(valores), "perda esperada não é monótona no score"
