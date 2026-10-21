"""A2a: cạnh cấu trúc contains / part_of giữa Điều > Khoản > Điểm.

Chỉ đọc triples của A1 (data/processed/a1_triples_<stem>.jsonl), không import a1_parse: nếu A1 đánh mã sai thì
lỗi hiện ra ở đây thay vì bị che, vì cha được suy từ chuỗi mã còn kiểm tra dùng thuộc tính type của A1.

Chạy: python -I src/a2_edges.py <file md nguồn>          (bắt buộc truyền path, không có mặc định)
      python -I src/a2_edges.py <file md nguồn> --refs   (Bước 2: chỉ in dẫn chiếu và bảng hình dạng, không ghi file)
      python -I src/a2_edges.py <file md nguồn> --refers-to   (A2b: ghi a2_refs_<stem>.jsonl và docs/a2_unresolved_<stem>.txt)
      python -I src/a2_edges.py <file md nguồn> --triggers   (A3 bước 1: chỉ in cụm trừ / ngoại trừ / không áp dụng, không ghi file)
"""
import argparse
import collections
import itertools
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT / "data" / "processed"

# Loại của cha mà mỗi loại con phải có. Nguồn là thuộc tính type của A1, độc lập với chuỗi mã.
PARENT_TYPE = {"khoan": "dieu", "diem": "khoan"}

# Thuộc tính của đơn vị mà hàm nạp giữ lại (text có thể vắng); heading, version không dùng ở A2a.
REQUIRED_ATTRS = ("type", "number", "source_line")
KEPT_ATTRS = REQUIRED_ATTRS + ("text",)


def triples_path(src):
    return PROCESSED_DIR / f"a1_triples_{Path(src).stem}.jsonl"


def edges_path(src):
    return PROCESSED_DIR / f"a2_edges_{Path(src).stem}.jsonl"


def load_units(path):
    """Gom triples theo s thành {id: {type, number, text (nếu có), source_line}}, giữ thứ tự xuất hiện trong file."""
    units = {}
    with open(path, encoding="utf-8", newline="") as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            s, p, o = row["s"], row["p"], row["o"]
            if p not in KEPT_ATTRS:
                continue
            attrs = units.setdefault(s, {})
            if p in attrs:
                raise ValueError(f"{path}:{line_no}: {s} có thuộc tính {p} lặp")
            attrs[p] = o
    for s, attrs in units.items():
        missing = [a for a in REQUIRED_ATTRS if a not in attrs]
        if missing:
            raise ValueError(f"{path}: {s} thiếu thuộc tính {missing}")
    return units


def parent_of(code):
    """Cha của một mã, chỉ suy từ chuỗi mã: tách theo dấu chấm.

    2 đoạn là Điều, không có cha (None). Nhiều hơn 2 đoạn thì cha là các đoạn trừ đoạn cuối.
    Mã 1 đoạn, rỗng hoặc có đoạn rỗng thì báo lỗi, không đoán.
    """
    parts = code.split(".")
    if len(parts) < 2 or not all(parts):
        raise ValueError(f"mã không hợp lệ: {code!r}")
    return None if len(parts) == 2 else ".".join(parts[:-1])


def build_edges(units):
    """Mỗi cặp cha-con trực tiếp thành 2 cạnh (s, p, o): (cha, contains, con) rồi (con, part_of, cha).

    Duyệt theo thứ tự đơn vị trong file triples; hai cạnh của cùng một con nằm liền nhau.
    """
    edges = []
    for code in units:
        parent = parent_of(code)
        if parent is None:
            continue
        edges.append((parent, "contains", code))
        edges.append((code, "part_of", parent))
    return edges


