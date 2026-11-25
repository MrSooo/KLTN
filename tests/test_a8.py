"""A8: kiểm tra phần dựng dữ liệu và ghi trang HTML xem đồ thị. Phần JavaScript trong khung không chạy ở đây (xem bằng trình duyệt).

Chạy: python -I tests/test_a8.py   (các hàm test_* cũng chạy được bằng pytest nếu có cài)
Chạy a7_graph.py cho p4 (trạng thái gốc và --versions data/processed/a4/p4_dev05_bai_bo_ds/a4_p4_dev05_bai_bo_ds_versions.jsonl --date 2027-01-01) trước;
các test "on_disk" đọc file A7 đã ghi. Test ghi file dùng thư mục tạm (đổi a8.OUT_DIR / a7.OUT_DIR).
"""
import contextlib
import io
import json
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))  # -I không tự thêm thư mục script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "utils" / "a8"))
import a4_versions as a4
import a7_graph as a7
import a8_viz as a8

ROOT = Path(__file__).resolve().parent.parent
FULL_FILE = ROOT / "data" / "raw" / "blds2015_p4.md"
DEV05 = ROOT / "data" / "processed" / "a4" / "p4_dev05_bai_bo_ds" / "a4_p4_dev05_bai_bo_ds_versions.jsonl"
P = "BLDS2015."


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


def n(code, type_, text=None, **extra):
    return {"id": P + code, "type": type_, "number": code.rsplit(".", 1)[-1], "heading": None, "text": text,
            "source_line": 1, "status": "ok", **extra}


def e(s, p, o, status="ok", evidence=""):
    return {"s": P + s, "p": p, "o": P + o, "evidence": evidence, "method": None, "status": status, "sources": ["t"]}


def tree_edges(*pairs):
    """contains + part_of cho mỗi cặp (cha, con)."""
    out = []
    for parent, child in pairs:
        out += [e(parent, "contains", child), e(child, "part_of", parent)]
    return out


MINI_NODES = [n("D1", "dieu"), n("D1.K1", "khoan", "a"), n("D1.K1.a", "diem", "b"), n("D2", "dieu", "c")]
MINI_TREE = tree_edges(("D1", "D1.K1"), ("D1.K1", "D1.K1.a"))


