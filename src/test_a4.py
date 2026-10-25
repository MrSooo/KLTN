"""A4: kiểm tra cơ chế cập nhật có phiên bản trên file mẫu 5 Điều và 8 văn bản dev trong data/dev_amend.

Chạy: python -I src/test_a4.py   (các hàm test_* cũng chạy được bằng pytest nếu có cài)
Cần a1_parse, a2_edges, a3_exceptions đã chạy cho data/sample/blds2015_5dieu.md (file cạnh gốc trong data/processed).
Mọi kỳ vọng ở các test (2), (3), (4), (6) được viết tay trong file này, hoặc quét độc lập từ file cạnh gốc / file md gốc,
không suy ra từ hàm của a4_versions. Test ghi file chỉ ghi vào thư mục tạm (a4.OUT_DIR / a4.DOCS_DIR được đổi trong sandbox()).
"""
import contextlib
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import a1_parse as a1
import a2_edges as a2
import a3_exceptions as a3
import a4_versions as a4

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_FILE = ROOT / "data" / "sample" / "blds2015_5dieu.md"
DEV = ROOT / "data" / "dev_amend"
IN_DIR = ROOT / "data" / "processed"
P = "BLDS2015."
STEM = "blds2015_5dieu"
DEV_FILES = {1: "dev01_bai_bo_khoan", 2: "dev02_sua_khoan", 3: "dev03_thay_dieu", 4: "dev04_bo_sung",
             5: "dev05_bai_bo_ds", 6: "dev06_cum_tu", 7: "dev07_doi_ten", 8: "dev08_thay_van_ban"}
DATE = "2027-01-01"


def dev(n):
    return DEV / (DEV_FILES[n] + ".md")


def c(*segs):
    return [P + s for s in segs]


# ---- tiện ích ----

def run_dev(*ns):
    return a4.apply_series(SAMPLE_FILE, [dev(n) for n in ns])


@contextlib.contextmanager
def sandbox():
    """Đổi thư mục ghi của a4 sang thư mục tạm."""
    with tempfile.TemporaryDirectory() as tmp:
        old = a4.OUT_DIR, a4.DOCS_DIR
        a4.OUT_DIR = a4.DOCS_DIR = Path(tmp)
        try:
            yield Path(tmp)
        finally:
            a4.OUT_DIR, a4.DOCS_DIR = old


