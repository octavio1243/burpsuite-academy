---
aliases:
  - Deser 007 - Ruby documented gadget chain
  - Ruby Marshal universal RCE gadget
tags:
  - vuln/insecure-deserialization
  - example
  - portswigger
---

# 007 — Ruby con gadget chain documentado (Marshal) ⭐

> Lab: [Exploiting Ruby deserialization using a documented gadget chain](https://portswigger.net/web-security/deserialization/exploiting/lab-deserialization-exploiting-ruby-deserialization-using-a-documented-gadget-chain) · **Practitioner** · técnica → [[vulnerabilities/013-insecure_deserialization/insecure-deserialization|entry point]]

## Ficha
- **Objeto:** Ruby **Marshal** (binario nativo; en base64 empieza con **`BAh`** = `04 08` crudo).
- **Codificación:** binario Marshal → `base64` → `url` → cookie.
- **Herramienta:** el **gadget universal de vakzz** (Ruby 2.x–3.0.2), generado con `ruby`.
- **Efecto:** **RCE** → `rm /home/carlos/morale.txt`.

## Generar el payload
No hay "ysoserial de Ruby": usás el **gadget chain documentado** ([devcraft.io](https://devcraft.io/2021/01/07/universal-deserialisation-gadget-for-ruby-2-x-3-x.html)) y solo cambiás el comando (`id` → `rm …`). En el vault: [`Ruby/serialize.py`](vulnerabilities/013-insecure_deserialization/Ruby/serialize.py) modo `gadget` lo arma vía Docker y lo devuelve en base64.

## El pipeline de codificación (lo importante)
> `Marshal.dump(payload)` (binario) **⟶** ==`base64`== **⟶** ==`url`== **⟶** cookie `session`

Reemplazás la cookie, mandás el request → al hacer `Marshal.load()` el gadget dispara `Kernel#system` con tu comando.

## Por qué funciona
- La app hace `Marshal.load()` sobre la cookie **sin validar** → reconstruye la cadena de objetos del gadget.
- La cadena encadena clases de la **stdlib/Gem** (`Gem::RequestSet`, `Net::WriteAdapter`, `TarReader`…) hasta llegar a `system("rm …")`.
- **`BAh` en base64 = Marshal de Ruby** → señal de que este gadget aplica.

## Detalles que se pasan por alto
- El gadget **depende de la versión de Ruby** (universal hasta **3.0.2**). Si falla, revisá la versión del target.
- Es **ciego** igual que Java: confirmás por el efecto, o exfiltrás con `wget --post-file`.
- El mismo script tiene modo `custom` para **forjar un objeto real** (ej. un `User`) cuando el ataque es de lógica y no de RCE.

→ Siguiente: [[vulnerabilities/013-insecure_deserialization/examples/008-java-custom-gadget-sqli|008 · Java custom → SQLi]]
