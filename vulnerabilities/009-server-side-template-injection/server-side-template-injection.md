---
aliases:
  - SSTI
  - ssti-entrypoint
  - Server-Side Template Injection
  - server-side template injection
tags:
  - vuln/ssti
  - entrypoint
---

# Server-Side Template Injection (SSTI) — Punto de entrada

> Documento **agnóstico al motor**: *cómo **detectar, identificar y explotar** SSTI*.
> **Payloads por lenguaje/motor** (leer archivo, listar, RCE) → [[vulnerabilities/009-server-side-template-injection/ssti-cheatsheet|cheatsheet de motores]].
> **Payload por lab** → [[vulnerabilities/009-server-side-template-injection/labs/README|labs/README]].

> [!abstract] La idea en una línea
> Tu input **no se pasa como dato a la plantilla, sino que se concatena dentro de ella** → el motor lo **evalúa como expresión suya**. Confirmás con `7*7`, **identificás el motor** por su sintaxis/errores, leés su doc y llegás a **leer archivos, fugar info o RCE**.

## 📚 Referencias rápidas

- 📖 **Cheatsheet de motores** (sintaxis + confirmar + leer/listar/RCE por lenguaje) → [[vulnerabilities/009-server-side-template-injection/ssti-cheatsheet|ssti-cheatsheet]]
- 🧪 **Labs** (7, con motor · lenguaje · payload que funcionó) → [[vulnerabilities/009-server-side-template-injection/labs/README|labs/README]]
- 🌐 **Externo** → [PayloadsAllTheThings — SSTI](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection)

## 🎯 Cómo surge (dos caminos)

1. **El dev concatena tu input dentro de la plantilla** (en vez de pasarlo como variable):
   ```php
   $output = $twig->render("Dear " . $_GET['name']);   // ← name={{7*7}} se evalúa
   ```
2. **La app deja editar plantillas a propósito** — a usuarios privilegiados (content managers, "preferred name", descripción de producto). Si comprometés esa cuenta, el SSTI es **by design**. ← *el caso típico del examen (Stage 3, ya sos admin)*.

## 💥 Qué se logra (espectro de impacto)

- **Fuga de info** — leer variables/objetos del contexto (`settings.SECRET_KEY`, env vars, config).
- **Lectura de archivos** — API nativa del motor (`File.read`, `open().read()`) → `/home/carlos/secret`.
- **RCE** — control total del back-end → pivotear a infra interna.

## 🧪 Metodología: Detectar → Identificar → Explotar

### 1) Detectar
Primero, **¿tu input se evalúa server-side?** Dependе del **contexto**:

- **Plaintext** (tu input se renderiza tal cual): meté una operación matemática.
  - `${7*7}` / `{{7*7}}` / `<%= 7*7 %>` → si devuelve `49`, se evaluó del lado del server.
- **Code context** (tu input ya cae **dentro** de una expresión del template): primero **descartá XSS**, después **rompé la expresión**.
  - `nombre}}<tag>` → si ves el HTML inyectado **y** el resto parseado, escapaste la expresión.
- **Fuzzing genérico** — tirá el polyglot y mirá si algo **rompe** (excepción/error):
  ```
  ${{<%[%'"}}%\
  ```
  Un error de plantilla ya te dice que **hay un motor interpretando**. Batería completa de polyglots + probes → [[vulnerabilities/009-server-side-template-injection/ssti-cheatsheet#🔍 Payloads de detección (fuzz → identificar)|payloads de detección]].

### 2) Identificar el motor
- **Por error:** una expresión inválida (`${foobar}`, `<%= foobar %>`) suele tirar un **stack trace que nombra el motor** (y hasta la versión). Es lo más rápido.
- **Por eliminación:** probás sintaxis de cada familia y ves cuál es válida. Árbol → [[vulnerabilities/009-server-side-template-injection/ssti-cheatsheet#🎯 Árbol de detección de SSTI (metodología PortSwigger)|árbol de detección]].
- ⚠️ **El mismo payload puede dar `49` en varios motores** (`{{7*7}}` = Jinja2 **o** Twig) → confirmá con un desempate (`{{7*'7'}}` → `49` Twig / `7777777` Jinja2). Nunca cierres el motor con una sola prueba.

### 3) Explotar (no es solo RCE)
Una vez que sabés el motor, **explorá qué te da** — en este orden de "ruido":

1. **Leé la doc del motor** — sintaxis, built-ins, notas de seguridad, exploits públicos documentados.
2. **Explorá el entorno** — objetos, variables y funciones accesibles. Buscá **objetos sensibles** y **objetos que puso el dev** (a veces te dan escalada sin RCE):
   - Enumerar (Django): `{% debug %}` → lista el contexto → `{{ settings.SECRET_KEY }}`.
   - Env vars (Java/Spring EL): `${T(java.lang.System).getenv()}`.
   - Objetos de la app (lab custom): descubrir `user.setAvatar()` / `user.gdprDelete()` y encadenarlos.
3. **Leer archivos / RCE** — con la API nativa del motor (más limpio, sobrevive a sandbox) o con exec/`system`. Payloads concretos → [[vulnerabilities/009-server-side-template-injection/ssti-cheatsheet#📖 Leer archivos y listar directorios (sin depender del shell)|leer/listar sin shell]] y [[vulnerabilities/009-server-side-template-injection/ssti-cheatsheet#💥 Payloads de RCE por motor|RCE por motor]].

> [!tip] Sandbox ≠ fin del juego
> Django y FreeMarker-sandbox **no dan RCE directo**. Ahí el objetivo se corre a **fuga de info** (SECRET_KEY) o a **reflection** sobre objetos disponibles (leer un archivo). Ver labs 5 y 6.

## 🛡️ Prevención

- **No dejar que ningún usuario edite/suba plantillas** (la defensa principal).
- Usar motores **logic-less** (Mustache) cuando alcance.
- **Sandbox** real: quitar módulos/funciones peligrosas, o correr el motor en un **contenedor aislado**.

---

> [!tip] Reglas mentales
> - **Detectar → Identificar → Explotar.** Nunca tires el payload de RCE antes de fijar el motor con `7*7` + error.
> - **Contexto:** plaintext (inyectás directo) vs code context (cerrás con `}}` primero).
> - **Un `49` no alcanza** para cerrar el motor → desempatá.
> - **Explotar es explorar:** doc → objetos/entorno → leer archivo / RCE. La fuga de info a veces basta.

> [!note] Relación con otras vulns
> - **OS command injection** — cuando el motor te da shell, es RCE igual que [[vulnerabilities/027-os-command-injection/os-command-injection|command injection]]; exfil del archivo idéntico (curl/wget OOB).
> - **XSS** — en code context, primero descartás que sea solo XSS del lado cliente antes de cantar SSTI.
