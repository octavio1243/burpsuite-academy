---
aliases:
  - SSRF 006 - ciego deteccion OOB
  - blind ssrf out-of-band
tags:
  - vuln/ssrf
  - example
  - portswigger
---

# 006 — SSRF ciego: detección out-of-band (Collaborator)

> Lab: [Blind SSRF with out-of-band detection](https://portswigger.net/web-security/ssrf/blind/lab-out-of-band-detection) · **Practitioner** · técnica → [[vulnerabilities/007-ssrf/ssrf|entry point]]

## ¿Por qué acá? (cambia el juego)
- **Hasta acá (001–005) SIEMPRE veías la respuesta** del fetch → apuntabas y leías.
- **Por qué eso ya no aplica:** la petición no la dispara un parámetro que te devuelve algo — la lanza el **software de analytics** al procesar el **`Referer`**, y **la respuesta no vuelve** al front. Sos **ciego**.
- **Entonces:** cambia el objetivo. Primero **confirmar que el SSRF existe** con un canal **out-of-band** (Burp **Collaborator**), porque no lo podés "ver".

## Cómo explotarlo
Generá un payload de Collaborator y ponelo en el **`Referer`** de una request a una página de producto:
```http
GET /product?productId=1 HTTP/1.1
Host: LAB.web-security-academy.net
Referer: http://TU-SUBDOMINIO.oastify.com
```
En Burp → **Collaborator → Poll now**.

## Verificación
Aparecen interacciones **DNS y/o HTTP** desde el server del lab hacia tu subdominio → **SSRF ciego confirmado**.

## Detalles que se pasan por alto
- **Va en el `Referer`, no en un parámetro** — esa es la "superficie oculta" (el analytics visita esa URL).
- Esto **solo confirma que existe**; no exfiltra nada por sí solo. Para **impacto real** hace falta un servicio interno vulnerable → [[vulnerabilities/007-ssrf/examples/007-ssrf-ciego-rce-shellshock|007]].
- Si no ves nada: probá también parámetros con URLs; el ciego puede estar en otras features además del `Referer`.

→ Siguiente: [[vulnerabilities/007-ssrf/examples/007-ssrf-ciego-rce-shellshock|007 · convertir el SSRF ciego en RCE (Shellshock)]]
