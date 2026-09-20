---
aliases:
  - Repaso final BSCP
  - última práctica examen
  - final review labs
tags:
  - exam
  - reference
  - to-do
created: 2026-09-20
---

# Repaso final — última práctica antes del examen

> **Qué es esto:** la lista curada para la última pasada. Priorizada según el [[exam/postmortem/POSTMORTEM|postmortem]] (mis dos fallas reales) y los [[exam/red-herrings|red herrings]]. 12 labs núcleo + 4 de refuerzo.
> **Regla:** timebox **15 min por lab**. Sin progreso → anotá y saltá. Antes de cada uno, decí **qué tipo de interacción de la víctima** aplica (lee correo / navega la home / abre tu exploit).

---

## 🅰️ Bloque A — Innegociables (hoy, sí o sí)

> [!danger] Son mis dos fallas de examen (Ex1: S1 cacheo sin confirmar + S3 XXE sin OOB). Si solo hago dos labs, son estos.

- [ ] **1. XXE blind exfil con DTD externo malicioso** — [Exploiting blind XXE to exfiltrate data using a malicious external DTD](https://portswigger.net/web-security/xxe/blind/lab-xxe-with-out-of-band-exfiltration). **Hacerlo 2 veces.** Grabar: **el `.dtd` se aloja en el exploit server, el Collaborator solo recibe.** Verificar el `.dtd` crudo en el navegador antes de disparar. → [[vulnerabilities/006-xxe/xxe|entry point XXE]] · [[vulnerabilities/006-xxe/examples/005-xxe-ciego-callback-oob|005 · XXE ciego OOB]]
- [ ] **2. WCP parameter cloaking** — [Parameter cloaking](https://portswigger.net/web-security/web-cache-poisoning/exploiting-implementation-flaws/lab-web-cache-poisoning-param-cloaking). **Practitioner (el más picante de los no-Expert).** El cache excluye un parámetro de la key; con `;` colás otro que el back-end sí parsea (`utm_content=x;callback=evil`). Drill: envenenar, reenviar con cache-buster y confirmar **`X-Cache: HIT`** con el poison antes de entregar (mi falla de S1). → [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|entry point WCP]]

---

## 🅱️ Bloque B — JWT (los dos que quiero)

> [!warning] Un JWT jodido es casi seguro. Uno con exploit server (jku) + uno Practitioner sin exploit server (kid traversal). Nada de Expert.

- [ ] **3. JWT jku header injection** — [JWT authentication bypass via jku header injection](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-jku-header-injection). **El del exploit server.** Hospedar el JWK Set (`{"keys":[...]}`) ahí; `jku`=tu URL, `kid`=el de tu clave, `sub:administrator`, firmado con tu privada. **Trap: el `kid` del token tiene que coincidir con el `kid` del JWKS.** → [[vulnerabilities/018-jwt-attacks/examples/005-jku-injection|005 · jku injection]]
- [ ] **4. JWT kid header path traversal** — [JWT authentication bypass via kid header path traversal](https://portswigger.net/web-security/jwt/lab-jwt-authentication-bypass-via-kid-header-path-traversal). **Practitioner.** El `kid` carga la clave desde el filesystem: apuntalo a un archivo de contenido predecible (p.ej. `/dev/null`, vacío) y firmá HS256 usando ese contenido como secreto. Pasos exactos en tu doc + el script. → [[vulnerabilities/018-jwt-attacks/examples/006-kid-path-traversal|006 · kid path traversal]] · `scripts/forge_kid_traversal_jwts.py`

| Lab | Necesita | Trap |
| --- | --- | --- |
| jku (3) | **Exploit server** (hospeda JWKS) | `kid` del token = `kid` del JWKS |
| kid traversal (4) | **Nada extra** (JWT Editor) | Elegir archivo de contenido predecible y derivar el secreto de ahí |

---

## 🅲 Bloque C — Uno por categoría filosa

> Orden por probabilidad de que aparezca y me trabe.

- [ ] **5. CSRF con bypass de Referer** — [CSRF where Referer validation depends on header being present](https://portswigger.net/web-security/csrf/bypassing-referer-based-defenses). Strippear con `<meta name="referrer" content="no-referrer">`. PoC vía Burp → Engagement Tools → Generate CSRF PoC. → [[vulnerabilities/003-csrf/csrf|entry point CSRF]]
- [ ] **6. CSRF SameSite** — [SameSite Lax bypass via method override](https://portswigger.net/web-security/csrf/bypassing-samesite-restrictions). Donde se traba la gente en Stage 2. → [[vulnerabilities/003-csrf/csrf|entry point CSRF]]
- [ ] **7. SSTI motor desconocido** — [SSTI in an unknown language with a documented exploit](https://portswigger.net/web-security/server-side-template-injection/exploiting/lab-server-side-template-injection-in-an-unknown-language-with-a-documented-exploit) (Handlebars). Polyglot de detección: `${{<%[%'"}}%\`. → [[vulnerabilities/009-server-side-template-injection/server-side-template-injection|entry point SSTI]] · [[vulnerabilities/009-server-side-template-injection/ssti-cheatsheet|cheatsheet]]
- [ ] **8. SSRF con filtro** — [SSRF with filter bypass via open redirection](https://portswigger.net/web-security/ssrf/lab-ssrf-filter-bypass-via-open-redirection). Encadena open-redirect + SSRF. → [[vulnerabilities/007-ssrf/ssrf|entry point SSRF]]
- [ ] **9. Business logic toma de cuenta** — [Weak isolation on a dual-use endpoint](https://portswigger.net/web-security/logic-flaws/examples/lab-logic-flaws-weak-isolation-on-dual-use-endpoint). Borrar `current-password`, poner `username=administrator`. → [[vulnerabilities/015-business-logic/business-logic|entry point business logic]]
- [ ] **10. SQLi blind** — [Blind SQL injection with conditional responses](https://portswigger.net/web-security/sql-injection/blind/lab-conditional-responses). El UNION exfil ya lo domino ([[vulnerabilities/001-sql-injection/examples/002-union-exfil-credenciales|002 · exfil credenciales]]); lo que me tumba en S3 es el blind sin salida visible. → [[vulnerabilities/001-sql-injection/README|entry point SQLi]]
- [ ] **11. CORS null origin** — [CORS vulnerability with trusted null origin](https://portswigger.net/web-security/cors/lab-null-origin-whitelisted-attack). Origen `null` vía iframe sandbox. Objetivo: `fetch` a `/accountDetails` + exfil API key. → [[vulnerabilities/005-cors/cors|entry point CORS]]
- [ ] **12. Param Miner** — [Targeted web cache poisoning using an unknown header](https://portswigger.net/web-security/web-cache-poisoning/exploiting-design-flaws/lab-web-cache-poisoning-targeted-using-an-unknown-header). Adivinar el header con Param Miner; la key incluye `User-Agent`. → [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|entry point WCP]]

---

## 🅳 Bloque D — Refuerzo (solo si sobra tiempo)

- [ ] **13. Path traversal, drill de filtros** — tres rápidos seguidos: `....//` ([stripped non-recursively](https://portswigger.net/web-security/file-path-traversal/lab-sequences-stripped-non-recursively)), `%252f` ([superfluous URL-decode](https://portswigger.net/web-security/file-path-traversal/lab-superfluous-url-decode)), null byte `%00.png`. → [[vulnerabilities/010-path-transversal/path-transversal|entry point traversal]]
- [ ] **14. Host header sin reset** — [Routing-based SSRF](https://portswigger.net/web-security/host-header/exploiting/lab-host-header-routing-based-ssrf) + [Host validation bypass via connection state attack](https://portswigger.net/web-security/host-header/exploiting/lab-host-header-authentication-bypass). Lo que aparece cuando el password reset no pica. → [[vulnerabilities/016-host-header-injection/host-header|entry point host header]]
- [ ] **15. DOM XSS** — [DOM XSS using web messages and a JavaScript URL](https://portswigger.net/web-security/dom-based/controlling-the-web-message-source/lab-dom-xss-using-web-messages-and-a-javascript-url). Mi variante iframe + `postMessage`. → [[vulnerabilities/025-dom-based/dom-based|entry point DOM]]
- [ ] **16. WCP header sin cachear (clásico)** — [Web cache poisoning with an unkeyed header](https://portswigger.net/web-security/web-cache-poisoning/exploiting-design-flaws/lab-web-cache-poisoning-with-an-unkeyed-header). El de manual: `X-Forwarded-Host: tu-exploit-server` se refleja sin estar en la cache key; se cachea un `<script>` importado desde tu dominio. Confirmá **`X-Cache: HIT`** con el poison antes de entregar. → [[vulnerabilities/030-web-cache-poisoning/examples/002-xfh-script-import|002 · XFH script import]] · [[vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|entry point WCP]]

---

## 🧭 Cómo correrlo

1. **Bloque A hoy.** Bloques B y C mañana. D solo si llego.
2. **Timebox 15 min por lab.** Sin progreso → anotar y saltar.
3. **Antes de cada lab:** ¿la víctima **lee correo** / **navega la home** / **abre mi exploit**? Elegir el vector según eso (es mi error recurrente — ver [[exam/red-herrings|red herrings]], nota de los 3 tipos de interacción).

> [!note] Vínculos maestros
> [[exam/postmortem/POSTMORTEM|Postmortem]] · [[exam/red-herrings|Red herrings]] · [[exam/STAGE_1/STAGE_1|Stage 1]] · [[exam/STAGE_2/STAGE_2|Stage 2]] · [[exam/STAGE_3/STAGE_3|Stage 3]]
