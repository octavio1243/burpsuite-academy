# STAGE 3 — DATA EXFILTRATION

> **Objetivo único:** leer el fichero **`/home/carlos/secret`** y pegarlo en *Submit solution*.
> Ya soy **administrador** (Stage 2). Ahora **no hay víctima que navegue**: el enemigo es el **servidor**.
> Cada vulnerabilidad es *un camino distinto* para lo mismo: **leer ese fichero** (directo, por RCE, o por SSRF a `localhost:6566`).

## 🧰 Herramientas que tengo para atacar

- 👑 Ya soy **admin** → tengo acceso a features "de servidor" que el user normal no ve.
- 🌐 **Collaborator / oastify** → confirmar callbacks ciegos (XXE ciego, SSRF, OAST en command injection/SSTI).
- 🐚 **Web shells listos** en `file-upload-vulnerabilities/` → subir y pedir por GET.
- El objetivo **no visita** nada: yo disparo todo directo contra el server.

## 🎯 Qué busco (todo apunta a `/home/carlos/secret`)

1. **Lectura directa de fichero** (XXE `file://`, LFI/path traversal, `file_get_contents`).
2. **RCE** → `cat /home/carlos/secret` (command injection, SSTI, deserialización, file upload).
3. **SSRF** → `http://localhost:6566/` (o `file://` + path traversal hasta el fichero).

## 🚦 Arranque (siempre)

- [ ] Ya como admin → cazar features de servidor: **subida de archivos, import/export XML, plantillas, previews de URL, deserialización, formularios que rozan el SO**.
- [ ] **Burp Scan** → *Scan Insertion Points* sobre cada input server-side.
- [ ] Tener el **Collaborator** a mano para lo ciego.

---

## ✅ Vulnerabilidades (Stage 3)

### SQL Injection (SQLi)
> [!danger] 🚩 ¿Está o no está?
> ¿El admin tiene acceso a **algo que permita hacer un search** (o cualquier consulta a BD)?

> *(idea propia: no es obvio leer un fichero con SQL)* → sí se puede en algunos motores.
- [ ] **MySQL**: `LOAD_FILE('/home/carlos/secret')` (requiere `secure_file_priv` permisivo).
- [ ] **PostgreSQL**: `COPY (...) TO/FROM`, `pg_read_file('/home/carlos/secret')`.
- [ ] **Stacked queries** → si el motor permite `;`, encadenar lectura/escritura.
- [ ] Si no hay lectura de fichero → **UNION/blind** para sacar datos que abran otra vía.
- 📁 `sql-injection/` · ofuscación en `obfuscacion/`

### XML External Entity (XXE)
> [!danger] 🚩 ¿Está o no está?
> **Se envía un XML**, o hay un **servicio SOAP** detrás, o carga de imágenes **SVG / DOCX**.

> **Hay que intentar leer el fichero sí o sí.**
- [ ] Entidad externa → `file:///home/carlos/secret` reflejada en la respuesta.
- [ ] Si no refleja → **XXE ciego** vía OAST (Collaborator) o *error-based*.
- [ ] Vía `SVG` / `.docx` / `Content-Type: application/xml`.
- [ ] *(escalada)* Usar el XXE como **SSRF** → con **path traversal** llegar al fichero.
- 📁 `xxe/`

### Server-Side Request Forgery (SSRF)
> [!danger] 🚩 ¿Está o no está?
> Un **Host header injection** deja pegarle a un **oastify**, o **`localhost:6566` responde**.

- [ ] Parámetro que hace fetch server-side → `http://localhost:6566/` e interno.
- [ ] `file:///home/carlos/secret` si el fetcher acepta esquemas.
- [ ] *(idea propia)* **Path traversal** en la URL interna hasta caer en el fichero.
- [ ] Bypass de filtros: IP encoding, redirect, `@`, `#`, DNS rebinding.
- 📁 `ssrf/`

### OS Command Injection (OSCi)
> [!danger] 🚩 ¿Está o no está?
> Un **formulario al que accede el admin** que roza el SO → **probar con oastify todas las variantes para escapar el comando**.

- [ ] Inyectar `;`, `|`, `&&`, `$(...)`, backticks, `%0a` en cada parámetro.
- [ ] **Ciego** → confirmar con OAST/DNS a Collaborator, o time delay (`sleep 10`).
- [ ] `; cat /home/carlos/secret` (o exfil del contenido a Collaborator si es ciego).
- 📁 *(crear `os-command-injection/`)*

### Server-Side Template Injection (SSTI)
> [!danger] 🚩 ¿Está o no está?
> Hay una **plantilla editable** (cambiar nombre, mensajes, etc.) que luego **se inserta/renderiza** → confirmar con **oastify**.

- [ ] Fuzz `${{7*7}}`, `{{7*7}}`, `<%= 7*7 %>` → detectar motor por la respuesta.
- [ ] Confirmar por OAST si es ciego (callback desde el render).
- [ ] Payload de **RCE** del motor → `cat /home/carlos/secret`.
- 📁 `server-side-template-injection/`

### Directory Traversal / LFI (Path Traversal)
> [!danger] 🚩 ¿Está o no está?
> Hay un **recurso que el usuario normal no carga**, servido con un parámetro tipo **`fileName`** (o similar).

- [ ] `../../../../home/carlos/secret` en el parámetro de fichero.
- [ ] Bypass: `....//`, encoding (`%2e`, doble `%252e`), null byte, prefijo/sufijo forzado.
- 📁 `path-transversal/` · ofuscación en `obfuscacion/`

### Insecure Deserialization (Deser)
> [!danger] 🚩 ¿Está o no está?
> **Aparece una cookie nueva** (u objeto serializado en params): PHP `O:`, Java `rO0`, .NET, Python pickle.

- [ ] Identificar el formato del objeto serializado.
- [ ] **Probar variantes de ysoserial** (Java) / **phpggc** (PHP) → gadget chain → RCE.
- [ ] RCE → `cat /home/carlos/secret`.
- 📁 `insecure_deserialization/`

### File Upload → RCE  ⭐ (el secreto a mano)
> [!danger] 🚩 ¿Está o no está?
> **Permite subir archivos** (típicamente solo al **administrador**) → avatar, adjunto, import.

- [ ] Subir **web shell** PHP y pedirlo por GET desde `/files/avatars/…`.
- [ ] Leer el secreto directo (shells ya listos en la carpeta):
  - `example_best.php?command=cat%20/home/carlos/secret` (system, salida limpia)
  - `exploit.php` (file_get_contents, **sin parámetro**)
- [ ] Bypass extensión / `Content-Type` / magic bytes / polyglot si filtran.
- 📁 **`file-upload-vulnerabilities/`** → shells listos + cheat-sheet de invocación.

---

## 🔎 Extras que ya teníamos (útiles en Stage 3)

### Server-Side Prototype Pollution (SSPP)
- [ ] JSON con `__proto__` → detectar cambio de comportamiento server-side.
- [ ] Escalar a RCE (gadget en el runtime, p.ej. `child_process`) → leer el secreto.
- 📁 `prototype-pollution/`

---

> [!success] Salida del Stage 3
> Contenido de `/home/carlos/secret` → **Submit solution**. Examen aprobado. 🎉

> [!todo] Pendiente de completar
> Crear `os-command-injection/`. Afinar payloads "a mano" por motor (SSTI, XXE file-read, LFI).
