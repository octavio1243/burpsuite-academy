---
aliases:
  - CSRF 004 - bypass SameSite Lax (method override)
  - csrf samesite lax bypass method override
tags:
  - vuln/csrf
  - example
  - portswigger
---

# 004 — Bypass de SameSite=Lax vía method override

> Lab: [SameSite Lax bypass via method override](https://portswigger.net/web-security/csrf/bypassing-samesite-restrictions/lab-samesite-lax-bypass-via-method-override) · **Practitioner** · técnica → [[vulnerabilities/003-csrf/csrf|entry point]]

## ¿Por qué acá? (la defensa ya no es token, es la cookie)
- Acá **no hay token CSRF**; la defensa es que la cookie de sesión es **SameSite=Lax**. Lax bloquea el envío de la cookie en **POST** cross-site, pero **sí** la manda en **GET de navegación top-level** (cuando la víctima "navega" a la URL).
- **Por qué funciona:** el framework acepta un **override de método** (`_method=POST`) → mandás un **GET** (que Lax permite y adjunta la cookie) y el server lo trata como el **POST** de `change-email`.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = tu dominio del lab + tu email. El truco es el parámetro <mark>_method=POST</mark> en un GET top-level.

Como es navegación top-level, no hace falta form: alcanza con redirigir la ventana a la URL GET con el override:
<pre class="payload"><code>&lt;script&gt;
  document.location = "https://<mark>LAB.web-security-academy.net</mark>/my-account/change-email?email=<mark>attacker@evil.com</mark>&amp;_method=POST";
&lt;/script&gt;</code></pre>
(Equivalente con `<form method="GET">` + `_method=POST` como campo oculto y auto-submit → ver [[exam/shortcuts/auto-submit-form|auto-submit]].)

## Verificación
En Repeater comprobás que un `GET /my-account/change-email?email=...&_method=POST` **cambia el email** (el server respeta el override). Entregás el PoC por el exploit server como **navegación top-level** (no `<img>`/iframe) → Lax adjunta la cookie → **solved**.

## Detalles que se pasan por alto
- Tiene que ser **navegación top-level** (`document.location`, click, form GET), **no** una subrequest (`<img src>`, iframe) → esas no cuentan como navegación y Lax no manda la cookie.
- Lax deja pasar cookies en GET incluso sin interacción **solo en los primeros ~120 s** tras setearse (regla de "Lax+POST" de Chrome); en el examen se ignora, pero explica falsos negativos.
- Escalón siguiente si la cookie es **Strict**: no sirve el override → hay que salir *desde el propio site* con un **redirect client-side** o un **subdominio hermano** (XSS/WebSocket) → [[vulnerabilities/003-csrf/csrf|entry point]].
