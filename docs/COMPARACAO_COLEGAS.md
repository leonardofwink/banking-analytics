# Comparação com o material dos colegas

> Feito em 2026-09-24, a partir dos arquivos que o Deni e o Marcelo colocaram
> na pasta do grupo. Reprodutível por `python/analises/15_comparar_colegas.py`.
>
> **Leitura de uso interno.** Serve para decidirmos o que submeter — não é
> avaliação de ninguém, e três dos achados aqui são coisas que nós não
> tínhamos feito e eles sim.

## O resumo, se você só ler uma coisa

Os três reportam ROI muito diferente: **nós 11,3%, Marcelo ~12%, Deni 18,4%.**
Só uma parte dessa diferença é de política. O resto é de **conta**.

Rodando as três tabelas no mesmo motor — o nosso, com os parâmetros de EAD e
LGD do professor e as nossas premissas de aceite:

| Política | Aprovação | ROI | Volume (pior) | Inadimpl. (pior) | Viável |
| -------- | --------- | --- | ------------- | ---------------- | ------ |
| **nossa** (score ≥ 5) | 59,5% | **11,33%** | R$ 45,1 mi | 6,58% | ✅ **sim** |
| Deni (corte PD 11%) | 50,2% | 13,78% | **R$ 22,3 mi** | 7,95% | ❌ volume |
| Marcelo, sem as regras dele | 62,8% | 11,78% | R$ 43,4 mi | **9,55%** | ❌ inadimplência |
| Marcelo, com as regras dele | 54,5% | 11,85% | **R$ 39,5 mi** | **8,82%** | ❌ ambos |

**A nossa é a única que sobrevive aos guard-rails nos três cenários.**

Com a ressalva honesta: isso é no *nosso* simulador, com as *nossas*
elasticidades. O Marcelo usa premissas de aceite diferentes e, com elas, a
política dele passa. Nenhum de nós sabe qual está certa — é a premissa mais
frágil dos três trabalhos, e todos declaramos isso.

---

## 1. Formato — o que o professor cruza

Este bloco não é sobre mérito técnico, mas custa o bloco inteiro se falhar.

| | Deni | Marcelo | Nós |
| - | ---- | ------- | --- |
| `submissao_modelo.csv` | 3.000 linhas | 3.000 linhas | 3.000 linhas |
| colunas | `id_contrato;probabilidade_default_pd;score_atribuido;decisao_politica` | `id_contrato,pd` ✅ | `id_contrato,pd` ✅ |
| separador | **`;`** | `,` ✅ | `,` ✅ |
| **ids que cruzam com a Base B** | **0 de 3.000** ❌ | 3.000 de 3.000 ✅ | 3.000 de 3.000 ✅ |
| `submissao_politica.csv` | **10 linhas** ❌ | 5.000 linhas ✅ | 5.000 linhas ✅ |
| ids que cruzam com a Base C | **0 de 5.000** ❌ | 5.000 de 5.000 ✅ | 5.000 de 5.000 ✅ |

### 🔴 Os dois problemas do Deni

1. **Os ids não existem.** Ele usa `CT-10001`; a Base B usa `T000001`. O
   professor cruza por `id_contrato` — **nenhuma linha vai casar**.
2. **A política tem 10 linhas, não 5.000.** Ele submeteu a *tabela de faixas*
   no lugar das decisões por proposta. O enunciado pede uma linha por
   proposta da Base C.

Somados, estes dois erros valem os 80 pontos dos dois entregáveis. **É a coisa
mais urgente a avisar a ele** — e é fácil de corrigir, porque o trabalho
analítico dele está feito.

---

## 2. Os modelos

| | Nós | Deni | Marcelo |
| - | --- | ---- | ------- |
| Algoritmo | XGBoost | Regressão logística | Árvores com boosting e restrições monotônicas |
| AuROC (validação) | **0,7234** | 0,6685 | 0,72–0,75 |
| KS | **0,3660** | 0,2935 | 0,36–0,40 |
| PD média na Base B | 7,88% | 8,30% | 7,91% |
| Cortes do score | fixos, absolutos | decis | decis da Base B, fixos |

As PDs médias são próximas — a diferença está na ordenação. Não deu para
correlacionar porque os ids do Deni não batem.

