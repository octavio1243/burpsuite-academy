---
aliases:
  - Deser 004 - arbitrary object injection PHP
  - CustomTemplate __destruct unlink
tags:
  - vuln/insecure-deserialization
  - example
  - portswigger
---

# 004 — Object injection en PHP (`__destruct` → `unlink`)

> Lab: [Arbitrary object injection in PHP](https://portswigger.net/web-security/deserialization/exploiting/lab-deserialization-arbitrary-object-injection-in-php) · **Practitioner** · técnica → [[vulnerabilities/013-insecure_deserialization/insecure-deserialization|entry point]]

## Ficha
- **Objeto:** PHP — pero **inyectás OTRA clase** (`CustomTemplate`), no la `User` esperada.
- **Codificación:** `base64` → `url`.
- **Herramienta:** ninguna, **a mano** (escribís el serializado vos).
- **Efecto:** el `__destruct()` de `CustomTemplate` hace `unlink($lock_file_path)` → borra `morale.txt`.

## El primer paso: leer el código fuente
El backup del editor queda accesible agregando **`~`** al archivo:
> `GET /libs/CustomTemplate.php`==`~`==

Ahí ves que `CustomTemplate` tiene un `__destruct()` que llama `unlink()` sobre `$this->lock_file_path`.

## El ataque
Forjás **un objeto de esa clase** con la ruta de la víctima y lo metés en la cookie:

> `O:14:"`==`CustomTemplate`==`":1:{s:14:"lock_file_path";s:23:"`==`/home/carlos/morale.txt`==`";}`

Al terminar el request, PHP destruye el objeto → dispara `__destruct()` → `unlink('/home/carlos/morale.txt')`.

## Por qué funciona
- `unserialize()` acepta **cualquier clase** que exista en el código, no solo `User`. Eso es *arbitrary object injection*.
- El **magic method `__destruct()` corre solo** al final → no necesitás que la app "use" el objeto para nada.

## Detalles que se pasan por alto
- **El `~` (o `.bak`, `.old`, `.swp`) filtrando fuente** es medio lab en sí mismo: sin el código no sabés qué gadget hay.
- Acá el gadget es **una sola clase**; cuando hace falta **encadenar varias**, mirás [[vulnerabilities/013-insecure_deserialization/examples/009-php-custom-gadget|009 (gadget chain PHP)]].

→ Siguiente: [[vulnerabilities/013-insecure_deserialization/examples/005-java-apache-commons-ysoserial|005 · Java · ysoserial]]
