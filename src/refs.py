"""L2: cạnh cấu trúc contains / part_of và cạnh dẫn chiếu refers_to trong và giữa các văn bản.

Chạy: python -I src/refs.py <doc_id>      một văn bản (cần l1 đã chạy cho văn bản đó và cho các văn bản nó trỏ tới)
      python -I src/refs.py --all         cả kho, ghi thêm data/processed/pending_links.jsonl

Đầu ra (data/processed/l2/, mỗi văn bản một bộ):
  l2_edges_<doc_id>.jsonl       contains / part_of, cha lấy từ thuộc tính `parent` của L1
  l2_refs_<doc_id>.jsonl        refers_to đã nối, kèm câu nguyên văn (evidence)
  l2_pending_<doc_id>.jsonl     dẫn chiếu tới văn bản/phụ lục chưa có trong kho: quan hệ chờ đích (nối khi văn bản đích được nạp)
  l2_unresolved_<doc_id>.jsonl  cụm đọc được nhưng không giải được (kèm lý do): không đoán
Báo cáo chữ: docs/bao_cao_chay/l2/l2_report_<doc_id>.txt.

Mọi cụm dẫn chiếu thuộc đúng một trong ba trạng thái: đã nối, chờ đích, unresolved. Không có cạnh nào trỏ tới mã không tồn tại.
Dòng chỉ thị sửa đổi ("Sửa đổi, bổ sung khoản 6 Điều 7 như sau:") KHÔNG sinh refers_to: dẫn chiếu trong đó trỏ vào văn bản bị sửa, việc
của L6. Quyết định chỗ spec im lặng: docs/quyet_dinh/l2_quyet_dinh.txt.
"""
import argparse
import collections
import datetime
import itertools
import re
import sys
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import parse as l1
import corpus

L2_DIR_NAME = "l2"

# ---- cụm dẫn chiếu: chuỗi mục "từ khoá + đối số" ----
# Điều/khoản: số có hậu tố chữ (Điều 20a, khoản 8a); điểm: một chữ kèm số tuỳ chọn (điểm a, điểm a1); "này" đứng riêng.
# Một mục có thể là danh sách cùng loại: "khoản 1, 2 và 3", "điểm a, b và đ", "Điều 5 và 6".
_NUM = r"\d+[a-z]?(?!\w)"
_LET = r"[a-zđ]\d?(?!\w)"
_LISTSEP = r"(?:,[ ]*|[ ]+(?:và|hoặc)[ ]+)"
_NUMLIST = rf"{_NUM}(?:{_LISTSEP}{_NUM})*"
_LETLIST = rf"{_LET}(?:{_LISTSEP}{_LET})*"
_ITEM = rf"(?<!\w)(?:(?:điều|khoản)[ ]+(?:này(?!\w)|{_NUMLIST})|điểm[ ]+(?:này(?!\w)|{_LETLIST}))"
_SEP = r"(?:[,;][ ]*|[ ]+(?:và|hoặc)[ ]+|[ ]+của[ ]+|[ ]+)"  # "khoản 6 của Điều 7" nối hai mục; "của Bộ luật này" là đuôi, không phải mục
CHAIN_RE = re.compile(rf"{_ITEM}(?:{_SEP}{_ITEM})*", re.I)
ITEM_RE = re.compile(rf"(?<!\w)(?:(điều|khoản)[ ]+(này(?!\w)|{_NUMLIST})|(điểm)[ ]+(này(?!\w)|{_LETLIST}))", re.I)
KEYWORD_RE = re.compile(r"(?<!\w)(?:điều|khoản|điểm)[ ]+(?:\d|này(?!\w)|[a-zđ]\d?(?!\w))", re.I)
LEVEL = {"điều": 0, "khoản": 1, "điểm": 2}
LEVEL_TYPE = ("dieu", "khoan", "diem")

# Phụ lục: "Phụ lục I", "Phụ lục I.7", "Phụ lục 2"; kèm "ban hành kèm theo <văn bản>" thì đuôi là văn bản đó.
PL_REF_RE = re.compile(r"(?<!\w)Phụ lục[ ]+([IVX]+(?:\.\d+)?|\d+)(?!\w)(?:[ ]+ban hành kèm theo)?")

