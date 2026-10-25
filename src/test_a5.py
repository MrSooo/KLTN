"""A5: kiểm tra bốn phép kiểm (1-3 trên A1-A3, 4 trên A4 khi có --versions) bằng dữ liệu dựng tay có bơm lỗi, rồi trên file thật.

Chạy: python -I src/test_a5.py   (các hàm test_* cũng chạy được bằng pytest nếu có cài)
Chạy a5_checks.py cho cả hai file trước (python -I src/a5_checks.py <file md>), test_reports_on_disk đọc báo cáo đã ghi.
Bước 4 (4a-4f): chạy a4_versions.py apply cho dev01+dev02, dev04_bo_sung (mẫu) và dev01_full (p4), rồi a5_checks.py <md> --versions
<file> cho từng bộ; test_versions_on_disk đọc file versions, test_reports_on_disk đọc báo cáo bước 4 đã ghi (xem VERSIONS_ON_DISK).
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
import a5_checks as a5

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_FILE = ROOT / "data" / "sample" / "blds2015_5dieu.md"
FULL_FILE = ROOT / "data" / "raw" / "blds2015_p4.md"
FILES = [("mẫu", SAMPLE_FILE), ("đầy đủ", FULL_FILE)]  # luôn mẫu trước
D, K, A = "X.D1", "X.D1.K1", "X.D1.K1.a"

# Số kỳ vọng đếm độc lập với a5_checks: type và part_of bằng grep trên file jsonl, Điều bằng "### Điều" trong md.
UNITS = {SAMPLE_FILE: 35, FULL_FILE: 215}   # Điều + Khoản + Điểm
DIEU = {SAMPLE_FILE: 5, FULL_FILE: 54}
CHUONG = {SAMPLE_FILE: 0, FULL_FILE: 4}     # review F-09: p4 có 4 tiêu đề "## Chương"
PART_OF = {SAMPLE_FILE: 30, FULL_FILE: 161 + 54}  # p4: Khoản/Điểm + mỗi Điều một part_of tới Chương
POOLED = {SAMPLE_FILE: 60 + 3 + 1, FULL_FILE: 430 + 25 + 4}  # a2_edges + a2_refs + a3_exceptions, số đã ghi ở A2/A3


def rows(*triples):
    """[(số dòng, dòng JSON)] từ các bộ (s, p, o) hoặc (s, p, o, evidence)."""
    return [(i, {"s": t[0], "p": t[1], "o": t[2], **({"evidence": t[3]} if len(t) > 3 else {})}) for i, t in enumerate(triples, 1)]


def mini_triples(*extra):
    """Ba đơn vị Điều > Khoản > Điểm, mỗi đơn vị một dòng type và một dòng number."""
    base = [(D, "type", "dieu"), (D, "number", "1"), (D, "heading", "Tên"),
            (K, "type", "khoan"), (K, "number", "1"),
            (A, "type", "diem"), (A, "number", "a")]
    return rows(*base, *extra)


def mini_edges(*extra):
    return rows((D, "contains", K), (K, "part_of", D), (K, "contains", A), (A, "part_of", K), *extra)


EXPECT = a5.Expect(units=3, dieu=1)


def codes(triples, expect=EXPECT):
    checks, _ = a5.check_codes(triples, expect)
    return {c.id: c for c in checks}


def parents(triples, edges, expect=EXPECT):
    _, unit_types = a5.check_codes(triples, expect)
    dieu_chuong = {r["s"]: r["o"] for _, r in triples if r["p"] == "chuong"}
    return {c.id: c for c in a5.check_parents(unit_types, edges, expect, dieu_chuong)}


def bad_ids(by_id):
    return sorted(i for i, c in by_id.items() if c.problems)


# ---- bước 1 ----

def test_mini_clean():
    by_id = codes(mini_triples())
    assert bad_ids(by_id) == [], by_id
    assert bad_ids(parents(mini_triples(), mini_edges())) == []
    assert not a5.check_duplicate_edges([("a2_edges", mini_edges())]).problems


def test_step1_duplicate_type_same_value():
    by_id = codes(mini_triples((K, "type", "khoan")))
    assert bad_ids(by_id) == ["1c", "1d"], bad_ids(by_id)
    assert by_id["1c"].problems == ["X.D1.K1: 2 dòng type (khoan, khoan)"]
    assert "(X.D1.K1, type) lặp ở dòng 4, 8" in by_id["1d"].problems[0]
    assert by_id["1a"].summary.startswith("3,")  # đếm theo s, không theo số dòng type


def test_step1_duplicate_type_other_value():
    by_id = codes(mini_triples((K, "type", "diem")))
    assert bad_ids(by_id) == ["1c", "1d"] and "khoan, diem" in by_id["1c"].problems[0]


def test_step1_duplicate_heading_is_caught():
    by_id = codes(mini_triples((D, "heading", "Tên khác")))
    assert bad_ids(by_id) == ["1d"], bad_ids(by_id)
    assert by_id["1d"].problems == ["(X.D1, heading) lặp ở dòng 3, 8"]


def test_step1_duplicate_pair_with_same_object_is_caught():
    assert bad_ids(codes(mini_triples((A, "number", "a")))) == ["1d"]


def test_step1_unit_without_type_row():
    by_id = codes(mini_triples(("X.D1.K2", "number", "2")))
    assert bad_ids(by_id) == ["1c"] and by_id["1c"].problems == ["X.D1.K2: 0 dòng type"]
    assert by_id["1a"].summary.startswith("3,")  # chỉ tính s có dòng type


def test_step1_wrong_unit_and_dieu_counts():
    assert bad_ids(codes(mini_triples(), a5.Expect(units=4, dieu=1))) == ["1a"]
    assert bad_ids(codes(mini_triples(), a5.Expect(units=3, dieu=2))) == ["1b"]
    assert bad_ids(codes(mini_triples()[:-2])) == ["1a"]  # mất Điểm cuối


# ---- bước 2 ----

def test_step2_dieu_with_parent():
    by_id = parents(mini_triples(), mini_edges((D, "part_of", "X")))
    assert "2a" in bad_ids(by_id) and by_id["2a"].problems == ["X.D1: Điều có 1 part_of (X), cần 0 (văn bản không có Chương)"]


def test_step2_chapters():
    """Review F-09: văn bản có Chương thì Điều có đúng một part_of tới Chương ghi ở dòng chuong; Chương không có cha."""
    C = "X.CI"
    triples = mini_triples((C, "type", "chuong"), (C, "number", "I"), (D, "chuong", C))
    expect = a5.Expect(units=3, dieu=1, chuong=1)
    good = mini_edges((C, "contains", D), (D, "part_of", C))
    assert bad_ids(parents(triples, good, expect)) == []
    assert codes(triples, expect)["1e"].problems == [] and codes(triples)["1e"].problems == ["có 1 Chương, cần 0"]
    by_id = parents(triples, mini_edges(), expect)  # thiếu cạnh Điều-Chương
    assert by_id["2a"].problems == ["X.D1: Điều có 0 part_of, cần 1 (văn bản có Chương)"], by_id["2a"].problems
    wrong = [(i, r) for i, r in triples if r["p"] != "chuong"] + rows((D, "chuong", "X.CII"))
    assert any("cha theo mã là X.CII" in p for p in parents(wrong, good, expect)["2c"].problems)
    to_khoan = mini_edges((K, "contains", D), (D, "part_of", K))
    assert any("cần chuong" in p for p in parents(rows(*[(r["s"], r["p"], r["o"]) for _, r in triples if r["p"] != "chuong"],
                                                         (D, "chuong", K)), to_khoan, expect)["2f"].problems)
    chapter_parent = good + rows((C, "part_of", D))
    assert any("là Chương nhưng có part_of" in p for p in parents(triples, chapter_parent, expect)["2a"].problems)


def test_step2_khoan_without_parent():
    edges = rows((D, "contains", K), (K, "contains", A), (A, "part_of", K))
    by_id = parents(mini_triples(), edges)
    assert by_id["2b"].problems == ["X.D1.K1: 0 part_of"]


def test_step2_two_parents():
    by_id = parents(mini_triples(), mini_edges((A, "part_of", D)))
    assert "2b" in bad_ids(by_id) and by_id["2b"].problems == ["X.D1.K1.a: 2 part_of (X.D1.K1, X.D1)"]
    assert "2c" in bad_ids(by_id)  # cạnh part_of → X.D1 sai theo mã


def test_step2_parent_not_last_segment_dropped():
    edges = rows((D, "contains", K), (K, "part_of", D), (D, "contains", A), (A, "part_of", D))
    by_id = parents(mini_triples(), edges)
    assert by_id["2c"].problems == ["dòng 4: X.D1.K1.a part_of X.D1, cha theo mã là X.D1.K1"]
    assert "2d" not in bad_ids(by_id)  # đối xứng vẫn đúng: chỉ cha sai


def test_step2_parent_type_row_missing():
    """Bỏ dòng type của Điều: cha của Khoản không còn là đơn vị, chỉ 2f đỏ."""
    triples = [(i, r) for i, r in mini_triples() if not (r["s"] == D and r["p"] == "type")]
    by_id = parents(triples, mini_edges(), a5.Expect(units=2, dieu=0))
    assert bad_ids(by_id) == ["2f"], bad_ids(by_id)
    assert by_id["2f"].problems == ["X.D1.K1: cha X.D1 không phải đơn vị"]


def test_step2_diem_directly_under_dieu():
    """Điểm X.D1.a part_of thẳng tới Điều X.D1: mã đúng theo quy tắc cắt đoạn cuối nên 2c xanh, nhưng sai bậc nên 2f đỏ."""
    direct = "X.D1.a"
    triples = rows((D, "type", "dieu"), (direct, "type", "diem"))
    edges = rows((D, "contains", direct), (direct, "part_of", D))
    by_id = parents(triples, edges, a5.Expect(units=2, dieu=1))
    assert bad_ids(by_id) == ["2f"], bad_ids(by_id)
    assert not by_id["2c"].problems
    assert by_id["2f"].problems == ["X.D1.a: cha X.D1 là dieu, cần khoan"]


def test_step2_khoan_under_khoan_wrong_level():
    triples = rows((D, "type", "dieu"), (K, "type", "khoan"), ("X.D1.K1.K2", "type", "khoan"))
    edges = rows((D, "contains", K), (K, "part_of", D), (K, "contains", "X.D1.K1.K2"), ("X.D1.K1.K2", "part_of", K))
    assert parents(triples, edges, a5.Expect(units=3, dieu=1))["2f"].problems == ["X.D1.K1.K2: cha X.D1.K1 là khoan, cần dieu"]


def test_step2_asymmetry_both_directions():
    no_contains = rows((D, "contains", K), (K, "part_of", D), (A, "part_of", K))
    assert parents(mini_triples(), no_contains)["2d"].problems == ["part_of X.D1.K1.a → X.D1.K1 không có contains X.D1.K1 → X.D1.K1.a"]
    no_part_of = rows((D, "contains", K), (K, "part_of", D), (K, "contains", A), (A, "part_of", K), (D, "contains", A))
    assert parents(mini_triples(), no_part_of)["2d"].problems == ["contains X.D1 → X.D1.K1.a không có part_of X.D1.K1.a → X.D1"]


def test_step2_part_of_count():
    by_id = parents(mini_triples(), mini_edges()[:-1])  # bỏ part_of cuối
    assert bad_ids(by_id) == ["2b", "2d", "2e"], bad_ids(by_id)
    assert by_id["2e"].problems == ["có 1 part_of, cần 2"]


def test_step2_unknown_type_and_part_of_from_non_unit():
    triples = rows((D, "type", "dieu"), (K, "type", "muc"))
    by_id = parents(triples, rows((K, "part_of", D), ("X.D9.K1", "part_of", "X.D9")), a5.Expect(units=2, dieu=1))
    assert "type 'muc' không phải" in by_id["2b"].problems[0]
    assert "X.D9.K1: có part_of nhưng không có dòng type" in by_id["2b"].problems[1]


# ---- bước 3 ----

def test_step3_duplicate_within_file_different_evidence():
    ref = rows((K, "refers_to", D, "Điều 1"), (K, "refers_to", D, "Điều này"), (A, "refers_to", D, "x"))
    c = a5.check_duplicate_edges([("a2_refs", ref)])
    assert len(c.problems) == 1
    assert c.problems[0] == f'{K}\trefers_to\t{D}\t2 lần\ta2_refs:1 "Điều 1"; a2_refs:2 "Điều này"'
    assert c.summary == "3 bộ ba, 2 khác nhau, 1 bị lặp"


def test_step3_duplicate_across_files_is_pooled():
    c = a5.check_duplicate_edges([("a2_refs", rows((K, "refers_to", D, "a"))), ("a3_exceptions", rows((K, "refers_to", D, "b")))])
    assert len(c.problems) == 1 and "a2_refs:1" in c.problems[0] and "a3_exceptions:1" in c.problems[0]


def test_step3_different_predicate_or_direction_is_not_duplicate():
    c = a5.check_duplicate_edges([("a2_edges", rows((K, "refers_to", D), (K, "exception_of", D), (D, "refers_to", K)))])
    assert not c.problems


# ---- bước 4 ----

# Nội dung A1 của ba đơn vị mini. type/number/heading khớp mini_triples; text chỉ có ở content_triples (cho các test 4e).
CONTENT = {D: {"type": "dieu", "number": "1", "heading": "Tên", "text": None},
           K: {"type": "khoan", "number": "1", "heading": None, "text": "Nội dung khoản"},
           A: {"type": "diem", "number": "a", "heading": None, "text": "Nội dung điểm"}}


def vrows(*specs):
    """[(số dòng, dòng versions)] từ các bộ (id, version, previous_version, effective_from, effective_to[, ghi đè]).

    Trường nội dung (type/number/heading/text) tự lấy từ CONTENT theo id, mã lạ thì None; phần tử thứ 6 (dict) ghi đè từng trường.
    """
    out = []
    for i, spec in enumerate(specs, 1):
        row = dict(zip(a5.VERSION_KEYS, spec[:5]))
        row.update({f: None for f in a5.CONTENT_FIELDS})
        row.update(CONTENT.get(row["id"], {}))
        row["source_doc"] = BASE_DOC_ID  # 4f chỉ cần version 1 của mã A1 có chung một source_doc khác null
        row.update(spec[5] if len(spec) > 5 else {})
        out.append((i, row))
    return out


BASE_DOC_ID, BASE_DATE = "X", "2017-01-01"


def mini_versions(*extra):
    """D và A một version; K hai version, version 1 đóng đúng ngày version 2 mở (nửa khoảng nên chạm nhau là hợp lệ).
    Version 1 bắt đầu từ ngày hiệu lực gốc BASE_DATE như A4 ghi."""
    return vrows((D, 1, None, BASE_DATE, None), (K, 1, None, BASE_DATE, "2027-01-01"),
                 (K, 2, 1, "2027-01-01", None, {"text": "Nội dung khoản sau sửa đổi"}), (A, 1, None, BASE_DATE, None), *extra)


def test_step4f_base_dates():
    assert a5.check_base_dates({D, K, A}, mini_versions()).problems == []
    # mã chỉ có trong versions (thêm bởi sửa đổi) là "dòng khác": phải bắt đầu sau ngày gốc
    assert a5.check_base_dates({D, K, A}, mini_versions(("X.D1a", 1, None, "2027-01-01", None))).problems == []
    late = a5.check_base_dates({D, K, A}, mini_versions(("X.D1a", 1, None, BASE_DATE, None))).problems
    assert late == [f"X.D1a version 1: effective_from '{BASE_DATE}' không sau ngày hiệu lực gốc {BASE_DATE}"], late
    old = vrows((D, 1, None, None, None), (K, 1, None, BASE_DATE, None), (A, 1, None, BASE_DATE, None))
    problems = a5.check_base_dates({D, K, A}, old).problems
    assert any("effective_from null" in p for p in problems) and any("không cùng" in p for p in problems), problems
    no_doc = vrows(*[(c, 1, None, BASE_DATE, None, {"source_doc": None}) for c in (D, K, A)])
    assert any("source_doc null" in p for p in a5.check_base_dates({D, K, A}, no_doc).problems)


def content_triples():
    """mini_triples kèm text cho K và A, nối ở cuối nên số dòng của mini_triples không đổi."""
    return mini_triples((K, "text", CONTENT[K]["text"]), (A, "text", CONTENT[A]["text"]))


def versions_checks(rows_, a1_ids=(D, K, A)):
    return {c.id: c for c in a5.check_versions(set(a1_ids), rows_)}


def test_step4_clean_and_new_unit_not_in_a1_is_fine():
    assert bad_ids(versions_checks(mini_versions())) == []
    # đơn vị chỉ có trong versions (văn bản sửa đổi thêm) có version 1 mang effective_from, không bị báo
    assert bad_ids(versions_checks(mini_versions(("X.D1a", 1, None, "2027-01-01", None)))) == []


def test_step4a_duplicate_pair():
    by_id = versions_checks(mini_versions((K, 2, 1, "2027-01-01", None)))
    assert by_id["4a"].problems == ["(X.D1.K1, version 2) lặp ở dòng 3, 5"], by_id["4a"].problems


def test_step4a_version_jump():
    rows_ = vrows((D, 1, None, None, None), (K, 1, None, None, "2027-01-01"), (K, 3, 2, "2027-01-01", None), (A, 1, None, None, None))
    by_id = versions_checks(rows_)
    assert by_id["4a"].problems == ["X.D1.K1: các version [1, 3], cần [1, 2]"], by_id["4a"].problems


def test_step4a_version_not_starting_at_1_and_not_int():
    assert versions_checks(vrows((D, 2, 1, "2027-01-01", None)), [D])["4a"].problems == ["X.D1: các version [2], cần [1]"]
    assert "version '1' không phải số nguyên" in versions_checks(vrows((D, "1", None, None, None)), [D])["4a"].problems[0]


def test_step4b_previous_version_wrong():
    by_id = versions_checks(mini_versions((D, 2, 5, "2027-01-01", None)))
    assert by_id["4b"].problems == ["dòng 5: X.D1 version 2: previous_version 5, cần 1"], by_id["4b"].problems
    by_id = versions_checks(vrows((D, 1, 0, None, None)), [D])
    assert by_id["4b"].problems == ["dòng 1: X.D1 version 1: previous_version 0, cần None"], by_id["4b"].problems
    by_id = versions_checks(vrows((D, 1, None, None, "2027-01-01"), (D, 2, None, "2027-01-01", None)), [D])  # version 2 không trỏ về 1
    assert by_id["4b"].problems == ["dòng 2: X.D1 version 2: previous_version None, cần 1"]


def test_step4c_overlap():
    rows_ = vrows((K, 1, None, None, "2027-03-01"), (K, 2, 1, "2027-01-01", None))
    assert versions_checks(rows_, [K])["4c"].problems == ["X.D1.K1: version 1 hết hiệu lực 2027-03-01 sau khi version 2 bắt đầu 2027-01-01"]
    assert bad_ids(versions_checks(rows_, [K])) == ["4c"]  # 4a, 4b, 4d vẫn xanh


def test_step4c_gap_between_versions_is_not_overlap():
    rows_ = vrows((K, 1, None, None, "2027-01-01"), (K, 2, 1, "2027-06-01", None))
    assert bad_ids(versions_checks(rows_, [K])) == []  # chỉ cấm chồng nhau; to < from là hở thời gian, spec không cấm


def test_step4c_previous_version_has_no_end():
    rows_ = vrows((K, 1, None, None, None), (K, 2, 1, "2027-01-01", None))
    assert versions_checks(rows_, [K])["4c"].problems == ["X.D1.K1: version 1 không có effective_to nhưng đã có version 2"]


def test_step4c_successor_has_no_start():
    rows_ = vrows((K, 1, None, None, "2027-01-01"), (K, 2, 1, None, None))
    assert versions_checks(rows_, [K])["4c"].problems == ["X.D1.K1: version 2 không có effective_from"]


def test_step4c_empty_interval_and_bad_date():
    same = vrows((K, 1, None, None, None), (K, 2, 1, "2027-01-01", "2027-01-01"))
    assert "X.D1.K1 version 2: khoảng hiệu lực rỗng [2027-01-01, 2027-01-01)" in versions_checks(same, [K])["4c"].problems
    reversed_ = vrows((K, 1, None, "2027-05-01", "2027-02-01"))
    assert versions_checks(reversed_, [K])["4c"].problems == ["X.D1.K1 version 1: khoảng hiệu lực rỗng [2027-05-01, 2027-02-01)"]
    for bad in ("2027-13-01", "2027/01/01", "20270101", 20270101):
        assert versions_checks(vrows((K, 1, None, None, bad)), [K])["4c"].problems == [f"X.D1.K1 version 1 effective_to: ngày {bad!r} không hợp lệ"], bad


def test_step4d_a1_unit_missing_from_versions():
    by_id = versions_checks(mini_versions(), [D, K, A, "X.D1.K2"])
    assert by_id["4d"].problems == ["X.D1.K2: có trong A1 nhưng không còn trong versions"]
    assert bad_ids(by_id) == ["4d"]
    # mất cả id, không chỉ một version: bỏ mọi dòng của A
    assert versions_checks(mini_versions()[:-1])["4d"].problems == ["X.D1.K1.a: có trong A1 nhưng không còn trong versions"]


def content_check(version_rows, a1_rows=None):
    return a5.check_version1_content(content_triples() if a1_rows is None else a1_rows, version_rows)


def test_step4e_version1_matches_a1():
    c = content_check(mini_versions())
    assert c.id == "4e" and c.problems == [], c.problems
    assert c.summary == "9 trường ở 3 dòng version 1"  # D: type/number/heading; K: type/number/text; A: type/number/text; version 2 không tính
    assert not set(a5.CONTENT_FIELDS) & set(a5.VERSION_KEYS)  # trường nội dung không bắt buộc trong file versions


def test_step4e_text_changed_in_version1_only_4e_red():
    rows_ = vrows((D, 1, None, None, None), (K, 1, None, None, "2027-01-01", {"text": "Nội dung khoản đã sửa"}),
                  (K, 2, 1, "2027-01-01", None, {"text": "Nội dung khoản sau sửa đổi"}), (A, 1, None, None, None))
    assert bad_ids(versions_checks(rows_)) == []  # 4a-4d xanh, version 2 giữ nguyên
    assert content_check(rows_).problems == ["X.D1.K1: text A1 'Nội dung khoản' khác version 1 'Nội dung khoản đã sửa'"]


def test_step4e_heading_changed_in_version1():
    rows_ = mini_versions()
    rows_[0][1]["heading"] = "Tên khác"
    assert bad_ids(versions_checks(rows_)) == []
    assert content_check(rows_).problems == ["X.D1: heading A1 'Tên' khác version 1 'Tên khác'"]


def test_step4e_type_number_and_missing_value():
    rows_ = vrows((D, 1, None, None, None), (K, 1, None, None, None, {"type": "diem", "number": "2"}), (A, 1, None, None, None))
    del rows_[1][1]["text"]  # thiếu khoá: tính là None
    assert content_check(rows_).problems == ["X.D1.K1: type A1 'khoan' khác version 1 'diem'", "X.D1.K1: number A1 '1' khác version 1 '2'",
                                             "X.D1.K1: text A1 'Nội dung khoản' khác version 1 'None'"]


def test_step4e_skips_fields_and_ids_missing_on_one_side():
    # A1 không có dòng text cho K và A: version có text cũng không bị so
    assert content_check(mini_versions(), mini_triples()).problems == []
    # mã chỉ có trong versions (văn bản sửa đổi thêm) và mã A1 không có trong versions (4d lo): đều bỏ qua
    only_versions = mini_versions(("X.D1a", 1, None, "2027-01-01", None, {"type": "dieu", "number": "1a", "heading": "Mới"}))
    assert content_check(only_versions).problems == []
    assert content_check(mini_versions()[:-1]).problems == []  # bỏ dòng A khỏi versions
    # A1 có heading mà version 1 để None là khác, kể cả khi A1 không có text
    rows_ = mini_versions()
    rows_[0][1]["heading"] = None
    assert content_check(rows_, mini_triples()).problems == ["X.D1: heading A1 'Tên' khác version 1 'None'"]


def test_step4e_exact_equality_no_whitespace_normalisation():
    for changed in ("Nội dung khoản ", " Nội dung khoản", "Nội  dung khoản", "Nội dung\nkhoản"):
        rows_ = vrows((K, 1, None, None, None, {"text": changed}))
        assert len(content_check(rows_).problems) == 1, repr(changed)


def test_step4e_prints_first_60_chars():
    a1_rows = rows((K, "text", "a" * 100))
    rows_ = vrows((K, 1, None, None, None, {"text": "a" * 99 + "b"}))
    assert content_check(rows_, a1_rows).problems == [f"X.D1.K1: text A1 '{'a' * 60}' khác version 1 '{'a' * 60}'"]


# ---- run / main ----

class Env:
    """Đổi đường dẫn vào/ra của a5 sang thư mục tạm, và bảng EXPECTED sang stem "t"."""

    def __init__(self, tmp, triples, edges, refs=(), exceptions=(), versions=None):
        self.tmp = Path(tmp)
        self.files = {"t1": triples, "te": edges, "tr": refs, "tx": exceptions}
        if versions is not None:
            self.files["v"] = versions

    def __enter__(self):
        for key, rs in self.files.items():
            with open(self.tmp / f"{key}.jsonl", "w", encoding="utf-8") as f:
                for _, r in rs:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
        self.saved = (a2.triples_path, a2.edges_path, a2.refs_path, a3.exceptions_path, a5.report_path, dict(a5.EXPECTED))
        a2.triples_path, a2.edges_path, a2.refs_path = (lambda s, k=k: self.tmp / f"{k}.jsonl" for k in ("t1", "te", "tr"))
        a3.exceptions_path = lambda s: self.tmp / "tx.jsonl"
        a5.report_path = lambda s, v=None: self.tmp / "report.txt"
        a5.EXPECTED["t"] = EXPECT
        return self

    def __exit__(self, *exc):
        a2.triples_path, a2.edges_path, a2.refs_path, a3.exceptions_path, a5.report_path, expected = self.saved
        a5.EXPECTED.clear()
        a5.EXPECTED.update(expected)

    def run(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = a5.main(["x/t.md", *args])
        return code, out.getvalue(), (self.tmp / "report.txt").read_text(encoding="utf-8")


def test_run_clean_exit_0_and_report_written():
    with tempfile.TemporaryDirectory() as tmp, Env(tmp, mini_triples(), mini_edges()) as env:
        code, out, report = env.run()
    assert code == 0 and out.startswith(report) and report.endswith("\nKẾT LUẬN: ĐẠT\n")
    assert report.count("-> ĐẠT") == 12 and "không trùng" not in report  # 1a-1e (5) + 2a-2f (6) + 3 (1)
    assert "[4a]" not in report  # không --versions thì không có bước 4


def test_run_violation_exit_1_all_three_steps_still_run():
    with tempfile.TemporaryDirectory() as tmp, Env(tmp, mini_triples((D, "heading", "Tên khác")), mini_edges((D, "part_of", "X")),
                                                    refs=rows((K, "refers_to", D), (K, "refers_to", D))) as env:
        code, _, report = env.run()
    assert code == 1
    assert "[1d]" in report and "-> KHÔNG ĐẠT (1)" in report                 # bước 1 báo lỗi
    assert "[2a]" in report and "[2c]" in report                              # bước 2 vẫn chạy và báo lỗi
    assert "[3]" in report and "2 lần" in report                              # bước 3 vẫn chạy và thấy cạnh lặp
    assert "KẾT LUẬN: KHÔNG ĐẠT" in report


def test_run_only_duplicate_edges_exit_1():
    """Cạnh trùng là vi phạm như bước 1-2: bàn giao ghi 'không có cạnh trùng' là yêu cầu."""
    with tempfile.TemporaryDirectory() as tmp, Env(tmp, mini_triples(), mini_edges(), refs=rows((K, "refers_to", D, "a"), (K, "refers_to", D, "b"))) as env:
        code, _, report = env.run()
    assert code == 1
    assert report.count("-> KHÔNG ĐẠT") == 1 and "[3]" in report and "-> KHÔNG ĐẠT (1)" in report.split("[3]")[1]
    assert 'a2_refs:1 "a"; a2_refs:2 "b"' in report and report.endswith("\nKẾT LUẬN: KHÔNG ĐẠT (1 chỗ sai)\n")


def test_run_unknown_stem_exits_with_error_and_no_report():
    with tempfile.TemporaryDirectory() as tmp, Env(tmp, mini_triples(), mini_edges()) as env:
        try:
            a5.main(["x/khac.md"])
        except SystemExit as e:
            assert "LỖI" in str(e.code) and "'khac'" in str(e.code)
        else:
            raise AssertionError("stem lạ phải thoát với LỖI")
        assert not (env.tmp / "report.txt").exists()


def test_run_missing_file_and_bad_input_exit_with_error():
    with tempfile.TemporaryDirectory() as tmp, Env(tmp, mini_triples(), mini_edges()) as env:
        (env.tmp / "tr.jsonl").unlink()
        for expect_text in ("chưa có", "JSON hỏng", "thiếu khoá s/p/o"):
            try:
                a5.main(["x/t.md"])
            except SystemExit as e:
                assert "LỖI" in str(e.code) and expect_text in str(e.code), (expect_text, e.code)
            else:
                raise AssertionError(f"{expect_text}: phải thoát với LỖI")
            (env.tmp / "tr.jsonl").write_text('{"s": "a"' if expect_text == "chưa có" else '{"s": "a", "p": "b"}\n', encoding="utf-8")
        assert not (env.tmp / "report.txt").exists()


def test_report_path_naming():
    assert a5.report_path("a/b.md").name == "a5_report_b.txt"  # không --versions: tên cũ, báo cáo bước 1-3 không đổi
    assert a5.report_path("a/b.md", "d/a4_dev01+dev02_versions.jsonl").name == "a5_report_b_dev01+dev02.txt"
    assert a5.report_path("a/b.md", "d/other.jsonl").name == "a5_report_b_other.txt"


def test_run_with_versions_clean():
    with tempfile.TemporaryDirectory() as tmp, Env(tmp, mini_triples(), mini_edges(), versions=mini_versions()) as env:
        code, _, report = env.run("--versions", str(env.tmp / "v.jsonl"))
    assert code == 0 and report.endswith("\nKẾT LUẬN: ĐẠT\n")
    assert "== Bước 4: lớp phiên bản của A4 ==" in report and all(f"[{i}]" in report for i in ("4a", "4b", "4c", "4d", "4e", "4f"))
    assert report.count("-> ĐẠT") == 18  # 1a-1e (5) + 2a-2f (6) + 3 (1) + 4a-4f (6)
    assert "v.jsonl" in report.split("== Bước 1")[0]  # file versions có trong danh sách file đã kiểm


def test_run_with_versions_violation_exit_1():
    bad = mini_versions((K, 2, 1, "2027-01-01", None))  # (id, version) lặp
    with tempfile.TemporaryDirectory() as tmp, Env(tmp, mini_triples(), mini_edges(), versions=bad) as env:
        code, _, report = env.run("--versions", str(env.tmp / "v.jsonl"))
    assert code == 1 and report.count("-> KHÔNG ĐẠT") == 1 and "[4a]" in report.split("-> KHÔNG ĐẠT")[0].split("\n")[-1]
    assert report.endswith("\nKẾT LUẬN: KHÔNG ĐẠT (1 chỗ sai)\n")


def test_run_with_versions_content_changed_exit_1():
    changed = mini_versions()
    changed[0][1]["heading"] = "Tên khác"  # chỉ nội dung version 1 đổi, 4a-4d vẫn xanh
    with tempfile.TemporaryDirectory() as tmp, Env(tmp, mini_triples(), mini_edges(), versions=changed) as env:
        code, _, report = env.run("--versions", str(env.tmp / "v.jsonl"))
    assert code == 1 and report.count("-> KHÔNG ĐẠT") == 1
    assert "[4e] version 1 giữ nguyên nội dung A1: 9 trường ở 3 dòng version 1 -> KHÔNG ĐẠT (1)" in report or "-> KHÔNG ĐẠT (1)" in report.split("[4e]")[1]
    assert "    X.D1: heading A1 'Tên' khác version 1 'Tên khác'" in report


def test_run_with_versions_missing_file_and_missing_keys():
    with tempfile.TemporaryDirectory() as tmp, Env(tmp, mini_triples(), mini_edges()) as env:
        try:
            env.run("--versions", str(env.tmp / "khong_co.jsonl"))
        except SystemExit as e:
            assert "LỖI" in str(e.code) and "chưa có" in str(e.code)
        else:
            raise AssertionError("thiếu file versions phải thoát với LỖI")
        (env.tmp / "v.jsonl").write_text('{"id": "X.D1", "version": 1}\n', encoding="utf-8")
        try:
            env.run("--versions", str(env.tmp / "v.jsonl"))
        except SystemExit as e:
            assert "thiếu khoá id/version/previous_version/effective_from/effective_to" in str(e.code)
        else:
            raise AssertionError("dòng versions thiếu khoá phải thoát với LỖI")
        assert not (env.tmp / "report.txt").exists()


# ---- file thật ----

# Bộ (md gốc, tên bộ A4, số dòng versions đếm bằng wc -l). Chạy a4_versions.py apply cho từng bộ trước.
VERSIONS_ON_DISK = [(SAMPLE_FILE, "dev01+dev02", 37), (SAMPLE_FILE, "dev04_bo_sung", 40), (FULL_FILE, "dev01_full", 215)]


def versions_file(name):
    return a2.PROCESSED_DIR / f"a4_{name}_versions.jsonl"

def raw_lines(path):
    return path.read_text(encoding="utf-8").split("\n")


def test_files_on_disk():
    """Số kỳ vọng đếm độc lập: type/part_of bằng dòng thô của jsonl, Điều bằng '### Điều' trong md."""
    for label, md in FILES:
        triples, edges = a2.triples_path(md), a2.edges_path(md)
        assert sum(1 for l in raw_lines(triples) if '"p": "type"' in l) == UNITS[md] + CHUONG[md], label
        assert sum(1 for l in raw_lines(md) if l.startswith("### Điều")) == DIEU[md], label
        assert sum(1 for l in raw_lines(md) if l.startswith("## Chương")) == CHUONG[md], label
        assert sum(1 for l in raw_lines(edges) if '"p": "part_of"' in l) == PART_OF[md], label
        assert a5.EXPECTED[md.stem] == a5.Expect(UNITS[md], DIEU[md], CHUONG[md]), label  # bảng cứng khớp số đếm độc lập
        a1_rows = a5.load_rows(triples)
        checks, unit_types = a5.check_codes(a1_rows, a5.EXPECTED[md.stem])
        checks += a5.check_parents(unit_types, a5.load_rows(edges), a5.EXPECTED[md.stem],
                                   {r["s"]: r["o"] for _, r in a1_rows if r["p"] == "chuong"})
        assert [(c.id, c.problems) for c in checks if c.problems] == [], label
        assert len(unit_types) == UNITS[md] + CHUONG[md] and sum(1 for t in unit_types.values() if t == "dieu") == DIEU[md], label


def test_pooled_triples_on_disk():
    for label, md in FILES:
        sources = [(n, a5.load_rows(p(md))) for n, p in zip(a5.EDGE_SOURCES, (a2.edges_path, a2.refs_path, a3.exceptions_path))]
        c = a5.check_duplicate_edges(sources)
        total = sum(len(r) for _, r in sources)
        assert total == POOLED[md], (label, total)
        distinct = {(r["s"], r["p"], r["o"]) for _, rs in sources for _, r in rs}
        excess = sum(int(re.search(r"\t(\d+) lần\t", p).group(1)) - 1 for p in c.problems)
        assert excess == total - len(distinct), label  # số lần thừa của các bộ ba lặp = tổng trừ số bộ ba khác nhau


def test_versions_on_disk():
    for md, name, n_lines in VERSIONS_ON_DISK:
        path = versions_file(name)
        assert path.exists(), f"chưa có {path}; chạy python -I src/a4_versions.py apply cho bộ {name}"
        assert sum(1 for l in raw_lines(path) if l.strip()) == n_lines, name
        a1_rows, version_rows = a5.load_rows(a2.triples_path(md)), a5.load_rows(path, a5.VERSION_KEYS)
        _, unit_types = a5.check_codes(a1_rows, a5.EXPECTED[md.stem])
        versioned = {u for u, t in unit_types.items() if t in a5.TYPES}  # Chương không lập phiên bản
        checks = a5.check_versions(versioned, version_rows) + [a5.check_version1_content(a1_rows, version_rows),
                                                               a5.check_base_dates(versioned, version_rows)]
        assert [(c.id, c.problems) for c in checks if c.problems] == [], name
        assert checks[-2].id == "4e" and checks[-2].summary.endswith(f"ở {UNITS[md]} dòng version 1"), name  # so đủ mọi đơn vị A1, không rỗng
        assert len(versioned) == UNITS[md], name


def test_reports_on_disk():
    for label, md in FILES:
        path = a5.report_path(md)
        assert path.exists(), f"{label}: chưa có {path}; chạy python -I src/a5_checks.py {md}"
        text = path.read_text(encoding="utf-8")
        assert f"A5 báo cáo kiểm tra: {md.stem}" in text and "KẾT LUẬN: ĐẠT" in text, label
        assert "[2f]" in text, f"{label}: báo cáo cũ (chưa có 2f); chạy lại python -I src/a5_checks.py {md}"
        assert not re.search(r"[A-Za-z]:\\", text), label  # báo cáo không dính đường dẫn tuyệt đối của máy
        assert "[4a]" not in text, f"{label}: báo cáo bước 1-3 không được chứa bước 4 (bước 4 ghi file riêng)"
    for md, name, _ in VERSIONS_ON_DISK:
        path = a5.report_path(md, versions_file(name))
        assert path.exists(), f"{name}: chưa có {path}; chạy python -I src/a5_checks.py {md} --versions {versions_file(name)}"
        text = path.read_text(encoding="utf-8")
        assert f"A5 báo cáo kiểm tra: {md.stem}" in text and "[4d]" in text and "[4e]" in text and text.endswith("\nKẾT LUẬN: ĐẠT\n"), name
        assert f"data/processed/a4_{name}_versions.jsonl" in text, name  # đường dẫn tương đối, không dính đường dẫn máy


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
