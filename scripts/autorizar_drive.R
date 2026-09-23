# autorizar_drive.R — autorização única do Drive, para rodar UMA vez
#
# Por que este arquivo existe separado do drive_mentoria.R: o `Rscript` roda em
# sessão não-interativa, e o gargle se recusa a abrir o navegador daí
# ("Can't get Google credentials"). A primeira autorização precisa de um R
# interativo. Depois dela o token fica em .secrets/gargle/ e o
# drive_mentoria.R passa a funcionar por Rscript, sem perguntar nada.
#
# COMO RODAR — no RStudio, ou num terminal com `R` (não `Rscript`):
#
#   source("scripts/autorizar_drive.R")
#
# O navegador abre. Escolha leonardofwink@gmail.com e autorize. Só isso.
#
# ⛔ Este script NÃO lê nem escreve nada no Drive. Ele só obtém o token.

if (!interactive()) {
  stop(
    "Rode isto num R INTERATIVO (RStudio ou `R` no terminal), não com Rscript.\n",
    "  source(\"scripts/autorizar_drive.R\")",
    call. = FALSE
  )
}

if (!requireNamespace("here", quietly = TRUE)) install.packages("here")
if (!requireNamespace("googledrive", quietly = TRUE)) install.packages("googledrive")

DIR_SECRETS <- file.path(here::here(), ".secrets", "gargle")
dir.create(DIR_SECRETS, recursive = TRUE, showWarnings = FALSE)

CONTA <- "leonardofwink@gmail.com"

options(gargle_oauth_cache = DIR_SECRETS, gargle_oauth_email = CONTA)

googledrive::drive_auth(email = CONTA, cache = DIR_SECRETS)

cat("\n")
cat("Autenticado como:", googledrive::drive_user()$emailAddress, "\n")
cat("Token guardado em:", DIR_SECRETS, "\n\n")
cat("Pronto. Agora o drive_mentoria.R funciona por Rscript:\n")
cat("  .\\scripts\\rscript.cmd scripts\\drive_mentoria.R --baixar\n")
