---
aliases:
  - Information disclosure labs
  - info-disclosure-labs
tags:
  - vuln/information-disclosure
  - labs
  - portswigger
---

# Information disclosure — Labs de PortSwigger

Labs de la categoría **[Information disclosure](https://portswigger.net/web-security/information-disclosure)**: **3 Apprentice + 2 Practitioner** (5 en total). **El hilo común:** la app **filtra información sensible** que no debería — versiones de frameworks, secret keys, código fuente, credenciales, o comportamiento interno — a través de **mensajes de error, páginas de debug, archivos olvidados (backups, `.git`, `robots.txt`), comentarios HTML o métodos HTTP** (TRACE). No es un exploit "activo": es **recon** que te entrega la pieza para el próximo paso (una credencial, un endpoint oculto, un header mágico). Lo que cambia lab a lab: **por dónde filtra** y **qué te da** esa fuga.

> [!note] Tres "sabores" de information disclosure
> - **Errores / debug verboso:** provocás un error o encontrás una página de debug → filtra **versión de framework** o **secret key**. Labs 1, 2.
> - **Archivos que quedaron:** `robots.txt`, `/backup`, `.bak`, `/.git` → **código fuente** y **credenciales** hardcodeadas. Labs 3, 5.
> - **Comportamiento / headers filtrados:** un método como **TRACE** revela un **header de auth interno** → lo reusás para bypass. Lab 4.

> **Herramientas:** Burp → **Engagement tools → Find comments** y **Discover content** (content discovery), `robots.txt`/`sitemap.xml` a mano, y para `.git`: descargarlo (`wget -r .../.git`) y leer `git log -p`. **Cómo leer las columnas:** **Dónde filtra** = la fuente de la fuga · **Técnica · qué necesitás** = cómo la sacás · **Objetivo** = qué conseguís. Pasos → [Solución por lab](#solución-por-lab).

## Apprentice

| #   | Laboratorio                                                                                                                                    | Dónde filtra                                                        | Técnica · qué necesitás                                                                                                                               | Objetivo                                                                 |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| 1   | [Information disclosure in error messages](https://portswigger.net/web-security/information-disclosure/exploiting/lab-infoleak-in-error-messages) | **Stack trace:** error verboso en producción.                      | **Romper un parámetro:** cambiás `productId` de entero a **string** → excepción con stack trace que revela **Apache Struts 2 2.3.31**. Solo Burp.    | Enviar la **versión del framework** que aparece en el error.             |
| 2   | [Information disclosure on debug page](https://portswigger.net/web-security/information-disclosure/exploiting/lab-infoleak-on-debug-page)          | **Página de debug** referenciada en un comentario HTML.            | **Find comments:** un comentario apunta a `/cgi-bin/phpinfo.php`; lo abrís en Repeater y buscás el **`SECRET_KEY`** en el volcado. Solo Burp.        | Enviar el **`SECRET_KEY`** expuesto en el debug.                         |
| 3   | [Source code disclosure via backup files](https://portswigger.net/web-security/information-disclosure/exploiting/lab-infoleak-via-backup-files)    | **Backup de código:** `.bak` en un dir listado en `robots.txt`.    | **robots.txt → /backup:** encontrás `/backup/ProductTemplate.java.bak`, lo leés y sacás la **contraseña de la DB** hardcodeada. Solo Burp.           | Enviar la **password de la DB** del código filtrado.                     |

## Practitioner

| # | Laboratorio | Dónde filtra | Técnica · qué necesitás | Objetivo |
| --- | --- | --- | --- | --- |
| 4 | [Authentication bypass via information disclosure](https://portswigger.net/web-security/information-disclosure/exploiting/lab-infoleak-authentication-bypass) | **Método TRACE:** refleja un **header de auth interno**. | **TRACE → header:** hacés `TRACE /admin` y la respuesta revela `X-Custom-IP-Authorization` (tu IP). Con **Match & Replace** lo agregás con `127.0.0.1` a todas las requests → te trata como interno. | Entrar a `/admin` con `X-Custom-IP-Authorization: 127.0.0.1` → **borrar a `carlos`**. |
| 5 | [Information disclosure in version control history](https://portswigger.net/web-security/information-disclosure/exploiting/lab-infoleak-in-version-control-history) | **`/.git` expuesto:** historial de commits. | **Descargar el `.git` y leer el historial:** `wget -r .../.git`, después `git log -p` → el commit *"Remove admin password from config"* deja la **password del admin** visible en el diff de `admin.conf`. | Sacar la password del **admin** del historial → login → **borrar a `carlos`**. |

---

## Solución por lab

**L1 — Error messages (romper el tipo del parámetro):**
1. En un producto, cambiá `GET /product?productId=1` → `productId=example` (string donde espera int).
2. La respuesta trae un **stack trace** con `Apache Struts 2 2.3.31` → esa versión es la solución.

**L2 — Debug page (`phpinfo`):**
1. Burp → **Engagement tools → Find comments** (o revisá el HTML): hay un comentario a `/cgi-bin/phpinfo.php`.
2. Abrí `/cgi-bin/phpinfo.php` en Repeater, buscá `SECRET_KEY` → envialo.

**L3 — Backup files (`robots.txt` → `.bak`):**
1. Leé `/robots.txt` → menciona `/backup`.
2. `GET /backup/ProductTemplate.java.bak` → dentro está la **password de la DB** hardcodeada → envialo.

**L4 — Auth bypass por TRACE (header interno):**
1. `TRACE /admin HTTP/1.1` → la respuesta refleja `X-Custom-IP-Authorization: <tu-ip>` (así decide "interno").
2. Burp → **Proxy → Match and replace**: agregá header `X-Custom-IP-Authorization: 127.0.0.1` a todas las requests.
3. Ahora `/admin` te deja → `/admin/delete?username=carlos`.

**L5 — Version control history (`/.git`):**
1. Descargá el repo expuesto: `wget -r https://LAB-ID.web-security-academy.net/.git` (o levantá los objetos a mano).
2. `git log --oneline` → buscá el commit *"Remove admin password from config"*; `git show <commit>` (o `git log -p admin.conf`) muestra el diff con la **password del admin**.
3. Login como `administrator` → `/admin` → borrar `carlos`.
   > Objetos `.git` + `read.py` de ejemplo → `vulnerabilities/014-information-disclousure/Leer .git/`.

---

## Atajos mentales / patrones

- **Info disclosure = recon que rinde.** No buscás romper nada: buscás lo que la app **regala**. Siempre mirá: `robots.txt`, `sitemap.xml`, **comentarios HTML/JS**, `/.git`, `.bak`/`~`/`.old`, `/backup`, páginas de debug (`phpinfo`, `/debug`, `/status`, `/actuator`).
- **Provocá errores a propósito:** tipos inválidos (string donde va int), parámetros faltantes, métodos raros (`TRACE`, `OPTIONS`), `Accept`/`Content-Type` inesperados → los **stack traces** filtran versiones y rutas internas.
- **Content discovery:** Burp **Discover content**, o fuzz de directorios/extensiones (`.bak`, `.txt`, `.old`, `.zip`, `.java`) sobre nombres de archivos que ya ves.
- **`.git` expuesto = jackpot:** `git log -p` reconstruye **todo** el código y las credenciales que alguna vez estuvieron ahí (aunque "las borren" en un commit posterior, quedan en el diff).
- **Headers/métodos que revelan lógica interna:** `TRACE` (refleja lo que llega), respuestas con `X-Powered-By`, `Server`, `X-Custom-*` → a veces te dan el **header exacto** para un bypass (L4).
- **Objetivos típicos:** conseguir una **credencial** (DB/admin), una **secret key**, una **versión** vulnerable, o un **header** que te habilite `/admin` → después borrás `carlos`.

> [!note] Ver también
> - **Access control** (el header interno / bypass de `/admin` del L4) → [[vulnerabilities/028-access-control/access-control|access control]].
> - **Authentication** (credenciales filtradas → toma de cuenta) → [[vulnerabilities/029-authentication/authentication|authentication]].
> - **`.git` descargado + `read.py`** para el L5 → `vulnerabilities/014-information-disclousure/Leer .git/`.
