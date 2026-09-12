---
aliases:
  - to-do GraphQL
tags:
  - exam/to-do
  - vuln/graphql
---

# GraphQL — Qué probar

> Técnica → carpeta `vulnerabilities/021-graphql/`

## 🚩 Flags

> [!danger] 🚩 ¿Está?
> Endpoint **GraphQL** (`/graphql`, `/api`). Extensión **InQL**.

## 🎯 Objetivo (Stage 2)
- Mutaciones no autorizadas (cambiar rol/password) o leer datos privados.

## ♾️ Independiente del stage
- [ ] **InQL** → introspección; si está off → probar **sugerencias/aliasing**.
- [ ] Mutaciones no autorizadas (rol/password).
- [ ] **Brute por batching** (aliases) saltando rate limit.

## 🔗 Referencias
- carpeta `vulnerabilities/021-graphql/`
