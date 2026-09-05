#!/usr/bin/env python3
"""
Ruby Marshal DESERIALIZER (via Docker)
=======================================
Toma un base64, lo Marshal.load DENTRO de un contenedor efimero y te muestra
el objeto reconstruido (clase + variables de instancia + inspect).

AISLAMIENTO: el load corre en un contenedor descartable (--rm --network none).
Si el base64 fuera un gadget RCE, el comando se ejecutaria SOLO adentro del
contenedor (sandbox), nunca en tu Windows.

De donde saca el base64 (en orden de prioridad):
  1) argumento de linea de comandos:  python deserialize.py <base64>
  2) la variable BASE64 de abajo
  3) el portapapeles

Uso:   python deserialize.py
"""

import subprocess
import sys
import os
import time

# ============ EDITAR ACA ============
BASE64     = "BAhvOglVc2VyBzoOQHVzZXJuYW1lSSILd2llbmVyBjoGRUY6EkBhY2Nlc3NfdG9rZW5JIiVpZTY5Z2dvdXF0dTY3MjAycHJydHhyZHJ1cmh1amRxcAY7B0YK"
RUBY_IMAGE = "ruby:3.0-slim"           # usa la MISMA version con la que se serializo
# ====================================

HERE = os.path.dirname(os.path.abspath(__file__))
DOCKER_DESKTOP = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"

# Loader Ruby: define al vuelo cualquier clase/modulo que falte (p. ej. User del target)
# y reintenta, asi Marshal.load no explota por "undefined class/module".
RUBY_LOADER = r'''
require "base64"
require "rubygems" rescue nil
require "net/protocol" rescue nil

def ensure_const(name)
  ns = Object
  name.split("::").each do |p|
    ns = ns.const_defined?(p, false) ? ns.const_get(p, false) : ns.const_set(p, Class.new)
  end
end

data = Base64.strict_decode64(File.read("/work/_payload.b64").strip)
STDERR.puts "[bytes] #{data.bytesize}"
begin
  obj = Marshal.load(data)
  STDERR.puts "[clase]  #{obj.class}"
  obj.instance_variables.each do |iv|
    STDERR.puts "  #{iv} = #{obj.instance_variable_get(iv).inspect}"
  end
  STDERR.puts "[inspect] #{obj.inspect}"
rescue ArgumentError => e
  m = e.message[/undefined class\/module ([\w:]+)/, 1]
  if m
    STDERR.puts "[auto] definiendo clase faltante: #{m}"
    ensure_const(m)
    retry
  end
  STDERR.puts "[error] #{e.class}: #{e.message}"
rescue => e
  STDERR.puts "[error] #{e.class}: #{e.message}"
end
'''


def docker_ok() -> bool:
    return subprocess.run(
        ["docker", "info"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0


def ensure_docker() -> bool:
    if docker_ok():
        return True
    print("[*] Docker no responde. Levantando Docker Desktop...")
    try:
        subprocess.Popen([DOCKER_DESKTOP])
    except FileNotFoundError:
        pass
    for _ in range(60):
        time.sleep(2)
        if docker_ok():
            return True
    return False


def get_clipboard() -> str:
    """Lee el portapapeles de Windows via PowerShell."""
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "Get-Clipboard"],
            capture_output=True, text=True,
        )
        return r.stdout.strip()
    except Exception:
        return ""


def resolve_base64() -> str:
    if len(sys.argv) > 1 and sys.argv[1].strip():
        return sys.argv[1].strip()
    if BASE64.strip():
        return BASE64.strip()
    return get_clipboard()


def main() -> int:
    b64 = resolve_base64()
    if not b64:
        print("[X] No hay base64 (ni argumento, ni variable, ni portapapeles).")
        return 1

    if not ensure_docker():
        print("[X] Docker no arranco. Abri Docker Desktop a mano y volve a correr.")
        return 1
    print(f"[+] Docker OK  (imagen: {RUBY_IMAGE})")

    # El base64 y el loader se pasan por archivos montados (nada por argumentos)
    b64_path = os.path.join(HERE, "_payload.b64")
    rb_path = os.path.join(HERE, "_load.rb")
    with open(b64_path, "w", encoding="ascii", newline="") as f:
        f.write(b64)
    with open(rb_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(RUBY_LOADER)

    print("[*] Deserializando en contenedor efimero (sandbox)...")
    print("=================== RESULTADO ===================")
    try:
        subprocess.run(
            ["docker", "run", "--rm", "--network", "none",
             "-v", f"{HERE}:/work", "-w", "/work",
             RUBY_IMAGE, "ruby", "/work/_load.rb"],
        )
    finally:
        for p in (b64_path, rb_path):
            try:
                os.remove(p)
            except OSError:
                pass
    print("================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
