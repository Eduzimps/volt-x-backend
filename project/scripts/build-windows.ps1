param([switch]$SkipInstall)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path '.venv-win/Scripts/python.exe')) {
    & py -3.11 -m venv .venv-win
    if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.11 x64 first.' }
}
$Python = Join-Path $PWD '.venv-win/Scripts/python.exe'
if (-not $SkipInstall) {
    & $Python -m pip install -r requirements-build-windows.txt
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
}
& $Python -m PyInstaller --noconfirm --clean pyla.spec
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed.' }
$Target = Join-Path $PWD 'dist/PylaAI-auditado'
if (Test-Path $Target) { Remove-Item -Recurse -Force $Target }
New-Item -ItemType Directory -Path $Target | Out-Null
Move-Item 'dist/pyla-internal' (Join-Path $Target 'internal')
foreach ($Name in @('cfg','api','images','models','playstyles','static','templates')) {
    Copy-Item -Recurse $Name (Join-Path $Target $Name)
}
foreach ($Name in @('start.bat','LICENSE','README-AUDITORIA.md')) {
    Copy-Item $Name (Join-Path $Target $Name)
}
& $Python -m pip freeze | Set-Content (Join-Path $Target 'DEPENDENCIAS-WINDOWS.txt')
$Zip = Join-Path $PWD 'dist/pyla-v0.8.19-auditado-windows.zip'
if (Test-Path $Zip) { Remove-Item $Zip }
Compress-Archive -Path "$Target/*" -DestinationPath $Zip -CompressionLevel Optimal
Write-Host "Built: $Zip"
