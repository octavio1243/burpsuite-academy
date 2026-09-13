---
aliases:
  - Business Logic - controles de seguridad inconsistentes
  - Inconsistent security controls
tags:
  - vuln/business-logic
  - example
  - portswigger
---

# Controles de seguridad inconsistentes (dominio del email)

> Lab: [Inconsistent security controls](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-inconsistent-security-controls) · **Apprentice** · técnica → [[vulnerabilities/015-business-logic/business-logic|entry point]]

## ¿Por qué acá? (confianza en el dominio del email)
- **La suposición que rompés:** el acceso a `/admin` se otorga a quien tenga un email `@dontwannacry.com`. El dev asume que ese dominio **solo lo tienen empleados**.
- **Por qué funciona:** el control es **inconsistente**: te deja **cambiar tu email** libremente después de registrarte, sin re-verificar que el dominio te pertenezca. Así te "ascendés" solo.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (tu subdominio del lab / el dominio admin).

1. Registrate con un email de tu propio inbox y confirmá desde el email client:
<pre class="payload"><code>algo@<mark>TU-ID.web-security-academy.net</mark></code></pre>
2. Logueá y andá a **My account → Update email**. Cambialo al dominio del admin:
<pre class="payload"><code>POST /my-account/change-email HTTP/1.1
Host: <mark>LAB.web-security-academy.net</mark>
Content-Type: application/x-www-form-urlencoded

email=<mark>algo@dontwannacry.com</mark></code></pre>
El check de privilegio confía en el dominio → aparece el link **Admin panel**.

## Verificación
Recargá y accedé a `/admin`: el panel está disponible → borrás `carlos` → lab resuelto.

## Detalles que se pasan por alto
- El registro **sí** exige verificar tu email real; el **cambio posterior** es el que no revalida el dominio.
- Es la vía **directa** del "email de la casa". La variante avanzada (cuando validan el dominio en el registro) es el **truncado a 255** → [[vulnerabilities/015-business-logic/examples/lab-logic-flaws-inconsistent-handling-of-exceptional-input|exceptional input]].

## 🔗 Relacionados
- [[vulnerabilities/015-business-logic/business-logic|entry point]] · [[vulnerabilities/015-business-logic/labs/README|labs]]
- Truncado del mismo dominio: [[vulnerabilities/015-business-logic/examples/lab-logic-flaws-inconsistent-handling-of-exceptional-input|inconsistent handling of exceptional input]]
