# S03 · Exploratória e split temporal

> Passo 3 de 11 do [`ROADMAP.md`](../ROADMAP.md). Depende do S01. **Abre o bloco do modelo.**
>
> ✅ **CONCLUÍDO em 2026-09-22** — 72 testes verdes. Achado principal: as duas variáveis mais preditivas (`score_bureau`, `qtd_restricoes_ativas`) são as mais instáveis na base C (PSI 0,50 e 5,93).

## Status das subetapas

| Subetapa | Entrega | DoD | Status | Commit |
| -------- | ------- | --- | ------ | ------ |
| S03.1 | `banking/split.py` — `dividir_temporal()` | 4/4 | ✅ | `e308913` |
| S03.2 | `banking/metricas.py` — `ks()`, `iv()`, `psi()` | 4/4 | ✅ | `e308913` |
| S03.3 | EDA: missing, safras, default por faixa | 3/3 | ✅ | `e308913` |
| S03.4 | IV univariado (só no treino) | 3/3 | ✅ | `e308913` |
| S03.5 | PSI de A/B contra C — medir a extrapolação | 3/3 | ✅ | `e308913` |
| S03.6 | Testes + pipeline + relatório | 3/3 | ✅ | `e308913` |

## Objetivo

Conhecer o dado e **fixar o split antes de ver qualquer resultado de modelo**.

## Por que este passo existe

Duas razões, e a segunda é a que economiza nota.

**A óbvia:** não se modela o que não se conhece. Precisamos saber onde estão os nulos, quais variáveis separam bom de mau e se alguma tem comportamento estranho.

**A que importa:** o split tem que ser **decidido antes**, e por um motivo que não é burocrático. Quem experimenta vários splits e fica com o que deu o melhor AuROC não escolheu o melhor modelo — escolheu o split mais sortudo. E sorte não se repete na base B, que é onde a nota acontece. Fixar antes é o que torna o número da validação uma **estimativa honesta** do que vai acontecer, em vez de um recorde pessoal.

O mesmo vale para o IV: ele é calculado **só no treino**. Calcular no conjunto inteiro é espiar a validação — a variável que parece boa passa a parecer boa porque viu a resposta.

## O split

```
Base A (10.000, 2022–2024)
├── treino      2022–2023   6.670 contratos   default 8,80%
└── validação   2024        3.330 contratos   default 7,18%
                                 ↓
Base B (jan–jun/2025, 3.000) ──► o professor mede o AuROC aqui
```

**Por que temporal e não aleatório:** o enunciado é explícito — *"crédito tem ordem temporal. Split aleatório é otimista por construção; o teste honesto é o período seguinte."* Embaralhar os anos deixa o modelo aprender com contratos de 2024 para prever contratos de 2022, o que nunca acontece na vida real. A avaliação é out-of-time (2025 contra 2022–2024), então a validação precisa imitar isso.

**Por que a prevalência muda e tudo bem:** o treino tem 8,80% de default e a validação 7,18%. A diferença é real. Por isso a comparação de modelos usa **AuROC e KS**, que medem ordenação e não dependem da prevalência — e não acurácia, que dependeria.

---

## Subetapas

### S03.1 · Split temporal
`banking/split.py` com `dividir_temporal(df)`, devolvendo treino e validação por ano de originação.

**DoD:** ✅ 6.670 / 3.330 contratos · ✅ nenhum contrato nos dois lados · ✅ nenhuma data de treino posterior a data de validação · ✅ determinístico (duas chamadas, mesma partição).

### S03.2 · Métricas
`banking/metricas.py` com `ks()`, `iv()` e `psi()` — usadas aqui e em todo o bloco do modelo (S04, S05, S06).

**DoD:** ✅ KS entre 0 e 1 · ✅ `iv()` devolve também a tabela de WOE por faixa · ✅ `psi()` com as faixas definidas na referência · ✅ testadas contra casos de resposta conhecida.

### S03.3 · Exploratória
Nulos por variável, default por safra, taxa de default por faixa das principais variáveis.

**DoD:** ✅ mapa de nulos · ✅ default por safra mensal · ✅ relatório em `outputs/tabelas/`.

### S03.4 · IV univariado
Poder preditivo de cada variável isolada, **calculado só no treino**.

**DoD:** ✅ IV de todas as preditoras · ✅ ordenadas · ✅ **nenhuma com IV > 0,5 sem justificativa** — acima disso é suspeita de vazamento até prova em contrário.

### S03.5 · PSI — quanto o modelo vai extrapolar
Estabilidade de cada variável entre a base A (treino) e as bases B e C.

**DoD:** ✅ PSI por variável para A→B e A→C · ✅ referência aplicada (< 0,1 estável · 0,1–0,25 atenção · > 0,25 instável) · ✅ as variáveis instáveis em C identificadas por nome.

Este é o passo que **dimensiona o risco nº 1 do projeto**: sabemos que a base C é mar aberto, mas o PSI diz *em quais variáveis* e *quanto*.

### S03.6 · Testes, pipeline e relatório
`tests/python/test_split.py`, `tests/python/test_metricas.py`, `python/modelagem/03_eda.py`.

**DoD:** ✅ testes verdes · ✅ pipeline roda do zero · ✅ relatório legível em `outputs/`.

---

## DoD do S03 (o passo inteiro)

- [x] Split em código, determinístico, com as contagens conferidas
- [x] IV calculado **só no treino**, com as variáveis ordenadas por poder
- [x] Nenhuma variável com IV suspeito sem explicação
- [x] PSI de A→C medido e as variáveis instáveis nomeadas
- [x] `pytest` verde
- [x] Relatório em `outputs/tabelas/`

## O que este passo **não** faz

- **Não treina modelo.** Isso é o S04.
- **Não seleciona variável.** O IV informa; a seleção acontece dentro do `Pipeline`, com base no treino.
- **Não imputa nada.** Continua valendo: transformação que aprende fica no `Pipeline`.
