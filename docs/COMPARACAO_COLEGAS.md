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
> O Renato entregou só a apresentação, sem CSVs — a seção 4b faz o pente fino
> do que dá para medir a partir dela.

## O resumo, se você só ler uma coisa

As três frentes reportam ROI muito diferente: **Léo 11,3%, Marcelo ~12%,
Deni 18,4%.** Só uma parte dessa diferença é de política. O resto é de
**conta**.

Rodando as três tabelas no mesmo motor — o do Léo, com os parâmetros de EAD e
LGD do professor e as premissas de aceite dele:

| Política | Aprovação | ROI | Volume central | Volume pior | Inadimpl. pior | Viável |
| -------- | --------- | --- | -------------- | ----------- | -------------- | ------ |
| **Léo** (score ≥ 5) | 59,5% | 11,33% | **R$ 66,7 mi** | **R$ 45,1 mi** | **6,58%** | ✅ **sim** |
| Marcelo (submissão dele, PD dele) | 49,2% | 12,32% | R$ 52,8 mi | R$ 34,6 mi | 7,03% | ❌ volume |
| Renato (tabela reconstruída) | 44,8% | **12,53%** | R$ 46,1 mi | R$ 29,3 mi | 7,49% | ❌ volume |
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
> As afirmações dos dois documentos foram conferidas contra as bases: a do
> Deni na seção 3b, a do Marcelo na 4.0.
>
> **O ROI cresce de cima para baixo, e a viabilidade cai junto.** É a mesma
> troca que aparece em todo o resto: ROI se compra com volume.

**A do Léo é a única que sobrevive aos guard-rails nos três cenários** — e é
a que entrega o menor ROI das três. Não é coincidência: é o preço da folga.

### ⚠️ Mas a tabela acima não diz que as outras estão erradas

Ela roda as três políticas com **as elasticidades de aceite do Léo**, que são
uma premissa calibrada por argumento — não uma medição. Ninguém do grupo sabe
a intensidade real, e o professor não revelou.

Trocando a premissa, a ordem muda. **Com aceite de 100% — a premissa do Deni —
e os parâmetros de EAD e LGD do professor:**

| | ROI | Volume | Inadimplência | Guard-rails |
| - | --- | ------ | ------------- | ----------- |
| **Deni** | **15,73%** | R$ 89,7 mi | 4,77% | ✅ **todos** |
| Léo | 11,68% | R$ 108,0 mi | 6,12% | ✅ todos |

**O Deni está certo: a política dele bate a meta de 15% e passa em todos os
guard-rails, dentro das premissas dele.** E isso não depende da LGD de 40%
dele — o número acima já usa a tabela do professor.

A tabela do resumo mede outra coisa: **quanta folga cada política tem se o
cliente for mais sensível a preço do que se supôs.** A do Léo aguenta mais
porque cobra menos; a do Deni entrega mais porque cobra mais. São apostas
diferentes sobre o mesmo desconhecido, e a seção 3 mostra exatamente onde
cada uma quebra.

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

### A política dele, de premissa em premissa

Este é o ponto que decide a comparação — e que o Deni levantou na reunião de
24/09, com razão. O que muda entre 15,7% e 13,8% **não é a conta da perda**: é
quanto cliente desiste quando o preço sobe.

| Premissa de aceite | Aceite | Volume | ROI | Guard-rails |
| ------------------ | ------ | ------ | --- | ----------- |
| **nenhuma fuga (a do Deni)** | 100% | **R$ 89,7 mi** | **15,73%** | ✅ **todos** |
| 20% da elasticidade do Léo | 72,0% | R$ 65,0 mi | 14,94% | ✅ todos |
| 50% da elasticidade do Léo | 57,5% | R$ 52,3 mi | 14,53% | ✅ todos |
| 80% da elasticidade do Léo | 47,0% | R$ 43,1 mi | 14,17% | ✅ todos |
| **100% — a premissa do Léo** | 41,6% | **R$ 38,2 mi** | 13,95% | ❌ volume, por R$ 1,8 mi |
| 150% | 31,6% | R$ 29,3 mi | 13,51% | ❌ volume |

**A política dele aguenta até 80% da elasticidade do Léo antes de furar.** E
quando fura, fura por R$ 1,8 milhão num piso de R$ 40 — não é um colapso.

