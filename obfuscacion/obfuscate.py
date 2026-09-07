#!/usr/bin/env python3
"""Ofusca un payload aplicando una lista ORDENADA de encodings (cada uno recibe
la salida del anterior). Pensado para saltar filtros/WAF en XSS, SQLi, XXE, etc.

Uso:
    python obfuscate.py "alert(1)" hex url          # aplica hex, luego url
    python obfuscate.py "alert(1)" --enc hex,url    # equivalente (coma)
    python obfuscate.py "<img src=x>" url url        # doble URL encoding
    python obfuscate.py "alert(1)" hex --special     # solo caracteres peligrosos
    python obfuscate.py -l                            # lista los encodings
"""
import base64
import sys

# En modo --special solo se codifican estos chars (el resto queda legible).
SPECIAL = set("()[]{}<>'\"=;:/\\`$&,. ")
_ONLY_SPECIAL = False


def should(c):
    return (c in SPECIAL) if _ONLY_SPECIAL else True


# --- ENCODERS (str -> str). Anade el tuyo aqui y registralo en ENCODERS -----
def url(s):                     # %XX por byte UTF-8   (<  -> %3C)
    return "".join("".join(f"%{b:02X}" for b in c.encode()) if should(c) else c
                   for c in s)


def double_url(s):              # URL encoding x2       (<  -> %253C)
    return "".join("%25" if ch == "%" else ch for ch in url(s))


def html_dec(s):                # entidad decimal       (:  -> &#58;)
    return "".join(f"&#{ord(c)};" if should(c) else c for c in s)


def html_hex(s):                # entidad hex           (:  -> &#x3a;)  (= XML)
    return "".join(f"&#x{ord(c):x};" if should(c) else c for c in s)


def js_unicode(s):              # \uNNNN                 (:  -> :)
    out = []
    for c in s:
        if not should(c):
            out.append(c); continue
        cp = ord(c)
        if cp > 0xFFFF:         # fuera del BMP -> par surrogate
            cp -= 0x10000
            out.append(f"\\u{0xD800 + (cp >> 10):04x}\\u{0xDC00 + (cp & 0x3FF):04x}")
        else:
            out.append(f"\\u{cp:04x}")
    return "".join(out)


def js_unicode_es6(s):          # \u{NN} (ES6)           (:  -> \u{3a})
    return "".join(f"\\u{{{ord(c):x}}}" if should(c) else c for c in s)


def js_hex(s):                  # \xNN por byte          (a  -> \x61)
    return "".join("".join(f"\\x{b:02x}" for b in c.encode()) if should(c) else c
                   for c in s)


def js_octal(s):                # \NNN octal por byte    (a  -> \141)
    return "".join("".join(f"\\{b:o}" for b in c.encode()) if should(c) else c
                   for c in s)


def b64(s):                     # base64 (envolver con atob(...) al usar)
    return base64.b64encode(s.encode()).decode()


def sql_char(s):                # CHAR(83)+CHAR(69)...   (para SQLi sin comillas)
    return "+".join(f"CHAR({ord(c)})" for c in s)


ENCODERS = {
    "url": url, "url-encoding": url,
    "double-url": double_url, "double-url-encoding": double_url,
    "html": html_dec, "html-decimal": html_dec,
    "html-hex": html_hex, "xml": html_hex, "xml-hex": html_hex,
    "unicode": js_unicode, "unicode-es6": js_unicode_es6,
    "hex": js_hex, "octal": js_octal,
    "base64": b64,
    "sql-char": sql_char,
}

# nombre canonico -> (descripcion, ejemplo) para el listado -l
DESC = {
    "url":         ("URL encoding  %XX",            "<  -> %3C"),
    "double-url":  ("URL encoding x2",              "<  -> %253C"),
    "html":        ("entidad HTML decimal",         ":  -> &#58;"),
    "html-hex":    ("entidad HTML/XML hex",         ":  -> &#x3a;"),
    "unicode":     ("escape JS \\uNNNN",            "a  -> \\u0061"),
    "unicode-es6": ("escape JS \\u{NN} (ES6)",      "a  -> \\u{61}"),
    "hex":         ("escape JS \\xNN por byte",     "a  -> \\x61"),
    "octal":       ("escape octal \\NNN por byte",  "a  -> \\141"),
    "base64":      ("base64 (envolver con atob)",   "->  YWxlcnQoMSk="),
    "sql-char":    ("CHAR(n)+CHAR(n)... (SQLi)",    "S  -> CHAR(83)"),
}


def main():
    args = sys.argv[1:]
    global _ONLY_SPECIAL
    if not args or args[0] in ("-l", "--list", "-h", "--help"):
        print("encodings disponibles:")
        for name, (desc, ex) in DESC.items():
            print(f"  {name:<13}{desc:<28}{ex}")
        print('\nuso: python obfuscate.py "PAYLOAD" enc1 enc2 ...  [--special]')
        return

    if "--special" in args:
        _ONLY_SPECIAL = True
        args = [a for a in args if a != "--special"]

    payload = args[0]
    chain = []
    for a in args[1:]:
        chain += [x for x in a.split(",") if x]  # admite --enc a,b y a b

    cur = payload
    print(f"[in]  {cur}")
    for name in chain:
        fn = ENCODERS.get(name.strip().lower())
        if not fn:
            sys.exit(f"[!] encoding desconocido: '{name}'  (usa -l para listar)")
        cur = fn(cur)
        print(f"[{name}]  {cur}")
    print(f"\n{cur}")


if __name__ == "__main__":
    main()
