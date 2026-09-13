---
aliases:
  - JWT 003 - Weak signing key
  - brute force HMAC hashcat
tags:
  - vuln/jwt
  - example
  - portswigger
---

# 003 — Weak signing key (brute force del secreto HMAC)

> Lab: [JWT authentication bypass via weak signing key](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-weak-signing-key) · Practitioner · Teoría → [[how-to-work/symmetric-vs-asymmetric|simétrico vs asimétrico]] · [[vulnerabilities/018-jwt-attacks/jwt-attacks|entry point]]

## Qué muestra
El JWT usa **HS256 (simétrico)** con un **secreto débil**. Lo **crackeás** con hashcat y, como en simétrico *firmar = verificar*, firmás vos tokens válidos.

## Diagrama

```mermaid
sequenceDiagram
    autonumber
    participant At as Atacante
    participant HC as hashcat local
    participant S as Server con JWT
    At->>S: login wiener:peter
    S-->>At: JWT HS256 firmado con secreto débil
    At->>HC: hashcat -m 16500 JWT + wordlist
    HC-->>At: secreto = secret1
    Note over At: JWT Editor: Symmetric Key k=base64(secret1)<br/>sub → administrator, Sign
    At->>S: GET /admin con el JWT re-firmado
    Note over S: verifica HMAC con "secret1" → válido
    S-->>At: 200 admin → borrar carlos
```

## Por qué funciona
- En **HS256** el mismo secreto firma y verifica. Si es adivinable, el atacante **también puede firmar**.
- El crackeo es offline: no tocás el server hasta tener el secreto.

## Cómo explotarlo (paso a paso)
1. Crackeá el secreto:
   ```
   hashcat -a 0 -m 16500 <JWT> jwt.secrets.list        # → secret1
   ```
   > O el script del repo: pegá el JWT en `scripts/crack_jwt.py` y `python crack_jwt.py`.
2. **JWT Editor Keys → New Symmetric Key** → reemplazá `k` por el **Base64url de `secret1`**.
3. En Repeater: `"sub":"administrator"` → **Sign** con esa clave (HS256).
4. Enviá → `/admin` → borrar `carlos`.

## Verificación
- El token re-firmado con el secreto crackeado valida y entrás a `/admin`.

## Detalles que se pasan por alto
- `-m 16500` es el modo JWT de hashcat. El `k` de la Symmetric Key es **Base64url**.
- Solo aplica a algoritmos **simétricos** (HS*). Para RS* la salida es algorithm confusion (007/008).
