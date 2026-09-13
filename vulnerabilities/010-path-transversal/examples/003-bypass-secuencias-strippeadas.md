---
aliases:
  - Path Traversal 003 - secuencias strippeadas no recursivamente
  - stripped sequences non-recursive
tags:
  - vuln/path-traversal
  - example
  - portswigger
---

# 003 — Strippea `../` **una sola vez** → `....//`

> Lab: [File path traversal, traversal sequences stripped non-recursively](https://portswigger.net/web-security/file-path-traversal/lab-sequences-stripped-non-recursively) · **Practitioner** · técnica → [[vulnerabilities/010-path-transversal/path-transversal|entry point]]

## ¿Por qué acá? (filtro que borra en vez de bloquear)
- **Qué defensa rompés:** el server **elimina** las secuencias `../` del input… pero lo hace **una sola vez** (no recursivo).
- **Por qué funciona:** si anidás las secuencias, al **borrar el `../` del medio** lo que queda **se reconstituye** en un `../` válido.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = host del lab + el **payload** anidado (`....//` por cada nivel).

<pre class="payload"><code>GET /image?filename=<mark>....//....//....//etc/passwd</mark> HTTP/1.1
Host: <mark>LAB.web-security-academy.net</mark></code></pre>

Cada `....//` → el filtro saca el `../` interno → queda `../`.

## Verificación
Devuelve **`/etc/passwd`** → lab resuelto. Confirmás el comportamiento si `../` te lo strippean pero `....//` cuela.

## Detalles que se pasan por alto
- **No es un encoding**, es **reconstrucción**: aprovechás que el reemplazo se aplica una única pasada.
- Si el filtro fuera **recursivo** (borra hasta que no queden), esto **no anda** → subís de nivel a **URL / doble URL encoding** (`..%2f`, `..%252f`).
- Variante equivalente: `..././` (mismo principio de anidado).

→ Siguiente: [[vulnerabilities/010-path-transversal/examples/004-bypass-extension-null-byte|004 · valida extensión `.png` → null byte `%00`]]
