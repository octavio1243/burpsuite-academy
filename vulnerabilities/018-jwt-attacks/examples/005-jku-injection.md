---
aliases:
  - JWT 005 - jku injection
  - JWKS en exploit server
tags:
  - vuln/jwt
  - example
  - portswigger
---

# 005 — `jku` injection (JWKS en tu server, self-signed)

> Lab: [JWT authentication bypass via jku header injection](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-jku-header-injection) · Practitioner · Teoría → [[how-to-work/jwt#3. `kid`, `jwk`, `jku` (cómo el server elige la clave)|jku en how-to-work]] · [[vulnerabilities/018-jwt-attacks/jwt-attacks|entry point]]

## Qué muestra
El server descarga la clave de verificación desde la **URL del header `jku`** sin validar el dominio. Apuntás `jku` a **tu exploit server**, que sirve **tu** clave pública.

## Diagrama

```mermaid
sequenceDiagram
    autonumber
    participant At as Atacante
    participant ES as Exploit Server
    participant S as Server con JWT
    Note over At: New RSA Key, copio mi JWK público
    At->>ES: hospedo JWKS keys=[mi pública] en /jwks.json
    Note over At: header jku=ES/jwks.json, kid=el mío<br/>sub → administrator, Sign con mi privada
    At->>S: GET /admin con el JWT
    S->>ES: GET /jwks.json (trae la clave por jku)
    ES-->>S: mi JWK público
    Note over S: verifica con mi clave → válido
    S-->>At: 200 admin → borrar carlos
```

## Por qué funciona
- El server confía en que el `jku` apunte a un JWKS legítimo, pero **no valida el dominio** → lo mandás a tu server.
- El `kid` del token elige tu clave dentro del `keys[]` que servís.

## Cómo explotarlo (paso a paso)
1. **New RSA Key** en JWT Editor. Copiá su **JWK público**.
2. En el **exploit server** serví un JWK Set (Content-Type `application/json`):
   ```json
   { "keys": [ { PEGÁ_ACÁ_TU_JWK_PÚBLICO } ] }
   ```
3. En el header del JWT: `"jku":"https://TU-EXPLOIT-SERVER/exploit"`, `"kid":"EL-KID-DE-TU-CLAVE"`, payload `"sub":"administrator"`.
4. **Sign** con tu RSA (RS256) → enviá → `/admin` → borrar `carlos`.

## Verificación
- En el access log del exploit server ves el `GET` del server a tu `/jwks.json`, y el token valida.

## Detalles que se pasan por alto
- El `kid` del token y el `kid` de tu clave en el JWKS **deben coincidir**.
- Único lab de JWT que necesita **exploit server** (los demás son de un solo actor).
