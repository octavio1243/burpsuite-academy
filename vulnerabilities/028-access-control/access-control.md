---
aliases:
  - Access Control
  - access-control-entrypoint
  - Broken Access Control
  - broken access control
  - IDOR
tags:
  - vuln/access-control
  - entrypoint
---

# Access Control — Punto de entrada

> Documento **agnóstico al negocio**: *cómo **detectar y explotar** fallas de control de acceso*.
> **Lab por lab** (inicial → logrado → cómo) → [[vulnerabilities/028-access-control/labs/README|labs/README]].

> [!abstract] La idea en una línea
> La app **no verifica que TENGAS permiso** para una acción o un recurso: hace la comprobación en el **cliente**, o solo en **una capa/paso**, o confía en algo que **vos controlás** (un `id`, una cookie, un header, el método). Entonces hacés algo **por encima de tu rol** (vertical) o **al costado**, sobre datos de otro (horizontal).

## 📚 Referencias rápidas

- 🧪 **Labs** — 13 (9 Apprentice + 4 Practitioner), cada uno con **acceso inicial → logrado → cómo** → [[vulnerabilities/028-access-control/labs/README|labs/README]]

## 🧩 Tipos de control de acceso

- **Vertical** — separa **roles/privilegios**. Ej.: el **admin** puede borrar usuarios y el usuario normal no. Romperlo = **escalada de privilegios** (llegar a `/admin`).
- **Horizontal** — mismo nivel, pero **datos de OTRO usuario**. Ej.: ver el **saldo/cuenta de otro**.
  - **IDOR** (Insecure Direct Object Reference): la app referencia un objeto por un **id que vos cambiás** (`?id=`, un filename, etc.).
  - **Evitá ids secuenciales** (1,2,3… se enumeran solos). Pero **un UUID no es garantía**: suele estar **filtrado** en otra parte (un blog post, un perfil, una respuesta JSON) → igual lo usás.
- **Context-dependent** — depende del **estado/paso** del flujo. Ej.: **modificar el carrito después de haberlo pagado**, o saltar a un paso al que todavía no deberías llegar.

## 🧪 Cómo cazarlo (metodología)

Por **cada acción y cada recurso**, repetí la request cambiando **quién/cómo/cuándo**:

1. **Vertical:** ¿la podés hacer con un **usuario de menor privilegio** (o anónimo)? Probá las funciones de admin sin ser admin.
2. **Horizontal:** cambiá el **identificador** (`id`, `user`, filename, GUID) por el de **otro usuario**. ¿Te devuelve sus datos?
3. **Context-dependent:** mandá la request **fuera de orden/estado** (repetir un paso ya cerrado, saltar uno).

> [!tip] Mirá SIEMPRE el body, aunque te redirija
> Un control flojo a veces **te patea al login con un `302 Location: /login`** … pero **el body de esa respuesta ya trae el dato** (la API key, la cuenta). No mires solo el status → leé el cuerpo → [User ID con fuga de datos en redirect](https://portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter-with-data-leakage-in-redirect).

## 🔓 Técnicas de bypass (el control existe, pero está mal puesto)

### A nivel de URL / ruteo
- **Headers no estándar** que el back respeta y el front no filtra:
  ```
  X-Original-URL: /admin/deleteUser
  X-Rewrite-URL:  /admin/deleteUser
  ```
  (mandás la request a `/`, el path real va en el header) → [URL-based access control circumvented](https://portswigger.net/web-security/access-control/lab-url-based-access-control-can-be-circumvented).
- **Slash final:** `/admin/deleteUser` vs `/admin/deleteUser/`.
- **Alternar mayúsculas:** `/ADMIN/DELETEUSER` vs `/admin/deleteUser`.
- **Sufijo (Spring `useSuffixPatternMatch`)** — en Spring **anterior a 5.3 viene habilitado por defecto**: `/admin/deleteUser.anything` matchea igual que `/admin/deleteUser` (y el filtro del front que miraba el path exacto no lo agarra).

### A nivel de método
- **Cambiar `POST` por `GET`** (u otro método) — si el control solo cubre el método original, la acción pasa → [Method-based access control circumvented](https://portswigger.net/web-security/access-control/lab-method-based-access-control-can-be-circumvented).

### Basado en headers "de confianza"
- **Referer:** subpáginas como `/admin/deleteUser` a veces **solo chequean el `Referer`** → se lo mandás vos:
  ```
  Referer: https://LAB/admin
  ```
  (nunca es una credencial) → [Referer-based access control](https://portswigger.net/web-security/access-control/lab-referer-based-access-control).

### Basado en geolocalización
- Control por **ubicación geográfica** → se saltea con **web proxies, VPNs** o **manipulando el mecanismo de geolocalización del cliente** (es client-side).

### Multi-paso / contexto
- **Seguridad floja en pasos posteriores:** los controles suelen estar en el **primer** paso; el **paso final** (el que confirma) a veces **no revalida** → **replay directo** de esa request con tu sesión → [Multi-step process with no access control](https://portswigger.net/web-security/access-control/lab-multi-step-process-with-no-access-control).

## 🛡️ Prevención

- **Denegar por defecto**; permitir solo lo explícito.
- **Verificar en el server, en CADA request** (no en el cliente, no una sola vez).
- **Nunca** confiar en **obscurity** (URLs "impredecibles"), ni en **method / URL-matching / Referer / geolocalización** como control.
- Referenciar objetos con **ids no adivinables Y con check de dueño** (el UUID no reemplaza la verificación de permiso).

---

> [!tip] Reglas mentales
> - **3 preguntas por request:** ¿la puede hacer alguien de **menor rol**? ¿con el **id de otro**? ¿**fuera de contexto**?
> - **El control puede existir pero estar mal puesto** → probá URL (header/slash/case/suffix), método, Referer.
> - **Leé el body** aunque el status sea 302/403.
> - **UUID ≠ seguro:** buscá dónde está filtrado.

> [!note] Relación con otras vulns
> - **Information disclosure** — `robots.txt`, JS y comentarios filtran rutas/GUID de admin → carpeta `vulnerabilities/014-information-disclousure/`.
> - **CSRF / clickjacking** — si una acción privilegiada no tiene otra protección, el control de acceso solo no alcanza.
> - **Business logic** — los context-dependent se solapan con fallas de lógica → carpeta `vulnerabilities/015-business-logic/`.
