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

## 3. Método: simular por dentro, decidir por cenário

⚠️ **Correção de rumo depois de ler o enunciado:** **não existe simulador para rodar.** A Base C só reage no dia da apuração, e o enunciado é explícito:

> "A direção de cada efeito está declarada. A intensidade, não — e não há como descobri-la por tentativa e erro, porque **vocês só submetem uma vez**. O caminho é **raciocinar sobre o trade-off, não otimizá-lo às cegas**."

Isso elimina a busca por força bruta. Mas **não** elimina a simulação: os parâmetros dados permitem calcular o ROI de qualquer política **condicionado ao aceite**. O que falta é só a curva de aceite — e essa vira cenário, não chute único.

**O que dá para calcular exatamente** (com `AutoCred_parametros_ead_lgd.xlsx`):

| Componente | Como |
| ---------- | ---- |
| Parcela | Tabela Price com a taxa e o prazo que ofertarmos |
| Juros de quem paga até o fim | `parcela × prazo − valor financiado` |
| Juros de quem quebra | `parcela × mês do default` — ponderado pela **distribuição do mês do default** (média 6,9, pico nos meses 5–8) |
| Perda realizada | `fator_EAD(prazo, faixa LTV) × valor financiado × LGD(idade veículo, faixa LTV)`, com −0,061 se houver avalista |
| Volume financiado | Soma do financiado dos contratos fechados |
| Prazo médio em anos | Média ponderada dos prazos ofertados ÷ 12 |

Com isso o ROI da fórmula oficial sai inteiro — **dado o conjunto de quem aceita**.

**O que não dá para calcular, e vira cenário:**
- Elasticidade do aceite à taxa, à entrada exigida e ao encurtamento de prazo.
- Intensidade da seleção adversa (quanto a PD sobe quando a taxa sobe).

**Método decidido:**

1. **Piso analítico por faixa** — a taxa mínima que cobre `EL` da faixa e ainda sobra. Dá o limite inferior, nunca a resposta.
2. **Simulação interna** do ROI para políticas candidatas, sob **três cenários de aceite** (otimista, central, pessimista) e **dois de seleção adversa** (leve, forte).
3. **Descartar quem viola guard-rail** em qualquer cenário razoável — não só no central.
4. **Escolher a política que é boa nos três cenários**, não a que é ótima no central. Como se submete uma vez só e a intensidade é desconhecida, **robustez vale mais que máximo**: uma política que entrega ROI 18% nos três cenários vence uma que entrega 24% no central e viola o volume no pessimista, porque essa última perde metade da nota.

## 4. Aritmética que já dá para fazer

Com a Base C em mãos, os números deixam de ser hipótese.

**Base C:** 5.000 propostas, volume financiado **desejado** de **R$ 167,1 milhões**, ticket médio **R$ 33.411** (mediana R$ 28.706).

**O volume aperta mais do que parece.** O guard-rail conta **contratos fechados**, não aprovados (o enunciado é explícito: proposta recusada pelo cliente "apenas não existe"). Então:

```
R$ 40.000.000 ÷ R$ 33.411 = 1.197 contratos EFETIVADOS
```

Aprovando o mínimo de 1.750 propostas, isso exige **aceite de 68%**. E aí entra a segunda mordida: **exigir entrada reduz o ticket**. Uma entrada adicional de 10 pontos percentuais sobre o valor do bem corta o financiado em ~13% (o LTV médio desejado é 0,778), derrubando o ticket para ~R$ 29.100 — e a exigência sobe para **1.375 contratos**, ou **aceite de 79%**, justo quando a entrada maior está derrubando o aceite.

> ⚠️ **A tensão central da política:** entrada mínima é a alavanca mais eficiente para o risco (derruba PD e LGD juntas), mas ataca o volume **duas vezes** — reduz o ticket de cada contrato **e** reduz quantos clientes aceitam. **Aprovar exatamente o mínimo de 35% é uma aposta apertada.** Provavelmente é preciso aprovar acima do piso e compensar o risco pelo preço e pela entrada nas faixas ruins, em vez de defender o volume só pelo corte.

**E a inadimplência é o limite que mais aperta.** O guard-rail é **≤ 8% dos contratos fechados**. A base A — que é a carteira da política antiga, já filtrada por ela — fechou em **8,26%**. E a Base C é pior: score de bureau 96 pontos menor e 2,7× mais restrições ativas. Ou seja:

