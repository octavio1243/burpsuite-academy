---
aliases:
  - Access Control 004 - bypass de plataforma por header/URL
  - url method based access control bypass
tags:
  - vuln/access-control
  - example
  - portswigger
---

# 004 — Bypass de plataforma: el control existe pero se saltea (URL / método / Referer)

> Lab: [URL-based access control can be circumvented](https://portswigger.net/web-security/access-control/lab-url-based-access-control-can-be-circumvented) · **Practitioner** · técnica → [[vulnerabilities/028-access-control/access-control|entry point]]

## ¿Por qué acá? (el control está mal ubicado)
- **Distinto a 002:** acá el control **sí existe**, pero vive en una capa (front-end / método / Referer) que no cubre todos los caminos → se lo esquiva sin credenciales.
- **Por qué funciona:** el front bloquea `GET /admin`, pero el back-end respeta cabeceras de reescritura de URL (`X-Original-URL` / `X-Rewrite-URL`). El front ve `POST /` (permitido) y el back procesa `/admin`.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = la ruta admin real que metés en el header + la víctima.

Confirmá que `GET /admin` da 403. Después mandá la request a la raíz con el header de reescritura:
<pre class="payload"><code>POST / HTTP/1.1
Host: LAB.web-security-academy.net
X-Original-URL: <mark>/admin/delete</mark>
Content-Type: application/x-www-form-urlencoded

username=<mark>carlos</mark></code></pre>
Si el path lleva query, va como parámetro (o `X-Original-URL: /admin/delete?username=carlos`).

## Verificación
El back procesa la ruta admin (no 403) y **carlos se borra** → lab resuelto.

## Detalles que se pasan por alto
- **Otras variantes del mismo patrón** (probalas todas):
  - **Método** → si el check solo cubre `POST`, cambialo a `GET` (method-based). 🔁
  - **Referer** → si el back confía en `Referer`, replay la acción de admin con tu cookie manteniendo `Referer: https://LAB…/admin`.
  - **URL matching** → slash final, mayúsculas, o `.anything` (Spring `useSuffixPatternMatch`).
- `X-Original-URL` **no** cambia el path que ve el front (por eso pasa el filtro); sí el que resuelve el back.

→ Fin de la serie core. Volvé al [[exam/to-do-list/access-control|to-do de Access Control]] para el checklist completo.
