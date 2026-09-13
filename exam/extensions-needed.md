---
aliases:
  - extensiones examen
  - burp extensions
  - extensions needed
tags:
  - exam/setup
  - burp/extensions
---

# Extensiones y herramientas de Burp — las que TENÉS que usar en el examen

> **Objetivo: ahorrar tiempo.** Cada una automatiza un paso que a mano es lento o propenso a error.
> Instalá todas **antes** del examen desde **`Extensions → BApp Store`** (las de Kettle/PortSwigger están ahí). Las built-in (CSRF PoC, DOM Invader, Collaborator) ya vienen en Professional.

## 🔥 Las 3 que no estás usando (prioridad máxima)

> [!danger] 🚩 Si aparece la vuln, abrí la herramienta ANTES de hacerlo a mano
> - **CSRF** → **Generate CSRF PoC** (built-in).
> - **Web cache** → **Param Miner**.
> - **Request smuggling** → **HTTP Request Smuggler**.

### 1) CSRF PoC generator (built-in, Professional)
- **Para:** [[to-do-list/csrf|CSRF]] · [[vulnerabilities/003-csrf/csrf|entry point]].
- **Qué hace:** genera el HTML auto-submit desde cualquier request capturada. Te evita escribir el `<form>` a mano y respeta method/body/content-type.
- **Cómo:** click derecho sobre la request (Proxy/Repeater) → **Engagement tools → Generate CSRF PoC** → marcá *"Include auto-submit script"* → **Copy HTML** al exploit server.
- ⚠️ No sirve para los bypasses que necesitan CRLF/Set-Cookie o `_method` — ahí armás el PoC a mano ([[shortcuts/auto-submit-form|auto-submit]]).

