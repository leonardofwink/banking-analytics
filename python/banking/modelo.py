"""S04 · Construção e avaliação dos modelos de PD.

Todo o pré-processamento vive **dentro do `Pipeline`**. Isso não é organização:
a imputação aprende uma mediana, e se essa mediana for calculada sobre treino +
validação juntos, a validação influenciou o treino e o AuROC medido fica
otimista — sem erro nenhum aparecer. Dentro do `Pipeline`, o ``fit`` acontece só
no treino por construção, e a garantia deixa de depender de disciplina.

É item explícito da rubrica: *"sem vazamento, split correto, Pipeline,
reprodutibilidade"* — 10 pontos.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from banking.dados import ALVO, PREDITORAS_CATEGORICAS, PREDITORAS_NUMERICAS
from banking.metricas import ks
from banking.projeto import SEMENTE

__all__ = [
    "PREDITORAS_DEPENDENTES_DE_POLITICA",
    "Resultado",
    "avaliar",
    "construir_pipeline",
    "preditoras",
]

# Variáveis que só existem depois que a política decide as condições do
# contrato. Existem em A e B (lá o contrato já foi fechado), mas em C teriam de
# ser recalculadas a partir da taxa e do prazo que ofertarmos — o que cria a
# circularidade descrita na spec do entregável 1.
PREDITORAS_DEPENDENTES_DE_POLITICA = ("comprometimento_renda",)

# Nunca entram no modelo:
#   taxa_juros_am, parcela_mensal — não existem na base C E codificam a decisão
#   da política antiga, que é justamente a que o conselho considera quebrada.
# (As colunas pós-concessão já foram removidas na ingestão, no S01.)


def preditoras(incluir_dependentes_de_politica: bool = True) -> tuple[list[str], list[str]]:
    """Devolve ``(numéricas, categóricas)`` a usar no modelo.

    :param incluir_dependentes_de_politica: se ``False``, remove as variáveis
        que só existiriam em C depois de a política decidir.
    """
    numericas = list(PREDITORAS_NUMERICAS)
    if not incluir_dependentes_de_politica:
        numericas = [c for c in numericas if c not in PREDITORAS_DEPENDENTES_DE_POLITICA]
    return numericas, list(PREDITORAS_CATEGORICAS)


def construir_pipeline(
    tipo: Literal["logistica"] = "logistica",
    incluir_dependentes_de_politica: bool = True,
    **parametros,
) -> Pipeline:
    """Monta o pipeline completo: pré-processamento + estimador.

    **Numéricas** recebem imputação pela mediana **com indicador de ausência**
    e padronização. O indicador não é detalhe: o S03 mostrou que quem não tem
    ``score_bureau`` quebra 10,1% contra 8,8% de quem tem. A ausência é
    informação de risco, e imputar sem marcar jogaria esse sinal fora.

    **Categóricas** recebem imputação pela moda e one-hot com
    ``handle_unknown="ignore"`` — uma categoria que apareça só na base C não
    pode derrubar a escoragem.

    :param tipo: por ora só ``"logistica"``; os desafiantes entram no S05.
    :param incluir_dependentes_de_politica: ver :func:`preditoras`.
    :param parametros: repassados ao estimador final.
    """
    numericas, categoricas = preditoras(incluir_dependentes_de_politica)

    trilha_numerica = Pipeline(
        [
            ("imputar", SimpleImputer(strategy="median", add_indicator=True)),
            ("escalar", StandardScaler()),
        ]
    )
    trilha_categorica = Pipeline(
        [
            ("imputar", SimpleImputer(strategy="most_frequent")),
            ("codificar", OneHotEncoder(handle_unknown="ignore", drop="first")),
        ]
    )

    preparo = ColumnTransformer(
        [
            ("num", trilha_numerica, numericas),
            ("cat", trilha_categorica, categoricas),
        ],
        remainder="drop",  # o que não foi declarado não entra: nada passa por engano
    )

    if tipo == "logistica":
        estimador = LogisticRegression(
            max_iter=2_000,
            random_state=SEMENTE,
            **{"C": 1.0, "solver": "lbfgs", **parametros},
        )
    else:
        raise ValueError(f"tipo desconhecido: {tipo!r}")

    return Pipeline([("preparo", preparo), ("modelo", estimador)])


@dataclass
class Resultado:
    """Métricas de um modelo em um conjunto.

    :param auroc: poder de ordenação. 0,5 é chute.
    :param ks: máxima separação entre as acumuladas de bons e maus.
    :param gini: ``2 × AuROC − 1``.
    :param brier: erro quadrático médio da probabilidade — mede **calibração**,
        não ordenação.
    :param pd_media: PD média prevista.
    :param taxa_observada: taxa de default real do conjunto. Comparada à
        ``pd_media``, é a checagem grosseira de calibração: um modelo pode
        ordenar bem e ainda assim errar o nível, e é o nível que vira preço.
    """

    nome: str
    conjunto: str
    n: int
    auroc: float
    ks: float
    gini: float
    brier: float
    pd_media: float
    taxa_observada: float
    extras: dict = field(default_factory=dict)

    @property
    def erro_de_calibracao(self) -> float:
        """Quanto a PD média se afasta da taxa observada, em pontos."""
        return self.pd_media - self.taxa_observada

    def como_linha(self) -> dict:
        return {
            "modelo": self.nome,
            "conjunto": self.conjunto,
            "n": self.n,
            "auroc": self.auroc,
            "ks": self.ks,
            "gini": self.gini,
            "brier": self.brier,
            "pd_media": self.pd_media,
            "taxa_observada": self.taxa_observada,
            "erro_calibracao": self.erro_de_calibracao,
        }


def avaliar(modelo: Pipeline, dados: pd.DataFrame, nome: str, conjunto: str) -> Resultado:
    """Mede um modelo já treinado sobre um conjunto com alvo.

    :param modelo: pipeline treinado.
    :param dados: DataFrame contendo as preditoras e o alvo.
    :param nome: identificação do modelo na tabela comparativa.
    :param conjunto: ``"treino"``, ``"validação"``…
    """
    if ALVO not in dados.columns:
        raise ValueError(
            f"{conjunto!r} não tem o alvo {ALVO!r} — não dá para avaliar. "
            "A base B não tem alvo: lá só é possível escorar."
        )

    y = dados[ALVO].to_numpy()
    p = modelo.predict_proba(dados)[:, 1]

    auroc = float(roc_auc_score(y, p))
    return Resultado(
        nome=nome,
        conjunto=conjunto,
        n=len(dados),
        auroc=auroc,
        ks=ks(y, p),
        gini=2 * auroc - 1,
        brier=float(brier_score_loss(y, p)),
        pd_media=float(np.mean(p)),
        taxa_observada=float(np.mean(y)),
    )


def coeficientes(modelo: Pipeline) -> pd.DataFrame:
    """Coeficientes da logística, com o nome de cada variável transformada.

    É o insumo da defesa: um scorecard precisa justificar variável a variável,
    e o sinal de cada coeficiente tem que fazer sentido de crédito. Mais
    restrições ativas deve **aumentar** a PD; score de bureau maior deve
    **reduzir**. Sinal invertido é sintoma de colinearidade ou de erro de
    preparo — e aparece aqui antes de virar decisão de política.
    """
    preparo = modelo.named_steps["preparo"]
    estimador = modelo.named_steps["modelo"]

    nomes = list(preparo.get_feature_names_out())
    coefs = estimador.coef_.ravel()

    tabela = pd.DataFrame({"variavel": nomes, "coeficiente": coefs})
    tabela["abs"] = tabela["coeficiente"].abs()
    tabela["direcao"] = np.where(tabela["coeficiente"] > 0, "aumenta a PD", "reduz a PD")
    return tabela.sort_values("abs", ascending=False).drop(columns="abs").reset_index(drop=True)
