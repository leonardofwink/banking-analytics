# S06 · Escoragem e submissão do modelo

> Passo 6 de 11 do [`ROADMAP.md`](../ROADMAP.md). Depende do S05. **→ Entregável 1 pronto (40 pts).**
>
> ✅ **CONCLUÍDO em 2026-09-22** — 3.000 PDs escoradas, PD média 0,0788, validador limpo.

## Status das subetapas

| Subetapa | Entrega | DoD | Status | Commit |
| -------- | ------- | --- | ------ | ------ |
| S06.1 | Configuração vencedora registrada **em código** | 3/3 | ✅ | `186c315` |
| S06.2 | Retreino na base A inteira | 3/3 | ✅ | `186c315` |
| S06.3 | Escoragem da base B | 3/3 | ✅ | `186c315` |
| S06.4 | `banking/submissao.py` — validador do arquivo | 4/4 | ✅ | `186c315` |
| S06.5 | `submissao_modelo.csv` gerado | 3/3 | ✅ | `186c315` |
| S06.6 | Testes | 2/2 | ✅ | `186c315` |

## Objetivo

`submissao_modelo.csv` com 3.000 linhas, `id_contrato` e `pd` — o arquivo que o professor cruza com o gabarito dele para calcular o AuROC.

## Por que retreinar na base A inteira

A validação 2024 cumpriu seu papel: **escolher** entre logística, Random Forest e XGBoost, e escolher os hiperparâmetros. Decidido isso, ela não tem mais função de juiz — e deixar 3.330 contratos (239 defaults) de fora seria desperdiçar um terço da amostra.

Retreinar com tudo é **mesma receita, mais ingredientes**. O que não pode acontecer é o contrário: escolher olhando 2025, que não temos.

```
escolha do modelo  ──►  treino 2022–2023, medido em 2024   (S04, S05)
modelo final       ──►  treino 2022–2024 inteiro           (S06)
escoragem          ──►  base B, jan–jun/2025               (S06)
```

⚠️ **Efeito colateral a declarar:** o modelo final **não tem conjunto de teste**. O AuROC de 0,7234 veio do modelo treinado só até 2023. O modelo que vai na submissão viu mais dado e provavelmente é um pouco melhor, mas isso **não é medível por nós** — só o professor pode. Qualquer número que reportarmos sobre o modelo final seria treino, e treino não vale como estimativa.

## A configuração vencedora mora em código, não em `outputs/`

Os hiperparâmetros escolhidos pela busca do S05 são uma **decisão do projeto**, não um artefato gerado. Por isso ficam em `banking/modelo.py`, versionados, e não num arquivo de `outputs/` que não entra no git.

O script do S05 passa a **avisar** se uma nova busca encontrar configuração diferente da registrada — assim a divergência aparece em vez de passar despercebida.

## O validador é obrigatório

Erro de formato no CSV custa os 30 pontos inteiros, e é o tipo de erro que só aparece quando já não dá para corrigir. O validador confere, antes de o arquivo existir:

| Verificação | Por quê |
| ----------- | ------- |
| Exatamente 3.000 linhas | Uma linha a menos e o cruzamento fica incompleto |
| Ids idênticos aos da base B, sem faltar nem sobrar | O professor cruza por `id_contrato` |
| Sem duplicados | Id repetido quebra o merge |
| `pd` entre 0 e 1, sem nulo | Probabilidade fora da faixa denuncia erro de unidade |
| Sem massa em 0 ou 1 | Distribuição degenerada indica modelo colapsado — foi exatamente o sintoma da armadilha do S01 |
| Duas colunas, nos nomes exatos do exemplo | O parser do professor espera esse cabeçalho |

O mesmo módulo servirá o `submissao_politica.csv` no S10, com as regras próprias daquele arquivo.

---

## Subetapas

### S06.1 · Configuração vencedora em código
`MODELO_ESCOLHIDO` e `HIPERPARAMETROS_ESCOLHIDOS` em `banking/modelo.py`, com a procedência documentada.

**DoD:** ✅ constantes importáveis · ✅ docstring cita a busca do S05 · ✅ S05 avisa se divergir.

### S06.2 · Retreino
`treinar_modelo_final(base_a)` — ajusta na base A inteira com `SEMENTE` fixa.

**DoD:** ✅ treina nos 10.000 · ✅ duas execuções produzem PDs idênticas · ✅ mesmo pipeline do S05.

### S06.3 · Escoragem da base B
**DoD:** ✅ 3.000 PDs · ✅ nenhum nulo · ✅ PD média coerente com a prevalência da base A (~8,3%).

### S06.4 · Validador
`banking/submissao.py` com `validar_submissao_modelo()`.

**DoD:** ✅ as seis verificações acima · ✅ mensagem diz qual falhou · ✅ testado com arquivo adulterado · ✅ reaproveitável no S10.

### S06.5 · Geração do arquivo
`outputs/submissao/submissao_modelo.csv`.

**DoD:** ✅ validador passa · ✅ formato idêntico ao exemplo do professor · ✅ gerado por pipeline, sem passo manual.

### S06.6 · Testes
**DoD:** ✅ testes verdes · ✅ o validador falha de verdade quando adulterado.

---

## DoD do S06 (o passo inteiro)

- [x] `submissao_modelo.csv` com 3.000 linhas e ids batendo com a base B
- [x] Modelo retreinado na base A inteira
- [x] Validador passa em todas as verificações
- [x] Reprodutível: duas execuções, arquivo idêntico
- [x] `pytest` verde

## O que este passo **não** faz

- **Não mede o modelo final.** Sem conjunto de teste, qualquer número seria treino.
- **Não aplica política.** Nenhuma decisão de crédito encosta na base B.
