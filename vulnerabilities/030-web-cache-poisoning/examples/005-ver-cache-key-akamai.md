---
aliases:
  - WCP 005 - ver la cache key
  - akamai x-get-cache-key
  - Pragma x-get-cache-key
tags:
  - vuln/web-cache-poisoning
  - example
  - portswigger
---

# 005 — Ver la cache key (recon: `Pragma: x-get-cache-key`)

> Técnica → [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|entry point]] · paso previo a **todos** los demás ejemplos

## Qué muestra
El **paso de reconocimiento** que ahorra tiempo: algunos CDNs **te dicen exactamente qué entra en la cache key**. En **Akamai**, mandás `Pragma: akamai-x-get-cache-key` y la respuesta trae `X-Cache-Key`. Sabiendo la key, distinguís al toque **qué es keyed** (no lo podés usar) de **qué es unkeyed** (tu arma).

## Request → Response

> `GET /?param=1 HTTP/1.1`
> `Host: innocent-website.com`
> `Pragma: `==`akamai-x-get-cache-key`==

**⬇️ te devuelve la key literal:**

> `HTTP/1.1 200 OK`
> `X-Cache-Key: `==`innocent-website.com/?param=1`==

(lo que NO figure en la key pero sí se refleje = **unkeyed**)

## Por qué sirve
- La `X-Cache-Key` te dibuja **la key literal**. Comparás lo que mandás contra lo que aparece:
  - Si un input **NO figura en la key** pero **sí se refleja en el body/headers** → **unkeyed** → candidato a envenenar.
  - Si figura en la key → cambiarlo genera una entrada nueva (sirve como **cache buster**, no como vector).
- Ejemplo: si `X-Cache-Key` es `.../?param=1` pero **omite** `utm_content`, ya sabés que `utm_content` es unkeyed (→ [[vulnerabilities/030-web-cache-poisoning/examples/008-unkeyed-query-parameter|008]]).

## Cómo usarlo
1. Repetí la request con `Pragma: akamai-x-get-cache-key` (o el genérico `Pragma: x-get-cache-key`).
2. Mirá `X-Cache-Key` y contrastá con los inputs que estás probando.
3. Confirmá el reflejo del input unkeyed en el cuerpo → pasá a armar el payload.

## Detalles que se pasan por alto
- No todos los CDNs lo exponen; cuando no, caés en el método clásico: **input reflejado + `X-Cache: hit` que no cambia** = unkeyed.
- Combinalo con **Param Miner** para barrer headers/params candidatos.
- Es puro recon: **no envenena nada**, te dice **dónde** apuntar.

→ Siguiente: [[vulnerabilities/030-web-cache-poisoning/examples/006-unkeyed-port|006 · Unkeyed port]]
