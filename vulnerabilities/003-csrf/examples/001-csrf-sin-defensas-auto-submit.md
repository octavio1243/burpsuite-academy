---
aliases:
  - CSRF 001 - sin defensas (auto-submit)
  - csrf no defenses
tags:
  - vuln/csrf
  - example
  - portswigger
---

# 001 — CSRF sin defensas (form auto-submit)

> Lab: [CSRF vulnerability with no defenses](https://portswigger.net/web-security/csrf/lab-no-defenses) · **Apprentice** · técnica → [[vulnerabilities/003-csrf/csrf|entry point]]

## ¿Por qué acá? (el caso base)
- **Es el punto de partida:** hay una **acción con estado** (`change-email`) que se dispara con una request **predecible** y **solo** con la cookie de sesión. **No hay token, ni SameSite útil, ni Referer.** Todo lo demás es este ataque + una defensa que sortear.
- **Por qué funciona:** el navegador de la víctima adjunta la cookie de sesión **sola** al hacer la request cross-site → si el server no exige nada más, la acción se ejecuta con la identidad de la víctima.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (dominio del lab, tu email) + el endpoint del ataque.

La request legítima es un `POST /my-account/change-email` con `email=...`. Como no hay defensa, la forjás desde el exploter. Usá el HTML de [[exam/shortcuts/auto-submit-form|auto-submit]] apuntando al `change-email`:
<pre class="payload"><code>&lt;form method="POST" action="https://<mark>LAB.web-security-academy.net</mark>/my-account/change-email"&gt;
  &lt;input type="hidden" name="email" value="<mark>attacker@evil.com</mark>"&gt;
&lt;/form&gt;
&lt;script&gt;document.forms[0].submit();&lt;/script&gt;</code></pre>
Atajo en Burp: request → **Engagement tools → Generate CSRF PoC** → **Store** en el exploit server → **Deliver to victim**.

## Verificación
Entregás el PoC al víctima (o probás con **View exploit** logueado con tu cuenta): el email cambia al que pusiste → el lab pasa a **solved**. En un caso real, después pedís **reset de password** al email que controlás.

## Detalles que se pasan por alto
- El form manda `Content-Type: application/x-www-form-urlencoded` **sin JS necesario** para el envío (el `submit()` es solo para que sea automático).
- No hace falta que la víctima haga clic: `document.forms[0].submit()` dispara solo al cargar.
- Este PoC es el **molde** de todos los demás: los siguientes labs son este form + un truco para saltar una defensa.

→ Siguiente: [[vulnerabilities/003-csrf/examples/002-bypass-token-metodo|002 · hay token, pero la validación depende del método]]
