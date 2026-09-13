---
aliases:
  - WCD 001 - path mapping
  - cache deception path mapping
tags:
  - vuln/web-cache-deception
  - example
  - portswigger
---

# 001 — Path mapping: `.js` colgado de `/my-account`

> Lab: [Exploiting path mapping](https://portswigger.net/web-security/web-cache-deception/lab-wcd-exploiting-path-mapping) · **Apprentice** · técnica → [[vulnerabilities/031-web-cache-deception/web-cache-deception|entry point]]

## Qué muestra
El **origen** usa **path mapping REST-style**: enruta por el **primer segmento** (`/my-account`) e **ignora** lo que viene después. La **caché**, en cambio, mira el **final** del path y ve `.js` → aplica su regla "cachear estáticos". Así `/my-account/wcd.js` devuelve la página **dinámica de la cuenta** pero queda **cacheada**. El atacante la pide después y **lee la API key** de la víctima.

## Request → Response

Estando **logueado como la víctima** (lo que hace el link entregado):

> `GET `==`/my-account/wcd.js`==` HTTP/1.1`
> `Host: victim.web-security-academy.net`
> `Cookie: session=<sesión de la víctima>`

**⬇️ el origen ignora `/wcd.js` y sirve `/my-account`; la caché lo guarda por la extensión `.js`:**

> `HTTP/1.1 200 OK` · `Cache-Control: max-age=30` · ==`X-Cache: miss`==
> `...Your API Key is: `==`<API KEY DE LA VÍCTIMA>`==`...`

**Después, el atacante pide la MISMA URL (sin sesión) y la lee de la caché:**

> `GET /my-account/wcd.js HTTP/1.1` → `HTTP/1.1 200 OK` · ==`X-Cache: hit`==

## Por qué funciona
- **Origen (path mapping):** `/my-account/wcd.js` matchea la ruta `/my-account`; el `/wcd.js` es un segmento sobrante que **no cambia el endpoint** → sirve la página de la cuenta **con datos privados**.
- **Caché (regla de extensión):** ve el path terminando en `.js` → "esto es un archivo estático, lo cacheo". No sabe que el origen lo trató como dinámico.
- **La discrepancia** entre "cómo enruta el origen" y "cómo decide cachear la caché" es todo el bug.

## Cómo explotarlo (weaponize)
1. Confirmá en Repeater que `GET /my-account/wcd.js` (con **tu** sesión) devuelve **tu** página de cuenta y que la respuesta trae headers de caché (`X-Cache`, `Cache-Control`).
2. Entregá el link a la víctima con el exploit server:
   ```
   <script>document.location="https://victim.web-security-academy.net/my-account/wcd.js"</script>
   ```
   La víctima autenticada lo abre → **su** respuesta queda cacheada bajo `/my-account/wcd.js`.
3. Pedí vos `GET /my-account/wcd.js` (sin sesión) → volvés a recibir la respuesta con `X-Cache: hit` y **leés la API key de la víctima**.

## Verificación
- La segunda vez que pedís la URL, la respuesta trae ==`X-Cache: hit`== y los **datos de la víctima**, no los tuyos → confirmaste que la caché guardó contenido privado.

## Detalles que se pasan por alto
- **La extensión tiene que estar en la lista de la caché** — probá `.js`, `.css`, `.jpg`; usá la que devuelva `X-Cache: hit` en un recurso real (ej. un `.js` legítimo del sitio).
- **El nombre del archivo es libre** (`wcd.js`, `x.js`) — lo que importa es la **extensión**, no el nombre.
- **Es el caso más simple:** acá no hace falta ni delimiter ni normalización, solo colgar un segmento. Si el origen **no** ignora el segmento extra (404), pasá a delimiters → [[vulnerabilities/031-web-cache-deception/examples/002-path-delimiters|002]].

→ Siguiente: [[vulnerabilities/031-web-cache-deception/examples/002-path-delimiters|002 · Delimitadores de path]]
