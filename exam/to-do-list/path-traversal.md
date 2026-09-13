---
aliases:
  - to-do Path Traversal
tags:
  - exam/to-do
  - vuln/path-traversal
---

# Path Traversal / LFI — Qué probar

> Técnica → [[vulnerabilities/010-path-transversal/path-transversal|entry point]] · labs → [[vulnerabilities/010-path-transversal/labs/README|labs]] · encodings → [[vulnerabilities/019-obfuscacion/encodings|encodings]] · ejemplos 001–004

## 🚩 Flags

> [!danger] 🚩 ¿Está?
> Un recurso (que el user normal no carga) servido con un parámetro tipo **`fileName`** / `file` / `path` / `download`.

## 🎯 Objetivo (Stage 3)
- Leer **`/home/carlos/secret`**.

## ♾️ Independiente del stage
- [ ] `../../../../home/carlos/secret` en el parámetro → [[vulnerabilities/010-path-transversal/examples/001-traversal-simple-etc-passwd|001 · traversal simple]].
- [ ] **Bypass:** ruta **absoluta** ([[vulnerabilities/010-path-transversal/examples/002-bypass-ruta-absoluta|002]]) · `....//` (strip no recursivo → [[vulnerabilities/010-path-transversal/examples/003-bypass-secuencias-strippeadas|003]]) · encoding `%2e` / doble `%252e` · **null byte** `%00.png` ([[vulnerabilities/010-path-transversal/examples/004-bypass-extension-null-byte|004]]) · **prefijo** `/var/www/images/` si valida el inicio.
- [ ] Orden: directo → absoluto → `....//` → URL/doble URL → UTF-8 overlong → `%00`/prefijo según filtro.

## 🔗 Referencias
- [[vulnerabilities/010-path-transversal/path-transversal|entry point]] · [[vulnerabilities/010-path-transversal/labs/README|labs]] · [[vulnerabilities/019-obfuscacion/encodings|encodings]]
- Ejemplos: [[vulnerabilities/010-path-transversal/examples/001-traversal-simple-etc-passwd|001 · simple]] · [[vulnerabilities/010-path-transversal/examples/002-bypass-ruta-absoluta|002 · absoluto]] · [[vulnerabilities/010-path-transversal/examples/003-bypass-secuencias-strippeadas|003 · `....//`]] · [[vulnerabilities/010-path-transversal/examples/004-bypass-extension-null-byte|004 · null byte]]
