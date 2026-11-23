import os, sys, importlib

PDFS = [
    "/mnt/e/KLTN/docs/papers/2509.13351v1.pdf",
    "/mnt/e/KLTN/docs/papers/DRAFT_PAPER_METHODS_LATEX.pdf",
    "/mnt/e/KLTN/docs/papers/SOICT2026_Grounded_DPO_SLM_camera_ready_v2 (2).pdf",
]

# Detect available extractor
extractor = None
for mod, fn in [
    ("fitz", "pymupdf"),
    ("pypdf", "pypdf"),
    ("PyPDF2", "pypdf2"),
    ("pdfminer", "pdfminer"),
]:
    try:
        importlib.import_module(mod)
        extractor = fn
        break
    except Exception:
        continue

print("extractor:", extractor)

def extract_text(path):
    if extractor == "pymupdf":
        import fitz
        doc = fitz.open(path)
        return "\n\n".join(page.get_text() for page in doc)
    if extractor == "pypdf":
        from pypdf import PdfReader
        r = PdfReader(path)
        return "\n\n".join(p.extract_text() or "" for p in r.pages)
    if extractor == "pypdf2":
        import PyPDF2
        r = PyPDF2.PdfReader(path)
        return "\n\n".join(p.extract_text() or "" for p in r.pages)
    if extractor == "pdfminer":
        from pdfminer.high_level import extract_text as et
        return et(path)
    return None

for i, p in enumerate(PDFS, 1):
    name = os.path.splitext(os.path.basename(p))[0]
    try:
        txt = extract_text(p)
        out = f"/tmp/pdf_{i}_{i}.txt"
        with open(out, "w", encoding="utf-8") as f:
            f.write(txt or "")
        print(f"{p} -> {out} ({len(txt or '')} chars)")
    except Exception as e:
        print(f"{p} -> ERROR: {e!r}")