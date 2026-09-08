# SQL Injection — Punto de entrada

> Documento **agnóstico al negocio**: responde *cómo **explotar** una SQLi ya localizada*.
> **Dónde** buscarla en el target y para qué objetivo → eso vive en los `STAGE_x` (recon del negocio).

## 📚 Referencias rápidas

- 🧪 **Laboratorios** — 18 labs, orden oficial + foco de cada uno: [labs/README.md](labs/README.md)
- 📄 **Cheat sheet** — sintaxis por motor (concat, substring, comentarios, versión, contenidos, errores condicionales, time delays, DNS/OAST…): [cheat-sheet.md](cheat-sheet.md)
- 🕶️ **Ofuscación SQL** (bypass de WAF): [[vulnerabilities/019-obfuscacion/sql-obfuscation|sql-obfuscation]]

## 🧪 Cómo explotar (metodología)

1. **Confirmar la inyección:** romper con `'`; observar error o cambio de comportamiento. Calibrar con `OR 1=1` / `AND 1=2`.
2. **Comentar el resto:** `--`, `-- ` (con espacio), `#` — según el motor.
3. **Identificar el motor** (Oracle / MySQL / MSSQL / PostgreSQL): define sintaxis de comentario, concatenación, `sleep` y vistas de metadatos → ver [cheat-sheet.md](cheat-sheet.md).
4. **UNION (salida visible):** nº de columnas (`ORDER BY n` / `UNION SELECT NULL,NULL…`) → columna que acepta texto → exfiltrar (`information_schema` / `all_tables`).
5. **Si es blind, escalar el oráculo en este orden:** `error-based` → `time-based` → `OAST / Collaborator`.
   - Booleano si la respuesta cambia; error condicional si no; retardo de tiempo si tampoco; out-of-band (DNS/HTTP) como último recurso.
6. **Filtro / WAF:** ofuscar el payload (entidades HTML/numéricas, tab *Hackvertor*) → ver [[vulnerabilities/019-obfuscacion/sql-obfuscation|sql-obfuscation]].

> [!warning] No es solo lectura: también es vector de escritura
> Una SQLi **no se limita a leer** con `SELECT`. Es poco probable, pero puede permitir **`UPDATE` / `INSERT` / `DELETE`** — o sea, **modificar** la base, no solo extraerla. Casos típicos:
> - La consulta vulnerable **ya es un `UPDATE`/`INSERT`** (ej. editar perfil, registro, carrito) → tu inyección altera esa escritura.
> - El motor/driver permite **stacked queries** (`; INSERT ...`, `; UPDATE ...`) → encadenás tu propia sentencia (ver *Batched queries* en la [cheat-sheet.md](cheat-sheet.md); ojo: Oracle no las soporta).
>
> **Foco:** ante una SQLi, no descartes escalar de *robar datos* a *cambiar datos* (ej. subir tu rol, `password` de otro usuario, precios). Trátala siempre como vector de ataque completo, no de solo lectura.

## 🐍 Scripts de ayuda

- Blind por errores condicionales → [blind-sql-conditional-errors.py](blind-sql-conditional-errors.py)
- Blind por retardos de tiempo → [blind-sql-using-delay.py](blind-sql-using-delay.py)
- Fuerza bruta de password extraído → [brute-force-password.py](brute-force-password.py)
