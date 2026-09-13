---
aliases:
  - Path Traversal 004 - bypass de extensión con null byte
  - null byte extension bypass
tags:
  - vuln/path-traversal
  - example
  - portswigger
---

# 004 — Valida extensión `.png` → **null byte** `%00`

> Lab: [File path traversal, validation of file extension with null byte bypass](https://portswigger.net/web-security/file-path-traversal/lab-validate-file-extension-null-byte-bypass) · **Practitioner** · técnica → [[vulnerabilities/010-path-transversal/path-transversal|entry point]]

## ¿Por qué acá? (validación de sufijo)
- **Qué defensa rompés:** el server exige que el nombre **termine en `.png`** (u otra extensión de imagen).
- **Por qué funciona:** el **null byte `%00`** corta el string a nivel del SO (truco viejo de C/PHP) → la comprobación de `.png` **pasa**, pero el archivo que se abre es el que va **antes** del null.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = host del lab + el **payload**: traversal + `%00` + extensión que exige el filtro.

<pre class="payload"><code>GET /image?filename=<mark>../../../etc/passwd%00.png</mark> HTTP/1.1
Host: <mark>LAB.web-security-academy.net</mark></code></pre>

## Verificación
Devuelve **`/etc/passwd`** aunque la URL "termine" en `.png` → lab resuelto.

## Detalles que se pasan por alto
- El `%00` es la **codificación URL** del byte nulo; el server lo decodifica antes de abrir el archivo.
- **Combinable:** el `%00.png` se **suma** a cualquier otro truco (anidado, encoding, prefijo). Del orden de prueba, es lo que agregás **cuando valida extensión**.
- Si además valida el **inicio** del path, combinás con el prefijo: `/var/www/images/../../../etc/passwd%00.png`.

→ Volvé al [[exam/to-do-list/path-traversal|to-do de Path Traversal]] para el resto de trucos (doble URL, UTF-8 overlong, prefijo).
