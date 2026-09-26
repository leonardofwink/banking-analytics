# S09 · A tabela de política

> Passo 9 de 11 do [`ROADMAP.md`](../ROADMAP.md). Depende do S07 e do S08. **É o entregável.**
>
> ✅ **CONCLUÍDO em 2026-09-22** — 155 testes verdes. Aprovar score ≥ 5, taxa 1,50% + 0,1×perda, entrada 10%. ROI 11,3% central, folga de 12,7%.

## Status das subetapas

| Subetapa | Entrega | DoD | Status | Commit |
| -------- | ------- | --- | ------ | ------ |
| S09.1 | Parametrização do espaço de políticas | 3/3 | ✅ | `2832bee` |
| S09.2 | Busca com os guard-rails como restrição dura | 4/4 | ✅ | `2832bee` |
| S09.3 | Critério de robustez — escolher a que sobrevive aos três cenários | 3/3 | ✅ | `2832bee` |
| S09.4 | A tabela final, com justificativa linha a linha | 3/3 | ✅ | `2832bee` |
| S09.5 | Testes | 2/2 | ✅ | `2832bee` |

## Objetivo

Dez linhas — uma por faixa de score — dizendo **aprovar ou negar, a que taxa, em que prazo, com quanta entrada**.

## O problema, como o S08 deixou

A primeira candidata (aprovar score ≥ 7, taxas de 1,45% a 1,95%) deu **ROI de 10%** e furou o volume no cenário pessimista. As alavancas se contradizem:

| Para subir o ROI | O que isso quebra |
| ---------------- | ----------------- |
| Cobrar mais caro | Derruba o aceite → volume cai abaixo de R$ 40 mi; e sobe a PD por seleção adversa |
| Aprovar mais fundo | Sobe a inadimplência na direção dos 8% |
| Exigir mais entrada | Reduz o risco, mas corta o ticket **e** o aceite — duplo golpe no volume |
| Prazo mais longo | Mais juros por contrato, mas mais exposição |

## ⚠️ A meta de 15% não é guard-rail

Distinção que muda o que otimizar. O conselho **quer** ROI acima de 15%, mas a rubrica não cobra isso: o ROI vale **25 pontos relativos ao melhor grupo**. Os quatro guard-rails, sim, são absolutos — furar qualquer um corta a nota de política **pela metade**.

Então o problema é:

```
maximizar   ROI anualizado
sujeito a   aprovação   ≥ 35%
            taxa        ≤ 3,5% a.m.
            inadimplência ≤ 8%
            volume      ≥ R$ 40 milhões
```

E a restrição precisa valer **nos três cenários**, não só no central — porque a intensidade real do aceite é desconhecida e só submetemos uma vez.

## Como parametrizamos o espaço

Deixar as 40 células da tabela livres seria espaço grande demais para buscar e impossível de defender. Em vez disso, **seis parâmetros geram a tabela inteira** — e cada um tem significado de negócio:

| Parâmetro | O que controla | Valores testados |
| --------- | -------------- | ---------------- |
| `corte` | a partir de que score aprovamos | 7, 6, 5, 4 *(a janela viável do S07)* |
| `taxa_base` | o preço da melhor faixa | 1,50% · 1,75% · 2,00% · 2,25% · 2,50% |
| `k_risco` | quanto a taxa sobe com a perda esperada da faixa | 0 · 0,10 · 0,20 · 0,30 |
| `prazo_max` | teto de prazo (o cliente recebe o menor entre o pedido e este) | 48 · 60 |
| `entrada_base` | entrada mínima da melhor faixa | 0% · 5% · 10% |
| `entrada_passo` | quanto a exigência sobe a cada faixa pior | 0 · 4 p.p. |

A regra de preço é **`taxa = taxa_base + k_risco × perda_esperada_da_faixa`** — precificação baseada em risco, que é exatamente o que a política antiga não fazia. Com `k_risco = 0` a política vira a antiga: mesmo preço para todo mundo. Deixar esse valor na grade é deliberado — serve de contrafactual.

**960 combinações × 3 cenários.** Grade pequena o bastante para ser auditável e grande o bastante para cobrir o trade-off.

## O critério de escolha, declarado antes

