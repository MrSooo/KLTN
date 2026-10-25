"""A7: kiểm tra đồ thị gộp: gộp bộ ba, bản sao text, cạnh treo, kiểm 7a-7f, ghi file, trạng thái gốc rồi theo ngày (nạp A4).

Chạy: python -I src/test_a7.py   (các hàm test_* cũng chạy được bằng pytest nếu có cài)
Chạy a6_general_exceptions.py rồi a7_graph.py cho cả hai file trước (python -I src/<file>.py <file md>); test_files_on_disk đọc file đã ghi.
Các test theo ngày tự chạy a4.apply_series vào thư mục tạm, không cần file a4_* trên đĩa.
"""
import collections
import contextlib
import io
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import a2_edges as a2
import a3_exceptions as a3
import a4_versions as a4
import a5_checks as a5
import a6_general_exceptions as a6
import a7_graph as a7

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_FILE = ROOT / "data" / "sample" / "blds2015_5dieu.md"
FULL_FILE = ROOT / "data" / "raw" / "blds2015_p4.md"
DEV_DIR = ROOT / "data" / "dev_amend"
FILES = [("mẫu", SAMPLE_FILE), ("đầy đủ", FULL_FILE)]  # luôn mẫu trước
P = "BLDS2015."

# Số kỳ vọng (nút, cạnh, nút duplicate): cộng độc lập ở test_files_match_independent_counts, không lấy từ a7.EXPECTED.
REFERENCE = {SAMPLE_FILE: (35, 64, 0), FULL_FILE: (220, 364, 4)}
DUPLICATE_PAIRS = [(P + a, P + b) for a, b in (("D617.K2.c", "D617.K1.d"), ("D618.K2.b", "D618.K1.b"),
                                               ("D618.K2.c", "D618.K1.c"), ("D637.K1", "D632.K1"))]


@contextlib.contextmanager
def patched(module, **attrs):
    saved = {k: getattr(module, k) for k in attrs}
    for k, v in attrs.items():
        setattr(module, k, v)
    try:
        yield
    finally:
        for k, v in saved.items():
            setattr(module, k, v)


def unit(code, type_, text=None):
    return a7.node(code, type_, number=code.rsplit(".", 1)[-1], text=text)


def edge(s, p, o, label="t", evidence="", method=None):
    return {"s": s, "p": p, "o": o, "evidence": evidence, "method": method, "status": a7.OK, "sources": [label]}


def graph_of(units, edges=(), conditions=()):
    es = a7.EdgeSet()
    for e in edges:
        es.add(e.get("label", "t"), e)
    return a7.assemble(list(units), list(conditions), es, {})


def problems_of(checks, check_id):
    return [p for c in checks if c.id == check_id for p in c.problems]


# ---- gộp bộ ba ----

def test_edgeset_merges_same_triple_from_two_sources():
    es = a7.EdgeSet()
    es.add("a2_refs", {"s": "X.D1", "p": "refers_to", "o": "X.D2", "evidence": "Điều 2"})
    es.add("a3_exceptions", {"s": "X.D1", "p": "refers_to", "o": "X.D2", "evidence": "điều 2 này", "method": "m"})
    es.add("a2_refs", {"s": "X.D1", "p": "refers_to", "o": "X.D2", "evidence": "Điều 2"})  # evidence lặp: không thêm
    es.add("a2_edges", {"s": "X.D1", "p": "contains", "o": "X.D1.K1", "evidence": ""})
    rows = es.rows()
    assert len(rows) == 2, rows
    assert rows[0]["sources"] == ["a2_refs", "a3_exceptions", "a2_refs"] and rows[0]["evidences"] == ["Điều 2", "điều 2 này"], rows[0]
    assert rows[0]["evidence"] == "Điều 2" and rows[0]["method"] is None, rows[0]  # giữ dòng đầu
    assert "evidences" not in rows[1] and rows[1]["sources"] == ["a2_edges"], rows[1]
    assert es.merged() == [("X.D1", "refers_to", "X.D2", 3)]


def test_edgeset_keeps_first_seen_order_and_remove():
    es = a7.EdgeSet()
    for o in ("B", "A", "C"):
        es.add("t", {"s": "S", "p": "p", "o": o})
    es.add("t", {"s": "S", "p": "p", "o": "B"})
    assert [e["o"] for e in es.rows()] == ["B", "A", "C"]
    es.remove(("S", "p", "A"))
    assert [e["o"] for e in es.rows()] == ["B", "C"] and ("S", "p", "A") not in es.seen


# ---- bản sao text ----

