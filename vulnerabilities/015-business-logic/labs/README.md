---
aliases:
  - Business logic labs
  - logic flaws labs
tags:
  - vuln/business-logic
  - labs
  - portswigger
---

# Business logic — Labs de PortSwigger

> 🔎 Metodología (romper suposiciones del dev: saltar/reordenar pasos, input fuera de rango, endpoints de doble uso, parsing de email) → [[vulnerabilities/015-business-logic/business-logic|entry point de Business Logic]].

Labs de la categoría **[Business logic vulnerabilities](https://portswigger.net/web-security/logic-flaws)**: **11 en total** (4 Apprentice · 6 Practitioner · 1 Expert). **El hilo común:** no hay una vuln técnica; la app **asume cómo la vas a usar** y vos **rompés esa suposición** — mandás un valor que no esperaban (negativo, gigante, truncado), **saltás o reordenás** un paso del flujo, o usás un endpoint **para algo que no era su propósito**. Lo que cambia lab a lab es *qué suposición* rompés y *qué conseguís*: unos son manipulación de **precio/crédito** (Stage 1), otros son **escalada / toma de cuenta** (Stage 2).

> [!tip] 🎯 Los que importan para el examen (Stage 2)
> **5 de 11 son escalada o toma de cuenta de admin** (🎯 en la tabla): **inconsistent security controls**, **inconsistent handling of exceptional input**, **weak isolation on dual-use endpoint**, **flawed state machine** y **encryption oracle**. Los otros 6 son precio/crédito/flujo de compra (Stage 1). El "qué probar" para el examen → [[exam/to-do-list/business-logic|business logic (Stage 2)]].

## Tabla maestra

| #   | Laboratorio | Nivel | Técnica · qué necesitás | Objetivo |
| --- | --- | --- | --- | --- |
| 1 | [Excessive trust in client-side controls](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-excessive-trust-in-client-side-controls) | Apprentice | El `price` viaja en el `POST /cart` y el server **no lo revalida**. Lo bajás en Repeater. | Comprar la chaqueta sin crédito. |
| 2 | [High-level logic vulnerability](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-high-level) | Apprentice | `quantity` **admite negativos**: metés una cantidad negativa de otro producto para cancelar el costo. | Comprar la chaqueta bajando el total (≥ $0). |
| 3 🎯 | [Inconsistent security controls](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-inconsistent-security-controls) | Apprentice | El `/admin` confía en el **dominio del email**. Te registrás, y con "update email" te cambiás a `@dontwannacry.com`. | **Admin panel** → borrar `carlos`. |
| 4 | [Flawed enforcement of business rules](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-flawed-enforcement-of-business-rules) | Apprentice | Solo bloquean **repetir el mismo cupón seguido**: alternás `NEWCUST5` y `SIGNUP30`. | Comprar la chaqueta acumulando descuentos. |
| 5 | [Low-level logic flaw](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-low-level) | Practitioner | **Integer overflow** del precio: sumás la chaqueta con Intruder hasta pasar el máximo de 32 bits y que dé negativo. | Comprar la chaqueta por overflow. |
| 6 🎯 | [Inconsistent handling of exceptional input](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-inconsistent-handling-of-exceptional-input) | Practitioner | El email se **trunca a 255**: armás uno que quede en `...@dontwannacry.com` tras truncar, pero que llegue a tu inbox. | **Admin panel** → borrar `carlos`. |
| 7 🎯 | [Weak isolation on dual-use endpoint](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-weak-isolation-on-dual-use-endpoint) | Practitioner | En `change-password` **borrás `current-password`** y ponés `username=administrator`. | **Cambiar la pass del admin** → borrar `carlos`. |
| 8 | [Insufficient workflow validation](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-insufficient-workflow-validation) | Practitioner | Reproducís el `GET /cart/order-confirmation?order-confirmation=true` **sin pasar por el pago**. | Comprar la chaqueta saltando el pago. |
| 9 🎯 | [Authentication bypass via flawed state machine](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-authentication-bypass-via-flawed-state-machine) | Practitioner | **Dropeás `GET /role-selector`** tras el login → el server te deja el rol **admin** por defecto. | **Admin** por defecto → borrar `carlos`. |
| 10 | [Infinite money logic flaw](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-infinite-money) | Practitioner | Gift card de $10 comprada con `SIGNUP30` (30%) sale $7 y canjea $10: macro + Intruder para loopear. | Crédito infinito → comprar la chaqueta. |
| 11 🎯 | [Authentication bypass via encryption oracle](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-authentication-bypass-via-encryption-oracle) | **Expert** | La cookie `notification` es un **oráculo** de cifrado/descifrado: forjás la `stay-logged-in` de `administrator`. | **Impersonar admin** → borrar `carlos`. |

---

## Solución por lab

**L1 — Excessive trust in client-side controls (precio):**
- Login `wiener:peter`. Agregá la chaqueta → capturá `POST /cart`. Trae `price`. En Repeater bajalo (`price=1`), recargá el carrito y ordená. El server nunca revalida el precio.

**L2 — High-level logic vulnerability (cantidad negativa):**
- En `POST /cart`, `quantity` no valida negativos. Agregá la chaqueta y **otro producto barato con `quantity` negativo** para que su total negativo baje el total general dentro de tu crédito (el total final debe quedar **≥ $0**). Ordená.

**L3 🎯 — Inconsistent security controls (dominio de email):**
- `/admin` solo para `@dontwannacry.com`. Registrate con `algo@tu-id.web-security-academy.net`, confirmá por el email client. En **My account → update email**, cambiá a `algo@dontwannacry.com`. El check de privilegio confía en el dominio → entrás a `/admin` y **borrás `carlos`**.

**L4 — Flawed enforcement of business rules (cupones):**
- Hay `NEWCUST5` (en el sitio) y `SIGNUP30` (por suscribirte al newsletter). Solo bloquean repetir el **mismo** código seguido. En el checkout **alterná** (`NEWCUST5`, `SIGNUP30`, `NEWCUST5`, …) hasta que el total entre en tu crédito.

**L5 — Low-level logic flaw (integer overflow):**
- Mandá el add de la chaqueta (`quantity=99`) a Intruder con **Null payloads** "continue indefinitely" hasta pasar el máximo de 32 bits (`2147483647`) y que el precio **desborde a negativo**. Después ajustá con Repeater (agregá unas 47 chaquetas más) para dejar el total cerca de `-$1221.96`, y sumá un segundo producto en la cantidad justa para que el total final quede entre $0 y tu crédito. Ordená.

**L6 🎯 — Inconsistent handling of exceptional input (truncado de email):**
- `/admin` solo `@dontwannacry.com`. El email se **trunca a 255 chars**. Registrate con una dirección armada para que, tras un relleno largo, `@dontwannacry.com` quede **exactamente en el borde de 255** y el subdominio real vaya después: `<relleno largo>@dontwannacry.com.<padding>@tu-id.web-security-academy.net`, dimensionado para que el valor guardado se trunque a `...@dontwannacry.com`. El mail de confirmación igual llega a **tu inbox**; confirmá, logueá, entrá a `/admin`, borrá `carlos`.

**L7 🎯 — Weak isolation on dual-use endpoint (pass del admin):**
- Login `wiener:peter`, capturá `POST /my-account/change-password`. **Borrá el parámetro `current-password` entero** — el endpoint acepta el cambio igual. Cambiá `username` a `administrator` y seteá una new password. Enviá → sobreescribís la pass del admin → logueá como `administrator` → admin panel → borrá `carlos`.

**L8 — Insufficient workflow validation (saltar pago):**
- Login `wiener:peter`, comprá algo barato para ver el flujo. Mandá `GET /cart/order-confirmation?order-confirmation=true` a Repeater. Agregá la chaqueta al carrito y **sin pagar**, reproducí ese request de confirmación: finaliza la orden sin revalidar el pago.

**L9 🎯 — Authentication bypass via flawed state machine (rol por defecto):**
- Logout → login con **intercept ON**. **Forwardeá `POST /login`** y **dropeá el `GET /role-selector`** que sigue. Navegá a la home / `/admin`: como el paso de rol nunca corrió, la sesión conserva el rol **`administrator`** por defecto. Borrá `carlos`.

**L10 — Infinite money logic flaw (crédito infinito):**
- Suscribite al newsletter (`SIGNUP30`, 30%). Una gift card de $10 con `SIGNUP30` sale **$7** y canjea **$10** (+$3 por ciclo). Armá un **macro de session handling** que encadene: agregar gift card → aplicar `SIGNUP30` → checkout → leer el código de la respuesta de confirmación → canjearlo en `POST /gift-card`. Configurá el macro para extraer el código y corré Intruder contra `/my-account` (~412 null payloads, 1 request concurrente) hasta poder comprar la chaqueta.

**L11 🎯 — Authentication bypass via encryption oracle (Expert, cookie forjada):**
1. Login `wiener:peter` con "Stay logged in" → cookie `stay-logged-in` cifrada (codifica `username:timestamp`).
2. Un comentario con **email inválido** refleja la cookie `notification` **descifrada** en el error = **oráculo de descifrado**; el mismo campo email es **oráculo de cifrado**.
3. Pegá tu `stay-logged-in` en la cookie `notification` → la descifrás y ves el formato `wiener:<timestamp>`.
4. Mandá `administrator:<timestamp>` por el campo email para **cifrarlo**; usá el oráculo para **alinear/strip** el prefijo `Invalid email address: ` a un borde de bloque de 16 bytes.
5. Seteá el ciphertext resultante como tu `stay-logged-in` → navegás como `administrator` → `/admin/delete?username=carlos`.

---

## Atajos mentales / patrones

- **No hay señal técnica**: business logic se caza pensando *"¿qué asume el dev que yo voy a hacer?"* y haciendo lo contrario.
- **Precio/crédito (Stage 1):** el cliente manda `price`/`quantity` → tamperealos (negativos, overflow); cupones que se apilan; gift cards que rinden más de lo que cuestan; saltar el paso de pago. Labs 1, 2, 4, 5, 8, 10.
- **Escalada / cuenta (Stage 2) 🎯:** las 3 vías limpias —
    - **Máquina de estados rota:** interceptá y **dropeá/reordená** un paso (rol, verificación) → el server asume un default (admin). L9.
    - **Endpoint de doble uso:** quitá el param "de seguridad" (`current-password`) y apuntá `username` a la víctima. L7.
    - **Confianza en el email:** registrate/cambiá el email al **dominio del admin** (directo o por **truncado a 255**). L3, L6.
    - **(Expert) Encryption oracle:** un error que refleja texto descifrado te da cifrado/descifrado arbitrario → forjás la cookie del admin. L11.
- **El objetivo del examen es siempre el mismo:** llegar a **admin → borrar `carlos`**.

> [!note] Ver también
> - **Entry point de la categoría** → [[vulnerabilities/015-business-logic/business-logic|business logic]].
> - **Examen (Stage 2, qué probar)** → [[exam/to-do-list/business-logic|business logic — qué probar]].
> - **Access control** (mismo objetivo final: admin → borrar carlos) → [[vulnerabilities/028-access-control/access-control|access control]].
> - **Authentication** (reset/2FA, otros flancos de cuenta; la cookie forjada del L11 roza el brute de stay-logged-in) → [[vulnerabilities/029-authentication/authentication|authentication]].
