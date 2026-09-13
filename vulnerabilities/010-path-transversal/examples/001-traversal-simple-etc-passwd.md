---
aliases:
  - Path Traversal 001 - traversal simple a /etc/passwd
  - simple path traversal
tags:
  - vuln/path-traversal
  - example
  - portswigger
---

# 001 — Traversal simple contra `/etc/passwd`

> Lab: [File path traversal, simple case](https://portswigger.net/web-security/file-path-traversal/lab-simple) · **Apprentice** · técnica → [[vulnerabilities/010-path-transversal/path-transversal|entry point]]

## ¿Por qué acá? (el caso base)
- **Es el punto de partida:** un parámetro lleva un **nombre de archivo** que el server abre del disco (el **cargador de imágenes de producto**) y **no hay ningún filtro**.
- **Por qué funciona:** metés `../` y **salís del directorio previsto** → lectura arbitraria. Todo lo demás en esta categoría es este ataque + una complicación de filtro.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (host del lab) + el **payload** (la ruta traversal).

Interceptá la carga de imagen (`GET /image?filename=...`) y reemplazá el nombre por la ruta traversal:
<pre class="payload"><code>GET /image?filename=<mark>../../../etc/passwd</mark> HTTP/1.1
Host: <mark>LAB.web-security-academy.net</mark></code></pre>

## Verificación
La respuesta trae el **contenido de `/etc/passwd`** (líneas `root:x:0:0:...`) en lugar de los bytes de la imagen → lab resuelto.

## Detalles que se pasan por alto
- Con **tres** `../` alcanza en estos labs, pero podés poner de más: subir por encima de `/` **no falla**, el SO se queda en la raíz.
- El objetivo es **leer un archivo del sistema**, no RCE. Para más impacto, encadenás con otra vuln.
- En back-end **Windows** el equivalente sería `..\..\..\windows\win.ini`.

→ Siguiente: [[vulnerabilities/010-path-transversal/examples/002-bypass-ruta-absoluta|002 · bloquea `../` pero acepta ruta absoluta]]
