---
aliases:
  - to-do GraphQL
tags:
  - exam/to-do
  - vuln/graphql
---

# GraphQL — Qué probar

> Técnica → [[vulnerabilities/021-graphql/graphql|entry point]] · labs → [[vulnerabilities/021-graphql/labs/README|labs]] · scripts → `vulnerabilities/021-graphql/scripts/` (`brute-force-graphql.py`, `execute-graphql.py`)

## 🚩 Flags

> [!danger] 🚩 ¿Está?
> Endpoint **GraphQL** (`/graphql`, `/api`, `/graphql/v1`, `/api/graphql`). Sonda universal: `{__typename}`. Extensión **InQL** para introspection.

## 🎯 Por stage

| Stage | Qué se logra | Cómo |
| --- | --- | --- |
| 🟢 **Stage 1** | **entrar como la víctima** (foothold) | si el **login es una mutation GraphQL** y hay rate limit, **batcheás** cientos de `login` con **alias** en 1 request → crackeás el password de `carlos`. → [[vulnerabilities/021-graphql/labs/README\|lab #4]] · `brute-force-graphql.py` |
| 🔴 **Stage 2** | escalar / datos privados | mutaciones no autorizadas (cambiar rol/password, `delete*`), o campos ocultos (`password`, `isAdmin`) por introspection/IDOR |

> [!tip] 💡 Alias = batching
> Cualquier límite "por request" (brute force de login, OTP, rate-limit) se saltea metiendo **N operaciones aliaseadas** en **un** request. Mandás uno solo y mirás qué alias devolvió `success:true`. Emparenta con [[exam/to-do-list/authentication|authentication]] (fuerza bruta).

## ♾️ Independiente del stage

- [ ] **InQL** → introspección; si está off → `__schema` + **newline**, o pedila por **GET**.
- [ ] Encontrar el endpoint: `{__typename}` sobre `/graphql`, `/api`, `/graphql/v1`, `/api/graphql`.
- [ ] **IDOR / campos ocultos:** pedí campos que la UI no muestra (`password`, `postPassword`) y cambiá `id`.
- [ ] Mutaciones no autorizadas (rol/password/`delete*`).
- [ ] **Brute por batching (alias)** saltando rate limit (login/OTP). → [[vulnerabilities/021-graphql/labs/README|lab #4]] · [lab](https://portswigger.net/web-security/graphql/lab-graphql-brute-force-protection-bypass)

## 🔗 Referencias

- [[vulnerabilities/021-graphql/graphql|entry point]] · [[vulnerabilities/021-graphql/labs/README|labs (5 resueltos)]] · scripts → `vulnerabilities/021-graphql/scripts/`
- Brute force (el alias batching emparenta) → carpeta `vulnerabilities/011-brute-force/`
