# QA da defesa — AutoCred, Grupo 3

> **O que é este documento.** Uma simulação da arguição. Escrevi como se fosse
> o professor tentando nos derrubar: as perguntas estão na linguagem que ele
> usaria, e cada resposta é rastreável a um número que medimos.
>
> **Como usar.** Não decore o texto — decore os **oito números do cartão** (§0)
> e entenda o **porquê** de cada resposta. Na banca, responda curto primeiro:
> a resposta em negrito é a que se fala. O resto é munição para quando ele
> insistir — e ele vai insistir.
>
> **A regra de ouro.** Ele avisou como julga: *"o grupo que vencer não será o
> que tiver o maior AuROC. Será o que conseguir explicar, diante do conselho,
> por que aprovou quem aprovou, por que cobrou o que cobrou, e por que isso
> dava o retorno que dava."* Toda resposta deve fechar nesse trio.

---

## 0. O cartão — os oito números que todos precisam saber de cor

| | Número | Limite | Folga |
| - | ------ | ------ | ----- |
| AuROC (validação out-of-time) | **0,7234** | — | — |
| ROI anual (cenário central) | **11,33%** | meta 15% | ❌ não batemos — §5.1 |
| Volume originado (central) | **R$ 66,7 mi** | ≥ R$ 40 mi | +67% |
| **Volume no pior cenário** | **R$ 45,1 mi** | ≥ R$ 40 mi | **+12,7% ← o que mais aperta** |
| Inadimplência da carteira | **6,33%** | ≤ 8% | +21% |
| Taxa de aprovação | **59,5%** | ≥ 35% | +70% |
| Taxa de juros | **1,63% a 2,29% a.m.** | ≤ 3,5% | 1,21 pp na mesa |
| Contratos fechados | **1.829** de 2.976 aprovados | — | aceite 61,4% |

> 🔑 **E um nono número, que não é nosso resultado mas decide o argumento:**
> com inadimplência **zero**, o ROI seria **12,42%**. Nenhuma alavanca de risco
> chega aos 15% — só preço chega, e preço custa volume. Ver §1.1.

**A frase de abertura, se ele pedir o resumo em dez segundos:**

> *"Aprovamos 59,5% das propostas, cobramos de 1,63% a 2,29% ao mês conforme o
> risco, e isso rende 11,33% ao ano passando nos quatro guard-rails nos três
> cenários. Não batemos os 15% — e medimos que, com estas premissas de aceite,
> ninguém bate sem furar o volume."*

---

## 1. As três perguntas que ele vai fazer com certeza

### 1.1 "Vocês não bateram a meta de 15%. Por quê?"

**Resposta curta:** *"Porque medimos que 15% e os guard-rails não coexistem
sob as nossas premissas de aceite. Testamos 26.400 políticas; 16.820 passam
dos 15% e nenhuma sobrevive aos quatro limites nos três cenários."*

**A prova mais limpa** — a nossa própria política, com o preço mais agressivo:

| `k_risco` | taxa | ROI central | volume no pior cenário | |
| --------- | ---- | ----------- | ---------------------- | - |
| **0,10 (escolhido)** | 1,63%–2,29% | **11,33%** | **R$ 45,1 mi** | ✅ viável |
| 0,20 | 1,77%–3,08% | 13,54% | R$ 27,4 mi | ❌ volume |
| **0,30** | 1,90%–3,50% | **15,46%** ← bate a meta | **R$ 17,9 mi** | ❌ volume |
| 0,50 | 2,17%–3,50% | 18,56% | R$ 9,2 mi | ❌ volume e inadimplência |

> **Diga isto:** *"Nós temos uma política que bate os 15%. É a linha do
> `k_risco` 0,30: ROI de 15,46%. Ela morre no guard-rail de volume, que cai
> para R$ 17,9 mi contra o piso de R$ 40 mi. Preferimos entregar 11,33%
> viável a 15,46% que o conselho rejeita."*

**Três caminhos independentes chegam ao mesmo teto**, o que descarta erro de
implementação em um deles:

| Caminho | Teto viável |
| ------- | ----------- |
| Varredura de 26.400 políticas | 11,97% |
| Varredura de prazo e entrada por faixa | 11,42% |
| Trocando o nosso modelo pelo do Marcelo | 11,54% |

**E o argumento que encerra a discussão — a aritmética do numerador:**

```
ROI = (juros − perda) / volume / prazo = (33,12 − 2,90) / 66,68 / 4 = 11,33%

A perda é R$ 2,90 mi contra R$ 33,12 mi de juros: 8,8% da receita.
Com perda ZERO:  33,12 / 66,68 / 4 = 12,42%
```

> **Diga isto quando ele sugerir mexer no risco:** *"Mesmo com inadimplência
> zero — modelo perfeito, nenhum calote — o ROI seria 12,42%. Faltariam 2,58
> pontos para a meta. Isso significa que **nenhuma alavanca de risco** chega
> aos 15%: nem corte mais duro, nem entrada maior, nem teto de comprometimento.
> O que nos separa da meta é preço, e preço custa volume."*