1. **Descartar quem viola guard-rail em qualquer cenário.** Não é o pior caso imaginável — é o pior dos três que declaramos.
2. Entre as sobreviventes, **maximizar o ROI do cenário central**.
3. **Desempate por folga**: entre políticas com ROI a menos de 1 ponto percentual de distância, vence a que tem maior margem até o guard-rail mais apertado.

O item 3 é o que evita a armadilha de otimizar até a borda. Uma política que entrega 0,3 ponto a mais de ROI e fica a 0,2 ponto de furar o volume é pior que a alternativa: o ganho é pequeno e certo, o risco é grande e binário.

## Monotonicidade é restrição, não resultado

A tabela precisa ser monotônica — score melhor nunca recebe condição pior. A parametrização garante isso por construção: a taxa cresce com a perda esperada, a entrada cresce conforme o score piora, e o prazo é o mesmo teto para todos.

Não é preciosismo estético: é o que torna a tabela defensável diante do conselho. Qualquer inversão exigiria explicar por que um cliente melhor paga mais.

---

## 🔄 Duas revisões durante a execução

Ambas ficam registradas porque mudar critério depois de ver resultado é exatamente o que este projeto evita — quando foi necessário, tem de estar explícito.

### 1. As elasticidades de aceite foram recalibradas

A primeira busca **degenerou**: 896 das 960 políticas morriam por volume, e a vencedora usava **preço único para todo risco**. Um resultado que reproduz a patologia diagnosticada pelo conselho é sintoma de premissa errada, não de política certa.

A âncora que corrigiu: **o teto de 3,5% a.m. só é guard-rail se as políticas quiserem chegar perto dele.** Se o aceite morresse a 2%, o teto seria decorativo. As elasticidades foram recalibradas (β_taxa de 0,8 / 1,5 / 2,5) para que cobrar no teto deixe aceite baixo mas não nulo. Registrado em [`DEBITO_TECNICO.md`](../DEBITO_TECNICO.md#4--as-elasticidades-da-base-c-são-premissa-não-medida).

### 2. O critério de desempate era largo demais — e a escolha foi para o humano

O critério declarado tratava como empate uma diferença de **1 ponto percentual** de ROI. Sobre uma base de ~11%, isso é 9% relativo: não é empate. Com essa janela, o desempate por folga descartou a melhor política e voltou a escolher **preço único**.

Em vez de estreitar a janela depois de ver o resultado — o que seria ajustar a régua ao alvo —, a decisão entre as quase-empatadas foi levada ao **responsável pela frente de política**, com as três candidatas e seus trade-offs explícitos. É uma decisão de **apetite a risco**, não técnica.

A escolhida está registrada em `banking/politica.POLITICA_ESCOLHIDA`, com a justificativa.

---

## Subetapas

### S09.1 · Parametrização
`gerar_politica(corte, taxa_base, k_risco, prazo_max, entrada_base, entrada_passo)`.

**DoD:** ✅ devolve as 10 linhas · ✅ monotônica por construção · ✅ taxa truncada no teto de 3,5%.

### S09.2 · Busca
Varrer a grade, simular nos três cenários, registrar tudo.

**DoD:** ✅ 960 combinações avaliadas · ✅ re-escoragem em cache (a PD não depende da taxa) · ✅ resultado completo em `outputs/` · ✅ determinística.

### S09.3 · Escolha
Aplicar o critério de três passos.

**DoD:** ✅ sobreviventes identificadas · ✅ critério aplicado na ordem declarada · ✅ a escolhida e as vice-campeãs registradas.

### S09.4 · A tabela final
Com a justificativa de cada linha — o insumo direto da defesa.

**DoD:** ✅ 10 linhas completas · ✅ cada uma com uma frase de razão · ✅ gravada em `outputs/`.

### S09.5 · Testes
**DoD:** ✅ monotonicidade travada em teste · ✅ a política escolhida passa nos guard-rails dos três cenários.

---

## DoD do S09 (o passo inteiro)

- [x] Tabela de 10 linhas, monotônica nas quatro alavancas
- [x] Guard-rails respeitados nos **três** cenários
- [x] Escolha pelo critério declarado antes da busca
- [x] Folga até o guard-rail mais apertado registrada
- [x] Cada linha com justificativa
- [x] `pytest` verde

## O que este passo **não** faz

- **Não gera o CSV.** Isso é o S10, com o validador.
- **Não promete o ROI oficial.** As elasticidades são premissa nossa; o valor é a comparação entre políticas sob a mesma régua.
