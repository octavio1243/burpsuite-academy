---
aliases:
  - WCP 004 - Host header injection en redirect
  - host header reflected in Location
tags:
  - vuln/web-cache-poisoning
  - example
  - portswigger
---

# 004 — Host Header Injection reflejado en el `Location` (gadget para cachear)

> Técnica → [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|entry point]] · base: **Host header attacks** → carpeta `vulnerabilities/016-host-header-injection/`

## Qué muestra
El **paso de descubrimiento** que conecta *Host header injection* con WCP: el **`Host` (con el puerto que inyectás) se refleja sin sanitizar** en el header `Location` de un redirect. Si esa respuesta **es cacheable**, el redirect envenenado se sirve a todos → poisoning del redirect.

## Request → Response

> `GET / HTTP/1.1`
> `Host: vulnerable-website.com:`==`1337`==

**⬇️ el puerto se refleja en el `Location`:**

> `HTTP/1.1 302 Moved Permanently`
> `Location: https://vulnerable-website.com:`==`1337`==`/en`
> `Cache-Status: miss`

## Por qué funciona
- La app **construye el `Location` a partir del `Host`** de la request, **sin validar** → todo lo que metas en `Host` (acá el puerto `:1337`) **vuelve reflejado** en el redirect.
- **`Cache-Status: miss`** te dice dos cosas: (1) la respuesta **pasa por caché** y (2) esta variante **aún no está cacheada** → es candidata a envenenar.
- Si el front-end deja pasar un `Host` **arbitrario** (no solo el puerto, sino otro dominio), el `Location` cacheado manda a **todas** las víctimas a **tu host**.

## Cómo explotarlo (weaponize)
1. **Confirmá el reflejo:** cambiá el `Host` (puerto o dominio) y verificá que aparece tal cual en `Location`.
2. **Confirmá cacheabilidad:** `Cache-Status`/`X-Cache` en `miss` → la respuesta entra a la caché.
3. **Envenená:** si podés inyectar un host completo (`Host: TU-exploit-server`) y queda cacheado, todo el que pida `/` recibe `Location: https://TU-exploit-server/en` → **redirect masivo** (phishing, robo de token en flujos OAuth, entrega de exploit).
4. Si solo entra el **puerto**, sirve igual para **client-side** / romper enlaces, y como prueba de que el `Host` se refleja.

## Verificación
- Reenviá la request y comprobá que el `Location` envenenado vuelve con `Cache-Status: hit`.

## Detalles que se pasan por alto
- **`Host` directo vs `X-Forwarded-Host`:** si el front normaliza/rechaza el `Host`, probá `X-Forwarded-Host` (ver [[vulnerabilities/030-web-cache-poisoning/examples/002-xfh-script-import|002]]) o doble `Host`.
- **El redirect es el gadget:** no siempre necesitás XSS; un `Location` cacheado hacia tu dominio ya es impacto (sobre todo encadenado con **OAuth** o **open redirect**).
- Este mismo reflejo del `Host` alimenta el **password reset poisoning** (el link del mail se arma con el Host) → [[vulnerabilities/029-authentication/authentication|Authentication → fase reset]].
- Base teórica del vector → carpeta `vulnerabilities/016-host-header-injection/`.
