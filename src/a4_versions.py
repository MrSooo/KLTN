"""A4: cơ chế cập nhật có phiên bản cho lớp văn bản (BLDS 2015, đơn vị Điều / Khoản / Điểm).

Chạy: python -I src/a4_versions.py apply --base <md gốc> --amend DOC [--amend DOC2 ...]
                                  [--effective-from YYYY-MM-DD] [--doc-id ID] [--name NAME]
      python -I src/a4_versions.py snapshot --name NAME --date YYYY-MM-DD [--out PATH]

apply: nạp văn bản gốc (a1.load_parsed) và cạnh gốc của A2/A3 (chỉ đọc), áp từng văn bản sửa đổi theo ngày hiệu lực.
  Không lỗi: ghi data/processed/a4_<name>_{versions,amend_edges,edge_changes}.jsonl, a4_<name>_{changed,impact}.json
  và docs/a4_report_<name>.txt, thoát 0. Có lỗi (bất kỳ kiểm nào): chỉ ghi docs/a4_report_<name>.txt, thoát 1.
snapshot: đơn vị đang hiệu lực tại ngày T, xuất Markdown cùng quy ước với file BLDS gốc (stdout hoặc --out).

Hiệu lực là nửa khoảng [effective_from, effective_to): đang hiệu lực tại T nếu (from null hoặc <= T) và (to null hoặc > T).
Mọi quyết định chỗ spec chưa nói nằm trong docs/a4_quyet_dinh.txt.
"""
import argparse
import collections
import datetime
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import a1_parse as a1
import a2_edges as a2
import a3_exceptions as a3

ROOT = a1.ROOT
IN_DIR = a2.PROCESSED_DIR     # file A1/A2/A3 đã sinh, chỉ đọc
OUT_DIR = a2.PROCESSED_DIR    # file dữ liệu A4 (test đổi sang thư mục tạm)
DOCS_DIR = ROOT / "docs"
DOC_PREFIX = a1.DOC_PREFIX

# A2/A3 nhận mã có hậu tố chữ làm nguồn (đã thử, khoá bằng test_a2_a3_accept_suffix_codes). Đặt False thì đơn vị
# có hậu tố bị loại khỏi tập đưa vào A2/A3 và được liệt kê ở mục "chưa tính cạnh (mã có hậu tố)" của báo cáo.
A2A3_ACCEPT_SUFFIX = True

REFERS, EXCEPTION = "refers_to", "exception_of"
CONTAINS, PART_OF = "contains", "part_of"


class A4Error(Exception):
    """Lỗi kiểm của A4: code (mã lỗi) và message; doc / line_no / line được điền dần khi lỗi đi qua các tầng."""

    def __init__(self, code, message, line_no=None, line=None, doc=None):
        super().__init__(f"{code}: {message}")
        self.code, self.message, self.line_no, self.line, self.doc = code, message, line_no, line, doc


def normalize_unknown_line(line):
    """Móc cho tầng chuẩn hoá dòng lạ (sau này gắn LLM). Trả về dòng chỉ thị chuẩn hoặc None.

    Mặc định trả None, tức là dòng lạ là LỖI (không đoán). Dòng trả về phải parse được thành một chỉ thị.
    """
    return None


# ---- mã đơn vị ----

def parent_code(code):
    """Cha của một mã bằng cách bỏ đoạn cuối; Điều (2 đoạn) không có cha."""
    parts = code.split(".")
    return None if len(parts) <= 2 else ".".join(parts[:-1])


def seg_key(seg):
    """Khoá sắp xếp một đoạn mã: Điều/Khoản theo (số, hậu tố), Điểm theo a1.DIEM_LETTERS."""
    m = re.fullmatch(r"[DK](\d+)([a-z]?)", seg)
    if m:
        return (1, int(m[1]), m[2])
    letter = "đ" if seg == "dd" else seg
    if len(letter) == 1 and letter in a1.DIEM_LETTERS:
        return (2, a1.DIEM_LETTERS.index(letter), "")
    return (0, 0, seg)


def code_key(code):
    return tuple(seg_key(s) for s in code.split("."))


def unit_of_code(code):
    """(type, number) từ đoạn cuối của mã: D621a -> (dieu, 621a), K2 -> (khoan, 2), dd -> (diem, đ)."""
    seg = code.split(".")[-1]
    m = re.fullmatch(r"([DK])(\d+[a-z]?)", seg)
    if m:
        return ("dieu" if m[1] == "D" else "khoan"), m[2]
    letter = "đ" if seg == "dd" else seg
    if len(letter) == 1 and letter in a1.DIEM_LETTERS:
        return "diem", letter
    raise A4Error("E_CODE", f"mã không hợp lệ: {code!r}")


def child_code(parent, kind, number):
    if kind == "khoan":
        return f"{parent}.K{number}"
    return f"{parent}.{a1.diem_code(number)}"


def has_suffix(code):
    """Mã có đoạn Điều/Khoản mang hậu tố chữ (D621a, K2a)."""
    return any(re.fullmatch(r"[DK]\d+[a-z]", s) for s in code.split("."))


def overlaps(a, b):
    """Hai mã bằng nhau hoặc một mã là tổ tiên của mã kia."""
    return a == b or a.startswith(b + ".") or b.startswith(a + ".")


# ---- chuẩn hoá văn bản sửa đổi, ngày hiệu lực ----

def norm_line(s):
    """NFC, \\xa0 -> dấu cách, gộp khoảng trắng."""
    s = unicodedata.normalize("NFC", s).replace("\xa0", " ")
    return re.sub(r"\s+", " ", s).strip()


def split_lines(text):
    """[(số dòng từ 1, dòng đã chuẩn hoá)], giữ dòng trống để phân biệt đoạn mới."""
    text = text.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return [(i, norm_line(line)) for i, line in enumerate(lines, 1)]


RE_EFFECTIVE = re.compile(r"có hiệu lực(?: thi hành)?(?: kể)? từ ngày (\d{1,2}) tháng (\d{1,2}) năm (\d{4})", re.I)


def parse_iso(s):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", s or ""):
        raise A4Error("E_ARGS", f"ngày phải có dạng YYYY-MM-DD: {s!r}")
    try:
        return datetime.date.fromisoformat(s)
    except ValueError:
        raise A4Error("E_ARGS", f"ngày không hợp lệ: {s!r}")


def find_effective_date(text, flag=None):
    """Ngày hiệu lực của văn bản: đúng một ngày (khớp trùng ngày tính một); flag, nếu có, phải trùng ngày trong văn bản."""
    dates = set()
    for d, m, y in RE_EFFECTIVE.findall(norm_line(text)):
        try:
            dates.add(datetime.date(int(y), int(m), int(d)))
        except ValueError:
            raise A4Error("E_DATE_INVALID", f"ngày hiệu lực không hợp lệ: {d}/{m}/{y}")
    if len(dates) > 1:
        raise A4Error("E_DATE_CONFLICT", f"văn bản có nhiều hơn một ngày hiệu lực: {sorted(d.isoformat() for d in dates)}")
    if flag is not None:
        want = parse_iso(flag)
        if dates and want not in dates:
            raise A4Error("E_DATE_FLAG", f"--effective-from {flag} khác ngày hiệu lực trong văn bản {next(iter(dates)).isoformat()}")
        return want
    if not dates:
        raise A4Error("E_NO_DATE", "văn bản không có ngày hiệu lực và không có --effective-from")
    return dates.pop()


# ---- danh sách đích (REFLIST) ----

class Ref(NamedTuple):
    dieu: str
    khoan: str | None = None
    diem: str | None = None


