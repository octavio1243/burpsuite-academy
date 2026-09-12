---
aliases:
  - to-do Clickjacking
tags:
  - exam/to-do
  - vuln/clickjacking
---

# Clickjacking — Qué probar

> Técnica → [[vulnerabilities/004-clickjacking/clickjacking|entry point]] · labs → [[vulnerabilities/004-clickjacking/labs/README|labs]]

## 🚩 Flags

> [!danger] 🚩 ¿Está? (las 3 juntas)
> 1. **Acción relevante y clickeable** del admin (cambiar email, borrar/aprobar, submit que dispara XSS).
> 2. **La página se deja enmarcar** → faltan `X-Frame-Options` **y** CSP `frame-ancestors`.
> 3. Hay **víctima admin** que hace clic → confirmá en el **Access log** (IP distinta). Sirve **aunque haya token CSRF**.

> [!warning] ⚠️ Casi siempre Stage 2
> En Stage 1 (sin víctima logueada) no aplica → su lugar es contra el **admin**.

## 🎯 Objetivo (Stage 2)
- Clic ciego del admin sobre un botón con estado → cambiar su email → reset → tu bandeja.

## ♾️ Independiente del stage
- [ ] Iframe del target casi transparente (`opacity` baja) + `<div>` señuelo sobre el botón (alineá con `0.1`, entregá con `~0.0001`).
- [ ] **Prellená** inputs por query params; si hay **frame buster** → `sandbox="allow-forms"`.
- [ ] **¿No sabés la resolución del admin?** beacon `<img>` con `screen`/`innerWidth`/`dpr` al Collaborator → recalculá `top`/`left` → [[vulnerabilities/004-clickjacking/clickjacking#6) Beacon de resolución/layout (para alinear a ciegas)|PoC beacon]].
- [ ] Señuelos típicos: `Delete account`(+`Yes` multistep) · `Update email` · `Submit feedback` (si dispara DOM XSS). El label real lo ves **registrando tu cuenta**.

## 🔗 Referencias
- [[vulnerabilities/004-clickjacking/clickjacking|entry point]] · [[vulnerabilities/004-clickjacking/labs/README|labs]]
