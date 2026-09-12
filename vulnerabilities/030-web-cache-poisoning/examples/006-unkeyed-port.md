---
aliases:
  - WCP 006 - unkeyed port
  - puerto no cacheable pisa reflexion
tags:
  - vuln/web-cache-poisoning
  - example
  - portswigger
---

# 006 — Unkeyed port (el puerto pisa una reflexión)

> Técnica → [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|entry point]] · se apoya en [[vulnerabilities/030-web-cache-poisoning/examples/004-host-header-injection-redirect|004 (Host en el redirect)]]

## Qué muestra
El **puerto del `Host` normalmente NO forma parte de la cache key**, pero la app suele **reflejar el `Host` completo (con puerto)** en cosas como el `Location`. Entonces metés tu payload **en el puerto**: cambia la respuesta (la reflexión) **sin cambiar la key** → se cachea envenenado.

## Request → Response

```http
GET / HTTP/1.1
Host: vulnerable-website.com:PAYLOAD
```

```http
HTTP/1.1 302 Moved Permanently
Location: https://vulnerable-website.com:PAYLOAD/en
Cache-Status: miss
```

## Por qué funciona
- **Keyed:** `host` + `path` (p. ej. `vulnerable-website.com/`). **Unkeyed:** el **puerto** que va después de los dos puntos.
- La app arma el `Location` con el `Host` **tal cual** (incluido el puerto) → todo lo que metas en el puerto **se refleja**.
- Como el puerto **no entra en la key**, la respuesta con tu payload queda cacheada bajo la **misma** key que piden las víctimas.

## Cómo explotarlo (weaponize)
1. Confirmá que el puerto se refleja: `Host: vulnerable-website.com:12345` → `Location: ...:12345/en`.
2. Meté un payload que rompa el contexto de la reflexión (si el `Location`/reflejo termina en HTML) o que arme un redirect útil.
3. Verificá cacheabilidad (`Cache-Status: miss` → entra a caché) y envenená sin cache buster.

## Detalles que se pasan por alto
- Es la **versión "unkeyed" del [[vulnerabilities/030-web-cache-poisoning/examples/004-host-header-injection-redirect|004]]**: ahí veías que el `Host` se refleja; acá el detalle es que **el puerto puntualmente no se keyea**, así que es el lugar ideal para colar el payload.
- Sirve tanto para **pisar un `Location`** (redirect masivo) como para **reflexiones en el body**.
- Si el frontend **normaliza** o descarta el puerto, no anda → probá `X-Forwarded-Host` ([[vulnerabilities/030-web-cache-poisoning/examples/002-xfh-script-import|002]]).

→ Siguiente: [[vulnerabilities/030-web-cache-poisoning/examples/007-unkeyed-query-string-cachebuster|007 · Query string unkeyed + cache buster]]
