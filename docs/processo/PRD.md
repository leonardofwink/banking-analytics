# Plano de execução — Desafio AutoCred

> **Passo a passo:** [`ROADMAP.md`](ROADMAP.md) — o objetivo final quebrado em 11 passos.
>
> **Requisitos** (o que o professor pediu): [`DESAFIO.md`](../DESAFIO.md) · **Como faremos**: [`ENTREGAVEL_1_MODELO.md`](../ENTREGAVEL_1_MODELO.md) e [`ENTREGAVEL_2_POLITICA.md`](../ENTREGAVEL_2_POLITICA.md) · **Aulas**: [`MENTORIA.md`](MENTORIA.md)
>
> Este documento é só o **plano**: quem faz o quê, em que ordem, até quando.

## Metodologia — SDD (Spec Driven Development)

A spec vem antes do código, e é o contrato:

```
Requisito (DESAFIO.md)  ──►  Spec do passo (docs/specs/S0x)  ──►  Implementação  ──►  Validação contra os critérios de aceite
                                   ▲                                            │
                                   └──────── divergiu? atualiza a spec ◄────────┘
```

Três regras:
1. **Código que diverge da spec está errado** até a spec ser atualizada — não o contrário.
2. **Mudança de requisito entra pelo `DESAFIO.md` primeiro**, e desce para as specs.
3. **Critérios de aceite são verificáveis por script**, não por opinião. Guard-rail conferido "a olho" não conta.

Por que isso importa aqui em particular: **o grupo trabalha em paralelo em três frentes**, e a interface entre elas é a spec. Quem faz a política precisa saber o contrato de saída do modelo antes de o modelo existir; quem faz a defesa precisa saber o que foi decidido e por quê, sem reconstituir a conversa.

## Divisão do grupo

| Papel | Responsável | Entregável | Spec |
| ----- | ----------- | ---------- | ---- |
| Modelagem | — | Modelo de PD (40 pts) | [Entregável 1](../ENTREGAVEL_1_MODELO.md) |
| **Política e precificação** | **Leonardo** | Tabela de faixas + CSV (40 pts) | [Entregável 2](../ENTREGAVEL_2_POLITICA.md) |
| Negócio e defesa | — | Apresentação ao conselho (20 pts) | — |

**O grupo decidiu que todos desenvolvem todas as partes**, comparam resultados e juntam o melhor de cada um. Os papéis acima marcam quem responde pela entrega final de cada bloco, não quem trabalha nele.

> ⚠️ **Consequência desse modelo: a comparação só vale se os três medirem igual.** Três pessoas modelando em paralelo com splits, sementes ou recortes diferentes produzem AuROCs que não são comparáveis — a diferença pode ser o método de medição, não a qualidade do modelo, e o grupo acaba escolhendo o mais otimista em vez do melhor. Antes de qualquer um começar a modelar, fixar: **mesmo split temporal (treino 2022–23, validação 2024), mesma semente, mesma métrica, mesma definição de default**. O que varia é o modelo; o resto é constante, senão não é experimento.

**A interface entre as frentes é o contrato de saída do modelo** (`escorar(df) -> pd`, § 7 da SPEC 01). Com ele fixado, a política pode ser construída e testada com uma PD provisória enquanto o modelo final ainda está sendo escolhido — as duas frentes não se bloqueiam.

## Dependências externas

**Recebido em 13/09** (em `dados/brutos/professor/`, fora do git): enunciado, dicionário de dados, parâmetros de EAD/LGD, as três bases e os modelos de submissão. **Nada mais bloqueia o início.**

