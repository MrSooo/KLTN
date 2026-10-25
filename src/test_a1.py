"""Chặng 3: kiểm tra đầu ra của a1_parse trên file mẫu rồi file đầy đủ.

Chạy: python -I src/test_a1.py   (các hàm test_* cũng chạy được bằng pytest nếu có cài)
"""
import collections
import functools
import json
import re
import sys
import tempfile
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import a1_parse as a1

SAMPLE_FILE = a1.ROOT / "data" / "sample" / "blds2015_5dieu.md"
FULL_FILE = a1.ROOT / "data" / "raw" / "blds2015_p4.md"
FILES = [("mẫu", SAMPLE_FILE), ("đầy đủ", FULL_FILE)]  # luôn mẫu trước

# Số đơn vị và số triples để đối chiếu (đã đếm lại độc lập bằng grep/awk, không qua parser).
REFERENCE = {SAMPLE_FILE: (35, 176), FULL_FILE: (215, 1173)}  # p4: 1099 + 54 dòng chuong của Điều + 4 Chương x 5 dòng

# Số (Khoản, Điểm) của từng Điều trong 5 điều mẫu, đếm trực tiếp từ file mẫu.
SAMPLE_TABLE = {"621": (2, 4), "626": (5, 0), "644": (2, 2), "650": (2, 7), "651": (3, 3)}

PREDICATES = {"type", "number", "heading", "chuong", "text", "version", "source_line"}  # không có effective_from


@functools.cache
def load(path):
    result, parsed = a1.load_parsed(path)
    assert not parsed.errors, f"{path.name}: lỗi parse {parsed.errors}"
    return result, parsed


def test_ids_unique():
    for name, path in FILES:
        ids = [u.id for u in load(path)[1].units]
        dup = [i for i, n in collections.Counter(ids).items() if n > 1]
        assert not dup, f"file {name}: mã trùng {dup}"
        assert not any("đ" in i for i in ids), f"file {name}: mã còn chữ đ"


def test_dd_does_not_collide_with_d():
    md = ("### Điều 1\\. A\n**1\\.** K\n- **a)** a\n- **b)** b\n- **c)** c\n- **d)** d\n- **đ)** đ\n- **e)** e\n")
    parsed = a1.parse(a1.tokenize(md).tokens, [1])
    assert not parsed.errors, parsed.errors
    ids = [u.id for u in parsed.units if u.type == "diem"]
    assert len(ids) == len(set(ids)) == 6
    assert "BLDS2015.D1.K1.d" in ids and "BLDS2015.D1.K1.dd" in ids
    dd = next(u for u in parsed.units if u.id.endswith(".dd"))
    assert dd.number == "đ"  # number vẫn là đ


def test_sample_table():
    units = load(SAMPLE_FILE)[1].units
    got = {}
    for u in units:
        if u.type == "dieu":
            got[u.number] = [0, 0]
        elif u.type == "khoan":
            got[u.id.split(".")[1][1:]][0] += 1
        else:
            got[u.id.split(".")[1][1:]][1] += 1
    got = {k: tuple(v) for k, v in got.items()}
    assert got == SAMPLE_TABLE, f"(Khoản, Điểm) theo Điều: {got}, cần {SAMPLE_TABLE}"


def test_reference_counts():
    for name, path in FILES:
        parsed = load(path)[1]
        want_units, want_triples = REFERENCE[path]
        got = (len(parsed.units), len(a1.to_triples(parsed.units, parsed.chapters)))
        assert got == (want_units, want_triples), f"file {name}: (đơn vị, triples) = {got}, cần {(want_units, want_triples)}"


def test_no_markdown_residue():
    for name, path in FILES:
        for u in load(path)[1].units:
            for text in ([u.heading] if u.heading is not None else []) + u.parts:
                bad = set(text) & set("\\*#")
                assert not bad, f"file {name}: {u.id} còn {bad} trong {text[:60]!r}"


def raw_words(path):
    """Vế 1: từ của file gốc, không đi qua tokenize, clean_text hay parse."""
    words = collections.Counter()
    with open(path, encoding="utf-8", newline="") as f:
        for line in f.read().split("\n"):
            if line.startswith(("# ", "## ", "---")):
                continue
            words.update(re.findall(r"\w+", unicodedata.normalize("NFC", line)))
    return words


def unit_words(units):
    """Vế 2: từ của number, heading, parts của mọi đơn vị, cộng từ "Điều" cho mỗi Điều."""
    words = collections.Counter()
    for u in units:
        for text in [u.number] + ([u.heading] if u.heading is not None else []) + u.parts:
            words.update(re.findall(r"\w+", unicodedata.normalize("NFC", text)))
        if u.type == "dieu":
            words["Điều"] += 1
    return words


def test_words_conserved_vs_raw():
    """Multiset từ của file gốc == multiset từ của các đơn vị. Bắt từ bị mất, thừa hoặc đổi.

    Không bắt được đoạn xếp sai Khoản: chuyển cả đoạn từ Khoản này sang Khoản khác vẫn giữ nguyên multiset.
    """
    for name, path in FILES:
        raw, got = raw_words(path), unit_words(load(path)[1].units)
        assert raw == got, f"file {name}: thiếu {dict(raw - got)}, thừa {dict(got - raw)}"


def test_notes():
    parsed = load(FULL_FILE)[1]
    assert parsed.notes == ["Điều 643, Khoản 2, dòng 303"], parsed.notes
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "a1_notes.txt"
        a1.write_notes(parsed.notes, out)
        lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1 and lines[0].startswith("Điều 643, Khoản 2,"), lines
    # mỗi file nguồn một file notes: chạy file mẫu không ghi đè notes của file đầy đủ
    assert a1.notes_path(SAMPLE_FILE) != a1.notes_path(FULL_FILE)


