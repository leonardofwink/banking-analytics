# Glossário — risco, crédito e modelagem

> Vocabulário comum do projeto. Sempre que um termo da mentoria aparecer pela primeira vez, registre aqui.
> Quando código e documentação usam a mesma palavra com o mesmo sentido, a discussão para de girar em torno de "o que você quis dizer com X".

---

## 1. Gestão de risco — o eixo inerente → controle → residual

Esta é a espinha dorsal conceitual do projeto. Os três termos só fazem sentido juntos.

### Risco inerente

O risco **bruto**, medido **antes** de qualquer controle. É a exposição natural da atividade: existe pelo simples fato de o banco emprestar dinheiro.

> *Exemplo:* conceder crédito pessoal sem garantia para um público de baixa renda tem risco inerente alto — é da natureza do produto, independentemente do quão bom seja o banco.

Medir o inerente exige um exercício de imaginação honesto: **se nenhum controle existisse, qual seria a probabilidade e o impacto?** É comum times subestimarem o inerente porque já estão olhando para a operação com os controles rodando.

### Controle / mitigador

Qualquer mecanismo deliberado que reduz a **probabilidade** de o evento ocorrer, o **impacto** caso ocorra, ou os dois.

Em crédito, os mitigadores clássicos — repare em qual componente da perda cada um ataca:

| Mitigador | Atua sobre | Como |
| --------- | ---------- | ---- |
| Política de crédito (regras de corte) | PD | Barra perfis fora do apetite antes da concessão |
| **Modelo de score / PD** | PD | Ordena o risco e permite um *cutoff* defensável |
| Limite de crédito | EAD | Reduz o quanto se pode perder se der errado |
| Garantia / colateral / alienação | LGD | Recupera parte do valor após o default |
| Seguro prestamista, cessão de carteira | LGD | **Transfere** o risco a um terceiro |
| Régua de cobrança | LGD | Recupera crédito já vencido |
| Provisão (ECL) | — | Absorve a perda **esperada** sem quebrar o resultado |
| Capital regulatório | — | Absorve a perda **inesperada** |

### Risco residual

O que **sobra** depois de os controles funcionarem. É o risco que o banco de fato carrega.

```
Risco residual  =  Risco inerente  −  efeito dos controles
```

A conta acima é conceitual, não aritmética: a redução depende de os controles estarem **desenhados corretamente** *e* **operando de fato**. Um controle que existe só no papel reduz o risco residual em zero — e essa é a armadilha mais comum em auditoria.

O residual é comparado ao **apetite a risco**. Três desfechos possíveis:

- **Residual ≤ apetite** → aceitar e monitorar.
- **Residual > apetite** → mitigar mais (novo controle, ou controle mais forte) ou reduzir a exposição.
- **Residual muito abaixo do apetite** → possível **excesso de controle**: dinheiro gasto em mitigação que o negócio não pediu, e crédito bom sendo recusado.

### Mitigar riscos — as quatro respostas

Mitigar é **uma** das quatro estratégias possíveis. Vale nomear todas, porque confundi-las gera decisão errada:

1. **Evitar** — não entrar no negócio / descontinuar o produto. O único que zera o risco inerente.
2. **Mitigar (reduzir)** — implantar controles que baixem probabilidade ou impacto. É o terreno da modelagem de crédito.
3. **Transferir** — passar o impacto a terceiro (seguro, resseguro, cessão, securitização). O risco não some: muda de dono — e nasce um risco de contraparte no lugar.
4. **Aceitar (reter)** — assumir conscientemente, com provisão e capital. Decisão legítima quando o retorno paga o risco.

> ⚠️ **Aceitar não é o mesmo que ignorar.** Aceitar é uma decisão registrada, com dono, limite e monitoramento. Ignorar é não ter medido.

### Apetite e tolerância a risco

- **Apetite a risco** — quanto risco a instituição *quer* correr para atingir seus objetivos. Declaração estratégica, do conselho.
- **Tolerância** — a variação aceitável em torno do apetite, expressa em métrica operacional (ex.: "inadimplência 90+ da safra entre 4% e 6%").
- **Limite** — o valor que dispara ação quando ultrapassado.

Sem apetite declarado, "risco residual alto" é uma opinião. Com apetite declarado, é um fato mensurável.

---

## 2. Risco de crédito — os componentes da perda

### Perda esperada (EL — *Expected Loss*)

Como apresentado na mentoria:

```
Perda esperada  =  PD (%)  ×  EAD (R$)  ×  LGD (%)
```

