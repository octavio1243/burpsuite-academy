---
aliases:
  - Clickjacking labs
  - clickjacking-labs
tags:
  - vuln/clickjacking
  - labs
  - portswigger
---

# Clickjacking — Labs de PortSwigger (Apprentice + Practitioner)

Tabla resumen de los labs de **Clickjacking** (categoría core), en el **mismo orden** que la [Web Security Academy](https://portswigger.net/web-security/all-labs#clickjacking). No hay labs **Expert** en esta categoría.

La idea es un **pantallazo de en qué hacer foco**: qué **acción relevante** logra ejecutar la víctima a ciegas (borrar cuenta, cambiar email, disparar XSS), **qué defensa** hay que sortear (token CSRF, frame buster, multistep) y **cómo** se arma el overlay.

> **Base común de todo clickjacking:** hay una **acción con estado** disparada por un **clic** (botón "Delete account", "Update email", "Submit feedback"…) en una página que **se puede enmarcar** (le faltan `X-Frame-Options` / CSP `frame-ancestors`). Montás la página real en un `<iframe>` casi transparente y ponés un **señuelo clickeable** justo encima del botón: la víctima cree que hace clic en tu página y en realidad clickea el botón real **con su sesión**. Metodología y plantillas → [[vulnerabilities/004-clickjacking/clickjacking|entry point]].

## Apprentice

| #   | Laboratorio | Defensa / Twist | Foco: qué logra, cómo se arma |
| --- | ----------- | --------------- | ----------------------------- |
| 1 | [Basic clickjacking with CSRF token protection](https://portswigger.net/web-security/clickjacking/lab-basic-csrf-protected) | Form protegido con **token CSRF** | **Logra:** que la víctima **borre su cuenta** (`Delete account`). **Cómo:** el token CSRF **no protege** del clickjacking porque la víctima manda el form real ella misma (el token viaja en la página enmarcada). Iframe con `opacity` baja + un `<div>` señuelo "Click me" encima del botón *Delete*. Foco: **token CSRF ≠ defensa anti-clickjacking**. |
| 2 | [Clickjacking with form input data prefilled from a URL parameter](https://portswigger.net/web-security/clickjacking/lab-prefilled-form-input) | El form se **prellena por query param** | **Logra:** **cambiar el email** de la víctima. **Cómo:** el campo email se autocompleta con `?email=...` en la URL del iframe → cargás el iframe con **tu** email prellenado y ponés el señuelo sobre *Update email*. Foco: **prellenar el input vía URL** para no depender de que la víctima tipee. |
| 3 | [Clickjacking with a frame buster script](https://portswigger.net/web-security/clickjacking/lab-frame-buster-script) | **Frame buster** (JS que rompe el iframe) | **Logra:** cambiar email. **Cómo:** la página trae un script que detecta estar enmarcada y se escapa (`top.location = self.location`). Lo **neutralizás** con `sandbox="allow-forms"` en el iframe (**sin** `allow-scripts` / `allow-top-navigation`) → el JS de la página no puede navegar el top. Foco: **`sandbox` mata el frame buster**. |

## Practitioner

| #   | Laboratorio | Defensa / Twist | Foco: qué logra, cómo se arma |
| --- | ----------- | --------------- | ----------------------------- |
| 4 | [Exploiting clickjacking vulnerability to trigger DOM-based XSS](https://portswigger.net/web-security/clickjacking/lab-exploiting-to-trigger-dom-based-xss) | Clickjacking **encadenado con DOM XSS** | **Logra:** disparar un **DOM XSS** (`print()`) que solo se activa con un clic. **Cómo:** hay un **feedback form** con DOM XSS; prellenás sus campos (name/email/comment) por **query params** con el payload y ponés el señuelo sobre *Submit feedback* → el clic a ciegas ejecuta el XSS. Foco: clickjacking como **gatillo de interacción** para un XSS que requiere clic. |
| 5 | [Multistep clickjacking](https://portswigger.net/web-security/clickjacking/lab-multistep) | Acción de **dos pasos** (confirmación) | **Logra:** **borrar la cuenta** cuando hace falta *dos* clics (botón + confirmación). **Cómo:** **dos señuelos** posicionados: "Click me first" sobre *Delete account* y "Click me next" sobre el *Yes/confirm*. Foco: **alinear varios overlays** para un flujo con confirmación. |

## 📎 Ejemplos resueltos (HTML real)

Exploits ya armados y calibrados, listos para adaptar (reemplazá `TARGET` / `EXPLOIT` / email):

| Ejemplo | Lab | Técnica |
| ------- | --- | ------- |
| [[vulnerabilities/004-clickjacking/examples/prefill-email-grid-overlay\|Prefill email + grilla]] | Prefilled from URL param | email por query param + grilla de señuelos que tapiza la pantalla |
| [[vulnerabilities/004-clickjacking/examples/multistep-delete-account\|Multistep delete account]] | Multistep | dos señuelos (`Click me first`/`next`) + beacon de layout |

---

## Cómo leer esta tabla / atajos mentales

- **Todo clickjacking = acción relevante clickeable + página enmarcable.** Primero confirmá que **(a)** hay una **acción con estado** que se dispara con un **clic** (borrar cuenta, cambiar email, submit) **y (b)** la página **se deja enmarcar** (no hay `X-Frame-Options: deny/sameorigin` ni CSP `frame-ancestors`). Sin esas dos, no hay clickjacking. Esa es la **FLAG** real. Ver [[vulnerabilities/004-clickjacking/clickjacking#🎯 Condiciones para que exista clickjacking (la FLAG real)|condiciones]].
- **La defensa NO suele ser una cabecera** (si estuviera, no habría lab), sino un **twist del form**:
  - **Token CSRF** (lab 1) → **no importa**: la víctima manda el form real, el token va incluido.
  - **Prefill por URL** (labs 2 y 4) → cargás el iframe con los valores ya puestos (`?email=`, campos del feedback) → la víctima solo pone el clic.
  - **Frame buster** (lab 3) → `sandbox="allow-forms"` sin `allow-scripts` → el script no corre / no puede navegar el top.
  - **Multistep** (lab 5) → varios señuelos alineados a cada botón del flujo.
- **La acción típica es `Delete account` o `change-email`** → mismo patrón que CSRF, pero acá la víctima **tiene que hacer clic** (no es silencioso). Por eso el **método de entrega es el exploit server** (la víctima visita tu página y "clickea").
- **Diferencia con [[vulnerabilities/003-csrf/csrf|CSRF]]:** CSRF forja la request **sin** interacción; clickjacking necesita **un clic de la víctima** pero **sí sirve cuando hay token CSRF** (que a CSRF puro lo frenaría). Son complementarios.
- **Alineá con `opacity` alta y bajala para entregar:** durante el armado usás `opacity: 0.1` para ver el botón real y posicionar el señuelo; para entregar la dejás casi en `0` (`0.0001`). El offset (`top`/`left`) del iframe alinea el botón bajo tu señuelo.
- Plantillas completas (overlay base, prefill, sandbox anti-frame-buster, multistep, DOM XSS, beacon de resolución) → [[vulnerabilities/004-clickjacking/clickjacking|entry point]].
