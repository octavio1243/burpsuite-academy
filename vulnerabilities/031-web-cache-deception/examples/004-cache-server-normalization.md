---
aliases:
  - WCD 004 - cache server normalization
  - cache deception cache normalization
tags:
  - vuln/web-cache-deception
  - example
  - portswigger
---

# 004 — Normalización en la CACHÉ

> Lab: [Exploiting cache server normalization](https://portswigger.net/web-security/web-cache-deception/lab-wcd-exploiting-cache-server-normalization) · **Practitioner** · técnica → [[vulnerabilities/031-web-cache-deception/web-cache-deception|entry point]]

## Qué muestra
El caso **inverso** al [[vulnerabilities/031-web-cache-deception/examples/003-origin-server-normalization|003]]: acá **la caché normaliza** el path (decodifica `%2f`, resuelve `..`) y el **origen no**. Armás una URL que el **origen** deja crudo y enruta al **endpoint dinámico** `/my-account`, mientras que la **caché**, al normalizar, la ve como un **archivo estático** (`.../static/wcd.js`) y la **cachea**.

## Request → Response

> `GET `==`/my-account%2f%2e%2e%2fstatic/wcd.js`==` HTTP/1.1`
> `Host: victim.web-security-academy.net`
> `Cookie: session=<sesión de la víctima>`

**⬇️ el origen NO normaliza → trata todo como parte de `/my-account` (dinámico); la caché SÍ normaliza → `/static/wcd.js` (estático) y lo guarda:**

> `HTTP/1.1 200 OK` · `Cache-Control: max-age=30` · ==`X-Cache: miss`==
> `...Your API Key is: `==`<API KEY DE LA VÍCTIMA>`==`...`

## Por qué funciona
- **Origen (no normaliza):** ve `/my-account%2f%2e%2e%2fstatic/wcd.js` como un path raro que empieza en `/my-account` → sirve la cuenta **dinámica** con datos (o ignora la cola).
- **Caché (normaliza):** decodifica `%2f`→`/` y `%2e%2e`→`..`, colapsa → `/my-account/../static/wcd.js` = `/static/wcd.js` → matchea su regla de estático y **cachea**.
- La discrepancia es la **misma normalización, pero al revés**: acá la resuelve la caché, no el origen.

## Cómo distinguirlo del 003 (recon)
- **Averiguá quién normaliza.** Mandá una URL con `..%2f` y mirá **a qué endpoint respondió el origen**:
  - Si el **origen** resolvió el `..` (te dio otra ruta) → normaliza el origen → patrón [[vulnerabilities/031-web-cache-deception/examples/003-origin-server-normalization|003]].
  - Si el **origen** NO lo resolvió (respondió como `/my-account`) pero igual quedó **cacheado como estático** → normaliza la **caché** → este patrón.
- Truco: comparás el comportamiento con y sin encoding y ves quién "colapsa" el dot-segment.

## Cómo explotarlo (weaponize)
1. Entregá el link a la víctima:
   ```
   <script>document.location="https://victim.web-security-academy.net/my-account%2f%2e%2e%2fstatic/wcd.js"</script>
   ```
2. La víctima autenticada lo abre → la caché normaliza y guarda **su** respuesta bajo la key estática.
3. Pedís vos la misma URL → `X-Cache: hit` → **leés la API key de la víctima**.

## Verificación
- La URL, sin sesión, vuelve con ==`X-Cache: hit`== y los datos de la víctima.

## Detalles que se pasan por alto
- **Origen vs caché es lo único que cambia** frente al 003 — el arsenal (`%2f`, `%2e%2e`) es el mismo; lo que decide el lab es **quién** resuelve los dot-segments.
- **Necesitás terminar en algo que la caché cachee** (`/static/wcd.js`, o una extensión) *después* de normalizar.
- Si la caché cachea por **nombre exacto** en vez de por directorio/extensión, el objetivo cambia → [[vulnerabilities/031-web-cache-deception/examples/005-exact-match-cache-rules|005]].

→ Siguiente: [[vulnerabilities/031-web-cache-deception/examples/005-exact-match-cache-rules|005 · Reglas de nombre exacto]]
