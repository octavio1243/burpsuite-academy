---
aliases:
  - Authentication
  - authentication-entrypoint
  - Broken Authentication
  - fuerza bruta
  - brute force
  - username enumeration
  - 2FA
  - MFA
tags:
  - vuln/authentication
  - entrypoint
---

# Authentication — Punto de entrada

> Documento **agnóstico al negocio**: *cómo **romper la autenticación** para entrar a una cuenta o escalarla*.
> **Lab por lab** (fase · endpoint · objetivo · cómo) → [[vulnerabilities/029-authentication/labs/README|labs/README]].
> **Herramientas de fuerza bruta** (scripts propios) → carpeta `vulnerabilities/011-brute-force/` (`login_userenum_password.py`, wordlists).

> [!abstract] La idea en una línea
> La autenticación es un **flujo de varias fases** (identificar usuario → probar password → 2FA → mantener sesión). Cada fase se puede romper por separado: **enumerar** usuarios, **fuerza bruta** de password/código, **saltear** un paso, o **falsear** algo que vos controlás (una cookie, un header, un token de reset). El objetivo siempre es **entrar a una cuenta ajena** o **escalar** a admin.

## 📚 Referencias rápidas

- 🧪 **Labs** — 14 (3 Apprentice + 9 Practitioner + 2 Expert), con **fase · endpoint/vector · objetivo · cómo** → [[vulnerabilities/029-authentication/labs/README|labs/README]]
- 🐍 **Scripts de fuerza bruta** → `vulnerabilities/011-brute-force/` (enum de usuarios + spray de passwords, wordlists `usernames.txt` / `passwords.txt`)
- 🔑 **Sesiones basadas en token firmado** → [[vulnerabilities/018-jwt-attacks/README|JWT]] · **login federado** → [[vulnerabilities/026-oauth/oauth|OAuth]]

## 🧬 Las fases de la autenticación (y cómo se rompe cada una)

La autenticación no es "una request a `/login`". Es una **cadena**; atacás el eslabón más débil.

### 1️⃣ Fase LOGIN — ¿quién sos + probás que lo sos?

**a) Username enumeration** (¿el usuario existe?) — la app te delata cuáles son válidos:
- **Mensajes distintos**: `Invalid username` vs `Incorrect password`.
- **Diferencias sutiles**: un punto final que aparece/desaparece, un espacio, largo distinto → grepear en Intruder.
- **Timing**: si el user es válido, la app **sí chequea el password** (más lento). Mandá un password larguísimo y medí el tiempo.
- **Account lock**: tras N intentos, los users **válidos** se lockean (respuesta distinta) → eso mismo los delata.

