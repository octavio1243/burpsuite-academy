---
aliases:
  - WCP 007 - unkeyed query string
  - cache buster
  - discrepancias de parseo de path
tags:
  - vuln/web-cache-poisoning
  - example
  - portswigger
---

# 007 — Query string entero unkeyed (+ el cache buster)

> Lab: [Unkeyed query string](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-unkeyed-query) · **Practitioner** · técnica → [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|entry point]]

## Qué muestra
El **query string completo** queda **fuera** de la cache key (solo se keyea `host + path`). Si la app **refleja el query** en el HTML, inyectás ahí → la respuesta envenenada se cachea bajo `GET /` → le pega a **todos**. El detalle práctico: como el query **no cambia la key**, para testear necesitás un **cache buster**.

## El ataque

> `GET /?`==`'/><script>alert(1)</script>`==` HTTP/1.1`
> `Host: innocent-website.com`

**⬇️ el query (unkeyed) se refleja en el HTML (canonical/`og:url`) y se cachea bajo `GET /`:**

> `<link rel="canonical" href="https://innocent-website.com/?`==`'/><script>alert(1)</script>`==`"/>`

## El problema: no ves tu cambio
- **Keyed:** `GET /`. **Unkeyed:** `?loquesea`.
- Mandás tu payload, pero el caché te devuelve la **copia vieja** de `/` → no ves el reflejo hasta que expire.
- **Solución = cache buster:** algo que **SÍ** cambie la key para traer respuesta **fresca** en cada prueba. Al confirmar el payload, lo **quitás** para envenenar la key real.

## Cache busters (para testear limpio)

> Catálogo general (params + headers + parseo) → [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning#🧨 El cache buster (probar sin esperar ni ensuciar)|entry point]].
> 🟡 ==Resaltado== = el valor que **bumpeás** en cada intento (`1`→`2`→…).
> ⚠️ **En este lab el query NO sirve de buster** (`?cb=1`): el query **entero es unkeyed** → no cambia la key. Acá busteás por **header** o por **parseo del path**.

**1) Headers keyed inofensivos** (cada valor único = entrada nueva):
> `Accept-Encoding: gzip, deflate, `==`cachebuster1`==
> `Accept: */*, text/`==`cachebuster1`==
> `Cookie: cachebuster=`==`1`==
> `Origin: https://`==`cachebuster1`==`.vulnerable-website.com`

**2) Param Miner** → activá **"Add static/dynamic cache buster"** e **"Include cache busters in headers"** (mete el buster solo en cada request).

**3) Discrepancias de parseo** frontend vs backend — el caché ve un path distinto pero el backend resuelve el mismo (sirve de buster **y** para entregar bajo una URL que la víctima visita):

| Server | Truco |
| --- | --- |
| Apache | `GET //` |
| Nginx | `GET /%2F` |
| PHP | `GET /index.php/xyz` |
| .NET | `GET /(A(xyz)/` |

## Weaponize
1. Con **cache buster**, iterá hasta ver tu payload reflejado.
2. **Quitá el buster** → mandá contra `GET /` → queda cacheado → todos los que pidan `/` reciben el payload (`X-Cache: hit`).

→ Siguiente: [[vulnerabilities/030-web-cache-poisoning/examples/008-unkeyed-query-parameter|008 · Un parámetro unkeyed]]
