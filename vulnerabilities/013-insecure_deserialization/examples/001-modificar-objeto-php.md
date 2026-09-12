---
aliases:
  - Deser 001 - modifying serialized objects
  - flip de atributo PHP
tags:
  - vuln/insecure-deserialization
  - example
  - portswigger
---

# 001 — Flip de atributo en un objeto PHP (`admin`)

> Lab: [Modifying serialized objects](https://portswigger.net/web-security/deserialization/exploiting/lab-deserialization-modifying-serialized-objects) · **Apprentice** · técnica → [[vulnerabilities/013-insecure_deserialization/insecure-deserialization|entry point]]

## Ficha
- **Objeto:** PHP serializado — `O:4:"User":2:{…}`
- **Codificación:** `base64` (URL-encoded en la cookie).
- **Herramienta:** ninguna, **a mano** (decode → editar → re-encode).
- **Efecto:** `admin` de `false` → `true` → panel de admin → borrar a carlos. *(sin RCE)*

## El ataque
La cookie `session` es el objeto `User` serializado y base64-eado. Lo decodificás y solo cambiás el booleano:

> `O:4:"User":2:{s:8:"username";s:6:"wiener";s:5:"admin";b:`==`1`==`;}`

`b:0` (false) → `b:`==`1`== (true). Re-encodás en base64, reemplazás la cookie → sos admin.

## Por qué funciona
- La app **confía en el atributo `admin`** que viene dentro del objeto que ella misma te mandó. Nunca imaginó que lo ibas a editar.
- `b:1` es la sintaxis PHP de un booleano `true`. No tocás longitudes → no se rompe nada.

## Detalles que se pasan por alto
- **`b:` = boolean, `s:N:` = string (con largo N), `i:` = integer, `O:N:"Clase"` = objeto, `a:` = array.** Vale memorizar esto: es el idioma de PHP serializado.
- Es el "hola mundo" de la deserialización: entendés que **la cookie ES un objeto** y que podés reescribirlo.

→ Siguiente: [[vulnerabilities/013-insecure_deserialization/examples/002-modificar-tipos-php|002 · type juggling]]
