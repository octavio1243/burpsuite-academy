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
- [ ] Manipular **`redirect_uri`** → desviar el **authorization code** a mi exploit server → robar su sesión. → [[vulnerabilities/026-oauth/examples/003-account-hijacking-redirect-uri|003 account hijacking]]
- [ ] Falta de **`state`** → CSRF de login / account linking. → [[vulnerabilities/026-oauth/examples/002-forced-profile-linking-csrf|002 CSRF sin state]]
- [ ] Robo de **`code`**/token por `Referer` (encadena con open redirect / DOM open-redirect). → [[vulnerabilities/026-oauth/examples/004-steal-token-open-redirect|004 open redirect]] · [[vulnerabilities/026-oauth/examples/005-steal-token-proxy-page|005 proxy postMessage]]
- [ ] **Bypass de auth** en implicit flow (substituir email/identidad de la víctima). → [[vulnerabilities/026-oauth/examples/001-implicit-flow-email-substitution|001 implicit substitution]]
- [ ] **SSRF** vía dynamic client registration (`logo_uri`/metadata). → [[vulnerabilities/026-oauth/examples/006-ssrf-dynamic-client-registration|006 SSRF]]

## 🔗 Referencias
- [[vulnerabilities/026-oauth/oauth|entry point]] · DOM open-redirect → [[vulnerabilities/025-dom-based/dom-based|DOM-based]]