| Componente | Pergunta que responde | Unidade |
| ---------- | --------------------- | ------- |
| **PD** — *Probability of Default* | Qual a chance de o cliente dar calote? | % (0 a 1) |
| **EAD** — *Exposure at Default* | Quanto ele vai estar me devendo nessa hora? | R$ |
| **LGD** — *Loss Given Default* | Desse valor, quanto eu não recupero? | % (0 a 1) |

> ⚠️ **Atenção às unidades.** Só a EAD é em reais; PD e LGD são percentuais. O resultado sai em **R$** — é dinheiro, não taxa. O erro clássico é somar ou multiplicar os três como se fossem todos percentuais, ou esquecer que PD "5%" no código precisa ser `0.05` e não `5`.

*Exemplo numérico:* PD = 5% · EAD = R$ 10.000 · LGD = 60% → **EL = 0,05 × 10.000 × 0,60 = R$ 300**.
Ou seja: espera-se perder R$ 300 nesse contrato. Não é o que vai acontecer com *aquele* cliente (ele paga tudo ou dá default), é a média esperada quando se olha para **mil contratos iguais a ele**.

**Onde isso entra na prática:** a EL é **custo de operação**, não surpresa. Ela é embutida no preço (spread) e vira **provisão** no balanço. Um banco que não cobre a EL no spread está vendendo com prejuízo estrutural.

**Ligação com a seção 1:** cada mitigador ataca um fator da fórmula — score e política derrubam a **PD**, limite derruba a **EAD**, garantia e cobrança derrubam a **LGD**. É por isso que a perda esperada é a tradução *em reais* do risco residual da carteira.

### Perda inesperada (UL — *Unexpected Loss*)

A volatilidade em torno da EL — o quanto a perda pode superar a média num ano ruim. **Não** é coberta por provisão; é coberta por **capital**. É aqui que Basileia mora.

> Mnemônico: **perda esperada → provisão (resultado); perda inesperada → capital (patrimônio).**

### Default

A definição de default é uma **escolha do projeto**, não uma verdade universal — e muda todos os números. O padrão de mercado é **atraso ≥ 90 dias** (90+), mas pode incluir gatilhos qualitativos (renegociação forçada, recuperação judicial). **Registre a definição adotada no [PRD](PRD.md) antes da primeira modelagem.**

---

## 3. Modelagem e scorecard

| Termo | O que é |
| ----- | ------- |
| **ABT** (*Analytical Base Table*) | A tabela final de modelagem: uma linha por cliente/contrato, com as variáveis explicativas e a flag de default |
| **Binning** | Agrupamento de uma variável contínua em faixas, geralmente otimizado para maximizar a separação entre bons e maus |
| **Calibração** | O score prevê 3% de default e 3% acontece? Ordenar bem (discriminação) e acertar o nível (calibração) são coisas diferentes |
| **Cutoff** | Ponto de corte do score que separa aprovação de recusa. É decisão **de negócio**, não estatística: depende do trade-off entre perda e receita |
| **Gini / AUC** | Poder de ordenação. `Gini = 2 × AUC − 1` |
| **IV** (*Information Value*) | Poder preditivo de uma variável isolada. Referência usual: < 0,02 inútil · 0,1–0,3 médio · > 0,5 suspeito de vazamento |
| **Janela de observação** | Período *antes* da concessão de onde vêm as variáveis. Não pode invadir a janela de performance — isso é vazamento |
| **Janela de performance** | Período após a concessão em que se observa se o cliente deu default (ex.: 12 meses) |
| **KS** (Kolmogorov-Smirnov) | Máxima distância entre as distribuições acumuladas de bons e maus. Métrica preferida do mercado de crédito |
| **MOB** (*Months on Book*) | Meses desde a originação. Curvas de inadimplência se leem por MOB, nunca por data de calendário |
| **Matriz de transição** | Generalização do roll rate: probabilidade de migrar entre todos os estados de atraso |
| **PSI** (*Population Stability Index*) | Mede se a população atual ainda parece a de desenvolvimento. Referência: < 0,1 estável · 0,1–0,25 atenção · > 0,25 recalibrar |
| **Reject inference** | Tratamento do viés de só termos performance de quem foi aprovado. Ignorar isso enviesa todo scorecard de reaprovação |
| **Restrição monotônica** | Amarra imposta ao modelo para que uma variável só empurre o risco numa direção — mais restrições no bureau **nunca** podem reduzir a PD prevista. Impede o modelo de aprender relações que contrariam o bom senso a partir de ruído da amostra. Custa pouco poder de discriminação e compra muita **defensabilidade**: sem ela, a resposta a *"por que este cliente pagou mais?"* pode ser indefensável num comitê |
| **Roll rate** | Probabilidade de migrar de uma faixa de atraso para a seguinte (ex.: 30→60 dias) |
| **Safra** (*vintage*) | Grupo de contratos originados no mesmo período. A unidade de análise em crédito — carteiras só são comparáveis dentro da mesma safra |
| **Swap set** | Quem o modelo novo aprova e o antigo recusava (e vice-versa). É onde se enxerga o ganho real de trocar de modelo |
| **WOE** (*Weight of Evidence*) | Transformação que substitui a categoria pelo log da razão entre bons e maus. Lineariza a variável e trata missing como categoria |

