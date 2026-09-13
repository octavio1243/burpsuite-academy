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

## ✅ Vulnerabilidades (Stage 2) — por prioridad

| # | Vulnerabilidad | 🚩 Señal detonante | Qué probar |
|---|---|---|---|
| 1 | 🎣 **CSRF — Account Takeover** | 🚩 Existe una **acción relevante del admin** que forjar (cambiar email/password) | [[exam/to-do-list/csrf\|Qué probar]] |
| 2 | 🔑 **Authentication / Password Reset** | 🚩 Hay **"recuperar contraseña"**; el reset/el cambio de password **mandan el `username`** → manipulable al admin | [[exam/to-do-list/authentication\|Qué probar]] |
| 3 | 🗄️ **SQL Injection** | 🚩 Hay **search/buscador** o input que consulta la BD | [[exam/to-do-list/sql-injection\|Qué probar]] (UNION saca user+pass del admin; o UPDATE/stacked sube tu rol) |
| 4 | 🛰️ **SSRF → panel admin interno** | 🚩 **Fetch server-side** (p.ej. `stockApi`) con filtro de host **bypasseable** (open redirect `next`/`path`) → alcanzás `localhost:6566/admin` | [[exam/to-do-list/ssrf\|Qué probar]] (chain open-redirect → panel admin → borrar/crear admin) |
| 5 | 🎫 **JWT** | 🚩 La sesión **es un JWT** → cambiar `sub`/`role` a administrator | [[exam/to-do-list/jwt\|Qué probar]] |
| 6 | 🧪 **Prototype Pollution (client-side)** | 🚩 **`__proto__`** en query/JSON cambia el comportamiento | [[exam/to-do-list/prototype-pollution\|Qué probar]] |
| 7 | 🧩 **API Testing / Mass Assignment** | 🚩 Endpoints **API (JSON)** con update de perfil | [[exam/to-do-list/api-testing\|Qué probar]] (`"isAdmin":true`/`roleid=2` → auto-escalada) |
| 8 | 🔓 **Access Control (IDOR)** | 🚩 Peticiones con **`username`/`id`/`role`** manipulable → vertical o horizontal→vertical | [[exam/to-do-list/access-control\|Qué probar]] |
| 9 | 🕸️ **GraphQL API Endpoints** | 🚩 Endpoint **GraphQL** (InQL) | [[exam/to-do-list/graphql\|Qué probar]] |
| 10 | 🔀 **CORS** | 🚩 `ACAO` refleja tu `Origin`/`null`/subdominio **+ `Allow-Credentials: true`** | [[exam/to-do-list/cors\|Qué probar]] |
| 11 | 🧠 **Business Logic** | 🚩 Un **flujo multipaso** (registro/login/checkout) o un **endpoint de doble uso** → saltar pasos, cambiar `username`, o email del **dominio admin** | [[exam/to-do-list/business-logic\|Qué probar]] (state machine · weak isolation · email dominio admin) |

### 🔻 Menos relevante en Stage 2

| Vulnerabilidad | 🚩 Señal detonante | Qué probar |
|---|---|---|
| 🧬 **XSS (Cross-Site Scripting)** | 🚩 **`.js` nuevos** al estar logueado / en zonas del admin | [[exam/to-do-list/xss\|Qué probar]] |
| 🌳 **DOM-Based** | 🚩 `.js` nuevos contra el admin con `postMessage`/`eval`/`addEventListener("message"` | [[exam/to-do-list/dom-based\|Qué probar]] |
| 🖱️ **Clickjacking** | 🚩 Acción clickeable del admin **+ página enmarcable** (sin `X-Frame-Options`/`frame-ancestors`) **+ víctima** | [[exam/to-do-list/clickjacking\|Qué probar]] |
| 📦 **HTTP Request Smuggling** | 🚩 *Smuggle probe*; la víctima activa suele ser el **admin** | [[exam/to-do-list/http-request-smuggling\|Qué probar]] |
| 🌐 **Web Cache Poisoning** | 🚩 `X-Cache`/`Age`/`Vary`/`Cache-Control` en la respuesta | [[exam/to-do-list/web-cache-poisoning\|Qué probar]] |
| 🏠 **HTTP Host Header** | 🚩 Panel **"accesible solo localmente"** (`Host: localhost` lo abre) · **routing** al interno (`localhost:6566`) · o **pisar el `Host`** del reset/cache-JS **contra el admin** | [[exam/to-do-list/host-header\|Qué probar]] (auth bypass `localhost` · routing-based SSRF · delivered al admin) · → [[exam/to-do-list/ssrf\|SSRF]] |
| 🪪 **OAuth** | 🚩 El login **usa OAuth** | [[exam/to-do-list/oauth\|Qué probar]] |
| 🧷 **Insecure Deserialization** *(último recurso)* | ⚠️ La cookie de sesión es un **objeto serializado** (PHP `O:` · Java `rO0`) y **agotaste** lo normal | [[exam/to-do-list/insecure-deserialization\|Qué probar (Stage 2)]] |
| 🧪 **Prototype Pollution (server-side)** *(último recurso)* | ⚠️ Un **update de perfil/datos (JSON)** que mergea sin sanear y **agotaste** mass assignment/IDOR → probá `"__proto__":{"isAdmin":true}` / `role` | [[exam/to-do-list/prototype-pollution\|Qué probar (escalada)]] |
| 🔎 **Information Disclosure (TRACE → header de auth)** *(caso borde)* | ⚠️ `/admin` restringido por **IP/header interno**: `TRACE /admin` refleja `X-Custom-IP-Authorization` → spoofealo a `127.0.0.1` | [[exam/to-do-list/content-discovery\|Qué probar]] · [lab](https://portswigger.net/web-security/information-disclosure/exploiting/lab-infoleak-authentication-bypass) |

---

> [!success] Salida del Stage 2
> Sesión/credenciales de **administrador** → usar para el **Stage 3**.
