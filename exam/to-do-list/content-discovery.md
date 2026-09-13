---
aliases:
  - to-do Content Discovery
tags:
  - exam/to-do
  - vuln/information-disclosure
---

# Content Discovery — Qué probar

> Técnica → [[vulnerabilities/014-information-disclousure/README|Content discovery]]

## 🎯 Objetivo (transversal)
- Encontrar endpoints/rutas/datos ocultos que abran otra vía (admin panel, GUID, credenciales, backups).

## ♾️ Independiente del stage
- [ ] **Wordlist del examen** (Intruder / Discover content): [[vulnerabilities/014-information-disclousure/burp-labs-wordlist|burp-labs-wordlist]] (279 rutas de labs BSCP).
- [ ] Burp **Discover content** · `robots.txt` · `sitemap.xml` · `/.git`, `/cgi-bin/phpinfo.php`.
- [ ] Comentarios HTML · JS del cliente · backups (`.bak`, `~`, `.old`) · endpoints/API ocultos.
- [ ] **Endpoint GraphQL** (probá universal + introspection con InQL): `/graphql` · `/api` · `/api/graphql` · `/graphql/api` · `/graphql/graphql`. → [[exam/to-do-list/graphql\|GraphQL]]
- [ ] **Documentación de API** (schema/endpoints expuestos): `/api` · `/swagger/index.html` · `/openapi.json`. → [[exam/to-do-list/api-testing\|API Testing]]

## 🔗 Referencias
- [[vulnerabilities/014-information-disclousure/README|Content discovery]]
