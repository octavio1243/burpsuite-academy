---
aliases:
  - Path Traversal wordlist
  - directory traversal wordlist
  - path-traversal-wordlist
  - wordlists de path traversal
tags:
  - vuln/path-traversal
  - wordlist
  - reference
---

# Path Traversal — Wordlists de detección

> Documento **agnóstico al negocio**: payloads listos para **Burp Intruder** que prueban el traversal contra **todas las profundidades y encodings** de `../`.
> Punto de entrada (teoría y escalera de bypass): [[vulnerabilities/010-path-transversal/path-transversal|entry point]].

## 🧮 Convención de variables

> [!tip] Reemplazá el placeholder antes de disparar
> En Burp Intruder marcás la posición con `§…§`; en estos archivos el nombre del archivo objetivo va con llaves.

| Variable | Qué es | Ejemplo |
| --- | --- | --- |
| `{FILE}` | El archivo que querés leer, **sin** el `../` inicial | `etc/passwd` · `windows/win.ini` |

> [!note] Cómo cargar `{FILE}` en Intruder
> Opción A — buscá y reemplazá `{FILE}` por `etc/passwd` en el `.txt` antes de cargarlo.
> Opción B — **Cluster bomb** con dos posiciones: el payload de la lista y `{FILE}` como segundo set.

## 📄 Las listas

| Archivo | Qué prueba |
| --- | --- |
| [`deep_traversal.txt`](deep_traversal.txt) | Escalera de profundidad (`../` × N) combinada con **encodings**: crudo, URL, doble URL, UTF-8 overlong, separadores `/` y `\`. Fuente: PayloadsAllTheThings. |

## ⚙️ Uso en Intruder

1. Marcá el parámetro que abre un archivo (`filename`, `file`, `path`, `document`, `download`, `template`, `image`).
2. Sustituí `{FILE}` por el objetivo (`etc/passwd`) o usalo como segundo payload set (cluster bomb).
3. Cargá el `.txt` como payload set.
4. **Encoding:** los payloads ya traen su encoding; **desactivá** "URL-encode these characters" para no re-encodear los `%2f` / `%252f`.
5. **Filtrá** el resultado por el canario **`root:x:0:0:`** (primera línea de `/etc/passwd`) en la columna de respuesta.

> [!tip] Orden mental (ver [entry point](path-transversal.md))
> `../` directo → ruta absoluta → anidado `....//` → URL / doble URL → UTF-8 overlong → `%00.png` / prefijo. Esta wordlist automatiza la parte de **profundidad + encoding**; el null byte y el prefijo de start-of-path los sumás a mano según el filtro.
