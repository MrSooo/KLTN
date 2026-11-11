"""Bước 1.3: tìm các điều khoản mà luật GIAO cho cấp dưới quy định chi tiết ("Chính phủ quy định chi tiết Điều này", "theo quy định của Bộ trưởng ...").

Chạy: python -I src/delegation.py        (cần bước parse)
Đầu ra (data/processed/l3/):
  delegation_clauses.jsonl  {clause_id, unit_id, pattern, subpattern, delegate, phrase, context, flags}
Báo cáo: docs/bao_cao_chay/l3/delegation_report.txt (số theo dạng, ca regex lỏng, mốc cổng).

Vì sao cần: đó là các chỗ luật chưa nói hết, chờ văn bản dưới luật lấp vào. KB phải biết chỗ nào còn trống thì mới trả lời được "chưa đủ căn cứ"
thay vì trả lời bừa. Việc nối các chỗ trống này với văn bản dưới luật (filled_by) thuộc bước 2.2 (links.py), không làm ở đây vì cần các văn bản khác.

Hai tầng, đều bằng regex (không LLM):
  Tầng chặt (flags=[]): bốn dạng, các ca chắc.
    A "Chính phủ / Bộ trưởng ... / Thủ tướng Chính phủ quy định ..." (gồm C "do Chính phủ quy định"); B "theo quy định của Chính phủ / Bộ trưởng";
    D "Bộ trưởng ... ban hành" (danh mục, chương trình ...); E "Thủ tướng Chính phủ quyết định".
  Tầng lỏng (pattern="loose", flags=["loose"]): câu có bên được giao đứng gần một động từ giao mà tầng chặt không bắt. Không vứt (bỏ sót nguy hiểm
    hơn thừa: KB tưởng luật đã đủ sẽ trả "bị bác" sai), nhưng gắn cờ để biết ca này chưa chắc. Đo ngày 11/11 trên BLLĐ: tầng chặt hụt các câu như
    "Bộ trưởng Bộ Lao động - Thương binh và Xã hội quy định chi tiết ..." vì dạng A chỉ cho phép các từ toàn chữ cái giữa "Bộ trưởng" và "quy định",
    dấu gạch ngang chặn lại. Số đếm là regex thô: ca không phải giao chi tiết vẫn có trong danh sách, không tự lọc.
Quyết định: docs/quyet_dinh/pipeline_moi_quyet_dinh.txt (A15, mục 1.3).
"""
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import parse as l1
import corpus

L3_DIR_NAME = "l3"

DELEG_PATTERNS = [
    ("A", re.compile(r"(?<!\w)(?:Chính phủ|Bộ trưởng(?:[ ]+[^\W\d_]+){0,10}?|Thủ tướng Chính phủ)[ ]+quy[ ]+định(?![ ]+tại)")),
    ("B", re.compile(r"theo[ ]+quy[ ]+định[ ]+của[ ]+(?:Chính phủ|Bộ trưởng|Thủ tướng Chính phủ)")),
    ("D", re.compile(r"Bộ[ ]+trưởng[^.;:]{0,100}?ban[ ]+hành", re.I)),
    ("E", re.compile(r"Thủ[ ]+tướng[ ]+Chính[ ]+phủ[ ]+quyết[ ]+định")),
]
DO_RE = re.compile(r"do[ ]+$")  # "do Chính phủ quy định": dạng C, nằm trong A
# Tầng lỏng: bên được giao gần một động từ giao (trong cùng một câu: không qua dấu . hoặc ;), thứ tự nào cũng được.
LOOSE_RE = re.compile(r"(?:Chính phủ|Bộ trưởng|Thủ tướng)[^.;]{0,90}?(?:quy định|ban hành|hướng dẫn|quyết định)"
                      r"|(?:quy định|ban hành|hướng dẫn|quyết định)[^.;]{0,50}?(?:Chính phủ|Bộ trưởng|Thủ tướng)")


def delegate_of(phrase):
    if "Thủ tướng" in phrase:
        return "Thủ tướng"
    return "Bộ trưởng" if "Bộ trưởng" in phrase else "Chính phủ"


