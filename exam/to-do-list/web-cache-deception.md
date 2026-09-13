---
aliases:
  - to-do WCD
  - web cache deception to-do
tags:
  - exam/to-do
  - vuln/web-cache-deception
---

# Web Cache Deception — Qué probar en el examen

> **Fuente única** para los stages (evita duplicar). Cada STAGE linkea acá.
> Técnica completa → [[vulnerabilities/031-web-cache-deception/web-cache-deception|entry point]] · labs → [[vulnerabilities/031-web-cache-deception/labs/README|labs]] · ejemplos → carpeta `examples/`.

> [!danger] WCD ≠ WCP
> **Deception LEE** el contenido privado de la víctima (la caché lo guarda por error → lo pido yo). **Poisoning ESCRIBE** mi payload en la respuesta de otros. Si el objetivo es **robarle un dato a la víctima/admin** (API key, CSRF token, sesión) pensá **deception**. → [[exam/to-do-list/web-cache-poisoning|to-do WCP]]

## 🚩 Flags

> [!danger] 🚩 ¿Hay caché? — headers/tiempo en la respuesta
> `X-Cache: hit/miss` · `X-Cache-Hits` · `Cache-Status` · `Age` · `Cache-Control` (`public`, `max-age`) · `Expires`. Un **`hit`** responde **mucho más rápido** que un `miss` → si no ves el header, medí el **tiempo**.
> **Recon de reglas:** pedí `/x.js`, `/x.css`, `/static/x`, `/robots.txt`, `/favicon.ico` → los que vuelven `hit` te dicen **qué cachea** (extensión / directorio / nombre exacto).

> [!tip] 💡 Gadgets que gritan WCD
> **Endpoint con datos privados** (`/my-account`, `/account`, `/settings`, `/api/...`) que refleja **API key / CSRF token / email** estando logueado · **hay una caché/CDN adelante** · **el origen enruta REST-style** (ignora segmentos o normaliza dot-segments).

## 🎯 En qué stage aparece

> **Deception necesita una víctima que navegue** (le entregás el link y su respuesta queda cacheada). Por eso encaja como **entrega client-side** → normalmente **Stage 2** (escalar a admin), no en el arranque no autenticado. Ver [[bscp-exam-structure]].

| Aspecto            | 🔴 Stage 2 (típico)                                              |
| ------------------ | --------------------------------------------------------------- |
| **Objetivo**       | **robar el secreto/dato del admin** (o de una víctima)          |
| **A quién le pega** | la **víctima/admin** que abre el link que le entrego            |
| **Flag extra**     | hay caché **+ una víctima que navega** el link                  |
| **Qué hago**       | crafteo la URL dinámica-que-la-caché-cree-estática → se la mando → su respuesta privada queda cacheada → **la leo yo** |
| **Dato robado**    | **API key** / **CSRF token** / datos de cuenta / a veces sesión |

## ♾️ Independiente del stage (el "cómo")

### 1) Encontrar el endpoint con datos privados
Logueado, buscá una respuesta que refleje algo sensible: `/my-account` con **API key**, un **CSRF token** en un form, email, etc. Ese es el que vas a hacer cachear.

### 2) Detección / cache oracle
Ver el bloque de Flags: `X-Cache`, `Age`, `Cache-Control` y **tiempo**. Confirmá `miss`→`hit`. Descubrí **qué reglas** tiene la caché (extensión / directorio / nombre exacto) pidiendo recursos de prueba.

### 3) Encontrar la discrepancia (el vector)
| Discrepancia | Cómo se ve | Payload | Ejemplo |
| --- | --- | --- | --- |
| **Path mapping** | el origen ignora el segmento extra | `/my-account/wcd.js` | [[vulnerabilities/031-web-cache-deception/examples/001-path-mapping\|001]] |
| **Delimitadores** | el origen corta en `;` `%23` `%3f` `%00` `%0a`, la caché no | `/my-account%23wcd.js` | [[vulnerabilities/031-web-cache-deception/examples/002-path-delimiters\|002]] |
| **Normaliza el origen** | el origen resuelve `..%2f` y vuelve al dinámico | `/static/..%2fmy-account` | [[vulnerabilities/031-web-cache-deception/examples/003-origin-server-normalization\|003]] |
| **Normaliza la caché** | la caché resuelve `%2f%2e%2e%2f` a estático, el origen no | `/my-account%2f%2e%2e%2fstatic/wcd.js` | [[vulnerabilities/031-web-cache-deception/examples/004-cache-server-normalization\|004]] |
| **Nombre exacto** | la caché cachea `robots.txt`/`favicon.ico` puntual | `/my-account%23%2f%2e%2e%2frobots.txt` | [[vulnerabilities/031-web-cache-deception/examples/005-exact-match-cache-rules\|005]] |

### 4) Fuzzing de delimitadores / normalización (desde Repeater)
El browser **URL-encodea** `;`, `#`, `?`, espacios → probá desde **Repeater** con los bytes crudos y encodeados:
```
; %3b   #(%23)   ?(%3f)   %00   %0a %0d   ..   %2f   %2e%2e%2f   \   ]
```
Buscá la variante que devuelve **la página con datos (200)** en vez de 404, **y** que quede cacheada (`X-Cache`).

### 5) Cache buster (probar sin ensuciar)
Mientras testeás, agregá una query única (`?cb=<random>`) para **no** cachear la URL real. Al entregar a la víctima usás la URL **limpia** que después vas a pedir vos.

### 6) Explotar (entrega + lectura)
1. Hosteo en el **exploit server** el redirect a la URL crafteada:
   ```
   <script>document.location="https://TARGET/my-account%23wcd.js"</script>
   ```
2. **Deliver to victim** → la víctima autenticada la abre → **su** respuesta privada queda cacheada.
3. **Pido yo** la misma URL (sin sesión) → `X-Cache: hit` → **leo su API key / CSRF token / datos**.
4. Uso el dato robado para el objetivo del stage (entrar a la cuenta / actuar como admin).

### 7) Referencias
- 📁 Entry point → [[vulnerabilities/031-web-cache-deception/web-cache-deception|web-cache-deception]]
- 🧪 Labs → [[vulnerabilities/031-web-cache-deception/labs/README|labs/README]]
- 📎 Ejemplos → `001`–`005` (path mapping · delimiters · origin norm · cache norm · exact-match)
- 🔗 Contraste con envenenamiento → [[exam/to-do-list/web-cache-poisoning|to-do WCP]] · [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|entry point WCP]]
