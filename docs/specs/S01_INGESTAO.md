# S01 · Ingestão e contrato de dados

> Passo 1 de 11 do [`ROADMAP.md`](../ROADMAP.md). **Não depende de nada e bloqueia tudo.**
>
> ✅ **CONCLUÍDO em 2026-09-14.** DoD verificado item a item; 28 testes verdes. Implementação em [`python/banking/dados.py`](../../python/banking/dados.py), [`python/etl/01_ingestao.py`](../../python/etl/01_ingestao.py) e [`tests/python/test_ingestao.py`](../../tests/python/test_ingestao.py).
> Dados descritos em [`DICIONARIO_DADOS.md`](../DICIONARIO_DADOS.md).

## Status das subetapas

| Subetapa | Entrega | DoD | Status | Commit |
| -------- | ------- | --- | ------ | ------ |
| [S01.1](#s011--contrato-de-dados-constantes) | `banking/dados.py` — constantes e esquemas | 4/4 | ✅ | `4cdcfec` |
| [S01.2](#s012--carga-e-tipagem) | `carregar_bruto(base)` | 4/4 | ✅ | `4cdcfec` |
| [S01.3](#s013--separação-preditoras-alvo-e-realizados) | `carregar()` · `carregar_realizados()` | 6/6 | ✅ | `4cdcfec` |
| [S01.4](#s014--validação-de-esquema) | `validar(df, base)` | 3/3 | ✅ | `4cdcfec` |
| [S01.5](#s015--gravação-em-parquet) | `gravar_parquet()` + 4 arquivos | 4/4 | ✅ | `4cdcfec` |
| [S01.6](#s016--testes) | `tests/python/test_ingestao.py` | 2/2 | ✅ | `4cdcfec` |
| [S01.7](#s017--pipeline-orquestrador) | `python/etl/01_ingestao.py` | 3/3 | ✅ | `4cdcfec` |
| **Passo** | **DoD do S01** | **8/8** | **✅** | `e15d1f0` |

**Verificações que fecharam o passo:** 28 testes verdes · 10.000/3.000/5.000 linhas · 23/22/20 colunas · zero colunas proibidas · nulos preservados (770/1.207/327) · R lê `2022-01-01` como `Date` sem deslocamento · pipeline idempotente (md5 igual em duas execuções) · `git status` limpo de dados · **proteção removida de propósito derrubou 4 testes**, incluindo o dedicado à armadilha.

## Objetivo

Ter as três bases carregadas, limpas das colunas proibidas, com os tipos corretos e gravadas em Parquet — e um teste que **falha** se a armadilha escapar.

## Por que este passo existe

Duas razões, e a segunda é a que importa.

**A primeira é banal:** tudo depois depende de a base estar certa.

**A segunda é a que salva 30 pontos:** a remoção das colunas proibidas precisa acontecer **em um lugar só**. Se cada script de modelagem remover por conta própria, alguém vai esquecer — e o esquecimento não dá erro. Ele gera um modelo com AuROC excelente na validação e ~0,5 na avaliação, porque [`qtd_parcelas_em_atraso_12m` vale zero nas bases B e C](../DICIONARIO_DADOS.md#-a-armadilha-qtd_parcelas_em_atraso_12m).

O nome disso é **contrato de dados**: a partir daqui, ninguém no projeto lê CSV. Todo mundo chama `carregar("A")`, e a função garante que o que sai dali é seguro de usar. Quem contornar o contrato está errado por definição.

## ⛔ O que **não** fazemos neste passo

Isto é tão importante quanto o que fazemos:

| Não fazemos | Por quê |
| ----------- | ------- |
| **Imputar os nulos** | Imputação **aprende** com o dado (a média, a mediana). Se aprender aqui, aprende com as três bases juntas — e a média da validação vaza para o treino. Tem que estar dentro do `Pipeline`, ajustada só no treino. É item explícito da nota (10 pts de qualidade técnica) |
| **Codificar as categóricas** | Mesma razão: encoding aprende as categorias existentes. Vai no `Pipeline` |
| **Criar variáveis derivadas** | Feature engineering é decisão de modelagem (S03/S04), não de ingestão. Misturar as duas coisas torna impossível saber onde um número veio a existir |
| **Filtrar linhas** | As bases têm exatamente 10.000 / 3.000 / 5.000 registros e o professor vai cruzar por id. Perder linha aqui quebra a submissão lá na frente |

**A regra geral:** o S01 **conserva** o dado e **remove o proibido**. Nada mais. Toda transformação que aprende alguma coisa fica para o Pipeline.

---

## Subetapas

### S01.1 · Contrato de dados (constantes)

**O que:** criar `python/banking/dados.py` com as constantes do domínio: caminhos dos três arquivos, `COLUNAS_PROIBIDAS`, `ALVO`, as listas de preditoras numéricas e categóricas, e o esquema esperado de cada base (linhas e colunas obrigatórias).

**Por quê:** fonte única. Hoje a lista de proibidas está em três lugares (dicionário do professor, nosso `DICIONARIO_DADOS.md` e a cabeça de quem lembrar). Precisa existir **em código**, num lugar que o teste consiga ler.

**DoD:**
- [x] `from banking.dados import COLUNAS_PROIBIDAS, ALVO` funciona
- [x] `COLUNAS_PROIBIDAS` tem exatamente as 5 colunas pós-concessão que **não** são o alvo: `qtd_parcelas_em_atraso_12m`, `mes_default`, `ead_realizado`, `lgd_realizado`, `perda_financeira`
- [x] `ALVO == "default_90_12"`, declarado separado (é proibido como **preditora**, obrigatório como **alvo**)
- [x] Esquema esperado registrado: A = 10.000 linhas, B = 3.000, C = 5.000

---

### S01.2 · Carga e tipagem

**O que:** função `carregar_bruto(base)` que lê o CSV correspondente e converte `data_originacao` / `data_proposta` para data.

**Por quê:** o `read_csv` traz data como texto. Data como texto ordena errado ("2024-1-5" > "2024-12-31" em ordem alfabética) e impede o split temporal do S03.

**DoD:**
- [x] `carregar_bruto("A" | "B" | "C")` devolve DataFrame com 10.000 / 3.000 / 5.000 linhas
- [x] Coluna de data é tipo data, não texto
- [x] Períodos conferem: A = 2022-01 a 2024-12 · B = 2025-01 a 2025-06 · C = 2025-07 a 2025-12
- [x] **Nulos preservados** — base A com 770 nulos em `renda_mensal_declarada`, 1.207 em `tempo_emprego_meses`, 327 em `score_bureau`

---

### S01.3 · Separação: preditoras, alvo e realizados

**O que:** `carregar(base)` remove as `COLUNAS_PROIBIDAS`, mantendo o alvo na base A. E `carregar_realizados()` devolve, à parte, as colunas de realizado da base A (`mes_default`, `ead_realizado`, `lgd_realizado`, `perda_financeira`) junto do `id_contrato`.

**Por quê — e esta é a sutileza do passo:** "proibido" tem dois sentidos diferentes e confundi-los quebra o projeto de dois jeitos opostos.

- `default_90_12` é proibido **como preditora** (seria prever a resposta com a resposta), mas é **obrigatório como alvo** — sem ele não há o que treinar.
- `ead_realizado` e `lgd_realizado` são proibidos como preditora, mas **não podem ser jogados fora**: o S02 precisa deles para conferir se as tabelas de EAD e LGD do professor foram interpretadas corretamente. É o nosso gabarito.

Por isso eles saem da base de modelagem e vão para um arquivo separado, em vez de sumirem.

**DoD:**
- [x] `carregar("A")` devolve 23 colunas: 22 preditoras/apoio + o alvo
- [x] `carregar("B")` devolve 22 colunas, **sem** o alvo
- [x] `carregar("C")` devolve 20 colunas
- [x] Nenhuma das 5 `COLUNAS_PROIBIDAS` presente em qualquer uma das três
- [x] `carregar_realizados()` devolve 10.000 linhas com `id_contrato` + as 4 colunas de realizado
- [x] Os 826 inadimplentes da base A têm `ead_realizado` preenchido; os adimplentes, nulo

---

### S01.4 · Validação de esquema

**O que:** função `validar(df, base)` que confere contagem de linhas, presença das colunas esperadas, ausência das proibidas e domínio dos valores.

**Por quê:** o professor pode mandar uma correção de base antes do dia 25 (já aconteceu de material vir em duas levas). Se isso ocorrer, queremos que o pipeline **grite** em vez de seguir silenciosamente com uma base diferente. Validação de esquema é o alarme.

Domínios a conferir: `prazo_meses` ∈ {24, 36, 48, 60} · `ltv` entre 0 e 1 · `default_90_12` ∈ {0, 1} · `valor_financiado` > 0 · ids únicos.

**DoD:**
- [x] `validar()` passa nas três bases como estão hoje
- [x] `validar()` **falha com mensagem clara** (dizendo qual coluna e qual valor) quando recebe uma base adulterada de propósito no teste
- [x] Ids únicos confirmados nas três

---

### S01.5 · Gravação em Parquet

**O que:** gravar `base_A.parquet`, `base_B.parquet`, `base_C.parquet` e `base_A_realizados.parquet` em `dados/processados/`, com as datas como `date32`.

**Por quê:** Parquet preserva tipo (CSV não) e é a [fronteira com o R](../../AGENTS.md#a-fronteira-entre-as-duas-linguagens). O `date32` não é detalhe: já verificamos neste repositório que `datetime64` do pandas chega no R **deslocado em −3h**, o que transformaria `2022-01-01` em `2021-12-31` e **moveria o contrato de safra**. Safra é a unidade de análise do S03.

**DoD:**
- [x] Os quatro arquivos existem em `dados/processados/`
- [x] Ler de volta em Python devolve exatamente as mesmas linhas e tipos (round-trip)
- [x] Ler no R com `arrow::read_parquet()` devolve as datas como `Date`, **sem deslocamento** — conferir que a menor data da base A é `2022-01-01`, não `2021-12-31`
- [x] Nenhum arquivo em `dados/` aparece em `git status`

---

### S01.6 · Testes

**O que:** `tests/python/test_ingestao.py`.

**Por quê:** o teste é o que transforma a regra em garantia. Sem ele, "não use a coluna proibida" é um lembrete num documento que ninguém relê às 23h do dia 25.

**Testes obrigatórios:**
1. Nenhuma coluna proibida sobrevive em nenhuma das três bases.
2. Contagem de linhas: 10.000 / 3.000 / 5.000.
3. O alvo existe em A e **não** existe em B nem em C.
4. `qtd_parcelas_em_atraso_12m` **não** está nas bases carregadas — teste dedicado, com o motivo escrito no docstring, para ninguém "consertar" achando que é redundante.
5. Nulos preservados nas contagens conhecidas.
6. Round-trip do Parquet preserva tipos.
7. `validar()` rejeita base adulterada.

**DoD:**
- [x] `.\scripts\py.cmd -m pytest -q` verde, incluindo os 7 acima
- [x] Cada teste falha de verdade se a proteção for removida (verificado quebrando de propósito uma vez)

---

### S01.7 · Pipeline orquestrador

**O que:** `python/etl/01_ingestao.py` — carrega as três, valida, grava, loga.

**Por quê:** separar biblioteca de pipeline é a convenção do repositório. As funções ficam testáveis; o script é o que alguém roda.

**DoD:**
- [x] `.\scripts\py.cmd python\etl\01_ingestao.py` roda do zero, sem passo manual
- [x] Loga cada base com linhas e colunas, e o caminho de cada arquivo gravado
- [x] Rodar duas vezes seguidas produz arquivos idênticos (idempotente)

---

## DoD do S01 (o passo inteiro)

Só está pronto quando **todos** estes verificam:

- [x] `.\scripts\py.cmd python\etl\01_ingestao.py` roda limpo e gera os 4 Parquets
- [x] `.\scripts\py.cmd -m pytest -q` verde
- [x] As três bases carregam com 10.000 / 3.000 / 5.000 linhas
- [x] **Zero colunas proibidas** nas bases de modelagem
- [x] Realizados preservados à parte, prontos para o S02
- [x] Datas lidas no R sem deslocamento de fuso
- [x] `git status` limpo de dados
- [x] O `DICIONARIO_DADOS.md` reflete os arquivos gerados

## Artefatos gerados

| Arquivo | Conteúdo | Consumido por |
| ------- | -------- | ------------- |
| `dados/processados/base_A.parquet` | 10.000 × 23 (preditoras + alvo) | S03, S04, S05, S06 |
| `dados/processados/base_B.parquet` | 3.000 × 22 | S06 |
| `dados/processados/base_C.parquet` | 5.000 × 20 | S07, S09, S10 |
| `dados/processados/base_A_realizados.parquet` | 10.000 × 5 | **S02** (gabarito de EAD/LGD) |
| `python/banking/dados.py` | O contrato | todos |
| `tests/python/test_ingestao.py` | As garantias | CI mental |

## Risco deste passo

**Baixo, mas com um ponto de atenção:** a tentação de "já aproveitar e imputar os nulos". Não. Imputação aqui vaza informação entre treino e validação e custa os 10 pontos de qualidade técnica — que são pontos absolutos, não relativos ao melhor grupo.
