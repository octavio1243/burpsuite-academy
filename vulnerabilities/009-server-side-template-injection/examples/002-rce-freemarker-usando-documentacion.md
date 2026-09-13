---
aliases:
  - SSTI 002 - RCE FreeMarker con documentación
  - freemarker ssti java
tags:
  - vuln/ssti
  - example
  - portswigger
---

# 002 — RCE en motor conocido leyendo su documentación (FreeMarker, Java)

> Lab: [SSTI using documentation](https://portswigger.net/web-security/server-side-template-injection/exploiting/lab-server-side-template-injection-using-documentation) · **Practitioner** · técnica → [[vulnerabilities/009-server-side-template-injection/server-side-template-injection|entry point]]

## ¿Por qué acá? (el salto realista)
- **Ya sabés el motor, pero no hay one-liner obvio:** el RCE sale **de la propia doc** del motor. Este es el flujo del examen: identificás → buscás la doc → armás el payload.
- **Por qué funciona:** editás la **descripción de un producto** (logueado como *content-manager*) y esa descripción se renderiza con **FreeMarker**. El built-in `?new()` te deja instanciar clases arbitrarias.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo reemplazable (comando a ejecutar).

**Identificar:** meté `${foobar}` en la descripción → el error de render **nombra FreeMarker**. Entonces, según la doc, `freemarker.template.utility.Execute` corre comandos:
<pre class="payload"><code>&lt;#assign ex="freemarker.template.utility.Execute"?new()&gt;${ ex("<mark>rm /home/carlos/morale.txt</mark>") }</code></pre>

## Verificación
Guardás la descripción, se re-renderiza el producto y el comando se ejecuta → **`morale.txt` desaparece** → lab resuelto.

## Detalles que se pasan por alto
- Sin **leer la doc** del motor no salís: el truco (`?new()` + `Execute`) no es adivinable.
- `${...}` es la sintaxis de expresión de FreeMarker → si `${7*7}` da `49` y el error dice *FreeMarker*, estás en este caso.
- El vector es una feature **de admin/content-manager**: primero conseguí ese rol (Stages 1–2) y recién ahí llegás a la descripción editable.

→ Siguiente: [[vulnerabilities/009-server-side-template-injection/examples/003-identificar-a-ciegas-y-exploit-documentado-handlebars|003 · motor desconocido → identificarlo por el error]]
