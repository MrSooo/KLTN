"""Chạy lại toàn bộ A1→A7 trên hai file nguồn và 8 văn bản dev. Dùng làm hồi quy cho mỗi bước sửa.

Chạy: python -I src/run_all.py            (cần Python >= 3.10; chỉ các bước chính A1→A7)
      python -I src/run_all.py --a8       (thêm A8: dựng ba trang xem đồ thị)
      python -I src/run_all.py --tests    (thêm bộ kiểm thử ngoài và các bộ test)
      python -I src/run_all.py --a8 --tests

Dữ liệu ghi vào data/processed/<bước>/ (a1/ … a8/; A4 chia thêm theo tên văn bản sửa đổi); báo cáo chữ ghi vào docs/bao_cao_chay/<bước>/ (a1/ … a7/, eval/).
Mỗi bước in một dòng: tên bước ghi trước, rồi OK (kèm số giây) hoặc LỖI khi bước xong; không in từng lệnh con. Bước lỗi thì in lệnh hoặc
bộ test lỗi cùng đầu ra của nó rồi thoát 1, các bước sau không chạy (riêng bước test chạy hết các bộ rồi mới báo). Sau khi chạy,
`git diff --stat data/ docs/bao_cao_chay/` cho biết bước sửa vừa rồi đổi những đầu ra nào.
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
A4_DIR = "data/processed/a4"
BASES = {"5dieu": "data/sample/blds2015_5dieu.md", "p4": "data/raw/blds2015_p4.md"}
DEV = ["dev01_bai_bo_khoan", "dev02_sua_khoan", "dev03_thay_dieu", "dev04_bo_sung",
       "dev05_bai_bo_ds", "dev06_cum_tu", "dev07_doi_ten", "dev08_thay_van_ban"]
SNAPSHOT_DATES = {"dev02_sua_khoan": ["2027-07-01"], "dev01+dev02": ["2027-01-01", "2027-07-01"]}  # còn lại: 2027-01-01
A5_VERSIONS = [("5dieu", "dev01+dev02"), ("5dieu", "dev04_bo_sung"), ("p4", "dev01_full")]
A7_AT_DATE = [("p4", "p4_dev05_bai_bo_ds", "2027-01-01")]
TESTS = [f"test_a{i}.py" for i in range(1, 8)] + ["test_a4_llm.py", "test_eval_gold.py", "test_eval_ext_amend.py"]


class StepError(Exception):
    """Một lệnh con lỗi; nội dung là đầu ra của nó rồi đến lệnh."""


def run(*args):
    cmd = [sys.executable, "-I", *map(str, args)]
    done = subprocess.run(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
    if done.returncode != 0:
        raise StepError(f"{done.stdout.rstrip()}\nthoát {done.returncode}: {' '.join(cmd[2:])}")
    return done.stdout


def amend(base, docs, name):
    args = ["src/a4_versions.py", "apply", "--base", BASES[base]]
    for d in docs:
        args += ["--amend", f"data/dev_amend/{d}.md"]
    run(*args, "--name", name)
    dates = [] if name == "dev01_full" else SNAPSHOT_DATES.get(name.removeprefix("p4_"), ["2027-01-01"])
    for date in dates:
        run("src/a4_versions.py", "snapshot", "--name", name, "--date", date,
            "--out", f"{A4_DIR}/{name}/a4_{name}_snapshot_{date}.md")


def versions_file(name):
    return f"{A4_DIR}/{name}/a4_{name}_versions.jsonl"


def step_a1():
    for src in BASES.values():
        run("src/a1_parse.py", src)


def step_a2():
    for src in BASES.values():
        run("src/a2_edges.py", src)
        run("src/a2_edges.py", src, "--refers-to")


def step_a3():
    for src in BASES.values():
        run("src/a3_exceptions.py", src)


def step_a6():
    for src in BASES.values():
        run("src/a6_general_exceptions.py", src)


def step_a5():
    for src in BASES.values():
        run("src/a5_checks.py", src)


def step_a7():
    for src in BASES.values():
        run("src/a7_graph.py", src)




def step_a4():
    for base, prefix in (("5dieu", ""), ("p4", "p4_")):
        for d in DEV:
            amend(base, [d], prefix + d)
        amend(base, DEV[:2], prefix + "dev01+dev02")
    amend("p4", DEV[:1], "dev01_full")


def step_a5_versions():
    for base, name in A5_VERSIONS:
        run("src/a5_checks.py", BASES[base], "--versions", versions_file(name))


def step_a7_at_date():
    for base, name, date in A7_AT_DATE:
        run("src/a7_graph.py", BASES[base], "--versions", versions_file(name), "--date", date)


def step_a8():
    for src in BASES.values():
        run("utils/a8/a8_viz.py", src)
    for base, name, date in A7_AT_DATE:
        run("utils/a8/a8_viz.py", BASES[base], "--versions", versions_file(name), "--date", date)


def step_external():
    run("tests/eval_ext_amend.py", "--llm", "off")  # bộ kiểm thử ngoài, không gọi LLM; chế độ replay chạy riêng khi đã có kết quả lưu


def step_tests():
    bad = []
    for t in TESTS:
        try:
            out = run(f"tests/{t}")
        except StepError as e:
            bad.append((t, str(e)))
            continue
        if out.strip().splitlines()[-1] != "tổng test lỗi: 0":
            bad.append((t, out.rstrip()))
    if bad:
        raise StepError("\n".join(f"--- {t}\n{out}" for t, out in bad) + f"\ntest lỗi: {[t for t, _ in bad]}")


MAIN_STEPS = [
    ("A1 tách văn bản", step_a1),
    ("A2 cạnh cấu trúc và dẫn chiếu", step_a2),
    ("A3 ngoại lệ tường minh", step_a3),
    ("A6 ngoại lệ chung", step_a6),
    ("A5 kiểm tra A1-A3", step_a5),
    ("A7 đồ thị gộp", step_a7),
    ("A4 phiên bản theo văn bản sửa đổi", step_a4),
    ("A5 kiểm tra phiên bản", step_a5_versions),
    ("A7 đồ thị tại ngày 2027-01-01", step_a7_at_date),
]
A8_STEPS = [("A8 trang xem đồ thị (cả bản tại ngày 2027-01-01)", step_a8)]
TEST_STEPS = [
    ("Bộ kiểm thử ngoài (không gọi LLM)", step_external),
    (f"Test ({len(TESTS)} bộ)", step_tests),
]


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
    sys.stdout.reconfigure(encoding="utf-8")  # tên bước và lỗi có tiếng Việt
    ap = argparse.ArgumentParser()
    ap.add_argument("--a8", action="store_true", help="thêm A8: dựng các trang xem đồ thị")
    ap.add_argument("--tests", action="store_true", help="thêm bộ kiểm thử ngoài và các bộ test")
    args = ap.parse_args()
    run_steps(MAIN_STEPS + (A8_STEPS if args.a8 else []) + (TEST_STEPS if args.tests else []))