_N = r"\d+[a-z]?(?!\w)"
_P = r"[a-zđ](?!\w)"
_LAW = r"(?: của Bộ luật (?:dân sự|này))?"
_NLIST = rf"{_N}(?:, {_N})*(?: và {_N})?"
_PLIST = rf"{_P}(?:, {_P})*(?: và {_P})?"
_UREF = rf"(?:điểm {_P} )?(?:khoản {_N} )?Điều {_N}{_LAW}"
RE_UREF = re.compile(rf"(?:điểm ({_P}) )?(?:khoản ({_N}) )?Điều ({_N}){_LAW}(?!\w)", re.I)
RE_G_DIEU = re.compile(rf"các điều ({_NLIST})(?!\w)", re.I)
RE_G_KHOAN = re.compile(rf"(?:các )?khoản ({_NLIST}) Điều ({_N}){_LAW}(?!\w)", re.I)
RE_G_DIEM = re.compile(rf"(?:các )?điểm ({_PLIST})(?: khoản ({_N}))? Điều ({_N}){_LAW}(?!\w)", re.I)
RE_SEP = re.compile(r", |; | và ")


def _ref(dieu, khoan=None, diem=None, where=""):
    diem = diem.lower() if diem else None
    if diem and diem not in a1.DIEM_LETTERS:
        raise A4Error("E_REFLIST", f"điểm {diem} không thuộc bảng chữ của Điểm {where}")
    if diem and not khoan:
        raise A4Error("E_REFLIST", f"điểm {diem} phải kèm khoản {where}")
    return Ref(dieu.lower(), khoan.lower() if khoan else None, diem)


def _items(s):
    return [x.lower() for x in re.split(r", | và ", s)]


def _match_group(text, pos):
    """Nhóm dài trước, rồi UREF. Trả về (list Ref, vị trí hết nhóm) hoặc None."""
    m = RE_G_DIEU.match(text, pos)
    if m:
        return [_ref(n, where=m[0]) for n in _items(m[1])], m.end()
    m = RE_G_KHOAN.match(text, pos)
    if m:
        return [_ref(m[2], k, where=m[0]) for k in _items(m[1])], m.end()
    m = RE_G_DIEM.match(text, pos)
    if m:
        return [_ref(m[3], m[2], p, where=m[0]) for p in _items(m[1])], m.end()
    m = RE_UREF.match(text, pos)
    if m:
        return [_ref(m[3], m[2], m[1], where=m[0])], m.end()
    return None


def parse_reflist(text):
    """Danh sách đích: một hoặc nhiều nhóm nối bằng ', ' / '; ' / ' và '. Không bắt một phần: sau nhóm phải là dấu nối hoặc hết chuỗi."""
    text = norm_line(text)
    refs, pos = [], 0
    while True:
        found = _match_group(text, pos)
        if found is None:
            raise A4Error("E_REFLIST", f"không đọc được danh sách đích tại {text[pos:]!r} (trong {text!r})")
        group, end = found
        refs += group
        if end == len(text):
            return refs
        sep = RE_SEP.match(text, end)
        if sep is None:
            raise A4Error("E_REFLIST", f"danh sách đích chỉ khớp một phần: {text[:end]!r} còn thừa {text[end:]!r}")
        pos = sep.end()


def parse_uref(text):
    refs = parse_reflist(text)
    if len(refs) != 1 or not RE_UREF.fullmatch(norm_line(text)):
        raise A4Error("E_REFLIST", f"cần đúng một đích: {text!r}")
    return refs[0]


def ref_code(ref):
    code = f"{DOC_PREFIX}.D{ref.dieu}"
    if ref.khoan:
        code += f".K{ref.khoan}"
    if ref.diem:
        code += "." + a1.diem_code(ref.diem)
    return code


def ref_kind(ref):
    return "diem" if ref.diem else "khoan" if ref.khoan else "dieu"


# ---- cây nội dung trong nháy ----

@dataclass
class Node:
    kind: str                 # dieu | khoan | diem
    number: str
    heading: str | None       # chỉ Điều
    parts: list = field(default_factory=list)
    children: list = field(default_factory=list)
    line_no: int = 0


RE_B_DIEU = re.compile(r"^Điều\s+(\d+[a-z]?)\s*\.\s*(.*)$")
RE_B_KHOAN = re.compile(r"^(\d+[a-z]?)\s*\.\s+(.*)$")
RE_B_DIEM = re.compile(r"^([a-zđ])\)\s+(.*)$")
LEVEL = {"dieu": 0, "khoan": 1, "diem": 2}


def _label(text):
    m = RE_B_DIEU.match(text)
    if m:
        return "dieu", m[1], m[2]
    m = RE_B_KHOAN.match(text)
    if m:
        return "khoan", m[1], m[2]
    m = RE_B_DIEM.match(text)
    if m:
        return "diem", m[1], m[2]
    return None


def _khoan_key(number):
    m = re.fullmatch(r"(\d+)([a-z]?)", number)
    return int(m[1]), m[2]


def _check_order(prev, node):
    """Khoản liên tiếp (2, 2a, 2b, 3; con đầu là 1), Điểm liên tiếp theo a1.DIEM_LETTERS (con đầu là a)."""
    if node.kind == "diem":
        if node.number not in a1.DIEM_LETTERS:
            raise A4Error("E_ORDER", f"điểm {node.number} không thuộc bảng chữ của Điểm", node.line_no)
        want = 0 if prev is None else a1.DIEM_LETTERS.index(prev.number) + 1
        got = a1.DIEM_LETTERS.index(node.number)
        if got != want:
            wl = a1.DIEM_LETTERS[want] if want < len(a1.DIEM_LETTERS) else "(hết bảng chữ)"
            raise A4Error("E_ORDER", f"điểm {node.number}, mong đợi điểm {wl}", node.line_no)
        return
    n, s = _khoan_key(node.number)
    if prev is None:
        ok = (n, s) == (1, "")
        want = "khoản 1"
    else:
        pn, ps = _khoan_key(prev.number)
        nxt = "a" if ps == "" else chr(ord(ps) + 1) if ps < "z" else None
        ok = (n == pn and nxt is not None and s == nxt) or (n == pn + 1 and s == "")
        want = f"khoản {pn}{nxt or ''} hoặc khoản {pn + 1}"
    if not ok:
        raise A4Error("E_ORDER", f"khoản {node.number}, mong đợi {want}", node.line_no)


def parse_tree(body):
    """body: [(số dòng, chữ)] ('' là dòng trống). Trả về Node gốc; gốc là Điều / Khoản / Điểm, đúng một gốc."""
    root, cur, last, after_blank = None, {}, None, False
    for no, text in body:
        if not text:
            after_blank = True
            continue
        lab = _label(text)
        if lab:
            kind, number, rest = lab
            node = Node(kind, number, rest if kind == "dieu" else None, [] if kind == "dieu" or not rest else [rest], [], no)
            level = LEVEL[kind]
            if root is None:
                root, cur = node, {level: node}
            else:
                if level <= LEVEL[root.kind]:
                    raise A4Error("E_BODY", f"nhãn {kind} {number} ngang hoặc cao hơn gốc ({root.kind} {root.number}): nội dung phải có đúng một gốc", no)
                parent = cur.get(level - 1)
                if parent is None:
                    raise A4Error("E_BODY", f"{kind} {number} khi chưa có cấp cha", no)
                _check_order(parent.children[-1] if parent.children else None, node)
                parent.children.append(node)
                cur = {k: v for k, v in cur.items() if k < level}
                cur[level] = node
            last = node
        else:
            if last is None:
                raise A4Error("E_BODY", "đoạn chữ đứng trước nhãn đầu tiên", no)
            if after_blank:
                last.parts.append(text)
            elif last.parts:
                last.parts[-1] += " " + text
            elif last.kind == "dieu":
                last.heading = (last.heading + " " + text).strip()
            else:
                last.parts.append(text)
        after_blank = False
    if root is None:
        raise A4Error("E_BODY", "nội dung trong nháy rỗng")
    return root


def flatten(node, code):
    """[(mã, Node)] theo thứ tự trước-sau, mã suy từ mã của gốc."""
    out = [(code, node)]
    for ch in node.children:
        out += flatten(ch, child_code(code, ch.kind, ch.number))
    return out


