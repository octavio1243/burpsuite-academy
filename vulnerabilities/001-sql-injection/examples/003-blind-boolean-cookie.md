---
aliases:
  - SQL Injection 003 - blind booleano en cookie
  - blind sqli conditional responses
tags:
  - vuln/sql-injection
  - example
  - portswigger
---

# 003 — Blind booleano en la cookie `TrackingId`

> Lab: [Blind SQL injection with conditional responses](https://portswigger.net/web-security/sql-injection/blind/lab-conditional-responses) · **Practitioner** · técnica → [[vulnerabilities/001-sql-injection/README|entry point]]

## ¿Por qué acá? (no ves el dato → lo inferís)
- **Es el arquetipo blind:** la inyección está en la cookie **`TrackingId`**, cuyo resultado **no se imprime**. Lo único observable es que la página muestra u oculta "Welcome back" → eso es tu **oráculo booleano** (true/false).
- **Por qué importa para el examen:** en Stage 1 esta cookie dumpea credenciales del admin **antes** de entrar. Se automatiza carácter a carácter.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (condición, usuario, posición y char probado).

**1) Calibrar el oráculo** (una da "Welcome back", la otra no):
<pre class="payload"><code>TrackingId=xyz<mark>' AND '1'='1</mark>     → verdadero: aparece "Welcome back"
TrackingId=xyz<mark>' AND '1'='2</mark>     → falso: NO aparece</code></pre>

**2) Extraer la clave** carácter a carácter (subís la posición y probás cada char):
<pre class="payload"><code>TrackingId=xyz' AND (SELECT SUBSTRING(<mark>password</mark>,<mark>1</mark>,1) FROM <mark>users</mark> WHERE <mark>username='administrator'</mark>)='<mark>a</mark></code></pre>

Cuando la condición acierta el char, vuelve "Welcome back" → registrás la letra y avanzás de posición.

## Verificación
- Reconstruís la contraseña del **administrator** char a char, te logueás y resolvés el lab.
- Automatizalo con [[vulnerabilities/001-sql-injection/blind-sql-conditional-errors.py|el script blind]] o con Intruder (cluster bomb: posición × charset).

## Detalles que se pasan por alto
- Si **no hay** diferencia booleana visible, escalá el oráculo en orden: **error condicional** → **tiempo** (`pg_sleep`) → **OOB / Collaborator**. Mismo patrón `SUBSTRING`, distinto canal.
- La misma cookie `TrackingId` es puerta para [[exam/to-do-list/xss|robo de cookie]] / [[exam/to-do-list/insecure-deserialization|deserialización]].
- Ojo con el largo: acotá primero cuántos caracteres tiene la clave antes de barrer.

→ Siguiente: [[vulnerabilities/001-sql-injection/examples/004-filter-bypass-xml-encoding|004 · bypass de WAF con XML encoding]]