def test_duplicate_pair_and_triple_group_point_to_first():
    units = [unit("X.D1", "dieu"), unit("X.D1.K1", "khoan"), unit("X.D1.K1.a", "diem", "Được hưởng thù lao."),
             unit("X.D1.K1.b", "diem", "được hưởng  thù lao;"), unit("X.D1.K1.c", "diem", "Khác hẳn."),
             unit("X.D1.K1.d", "diem", "ĐƯỢC HƯỞNG THÙ LAO")]
    g = graph_of(units)
    assert [(e["s"], e["o"], e["method"]) for e in g.edges if e["p"] == a7.SAME_TEXT] == [
        ("X.D1.K1.b", "X.D1.K1.a", a7.SAME_METHOD), ("X.D1.K1.d", "X.D1.K1.a", a7.SAME_METHOD)]
    assert {n["id"]: n["status"] for n in g.nodes} == {"X.D1": "ok", "X.D1.K1": "ok", "X.D1.K1.a": "ok", "X.D1.K1.b": "duplicate",
                                                       "X.D1.K1.c": "ok", "X.D1.K1.d": "duplicate"}


def test_same_text_of_different_type_is_not_grouped():
    g = graph_of([unit("X.D1", "dieu"), unit("X.D1.K1", "khoan", "Nội dung A."), unit("X.D1.K1.a", "diem", "Nội dung A.")])
    assert g.edges == [] and all(n["status"] == "ok" for n in g.nodes)


def test_units_without_text_and_condition_nodes_are_not_grouped():
    cond1, cond2 = (a7.node(f"X.C_{i}", a6.COND_TYPE, text="có thỏa thuận khác") for i in (1, 2))
    g = graph_of([unit("X.D1", "dieu"), unit("X.D2", "dieu"), unit("X.D2.K1", "khoan", "có thỏa thuận khác")], conditions=[cond1, cond2])
    assert g.edges == [] and all(n["status"] == "ok" for n in g.nodes), g


# ---- nạp đầu vào ----

def test_unit_nodes_group_triples_and_keep_first_line():
    rows = [(1, {"s": "X.D1", "p": "type", "o": "dieu"}), (2, {"s": "X.D1", "p": "number", "o": "1"}),
            (3, {"s": "X.D1", "p": "heading", "o": "Tên"}), (4, {"s": "X.D1.K1", "p": "type", "o": "khoan"}),
            (5, {"s": "X.D1.K1", "p": "text", "o": "A"}), (6, {"s": "X.D1.K1", "p": "text", "o": "B"})]
    nodes = a7.unit_nodes(rows)
    assert [(n["id"], n["type"], n["heading"], n["text"]) for n in nodes] == [("X.D1", "dieu", "Tên", None), ("X.D1.K1", "khoan", None, "A")]
    try:
        a7.unit_nodes([(1, {"s": "X.D9", "p": "number", "o": "9"})])
    except ValueError as e:
        assert "X.D9" in str(e)
    else:
        raise AssertionError("thiếu type phải ValueError")


# ---- kiểm 7a-7f ----

def structural(units):
    out = []
    for u in units:
        if u["type"] != "dieu":
            parent = u["id"].rsplit(".", 1)[0]
            out += [edge(parent, "contains", u["id"]), edge(u["id"], "part_of", parent)]
    return out


def test_check_graph_is_clean_on_a_mini_graph():
    units = [unit("X.D1", "dieu"), unit("X.D1.K1", "khoan", "A."), unit("X.D1.K1.a", "diem", "B."), unit("X.D2", "dieu"),
             unit("X.D2.K1", "khoan", "A.")]
    g = graph_of(units, structural(units) + [edge("X.D2.K1", "refers_to", "X.D1.K1")])
    checks = a7.check_graph(g, a7.Expect(nodes=5, edges=len(g.edges), duplicates=1))
    assert a5.failures(checks) == 0, [(c.id, c.problems) for c in checks]
    assert [c.id for c in checks] == ["7a", "7b", "7c", "7d", "7e", "7f", "7g"]
    assert [c.id for c in a7.check_graph(g)] == ["7a", "7b", "7c", "7d", "7e", "7g"]  # không có expect thì bỏ 7f


def test_find_cycle():
    E = lambda *pairs, p="exception_of": [edge(s, p, o) for s, o in pairs]
    assert a7.find_cycle(E(("A", "B"), ("B", "C")), "exception_of") is None
    assert a7.find_cycle(E(("A", "B"), ("B", "A")), "exception_of") == ["A", "B", "A"]
    assert a7.find_cycle(E(("X", "A"), ("A", "B"), ("B", "C"), ("C", "A")), "exception_of") == ["A", "B", "C", "A"]
    assert a7.find_cycle(E(("A", "A")), "exception_of") == ["A", "A"]
    assert a7.find_cycle(E(("A", "B"), ("B", "A"), p="refers_to"), "exception_of") is None  # chỉ xét đúng predicate
    # nhánh đã duyệt xong không bị coi là vòng (kim cương A→B, A→C, B→D, C→D)
    assert a7.find_cycle(E(("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")), "exception_of") is None