def test_para_placement_in_full_file():
    """Đoạn chữ nằm sau Khoản (631 Khoản 3, 645 Khoản 1) và sau Điểm (643 Khoản 2) đều vào parts của Khoản.

    Nguồn chuẩn là chính file blds2015_p4.md (đã chốt), nên không đối chiếu thêm với bản luật gốc. Test này khoá
    kết quả của quy tắc nối para (para vào Khoản hiện tại); các chỗ 631 Khoản 3, 643 Khoản 2, 645 Khoản 1 đã
    được xem trực tiếp trên p4.md (dòng 198-200, 298-303, 322-326; +2 từ khi thêm tiêu đề Chương XXI ở dòng 3).
    """
    units = {u.id: u for u in load(FULL_FILE)[1].units}
    multi = {i: len(u.parts) for i, u in units.items() if u.type == "khoan" and len(u.parts) > 1}
    assert multi == {"BLDS2015.D631.K3": 2, "BLDS2015.D643.K2": 2, "BLDS2015.D645.K1": 3}, multi
    # Điểm cuối của 643 Khoản 2 không bị nhận đoạn chữ của Khoản
    assert len(units["BLDS2015.D643.K2.b"].parts) == 1


def test_chapters_of_full_file():
    """Review F-09: 4 Chương của p4, mỗi Điều thuộc đúng Chương của nó (đối chiếu dãy Điều của từng Chương trong BLDS 2015)."""
    parsed = load(FULL_FILE)[1]
    assert [(c.id, c.number, c.heading, c.source_line) for c in parsed.chapters] == [
        ("BLDS2015.CXXI", "XXI", "QUY ĐỊNH CHUNG", 3), ("BLDS2015.CXXII", "XXII", "THỪA KẾ THEO DI CHÚC", 124),
        ("BLDS2015.CXXIII", "XXIII", "THỪA KẾ THEO PHÁP LUẬT", 358), ("BLDS2015.CXXIV", "XXIV", "THANH TOÁN VÀ PHÂN CHIA DI SẢN", 413)]
    ranges = {"BLDS2015.CXXI": (609, 623), "BLDS2015.CXXII": (624, 648), "BLDS2015.CXXIII": (649, 655), "BLDS2015.CXXIV": (656, 662)}
    for u in parsed.units:
        if u.type == "dieu":
            lo, hi = ranges[u.chuong]
            assert lo <= int(u.number) <= hi, (u.id, u.chuong)
        else:
            assert u.chuong is None, u.id
    assert load(SAMPLE_FILE)[1].chapters == ()  # file mẫu không có Chương: Điều là gốc
    # triples: Chương xen vào ngay trước Điều đầu tiên của nó
    subjects = list(dict.fromkeys(s for s, _, _ in a1.to_triples(parsed.units, parsed.chapters)))
    assert subjects[:2] == ["BLDS2015.CXXI", "BLDS2015.D609"] and subjects.index("BLDS2015.CXXII") == subjects.index("BLDS2015.D624") - 1


def test_dieu_before_first_chapter_and_repeated_chapter_are_errors():
    text = "### Điều 1\\. A\n\n## Chương I – MỘT\n\n### Điều 2\\. B\n\n## Chương I – LẶP\n"
    parsed = a1.parse(a1.tokenize(text).tokens, [1, 2])
    assert [e.reason for e in parsed.errors] == ["Chương I lặp", "Điều 1 đứng trước Chương đầu tiên"], parsed.errors


def test_jsonl_written_correctly():
    for name, path in FILES:
        parsed = load(path)[1]
        triples = a1.to_triples(parsed.units)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "t.jsonl"
            a1.write_triples(triples, out)
            raw = out.read_bytes()
        assert not raw.startswith(b"\xef\xbb\xbf"), "có BOM"
        assert b"\\u" not in raw, "còn escape \\u (ensure_ascii phải là False)"
        assert b"\r" not in raw
        rows = [json.loads(line) for line in raw.decode("utf-8").split("\n") if line]
        assert all(list(r) == ["s", "p", "o"] for r in rows), f"file {name}: sai khóa"
        assert [(r["s"], r["p"], r["o"]) for r in rows] == triples, f"file {name}: đọc lại không khớp"
        assert {r["p"] for r in rows} <= PREDICATES, {r["p"] for r in rows} - PREDICATES

        by_s = collections.defaultdict(list)
        for r in rows:
            by_s[r["s"]].append(r)
        assert len(by_s) == len(parsed.units)
        for u in parsed.units:
            preds = [r["p"] for r in by_s[u.id]]
            assert len(preds) == len(set(preds)), f"{u.id}: predicate lặp"
            assert ("heading" in preds) == (u.type == "dieu"), f"{u.id}: heading"
            assert ("chuong" in preds) == (u.type == "dieu" and bool(parsed.chapters)), f"{u.id}: chuong"
            assert ("text" in preds) == bool(u.parts), f"{u.id}: text"
            o = {r["p"]: r["o"] for r in by_s[u.id]}
            assert o["version"] == 1 and isinstance(o["version"], int)
            assert o["source_line"] == u.source_line and isinstance(o["source_line"], int)
            assert o["number"] == u.number and o["type"] == u.type
            if "text" in o:
                assert o["text"] == "\n".join(u.parts)


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
            except SystemExit as e:  # load_parsed thoát khi file có lỗi; chi tiết đã in ở stderr
                failed += 1
                print("FAIL", fn_name, "-> load_parsed thoát", repr(e.code), "(xem stderr)")
            except Exception as e:
                failed += 1
                print("FAIL", fn_name, "->", type(e).__name__, e)
    print("tổng test lỗi:", failed)
    return failed


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(1 if main() else 0)
