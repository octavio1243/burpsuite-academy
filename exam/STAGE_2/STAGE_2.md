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
> [!danger] 🚩 ¿Está o no está? (las 3 juntas)
> 1. **Acción relevante y clickeable** del admin (cambiar su email, borrar/aprobar algo, submit que dispara XSS…).
> 2. **La página del admin se deja enmarcar** → **faltan** `X-Frame-Options` **y** CSP `frame-ancestors` en la response.
> 3. Hay una **víctima admin** que visita tu entrega y **hace clic** → confirmalo con el **Access log** del exploit server (IP distinta a la tuya, igual que con CSRF/XSS entregados).
> Si la página **no** se enmarca → descartá clickjacking (pivoteá a CSRF/XSS). **Sirve aunque el form tenga token CSRF** (la víctima manda su form real).

**Acciones del admin a probar (¿alguna es clickeable a ciegas?):**
- [ ] **Cambiar email** del admin → el campo se puede **prellenar por query param** en el `src` del iframe → clic ciego → reset de password → **llega a tu bandeja**.
- [ ] **Borrar/aprobar** algo con estado (incluso **multistep** con confirmación → varios señuelos).
- [ ] **Submit** que dispara un **DOM XSS** → el clic ciego ejecuta el payload (prellenado por URL).

> [!tip] 🏷️ Nombres de botones/señuelos (no se adivinan, se leen)
> El **texto del señuelo** lo elegís vos (los labs usan **`Test me`**, o **`Click me first`** / **`Click me next`** en multistep). El **botón real** del admin lo **reconocés registrando tu propia cuenta** y navegando el target (ahí ves el label exacto y si hay confirmación). Candidatos vistos en los labs para buscar/alinear en el target:
> - **`Delete account`** (+ confirmación **`Yes`**) → suele ser **multistep**.
> - **`Update email`** → change-email (prellenable por URL).
> - **`Submit feedback`** → si dispara DOM XSS.
> Orden multistep típico: **botón de acción → `Yes`**.