def test_check_7g_exception_cycle_fails_refers_to_cycle_is_only_noted():
    units = [unit("X.D1", "dieu", "A."), unit("X.D2", "dieu", "B.")]
    mixed = graph_of(units, [edge("X.D1", "refers_to", "X.D2"), edge("X.D2", "exception_of", "X.D1"),
                             edge("X.D2", "refers_to", "X.D1")])
    c7g = [c for c in a7.check_graph(mixed) if c.id == "7g"][0]
    assert c7g.problems == [] and "X.D1 → X.D2 → X.D1" in c7g.summary, c7g
    loop = graph_of(units, [edge("X.D1", "exception_of", "X.D2"), edge("X.D2", "exception_of", "X.D1")])
    assert problems_of(a7.check_graph(loop), "7g") == ["vòng exception_of: X.D1 → X.D2 → X.D1"]


def test_check_graph_catches_each_kind_of_problem():
    units = [unit("X.D1", "dieu"), unit("X.D1.K1", "khoan", "A."), unit("X.D1.K2", "khoan", "A."), unit("X.D2", "dieu")]
    good = graph_of(units, structural(units))
    assert a5.failures(a7.check_graph(good)) == 0

    def broken(nodes=None, edges=None):
        return a7.Graph(nodes if nodes is not None else [dict(n) for n in good.nodes],
                        edges if edges is not None else [dict(e) for e in good.edges], [], {})

    def with_edges(*extra):
        return broken(edges=[dict(e) for e in good.edges] + list(extra))

    assert any("lặp 2 lần" in p for p in problems_of(a7.check_graph(broken(nodes=good.nodes + [dict(good.nodes[0])])), "7a"))
    bad_status = [dict(n) for n in good.nodes]
    bad_status[0]["status"] = "zzz"
    assert any("status" in p for p in problems_of(a7.check_graph(broken(nodes=bad_status)), "7a"))
    assert any("X.D9 không phải nút" in p for p in problems_of(a7.check_graph(with_edges(edge("X.D1", "refers_to", "X.D9"))), "7b"))
    dangling_to_node = {**edge("X.D1", "refers_to", "X.D2"), "status": a7.DANGLING}
    assert any("cạnh treo" in p for p in problems_of(a7.check_graph(with_edges(dangling_to_node)), "7b"))
    dangling_ok = {**edge("X.D1", "refers_to", "X.D9"), "status": a7.DANGLING}
    assert problems_of(a7.check_graph(with_edges(dangling_ok)), "7b") == []
    assert any("status" in p for p in problems_of(a7.check_graph(with_edges({**edge("X.D1", "refers_to", "X.D2"), "status": "zzz"})), "7b"))
    assert any("lặp 2 lần" in p for p in problems_of(a7.check_graph(with_edges(*[edge("X.D1", "refers_to", "X.D2")] * 2)), "7c"))
    # 7d: K2 cùng text với K1 nhưng thiếu cạnh và nhãn đã bị xoá
    stripped = a7.Graph(units and [dict(n, status="ok") for n in good.nodes],
                        [e for e in good.edges if e["p"] != a7.SAME_TEXT], [], {})
    assert any("X.D1.K2" in p and "status" in p for p in problems_of(a7.check_graph(stripped), "7d"))
    assert any("same_text_as tới []" in p for p in problems_of(a7.check_graph(stripped), "7d"))
    wrong_target = [dict(e) for e in good.edges]
    for e in wrong_target:
        if e["p"] == a7.SAME_TEXT:
            e["o"] = "X.D2"
    assert any("cần ['X.D1.K1']" in p for p in problems_of(a7.check_graph(broken(edges=wrong_target)), "7d"))
    assert any("không phải bản sau" in p for p in problems_of(a7.check_graph(with_edges(edge("X.D2", a7.SAME_TEXT, "X.D1"))), "7d"))
    phantom = [dict(n) for n in good.nodes]
    phantom[0]["status"] = a7.DUPLICATE
    assert any("không có đơn vị đứng trước" in p for p in problems_of(a7.check_graph(broken(nodes=phantom)), "7d"))
    # 7e: thiếu part_of, cha sai, contains lẻ
    no_part = [e for e in good.edges if not (e["p"] == "part_of" and e["s"] == "X.D1.K1")]
    assert any("X.D1.K1: part_of tới []" in p for p in problems_of(a7.check_graph(broken(edges=no_part)), "7e"))
    assert any("không có part_of ngược" in p for p in problems_of(a7.check_graph(broken(edges=no_part)), "7e"))
    wrong_parent = [dict(e) if not (e["p"] == "part_of" and e["s"] == "X.D1.K1") else dict(e, o="X.D2") for e in good.edges]
    assert any("cần ['X.D1']" in p for p in problems_of(a7.check_graph(broken(edges=wrong_parent)), "7e"))
    assert any("là Điều nhưng có part_of" in p for p in problems_of(a7.check_graph(with_edges(edge("X.D2", "part_of", "X.D1"))), "7e"))
    # 7f
    assert len(problems_of(a7.check_graph(good, a7.Expect(nodes=1, edges=1, duplicates=0)), "7f")) == 3


