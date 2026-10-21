"""A3: kiểm tra cạnh exception_of (hai quy tắc tường minh) trên ví dụ dựng tay, file mẫu rồi file đầy đủ.

Chạy: python -I src/test_a3.py   (các hàm test_* cũng chạy được bằng pytest nếu có cài)
Chạy a3_exceptions.py cho cả hai file trước (python -I src/a3_exceptions.py <file md>), test_files_on_disk đọc file đã ghi.
"""
import collections
import contextlib
import io
import json
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import a2_edges as a2
import a3_exceptions as a3

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_FILE = ROOT / "data" / "sample" / "blds2015_5dieu.md"
FULL_FILE = ROOT / "data" / "raw" / "blds2015_p4.md"
FILES = [("mẫu", SAMPLE_FILE), ("đầy đủ", FULL_FILE)]  # luôn mẫu trước
P = "BLDS2015."

# Số kỳ vọng do user đếm tay từ file md. Số trigger (11 và 1) đếm lại độc lập ở test_trigger_accounting_independent.
TRIGGER_TOTAL = {SAMPLE_FILE: 1, FULL_FILE: 11}
EDGES_REFERENCE = {
    SAMPLE_FILE: [(P + "D644.K2", P + "D644.K1", "khoản 1 Điều này không áp dụng", a3.NOT_APPLY)],
    FULL_FILE: [(P + f"D632.K{k}", P + "D632", "Mọi người đều có thể làm chứng cho việc lập di chúc, trừ những người sau đây:",
                 a3.EXCEPT_LIST) for k in (1, 2, 3)]
              + [(P + "D644.K2", P + "D644.K1", "khoản 1 Điều này không áp dụng", a3.NOT_APPLY)],
}
UNHANDLED_REFERENCE = {
    SAMPLE_FILE: [],
    FULL_FILE: [P + c for c in ("D615.K1", "D615.K3", "D617.K1.a", "D619", "D620.K1", "D646.K3", "D659.K1", "D662.K1", "D662.K2")],
}
HANDLED_TRIGGERS = {SAMPLE_FILE: 1, FULL_FILE: 2}


def mini_units(spec):
    """Đơn vị nhỏ dựng tay: {mã: (type, text hoặc None)}. Giữ thứ tự khai báo."""
    return {code: {"type": t, "number": "x", "source_line": 1, **({"text": text} if text else {})}
            for code, (t, text) in spec.items()}


def load(path):
    return a2.load_units(a2.triples_path(path))


def exceptions_of(units):
    return a3.find_exceptions(units, a2.build_edges(units))


def trigger_tokens(text):
    """Đếm trigger độc lập với TRIGGER_RE và find_refs: tách \\w+ từng đoạn, đếm token "trừ" và chuỗi "không áp dụng"."""
    count = 0
    for paragraph in text.split("\n"):
        words = [w.casefold() for w in re.findall(r"\w+", paragraph)]
        count += words.count("trừ")
        count += sum(1 for i in range(len(words) - 2) if words[i:i + 3] == ["không", "áp", "dụng"])
    return count


# ---- quy tắc 1: "không áp dụng" ----

def test_rule1_phrase_immediately_before():
    text = "Quy định tại khoản 1 Điều này không áp dụng đối với người từ chối nhận di sản theo quy định tại Điều 6."
    units = mini_units({"X.D5": ("dieu", None), "X.D5.K1": ("khoan", None), "X.D5.K2": ("khoan", text), "X.D6": ("dieu", None)})
    edges, handled, unhandled = exceptions_of(units)
    # chỉ cụm đứng ngay trước là đích; "Điều 6" đứng sau "không áp dụng" thì không phải đích
    assert edges == [("X.D5.K2", "exception_of", "X.D5.K1", "khoản 1 Điều này không áp dụng", a3.NOT_APPLY)]
    assert handled == [("X.D5.K2", "không áp dụng", a3.NOT_APPLY)] and unhandled == []
    assert a3.check_exceptions(units, a2.build_edges(units), edges, handled, unhandled) == []


