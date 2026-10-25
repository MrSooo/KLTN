"""A6: kiểm tra ngoại lệ chung (nút điều kiện + cạnh exception_of) trên ví dụ dựng tay, file mẫu rồi file đầy đủ.

Chạy: python -I src/test_a6.py   (các hàm test_* cũng chạy được bằng pytest nếu có cài)
Chạy a6_general_exceptions.py cho cả hai file trước (python -I src/a6_general_exceptions.py <file md>), test_files_on_disk đọc file đã ghi.
"""
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
import a6_general_exceptions as a6

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_FILE = ROOT / "data" / "sample" / "blds2015_5dieu.md"
FULL_FILE = ROOT / "data" / "raw" / "blds2015_p4.md"
FILES = [("mẫu", SAMPLE_FILE), ("đầy đủ", FULL_FILE)]  # luôn mẫu trước
P = "BLDS2015."

# Số kỳ vọng: 9 là số lần "trừ trường hợp" đếm độc lập ở test_independent_count_of_phrase (đếm trên file md, không qua TRIGGER_RE).
GENERAL_UNITS = {
    SAMPLE_FILE: [],
    FULL_FILE: [P + c for c in ("D615.K1", "D615.K3", "D617.K1.a", "D619", "D620.K1", "D646.K3", "D659.K1", "D662.K1", "D662.K2")],
}
SHARED_CLAUSE = "có thỏa thuận khác"  # 5 câu của file đầy đủ dùng chung một nút
SHARED_UNITS = [P + c for c in ("D615.K1", "D615.K3", "D659.K1", "D662.K1", "D662.K2")]
NODE_COUNT = {SAMPLE_FILE: 0, FULL_FILE: 5}


def mini_units(spec):
    """Đơn vị nhỏ dựng tay: {mã: (type, text hoặc None)}. Giữ thứ tự khai báo."""
    return {code: {"type": t, "number": "x", "source_line": 1, **({"text": text} if text else {})}
            for code, (t, text) in spec.items()}


def load(path):
    return a2.load_units(a2.triples_path(path))


def general_of(spec):
    return a6.find_general(mini_units(spec))


def test_single_clause_makes_node_and_edge():
    r = general_of({"X.D1": ("dieu", None), "X.D1.K1": ("khoan", "Người lập di chúc có quyền A, trừ trường hợp có thỏa thuận khác.")})
    assert [clause for _, clause in r.nodes] == ["có thỏa thuận khác"], r.nodes
    cond = r.nodes[0][0]
    assert r.edges == [(cond, "exception_of", "X.D1.K1", "trừ trường hợp có thỏa thuận khác.", a6.METHOD)], r.edges
    assert r.handled == [("X.D1.K1", "trừ")] and r.unhandled == [] and r.skipped == []
    assert re.fullmatch(r"X\.C_[0-9a-f]{8}", cond), cond


def test_same_clause_in_two_units_shares_one_node():
    r = general_of({"X.D1": ("dieu", "Quy tắc A, trừ trường hợp có thỏa thuận khác."),
                    "X.D2": ("dieu", "Quy tắc B, trừ trường hợp có thỏa thuận khác."),
                    "X.D3": ("dieu", "Quy tắc C, trừ trường hợp khác hẳn.")})
    assert len(r.nodes) == 2, r.nodes
    assert [(s == r.nodes[0][0], o) for s, _, o, _, _ in r.edges] == [(True, "X.D1"), (True, "X.D2"), (False, "X.D3")], r.edges


def test_case_and_trailing_punctuation_variants_merge():
    r = general_of({"X.D1": ("dieu", "A, trừ trường hợp Có thỏa  thuận khác."),
                    "X.D2": ("dieu", "B, trừ trường hợp có thỏa thuận khác;"),
                    "X.D3": ("dieu", "C, trừ trường hợp có thỏa thuận khác")})
    assert len(r.nodes) == 1 and len(r.edges) == 3, r
    assert r.nodes[0][1] == "Có thỏa  thuận khác", r.nodes  # nút giữ mệnh đề nguyên văn của lần đầu, đã bỏ dấu cuối
    assert a6.norm_text("Có thỏa  thuận khác.;") == "có thỏa thuận khác"


def test_ngoai_tru_truong_hop_also_matches():
    r = general_of({"X.D1": ("dieu", "A, ngoại trừ trường hợp pháp luật có quy định khác.")})
    assert len(r.edges) == 1 and r.edges[0][3] == "ngoại trừ trường hợp pháp luật có quy định khác.", r.edges
    assert r.nodes[0][1] == "pháp luật có quy định khác"