def _units_with_text(units):
    for uid, u in units.items():
        if u["type"] in ("dieu", "khoan", "diem") and u.get("text"):
            yield uid, u["text"]


def find_delegation(units, doc_id):
    """Các điều khoản giao chi tiết trong văn bản gốc: trước hết các ca tầng chặt (flags=[]), theo thứ tự đơn vị rồi vị trí trong text; sau đó các ca
    chỉ tầng lỏng bắt được (pattern="loose", flags=["loose"]). Ca lỏng trùng vị trí với một ca chặt thì không tính lại. Mã clause_id của ca chặt không
    đổi khi thêm tầng lỏng, vì ca lỏng đánh số tiếp sau ca chặt của cùng đơn vị."""
    clauses, counter, spans = [], collections.Counter(), collections.defaultdict(list)

    def add(uid, text, m, pattern, subpattern, flags):
        counter[uid] += 1
        short = uid.split(".", 1)[1].replace(".", "_")
        clauses.append({"clause_id": f"DC_{short}_{counter[uid]}", "unit_id": uid, "pattern": pattern, "subpattern": subpattern,
                        "delegate": delegate_of(m[0]), "phrase": m[0], "context": text[max(0, m.start() - 40):m.end() + 60], "flags": flags})

    for uid, text in _units_with_text(units):
        for pattern, rx in DELEG_PATTERNS:
            for m in rx.finditer(text):
                spans[uid].append(m.span())
                is_c = pattern == "A" and DO_RE.search(text[:m.start()]) is not None
                add(uid, text, m, pattern, "C" if is_c else None, [])
    strict_count = len(clauses)
    for uid, text in _units_with_text(units):
        for m in LOOSE_RE.finditer(text):
            if any(m.start() < end and start < m.end() for start, end in spans[uid]):
                continue  # đã được tầng chặt bắt
            add(uid, text, m, "loose", None, ["loose"])
    assert all(not c["flags"] for c in clauses[:strict_count])
    return clauses


def main():
    base = corpus.BASE_DOC_ID
    clauses = find_delegation(l1.load_units(base), base)
    strict = [c for c in clauses if not c["flags"]]
    loose = [c for c in clauses if c["flags"]]
    l1.write_jsonl(corpus.out_dir(L3_DIR_NAME) / "delegation_clauses.jsonl", clauses)

    per_pat = collections.Counter(c["pattern"] for c in strict)
    dieu_pat = {p: len({c["unit_id"].split(".")[1] for c in strict if c["pattern"] == p}) for p in per_pat}
    units_with = {c["unit_id"] for c in strict}
    have = lambda u: u in units_with or any(x.startswith(u + ".") or u.startswith(x + ".") for x in units_with)
    milestones = [("BLLD.D91.K4 (dạng A)", have("BLLD_45-2019.D91.K4")), ("D154.K1/K2/K9 (dạng B)", all(have(f"BLLD_45-2019.D154.K{k}") for k in (1, 2, 9))),
                  ("D142.K1 (dạng D)", have("BLLD_45-2019.D142.K1")), ("D112 (dạng E)", have("BLLD_45-2019.D112"))]
    report = ["Báo cáo điều khoản giao chi tiết (bước 1.3)",
              f"tầng chặt: {len(strict)} cụm ở {len(units_with)} đơn vị; theo dạng {dict(per_pat)}; số Điều theo dạng {dieu_pat}",
              "(plan 8/11: A 39 cụm/37 Điều, B 10/8, C 2 trong A, D 5 Điều, E 1 Điều; tổng ~55 cụm/~50 Điều; đây là regex thô, chưa lọc ca không phải giao chi tiết)",
              f"tầng lỏng (cờ loose, chưa chắc là điều khoản giao, cần người xem): {len(loose)} cụm"]
    report += [f"  {c['unit_id']}: {c['phrase']}" for c in loose]
    report += ["mốc cổng tầng chặt:"] + [f"  {'đạt' if ok else 'KHÔNG đạt'}: {name}" for name, ok in milestones]
    rp = corpus.report_dir(L3_DIR_NAME) / "delegation_report.txt"
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text("\n".join(report) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(report))
    if not all(ok for _, ok in milestones):
        raise SystemExit(1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
