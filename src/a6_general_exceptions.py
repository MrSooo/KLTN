"""A6: ngoại lệ chung "..., trừ trường hợp X" thành nút điều kiện và cạnh exception_of (file riêng, không sửa A3).

Đầu vào: triples của A1 (a2.read_units). Không đọc file A3: A3 chỉ nhận một trigger "trừ"/"ngoại trừ" khi text kết thúc bằng
"sau đây:" (quy tắc 2, a3.find_exceptions), nên mọi trigger "trừ" còn lại là phần của A6 hoặc unhandled của A6.
Đầu ra: data/processed/a6_conditions_<stem>.jsonl (bộ ba s,p,o của nút điều kiện: type, text),
        data/processed/a6_exceptions_<stem>.jsonl (s, p, o, evidence, method), docs/a6_unhandled_<stem>.txt.
Chiều cạnh giống A3: s là phần ngoại lệ (nút điều kiện), o là đơn vị quy tắc bị ngoại trừ.

  Mẫu: (ngoại )trừ trường hợp <mệnh đề>. Mệnh đề chạy đến hết đoạn (không vượt qua dòng mới), bỏ . ; : , ở cuối. Nếu
    "trừ trường hợp" đứng đầu đoạn ("Trừ trường hợp X, quy tắc") thì mệnh đề dừng ở dấu phẩy đầu tiên.
  Nút điều kiện: một nút cho mỗi khoá gộp (norm_text của mệnh đề), mã BLDS2015.C_<8 ký tự đầu của sha1(khoá)>, type "dieu_kien".
  Trigger "trừ" mà text không kết thúc "sau đây:" nhưng không đi kèm "trường hợp" là unhandled (mã đơn vị và câu). Mỗi
    "không được áp dụng" (không trigger nào bắt) cũng là unhandled.
  Hai "trừ trường hợp" trong một đơn vị, mệnh đề rỗng, hoặc "trừ trường hợp" đầu đoạn mà đoạn không có dấu phẩy: ValueError
    (spec không nói cách xử lý, không đoán).
  Trigger "không áp dụng" không phải việc của A6.

Chạy: python -I src/a6_general_exceptions.py <file md nguồn>   (bắt buộc truyền path, không có mặc định)
"""
import argparse
import collections
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import a2_edges as a2
import a3_exceptions as a3

PREDICATE = a3.PREDICATE
METHOD = "general_except_pattern"
COND_TYPE = "dieu_kien"
ID_HEX = 8  # số ký tự hex của sha1 trong mã nút điều kiện

# Khớp tại vị trí của một trigger "trừ"/"ngoại trừ" của a2.TRIGGER_RE; chỉ nối bằng dấu cách nên không vắt qua dòng mới.
GENERAL_RE = re.compile(r"(?:ngoại[ ]+)?trừ[ ]+trường[ ]+hợp(?!\w)", re.I)
# Cách viết ngoại lệ mà a2.TRIGGER_RE không bắt ("không áp dụng" có "được" ở giữa): không trigger nào của A3/A6 thấy nó,
# nên A6 tự quét và đưa vào unhandled để nó hiện ra thay vì mất (review F-05). Không sửa TRIGGER_RE vì A3 dùng chung.
NOT_ALLOWED_RE = re.compile(r"(?<!\w)không[ ]+được[ ]+áp[ ]+dụng(?!\w)", re.I)


def conditions_path(src):
    return a2.PROCESSED_DIR / f"a6_conditions_{Path(src).stem}.jsonl"


def exceptions_path(src):
    return a2.PROCESSED_DIR / f"a6_exceptions_{Path(src).stem}.jsonl"


def unhandled_path(src):
    """Mỗi file nguồn một file unhandled, để chạy file này không ghi đè file kia."""
    return a2.ROOT / "docs" / f"a6_unhandled_{Path(src).stem}.txt"


def norm_text(s):
    """Khoá gộp: gộp khoảng trắng, casefold, bỏ . ; : , và dấu cách ở cuối. Dùng chung với same_text_as của A7."""
    s = re.sub(r"\s+", " ", s).strip().casefold()
    return re.sub(r"[ .;:,]+$", "", s)


