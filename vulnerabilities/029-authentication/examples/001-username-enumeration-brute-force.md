---
aliases:
  - Authentication 001 - enumeración de usuario + fuerza bruta
  - username enumeration different responses
tags:
  - vuln/authentication
  - example
  - portswigger
---

# 001 — Enumeración de usuario + fuerza bruta del password

> Lab: [Username enumeration via different responses](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-different-responses) · **Apprentice** · técnica → [[vulnerabilities/029-authentication/authentication|entry point]]

## ¿Por qué acá? (el caso base)
- **Es el punto de partida del login:** el server te dice **demasiado**. Primero descubrís **quién existe**, después le tirás passwords. Todo lo demás en `/login` es esto con una complicación (timing, lockout, rate limit).
- **Por qué funciona:** el mensaje de error **cambia** según la fase que falla → `Invalid username` (usuario no existe) vs `Incorrect password` (usuario existe, password mal). Esa diferencia es el oráculo.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (host del lab, listas) + el **payload** (usuario/password candidato).

**Paso 1 — enumerar el usuario.** Mandá el `POST /login` a Intruder, marcá `username`, cargá la wordlist de candidates y filtrá por el error distinto:
<pre class="payload"><code>POST /login HTTP/1.1
Host: <mark>LAB.web-security-academy.net</mark>
Content-Type: application/x-www-form-urlencoded

username=<mark>§candidato§</mark>&password=x</code></pre>
El usuario válido es el que devuelve **`Incorrect password`** (los demás dan `Invalid username`), o el único con **length de respuesta distinta**.

**Paso 2 — fuerza bruta del password.** Fijás el `username` válido y ahora iterás el `password`:
<pre class="payload"><code>username=<mark>carlos</mark>&password=<mark>§candidato§</mark></code></pre>
El password correcto responde **302** (redirect a `/my-account`), el resto **200** con `Incorrect password`.

## Verificación
Entrás a `/my-account` como el usuario enumerado → lab resuelto. El request ganador se ve por el **status 302** (o el cambio de length) en la tabla de Intruder.

## Detalles que se pasan por alto
- **Ordená por length** en Intruder: la anomalía salta sola sin leer cada respuesta.
- Cuidado con el **punto final variable** del mensaje: si la diferencia es sutil usá **grep-match** (ver [Username enumeration via subtly different responses](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-subtly-different-responses)).
- Si hay **rate limit / lockout**, primero resolvés eso (`X-Forwarded-For`, array de passwords) — ver entry point, sección de bypass de fuerza bruta.
- Script propio para las dos fases: [[vulnerabilities/011-brute-force/login_userenum_password.py|login_userenum_password.py]].

→ Siguiente: [[vulnerabilities/029-authentication/examples/002-2fa-simple-bypass|002 · ya tenés las creds pero hay 2FA: salteá el paso]]
