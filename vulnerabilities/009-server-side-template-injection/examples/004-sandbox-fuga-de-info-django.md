---
aliases:
  - SSTI 004 - sandbox → fuga de info (Django)
  - django ssti secret_key
tags:
  - vuln/ssti
  - example
  - portswigger
---

# 004 — Motor sandboxeado sin RCE → fuga de info (Django, Python)

> Lab: [SSTI with information disclosure via user-supplied objects](https://portswigger.net/web-security/server-side-template-injection/exploiting/lab-server-side-template-injection-with-information-disclosure-via-user-supplied-objects) · **Practitioner** · técnica → [[vulnerabilities/009-server-side-template-injection/server-side-template-injection|entry point]]

## ¿Por qué acá? (sandbox = no hay RCE)
- **Cuando el motor está sandboxeado, el objetivo cambia:** ya no borrás un archivo, **filtrás un secreto** desde los objetos que el dev dejó en el contexto.
- **Por qué funciona:** editás la **descripción de producto** (logueado) y se renderiza con **Django**, que está **muy restringido**: `{{7*7}}` **no da 49** (no evalúa aritmética) → no hay RCE directo, pero sí acceso a objetos como `settings`.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = payload fijo de Django (no hay nada que reemplazar salvo el vector editable).

**Enumerar** lo accesible: el tag `{% debug %}` lista todo el contexto → aparece `settings`.
<pre class="payload"><code><mark>{% debug %}</mark></code></pre>
**Filtrar** el secreto:
<pre class="payload"><code><mark>{{settings.SECRET_KEY}}</mark></code></pre>

## Verificación
`{% debug %}` te muestra `settings` entre los objetos disponibles; `{{settings.SECRET_KEY}}` **renderiza la SECRET_KEY** en la página → la enviás para resolver el lab.

## Detalles que se pasan por alto
- **`{{7*7}}` que NO da `49` es la pista:** motor sandboxeado (Django) → dejá de buscar RCE y pasá a **fuga de info / reflection**.
- El objetivo **no es** borrar `morale.txt`: es **leer** `settings.SECRET_KEY`.
- Mismo patrón para **FreeMarker con sandbox**: si el RCE clásico está bloqueado, escapás por **reflection** desde un objeto disponible (ej. `product`).

→ Siguiente: volvé al [[vulnerabilities/009-server-side-template-injection/labs/README|README de labs]] para los casos Expert (FreeMarker sandbox por reflection y motor custom).
