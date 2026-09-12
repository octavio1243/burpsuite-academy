---
aliases:
  - to-do File Upload
tags:
  - exam/to-do
  - vuln/file-upload
---

# File Upload → RCE — Qué probar ⭐

> Técnica → carpeta `vulnerabilities/017-file-upload-vulnerabilities/` (shells listos + cheat-sheet de invocación)

## 🚩 Flags

> [!danger] 🚩 ¿Está?
> **Permite subir archivos** (típicamente solo el **admin**): avatar, adjunto, import.

## 🎯 Objetivo (Stage 3)
- Subir **web shell** → leer **`/home/carlos/secret`**.

## ♾️ Independiente del stage
- [ ] Subir shell PHP y pedirlo por GET desde `/files/avatars/…`.
- [ ] Shells listos:
  - `example_best.php?command=cat%20/home/carlos/secret` (system, salida limpia)
  - `exploit.php` (file_get_contents, **sin parámetro**)
- [ ] **Bypass** si filtran: extensión (blacklist), `Content-Type`, magic bytes, **polyglot**, path traversal en el nombre.

## 🔗 Referencias
- carpeta `vulnerabilities/017-file-upload-vulnerabilities/`
