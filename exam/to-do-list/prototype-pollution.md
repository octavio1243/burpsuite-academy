---
aliases:
  - to-do Prototype Pollution
tags:
  - exam/to-do
  - vuln/prototype-pollution
---

# Prototype Pollution — Qué probar

> Técnica → carpeta `vulnerabilities/020-prototype-pollution/`

## 🚩 Flags

> [!danger] 🚩 ¿Está?
> **`__proto__`** en query/JSON/params cambia el comportamiento. DOM Invader detecta source→sink (client-side).

## 🎯 Por stage
- **Stage 2 (client-side):** gadget que afecta la lógica → XSS/escalada. · **Stage 3 (server-side, SSPP):** escalar a **RCE**.

## ♾️ Independiente del stage
- [ ] Buscar **gadget**: `__proto__.<prop>` en query/JSON → propiedad que afecte la lógica.
- [ ] **Client-side:** DOM Invader (Burp) para source→sink.
- [ ] **Server-side (SSPP):** JSON con `__proto__` → detectar cambio server-side → escalar a RCE (gadget en el runtime, p.ej. `child_process`) → leer el secreto.

## 🔗 Referencias
- carpeta `vulnerabilities/020-prototype-pollution/`