# ---- trạng thái gốc, trên file thật ----

def count_lines(path):
    with open(path, encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def test_files_match_independent_counts():
    """Cộng số dòng của file nguồn và đếm bản sao bằng Counter riêng, không qua EdgeSet / mark_duplicates / a7.EXPECTED."""
    for name, path in FILES:
        graph, _ = a7.graph_base(path)
        a1 = [json.loads(line) for line in a2.triples_path(path).read_text(encoding="utf-8").split("\n") if line]
        cond_ids = {json.loads(line)["s"] for line in a6.conditions_path(path).read_text(encoding="utf-8").split("\n") if line}
        types = {r["s"]: r["o"] for r in a1 if r["p"] == "type"}
        texts = {r["s"]: r["o"] for r in a1 if r["p"] == "text"}
        groups = collections.Counter((types[s], t.casefold().rstrip(".;:, ")) for s, t in texts.items())
        n_dup = sum(c - 1 for c in groups.values())
        n_edges = sum(count_lines(p) for p in (a2.edges_path(path), a2.refs_path(path), a3.exceptions_path(path), a6.exceptions_path(path)))
        want = (len(types) + len(cond_ids), n_edges + n_dup, n_dup)
        assert want == REFERENCE[path], f"file {name}: cộng độc lập {want}, bảng {REFERENCE[path]}"
        got = (len(graph.nodes), len(graph.edges), sum(1 for n in graph.nodes if n["status"] == "duplicate"))
        assert got == want, f"file {name}: đồ thị {got}, cộng độc lập {want}"
        assert a7.EXPECTED[path.stem] == a7.Expect(*REFERENCE[path]), f"file {name}: EXPECTED lệch bảng test"


def test_files_graph_content():
    for name, path in FILES:
        graph, _ = a7.graph_base(path)
        assert a5.failures(a7.check_graph(graph, a7.EXPECTED[path.stem])) == 0, f"file {name}"
        assert graph.merged == [], f"file {name}: dữ liệu thật không có bộ ba trùng"
        assert all(e["status"] == "ok" for e in graph.edges) and all(len(e["sources"]) == 1 for e in graph.edges)
        pairs = [(e["s"], e["o"]) for e in graph.edges if e["p"] == a7.SAME_TEXT]
        assert pairs == (DUPLICATE_PAIRS if path == FULL_FILE else []), f"file {name}: {pairs}"
        # mọi cạnh nguồn vào đồ thị nguyên vẹn: (s, p, o, evidence, method) khớp file gốc
        for label, rows_path in (("a2_edges", a2.edges_path(path)), ("a2_refs", a2.refs_path(path)),
                                 ("a3_exceptions", a3.exceptions_path(path)), ("a6_exceptions", a6.exceptions_path(path))):
            src_rows = [json.loads(line) for line in rows_path.read_text(encoding="utf-8").split("\n") if line]
            mine = [e for e in graph.edges if e["sources"] == [label]]
            assert [(e["s"], e["p"], e["o"], e["evidence"], e["method"]) for e in mine] == \
                   [(r["s"], r["p"], r["o"], r["evidence"], r.get("method")) for r in src_rows], f"file {name}: {label}"
    graph, _ = a7.graph_base(FULL_FILE)
    cond = {n["id"]: n for n in graph.nodes if n["type"] == a6.COND_TYPE}
    assert len(cond) == 5 and all(n["text"] and n["number"] is None and n["status"] == "ok" for n in cond.values())
    exc_to_unit = [e for e in graph.edges if e["p"] == "exception_of" and e["s"] in cond]
    assert len(exc_to_unit) == 9 and all(e["method"] == a6.METHOD for e in exc_to_unit)


def test_files_on_disk():
    """Chạy a7_graph.py <md> trước. File trên đĩa phải khớp dựng lại."""
    for name, path in FILES:
        graph, _ = a7.graph_base(path)
        stem = path.stem
        for on_disk in (a7.nodes_path(stem), a7.edges_path(stem), a7.report_path(stem)):
            assert on_disk.exists(), f"file {name}: chưa có {on_disk}, chạy a7_graph.py trước"
        nodes = [json.loads(line) for line in a7.nodes_path(stem).read_text(encoding="utf-8").split("\n") if line]
        edges = [json.loads(line) for line in a7.edges_path(stem).read_text(encoding="utf-8").split("\n") if line]
        assert nodes == graph.nodes and edges == graph.edges, f"file {name}: khác dựng lại"
        assert all(list(n) == ["id", "type", "number", "heading", "text", "source_line", "status"] for n in nodes)
        assert all(list(e)[:7] == ["s", "p", "o", "evidence", "method", "status", "sources"] for e in edges)
        assert a7.report_path(stem).read_text(encoding="utf-8").rstrip().endswith("KẾT LUẬN: ĐẠT"), f"file {name}: báo cáo"


def test_base_cli_writes_files_and_exit_codes():
    with tempfile.TemporaryDirectory() as tmp:
        with patched(a7, OUT_DIR=Path(tmp), DOCS_DIR=Path(tmp)), contextlib.redirect_stdout(io.StringIO()) as out:
            assert a7.main([str(FULL_FILE)]) == 0
        names = sorted(p.name for p in Path(tmp).iterdir())
        assert names == ["a7_blds2015_p4_edges.jsonl", "a7_blds2015_p4_nodes.jsonl", "a7_report_blds2015_p4.txt"], names
        assert "nút 220/220, cạnh 364/364, duplicate 4/4" in out.getvalue()
    # stem chưa có trong EXPECTED: thoát với lỗi, không ghi gì
    with tempfile.TemporaryDirectory() as tmp:
        with patched(a7, OUT_DIR=Path(tmp), DOCS_DIR=Path(tmp)):
            try:
                a7.main([str(ROOT / "data" / "sample" / "khac.md")])
            except SystemExit as e:
                assert "chưa có số đối chiếu" in str(e.code), e.code
            else:
                raise AssertionError("phải thoát")
        assert list(Path(tmp).iterdir()) == []
    # kiểm 7f không đạt: ghi báo cáo, thoát 1, không ghi file dữ liệu
    with tempfile.TemporaryDirectory() as tmp:
        wrong = dict(a7.EXPECTED, blds2015_5dieu=a7.Expect(nodes=1, edges=1, duplicates=0))
        with patched(a7, OUT_DIR=Path(tmp), DOCS_DIR=Path(tmp), EXPECTED=wrong), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            assert a7.main([str(SAMPLE_FILE)]) == 1
        assert [p.name for p in Path(tmp).iterdir()] == ["a7_report_blds2015_5dieu.txt"]
        assert "KHÔNG ĐẠT" in (Path(tmp) / "a7_report_blds2015_5dieu.txt").read_text(encoding="utf-8")


def test_versions_and_date_must_come_together():
    for argv in ([str(FULL_FILE), "--versions", "x"], [str(FULL_FILE), "--date", "2027-01-01"]):
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                a7.main(argv)
        except SystemExit as e:
            assert e.code == 2, e.code
        else:
            raise AssertionError("phải thoát mã 2")


# ---- theo ngày: thế giới nhỏ dựng tay ----

MINI_UNITS = {  # mã -> (type, text); đủ để thử add / close / dangling / source_closed / đơn vị mới / đơn vị bị đóng
    "X.D1": ("dieu", "Quy tắc chung."), "X.D1.K1": ("khoan", "Khoản một, theo Điều 2."),
    "X.D1.K2": ("khoan", "Khoản hai."), "X.D2": ("dieu", "Điều hai."),
}


def jl(rows):
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)