# ---- chỉ thị ----

@dataclass
class Directive:
    seq: int = 0
    line_no: int = 0
    line: str = ""
    op: str = ""             # replace_unit | insert_unit | repeal_unit | rename_heading | phrase | replace_doc
    relation: str = ""       # amends | replaces | repeals
    targets: list = field(default_factory=list)  # mã đơn vị (insert_unit: mã đơn vị mới; replace_doc: BLDS2015)
    number: str | None = None   # replace_unit / insert_unit: số của gốc cây nội dung
    after: str | None = None    # insert_unit: mã anh em trong "vào sau"
    tree: Node | None = None    # replace_unit / insert_unit
    mode: str | None = None     # phrase: replace | delete | insert
    old: str | None = None      # phrase: cụm cũ / cụm neo; rename_heading: tiêu đề cũ (nếu có)
    new: str | None = None      # phrase: cụm mới; rename_heading: tiêu đề mới


class Matched(NamedTuple):
    kind: str
    data: dict


class Parsed(NamedTuple):
    directives: list
    skipped: list  # [(số dòng, dòng, lý do)]


_Q = r"“(?P<{}>[^“”]*)”"
_TAIL = r"(?: tại (?P<l>.+?))?[.;]*$"
RE_NUM = re.compile(r"^\d+\.\s+")
RE_R6 = re.compile(r"^(?:Luật|Bộ luật|Văn bản) này thay thế (?:toàn bộ )?Bộ luật dân sự(?: năm 2015| số 91/2015/QH13)?\.?$", re.I)
RE_R1 = [
    re.compile(rf"^(?P<u>{_UREF}) (?P<w>được sửa đổi, bổ sung|được sửa đổi|được thay thế) như sau:$", re.I),
    re.compile(rf"^(?P<w>Sửa đổi, bổ sung|Sửa đổi|Thay thế) (?P<u>{_UREF}) như sau:$", re.I),
]
RE_R2_DIEU = re.compile(rf"^Bổ sung Điều (?P<n>{_N})(?: vào sau Điều (?P<m>{_N}){_LAW})? như sau:$", re.I)
RE_R2_KHOAN = re.compile(
    rf"^Bổ sung khoản (?P<n>{_N})(?: vào(?: sau khoản (?P<m>{_N}))?)? Điều (?P<x>{_N}){_LAW} như sau:$", re.I)
RE_R2_DIEM = re.compile(
    rf"^Bổ sung điểm (?P<n>{_P})(?: vào(?: sau điểm (?P<m>{_P}))?)? khoản (?P<k>{_N}) Điều (?P<x>{_N}){_LAW} như sau:$", re.I)
RE_R3 = re.compile(r"^Bãi bỏ (?P<l>.+?)\.?$", re.I)
RE_R4 = re.compile(rf"^Tên Điều (?P<n>{_N}) được sửa đổi như sau:$", re.I)
RE_R4_OLDNEW = re.compile(r"^“(?P<o>[^“”]*)” được sửa đổi thành “(?P<n>[^“”]*)”[.;]*$")
RE_R4_NEW = re.compile(r"^“(?P<n>[^“”]*)”[.;]*$")
PHRASE_FORMS = [  # (mode, relation, regex)
    ("replace", "amends", re.compile(rf"^Sửa đổi cụm từ {_Q.format('o')} thành cụm từ {_Q.format('n')}{_TAIL}", re.I)),
    ("replace", "replaces", re.compile(rf"^Thay thế cụm từ {_Q.format('o')} bằng cụm từ {_Q.format('n')}{_TAIL}", re.I)),
    ("delete", "amends", re.compile(rf"^Bỏ cụm từ {_Q.format('o')}{_TAIL}", re.I)),
    ("insert", "amends", re.compile(rf"^Bổ sung cụm từ {_Q.format('n')} vào sau cụm từ {_Q.format('o')}{_TAIL}", re.I)),
]
RE_SCOPE = re.compile(r"^(?:Sửa đổi, bổ sung|Sửa đổi|Bổ sung) một số cụm từ tại (?P<l>.+?) như sau:$", re.I)

RE_OWN_DIEU = re.compile(r"^Điều \d+[a-z]?\s*\.")  # tiêu đề Điều của chính văn bản sửa đổi (có dấu chấm sau số)
RE_TITLE = re.compile(r"^(Sửa đổi|Bổ sung|Bãi bỏ)[^.]* một số điều của .+:?$")
RE_WORDS = re.compile(r"được sửa đổi|được thay thế|được bổ sung|Sửa đổi|Bổ sung|Bãi bỏ|Thay thế|Bỏ cụm|Thay cụm|thay thế")
# Dòng không khớp RE_WORDS nhưng vẫn có dáng chỉ thị (bị động, "hết hiệu lực", "thay bằng") là dòng lạ, không bị bỏ qua (C8).
RE_ACTION = re.compile(r"(?<!\w)(?:sửa|bổ sung|thay|bỏ)(?!\w)", re.I)
RE_ACTION_ALONE = re.compile(r"(?<!\w)(?:bãi bỏ|hết hiệu lực)(?!\w)", re.I)  # không cần kèm tham chiếu (cấp văn bản)
RE_STRUCT_REF = re.compile(r"(?<!\w)(?:điều|khoản|điểm)[ ]+(?:\d+[a-zđ]?|[a-zđ])(?!\w)", re.I)
RE_UNSUPPORTED = re.compile(r"đánh số lại|trở thành", re.I)


def strip_number(line):
    return RE_NUM.sub("", line, count=1)


def _curly(line):
    return re.sub(r'"([^"]*)"', r"“\1”", line)


def match_directive(line):
    """Nhận một dòng (đã chuẩn hoá, đã bỏ số thứ tự) là chỉ thị R1–R6 hoặc dòng phạm vi cụm từ; không khớp thì None.

    Dòng có khung 'Bãi bỏ ...' nhưng danh sách đích không đọc được thì báo lỗi (không bỏ qua, không bắt một phần).
    """
    if RE_R6.match(line):
        return Matched("replace_doc", {})
    for rx in RE_R1:
        m = rx.match(line)
        if m:
            rel = "replaces" if "thay thế" in m["w"].lower() else "amends"
            return Matched("replace_unit", {"ref": parse_uref(m["u"]), "relation": rel})
    m = RE_R4.match(line)
    if m:
        return Matched("rename_heading", {"dieu": m["n"].lower()})
    m = RE_R2_DIEU.match(line)
    if m:
        after = f"{DOC_PREFIX}.D{m['m'].lower()}" if m["m"] else None
        return Matched("insert_unit", {"kind": "dieu", "number": m["n"].lower(), "code": f"{DOC_PREFIX}.D{m['n'].lower()}", "after": after})
    m = RE_R2_KHOAN.match(line)
    if m:
        dieu = f"{DOC_PREFIX}.D{m['x'].lower()}"
        after = f"{dieu}.K{m['m'].lower()}" if m["m"] else None
        return Matched("insert_unit", {"kind": "khoan", "number": m["n"].lower(), "code": f"{dieu}.K{m['n'].lower()}", "after": after})
    m = RE_R2_DIEM.match(line)
    if m:
        khoan = f"{DOC_PREFIX}.D{m['x'].lower()}.K{m['k'].lower()}"
        for letter in (m["n"], m["m"]):
            if letter and letter.lower() not in a1.DIEM_LETTERS:
                raise A4Error("E_REFLIST", f"điểm {letter} không thuộc bảng chữ của Điểm")
        n = m["n"].lower()
        after = f"{khoan}.{a1.diem_code(m['m'].lower())}" if m["m"] else None
        return Matched("insert_unit", {"kind": "diem", "number": n, "code": f"{khoan}.{a1.diem_code(n)}", "after": after})
    curly = _curly(line)
    for mode, rel, rx in PHRASE_FORMS:
        m = rx.match(curly)
        if m:
            gd = m.groupdict()
            refs = parse_reflist(gd["l"]) if gd.get("l") else None
            return Matched("phrase", {"mode": mode, "relation": rel, "old": gd.get("o"), "new": gd.get("n"), "refs": refs})
    m = RE_SCOPE.match(line)
    if m:
        return Matched("scope", {"refs": parse_reflist(m["l"])})
    if RE_TITLE.match(line):
        return None
    m = RE_R3.match(line)
    if m:
        return Matched("repeal_unit", {"refs": parse_reflist(m["l"])})
    return None


