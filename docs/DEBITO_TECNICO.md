# Débito técnico — o que foi cortado pelo prazo

> **Por que este documento existe:** o prazo é 25/09 e o projeto começou em 13/09. Várias decisões foram tomadas *porque o relógio mandou*, não porque são as melhores. Sem registro, daqui a um mês ninguém distingue **"fizemos assim porque é certo"** de **"fizemos assim porque não deu tempo"** — e a segunda vira dogma.
>
> Cada item traz: o que deixamos de fazer, qual o risco de não ter feito, e o que faríamos com mais tempo.
>
> **Uso na defesa (20 pts):** reconhecer limitação com precisão é sinal de domínio, não de fraqueza. "Não fizemos reject inference, e a consequência é esta" vale mais que silêncio — o professor sabe que não fizemos.

---

## 1. 🔴 Reject inference não será tratado

**O que deixamos de fazer:** as bases A e B só têm contratos **aprovados** pela política antiga; a base C é mar aberto. O tratamento formal desse descasamento (*reject inference*: parcelling, augmentation, fuzzy augmentation) não entra nesta entrega.

**O risco, agora medido (S03):** o PSI confirma e dimensiona. A base B é praticamente idêntica à A; a base C é outro mundo — e justamente nas duas variáveis **mais preditivas**:

| Variável | IV (poder no treino) | PSI A→B | PSI A→C |
| -------- | -------------------- | ------- | ------- |
| `score_bureau` | **0,176** (1º lugar) | 0,002 | **0,496** 🔴 |
| `qtd_restricoes_ativas` | **0,133** (2º lugar) | 0,000 | **5,93** 🔴🔴 |
| `renda_mensal_declarada` | 0,114 | 0,005 | 0,141 🟡 |

PSI de 5,93 está fora de qualquer escala usual (a referência de mercado trata 0,25 como instável). As demais variáveis ficam abaixo de 0,09 — ou seja, **a instabilidade é concentrada, não difusa**, o que é uma boa notícia: sabemos exatamente onde o modelo vai extrapolar.

O modelo vai apoiar-se nas duas variáveis mais fortes exatamente onde elas menos se parecem com o treino. A **ordenação** tende a sobreviver; o **nível** da PD, não — e provavelmente **subestima** o risco de quem a política velha recusava. Como a política precifica em cima dessa PD, o efeito prático é **cobrar barato demais de quem é caro**.

**Mitigação adotada:** tratar a PD como *ordenação confiável, nível suspeito*; medir o PSI entre A/B e C para dimensionar a extrapolação; embutir margem de segurança no preço das faixas baixas.

**Com mais tempo:** parcelling sobre a base C usando a PD do modelo, recalibração do intercepto para a prevalência esperada em mar aberto, e comparação do swap set.

---

## 2. 🟡 Comparação de modelos pode não acontecer (S05)

**O que deixamos de fazer:** o enunciado pede testar regressão logística, Random Forest e XGBoost. O plano de prazo torna **S05 opcional** — se o tempo apertar, entregamos só a logística.

**O risco:** perder AuROC. Modelos de árvore costumam ganhar da logística em dado tabular com interação, e o AuROC vale 30 pontos **relativos ao melhor grupo** — se os outros grupos usarem XGBoost e nós não, a diferença aparece direto na nota.

**Mitigação adotada:** a logística é candidata legítima e a mais fácil de defender (20 pts de defesa são absolutos). Entregar um CSV válido com modelo simples vale mais que um modelo bom sem CSV.

**Com mais tempo:** os três com o mesmo pipeline, mesmo split, mesma semente, e a escolha justificada pela diferença medida.

---

## 3. 🟡 Feature engineering mínima

**O que deixamos de fazer:** usar as variáveis como vieram, sem construir derivadas (razão parcela/renda ajustada, interações LTV × idade do veículo, agrupamento de canal por risco, tratamento de `score_bureau` ausente como categoria própria).

**O risco:** deixar AuROC na mesa. `score_bureau` nulo (3,3%) provavelmente **não é aleatório** — é quem não tem histórico no bureau, o que é informação de risco, não ruído. Imputar pela mediana joga esse sinal fora.

**Mitigação adotada:** criar um indicador binário de "sem bureau" já no pipeline da logística — é barato e captura a maior parte do sinal.

**Com mais tempo:** binning ótimo com `optbinning`, WOE por variável, análise de IV, e interações testadas contra a validação.

---

## 4. 🟡 As elasticidades da base C são premissa, não medida

**O que deixamos de fazer:** o simulador do professor tem curva de aceite e seleção adversa cujas **intensidades não são reveladas** — e a submissão é única, sem feedback. Não há como calibrar.

**O risco:** a política inteira é escolhida sob premissa. Se a elasticidade real for muito diferente da assumida, o ponto de operação sai errado — e como os guard-rails cortam a nota pela metade, errar para o lado errado é caro.

