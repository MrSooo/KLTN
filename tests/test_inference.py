"""A9: đường dẫn JSONL theo kiểu v3 và cơ chế chặn ngoại lệ của s(CASP).

Chạy: python -I tests/test_inference.py   (các hàm test_* cũng chạy được bằng pytest nếu có cài)
Test truy vấn sống cần swipl + library(scasp) và file data/processed/a9_lld2019_labor.pl đã sinh.
"""
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))  # tests/ is separate; import modules from src/
import edges
import inference

ROOT = Path(__file__).resolve().parent.parent
LABOR_PROGRAM = ROOT / "data" / "processed" / "a9_lld2019_labor.pl"

# Nguồn giả: stem phải có trong law_registry để unit_prefix ra LLD2019.
SRC = ROOT / "data" / "raw" / "lld2019_labor.md"
BLOCKED_UNIT = "LLD2019.D35.K2.e"


def write_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def with_processed_dir(tmp):
    """Tạm đổi gốc data/processed sang thư mục tạm; nơi gọi trả lại giá trị cũ trong finally."""
    saved = edges.PROCESSED_DIR
    edges.PROCESSED_DIR = Path(tmp)
    return saved


def test_resolve_jsonl_path_v3_subdir():
    """Ưu tiên thư mục bước kiểu v3: a3/a3_exceptions_<stem>.jsonl."""
    with tempfile.TemporaryDirectory() as tmp:
        v3 = Path(tmp) / "a3" / "a3_exceptions_demo.jsonl"
        flat = Path(tmp) / "a3_exceptions_demo.jsonl"
        v3.parent.mkdir(parents=True)
        v3.write_text("", encoding="utf-8")
        flat.write_text("", encoding="utf-8")
        saved = with_processed_dir(tmp)
        try:
            got = inference._resolve_jsonl_path("a3", "a3_exceptions", "demo", None)
        finally:
            edges.PROCESSED_DIR = saved
        assert got == v3, f"phải chọn bản v3 {v3}, nhận {got}"


def test_resolve_jsonl_path_legacy_flat():
    """Không có thư mục bước thì lùi về tệp phẳng kiểu cũ."""
    with tempfile.TemporaryDirectory() as tmp:
        flat = Path(tmp) / "a6_exceptions_demo.jsonl"
        flat.write_text("", encoding="utf-8")
        saved = with_processed_dir(tmp)
        try:
            got = inference._resolve_jsonl_path("a6", "a6_exceptions", "demo", None)
        finally:
            edges.PROCESSED_DIR = saved
        assert got == flat, f"phải chọn tệp phẳng {flat}, nhận {got}"


def test_resolve_jsonl_path_missing():
    """Không có tệp nào: trả vị trí v3 (đọc ra rỗng), không ném lỗi, không đoán sang tệp khác."""
    with tempfile.TemporaryDirectory() as tmp:
        saved = with_processed_dir(tmp)
        try:
            got = inference._resolve_jsonl_path("a8", "a8_implicit_exceptions", "demo", "_v1_2020-01-01")
            rows = inference.read_rows(got)
        finally:
            edges.PROCESSED_DIR = saved
        assert got == Path(tmp) / "a8" / "a8_implicit_exceptions_demo_v1_2020-01-01.jsonl", got
        assert rows == []


def test_resolve_jsonl_path_ignores_same_name_file_of_other_stage():
    """Tệp cùng tên nhưng khác thư mục bước không được nhận nhầm (lỗi cũ: a3/a3_<stem>)."""
    with tempfile.TemporaryDirectory() as tmp:
        wrong = Path(tmp) / "a3" / "a3_demo.jsonl"
        right = Path(tmp) / "a6" / "a6_exceptions_demo.jsonl"
        wrong.parent.mkdir(parents=True)
        right.parent.mkdir(parents=True)
        wrong.write_text("", encoding="utf-8")
        right.write_text("", encoding="utf-8")
        saved = with_processed_dir(tmp)
        try:
            got = inference._resolve_jsonl_path("a6", "a6_exceptions", "demo", None)
        finally:
            edges.PROCESSED_DIR = saved
        assert got == right, f"nhận nhầm {got}"