def check_edges(units, edges):
    """Trả về list lỗi (rỗng nếu sạch). So loại của cha theo thuộc tính type của A1, không theo mã."""
    errors = []

    for edge, n in collections.Counter(edges).items():
        if n > 1:
            errors.append(f"cạnh trùng {n} lần: {edge}")

    contains = [(s, o) for s, p, o in edges if p == "contains"]
    part_of = [(o, s) for s, p, o in edges if p == "part_of"]  # đảo về (cha, con) để so với contains
    for s, o in contains:
        missing = [x for x in (s, o) if x not in units]
        if missing:
            errors.append(f"contains {s} -> {o}: không có trong tập đơn vị: {missing}")
            continue
        want = PARENT_TYPE.get(units[o]["type"])
        if units[s]["type"] != want:
            errors.append(f"{o} (type {units[o]['type']}) có cha {s} (type {units[s]['type']}), "
                          f"mong đợi cha type {want}")
    if collections.Counter(contains) != collections.Counter(part_of):
        errors.append(f"contains và part_of không đối xứng: chỉ có contains {sorted(set(contains) - set(part_of))}, "
                      f"chỉ có part_of {sorted(set(part_of) - set(contains))}")

    # mỗi đơn vị không phải Điều có đúng một cha, Điều không có cha
    n_parents = collections.Counter(o for _, o in contains)
    for code, u in units.items():
        want = 0 if u["type"] == "dieu" else 1
        if n_parents[code] != want:
            errors.append(f"{code} (type {u['type']}) có {n_parents[code]} cha, mong đợi {want}")
    n_children = sum(1 for u in units.values() if u["type"] != "dieu")
    if len(contains) != n_children:
        errors.append(f"số contains = {len(contains)}, số đơn vị type khác dieu = {n_children}")
    return errors


