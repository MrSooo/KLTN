"""L1: tách một văn bản lao động (.txt) thành các đơn vị, đọc đầu văn bản và nội dung trích dẫn sửa đổi.

Chạy: python -I src/parse.py <doc_id | đường dẫn file>     một văn bản
      python -I src/parse.py --all                          cả kho (và ghi documents.jsonl)

Đầu vào: file .txt trong data/raw/labor/ (UTF-8, mỗi đoạn một dòng) + dòng manifest.csv của nó.
Đầu ra (data/processed/l1/, mỗi văn bản một bộ):
  l1_triples_<doc_id>.jsonl    bộ ba (s,p,o) của từng đơn vị: type, number, heading, parent, text, scope, footnote, source_line
  l1_payloads_<doc_id>.jsonl   mỗi khối trích dẫn “…” đứng sau câu dẫn (nội dung sửa đổi cho L6): không là đơn vị của văn bản chứa nó
  l1_tables_<doc_id>.jsonl     bảng đã ghép lại (bảng lương vùng bị trải từng ô một dòng)
  l1_footnotes_<doc_id>.jsonl  chú thích [n] cuối văn bản hợp nhất
  documents.jsonl              thông tin mỗi văn bản (chỉ ghi khi chạy --all)
Báo cáo chữ: docs/bao_cao_chay/l1/l1_report_<doc_id>.txt.

Cổng: số Điều = cột so_dieu_dem_duoc của manifest; không còn dòng nghi ngờ; mọi mã khác nhau. Sai thì thoát mã 1, không ghi file.

Loại đơn vị: chuong, muc, dieu, khoan, diem (thân văn bản); pl (phụ lục), pl_muc (Mục / A. / I. trong phụ lục), pl_row (một dòng
của phụ lục). Mã: <doc_id>.C<La Mã>.M<n>, .D<n><hậu tố>, .K<n><hậu tố>, .<điểm> (đ viết thành dd), .PL<nhãn>.M<n>.L<chữ>.S<La Mã>.R<k>.
Quyết định chỗ spec im lặng: docs/quyet_dinh/l1_quyet_dinh.txt.
"""
import argparse
import collections
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import corpus

ROOT = corpus.ROOT
PROCESSED_DIR = corpus.PROCESSED_DIR
L1_DIR_NAME = "l1"

# Chữ của Điểm: bảng chữ trong văn bản luật (có đ, không có f j w z). Không dùng [a-z].
DIEM_LETTERS = "abcdđeghiklmnopq"

_L = DIEM_LETTERS
RE_DIEU = re.compile(r"^Điều (\d+[a-z]?)\.\s*(.*)$")
RE_KHOAN = re.compile(r"^(\d+[a-z]?)\.(?:\s+|(?=\[\d+\]))(.*)$")  # "8a.[2] ..." (văn bản hợp nhất) cũng là khoản; "4.960.000" thì không
RE_DIEM = re.compile(rf"^([{_L}]\d?)\)\s*(.*)$")
RE_CHUONG = re.compile(r"^Chương ([IVXLC]+)\.?\s*(.*)$")
RE_MUC = re.compile(r"^Mục (\d+)\.?\s*(.*)$")
RE_PHAN_LA = re.compile(r"^(Phần|Tiểu mục) \S+")  # kho không có; gặp thì báo, không đoán
RE_PL = re.compile(r"^(?:PHỤ LỤC|Phụ lục)\s+([IVX]+(?:\.\d+)?|\d+)\b\s*[:.\-–]?\s*(.*)$")
RE_PL_BARE = re.compile(r"^(?:PHỤ LỤC|Phụ lục)$")  # tiêu đề đứng một mình, nhãn/tiêu đề ở dòng sau (TT_10)
RE_KEMTHEO = re.compile(r"^\((?:Ban hành )?[Kk]èm theo\b")
RE_NOINHAN = re.compile(r"^Nơi nhận\b[:\s]*(.*)$")
RE_FOOTNOTE = re.compile(r"^\[(\d+)\]\s*(.*)$")
RE_FN_MARK = re.compile(r"\[(\d+)\]")
RE_DASH = re.compile(r"^[-–•]\s+")
RE_PLM = re.compile(r"^Mục (\d+)\.?\s*(.*)$")          # trong phụ lục
RE_PLL = re.compile(r"^([A-Z])\.\s+(\S.*)$")            # "A. LĨNH VỰC ..."
RE_PLS = re.compile(r"^([IVX]{1,6})\.\s*(\S.*)$")       # "I. Thời hạn ...", "VII.THÔNG TIN ..."
RE_SOHIEU = re.compile(r"(\d+(?:\.\d+)?/(?:\d{4}/)?[A-ZĐ][A-Za-zĐđ0-9\-]*)")

