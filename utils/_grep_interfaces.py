import re
for path in ["/mnt/e/KLTN/src/validation.py", "/mnt/e/KLTN/src/graph.py"]:
    print("=" * 40, path)
    txt = open(path, encoding="utf-8").read()
    for i, ln in enumerate(txt.splitlines(), 1):
        if re.search(r"class (Check|Expect|Graph|EdgeSet)|def (check_graph|graph_base|graph_at|check_codes|check_parents|check_duplicate_edges)|Check\(|def verdict|def failures", ln):
            print(f"{i}: {ln[:140]}")