**b) Password brute force / spray** — una vez que tenés el usuario, probás passwords. Acá entra toda la **fuerza bruta** (ver [[#🚦 Bypass de protección anti-fuerza bruta (rate limits)|apartado de rate limits]] abajo).

### 2️⃣ Fase 2FA / MFA — el segundo factor

Tres formas de pasarlo:
- **Saltearlo (simple bypass)**: completás la primera fase (usuario+password) y **navegás directo** a la página post-login (`/my-account`) **sin** pasar por la verificación del código. El paso de 2FA no está realmente **forzado** del lado server.
- **Lógica rota (`verify` controlable)**: el código se genera/valida contra un **valor que vos controlás** (cookie/param `verify=carlos`). Lo cambiás a la víctima → el server genera el código **para la víctima** → lo **fuerza-bruteás** (4 dígitos = 10 000 combinaciones).
- **Fuerza bruta del código**: 4 dígitos son pocos; el problema es que la app **te desloguea** tras varios fallos → automatizás el **re-login antes de cada intento** (macro de session handling / Turbo Intruder).

### 3️⃣ Fase SESIÓN y recuperación — mantener/recuperar la cuenta

- **Cookies "recordarme" (stay-logged-in)**: muchas veces es un valor **predecible/derivado del password** (`base64(user:md5(password))`). Eso la convierte en **otro vector de fuerza bruta** — y **no pega contra `/login`** sino contra **cualquier endpoint autenticado que acepte la cookie** (`GET /my-account`). Sin protección anti-brute-force ahí.
- **Offline cracking**: si robás esa cookie (p. ej. por **XSS**), la decodificás y **crackeás el hash offline** (sin tocar el server, sin rate limit).
- **Password reset**: el flujo de "olvidé mi contraseña" suele ser el eslabón más flojo:
  - **Lógica rota**: el token no se valida o el `username` del POST final se puede **cambiar a la víctima**.
  - **Poisoning por middleware**: el link del mail se arma con el **Host header** → con `X-Forwarded-Host: TU-collaborator` envenenás el link y **el token de la víctima te llega a vos**.
- **Password change**: el "cambiar contraseña" puede filtrar el **current-password** por diferencia de respuestas (mandás dos new-passwords distintas y observás cuál error tira) → fuerza bruta **sin lockear**.

> [!tip] Regla de oro: la cookie también es fuerza bruta
> No pienses solo en `/login`. **Cualquier endpoint que reciba una cookie de sesión/recordarme** es superficie de ataque: si la cookie es predecible o derivada del password, la fuerza-bruteás ahí, donde normalmente **no hay rate limit**.

## 🚦 Bypass de protección anti-fuerza bruta (rate limits)

El bloqueo casi siempre está mal implementado. Trucos para saltarlo:

- **`X-Forwarded-For`** (y variantes) — si el bloqueo es **por IP**, la app suele confiar en este header para saber "tu IP". Rotalo/spoofealo en cada request para **parecer una IP distinta**:
  ```
  X-Forwarded-For: 1.2.3.4
  ```
  Variantes que algunos back respetan: `X-Forwarded-For`, `X-Originating-IP`, `X-Remote-IP`, `X-Client-IP`, `X-Real-IP`.
- **Resetear el contador con un login válido** — si te bloquean tras N fallos pero **un login exitoso resetea el contador**, intercalá un login correcto **con tu propia cuenta** cada pocos intentos sobre la víctima.
- **Múltiples credenciales por request** — si el rate limit es **por request**, mandá **muchos passwords en uno solo** (array JSON):
  ```json
  { "username": "carlos", "password": ["123456","password","qwerty","..."] }
  ```
- **Atacar donde no hay límite** — el rate limit suele estar solo en `/login`. La **cookie stay-logged-in**, el **password change** o el **reset** normalmente **no lo tienen**.
- **Enumeración por canal lateral** — cuando no hay mensaje explícito, usá **timing** o **account lock** como oráculo booleano de "usuario válido".

## 🛡️ Prevención

- **Mensajes de error idénticos y genéricos** ("Invalid username or password") y **tiempos de respuesta uniformes** (chequear siempre el password, aun si el user no existe).
- **Rate limiting / lockout robusto**: basado en cuenta **y** en IP real (no en headers que el cliente controla), con CAPTCHA/backoff; que un login OK **no** resetee el contador de ataque.
- **2FA forzado del lado server** en cada paso; el código atado a la **sesión autenticada**, no a un valor que manda el cliente; código de suficiente entropía y con límite de intentos.
- **Cookies de sesión** aleatorias y opacas (no derivadas del password); "recordarme" con token firmado/rotable, no `base64(user:md5(pass))`.
- **Password reset** con token de un solo uso, aleatorio, corto de vida, atado al usuario; **no** construir URLs con el `Host`/`X-Forwarded-Host`.

---

> [!tip] Reglas mentales
> - **La auth es un flujo:** login → 2FA → sesión → reset. Atacá el eslabón más flojo, no siempre `/login`.
> - **Primero enumerá, después forzá:** confirmá usuarios válidos (mensaje/timing/lock) antes de tirar passwords.
> - **La cookie es fuerza bruta:** stay-logged-in / `verify` son predecibles → brute-force fuera de `/login`, donde no hay límite.
> - **El rate limit casi siempre está mal:** probá `X-Forwarded-For`, login-válido-que-resetea, array de passwords.
> - **El reset de password es el flanco débil:** token no validado, `username` cambiable, o link envenenado por Host header.

> [!note] Relación con otras vulns
> - **JWT** — si la sesión es un token firmado, el bypass va por ahí → [[vulnerabilities/018-jwt-attacks/README|018-jwt-attacks]].
> - **OAuth** — login federado con sus propios bypass → [[vulnerabilities/026-oauth/oauth|026-oauth]].
> - **Host header** — el password reset poisoning se apoya en el Host/`X-Forwarded-Host` → carpeta `vulnerabilities/016-host-header-injection/`.
> - **XSS** — para robar la cookie stay-logged-in y crackearla offline → carpeta `vulnerabilities/002-xss/`.
> - **Information disclosure** — usuarios/GUID filtrados aceleran la enumeración → carpeta `vulnerabilities/014-information-disclousure/`.