---

## 4. Regulação e provisionamento

| Termo | O que é |
| ----- | ------- |
| **Basileia (II / III)** | Acordos de capital. Origem da tríade PD/LGD/EAD e da separação perda esperada × inesperada |
| **ECL** (*Expected Credit Loss*) | A provisão sob IFRS 9 — a perda esperada levada ao balanço |
| **Estágios 1 / 2 / 3** | 1: sem deterioração relevante → ECL de 12 meses. 2: aumento significativo de risco (SICR) → ECL *lifetime*. 3: já em default → ECL *lifetime* com juros sobre o líquido |
| **IFRS 9** | Norma contábil internacional de instrumentos financeiros. Provisão por **perda esperada**, não por perda incorrida |
| **Res. CMN 2.682/1999** | O regime brasileiro anterior: provisão por faixa de atraso e rating AA a H. Ainda aparece em base histórica |
| **Resolução CMN 4.966/2021** | A adaptação brasileira do IFRS 9, vigente desde 2025. Substitui a 2.682 |
| **RWA** | *Risk-Weighted Assets* — ativo ponderado pelo risco, base do requerimento de capital |
| **SCR** | Sistema de Informações de Créditos do BCB — o histórico de crédito que as instituições consultam e alimentam |
| **SICR** | *Significant Increase in Credit Risk* — o gatilho que move do estágio 1 para o 2. Definir esse gatilho é decisão de modelagem com efeito direto no resultado |

---

## 5. Rentabilidade — o outro lado da balança

Risco sozinho não decide nada. Uma carteira de risco zero é uma carteira que não empresta — e não ganha dinheiro. A pergunta certa nunca é "qual o risco?", e sim **"o retorno paga o risco?"**.

### ROE — retorno sobre o capital

Como apresentado na mentoria:

```
ROE  =  (Receita − Perda)  /  Volume negociado
```

| Componente | O que é |
| ---------- | ------- |
| **Receita** | O que a operação gera: juros, tarifas, *spread* |
| **Perda** | A perda esperada da carteira (a `EL` da seção 2) |
| **Volume negociado** | O montante emprestado — o capital colocado em risco |

A leitura: **de cada real emprestado, quanto sobra depois de descontar a perda.** É a métrica que amarra as duas metades do projeto — a modelagem de risco produz o termo `Perda`, e é só aí que dá para dizer se a operação vale a pena.

*Exemplo:* carteira de R$ 1.000.000 · receita de R$ 180.000 · perda esperada de R$ 30.000 → ROE = (180.000 − 30.000) / 1.000.000 = **15%**.

**Por que isso muda a discussão sobre o cutoff:** subir o corte do score derruba a perda — e derruba a receita junto, porque recusa cliente bom. Descer o corte faz o inverso. O cutoff ótimo não é o que minimiza a perda; é o que **maximiza o ROE**. Um modelo de crédito avaliado só por KS ou Gini responde metade da pergunta.

> ℹ️ **Nota de vocabulário** (útil para quem vier de fora do banking): a sigla ROE, na contabilidade clássica, é *Return on Equity* = **lucro líquido / patrimônio líquido** — retorno sobre o capital **do acionista**. A fórmula apresentada na aula usa o **volume negociado** no denominador, o que a aproxima de um **retorno sobre ativos** ou de um **RAROC simplificado**. Não é erro: em análise de carteira é comum usar a versão simplificada, porque o que interessa ali é a rentabilidade *daquela* operação, não a da instituição inteira. Só vale saber que as duas definições circulam com o mesmo nome — **ao ler um número de ROE, confirme sempre qual é o denominador.**

### Termos vizinhos

| Termo | O que é |
| ----- | ------- |
| **RAROC** | *Risk-Adjusted Return on Capital* — a formalização da ideia acima: `(receita − custos − perda esperada) / capital econômico`. Permite comparar produtos de risco muito diferente na mesma régua |
| **ROA** | *Return on Assets* — lucro sobre o ativo total |
| **ROE contábil** | *Return on Equity* — lucro líquido / patrimônio líquido |
| **NIM** | *Net Interest Margin* — margem financeira: receita de juros menos custo de captação, sobre o ativo rentável |
| **Índice de eficiência** | Despesa operacional / receita. Quanto **menor**, melhor — é uma das poucas métricas bancárias em que menos é mais |
| **Custo de captação** | O que o banco paga para ter o dinheiro que empresta. O piso de qualquer precificação |