def test_two_general_clauses_in_one_unit_raises():
    try:
        general_of({"X.D1": ("dieu", "A, trừ trường hợp B, và trừ trường hợp C.")})
    except ValueError as e:
        assert "X.D1" in str(e), e
    else:
        raise AssertionError("phải ValueError")


def test_tru_without_truong_hop_is_unhandled():
    text = "Mọi người đều có quyền, trừ người chưa thành niên."
    r = general_of({"X.D1": ("dieu", text)})
    assert r.nodes == [] and r.edges == [] and r.unhandled == [("X.D1", text)], r


def test_unit_ending_with_list_end_belongs_to_a3():
    r = general_of({"X.D1": ("dieu", "Mọi người đều có thể làm chứng, trừ những người sau đây:"), "X.D1.K1": ("khoan", "Người A.")})
    assert r.edges == [] and r.unhandled == [] and r.skipped == [("X.D1", "trừ")], r
    # đơn vị kết thúc "sau đây:" có hai "trừ trường hợp": việc báo lỗi là của A3, A6 không báo
    r = general_of({"X.D1": ("dieu", "A, trừ trường hợp B, trừ trường hợp C, trừ những người sau đây:")})
    assert r.edges == [] and len(r.skipped) == 3, r


def test_khong_ap_dung_is_not_a6_territory():
    r = general_of({"X.D1": ("dieu", None), "X.D1.K1": ("khoan", "Quy định này không áp dụng cho ai.")})
    assert r.nodes == [] and r.edges == [] and r.handled == [] and r.unhandled == [] and r.skipped == [], r


def test_leading_clause_stops_at_first_comma():
    """Review F-04: "Trừ trường hợp X, quy tắc" không được nuốt quy tắc chính vào mệnh đề."""
    full = {c: clause for c, clause in a6.find_general(load(FULL_FILE)).nodes}
    for text, clause in [("Trừ trường hợp pháp luật có quy định khác, người thừa kế phải thực hiện nghĩa vụ tài sản của người chết.",
                          "pháp luật có quy định khác"),
                         ("Quy tắc chung.\nTrừ trường hợp có thỏa thuận khác, di sản được chia đều.", "có thỏa thuận khác")]:
        r = general_of({P + "D1": ("dieu", text)})
        assert [c for _, c in r.nodes] == [clause], (text, r.nodes)
        assert r.nodes[0][0] in full, "phải trùng mã với nút cùng mệnh đề của p4"
        assert r.edges[0][3] == f"Trừ trường hợp {clause}," and r.edges[0][3] in text, r.edges
        assert a6.check_general(mini_units({P + "D1": ("dieu", text)}), r) == []
    try:
        general_of({"X.D1": ("dieu", "Trừ trường hợp có thỏa thuận khác thì di sản được chia đều.")})
    except ValueError as e:
        assert "dấu phẩy" in str(e), e
    else:
        raise AssertionError("đầu đoạn mà không có dấu phẩy phải ValueError")


def test_khong_duoc_ap_dung_is_unhandled_not_lost():
    """Review F-05: "không được áp dụng" không phải trigger của A2/A3 nhưng phải hiện ra ở unhandled của A6."""
    text = "Quy định này không được áp dụng cho người chưa thành niên."
    units = mini_units({"X.D1": ("dieu", text)})
    r = a6.find_general(units)
    assert r.nodes == [] and r.edges == [] and r.unhandled == [("X.D1", text)], r
    assert a6.check_general(units, r) == []
    # kể cả trong đơn vị kết thúc "sau đây:" (A3 chỉ nhận trigger "trừ")
    text = "Không được áp dụng, trừ những người sau đây:"
    r = general_of({"X.D1": ("dieu", text), "X.D1.K1": ("khoan", "Người A.")})
    assert r.unhandled == [("X.D1", text)] and r.skipped == [("X.D1", "trừ")], r


def test_clause_stops_at_end_of_paragraph():
    text = "Quy tắc A, trừ trường hợp có thỏa thuận khác.\nĐoạn hai nói về việc khác."
    r = general_of({"X.D1": ("dieu", text)})
    assert [clause for _, clause in r.nodes] == ["có thỏa thuận khác"], r.nodes
    assert r.edges[0][3] == "trừ trường hợp có thỏa thuận khác." and r.edges[0][3] in text


def test_empty_clause_raises():
    try:
        general_of({"X.D1": ("dieu", "Quy tắc A, trừ trường hợp.")})
    except ValueError as e:
        assert "X.D1" in str(e) and "rỗng" in str(e), e
    else:
        raise AssertionError("phải ValueError")


