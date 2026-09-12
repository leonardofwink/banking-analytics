@echo off
rem rscript.cmd - ponto de entrada para chamar o R do projeto, em qualquer maquina.
rem
rem Delega para rscript.ps1 (que descobre o Rscript.exe local) passando
rem -ExecutionPolicy Bypass: a politica padrao do Windows e Restricted, que
rem impede executar .ps1 diretamente. Um .cmd roda sempre, independente de
rem politica, e funciona igual em PowerShell, cmd e Git Bash.
rem
rem   scripts\rscript.cmd                          -> imprime o Rscript resolvido
rem   scripts\rscript.cmd scripts\etl\00_pipeline.R -> roda o pipeline
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0rscript.ps1" %*
exit /b %ERRORLEVEL%
