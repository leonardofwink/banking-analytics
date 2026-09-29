# Banking Analytics — Desafio AutoCred

**Grupo 3** · Mentoria ANALITICA · Deni Alan, Leonardo Wink, Marcelo Félix e Renato

> ## Recomendamos aprovar 59,5% das propostas, com preço de 1,63% a 2,29% ao mês conforme o risco.
>
> Isso rende **ROI de 11,33% ao ano** e cumpre os **quatro guard-rails nos três
> cenários** de aceite. Não alcança a meta de 15% — e a parte mais útil deste
> repositório é a medição de **por que ninguém alcança** sem furar o piso de
> volume.

## ▶ Comece pelo painel

### [⤓ Baixar o simulador](painel/AutoCred%20-%20Painel%20da%20Politica%20-%20Grupo%203.html)

Um arquivo só, com tudo dentro. **Dois cliques:**

1. Abra o link acima e clique em **`Download raw file`** (o ícone ⤓ no canto
   superior direito da página do GitHub).
2. Abra o arquivo baixado no navegador.

Pronto — nada a instalar, sem internet, sem clonar o repositório. Os dados vão
embutidos no próprio arquivo.

Mexa nas seis alavancas — corte, taxa base, prêmio de risco, prazo, entrada e
escalonamento da entrada por faixa — e veja o ROI e os quatro limites
responderem na hora. A fronteira mostra **todas as políticas que testamos**,
com a nossa marcada e o ótimo viável destacado; a base C aparece proposta a
proposta, com a PD re-escorada pelo LTV e prazo que a política oferta.

> ⚠️ Não baixe o `painel/index.html` sozinho — ele lê o `dados.js` da pasta ao
> lado e abriria em branco. Esse par existe para quem **clona** o repositório;
> para baixar um arquivo só, use o link acima.

## Os documentos que respondem à banca

| | |
| - | - |
| 💰 **[Entregável 2 — a política](docs/ENTREGAVEL_2_POLITICA.md)** | Por que aprovamos quem aprovamos, por que cobramos o que cobramos, e por que isso dá o retorno que dá |
| 🧮 **[Entregável 1 — o modelo](docs/ENTREGAVEL_1_MODELO.md)** | PD 90/12: variáveis, validação out-of-time, calibração e o que ficou de fora por vazamento |
| 📊 **[O painel](docs/PAINEL.md)** | Como o simulador funciona, e por que ele é fiel ao motor que produziu os números |

---

## Mapa da documentação

| Documento | Para quê |
| --------- | -------- |
| 🎯 [`docs/DESAFIO.md`](docs/DESAFIO.md) | **O briefing da AutoCred** — requisitos, bases, guard-rails, rubrica e formato de submissão. Fonte única do que foi pedido |
| 🗺️ [`docs/processo/ROADMAP.md`](docs/processo/ROADMAP.md) | **O objetivo quebrado em 11 passos** — o que fazer, por quê, como e quando está pronto |
| 🧮 [`docs/ENTREGAVEL_1_MODELO.md`](docs/ENTREGAVEL_1_MODELO.md) | Decisões do entregável 1 — modelo de PD (40 pts) |
| 💰 [`docs/ENTREGAVEL_2_POLITICA.md`](docs/ENTREGAVEL_2_POLITICA.md) | Decisões do entregável 2 — política e precificação (40 pts) |
| 📋 [`docs/processo/PRD.md`](docs/processo/PRD.md) | Plano de execução: SDD, divisão do grupo, cronograma até 25/09, riscos |
| 📖 [`docs/GLOSSARIO.md`](docs/GLOSSARIO.md) | **O vocabulário do projeto.** Risco inerente/residual, mitigação, perda esperada, scorecard, regulação, rentabilidade |
| 🎓 [`docs/processo/MENTORIA.md`](docs/processo/MENTORIA.md) | Diário de bordo das aulas: conceito → implicação → pendência |
| ⚠️ [`docs/MATRIZ_RISCOS.md`](docs/MATRIZ_RISCOS.md) | Riscos do negócio, do modelo e do projeto: inerente → controles → residual |
| 🗂️ [`docs/DICIONARIO_DADOS.md`](docs/DICIONARIO_DADOS.md) | O que cada campo da base significa, e as armadilhas encontradas nela |
| 📊 [`docs/PAINEL.md`](docs/PAINEL.md) | O simulador interativo: o que ele mostra e por que é fiel ao motor |
| 🔍 [`docs/COMPARACAO_COLEGAS.md`](docs/COMPARACAO_COLEGAS.md) | Os quatro trabalhos do grupo rodados **no mesmo motor** — e o que cada um tem que os outros não |
| 🤖 [`AGENTS.md`](AGENTS.md) | Convenções do repositório: código, git, regras críticas. **Vale para humanos e IA** |

