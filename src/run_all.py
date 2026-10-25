"""Chạy lại toàn bộ A1→A7 trên hai file nguồn và 8 văn bản dev, rồi chạy các bộ test. Dùng làm hồi quy cho mỗi bước sửa.

Chạy: python -I src/run_all.py            (cần Python >= 3.10)
      python -I src/run_all.py --no-tests

Ghi đè đúng các file đang có trong data/processed và docs (cùng tên, cùng tham số đã dùng để sinh chúng). Sau khi chạy,
`git diff --stat data/ docs/` cho biết bước sửa vừa rồi đổi những đầu ra nào. Dừng ở lệnh đầu tiên thoát khác 0.
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
BASES = {"5dieu": "data/sample/blds2015_5dieu.md", "p4": "data/raw/blds2015_p4.md"}
DEV = ["dev01_bai_bo_khoan", "dev02_sua_khoan", "dev03_thay_dieu", "dev04_bo_sung",
       "dev05_bai_bo_ds", "dev06_cum_tu", "dev07_doi_ten", "dev08_thay_van_ban"]
SNAPSHOT_DATES = {"dev02_sua_khoan": ["2027-07-01"], "dev01+dev02": ["2027-01-01", "2027-07-01"]}  # còn lại: 2027-01-01
A5_VERSIONS = [("5dieu", "dev01+dev02"), ("5dieu", "dev04_bo_sung"), ("p4", "dev01_full")]
A7_AT_DATE = [("p4", "p4_dev05_bai_bo_ds", "2027-01-01")]
TESTS = [f"test_a{i}.py" for i in range(1, 8)] + ["test_eval_gold.py"]


def run(*args):
    cmd = [sys.executable, "-I", *map(str, args)]
    print("$", " ".join(cmd[2:]), flush=True)
    done = subprocess.run(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
    if done.returncode != 0:
        print(done.stdout)
        raise SystemExit(f"thoát {done.returncode}: {' '.join(cmd[2:])}")
    return done.stdout


def amend(base, docs, name):
    args = ["src/a4_versions.py", "apply", "--base", BASES[base]]
    for d in docs:
        args += ["--amend", f"data/dev_amend/{d}.md"]
    run(*args, "--name", name)
    dates = [] if name == "dev01_full" else SNAPSHOT_DATES.get(name.removeprefix("p4_"), ["2027-01-01"])
    for date in dates:
        run("src/a4_versions.py", "snapshot", "--name", name, "--date", date,
            "--out", f"data/processed/a4_{name}_snapshot_{date}.md")


def pipeline():
    for src in BASES.values():
        run("src/a1_parse.py", src)
        run("src/a2_edges.py", src)
        run("src/a2_edges.py", src, "--refers-to")
        run("src/a3_exceptions.py", src)
        run("src/a6_general_exceptions.py", src)
        run("src/a5_checks.py", src)
        run("src/a7_graph.py", src)
    for base, prefix in (("5dieu", ""), ("p4", "p4_")):
        for d in DEV:
            amend(base, [d], prefix + d)
        amend(base, DEV[:2], prefix + "dev01+dev02")
    amend("p4", DEV[:1], "dev01_full")
    for base, name in A5_VERSIONS:
        run("src/a5_checks.py", BASES[base], "--versions", f"data/processed/a4_{name}_versions.jsonl")
    for base, name, date in A7_AT_DATE:
        run("src/a7_graph.py", BASES[base], "--versions", f"data/processed/a4_{name}_versions.jsonl", "--date", date)


def tests():
    bad = []
    for t in TESTS:
        last = run(f"src/{t}").strip().splitlines()[-1]
        print("  ", last)
        if last != "tổng test lỗi: 0":
            bad.append(t)
    if bad:
        raise SystemExit(f"test lỗi: {bad}")


if __name__ == "__main__":
    if sys.version_info < (3, 10):
        raise SystemExit(f"cần Python >= 3.10, đang chạy {sys.version.split()[0]}")
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-tests", action="store_true")
    args = ap.parse_args()
    pipeline()
    if not args.no_tests:
        tests()
    print("XONG")