def test_edges_triples_path_prefers_canonical_a1_file():
    """edges.triples_path phải đọc a1/a1_triples_<stem>.jsonl do A1 ghi, không tìm a1_<stem>.jsonl."""
    with tempfile.TemporaryDirectory() as tmp:
        canonical = Path(tmp) / "a1" / "a1_triples_demo.jsonl"
        legacy = Path(tmp) / "a1" / "a1_demo.jsonl"
        canonical.parent.mkdir(parents=True)
        canonical.write_text("", encoding="utf-8")
        legacy.write_text("", encoding="utf-8")
        saved = with_processed_dir(tmp)
        try:
            got = edges.triples_path(Path(tmp) / "demo.md")
        finally:
            edges.PROCESSED_DIR = saved
        assert got == canonical, f"phải chọn {canonical}, nhận {got}"


def test_render_program_grounds_blocking():
    """blocked/1 phải đọc has_exception/1 (fact đơn trị, khử trùng) thay vì quét exception_of/2."""
    with tempfile.TemporaryDirectory() as tmp:
        write_rows(Path(tmp) / "a3" / "a3_exceptions_lld2019_labor.jsonl",
                   [{"s": "LLD2019.C_1", "p": "exception_of", "o": BLOCKED_UNIT}])
        write_rows(Path(tmp) / "a6" / "a6_exceptions_lld2019_labor.jsonl",
                   [{"s": "LLD2019.D36.K1.b", "p": "exception_of", "o": BLOCKED_UNIT},
                    {"s": "LLD2019.C_2", "p": "exception_of", "o": "LLD2019.D46.K1"}])
        saved_dir = with_processed_dir(tmp)
        saved_codes = inference.active_codes
        inference.active_codes = lambda *a, **k: [BLOCKED_UNIT, "LLD2019.D36.K1.b", "LLD2019.D46.K1"]
        try:
            program, n_units, n_exc, n_rules = inference.render_program(SRC)
        finally:
            inference.active_codes = saved_codes
            edges.PROCESSED_DIR = saved_dir
        assert n_units == 3 and n_exc == 3, (n_units, n_exc, n_rules)
        # chứng cứ nguồn gốc vẫn còn, nhưng chỉ một fact has_exception cho mỗi đích
        assert program.count("exception_of(") == 3, program
        assert program.count(f"has_exception('{BLOCKED_UNIT}').") == 1, program
        assert program.count("has_exception('LLD2019.D46.K1').") == 1, program
        assert program.count("has_exception('") == 2, program
        assert "blocked(U) :- has_exception(U)." in program
        assert "blocked(U) :- exception_of(_, U)." not in program
        assert "holds(U) :- in_force(U), not blocked(U)." in program


def test_labor_program_has_ten_exceptions_and_grounded_rule():
    """Chương trình đã sinh cho mẫu lao động: 10 cạnh exception_of, luật chặn đã ground."""
    if not LABOR_PROGRAM.exists():
        return  # chưa chạy src/inference.py cho lld2019_labor
    text = LABOR_PROGRAM.read_text(encoding="utf-8")
    assert text.count("\nexception_of(") == 10, text.count("\nexception_of(")
    assert "blocked(U) :- has_exception(U)." in text
    assert "blocked(U) :- exception_of(_, U)." not in text


def test_holds_blocked_returns_no_fast():
    """Truy vấn sống: holds(đơn vị bị chặn) trả 'no' nhanh, không timeout, không cảnh báo."""
    if not shutil.which("swipl"):
        return  # máy không có swipl: bỏ qua, phần còn lại của bộ test vẫn chạy
    if not LABOR_PROGRAM.exists():
        return
    start = time.monotonic()
    out, note = inference._run_solver(LABOR_PROGRAM, "holds('%s')" % BLOCKED_UNIT)
    elapsed = time.monotonic() - start
    assert out is not None, note
    assert elapsed < 60, f"truy vấn mất {elapsed:.1f}s, cần < 60s"
    assert "ANSWER: no" in out, out
    assert "Warning:" not in out, out
    assert "SCASP_ERROR" not in out, out


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

