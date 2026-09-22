"""S04.6 · Testes do pipeline de modelagem.

O foco é o que a rubrica cobra e o que não dá erro sozinho: vazamento de
pré-processamento, categoria desconhecida na escoragem, e falta de
reprodutibilidade. Nenhum desses três levanta exceção — os dois primeiros
produzem um número bonito e errado, e o terceiro só aparece quando alguém
tenta repetir o resultado.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from banking.dados import ALVO, COLUNAS_PROIBIDAS, carregar_processada
from banking.modelo import (
    PREDITORAS_DEPENDENTES_DE_POLITICA,
    avaliar,
    coeficientes,
    construir_pipeline,
    preditoras,
)
from banking.split import dividir_temporal


@pytest.fixture(scope="module")
def particoes():
    try:
        base_a = carregar_processada("A")
    except FileNotFoundError as erro:
        pytest.skip(str(erro))
    return dividir_temporal(base_a)


@pytest.fixture(scope="module")
def modelo_treinado(particoes):
    treino, _ = particoes
    modelo = construir_pipeline("logistica")
    modelo.fit(treino, treino[ALVO])
    return modelo


# --- O que vale 10 pontos: sem vazamento -------------------------------------
def test_imputacao_aprende_apenas_no_treino(particoes) -> None:
    """A mediana usada na validação tem que ser a do TREINO.

    Se fosse recalculada sobre a validação, a informação dela teria entrado no
    modelo — e o AuROC medido ficaria otimista sem nenhum sinal de erro.
    """
    treino, validacao = particoes
    modelo = construir_pipeline("logistica")
    modelo.fit(treino, treino[ALVO])

    imputador = modelo.named_steps["preparo"].named_transformers_["num"].named_steps["imputar"]
    numericas, _ = preditoras(True)
    mediana_treino = treino[numericas].median().to_numpy()

    assert np.allclose(imputador.statistics_, mediana_treino, equal_nan=True), (
        "a mediana do imputador deveria ser a do treino"
    )


def test_indicador_de_ausencia_esta_presente(modelo_treinado) -> None:
    """A ausência é informação: quem não tem score_bureau quebra 10,1% x 8,8%.

    Imputar sem marcar apagaria esse sinal. O `add_indicator` o preserva.
    """
    nomes = list(modelo_treinado.named_steps["preparo"].get_feature_names_out())
    assert any("missingindicator" in n.lower() for n in nomes), (
        "nenhum indicador de ausência no pipeline"
    )


def test_nenhuma_coluna_proibida_chega_ao_modelo(modelo_treinado) -> None:
    """Rede de segurança: mesmo que a ingestão falhasse, nada proibido entraria."""
    nomes = " ".join(modelo_treinado.named_steps["preparo"].get_feature_names_out())
    for proibida in COLUNAS_PROIBIDAS:
        assert proibida not in nomes, f"{proibida} chegou ao modelo"
    assert ALVO not in nomes, "o alvo entrou como preditora"


def test_taxa_e_parcela_ficam_de_fora(modelo_treinado) -> None:
    """Não existem na base C e codificam a política antiga.

    Um modelo que dependesse delas não conseguiria escorar as propostas — e
    estaria aprendendo a decisão que o conselho considera quebrada.
    """
    nomes = " ".join(modelo_treinado.named_steps["preparo"].get_feature_names_out())
    assert "taxa_juros_am" not in nomes
    assert "parcela_mensal" not in nomes


# --- Robustez na escoragem ---------------------------------------------------
def test_categoria_desconhecida_nao_quebra(particoes, modelo_treinado) -> None:
    """A base C pode trazer categoria que não existe em A.

    Com `handle_unknown="ignore"`, a escoragem continua; sem isso, a submissão
    inteira falharia no dia da entrega.
    """
    _, validacao = particoes
    estranha = validacao.head(5).copy()
    estranha["ocupacao"] = "Categoria Que Nao Existe"
    p = modelo_treinado.predict_proba(estranha)[:, 1]
    assert len(p) == 5 and np.all((p >= 0) & (p <= 1))


def test_nulo_na_escoragem_nao_quebra(particoes, modelo_treinado) -> None:
    _, validacao = particoes
    com_nulo = validacao.head(5).copy()
    com_nulo["score_bureau"] = np.nan
    p = modelo_treinado.predict_proba(com_nulo)[:, 1]
    assert np.all(np.isfinite(p))


# --- Reprodutibilidade -------------------------------------------------------
def test_duas_execucoes_dao_o_mesmo_resultado(particoes) -> None:
    treino, validacao = particoes
    resultados = []
    for _ in range(2):
        modelo = construir_pipeline("logistica")
        modelo.fit(treino, treino[ALVO])
        resultados.append(avaliar(modelo, validacao, "teste", "validação").auroc)
    assert resultados[0] == pytest.approx(resultados[1])


# --- Métricas ----------------------------------------------------------------
def test_gini_e_coerente_com_auroc(particoes, modelo_treinado) -> None:
    _, validacao = particoes
    r = avaliar(modelo_treinado, validacao, "logistica", "validação")
    assert r.gini == pytest.approx(2 * r.auroc - 1)


def test_modelo_ordena_melhor_que_chute(particoes, modelo_treinado) -> None:
    """AuROC de 0,5 é moeda. Abaixo de 0,60 em crédito é sinal de problema."""
    _, validacao = particoes
    r = avaliar(modelo_treinado, validacao, "logistica", "validação")
    assert r.auroc > 0.60
    assert 0.0 < r.ks < 1.0


def test_avaliar_exige_o_alvo(modelo_treinado) -> None:
    """A base B não tem alvo: lá só é possível escorar, não avaliar."""
    try:
        base_b = carregar_processada("B")
    except FileNotFoundError as erro:
        pytest.skip(str(erro))
    with pytest.raises(ValueError, match="não tem o alvo"):
        avaliar(modelo_treinado, base_b, "logistica", "base B")


# --- Interpretabilidade: o insumo da defesa ----------------------------------
def test_sinais_dos_coeficientes_fazem_sentido_de_credito(modelo_treinado) -> None:
    """Sinal invertido denuncia colinearidade ou erro de preparo.

    Mais restrições ativas tem que AUMENTAR a PD; score de bureau maior tem
    que REDUZIR. Se algum sair ao contrário, o modelo está aprendendo ruído —
    e isso apareceria na defesa como pergunta sem resposta.
    """
    coefs = coeficientes(modelo_treinado).set_index("variavel")["coeficiente"]

    assert coefs["num__qtd_restricoes_ativas"] > 0, "mais restrições deveria aumentar a PD"
    assert coefs["num__score_bureau"] < 0, "score de bureau maior deveria reduzir a PD"
    assert coefs["num__prazo_meses"] > 0, "prazo mais longo alonga a exposição ao risco"


# --- A variante independente de política -------------------------------------
def test_variante_independente_remove_a_variavel_circular() -> None:
    numericas_com, _ = preditoras(True)
    numericas_sem, _ = preditoras(False)
    for coluna in PREDITORAS_DEPENDENTES_DE_POLITICA:
        assert coluna in numericas_com
        assert coluna not in numericas_sem


def test_variante_independente_escora_a_base_c(particoes) -> None:
    """O teste que justifica a variante existir.

    A base C não tem `comprometimento_renda`. Um modelo sem essa variável
    escora as 5.000 propostas direto, sem precisar das duas passagens — que é
    a razão de termos declarado a preferência por ela em caso de empate.
    """
    try:
        base_c = carregar_processada("C")
    except FileNotFoundError as erro:
        pytest.skip(str(erro))

    treino, _ = particoes
    modelo = construir_pipeline("logistica", incluir_dependentes_de_politica=False)
    modelo.fit(treino, treino[ALVO])

    # A base C usa nomes "desejados" — renomear é o que o S10 fará de verdade.
    c = base_c.rename(
        columns={
            "ltv_desejado": "ltv",
            "prazo_desejado_meses": "prazo_meses",
            "valor_financiado_desejado": "valor_financiado",
        }
    )
    p = modelo.predict_proba(c)[:, 1]
    assert len(p) == 5_000
    assert np.all((p > 0) & (p < 1))


def test_pd_da_base_c_e_maior_que_a_da_validacao(particoes) -> None:
    """A base C é mar aberto — o modelo precisa refletir isso.

    Se a PD média em C saísse igual ou menor que na validação, seria sinal de
    que o modelo não está enxergando o risco extra da população nova.
    """
    try:
        base_c = carregar_processada("C")
    except FileNotFoundError as erro:
        pytest.skip(str(erro))

    treino, validacao = particoes
    modelo = construir_pipeline("logistica", incluir_dependentes_de_politica=False)
    modelo.fit(treino, treino[ALVO])

    c = base_c.rename(
        columns={
            "ltv_desejado": "ltv",
            "prazo_desejado_meses": "prazo_meses",
            "valor_financiado_desejado": "valor_financiado",
        }
    )
    pd_c = modelo.predict_proba(c)[:, 1].mean()
    pd_val = modelo.predict_proba(validacao)[:, 1].mean()
    assert pd_c > pd_val, f"PD em C ({pd_c:.4f}) deveria superar a da validação ({pd_val:.4f})"


# --- S05 · Desafiantes -------------------------------------------------------
def test_os_tres_modelos_compartilham_o_mesmo_preparo() -> None:
    """A comparação do S05 só é legítima se só o estimador mudar.

    Se o pré-processamento variasse junto, não saberíamos a que atribuir a
    diferença de AuROC — e a conclusão "XGBoost ganha da logística" poderia
    ser, na verdade, "este preparo ganha daquele".
    """
    preparos = {}
    for tipo in ("logistica", "random_forest", "xgboost"):
        preparo = construir_pipeline(tipo).named_steps["preparo"]
        preparos[tipo] = [(nome, cols) for nome, _, cols in preparo.transformers]

    assert preparos["logistica"] == preparos["random_forest"] == preparos["xgboost"]


def test_xgboost_treina_e_escora(particoes) -> None:
    treino, validacao = particoes
    modelo = construir_pipeline("xgboost", incluir_dependentes_de_politica=False)
    modelo.fit(treino, treino[ALVO])
    r = avaliar(modelo, validacao, "xgboost", "validação")
    assert r.auroc > 0.65, "o XGBoost deveria superar o baseline da logística"


def test_tipo_de_modelo_desconhecido_falha_claro() -> None:
    with pytest.raises(ValueError, match="tipo desconhecido"):
        construir_pipeline("rede_neural")


def test_class_weight_balanced_destroi_a_calibracao(particoes) -> None:
    """Achado do S05, travado em teste porque é contraintuitivo.

    `class_weight="balanced"` melhora a ordenação do Random Forest, mas
    reponderar as classes empurra a probabilidade prevista para perto de 0,5 —
    a PD média sai em ~0,42 contra uma taxa real de 7,2%.

    Para **ordenar** isso não atrapalha; para **precificar**, inviabiliza: a
    perda esperada é `PD × EAD × LGD`, e uma PD seis vezes maior que a real
    produziria um preço absurdo. É a razão de o Brier entrar na decisão do
    modelo, e não só o AuROC.
    """
    treino, validacao = particoes

    equilibrado = construir_pipeline(
        "random_forest", incluir_dependentes_de_politica=False, class_weight="balanced"
    )
    equilibrado.fit(treino, treino[ALVO])
    r_eq = avaliar(equilibrado, validacao, "rf_balanced", "validação")

    natural = construir_pipeline("random_forest", incluir_dependentes_de_politica=False)
    natural.fit(treino, treino[ALVO])
    r_nat = avaliar(natural, validacao, "rf", "validação")

    assert r_eq.pd_media > 5 * r_eq.taxa_observada, "a PD reponderada deveria explodir"
    assert r_nat.pd_media < 3 * r_nat.taxa_observada, "sem reponderar, a PD fica no nível certo"
    assert r_eq.brier > r_nat.brier, "reponderar piora a calibração"