OPEN_Q, CLOSE_Q = "“", "”"
PL_RANK = {"M": 1, "L": 2, "S": 3}


class Anomaly(NamedTuple):
    line_no: int
    reason: str


@dataclass
class Unit:
    id: str
    type: str
    number: str
    heading: str | None
    parts: list
    source_line: int
    parent: str | None = None
    scope: str | None = None  # chỉ phụ lục: "out_of_scope" khi không bóc chi tiết
    fn: list = field(default_factory=list)  # số chú thích [n] gắn với đơn vị (văn bản hợp nhất)

    @property
    def text(self):
        return "\n".join(self.parts)


@dataclass
class Payload:
    payload_id: str
    first_line: int
    last_line: int
    lead_text: str     # dòng đứng ngay trước khối (câu dẫn, thường kết thúc "như sau:")
    lead_line: int
    lead_unit: str | None  # đơn vị đang mở lúc gặp khối
    lines: list = field(default_factory=list)  # nguyên dòng, còn dấu nháy


class Parsed(NamedTuple):
    doc_id: str
    units: list
    payloads: list
    footnotes: list     # [(số, chữ)]
    tables: list
    header: dict
    errors: list        # list[Anomaly]; sau khi parse xong phải rỗng
    notes: list         # para đứng ngay sau một Điểm
    skipped: collections.Counter  # lý do bỏ qua -> số dòng
    scan: dict          # kết quả quét ký tự của file nguồn


def normalize_line(s):
    """NFC, \\xa0 -> dấu cách, bỏ khoảng trắng cuối dòng, gộp khoảng trắng liền nhau."""
    s = unicodedata.normalize("NFC", s).replace("\xa0", " ")
    return re.sub(r"[ \t]+", " ", s).strip()


def scan_source(text):
    """Quét file thô: BOM, CRLF, dòng chưa NFC, ký tự điều khiển. Chỉ để báo cáo; parse tự chuẩn hoá."""
    nfc_bad = sum(1 for l in text.split("\n") if unicodedata.normalize("NFC", l) != l)
    odd = collections.Counter(c for c in text if unicodedata.category(c) in ("Cc", "Cf") and c not in "\n\r\t﻿")
    return {"bom": text.startswith("﻿"), "crlf": text.count("\r\n"), "dong_chua_nfc": nfc_bad,
            "ky_tu_dieu_khien": {hex(ord(k)): v for k, v in odd.items()}, "markdown_heading": len(re.findall(r"(?m)^#{1,6} ", text))}


def read_lines(path):
    """Đọc file, trả về (danh sách dòng đã chuẩn hoá, kết quả scan_source). Không giả định \\r\\n."""
    with open(path, encoding="utf-8", newline="") as f:
        raw = f.read()
    scan = scan_source(raw)
    text = raw.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return [normalize_line(l) for l in lines], scan


def diem_code(label):
    """Chữ Điểm khi ghép mã: đ -> dd (number vẫn lưu đ)."""
    return label.replace("đ", "dd")


def has_lower(s):
    return any(c.islower() for c in s)


def is_title_line(line):
    """Dòng tiêu đề viết hoa toàn bộ (Chương/Mục có tiêu đề ở dòng kế)."""
    return bool(line) and not has_lower(line) and not RE_DIEU.match(line) and not RE_CHUONG.match(line) \
        and not RE_MUC.match(line)


def next_number_ok(prev, cur):
    """Số hiệu liền sau: (n+1) hoặc cùng n với hậu tố chữ kế tiếp ('' -> a -> b). prev None: nhận mọi giá trị."""
    if prev is None:
        return True
    pm, cm = re.fullmatch(r"(\d+)([a-z]?)", prev), re.fullmatch(r"(\d+)([a-z]?)", cur)
    if not pm or not cm:
        return False
    pn, ps, cn, cs = int(pm[1]), pm[2], int(cm[1]), cm[2]
    if cn == pn + 1 and not cs:
        return True
    if cn == pn and cs:
        return cs == ("a" if not ps else chr(ord(ps) + 1))
    return False