### 2) Param Miner (James Kettle / PortSwigger)
- **Para:** [[to-do-list/web-cache-poisoning|Web Cache Poisoning]] · headers/params ocultos · [[to-do-list/content-discovery|content discovery]] · [[to-do-list/host-header|host header]].
- **Qué hace:** descubre **headers, params y cookies unkeyed/secretos** por fuerza bruta con wordlist. Es *el* paso que detecta el vector de cache poisoning.
- **Cómo:** click derecho → **Extensions → Param Miner → Guess headers** (o *Guess GET/POST params* / *Guess cookies*).
- **Imprescindible para caché:** activá **"Add static/dynamic cache buster"** e **"Include cache busters in headers"** → cada prueba usa una entrada fresca y no te engaña el hit.
- Detalle completo del flujo → [[to-do-list/web-cache-poisoning#3) Cómo usar Param Miner|to-do WCP §3]].

### 3) HTTP Request Smuggler (James Kettle / PortSwigger)
- **Para:** [[to-do-list/http-request-smuggling|Request Smuggling]] · [[vulnerabilities/008-http_smuggling/http-smuggling|entry point]].
- **Qué hace:** **detecta** CL.TE / TE.CL / TE.TE / CL.0 / H2 automáticamente (*Smuggle probe*), y **construye** el ataque respetando el `Content-Length` — que a mano es lo que más tiempo te come y donde más se falla.
- **Cómo:** click derecho → **Extensions → HTTP Request Smuggler → Smuggle probe** (detección) y **… → Smuggle attack (CL.TE / TE.CL)** para armar la request. Combinalo con **"Duplicate & fix content length"**.
- ⚠️ Desactivá **Update Content-Length** de Repeater cuando lo pide el ataque (o usá los scripts en `vulnerabilities/008-http_smuggling/scripts/`).

## 🔑 JWT Editor — casos puntuales (editar la cookie/token de sesión)

- **Para:** [[to-do-list/jwt|JWT]] · [[vulnerabilities/018-jwt-attacks/jwt-attacks|entry point]] · también el `id_token` de [[to-do-list/oauth|OAuth/OIDC]].
- **Base:** decodifica y **edita header/payload en Repeater** sin scriptear, y en la pestaña **JWT Editor Keys** creás/importás claves (RSA, EC, simétrica/HMAC) para firmar.
- **Flujo:** editás el claim en la pestaña **JSON Web Token** del mensaje → botón **Sign** (elegís la key) o **Attack** (ataques de un click).

> [!danger] 🚩 Qué caso usar según cómo verifica el server → [[vulnerabilities/018-jwt-attacks/jwt-attacks#🗺️ Mapa de vulnerabilidades (árbol de decisión)|árbol de decisión]]

| Caso (cómo verifica el server) | Qué hacés en JWT Editor | Botón |
| --- | --- | --- |
| **No verifica la firma** | Cambiás el claim (`sub→administrator`, `isAdmin:true`, `role:admin`) y reenviás | Editar payload → *no re-firmar* |
| **Acepta `alg:none`** | Setea `alg:none` y deja la firma vacía (`header.payload.`) | **Attack → "none" Algorithm** |
| **HS256 con secreto débil** | Crackeás el secreto (hashcat `-m 16500` / [[vulnerabilities/018-jwt-attacks/crack_jwt.py\|crack_jwt.py]]), lo cargás como **New Symmetric Key** y firmás | Keys → **New Symmetric Key** → **Sign** |
| **RS256 confía en `jwk` del header** | Generás **New RSA Key** y la embebés en el header; firmás con tu privada | **Attack → Embedded JWK** |
| **RS256 confía en `jku` (URL)** | Publicás tu **JWK Set** en el exploit server, apuntás `jku` ahí, firmás con tu RSA | Keys → *Copy as JWK* + editar header → **Sign** |
| **`kid` es una ruta de archivo** | Path traversal en `kid` a un archivo conocido (`/dev/null` → vacío) y firmás con esa key "predecible" | Editar header → **Sign** (key simétrica del archivo) |
| **No fija el `alg` + pública expuesta** | **Algorithm confusion RS256→HS256**: usás la pública (`/jwks.json`) como **secreto HMAC** | Keys → **New Symmetric Key** (desde PEM) → **Sign HS256** |

> [!tip] 💡 Dónde sale la pública para algorithm confusion
> `/jwks.json` · `/.well-known/jwks.json`. Si no está publicada → derivarla de 2 JWT con `sig2n`/`rsa_sign2n` ([[vulnerabilities/018-jwt-attacks/jwt-attacks#En la Signature|entry point §Signature]]).

## 🧰 Resto del arsenal (por vuln)

| Extensión / Herramienta | Para qué vuln | Qué te ahorra | Cómo |
| --- | --- | --- | --- |
| **Hackvertor** | Transversal (**encoding**, WCP, hashing) | **Codificar/decodificar inline** con tags: `<@url_encode>`, `<@base64>`, `<@html_entities>`, `<@hex>`, **anidados** para saltar filtros/WAF; además hashing y el cache buster `<@random_num(10)/>` | Seleccionar texto en Repeater → menú **Hackvertor** → tag; o escribir el tag a mano. Ver [[to-do-list/web-cache-poisoning#4) Cache buster|cache buster]] |
| **Content Type Converter** | [[to-do-list/csrf\|CSRF]], APIs | Convierte **JSON ↔ x-www-form-urlencoded** de un click → clave para CSRF contra API REST | Click derecho → *Change content type* |
| **Paramalyzer** | Recon / [[to-do-list/content-discovery\|content discovery]] transversal | **Analiza TODOS los params ya vistos** en el tráfico: marca los **reflejados** (candidatos XSS/SSRF/open-redirect), agrupa por nombre, decodifica valores y **flaggea entropía alta** (tokens/secretos). Complementa a Param Miner (Miner *adivina* params ocultos; Paramalyzer *analiza* los que ya pasaron) | Navegás el sitio → pestaña **Paramalyzer → Analyze**. **Cuándo:** fase de recon, para no leer params a ojo request por request |
| **Turbo Intruder** | Race conditions, brute force | Envío masivo/paralelo (**single-packet attack**) que Intruder normal no da | Click derecho → *Send to turbo intruder* + script Python |
| **DOM Invader** (built-in, Burp Browser) | [[to-do-list/dom-based\|DOM XSS]], [[to-do-list/prototype-pollution\|Prototype Pollution]], postMessage | Encuentra sources/sinks y **prototype pollution** automáticamente | Activar en **Burp Browser → extensión DOM Invader** |
| **InQL Scanner** | [[to-do-list/graphql\|GraphQL]] | Introspection + genera queries/mutations listas | Click derecho → *Send to InQL* |
| **Collaborator Everywhere** | [[to-do-list/ssrf\|SSRF]], [[to-do-list/host-header\|Host header]] | Inyecta payloads de Collaborator en headers de todo el tráfico → pesca SSRF/host ciegos | Pasivo: navegás y revisás interactions |
| **Upload Scanner** | [[to-do-list/file-upload\|File Upload]] | Automatiza pruebas de bypass de tipo/extensión | Click derecho → *Active scan (Upload Scanner)* |

> [!tip] 💡 Regla de oro del examen
> Antes de pelear una vuln a mano, preguntate: **"¿hay una extensión que ya hace este paso?"**. CSRF PoC, Param Miner y HTTP Request Smuggler son las que más minutos te devuelven.

## 🧪 Labs para probar cada extensión (qué practicar)

> Labs concretos de PortSwigger para entrenar la herramienta **y** dónde la extensión **no alcanza** y tenés que extender a mano.

### CSRF PoC generator
Ambos usan **double-submit / token atado a cookie no-de-sesión** → el gadget es el **`search` que refleja en `Set-Cookie`** (CRLF).

| Lab | Qué probar | Rol de la extensión |
| --- | --- | --- |
| [Token duplicated in cookie](https://portswigger.net/web-security/csrf/bypassing-token-validation/lab-token-duplicated-in-cookie) | El server solo compara `csrf` del **body** == `csrf` de la **cookie**. Inyectás una cookie falsa y mandás el mismo valor en el body → coinciden → pasa | **Generate CSRF PoC** te arma el `<form>` base; **a mano** agregás el `<img>` con la inyección CRLF |
| [Token tied to non-session cookie](https://portswigger.net/web-security/csrf/bypassing-token-validation/lab-token-tied-to-non-session-cookie) | El `csrf` está atado a `csrfKey`, pero `csrfKey` **no** está atado a la sesión. Logueás como atacante, tomás **tu** par `csrfKey`+`csrf` válido y le seteás **tu `csrfKey`** a la víctima; el `session` sigue siendo el de ella | Igual: el generator da el form; sumás el `<img>` que setea `csrfKey` |

> [!danger] 🚩 Dónde el generator NO alcanza → lo agregás vos
> El PoC generator **no** hace la inyección de cookie. Después de generar el form, insertás el gadget CRLF antes del submit:
> ```html
> <!-- (a) setea la cookie CSRF en la víctima vía search + CRLF -->
> <img src="https://TARGET/?search=x%0d%0aSet-Cookie:%20csrf=fake%3b%20SameSite=None" onerror="submitForm()">
> <!-- lab 2: cambiá csrf= por csrfKey=TU-KEY -->
> ```
> Plantilla completa (setea cookie → `setTimeout` → submit) → [[vulnerabilities/003-csrf/csrf#3) CRLF → Set-Cookie|PoC CRLF del entry point]] · [[shortcuts/auto-submit-form|auto-submit]].

## 🔗 Checklist de instalación (pre-examen)
- [ ] Param Miner
- [ ] HTTP Request Smuggler
- [ ] Hackvertor
- [ ] JWT Editor
- [ ] Content Type Converter
- [ ] Turbo Intruder
- [ ] InQL Scanner
- [ ] Upload Scanner
- [ ] (Built-in ya presentes: CSRF PoC, DOM Invader, Collaborator)
