---
aliases:
  - to-do XSS
tags:
  - exam/to-do
  - vuln/xss
---

# Cross-Site Scripting (XSS) — Qué probar

> Técnica → [[vulnerabilities/002-xss/README|entry point]] · labs → [[vulnerabilities/002-xss/labs/README|labs]] · [[vulnerabilities/002-xss/cheat-sheet|cheat sheet]] · ofuscación → [[vulnerabilities/019-obfuscacion/xss-obfuscation|xss-obfuscation]]

## 🚩 Flags

> [!danger] 🚩 ¿Está?
> Se **importan `.js`** en la página (posible inyección/robo). **Stage 2:** ¿aparecen `.js` **nuevos** al estar logueado / en zonas del admin?

> [!warning] 🍪 `HttpOnly` bifurca el camino, NO descarta el XSS
> - `HttpOnly: false` → `document.cookie` la ve → **robo directo de cookie**.
> - `HttpOnly: true` → no la leés, pero el XSS **igual sirve**: `fetch` same-origin a `/my-account` (sacar `email`/`apiKey`), **leer el CSRF token y cambiar email/password**, reenviar el body. → [[vulnerabilities/002-xss/README#🎯 Qué hacer con un XSS (objetivos de explotación)|objetivos]].

## 🎯 Por stage

| Aspecto | 🟢 Stage 1 | 🔴 Stage 2 |
| --- | --- | --- |
| **A quién** | una víctima que navega | el **admin** |
| **Objetivo** | robar su cookie/sesión → su cuenta | robar cookie del admin o **actuar como él** (cambiar su email/password) |
| **Entrega** | stored, o reflejado al exploit server | stored en campo que el admin ve (`/admin`), o entregado y confirmado en **Access log** |

## ♾️ Independiente del stage

**Dónde probar (recon):**
- [ ] **Reflexión en el buscador** → romper contexto HTML con `<>` (`"><svg onload=...>`).
- [ ] **Stored en comentarios** → probar también el campo **website/URL** (va a un `href`).
- [ ] **DOM:** `document.write` · `location.search/hash` · `innerHTML` (DOM Invader).
- [ ] **jQuery** (¿versión? sinks `$()`, `.html()`, `attr('href')`) · **`ng-app`/AngularJS** (`{{...}}`) · **`eval`** (reflected DOM).

**Qué hacer con él:**
- [ ] **Exfiltrar cookies** al exploit server → [[vulnerabilities/002-xss/exfil-payloads.js|exfil-payloads.js]].
- [ ] Si `HttpOnly` → actuar en su sesión (CSRF token + `fetch`) o exfiltrar `apiKey`/`/my-account`.

## 🔗 Referencias
- [[vulnerabilities/002-xss/README|entry point]] · [[vulnerabilities/002-xss/labs/README|labs]] · [[vulnerabilities/002-xss/cheat-sheet|cheat sheet]] · [[vulnerabilities/019-obfuscacion/xss-obfuscation|ofuscación]] · DOM → [[vulnerabilities/025-dom-based/dom-based|DOM-based]]
