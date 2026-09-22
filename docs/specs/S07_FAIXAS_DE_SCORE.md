# S07 · Faixas de score (PD → 1 a 10)

> Passo 7 de 11 do [`ROADMAP.md`](../ROADMAP.md). Abre a frente da política.

## Status das subetapas

| Subetapa | Entrega | DoD | Status | Commit |
| -------- | ------- | --- | ------ | ------ |
| S07.1 | Critérios de uma boa faixa, declarados antes | 3/3 | ⬜ | — |
| S07.2 | `banking/score.py` — cortes e `score_de_pd()` | 4/4 | ⬜ | — |
| S07.3 | Distribuição verificada nas três bases | 3/3 | ⬜ | — |
| S07.4 | Perda esperada por faixa | 3/3 | ⬜ | — |
| S07.5 | Testes + relatório | 3/3 | ⬜ | — |

## Objetivo

Uma função determinística `PD → score de 1 a 10`, com **10 = melhor risco** e **1 = pior**, como manda o enunciado.

## Por que isso não é detalhe

O enunciado é explícito: *"toda decisão de política se apoia no score, não na PD bruta"*, e *"como agrupar as PDs nessas dez faixas é escolha de vocês — e é uma escolha com consequência"*.

A consequência é direta:

- **Faixa larga demais** cobra o mesmo preço de riscos diferentes. Quem está no piso da faixa subsidia quem está no teto — e o cliente bom vai para o concorrente que o precifica direito.
- **Faixa estreita demais** cria faixas com pouca gente, que não sustentam uma decisão de preço e viram ruído na tabela.

## ⚠️ Cortes por PD absoluta, não por quantil

Esta é a decisão estrutural do passo.

**Quantil** (os 10% piores viram score 1) é o caminho fácil e está errado aqui: o significado da faixa muda quando a população muda. E a base C **é** outra população — o S03 mediu PSI de 5,93 em `qtd_restricoes_ativas` e 0,50 em `score_bureau`.

Com quantil, "score 5" significaria coisas diferentes em B e em C, e a mesma tabela de preços produziria margens diferentes sem ninguém perceber.

**Com corte absoluto**, a faixa 5 quer dizer *"PD entre 9,5% e 13%"* em qualquer base, para sempre. O preço da faixa passa a ser defensável: ele cobre aquele risco, e aquele risco é o mesmo em toda parte.

## Critérios de uma boa faixa (declarados antes de ver os números)

1. **Monotonicidade** — score maior é sempre PD menor. Inegociável: é o que o exemplo do professor mostra e o que torna a tabela defensável.
2. **Nenhuma faixa vazia ou irrelevante** na base C — mínimo de **3%** das 5.000 propostas (150), senão ela não sustenta uma decisão de preço.
3. **Faixas distinguíveis em perda esperada** — se duas faixas vizinhas têm EL praticamente igual, elas não precisavam ser duas.
4. **Mais granularidade em cima** — é onde a aprovação acontece e onde o preço precisa ser competitivo. Embaixo, tudo será negado, e granularidade ali é desperdício.
5. **Progressão aproximadamente geométrica** — risco de crédito cresce multiplicativamente, não em degraus iguais. Faixas de largura constante em PD seriam finas demais em cima e grossas demais embaixo.

## Os cortes adotados

| Score | Faixa de PD | Base C | PD média | Perda esperada |
| ----- | ----------- | ------ | -------- | -------------- |
| **10** | ≤ 2,5% | 6,7% | 1,95% | 1,34% |
| **9** | 2,5 – 3,5% | 8,6% | 3,01% | 2,07% |
| **8** | 3,5 – 5,0% | 12,5% | 4,25% | 2,92% |
| **7** | 5,0 – 7,0% | 12,2% | 5,92% | 4,07% |
| **6** | 7,0 – 9,5% | 10,4% | 8,17% | 5,77% |
| **5** | 9,5 – 13% | 9,0% | 11,08% | 7,92% |
| **4** | 13 – 18% | 9,2% | 15,33% | 11,18% |
| **3** | 18 – 25% | 10,4% | 21,49% | 15,61% |
| **2** | 25 – 35% | 10,9% | 29,42% | 21,28% |
| **1** | > 35% | 10,0% | 45,07% | 33,31% |