def next_letter_ok(prev, cur):
    """Chữ Điểm liền sau trong DIEM_LETTERS; a1 sau a, a2 sau a1. prev None: nhận mọi giá trị."""
    if prev is None:
        return True
    pl, pd = prev[0], prev[1:]
    cl, cd = cur[0], cur[1:]
    if cl == pl:
        return cd.isdigit() and (int(cd) == (int(pd) + 1 if pd else 1))
    return not cd and DIEM_LETTERS.index(cl) == DIEM_LETTERS.index(pl) + 1


class Parser:
    """Máy trạng thái duyệt các dòng đã chuẩn hoá, dựng thân văn bản rồi phụ lục."""

    def __init__(self, doc_id, lines):
        self.doc_id = doc_id
        self.lines = lines
        self.units, self.payloads, self.footnotes, self.errors = [], [], [], []
        self.notes, self.skipped = [], collections.Counter()
        self.header_lines = []
        self.ids = set()
        self.consumed = set()
        self.chuong = self.muc = self.dieu = self.khoan = self.diem = None
        self.last = {"dieu": None, "khoan": None, "diem": None}
        self.pl_start = None
        self.footnote_start = None
        self.in_footer = False
        self.in_head = True
        self.has_fn = any(RE_FOOTNOTE.match(l) and RE_FOOTNOTE.match(l)[1] == "1" for l in lines)

    # ---- tiện ích ----
    def err(self, line_no, reason):
        self.errors.append(Anomaly(line_no, reason))

    def add(self, unit):
        if unit.id in self.ids:
            self.err(unit.source_line, f"mã lặp: {unit.id}")
        self.ids.add(unit.id)
        self.units.append(unit)
        return unit

    def prev_nonblank(self, i):
        j = i - 1
        while j >= 0 and not self.lines[j]:
            j -= 1
        return j

    def next_nonblank(self, i):
        j = i + 1
        while j < len(self.lines) and not self.lines[j]:
            j += 1
        return j if j < len(self.lines) else None

    def kemtheo_titles(self):
        """{chỉ số dòng tiêu đề: chỉ số dòng '(Kèm theo ...)'}: phụ lục không có nhãn 'Phụ lục' (TT_11, TT_19).
        Chỉ xét trước phụ lục có nhãn đầu tiên: sau đó dòng '(Kèm theo ...)' là phụ đề của mẫu/phụ lục đang mở."""
        first_explicit = next((i for i, l in enumerate(self.lines) if self.is_pl_heading(l)), len(self.lines))
        out = {}
        for i, line in enumerate(self.lines[:first_explicit]):
            if RE_KEMTHEO.match(line):
                j = self.prev_nonblank(i)
                if j >= 0 and is_title_line(self.lines[j]):
                    out[j] = i
        return out

    def is_pl_heading(self, line):
        if RE_PL_BARE.match(line):
            return True
        m = RE_PL.match(line)
        if not m:
            return False
        rest = m[2]
        return not rest or not has_lower(rest) or len(rest) <= 80

    def strip_fn(self, line):
        """Gỡ dấu chú thích [n] khỏi dòng (chỉ ở văn bản có chú thích cuối trang). Trả (dòng sạch, [n])."""
        if not self.has_fn:
            return line, []
        refs = [int(n) for n in RE_FN_MARK.findall(line)]
        return re.sub(r"\s+", " ", RE_FN_MARK.sub("", line)).strip(), refs

    # ---- thân văn bản ----
    def run(self):
        L = self.lines
        kem = self.kemtheo_titles()
        depth = 0
        payload = None
        i = 0
        while i < len(L):
            line, no = L[i], i + 1
            if payload is not None:  # trong khối trích dẫn: nuốt dòng đến khi nháy cân bằng
                payload.lines.append(line)
                payload.last_line = no
                depth += line.count(OPEN_Q) - line.count(CLOSE_Q)
                if depth <= 0:
                    if depth < 0:
                        self.err(no, "nháy đóng thừa trong khối trích dẫn")
                    self.payloads.append(payload)
                    payload, depth = None, 0
                i += 1
                continue
            if not line or i in self.consumed:
                i += 1
                continue
            if RE_FOOTNOTE.match(line) and RE_FOOTNOTE.match(line)[1] == "1":
                self.footnote_start = i
                break
            if i in kem or self.is_pl_heading(line):
                self.pl_start = i
                break
            m = RE_NOINHAN.match(line)
            if m:
                self.skipped["nơi nhận / chữ ký"] += 1
                self.in_footer = not m[1].strip()  # "Nơi nhận: - A; - B" một dòng: bỏ đúng dòng đó
                i += 1
                continue
            if self.in_footer:
                if RE_DIEU.match(line) or RE_CHUONG.match(line):
                    self.in_footer = False
                else:
                    self.skipped["nơi nhận / chữ ký"] += 1
                    i += 1
                    continue
            if line.startswith(OPEN_Q):
                opens, closes = line.count(OPEN_Q), line.count(CLOSE_Q)
                prev = L[self.prev_nonblank(i)] if self.prev_nonblank(i) >= 0 else ""
                if opens > closes or prev.endswith(":"):
                    payload = self.start_payload(i, line)
                    depth = opens - closes
                    if depth <= 0:  # khối một dòng
                        self.payloads.append(payload)
                        payload, depth = None, 0
                    i += 1
                    continue
            elif line.count(OPEN_Q) != line.count(CLOSE_Q):
                self.err(no, f"nháy “ ” không cân bằng trong dòng: {line[:60]!r}")
            self.token(i, line)
            i += 1
        if payload is not None:
            self.err(payload.first_line, "khối trích dẫn mở nháy nhưng không đóng đến hết văn bản")
        if self.footnote_start is not None:
            self.parse_footnotes(self.footnote_start)
        return self

    def start_payload(self, i, line):
        j = self.prev_nonblank(i)
        lead = self.lines[j] if j >= 0 else ""
        unit = (self.diem or self.khoan or self.dieu)
        p = Payload(f"{self.doc_id}.Q{len(self.payloads) + 1}", i + 1, i + 1, lead, j + 1,
                    unit.id if unit else None)
        p.lines.append(line)
        return p

    def title_after(self, i, title):
        """Tiêu đề Chương/Mục: phần cùng dòng, hoặc dòng viết hoa kế tiếp; tiếp tục nối các dòng viết hoa liền sau
        (tiêu đề dài bị xuống dòng, ND_28 Chương IV)."""
        j = self.next_nonblank(i)
        while j is not None and is_title_line(self.lines[j]) and not RE_PL.match(self.lines[j]) \
                and (not title or title.rstrip()[-1:] not in ".;") and j not in self.consumed:
            title = f"{title} {self.lines[j]}".strip()
            self.consumed.add(j)
            j = self.next_nonblank(j)
        return title

    def token(self, i, line):
        """Phân loại một dòng thân văn bản và gắn vào cây đơn vị; chú thích [n] gỡ khỏi chữ và ghi vào đơn vị."""
        line, refs = self.strip_fn(line)
        if not line:
            return
        unit = self._token(i, line)
        if unit is not None and refs:
            unit.fn.extend(n for n in refs if n not in unit.fn)

    def _token(self, i, line):
        no = i + 1
        m = RE_CHUONG.match(line)
        if m:
            self.in_head = False
            title = self.title_after(i, m[2])
            uid = f"{self.doc_id}.C{m[1]}"
            if uid in self.ids and self.doc_id in corpus.DUP_CHUONG_OK:  # lỗi đánh số của nguồn (ND_145: hai Chương XI)
                self.notes.append(f"dòng {no}: nguồn lặp nhãn Chương {m[1]}, mã đổi thành {uid}_2")
                uid += "_2"
            self.chuong = self.add(Unit(uid, "chuong", m[1], title or None, [], no))
            self.muc = self.dieu = self.khoan = self.diem = None
            return self.chuong
        m = RE_MUC.match(line)
        if m:
            self.in_head = False
            title = self.title_after(i, m[2])
            base = f"{self.chuong.id}." if self.chuong else f"{self.doc_id}."
            self.muc = self.add(Unit(f"{base}M{m[1]}", "muc", m[1], title or None, [], no,
                                     self.chuong.id if self.chuong else None))
            self.dieu = self.khoan = self.diem = None
            return self.muc
        if RE_PHAN_LA.match(line):
            self.err(no, f"cấp Phần / Tiểu mục chưa được hỗ trợ: {line[:50]!r}")
            return None
        m = RE_DIEU.match(line)
        if m:
            self.in_head = False
            if not next_number_ok(self.last["dieu"], m[1]):
                self.err(no, f"Điều {m[1]} sau Điều {self.last['dieu']}")
            parent = (self.muc or self.chuong)
            self.dieu = self.add(Unit(f"{self.doc_id}.D{m[1]}", "dieu", m[1], m[2], [], no, parent.id if parent else None))
            self.last.update(dieu=m[1], khoan=None, diem=None)
            self.khoan = self.diem = None
            return self.dieu
        if self.in_head:
            self.header_lines.append(line)
            return None
        if self.dieu is None:
            self.err(no, f"dòng chữ khi chưa có Điều: {line[:50]!r}")
            return None
        m = RE_KHOAN.match(line)
        if m:
            if not next_number_ok(self.last["khoan"], m[1]):
                self.err(no, f"Khoản {m[1]} sau Khoản {self.last['khoan']} (Điều {self.dieu.number})")
            self.khoan = self.add(Unit(f"{self.dieu.id}.K{m[1]}", "khoan", m[1], None, [m[2]] if m[2] else [], no, self.dieu.id))
            self.last.update(khoan=m[1], diem=None)
            self.diem = None
            return self.khoan
        m = RE_DIEM.match(line)
        if m:
            parent = self.khoan or self.dieu  # Điều có điểm đứng thẳng dưới Điều (không Khoản): mã D1.a (ND_283 Điều 1)
            if not next_letter_ok(self.last["diem"], m[1]):
                self.err(no, f"Điểm {m[1]} sau điểm {self.last['diem']} (Điều {self.dieu.number}"
                             f"{', Khoản ' + self.khoan.number if self.khoan else ''})")
            self.diem = self.add(Unit(f"{parent.id}.{diem_code(m[1])}", "diem", m[1], None, [m[2]] if m[2] else [], no, parent.id))
            self.last["diem"] = m[1]
            return self.diem
        # đoạn chữ không nhãn: gạch đầu dòng vào đơn vị sâu nhất; còn lại vào Khoản (chưa có thì Điều)
        target = (self.diem or self.khoan or self.dieu) if RE_DASH.match(line) else (self.khoan or self.dieu)
        if self.diem is not None and not RE_DASH.match(line):
            self.notes.append(f"{target.id}, dòng {no}: đoạn chữ ngay sau một Điểm, gắn vào {target.id}")
        target.parts.append(line)
        return target

    # ---- chú thích [n] ----
    def parse_footnotes(self, start):
        cur = None
        for i in range(start, len(self.lines)):
            line = self.lines[i]
            if not line:
                continue
            m = RE_FOOTNOTE.match(line)
            if m:
                cur = [int(m[1]), [m[2]]]
                self.footnotes.append(cur)
            elif cur is not None:
                cur[1].append(line)  # dòng sau [n] (kể cả dòng trông như khoản) là chữ của chú thích
        self.footnotes = [(n, "\n".join(parts)) for n, parts in self.footnotes]
        nums = [n for n, _ in self.footnotes]
        if nums != list(range(1, len(nums) + 1)):
            self.err(start + 1, f"chú thích không liên tục: {nums}")

    # ---- phụ lục ----
    def parse_appendices(self, in_scope):
        if self.pl_start is None:
            return
        L = self.lines
        end = self.footnote_start if self.footnote_start is not None else len(L)
        kem = self.kemtheo_titles()
        # chia đoạn [pl_start, end) theo dòng tiêu đề phụ lục
        starts = [i for i in range(self.pl_start, end) if i in kem or self.is_pl_heading(L[i])]
        blocks = []
        for k, s in enumerate(starts):
            blocks.append((s, starts[k + 1] if k + 1 < len(starts) else end))
        seq = 0
        parsed = []
        for s, e in blocks:
            head = L[s]
            m = RE_PL.match(head)
            if m:
                label, rest = m[1], m[2]
            else:
                seq += 1
                # không nhãn: "PHỤ LỤC" đứng một mình (tiêu đề ở dòng sau) hoặc dòng viết hoa đứng trước "(Kèm theo ...)"
                label, rest = f"_{seq}", ("" if RE_PL_BARE.match(head) else head)
            parsed.append([label.replace(".", "_"), rest, s, e])
        # mục lục: khối "Phụ lục X" chỉ có tiêu đề (<= 3 dòng chữ) mà nhãn đó còn xuất hiện lại về sau -> bỏ khối mục lục
        keep = []
        for k, (label, rest, s, e) in enumerate(parsed):
            body = [x for x in L[s + 1:e] if x]
            if len(body) <= 3 and any(p[0] == label for p in parsed[k + 1:]):
                self.skipped["mục lục phụ lục"] += len(body) + 1
                continue
            keep.append((label, rest, s, e))
        for label, rest, s, e in keep:
            self.parse_one_appendix(label, rest, s, e, in_scope)

    def parse_one_appendix(self, label, rest, s, e, in_scope):
        L = self.lines
        pl_id = f"{self.doc_id}.PL{label}"
        title_lines = [rest] if rest else []
        j = s + 1
        # tiêu đề: dòng viết hoa kế tiếp và dòng "(Kèm theo ...)" nếu có
        while j < e and not L[j]:
            j += 1
        bare = RE_PL_BARE.match(L[s]) is not None
        if not rest and j < e and (bare or is_title_line(L[j])) and not RE_PLM.match(L[j]) and not RE_PLL.match(L[j]):
            title_lines.append(L[j])
            j += 1
        k = j
        while k < e and not L[k]:
            k += 1
        if k < e and RE_KEMTHEO.match(L[k]):
            title_lines.append(L[k])
            j = k + 1
        out = in_scope is not None and label not in in_scope
        pl = self.add(Unit(pl_id, "pl", label.replace("_", ".") if not label.startswith(".") else label, " ".join(title_lines) or None,
                           [], s + 1, None, "out_of_scope" if out else None))
        if out:
            self.skipped["phụ lục ngoài phạm vi (chỉ giữ nút)"] += sum(1 for x in L[j:e] if x)
            return
        stack = {}   # rank -> Unit
        row_no = collections.Counter()
        for idx in range(j, e):
            line = L[idx]
            if not line:
                continue
            kind = code = title = None
            m = RE_PLM.match(line)
            if m:
                kind, code, title = "M", m[1], m[2]
            else:
                m = RE_PLL.match(line)
                if m and not has_lower(m[2]):
                    kind, code, title = "L", m[1], m[2]
                else:
                    m = RE_PLS.match(line)
                    if m:
                        kind, code, title = "S", m[1], m[2]
            if kind:
                rank = PL_RANK[kind]
                for r in [r for r in stack if r >= rank]:
                    del stack[r]
                parent = stack[max(stack)] if stack else pl
                unit = self.add(Unit(f"{parent.id}.{kind}{code}", "pl_muc", code, title or None, [], idx + 1, parent.id))
                stack[rank] = unit
                continue
            parent = stack[max(stack)] if stack else pl
            row_no[parent.id] += 1
            self.add(Unit(f"{parent.id}.R{row_no[parent.id]}", "pl_row", str(row_no[parent.id]), None, [line], idx + 1, parent.id))


