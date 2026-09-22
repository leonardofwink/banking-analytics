# drive_mentoria.R — acesso SOMENTE LEITURA à pasta compartilhada do grupo
#
# A pasta da mentoria é compartilhada entre os três integrantes, cada um com a
# sua subpasta. Este script autentica como leonardofwink@gmail.com e lista o
# que existe lá, para acompanharmos o andamento dos colegas.
#
# ⛔ REGRA INEGOCIÁVEL: este script NUNCA escreve no Drive.
#    Nada de drive_upload(), drive_rm(), drive_mv(), drive_mkdir(), drive_cp(),
#    drive_trash(), drive_update() ou sheet_write(). As pastas dos colegas são
#    de leitura e ponto. Se algum dia for preciso subir nosso entregável, isso
#    será feito em um script separado, explícito, e com o "ok" do Leonardo.
#
# Rodar:
#   .\scripts\rscript.cmd scripts\drive_mentoria.R              # lista a árvore
#   .\scripts\rscript.cmd scripts\drive_mentoria.R --baixar     # + baixa para dados/brutos/drive/
#
# Na PRIMEIRA execução o navegador abre para você autorizar a conta. O token
# fica em .secrets/gargle/ (fora do git) e as próximas execuções não perguntam.

source(here::here("scripts", "_setup.R"))

pacman::p_load(googledrive, googlesheets4, dplyr, purrr, fs, cli)

# --- Autenticação ------------------------------------------------------------
# O token é credencial: cache dentro do projeto, em .secrets/ (já no .gitignore).
# Guardar no cache padrão do gargle (~/.cache/gargle) também funciona, mas
# deixar no projeto torna óbvio o que apagar se a conta mudar.
DIR_SECRETS <- fs::path(PROJ_ROOT, ".secrets", "gargle")
fs::dir_create(DIR_SECRETS, recurse = TRUE)

CONTA <- "leonardofwink@gmail.com"

options(
  gargle_oauth_cache = DIR_SECRETS,
  gargle_oauth_email = CONTA
)

#' Autentica no Drive e no Sheets com a mesma conta e o mesmo token.
#'
#' `gs4_auth()` recebe o token já obtido pelo `drive_auth()` — sem isso o
#' googlesheets4 abriria um segundo fluxo de autorização para a mesma conta.
#'
#' @return `invisible(NULL)`.
autenticar <- function() {
  log_step(sprintf("Autenticando como %s", CONTA))
  googledrive::drive_auth(email = CONTA, cache = DIR_SECRETS)
  googlesheets4::gs4_auth(token = googledrive::drive_token())
  log_step(sprintf("Autenticado: %s", googledrive::drive_user()$emailAddress), "ok")
  invisible(NULL)
}

# --- A pasta do grupo --------------------------------------------------------
URL_PASTA <- "https://drive.google.com/drive/folders/1sp5l1YqVmDGEBYhkCtv1nLLcjNXZZIm6"

# Diretório local para o que for baixado. Fica em dados/brutos/ — não versionado.
DIR_DRIVE <- fs::path(DIR_BRUTOS, "drive")

#' Lista o conteúdo de uma pasta do Drive, recursivamente, imprimindo a árvore.
#'
#' @param id      Id (ou `dribble`) da pasta.
#' @param nivel   Profundidade atual, usada só para a indentação.
#' @param prefixo Rótulo do caminho, para montar o caminho relativo.
#' @return Um data frame com uma linha por arquivo encontrado (pastas excluídas).
listar_recursivo <- function(id, nivel = 0, prefixo = "") {
  itens <- googledrive::drive_ls(googledrive::as_id(id), n_max = 500)
  if (nrow(itens) == 0) return(tibble::tibble())

  eh_pasta <- purrr::map_chr(itens$drive_resource, "mimeType") ==
    "application/vnd.google-apps.folder"

  arquivos <- list()
  for (i in seq_len(nrow(itens))) {
    recuo <- strrep("  ", nivel)
    caminho <- if (prefixo == "") itens$name[i] else paste0(prefixo, "/", itens$name[i])

    if (eh_pasta[i]) {
      cat(cli::col_cyan(sprintf("%s📁 %s\n", recuo, itens$name[i])))
      arquivos[[length(arquivos) + 1]] <-
        listar_recursivo(itens$id[i], nivel + 1, caminho)
    } else {
      recurso <- itens$drive_resource[[i]]
      modificado <- substr(recurso$modifiedTime %||% "", 1, 16)
      cat(sprintf("%s   %s  %s\n", recuo, itens$name[i],
                  cli::col_grey(sprintf("(%s)", modificado))))
      arquivos[[length(arquivos) + 1]] <- tibble::tibble(
        caminho = caminho, nome = itens$name[i], id = itens$id[i],
        modificado = modificado
      )
    }
  }
  dplyr::bind_rows(arquivos)
}

#' Baixa os arquivos listados para `dados/brutos/drive/`, preservando o caminho.
#'
#' Só faz download — nunca envia nada. Arquivos já existentes são sobrescritos,
#' porque a fonte da verdade é o Drive.
#'
#' @param arquivos Data frame devolvido por [listar_recursivo()].
#' @return `invisible(NULL)`.
baixar <- function(arquivos) {
  if (nrow(arquivos) == 0) {
    log_step("Nada para baixar.", "aviso")
    return(invisible(NULL))
  }
  for (i in seq_len(nrow(arquivos))) {
    destino <- fs::path(DIR_DRIVE, arquivos$caminho[i])
    fs::dir_create(fs::path_dir(destino), recurse = TRUE)
    tryCatch(
      {
        googledrive::drive_download(
          googledrive::as_id(arquivos$id[i]), path = destino, overwrite = TRUE
        )
        log_step(sprintf("baixado: %s", arquivos$caminho[i]), "ok")
      },
      error = function(e) {
        # Google Docs/Sheets nativos precisam de export explícito; se falhar,
        # avisa e segue — um arquivo problemático não pode derrubar a varredura.
        log_step(sprintf("falhou %s: %s", arquivos$caminho[i], conditionMessage(e)), "aviso")
      }
    )
  }
  invisible(NULL)
}

# --- Execução ----------------------------------------------------------------
main <- function(baixar_tudo = FALSE) {
  autenticar()

  pasta <- googledrive::drive_get(googledrive::as_id(URL_PASTA))
  log_step(sprintf("Pasta do grupo: %s", pasta$name), "ok")
  cat("\n")

  arquivos <- listar_recursivo(pasta$id)

  cat("\n")
  log_step(sprintf("%d arquivo(s) encontrado(s).", nrow(arquivos)), "ok")

  if (baixar_tudo) {
    log_step(sprintf("Baixando para %s", DIR_DRIVE))
    baixar(arquivos)
  } else {
    log_step("Para baixar: .\\scripts\\rscript.cmd scripts\\drive_mentoria.R --baixar")
  }

  invisible(arquivos)
}

if (!interactive()) {
  main(baixar_tudo = "--baixar" %in% commandArgs(trailingOnly = TRUE))
}
