"""A3: cạnh exception_of tường minh, chỉ hai quy tắc riêng (không có bộ khớp tổng quát).

Đầu vào: triples của A1 (a2.read_units) và cạnh contains của A2a (a2.build_edges).
Đầu ra: data/processed/a3_exceptions_<stem>.jsonl (s, p, o, evidence, method) và docs/a3_unhandled_<stem>.txt.
Chiều cạnh: s là phần ngoại lệ, o là quy tắc bị ngoại trừ.

  Quy tắc 1, not_apply_pattern: đơn vị U có "không áp dụng". Nếu cụm dẫn chiếu (a2.CHAIN_RE) đứng NGAY trước nó, chỉ
    cách dấu cách, thì mỗi đích của cụm (a2.group_targets) là o, s = U. Evidence là từ đầu cụm đến hết "không áp dụng".
  Quy tắc 2, except_list_pattern: text của U có "trừ" (hoặc "ngoại trừ") và kết thúc bằng "sau đây:". Mỗi đơn vị con trực
    tiếp C của U là s, o = U. Evidence là câu chứa "trừ", nằm trong text của U (= o); câu là toàn bộ text của đơn vị.

Mọi trigger (a2.TRIGGER_RE) phải rơi vào đúng một trong hai: đã xử lý (sinh cạnh) hoặc unhandled (mã đơn vị và câu).
Ca nằm ngoài hai quy tắc không được nới ra để bắt thêm; nó là ngoại lệ chung hoặc thuộc bước sau.

Chạy: python -I src/a3_exceptions.py <file md nguồn>   (bắt buộc truyền path, không có mặc định)
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import a2_edges as a2

PREDICATE = "exception_of"
NOT_APPLY = "not_apply_pattern"
EXCEPT_LIST = "except_list_pattern"
METHODS = (NOT_APPLY, EXCEPT_LIST)

NOT_APPLY_KIND = "không áp dụng"
EXCEPT_KINDS = ("trừ", "ngoại trừ")  # "ngoại trừ" là một cụm, cũng khớp quy tắc 2 (user xác nhận)
LIST_END = "sau đây:"


def exceptions_path(src):
    return a2.PROCESSED_DIR / f"a3_exceptions_{Path(src).stem}.jsonl"


def unhandled_path(src):
    """Mỗi file nguồn một file unhandled, để chạy file này không ghi đè file kia."""
    return a2.ROOT / "docs" / f"a3_unhandled_{Path(src).stem}.txt"


def kind_of(phrase):
    """Chuẩn hoá giống a2.find_triggers: một dấu cách, viết thường."""
    return re.sub(r"[ ]+", " ", phrase).casefold()


def phrase_before(text, pos):
    """Cụm dẫn chiếu đứng ngay trước vị trí pos, chỉ cách dấu cách (không vắt qua dòng mới); không có thì None."""
    for m in a2.CHAIN_RE.finditer(text):
        if m.end() <= pos and not text[m.end():pos].strip(" "):
            return m
    return None


def children_of(structural):
    """{cha: [con trực tiếp]} theo cạnh contains của A2a, giữ thứ tự cạnh."""
    children = collections.defaultdict(list)
    for s, p, o in structural:
        if p == "contains":
            children[s].append(o)
    return children


def find_exceptions(units, structural):
    """Trả về (edges, handled, unhandled), duyệt theo thứ tự đơn vị trong triples rồi thứ tự trigger trong text.

    edges: (s, "exception_of", o, evidence, method); quy tắc 1 theo thứ tự đích của cụm, quy tắc 2 theo thứ tự con.
    handled: (đơn vị, trigger nguyên văn, method) cho mỗi trigger đã sinh cạnh.
    unhandled: (đơn vị, câu) cho mỗi trigger không rơi vào quy tắc nào; câu là toàn bộ text của đơn vị.
    Chỗ quy tắc khớp mà spec không nói cách xử lý thì báo ValueError, không đoán: cụm trước "không áp dụng" có dạng
    group_targets không nhận, đích không có trong tập đơn vị, quy tắc 2 khớp nhưng U không có con, hoặc U có nhiều
    hơn một "trừ" mà text kết thúc bằng "sau đây:".
    """
    children = children_of(structural)
    edges, handled, unhandled = [], [], []
    for code, u in units.items():
        text = u.get("text")
        if not text:
            continue
        hits = [(m, kind_of(m.group(0))) for m in a2.TRIGGER_RE.finditer(text)]
        n_except = sum(1 for _, kind in hits if kind in EXCEPT_KINDS)
        for m, kind in hits:
            new, method = [], None
            ref = phrase_before(text, m.start()) if kind == NOT_APPLY_KIND else None
            if ref:
                method = NOT_APPLY
                evidence = text[ref.start():m.end()]
                for target in a2.group_targets(code, ref.group(0), units):
                    if target not in units:
                        raise ValueError(f"{code}: đích {target} không có trong tập đơn vị: {evidence!r}")
                    new.append((code, PREDICATE, target, evidence, method))
            elif kind in EXCEPT_KINDS and text.endswith(LIST_END):
                method = EXCEPT_LIST
                if n_except > 1:
                    raise ValueError(f"{code}: {n_except} cụm trừ và text kết thúc bằng {LIST_END!r}, chưa có quy tắc")
                if not children[code]:
                    raise ValueError(f"{code}: text kết thúc bằng {LIST_END!r} nhưng không có đơn vị con")
                new = [(child, PREDICATE, code, text, method) for child in children[code]]
            if new:
                edges += new
                handled.append((code, m.group(0), method))
            else:
                unhandled.append((code, text))
    return edges, handled, unhandled


def check_exceptions(units, structural, edges, handled, unhandled):
    """Trả về list lỗi (rỗng nếu sạch): không trùng, không tự trỏ, hai đầu tồn tại, evidence đúng chỗ, đếm trigger khớp."""
    errors = []
    for key, n in collections.Counter((s, p, o) for s, p, o, _, _ in edges).items():
        if n > 1:
            errors.append(f"cạnh trùng {n} lần: {key}")
    contains = {(s, o) for s, p, o in structural if p == "contains"}
    for s, p, o, evidence, method in edges:
        if p != PREDICATE:
            errors.append(f"{s} -> {o}: p là {p!r}, mong đợi {PREDICATE!r}")
        if method not in METHODS:
            errors.append(f"{s} -> {o}: method {method!r} không thuộc {METHODS}")
        if s == o:
            errors.append(f"{s} {PREDICATE} chính nó: {evidence!r}")
        missing = [x for x in (s, o) if x not in units]
        if missing:
            errors.append(f"{s} -> {o}: không có trong tập đơn vị: {missing}")
            continue
        holder = o if method == EXCEPT_LIST else s  # evidence nằm trong text của o ở quy tắc 2, của s ở quy tắc 1
        if not evidence or evidence not in units[holder].get("text", ""):
            errors.append(f"{s} -> {o}: evidence {evidence!r} không nằm trong text của {holder}")
        if method == NOT_APPLY and not kind_of(evidence).endswith(NOT_APPLY_KIND):
            errors.append(f"{s} -> {o}: evidence quy tắc 1 phải kết thúc bằng {NOT_APPLY_KIND!r}: {evidence!r}")
        if method == EXCEPT_LIST:
            if (o, s) not in contains:
                errors.append(f"{s} không phải con trực tiếp của {o} theo contains")
            if not evidence.endswith(LIST_END):
                errors.append(f"{s} -> {o}: evidence quy tắc 2 phải kết thúc bằng {LIST_END!r}: {evidence!r}")

    n_triggers = len(a2.find_triggers(units))
    if len(handled) + len(unhandled) != n_triggers:
        errors.append(f"số trigger = {n_triggers}, đã xử lý {len(handled)} + unhandled {len(unhandled)}")
    for code, phrase, method in handled:
        if not any((s if method == NOT_APPLY else o) == code and m == method for s, _, o, _, m in edges):
            errors.append(f"{code}: trigger {phrase!r} ghi đã xử lý nhưng không có cạnh {method}")
    for code, sentence in unhandled:
        if code not in units or sentence != units[code].get("text"):
            errors.append(f"unhandled {code}: câu không phải text của đơn vị")
        elif "\t" in sentence or "\n" in sentence:
            errors.append(f"unhandled {code}: câu có tab hoặc xuống dòng, không ghi được thành một dòng của file")
    return errors


def write_exceptions(edges, path):
    """Ghi JSONL, mỗi dòng {"s","p","o","evidence","method"}."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for s, p, o, evidence, method in edges:
            f.write(json.dumps({"s": s, "p": p, "o": o, "evidence": evidence, "method": method}, ensure_ascii=False) + "\n")