Para ROI de 15% seriam precisos R$ 42,91 mi de juros — **+29,6%** —, o que leva
a taxa média de 1,86% para ~2,41% a.m. É exatamente a linha do `k_risco` 0,30
acima, e é onde o volume morre.

**Se ele insistir "então a meta era impossível?":** *"Não necessariamente — ela
é impossível **com a nossa premissa de elasticidade**. Se o cliente for 5×
menos sensível a preço do que supusemos, 15% é alcançável. Não temos como
saber: o enunciado dá a direção de cada efeito e declara que a intensidade não
está dada. Foi a única premissa que tivemos de inventar, e declaramos isso."*

### 1.1b ⚠️⚠️ "Seu próprio painel mostra uma política viável que rende 11,97%. Por que vocês submeteram a de 11,33%?"

**A pergunta mais perigosa do dia, e ela vem do nosso próprio material.**
Responda com a tabela, não com adjetivos.

| | ROI central | Volume no pior caso | Folga até o piso |
| - | ----------- | ------------------- | ---------------- |
| **A que submetemos** | 11,33% | R$ 45,08 mi | **+12,7%** |
| A de maior ROI viável | **11,97%** | R$ 40,03 mi | **+0,1%** |

**Resposta curta:** *"Porque ela sobrevive ao nosso cenário pessimista por
R$ 30 mil. E o cenário pessimista é uma premissa nossa, não um dado."*

**A munição, se ele apertar** — os quatro limites das duas, no pior cenário:

| Limite | A nossa | A de 11,97% |
| ------ | ------- | ----------- |
| Aprovação | +70,1% | +96,4% |
| Inadimplência | +17,8% | +18,5% |
| Taxa máxima | +34,5% | **+0,4%** |
| Volume | **+12,7%** | **+0,1%** |

> *"A nossa tem um gargalo com 12,7% de margem. A de 11,97% tem **dois**
> gargalos com menos de meio por cento: a taxa a 0,01 ponto do teto e o volume
> a R$ 30 mil do piso. Ela rende 0,65 ponto a mais no cenário que projetamos, e
> quebra no primeiro cenário que não projetamos."*

**E o argumento que fecha:** *"O senhor escreveu que furar um guard-rail corta
a nota de política pela metade. Estávamos escolhendo entre ganhar 0,65 ponto de
ROI e arriscar metade da nota num limite cuja folga depende de uma elasticidade
que o próprio enunciado diz não estar dada. Preferimos o retorno que aguenta a
premissa estar errada."*

💡 **Por que levar isso à banca em vez de torcer para não perguntarem:** o
painel mostra a fronteira inteira, com o ótimo destacado em verde. Ele vai ver.
Um grupo que conhece a política melhor que a sua e sabe dizer por que não a
escolheu está numa posição muito mais forte do que um que se surpreende com ela.

### 1.2 "Por que aprovaram quem aprovaram?"

**Resposta curta:** *"O corte é score ≥ 5. Não foi escolhido pelo risco — foi
escolhido pelo volume."*

| Corte | Aprovação | ROI | Volume central | **Volume pior** | Inadimplência | |
| ----- | --------- | --- | -------------- | --------------- | ------------- | - |
| **≥ 5** | **59,5%** | **11,33%** | R$ 66,7 mi | **R$ 45,1 mi** | 6,33% | ✅ |
| ≥ 6 | 50,5% | 11,21% | R$ 60,3 mi | R$ 41,8 mi | 5,53% | ✅ |
| ≥ 7 | 40,1% | 11,05% | R$ 51,0 mi | R$ 36,4 mi | 4,83% | ❌ volume |

> **O argumento:** *"Cortar mais fundo não melhora o ROI — piora. E no corte 7
> o volume morre. A faixa 5 não entrou por generosidade: ela é a que sustenta
> a margem de volume que nos mantém viáveis no pior cenário."*

### 1.3 "Por que cobraram o que cobraram?"

**Resposta curta:** *"A taxa de cada faixa é o custo do dinheiro mais a perda
esperada daquela faixa. Não é tabelada por feeling — sai de uma fórmula."*

```
taxa da faixa = 1,50% a.m. (base)  +  0,10 × perda esperada da faixa
```

| Faixa | Taxa | Volume | Margem (juros − perda) | Margem relativa |
| ----- | ---- | ------ | ---------------------- | --------------- |
| 10 | 1,63% | R$ 9,7 mi | R$ 3,9 mi | 10,12% |
| 9 | 1,71% | R$ 12,0 mi | R$ 5,0 mi | 10,35% |
| 8 | 1,79% | R$ 16,1 mi | R$ 6,9 mi | 10,69% |
| 7 | 1,91% | R$ 13,2 mi | R$ 5,8 mi | 11,00% |
| 6 | 2,08% | R$ 9,3 mi | R$ 4,3 mi | 11,48% |
| **5** | **2,29%** | R$ 6,3 mi | R$ 3,0 mi | **11,77%** |

> **O fecho:** *"Toda faixa se paga, e a margem cresce com o risco — que é
> exatamente o que se espera de um preço bem calibrado. Se a faixa 5 desse
> prejuízo, ela não estaria na tabela."*

