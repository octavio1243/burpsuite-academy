---
aliases:
  - OAuth 001 - Auth bypass implicit flow
  - implicit email substitution
tags:
  - vuln/oauth
  - example
  - portswigger
---

# 001 — Auth bypass por implicit flow (sustitución de email)

> Lab: [Authentication bypass via OAuth implicit flow](https://portswigger.net/web-security/oauth/lab-oauth-authentication-bypass-via-oauth-implicit-flow) · Apprentice · Teoría → [[vulnerabilities/026-oauth/oauth#A.1 — Implementación incorrecta del implicit grant|entry point A.1]] · [[vulnerabilities/026-oauth/labs/README|labs]]

## Qué muestra
En el **implicit flow** el cliente recibe el token y después **su propio JS le POSTea al backend la identidad del usuario** (`email`) para armar la sesión. El backend **confía en ese `email` sin verificar que corresponda al token** → cambiás el email en el POST y **te logueás como cualquiera**. Ataque de **un solo actor** (no hace falta víctima ni exploit server).

## Diagrama

```mermaid
sequenceDiagram
    autonumber
    participant At as Atacante
    participant OA as OAuth service
    participant C as Cliente — target
    At->>OA: login social con MI cuenta (response_type=token)
    OA-->>At: 302 redirect_uri#access_token=... (MI token)
    At->>C: POST /authenticate {email: MI email, token: MI token}
    Note over At,C: intercepto en Burp y cambio<br/>email → carlos@carlos-montoya.net
    Note over C: confia en el email del body;<br/>NO valida que el token sea de carlos
    C-->>At: Set-Cookie: sesion de CARLOS
```

## Por qué funciona
- El token del implicit flow **no está atado** al `email` que el cliente manda a `/authenticate`: son dos datos independientes que el backend **no cruza**.
- El backend usa el `email` como **clave de identidad** y crea/recupera la sesión de ese usuario → controlás a quién "sos".
- El `token` puede quedar el tuyo; muchas implementaciones ni lo revalidan contra el email.

## Cómo explotarlo (paso a paso)
1. Logueate con **tu** cuenta social ("Log in with social media") una vez para completar el flujo.
2. En el Proxy history, ubicá el `POST /authenticate` (a veces `/authentication`) con `{email, username, token}`.
3. Reenvialo a **Repeater**, cambiá `email` por `carlos@carlos-montoya.net` y mandalo.
4. La respuesta trae la **cookie de sesión de carlos** → navegás como él.

## Verificación
- Cargá la home con esa cookie: aparecés logueado como `carlos`.

## Detalles que se pasan por alto
- Es **específico del implicit** (o de clientes que confían en identidad enviada por el front). En **code grant** bien hecho el backend saca la identidad del `/userinfo` con el token, y esto no aplica.
- La causa raíz es de **cliente**, no del OAuth service → el proveedor puede estar perfecto.
- Regla de oro: **nunca** confiar en `email`/`sub` que venga del navegador; pedilo al `/userinfo` **con el token**.
