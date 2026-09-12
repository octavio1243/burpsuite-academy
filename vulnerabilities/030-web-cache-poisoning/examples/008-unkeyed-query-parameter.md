---
aliases:
  - WCP 008 - unkeyed query parameter
  - utm_content unkeyed
tags:
  - vuln/web-cache-poisoning
  - example
  - portswigger
---

# 008 — Un parámetro puntual unkeyed (`utm_content`)

> Lab: [Unkeyed query parameter](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-unkeyed-param) · **Practitioner** · técnica → [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|entry point]]

## Qué muestra
El caché **excluye de la key ciertos parámetros** (típicos de analítica: `utm_content`, `utm_source`, etc.) porque "no cambian la página". Pero si la app **los refleja**, tenés un input **unkeyed** perfecto: inyectás XSS en `utm_content` y **no cambia la key** → se cachea para todos.

## Request

```http
GET /?utm_content=<@burp_urlencode>'/><script>alert(1)</script><'</@burp_urlencode> HTTP/2
Host: 0ae0000303146144801476c300a5007e.web-security-academy.net
Pragma: x-get-cache-key
```

## Por qué funciona
- **Keyed:** `host + path` (y quizás otros params). **Unkeyed:** `utm_content`.
- El `Pragma: x-get-cache-key` te confirma que `utm_content` **NO aparece** en la key → mientras lo veas reflejado en el body, es explotable.
- El `<@burp_urlencode>…</@burp_urlencode>` es una **tag de Burp** que URL-encodea el payload en el envío (cómodo para no romper el parseo del query).

## Cómo explotarlo (weaponize)
1. Confirmá con `Pragma: x-get-cache-key` que `utm_content` no está en la key.
2. Verificá el reflejo del `'/><script>alert(1)</script><'` en la respuesta.
3. Cambiá `alert(1)` por exfil real y **cacheá** la respuesta (sin buster) → toda víctima que pida `/` (aunque no mande `utm_content`) recibe la copia envenenada.

## Detalles que se pasan por alto
- **Por qué `utm_content`:** los CDNs los excluyen a propósito para mejorar el hit-rate → son candidatos clásicos.
- Distinto del [[vulnerabilities/030-web-cache-poisoning/examples/007-unkeyed-query-string-cachebuster|007]]: allá es **todo** el query, acá es **un** parámetro puntual.
- Si el param excluido **no se refleja** pero la app igual lo procesa, mirá **[[vulnerabilities/030-web-cache-poisoning/examples/009-parameter-cloaking|parameter cloaking (009)]]**.

→ Siguiente: [[vulnerabilities/030-web-cache-poisoning/examples/009-parameter-cloaking|009 · Parameter cloaking]]