def test_rule1_every_target_hoa_thuong_gap_and_tail():
    units = mini_units({
        "X.D5": ("dieu", None), "X.D6": ("dieu", None), "X.D7": ("dieu", None), "X.D8": ("dieu", None),
        "X.D5.K1": ("khoan", "Điều 6 và Điều 7  Không áp dụng nếu có thỏa thuận."),   # hai đích; hai dấu cách; chữ hoa
        "X.D5.K2": ("khoan", "Điều 8 của Bộ luật này không áp dụng cho ai."),         # đuôi "của Bộ luật này"
    })
    edges, handled, unhandled = exceptions_of(units)
    assert edges == [
        ("X.D5.K1", "exception_of", "X.D6", "Điều 6 và Điều 7  Không áp dụng", a3.NOT_APPLY),
        ("X.D5.K1", "exception_of", "X.D7", "Điều 6 và Điều 7  Không áp dụng", a3.NOT_APPLY),
        ("X.D5.K2", "exception_of", "X.D8", "Điều 8 của Bộ luật này không áp dụng", a3.NOT_APPLY),
    ]
    assert handled == [("X.D5.K1", "Không áp dụng", a3.NOT_APPLY), ("X.D5.K2", "không áp dụng", a3.NOT_APPLY)]
    assert unhandled == []


def test_rule1_phrase_not_immediately_before_gives_no_edge():
    cases = {
        "after": "Không áp dụng đối với khoản 1 Điều này.",              # cụm đứng sau
        "words": "khoản 1 Điều này nêu trên không áp dụng cho ai.",     # có từ xen giữa
        "comma": "khoản 1 Điều này, không áp dụng cho ai.",             # có dấu phẩy xen giữa
        "newline": "khoản 1 Điều này\nkhông áp dụng cho ai.",           # khoảng trắng = dấu cách, xuống dòng không tính
        "none": "Quy định này không áp dụng cho ai.",                   # không có cụm nào
    }
    for name, text in cases.items():
        units = mini_units({"X.D5": ("dieu", None), "X.D5.K1": ("khoan", None), "X.D5.K2": ("khoan", text)})
        edges, handled, unhandled = exceptions_of(units)
        assert (edges, handled) == ([], []) and unhandled == [("X.D5.K2", text)], f"{name}: {edges} {unhandled}"


def test_rule1_unconfirmed_shape_or_missing_target_is_error():
    units = mini_units({"X.D5": ("dieu", None), "X.D5.K1": ("khoan", None),
                        "X.D5.K2": ("khoan", "khoản 1 không áp dụng cho ai.")})        # khoản có số, không có Điều
    for text in ("khoản 1 không áp dụng cho ai.", "Điều 99 không áp dụng cho ai."):    # dạng chưa có quy tắc; đích thiếu
        units["X.D5.K2"]["text"] = text
        try:
            exceptions_of(units)
        except ValueError:
            continue
        raise AssertionError(f"{text!r} phải báo lỗi, không đoán")


# ---- quy tắc 2: "trừ ... sau đây:" ----

def rule2_units(text, with_children=True):
    spec = {"X.D1": ("dieu", text)}
    if with_children:
        spec.update({"X.D1.K1": ("khoan", "Người chưa đủ tuổi."), "X.D1.K1.a": ("diem", "Dưới mười tám tuổi."),
                     "X.D1.K2": ("khoan", "Người mất năng lực hành vi dân sự.")})
    return mini_units(spec)


