---
aliases:
  - to-do XXE
tags:
  - exam/to-do
  - vuln/xxe
---

# XXE — Qué probar

> Técnica → [[vulnerabilities/006-xxe/xxe|entry point]] · labs → [[vulnerabilities/006-xxe/labs/README|labs]] · ejemplos 001–008 · scripts → [[vulnerabilities/006-xxe/scripts/README|gen_svg_xxe.py]]

## 🚩 Flags

> [!danger] 🚩 ¿Está?
> **Algo parsea XML:** envío de XML directo (stock check), SOAP, o carga de **SVG / DOCX / XLSX**.

> [!tip] 💡 Dónde probar (siendo admin)
> **Subir avatar/imagen** → SVG con entidad (`gen_svg_xxe.py -r file:///home/carlos/secret`) = el más jugoso. También: stock check (cambiar `Content-Type` a `application/xml`), import/export del panel, `username` del delete-user.

## 🎯 Objetivo (Stage 3)
- Leer **`/home/carlos/secret`** vía `file://` (o escalar a SSRF a `localhost:6566`).

## ♾️ Independiente del stage
- [ ] **Refleja** → entidad in-band `file:///home/carlos/secret` → [[vulnerabilities/006-xxe/examples/001-leer-archivo-in-band|001]].
- [ ] **Ciego** → OOB ([[vulnerabilities/006-xxe/examples/005-xxe-ciego-callback-oob|005]]) → exfil con **DTD externo** ([[vulnerabilities/006-xxe/examples/006-xxe-ciego-exfiltrar-con-dtd-externo|006]]).
- [ ] Rompe la exfil → **error-based** ([[vulnerabilities/006-xxe/examples/007-xxe-ciego-error-based-con-dtd-externo|007]]); sin salida → **DTD local** ([[vulnerabilities/006-xxe/examples/008-xxe-ciego-reutilizar-dtd-local|008]]).
- [ ] **No controlás el XML** → **XInclude** ([[vulnerabilities/006-xxe/examples/003-xinclude-sin-controlar-el-xml|003]]).
- [ ] **XXE → SSRF** a `localhost:6566` ([[vulnerabilities/006-xxe/examples/002-xxe-a-ssrf-metadata-cloud|002]]).

## 🔗 Referencias
- [[vulnerabilities/006-xxe/xxe|entry point]] · [[vulnerabilities/006-xxe/labs/README|labs]] · ejemplos 001–008