def skip_reason(line):
    """Lý do bỏ qua một dòng ngoài nháy không phải chỉ thị; None nếu là 'dòng lạ'."""
    if RE_OWN_DIEU.match(line):
        return "tiêu đề Điều của văn bản sửa đổi"
    if RE_TITLE.match(line):
        return "tiêu đề chung"
    if RE_ACTION_ALONE.search(line) or (RE_ACTION.search(line) and RE_STRUCT_REF.search(line)):
        return None
    if not RE_WORDS.search(line):
        return "không phải chỉ thị"
    return None


def read_block(lines, start):
    """Vùng nội dung trong nháy sau một dòng chỉ thị: từ dòng start đến dòng có dấu đóng nháy cuối cùng trước chỉ thị kế tiếp.

    Trả về (các dòng của vùng, chỉ số dòng kế tiếp). Chỉ thị kế tiếp chỉ được nhận khi không còn nằm trong nháy.
    """
    depth, style, last_close, j = 0, None, -1, start
    while j < len(lines):
        no, line = lines[j]
        if depth == 0 and line and match_directive(strip_number(line)) is not None:
            break
        for ch in line:
            if depth == 0:
                if ch in "“\"":
                    depth, style = 1, ch
            elif style == "“":
                if ch == "“":
                    depth += 1
                elif ch == "”":
                    depth -= 1
                    if depth == 0:
                        last_close = j
            elif ch == "\"":
                depth, last_close = 0, j
        j += 1
    if depth > 0:
        raise A4Error("E_BODY", "dấu mở nháy không được đóng trước hết văn bản hoặc chỉ thị kế tiếp", lines[start][0] if start < len(lines) else None)
    if last_close < 0:
        raise A4Error("E_BODY", "thiếu nội dung trong nháy sau dòng chỉ thị")
    return lines[start:last_close + 1], last_close + 1


def extract_body(region):
    """Chữ trong nháy của một vùng: [(số dòng, chữ)]. Phần ngoài nháy chỉ được là trống, dấu chấm, chấm phẩy."""
    body, depth, style = [], 0, None
    for no, line in region:
        buf, started = [], depth > 0
        for ch in line:
            if depth == 0:
                if ch in "“\"":
                    depth, style, started = 1, ch, True
                elif not (ch.isspace() or ch in ".;"):
                    raise A4Error("E_BODY", f"chữ ngoài nháy {ch!r} trong vùng nội dung (chỉ cho phép trống, '.', ';')", no)
            elif style == "“":
                if ch == "“":
                    depth += 1
                    buf.append(ch)
                elif ch == "”":
                    depth -= 1
                    if depth > 0:
                        buf.append(ch)
                else:
                    buf.append(ch)
            elif ch == "\"":
                depth = 0
            else:
                buf.append(ch)
        if started:
            body.append((no, "".join(buf).strip()))
    while body and not body[0][1]:
        body.pop(0)
    while body and not body[-1][1]:
        body.pop()
    return body


def _strip_dieu_prefix(title, number, no):
    m = re.match(r"^Điều\s+(\d+[a-z]?)\s*\.\s*", title)
    if not m:
        return title
    if m[1] != number:
        raise A4Error("E_BODY", f"tiêu đề có tiền tố Điều {m[1]}, khác Điều {number} của chỉ thị", no)
    return title[m.end():]


def _root_check(root, kind, number, no):
    if root.kind != kind or root.number.lower() != number:
        raise A4Error("E_ROOT", f"gốc nội dung là {root.kind} {root.number}, chỉ thị nói {kind} {number}", no)


def build_directives(m, lines, i, no, raw, scope, seq0):
    """Dựng Directive từ một dòng chỉ thị đã nhận; đọc tiếp nội dung trong nháy nếu cần. Trả về (list Directive, i mới)."""
    def mk(**kw):
        return Directive(line_no=no, line=raw, **kw)

    d = m.data
    if m.kind == "replace_doc":
        out = [mk(op="replace_doc", relation="replaces", targets=[DOC_PREFIX])]
    elif m.kind == "repeal_unit":
        out = [mk(op="repeal_unit", relation="repeals", targets=[ref_code(r)]) for r in d["refs"]]
    elif m.kind == "phrase":
        refs = d["refs"] if d["refs"] is not None else scope
        if refs is None:
            raise A4Error("E_SCOPE", "chỉ thị cụm từ không có 'tại' mà chưa có dòng phạm vi")
        if d["old"] == "" or (d["mode"] == "insert" and d["new"] == "") or (d["mode"] == "replace" and d["new"] is None):
            raise A4Error("E_PHRASE", "cụm từ rỗng")
        out = [mk(op="phrase", relation=d["relation"], targets=[ref_code(r) for r in refs], mode=d["mode"], old=d["old"], new=d["new"])]
    else:  # replace_unit | insert_unit | rename_heading: có nội dung trong nháy
        region, i = read_block(lines, i)
        if m.kind == "rename_heading":
            number = d["dieu"]
            flat = " ".join(line for _, line in region if line)
            flat = _curly(flat)
            mo = RE_R4_OLDNEW.match(flat)
            mn = None if mo else RE_R4_NEW.match(flat)
            if not (mo or mn):
                raise A4Error("E_BODY", f"nội dung đổi tên Điều không đúng dạng: {flat!r}", region[0][0])
            old = _strip_dieu_prefix(mo["o"], number, region[0][0]) if mo else None
            new = _strip_dieu_prefix((mo or mn)["n"], number, region[0][0])
            out = [mk(op="rename_heading", relation="amends", targets=[f"{DOC_PREFIX}.D{number}"], old=old, new=new)]
        else:
            tree = parse_tree(extract_body(region))
            if m.kind == "replace_unit":
                ref = d["ref"]
                _root_check(tree, ref_kind(ref), (ref.diem or ref.khoan or ref.dieu), region[0][0])
                out = [mk(op="replace_unit", relation=d["relation"], targets=[ref_code(ref)], number=tree.number, tree=tree)]
            else:
                _root_check(tree, d["kind"], d["number"], region[0][0])
                out = [mk(op="insert_unit", relation="amends", targets=[d["code"]], number=tree.number, after=d["after"], tree=tree)]
    for k, dr in enumerate(out, 1):
        dr.seq = seq0 + k
    return out, i


def resolve_unmatched(raw, no, skipped):
    """Dòng không khớp chỉ thị: bỏ qua (ghi vào skipped) hoặc gọi hàm móc. Trả về Matched hoặc None nếu đã bỏ qua."""
    stripped = strip_number(raw)
    if RE_UNSUPPORTED.search(raw):
        raise A4Error("E_UNSUPPORTED", "chưa hỗ trợ 'đánh số lại' / 'trở thành' trong khối chỉ thị", no, raw)
    reason = skip_reason(stripped)
    if reason:
        skipped.append((no, raw, reason))
        return None
    fixed = normalize_unknown_line(raw)
    if fixed is None:
        raise A4Error("E_UNKNOWN_LINE", "dòng lạ: không khớp chỉ thị R1–R6 và hàm chuẩn hoá không xử lý được", no, raw)
    m = match_directive(strip_number(norm_line(fixed)))
    if m is None:
        raise A4Error("E_UNKNOWN_LINE", f"dòng chuẩn do normalize_unknown_line trả về không parse được: {fixed!r}", no, raw)
    return m


