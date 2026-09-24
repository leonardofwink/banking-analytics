# Comparação com o material dos colegas

> Feito em 2026-09-24, a partir dos arquivos que o Deni e o Marcelo colocaram
> na pasta do grupo. Reprodutível por `python/analises/15_comparar_colegas.py`.
>
> **Leitura de uso interno**, para o grupo decidir o que submeter. As frentes
> aparecem pelo nome — **Léo**, **Deni**, **Marcelo** — em vez de "nós" e
> "eles", para que a comparação se leia igual de qualquer lado. Não é avaliação
> de ninguém: três dos achados aqui são coisas que o Léo não tinha feito e os
> outros sim.
>
> ⚠️ **Falta o Renato.** Na reunião de 24/09 ele apresentou números próximos
> aos do Léo, mas ainda não subiu os arquivos. Quando subir, entra aqui — e
> vale conferir se a proximidade se sustenta no mesmo motor.

## O resumo, se você só ler uma coisa

As três frentes reportam ROI muito diferente: **Léo 11,3%, Marcelo ~12%,
Deni 18,4%.** Só uma parte dessa diferença é de política. O resto é de
**conta**.

Rodando as três tabelas no mesmo motor — o do Léo, com os parâmetros de EAD e
LGD do professor e as premissas de aceite dele:

| Política | Aprovação | ROI | Volume central | Volume pior | Inadimpl. pior | Viável |
| -------- | --------- | --- | -------------- | ----------- | -------------- | ------ |
| **Léo** (score ≥ 5) | 59,5% | 11,33% | **R$ 66,7 mi** | **R$ 45,1 mi** | **6,58%** | ✅ **sim** |
| Marcelo (submissão dele, PD dele) | 49,2% | **12,32%** | R$ 52,8 mi | R$ 34,6 mi | 7,03% | ❌ volume |
| Deni (tabela reconstruída) | 50,2% | **13,78%** | R$ 38,2 mi | R$ 22,3 mi | 7,95% | ❌ volume |

> ⚠️ **Estes números não são os que cada um reporta.** São o resultado de
> passar cada política pelo mesmo motor, com as mesmas premissas de aceite e
> os parâmetros de EAD e LGD do professor.
>
> A linha do **Marcelo** é a submissão dele rodada como entregou — as PDs
> dele, as ofertas dele, sem reconstrução. A do **Deni** teve de ser
> reconstruída da tabela, porque ele não submeteu decisões por proposta; a
> seção 3 mostra que a conclusão não muda com nenhuma das versões da tabela
> dele.
>
> **O ROI cresce de cima para baixo, e a viabilidade cai junto.** É a mesma
> troca que aparece em todo o resto: ROI se compra com volume.

**A do Léo é a única que sobrevive aos guard-rails nos três cenários** — e é
a que entrega o menor ROI das três. Não é coincidência: é o preço da folga.

Com a ressalva honesta: isso é no simulador do Léo, com as elasticidades dele.
O Marcelo usa premissas de aceite diferentes e, com elas, a política dele
passa no volume. Ninguém sabe qual está certa — é a premissa mais frágil dos
três trabalhos, e os três a declaram. O que o motor comum mostra não é quem
está certo, e sim **quanta folga cada política tem se o cliente for mais
sensível a preço do que se supôs**.

---

## 1. Formato — o que o professor cruza

Este bloco não é sobre mérito técnico, mas custa o bloco inteiro se falhar.

| | Deni | Marcelo | Léo |
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

| | Léo | Deni | Marcelo |
| - | --- | ---- | ------- |
| Algoritmo | XGBoost | Regressão logística | Árvores com boosting e restrições monotônicas |
| AuROC (validação) | **0,7234** | 0,6685 | 0,72–0,75 |
| KS | **0,3660** | 0,2935 | 0,36–0,40 |
| PD média na Base B | 7,88% | 8,30% | 7,91% |
| Cortes do score | fixos, absolutos | decis | decis da Base B, fixos |

As PDs médias são próximas — a diferença está na ordenação. Não deu para
correlacionar porque os ids do Deni não batem.

O **Marcelo tem o modelo mais forte do grupo**, e por uma razão que vale
copiar: ele usou **restrições monotônicas**, que reduziram a distância entre
treino e validação de 0,15 para 0,06 e ainda subiram a AuROC. É exatamente o
sobreajuste que fez o Léo desconfiar das árvores livres — o treino dele dá
0,8701 contra 0,7234 de validação, folga de 0,147.

---

## 3. 🔑 De onde vêm os 18,4% do Deni

