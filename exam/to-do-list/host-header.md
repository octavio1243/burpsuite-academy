---
aliases:
  - to-do Host Header
tags:
  - exam/to-do
  - vuln/host-header-injection
---

# HTTP Host Header — Qué probar

> Técnica → carpeta `vulnerabilities/016-host-header-injection/` · script → [[vulnerabilities/016-host-header-injection/conn_reuse.py|conn_reuse.py]]

## 🚩 Flags

> [!danger] 🚩 ¿Está?
> El **`Host` (o `X-Forwarded-Host`) manipulado termina reflejado** — en el link del mail de reset, en un redirect, o el server se pega solo a un interno.

## 🎯 Por stage

| Aspecto | 🟢 Stage 1 | 🔴 Stage 2 | 🟣 Stage 3 |
| --- | --- | --- | --- |
| **Uso** | envenenar el reset de una víctima | reset poisoning al **admin** | **SSRF** al interno `localhost:6566` |

## ♾️ Independiente del stage
- [ ] En **recuperar contraseña**, cambiar `Host` → ¿el link de reset apunta a **oastify/Collaborator**? → capturás el token.
- [ ] Variantes: **`X-Forwarded-Host`**, doble `Host`, `Host: localhost`.
- [ ] *(Stage 3)* Inyectar `Host`/`X-Forwarded-Host` para que el server se pegue a su **servicio interno** o a un oastify (SSRF) → [[vulnerabilities/007-ssrf/ssrf|SSRF]].

## 🔗 Referencias
- carpeta `vulnerabilities/016-host-header-injection/` · reset → [[vulnerabilities/029-authentication/authentication|Authentication]]
