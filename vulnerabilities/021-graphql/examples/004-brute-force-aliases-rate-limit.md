---
aliases:
  - GraphQL 004 - brute force sin rate limit vía aliases
  - graphql alias batching brute force
tags:
  - vuln/graphql
  - example
  - portswigger
---

# 004 — Brute force sin rate limit batcheando con alias

> Lab: [Bypassing GraphQL brute force protections](https://portswigger.net/web-security/graphql/lab-graphql-brute-force-protection-bypass) · **Practitioner** · técnica → [[vulnerabilities/021-graphql/graphql|entry point]]

## ¿Por qué acá? (romper el rate-limit)
- **El límite cuenta requests, no operaciones.** GraphQL permite **aliasear** la misma operación N veces en **un solo** request → mandás cientos de `login` en una request y el rate-limit no se entera.
- **Por qué funciona:** cada alias es una ejecución independiente del mismo campo; el server las resuelve todas y devuelve el resultado de cada una.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (usuario objetivo y los passwords de la wordlist).

Armá **una** mutation con un `login` aliaseado por cada password:
<pre class="payload"><code>mutation {
  b0: login(input: {username: "<mark>carlos</mark>", password: "<mark>123456</mark>"}) { token success }
  b1: login(input: {username: "<mark>carlos</mark>", password: "<mark>password</mark>"}) { token success }
  b2: login(input: {username: "<mark>carlos</mark>", password: "<mark>qwerty</mark>"}) { token success }
  # ... un alias por cada password de la wordlist
}</code></pre>
> Automatizado (genera los alias desde la wordlist) → `vulnerabilities/021-graphql/scripts/brute-force-graphql.py`.

## Verificación
Una sola request; en la respuesta buscás el alias que devolvió `success: true` → ese es el password de `carlos`. Logueás como él → lab resuelto.

## Detalles que se pasan por alto
- **Alias = batching:** el mismo truco saltea cualquier límite "por request" (login, **OTP**, rate-limit). Emparenta con `vulnerabilities/011-brute-force/` y [[exam/to-do-list/authentication|authentication]].
- Mirá la respuesta con el buscador de Burp filtrando `success: true` — es un JSON grande con un objeto por alias.
- Otro sabor de ataque GraphQL: **CSRF over GraphQL** (mutation `changeEmail` vía form cross-site) → PoC en [[vulnerabilities/021-graphql/graphql|entry point]] · [lab](https://portswigger.net/web-security/graphql/lab-graphql-csrf-via-graphql-api).
