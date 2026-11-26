"""Đếm quy tắc có nguyên tử mang phủ định trong TÊN mà còn bị phủ định bằng cờ neg (dấu hiệu phủ định kép làm ngược nghĩa quy tắc).
Số đo chuẩn bị cho lần sửa 4 (chưa chạy, xem báo cáo docs/run_reports_ckey/ckey_kb_report.md mục 4). Danh sách từ do agent tự đặt,
nên kết quả phải đọc tay đối chiếu.
Chạy ở gốc repo: python -X utf8 -I utils/llm_runs/count_inverted_negation.py <run>   (đọc rules gốc và update_rules của tập con lldnn)"""
import json, re, sys
run = sys.argv[1]
P = f"data/processed_subset/lldnn/processed_{run}"
NEG = re.compile(r"(^|_)(lack|refuse|refusal|denial|deny|fall_short|differ|differs|maximum|max|not|no|without|non|fail|unable|exceed|insufficient|failure|unfilled|absence|absent)(_|$)")
seen, hits = set(), []
for fn in (f"{P}/rules/rules_BLLD_45-2019.jsonl", f"{P}/update/update_rules.jsonl"):
    for l in open(fn, encoding="utf-8"):
        r = json.loads(l); rr = r.get("rule", r)
        atoms = [("head", rr["head"])] + [("body", b) for b in rr["body"]]
        for where, a in atoms:
            if a.get("neg") and NEG.search(a["atom"]):
                k = (rr["unit"], where, a["atom"])
                if k not in seen:
                    seen.add(k); hits.append(k)
print(f"run {run}: {len(hits)} nguyên tử phủ định trong tên mà neg=True")
for h in hits:
    print("   ", *h)
