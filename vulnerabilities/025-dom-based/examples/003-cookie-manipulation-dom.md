---
aliases:
  - DOM-based 003 - cookie manipulation
  - dom based cookie manipulation xss
tags:
  - vuln/dom-based
  - example
  - portswigger
---

# 003 — DOM-based cookie manipulation (envenenás `document.cookie` → XSS en la carga siguiente)

> Lab: [DOM-based cookie manipulation](https://portswigger.net/web-security/dom-based/cookie-manipulation/lab-dom-cookie-manipulation) · **Practitioner** · técnica → [[vulnerabilities/025-dom-based/dom-based|entry point]]

## ¿Por qué acá? (source en 2 tiempos)
- **El source no está en la URL directa del sink:** un valor de la URL se guarda en `document.cookie` (`lastViewedProduct`) en **una** carga y se **escribe en el HTML** en la **siguiente**. El truco es el **iframe que se recarga**.
- **Por qué funciona:** la cookie se pinta sin sanitizar → si la envenenás con HTML, al reusarse ejecuta. Es "XSS vía cookie".

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (target + PoC).

En el **exploit server**, un `<iframe>` que primero **envenena** la cookie y en `onload` redirige al home (donde la cookie se pinta):
<pre class="payload"><code>&lt;iframe src="https://<mark>TARGET</mark>.web-security-academy.net/product?productId=1&amp;'&gt;&lt;script&gt;<mark>print()</mark>&lt;/script&gt;"
  onload="if(!window.x)this.src='https://<mark>TARGET</mark>.web-security-academy.net';window.x=1;"&gt;
&lt;/iframe&gt;</code></pre>

Primera carga: setea `lastViewedProduct` con el `'><script>print()</script>`. Segunda carga (el `onload` cambia el `src` al home): la cookie se escribe en el HTML → ejecuta.

**Store** → **Deliver exploit to victim**.

## Verificación
El `print()` salta al recargarse el iframe en el home → lab resuelto. Confirmá la visita por el **Access log**.

## Detalles que se pasan por alto
- El `if(!window.x)…;window.x=1;` evita un bucle infinito de recargas (solo redirige una vez).
- El payload va **URL-encodeado** dentro del `src` del iframe; la comilla `'` cierra el atributo donde se refleja la cookie.
- A diferencia de un XSS reflejado normal, el disparo está **partido en dos requests** → por eso hace falta el iframe que se auto-recarga.

→ Siguiente: [[vulnerabilities/025-dom-based/examples/004-dom-clobbering-cid|004 · cuando el XSS está filtrado (DOMPurify) → DOM clobbering]]
