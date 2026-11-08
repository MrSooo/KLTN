"""Chạy lại cả chuỗi L1 -> L6 -> đồ thị trên cả kho lao động. Dùng làm hồi quy cho mỗi bước sửa.

Chạy: python -I src/run_all.py            (L1 A1, L2 A2, L4, L5 A3 + A6, L3, L6 phiên bản, A5 kiểm tra, A7 đồ thị)
      python -I src/run_all.py --a8       (thêm A8: dựng trang xem đồ thị)
      python -I src/run_all.py --tests    (thêm mọi tests/test_*.py)
      python -I src/run_all.py --a8 --tests

Dữ liệu ghi vào data/processed/<bước>/; báo cáo chữ ghi vào docs/bao_cao_chay/<bước>/. Mỗi bước in một dòng: tên bước, rồi OK (kèm số giây)
hoặc LỖI kèm đầu ra của lệnh; bước lỗi thì dừng, các bước sau không chạy (riêng bước test chạy hết các bộ rồi mới báo). Sau khi chạy,
`git diff --stat docs/bao_cao_chay/` cho biết bước sửa vừa rồi đổi những báo cáo nào (`data/processed/` bị `.gitignore`, so bằng báo cáo chữ). Thứ tự theo phụ thuộc dữ liệu, không theo số L:
L4 chạy trước L6 (Điều nhãn effect_transition là nguồn chỉ thị), A3 trước A6, L3 sau A2.
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STEPS = [
    ("L1 A1 tách cấu trúc 18 văn bản", ["src/a1_parse.py", "--all"]),
    ("L2 A2 cạnh cấu trúc và dẫn chiếu", ["src/a2_edges.py", "--all"]),
    ("L4 phân loại Điều", ["src/l4_classify.py"]),
    ("L5 A3 ngoại lệ tường minh", ["src/a3_exceptions.py", "--all"]),
    ("L5 A6 ngoại lệ chung", ["src/a6_general_exceptions.py", "--all"]),
    ("L3 điều khoản giao chi tiết, based_on, details", ["src/l3_links.py"]),
    ("L6 phiên bản theo ngày hiệu lực", ["src/a4_versions.py"]),
    ("A5 kiểm tra độc lập", ["src/a5_checks.py"]),
    ("A7 đồ thị gộp", ["src/a7_graph.py"]),
]
A8_STEPS = [("A8 trang xem đồ thị", ["utils/a8/a8_viz.py"])]


class StepError(Exception):
    """Một lệnh con lỗi; nội dung là đầu ra của nó rồi đến lệnh."""


def run(*args):
    cmd = [sys.executable, "-X", "utf8", "-I", *map(str, args)]
    done = subprocess.run(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
    if done.returncode != 0:
        raise StepError(f"{done.stdout.rstrip()}\nthoát {done.returncode}: {' '.join(cmd[4:])}")
    return done.stdout


def step_tests():
    bad = []
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        try:
            out = run(f"tests/{path.name}")
        except StepError as e:
            bad.append((path.name, str(e)))
            continue
        if out.strip().splitlines()[-1] != "tổng test lỗi: 0":
            bad.append((path.name, out.rstrip()))
    if bad:
        raise StepError("\n".join(f"--- {t}\n{out}" for t, out in bad) + f"\ntest lỗi: {[t for t, _ in bad]}")


def run_steps(steps):
    width = max(len(name) for name, _ in steps)
    start = time.monotonic()
    for i, (name, fn) in enumerate(steps, 1):
        print(f"[{i:>2}/{len(steps)}] {name:<{width}}  ", end="", flush=True)
        began = time.monotonic()
        try:
            fn()
        except StepError as e:
            print("LỖI\n")
            print(e)
            raise SystemExit(1)
        print(f"OK  ({time.monotonic() - began:.1f}s)")
    print(f"XONG: {len(steps)}/{len(steps)} bước, {time.monotonic() - start:.0f}s")


if __name__ == "__main__":
    if sys.version_info < (3, 10):
        raise SystemExit(f"cần Python >= 3.10, đang chạy {sys.version.split()[0]}")
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--a8", action="store_true", help="thêm A8: dựng trang xem đồ thị")
    ap.add_argument("--tests", action="store_true", help="thêm mọi tests/test_*.py")
    args = ap.parse_args()
    steps = [(name, lambda cmd=cmd: run(*cmd)) for name, cmd in STEPS + (A8_STEPS if args.a8 else [])]
    if args.tests:
        steps.append((f"Test ({len(list((ROOT / 'tests').glob('test_*.py')))} bộ)", step_tests))
    run_steps(steps)
