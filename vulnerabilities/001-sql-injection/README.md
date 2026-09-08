# SQL Injection — Punto de entrada

> Documento inicial de SQL Injection. Acá va **en qué hacer foco** antes de abrir los labs.

## 📚 Referencias rápidas

- 🧪 **Laboratorios** — detalle lab por lab (18 labs, orden oficial + foco de cada uno): [labs/README.md](labs/README.md)
- 📄 **Cheat sheet** — sintaxis por motor (concat, substring, comentarios, versión, contenidos, errores condicionales, time delays, DNS/OAST…): [cheat-sheet.md](cheat-sheet.md)

> [!danger] 🚩 ¿Está o no está?
> Si la app usa una **cookie `TrackingId`** → **casi seguro hay SQL Injection**.
> Ojo: cuando entra por la cookie suele ser **blind**. Si hay tracking, hay 🚩 **FLAG** casi asegurada.

## 📍 Dónde buscar la inyección (puntos de entrada)

- [ ] **Filtro de categoría** (`?category=...`) → cláusula WHERE / UNION, **salida visible**. El caso más directo.
- [ ] **Login** (campo `username`) → bypass con `administrator'--` (comenta la verificación de password).
- [ ] **Cookie `TrackingId`** → **blind** (⚠️ cuidado). *Casi seguro que si hay tracking hay SQL Injection.*
- [ ] **Stock check** → suele llevar **body XML**; es el punto típico de **filter bypass con WAF**.

## 🧪 Cosas a tener en cuenta en las pruebas

- [ ] **Si es blind, probar en este orden:** `error-based` → `time-based` → `OAST/Collaborator`.
  - Primero intento que un **error condicional** me dé el oráculo.
  - Si no hay error, paso a **retardos de tiempo** (`pg_sleep`, `WAITFOR`, etc.).
  - Si no hay ni tiempo, escalo a **out-of-band** (DNS/HTTP a Burp Collaborator).
- [ ] **XML (stock check):** si hay **WAF** que bloquea `UNION`/`SELECT`, **ofuscar** con **entidades HTML/numéricas** (tab *Hackvertor* de Burp) para colar el payload.
- [ ] **Base (siempre):** romper con `'`, comentar el resto (`--`, `-- ` con espacio, `#`), condición verdadera/falsa (`OR 1=1` / `AND 1=2`), e **identificar el motor** (Oracle / MySQL / MSSQL / PostgreSQL) — define comentario, concatenación, `sleep` y metadatos.

## 🗺️ Referencias

- 📊 **Tabla de los 18 labs** (orden oficial + foco por lab): [labs/README.md](labs/README.md)
- 🐍 **Scripts de ayuda:**
  - Blind por errores condicionales → [blind-sql-conditional-errors.py](blind-sql-conditional-errors.py)
  - Blind por retardos de tiempo → [blind-sql-using-delay.py](blind-sql-using-delay.py)
  - Fuerza bruta de password extraído → [brute-force-password.py](brute-force-password.py)
