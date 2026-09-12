# AGENTS.md — diretrizes para sessões de IA

> Arquivo **canônico** de convenções deste repositório (padrão cross-tool: Claude Code, Cursor, Copilot…).
> Vale para **humanos e IA**. O `CLAUDE.md` apenas aponta para cá. **Leia antes de editar ou rodar qualquer coisa.**
> Regras críticas estão aqui no corpo; o resto é ponteiro para os docs detalhados (sem duplicar).
> **Idioma:** português (pt-BR) em docs, comentários e commits; inglês só nos identificadores do código R (idiomático).
> **Princípio geral:** mudanças pequenas e validadas, código legível e sem redundância; **toda ação externa (push, merge, criar repo/PR) só com o "ok" do Leonardo**. Entre "rápido" e "bem feito", prefira **bem feito**.

## Sobre o projeto

**Banking Analytics** — projeto de **modelagem de crédito e banking analytics** desenvolvido no âmbito da mentoria **ANALITICA**.

O escopo detalhado está sendo definido conforme a mentoria avança — a fonte da verdade é o [`docs/PRD.md`](docs/PRD.md), e o diário das aulas é o [`docs/MENTORIA.md`](docs/MENTORIA.md). **Não invente escopo:** o que não estiver registrado no PRD está em aberto.

O eixo conceitual do projeto:

```
Risco inerente  ──(controles / mitigadores)──►  Risco residual  ──►  Perda esperada (PD × EAD × LGD)  ──►  ROE
```

Vocabulário completo em [`docs/GLOSSARIO.md`](docs/GLOSSARIO.md).

### Fases

