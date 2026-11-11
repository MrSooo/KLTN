r"""Chạy lại cả chuỗi L1 -> L6 -> đồ thị trên cả kho lao động. Dùng làm hồi quy cho mỗi bước sửa.

Chạy: python -I src/run_all.py            (L1, L2, L4, L5 tường minh + chung, L3, L6, checks, graph)
      python -I src/run_all.py --viewer       (thêm viewer: dựng trang xem đồ thị)
      python -I src/run_all.py --tests    (thêm mọi tests/test_*.py)
      python -I src/run_all.py --viewer --tests

LLM (mặc định tắt): --llm off | replay | live, chỉ ảnh hưởng một bước dùng LLM là L3 (đề xuất cạnh details). Bước loại Điều (article_type) không dùng LLM từ 11/11 (A14).
  off     không gọi gì (mặc định, kết quả tất định, cùng kết quả khi chưa có cache)
  replay  chỉ đọc phản hồi đã lưu ở data/llm_cache/, thiếu thì bước đó giữ kết quả như off (không chạm mạng)
  live    như replay, thiếu cache thì GỌI API THẬT (tốn hạn mức theo docs/llm_config.md). Cần biến môi trường GEMINI_API_KEY trong process này và
          gói google-genai (cài trong .venv: `.venv\Scripts\python.exe -m pip install google-genai`). Chạy: `python -I src\run_all.py --llm live --viewer --tests`.
          Thiếu khoá thì dừng ngay, trước khi chạy bất kỳ bước nào. Kiểm trước (không tốn lượt): `python -I src\llm_client.py --check-models`.
          Đặt khoá MỘT LẦN, ở terminal riêng của bạn (KHÔNG dùng tiền tố `!` của Claude Code, vì lệnh sẽ nằm trong cuộc trò chuyện):
              setx GEMINI_API_KEY "<khoá>"      rồi mở terminal / VS Code MỚI (setx không đổi terminal đang mở).
          Biến này gắn với tài khoản Windows, không gắn với venv, nên dựng lại venv không phải lấy lại khoá. Đổi khoá thì chạy setx lại.
          Dùng .env trong repo là KHÔNG được (CLAUDE.md mục 1.7: khoá chỉ nằm trong biến môi trường).

Dữ liệu ghi vào data/processed/<bước>/; báo cáo chữ ghi vào docs/bao_cao_chay/<bước>/. Mỗi bước in một dòng: tên bước, rồi OK (kèm số giây)
hoặc LỖI kèm đầu ra của lệnh; bước lỗi thì dừng, các bước sau không chạy (riêng bước test chạy hết các bộ rồi mới báo). Sau khi chạy,
`git diff --stat docs/bao_cao_chay/` cho biết bước sửa vừa rồi đổi những báo cáo nào (`data/processed/` bị `.gitignore`, so bằng báo cáo chữ). Thứ tự theo phụ thuộc dữ liệu, không theo số L:
L4 chạy trước L6 (Điều nhãn effect_transition là nguồn chỉ thị), L5 tường minh trước L5 chung, L3 sau L2.
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))  # -I không tự thêm thư mục script
import llm_client  # noqa: E402

LLM_SCRIPTS = ("src/links.py",)  # chỉ bước này nhận --llm

STEPS = [
    ("L1 tách cấu trúc 18 văn bản", ["src/parse.py", "--all"]),
    ("L2 cạnh cấu trúc và dẫn chiếu", ["src/refs.py", "--all"]),
    ("L4 phân loại Điều", ["src/article_type.py"]),
    ("L5 ngoại lệ tường minh", ["src/exceptions_explicit.py", "--all"]),
    ("L5 ngoại lệ chung", ["src/exceptions_general.py", "--all"]),
    ("1.3 điều khoản giao chi tiết", ["src/delegation.py"]),
    ("2.2 nối văn bản: based_on, details", ["src/links.py"]),
    ("L6 phiên bản theo ngày hiệu lực", ["src/l6_versions.py"]),
    ("checks: kiểm tra độc lập", ["src/checks.py"]),
    ("graph: đồ thị gộp", ["src/graph.py"]),
]
VIEWER_STEPS = [("viewer: trang xem đồ thị", ["utils/viewer/viewer.py"])]


class StepError(Exception):
    """Một lệnh con lỗi; nội dung là đầu ra của nó rồi đến lệnh."""


def run(*args, relay_stderr=False):
    """Chạy một lệnh con, gom stdout. relay_stderr=True: stderr của lệnh con đi thẳng ra console (không gom) để thấy log tiến độ LLM khi đang chạy;
    nếu lệnh lỗi, traceback đã hiện ở console nên StepError chỉ mang phần stdout."""
    cmd = [sys.executable, "-X", "utf8", "-I", *map(str, args)]
    done = subprocess.run(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=None if relay_stderr else subprocess.STDOUT, text=True, encoding="utf-8")
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
    """steps: list (tên, hàm, chatty). chatty=True là bước tự in log ra stderr khi chạy: in tiêu đề rồi xuống dòng, kết quả ghi ở dòng riêng sau log."""
    width = max(len(name) for name, _, _ in steps)
    start = time.monotonic()
    for i, (name, fn, chatty) in enumerate(steps, 1):
        print(f"[{i:>2}/{len(steps)}] {name:<{width}}  ", end="\n" if chatty else "", flush=True)
        began = time.monotonic()
        try:
            fn()
        except StepError as e:
            print(("      " if chatty else "") + "LỖI\n")
            print(e)
            raise SystemExit(1)
        print(f"{'      -> ' if chatty else ''}OK  ({time.monotonic() - began:.1f}s)")
    print(f"XONG: {len(steps)}/{len(steps)} bước, {time.monotonic() - start:.0f}s")


if __name__ == "__main__":
    if sys.version_info < (3, 10):
        raise SystemExit(f"cần Python >= 3.10, đang chạy {sys.version.split()[0]}")
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")  # thông báo SystemExit có tiếng Việt
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--viewer", action="store_true", help="thêm viewer: dựng trang xem đồ thị")
    ap.add_argument("--tests", action="store_true", help="thêm mọi tests/test_*.py")
    ap.add_argument("--llm", choices=("off", "replay", "live"), default="off", help="chế độ LLM cho L3 (xem đầu file); mặc định off")
    args = ap.parse_args()
    if args.llm == "live":
        if not llm_client.key_is_set():
            raise SystemExit("--llm live nhưng không thấy GEMINI_API_KEY trong môi trường của process này; chưa chạy bước nào, chưa tốn lượt nào.\n"
                             "Đặt khoá MỘT LẦN bằng `setx GEMINI_API_KEY` (xem hướng dẫn ở đầu src/run_all.py), mở terminal mới rồi chạy lại.")
        cfg = llm_client.load_config()
        print(f"LLM live: sẽ gọi API thật khi thiếu cache. Hạn mức: chinh {cfg['chinh.model']} {cfg['chinh.luot_moi_ngay']}/ngày, "
              f"kiem {cfg['kiem.model']} {cfg['kiem.luot_moi_ngay']}/ngày.")
    cmds = [(name, cmd + (["--llm", args.llm] if args.llm != "off" and cmd[0] in LLM_SCRIPTS else [])) for name, cmd in STEPS + (VIEWER_STEPS if args.viewer else [])]
    chatty = lambda cmd: args.llm != "off" and cmd[0] in LLM_SCRIPTS  # noqa: E731  bước LLM: cho stderr (log tiến độ) hiện ngay
    steps = [(name, lambda cmd=cmd: run(*cmd, relay_stderr=chatty(cmd)), chatty(cmd)) for name, cmd in cmds]
    if args.tests:
        steps.append((f"Test ({len(list((ROOT / 'tests').glob('test_*.py')))} bộ)", step_tests, False))
    run_steps(steps)
    if args.llm != "off":
        c = llm_client.Client("off")
        print(f"LLM hôm nay đã dùng: chinh {c.used_today('chinh')}/{c.cfg['chinh.luot_moi_ngay']}, kiem {c.used_today('kiem')}/{c.cfg['kiem.luot_moi_ngay']}")
