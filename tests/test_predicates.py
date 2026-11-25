"""Test bước 1.6B (src/predicates.py): phép so chữ ký tham số và chữ nối "coi là" của names-2.1 và names-2.2 (A61).

Lần chạy mặc định dùng names-2.1 (`LOOSE` tắt); test bật `LOOSE` tạm thời để thử nhánh names-2.2 rồi trả lại như cũ.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import _harness  # noqa: E402
import predicates as P  # noqa: E402


def _with_loose(value, fn):
    old = P.LOOSE
    P.LOOSE = value
    try:
        fn()
    finally:
        P.LOOSE = old


def test_compatible_strict_names_2_1():
    def check():
        assert P.compatible(("E",), ("E",)) and P.compatible(("?",), ("W",))
        assert not P.compatible((), ("E",)), "names-2.1 đòi cùng số tham số"
        assert not P.compatible(("E",), ("E", "W"))
    _with_loose(False, check)


def test_compatible_subsequence_names_2_2():
    def check():
        assert P.compatible((), ("E",)), "chữ không nêu chủ thể vẫn là ứng viên (D42.K3 so với D48)"
        assert P.compatible(("E",), ("E", "W")) and P.compatible(("W",), ("E", "W")) and P.compatible(("?",), ("E", "W"))
        assert not P.compatible(("E",), ("W",)), "cùng độ dài thì vẫn so từng vị trí"
        assert not P.compatible(("E", "W"), ("W", "E")), "dãy con phải giữ thứ tự"
        assert not P.compatible(("C",), ("E", "W"))
    _with_loose(True, check)


def test_book_keeps_longest_signature():
    """Tên đã nhận () rồi (E) thì không nhận (W): sổ giữ chữ ký dài nhất, nên một tên không gom hai việc ngược chiều qua chữ không nêu chủ thể."""
    def check():
        words = [{"params": ()}, {"params": ("E",)}, {"params": ("W",)}]
        book = P.Book(words)
        book.add(0, "structural_change")
        book.add(1, "structural_change")
        assert book.name_params["structural_change"] == ("E",)
        try:
            book.add(2, "structural_change")
        except ValueError:
            return
        raise AssertionError("(W) không được nhận vào tên đã có chữ ký (E)")
    _with_loose(True, check)


def test_strip_copula():
    def check():
        assert P.strip_copula("coi là thay đổi cơ cấu, công nghệ") == "thay đổi cơ cấu, công nghệ"
        assert P.strip_copula("được coi là vì lý do kinh tế") == "vì lý do kinh tế"
        assert P.strip_copula("coi là") == "coi là", "không để chữ rỗng"
        assert P.strip_copula("thay đổi cơ cấu") == "thay đổi cơ cấu"
    _with_loose(True, check)
    _with_loose(False, lambda: P.strip_copula("coi là x") == "coi là x" or (_ for _ in ()).throw(AssertionError("names-2.1 giữ nguyên chữ")))


class _FakeRun:
    def __init__(self, words, names):
        self.words = words
        self.book = P.Book(words)
        old = P.LOOSE
        P.LOOSE = True
        try:
            for i, n in enumerate(names):
                if n:
                    self.book.add(i, n)
        finally:
            P.LOOSE = old


def test_merge_same_text_w_e_and_short_guard():
    """A61: cùng mặt chữ (>= 3 tiếng) khác tên thì gộp, kể cả khác loại chủ thể (W, E); tên giữ là tên xuất hiện nhiều nhất; chữ khác đã reuse tên bị
    gộp cũng chuyển theo; chữ ngắn ("tổ chức") không gộp."""
    w = lambda s, p, n=1: {"surface": s, "params": p, "n": n}  # noqa: E731
    words = [w("thành lập tổ chức nghề nghiệp", ("W",), 1), w("Thành lập tổ chức nghề nghiệp", ("E",), 3),
             w("lập tổ chức nghề nghiệp", ("W",)), w("tổ chức", ()), w("tổ chức", ("E",))]
    run = _FakeRun(words, ["join_occ_org_w", "establish_professional_organization", "join_occ_org_w", "organization", "stage_strike"])
    merged = P.merge_same_text(run)
    assert merged == [("establish_professional_organization", ["join_occ_org_w"])], merged
    assert [run.book.name_of[i] for i in range(3)] == ["establish_professional_organization"] * 3
    assert run.book.name_of[3] == "organization" and run.book.name_of[4] == "stage_strike", "chữ <= 2 tiếng không gộp"
    assert "join_occ_org_w" not in run.book.members and "join_occ_org_w" not in run.book.name_params


def test_merge_same_text_short_text_does_not_drag_other_surfaces():
    """A62: mặt chữ chung chỉ 3 tiếng ("hết thời hạn") thì chỉ chuyển đúng chữ đó; chữ khác mặt chữ đã dùng lại tên bị gộp giữ tên cũ."""
    w = lambda s, n=1: {"surface": s, "params": (), "n": n}  # noqa: E731
    words = [w("hết thời hạn", 3), w("hết thời hạn"), w("giấy phép lao động hết thời hạn")]
    run = _FakeRun(words, ["contract_expires", "work_permit_term_expires", "work_permit_term_expires"])
    assert P.merge_same_text(run) == [("contract_expires", ["work_permit_term_expires"])]
    assert [run.book.name_of[i] for i in range(3)] == ["contract_expires", "contract_expires", "work_permit_term_expires"]


def test_run_rounds_merge_flag():
    """Sổ vị từ 2.6 gọi run_rounds(merge=False) cho phần KU: không gộp (gộp ở đó có thể xoá một tên gốc); bước 1.6B gốc gộp khi bật GOP_CHU."""
    w = lambda s, p: {"surface": s, "params": p, "n": 1}  # noqa: E731
    old = P.GOP_CHU
    P.GOP_CHU = True
    try:
        for merge, want in ((False, None), (True, [("a_name", ["b_name"])])):
            run = _FakeRun([w("thành lập tổ chức nghề nghiệp", ("W",)), w("thành lập tổ chức nghề nghiệp", ("E",))], ["a_name", "b_name"])
            run.next_round = lambda: None
            assert P.run_rounds(None, run, merge=merge) is None
            assert getattr(run, "merged", None) == want, (merge, getattr(run, "merged", None))
    finally:
        P.GOP_CHU = old


_harness.run(globals())
