---
aliases:
  - XSS 002 - breakout de atributo y string JS
  - xss attribute javascript context breakout
tags:
  - vuln/xss
  - example
  - portswigger
---

# 002 — Romper el contexto: atributo y string JS

> Lab: [Reflected XSS into attribute with angle brackets HTML-encoded](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-attribute-angle-brackets-html-encoded) · [Reflected XSS into a JavaScript string with angle brackets HTML encoded](https://portswigger.net/web-security/cross-site-scripting/contexts/lab-javascript-string-angle-brackets-html-encoded) · **Apprentice** · técnica → [[vulnerabilities/002-xss/README|entry point]]

## ¿Por qué acá? (cuando no podés abrir tags)
- **El input no cae en HTML crudo:** cae **dentro de un atributo** (`value="..."`) o **dentro de un string JS**, y los `<>` van **HTML-encodeados**. No podés inyectar un tag nuevo.
- La clave: **identificar el contexto exacto** del reflejo y **romperlo con el carácter que sí pasa** (la comilla), no con `<>`.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = el carácter de breakout según el contexto.

**Contexto atributo** (`<input value="TU_INPUT">`) → cerrar la comilla + event handler (los `<>` no sirven):
<pre class="payload"><code><mark>"</mark> autofocus onfocus=<mark>"</mark>alert(1)</code></pre>
**Contexto string JS** (`var x = 'TU_INPUT';`) → cerrar la comilla del string y ejecutar:
<pre class="payload"><code><mark>'</mark>-alert(1)-<mark>'</mark></code></pre>
o cerrando la sentencia:
<pre class="payload"><code><mark>'</mark>;alert(1)//</code></pre>
**Si escapan `'` pero `\` pasa sin filtrar** → anulás el escape con backslash:
<pre class="payload"><code><mark>\</mark>'-alert(1)//</code></pre>

## Verificación
El `alert` dispara → confirmás que rompiste el contexto. Si no salta, revisá en la respuesta **cómo quedó exactamente** tu input (¿la comilla se codificó? ¿se escapó el `\`?).

## Detalles que se pasan por alto
- **`autofocus onfocus`** dispara sin interacción de la víctima (útil en atributo).
- En string JS **no necesitás `<>`**: el breakout es solo de comilla → por eso funciona aunque los `<>` estén encodeados.
- El truco cambia según **qué carácter lograron filtrar**: comilla escapada → salir del `<script>` entero (`</script><script>alert(1)</script>`).

→ Siguiente: [[vulnerabilities/002-xss/examples/003-dom-xss-source-sink|003 · DOM XSS siguiendo source → sink]]