---

## 2. Bloco de negócio

### 2.1 "Qual é o problema da AutoCred, na sua leitura?"

*"A AutoCred financia com LTV médio de 74%, mas tem contratos chegando a 95%.
Quando o cliente quebra, a retomada recupera pouco: a LGD fica em torno de 70%,
contra 45% a 55% de bancos estabelecidos. Ou seja — a empresa está emprestando
perto do valor do bem e recuperando mal. O problema não é ter inadimplência, é
não estar cobrando o preço certo por ela."*

### 2.2 "O que a sua política muda na prática?"

*"Três coisas. Primeira: entrada mínima de 10%, que trava o LTV em 90% e tira
a carteira da faixa em que a LGD explode — na prática a entrada média fica em
25%, porque o cliente já quer dar mais. Segunda: preço por faixa de risco, de
1,63% a 2,29% — hoje a empresa não diferencia. Terceira: um corte objetivo em
score 5, no lugar da regra antiga."*

### 2.3 "Por que o conselho deveria aprovar 11,33% e não exigir mais?"

*"Porque os 11,33% vêm com uma garantia que os números maiores não têm:
sobrevivem ao cenário pessimista. Se o aceite do cliente vier 30% pior do que
projetamos, ainda originamos R$ 45,1 mi e passamos em todos os limites. As
políticas de ROI mais alto entregam mais no papel e quebram o compromisso de
crescimento na primeira contrariedade."*

### 2.4 ⚠️ "Vocês aprovam 59,5%. A política antiga aprovava quanto? Não estão afrouxando?"

**A armadilha:** não temos esse número — as Bases A e B só contêm aprovados.
Não invente.

*"Não sabemos, e não temos como saber: as Bases A e B só trazem quem a política
antiga aprovou. O que sabemos é que a carteira antiga rodava com 8,26% de
inadimplência e a nossa projeta 6,33%. Estamos aprovando com um critério
explícito e um preço que cobre a perda — o que não é afrouxar, é precificar."*

---

## 3. Bloco de modelo

### 3.1 ⚠️ "Qual é o seu AuROC na Base B?"

**A pegadinha:** a Base B não tem o alvo. Quem responder um número está
inventando ou vazou de algum lugar.

**Resposta curta:** *"Não temos como calcular — a Base B veio sem o alvo, o
gabarito está com o senhor. O que reportamos é o nosso melhor proxy honesto:
**0,7234 na validação out-of-time interna da Base A**, separando os últimos
meses do período de treino."*

**Se ele perguntar "e na Base A inteira?":** *"0,8576. Mas esse número inclui
os dados de treino e não vale nada como estimativa — é justamente o erro contra
o qual o senhor nos alertou. Reportamos 0,7234 porque é o único defensável."*

> 💡 Esta resposta ganha pontos. Muita gente vai reportar o número inflado.

### 3.2 ⚠️ "Que variáveis vocês usaram? Alguma delas não existia na concessão?"

*"Removemos cinco colunas marcadas 'Disponível na concessão? = NÃO'. A mais
perigosa é a **`qtd_parcelas_em_atraso_12m`**: ela aparece nas três bases, o
que dá a impressão de ser utilizável — mas é constante zero nas Bases B e C.
Quem a usa vê o AuROC subir na Base A e o modelo morrer na aplicação. As outras
quatro são os realizados: `mes_default`, `ead_realizado`, `lgd_realizado` e
`perda_financeira`."*

**O detalhe que impressiona:** *"Não jogamos os realizados fora — usamos como
gabarito para conferir se interpretamos corretamente as suas tabelas de EAD e
LGD. Eles saem da base de modelagem e vão para um arquivo separado."*

### 3.3 "Seu modelo é um XGBoost. Como você explica uma negativa ao cliente?"

*"A negativa não vem do modelo — vem da política. O cliente recebe 'seu score
ficou em 4, e aprovamos a partir de 5'. O score é uma faixa de 1 a 10, é
auditável e é o mesmo para todo mundo. O modelo ordena o risco; quem decide é a
tabela, e a tabela cabe em uma página."*

**Se ele insistir em interpretabilidade:** *"Para atender ao regulador temos a
importância das variáveis e a análise de contribuição por proposta. E medimos o
custo de não usar o XGBoost: a regressão logística perde poder de ordenação, e
essa perda se converte em preço errado nas pontas."*

### 3.4 ⚠️ "O PSI entre a Base A e a Base C é de 0,39. Seu modelo não vale nada lá."

**A pegadinha mais técnica.** Ele está certo no número e errado na conclusão.

**Resposta curta:** *"O PSI de 0,3899 confirma o que o senhor escreveu no
enunciado: a Base C é mar aberto e inclui perfis que a política antiga recusava.
É inferência de rejeitados, e era esperado. O contraste importante é que o PSI
entre A e B é de **0,0070** — o modelo está estável no tempo. O que mudou não
foi a população ao longo dos meses, foi o filtro de quem chega até nós."*

