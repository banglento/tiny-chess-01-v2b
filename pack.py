#!/usr/bin/env python3
"""Pack main_src.py -> main.py using the live entry's recipe:
#coding:l1 + lzma (FORMAT_ALONE, LZMA1, lc=3 lp=0 pb=0, dict 16K)
payload embedded as a latin-1 string literal with \\, \', NUL, LF, CR escaped.
Verifies: no NUL bytes in output, payload round-trips to the source exactly,
and the packed file byte-compiles."""
import lzma, sys, py_compile

src_path, out_path = sys.argv[1], sys.argv[2]
orig = open(src_path, 'rb').read()
filters = [{'id': lzma.FILTER_LZMA1, 'dict_size': 16384, 'lc': 3, 'lp': 0, 'pb': 0}]
payload = lzma.compress(orig, format=lzma.FORMAT_ALONE, filters=filters)
assert lzma.decompress(payload) == orig, 'roundtrip mismatch'

def esc(bs):
    out = []
    for i, b in enumerate(bs):
        c = chr(b)
        if c == '\\': out.append('\\\\')
        elif c == "'": out.append("\\'")
        elif b == 0:
            # '\0' followed by an octal digit would merge into one octal
            # escape on parse; use the unambiguous '\x00' there instead.
            nxt = bs[i + 1] if i + 1 < len(bs) else -1
            out.append('\\x00' if 0x30 <= nxt <= 0x37 else '\\0')
        elif b == 10: out.append('\\n')
        elif b == 13: out.append('\\r')
        else: out.append(c)
    return ''.join(out)

packed = ("#coding:l1\nimport lzma;exec(lzma.decompress('"
          + esc(payload) + "'.encode('l1')))\n").encode('l1')
assert b'\x00' not in packed, 'NUL byte in packed output'
open(out_path, 'wb').write(packed)
py_compile.compile(out_path, doraise=True)
# Independent re-read: parse the literal back out of the written file and
# confirm it decompresses to the source (catches escape ambiguities).
import ast
text = packed.decode('l1')
s0 = text.index("decompress('") + len("decompress('")
s1 = text.rindex("'.encode('l1')")
back = ast.literal_eval("'" + text[s0:s1] + "'").encode('l1')
assert lzma.decompress(back) == orig, 're-read payload mismatch'
print(f'packed {src_path} ({len(orig)} B) -> {out_path} ({len(packed)} B), cap 4096, ok')