def vrow(code, version, type_, text, frm=None, to=None):
    return {"id": code, "version": version, "type": type_, "number": code.rsplit(".", 1)[-1], "heading": None, "text": text,
            "effective_from": frm, "effective_to": to, "previous_version": version - 1 if version > 1 else None,
            "source_doc": None, "directive_seq": None}


def mini_world(tmp, changes=None):
    """Ghi file A1-A3 và a4_mini_{versions,edge_changes} của stem "mini" vào tmp; trả về đường dẫn file versions."""
    tmp = Path(tmp)
    a1 = []
    for code, (t, text) in MINI_UNITS.items():
        a1 += [{"s": code, "p": "type", "o": t}, {"s": code, "p": "number", "o": code.rsplit(".", 1)[-1]}]
        a1.append({"s": code, "p": "text", "o": text})
    e = lambda s, p, o, ev="": {"s": s, "p": p, "o": o, "evidence": ev}
    (tmp / "a1_triples_mini.jsonl").write_text(jl(a1), encoding="utf-8")
    (tmp / "a2_edges_mini.jsonl").write_text(jl([e("X.D1", "contains", "X.D1.K1"), e("X.D1.K1", "part_of", "X.D1"),
                                                 e("X.D1", "contains", "X.D1.K2"), e("X.D1.K2", "part_of", "X.D1")]), encoding="utf-8")
    (tmp / "a2_refs_mini.jsonl").write_text(jl([e("X.D1.K1", "refers_to", "X.D2", "Điều 2"), e("X.D1.K2", "refers_to", "X.D2", "Điều 2"),
                                                e("X.D2", "refers_to", "X.D1", "Điều 1")]), encoding="utf-8")
    (tmp / "a3_exceptions_mini.jsonl").write_text(jl([{**e("X.D1.K2", "exception_of", "X.D1.K1", "x"), "method": "not_apply_pattern"}]),
                                                  encoding="utf-8")
    versions = [vrow("X.D1", 1, "dieu", "Quy tắc chung."),
                vrow("X.D1.K1", 1, "khoan", MINI_UNITS["X.D1.K1"][1], None, "2027-01-01"),
                vrow("X.D1.K1", 2, "khoan", "Khoản một mới, theo Điều 3.", "2027-01-01"),
                vrow("X.D1.K2", 1, "khoan", "Khoản hai."),
                vrow("X.D2", 1, "dieu", "Điều hai.", None, "2027-03-01"),
                vrow("X.D3", 1, "dieu", "Điều ba, trừ trường hợp có thỏa thuận khác.", "2027-01-01")]
    if changes is None:
        changes = [{"op": "close", "s": "X.D1.K1", "p": "refers_to", "o": "X.D2", "at": "2027-01-01"},
                   {"op": "add", "s": "X.D1.K1", "p": "refers_to", "o": "X.D3", "at": "2027-01-01", "evidence": "Điều 3"},
                   {"op": "add", "s": "X.D1.K2", "p": "refers_to", "o": "X.D1.K1", "at": "2027-06-01", "evidence": "khoản 1"}]
    (tmp / "a4_x_versions.jsonl").write_text(jl(versions), encoding="utf-8")
    (tmp / "a4_x_edge_changes.jsonl").write_text(jl(changes), encoding="utf-8")
    return tmp / "a4_x_versions.jsonl"


