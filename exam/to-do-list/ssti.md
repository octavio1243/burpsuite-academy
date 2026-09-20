---
aliases:
  - to-do SSTI
tags:
  - exam/to-do
  - vuln/ssti
---

# SSTI — Qué probar

> Técnica → [[vulnerabilities/009-server-side-template-injection/server-side-template-injection|entry point]] · payload por motor → [[vulnerabilities/009-server-side-template-injection/ssti-cheatsheet|cheatsheet]] · ejemplos 001–004 · labs → [[vulnerabilities/009-server-side-template-injection/labs/README|labs]]

## 🚩 Flags

> [!danger] 🚩 ¿Está?
> Algo **editable que después se renderiza**: el ***preferred name***, o —lo más probable— la **descripción de un producto**. Confirmá con `7*7` (y oastify si es ciego).

## 🎯 Objetivo (Stage 3)
- **RCE** → `cat /home/carlos/secret`; o **fuga de info** si el motor está sandboxeado.

## ♾️ Independiente del stage
- [ ] **Identificar motor:** fuzz `${7*7}` · `{{7*7}}` · `<%= 7*7 %>` · `#{7*7}` → mirá cuál da `49` y el **error** → [[vulnerabilities/009-server-side-template-injection/ssti-cheatsheet#🔍 Payloads de detección (fuzz → identificar)|payloads de detección]] · [[vulnerabilities/009-server-side-template-injection/ssti-cheatsheet#🎯 Árbol de detección de SSTI (metodología PortSwigger)|árbol]]. Motor desconocido → identificalo por el **error** con el polyglot → [[vulnerabilities/009-server-side-template-injection/examples/003-identificar-a-ciegas-y-exploit-documentado-handlebars|003]].
- [ ] **Polyglot para que explote:** `${{<%[%'"}}%` — mezcla la sintaxis de todos los motores, así que ninguno lo parsea limpio. **Metelo entero y mirá qué error tira:** cada engine falla distinto y el mensaje delata cuál es (FreeMarker, Velocity, Jinja2/Tornado, ERB, Handlebars…). Sirve incluso cuando `7*7` no refleja `49`.

| Lenguaje | Motor típico |
| --- | --- |
| Ruby | ERB |
| Python | Tornado · Django |
| Java | FreeMarker |
| Node | Handlebars |

- [ ] **Según el motor** (payload en el cheatsheet): RCE → leer el secreto. Plaintext directo (ERB) → [[vulnerabilities/009-server-side-template-injection/examples/001-deteccion-y-rce-erb-plaintext|001]] · motor conocido con doc (FreeMarker) → [[vulnerabilities/009-server-side-template-injection/examples/002-rce-freemarker-usando-documentacion|002]].
- [ ] **Django / FreeMarker sandbox** → no dan RCE directo → fuga de info (`{% debug %}` → `settings.SECRET_KEY`) o reflection → [[vulnerabilities/009-server-side-template-injection/examples/004-sandbox-fuga-de-info-django|004]].
- [ ] Ciego → confirmar por **OAST**. → [[vulnerabilities/009-server-side-template-injection/server-side-template-injection|entry point]]

## 🔗 Referencias
- [[vulnerabilities/009-server-side-template-injection/server-side-template-injection|entry point]] · [[vulnerabilities/009-server-side-template-injection/ssti-cheatsheet|cheatsheet]] · ejemplos [[vulnerabilities/009-server-side-template-injection/examples/001-deteccion-y-rce-erb-plaintext|001]] · [[vulnerabilities/009-server-side-template-injection/examples/002-rce-freemarker-usando-documentacion|002]] · [[vulnerabilities/009-server-side-template-injection/examples/003-identificar-a-ciegas-y-exploit-documentado-handlebars|003]] · [[vulnerabilities/009-server-side-template-injection/examples/004-sandbox-fuga-de-info-django|004]] · [[vulnerabilities/009-server-side-template-injection/labs/README|labs]] · [PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection)
