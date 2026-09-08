---
aliases:
  - DOM sinks
  - DOM sources
  - sinks & sources
tags:
  - vuln/dom-based
  - reference
  - cheat-sheet
---

# DOM — Sources & Sinks (lista para grepear)

> Referencia para **cazar DOM-based**: buscá (Ctrl+F en los `.js` / DOM Invader) un **source controlable** que fluya hacia un **sink peligroso**. Si además ves `postMessage` / `addEventListener("message")` / `eval` → prioridad máxima. Técnica → [[vulnerabilities/025-dom-based/dom-based|entry point]].

## 📥 Sources — datos que el atacante controla

Lo que entra bajo tu control y puede terminar en un sink:

| Fuente | De dónde sale / cómo la controlás |
| ------ | --------------------------------- |
| `location` (`location.search`, `location.hash`, `location.pathname`) | la **URL** que le mandás a la víctima |
| `document.URL` | URL completa |
| `document.documentURI` | URL del documento |
| `document.URLUnencoded` | URL sin decodificar (legacy) |
| `document.baseURI` | base del documento |
| `document.referrer` | página anterior → la controlás poniendo el link en **tu** página |
| `document.cookie` | cookies del cliente → controlable si hay **cookie manipulation** |
| `window.name` | persiste entre navegaciones → lo setea la ventana que abre |
| **web messages** (`event.data` de `message`) | `postMessage` desde un `<iframe>`/ventana tuya |
| `history.pushState` / `history.replaceState` | manipulan la URL sin recargar |
| `localStorage` / `sessionStorage` | storage envenenable |
| `IndexedDB` (`mozIndexedDB`, `webkitIndexedDB`, `msIndexedDB`) | storage del cliente |
| `Database` (WebSQL) | storage del cliente (legacy) |

> **Los 4 más usados en labs/examen:** `location.search`, `location.hash`, `document.referrer`, y **web messages** (`postMessage`).

## 📤 Sinks — funciones peligrosas (destino)

### HTML / XSS (ejecución de JS)

| Sink | Nota |
| ---- | ---- |
| `eval()` | ejecuta el string como JS |
| `Function()` / `new Function()` | idem |
| `setTimeout("…")` / `setInterval("…")` | con **string** ejecutan JS |
| `document.write()` / `document.writeln()` | escribe HTML crudo |
| `element.innerHTML` | ⚠️ **NO ejecuta `<script>` ni `<svg>`** → usá `<img src=1 onerror=…>` o `<iframe>` |
| `element.outerHTML` | idem innerHTML |
| `element.insertAdjacentHTML()` | idem |
| `element.onevent` (`onclick`, `onerror`, `onload`…) | handler asignado con dato controlado |
| `document.domain` | relaja SOP (document-domain manipulation) |
| `range.createContextualFragment()` | parsea HTML |

> [!warning] `innerHTML` y sus límites
> `element.innerHTML` **no corre `<script>`** (ni tags `<svg>` que dependan de script en algunos casos). **Alternativa:** inyectar `<img>` o `<iframe>` con un event handler: `<img src=1 onerror=alert(1)>`.

### jQuery (si el target usa jQuery — chequeá la versión)

`add()` · `after()` · `append()` · `animate()` · `insertAfter()` · `insertBefore()` · `before()` · `html()` · `prepend()` · `replaceAll()` · `replaceWith()` · `wrap()` · `wrapInner()` · `wrapAll()` · `has()` · `constructor()` · `init()` · `index()` · `jQuery.parseHTML()` · `$.parseHTML()`

También sinks de **atributo/selector** en jQuery: `$(selector)` (`$(location.hash)`), `.attr('href', …)` (→ `javascript:`).

### Otros sinks (no-XSS, cada uno = otra vuln DOM-based)

| Sink | Vuln resultante |
| ---- | --------------- |
| `window.location` / `location.href` / `location.assign()` / `location.replace()` | **open redirection** / JS injection (`javascript:`) |
| `document.cookie` | **cookie manipulation** |
| `postMessage()` | **web message manipulation** |
| `element.src` / `element.href` / `element.action` | **link manipulation** |
| `WebSocket()` | **WebSocket-URL poisoning** |
| `XMLHttpRequest.setRequestHeader()` | **Ajax request-header manipulation** |
| `FileReader.readAsText()` | **local file-path manipulation** |
| `ExecuteSql()` | **client-side SQL injection** (WebSQL) |
| `sessionStorage.setItem()` / `localStorage.setItem()` | **HTML5-storage manipulation** |
| `document.evaluate()` | **client-side XPath injection** |
| `JSON.parse()` | **client-side JSON injection** |
| `element.setAttribute()` | **DOM-data manipulation** |
| `RegExp()` | **denial of service** (ReDoS) |

## 🔎 Cómo usar esta lista

1. **Grep en el JS** del target por los **sinks** (empezá por `eval`, `innerHTML`, `document.write`, `postMessage`, `location`, `document.cookie`).
2. En cada hit, **rastreá hacia atrás**: ¿el argumento viene de un **source** de arriba? → hay vuln.
3. **DOM Invader** (browser de Burp) hace 1+2 automáticamente y marca la cadena source→sink.
4. El **sink** te dice **qué vuln es** (tabla de "otros sinks") y por lo tanto **qué payload** armar.

> Lista canónica de sinks DOM-XSS de PortSwigger: <https://portswigger.net/web-security/cross-site-scripting/dom-based#which-sinks-can-lead-to-dom-xss-vulnerabilities>
