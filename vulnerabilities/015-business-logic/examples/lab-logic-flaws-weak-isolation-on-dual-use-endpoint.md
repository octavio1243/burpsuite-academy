---
aliases:
  - Business Logic - endpoint de doble uso
  - Weak isolation on dual-use endpoint
tags:
  - vuln/business-logic
  - example
  - portswigger
---

# Aislamiento débil en endpoint de doble uso

> Lab: [Weak isolation on dual-use endpoint](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-weak-isolation-on-dual-use-endpoint) · **Practitioner** · técnica → [[vulnerabilities/015-business-logic/business-logic|entry point]]

## ¿Por qué acá? (reusar un endpoint para otra cosa)
- **La suposición que rompés:** `change-password` es un endpoint de **doble uso** (cambiar tu pass o resetear la de otro). El dev asume que `username` siempre sos vos y que `current-password` siempre viaja.
- **Por qué funciona:** si **borrás `current-password`**, el server no exige la clave actual, y si cambiás `username=administrator`, aplica el cambio sobre **otra cuenta**. No hay aislamiento entre "yo cambio mi pass" y "yo cambio la del admin".

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás/borrás vos.

Login `wiener:peter`, capturá el `POST /my-account/change-password` y mandalo a Repeater. **Eliminá el parámetro `current-password` entero**, apuntá `username` al admin y poné una new password:
<pre class="payload"><code>POST /my-account/change-password HTTP/1.1
Host: <mark>LAB.web-security-academy.net</mark>
Content-Type: application/x-www-form-urlencoded

username=<mark>administrator</mark>&new-password-1=<mark>hacked</mark>&new-password-2=<mark>hacked</mark></code></pre>
(Fijate que **no** hay `current-password` en el body.) Envialo → sobreescribís la pass del admin. Logueá como `administrator:hacked`.

## Verificación
El login como `administrator` funciona con la clave que seteaste → entrás al admin panel → borrás `carlos` → lab resuelto.

## Detalles que se pasan por alto
- **Borrar el parámetro, no vaciarlo:** dejar `current-password=` (vacío) puede fallar; hay que **quitar la línea entera**.
- `new-password-1` y `new-password-2` tienen que coincidir.
- Es el patrón "endpoint de doble uso": quitás el param "de seguridad" y apuntás `username` a la víctima.

## 🔗 Relacionados
- [[vulnerabilities/015-business-logic/business-logic|entry point]] · [[vulnerabilities/015-business-logic/labs/README|labs]]
- Otra toma de cuenta sin credenciales: [[vulnerabilities/015-business-logic/examples/lab-logic-flaws-authentication-bypass-via-flawed-state-machine|flawed state machine]]
