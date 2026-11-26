"""Gom thời gian chạy model theo bước, từ log sandbox_api (UTF-16 lẫn UTF-8) và bản ghi cache sandbox_api.
Chạy: python -X utf8 -I utils/llm_runs/sandbox_api_timing.py <log>... (log ở docs/run_reports*/.../run_logs/) ; in số lô xong, tổng giây gọi, số lần thử lại, lỗi theo mã."""
import re
import sys
from collections import Counter


def doc(path):
    b = open(path, "rb").read()
    # log PowerShell: phần đầu UTF-16-LE, phần nối thêm có thể là UTF-8; thử cả hai, lấy dòng đọc được
    out = []
    for enc in ("utf-16-le", "utf-8"):
        t = b.decode(enc, errors="ignore")
        out += [l for l in t.splitlines() if "LLM sandbox_api" in l or "API lỗi" in l or "ma thoat" in l]
    return out


for p in sys.argv[1:]:
    lines = doc(p)
    xong = [l for l in lines if "xong sau" in l]
    giay = [int(m.group(1)) for l in xong for m in [re.search(r"xong sau (\d+)s", l)] if m]
    ra = [int(m.group(1)) for l in xong for m in [re.search(r"ra (\d+)", l)] if m]
    loi = Counter(m.group(1) for l in lines for m in [re.search(r"API lỗi (\d+|\w+)", l)] if m)
    loi_lo = sorted({m.group(1) for l in lines if "API lỗi" in l or "lỗi" in l for m in [re.search(r"lô (\d+)", l)] if m})
    print(f"{p}: lần gọi xong {len(xong)}, tổng giây gọi {sum(giay)}, max {max(giay, default=0)}s, token ra {sum(ra)}, lỗi API theo mã {dict(loi)}")