## Estrutura

```
.
├── python/
│   ├── banking/            A biblioteca: funções puras e testadas
│   │   ├── projeto.py      Âncora: raiz, diretórios, log, semente
│   │   ├── dados.py        Ingestão, colunas proibidas, preparação da base C
│   │   ├── modelo.py       Pipeline de PD, preditoras, treino
│   │   ├── perda.py        EAD e LGD — as tabelas do enunciado
│   │   ├── price.py        Tabela Price: parcela e saldo devedor
│   │   ├── politica.py     Geração da tabela de política
│   │   ├── roi.py          O motor: oferta → aceite → ROI e guard-rails
│   │   └── score.py        PD → faixa de 1 a 10
│   ├── etl/                01–02  ingestão e parâmetros de EAD/LGD
│   ├── modelagem/          03–14  do EDA à fronteira ROI × volume
│   ├── analises/           16·21·24  investigações sobre a nossa política
│   ├── conferencias/       15·17·19·20·22·23  o trabalho dos colegas, no nosso motor
│   ├── relatorios/         11·25·26  documento de política e dados do painel
│   └── ferramentas/        utilitários sem ordem — markdown → PDF
├── scripts/                Wrappers de execução (py.cmd, setup_python.cmd)
├── apresentacoes/          🎞️ Geradores dos decks (pptxgenjs)
│   ├── 06_defesa.js        O deck da defesa — este é o vigente
│   └── _superados/         Decks de trabalho, mantidos por histórico
├── painel/                 📊 O simulador: HTML + os dados que ele consome
├── docs/                   Documentação (ver mapa acima)
│   ├── specs/              Uma spec por passo, com DoD
│   └── processo/           PRD, roadmap, diário e débito técnico
├── tests/python/           pytest — um arquivo por módulo da biblioteca
├── dados/                  ⛔ NÃO versionado — brutos, intermediários, processados
└── outputs/                ⛔ NÃO versionado — figuras, tabelas, entregáveis gerados
```

**A numeração dos pipelines é global e cronológica** (01→26): ela conta a ordem
em que o trabalho foi feito, não a pasta onde mora. Por isso `analises/` tem
16, 21 e 24, e `conferencias/` tem os demais — o número é a linha do tempo, a
pasta é o propósito.

**A distinção que sustenta tudo:** `python/banking/` tem **funções** — puras, testáveis, sem efeito colateral ao ser importadas. As outras pastas de `python/` têm **pipelines** — rodam, leem e escrevem arquivos, imprimem log. Cálculo que vale testar vira função na biblioteca; a sequência que orquestra vira pipeline. É o que permite que os 185 testes cubram o que importa sem precisar rodar nada de ponta a ponta.

## Sobre o repositório

Organizado para reprodutibilidade: o git versiona **apenas código e documentação** — nenhuma base de dados entra no histórico, e qualquer pessoa reconstrói os dados rodando os scripts. (A única exceção é `painel/dados.js`, para o painel abrir de um clone; o porquê está no [`.gitignore`](.gitignore) e no [`AGENTS.md`](AGENTS.md).)