def test_rule2_direct_children_and_evidence_in_o():
    text = "Mọi người đều có thể làm chứng, trừ những người sau đây:"
    units = rule2_units(text)
    edges, handled, unhandled = exceptions_of(units)
    # chỉ con trực tiếp (không lấy X.D1.K1.a); s là con, o là U; evidence là câu của U chứ không phải của con
    assert edges == [("X.D1.K1", "exception_of", "X.D1", text, a3.EXCEPT_LIST),
                     ("X.D1.K2", "exception_of", "X.D1", text, a3.EXCEPT_LIST)]
    assert handled == [("X.D1", "trừ", a3.EXCEPT_LIST)] and unhandled == []
    assert a3.check_exceptions(units, a2.build_edges(units), edges, handled, unhandled) == []


def test_rule2_hoa_thuong_and_ngoai_tru():
    for text, kind in (("TRỪ những người sau đây:", "TRỪ"), ("Ngoại  trừ những người sau đây:", "Ngoại  trừ")):
        edges, handled, unhandled = exceptions_of(rule2_units(text))
        assert [(s, o) for s, _, o, _, _ in edges] == [("X.D1.K1", "X.D1"), ("X.D1.K2", "X.D1")], text
        assert handled == [("X.D1", kind, a3.EXCEPT_LIST)] and unhandled == [], text


def test_rule2_text_not_ending_with_sau_day_colon_is_not_matched():
    for text in ("Mọi người đều có thể làm chứng, trừ những người sau đây;",     # kết thúc bằng ;
                 "Mọi người đều có thể làm chứng, trừ những người sau đây.",     # kết thúc bằng .
                 "Mọi người đều có thể làm chứng, trừ những người sau:",         # không phải "sau đây:"
                 "Trừ những người sau đây: không được làm chứng"):               # "sau đây:" nằm giữa text
        edges, handled, unhandled = exceptions_of(rule2_units(text))
        assert (edges, handled) == ([], []) and unhandled == [("X.D1", text)], f"{text!r}: {edges}"


def test_rule2_without_tru_is_not_a_trigger():
    edges, handled, unhandled = exceptions_of(rule2_units("Người lập di chúc có quyền sau đây:"))
    assert (edges, handled, unhandled) == ([], [], [])   # đơn vị kết thúc bằng "sau đây:" mà không có trigger: bỏ qua, không phải unhandled


def test_rule2_unconfirmed_shape_is_error():
    for units in (rule2_units("trừ những người sau đây:", with_children=False),    # khớp quy tắc nhưng không có con
                  rule2_units("trừ A, trừ B, trừ những người sau đây:")):          # nhiều hơn một "trừ"
        try:
            exceptions_of(units)
        except ValueError:
            continue
        raise AssertionError("dạng chưa có quy tắc phải báo lỗi, không đoán")


# ---- đếm trigger: mỗi trigger đúng một trong hai ----

def test_every_trigger_is_handled_or_unhandled_hand_built():
    units = mini_units({
        "X.D1": ("dieu", "Mọi người đều có thể làm chứng, trừ những người sau đây:"),    # quy tắc 2
        "X.D1.K1": ("khoan", "Người A."),
        "X.D1.K2": ("khoan", "khoản 1 Điều này không áp dụng, trừ trường hợp có thỏa thuận khác."),  # quy tắc 1 + một trừ lạc
        "X.D2": ("dieu", "Trừ trường hợp luật có quy định khác."),                         # unhandled
    })
    edges, handled, unhandled = exceptions_of(units)
    independent = sum(trigger_tokens(u["text"]) for u in units.values() if "text" in u)
    assert independent == len(handled) + len(unhandled) == 4, (independent, handled, unhandled)
    # từng đơn vị: số trigger trong text = số lần đơn vị đó xuất hiện ở handled + unhandled
    per_unit = collections.Counter(c for c, *_ in handled) + collections.Counter(c for c, _ in unhandled)
    assert per_unit == {c: trigger_tokens(u["text"]) for c, u in units.items() if trigger_tokens(u.get("text", ""))}
    assert a3.check_exceptions(units, a2.build_edges(units), edges, handled, unhandled) == []