Ou seja: **a divergência entre os dois trabalhos é uma única premissa**, e
nenhum dos dois a mediu. O Deni assume que o cliente não foge; o Léo assume
que foge bastante, calibrado pelo argumento de que um teto de 3,5% só é
guard-rail se as políticas quiserem chegar perto dele.

O que o enunciado diz, e que pesa contra o aceite de 100%:

> *"Taxa alta afasta o cliente. Ele tem concorrente. Preço acima do mercado
> derruba a taxa de aceite, e proposta não aceita não gera receita nenhuma."*

A taxa média dele é de 2,41% ao mês, 51% acima do mercado de 1,59%. Alguma
fuga é certa; **quanta, ninguém sabe** — e é exatamente aí que os dois
trabalhos se separam.

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

Separando o que é fato do que é premissa:

**Fatos** — não dependem de quem simula:

| O que está errado | Quanto custa |
| ----------------- | ------------ |
| Os ids (`CT-10001` × `T000001`) não cruzam | ❌ custa os dois entregáveis |
| A política tem 10 linhas, não 5.000 | ❌ custa o entregável 2 |
| A LGD de 40% contra os 67,8% da tabela | vale 0,44 ponto de ROI |
| O contrato fixado em R$ 15.000 | subestima o volume dele em 3× |
| O CSV e o documento trazem tabelas diferentes | ver 3b |

**Premissa** — e aqui ele não está errado:

O ROI acima de 15% **se sustenta** com os parâmetros do professor, desde que o
aceite seja alto. Não é artefato da LGD. É uma aposta sobre o comportamento do
cliente — e ele pode ganhar essa aposta.

**Se o simulador do professor for pouco elástico, a política do Deni é melhor
que a do Léo.** Se for elástico como o Léo supôs, ela fura o volume por R$ 1,8
milhão e perde metade da nota de política. É esse o trade-off que o grupo
precisa decidir, e não dá para decidir por argumento.

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

### 4.0 🔑 O material dele resiste à conferência

O documento do Marcelo é o mais rico em números verificáveis dos três. Testei
cada afirmação contra as bases do professor e contra o CSV que ele submeteu
(`python/analises/22_conferir_marcelo.py`). **Dezesseis de dezoito batem.**

**O que ele diz sobre a Base C — tudo confere:**

| Afirmação dele | Medido |
| -------------- | ------ |
| "39% (1.973) têm bureau < 460, 3+ restrições ou LTV > 95%" | ✅ 39,5% / **1.973** |
| "38% caem no score 1" | ✅ 37,9% |
| "3.102 propostas nos scores 2 a 10" | ✅ 3.104 |
| "2.461 aprovadas depois das regras" | ✅ **2.461** |
| "aprovar do score 5 daria 35,2%" | ✅ 34,9% |
| "do score 2, 62% antes das regras" | ✅ 62,1% |

**O que ele diz sobre a Base A — tudo confere:**

| Afirmação dele | Medido |
| -------------- | ------ |
| "default de 8,67% (2022)" | ✅ 8,67% |
| "8,94% (2023)" | ✅ 8,94% |
| "7,18% (2024)" | ✅ 7,18% |
| "ausentes: renda 7,7%" | ✅ 7,7% |

**A tabela contra o CSV — tudo confere:**

| Item | No documento | No CSV |
| ---- | ------------ | ------ |
| Aprovação | 49,2% | ✅ 49,2% |
| Taxa | 1,85% a 2,18%, ~1,95% | ✅ 1,85%–2,18%, média 1,96% |
| Prazos | 60, e 48 nos scores 2 e 3 | ✅ 48 e 60 |
| Entradas | 5% a 15% | ✅ 5%, 10%, 15% |
| Score mínimo | "scores 2 a 10" | ✅ 2 |
| Score de cada linha | pelos cortes publicados | ✅ bate em 98,2% |

**As afirmações econômicas:**

| Afirmação dele | Medido |
| -------------- | ------ |
| "perda de 2,0% do financiado no score 10" | ✅ 2,0% |
| "8,2% no score 2" | ✅ 8,5% |
| "precisa de ~45% de aceite para R$ 40 mi" | ✅ 45,2% |
| "ROI ~12% (11,8% a 12,3%)" | ≈ 13,16% |
| **"os juros somam cerca de 48% do volume"** | ❌ **67,1%** |

