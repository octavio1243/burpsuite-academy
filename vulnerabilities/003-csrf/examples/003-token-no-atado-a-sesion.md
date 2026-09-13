---
aliases:
  - CSRF 003 - token no atado a la sesión
  - csrf token not tied to session
tags:
  - vuln/csrf
  - example
  - portswigger
---

# 003 — Token válido pero no atado a la sesión

> Lab: [Token not tied to user session](https://portswigger.net/web-security/csrf/bypassing-token-validation/lab-token-not-tied-to-user-session) · **Practitioner** · técnica → [[vulnerabilities/003-csrf/csrf#🔎 Puntos flojos a verificar (bypass de token)|entry point]]

## ¿Por qué acá? (el token existe y se valida… pero es global)
- El server **sí** valida el `csrf`, y en cualquier método. La debilidad es otra: el token **no está ligado a quién sos**. Un token generado para **tu** cuenta de atacante es aceptado como válido para la **sesión de la víctima**.
- **Por qué funciona:** el pool de tokens es global (no `token ↔ sesión`). Como atacante tenés cuenta propia → generás un token legítimo y lo **precargás** en el PoC de la víctima.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = tu dominio + tu email + el **token que capturaste con tu cuenta** (no el de la víctima).

1. Logueado como **atacante**, cargá el form de `change-email`, **capturá un `csrf` válido** (Burp) y **no lo uses** (para que no se consuma).
2. Meté ese token fijo en el PoC contra la víctima:
<pre class="payload"><code>&lt;form method="POST" action="https://<mark>LAB.web-security-academy.net</mark>/my-account/change-email"&gt;
  &lt;input type="hidden" name="email" value="<mark>attacker@evil.com</mark>"&gt;
  &lt;input type="hidden" name="csrf" value="<mark>TOKEN_VALIDO_TUYO</mark>"&gt;
&lt;/form&gt;
&lt;script&gt;document.forms[0].submit();&lt;/script&gt;</code></pre>

## Verificación
En Repeater: tomá la request de la víctima y reemplazá su `csrf` por el **tuyo** → si el email cambia igual, el token **no está atado a la sesión**. Entregás el PoC y el lab pasa a **solved**.

## Detalles que se pasan por alto
- El token **parece** una defensa real (es válido, no vacío), pero la pregunta correcta es *"¿este token sirve para cualquier usuario?"* → reusá el tuyo para comprobarlo.
- No confundir con **token atado a cookie no-de-sesión** (`csrfKey`): ahí el token sí está ligado a *una* cookie, y el bypass es inyectarla por **CRLF Set-Cookie** → ver [[vulnerabilities/003-csrf/csrf#🔎 Puntos flojos a verificar (bypass de token)|entry point]].
- Si el token estuviera bien atado y sin bypass → cambiás de estrategia: **XSS que lea el token** o **dangling markup**.

→ Siguiente: [[vulnerabilities/003-csrf/examples/004-bypass-samesite-lax-method-override|004 · no hay token, pero la cookie es SameSite=Lax]]
