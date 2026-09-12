# Banking Analytics

Projeto de **modelagem de crédito e banking analytics**, desenvolvido no âmbito da mentoria **ANALITICA**.

Repositório em **R**, organizado para reprodutibilidade: o git versiona **apenas código e documentação** — nenhuma base de dados entra no histórico, e qualquer pessoa reconstrói os dados rodando os scripts.

> 📖 **Começando agora? Leia o [glossário](docs/GLOSSARIO.md) primeiro.** Ele é a peça central do projeto: risco inerente, risco residual, mitigação, PD/EAD/LGD, ROE e o vocabulário de crédito que aparece em todo o resto.

---

## Mapa da documentação

| Documento | Para quê |
| --------- | -------- |
| 📖 [`docs/GLOSSARIO.md`](docs/GLOSSARIO.md) | **O vocabulário do projeto.** Risco inerente/residual, mitigação, perda esperada, scorecard, regulação, rentabilidade |
| 🎓 [`docs/MENTORIA.md`](docs/MENTORIA.md) | Diário de bordo das aulas: conceito → implicação → pendência |
| 📋 [`docs/PRD.md`](docs/PRD.md) | Objetivo, escopo, fases e **as decisões de modelagem** (definição de default, janelas, métricas) |
| ⚠️ [`docs/MATRIZ_RISCOS.md`](docs/MATRIZ_RISCOS.md) | Riscos do negócio, do modelo e do projeto: inerente → controles → residual |
| 🗂️ [`docs/DICIONARIO_DADOS.md`](docs/DICIONARIO_DADOS.md) | O que cada campo da base significa, e as armadilhas encontradas nela |
| 🤖 [`AGENTS.md`](AGENTS.md) | Convenções do repositório: código, git, regras críticas. **Vale para humanos e IA** |

## Estrutura

```
.
├── R/                      Funções reutilizáveis (biblioteca interna, carregada pelo _setup.R)
├── scripts/                Pipelines executáveis
│   ├── _setup.R            Âncora: raiz, diretórios, pacotes, log, semente
│   ├── rscript.cmd         Wrapper que acha o Rscript desta máquina
│   ├── etl/                Ingestão, limpeza, construção da ABT
│   ├── analises/           Exploratória, safras, univariadas
│   ├── modelagem/          Scorecard, PD/LGD/EAD, validação
│   └── relatorios/         Saídas para apresentação
├── dados/                  ⛔ NÃO versionado
│   ├── brutos/             Como chegou — somente leitura
│   ├── intermediarios/     Limpo e padronizado
│   └── processados/        ABT — base analítica pronta
├── outputs/                ⛔ NÃO versionado (figuras, tabelas, relatórios)
├── docs/                   Documentação
└── tests/                  Testes das funções de R/
```

**A distinção que importa:** `R/` tem **funções** (puras, testáveis, sem efeito colateral ao carregar); `scripts/` tem **pipelines** (rodam, leem e escrevem arquivos, imprimem log). Cálculo que vale a pena testar vira função em `R/`; a sequência que orquestra vira script em `scripts/`.

## Como rodar

**Pré-requisito:** R ≥ 4.5. Não precisa estar no PATH — o wrapper descobre a instalação.

```powershell
# 1. Conferir qual R o projeto vai usar
.\scripts\rscript.cmd

# 2. Rodar um script qualquer
.\scripts\rscript.cmd scripts\etl\01_ingestao.R
```

Todo script começa sourçando a âncora, que resolve os caminhos a partir da raiz do repositório:

```r
source(here::here("scripts", "_setup.R"))
```

Os pacotes são instalados sob demanda por `pacman::p_load()` na primeira execução.

### Variáveis de ambiente

Credenciais e caminhos de máquina ficam em um `.Renviron` local, **fora do git**:

```powershell
Copy-Item .Renviron.example .Renviron   # depois preencha os valores
```

---

## Estado atual

**Fase 0 — Fundações.** Estrutura do repositório criada; escopo da mentoria em definição. As pendências abertas estão em [`docs/PRD.md`](docs/PRD.md#8-perguntas-em-aberto) e [`docs/MENTORIA.md`](docs/MENTORIA.md).
