"""Test bộ kiểm thử ngoài của A4 (eval_ext_amend): câu gốc đúng nguyên văn nguồn, và không ca nào bị áp sai im lặng."""
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import eval_ext_amend as ev

# Kết quả khoá ở chế độ off (không LLM): ca nào văn phạm chuẩn nhận được, ca nào dừng.
OFF_KY_HIEU = {"c01", "c03", "c05", "c08", "c09", "c16", "c17", "c18", "c19"}


def source_lines():
    out = {}
    for line in ev.SOURCE.read_text(encoding="utf-8").split("\n"):
        if line and line[0].isdigit():
            no, text = line.split("\t", 1)
            out[int(no)] = text
    return out


def test_original_sentences_are_verbatim_from_the_source():
    src = source_lines()
    cases = ev.load_cases()
    assert len(cases) == 19 and len({c["id"] for c in cases}) == 19
    for c in cases:
        assert c["cau_goc"] == [src[n] for n in c["nguon_dong"]], c["id"]
        assert c["mong_doi"], c["id"]


def test_off_mode_never_applies_a_wrong_change():
    results = ev.evaluate("off")
    by_outcome = collections.defaultdict(set)
    for case, outcome, _, _ in results:
        by_outcome[outcome].add(case["id"])
    assert by_outcome["SAI"] == set(), by_outcome["SAI"]
    assert by_outcome["ky_hieu"] == OFF_KY_HIEU, sorted(by_outcome["ky_hieu"])
    assert by_outcome["llm"] == set() and len(by_outcome["dung_loi"]) == 19 - len(OFF_KY_HIEU)


def main():
    failed = 0
    for fn_name, fn in list(globals().items()):
        if fn_name.startswith("test_") and callable(fn):
            try:
                fn()
                print("OK  ", fn_name)
            except AssertionError as e:
                failed += 1
                print("FAIL", fn_name, "->", e)
            except Exception as e:
                failed += 1
                print("FAIL", fn_name, "->", type(e).__name__, e)
    print("tổng test lỗi:", failed)
    return failed


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(1 if main() else 0)
