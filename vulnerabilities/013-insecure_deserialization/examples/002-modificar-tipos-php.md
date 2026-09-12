---
aliases:
  - Deser 002 - modifying serialized data types
  - PHP type juggling deserializacion
tags:
  - vuln/insecure-deserialization
  - example
  - portswigger
---

# 002 — Cambiar el TIPO del dato (type juggling `==`)

> Lab: [Modifying serialized data types](https://portswigger.net/web-security/deserialization/exploiting/lab-deserialization-modifying-serialized-data-types) · **Practitioner** · técnica → [[vulnerabilities/013-insecure_deserialization/insecure-deserialization|entry point]]

## Ficha
- **Objeto:** PHP serializado — `O:4:"User":2:{…}`
- **Codificación:** `base64`.
- **Herramienta:** ninguna, **a mano**.
- **Efecto:** logueás como `administrator` **sin saber su token**, abusando de la comparación floja `==` de PHP.

## El ataque
Cambiás el username y **degradás el tipo** del `access_token` de string a **entero `0`**:

> `O:4:"User":2:{s:8:"username";s:13:"`==`administrator`==`";s:12:"access_token";`==`i:0`==`;}`

- `username`: `s:6:"wiener"` → `s:13:"administrator"` (ojo: **cambia el largo** a `13`).
- `access_token`: `s:32:"…"` → `i:0` (entero cero, ya no un string).

## Por qué funciona
- El server valida el token con **`==` (comparación floja)**. En PHP < 8, `0 == "cualquier_string_no_numérico"` devuelve **`true`**.
- Al mandar `i:0`, la comparación `0 == "<token real de admin>"` da **true** → entrás sin conocer el token.

## Detalles que se pasan por alto
- **La clave es el TIPO, no el valor:** el mismo bug de `==` que ves en [[vulnerabilities/001-sql-injection/README|SQLi]]/lógica, acá se dispara **eligiendo el tipo** en el serializado.
- **Contá bien el largo del string** (`s:13:"administrator"`) o PHP rompe el unserialize.

→ Siguiente: [[vulnerabilities/013-insecure_deserialization/examples/003-usar-funcionalidad-app|003 · abusar una feature]]