def mini_graph(date, changes=None):
    with tempfile.TemporaryDirectory() as tmp:
        versions = mini_world(tmp, changes)
        with patched(a2, PROCESSED_DIR=Path(tmp)):
            graph, _ = a7.graph_at("mini.md", versions, date)
    return graph


def triples(graph, only=None):
    return [(e["s"], e["p"], e["o"], e["status"]) for e in graph.edges if only is None or e["p"] in only]


def test_mini_before_any_change_is_the_base():
    g = mini_graph("2026-12-31")
    assert [n["id"] for n in g.nodes if n["type"] != a6.COND_TYPE] == ["X.D1", "X.D1.K1", "X.D1.K2", "X.D2"]
    assert triples(g, ("refers_to", "exception_of")) == [
        ("X.D1.K1", "refers_to", "X.D2", "ok"), ("X.D1.K2", "refers_to", "X.D2", "ok"), ("X.D2", "refers_to", "X.D1", "ok"),
        ("X.D1.K2", "exception_of", "X.D1.K1", "ok")]
    assert g.notes["applied"] == {} and g.notes["dangling"] == [] and g.notes["dropped"] == {}
    assert next(n for n in g.nodes if n["id"] == "X.D1.K1")["version"] == 1


def test_mini_edge_changes_apply_on_their_date():
    g = mini_graph("2027-01-01")  # chính ngày hiệu lực: close và add đã có hiệu lực
    assert [(n["id"], n["version"]) for n in g.nodes if n["type"] != a6.COND_TYPE] == [
        ("X.D1", 1), ("X.D1.K1", 2), ("X.D1.K2", 1), ("X.D2", 1), ("X.D3", 1)]
    assert triples(g, ("refers_to",)) == [("X.D1.K2", "refers_to", "X.D2", "ok"), ("X.D2", "refers_to", "X.D1", "ok"),
                                          ("X.D1.K1", "refers_to", "X.D3", "ok")], triples(g, ("refers_to",))
    assert g.notes["applied"] == {"close": 1, "add": 1}
    assert [(n["id"], n["text"]) for n in g.nodes if n["type"] == a6.COND_TYPE] == [(a6.condition_id("X", "có thỏa thuận khác"), "có thỏa thuận khác")]
    assert triples(g, ("exception_of",))[-1] == (a6.condition_id("X", "có thỏa thuận khác"), "exception_of", "X.D3", "ok")


def test_mini_dangling_and_source_closed_after_unit_is_closed():
    g = mini_graph("2027-03-01")  # D2 hết hiệu lực đúng ngày này (to = 2027-03-01 nên đã đóng tại T)
    assert [n["id"] for n in g.nodes if n["type"] != a6.COND_TYPE] == ["X.D1", "X.D1.K1", "X.D1.K2", "X.D3"]
    assert g.notes["dangling"] == [("X.D1.K2", "refers_to", "X.D2")], g.notes["dangling"]
    assert ("X.D1.K2", "refers_to", "X.D2", "dangling") in triples(g)
    assert g.notes["dropped"] == {"source_closed": 1}, g.notes["dropped"]  # D2 refers_to D1: nguồn đã đóng
    assert all(s != "X.D2" for s, _, _, _ in triples(g))
    assert a5.failures(a7.check_graph(g)) == 0


def test_mini_later_add_is_not_applied_early():
    early, late = mini_graph("2027-05-31"), mini_graph("2027-06-01")
    key = ("X.D1.K2", "refers_to", "X.D1.K1", "ok")
    assert key not in triples(early) and key in triples(late)
    assert late.notes["applied"] == {"close": 1, "add": 2}