def test_trigger_accounting_independent():
    """Số trigger đếm độc lập (không qua find_refs, không qua TRIGGER_RE) = đã xử lý + unhandled = số kỳ vọng của user."""
    for name, path in FILES:
        units = load(path)
        _, handled, unhandled = exceptions_of(units)
        independent = sum(trigger_tokens(u["text"]) for u in units.values() if "text" in u)
        assert independent == len(handled) + len(unhandled) == TRIGGER_TOTAL[path], f"file {name}: {independent}, {len(handled)}, {len(unhandled)}"
        assert len(a2.find_triggers(units)) == independent, f"file {name}: lệch find_triggers của A2"
        assert len(handled) == HANDLED_TRIGGERS[path], f"file {name}: đã xử lý {len(handled)}"
        per_unit = collections.Counter(c for c, *_ in handled) + collections.Counter(c for c, _ in unhandled)
        assert per_unit == {c: trigger_tokens(u["text"]) for c, u in units.items() if "text" in u and trigger_tokens(u["text"])}, f"file {name}"


# ---- dữ liệu thật ----

def test_counts_and_reviewed_lists():
    for name, path in FILES:
        units = load(path)
        edges, handled, unhandled = exceptions_of(units)
        assert [(s, o, ev, m) for s, _, o, ev, m in edges] == EDGES_REFERENCE[path], f"file {name}: {edges}"
        assert len(edges) == len(EDGES_REFERENCE[path]) == {SAMPLE_FILE: 1, FULL_FILE: 4}[path]
        assert [c for c, _ in unhandled] == UNHANDLED_REFERENCE[path], f"file {name}: {[c for c, _ in unhandled]}"
        assert all(sentence == units[c]["text"] for c, sentence in unhandled), f"file {name}: câu phải là toàn bộ text"
        assert all(p == "exception_of" for _, p, _, _, _ in edges)


def test_edges_invariants_and_check_clean():
    for name, path in FILES:
        units = load(path)
        structural = a2.build_edges(units)
        edges, handled, unhandled = a3.find_exceptions(units, structural)
        assert all(s != o for s, _, o, _, _ in edges), f"file {name}: có cạnh s == o"
        triples = [(s, p, o) for s, p, o, _, _ in edges]
        assert len(triples) == len(set(triples)), f"file {name}: cạnh trùng"
        assert a3.check_exceptions(units, structural, edges, handled, unhandled) == [], f"file {name}"
        # evidence nằm nguyên văn trong text của đơn vị chứa trigger: s ở quy tắc 1, o ở quy tắc 2
        for s, _, o, evidence, method in edges:
            holder = s if method == a3.NOT_APPLY else o
            assert evidence in units[holder]["text"], f"file {name}: {s} -> {o}"
            if method == a3.EXCEPT_LIST:
                assert evidence not in units[s].get("text", ""), f"file {name}: evidence quy tắc 2 phải lấy từ o, không từ {s}"


def test_rule2_children_match_independent_code_prefix():
    """Con trực tiếp của U tính bằng tiền tố mã (không qua contains của A2a) phải đúng bằng các s của quy tắc 2."""
    for name, path in FILES:
        units = load(path)
        edges = exceptions_of(units)[0]
        for u in {o for _, _, o, _, m in edges if m == a3.EXCEPT_LIST}:
            by_prefix = [c for c in units if c.startswith(u + ".") and c.count(".") == u.count(".") + 1]
            assert [s for s, _, o, _, m in edges if m == a3.EXCEPT_LIST and o == u] == by_prefix, f"file {name}: {u}"


