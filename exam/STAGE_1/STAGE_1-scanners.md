---
aliases: [Scanners Stage 1, Escaneo Stage 1]
tags: [exam/scan, burp/scanner]
---

# 🛰️ Escaneo — Stage 1 (issues a activar)

> Config de escaneo de Burp para **[[exam/STAGE_1/STAGE_1|Stage 1 — Foothold]]**.
> **Idea:** dejá ON **solo** lo que el scanner realmente cacha y sirve al foothold. Lo demás (lógica, CSRF, IDOR, JWT…) es **manual** — tenerlo ON no ayuda. En S1 corré esto *full domain* una vez.

## 🟢 Pasivos (recon — activar una vez sobre todo el dominio, no se repiten)

| Grupo | Issues ON |
|---|---|
| 📂 Divulgación | Source code disclosure · Backup file · Directory listing · Robots.txt file · Private IP addresses disclosed · Database connection string disclosed · Private key disclosed · Json Web Key Set disclosed · JWT private key disclosed · Email addresses disclosed |
| 🔑 Creds en tránsito | Cleartext submission of password · Password submitted using GET method · Password returned in later response · Password returned in URL query string · Password value set in cookie · Session token in URL |
| 🕸️ Recon de API | OpenAPI definition found (active + passive) · GraphQL endpoint found/discovered · GraphQL introspection enabled · GraphQL suggestions enabled · GraphQL content type not validated |
| 🧪 Pistas de inyección | Input returned in response (reflected + stored) · Suspicious input transformation (reflected + stored) · Base64-encoded data in parameter |
| 🚧 Señales de bypass | Spoofable client IP address · User agent-dependent response · Referer-dependent response · Request URL override |

## 🔴 Activos (client-side entregado + smuggling + cache — hay víctima logueada)

| Grupo | Issues ON |
|---|---|
| 🧬 XSS | Cross-site scripting (reflected · stored · reflected DOM-based · stored DOM-based · DOM-based) |
| 🌳 DOM family | DOM data manipulation (3) · JavaScript injection (3) · Open redirection DOM (3) · Link manipulation DOM (2) · Cookie manipulation DOM (3) · HTML5 web message manipulation (3) · HTML5 storage manipulation (3) · WebSocket URL poisoning (3) · Document domain manipulation (3) · Ajax request header manipulation (3) · Local file path manipulation (3) · Client-side JSON injection (3) · Client-side XPath injection (3) · Client-side HTTP parameter pollution (2) · Client-side template injection · Client-side prototype pollution · Client-side desync |
| 🌐 Cache | Web cache poisoning · Web cache deception |
| 📦 Smuggling / splitting | HTTP request smuggling · HTTP response header injection |
| 🔗 Chains host-header/redirect | Open redirection (stored + reflected) · Link manipulation (stored + reflected) · Form action hijacking (stored + reflected) · CSS injection (stored + reflected) |
| 📡 OOB (host header / smuggling ciego) | Out-of-band resource load (HTTP) · External service interaction (DNS · HTTP · SMTP) |
| 🗄️ SQLi (barato, run-once) | SQL injection · SQL injection (second order) · SQL statement in request parameter |

> [!warning] ✋ Manual en S1 (el scanner NO los caza — no esperes que salten solos)
> Authentication (login/reset logic, rate-limit) · GraphQL brute-force con alias · Access Control (IDOR) · CORS · JWT · OAuth · Host Header (reset poisoning) explotación.
> CORS y JWT tienen checks pasivos útiles y quedan ON igual, pero la **explotación** es a mano.

## 🚫 Ruido — OFF SIEMPRE (bucket completo del vault)

> Destildá todo esto en *Issues reported*: nunca gana una flag BSCP y solo alarga el escaneo. **Este es el bucket de referencia** que S2 y S3 reutilizan.

TLS certificate · TLS cookie without secure flag set · Unencrypted communications · Strict transport security not enforced · Mixed content · Cacheable HTTPS response · Silverlight cross-domain policy · Flash cross-domain policy · Multiple content types specified · Content type is not specified · Content type incorrectly stated · HTML uses unrecognized charset · HTML does not specify charset · Long redirection response · Cookie without HttpOnly flag set · Cookie scoped to parent domain · Duplicate cookies set · Path-relative style sheet import · Frameable response (potential Clickjacking) · Content security policy: not enforced / malformed syntax / allows untrusted style execution / allows untrusted script execution / allows form hijacking / allows clickjacking / allowlisted script resources · Social security numbers disclosed · Credit card numbers disclosed · Hidden HTTP 2 · Cross-domain script include · Cross-domain Referer leakage · Cross-domain POST.

> [!tip] 🛠️ Cómo dejarlo listo en Burp (una vez, reutilizable)
> 1. **Settings → Scan configurations → New** (Scan configuration library).
> 2. En **Issues reported**: destildá todo → tildá solo las listas ON de arriba.
> 3. Guardá como **`BSCP-Stage-1`** en la library.
> 4. Aplicalo en un escaneo **full domain**.
> 5. Optimización: *Fastest* / *Minimize false negatives* según tiempo.

---
> Volver a **[[exam/STAGE_1/STAGE_1|Stage 1 — Foothold]]** · Referencia: [[exam/all-scans|All Scans]]
