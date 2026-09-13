---
aliases:
  - Access Control 002 - escalada vertical a /admin sin proteger
  - unprotected admin functionality vertical
tags:
  - vuln/access-control
  - example
  - portswigger
---

# 002 — Escalada vertical: función de admin sin protección

> Lab: [Unprotected admin functionality](https://portswigger.net/web-security/access-control/lab-unprotected-admin-functionality) · **Apprentice** · técnica → [[vulnerabilities/028-access-control/access-control|entry point]]

## ¿Por qué acá? (el caso base vertical)
- **Es el arquetipo de acceso vertical por "obscurity":** el panel admin existe y **no está protegido**; solo está *escondido*. Si descubrís la URL, entrás.
- **Por qué funciona:** la app confía en que nadie conoce la ruta en vez de comprobar el rol → cualquiera que la encuentre ejecuta funciones de admin.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = la ruta admin que descubrís + la víctima a borrar.

Buscá dónde se filtra la ruta. Empezá por `/robots.txt`:
<pre class="payload"><code>GET /robots.txt HTTP/1.1
Host: LAB.web-security-academy.net</code></pre>
Revela `Disallow: /administrator-panel`. Entrá directo y usá la acción de borrado:
<pre class="payload"><code>GET /<mark>administrator-panel</mark> HTTP/1.1
Host: LAB.web-security-academy.net</code></pre>
Desde el panel, borrá a <mark>carlos</mark>.

## Verificación
El panel admin carga (200 + HTML con la lista de usuarios) sin credenciales de admin; tras el borrado **carlos desaparece** → lab resuelto.

## Detalles que se pasan por alto
- Si `robots.txt` no la revela, la URL puede estar **hardcodeada en el JavaScript** de la home (variante con "URL impredecible") → grepeá el JS por `admin`.
- No confundir con bypass de plataforma: acá **no hay control**; en [[vulnerabilities/028-access-control/examples/004-bypass-plataforma-header-url|004]] el control existe pero se saltea.

→ Siguiente: [[vulnerabilities/028-access-control/examples/003-mass-assignment-roleid|003 · auto-escalada por mass assignment del rol]]
