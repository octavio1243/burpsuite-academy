---
aliases:
  - OAuth
  - oauth-entrypoint
  - redirect_uri
tags:
  - vuln/oauth
  - entrypoint
  - incompleto
---

# OAuth Authentication — Punto de entrada

> [!warning] 🚧 Documento incompleto
> Stub creado para que las referencias no queden rotas (lo enlaza [[vulnerabilities/025-dom-based/labs/README|el lab de open redirect]] y los `STAGE_x`). **Completar** las secciones marcadas `(por completar)` en otra sesión.

> Documento **agnóstico al negocio**: *cómo **explotar** OAuth*. **Dónde** aplica (qué proveedor, qué endpoint) → `STAGE_x`.

## 📚 Referencias rápidas

- 🧪 **Laboratorios** — *(por completar: listar labs de OAuth de PortSwigger, Apprentice→Expert)*
- 🔗 Se **combina** con **open redirect** (DOM o server-side) para robar el `code`/token → [[vulnerabilities/025-dom-based/dom-based|DOM-based]] · [[vulnerabilities/025-dom-based/labs/README|lab open redirect]].
- 🧰 **Método de entrega:** **exploit server** (la víctima/admin visita un link que dispara el flujo OAuth con tu `redirect_uri`).

## 🎯 Condiciones para que exista (la FLAG real)

1. **El login usa OAuth** (botón "Log in with…", flujo con `client_id`, `redirect_uri`, `response_type=code/token`, `/authorize`, `/callback`). Si no hay OAuth → no aplica.
2. Hay algún **control mal implementado**: `redirect_uri` no validado (o validado por prefijo/substring), falta de `state`, `code` reutilizable, scope mal chequeado, etc.

## 🧪 Cómo explotar (metodología)

> El vector más común y el que conecta con DOM/open-redirect: **robo del `authorization code`** vía `redirect_uri`.

### 1) `redirect_uri` no validado → robar el `code` del admin

- El servidor de autorización devuelve el `code` a la URL de `redirect_uri`. Si **no valida** ese parámetro (o lo valida débil: `startsWith`, substring, dominios permitidos por prefijo), lo apuntás a **tu exploit server**.
- Armás un link al endpoint `/authorize?...&redirect_uri=https://EXPLOIT.exploit-server.net` y **se lo entregás a la víctima/admin** (ya logueada en el proveedor). Al visitarlo, el `code` **de su sesión** llega a tu Access log.
- Con ese `code` completás el flujo (`/callback?code=...`) y **entrás como la víctima**.
- **Encadena con [open redirect](../025-dom-based/labs/README.md):** si `redirect_uri` está whitelisteado al dominio del target pero **hay un open redirect en el target**, lo usás como salto para desviar el `code` igual. → [[vulnerabilities/025-dom-based/dom-based#🐍 Plantillas (reemplazá lo resaltado)|plantilla open redirect]].

### 2) Falta de `state` → CSRF de login / account linking

- *(por completar)* Sin `state` (o sin validarlo), forzás a la víctima a **vincular tu cuenta** del proveedor a su cuenta del target, o CSRF de login.

### 3) Otros

- *(por completar)* `code`/token reutilizable, `scope` upgrade, robo por `Referer`, OpenID flaws, SSRF en OIDC discovery, etc.

## 🐍 Plantillas

- *(por completar)* link de robo de `code`, página que fuerza el flujo, etc.

> [!note] Relación con otras vulns
> - **Open redirect** (DOM/server) = la munición clásica para saltarse un `redirect_uri` whitelisteado → [[vulnerabilities/025-dom-based/dom-based|DOM-based]].
> - El `code`/token robado se entrega por **exploit server** (víctima/admin logueada visita) → misma mecánica de víctima que CSRF/clickjacking/XSS entregado.
