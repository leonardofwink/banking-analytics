# S02 · Perda esperada (EAD e LGD)

> Passo 2 de 11 do [`ROADMAP.md`](../ROADMAP.md). Depende do S01. **Libera a frente de política.**
>
> ✅ **CONCLUÍDO em 2026-09-22** — commit `8a9e6dc`, 49 testes verdes.

## Status das subetapas

| Subetapa | Entrega | DoD | Status | Commit |
| -------- | ------- | --- | ------ | ------ |
| S02.1 | `carregar_parametros_ead_lgd()` em `banking/dados.py` | 3/3 | ✅ | `8a9e6dc` |
| S02.2 | `faixa_ltv()` · `faixa_idade_veiculo()` | 3/3 | ✅ | `8a9e6dc` |
| S02.3 | `fator_ead()` · `ead()` | 3/3 | ✅ | `8a9e6dc` |
| S02.4 | `lgd()` com os dois modos de avalista | 4/4 | ✅ | `8a9e6dc` |
| S02.5 | `perda_esperada()` | 3/3 | ✅ | `8a9e6dc` |
| S02.6 | Validação contra o gabarito da base A | 4/4 | ✅ | `8a9e6dc` |
| S02.7 | Testes + pipeline | 3/3 | ✅ | `8a9e6dc` |

## Objetivo

Transformar as duas tabelas do professor em funções, e **provar que as interpretamos certo** comparando com os 826 contratos da base A que realmente deram default.

```
Perda esperada = PD × EAD × LGD
                      │     └── tabela por idade do veículo × faixa de LTV (+ ajuste de avalista)
                      └──────── fator por prazo × faixa de LTV, multiplicado pelo valor financiado
```

## Por que este passo existe

É o elo que transforma **probabilidade em dinheiro**. Sem ele, a PD é um número abstrato: não dá para decidir taxa, não dá para calcular ROI, não dá para dizer se uma faixa de score se paga.

E há um motivo que vale ainda mais: **temos gabarito**. A base A traz `ead_realizado` e `lgd_realizado` dos 826 inadimplentes. Dá para conferir se entendemos as tabelas **antes** de construir a política inteira em cima delas. Isso é raro — normalmente se descobre o erro de interpretação depois, quando já custou caro.

## ⚠️ As tabelas são médias por célula, não valores por contrato

Descoberta da validação, e ela muda o que "bater com o gabarito" significa.

Comparar a tabela **linha a linha** contra o realizado dá erro médio de 0,098 na LGD — o que pareceria erro de interpretação. Não é. As tabelas são a **média dos inadimplentes de cada célula**, e o professor diz isso: *"valores observados nos contratos inadimplentes da Base A"*. Dentro de uma célula, a LGD real varia bastante (desvio-padrão mediano de **0,099**, máximo de 0,27).

Comparando **média contra média**, o encaixe é quase perfeito:

| Tabela | Erro médio por célula | Erro máximo |
| ------ | --------------------- | ----------- |
| **LGD** | **0,0003** | 0,0007 |
| **Fator de EAD** | **0,00051** | 0,00338 |

**Conclusão:** interpretamos as faixas corretamente, e as tabelas reproduzem o comportamento médio. **Consequência para a política:** ao aplicar a tabela a um contrato individual, estamos usando a média da célula — que é o certo para calcular perda **esperada**, mas esconde dispersão real. Duas carteiras com a mesma perda esperada podem ter caudas bem diferentes.

**Convenção de faixa adotada:** intervalos fechados à direita — `até 60%` é `ltv ≤ 0,60`, `60% a 70%` é `0,60 < ltv ≤ 0,70`, e assim por diante. Testamos as duas convenções contra o gabarito e o resultado é indistinguível (não há contratos exatamente na borda), então a escolha é por clareza.

## 🚩 O ajuste de avalista tem viés conhecido

O professor manda **somar −0,061 à LGD da tabela quando há avalista**. Mas a tabela já é a média de **todos** os inadimplentes da célula — com e sem avalista (19,7% dos 826 têm avalista). Aplicar o desconto por cima conta o benefício duas vezes.