def run_quiet(fn, *args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = fn(*args)
        except SystemExit as exit_:
            code = exit_.code
    return code, out.getvalue(), err.getvalue()


def test_build_view_gives_parent_and_keeps_only_semantic_edges():
    view = a8.build_view(MINI_NODES, MINI_TREE + [e("D2", "refers_to", "D1.K1", evidence="khoản 1 Điều 1")])
    parents = {x["id"]: x["parent"] for x in view["nodes"]}
    assert parents == {P + "D1": None, P + "D1.K1": P + "D1", P + "D1.K1.a": P + "D1.K1", P + "D2": None}, parents
    assert [x["id"] for x in view["nodes"]] == [x["id"] for x in MINI_NODES]  # giữ thứ tự file
    assert [(x["s"], x["p"], x["o"]) for x in view["edges"]] == [(P + "D2", "refers_to", P + "D1.K1")]
    assert view["edges"][0]["evidence"] == "khoản 1 Điều 1"


def test_build_view_adds_closed_nodes_for_dangling_and_historical_targets_once():
    edges = MINI_TREE + [e("D2", "refers_to", "D1.K9", status="dangling"), e("D2", "exception_of", "D1.K9", status="dangling"),
                         e("D2", "refers_to", "D7", status="dangling"), e("D2", "repeals", "D1.K1.z", status="historical")]
    view = a8.build_view(MINI_NODES, edges)
    closed = {x["id"]: x for x in view["nodes"] if x["type"] == a8.CLOSED}
    assert set(closed) == {P + "D1.K9", P + "D7", P + "D1.K1.z"}, set(closed)  # D1.K9 hai cạnh mà chỉ một nút
    assert closed[P + "D1.K9"]["parent"] == P + "D1"
    assert closed[P + "D1.K1.z"]["parent"] == P + "D1.K1"
    assert closed[P + "D7"]["parent"] is None  # Điều: mã hai đoạn, không suy được Chương
    assert all(c["status"] == "closed" for c in closed.values())
    assert [x["id"] for x in view["nodes"][:len(MINI_NODES)]] == [x["id"] for x in MINI_NODES]  # nút thật đứng trước


def test_ghost_parent_needs_three_parts_and_a_node_that_exists():
    ids = {P + "D1", P + "D1.K1"}
    assert a8.ghost_parent(P + "D1.K2", ids) == P + "D1"
    assert a8.ghost_parent(P + "D1.K1.a", ids) == P + "D1.K1"
    assert a8.ghost_parent(P + "D1", ids) is None
    assert a8.ghost_parent(P + "D5.K2", ids) is None  # cha cũng đã đóng


def test_build_view_rejects_what_the_spec_does_not_cover():
    cases = {
        "p lạ": MINI_TREE + [e("D2", "cites", "D1")],
        "đầu cạnh không phải nút mà cạnh ok": MINI_TREE + [e("D2", "refers_to", "D9")],
        "hai part_of": MINI_TREE + [e("D1.K1", "part_of", "D2")],
    }
    for label, edges in cases.items():
        try:
            a8.build_view(MINI_NODES, edges)
        except ValueError:
            continue
        raise AssertionError(f"{label}: phải ValueError")


def test_python_and_template_agree_on_the_predicates():
    template = a8.TEMPLATE.read_text(encoding="utf-8")
    block = template.split("const SEM = {", 1)[1].split("};", 1)[0]
    in_template = set(re.findall(r"^\s*(\w+):\s*\{ group:", block, flags=re.M))
    assert in_template == set(a8.SEMANTIC_P), (in_template, a8.SEMANTIC_P)
    short = set(re.findall(r"(\w+):\s*'", template.split("const SHORT = {", 1)[1].split("};", 1)[0]))
    assert short == set(a8.SEMANTIC_P), short


def test_render_html_embeds_data_that_cannot_close_the_script_tag():
    nodes = [n("D1", "dieu", "ghi chú </script><script>alert(1)</script> <!-- x")]
    view = a8.build_view(nodes, [])
    template = "<title>__TITLE__</title><script id=data>__DATA__</script><script>__CYTOSCAPE__</script>"
    page = a8.render_html(view, "A & <B>", {"stem": "s"}, template, "var lib=1;")
    assert page.count("</script>") == 2, page  # chỉ hai thẻ đóng của khung
    assert "<title>A &amp; &lt;B></title>" in page
    data = re.search(r"<script id=data>(.*?)</script>", page, flags=re.S).group(1)
    decoded = json.loads(data)
    assert decoded["nodes"][0]["text"] == nodes[0]["text"]
    assert decoded["meta"] == {"stem": "s"}


def test_render_html_needs_each_placeholder_exactly_once():
    view = {"nodes": [], "edges": []}
    for template in ("__DATA__ __CYTOSCAPE__", "__TITLE__ __DATA__ __DATA__ __CYTOSCAPE__"):
        try:
            a8.render_html(view, "t", {}, template, "")
        except ValueError:
            continue
        raise AssertionError(f"khung {template!r} phải ValueError")


def test_script_safe_rejects_closing_tag_in_any_case():
    for bad in ("x</script>", "x</SCRIPT >", "a<!--b"):
        try:
            a8.script_safe(bad)
        except ValueError:
            continue
        raise AssertionError(f"{bad!r} phải ValueError")
    assert a8.script_safe("a < b && c") == "a < b && c"


def test_vendored_library_is_embeddable():
    text = a8.CYTOSCAPE.read_text(encoding="utf-8")
    a8.script_safe(text)
    assert "Cytoscape Consortium" in text[:400] and "MIT" in text[:1500] or "Permission is hereby granted" in text[:1500]


def test_files_on_disk_base_p4():
    view = a8.build_view(a4.read_jsonl(a7.nodes_path("blds2015_p4")), a4.read_jsonl(a7.edges_path("blds2015_p4")))
    assert len(view["nodes"]) == 225 and len(view["edges"]) == 43, (len(view["nodes"]), len(view["edges"]))
    assert collections_count(view["edges"], "p") == {"refers_to": 25, "exception_of": 14, "same_text_as": 4}
    ids = {x["id"] for x in view["nodes"]}
    assert all(x["parent"] in ids for x in view["nodes"] if x["parent"])
    assert all(x["s"] in ids and x["o"] in ids for x in view["edges"])
    assert not [x for x in view["nodes"] if x["type"] == a8.CLOSED]
    roots = [x["id"] for x in view["nodes"] if x["parent"] is None and x["type"] != "dieu_kien"]
    assert roots == [P[:-1]], roots  # một gốc duy nhất: văn bản


def test_files_on_disk_dev05_closed_units_become_nodes():
    tag = a7.tag_of(DEV05, "2027-01-01")
    view = a8.build_view(a4.read_jsonl(a7.nodes_path("blds2015_p4", tag)), a4.read_jsonl(a7.edges_path("blds2015_p4", tag)))
    closed = {x["id"]: x["parent"] for x in view["nodes"] if x["type"] == a8.CLOSED}
    assert closed == {P + "D621.K2": P + "D621", P + "D650.K1.a": P + "D650.K1", P + "D626": None, P + "D651": None}, closed
    amend = [x for x in view["edges"] if x["p"] in a7.AMEND_P]
    assert len(amend) == 4 and {x["status"] for x in amend} == {"historical"}
    assert [x["status"] for x in view["edges"] if x["status"] == "dangling"] == ["dangling"]


def collections_count(rows, key):
    out = {}
    for r in rows:
        out[r[key]] = out.get(r[key], 0) + 1
    return out


def test_cli_writes_a_single_self_contained_file():
    with tempfile.TemporaryDirectory() as tmp, patched(a8, OUT_DIR=Path(tmp)):
        code, out, _ = run_quiet(a8.main, [str(FULL_FILE)])
        assert code == 0, out
        page = (Path(tmp) / "a8_blds2015_p4.html").read_text(encoding="utf-8")
        assert "cytoscape" in page and "<script src" not in page and "<link" not in page  # không gọi tài nguyên ngoài
        data = json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', page, flags=re.S).group(1))
        assert len(data["nodes"]) == 225 and len(data["edges"]) == 43 and data["meta"]["stem"] == "blds2015_p4"
        assert [p.name for p in Path(tmp).iterdir()] == ["a8_blds2015_p4.html"]


def test_cli_at_date_names_the_file_with_the_tag():
    with tempfile.TemporaryDirectory() as tmp, patched(a8, OUT_DIR=Path(tmp)):
        code, out, _ = run_quiet(a8.main, [str(FULL_FILE), "--versions", str(DEV05), "--date", "2027-01-01"])
        assert code == 0, out
        assert "(4 đã đóng)" in out, out
        assert [p.name for p in Path(tmp).iterdir()] == ["a8_blds2015_p4_p4_dev05_bai_bo_ds_2027-01-01.html"]


def test_cli_without_a7_files_says_which_command_to_run_first():
    with tempfile.TemporaryDirectory() as tmp, patched(a7, OUT_DIR=Path(tmp)), patched(a8, OUT_DIR=Path(tmp)):
        code, _, _ = run_quiet(a8.main, [str(FULL_FILE)])
        assert isinstance(code, str) and "a7_graph.py" in code and "a7_blds2015_p4_nodes.jsonl" in code, code
        assert not list(Path(tmp).iterdir())


def test_versions_and_date_must_come_together_and_date_must_be_iso():
    with tempfile.TemporaryDirectory() as tmp, patched(a8, OUT_DIR=Path(tmp)):
        _, _, err = run_quiet(a8.main, [str(FULL_FILE), "--versions", str(DEV05)])
        assert "phải đi cùng nhau" in err, err
        code, _, _ = run_quiet(a8.main, [str(FULL_FILE), "--versions", str(DEV05), "--date", "01/01/2027"])
        assert isinstance(code, str) and "YYYY-MM-DD" in code, code
        assert not list(Path(tmp).iterdir())


def main():
    failed = 0
    for fn_name, fn in list(globals().items()):
        if fn_name.startswith("test_") and callable(fn):
            try:
                fn()
                print("OK  ", fn_name)
            except AssertionError as e_:
                failed += 1
                print("FAIL", fn_name, "->", e_)
            except Exception as e_:
                failed += 1
                print("FAIL", fn_name, "->", type(e_).__name__, e_)
    print("tổng test lỗi:", failed)
    return failed


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(1 if main() else 0)
