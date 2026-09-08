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

> A priori se busca **obtener sus cookies**.
- [ ] Buscador con XSS → exfiltrar cookies al exploit server.
- [ ] XSS **almacenado** en un comentario → se dispara cuando la víctima lo ve.
- [ ] Prototype pollution puede ser (correr extensión / DOM Invader).
- [ ] *(extra)* Si la cookie es `HttpOnly` y no la podés robar → usar el XSS para **actuar en su sesión**: leer el CSRF token + hacer `fetch` a `/my-account` o cambiar email/password en su nombre.
- [ ] *(extra)* Exfiltrar `apiKey`/datos de `/my-account` con `fetch` same-origin desde el XSS.
- 📁 [[vulnerabilities/002-xss/ejemplo-iframe.html|XSS]] · ofuscación en [[vulnerabilities/019-obfuscacion/xss-obfuscation|ofuscación XSS]]

### Cross-Site Request Forgery (CSRF)
> [!danger] 🚩 ¿Está o no está?
> **No existe token CSRF** en el form (o no se valida). Buen inicio que no lo tenga.

- [ ] *(por completar)* Endpoint que cambia **email/password sin token CSRF** (o token no validado) → PoC en exploit server → la víctima lo visita → cambio su email a uno mío → recupero contraseña por correo.
- [ ] *(por validar)* ¿SameSite de la cookie? `Lax`/`None` habilita variantes.
- 📁 [[vulnerabilities/003-csrf/csrf|CSRF]]

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
- 📁 [[vulnerabilities/002-xss/ejemplo-iframe.html|XSS]] (DOM)

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
