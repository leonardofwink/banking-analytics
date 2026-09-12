"""``banking`` — biblioteca interna do projeto Banking Analytics.

Aqui moram **funções reutilizáveis**: cálculo de WOE/IV, métricas de
discriminação (KS, Gini), perda esperada, binning, validação. É o equivalente
Python da pasta ``R/``.

Regras (ver ``AGENTS.md``):

- Funções **puras e testáveis**: nada roda ao importar, nada lê nem escreve
  arquivo, nada imprime. Pipeline que lê, escreve e loga vive em ``python/etl/``,
  ``python/modelagem/`` e ``python/relatorios/``.
- A única exceção é :mod:`banking.projeto`, a âncora — ela resolve caminhos e
  cria os diretórios de dados, por definição.
- Toda função de crédito documenta a **convenção de unidade**: PD e LGD em
  fração (0–1), nunca em 0–100; EAD em reais.
"""

__all__ = ["projeto"]
