---
aliases:
  - OS Command Injection
  - os-command-injection-entrypoint
  - command injection
  - shell injection
  - RCE por comando
tags:
  - vuln/os-command-injection
  - entrypoint
---

# OS Command Injection — Punto de entrada

> Documento **agnóstico al negocio**: *cómo **detectar y explotar** la inyección de comandos*.
> **Dónde** aplica (qué feature llama al SO) → eso vive en los `STAGE_x`.

> [!abstract] La idea en una línea
> Una feature del server **arma un comando del sistema operativo con datos que vos controlás** (un ping, un `nslookup`, un conversor de imágenes, un mail…) y lo pasa a una **shell**. Si metés un **separador de comandos**, la shell ejecuta **tu** comando pegado al de la app → **RCE** con los privilegios del proceso web.

## 📚 Referencias rápidas

- 🐍 **Ejemplos / PoCs** (del más simple al más ciego, cada uno con su "por qué"):
    - [[vulnerabilities/027-os-command-injection/examples/001-simple-in-band|001 · caso simple (in-band)]] · [[vulnerabilities/027-os-command-injection/examples/002-blind-time-delay|002 · ciego por time delay]]
    - [[vulnerabilities/027-os-command-injection/examples/003-blind-output-redirection|003 · redirección de salida]] · [[vulnerabilities/027-os-command-injection/examples/004-blind-oob-interaction|004 · OOB por DNS]]
    - Exfil: [[vulnerabilities/027-os-command-injection/examples/005-blind-oob-exfil|005 · OOB por DNS ⭐]] · [[vulnerabilities/027-os-command-injection/examples/006-exfil-archivo-completo|006 · archivo entero (POST) ⭐]]
- 🔗 **OAST/Collaborator:** mismo canal que el [[vulnerabilities/007-ssrf/ssrf|SSRF ciego]].

## 🎯 Cuándo hay command injection (condiciones)

1. **Un input alimenta un comando del SO** — pistas clásicas: "check stock" con `storeID`, DNS/ping tools, feedback que manda mail (`mail -s`), thumbnails/PDF (`convert`, `wkhtmltopdf`), backups, `ping`/`nslookup`/`whois`.
2. **La app usa una shell** (`system()`, `exec()` con shell, `os.system`, backticks de Perl/PHP…) → los **metacaracteres** de la shell se interpretan.
3. **Tu dato no está saneado** (o el filtro es débil / escapea mal).

## 🧪 Cómo detectarlo (metodología)

1. **Encontrá el input que alimenta un comando** — stock checker (`storeId`), formulario de feedback (`email`), tools de ping/DNS/whois, generadores de PDF/thumbnails.
2. **¿La salida vuelve en la respuesta?** → **in-band**, RCE directo (001).
3. **¿No ves nada?** → sos **ciego**: subí la escalera **en orden**, de más simple a más furtivo (002 → 005).

| Situación | Técnica | Ejemplo |
| --- | --- | --- |
| Ves la salida en la respuesta | separador + comando | [[vulnerabilities/027-os-command-injection/examples/001-simple-in-band\|001 · in-band]] |
| No ves salida — confirmar que ejecuta | **time delay** (`ping`) | [[vulnerabilities/027-os-command-injection/examples/002-blind-time-delay\|002 · time delay]] |
| Ejecuta, pero querés **leer** la salida (hay dir web escribible) | **redirección** a archivo | [[vulnerabilities/027-os-command-injection/examples/003-blind-output-redirection\|003 · redirección]] |
| Sin dir escribible / HTTP saliente filtrado | **OAST** por DNS (confirmar) | [[vulnerabilities/027-os-command-injection/examples/004-blind-oob-interaction\|004 · OOB DNS]] |
| Confirmado por DNS, querés un **dato corto** | **exfil** en el subdominio (inline) | [[vulnerabilities/027-os-command-injection/examples/005-blind-oob-exfil\|005 · OOB exfil]] |
| El dato es un **archivo entero** (secreto/token) | **POST** del archivo por HTTP (`curl --data @` / `wget --post-file`) | [[vulnerabilities/027-os-command-injection/examples/006-exfil-archivo-completo\|006 · archivo entero]] |

