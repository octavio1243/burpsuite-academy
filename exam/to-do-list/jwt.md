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
- [ ] Forjar/alterar: **`alg:none`** ([[vulnerabilities/018-jwt-attacks/examples/002-alg-none|002]]), firma **no verificada** ([[vulnerabilities/018-jwt-attacks/examples/001-unverified-signature|001]]), **HS256 débil** (crackear con `crack_jwt.py` → [[vulnerabilities/018-jwt-attacks/examples/003-weak-signing-key|003]]), inyección **`jwk`** ([[vulnerabilities/018-jwt-attacks/examples/004-jwk-injection|004]]) / **`jku`** ([[vulnerabilities/018-jwt-attacks/examples/005-jku-injection|005]]) / **`kid`** ([[vulnerabilities/018-jwt-attacks/examples/006-kid-path-traversal|006]]).
- [ ] **Algorithm confusion** (RS256→HS256): con clave pública expuesta ([[vulnerabilities/018-jwt-attacks/examples/007-algorithm-confusion|007]]) o derivándola con `sig2n` ([[vulnerabilities/018-jwt-attacks/examples/008-algorithm-confusion-no-exposed-key|008]]).
- [ ] Cambiar `sub`/`role` → admin.

## 🔗 Referencias
- carpeta `vulnerabilities/018-jwt-attacks/` · [[vulnerabilities/018-jwt-attacks/crack_jwt.py|crack_jwt.py]] · ejemplos 001–008
