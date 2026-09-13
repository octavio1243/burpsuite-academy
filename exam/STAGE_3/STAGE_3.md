# STAGE 3 — DATA EXFILTRATION

> **Objetivo único:** leer **`/home/carlos/secret`** y pegarlo en *Submit solution*.
> Ya soy **administrador**. **No hay víctima que navegue**: el enemigo es el **servidor** (directo, RCE, o SSRF a `localhost:6566`).
> 🚩=`[!danger]` · 💡=`[!tip]` · ⚠️=`[!warning]`. El "qué probar" completo vive en `exam/to-do-list/<vuln>`.

## 🧰 Herramientas que tengo para atacar

- 👑 Ya soy **admin** → features "de servidor" que el user normal no ve.
- 🌐 **Collaborator / oastify** → confirmar callbacks ciegos (XXE, SSRF, OAST en command injection/SSTI).
- 🐚 **Web shells listos** en `vulnerabilities/017-file-upload-vulnerabilities/`.
- El objetivo **no visita** nada: yo disparo todo directo contra el server.

## 🎯 Qué busco (todo apunta a `/home/carlos/secret`)

1. **Lectura directa de fichero** (XXE `file://`, LFI/path traversal).
2. **RCE** → `cat /home/carlos/secret` (command injection, SSTI, deserialización, file upload).
3. **SSRF** → `http://localhost:6566/` (o `file://` + path traversal).

## 🚦 Arranque (siempre)

- [ ] Cazar features de servidor: **subida de archivos, import/export XML, plantillas, previews de URL, deserialización, formularios que rozan el SO**.
- [ ] **Burp Scan** → *Scan Insertion Points* sobre cada input server-side.
- [ ] **Collaborator** a mano para lo ciego.

---

## ✅ Vulnerabilidades (Stage 3) — por prioridad

| # | Vulnerabilidad | 🚩 Señal detonante | Qué probar |
|---|---|---|---|
| 1 | 📄 **XXE — XML entities & Injections** | 🚩 **Algo parsea XML** (stock check, SOAP, subida de **SVG/DOCX/XLSX**) | [[exam/to-do-list/xxe\|Qué probar]] (SVG avatar con `file:///home/carlos/secret` = el más jugoso) |
| 2 | 🛰️ **SSRF — Server Side Request Forgery** | 🚩 Fetch server-side, Host header injection, o **`localhost:6566` responde** | [[exam/to-do-list/ssrf\|Qué probar]] |
| 3 | 📐 **SSTI — Server Side Template Injection** | 🚩 Algo **editable que se renderiza** (preferred name / **descripción de producto**) → `7*7` | [[exam/to-do-list/ssti\|Qué probar]] |
| 4 | 🧪 **SSPP — Server-Side Prototype Pollution** | 🚩 JSON con **`__proto__`** cambia el comportamiento server-side | [[exam/to-do-list/prototype-pollution\|Qué probar]] (RCE vía `child_process`: `execArgv`/`fork` o `shell`+`input`/`execSync`) |
| 5 | 📁 **LFI — File Path Traversal** | 🚩 Recurso con parámetro tipo **`fileName`** que el user normal no carga | [[exam/to-do-list/path-traversal\|Qué probar]] |
| 6 | ⬆️ **File Uploads → RCE** ⭐ | 🚩 **Permite subir archivos** (típicamente solo el admin) | [[exam/to-do-list/file-upload\|Qué probar]] (shells listos → `cat /home/carlos/secret`) |
| 7 | 🧷 **Deserialization** | 🚩 Aparece un **objeto serializado** (PHP `O:` · Java `rO0` · pickle) | [[exam/to-do-list/insecure-deserialization\|Qué probar]] |
| 8 | 💻 **OS Command Injection** | 🚩 **Si el admin toca un parámetro, se prueba** (barato, premio = RCE) | [[exam/to-do-list/os-command-injection\|Qué probar]] |

### 🔻 Menos relevante en Stage 3

| Vulnerabilidad | 🚩 Señal detonante | Qué probar |
|---|---|---|
| 🗄️ **SQL Injection** | 🚩 El admin tiene un **search**/consulta a BD → apuntá a lectura de fichero o `localhost:6566` | [[exam/to-do-list/sql-injection\|Qué probar]] (`LOAD_FILE`/`pg_read_file`/`OPENROWSET`/Oracle-XXE + exfil OOB) |

---

> [!success] Salida del Stage 3
> Contenido de `/home/carlos/secret` → **Submit solution**. Examen aprobado. 🎉
