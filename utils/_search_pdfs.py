import glob, os, re, sys

# 1) Ensure all three PDFs are extracted.
sys.path.insert(0, "/mnt/e/KLTN")
import _pdftext as P

papers = glob.glob("/mnt/e/KLTN/docs/papers/*.pdf")
for p in papers:
    out = "/tmp/_p_" + os.path.splitext(os.path.basename(p))[0].replace(" ", "_").replace("(", "").replace(")", "") + ".txt"
    if not os.path.exists(out) or os.path.getsize(out) == 0:
        t = P.extract_text_from_pdf(p)
        open(out, "w", encoding="utf-8").write(t)
    print(os.path.basename(p), "->", out, os.path.getsize(out), "chars")

# 2) Search key terms with context.
TERMS = [
    "state transition", "state distance", "verifier feedback", "precondition",
    "detailed feedback", "PDDL", "reachability", "reward margin", "abstention",
    "Benjamini", "Pareto", "FDR", "extraction", "action", "goal",
]
findings = {}
for p in glob.glob("/tmp/_p_*.txt"):
    text = open(p, encoding="utf-8").read()
    name = os.path.basename(p)
    for t in TERMS:
        for m in re.finditer(re.escape(t), text, re.I):
            s = max(0, m.start() - 120)
            e = min(len(text), m.end() + 160)
            ctx = text[s:e].replace("\n", " ")
            findings.setdefault(t, []).append((name, ctx))

for t in TERMS:
    hits = findings.get(t, [])
    print(f"\n\n########## {t}  ({len(hits)} hits) ##########")
    for name, ctx in hits[:4]:
        print(f"--[{name}]-- {ctx}")