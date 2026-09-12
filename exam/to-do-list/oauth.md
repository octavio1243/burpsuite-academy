---
aliases:
  - to-do OAuth
tags:
  - exam/to-do
  - vuln/oauth
---

# OAuth — Qué probar

> Técnica → [[vulnerabilities/026-oauth/oauth|entry point]] *(incompleto)*

## 🚩 Flags

> [!danger] 🚩 ¿Está?
> **Requisito:** el login es **por OAuth** (si no, no aplica).

## 🎯 Por stage
- **Stage 1:** robar la sesión de una víctima. · **Stage 2:** desviar el `code` del **admin**.

## ♾️ Independiente del stage
- [ ] Manipular **`redirect_uri`** → desviar el **authorization code** a mi exploit server → robar su sesión.
- [ ] Falta de **`state`** → CSRF de login / account linking.
- [ ] Robo de **`code`** por `Referer` (encadena con open redirect / DOM open-redirect).

## 🔗 Referencias
- [[vulnerabilities/026-oauth/oauth|entry point]] · DOM open-redirect → [[vulnerabilities/025-dom-based/dom-based|DOM-based]]
