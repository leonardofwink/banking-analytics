# Dicionário de dados

> **Status: a preencher** — a base da mentoria ainda não foi definida.
>
> Este documento é a fonte da verdade sobre **o que cada campo significa**. Em modelagem de crédito ele não é burocracia: metade dos erros de modelo vem de alguém assumir o sentido errado de uma coluna (`valor` é o contratado ou o saldo devedor? `data` é a da proposta ou a do desembolso?).

## Fonte

| Item | Valor |
| ---- | ----- |
| Origem da base | *a definir* |
| Formato | |
| Período coberto | |
| Granularidade (1 linha = ?) | |
| Volume (linhas × colunas) | |
| Data da extração | |
| Contém dado pessoal? | **Assumir que sim** até prova em contrário |
| Restrição de uso | |

## Camadas

O dado atravessa três camadas, todas **fora do git** (ver `.gitignore`):

| Camada | Pasta | O que é | Regra |
| ------ | ----- | ------- | ----- |
| Bruto | `dados/brutos/` | Exatamente como chegou | **Somente leitura.** Nunca editar, nunca sobrescrever |
| Intermediário | `dados/intermediarios/` | Limpo, tipado, padronizado | Gerado por script, sempre reconstruível |
| Processado | `dados/processados/` | A ABT — base analítica pronta para modelar | Gerado por script, sempre reconstruível |

> Se um arquivo em `intermediarios/` ou `processados/` não pode ser regenerado rodando os scripts, existe um passo manual escondido — e o projeto deixou de ser reprodutível.

## Campos

> Uma linha por coluna da base. Preencher conforme a base for conhecida.

| Campo | Tipo | Descrição | Domínio / valores | Missing | Observações |
| ----- | ---- | --------- | ----------------- | ------- | ----------- |
| | | | | | |

## Variável resposta (target)

| Item | Valor |
| ---- | ----- |
| Nome do campo | *a definir* |
| Definição de default | *a definir* — ver [`PRD.md`](PRD.md#4-decisões-de-modelagem) |
| Janela de performance | |
| Taxa de default na base | |

## Alertas e armadilhas conhecidas

> Registrar aqui toda esquisitice encontrada na base. Este é o campo que mais economiza tempo no futuro.

- **Data atravessando a fronteira Python → R.** `datetime64` do pandas chega no R deslocado em −3h (o `arrow` lê como UTC e converte para o fuso local): `2026-01-15` vira `2026-01-14 21:00:00`. Num contrato do dia 1º isso **muda a safra**. Data de calendário tem que ser gravada como `date32` — ver [`AGENTS.md`](../AGENTS.md#️-data-de-negócio-atravessa-a-fronteira-como-date32-nunca-como-timestamp). *Verificado neste repositório.*
- *(exemplo)* Campo `renda` tem zeros que na verdade são missing.
- *(exemplo)* Contratos renegociados aparecem duas vezes, com o mesmo ID.
