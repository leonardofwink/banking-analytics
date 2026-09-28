"""S08 · Motor de simulação do ROI — o simulador que o professor não deu.

    simular(ofertas, cenario) → ROI anualizado · inadimplência · volume · aprovação

Fórmula oficial do desafio::

    ROI anual = [ (juros recebidos − perda realizada) ÷ volume financiado ] ÷ prazo médio em anos

⚠️ **O que é medido e o que é premissa.** Tudo que vem de tabela do professor ou
do nosso modelo é calculado: parcela, juros, EAD, LGD, distribuição do mês do
default, e o efeito da entrada sobre a PD (via re-escoragem com o LTV ofertado).
O que **não** é revelado — a intensidade do aceite e da seleção adversa — entra
como premissa explícita, em três cenários.

O valor deste motor não é acertar o número do professor: é **comparar políticas
sob a mesma premissa**, e ver quais sobrevivem aos três cenários.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from banking.perda import fator_ead, lgd, tabelas
from banking.price import juros_pagos_ate, juros_totais
from banking.score import score_de_pd

__all__ = [
    "CENARIOS",
    "Cenario",
    "GUARD_RAILS",
    "PREMISSAS_SUBMETIDAS",
    "Premissas",
    "Resultado",
    "TAXA_MERCADO",
    "aplicar_politica",
    "premissas_do_modulo",
    "simular",
]

# Taxa média praticada pela política antiga na base A — a melhor proxy do preço
# que o cliente encontra no concorrente. Não é chute: é dado.
#
# O achado que a acompanha: a política antiga cobrava 1,57% do score 10 e 1,64%
# do score 1, para riscos de 0,2% e 69,6% de default. Sete pontos-base separando
# tudo isso. É o diagnóstico do conselho em números — e a razão de o teto de
# 3,5% a.m. NÃO ser a restrição que morde: quem limita o preço é o aceite do
# cliente, não o CET regulatório.
TAXA_MERCADO = 0.0159

GUARD_RAILS = {
    "aprovacao_minima": 0.35,
    "taxa_maxima": 0.035,
    "inadimplencia_maxima": 0.08,
    "volume_minimo": 40_000_000.0,
}


@dataclass(frozen=True)
class Cenario:
    """Premissas sobre como a base C reage — a parte que não é revelada.

    :param a0: aceite na condição de referência (taxa de mercado, sem entrada
        extra, prazo pedido).
    :param beta_taxa: quanto o aceite cai por unidade de excesso de taxa.
    :param beta_entrada: idem, por ponto de entrada exigido acima do desejado.
    :param beta_prazo: idem, por redução relativa do prazo pedido.
    :param gama: seleção adversa — quanto a PD sobe por unidade de excesso de
        taxa. Quem aceita pagar caro costuma ser quem não tem alternativa.
    """

    nome: str
    a0: float
    beta_taxa: float
    beta_entrada: float
    beta_prazo: float
    gama: float


# Os três cenários bracketam a premissa. Como a submissão é única e a
# intensidade real é desconhecida, a política escolhida tem de sobreviver aos
# três — não ser ótima no central.
#
# ⚠️ CALIBRAÇÃO REVISADA (S09). A primeira versão usava beta_taxa de 1,5/3,0/5,0
# e a busca degenerou: 896 das 960 políticas morriam por volume, e a vencedora
# era PREÇO ÚNICO para todo risco — exatamente a patologia que o conselho
# diagnosticou na política antiga. Isso é sintoma de premissa errada, não de
# política certa.
#
# A âncora que corrigiu: o professor impôs um TETO de 3,5% a.m. como guard-rail.
# Um teto só é guard-rail se as políticas quiserem chegar perto dele. Se o
# aceite morresse a 2%, o teto seria decorativo — ninguém o alcançaria. A
# existência do teto implica que o simulador permite operar bem acima do
# mercado, e as elasticidades foram recalibradas para que cobrar no teto deixe
# um aceite baixo mas não nulo (16% do nível de referência, no central).
CENARIOS = {
    "otimista": Cenario("otimista", a0=0.95, beta_taxa=0.8, beta_entrada=1.2, beta_prazo=0.4, gama=0.2),
    "central": Cenario("central", a0=0.85, beta_taxa=1.5, beta_entrada=2.0, beta_prazo=0.8, gama=0.5),
    "pessimista": Cenario("pessimista", a0=0.70, beta_taxa=2.5, beta_entrada=3.5, beta_prazo=1.5, gama=1.0),
}


@dataclass(frozen=True)
class Premissas:
    """As suposições sobre o mundo que o simulador não mede — juntas e com nome.

    ``TAXA_MERCADO`` e ``CENARIOS`` nasceram como constantes de módulo. Quem
    chamava :func:`simular` não precisava declará-las, e por isso ninguém as
    questionou: o desafio de 2026 foi perdido por uma delas estar errada, e o
    diagnóstico está em ``docs/processo/POST_MORTEM.md``.

    Agrupá-las num objeto nomeado não muda nenhum número — muda o fato de que
    **usar uma premissa passa a ser uma escolha explícita**.

    :param nome: identifica o conjunto nos relatórios. Aparece ao lado de todo
        número que dependa dele.
    :param taxa_mercado: o preço que o cliente encontraria no concorrente. É o
        denominador do excesso de taxa, e portanto a régua contra a qual "caro"
        é medido. Ver ``docs/GLOSSARIO.md`` § âncora de preço.
    :param cenarios: as elasticidades, por nome de cenário.
    """

    nome: str
    taxa_mercado: float
    cenarios: dict[str, Cenario]


def premissas_do_modulo() -> Premissas:
    """As premissas tal como o módulo as declara **neste instante**.

    Lê :data:`TAXA_MERCADO` e :data:`CENARIOS` na chamada, em vez de capturá-los
    na importação. É o que preserva o comportamento de
    ``analises/21_premissa_de_aceite.py`` e ``modelagem/13_alavancas_de_volume.py``,
    que injetam cenários extras reatribuindo ``roi.CENARIOS`` em tempo de execução.

    **Código novo não deve depender disto**: construa um :class:`Premissas` e
    passe-o a :func:`simular`. Este acessor existe para que a introdução do
    parâmetro não altere nada do que já roda.
    """
    return Premissas("submetidas", TAXA_MERCADO, CENARIOS)


#: O que foi efetivamente submetido ao professor em 25/09/2026. Imutável: serve
#: de linha de base para qualquer comparação com premissas recalibradas.
PREMISSAS_SUBMETIDAS = Premissas("submetidas", TAXA_MERCADO, CENARIOS)


@dataclass
class Resultado:
    """O que o conselho vai olhar, mais o que explica o número."""

    cenario: str
    roi_anual: float
    inadimplencia: float
    volume_originado: float
    taxa_aprovacao: float
    contratos_esperados: float
    taxa_aceite_media: float
    prazo_medio_anos: float
    juros_recebidos: float
    perda_realizada: float
    violacoes: list[str] = field(default_factory=list)

    @property
    def dentro_dos_guard_rails(self) -> bool:
        return not self.violacoes

    def como_linha(self) -> dict:
        return {
            "cenario": self.cenario,
            "roi_anual": self.roi_anual,
            "inadimplencia": self.inadimplencia,
            "volume_mi": self.volume_originado / 1e6,
            "aprovacao": self.taxa_aprovacao,
            "contratos": self.contratos_esperados,
            "aceite_medio": self.taxa_aceite_media,
            "prazo_anos": self.prazo_medio_anos,
            "violacoes": " · ".join(self.violacoes) if self.violacoes else "—",
        }


def aplicar_politica(
    propostas: pd.DataFrame, politica: pd.DataFrame, escorar=None
) -> pd.DataFrame:
    """Traduz cada proposta na oferta que a política faz a ela.

    A entrada efetiva é o **máximo** entre a que o cliente ofereceu e a que
    exigimos — ninguém é obrigado a dar menos do que queria. Com ela mudam o
    LTV e o valor financiado, e com o LTV muda a PD.

    **O efeito da entrada sobre a PD é medido, não assumido:** se ``escorar``
    for fornecida, a PD é recalculada com o LTV ofertado. É a segunda passagem
    prevista desde o S01 — e é o que permite dizer *quanto* de risco a entrada
    compra, em vez de supor.

    :param propostas: base C, com ``pd`` já escorada nas condições desejadas.
    :param politica: indexada por ``score``, com ``decisao``, ``taxa_am``,
        ``prazo_meses`` e ``pct_entrada_minima``.
    :param escorar: callable que recebe o DataFrame ajustado e devolve a PD.
    :return: uma linha por proposta, com a oferta e a economia de cada uma.
    """
    obrigatorias = {"decisao", "taxa_am", "prazo_meses", "pct_entrada_minima"}
    faltando = obrigatorias - set(politica.columns)
    if faltando:
        raise ValueError(f"política sem as colunas {sorted(faltando)}")

    o = propostas.copy()
    o["score"] = score_de_pd(o["pd"])

    regras = politica.set_index("score") if "score" in politica.columns else politica
    for coluna in ("decisao", "taxa_am", "prazo_meses", "pct_entrada_minima"):
        o[coluna] = o["score"].map(regras[coluna])

    o["aprovada"] = o["decisao"].astype(str).str.upper().eq("APROVAR")

    # Entrada efetiva: o cliente nunca dá menos do que já queria dar.
    o["pct_entrada_efetiva"] = np.maximum(
        o["pct_entrada_desejada"].to_numpy(), o["pct_entrada_minima"].to_numpy()
    )
    o["entrada_extra"] = o["pct_entrada_efetiva"] - o["pct_entrada_desejada"]
    o["valor_financiado_ofertado"] = o["valor_bem"] * (1.0 - o["pct_entrada_efetiva"])
    o["ltv_ofertado"] = 1.0 - o["pct_entrada_efetiva"]

    # Re-escoragem: a entrada muda o LTV, e o LTV é preditora do modelo.
    if escorar is not None:
        ajustada = o.copy()
        ajustada["ltv"] = o["ltv_ofertado"]
        ajustada["valor_financiado"] = o["valor_financiado_ofertado"]
        ajustada["prazo_meses"] = o["prazo_meses"].fillna(o["prazo_desejado_meses"])
        o["pd_ofertada"] = escorar(ajustada)
    else:
        o["pd_ofertada"] = o["pd"]

    return o


def simular(
    ofertas: pd.DataFrame,
    cenario: Cenario | str = "central",
    premissas: Premissas | None = None,
) -> Resultado:
    """Calcula o ROI anualizado da carteira que a política gera.

    :param ofertas: saída de :func:`aplicar_politica`.
    :param cenario: um :class:`Cenario` ou o nome de um cenário das ``premissas``.
    :param premissas: a âncora de preço e as elasticidades. Omitir usa
        :func:`premissas_do_modulo` — o comportamento histórico, idêntico ao de
        antes deste parâmetro existir. **Código novo passa explicitamente**,
        porque a premissa é a parte do resultado que os dados não sustentam.
    """
    p = premissas if premissas is not None else premissas_do_modulo()
    c = p.cenarios[cenario] if isinstance(cenario, str) else cenario

    aprovadas = ofertas[ofertas["aprovada"]].copy()
    taxa_aprovacao = len(aprovadas) / max(len(ofertas), 1)

    if aprovadas.empty:
        return Resultado(
            cenario=c.nome, roi_anual=0.0, inadimplencia=0.0, volume_originado=0.0,
            taxa_aprovacao=0.0, contratos_esperados=0.0, taxa_aceite_media=0.0,
            prazo_medio_anos=0.0, juros_recebidos=0.0, perda_realizada=0.0,
            violacoes=["nenhuma proposta aprovada"],
        )

    taxa = aprovadas["taxa_am"].to_numpy(dtype=float)
    prazo = aprovadas["prazo_meses"].to_numpy(dtype=float)
    principal = aprovadas["valor_financiado_ofertado"].to_numpy(dtype=float)

    # --- reação do cliente (premissa do cenário) ----------------------------
    excesso_taxa = taxa / p.taxa_mercado - 1.0
    encurtamento = np.clip(
        1.0 - prazo / aprovadas["prazo_desejado_meses"].to_numpy(dtype=float), 0.0, 1.0
    )
    aceite = (
        c.a0
        * np.exp(-c.beta_taxa * np.maximum(excesso_taxa, 0.0))
        * np.exp(-c.beta_entrada * aprovadas["entrada_extra"].to_numpy(dtype=float))
        * np.exp(-c.beta_prazo * encurtamento)
    )
    aceite = np.clip(aceite, 0.0, 1.0)

    # Seleção adversa: quem aceita pagar caro costuma ser quem não tem opção.
    pd_efetiva = np.clip(
        aprovadas["pd_ofertada"].to_numpy(dtype=float)
        * (1.0 + c.gama * np.maximum(excesso_taxa, 0.0)),
        0.0,
        1.0,
    )

    # --- economia de cada contrato ------------------------------------------
    # Quem paga até o fim.
    juros_integrais = juros_totais(principal, taxa, prazo)

    # Quem quebra: a receita depende de QUANDO. Média ponderada pela
    # distribuição do mês do default (média 6,9, pico entre o 5º e o 8º mês).
    distribuicao = tabelas().dist_mes_default
    juros_se_quebra = np.zeros_like(principal)
    for mes, frequencia in distribuicao.items():
        meses = np.minimum(float(mes), prazo)  # contrato de 24m não quebra no mês 30
        juros_se_quebra += float(frequencia) * juros_pagos_ate(principal, taxa, prazo, meses)

    perda_por_contrato = (
        fator_ead(prazo, aprovadas["ltv_ofertado"])
        * principal
        * lgd(
            aprovadas["idade_veiculo_anos"],
            aprovadas["ltv_ofertado"],
            aprovadas["possui_avalista"],
        )
    )

    # --- agregação, ponderada pelo aceite -----------------------------------
    # O aceite entra como PESO, não como sorteio: duas políticas idênticas
    # precisam dar exatamente o mesmo número, sem ruído de Monte Carlo.
    juros_esperados = (1.0 - pd_efetiva) * juros_integrais + pd_efetiva * juros_se_quebra
    perda_esperada = pd_efetiva * perda_por_contrato

    juros_total = float(np.sum(aceite * juros_esperados))
    perda_total = float(np.sum(aceite * perda_esperada))
    volume = float(np.sum(aceite * principal))
    contratos = float(np.sum(aceite))
    inadimplencia = float(np.sum(aceite * pd_efetiva) / contratos) if contratos else 0.0
    prazo_medio_anos = (
        float(np.sum(aceite * prazo) / contratos / 12.0) if contratos else 0.0
    )

    roi = (
        (juros_total - perda_total) / volume / prazo_medio_anos
        if volume > 0 and prazo_medio_anos > 0
        else 0.0
    )

    violacoes = []
    if taxa_aprovacao < GUARD_RAILS["aprovacao_minima"]:
        violacoes.append(f"aprovação {taxa_aprovacao:.1%} < 35%")
    if float(np.nanmax(taxa)) > GUARD_RAILS["taxa_maxima"]:
        violacoes.append(f"taxa {np.nanmax(taxa):.2%} > 3,5% a.m.")
    if inadimplencia > GUARD_RAILS["inadimplencia_maxima"]:
        violacoes.append(f"inadimplência {inadimplencia:.1%} > 8%")
    if volume < GUARD_RAILS["volume_minimo"]:
        violacoes.append(f"volume R$ {volume / 1e6:.1f} mi < R$ 40 mi")

    return Resultado(
        cenario=c.nome,
        roi_anual=roi,
        inadimplencia=inadimplencia,
        volume_originado=volume,
        taxa_aprovacao=taxa_aprovacao,
        contratos_esperados=contratos,
        taxa_aceite_media=float(np.mean(aceite)),
        prazo_medio_anos=prazo_medio_anos,
        juros_recebidos=juros_total,
        perda_realizada=perda_total,
        violacoes=violacoes,
    )
