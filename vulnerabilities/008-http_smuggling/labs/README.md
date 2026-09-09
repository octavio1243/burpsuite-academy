---
aliases:
  - HTTP Request Smuggling labs
  - smuggling-labs
tags:
  - vuln/http-smuggling
  - labs
  - portswigger
---

# HTTP Request Smuggling — Labs de PortSwigger

Labs de la categoría **[HTTP request smuggling](https://portswigger.net/web-security/request-smuggling)**: **15 Practitioner + 7 Expert** (22 en total; **no hay Apprentice** — el tema arranca en Practitioner). **El hilo común:** entre vos y la app hay **dos servidores en cadena** (front-end/proxy → back-end). Si **discrepan en dónde termina una petición**, podés meter (*colar*) el **inicio de una segunda petición** dentro de la primera. El front-end reenvía todo junto; el back-end la parte mal y trata tus bytes colados como la **request del próximo usuario** → saltás controles del front, robás requests/cookies ajenas, o inyectás XSS/redirects a otros.

> [!abstract] La discrepancia siempre es sobre la **longitud del cuerpo**
> Dos formas de decir "cuánto mide el body": **`Content-Length` (CL)** — cuenta bytes — y **`Transfer-Encoding: chunked` (TE)** — cierra con un chunk `0`. Cuando un server hace caso a uno y el otro al otro, aparece el desync. El **nombre del ataque dice quién usa qué**: `CL.TE` = *front usa CL, back usa TE*; `TE.CL` = al revés; `TE.TE` = ambos aceptan TE pero uno se lo ofusca; `CL.0`/`0.CL` = uno trata el CL como 0.

> [!note] Cómo leer las columnas
> **Técnica · cómo llegás** = la variante de desync + el truco/herramienta que necesitás (Collaborator, Intruder, exploit server, request cruda por socket). **Qué se logra** = el objetivo textual del lab. Esqueletos de payload por familia → [abajo](#esqueletos-por-familia). Scripts → [[vulnerabilities/008-http_smuggling/labs/README#🛠️-scripts-de-la-carpeta|scripts]].
> **Detección + explotación paso a paso** → [[vulnerabilities/008-http_smuggling/http-smuggling|entry point]] · ejemplos: [[vulnerabilities/008-http_smuggling/examples/001-cl-te|001 · CL.TE]] · [[vulnerabilities/008-http_smuggling/examples/002-te-cl|002 · TE.CL]].

---

## 1) Fundamentos — CL.TE / TE.CL / TE.TE (HTTP/1.1)

Probar que el desync existe. El objetivo de los tres es el mismo: que la **siguiente** request que procese el back-end aparezca con el método inválido **`GPOST`**.

| # | Laboratorio | Nivel | Técnica · cómo llegás | Qué se logra (objetivo) |
| --- | --- | --- | --- | --- |
| 1 | [Basic CL.TE](https://portswigger.net/web-security/request-smuggling/lab-basic-cl-te) | Practitioner | Front **CL** / back **TE**. Cuerpo ambiguo: chunk de cierre `0\r\n\r\n` + request colada; el CL exterior cubre todo. | Colar una request para que la **próxima** que procese el back-end use el método **`GPOST`** (prueba de desync). |
| 2 | [Basic TE.CL](https://portswigger.net/web-security/request-smuggling/lab-basic-te-cl) | Practitioner | Front **TE** / back **CL**. El chunk se corta en `0`, el back (CL) espera más bytes y se come el inicio de la colada. | Mismo **`GPOST`**, desync en sentido inverso. |
| 3 | [Obfuscating the TE header](https://portswigger.net/web-security/request-smuggling/lab-obfuscating-te-header) | Practitioner | **TE.TE**: ambos soportan TE, así que **ofuscás** el header (`Transfer-encoding: cow`, espacios, doble header) para que **uno lo ignore**. | Mismo **`GPOST`**, pero hay que ofuscar el `Transfer-Encoding` para romper el empate. |

## 2) Confirmar sin colgar el server — differential responses

En vez de detectar por **timeout** (que puede afectar a otros usuarios), colás una request a una **URL inexistente** y observás que la **respuesta siguiente cambia** (404). Método más limpio y confiable.

| # | Laboratorio | Nivel | Técnica · cómo llegás | Qué se logra (objetivo) |
| --- | --- | --- | --- | --- |
| 4 | [Confirming CL.TE via differential responses](https://portswigger.net/web-security/request-smuggling/finding/lab-confirming-cl-te-via-differential-responses) | Practitioner | Colás por CL.TE una request a una ruta que no existe → la **request normal siguiente** recibe una respuesta distinta (error/404). | **Confirmar** el CL.TE por respuesta diferencial, sin depender del timing. |
| 5 | [Confirming TE.CL via differential responses](https://portswigger.net/web-security/request-smuggling/finding/lab-confirming-te-cl-via-differential-responses) | Practitioner | Igual, variante TE.CL (ojo con los tamaños de chunk). | **Confirmar** el TE.CL por respuesta diferencial. |

## 3) Explotación clásica (HTTP/1.1)

Del desync ya confirmado a impacto real: saltar el front, robar requests/cookies, XSS y caché.

| # | Laboratorio | Nivel | Técnica · cómo llegás | Qué se logra (objetivo) |
| --- | --- | --- | --- | --- |
| 6 | [Bypass front-end controls, CL.TE](https://portswigger.net/web-security/request-smuggling/exploiting/lab-bypass-front-end-controls-cl-te) | Practitioner | El front **bloquea `/admin`**; colás por CL.TE una request a `/admin` que el front **nunca inspecciona**. | Entrar al **panel admin** `/admin` y **borrar a `carlos`**. |
| 7 | [Bypass front-end controls, TE.CL](https://portswigger.net/web-security/request-smuggling/exploiting/lab-bypass-front-end-controls-te-cl) | Practitioner | Igual, variante TE.CL. | `/admin` → **borrar `carlos`**. |
| 8 | [Reveal front-end request rewriting](https://portswigger.net/web-security/request-smuggling/exploiting/lab-reveal-front-end-request-rewriting) | Practitioner | `/admin` exige un header interno (ej. IP) que **agrega el front**. Colás una request que **refleja** ese header (campo de búsqueda) para **leerlo**, luego lo incluís. | Leer el **header que inyecta el front**; después colar una request **con** ese header → `/admin` → **borrar `carlos`**. |
| 9 | [Capture other users' requests](https://portswigger.net/web-security/request-smuggling/exploiting/lab-capture-other-users-requests) | Practitioner | Colás una request que **guarda** un comentario con un `Content-Length` grande → la request del **próximo usuario** queda almacenada dentro del comentario. | Capturar la request del siguiente usuario → **robar su cookie** → entrar a su cuenta. |
| 10 | [Deliver reflected XSS](https://portswigger.net/web-security/request-smuggling/exploiting/lab-deliver-reflected-xss) | Practitioner | XSS reflejado en el **`User-Agent`**; lo colás para que la respuesta que reciba la **víctima** traiga tu payload. | Colar `User-Agent: "/><script>alert(1)</script>` para que la **próxima víctima** ejecute `alert(1)`. |
| 11 | [Web cache poisoning](https://portswigger.net/web-security/request-smuggling/exploiting/lab-perform-web-cache-poisoning) | Expert | CL.TE + **on-site redirect**: colás para que la respuesta de un `.js` quede **envenenada en la caché**. | Envenenar la caché para que un pedido de un **archivo JS** reciba un **redirect al exploit server**. |
| 12 | [Web cache deception](https://portswigger.net/web-security/request-smuggling/exploiting/lab-perform-web-cache-deception) | Expert | CL.TE: colás para que la respuesta con datos sensibles del siguiente usuario quede **cacheada** en una ruta estática que vos podés pedir. | Hacer que la **API key** del siguiente usuario se **guarde en la caché** → leerla. |

## 4) HTTP/2 — downgrade & CRLF injection

El front habla HTTP/2 con el cliente pero **lo degrada a HTTP/1.1** contra el back. Ese downgrade reintroduce la ambigüedad de longitud, y como H2 es binario, un `\r\n` metido en un valor/nombre de header sobrevive al pasaje a texto.

| #   | Laboratorio                                                                                                                                                                                                   | Nivel        | Técnica · cómo llegás                                                                                                                       | Qué se logra (objetivo)                                                                                          |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| 13  | [H2.CL request smuggling](https://portswigger.net/web-security/request-smuggling/advanced/lab-request-smuggling-h2-cl-request-smuggling)                                                                      | Practitioner | En H2 mandás un **`Content-Length` falso**; al degradar, el front se desincroniza y colás un prefijo que redirige el tráfico siguiente.     | Hacer que el **browser de la víctima** cargue y ejecute un **JS del exploit server** → `alert(document.cookie)`. |
| 14  | [Response queue poisoning via H2.TE](https://portswigger.net/web-security/request-smuggling/advanced/response-queue-poisoning/lab-request-smuggling-h2-response-queue-poisoning-via-te-request-smuggling)     | Practitioner | H2.TE: metés `chunked` y colás una **request completa** → desincronizás la **cola de respuestas** y quedás recibiendo respuestas ajenas.    | Capturar la **cookie del admin** al loguearse → `/admin` → **borrar `carlos`** (response queue poisoning).       |
| 15  | [HTTP/2 smuggling via CRLF injection](https://portswigger.net/web-security/request-smuggling/advanced/lab-request-smuggling-h2-request-smuggling-via-crlf-injection)                                          | Practitioner | Inyectás `\r\n` en el **valor** de un header H2 para colar un `Transfer-Encoding: chunked` que el front no sanea al degradar.               | Vector **exclusivo de H2**: **entrar a la cuenta de otro usuario**.                                              |
| 16  | [HTTP/2 request splitting via CRLF injection](https://portswigger.net/web-security/request-smuggling/advanced/lab-request-smuggling-h2-request-splitting-via-crlf-injection)                                  | Practitioner | CRLF en H2 **parte una request en dos** completas → response queue poisoning.                                                               | **Borrar `carlos`** vía RQP entrando a `/admin`.                                                                 |
| 17  | [Bypass access controls via H2 request tunnelling](https://portswigger.net/web-security/request-smuggling/advanced/request-tunnelling/lab-request-smuggling-h2-bypass-access-controls-via-request-tunnelling) | Expert       | **Request tunnelling**: CRLF en **nombres** de header; el front no desincroniza del todo, pero tuneás una request oculta dentro de la tuya. | Acceder a `/admin` como **`administrator`** → **borrar `carlos`**.                                               |
| 18  | [Web cache poisoning via H2 request tunnelling](https://portswigger.net/web-security/request-smuggling/advanced/request-tunnelling/lab-request-smuggling-h2-web-cache-poisoning-via-request-tunnelling)       | Expert       | Tunnelling por el **pseudo-header `:path`** + cache poisoning.                                                                              | Envenenar la home para que la **víctima** ejecute `alert(1)`.                                                    |

## 5) Clases nuevas de desync (CL.0 / 0.CL / browser-powered)

Variantes modernas donde uno de los servers **trata el `Content-Length` como 0** (o el desync ocurre en el **propio browser** de la víctima).

| # | Laboratorio | Nivel | Técnica · cómo llegás | Qué se logra (objetivo) |
| --- | --- | --- | --- | --- |
| 19 | [CL.0 request smuggling](https://portswigger.net/web-security/request-smuggling/browser/cl-0/lab-cl-0-request-smuggling) | Practitioner | El **back-end ignora el `Content-Length`** en ciertos endpoints (lo trata como 0) → el cuerpo queda colado. Hay que **encontrar el endpoint** vulnerable. | Colar a `/admin` → **borrar `carlos`**. |
| 20 | [0.CL request smuggling](https://portswigger.net/web-security/request-smuggling/advanced/lab-request-smuggling-0cl-request-smuggling) | Expert | El **front** ve `Content-Length: 0` y el back sí lee el cuerpo (desync inverso). `carlos` visita la home cada 5s. | Colar un XSS → ejecutar **`alert()` en el browser de `carlos`**. |
| 21 | [Client-side desync](https://portswigger.net/web-security/request-smuggling/browser/client-side-desync/lab-client-side-desync) | Expert | **Browser-powered**: el server ignora el CL en un endpoint → el **propio browser de la víctima** desincroniza y dispara requests cross-domain. Se arma en el exploit server. | Encadenar un gadget de almacenamiento → hacer que el browser de la víctima **filtre su cookie** → entrar a su cuenta. |
| 22 | [Server-side pause-based request smuggling](https://portswigger.net/web-security/request-smuggling/browser/pause-based-desync/lab-server-side-pause-based-request-smuggling) | Expert | **Pause-based CL.0** (Apache 2.4.52 en endpoints de redirect): **pausás** entre headers y cuerpo para desincronizar. | Colar a `/admin` con `Host: localhost` → **borrar `carlos`**. |

---

## Esqueletos por familia

> Reglas de oro para todos: **request cruda por socket** (Repeater "Content-Length: update" **desactivado**, o script Python), terminadores **`\r\n` exactos**, y el `Content-Length` **exterior** debe cubrir **todo** el cuerpo (incluida la request colada). Muchos ataques hay que **enviarlos 2 veces**: la 1ª envenena, la 2ª (o la de la víctima) dispara.

**CL.TE** — front cuenta bytes, back cierra con el chunk `0`:
```http
POST / HTTP/1.1
Host: LAB
Content-Length: 6      ← cubre "0\r\n\r\nG" (los bytes que el front reenvía)
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
Foo: x
```

**TE.CL** — front cierra en el chunk, back cuenta bytes. El tamaño va en **hex** y el CL de la colada suele ser chico:
```http
POST / HTTP/1.1
Host: LAB
Content-Length: 4      ← el back (CL) lee solo "5c\r\n"
Transfer-Encoding: chunked

5c
GPOST /admin HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

x=1
0

```

**TE.TE (ofuscación)** — dos headers TE, uno malformado para que un server lo ignore:
```
Transfer-Encoding: chunked
Transfer-encoding: cow      ← también: "Transfer-Encoding : chunked", espacio+tab, doble
```

**H2.CL / H2.TE** — en HTTP/2 la longitud la fija el frame; agregás un `content-length`/`transfer-encoding` **mentiroso** que solo importa tras el **downgrade** a HTTP/1.1.

**CRLF injection en H2** — metés `\r\n` dentro de un valor de header (Burp permite escribirlo literal en el editor H2) para inyectar `Transfer-Encoding: chunked` o partir la request.

---

## 🛠️ Scripts de la carpeta

En [[vulnerabilities/008-http_smuggling/scripts|scripts/]] — todos en **Python** (socket crudo, sin librerías que "arreglen" tus headers).

**✅ Andan (los que uso hoy):**
- **[[vulnerabilities/008-http_smuggling/scripts/cl_te.py|cl_te.py]]** — explota **CL.TE** (chunk `0` + colada, calcula el CL exterior solo). → labs 1, 4, 6, 8-12.
- **[[vulnerabilities/008-http_smuggling/scripts/te_cl.py|te_cl.py]]** — explota **TE.CL**. → labs 2, 5, 7.
- **[[vulnerabilities/008-http_smuggling/scripts/detect.py|detect.py]]** — detector por **timing** CL.TE/TE.CL: manda una sonda ambigua; si el server se cuelga (timeout), es vulnerable a esa variante. Prueba **CL.TE primero** (recomendación de PortSwigger). → labs 1-5. ⚠️ **Parcial:** solo cubre CL.TE/TE.CL por timing; no detecta TE.TE, CL.0/0.CL ni variantes H2. Falta trabajo.

**🚧 WIP — todavía no andan bien (para después):**
- **[[vulnerabilities/008-http_smuggling/scripts/h2_cl.py|h2_cl.py]]** — **H2.CL** (lab 13).
- **[[vulnerabilities/008-http_smuggling/scripts/h2_te.py|h2_te.py]]** — **H2.TE** (lab 14).
- **[[vulnerabilities/008-http_smuggling/scripts/h2_rqp.py|h2_rqp.py]]** — **response queue poisoning** H2 (labs 14, 16).
- **[[vulnerabilities/008-http_smuggling/scripts/raw_socket.py|raw_socket.py]]** — helper para enviar bytes exactos por socket/TLS.

> Para los labs H2, hoy conviene ir a mano con Burp Repeater (HTTP/2, con **inspector** para escribir `\r\n` en headers) hasta arreglar estos scripts.

---

## Atajos mentales / patrones

- **La pista de que hay smuggling:** hay un **front-end/CDN/proxy** delante (headers tipo `Via`, `X-Forwarded-*`, `cache`), y podés mandar `Content-Length` **y** `Transfer-Encoding` juntos sin que te rechacen. Nunca lo confirmes por timing en producción ajena — **usá differential responses** (labs 4-5).
- **Nombre = quién usa qué:** `CL.TE` (front CL, back TE) · `TE.CL` (front TE, back CL) · `TE.TE` (empate → ofuscá) · `CL.0` (back ignora CL) · `0.CL` (front ignora CL).
- **Escalera de impacto:** probar el desync (`GPOST`) → saltar el front hacia `/admin` (**borrar carlos**) → robar la request/cookie del **próximo usuario** → XSS/redirect a la víctima → envenenar **caché** (afecta a todos).
- **HTTP/2:** si el front **degrada** a H1, casi todo lo clásico revive; sumá **CRLF injection** (H2 binario deja pasar `\r\n`) y **request tunnelling** cuando no hay desync total.
- **Enviar 2 veces:** casi siempre la primera envenena la conexión/cola y la segunda (tuya o de la víctima) es la que muestra el efecto.
- **Objetivo típico:** `GET /admin/delete?username=carlos` una vez que llegás al panel — igual que en el resto de la Academy.

> [!note] Ver también
> - **Scripts de explotación** (Python, socket crudo) → [[vulnerabilities/008-http_smuggling|carpeta 008]]
> - **Host header injection** — a veces se combina para llegar a `/admin` con `Host: localhost` (lab 22) → carpeta `vulnerabilities/016-host-header-injection/`
