---
aliases:
  - to-do Access Control
tags:
  - exam/to-do
  - vuln/access-control
---

# Access Control (IDOR) — Qué probar

> Técnica → [[vulnerabilities/028-access-control/access-control|entry point]] · labs → [[vulnerabilities/028-access-control/labs/README|labs]] · ejemplos 001–004

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
- [ ] **`/my-account?username=carlos`** (incluso sin loguear) → sus datos. Anda cuando la app confía en el `username` de la query. → [[vulnerabilities/028-access-control/examples/001-idor-horizontal-parametro-id|001]]
- [ ] **`userId` filtrado** en comentarios/blog → `/my-account?username=<userId>` (puede ser `administrator`). → [[vulnerabilities/028-access-control/examples/001-idor-horizontal-parametro-id|001]]
- [ ] Cambiar `id`/GUID en URL/params/cookies. GUID "impredecible" suele estar **filtrado** en un post. → [[vulnerabilities/028-access-control/examples/001-idor-horizontal-parametro-id|001]]
- [ ] **IDOR en archivo estático** → `/download-transcript/N.txt` (incremental). 🚩 si hay live chat = FLAG (credenciales en el log). → [[vulnerabilities/028-access-control/labs/README|labs · IDOR archivo estático]]
- [ ] 🔁 **`GET` filtrado → cambiá el método:** `POST /my-account?username=administrator` (method-based bypass). → [[vulnerabilities/028-access-control/examples/004-bypass-plataforma-header-url|004 · método]]

**Vertical (subir de rol):**
- [ ] **Cookie de rol** `Admin=false` → `true`. → [[vulnerabilities/028-access-control/labs/README|labs · cookie de rol]]
- [ ] **Mass assignment** → `roleid=2` / `role` / `isAdmin` en un update de perfil (auto-escalada). → [[vulnerabilities/028-access-control/examples/003-mass-assignment-roleid|003]]
- [ ] **Bypass de plataforma:** `X-Original-URL`/`X-Rewrite-URL` a `/admin`; slash final; case; Spring `useSuffixPatternMatch` (`.anything`); `Referer: …/admin`. → [[vulnerabilities/028-access-control/examples/004-bypass-plataforma-header-url|004]]
- [ ] **Función de admin sin proteger** (obscurity): ruta filtrada en `/robots.txt` o en el JS de la home → entrar directo. → [[vulnerabilities/028-access-control/examples/002-vertical-admin-sin-proteger|002]]
- [ ] **Header de auth interno vía TRACE (caso borde):** si `/admin` filtra por un **header interno** (ej. `X-Custom-IP-Authorization`), descubrilo con `TRACE /admin` y spoofealo a `127.0.0.1`. → [[vulnerabilities/014-information-disclousure/labs/README|info disclosure · lab #4]]

## 🔗 Referencias
- [[vulnerabilities/028-access-control/access-control|entry point]] · [[vulnerabilities/028-access-control/labs/README|labs]]
- Ejemplos core: [[vulnerabilities/028-access-control/examples/001-idor-horizontal-parametro-id|001 · IDOR horizontal]] · [[vulnerabilities/028-access-control/examples/002-vertical-admin-sin-proteger|002 · admin sin proteger]] · [[vulnerabilities/028-access-control/examples/003-mass-assignment-roleid|003 · mass assignment]] · [[vulnerabilities/028-access-control/examples/004-bypass-plataforma-header-url|004 · bypass de plataforma]]
