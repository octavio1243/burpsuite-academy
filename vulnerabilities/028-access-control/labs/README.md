---
aliases:
  - Access Control labs
  - broken access control labs
  - IDOR labs
tags:
  - vuln/access-control
  - labs
  - portswigger
---

# Access Control — Labs de PortSwigger

Labs de la categoría **[Access control](https://portswigger.net/web-security/access-control)**: **13 labs** (9 Apprentice + 4 Practitioner). **Metodología general + técnicas de bypass** → [[vulnerabilities/028-access-control/access-control|entry point]]. El hilo común: la app **no verifica que tengas permiso** para una acción/recurso → hacés algo **por encima** o **al costado** de tu rol.

> [!abstract] Los tres tipos (te dicen "de qué acceso a qué acceso")
> - **Vertical** — subís de privilegio: de usuario normal (o anónimo) a **funciones de admin**.
> - **Horizontal** — mismo nivel, **datos de OTRO usuario** (IDOR: cambiar un `id`).
> - **Horizontal → vertical** — un horizontal que te da credenciales de admin (ej. leer el password del administrator) → terminás vertical.
> - *(Aparte)* **Bypass a nivel plataforma** — el control existe pero se saltea por **URL / método / Referer**.

> [!note] Cómo leer la tabla
> **Inicial → Logrado** = de qué acceso partís y a cuál llegás. **Cómo** = el truco puntual (sin explayar; el detalle vive en el link del lab).

---

## Tabla de labs

| #   | Lab · nivel                                                                                                                                                                        | Tipo                  | Inicial → Logrado                                      | Cómo (el truco)                                                                                                       |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------- | ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| 1   | [Unprotected admin functionality](https://portswigger.net/web-security/access-control/lab-unprotected-admin-functionality) · **Apprentice**                                        | Vertical              | anónimo → **admin**                                    | `/robots.txt` revela `/administrator-panel` → entrar directo                                                          |
| 2   | [Unprotected admin (URL impredecible)](https://portswigger.net/web-security/access-control/lab-unprotected-admin-functionality-with-unpredictable-url) · **Apprentice**            | Vertical              | anónimo → **admin**                                    | la URL del admin está **hardcodeada en el JS** de la home                                                             |
| 3   | [User role controlled by request parameter](https://portswigger.net/web-security/access-control/lab-user-role-controlled-by-request-parameter) · **Apprentice**                    | Vertical              | wiener → **admin**                                     | cookie `Admin=false` → cambiarla a `Admin=true`                                                                       |
| 4   | [User role modifiable in user profile](https://portswigger.net/web-security/access-control/lab-user-role-can-be-modified-in-user-profile) · **Apprentice**                         | Vertical              | wiener → **admin**                                     | **mass assignment**: agregar `"roleid":2` al JSON de update de email                                                  |
| 5   | [User ID controlled by request parameter](https://portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter) · **Apprentice**                        | Horizontal            | wiener → **API key de carlos**                         | **IDOR**: `id=wiener` → `id=carlos`                                                                                   |
| 6   | [...con user IDs impredecibles](https://portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter-with-unpredictable-user-ids) · **Apprentice**      | Horizontal            | wiener → **cuenta de carlos**                          | el **GUID** de carlos está expuesto en un **blog post** suyo → usarlo en `id`                                         |
| 7   | [...con fuga de datos en redirect](https://portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter-with-data-leakage-in-redirect) · **Apprentice** | Horizontal            | wiener → **API key de carlos**                         | cambiás `id` a carlos: responde **302 pero el body del redirect** trae la key                                         |
| 8   | [...con password disclosure](https://portswigger.net/web-security/access-control/lab-user-id-controlled-by-request-parameter-with-password-disclosure) · **Apprentice**            | Horizontal → vertical | wiener → **admin**                                     | `id=administrator` → la cuenta trae el **password del admin** (input masked) → login → borrar carlos                  |
| 9   | [Insecure direct object references (IDOR)](https://portswigger.net/web-security/access-control/lab-insecure-direct-object-references) · **Apprentice**                             | Horizontal            | usuario chat → **password de otro user**               | **IDOR en archivo estático**: `/download-transcript/1.txt` (número incremental)                                       |
| 10  | [URL-based access control circumvented](https://portswigger.net/web-security/access-control/lab-url-based-access-control-can-be-circumvented) · **Practitioner**                   | Bypass (URL)          | wiener → **admin**                                     | front bloquea `/admin`; el back respeta `X-Original-URL` → `POST /` + `X-Original-URL: /admin/delete?username=carlos` |
| 11  | [Method-based access control circumvented](https://portswigger.net/web-security/access-control/lab-method-based-access-control-can-be-circumvented) · **Practitioner**             | Bypass (método)       | wiener (+ admin de muestra) → **self-upgrade a admin** | el control está atado al método → cambiar `POST` a `GET` en la acción de upgrade                                      |
| 12  | [Multi-step process with no access control](https://portswigger.net/web-security/access-control/lab-multi-step-process-with-no-access-control) · **Practitioner**                  | Lógica multi-paso     | wiener (+ admin de muestra) → **self-upgrade a admin** | el **paso final de confirmación** (`confirmed=true`) no revalida admin → replay con sesión de wiener                  |
| 13  | [Referer-based access control](https://portswigger.net/web-security/access-control/lab-referer-based-access-control) · **Practitioner**                                            | Bypass (Referer)      | wiener → **admin**                                     | el control confía en el `Referer` → replay la request de admin con tu cookie **manteniendo `Referer: …/admin`**       |

---

## Patrones / cosas relevantes

- **Vertical (subir de rol):** buscá **funciones de admin sin proteger** (obscurity: `robots.txt`, JS) y **decisiones de rol que viajan en la request** y podés falsear (cookie `Admin`, `roleid`, mass assignment).
- **Horizontal (IDOR):** cualquier **identificador en la request** (`id`, `user`, filename incremental, GUID). Aunque el ID parezca impredecible (**GUID**), suele estar **filtrado** en otra parte (blog, perfil). Ojo con la **fuga en el body de un 302**.
- **Horizontal → vertical:** el mejor botín de un IDOR es **credenciales** (password del admin, API key) → te reconvierte en escalada vertical.
- **Bypass de plataforma:** cuando el control **existe** pero está mal ubicado:
  - **URL** — `X-Original-URL` / `X-Rewrite-URL` (el front filtra por path, el back respeta el header).
  - **Método** — el check solo cubre `POST` → probá `GET` (o un método inválido para ver si "falla abierto").
  - **Referer** — nunca es una credencial; si el back confía en él, lo mandás vos.
- **Multi-paso:** los controles suelen estar en el **primer** paso; el **último** (el que confirma) a veces no revalida → **replay directo**.
- **Objetivo típico:** llegar a `/admin` y **borrar a `carlos`**, o robar la **API key/credencial** de otro usuario.
