---
aliases:
  - SQL Injection 004 - filter bypass XML encoding
  - sqli waf bypass xml encoding
tags:
  - vuln/sql-injection
  - example
  - portswigger
---

# 004 — Bypass de WAF con XML encoding (stock check)

> Lab: [SQL injection with filter bypass via XML encoding](https://portswigger.net/web-security/sql-injection/lab-sql-injection-with-filter-bypass-via-xml-encoding) · **Practitioner** · técnica → [[vulnerabilities/001-sql-injection/README|entry point]]

## ¿Por qué acá? (el SQL es simple; lo que se practica es evadir el filtro)
- **Es el caso "con WAF":** el **stock check** manda un cuerpo **XML** y un WAF bloquea palabras como `UNION`/`SELECT`. La inyección en sí es un UNION normal; lo que cambia es que hay que **ofuscarla** para colarla.
- **Por qué funciona:** el parser XML **decodifica entidades numéricas** (`&#x53;` = `S`) *antes* de que la query llegue a la base → el WAF ve entidades, la base ve `SELECT`.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (el valor inyectado; luego lo codificás entero como entidades HTML).

El body original del **stock check** es XML con un `productId`:
<pre class="payload"><code>&lt;stockCheck&gt;
  &lt;productId&gt;<mark>1 UNION SELECT username || '~' || password FROM users</mark>&lt;/productId&gt;
  &lt;storeId&gt;1&lt;/storeId&gt;
&lt;/stockCheck&gt;</code></pre>

Como el WAF bloquea `UNION`/`SELECT`, **codificá el payload con entidades HTML numéricas** (usá el tab **Hackvertor** de Burp → *Encode → hex entities*). Queda algo así:
<pre class="payload"><code>&lt;productId&gt;<mark>1 &#x55;NION &#x53;ELECT ...</mark>&lt;/productId&gt;</code></pre>

## Verificación
- La respuesta del stock check devuelve el resultado del UNION (`username~password`) pese al WAF → copiás las creds del admin → lab resuelto.

## Detalles que se pasan por alto
- **No hace falta** codificar todo: alcanza con ofuscar las palabras filtradas (`UNION`, `SELECT`) para que el WAF no las reconozca.
- Hackvertor aplica el encoding **al enviar**, así ves el payload legible mientras editás.
- Otras ofuscaciones (comentarios inline, cambio de case, encoding) → [[vulnerabilities/019-obfuscacion/README|ofuscación]].