def write_unhandled(unhandled, path):
    """Mỗi dòng: đơn vị chứa trigger, câu, cách nhau bằng tab. Ghi cả khi rỗng để không còn file cũ."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for code, sentence in unhandled:
            f.write(f"{code}\t{sentence}\n")


def run(src):
    """Dựng cạnh exception_of từ triples của A1 và contains của A2a, in kết quả, chỉ ghi file khi sạch."""
    units = a2.read_units(src)
    structural = a2.build_edges(units)
    try:
        edges, handled, unhandled = find_exceptions(units, structural)
    except ValueError as e:
        raise SystemExit(f"LỖI: {e}")
    a2.fail_if_errors(check_exceptions(units, structural, edges, handled, unhandled))

    for s, _, o, evidence, method in edges:
        print(f"{s} → {o} | {evidence} [{method}]")
    for code, sentence in unhandled:
        print(f"unhandled {code}: {sentence}")
    per_method = collections.Counter(method for _, _, method in handled)
    print("số đơn vị:", len(units), "| trigger:", len(a2.find_triggers(units)),
          "| đã xử lý:", len(handled), dict(per_method), "| unhandled:", len(unhandled), "| cạnh exception_of:", len(edges))
    write_exceptions(edges, exceptions_path(src))
    write_unhandled(unhandled, unhandled_path(src))
    print("đã ghi", exceptions_path(src))
    print("đã ghi", unhandled_path(src))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("path", help="file md nguồn, dùng để suy stem của file triples A1")
    args = ap.parse_args(argv)
    run(args.path)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()
