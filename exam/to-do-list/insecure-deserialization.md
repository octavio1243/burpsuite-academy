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

## 🎯 Por stage

> **Uso típico = Stage 3 (RCE).** Pero si la cookie de sesión es un objeto serializado, **también** sirve para escalar en Stage 2.

| Stage | Qué se logra | Cómo | Probabilidad |
| --- | --- | --- | --- |
| 🔴 **Stage 2** | escalar a **administrator** | editar atributos/tipos del objeto de sesión (`admin`→true, `access_token`→`i:0`) | **último recurso** |
| ⚫ **Stage 3** | **RCE** → `cat /home/carlos/secret` | gadget chain (ysoserial / phpggc / Marshal) | lo típico |

> [!tip] 💡 Stage 2 por deserialización (último recurso)
> Si **ya agotaste** los vectores normales de escalada (IDOR, roles, JWT…) **y** ves un objeto serializado en la cookie: probá **reescribirlo** sin herramienta.
> - **Flip de booleano:** `s:5:"admin";b:`==`1`==`;` → sos admin. → [[vulnerabilities/013-insecure_deserialization/examples/001-modificar-objeto-php|001]]
> - **Type juggling `==`:** `username`→`administrator` + `access_token`→`i:0` (PHP: `0 == "str"` es true). → [[vulnerabilities/013-insecure_deserialization/examples/002-modificar-tipos-php|002]]
>
> Es raro (normalmente la deser aparece para RCE en Stage 3), **pero totalmente posible** y **barato**: no necesitás gadget ni herramienta, solo decodificar → editar → re-encodear.

## ♾️ Independiente del stage
- [ ] Identificar el formato del objeto serializado.
- [ ] **Escalada (Stage 2, barato):** editar atributos/tipos si la lógica lo permite (`admin`, `access_token`, rutas) → 001–003.
- [ ] **RCE (Stage 3):** **gadget chain** — **ysoserial** (Java, ej. CommonsCollections) / **phpggc** (PHP) / Marshal (Ruby).

## 🔗 Referencias
- [[vulnerabilities/013-insecure_deserialization/insecure-deserialization|entry point + tabla maestra]] (lenguaje · codificación · herramienta por lab)
- ⭐ con herramienta: [[vulnerabilities/013-insecure_deserialization/examples/005-java-apache-commons-ysoserial|005 Java·ysoserial]] · [[vulnerabilities/013-insecure_deserialization/examples/006-php-phpggc-symfony|006 PHP·phpggc]] · [[vulnerabilities/013-insecure_deserialization/examples/007-ruby-gadget-documentado|007 Ruby·Marshal]]
- cross-ref OSCi ysoserial → [[vulnerabilities/027-os-command-injection/examples/006-exfil-archivo-completo|006]]
