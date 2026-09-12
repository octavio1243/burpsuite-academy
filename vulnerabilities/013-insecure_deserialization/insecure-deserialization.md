---
aliases:
  - Insecure Deserialization
  - insecure-deserialization-entrypoint
  - deserializacion insegura
  - object injection
  - gadget chain
tags:
  - vuln/insecure-deserialization
  - entrypoint
---

# Insecure Deserialization — Punto de entrada

> Documento **agnóstico al negocio**: *cómo **detectar y explotar** la deserialización insegura*.
> **Dónde** aparece (qué cookie/parámetro trae el objeto) → eso vive en los `STAGE_x` y en [[exam/to-do-list/insecure-deserialization|Qué probar]].

> [!abstract] La idea en una línea
> La app **reconstruye un objeto a partir de datos que vos controlás** (típico: la cookie de sesión). Si podés **modificar ese objeto** —cambiar un atributo, cambiar su **tipo**, o inyectar **otra clase**— disparás lógica que el dev no esperaba: desde `admin=true` hasta **RCE** encadenando *magic methods* (**gadget chain**).

## 📚 Ejemplos / PoCs

> Del más simple (editar a mano) al más avanzado (gadget chain propio):

- **PHP a mano** (sin herramienta, solo editar el serializado):
    - [[vulnerabilities/013-insecure_deserialization/examples/001-modificar-objeto-php|001 · flip de atributo (`admin`)]] · [[vulnerabilities/013-insecure_deserialization/examples/002-modificar-tipos-php|002 · type juggling (`==`)]]
    - [[vulnerabilities/013-insecure_deserialization/examples/003-usar-funcionalidad-app|003 · abusar una feature (borrar archivo)]] · [[vulnerabilities/013-insecure_deserialization/examples/004-object-injection-php|004 · object injection (`__destruct`)]]
- **Con herramienta** (gadget chains pre-armados) ⭐ el corazón del examen:
    - [[vulnerabilities/013-insecure_deserialization/examples/005-java-apache-commons-ysoserial|005 · Java · ysoserial]] · [[vulnerabilities/013-insecure_deserialization/examples/006-php-phpggc-symfony|006 · PHP · phpggc + firma]] · [[vulnerabilities/013-insecure_deserialization/examples/007-ruby-gadget-documentado|007 · Ruby · Marshal]]
- **Gadget chain propio** (Expert):
    - [[vulnerabilities/013-insecure_deserialization/examples/008-java-custom-gadget-sqli|008 · Java custom → SQLi]] · [[vulnerabilities/013-insecure_deserialization/examples/009-php-custom-gadget|009 · PHP custom]] · [[vulnerabilities/013-insecure_deserialization/examples/010-phar-deserialization|010 · PHAR (sin entry point)]]

## 🗺️ Tabla maestra (lenguaje · codificación · herramienta · efecto)

> **Esto es lo que hay que tener a mano en el examen:** qué objeto es, qué capas de encoding le pusieron y con qué se generó.

| # | Lab · nivel | Objeto (lenguaje) | Pipeline de codificación | Herramienta | Efecto |
| --- | --- | --- | --- | --- | --- |
| [[vulnerabilities/013-insecure_deserialization/examples/001-modificar-objeto-php\|001]] | Modifying serialized objects · Appr | **PHP** `O:4:"User"…` | `base64` | a mano | `admin` → true |
| [[vulnerabilities/013-insecure_deserialization/examples/002-modificar-tipos-php\|002]] | Modifying serialized data types · Prac | **PHP** `O:4:"User"…` | `base64` | a mano | type juggling `==` |
| [[vulnerabilities/013-insecure_deserialization/examples/003-usar-funcionalidad-app\|003]] | Using app functionality · Prac | **PHP** `O:…` | `base64` | a mano | borrar `morale.txt` |
| [[vulnerabilities/013-insecure_deserialization/examples/004-object-injection-php\|004]] | Arbitrary object injection · Prac | **PHP** `O:14:"CustomTemplate"…` | `base64` → `url` | a mano | `__destruct`→`unlink` |
| [[vulnerabilities/013-insecure_deserialization/examples/005-java-apache-commons-ysoserial\|005]] | Java w/ Apache Commons · Prac | **Java** `rO0AB…` | bytes → `base64` → `url` | **ysoserial** | **RCE** `rm …` |
| [[vulnerabilities/013-insecure_deserialization/examples/006-php-phpggc-symfony\|006]] | PHP pre-built chain · Prac | **PHP** (Symfony) | serial → `base64` → JSON+HMAC → `base64` → `url` | **phpggc** + firma | **RCE** `rm …` |
| [[vulnerabilities/013-insecure_deserialization/examples/007-ruby-gadget-documentado\|007]] | Ruby documented chain · Prac | **Ruby** Marshal | binario → `base64` → `url` | gadget universal (ruby) | **RCE** `rm …` |
| [[vulnerabilities/013-insecure_deserialization/examples/008-java-custom-gadget-sqli\|008]] | Custom Java chain · Expert | **Java** `ProductTemplate` | `base64` | Java propio / Hackvertor | **SQLi** → pass admin |
| [[vulnerabilities/013-insecure_deserialization/examples/009-php-custom-gadget\|009]] | Custom PHP chain · Expert | **PHP** `CustomTemplate`+`DefaultMap` | `base64` → `url` | a mano | **RCE** `exec()` |
| [[vulnerabilities/013-insecure_deserialization/examples/010-phar-deserialization\|010]] | PHAR deserialization · Expert | **PHP** dentro de **PHAR** | polyglot JPG+PHAR (upload) | phpggc `-p phar` | **RCE** vía `phar://` |

