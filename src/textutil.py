"""Tiện ích chữ dùng chung cho mọi bước.

Trước đây `text_norm` nằm trong l6_versions.py (bước kho phiên bản), nên bước loại Điều phải import từ bước đó chỉ để dùng một hàm chuẩn
hoá chữ. Để ở đây thì bước nào cần cũng import được mà không kéo theo bước khác.
"""
import re
import unicodedata

# Các cặp kiểu đặt dấu thanh coi là một (hòa/hoà, ủy/uỷ). Công khai vì l6_directives.py cũng dùng để dựng regex khớp mềm.
TONE = (("òa", "oà"), ("óa", "oá"), ("ỏa", "oả"), ("õa", "oã"), ("ọa", "oạ"),
        ("ùy", "uỳ"), ("úy", "uý"), ("ủy", "uỷ"), ("ũy", "uỹ"), ("ụy", "uỵ"))


def text_norm(s):
    """Khoá so sánh hai bản chữ: NFC, casefold, thống nhất kiểu đặt dấu thanh (hòa/hoà, ủy/uỷ), bỏ [n], thống nhất gạch, bỏ mọi
    khoảng trắng (gồm dính chữ và khoảng trắng sau nháy), bỏ dấu câu cuối."""
    s = unicodedata.normalize("NFC", s or "").casefold()
    s = re.sub(r"\[\d+\]", "", s)
    s = s.replace("–", "-").replace("—", "-").replace("−", "-")
    for a, b in TONE:
        s = s.replace(a, b)
    return re.sub(r"\s+", "", s).rstrip(".;:,")
