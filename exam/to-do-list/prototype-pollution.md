---
aliases:
  - to-do Prototype Pollution
tags:
  - exam/to-do
  - vuln/prototype-pollution
---

# Prototype Pollution — Qué probar

> Técnica → [[vulnerabilities/020-prototype-pollution/prototype-pollution|entry point]] · labs → [[vulnerabilities/020-prototype-pollution/labs/README|labs]]

## 🚩 Flags

> [!danger] 🚩 ¿Está?
> **`__proto__` / `constructor.prototype`** en query o JSON **cambia el comportamiento**.
> - **Client-side:** DOM Invader (source→sink, "Scan for gadgets"). Confirmás con `Object.prototype.foo`.
> - **Server-side (SSPP):** lo detectás **a ciegas** — reflexión de la prop, o override no destructivo: `status` / `json spaces` / `charset` (utf-7).

## 🎯 Por stage

| Stage | Qué se logra | Cómo | Probabilidad |
| --- | --- | --- | --- |
| 🔴 **Stage 2** | escalar a **administrator** | update de perfil/datos (JSON) que **mergea sin sanear** → gadget `isAdmin`/`role` cae en `Object.prototype` | **último recurso** |
| ⚫ **Stage 3** | **RCE** → `cat /home/carlos/secret` | gadget del runtime Node (`child_process`): `execArgv`/`fork` · `shell`+`input`/`execSync` | lo típico (server-side) |

> [!tip] 💡 Stage 2 por prototype pollution (último recurso)
> Si **ya agotaste** los vectores normales de escalada (mass assignment, IDOR, JWT…) **y** el endpoint de **update de perfil** mergea el JSON sin sanear: probá contaminar el rol.
> - **Detección:** `"__proto__":{"foo":"bar"}` → ¿se refleja? Si no, override no destructivo (`status`/`json spaces`/`charset`). → [[vulnerabilities/020-prototype-pollution/examples/003-server-side-deteccion-a-ciegas|003 · detección a ciegas]]
> - **Escalada:** `"__proto__":{"isAdmin":true}` (o `role`) → refrescás y aparece el admin panel. → [[vulnerabilities/020-prototype-pollution/examples/004-server-side-escalada-isadmin|004 · escalada isAdmin]]
> - **Si filtran `__proto__`:** `"constructor":{"prototype":{"isAdmin":true}}`. → [[vulnerabilities/020-prototype-pollution/examples/005-bypass-constructor-y-sanitizacion|005 · bypass constructor]]
>
> **No es mass assignment.** Mass assignment escribe `isAdmin` en **tu propio registro** (el server confía en campos extra); acá el merge escribe `__proto__.isAdmin=true` en **`Object.prototype`** y el rol lo **hereda todo objeto**. Es la vía cuando el mass assignment directo (`"isAdmin":true`/`roleid=2`) **está filtrado**. Cruza con [[exam/to-do-list/access-control|access control]] y [[exam/to-do-list/api-testing|api testing]].

> [!warning] ⚠️ RCE en Stage 3 (server-side)
> Confirmada la SSPP, escalás a **RCE** por gadgets de `child_process` (los "maintenance jobs" del admin suelen ser el disparador, asíncrono):
> - **`fork()` → `execArgv`** con `--eval`. → [[vulnerabilities/020-prototype-pollution/examples/006-server-side-rce-execargv-fork|006 · execArgv/fork]]
> - **`execSync()` → `shell`+`input`** (`vim` con `:!`) o **`NODE_OPTIONS`** → exfil del secret a Collaborator. → [[vulnerabilities/020-prototype-pollution/examples/007-server-side-rce-exfil-execsync|007 · shell+input/execSync + exfil]]
> - **Siempre** confirmá con un `curl` a Collaborator antes de comandos destructivos.

## ♾️ Independiente del stage

- [ ] Inyectá una prop **basura** por la source: query `__proto__[foo]=bar` / `__proto__.foo=bar` ; JSON `"__proto__":{"foo":"bar"}`. Confirmá (`Object.prototype.foo` o reflexión).
- [ ] **Client-side:** DOM Invader (Burp) → source→sink + "Scan for gadgets".
- [ ] **Server-side:** si no se refleja, **override no destructivo** (`status`/`json spaces`/`charset` utf-7). **Nunca rompas el server de entrada** (la contaminación persiste toda la vida del proceso Node).
- [ ] Filtran `__proto__` → `constructor.prototype` ; filtro **no recursivo** → `__pro__proto__to__`.

## 🔗 Referencias

- [[vulnerabilities/020-prototype-pollution/prototype-pollution|entry point]] · [[vulnerabilities/020-prototype-pollution/labs/README|labs]]
- 🔴 Stage 2: [[vulnerabilities/020-prototype-pollution/examples/004-server-side-escalada-isadmin|004 escalada isAdmin]] (apoyo: [[vulnerabilities/020-prototype-pollution/examples/003-server-side-deteccion-a-ciegas|003 detección]] · [[vulnerabilities/020-prototype-pollution/examples/005-bypass-constructor-y-sanitizacion|005 bypass]])
- ⚫ Stage 3: [[vulnerabilities/020-prototype-pollution/examples/006-server-side-rce-execargv-fork|006 RCE fork/execArgv]] · [[vulnerabilities/020-prototype-pollution/examples/007-server-side-rce-exfil-execsync|007 RCE/exfil execSync]]
