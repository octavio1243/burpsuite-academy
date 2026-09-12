---
aliases:
  - to-do SSRF
tags:
  - exam/to-do
  - vuln/ssrf
---

# SSRF — Qué probar

> Técnica → [[vulnerabilities/007-ssrf/ssrf|entry point]] · labs → [[vulnerabilities/007-ssrf/labs/README|labs]]

## 🚩 Flags

> [!danger] 🚩 ¿Está?
> Un parámetro hace **fetch server-side**, un **Host header injection** llega a un oastify, o **`localhost:6566` responde**.

> [!tip] 📍 El servicio de interés está en `localhost:6566`
> Primer objetivo: ¿es alcanzable **`http://localhost:6566/`** desde el server? Navegá desde ahí (endpoints internos, o `file://` al secreto).

## 🎯 Objetivo (Stage 3)
- Pegarle a **`localhost:6566`** o leer **`/home/carlos/secret`** por `file://`.

## ♾️ Independiente del stage
- [ ] Parámetro-URL → `http://localhost:6566/` · `file:///home/carlos/secret`.
- [ ] **`Referer`** → puede haber analytics que lo visite (SSRF ciego) → Collaborator + Poll now → [[vulnerabilities/007-ssrf/examples/006-ssrf-ciego-deteccion-oob|006]].
- [ ] **Path traversal** en la URL interna hasta el fichero.
- [ ] Bypass de filtros: IP encoding, redirect, `@`, `#`, DNS rebinding.
- [ ] **Filtro que no cede → open redirect** (funcionalidad "next/returnUrl" que cae en `Location:`) → apuntá a `localhost:6566` → [[vulnerabilities/open-redirect/README|Open Redirect]] · [[vulnerabilities/007-ssrf/examples/005-bypass-open-redirect|005]].

## 🔗 Referencias
- [[vulnerabilities/007-ssrf/ssrf|entry point]] · [[vulnerabilities/007-ssrf/labs/README|labs]] · Host header → carpeta `vulnerabilities/016-host-header-injection/`
