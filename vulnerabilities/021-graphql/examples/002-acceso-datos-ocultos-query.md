---
aliases:
  - GraphQL 002 - acceso a datos ocultos vía query
  - graphql hidden field IDOR
tags:
  - vuln/graphql
  - example
  - portswigger
---

# 002 — Acceso a datos ocultos vía query (campo oculto + IDOR)

> Lab: [Accessing private GraphQL posts](https://portswigger.net/web-security/graphql/lab-graphql-reading-private-posts) · **Apprentice** · técnica → [[vulnerabilities/021-graphql/graphql|entry point]]

## ¿Por qué acá? (variante de 001)
- **Mismo defecto de autz por campo/objeto**, pero acá lo explotás como **IDOR**: los `id` de los posts son **secuenciales** y falta el **3** (post privado). El schema tiene un campo `postPassword` que la UI nunca pide.
- **Por qué funciona:** el resolver no valida quién pide el objeto → si conocés el `id` y el campo, te lo devuelve.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (el `id` del objeto oculto).

Por introspection ([[vulnerabilities/021-graphql/examples/001-introspection-mapear-schema|001]]) ves el campo `postPassword` en `BlogPost`. Pedí el post faltante **incluyendo el campo oculto**:
<pre class="payload"><code>query {
  getBlogPost(id: <mark>3</mark>) {
    title
    postPassword
  }
}</code></pre>

## Verificación
La respuesta trae el `postPassword` del post oculto (`id 3`). Enviá ese password en el formulario del lab → resuelto.

## Detalles que se pasan por alto
- El patrón es **pedir campos que la UI no muestra** + **cambiar el `id`** (IDOR). Emparenta con [[vulnerabilities/028-access-control/access-control|access control]].
- No hace falta bypass ni exploit server: la introspection está activa y el endpoint es el estándar.
- Si no ves el campo en el schema porque la introspection está bloqueada → primero [[vulnerabilities/021-graphql/examples/003-bypass-introspection-endpoint-oculto|003]].

→ Siguiente: [[vulnerabilities/021-graphql/examples/003-bypass-introspection-endpoint-oculto|003 · endpoint oculto + bypass de introspection + mutation]]
