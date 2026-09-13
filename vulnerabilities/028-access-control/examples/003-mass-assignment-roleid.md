---
aliases:
  - Access Control 003 - mass assignment roleid
  - privilege escalation role in request
tags:
  - vuln/access-control
  - example
  - portswigger
---

# 003 — Auto-escalada por mass assignment del rol

> Lab: [User role can be modified in user profile](https://portswigger.net/web-security/access-control/lab-user-role-can-be-modified-in-user-profile) · **Apprentice** · técnica → [[vulnerabilities/028-access-control/access-control|entry point]]

## ¿Por qué acá? (la decisión de rol viaja en la request)
- **Variante vertical más peligrosa:** no buscás una URL escondida; **te asignás el rol vos mismo** metiendo el campo de privilegio en una request legítima.
- **Por qué funciona:** el endpoint de update de perfil **bindea todos los campos del JSON** al objeto usuario (mass assignment). Si agregás `roleid`, la app lo persiste sin validar.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = el campo de rol que inyectás y su valor de admin.

Primero descubrí el nombre del campo: hacé un `GET` a tu perfil/API y fijate qué devuelve (`"roleid":1`). Después, en el update de email agregá ese campo con el valor de admin:
<pre class="payload"><code>POST /my-account/change-email HTTP/1.1
Host: LAB.web-security-academy.net
Content-Type: application/json
Cookie: session=...

{"email":"test@test.com",<mark>"roleid":2</mark>}</code></pre>

## Verificación
La respuesta refleja `"roleid":2`; recargá y ahora tenés acceso al **panel admin** → borrá a carlos → lab resuelto.

## Detalles que se pasan por alto
- **El nombre y valor del campo se descubren, no se adivinan:** miralos en la **respuesta** del `GET` al perfil (o en un update de admin de muestra). Acá es `roleid:2`, pero puede ser `role`, `isAdmin`, etc.
- Meté el campo en el **mismo JSON** que la app ya acepta; agregarlo suelto en otro endpoint no lo bindea.

→ Siguiente: [[vulnerabilities/028-access-control/examples/004-bypass-plataforma-header-url|004 · el control existe pero se saltea por header/URL]]
