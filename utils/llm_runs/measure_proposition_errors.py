"""Đo lỗi 1.6A của một lần chạy trên tập con lldnn (định nghĩa chốt TRƯỚC khi chạy ckey2, A50).
Chạy ở gốc repo: python -X utf8 -I utils/llm_runs/measure_proposition_errors.py <run>   (đọc data/llm_cache/propositions/*.lldnn.<run>.json và ku/*.lldnn.<run>.json)
M1  mục con của câu dẫn yêu cầu ("phải đáp ứng / phải có đủ / phải tuân theo ... sau đây"): bao nhiêu mục có dòng menh_de vai ket_luan.
M2  câu dẫn lọt: menh_de chứa "sau đây" / "như sau" / "gồm" ở cuối (đếm máy; đọc tay ghi riêng).
M4  phủ định kép: menh_de bắt đầu "không"/"chưa" mà cuc = phu_dinh.
Lỗi cổng (M3 là 1.9, đọc ở báo cáo answering) lấy từ trường lỗi cổng của cache nếu có."""
import glob
import json
import re
import sys
from collections import Counter

run = sys.argv[1]
units = {}
for f in glob.glob(f"data/llm_cache/propositions/*.lldnn.{run}.json") + glob.glob(f"data/llm_cache/propositions/ku/*.lldnn.{run}.json"):
    d = json.load(open(f, encoding="utf-8"))
    units.update(d["units"])

LEAD = re.compile(r"phải\s+(đáp ứng|có đủ|tuân theo)[^:]{0,60}sau đây\s*:?\s*$", re.I)
parents = [u for u, rec in units.items() if any(LEAD.search(" ".join(r.get("trich") or [])) for r in rec["dong"])]
m1_tot = m1_ok = 0
detail = []
for p in parents:
    kids = [u for u in units if u.startswith(p + ".") and u.count(".") == p.count(".") + 1]
    for k in kids:
        rows = [r for r in units[k]["dong"] if r.get("loai") == "menh_de"]
        ok = any(r.get("vai") == "ket_luan" for r in rows)
        m1_tot += 1
        m1_ok += ok
        detail.append((k, [r.get("vai") for r in rows]))

leak = [(u, r["menh_de"]) for u, rec in units.items() for r in rec["dong"]
        if r.get("loai") == "menh_de" and re.search(r"(sau đây|như sau|\bgồm)\s*$", r.get("menh_de") or "")]
dneg = [(u, r["menh_de"]) for u, rec in units.items() for r in rec["dong"]
        if r.get("loai") == "menh_de" and r.get("cuc") == "phu_dinh" and re.match(r"(không|chưa)\b", (r.get("menh_de") or "").strip().lower())]
gate, gate_units = Counter(), 0
for u, rec in units.items():
    errs = rec.get("loi") or []
    gate_units += bool(errs)
    for e in errs:
        s = e[1] if isinstance(e, list) and len(e) > 1 else str(e)
        gate[re.split(r"[:'\"{(\d]", s, maxsplit=1)[0].strip()[:50]] += 1
n_rows = sum(len(rec["dong"]) for rec in units.values())
print(f"run {run}: {len(units)} đơn vị, {n_rows} dòng")
print(f"M1 câu dẫn yêu cầu: {len(parents)} cha {parents}; mục con có ket_luan {m1_ok}/{m1_tot}")
for k, v in detail:
    print("   ", k, v)
print(f"M2 câu dẫn lọt (máy): {len(leak)}")
for x in leak:
    print("   ", x)
print(f"lỗi cổng: {sum(gate.values())} lỗi ở {gate_units} đơn vị")
for k, v in gate.most_common(12):
    print(f"    {v:3d}  {k}")
print(f"M4 phủ định kép: {len(dneg)}")
for x in dneg[:10]:
    print("   ", x)
