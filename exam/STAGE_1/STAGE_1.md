# STAGE 1 — FOOTHOLD

> **Objetivo único:** entrar en la cuenta de un **usuario víctima que está logueado y
> navegando** la web. Cada vulnerabilidad es *un camino distinto* para lo mismo: **acceder a su cuenta**.
> 🚩=`[!danger]` · 💡=`[!tip]` · ⚠️=`[!warning]`. El "qué probar" completo vive en `exam/to-do-list/<vuln>`.

## 🧰 Herramientas que tengo para atacar

- 📧 **Bandeja de correo** (`carlos@carlos-montoya.net` / la mía) → recibir links de reset, confirmaciones.
- 🌐 **Exploit server** → alojar y **entregar el exploit** a la víctima (HTML/JS malicioso, CSRF PoC, iframe, JS cacheado…).
- La víctima **visita** lo que le sirvo → dispara el ataque en su sesión.

## 🎯 Qué busco (lo que me da la cuenta)

1. **Sus cookies de sesión** → las pego y ya estoy dentro.
2. **Sus datos en `/my-account`** → `email`, `apiKey`, `password`.
3. **Cambiar sus credenciales** (email/password) y **recuperarlas por mi bandeja**.

## 🚦 Arranque (siempre)

- [ ] **Burp Scan** → *full domain* de fondo.
- [ ] Navegar toda la app (log/deslogueado) → poblar site map + Proxy history.
- [ ] Extensiones: **Param Miner**, **HTTP Request Smuggler**, **InQL**.
- [ ] JS del cliente → sinks: `location`, `eval`, `replace`, `addEventListener`, `postMessage`, `ng-app`.

---

## ✅ Vulnerabilidades (Stage 1)

### 🗄️ SQL Injection
> [!danger] 🚩 Cookie **`TrackingId`** → casi seguro SQLi (suele ser **blind**)

→ [[exam/to-do-list/sql-injection|Qué probar]]

### 🧬 Cross-Site Scripting (XSS)
> [!danger] 🚩 Se **importan `.js`** en la página (inyección/robo de cookie)

→ [[exam/to-do-list/xss|Qué probar]]

### 🎣 CSRF
> [!warning] ⚠️ Casi siempre **Stage 2** — el CSRF no te loguea; en S1 (sin cuenta) saltalo salvo víctima logueada + cuenta propia

→ [[exam/to-do-list/csrf|Qué probar]]

### 🖱️ Clickjacking
> [!warning] ⚠️ Casi siempre **Stage 2** — en S1 no hay víctima logueada cuyo clic robar

→ [[exam/to-do-list/clickjacking|Qué probar]]

### 🌳 DOM-Based
> [!danger] 🚩 `.js` con `addEventListener("message"` / `postMessage(` / `eval(`

→ [[exam/to-do-list/dom-based|Qué probar]]

### 🔀 CORS
> [!danger] 🚩 `ACAO` refleja tu `Origin` (o `null`) **+ `Allow-Credentials: true`**

→ [[exam/to-do-list/cors|Qué probar]]

### 📦 HTTP Request Smuggling
> [!danger] 🚩 *Smuggle probe* (CL.TE antes que TE.CL; diferencial > timing)

→ [[exam/to-do-list/http-request-smuggling|Qué probar]]

### 🔓 Access Control (IDOR)
> [!danger] 🚩 Peticiones con **`username`/`id`/GUID** manipulable → `/my-account?username=carlos`

→ [[exam/to-do-list/access-control|Qué probar]]

### 🔑 Authentication
> [!danger] 🚩 Error de login distinto por usuario · rate limit en login · checkbox "stay logged in"

→ [[exam/to-do-list/authentication|Qué probar]]

### 🌐 Web Cache Poisoning
> [!danger] 🚩 `X-Cache`/`Age`/`Vary`/`Cache-Control` en la respuesta

→ [[exam/to-do-list/web-cache-poisoning|Qué probar]]

### 🏠 HTTP Host Header
> [!danger] 🚩 El `Host`/`X-Forwarded-Host` manipulado termina en el link del mail de reset

→ [[exam/to-do-list/host-header|Qué probar]]

### 🪪 OAuth
> [!danger] 🚩 El login es **por OAuth** (si no, no aplica)

→ [[exam/to-do-list/oauth|Qué probar]]

### 🎫 JWT
> [!danger] 🚩 La sesión **es un JWT** (no una cookie de sesión simple)

→ [[exam/to-do-list/jwt|Qué probar]]

### 🔎 Content Discovery
→ [[exam/to-do-list/content-discovery|Qué probar]] (`robots.txt`, `/.git`, backups, endpoints ocultos)

---

> [!success] Salida del Stage 1
> Cookie/sesión **o** credenciales del usuario → guardar para el **Stage 2**.
