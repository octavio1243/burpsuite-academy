---
aliases:
  - to-do API Testing
  - to-do Mass Assignment
tags:
  - exam/to-do
  - vuln/api-testing
---

# API Testing / Mass Assignment — Qué probar

## 🚩 Flags

> [!danger] 🚩 ¿Está?
> Endpoints de **API** (JSON) con updates de perfil, o documentación/endpoints ocultos.

## 🎯 Objetivo (Stage 2)
- **Auto-escalada** de rol sin tocar al admin.

## ♾️ Independiente del stage
- [ ] **Mass assignment:** añadir `"isAdmin":true` / `"role":"admin"` / `"roleid":2` al JSON del perfil.
- [ ] Métodos alternos (`PUT`/`PATCH`/`DELETE`) · **`Content-Type` swaps**.
- [ ] Documentación / endpoints ocultos de la API.

## 🔗 Referencias
- Access Control (mass assignment) → [[vulnerabilities/028-access-control/access-control|entry point]]
