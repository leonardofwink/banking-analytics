# PRD — Banking Analytics

> **Status: rascunho.** O escopo da mentoria ainda está sendo apresentado. Este documento é o lugar onde ele será registrado à medida que for definido — não invente conteúdo aqui; preencha o que for confirmado e deixe o resto marcado como pendente.
>
> Este é o documento de **o quê** e **por quê**. O **como** (estrutura, convenções, comandos) vive em [`AGENTS.md`](../AGENTS.md) e [`README.md`](../README.md).

---

## 1. Contexto

Projeto desenvolvido no âmbito de uma mentoria em **modelagem de crédito e banking analytics**.

- **Mentoria:** ANALITICA
- **Início:** setembro de 2026
- **Registro das aulas:** [`MENTORIA.md`](MENTORIA.md)

## 2. Objetivo

> *A definir com o escopo da mentoria.*

Uma frase que responda: **que decisão de negócio este projeto melhora?** Não "construir um scorecard", e sim "decidir a quem conceder crédito com perda esperada dentro do apetite".

## 3. Escopo

### Em escopo

> *A definir.* Candidatos discutidos na abertura do projeto:
>
> - [ ] **Credit scoring / PD** — scorecard, WOE/IV, regressão logística, KS/Gini, calibração, safra e vintage
> - [ ] **Perda esperada (ECL)** — PD × EAD × LGD, provisão IFRS 9 / Res. 4.966, estágios 1/2/3
> - [ ] **Framework de risco** — matriz de riscos inerente/residual, controles e mitigadores, apetite ([`MATRIZ_RISCOS.md`](MATRIZ_RISCOS.md))
> - [ ] **Banking analytics geral** — churn, LTV, rentabilidade de carteira, comportamento transacional, segmentação

### Fora de escopo

> *A definir.* Registrar explicitamente o que **não** será feito é tão importante quanto o que será — evita o projeto crescer sem limite.

## 4. Decisões de modelagem

> Cada linha abaixo é uma decisão que muda todos os números do projeto. Enquanto estiver "a definir", nenhum resultado é comparável entre versões.

| Decisão | Valor adotado | Justificativa | Definido em |
| ------- | ------------- | ------------- | ----------- |
| **Definição de default** | *a definir* (padrão de mercado: atraso ≥ 90 dias) | | |
| **Janela de performance** | *a definir* (usual: 12 meses) | | |
| **Janela de observação** | *a definir* | | |
| **Unidade de análise** | *a definir* (cliente × contrato) | | |
| **Horizonte da PD** | *a definir* (12 meses × lifetime) | | |
| **Partição treino/teste** | *a definir* (aleatória × temporal out-of-time) | | |
| **Tratamento de rejeitados** | *a definir* (reject inference?) | | |
| **Métrica principal de aceite** | *a definir* (KS? Gini? ambos + calibração) | | |

## 5. Dados

> *A definir.* Ver [`DICIONARIO_DADOS.md`](DICIONARIO_DADOS.md) para o detalhe por campo quando a base chegar.

- **Fonte:**
- **Período coberto:**
- **Volume:**
- **Contém dado pessoal (LGPD)?** Assumir que **sim** até prova em contrário — ver regras críticas em [`AGENTS.md`](../AGENTS.md).
- **Condições de uso / confidencialidade:**

## 6. Fases

> Princípio: *"não dá pra construir o telhado sem as paredes"* — respeitar a ordem das dependências.

1. **Fase 0 — Fundações** *(em andamento)*: estrutura do repositório, glossário, convenções. Definição de escopo, base de dados e das decisões de modelagem da seção 4.
2. **Fase 1 — Dados**: ingestão, limpeza, dicionário de dados, construção da ABT (base analítica). Nenhuma modelagem antes de a ABT estar auditada.
3. **Fase 2 — Exploração**: análise univariada, IV/WOE, safras, curvas de inadimplência por MOB.
4. **Fase 3 — Modelagem**: o(s) modelo(s) dentro do escopo definido.
5. **Fase 4 — Validação**: performance out-of-time, estabilidade (PSI), calibração, documentação do modelo.
6. **Fase 5 — Decisão e comunicação**: cutoff, impacto em perda esperada e no negócio, relatório final.

## 7. Critérios de sucesso

> *A definir.* Tanto técnicos (métricas mínimas aceitáveis) quanto de aprendizado (o que a mentoria espera entregar).

## 8. Perguntas em aberto

- [ ] Qual o escopo exato do projeto da mentoria?
- [ ] A base de dados é fornecida pela mentoria, pública ou construída por nós?
- [ ] O entregável final é um modelo, um relatório, uma apresentação — ou os três?
- [ ] Há restrição de confidencialidade que impeça publicar o repositório?