> [!tip] Por qué se envuelve el payload (`x|| … ||` o `& … &`)
> El separador de adelante **cierra** el comando original; tu comando corre; el de atrás deja todo "cerrado" para que **lo que la app pegue después** (comillas, más argumentos) **no rompa** tu inyección. Es el equivalente al header "colador" del smuggling: dejás prolijo alrededor de lo tuyo.

> [!note] Mismo Collaborator que en SSRF
> El OAST acá es idéntico al de [[vulnerabilities/007-ssrf/ssrf|SSRF ciego]]: no ves la respuesta, así que **hacés que el server te "llame" afuera**. DNS > HTTP porque el egress de DNS casi nunca está filtrado.

---

## 🧩 Separadores de comandos (la chuleta)

La discrepancia clave es **qué shell hay detrás**. Los primeros sirven en Windows y Unix; el resto es Unix-only.

**Linux y Windows:**
- `&` — corre lo tuyo en background y sigue
- `&&` — corre lo tuyo **si** el 1º salió OK
- `|` — pipe: la salida del 1º entra al 2º
- `||` — corre lo tuyo **si** el 1º **falló**

**Solo Linux:**
- `;` — separador de comandos secuencial
- **Newline** (`0x0a` / `\n`) — una línea nueva **es** un separador

> [!tip] Cuál probar primero
> Empezá con **`&`** (anda en las dos plataformas y no depende de que el 1º comando falle o no). Si el input va dentro de comillas o de un argumento, mirá **ejecución inline** ↓.

## 🔤 Ejecución inline (Unix) — cuando no podés separar

Si tu input cae **dentro** de un comando ya armado (p. ej. entre comillas) y los separadores no cortan, ejecutás **anidado** — corre *dentro* del comando original y su salida se sustituye ahí mismo:

```
` injected command `      ← backticks
$( injected command )     ← forma moderna, anidable
```

Ej: `filename=$(whoami).jpg` hace que el `whoami` se ejecute y su salida se use como nombre. Útil también para el **exfil por DNS** (`` `whoami` `` dentro del subdominio, como arriba).

## 🧰 Comandos básicos de recon

Lo primero que tirás al confirmar RCE, para ubicarte:

| Propósito | Linux | Windows |
| --- | --- | --- |
| Usuario actual | `whoami` | `whoami` |
| Sistema operativo | `uname -a` | `ver` |
| Configuración de red | `ifconfig` | `ipconfig /all` |
| Conexiones de red | `netstat -an` | `netstat -an` |
| Procesos corriendo | `ps -ef` | `tasklist` |

## 🛡️ Prevención (para el lado defensivo)

- **La regla de oro:** **no llamar a la shell del SO** desde código web. Usá APIs nativas del lenguaje (ej. una librería de mail en vez de invocar `mail`).
- Si es inevitable: **validación por whitelist** (valores permitidos, solo numérico, solo alfanumérico). **Nunca** intentes "escapar" los metacaracteres a mano — siempre se te escapa alguno.
- Correr el proceso con **mínimos privilegios**.

---

> [!tip] Reglas mentales
> - **Separador primero (`&`), inline (`` ` `` / `$()`) si estás encerrado en comillas.**
> - **Ciego = escalera:** `ping` (tiempo) → `> /var/www/…` (leer por HTTP) → `nslookup` (DNS/OAST + exfil).
> - **DNS sale casi siempre**, aunque HTTP esté filtrado.
> - **Recon mínimo** (`whoami`, `uname -a`) antes de escalar.

> [!note] Relación con otras vulns
> - **SSRF ciego** — mismo juego de OAST/Collaborator para confirmar sin ver la respuesta → [[vulnerabilities/007-ssrf/ssrf|SSRF]].
> - **File upload / deserialización** — otras rutas a RCE; command injection es la más directa cuando la app ya está llamando al SO.
