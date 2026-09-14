# SPEC 02 — Política de crédito e precificação

> **Entregável 2** do [desafio AutoCred](DESAFIO.md). Vale **40 pontos**: 25 pelo ROI na Base C (relativo ao melhor grupo) + 10 pela coerência entre a tabela de faixas e o que foi submetido + 5 pelo volume originado.
>
> **Status:** aguardando as bases e a documentação do simulador.

## 1. Objetivo

Transformar a PD em decisão. O artefato central **não é um modelo, é uma tabela**: 10 linhas, uma por faixa de score, cada uma dizendo **aprovar ou negar, a que taxa, em que prazo, com quanta entrada**.

```
Maximizar:  ROI anual = [ (juros recebidos − perda realizada) ÷ volume financiado ] ÷ prazo médio em anos

Sujeito a:  taxa de aprovação  ≥ 35% das propostas
            taxa               ≤ 3,5% ao mês
            inadimplência      ≤ 8% dos contratos
            volume originado   ≥ R$ 40 milhões
```

Guard-rail descumprido **corta a nota de política pela metade** — exceto o teto de taxa, que é truncado. Ou seja: **uma política com ROI espetacular e 34% de aprovação vale menos que uma política mediana dentro dos limites.** Respeitar os quatro limites vem antes de otimizar.

## 2. A tabela de faixas (o artefato)

| Score | Faixa de PD | Decisão | Taxa a.m. | Prazo (meses) | Entrada mínima |
| ----- | ----------- | ------- | --------- | ------------- | -------------- |
| 10 | | | | | |
| 9 | | | | | |
| … | *a preencher quando a PD existir* | | | | |
| 1 | | | | | |

**Regras de construção:**

1. **Monotonicidade** — score melhor não pode receber condição pior. Taxa não-crescente, prazo não-decrescente, entrada não-crescente conforme o score sobe. É o que o exemplo do professor mostra, e é o que torna a política defensável: qualquer inversão exige explicação diante do conselho.
2. **Faixas por PD, não por quantil** — o corte de score sai da PD, para que a faixa signifique a mesma coisa em qualquer base. Faixa por quantil muda de sentido quando a população muda (e a base C é outra população).
3. **Toda linha aprovada precisa cobrir a própria perda esperada.** `EL_faixa = PD × EAD × LGD`. Taxa que não cobre a EL da faixa é prejuízo contratado.

## 3. Método: buscar, não derivar

A tentação é derivar a taxa analiticamente (`taxa = funding + EL + opex + margem`). Isso serve como **ponto de partida**, mas não como resposta, por um motivo: **a Base C reage**. Taxa alta derruba o aceite e ainda piora a PD por seleção adversa — dois efeitos que a fórmula não enxerga.

Método decidido:

1. **Ponto de partida analítico** — para cada faixa, a taxa mínima que cobre `EL + funding + opex + margem`. Dá o piso.
2. **Busca sobre a tabela** — varrer combinações de (corte de aprovação × taxa × prazo × entrada) por faixa, simulando o ROI na Base C.
3. **Filtrar pelos guard-rails** antes de comparar ROI. Candidata que viola limite está fora, por melhor que seja o número.
4. **Escolher a robusta, não a máxima.** Se a melhor combinação tem ROI 0,3 ponto acima da segunda e fica a 0,2 ponto de violar o limite de inadimplência, a segunda é a resposta. O simulador tem aleatoriedade; uma política no limite quebra na hora da avaliação.

## 4. Aritmética que já dá para fazer

**Volume mínimo × aprovação mínima.** 5.000 propostas × 35% = **1.750 aprovações**. Para chegar a R$ 40 milhões:

```
R$ 40.000.000 ÷ 1.750 = R$ 22.857 por contrato
```

Se o ticket médio da Base C for maior que isso, o volume vem sozinho com a aprovação mínima e o guard-rail de R$ 40 mi não morde. Se for menor, **aprovar 35% não basta** — o volume passa a ser a restrição ativa, e é preciso aprovar mais, ou aprovar mais caro (ticket maior), ou exigir menos entrada (entrada reduz o valor financiado e, portanto, o volume originado).

