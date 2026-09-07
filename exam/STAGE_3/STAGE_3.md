# STAGE 3 — DATA EXFILTRATION

> **Objetivo:** leer el fichero **`/home/carlos/secret`** y enviarlo en *Submit solution*.
> Solo pueden aparecer las vulns de esta lista. Metodología = qué probar, en orden.

## 🎯 El objetivo siempre es el mismo

Leer **`/home/carlos/secret`**. Toda técnica de abajo se orienta a eso
(o a leerlo vía RCE / SSRF a `localhost:6566` / lectura de fichero).

## 🚦 Arranque

- [ ] Ya como admin (Stage 2) → buscar features "de servidor": subida de archivos, import/export XML, plantillas, previews de URL, deserialización, funciones que llaman al SO.
- [ ] Burp Scan → *Scan Insertion Points*.

---

## ✅ Checklist de vulnerabilidades (Stage 3)

### 1. XXE
- [ ] Endpoint que parsea XML → inyectar entidad externa `file:///home/carlos/secret`.
- [ ] Si no refleja → **XXE ciego** vía OAST (Collaborator) o *error-based*.
- [ ] Vía `SVG`/`.docx`/`Content-Type: application/xml`.
- 📁 `xxe/`

### 2. SSRF
- [ ] Parámetro que hace fetch server-side → apuntar a `http://localhost:6566/` e interno.
- [ ] `file:///home/carlos/secret`, metadata cloud, bypass de filtros (IP encoding, redirect).
- 📁 `ssrf/`

### 3. SSTI
- [ ] Fuzz `${{7*7}}`, `{{7*7}}`, `<%= 7*7 %>` → detectar motor por la respuesta.
- [ ] Payload de **RCE** del motor → `cat /home/carlos/secret`.
- 📁 `server-side-template-injection/`

### 4. SSPP (Server-Side Prototype Pollution)
- [ ] JSON con `__proto__` → detectar cambio de comportamiento server-side.
- [ ] Escalar a RCE (gadget en el runtime, p.ej. `child_process`).
- 📁 `prototype-pollution/`

### 5. LFI / Path Traversal
- [ ] `../../../../home/carlos/secret` en parámetros de fichero.
- [ ] Bypass: `....//`, encoding (`%2e`, doble), null byte, prefijo/sufijo forzado.
- 📁 `path-transversal/` · ofuscación en `obfuscacion/`

### 6. File Upload → RCE  ⭐ (secret a mano)
- [ ] Subir **web shell** PHP y pedirlo por GET.
- [ ] Leer el secreto directo:
  - `example_best.php?command=cat%20/home/carlos/secret` (system, salida limpia)
  - `exploit.php` (file_get_contents, sin parámetro)
- [ ] Bypass extensión/Content-Type/magic bytes/polyglot si filtran.
- 📁 **`file-upload-vulnerabilities/`** → shells listos + cheat-sheet de invocación.

### 7. Deserialization
- [ ] Detectar objeto serializado (PHP `O:`, Java `rO0`, .NET, Python pickle) en cookies/params.
- [ ] Gadget chain (ysoserial / phpggc) → RCE → leer el secreto.
- 📁 `insecure_deserialization/`

### 8. OS Command Injection
- [ ] Inyectar `;`, `|`, `&&`, `$(...)`, backticks en params que rozan el SO.
- [ ] Ciego → time delay (`sleep 10`) o exfil por OAST/DNS.
- [ ] `; cat /home/carlos/secret` (o exfil a Collaborator).
- 📁 (crear `os-command-injection/`)

---

> [!success] Salida del Stage 3
> Contenido de `/home/carlos/secret` → **Submit solution**. Examen aprobado. 🎉
