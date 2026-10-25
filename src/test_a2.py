"""A2a: kiểm tra cạnh cấu trúc contains / part_of trên file mẫu rồi file đầy đủ.

Chạy: python -I src/test_a2.py   (các hàm test_* cũng chạy được bằng pytest nếu có cài)
Chạy a2_edges.py cho cả hai file trước (python -I src/a2_edges.py <file md>), test_edges_on_disk đọc file đã ghi.
"""
import ast
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

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_FILE = ROOT / "data" / "sample" / "blds2015_5dieu.md"
FULL_FILE = ROOT / "data" / "raw" / "blds2015_p4.md"
FILES = [("mẫu", SAMPLE_FILE), ("đầy đủ", FULL_FILE)]  # luôn mẫu trước

# Số cạnh mỗi loại (contains, part_of đều bằng nhau): Khoản + Điểm, không tính Điều.
REFERENCE = {SAMPLE_FILE: 30, FULL_FILE: 161}
REFERENCE_TOTAL = {SAMPLE_FILE: 60, FULL_FILE: 322}

# Bước 2. Tổng số từ khoá điều/khoản/điểm (101 và 11) đã đếm bằng tìm chuỗi con trên text, không qua find_refs.
# Số cụm và bảng hình dạng khoá kết quả đã xem trực tiếp: từng cụm đối chiếu với ngữ cảnh 40 ký tự mỗi bên.
KEYWORD_TOTAL = {SAMPLE_FILE: 11, FULL_FILE: 101}
REFS_REFERENCE = {SAMPLE_FILE: 4, FULL_FILE: 21}
SHAPES_FULL = {
    "khoản N Điều N của Bộ luật này": 4,
    "khoản N Điều này": 4,
    "Điều N của Bộ luật này": 4,
    "Điều N và Điều N của Bộ luật này": 3,
    "khoản N và khoản N Điều N của Bộ luật này": 2,
    "khoản N và khoản N Điều này": 1,
    "Điều N": 1,
    "điểm X khoản N Điều N của Bộ luật này": 1,
    "điểm X khoản này": 1,
}
LEVEL = {"điều": 0, "khoản": 1, "điểm": 2}  # cấp của từ khoá: Điều > khoản > điểm


def build(path):
    units = a2.load_units(a2.triples_path(path))
    return units, a2.build_edges(units)


def md_counts(path):
    """Đếm độc lập: số dòng Khoản và Điểm của file md gốc, không qua a1, không qua a2, không qua triples."""
    khoan = diem = 0
    with open(path, encoding="utf-8", newline="") as f:
        for line in f.read().split("\n"):
            if re.match(r"\*\*\d+\\\.\*\*", line):
                khoan += 1
            elif re.match(r"- \*\*\S\)\*\*", line):
                diem += 1
    return khoan, diem