def test_check_catches_corrupted_data():
    units = load(FULL_FILE)
    structural = a2.build_edges(units)
    edges, handled, unhandled = a3.find_exceptions(units, structural)
    first, last = edges[0], edges[-1]   # quy tắc 2 rồi quy tắc 1

    def errors(**kw):
        args = dict(edges=edges, handled=handled, unhandled=unhandled)
        args.update(kw)
        return a3.check_exceptions(units, structural, args["edges"], args["handled"], args["unhandled"])

    assert any("cạnh trùng" in e for e in errors(edges=edges + [first]))
    assert any("chính nó" in e for e in errors(edges=edges + [(first[2], first[1], first[2], first[3], first[4])]))
    assert any("không có trong tập đơn vị" in e for e in errors(edges=edges + [("X.D9", "exception_of", first[2], first[3], first[4])]))
    assert any("evidence" in e for e in errors(edges=edges[:-1] + [last[:3] + ("không có trong text", last[4])]))
    assert any("evidence" in e for e in errors(edges=edges[:-1] + [last[:3] + ("", last[4])]))
    assert any("method" in e for e in errors(edges=edges[:-1] + [last[:4] + ("khac",)]))
    assert any("p là" in e for e in errors(edges=edges[:-1] + [(last[0], "refers_to") + last[2:]]))
    # quy quắc 2 nhưng s không phải con trực tiếp của o
    assert any("con trực tiếp" in e for e in errors(edges=edges + [("BLDS2015.D615.K1", "exception_of", first[2], first[3], first[4])]))
    # số trigger không khớp: bỏ một unhandled, hoặc thêm một handled
    assert any("số trigger" in e for e in errors(unhandled=unhandled[1:]))
    assert any("số trigger" in e for e in errors(handled=handled + handled[:1]))
    # trigger ghi đã xử lý nhưng không có cạnh
    assert any("không có cạnh" in e for e in errors(edges=edges[:3]))
    # câu unhandled không phải text của đơn vị
    assert any("câu không phải text" in e for e in errors(unhandled=[(unhandled[0][0], "khác")] + unhandled[1:]))
    # câu có xuống dòng không ghi được thành một dòng
    bad = {c: dict(u) for c, u in units.items()}
    bad[unhandled[0][0]]["text"] += "\nđoạn hai"
    bad_unhandled = [(unhandled[0][0], bad[unhandled[0][0]]["text"])] + unhandled[1:]
    assert any("tab hoặc xuống dòng" in e for e in a3.check_exceptions(bad, structural, edges, handled, bad_unhandled))


# ---- ghi file và CLI ----

def test_files_written_correctly():
    for name, path in FILES:
        edges, _, unhandled = exceptions_of(load(path))
        with tempfile.TemporaryDirectory() as tmp:
            out, txt = Path(tmp) / "e.jsonl", Path(tmp) / "u.txt"
            a3.write_exceptions(edges, out)
            a3.write_unhandled(unhandled, txt)
            raw, raw_txt = out.read_bytes(), txt.read_bytes()
        for data in (raw, raw_txt):
            assert not data.startswith(b"\xef\xbb\xbf"), "có BOM"
            assert b"\\u" not in data and b"\r" not in data
        rows = [json.loads(line) for line in raw.decode("utf-8").split("\n") if line]
        assert all(list(r) == ["s", "p", "o", "evidence", "method"] for r in rows), f"file {name}: sai khoá"
        assert [(r["s"], r["p"], r["o"], r["evidence"], r["method"]) for r in rows] == edges, f"file {name}: đọc lại không khớp"
        lines = raw_txt.decode("utf-8").split("\n")
        assert (lines[-1] == "" or not unhandled) and [tuple(x.split("\t")) for x in lines[:-1]] == unhandled, f"file {name}: unhandled"
        assert (raw_txt == b"") == (not unhandled), f"file {name}: file unhandled rỗng khi và chỉ khi không có ca"