# Đuôi văn bản ngay sau cụm: "của Bộ luật này", "Nghị định số 145/2020/NĐ-CP", "Bộ luật Lao động", "Luật Việc làm".
KINDS = r"(?:Hiến pháp|Bộ luật|Luật|Pháp lệnh|Nghị quyết|Nghị định|Quyết định|Thông tư)"
TAIL_KIND_RE = re.compile(rf"[ ]+(?:của[ ]+)?({KINDS})(?!\w)")
NUMBER_RE = r"\d+(?:\.\d+)?/(?:\d{4}/)?[A-ZĐ][A-Za-zĐđ0-9\-]*"
TAIL_NUM_RE = re.compile(rf"(?:[ ]+[^\W\d_]+){{0,6}}?[ ]+số[ ]+({NUMBER_RE})")
# Tên văn bản không số hiệu ("Luật Bảo hiểm xã hội", "Bộ luật Lao động") gồm các chữ LIỀN NHAU sau loại văn bản, kể cả chữ thường; dừng ở dấu câu,
# chữ số, hoặc từ dừng dưới đây (từ nối, từ đầu mệnh đề sau tên, từ khoá của một dẫn chiếu khác). Danh sách này viết tay theo chữ gặp trong kho (A23).
NAME_STOP = {"quy", "này", "ngày", "của", "để", "thì", "mà", "là", "được", "có", "và", "hoặc", "về", "do", "theo", "trong", "khi",
             "đi", "năm", "không", "như", "nhưng", "điều", "khoản", "điểm", "chương", "mục", "phụ", "luật", "nghị", "thông", "quyết"}
NAME_MAX_WORDS = 8
# Dấu phẩy thường là hết tên ("Luật Công đoàn, hoặc ..."), nên chỉ nhận tên có dấu phẩy bên trong khi nó nằm trong danh sách này (viết tay).
LAW_NAMES_WITH_COMMA = ("An toàn, vệ sinh lao động",)
NAME_WORD_RE = re.compile(r"[ ]+([^\W\d_][\w]*)")
SELF_KIND = {"Bộ luật": ("bo_luat", "van_ban_hop_nhat"), "Luật": ("bo_luat", "van_ban_hop_nhat"), "Nghị định": ("nghi_dinh",),
             "Nghị quyết": ("nghi_quyet_cp",), "Thông tư": ("thong_tu",)}

# Bộ luật Lao động 2012: ngoài kho. Số hiệu lấy từ hiểu biết ngoài repo (không đối chiếu được trong kho): ghi vào quyết định L2.
BLLD_2012 = "10/2012/QH13"
BLLD_NAME = "Bộ luật Lao động"
BLLD_2019_DATE = datetime.date(2019, 11, 20)
BLLD_2019_EFFECTIVE = datetime.date(2021, 1, 1)

# Dòng chỉ thị sửa đổi: động từ chỉ thị đi liền một danh từ đích ("Sửa đổi, bổ sung khoản 6 ...", "Bãi bỏ điểm c ...", "Thay thế cụm từ ...").
# Không nhận "Sửa chữa, làm sai lệch ...", "Thay đổi cơ cấu ...", "Thay thế người lao động ...": đó là điều quy tắc bình thường. Việc của L6.
DIRECTIVE_RE = re.compile(r"^(?:Sửa đổi, bổ sung|Sửa đổi|Bổ sung|Bãi bỏ|Thay thế, bổ sung|Thay thế|Đổi tên|Hủy bỏ|Bỏ|Đính chính|Tạm ngưng|Đình chỉ)[ ]+"
                          r"(?:một[ ]+số[ ]+|các[ ]+|toàn[ ]+bộ[ ]+)?(?:tên[ ]+)?"
                          r"(?:điều|khoản|điểm|mục|chương|phụ[ ]+lục|mẫu|cụm[ ]+từ|từ|đoạn|nội[ ]+dung|quy[ ]+định|tiết|hiệu[ ]+lực|thi[ ]+hành|việc[ ]+thi[ ]+hành)(?!\w)", re.I)

