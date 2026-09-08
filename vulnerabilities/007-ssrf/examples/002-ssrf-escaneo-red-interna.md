---
aliases:
  - SSRF 002 - escaneo de red interna
  - basic ssrf backend system
tags:
  - vuln/ssrf
  - example
  - portswigger
---

# 002 — SSRF a otro back-end (escanear la red interna)

> Lab: [Basic SSRF against another back-end system](https://portswigger.net/web-security/ssrf/lab-basic-ssrf-against-backend-system) · **Apprentice** · técnica → [[vulnerabilities/007-ssrf/ssrf|entry point]]

## ¿Por qué acá?
- **Vengo de [[vulnerabilities/007-ssrf/examples/001-ssrf-directo-localhost|001]]:** mismo control (`stockApi`), misma visibilidad (veo la respuesta), sin filtro.
- **Por qué no me alcanza 001:** el admin **no está en `localhost`** — vive en **otra máquina de la LAN** y no sé su IP. Tengo que **descubrirla**.
- **Entonces:** escaneo el rango privado `192.168.0.0/24` en el puerto `8080` hasta que uno responda con el panel.

## Cómo explotarlo
Poné el rango en `stockApi` y **fuzzeá el último octeto** con Burp **Intruder** (sniper, 1-255):
```http
POST /product/stock HTTP/1.1
Host: LAB.web-security-academy.net
Content-Type: application/x-www-form-urlencoded

stockApi=http://192.168.0.§1§:8080/admin
```
La IP que devuelva **200** (distinta a las "connection refused") tiene el panel. Después:
```http
stockApi=http://192.168.0.X:8080/admin/delete?username=carlos
```
> Alternativa en Python: [[vulnerabilities/007-ssrf/scripts/scan_internal.py|scan_internal.py]] itera el rango de forma async.

## Verificación
Una sola IP del rango responde 200 con el admin; el resto da error de conexión. Borrás carlos desde esa IP.

## Detalles que se pasan por alto
- **Puerto 8080**, no 80: el servicio interno escucha ahí.
- Ordená los resultados de Intruder por **status / longitud** para pescar el 200 entre los refused.
- Es SSRF como **pivote lateral**: el server es tu proxy hacia la red interna.

→ Siguiente: [[vulnerabilities/007-ssrf/examples/003-bypass-blacklist-variantes-localhost|003 · ahora empiezan a filtrarte localhost y "admin"]]
