---
aliases:
  - GraphQL wordlist
  - graphql endpoints wordlist
  - graphql-endpoint-discovery
  - wordlists de graphql
tags:
  - vuln/graphql
  - wordlist
  - reference
---

# GraphQL — Wordlist de descubrimiento de endpoint

> Documento **agnóstico al negocio**: rutas listas para **fuzzear dónde vive el endpoint GraphQL** cuando no es visible a simple vista.
> Punto de entrada (teoría, introspection, ataques): [[vulnerabilities/021-graphql/graphql|entry point]].

## 🎯 Para qué sirve

El endpoint muchas veces **no está a la vista**. GraphQL suele colgar de una ruta única y hay que adivinarla. Esta lista automatiza esa búsqueda: paths clásicos (`graphql`), variantes bajo `api/`, versionado (`v1`/`v2`/`v3`) y las **consolas embebidas** (`graphiql`, `playground`, `voyager`, `altair`) que, si responden, te confirman GraphQL y a veces traen introspection abierta.

> [!tip] 🔁 Probá GET **y** POST
> El mismo path puede estar mudo en GET y responder en POST (o al revés). Fuzzeá los dos métodos.
> - Sonda universal para confirmar que es GraphQL: `{"query":"{__typename}"}`. Si devuelve `{"data":{"__typename":"Query"}}` (o `"query"`), acertaste.
> - Si el endpoint rechaza el método, probá el otro antes de descartarlo.

## 🧮 Convención

> [!note] Sin `/` inicial
> Las entradas van **sin barra inicial** para concatenar como `BASE/FUZZ` (ffuf, Burp Intruder sniper sobre la ruta). Si tu herramienta necesita la barra, prependeá `/`.

| Cómo se usa | Detalle |
| --- | --- |
| Base | `https://TARGET/` |
| Fuzz | cada línea del `.txt` se pega al final de la base |
| Resultado | `https://TARGET/api/graphql`, `https://TARGET/v1/graphql`, … |

## 📄 Las listas

| Archivo | Qué prueba |
| --- | --- |
| [`graphql-endpoints.txt`](graphql-endpoints.txt) | Paths de endpoint GraphQL: raíz (`graphql`), bajo `api/`, versionado `v1`–`v3`, consolas (`graphiql`/`playground`/`voyager`/`altair`), subscriptions y variantes ocultas (`__graphql`, `admin/graphql`). |

## ⚙️ Uso

**ffuf (GET):**
```bash
ffuf -u https://TARGET/FUZZ -w graphql-endpoints.txt -mc 200,400,405,500
```

**ffuf (POST con sonda de introspection ligera):**
```bash
ffuf -u https://TARGET/FUZZ -w graphql-endpoints.txt \
  -X POST -H "Content-Type: application/json" \
  -d '{"query":"{__typename}"}' -mc 200,400,500
```

**Burp Intruder:** marcá la posición en la ruta (`GET /§graphql§ HTTP/1.1`), cargá el `.txt` como payload set, y repetí con método POST.

> [!warning] ⚠️ No filtres solo por 200
> Un endpoint GraphQL suele responder **400/405/500** ante una request malformada o un método equivocado, y eso **igual confirma** que existe. Incluí esos códigos (`-mc 200,400,405,500`) y mirá el **cuerpo**: si menciona `query`, `errors`, `mustProvideQuery`, `GraphQL`, encontraste el endpoint aunque el status no sea 200.

## 🔎 Señales de acierto

- Cuerpo con `{"data":…}` o `{"errors":[{"message":"…"}]}`.
- Mensajes tipo `Must provide query string` / `GET query missing` / `Cannot query field`.
- Una **consola** (`graphiql`/`playground`/`voyager`) que carga HTML interactivo → confirmá y probá introspection (ver [[vulnerabilities/021-graphql/examples/001-introspection-mapear-schema|001 · introspection]]).
- Si introspection está apagada, saltá a [[vulnerabilities/021-graphql/examples/003-bypass-introspection-endpoint-oculto|003 · bypass introspection]].
