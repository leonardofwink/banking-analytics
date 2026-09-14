# Plano de execução — Desafio AutoCred

> **Requisitos** (o que o professor pediu): [`DESAFIO.md`](DESAFIO.md) · **Como faremos**: [`SPEC_01_MODELO_PD.md`](SPEC_01_MODELO_PD.md) e [`SPEC_02_POLITICA.md`](SPEC_02_POLITICA.md) · **Aulas**: [`MENTORIA.md`](MENTORIA.md)
>
> Este documento é só o **plano**: quem faz o quê, em que ordem, até quando.

## Metodologia — SDD (Spec Driven Development)

A spec vem antes do código, e é o contrato:

```
Requisito (DESAFIO.md)  ──►  Spec (SPEC_0x)  ──►  Implementação  ──►  Validação contra os critérios de aceite
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
| Modelagem | *a definir* | Modelo de PD (40 pts) | [SPEC 01](SPEC_01_MODELO_PD.md) |
| Política e precificação | *a definir* | Tabela de faixas + CSV (40 pts) | [SPEC 02](SPEC_02_POLITICA.md) |
| Negócio e defesa | *a definir* | Apresentação ao conselho (20 pts) | — |

**A interface entre as frentes é o contrato de saída do modelo** (`escorar(df) -> pd`, § 7 da SPEC 01). Com ele fixado, a política pode ser construída e testada com uma PD provisória enquanto o modelo final ainda está sendo escolhido — as duas frentes não se bloqueiam.

## Dependências externas (bloqueiam o início)

| O que falta | De quem | Bloqueia |
| ----------- | ------- | -------- |
| Bases A, B e C (arquivo Excel) | Professor | Tudo |
| Tabela de EAD e LGD | Professor | Perda esperada → política |
| Documentação do simulador da Base C | Professor | Otimização da política |
| Respostas às 5 perguntas da [SPEC 02 § 6](SPEC_02_POLITICA.md#6-perguntas-para-o-professor) | Professor | Precificação |

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
| Viés de seleção (A/B aprovados × C mar aberto) | [SPEC 01 § 6](SPEC_01_MODELO_PD.md#6--risco-central-as-bases-a-e-b-são-de-aprovados-a-base-c-é-mar-aberto). Tratar a PD como ordenação confiável, nível suspeito |
| Otimizar AuROC e perder no ROI | Os blocos valem 40 + 40. Modelo bom com política ruim perde |
| Política no limite de um guard-rail | Escolher a robusta, não a máxima — margem deliberada |
| Erro de formato no CSV | Validador obrigatório antes do envio |
