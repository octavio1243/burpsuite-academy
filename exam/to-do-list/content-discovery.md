---
aliases:
  - to-do Content Discovery
tags:
  - exam/to-do
  - vuln/information-disclosure
---

# Content Discovery — Qué probar

> Técnica → [[vulnerabilities/014-information-disclousure/information-disclosure|Information disclosure]] · labs → [[vulnerabilities/014-information-disclousure/labs/README|labs]]

## 🎯 Objetivo (transversal)
- Encontrar endpoints/rutas/datos ocultos que abran otra vía (admin panel, GUID, credenciales, backups).

## 🎯 Caso borde (Stage 2)
- [ ] **TRACE → header de auth interno (poco probable, barato):** si `/admin` está restringido por **IP o un header interno**, mandá `TRACE /admin` → la respuesta **refleja** `X-Custom-IP-Authorization` con tu IP. Agregalo con `127.0.0.1` (Burp **Match & Replace**) a todas las requests → el back-end te trata como **interno** y entrás a `/admin`. → [[vulnerabilities/014-information-disclousure/labs/README|info disclosure · lab #4]] · [lab](https://portswigger.net/web-security/information-disclosure/exploiting/lab-infoleak-authentication-bypass)

## ♾️ Independiente del stage
- [ ] **Wordlist del examen** (Intruder / Discover content): [[vulnerabilities/014-information-disclousure/burp-labs-wordlist|burp-labs-wordlist]] (279 rutas de labs BSCP).
- [ ] Burp **Discover content** · `robots.txt` · `sitemap.xml` · `/.git`, `/cgi-bin/phpinfo.php`.
- [ ] Comentarios HTML · JS del cliente · backups (`.bak`, `~`, `.old`) · endpoints/API ocultos.
- [ ] **Endpoint GraphQL** (probá universal + introspection con InQL): `/graphql` · `/api` · `/api/graphql` · `/graphql/api` · `/graphql/graphql`. → [[exam/to-do-list/graphql\|GraphQL]]
- [ ] **Documentación de API** (schema/endpoints expuestos): `/api` · `/swagger/index.html` · `/openapi.json`. → [[exam/to-do-list/api-testing\|API Testing]]

## 🔗 Referencias
- [[vulnerabilities/014-information-disclousure/information-disclosure|Information disclosure (entry point)]] · [[vulnerabilities/014-information-disclousure/labs/README|labs]] · [[vulnerabilities/014-information-disclousure/burp-labs-wordlist|wordlist BSCP]]