O **Marcelo tem o modelo mais forte do grupo**, e por uma razão que vale
roubar: ele usou **restrições monotônicas**, que reduziram a distância entre
treino e validação de 0,15 para 0,06 e ainda subiram a AuROC. É exatamente o
sobreajuste que nos fez desconfiar das árvores livres (o nosso treino dá
0,8701 contra 0,7234 de validação, folga de 0,147).

---

## 3. 🔑 De onde vêm os 18,4% do Deni

O documento dele declara, na seção 4:

> *"A perda esperada unitária por contrato é calculada via PD × EAD
> (R$ 15.000) × LGD (40%)."*

Ele usa **EAD e LGD fixos**, em vez das tabelas do professor:

| | Deni | Parâmetros do desafio |
| - | ---- | --------------------- |
| EAD por contrato | R$ 15.000 fixo | **R$ 37.418** (média real dos aprovados) |
| LGD | 40% fixo | **67,9%** (média das tabelas, por faixa de LTV e idade) |
| Perda por unidade de PD | R$ 6.000 | **R$ 25.389** |

**A perda dele é 4,2 vezes menor que a dos parâmetros do desafio.**

O enunciado entrega duas tabelas — `fator_ead` por prazo × LTV e LGD por
idade do veículo × LTV — e o EAD real é o valor financiado vezes um fator de
0,98 a 1,04. Um EAD fixo de R$ 15.000 subestima quase três vezes o valor
financiado mediano, e 40% de LGD é quase metade do que a tabela dá.

### Quanto disso explica o ROI

Trocando **só** os parâmetros de perda na nossa carteira, com as mesmas taxas:

| | ROI | Perda total |
| - | --- | ----------- |
| parâmetros do professor | 12,32% | R$ 4,6 mi |
| parâmetros do Deni | 13,12% | R$ 1,1 mi |

Isso dá **+0,8 ponto**. Não explica sozinho a distância de 11,3% para 18,4%.

O resto vem de **preço sem consequência**: ele cobra 2,41% ao mês em média
(contra os nossos 1,91%), chegando a 3,30% na pior faixa, e projeta volume de
R$ 46,7 mi assumindo que isso não afasta ninguém. No nosso motor, essa taxa
derruba o aceite para 41,6% e o volume para R$ 38,2 mi — **abaixo do piso de
R$ 40 mi**.

### 🔑 O Deni é um caso concreto do que o S12 mediu

A [varredura do S12](specs/S12_FRONTEIRA_ROI_VOLUME.md) encontrou **4.044
políticas que batem 15% de ROI e nenhuma viável**, todas mortas pelo volume.
A política do Deni é uma delas: 13,78% de ROI no nosso motor, R$ 22,3 mi de
volume no pior cenário.

Não é que ele errou a política. É que ele mediu o ROI sem medir o custo dela.

---

## 4. O que o Marcelo fez melhor que nós

Três coisas, e todas são adotáveis.

### 4.1 Restrições monotônicas no modelo

Ele obriga o modelo a respeitar a direção conhecida de cada variável (mais
restrições → mais risco, nunca o contrário). Resultado: **folga treino-validação
de 0,06 contra os nossos 0,147**, com AuROC igual ou melhor.

É a resposta técnica à crítica mais provável ao nosso XGBoost.

### 4.2 As regras de exclusão, com o argumento certo

> *"negar score de bureau abaixo de 460 e 3 ou mais restrições ativas
> (**perfis que o modelo nunca viu**)"*

São **exatamente os limites da Base A** que encontramos ao investigar as hard
rules do Deni: bureau mínimo 460, máximo 2 restrições. Ele chegou lá
independentemente, e usou o argumento de domínio — o mesmo que eu tinha
recomendado a você.

### 4.3 Uma validação que nós não temos

> *"aplicar os preços da V3 aos contratos de 2024 com os defaults reais dá
> ROI de 12,4%"*

Ele testou a precificação contra **default realizado**, não projetado. É uma
âncora independente do simulador de aceite — a nossa maior fragilidade.

**Isto é o que eu mais recomendo copiar.**

---

## 5. Onde nós estamos melhor

| | Nosso diferencial |
| - | ----------------- |
| **Viabilidade** | única das três que passa nos guard-rails nos três cenários |
| **Reprodutibilidade** | 167 testes; todo número do documento vem do pipeline na geração |
| **A armadilha** | `qtd_parcelas_em_atraso_12m` removida e travada por teste |
| **Anti-circularidade** | `comprometimento_renda` fora do modelo; o Deni a usa, e ela não existe na Base C |
| **A pergunta dos 15%** | respondida por medição (5.600 políticas) e não por argumento |
| **Folga declarada** | escolhemos 12,7% de margem em vez do ROI máximo, e está escrito |

