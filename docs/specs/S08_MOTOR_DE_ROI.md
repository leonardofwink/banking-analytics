# S08 · Motor de simulação do ROI

> Passo 8 de 11 do [`ROADMAP.md`](../ROADMAP.md). Depende do S02. **O passo mais trabalhoso da frente de política.**
>
> ✅ **CONCLUÍDO em 2026-09-22** — 141 testes verdes. Price validada contra a base A (erro 0,0003%).

## Status das subetapas

| Subetapa | Entrega | DoD | Status | Commit |
| -------- | ------- | --- | ------ | ------ |
| S08.1 | Tabela Price — parcela, saldo e juros pagos até o mês *m* | 4/4 | ✅ | `c5b6ade` |
| S08.2 | `aplicar_politica()` — da proposta à oferta | 4/4 | ✅ | `c5b6ade` |
| S08.3 | Aceite e seleção adversa como **cenários** | 3/3 | ✅ | `c5b6ade` |
| S08.4 | `simular()` — ROI, inadimplência, volume, aprovação | 4/4 | ✅ | `c5b6ade` |
| S08.5 | Testes contra casos de resposta conhecida | 3/3 | ✅ | `c5b6ade` |

## Objetivo

Uma função que recebe **uma política** e **um cenário** e devolve os quatro números que o conselho vai olhar:

```
simular(ofertas, cenario)  →  ROI anualizado · inadimplência · volume originado · taxa de aprovação
```

## Por que este passo existe

**Ele substitui o simulador que o professor não deu.** O enunciado é explícito:

> *"A direção de cada efeito está declarada. A intensidade, não — e não há como descobri-la por tentativa e erro, porque vocês só submetem uma vez. O caminho é raciocinar sobre o trade-off, não otimizá-lo às cegas."*

Sem motor, escolher entre aprovar score ≥ 7 e score ≥ 4 é chute. Com motor, é comparação — sob premissas declaradas.

## A fórmula oficial, peça por peça

```
ROI anual = [ (juros recebidos − perda realizada) ÷ volume financiado ] ÷ prazo médio em anos
```

