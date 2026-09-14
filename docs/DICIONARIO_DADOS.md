# Dicionário de dados — AutoCred

> Fonte: `AutoCred_Dicionario_de_Dados.xlsx` + inspeção das três bases (2026-09-13).
> Arquivos do professor em `dados/brutos/professor/` — **fora do git**, como todo dado.

## As três bases

| Base | Arquivo | Linhas × colunas | Período | Alvo |
| ---- | ------- | ---------------- | ------- | ---- |
| **A** desenvolvimento | `base_A_autocred_base_desenvolvimento.csv` | 10.000 × 28 | 2022-01 a 2024-12 | sim |
| **B** teste do modelo | `base_B_autocred_base_teste_modelo.csv` | 3.000 × 23 | 2025-01 a 2025-06 | não |
| **C** propostas | `base_C_autocred_base_politica.csv` | 5.000 × 21 | 2025-07 a 2025-12 | não |

**Taxa de default na base A: 8,26%** — bate com os 8,3% do briefing.

| Safra | n | Default |
| ----- | - | ------- |
| 2022 | 3.380 | 8,67% |
| 2023 | 3.290 | 8,94% |
| 2024 | 3.330 | 7,18% |

---

## 🚨 A armadilha: `qtd_parcelas_em_atraso_12m`

**Esta é a variável que decide o desafio.** O dicionário a marca como `Disponível na concessão? = NÃO`, e ela está presente **nas três bases**. Verificado nos dados:

| Base | Valores | Média |
| ---- | ------- | ----- |
| A (treino) | 0 a 7 | **0,903** |
| B (teste) | **só 0** | 0,000 |
| C (propostas) | **só 0** | 0,000 |

**Correlação com o alvo na base A: 0,74.**

O mecanismo da armadilha, passo a passo:

1. Quem não ler o dicionário inclui a variável. Ela domina o modelo — correlação 0,74 com o alvo.
2. O AuROC na validação fica **excelente**, porque a validação também sai da base A.
3. Ao escorar a base B, a variável vale **zero para todos os 3.000 contratos**.
4. O termo que dominava o modelo vira uma constante. O modelo **colapsa**: todo mundo recebe praticamente a mesma PD.
5. **AuROC na avaliação ≈ 0,5** — o mesmo que chutar. E os 30 pontos vão embora.

Não há mensagem de erro em nenhum passo. O código roda, o modelo treina, o CSV sai bonito. É exatamente o que o enunciado avisa: *"um modelo que usa informação do futuro parece excelente na base histórica e não vale nada em produção"*.

> **Regra:** `qtd_parcelas_em_atraso_12m` é **removida na ingestão**, antes de qualquer análise — não na hora de treinar. Variável excluída que continua no DataFrame acaba entrando por um `select_dtypes` distraído.

## Colunas proibidas (pós-concessão)

Todas marcadas `NÃO` no dicionário. Nenhuma pode ser preditora:

| Coluna | O que é | Onde existe |
| ------ | ------- | ----------- |
| `qtd_parcelas_em_atraso_12m` | Parcelas em atraso nos 12 meses seguintes | A, B, C (zerada em B e C) |
| `default_90_12` | **O ALVO** | só A |
| `mes_default` | Mês do default, contado da originação | só A |
| `ead_realizado` | Saldo devedor no default + 3 parcelas vencidas | só A |
| `lgd_realizado` | % do EAD perdido após workout de 24 meses | só A |
| `perda_financeira` | `ead_realizado × lgd_realizado`, em reais | só A |

> `mes_default`, `ead_realizado` e `lgd_realizado` só existem para os inadimplentes (9.174 nulos em 10.000 = os adimplentes). Servem para **conferir** os parâmetros de EAD/LGD, nunca para prever.

## Preditoras (disponíveis na concessão)

| Coluna | Tipo | Observação |
| ------ | ---- | ---------- |
| `valor_financiado` | numérico | Valor do bem menos a entrada |
| `ltv` | numérico | `valor_financiado / valor_bem`. Quanto maior, menor a pele do cliente no jogo |
| `prazo_meses` | inteiro | 24, 36, 48 ou 60 |
| `comprometimento_renda` | numérico | `parcela_mensal / renda_declarada` |
| `canal_originacao` | categórica | Concessionária, Revenda multimarca, Digital, Correspondente bancário |
| `idade_veiculo_anos` | inteiro | 0 = zero quilômetro. **Entra também na tabela de LGD** |
| `idade_cliente` | inteiro | |
| `ocupacao` | categórica | CLT, Autônomo, Servidor público, Empresário, Aposentado |
| `renda_mensal_declarada` | numérico | **770 nulos** (7,7%) |
| `tempo_emprego_meses` | numérico | **1.207 nulos** (12,1%) |
| `tipo_residencia` | categórica | Própria, Financiada, Alugada, Familiar |
| `score_bureau` | numérico | 0 a 1000. **327 nulos** (3,3%) — ausente = sem histórico no bureau, o que é informação, não ruído |
| `qtd_restricoes_ativas` | inteiro | Protestos e negativações na data da proposta |
| `qtd_consultas_bureau_3m` | inteiro | Consultas ao CPF nos 3 meses anteriores |
| `possui_avalista` | categórica | Sim/Não. **Ajuste de −0,061 na LGD** quando Sim |

**Apoio** (não classificadas como preditoras): `valor_bem`, `valor_entrada`, `taxa_juros_am`, `parcela_mensal`, `ano_modelo`, `data_originacao`.

> ⚠️ O tratamento dos nulos (`renda_mensal_declarada`, `tempo_emprego_meses`, `score_bureau`) precisa ser **ajustado só no treino** e aplicado às demais, dentro do `Pipeline`. O dicionário cobra isso explicitamente.

