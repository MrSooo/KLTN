"""Đếm đúng/sai trên báo cáo 1.9 của bộ blld_questions (A62): dùng để so các KB (ckey, tach gốc, tach sau sửa) trên cùng bộ câu.
Dùng: python -X utf8 -I utils/llm_runs/score_blld_questions.py <báo cáo 1> [<báo cáo 2> ...]
In: số câu đúng, đúng theo nhóm lỗi (`loi` trong bộ câu hỏi), và bảng từng câu để thấy câu nào đổi kết quả giữa các KB.
"Đúng chặt": nhãn đúng VÀ căn cứ (quy tắc đã chạy) có ít nhất một đơn vị của căn cứ chuẩn (hoặc đơn vị con/cha của nó); chỉ xét với nhãn
chuẩn ket_luan_duoc hoặc bi_bac (nhãn khác không có quy tắc để so). Lý do: một số câu "đúng" nhờ quy tắc khác Điều (B06 gốc ra đúng nhờ D35, quyền
của người lao động), nên đếm nhãn thôi sẽ thưởng cho suy luận sai."""
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
Q = {q["id"]: q for q in json.load(open(ROOT / "data/eval_dev/blld_questions.json", encoding="utf-8"))["cau_hoi"]}
LINE = re.compile(r"^(B\d+) \S+ chuẩn=(\S+) ra=(\S+) \[(ĐÚNG|sai)\]")
CAN_CU = re.compile(r"căn cứ: (\[.*?\]); căn cứ chuẩn: (\[.*?\])")


def _gan(a, b):
    return a == b or a.startswith(b + ".") or b.startswith(a + ".")


def doc(path):
    """Kết quả từng câu: id -> (ra, đúng?, đúng chặt?). Dòng căn cứ là dòng đầu tiên sau dòng kết quả có "căn cứ chuẩn"."""
    out, cur = {}, None
    for line in open(path, encoding="utf-8"):
        m = LINE.match(line)
        if m:
            cur = m.group(1)
            out[cur] = [m.group(3), m.group(4) == "ĐÚNG", m.group(4) == "ĐÚNG"]
            if m.group(2) not in ("ket_luan_duoc", "bi_bac"):  # chưa đủ căn cứ / không trả lời: không có quy tắc nào để so
                cur = None
            continue
        c = CAN_CU.search(line)
        if c and cur and out[cur][1]:
            got, gold = ast.literal_eval(c.group(1)), ast.literal_eval(c.group(2))
            if gold:
                out[cur][2] = any(_gan(x, y) for x in got for y in gold)
            cur = None
    return {k: tuple(v) for k, v in out.items()}


def main():
    runs = [(p, doc(p)) for p in sys.argv[1:]]
    for p, r in runs:
        nhom = {}
        for qid, (_ra, ok, _ch) in r.items():
            k = Q.get(qid, {}).get("loi", "?")
            a, b = nhom.get(k, (0, 0))
            nhom[k] = (a + ok, b + 1)
        print(f"{p}: đúng {sum(v[1] for v in r.values())}/{len(r)}, đúng chặt {sum(v[2] for v in r.values())}/{len(r)}")
        for k, (a, b) in sorted(nhom.items()):
            print(f"   {k}: {a}/{b}")
    if len(runs) > 1:
        print("câu khác nhau giữa các bản (ra, đúng=1):")
        for qid in sorted(Q):
            cells = [r.get(qid, ("-", False, False)) for _p, r in runs]
            if len({c for c in cells}) > 1:
                print("  ", qid, Q[qid].get("loi"), " | ".join(f"{ra}:{int(ok)}{'' if ch == ok else '(căn cứ sai)'}" for ra, ok, ch in cells))


if __name__ == "__main__":
    main()