def test_mini_bad_edge_changes_raise():
    for changes, text in (([{"op": "close", "s": "X.D1", "p": "refers_to", "o": "X.D2", "at": "2027-01-01"}], "close một cạnh không có"),
                          ([{"op": "zap", "s": "X.D1", "p": "refers_to", "o": "X.D2", "at": "2027-01-01"}], "không phải add/close")):
        try:
            mini_graph("2027-02-01", changes)
        except ValueError as e:
            assert text in str(e), e
        else:
            raise AssertionError(f"phải ValueError: {text}")
    # close của dòng ở sau T không được áp, nên không lỗi dù cạnh không có
    mini_graph("2026-12-31", [{"op": "close", "s": "X.D1", "p": "refers_to", "o": "X.D2", "at": "2027-01-01"}])


def test_mini_versions_from_another_base_is_rejected():
    with tempfile.TemporaryDirectory() as tmp:
        versions = mini_world(tmp)
        (Path(tmp) / "a4_x_versions.jsonl").write_text(jl([vrow("X.D1", 1, "dieu", "Quy tắc chung.")]), encoding="utf-8")
        with patched(a2, PROCESSED_DIR=Path(tmp)):
            try:
                a7.graph_at("mini.md", versions, "2027-01-01")
            except ValueError as e:
                assert "không phải của mini" in str(e), e
            else:
                raise AssertionError("phải ValueError")


def test_versions_file_name_must_match_pattern():
    assert a7.edge_changes_path(Path("d") / "a4_p4_dev05_versions.jsonl") == Path("d") / "a4_p4_dev05_edge_changes.jsonl"
    try:
        a7.edge_changes_path("versions.jsonl")
    except ValueError as e:
        assert "a4_<name>_versions.jsonl" in str(e)
    else:
        raise AssertionError("phải ValueError")
    assert a7.tag_of("data/a4_p4_dev05_versions.jsonl", "2027-01-01") == "p4_dev05_2027-01-01"


# ---- theo ngày: kết quả A4 thật ----

def a4_run(tmp, base, docs, name):
    """Chạy a4.apply_series (không ghi gì vào đĩa của dự án) rồi ghi versions và edge_changes vào tmp; trả về (run, đường dẫn versions)."""
    run = a4.apply_series(base, [str(d) for d in docs], name)
    a4.write_jsonl(run.version_rows(), Path(tmp) / f"a4_{name}_versions.jsonl")
    a4.write_jsonl(run.edge_changes, Path(tmp) / f"a4_{name}_edge_changes.jsonl")
    return run, Path(tmp) / f"a4_{name}_versions.jsonl"


DEV_DOCS = sorted(DEV_DIR.glob("dev0*.md"))


def test_before_every_effective_date_the_graph_is_the_base():
    base, _ = a7.graph_base(FULL_FILE)
    with tempfile.TemporaryDirectory() as tmp:
        _, versions = a4_run(tmp, FULL_FILE, [DEV_DIR / "dev05_bai_bo_ds.md"], "d5")
        at, _ = a7.graph_at(FULL_FILE, versions, "2026-12-31")
    drop = ("version", "effective_from", "source_line")
    assert [{k: v for k, v in n.items() if k not in drop} for n in at.nodes] == [{k: v for k, v in n.items() if k not in drop} for n in base.nodes]
    assert at.edges == base.edges, "cạnh trước mọi ngày hiệu lực phải đúng đồ thị gốc, kể cả thứ tự và sources"
    assert all(n["version"] == 1 and n["effective_from"] is None for n in at.nodes if n["type"] != a6.COND_TYPE)


def test_dev05_closes_units_and_flags_the_broken_reference():
    with tempfile.TemporaryDirectory() as tmp:
        run, versions = a4_run(tmp, FULL_FILE, [DEV_DIR / "dev05_bai_bo_ds.md"], "d5")
        g, _ = a7.graph_at(FULL_FILE, versions, "2027-01-01")
    assert len(run.closed) == 15
    assert len(g.nodes) == 215 - 15 + 5 == 205
    assert {x for x in run.closed} & {n["id"] for n in g.nodes} == set()
    assert g.notes["dangling"] == [(P + "D653", "refers_to", P + "D651")], g.notes["dangling"]
    assert {(s, p, o) for _, s, p, o, _ in run.broken} == set(g.notes["dangling"]), "cạnh treo tại T phải bằng cờ cạnh đứt của A4"
    assert a5.failures(a7.check_graph(g)) == 0


