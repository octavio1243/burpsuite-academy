---
aliases:
  - Business Logic - input excepcional (email truncado)
  - Inconsistent handling of exceptional input
tags:
  - vuln/business-logic
  - example
  - portswigger
---

# Manejo inconsistente de input excepcional (email truncado a 255)

> Lab: [Inconsistent handling of exceptional input](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-inconsistent-handling-of-exceptional-input) · **Practitioner** · técnica → [[vulnerabilities/015-business-logic/business-logic|entry point]]

## ¿Por qué acá? (valor gigante que rompe el parsing)
- **La suposición que rompés:** `/admin` confía en el dominio `@dontwannacry.com`, y acá **sí** validan el dominio en el registro. Pero el dev asume que el email guardado es **el mismo** que el que validó.
- **Por qué funciona:** el email se **trunca a 255 caracteres** en la base. Armás una dirección que **para el envío** llega a tu inbox, pero que **tras truncar** queda como `...@dontwannacry.com`. Validación y almacenamiento manejan el valor de forma **inconsistente**.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que dimensionás/reemplazás vos (relleno + tu subdominio real).

Registrate con un email armado para que `@dontwannacry.com` caiga **justo en el borde de 255** y el subdominio real que entrega el mail vaya **después** del corte:
<pre class="payload"><code><mark>&lt;relleno largo&gt;</mark>@dontwannacry.com.<mark>&lt;padding&gt;</mark>@<mark>TU-ID.web-security-academy.net</mark></code></pre>
Dimensioná el relleno para que el valor **guardado** se trunque exactamente a `...@dontwannacry.com`. El mail de confirmación igual llega a **tu inbox** (el dominio real del final). Confirmá, logueá, entrá a `/admin`.

## Verificación
Tras confirmar, la cuenta aparece como `@dontwannacry.com` (truncada) y `/admin` te deja entrar → borrás `carlos` → lab resuelto.

## Detalles que se pasan por alto
- Contá bien: el `@dontwannacry.com` tiene que terminar **en la posición 255**; ni antes ni después.
- El correo se **entrega** al dominio real (después del corte), por eso podés confirmar; se **almacena** truncado, por eso pasás el check.
- Es la variante "avanzada" de [[vulnerabilities/015-business-logic/examples/lab-logic-flaws-inconsistent-security-controls|inconsistent controls]]: mismo objetivo (dominio admin), pero explotando el **manejo del input excepcional**.

## 🔗 Relacionados
- [[vulnerabilities/015-business-logic/business-logic|entry point]] · [[vulnerabilities/015-business-logic/labs/README|labs]]
- Vía directa del mismo dominio: [[vulnerabilities/015-business-logic/examples/lab-logic-flaws-inconsistent-security-controls|inconsistent security controls]]
