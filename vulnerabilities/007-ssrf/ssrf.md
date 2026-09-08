---
aliases:
  - SSRF
  - ssrf-entrypoint
  - Server-Side Request Forgery
  - server-side request forgery
tags:
  - vuln/ssrf
  - entrypoint
---

# SSRF — Punto de entrada

> Documento **agnóstico al negocio**: *cómo **detectar y explotar** SSRF*.
> **Payloads por lab** → [[vulnerabilities/007-ssrf/labs/README|labs/README]].
> **Dónde** aplica (qué feature come URLs) → eso vive en los `STAGE_x`.

> [!abstract] La idea en una línea
> Si una feature del server **hace una petición HTTP a una URL que vos controlás**, la redirigís a un **recurso interno** (`localhost`, `127.0.0.1`, `192.168.0.X:8080`, `169.254.169.254`) al que el firewall/ACL no te deja llegar de afuera. El server pide **por vos** desde adentro → accedés a paneles admin, metadata cloud o servicios internos.

## 📚 Referencias rápidas

- 🧪 **Laboratorios** — 7 labs (2 Apprentice + 3 Practitioner + 2 Expert), **payload exacto por lab** → [[vulnerabilities/007-ssrf/labs/README|labs/README]]
- 🛠️ **Scripts** (escaneo de red interna en Python) → [[vulnerabilities/007-ssrf/example1.py|example1.py]] (async, itera `192.168.0.X`)
- 🔗 **XXE → SSRF:** una entidad XML puede apuntar a una URL interna → [[vulnerabilities/006-xxe/examples/002-xxe-a-ssrf-metadata-cloud|XXE ejemplo 002]].
- 🔗 **Open redirection:** es el *pivote* del filtro whitelist (lab 5) — si no podés falsear el host, dejás que otra feature redirija por vos.

## 🎯 Cuándo hay SSRF (condiciones)

1. **Un parámetro lleva una URL o un host** — `stockApi`, `url`, `path`, `dest`, `feed`, `callback`, `next`, previews de link, webhooks, importadores de XML/imágenes.
2. **El server la va a *buscar*** (fetch server-side), no solo a guardarla.
3. **Hay algo interno que vale la pena** — panel admin sin auth desde localhost, otro back-end en la LAN, o metadata cloud.

## 🧪 Cómo cazarlo (metodología)