def parse_amendment(text):
    """Văn bản sửa đổi -> Parsed(directives, skipped). Chưa kiểm gì với trạng thái văn bản gốc."""
    lines = split_lines(text)
    directives, skipped, scope, i = [], [], None, 0
    while i < len(lines):
        no, raw = lines[i]
        i += 1
        if not raw:
            continue
        try:
            m = match_directive(strip_number(raw))
            if m is None:
                m = resolve_unmatched(raw, no, skipped)
            if m is None:
                continue
            if m.kind == "scope":
                scope = m.data["refs"]
                continue
            if m.kind != "phrase":
                scope = None
            new, i = build_directives(m, lines, i, no, raw, scope, len(directives))
            directives += new
        except A4Error as e:
            e.line_no = e.line_no or no
            e.line = e.line or raw
            raise
    if not directives:
        raise A4Error("E_NO_DIRECTIVE", "văn bản sửa đổi không có chỉ thị nào")
    return Parsed(directives, skipped)


def check_overlap(directives):
    """Hai chỉ thị cùng văn bản có cây đích chồng lấn là lỗi, trừ khi cả hai là cụm từ."""
    for a in range(len(directives)):
        da = directives[a]
        for b in range(a, len(directives)):
            db = directives[b]
            if a == b:  # các đích của cùng một chỉ thị cụm từ cũng không được chồng nhau
                pairs = [(x, y) for p, x in enumerate(da.targets) for y in da.targets[p + 1:]] if da.op == "phrase" else []
            elif da.op == db.op == "phrase":
                continue
            else:
                pairs = [(x, y) for x in da.targets for y in db.targets]
            for x, y in pairs:
                if overlaps(x, y):
                    raise A4Error("E_OVERLAP", f"chỉ thị {da.seq} ({x}) và chỉ thị {db.seq} ({y}) có cây đích chồng lấn",
                                  db.line_no, db.line)


# ---- phiên bản ----

@dataclass
class Version:
    id: str
    version: int
    type: str
    number: str
    heading: str | None
    parts: list
    effective_from: str | None = None
    effective_to: str | None = None
    previous_version: int | None = None
    source_doc: str | None = None
    directive_seq: int | None = None

    @property
    def text(self):
        return "\n".join(self.parts) if self.parts else None

    def row(self):
        return {"id": self.id, "version": self.version, "type": self.type, "number": self.number, "heading": self.heading,
                "text": self.text, "effective_from": self.effective_from, "effective_to": self.effective_to,
                "previous_version": self.previous_version, "source_doc": self.source_doc, "directive_seq": self.directive_seq}


class Store:
    """Mọi phiên bản của mọi đơn vị: {mã: [Version, ...]} theo thứ tự tạo; phiên bản cuối đang hiệu lực nếu effective_to là None."""

    def __init__(self):
        self.versions = {}

    def cur(self, code):
        vs = self.versions.get(code)
        return vs[-1] if vs and vs[-1].effective_to is None else None

    def active(self):
        return [c for c, vs in self.versions.items() if vs[-1].effective_to is None]

    def subtree(self, code):
        """Mã đang hiệu lực của code và mọi con cháu, theo thứ tự lưu."""
        return [c for c in self.active() if c == code or c.startswith(code + ".")]

    def create(self, code, node_or_unit, date, doc, seq):
        """Phiên bản mới của một mã: 1 nếu chưa từng có, ngược lại số kế tiếp (mở lại mã đã đóng)."""
        kind, number = unit_of_code(code)
        prev = self.versions[code][-1] if code in self.versions else None
        heading, parts = node_or_unit
        v = Version(code, prev.version + 1 if prev else 1, kind, number, heading, list(parts), date, None,
                    prev.version if prev else None, doc, seq)
        self.versions.setdefault(code, []).append(v)
        return v

    def modify(self, code, heading, parts, date, doc, seq):
        """Phiên bản mới của đơn vị đang hiệu lực. Nếu phiên bản hiện tại tạo trong chính văn bản này thì sửa tại chỗ."""
        cur = self.cur(code)
        if cur.source_doc == doc and cur.effective_from == date:
            cur.heading, cur.parts = heading, list(parts)
            return cur
        cur.effective_to = date
        return self.create(code, (heading, parts), date, doc, seq)

    def close(self, code, date):
        self.versions[code][-1].effective_to = date


# ---- cạnh ----

class EdgeState:
    """Cạnh đang có hiệu lực: {(s, p, o): dòng}, cộng tập khoá cạnh gốc. Cạnh gốc không bao giờ bị xoá khỏi file gốc."""

    def __init__(self, rows):
        self.edges = {(r["s"], r["p"], r["o"]): r for r in rows}
        self.base = set(self.edges)


def read_jsonl(path):
    rows = []
    with open(path, encoding="utf-8", newline="") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_base_edges(stem):
    """Cạnh gốc: contains/part_of (A2a), refers_to (A2b), exception_of (A3), chỉ đọc."""
    paths = [IN_DIR / f"a2_edges_{stem}.jsonl", IN_DIR / f"a2_refs_{stem}.jsonl", IN_DIR / f"a3_exceptions_{stem}.jsonl"]
    rows = []
    for p in paths:
        if not p.exists():
            raise A4Error("E_BASE", f"chưa có {p}; chạy a2_edges.py và a3_exceptions.py cho file gốc trước")
        rows += read_jsonl(p)
    return rows


def impact_set(U, edges):
    """{đơn vị: [lý do]} cho U = changed ∪ closed. edges: (s, p, o) của cạnh gốc đang hiệu lực.

    Nguồn có refers_to tới đơn vị m trong U: 'refers_to m'. Đơn vị nối với m trong U bằng exception_of: 'exception_of m' nếu
    nó là ngoại lệ của m, 'exception_of_by m' nếu m là ngoại lệ của nó. Tầng khái niệm/quy tắc sẽ mở rộng sau.
    """
    U, out = set(U), collections.defaultdict(set)
    for s, p, o in edges:
        if p == REFERS and o in U:
            out[s].add(f"{REFERS} {o}")
        elif p == EXCEPTION:
            if o in U:
                out[s].add(f"{EXCEPTION} {o}")
            if s in U:
                out[o].add(f"{EXCEPTION}_by {s}")
    return {k: sorted(v) for k, v in sorted(out.items(), key=lambda kv: code_key(kv[0]))}


# ---- cờ chưa phủ ----

RE_MENTION = re.compile(r"\b(?:Điều|khoản|điểm)\s+(?:\d+[a-zđ]?|[a-zđ])(?!\w)", re.I)


def uncovered_mentions(code, text):
    """Mention điều/khoản/điểm không nằm trong cụm mà a2.find_refs nhận ra trên đơn vị: [(mã, mention, ngữ cảnh)]."""
    refs = a2.find_refs({code: {"type": "khoan", "number": "x", "source_line": 0, "text": text}})[0]
    spans, pos = [], 0
    for r in refs:
        k = text.find(r.phrase, pos)
        spans.append((k, k + len(r.phrase)))
        pos = k + len(r.phrase)
    out = []
    for m in RE_MENTION.finditer(text):
        if not any(a <= m.start() and m.end() <= b for a, b in spans):
            ctx = text[max(0, m.start() - a2.CONTEXT_CHARS):m.end() + a2.CONTEXT_CHARS].replace("\n", " ")
            out.append((code, m.group(0), ctx))
    return out


# ---- áp dụng ----

@dataclass
class Doc:
    doc_id: str
    path: str
    date: str
    directives: list
    skipped: list


