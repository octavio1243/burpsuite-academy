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
> - **Error de login distinto** por usuario → **enumeración** (`Invalid username` vs `Incorrect password`, o diff sutil / timing). Test: `carlos` existe, `carlosasdf` no → comparar.
> - **Rate limit en el login** → la vía intencionada es **fuerza bruta**.
> - **Checkbox "stay logged in"** → cookie `base64(user:md5(pass))` = vector de brute force **fuera de `/login`**.

> [!danger] 🚩 ¿Está? (Stage 2)
> - Hay **"recuperar contraseña"** (el reset es el flanco flojo).
> - El reset / el cambio de password **mandan el `username`** → manipulable → apuntar al admin / oráculo de fuerza bruta.

## 🎯 Por stage

| Aspecto | 🟢 Stage 1 | 🔴 Stage 2 |
| --- | --- | --- |
| **Objetivo** | entrar a la cuenta de la víctima | escalar a **admin** |
| **Caminos** | fuerza bruta, bypass 2FA, brute de stay-logged-in cookie | reset poisoning al admin, tokens cruzados, brute vía cambio de password, brute por cookie |

## ♾️ Independiente del stage

**Login / fuerza bruta:**
- [ ] Enumerar usuario (mensaje/timing/lock) → spray de passwords. Bloqueo por IP → **`X-Forwarded-For`**; por-request → **array de passwords** en JSON.
- [ ] **Stay-logged-in cookie** `base64(user:md5(pass))` → brute contra endpoint autenticado (sin rate limit).

**2FA:**
- [ ] **Simple bypass:** completás user+pass y navegás directo a `/my-account`.
- [ ] **Lógica rota:** cookie/param `verify=<víctima>` → brute del código (4 dígitos).

**Reset / cambio de password:**
- [ ] **Reset poisoning:** `X-Forwarded-Host: TU-collab` en el forgot → el token de la víctima te llega.
- [ ] **Tokens cruzados:** tu token válido + cambiar `username` al admin en el POST final.
- [ ] **Brute vía cambio de password:** 2 new-passwords distintas + `username` del admin → `New passwords do not match` delata el correcto sin lockear.

## 🔗 Referencias
- [[vulnerabilities/029-authentication/authentication|entry point]] · [[vulnerabilities/029-authentication/labs/README|labs]] · [[vulnerabilities/011-brute-force/login_userenum_password.py|scripts brute-force]] · Host header → carpeta `vulnerabilities/016-host-header-injection/`
