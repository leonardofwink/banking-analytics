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

**A frase de abertura, se ele pedir o resumo em dez segundos:**

> *"Aprovamos 59,5% das propostas, cobramos de 1,63% a 2,29% ao mês conforme o
> risco, e isso rende 11,33% ao ano passando nos quatro guard-rails nos três
> cenários. Não batemos os 15% — e medimos que, com estas premissas de aceite,
> ninguém bate sem furar o volume."*

---

## 1. As três perguntas que ele vai fazer com certeza

### 1.1 "Vocês não bateram a meta de 15%. Por quê?"

**Resposta curta:** *"Porque medimos que 15% e os guard-rails não coexistem
sob as nossas premissas de aceite. Testamos 5.600 políticas; 4.044 passam dos
15% e nenhuma sobrevive ao guard-rail de volume."*

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
| Varredura de 5.600 políticas (S12) | 11,46% |
| Varredura de prazo e entrada por faixa | 11,42% |
| Trocando o nosso modelo pelo do Marcelo | 11,54% |

**Se ele insistir "então a meta era impossível?":** *"Não necessariamente — ela
é impossível **com a nossa premissa de elasticidade**. Se o cliente for 5×
menos sensível a preço do que supusemos, 15% é alcançável. Não temos como
saber: o enunciado dá a direção de cada efeito e declara que a intensidade não
está dada. Foi a única premissa que tivemos de inventar, e declaramos isso."*

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

*"Três coisas. Primeira: entrada mínima de 10% para todo mundo, o que trava o
LTV em 90% e tira a carteira da faixa em que a LGD explode. Segunda: preço por
faixa de risco, de 1,63% a 2,29% — hoje a empresa não diferencia. Terceira: um
corte objetivo em score 5, no lugar da regra antiga."*

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

### 4.3 "Por que entrada de 10% e não mais?"

*"Porque medimos os dois lados. A entrada de 10% derruba a PD reescorada de
6,38% para 6,12% — e isso é medido **reescorando** as propostas com o LTV novo,
não estimado. Ela também trava o LTV máximo em 90%, tirando a carteira da faixa
onde a LGD dispara."*

*"Acima disso, o aceite começa a cair mais rápido do que o risco melhora. E o
senhor mesmo avisou: exigir muito derruba o aceite do cliente."*

### 4.4 ⚠️ "Seu teto é 3,5% e vocês param em 2,29%. Deixaram 1,21 ponto na mesa."

**Resposta curta:** *"Deixamos de propósito, e medimos o que aconteceria se não
tivéssemos deixado."* → mostrar a tabela de `k_risco` da §1.1.

*"Chegar perto do teto empurra o ROI para 15,46%, mas leva o volume a R$ 17,9
milhões no pior cenário. E há um segundo efeito que o enunciado declara: taxa
alta atrai o cliente errado. A nossa seleção adversa está modelada — quem
aceita pagar caro tem PD maior. Cobrar o teto compraria receita e risco ao
mesmo tempo."*

### 4.5 "Como vocês agruparam as PDs em dez faixas?"

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