### A única divergência de verdade: os 48% de juros

Com taxa média de 1,96% e prazo médio de 57,3 meses, os juros somam **67,1%**
do valor financiado. Para dar 48% seria preciso cobrar 1,45% ao mês.

A explicação mais provável é troca de denominador:

| Cálculo | Resultado |
| ------- | --------- |
| juros ÷ valor **financiado** | 67,1% |
| **juros ÷ valor do bem** | **49,9%** ← perto dos 48% |
| juros ÷ total pago | 40,2% |

**É lapso de redação, não de cálculo.** Se ele tivesse usado 48% na conta do
ROI, o resultado seria 9%, não os 12% que ele reporta — e os 12% conferem. O
parágrafo está errado; o número que importa, não.

### A validação dele contra o default real de 2024

Refiz o teste que ele descreve — aplicar os preços da V3 aos contratos de 2024
com os defaults observados:

| | ROI |
| - | --- |
| ele reporta | 12,4% |
| refazendo aqui | **13,46%** |

A diferença de 1 ponto é esperada: a reprodução usa o modelo do Léo para
atribuir o score, não o dele. **A ordem de grandeza confere, e é a única
evidência do grupo que não depende do simulador de aceite.**

### O que isso quer dizer

O material do Marcelo é o mais auditável dos três. Números como "1.973
propostas" e "2.461 aprovadas" batem **exatamente**, o que só acontece quando
o documento é gerado a partir do mesmo código que produziu o CSV.

É o único dos três em que o CSV e o documento contam a mesma história.

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

### 4.3 Uma validação que ninguém mais fez

> *"aplicar os preços da V3 aos contratos de 2024 com os defaults reais dá
> ROI de 12,4%"*

Ele testou a precificação contra **default realizado**, não projetado. É uma
âncora independente do simulador de aceite — a maior fragilidade das três
frentes.

**É o que mais vale copiar.**

---

## 4b. 🔑 O Renato — o material que mais resiste ao pente fino

Ele entregou só a apresentação, sem CSVs. Mesmo assim é o material mais
verificável dos três, porque quase toda afirmação é numérica e rastreável
(`python/analises/23_conferir_renato.py`).

### As afirmações sobre as bases

| Afirmação dele | Medido |
| -------------- | ------ |
| "a inadimplência chegou a 8,3%" | ✅ 8,3% |
| "LTV médio da carteira é 74%" | ✅ 74% |
| "a retomada perde cerca de 70% do exposto" | ✅ 67,2% |
| "PD média de 8,4% na Base A" | ✅ 8,3% |
| **"36% (1.800) fora do domínio do treino"** | ✅ **36,0% / 1.800** |
| "estabilidade 0,44 na Base C, 0,02 na Base B" | ✅ 0,39 / 0,01 |
| "ausentes: bureau 3%, renda 8%, emprego 12%" | ✅ 3% / 8% / 12% |
| "PD média de 19,4% na Base C" | ≈ 14,8% — modelo diferente |

O **1.800 exato** é o mesmo tipo de sinal que apareceu no material do Marcelo:
só bate assim quando o slide é gerado do mesmo código que rodou a análise.

### O slide 9 — um contrato, passo a passo

Ele percorre os seis passos da cadeia num único financiamento. Refiz cada um:

| Passo | Ele diz | Medido |
| ----- | ------- | ------ |
| Fator de EAD | 1,032 | ✅ 1,032 |
| EAD | R$ 30.960 | ✅ R$ 30.960 |
| LGD da célula | 70,4% | ✅ 70,4% |
| Perda esperada | R$ 1.322 | ✅ R$ 1.330 |
| Parcela | R$ 1.039 | ✅ R$ 1.039 |
| Juros esperados | R$ 18.930 | ✅ R$ 18.924 |
| **ROI do contrato** | **14,7%** | ✅ **14,7%** |

**Os sete batem.** E o detalhe que mais impressiona é o dos juros: eles não são
os R$ 19.858 do contrato inteiro, e sim os **R$ 18.924 ponderados pela chance
de o cliente quebrar no meio**. Ele modela isso e declara no slide — *"quem dá
calote paga só até o mês da quebra"*.

> Na primeira conferência marquei este item como divergência, comparando com
> os juros integrais. **O erro era meu**: ele está certo, e mais rigoroso do
> que a comparação que fiz.