## ⚠️ A base C não tem as variáveis que dependem da política

Este é o segundo ponto estrutural do desafio. Comparando as colunas:

**Existem em A/B mas não em C:** `ltv`, `prazo_meses`, `valor_financiado`, `valor_entrada`, `taxa_juros_am`, `parcela_mensal`, `comprometimento_renda`.

**Só existem em C:** `ltv_desejado`, `prazo_desejado_meses`, `valor_financiado_desejado`, `valor_entrada_desejada`, `pct_entrada_desejada`, `data_proposta`, `id_proposta`.

A base C traz o que o cliente **pediu**, não o que foi contratado — porque o contratado é decisão nossa. Consequência:

> **Quatro preditoras do modelo (`ltv`, `prazo_meses`, `valor_financiado`, `comprometimento_renda`) só existem em C depois que a política decide.** E a política decide olhando a PD, que vem do modelo, que precisa dessas variáveis. **A dependência é circular.**

Como resolver está na [ENTREGÁVEL 1 § 7](ENTREGAVEL_1_MODELO.md) e na [Entregável 2](ENTREGAVEL_2_POLITICA.md): escorar em duas passagens — a primeira com as condições *desejadas* para achar a faixa de score, a segunda com as condições *ofertadas* para estimar o risco do que de fato será contratado.

## A base C é medi­velmente mais arriscada

O "mar aberto" do enunciado não é retórica — aparece nos números:

| Indicador | Base A | Base B | **Base C** |
| --------- | ------ | ------ | ---------- |
| `score_bureau` médio | 645,5 | 646,2 | **549,5** |
| `qtd_restricoes_ativas` média | 0,63 | 0,62 | **1,70** |
| LTV médio | 0,743 | 0,746 | **0,778** (desejado) |

A base C tem score de bureau **96 pontos menor** e **2,7× mais restrições ativas**. São perfis que a política antiga recusava e que, portanto, **não estão representados no treino**. O modelo vai extrapolar — e extrapolação de modelo de crédito subestima risco.

## Parâmetros de EAD e LGD (dados, não modelados)

`AutoCred_parametros_ead_lgd.xlsx`. Origem: contratos inadimplentes da base A.

**Fator de EAD** (× valor financiado) — por prazo e faixa de LTV:

| Prazo | até 60% | 60–70% | 70–80% | 80–90% | >90% |
| ----- | ------- | ------ | ------ | ------ | ---- |
| 24 | 0,980 | 1,003 | 0,995 | 1,013 | 1,002 |
| 36 | 1,021 | 1,015 | 1,020 | 1,015 | 1,027 |
| 48 | 1,024 | 1,027 | 1,032 | 1,040 | 1,038 |
| 60 | 1,040 | 1,037 | 1,041 | 1,040 | 1,042 |

Passa de 1 porque o EAD soma as 3 parcelas vencidas ao saldo devedor. **Varia pouco (0,98–1,04): não é alavanca de política.**

**LGD** — por idade do veículo na originação e faixa de LTV:

| Idade do veículo | até 60% | 60–70% | 70–80% | 80–90% | >90% |
| ---------------- | ------- | ------ | ------ | ------ | ---- |
| 0 a 2 anos | **0,412** | 0,571 | 0,596 | 0,652 | 0,664 |
| 3 a 5 anos | 0,584 | 0,622 | 0,704 | 0,748 | 0,736 |
| 6 a 8 anos | 0,628 | 0,738 | 0,817 | 0,817 | 0,826 |
| 9 anos ou mais | 0,842 | 0,830 | 0,900 | 0,886 | **0,908** |

Ajuste por avalista: **somar −0,061** à LGD da tabela. Workout: 24 meses.

> **Aqui está a alavanca.** A LGD vai de 0,412 a 0,908 — varia **50 pontos percentuais**, contra 6 pontos do fator de EAD. E ela responde a duas coisas que a política controla ou observa: a **faixa de LTV** (que a entrada mínima move) e a **idade do veículo** (que a política pode restringir). Baixar um contrato de 3–5 anos de LTV >90% para LTV ≤60% corta a LGD de 0,736 para 0,584 — **15 pontos de perda a menos, no mesmo cliente**.

**Distribuição do mês do default** (dos que quebram, quando quebram):

| Mês | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
| --- | - | - | - | - | - | - | - | - | - | -- | -- | -- |
| Freq. | 1,45% | 4,12% | 7,02% | 8,84% | 11,38% | 13,80% | 12,71% | 11,74% | 7,63% | 8,60% | 6,78% | 5,93% |

**Mês médio do default: 6,9.** Essa tabela é o que permite simular o ROI internamente: o enunciado diz que *"os juros de um contrato inadimplente contam apenas até o mês do calote"* — com a distribuição acima dá para calcular quantas parcelas um contrato que quebra chega a pagar.

## Formato dos entregáveis

**`submissao_modelo.csv`** — 3.000 linhas (base B):

| id_contrato | pd |
| ----------- | -- |
| T000001 | 0.0412 |

**`submissao_politica.csv`** — 5.000 linhas (base C):

| id_proposta | pd | score_1a10 | decisao | taxa_am | prazo_meses | pct_entrada_minima |
| ----------- | -- | ---------- | ------- | ------- | ----------- | ------------------ |
| P000001 | 0.0166 | 10 | APROVAR | 0.0155 | 60 | 0.00 |
| P000007 | 0.1873 | 3 | NEGAR | | | |

Linha `NEGAR` tem taxa, prazo e entrada **vazios**.
