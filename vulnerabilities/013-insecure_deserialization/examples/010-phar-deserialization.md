---
aliases:
  - Deser 010 - PHAR deserialization
  - phar wrapper polyglot JPG
tags:
  - vuln/insecure-deserialization
  - example
  - portswigger
---

# 010 — PHAR deserialization (sin entry point visible)

> Lab: [Using PHAR deserialization to deploy a custom gadget chain](https://portswigger.net/web-security/deserialization/exploiting/lab-deserialization-using-phar-deserialization-to-deploy-a-custom-gadget-chain) · **Expert** · técnica → [[vulnerabilities/013-insecure_deserialization/insecure-deserialization|entry point]]

## Ficha
- **Objeto:** PHP serializado, **dentro del manifest de un archivo PHAR**.
- **Codificación:** **no** es base64 en cookie → es un **archivo polyglot JPG+PHAR** que subís como avatar.
- **Herramienta:** **phpggc** con `-p phar` (+ hacerlo polyglot con un JPEG).
- **Efecto:** **RCE** vía **`phar://`** → borrar `morale.txt` (a través de Twig/SSTI).

## El truco: no hay `unserialize()` a la vista
Ninguna cookie se deserializa. Pero **cualquier función de archivo** (`file_exists`, `fopen`, `file_get_contents`…) sobre una ruta **`phar://`** **deserializa el manifest del PHAR automáticamente**.

## El ataque
1. Generás el PHAR con el gadget y lo hacés **polyglot con un JPEG** (para pasar el validador de imagen del upload):
   > `phpggc` ... `-p phar -o evil.phar` → prepend del header JPEG.
2. Lo subís como **avatar** → queda en el server.
3. Disparás la deserialización apuntando el wrapper a tu archivo:
   > `GET /cgi-bin/avatar.php?avatar=`==`phar://`==`wiener`

Al abrir el PHAR, corre el gadget (`__destruct` de la cadena `Blog`/`Author`) que termina en un **payload Twig/SSTI**:
> ==`{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("rm /home/carlos/morale.txt")}}`==

## El pipeline (lo importante)
> `phpggc -p phar` **⟶** ==`polyglot JPG+PHAR`== **⟶** upload avatar **⟶** trigger ==`phar://`== **⟶** RCE

## Por qué funciona
- **`phar://` deserializa sin `unserialize()` explícito** → el "entry point" es cualquier operación de archivo que acepte una ruta que controlás.
- El **polyglot** engaña al validador (lo ve como JPG) pero el intérprete lo trata como PHAR.

## Detalles que se pasan por alto
- **Cuando no encontrás dónde deserializa, pensá en `phar://`** + un file upload + una función de archivo con ruta controlable.
- Este lab combina **file upload** + **deserialización** + **SSTI** → cross-ref [[vulnerabilities/017-file-upload-vulnerabilities/file-upload-vulnerabilities|file upload]] y [[vulnerabilities/009-server-side-template-injection/server-side-template-injection|SSTI]].

← Vuelta al [[vulnerabilities/013-insecure_deserialization/insecure-deserialization|entry point]]
