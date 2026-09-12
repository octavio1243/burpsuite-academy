---
aliases:
  - WCP 007 - unkeyed query string
  - cache buster
  - discrepancias de parseo de path
tags:
  - vuln/web-cache-poisoning
  - example
  - portswigger
---

# 007 — Query string entero unkeyed → el problema del CACHE BUSTER

> Lab: [Unkeyed query string](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-unkeyed-query) · **Practitioner** · técnica → [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|entry point]]

## Qué muestra
Cuando **todo el query string es unkeyed** (la key es solo `host + path`), cambiar `?param=…` **no genera una entrada nueva**: el caché te devuelve la copia vieja. Para **probar sin esperar** a que expire (y sin envenenar la key real por accidente), la **idea principal es lograr un CACHE BUSTER**: algo que **sí** cambie la key para que cada test traiga una respuesta **fresca**.

## El problema
- **Keyed:** `GET /` (solo el path). **Unkeyed:** `?param=cualquiercosa`.
- Mandás `?param=payload` → el reflejo puede estar, pero **la respuesta cacheada** es la anterior → no ves tu cambio hasta que caduque.

## Técnicas de cache buster

### 1) Cambiar headers que SÍ se keyean (sin romper la respuesta)
```http
Accept-Encoding: gzip, deflate, cachebuster
Accept: */*, text/cachebuster
Cookie: cachebuster=1
Origin: https://cachebuster.vulnerable-website.com
```
Cada valor único fuerza una **entrada nueva** en el caché → respuesta fresca para tu prueba.

### 2) Param Miner
Activá las opciones **"Add static/dynamic cache buster"** e **"Include cache busters in headers"** → Param Miner mete el buster solo en cada request.

### 3) Discrepancias de parseo frontend (proxy reverso) vs backend
Distintas formas de escribir el path que el **caché ve distinto** pero el **backend resuelve igual** → obtenés respuesta fresca (o servís bajo una key controlada):

| Server  | Truco                |
| ------- | -------------------- |
| Apache  | `GET //`             |
| Nginx   | `GET /%2F`           |
| PHP     | `GET /index.php/xyz` |
| .NET    | `GET /(A(xyz)/`      |

## Cómo explotarlo (weaponize)
1. Probá con **cache buster** hasta ver tu reflejo del query en la respuesta.
2. Confirmado el payload, **sacá el cache buster** y mandá la request contra la key real (`GET /`) → queda cacheada → todos los que pidan `/` reciben tu payload.

## Detalles que se pasan por alto
- El cache buster es **para vos** (testear limpio): al final **hay que quitarlo** para pegarle a la key que piden las víctimas.
- Las discrepancias de parseo sirven **doble**: como buster y como forma de **entregar** el payload bajo una URL que la víctima realmente visita.
- Verificá siempre con `X-Cache: hit` que la key real quedó envenenada.

→ Siguiente: [[vulnerabilities/030-web-cache-poisoning/examples/008-unkeyed-query-parameter|008 · Un parámetro unkeyed]]
