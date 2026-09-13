---
aliases:
  - DOM-based 004 - DOM clobbering + cid
  - dom clobbering enable xss dompurify cid
tags:
  - vuln/dom-based
  - example
  - portswigger
---

# 004 — DOM clobbering para habilitar XSS (cuando DOMPurify filtra el JS)

> Lab: [Exploiting DOM clobbering to enable XSS](https://portswigger.net/web-security/dom-based/dom-clobbering/lab-dom-xss-exploiting-dom-clobbering) · **Expert** · técnica → [[vulnerabilities/025-dom-based/dom-based|entry point]]

## ¿Por qué acá? (no ejecutás JS propio)
- **Cuando el XSS está filtrado pero podés meter HTML:** metés `<a>`/`<form>` con `id`/`name` que **pisan (clobber) una variable global** que el JS usa mal (`window.x || {}`). Cambiás el comportamiento del JS **sin ejecutar JS tuyo**.
- **Por qué aparece:** hay **DOMPurify** (deja pasar `id`/`name`). El developer usa `window.defaultAvatar || {avatar:…}` → si clobbereás `defaultAvatar`, controlás el valor que termina en un sink.
- **El twist:** DOMPurify permite el protocolo **`cid:`**, que **no URL-encodea las comillas dobles** → colás un `"` para romper a XSS.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (PoC).

Patrón vulnerable en el target:
<pre class="payload"><code>let defaultAvatar = window.defaultAvatar || {avatar: '/resources/images/avatarDefault.svg'};
// ...usa defaultAvatar.avatar como atributo (sin re-sanitizar)</code></pre>

Dejá un **comentario** con dos `<a>` que clobberean `defaultAvatar.avatar`, usando `cid:` para colar la comilla:
<pre class="payload"><code>&lt;a id=defaultAvatar&gt;&lt;a id=defaultAvatar name=avatar href="cid:&amp;quot;onerror=<mark>alert(1)</mark>//"&gt;</code></pre>

Un **segundo comentario** cualquiera recarga la página y hace que el JS use la global ya clobbeada → dispara.

## Verificación
Al cargar la página con la global clobbeada, salta `alert(1)` → lab resuelto.

## Detalles que se pasan por alto
- **Dos `<a>` con el mismo `id`** se agrupan en una colección; el segundo con `name=avatar` es el que **pisa la propiedad `.avatar`**.
- El `&quot;` sobrevive porque **`cid:` no encodea las comillas** — ese es el corazón del bypass de DOMPurify.
- Variante hermana (lab 7): clobbear la propiedad **`attributes`** (`<form id=x tabindex=0 onfocus=print()><input id=attributes>`) para romper un filtro que recorre `element.attributes`.
- Repaso de la técnica y cuándo elegir clobbering vs. dangling markup → [[vulnerabilities/025-dom-based/dom-based|entry point]].