### A política dele no motor do Léo

| Cenário | ROI | Volume | Inadimplência | Guard-rails |
| ------- | --- | ------ | ------------- | ----------- |
| otimista | 12,79% | R$ 62,5 mi | 6,42% | ✅ todos |
| **central** | **12,53%** | R$ 46,1 mi | 6,86% | ✅ todos |
| pessimista | 12,18% | **R$ 29,3 mi** | 7,49% | ❌ volume |

Mesmo padrão dos outros: **ROI maior que o do Léo (12,53% contra 11,33%), e
volume que não sobrevive ao cenário pessimista.** Ele cobra mais caro nas
faixas boas (1,8% contra 1,63%) e dá 60 meses onde o Léo dá 48.

### 🔑 O teste que ele tem e o Léo não

Ele estressa a PD em +30% e mostra que os quatro limites seguem valendo. **É
uma dimensão de robustez que a análise do Léo não cobre** — o Léo varia o
aceite, não o risco.

Aplicando o mesmo estresse às duas políticas, no cenário central:

| | Inadimplência base | Com PD +30% | |
| - | ------------------ | ----------- | - |
| Renato | 6,86% | **8,91%** | ❌ estoura |
| **Léo** | 6,33% | **8,23%** | ❌ **estoura** |

**As duas quebram — inclusive a nossa.** Ele reporta 7,0% porque a composição
da carteira dele é outra sob as premissas de aceite dele; no motor do Léo, com
as elasticidades do Léo, nenhuma das duas aguenta.

Isso não desmente o teste dele — **valida a ideia**. Ter medido é o mérito, e é
uma lacuna real do nosso trabalho.

### O que vale copiar dele

| | Por quê |
| - | ------- |
| **Estresse de PD +30%** | robustez ao erro de nível do modelo, que a inferência de rejeitados torna provável |
| **"O CASE PEDE" em cada slide** | amarra cada página a uma exigência do enunciado — a banca não precisa procurar |
| **O slide do contrato passo a passo** | torna a cadeia PD → EAD → LGD → perda → preço → ROI concreta em números que dá para conferir |
| **Calibração declarada** | "previmos 8,5% e observamos 7,2%, erro a favor da segurança" |

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

**Urgente — avisar o Deni.** Quatro coisas, em ordem de custo:

1. **Os ids** (`CT-10001` contra `T000001`) e a política com 10 linhas em vez
   de 5.000 — invalidam os dois entregáveis, e são 15 minutos de conserto.
   **Isto é o que importa; o resto é refinamento.**
2. **As duas versões da tabela** (seção 3b) — decidir qual vale.
3. **A LGD de 40%** contra os 67,8% da tabela do professor.
4. **O contrato fixado em R$ 15.000**, que subestima o volume dele em 3×.
   Corrigir joga a favor dele.

Nada disso invalida o ROI acima de 15% dele, que se sustenta com os
parâmetros corretos desde que o aceite seja alto.

**Para a submissão do grupo**, a leitura que os números sustentam:

| Peça | De quem | Por quê |
| ---- | ------- | ------- |
| Modelo de PD | **Marcelo** | AuROC 0,72–0,75 com folga de 0,06; monotonicidade resolve o sobreajuste |
| Política e preço | **a decidir** | Léo se o aceite for elástico; Deni se não for — ver seção 3 |
| Regras de exclusão | **Marcelo** | mesmos limites que o Léo achou, com o argumento de domínio |
| Validação contra default real | **Marcelo** | âncora que não depende do simulador |
| Documento e defesa | **Léo** | cadeia completa, com a lacuna dos 15% medida e declarada |
| Estresse de risco | **Renato** | PD +30%: a dimensão que o Léo não cobriu, e que quebra as duas políticas |
| Narrativa por slide | **Renato** | o "O CASE PEDE" amarrando cada página ao enunciado |

**A juntar, se der tempo:** as restrições monotônicas no modelo e a validação
contra o default realizado de 2024. As duas vêm do Marcelo, e nenhuma passa
por cobrar mais caro.

**E o material do Renato**, assim que ele subir. Se os números dele batem com
os do Léo por caminhos diferentes, é a confirmação independente mais forte que
o grupo pode levar para a banca — e vale um parágrafo no documento de defesa.