**Cómo explotarla:**
- [ ] Iframe del target casi transparente (`opacity` baja) + `<div>` señuelo sobre el botón; alineá con `opacity:0.1` y entregá con `~0.0001`.
- [ ] **¿No sabés la resolución del admin?** Mandá un **beacon** (`<img>`) con `screen.width/height` + `innerWidth/Height` + `dpr` al **Collaborator** o al **Access log** del exploit server → recalculá los `top`/`left` (o posicioná el señuelo por proporción de `innerWidth`). Ver [[vulnerabilities/004-clickjacking/clickjacking#6) Beacon de resolución/layout (para alinear a ciegas)|PoC beacon]].
- [ ] **Prellená** los inputs por query params; si hay **frame buster** → `sandbox="allow-forms"`.
- 📁 **Cómo explotar:** [[vulnerabilities/004-clickjacking/clickjacking|Clickjacking]] · labs: [[vulnerabilities/004-clickjacking/labs/README|labs]]

### DOM-Based Vulnerabilities (DOM)
> [!danger] 🚩 ¿Está o no está? — **grepeá el JS (sobre todo el nuevo)**
> **`.js` nuevos que aparecen contra el admin** (checkout, `my-account`, home). Buscá (Ctrl+F): **`addEventListener("message"` / `postMessage(` / `eval(`** → **altamente probable** que haya vuln DOM-based (prioridad alta). Otros sinks: `innerHTML`, `document.write`, `location`/`location.href`, `document.cookie`, `setTimeout(str)`, jQuery `$()`. Sources: `location.search/hash`, `document.referrer`, `document.cookie`, `window.name`, web messages. Lista → [[vulnerabilities/025-dom-based/sinks|sinks & sources]].

> [!note] 🎯 Objetivo y entrega (leé esto antes de la checklist)
> **Objetivo:** ejecutar JS en la sesión del **admin** → **robar su cookie** (si no es `HttpOnly`) o **actuar como él** (leer su CSRF token y cambiarle email/password, o disparar la acción de admin). Mismo fin que un XSS.
> **¿Requiere exploit server? SÍ.** Estos DOM-based **no persisten** en el target (el bug vive en el JS del cliente) → tenés que **entregar** un `<iframe>`/URL por el **exploit server** y que el **admin lo visite**. Única excepción: **open redirect**, que puede ser una URL directa (para robar el `code` en OAuth).
> **Tu duda ("¿sirve en Stage 2? depende del exploit server"):** sí, **depende de que el admin visite** tu exploit — y eso es exactamente lo que hace el **bot víctima** del examen. Es la vía clásica para escalar a admin cuando su cookie se puede robar o podés actuar en su sesión. **Confirmá la visita en el Access log** (IP distinta).

- [ ] **Grepeá los sinks** en cada `.js` → rastreá source→sink (**DOM Invader**). Un `postMessage`/`addEventListener('message')`/`eval` es la señal fuerte.
- [ ] **Web message** (`postMessage` sin chequeo de `origin`) → `<iframe>` al target que dispara `postMessage` en `onload`; se lo hacés llegar al **admin** por el exploit server → XSS en su sesión.
- [ ] **DOM-XSS** → mismo fin que XSS contra el admin: robar sesión / actuar como él (leer su CSRF token, cambiar email/password).
- [ ] **DOM open-redirect** → robar **token/`code`** del admin en OAuth. **Cookie manipulation** / **DOM clobbering** (si hay DOMPurify + `id`/`name` permitidos).
- 📁 **Cómo explotar:** [[vulnerabilities/025-dom-based/dom-based|DOM-based]] · sinks: [[vulnerabilities/025-dom-based/sinks|sinks & sources]] · labs: [[vulnerabilities/025-dom-based/labs/README|labs]] · DOM-XSS clásico: [[vulnerabilities/002-xss/README#🌳 DOM XSS — source → sink|XSS→DOM]]

### Cross-Origin Resource Sharing (CORS)
> [!danger] 🚩 FLAG — se tiene que cumplir esto (en la respuesta del endpoint de datos)
> **Las dos juntas** para leer los datos del **admin**:
> 1. **`Access-Control-Allow-Origin` refleja tu `Origin` arbitrario** (probalo en Repeater con `Origin: https://evil.com`) — o acepta **`Origin: null`** — o **confía en subdominios** (ahí necesitás un **XSS en un subdominio** como trampolín).
> 2. **`Access-Control-Allow-Credentials: true`** (necesario para que viajen las cookies del admin).
>
> ⚠️ **`ACAO: *` NO sirve** para robar la sesión del admin (`*` no convive con credenciales). Buscás **reflejo** / **`null`** / **subdominio confiable**.

> **Objetivo:** leer el `/my-account` (o `/accountDetails`) del **admin** → robar su `apiKey`/datos → escalar.
- [ ] En Repeater, agregar `Origin: https://evil.com` a la request de datos → confirmar reflejo + `Allow-Credentials: true`.
- [ ] **Entrega (respuesta a tu duda "cómo se lo doy al admin"):** subís al **exploit server** un `<script>`/`<iframe>` con `fetch(endpoint,{credentials:'include'})`, exfiltrás a `…/log?key=`, y usás **"Deliver exploit to victim"** → el bot admin lo visita con **sus** cookies. Confirmás en el **Access log**.
- [ ] Si confía en subdominios/HTTP → el trampolín es un **XSS en subdominio** (ver lab Practitioner).
- 📁 **Cómo explotar:** [[vulnerabilities/005-cors/cors|CORS]] · labs: [[vulnerabilities/005-cors/labs/README|labs]]

### HTTP Request Smuggling (HRS)
> [!danger] 🚩 ¿Está o no está?
> Igual que Stage 1 (HTTP Request Smuggler; **CL.TE antes que TE.CL**; **diferencial > timing**). La diferencia: acá la **víctima activa suele ser el `administrator`**.

> **En Stage 2 (escalar a admin):** aprovechás que **el admin navega** y/o entrás directo al panel.
- [ ] **Comentario + admin navegando** → si podés **comentar** y el admin **visita el post**, colá para **robarle las cookies** (capturar su request / meter un stored XSS que caiga en su sesión).
- [ ] **Header especial para ser admin** → **revelá/reflejá tus headers** (reveal front-end rewriting) y **compará con los del admin**: deducí qué header agrega el front (IP interna, rol, `X-…`) y **replicalo** en la request colada → [[vulnerabilities/008-http_smuggling/labs/README|lab 8]].
- [ ] **Entrar al admin directo:** basta con **bypassear el front y contrabandear la 2ª petición** a `/admin/…` (borrar carlos / crear admin) → [[vulnerabilities/008-http_smuggling/examples/001-cl-te|CL.TE]] / [[vulnerabilities/008-http_smuggling/examples/002-te-cl|TE.CL]].
- [ ] **Recurso estático (CL.0) hacia `/admin`:** posible, **pero es ciego** (no ves la respuesta) → no sabés qué pasó → **escenario poco probable/poco útil** salvo una acción a ciegas ya conocida → [[vulnerabilities/008-http_smuggling/examples/006-cl-0|006 · CL.0]].
- [ ] **También acá:** envenenar caché con JS del exploit, **web cache deception** y **response queue poisoning** → [[vulnerabilities/008-http_smuggling/examples/007-response-queue-poisoning|007]] (ver detalle en Stage 1).
- 📁 **Cómo explotar:** [[vulnerabilities/008-http_smuggling/http-smuggling|entry point]] · [[vulnerabilities/008-http_smuggling/labs/README|labs]]

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
- 📁 **Cómo explotar:** [[vulnerabilities/026-oauth/oauth|OAuth]] *(entry point incompleto)*

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