def test_condition_id_is_stable_and_distinct():
    a = a6.condition_id("X", a6.norm_text("Có thỏa thuận khác."))
    assert a == a6.condition_id("X", "có thỏa thuận khác") == "X.C_" + a.split("_")[1]
    assert a != a6.condition_id("Y", "có thỏa thuận khác") and a != a6.condition_id("X", "pháp luật có quy định khác")
    # mã từ file thật không đổi theo thứ tự hay tập đơn vị: đây là mã của "có thỏa thuận khác" đã ghi ở file đầy đủ
    assert a6.condition_id("BLDS2015", SHARED_CLAUSE) == "BLDS2015.C_426b8c79"


def test_hash_collision_raises():
    saved = a6.ID_HEX
    a6.ID_HEX = 0  # mọi khoá cùng mã "X.C_"
    try:
        try:
            general_of({"X.D1": ("dieu", "A, trừ trường hợp một."), "X.D2": ("dieu", "B, trừ trường hợp hai.")})
        except ValueError as e:
            assert "cùng mã băm" in str(e), e
        else:
            raise AssertionError("phải ValueError")
    finally:
        a6.ID_HEX = saved


def test_check_general_catches_problems():
    units = mini_units({"X.D1": ("dieu", "A, trừ trường hợp có thỏa thuận khác."), "X.D2": ("dieu", "B.")})
    good = a6.find_general(units)
    assert a6.check_general(units, good) == []
    cond, _, o, ev, method = good.edges[0]

    def errors(**changes):
        return a6.check_general(units, good._replace(**changes))

    assert any("evidence" in e for e in errors(edges=[(cond, "exception_of", o, "trừ trường hợp khác", method)]))
    assert any("bắt đầu bằng" in e for e in errors(edges=[(cond, "exception_of", o, "có thỏa thuận khác.", method)]))
    assert any("không phải nút điều kiện" in e for e in errors(edges=[("X.D2", "exception_of", o, ev, method)]))
    assert any("không có trong tập đơn vị" in e for e in errors(edges=[(cond, "exception_of", "X.D9", ev, method)]))
    assert any("cạnh trùng" in e for e in errors(edges=good.edges * 2))
    assert any("method" in e for e in errors(edges=[(cond, "exception_of", o, ev, "khac")]))
    assert any("không có cạnh nào" in e for e in errors(edges=[]))
    assert any("mã không khớp băm" in e for e in errors(nodes=[("X.C_00000000", good.nodes[0][1])], edges=[("X.C_00000000", "exception_of", o, ev, method)]))
    assert any("số trigger" in e for e in errors(handled=[]))
    assert any("trùng mã với một đơn vị" in e for e in errors(nodes=[("X.D2", "có thỏa thuận khác")]))


def test_independent_count_of_phrase():
    """Đếm "trừ trường hợp" thẳng trên file md (không qua TRIGGER_RE, A1 hay A2), đối chiếu với số cạnh."""
    for name, path in FILES:
        n = len(re.findall(r"trừ\s+trường\s+hợp", path.read_text(encoding="utf-8"), re.I))
        r = a6.find_general(load(path))
        assert n == len(r.edges) == len(GENERAL_UNITS[path]), f"file {name}: md có {n}, cạnh {len(r.edges)}"


def test_files_edges_and_nodes():
    for name, path in FILES:
        units = load(path)
        r = a6.find_general(units)
        assert [o for _, _, o, _, _ in r.edges] == GENERAL_UNITS[path], f"file {name}: đơn vị"
        assert len(r.nodes) == NODE_COUNT[path], f"file {name}: {len(r.nodes)} nút"
        assert r.unhandled == [], f"file {name}: unhandled"
        assert a6.check_general(units, r) == [], f"file {name}: check"
    r = a6.find_general(load(FULL_FILE))
    shared = [s for s, _ in r.nodes if dict(r.nodes)[s] == SHARED_CLAUSE]
    assert len(shared) == 1
    assert [o for s, _, o, _, _ in r.edges if s == shared[0]] == SHARED_UNITS
    assert len(r.skipped) == 1 and r.skipped[0][0] == P + "D632", r.skipped  # trigger "trừ" của quy tắc 2 A3


def test_a6_covers_exactly_what_a3_left_unhandled():
    """Ở hai file này A3 unhandled không có ca "không áp dụng", nên đơn vị A3 bỏ lại = đơn vị A6 xử lý hoặc unhandled."""
    for name, path in FILES:
        units = load(path)
        _, _, a3_unhandled = a3.find_exceptions(units, a2.build_edges(units))
        r = a6.find_general(units)
        assert sorted({c for c, _ in a3_unhandled}) == sorted({c for c, _ in r.handled} | {c for c, _ in r.unhandled}), f"file {name}"


