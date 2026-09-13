---
aliases:
  - Information disclosure
  - info-disclosure-entrypoint
tags:
  - vuln/information-disclosure
  - entrypoint
---

# Information disclosure — Punto de entrada

> Documento **agnóstico**: *dónde busca uno la info filtrada y con qué*. Es **recon**: la app **regala** datos (versiones, secrets, código, credenciales) que te dan el próximo paso. Los labs con objetivo y solución → [[vulnerabilities/014-information-disclousure/labs/README|labs de Information disclosure]].

## 📍 Dónde suele filtrar (fuentes)

### Archivos para crawlers
- `robots.txt`
- `sitemap.xml`

### Directory listings
- Directorios que listan su contenido (sin `index`) → exponen archivos que no deberías ver.

### Comentarios de desarrolladores
- **in-line** en el HTML
- en el **código JS**

### Mensajes de error
- **Errores verbosos** (stack traces) → revelan las tecnologías del sitio:
    - nombre del **template engine**
    - tipo de **base de datos**
    - **servidor y su versión**

### Datos de debug
- variables de **sesión** clave
- **hostnames y credenciales**
- nombres de **archivos y directorios** en el server
- **claves** usadas para cifrar datos que se transmiten por el cliente

### Páginas de cuenta de usuario
```
GET /user/personal-info?user=<USER_NAME>
```
> IDOR/enumeración: cambiás el `user` y ves datos de otros.

### Source code disclosure via backup files
- archivos que terminan en `~` (y `.bak`, `.old`, `.txt`, `.zip`…)
- > ⚠️ Defensa: **no hardcodear** variables/credenciales en el código fuente.

### Configuración insegura
- **HTTP TRACE** no deshabilitado (refleja headers internos)
- `/cgi-bin/phpinfo.php` (y otras páginas de debug)

### Historial de control de versiones
- `/.git` expuesto → se reconstruye todo el código e historial.

## 🧰 Técnicas y herramientas (high-level)

- **Fuzzing con Intruder** — comparás **tiempos de respuesta, longitudes, status code** y **grep matching** para detectar respuestas anómalas.
    - **Logger++** (extensión de Burp) para revisar/filtrar todo el tráfico.
- **Burp Scanner** — descubre **private keys, emails, números de tarjeta** en respuestas, **archivos de backup**, **directory listings**, etc.
- **Engagement tools de Burp** — sobre una request: **Search**, **Find comments**, **Discover content**.
- **Qué mirar concretamente:**
    - respuestas "informativas" → leer **`robots.txt`**
    - **backups temporales** con el código fuente
    - menciones de **tablas o columnas** de la base de datos
    - **API keys, IPs, credenciales de DB**, etc. **en el código**

> [!note] Ver también
> - **Wordlist del examen** (Intruder/Discover content, 279 rutas de labs BSCP) → [[vulnerabilities/014-information-disclousure/burp-labs-wordlist|burp-labs-wordlist]].
> - **Labs** (5, con objetivo y solución paso a paso) → [[vulnerabilities/014-information-disclousure/labs/README|labs de Information disclosure]].
> - **`.git` descargado + `read.py`** (lab de version control) → `vulnerabilities/014-information-disclousure/Leer .git/`.
> - **Access control** (headers internos / bypass de `/admin`) → [[vulnerabilities/028-access-control/access-control|access control]].
> - **Authentication** (credenciales filtradas → toma de cuenta) → [[vulnerabilities/029-authentication/authentication|authentication]].
