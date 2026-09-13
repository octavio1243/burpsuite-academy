---
aliases: [Scanners Stage 2, Escaneo Stage 2]
tags: [exam/scan, burp/scanner]
---

# 🛰️ Escaneo — Stage 2 (issues a activar)

> Config de escaneo de Burp para **[[exam/STAGE_2/STAGE_2|Stage 2 — Privilege Escalation]]**.
> **Idea:** en S2 casi todo lo que escala es **manual** (CSRF, IDOR, JWT, mass assignment, business logic). El scanner solo suma CORS, SSRF (detección) y re-chequeo de inyecciones/XSS sobre superficie **nueva** del admin.

## 🟢 Issues ON (re-escanear solo endpoints nuevos, no full-domain)

| Grupo                                   | Issues ON                                                                                                                         |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| 🔀 CORS (robo de datos admin)           | Cross-origin resource sharing · CORS: arbitrary origin trusted · CORS: all subdomains trusted · CORS: unencrypted origin trusted  |
| 🧬 XSS/DOM nuevos                       | Todas las variantes de Cross-site scripting + DOM family (mismas que S1) — **solo sobre `.js`/endpoints nuevos del admin**        |
| 🗄️ SQLi (superficie autenticada nueva) | SQL injection · SQL injection (second order) · SQL statement in request parameter                                                 |
| 🛰️ SSRF (detección)                    | Out-of-band resource load (HTTP) · External service interaction (DNS · HTTP · SMTP) · Open redirection (reflected + stored + DOM) |
| 📦 Cache/smuggling contra admin         | Web cache poisoning · Web cache deception · HTTP request smuggling · Client-side desync · HTTP response header injection          |
| 🧪 Client-side escalada                 | Client-side prototype pollution · Client-side template injection                                                                  |
| 🎣 CSRF/forms                           | Cross-site request forgery · Form action hijacking (reflected + stored)                                                           |

> [!warning] ✋ Manual en S2 (el grueso de la escalada — no lo caza el scanner)
> CSRF account-takeover (PoC) · Auth/password reset (username manipulable) · SSRF explotación (chain open-redirect → `localhost:6566/admin`) · JWT (`sub`/`role`) · API/Mass Assignment (`isAdmin`) · Access Control (IDOR) · GraphQL · Business Logic · Host Header (auth bypass `localhost`) · OAuth · Deserialization · SSPP · Info Disclosure TRACE (`X-Custom-IP-Authorization`).

> 🚫 **Ruido OFF:** mismo bucket que [[exam/STAGE_1/STAGE_1-scanners#🚫 Ruido — OFF SIEMPRE (bucket completo del vault)|Stage 1]].

> [!tip] 🛠️ En Burp
> Guardá la config como **`BSCP-Stage-2`**. Aplicala con **Scan insertion points** sobre requests nuevos (Repeater → Scan), **no** un full-domain de nuevo.

---
> Volver a **[[exam/STAGE_2/STAGE_2|Stage 2 — Privilege Escalation]]** · Referencia: [[exam/all-scans|All Scans]]