def cli(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            a4.main([str(a) for a in argv])
            code = 0
        except SystemExit as e:
            code = e.code
    return code, out.getvalue(), err.getvalue()


def amend_text(body, date="01 tháng 01 năm 2027"):
    """Văn bản sửa đổi dựng tay: Điều 1 (tiêu đề), nội dung từ dòng 3, Điều 2 và câu hiệu lực."""
    tail = f"Luật này có hiệu lực thi hành từ ngày {date}." if date else "Luật này có hiệu lực thi hành."
    return ("Điều 1. Sửa đổi, bổ sung một số điều của Bộ luật Dân sự số 91/2015/QH13\n\n" + body
            + "\n\nĐiều 2. Hiệu lực thi hành\n\n" + tail + "\n")


def parse_body(body):
    return a4.parse_amendment(amend_text(body))


def one(body):
    ds = parse_body(body).directives
    assert len(ds) == 1, [d.op for d in ds]
    return ds[0]


def raises(code, fn, *args):
    try:
        fn(*args)
    except a4.A4Error as e:
        assert e.code == code, f"mã lỗi {e.code} ({e.message}), cần {code}"
        return e
    raise AssertionError(f"phải báo lỗi {code}")


def data_files(tmp):
    return sorted(p.name for p in Path(tmp).iterdir() if p.name.startswith("a4_") and not p.name.startswith("a4_report_"))


def apply_cli_error(code, texts, *flags, base=SAMPLE_FILE):
    """Ghi các văn bản vào thư mục tạm, chạy apply: phải thoát 1, chỉ có báo cáo (mã lỗi `code`), không file dữ liệu."""
    with sandbox() as tmp:
        paths = []
        for i, text in enumerate(texts):
            p = tmp / f"amend{i}.md"
            p.write_text(text, encoding="utf-8", newline="\n")
            paths.append(p)
        argv = ["apply", "--base", base] + [x for p in paths for x in ("--amend", p)] + list(flags)
        exit_code, _, err = cli(*argv)
        assert exit_code == 1, f"exit {exit_code}, cần 1 (stderr: {err})"
        assert data_files(tmp) == [], f"có file dữ liệu: {data_files(tmp)}"
        reports = sorted(p.name for p in tmp.iterdir() if p.name.startswith("a4_report_"))
        assert len(reports) == 1, reports
        report = (tmp / reports[0]).read_text(encoding="utf-8")
        assert f"mã lỗi: {code}" in report, report
        return report


# ---- quét độc lập file cạnh gốc ----

def base_edges():
    rows = []
    for name in (f"a2_edges_{STEM}.jsonl", f"a2_refs_{STEM}.jsonl", f"a3_exceptions_{STEM}.jsonl"):
        with open(IN_DIR / name, encoding="utf-8") as f:
            rows += [json.loads(line) for line in f if line.strip()]
    return rows


def base_ids():
    with open(IN_DIR / f"a1_triples_{STEM}.jsonl", encoding="utf-8") as f:
        return [r["s"] for r in map(json.loads, f) if r["p"] == "type"]


def scan_broken(closed):
    """Cạnh refers_to / exception_of có nguồn còn hiệu lực (ngoài closed) và đích thuộc closed."""
    closed = set(closed)
    return sorted((r["s"], r["p"], r["o"]) for r in base_edges()
                  if r["p"] in ("refers_to", "exception_of") and r["o"] in closed and r["s"] not in closed)


def scan_impact(U, closed):
    U, closed, out = set(U), set(closed), {}
    for r in base_edges():
        s, p, o = r["s"], r["p"], r["o"]
        if p == "refers_to" and o in U:
            out.setdefault(s, set()).add(f"refers_to {o}")
        if p == "exception_of" and o in U:
            out.setdefault(s, set()).add(f"exception_of {o}")
        if p == "exception_of" and s in U:
            out.setdefault(o, set()).add(f"exception_of_by {s}")
    return {k: sorted(v) for k, v in out.items() if k not in closed}


def versions_of(run, code):
    return [r for r in run.version_rows() if r["id"] == code]


def same(a, b):
    return set(a) == set(b) and len(a) == len(b)


# ---- (1) parse_reflist và các dạng R1–R6 ----

def test_parse_reflist_forms():
    cases = {
        "khoản 2 Điều 621": c("D621.K2"),
        "khoản 2 Điều 621 và điểm a khoản 1 Điều 650": c("D621.K2", "D650.K1.a"),
        "các điều 626, 644 và 651": c("D626", "D644", "D651"),
        "các điều 626 và 651": c("D626", "D651"),
        "khoản 1, 2 và 3 Điều 5": c("D5.K1", "D5.K2", "D5.K3"),
        "các khoản 1 và 3 Điều 616 của Bộ luật dân sự": c("D616.K1", "D616.K3"),
        "điểm a, b và đ khoản 1 Điều 650": c("D650.K1.a", "D650.K1.b", "D650.K1.dd"),
        "các điểm a và b khoản 2 Điều 7": c("D7.K2.a", "D7.K2.b"),
        "Điều 621a; khoản 2a Điều 626, điểm đ khoản 1 Điều 650": c("D621a", "D626.K2a", "D650.K1.dd"),
        "điểm a khoản 1 Điều 650 của Bộ luật này": c("D650.K1.a"),
        "KHOẢN 2 ĐIỀU 621": c("D621.K2"),                    # không phân biệt hoa thường
        "khoản 2 Điều 621, điểm a khoản 1 Điều 650 và Điều 626": c("D621.K2", "D650.K1.a", "D626"),
    }
    for text, want in cases.items():
        got = [a4.ref_code(r) for r in a4.parse_reflist(text)]
        assert got == want, f"{text!r}: {got}, cần {want}"
    assert a4.parse_reflist("điểm đ khoản 1 Điều 650") == [a4.Ref("650", "1", "đ")]
    assert a4.parse_reflist("Điều 621a") == [a4.Ref("621a")]


def test_parse_reflist_partial_or_malformed_is_error():
    bad = ["", "khoản 2 Điều 621 và", "khoản 2 Điều 621 điểm a khoản 1 Điều 650", "khoản 2 Điều 621 và điểm a",
           "Điều 621, 626", "điểm a Điều 650", "điểm f khoản 1 Điều 650", "khoản 2 Điều 621xyz",
           "các điều 626 và", "khoản 2 Điều 621. Điều 626", "điểm a và điểm đ khoản 1 Điều 7"]
    for text in bad:
        raises("E_REFLIST", a4.parse_reflist, text)


R1_CASES = [  # (dòng chỉ thị, mã đích, relation, số của gốc cây, nội dung)
    ("Khoản 1 Điều 621 được sửa đổi, bổ sung như sau:", "D621.K1", "amends", "1", "“1. Nội dung mới.”"),
    ("khoản 1 Điều 621 được sửa đổi như sau:", "D621.K1", "amends", "1", "“1. Nội dung mới.”"),
    ("Điều 626 được sửa đổi như sau:", "D626", "amends", "626", "“Điều 626. Tên mới”"),
    ("Điều 626 được thay thế như sau:", "D626", "replaces", "626", "“Điều 626. Tên mới”"),
    ("Sửa đổi, bổ sung điểm a khoản 1 Điều 650 như sau:", "D650.K1.a", "amends", "a", "“a) Nội dung mới.”"),
    ("Sửa đổi khoản 1 Điều 621 như sau:", "D621.K1", "amends", "1", "“1. Nội dung mới.”"),
    ("Thay thế khoản 1 Điều 621 của Bộ luật dân sự như sau:", "D621.K1", "replaces", "1", "“1. Nội dung mới.”"),
    ("3. Điểm đ khoản 1 Điều 650 được thay thế như sau:", "D650.K1.dd", "replaces", "đ", "“đ) Nội dung mới.”"),
]


def test_r1_replace_unit_forms():
    for line, code, relation, number, body in R1_CASES:
        d = one(f"{line}\n\n{body}")
        assert (d.op, d.relation, d.targets, d.number) == ("replace_unit", relation, [P + code], number), (line, d)
        assert d.tree.number == number


def test_r1_bo_sung_form_is_unsupported_error():
    for line in ("Điều 621 được bổ sung như sau:", "khoản 3 Điều 621 được bổ sung như sau:"):
        e = raises("E_UNKNOWN_LINE", parse_body, f"{line}\n\n“3. Nội dung.”")
        assert e.line_no == 3 and e.line == line


def test_r2_insert_forms():
    cases = [
        ("Bổ sung Điều 621a vào sau Điều 621 như sau:", "D621a", "621a", "D621", "“Điều 621a. Tên\n\n1. A.”"),
        ("Bổ sung Điều 621a như sau:", "D621a", "621a", None, "“Điều 621a. Tên”"),
        ("Bổ sung khoản 3 Điều 621 như sau:", "D621.K3", "3", None, "“3. A.”"),
        ("Bổ sung khoản 3 vào Điều 621 như sau:", "D621.K3", "3", None, "“3. A.”"),
        ("Bổ sung khoản 3 vào sau khoản 2 Điều 621 như sau:", "D621.K3", "3", "D621.K2", "“3. A.”"),
        ("Bổ sung khoản 2a vào sau khoản 2 Điều 621 của Bộ luật dân sự như sau:", "D621.K2a", "2a", "D621.K2", "“2a. A.”"),
        ("Bổ sung điểm đ vào sau điểm d khoản 1 Điều 650 như sau:", "D650.K1.dd", "đ", "D650.K1.d", "“đ) A.”"),
        ("Bổ sung điểm đ khoản 1 Điều 650 như sau:", "D650.K1.dd", "đ", None, "“đ) A.”"),
        ("2. Bổ sung điểm e vào khoản 1 Điều 650 như sau:", "D650.K1.e", "e", None, "“e) A.”"),
    ]
    for line, code, number, after, body in cases:
        d = one(f"{line}\n\n{body}")
        assert (d.op, d.relation, d.targets, d.number, d.after) == (
            "insert_unit", "amends", [P + code], number, None if after is None else P + after), (line, d)


def test_r3_repeal_forms():
    ds = parse_body("Bãi bỏ khoản 2 Điều 621 và điểm a khoản 1 Điều 650.").directives
    assert [(d.op, d.relation, d.targets, d.seq) for d in ds] == [
        ("repeal_unit", "repeals", c("D621.K2"), 1), ("repeal_unit", "repeals", c("D650.K1.a"), 2)]
    ds = parse_body("Bãi bỏ các điều 626, 644 và 651").directives  # dấu chấm cuối tuỳ chọn
    assert [d.targets for d in ds] == [c("D626"), c("D644"), c("D651")] and {d.relation for d in ds} == {"repeals"}
    raises("E_REFLIST", parse_body, "Bãi bỏ khoản 2 Điều 621 và điểm a.")        # chỉ khớp một phần
    raises("E_REFLIST", parse_body, "Bãi bỏ khoản 2 Điều 621 điểm a khoản 1 Điều 650.")


def test_r4_rename_forms():
    d = one("Tên Điều 621 được sửa đổi như sau:\n\n“Điều 621. Người không được quyền hưởng di sản” được sửa đổi thành "
            "“Điều 621. Những người không được quyền hưởng di sản”.")
    assert (d.op, d.relation, d.targets, d.old, d.new) == (
        "rename_heading", "amends", c("D621"), "Người không được quyền hưởng di sản", "Những người không được quyền hưởng di sản")
    d = one("Tên Điều 626 được sửa đổi như sau:\n\n“Điều 626. Quyền mới”")                 # một chuỗi, có tiền tố
    assert (d.old, d.new) == (None, "Quyền mới")
    d = one("Tên Điều 626 được sửa đổi như sau:\n\n“Quyền mới”")                          # một chuỗi, không tiền tố
    assert (d.old, d.new) == (None, "Quyền mới")
    d = one('Tên Điều 626 được sửa đổi như sau:\n\n"Quyền mới"')                          # nháy thẳng
    assert d.new == "Quyền mới"
    raises("E_BODY", parse_body, "Tên Điều 626 được sửa đổi như sau:\n\n“Điều 621. Quyền mới”")  # tiền tố khác số


def test_r5_phrase_forms():
    cases = [
        ("Sửa đổi cụm từ “A” thành cụm từ “B” tại khoản 1 Điều 621", "replace", "amends", "A", "B"),
        ("Thay thế cụm từ “A” bằng cụm từ “B” tại khoản 1 Điều 621.", "replace", "replaces", "A", "B"),
        ("Bỏ cụm từ “A” tại khoản 1 Điều 621;", "delete", "amends", "A", None),
        ("Bổ sung cụm từ “B” vào sau cụm từ “A” tại khoản 1 Điều 621", "insert", "amends", "A", "B"),
        ('Sửa đổi cụm từ "A" thành cụm từ "B" tại khoản 1 Điều 621', "replace", "amends", "A", "B"),   # nháy thẳng
        ("2. Bỏ cụm từ “A” tại khoản 1 Điều 621", "delete", "amends", "A", None),
    ]
    for line, mode, relation, old, new in cases:
        d = one(line)
        assert (d.op, d.mode, d.relation, d.targets, d.old, d.new) == ("phrase", mode, relation, c("D621.K1"), old, new), line
    d = one("Bỏ cụm từ “A” tại khoản 1 Điều 621 và điểm a khoản 1 Điều 650")
    assert d.targets == c("D621.K1", "D650.K1.a")


def test_r5_scope_line_and_missing_scope():
    ds = parse_body("Sửa đổi, bổ sung một số cụm từ tại khoản 1 Điều 650 như sau:\nThay thế cụm từ “A” bằng cụm từ “B”;\n"
                    "Bỏ cụm từ “C”;\nBổ sung cụm từ “E” vào sau cụm từ “D”.").directives
    assert [(d.mode, d.relation, d.targets, d.old, d.new, d.seq) for d in ds] == [
        ("replace", "replaces", c("D650.K1"), "A", "B", 1), ("delete", "amends", c("D650.K1"), "C", None, 2),
        ("insert", "amends", c("D650.K1"), "D", "E", 3)]
    # phạm vi chấm dứt ở chỉ thị không phải cụm từ kế tiếp
    raises("E_SCOPE", parse_body, "Bổ sung một số cụm từ tại Điều 621 như sau:\nBỏ cụm từ “A”;\nBãi bỏ khoản 2 Điều 626.\nBỏ cụm từ “B”;")
    raises("E_SCOPE", parse_body, "Bỏ cụm từ “A”.")                                  # chưa có phạm vi
    # chỉ thị có "tại" riêng không dùng phạm vi, và không chấm dứt phạm vi
    ds = parse_body("Sửa đổi một số cụm từ tại Điều 621 như sau:\nBỏ cụm từ “A” tại Điều 626;\nBỏ cụm từ “B”.").directives
    assert [d.targets for d in ds] == [c("D626"), c("D621")]


def test_r6_replace_doc_forms():
    for line in ("Luật này thay thế Bộ luật dân sự năm 2015.", "Bộ luật này thay thế toàn bộ Bộ luật Dân sự số 91/2015/QH13.",
                 "Văn bản này thay thế Bộ luật dân sự", "1. Luật này thay thế Bộ luật dân sự."):
        d = one(line)
        assert (d.op, d.relation, d.targets) == ("replace_doc", "replaces", ["BLDS2015"]), line


def test_skipped_lines_are_listed_not_errors():
    parsed = parse_body("Bãi bỏ khoản 2 Điều 621.\n\nSửa đổi, bổ sung một số điều của Bộ luật dân sự:\n\nGhi chú không liên quan.")
    reasons = {line: reason for _, line, reason in parsed.skipped}
    assert reasons["Điều 1. Sửa đổi, bổ sung một số điều của Bộ luật Dân sự số 91/2015/QH13"] == "tiêu đề Điều của văn bản sửa đổi"
    assert reasons["Điều 2. Hiệu lực thi hành"] == "tiêu đề Điều của văn bản sửa đổi"
    assert reasons["Sửa đổi, bổ sung một số điều của Bộ luật dân sự:"] == "tiêu đề chung"
    assert reasons["Ghi chú không liên quan."] == "không phải chỉ thị"
    assert len(parsed.directives) == 1


# Dạng bị động / "hết hiệu lực" / "thay bằng": trước đây bị bỏ qua êm (review F-03), nay là dòng lạ.
LOOKS_LIKE_DIRECTIVE = [
    "Khoản 2 Điều 621 được bãi bỏ.",
    "Điều 621 bị bãi bỏ.",
    "Khoản 2 Điều 621 hết hiệu lực kể từ ngày 01 tháng 01 năm 2027.",
    "Các Điều 621 và 626 hết hiệu lực.",
    "Sửa cụm từ “người thừa kế” thành “người hưởng thừa kế” tại Điều 621.",
    "Cụm từ “người thừa kế” tại Điều 621 được thay bằng cụm từ “người hưởng thừa kế”.",
    "Bộ luật Dân sự số 91/2015/QH13 hết hiệu lực kể từ ngày Luật này có hiệu lực.",
]


def test_lines_that_look_like_directives_are_unknown_not_skipped():
    for line in LOOKS_LIKE_DIRECTIVE:
        e = raises("E_UNKNOWN_LINE", parse_body, f"Bãi bỏ khoản 2 Điều 650.\n\n{line}")
        assert e.line_no == 5 and e.line == line, (line, e.line_no, e.line)


def test_line_with_reference_but_no_action_word_is_still_skipped():
    line = "Hợp đồng giao kết theo khoản 1 Điều 621 trước ngày Luật này có hiệu lực thì tiếp tục được thực hiện."
    parsed = parse_body(f"Bãi bỏ khoản 2 Điều 621.\n\n{line}")
    assert {l: r for _, l, r in parsed.skipped}[line] == "không phải chỉ thị"
    assert len(parsed.directives) == 1


# ---- (2) áp từng văn bản dev: kỳ vọng viết tay ----

K1 = c("D621.K1", "D621.K1.a", "D621.K1.b", "D621.K1.c", "D621.K1.d")
EXPECT = {
    1: dict(changed=[], new=[], closed=c("D621.K2"), named=[]),
    2: dict(changed=c("D621.K1", "D621.K1.b"), new=[], closed=[], named=c("D621.K1.a", "D621.K1.c", "D621.K1.d")),
    3: dict(changed=c("D626.K3"), new=c("D626.K2a"), closed=c("D626.K4", "D626.K5"), named=c("D626", "D626.K1", "D626.K2")),
    4: dict(changed=[], new=c("D621.K3", "D621a", "D621a.K1", "D621a.K2", "D650.K1.dd"), closed=[], named=[]),
    5: dict(changed=[], new=[], named=[], closed=c(
        "D621.K2", "D650.K1.a", "D626", "D626.K1", "D626.K2", "D626.K3", "D626.K4", "D626.K5",
        "D651", "D651.K1", "D651.K1.a", "D651.K1.b", "D651.K1.c", "D651.K2", "D651.K3")),
    6: dict(changed=c("D621.K2", "D644.K1", "D650.K1", "D650.K1.d", "D651.K1"), new=[], closed=[], named=[]),
    7: dict(changed=c("D621", "D626"), new=[], closed=[], named=[]),
    8: dict(changed=[], new=[], closed=None, named=[]),   # closed = mọi đơn vị trong triples của A1
}


def expected_sets(n):
    e = dict(EXPECT[n])
    if e["closed"] is None:
        e["closed"] = base_ids()
        assert len(e["closed"]) == 35
    return e


def test_dev_docs_change_sets_and_independent_scans():
    for n in DEV_FILES:
        run, e = run_dev(n), expected_sets(n)
        assert same(run.changed, e["changed"]), f"dev{n} changed {run.changed}"
        assert same(run.new, e["new"]), f"dev{n} new {run.new}"
        assert same(run.closed, e["closed"]), f"dev{n} closed {run.closed}"
        assert same(run.named_unchanged, e["named"]), f"dev{n} named_unchanged {run.named_unchanged}"
        U = set(e["changed"]) | set(e["closed"])
        assert sorted((s, p, o) for _, s, p, o, _ in run.broken) == scan_broken(e["closed"]), f"dev{n} cạnh đứt"
        assert run.impact == scan_impact(U, e["closed"]), f"dev{n} tập ảnh hưởng: {run.impact}"
        assert json.loads(json.dumps(run.changed_json())) == run.changed_json()
        assert set(run.changed_json()) == {"changed", "new", "closed", "named_unchanged"}


def test_dev01_repeal_khoan_2_dieu_621():
    run = run_dev(1)
    assert [(r["s"], r["p"], r["o"], r["directive_seq"], r["effective_from"], r["new_version"]) for r in run.amend_edges] == [
        (DEV_FILES[1], "repeals", P + "D621.K2", 1, DATE, None)]
    (k2,) = versions_of(run, P + "D621.K2")
    assert (k2["version"], k2["effective_from"], k2["effective_to"]) == (1, a4.BASE_EFFECTIVE, DATE)
    assert len(run.version_rows()) == 35 and all(r["version"] == 1 for r in run.version_rows())
    assert run.edge_changes == [] and run.broken == [] and run.impact == {}      # không đơn vị changed/new; không ai trỏ vào K2
    assert scan_broken([P + "D621.K2"]) == [] and scan_impact({P + "D621.K2"}, {P + "D621.K2"}) == {}


def test_dev02_sua_khoan_1_dieu_621():
    run = run_dev(2)
    for code, new_text in ((P + "D621.K1", "Những người sau đây không được quyền hưởng di sản theo quy định của pháp luật:"),
                           (P + "D621.K1.b", "Người vi phạm nghiêm trọng nghĩa vụ nuôi dưỡng, chăm sóc người để lại di sản;")):
        v1, v2 = versions_of(run, code)
        assert (v1["version"], v1["effective_from"], v1["effective_to"], v1["previous_version"]) == (1, a4.BASE_EFFECTIVE, "2027-07-01", None)
        assert (v2["version"], v2["effective_from"], v2["effective_to"], v2["previous_version"]) == (2, "2027-07-01", None, 1)
        assert (v2["source_doc"], v2["directive_seq"], v2["text"]) == (DEV_FILES[2], 1, new_text)
        assert v1["source_doc"] == a4.DOC_PREFIX and v1["directive_seq"] is None
    for code in K1[1:4:2] + c("D621.K1.d"):                                       # a, c, d giữ nguyên, chỉ một phiên bản
        (v,) = versions_of(run, code)
        assert v["version"] == 1 and v["effective_to"] is None
    assert [(r["p"], r["o"], r["new_version"], r["effective_from"]) for r in run.amend_edges] == [
        ("amends", P + "D621.K1", 2, "2027-07-01")]
    assert run.edge_changes == []                                                 # chữ mới không có dẫn chiếu
    assert run.impact == {P + "D621.K2": ["refers_to " + P + "D621.K1"], P + "D644.K2": ["refers_to " + P + "D621.K1"]}


def test_dev03_thay_dieu_626_khoan_bot_va_khoan_moi():
    run = run_dev(3)
    assert [(r["p"], r["o"], r["new_version"]) for r in run.amend_edges] == [("replaces", P + "D626", None)]  # gốc không đổi
    (k4,), (k5,) = versions_of(run, P + "D626.K4"), versions_of(run, P + "D626.K5")
    assert k4["effective_to"] == k5["effective_to"] == DATE
    (k2a,) = versions_of(run, P + "D626.K2a")
    assert (k2a["version"], k2a["type"], k2a["number"], k2a["effective_from"], k2a["previous_version"], k2a["source_doc"],
            k2a["text"]) == (1, "khoan", "2a", DATE, None, DEV_FILES[3], "Chỉ định người đại diện để thực hiện di chúc.")
    v1, v2 = versions_of(run, P + "D626.K3")
    assert (v2["version"], v2["previous_version"], v1["effective_to"]) == (2, 1, DATE)
    assert v2["text"] == "Dành một phần tài sản trong khối di sản để di tặng, thờ cúng hoặc sử dụng vào mục đích từ thiện."
    for code in c("D626", "D626.K1", "D626.K2"):
        assert len(versions_of(run, code)) == 1
    assert [(r["op"], r["s"], r["p"], r["o"], r["at"]) for r in run.edge_changes] == [
        ("add", P + "D626", "contains", P + "D626.K2a", DATE), ("add", P + "D626.K2a", "part_of", P + "D626", DATE)]
    assert run.impact == {} and run.broken == []


def test_dev04_bo_sung_dieu_621a_khoan_3_diem_dd():
    run = run_dev(4)
    want = {  # mã: (loại, số, directive_seq, text); Điều 621a có heading
        "D621a": ("dieu", "621a", 1, None), "D621a.K1": ("khoan", "1", 1, None), "D621a.K2": ("khoan", "2", 1, None),
        "D621.K3": ("khoan", "3", 2, None), "D650.K1.dd": ("diem", "đ", 3, "Trường hợp khác do pháp luật quy định.")}
    for code, (kind, number, seq, text) in want.items():
        (v,) = versions_of(run, P + code)
        assert (v["version"], v["type"], v["number"], v["effective_from"], v["effective_to"], v["previous_version"],
                v["source_doc"], v["directive_seq"]) == (1, kind, number, DATE, None, None, DEV_FILES[4], seq), code
        if text:
            assert v["text"] == text
    (d,) = versions_of(run, P + "D621a")
    assert d["heading"] == "Người bị hạn chế quyền hưởng di sản" and d["text"] is None
    assert [(r["o"], r["directive_seq"], r["new_version"]) for r in run.amend_edges] == [
        (P + "D621a", 1, 1), (P + "D621.K3", 2, 1), (P + "D650.K1.dd", 3, 1)]
    got = {(r["op"], r["s"], r["p"], r["o"]) for r in run.edge_changes}
    pairs = (("D621a", "D621a.K1"), ("D621a", "D621a.K2"), ("D621", "D621.K3"), ("D650.K1", "D650.K1.dd"))   # (cha, con mới)
    structural = {("add", P + a, "contains", P + b) for a, b in pairs} | {("add", P + b, "part_of", P + a) for a, b in pairs}
    refs ={("add", P + "D621a.K2", "refers_to", P + "D621a.K1"), ("add", P + "D621.K3", "refers_to", P + "D621.K1.a")}
    assert got == structural | refs and len(run.edge_changes) == 10, run.edge_changes
    ev = {(r["s"], r["o"]): r["evidence"] for r in run.edge_changes if r["p"] == "refers_to"}
    assert ev == {(P + "D621a.K2", P + "D621a.K1"): "khoản 1 Điều này", (P + "D621.K3", P + "D621.K1.a"): "điểm a khoản 1 Điều này"}
    assert not any(r["o"] == P + "D621a" and r["p"] == "refers_to" for r in run.edge_changes)   # "Điều 621a" không thành cạnh
    assert [(doc, u) for doc, u, _ in run.unhandled] == [(DEV_FILES[4], P + "D621a.K1")]          # "trừ trường hợp ..." chưa xử lý
    assert run.impact == {} and run.broken == []                                                  # chỉ thêm mới, không đổi/đóng


def test_dev05_bai_bo_danh_sach():
    run = run_dev(5)
    assert [(r["o"], r["directive_seq"]) for r in run.amend_edges] == [
        (P + "D621.K2", 1), (P + "D650.K1.a", 2), (P + "D626", 3), (P + "D651", 4)]
    assert {r["p"] for r in run.amend_edges} == {"repeals"}
    assert [(row[1], row[2], row[3]) for row in run.table] == [(1, 3, "repeal_unit"), (2, 3, "repeal_unit"), (3, 5, "repeal_unit"), (4, 5, "repeal_unit")]
    active = {r["id"] for r in a4.active_rows(run.version_rows(), DATE)}
    assert len(active) == 35 - 15 and P + "D644.K2" in active and P + "D650.K1.b" in active and P + "D651" not in active
    assert len([r for r in run.version_rows() if r["effective_to"] == DATE]) == 15


def test_dev06_cum_tu_inline_va_dong_pham_vi():
    run = run_dev(6)
    text = {code: versions_of(run, P + code)[-1]["text"] for code in ("D651.K1", "D621.K2", "D644.K1", "D650.K1", "D650.K1.d")}
    assert text == {
        "D651.K1": "Những người thừa kế theo pháp luật hiện hành được quy định theo thứ tự sau đây:",
        "D621.K2": "Những người quy định tại khoản 1 Điều này vẫn được hưởng di sản, nếu người để lại di sản đã biết hành vi của những người đó.",
        "D644.K1": "Những người sau đây vẫn được hưởng phần di sản bằng hai phần ba suất của một người thừa kế theo pháp luật nếu di sản được chia "
                   "theo pháp luật, trong trường hợp họ không được người lập di chúc hoặc cơ quan, tổ chức có thẩm quyền cho hưởng di sản hoặc chỉ cho "
                   "hưởng phần di sản ít hơn hai phần ba suất đó:",
        "D650.K1": "Thừa kế theo pháp luật luôn được áp dụng trong các trường hợp sau đây:",
        "D650.K1.d": "Những người được chỉ định làm người thừa kế theo di chúc mà không có quyền hưởng di sản."}
    assert [(len(versions_of(run, P + code)), versions_of(run, P + code)[-1]["directive_seq"]) for code in text] == [
        (2, 1), (2, 2), (2, 3), (2, 4), (2, 5)]       # D650.K1 do chỉ thị 4 tạo, chỉ thị 6 sửa tại chỗ nên vẫn là phiên bản 2
    for code in ("D650.K1.a", "D650.K1.b", "D650.K1.c", "D651.K1.a", "D644.K1.a", "D644.K2"):
        assert len(versions_of(run, P + code)) == 1
    assert [(r["p"], r["o"], r["directive_seq"], r["new_version"]) for r in run.amend_edges] == [
        ("amends", P + "D651.K1", 1, 2), ("amends", P + "D621.K2", 2, 2), ("amends", P + "D644.K1", 3, 2),
        ("replaces", P + "D650.K1", 4, 2), ("amends", P + "D650.K1", 5, None), ("replaces", P + "D650.K1", 6, 2)]
    assert run.edge_changes == []                       # D621.K2 vẫn dẫn chiếu "khoản 1 Điều này"
    assert run.impact == {P + "D644.K2": ["exception_of " + P + "D644.K1", "refers_to " + P + "D644.K1"]}


def test_dev07_doi_ten_dieu():
    run = run_dev(7)
    v1, v2 = versions_of(run, P + "D621")
    assert (v1["heading"], v1["effective_to"], v2["heading"], v2["version"], v2["previous_version"]) == (
        "Người không được quyền hưởng di sản", DATE, "Những người không được quyền hưởng di sản", 2, 1)
    assert v2["text"] == v1["text"] is None
    v1, v2 = versions_of(run, P + "D626")
    assert v2["heading"] == "Quyền của người lập di chúc theo pháp luật" and v2["text"] == v1["text"] == "Người lập di chúc có quyền sau đây:"
    assert [(r["p"], r["o"], r["new_version"]) for r in run.amend_edges] == [("amends", P + "D621", 2), ("amends", P + "D626", 2)]


def test_dev08_thay_the_ca_van_ban():
    run = run_dev(8)
    assert [(r["p"], r["o"], r["directive_seq"], r["new_version"]) for r in run.amend_edges] == [("replaces", "BLDS2015", 1, None)]
    assert all(r["effective_to"] == DATE and r["version"] == 1 for r in run.version_rows()) and len(run.version_rows()) == 35
    assert a4.active_rows(run.version_rows(), DATE) == [] and run.impact == {} and run.edge_changes == []


def test_base_rows_match_a1_triples():
    """Dòng gốc (version 1, source_doc là mã văn bản gốc) khớp từng chữ với triples của A1, với mọi văn bản dev."""
    with open(IN_DIR / f"a1_triples_{STEM}.jsonl", encoding="utf-8") as f:
        triples = {}
        for r in map(json.loads, f):
            triples.setdefault(r["s"], {})[r["p"]] = r["o"]
    for n in DEV_FILES:
        base = [r for r in run_dev(n).version_rows() if r["source_doc"] == a4.DOC_PREFIX]
        assert len(base) == 35
        for r in base:
            t = triples[r["id"]]
            assert (r["type"], r["number"], r["heading"], r["text"]) == (t["type"], t["number"], t.get("heading"), t.get("text")), r["id"]
            assert (r["version"], r["effective_from"], r["previous_version"], r["directive_seq"]) == (1, a4.BASE_EFFECTIVE, None, None)


# ---- cờ cạnh đứt và tập ảnh hưởng với đích có người trỏ tới (văn bản dựng tay) ----

def run_text(body, date="01 tháng 01 năm 2027"):
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "fx.md"
        p.write_text(amend_text(body, date), encoding="utf-8", newline="\n")
        return a4.apply_series(SAMPLE_FILE, [p])


def test_broken_edges_and_impact_when_target_has_referrers():
    run = run_text("Bãi bỏ khoản 1 Điều 621.")
    closed = c("D621.K1", "D621.K1.a", "D621.K1.b", "D621.K1.c", "D621.K1.d")
    assert same(run.closed, closed)
    got = sorted((s, p, o) for _, s, p, o, _ in run.broken)
    assert got == sorted([(P + "D621.K2", "refers_to", P + "D621.K1"), (P + "D644.K2", "refers_to", P + "D621.K1")]) == scan_broken(closed)
    assert run.impact == {P + "D621.K2": ["refers_to " + P + "D621.K1"], P + "D644.K2": ["refers_to " + P + "D621.K1"]} == scan_impact(closed, closed)
    assert {ev for *_, ev in run.broken} == {"khoản 1 Điều này", "khoản 1 Điều 621 của Bộ luật này"}

    run = run_text("Bãi bỏ khoản 1 Điều 644.")
    closed = c("D644.K1", "D644.K1.a", "D644.K1.b")
    got = sorted((s, p, o) for _, s, p, o, _ in run.broken)
    assert got == sorted([(P + "D644.K2", "refers_to", P + "D644.K1"), (P + "D644.K2", "exception_of", P + "D644.K1")]) == scan_broken(closed)
    assert run.impact == {P + "D644.K2": ["exception_of " + P + "D644.K1", "refers_to " + P + "D644.K1"]}

    # cạnh có nguồn bị đóng thì không cờ: đóng cả Điều 644 (nguồn D644.K2 cũng đóng)
    run = run_text("Bãi bỏ Điều 644.")
    assert all(s != P + "D644.K2" for _, s, *_ in run.broken) and run.impact == {}


def test_edge_changes_close_and_add_for_changed_source():
    run = run_text("Thay thế khoản 2 Điều 644 như sau:\n\n“2. Quy định tại khoản 1 Điều này áp dụng cho mọi trường hợp.”")
    assert run.changed == [P + "D644.K2"] and run.new == []
    closes = sorted((r["s"], r["p"], r["o"], r.get("evidence"), r.get("method")) for r in run.edge_changes if r["op"] == "close")
    assert closes == sorted([
        (P + "D644.K2", "refers_to", P + "D621.K1", "khoản 1 Điều 621 của Bộ luật này", None),
        (P + "D644.K2", "exception_of", P + "D644.K1", "khoản 1 Điều này không áp dụng", "not_apply_pattern")])
    assert [r for r in run.edge_changes if r["op"] == "add"] == []               # refers_to D644.K2 -> D644.K1 vẫn còn, không ghi lại
    assert all(r["at"] == DATE for r in run.edge_changes)
    # cạnh gốc không bị xoá khỏi file gốc: file không đổi và vẫn còn cạnh đã close
    assert any(r["s"] == P + "D644.K2" and r["p"] == "exception_of" for r in base_edges())


def test_exception_list_edges_follow_the_text_of_the_parent():
    """Quy tắc 2 của A3: chứng cứ là chữ của cha, nguồn là con. Cha đổi chữ thì cạnh của các con chưa đổi cũng add/close;
    con mới dưới cha đang có 'trừ ... sau đây:' thì có cạnh mới."""
    K1 = P + "D650.K1"
    with tempfile.TemporaryDirectory() as tmp:
        a = write(tmp, "a.md", amend_text("Sửa đổi cụm từ “được áp dụng trong trường hợp sau đây” thành cụm từ "
                                          "“được áp dụng, trừ trường hợp sau đây” tại khoản 1 Điều 650.", "01 tháng 01 năm 2027"))
        b = write(tmp, "b.md", amend_text("Bổ sung điểm đ vào sau điểm d khoản 1 Điều 650 như sau:\n\n“đ) Trường hợp khác.”", "01 tháng 7 năm 2027"))
        d = write(tmp, "c.md", amend_text("Sửa đổi cụm từ “, trừ trường hợp sau đây” thành cụm từ “ trong trường hợp sau đây” tại khoản 1 Điều 650.",
                                          "01 tháng 01 năm 2028"))
        run = a4.apply_series(SAMPLE_FILE, [a, b, d])
    by_step = [[(r["op"], r["s"], r["p"], r["o"], r["at"], r.get("method")) for r in s.edge_rows] for s in run.steps]
    exc = lambda op, letters, at: [(op, f"{K1}.{x}", "exception_of", K1, at, "except_list_pattern") for x in letters]
    assert by_step[0] == exc("add", ["a", "b", "c", "d"], "2027-01-01")                     # con chưa đổi, cha đổi chữ
    assert [r for r in by_step[1] if r[2] == "exception_of"] == exc("add", ["dd"], "2027-07-01")   # con mới, cha không đổi
    assert by_step[2] == exc("close", ["a", "b", "c", "d", "dd"], "2028-01-01")             # cha hết "trừ": đóng cả năm cạnh
    closed_ev = {r["evidence"] for s in run.steps for r in s.edge_rows if r["op"] == "close"}
    assert closed_ev == {"Thừa kế theo pháp luật được áp dụng, trừ trường hợp sau đây:"}  # evidence của cạnh bị đóng là chữ cũ của cha
    assert all(not (r["p"] == "exception_of" and r["s"].startswith(K1)) for r in base_edges())  # cạnh gốc không có, file gốc không đổi


def test_a2_error_on_changed_unit_stops_but_dangling_unchanged_edge_does_not():
    # đơn vị mới trỏ khoản 9 Điều 621 (Điều có mà khoản không có): A2 báo ValueError, A4 dừng và nêu mã đơn vị
    e = raises("E_A2", run_text, "Bổ sung khoản 3 vào Điều 621 như sau:\n\n“3. Xem khoản 9 Điều này.”")
    assert P + "D621.K3" in e.message
    # D644.K2 (không đổi) vẫn trỏ D621.K1 đã đóng: chỉ là cờ cạnh đứt, A2 không chạy lại trên nó
    run = run_text("Bãi bỏ khoản 1 Điều 621.")
    assert run.broken


# ---- (3) snapshot ----

BASE_TEXT = SAMPLE_FILE.read_text(encoding="utf-8")
L = BASE_TEXT.rstrip("\n").split("\n")   # L[i] là dòng thứ i+1 của file mẫu


def snapshot(run, date):
    return a4.render_markdown(a4.active_rows(run.version_rows(), date))


def unit_view(units):
    return [(u.id, u.type, u.number, u.heading, "\n".join(u.parts) if u.parts else None) for u in units]


def reparse(md):
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "blds2015_5dieu.md"      # a1.load_parsed nhận theo tên file
        p.write_text(md, encoding="utf-8", newline="\n")
        _, parsed = a1.load_parsed(p)
    assert not parsed.errors, parsed.errors
    return unit_view(parsed.units)


def test_snapshot_before_earliest_date_equals_base_file():
    base_view = reparse(BASE_TEXT)
    assert len(base_view) == 35
    for n in DEV_FILES:
        md = snapshot(run_dev(n), "2026-12-31")
        assert reparse(md) == base_view, f"dev{n}: snapshot trước ngày hiệu lực khác file gốc (parse lại bằng a1)"
        assert md == BASE_TEXT, f"dev{n}: snapshot trước ngày hiệu lực không giống từng byte file gốc"


def test_snapshot_after_effective_date_matches_handwritten_text():
    # văn bản 1: bỏ khoản 2 Điều 621 = bỏ dòng 10-11 của file mẫu
    assert snapshot(run_dev(1), DATE) == "\n".join(L[0:9] + L[11:]) + "\n"
    # văn bản 3: thay Điều 626 (dòng 12-24) bằng khối viết tay
    block = ["### Điều 626\\. Quyền của người lập di chúc", "", "Người lập di chúc có quyền sau đây:", "",
             "**1\\.** Chỉ định người thừa kế; truất quyền hưởng di sản của người thừa kế.", "",
             "**2\\.** Phân định phần di sản cho từng người thừa kế.", "",
             "**2a\\.** Chỉ định người đại diện để thực hiện di chúc.", "",
             "**3\\.** Dành một phần tài sản trong khối di sản để di tặng, thờ cúng hoặc sử dụng vào mục đích từ thiện."]
    assert snapshot(run_dev(3), DATE) == "\n".join(L[0:11] + block + [""] + L[25:]) + "\n"
    # văn bản 5: bỏ K2 Điều 621 (10-11), Điều 626 (12-25), điểm a K1 Điều 650 (39), Điều 651 (50-60)
    assert snapshot(run_dev(5), DATE) == "\n".join(L[0:9] + L[25:38] + L[39:48]) + "\n"
    # văn bản 7: đổi tên Điều 621 (dòng 1) và Điều 626 (dòng 12)
    want = list(L)
    want[0] = "### Điều 621\\. Những người không được quyền hưởng di sản"
    want[11] = "### Điều 626\\. Quyền của người lập di chúc theo pháp luật"
    assert snapshot(run_dev(7), DATE) == "\n".join(want) + "\n"
    # văn bản 8: thay cả văn bản, không còn đơn vị nào
    assert snapshot(run_dev(8), DATE) == ""
    # a1 đọc lại được snapshot của các văn bản không có hậu tố và còn đủ 5 Điều (EXPECTED_DIEU của a1 đòi đủ 5):
    # văn bản 1 bỏ K2 Điều 621; văn bản 7 chỉ đổi tên hai Điều. Danh sách (mã, loại, số, heading, text) viết tay từ file mẫu.
    base_view = reparse(BASE_TEXT)
    assert reparse(snapshot(run_dev(1), DATE)) == [u for u in base_view if u[0] != P + "D621.K2"]
    renamed = {P + "D621": "Những người không được quyền hưởng di sản", P + "D626": "Quyền của người lập di chúc theo pháp luật"}
    assert reparse(snapshot(run_dev(7), DATE)) == [(i, t, n, renamed.get(i, h), x) for i, t, n, h, x in base_view]


def test_snapshot_after_dev04_contains_dieu_621a_in_order():
    md = snapshot(run_dev(4), DATE)
    assert "### Điều 621a\\. Người bị hạn chế quyền hưởng di sản" in md
    i621, i621a, i626 = (md.index(f"### Điều {x}\\.") for x in ("621", "621a", "626"))
    assert i621 < i621a < i626                                       # Điều xếp theo (số, hậu tố)
    assert md.index("**2\\.** Những người quy định") < md.index("**3\\.** Người quy định tại điểm a") < i621a
    lines = md.split("\n")
    d = next(i for i, l in enumerate(lines) if l.startswith("- **d)** Những người được chỉ định"))
    assert lines[d].endswith("  ") is True and lines[d + 1] == "- **đ)** Trường hợp khác do pháp luật quy định."
    assert not lines[d + 1].endswith(" ")                            # điểm cuối nhóm không có hai dấu cách
    assert lines[d - 1].endswith("  ")
    assert md.count("### Điều ") == 6 and md.endswith("\n") and not md.endswith("\n\n")


def test_active_rows_half_open_interval():
    rows = [{"id": "x", "effective_from": None, "effective_to": "2027-01-01"},
            {"id": "y", "effective_from": "2027-01-01", "effective_to": None},
            {"id": "z", "effective_from": "2027-01-01", "effective_to": "2027-07-01"}]
    ids = lambda d: [r["id"] for r in a4.active_rows(rows, d)]
    assert ids("2026-12-31") == ["x"] and ids("2027-01-01") == ["y", "z"] and ids("2027-06-30") == ["y", "z"] and ids("2027-07-01") == ["y"]


# ---- (4) nạp liên tiếp ----

def test_series_dev01_then_dev02():
    for order in ((1, 2), (2, 1)):                    # thứ tự trên dòng lệnh không quan trọng: sắp theo ngày hiệu lực
        run = run_dev(*order)
        assert [d.doc_id for d in run.docs] == [DEV_FILES[1], DEV_FILES[2]]
        rows = run.version_rows()
        assert len(rows) == 35 + 2                    # K1 và K1.b có thêm phiên bản 2
        by_id = {}
        for r in rows:
            by_id.setdefault(r["id"], []).append(r)
        assert {i: len(v) for i, v in by_id.items() if len(v) > 1} == {P + "D621.K1": 2, P + "D621.K1.b": 2}
        (k2,) = by_id[P + "D621.K2"]
        assert (k2["version"], k2["effective_to"]) == (1, DATE)                    # văn bản 1 đóng K2 ngày 2027-01-01
        v1, v2 = by_id[P + "D621.K1"]
        assert (v1["effective_to"], v2["effective_from"], v2["previous_version"], v2["source_doc"]) == ("2027-07-01", "2027-07-01", 1, DEV_FILES[2])
        assert [(r["s"], r["p"], r["o"]) for r in run.amend_edges] == [
            (DEV_FILES[1], "repeals", P + "D621.K2"), (DEV_FILES[2], "amends", P + "D621.K1")]
        assert same(run.closed, c("D621.K2")) and same(run.changed, c("D621.K1", "D621.K1.b"))
        # K2 đã bị đóng từ văn bản 1 nên không còn là nguồn trỏ vào K1 đang đổi: chỉ D644.K2 bị ảnh hưởng
        assert run.impact == {P + "D644.K2": ["refers_to " + P + "D621.K1"]}
        mar, jul = snapshot(run, "2027-03-01"), snapshot(run, "2027-07-01")
        assert "**2\\.** Những người quy định" not in mar and "không được quyền hưởng di sản:" in mar
        assert "theo quy định của pháp luật:" not in mar and "theo quy định của pháp luật:" in jul
    # tên mặc định: các doc-id nối bằng '+' theo thứ tự trên dòng lệnh
    assert run_dev(1, 2).name == f"{DEV_FILES[1]}+{DEV_FILES[2]}" and run_dev(2, 1).name == f"{DEV_FILES[2]}+{DEV_FILES[1]}"


def test_series_later_document_sees_state_after_earlier_one():
    with tempfile.TemporaryDirectory() as tmp:
        a = Path(tmp) / "first.md"
        a.write_text(amend_text("Bãi bỏ khoản 2 Điều 621."), encoding="utf-8")
        b = Path(tmp) / "second.md"
        b.write_text(amend_text("Bổ sung khoản 2 vào Điều 621 như sau:\n\n“2. Nội dung.”", "01 tháng 7 năm 2027"), encoding="utf-8")
        raises("E_EXISTS", a4.apply_series, SAMPLE_FILE, [a, b])                  # mã đã đóng vẫn là mã đã từng tồn tại
        c_ = Path(tmp) / "third.md"
        c_.write_text(amend_text("Khoản 2 Điều 621 được sửa đổi như sau:\n\n“2. Nội dung.”", "01 tháng 7 năm 2027"), encoding="utf-8")
        raises("E_TARGET", a4.apply_series, SAMPLE_FILE, [a, c_])                 # đích đã bị đóng ở văn bản trước


# ---- (5) lỗi: exit 1, chỉ báo cáo ----

def test_error_unknown_line_without_hook():
    r = apply_cli_error("E_UNKNOWN_LINE", [amend_text("Khoản 2 Điều 621 được thay thế bằng quy định mới.")])
    assert "dòng: 3: Khoản 2 Điều 621 được thay thế bằng quy định mới." in r


def test_error_no_directive():
    raises("E_NO_DIRECTIVE", parse_body, "Ghi chú không liên quan.")
    apply_cli_error("E_NO_DIRECTIVE", [amend_text("Ghi chú không liên quan.")])


def test_error_target_missing_and_closed():
    apply_cli_error("E_TARGET", [amend_text("Bãi bỏ khoản 9 Điều 621.")])
    apply_cli_error("E_TARGET", [amend_text("Điều 700 được sửa đổi như sau:\n\n“Điều 700. Tên”")])
    apply_cli_error("E_TARGET", [amend_text("Bỏ cụm từ “a” tại khoản 1 Điều 99.")])
    apply_cli_error("E_TARGET", [amend_text("Tên Điều 99 được sửa đổi như sau:\n\n“Tên mới”")])


def test_error_insert_existing_code():
    r = apply_cli_error("E_EXISTS", [amend_text("Bổ sung khoản 2 vào Điều 621 như sau:\n\n“2. Nội dung.”")])
    assert "dòng: 3" in r
    apply_cli_error("E_EXISTS", [amend_text("Bổ sung Điều 626 như sau:\n\n“Điều 626. Tên”")])


def test_error_insert_parent_after_and_order():
    apply_cli_error("E_PARENT", [amend_text("Bổ sung khoản 1 vào Điều 700 như sau:\n\n“1. Nội dung.”")])
    apply_cli_error("E_PARENT", [amend_text("Bổ sung điểm e vào khoản 7 Điều 621 như sau:\n\n“e) Nội dung.”")])
    apply_cli_error("E_AFTER", [amend_text("Bổ sung khoản 3 vào sau khoản 4 Điều 621 như sau:\n\n“3. Nội dung.”")])   # khoản 4 không có
    apply_cli_error("E_AFTER", [amend_text("Bổ sung Điều 640 vào sau Điều 644 như sau:\n\n“Điều 640. Tên”")])           # xếp trước, không sau


def test_error_root_number_or_kind_differs_from_target():
    apply_cli_error("E_ROOT", [amend_text("Khoản 1 Điều 621 được sửa đổi như sau:\n\n“2. Nội dung.”")])
    apply_cli_error("E_ROOT", [amend_text("Khoản 1 Điều 621 được sửa đổi như sau:\n\n“a) Nội dung.”")])
    apply_cli_error("E_ROOT", [amend_text("Điều 626 được sửa đổi như sau:\n\n“Điều 627. Tên”")])
    apply_cli_error("E_ROOT", [amend_text("Bổ sung khoản 3 vào Điều 621 như sau:\n\n“4. Nội dung.”")])


def test_error_phrase_not_found_anywhere_in_target_tree():
    r = apply_cli_error("E_PHRASE_MISSING", [amend_text("Bỏ cụm từ “không có ở đâu cả” tại Điều 621.")])
    assert "dòng: 3" in r
    # chỉ cần có ở một đơn vị trong cây là đủ; thiếu ở cây của một đích khác thì lỗi
    apply_cli_error("E_PHRASE_MISSING", [amend_text("Bỏ cụm từ “Chỉ định” tại khoản 1 Điều 626 và khoản 2 Điều 626.")])


def test_error_missing_date_and_conflicting_dates():
    apply_cli_error("E_NO_DATE", [amend_text("Bãi bỏ khoản 2 Điều 621.", date=None)])
    two = amend_text("Bãi bỏ khoản 2 Điều 621.") + "Luật này có hiệu lực thi hành từ ngày 02 tháng 01 năm 2027.\n"
    apply_cli_error("E_DATE_CONFLICT", [two])
    same_date_twice = amend_text("Bãi bỏ khoản 2 Điều 621.") + "Điều này có hiệu lực từ ngày 1 tháng 1 năm 2027.\n"
    with sandbox() as tmp:                              # hai khớp trùng ngày tính là một ngày: không lỗi
        assert cli("apply", "--base", SAMPLE_FILE, "--amend", write(tmp, "x.md", same_date_twice))[0] == 0


def test_error_effective_date_not_after_base_and_base_doc_id():
    """Review F-08: văn bản sửa đổi phải có hiệu lực SAU ngày hiệu lực của văn bản gốc; doc-id không được trùng mã văn bản gốc."""
    for date in ("01 tháng 6 năm 2016", "01 tháng 01 năm 2017"):
        apply_cli_error("E_DATE_BEFORE_BASE", [amend_text("Bãi bỏ khoản 2 Điều 621.", date=date)])
    raises("E_ARGS", a4.apply_series, SAMPLE_FILE, [(dev(1), a4.DOC_PREFIX)])
    with sandbox() as tmp:                              # ngày ngay sau ngày gốc: hợp lệ
        assert cli("apply", "--base", SAMPLE_FILE, "--amend",
                   write(tmp, "x.md", amend_text("Bãi bỏ khoản 2 Điều 621.", date="02 tháng 01 năm 2017")))[0] == 0


def write(tmp, name, text):
    p = Path(tmp) / name
    p.write_text(text, encoding="utf-8", newline="\n")
    return p


def test_error_renumbering_not_supported():
    apply_cli_error("E_UNSUPPORTED", [amend_text("Bổ sung khoản 3 vào Điều 621 và đánh số lại các khoản như sau:\n\n“3. Nội dung.”")])
    apply_cli_error("E_UNSUPPORTED", [amend_text("Khoản 3 Điều 621 trở thành khoản 4.")])
    apply_cli_error("E_UNSUPPORTED", [amend_text("Bãi bỏ khoản 2 Điều 621.\nĐánh số lại các khoản còn lại.")])
    # chữ "trở thành" trong nội dung trong nháy là chữ của luật, không phải chỉ thị: không lỗi
    run = run_text("Bổ sung khoản 3 vào Điều 621 như sau:\n\n“3. Người đó trở thành người thừa kế.”")
    assert run.new == c("D621.K3")


def test_error_overlapping_directives():
    apply_cli_error("E_OVERLAP", [amend_text("Bãi bỏ khoản 1 Điều 621.\n\nBãi bỏ điểm a khoản 1 Điều 621.")])               # tổ tiên
    apply_cli_error("E_OVERLAP", [amend_text("Bãi bỏ khoản 2 Điều 621.\n\nBãi bỏ khoản 2 Điều 621.")])                         # bằng nhau
    apply_cli_error("E_OVERLAP", [amend_text("Bãi bỏ khoản 1 Điều 621 và điểm a khoản 1 Điều 621.")])                         # trong cùng dòng
    apply_cli_error("E_OVERLAP", [amend_text("Khoản 1 Điều 621 được sửa đổi như sau:\n\n“1. Nội dung.”\n\nBỏ cụm từ “a” tại điểm a khoản 1 Điều 621.")])
    apply_cli_error("E_OVERLAP", [amend_text("Điều 621 được thay thế như sau:\n\n“Điều 621. Tên”\n\nBổ sung khoản 3 vào Điều 621 như sau:\n\n“3. A.”")])
    # hai chỉ thị cụm từ chồng lấn thì được (dev06 đã dùng); một chỉ thị cụm từ có hai đích chồng nhau thì không
    apply_cli_error("E_OVERLAP", [amend_text("Bỏ cụm từ “a” tại khoản 1 Điều 621 và điểm a khoản 1 Điều 621.")])
    run = run_text("Bỏ cụm từ “Những người sau” tại khoản 1 Điều 621.\n\nBỏ cụm từ “đây không” tại Điều 621.")
    assert P + "D621.K1" in run.changed


def test_error_effective_from_flag():
    text = amend_text("Bãi bỏ khoản 2 Điều 621.")
    r = apply_cli_error("E_DATE_FLAG", [text], "--effective-from", "2027-02-02")
    assert "2027-01-01" in r
    with sandbox() as tmp:                               # cờ trùng ngày trong văn bản: dùng được; văn bản không có ngày: cờ cung cấp
        assert cli("apply", "--base", SAMPLE_FILE, "--amend", write(tmp, "a.md", text), "--effective-from", "2027-01-01")[0] == 0
        no_date = write(tmp, "b.md", amend_text("Bãi bỏ khoản 2 Điều 621.", date=None))
        assert cli("apply", "--base", SAMPLE_FILE, "--amend", no_date, "--effective-from", "2028-03-04", "--name", "flagonly")[0] == 0
        assert json.loads((a4.OUT_DIR / "a4_flagonly_amend_edges.jsonl").read_text(encoding="utf-8"))["effective_from"] == "2028-03-04"
    apply_cli_error("E_ARGS", [text], "--effective-from", "01/01/2027")


def test_error_reflist_matches_only_part():
    apply_cli_error("E_REFLIST", [amend_text("Bãi bỏ khoản 2 Điều 621 và điểm a.")])
    apply_cli_error("E_REFLIST", [amend_text("Bãi bỏ khoản 2 Điều 621 điểm a khoản 1 Điều 650.")])
    apply_cli_error("E_REFLIST", [amend_text("Bỏ cụm từ “a” tại khoản 1 Điều 621 và.")])


def test_error_same_date_two_documents():
    r = apply_cli_error("E_SAME_DATE", [amend_text("Bãi bỏ khoản 2 Điều 621."), amend_text("Bãi bỏ khoản 1 Điều 644.")])
    assert "2027-01-01" in r


def test_error_scope_body_order_and_headings():
    apply_cli_error("E_SCOPE", [amend_text("Bỏ cụm từ “a”.")])
    apply_cli_error("E_ORDER", [amend_text("Khoản 1 Điều 621 được sửa đổi như sau:\n\n“1. Lead.\n\na) A;\nc) C.”")])        # a rồi c
    apply_cli_error("E_ORDER", [amend_text("Điều 626 được thay thế như sau:\n\n“Điều 626. Tên\n\n1. A.\n\n3. C.”")])         # khoản 1 rồi 3
    apply_cli_error("E_ORDER", [amend_text("Điều 626 được thay thế như sau:\n\n“Điều 626. Tên\n\n2. B.”")])                 # không bắt đầu từ 1
    apply_cli_error("E_ORDER", [amend_text("Khoản 1 Điều 621 được sửa đổi như sau:\n\n“1. Lead.\n\nf) A.”")])              # f ngoài bảng chữ
    apply_cli_error("E_BODY", [amend_text("Khoản 1 Điều 621 được sửa đổi như sau:\n\n“1. Lead.\n\n2. Khoản thứ hai.”")])    # hai gốc
    apply_cli_error("E_BODY", [amend_text("Khoản 1 Điều 621 được sửa đổi như sau:\n\n“1. Chưa đóng nháy.")])
    apply_cli_error("E_BODY", [amend_text("Khoản 1 Điều 621 được sửa đổi như sau:\n\n“1. Nội dung.” thêm chữ ngoài nháy")])
    apply_cli_error("E_BODY", [amend_text("Khoản 1 Điều 621 được sửa đổi như sau:\n\nKhông có nháy nào.")])
    apply_cli_error("E_HEADING", [amend_text("Tên Điều 621 được sửa đổi như sau:\n\n“Điều 621. Tên cũ sai” được sửa đổi thành “Điều 621. Tên mới”.")])


def test_error_report_content_and_no_stale_files():
    with sandbox() as tmp:
        (tmp / "a4_dev_versions.jsonl").write_text("cũ\n", encoding="utf-8")                  # file của lần chạy trước không bị đụng
        p = tmp / "bad.md"
        p.write_text(amend_text("Bãi bỏ khoản 9 Điều 621."), encoding="utf-8")
        code, _, err = cli("apply", "--base", SAMPLE_FILE, "--amend", p, "--name", "dev")
        assert code == 1 and "E_TARGET" in err
        assert (tmp / "a4_dev_versions.jsonl").read_text(encoding="utf-8") == "cũ\n"
        assert not (tmp / "a4_dev_changed.json").exists()
        report = (tmp / "a4_report_dev.txt").read_text(encoding="utf-8")
        assert report.splitlines()[:5] == ["A4 LỖI: dev", "mã lỗi: E_TARGET", "văn bản: bad", "dòng: 3: Bãi bỏ khoản 9 Điều 621.",
                                           "mô tả: đích BLDS2015.D621.K9 không tồn tại"]


def test_script_runs_isolated_and_exits_1_on_error():
    name = "_test_a4_subprocess"
    report = ROOT / "docs" / f"a4_report_{name}.txt"
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "bad.md"
        bad.write_text(amend_text("Bãi bỏ khoản 9 Điều 621."), encoding="utf-8")
        try:
            r = subprocess.run([sys.executable, "-I", str(ROOT / "src" / "a4_versions.py"), "apply", "--base", str(SAMPLE_FILE),
                                "--amend", str(bad), "--name", name], capture_output=True, text=True, encoding="utf-8")
            assert r.returncode == 1 and "E_TARGET" in r.stderr, (r.returncode, r.stderr)
            assert report.exists() and not list((ROOT / "data" / "processed").glob(f"a4_{name}_*"))
        finally:
            report.unlink(missing_ok=True)


# ---- (6) chữ không đổi thì không tạo phiên bản ----

def test_identical_text_creates_no_version():
    run = run_text("Khoản 2 Điều 626 được thay thế như sau:\n\n“2. Phân định phần di sản cho từng người thừa kế.”")
    assert run.changed == [] and run.new == [] and run.closed == [] and run.named_unchanged == [P + "D626.K2"]
    assert all(r["version"] == 1 and r["effective_to"] is None for r in run.version_rows())
    assert [(r["p"], r["o"], r["new_version"]) for r in run.amend_edges] == [("replaces", P + "D626.K2", None)]
    assert run.edge_changes == [] and run.impact == {}
    # cả cây giống hệt: Điều 650 K2 và ba Điểm (chữ chép từ dòng 44-48 của file mẫu)
    run = run_text(
        "Khoản 2 Điều 650 được sửa đổi như sau:\n\n"
        "“2. Thừa kế theo pháp luật cũng được áp dụng đối với các phần di sản sau đây:\n\n"
        "a) Phần di sản không được định đoạt trong di chúc;\n"
        "b) Phần di sản có liên quan đến phần của di chúc không có hiệu lực pháp luật;\n"
        "c) Phần di sản có liên quan đến người được thừa kế theo di chúc nhưng họ không có quyền hưởng di sản, từ chối nhận di sản, "
        "chết trước hoặc chết cùng thời điểm với người lập di chúc; liên quan đến cơ quan, tổ chức được hưởng di sản theo di chúc, "
        "nhưng không còn tồn tại vào thời điểm mở thừa kế.”")
    assert run.changed == [] and run.closed == [] and same(run.named_unchanged, c("D650.K2", "D650.K2.a", "D650.K2.b", "D650.K2.c"))
    # phiên bản mới chỉ khi chữ đổi, kể cả dấu cách thừa được chuẩn hoá thì không tính là đổi
    run = run_text("Khoản 2 Điều 626 được thay thế như sau:\n\n“2.   Phân định  phần di sản cho từng người   thừa kế.”")
    assert run.changed == [] and run.named_unchanged == [P + "D626.K2"]
    run = run_text("Sửa đổi cụm từ “người thừa kế” thành cụm từ “người thừa kế” tại khoản 2 Điều 626.")
    assert run.changed == [] and run.named_unchanged == [P + "D626.K2"]


# ---- (7) cờ chưa phủ ----

def test_uncovered_mentions_consistent_with_find_refs():
    run = run_dev(4)
    sentence = versions_of(run, P + "D621a.K2")[0]["text"]
    assert "Điều 621a của Bộ luật này" in sentence
    refs = a2.find_refs({"X": {"type": "khoan", "number": "2", "source_line": 0, "text": sentence}})[0]
    recognized = any("621a" in r.phrase for r in refs)
    listed = [m for _, u, m, _ in run.uncovered if u == P + "D621a.K2"]
    assert ("Điều 621a" in listed) == (not recognized), (listed, [r.phrase for r in refs])
    assert "khoản 1" not in listed                                         # "khoản 1 Điều này" được A2 nhận ra nên không phải chưa phủ
    report = a4.format_report(run)
    section = report.split("== Chưa phủ")[1].split("== Chưa tính cạnh")[0]
    assert (f"{DEV_FILES[4]}\t{P}D621a.K2\tĐiều 621a\t" in section) == (not recognized)
    # mention chỉ tính cho đơn vị changed ∪ new: Điều 644 K2 (không đổi) có "Điều 620" nhưng không xuất hiện
    assert all(u in run.new for _, u, _, _ in run.uncovered)


def test_uncovered_mentions_cases():
    case = lambda text: [m for _, m, _ in a4.uncovered_mentions("X", text)]
    assert case("theo khoản 2a Điều 626, điểm đ khoản 1 Điều 650") != [] and "khoản 2a" in case("theo khoản 2a Điều 626")
    assert case("quy định tại điểm a khoản 1 Điều này") == []                 # A2 nhận ra cả cụm
    assert case("điểm chỉ và khoản này") == []                                 # không phải mention
    assert case("Điều 5a và Điều 7") == ["Điều 5a"]
    assert case("Khoản 3a Điều này") == ["Khoản 3a"]                           # chữ hoa đầu câu vẫn là mention


def test_suffix_codes_accepted_by_a2_a3_as_sources():
    """A4 dựa vào việc A2/A3 nhận mã có hậu tố chữ làm nguồn (không sửa A2/A3). Khoá giả định này."""
    def U(kind, text=None):
        return {"type": kind, "number": "x", "source_line": 0, **({"text": text} if text else {})}
    units = {"X.D5": U("dieu"), "X.D5.K1": U("khoan", "nội dung"), "X.D5a": U("dieu"), "X.D5a.K1": U("khoan", "nội dung"),
             "X.D5a.K2": U("khoan", "Khoản 1 Điều này không áp dụng đối với khoản 1 Điều 5."),
             "X.D5a.K3": U("khoan", "Mọi người, trừ những người sau đây:"), "X.D5a.K3.a": U("diem", "a")}
    refs, _ = a2.build_refs(units)
    assert refs == [("X.D5a.K2", "refers_to", "X.D5a.K1", "Khoản 1 Điều này"), ("X.D5a.K2", "refers_to", "X.D5.K1", "khoản 1 Điều 5")]
    exc, handled, unhandled = a3.find_exceptions(units, a2.build_edges(units))
    assert [(s, o, m) for s, _, o, _, m in exc] == [("X.D5a.K2", "X.D5a.K1", a3.NOT_APPLY), ("X.D5a.K3.a", "X.D5a.K3", a3.EXCEPT_LIST)]
    # đích có hậu tố thì A2 không nhận: không cạnh nào ra (đó là lý do có cờ "chưa phủ"); A4 gọi với allow_uncovered=True,
    # còn mặc định của A2 là dừng (review F-02)
    units["X.D5.K1"]["text"] = "theo Điều 5a của Bộ luật này"
    assert a2.build_refs(units, allow_uncovered=True)[0] == refs[:2]
    try:
        a2.build_refs(units)
    except ValueError as e:
        assert "Điều 5a" in str(e), e
    else:
        raise AssertionError("A2 mặc định phải dừng với 'Điều 5a'")


def test_exclude_suffix_mode_reports_units_and_skips_edges():
    old = a4.A2A3_ACCEPT_SUFFIX
    a4.A2A3_ACCEPT_SUFFIX = False
    try:
        run = run_dev(4)
    finally:
        a4.A2A3_ACCEPT_SUFFIX = old
    assert sorted(u for _, u in run.excluded) == sorted(c("D621a", "D621a.K1", "D621a.K2"))
    refs = {(r["s"], r["o"]) for r in run.edge_changes if r["p"] == "refers_to"}
    assert refs == {(P + "D621.K3", P + "D621.K1.a")}                          # D621a.K2 -> D621a.K1 không được tính
    assert any(r["s"] == P + "D621a" and r["p"] == "contains" for r in run.edge_changes)   # cạnh cấu trúc vẫn có
    section = a4.format_report(run).split("== Chưa tính cạnh")[1]
    assert all(f"{DEV_FILES[4]}\t{P}{u}" in section for u in ("D621a", "D621a.K1", "D621a.K2"))
    assert run_dev(4).excluded == [] and "(không có:" in a4.format_report(run_dev(4)).split("== Chưa tính cạnh")[1]   # chế độ mặc định


# ---- (8) hàm móc normalize_unknown_line ----

STRANGE = "Khoản 2 Điều 621 được thay thế bằng quy định mới."


def run_with_hook(hook, body):
    old = a4.normalize_unknown_line
    a4.normalize_unknown_line = hook
    try:
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "fx.md"
            p.write_text(amend_text(body), encoding="utf-8", newline="\n")
            return a4.apply_series(SAMPLE_FILE, [a4.AmendSpec(str(p), "X")])
    finally:
        a4.normalize_unknown_line = old


def test_default_hook_returns_none():
    assert a4.normalize_unknown_line(STRANGE) is None


def test_hook_canonical_line_gives_same_result_as_that_line():
    calls = []

    def hook(line):
        calls.append(line)
        return "Bãi bỏ khoản 2 Điều 621." if line == STRANGE else None

    got = run_with_hook(hook, STRANGE)
    want = run_with_hook(lambda line: None, "Bãi bỏ khoản 2 Điều 621.")
    assert calls == [STRANGE]
    for attr in ("changed", "new", "closed", "named_unchanged", "amend_edges", "edge_changes", "impact", "broken", "table"):
        assert getattr(got, attr) == getattr(want, attr), attr
    assert got.version_rows() == want.version_rows()
    # chỉ thị có nội dung trong nháy: hàm móc trả dòng chuẩn, nội dung lấy từ các dòng sau như thường
    block = "\n\n“1. Những người sau đây không được quyền hưởng di sản theo pháp luật:”"
    got = run_with_hook(lambda line: "Khoản 1 Điều 621 được sửa đổi như sau:" if line == "Khoản 1 Điều 621 được thay thế bằng quy định mới." else None,
                        "Khoản 1 Điều 621 được thay thế bằng quy định mới." + block)
    want = run_with_hook(lambda line: None, "Khoản 1 Điều 621 được sửa đổi như sau:" + block)
    assert got.version_rows() == want.version_rows() and got.amend_edges == want.amend_edges
    assert got.changed == c("D621.K1") and same(got.closed, c("D621.K1.a", "D621.K1.b", "D621.K1.c", "D621.K1.d"))


def test_hook_unparseable_line_is_still_error():
    for bad in ("xin chào", "Bãi bỏ", "", "Khoản 2 Điều 621 được thay thế bằng quy định mới."):    # dòng cuối: trả lại chính dòng lạ
        raises("E_UNKNOWN_LINE", run_with_hook, lambda line, bad=bad: bad, STRANGE)
    raises("E_UNKNOWN_LINE", run_with_hook, lambda line: None, STRANGE)


# ---- tập ảnh hưởng, định dạng file ----

def test_impact_set_function():
    edges = [("a", "refers_to", "u"), ("b", "refers_to", "x"), ("c", "exception_of", "u"), ("u", "exception_of", "d"),
             ("u", "contains", "e"), ("f", "part_of", "u"), ("g", "refers_to", "u"), ("c", "refers_to", "u")]
    assert a4.impact_set({"u"}, edges) == {
        "a": ["refers_to u"], "c": ["exception_of u", "refers_to u"], "d": ["exception_of_by u"], "g": ["refers_to u"]}
    assert a4.impact_set(set(), edges) == {} and a4.impact_set({"zzz"}, edges) == {}


def test_cli_writes_all_files_with_conventions():
    with sandbox() as tmp:
        code, out, _ = cli("apply", "--base", SAMPLE_FILE, "--amend", dev(2))
        assert code == 0, out
        name = DEV_FILES[2]
        assert data_files(tmp) == sorted(f"a4_{name}_{k}" for k in ("amend_edges.jsonl", "changed.json", "edge_changes.jsonl", "impact.json", "versions.jsonl"))
        assert (tmp / f"a4_report_{name}.txt").exists()
        for p in tmp.iterdir():
            raw = p.read_bytes()
            assert not raw.startswith(b"\xef\xbb\xbf") and b"\r" not in raw and b"\\u" not in raw, p.name
            assert raw == b"" or (raw.endswith(b"\n") and not raw.endswith(b"\n\n")), p.name    # jsonl rỗng khi không có dòng nào
        rows = [json.loads(line) for line in (tmp / f"a4_{name}_versions.jsonl").read_text(encoding="utf-8").split("\n") if line]
        assert all(list(r) == ["id", "version", "type", "number", "heading", "text", "effective_from", "effective_to",
                               "previous_version", "source_doc", "directive_seq"] for r in rows)
        assert (len(rows), sum(1 for r in rows if r["heading"] is not None)) == (37, 5)
        edge = json.loads((tmp / f"a4_{name}_amend_edges.jsonl").read_text(encoding="utf-8"))
        assert list(edge) == ["s", "p", "o", "directive_seq", "effective_from", "new_version"]
        assert json.loads((tmp / f"a4_{name}_changed.json").read_text(encoding="utf-8")) == {
            "changed": c("D621.K1", "D621.K1.b"), "new": [], "closed": [], "named_unchanged": c("D621.K1.a", "D621.K1.c", "D621.K1.d")}
        assert json.loads((tmp / f"a4_{name}_impact.json").read_text(encoding="utf-8")) == {
            P + "D621.K2": ["refers_to " + P + "D621.K1"], P + "D644.K2": ["refers_to " + P + "D621.K1"]}
        report = (tmp / f"a4_report_{name}.txt").read_text(encoding="utf-8")
        for title in ("Bảng chỉ thị", "Thay đổi", "Cờ cạnh đứt", "Tập ảnh hưởng", "Dòng bị bỏ qua", "A3 chưa xử lý", "Chưa phủ", "Chưa tính cạnh"):
            assert f"== {title}" in report, title
        # snapshot qua CLI ghi file đúng bằng hàm
        out_md = tmp / "snap.md"
        assert cli("snapshot", "--name", name, "--date", "2027-07-01", "--out", out_md)[0] == 0
        assert out_md.read_text(encoding="utf-8") == snapshot(run_dev(2), "2027-07-01") and b"\r" not in out_md.read_bytes()
        assert cli("snapshot", "--name", "khong_co", "--date", "2027-07-01")[0] not in (0, None)


def test_cli_doc_id_name_and_arg_counts():
    with sandbox() as tmp:
        assert cli("apply", "--base", SAMPLE_FILE, "--amend", dev(1), "--doc-id", "LUAT-1", "--name", "n1")[0] == 0
        edge = json.loads((tmp / "a4_n1_amend_edges.jsonl").read_text(encoding="utf-8"))
        assert edge["s"] == "LUAT-1"
        assert cli("apply", "--base", SAMPLE_FILE, "--amend", dev(1), "--amend", dev(2), "--doc-id", "only-one")[0] == 1
    with sandbox() as tmp:
        assert cli("apply", "--base", SAMPLE_FILE, "--amend", dev(1), "--amend", dev(2))[0] == 0
        assert (tmp / f"a4_{DEV_FILES[1]}+{DEV_FILES[2]}_versions.jsonl").exists()


def test_base_files_are_not_modified():
    paths = [IN_DIR / f"{k}_{STEM}.jsonl" for k in ("a1_triples", "a2_edges", "a2_refs", "a3_exceptions")] + [SAMPLE_FILE]
    before = {p: p.read_bytes() for p in paths}
    for n in DEV_FILES:
        run_dev(n)
    with sandbox():
        cli("apply", "--base", SAMPLE_FILE, "--amend", dev(4))
    assert {p: p.read_bytes() for p in paths} == before


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
