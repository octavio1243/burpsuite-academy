---
aliases:
  - WCP 010 - fat GET
  - GET con body
  - X-HTTP-Method-Override
tags:
  - vuln/web-cache-poisoning
  - example
  - portswigger
---

# 010 — Fat GET (cuerpo en un GET) + method override

> Lab: [Fat GET request](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-fat-get) · **Practitioner** · técnica → [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|entry point]]

## Qué muestra
Un **GET que lleva body** ("fat GET"): el **caché keyea la URL** (`?param=innocent`), pero el **backend lee el parámetro del cuerpo** (`param=bad-stuff-here`). Discrepancia perfecta: la key queda "inocente", la respuesta va envenenada.

## Request → variantes

**Fat GET clásico** (la URL keyea `?param=innocent`; el body pisa):
> `GET /?param=innocent HTTP/1.1`
> `Content-Type: application/x-www-form-urlencoded`
>
> `param=`==`bad-stuff-here`==

**Si no lee el body → forzalo con method override:**
> `GET /?param=innocent HTTP/1.1`
> `X-HTTP-Method-Override: POST`
> `Content-Type: application/x-www-form-urlencoded`
>
> `param=`==`bad-stuff-here`==

**⬇️** el backend refleja el **valor del body** bajo la key `?param=innocent`.

## Por qué funciona
- El **caché** arma la key con la **URL** → ve `param=innocent`.
- El **backend** da **precedencia al valor del body** (`param=bad-stuff-here`) → refleja/usa tu payload.
- Con `X-HTTP-Method-Override: POST` empujás a la app a **tratar la request como POST** y leer el cuerpo, por si con GET puro lo ignora.
- La respuesta envenenada se cachea bajo la key **`?param=innocent`** → la reciben todos los que piden esa URL.

## Cómo explotarlo (weaponize)
1. Duplicá el parámetro: **inocente en la URL**, **payload en el body**.
2. Si no toma el body, sumá `X-HTTP-Method-Override: POST`.
3. Confirmá el reflejo del body en la respuesta y **cacheá** (sin buster).

## Detalles que se pasan por alto
- Ajustá bien `Content-Length` al largo real del body o algunos proxies lo cortan.
- No todos los servers aceptan body en GET → probar es barato; si anda, es oro.
- Emparienta con la familia de **discrepancias caché vs backend** ([[vulnerabilities/030-web-cache-poisoning/examples/009-parameter-cloaking|009]]).

→ Siguiente: [[vulnerabilities/030-web-cache-poisoning/examples/011-dynamic-resource-imports-css|011 · Contenido dinámico en imports (CSS)]]