PENDING_EDGE = "refers_to"


class Ref(NamedTuple):
    unit: str
    phrase: str      # cụm nguyên văn, gồm cả đuôi văn bản nếu có
    start: int
    end: int
    items: list      # [(cấp, [đối số])] theo thứ tự xuất hiện; rỗng với tham chiếu phụ lục
    pl: str | None   # nhãn phụ lục nếu là tham chiếu phụ lục
    tail: object     # DocTail hoặc None


class DocTail(NamedTuple):
    kind: str            # Bộ luật / Nghị định / ...
    self_ref: bool       # "<loại> này"
    number: str | None   # số hiệu nếu có
    name: str | None     # tên nếu không có số (Bộ luật Lao động, Luật Việc làm)
    end: int             # vị trí hết đuôi trong text


def norm_number(s):
    return re.sub(r"\s", "", s).upper()


# ---- cạnh cấu trúc ----
PARENT_TYPES = {
    "chuong": {None}, "muc": {"chuong", None}, "dieu": {"muc", "chuong", None}, "khoan": {"dieu"},
    "diem": {"khoan", "dieu"}, "pl": {None}, "pl_muc": {"pl", "pl_muc"}, "pl_row": {"pl", "pl_muc"},
}


def build_structure_edges(units):
    """Mỗi cặp cha-con trực tiếp thành 2 cạnh (cha, contains, con) rồi (con, part_of, cha), theo thứ tự đơn vị trong L1."""
    edges = []
    for uid, u in units.items():
        parent = u.get("parent")
        if parent is not None:
            edges.append((parent, "contains", uid))
            edges.append((uid, "part_of", parent))
    return edges


def check_structure(units, edges):
    """Lỗi cấu trúc (rỗng nếu sạch): cha tồn tại và đúng loại, mỗi đơn vị đúng một cha (hoặc là gốc), cạnh đối xứng, không trùng."""
    errors = []
    for edge, n in collections.Counter(edges).items():
        if n > 1:
            errors.append(f"cạnh trùng {n} lần: {edge}")
    contains = collections.Counter((s, o) for s, p, o in edges if p == "contains")
    part_of = collections.Counter((o, s) for s, p, o in edges if p == "part_of")
    if contains != part_of:
        errors.append("contains và part_of không đối xứng")
    n_parents = collections.Counter(o for _, o in contains)
    for uid, u in units.items():
        parent = u.get("parent")
        ptype = units[parent]["type"] if parent in units else None
        if parent is not None and parent not in units:
            errors.append(f"{uid}: cha {parent} không có trong tập đơn vị")
        elif ptype not in PARENT_TYPES[u["type"]]:
            errors.append(f"{uid} (type {u['type']}) có cha type {ptype}, mong đợi {PARENT_TYPES[u['type']]}")
        if n_parents[uid] != (0 if parent is None else 1):
            errors.append(f"{uid}: {n_parents[uid]} cạnh cha, mong đợi {0 if parent is None else 1}")
    return errors


# ---- tìm cụm dẫn chiếu ----

def merge_runs(items):
    """[(cấp, [đối số])] -> các mục liền nhau cùng cấp gộp một nhóm ('khoản 1 và khoản 3' -> (1, ['1','3']))."""
    runs = []
    for level, group in itertools.groupby(items, key=lambda it: it[0]):
        runs.append((level, [a for _, args in group for a in args]))
    return runs


class Group(NamedTuple):
    items: list  # [(cấp, [đối số])] chưa gộp
    start: int
    end: int


