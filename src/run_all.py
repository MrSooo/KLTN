r"""Chạy lại cả chuỗi 1.1 -> 2.3-2.4 -> đồ thị trên cả kho lao động. Dùng làm hồi quy cho mỗi bước sửa.

Chạy: python -I src/run_all.py            (1.1, 1.2, 1.4, 1.5 tường minh + chung, 1.6 gạch cụm, 1.6B-1.8 bản viết lại, 2.2, 2.3-2.4, checks, graph)
      python -I src/run_all.py --viewer       (thêm viewer: dựng trang xem đồ thị)
      python -I src/run_all.py --tests    (thêm mọi tests/test_*.py)
      python -I src/run_all.py --viewer --tests

LLM (mặc định tắt): --llm off | replay | live, chỉ ảnh hưởng ba bước dùng LLM: 2.2 (links: đề xuất cạnh details), 1.6 giai đoạn A (concepts: gạch cụm) và 1.6 giai đoạn B
(concepts_names: đặt tên vị từ; chỉ off hoặc replay, live chạy bước này ở replay vì phần LLM của nó làm bằng phiên Claude Code, A37). Bước loại Điều (article_type) không dùng LLM từ 11/11 (A14).
  off     không gọi gì (mặc định, kết quả tất định, cùng kết quả khi chưa có cache)
  replay  chỉ đọc phản hồi đã lưu ở data/llm_cache/, thiếu thì bước đó giữ kết quả như off (không chạm mạng)
  live    như replay, thiếu cache thì GỌI API THẬT (tốn hạn mức theo docs/llm_config.md). Cần biến môi trường GEMINI_API_KEY (2.2) và ANTHROPIC_API_KEY (1.6, trả phí, A34)
          trong process này, cùng hai gói google-genai và anthropic (cài trong .venv: `.venv\Scripts\python.exe -m pip install google-genai anthropic`).
          Chạy: `python -I src\run_all.py --llm live --viewer --tests`; muốn chỉ chạy 1.6 thì `python -I src\concepts.py --llm live --max-batches N`.
          Thiếu khoá thì dừng ngay, trước khi chạy bất kỳ bước nào. Kiểm trước (không tốn lượt): `python -I src\llm_client.py --check-models`.
          Đặt khoá MỘT LẦN, ở terminal riêng của bạn (không chạy trong cuộc trò chuyện của công cụ AI, vì khoá sẽ nằm trong nội dung trò chuyện):
              setx GEMINI_API_KEY "<khoá>"      rồi mở terminal / VS Code MỚI (setx không đổi terminal đang mở).
          Biến này gắn với tài khoản Windows, không gắn với venv, nên dựng lại venv không phải lấy lại khoá. Đổi khoá thì chạy setx lại.
          Không dùng .env trong repo: khoá chỉ nằm trong biến môi trường (CONTRIBUTING.md, mục Bí mật).

Dữ liệu ghi vào data/processed/<bước>/; báo cáo chữ ghi vào docs/run_reports/<bước>/. Mỗi bước in một dòng: tên bước, rồi OK (kèm số giây)
hoặc LỖI kèm đầu ra của lệnh; bước lỗi thì dừng, các bước sau không chạy (riêng bước test chạy hết các bộ rồi mới báo). Sau khi chạy,
`git diff --stat docs/run_reports/` cho biết bước sửa vừa rồi đổi những báo cáo nào (`data/processed/` bị `.gitignore`, so bằng báo cáo chữ). Thứ tự theo phụ thuộc dữ liệu, không theo số L:
1.4 chạy trước 2.3-2.4 (Điều nhãn effect_transition là nguồn chỉ thị), 1.5 tường minh trước 1.5 chung, 2.2 sau 1.2.
"""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))  # -I không tự thêm thư mục script
import llm_client  # noqa: E402

LLM_SCRIPTS = ("src/links.py", "src/concepts.py")  # hai bước này nhận --llm off|replay|live
# 1.6B (A37) chỉ có off|replay: phần LLM chạy bằng phiên Claude Code, không gọi API. [THÊM] `--llm live` của run_all chạy bước này ở replay (in rõ), không từ chối,
# để `run_all --llm live` vẫn dùng được cho 1.6A và 2.2.
NAMES_SCRIPT = "src/concepts_names.py"
# Bản viết lại 1.6B-1.8 (A41): phần LLM làm bằng phiên Claude Code ngoài repo, run_all chỉ đọc cache (off giữ off, replay và live thành replay).
# Kho chưa có kết quả 1.6A (kho đầy đủ trước lần chạy cả kho) thì ba bước tự in "BỎ QUA" và thoát 0; chạy thật trên tập con: --tap-con lldnn.
SANDBOX_SCRIPTS = (NAMES_SCRIPT, "src/predicates.py")

