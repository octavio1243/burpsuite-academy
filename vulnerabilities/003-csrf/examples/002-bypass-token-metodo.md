---
aliases:
  - CSRF 002 - bypass de token por método
  - csrf token validation depends on method
tags:
  - vuln/csrf
  - example
  - portswigger
---

# 002 — Bypass de token: la validación depende del método

> Lab: [Token validation depends on request method](https://portswigger.net/web-security/csrf/bypassing-token-validation/lab-token-validation-depends-on-request-method) · **Practitioner** · técnica → [[vulnerabilities/003-csrf/csrf#🔎 Puntos flojos a verificar (bypass de token)|entry point]]

## ¿Por qué acá? (primera defensa: el token)
- Ahora **sí hay** parámetro `csrf` en el `POST /my-account/change-email`. Pero el token está **mal implementado**: el server **solo lo valida en POST**. Si mandás la misma acción por **GET**, no lo chequea.
- **Por qué funciona:** la validación está atada al método, no a la acción. Cambiar `POST`→`GET` conserva el efecto (cambiar email) pero esquiva el control.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = tu dominio del lab y tu email. Fijate que **no hay parámetro `csrf`**.

Probá primero en Burp Repeater: cambiá la línea de request a `GET /my-account/change-email?email=...` y **borrá** el `csrf`. Si devuelve 302/200 y cambia el email → la defensa depende del método. PoC:
<pre class="payload"><code>&lt;form method="GET" action="https://<mark>LAB.web-security-academy.net</mark>/my-account/change-email"&gt;
  &lt;input type="hidden" name="email" value="<mark>attacker@evil.com</mark>"&gt;
&lt;/form&gt;
&lt;script&gt;document.forms[0].submit();&lt;/script&gt;</code></pre>

## Verificación
En Repeater, la variante **GET sin token** responde igual que la POST con token (email cambiado) → confirmado. Entregás el PoC GET por el exploit server y el lab pasa a **solved**.

## Detalles que se pasan por alto
- La clave es **probar cambiar el método** antes de rendirse ante un token: `POST`→`GET` es el primer test.
- Un `<form method="GET">` manda los campos en la **query string**, no en el body → no necesitás `_method` acá (eso es de [[vulnerabilities/003-csrf/examples/004-bypass-samesite-lax-method-override|SameSite Lax]]).
- Si en GET **sigue** pidiendo token, probá el siguiente eslabón: **quitarlo** entero, o **reusar un token tuyo** válido ([[vulnerabilities/003-csrf/examples/003-token-no-atado-a-sesion|003]]).

→ Siguiente: [[vulnerabilities/003-csrf/examples/003-token-no-atado-a-sesion|003 · el token es válido pero no está atado a tu sesión]]