def split_chain(text, start, end):
    """Tách một chuỗi mục thành các dẫn chiếu riêng. Một dẫn chiếu mới bắt đầu khi cấp đi từ thô xuống mịn
    ('Điều 18, điểm a khoản 1 Điều 145': Điều rồi điểm) hoặc ngay sau một mục 'này' ('khoản 8 Điều này, Điều 24')."""
    groups, cur, last_level, last_this = [], [], None, False
    for m in ITEM_RE.finditer(text, start, end):
        level = LEVEL[(m[1] or m[3]).casefold()]
        body = m[2] or m[4]
        args = ["này"] if body.casefold() == "này" else [a.lower() for a in re.split(_LISTSEP, body)]
        # "điểm e, g, h khoản 2 Điều 7 và Điều 14": mục Điều thứ hai sau một chuỗi đã có mục cấp thấp là dẫn chiếu riêng
        if cur and (level > last_level or last_this or (level == 0 == last_level and len(cur) > 1)):
            groups.append(Group(cur, cur_start, cur_end))
            cur = []
        if not cur:
            cur_start = m.start()
        cur.append((level, args))
        cur_end, last_level, last_this = m.end(), level, args == ["này"]
    if cur:
        groups.append(Group(cur, cur_start, cur_end))
    # Viết lược: "điểm h khoản 1 và điểm đ khoản 2 Điều này" - Điều chỉ nêu ở dẫn chiếu cuối, dùng chung cho các dẫn chiếu trước.
    for i in range(len(groups) - 2, -1, -1):
        nxt = groups[i + 1]
        if groups[i].items[-1][0] > 0 and nxt.items[-1][0] == 0:
            groups[i] = Group(groups[i].items + [nxt.items[-1]], groups[i].start, groups[i].end)
    return groups


def parse_tail(text, pos):
    """Đuôi văn bản đứng ngay sau vị trí pos (hết cụm), hoặc None."""
    m = TAIL_KIND_RE.match(text, pos)
    if not m:
        return None
    kind = m[1]
    after = m.end()
    rest = text[after:]
    if re.match(r"[ ]+này(?!\w)", rest, re.I):
        return DocTail(kind, True, None, None, after + len(re.match(r"[ ]+này", rest, re.I)[0]))
    mnum = TAIL_NUM_RE.match(rest)
    if mnum:
        return DocTail(kind, False, norm_number(mnum[1]), None, after + mnum.end())
    if kind == "Luật":
        for named in LAW_NAMES_WITH_COMMA:
            if text.startswith(" " + named, after):
                return DocTail(kind, False, None, f"{kind} {named}", after + 1 + len(named))
    words, ends = [], []
    while len(words) < NAME_MAX_WORDS:
        w = NAME_WORD_RE.match(text, ends[-1] if ends else after)  # match (không finditer): từ kế phải LIỀN, không nhảy qua dấu câu hay xuống dòng
        if not w or w[1].casefold() in NAME_STOP:
            break
        words.append(w[1])
        ends.append(w.end())
    if kind == "Bộ luật" and words[:2] == ["Lao", "động"]:  # tên đã đủ; chữ hoa liền sau (nếu có) là đầu câu khác, không phải của tên
        words, ends = words[:2], ends[:2]
    return DocTail(kind, False, None, " ".join([kind, *words]) if words else kind, ends[-1] if ends else after)


def find_refs(unit_id, text):
    """Các cụm dẫn chiếu trong text của một đơn vị: điều/khoản/điểm và phụ lục, kèm đuôi văn bản."""
    refs = []
    for m in CHAIN_RE.finditer(text):
        tail = parse_tail(text, m.end())
        chain_end = tail.end if tail else m.end()
        groups = split_chain(text, m.start(), m.end())
        for i, g in enumerate(groups):
            this = g.items[-1][1] == ["này"]  # dẫn chiếu kết thúc bằng 'này' tự nêu văn bản; còn lại dùng đuôi chung của chuỗi
            end = chain_end if i == len(groups) - 1 and not this else g.end
            refs.append(Ref(unit_id, text[g.start:end], g.start, end, merge_runs(g.items), None, None if this else tail))
    for m in PL_REF_RE.finditer(text):
        tail = parse_tail(text, m.end())
        end = tail.end if tail else m.end()
        refs.append(Ref(unit_id, text[m.start():end], m.start(), end, [], m[1].replace(".", "_"), tail))
    return sorted(refs, key=lambda r: r.start)


