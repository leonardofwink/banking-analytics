# S10 · Aplicação à base C e submissão

> Passo 10 de 11 do [`ROADMAP.md`](../ROADMAP.md). Depende do S09. **→ Entregável 2 pronto (40 pts).**
>
> ✅ **CONCLUÍDO em 2026-09-22** — 5.000 linhas, 59,5% aprovadas, 167 testes verdes.

## Status das subetapas

| Subetapa | Entrega | DoD | Status | Commit |
| -------- | ------- | --- | ------ | ------ |
| S10.1 | Decisão de formato: qual PD vai no arquivo | 2/2 | ✅ | `6b0cf63` |
| S10.2 | Aplicação da política às 5.000 propostas | 3/3 | ✅ | `6b0cf63` |
| S10.3 | Validador de coerência tabela ↔ CSV | 5/5 | ✅ | `6b0cf63` |
| S10.4 | `submissao_politica.csv` gerado | 3/3 | ✅ | `6b0cf63` |
| S10.5 | Testes | 2/2 | ✅ | `6b0cf63` |

## Objetivo

`submissao_politica.csv` com 5.000 linhas e as sete colunas do modelo do professor.

## 🔑 Qual PD vai no arquivo — e por que isso não é detalhe

Há duas PDs possíveis para cada proposta, e escolher errado custa os **10 pontos de coerência**:

| | O que é | Problema |
| - | ------- | -------- |
| **PD do pedido** | escorada com o LTV e o prazo que o cliente pediu | é a que gerou o score, que gerou a decisão |
| PD da oferta | re-escorada com o LTV depois da entrada exigida | é menor, e **não bate com o score reportado** |

Exigir 10% de entrada de quem ofereceu 5% reduz o LTV, e o LTV é preditora do modelo — a PD cai. Se reportássemos essa PD menor ao lado do score que veio da PD maior, **a dupla `pd` / `score_1a10` ficaria inconsistente**, e a coerência é exatamente o que vale 10 pontos.

**Decisão: vai a PD do pedido.** O CSV é o registro de uma decisão, e a decisão foi tomada com aquela PD. Assim `score_1a10 == score_de_pd(pd)` é verdade linha a linha, auditável por qualquer um.

O efeito da entrada sobre o risco não se perde — ele está no motor de ROI e no documento de política, que é onde ele serve para argumentar.

## As três colunas de condição vêm da tabela, não do pedido

`taxa_am`, `prazo_meses` e `pct_entrada_minima` saem **direto da linha da tabela** correspondente ao score. Não são ajustadas caso a caso.

Duas razões:

1. **Coerência.** A rubrica confere se o submetido bate com a tabela de faixas. Valor por linha que varia dentro da mesma faixa levanta a pergunta "então qual é a sua política?".
2. **Consistência com a simulação.** O ROI de 11,3% foi calculado assumindo exatamente esses valores. Submeter outra coisa tornaria a projeção da defesa incompatível com a submissão.

A coluna se chama `pct_entrada_minima`: é o **requisito**, não a entrada efetiva. Quem já oferecia mais continua oferecendo mais — isso entra na economia, não no arquivo.

## O validador

Nenhum arquivo sai sem passar. Erro de formato custa os 40 pontos do bloco, e só aparece quando não dá mais para corrigir.

| Verificação | Por quê |
| ----------- | ------- |
| 5.000 linhas, ids idênticos aos da base C | o professor cruza por `id_proposta` |
| Sem duplicados | id repetido quebra o cruzamento |
| `pd` em [0,1], sem nulo | erro de unidade |
| `score_1a10` inteiro de 1 a 10 **e igual a `score_de_pd(pd)`** | a coerência que vale 10 pontos |
| `decisao` ∈ {APROVAR, NEGAR}, maiúsculas | formato do exemplo |
| `NEGAR` com taxa, prazo e entrada **vazios** | o exemplo do professor mostra assim |
| `APROVAR` com os três preenchidos | linha incompleta é proposta sem oferta |
| `taxa_am` ≤ 3,5% | guard-rail; acima disso é truncado por ele |
| Todas as linhas da mesma faixa com as mesmas condições | coerência com a tabela |
| Taxa de aprovação ≥ 35% | guard-rail |
| Sete colunas, na ordem exata | o parser do professor |

---

## Subetapas

### S10.1 · Decisão de formato
Registrar qual PD e de onde vêm as condições.

**DoD:** ✅ decisão documentada nesta spec · ✅ `score_1a10 == score_de_pd(pd)` garantido por construção.

### S10.2 · Aplicação
Escorar a base C, atribuir faixa, aplicar a tabela.

**DoD:** ✅ 5.000 linhas · ✅ aprovação de 59,5% · ✅ nenhuma proposta sem decisão.

### S10.3 · Validador
`validar_submissao_politica()` em `banking/submissao.py`.

**DoD:** ✅ as onze verificações · ✅ mensagem diz qual falhou · ✅ testado com arquivo adulterado em cada regra · ✅ recusa incoerência entre `pd` e `score` · ✅ recusa condição divergente da tabela.

### S10.4 · O arquivo
`outputs/submissao/submissao_politica.csv`.

**DoD:** ✅ validador limpo · ✅ formato idêntico ao exemplo · ✅ gerado por pipeline, sem passo manual.

### S10.5 · Testes
**DoD:** ✅ testes verdes · ✅ o arquivo real validado no teste.

---

## DoD do S10 (o passo inteiro)

- [x] `submissao_politica.csv` com 5.000 linhas e ids batendo com a base C
- [x] `score_1a10` coerente com `pd` em todas as linhas
- [x] Condições idênticas à tabela do S09, faixa a faixa
- [x] Validador passa em todas as verificações
- [x] Reprodutível
- [x] `pytest` verde
