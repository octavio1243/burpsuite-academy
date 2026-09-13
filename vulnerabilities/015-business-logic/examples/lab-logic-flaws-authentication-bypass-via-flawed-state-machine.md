---
aliases:
  - Business Logic - máquina de estados rota
  - Authentication bypass via flawed state machine
tags:
  - vuln/business-logic
  - example
  - portswigger
---

# Bypass de autenticación por máquina de estados rota

> Lab: [Authentication bypass via flawed state machine](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-authentication-bypass-via-flawed-state-machine) · **Practitioner** · técnica → [[vulnerabilities/015-business-logic/business-logic|entry point]]

## ¿Por qué acá? (saltar un paso del flujo)
- **La suposición que rompés:** el dev asume que el login es un flujo de **dos pasos** — primero `POST /login`, después `GET /role-selector` donde elegís rol. Confía en que **siempre** vas a pasar por el segundo paso.
- **Por qué funciona:** si nunca corrés el `role-selector`, la sesión **conserva el rol por defecto**, que resulta ser `administrator`. Saltar el paso no te baja privilegios: te los deja intactos.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que tocás vos (el request que **dropeás**).

Logout → login con **intercept ON**. Forwardeá el `POST /login`, y cuando aparezca el segundo request, **dropealo**:
<pre class="payload"><code>POST /login HTTP/1.1     → Forward
GET /role-selector HTTP/1.1     → <mark>Drop</mark></code></pre>
Apagá el intercept y navegá a la home o directo a `/admin`. La sesión sigue con rol admin porque el paso que lo "ajustaba" nunca corrió:
<pre class="payload"><code>GET <mark>/admin</mark> HTTP/1.1
Host: <mark>LAB.web-security-academy.net</mark></code></pre>

## Verificación
`/admin` responde el panel (no un 401/redirect), y desde ahí borrás a `carlos` → lab resuelto.

## Detalles que se pasan por alto
- **Drop, no forward:** si forwardeás el `role-selector` te asigna el rol normal y perdés el default admin.
- Es la variante "limpia" de máquina de estados: no hay parámetro que tocar, solo **omitir** un request.
- Mismo objetivo final que el resto de Stage 2: **admin → borrar `carlos`**.

## 🔗 Relacionados
- [[vulnerabilities/015-business-logic/business-logic|entry point]] · [[vulnerabilities/015-business-logic/labs/README|labs]]
- Otra vía de toma de cuenta sin tocar valores: [[vulnerabilities/015-business-logic/examples/lab-logic-flaws-weak-isolation-on-dual-use-endpoint|weak isolation]]
