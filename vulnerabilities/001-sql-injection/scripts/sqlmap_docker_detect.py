#!/usr/bin/env python3
"""
Detection-only sqlmap in Docker, through Burp. Does NOT dump data.

Edit the CONFIG block below, drop request.req in this folder, then:
    python sqlmap_docker_detect.py
"""

import argparse
import os
import shutil
import subprocess
import sys

# ============================ CONFIG (edit) ============================
REQUEST_FILE = "request.req"   # raw request from Burp, in the current folder
TARGET_URL   = ""              # optional: use a URL instead of REQUEST_FILE
PARAMS       = []              # only test these, e.g. ["TrackingId", "username"]
DBMS         = ["postgresql"]  # motors to try; e.g. ["postgresql", "mysql"]
FORCE_HTTPS  = True            # BSCP targets are HTTPS
BURP_HOST    = "127.0.0.1"
BURP_PORT    = "8080"
SCOPE        = "URL_BODY"      # where to test: URL_BODY | COOKIE | HEADER
RISK         = 1               # 1-3, higher = heavier payloads
# Techniques (letters = try order). Legend:
#   B = boolean-based blind (conditional response, incl. conditional errors)
#   E = error-based (DB error text reflected in the response)
#   T = time-based blind (only the response time changes)
#   U = UNION query-based (in-band, data in the response)
#   S = stacked queries (multiple statements, e.g. ; ...)
#   Q = inline queries (subquery embedded in the original one)
TECHNIQUE    = "BETUSQ"        # B/E (conditional error) and T (time) tried first
IMAGE        = "parrotsec/sqlmap"
# ======================================================================

# SCOPE is cumulative: COOKIE also covers URL_BODY, HEADER covers everything.
SCOPE_TO_LEVEL = {"URL_BODY": 1, "COOKIE": 2, "HEADER": 3}

CONTAINER_TO_HOST = "host.docker.internal"
LOCAL_ALIASES = {"127.0.0.1", "localhost", "0.0.0.0", "::1"}
OUTPUT_DIRNAME = "sqlmap-output"


def die(message: str) -> None:
    print(f"[!] {message}", file=sys.stderr)
    sys.exit(1)


def check_docker() -> None:
    if shutil.which("docker") is None:
        die("docker CLI not found in PATH. Install/start Docker Desktop first.")
    if subprocess.run(["docker", "info"],
                      stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL).returncode != 0:
        die("Docker daemon is not running. Start Docker Desktop.")


def ensure_image(image: str) -> None:
    if subprocess.run(["docker", "image", "inspect", image],
                      stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL).returncode == 0:
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


def build_command(args, dbms):
    target_url = args.url or TARGET_URL

    if target_url:
        input_args = ["-u", target_url]
        work_dir = os.getcwd()
        print(f"[*] Input mode: URL -> {target_url}")
    else:
        request_path = os.path.abspath(args.request or REQUEST_FILE)
        if not os.path.isfile(request_path):
            die(f"Request file not found: {request_path}")
        work_dir = os.path.dirname(request_path)
        input_args = ["-r", f"/work/{os.path.basename(request_path)}"]
        print(f"[*] Input mode: request file -> {request_path}")

    output_host_dir = os.path.join(work_dir, OUTPUT_DIRNAME)
    os.makedirs(output_host_dir, exist_ok=True)

    proxy_url = f"http://{resolve_proxy_host(args.burp_host)}:{args.burp_port}"

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
    params = args.param or ",".join(PARAMS)
    if params:
        sqlmap_args += ["-p", params]
    if dbms:
        sqlmap_args += ["--dbms", dbms]
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
        description="Detection-only sqlmap wrapper (Docker + Burp). "
                    "Defaults come from the CONFIG block; flags override.",
        epilog="Extra sqlmap flags go after `--`.",
    )
    p.add_argument("request", nargs="?", default=None, help="Request file override.")
    p.add_argument("-u", "--url", default="", help="URL override.")
    p.add_argument("-p", "--param", default="", help="Param override (comma list).")
    p.add_argument("--dbms", default="", help="Single DBMS override.")
    p.add_argument("--image", default=IMAGE)
    p.add_argument("--sqlmap-bin", default="")
    p.add_argument("--burp-host", default=BURP_HOST)
    p.add_argument("--burp-port", default=BURP_PORT)
    p.add_argument("--technique", default=TECHNIQUE)
    p.add_argument("--scope", default=SCOPE, choices=SCOPE_TO_LEVEL.keys(),
                   help="Where to test: URL_BODY | COOKIE | HEADER (cumulative).")
    p.add_argument("--level", type=int, default=None, choices=range(1, 6),
                   help="Raw sqlmap level; overrides --scope if given.")
    p.add_argument("--risk", type=int, default=RISK, choices=range(1, 4))
    p.add_argument("-v", "--verbosity", type=int, default=3, choices=range(0, 7))
    p.add_argument("--https", dest="https", action="store_true", default=FORCE_HTTPS)
    p.add_argument("--no-https", dest="https", action="store_false")
    p.add_argument("--flush-session", action="store_true")
    p.add_argument("--oob-domain", default="")
    p.add_argument("--dry-run", action="store_true")

    argv = sys.argv[1:]
    if "--" in argv:
        idx = argv.index("--")
        pre, passthrough = argv[:idx], argv[idx + 1:]
    else:
        pre, passthrough = argv, []
    args = p.parse_args(pre)
    if args.level is None:
        args.level = SCOPE_TO_LEVEL[args.scope]
    args.passthrough = passthrough
    return args


def main():
    args = parse_args()

    dbms_list = [args.dbms] if args.dbms else (DBMS or [""])

    if not args.dry_run:
        check_docker()
        ensure_image(args.image)

    last_rc = 0
    output_host_dir = None
    for dbms in dbms_list:
        label = dbms or "auto"
        print(f"\n===== DBMS: {label} =====")
        command, output_host_dir = build_command(args, dbms)
        print(f"[*] Command:\n    {' '.join(command)}\n")
        if args.dry_run:
            continue
        print("[*] Running sqlmap (detection only)...\n")
        last_rc = subprocess.run(command).returncode

    if args.dry_run:
        print("[*] --dry-run set; not executing.")
        return

    print()
    print("[+] sqlmap finished." if last_rc == 0
          else f"[!] sqlmap exited with code {last_rc}.")
    print(f"[*] Log and payloads saved under:\n    {output_host_dir}")
    sys.exit(last_rc)


if __name__ == "__main__":
    main()