def uncovered_keywords(text, refs):
    """Từ khoá 'điều/khoản/điểm' kèm đối số mà không nằm trong cụm nào (chỉ để báo cáo)."""
    spans = [(r.start, r.end) for r in refs]
    return [m[0] for m in KEYWORD_RE.finditer(text) if not any(a <= m.start() < b for a, b in spans)]


def is_directive(text):
    """Dòng chỉ thị sửa đổi (xem DIRECTIVE_RE), xét dòng đầu của text."""
    return bool(DIRECTIVE_RE.match(text.split("\n")[0].strip()))


# ---- đích của cụm ----

def code_segment(level, arg):
    """Đoạn mã: Điều 5 -> D5, khoản 2 -> K2, điểm a -> a (đ -> dd như id của L1)."""
    return f"D{arg}" if level == 0 else f"K{arg}" if level == 1 else l1.diem_code(arg)


def enclosing(unit_id, level, units):
    """Tổ tiên (hoặc chính nó) có type đúng cấp level, đi ngược theo `parent`. Không có thì None."""
    cur = units.get(unit_id)
    while cur is not None:
        if cur["type"] == LEVEL_TYPE[level]:
            return cur["id"]
        cur = units.get(cur.get("parent"))
    return None


def chain_targets(source, runs, units, doc_id):
    """Mã đích trong văn bản doc_id; (danh sách, lý do lỗi). Cấp phải giảm liên tiếp và kết thúc ở Điều hoặc 'này'.
    Cụm nhiều cấp chỉ một đích sâu nhất ('điểm a khoản 1 Điều 5'); nhóm cấp cao cuối cùng dùng chung cho nhóm trước nó."""
    levels = [lv for lv, _ in runs]
    if levels != list(range(levels[0], levels[0] - len(levels), -1)):
        return None, f"cấp các mục không giảm liên tiếp {levels}"
    anchor_level, anchor_args = runs[-1]
    this = [args == ["này"] for _, args in runs]
    if any(this[:-1]) or (this[-1] and len(anchor_args) > 1):
        return None, "'này' chỉ được là mục đứng cuối và đứng riêng"
    if any(len(args) > 1 for _, args in runs[1:]) and len(runs) > 1:
        return None, "mục cấp trên có nhiều hơn một đối số"  # chỉ mục thấp nhất được là danh sách ('khoản 1, 2 và 3 Điều 5')
    if this[-1]:
        if anchor_level == 2:
            return None, "'điểm này' chưa có quy tắc"
        encl = enclosing(source, anchor_level, units)
        if encl is None:
            return None, f"không có {LEVEL_TYPE[anchor_level]} chứa {source}"
        prefixes = [encl]
    elif anchor_level == 0:
        prefixes = [f"{doc_id}.{code_segment(0, a)}" for a in anchor_args]
    else:
        return None, "cụm kết thúc bằng khoản/điểm, không có Điều"
    for level, args in reversed(runs[:-1]):
        prefixes = [f"{p}.{code_segment(level, a)}" for p in prefixes for a in args]
    return prefixes, None


# ---- giải văn bản đích ----

class Resolver:
    """Giải đuôi văn bản thành doc_id trong kho, hoặc đích chờ. Chọn Bộ luật Lao động 2012/2019 theo dòng 'Căn cứ' của văn bản nguồn."""

    def __init__(self, docs, headers):
        self.docs = docs
        self.by_number = {norm_number(d.so_hieu): d.doc_id for d in docs.values()}
        self.headers = headers

    def blld_year(self, source_doc):
        """2019 hay 2012 cho cụm 'Bộ luật Lao động' không kèm số: ngày trong dòng 'Căn cứ Bộ luật Lao động ngày ...' của văn bản
        nguồn; không có dòng đó (mất đầu văn bản) thì theo ngày hiệu lực của văn bản nguồn (>= 01/01/2021 là bản 2019)."""
        for g in self.headers.get(source_doc.doc_id, {}).get("grounds", []):
            if g.startswith("Căn cứ Bộ luật Lao động"):
                d = corpus.find_vn_date(g)
                if d is not None:
                    return 2019 if d >= BLLD_2019_DATE else 2012
        return 2019 if source_doc.ngay_hieu_luc >= BLLD_2019_EFFECTIVE else 2012

    def resolve(self, tail, source_doc):
        """-> ("doc", doc_id) | ("pending", số hiệu hoặc None, tên hoặc None) | ("error", lý do)."""
        if tail is None:
            return ("doc", source_doc.doc_id)
        if tail.self_ref:
            if source_doc.doc_type not in SELF_KIND.get(tail.kind, ()):
                return ("error", f"'{tail.kind} này' trong văn bản loại {source_doc.doc_type}")
            return ("doc", source_doc.doc_id)
        if tail.number:
            doc_id = self.by_number.get(tail.number)
            return ("doc", doc_id) if doc_id else ("pending", tail.number, None)
        if tail.name == BLLD_NAME or (tail.name or "").startswith(BLLD_NAME):
            if source_doc.doc_id == corpus.BASE_DOC_ID or source_doc.is_consolidation:
                return ("doc", source_doc.doc_id)
            if self.blld_year(source_doc) == 2019:
                return ("doc", corpus.BASE_DOC_ID)
            return ("pending", BLLD_2012, tail.name)
        return ("pending", None, tail.name)


