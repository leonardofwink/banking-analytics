# Desafio AutoCred — briefing

> **Fonte:** slides apresentados na mentoria em 2026-09-12. Este documento é a **captura fiel do que foi pedido** — não misture decisões nossas aqui. O que nós decidimos vive nas specs ([`SPEC_01_MODELO_PD.md`](SPEC_01_MODELO_PD.md), [`SPEC_02_POLITICA.md`](SPEC_02_POLITICA.md)).
>
> Regra: mudou o briefing (material novo do professor), atualiza aqui **primeiro**; as specs se ajustam depois.

---

## A empresa

**AutoCred** — fintech de financiamento de carros, operando desde 2022.

Cresceu rápido, com **política escrita em 2022 e nunca revisada**. O conselho concluiu que o problema **não está na cobrança, e sim na porta de entrada**.

| Indicador | Valor | Observação |
| --------- | ----- | ---------- |
| **LTV médio** | 74% | há contratos com 95% |
| **Inadimplência** | 8,3% | PD 90/12 da carteira |
| **LGD média** | 70% | retomada ainda imatura |
| **ROI exigido** | 15% ao ano | pelo conselho |

> **LTV** (*Loan to Value*): razão entre o que se empresta e o valor da garantia. `LTV = valor financiado / valor do bem`.

## Os dois entregáveis

Cada grupo entrega os dois. **Eles são avaliados separadamente.**

| # | Entregável | O que é | Métrica oficial |
| - | ---------- | ------- | --------------- |
| **1** | **Modelo de PD** | Estimar a probabilidade de o contrato atingir **90 dias de atraso nos 12 meses após a concessão** | **AuROC**, medido em uma base out-of-time que não conhecemos |
| **2** | **Política de crédito** | Transformar o score em decisão: **a quem conceder, a que preço, em que prazo, com quanta entrada** | **ROI anualizado** da carteira que a política gerar |

## As três bases

| Base | O que é |
| ---- | ------- |
| **A · desenvolvimento** | 10.000 contratos de **2022 a 2024**, com o alvo e os **realizados de EAD e LGD** |
| **B · teste do modelo** | 3.000 contratos de **2025**, mesmas variáveis, **sem o alvo** — é aqui que o AuROC é medido |
| **C · propostas** | 5.000 propostas para aplicar a política — **sem taxa e sem prazo**, porque isso é decisão nossa |

> ⚠️ **As bases A e B só contêm contratos aprovados pela política antiga. A base C é de mar aberto.**

## Do score ao resultado

A cadeia inteira, que é o que precisamos fechar:

```
Modelo de PD  ──►  Perda esperada  ──►  Faixa de score  ──►  Preço e condições  ──►  ROI da carteira
(prob. calote)     (PD × EAD × LGD)     (1 = pior,          (taxa, prazo,          (o que o conselho
                                         10 = melhor)        entrada)                vai olhar)
```

**Fórmula oficial do ROI:**

```
ROI anual = [ (juros recebidos − perda realizada) ÷ volume financiado ] ÷ prazo médio em anos
```

> Neste desafio, **EAD e LGD vêm prontos, em tabela**. Nós modelamos a PD e decidimos a política: é onde mora a decisão de negócio.

## O que a taxa precisa cobrir

Exemplo **ilustrativo** da ordenação (fornecido pelo professor — os números da nossa carteira sairão do nosso modelo):

| Score | PD | EAD (× valor financiado) | LGD | Perda esperada | Isso significa |
| ----- | -- | ------------------------ | --- | -------------- | -------------- |
| 10 | 0,1% | 1,03 | 58% | 0,1% | praticamente sem risco de perda |
| 9 | 1,5% | 1,03 | 60% | 0,9% | taxa baixa já cobre com folga |
| 8 | 3,0% | 1,03 | 64% | 2,0% | preço padrão resolve |
| 6 | 8,5% | 1,03 | 69% | 6,0% | precisa de preço acima do padrão |
| 5 | 10,0% | 1,03 | 70% | 7,2% | exigir entrada pode salvar a faixa |
| 3 | 19,5% | 1,03 | 71% | 14,3% | quase nenhuma taxa legal cobre |
| 1 | 60,0% | 1,03 | 72% | 44,5% | não há preço que resolva |

Dois padrões a notar: **EAD > 1** (o saldo no default inclui juros acumulados) e **LGD cresce com o risco** (58% no topo, 72% na base) — pior perfil recupera pior.

## As quatro alavancas

Uma política de crédito é **uma tabela de regras, não um modelo**.

| Alavanca | O que faz | Tensão |
| -------- | --------- | ------ |
| **Aprovar ou negar** | O corte de score define o perfil da carteira | Cortar fundo demais derruba a originação, e a empresa precisa crescer |
| **Taxa de juros** | É a receita. Precisa cobrir a perda esperada da faixa **e ainda sobrar** | **Teto de 3,5% ao mês** |
| **Prazo máximo** | Prazo longo cabe no bolso do cliente | Mas alonga a exposição ao risco. Encurtar demais inviabiliza a parcela |
| **Entrada mínima** | Reduz o LTV — e **LTV menor derruba PD e LGD ao mesmo tempo** | É a alavanca mais subestimada |

