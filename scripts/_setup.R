# _setup.R — âncora do projeto Banking Analytics
#
# Sourçar no TOPO de todo script:
#   source(here::here("scripts", "_setup.R"))
#
# Define a raiz do projeto, os diretórios padrão, carrega as funções de R/ e
# expõe os helpers compartilhados (log e semente). Convenções: ver AGENTS.md.
# Nunca use setwd() avulso nem caminhos absolutos soltos — sempre os DIR_*.

# --- Pacotes base do projeto -------------------------------------------------
if (!requireNamespace("pacman", quietly = TRUE)) install.packages("pacman")
pacman::p_load(here, cli, fs, dplyr, tidyr, readr, stringr, lubridate, janitor)

# --- Raiz do projeto ---------------------------------------------------------
# `here` ancora na raiz do repositório (encontra o .git); robusto a partir de
# qualquer subpasta.
PROJ_ROOT <- here::here()

# --- Diretórios padrão -------------------------------------------------------
DIR_SCRIPTS     <- fs::path(PROJ_ROOT, "scripts")
DIR_ETL         <- fs::path(DIR_SCRIPTS, "etl")
DIR_ANALISES    <- fs::path(DIR_SCRIPTS, "analises")
DIR_MODELAGEM   <- fs::path(DIR_SCRIPTS, "modelagem")
DIR_RELATORIOS  <- fs::path(DIR_SCRIPTS, "relatorios")

DIR_R           <- fs::path(PROJ_ROOT, "R")        # funções reutilizáveis

# Camadas de dado — NENHUMA é versionada (ver .gitignore).
DIR_DADOS       <- fs::path(PROJ_ROOT, "dados")
DIR_BRUTOS      <- fs::path(DIR_DADOS, "brutos")          # como chegou, intocado
DIR_INTERMED    <- fs::path(DIR_DADOS, "intermediarios")  # limpo/padronizado
DIR_PROCESSADOS <- fs::path(DIR_DADOS, "processados")     # base analítica (ABT)

DIR_OUTPUTS     <- fs::path(PROJ_ROOT, "outputs")  # saídas geradas — NÃO versionar
DIR_FIGURAS     <- fs::path(DIR_OUTPUTS, "figuras")
DIR_TABELAS     <- fs::path(DIR_OUTPUTS, "tabelas")
DIR_RELATORIOS  <- fs::path(DIR_OUTPUTS, "relatorios")
DIR_DOCS        <- fs::path(PROJ_ROOT, "docs")

# Cria os diretórios de dados/saída se ainda não existirem (idempotente).
# Eles não são versionados (ver .gitignore), então num clone novo não existem —
# é aqui que a árvore de pastas do projeto é reconstruída.
for (.d in c(DIR_BRUTOS, DIR_INTERMED, DIR_PROCESSADOS,
             DIR_FIGURAS, DIR_TABELAS, DIR_RELATORIOS)) {
  if (!fs::dir_exists(.d)) fs::dir_create(.d, recurse = TRUE)
}

# --- Reprodutibilidade -------------------------------------------------------
# Modelagem de crédito envolve amostragem (treino/teste, bootstrap, validação
# cruzada). Semente fixa no setup = todo mundo que rodar o script chega no
# mesmo número. Se um script precisar de outra semente, que a declare explícito.
SEMENTE <- 42
set.seed(SEMENTE)

# --- Helper de log -----------------------------------------------------------
#' Loga uma etapa com timestamp e semântica de cor.
#'
#' @param msg   Mensagem a exibir.
#' @param nivel Um de "info" (ciano, progresso), "ok" (verde, sucesso),
#'   "aviso" (amarelo) ou "erro" (vermelho). Padrão "info".
#' @return `invisible(NULL)`. Efeito colateral: imprime no console.
log_step <- function(msg, nivel = c("info", "ok", "aviso", "erro")) {
  nivel <- match.arg(nivel)
  cor <- switch(nivel,
    info  = cli::col_cyan,
    ok    = cli::col_green,
    aviso = cli::col_yellow,
    erro  = cli::col_red
  )
  ts <- format(Sys.time(), "%H:%M:%S")
  cat(cor(sprintf("[%s] %s\n", ts, msg)))
  invisible(NULL)
}

# --- Carrega as funções do projeto ------------------------------------------
# Tudo em R/ é biblioteca interna: funções puras, testáveis, sem efeito
# colateral no load. Scripts de pipeline ficam em scripts/, nunca aqui.
.arquivos_r <- fs::dir_ls(DIR_R, glob = "*.R", fail = FALSE)
for (.f in .arquivos_r) source(.f)

if (length(.arquivos_r) > 0) {
  log_step(sprintf("Setup carregado. Raiz: %s | %d arquivo(s) de R/",
                   PROJ_ROOT, length(.arquivos_r)), "ok")
} else {
  log_step(sprintf("Setup carregado. Raiz: %s", PROJ_ROOT), "ok")
}
