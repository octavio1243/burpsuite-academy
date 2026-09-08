---
aliases:
  - CSRF labs
  - Cross-Site Request Forgery labs
  - csrf-labs
tags:
  - vuln/csrf
  - labs
  - portswigger
---

# CSRF — Labs de PortSwigger (Apprentice + Practitioner)

Tabla resumen de los labs de **CSRF** (categoría core), en el **mismo orden** que la [Web Security Academy](https://portswigger.net/web-security/all-labs#cross-site-request-forgery-csrf). No hay labs **Expert** en esta categoría.

La idea es un **pantallazo de en qué hacer foco**: qué **acción relevante** se logra ejecutar (cambiar email, cambiar contraseña, etc.), **qué defensa** hay que sortear (token, SameSite, Referer) y **cómo** se bypassea cada una.

> **Base común de todo CSRF:** hay una **acción con estado** (cambiar email/password, borrar cuenta…) que se dispara con una request **predecible** y **solo** con la cookie de sesión (que el navegador manda sola). Si además la defensa es débil/ausente → forjás la request desde tu página y la víctima la ejecuta al visitarla. Metodología y bypasses → [[vulnerabilities/003-csrf/csrf|entry point]].

## Apprentice

| #   | Laboratorio | Defensa | Foco: qué logra, cómo se bypassa |
| --- | ----------- | ------- | -------------------------------- |
| 1 | [CSRF vulnerability with no defenses](https://portswigger.net/web-security/csrf/lab-no-defenses) | **Ninguna** | El caso base: `change-email` **sin token CSRF**. **Logra:** cambiar el email de la víctima → después reseteás su password por correo. **Cómo:** form auto-submit (Burp → *Generate CSRF PoC*) en el exploit server. |

## Practitioner

| #   | Laboratorio | Defensa | Foco: qué logra, cómo se bypassa |
| --- | ----------- | ------- | -------------------------------- |
| 2 | [Token validation depends on request method](https://portswigger.net/web-security/csrf/bypassing-token-validation/lab-token-validation-depends-on-request-method) | Token **solo en POST** | **Logra:** cambiar email. **Cómo:** cambiá `POST`→`GET`; en GET **no valida** el token → lo omitís. Foco: la validación depende del método. |
| 3 | [Token validation depends on token being present](https://portswigger.net/web-security/csrf/bypassing-token-validation/lab-token-validation-depends-on-token-being-present) | Token **solo si está** | **Logra:** cambiar email. **Cómo:** **eliminá** por completo el parámetro `csrf` → si no está, no lo valida. Foco: "valida solo si el token existe". |
| 4 | [Token not tied to user session](https://portswigger.net/web-security/csrf/bypassing-token-validation/lab-token-not-tied-to-user-session) | Token válido pero **global** | **Logra:** cambiar email. **Cómo:** logueate como atacante, **capturá un token válido tuyo** y usalo en el PoC contra la víctima (el token no está atado a *quién* es). Foco: token no ligado a la sesión. |
| 5 | [Token tied to non-session cookie](https://portswigger.net/web-security/csrf/bypassing-token-validation/lab-token-tied-to-non-session-cookie) | Token atado a `csrfKey` (cookie **no** de sesión) | **Logra:** cambiar email. **Cómo:** el token se valida contra una cookie `csrfKey` que **no** es la de sesión → buscá un endpoint que **inyecte Set-Cookie** (p. ej. `search` con CRLF) para setear tu `csrfKey` en la víctima + tu token que matchea. Foco: la cookie de CSRF es independiente de la sesión. |
| 6 | [Token duplicated in cookie](https://portswigger.net/web-security/csrf/bypassing-token-validation/lab-token-duplicated-in-cookie) | **Double submit** (body == cookie) | **Logra:** cambiar email. **Cómo:** solo compara que `csrf` del **body** == `csrf` de la **cookie**; no valida el token de verdad → inyectá `Set-Cookie: csrf=fake` (CRLF) y mandá `csrf=fake` en el body. Foco: **token duplicado header/cookie + body** → basta con que coincidan. |
| 7 | [SameSite Lax bypass via method override](https://portswigger.net/web-security/csrf/bypassing-samesite-restrictions/lab-samesite-lax-bypass-via-method-override) | Cookie **SameSite=Lax** | **Logra:** cambiar email. **Cómo:** Lax bloquea POST cross-site pero deja pasar **GET de navegación** → mandá GET con `_method=POST` (override de método). Foco: convertir el POST prohibido en un GET permitido. |
| 8 | [SameSite Strict bypass via client-side redirect](https://portswigger.net/web-security/csrf/bypassing-samesite-restrictions/lab-samesite-strict-bypass-via-client-side-redirect) | Cookie **SameSite=Strict** | **Logra:** cambiar email. **Cómo:** Strict bloquea todo lo cross-site → encadená con un **redirect del lado cliente** ya presente en el sitio (gadget que redirige según un parámetro): tu exploit navega a esa URL **same-site** que reenvía al `change-email`. Foco: la request final sale *desde el propio sitio*. |
| 9 | [SameSite Strict bypass via sibling domain](https://portswigger.net/web-security/csrf/bypassing-samesite-restrictions/lab-samesite-strict-bypass-via-sibling-domain) | **SameSite=Strict** | **Logra:** ejecutar acción vía **XSS/WebSocket** en un **subdominio hermano** (mismo *site*) → las cookies Strict **sí** viajan entre hermanos. **Cómo:** encontrás XSS en `cms.` (o similar) y desde ahí lanzás el ataque same-site. Foco: "same-site" incluye subdominios hermanos. *(Ejemplo completo con WebSocket en el [[vulnerabilities/003-csrf/csrf|entry point]].)* |
| 10 | [Referer validation depends on header being present](https://portswigger.net/web-security/csrf/bypassing-referer-based-defenses/lab-referer-validation-depends-on-header-being-present) | Valida **Referer** solo si está | **Logra:** cambiar email. **Cómo:** **suprimí** el header `Referer` con `<meta name="referrer" content="no-referrer">` → si no está, no valida. Foco: defensa que solo actúa cuando el Referer existe. |
| 11 | [CSRF with broken Referer validation](https://portswigger.net/web-security/csrf/bypassing-referer-based-defenses/lab-referer-validation-broken) | **Referer** mal validado (substring) | **Logra:** cambiar email. **Cómo:** solo chequea que el Referer **contenga** el dominio target → metelo en tu query string (`exploit.net/?target.web-security-academy.net`) usando `Referrer-Policy: unsafe-url` / `history.pushState`. Foco: validación por substring, no por origen real. |

## Labs de CSRF en otras categorías (cross-ref)

Estos aparecen fuera de la sección CSRF pero son CSRF puro combinado con otra técnica:

| Laboratorio | Categoría | Foco |
| ----------- | --------- | ---- |
| [Exploiting XSS to bypass CSRF defenses](https://portswigger.net/web-security/cross-site-scripting/exploiting/lab-perform-csrf) | XSS | Cuando **SÍ hay token**: un XSS lo **lee** y forja la request → ver [[vulnerabilities/002-xss/README#🎯 Qué hacer con un XSS (objetivos de explotación)|XSS → bypass CSRF]]. |
| [Basic clickjacking with CSRF token protection](https://portswigger.net/web-security/clickjacking/lab-basic-csrf-protected) | Clickjacking | El token CSRF **no** protege del clickjacking (la víctima envía el form real ella misma) → [[vulnerabilities/004-clickjacking/clickjacking\|Clickjacking]]. |
| [Performing CSRF exploits over GraphQL](https://portswigger.net/web-security/graphql/lab-graphql-csrf-via-graphql-api) | GraphQL | CSRF sobre un endpoint GraphQL que acepta `Content-Type` de formulario. |

---

## Cómo leer esta tabla / atajos mentales

- **Todo CSRF = acción relevante + request predecible + solo cookie.** Primero confirmá que hay una **acción con estado** que valga forjar (cambiar email/password sobre todo). Sin acción relevante, no hay CSRF que rinda. Esa es la **FLAG** real, no la ausencia de token.
- **Defensa → bypass** (columna clave):
  - **Sin defensa** (lab 1) → PoC directo.
  - **Token** (labs 2-6) → el token puede estar mal implementado: depende del método, solo se valida si está, no atado a la sesión, atado a cookie no-de-sesión, o duplicado (double-submit). **Probá quitarlo, cambiar método, reusar el tuyo, o setear la cookie con CRLF.**
  - **SameSite** (labs 7-9) → `Lax` cae con GET + `_method=POST`; `Strict` cae con **redirect client-side** o **subdominio hermano**. Mirá el atributo SameSite de la cookie.
  - **Referer** (labs 10-11) → suprimir el header, o meter el dominio target como substring.
- **La acción típica del lab es `change-email`** → cambiás el email de la víctima a uno tuyo y después **reseteás su contraseña** por correo. En algún lab es otra acción (comentario, etc.), pero el patrón es el mismo.
- **Si hay token y no lo podés bypassear** solo con CSRF → no es callejón sin salida: buscá **XSS** (lee el token) o **dangling markup** (lo exfiltra bajo CSP). El *cómo* está en el [[vulnerabilities/002-xss/README#🎯 Qué hacer con un XSS (objetivos de explotación)|entry point de XSS]].
- Técnica de explotación completa (PoCs, CRLF Set-Cookie, `_method`, SameSite) → [[vulnerabilities/003-csrf/csrf|entry point]].
