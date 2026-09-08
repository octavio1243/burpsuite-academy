# STAGE 2 — PRIVILEGE ESCALATION

> **Objetivo único:** escalar del usuario normal (Stage 1) a **administrador**.
> Ahora **la víctima activa que navega y está logueada es el administrator**.
> Cada vulnerabilidad es *un camino distinto* para lo mismo: **tomar su cuenta o su rol**.

## 🧰 Herramientas que tengo para atacar

- 🔑 Ya estoy dentro como **usuario normal** (cuenta del Stage 1).
- 📧 **Bandeja de correo** → recibir links de reset / confirmaciones a un correo mío.
- 🌐 **Exploit server** → entregarle el exploit al **administrator** (HTML/JS, CSRF PoC, iframe, JS cacheado…).
- El admin **visita** lo que le sirvo → dispara el ataque en **su** sesión.

## 🎯 Qué busco (lo que me da admin)

1. **Sus credenciales** (usuario/contraseña de admin) → login directo.
2. **Su sesión / cookies** → las pego y soy admin.
3. **Cambiar su email/password** y recuperar por mi bandeja.
4. **Escalar mi propio rol** (`role=2`, `isAdmin=true`) sin tocar al admin.

## 🚦 Arranque (siempre)

- [ ] Ya logueado como user normal → mapear **qué hace el admin que yo no puedo**.
- [ ] **Burp Scan** → *Scan Insertion Points* sobre requests de Repeater interesantes.
- [ ] Comparar requests **user vs. admin** (¿solo cambia un `role`, `id`, cookie?).
- [ ] Extensiones: **Param Miner**, **HTTP Request Smuggler**, **InQL**.

---

## ✅ Vulnerabilidades (Stage 2)

### SQL Injection (SQLi)
> [!danger] 🚩 ¿Está o no está?
> Hay un **search / buscador** (o cualquier input que consulte la base de datos).

> **Objetivo:** obtener **usuario y contraseña de admin** por inyección SQL.
- [ ] Puntos: buscador, login, filtros, cookies, headers. `'`, `''`, `OR 1=1`.
- [ ] **UNION** → extraer credenciales del admin de la tabla de usuarios.
- [ ] Blind → condicional / time-based si no refleja.
- [ ] Bypass filtros/WAF con ofuscación.
- [ ] *(menos común)* **Escritura para escalar:** si la SQLi es un `UPDATE`/`INSERT` o permite stacked queries (`; UPDATE…`) → **subir tu propio rol** (`roleId` / `role` / `isAdmin`) en vez de robarle al admin. Ver callout *"vector de escritura"* en el entry point.
- 📁 **Cómo explotar:** [[vulnerabilities/001-sql-injection/README|SQL Injection]] · [[vulnerabilities/001-sql-injection/labs/README|labs]] · [[vulnerabilities/001-sql-injection/cheat-sheet|cheat sheet]]

### Cross-Site Scripting (XSS)
> [!danger] 🚩 ¿Está o no está?
> **¿Aparecen archivos `.js` nuevos** cuando estás logueado? Zonas que ve el admin.

