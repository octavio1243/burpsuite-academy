# STAGE 1 — FOOTHOLD

> **Objetivo:** acceder a una cuenta de usuario con **bajos privilegios**.
> Solo pueden aparecer las vulns de esta lista. Metodología = qué probar, en orden.

## 🚦 Arranque (siempre)

- [ ] **Burp Scan** → *full domain* (dejar corriendo de fondo).
- [ ] Navegar toda la app logueado/deslogueado → poblar el *site map* + Proxy history.
- [ ] Extensiones activas: **Param Miner**, **HTTP Request Smuggler**, **InQL**.
- [ ] Mirar JS del cliente buscando *sinks*: `location`, `eval`, `replace`, `addEventListener`, `postMessage`, `ng-app`.
- [ ] Registrar/loguear si se puede → ver rol y qué endpoints toca.

---

## ✅ Checklist de vulnerabilidades (Stage 1)

### 1. Content Discovery
- [ ] Burp *Discover content* (engine) sobre la raíz.
- [ ] `robots.txt`, `sitemap.xml`, `/.git`, comentarios HTML, backups (`.bak`, `~`, `.old`).
- [ ] Endpoints/rutas de admin o API expuestos.
- 📁 `information-disclousure/`

### 2. DOM-XSS
- [ ] Rastrear *source → sink* en el JS: `location.hash/search`, `document.referrer`, `postMessage`.
- [ ] Sinks: `innerHTML`, `eval`, `document.write`, `location`, `setTimeout`, jQuery `$()`, `ng-app` (AngularJS sandbox escape).
- [ ] Probar por `#`/query params. Ofuscar si hay filtro.
- 📁 `xss/` · ofuscación en `obfuscacion/`

### 3. XSS (reflejado / almacenado)
- [ ] Inyectar marcador único en cada input reflejado y buscarlo en la respuesta.
- [ ] Identificar **contexto** (HTML, atributo, script, URL) → payload acorde.
- [ ] Robo de sesión / forzar acción → escalar a otra cuenta.
- 📁 `xss/`

### 4. Web Cache Poisoning
- [ ] Detectar caché: `X-Cache: hit/miss`, `Age`, `Cache-Control`.
- [ ] **Param Miner** → *Guess headers* (unkeyed inputs).
- [ ] Envenenar con header no-keyed (`X-Forwarded-Host`, `X-Host`…) → XSS/redirect servido a otros.
- 📁 (crear) — ver `host-header-injection/`

### 5. Host Header Injection
- [ ] Cambiar `Host` → ¿se refleja? ¿password reset apunta ahí?
- [ ] `X-Forwarded-Host`, doble `Host`, `Host: localhost` → acceso interno / bypass.
- [ ] Combinar con reset de contraseña (link envenenado).
- 📁 `host-header-injection/`

### 6. HTTP Request Smuggling
- [ ] **HTTP Request Smuggler** → *Launch smuggle probe*.
- [ ] Probar **CL.TE** y **TE.CL** manualmente si el probe marca algo.
- [ ] Capturar request de otro usuario / bypass de front-end controls.
- 📁 `http_smuggling/`

### 7. Brute Force
- [ ] Enumerar usuarios: diferencias en mensaje/tiempo ("Invalid username or password").
- [ ] Password spray sobre user válido. Ojo con **rate limit** (X-Forwarded-For para resetear contador).
- [ ] Scripts listos en `brute-force/` (enum + spray).
- 📁 `brute-force/`

### 8. Authentication
- [ ] Lógica rota: 2FA saltable, "remember me" con token predecible, verificación de paso omitible.
- [ ] Fuerza bruta de código 2FA (`brute-force/script.py`).
- [ ] Truncamiento de contraseña, credenciales por defecto.
- 📁 `brute-force/` (2FA) · (crear `authentication/`)

---

> [!success] Salida del Stage 1
> Sesión/credenciales de un usuario normal → guardar cookie/token para el **Stage 2**.
