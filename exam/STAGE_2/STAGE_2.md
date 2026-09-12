# STAGE 2 — PRIVILEGE ESCALATION

> **Objetivo único:** escalar del usuario normal (Stage 1) a **administrador**.
> Ahora **la víctima activa que navega y está logueada es el administrator**. Cada vulnerabilidad es *un camino distinto* para **tomar su cuenta o su rol**.
> 🚩=`[!danger]` · 💡=`[!tip]` · ⚠️=`[!warning]`. El "qué probar" completo vive en `exam/to-do-list/<vuln>`.

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

> [!tip] ✅ ¿Hay víctima que visita tus entregas? (Access log)
> Entregá algo trivial por el exploit server → **IP distinta** en el Access log = hay bot admin → los ataques *delivered* (CSRF/XSS/clickjacking) son viables. **Solo tu IP** → el admin solo ve contenido in-app (⇒ stored XSS) o el camino es **auto-escalada** (mass assignment, IDOR, JWT).

---

## ✅ Vulnerabilidades (Stage 2)

### 🗄️ SQL Injection
> [!danger] 🚩 Hay **search/buscador** o input que consulta la BD

→ [[exam/to-do-list/sql-injection|Qué probar]] (S2: UNION saca user+pass del admin; o UPDATE/stacked sube tu rol)

### 🧬 Cross-Site Scripting (XSS)
> [!danger] 🚩 **`.js` nuevos** al estar logueado / en zonas del admin

→ [[exam/to-do-list/xss|Qué probar]]

### 🎣 CSRF
> [!danger] 🚩 Existe una **acción relevante del admin** que forjar (cambiar email/password)

→ [[exam/to-do-list/csrf|Qué probar]]

### 🖱️ Clickjacking
> [!danger] 🚩 Acción clickeable del admin **+ página enmarcable** (sin `X-Frame-Options`/`frame-ancestors`) **+ víctima**

→ [[exam/to-do-list/clickjacking|Qué probar]]

### 🌳 DOM-Based
> [!danger] 🚩 `.js` nuevos contra el admin con `postMessage`/`eval`/`addEventListener("message"`

→ [[exam/to-do-list/dom-based|Qué probar]]

### 🔀 CORS
> [!danger] 🚩 `ACAO` refleja tu `Origin`/`null`/subdominio **+ `Allow-Credentials: true`**

→ [[exam/to-do-list/cors|Qué probar]]

### 📦 HTTP Request Smuggling
> [!danger] 🚩 *Smuggle probe*; la víctima activa suele ser el **admin**

→ [[exam/to-do-list/http-request-smuggling|Qué probar]]

### 🔓 Access Control (IDOR)
> [!danger] 🚩 Peticiones con **`username`/`id`/`role`** manipulable → vertical o horizontal→vertical

→ [[exam/to-do-list/access-control|Qué probar]]

### 🔑 Authentication (incluye Password Reset)
> [!danger] 🚩 Hay **"recuperar contraseña"**; el reset/el cambio de password **mandan el `username`** → manipulable al admin

→ [[exam/to-do-list/authentication|Qué probar]]

### 🌐 Web Cache Poisoning
> [!danger] 🚩 `X-Cache`/`Age`/`Vary`/`Cache-Control` en la respuesta

→ [[exam/to-do-list/web-cache-poisoning|Qué probar]]

### 🏠 HTTP Host Header
> [!danger] 🚩 Panel **"accesible solo localmente"** (`Host: localhost` lo abre) · **routing** al interno (`localhost:6566`, confirmá con Collaborator) · o **pisar el `Host`** del reset/cache-JS **contra el admin**

→ [[exam/to-do-list/host-header|Qué probar]] (S2: auth bypass `localhost` · routing-based SSRF · delivered al admin)

### 🪪 OAuth
> [!danger] 🚩 El login **usa OAuth**

→ [[exam/to-do-list/oauth|Qué probar]]

### 🎫 JWT
> [!danger] 🚩 La sesión **es un JWT** → cambiar `sub`/`role` a administrator

→ [[exam/to-do-list/jwt|Qué probar]]

### 🧩 API Testing / Mass Assignment
> [!danger] 🚩 Endpoints **API (JSON)** con update de perfil

→ [[exam/to-do-list/api-testing|Qué probar]] (`"isAdmin":true`/`roleid=2` → auto-escalada)

### 🕸️ GraphQL
> [!danger] 🚩 Endpoint **GraphQL** (InQL)

→ [[exam/to-do-list/graphql|Qué probar]]

### 🧪 Prototype Pollution (client-side)
> [!danger] 🚩 **`__proto__`** en query/JSON cambia el comportamiento

→ [[exam/to-do-list/prototype-pollution|Qué probar]]

### 🧷 Insecure Deserialization *(último recurso)*
> [!warning] ⚠️ La cookie de sesión es un **objeto serializado** (PHP `O:` · Java `rO0`) y **agotaste** lo normal
> Reescribí atributos/tipos sin herramienta: `admin`→true / `access_token`→`i:0` (type juggling). Raro pero **posible y barato**.

→ [[exam/to-do-list/insecure-deserialization|Qué probar (Stage 2)]]

---

> [!success] Salida del Stage 2
> Sesión/credenciales de **administrador** → usar para el **Stage 3**.