**E a consequência que tiramos:** *"É por isso que a nossa política não aposta
tudo no modelo. O corte é conservador, a entrada de 10% é exigida de todos, e o
preço tem margem sobre a perda esperada. Tratamos o modelo como bom para
ordenar, não como oráculo para extrapolar."*

### 3.5 ⚠️ "36% da Base C está fora do domínio do seu treino. Quantos desses vocês aprovaram?"

**Resposta curta:** *"346 propostas — **11,6% dos nossos aprovados**. O filtro
natural do score já derrubou a maioria: eram 1.800 na base inteira."*

**Se ele perguntar por que não negamos todos automaticamente:**

*"Porque negar por estar fora do domínio é assumir que a política antiga estava
certa ao recusá-los — que é exatamente o viés que a inferência de rejeitados
denuncia. Se fizéssemos isso, estaríamos reproduzindo a política que a AutoCred
quer substituir. Optamos por deixar o score decidir e monitorar: esses 11,6%
entram com acompanhamento separado no plano de implantação."*

### 3.6 "Seu modelo está calibrado?"

*"Está. Na Base A, a PD média prevista é 8,29% e a inadimplência realizada é
8,26% — um erro de **0,03 ponto percentual**. Isso importa mais que o AuROC
para nós, porque a taxa é construída sobre a perda esperada: um modelo
descalibrado precifica errado mesmo ordenando bem."*

### 3.7 "Como vocês validaram? Split aleatório?"

*"Não. Split temporal, como o senhor pediu: treino nos períodos mais antigos,
validação no período seguinte. A validação cruzada é `TimeSeriesSplit`. E todo
o pré-processamento que aprende com o dado — imputação, encoding, padronização
— está dentro de um `Pipeline` do scikit-learn, ajustado só no treino."*

---

## 4. Bloco de política e precificação

### 4.1 ⚠️⚠️ "Vocês aprovam faixas com inadimplência de 9,1% e 13,3%. Seu guard-rail é 8%. Como justificam?"

**Esta é a pergunta mais perigosa do documento.** Ela está correta nos fatos.

**Resposta curta:** *"O guard-rail é sobre a carteira, e a carteira fecha em
6,33%. As faixas 5 e 6 têm inadimplência acima de 8% isoladamente — e são
cobradas mais caro exatamente por isso."*

**A munição, se ele apertar:**

> *"A faixa 5 é a que **mais** contribui para o resultado: margem relativa de
> 11,77%, contra 10,12% da faixa 10. Ela gera R$ 3,0 milhões de margem sobre
> R$ 6,3 milhões de volume. O preço de 2,29% ao mês não é punição, é o que a
> perda daquela faixa custa — e sobra."*

**E o teste que fizemos antes de decidir:**

| Se cortássemos a faixa 5 | ROI | Volume pior |
| ------------------------ | --- | ----------- |
| Com ela (corte ≥ 5) | 11,33% | R$ 45,1 mi |
| Sem ela (corte ≥ 6) | 11,21% | R$ 41,8 mi |

*"Cortar a faixa 5 piora o ROI e come quase toda a nossa folga de volume.
Ficaríamos com 4,5% de margem sobre o piso em vez de 12,7% — mais frágeis, não
mais seguros."*

### 4.2 "Por que 48 meses para todo mundo? Cadê a diferenciação por prazo?"

**Resposta honesta:** *"Testamos prazo por faixa numa varredura dedicada, com
24, 36, 48 e 60 meses. O ganho foi marginal e veio junto com perda de aceite
nas faixas boas. Preferimos uma tabela simples que a operação executa sem erro
a uma tabela sofisticada que rende 0,04 ponto a mais no papel."*

**Se ele apontar que 60 meses aumentaria o aceite:** *"Aumenta o aceite e
alonga a exposição ao risco — o senhor colocou isso na tabela de alavancas.
Nos nossos testes o efeito líquido não compensou, e 48 meses mantém a carteira
girando mais rápido."*

> ⚠️ **Cuidado:** esta pergunta é sobre *diferenciar* o prazo por faixa. Se ele
> for pelo outro lado — *"vocês dão 48 a quem pediu 24"* — é a §4.5, e a
> resposta lá é uma concessão, não uma defesa. Não misture as duas.

### 4.3 ⚠️⚠️ "Entrada de só 10%? O mercado pratica 20% a 30%. Vocês estão emprestando com LTV de 90%."

**Provavelmente a pergunta de negócio mais forte que ele pode fazer.** A
resposta tem três camadas, e a primeira desarma a premissa.

**Camada 1 — a carteira não é de entrada 10%:**

> *"Os 10% são o piso, não a prática. A entrada **efetiva média** dos nossos
> aprovados é de **25%** — dentro do padrão de mercado que o senhor citou. A
> mediana do que o cliente já quer dar é 20%, então o piso de 10% só morde
> 21% da carteira. O LTV médio ofertado é de 71,7% a 78,8% por faixa, não 90%."*

| Score | Entrada efetiva média | No piso de 10% | LTV ofertado |
| ----- | --------------------- | -------------- | ------------ |
| 10 | 28,3% | 3,9% | 71,7% |
| 8 | 24,8% | 11,8% | 75,2% |
| 6 | 23,0% | 21,7% | 77,0% |
| **5** | **21,2%** | **25,1%** | **78,8%** |

