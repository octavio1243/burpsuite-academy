---
aliases:
  - Web Cache Deception labs
  - WCD labs
tags:
  - vuln/web-cache-deception
  - labs
  - portswigger
---

# Web Cache Deception — Labs de PortSwigger

Labs de la categoría **[Web cache deception](https://portswigger.net/web-security/web-cache-deception)**: **5 labs** (1 Apprentice + 4 Practitioner). **Metodología + prevención** → [[vulnerabilities/031-web-cache-deception/web-cache-deception|entry point]]. El hilo común: la **caché** y el **origen** interpretan **distinto** la misma URL → el origen sirve un endpoint **dinámico con datos privados** que la caché guarda como **estático** → el atacante **lee** la respuesta cacheada de la víctima.

> [!danger] WCD ≠ WCP
> **Deception LEE** el contenido privado de la víctima (la caché lo guarda por error). **Poisoning ESCRIBE** el payload del atacante en la respuesta que reciben otros. Misma raíz (discrepancia caché ↔ origen), objetivo inverso. → [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|WCP]]

> [!note] Cómo leer la tabla
> **Discrepancia** = por qué caché y origen difieren. **Payload** = la URL que crafteás. **Dato robado** = qué se filtra de la respuesta cacheada. El fin práctico es siempre el mismo: **leer datos privados de la víctima** (API key, CSRF token, datos de cuenta).

---

## Tabla de labs

| #   | Lab · nivel                                                                                                                                                                              | Discrepancia (caché ↔ origen)                                             | Payload de resolución                                  | Dato robado                                  |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------ | -------------------------------------------- |
| 1   | [Exploiting path mapping](https://portswigger.net/web-security/web-cache-deception/lab-wcd-exploiting-path-mapping) · **Apprentice**                                                     | El origen usa rutas REST-style e **ignora** el segmento extra del path    | `GET /my-account/wcd.js`                               | **API key** de la víctima                    |
| 2   | [Exploiting path delimiters](https://portswigger.net/web-security/web-cache-deception/lab-wcd-exploiting-path-delimiters) · **Practitioner**                                             | El origen **corta** el path en un delimitador que la caché **no** honra   | `GET /my-account%23wcd.js` (o `;`, `%3f`)              | **API key** de la víctima                    |
| 3   | [Exploiting origin server normalization](https://portswigger.net/web-security/web-cache-deception/lab-wcd-exploiting-origin-server-normalization) · **Practitioner**                     | El **origen** normaliza dot-segments (`..%2f`) → vuelve al endpoint dinámico | `GET /static/..%2fmy-account`                          | **API key** de la víctima                    |
| 4   | [Exploiting cache server normalization](https://portswigger.net/web-security/web-cache-deception/lab-wcd-exploiting-cache-server-normalization) · **Practitioner**                       | La **caché** normaliza el path → matchea una regla estática que el origen no ve | `GET /my-account%2f%2e%2e%2fstatic/wcd.js`            | **API key** de la víctima                    |
| 5   | [Exploiting exact-match cache rules](https://portswigger.net/web-security/web-cache-deception/lab-wcd-exploiting-exact-match-cache-rules) · **Practitioner**                             | Regla de **nombre exacto** (`robots.txt`) + delimiter/normalización        | `GET /my-account%23%2f%2e%2e%2frobots.txt`            | **API key** de la víctima                    |

---

## Patrones / cosas relevantes

- **Siempre hay dos actores que discrepan** — la **caché** (¿cacheo esto?) y el **origen** (¿qué endpoint sirvo?). El bug es la **diferencia** de parseo/normalización entre ambos. Sin discrepancia no hay deception.
- **Cache oracle** — `X-Cache: hit/miss` + `Age` + **tiempo de respuesta** te dicen (a) que hay caché y (b) si tu URL quedó cacheada. Es la 🚩 FLAG que anotás en el to-do.
- **Descubrí las reglas de cacheo primero** — pedí `/algo.js`, `/algo.css`, `/static/algo`, `/robots.txt` y mirá cuáles vuelven con `X-Cache: hit`. Eso te dice **qué extensiones/rutas/nombres** cachea → contra eso armás el payload.
- **Se prueba desde Repeater, no desde el browser** — el navegador **URL-encodea** `;`, `#`, `?`, espacios; para pegarle al gadget con el char **crudo** (delimiter o dot-segment) mandás la request desde Burp.
- **Cache buster al probar** — usá `?cb=<único>` mientras testeás para no cachear la URL real; al entregar a la víctima usás la URL **limpia** que después vas a pedir vos.
- **La entrega es client-side** — le mandás el link a la víctima (autenticada); su respuesta privada queda cacheada; **vos** pedís la misma URL y la leés. Por eso en el examen suele ser **Stage 2** (requiere una víctima que navegue). → [[exam/to-do-list/web-cache-deception|to-do del examen]]
- **El dato robado varía** pero el patrón es el mismo: en los labs es la **API key** de `/my-account`; en un target real puede ser el **CSRF token**, el email o la sesión.

## Payloads por lab (resumen)

| Técnica                        | Char/truco clave                    | Ejemplo                                                    |
| ------------------------------ | ----------------------------------- | --------------------------------------------------------- |
| Path mapping                   | segmento extra con extensión        | `/my-account/wcd.js`                                       |
| Path delimiters                | `;` `%3b` `%23` `%3f` `%0a` `%00`   | `/my-account;wcd.js` · `/my-account%23wcd.js`             |
| Origin normalization           | `..%2f` (el **origen** lo resuelve) | `/static/..%2fmy-account`                                  |
| Cache normalization            | `%2f%2e%2e%2f` (la **caché** lo resuelve) | `/my-account%2f%2e%2e%2fstatic/wcd.js`               |
| Exact-match cache rules        | nombre exacto + delimiter/dot-seg   | `/my-account%23%2f%2e%2e%2frobots.txt`                    |
