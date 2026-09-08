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
- 📁 `vulnerabilities/sql-injection/` · ofuscación en `vulnerabilities/obfuscacion/`

### Cross-Site Scripting (XSS)
> [!danger] 🚩 ¿Está o no está?
> **¿Aparecen archivos `.js` nuevos** cuando estás logueado? Zonas que ve el admin.

> Si hay un **XSS en `my-account`** → hay que ver **cómo hacérselo llegar al administrator**.
- [ ] XSS **almacenado** (comentario/campo que el admin visita) → se dispara en su sesión.
- [ ] Con el XSS: robar sus cookies, o leer su CSRF token y **cambiar su email/password** vía `fetch`.
- [ ] *(extra)* Exfiltrar datos de `/my-account` del admin (`email`, `apiKey`) al exploit server.
- 📁 `vulnerabilities/xss/` · ofuscación en `vulnerabilities/obfuscacion/`

### Cross-Site Request Forgery (CSRF)
> [!danger] 🚩 ¿Está o no está?
> **No hay token CSRF** en el `<form>` (o no se valida).

> **Cambio de correo/contraseña** del admin vía `<form>` malicioso.
- [ ] Generar PoC (Burp → *Generate CSRF PoC*) → entregar al admin por exploit server.
- [ ] Le cambio el email a uno mío → **recupero la contraseña** por correo → login como admin.
- [ ] *(por validar)* SameSite de la cookie (`Lax`/`None` habilita variantes).
- 📁 `vulnerabilities/csrf/`

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
- 📁 `vulnerabilities/xss/` (DOM)

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