def write_edges(edges, path):
    """Ghi JSONL, mỗi dòng {"s","p","o","evidence"}. evidence rỗng cho cạnh cấu trúc."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for s, p, o in edges:
            f.write(json.dumps({"s": s, "p": p, "o": o, "evidence": ""}, ensure_ascii=False) + "\n")


def fail_if_errors(errors):
    if not errors:
        return
    print("\nLỖI KIỂM CẠNH (phải rỗng):", file=sys.stderr)
    for e in errors:
        print(" ", e, file=sys.stderr)
    raise SystemExit(1)


def read_units(src):
    tpath = triples_path(src)
    if not tpath.exists():
        raise SystemExit(f"chưa có {tpath}; chạy python src/a1_parse.py -s 4 {src} trước")
    return load_units(tpath)


def run(src):
    """Đọc triples của A1, dựng và kiểm cạnh, chỉ ghi khi sạch."""
    units = read_units(src)
    edges = build_edges(units)
    fail_if_errors(check_edges(units, edges))

    per_pred = collections.Counter(p for _, p, _ in edges)
    print("số đơn vị:", len(units), "| số cạnh:", len(edges), "| theo loại:", dict(per_pred))
    out = edges_path(src)
    write_edges(edges, out)
    print("đã ghi", out)


# ---- Bước 2: liệt kê dẫn chiếu trong text, chưa tạo cạnh ----

# Một cụm là chuỗi các mục "từ khoá + đối số" (đối số: số, một chữ điểm, hoặc "này"), nối bằng dấu cách, dấu phẩy,
# "và" hoặc "hoặc", có thể kèm đuôi "của Bộ luật này". Từ khoá không kèm đối số ("thời điểm mở", "điều kiện",
# "một khoản tiền") không thuộc cụm mà được đếm riêng là bị loại. Chỉ nối bằng dấu cách (không \s) nên cụm
# không vắt qua dòng mới giữa hai đoạn của một đơn vị.
_KW = r"(?:điều|khoản|điểm)"
_ARG = r"(?:\d+|này|[^\W\d_])(?!\w)"
_ITEM = rf"(?<!\w){_KW}[ ]+{_ARG}"
_SEP = r"(?:,[ ]*|[ ]+(?:và|hoặc)[ ]+|[ ]+)"
CHAIN_RE = re.compile(rf"{_ITEM}(?:{_SEP}{_ITEM})*(?: của Bộ luật này)?", re.I)
ITEM_RE = re.compile(rf"(?<!\w)({_KW})[ ]+(\d+|này|[^\W\d_])(?!\w)", re.I)  # để chuẩn hoá hình dạng
KEYWORD_RE = re.compile(rf"(?<!\w){_KW}(?!\w)", re.I)

CONTEXT_CHARS = 40  # số ký tự lấy quanh cụm


class Ref(NamedTuple):
    unit: str     # mã đơn vị chứa cụm
    phrase: str   # cụm nguyên văn
    shape: str    # hình dạng: số thành N, chữ điểm thành X
    context: str  # CONTEXT_CHARS ký tự mỗi bên của cụm


class Excluded(NamedTuple):
    unit: str
    keyword: str  # từ khoá nguyên văn
    after: str    # từ đứng ngay sau từ khoá, "" nếu không có


def shape_of(phrase):
    """Chuẩn hoá cụm: số thành N, chữ điểm thành X; giữ nguyên chữ hoa/thường của từ khoá, "này", và, hoặc, đuôi."""
    def norm(m):
        arg = m.group(2)
        kind = "N" if arg[0].isdigit() else "này" if arg.casefold() == "này" else "X"
        return f"{m.group(1)} {kind}"
    return ITEM_RE.sub(norm, phrase)


def find_refs(units):
    """Với mỗi đơn vị có text, trả về (refs, excluded, total): các cụm dẫn chiếu, các từ khoá bị loại, số từ khoá.

    total = số lần xuất hiện nguyên từ của điều/khoản/điểm (kể cả viết thường) = số từ khoá nằm trong cụm + len(excluded).
    """
    refs, excluded, total = [], [], 0
    for code, u in units.items():
        text = u.get("text")
        if not text:
            continue
        spans = []
        for m in CHAIN_RE.finditer(text):
            spans.append(m.span())
            context = text[max(0, m.start() - CONTEXT_CHARS):m.end() + CONTEXT_CHARS]
            refs.append(Ref(code, m.group(0), shape_of(m.group(0)), context))
        for m in KEYWORD_RE.finditer(text):
            total += 1
            if not any(a <= m.start() < b for a, b in spans):
                after = re.match(r"[ ]*(\w+)", text[m.end():])
                excluded.append(Excluded(code, m.group(0), after.group(1) if after else ""))
    return refs, excluded, total


def shape_table(refs):
    """Danh sách (hình dạng, số lần, ví dụ đầu tiên theo thứ tự file), xếp theo số lần giảm dần rồi theo hình dạng."""
    counts, example = collections.Counter(), {}
    for r in refs:
        counts[r.shape] += 1
        example.setdefault(r.shape, r)
    return [(shape, n, example[shape]) for shape, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]


def print_refs(refs, excluded, total):
    for r in refs:
        print(f"{r.unit}  {r.phrase!r}  {r.context!r}")
    print()
    print(f"{'số lần':>6}  {'hình dạng':<48}  ví dụ")
    for shape, n, ex in shape_table(refs):
        print(f"{n:>6}  {shape:<48}  {ex.unit}: {ex.phrase!r}")
    print()
    print(f"từ khoá: {total} = {total - len(excluded)} nằm trong {len(refs)} cụm + {len(excluded)} bị loại")
    by_kw = collections.defaultdict(collections.Counter)
    for e in excluded:
        by_kw[e.keyword.lower()][e.after] += 1
    for kw, after in sorted(by_kw.items()):
        print(f"  bị loại {kw}: {sum(after.values())}, từ theo sau:",
              ", ".join(f"{w or '(không có từ)'} {n}" for w, n in after.most_common()))


def run_refs(src):
    refs, excluded, total = find_refs(read_units(src))
    print_refs(refs, excluded, total)


# ---- A2b: cạnh refers_to từ các cụm dẫn chiếu ----

LEVEL = {"điều": 0, "khoản": 1, "điểm": 2}  # cấp của từ khoá: Điều > khoản > điểm
LEVEL_TYPE = ("dieu", "khoan", "diem")      # thuộc tính type của A1 theo cấp


def refs_path(src):
    return PROCESSED_DIR / f"a2_refs_{Path(src).stem}.jsonl"


def unresolved_path(src):
    """Mỗi file nguồn một file unresolved, để chạy file này không ghi đè file kia."""
    return ROOT / "docs" / f"a2_unresolved_{Path(src).stem}.txt"


def code_segment(level, arg):
    """Đoạn mã của một mục: Điều 5 -> D5, khoản 2 -> K2, điểm a -> a (đ -> dd như id của A1)."""
    if level == 0:
        return f"D{arg}"
    if level == 1:
        return f"K{arg}"
    return arg.replace("đ", "dd")


def enclosing_unit(source, level, units):
    """Tổ tiên (không tính chính source) có type đúng cấp level, đi ngược theo mã. Không có thì báo lỗi."""
    code = parent_of(source)
    while code is not None:
        if code not in units:
            raise ValueError(f"{source}: tổ tiên {code} không có trong tập đơn vị")
        if units[code]["type"] == LEVEL_TYPE[level]:
            return code
        code = parent_of(code)
    raise ValueError(f"{source}: không có tổ tiên type {LEVEL_TYPE[level]}")


def group_targets(source, phrase, units):
    """Các mã đích của một cụm dẫn chiếu nằm trong đơn vị source (chưa kiểm đích có tồn tại).

    Cụm là chuỗi mục có cấp giảm liên tiếp (điểm > khoản > Điều). Mục cấp cao đứng cuối dùng chung cho các mục đứng
    trước nó: 'khoản 1 và khoản 3 Điều 616' ra 2 đích, 'Điều 631 và Điều 632' ra 2 đích. Cụm nhiều cấp chỉ ra MỘT đích
    sâu nhất: 'điểm a khoản 1 Điều 630' ra D630.K1.a. 'Điều này' / 'khoản này' là tổ tiên đúng loại của source.
    Dạng chưa có quy tắc thì báo lỗi, không đoán: cấp nhảy hoặc tăng, mục cấp trên có nhiều mục, 'này' không đứng
    cuối hoặc không đứng riêng, 'điểm này', cụm kết thúc bằng khoản/điểm có số (không có Điều).
    """
    def bad(why):
        return ValueError(f"{source}: {why}: {phrase!r}")

    items = [(LEVEL[kw.casefold()], arg) for kw, arg in ITEM_RE.findall(phrase)]
    if not items:
        raise bad("cụm không có mục nào")
    runs = [list(run) for _, run in itertools.groupby(items, key=lambda it: it[0])]  # các mục liền nhau cùng cấp
    levels = [run[0][0] for run in runs]
    if levels != list(range(levels[0], levels[0] - len(levels), -1)):
        raise bad(f"cấp các mục không giảm liên tiếp {levels}")
    anchor = runs[-1]  # nhóm cấp cao nhất, đứng cuối
    this = [arg.casefold() == "này" for _, arg in items]
    if any(this[:-1]) or (this[-1] and len(anchor) > 1):
        raise bad("'này' chỉ được là mục đứng cuối và đứng riêng")
    if any(len(run) > 1 for run in runs[1:]):
        raise bad("mục cấp trên có nhiều hơn một mục")

    if this[-1]:
        if levels[-1] == 2:
            raise bad("'điểm này' chưa có quy tắc")
        prefixes = [enclosing_unit(source, levels[-1], units)]
    elif levels[-1] == 0:
        prefixes = [f"{source.split('.')[0]}.{code_segment(0, arg)}" for _, arg in anchor]
    else:
        raise bad("cụm kết thúc bằng khoản/điểm có số, không có Điều")
    for run in reversed(runs[:-1]):  # từ cấp cao xuống cấp thấp
        prefixes = [f"{p}.{code_segment(level, arg)}" for p in prefixes for level, arg in run]
    return prefixes


def dieu_of(code):
    """Mã Điều chứa một mã: hai đoạn đầu (BLDS2015.D616.K1.a -> BLDS2015.D616)."""
    return ".".join(code.split(".")[:2])


def build_refs(units):
    """Từ các cụm dẫn chiếu thành (edges, unresolved), theo thứ tự cụm trong file triples rồi thứ tự đích trong cụm.

    edges: (s, "refers_to", o, evidence): s là đơn vị chứa cụm, o là đích có trong units, evidence là cụm nguyên văn.
    unresolved: (s, cụm nguyên văn, đích); không tạo cạnh. Chỉ dành cho đích mà Điều của nó chưa được nạp.
    Đích không có trong units mà Điều của nó có (ví dụ 'khoản 9 Điều 616' khi D616 chỉ có K1-K3) thì báo lỗi.
    """
    edges, unresolved = [], []
    for ref in find_refs(units)[0]:
        for target in group_targets(ref.unit, ref.phrase, units):
            if target in units:
                edges.append((ref.unit, "refers_to", target, ref.phrase))
            elif dieu_of(target) in units:
                raise ValueError(f"{ref.unit}: đích {target} không có trong tập đơn vị dù {dieu_of(target)} có: {ref.phrase!r}")
            else:
                unresolved.append((ref.unit, ref.phrase, target))
    return edges, unresolved


def check_refs(units, edges, unresolved):
    """Trả về list lỗi (rỗng nếu sạch): không tự trỏ, không trùng, hai đầu tồn tại, evidence là đoạn của text nguồn."""
    errors = []
    for key, n in collections.Counter((s, p, o) for s, p, o, _ in edges).items():
        if n > 1:
            errors.append(f"cạnh trùng {n} lần: {key}")
    for s, p, o, evidence in edges:
        if p != "refers_to":
            errors.append(f"{s} -> {o}: p là {p!r}, mong đợi 'refers_to'")
        if s == o:
            errors.append(f"{s} refers_to chính nó: {evidence!r}")
        missing = [x for x in (s, o) if x not in units]
        if missing:
            errors.append(f"{s} -> {o}: không có trong tập đơn vị: {missing}")
        elif not evidence or evidence not in units[s].get("text", ""):
            errors.append(f"{s} -> {o}: evidence {evidence!r} không nằm trong text của {s}")
    for s, phrase, target in unresolved:
        if target in units:
            errors.append(f"{s}: {phrase!r} ghi unresolved nhưng {target} có trong tập đơn vị")
        elif dieu_of(target) in units:
            errors.append(f"{s}: {phrase!r} ghi unresolved nhưng {dieu_of(target)} (Điều của đích {target}) có trong tập đơn vị")
        if s not in units:
            errors.append(f"unresolved {s}: không có trong tập đơn vị")
    return errors


def write_ref_edges(edges, path):
    """Ghi JSONL, mỗi dòng {"s","p","o","evidence"}; evidence là cụm nguyên văn."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for s, p, o, evidence in edges:
            f.write(json.dumps({"s": s, "p": p, "o": o, "evidence": evidence}, ensure_ascii=False) + "\n")