class Result(NamedTuple):
    edges: list       # (s, "refers_to", o, evidence)
    pending: list     # dict
    unresolved: list  # dict
    skipped_directive: list  # (unit, đầu dòng)
    uncovered: list   # (unit, từ khoá)
    n_refs: int


class Resolved(NamedTuple):
    targets: list         # mã đích đã kiểm có trong kho
    missing: list         # [(mã đích, lý do)] đích đọc được nhưng không tồn tại
    pending: dict | None  # quan hệ chờ đích nếu văn bản/phụ lục đích chưa có trong KB
    error: str | None     # cụm không giải được


def resolve_ref(doc, uid, units, ref, all_units, resolver, available):
    """Giải một cụm dẫn chiếu của đơn vị uid (văn bản doc) thành đích. Dùng chung cho L2 (refers_to), L5 tường minh và L5 chung (exception_of).
    available: các văn bản đã có trong KB; đích thuộc văn bản chưa có thì thành quan hệ chờ đích."""
    res = resolver.resolve(ref.tail, doc)
    if res[0] == "error":
        return Resolved([], [], None, res[1])
    if res[0] == "pending" or res[1] not in available:
        number = res[1] if res[0] == "pending" else resolver.docs[res[1]].so_hieu
        name = res[2] if res[0] == "pending" else None
        if ref.pl is not None:
            tgt = [f"PL{ref.pl}"]
        else:
            sub, why = chain_targets(uid, ref.items, units, "X")
            if why:
                return Resolved([], [], None, why)
            tgt = [t[2:] for t in sub]
        return Resolved([], [], {"source": uid, "edge": PENDING_EDGE, "target_number": number, "target_name": name,
                                 "target_units": tgt, "text": ref.phrase}, None)
    target_doc = res[1]
    tunits = all_units[target_doc]
    if ref.pl is not None:
        targets, why = [f"{target_doc}.PL{ref.pl}"], None
    else:
        targets, why = chain_targets(uid, ref.items, units if target_doc == doc.doc_id else tunits, target_doc)
        if targets is not None and target_doc != doc.doc_id and any(a == ["này"] for _, a in ref.items):
            why = "'này' dẫn tới văn bản khác"
    if why:
        return Resolved([], [], None, why)
    found, missing = [], []
    for t in targets:
        if t == uid:
            continue
        if t in tunits:
            found.append(t)
        else:
            implicit = " (cụm không nêu văn bản đích; văn bản đích có thể nằm ở câu dẫn, việc của L3)" if ref.tail is None else ""
            missing.append((t, f"phụ lục {t} không có trong kho (file nguồn không kèm phụ lục này)" if ref.pl is not None
                            else f"đích {t} không có trong {target_doc}{implicit}"))
    return Resolved(found, missing, None, None)