> **O limite de inadimplência já era violado pela política antiga, numa população melhor do que a que vamos enfrentar.** Não dá para bater esse guard-rail aprovando amplamente: ele exige corte de risco real. Este é, muito provavelmente, o **limite que decide a política** — e a tentação de aprovar mais para salvar o volume esbarra exatamente nele.

**Onde a LGD dá dinheiro.** O fator de EAD varia entre 0,980 e 1,042 — 6 pontos, irrelevante. A LGD varia de **0,412 a 0,908** — 50 pontos, e responde a duas coisas que a política enxerga:

| Alavanca | Efeito na LGD |
| -------- | ------------- |
| Baixar a faixa de LTV (entrada) | Veículo de 3–5 anos: **0,736 → 0,584** indo de >90% para ≤60%. **15 pontos** |
| Restringir idade do veículo | Veículo 0–2 anos com LTV ≤60%: **0,412**. Veículo 9+ anos com LTV >90%: **0,908**. **50 pontos** |
| Exigir avalista | **−0,061**, direto |

A idade do veículo é a variável mais subestimada aqui: ela não é alavanca de preço, é **critério de elegibilidade**. Um contrato de veículo com 9+ anos e LTV alto perde 90% da exposição quando quebra — quase nenhuma taxa dentro do teto cobre isso. Vale avaliar uma regra de corte por idade do veículo, além do corte por score.

**Espaço de preço.** Com teto de 3,5% a.m. e 36 meses, os juros de um contrato pago até o fim somam ~77% do principal. Contra a perda esperada, sobra margem — **desde que o contrato seja pago**. Mas o enunciado lembra que **quem quebra pagou só até o mês do calote**, e a distribuição mostra que o default acontece cedo: **mês médio 6,9**, com pico entre o 5º e o 8º. Um contrato de 48 meses que quebra no mês 6 devolveu 6 parcelas e levou o EAD inteiro. **Precificar como se o inadimplente pagasse metade do contrato superestima a receita.**

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

## 6. Perguntas — o que o enunciado respondeu e o que falta

**Respondidas pelo material de 13/09:**

| Pergunta | Resposta |
| -------- | -------- |
| Volume conta aprovadas ou aceitas? | **Aceitas.** "Só entra na conta quem efetivamente contratou. Proposta aprovada que o cliente recusa não gera receita nem prejuízo — apenas não existe" |
| Inadimplência sobre o quê? | **"8% dos contratos fechados"** — quantidade, sobre os efetivados |
| Haverá simulador para calibrar? | **Não.** Submissão única, sem feedback. As intensidades não serão reveladas |
| `valor_bem` está na Base C? | **Sim**, junto com `pct_entrada_desejada` e `ltv_desejado` — dá para recalcular o LTV sob qualquer entrada exigida |

**Ainda em aberto:**

1. **Custo de captação (funding) e despesa operacional por contrato.** Sem eles, "cobrir a perda e ainda sobrar" não tem piso definido — o ROI de 15% a.a. é líquido de quê? A fórmula oficial do ROI não subtrai custo de captação, o que sugere que o ROI apurado é **antes** do funding; convém confirmar, porque muda a taxa mínima de cada faixa.
2. **O documento "AutoCred — Regras da Competição"**, citado no fim do enunciado como fonte das regras completas de submissão e da rubrica. Não veio no pacote.
3. **Para qual e-mail enviar**, e se os três arquivos vão juntos.
4. **A taxa de aprovação de 35% é sobre as 5.000 propostas** (e não sobre as elegíveis) — o enunciado diz "35% das 5.000 propostas", o que parece fechar a questão, mas vale confirmar que propostas negadas por regra de elegibilidade (ex.: idade do veículo) contam no denominador.

## 7. Critérios de aceite

- [ ] Tabela de faixas preenchida, monotônica nas quatro alavancas
- [ ] Toda faixa aprovada tem taxa que cobre a própria perda esperada
- [ ] Os quatro guard-rails verificados por script, não a olho
- [ ] CSV com 5.000 linhas, ids idênticos aos da Base C
- [ ] Validador de coerência passa sem erro
- [ ] Sensibilidade testada: o que acontece com o ROI se o aceite for 10 pontos pior que o assumido
- [ ] Cada decisão da tabela tem uma frase de justificativa — é o insumo da defesa
