# Ofuscación / Bypass de filtros

Colección de notas sobre **cómo ofuscar payloads** para saltar filtros, WAFs y
sanitizadores en distintos contextos de inyección. Un archivo por tipo.

## Índice

**Empieza por objetivo:** [encodings.md](encodings.md) tiene la tabla "🎯 Por objetivo"
que te manda al encoding y al archivo correcto según lo que estés atacando.

> **Navegación rápida:** cada nota abre con un **🔎 Índice de bypasses** (enlaces a cada
> técnica) y lleva `tags` en el frontmatter. Busca en el vault por tag —
> `#filter-bypass`, `#waf-bypass`, `#obfuscation`, o por contexto: `#xss`, `#sqli`,
> `#xxe`, `#javascript`, `#mxss`.

| Archivo | Contexto | De qué va |
|---------|----------|-----------|
| [encodings.md](encodings.md) | **Encodings (transversal)** | Cada codificación (URL, doble URL, HTML, XML, unicode, hex, octal, multiple, `CHAR()`) explicada, **con mapa por objetivo**. |
| [obfuscate.py](obfuscate.py) | **Script** | Aplica una lista ordenada de encodings a un payload: `python obfuscate.py "alert(1)" hex url`. `-l` lista todos. |
| [js-obfuscation.md](js-obfuscation.md) | **JavaScript** | Ejecutar JS cuando se filtran `()`, comillas, palabras clave. `eval`/`atob`/`btoa`, template literals, `${...}`. **El más completo.** |
| [xss-obfuscation.md](xss-obfuscation.md) | XSS (HTML/DOM) | Bypass de `()` filtrados, encoding `\xNN` / `\uNNNN` / entidades HTML, contextos de inyección. |
| [sql-obfuscation.md](sql-obfuscation.md) | SQL Injection | Bypass de espacios, comillas, keywords, comentarios, encoding, WAF. |
| [xxe-obfuscation.md](xxe-obfuscation.md) | XXE / XML | Ofuscar entidades, encoding, parameter entities, wrappers PHP. |
| [html-obfuscation.md](html-obfuscation.md) | HTML / atributos | Entidades, mayúsculas/minúsculas, atributos raros, mutación (mXSS). |

## Idea general (aplica a todos)

Un filtro casi siempre bloquea **caracteres o strings literales**. La ofuscación
consiste en **expresar lo mismo con una representación que el filtro no reconoce
pero el intérprete (navegador, motor SQL, parser XML) sí decodifica**:

1. **Encoding**: hex, unicode, URL, base64, entidades HTML/XML.
2. **Construcción dinámica**: montar el string/keyword en runtime (concatenación,
   `char()`, `atob()`, `String.fromCharCode`, `${...}`).
3. **Sintaxis alternativa**: llamar sin `()` (template literals, `throw`/`onerror`),
   comentarios en medio de keywords SQL, etc.
4. **Mutación (mXSS)**: dejar que el propio parser reescriba tu input a algo peligroso.

> Uso educativo / pentesting autorizado / CTF (PortSwigger, HTB, etc.).
