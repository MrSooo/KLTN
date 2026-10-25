"""Test eval_gold: chấm precision / recall trên đồ thị và đáp án dựng tay (không dùng đáp án thật, vì đáp án do người gán)."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import a6_general_exceptions as a6
import eval_gold as eg

P = "BLDS2015."
COND = a6.condition_id("BLDS2015", "có thỏa thuận khác")


def n(code, type_, number=None, text=None):
    return {"id": P + code if type_ != a6.COND_TYPE else code, "type": type_, "number": number, "text": text}


NODES = [n("D609", "dieu", "609"), n("D609.K1", "khoan", "1"), n("D610", "dieu", "610"), n("D614", "dieu", "614"),
         n("D614.K1", "khoan", "1"), n(COND, a6.COND_TYPE, text="có thỏa thuận khác")]


def e(s, p, o):
    full = lambda c: c if c.startswith(P) else P + c
    return {"s": full(s), "p": p, "o": full(o)}


EDGES = [e("D609.K1", "refers_to", "D614"),   # đúng
         e("D614.K1", "refers_to", "D610"),   # thừa
         e("D610", "refers_to", "D609"),      # ngoài mẫu (610 không thuộc mẫu), không chấm
         e(COND, "exception_of", "D614.K1"),  # đúng (đáp án ghi bằng mệnh đề)
         e("D609", "contains", "D609.K1")]


def gold(*rows):
    return [(i, dict(zip(eg.COLUMNS, list(r) + [""] * (len(eg.COLUMNS) - len(r))))) for i, r in enumerate(rows, 1)]


def test_sample_rule():
    assert eg.sample_dieu(NODES) == [P + "D609", P + "D614"]  # 610 không chia 5 dư


def test_score_precision_recall_and_implicit():
    rows = gold(("refers_to", "D609.K1", "D614"), ("refers_to", "D614.K1", "D609"),
                ("exception_of", '"Có thỏa  thuận khác."', "D614.K1"), ("exception_of", "D614.K1", "D609.K1", "1"),
                ("refers_to", "D610", "D614"), ("refers_to_external", "D609", "Luật Đất đai"))
    result, dieu, out, external = eg.score(rows, NODES, EDGES)
    r = result["refers_to"]
    assert (len(r["tp"]), len(r["fp"]), len(r["fn"])) == (1, 1, 1) and r["precision"] == 0.5 and r["recall"] == 0.5, r
    x = result["exception_of"]
    assert len(x["tp"]) == 1 and x["fn"] == [(P + "D614.K1", "exception_of", P + "D609.K1")], x
    assert x["recall"] == 0.5 and x["recall_explicit"] == 1.0 and x["implicit"] == 1 and x["precision"] == 1.0
    assert out == [(5, (P + "D610", "refers_to", P + "D614"))] and external == 1


def test_clause_without_condition_node_is_kept_as_text():
    result, *_ = eg.score(gold(("exception_of", '"pháp luật có quy định khác"', "D609")), NODES, EDGES)
    assert result["exception_of"]["fn"] == [("(mệnh đề) pháp luật có quy định khác", "exception_of", P + "D609")]


def test_read_gold_status_and_format_errors():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "g.tsv"
        path.write_text(eg.TODO + "\n" + "\t".join(eg.COLUMNS) + "\nrefers_to\tD609\tD614\n", encoding="utf-8")
        done, rows = eg.read_gold(path)
        assert not done and rows[0][1]["s"] == "D609" and rows[0][1]["ngam"] == ""
        for bad in ("refers_too\tD609\tD614", "refers_to\tD609\t", "refers_to\tD609\tD614\t2"):
            path.write_text(eg.DONE + "\n" + bad + "\n", encoding="utf-8")
            try:
                eg.read_gold(path)
            except eg.GoldError as err:
                assert "g.tsv:2" in str(err), err
            else:
                raise AssertionError(f"phải lỗi: {bad!r}")


def test_template_does_not_overwrite_and_unannotated_is_refused():
    real = Path(eg.__file__).resolve().parent.parent / "data" / "raw" / "blds2015_p4.md"
    with tempfile.TemporaryDirectory() as tmp:
        old = eg.GOLD_DIR
        eg.GOLD_DIR = Path(tmp)
        try:
            assert [p.name for p in eg.write_template(real)] == ["units_blds2015_p4.md", "gold_blds2015_p4.tsv"]
            eg.gold_path(real).write_text(eg.DONE + "\nrefers_to\tD619\tD652\n", encoding="utf-8")
            assert eg.write_template(real) == [] and eg.read_gold(eg.gold_path(real))[0]  # không ghi đè đáp án đã gán
            eg.gold_path(real).write_text(eg.TODO + "\n", encoding="utf-8")
            try:
                eg.run(real)
            except SystemExit as err:
                assert "chưa đánh dấu" in str(err.code), err.code
            else:
                raise AssertionError("chưa gán xong thì không chấm")
        finally:
            eg.GOLD_DIR = old


def main():
    failed = 0
    for fn_name, fn in list(globals().items()):
        if fn_name.startswith("test_") and callable(fn):
            try:
                fn()
                print("OK  ", fn_name)
            except AssertionError as err:
                failed += 1
                print("FAIL", fn_name, "->", err)
            except Exception as err:
                failed += 1
                print("FAIL", fn_name, "->", type(err).__name__, err)
    print("tổng test lỗi:", failed)
    return failed


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(1 if main() else 0)