**Camada 2 — mas ele tem razão na direção:** *"O senhor está certo que a
alavancagem se concentra nas faixas piores: 25,1% do score 5 fica no piso,
contra 3,9% do score 10. Por isso o preço da faixa 5 é 2,29% e o da 10 é 1,63%."*

**Camada 3 — e medimos o que custaria exigir mais:**

| Entrada | ROI | Volume pior | |
| ------- | --- | ----------- | - |
| **10% (atual)** | **11,33%** | **R$ 45,1 mi** | ✅ |
| 20% | 11,37% | R$ 39,4 mi | ❌ volume |
| 30% | 11,42% | R$ 30,8 mi | ❌ volume |
| 40% | 11,59% | R$ 21,6 mi | ❌ volume |

*"Subir para 20% rende **+0,04 ponto de ROI** e custa **R$ 5,7 milhões** de
volume no pior cenário — o suficiente para furar o guard-rail. A entrada não é
uma alavanca de retorno: é uma alavanca de risco, e o risco já não é o que nos
separa da meta."*

**Se ele perguntar pela entrada escalonada por faixa** (exigir mais de quem tem
score pior — a versão mais inteligente da crítica):

| Entrada | ROI | Volume pior | Inadimpl. | Aguenta PD errar |
| ------- | --- | ----------- | --------- | ---------------- |
| 10% fixa (atual) | 11,33% | R$ 45,1 mi | 6,33% | +26,3% |
| 20% a 10% | 11,33% | R$ 42,8 mi | 6,24% | — |
| 30% a 10% | 11,31% | **R$ 39,6 mi** ❌ | 6,20% | **+29,1%** |

*"Testamos. É conceitualmente superior — melhora a robustez em 2,8 pontos, que
é a nossa fragilidade principal. Mas a versão que entrega essa robustez fura o
volume por R$ 0,4 milhão. A versão que cabe troca 5,7 pontos de folga de volume
por 0,09 ponto de inadimplência. No limite que mais aperta, não compensou."*

### 4.4 ⚠️ "Vocês não limitaram o comprometimento de renda? A parcela não pode passar de 25% a 30% da renda."

**A resposta contraintuitiva — e é medida.**

**Resposta curta:** *"Não limitamos, e não foi esquecimento: medimos que o
corte de score já captura o comprometimento. Na nossa carteira o DTI mediano é
de 20,3%, e 31,2% dos aprovados passam de 25%."*

**A prova — inadimplência REAL na Base A, por faixa de score:**

| Score | DTI ≤ 30% | DTI > 30% | diferença |
| ----- | --------- | --------- | --------- |
| 8 | 1,70% | 0,29% | **−1,41 pp** |
| 7 | 5,19% | 3,41% | **−1,78 pp** |
| 6 | 7,82% | 8,04% | +0,23 pp |
| 5 | 11,73% | 10,57% | −1,16 pp |
| — | — | — | — |
| 4 | 16,35% | 21,94% | +5,59 pp |
| 2 | 32,34% | 41,57% | **+9,23 pp** |

> **O argumento:** *"Nas faixas que **aprovamos**, comprometimento alto não
> piora a inadimplência — em várias ela é menor. O DTI só machuca nas faixas 1
> a 4, que já negamos. A leitura de crédito é conhecida: entre bons pagadores,
> parcela grande é sinal de quem **pode** assumi-la; entre maus pagadores, é
> aperto real. O nosso corte já separou os dois."*

**O efeito no resultado, se aplicássemos o teto mesmo assim:**

| Teto de DTI | ROI | Volume pior | Inadimpl. | Aprovação |
| ----------- | --- | ----------- | --------- | --------- |
| **sem teto (atual)** | **11,33%** | **R$ 45,1 mi** | 6,33% | 59,5% |
| 30% | 11,33% | R$ 35,3 mi ❌ | 5,71% | 46,9% |
| 25% | 11,32% | R$ 30,9 mi ❌ | 5,50% | 40,9% |

*"O ROI não se move um centésimo — 11,33% para 11,32%. O teto corta volume sem
melhorar retorno, porque corta gente que não era mais arriscada."*

⚠️ **A ressalva honesta, se ele apertar:** *"Esse resultado carrega uma
limitação: a Base A só tem quem a política antiga aprovou. Se ela já filtrava
por comprometimento, quem tem DTI alto e passou pode ter sido filtrado em outra
dimensão. Não temos como descartar isso."*

**Se ele perguntar por que não usamos como preditora:** → §6.5, a circularidade.
São coisas diferentes: como preditora ela é circular; como **regra de política
aplicada depois da oferta**, não é — e foi assim que testamos.

### 4.5 ⚠️⚠️ "Vocês ofertam 48 meses a quem pediu 24. Não estão alongando a exposição de graça?"

**A pergunta mais perigosa deste bloco, e a que menos esperamos.** Ele tem
razão nos fatos.

**Os números, sem rodeio:**