O documento dele declara, na seção 4:

> *"A perda esperada unitária por contrato é calculada via PD × EAD
> (R$ 15.000) × LGD (40%)."*

São dois parâmetros fixos no lugar das tabelas do professor — e eles fazem
coisas **diferentes**, que vale separar.

| | Deni | Parâmetros do desafio |
| - | ---- | --------------------- |
| EAD por contrato | R$ 15.000 fixo | **R$ 37.535** (média dos aprovados) |
| LGD | 40% fixo | **67,8%** (tabela, por LTV e idade do veículo) |

### O EAD fixo mexe no volume. A LGD mexe no ROI.

O ROI é uma **razão** — (juros − perda) ÷ volume ÷ anos. Se o contrato inteiro
encolhe de R$ 37 mil para R$ 15 mil, os juros, a perda e o volume encolhem
**juntos**, e o retorno quase não se move. Testando um efeito de cada vez na
carteira do Léo:

| | ROI | vs. base |
| - | --- | -------- |
| (a) parâmetros do professor | 12,32% | — |
| (b) só a LGD em 40%, EAD real | 12,76% | **+0,44 pp** |
| (c) contrato fixo de R$ 15.000, LGD real | 12,35% | +0,03 pp |

**Quem move o ROI é a LGD, e ela vale +0,44 ponto — não os 7 pontos de
diferença.** O EAD fixo não infla retorno nenhum; ele distorce o volume.

### Os R$ 46,7 milhões

Ele reporta 77,9% de aprovação — 3.895 contratos — e R$ 46,7 mi de volume.
Isso dá um ticket médio de **R$ 11.990 por contrato**, quando o financiado
médio pedido na Base C é de **R$ 33.411**.

A conta fecha exata de outro jeito:

```
3.895 contratos × R$ 15.000 × 0,80 (entrada de 20%) = R$ 46,7 milhões
```

**O contrato foi fixado em R$ 15.000 — o mesmo número usado como EAD.** Com os
valores reais da Base C e os mesmos 77,9% aprovados, sem modelar nenhuma
recusa, o volume seria de **R$ 131 milhões**.

Ou seja: **o volume dele não está inflado. Está cerca de 3× subestimado.** Se
ele refizer a conta com os valores reais, o volume dele sobe muito — e o
guard-rail de R$ 40 mi deixa de ser problema, desde que o aceite colabore.

### O que a política dele faz no motor do Léo

| Cenário | Volume | Aceite | ROI | |
| ------- | ------ | ------ | --- | - |
| otimista | R$ 57,1 mi | 62,6% | 14,58% | ✅ |
| **central** | **R$ 38,2 mi** | 41,6% | 13,78% | ❌ volume |
| pessimista | R$ 22,3 mi | 24,0% | 12,91% | ❌ volume |

A taxa média de 2,41% ao mês — 51% acima do mercado de 1,59% — derruba o
aceite para 41,6% no cenário central. **É o aceite que fura o volume, não o
tamanho do contrato.**

### E a aprovação de 77,9%?

Essa diferença é de **modelo**, não de política. O corte dele é PD ≤ 11%:

| | Aprovação com PD ≤ 11% |
| - | ---------------------- |
| com as PDs do Deni (logística) | **77,9%** |
| com as PDs do Léo (XGBoost) | **50,2%** |

A logística dele comprime a cauda: mediana 6,78% e máximo 47,87% na Base B,
contra 9,36% e 81,19% do Léo na Base C. O mesmo corte pega populações
diferentes.

### O que isso quer dizer

Não dá para reproduzir os 18,4% com os parâmetros do desafio. A LGD explica
0,44 ponto; o resto vem de cobrar mais caro **sem modelar que preço afasta
cliente** — o enunciado diz explicitamente que afasta.

Mas o erro que mais custa a ele não é esse: é o volume 3× subestimado, que faz
a política dele parecer mais apertada do que é. **Vale avisar, porque corrigir
joga a favor dele.**

## 3b. ⚠️ O material do Deni é internamente inconsistente

A tabela de política aparece **duas vezes** no material dele, com números
diferentes. Comparando linha a linha:

