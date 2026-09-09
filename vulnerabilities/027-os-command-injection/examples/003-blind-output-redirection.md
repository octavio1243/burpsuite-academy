---
aliases:
  - OS Command Injection 003 - output redirection
  - blind command injection read output
tags:
  - vuln/os-command-injection
  - example
  - portswigger
---

# 003 — Ciego con redirección de salida (leerla por HTTP)

> Lab: [Blind OS command injection with output redirection](https://portswigger.net/web-security/os-command-injection/lab-blind-output-redirection) · **Practitioner** · técnica → [[vulnerabilities/027-os-command-injection/os-command-injection|entry point]]

## ¿Por qué acá? (de "ejecuta" a "leo la salida")
- **En 002 confirmaste que ejecuta, pero seguís sin ver nada.** Querés la **salida real** (`whoami`, `ls`…).
- **Truco:** si hay una **carpeta servida por la web y escribible**, redirigís la salida a un archivo ahí y **lo pedís con el browser**.

## Dónde se incrusta
- Mismo **`email`** del feedback (`POST /feedback/submit`).
- La app sirve imágenes de producto desde un dir web → ese dir suele ser **escribible**: `/var/www/images/`.

## Cómo explotarlo
1. Redirigís la salida a un archivo en el dir web:
```
email=||whoami>/var/www/images/output.txt||
```
2. Lo leés reutilizando la feature de imágenes — cambiás el `filename` por tu archivo:
```
GET /image?filename=output.txt HTTP/1.1
```
La respuesta trae el contenido de `output.txt` → **leíste la salida**.

## Verificación
- `GET /image?filename=output.txt` devuelve el usuario (`peter-XXXX`) en texto plano.

## Detalles que se pasan por alto
- **Necesitás un dir escribible Y servido.** El de imágenes es el candidato obvio; si no, probá otros paths o pasá a OAST (004).
- **`>` sobrescribe** el archivo cada vez — cómodo para ir tirando comandos distintos.
- **La feature de lectura ya existe** (el visor de imágenes): no “abrís” nada nuevo, **reutilizás** un endpoint legítimo.
- Si no hay dir escribible ni forma de leer archivos → el canal es **out-of-band** → 004/005.

→ Siguiente: [[vulnerabilities/027-os-command-injection/examples/004-blind-oob-interaction|004 · OOB por DNS (confirmar)]]
