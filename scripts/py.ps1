<#
.SYNOPSIS
  Roda um script Python no ambiente virtual do projeto, sem precisar ativá-lo.

.DESCRIPTION
  Ativar o venv ("Activate.ps1") é fácil de esquecer, e o sintoma é traiçoeiro:
  o script roda no Python global, não acha `banking` ou usa outra versão de
  biblioteca, e o erro não diz isso. Este wrapper elimina o passo — sempre chama
  o interpretador de dentro do .venv.

  Espelha o papel do scripts/rscript.cmd no lado R.

.EXAMPLE
  .\scripts\py.cmd python\etl\01_ingestao.py

.EXAMPLE
  # sem argumentos: informa qual interpretador está sendo usado
  .\scripts\py.cmd

.EXAMPLE
  # também aceita as flags do próprio Python
  .\scripts\py.cmd -m pytest
#>
# Sem bloco param(): os argumentos chegam pelo $args automático e seguem
# literais para o Python. Um param() faria o PowerShell disputar flags do
# próprio interpretador (-m, -c) como se fossem parâmetros comuns.
$ErrorActionPreference = 'Stop'

$raiz = Split-Path -Parent $PSScriptRoot
$venvPy = Join-Path $raiz '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $venvPy)) {
  Write-Error @"
Ambiente virtual não encontrado em $venvPy
Rode primeiro:  .\scripts\setup_python.cmd
"@
  exit 1
}

if (-not $args) {
  Write-Host $venvPy           # sem argumentos: só informa o interpretador
  exit 0
}

& $venvPy @args
exit $LASTEXITCODE
