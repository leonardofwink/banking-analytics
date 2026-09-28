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
| 1 | BCB · Olinda / taxaJuros | modalidade **401101** | 2025-07-01 a 2025-12-31 | 2026-09-28 | `recuperacao/27_ancora_de_mercado.py` |
| 2 | BCB · SGS | série **20749** | jul a dez/2025 | 2026-09-28 | idem |

### 1 · Taxa por instituição — a distribuição

```
https://olinda.bcb.gov.br/olinda/servico/taxaJuros/versao/v2/odata/TaxasJurosDiariaPorInicioPeriodo
  $filter = Modalidade eq 'Aquisição de veículos - Prefixado'
            and InicioPeriodo ge '2025-07-01' and InicioPeriodo le '2025-12-31'
```

**O que mede:** taxa de juros **prefixada**, ao mês, cobrada por cada instituição em operações de **aquisição de veículos** para **pessoa física** — a mesma operação da AutoCred. O período é semanal, e a consulta cobre exatamente o intervalo da Base C.

**O recorte:** 5.346 observações, **53 instituições**, 130 semanas.

| | % a.m. |
| - | ------ |
| p5 | 1,050 |
| p25 | 1,440 |
| **mediana** | **1,820** |
| p75 | 2,120 |
| p95 | 3,150 |
| máximo | 3,590 |

**Ressalva registrada:** 53 observações (1,0%) ficam abaixo de 0,30% a.m. — taxa promocional de banco de montadora, não preço de crédito. Excluí-las move a mediana de 1,820% para 1,830%, então **não** foram excluídas: o efeito é imaterial e apagar dado exige motivo melhor que conveniência.

**Dois detalhes técnicos que custam tempo:** o OData recusa espaço codificado como `+`, então a URL é montada à mão em vez de por `params=`; e a resposta vem com charset mal declarado, então o encoding é forçado para UTF-8 — sem isso todo acento vira `?`.

### 2 · Taxa média do mercado — o nível

```
https://api.bcb.gov.br/dados/serie/bcdata.sgs.20749/dados?formato=json
  dataInicial = 01/07/2025   dataFinal = 31/12/2025
```

**O que mede:** taxa média das operações de crédito com recursos livres, pessoas físicas, aquisição de veículos. Vem em **% ao ano** e é **ponderada por volume**.

**Conversão:** taxa mensal equivalente por juros compostos — `(1 + i_aa)^(1/12) − 1`, não `i_aa / 12`.

**Resultado:** média de **2,021% a.m.** no semestre (27,14% a.a.).

### Por que as duas, e não uma

Respondem perguntas diferentes, e a escolha entre elas é decisão de política, não do script:

| | Responde |
| - | -------- |
| Mediana por instituição — **1,820%** | *"o concorrente típico cobra quanto?"* |
| Média SGS ponderada por volume — **2,021%** | *"o real emprestado no mercado saiu a quanto?"* |

As duas estão **acima** de `TAXA_MERCADO = 1,590%`, que é onde o projeto ancorou. Esse valor cai no **percentil 33** da distribuição: tratamos como preço de mercado algo que só um terço das instituições cobrava ou menos.

### Como preencher uma fonte nova

Cada linha ganha uma seção com: **URL exata** reproduzível; **o que a série mede** (modalidade, tipo de pessoa, pré ou pós-fixado); **o recorte** e por quê; **a data de extração**; e **o número que entrou no código**.

> ⚠️ **Série revisada é armadilha silenciosa.** O BCB republica séries com correções. Sem a data de extração registrada, um número que não reproduz vira discussão sobre quem digitou errado — quando a explicação é que a fonte mudou.

## O que **não** entra aqui

- **Dado do professor** (bases A/B/C, parâmetros de EAD/LGD): não é externo, é insumo do desafio. Está descrito em [`DICIONARIO_DADOS.md`](DICIONARIO_DADOS.md).
- **Número lembrado, estimado ou citado de memória.** Se não há URL e data, não entra — nem no código, nem em documento, nem em slide.