def test_every_dev_document_gives_a_consistent_graph_and_matches_a4_flags():
    for doc in DEV_DOCS:
        with tempfile.TemporaryDirectory() as tmp:
            run, versions = a4_run(tmp, FULL_FILE, [doc], "d")
            date = run.docs[0].date
            g, _ = a7.graph_at(FULL_FILE, versions, date)
        assert a5.failures(a7.check_graph(g)) == 0, (doc.name, [(c.id, c.problems[:2]) for c in a7.check_graph(g) if c.problems])
        units = [n for n in g.nodes if n["type"] != a6.COND_TYPE]
        assert len(units) == 215 + len(run.new) - len(run.closed), doc.name
        assert {(s, p, o) for _, s, p, o, _ in run.broken} == set(g.notes["dangling"]), doc.name
        for code in run.new:  # đơn vị mới kèm contains/part_of đúng cha
            parent = code.rsplit(".", 1)[0] if code.count(".") > 1 else None
            if parent:
                assert (parent, "contains", code, "ok") in triples(g) and (code, "part_of", parent, "ok") in triples(g), (doc.name, code)


def test_dev04_new_units_are_nodes_with_structural_edges():
    with tempfile.TemporaryDirectory() as tmp:
        run, versions = a4_run(tmp, FULL_FILE, [DEV_DIR / "dev04_bo_sung.md"], "d4")
        g, _ = a7.graph_at(FULL_FILE, versions, run.docs[0].date)
    assert run.new, "dev04 phải có đơn vị mới"
    ids = {n["id"] for n in g.nodes}
    assert set(run.new) <= ids
    assert all(n["version"] == 1 and n["effective_from"] == run.docs[0].date for n in g.nodes if n["id"] in run.new)


def test_dev01_dev02_two_dates():
    with tempfile.TemporaryDirectory() as tmp:
        run, versions = a4_run(tmp, FULL_FILE, [DEV_DIR / "dev01_bai_bo_khoan.md", DEV_DIR / "dev02_sua_khoan.md"], "d12")
        first, _ = a7.graph_at(FULL_FILE, versions, "2027-01-01")
        second, _ = a7.graph_at(FULL_FILE, versions, "2027-07-01")
    for g in (first, second):
        assert P + "D621.K2" not in {n["id"] for n in g.nodes}, "dev01 bãi bỏ D621.K2"
        assert len(g.nodes) == 215 - 1 + 5
        assert [e for e in g.edges if e["p"] == "contains"].__len__() == 160 and g.notes["dangling"] == []
        assert a5.failures(a7.check_graph(g)) == 0
    version_of = lambda g: next(n["version"] for n in g.nodes if n["id"] == P + "D621.K1")
    assert (version_of(first), version_of(second)) == (1, 2)
    assert (P + "D644.K2", "refers_to", P + "D621.K1", "ok") in triples(second)


def test_dev08_replace_whole_document_gives_an_empty_graph():
    with tempfile.TemporaryDirectory() as tmp:
        run, versions = a4_run(tmp, FULL_FILE, [DEV_DIR / "dev08_thay_van_ban.md"], "d8")
        before, _ = a7.graph_at(FULL_FILE, versions, "2026-12-31")
        after, _ = a7.graph_at(FULL_FILE, versions, run.docs[0].date)
    assert len(before.nodes) == 220
    assert after.nodes == [] and after.edges == [] and after.notes["dangling"] == []
    assert a5.failures(a7.check_graph(after)) == 0


def test_at_date_cli_writes_tagged_files():
    with tempfile.TemporaryDirectory() as tmp:
        run, versions = a4_run(tmp, FULL_FILE, [DEV_DIR / "dev05_bai_bo_ds.md"], "d5")
        out = Path(tmp) / "out"
        with patched(a7, OUT_DIR=out, DOCS_DIR=out), contextlib.redirect_stdout(io.StringIO()) as buf:
            assert a7.main([str(FULL_FILE), "--versions", str(versions), "--date", "2027-01-01"]) == 0
        assert sorted(p.name for p in out.iterdir()) == [
            "a7_blds2015_p4_d5_2027-01-01_edges.jsonl", "a7_blds2015_p4_d5_2027-01-01_nodes.jsonl", "a7_report_blds2015_p4_d5_2027-01-01.txt"]
        report = (out / "a7_report_blds2015_p4_d5_2027-01-01.txt").read_text(encoding="utf-8")
        assert "BLDS2015.D653 refers_to BLDS2015.D651" in report and report.rstrip().endswith("KẾT LUẬN: ĐẠT")
        assert "[7e]" in report and "[7f]" not in report, "chế độ theo ngày kiểm 7a-7e, không dùng bảng EXPECTED"
        # ngày sai dạng: thoát với lỗi, không ghi file mới
        with patched(a7, OUT_DIR=out, DOCS_DIR=out), contextlib.redirect_stdout(io.StringIO()):
            try:
                a7.main([str(FULL_FILE), "--versions", str(versions), "--date", "01/01/2027"])
            except SystemExit as e:
                assert "YYYY-MM-DD" in str(e.code), e.code
            else:
                raise AssertionError("phải thoát")
        assert len(list(out.iterdir())) == 3


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
