param([ValidateSet('desktop','browser','headless')][string]$Mode = 'desktop')
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$Python = Join-Path $PWD '.venv-win/Scripts/python.exe'
if (-not (Test-Path $Python)) { throw 'Run scripts/build-windows.ps1 first to install dependencies.' }
& $Python main.py "--$Mode"
exit $LASTEXITCODE