| Pediu | n | Recebeu | PD do pedido | PD ofertada | |
| ----- | - | ------- | ------------ | ----------- | - |
| 24 | 620 | 48 | 6,06% | 6,58% | **+0,52 pp** |
| 36 | 838 | 48 | 5,81% | 6,94% | **+1,13 pp** |
| 48 | 899 | 48 | 6,02% | 5,82% | −0,21 pp |
| 60 | 619 | 48 | 5,55% | 4,99% | −0,56 pp |

**49% dos aprovados recebem mais prazo do que pediram.**

**Resposta curta:** *"Sim, e é uma decisão consciente. A alavanca do enunciado
se chama **prazo máximo**, e o exemplo de submissão que o senhor nos deu oferta
prazo mais longo que o pedido em metade das linhas — conferimos contra ele
antes de decidir."*

**E medimos o custo de não fazer isso:**

| | ROI central | Volume | Inadimplência |
| - | ----------- | ------ | ------------- |
| **48 para todos (atual)** | **11,33%** | R$ 66,7 mi | 6,33% |
| respeitando o prazo pedido | 11,21% | **R$ 66,7 mi** | **5,70%** |

> **A concessão honesta, se ele insistir:** *"Essa é provavelmente a alavanca
> de risco mais barata que deixamos na mesa. Respeitar o prazo pedido custaria
> 0,12 ponto de ROI e **não custaria volume nenhum** — o volume é o valor
> financiado, que não depende do prazo — e melhoraria a inadimplência em 0,63
> ponto. É a melhor troca risco/retorno que encontramos, e escolhemos o ROI.
> Numa segunda rodada, é o primeiro item que eu revisitaria."*

💡 **Por que responder assim:** ele vai gostar mais de um grupo que conhece a
própria lacuna e a quantificou do que de um que a esconde. Compare com §8.

### 4.6 ⚠️ "Seu teto é 3,5% e vocês param em 2,29%. Deixaram 1,21 ponto na mesa."

**Resposta curta:** *"Deixamos de propósito, e medimos o que aconteceria se não
tivéssemos deixado."* → mostrar a tabela de `k_risco` da §1.1.

*"Chegar perto do teto empurra o ROI para 15,46%, mas leva o volume a R$ 17,9
milhões no pior cenário. E há um segundo efeito que o enunciado declara: taxa
alta atrai o cliente errado. A nossa seleção adversa está modelada — quem
aceita pagar caro tem PD maior. Cobrar o teto compraria receita e risco ao
mesmo tempo."*

### 4.7 "Como vocês agruparam as PDs em dez faixas?"

*"Por cortes de PD, com a convenção do enunciado: 1 é o pior risco e 10 o
melhor. A escolha tem consequência, como o senhor sinalizou — faixas largas
demais misturam riscos diferentes no mesmo preço, e faixas estreitas demais
ficam com pouca gente e preço instável. As nossas faixas aprovadas têm entre
337 e 627 propostas cada, o que nos pareceu o equilíbrio."*

---

## 5. Bloco de ROI e guard-rails

### 5.1 "Mostre a conta do ROI."

```
ROI anual = [ (juros recebidos − perda realizada) ÷ volume originado ] ÷ prazo médio em anos
          = [ (R$ 33,12 mi − R$ 2,90 mi) ÷ R$ 66,68 mi ] ÷ 4,00
          = 11,33%
```

*"Volume originado de R$ 66,68 milhões em 1.829 contratos, prazo médio de 4
anos exatos porque ofertamos 48 meses a todos."*

### 5.2 ⚠️ "Vocês contaram os juros do contrato inteiro para quem deu calote?"

**Pegadinha direta do enunciado.**

*"Não. Quem quebra no mês 4 pagou quatro parcelas. O motor pondera os juros
pela probabilidade de sobrevivência do contrato até cada mês — é por isso que
os juros recebidos são R$ 33,12 milhões e não o valor do contrato cheio."*

### 5.3 ⚠️ "Proposta aprovada que o cliente recusou entrou na sua conta?"

*"Não. Aprovamos 2.976 propostas, mas só **1.829** viram contrato — um aceite
de 61,4%. O volume de R$ 66,7 milhões é dos 1.829. Se contássemos todos os
aprovados, seria R$ 108 milhões, e seria uma conta errada: proposta recusada
não gera receita nem prejuízo, ela simplesmente não existe."*

### 5.4 ⚠️⚠️ "E se sua PD estiver errada? Estresse ela em 30%."

**A pergunta que quebra a nossa política. Responda com o número antes que ele
descubra.**

| Choque na PD | Inadimplência | ROI | |
| ------------ | ------------- | --- | - |
| 0% | 6,33% | 11,33% | ✅ |
| +10% | 6,97% | 11,16% | ✅ |
| +20% | 7,60% | 10,98% | ✅ |
| **+26,3%** | **8,00%** | — | **⚠️ o ponto de virada** |
| +30% | 8,23% | 10,81% | ❌ fura o guard-rail |

**Resposta curta:** *"A política aguenta a PD errar até **+26,3%** antes de
furar o guard-rail de inadimplência. Acima disso, fura — e o senhor está certo
em apontar isso como a nossa fragilidade principal."*

