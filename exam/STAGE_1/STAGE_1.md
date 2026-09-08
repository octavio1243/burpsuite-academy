# STAGE 1 — FOOTHOLD

> **Objetivo único:** entrar en la cuenta de un **usuario víctima que está logueado y
> navegando** la web. Cada vulnerabilidad es *un camino distinto* para lograr lo mismo.
> Independientemente de las variantes, el fin es uno: **acceder a su cuenta**.

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

### SQL Injection (SQLi)
> [!danger] 🚩 ¿Está o no está?
> Si hay una **cookie `TrackingId`** → **casi seguro hay SQL Injection** (suele ser **blind**). 🚩 FLAG casi asegurada.

> Fin: **bypass de login** o **extraer credenciales** de la tabla de usuarios → entrar en la cuenta.
- [ ] **Filtro de categoría** (`?category=`) → WHERE / UNION, salida visible.
- [ ] **Login** (`username`) → `administrator'--` (bypass, comenta el password).
- [ ] **Cookie `TrackingId`** → **blind** (⚠️). Si hay tracking, hay SQLi.
- [ ] **Stock check** → body XML → **filter bypass** si hay WAF.
- 📁 **Cómo explotar:** [[vulnerabilities/001-sql-injection/README|SQL Injection]] · labs: [[vulnerabilities/001-sql-injection/labs/README|labs]] · cheat sheet: [[vulnerabilities/001-sql-injection/cheat-sheet|cheat sheet]]

### Cross-Site Scripting (XSS)
> [!danger] 🚩 ¿Está o no está?
> Se **importan archivos `.js`** en la página (posible punto de inyección/robo).

