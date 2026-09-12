---
aliases:
  - to-do Access Control
tags:
  - exam/to-do
  - vuln/access-control
---

# Access Control (IDOR) — Qué probar

> Técnica → [[vulnerabilities/028-access-control/access-control|entry point]] · labs → [[vulnerabilities/028-access-control/labs/README|labs]]

## 🚩 Flags

> [!danger] 🚩 ¿Está?
> Peticiones con **`username` / `id` / GUID / `role`** manipulables (IDOR). No hay señal única → se prueba.

> [!warning] ⚠️ Leé el body aunque redirija
> `/my-account?username=carlos` puede responder **`302` al login pero con el body lleno** → leé el **cuerpo**, no el status.

## 🎯 Por stage

| Aspecto | 🟢 Stage 1 | 🔴 Stage 2 |
| --- | --- | --- |
| **Tipo** | horizontal | vertical / horizontal→vertical |
| **Objetivo** | leer datos de otra cuenta (`email`/`apiKey`/`password`) | llegar a **admin** o robar credenciales de admin |

## ♾️ Independiente del stage

**Horizontal (datos de otro):**
- [ ] **`/my-account?username=carlos`** (incluso sin loguear) → sus datos. Anda cuando la app confía en el `username` de la query.
- [ ] **`userId` filtrado** en comentarios/blog → `/my-account?username=<userId>` (puede ser `administrator`).
- [ ] Cambiar `id`/GUID en URL/params/cookies. GUID "impredecible" suele estar **filtrado** en un post.
- [ ] **IDOR en archivo estático** → `/download-transcript/N.txt` (incremental). 🚩 si hay live chat = FLAG (credenciales en el log).
- [ ] 🔁 **`GET` filtrado → cambiá el método:** `POST /my-account?username=administrator` (method-based bypass).

**Vertical (subir de rol):**
- [ ] **Cookie de rol** `Admin=false` → `true`.
- [ ] **Mass assignment** → `roleid=2` / `role` / `isAdmin` en un update de perfil (auto-escalada).
- [ ] **Bypass de plataforma:** `X-Original-URL`/`X-Rewrite-URL` a `/admin`; slash final; case; Spring `useSuffixPatternMatch` (`.anything`); `Referer: …/admin`.

## 🔗 Referencias
- [[vulnerabilities/028-access-control/access-control|entry point]] · [[vulnerabilities/028-access-control/labs/README|labs]]
