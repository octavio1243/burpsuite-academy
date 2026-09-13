---
aliases:
  - JWT
  - jwt-attacks
  - jwk
  - jku
  - kid
tags:
  - vuln/jwt
  - entrypoint
---

# JWT attacks — Punto de entrada

> Documento **agnóstico**: *cómo funciona un JWT* (teoría mínima) para entender los ataques. La explotación lab por lab → [[vulnerabilities/018-jwt-attacks/labs/README|labs de JWT]].

## 🧠 Cómo funciona un JWT (how-to-work)

Un **JWT** es un token que lleva datos (claims) y una **firma** que prueba que nadie los tocó. Son **3 partes en Base64url separadas por puntos**:

```
<Header>.<Payload>.<Signature>
```

### Header
JSON con **metadata del token**: qué algoritmo lo firma y (opcionalmente) **con qué clave** verificarlo.
```json
{ "typ": "JWT", "alg": "HS256" }
```
- `alg` → algoritmo de firma (`HS256`, `RS256`, …).
- `typ` → tipo (casi siempre `JWT`).
- **Selección de clave (opcional):** `kid`, `jwk`, `jku` (ver abajo — **acá viven los bugs de header injection**).

### Payload
JSON con los **claims** (los datos). **Base64url, NO cifrado → cualquiera lo lee.** La firma protege que no se **modifiquen**, no que no se **vean**.
```json
{ "sub": "wiener", "iss": "portswigger", "exp": 1786914938 }
```
- `sub` (usuario), `iss` (emisor), `exp` (expiración), `iat`… + custom (`role`, `isAdmin`).

### Signature
Garantiza **integridad**. Se calcula sobre `Base64url(Header) + "." + Base64url(Payload)`. Dos familias:
- **Simétrica — `Hash(Header, Payload)` con secreto** (HMAC, `HS256`): `HMAC-SHA256(data, secreto)`. **El mismo secreto firma y verifica** → si el secreto es débil, se crackea.
- **Asimétrica — `Encrypt(Hash(Header, Payload))`** (RSA/ECDSA, `RS256`): se hashea y el hash se **firma con la clave privada**; se **verifica con la pública**. Nunca deberías poder firmar… salvo bugs (algorithm confusion, key injection).

## 🔐 Algoritmos: simétrico vs asimétrico

Cómo se genera y verifica la firma depende del tipo de clave del `alg`:

- **`HS256` (HMAC + SHA-256) → simétrico:** el server usa **una sola clave** (un secreto) para **firmar y verificar**. Quien tiene el secreto puede hacer ambas cosas.
- **`RS256` (RSA + SHA-256) → asimétrico:** usa un **par de claves**. La **privada** (solo el server) **firma**; la **pública** (matemáticamente relacionada, y que puede ser conocida) solo **verifica**.

| | **HS256** (simétrico) | **RS256** (asimétrico) |
| --- | --- | --- |
| Clave para **firmar** | el **secreto** compartido | clave **privada** |
| Clave para **verificar** | el **mismo secreto** | clave **pública** |
| ¿El que verifica puede firmar? | **Sí** (misma clave) | **No** (solo con la privada) |
| Riesgo típico | secreto **débil → se crackea** | **algorithm confusion** / key injection |

**Ejemplo (mismos claims, distinta firma):**
```
data = base64url(Header) + "." + base64url(Payload)

HS256:  signature = HMAC_SHA256(data, secreto)          → verificar = recalcular con el MISMO secreto y comparar
RS256:  signature = RSA_sign(SHA256(data), privateKey)  → verificar = RSA_verify(data, signature, publicKey)
```

> **Por qué importa para atacar:** en **HS256** basta conseguir/adivinar el secreto para forjar tokens (lab weak key). En **RS256** no podés forjar sin la privada… salvo que el server **confunda el algoritmo** y verifique un `HS256` usando la **clave pública como secreto** (algorithm confusion).

## 🔑 `kid`, `jwk`, `jku` (cómo el server elige la clave)

Son campos del **header** que le dicen al verificador **qué clave usar**. Si la app confía en ellos sin validar, vos controlás la clave → forjás tokens.

- **`kid` (Key ID):** un **identificador** que apunta a la clave (índice en un JWKS, o a veces un **path/registro**). Bug: **path traversal** / SQLi si se usa sin sanitizar.
  ```json
  { "kid": "ed2Nf8sb-sD6ng0-scs5390g-fFD8sfxG", "typ": "JWT", "alg": "RS256" }
  ```
- **`jwk` (JSON Web Key):** la clave pública **embebida dentro del propio token**. Bug: el server verifica con la clave que **vos** metiste.
  ```json
  {
    "kid": "ed2Nf8sb-sD6ng0-scs5390g-fFD8sfxG",
    "typ": "JWT",
    "alg": "RS256",
    "jwk": {
      "kty": "RSA",
      "e": "AQAB",
      "kid": "ed2Nf8sb-sD6ng0-scs5390g-fFD8sfxG",
      "n": "yy1wpYmffgXBxhAUJzHHocCuJolwDqql75ZWuCQ_cb33K2vh9m"
    }
  }
  ```
