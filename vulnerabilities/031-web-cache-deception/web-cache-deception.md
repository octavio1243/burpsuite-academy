---
aliases:
  - Web Cache Deception
  - web-cache-deception-entrypoint
  - WCD
  - cache deception
tags:
  - vuln/web-cache-deception
  - entrypoint
---

# Web Cache Deception — Punto de entrada

> Documento **agnóstico al negocio**: *cómo engañar a la caché para que guarde la respuesta privada de la víctima y después leerla yo*.
> **Lab por lab** (discrepancia · vector · dato robado) → [[vulnerabilities/031-web-cache-deception/labs/README|labs/README]].

> [!abstract] La idea en una línea
> La caché decide "guardar o no" con **reglas** (extensión `.js`/`.css`, directorio `/static`, nombre exacto `robots.txt`). Si la **caché** y el **origen** interpretan **distinto** una misma URL, crafteo un path que el **origen** enruta a un **endpoint dinámico con datos privados** pero que la **caché** clasifica como **estático y cacheable**. La respuesta con los datos de la víctima queda cacheada → **la pido yo y la leo**.

> [!danger] WCD ≠ WCP — no los confundas
> - **Web Cache Poisoning** → manipulo la **cache key** para que la caché sirva **mi payload a otros**. Ataco a terceros. → [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|WCP]]
> - **Web Cache Deception** → engaño a las **reglas de cacheo** para que la caché **guarde el contenido privado de la víctima** y **yo lo leo**. Robo datos de la víctima.
> Poisoning **escribe** en la respuesta de otros; deception **lee** la respuesta de otro.

## 📚 Referencias rápidas

- 🧪 **Labs** — 5 (1 Apprentice + 4 Practitioner), con **discrepancia · payload · dato robado** → [[vulnerabilities/031-web-cache-deception/labs/README|labs/README]]
- 📎 **Ejemplos concretos** (request/response comentados) → carpeta `examples/`:
  - [[vulnerabilities/031-web-cache-deception/examples/001-path-mapping|001 · Path mapping (`.js` sobre `/my-account`)]]
  - [[vulnerabilities/031-web-cache-deception/examples/002-path-delimiters|002 · Delimitadores de path (`;`, `%23`…)]]
  - [[vulnerabilities/031-web-cache-deception/examples/003-origin-server-normalization|003 · Normalización en el origen (`..%2f`)]]
  - [[vulnerabilities/031-web-cache-deception/examples/004-cache-server-normalization|004 · Normalización en la caché]]
  - [[vulnerabilities/031-web-cache-deception/examples/005-exact-match-cache-rules|005 · Reglas de nombre exacto (`robots.txt`)]]
- 🛠️ **Herramienta clave** — **Burp Repeater** (mandás los bytes crudos que el browser encodearía) + el **oráculo de caché** (`X-Cache`, `Age`, tiempos).
- 🔗 **Vecinos** — comparte "discrepancia de parseo caché ↔ origen" con [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|Web Cache Poisoning]]; el dato robado suele ser una sesión/CSRF token → se encadena con [[vulnerabilities/003-csrf/csrf|CSRF]] o robo de cuenta.

## 🎯 Qué se logra (y qué NO)

- **Leer datos privados de la víctima** que quedaron cacheados: datos de cuenta, **API key**, **CSRF token**, email, a veces la propia sesión.
- Con el **CSRF token** o la **API key** de la víctima → actúo en su nombre / entro a su cuenta. Si la víctima entregada es el **admin** → robo su secreto.
- ⚠️ **NO envenena la respuesta de otros** — no sirve mi payload a terceros (eso es WCP). Acá **yo leo**, no escribo.
- ⚠️ **NO ejecuta JS por sí solo** — el vehículo es **exfiltración de contenido cacheado**, no XSS. La escalada sale de *qué dato* robás y *a quién* se lo robás.

## 🧩 Qué recurso/dato se roba

El objetivo **siempre es un endpoint dinámico que refleja datos de la víctima**, servido bajo una URL que la caché creyó estática:

- **`/my-account`** (o `/account`, `/profile`) → nombre, email, **API key**, **CSRF token**.
- **Respuestas de API** autenticadas (`/api/...`) con datos de sesión.
- Cualquier página **per-user** con `Set-Cookie`/token que la regla de caché no debería tocar.

## 🧪 Metodología