**O contrapeso:** *"Duas coisas dão conforto. O erro de calibração medido na
Base A é de 0,03 ponto percentual, muito longe de 26%. E o ROI é robusto mesmo
no choque: cai de 11,33% para 10,81%, porque o preço já carrega a perda
esperada. O que quebra é o limite de inadimplência, não a rentabilidade."*

**Se ele perguntar "e o que vocês fariam?":** *"O plano de implantação prevê
revisão trimestral do corte. Com a PD realizada 20% acima do previsto, subimos
o corte para 6 — perdemos R$ 6,4 milhões de volume e voltamos para 5,53% de
inadimplência, dentro do limite."*

### 5.5 "Sua política passa nos três cenários?"

| Cenário | ROI | Volume | Inadimplência | Aprovação | Violações |
| ------- | --- | ------ | ------------- | --------- | --------- |
| Otimista | 11,51% | R$ 86,1 mi | 6,16% | 59,5% | nenhuma |
| **Central** | **11,33%** | **R$ 66,7 mi** | **6,33%** | **59,5%** | **nenhuma** |
| Pessimista | 11,09% | R$ 45,1 mi | 6,58% | 59,5% | nenhuma |

*"Nos três. E note que a taxa de aprovação não muda: ela é decisão nossa. O que
muda entre cenários é quanta gente aceita a oferta."*

### 5.6 ⚠️ "De onde vieram essas elasticidades? Você as inventou."

**Ele tem razão, e a melhor defesa é concordar primeiro.**

*"Inventamos, sim — e é a única premissa do trabalho que não sai dos dados. O
enunciado declara a direção de cada efeito e diz explicitamente que a
intensidade não está dada, e que não há como descobri-la por tentativa e erro
porque submetemos uma vez só."*

*"O que fizemos foi não depender de um chute único: montamos três cenários com
elasticidades de preço variando de 0,8 a 2,5, e só consideramos viável a
política que passa nos quatro guard-rails **nos três**. É uma decisão tomada
sob incerteza declarada, não um número disfarçado de certeza."*

### 5.7 "Por que não deixam o dinheiro rendendo no CDI para ajudar o ROI?"

**Pergunta de banca esperta — e a resposta é contraintuitiva.**

*"Olhamos. O capital não fica imobilizado os quatro anos: pela Tabela Price ele
volta em parcelas. O saldo devedor médio é de R$ 38,3 milhões contra R$ 66,7
milhões originados — o capital realmente empregado é 57% do originado, e sobre
ele o retorno é 19,72%."*

*"Mas aplicar o que volta no CDI não fecha a conta, porque traz junto o custo de
ter captado o dinheiro. A 9% ao ano, o ganho sobre o caixa ocioso é +3,60
pontos e o custo de captação sobre o saldo devedor é −4,86 pontos: **líquido de
−1,26 ponto**. O saldo devedor médio é maior que o ocioso médio, então o custo
supera o ganho em qualquer CDI."*

---

## 6. Os pega-ratão

Perguntas construídas para induzir uma resposta errada. A armadilha está
marcada em cada uma.

### 6.1 "Seu AuROC de 0,72 é baixo. O grupo X entregou 0,85."

🪤 **A armadilha:** aceitar a comparação e parecer inferior.

*"Depende de onde o 0,85 foi medido. Na Base A inteira o nosso também dá 0,8576
— mas esse número inclui o treino. O único AuROC comparável é o que o senhor vai
calcular na Base B, e nenhum de nós tem esse número. Reportamos a validação
out-of-time porque é a que estima o desempenho fora do tempo."*

### 6.2 "Então vocês admitem que uma política mais agressiva ganharia mais dinheiro?"

🪤 **A armadilha:** responder "sim" isolado vira "vocês deixaram dinheiro na
mesa".

*"Ganharia mais ROI e originaria menos. O senhor escreveu o guard-rail de volume
justamente para impedir a política degenerada: aprovar no papel, cobrar o teto,
exigir entrada alta e fechar pouquíssimos contratos — ROI excelente e empresa
parada. A nossa escolha foi a que o guard-rail pede."*

### 6.3 "Se o guard-rail de volume não existisse, qual seria sua política?"

🪤 **A armadilha:** revelar que a política foi desenhada para o limite, não
para o negócio.

*"Seria outra, e o senhor sabe disso — é o ponto do guard-rail. Mas a resposta
honesta é que o volume não é uma amarra artificial: a AutoCred precisa crescer.
Uma financeira que otimiza ROI encolhendo a carteira está gerindo a liquidação
dela, não o negócio."*

### 6.4 "Vocês olharam o resultado da Base C antes de escolher a política?"

🪤 **A armadilha:** admitir overfitting na base de aplicação.

*"Escolhemos a política por varredura sobre cenários de premissa, não por
tentativa e erro na Base C — até porque a Base C não tem desfecho fixo: o que
acontece com cada proposta depende das condições que ofertarmos. Não há um
resultado para espiar."*

### 6.5 ⚠️ "Por que vocês descartaram o comprometimento de renda? É a variável mais óbvia de crédito."