Todas as faixas ficam entre **6,7% e 12,5%** da base C — nenhuma vazia, nenhuma dominante. A perda esperada sobe de 1,34% a 33,31%: cada faixa é economicamente distinta da vizinha.

## 🔑 O que a distribuição revela para a política (S09)

Aprovando de cima para baixo, na base C:

| Corte | Aprovação | Volume desejado | Inadimplência esperada |
| ----- | --------- | --------------- | ---------------------- |
| score ≥ 8 | 27,9% | R$ 52,8 mi | ~3,3% |
| **score ≥ 7** | **40,1%** | **R$ 74,8 mi** | **~4,1%** |
| score ≥ 6 | 50,5% | R$ 93,3 mi | ~4,9% |
| score ≥ 5 | 59,5% | R$ 108,7 mi | ~5,9% |
| score ≥ 4 | 68,7% | R$ 123,5 mi | ~7,1% |
| score ≥ 3 | 79,2% | R$ 139,7 mi | ~9,0% ⛔ |

Três leituras que mudam o plano da política:

1. **O corte de aprovação não pode ser acima de score 7.** Score ≥ 8 dá 27,9% de aprovação e fura o guard-rail de 35% — que corta a nota pela metade.
2. **O guard-rail de inadimplência morde em score 3**, não antes. A ordenação do modelo é boa o suficiente para aprovar fundo sem estourar os 8%. **Isso contraria a hipótese que eu tinha levantado no S02** de que a inadimplência seria a restrição decisiva — ela dá mais folga do que a conta grosseira sugeria.
3. **Mas esses números são a PD do modelo**, que em mar aberto tende a **subestimar**. Some a seleção adversa (quem aceita pagar caro costuma ser quem não tem alternativa) e a inadimplência realizada será maior. A folga aparente não é folga para gastar inteira.

---

## Subetapas

### S07.1 · Critérios
Declarar o que é uma boa faixa antes de escolher os cortes.

**DoD:** ⬜ cinco critérios escritos · ⬜ a decisão quantil × absoluto justificada · ⬜ registrados nesta spec.

### S07.2 · Implementação
`banking/score.py` com `CORTES_PD` e `score_de_pd()`, vetorizada.

**DoD:** ⬜ 10 = melhor, 1 = pior · ⬜ determinística · ⬜ toda PD em [0,1] recebe faixa · ⬜ o inverso (`faixa_de_score`) devolve o intervalo, para a tabela de política.

### S07.3 · Distribuição
Conferir as três bases.

**DoD:** ⬜ nenhuma faixa abaixo de 3% da base C · ⬜ monotonicidade verificada · ⬜ tabela em `outputs/`.

### S07.4 · Perda esperada por faixa
Cruzar com as funções do S02.

**DoD:** ⬜ EL por faixa · ⬜ crescente com o risco · ⬜ faixas vizinhas distinguíveis.

### S07.5 · Testes e relatório
**DoD:** ⬜ testes verdes · ⬜ o acumulado de aprovação por corte documentado · ⬜ pipeline roda do zero.

---

## DoD do S07 (o passo inteiro)

- [ ] `score_de_pd()` determinística e monotônica
- [ ] Cortes absolutos, não quantis, com a razão registrada
- [ ] Nenhuma faixa irrelevante na base C
- [ ] Perda esperada crescente e distinguível entre vizinhas
- [ ] O acumulado de aprovação documentado — insumo direto do S09
- [ ] `pytest` verde

## O que este passo **não** faz

- **Não decide o corte de aprovação.** A tabela acima informa; quem decide é o S09, com o motor de ROI do S08.
- **Não precifica.** Faixa é o eixo da tabela de preços, não o preço.
