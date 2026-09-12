<#
.SYNOPSIS
  Descobre o Rscript.exe desta máquina e repassa os argumentos recebidos.

.DESCRIPTION
  O caminho do R muda de máquina para máquina (instalação em Program Files ou
  por usuário, versões diferentes) e o `Rscript` normalmente não fica no PATH.
  Fixar o caminho na documentação quebra em qualquer máquina que não seja a de
  quem escreveu. Este wrapper resolve o interpretador em tempo de execução, de
  modo que os comandos documentados rodem em todas as máquinas do time.

  Ordem de resolução (a primeira que responder vence):
    1. $env:RSCRIPT        — override explícito, para casos fora do padrão
    2. Rscript no PATH
    3. Registro do Windows — HKLM/HKCU SOFTWARE\R-core\R (InstallPath)
    4. Pastas padrão       — Program Files\R e %LOCALAPPDATA%\Programs\R
  Havendo mais de uma instalação, vence a versão mais recente.

.EXAMPLE
  .\scripts\rscript.ps1 scripts\etl\00_pipeline.R

.EXAMPLE
  # forçar uma instalação específica nesta sessão
  $env:RSCRIPT = "D:\R\R-4.5.2\bin\Rscript.exe"
  .\scripts\rscript.ps1 scripts\analises\share_tempo.R
#>
# Sem bloco param(): os argumentos chegam pelo $args automático e seguem
# literais para o Rscript. Um param() tornaria o script uma função avançada, e
# o PowerShell passaria a disputar flags do próprio R (-e, -q) como se fossem
# parâmetros comuns (-ErrorAction e afins).
$ErrorActionPreference = 'Stop'

#' Extrai a versão do caminho de instalação (R-4.6.1 -> [version]4.6.1) para
#' ordenar candidatos. Caminho sem versão legível vai para o fim da fila.
function Get-VersaoR {
  param([string] $Caminho)
  if ($Caminho -match 'R-(\d+\.\d+(\.\d+)?)') { return [version] $Matches[1] }
  return [version] '0.0.0'
}

#' Resolve o Rscript.exe desta máquina, ou $null se não achar nenhum.
function Resolve-Rscript {
  # 1. override explícito
  if ($env:RSCRIPT -and (Test-Path -LiteralPath $env:RSCRIPT)) { return $env:RSCRIPT }

  # 2. PATH
  $noPath = Get-Command 'Rscript.exe' -ErrorAction SilentlyContinue
  if ($noPath) { return $noPath.Source }

  $candidatos = New-Object System.Collections.Generic.List[string]

  # 3. registro (chave raiz + uma subchave por versão instalada)
  foreach ($raiz in 'HKLM:\SOFTWARE\R-core\R', 'HKCU:\SOFTWARE\R-core\R') {
    if (-not (Test-Path $raiz)) { continue }
    $chaves = @($raiz) + @(Get-ChildItem $raiz -ErrorAction SilentlyContinue | ForEach-Object { $_.PSPath })
    foreach ($k in $chaves) {
      try {
        $inst = (Get-ItemProperty -Path $k -Name 'InstallPath' -ErrorAction Stop).InstallPath
        if ($inst) { $candidatos.Add((Join-Path $inst 'bin\Rscript.exe')) }
      } catch { }
    }
  }

  # 4. pastas padrão de instalação
  $padroes = @(
    (Join-Path $env:ProgramFiles        'R\R-*\bin\Rscript.exe'),
    (Join-Path ${env:ProgramFiles(x86)} 'R\R-*\bin\Rscript.exe'),
    (Join-Path $env:LOCALAPPDATA        'Programs\R\R-*\bin\Rscript.exe')
  )
  foreach ($p in $padroes) {
    if (-not $p) { continue }
    Get-ChildItem -Path $p -ErrorAction SilentlyContinue |
      ForEach-Object { $candidatos.Add($_.FullName) }
  }

  $validos = $candidatos | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -Unique
  if (-not $validos) { return $null }
  return ($validos | Sort-Object -Property @{ Expression = { Get-VersaoR $_ } } -Descending | Select-Object -First 1)
}

$rscript = Resolve-Rscript
if (-not $rscript) {
  Write-Error @"
Rscript.exe não encontrado nesta máquina.
Instale o R (https://cran.r-project.org/bin/windows/base/) ou aponte o caminho:
  `$env:RSCRIPT = "C:\caminho\para\R\bin\Rscript.exe"
"@
  exit 1
}

if (-not $args) {
  Write-Host $rscript          # sem argumentos: só informa o caminho resolvido
  exit 0
}

& $rscript @args
exit $LASTEXITCODE
