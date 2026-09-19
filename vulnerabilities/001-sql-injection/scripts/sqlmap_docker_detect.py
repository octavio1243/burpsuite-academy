#!/usr/bin/env python3
"""
Detection-only sqlmap in Docker, through Burp. Does NOT dump data.

Run it:
    python sqlmap_docker_detect.py request.req -p category --https
    python sqlmap_docker_detect.py -u "https://x/filter?category=Gifts"
"""

import argparse
import os
import shutil
import subprocess
import sys

DEFAULT_IMAGE = os.environ.get("SQLMAP_IMAGE", "parrotsec/sqlmap")
DEFAULT_BURP_HOST = os.environ.get("BURP_HOST", "127.0.0.1")
DEFAULT_BURP_PORT = os.environ.get("BURP_PORT", "8080")

# Paste a URL here to run with no arguments (overridden by --url / env).
TARGET_URL = os.environ.get("TARGET_URL", "")

CONTAINER_TO_HOST = "host.docker.internal"
LOCAL_ALIASES = {"127.0.0.1", "localhost", "0.0.0.0", "::1"}
OUTPUT_DIRNAME = "sqlmap-output"


def die(message: str) -> None:
    print(f"[!] {message}", file=sys.stderr)
    sys.exit(1)


def check_docker() -> None:
    if shutil.which("docker") is None:
        die("docker CLI not found in PATH. Install/start Docker Desktop first.")
    result = subprocess.run(["docker", "info"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode != 0:
        die("Docker daemon is not running. Start Docker Desktop.")


def ensure_image(image: str) -> None:
    inspect = subprocess.run(["docker", "image", "inspect", image],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if inspect.returncode == 0:
        print(f"[*] Image '{image}' already present.")
        return
    print(f"[*] Image '{image}' not found. Pulling...")
    if subprocess.run(["docker", "pull", image]).returncode != 0:
        die(f"Failed to pull image '{image}'.")
    print(f"[+] Image '{image}' pulled.")


def resolve_proxy_host(host: str) -> str:
    if host in LOCAL_ALIASES:
        print(f"[*] Burp host '{host}' rewritten to '{CONTAINER_TO_HOST}'.")
        return CONTAINER_TO_HOST
    return host


def build_command(args):
    target_url = args.url or TARGET_URL

    if target_url:
        input_args = ["-u", target_url]
        work_dir = os.getcwd()
        print(f"[*] Input mode: URL -> {target_url}")
    else:
        request_path = os.path.abspath(args.request or "request.req")
        if not os.path.isfile(request_path):
            die(f"No URL and request file not found: {request_path}\n"
                "    Give a URL (--url / TARGET_URL) or a request file.")
        work_dir = os.path.dirname(request_path)
        input_args = ["-r", f"/work/{os.path.basename(request_path)}"]
        print(f"[*] Input mode: request file -> {request_path}")

    output_host_dir = os.path.join(work_dir, OUTPUT_DIRNAME)
    os.makedirs(output_host_dir, exist_ok=True)

    proxy_host = resolve_proxy_host(args.burp_host)
    proxy_url = f"http://{proxy_host}:{args.burp_port}"

    docker_cmd = [
        "docker", "run", "--rm",
        "--add-host", f"{CONTAINER_TO_HOST}:host-gateway",
        "-v", f"{work_dir}:/work",
    ]
    if args.oob_domain:
        docker_cmd += ["-p", "53:53/udp"]
    docker_cmd.append(args.image)
    if args.sqlmap_bin:
        docker_cmd += args.sqlmap_bin.split()

    sqlmap_args = input_args + [
        "--proxy", proxy_url,
        "--batch",
        "--technique", args.technique,
        f"--level={args.level}",
        f"--risk={args.risk}",
        f"-v{args.verbosity}",
        "--output-dir=/work/" + OUTPUT_DIRNAME,
    ]
    if args.param:
        sqlmap_args += ["-p", args.param]
    if args.dbms:
        sqlmap_args += ["--dbms", args.dbms]
    if args.https:
        sqlmap_args.append("--force-ssl")
    if args.flush_session:
        sqlmap_args.append("--flush-session")
    if args.oob_domain:
        sqlmap_args += ["--dns-domain", args.oob_domain]
    sqlmap_args += args.passthrough

    return docker_cmd + sqlmap_args, output_host_dir


def parse_args():
    p = argparse.ArgumentParser(
        description="Detection-only sqlmap wrapper (Docker + Burp).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Extra sqlmap flags go after `--`, e.g. `-- --tamper=space2comment`.",
    )
    p.add_argument("request", nargs="?", default=None,
                   help="Request file from Burp (default: request.req).")
    p.add_argument("-u", "--url", default="",
                   help="Target URL instead of a request file (param in query).")
    p.add_argument("--image", default=DEFAULT_IMAGE, help="sqlmap Docker image.")
    p.add_argument("--sqlmap-bin", default="",
                   help="Prefix if image ENTRYPOINT is not sqlmap.")
    p.add_argument("--burp-host", default=DEFAULT_BURP_HOST, help="Burp host.")
    p.add_argument("--burp-port", default=DEFAULT_BURP_PORT, help="Burp port.")
    p.add_argument("-p", "--param", default="", help="Restrict to this parameter.")
    p.add_argument("--dbms", default="", help="DBMS hint (mysql, postgresql...).")
    p.add_argument("--technique", default="BEUSTQ", help="Techniques; keep T for blind.")
    p.add_argument("--level", type=int, default=1, choices=range(1, 6))
    p.add_argument("--risk", type=int, default=1, choices=range(1, 4))
    p.add_argument("-v", "--verbosity", type=int, default=3, choices=range(0, 7))
    p.add_argument("--https", action="store_true", help="Force HTTPS (--force-ssl).")
    p.add_argument("--flush-session", action="store_true", help="Re-test from scratch.")
    p.add_argument("--oob-domain", default="",
                   help="Out-of-band DNS exfil for blind (needs a delegated domain).")
    p.add_argument("--dry-run", action="store_true", help="Print command, don't run.")

    argv = sys.argv[1:]
    if "--" in argv:
        idx = argv.index("--")
        pre, passthrough = argv[:idx], argv[idx + 1:]
    else:
        pre, passthrough = argv, []
    args = p.parse_args(pre)
    args.passthrough = passthrough
    return args


def main():
    args = parse_args()
    command, output_host_dir = build_command(args)
    print(f"[*] Command:\n    {' '.join(command)}\n")

    if args.dry_run:
        print("[*] --dry-run set; not executing.")
        return

    check_docker()
    ensure_image(args.image)

    print("[*] Running sqlmap (detection only)...\n")
    result = subprocess.run(command)
    print()
    print("[+] sqlmap finished." if result.returncode == 0
          else f"[!] sqlmap exited with code {result.returncode}.")
    print(f"[*] Log and payloads saved under:\n    {output_host_dir}")
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
