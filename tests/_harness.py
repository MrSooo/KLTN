"""Khung test tối giản (chỉ thư viện chuẩn): mỗi file test gọi run(globals()); dòng cuối in luôn là `tổng test lỗi: N`.

Một test là hàm `test_*` không tham số; lỗi là AssertionError hoặc ngoại lệ bất kỳ. Thoát mã 1 nếu có test lỗi.
"""
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))  # -I không tự thêm thư mục script


def run(ns):
    sys.stdout.reconfigure(encoding="utf-8")
    tests = [(n, f) for n, f in ns.items() if n.startswith("test_") and callable(f)]
    fails = 0
    for name, fn in tests:
        try:
            fn()
            print(f"ok    {name}")
        except Exception:
            fails += 1
            print(f"LỖI   {name}")
            traceback.print_exc(file=sys.stdout)
    print(f"{len(tests)} test")
    print(f"tổng test lỗi: {fails}")
    raise SystemExit(1 if fails else 0)
