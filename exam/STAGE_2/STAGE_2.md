# STAGE 2 — PRIVILEGE ESCALATION

> **Objetivo:** escalar del usuario normal (Stage 1) a **administrador**.
> Solo pueden aparecer las vulns de esta lista. Metodología = qué probar, en orden.

## 🚦 Arranque

- [ ] Ya logueado como user normal → mapear qué hace el **admin** que yo no puedo.
- [ ] Burp Scan → *Scan Insertion Points* sobre requests de Repeater interesantes.
- [ ] Comparar requests user vs. admin (¿solo cambia un `role`, `id`, cookie?).

---

## ✅ Checklist de vulnerabilidades (Stage 2)

### 1. CSRF → Account Takeover
- [ ] Endpoint que cambia email/password **sin** token CSRF (o token no validado).
- [ ] Generar PoC (Burp → *Generate CSRF PoC*), entregar al admin → tomar su cuenta.
- 📁 `csrf/`

### 2. Password Reset
- [ ] Token débil/predecible, reutilizable, o ligado al **Host header**.
- [ ] `username`/`user_id` manipulable en el POST de reset → resetear al admin.
- 📁 (crear) · ver `host-header-injection/`

### 3. SQL Injection
- [ ] Puntos: login, filtros, cookies, headers. `'`, `''`, `OR 1=1`.
- [ ] UNION → extraer credenciales admin. Blind → condicional/time-based.
- [ ] Bypass filtros/WAF con ofuscación.
- 📁 `sql-injection/` · ofuscación en `obfuscacion/`

### 4. JWT
- [ ] `alg:none`, firma no verificada, `kid` inyectable, clave débil (crackear HS256).
- [ ] Confusión de algoritmo (RS256→HS256 con pub key), `jwk`/`jku` embebido.
- [ ] Cambiar `sub`/`role` a admin.
- 📁 `jwt-attacks/`

### 5. Prototype Pollution (client-side)
- [ ] Buscar *gadget*: `__proto__` en query/JSON/params → propiedad que afecte lógica.
- [ ] DOM Invader (Burp) para detectar source→sink.
- 📁 `prototype-pollution/`

### 6. API Testing
- [ ] Métodos alternos (`PUT`/`DELETE`/`PATCH`), `Content-Type` swaps.
- [ ] Mass assignment: añadir `"isAdmin":true`, `"role":"admin"` al JSON.
- [ ] Documentación/endpoints ocultos de la API.
- 📁 (crear `api-testing/`)

### 7. Access Control (IDOR / broken)
- [ ] Cambiar `id`, `user`, GUID en URL/params/cookies → recurso ajeno.
- [ ] Forzar rutas de admin (`/admin`) con user normal; header `X-Original-URL`, `X-Forwarded-For`.
- [ ] Parámetro de rol en registro/perfil.
- 📁 (crear `access-control/`)

### 8. GraphQL
- [ ] **InQL** → introspección; si off, probar sugerencias/aliasing.
- [ ] Consultas/mutaciones no autorizadas (leer users, cambiar rol/password).
- [ ] Brute force por batching (aliases) saltando rate limit.
- 📁 `graphql/`

### 9. CORS
- [ ] `Origin: evil.com` → ¿refleja `Access-Control-Allow-Origin` + `Allow-Credentials: true`?
- [ ] `Origin: null`, subdominios confiados → exfiltrar datos/token del admin.
- 📁 `cors/`

---

> [!success] Salida del Stage 2
> Sesión/credenciales de **administrador** → usar para el **Stage 3**.