def triples_type_counts(path):
    """Đếm độc lập thứ hai: số dòng "p": "type" theo giá trị o, đọc thẳng file triples, không qua load_units."""
    counts = collections.Counter()
    with open(a2.triples_path(path), encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            if row["p"] == "type":
                counts[row["o"]] += 1
    return counts


def test_parent_of():
    assert a2.parent_of("BLDS2015.D621") is None
    assert a2.parent_of("BLDS2015.D621.K1") == "BLDS2015.D621"
    assert a2.parent_of("BLDS2015.D621.K1.a") == "BLDS2015.D621.K1"
    assert a2.parent_of("BLDS2015.D1.K1.dd") == "BLDS2015.D1.K1"
    for bad in ("", "BLDS2015", "BLDS2015..D1", "BLDS2015.D1.", ".D1"):
        try:
            a2.parent_of(bad)
        except ValueError:
            continue
        raise AssertionError(f"mã {bad!r} phải báo lỗi")


def test_counts_match_reference():
    for name, path in FILES:
        edges = build(path)[1]
        per_pred = collections.Counter(p for _, p, _ in edges)
        want = REFERENCE[path]
        assert per_pred == {"contains": want, "part_of": want}, f"file {name}: {dict(per_pred)}, cần {want} mỗi loại"
        assert len(edges) == REFERENCE_TOTAL[path], f"file {name}: tổng {len(edges)}, cần {REFERENCE_TOTAL[path]}"


def test_counts_match_independent_recount():
    """Số cạnh mỗi loại == số Khoản + số Điểm, đếm bằng hai đường không đi qua a2: dòng của md gốc và type trong triples."""
    for name, path in FILES:
        khoan, diem = md_counts(path)
        types = triples_type_counts(path)
        assert (khoan, diem) == (types["khoan"], types["diem"]), f"file {name}: md {(khoan, diem)}, triples {dict(types)}"
        edges = build(path)[1]
        per_pred = collections.Counter(p for _, p, _ in edges)
        assert per_pred["contains"] == per_pred["part_of"] == khoan + diem, f"file {name}: {dict(per_pred)}"
        assert khoan + diem == REFERENCE[path], f"file {name}: Khoản + Điểm = {khoan + diem}"


def test_check_clean_on_real_data():
    for name, path in FILES:
        units, edges = build(path)
        assert a2.check_edges(units, edges) == [], f"file {name}: {a2.check_edges(units, edges)}"


def test_parent_types_via_type_attribute():
    """Dùng thuộc tính type của A1 (không dùng mã): cha của Khoản là Điều, cha của Điểm là Khoản, Điều không có cha."""
    for name, path in FILES:
        units, edges = build(path)
        parents = collections.defaultdict(list)
        for s, p, o in edges:
            if p == "contains":
                parents[o].append(s)
        for code, u in units.items():
            if u["type"] == "dieu":
                assert code not in parents, f"file {name}: {code} là Điều nhưng có cha"
                continue
            assert len(parents[code]) == 1, f"file {name}: {code} có cha {parents[code]}"
            want = {"khoan": "dieu", "diem": "khoan"}[u["type"]]
            assert units[parents[code][0]]["type"] == want, f"file {name}: {code} ({u['type']}) có cha type {units[parents[code][0]]['type']}"


def test_direct_only_no_transitive():
    """Không có cạnh bắc cầu: không có Điều chứa Điểm; mỗi đơn vị không phải Điều có đúng một cạnh part_of đi ra."""
    for name, path in FILES:
        units, edges = build(path)
        for s, p, o in edges:
            if p == "contains":
                assert not (units[s]["type"] == "dieu" and units[o]["type"] == "diem"), f"file {name}: {s} -> {o} bắc cầu"
        out = collections.Counter(s for s, p, _ in edges if p == "part_of")
        for code, u in units.items():
            assert out[code] == (0 if u["type"] == "dieu" else 1), f"file {name}: {code} có {out[code]} part_of"


def test_edge_order_per_child():
    for name, path in FILES:
        units, edges = build(path)
        children = [c for c, u in units.items() if u["type"] != "dieu"]  # thứ tự trong file triples
        assert len(edges) == 2 * len(children)
        for i, child in enumerate(children):
            contains, part_of = edges[2 * i], edges[2 * i + 1]
            assert contains[1] == "contains" and contains[2] == child, f"file {name}: {contains}"
            assert part_of == (child, "part_of", contains[0]), f"file {name}: {part_of}"


def test_check_catches_corrupted_data():
    """Phép kiểm phải bắt được dữ liệu hỏng: đổi type, thiếu cha, cạnh trùng, mất cạnh part_of, Điều có cha."""
    units, edges = build(SAMPLE_FILE)
    khoan = next(c for c, u in units.items() if u["type"] == "khoan")
    diem = next(c for c, u in units.items() if u["type"] == "diem")

    # 1. cha của Khoản không còn type dieu (mã A1 và type mâu thuẫn nhau)
    bad = {c: dict(u) for c, u in units.items()}
    bad[a2.parent_of(khoan)]["type"] = "khoan"
    assert any(khoan in e and "mong đợi cha type dieu" in e for e in a2.check_edges(bad, edges))

    # 2. Điểm bị gắn nhầm type khoan -> cha phải là Điều nhưng cha thật là Khoản
    bad = {c: dict(u) for c, u in units.items()}
    bad[diem]["type"] = "khoan"
    assert any(diem in e for e in a2.check_edges(bad, edges))

    # 3. cha không có trong tập đơn vị
    bad = {c: u for c, u in units.items() if c != a2.parent_of(khoan)}
    assert any("không có trong tập đơn vị" in e for e in a2.check_edges(bad, edges))

    # 4. cạnh trùng
    assert any("cạnh trùng" in e for e in a2.check_edges(units, edges + [edges[0]]))

    # 5. mất một cạnh part_of -> không đối xứng
    assert any("không đối xứng" in e for e in a2.check_edges(units, [e for e in edges if e != edges[1]]))

    # 6. Điều có cha (type dieu bị gán cho đơn vị có mã 3 đoạn)
    bad = {c: dict(u) for c, u in units.items()}
    bad[khoan]["type"] = "dieu"
    assert any(khoan in e for e in a2.check_edges(bad, edges))


def test_load_units_rejects_incomplete_triples():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "t.jsonl"
        p.write_text('{"s": "X.D1", "p": "type", "o": "dieu"}\n', encoding="utf-8")
        try:
            a2.load_units(p)
        except ValueError:
            return
    raise AssertionError("triples thiếu number/source_line phải báo lỗi")


def test_jsonl_written_correctly():
    for name, path in FILES:
        edges = build(path)[1]
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "e.jsonl"
            a2.write_edges(edges, out)
            raw = out.read_bytes()
        assert not raw.startswith(b"\xef\xbb\xbf"), "có BOM"
        assert b"\\u" not in raw, "còn escape \\u (ensure_ascii phải là False)"
        assert b"\r" not in raw
        rows = [json.loads(line) for line in raw.decode("utf-8").split("\n") if line]
        assert all(list(r) == ["s", "p", "o", "evidence"] for r in rows), f"file {name}: sai khóa"
        assert all(r["evidence"] == "" for r in rows), f"file {name}: evidence phải là chuỗi rỗng"
        assert [(r["s"], r["p"], r["o"]) for r in rows] == edges, f"file {name}: đọc lại không khớp"


def test_edges_on_disk():
    """File a2_edges_<stem>.jsonl đã ghi bằng CLI phải khớp cạnh dựng lại từ triples."""
    for name, path in FILES:
        on_disk = a2.edges_path(path)
        assert on_disk.exists(), f"file {name}: chưa có {on_disk}, chạy a2_edges.py trước"
        rows = [json.loads(line) for line in on_disk.read_text(encoding="utf-8").split("\n") if line]
        assert [(r["s"], r["p"], r["o"]) for r in rows] == build(path)[1], f"file {name}: file trên đĩa khác cạnh dựng lại"
        assert all(r["evidence"] == "" for r in rows)


def test_a2_does_not_import_a1():
    tree = ast.parse(Path(a2.__file__).read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module)
    assert not any(m and m.startswith("a1") for m in imported), f"a2_edges import a1: {imported}"


def keyword_tokens(text):
    """Đếm độc lập với find_refs: tách từ bằng \\w+ rồi đếm từ là điều/khoản/điểm (không phân biệt hoa thường)."""
    return [w for w in re.findall(r"\w+", text) if w.casefold() in LEVEL]


def refs_of(text):
    refs, excluded, total = a2.find_refs({"X.D1": {"type": "dieu", "number": "1", "source_line": 1, "text": text}})
    return refs, excluded, total


def test_refs_noise_is_excluded_and_reported():
    for text in ("Thời điểm mở thừa kế là ngày", "ký hoặc điểm chỉ vào bản di chúc", "có đủ điều kiện sau đây",
                 "người điều trị tại bệnh viện", "một khoản tiền tương ứng", "cùng thời điểm hoặc được coi là"):
        refs, excluded, total = refs_of(text)
        assert refs == [] and len(excluded) == total == 1, f"{text!r}: refs {refs}, excluded {excluded}"


def test_refs_shapes_of_known_phrases():
    cases = {
        "theo điểm a khoản 1 Điều 630 của Bộ luật này.": ("điểm a khoản 1 Điều 630 của Bộ luật này", "điểm X khoản N Điều N của Bộ luật này"),
        "tại khoản 1 và khoản 3 Điều 616 của Bộ luật này có": ("khoản 1 và khoản 3 Điều 616 của Bộ luật này", "khoản N và khoản N Điều N của Bộ luật này"),
        "tại Điều 631 và Điều 632 của Bộ luật này.": ("Điều 631 và Điều 632 của Bộ luật này", "Điều N và Điều N của Bộ luật này"),
        "tại Điều 620 hoặc họ là những người": ("Điều 620", "Điều N"),  # "hoặc họ": họ không phải mục nên chuỗi dừng trước "hoặc"
        "tại khoản 1 và khoản 2 Điều này thì": ("khoản 1 và khoản 2 Điều này", "khoản N và khoản N Điều này"),
        "quy định tại điểm a khoản này.": ("điểm a khoản này", "điểm X khoản này"),
        "tại điểm đ khoản 2 Điều 5": ("điểm đ khoản 2 Điều 5", "điểm X khoản N Điều N"),
        "tại khoản 1, khoản 2 Điều 5": ("khoản 1, khoản 2 Điều 5", "khoản N, khoản N Điều N"),
        "tại Khoản 1 Điều 5": ("Khoản 1 Điều 5", "Khoản N Điều N"),  # giữ nguyên chữ hoa/thường của từ khoá
    }
    for text, (phrase, shape) in cases.items():
        refs = refs_of(text)[0]
        assert [(r.phrase, r.shape) for r in refs] == [(phrase, shape)], f"{text!r}: {refs}"
        assert phrase in refs[0].context


def test_refs_do_not_span_paragraphs():
    refs = refs_of("theo điểm a\nkhoản 1 và")[0]
    assert [r.phrase for r in refs] == ["điểm a", "khoản 1"], refs


def test_refs_context_window():
    text = "x" * 100 + " khoản 1 Điều này " + "y" * 100
    ref = refs_of(text)[0][0]
    assert ref.phrase == "khoản 1 Điều này"
    start = text.index(ref.phrase)
    assert ref.context == text[start - 40:start + len(ref.phrase) + 40]


def test_refs_keywords_reconcile_with_independent_count():
    """Mọi từ khoá hoặc nằm trong một cụm hoặc nằm trong danh sách bị loại: không rơi mất, không đếm hai lần."""
    for name, path in FILES:
        units = a2.load_units(a2.triples_path(path))
        refs, excluded, total = a2.find_refs(units)
        independent = sum(len(keyword_tokens(u["text"])) for u in units.values() if "text" in u)
        assert total == independent == KEYWORD_TOTAL[path], f"file {name}: {total}, {independent}, cần {KEYWORD_TOTAL[path]}"
        in_refs = sum(len(keyword_tokens(r.phrase)) for r in refs)
        assert in_refs + len(excluded) == total, f"file {name}: {in_refs} + {len(excluded)} != {total}"
        for r in refs:
            assert r.phrase in units[r.unit]["text"] and r.phrase in r.context


def test_refs_counts_and_shape_table():
    for name, path in FILES:
        refs = a2.find_refs(a2.load_units(a2.triples_path(path)))[0]
        assert len(refs) == REFS_REFERENCE[path], f"file {name}: {len(refs)} cụm, cần {REFS_REFERENCE[path]}"
        table = {shape: n for shape, n, _ in a2.shape_table(refs)}
        if path == FULL_FILE:
            assert table == SHAPES_FULL, f"file {name}: {table}"
        else:
            assert set(table) <= set(SHAPES_FULL), f"file {name}: hình dạng lạ {set(table) - set(SHAPES_FULL)}"
        assert all(not re.search(r"\d", shape) for shape in table), "hình dạng còn chữ số"


def test_shapes_follow_dieu_khoan_diem_order():
    """Tiêu chí bác bỏ: mọi hình dạng phải biểu diễn được bằng thứ tự điểm > khoản > Điều (cấp không tăng dọc cụm)."""
    for name, path in FILES:
        refs = a2.find_refs(a2.load_units(a2.triples_path(path)))[0]
        for shape in {r.shape for r in refs}:
            levels = [LEVEL[w.casefold()] for w in keyword_tokens(shape)]
            assert levels == sorted(levels, reverse=True), f"file {name}: {shape!r} có cấp {levels}"


def test_refs_flag_writes_nothing():
    on_disk = {p: p.read_bytes() for p in (a2.edges_path(SAMPLE_FILE), a2.edges_path(FULL_FILE))}
    real_write = a2.write_edges
    a2.write_edges = lambda *a, **k: (_ for _ in ()).throw(AssertionError("--refs không được ghi file"))
    try:
        for _, path in FILES:
            with contextlib.redirect_stdout(io.StringIO()) as out:
                a2.main([str(path), "--refs"])
            assert "hình dạng" in out.getvalue()
    finally:
        a2.write_edges = real_write
    assert {p: p.read_bytes() for p in on_disk} == on_disk


# ---- A2b: refers_to ----

def mini_units(spec):
    """Đơn vị nhỏ dựng tay cho test hàm nhóm đích: {mã: (type, text hoặc None)}. Giữ thứ tự khai báo."""
    return {code: {"type": t, "number": "x", "source_line": 1, **({"text": text} if text else {})}
            for code, (t, text) in spec.items()}


# Bốn ca đơn vị lấy từ file thật (văn bản rút gọn quanh cụm). D620 cố ý không có: file mẫu cũng không có Điều 620.
FOUR_CASES = mini_units({
    "BLDS2015.D616": ("dieu", None),
    "BLDS2015.D616.K1": ("khoan", None),
    "BLDS2015.D616.K2": ("khoan", None),
    "BLDS2015.D616.K3": ("khoan", None),
    "BLDS2015.D617": ("dieu", None),
    "BLDS2015.D617.K1": ("khoan", "Người quản lý di sản quy định tại khoản 1 và khoản 3 Điều 616 của Bộ luật này có nghĩa vụ sau đây:"),
    "BLDS2015.D621": ("dieu", None),
    "BLDS2015.D621.K1": ("khoan", None),
    "BLDS2015.D623": ("dieu", None),
    "BLDS2015.D623.K1": ("khoan", None),
    "BLDS2015.D623.K1.a": ("diem", None),
    "BLDS2015.D623.K1.b": ("diem", "Nếu không có người chiếm hữu quy định tại điểm a khoản này."),
    "BLDS2015.D625": ("dieu", None),
    "BLDS2015.D625.K1": ("khoan", "Người thành niên có đủ điều kiện theo quy định tại điểm a khoản 1 Điều 630 của Bộ luật này có quyền lập di chúc"),
    "BLDS2015.D630": ("dieu", None),
    "BLDS2015.D630.K1": ("khoan", None),
    "BLDS2015.D630.K1.a": ("diem", None),
    "BLDS2015.D644": ("dieu", None),
    "BLDS2015.D644.K1": ("khoan", None),
    "BLDS2015.D644.K2": ("khoan", "Quy định tại khoản 1 Điều này không áp dụng đối với người từ chối nhận di sản theo quy định tại "
                                  "Điều 620 hoặc họ là những người không có quyền hưởng di sản theo quy định tại khoản 1 Điều 621 của Bộ luật này."),
})
P = "BLDS2015."


def targets_in(units, source):
    """Đích của từng cụm trong text của source, theo thứ tự cụm: [(cụm, [đích])]."""
    refs = a2.find_refs({source: units[source]})[0]
    return [(r.phrase, a2.group_targets(source, r.phrase, units)) for r in refs]


def test_group_targets_four_unit_cases():
    # 617.K1: Khoản dùng chung Điều cuối -> 2 đích
    assert targets_in(FOUR_CASES, P + "D617.K1") == [
        ("khoản 1 và khoản 3 Điều 616 của Bộ luật này", [P + "D616.K1", P + "D616.K3"])]
    # 623.K1.b: 'khoản này' là Khoản chứa điểm, điểm a của Khoản đó
    assert targets_in(FOUR_CASES, P + "D623.K1.b") == [("điểm a khoản này", [P + "D623.K1.a"])]
    # 625.K1: cụm ba cấp ra một đích sâu nhất, ở Điều khác với Điều nguồn
    assert targets_in(FOUR_CASES, P + "D625.K1") == [
        ("điểm a khoản 1 Điều 630 của Bộ luật này", [P + "D630.K1.a"])]
    # 644.K2: ba cụm trong một đơn vị; 'Điều này' là D644, 'Điều 620' chưa có trong tập (xử lý ở build_refs)
    assert targets_in(FOUR_CASES, P + "D644.K2") == [
        ("khoản 1 Điều này", [P + "D644.K1"]),
        ("Điều 620", [P + "D620"]),
        ("khoản 1 Điều 621 của Bộ luật này", [P + "D621.K1"]),
    ]


def test_build_refs_four_unit_cases():
    edges, unresolved = a2.build_refs(FOUR_CASES)
    assert edges == [
        (P + "D617.K1", "refers_to", P + "D616.K1", "khoản 1 và khoản 3 Điều 616 của Bộ luật này"),
        (P + "D617.K1", "refers_to", P + "D616.K3", "khoản 1 và khoản 3 Điều 616 của Bộ luật này"),
        (P + "D623.K1.b", "refers_to", P + "D623.K1.a", "điểm a khoản này"),
        (P + "D625.K1", "refers_to", P + "D630.K1.a", "điểm a khoản 1 Điều 630 của Bộ luật này"),
        (P + "D644.K2", "refers_to", P + "D644.K1", "khoản 1 Điều này"),
        (P + "D644.K2", "refers_to", P + "D621.K1", "khoản 1 Điều 621 của Bộ luật này"),
    ]
    assert unresolved == [(P + "D644.K2", "Điều 620", P + "D620")]
    assert a2.check_refs(FOUR_CASES, edges, unresolved) == []


def test_group_targets_multiple_items_and_diem_dd():
    units = mini_units({"X.D5": ("dieu", None), "X.D6": ("dieu", None), "X.D7": ("dieu", None),
                        "X.D7.K1": ("khoan", None), "X.D7.K1.a": ("diem", None)})
    assert a2.group_targets("X.D7.K1.a", "Điều 5 và Điều 6", units) == ["X.D5", "X.D6"]
    assert a2.group_targets("X.D7.K1.a", "điểm a và điểm đ khoản 1 Điều 7", units) == ["X.D7.K1.a", "X.D7.K1.dd"]
    assert a2.group_targets("X.D7.K1.a", "điểm đ khoản này", units) == ["X.D7.K1.dd"]


def test_this_resolves_to_enclosing_unit_of_right_type():
    """'Điều này' và 'khoản này' lấy tổ tiên đúng loại, kể cả khi cách nhiều cấp; không lấy cha trực tiếp, không lấy chính nó."""
    units = mini_units({"X.D5": ("dieu", None), "X.D5.K1": ("khoan", None), "X.D5.K2": ("khoan", None),
                        "X.D5.K2.a": ("diem", None), "X.D5.K2.b": ("diem", None), "X.D6": ("dieu", None)})
    # nguồn là Điểm: 'Điều này' cách hai cấp, cha trực tiếp là Khoản K2 nên lấy cha sẽ ra X.D5.K2.K1 hoặc sai Điều
    assert a2.group_targets("X.D5.K2.a", "khoản 1 Điều này", units) == ["X.D5.K1"]
    assert a2.group_targets("X.D5.K2.a", "điểm b khoản này", units) == ["X.D5.K2.b"]
    assert a2.group_targets("X.D5.K2", "khoản 1 Điều này", units) == ["X.D5.K1"]
    # nguồn nằm ở Điều khác thì 'Điều này' đi theo nguồn, không đi theo Điều đầu tiên trong tập
    units["X.D6.K1"] = mini_units({"c": ("khoan", None)})["c"]
    assert a2.group_targets("X.D6.K1", "khoản 2 Điều này", units) == ["X.D6.K2"]
    # không có tổ tiên đúng loại thì báo lỗi, không đoán
    for source, phrase in (("X.D5", "khoản 1 Điều này"), ("X.D5.K1", "điểm a khoản này")):
        try:
            a2.group_targets(source, phrase, units)
        except ValueError:
            continue
        raise AssertionError(f"{source}: {phrase!r} phải báo lỗi vì không có tổ tiên đúng loại")


def test_group_targets_rejects_unconfirmed_shapes():
    units = mini_units({"X.D5": ("dieu", None), "X.D5.K1": ("khoan", "x")})
    for phrase in ("khoản 1",                              # không có Điều
                   "điểm a",                               # không có khoản, Điều
                   "điểm a Điều 5",                        # nhảy cấp
                   "Điều 5 khoản 1",                       # cấp tăng
                   "khoản 1 và khoản 2 Điều 5 và Điều 6",  # mục cấp trên có nhiều mục
                   "Điều này và Điều 5",                   # 'này' không đứng cuối
                   "Điều 5 và Điều này",                   # 'này' không đứng riêng
                   "điểm này",                             # chưa có quy tắc
                   "khoản 1 Điều 5 khoản 2 Điều 6"):       # hai nhóm trong một cụm
        try:
            a2.group_targets("X.D5.K1", phrase, units)
        except ValueError:
            continue
        raise AssertionError(f"{phrase!r} phải báo lỗi")


def test_check_refs_catches_corrupted_data():
    units = mini_units({"X.D1": ("dieu", "theo Điều 2"), "X.D2": ("dieu", None)})
    good = [("X.D1", "refers_to", "X.D2", "Điều 2")]
    assert a2.check_refs(units, good, []) == []
    assert any("chính nó" in e for e in a2.check_refs(units, [("X.D1", "refers_to", "X.D1", "Điều 2")], []))
    assert any("cạnh trùng" in e for e in a2.check_refs(units, good + good, []))
    assert any("không có trong tập" in e for e in a2.check_refs(units, [("X.D1", "refers_to", "X.D9", "Điều 2")], []))
    assert any("evidence" in e for e in a2.check_refs(units, [("X.D1", "refers_to", "X.D2", "Điều 3")], []))
    assert any("evidence" in e for e in a2.check_refs(units, [("X.D1", "refers_to", "X.D2", "")], []))
    assert any("'refers_to'" in e for e in a2.check_refs(units, [("X.D1", "part_of", "X.D2", "Điều 2")], []))
    assert any("unresolved" in e for e in a2.check_refs(units, [], [("X.D1", "Điều 2", "X.D2")]))


# Số (cạnh, unresolved) đếm lại tay từ danh sách --refs: mỗi cụm ra bao nhiêu đích rồi trừ đích không có trong tập đơn vị.
REFERS_REFERENCE = {SAMPLE_FILE: (3, 1), FULL_FILE: (25, 2)}
# Danh sách (nguồn, đích) đã đọc hết bằng mắt, đối chiếu từng cụm với ngữ cảnh trong --refs. Mã viết tắt, thiếu tiền tố BLDS2015.
REFERS_SAMPLE = [("D621.K2", "D621.K1"), ("D644.K2", "D644.K1"), ("D644.K2", "D621.K1")]
UNRESOLVED_SAMPLE = [("D644.K2", "D620")]
REFERS_FULL = [
    ("D616.K3", "D616.K1"), ("D616.K3", "D616.K2"),
    ("D617.K1", "D616.K1"), ("D617.K1", "D616.K3"), ("D617.K2", "D616.K2"),
    ("D618.K1", "D616.K1"), ("D618.K1", "D616.K3"), ("D618.K2", "D616.K2"),
    ("D619", "D652"), ("D621.K2", "D621.K1"),
    ("D623.K1.b", "D623.K1.a"), ("D625.K1", "D630.K1.a"),
    ("D630.K4", "D630.K1"), ("D631.K2", "D631.K1"),
    ("D633", "D631"), ("D634", "D631"), ("D634", "D632"), ("D639.K2", "D636"),
    ("D644.K2", "D644.K1"), ("D644.K2", "D620"), ("D644.K2", "D621.K1"),
    ("D653", "D651"), ("D653", "D652"), ("D654", "D652"), ("D654", "D653"),
]
UNRESOLVED_FULL = [("D611.K1", "D71.K2"), ("D623.K1.a", "D236")]


def refers_expected(path):
    pairs, unresolved = (REFERS_SAMPLE, UNRESOLVED_SAMPLE) if path == SAMPLE_FILE else (REFERS_FULL, UNRESOLVED_FULL)
    return [(P + s, P + o) for s, o in pairs], [(P + s, P + o) for s, o in unresolved]


def test_refers_to_counts_and_reviewed_list():
    for name, path in FILES:
        units = a2.load_units(a2.triples_path(path))
        edges, unresolved = a2.build_refs(units)
        assert (len(edges), len(unresolved)) == REFERS_REFERENCE[path], f"file {name}: {len(edges)}, {len(unresolved)}"
        want_edges, want_unresolved = refers_expected(path)
        assert [(s, o) for s, _, o, _ in edges] == want_edges, f"file {name}: cạnh khác danh sách đã duyệt"
        assert [(s, t) for s, _, t in unresolved] == want_unresolved, f"file {name}: unresolved khác danh sách đã duyệt"
        assert a2.check_refs(units, edges, unresolved) == [], f"file {name}"
        assert all(s != o for s, _, o, _ in edges), f"file {name}: có cạnh s == o"


def test_refers_to_independent_recount():
    """Số đích của mỗi cụm đếm bằng cách khác: số mục có cùng từ khoá với mục đầu của cụm (mục cấp thấp nhất). Không qua group_targets."""
    for name, path in FILES:
        units = a2.load_units(a2.triples_path(path))
        refs = a2.find_refs(units)[0]
        total = 0
        for r in refs:
            words = re.findall(r"(?<!\w)(điều|khoản|điểm)[ ]+(?:\d+|này|[^\W\d_])(?!\w)", r.phrase, re.I)
            total += sum(1 for w in words if w.casefold() == words[0].casefold())
        edges, unresolved = a2.build_refs(units)
        assert len(edges) + len(unresolved) == total, f"file {name}: {len(edges)} + {len(unresolved)} != {total}"
        assert len(edges) + len(unresolved) == sum(REFERS_REFERENCE[path]), f"file {name}"


def test_refers_to_evidence_is_phrase_from_source_text():
    for name, path in FILES:
        units = a2.load_units(a2.triples_path(path))
        refs = {(r.unit, r.phrase) for r in a2.find_refs(units)[0]}
        for s, p, o, evidence in a2.build_refs(units)[0]:
            assert p == "refers_to" and (s, evidence) in refs and evidence in units[s]["text"], f"file {name}: {s} -> {o}"


def test_refers_files_on_disk():
    """Chạy a2_edges.py <md> --refers-to trước. File a2_refs và a2_unresolved phải khớp build_refs; file A2a không lẫn refers_to."""
    for name, path in FILES:
        units = a2.load_units(a2.triples_path(path))
        edges, unresolved = a2.build_refs(units)
        on_disk = a2.refs_path(path)
        assert on_disk.exists(), f"file {name}: chưa có {on_disk}, chạy a2_edges.py --refers-to trước"
        rows = [json.loads(line) for line in on_disk.read_text(encoding="utf-8").split("\n") if line]
        assert all(list(r) == ["s", "p", "o", "evidence"] for r in rows), f"file {name}: sai khoá"
        assert [(r["s"], r["p"], r["o"], r["evidence"]) for r in rows] == edges, f"file {name}: file refs khác dựng lại"
        lines = a2.unresolved_path(path).read_text(encoding="utf-8").split("\n")
        assert lines[-1] == "" and [tuple(x.split("\t")) for x in lines[:-1]] == unresolved, f"file {name}: unresolved"
        structural = [json.loads(line)["p"] for line in a2.edges_path(path).read_text(encoding="utf-8").split("\n") if line]
        assert set(structural) == {"contains", "part_of"}, f"file {name}: file A2a có predicate lạ {set(structural)}"


def test_missing_target_in_loaded_dieu_is_error_not_unresolved():
    """Unresolved chỉ nghĩa là Điều đích chưa được nạp. Điều có trong tập mà Khoản/Điểm không có thì báo lỗi."""
    base = {"BLDS2015.D616": ("dieu", None), "BLDS2015.D616.K1": ("khoan", None), "BLDS2015.D616.K2": ("khoan", None),
            "BLDS2015.D616.K3": ("khoan", None), "BLDS2015.D617": ("dieu", None)}
    for phrase in ("khoản 9 Điều 616 của Bộ luật này", "điểm a khoản 1 Điều 616 của Bộ luật này"):
        units = mini_units({**base, "BLDS2015.D617.K1": ("khoan", f"theo quy định tại {phrase} thì")})
        try:
            a2.build_refs(units)
        except ValueError as e:
            assert "BLDS2015.D616" in str(e) and phrase in str(e), e
            continue
        raise AssertionError(f"{phrase!r}: Điều 616 có trong tập, đích thiếu phải báo lỗi chứ không vào unresolved")
    # đối chứng: Điều 71 không có trong tập thì đúng là unresolved, không phải lỗi
    units = mini_units({**base, "BLDS2015.D617.K1": ("khoan", "theo khoản 2 Điều 71 của Bộ luật này thì")})
    edges, unresolved = a2.build_refs(units)
    assert edges == [] and unresolved == [("BLDS2015.D617.K1", "khoản 2 Điều 71 của Bộ luật này", "BLDS2015.D71.K2")]
    assert a2.check_refs(units, edges, unresolved) == []
    # check_refs cũng bắt unresolved có Điều đã nạp (đường kiểm thứ hai, độc lập với build_refs)
    assert any("D616" in e for e in a2.check_refs(units, [], [("BLDS2015.D617.K1", "khoản 9 Điều 616", "BLDS2015.D616.K9")]))


TAIL_BASE = {"BLDS2015.D5": ("dieu", None), "BLDS2015.D6": ("dieu", None), "BLDS2015.D7": ("dieu", None),
             "BLDS2015.D8": ("dieu", None), "BLDS2015.D9": ("dieu", None)}


def test_external_refs_are_unresolved_not_edges():
    """Review F-01: cụm theo sau bởi tên văn bản khác không thành cạnh tới Điều cùng số của Bộ luật."""
    cases = [("theo quy định tại Điều 5 của Luật Đất đai.", "Điều 5", "Luật Đất đai"),
             ("theo khoản 2 Điều 5 Nghị định số 01/2021/NĐ-CP và Điều 6 của Bộ luật này", "khoản 2 Điều 5", "Nghị định số 01/2021/NĐ-CP"),
             ("theo Điều 5 của Bộ luật dân sự năm 2005;", "Điều 5", "Bộ luật dân sự năm 2005")]
    for text, phrase, doc in cases:
        units = mini_units({**TAIL_BASE, "BLDS2015.D9.K1": ("khoan", text)})
        edges, unresolved = a2.build_refs(units)
        assert unresolved == [("BLDS2015.D9.K1", phrase, a2.EXTERNAL + doc)], (text, unresolved)
        assert all(o != "BLDS2015.D5" for _, _, o, _ in edges), (text, edges)
        assert a2.check_refs(units, edges, unresolved) == []
    # "Bộ luật này" không cần "của" vẫn là chính văn bản
    units = mini_units({**TAIL_BASE, "BLDS2015.D9.K1": ("khoan", "theo Điều 5 Bộ luật này")})
    assert a2.build_refs(units) == ([("BLDS2015.D9.K1", "refers_to", "BLDS2015.D5", "Điều 5")], [])


def test_unsupported_tails_and_uncovered_numbers_stop():
    """Review F-01, F-02: dạng trước đây cho cạnh thiếu hoặc sai mà không báo, nay dừng bằng ValueError."""
    for text, why in [("theo Điều 5 của Luật này", "không phải văn bản đang xử lý"),
                      ("theo Điều 5 Nghị định này", "không phải văn bản đang xử lý"),
                      ("theo Điều 5 của hợp đồng", "đuôi 'của …'"),
                      ("từ Điều 5 đến Điều 8", "khoảng"),
                      ("các điều 5, 6 và 7", "danh sách số trần"),
                      ("theo khoản 1, 2 Điều 5", "danh sách số trần"),
                      ("theo khoản 2a Điều 5", "không thuộc cụm nào"),
                      ("theo Điều 5a", "không thuộc cụm nào")]:
        units = mini_units({**TAIL_BASE, "BLDS2015.D9.K1": ("khoan", text)})
        try:
            a2.build_refs(units)
        except ValueError as e:
            assert why in str(e), (text, str(e))
            continue
        raise AssertionError(f"{text!r}: phải báo lỗi")


def test_cli_stops_and_writes_nothing_on_missing_target():
    units = mini_units({"BLDS2015.D616": ("dieu", None), "BLDS2015.D616.K1": ("khoan", None),
                        "BLDS2015.D617": ("dieu", "theo khoản 9 Điều 616 của Bộ luật này")})
    saved = a2.read_units, a2.refs_path, a2.unresolved_path
    with tempfile.TemporaryDirectory() as tmp:
        a2.read_units = lambda src: units
        a2.refs_path = lambda src: Path(tmp) / "refs.jsonl"
        a2.unresolved_path = lambda src: Path(tmp) / "unresolved.txt"
        try:
            try:
                a2.run_refers_to("x")
            except SystemExit as e:
                assert e.code not in (0, None), e.code
            else:
                raise AssertionError("phải thoát khác 0")
        finally:
            a2.read_units, a2.refs_path, a2.unresolved_path = saved
        assert list(Path(tmp).iterdir()) == [], "lỗi mà vẫn ghi file"


# Phép kiểm cho giả định ngầm: mọi cụm trong text đều là của chính Bộ luật (group_targets dùng tiền tố BLDS2015 của nguồn).
# Quét mọi chỗ "Điều/khoản/điểm <gì đó> của" không theo sau bởi "Bộ luật này". File đầy đủ có 3 chỗ, đã đọc từng chỗ:
# đều là "điểm chỉ của người ..." (dấu điểm chỉ, danh từ), không phải dẫn chiếu. Danh sách này phải đúng bằng kết quả quét,
# nên chỗ mới nào xuất hiện cũng làm test FAIL.
FOREIGN_RE = re.compile(r"(?:Điều|khoản|điểm) \S+ của (?!Bộ luật này)")
FOREIGN_CLEARED = {
    SAMPLE_FILE: [],
    FULL_FILE: [("BLDS2015.D630.K5", "điểm chỉ của "), ("BLDS2015.D631.K3", "điểm chỉ của "), ("BLDS2015.D634", "điểm chỉ của ")],
}


def test_no_reference_to_another_law():
    for name, path in FILES:
        units = a2.load_units(a2.triples_path(path))
        hits = [(code, m.group(0)) for code, u in units.items() for m in FOREIGN_RE.finditer(u.get("text", ""))]
        assert hits == FOREIGN_CLEARED[path], f"file {name}: chỗ khớp chưa đọc: {[h for h in hits if h not in FOREIGN_CLEARED[path]]}"
        # chặt hơn: sau mỗi cụm mà find_refs nhận ra không được có "của <luật khác>"
        for r in a2.find_refs(units)[0]:
            tail = re.search(re.escape(r.phrase) + r" của (?!Bộ luật này)", units[r.unit]["text"])
            assert tail is None, f"file {name}: {r.unit}: {r.phrase!r} đi kèm 'của' khác Bộ luật này"


# ---- A3 bước 1: --triggers ----

# Số cụm đếm độc lập với TRIGGER_RE: tách \w+ từng đoạn rồi đếm token "trừ" (mỗi "ngoại trừ" có đúng một token "trừ")
# và chuỗi ba token "không áp dụng". Các số 11 và 1 trùng với lần quét thăm dò bằng regex riêng ngoài code.
TRIGGER_TOTAL = {SAMPLE_FILE: 1, FULL_FILE: 11}
TRIGGER_KINDS = {SAMPLE_FILE: {"không áp dụng": 1}, FULL_FILE: {"trừ": 10, "không áp dụng": 1}}
# Bảng 6 từ đứng sau đã đọc từng dòng, đối chiếu với ngữ cảnh 40 ký tự của --triggers.
TRIGGER_TABLE = {
    SAMPLE_FILE: {"đối với người từ chối nhận": 1},
    FULL_FILE: {
        "trường hợp có thỏa thuận khác": 5,
        "những người sau đây": 1,
        "trường hợp pháp luật có quy": 1,
        "trường hợp thừa kế thế vị": 1,
        "trường hợp toàn bộ di sản": 1,
        "trường hợp việc từ chối nhằm": 1,
        "đối với người từ chối nhận": 1,
    },
}


def trigger_tokens(text):
    count = 0
    for paragraph in text.split("\n"):
        words = [w.casefold() for w in re.findall(r"\w+", paragraph)]
        count += words.count("trừ")
        count += sum(1 for i in range(len(words) - 2) if words[i:i + 3] == ["không", "áp", "dụng"])
    return count


def triggers_of(text):
    return a2.find_triggers({"X.D1": {"type": "dieu", "number": "1", "source_line": 1, "text": text}})


def test_triggers_word_boundary_and_longest_match():
    for text in ("trừng phạt kẻ gian", "trừu tượng", "áp dụng quy định", "không được áp dụng", "không\náp dụng", "không áp  dụngx"):
        assert triggers_of(text) == [], f"{text!r}: {triggers_of(text)}"
    cases = {
        "TRỪ trường hợp": [("TRỪ", "trừ")],                      # không phân biệt hoa thường
        "ngoại trừ trường hợp": [("ngoại trừ", "ngoại trừ")],    # một cụm, không thêm "trừ" bên trong
        "Ngoại  trừ nếu": [("Ngoại  trừ", "ngoại trừ")],         # nhiều dấu cách, kind chuẩn hoá
        "không  áp dụng đối với": [("không  áp dụng", "không áp dụng")],
        "khấu trừ nghĩa vụ": [("trừ", "trừ")],                   # ranh giới là tiếng: "khấu trừ" vẫn khớp, đọc bảng để biết
        "trừ ... không áp dụng": [("trừ", "trừ"), ("không áp dụng", "không áp dụng")],
    }
    for text, want in cases.items():
        assert [(t.phrase, t.kind) for t in triggers_of(text)] == want, f"{text!r}: {triggers_of(text)}"


def test_triggers_words_after():
    cases = {
        "a, trừ trường hợp có thỏa thuận khác.": "trường hợp có thỏa thuận khác",
        "trừ một hai ba bốn năm sáu bảy tám": "một hai ba bốn năm sáu",         # đúng 6 từ
        "trừ những người sau đây:\nđiểm a người": "những người sau đây",        # dừng ở hết đoạn
        "trừ, trường hợp (a) b": "trường hợp a b",                              # bỏ dấu câu
        "Trừ Trường hợp": "Trường hợp",                                         # after giữ chữ hoa/thường
        "kết thúc bằng trừ": "",
    }
    for text, want in cases.items():
        assert [t.after for t in triggers_of(text)] == [want], f"{text!r}: {triggers_of(text)}"
    table = a2.trigger_table(triggers_of("Trừ Trường hợp.\ntrừ trường hợp!"))
    assert [(key, n) for key, n, _ in table] == [("trường hợp", 2)], "khoá bảng phải viết thường"


def test_triggers_context_window():
    text = "x" * 100 + " trừ " + "y" * 100
    t = triggers_of(text)[0]
    start = text.index("trừ")
    assert t.context == text[start - 40:start + len("trừ") + 40]


def test_triggers_count_matches_independent_recount():
    for name, path in FILES:
        units = a2.load_units(a2.triples_path(path))
        triggers = a2.find_triggers(units)
        independent = sum(trigger_tokens(u["text"]) for u in units.values() if "text" in u)
        assert len(triggers) == independent == TRIGGER_TOTAL[path], f"file {name}: {len(triggers)}, {independent}"
        assert dict(collections.Counter(t.kind for t in triggers)) == TRIGGER_KINDS[path], f"file {name}"
        for t in triggers:
            assert t.phrase in units[t.unit]["text"] and t.phrase in t.context, f"file {name}: {t}"


def test_triggers_table_reviewed():
    for name, path in FILES:
        triggers = a2.find_triggers(a2.load_units(a2.triples_path(path)))
        table = a2.trigger_table(triggers)
        assert {key: n for key, n, _ in table} == TRIGGER_TABLE[path], f"file {name}: {table}"
        assert sum(n for _, n, _ in table) == len(triggers)
        assert [n for _, n, _ in table] == sorted((n for _, n, _ in table), reverse=True)


def test_triggers_flag_writes_nothing():
    outputs = [f(p) for p in (SAMPLE_FILE, FULL_FILE) for f in (a2.edges_path, a2.refs_path, a2.unresolved_path)]
    before = {p: p.read_bytes() for p in outputs}
    saved = a2.write_edges, a2.write_ref_edges, a2.write_unresolved

    def forbidden(*a, **k):
        raise AssertionError("--triggers không được ghi file")
    a2.write_edges = a2.write_ref_edges = a2.write_unresolved = forbidden
    try:
        for _, path in FILES:
            with contextlib.redirect_stdout(io.StringIO()) as out:
                a2.main([str(path), "--triggers"])
            assert "6 từ đứng sau" in out.getvalue() and "từ khoá:" in out.getvalue()
    finally:
        a2.write_edges, a2.write_ref_edges, a2.write_unresolved = saved
    assert {p: p.read_bytes() for p in outputs} == before


def test_mode_flags_are_mutually_exclusive():
    for flags in (["--refs", "--triggers"], ["--refers-to", "--triggers"], ["--refs", "--refers-to"]):
        with contextlib.redirect_stderr(io.StringIO()):
            try:
                a2.main([str(SAMPLE_FILE)] + flags)
            except SystemExit as e:
                assert e.code == 2, e.code
                continue
        raise AssertionError(f"{flags} dùng cùng lúc phải bị từ chối")


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
