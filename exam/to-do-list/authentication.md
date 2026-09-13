---
aliases:
  - to-do Authentication
tags:
  - exam/to-do
  - vuln/authentication
---

# Authentication — Qué probar

> Técnica → [[vulnerabilities/029-authentication/authentication|entry point]] · labs → [[vulnerabilities/029-authentication/labs/README|labs]] · scripts → [[vulnerabilities/011-brute-force/login_userenum_password.py|brute-force]]

## 🚩 Flags

> [!danger] 🚩 ¿Está? (Stage 1)
> - **Error de login distinto** por usuario → **enumeración** (`Invalid username` vs `Incorrect password`, o diff sutil / timing). Test: `carlos` existe, `carlosasdf` no → comparar. → [[vulnerabilities/029-authentication/authentication#1️⃣ Fase LOGIN — ¿quién sos + probás que lo sos?|técnica]] · [Username enumeration via different responses](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-different-responses)
> - **Rate limit en el login** → la vía intencionada es **fuerza bruta**. → [[vulnerabilities/029-authentication/authentication#🚦 Bypass de protección anti-fuerza bruta (rate limits)|técnica]] · [Broken brute-force protection, IP block](https://portswigger.net/web-security/authentication/password-based/lab-broken-brute-force-protection-ip-block)
> - **Checkbox "stay logged in"** → cookie `base64(user:md5(pass))` = vector de brute force **fuera de `/login`**. → [[vulnerabilities/029-authentication/authentication#3️⃣ Fase SESIÓN y recuperación — mantener/recuperar la cuenta|técnica]] · [Brute-forcing a stay-logged-in cookie](https://portswigger.net/web-security/authentication/other-mechanisms/lab-brute-forcing-a-stay-logged-in-cookie)
> - **Reset con lógica rota** → el `POST /forgot-password` lleva `temp-forgot-password-token` + `username`: si **borrás el token** (o el param entero) y cambiás `username` a la víctima, la password se resetea igual → tomás la cuenta **sin token**. → [[vulnerabilities/029-authentication/authentication#3️⃣ Fase SESIÓN y recuperación — mantener/recuperar la cuenta|técnica]] · [Password reset broken logic](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-reset-broken-logic)

> [!danger] 🚩 ¿Está? (Stage 2)
> - Hay **"recuperar contraseña"** (el reset es el flanco flojo). → [[vulnerabilities/029-authentication/authentication#3️⃣ Fase SESIÓN y recuperación — mantener/recuperar la cuenta|técnica]] · [Password reset poisoning via middleware](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-reset-poisoning-via-middleware)
> - El reset / el cambio de password **mandan el `username`** → manipulable → apuntar al admin / oráculo de fuerza bruta. → [[vulnerabilities/029-authentication/authentication#3️⃣ Fase SESIÓN y recuperación — mantener/recuperar la cuenta|técnica]] · [Password brute-force via password change](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-brute-force-via-password-change)
>
> _Los labs de reset apuntan a **carlos** (Stage 1); en Stage 2 es la **misma técnica** con target = **admin**._

## 🎯 Por stage

| Aspecto | 🟢 Stage 1 | 🔴 Stage 2 |
| --- | --- | --- |
| **Objetivo** | entrar a la cuenta de la víctima | escalar a **admin** |
| **Caminos** | [[vulnerabilities/029-authentication/authentication#1️⃣ Fase LOGIN — ¿quién sos + probás que lo sos?\|fuerza bruta]], [[vulnerabilities/029-authentication/authentication#2️⃣ Fase 2FA / MFA — el segundo factor\|bypass 2FA]], [[vulnerabilities/029-authentication/authentication#3️⃣ Fase SESIÓN y recuperación — mantener/recuperar la cuenta\|brute de stay-logged-in cookie]], **[[vulnerabilities/029-authentication/authentication#3️⃣ Fase SESIÓN y recuperación — mantener/recuperar la cuenta\|reset con lógica rota]]** (token no validado) | [[vulnerabilities/029-authentication/authentication#3️⃣ Fase SESIÓN y recuperación — mantener/recuperar la cuenta\|reset poisoning al admin]], [[vulnerabilities/029-authentication/authentication#3️⃣ Fase SESIÓN y recuperación — mantener/recuperar la cuenta\|tokens cruzados]], [[vulnerabilities/029-authentication/authentication#3️⃣ Fase SESIÓN y recuperación — mantener/recuperar la cuenta\|brute vía cambio de password]], [[vulnerabilities/029-authentication/authentication#3️⃣ Fase SESIÓN y recuperación — mantener/recuperar la cuenta\|brute por cookie]] |

## ♾️ Independiente del stage

**Login / fuerza bruta:**
- [ ] Enumerar usuario (mensaje/timing/lock) → spray de passwords. → [[vulnerabilities/029-authentication/authentication#1️⃣ Fase LOGIN — ¿quién sos + probás que lo sos?|técnica]] · [different responses](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-different-responses) · [subtly different](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-subtly-different-responses) · [response timing](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-response-timing) · [account lock](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-account-lock)
- [ ] Bloqueo por IP → **`X-Forwarded-For`**; por-request → **array de passwords** en JSON. → [[vulnerabilities/029-authentication/authentication#🚦 Bypass de protección anti-fuerza bruta (rate limits)|técnica]] · [IP block](https://portswigger.net/web-security/authentication/password-based/lab-broken-brute-force-protection-ip-block) · [multiple credentials per request](https://portswigger.net/web-security/authentication/password-based/lab-broken-brute-force-protection-multiple-credentials-per-request)
- [ ] **Stay-logged-in cookie** `base64(user:md5(pass))` → brute contra endpoint autenticado (sin rate limit). → [[vulnerabilities/029-authentication/authentication#3️⃣ Fase SESIÓN y recuperación — mantener/recuperar la cuenta|técnica]] · [Brute-forcing a stay-logged-in cookie](https://portswigger.net/web-security/authentication/other-mechanisms/lab-brute-forcing-a-stay-logged-in-cookie) · [Offline password cracking](https://portswigger.net/web-security/authentication/other-mechanisms/lab-offline-password-cracking)

**2FA:**
- [ ] **Simple bypass:** completás user+pass y navegás directo a `/my-account`. → [[vulnerabilities/029-authentication/authentication#2️⃣ Fase 2FA / MFA — el segundo factor|técnica]] · [2FA simple bypass](https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-simple-bypass)
- [ ] **Lógica rota:** cookie/param `verify=<víctima>` → brute del código (4 dígitos). → [[vulnerabilities/029-authentication/authentication#2️⃣ Fase 2FA / MFA — el segundo factor|técnica]] · [2FA broken logic](https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-broken-logic) · [2FA bypass using a brute-force attack](https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-bypass-using-a-brute-force-attack)

**Reset / cambio de password:**
- [ ] **Lógica rota (Stage 1):** en el `POST /forgot-password`, **borrá el valor del `temp-forgot-password-token`** (o el param entero) y cambiá `username` a la víctima → si el server no valida el token, la password se resetea igual. → [Password reset broken logic](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-reset-broken-logic).
- [ ] **Reset poisoning:** `X-Forwarded-Host: TU-collab` en el forgot → el token de la víctima te llega. → [[vulnerabilities/029-authentication/authentication#3️⃣ Fase SESIÓN y recuperación — mantener/recuperar la cuenta|técnica]] · [Password reset poisoning via middleware](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-reset-poisoning-via-middleware)
- [ ] **Tokens cruzados:** tu token válido + cambiar `username` al admin en el POST final. → [[vulnerabilities/029-authentication/authentication#3️⃣ Fase SESIÓN y recuperación — mantener/recuperar la cuenta|técnica]] · [Password reset broken logic](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-reset-broken-logic)
- [ ] **Brute vía cambio de password:** 2 new-passwords distintas + `username` del admin → `New passwords do not match` delata el correcto sin lockear. → [[vulnerabilities/029-authentication/authentication#3️⃣ Fase SESIÓN y recuperación — mantener/recuperar la cuenta|técnica]] · [Password brute-force via password change](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-brute-force-via-password-change)
- [ ] **Token predecible por tiempo (Stage 2):** dispará **dos resets en paralelo** (admin + una cuenta tuya) con Repeater *Send group in parallel* / Turbo Intruder → si el token se deriva del **timestamp** y no está atado al usuario, el que te llega a **tu mail** canjea el del admin (`/forgot-password?token=<EL-TUYO>`). Difícil pero se intenta; señal: el token parece **secuencial/temporal**, no aleatorio. → [[vulnerabilities/029-authentication/authentication#3️⃣ Fase SESIÓN y recuperación — mantener/recuperar la cuenta|técnica]] · _sin lab dedicado_

## 🔗 Referencias
- [[vulnerabilities/029-authentication/authentication|entry point]] · [[vulnerabilities/029-authentication/labs/README|labs]] · [[vulnerabilities/011-brute-force/login_userenum_password.py|scripts brute-force]] · Host header → carpeta `vulnerabilities/016-host-header-injection/`
