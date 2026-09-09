---
aliases:
  - HTTP Smuggling 003 - TE.TE
  - te.te
  - obfuscating TE header
tags:
  - vuln/http-smuggling
  - example
  - portswigger
---

# 003 — TE.TE (ofuscación del header)

> Lab: [Obfuscating the TE header](https://portswigger.net/web-security/request-smuggling/lab-obfuscating-te-header) · **Practitioner** · técnica → [[vulnerabilities/008-http_smuggling/http-smuggling|entry point]]

## ¿Por qué acá?

- **Vengo de [[vulnerabilities/008-http_smuggling/examples/001-cl-te|001]] y [[vulnerabilities/008-http_smuggling/examples/002-te-cl|002]]:** ahí uno de los servers usaba CL y el otro TE, y el desync salía "gratis".
- **Por qué no me alcanzan:** acá **los dos servers soportan `Transfer-Encoding`** (es un caso **TE.TE**). Si mandás un `chunked` normal, **ambos** lo procesan igual → **no hay desync**.
- **Entonces:** hay que **ofuscar** el header `Transfer-Encoding` de modo que **uno de los dos lo ignore** (y caiga a `Content-Length`) mientras **el otro lo sigue procesando**. En cuanto rompés el empate, el caso **se convierte en CL.TE o TE.CL** y lo explotás igual que 001/002.

## La idea clave

**TE.TE no es una técnica nueva de armado del cuerpo** — es CL.TE o TE.CL **disfrazado**. Lo único distinto es que tenés que **encontrar la ofuscación** que hace que un server se "coma" el `Transfer-Encoding`:

- Si el que ignora el TE es el **front-end** → el front usa CL, el back usa TE → **TE.CL**… ojo: front CL / back TE es **CL.TE**. Cuidá cuál ignora:
  - **Front ignora TE (usa CL), back procesa TE** → **CL.TE** → armá el cuerpo como en [[vulnerabilities/008-http_smuggling/examples/001-cl-te|001]].
  - **Front procesa TE, back ignora TE (usa CL)** → **TE.CL** → armá el cuerpo como en [[vulnerabilities/008-http_smuggling/examples/002-te-cl|002]].
- **No sabés de antemano cuál lo va a ignorar** → probás las ofuscaciones **una por una** hasta que una funcione, y según cuál rompa, seguís por el molde de 001 o de 002.

## Ofuscaciones a probar

> [!info] Color
> <span style="color:#d17a22"><b>■ Naranja = lo que cambiás VOS</b></span>: el header `Transfer-Encoding` ofuscado. Es lo único que varía respecto de 001/002; el **resto del cuerpo** (chunks / CL) se arma igual que en el molde que termine aplicando.

Cada variante busca que **un parser** acepte el header como `Transfer-Encoding: chunked` válido y **el otro no**:

| # | Ofuscación | Cómo se ve | Por qué puede romper el empate |
| --- | --- | --- | --- |
| 1 | Valor con basura | <span style="color:#d17a22">`Transfer-Encoding: xchunked`</span> | Un parser tolerante busca "chunked" como substring y lo acepta; uno estricto ve `xchunked` (valor desconocido) y lo ignora → usa CL. |
| 2 | Espacio antes de `:` | <span style="color:#d17a22">`Transfer-Encoding : chunked`</span> | El header con espacio antes de los dos puntos es inválido para unos (lo ignoran) y normalizado por otros. |
| 3 | Header duplicado | <span style="color:#d17a22">`Transfer-Encoding: chunked`</span><br><span style="color:#d17a22">`Transfer-Encoding: x`</span> | Un server usa el **primero** (chunked), el otro el **segundo** (`x`, inválido → CL). |
| 4 | Tab en vez de espacio | <span style="color:#d17a22">`Transfer-Encoding:[tab]chunked`</span> | Unos aceptan el TAB como separador válido, otros no reconocen el valor. |
| 5 | Espacio inicial (indent) | <span style="color:#d17a22">`[space]Transfer-Encoding: chunked`</span> | La línea indentada se lee como **continuación** del header anterior (o header inválido) para unos, header normal para otros. |
| 6 | Inyección de línea | <span style="color:#d17a22">`X: X[\n]Transfer-Encoding: chunked`</span> | Un parser que corta en `\n` ve dos headers (y procesa el TE); otro lo ve todo como el valor de `X` y no ve el TE. |
| 7 | Nombre partido (folding) | <span style="color:#d17a22">`Transfer-Encoding[\n] : chunked`</span> | El "line folding" (continuación en la línea siguiente) lo re-arma un parser y lo descarta el otro. |

> `[tab]` = carácter tabulador · `[space]` = espacio literal al inicio · `[\n]` = salto de línea (LF) crudo. En Burp escribilos a mano; **no dejes que "Update Content-Length" ni el normalizador te los borre**.

## Cómo detectarlo / explotarlo (paso a paso)

1. **Confirmá que es TE.TE:** un `chunked` limpio no desincroniza (001/002 no dan), pero el sitio claramente usa TE. → sospechá empate.
2. **Probá una ofuscación** (empezá por la #1 o #3, las más comunes).
3. **Mirá qué pasa** con la sonda de detección (mismo criterio que el entry point):
   - Si rompe como **CL.TE** → seguí el molde de [[vulnerabilities/008-http_smuggling/examples/001-cl-te|001]] (recordá: **CL.TE se prueba primero, no contamina**).
   - Si rompe como **TE.CL** → molde de [[vulnerabilities/008-http_smuggling/examples/002-te-cl|002]] (**contamina el socket, cuidado**).
4. **Explotá igual que el molde** que aplicó: `SMUGGLED` = request completa, `Content-Length` grande, mandar 2 veces.

**Objetivo del lab:** que la **siguiente** request procesada por el back use el método **`GPOST`** (prueba de desync) — igual que 001/002, pero solo lo lográs con el header ofuscado.

## Detalles que se pasan por alto

- **TE.TE ≠ técnica nueva:** es CL.TE/TE.CL con el header disfrazado. Todo el conteo de bytes/chunks es idéntico al molde que aplique.
- **Es prueba y error:** ninguna ofuscación funciona en todos lados; probá la lista hasta que una rompa el empate.
- **No sanear el header:** cualquier herramienta que "normalice" tus headers (o el "Update Content-Length" de Repeater) te borra justo la ofuscación. Usá request cruda.
- **Cuidá cuál server ignora el TE** → eso define si es CL.TE (no contamina) o TE.CL (contamina).

→ Siguiente: [[vulnerabilities/008-http_smuggling/examples/004-h2-cl|004 · H2.CL (salto a HTTP/2)]]
