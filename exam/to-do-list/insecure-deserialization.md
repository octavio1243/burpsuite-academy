---
aliases:
  - to-do Insecure Deserialization
tags:
  - exam/to-do
  - vuln/insecure-deserialization
---

# Insecure Deserialization — Qué probar

> Técnica → [[vulnerabilities/013-insecure_deserialization/insecure-deserialization|entry point]] · [tabla maestra + 10 ejemplos](vulnerabilities/013-insecure_deserialization/insecure-deserialization.md)

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
- [[vulnerabilities/013-insecure_deserialization/insecure-deserialization|entry point + tabla maestra]] (lenguaje · codificación · herramienta por lab)
- ⭐ con herramienta: [[vulnerabilities/013-insecure_deserialization/examples/005-java-apache-commons-ysoserial|005 Java·ysoserial]] · [[vulnerabilities/013-insecure_deserialization/examples/006-php-phpggc-symfony|006 PHP·phpggc]] · [[vulnerabilities/013-insecure_deserialization/examples/007-ruby-gadget-documentado|007 Ruby·Marshal]]
- cross-ref OSCi ysoserial → [[vulnerabilities/027-os-command-injection/examples/006-exfil-archivo-completo|006]]