@dataclass
class Step:
    doc: Doc
    changed: dict = field(default_factory=dict)   # dict dùng như tập có thứ tự
    new: dict = field(default_factory=dict)
    closed: dict = field(default_factory=dict)
    named: dict = field(default_factory=dict)
    named_unchanged: list = field(default_factory=list)
    amend_rows: list = field(default_factory=list)
    edge_rows: list = field(default_factory=list)
    broken: list = field(default_factory=list)      # [(s, p, o, evidence)]
    unhandled: list = field(default_factory=list)   # [(mã, câu)] của A3
    uncovered: list = field(default_factory=list)   # [(mã, mention, ngữ cảnh)]
    excluded: list = field(default_factory=list)    # mã bị loại khỏi A2/A3 vì hậu tố

    def amend(self, d, target, new_version):
        self.amend_rows.append({"s": self.doc.doc_id, "p": d.relation, "o": target, "directive_seq": d.seq,
                                "effective_from": self.doc.date, "new_version": new_version})


def need_active(store, code):
    if store.cur(code) is None:
        why = "đã bị đóng" if code in store.versions else "không tồn tại"
        raise A4Error("E_TARGET", f"đích {code} {why}")
    return store.cur(code)


def apply_replace_unit(store, step, d):
    code, date, doc = d.targets[0], step.doc.date, step.doc.doc_id
    need_active(store, code)
    flat = flatten(d.tree, code)
    root_version = None
    for c, node in flat:
        v = store.cur(c)
        if v is not None:
            step.named[c] = True
            if (v.heading, v.parts) == (node.heading, node.parts):
                continue
            nv = store.modify(c, node.heading, node.parts, date, doc, d.seq)
            step.changed[c] = True
            if c == code:
                root_version = nv.version
        else:
            existed = c in store.versions
            store.create(c, (node.heading, node.parts), date, doc, d.seq)
            (step.changed if existed else step.new)[c] = True
    keep = {c for c, _ in flat}
    for c in store.subtree(code):
        if c not in keep:
            store.close(c, date)
            step.closed[c] = True
    step.amend(d, code, root_version)


def apply_insert_unit(store, step, d):
    code, date, doc = d.targets[0], step.doc.date, step.doc.doc_id
    if code in store.versions:
        raise A4Error("E_EXISTS", f"{code} đã từng tồn tại (kể cả đã đóng), không chèn lại được")
    parent = parent_code(code)
    if parent is not None and store.cur(parent) is None:
        raise A4Error("E_PARENT", f"cha {parent} của {code} không đang hiệu lực")
    if d.after is not None:
        if d.after not in store.versions:
            raise A4Error("E_AFTER", f"'vào sau' trỏ {d.after} không phải đơn vị có thật")
        if seg_key(code.split(".")[-1]) <= seg_key(d.after.split(".")[-1]):
            raise A4Error("E_AFTER", f"{code} không xếp sau {d.after} theo thứ tự (số, hậu tố)")
    for c, node in flatten(d.tree, code):
        if c in store.versions:
            raise A4Error("E_EXISTS", f"{c} đã từng tồn tại, không chèn lại được")
        store.create(c, (node.heading, node.parts), date, doc, d.seq)
        step.new[c] = True
    step.amend(d, code, 1)


def apply_repeal_unit(store, step, d):
    code = d.targets[0]
    need_active(store, code)
    for c in store.subtree(code):
        store.close(c, step.doc.date)
        step.closed[c] = True
    step.amend(d, code, None)


def apply_rename_heading(store, step, d):
    code = d.targets[0]
    v = need_active(store, code)
    if d.old is not None and d.old != v.heading:
        raise A4Error("E_HEADING", f"tiêu đề cũ {d.old!r} khác tiêu đề hiện tại {v.heading!r}")
    if d.new == v.heading:
        step.named[code] = True
        step.amend(d, code, None)
        return
    nv = store.modify(code, d.new, v.parts, step.doc.date, step.doc.doc_id, d.seq)
    step.changed[code] = True
    step.amend(d, code, nv.version)


def _phrase_sub(s, d):
    """Áp chỉ thị cụm từ lên một chuỗi: (chuỗi mới, có cụm cũ hay không)."""
    if d.old not in s:
        return s, False
    if d.mode == "replace":
        return s.replace(d.old, d.new), True
    if d.mode == "delete":
        return re.sub(r" {2,}", " ", s.replace(d.old, "")).strip(), True
    sep = "" if d.new[:1] in ",;.:" else " "  # chèn sau cụm neo; cụm chèn mở đầu bằng dấu câu thì không thêm dấu cách
    return s.replace(d.old, d.old + sep + d.new), True


def apply_phrase(store, step, d):
    date, doc = step.doc.date, step.doc.doc_id
    for target in d.targets:
        need_active(store, target)
        found, root_version = False, None
        for c in store.subtree(target):
            v = store.cur(c)
            heading, hit_h = _phrase_sub(v.heading, d) if v.heading is not None else (None, False)
            parts, hit_p = [], False
            for p in v.parts:
                np, hit = _phrase_sub(p, d)
                parts.append(np)
                hit_p = hit_p or hit
            parts = [p for p in parts if p]
            found = found or hit_h or hit_p
            if (heading, parts) != (v.heading, v.parts):
                nv = store.modify(c, heading, parts, date, doc, d.seq)
                step.changed[c] = True
                if c == target:
                    root_version = nv.version
        if not found:
            raise A4Error("E_PHRASE_MISSING", f"cụm {d.old!r} không có ở đâu trong cây của {target}")
        if root_version is None:
            step.named[target] = True
        step.amend(d, target, root_version)


def apply_replace_doc(store, step, d):
    for c in store.active():
        store.close(c, step.doc.date)
        step.closed[c] = True
    step.amend(d, DOC_PREFIX, None)


APPLY = {"replace_unit": apply_replace_unit, "insert_unit": apply_insert_unit, "repeal_unit": apply_repeal_unit,
         "rename_heading": apply_rename_heading, "phrase": apply_phrase, "replace_doc": apply_replace_doc}


def edge_view(store, text_for, skip=()):
    """Tập đơn vị đang hiệu lực ở dạng A2 nhận (type, number, source_line); chỉ các mã trong text_for mới có text."""
    view = {}
    for c in store.active():
        if c in skip:
            continue
        v = store.cur(c)
        u = {"type": v.type, "number": v.number, "source_line": 0}
        if c in text_for and v.text:
            u["text"] = v.text
        view[c] = u
    return view


def _edge_row(op, key, row, at):
    s, p, o = key
    out = {"op": op, "s": s, "p": p, "o": o, "at": at}
    if row.get("evidence"):
        out["evidence"] = row["evidence"]
    if row.get("method"):
        out["method"] = row["method"]
    return out


