---
aliases:
  - Deser 008 - custom Java gadget chain
  - ProductTemplate readObject SQLi
tags:
  - vuln/insecure-deserialization
  - example
  - portswigger
---

# 008 — Gadget chain Java propio (→ SQLi por deserialización)

> Lab: [Developing a custom gadget chain for Java deserialization](https://portswigger.net/web-security/deserialization/exploiting/lab-deserialization-developing-a-custom-gadget-chain-for-java-deserialization) · **Expert** · técnica → [[vulnerabilities/013-insecure_deserialization/insecure-deserialization|entry point]]

## Ficha
- **Objeto:** Java serializado — pero el gadget lo armás con **una clase de la propia app** (`ProductTemplate`).
- **Codificación:** `base64` → cookie.
- **Herramienta:** un **programa Java propio** que instancia y serializa el objeto (o **Hackvertor** para re-encodar en vivo).
- **Efecto:** **no es RCE** → es **SQL injection** disparada dentro del `readObject()` → sacar la pass del admin.

## Paso 1 — leer el código fuente
El código está expuesto en `/backup`:
> `GET /backup/ProductTemplate.java` · `GET /backup/AccessTokenUser.java`

Ahí ves que `ProductTemplate.readObject()` **mete el atributo `id` directo en una query SQL** → SQLi.

## El ataque
Instanciás `ProductTemplate` con un `id` malicioso, lo serializás y base64. El `id` lleva el UNION:

> `id =` ==`' UNION SELECT NULL,NULL,NULL,CAST(password AS numeric),NULL,NULL,NULL,NULL FROM users--`==

El `CAST(password AS numeric)` fuerza un **error de conversión** que **filtra la contraseña** en el mensaje.

## El pipeline de codificación (lo importante)
> `Java serialize(ProductTemplate)` **⟶** ==`base64`== **⟶** cookie

## Por qué funciona
- `readObject()` corre **al deserializar** y ejecuta la query con tu `id` → la SQLi vive **dentro del proceso de deserialización**, no en un parámetro HTTP normal.
- No hay gadget de RCE disponible, pero **la propia clase de la app es el gadget**: te da un sink (SQL) que alcanza para robar credenciales.

## Detalles que se pasan por alto
- **Recompilar es lento:** usá **Hackvertor** (`<@base64>…</@base64>`) para editar el payload y re-encodar sin recompilar — además recalcula offsets solo.
- PortSwigger da un **template Java** en su repo `serialization-examples`; solo cambiás el `id`.
- Con la pass del admin → logueás y borrás a carlos.

→ Siguiente: [[vulnerabilities/013-insecure_deserialization/examples/009-php-custom-gadget|009 · PHP custom]]
