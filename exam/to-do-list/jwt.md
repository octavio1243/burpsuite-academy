---
aliases:
  - to-do JWT
tags:
  - exam/to-do
  - vuln/jwt
---

# JWT — Qué probar

> Técnica → carpeta `vulnerabilities/018-jwt-attacks/` · script → [[vulnerabilities/018-jwt-attacks/crack_jwt.py|crack_jwt.py]]

## 🚩 Flags

> [!danger] 🚩 ¿Está?
> **Requisito:** la sesión **es un JWT** (no una cookie de sesión simple).

## 🎯 Por stage
- **Stage 1:** forjar el token de la víctima. · **Stage 2:** cambiar `sub`/`role` → **administrator**.

## ♾️ Independiente del stage
- [ ] Forjar/alterar: **`alg:none`**, firma **no verificada**, **HS256 débil** (crackear con `crack_jwt.py`), inyección **`kid`/`jwk`/`jku`**.
- [ ] Cambiar `sub`/`role` → admin.

## 🔗 Referencias
- carpeta `vulnerabilities/018-jwt-attacks/` · [[vulnerabilities/018-jwt-attacks/crack_jwt.py|crack_jwt.py]]