> Princípio: *"não dá pra construir o telhado sem as paredes"* — respeitar a ordem das dependências. Detalhe em [`docs/PRD.md`](docs/PRD.md#6-fases).

**Fase 0 — Fundações** *(atual)* → 1. Dados → 2. Exploração → 3. Modelagem → 4. Validação → 5. Decisão e comunicação.

## Estrutura do repositório

> **Mapa central:** o [`README.md`](README.md) é a fonte única da estrutura — árvore de pastas, como rodar, mapa dos documentos. Atualize-o sempre que um script for adicionado ou renomeado. A tabela abaixo é o resumo de convenção.

| O que | Onde |
| ----- | ---- |
| **Funções reutilizáveis** (puras, testáveis) | `R/` — carregadas automaticamente pelo `_setup.R` |
| Âncora do projeto (raiz, diretórios, log, semente) | [`scripts/_setup.R`](scripts/_setup.R) — sourçada no topo de todo script |
| Ingestão, limpeza, construção da ABT | `scripts/etl/` — prefixos de ordem `00_`, `01_`, … |
| Análise exploratória, safras, univariadas | `scripts/analises/` |
| Scorecard, PD/LGD/EAD, validação | `scripts/modelagem/` |
| Saídas para apresentação | `scripts/relatorios/` |
| Dados (**NUNCA versionar**) | `dados/brutos/` · `dados/intermediarios/` · `dados/processados/` |
| Saídas geradas (**NÃO versionar**) | `outputs/` |
| Documentação | `docs/` |
| Testes das funções de `R/` | `tests/testthat/` |

**`R/` × `scripts/`:** `R/` tem funções — não roda nada ao ser carregado, não lê nem escreve arquivo, não imprime. `scripts/` tem pipelines — rodam, leem, escrevem e logam. Cálculo que vale testar (WOE, IV, KS, perda esperada) vira função em `R/`; a sequência que orquestra vira script.

**Camadas de dado:** `brutos/` é **somente leitura** — nunca editar nem sobrescrever. `intermediarios/` e `processados/` são sempre **regeneráveis pelos scripts**. Se não for possível regenerar, existe um passo manual escondido e o projeto deixou de ser reprodutível.

## ⚠️ Regras críticas (não quebrar)

1. **NENHUM dado entra no git.** Base de crédito contém dado pessoal e sigilo bancário. Não versione `.csv`, `.xlsx`, `.rds`, `.parquet` — **nem amostra, nem "só umas linhas para exemplo", nem print de tabela com dado real**. O `.gitignore` bloqueia esses formatos por padrão; **nunca** use `git add -f` para furar o bloqueio. Se um script salvar em `dados/` ou `outputs/`, não dê `git add` nele.
2. **LGPD e anonimização.** CPF, nome, endereço, telefone e e-mail não devem sair da camada bruta. Se a modelagem precisar de identificador, use chave substituta (hash ou ID sequencial) gerada na ingestão. Dado pessoal nunca vai para `outputs/`, para documentação ou para o chat.
3. **Segredos fora do versionamento.** `.Renviron`, tokens e credenciais **jamais** vão para o git. Use `.Renviron` local (modelo em `.Renviron.example`) e `Sys.getenv()`.
4. **Termo novo da mentoria vai para o glossário.** Todo conceito apresentado nas aulas entra em [`docs/GLOSSARIO.md`](docs/GLOSSARIO.md), na seção certa. O Leonardo **não vem de banking** — não presuma vocabulário conhecido: ao usar um termo técnico pela primeira vez numa resposta ou num comentário de código, explique-o em uma linha e registre-o no glossário.
5. **Decisão de modelagem é registrada antes de ser usada.** Definição de default, janelas de observação e performance, partição treino/teste, tratamento de rejeitados: tudo em [`docs/PRD.md`](docs/PRD.md#4-decisões-de-modelagem). Sem isso, resultado de hoje não é comparável com o de amanhã.
6. **Ações externas só com confirmação.** Rodar scripts e mostrar preview do resultado pode; **push / merge / criar repo / abrir PR** exigem o "ok" do Leonardo.

## Convenções de código R

- **Âncora de caminhos:** todo script começa com `source(here::here("scripts", "_setup.R"))`. **Nunca** use `setwd()` avulso nem caminhos absolutos soltos — sempre os objetos `DIR_*` definidos na âncora.
- **Pacotes:** `pacman::p_load(...)` no `_setup.R` para os transversais; no topo do script para os específicos daquela tarefa.
- **Logs informativos:** helper `log_step()` do `_setup.R`, no padrão `[HH:MM:SS] mensagem`. Semântica de cor: **ciano** = progresso · **verde** = sucesso · **amarelo** = aviso · **vermelho** = erro. Sempre `cli::col_*`, nunca cores ANSI cruas. **Nunca erro mudo** — diga o quê, onde e com qual dado; `tryCatch` com mensagem de contexto.
- **Reprodutibilidade:** semente fixa (`SEMENTE` no `_setup.R`) antes de qualquer amostragem, partição ou bootstrap. O script deve rodar do zero, sem passo manual escondido.
- **Docstrings** roxygen (`#'`) nas funções de `R/`: o que faz, `@param`, `@return`. Em funções de crédito, documentar também **a convenção de unidade** (PD e LGD em fração 0–1, não em 0–100).
- **Nomes:** funções e objetos em `snake_case`. Identificadores em inglês (`calculate_woe`, `expected_loss`), comentários e mensagens em pt-BR.
- **Chamar o R: use o wrapper [`scripts/rscript.cmd`](scripts/rscript.cmd).** O `Rscript` não fica no PATH e o caminho da instalação muda de máquina. O wrapper resolve o interpretador local (`$env:RSCRIPT` → PATH → registro → pastas padrão; entre versões, vence a mais recente):
  `.\scripts\rscript.cmd scripts\etl\01_ingestao.R`
  Sem argumentos, imprime o caminho resolvido. **Nunca fixe caminho absoluto de R** em script ou documentação. Requer **R ≥ 4.5**.

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
| `refactor` | **reestrutura** sem mudar resultado | extrai cálculo de KS para função em `R/` |
| `chore` | **manutenção/config** que não muda resultado | `.gitignore`; estrutura de pastas |
| `docs` | só **documentação** | registra conceito de perda esperada no glossário |

**Formato:** `tipo(escopo): descrição no imperativo` (pt-BR). Escopos usuais: `etl` · `modelagem` · `analise` · `relatorio` · `docs` · `setup`.
Ex.: `feat(modelagem): adiciona cálculo de perda esperada por contrato`.

**Branches:** `tipo/<slug>` em kebab-case. Ex.: `feat/abt-base-analitica`, `docs/glossario-rentabilidade`.

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
- Ao criar script, verificar se `_setup.R` é sourçado no topo e se as saídas caem em `outputs/`.

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
- [ ] Preencher o escopo em [`docs/PRD.md`](docs/PRD.md) conforme a mentoria o apresentar.
- [ ] Registrar a **definição de default** e as janelas antes da primeira modelagem.
- [ ] Documentar a base de dados em [`docs/DICIONARIO_DADOS.md`](docs/DICIONARIO_DADOS.md) quando ela chegar.
- [ ] Preencher a [`docs/MATRIZ_RISCOS.md`](docs/MATRIZ_RISCOS.md) com os riscos reais (as linhas atuais são exemplos ilustrativos).
