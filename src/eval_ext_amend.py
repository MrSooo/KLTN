"""Bộ kiểm thử ngoài của A4: câu chỉ thị thật của Luật 85/2025/QH15, đổi số hiệu sang BLDS 2015 phần thừa kế (plan bước 3.2b).

Chạy: python -I src/eval_ext_amend.py [--llm off|replay|live]   (mặc định replay; live cần .venv/bin/python và ANTHROPIC_API_KEY)

Mỗi ca trong data/ext_amend/cases_blds2015_p4.json là một văn bản sửa đổi riêng: phần đầu chuẩn + các dòng van_ban_bld (giữ khung câu
của cau_goc, chỉ đổi số hiệu, cụm từ, nội dung trong nháy) + câu hiệu lực. Áp lên blds2015_p4 bằng a4.apply_series rồi so (op, đích)
với mong_doi. Kết quả mỗi ca:
  ky_hieu   đúng, mọi chỉ thị do văn phạm chuẩn nhận
  llm       đúng, có chỉ thị qua tầng chuẩn hoá
  dung_loi  A4 dừng với mã lỗi (fail-closed: không áp gì)
  SAI       chạy xong nhưng (op, đích) khác mong đợi: lỗi nghiêm trọng (fail-open)
Báo cáo: docs/ext_amend_report_<mode>.txt. Thoát 1 nếu có ca SAI.
"""
import argparse
import collections
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import a4_versions as a4

ROOT = Path(__file__).resolve().parent.parent
BASE = ROOT / "data" / "raw" / "blds2015_p4.md"
CASES = ROOT / "data" / "ext_amend" / "cases_blds2015_p4.json"
SOURCE = ROOT / "data" / "ext_amend" / "nguon_luat_85_2025_QH15.txt"
HEAD = "Điều 1. Sửa đổi, bổ sung một số điều của Bộ luật Dân sự số 91/2015/QH13"
TAIL = ["Điều 2. Hiệu lực thi hành", "Luật này có hiệu lực thi hành từ ngày 01 tháng 01 năm 2027."]
OUTCOMES = ("ky_hieu", "llm", "dung_loi", "SAI")


def load_cases(path=CASES):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def case_text(case):
    """Văn bản sửa đổi của một ca, trình bày như Công báo: một đoạn một dòng, không dòng trống."""
    return "\n".join([HEAD, *case["van_ban_bld"], *TAIL]) + "\n"


def short(code):
    return code.split(".", 1)[1]


def run_case(case):
    """(kết quả, chi tiết, [(op, đích)] thực nhận)."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / f"ext_{case['id']}.md"
        path.write_text(case_text(case), encoding="utf-8")
        try:
            run = a4.apply_series(BASE, [path])
        except a4.A4Error as e:
            return "dung_loi", f"{e.code}: {e.message}"[:200], []
    ds = run.docs[0].directives
    got = sorted([d.op, short(t)] for d in ds for t in d.targets)
    if got != sorted(case["mong_doi"]):
        return "SAI", f"nhận {got}, mong đợi {sorted(case['mong_doi'])}", got
    via = "llm" if any(d.via == "llm" for d in ds) else "ky_hieu"
    rounds = [b.rounds for b in run.docs[0].llm]
    return via, (f"số lần đề xuất {rounds}" if rounds else ""), got


def evaluate(mode):
    saved = a4.BLOCK_PROPOSER
    if mode == "off":
        a4.BLOCK_PROPOSER = None
    else:
        import a4_llm
        a4.BLOCK_PROPOSER = a4_llm.ClaudeProposer(mode)
    try:
        return [(c, *run_case(c)) for c in load_cases()]
    finally:
        calls = getattr(a4.BLOCK_PROPOSER, "calls", 0)
        a4.BLOCK_PROPOSER = saved
        evaluate.api_calls = calls


def format_report(mode, results):
    count = collections.Counter(r for _, r, _, _ in results)
    L = [f"Bộ kiểm thử ngoài của A4 (chế độ --llm {mode})",
         f"nguồn câu gốc: {SOURCE.relative_to(ROOT)} (Luật 85/2025/QH15, Công báo số 953 + 954 ngày 21/07/2025)",
         f"ca: {len(results)} | " + " | ".join(f"{k} {count.get(k, 0)}" for k in OUTCOMES) +
         f" | gọi API lần này: {getattr(evaluate, 'api_calls', 0)}", ""]
    for case, outcome, detail, _ in results:
        L.append(f"{case['id']}\t{outcome}\t{detail}")
        L.append(f"    gốc (dòng {', '.join(map(str, case['nguon_dong']))}): {case['cau_goc'][0]}")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--llm", choices=("off", "replay", "live"), default="replay")
    args = ap.parse_args(argv)
    results = evaluate(args.llm)
    text = format_report(args.llm, results)
    print(text, end="")
    out = a4.DOCS_DIR / f"ext_amend_report_{args.llm}.txt"
    a4.write_text(text, out)
    print("đã ghi", out)
    return 1 if any(r == "SAI" for _, r, _, _ in results) else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
