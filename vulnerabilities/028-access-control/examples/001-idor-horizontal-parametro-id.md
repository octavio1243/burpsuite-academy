---
aliases:
  - Access Control 001 - IDOR horizontal por parámetro id
  - horizontal idor request parameter
tags:
  - vuln/access-control
  - example
  - portswigger
---

# 001 — IDOR horizontal: leer datos de otro usuario cambiando `id`

> Lab: [User ID controlled by request parameter](https://portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter) · **Apprentice** · técnica → [[vulnerabilities/028-access-control/access-control|entry point]]

## ¿Por qué acá? (el caso base horizontal)
- **Es el punto de partida del acceso horizontal:** un identificador de usuario viaja **en la request** y la app **no verifica** que ese id sea el tuyo → cambiándolo leés datos ajenos.
- **Por qué funciona:** `/my-account?id=wiener` te muestra *tu* cuenta; la app usa el valor del parámetro sin comprobar contra la sesión → poné el de otro y te devuelve **sus** datos (API key, email, etc.).

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (tu usuario → la víctima).

Logueado como wiener, andá a **My account** y mirá la URL. Cambiá el `id` por el de la víctima:
<pre class="payload"><code>GET /my-account?id=<mark>carlos</mark> HTTP/1.1
Host: LAB.web-security-academy.net
Cookie: session=...</code></pre>
La respuesta trae la página de cuenta de `carlos` con su **API key**.

## Verificación
El body de la respuesta contiene el `email` / `apiKey` de `carlos` (no el tuyo). Enviá esa API key → lab resuelto.

## Detalles que se pasan por alto
- El `id` puede ser un **username** (`carlos`) o un **GUID** aparentemente impredecible; si es GUID, suele estar **filtrado** en un blog post o perfil de la víctima → copialo de ahí.
- 🚩 Aunque la respuesta sea un **302**, **leé el cuerpo**: la fuga puede venir en el body del redirect, no en el status.

→ Siguiente: [[vulnerabilities/028-access-control/examples/002-vertical-admin-sin-proteger|002 · subir de rol: llegar a /admin sin ser admin]]