def test_files_on_disk():
    """Chạy a6_general_exceptions.py <md> trước. File trên đĩa phải khớp dựng lại; A2/A3 không bị lẫn nút điều kiện."""
    for name, path in FILES:
        r = a6.find_general(load(path))
        for on_disk in (a6.conditions_path(path), a6.exceptions_path(path), a6.unhandled_path(path)):
            assert on_disk.exists(), f"file {name}: chưa có {on_disk}, chạy a6_general_exceptions.py trước"
        rows = [json.loads(line) for line in a6.conditions_path(path).read_text(encoding="utf-8").split("\n") if line]
        assert all(list(x) == ["s", "p", "o"] for x in rows), f"file {name}: sai khoá nút"
        assert [(x["s"], x["p"], x["o"]) for x in rows] == [(c, p, o) for c, clause in r.nodes
                                                           for p, o in (("type", "dieu_kien"), ("text", clause))], f"file {name}: nút"
        rows = [json.loads(line) for line in a6.exceptions_path(path).read_text(encoding="utf-8").split("\n") if line]
        assert all(list(x) == ["s", "p", "o", "evidence", "method"] for x in rows), f"file {name}: sai khoá cạnh"
        assert [(x["s"], x["p"], x["o"], x["evidence"], x["method"]) for x in rows] == r.edges, f"file {name}: cạnh"
        lines = a6.unhandled_path(path).read_text(encoding="utf-8").split("\n")
        assert [tuple(x.split("\t")) for x in lines[:-1]] == r.unhandled and lines[-1] == "", f"file {name}: unhandled"
        a3_rows = [json.loads(line) for line in a3.exceptions_path(path).read_text(encoding="utf-8").split("\n") if line]
        assert not any(x["method"] == a6.METHOD for x in a3_rows), f"file {name}: a3_exceptions lẫn cạnh của A6"
        assert not any(x["s"] in dict(r.nodes) for x in a3_rows), f"file {name}: a3_exceptions lẫn nút điều kiện"


def run_cli(units, argv=("x",)):
    """Chạy a6.main trên đơn vị dựng tay, ghi vào thư mục tạm; trả về (mã thoát, {tên file: nội dung}, stdout)."""
    saved = a2.read_units, a6.conditions_path, a6.exceptions_path, a6.unhandled_path
    with tempfile.TemporaryDirectory() as tmp:
        a2.read_units = lambda src: units
        a6.conditions_path = lambda src: Path(tmp) / "c.jsonl"
        a6.exceptions_path = lambda src: Path(tmp) / "e.jsonl"
        a6.unhandled_path = lambda src: Path(tmp) / "u.txt"
        code, out = 0, io.StringIO()
        try:
            try:
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                    a6.main(list(argv))
            except SystemExit as e:
                code = e.code
        finally:
            a2.read_units, a6.conditions_path, a6.exceptions_path, a6.unhandled_path = saved
        files = {p.name: p.read_text(encoding="utf-8") for p in Path(tmp).iterdir()}
    return code, files, out.getvalue()


def test_cli_stops_and_writes_nothing_on_error():
    # lỗi từ find_general (ValueError): hai "trừ trường hợp" trong một đơn vị
    code, files, _ = run_cli(mini_units({"X.D1": ("dieu", "A, trừ trường hợp B, trừ trường hợp C.")}))
    assert code not in (0, None) and files == {}, (code, files)
    # lỗi từ check_general: câu unhandled có xuống dòng nên không ghi được thành một dòng
    code, files, _ = run_cli(mini_units({"X.D1": ("dieu", "Trừ người A.\nĐoạn hai.")}))
    assert code not in (0, None) and files == {}, (code, files)


def test_cli_writes_all_three_files_when_clean():
    units = mini_units({"X.D1": ("dieu", "A, trừ trường hợp có thỏa thuận khác."), "X.D2": ("dieu", "B, trừ trường hợp có thỏa thuận khác."),
                        "X.D3": ("dieu", "Trừ người C.")})
    code, files, out = run_cli(units)
    assert code == 0, code
    cond = a6.condition_id("X", "có thỏa thuận khác")
    assert files["c.jsonl"] == (json.dumps({"s": cond, "p": "type", "o": "dieu_kien"}, ensure_ascii=False) + "\n"
                                + json.dumps({"s": cond, "p": "text", "o": "có thỏa thuận khác"}, ensure_ascii=False) + "\n")
    assert [(json.loads(x)["s"], json.loads(x)["o"]) for x in files["e.jsonl"].split("\n") if x] == [(cond, "X.D1"), (cond, "X.D2")]
    assert files["u.txt"] == "X.D3\tTrừ người C.\n"
    assert "trigger trừ/ngoại trừ: 3 = thuộc A3 0 + đã xử lý 2 + unhandled 1" in out and "nút điều kiện: 1" in out and "cạnh exception_of: 2" in out, out


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