## A Base C reage às nossas decisões

**Não há um desfecho fixo esperando para ser revelado** — a base C é um **simulador**:

1. **Taxa alta afasta o cliente.** Ele tem concorrente. Preço acima do mercado derruba a taxa de aceite, e proposta não aceita não gera receita nenhuma.
2. **Taxa alta também aumenta a PD.** Quem aceita pagar caro costuma ser quem não tem alternativa. **Seleção adversa é real, e ela está no simulador.**
3. **Exigir entrada reduz o risco de verdade.** LTV menor significa PD e LGD menores. Mas cada ponto de entrada a mais também derruba o aceite.

## Quatro limites inegociáveis (guard-rails)

O conselho não quer só ROI: quer **ROI dentro do apetite de risco, e sem parar de crescer**.

| Guard-rail | Limite | Se descumprir |
| ---------- | ------ | ------------- |
| Taxa de aprovação | **no mínimo 35%** das propostas | nota de política pela metade |
| Teto de taxa (CET) | **no máximo 3,5% ao mês** | taxa truncada no teto |
| Inadimplência da carteira | **no máximo 8%** dos contratos | nota de política pela metade |
| Volume originado | **no mínimo R$ 40 milhões** | nota de política pela metade |

## Como somos avaliados

**100 pontos, mais 5 de bônus.**

| Bloco | Critério | Pontos |
| ----- | -------- | ------ |
| **Modelo: 40%** | AuROC na base out-of-time (**relativo ao melhor grupo**) | 30 |
| | Qualidade técnica: sem vazamento, split correto, Pipeline, reprodutibilidade | 10 |
| **Política: 40%** | ROI anualizado na Base C (**relativo ao melhor grupo**) | 25 |
| | Coerência entre a tabela de faixas e o que foi submetido | 10 |
| | Volume originado | 5 |
| **Defesa: 20%** | Encadeamento PD → EAD → LGD → perda → preço → ROI | 20 |

> As notas de ROI são **relativas**: o melhor grupo leva a pontuação cheia.

## Formato da submissão

Arquivo `.csv` escorado, enviado **por e-mail**. Modelo fornecido: `submissao_politica_EXEMPLO.csv`

| id_proposta | pd | score_1a10 | decisao | taxa_am | prazo_meses | pct_entrada_minima |
| ----------- | -- | ---------- | ------- | ------- | ----------- | ------------------ |
| P000001 | 0.0166 | 10 | APROVAR | 0.0155 | 60 | 0.0 |
| P000002 | 0.0298 | 9 | APROVAR | 0.017 | 60 | 0.05 |
| P000003 | 0.0412 | 8 | APROVAR | 0.0195 | 48 | 0.1 |
| P000004 | 0.0721 | 7 | APROVAR | 0.0235 | 48 | 0.2 |
| P000005 | 0.0955 | 6 | APROVAR | 0.028 | 36 | 0.3 |
| P000006 | 0.1104 | 5 | APROVAR | 0.032 | 36 | 0.4 |
| P000007 | 0.1873 | 3 | NEGAR | | | |
| P000008 | 0.2431 | 1 | NEGAR | | | |

Regras que o exemplo revela:
- `pd` é a **probabilidade**, em fração (0–1), com 4 casas.
- `score_1a10` é inteiro de 1 a 10, **10 = melhor**.
- `decisao` é `APROVAR` ou `NEGAR`, em maiúsculas.
- Linha `NEGAR` tem **taxa, prazo e entrada vazios**.
- `taxa_am` é a taxa **ao mês**, em fração (`0.0155` = 1,55% a.m.).
- `pct_entrada_minima` em fração (`0.3` = 30%).
- No exemplo, score **melhor** → taxa menor, prazo maior, entrada menor. A ordenação é monotônica.

## Prazos e organização

| Data | O quê |
| ---- | ----- |
| **25/09/2026** | **Prazo limite** — entrega do modelo e da política (e-mail com o `.csv` escorado) |
| **26/09/2026** | Próxima mentoria — **leaderboard** |

**Divisão do grupo (3 pessoas):**

| Papel | Responsabilidade |
| ----- | ---------------- |
| Modelagem | Entregável 1 — modelo de PD |
| Política e precificação | Entregável 2 — tabela de faixas, taxa, prazo, entrada |
| Negócio e defesa | Bloco de defesa (20%) — o encadeamento PD → ROI diante do conselho |

**Material ainda pendente do professor:** as bases (arquivo Excel), a tabela de EAD e LGD, e a documentação do simulador da Base C.

---

## A frase de fechamento

> O grupo que vencer **não será o que tiver o maior AuROC**. Será o que conseguir explicar, diante do conselho, **por que aprovou quem aprovou, por que cobrou o que cobrou, e por que isso dava o retorno que dava**.
>
> **Modelo é meio. Decisão é o fim.**
