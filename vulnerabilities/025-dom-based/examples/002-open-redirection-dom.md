---
aliases:
  - DOM-based 002 - open redirection
  - dom based open redirect
tags:
  - vuln/dom-based
  - example
  - portswigger
---

# 002 — DOM-based open redirection (source `location` → sink `location.href`)

> Lab: [DOM-based open redirection](https://portswigger.net/web-security/dom-based/open-redirection/lab-dom-open-redirection) · **Practitioner** · técnica → [[vulnerabilities/025-dom-based/dom-based|entry point]]

## ¿Por qué acá? (el sink cambia el impacto)
- **Mismo patrón, otro sink:** un dato de la URL (param `url`) llega a `location.href`. **No es XSS** → es **redirección**. Es el ejemplo de que *el sink decide el impacto*.
- **Su valor real:** munición para **OAuth/SSO** → robar el `code`/`token` en el `redirect_uri` del admin. Como PoC alcanza con redirigir al exploit server.
- **Excepción a la regla:** este **no necesita exploit server**, es **solo una URL** directa.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (target + destino de la redirección).

El JS toma el param `url` (regex `/url=https?:\/\/.+/`) y hace `location.href = url`. Basta respetar el `https://` que pide el regex:
<pre class="payload"><code>https://<mark>TARGET</mark>.web-security-academy.net/post?postId=4&url=https://<mark>EXPLOIT</mark>.exploit-server.net/</code></pre>

Al abrir el post, el navegador salta a tu exploit server.

## Verificación
La navegación termina en `https://EXPLOIT.exploit-server.net/` (o el dominio que pusiste) → lab resuelto. Real: en un flujo OAuth, apuntás `url`/`redirect_uri` a tu server y capturás el `code`.

## Detalles que se pasan por alto
- El regex solo exige que el valor **empiece con `http://`/`https://`** → no valida el dominio.
- No hay iframe ni `postMessage`: la explotación es **la URL sola**, ideal cuando la víctima solo tiene que hacer clic.
- El impacto grave está en el encadenado → [[vulnerabilities/026-oauth/oauth|OAuth]] (robo de `code` vía `redirect_uri`).

→ Siguiente: [[vulnerabilities/025-dom-based/examples/003-cookie-manipulation-dom|003 · el source es la cookie que envenenás en una carga previa]]
