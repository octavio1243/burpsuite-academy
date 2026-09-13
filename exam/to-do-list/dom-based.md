---
aliases:
  - to-do DOM-based
tags:
  - exam/to-do
  - vuln/dom-based
---

# DOM-Based — Qué probar

> Técnica → [[vulnerabilities/025-dom-based/dom-based|entry point]] · sinks → [[vulnerabilities/025-dom-based/sinks|sinks & sources]] · labs → [[vulnerabilities/025-dom-based/labs/README|labs]] · ejemplos 001–004

## 🚩 Flags

> [!danger] 🚩 ¿Está? — grepeá el `.js` del cliente
> Ctrl+F: **`addEventListener("message"` / `postMessage(` / `eval(`** → altamente probable (prioridad alta). Otros sinks: `innerHTML`, `document.write`, `location.href`, `document.cookie`, `setTimeout(str)`, jQuery `$()`. Sources: `location.search/hash`, `document.referrer`, `window.name`, web messages. → [[vulnerabilities/025-dom-based/sinks|lista]].

> [!warning] ⚠️ Requiere exploit server + víctima
> No persisten (el bug vive en el JS) → entregás `<iframe>`/URL y necesitás que la víctima/admin lo visite (confirmá en Access log). Excepción: **open redirect** (URL directa, para OAuth).

## 🎯 Por stage

| Aspecto | 🟢 Stage 1 | 🔴 Stage 2 |
| --- | --- | --- |
| **A quién** | una víctima | el **admin** |
| **Objetivo** | robar cookie / actuar en su sesión | robar cookie del admin / actuar como él |

## ♾️ Independiente del stage
- [ ] Grepear sinks → rastrear **source → sink** (DOM Invader).
- [ ] **`postMessage`/`addEventListener('message')` sin chequeo de `origin`** → `<iframe>` que hace `postMessage` en `onload` → [[vulnerabilities/025-dom-based/examples/001-web-message-innerhtml|001 · web message → innerHTML]].
- [ ] **`eval`/`Function`/`setTimeout(str)`** → ejecución directa (reflected DOM).
- [ ] **DOM open-redirect** (`location.href` con param `url`) → robar `token`/`code` en OAuth → [[vulnerabilities/025-dom-based/examples/002-open-redirection-dom|002 · open redirect DOM]].
- [ ] **Cookie manipulation** (`document.cookie`) → [[vulnerabilities/025-dom-based/examples/003-cookie-manipulation-dom|003 · cookie manipulation]] · **DOM clobbering** (`window.x || {}` + HTML con `id`/`name`) → [[vulnerabilities/025-dom-based/examples/004-dom-clobbering-cid|004 · clobbering + cid]].

## 🔗 Referencias
- [[vulnerabilities/025-dom-based/dom-based|entry point]] · [[vulnerabilities/025-dom-based/sinks|sinks]] · [[vulnerabilities/025-dom-based/labs/README|labs]] · [[vulnerabilities/002-xss/README#🌳 DOM XSS — source → sink|XSS→DOM]]
- Ejemplos: [[vulnerabilities/025-dom-based/examples/001-web-message-innerhtml|001 · web message → innerHTML]] · [[vulnerabilities/025-dom-based/examples/002-open-redirection-dom|002 · open redirect]] · [[vulnerabilities/025-dom-based/examples/003-cookie-manipulation-dom|003 · cookie manipulation]] · [[vulnerabilities/025-dom-based/examples/004-dom-clobbering-cid|004 · DOM clobbering]]
