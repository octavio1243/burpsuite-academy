---
aliases:
  - Path Traversal labs
  - directory traversal labs
tags:
  - vuln/path-traversal
  - labs
  - portswigger
---

# Path Traversal — Labs de PortSwigger

Labs de la categoría **[File path traversal](https://portswigger.net/web-security/file-path-traversal)**: **6 labs** (1 Apprentice + 5 Practitioner). **Metodología general** → [[vulnerabilities/010-path-transversal/path-transversal|entry point]]. **Encodings / ofuscación** (los métodos pioneros para saltar filtros) → [[vulnerabilities/019-obfuscacion/encodings|encodings.md]] · [[vulnerabilities/019-obfuscacion/README|índice de ofuscación]].

> [!abstract] El vector es siempre el mismo
> Un parámetro lleva un **nombre de archivo** que el server abre del disco — casi siempre el **cargador de imágenes de producto** (`GET /image?filename=...` o `/loadImage?filename=`). Si podés meter **`../`** (o su equivalente ofuscado), **salís del directorio previsto** y leés cualquier archivo.

> [!important] 🎯 El objetivo NO cambia entre labs
> Los **6** piden lo mismo: **leer `/etc/passwd`** (lectura arbitraria de archivos del sistema). Lo único que cambia es el **filtro** que hay que saltar y, por lo tanto, el **encoding/truco**. En Windows el equivalente sería `..\..\..\windows\win.ini`.

---

## Tabla de labs

| # | Lab · nivel | Defensa que rompés | Truco · encoding | Payload que funcionó | Objetivo |
| --- | --- | --- | --- | --- | --- |
| 1 | [Simple case](https://portswigger.net/web-security/file-path-traversal/lab-simple) · **Apprentice** | ninguna | `../` directo | `../../../etc/passwd` | leer `/etc/passwd` |
| 2 | [Absolute path bypass](https://portswigger.net/web-security/file-path-traversal/lab-absolute-path-bypass) · **Practitioner** | bloquea `../` pero trata el nombre como **relativo a un dir por defecto** | **ruta absoluta** (no necesitás `../`) | `/etc/passwd` | leer `/etc/passwd` |
| 3 | [Stripped non-recursively](https://portswigger.net/web-security/file-path-traversal/lab-sequences-stripped-non-recursively) · **Practitioner** | **elimina `../`** … pero **una sola vez** | **secuencias anidadas** (al sacar el `../` del medio queda otro) | `....//....//....//etc/passwd` | leer `/etc/passwd` |
| 4 | [Superfluous URL-decode](https://portswigger.net/web-security/file-path-traversal/lab-superfluous-url-decode) · **Practitioner** | bloquea `../` y después hace **un URL-decode de más** | **doble URL encoding** (`/` → `%252f`) | `..%252f..%252f..%252fetc/passwd` | leer `/etc/passwd` |
| 5 | [Validate start of path](https://portswigger.net/web-security/file-path-traversal/lab-validate-start-of-path) · **Practitioner** | exige que el path **empiece** con `/var/www/images/` | **prefijás la carpeta esperada** y después salís con `../` | `/var/www/images/../../../etc/passwd` | leer `/etc/passwd` |
| 6 | [Validate file extension (null byte)](https://portswigger.net/web-security/file-path-traversal/lab-validate-file-extension-null-byte-bypass) · **Practitioner** | exige que termine en **`.png`** | **null byte** `%00` corta el string antes de la extensión | `../../../etc/passwd%00.png` | leer `/etc/passwd` |

---

## 🥷 Encodings y trucos clásicos (los "pioneros")

Cada filtro bloquea un **string literal** (`../`, `..`, `/`). La gracia es expresar lo mismo con una representación que el filtro no reconoce pero **el sistema de archivos sí resuelve**. Detalle general de cada encoding → [[vulnerabilities/019-obfuscacion/encodings|encodings.md]].

| Truco | `../` queda como… | Cuándo sirve | Ref |
| --- | --- | --- | --- |
| **URL encode** | `..%2f` · `%2e%2e%2f` | filtro que mira el `/` o el `.` literal | [[vulnerabilities/019-obfuscacion/encodings#1. URL encoding\|URL]] |
| **Doble URL encode** | `..%252f` | el server **decodifica dos veces** (lab 4) | [[vulnerabilities/019-obfuscacion/encodings#2. Double URL encoding\|doble URL]] |
| **Anidado (no-recursivo)** | `....//` · `..././` | el filtro strippea `../` **una vez** (lab 3) | — (no es encoding, es reconstrucción) |
| **UTF-8 overlong / no estándar** | `..%c0%af` (`%c0%af`=`/`) · `..%c1%9c` (`=\`) | parsers viejos que aceptan UTF-8 malformado | [[vulnerabilities/019-obfuscacion/encodings#5. Unicode escaping\|unicode]] |
| **Null byte** | `…/etc/passwd%00.png` | validación de **extensión** (lab 6) | — |
| **Backslash (Windows)** | `..%5c` · `..\..\` | back-end Windows | — |

> [!tip] Orden de prueba
> `../` directo → ruta **absoluta** → **anidado** `....//` → **URL / doble URL** → **UTF-8 overlong** → sumá **`%00.png`** si valida extensión y **prefijo** `/var/www/images/` si valida el inicio. Combinables entre sí.

---

## Peculiaridades por lab

- **Lab 2 (absoluto):** cuando bloquean `../`, muchas veces **no hace falta traversal**: si el nombre se resuelve contra un working dir, una **ruta absoluta** (`/etc/passwd`) apunta directo.
- **Lab 3 (anidado):** `....//` funciona porque el filtro borra el `../` **del medio** y lo que queda **se reconstituye** en `../`. Si fuera recursivo, no andaría → ahí pasás a encodings.
- **Lab 4 (doble URL):** `%252f` sobrevive el **primer** decode (queda `%2f`) y el **segundo** lo vuelve `/`. Es el caso escuela de [[vulnerabilities/019-obfuscacion/encodings#2. Double URL encoding|doble URL encoding]].
- **Lab 5 (start of path):** validan el **prefijo** sin **canonicalizar** primero → les das el prefijo que quieren y después `../` para escapar.
- **Lab 6 (null byte):** truco viejo de C/PHP: `%00` termina el string a nivel del SO → la comprobación de `.png` pasa pero el archivo abierto es el anterior al null.

## Patrones mentales

- **El objetivo es leer un archivo del sistema** (`/etc/passwd`, `win.ini`, configs, claves) — no RCE. Si querés más impacto, encadená con otra vuln.
- **Punto de inyección típico:** cualquier parámetro que termine abriendo un archivo (`filename`, `file`, `path`, `document`, `folder`, `template`, `download`).
- **Si un encoding no cuela, subí un nivel de ofuscación** (URL → doble URL → UTF-8 overlong) y combiná con prefijo/null byte según el filtro.
- **Chuleta de encodings completa** (y `obfuscate.py` para automatizar) → [[vulnerabilities/019-obfuscacion/README|carpeta de ofuscación]].
