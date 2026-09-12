---
aliases:
  - to-do HTTP Request Smuggling
  - to-do HRS
tags:
  - exam/to-do
  - vuln/http-smuggling
---

# HTTP Request Smuggling — Qué probar

> Técnica → [[vulnerabilities/008-http_smuggling/http-smuggling|entry point]] · labs → [[vulnerabilities/008-http_smuggling/labs/README|labs]] · scripts → [[vulnerabilities/008-http_smuggling/scripts/detect.py|detect.py]]

## 🚩 Flags

> [!danger] 🚩 ¿Está?
> Extensión **HTTP Request Smuggler** → *smuggle probe*. Orden: **CL.TE primero (no contamina), TE.CL después**. Preferí detección **diferencial (404)** al timing → [[vulnerabilities/008-http_smuggling/http-smuggling#🧪-cómo-detectarlo|cómo detectar]].

## 🎯 Por stage

| Aspecto | 🟢 Stage 1 | 🔴 Stage 2 |
| --- | --- | --- |
| **Víctima** | cualquier usuario / la caché | el **admin** que navega |
| **Objetivo** | robar sesión/datos del próximo user, o envenenar caché | robar cookie del admin, deducir header de admin, o entrar directo a `/admin` |

## ♾️ Independiente del stage
- [ ] **Robar `/my-account` del próximo** → colás para capturar su request / recibir su respuesta.
- [ ] **XSS reflejado colado** (ej. `User-Agent`) → cae en la próxima víctima → [[vulnerabilities/008-http_smuggling/labs/README|lab 10]].
- [ ] **Reveal front-end rewriting** → deducí qué header agrega el front (IP interna, rol) y **replicalo** para ser admin → [[vulnerabilities/008-http_smuggling/labs/README|lab 8]].
- [ ] **Entrar directo a `/admin`** contrabandeando la 2ª petición → [[vulnerabilities/008-http_smuggling/examples/001-cl-te|CL.TE]] / [[vulnerabilities/008-http_smuggling/examples/002-te-cl|TE.CL]].
- [ ] **Envenenar caché** (JS del exploit) · **web cache deception** · **response queue poisoning** → [[vulnerabilities/008-http_smuggling/examples/007-response-queue-poisoning|007]].
- [ ] **CL.0 hacia `/admin`** → posible pero **ciego** → [[vulnerabilities/008-http_smuggling/examples/006-cl-0|006]].

## 🔗 Referencias
- [[vulnerabilities/008-http_smuggling/http-smuggling|entry point]] · [[vulnerabilities/008-http_smuggling/labs/README|labs]] · [[vulnerabilities/008-http_smuggling/scripts/detect.py|detect.py]]