### Elasticidade do aceite — quanto o cliente foge quando o preço sobe

**Elasticidade** é o quanto uma quantidade reage à variação de outra. Aqui: **quantos clientes desistem da proposta a cada ponto de taxa a mais**.

No motor de ROI ela aparece como o `β` de uma curva exponencial:

```
aceite = a0 · e^(−β · excesso)        excesso = taxa cobrada / taxa de mercado − 1
```

- `β` **alto** = cliente sensível a preço, foge rápido. `β` **baixo** = cliente aguenta preço maior.
- `a0` é o aceite na condição de referência — quanto fecha quando você cobra exatamente o preço de mercado.

**Por que é o número mais perigoso do projeto:** ele não está nos dados. Cobrar mais aumenta a receita por contrato e diminui o número de contratos, e é a elasticidade que decide qual dos dois efeitos ganha. Errá-la para cima faz uma política lucrativa parecer inviável — foi exatamente o que aconteceu, e está em [`processo/POST_MORTEM.md`](processo/POST_MORTEM.md).

### Âncora de preço — a régua contra a qual "caro" é medido

"Caro" não existe sozinho: existe **em relação a alguma coisa**. A âncora de preço é essa referência — o preço que o cliente encontraria **se fosse ao concorrente**.

Ela entra como denominador do excesso, e por isso escolhe-la errada distorce tudo o que vem depois:

| Âncora | Cobrar 2,5% a.m. parece… |
| ------ | ------------------------ |
| 1,59% (a média da nossa própria carteira antiga) | **57% acima do mercado** |
| 2,3% (mediana das instituições, dado público do BCB) | **9% acima do mercado** |

**A regra prática:** a âncora tem de vir de **fora da sua própria operação**. O preço que você mesmo pratica não mede o mercado — mede você. No Brasil, o Banco Central publica as taxas médias por modalidade e por instituição, e é dado público.

### RAROC — precificar pelo retorno que se quer, não pelo custo que se tem

*Risk-Adjusted Return on Capital.* Em vez de somar margem em cima do custo (**cost-plus**: `preço = custo + perda esperada + margem`), inverte-se a pergunta: **qual preço entrega o retorno-alvo, dado o risco daquele cliente?**

| Abordagem | Como se define o preço |
| --------- | ---------------------- |
| **Cost-plus** | parte do custo e soma margem — o preço é consequência |
| **RAROC** | parte do retorno exigido e resolve para o preço — o retorno é a restrição |

É o que bancos fazem de fato, e a diferença aparece quando o retorno tem piso contratual: no cost-plus você descobre o ROI no fim e torce; no RAROC ele é a entrada.

> ⚠️ **A ressalva que o professor fez:** preço calculado contrato a contrato *"é um algoritmo, não uma tabela de política — funciona, mas é difícil de defender num comitê"*. Uma **tabela fixa por faixa de score**, validada contra referência externa, é menos ótima e mais defensável — e foi a que venceu o desafio.

---

## 6. Termos de negócio bancário

| Termo | O que é |
| ----- | ------- |
| **Carteira** | O conjunto de contratos ativos |
| **Churn** | Perda de cliente |
| **LTV** (*Lifetime Value*) | Valor esperado do cliente ao longo do relacionamento. Em crédito, **líquido da perda esperada** |
| **LTV** (*Loan-to-Value*) | ⚠️ Sigla homônima, sentido diferente: razão entre o valor do empréstimo e o da garantia. O contexto manda |
| **NPL** (*Non-Performing Loan*) | Crédito em atraso relevante (geralmente 90+). `NPL ratio` = NPL / carteira |
| **Originação** | O ato de conceder o crédito. "Safra de originação" = quando o contrato nasceu |
| **Recuperação** | Valor recebido após o default. Entra no cálculo da LGD |
| **Renegociação** | Alteração de condições para viabilizar o pagamento. Cuidado: "cura" artificialmente o atraso e mascara a inadimplência real |
| **Spread** | Diferença entre a taxa cobrada e o custo de captação. É de onde sai o pagamento pela perda esperada |
| **Write-off** | Baixa contábil do crédito considerado irrecuperável. Some da carteira e distorce o NPL ratio se não for tratado |

---

> **Convenção:** termo novo entra na seção certa, em ordem alfabética dentro da tabela, com uma linha de definição e — quando for uma decisão do projeto, como a definição de default — um ponteiro para onde ela está registrada.