🪤 **A armadilha:** parece descuido. É o contrário — é a decisão mais sutil do
modelo.

*"Porque ela é circular na Base C. O comprometimento de renda depende da
parcela, e a parcela depende da taxa e do prazo que **nós** vamos ofertar. Nas
Bases A e B ela existe porque o contrato já foi fechado; em C teríamos de
recalculá-la a partir da nossa própria decisão de política — o modelo passaria a
prever o risco usando como insumo a condição que ele mesmo vai ajudar a
definir."*

**O número, se ele quiser saber o custo:** *"Medimos as duas versões. Incluí-la
rende +0,0060 de AuROC — diferença dentro do ruído. Trocamos esse nada por
eliminar a circularidade."*

**Mesma lógica para duas outras:** *"`taxa_juros_am` e `parcela_mensal` também
ficaram fora, e por um motivo a mais: elas codificam a decisão da política
antiga — justamente a que o conselho considera quebrada. Um modelo que as usa
aprende a reproduzir o critério que viemos substituir."*

### 6.6 "Sua taxa mínima é 1,63%. O mercado está em quanto?"

🪤 **A armadilha:** se respondermos "abaixo do mercado", parece que damos
dinheiro; se "acima", parece que afastamos cliente.

*"A referência que usamos como condição de aceite neutro é 1,59% ao mês. A nossa
faixa 10 sai a 1,63% — praticamente no mercado, que é o preço certo para o
melhor risco. Quem paga mais que o mercado, na nossa tabela, é quem traz mais
perda esperada."*

### 6.7 "Vocês usaram regra rígida ou só o score?"

*"Só o score e a tabela. Não temos regra rígida de negativa fora do modelo. É
uma decisão consciente: cada regra rígida que se empilha é uma decisão que sai
do critério auditável e vira exceção difícil de explicar ao regulador."*

### 6.8 "Quem no grupo fez o quê? E você, sabe explicar o que o outro fez?"

🪤 **A armadilha clássica** — ele pergunta a parte do modelo para quem fez
política, e vice-versa.

**Ninguém responde "isso foi o fulano que fez".** Todos precisam saber o
essencial dos três blocos. Se a pergunta for técnica demais, passe a bola com
a resposta começada: *"O corte temporal a gente definiu junto, o Deni implementou
— Deni, conta o detalhe."*

---

## 7. Quando não soubermos a resposta

Três formas de sair sem perder pontos. Todas melhores que inventar um número.

1. **"Não medimos isso. O que medimos foi X, que chega perto pelo lado Y."**
2. **"Não sabemos — e essa informação não está nas bases que recebemos."**
   (Vale para: quanto a política antiga aprovava, o AuROC na Base B, a
   elasticidade verdadeira.)
3. **"Esse é um ponto frágil do nosso trabalho. O que fizemos para cercá-lo
   foi Z."** — usar para o estresse de PD e para as elasticidades.

> ⚠️ **Nunca** diga um número que não esteja neste documento ou no deck. O
> professor conhece as bases melhor que nós, e um número inventado derruba a
> credibilidade de todos os outros.

---

## 8. O que o Renato tem e nós não

Ele testou a PD em +30% e reportou que a política dele resiste. Nós fizemos o
mesmo teste depois, e ele **quebra a nossa política** (§5.4). Duas atitudes
possíveis na banca, e a segunda é melhor:

❌ Esconder e torcer para não perguntarem.
✅ **Trazer nós mesmos**, com o ponto de virada medido: *"a política aguenta a
PD errar até +26,3%"*. Antecipar a objeção vale mais que sobreviver a ela.

**As duas lacunas que conhecemos e quantificamos.** Se sobrar tempo na
apresentação, dizê-las é ganho líquido — mostra que auditamos o próprio
trabalho:

| Lacuna | O que custaria corrigir |
| ------ | ----------------------- |
| Estresse de PD: quebramos em +26,3% (§5.4) | subir o corte para 6 com a PD 20% acima do previsto |
| Prazo alongado para 49% dos aprovados (§4.5) | −0,12 pp de ROI, **zero** de volume, −0,63 pp de inadimplência |

A segunda é a mais barata que deixamos passar, e é a que eu levaria para uma
próxima rodada.

---

## Anexo — a tabela de política, para consulta rápida

| Score | Decisão | Taxa a.m. | Prazo | Entrada mínima | Propostas | Inadimplência isolada |
| ----- | ------- | --------- | ----- | -------------- | --------- | --------------------- |
| 10 | APROVAR | 1,63% | 48 | 10% | 337 | 2,87% |
| 9 | APROVAR | 1,71% | 48 | 10% | 432 | 3,88% |
| 8 | APROVAR | 1,79% | 48 | 10% | 627 | 4,65% |
| 7 | APROVAR | 1,91% | 48 | 10% | 610 | 6,15% |
| 6 | APROVAR | 2,08% | 48 | 10% | 520 | 9,14% |
| 5 | APROVAR | 2,29% | 48 | 10% | 450 | 13,33% |
| 4 a 1 | NEGAR | — | — | — | — | — |

**Carteira consolidada: 6,33% de inadimplência, dentro do limite de 8%.**