def write_unresolved(unresolved, path):
    """Mỗi dòng: đơn vị nguồn, cụm nguyên văn, đích thiếu, cách nhau bằng tab. Ghi cả khi rỗng để không còn file cũ."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for s, phrase, target in unresolved:
            f.write(f"{s}\t{phrase}\t{target}\n")


def run_refers_to(src):
    """Dựng cạnh refers_to từ triples của A1, in từng cạnh, chỉ ghi file khi sạch."""
    units = read_units(src)
    try:
        edges, unresolved = build_refs(units)
    except ValueError as e:
        raise SystemExit(f"LỖI: {e}")
    fail_if_errors(check_refs(units, edges, unresolved))

    for s, _, o, evidence in edges:
        print(f"{s} → {o} | {evidence}")
    for s, phrase, target in unresolved:
        print(f"unresolved {s}: {phrase!r} (thiếu {target})")
    print("số đơn vị:", len(units), "| cạnh refers_to:", len(edges), "| unresolved:", len(unresolved))
    write_ref_edges(edges, refs_path(src))
    write_unresolved(unresolved, unresolved_path(src))
    print("đã ghi", refs_path(src))
    print("đã ghi", unresolved_path(src))


# ---- A3 bước 1: liệt kê cụm "trừ" / "ngoại trừ" / "không áp dụng", chưa tạo cạnh ----

# Ranh giới từ ở hai đầu nên "trừng", "trừu" không khớp. Quét từ trái sang phải nên "ngoại trừ" khớp từ chữ "ngoại" và
# thành một cụm, không đếm thêm "trừ" bên trong. Chỉ nối bằng dấu cách (không \s) nên cụm không vắt qua dòng mới.
TRIGGER_RE = re.compile(r"(?<!\w)(?:ngoại[ ]+trừ|trừ|không[ ]+áp[ ]+dụng)(?!\w)", re.I)
AFTER_WORDS = 6  # số từ lấy sau cụm; "từ" là chuỗi chữ \w+ (bỏ dấu câu), nên "trường hợp" tính 2 từ


class Trigger(NamedTuple):
    unit: str     # mã đơn vị chứa cụm
    phrase: str   # cụm nguyên văn
    kind: str     # "trừ", "ngoại trừ" hoặc "không áp dụng" (viết thường, một dấu cách)
    after: str    # tối đa AFTER_WORDS từ đứng sau cụm, dừng ở hết đoạn, nguyên chữ hoa/thường
    context: str  # CONTEXT_CHARS ký tự mỗi bên của cụm


def find_triggers(units):
    """Với mỗi đơn vị có text, trả về các cụm kích hoạt ngoại lệ theo thứ tự đơn vị trong file triples rồi thứ tự trong text."""
    triggers = []
    for code, u in units.items():
        text = u.get("text")
        if not text:
            continue
        for m in TRIGGER_RE.finditer(text):
            words = re.findall(r"\w+", text[m.end():].split("\n")[0])[:AFTER_WORDS]  # không vượt qua hết đoạn
            context = text[max(0, m.start() - CONTEXT_CHARS):m.end() + CONTEXT_CHARS]
            triggers.append(Trigger(code, m.group(0), re.sub(r"[ ]+", " ", m.group(0)).casefold(), " ".join(words), context))
    return triggers


def trigger_table(triggers):
    """Danh sách (6 từ sau viết thường, số lần, ví dụ đầu tiên theo thứ tự file), xếp theo số lần giảm dần rồi theo chữ."""
    counts, example = collections.Counter(), {}
    for t in triggers:
        key = t.after.casefold()
        counts[key] += 1
        example.setdefault(key, t)
    return [(key, n, example[key]) for key, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]


def print_triggers(triggers):
    for t in triggers:
        print(f"{t.unit}  {t.phrase!r}  {t.after!r}  {t.context!r}")
    print()
    table = trigger_table(triggers)
    width = max([len(key) for key, _, _ in table] + [len(f"{AFTER_WORDS} từ đứng sau")])
    print(f"{'số lần':>6}  {f'{AFTER_WORDS} từ đứng sau':<{width}}  ví dụ")
    for key, n, ex in table:
        print(f"{n:>6}  {key:<{width}}  {ex.unit}: {ex.phrase!r}")
    print()
    per_kind = collections.Counter(t.kind for t in triggers)
    print(f"từ khoá: {len(triggers)} cụm = trừ {per_kind['trừ']} + ngoại trừ {per_kind['ngoại trừ']} + "
          f"không áp dụng {per_kind['không áp dụng']} (ngoại trừ tính một cụm, không đếm thêm trừ bên trong)")


def run_triggers(src):
    print_triggers(find_triggers(read_units(src)))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="file md nguồn, dùng để suy stem của file triples A1")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--refs", action="store_true",
                      help="Bước 2: chỉ in danh sách dẫn chiếu và bảng hình dạng, không ghi file nào")
    mode.add_argument("--refers-to", action="store_true",
                      help="A2b: dựng cạnh refers_to, ghi a2_refs_<stem>.jsonl và docs/a2_unresolved_<stem>.txt")
    mode.add_argument("--triggers", action="store_true",
                      help="A3 bước 1: chỉ in cụm trừ / ngoại trừ / không áp dụng và bảng 6 từ đứng sau, không ghi file nào")
    args = ap.parse_args(argv)
    run_fn = run_refs if args.refs else run_refers_to if args.refers_to else run_triggers if args.triggers else run
    run_fn(args.path)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()