def rebuild_wage_tables(units):
    """Ghép bảng mức lương tối thiểu vùng bị trải mỗi ô một dòng: tiêu đề 'Vùng' / 'Mức ... tháng' / 'Mức ... giờ', rồi
    từng bộ ba (Vùng X, số tháng, số giờ). Trả list bảng; đơn vị giữ nguyên chữ gốc."""
    tables = []
    for u in units:
        if u.type not in ("khoan", "dieu"):
            continue
        p = u.parts
        for i in range(len(p) - 2):
            if p[i] == "Vùng" and p[i + 1].startswith("Mức lương tối thiểu tháng") and p[i + 2].startswith("Mức lương tối thiểu giờ"):
                rows, k = [], i + 3
                while k + 2 < len(p) + 0 and re.fullmatch(r"Vùng ([IVX]+)", p[k]):
                    thang, gio = p[k + 1].replace(".", ""), p[k + 2].replace(".", "")
                    if not (thang.isdigit() and gio.isdigit()):
                        break
                    rows.append({"vung": p[k][5:], "muc_thang": int(thang), "muc_gio": int(gio)})
                    k += 3
                if rows:
                    tables.append({"table_id": f"{u.id}.T{len(tables) + 1}", "unit": u.id,
                                   "columns": ["vung", "muc_thang", "muc_gio"], "rows": rows})
    return tables