| Ainda falta | De quem | Bloqueia |
| ----------- | ------- | -------- |
| Documento "AutoCred — Regras da Competição" | Professor | Confirmação da rubrica e das regras de submissão |
| E-mail de destino da entrega | Professor | Só o envio, no dia 25 |
| Custo de captação e despesa operacional | Professor | Piso da taxa por faixa ([ENTREGÁVEL 2 § 6](../ENTREGAVEL_2_POLITICA.md#6-perguntas--o-que-o-enunciado-respondeu-e-o-que-falta)) |

> Não há simulador da Base C: **a submissão é única e sem feedback**. A política é decidida por raciocínio sobre o trade-off e testada por cenários internos, não calibrada por tentativa.

## Decisões de modelagem

> **Regra crítica 5 do [`AGENTS.md`](../../AGENTS.md):** decisão de modelagem se registra **antes** de ser usada. Sem isso, o resultado de hoje não é comparável com o de amanhã — e uma premissa que ninguém precisou declarar é uma premissa que ninguém questiona.
>
> Decisões dos passos S01–S12 estão nas specs correspondentes. Esta seção recebe as que **atravessam** passos.

### D1 · A âncora de preço passa a ser referência externa, não o livro da AutoCred

**Registrada em 28/09/2026, para o [S13](../specs/S13_POST_MORTEM_E_RECUPERACAO.md).**

`TAXA_MERCADO = 0.0159` (`banking/roi.py:49`) é a média da taxa praticada na Base A — o **livro da própria AutoCred** — e é usada como denominador de `excesso = taxa / TAXA_MERCADO − 1`, isto é, como *"o preço que o cliente encontra no concorrente"*.

**O concorrente é o mercado, e o preço do mercado é público.** A recuperação passa a ancorar em série do Banco Central para crédito a pessoa física, aquisição de veículos, no período da Base C.

**A razão anterior para recusar, que estava errada.** Durante a análise a referência externa foi considerada e descartada com o argumento de que *"trazer dado de fora para um exercício fechado é arriscado na banca"*. O grupo vencedor fez exatamente isso e o professor registrou como diferencial: *"fez o que nenhum outro fez — comparou a taxa proposta com dados públicos do Banco Central… preço defensável, não arbitrado."*

Fica escrito porque **decisão revertida sem o motivo registrado volta a ser tomada**.

**Onde é usada:** `recuperacao/27_ancora_de_mercado.py` produz o valor; `Premissas.taxa_mercado` o carrega. A âncora antiga sobrevive em `PREMISSAS_SUBMETIDAS`, para a comparação continuar honesta.

**Procedência é obrigatória:** série, período e data de extração ficam em [`FONTES_EXTERNAS.md`](../FONTES_EXTERNAS.md). Dado externo sem procedência não entra.

#### D1.1 · Qual das duas réguas — decidida em 28/09/2026

O BCB dá duas respostas para "quanto o mercado cobrava", e elas respondem perguntas diferentes:

| Régua | Valor | Responde |
| ----- | ----- | -------- |
| Mediana por instituição (Olinda, 53 instituições) | 1,820% a.m. | *"o concorrente típico cobra quanto?"* |
| **Média ponderada por volume (SGS 20749)** | **2,021% a.m.** | *"o dinheiro emprestado no mercado saiu a quanto?"* |

**Escolhida: a ponderada por volume.** Não pelo argumento conceitual — os dois são defensáveis — mas porque **um dado independente discriminou**.

A calibração do aceite (S13.5) foi rodada com as duas. Nos números de ROI e volume, a mediana ajusta ligeiramente melhor. Mas o professor afirmou que a nossa política com 0,7 ponto a mais na taxa ficaria *"dentro dos quatro guard-rails"*, e essa afirmação **não entrou em nenhuma das duas calibrações**:

| Âncora | Inadimplência prevista nessa política |
| ------ | ------------------------------------- |
| Mediana (1,820%) | **8,2%** — estoura o teto de 8% |
| Ponderada (2,021%) | **dentro** — os quatro guard-rails fecham |

Uma informação qualitativa, independente de ROI e de volume, separou as duas. É o tipo de teste que vale mais que preferência metodológica.

**Registrado como premissa nomeada** em `banking/roi.py`: `PREMISSAS_CALIBRADAS`, âncora 2,021%, com `CENARIO_CALIBRADO` (`a0` 0,838 · `beta_taxa` 1,186 · `gama` 1,072). `PREMISSAS_SUBMETIDAS` continua intacta ao lado, porque é o registro do que foi defendido.

### D2 · O critério de escolha passa a ser máximo ROI com piso de 15%

**Registrada em 28/09/2026, para o [S13](../specs/S13_POST_MORTEM_E_RECUPERACAO.md).**

O S09 escolheu por **viabilidade nos três cenários** (`09_buscar_politica.py:6-8`) e desempate por folga. Os quatro limites do enunciado eram invioláveis; a exigência de robustez nos três cenários era **nossa**; e quando o conjunto ficou vazio, foi a meta de **15% exigida pelo conselho** que cedeu.

A recuperação inverte a assimetria: os 15% entram como **quinto guard-rail**, e o que cede é a premissa.

**O que isso não significa.** Não é abandonar análise de cenário — o grupo vencedor *"testou subir a taxa em 0,3 ponto, viu que romperia dois guard-rails no cenário severo e desistiu"*. A política escolhida segue sendo reportada sob o cenário severo; a diferença é que a robustez deixa de **filtrar** e passa a **informar**.

**Onde é usada:** `recuperacao/29_politica_sob_piso.py`. `EMPATE_ROI` não se aplica.

### O que deixou de valer com a apuração

A seção *Dependências externas* registra que *"a submissão é única e sem feedback"* e que a política seria *"testada por cenários internos, não calibrada por tentativa"*. Isso valia até 26/09/2026.

A apuração devolveu ROI e volume realizados por grupo, e o aceite do vencedor a um preço conhecido. **A elasticidade do aceite deixou de ser premissa e passou a ser estimável** — é o que o S13.5 faz.

## Cronograma

Prazo: **25/09** (entrega por e-mail). Leaderboard: **26/09**.

| Quando | O quê | Frente |
| ------ | ----- | ------ |
| Ao receber as bases | Dicionário de dados; conferir o que existe no momento da proposta (anti-vazamento) | Modelagem |
| | EDA: distribuições, missing, taxa de default por safra | Modelagem |
| ~16–19/09 | Baseline logística → RF → XGBoost, validação out-of-time em 2024 | Modelagem |
| | PSI de A/B contra C; avaliar o viés de seleção | Modelagem |
| ~17–21/09 | Tabela de faixas v1 com PD provisória; validador do CSV | Política |
| ~21–23/09 | Modelo escolhido e retreinado em A; escoragem de B e C | Modelagem |
| | Busca da política sobre a Base C; verificação dos guard-rails | Política |
| ~23–24/09 | Teste de sensibilidade; congelar a política | Política |
| | Montar o encadeamento PD → EAD → LGD → perda → preço → ROI | Defesa |
| **25/09** | **Validador roda → envio do e-mail com o CSV** | Todos |

> Folga proposital de um dia antes do prazo. Submissão em cima da hora é onde erro de formato acontece — e formato vale 10 pontos.

## Riscos do projeto

| Risco | Mitigação |
| ----- | --------- |
| Bases chegam tarde e sobra pouco tempo | Specs, validador e esqueleto do pipeline prontos **antes** do dado. Quando a base chegar, é só rodar |
| Viés de seleção (A/B aprovados × C mar aberto) | [ENTREGÁVEL 1 § 6](../ENTREGAVEL_1_MODELO.md#6--risco-central-as-bases-a-e-b-são-de-aprovados-a-base-c-é-mar-aberto). Tratar a PD como ordenação confiável, nível suspeito |
| Otimizar AuROC e perder no ROI | Os blocos valem 40 + 40. Modelo bom com política ruim perde |
| Política no limite de um guard-rail | Escolher a robusta, não a máxima — margem deliberada |
| Erro de formato no CSV | Validador obrigatório antes do envio |