| Peça | Como calculamos |
| ---- | --------------- |
| **Parcela** | Tabela Price: `P × i / (1 − (1+i)^−n)`. **Verificado**: reproduz a `parcela_mensal` da base A com erro relativo médio de 0,0003% |
| **Juros de quem paga até o fim** | `parcela × n − P` |
| **Juros de quem quebra no mês m** | `parcela × m − (P − saldo_m)`, com `saldo_m = P × [(1+i)^n − (1+i)^m] / [(1+i)^n − 1]`. Só a parte de **juros** das parcelas pagas — a amortização não é receita |
| **Quando ele quebra** | Média sobre a [distribuição do mês do default](../DICIONARIO_DADOS.md#parâmetros-de-ead-e-lgd-dados-não-modelados) (média 6,9, pico entre o 5º e o 8º mês) |
| **Perda realizada** | `fator_ead(prazo, LTV) × financiado × lgd(idade, LTV, avalista)` — as funções do S02 |
| **Volume financiado** | Soma do financiado dos contratos **efetivados**, não aprovados |
| **Prazo médio em anos** | Média ponderada dos prazos ofertados ÷ 12 |

**Simplificação declarada:** contratos que sobrevivem aos 12 meses da janela de performance são tratados como pagos até o fim. O alvo é PD 90/12, então não temos informação sobre default posterior — assumir o contrário exigiria inventar dado.

## 🔑 A referência de mercado sai do dado, não de chute

A base A traz `taxa_juros_am` — o que a política antiga cobrou. É a melhor proxy disponível do preço que o cliente encontra no concorrente:

**Taxa média: 1,59% a.m.** (p05 1,38% · p95 1,80%)

E, mais importante, o que ela revela:

| Score | Default real | Taxa cobrada |
| ----- | ------------ | ------------ |
| 10 | 0,2% | 1,57% |
| 7 | 4,8% | 1,59% |
| 4 | 18,1% | 1,61% |
| 1 | **69,6%** | **1,64%** |

**Sete pontos-base separando um risco que vai de 0,2% a 69,6%.** Correlação taxa × PD de apenas **+0,125**.

Isto é o diagnóstico do conselho em números: a política antiga **cobrava quase o mesmo de todo mundo**. O bom cliente subsidiava o ruim — e, cobrado acima do que valia, ia para o concorrente. É o mecanismo clássico de espiral de seleção adversa.

**Consequência para a nossa precificação:** o teto de 3,5% a.m. **não é a restrição que morde**. Ele está 2,2× acima do mercado praticado. Quem limita o preço é o **aceite do cliente**, não o CET regulatório. Uma política que cobra 3% de alguém num mercado de 1,6% não vai ter esse cliente.

## Aceite e seleção adversa: o que assumimos

A intensidade não é revelada, então ela entra como **premissa declarada**, em três cenários. A forma funcional é decaimento exponencial sobre o excesso em relação à referência:

```
p_aceite = a₀ · exp(−β_taxa · excesso_taxa) · exp(−β_entrada · entrada_extra) · exp(−β_prazo · encurtamento)

pd_efetiva = pd_modelo · (1 + γ · excesso_taxa)
```

onde `excesso_taxa = taxa_ofertada / 1,59% − 1`, `entrada_extra` é o quanto exigimos acima da entrada que o cliente pediu, e `encurtamento` é a redução relativa do prazo pedido.

| Parâmetro | Otimista | **Central** | Pessimista |
| --------- | -------- | ----------- | ---------- |
| `a₀` — aceite na condição de referência | 0,95 | **0,85** | 0,70 |
| `β_taxa` | 1,5 | **3,0** | 5,0 |
| `β_entrada` | 1,5 | **3,0** | 5,0 |
| `β_prazo` | 0,5 | **1,0** | 2,0 |
| `γ` — seleção adversa | 0,2 | **0,5** | 1,0 |

Para calibrar a intuição, no cenário central: cobrar **2,0% a.m.** (26% acima do mercado) derruba o aceite para **46%** do nível de referência e sobe a PD em **13%**. Cobrar **3,0%** derruba para **7%** e sobe a PD em **45%**.

**O efeito da entrada sobre a PD não é premissa — é medido.** Exigir mais entrada reduz o LTV, e o LTV é preditora do nosso modelo. Então **re-escoramos** com o LTV ofertado, em vez de assumir uma elasticidade. É a segunda passagem prevista lá no S01.

## Expectativa, não sorteio

O aceite entra como **probabilidade ponderando cada proposta**, não como sorteio. Uma carteira simulada por Monte Carlo teria ruído próprio, e comparar duas políticas exigiria distinguir diferença real de variação amostral. Com valor esperado, duas políticas idênticas dão exatamente o mesmo número — que é também o que o enunciado promete do simulador oficial (*"os sorteios de cada proposta são fixos"*).

---

## Subetapas

### S08.1 · Tabela Price
`parcela()`, `saldo_devedor()` e `juros_pagos_ate()`.

**DoD:** ✅ a parcela reproduz a base A com erro < 0,01% · ✅ saldo no último mês é zero · ✅ juros até o fim = `parcela×n − P` · ✅ taxa zero não divide por zero.

### S08.2 · Da proposta à oferta
`aplicar_politica(propostas, politica, escorar)`.

**DoD:** ✅ entrada efetiva = máximo entre desejada e exigida · ✅ LTV e financiado recalculados · ✅ PD re-escorada com o LTV ofertado · ✅ negados saem com campos vazios.

### S08.3 · Cenários
`CENARIOS` com os três conjuntos de parâmetros.

**DoD:** ✅ os três implementados · ✅ aceite em [0,1] · ✅ PD efetiva ≥ PD do modelo.

### S08.4 · Simulação
`simular(ofertas, cenario)`.

**DoD:** ✅ reproduz a fórmula oficial · ✅ devolve os quatro indicadores · ✅ diz quais guard-rails foram violados · ✅ determinística.

### S08.5 · Testes
**DoD:** ✅ casos de resposta conhecida · ✅ carteira sem default → ROI = juros ÷ volume ÷ anos · ✅ testes verdes.

---

## DoD do S08 (o passo inteiro)

- [x] Tabela Price validada contra a base A
- [x] ROI reproduzindo a fórmula oficial, peça por peça
- [x] Aceite e seleção adversa como cenários declarados, não números escondidos
- [x] Efeito da entrada sobre a PD **medido** pelo modelo, não assumido
- [x] Determinístico
- [x] `pytest` verde

## O que este passo **não** faz

- **Não escolhe a política.** Ele mede candidatas; quem escolhe é o S09.
- **Não prevê o resultado oficial.** As elasticidades são nossas premissas. O valor está em **comparar** políticas sob a mesma premissa, não em acertar o número do professor.
