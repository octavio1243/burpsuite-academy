---
aliases:
  - to-do CSRF
tags:
  - exam/to-do
  - vuln/csrf
---

# CSRF — Qué probar

> Técnica → [[vulnerabilities/003-csrf/csrf|entry point]] · labs → [[vulnerabilities/003-csrf/labs/README|labs]]

## 🚩 Flags

> [!danger] 🚩 ¿Está?
> Existe una **acción relevante autenticada que forjar** (cambiar email/password del admin…). Sin token = fácil; con token casi siempre hay bypass.

> [!warning] ⚠️ Casi siempre es Stage 2 (no Stage 1)
> El CSRF **no te loguea**: actúa dentro de una sesión ya logueada → sirve **contra el admin** (Stage 2). En Stage 1 (sin cuenta) saltalo salvo que puedas registrar tu cuenta y haya víctima logueada.

> [!tip] ✅ Confirmá que hay víctima (Access log)
> Entregá algo trivial por el exploit server → si aparece **IP distinta** en el Access log, el CSRF *delivered* al admin es viable. Solo tu IP → el admin solo ve contenido in-app (⇒ stored XSS) o el camino es auto-escalada.

## 🎯 Objetivo (Stage 2)
- Forjar una acción del admin → **cambiarle el email** → reset de password por correo → login como admin.

## ♾️ Independiente del stage

**Acciones a probar:** cambiar email · cambiar contraseña (sobre todo si NO pide la actual) · flujo de reset · cualquier acción con estado.
- [ ] PoC con Burp → *Generate CSRF PoC* → entregar por exploit server.
- [ ] **Si hay token:** ¿solo en POST? ¿solo si está presente? ¿no atado a la sesión? ¿atado a cookie seteable? ¿duplicado en cookie+body? → [[vulnerabilities/003-csrf/csrf#🔎 Puntos flojos a verificar (bypass de token)|puntos flojos]].
- [ ] **SameSite** (enruta, no descarta): `None`/ausente → todo; `Lax` → GET top-level + `_method=POST`; `Strict` → redirect client-side / subdominio hermano.
- [ ] **API JSON:** probá pasar el body a `x-www-form-urlencoded`/`text/plain` (no dispara preflight).
- [ ] **Token bien atado y sin bypass** → buscá **XSS** que lo lea, o **dangling markup** para exfiltrarlo.

## 🔗 Referencias
- [[vulnerabilities/003-csrf/csrf|entry point]] · [[vulnerabilities/003-csrf/labs/README|labs]] · XSS→CSRF → [[vulnerabilities/002-xss/README#🎯 Qué hacer con un XSS (objetivos de explotación)|XSS]]
