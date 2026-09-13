---
aliases:
  - Business logic
  - business-logic
  - logic flaws
tags:
  - vuln/business-logic
  - entrypoint
---

# Business Logic — Punto de entrada

> Documento **agnóstico al negocio**: *cómo **detectar y explotar** fallas de lógica*. La explotación lab por lab → [[vulnerabilities/015-business-logic/labs/README|labs de Business Logic]].

> [!abstract] La idea en una línea
> No hay una vuln técnica: la app **asume cómo la vas a usar** y **confía en esa suposición**. La explotás **haciendo lo que no previeron** — mandás un valor fuera de rango (negativo, gigante, truncado), **saltás o reordenás** un paso del flujo, o usás un endpoint **para algo que no era su propósito**.

## 🎯 Cuándo aparece

- **Flujos multipaso** (registro, login con selección de rol, checkout, reset) → ¿podés **saltar/reordenar** un paso y que el server asuma un default?
- **Endpoints de doble uso** (un `change-password` que sirve para vos y para otros) → ¿podés quitar un parámetro "de seguridad" y apuntar a la víctima?
- **Confianza en datos del cliente** (`price`, `quantity`, dominio del email) → ¿el server **revalida** o confía?

## 🎯 Qué se logra (en el examen)

- **Stage 2 — escalada / toma de cuenta:** volverte **admin** (rol por defecto, dominio de email, cookie forjada) o **cambiarle la password al admin**. El objetivo final es siempre **admin → borrar `carlos`**.
- El resto de la categoría (precio/crédito/flujo de compra) es lógica de **Stage 1**.

> [!note] Seguir
> - **Labs** (11 resueltos, con los 🎯 de escalada marcados) → [[vulnerabilities/015-business-logic/labs/README|labs de Business Logic]].
> - **Examen (qué probar, Stage 2)** → [[exam/to-do-list/business-logic|business logic — qué probar]].
> - **Access control** (mismo objetivo admin) → [[vulnerabilities/028-access-control/access-control|access control]].
> - **Authentication** (reset/2FA y otros flancos de cuenta) → [[vulnerabilities/029-authentication/authentication|authentication]].