def recompute_edges(store, state, step, S):
    """Chạy lại a2.build_refs và a3.find_exceptions cho nguồn thuộc S, so với cạnh hiện có cùng nguồn, ghi add/close.

    Chỉ nguồn thuộc S có text trong tập đưa vào A2/A3; mọi đơn vị đang hiệu lực khác chỉ làm đích và tổ tiên. Nhờ vậy cạnh
    gốc của đơn vị không đổi mà trỏ vào đích đã đóng không làm A2/A3 báo lỗi: nó thành cờ cạnh đứt.
    """
    date = step.doc.date
    skip = set() if A2A3_ACCEPT_SUFFIX else {c for c in store.active() if has_suffix(c)}
    step.excluded = [c for c in S if c in skip]
    S_set = {c for c in S if c not in skip}
    # cha có "sau đây:" cần text để quy tắc 2 của A3 sinh cạnh cho con mới
    listy = {parent_code(c) for c in S_set if parent_code(c) and (store.cur(parent_code(c)).text or "").endswith(a3.LIST_END)}
    try:
        view = edge_view(store, S_set, skip)
        new_refs = [(s, p, o, ev) for s, p, o, ev in a2.build_refs(view)[0] if s in S_set]
    except ValueError as e:
        raise A4Error("E_A2", str(e))
    try:
        view3 = edge_view(store, S_set | listy, skip)
        exc, _, unhandled = a3.find_exceptions(view3, a2.build_edges(view3))
    except ValueError as e:
        raise A4Error("E_A3", str(e))
    # Cạnh thuộc phạm vi so khi đơn vị giữ chứng cứ của nó thuộc S. Với refers_to và quy tắc 1 đó là nguồn s; với quy tắc 2
    # (except_list_pattern) chứng cứ là chữ của cha o, còn nguồn s là con, nên con của một cha changed cũng được so.
    in_scope = lambda s, o, method: s in S_set or (method == a3.EXCEPT_LIST and o in S_set)
    new_exc = [(s, p, o, ev, method) for s, p, o, ev, method in exc if in_scope(s, o, method)]
    step.unhandled = [(c, sentence) for c, sentence in unhandled if c in S_set]

    new_rows = {(s, p, o): {"evidence": ev} for s, p, o, ev in new_refs}
    new_rows.update({(s, p, o): {"evidence": ev, "method": method} for s, p, o, ev, method in new_exc})
    old = [k for k, row in state.edges.items()
           if (k[1] == REFERS and k[0] in S_set) or (k[1] == EXCEPTION and in_scope(k[0], k[2], row.get("method")))]
    rows = []
    for k in old:
        if k not in new_rows:
            rows.append(_edge_row("close", k, state.edges[k], date))
            del state.edges[k]
    for c in step.new:  # contains / part_of cho mã mới, suy từ mã
        parent = parent_code(c)
        if parent is None:
            continue
        for key in ((parent, CONTAINS, c), (c, PART_OF, parent)):
            if key not in state.edges:
                state.edges[key] = {"s": key[0], "p": key[1], "o": key[2], "evidence": ""}
                rows.append(_edge_row("add", key, {}, date))
    for k, meta in new_rows.items():
        if k not in state.edges:
            state.edges[k] = {"s": k[0], "p": k[1], "o": k[2], **meta}
            rows.append(_edge_row("add", k, meta, date))
    step.edge_rows = rows


def find_broken(store, state, date):
    """Cạnh refers_to / exception_of mà nguồn còn hiệu lực và đích bị đóng tại ngày hiệu lực."""
    out = []
    for (s, p, o), row in state.edges.items():
        if p not in (REFERS, EXCEPTION) or store.cur(s) is None:
            continue
        vs = store.versions.get(o)
        if vs and vs[-1].effective_to == date:
            out.append((s, p, o, row.get("evidence", "")))
    return out


def apply_doc(store, state, doc):
    step = Step(doc)
    check_overlap(doc.directives)
    for d in doc.directives:
        try:
            APPLY[d.op](store, step, d)
        except A4Error as e:
            e.doc, e.line_no, e.line = e.doc or doc.doc_id, e.line_no or d.line_no, e.line or d.line
            raise
    step.named_unchanged = [c for c in step.named if c not in step.changed and c not in step.new and c not in step.closed]
    S = sorted((c for c in list(step.changed) + list(step.new) if store.cur(c) is not None), key=code_key)
    S = list(dict.fromkeys(S))
    try:
        recompute_edges(store, state, step, S)
    except A4Error as e:
        e.doc = e.doc or doc.doc_id
        raise
    for c in S:
        if c not in step.excluded:
            step.uncovered += uncovered_mentions(c, store.cur(c).text or "")
    step.broken = find_broken(store, state, doc.date)
    return step


class Run:
    """Kết quả apply_series: mọi thứ cần ghi ra file và vào báo cáo."""

    def __init__(self, name, base, docs, store, state, steps):
        self.name, self.base, self.docs, self.store, self.state, self.steps = name, base, docs, store, state, steps
        order = lambda ss: sorted(set().union(*ss) if ss else set(), key=code_key)
        self.changed = order([set(s.changed) for s in steps])
        self.new = order([set(s.new) for s in steps])
        self.closed = order([set(s.closed) for s in steps])
        self.named_unchanged = order([set(s.named_unchanged) for s in steps])
        self.amend_edges = [r for s in steps for r in s.amend_rows]
        self.edge_changes = [r for s in steps for r in s.edge_rows]
        self.broken = [(s.doc.doc_id,) + b for s in steps for b in s.broken]
        base_active = [k for k in state.edges if k in state.base]
        impact = impact_set(set(self.changed) | set(self.closed), base_active)
        self.impact = {k: v for k, v in impact.items() if store.cur(k) is not None}
        self.table = [(d.doc_id, x.seq, x.line_no, x.op, x.relation, ", ".join(x.targets)) for d in docs for x in d.directives]
        self.skipped = [(d.doc_id,) + sk for d in docs for sk in d.skipped]
        self.unhandled = [(s.doc.doc_id,) + u for s in steps for u in s.unhandled]
        self.uncovered = [(s.doc.doc_id,) + u for s in steps for u in s.uncovered]
        self.excluded = [(s.doc.doc_id, c) for s in steps for c in s.excluded]

    def version_rows(self):
        return [v.row() for vs in self.store.versions.values() for v in vs]

    def changed_json(self):
        return {"changed": self.changed, "new": self.new, "closed": self.closed, "named_unchanged": self.named_unchanged}


class AmendSpec(NamedTuple):
    path: str
    doc_id: str | None = None
    effective_from: str | None = None


def load_base(base):
    base = Path(base)
    try:
        _, parsed = a1.load_parsed(base)
    except SystemExit as e:
        raise A4Error("E_BASE", f"không nạp được văn bản gốc {base} (A1 thoát {e.code!r}; xem stderr)")
    if parsed.errors:
        raise A4Error("E_BASE", f"văn bản gốc {base} còn lỗi parse A1: {parsed.errors[:3]}")
    store = Store()
    for u in parsed.units:
        store.versions[u.id] = [Version(u.id, 1, u.type, u.number, u.heading, list(u.parts))]
    return store


def _display_path(path):
    """Đường dẫn trong báo cáo: tương đối so với gốc dự án nếu nằm trong đó, để báo cáo không dính đường dẫn của máy."""
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def apply_series(base, amends, name=None):
    """Áp lần lượt các văn bản sửa đổi lên văn bản gốc; trả về Run, hoặc raise A4Error (chưa ghi gì)."""
    stem = Path(base).stem
    store = load_base(base)
    state = EdgeState(load_base_edges(stem))
    docs = []
    for spec in amends:
        spec = AmendSpec(str(spec)) if isinstance(spec, (str, Path)) else AmendSpec(*spec)
        doc_id = spec.doc_id or Path(spec.path).stem
        try:
            text = Path(spec.path).read_text(encoding="utf-8-sig")
            date = find_effective_date(text, spec.effective_from).isoformat()
            parsed = parse_amendment(text)
        except OSError as e:
            raise A4Error("E_ARGS", f"không đọc được văn bản sửa đổi {spec.path}: {e}", doc=doc_id)
        except A4Error as e:
            e.doc = e.doc or doc_id
            raise
        docs.append(Doc(doc_id, _display_path(spec.path), date, parsed.directives, parsed.skipped))
    by_date = collections.defaultdict(list)
    for d in docs:
        by_date[d.date].append(d.doc_id)
    for date, ids in by_date.items():
        if len(ids) > 1:
            raise A4Error("E_SAME_DATE", f"các văn bản {ids} cùng ngày hiệu lực {date}")
    ordered = sorted(docs, key=lambda d: d.date)
    steps = [apply_doc(store, state, d) for d in ordered]
    return Run(name or "+".join(d.doc_id for d in docs), stem, ordered, store, state, steps)


# ---- ghi file, báo cáo ----

def path_of(name, kind, ext="jsonl"):
    return OUT_DIR / f"a4_{name}_{kind}.{ext}"


def report_path(name):
    return DOCS_DIR / f"a4_report_{name}.txt"


