---
aliases:
  - SQL Injection 001 - login bypass
  - sqli login bypass
tags:
  - vuln/sql-injection
  - example
  - portswigger
---

# 001 — Login bypass con comentario

> Lab: [SQL injection vulnerability allowing login bypass](https://portswigger.net/web-security/sql-injection/lab-login-bypass) · **Apprentice** · técnica → [[vulnerabilities/001-sql-injection/README|entry point]]

## ¿Por qué acá? (el caso base de Stage 1)
- **Es el foothold más barato:** el login arma algo como `... WHERE username='X' AND password='Y'`. Si comentás desde el `username`, matás la comprobación de la contraseña y entrás **sin saber la clave**.
- **Por qué funciona:** `--` (o `-- ` con espacio, o `#`) convierte el resto de la query en comentario → el `AND password=...` deja de existir.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (el usuario objetivo).

En el campo **`username`** del login mandá:
<pre class="payload"><code>username=<mark>administrator</mark>'--
password=cualquier-cosa</code></pre>

La consulta queda `... WHERE username='administrator'--' AND password='...'` → todo lo que sigue al `--` se ignora.

Si **no sabés** el nombre de usuario, forzá una condición siempre verdadera:
<pre class="payload"><code>username=<mark>' OR 1=1--</mark></code></pre>

## Verificación
- Entrás como **administrator** (o el primer usuario que devuelva la consulta con `OR 1=1`) sin contraseña válida → lab resuelto.

## Detalles que se pasan por alto
- Usá `-- ` **con espacio** o `#` (MySQL) si el `--` pelado no funciona: depende del motor.
- Con `' OR 1=1--` entrás como el **primer** registro de la tabla, que no siempre es el admin.
- El mismo campo `username` es una puerta: si no bypassa, probá [[exam/to-do-list/authentication|enum + brute force]].

→ Siguiente: [[vulnerabilities/001-sql-injection/examples/002-union-exfil-credenciales|002 · sacar credenciales del admin con UNION]]