def extract_header(doc, header_lines, units):
    """Thông tin đầu văn bản bằng regex, đối chiếu manifest. Lệch thì gắn cờ; mất đầu văn bản thì lấy từ manifest."""
    flags = []
    so = date = None
    for l in header_lines[:40]:
        m = RE_SOHIEU.search(l)
        if m and re.search(r"(?i)\bsố\b|luật số", l) and so is None:
            so = m[1]
        if date is None and not l.startswith("Căn cứ"):
            date = corpus.find_vn_date(l)
    grounds = [l for l in header_lines if l.startswith("Căn cứ")]
    if so is None and date is None:
        flags.append("header_from_manifest")  # TT_09, TT_10, TT_11 mất phần đầu
    else:
        if so is not None and re.sub(r"\s", "", so).lower() != re.sub(r"\s", "", doc.so_hieu).lower():
            flags.append(f"so_hieu_lech_manifest:{so}")
        if date is not None and doc.ngay_ban_hanh is not None and date != doc.ngay_ban_hanh:
            flags.append(f"ngay_ky_lech_manifest:{date.isoformat()}")
    if doc.issued_uncertain:
        flags.append("issued_uncertain")
    return {"doc_id": doc.doc_id, "number": doc.so_hieu, "doc_type": doc.doc_type, "issuer": doc.issuer, "level": doc.level,
            "issued": doc.ngay_ban_hanh.isoformat() if doc.ngay_ban_hanh else None,
            "effective_from": doc.ngay_hieu_luc.isoformat(), "title": doc.ten_ngan, "grounds": grounds, "flags": flags,
            "group": doc.nhom}