## 🎯 Qué se logra (por qué importa)

- **Escalada de privilegios sin RCE** (001–003): la app confía en atributos del objeto (`admin`, `access_token`, rutas). Los reescribís → sos otro usuario o borrás lo que quieras. *Barato, sin herramientas.*
- **RCE por gadget chain** (004–010): encadenás métodos mágicos (`__destruct`, `__wakeup`, `readObject`…) que ya existen en el código/librerías → ejecutás comandos. **Es el camino a `cat /home/carlos/secret` del Stage 3.**

## 🧪 Cómo detectarlo (metodología)

1. **Buscá el objeto serializado** — casi siempre la **cookie de sesión**. Reconocé el formato por el prefijo:

| Lenguaje | Pista (crudo) | Pista (base64) |
| --- | --- | --- |
| **PHP** | `O:4:"User":…`, `a:2:{…}`, `s:6:"…"` | `Tzo0…`, `YToy…` |
| **Java** | bytes `AC ED 00 05` | **`rO0AB`** |
| **Ruby** (Marshal) | bytes `04 08` | `BAh…` |
| **.NET** | `AAEAAAD…` (BinaryFormatter) | `AAEAAAD…` |
| **Python** (pickle) | opcodes `(dp0`, `c__main__` | `gAN…`, `KGRw…` |

2. **Decodificá las capas** con Burp (Inspector / `Ctrl+B`): normalmente **URL-decode → base64-decode** te deja el objeto legible.
3. **Manipulá y re-encodá** aplicando las capas **al revés**. Ojo con los **contadores de longitud** de PHP (`s:6:"wiener"` → si cambiás el string tenés que cambiar el `6`).

## 🔤 Los métodos mágicos (los "gadgets")

> La deserialización **invoca métodos solita**. Esos son los ganchos que se encadenan.

| Lenguaje | Se dispara al deserializar / destruir | Sink típico |
| --- | --- | --- |
| **PHP** | `__wakeup()`, `__destruct()`, `__toString()`, `__get()` | `unlink`, `call_user_func`, `exec` |
| **Java** | `readObject()` | reflexión → `Runtime.exec` (CommonsCollections) |
| **Ruby** | `_load`, métodos de las libs (Gem) | `Kernel#system` |

## 🧰 Herramientas y scripts del vault

- **Java →** `ysoserial-all.jar` + [`JAVA/serialize_payload.py`](vulnerabilities/013-insecure_deserialization/JAVA/serialize_payload.py) (genera el gadget y aplica el pipeline de capas configurable: `gzip,base64,url`…).
- **PHP →** [`PHP/gen-payload.ps1`](vulnerabilities/013-insecure_deserialization/PHP/gen-payload.ps1) (corre **phpggc** en Docker) + [`PHP/sign-cookie.ps1`](vulnerabilities/013-insecure_deserialization/PHP/sign-cookie.ps1) (firma HMAC-SHA1 para el lab Symfony).
- **Ruby →** [`Ruby/serialize.py`](vulnerabilities/013-insecure_deserialization/Ruby/serialize.py) (Marshal vía Docker: modo `gadget` = RCE universal, `custom` = forjar un objeto real, `object` = entender el formato).
- **Hackvertor** (BApp): tags `<@base64>…</@base64>` para re-encodar en vivo sin recompilar (clave en el lab Java custom, que recalcula offsets).

## 🛡️ Prevención (lado defensivo)

- **No deserializar datos que vengan del usuario.** Si es inevitable, firmá el objeto (HMAC) y verificá **antes** de deserializar.
- **Allow-list de clases** permitidas al deserializar (no arbitrary types).
- Preferir formatos de datos **sin ejecución de código** (JSON puro parseado a un DTO), no serializadores nativos.

---

> [!tip] Reglas mentales
> - **Cookie rara + `rO0`/`Tzo0`/`BAh` = deserialización.** Decodificá capas, mirá el objeto.
> - **¿Solo escalada?** editá atributos/tipos a mano (001–003). **¿RCE?** gadget chain con herramienta (005–007).
> - **PHP a mano:** cuidá los **contadores de longitud**. **Java/Ruby:** las capas casi siempre son `base64 → url`.
> - **Sin entry point visible** pero hay **file upload** → probá **PHAR** (`phar://`).

> [!note] Relación con otras vulns
> - **RCE** — misma meta que [[vulnerabilities/027-os-command-injection/os-command-injection|OS command injection]] y [[vulnerabilities/017-file-upload-vulnerabilities/file-upload-vulnerabilities|file upload]], por otra puerta.
> - **SQLi** — el lab Java custom (008) llega a la base **a través** de la deserialización → [[vulnerabilities/001-sql-injection/README|SQL injection]].
> - **SSTI** — el PHAR (010) termina en **Twig** → [[vulnerabilities/009-server-side-template-injection/server-side-template-injection|SSTI]].
