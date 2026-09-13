---
aliases:
  - GraphQL 001 - introspection para mapear el schema
  - graphql schema introspection
tags:
  - vuln/graphql
  - example
  - portswigger
---

# 001 — Introspection: mapear el schema y encontrar campos jugosos

> Lab: [Accidental exposure of private GraphQL fields](https://portswigger.net/web-security/graphql/lab-graphql-accidental-field-exposure) · **Apprentice** · técnica → [[vulnerabilities/021-graphql/graphql|entry point]]

## ¿Por qué acá? (el caso base)
- **Es el primer paso siempre:** GraphQL expone **un solo endpoint** y el schema es **consultable**. La introspection te da el mapa completo (tipos, queries, mutations, campos) → ahí aparecen los campos que la UI **no muestra** (`password`, `postPassword`, `isAdmin`).
- **Por qué funciona:** la autz suele estar por **endpoint**, no por campo → `getUser` devuelve `username` **y `password`** aunque la app nunca los pinte juntos.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (target / `id` a iterar).

**1) ¿Está habilitada la introspection?** (probe):
<pre class="payload"><code>{ "query": "{__schema{queryType{name}}}" }</code></pre>
Si la respuesta trae `__schema`, está activa. En Burp: mandá a **Repeater** (pestaña GraphQL) o mirala como árbol con **InQL**.

**2) Mapeá todo el schema** (query universal):
<pre class="payload"><code>query { __schema { types { name fields { name } } queryType { name } mutationType { name } } }</code></pre>
Ahí ves que `getUser(id)` expone el campo `password`. Pedilo, iterando el `id` hasta dar con el admin:
<pre class="payload"><code>query {
  getUser(id: <mark>1</mark>) {
    username
    password
  }
}</code></pre>

## Verificación
El server devuelve `username` **y** `password` del usuario. Con las credenciales del **admin** te logueás y **borrás a `carlos`** → lab resuelto.

## Detalles que se pasan por alto
- Si la introspection está filtrada, es casi siempre un **regex ingenuo** sobre `__schema{` → ver [[vulnerabilities/021-graphql/examples/003-bypass-introspection-endpoint-oculto|003]].
- Herramientas cuando la introspection está **off**: **Clairvoyance** (infiere el schema) o **Apollo Sandbox**.
- Los campos jugosos a buscar en el schema: `password`, `postPassword`, `isAdmin`, y mutations `delete*` / `changeEmail` / `promote*`.

→ Siguiente: [[vulnerabilities/021-graphql/examples/002-acceso-datos-ocultos-query|002 · pedir un objeto oculto por id (campo + IDOR)]]
