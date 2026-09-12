---
aliases:
  - Path Traversal
  - path-traversal-entrypoint
  - Directory Traversal
  - directory traversal
  - LFI
tags:
  - vuln/path-traversal
  - entrypoint
---

# Path Traversal (Directory Traversal) — Punto de entrada

> Documento **agnóstico al negocio**: *cómo **detectar y explotar** el traversal*.
> **Payload por lab + encodings** → [[vulnerabilities/010-path-transversal/labs/README|labs/README]].
> **Ofuscación / encodings** (saltar filtros) → [[vulnerabilities/019-obfuscacion/encodings|encodings.md]].

> [!abstract] La idea en una línea
> Un parámetro lleva un **nombre de archivo** que el server **abre del disco**. Si metés **`../`** (o su equivalente ofuscado), **salís del directorio previsto** y leés —o a veces **escribís**— cualquier archivo del sistema (código, credenciales, `/etc/passwd`).

## 📚 Referencias rápidas

- 🧪 **Labs** — 6 (1 Apprentice + 5 Practitioner), defensa · encoding · payload → [[vulnerabilities/010-path-transversal/labs/README|labs/README]]
- 🥷 **Encodings** (URL, doble URL, UTF-8 overlong, null byte…) → [[vulnerabilities/019-obfuscacion/encodings|encodings.md]] · [[vulnerabilities/019-obfuscacion/README|índice de ofuscación]]

## 🎯 Cómo surge

La app **concatena tu input dentro de una ruta** sin validar. Clásico: un cargador de imágenes.

```
<img src="/loadImage?filename=218.png">   →  abre  /var/www/images/218.png
```

Si controlás `filename`, con `../` **subís de directorio** hasta la raíz:

```
Linux:   /loadImage?filename=../../../etc/passwd        →  /etc/passwd
Windows: /loadImage?filename=..\..\..\windows\win.ini   →  C:\windows\win.ini
```

Tres `../` te llevan de `/var/www/images/` a `/`.

## 💥 Qué se logra (impacto)

- **Leer archivos arbitrarios** — lo típico: **código fuente**, **credenciales/config** (`.env`, `config.php`, claves), archivos del SO (`/etc/passwd`). El objetivo de los 6 labs es **leer `/etc/passwd`**.
- **Escribir archivos arbitrarios** — *en algunos casos* el mismo parámetro sirve para **escribir** → modificás datos/comportamiento de la app y podés escalar a **control total del server** (p. ej. pisar un archivo que luego se ejecuta). Menos común, pero es el techo del impacto.

## 🧪 Cómo detectarlo y explotarlo

1. **Encontrá el parámetro que abre un archivo** — `filename`, `file`, `path`, `document`, `folder`, `download`, `template`, `image`.
2. **Probá `../` directo** → `../../../etc/passwd`. ¿Vuelve el archivo? → traversal ✅.
3. **¿Te filtran?** Subí la escalera de bypass (cada uno rompe una defensa distinta) — todos con payload exacto en [[vulnerabilities/010-path-transversal/labs/README|labs/README]]:

| Defensa | Bypass |
| --- | --- |
| Bloquea `../` (path relativo a un dir) | **ruta absoluta** `/etc/passwd` |
| Strippea `../` **una vez** | **anidado** `....//` |
| Hace un **URL-decode de más** | **doble URL** `..%252f` |
| Mira el `/` o `.` literal | **URL** `..%2f` · **UTF-8 overlong** `..%c0%af` / `..%ef%bc%8f` |
| Valida el **inicio** del path | **prefijo** `/var/www/images/` + `../` |
| Valida la **extensión** | **null byte** `…/etc/passwd%00.png` |

> [!tip] Orden mental
> `../` directo → absoluto → anidado `....//` → URL / doble URL → UTF-8 overlong → sumá `%00.png` (extensión) y/o prefijo (start-of-path). **Son combinables.**

## 🛡️ Prevención

- **La mejor defensa:** **no pasar input del usuario a las APIs de archivos.** Si el set de archivos es fijo, usá un **ID → nombre real** en el server (mapa), nunca el nombre crudo.
- **Si es inevitable, dos capas:**
  1. Validá el input (**whitelist** / solo alfanumérico).
  2. **Canonicalizá** la ruta con la API del SO y verificá que **empiece por el directorio base** (después de resolver `../`):
     ```java
     File file = new File(BASE_DIRECTORY, userInput);
     if (file.getCanonicalPath().startsWith(BASE_DIRECTORY)) {
         // OK, procesar
     }
     ```
  > El bug del **lab 5** es justamente **validar el prefijo sin canonicalizar primero**.

---

> [!tip] Reglas mentales
> - **Objetivo = leer un archivo** (código, credenciales, `/etc/passwd`); en algunos casos **escribir** → RCE.
> - **La discrepancia es sobre el `/` y el `..`:** el filtro mira el literal, el filesystem resuelve la versión decodificada.
> - **Escalera de bypass:** directo → absoluto → anidado → URL/doble URL → overlong → null byte / prefijo.

> [!note] Relación con otras vulns
> - **LFI / RFI** — el traversal es el primitivo de la *Local File Inclusion*; si además el archivo se **incluye/ejecuta**, escalás a RCE.
> - **File upload** — si podés **escribir** vía traversal (o subir con un path controlado), pisás un archivo servido/ejecutado → carpeta `vulnerabilities/017-file-upload-vulnerabilities/`.
> - **SSTI / command injection** — otras rutas de lectura del secreto en Stage 3; ver [[exam/STAGE_3/STAGE_3|STAGE_3]].
