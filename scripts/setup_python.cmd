@echo off
rem setup_python.cmd - prepara o ambiente Python do projeto.
rem
rem Cria o .venv, instala as dependencias e registra a biblioteca interna
rem `banking` em modo editavel. Rode uma vez por maquina, e de novo sempre que
rem o requirements.txt mudar. E idempotente.
rem
rem Delega para setup_python.ps1 com -ExecutionPolicy Bypass: a politica padrao
rem do Windows e Restricted e barra .ps1 chamado direto. Um .cmd roda sempre.
rem
rem   scripts\setup_python.cmd
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_python.ps1" %*
exit /b %ERRORLEVEL%
