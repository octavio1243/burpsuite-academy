---
aliases:
  - Open Redirect
  - open redirection
  - open-redirect
tags:
  - vuln/open-redirect
  - entrypoint
---

# Open Redirect

> **Cómo funciona la vuln en sí** (agnóstica). Sus **usos** (bypass de SSRF, robo de token OAuth, phishing) se explican en cada sección que la aprovecha y referencian acá.

> [!abstract] Qué es
> Un endpoint que **redirige (`3xx`) a una URL que vos controlás por un parámetro**. La app toma ese valor y lo mete en el header `Location` **sin validar el destino**.

## Cómo se ve
```http
GET /product/nextProduct?path=/product?productId=2 HTTP/1.1
```
```http
HTTP/1.1 302 Found
Location: /product?productId=2
```
Si cambiás `path` por `http://evil.com` y el `Location` pasa a apuntar **afuera** → es open redirect.

## Cómo detectarlo
1. **Buscá respuestas `3xx`** en el Proxy history y mirá el header **`Location`**.
2. **Buscá un parámetro cuyo valor termine dentro de ese `Location`.** Nombres típicos: `path`, `url`, `next`, `returnUrl`, `redirect`, `dest`, `continue`, `r`, `u`.
3. **Apuntalo afuera** con algo reconocible:
   ```
   ?path=http://TU-SUBDOMINIO.oastify.com
   ```
   Si te redirige **fuera del sitio** → open redirect. Confirmalo por el `Location` o con Collaborator (**Poll now**).

> [!tip] URL absoluta vs. ruta relativa (define para qué sirve)
> - Acepta **URL absoluta** (`http://host-arbitrario/...`) → podés **elegir el host** → sirve para bypass de SSRF y robo de token.
> - Solo acepta **rutas relativas** del mismo sitio → redirige pero **no elegís el host** → sigue siendo open redirect (útil para phishing dentro del dominio), pero **no** como pivote de SSRF.

## Para qué se usa (impacto)
- **Phishing / abuso de confianza:** una URL del dominio legítimo que termina en un sitio malicioso.
- **Robo de token OAuth:** open redirect en el `redirect_uri` desvía el `code`/token al atacante → [[vulnerabilities/026-oauth/oauth|OAuth]].
- **Bypass de whitelist en SSRF:** la whitelist ve una URL del propio sitio; el fetcher sigue el `302` hasta el host interno → [[vulnerabilities/007-ssrf/examples/005-bypass-open-redirect|SSRF ejemplo 005]] (ahí está el caso completo con el mermaid del `302`).

## Detalle clave
No es un "redirect especial del server": es el open redirect común. Lo que cambia según el caso es **quién sigue el `302`** — tu browser (phishing/OAuth) o el **cliente HTTP del server** (SSRF).

> [!note] Ver también
> - **Uso como bypass de SSRF** (request + payload + mermaid del flujo) → [[vulnerabilities/007-ssrf/examples/005-bypass-open-redirect|SSRF ejemplo 005]]
> - **Entry point SSRF** → [[vulnerabilities/007-ssrf/ssrf|ssrf]] · **OAuth** → [[vulnerabilities/026-oauth/oauth|oauth]]
