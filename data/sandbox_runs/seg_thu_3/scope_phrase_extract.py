"""Trích mọi đoạn `menh_de` có "đối với" (không phân biệt hoa thường) từ phản hồi lượt 1.

Dùng để đếm E4 (24/11). Cột nhóm A1/A2/B/C/N trong `scope_phrase_labels.tsv` do agent đọc tay,
không do script này sinh. Chạy: python -I -X utf8 scope_phrase_extract.py phan_hoi > out.tsv
"""
import json, re, sys, pathlib
d = pathlib.Path(sys.argv[1])
cau_n = seg_n = 0
for f in sorted(d.glob("*.json")):
    j = json.loads(f.read_text(encoding="utf-8"))
    t = j["phan_hoi"]["content"][0]["text"]
    m = re.search(r"\{.*\}", t, re.S)
    try: doan = json.loads(m.group(0))["doan"]
    except Exception: continue
    hits = [x for x in doan if x.get("loai") == "menh_de" and "đối với" in x["chu"].lower()]
    if hits:
        cau_n += 1
        for x in hits:
            seg_n += 1
            print(f"{f.stem}\t{x['id']}\t{x['chu']}")
print("CAU", cau_n, "DOAN", seg_n, file=sys.stderr)
