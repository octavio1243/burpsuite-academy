---
aliases:
  - JWT labs
  - jwt-labs
tags:
  - vuln/jwt
  - labs
  - portswigger
---

# JWT attacks — Labs de PortSwigger

> 🧠 ¿Cómo funciona un JWT (formato, firma, `kid`/`jwk`/`jku`, JWS vs JWE)? → [[vulnerabilities/018-jwt-attacks/jwt-attacks|teoría / punto de entrada]].

Labs de la categoría **[JWT attacks](https://portswigger.net/web-security/jwt)**: **2 Apprentice + 4 Practitioner + 2 Expert** (8 en total). **El hilo común:** el server guarda tu identidad en un **JWT** (típicamente `sub: wiener`) y **confía en los claims** que van adentro. La firma existe justamente para que **no puedas tocar esos claims**… pero en cada lab la **verificación de la firma está rota** de una forma distinta. **El objetivo es siempre el mismo:** forjar un token con **`sub: administrator`** (a veces `role`/`isAdmin`), que el server lo acepte, entrar a **`/admin`** y **borrar a `carlos`**. Lo que cambia lab a lab es **por qué** el server acepta tu firma falsa.

> [!note] Cuatro "sabores" de JWT attack (según qué rompe la verificación)
> - **No verifica la firma (o acepta `alg:none`):** el server lee los claims sin validar la firma, o acepta tokens "sin firmar". Cambiás `sub` y listo. Labs 1, 2.
> - **Secreto débil (HMAC):** el token está firmado con HS256 pero con un secreto **adivinable** → lo **crackeás** (hashcat/wordlist) y firmás vos tokens válidos. Lab 3.
> - **Inyección de key material en el header:** el server confía en que **vos** le digas **con qué clave** verificar → le pasás **tu** clave por `jwk` (embebida), `jku` (URL a tu JWKS) o `kid` (path traversal a un archivo predecible). Labs 4, 5, 6.
> - **Algorithm confusion (RS256 → HS256):** el server **firma con RSA** (asimétrico: clave privada firma, pública verifica) pero **no fija el algoritmo** al verificar → cambiás `alg` a HS256 y firmás con la **clave pública** (que es, del server) usada como **secreto HMAC**. Labs 7, 8.

> **Herramienta central:** la extensión **JWT Editor** (BApp store). Agrega una pestaña para **decodificar/editar** el JWT en Repeater/Proxy y una pestaña **"JWT Editor Keys"** para crear claves (RSA / simétricas) y **firmar**. **Cómo leer las columnas:** **Qué falla en la verificación** = por qué el server traga tu token · **Técnica · qué necesitás** = cómo forjás la firma + herramientas · **Objetivo** = qué conseguís. Pasos completos → sección [Solución por lab](#solución-por-lab).

## Apprentice

| #   | Laboratorio                                                                                                                              | Qué falla en la verificación                                                              | Técnica · qué necesitás                                                                                                                                                              | Objetivo                                                                              |
| --- | -------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| 1   | [JWT authentication bypass via unverified signature](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-unverified-signature) | **No verifica la firma:** el server decodifica los claims pero **no valida** la firma.    | **Editar el payload y nada más:** cambiás `sub` a `administrator` en la pestaña JWT Editor y reenviás. **No hace falta re-firmar.** Sólo Burp + JWT Editor.                          | `sub: administrator` → `/admin` → **borrar a `carlos`**.                               |
| 2   | [JWT authentication bypass via flawed signature verification](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-flawed-signature-verification) | **Acepta `alg: none`:** trata como válido un token **sin firma** si el algoritmo es `none`. | **Downgrade a `none`:** cambiás `sub` a `administrator`, ponés `"alg":"none"` en el header y **borrás la firma dejando el punto final** (`header.payload.`). Sólo Burp + JWT Editor. | Token no firmado con `sub: administrator` → `/admin` → **borrar a `carlos`**.          |

## Practitioner

| #   | Laboratorio                                                                                                                          | Qué falla en la verificación                                                                                                    | Técnica · qué necesitás                                                                                                                                                                                                                                                | Objetivo                                                                    |
| --- | -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| 3   | [JWT authentication bypass via weak signing key](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-weak-signing-key) | **Secreto HMAC débil:** HS256 firmado con un secreto **adivinable** (`secret1`).                                                | **Brute force del secreto:** crackeás el JWT con **hashcat** (`-m 16500`) + wordlist de secretos comunes → `secret1`. Creás una **Symmetric Key** con ese secreto (Base64) en JWT Editor y **firmás** el token con `sub: administrator`. → script `crack_jwt.py`.       | Crackear el secreto → firmar `sub: administrator` → `/admin` → borrar `carlos`. |
| 4   | [JWT authentication bypass via jwk header injection](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-jwk-header-injection) | **Confía en el `jwk` del header:** verifica con la **clave pública embebida en el propio token**, sin comprobar que sea la suya. | **Embedded JWK:** generás un **par RSA** en JWT Editor, cambiás `sub` a `administrator` y usás el ataque **"Embedded JWK"** (firma con tu privada y mete tu pública en el header `jwk`). El server verifica con **tu** clave. Sólo Burp + JWT Editor.                     | Firmar con tu RSA + `jwk` embebido → `/admin` → borrar `carlos`.             |
| 5   | [JWT authentication bypass via jku header injection](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-jku-header-injection) | **Confía en el `jku` (URL) del header:** va a buscar la clave de verificación a la URL que **vos** indiques, sin validar el dominio. | **JKU apuntando a tu JWKS:** generás un par RSA, **hospedás tu JWK Set** (`{"keys":[...]}`) en el **exploit server**, y en el token ponés `jku` = tu URL, `kid` = el de tu clave, `sub: administrator`, firmado con tu privada. Necesitás **exploit server**.            | Que el server traiga tu clave por `jku` → `/admin` → borrar `carlos`.        |
| 6   | [JWT authentication bypass via kid header path traversal](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-kid-header-path-traversal) | **`kid` sin sanitizar:** usa `kid` como **ruta de archivo** para cargar la clave → **path traversal** a un archivo predecible.   | **`kid` → `/dev/null`:** apuntás `kid` a `../../../../../../dev/null` (contenido **vacío/predecible**) y creás una **Symmetric Key** cuyo `k` sea ese valor conocido (null byte, `AA==`). Firmás HS256 con esa clave. Sólo Burp + JWT Editor.                            | Forzar una clave conocida vía `kid` → `/admin` → borrar `carlos`.           |

## Expert

| # | Laboratorio | Qué falla en la verificación | Técnica · qué necesitás | Objetivo |
| --- | --- | --- | --- | --- |
| 7 | [JWT authentication bypass via algorithm confusion](https://portswigger.net/web-security/jwt/algorithm-confusion/lab-jwt-authentication-bypass-via-algorithm-confusion) | **No fija el algoritmo:** firma con **RS256** (asimétrico) pero acepta **HS256** al verificar, usando la **clave pública como secreto**. | **RS256 → HS256:** bajás la **clave pública** de `/jwks.json`, la convertís a **PEM**, la **Base64**-eás y la usás como **Symmetric Key**. Cambiás `alg` a HS256 + `sub: administrator` y firmás con esa "clave". Sólo Burp + JWT Editor. | Firmar HS256 con la pública del server → `/admin` → borrar `carlos`. |
| 8 | [Algorithm confusion with no exposed key](https://portswigger.net/web-security/jwt/algorithm-confusion/lab-jwt-authentication-bypass-via-algorithm-confusion-with-no-exposed-key) | Igual que el 7 **pero la clave pública NO está expuesta** (no hay `/jwks.json`). | **Derivar la pública de 2 tokens:** juntás **2 JWTs** del server y con el tool **`sig2n`/`rsa_sign2n`** (Docker) calculás los **candidatos** de clave pública. Probás cuál valida, y con esa clave repetís el ataque del 7. Necesitás **Docker** (`portswigger/sig2n`). | Reconstruir la pública → algorithm confusion → `/admin` → borrar `carlos`. |

---

## Solución por lab

> Instalá **JWT Editor** (Extensions → BApp Store). En Repeater aparece la pestaña **"JSON Web Token"** (edita header/payload y tiene botón **Sign**); arriba está **"JWT Editor Keys"** para crear/importar claves. El **borrado de carlos** es `GET /admin/delete?username=carlos` (o el botón Delete del panel).

**L1 — Unverified signature (sólo editar el payload):**
1. Logueate como `wiener:peter` y mandá la request con el JWT a **Repeater**.
2. En la pestaña **JSON Web Token**, cambiá `"sub":"wiener"` → `"sub":"administrator"`.
3. Enviá tal cual (la firma queda inválida, **pero el server no la chequea**). Andá a `/admin` → borrá a `carlos`.

**L2 — `alg: none` (token sin firma):**
1. En Repeater, editá el payload: `"sub":"administrator"`.
2. Editá el header: `"alg":"none"`.
3. **Borrá la firma** pero **dejá el punto final**: el token queda `BASE64(header).BASE64(payload).`
   > En JWT Editor podés usar el botón de ataque **"none"** que hace esto automáticamente.
4. Enviá → `/admin` → borrar `carlos`.

**L3 — Weak signing key (crackear el secreto):**
1. Copiá el JWT y crackealo. Con **hashcat**:
   ```
   hashcat -a 0 -m 16500 <JWT> jwt.secrets.list        # → recupera: secret1
   ```
   > O usá el script del repo: pegá el JWT en `crack_jwt.py` y corré `python crack_jwt.py` (usa hashcat `-m 16500` + `jwt.secrets.list`). → `vulnerabilities/018-jwt-attacks/scripts/crack_jwt.py`
2. **JWT Editor Keys** → **New Symmetric Key** → Generate → reemplazá el `k` por el **Base64url de `secret1`**.
3. En Repeater: `"sub":"administrator"` → **Sign** con esa clave (HS256).
4. Enviá → `/admin` → borrar `carlos`.

**L4 — jwk header injection (Embedded JWK):**
1. **JWT Editor Keys** → **New RSA Key** → Generate.
2. En Repeater, payload: `"sub":"administrator"`.
3. Botón **Attack** → **"Embedded JWK"** → elegí tu clave. Firma con tu privada y embebe tu **pública** en el header `jwk`.
4. Enviá → el server verifica con **tu** clave → `/admin` → borrar `carlos`.

**L5 — jku header injection (JWKS en tu server):**
1. **New RSA Key** en JWT Editor. Copiá su representación **JWK pública**.
2. En el **exploit server** serví un JWK Set (Content-Type `application/json`):
   ```json
   { "keys": [ { PEGÁ_ACÁ_TU_JWK_PÚBLICO } ] }
   ```
3. En Repeater, header del JWT:
   - `"jku":"https://TU-EXPLOIT-SERVER.exploit-server.net/.well-known/jwks.json"`
   - `"kid":"EL-KID-DE-TU-CLAVE"` (el mismo `kid` que en tu JWKS)
   - payload: `"sub":"administrator"`
4. **Sign** con tu clave RSA (RS256) → enviá. El server descarga tu JWKS por `jku`, encuentra tu clave por `kid`, valida → `/admin` → borrar `carlos`.

**L6 — kid path traversal (`/dev/null`):**
1. **JWT Editor Keys** → **New Symmetric Key** → Generate → reemplazá `k` por **`AA==`** (Base64 de un null byte, contenido "conocido").
2. En Repeater, header: `"kid":"../../../../../../../dev/null"` (el server lee ese archivo **vacío** como clave).
3. payload: `"sub":"administrator"` → **Sign** (HS256) con esa Symmetric Key.
4. Enviá → el server firma/valida con el "contenido" de `/dev/null` (= tu clave conocida) → `/admin` → borrar `carlos`.

**L7 — Algorithm confusion (RS256 → HS256, con clave expuesta):**
1. Bajá la clave pública: `GET /jwks.json` (o `/.well-known/jwks.json`).
2. **JWT Editor Keys** → **New RSA Key** → pegá el **JWK** de la respuesta.
3. Click derecho sobre esa clave → **Copy Public Key as PEM**. **Base64**-eá ese PEM entero.
4. **New Symmetric Key** → Generate → reemplazá `k` por el **Base64 del PEM**.
5. En Repeater: header `"alg":"HS256"`, payload `"sub":"administrator"` → **Sign** con la Symmetric Key.
6. Enviá → el server usa su **pública** como secreto HMAC y valida tu token → `/admin` → borrar `carlos`.

**L8 — Algorithm confusion sin clave expuesta (derivarla):**
1. Logueate **dos veces** y guardá **2 JWTs** distintos del mismo server.
2. Derivá los candidatos de clave pública con **sig2n** (Docker):
   ```
   docker run --rm -it portswigger/sig2n <TOKEN_1> <TOKEN_2>
   ```
   > Devuelve varios **X.509 PEM** candidatos y, para cada uno, un **JWT ya tampereado y firmado en HS256** con ese candidato como secreto.
3. **Probá cada JWT tampereado** contra un endpoint autenticado (ej. `GET /my-account`): el que devuelve **200** identifica la **clave correcta** (`Tampered JWT (X.509)`).
4. Tomá ese PEM/clave, creá la **Symmetric Key** en JWT Editor (Base64 del PEM), y repetí el **L7**: `alg:HS256` + `sub:administrator` → **Sign** → `/admin` → borrar `carlos`.

---

## Atajos mentales / patrones

- **La pista de que hay JWT:** una cookie/token con **3 partes separadas por `.`** que empiezan en `eyJ...` (`eyJ` = `{"` en Base64). Decodificá header y payload (son Base64**url**, sin padding). El header trae `alg` y a veces `kid`/`jwk`/`jku`.
- **Siempre probá primero lo barato** (labs 1 y 2): cambiá un claim **sin re-firmar** (¿verifica la firma?) y probá **`alg:none`** con la firma borrada. Muchos bugs reales son eso.
- **`alg` = simétrico vs asimétrico:**
  - `HS256/384/512` → **HMAC**, un **secreto compartido**. Si es débil → **crackealo** (hashcat `-m 16500`). Si el server confunde algoritmos → **algorithm confusion**.
  - `RS256/ES256` → **asimétrico**, privada firma / **pública** verifica. Nunca deberías poder firmar… salvo que el server acepte HS256 (confusion) o confíe en key material que vos controlás.
- **Header params que son key material controlable (labs 4-6)** — la app **nunca** debería confiar en ellos sin whitelist:
  - `jwk` → clave **embebida** en el token (embedded JWK).
  - `jku` → **URL** de un JWKS (apuntala a tu exploit server).
  - `kid` → **id/ruta** de la clave → **path traversal** (`/dev/null`, o SQLi si el `kid` va a una DB).
- **Algorithm confusion (labs 7-8):** el ataque estrella cuando el server usa RSA pero no fija el `alg`. La clave es tratar la **pública** (que es, del server) como **secreto HMAC**. Si no está publicada (`/jwks.json`), se **reconstruye** con `sig2n` a partir de 2 tokens.
- **JWT Editor — operaciones clave:** *New RSA Key* / *New Symmetric Key* (pestaña Keys) · botón **Sign** (elige clave y `alg`) · **Attack → Embedded JWK** (lab 4) · botón **none** (lab 2). El `k` de una Symmetric Key es **Base64url**.
- **El objetivo casi siempre es el mismo:** `sub → administrator`, entrar a `/admin`, y **`GET /admin/delete?username=carlos`**. Confirmá primero que el token tampereado te deja entrar a `/admin` antes de disparar el delete.
- **Otros claims a mirar** además de `sub`: `role`, `isAdmin`, `iss`, y **`exp`** (si expiró, el token válido deja de andar → generá uno nuevo).

> [!note] Ver también
> - **Scripts del repo:** `crack_jwt.py` (hashcat `-m 16500` + `jwt.secrets.list`) para el L3 → `vulnerabilities/018-jwt-attacks/scripts/`.
> - **OAuth / OpenID:** el **`id_token`** de OpenID Connect **es un JWT firmado** → todo esto aplica si su validación es débil → [[vulnerabilities/026-oauth/oauth|oauth]] · [[vulnerabilities/026-oauth/labs/README|labs OAuth]].
> - **Toma de cuenta / bypass de auth** en general → [[vulnerabilities/029-authentication/authentication|authentication]] · [[vulnerabilities/028-access-control/access-control|access control]].
