---
aliases:
  - Business Logic - oráculo de cifrado
  - Authentication bypass via encryption oracle
tags:
  - vuln/business-logic
  - example
  - portswigger
---

# Bypass de autenticación por oráculo de cifrado

> Lab: [Authentication bypass via encryption oracle](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-authentication-bypass-via-encryption-oracle) · **Expert** · técnica → [[vulnerabilities/015-business-logic/business-logic|entry point]]

## ¿Por qué acá? (un error que descifra por vos)
- **La suposición que rompés:** el dev asume que un mensaje de error es inofensivo. Pero el error de "email inválido" **refleja la cookie `notification` ya descifrada** → te regala un **oráculo de descifrado**, y el mismo campo email actúa como **oráculo de cifrado**.
- **Por qué funciona:** la cookie `stay-logged-in` cifra `username:timestamp`. Con cifrar/descifrar arbitrario forjás una cookie válida para `administrator` sin conocer la clave.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (tu ciphertext / el username objetivo).

1. Login `wiener:peter` con **"Stay logged in"** → obtenés la cookie `stay-logged-in` cifrada.
2. Descifrá tu propia cookie: pegá su valor en la cookie `notification` y disparás el error (comentario con email inválido). El error refleja el plaintext:
<pre class="payload"><code>Cookie: notification=<mark>&lt;tu stay-logged-in&gt;</mark>
→ error: ... <mark>wiener:1700000000</mark></code></pre>
3. Confirmado el formato `username:timestamp`, **cifrá** el del admin por el campo email (oráculo de cifrado):
<pre class="payload"><code>email=<mark>administrator:1700000000</mark></code></pre>
4. El prefijo `Invalid email address: ` contamina el bloque → usá el oráculo para **alinear a un borde de bloque de 16 bytes** y **strippear** ese prefijo, quedándote con el ciphertext limpio de `administrator:<timestamp>`.
5. Seteá ese ciphertext como tu `stay-logged-in` y navegá autenticado como admin:
<pre class="payload"><code>Cookie: stay-logged-in=<mark>&lt;ciphertext forjado&gt;</mark>
GET /admin/delete?username=carlos</code></pre>

## Verificación
Con la cookie forjada, el sitio te trata como `administrator` y `/admin/delete?username=carlos` borra a carlos → lab resuelto.

## Detalles que se pasan por alto
- **Dos oráculos en un mismo endpoint:** el email de un comentario **cifra** lo que mandás; la cookie `notification` reflejada en el error **descifra**.
- El trabajo fino es el **alineamiento de bloques** (16 bytes) para descartar el prefijo `Invalid email address: `.
- Es el único **Expert** de la categoría y el más "cripto": roza el brute de `stay-logged-in` de [[vulnerabilities/029-authentication/authentication|authentication]].

## 🔗 Relacionados
- [[vulnerabilities/015-business-logic/business-logic|entry point]] · [[vulnerabilities/015-business-logic/labs/README|labs]]
- Otras tomas de cuenta de Stage 2: [[vulnerabilities/015-business-logic/examples/lab-logic-flaws-authentication-bypass-via-flawed-state-machine|flawed state machine]] · [[vulnerabilities/015-business-logic/examples/lab-logic-flaws-weak-isolation-on-dual-use-endpoint|weak isolation]]