> [!note] 🍪 `HttpOnly` — bifurca el camino, NO descarta el XSS
> **Mirá el flag `HttpOnly` de la cookie de sesión** (Burp → Response / DevTools) **antes** de invertir tiempo en robar la cookie:
> - `HttpOnly: false` → `document.cookie` la ve → **robo directo de cookie** (win rápido).
> - `HttpOnly: true` → **no** podés leer la cookie, pero el XSS **sigue teniendo impacto**: `fetch` same-origin a `/my-account` para rascar info (`email`, `apiKey`), **actuar en su sesión** (cambiar email/password leyendo el CSRF token), o reenviar el body. Es un ataque **más complejo** pero válido → probarlo llegado el caso. Detalle en [[vulnerabilities/002-xss/README#🎯 Qué hacer con un XSS (objetivos de explotación)|entry point → objetivos]].

> A priori se busca **obtener sus cookies**.

**Dónde probar (recon):**
- [ ] **Reflexión en el buscador** → romper el contexto HTML con `<>` (`"><svg onload=...>`).
- [ ] **XSS en comentarios** (stored) → probar también el campo **website/URL** (va a un `href`).
- [ ] **DOM:** ¿hay `document.write`? ¿`location.search`? ¿`innerHTML`? ¿`location.hash`? → seguir **source → sink** (DOM Invader).
- [ ] ¿Está corriendo **jQuery**? ¿**qué versión**? (sinks `$()`, `.html()`, `attr('href')`).
- [ ] ¿Hay **`ng-app`** / **AngularJS**? → inyección por **expresión** `{{...}}`, no HTML.
- [ ] ¿Hay **`eval`** (u otro sink que evalúe la respuesta)? → reflected DOM.
- [ ] Prototype pollution puede ser (correr extensión / DOM Invader).

**Qué hacer con él:**
- [ ] Buscador/comentario con XSS → **exfiltrar cookies** al exploit server (payloads: [[vulnerabilities/002-xss/exfil-payloads.js|exfil-payloads.js]]).
- [ ] *(extra)* Si la cookie es `HttpOnly` y no la podés robar → usar el XSS para **actuar en su sesión**: leer el CSRF token + hacer `fetch` a `/my-account` o cambiar email/password en su nombre.
- [ ] *(extra)* Exfiltrar `apiKey`/datos de `/my-account` con `fetch` same-origin desde el XSS.
- 📁 **Cómo explotar:** [[vulnerabilities/002-xss/README|XSS]] · labs: [[vulnerabilities/002-xss/labs/README|labs]] · cheat sheet: [[vulnerabilities/002-xss/cheat-sheet|cheat sheet]] · ofuscación: [[vulnerabilities/019-obfuscacion/xss-obfuscation|xss-obfuscation]]

### Cross-Site Request Forgery (CSRF)
> [!danger] 🚩 ¿Está o no está?
> **La FLAG es que haya una acción relevante que forjar** (cambiar email/password sobre todo). Si la hay → evaluá la defensa. Que **no tenga token** es el caso fácil; con token, casi siempre hay bypass.

- [ ] *(por completar)* Endpoint que cambia **email/password** → PoC en exploit server → la víctima lo visita → cambio su email a uno mío → recupero contraseña por correo.
- [ ] **Si hay token CSRF** → probá los **puntos flojos** antes de descartar: ¿valida solo en POST? ¿solo si está presente? ¿no atado a la sesión? ¿atado a una cookie que puedo setear (CRLF)? ¿duplicado en cookie+body? → [[vulnerabilities/003-csrf/csrf#🔎 Puntos flojos a verificar (bypass de token)|puntos flojos]].
- [ ] *(por validar)* **SameSite** de la cookie (enruta el vector, **no** descarta): `None`/ausente → todos los vectores; `Lax` → solo GET top-level + `_method=POST`; `Strict` → redirect client-side / subdominio hermano.
- [ ] *(por validar)* **¿API REST (JSON)?** No es descarte → probá **convertir el body JSON a `x-www-form-urlencoded`** (o `text/plain`): si el server igual lo parsea, el CSRF sigue vivo (esos content-types no disparan preflight CORS).
- [ ] **Si el token está bien atado y no hay bypass** → buscá un **XSS** que lea el token y forje la request, o **dangling markup** para exfiltrarlo. Ver [[vulnerabilities/002-xss/README#🎯 Qué hacer con un XSS (objetivos de explotación)|XSS → bypass CSRF / dangling markup]].
- 📁 **Cómo explotar:** [[vulnerabilities/003-csrf/csrf|CSRF]] · labs: [[vulnerabilities/003-csrf/labs/README|labs]]

### Clickjacking
> [!danger] 🚩 ¿Está o no está?
> **No tiene** cabecera `X-Frame-Options` ni CSP `frame-ancestors` → se puede enmarcar.

- [ ] Iframe transparente sobre botones → hacerle **cambiar la contraseña o el email** a ciegas; luego recupero la contraseña y **llega a mi bandeja**.
- [ ] *(extra)* Prellenar el form vía parámetros en la URL del iframe (labs de "change email"). Requiere que falte `X-Frame-Options` / `frame-ancestors`.
- 📁 [[vulnerabilities/004-clickjacking/clickjacking|Clickjacking]]

### DOM-Based Vulnerabilities (DOM)
> [!danger] 🚩 ¿Está o no está?
> Hay `.js` con **sinks peligrosos**: `innerHTML`, `document.write`, `location`,
> `eval`, `postMessage`, `addEventListener` / listeners, `setTimeout`, jQuery `$()`.

- [ ] *(por completar)* DOM-XSS: rastrear **source → sink** (`location.hash/search`, `document.referrer`, `postMessage`) → mismo fin que XSS (cookies/acciones).
- [ ] *(por validar)* `postMessage` sin chequeo de `origin` → inyectar. DOM open-redirect para robar token en flujos OAuth.
- 📁 **Cómo explotar:** [[vulnerabilities/002-xss/README#🌳 DOM XSS — source → sink|DOM XSS]] · labs: [[vulnerabilities/002-xss/labs/README|labs]]

### Cross-Origin Resource Sharing (CORS)
> [!danger] 🚩 ¿Está o no está?
> Refleja **`Origin` arbitrario** en `Access-Control-Allow-Origin` **+
> `Allow-Credentials: true`** (o acepta `Origin: null`). *A verificar en la respuesta.*

- [ ] `fetch` a `/my-account` buscando datos del usuario (`email`, `apiKey`, `password`).
- [ ] *(extra)* Servir el `fetch` **con credenciales desde el exploit server**: si refleja `Origin` arbitrario + `Allow-Credentials: true` (o `Origin: null`) → exfiltro la respuesta.
- 📁 [[vulnerabilities/005-cors/cors|CORS]]

### HTTP Request Smuggling (HRS)
> [!danger] 🚩 ¿Está o no está?
> **Correr scripts de detección** (HTTP Request Smuggler → *smuggle probe*) →
> confirma CL.TE / TE.CL.

- [ ] Emitir otra petición que haga `GET /my-account` → robar `email`/`apiKey`/`password`.
- [ ] Emitir petición que fuerce un `Set-Cookie` **que refleje las cookies** → obtener las suyas.
- [ ] **Robar su petición** por desfase de colas (capturar su request completa).
- [ ] *(por validar)* HTTP Request Smuggler → *smuggle probe*; probar **CL.TE** / **TE.CL**.
- 📁 [[vulnerabilities/008-http_smuggling/detect.py|HTTP Request Smuggling]]

### Access Control Vulnerabilities (IDOR / Broken Access Control)
> [!danger] 🚩 ¿Está o no está?
> No hay una señal única (va más por probar). Pista: **peticiones que llevan el
> nombre de usuario / `id` / GUID** manipulable (IDOR).

- [ ] `/my-account?username=carlos` (sin loguear) → ver si devuelve sus datos → `email`, `apiKey`, `password`.
- [ ] *(extra)* Cambiar `id`/GUID en URL/params/cookies → recurso ajeno. Forzar `/admin` o rutas ocultas.
- 📁 *(crear)* [[vulnerabilities/access-control/README|Access Control]]

### Authentication (Auth)
> [!danger] 🚩 ¿Está o no está?
> **Rate limit en el login** (si lo hay, es la pista: no te lo dejan tan fácil →
> dificultad mínima esperada).

- [ ] **Fuerza bruta** con las listas (~11000 peticiones) → usar scripts de [[vulnerabilities/011-brute-force/login_userenum_password.py|brute-force]].
- [ ] *(extra)* Enumeración de usuario (mensaje/tiempo distinto), bypass de 2FA / brute del código, reset poisoning, credenciales por defecto.
- [ ] *(por validar)* Rate limit → resetear contador con `X-Forwarded-For`.
- 📁 [[vulnerabilities/011-brute-force/login_userenum_password.py|brute-force]]

### Web Cache Poisoning (WCP)
> [!danger] 🚩 ¿Está o no está?
> **Sí o sí** cabeceras **`X-Cache`** (`hit`/`miss`) **+ `Age`** en la respuesta de
> un `.js` → hay caché que envenenar.

- [ ] Cachear un **JavaScript falso mío** que envíe las cookies a mi exploit server.
- [ ] *(extra)* Detectar caché (`X-Cache`, `Age`) + **Param Miner → Guess headers** para hallar el input no-keyed que envenena.
- 📁 *(crear)* · ver [[vulnerabilities/016-host-header-injection/conn_reuse.py|Host header]]

### HTTP Host Header Attacks (Host)
> [!danger] 🚩 ¿Está o no está?
> *(por definir señal)* — de momento: probar en **recuperar contraseña** si el `Host`
> manipulado termina en el link del correo.

- [ ] En **recuperar contraseña**, cambiar el `Host` → ver si el link de reset apunta a **oastify/Collaborator** (envenenamiento del reset).
- [ ] *(extra)* `X-Forwarded-Host`, doble `Host`, `Host: localhost` → bypass / acceso interno.
- 📁 [[vulnerabilities/016-host-header-injection/conn_reuse.py|Host header]]

### OAuth Authentication (OAuth)
> [!danger] 🚩 ¿Está o no está?
> **Requisito necesario:** el login debe ser **por OAuth** sí o sí (si no, no aplica).

- [ ] *(por completar)* Manipular `redirect_uri` → desviar el **authorization code** a mi exploit server → robar su sesión.
- [ ] *(por validar)* Falta de `state` → CSRF de login / account linking. Robo de `code` por `Referer`.
- 📁 *(crear)* [[vulnerabilities/oauth/README|OAuth]]

### JSON Web Tokens (JWT)
> [!danger] 🚩 ¿Está o no está?
> **Requisito necesario:** el login usa **JWT** (no una session cookie simple).

- [ ] *(por completar)* Forjar token de la víctima: `alg:none`, firma no verificada, clave HS256 débil (crackear), inyección `kid`/`jwk`/`jku`.
- 📁 [[vulnerabilities/018-jwt-attacks/crack_jwt.py|JWT]]

---

## 🔎 Extras que ya teníamos (útiles)

### Content Discovery
- [ ] Burp *Discover content*, `robots.txt`, `sitemap.xml`, `/.git`, comentarios HTML, backups (`.bak`, `~`, `.old`), endpoints/API ocultos.
- 📁 [[vulnerabilities/014-information-disclousure/README|Content discovery]]

---

> [!success] Salida del Stage 1
> Cookie/sesión **o** credenciales del usuario → guardar para el **Stage 2**.

> [!todo] Pendiente de completar
> Los marcados **`?` / (por completar)** los llenamos en la próxima iteración
> (CSRF, DOM, OAuth, JWT sobre todo).