def write_jsonl(rows, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_json(obj, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def write_text(text, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def _section(lines, title, rows):
    lines += ["", f"== {title} =="]
    lines += rows or ["(không có)"]


def format_report(run):
    L = [f"A4 báo cáo cập nhật: {run.name}", f"cơ sở: {run.base}", "văn bản sửa đổi, theo thứ tự áp dụng:"]
    L += [f"  {k}. {d.doc_id}\thiệu lực từ {d.date}\t{d.path}" for k, d in enumerate(run.docs, 1)]
    _section(L, "Bảng chỉ thị (văn bản, seq, dòng, op, relation, đích)", ["\t".join(str(x) for x in r) for r in run.table])
    L += ["", "== Thay đổi =="]
    for key, vals in (("changed", run.changed), ("new", run.new), ("closed", run.closed), ("named_unchanged", run.named_unchanged)):
        L.append(f"{key} ({len(vals)}): " + (", ".join(vals) if vals else "(không có)"))
    _section(L, "Cờ cạnh đứt (nguồn còn hiệu lực, đích đã bị đóng tại ngày hiệu lực)",
             ["\t".join([doc, s, p, o, ev]) for doc, s, p, o, ev in run.broken])
    _section(L, "Tập ảnh hưởng (đơn vị, lý do)", [f"{k}\t{'; '.join(v)}" for k, v in run.impact.items()])
    _section(L, "Dòng bị bỏ qua (văn bản, dòng, lý do, nội dung)", ["\t".join([doc, str(no), reason, line]) for doc, no, line, reason in run.skipped])
    _section(L, "A3 chưa xử lý (đơn vị changed/new: văn bản, đơn vị, câu)", ["\t".join(x) for x in run.unhandled])
    _section(L, "Chưa phủ (mention không nằm trong cụm A2 nhận ra: văn bản, đơn vị, mention, ngữ cảnh)", ["\t".join(x) for x in run.uncovered])
    none = ["(không có: A2/A3 nhận mã có hậu tố làm nguồn nên không đơn vị nào bị loại; mention trỏ tới mã hậu tố nằm ở mục 'Chưa phủ')"]
    _section(L, "Chưa tính cạnh (mã có hậu tố)", [f"{doc}\t{c}" for doc, c in run.excluded] or none)
    return "\n".join(L) + "\n"


def format_error(name, err):
    L = [f"A4 LỖI: {name}", f"mã lỗi: {err.code}", f"văn bản: {err.doc or '(chưa xác định)'}"]
    L.append(f"dòng: {err.line_no if err.line_no is not None else '-'}: {err.line if err.line is not None else ''}")
    L.append(f"mô tả: {err.message}")
    return "\n".join(L) + "\n"


def write_outputs(run):
    write_jsonl(run.version_rows(), path_of(run.name, "versions"))
    write_jsonl(run.amend_edges, path_of(run.name, "amend_edges"))
    write_jsonl(run.edge_changes, path_of(run.name, "edge_changes"))
    write_json(run.changed_json(), path_of(run.name, "changed", "json"))
    write_json(run.impact, path_of(run.name, "impact", "json"))
    write_text(format_report(run), report_path(run.name))


# ---- snapshot ----

def active_rows(rows, date):
    """Đơn vị đang hiệu lực tại ngày T (YYYY-MM-DD, so chuỗi = so ngày): (from null hoặc <= T) và (to null hoặc > T)."""
    return [r for r in rows if (r["effective_from"] is None or r["effective_from"] <= date)
            and (r["effective_to"] is None or r["effective_to"] > date)]


def render_markdown(rows):
    """Markdown cùng quy ước file BLDS gốc. Đoạn thêm của Khoản đặt ngay sau dòng nhãn, trước các Điểm."""
    kids, dieu = collections.defaultdict(list), []
    for r in rows:
        p = parent_code(r["id"])
        (dieu if p is None else kids[p]).append(r)
    key = lambda r: code_key(r["id"])
    parts_of = lambda r: r["text"].split("\n") if r["text"] else []
    blocks = []
    for d in sorted(dieu, key=key):
        blocks.append([f"### Điều {d['number']}\\." + (f" {d['heading']}" if d["heading"] else "")])
        blocks += [[t] for t in parts_of(d)]
        for k in sorted(kids[d["id"]], key=key):
            ps = parts_of(k)
            blocks.append([f"**{k['number']}\\.**" + (f" {ps[0]}" if ps else "")])
            blocks += [[t] for t in ps[1:]]
            lines = []
            for p in sorted(kids[k["id"]], key=key):
                pp = parts_of(p)
                lines.append(f"- **{p['number']})**" + (f" {pp[0]}" if pp else ""))
                lines += pp[1:]
            if lines:
                blocks.append([l + "  " for l in lines[:-1]] + lines[-1:])
    return "\n\n".join("\n".join(b) for b in blocks) + "\n" if blocks else ""


def cmd_snapshot(args):
    date = parse_iso(args.date).isoformat()
    path = path_of(args.name, "versions")
    if not path.exists():
        raise SystemExit(f"chưa có {path}; chạy apply --name {args.name} trước")
    text = render_markdown(active_rows(read_jsonl(path), date))
    if args.out:
        write_text(text, args.out)
        print("đã ghi", args.out)
    else:
        sys.stdout.buffer.write(text.encode("utf-8"))  # buffer để giữ LF, không BOM
        sys.stdout.buffer.flush()
    return 0


def cmd_apply(args):
    amends = args.amend
    ids = args.doc_id or [None] * len(amends)
    dates = args.effective_from or [None] * len(amends)
    shown = [i or Path(p).stem for i, p in zip(ids, amends)]
    name = args.name or "+".join(shown)
    try:
        if len(ids) != len(amends) or len(dates) != len(amends):
            raise A4Error("E_ARGS", "--doc-id và --effective-from, nếu có, phải có số lần bằng số --amend (một giá trị cho mỗi văn bản)")
        run = apply_series(args.base, [AmendSpec(p, i, d) for p, i, d in zip(amends, ids, dates)], name)
    except A4Error as e:
        write_text(format_error(name, e), report_path(name))
        print(f"LỖI {e.code}: {e.message}", file=sys.stderr)
        if e.line_no is not None:
            print(f"  {e.doc or ''} dòng {e.line_no}: {e.line}", file=sys.stderr)
        print("đã ghi", report_path(name), file=sys.stderr)
        raise SystemExit(1)
    write_outputs(run)
    print(f"{run.name}: {len(run.table)} chỉ thị | changed {len(run.changed)}, new {len(run.new)}, closed {len(run.closed)}, "
          f"named_unchanged {len(run.named_unchanged)} | cờ cạnh đứt {len(run.broken)} | ảnh hưởng {len(run.impact)}")
    print("đã ghi", report_path(run.name))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    ap_apply = sub.add_parser("apply", help="áp các văn bản sửa đổi lên văn bản gốc")
    ap_apply.add_argument("--base", required=True, help="file md gốc (cùng stem với file A1/A2/A3 đã sinh)")
    ap_apply.add_argument("--amend", action="append", required=True, help="văn bản sửa đổi, lặp lại để nạp nhiều văn bản")
    ap_apply.add_argument("--effective-from", action="append", help="ngày hiệu lực YYYY-MM-DD, một giá trị cho mỗi --amend")
    ap_apply.add_argument("--doc-id", action="append", help="mã văn bản (mặc định: tên file không đuôi), một giá trị cho mỗi --amend")
    ap_apply.add_argument("--name", help="tên bộ kết quả (mặc định: các doc-id nối bằng '+')")
    ap_snap = sub.add_parser("snapshot", help="xuất Markdown trạng thái đang hiệu lực tại một ngày")
    ap_snap.add_argument("--name", required=True)
    ap_snap.add_argument("--date", required=True, help="YYYY-MM-DD")
    ap_snap.add_argument("--out", help="ghi ra file thay vì stdout")
    args = ap.parse_args(argv)
    return (cmd_apply if args.cmd == "apply" else cmd_snapshot)(args)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
