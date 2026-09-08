---
aliases:
  - XXE - vía subida de SVG
  - xxe file upload svg
  - xxe imagen
tags:
  - vuln/xxe
  - example
  - portswigger
---

# Ejemplo — XXE por subida de imagen (SVG)

> Lab: [Exploiting XXE via image file upload](https://portswigger.net/web-security/xxe/lab-xxe-via-file-upload) · **Practitioner** · técnica → [[vulnerabilities/006-xxe/xxe|entry point]] · relación → [[vulnerabilities/017-file-upload-vulnerabilities/README|file upload]]

**Qué demuestra:** un **SVG es XML**. Si una feature procesa imágenes SVG (avatar de comentario, adjunto), le metés `<!DOCTYPE>`+entidad y el server **renderiza el archivo con el contenido dentro**.

## Vector completo

**Archivo `exploit.svg`** (ya está en el repo → [[vulnerabilities/006-xxe/bitso.0whvrzxl.oti8.svg|bitso…svg]]):
```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE test [ <!ENTITY xxe SYSTEM "file:///etc/hostname" > ]>
<svg width="128px" height="128px" xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1">
  <text font-size="16" x="0" y="16">&xxe;</text>
</svg>
```

**Flujo (lab):**
1. Postear un comentario **subiendo este `.svg` como avatar**.
2. Volver al comentario → el avatar renderizado **muestra el `/etc/hostname`** como texto.
3. Si no se ve directo, abrir la URL de la imagen (`/files/avatars/exploit.svg`) → el contenido está dentro del SVG.

## Verificación
El texto del SVG muestra el hostname en vez de quedar vacío.

## Detalles que se pasan por alto
- **El `&xxe;` va dentro de un `<text>`** para que se renderice visible. Sin un elemento que lo muestre, el contenido se resuelve pero no lo ves.
- `standalone="yes"` no es obligatorio pero es el del payload canónico.
- Misma idea aplica a **DOCX/XLSX/PPTX** (son ZIP con XML adentro) y a cualquier procesador de imágenes/documentos que parsee XML. Un [[vulnerabilities/017-file-upload-vulnerabilities/README|upload]] que acepte estos formatos = superficie XXE.
- Si filtran `.svg` por extensión/Content-Type → aplicar bypasses de file upload.
