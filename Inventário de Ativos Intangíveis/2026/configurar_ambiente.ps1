# Cria o ambiente Python do projeto e instala as bibliotecas (Windows / PowerShell).
# Uso: clique duas vezes em configurar_ambiente.bat, ou rode no terminal do VS Code:
#   powershell -ExecutionPolicy Bypass -File .\configurar_ambiente.ps1
$ErrorActionPreference = 'Stop'
Set-Location -Path $PSScriptRoot

function Get-Args($parts) { if ($parts.Length -gt 1) { return $parts[1..($parts.Length - 1)] } else { return @() } }

function Find-Python {
    foreach ($cand in @('py -3.13', 'py -3.12', 'py -3.11', 'python', 'python3')) {
        $parts = $cand.Split(' ')
        try {
            $extra = Get-Args $parts
            $v = & $parts[0] @extra -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>$null
            if ($LASTEXITCODE -eq 0 -and $v) {
                $maj, $min = $v.Trim().Split('.')
                if ([int]$maj -eq 3 -and [int]$min -ge 11) { return $cand }
            }
        } catch { }
    }
    return $null
}

Write-Host '1/5 Procurando Python 3.11 ou superior...'
$py = Find-Python
if (-not $py) {
    Write-Host 'Python 3.11+ nao encontrado. Instale em https://www.python.org/downloads/ (marque "Add python.exe to PATH") e rode de novo.' -ForegroundColor Red
    exit 1
}
Write-Host "    usando: $py"
$parts = $py.Split(' ')

if (-not (Test-Path '.venv\Scripts\python.exe')) {
    Write-Host '2/5 Criando o ambiente virtual .venv...'
    $extra = Get-Args $parts
    & $parts[0] @extra -m venv .venv
} else { Write-Host '2/5 Ambiente .venv ja existe.' }
$venvPy = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'

Write-Host '3/5 Instalando as bibliotecas (pode levar alguns minutos)...'
& $venvPy -m pip install --upgrade pip
& $venvPy -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host 'Falha no pip. Se a rede da SEPLAG usa proxy, defina antes: $env:HTTPS_PROXY = "http://usuario:senha@proxy:porta"' -ForegroundColor Red
    exit 1
}

Write-Host '4/5 Instalando o navegador Chromium do Playwright (PDFs e prints)...'
& $venvPy -m playwright install chromium

Write-Host '5/5 Registrando o kernel do Jupyter para o VS Code...'
& $venvPy -m ipykernel install --user --name inventario-2026 --display-name 'Inventario 2026 (.venv)'

Write-Host ''
Write-Host 'Ambiente pronto.' -ForegroundColor Green
Write-Host 'Para ativar no terminal:   .\.venv\Scripts\Activate.ps1'
Write-Host 'Para refazer tudo:         python executar.py --tudo'
