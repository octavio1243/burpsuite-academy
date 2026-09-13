# Cómo funciona un JWT (y JWS / JWE)

> Base **conceptual**: qué es un JWT, cómo se forma la firma, algoritmos simétricos vs asimétricos, y `kid`/`jwk`/`jku`.
> **Cómo se explota** (ataques, ejemplos, labs) → [[vulnerabilities/018-jwt-attacks/jwt-attacks|entry point de JWT]].

## 1. Formato

Un **JWT** lleva datos (claims) y una **firma** que prueba que nadie los tocó. Son **3 partes en Base64url separadas por puntos**:

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
- **Selección de clave (opcional):** `kid`, `jwk`, `jku` (sección 3).

### Payload
JSON con los **claims** (los datos). **Base64url, NO cifrado → cualquiera lo lee.** La firma protege que no se **modifiquen**, no que no se **vean**.
```json
{ "sub": "wiener", "iss": "portswigger", "exp": 1786914938 }
```
- `sub` (usuario), `iss` (emisor), `exp` (expiración), `iat`… + custom (`role`, `isAdmin`).

### Signature
Garantiza **integridad**. Se calcula sobre `Base64url(Header) + "." + Base64url(Payload)`:
- **Simétrica — `Hash(Header, Payload)` con secreto** (HMAC): `HMAC-SHA256(data, secreto)`.
- **Asimétrica — `Encrypt(Hash(Header, Payload))`** (RSA/ECDSA): se hashea y el hash se **firma con la clave privada**; se **verifica con la pública**.

## 2. Algoritmos: simétrico vs asimétrico

> Concepto general (clave única vs par pública/privada) → [[how-to-work/symmetric-vs-asymmetric|cifrado simétrico vs asimétrico]].

Aplicado al `alg` del JWT:
- **`HS256` (HMAC + SHA-256) → simétrico:** una sola clave (secreto) **firma y verifica**.
- **`RS256` (RSA + SHA-256) → asimétrico:** la **privada** firma, la **pública** verifica.

**Ejemplo (mismos claims, distinta firma):**
```
data = base64url(Header) + "." + base64url(Payload)

HS256:  signature = HMAC_SHA256(data, secreto)          → verificar = recalcular con el MISMO secreto y comparar
RS256:  signature = RSA_sign(SHA256(data), privateKey)  → verificar = RSA_verify(data, signature, publicKey)
```

## 3. `kid`, `jwk`, `jku` (cómo el server elige la clave)

Son campos del **header** que le dicen al verificador **qué clave usar**.

- **`kid` (Key ID):** un **identificador** que apunta a la clave (índice en un JWKS, o a veces un **path/registro**).
  ```json
  { "kid": "ed2Nf8sb-sD6ng0-scs5390g-fFD8sfxG", "typ": "JWT", "alg": "RS256" }
  ```
- **`jwk` (JSON Web Key):** la clave pública **embebida dentro del propio token**.
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
- **`jku` (JWK Set URL):** una **URL** que apunta a un **JWK Set** (un `{ "keys": [...] }` con varias claves públicas).
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

## 4. JWT vs JWS vs JWE

- **JWT (JSON Web Token):** el estándar del **token con claims**. Es el "qué". En la práctica, un JWT casi siempre está implementado como un **JWS**.
- **JWS (JSON Web Signature):** contenido **firmado** → da **integridad/autenticidad**. El payload es **legible** (Base64url, no cifrado). **3 partes.** Es lo que ves normalmente.
- **JWE (JSON Web Encryption):** contenido **cifrado** → da **confidencialidad**. El payload **no se puede leer**. **5 partes.**

| | **JWS** (lo normal) | **JWE** |
| --- | --- | --- |
| Qué aporta | Firma (integridad) | Cifrado (confidencialidad) |
| ¿Se lee el payload? | **Sí** (Base64url) | **No** |
| Nº de partes | **3** (`h.p.s`) | **5** |

> **Regla práctica:** casi todos los JWT que vas a atacar son **JWS**.

---

> [!note] Seguir
> - Explotarlo (ataques por Header/Payload/Signature, ejemplos) → [[vulnerabilities/018-jwt-attacks/jwt-attacks|entry point de JWT]].
> - Los 8 labs con solución paso a paso → [[vulnerabilities/018-jwt-attacks/labs/README|labs de JWT]].