> [!note] 🍪 `HttpOnly` — bifurca el camino, NO descarta el XSS
> **Mirá el flag `HttpOnly` de la cookie del admin antes** de apostar todo a robarla:
> - `HttpOnly: false` → **robo directo** de su cookie → sesión de admin.
> - `HttpOnly: true` → no la leés, pero el XSS **sigue sirviendo contra el admin**: `fetch` a `/my-account` para sacar `email`/`apiKey`, **leer su CSRF token y cambiarle email/password**, o reenviar el body como él. Más complejo, pero es la vía cuando la cookie está blindada. Detalle en [[vulnerabilities/002-xss/README#🎯 Qué hacer con un XSS (objetivos de explotación)|entry point → objetivos]].

> Si hay un **XSS en `my-account`** → hay que ver **cómo hacérselo llegar al administrator**.

**Dónde probar (recon):**
- [ ] **Reflexión en el buscador** → romper el contexto HTML con `<>`.
- [ ] **XSS en comentarios** (stored) → probar también el campo **website/URL** (va a un `href`).
- [ ] **DOM:** ¿hay `document.write`? ¿`location.search`? ¿`innerHTML`? ¿`location.hash`? (source → sink, DOM Invader).
- [ ] ¿Está corriendo **jQuery**? ¿**qué versión**? (sinks `$()`, `.html()`, `attr('href')`).
- [ ] ¿Hay **`ng-app`** / **AngularJS**? → inyección por **expresión** `{{...}}`.
- [ ] ¿Hay **`eval`** (u otro sink que evalúe la respuesta)? → reflected DOM.

**Qué hacer con él (contra el admin):**
- [ ] XSS **almacenado** (comentario/campo que el admin visita) → se dispara en su sesión.
- [ ] Con el XSS: robar sus cookies, o leer su CSRF token y **cambiar su email/password** vía `fetch` (payloads: [[vulnerabilities/002-xss/exfil-payloads.js|exfil-payloads.js]]).
- [ ] *(extra)* Exfiltrar datos de `/my-account` del admin (`email`, `apiKey`) al exploit server.
- 📁 **Cómo explotar:** [[vulnerabilities/002-xss/README|XSS]] · labs: [[vulnerabilities/002-xss/labs/README|labs]] · cheat sheet: [[vulnerabilities/002-xss/cheat-sheet|cheat sheet]] · ofuscación: [[vulnerabilities/019-obfuscacion/xss-obfuscation|xss-obfuscation]]

### Cross-Site Request Forgery (CSRF)
> [!danger] 🚩 ¿Está o no está?
> **La FLAG es que exista una acción relevante del admin que forjar.** Acá **sí** estás logueado (usuario normal) y el objetivo es **comprometer al admin** → CSRF es un vector de primera. Si hay acción relevante → evaluá la defensa; sin token es fácil, con token casi siempre hay bypass.

> [!tip] ✅ Confirmá que hay una víctima que visita tus entregas (Access log)
> Antes de invertir en un CSRF/XSS **entregado por exploit server**: entregá algo trivial y mirá el **Access log** del exploit server.
> - Aparece una **IP distinta a la tuya** → hay un **victim simulado** que visita tus entregas → el ataque *delivered* (CSRF/XSS al admin) **es viable**.
> - **Solo tu IP** → nadie consume las entregas → CSRF por exploit server **no aplica** → el admin solo **revisa contenido in-app** (⇒ **stored XSS** en un campo que ve en `/admin`), o el camino es **auto-escalada de privilegios** (sin víctima: mass-assignment `roleid`, IDOR, JWT…).
> ⚠️ Que hayas usado (o no) el exploit server en STAGE 1 **no** es la señal — es **reutilizable**. La señal es **quién aparece en el log**.

**Acciones del admin a probar (¿alguna es CSRF-able?):**
- [ ] **Cambiar email** → cambiárselo a uno mío → **reset de password** por correo → login como admin.
- [ ] **Cambiar contraseña** → sobre todo si el form **NO pide la contraseña actual** → CSRF directo.
- [ ] **Flujo de recuperación de cuenta** (forgot/reset password) → ¿puedo forjar el disparo del reset, o cómo se setea/valida el token de reset?
- [ ] Cualquier **otra acción con estado** del admin (cambiar rol, 2FA, borrar usuario, etc.).

**Cómo explotarla una vez encontrada:**
- [ ] Generar PoC (Burp → *Generate CSRF PoC*) → entregar al admin por exploit server → el admin la visita → se ejecuta en su sesión.
- [ ] Le cambio el email a uno mío → **recupero la contraseña** por correo → login como admin.
- [ ] **Si hay token CSRF** → probá los **puntos flojos** antes de descartar: ¿solo en POST? ¿solo si está presente? ¿no atado a la sesión? ¿atado a una cookie que puedo setear (CRLF)? ¿duplicado en cookie+body? → [[vulnerabilities/003-csrf/csrf#🔎 Puntos flojos a verificar (bypass de token)|puntos flojos]].
- [ ] *(por validar)* **SameSite** de la cookie (enruta el vector, **no** descarta): `None`/ausente → todos los vectores; `Lax` → solo GET top-level + `_method=POST`; `Strict` → redirect client-side / subdominio hermano.
- [ ] *(por validar)* **¿API REST (JSON)?** No es descarte → probá **convertir el body JSON a `x-www-form-urlencoded`** (o `text/plain`): si el server igual lo parsea, el CSRF sigue vivo (esos content-types no disparan preflight CORS).
- [ ] **Si el token está bien atado y no hay bypass** → buscá un **XSS** que lo lea y forje la request, o **dangling markup** para exfiltrarlo. Ver [[vulnerabilities/002-xss/README#🎯 Qué hacer con un XSS (objetivos de explotación)|XSS → bypass CSRF / dangling markup]].
- 📁 **Cómo explotar:** [[vulnerabilities/003-csrf/csrf|CSRF]] · labs: [[vulnerabilities/003-csrf/labs/README|labs]]

### Clickjacking
> [!danger] 🚩 ¿Está o no está?
> **Permite iframear** (faltan `X-Frame-Options` / CSP `frame-ancestors`).

> **Iframe que le cambie el email** al admin; **autocompletar el email por query params**.
- [ ] Iframe transparente sobre el form de "change email" con el campo prellenado en la URL.
- [ ] Le hago clic a ciegas → cambia email → recupero contraseña → **llega a mi bandeja**.
- 📁 `vulnerabilities/clickjacking/`

### DOM-Based Vulnerabilities (DOM)
> [!danger] 🚩 ¿Está o no está?
> **`.js` nuevos que hacen cosas raras** (`innerHTML`, `location`, `document.write`,
> `postMessage`, listeners…) especialmente en **`my-account`**.

- [ ] Rastrear **source → sink** (`location.hash/search`, `document.referrer`, `postMessage`).
- [ ] DOM-XSS → mismo fin que XSS: robar sesión / actuar como el admin.
- [ ] *(por validar)* `postMessage` sin chequeo de `origin`.
- 📁 **Cómo explotar:** [[vulnerabilities/002-xss/README#🌳 DOM XSS — source → sink|DOM XSS]] · labs: [[vulnerabilities/002-xss/labs/README|labs]]

### Cross-Origin Resource Sharing (CORS)
> [!danger] 🚩 ¿Está o no está?
> **Permite leer datos cross-site** con los headers habilitantes
> (`Access-Control-Allow-Origin` refleja `Origin` + `Allow-Credentials: true`).

> **Leer el `my-account`** del admin. *(pregunta: cómo entregarle el fetch al administrator?)*
- [ ] Servir desde el exploit server un `fetch` **con credenciales** a `/my-account`.
- [ ] Si refleja `Origin` arbitrario / `Origin: null` + `Allow-Credentials: true` → exfiltro su respuesta.
- 📁 `vulnerabilities/cors/`

### HTTP Request Smuggling (HRS)
> [!danger] 🚩 ¿Está o no está?
> **Pasaron los detectores** (HTTP Request Smuggler → *smuggle probe* confirma CL.TE / TE.CL).

> Permite interferir en la petición de **la víctima activa** (que puede ser el **administrator**) al encolar peticiones.
- [ ] **Robar su petición completa** por desfase de colas → capturar sus cookies/headers.
- [ ] Hacer un **`/my-account` camuflado** que caiga en su sesión.
- [ ] **Crear un comentario del admin** en un post con **sus headers** (probar su identidad / exfiltrar).
- 📁 `vulnerabilities/http_smuggling/`

### Access Control (IDOR / Broken Access Control)
> [!danger] 🚩 ¿Está o no está?
> Peticiones con **`username` / `id` / `role`** manipulables. Probar accesos directos.

- [ ] `/my-account?username=administrator` → ¿me devuelve sus datos?
- [ ] **Escalar privilegios de carlos** con un `update` → `role=2` (o `roleid`, `isAdmin`).
- [ ] Forzar rutas de admin (`/admin`) con user normal; headers `X-Original-URL`, `X-Forwarded-For`.
- 📁 *(crear `vulnerabilities/access-control/`)*

### Authentication (Auth)
> [!danger] 🚩 ¿Está o no está?
> *(por definir señal)* — probable: **rate limit en login** / 2FA / reset débil.

- [ ] *(por completar)* Fuerza bruta de credenciales de admin, bypass 2FA, enumeración, reset poisoning.
- 📁 `vulnerabilities/brute-force/`

### Web Cache Poisoning (WCP)
> [!danger] 🚩 ¿Está o no está?
> **Que se pueda cachear un `.js`** (`X-Cache: hit/miss` + `Age` en la respuesta).

> **Pisar archivos `.js`** para ejecutar los nuestros — o incluso **la página completa** y servir un HTML nuevo.
- [ ] Cachear un **JS falso mío** que le robe la sesión al admin cuando cargue la página.
- [ ] **Param Miner → Guess headers** para hallar el input no-keyed que envenena.
- 📁 *(crear `vulnerabilities/web-cache-poisoning/`)* · ver `vulnerabilities/host-header-injection/`

### HTTP Host Header Attacks (Host)
> [!danger] 🚩 ¿Está o no está?
> **Pisar el `Host`** del email de recuperar contraseña → el link apunta a **oastify/Collaborator** y **se ejecuta**.

- [ ] En **recuperar contraseña**, cambiar el `Host` → el link de reset del admin llega a mi Collaborator → capturo su token.
- [ ] *(variante)* Desde el usuario logueado, **cambiar la URL del reset** tras haber cambiado el correo primero.
- [ ] `X-Forwarded-Host`, doble `Host`, `Host: localhost`.
- 📁 `vulnerabilities/host-header-injection/`

### OAuth Authentication (OAuth)
> [!danger] 🚩 ¿Está o no está?
> **Requisito necesario:** el login **usa OAuth** (si no, no aplica).

- [ ] Manipular `redirect_uri` → desviar el **authorization code** del admin a mi exploit server.
- [ ] Falta de `state` → CSRF de login / account linking. Robo de `code` por `Referer`.
- 📁 *(crear `vulnerabilities/oauth/`)*

### JSON Web Tokens (JWT)
> [!danger] 🚩 ¿Está o no está?
> **Requisito necesario:** la sesión **es un JWT** (no una cookie de sesión simple).

- [ ] Forjar/alterar el token: `alg:none`, firma no verificada, HS256 débil (crackear), `kid`/`jwk`/`jku`.
- [ ] Cambiar `sub`/`role` → **administrator**.
- 📁 `vulnerabilities/jwt-attacks/`

---

## 🔎 Extras que ya teníamos (útiles en Stage 2)

### Password Reset
- [ ] Token débil/predecible, reutilizable, o ligado al **Host header**.
- [ ] `username`/`user_id` manipulable en el POST de reset → resetear al **admin**.
- 📁 *(crear `vulnerabilities/password-reset/`)* · ver `vulnerabilities/host-header-injection/`

### API Testing / Mass Assignment
- [ ] Métodos alternos (`PUT`/`PATCH`/`DELETE`), `Content-Type` swaps.
- [ ] **Mass assignment**: añadir `"isAdmin":true`, `"role":"admin"` al JSON del perfil.
- [ ] Documentación/endpoints ocultos de la API.
- 📁 *(crear `vulnerabilities/api-testing/`)*

### GraphQL (InQL)
- [ ] **InQL** → introspección; si está off, probar sugerencias/aliasing.
- [ ] Mutaciones no autorizadas (cambiar rol/password). Brute por batching (aliases) saltando rate limit.
- 📁 `vulnerabilities/graphql/`

### Prototype Pollution (client-side)
- [ ] Buscar *gadget*: `__proto__` en query/JSON/params → propiedad que afecte la lógica.
- [ ] DOM Invader (Burp) para detectar source→sink.
- 📁 `vulnerabilities/prototype-pollution/`

---

> [!success] Salida del Stage 2
> Sesión/credenciales de **administrador** → usar para el **Stage 3**.

> [!todo] Pendiente de completar
> **Authentication** (definir señal/escenario) y afinar los `?` cuando aparezcan en labs.