def parse_document(doc):
    """Đọc và parse một văn bản của manifest. Trả về Parsed; chưa kiểm cổng."""
    lines, scan = read_lines(doc.path)
    p = Parser(doc.doc_id, lines).run()
    p.parse_appendices(corpus.PL_IN_SCOPE.get(doc.doc_id))
    tables = rebuild_wage_tables(p.units)
    header = extract_header(doc, p.header_lines, p.units)
    n_dieu = sum(1 for u in p.units if u.type == "dieu")
    if n_dieu != doc.so_dieu:
        p.err(0, f"số Điều {n_dieu} khác manifest {doc.so_dieu}")
    return Parsed(doc.doc_id, p.units, p.payloads, p.footnotes, tables, header, p.errors, p.notes, p.skipped, scan)


# ---- ghi / đọc ----

def to_triples(units):
    """Mỗi đơn vị thành các bộ ba (s,p,o), p theo thứ tự: type, number, heading, parent, scope, footnote, text, source_line."""
    triples = []
    for u in sorted(units, key=lambda u: (u.source_line, u.id)):
        triples.append((u.id, "type", u.type))
        triples.append((u.id, "number", u.number))
        if u.heading is not None:
            triples.append((u.id, "heading", u.heading))
        if u.parent is not None:
            triples.append((u.id, "parent", u.parent))
        if u.scope is not None:
            triples.append((u.id, "scope", u.scope))
        for n in u.fn:
            triples.append((u.id, "footnote", n))
        if u.parts:
            triples.append((u.id, "text", u.text))
        triples.append((u.id, "source_line", u.source_line))
    return triples


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def l1_dir():
    return corpus.out_dir(L1_DIR_NAME)


