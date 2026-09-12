@echo off
rem py.cmd - roda um script Python no .venv do projeto, sem precisar ativa-lo.
rem
rem Espelha o scripts\rscript.cmd do lado R. Delega para py.ps1 com
rem -ExecutionPolicy Bypass: a politica padrao do Windows e Restricted e barra
rem .ps1 chamado direto. Um .cmd roda sempre, em PowerShell, cmd ou Git Bash.
rem
rem   scripts\py.cmd                             -> imprime o interpretador do venv
rem   scripts\py.cmd python\etl\01_ingestao.py   -> roda o script
rem   scripts\py.cmd -m pytest                   -> roda os testes
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0py.ps1" %*
exit /b %ERRORLEVEL%
