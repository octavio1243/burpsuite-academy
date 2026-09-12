---
aliases:
  - to-do SSTI
tags:
  - exam/to-do
  - vuln/ssti
---

# SSTI — Qué probar

> Técnica → [[vulnerabilities/009-server-side-template-injection/server-side-template-injection|entry point]] · payload por motor → [[vulnerabilities/009-server-side-template-injection/ssti-cheatsheet|cheatsheet]] · labs → [[vulnerabilities/009-server-side-template-injection/labs/README|labs]]

## 🚩 Flags

> [!danger] 🚩 ¿Está?
> Algo **editable que después se renderiza**: el ***preferred name***, o —lo más probable— la **descripción de un producto**. Confirmá con `7*7` (y oastify si es ciego).

## 🎯 Objetivo (Stage 3)
- **RCE** → `cat /home/carlos/secret`; o **fuga de info** si el motor está sandboxeado.

## ♾️ Independiente del stage
- [ ] **Identificar motor:** fuzz `${7*7}` · `{{7*7}}` · `<%= 7*7 %>` · `#{7*7}` → mirá cuál da `49` y el **error** → [[vulnerabilities/009-server-side-template-injection/ssti-cheatsheet#🎯 Árbol de detección de SSTI (metodología PortSwigger)|árbol de detección]].

  | Lenguaje | Motor típico |
  | --- | --- |
  | Ruby | ERB |
  | Python | Tornado · Django |
  | Java | FreeMarker |
  | Node | Handlebars |

- [ ] **Según el motor** (payload en el cheatsheet): RCE → leer el secreto.
- [ ] **Django / FreeMarker sandbox** → no dan RCE directo → fuga de info (`{% debug %}` → `settings.SECRET_KEY`) o reflection.
- [ ] Ciego → confirmar por **OAST**.

## 🔗 Referencias
- [[vulnerabilities/009-server-side-template-injection/server-side-template-injection|entry point]] · [[vulnerabilities/009-server-side-template-injection/ssti-cheatsheet|cheatsheet]] · [[vulnerabilities/009-server-side-template-injection/labs/README|labs]] · [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection)
