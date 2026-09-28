# AGENTS.md — diretrizes para sessões de IA

> Arquivo **canônico** de convenções deste repositório (padrão cross-tool: Claude Code, Cursor, Copilot…).
> Vale para **humanos e IA**. O `CLAUDE.md` apenas aponta para cá. **Leia antes de editar ou rodar qualquer coisa.**
> Regras críticas estão aqui no corpo; o resto é ponteiro para os docs detalhados (sem duplicar).
> **Idioma:** português (pt-BR) em docs, comentários, identificadores e commits. O domínio é em português e o código acompanha — `perda_esperada`, não `expected_loss`.
> **Princípio geral:** mudanças pequenas e validadas, código legível e sem redundância; **toda ação externa (push, merge, criar repo/PR) só com o "ok" do Leonardo**. Entre "rápido" e "bem feito", prefira **bem feito**.

## Sobre o projeto

**Banking Analytics** — projeto de **modelagem de crédito e banking analytics** desenvolvido no âmbito da mentoria **ANALITICA**.

O escopo detalhado está sendo definido conforme a mentoria avança — a fonte da verdade é o [`docs/processo/PRD.md`](docs/processo/PRD.md), e o diário das aulas é o [`docs/processo/MENTORIA.md`](docs/processo/MENTORIA.md). **Não invente escopo:** o que não estiver registrado no PRD está em aberto.

O eixo conceitual do projeto:

```
Risco inerente  ──(controles / mitigadores)──►  Risco residual  ──►  Perda esperada (PD × EAD × LGD)  ──►  ROE
```

Vocabulário completo em [`docs/GLOSSARIO.md`](docs/GLOSSARIO.md).

### Fases

