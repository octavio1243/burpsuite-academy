---
aliases:
  - Web Cache Poisoning labs
  - WCP labs
tags:
  - vuln/web-cache-poisoning
  - labs
  - portswigger
---

# Web Cache Poisoning — Labs de PortSwigger

Labs de la categoría **[Web cache poisoning](https://portswigger.net/web-security/web-cache-poisoning)**: **13 labs** (9 Practitioner + 4 Expert). **Metodología + prevención** → [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|entry point]]. El hilo común: un input **unkeyed** (que no entra en la cache key) **cambia la respuesta** → queda cacheada → se sirve a **todos**.

> [!abstract] Dos clases (cómo las agrupa PortSwigger)
> - **Design flaws** — el diseño mismo del caché ignora un input que sí afecta la respuesta (headers/cookies unkeyed).
> - **Implementation flaws** — discrepancias de **parseo/normalización** entre caché y origen (query, `;`, `fat GET`, URL-decode, cache key).

> [!note] Cómo leer la tabla
> **Vector** = el input unkeyed que abusás. **Recurso** = qué respuesta cacheada se envenena. **Efecto** = qué termina ejecutándose. El fin práctico es siempre el mismo: **JS en el browser de cada visitante → robo de sesión**.

---

## Tabla de labs

| #   | Lab · nivel                                                                                                                                                                                                                            | Clase          | Vector (input unkeyed)                                             | Recurso contaminado               | Efecto                                       |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ------------------------------------------------------------------ | --------------------------------- | -------------------------------------------- |
| 1   | [Unkeyed header](https://portswigger.net/web-security/web-cache-poisoning/exploiting-design-flaws/lab-web-cache-poisoning-with-an-unkeyed-header) · **Practitioner**                                                                   | Design         | `X-Forwarded-Host` reflejado en `<script src>`                     | HTML → importa tu JS              | XSS a todos                                  |
| 2   | [Unkeyed cookie](https://portswigger.net/web-security/web-cache-poisoning/exploiting-design-flaws/lab-web-cache-poisoning-with-an-unkeyed-cookie) · **Practitioner**                                                                   | Design         | cookie reflejada en JS inline                                      | HTML (JS inline)                  | XSS (breakout de string)                     |
| 3   | [Multiple headers](https://portswigger.net/web-security/web-cache-poisoning/exploiting-design-flaws/lab-web-cache-poisoning-with-multiple-headers) · **Practitioner**                                                                  | Design         | `X-Forwarded-Host` + `X-Forwarded-Scheme` combinados               | HTML → import JS                  | XSS                                          |
| 4   | [Targeted, unknown header](https://portswigger.net/web-security/web-cache-poisoning/exploiting-design-flaws/lab-web-cache-poisoning-targeted-using-an-unknown-header) · **Practitioner**                                               | Design         | header secreto (Param Miner); key incluye `User-Agent`             | HTML → import JS                  | XSS **dirigido** a una víctima concreta      |
| 5   | [Unkeyed query string](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-unkeyed-query) · **Practitioner**                                                              | Implementation | todo el query fuera de la key (solo keyea el path)                 | HTML reflejado bajo `/`           | XSS                                          |
| 6   | [Unkeyed query parameter](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-unkeyed-param) · **Practitioner**                                                           | Implementation | un param puntual (`utm_content`) unkeyed                           | HTML reflejado                    | XSS                                          |
| 7   | [Parameter cloaking](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-param-cloaking) · **Practitioner**                                                               | Implementation | cloak con `;` tras `utm_content` → pisa el `callback`              | **JS** (`geolocate.js`)           | ejecuta `alert(1)`                           |
| 8   | [Fat GET request](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-fat-get) · **Practitioner**                                                                         | Implementation | GET con **body**: cache keyea la URL, la app lee el body           | HTML/JS reflejado                 | XSS                                          |
| 9   | [URL normalization](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-normalization) · **Practitioner**                                                                 | Implementation | el caché decodifica el path distinto que el browser                | **página 404** (path reflejado)   | reflected XSS entregado por link             |
| 10  | [DOM vuln vía strict cacheability](https://portswigger.net/web-security/web-cache-poisoning/exploiting-design-flaws/lab-web-cache-poisoning-to-exploit-a-dom-vulnerability-via-a-cache-with-strict-cacheability-criteria) · **Expert** | Design         | `X-Forwarded-Host` contamina un **JSON** que lee `initGeoLocate()` | **JSON** → sink DOM               | `<img src=1 onerror=alert(document.cookie)>` |
| 11  | [Combining WCP vulnerabilities](https://portswigger.net/web-security/web-cache-poisoning/exploiting-design-flaws/lab-web-cache-poisoning-combining-vulnerabilities) · **Expert**                                                       | Design         | encadena varias técnicas (excavar + unkeyed)                       | HTML → import JS                  | XSS completo                                 |
| 12  | [Cache key injection](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-cache-key-injection) · **Expert**                                                               | Implementation | inyección en `Origin` (con `cors=1`) reflejada                     | HTML login → import `localize.js` | XSS                                          |
| 13  | [Internal cache poisoning](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-internal) · **Expert**                                                                     | Implementation | caché **interna** trata `X-Forwarded-Host` como unkeyed            | import `geolocate.js` → tu server | `alert(document.cookie)`                     |

---

## Patrones / cosas relevantes

- **El header rey es `X-Forwarded-Host`** — casi todos los "design flaws" nacen de reflejarlo en un `<script src>`/import del HTML → apuntás el import a tu exploit server.
- **Cache oracle** — `X-Cache: hit/miss` + `Age` te dicen (a) que hay caché y (b) si pegaste el hit. Es la 🚩 FLAG que ya anotás en los STAGE.
- **Param Miner** es la herramienta central: *Guess headers* para los design flaws, *Guess params* para los implementation flaws.
- **Implementation flaws = discrepancia de parseo** entre caché y origen: query unkeyed (5, 6), cloaking con `;` (7), body en un GET (8), normalización de URL (9), inyección en la key (12), caché interna vs externa (13).
- **El efecto es siempre XSS a escala** → `alert(document.cookie)` en el lab, exfil real de cookie en el examen → **robás la sesión de quien visite** (víctima o admin). **No es escalada de privilegios** por sí sola.
- **Recurso contaminado varía** pero el vehículo es JS: HTML que importa JS (mayoría), un JS directo (7, 13), un JSON leído por el cliente (10), o una 404 reflejada (9).