| Score | Faixa de PD no CSV | Faixa de PD no documento | Perda no CSV | Perda no doc | ROI no CSV | ROI no doc |
| ----- | ------------------ | ------------------------ | ------------ | ------------ | ---------- | ---------- |
| 10 | 0,74% – 3,03% | 0,8% – 2,1% | R$ 142,00 | R$ 87,00 | 21,2% | 21,2% |
| 9 | 3,04% – 4,01% | 2,1% – 3,4% | R$ 212,24 | R$ 165,00 | **24,0%** | **20,4%** |
| 8 | 4,01% – 4,92% | 3,4% – 4,8% | R$ 268,69 | R$ 246,00 | **27,0%** | **19,8%** |
| 7 | 4,92% – 5,77% | 4,8% – 6,2% | R$ 320,33 | R$ 330,00 | **30,1%** | **19,1%** |
| 6 | 5,77% – 6,78% | 6,2% – 7,8% | R$ 377,23 | R$ 420,00 | **33,2%** | **18,5%** |
| 5 | 6,78% – 7,86% | 7,8% – 9,5% | R$ 438,10 | R$ 519,00 | **36,3%** | **17,6%** |
| 4 | 7,86% – 9,41% | 9,5% – 11,2% | R$ 515,05 | R$ 621,00 | **39,6%** | **16,8%** |

- **As 10 faixas de PD divergem.** Todas.
- **As 10 perdas esperadas divergem.**
- **O ROI por faixa diverge em 6 das 7 aprovadas** — e não só no valor: no CSV
  ele **cresce** com o risco (21,2% → 39,6%), no documento ele **cai**
  (21,2% → 16,8%). São afirmações opostas sobre qual faixa dá mais retorno.
- **Taxa, prazo e entrada batem** nas duas fontes. Essas são as únicas que a
  reconstrução usou.

Parece uma versão antiga que ficou para trás em um dos arquivos. Vale conferir
qual é a boa antes de submeter — se o professor abrir os dois, a pergunta é
imediata.

### A conclusão muda conforme a versão?

Não. Rodando as três leituras possíveis do material dele:

| Leitura | Aprovação | ROI | Volume central | Viável |
| ------- | --------- | --- | -------------- | ------ |
| faixas do CSV + corte do CSV (0,0941) | 50,2% | 13,78% | R$ 38,2 mi | ❌ volume |
| faixas do CSV + corte do texto (0,11) | 50,2% | 13,78% | R$ 38,2 mi | ❌ volume |
| faixas do documento + corte dele (0,112) | 55,6% | 14,69% | R$ 37,4 mi | ❌ volume e inadimplência |

**As três furam o volume.** A conclusão não depende de qual tabela se use — o
que muda é o tamanho da violação.

---

## 4. O que o Marcelo fez melhor

Três coisas, e todas são adotáveis.

### 4.1 Restrições monotônicas no modelo

Ele obriga o modelo a respeitar a direção conhecida de cada variável (mais
restrições → mais risco, nunca o contrário). Resultado: **folga treino-validação
de 0,06 contra 0,147 do Léo**, com AuROC igual ou melhor.

É a resposta técnica à crítica mais provável ao XGBoost do Léo.

### 4.2 As regras de exclusão, com o argumento certo

> *"negar score de bureau abaixo de 460 e 3 ou mais restrições ativas
> (**perfis que o modelo nunca viu**)"*

São **exatamente os limites da Base A** que apareceram quando o Léo foi
investigar as hard rules do Deni: bureau mínimo 460, máximo 2 restrições. O
Marcelo chegou lá por conta própria, e com o argumento de domínio.

### 4.0 A submissão dele está completa e consistente

Conferido item a item contra o documento:

| | No CSV dele | No documento dele | |
| - | ----------- | ----------------- | - |
| Aprovação | 49,2% | 49,2% | ✅ |
| Taxa | 1,85% a 2,18%, média 1,96% | 1,85% a 2,18%, ~1,95% | ✅ |
| Prazos ofertados | 48 e 60 | 60 (48 nos scores 2 e 3) | ✅ |
| Entradas | 5%, 10%, 15% | 5% a 15% | ✅ |
| Score mínimo aprovado | 2 | "scores 2 a 10" | ✅ |

**Nenhuma divergência.** É o único dos três materiais em que o CSV e o
documento contam a mesma história.

### 4.3 Uma validação que ninguém mais fez

> *"aplicar os preços da V3 aos contratos de 2024 com os defaults reais dá
> ROI de 12,4%"*

Ele testou a precificação contra **default realizado**, não projetado. É uma
âncora independente do simulador de aceite — a maior fragilidade das três
frentes.

**É o que mais vale copiar.**

---

## 5. Onde o Léo está melhor

