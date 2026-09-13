---
aliases:
  - JWT 002 - alg none
  - flawed signature verification
tags:
  - vuln/jwt
  - example
  - portswigger
---

# 002 — `alg: none` (token sin firma)

> Lab: [JWT authentication bypass via flawed signature verification](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-flawed-signature-verification) · Apprentice · Teoría → [[how-to-work/jwt|cómo funciona un JWT]] · [[vulnerabilities/018-jwt-attacks/jwt-attacks|entry point]]

## Qué muestra
El server **acepta tokens "sin firmar"** cuando `alg` es `none`. Ponés `alg:none`, editás el claim y **borrás la firma** (dejando el punto final).

## JWT (original → modificado)

Las 3 partes decodificadas. <mark style="background:#a5d6a7;color:#111">🎯 objetivo</mark> = lo que querés · <mark style="background:#ffcc80;color:#111">⚙️ consecuencia</mark> = lo que cambia para que valide.

| Parte | Original | Modificado |
| --- | --- | --- |
| **header** | { "alg": "HS256", "typ": "JWT" } | { "alg": <mark style="background:#ffcc80;color:#111">"none"</mark>, "typ": "JWT" } |
| **payload** | { "sub": "wiener" } | { "sub": <mark style="background:#a5d6a7;color:#111">"administrator"</mark> } |
| **signature** | HMAC-SHA256 (secreto del server) | <mark style="background:#ffcc80;color:#111">eliminada</mark> → token `header.payload.` |

> **🎯 Objetivo:** `sub → administrator`. **⚙️ Consecuencia:** `alg → none` y **firma eliminada** (`header.payload.`) para que el claim forjado sea aceptado.

## Diagrama

```mermaid
sequenceDiagram
    autonumber
    participant At as Atacante
    participant S as Server con JWT
    At->>S: login wiener:peter
    S-->>At: JWT con sub=wiener, alg=HS256
    Note over At: sub → administrator<br/>alg → none<br/>borro la firma, dejo header.payload.
    At->>S: GET /admin con header.payload. (sin firma)
    Note over S: alg=none → acepta sin verificar firma
    S-->>At: 200 admin → borrar carlos
```

## Por qué funciona
- `alg:none` le dice al server "este token no tiene firma"; una implementación insegura **lo cree** y salta la verificación.
- El punto final (`header.payload.`) es obligatorio: el JWT sigue teniendo 3 partes, la 3ª vacía.

## Cómo explotarlo (paso a paso)
1. En Repeater, payload: `"sub":"administrator"`.
2. Header: `"alg":"none"`.
3. **Borrá la firma** dejando el punto final → `BASE64(header).BASE64(payload).`
   > En JWT Editor podés usar el botón de ataque **"none"** que lo hace solo.
4. Enviá → `/admin` → borrar `carlos`.

## Verificación
- El token sin firma con `sub:administrator` te deja entrar a `/admin`.

## Detalles que se pasan por alto
- Probá variantes de capitalización (`None`, `NONE`) si `none` es filtrado por una blacklist ingenua.
- Distinto del 001: acá el server **sí** intentaría verificar, pero `none` lo desactiva.