**Mitigação adotada:** decidir por **cenários** (otimista, central, pessimista) e escolher a política **robusta nos três**, não a ótima no central. Testar sensibilidade do ROI a ±10 pontos de aceite.

**Com mais tempo:** nada mudaria — é limitação do desafio, não nossa. Mas daria para explorar mais cenários e mapear a fronteira de quebra de cada guard-rail.

---

## 5. 🟠 O ajuste de avalista da LGD tem viés conhecido (e vamos usar assim mesmo)

**O que descobrimos (S02):** a tabela de LGD do professor reproduz a **média por célula** dos inadimplentes da base A com erro de 0,0003 — ela é exata. Mas essa média **já inclui a mistura de contratos com e sem avalista** (19,7% dos inadimplentes têm avalista).

Aplicar a regra oficial — *"some −0,061 à LGD da tabela quando o contrato tem avalista"* — em cima de uma média que já embute o efeito **conta o benefício duas vezes**:

| Regra | Viés médio contra o realizado |
| ----- | ----------------------------- |
| Oficial (`−0,061` só para avalista) | **−0,0121** — subestima a perda |
| Centrada (`−0,061×(1−s)` / `+0,061×s`, com s = 19,7%) | **−0,0001** — praticamente sem viés |

**O risco:** 1,2 ponto percentual de LGD subestimada em toda a carteira. Sobre uma LGD média de ~0,70, é ~1,7% de perda a menos do que a real — dinheiro que não entra no preço.

**Decisão:** usamos a **regra oficial** como padrão, porque é o parâmetro declarado e a coerência com o enunciado vale 10 pontos. A versão centrada fica implementada e disponível, e o viés conhecido é **compensado explicitamente na margem de segurança da precificação**, em vez de ser corrigido por fora do parâmetro oficial.

**Com mais tempo:** levar a questão ao professor antes da entrega. É possível que a intenção fosse que a tabela representasse só os sem avalista.

---

## 6. 🟢 Sem calibração formal da PD

**O que deixamos de fazer:** verificar se a PD prevista bate com a frequência observada (curva de calibração, Brier score, recalibração isotônica ou de Platt).

**O risco:** o AuROC mede **ordenação**; a política precisa de **nível**. Um modelo pode ordenar perfeitamente e ainda assim dizer 5% onde o real é 9% — e a perda esperada, que vira preço, sai errada na mesma proporção.

**Mitigação adotada:** conferir a PD média prevista contra a taxa de default observada na validação. É pobre comparado a uma curva de calibração, mas pega erro grosseiro.

**Com mais tempo:** curva de calibração por decil e recalibração antes de usar a PD na precificação.

---

## 7. 🟢 Sem validação cruzada — só um holdout temporal

**O que deixamos de fazer:** validação cruzada temporal (*walk-forward*) com várias janelas.

**O risco:** a estimativa de AuROC vem de **uma** partição (validação = 2024, 3.330 contratos, 239 defaults). Com essa amostra, o intervalo de confiança do AuROC é largo — diferenças menores que ~0,02 entre modelos podem ser ruído, e escolher o "melhor" pode ser escolher o mais sortudo.

**Mitigação adotada:** regra de desempate declarada **antes** de ver os números: diferença menor que 0,01 de AuROC → fica o modelo mais simples.

**Com mais tempo:** walk-forward com 3 janelas (treina 2022 → valida 2023; treina 2022-23 → valida 2024) e intervalo de confiança por bootstrap.

---

## 8. 🟢 Sem testes de fairness / variável proxy

**O que deixamos de fazer:** verificar se alguma variável funciona como proxy de característica protegida, e se a aprovação fica desbalanceada entre grupos.

**O risco:** baixo neste desafio (a base não tem gênero, raça ou CEP), mas `ocupacao`, `idade_cliente` e `tipo_residencia` podem carregar correlação socioeconômica. Em produção real isso seria bloqueante.

**Com mais tempo:** análise de disparate impact por faixa etária e ocupação.

---

## Resumo por prioridade

| # | Débito | Gravidade | Custo de corrigir |
| - | ------ | --------- | ----------------- |
| 1 | Reject inference | 🔴 alta | alto — dias |
| 5 | Viés do ajuste de avalista | 🟠 média-alta | baixo — já medido |
| 2 | Sem RF/XGBoost | 🟡 média | médio — horas |
| 3 | Feature engineering mínima | 🟡 média | médio |
| 4 | Elasticidades como premissa | 🟡 média | impossível (limite do desafio) |
| 6 | Sem calibração formal | 🟢 baixa-média | baixo |
| 7 | Só um holdout | 🟢 baixa | médio |
| 8 | Sem fairness | 🟢 baixa (aqui) | baixo |

> **Regra:** item resolvido **sai daqui e vira nota na spec correspondente**. Débito que fica marcado como "resolvido" neste documento polui a leitura e faz o resto parecer menos urgente.
