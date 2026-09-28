# Fontes externas — procedência do dado que não veio do professor

> **Por que este documento existe:** o desafio foi entregue com três bases e um arquivo de parâmetros. Qualquer número que **não** venha dali é dado externo, e dado externo sem procedência não é verificável — é opinião com casas decimais.
>
> **A regra:** nenhum número externo entra em script ou documento sem uma linha aqui, com **fonte, identificador, período e data de extração**. Quem ler o repositório daqui a seis meses tem de conseguir baixar o mesmo arquivo e obter o mesmo valor.
>
> **Onde o arquivo mora:** `dados/externos/`, com a mesma regra de `dados/brutos/` — **somente leitura**, nunca editado à mão, fora do git (regra crítica 1). O que é versionado é este manifesto.

## Por que passamos a usar dado externo

Até a apuração do desafio, o projeto media "preço acima do mercado" contra a **média do próprio livro da AutoCred** (`TAXA_MERCADO = 0.0159`, de `banking/roi.py`). Isso mede a AutoCred, não o mercado.

O grupo vencedor comparou a taxa proposta com **dados públicos do Banco Central** e mostrou onde ela caía na distribuição das instituições. O professor registrou como diferencial: *"fez o que nenhum outro fez… preço defensável, não arbitrado."*

A decisão está registrada em [`processo/PRD.md § Decisões de modelagem`](processo/PRD.md#decisões-de-modelagem) — **D1** —, incluindo a razão pela qual a referência externa havia sido recusada antes, e por que estava errada.

## Fontes registradas

| # | Fonte | Identificador | Período | Extraído em | Usada em |
| - | ----- | ------------- | ------- | ----------- | -------- |
| | *(a preencher pelo `recuperacao/27_ancora_de_mercado.py`)* | | | | |

### Como preencher

Cada linha ganha, abaixo da tabela, uma seção com:

- **URL exata** da consulta ou do endpoint, reproduzível por quem ler;
- **o que a série mede** — modalidade, tipo de pessoa, encargo incluído (taxa nominal, CET, pré ou pós-fixado);
- **o recorte usado** e por quê (mediana, quartis, média ponderada);
- **a data de extração**, porque série revisada muda valor sem avisar;
- **o número que entrou no código**, para conferência direta.

> ⚠️ **Série revisada é armadilha silenciosa.** O BCB republica séries com correções. Sem a data de extração registrada, um número que não reproduz vira discussão sobre quem digitou errado — quando a explicação é que a fonte mudou.

## O que **não** entra aqui

- **Dado do professor** (bases A/B/C, parâmetros de EAD/LGD): não é externo, é insumo do desafio. Está descrito em [`DICIONARIO_DADOS.md`](DICIONARIO_DADOS.md).
- **Número lembrado, estimado ou citado de memória.** Se não há URL e data, não entra — nem no código, nem em documento, nem em slide.
