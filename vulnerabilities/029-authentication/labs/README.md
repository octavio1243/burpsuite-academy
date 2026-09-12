---
aliases:
  - Authentication labs
  - brute force labs
  - 2FA labs
tags:
  - vuln/authentication
  - labs
  - portswigger
---

# Authentication — Labs de PortSwigger

Labs de la categoría **[Authentication](https://portswigger.net/web-security/authentication)**: **14 labs** (3 Apprentice + 9 Practitioner + 2 Expert). **Metodología general + fases + bypass de rate limits** → [[vulnerabilities/029-authentication/authentication|entry point]]. **Scripts propios de fuerza bruta** → carpeta `vulnerabilities/011-brute-force/`.

> [!abstract] Las tres fases (te dicen "por dónde entra")
> - **Login** — identificar usuario (enumeration) + probar password (brute force / spray).
> - **2FA / MFA** — saltear el paso, falsear a quién apunta el código, o fuerza bruta del código.
> - **Sesión / recuperación** — cookies "recordarme" predecibles, cracking offline, y el flujo de **password reset / change**.

> [!note] Cómo leer la tabla
> **Endpoint · vector** = contra qué request pega el ataque — clave: **no siempre es `/login`**; una **cookie** en un endpoint autenticado también es vector de fuerza bruta. **Objetivo** = obtener una cuenta o escalar. **Cómo** = el truco puntual (el detalle vive en el link del lab).

---

## Tabla de labs

| #   | Lab · nivel                                                                                                                                                                                                           | Fase           | Endpoint · vector                            | Objetivo                           | Cómo (el truco)                                                                                                              |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | -------------------------------------------- | ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| 1   | [Username enumeration via different responses](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-different-responses) · **Apprentice**                                  | Login          | `POST /login`                                | obtener cuenta (carlos)            | error distinto: `Invalid username` vs `Incorrect password` enumera users → luego brute-force del password                    |
| 2   | [2FA simple bypass](https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-simple-bypass) · **Apprentice**                                                                                          | 2FA            | página post-login (`/my-account`)            | obtener cuenta (tenés sus creds)   | logueás la 1ª fase y **navegás directo** a `/my-account`, salteando la verificación del código                               |
| 3   | [Password reset broken logic](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-reset-broken-logic) · **Apprentice**                                                                    | Reset          | `POST /forgot-password`                      | tomar cuenta carlos                | el token no se valida → cambiás `username=carlos` en el POST que setea la password nueva                                     |
| 4   | [Username enumeration via subtly different responses](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-subtly-different-responses) · **Practitioner**                  | Login          | `POST /login`                                | obtener cuenta                     | la diferencia es **sutil** (un punto final variable) → grep-match en Intruder para aislar el user válido                     |
| 5   | [Username enumeration via response timing](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-response-timing) · **Practitioner**                                        | Login          | `POST /login` + `X-Forwarded-For`            | obtener cuenta                     | user válido → chequea password (más lento); password largo amplifica el delay. `X-Forwarded-For` saltea el bloqueo por IP    |
| 6   | [Broken brute-force protection, IP block](https://portswigger.net/web-security/authentication/password-based/lab-broken-brute-force-protection-ip-block) · **Practitioner**                                           | Login          | `POST /login`                                | obtener cuenta carlos              | te bloquean por IP tras N fallos, pero **un login OK resetea el contador** → intercalás tu login válido cada pocos intentos  |
| 7   | [Username enumeration via account lock](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-account-lock) · **Practitioner**                                              | Login          | `POST /login`                                | obtener cuenta                     | tras N fallos, los users **válidos se lockean** (respuesta distinta) → eso los enumera → luego brute-force                   |
| 8   | [2FA broken logic](https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-broken-logic) · **Practitioner**                                                                                          | 2FA            | `POST /login2` + cookie `verify`             | obtener cuenta carlos              | cookie `verify=carlos` genera y ata el código a carlos → brute-force del **código de 4 dígitos**                             |
| 9   | [Brute-forcing a stay-logged-in cookie](https://portswigger.net/web-security/authentication/other-mechanisms/lab-brute-forcing-a-stay-logged-in-cookie) · **Practitioner**                                            | Sesión·cookie  | `GET /my-account` (cookie stay-logged-in)    | obtener cuenta carlos              | cookie = `base64(user:md5(password))` → brute-force la cookie contra un endpoint **autenticado, sin `/login` ni rate limit** |
| 10  | [Offline password cracking](https://portswigger.net/web-security/authentication/other-mechanisms/lab-offline-password-cracking) · **Practitioner**                                                                    | Sesión·cookie  | cookie robada vía **XSS**                    | obtener cuenta carlos (y borrarla) | **XSS** roba la stay-logged-in → decode base64 → **crackeás el MD5 offline** → login                                         |
| 11  | [Password reset poisoning via middleware](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-reset-poisoning-via-middleware) · **Practitioner**                                          | Reset          | `POST /forgot-password` + `X-Forwarded-Host` | tomar cuenta carlos                | el link del mail se arma con el Host → `X-Forwarded-Host: TU-collab` envenena el link → el **token de carlos te llega**      |
| 12  | [Password brute-force via password change](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-brute-force-via-password-change) · **Practitioner**                                      | Cambio de pass | `POST /my-account/change-password`           | obtener password de carlos         | new-passwords **distintas**: `New passwords do not match` delata el `current-password` correcto **sin lockear**              |
| 13  | [Broken brute-force protection, multiple credentials per request](https://portswigger.net/web-security/authentication/password-based/lab-broken-brute-force-protection-multiple-credentials-per-request) · **Expert** | Login          | `POST /login` (JSON)                         | obtener cuenta carlos              | rate limit **por request** → mandás un **array de passwords** en un solo request JSON `"password":[...]`                     |
| 14  | [2FA bypass using a brute-force attack](https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-bypass-using-a-brute-force-attack) · **Expert**                                                      | 2FA            | `POST /login2`                               | obtener cuenta carlos              | brute-force del código de 4 dígitos con **re-login automático** antes de cada intento (macro / Turbo Intruder)               |

---

## Patrones / cosas relevantes

- **Fase LOGIN — primero enumerá, después forzá:** confirmá usuarios válidos por **mensaje** (labs 1, 4), **timing** (5) o **account lock** (7). Recién ahí tirás passwords.
- **Fuerza bruta — el rate limit casi siempre está roto:** por IP que confía en `X-Forwarded-For` (5), contador que un login OK resetea (6), o límite por-request que se saltea con **array de passwords** (13). Herramientas propias en `vulnerabilities/011-brute-force/`.
- **Fase 2FA — tres sabores:** saltear el paso (2), falsear a quién apunta el código con la cookie `verify` (8), o fuerza bruta del código lidiando con el logout (14).
- **Fase SESIÓN — la cookie ES un vector:** si la stay-logged-in es `base64(user:md5(pass))` la brute-forceás contra un endpoint autenticado (9) o la robás por XSS y la crackeás offline (10). **No pega contra `/login`** → normalmente **sin rate limit**.
- **Password reset / change — el flanco más débil:** token no validado o `username` cambiable (3), link envenenado por Host header (11), o el cambio de password que filtra el current por diferencia de errores (12).
- **Objetivo típico:** **entrar a la cuenta de `carlos`** (o escalar a admin) — a veces el objetivo explícito es **borrar** su cuenta desde adentro.
