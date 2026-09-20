---
aliases:
  - to-do API Testing
  - to-do Mass Assignment
  - to-do Parameter Pollution
tags:
  - exam/to-do
  - vuln/api-testing
---

# API Testing / Mass Assignment — Qué probar

> Sin vuln/entry point propio. Mass assignment → [[vulnerabilities/028-access-control/access-control|access control]] · SSPP → [Server-side parameter pollution](https://portswigger.net/web-security/api-testing/server-side-parameter-pollution) (sin example local).

## 🚩 Flags

> [!danger] 🚩 ¿Está?
> - Endpoints de **API** (JSON) con updates de perfil, o documentación/endpoints ocultos → **mass assignment**.
> - Un **`.js`** revela una **API interna** con params tipo `username`/`field`/`format` → **server-side parameter pollution** (inyectás params en una query que el server rearma).

## 🎯 Objetivo (Stage 2)
- **Auto-escalada** de rol sin tocar al admin (mass assignment).
- **Account takeover del admin** filtrando su **reset token** (parameter pollution).

## ♾️ Mass assignment
- [ ] Añadir `"isAdmin":true` / `"role":"admin"` / `"roleid":2` al JSON del perfil. → [[vulnerabilities/028-access-control/examples/003-mass-assignment-roleid|003]]
- [ ] Métodos alternos (`PUT`/`PATCH`/`DELETE`) · **`Content-Type` swaps**. → [[vulnerabilities/028-access-control/labs/README|labs · método]]
- [ ] Documentación / endpoints ocultos de la API. → [[exam/to-do-list/content-discovery|content discovery]]
- Ejemplo: [[vulnerabilities/028-access-control/examples/003-mass-assignment-roleid|auto-escalada por `roleid`]]

## 🧬 Server-Side Parameter Pollution (query string)

> Lab (los pasos de abajo) → [SSPP in a query string](https://portswigger.net/web-security/api-testing/server-side-parameter-pollution/lab-exploiting-server-side-parameter-pollution-in-query-string) · sin example local.

> [!tip] 💡 Fuga del reset token del admin (Stage 2)
> Si en el **reset de contraseña** un `.js` (ej. `/static/js/forgotPassword.js`) revela que el backend arma una **query interna** con `username` y un `field` (ej. `/forgot-password?reset_token=...`), inyectás caracteres **codificados** en `username` para **truncar** y **agregar** parámetros a esa query interna:

- [ ] **Reconocimiento:** leé el `.js` del reset en el HTTP history → mirá qué params usa la API interna (`username`, `field`, `reset_token`).
- [ ] **Truncar** con `%23` (`#`): `username=administrator%23` → si aparece un error tipo `Field not specified`, confirmás que hay un `field` que quedó cortado.
- [ ] **Agregar** con `%26` (`&`): `username=administrator%26field=x%23` → `Invalid field` = el server **procesa** tu parámetro inyectado.
- [ ] **Brute del `field`:** Intruder con la lista **server-side variable names** → `field=email` devuelve `200`.
- [ ] **Fuga del token:** `username=administrator%26field=reset_token%23` → devuelve el **reset token del admin**.
- [ ] **Takeover:** `/forgot-password?reset_token=<TOKEN-ROBADO>` → seteás la password del admin → login → borrás `carlos`.

> Cruza con el flanco de reset en [[exam/to-do-list/authentication|authentication]]. · Lab: [Exploiting server-side parameter pollution in a query string](https://portswigger.net/web-security/api-testing/server-side-parameter-pollution/lab-exploiting-server-side-parameter-pollution-in-query-string)

## 🔗 Referencias
- Mass assignment (auto-escalada) → [[vulnerabilities/028-access-control/access-control|access control]]
- Reset / account takeover → [[exam/to-do-list/authentication|authentication]]
- Parameter pollution: [Server-side parameter pollution](https://portswigger.net/web-security/api-testing/server-side-parameter-pollution) · [lab (query string)](https://portswigger.net/web-security/api-testing/server-side-parameter-pollution/lab-exploiting-server-side-parameter-pollution-in-query-string)