def extract(doc, units, all_units, resolver, available):
    """Dẫn chiếu của mọi đơn vị trong `units` (văn bản doc). all_units: {doc_id: units} của các văn bản đã đọc.
    available: tập doc_id được coi là đã có trong KB; đích thuộc kho nhưng chưa nạp thì vào chờ đích."""
    edges, pending, unresolved, skipped, uncovered = [], [], [], [], []
    seen_edges, seen_unres = set(), set()
    n_refs = 0

    def add_unresolved(unit, phrase, reason):  # cùng cụm, cùng lý do chỉ ghi một lần
        if (unit, phrase, reason) not in seen_unres:
            seen_unres.add((unit, phrase, reason))
            unresolved.append({"unit": unit, "phrase": phrase, "reason": reason})

    for uid, u in units.items():
        if u["type"] not in ("dieu", "khoan", "diem") or not u.get("text"):
            continue
        text = u["text"]
        if is_directive(text):
            skipped.append((uid, text.split("\n")[0][:70]))
            continue
        refs = find_refs(uid, text)
        uncovered += [(uid, k) for k in uncovered_keywords(text, refs)]
        for ref in refs:
            n_refs += 1
            r = resolve_ref(doc, uid, units, ref, all_units, resolver, available)
            if r.error:
                add_unresolved(uid, ref.phrase, r.error)
            if r.pending:
                pending.append(r.pending)
            for t, reason in r.missing:
                add_unresolved(uid, ref.phrase, reason)
            for t in r.targets:
                if (uid, t) not in seen_edges:  # nhiều cụm cùng trỏ một đích: giữ cụm đầu làm evidence
                    seen_edges.add((uid, t))
                    edges.append((uid, "refers_to", t, ref.phrase))
    return Result(edges, pending, unresolved, skipped, uncovered, n_refs)


def check_refs(doc, units, all_units, result):
    """Lỗi (rỗng nếu sạch): không trùng, không tự trỏ, hai đầu tồn tại, evidence nằm trong text nguồn."""
    errors = []
    for key, n in collections.Counter((s, o) for s, _, o, _ in result.edges).items():
        if n > 1:
            errors.append(f"cạnh trùng {n} lần: {key}")
    for s, p, o, ev in result.edges:
        tdoc = o.split(".")[0]
        if s == o:
            errors.append(f"{s} refers_to chính nó")
        if s not in units:
            errors.append(f"{s}: không có trong tập đơn vị")
        elif ev not in units[s].get("text", ""):
            errors.append(f"{s} -> {o}: evidence {ev!r} không nằm trong text của {s}")
        if o not in all_units.get(tdoc, {}):
            errors.append(f"{s} -> {o}: đích không tồn tại")
    return errors


def load_all_units(docs):
    out = {}
    for doc_id in docs:
        if l1.triples_path(doc_id).exists():
            out[doc_id] = l1.load_units(doc_id)
    return out


def load_headers():
    path = corpus.PROCESSED_DIR / "documents.jsonl"
    return {d["doc_id"]: d for d in l1.read_jsonl(path)} if path.exists() else {}


def load_context():
    """(docs, all_units, resolver, available) cho các bước đọc L1/L2 của cả kho. L2 tĩnh: mọi văn bản đã có L1 coi là đã nạp."""
    docs = corpus.load_manifest()
    all_units = load_all_units(docs)
    return docs, all_units, Resolver(docs, load_headers()), set(all_units)


def l2_dir():
    return corpus.out_dir(L2_DIR_NAME)


def write_outputs(doc, structure, result):
    d = l2_dir()
    # Khuôn cạnh chung (A12): {s, p, o, evidence, how, flags}. Cạnh cha-con không có câu bằng chứng (lấy từ thuộc tính `parent` của bước parse): how="parent".
    l1.write_jsonl(d / f"l2_edges_{doc.doc_id}.jsonl", [{"s": s, "p": p, "o": o, "evidence": "", "how": "parent", "flags": []} for s, p, o in structure])
    l1.write_jsonl(d / f"l2_refs_{doc.doc_id}.jsonl",
                   [{"s": s, "p": p, "o": o, "evidence": ev, "how": "regex", "flags": []} for s, p, o, ev in result.edges])
    l1.write_jsonl(d / f"l2_pending_{doc.doc_id}.jsonl", result.pending)
    l1.write_jsonl(d / f"l2_unresolved_{doc.doc_id}.jsonl", result.unresolved)


