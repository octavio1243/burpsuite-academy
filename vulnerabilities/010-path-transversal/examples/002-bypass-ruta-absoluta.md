---
aliases:
  - Path Traversal 002 - bypass con ruta absoluta
  - absolute path bypass
tags:
  - vuln/path-traversal
  - example
  - portswigger
---

# 002 — Bloquea `../`, pero acepta **ruta absoluta**

> Lab: [File path traversal, traversal sequences blocked with absolute path bypass](https://portswigger.net/web-security/file-path-traversal/lab-absolute-path-bypass) · **Practitioner** · técnica → [[vulnerabilities/010-path-transversal/path-transversal|entry point]]

## ¿Por qué acá? (primer filtro)
- **Qué defensa rompés:** el server **bloquea las secuencias `../`**, pero trata el nombre de archivo como **relativo a un directorio por defecto**.
- **Por qué funciona:** si no hace falta subir de directorio, **no necesitás `../`** en absoluto → una **ruta absoluta** apunta directo al archivo del sistema.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = host del lab + el **payload** (ruta **absoluta**, sin `../`).

<pre class="payload"><code>GET /image?filename=<mark>/etc/passwd</mark> HTTP/1.1
Host: <mark>LAB.web-security-academy.net</mark></code></pre>

## Verificación
Devuelve el contenido de **`/etc/passwd`** → lab resuelto. Si al mandar `../` te lo rechaza pero con `/etc/passwd` responde, confirmaste que **valida `../` pero resuelve rutas absolutas**.

## Detalles que se pasan por alto
- Es la primera prueba tras el `../` directo: **antes de complicarte con encoding, probá la ruta absoluta**.
- Funciona porque el filtro mira el **string `../`** literal, no el resultado canonicalizado del path.
- Si además validara el **inicio** del path (`/var/www/images/`), esto no alcanzaría → ahí prefijás la carpeta esperada y salís con `../`.

→ Siguiente: [[vulnerabilities/010-path-transversal/examples/003-bypass-secuencias-strippeadas|003 · elimina `../` una sola vez → `....//`]]