def condition_id(prefix, key):
    """Mã nút điều kiện từ khoá gộp; băm nên ổn định giữa các ngày và phiên bản (đánh số tuần tự sẽ đổi khi tập câu đổi)."""
    return f"{prefix}.C_{hashlib.sha1(key.encode('utf-8')).hexdigest()[:ID_HEX]}"


class General(NamedTuple):
    nodes: list      # [(mã nút, mệnh đề)] theo thứ tự xuất hiện đầu tiên, mệnh đề nguyên văn (đã bỏ dấu cuối) của lần đầu
    edges: list      # [(s, "exception_of", o, evidence, METHOD)] theo thứ tự đơn vị rồi thứ tự trigger
    handled: list    # [(đơn vị, trigger nguyên văn)] mỗi trigger đã sinh cạnh
    unhandled: list  # [(đơn vị, câu)] trigger "trừ" không rơi vào A3 hay A6, và mỗi "không được áp dụng"; câu là toàn bộ text
    skipped: list    # [(đơn vị, trigger nguyên văn)] trigger "trừ" thuộc A3 (text kết thúc "sau đây:")


def find_general(units):
    """Duyệt đơn vị theo thứ tự trong triples rồi trigger theo thứ tự trong text, trả về General.

    "Trừ trường hợp X, quy tắc" (đứng đầu đoạn): mệnh đề dừng ở dấu phẩy đầu tiên, vì phần sau là quy tắc chính (review F-04).
    Chỗ spec không nói thì ValueError: một đơn vị có nhiều hơn một "trừ trường hợp", hoặc mệnh đề rỗng sau khi bỏ dấu cuối;
    "trừ trường hợp" đứng đầu đoạn mà đoạn không có dấu phẩy; hai khoá khác nhau trùng mã băm.
    """
    nodes, edges, handled, unhandled, skipped = {}, [], [], [], []
    keys = {}  # mã nút -> khoá, để bắt hai khoá khác nhau trùng mã
    for code, u in units.items():
        text = u.get("text")
        if not text:
            continue
        unhandled += [(code, text) for _ in NOT_ALLOWED_RE.finditer(text)]
        hits = [m for m in a2.TRIGGER_RE.finditer(text) if a3.kind_of(m.group(0)) in a3.EXCEPT_KINDS]
        if text.endswith(a3.LIST_END):  # quy tắc 2 của A3 nhận mọi trigger trừ trong đơn vị này
            skipped += [(code, m.group(0)) for m in hits]
            continue
        n_general = sum(1 for m in hits if GENERAL_RE.match(text, m.start()))
        if n_general > 1:
            raise ValueError(f"{code}: {n_general} cụm 'trừ trường hợp', chưa có quy tắc")
        for m in hits:
            g = GENERAL_RE.match(text, m.start())
            if not g:
                unhandled.append((code, text))
                continue
            paragraph = text[g.end():].split("\n")[0]
            if m.start() == 0 or text[m.start() - 1] == "\n":
                if "," not in paragraph:
                    raise ValueError(f"{code}: 'trừ trường hợp' đứng đầu đoạn mà không có dấu phẩy, chưa có quy tắc: {text!r}")
                paragraph = paragraph[:paragraph.index(",") + 1]
            clause = re.sub(r"[ .;:,]+$", "", paragraph.strip())
            if not clause:
                raise ValueError(f"{code}: mệnh đề rỗng sau 'trừ trường hợp': {text!r}")
            key = norm_text(clause)
            cond = condition_id(code.split(".")[0], key)
            if keys.setdefault(cond, key) != key:
                raise ValueError(f"{code}: hai khoá khác nhau cùng mã băm {cond}: {keys[cond]!r} và {key!r}")
            nodes.setdefault(cond, clause)
            edges.append((cond, PREDICATE, code, text[m.start():g.end() + len(paragraph)], METHOD))
            handled.append((code, m.group(0)))
    return General(list(nodes.items()), edges, handled, unhandled, skipped)


