---
aliases:
  - Deser 003 - using application functionality
  - abusar feature borrar archivo
tags:
  - vuln/insecure-deserialization
  - example
  - portswigger
---

# 003 — Abusar una feature de la app (borrar archivo)

> Lab: [Using application functionality to exploit insecure deserialization](https://portswigger.net/web-security/deserialization/exploiting/lab-deserialization-using-application-functionality-to-exploit-insecure-deserialization) · **Practitioner** · técnica → [[vulnerabilities/013-insecure_deserialization/insecure-deserialization|entry point]]

## Ficha
- **Objeto:** PHP serializado (trae la ruta del avatar).
- **Codificación:** `base64`.
- **Herramienta:** ninguna, **a mano**.
- **Efecto:** que la app **borre `/home/carlos/morale.txt`** usando su propia función "delete account".

## El ataque
El objeto de sesión guarda la **ruta del avatar** del usuario. La feature *delete account* borra ese archivo. Apuntás la ruta al archivo de la víctima:

> `O:4:"User":3:{…s:11:"avatar_link";s:23:"`==`/home/carlos/morale.txt`==`";}`

Después clickeás **"Delete account"** → la app hace `unlink()` sobre esa ruta → borra el archivo de carlos.

## Por qué funciona
- **No hace falta gadget ni RCE:** usás una **funcionalidad legítima** (borrar tu avatar) pero **con una ruta que no es tuya**.
- La app confía en que `avatar_link` apunta a *tu* archivo; vos lo reapuntás.

## Detalles que se pasan por alto
- Esta clase de ataque = **"gadget" hecho de la propia lógica de negocio**, no de librerías. Buscá features que **lean/escriban/borren** según un campo del objeto.
- Recordá ajustar el **contador de longitud** (`s:23:"/home/carlos/morale.txt"` = 23 chars).

→ Siguiente: [[vulnerabilities/013-insecure_deserialization/examples/004-object-injection-php|004 · object injection]]