- **`jku` (JWK Set URL):** una **URL** que apunta a un **JWK Set** (un `{ "keys": [...] }` con varias claves públicas). Bug: si no valida el dominio, apuntás el `jku` a **tu** server.
  ```json
  {
    "keys": [
      {
        "kty": "RSA",
        "e": "AQAB",
        "kid": "75d0ef47-af89-47a9-9061-7c02a610d5ab",
        "n": "o-yy1wpYmffgXBxhAUJzHHocCuJolwDqql75ZWuCQ_cb33K2vh9mk6GPM9gNN4Y_qTVX67WhsN3JvaFYw-fhvsWQ"
      },
      {
        "kty": "RSA",
        "e": "AQAB",
        "kid": "d8fDFo-fS9-faS14a9-ASf99sa-7c1Ad5abA",
        "n": "fc3f-yy1wpYmffgXBxhAUJzHql79gNNQ_cb33HocCuJolwDqmk6GPM4Y_qTVX67WhsN3JvaFYw-dfg6DH-asAScw"
      }
    ]
  }
  ```
  > El `kid` del token **elige cuál** de las claves del `keys[]` se usa para verificar.

## 🔀 JWT vs JWS vs JWE

- **JWT (JSON Web Token):** el estándar del **token con claims**. Es el "qué". En la práctica, un JWT casi siempre está implementado como un **JWS**.
- **JWS (JSON Web Signature):** contenido **firmado** → da **integridad/autenticidad**. El payload es **legible** (Base64url, no cifrado). **3 partes.** Es lo que ves normalmente.
- **JWE (JSON Web Encryption):** contenido **cifrado** → da **confidencialidad**. El payload **no se puede leer**. **5 partes.**

| | **JWS** (lo normal) | **JWE** |
| --- | --- | --- |
| Qué aporta | Firma (integridad) | Cifrado (confidencialidad) |
| ¿Se lee el payload? | **Sí** (Base64url) | **No** |
| Nº de partes | **3** (`h.p.s`) | **5** |
| Se ataca por… | firma mal verificada / key injection | mucho más raro en labs |

> **Regla práctica:** casi todos los JWT que vas a atacar son **JWS**. El objetivo del atacante es **modificar un claim** (`sub → administrator`) y lograr que la **firma se valide igual** — porque no se verifica, es débil, o el server confía en `kid`/`jwk`/`jku` que vos controlás.

## 💥 Ataques comunes (y ejemplos)

Todos buscan lo mismo: **tocar un claim** (típico `sub → administrator`) y que la **firma valide igual**. Se agrupan según qué parte del JWT abusás.

### En el Header
- **`alg: none` + borrar la firma** — el server acepta tokens "sin firmar". Ponés `"alg":"none"`, editás el payload y dejás el token como `header.payload.` (**con el punto final**, firma vacía). → labs [L2].
- **`jwk` injection (self-signed JWT)** — embebés **tu** clave pública en el header `jwk`; si la implementación **le da prioridad a la clave que viene en el token**, verifica con la tuya. Firmás vos con tu privada. → [L4].
- **`jku` injection (self-signed JWT)** — apuntás `jku` a un **JWK Set en tu server**; si no valida el dominio, el server descarga tu clave y verifica con ella. → [L5].
- **`kid` injection (self-signed JWT)** — si `kid` es una **referencia a un archivo**, hacés **path traversal** a uno de contenido predecible (ej. `/dev/null` → vacío) y firmás con esa clave "conocida":
  ```json
  {
      "kid": "../../path/to/file",
      "typ": "JWT",
      "alg": "HS256",
      "k": "asGsADas3421-dfh9DGN-AFDFDbasfd8-anfjkvc"
  }
  ```
  → [L6].

### En el Payload
- **Tamper de claims** — cambiás el claim que decide privilegios: `"sub":"administrator"`, `"isAdmin": true`, `"role":"admin"`, etc. Funciona directo si el server **no verifica la firma**. → [L1].

### En la Signature
- **Bruteforce del secreto (HMAC)** — si es `HS256` con secreto débil, lo crackeás con **hashcat** (`-m 16500`) + wordlist → firmás tokens válidos. → [L3] · script `scripts/crack_jwt.py`.
- **Algorithm confusion (RS256 → HS256)** — usás la **clave pública** del server como **secreto HMAC**. Necesitás la pública (ver abajo). → [L7].
- **Derivar la clave pública de tokens existentes** — cuando la pública **no está publicada**: juntás **2 JWT** del mismo server y con **`sig2n` / `rsa_sign2n`** (Docker) reconstruís **candidatos** de la pública; probás cuál valida y con esa hacés algorithm confusion. → [L8].
- **Encontrar las claves JWT (JWKS)** — la pública suele estar expuesta en:
  ```
  /jwks.json
  /.well-known/jwks.json
  ```

> Los `[Lx]` remiten a la tabla de [[vulnerabilities/018-jwt-attacks/labs/README|labs de JWT]], donde está la solución paso a paso de cada uno.

> [!note] Seguir
> - **Labs** (8, con objetivo y solución paso a paso) → [[vulnerabilities/018-jwt-attacks/labs/README|labs de JWT]].
> - **Scripts** (crackear HMAC débil con hashcat) → `vulnerabilities/018-jwt-attacks/scripts/`.
> - El **`id_token`** de OpenID Connect es un JWT → [[vulnerabilities/026-oauth/oauth|oauth]].