> Princípio: *"não dá pra construir o telhado sem as paredes"* — respeitar a ordem das dependências. Detalhe em [`docs/processo/PRD.md`](docs/processo/PRD.md#6-fases).

**Fase 0 — Fundações** *(atual)* → 1. Dados → 2. Exploração → 3. Modelagem → 4. Validação → 5. Decisão e comunicação.

## Specs e DoD (Definition of Done)

O trabalho é dividido em **passos pequenos** ([`docs/processo/ROADMAP.md`](docs/processo/ROADMAP.md)). Cada passo é uma **spec** em `docs/specs/`, e cada spec se quebra em **subetapas** numeradas (`S01.1`, `S01.2`, …) para dar rastreio.

**Toda spec e toda subetapa tem um DoD explícito.** Sem exceção.

O DoD é a lista de condições que definem "pronto". Ele **não descreve o trabalho** — descreve como se prova que o trabalho acabou. Quatro regras:

1. **Verificável por comando**, não por opinião. "A ingestão está boa" não é DoD. "`pytest -k ingestao` passa e as três bases carregam com 10.000 / 3.000 / 5.000 linhas" é.
2. **Escrito antes de implementar.** DoD redigido depois vira descrição do que foi feito, e aí ele aprova qualquer coisa. É SDD: a spec é o contrato.
3. **Quando não dá para automatizar, diga como conferir à mão** — o comando a rodar, o número a olhar, o valor esperado. Um DoD manual é aceitável; um DoD vago não.
4. **Nada é marcado como concluído com o DoD parcialmente satisfeito.** Se um item não vale mais, a spec é atualizada e o motivo fica registrado — não se apaga o item em silêncio.

No `ROADMAP.md` o DoD de cada passo aparece como **"DoD — pronto quando"**. Nas specs, cada subetapa carrega o seu.

### Formato de um arquivo de spec

**Um arquivo por passo** (`docs/specs/S0X_NOME.md`), com as subetapas como seções `###` dentro dele — não um arquivo por subetapa. O que decide isso é que o contexto mais valioso de um passo (o "⛔ o que **não** fazemos aqui") vale para todas as subetapas: separado em arquivos, ele ficaria órfão ou repetido.

O arquivo abre com uma **tabela de status das subetapas**, para o rastreio ficar visível sem precisar ler o documento inteiro:

| Subetapa | Entrega | DoD | Status | Commit |
| -------- | ------- | --- | ------ | ------ |
| S0X.1 | o artefato que ela produz | itens cumpridos / total | ⬜ / 🔄 / ✅ | hash curto |

Regras da tabela:
- **`DoD` é uma fração** (`3/4`), não um rótulo. "Quase pronto" esconde qual item ficou faltando; `3/4` obriga a olhar qual.
- **`Commit` é preenchido quando a subetapa fecha** — é o que liga a spec ao código e permite auditar depois o que foi entregue por qual mudança.
- A última linha é o **passo inteiro**, com o DoD global.
- Abaixo da tabela, uma linha com as **verificações que fecharam o passo** (os números que foram conferidos, não a promessa de conferir).

Modelo de referência: [`docs/specs/S01_INGESTAO.md`](docs/specs/S01_INGESTAO.md).

> Por que isso importa neste projeto em particular: a maior parte dos erros de modelagem de crédito **não levanta exceção**. Vazamento de variável, imputação ajustada no conjunto errado, data deslocada por fuso — tudo isso roda, gera número e sai bonito no CSV. O DoD é o que transforma "parece certo" em "foi verificado".

## Estrutura do repositório

> **Mapa central:** o [`README.md`](README.md) é a fonte única da estrutura — árvore de pastas, como rodar, mapa dos documentos. Atualize-o sempre que um script for adicionado ou renomeado. A tabela abaixo é o resumo de convenção.

O projeto é **Python**. Ele nasceu para ser poliglota e não foi — ver § A linguagem que ficou de fora.

| O que | Onde |
| ----- | ---- |
| **Funções reutilizáveis** (puras, testáveis) | `python/banking/` — o pacote interno |
| Âncora (raiz, diretórios, log, semente) | [`python/banking/projeto.py`](python/banking/projeto.py) — importada no topo de todo script |
| Pipelines do desafio, numerados na ordem em que foram feitos | `python/etl/` (01–02) · `python/modelagem/` (03–14) · `python/relatorios/` (11, 25–26) |
| Investigações sobre a nossa política | `python/analises/` (16, 21, 24) |
| O trabalho dos colegas, rodado no nosso motor | `python/conferencias/` (15, 17, 19, 20, 22, 23) |
| Utilitários sem lugar na ordem | `python/ferramentas/` — sem número, porque não são passo de nada |
| Geradores de deck (pptxgenjs) | `apresentacoes/` — o vigente é `06_defesa.js`; `_superados/` guarda os anteriores |
| O simulador interativo | `painel/` — HTML e os dados que ele consome |
| Dados (**NUNCA versionar**) | `dados/brutos/` · `dados/intermediarios/` · `dados/processados/` |
| Saídas geradas (**NÃO versionar**) | `outputs/` |
| Documentação | `docs/` — `specs/` por passo, `processo/` para o que é nosso e não do avaliador |
| Testes | `tests/python/` (pytest) — um arquivo por módulo da biblioteca |

**A numeração é global e cronológica.** Um pipeline leva o número da ordem em que foi escrito, não da pasta onde mora: por isso `analises/` tem 16, 21 e 24 e `conferencias/` tem os outros. O número é a linha do tempo; a pasta é o propósito. Script novo pega o próximo número livre.

**Biblioteca × pipeline.** `python/banking/` tem **funções**: não rodam nada ao ser importadas, não leem nem escrevem arquivo, não imprimem. As outras pastas de `python/` têm **pipelines**: rodam, leem, escrevem e logam. Cálculo que vale testar (perda esperada, Price, ROI, faixa de score) vira função na biblioteca; a sequência que orquestra vira pipeline. É isso que permite 173 testes sem rodar nada de ponta a ponta.

**Camadas de dado:** `brutos/` é **somente leitura** — nunca editar nem sobrescrever. `intermediarios/` e `processados/` são sempre **regeneráveis pelos scripts**. Se não for possível regenerar, existe um passo manual escondido e o projeto deixou de ser reprodutível.

## A linguagem que ficou de fora

O projeto foi desenhado poliglota: Python para o ferramental de crédito
(`optbinning`, `lightgbm`, `shap`), R para exploração e comunicação
(`dplyr`, `ggplot2`, Quarto), conversando por Parquet em `dados/processados/`.

**Não foi o que aconteceu.** Em treze dias entre o lançamento e a entrega, não
houve espaço para manter duas linguagens em sincronia — e a regra que
sustentava o desenho era que a ABT tivesse **uma única construção**, porque
duas viram dois projetos que discordam. Tudo foi feito em Python; `R/` foi
removido, junto com o andaime que o sustentava: `_setup.R`, os wrappers
`rscript.*`, o `.Rproj` e o `.Renviron.example`. Repositório que carrega
estrutura para algo que não existe ensina o errado a quem chega.

Removido em `2de6840` — junto com `test_semente_bate_com_o_lado_r`, que era o único teste a depender do lado R. **Esta seção é o registro da decisão.**

### Se o R voltar, duas coisas continuam valendo

**A fronteira é o arquivo, nunca a chamada.** Nada de `reticulate` ou `rpy2`:
a troca é por Parquet, para que cada lado rode sozinho e a dependência fique
visível. Parquet e não CSV, porque CSV perde tipo — data vira texto, decimal
vira `float` com vírgula errada, categórico com nível vazio vira `NA` silencioso.

**⚠️ Data de negócio atravessa como `date32`, nunca como timestamp.** Armadilha
*verificada neste repositório*, não teórica. O `pandas` grava `datetime64` sem
fuso; o `arrow` do lado R lê como UTC e converte para o fuso local (−3h em São
Paulo):

```
Python grava:  2026-01-15  ──►  R lê:  2026-01-14 21:00:00
```

O dia **retrocede**. Num contrato originado no dia 1º, isso joga a operação
para o mês anterior e **muda a safra** — que é a unidade de análise de todo o
projeto. Não levanta exceção, não aparece no `head()` e sobrevive até alguém
estranhar a curva de inadimplência. Data de calendário é gravada como
`date32`: data pura, sem hora e sem fuso, portanto sem nada a converter.

## ⚠️ Regras críticas (não quebrar)

1. **NENHUM dado entra no git.** Base de crédito contém dado pessoal e sigilo bancário. Não versione `.csv`, `.xlsx`, `.rds`, `.parquet` — **nem amostra, nem "só umas linhas para exemplo", nem print de tabela com dado real**. O `.gitignore` bloqueia esses formatos por padrão; **nunca** use `git add -f` para furar o bloqueio. Se um script salvar em `dados/` ou `outputs/`, não dê `git add` nele.
   > **A única exceção aberta, em 25/09/2026:** `painel/dados.js` traz as 5.000
   > propostas da Base C (valor, entrada, prazo, idade, renda, bureau, ocupação)
   > porque sem ele o painel interativo não abre a partir de um clone — que é o
   > motivo de ele existir. Vale porque a Base C é **fictícia**, é material do
   > próprio desafio, o destinatário do repositório é o **professor que a
   > escreveu**, e o repositório é **privado**. A exceção é desse arquivo e de
   > mais nenhum: base real de cliente segue proibida em qualquer hipótese, e
   > `git add -f` segue proibido. Está registrada também no `.gitignore`, ao
   > lado da regra que ela excepciona.

2. **LGPD e anonimização.** CPF, nome, endereço, telefone e e-mail não devem sair da camada bruta. Se a modelagem precisar de identificador, use chave substituta (hash ou ID sequencial) gerada na ingestão. Dado pessoal nunca vai para `outputs/`, para documentação ou para o chat.
3. **Segredos fora do versionamento.** Tokens e credenciais **jamais** vão para o git — use variáveis de ambiente e leia com `os.environ`. O `.gitignore` já bloqueia `secrets/`, `token*.json` e `credentials*.json`.
4. **Termo novo da mentoria vai para o glossário.** Todo conceito apresentado nas aulas entra em [`docs/GLOSSARIO.md`](docs/GLOSSARIO.md), na seção certa. O Leonardo **não vem de banking** — não presuma vocabulário conhecido: ao usar um termo técnico pela primeira vez numa resposta ou num comentário de código, explique-o em uma linha e registre-o no glossário.
5. **Decisão de modelagem é registrada antes de ser usada.** Definição de default, janelas de observação e performance, partição treino/teste, tratamento de rejeitados: tudo em [`docs/processo/PRD.md`](docs/processo/PRD.md#decisões-de-modelagem). Sem isso, resultado de hoje não é comparável com o de amanhã.
6. **Ações externas só com confirmação.** Rodar scripts e mostrar preview do resultado pode; **push / merge / criar repo / abrir PR** exigem o "ok" do Leonardo.
7. **Conclusão negativa exige teste de premissa.** Antes de publicar que algo **"não dá para fazer"**, varra a **premissa** que sustenta a conclusão, não só as variáveis de decisão. Um resultado negativo fecha a porta para a ação e ninguém volta a abri-la — ele carrega ônus de prova **maior** que um positivo, não menor.
   > **Sintoma de violação:** a varredura tem milhares de combinações das variáveis que você escolhe e **zero** da suposição que as domina.
   >
   > Esta regra nasceu de um erro concreto, registrado em [`docs/processo/POST_MORTEM.md`](docs/processo/POST_MORTEM.md): o projeto varreu 5.600 combinações de política sobre uma elasticidade de aceite assumida, concluiu que a meta de ROI era inalcançável, e publicou isso como *"medido, não argumentado"*. A meta era alcançável — bastavam **0,7 ponto a mais na taxa**, na mesma política. Nenhum artefato interno acusou: a spec passou no DoD, os testes passaram, os números reproduziram.

## Convenções de código Python

- **Âncora de caminhos:** todo script começa com `from banking.projeto import ...`. **Nunca** use `os.chdir()` nem caminho absoluto solto — sempre as constantes `DIR_*`. Elas resolvem a partir da raiz do repositório, então o script roda igual chamado de qualquer lugar.
- **Ambiente:** `.venv` na raiz, criado por `.\scripts\setup_python.cmd`. O pacote `banking` é instalado em **modo editável** (`pip install -e .`), o que o torna importável de qualquer lugar sem gambiarra de `sys.path`.
- **Rodar: use o wrapper [`scripts/py.cmd`](scripts/py.cmd)**, que chama o interpretador do `.venv` sem exigir ativação — esquecer de ativar o venv é o erro mais comum e o sintoma é traiçoeiro (roda no Python global e usa outra versão de biblioteca, sem dizer isso):
  `.\scripts\py.cmd python\modelagem\01_scorecard.py` · `.\scripts\py.cmd -m pytest`
- **Dependências:** declare a intenção (com o porquê) em `requirements.txt`; as versões travadas ficam em `requirements.lock.txt`, **gerado** pelo setup. Nunca edite o lock à mão. Subir versão é decisão deliberada: sobe, roda os testes, confere que o número não mudou.
- **Logs:** helper `log_step()` de `banking.projeto`, com a mesma semântica de cor do lado R — a saída dos dois tem que parecer a mesma coisa.
- **Reprodutibilidade:** chame `semear()` antes de qualquer amostragem, partição ou treino.
- **Estilo:** `snake_case`, type hints nas assinaturas públicas, docstrings em pt-BR. Linha de até 100 colunas.
- **Duas exceções declaradas à regra de biblioteca pura:** [`banking/projeto.py`](python/banking/projeto.py) (a âncora — resolve caminhos e cria diretórios por definição) e `banking/dados.py` (a porta de entrada dos dados — centralizar a carga em um lugar só é justamente o objetivo do passo S01). Qualquer outro módulo de `banking/` que leia ou escreva arquivo está no lugar errado.
- **Notebooks:** úteis para explorar, **não** para entregar. O `.gitignore` bloqueia `.ipynb` de propósito: notebook guarda a saída das células junto com o código — inclusive tabelas com dado real. Conclusão que importa vira script em `python/` ou `scripts/`.

### Armadilhas específicas de modelagem de crédito

> Erros que não quebram o código — apenas produzem um número errado com cara de certo. **Desconfiar é parte do trabalho.**

- **Vazamento temporal.** Variável explicativa não pode carregar informação posterior à concessão. Um IV acima de 0,5 quase nunca é sorte: é vazamento até prova em contrário.
- **Unidades.** Na perda esperada, só a EAD é em reais; PD e LGD são frações. `0.05`, não `5`.
- **Safra é a unidade de análise.** Inadimplência se compara por **MOB** (meses desde a originação), nunca por data de calendário — safras novas sempre parecem melhores porque ainda não tiveram tempo de dar default.
- **Validação out-of-time.** Partição aleatória em dado temporal superestima a performance. Se houver tempo na base, separe por período.
- **Discriminação × calibração** são coisas diferentes: ordenar bem não é acertar o nível.
- **Métrica não é decisão.** KS alto não diz onde cortar — o cutoff sai do trade-off de ROE (ver [`docs/GLOSSARIO.md`](docs/GLOSSARIO.md#5-rentabilidade--o-outro-lado-da-balança)).

## Versionamento (commits, branches, merges)

- **Repositório:** repo **privado e dedicado** — a criar como `github.com/leonardofwink/banking-analytics`. Independente do monorepo `R_Projects`, que ignora esta pasta.
- **Identidade:** `Leonardo <leonardofwink@gmail.com>`.
- **Branch oficial:** `main`. **Uma tarefa = uma branch = um PR**, e **todo trabalho fecha com um nó de merge** (`gh pr merge --merge`) — **inclusive ajustes pequenos** — para cada tarefa aparecer no grafo. ⚠️ **Sempre `--merge`** — **nunca** `--squash` nem `--rebase`, que achatam o histórico e somem com o nó.

### Prefixos (Conventional Commits) — o mesmo prefixo serve para branch e mensagem

| Prefixo | Significa | Exemplo |
| ------- | --------- | ------- |
| `feat` | **cria** uma capacidade nova | script que calcula WOE e IV |
| `fix` | **corrige** um comportamento errado | corrige janela de performance que invadia a observação |
| `refactor` | **reestrutura** sem mudar resultado | extrai cálculo de KS para função em `banking/metricas.py` |
| `chore` | **manutenção/config** que não muda resultado | `.gitignore`; estrutura de pastas |
| `docs` | só **documentação** | registra conceito de perda esperada no glossário |

**Formato:** `tipo(escopo): descrição no imperativo` (pt-BR). Escopos usuais: `etl` · `modelagem` · `analise` · `relatorio` · `docs` · `setup`.
Ex.: `feat(modelagem): adiciona cálculo de perda esperada por contrato`.

**Branches:** `tipo/<slug>` em kebab-case. Ex.: `feat/abt-base-analitica`, `docs/glossario-rentabilidade`.

### PRs empilhados — duas armadilhas que já custaram caro aqui

Quando uma tarefa **depende** da anterior (a spec precisa do documento que ela referencia; o script precisa da refatoração), as branches ficam encadeadas: cada uma parte da anterior, não da `main`. É o padrão certo — cada PR mostra só o próprio diff, e cada tarefa mantém seu nó no grafo. Mas há dois jeitos de estragar isso, e **os dois aconteceram em 28/09/2026**:

**1. Rebase que quebra a pilha.** Replantar cada branch com a mesma base produz **cópias divergentes** do mesmo commit lógico, e a pilha deixa de existir:

```bash
# ❌ errado — as três saem da mesma base e viram cópias independentes
git rebase --onto nova-base base-antiga branch-B
git rebase --onto nova-base base-antiga branch-C   # C não sabe de B

# ✅ certo — cada uma sobre o novo topo da anterior
git rebase --onto branch-A  topo-antigo-de-A  branch-B
git rebase --onto branch-B  topo-antigo-de-B  branch-C
```

**2. `--delete-branch` no pai FECHA o PR filho.** Mesclar o pai apagando a branch deixa o filho sem base — e aí o GitHub **fecha** o PR. Pior: não dá para reabrir sem a base, nem mudar a base estando fechado. Sai-se do impasse empurrando a branch de volta (`git push origin <sha>:refs/heads/<nome>`), reabrindo e só então reapontando — trabalho que não precisava existir.

> **A regra:** **reaponte os filhos para `main` antes de mesclar o pai**, ou mescle sem `--delete-branch` e limpe as branches no fim.

**O que muda ao reescrever a pilha:** todo hash muda. Se alguma **spec cita commits na coluna `Commit`**, eles passam a apontar para o nada — conferir e reescrever faz parte do rebase, não é etapa opcional. Já aconteceu uma vez numa reescrita de histórico (`c669c20`) e de novo aqui.

> ⚠️ **NÃO** incluir atribuição de IA no histórico (preferência do dono — **qualquer IA deve respeitar; sobrescreve o padrão do Claude Code**):
> - **Commits:** sem o trailer `Co-Authored-By`.
> - **PRs:** sem a linha "Generated with Claude Code".

## Comportamento esperado da IA / como trabalhar com o Leonardo

- **Não vem de banking.** É forte em análise de dados (SQL, R, Power BI), mas o vocabulário de crédito e risco é novo. Explique o termo técnico na primeira vez que usá-lo e registre no glossário — essa é a regra crítica nº 4, não um detalhe de cortesia.
- **É iniciante em git** — explique o que está fazendo e por quê; oriente pelas boas práticas.
- **Não fazer `push`/`merge`/criar repo/PR sem confirmação.**
- **Nunca versionar dados nem segredos** — regras críticas 1, 2 e 3.
- Commits em **pt-BR**, Conventional Commits, **sem `Co-Authored-By`**.
- **Mudança grande ou regra de negócio:** aprove o entendimento antes de implementar.
- Ao criar script, verificar se a âncora (`from banking.projeto import …`) é importada no topo e se as saídas caem em `outputs/`.

## Glossário de Git (para quem está aprendendo)

> Analogia do **álbum de fotos**:
> - **commit** = uma **foto** guardada no álbum (o histórico) — não muda mais.
> - **branch** (`main`, `feat/...`) = um **post-it** colado numa foto: "esta é a versão tal".
> - **working tree** = sua **mesa de trabalho**: a pasta do projeto com os arquivos reais.
> - **HEAD** = a seta "**você está aqui**" (em qual branch/foto você está).
> - **push / pull** = enviar/baixar fotos de/para o GitHub.
> - **PR (pull request)** = o pedido, no GitHub, para juntar sua branch na `main`.
> - **merge via PR** (`gh pr merge --merge`) = junta a branch na `main` **no GitHub**, com um commit de junção — a branch **aparece no grafo**.

## Pendências (TODO)

- [ ] Criar o repositório remoto **privado** `leonardofwink/banking-analytics` e dar o primeiro push (ação externa — pede "ok").
- [ ] Preencher o escopo em [`docs/processo/PRD.md`](docs/processo/PRD.md) conforme a mentoria o apresentar.
- [ ] Registrar a **definição de default** e as janelas antes da primeira modelagem.
- [ ] Documentar a base de dados em [`docs/DICIONARIO_DADOS.md`](docs/DICIONARIO_DADOS.md) quando ela chegar.
- [ ] Preencher a [`docs/MATRIZ_RISCOS.md`](docs/MATRIZ_RISCOS.md) com os riscos reais (as linhas atuais são exemplos ilustrativos).
