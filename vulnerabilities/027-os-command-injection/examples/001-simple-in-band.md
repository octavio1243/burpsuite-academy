---
aliases:
  - OS Command Injection 001 - simple in-band
  - command injection simple case
tags:
  - vuln/os-command-injection
  - example
  - portswigger
---

# 001 — Caso simple (in-band: ves la salida)

> Lab: [OS command injection, simple case](https://portswigger.net/web-security/os-command-injection/lab-simple) · **Apprentice** · técnica → [[vulnerabilities/027-os-command-injection/os-command-injection|entry point]]

## ¿Por qué acá? (el más fácil)
- **La app arma un comando del SO con tu input y te devuelve la salida en la misma respuesta.** No necesitás víctima, ni Collaborator, ni tiempos: inyectás y **leés el resultado ahí mismo**.
- Es la base: si esto anda, tenés RCE directo. Todo lo demás (002–005) es "lo mismo pero **sin ver** la salida".

## Dónde se incrusta
- Feature: **check stock** → `POST /product/stock`, body `productId=1&storeId=1`.
- El back-end corre algo tipo `stockreport.pl <productId> <storeId>` → el **`storeId`** cae en el comando.

## Cómo explotarlo
En el `storeId`, cortás con un separador y pegás tu comando:
```
storeId=1|whoami
```
La respuesta trae el usuario (`peter-XXXX`) en vez del stock → **RCE confirmado**.

## Verificación
- La respuesta muestra la salida cruda de `whoami` donde iría el número de stock.

## Probá varios separadores
Si el `|` no corta, iterá — cada shell/contexto acepta distintos:
```
1|whoami
1||whoami
1;whoami
1&&whoami
```

## Detalles que se pasan por alto
- **`|` (pipe)** acá alcanza: pasa la salida del 1º comando al 2º y la app devuelve lo último. Si no, probá `||`, `&`, `&&`, `;` (ver [separadores](vulnerabilities/027-os-command-injection/os-command-injection.md)).
- **In-band = lujo.** En apps reales casi nunca ves la salida → pasás a la escalera ciega (002+).
- **Recon primero:** `whoami`, `uname -a` para ubicarte antes de escalar.

→ Siguiente: [[vulnerabilities/027-os-command-injection/examples/002-blind-time-delay|002 · ciego por time delay]]
