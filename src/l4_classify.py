"""L4: gắn mỗi Điều một nhãn để biết nó đi tiếp tới bước nào (trích quy tắc, chỉ thị hiệu lực, chỉ giữ chữ ...).

Chạy: python -I src/l4_classify.py       (cả kho; cần a1)
Đầu ra: data/processed/l4/l4_labels.jsonl  {id, label, how, heading, flags}; docs/bao_cao_chay/l4/l4_report.txt.

Nhãn: substantive (điều có điều kiện, quyền, nghĩa vụ, mức, thời hạn, ngoại lệ, chế tài) | definition | effect_transition (hiệu lực,
chuyển tiếp, bãi bỏ, và các Điều "Sửa đổi, bổ sung ..." của văn bản sửa đổi: nguồn câu chỉ thị cho L6) | procedural (hồ sơ, trình tự,
thủ tục) | authority (trách nhiệm, thẩm quyền cơ quan) | appendix (phụ lục) .
Mọi Điều vẫn nằm trong KB, vẫn có phiên bản và là đích sửa đổi được; nhãn chỉ quyết định Điều đó có được dịch thành quy tắc không.

Cách xếp: regex trên tiêu đề trước (how=regex). Điều không khớp mẫu nào cần LLM phân loại theo lô (plan L4); khi chưa chạy LLM thì giữ
tạm nhãn substantive (an toàn hơn: không bỏ sót quy tắc) với how=default_pending_llm và cờ llm_pending, báo cáo đếm riêng.
"""
import collections
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import a1_parse as a1
import corpus

L4_DIR_NAME = "l4"

RULES = [  # (nhãn, regex trên tiêu đề, theo thứ tự ưu tiên)
    ("definition", re.compile(r"^Giải thích từ ngữ", re.I)),
    ("effect_transition", re.compile(r"^(?:Hiệu lực(?: thi hành)?|Quy định chuyển tiếp|Điều khoản chuyển tiếp|Điều khoản thi hành|Bãi bỏ|"
                                      r"Sửa đổi, bổ sung|Sửa đổi|Bổ sung|Thay thế|Hết hiệu lực|Áp dụng pháp luật)", re.I)),
    # "Trách nhiệm" chỉ là authority khi chủ thể là cơ quan, tổ chức nhà nước; "Trách nhiệm khi chấm dứt hợp đồng lao động" là nghĩa vụ của các bên.
    ("authority", re.compile(r"^(?:Trách nhiệm của (?:các )?(?:Bộ|cơ quan|Ủy ban|Sở|Chính phủ|Thủ tướng|Tổng liên đoàn|UBND|tổ chức có thẩm quyền)|"
                             r"Trách nhiệm (?:thi hành|quản lý nhà nước)|Thẩm quyền|Nhiệm vụ|Quyền hạn|Tổ chức thực hiện|Cơ quan)", re.I)),
    ("procedural", re.compile(r"^(?:Hồ sơ|Trình tự|Thủ tục|Cách thức|Tiếp nhận|Nộp hồ sơ|Thời hạn giải quyết|Quy trình)", re.I)),
]


def classify_heading(heading):
    """-> (nhãn, how). Không khớp mẫu nào thì nhãn tạm substantive, how=default_pending_llm."""
    for label, rx in RULES:
        if rx.match(heading or ""):
            return label, "regex"
    return "substantive", "default_pending_llm"


def main():
    docs = corpus.load_manifest()
    rows = []
    for doc_id in docs:
        units = a1.load_units(doc_id)
        for uid, u in units.items():
            if u["type"] == "dieu":
                label, how = classify_heading(u.get("heading", ""))
                rows.append({"id": uid, "label": label, "how": how, "heading": u.get("heading", ""),
                             "flags": ["llm_pending"] if how == "default_pending_llm" else []})
            elif u["type"] == "pl":
                rows.append({"id": uid, "label": "appendix", "how": "type", "heading": u.get("heading") or "", "flags": []})
    a1.write_jsonl(corpus.out_dir(L4_DIR_NAME) / "l4_labels.jsonl", rows)

    report = ["L4 báo cáo", f"tổng Điều/phụ lục có nhãn: {len(rows)}"]
    by_doc = collections.defaultdict(collections.Counter)
    for r in rows:
        by_doc[r["id"].split(".")[0]][r["label"]] += 1
    report.append("phân bố nhãn theo văn bản:")
    report += [f"  {d:<22} {dict(c)}" for d, c in by_doc.items()]
    n_regex = sum(1 for r in rows if r["how"] == "regex")
    n_def = sum(1 for r in rows if r["how"] == "default_pending_llm")
    report.append(f"xếp bằng regex: {n_regex}; chưa xếp được (nhãn tạm substantive, chờ LLM): {n_def}; phụ lục: {sum(1 for r in rows if r['how'] == 'type')}")
    sample = random.Random(20261109).sample([r for r in rows if r["label"] != "appendix"], 10)
    report.append("10 Điều mẫu ngẫu nhiên (hạt giống cố định):")
    report += [f"  {r['id']:<34} {r['label']:<18} {r['how']:<20} {r['heading'][:60]}" for r in sample]
    path = corpus.report_dir(L4_DIR_NAME) / "l4_report.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(report) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(report))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()
