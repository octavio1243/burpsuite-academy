---
aliases:
  - WCP 009 - parameter cloaking
  - cache parameter cloaking Ruby on Rails
tags:
  - vuln/web-cache-poisoning
  - example
  - portswigger
---

# 009 — Cache parameter cloaking (esconder un parámetro de la key)

> Lab: [Parameter cloaking](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-param-cloaking) · **Practitioner** · técnica → [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|entry point]]

## Qué muestra
Cuando el caché **excluye un parámetro** de la key, "escondés" (*cloak*) un **segundo** parámetro **detrás** de ese excluido usando un separador que el **backend** interpreta distinto que el **caché**. Resultado: el caché no ve tu payload (cree que es parte del param excluido), pero el backend **sí lo procesa**.

## Cómo se ve

### Cloaking con un segundo `?`
```http
GET /?example=123?excluded_param=bad-stuff-here
```

### Ruby on Rails: separa por `&` **y por `;`**
```http
GET /?keyed_param=abc&excluded_param=123;keyed_param=bad-stuff-here
```
Rails parte el query en **3 parámetros**:
- `keyed_param=abc`
- `excluded_param=123`
- `keyed_param=bad-stuff-here`  ← **tiene precedencia** (gana el último)

## Por qué funciona
- El **caché** keyea `keyed_param=abc` y trata todo lo que va después de `excluded_param=` (incluido el `;keyed_param=bad-stuff-here`) como **valor del param excluido** → **no lo mete en la key**.
- El **backend (Rails)** interpreta el `;` como **separador** → ve un **segundo `keyed_param`** y le da **precedencia** → usa `bad-stuff-here`.
- Así **pisás un parámetro keyed** (metés tu payload) **sin cambiar la cache key** → se cachea envenenado.

## Cómo explotarlo (weaponize)
1. Identificá el param excluido (con [[vulnerabilities/030-web-cache-poisoning/examples/005-ver-cache-key-akamai|la cache key]] o Param Miner).
2. Escondé detrás de él un **parámetro que sí importa** (uno que la app refleje/use, p. ej. el `callback` de un JS) con `;` o `?`.
3. Poné el payload en ese parámetro cloakeado → cacheá.

## Detalles que se pasan por alto
- La técnica depende del **framework**: Rails separa por `;`; otros stacks tienen sus propias rarezas de parseo → **discrepancia caché vs backend**.
- Caso típico del lab: pisar el nombre de la **función callback** de un `.js` (`setCountryCookie` → `alert(1)`) → ejecución en la home.
- Emparenta con las **discrepancias de parseo de path** del [[vulnerabilities/030-web-cache-poisoning/examples/007-unkeyed-query-string-cachebuster|007]], pero acá es a nivel **parámetro**.

→ Siguiente: [[vulnerabilities/030-web-cache-poisoning/examples/010-fat-get|010 · Fat GET]]