def report_text(doc, units, structure, result):
    per_target = collections.Counter(o.split(".")[0] for _, _, o, _ in result.edges)
    out = [f"L2 báo cáo: {doc.doc_id}", f"số đơn vị: {len(units)}  cạnh cấu trúc: {len(structure)}",
           f"cụm dẫn chiếu: {result.n_refs} = nối {len(result.edges)} cạnh + chờ đích {len(result.pending)} + unresolved {len(result.unresolved)}"
           f" (một cụm có thể ra nhiều đích)",
           f"refers_to theo văn bản đích: {dict(per_target)}",
           f"dòng chỉ thị sửa đổi bỏ qua (việc của L6): {len(result.skipped_directive)}",
           f"từ khoá điều/khoản/điểm kèm số nằm ngoài mọi cụm: {len(result.uncovered)}"]
    pend = collections.Counter((p["target_number"] or p["target_name"]) for p in result.pending)
    out.append(f"chờ đích theo văn bản: {dict(pend)}")
    out.append("unresolved:")
    out += [f"  {u['unit']}: {u['phrase']!r}: {u['reason']}" for u in result.unresolved] or ["  (không có)"]
    out.append("dòng chỉ thị bỏ qua (mẫu):")
    out += [f"  {u}: {t}" for u, t in result.skipped_directive[:8]] or ["  (không có)"]
    out.append("từ khoá ngoài cụm (mẫu):")
    out += [f"  {u}: {k}" for u, k in result.uncovered[:8]] or ["  (không có)"]
    return "\n".join(out) + "\n"


def run_doc(doc, docs, all_units, resolver, available):
    units = all_units[doc.doc_id]
    structure = build_structure_edges(units)
    errors = check_structure(units, structure)
    result = extract(doc, units, all_units, resolver, available)
    errors += check_refs(doc, units, all_units, result)
    path = corpus.report_dir(L2_DIR_NAME) / f"l2_report_{doc.doc_id}.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report_text(doc, units, structure, result) + (("LỖI KIỂM:\n" + "\n".join(errors) + "\n") if errors else ""),
                    encoding="utf-8", newline="\n")
    if not errors:
        write_outputs(doc, structure, result)
    return structure, result, errors


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("target", nargs="?", help="doc_id")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args(argv)
    docs = corpus.load_manifest()
    targets = list(docs.values()) if args.all else [corpus.get_doc(args.target, docs)] if args.target else ap.error("cần doc_id hoặc --all")
    all_units = load_all_units(docs)
    missing = [d.doc_id for d in targets if d.doc_id not in all_units]
    if missing:
        raise SystemExit(f"chưa có l1 của {missing}; chạy src/parse.py trước")
    resolver = Resolver(docs, load_headers())
    available = set(all_units)  # L2 tĩnh: mọi văn bản trong kho coi là đã có; L6/L11 truyền tập đã nạp theo ngày
    bad, pending_all = [], []
    for doc in targets:
        structure, result, errors = run_doc(doc, docs, all_units, resolver, available)
        print(f"{doc.doc_id:<22} cấu trúc {len(structure):>5}  refers_to {len(result.edges):>4}  chờ {len(result.pending):>3}  "
              f"unresolved {len(result.unresolved):>3}  chỉ thị bỏ qua {len(result.skipped_directive):>3}  {'OK' if not errors else 'LỖI'}")
        pending_all += result.pending
        if errors:
            bad.append((doc, errors))
    if bad:
        for doc, errors in bad:
            print(f"\nLỖI {doc.doc_id}:", file=sys.stderr)
            for e in errors[:20]:
                print("  ", e, file=sys.stderr)
        raise SystemExit(1)
    if args.all:
        l1.write_jsonl(corpus.PROCESSED_DIR / "pending_links.jsonl", pending_all)
        print(f"đã ghi {corpus.PROCESSED_DIR / 'pending_links.jsonl'} ({len(pending_all)} quan hệ chờ đích)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()
