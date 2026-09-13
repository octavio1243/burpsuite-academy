---
aliases:
  - to-do Business Logic
  - to-do Logic Flaws
tags:
  - exam/to-do
  - vuln/business-logic
---

# Business Logic — Qué probar

> Técnica → [[vulnerabilities/015-business-logic/business-logic|entry point]] · labs → [[vulnerabilities/015-business-logic/labs/README|labs]]

## 🚩 Flags

> [!danger] 🚩 ¿Está?
> **No hay señal única.** La app **asume cómo la vas a usar** y confía en eso. Probá **romper el flujo esperado**: saltar/reordenar pasos, mandar valores fuera de rango (negativos, gigantes, truncados), usar un endpoint de **doble uso** para otra cosa, o registrarte con un email del **dominio del admin**.

## 🎯 Por stage

> **Uso en el examen = Stage 2 (escalada / toma de cuenta).** Es el "último recurso de flujo": cuando agotaste los vectores técnicos (JWT, IDOR, mass assignment, access control), mirás la **lógica del negocio**.

| Camino (Stage 2) | Cómo | Lab |
| --- | --- | --- |
| **Máquina de estados rota** | interceptá el login y **dropeá `GET /role-selector`** → el server te deja el rol **admin** por defecto | [[vulnerabilities/015-business-logic/labs/README\|state machine]] · [lab](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-authentication-bypass-via-flawed-state-machine) |
| **Endpoint de doble uso** | en `change-password`, **borrá `current-password`** y poné `username=administrator` → cambiás la pass del admin | [[vulnerabilities/015-business-logic/labs/README\|weak isolation]] · [lab](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-weak-isolation-on-dual-use-endpoint) |
| **Confianza en el email (dominio admin)** | registrarte / cambiar el email a `@<dominio-admin>` (ej. `@dontwannacry.com`) → `/admin` | [[vulnerabilities/015-business-logic/labs/README\|inconsistent controls]] · [lab](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-inconsistent-security-controls) |
| **Email truncado (255)** | armar el email para que **tras truncar** quede en `@dontwannacry.com` pero llegue a tu inbox | [[vulnerabilities/015-business-logic/labs/README\|exceptional input]] · [lab](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-inconsistent-handling-of-exceptional-input) |
| **(Expert) Encryption oracle** | un error que refleja texto **descifrado** = oráculo → forjás la cookie `stay-logged-in` de admin | [[vulnerabilities/015-business-logic/labs/README\|encryption oracle]] · [lab](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-authentication-bypass-via-encryption-oracle) |

> [!tip] 💡 Es un Stage 2 "de flujo"
> Preguntate: ¿puedo **saltarme un paso**, **reusar un endpoint** para otra cosa, o entrar con un email **"de la casa"**? El objetivo es siempre **admin → borrar `carlos`**. Los labs de precio/crédito (client-side controls, cantidad negativa, cupones, overflow, gift cards) son lógica de **compra** (Stage 1), no escalada.

## ♾️ Independiente del stage

- [ ] **Máquina de estados:** interceptá el flujo (login/registro/checkout) y **dropeá/reordená** requests → ¿el server asume un default (admin)?
- [ ] **Endpoint de doble uso:** quitá params "de seguridad" (`current-password`) y apuntá `username`/`email` a la víctima.
- [ ] **Email del dominio admin:** registro o cambio de email a `@<dominio-admin>`; probá también **truncado** (emails largos) y parsing raro.
- [ ] **Client-side controls (Stage 1):** tamperear `price`/`quantity` (negativos, overflow), apilar cupones, saltar el pago.

## 🔗 Referencias

- [[vulnerabilities/015-business-logic/business-logic|entry point]] · [[vulnerabilities/015-business-logic/labs/README|labs (11 resueltos)]]
- Escalada/cuenta: labs **3, 6, 7, 9, 11** (los 🎯 del labs/README).
- Cruces: [[exam/to-do-list/access-control|access control]] (mismo objetivo admin) · [[exam/to-do-list/authentication|authentication]] (reset/2FA, cookie stay-logged-in del L11).
