"""Bước 1.4: gắn mỗi Điều một nhãn để biết nó đi tiếp tới bước nào (trích quy tắc, chỉ thị hiệu lực, chỉ giữ chữ ...).

Chạy: python -I src/article_type.py       (cả kho; cần bước parse)
Đầu ra: data/processed/l4/l4_labels.jsonl  {id, label, how}; docs/bao_cao_chay/l4/l4_report.txt.

Nhãn: substantive (điều có điều kiện, quyền, nghĩa vụ, mức, thời hạn, ngoại lệ, chế tài) | definition | effect_transition (hiệu lực,
chuyển tiếp, bãi bỏ, và các Điều "Sửa đổi, bổ sung ..." của văn bản sửa đổi: nguồn câu chỉ thị cho L6) | procedural (hồ sơ, trình tự,
thủ tục) | authority (trách nhiệm, thẩm quyền cơ quan) | appendix (phụ lục).
Mọi Điều vẫn nằm trong KB, vẫn có phiên bản và là đích sửa đổi được; nhãn chỉ quyết định Điều đó có được dịch thành quy tắc không.

Cách xếp: regex trên TIÊU ĐỀ (how=regex). Điều không khớp mẫu nào mang nhãn substantive, how=default. Đó là mặc định an toàn: nhãn sai ở
hướng ngược lại (đẩy một Điều có điều kiện thật ra khỏi substantive) làm mất quy tắc, còn để thừa một Điều thủ tục ở substantive chỉ tốn
công ở bước trích quy tắc, và bước đó có cổng kiểm riêng. Phụ lục: nhãn appendix, how=type.

KHÔNG dùng LLM (quyết định A14, docs/quyet_dinh/pipeline_moi_quyet_dinh.txt). Bản cũ gọi LLM cho các Điều không khớp mẫu và dùng model
thứ hai kiểm: LLM kiểm LLM không chứng minh được đúng sai, và đo thực tế trên 18 văn bản thì trong 742 Điều không khớp mẫu, LLM chỉ đổi nhãn 93 Điều,
không Điều nào thành effect_transition (nguồn của bước đọc chỉ thị).
"""
import collections
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import parse as l1
import corpus

L4_DIR_NAME = "l4"

# Danh từ chỉ đơn vị pháp luật hoặc văn bản. Đứng sau "Sửa đổi, bổ sung" hay "Hiệu lực của" thì tiêu đề nói về chính văn bản luật (chỉ thị
# sửa đổi, hiệu lực của luật). Thiếu danh từ này ("Sửa đổi, bổ sung hợp đồng lao động", "Hiệu lực của nội quy lao động") thì đó là quy tắc
# thường về hợp đồng, thỏa ước, nội quy: nếu xếp effect_transition thì Điều bị đẩy khỏi substantive và mất quy tắc (A21).
_LEGAL_NOUN = (r"(?:điều|khoản|điểm|mục|chương|phụ[ ]+lục|danh[ ]+mục|quy[ ]+định|nghị[ ]+định|thông[ ]+tư|luật|bộ[ ]+luật|"
               r"nghị[ ]+quyết|quyết[ ]+định|văn[ ]+bản)(?!\w)")

RULES = [  # (nhãn, regex trên tiêu đề, theo thứ tự ưu tiên)
    ("definition", re.compile(r"^Giải thích từ ngữ", re.I)),
    ("effect_transition", re.compile(
        rf"^(?:Hiệu lực(?![ ]+của[ ]+(?!{_LEGAL_NOUN}))(?![ ]+và[ ]+thời[ ]+hạn)|"
        r"Quy định chuyển tiếp|Điều khoản chuyển tiếp|Điều khoản thi hành|Bãi bỏ|Hết hiệu lực|Áp dụng pháp luật|"
        rf"(?:Sửa đổi, bổ sung|Sửa đổi|Bổ sung|Thay thế)[ ]+(?:(?:một[ ]+số|các|toàn[ ]+bộ)[ ]+)?{_LEGAL_NOUN})", re.I)),
    # "Trách nhiệm" chỉ là authority khi chủ thể là cơ quan, tổ chức nhà nước; "Trách nhiệm khi chấm dứt hợp đồng lao động" là nghĩa vụ của các bên.
    # "Thẩm quyền giao kết hợp đồng lao động" (ai được ký hợp đồng) là quy tắc của các bên, không phải thẩm quyền cơ quan; loại riêng.
    # "Thẩm quyền tuyên bố ... vô hiệu" (Tòa án) vẫn là authority.
    ("authority", re.compile(r"^(?:Trách nhiệm của (?:các )?(?:Bộ|cơ quan|Ủy ban|Sở|Chính phủ|Thủ tướng|Tổng liên đoàn|UBND|tổ chức có thẩm quyền)|"
                             r"Trách nhiệm (?:thi hành|quản lý nhà nước)|Thẩm quyền(?![ ]+giao[ ]+kết)|Nhiệm vụ|Quyền hạn|Tổ chức thực hiện|Cơ quan)", re.I)),
    ("procedural", re.compile(r"^(?:Hồ sơ|Trình tự|Thủ tục|Cách thức|Tiếp nhận|Nộp hồ sơ|Thời hạn giải quyết|Quy trình)", re.I)),
]


def classify_heading(heading):
    """-> (nhãn, how). Không khớp mẫu nào thì substantive, how=default."""
    for label, rx in RULES:
        if rx.match(heading or ""):
            return label, "regex"
    return "substantive", "default"


def build_rows(docs):
    """-> (rows {id, label, how}, headings {id: tiêu đề}). Tiêu đề chỉ để in mẫu ở báo cáo, không ghi vào dòng nhãn (không bước nào đọc)."""
    rows, headings = [], {}
    for doc_id in docs:
        for uid, u in l1.load_units(doc_id).items():
            if u["type"] == "dieu":
                label, how = classify_heading(u.get("heading", ""))
                rows.append({"id": uid, "label": label, "how": how})
                headings[uid] = u.get("heading", "")
            elif u["type"] == "pl":
                rows.append({"id": uid, "label": "appendix", "how": "type"})
                headings[uid] = u.get("heading") or ""
    return rows, headings


def main():
    rows, headings = build_rows(corpus.load_manifest())
    l1.write_jsonl(corpus.out_dir(L4_DIR_NAME) / "l4_labels.jsonl", rows)

    report = ["L4 báo cáo", f"tổng Điều/phụ lục có nhãn: {len(rows)}"]
    by_doc = collections.defaultdict(collections.Counter)
    for r in rows:
        by_doc[r["id"].split(".")[0]][r["label"]] += 1
    report.append("phân bố nhãn theo văn bản:")
    report += [f"  {d:<22} {dict(c)}" for d, c in by_doc.items()]
    how = collections.Counter(r["how"] for r in rows)
    report.append(f"cách xếp: regex {how['regex']}; mặc định substantive (không khớp mẫu nào) {how['default']}; phụ lục {how['type']}")
    report.append("LLM: không dùng (quyết định A14)")
    sample = random.Random(20261109).sample([r for r in rows if r["label"] != "appendix"], 10)
    report.append("10 Điều mẫu ngẫu nhiên (hạt giống cố định):")
    report += [f"  {r['id']:<34} {r['label']:<18} {r['how']:<20} {headings[r['id']][:60]}" for r in sample]
    path = corpus.report_dir(L4_DIR_NAME) / "l4_report.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(report) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(report))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
