---
aliases:
  - to-do Insecure Deserialization
tags:
  - exam/to-do
  - vuln/insecure-deserialization
---

# Insecure Deserialization — Qué probar

> Técnica → carpeta `vulnerabilities/013-insecure_deserialization/` (JAVA · PHP · Ruby)

## 🚩 Flags

> [!danger] 🚩 ¿Está?
> **Aparece una cookie/objeto serializado:** PHP `O:` · Java `rO0` (base64) · .NET · Python pickle.

## 🎯 Objetivo (Stage 3)
- **RCE** → `cat /home/carlos/secret`.

## ♾️ Independiente del stage
- [ ] Identificar el formato del objeto serializado.
- [ ] **Gadget chain:** **ysoserial** (Java, ej. CommonsCollections) / **phpggc** (PHP) → RCE.
- [ ] Modificar tipos/atributos si la lógica lo permite (escalada sin RCE).

## 🔗 Referencias
- carpeta `vulnerabilities/013-insecure_deserialization/` · cross-ref OSCi ysoserial → [[vulnerabilities/027-os-command-injection/examples/006-exfil-archivo-completo|006]]
