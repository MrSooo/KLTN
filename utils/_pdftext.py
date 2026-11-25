import re, zlib, sys

def extract_text_from_pdf(path):
    data = open(path, "rb").read()
    # Split into objects
    out = []
    # Find stream...endstream blocks inside obj...endobj
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", data, re.S):
        raw = m.group(1)
        # strip trailing newline before endstream
        raw = raw.rstrip(b"\r\n")
        # filters
        decoded = None
        if b"FlateDecode" in data[max(0, m.start()-200):m.start()]:
            try:
                decoded = zlib.decompress(raw)
            except Exception:
                decoded = raw
        else:
            decoded = raw
        if decoded is None:
            continue
        # extract text-showing operators
        txt = extract_ops(decoded)
        if txt:
            out.append(txt)
    return "\n".join(out)


def extract_ops(content):
    # Decode as latin-1 to keep byte->char 1:1 for regex work
    s = content.decode("latin-1", errors="replace")
    chunks = []
    # TJ arrays: [(text) -300 (text) ...] TJ
    for arr in re.finditer(r"\[(.*?)\]\s*TJ", s, re.S):
        inner = arr.group(1)
        for part in re.finditer(r"\(((?:[^()\\]|\\.)*)\)", inner):
            chunks.append(decode_pdf_str(part.group(1)))
    s2 = re.sub(r"\[(.*?)\]\s*TJ", "", s, flags=re.S)
    # Tj: (text) Tj
    for m in re.finditer(r"\(((?:[^()\\]|\\.)*)\)\s*T[jJ]", s2):
        chunks.append(decode_pdf_str(m.group(1)))
    # quotes: (text) ' and (text) "
    for m in re.finditer(r"\(((?:[^()\\]|\\.)*)\)\s*['\"]", s2):
        chunks.append(decode_pdf_str(m.group(1)))
    return "".join(chunks)


def decode_pdf_str(s):
    # unescape common PDF escapes
    s = s.replace(r"\(", "(").replace(r"\)", ")").replace(r"\\", "\\")
    # octal escapes \ddd
    s = re.sub(r"\\([0-7]{1,3})", lambda m: chr(int(m.group(1), 8)), s)
    return s


if __name__ == "__main__":
    for src in sys.argv[1:]:
        try:
            t = extract_text_from_pdf(src)
            import os
            name = os.path.basename(src)
            out = "/tmp/" + name.replace(" ", "_").replace("(", "").replace(")", "") + ".txt"
            with open(out, "w", encoding="utf-8") as f:
                f.write(t)
            print(f"{name} -> {out} ({len(t)} chars)")
        except Exception as e:
            print(f"{name} -> ERROR {e!r}")