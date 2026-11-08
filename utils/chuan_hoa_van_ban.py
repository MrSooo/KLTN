"""Chuẩn hoá một file văn bản thô về dạng của kho data/raw/labor/: UTF-8 không BOM, LF, NFC, không dấu markdown.

Chạy: python -X utf8 -I utils/chuan_hoa_van_ban.py <file vào> <file ra>

Chỉ bỏ phần định dạng, không đụng nội dung pháp lý:
  - BOM, CRLF -> LF, NFC, bỏ khoảng trắng cuối dòng, nhiều dòng trống liền nhau thành một;
  - tiền tố tiêu đề markdown "## " ở đầu dòng; dòng kẻ ngang markdown "---";
  - khối "Nơi nhận:" của chính văn bản (danh sách nơi nhận và chữ ký) đến trước dòng cấu trúc kế tiếp (Điều, Chương, PHỤ LỤC);
    chỉ trước phụ lục đầu tiên, vì biểu mẫu trong phụ lục cũng có "Nơi nhận" và đó là nội dung của mẫu.
Nơi dùng: bản đầy đủ NQ 66.16/2026 (có Phụ lục I.7) học viên gửi ngày 08/11/2026. In ra số dòng đã bỏ để duyệt.
"""
import re
import sys
import unicodedata
from pathlib import Path

RE_NOINHAN = re.compile(r"^Nơi nhận\b")
RE_STRUCT = re.compile(r"^(?:Điều \d|Chương [IVXLC]+\b|Mục \d|PHỤ LỤC|Phụ lục [IVX\d])")
RE_HR = re.compile(r"^---$")  # đúng 3 dấu gạch: kẻ ngang markdown; dòng gạch dài trang trí ở đầu văn bản giữ nguyên
RE_PL = re.compile(r"^(?:PHỤ LỤC|Phụ lục)\b")


def normalize(raw):
    """Trả (văn bản mới, thống kê dòng bỏ)."""
    stats = {"markdown_heading": 0, "ke_ngang": 0, "noi_nhan": 0}
    text = unicodedata.normalize("NFC", raw.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n"))
    out, in_footer, seen_pl = [], False, False
    for line in text.split("\n"):
        line = line.rstrip()
        seen_pl = seen_pl or bool(RE_PL.match(line))
        if in_footer:
            if RE_STRUCT.match(line):
                in_footer = False
            else:
                stats["noi_nhan"] += 1
                continue
        if RE_NOINHAN.match(line) and not seen_pl:
            in_footer = True
            stats["noi_nhan"] += 1
            continue
        if RE_HR.match(line):
            stats["ke_ngang"] += 1
            continue
        m = re.match(r"^#{1,6} (.*)$", line)
        if m:
            stats["markdown_heading"] += 1
            line = m[1]
        out.append(line)
    cleaned, blank = [], 0
    for line in out:
        blank = blank + 1 if not line else 0
        if blank <= 1:
            cleaned.append(line)
    return "\n".join(cleaned).strip("\n") + "\n", stats


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    text, stats = normalize(src.read_bytes().decode("utf-8"))
    dst.write_text(text, encoding="utf-8", newline="\n")
    print(f"đã ghi {dst} ({text.count(chr(10))} dòng); đã bỏ: {stats}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