def test_files_on_disk():
    """Chạy a3_exceptions.py <md> trước. File trên đĩa phải khớp dựng lại; file A2 không bị lẫn exception_of."""
    for name, path in FILES:
        edges, _, unhandled = exceptions_of(load(path))
        on_disk = a3.exceptions_path(path)
        assert on_disk.exists(), f"file {name}: chưa có {on_disk}, chạy a3_exceptions.py trước"
        rows = [json.loads(line) for line in on_disk.read_text(encoding="utf-8").split("\n") if line]
        assert all(list(r) == ["s", "p", "o", "evidence", "method"] for r in rows), f"file {name}: sai khoá"
        assert [(r["s"], r["p"], r["o"], r["evidence"], r["method"]) for r in rows] == edges, f"file {name}: khác dựng lại"
        lines = a3.unhandled_path(path).read_text(encoding="utf-8").split("\n")
        assert [tuple(x.split("\t")) for x in lines[:-1]] == unhandled and lines[-1] == "", f"file {name}: unhandled"
        for other in (a2.edges_path(path), a2.refs_path(path)):
            preds = {json.loads(line)["p"] for line in other.read_text(encoding="utf-8").split("\n") if line}
            assert "exception_of" not in preds, f"file {name}: {other.name} lẫn exception_of"


def run_cli_expecting_exit(units):
    """Chạy a3.run trên đơn vị dựng tay, ghi vào thư mục tạm; trả về danh sách file đã ghi. Phải thoát khác 0."""
    saved = a2.read_units, a3.exceptions_path, a3.unhandled_path
    with tempfile.TemporaryDirectory() as tmp:
        a2.read_units = lambda src: units
        a3.exceptions_path = lambda src: Path(tmp) / "e.jsonl"
        a3.unhandled_path = lambda src: Path(tmp) / "u.txt"
        try:
            try:
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    a3.run("x")
            except SystemExit as e:
                assert e.code not in (0, None), e.code
            else:
                raise AssertionError("phải thoát khác 0")
        finally:
            a2.read_units, a3.exceptions_path, a3.unhandled_path = saved
        return list(Path(tmp).iterdir())


def test_cli_stops_and_writes_nothing_on_error():
    # lỗi từ find_exceptions (ValueError): quy tắc 2 khớp mà không có con
    assert run_cli_expecting_exit(rule2_units("trừ những người sau đây:", with_children=False)) == []
    # lỗi từ check_exceptions: hai trigger cùng sinh một cạnh (cạnh trùng)
    dup = mini_units({"X.D5": ("dieu", None), "X.D6": ("dieu", None),
                      "X.D5.K1": ("khoan", "Điều 6 không áp dụng cho A, Điều 6 không áp dụng cho B.")})
    assert run_cli_expecting_exit(dup) == []
    # lỗi từ check_exceptions: cạnh tự trỏ (khoản 1 Điều này không áp dụng nằm ngay trong khoản 1)
    selfref = mini_units({"X.D5": ("dieu", None), "X.D5.K1": ("khoan", "khoản 1 Điều này không áp dụng cho ai.")})
    assert run_cli_expecting_exit(selfref) == []


def test_cli_writes_both_files_when_clean():
    units = rule2_units("trừ những người sau đây:")
    units["X.D2"] = mini_units({"c": ("dieu", "Trừ trường hợp khác.")})["c"]
    saved = a2.read_units, a3.exceptions_path, a3.unhandled_path
    with tempfile.TemporaryDirectory() as tmp:
        a2.read_units = lambda src: units
        a3.exceptions_path = lambda src: Path(tmp) / "e.jsonl"
        a3.unhandled_path = lambda src: Path(tmp) / "u.txt"
        try:
            with contextlib.redirect_stdout(io.StringIO()) as out:
                a3.main(["x"])
        finally:
            a2.read_units, a3.exceptions_path, a3.unhandled_path = saved
        rows = [json.loads(line) for line in (Path(tmp) / "e.jsonl").read_text(encoding="utf-8").split("\n") if line]
        assert [(r["s"], r["o"]) for r in rows] == [("X.D1.K1", "X.D1"), ("X.D1.K2", "X.D1")]
        assert (Path(tmp) / "u.txt").read_text(encoding="utf-8") == "X.D2\tTrừ trường hợp khác.\n"
    assert "trigger: 2 | đã xử lý: 1" in out.getvalue() and "unhandled: 1" in out.getvalue()


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
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(1 if main() else 0)
