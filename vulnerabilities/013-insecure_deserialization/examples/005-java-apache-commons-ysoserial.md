---
aliases:
  - Deser 005 - Java Apache Commons ysoserial
  - ysoserial CommonsCollections4
tags:
  - vuln/insecure-deserialization
  - example
  - portswigger
---

# 005 — Java con Apache Commons (ysoserial) ⭐

> Lab: [Exploiting Java deserialization with Apache Commons](https://portswigger.net/web-security/deserialization/exploiting/lab-deserialization-exploiting-java-deserialization-with-apache-commons) · **Practitioner** · técnica → [[vulnerabilities/013-insecure_deserialization/insecure-deserialization|entry point]]

## Ficha
- **Objeto:** Java serializado — en base64 empieza con **`rO0AB`** (`AC ED 00 05` crudo).
- **Codificación:** bytes crudos de ysoserial → `base64` → `url` → cookie.
- **Herramienta:** **ysoserial** (gadget **CommonsCollections4**).
- **Efecto:** **RCE** → `rm /home/carlos/morale.txt`.

## Generar el payload
ysoserial arma la cadena de gadgets que abusa la lib **Apache Commons Collections** (ya cargada por la app):

```
java -jar ysoserial-all.jar CommonsCollections4 'rm /home/carlos/morale.txt' | base64
```

> En JDK ≥ 16 hacen falta los `--add-opens`. En el vault: [`JAVA/serialize_payload.py`](vulnerabilities/013-insecure_deserialization/JAVA/serialize_payload.py) los agrega solo y aplica el pipeline `base64,url`.

## El pipeline de codificación (lo importante)
> `bytes ysoserial` **⟶** ==`base64`== **⟶** ==`url-encode`== **⟶** valor de la cookie `session`

Pegás ese valor en la cookie, mandás el request, y al deserializar la app **ejecuta el comando**.

## Por qué funciona
- La app hace `readObject()` sobre la cookie **sin validar la clase**.
- El gadget **CommonsCollections** encadena reflexión hasta `Runtime.exec()` → tu comando corre con los privilegios del server.
- **`rO0AB` en una cookie = Java serializado en base64** → señal directa de que ysoserial aplica.

## Detalles que se pasan por alto
- **Elegí el gadget según la lib presente:** si CC4 no anda, probá `CommonsCollections3/2`, `CommonsBeanutils1`, `Groovy1`. La lib tiene que estar en el classpath.
- Es **ciego**: no ves salida. Confirmás por el **efecto** (archivo borrado) o exfiltrás con `wget --post-file` (ver [[vulnerabilities/027-os-command-injection/examples/006-exfil-archivo-completo|OSCi 006]]).

→ Siguiente: [[vulnerabilities/013-insecure_deserialization/examples/006-php-phpggc-symfony|006 · PHP · phpggc + firma]]
