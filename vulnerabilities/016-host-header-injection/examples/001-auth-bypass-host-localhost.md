---
aliases:
  - Host Header 001 - auth bypass con Host localhost
  - host header authentication bypass
tags:
  - vuln/host-header
  - example
  - portswigger
---

# 001 — Bypass de autenticación con `Host: localhost`

> Lab: [Host header authentication bypass](https://portswigger.net/web-security/host-header/exploiting/lab-host-header-authentication-bypass) · **Practitioner** · técnica → [[vulnerabilities/016-host-header-injection/host-header|entry point]]

## ¿Por qué acá? (el caso base de "decisión de acceso")
- **Es el arranque más simple:** no necesitás exploit server ni Collaborator, solo **editar un header**. El server usa el `Host` para una **decisión de autorización**: `/admin` está reservado "solo para usuarios locales".
- **Por qué funciona:** la app decide "sos interno" mirando el `Host`. Ponés `Host: localhost` y te hacés pasar por una request que salió de la propia máquina → te abre el panel.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás/inyectás vos.

Interceptá la request a `/admin` y cambiá el `Host`:
<pre class="payload"><code>GET /admin HTTP/1.1
Host: <mark>localhost</mark></code></pre>
Con el panel abierto, mandá la acción de borrado:
<pre class="payload"><code>GET /admin/delete?username=<mark>carlos</mark> HTTP/1.1
Host: <mark>localhost</mark></code></pre>

## Verificación
`/admin` con `Host: localhost` devuelve el **panel de administración** (200 + HTML) en vez del `401/403` habitual, y tras el segundo request **carlos desaparece** → lab resuelto.

## Detalles que se pasan por alto
- Si `Host: localhost` no anda directo, la app puede confiar en un **header alternativo**: probá `X-Forwarded-Host: localhost` (o `127.0.0.1`). Variantes completas → [[exam/shortcuts/host-headers|shortcut de headers]].
- El auth bypass por `Host` es control de acceso roto → misma familia que [[vulnerabilities/028-access-control/access-control|access control]].

→ Siguiente: [[vulnerabilities/016-host-header-injection/examples/002-password-reset-poisoning|002 · el Host no decide acceso, sino que arma la URL de un email de reset]]
