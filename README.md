# Banking Analytics

Projeto de **modelagem de crédito e banking analytics**, desenvolvido no âmbito da mentoria **ANALITICA**.

Repositório **poliglota (R + Python)**, organizado para reprodutibilidade: o git versiona **apenas código e documentação** — nenhuma base de dados entra no histórico, e qualquer pessoa reconstrói os dados rodando os scripts.

**Python modela · R explora e comunica.** Python entra pelo ferramental de crédito que não tem equivalente maduro em R (`optbinning` para binning/WOE/scorecard, `lightgbm`, `shap`); R continua melhor para investigar e apresentar (`dplyr`, `ggplot2`, Quarto). As duas linguagens **não se importam** — conversam por arquivo Parquet em `dados/`. A regra completa está em [`AGENTS.md`](AGENTS.md#a-fronteira-entre-as-duas-linguagens).

> 📖 **Começando agora? Leia o [glossário](docs/GLOSSARIO.md) primeiro.** Ele é a peça central do projeto: risco inerente, risco residual, mitigação, PD/EAD/LGD, ROE e o vocabulário de crédito que aparece em todo o resto.

---

## Mapa da documentação

| Documento | Para quê |
| --------- | -------- |
| 🎯 [`docs/DESAFIO.md`](docs/DESAFIO.md) | **O briefing da AutoCred** — requisitos, bases, guard-rails, rubrica e formato de submissão. Fonte única do que foi pedido |
| 🗺️ [`docs/ROADMAP.md`](docs/ROADMAP.md) | **O objetivo quebrado em 11 passos** — o que fazer, por quê, como e quando está pronto |
| 🧮 [`docs/ENTREGAVEL_1_MODELO.md`](docs/ENTREGAVEL_1_MODELO.md) | Decisões do entregável 1 — modelo de PD (40 pts) |
| 💰 [`docs/ENTREGAVEL_2_POLITICA.md`](docs/ENTREGAVEL_2_POLITICA.md) | Decisões do entregável 2 — política e precificação (40 pts) |
| 📋 [`docs/PRD.md`](docs/PRD.md) | Plano de execução: SDD, divisão do grupo, cronograma até 25/09, riscos |
| 📖 [`docs/GLOSSARIO.md`](docs/GLOSSARIO.md) | **O vocabulário do projeto.** Risco inerente/residual, mitigação, perda esperada, scorecard, regulação, rentabilidade |
| 🎓 [`docs/MENTORIA.md`](docs/MENTORIA.md) | Diário de bordo das aulas: conceito → implicação → pendência |
| ⚠️ [`docs/MATRIZ_RISCOS.md`](docs/MATRIZ_RISCOS.md) | Riscos do negócio, do modelo e do projeto: inerente → controles → residual |
| 🗂️ [`docs/DICIONARIO_DADOS.md`](docs/DICIONARIO_DADOS.md) | O que cada campo da base significa, e as armadilhas encontradas nela |
| 🤖 [`AGENTS.md`](AGENTS.md) | Convenções do repositório: código, git, regras críticas. **Vale para humanos e IA** |

## Estrutura

```
.
├── R/                      🇷 Funções R reutilizáveis (carregadas pelo _setup.R)
├── scripts/                🇷 Pipelines R + wrappers de execução
│   ├── _setup.R            Âncora R: raiz, diretórios, pacotes, log, semente
│   ├── rscript.cmd         Acha o Rscript desta máquina
│   ├── setup_python.cmd    Cria o .venv e instala as dependências Python
│   ├── py.cmd              Roda Python no .venv, sem precisar ativá-lo
│   ├── etl/                Ingestão e limpeza
│   ├── analises/           Exploratória, safras, univariadas
│   ├── modelagem/          Modelagem em R (quando fizer sentido)
│   └── relatorios/         Saídas para apresentação
├── python/                 🐍 Lado Python
│   ├── banking/            Biblioteca interna (pacote importável)
│   │   └── projeto.py      Âncora Python: raiz, diretórios, log, semente
│   ├── etl/                Ingestão e construção da ABT
│   ├── modelagem/          Binning, WOE/IV, scorecard, challenger, SHAP
│   └── relatorios/         Saídas geradas em Python
├── dados/                  ⛔ NÃO versionado
│   ├── brutos/             Como chegou — somente leitura
│   ├── intermediarios/     Limpo e padronizado
│   └── processados/        ABT — base analítica pronta (fronteira Python ↔ R)
├── outputs/                ⛔ NÃO versionado (figuras, tabelas, relatórios)
├── docs/                   Documentação
└── tests/                  testthat/ (R) · python/ (pytest)
```

**A distinção que importa, nas duas linguagens:** `R/` e `python/banking/` têm **funções** (puras, testáveis, sem efeito colateral ao carregar); `scripts/` e `python/{etl,modelagem,relatorios}/` têm **pipelines** (rodam, leem e escrevem arquivos, imprimem log). Cálculo que vale testar vira função na biblioteca; a sequência que orquestra vira pipeline.

## Como rodar

### R

**Pré-requisito:** R ≥ 4.5. Não precisa estar no PATH — o wrapper descobre a instalação.

```powershell
.\scripts\rscript.cmd                          # qual R o projeto vai usar
.\scripts\rscript.cmd scripts\etl\01_ingestao.R
```

Todo script começa sourçando a âncora, que resolve os caminhos a partir da raiz do repositório:

```r
source(here::here("scripts", "_setup.R"))
```

Os pacotes são instalados sob demanda por `pacman::p_load()` na primeira execução.

### Python

**Pré-requisito:** Python ≥ 3.12. Uma vez por máquina (e sempre que o `requirements.txt` mudar):

```powershell
.\scripts\setup_python.cmd     # cria o .venv, instala tudo, trava as versões
```

Depois, rode sem precisar ativar o ambiente — o wrapper usa o interpretador do `.venv`:

```powershell
.\scripts\py.cmd                                  # qual interpretador está em uso
.\scripts\py.cmd python\modelagem\01_scorecard.py
.\scripts\py.cmd -m pytest                        # testes
```

Todo script Python começa importando a âncora:

```python
from banking.projeto import DIR_PROCESSADOS, SEMENTE, log_step, semear
```

As versões instaladas ficam travadas em `requirements.lock.txt` (gerado — não editar à mão). É ele que garante que outra máquina chegue no mesmo número.

### Variáveis de ambiente

Credenciais e caminhos de máquina ficam em um `.Renviron` local, **fora do git**:

```powershell
Copy-Item .Renviron.example .Renviron   # depois preencha os valores
```

---

## Estado atual

**Desafio AutoCred, fase 0.** Material do professor recebido e analisado; specs abertas; nenhum código de modelagem escrito ainda. Próximo passo: **S01 — ingestão** ([`docs/ROADMAP.md`](docs/ROADMAP.md)). Prazo: **25/09**.