STEPS = [
    ("1.1 tách cấu trúc văn bản", ["src/parse.py", "--all"]),
    ("1.2 cạnh cấu trúc và dẫn chiếu", ["src/refs.py", "--all"]),
    ("1.4 phân loại Điều", ["src/article_type.py"]),
    ("1.5 ngoại lệ tường minh", ["src/exceptions_explicit.py", "--all"]),
    ("1.5 ngoại lệ chung", ["src/exceptions_general.py", "--all"]),
    ("1.6 gạch cụm (giai đoạn A)", ["src/concepts.py"]),
    ("1.6 đặt tên vị từ (giai đoạn B)", [NAMES_SCRIPT]),
    ("1.6B vị từ, bản viết lại (A41)", ["src/predicates.py"]),
    ("1.7 ngoại lệ ngầm (A41)", ["src/implicit_exceptions.py"]),
    ("1.8 quy tắc s(CASP) (A41)", ["src/rules.py"]),
    ("1.3 điều khoản giao chi tiết", ["src/delegation.py"]),
    ("2.2 nối văn bản: based_on, details", ["src/links.py"]),
    ("2.3-2.4 phiên bản theo ngày hiệu lực", ["src/versions.py"]),
    ("checks: kiểm tra độc lập", ["src/checks.py"]),
    ("graph: đồ thị gộp", ["src/graph.py"]),
]
VIEWER_STEPS = [("viewer: trang xem đồ thị", ["utils/viewer/viewer.py"])]


def llm_flag(cmd, mode):
    """Cờ --llm thêm vào lệnh của một bước. 1.6B: off giữ off, replay và live đều thành replay."""
    if mode == "off":
        return []
    if cmd[0] in SANDBOX_SCRIPTS:
        return ["--llm", "replay"]
    return ["--llm", mode] if cmd[0] in LLM_SCRIPTS else []


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
    ap.add_argument("--llm", choices=("off", "replay", "live"), default="off", help="chế độ LLM cho 2.2 và 1.6 (xem đầu file); mặc định off")
    ap.add_argument("--tap-con", metavar="TÊN", help="chạy trên kho con data/subsets/<TÊN>.json (A41): dựng kho con trước, đầu ra ở data/processed_subset/<TÊN>/")
    args = ap.parse_args()
    if args.tap_con:
        # Bộ test viết cho kho đầy đủ (số đối chiếu, mốc), chạy trên kho con thì đỏ giả: không cho ghép hai cờ.
        if args.tests:
            raise SystemExit("--tests chỉ chạy trên kho đầy đủ; bỏ --tap-con hoặc bỏ --tests")
        # Đặt trong os.environ để mọi lệnh con (mỗi bước là một process) thấy cùng kho con qua corpus.py.
        os.environ["KLTN_TAP_CON"] = args.tap_con
        print(run("utils/subset/build_subset.py", args.tap_con), end="")
    if args.llm == "live":
        cfg = llm_client.load_config()
        # 2.2 dùng vai chinh và kiem, 1.6 dùng vai trich: cần khoá của mọi nhà cung cấp đang dùng, thiếu cái nào cũng dừng ngay trước khi chạy bước nào
        missing = [llm_client.PROVIDERS[p] for p in sorted({llm_client.provider_of(cfg, r) for r in llm_client.ROLES + llm_client.EXTRA_ROLES}) if not llm_client.key_is_set(p)]
        if missing:
            raise SystemExit(f"--llm live nhưng không thấy {', '.join(missing)} trong môi trường của process này; chưa chạy bước nào, chưa tốn lượt nào.\n"
                             f"Đặt khoá MỘT LẦN bằng `setx <tên biến>` (xem hướng dẫn ở đầu src/run_all.py), mở terminal mới rồi chạy lại.")
        print(f"LLM live: sẽ gọi API thật khi thiếu cache. Hạn mức: chinh {cfg['chinh.model']} {cfg['chinh.luot_moi_ngay']}/ngày, "
              f"kiem {cfg['kiem.model']} {cfg['kiem.luot_moi_ngay']}/ngày, trich {cfg['trich.model']} (chặn an toàn {cfg['trich.luot_moi_ngay']}/ngày).")
    if args.llm == "live":
        print("1.6B (đặt tên vị từ) không có live (A37): bước này chạy ở replay, phần LLM của nó làm bằng phiên Claude Code (docs/operations/llm_sandbox.md).")
    cmds = [(name, cmd + llm_flag(cmd, args.llm)) for name, cmd in STEPS + (VIEWER_STEPS if args.viewer else [])]
    chatty = lambda cmd: args.llm != "off" and cmd[0] in LLM_SCRIPTS  # noqa: E731  bước LLM: cho stderr (log tiến độ) hiện ngay
    steps = [(name, lambda cmd=cmd: run(*cmd, relay_stderr=chatty(cmd)), chatty(cmd)) for name, cmd in cmds]
    if args.tests:
        steps.append((f"Test ({len(list((ROOT / 'tests').glob('test_*.py')))} bộ)", step_tests, False))
    run_steps(steps)
    if args.llm != "off":
        c = llm_client.Client("off")
        print(f"LLM hôm nay đã dùng: chinh {c.used_today('chinh')}/{c.cfg['chinh.luot_moi_ngay']}, kiem {c.used_today('kiem')}/{c.cfg['kiem.luot_moi_ngay']}, "
              f"trich {c.used_today('trich')}/{c.cfg['trich.luot_moi_ngay']}")