Medido contra o gabarito:

| Regra | Viés médio | Leitura |
| ----- | ---------- | ------- |
| **Oficial** (`−0,061` só para avalista) | **−0,0121** | **subestima** a perda em 1,2 p.p. |
| **Centrada** (`−0,061×(1−s)` / `+0,061×s`) | **−0,0001** | praticamente sem viés |

O efeito real do avalista na base A é de **0,079** (resíduo médio de −0,0633 com avalista contra +0,0157 sem), e não 0,061 — mais um sinal de que o parâmetro declarado não foi calculado sobre a mesma referência.

**Decisão:** `modo="oficial"` é o **padrão**, porque é o parâmetro declarado e a coerência com o enunciado vale 10 pontos. `modo="centrado"` fica implementado e o viés é compensado explicitamente na margem de segurança da precificação (S09). Registrado em [`DEBITO_TECNICO.md`](../DEBITO_TECNICO.md#5--o-ajuste-de-avalista-da-lgd-tem-viés-conhecido-e-vamos-usar-assim-mesmo).

---

## Subetapas

### S02.1 · Leitura dos parâmetros
`carregar_parametros_ead_lgd()` em `banking/dados.py` (o módulo que concentra IO), devolvendo as três abas: fator de EAD, LGD e distribuição do mês do default.

**DoD:** ✅ as três abas carregam · ✅ 4 prazos × 5 faixas no EAD e 4 idades × 5 faixas na LGD · ✅ a distribuição do mês soma 1,0.

### S02.2 · Faixas
`faixa_ltv()` e `faixa_idade_veiculo()`, vetorizadas.

**DoD:** ✅ fechadas à direita · ✅ classificam todos os contratos das três bases sem sobrar `NaN` · ✅ rótulos idênticos aos do Excel.

### S02.3 · Fator de EAD e EAD em reais
`fator_ead(prazo, ltv)` e `ead(valor_financiado, prazo, ltv)`.

**DoD:** ✅ fator entre 0,98 e 1,05 · ✅ média por célula bate com a tabela (erro < 0,005) · ✅ EAD em reais, não fração.

### S02.4 · LGD
`lgd(idade_veiculo_anos, ltv, possui_avalista, modo)`.

**DoD:** ✅ resultado sempre em [0, 1] · ✅ média por célula bate (erro < 0,001) · ✅ os dois modos implementados · ✅ o padrão é `"oficial"`.

### S02.5 · Perda esperada
`perda_esperada(pd, valor_financiado, prazo, ltv, idade_veiculo_anos, possui_avalista)`.

**DoD:** ✅ resultado em **reais** · ✅ PD em fração rejeita valor > 1 · ✅ reproduz a tabela ilustrativa do professor (score 6: PD 8,5% × 1,03 × 69% ≈ 6,0%).

### S02.6 · Validação contra o gabarito
Script que compara célula a célula o calculado contra o realizado dos 826 inadimplentes.

**DoD:** ✅ LGD com erro médio < 0,001 · ✅ EAD com erro médio < 0,005 · ✅ relatório gravado em `outputs/` · ✅ o viés do avalista quantificado.

### S02.7 · Testes e pipeline
`tests/python/test_perda.py` e `python/etl/02_parametros_ead_lgd.py`.

**DoD:** ✅ testes verdes · ✅ pipeline roda do zero · ✅ unidades documentadas em cada função.

---

## DoD do S02 (o passo inteiro)

- [x] As duas tabelas viraram funções vetorizadas
- [x] Validadas contra o gabarito: LGD 0,0003 · EAD 0,00051 de erro médio por célula
- [x] Convenção de faixa decidida e testada
- [x] Viés do avalista medido, documentado e com os dois modos disponíveis
- [x] `pytest` verde
- [x] Relatório de validação em `outputs/`

## O que este passo **não** faz

- **Não modela** EAD nem LGD. São parâmetros dados; nós modelamos só a PD.
- **Não decide preço.** Perda esperada é insumo da precificação (S09), não a precificação.
- **Não usa** `ead_realizado`/`lgd_realizado` como preditoras — elas só validam.
