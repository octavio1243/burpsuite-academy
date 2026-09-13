---
aliases: [Scanners Stage 3, Escaneo Stage 3]
tags: [exam/scan, burp/scanner]
---

# 🛰️ Escaneo — Stage 3 (issues a activar)

> Config de escaneo de Burp para **[[exam/STAGE_3/STAGE_3|Stage 3 — Data Exfiltration]]**.
> **Idea:** ya sos admin y no hay víctima. Todo es **server-side**: RCE, lectura de fichero, XXE, SSRF. Apuntá el scan a cada input nuevo del panel admin.

## 🟢 Issues ON (sobre la superficie server-side del admin)

| Grupo | Issues ON |
|---|---|
| 💻 RCE / code injection | OS command injection · Server-side template injection · Expression Language injection · Server-side JavaScript code injection · PHP code injection · Python code injection · Ruby code injection · Perl code injection · Unidentified code injection · React Server Components RCE (React2Shell) · SSI injection |
| 🧷 Deserialización | Serialized object in HTTP message · ASP.NET ViewState without MAC enabled · ASP.NET debugging enabled · ASP.NET tracing enabled |
| 📄 XXE / XML | XML external entity injection · XML injection · XML entity expansion |
| 📁 File read / upload | File path traversal · File path manipulation · File upload functionality |
| 📡 SSRF / OOB (blind) | Out-of-band resource load (HTTP) · External service interaction (DNS · HTTP · SMTP) |
| 🗄️ Inyecciones de lectura de datos | SQL injection (+ second order + statement) · LDAP injection · XPath injection · SMTP header injection |
| 🔎 Ruta del secreto | Source code disclosure · Backup file · Directory listing |

> [!warning] ✋ Manual en S3 (confirmación/explotación a mano)
> SSRF chain a `localhost:6566` · SSPP → RCE (`child_process`) · File upload → webshell (shells listos en `vulnerabilities/017-file-upload-vulnerabilities/`) · Deserialization gadget chains · path traversal a `/home/carlos/secret` exacto · Collaborator para callbacks ciegos.

> 🚫 **Ruido OFF:** mismo bucket que [[exam/STAGE_1/STAGE_1-scanners#🚫 Ruido — OFF SIEMPRE (bucket completo del vault)|Stage 1]].

> [!tip] 🛠️ En Burp
> Guardá la config como **`BSCP-Stage-3`**. Aplicala con **Scan insertion points** sobre cada input server-side nuevo del admin.

---
> Volver a **[[exam/STAGE_3/STAGE_3|Stage 3 — Data Exfiltration]]** · Referencia: [[exam/all-scans|All Scans]]