def check_general(units, result):
    """Trả về list lỗi (rỗng nếu sạch): không trùng, đầu s là nút điều kiện, đầu o là đơn vị, evidence đúng chỗ, mã 1-1 với khoá, đếm khớp."""
    errors = []
    node_ids = [c for c, _ in result.nodes]
    for c, n in collections.Counter(node_ids).items():
        if n > 1:
            errors.append(f"nút {c} lặp {n} lần")
    key_to_id = collections.defaultdict(list)
    for c, clause in result.nodes:
        key_to_id[norm_text(clause)].append(c)
        if c in units:
            errors.append(f"nút điều kiện {c} trùng mã với một đơn vị")
        elif c != condition_id(c.split(".")[0], norm_text(clause)):
            errors.append(f"nút {c}: mã không khớp băm của mệnh đề {clause!r}")
    for key, ids in key_to_id.items():
        if len(ids) > 1:
            errors.append(f"khoá {key!r} có {len(ids)} nút: {ids}")
    for key, n in collections.Counter((s, p, o) for s, p, o, _, _ in result.edges).items():
        if n > 1:
            errors.append(f"cạnh trùng {n} lần: {key}")
    for s, p, o, evidence, method in result.edges:
        if p != PREDICATE:
            errors.append(f"{s} -> {o}: p là {p!r}, mong đợi {PREDICATE!r}")
        if method != METHOD:
            errors.append(f"{s} -> {o}: method {method!r}, mong đợi {METHOD!r}")
        if s not in node_ids:
            errors.append(f"{s} -> {o}: {s} không phải nút điều kiện")
        if o not in units:
            errors.append(f"{s} -> {o}: {o} không có trong tập đơn vị")
        elif not evidence or evidence not in units[o].get("text", ""):
            errors.append(f"{s} -> {o}: evidence {evidence!r} không nằm trong text của {o}")
        elif not GENERAL_RE.match(evidence):
            errors.append(f"{s} -> {o}: evidence phải bắt đầu bằng 'trừ trường hợp': {evidence!r}")
    used = {s for s, _, _, _, _ in result.edges}
    errors += [f"nút {c} không có cạnh nào" for c in node_ids if c not in used]

    n_except = sum(1 for t in a2.find_triggers(units) if a3.kind_of(t.phrase) in a3.EXCEPT_KINDS)
    n_not_allowed = sum(len(NOT_ALLOWED_RE.findall(u.get("text") or "")) for u in units.values())
    done = len(result.skipped) + len(result.handled) + len(result.unhandled)
    if done != n_except + n_not_allowed:
        errors.append(f"số trigger trừ/ngoại trừ = {n_except} + không được áp dụng = {n_not_allowed}, thuộc A3 {len(result.skipped)} "
                      f"+ đã xử lý {len(result.handled)} + unhandled {len(result.unhandled)}")
    for code, sentence in result.unhandled:
        if code not in units or sentence != units[code].get("text"):
            errors.append(f"unhandled {code}: câu không phải text của đơn vị")
        elif "\t" in sentence or "\n" in sentence:
            errors.append(f"unhandled {code}: câu có tab hoặc xuống dòng, không ghi được thành một dòng của file")
    return errors


def write_conditions(nodes, path):
    """Ghi JSONL bộ ba {"s","p","o"} của nút điều kiện: type rồi text."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for cond, clause in nodes:
            for p, o in (("type", COND_TYPE), ("text", clause)):
                f.write(json.dumps({"s": cond, "p": p, "o": o}, ensure_ascii=False) + "\n")


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
    """Dựng nút điều kiện và cạnh exception_of từ triples của A1, in kết quả, chỉ ghi file khi sạch."""
    units = a2.read_units(src)
    try:
        result = find_general(units)
    except ValueError as e:
        raise SystemExit(f"LỖI: {e}")
    a2.fail_if_errors(check_general(units, result))

    for s, _, o, evidence, _ in result.edges:
        print(f"{s} → {o} | {evidence}")
    for code, sentence in result.unhandled:
        print(f"unhandled {code}: {sentence}")
    n_except = len(result.skipped) + len(result.handled) + len(result.unhandled)
    print("số đơn vị:", len(units), f"| trigger trừ/ngoại trừ: {n_except} = thuộc A3 {len(result.skipped)} + đã xử lý "
          f"{len(result.handled)} + unhandled {len(result.unhandled)}", "| nút điều kiện:", len(result.nodes),
          "| cạnh exception_of:", len(result.edges))
    write_conditions(result.nodes, conditions_path(src))
    write_exceptions(result.edges, exceptions_path(src))
    write_unhandled(result.unhandled, unhandled_path(src))
    print("đã ghi", conditions_path(src))
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
