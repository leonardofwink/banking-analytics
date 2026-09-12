<#
.SYNOPSIS
  Prepara o ambiente Python do projeto: cria o .venv, instala as dependências e
  registra a biblioteca interna `banking` em modo editável.

.DESCRIPTION
  Roda uma vez por máquina (e de novo quando o requirements.txt mudar). É
  idempotente: se o .venv já existe, reaproveita.

  Passos:
    1. Descobre um Python >= 3.12 (launcher `py`, depois PATH).
    2. Cria .venv/ na raiz do projeto (fora do git).
    3. Instala requirements.lock.txt se existir — é o que garante reprodução
       exata. Só cai no requirements.txt quando ainda não há lock.
    4. Instala o projeto em modo editável (`pip install -e .`), tornando
       `from banking.projeto import ...` disponível de qualquer lugar.
    5. Gera/atualiza o requirements.lock.txt com o que de fato ficou instalado.

.EXAMPLE
  .\scripts\setup_python.cmd

.EXAMPLE
  # forçar recriação do ambiente do zero
  Remove-Item -Recurse -Force .venv ; .\scripts\setup_python.cmd
#>
$ErrorActionPreference = 'Stop'

# A raiz é o diretório-pai de scripts/ — o script funciona chamado de qualquer lugar.
$raiz = Split-Path -Parent $PSScriptRoot
$venv = Join-Path $raiz '.venv'
$venvPy = Join-Path $venv 'Scripts\python.exe'

function Escrever($msg, $cor = 'Cyan') { Write-Host "[setup-python] $msg" -ForegroundColor $cor }

#' Resolve um interpretador Python >= 3.12 desta máquina, ou $null.
function Resolve-Python {
  # O launcher `py` é o caminho mais confiável no Windows: sabe todas as versões
  # instaladas e não depende de PATH.
  $launcher = Get-Command 'py.exe' -ErrorAction SilentlyContinue
  if ($launcher) {
    foreach ($v in '-3.13', '-3.12', '-3') {
      try {
        $caminho = & $launcher.Source $v -c "import sys; print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $caminho) { return $caminho.Trim() }
      } catch { }
    }
  }
  $noPath = Get-Command 'python.exe' -ErrorAction SilentlyContinue
  if ($noPath) { return $noPath.Source }
  return $null
}

if (-not (Test-Path -LiteralPath $venvPy)) {
  $python = Resolve-Python
  if (-not $python) {
    Write-Error @"
Python não encontrado nesta máquina.
Instale o Python 3.12 ou superior (https://www.python.org/downloads/windows/),
marcando "Add python.exe to PATH" no instalador.
"@
    exit 1
  }
  Escrever "Criando ambiente virtual com $python"
  & $python -m venv $venv
  if ($LASTEXITCODE -ne 0) { Write-Error 'Falha ao criar o .venv.'; exit 1 }
} else {
  Escrever 'Ambiente virtual já existe — reaproveitando.'
}

Escrever 'Atualizando pip'
& $venvPy -m pip install --quiet --upgrade pip

$lock = Join-Path $raiz 'requirements.lock.txt'
$reqs = Join-Path $raiz 'requirements.txt'

if (Test-Path -LiteralPath $lock) {
  Escrever 'Instalando a partir do requirements.lock.txt (versões travadas)'
  & $venvPy -m pip install -r $lock
} else {
  Escrever 'Sem lock ainda — instalando a partir do requirements.txt'
  & $venvPy -m pip install -r $reqs
}
if ($LASTEXITCODE -ne 0) { Write-Error 'Falha ao instalar as dependências.'; exit 1 }

Escrever 'Registrando a biblioteca interna `banking` em modo editável'
& $venvPy -m pip install --quiet -e $raiz
if ($LASTEXITCODE -ne 0) { Write-Error 'Falha ao instalar o projeto em modo editável.'; exit 1 }

# O freeze exclui o próprio projeto (-e .), que é reinstalado pelo passo acima e
# apontaria para um caminho absoluto da máquina de quem rodou.
Escrever 'Gravando requirements.lock.txt'
$congelado = & $venvPy -m pip freeze --exclude-editable
$cabecalho = @(
  '# requirements.lock.txt — GERADO AUTOMATICAMENTE por scripts/setup_python.cmd.',
  '#',
  '# Não edite à mão. Declare a intenção em requirements.txt e rode o setup de novo.',
  '# Este arquivo trava as versões exatas que foram validadas: é o que faz outra',
  '# máquina reproduzir o mesmo número. Modelo treinado com outra versão de',
  '# scikit-learn pode dar outro resultado — sem ninguém perceber.',
  "# Gerado em: $(Get-Date -Format 'yyyy-MM-dd HH:mm')",
  ''
)
Set-Content -Path $lock -Value ($cabecalho + $congelado) -Encoding utf8

Escrever 'Pronto. Rode os scripts com .\scripts\py.cmd <arquivo.py>' 'Green'