> ⚠️ **Tensão a resolver:** entrada mínima é a alavanca mais eficiente para risco (derruba PD e LGD juntas), **mas reduz o volume financiado** — que é guard-rail e vale 5 pontos. Exigir 30% de entrada em metade da carteira pode cortar o volume abaixo dos R$ 40 mi. Essas duas alavancas puxam em direções opostas e precisam ser otimizadas **juntas**, nunca uma de cada vez.

**Espaço de preço.** Com teto de 3,5% a.m. e prazo de 36 meses, os juros de um contrato pago até o fim somam ~77% do principal. Contra uma perda esperada de 14,3% (score 3 da tabela ilustrativa), sobra margem — **desde que o contrato seja pago**. O que estreita a política não é a matemática do preço, é o **aceite** (taxa alta afasta) e o **guard-rail de 8% de inadimplência**. Tratar o problema como "qual taxa cobre a perda" resolve a parte fácil.

## 5. Contrato do arquivo de submissão

`submissao_politica.csv` — uma linha por proposta da Base C (5.000 linhas + cabeçalho).

| Coluna | Tipo | Regra |
| ------ | ---- | ----- |
| `id_proposta` | texto | Exatamente o id da Base C. Nenhum a mais, nenhum a menos |
| `pd` | fração 0–1 | Saída do modelo. 4 casas decimais |
| `score_1a10` | inteiro 1–10 | 10 = melhor. Derivado da `pd` pela tabela de faixas |
| `decisao` | `APROVAR` / `NEGAR` | Maiúsculas |
| `taxa_am` | fração 0–1 | Taxa **ao mês** (`0.0155` = 1,55%). ≤ `0.035`. **Vazio se NEGAR** |
| `prazo_meses` | inteiro | **Vazio se NEGAR** |
| `pct_entrada_minima` | fração 0–1 | `0.3` = 30%. **Vazio se NEGAR** |

**Validador obrigatório antes de enviar** (os 10 pontos de coerência dependem disso): um script que confere, linha a linha, que o CSV bate com a tabela de faixas — mesmo score para a mesma PD, mesma taxa/prazo/entrada para o mesmo score, campos vazios em todo `NEGAR`, ids completos, taxa dentro do teto, e a taxa de aprovação resultante ≥ 35%. **Nenhum arquivo é enviado sem passar.**

Erro de formato aqui custa mais barato de evitar do que de explicar depois.

## 6. Perguntas para o professor

Respostas que mudam a política e que não estão nos slides:

1. **O volume originado de R$ 40 mi conta as propostas aprovadas ou só as aceitas pelo cliente?** Se for aceitas, a conta do § 4 muda: com 60% de aceite seriam ~1.050 contratos e ticket médio de R$ 38 mil. Isso desloca todo o ponto de operação.
2. **Qual o custo de captação (funding) e a despesa operacional por contrato?** Sem eles, a taxa mínima que "cobre a perda e ainda sobra" não tem piso definido — o ROI exigido de 15% a.a. é o retorno depois de qual custo?
3. **A inadimplência de 8% é medida sobre contratos aceitos, em quantidade ou em valor?** O guard-rail diz "8% dos contratos", o que sugere quantidade — confirmar.
4. **A documentação do simulador da Base C será fornecida** (curva de aceite em função da taxa, e o efeito de seleção adversa)? Sem isso, a busca do § 3 vira chute e só dá para testar sensibilidade sob premissas assumidas.
5. **O valor do bem está na Base C?** É necessário para calcular o LTV e, portanto, o efeito da entrada mínima sobre PD e LGD.

## 7. Critérios de aceite

- [ ] Tabela de faixas preenchida, monotônica nas quatro alavancas
- [ ] Toda faixa aprovada tem taxa que cobre a própria perda esperada
- [ ] Os quatro guard-rails verificados por script, não a olho
- [ ] CSV com 5.000 linhas, ids idênticos aos da Base C
- [ ] Validador de coerência passa sem erro
- [ ] Sensibilidade testada: o que acontece com o ROI se o aceite for 10 pontos pior que o assumido
- [ ] Cada decisão da tabela tem uma frase de justificativa — é o insumo da defesa