---

## 6. 🔑 Tentamos copiar o que eles fazem. Não chega aos 15%.

Duas coisas que eles fazem e nós não, testadas no nosso motor.

### 6.1 Prazo e entrada que variam por faixa

O Deni dá 60 meses aos scores bons e 48 aos ruins, com entrada de 10% a 30%.
O Marcelo dá 60 a quase todos e entrada de 5% a 15%. A nossa grade sempre
deu **o mesmo prazo e a mesma entrada a todas as faixas** — nunca tínhamos
testado o contrário.

Varremos 1.536 combinações, incluindo os perfis exatos dos dois
(`python/analises/16_prazo_por_faixa.py`):

| Perfil de prazo | Melhor ROI viável |
| --------------- | ----------------- |
| **48 para todas — o nosso** | **11,42%** |
| 60 nos bons, 36 nos ruins | 11,32% |
| 48 nos bons, 36 nos ruins | 11,31% |
| 60 até o score 8, 48 abaixo | 11,28% |
| 60 nos bons, 48 nos ruins | 11,13% |
| 60 para todas | 8,84% |

| Perfil de entrada | Melhor ROI viável |
| ----------------- | ----------------- |
| **10% para todas — o nosso** | **11,42%** |
| 10/20/30, como o Deni | 11,40% |
| 5 a 15, como o Marcelo | 11,34% |
| sem entrada | 11,32% |

**A nossa configuração já era a ótima.** Prazo longo em cliente bom rende mais
juros, mas alonga a exposição e o efeito se cancela; prazo curto derruba os
juros mais do que reduz a perda. Nenhum perfil chega perto dos 15%.

### 6.2 E se o gargalo for o modelo?

O Marcelo submeteu a PD das 5.000 propostas da Base C, então dá para rodar
**a nossa política sobre o modelo dele** e isolar o efeito
(`python/analises/17_modelo_do_marcelo.py`). Os dois sem re-escoragem, para
ser justo:

| | Aprovação | ROI | Volume (pior) | Inadimpl. (pior) |
| - | --------- | --- | ------------- | ---------------- |
| nossa política, nosso modelo | 59,5% | 11,40% | **R$ 45,1 mi** | **6,11%** |
| nossa política, modelo do Marcelo | 59,2% | **11,54%** | R$ 41,6 mi | 7,02% |

**+0,14 ponto de ROI, e a folga cai de 12,7% para 4%.** A correlação de
Spearman entre os dois modelos é 0,907 — eles ordenam quase igual, e a
diferença econômica é pequena.

### O que isso fecha

Três caminhos independentes chegaram ao mesmo teto:

| Caminho | Teto viável |
| ------- | ----------- |
| S12 — 5.600 políticas, grade aberta | 11,46% |
| S16 — prazo e entrada por faixa | 11,42% |
| S17 — trocando o modelo de PD | 11,54% |

**Não há alavanca conhecida que leve aos 15% respeitando os guard-rails.** A
lacuna não é de execução: é a premissa de aceite, e para 15% ela teria que
estar errada por um fator de cinco.

---

## 7. O que fazer com isto

**Urgente — avisar o Deni hoje.** Os ids e o formato da política invalidam os
dois entregáveis dele, e são 15 minutos de conserto.

**Para a submissão do grupo**, a leitura que os números sustentam:

| Peça | De quem | Por quê |
| ---- | ------- | ------- |
| Modelo de PD | **Marcelo** | AuROC 0,72–0,75 com folga de 0,06; monotonicidade resolve o sobreajuste |
| Política e preço | **nós** | única viável nos três cenários, com folga medida |
| Regras de exclusão | **Marcelo** | mesmos limites que achamos, com o argumento de domínio |
| Validação contra default real | **Marcelo** | âncora que não depende do simulador |
| Documento e defesa | **nós** | cadeia completa, com a lacuna dos 15% medida e declarada |

**A juntar, se der tempo:** testar a nossa política sobre o modelo do Marcelo.
Se a ordenação dele for melhor, a mesma tabela de preços rende mais — e é o
único caminho que aumenta ROI **sem** trocar volume, porque não passa por
cobrar mais caro.
