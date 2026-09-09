---
aliases:
  - OS Command Injection 002 - blind time delay
  - blind command injection ping
tags:
  - vuln/os-command-injection
  - example
  - portswigger
---

# 002 — Ciego por time delay (confirmar por tiempo)

> Lab: [Blind OS command injection with time delays](https://portswigger.net/web-security/os-command-injection/lab-blind-time-delays) · **Practitioner** · técnica → [[vulnerabilities/027-os-command-injection/os-command-injection|entry point]]

## ¿Por qué acá? (cambia el juego)
- **En 001 veías la salida.** Acá el comando corre **asíncrono** y **no afecta la respuesta** → sos **ciego**, no ves nada.
- **Primer paso ciego:** antes de intentar leer la salida, confirmá que **el comando ejecuta**. La forma más simple: hacé que **tarde** y medí.

## Dónde se incrusta
- Feature: **formulario de feedback** → `POST /feedback/submit`, params `csrf`, `name`, `email`, `subject`, `message`.
- El vulnerable es **`email`** (el back lo usa en un comando de mail).

## Cómo explotarlo
Metés un comando que **demore** y medís. Dos formas:
```
email=test%40test.com||sleep+5||          ← sleep: el más limpio (5s exactos)
email=test%40test.com||ping+-c+5+127.0.0.1||   ← ping: N paquetes ≈ N segundos
```
La respuesta tarda ~5s (vs. instantánea sin el payload) → **ejecuta**.

> [!tip] Usá un email "de verdad" antes del `||`
> `test%40test.com` (= `test@test.com`, `%40` es el `@`) hace que el 1º comando/validación no falle raro. El `||` de la izquierda corta y el de la derecha aísla; así tu comando queda limpio en el medio.

## Verificación
- **Baseline:** mandá el form normal (responde al toque). Con el payload, ~10s → confirmado.
- Subí/bajá el número de paquetes y verificá que la demora escala con él (descarta falso positivo por lag).

## Detalles que se pasan por alto
- **Patrón `<relleno>|| … ||`** — el relleno (`x` o un email válido) alimenta el 1º comando y los `||` de los costados aíslan el tuyo. Con `||` corre "si el anterior falla", que acá conviene.
- **`+` = espacios URL-encoded** (vas por body `x-www-form-urlencoded`).
- **Windows:** `ping -n 10 127.0.0.1` (no `-c`).
- Esto **solo confirma que ejecuta**; todavía no leíste ninguna salida → 003.

→ Siguiente: [[vulnerabilities/027-os-command-injection/examples/003-blind-output-redirection|003 · leer la salida por redirección]]