1. **Encontrá el parámetro URL.** El clásico es **"Check stock"** (`POST /product/stock`, body `stockApi=<URL>`). Ojo también con **partial URLs** (solo el host o solo el path) y con la **superficie oculta** (ver más abajo).
2. **Apuntá adentro.** Cambiá el valor por `http://localhost/admin` (o `http://127.0.0.1/`). ¿Vuelve algo distinto (200, HTML del admin, error interno)? → **SSRF directo** ✅.
3. **¿No refleja nada? → blind.** Poné tu **Collaborator** en el valor (o en el `Referer`) y **Poll now**: si hay DNS/HTTP → SSRF ciego confirmado.
4. **¿Te bloquean?** Identificá el filtro (blacklist vs whitelist) y andá a la [chuleta de bypass](#🔓-bypass-de-filtros).
5. **Escalá.** Panel admin → **borrar carlos** (`/admin/delete?username=carlos`). Interno ciego → buscá un servicio **vulnerable** (RCE).

> [!note] ¿Requiere enviar exploit?
> **No** en los directos: se dispara en la **misma request** que mandás vos (Repeater). Solo necesitás **Collaborator** cuando es **blind** (labs 3 y 6). No hace falta víctima/admin como en CSRF/XSS.

---

## 🧩 Árbol de decisión (cada fila → su lab)

| Situación | Técnica | Lab |
| --- | --- | --- |
| Controlás la URL **y ves la respuesta**, sin filtro | **SSRF directo a `localhost`** | [[vulnerabilities/007-ssrf/labs/README\|L1]] |
| Igual, pero el target es **otro back-end** interno | **Escaneo `192.168.0.X:8080`** (Intruder) | [[vulnerabilities/007-ssrf/labs/README\|L2]] |
| **No ves** la respuesta (algo dispara la request) | **Blind → Collaborator (OOB)** | [[vulnerabilities/007-ssrf/labs/README\|L3]] |
| Bloquea `localhost`/`127.0.0.1`/`admin` | **Bypass blacklist** (reps IP + encode) | [[vulnerabilities/007-ssrf/labs/README\|L4]] |
| Solo acepta el **dominio propio** (whitelist) | **Bypass whitelist** (`@`, `#`, encode) | [[vulnerabilities/007-ssrf/labs/README\|L7]] |
| No podés **falsear el host** | **Open redirect** de otra feature | [[vulnerabilities/007-ssrf/labs/README\|L5]] |
| Blind, querés **impacto real** | **Servicio interno vulnerable → RCE** (Shellshock) | [[vulnerabilities/007-ssrf/labs/README\|L6]] |

## 🗺️ Qué probar primero (flujo)

```mermaid
flowchart TD
    S(["Un parámetro lleva una URL o un host"]) --> V{"¿Ves la respuesta<br/>del fetch?"}
    V -->|Sí · directo| F{"¿Hay filtro?"}
    V -->|No · ciego| C["L3 · confirmar con Collaborator"]
    F -->|Sin filtro| D["L1/L2 · localhost o 192.168.0.X:8080"]
    F -->|Blacklist| B["L4 · 127.1 / decimal / doble-encode"]
    F -->|Whitelist| W["L7 · user@host + # doble-encode"]
    F -->|No puedo falsear el host| O["L5 · open redirect"]
    C --> R["L6 · servicio interno vulnerable a RCE"]
```

---

## 🔓 Bypass de filtros

### Blacklist (bloquea `localhost`, `127.0.0.1`, `admin`…)
- **Reps alternativas de `127.0.0.1`:** `127.1` · decimal `2130706433` · octal `017700000001` · `[::1]` · `0`.
- **Dominio propio que resuelve a `127.0.0.1`** (o `spoofed.<tu-collaborator>`).
- **Encoding de la palabra filtrada:** `admin` → doble-encode una letra (`a` = `%2561`) → `%2561dmin`. A veces hay que insistir con más encoding.
- **Mayúsculas mezcladas** en host/path (`ADMIN`, `LocalHost`).
- **Cambiar de esquema** (`http`↔`https`) si el filtro es específico de protocolo.

### Whitelist (solo acepta el dominio permitido `X`)
> Truco general: hacer que **el validador vea `X`** como host, pero **el cliente HTTP conecte a otro lado**. Aprovecha parseos inconsistentes.
- **Credenciales embebidas:** `https://X@evil-host` (el validador valida `X`, pero el host real es `evil-host`).
- **Fragmento `#`:** `https://evil-host#X` (el `#` corta; el backend ignora lo de después).
- **Combo del lab 7:** `http://localhost:80%2523@stock.weliketoshop.net/admin` (`%2523` = `%23` = `#` doble-encodeado).
- **Sub-dominio:** `https://X.evil-host` (si el filtro hace "contiene X").
- **URL-encode / doble-encode** de `/` (`%2f`, `%252f`) y `.` (`%2e`, `%252e`) si validador y backend decodifican distinto.

### Vía open redirect (cuando no podés falsear el host)
Si el `stockApi` solo acepta rutas del propio sitio, apuntá a un endpoint **con open redirect** y que **él** reenvíe adentro:
```
stockApi=/product/nextProduct?path=http://192.168.0.12:8080/admin
```

---

## 🕳️ Superficie oculta (dónde más buscar)

- **`Referer` header:** el **analytics** suele visitar la URL del `Referer` → SSRF ciego (labs 3 y 6). Meté tu Collaborator ahí.
- **Partial URLs:** el parámetro es solo el **host** o solo el **path** y el server arma la URL completa → control limitado, pero explotable.
- **URLs dentro de formatos de datos:** **XML** (SVG, SOAP, DOCX) puede llevar una entidad que apunta a una URL interna → **[[vulnerabilities/006-xxe/xxe|XXE → SSRF]]**.

---

> [!tip] Reglas mentales
> - **Objetivos internos:** `http://localhost/admin` · `http://192.168.0.X:8080/` (**escanealo con Intruder**) · `http://169.254.169.254/` (metadata cloud) · `file:///…` si acepta el esquema.
> - **Directo → apuntá y actuá. Ciego → Collaborator.** Sin excepción.
> - **Escalera de filtros:** sin filtro → blacklist (reps/encode) → whitelist (`@`/`#`/encode) → o esquivá con **open redirect**.
> - **El impacto casi siempre es** panel admin → `/admin/delete?username=carlos`. En ciego, buscá **RCE** en el servicio interno.

> [!note] Relación con otras vulns
> - **XXE** — vector clásico para llegar a la red interna/metadata → [[vulnerabilities/006-xxe/xxe|XXE]].
> - **Open redirection** — habilita el bypass de whitelist (lab 5).
> - **CSRF** — no confundir: CSRF hace que **la víctima** mande la request; SSRF hace que **el server** la mande. Acá el enemigo es el servidor.
