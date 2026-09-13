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

## 🎯 Por stage

| | 🔴 Stage 2 (→ admin) | 🟣 Stage 3 (leer secret) |
| --- | --- | --- |
| **Objetivo** | alcanzar el **panel admin interno** en `localhost:6566` y ejecutar una acción de admin (borrar/crear admin, subir rol) | leer `/home/carlos/secret` o pegarle a `http://localhost:6566/` |
| **Vector típico** | fetch server-side (`stockApi`) con filtro de host → **bypass vía open redirect** | parámetro-URL / Host header → `file://` o `http://localhost:6566/` |

## 🔴 Stage 2 — panel admin interno vía open redirect

> [!danger] 🚩 Cuándo
> El fetch server-side (`stockApi`) **valida el host** y solo acepta URLs del propio sitio, pero existe un **open redirect** (`next`/`path`/`returnUrl` que cae en `Location:`). El server sigue el 302 **sin re-validar** el destino.

Chain (el path propio pasa el filtro → el 302 lo lleva al interno):

<pre class="payload"><code>stockApi=/product/nextProduct?path=http://<mark>localhost:6566</mark>/admin
→ (responde el panel admin) → /admin/delete?username=carlos   # o crear admin / subir rol
</code></pre>

> [!note] 📎 Traducción examen
> El lab de PortSwigger usa `192.168.0.12:8080`; en el examen el interno es **`localhost:6566`**. Técnica agnóstica → [[vulnerabilities/007-ssrf/examples/005-bypass-open-redirect|005 · open redirect]] · [[vulnerabilities/open-redirect/README|Open Redirect]].

## 🟣 Stage 3 — leer el secret
- Pegarle a **`localhost:6566`** o leer **`/home/carlos/secret`** por `file://`.

## ♾️ Independiente del stage
- [ ] Parámetro-URL → `http://localhost:6566/` · `file:///home/carlos/secret`.
- [ ] **`Referer`** → puede haber analytics que lo visite (SSRF ciego) → Collaborator + Poll now → [[vulnerabilities/007-ssrf/examples/006-ssrf-ciego-deteccion-oob|006]].
- [ ] **Path traversal** en la URL interna hasta el fichero.
- [ ] Bypass de filtros: IP encoding, redirect, `@`, `#`, DNS rebinding.
- [ ] **Filtro que no cede → open redirect** (`next`/`returnUrl`/`path` que cae en `Location:`) → ver **🔴 Stage 2** arriba (chain a `localhost:6566`) · [[vulnerabilities/007-ssrf/examples/005-bypass-open-redirect|005]].

## 🔗 Referencias
- [[vulnerabilities/007-ssrf/ssrf|entry point]] · [[vulnerabilities/007-ssrf/labs/README|labs]] · [[vulnerabilities/open-redirect/README|Open Redirect]] · [[vulnerabilities/007-ssrf/examples/005-bypass-open-redirect|005 · open redirect]] · Host header → carpeta `vulnerabilities/016-host-header-injection/`
