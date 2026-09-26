# S05 · Desafiantes — Random Forest e XGBoost

> Passo 5 de 11 do [`ROADMAP.md`](../ROADMAP.md). Depende do S04. **Encerra a escolha do modelo.**
>
> ✅ **CONCLUÍDO em 2026-09-22** — XGBoost escolhido: AuROC 0,7234 · KS 0,3660 na validação 2024 (+0,0745 sobre a logística).

## Status das subetapas

| Subetapa | Entrega | DoD | Status | Commit |
| -------- | ------- | --- | ------ | ------ |
| S05.1 | Busca de hiperparâmetros com CV temporal **dentro do treino** | 3/3 | ✅ | `69851b0` |
| S05.2 | Random Forest no mesmo pipeline | 3/3 | ✅ | `69851b0` |
| S05.3 | XGBoost no mesmo pipeline | 3/3 | ✅ | `69851b0` |
| S05.4 | Comparação final na validação — **medida uma vez só** | 3/3 | ✅ | `69851b0` |
| S05.5 | Escolha pela regra declarada antes | 2/2 | ✅ | `69851b0` |
| S05.6 | Testes | 2/2 | ✅ | `69851b0` |

## Objetivo

Descobrir **quanto** os modelos de árvore ganham da logística (AuROC 0,6489) e decidir qual vai para a submissão.

## O plano

```
              treino 2022–2023 (6.670)                    validação 2024 (3.330)
                       │                                            │
     ┌─────────────────┴─────────────────┐                          │
     │  CV temporal em 3 dobras          │                          │
     │  ajusta os hiperparâmetros AQUI   │                          │
     └─────────────────┬─────────────────┘                          │
                       │                                            │
              melhor configuração  ──── treina no treino inteiro ───►  medida UMA VEZ
```

**Três regras, todas declaradas antes de qualquer número aparecer:**

### 1. A validação não participa da busca

Os hiperparâmetros são escolhidos por **validação cruzada temporal dentro do treino**, nunca olhando 2024. O motivo é o mesmo do split: se testarmos 12 configurações na validação e ficarmos com a melhor, o número que sobra não é performance — é o máximo de 12 sorteios. E esse máximo não se repete na base B, que é onde a nota acontece.

A validação 2024 é tocada **uma única vez**, no fim, com a configuração já escolhida.

### 2. Mesmo pipeline, mesmo split, mesma semente

Só o estimador final muda. Se o pré-processamento ou a partição variassem junto, não saberíamos a que atribuir a diferença — e a comparação perderia o sentido.

### 3. Regra de desempate (a mesma do S04)

**Diferença de AuROC menor que 0,01 → vence o modelo mais simples.**

Não é preferência estética. Três razões concretas:

- A validação tem **239 defaults**. Com essa amostra, o intervalo de confiança do AuROC é largo o bastante para que diferenças pequenas sejam ruído — está no [débito técnico](../DEBITO_TECNICO.md#7--sem-validação-cruzada--só-um-holdout-temporal), item 7.
- O AuROC vale **30 pontos relativos** ao melhor grupo; a defesa vale **20 absolutos**. Um modelo explicável coeficiente a coeficiente rende mais na segunda conta.
- Árvores produzem probabilidade **pior calibrada** que a logística, e a política precisa de **nível**, não só de ordenação.

## O que cada modelo pode trazer

| Modelo | Por que pode ganhar | O que custa |
| ------ | ------------------- | ----------- |
| **Random Forest** | Captura interação e não-linearidade sem tuning pesado. Robusto a outlier | Probabilidade mal calibrada; explicação só via importância |
| **XGBoost** | Normalmente o melhor AuROC bruto em dado tabular | Sobreajusta fácil com 587 defaults no treino; exige regularização e explicação via SHAP |

**Risco real desta etapa:** o treino tem 6.670 linhas e **587 defaults**. É pouco para modelo complexo. Por isso a busca privilegia configurações **rasas e regularizadas** — árvores profundas decoram o treino e a folga treino-validação denuncia.

## A grade de busca

Pequena de propósito: cada configuração testada é uma chance a mais de achar um resultado bom por acaso.

**Random Forest** — profundidade 4/6/8 · mínimo de 20/50 por folha · com e sem `class_weight="balanced"`.

**XGBoost** — profundidade 3/4/5 · taxa de aprendizado 0,05/0,1 · `min_child_weight` 5/20 · subamostragem 0,8.

O desbalanceamento (8,8% de default) entra como opção na grade em vez de premissa: para **ordenação**, reponderar nem sempre ajuda, e deixar a CV decidir é mais honesto que assumir.

---

## Subetapas

### S05.1 · Busca com CV temporal
`TimeSeriesSplit` de 3 dobras sobre o treino ordenado por data, otimizando AuROC.

**DoD:** ✅ as dobras respeitam a ordem temporal · ✅ a validação 2024 não é tocada na busca · ✅ melhor configuração registrada.

### S05.2 · Random Forest
**DoD:** ✅ mesmo `ColumnTransformer` da logística · ✅ AuROC na CV e na validação · ✅ folga treino-validação reportada.

### S05.3 · XGBoost
**DoD:** ✅ mesmo pipeline · ✅ AuROC na CV e na validação · ✅ folga reportada.

### S05.4 · Comparação
Tabela com os três, mesma validação, mesmas métricas.

**DoD:** ✅ AuROC, KS, Gini, Brier e erro de calibração dos três · ✅ validação medida uma vez · ✅ tabela em `outputs/`.

### S05.5 · Escolha
**DoD:** ✅ regra aplicada e registrada · ✅ modelo escolhido salvo para o S06.

### S05.6 · Testes
**DoD:** ✅ testes verdes · ✅ um teste garante que os três usam o mesmo pré-processamento.

---

## DoD do S05 (o passo inteiro)

- [x] Os três modelos comparados na mesma validação
- [x] Hiperparâmetros escolhidos **sem** tocar a validação
- [x] Escolha pela regra declarada antes
- [x] Sobreajuste verificado em cada um
- [x] `pytest` verde
