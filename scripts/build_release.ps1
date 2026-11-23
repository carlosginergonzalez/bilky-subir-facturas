# Empaqueta Bilky Subir Facturas para Windows (carpeta + ZIP para GitHub Release)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Version = (Get-Content "VERSION" -Raw).Trim()
$Name = "BilkySubirFacturas"
$DistDir = Join-Path $Root "dist\$Name"
$ZipPath = Join-Path $Root "dist\${Name}-${Version}-win64.zip"

if (-not (Test-Path ".\.venv\Scripts\flet.exe")) {
    throw "Ejecuta primero: py -m venv .venv; pip install -r requirements.txt"
}

Write-Host "==> Empaquetando con flet pack (v$Version)..."
& .\.venv\Scripts\flet.exe pack run_app.py `
  -n $Name `
  -i assets\icon.ico `
  -D `
  --product-name "Bilky Subir Facturas" `
  --product-version $Version `
  --file-version "$Version.0" `
  --company-name "Asesoria Colon" `
  --file-description "Subida de facturas PDF a Bilky" `
  --add-data "assets;assets" `
  --hidden-import playwright `
  --hidden-import playwright.sync_api `
  --hidden-import playwright._impl._driver `
  -y

if (-not (Test-Path $DistDir)) {
    throw "No se generó $DistDir"
}

$PwBrowsers = Join-Path $env:LOCALAPPDATA "ms-playwright"
if (-not (Test-Path $PwBrowsers)) {
    Write-Host "Instalando Chromium de Playwright..."
    & .\.venv\Scripts\python.exe -m playwright install chromium
}

Write-Host "==> Copiando motor Chromium (~200 MB) junto al ejecutable..."
$TargetBrowsers = Join-Path $DistDir "ms-playwright"
if (Test-Path $TargetBrowsers) {
    Remove-Item -Recurse -Force $TargetBrowsers
}
Copy-Item -Recurse $PwBrowsers $TargetBrowsers

if (Test-Path $ZipPath) { Remove-Item -Force $ZipPath }
Write-Host "==> Creando $ZipPath"
Compress-Archive -Path $DistDir -DestinationPath $ZipPath -Force

Write-Host ""
Write-Host "Listo:"
Write-Host "  Ejecutable: $DistDir\$Name.exe"
Write-Host "  ZIP release: $ZipPath"