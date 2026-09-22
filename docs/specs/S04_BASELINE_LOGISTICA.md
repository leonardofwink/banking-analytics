# S04 · Baseline — regressão logística

> Passo 4 de 11 do [`ROADMAP.md`](../ROADMAP.md). Depende do S03. **O primeiro número de verdade.**

## Status das subetapas

| Subetapa | Entrega | DoD | Status | Commit |
| -------- | ------- | --- | ------ | ------ |
| S04.1 | `banking/modelo.py` — pré-processamento no `Pipeline` | 4/4 | ⬜ | — |
| S04.2 | Logística treinada no treino 2022–2023 | 3/3 | ⬜ | — |
| S04.3 | `avaliar()` — AuROC, KS, Gini, calibração | 4/4 | ⬜ | — |
| S04.4 | Variante sem variáveis dependentes da política | 3/3 | ⬜ | — |
| S04.5 | Coeficientes — a explicação para a defesa | 2/2 | ⬜ | — |
| S04.6 | Testes + pipeline | 3/3 | ⬜ | — |

## Objetivo

Um modelo de PD funcionando ponta a ponta, com **AuROC e KS medidos na validação 2024**, dentro de um `Pipeline` que garante que nada vaze do treino para a validação.

## Por que este passo existe

**Baseline é régua.** Sem ela, um AuROC de 0,72 não significa nada — pode ser fraco (se o problema for fácil) ou ótimo (se for difícil). Só dá para saber se o XGBoost vale a pena depois de existir um número de referência.

Mas a logística não é só régua aqui: é **candidata séria**. Ela é explicável coeficiente a coeficiente, e a defesa vale 20 pontos absolutos contra 30 relativos do AuROC. Se a diferença de performance for pequena, a logística ganha.

## O `Pipeline` não é organização — é o que vale 10 pontos

A rubrica cobra "sem vazamento, split correto, **Pipeline**, reprodutibilidade". O motivo é concreto: a imputação **aprende** uma mediana. Se essa mediana for calculada sobre treino + validação juntos, a validação influenciou o treino e o AuROC medido fica otimista — sem erro nenhum aparecer.

Dentro de um `Pipeline`, o `.fit()` acontece **só no treino** e o `.transform()` é aplicado aos demais. A garantia deixa de depender de disciplina e passa a ser estrutural.

**O que vai no pré-processamento:**

| Tipo | Tratamento | Por quê |
| ---- | ---------- | ------- |
| Numéricas | Imputação pela mediana **+ indicador de ausência** | O S03 mostrou que quem não tem `score_bureau` quebra 10,1% contra 8,8%. A ausência é informação: o indicador a preserva |
| Numéricas | Padronização | A logística é sensível à escala dos coeficientes |
| Categóricas | Imputação pela moda + one-hot com `handle_unknown="ignore"` | Categoria nova na base C não pode quebrar a escoragem |

## ⚠️ Duas variáveis de apoio ficam de fora, e não é por acaso

`taxa_juros_am` e `parcela_mensal` **não entram no modelo**, por dois motivos que se somam:

1. **Não existem na base C.** Lá não há taxa nem prazo contratado — essas condições são decisão nossa. Um modelo que dependesse delas não conseguiria escorar as propostas.
2. **Codificam a política antiga.** A taxa que a AutoCred cobrou reflete o risco que ela *percebeu* na época. Usar isso é deixar o modelo aprender a decisão velha — exatamente a política que o conselho considera quebrada.

## A variante que vamos testar

`comprometimento_renda` é `parcela_mensal / renda`, e a parcela depende da taxa e do prazo. Ela existe em A e B, mas em C só existiria **depois** que a política decidisse as condições.

Isso cria a circularidade descrita na [SPEC do entregável 1](../ENTREGAVEL_1_MODELO.md). Duas saídas:

- **Variante completa** — mantém a variável e resolve com escoragem em duas passagens no S10.
- **Variante independente de política** — descarta `comprometimento_renda` (e usa `ltv`, `prazo` e `valor_financiado` como *desejados*), eliminando a circularidade.

**Decisão declarada antes de ver o resultado:** se a diferença de AuROC for **menor que 0,01**, fica a variante independente — simplicidade e ausência de circularidade valem mais que um ganho dentro do ruído. Acima disso, mantemos a completa e pagamos o custo das duas passagens.

---

## Subetapas

### S04.1 · Pipeline de pré-processamento
`banking/modelo.py` com `construir_pipeline()`, montando `ColumnTransformer` + estimador.

**DoD:** ⬜ imputação e escala só aprendidas no treino · ⬜ indicador de ausência presente · ⬜ categoria desconhecida não quebra · ⬜ o objeto inteiro serializa.

### S04.2 · Treino
Ajustar no treino 2022–2023 com `SEMENTE` fixa.

**DoD:** ⬜ converge sem aviso · ⬜ duas execuções dão o mesmo AuROC · ⬜ nenhuma coluna proibida entre as usadas.

### S04.3 · Avaliação
`avaliar()` devolvendo AuROC, KS, Gini e erro de calibração.

**DoD:** ⬜ AuROC e KS na validação · ⬜ Gini = 2×AuROC−1 conferido · ⬜ PD média prevista comparada à taxa observada · ⬜ resultado em tabela.

### S04.4 · Variante independente de política
Mesmo pipeline, sem `comprometimento_renda`.

**DoD:** ⬜ as duas treinadas com o mesmo split e semente · ⬜ diferença de AuROC reportada · ⬜ escolha registrada pela regra declarada acima.

### S04.5 · Coeficientes
Tabela de coeficientes com sinal e magnitude — o insumo da defesa.

**DoD:** ⬜ coeficientes exportados · ⬜ **sinais conferidos contra o senso de crédito** (mais restrições deve aumentar a PD; score de bureau maior deve reduzir).

### S04.6 · Testes e pipeline
`tests/python/test_modelo.py` e `python/modelagem/04_baseline_logistica.py`.

**DoD:** ⬜ testes verdes · ⬜ pipeline roda do zero · ⬜ artefato do modelo salvo fora do git.

---

## DoD do S04 (o passo inteiro)

- [ ] AuROC e KS reportados na validação 2024
- [ ] Todo o pré-processamento dentro do `Pipeline`
- [ ] Reprodutível: duas execuções, mesmo número
- [ ] Variante escolhida pela regra declarada **antes** do resultado
- [ ] Sinais dos coeficientes coerentes com o domínio
- [ ] `pytest` verde