def triples_path(doc_id):
    return l1_dir() / f"l1_triples_{doc_id}.jsonl"


def load_units(doc_id):
    """Đọc lại l1_triples: {id: {type, number, heading, parent, text, scope, footnote, source_line}} theo thứ tự file."""
    units = collections.OrderedDict()
    for t in read_jsonl(triples_path(doc_id)):
        u = units.setdefault(t["s"], {"id": t["s"]})
        if t["p"] == "footnote":  # một đơn vị có thể mang nhiều chú thích
            u.setdefault("footnote", []).append(t["o"])
        else:
            u[t["p"]] = t["o"]
    return units


def load_payloads(doc_id):
    return read_jsonl(l1_dir() / f"l1_payloads_{doc_id}.jsonl")


def report_text(doc, parsed):
    ty = collections.Counter(u.type for u in parsed.units)
    out = [f"L1 báo cáo: {doc.doc_id} ({doc.so_hieu})", f"file: {doc.path.relative_to(ROOT).as_posix()}",
           f"số đơn vị theo loại: {dict(ty)}", f"số Điều: {ty['dieu']} (manifest {doc.so_dieu})",
           f"khối trích dẫn: {len(parsed.payloads)}  chú thích: {len(parsed.footnotes)}  bảng ghép: {len(parsed.tables)}",
           f"cờ đầu văn bản: {parsed.header['flags'] or 'không'}", f"dòng bỏ qua có chủ đích: {dict(parsed.skipped) or 'không'}",
           f"quét file nguồn: {parsed.scan}", f"đoạn chữ ngay sau một Điểm (gắn vào Khoản): {len(parsed.notes)}",
           f"lỗi parse: {len(parsed.errors)}"]
    out += [f"  dòng {e.line_no}: {e.reason}" for e in parsed.errors]
    return "\n".join(out) + "\n"