| | Diferencial |
| - | ----------------- |
| **Viabilidade** | única das três que passa nos guard-rails nos três cenários |
| **Reprodutibilidade** | 167 testes; todo número do documento vem do pipeline na geração |
| **A armadilha** | `qtd_parcelas_em_atraso_12m` removida e travada por teste |
| **Anti-circularidade** | `comprometimento_renda` fora do modelo; o Deni a usa, e ela não existe na Base C |
| **A pergunta dos 15%** | respondida por medição (5.600 políticas) e não por argumento |
| **Folga declarada** | 12,7% de margem escolhidos em vez do ROI máximo, e está escrito |

---

## 6. 🔑 Copiar o que os outros fazem não chega aos 15%

Duas coisas que o Deni e o Marcelo fazem e o Léo não, testadas no mesmo motor.

### 6.1 Prazo e entrada que variam por faixa

O Deni dá 60 meses aos scores bons e 48 aos ruins, com entrada de 10% a 30%.
O Marcelo dá 60 a quase todos e entrada de 5% a 15%. A grade do Léo sempre
deu **o mesmo prazo e a mesma entrada a todas as faixas** — o contrário nunca
tinha sido testado.

São 1.536 combinações, incluindo os perfis exatos dos dois
(`python/analises/16_prazo_por_faixa.py`):

| Perfil de prazo | Melhor ROI viável |
| --------------- | ----------------- |
| **48 para todas — a do Léo** | **11,42%** |
| 60 nos bons, 36 nos ruins | 11,32% |
| 48 nos bons, 36 nos ruins | 11,31% |
| 60 até o score 8, 48 abaixo | 11,28% |
| 60 nos bons, 48 nos ruins | 11,13% |
| 60 para todas | 8,84% |

| Perfil de entrada | Melhor ROI viável |
| ----------------- | ----------------- |
| **10% para todas — a do Léo** | **11,42%** |
| 10/20/30, como o Deni | 11,40% |
| 5 a 15, como o Marcelo | 11,34% |
| sem entrada | 11,32% |

**A configuração do Léo já era a ótima.** Prazo longo em cliente bom rende mais
juros, mas alonga a exposição e o efeito se cancela; prazo curto derruba os
juros mais do que reduz a perda. Nenhum perfil chega perto dos 15%.

### 6.2 E se o gargalo for o modelo?

O Marcelo submeteu a PD das 5.000 propostas da Base C, então dá para rodar
**a política do Léo sobre o modelo dele** e isolar o efeito
(`python/analises/17_modelo_do_marcelo.py`). Os dois sem re-escoragem, para
ser justo:

| | Aprovação | ROI | Volume (pior) | Inadimpl. (pior) |
| - | --------- | --- | ------------- | ---------------- |
| política do Léo, modelo do Léo | 59,5% | 11,40% | **R$ 45,1 mi** | **6,11%** |
| política do Léo, modelo do Marcelo | 59,2% | **11,54%** | R$ 41,6 mi | 7,02% |

**+0,14 ponto de ROI, e a folga cai de 12,7% para 4%.** Na Base C os dois
modelos têm correlação de Spearman de **0,907**, PD média de 14,84% contra
14,59% e máximo de 81,2% contra 83,8% — ordenam quase igual, e a diferença
econômica é pequena.

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

**Urgente — avisar o Deni.** Três coisas, em ordem de custo:

1. **Os ids** (`CT-10001` contra `T000001`) e a política com 10 linhas em vez
   de 5.000 — invalidam os dois entregáveis, e são 15 minutos de conserto.
2. **A LGD de 40%** contra os 67,8% da tabela do professor.
3. **O contrato fixado em R$ 15.000**, que subestima o volume dele em 3×.
   Corrigir isso joga a favor dele.

**Para a submissão do grupo**, a leitura que os números sustentam:

| Peça | De quem | Por quê |
| ---- | ------- | ------- |
| Modelo de PD | **Marcelo** | AuROC 0,72–0,75 com folga de 0,06; monotonicidade resolve o sobreajuste |
| Política e preço | **Léo** | única viável nos três cenários, com folga medida |
| Regras de exclusão | **Marcelo** | mesmos limites que o Léo achou, com o argumento de domínio |
| Validação contra default real | **Marcelo** | âncora que não depende do simulador |
| Documento e defesa | **Léo** | cadeia completa, com a lacuna dos 15% medida e declarada |

**A juntar, se der tempo:** as restrições monotônicas no modelo e a validação
contra o default realizado de 2024. As duas vêm do Marcelo, e nenhuma passa
por cobrar mais caro.

**E o material do Renato**, assim que ele subir. Se os números dele batem com
os do Léo por caminhos diferentes, é a confirmação independente mais forte que
o grupo pode levar para a banca — e vale um parágrafo no documento de defesa.