**Tudo em Python.** O projeto foi montado para ser poliglota — R para exploração e comunicação, Python para o ferramental de crédito — mas **o R acabou não sendo usado**: o prazo de treze dias não deixou espaço para manter duas linguagens em sincronia, e a regra do projeto é que a ABT tenha uma única construção. O andaime de R foi removido do repositório; o registro da decisão está no [`AGENTS.md`](AGENTS.md#a-linguagem-que-ficou-de-fora).

> 📖 **Vocabulário:** o [glossário](docs/GLOSSARIO.md) cobre risco inerente, risco residual, mitigação, PD/EAD/LGD, ROE e os termos que aparecem em todo o resto.

---

## Como rodar

**Pré-requisito:** Python ≥ 3.12. Uma vez por máquina (e sempre que o `requirements.txt` mudar):

```powershell
.\scripts\setup_python.cmd     # cria o .venv, instala tudo, trava as versões
```

Depois, rode sem precisar ativar o ambiente — o wrapper usa o interpretador do `.venv`:

```powershell
.\scripts\py.cmd                                  # qual interpretador está em uso
.\scripts\py.cmd python\modelagem\05_desafiantes.py
.\scripts\py.cmd -m pytest                        # os 185 testes
```

Todo script começa importando a âncora, que resolve os caminhos a partir da raiz:

```python
from banking.projeto import DIR_PROCESSADOS, SEMENTE, log_step, semear
```

As versões instaladas ficam travadas em `requirements.lock.txt` (gerado — não editar à mão). É ele que garante que outra máquina chegue no mesmo número.

---

## Reproduzir os nossos números

O que defendemos: **ROI de 11,33%** ao ano no cenário central, **R$ 66,7 mi** de
volume originado, **6,33%** de inadimplência e **59,5%** de aprovação — com os
quatro guard-rails cumpridos **nos três cenários** de aceite.

O repositório não carrega dado nenhum. Para chegar nesses números do zero:

```powershell
# 1. as bases do desafio em dados/brutos/professor/bases/
#    base_A_...csv · base_B_...csv · base_C_...csv
#    AutoCred_parametros_ead_lgd.xlsx · AutoCred_Dicionario_de_Dados.xlsx

.\scripts\setup_python.cmd                                   # 2. o ambiente (uma vez)

.\scripts\py.cmd python\etl\01_ingestao.py                   # 3. ingestão e ABT
.\scripts\py.cmd python\etl\02_parametros_ead_lgd.py         #    tabelas de EAD e LGD
.\scripts\py.cmd python\modelagem\05_desafiantes.py          # 4. o modelo de PD
.\scripts\py.cmd python\modelagem\06_submissao_modelo.py     #    escoragem da base B
.\scripts\py.cmd python\modelagem\09_buscar_politica.py      # 5. a política
.\scripts\py.cmd python\modelagem\10_submissao_politica.py   #    decisões da base C

.\scripts\py.cmd -m pytest                                   # 6. 185 testes
```

O passo 5 é o que importa para a defesa: ele varre o espaço de políticas e
mostra por que a escolhida foi a escolhida. O
[`12_fronteira_roi_volume.py`](python/modelagem/12_fronteira_roi_volume.py)
estende a varredura para 5.600 políticas e produz a medição de que **a meta de
15% de ROI e o piso de volume não coexistem** sob as nossas premissas de aceite.

### Refazer a varredura do painel

O painel **não recalcula** o ROI no navegador: consulta a varredura das 5.600
políticas — a mesma do S12 — feita no mesmo motor que produziu os números acima. É o que o torna
fiel — e é por isso que abrir `painel/index.html` basta, sem ambiente nem bases.
Para refazê-la:

```powershell
.\scripts\py.cmd python\relatorios\25_dados_do_painel.py     # ~17 min: 5.600 políticas
.\scripts\py.cmd python\relatorios\26_tabelas_do_painel.py   # tabelas de EAD/LGD + dados.js
```

Ao terminar, o primeiro passo confere sozinho que o padrão da grade devolve os
11,33% de ROI e os R$ 45,1 mi de volume pessimista deste README. Se divergir, a
grade e a política saíram de sincronia — e o painel não deve ser publicado até
que batam. Ver [`docs/PAINEL.md`](docs/PAINEL.md).

---

## Estado atual

**Desafio AutoCred, entregue.** Os dois entregáveis fechados, 185 testes passando.

| | |
| - | - |
| **Modelo de PD** | XGBoost, AuROC de **0,7234** na validação out-of-time. Erro de calibração de 0,03 pp |
| **Política** | corte no score 5 · taxa de **1,63% a 2,29%** a.m. por faixa · 48 meses · entrada mínima de 10% |
| **Resultado** | ROI **11,33%** · volume **R$ 66,7 mi** · inadimplência **6,33%** · aprovação **59,5%** |
| **Guard-rails** | os quatro cumpridos, nos três cenários de aceite |

**Não batemos a meta de 15%, e medimos por quê.** Três caminhos independentes
convergem num teto de ~11,5% para as políticas viáveis. O argumento que fecha a
questão é aritmético: a perda é 8,8% dos juros, então **mesmo com inadimplência
zero o ROI seria 12,42%** — nenhuma alavanca de risco alcança a meta. Só preço
alcança, e preço derruba o volume abaixo do piso de R$ 40 mi. A medição está em
[`docs/ENTREGAVEL_2_POLITICA.md`](docs/ENTREGAVEL_2_POLITICA.md) e no painel.

**Grupo 3** — Deni Alan (modelagem) · Leonardo Wink (política e precificação) ·
Marcelo Félix e Renato (negócio e defesa).