def write_outputs(doc, parsed):
    d = l1_dir()
    write_jsonl(triples_path(doc.doc_id), [{"s": s, "p": p, "o": o} for s, p, o in to_triples(parsed.units)])
    write_jsonl(d / f"l1_payloads_{doc.doc_id}.jsonl",
                [{"payload_id": p.payload_id, "first_line": p.first_line, "last_line": p.last_line, "lead_text": p.lead_text,
                  "lead_line": p.lead_line, "lead_unit": p.lead_unit, "lines": p.lines} for p in parsed.payloads])
    write_jsonl(d / f"l1_tables_{doc.doc_id}.jsonl", parsed.tables)
    write_jsonl(d / f"l1_footnotes_{doc.doc_id}.jsonl", [{"n": n, "text": t} for n, t in parsed.footnotes])


def write_report(doc, parsed):
    path = corpus.report_dir(L1_DIR_NAME) / f"l1_report_{doc.doc_id}.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report_text(doc, parsed), encoding="utf-8", newline="\n")
    return path


def run_doc(doc):
    """Parse + kiểm cổng + ghi. Lỗi parse: chỉ ghi báo cáo, trả (parsed, False)."""
    parsed = parse_document(doc)
    write_report(doc, parsed)
    if parsed.errors:
        return parsed, False
    write_outputs(doc, parsed)
    return parsed, True


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("target", nargs="?", help="doc_id hoặc đường dẫn file .txt")
    ap.add_argument("--all", action="store_true", help="cả kho, ghi documents.jsonl")
    args = ap.parse_args(argv)
    docs = corpus.load_manifest()
    if args.all:
        targets = list(docs.values())
    elif args.target:
        targets = [corpus.get_doc(Path(args.target).stem if Path(args.target).suffix else args.target, docs)]
    else:
        ap.error("cần doc_id/đường dẫn hoặc --all")
    bad, headers = [], []
    for doc in targets:
        parsed, ok = run_doc(doc)
        ty = collections.Counter(u.type for u in parsed.units)
        print(f"{doc.doc_id:<22} Điều {ty['dieu']:>4}/{doc.so_dieu:<4} Khoản {ty['khoan']:>4} Điểm {ty['diem']:>4} "
              f"PL {ty['pl']:>2} hàng PL {ty['pl_row']:>5} trích dẫn {len(parsed.payloads):>3}  {'OK' if ok else 'LỖI ' + str(len(parsed.errors))}")
        if not ok:
            bad.append((doc, parsed))
        headers.append(parsed.header)
    if bad:
        for doc, parsed in bad:
            print(f"\nLỖI PARSE {doc.doc_id}:", file=sys.stderr)
            for e in parsed.errors[:30]:
                print(f"  dòng {e.line_no}: {e.reason}", file=sys.stderr)
        raise SystemExit(1)
    if args.all:
        write_jsonl(PROCESSED_DIR / "documents.jsonl", headers)
        print(f"đã ghi {PROCESSED_DIR / 'documents.jsonl'} ({len(headers)} văn bản)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()