1. **Encontrá un endpoint dinámico con datos privados** — típico `/my-account`. Confirmá que refleja algo sensible (API key, CSRF token, email) **estando logueado**.
2. **Detectá que hay caché y sus reglas** (cache oracle, 🚩 FLAG que anotás en el to-do):
   - `X-Cache: hit`/`miss`, `X-Cache-Hits`, `Cache-Status`, `Age` → indica si vino de caché.
   - `Cache-Control` (`public`, `max-age`), `Expires` → qué/cuánto se cachea.
   - **Diferencia de tiempo**: un `hit` responde mucho más rápido que un `miss`.
   - Probá qué **cachea**: pedí `/foo.js`, `/foo.css`, `/static/foo` y mirá si vuelven con `X-Cache: hit` → esas son las **reglas de cacheo**.
3. **Buscá la discrepancia caché ↔ origen** — cuatro familias (una por lab):
   - **Path mapping** → el origen usa rutas REST-style e **ignora** el segmento extra (`/my-account/wcd.js` sigue siendo `/my-account`).
   - **Delimitadores** → el origen **corta** el path en un char (`;`, `%23`, `%3f`, `%0a`) que la caché **no** trata como delimitador.
   - **Normalización en el origen** → el origen resuelve `..%2f` / dot-segments y "vuelve" al endpoint dinámico.
   - **Normalización en la caché** → la caché decodifica/resuelve el path y lo hace matchear una regla estática.
4. **Crafteá la URL** que el **origen** sirve **dinámica** (con los datos) pero la **caché** guarda como **estática**. Probá **desde Repeater** (el browser encodearía `;`, `<`, etc.).
5. **Cache buster al probar** — mientras testeás, usá una query única (`?cb=123`) para **no** cachear la URL que le vas a mandar a la víctima. Confirmás la técnica sin ensuciar.
6. **Entregá el link a la víctima** — la víctima **autenticada** abre tu URL → **su** respuesta privada queda cacheada bajo esa key → **pedís vos la misma URL** (sin sesión) y **leés sus datos** con `X-Cache: hit`.

### 🧩 Recon de discrepancias (payloads que probás)

- **Extensión estática** (path mapping): `GET /my-account/wcd.js` · `.css` · `.jpg`.
- **Delimitadores** (según parser): `;` · `%3b` · `%23` (`#`) · `%3f` (`?`) · `%0a` (`\n`) · `%00`.
  - `GET /my-account;wcd.js` · `GET /my-account%23wcd.js`.
- **Dot-segments encodeados** (normalización): `%2f` (`/`) · `%2e` (`.`) · `..%2f`.
  - `GET /static/..%2fmy-account` · `GET /my-account%2f%2e%2e%2fstatic/wcd.js`.
- **Nombres exactos** (exact-match): `robots.txt` · `favicon.ico` · `index.html` — combinás delimiter/normalización para caer en ese nombre.

## 🛡️ Prevención

- **Reglas de caché por respuesta, no solo por URL**: cachear solo si `Cache-Control` lo permite; respetar `Cache-Control: no-store`/`private` del origen.
- **Que caché y origen normalicen igual** la URL (mismo decode, misma resolución de dot-segments, mismos delimitadores) → sin discrepancia no hay engaño.
- **No cachear por extensión a ciegas**: verificar el `Content-Type` real, no adivinar por `.js`/`.css`.
- Endpoints con datos de usuario → `Cache-Control: no-store` **explícito**.

---

> [!tip] Reglas mentales
> - **WCD lee, WCP escribe:** si robás datos de otro = deception; si servís tu payload a otro = poisoning.
> - **Discrepancia = oro:** el bug vive en que caché y origen **parsean/normalizan distinto** la misma URL.
> - **Cache oracle primero:** `X-Cache`/`Age`/tiempo te dicen si hay caché y si pegaste el hit.
> - **Repeater, no browser:** el navegador encodea `;`,`#`,`?` → mandá los bytes crudos desde Burp.
> - **Cache buster al probar, link limpio al entregar:** no caches de más mientras testeás.
> - **Impacto = qué dato robás:** API key/CSRF token/sesión de la víctima o del admin.

> [!note] Relación con otras vulns
> - **Web Cache Poisoning** — misma raíz (discrepancia caché ↔ origen) pero objetivo inverso → carpeta `vulnerabilities/030-web-cache-poisoning/`.
> - **CSRF** — el dato robado suele ser un **CSRF token** → carpeta `vulnerabilities/003-csrf/`.
> - **Information disclosure** — WCD es una forma de **filtrar datos** privados vía caché → carpeta `vulnerabilities/014-information-disclousure/`.
> - **Access control** — robar la API key/sesión de la víctima puede dar acceso a lo que ella ve → carpeta `vulnerabilities/028-access-control/`.
