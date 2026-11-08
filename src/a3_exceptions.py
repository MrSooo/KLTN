"""A3 (L5): cạnh exception_of tường minh trong chữ, hai quy tắc riêng, chạy cho mọi văn bản.

Chạy: python -I src/a3_exceptions.py <doc_id> | --all
Đầu vào: A1 (đơn vị) và A2 (cách giải dẫn chiếu, kể cả sang văn bản khác). Đầu ra (data/processed/a3/):
  a3_exceptions_<doc_id>.jsonl  {s, p, o, evidence, method}; s là phần ngoại lệ, o là quy tắc bị ngoại trừ
  a3_unhandled_<doc_id>.jsonl   trigger không rơi vào hai quy tắc (việc của A6) hoặc rơi vào mà không giải được
  a3_pending_<doc_id>.jsonl     đích nằm ở văn bản chưa có trong KB (quan hệ chờ đích)

  Quy tắc 1, not_apply_pattern: đơn vị U có "không áp dụng" và một cụm dẫn chiếu đứng NGAY trước nó (chỉ cách dấu cách):
    mỗi đích của cụm là o, s = U. Evidence từ đầu cụm đến hết "không áp dụng".
  Quy tắc 2, except_list_pattern: text của U có "trừ" (hoặc "ngoại trừ") và kết thúc bằng "sau đây:". Mỗi đơn vị con trực tiếp C
    của U là s, o = U. Evidence là câu chứa "trừ" (= toàn bộ text của U).

Mọi trigger thuộc đúng một trong hai: đã xử lý (có cạnh) hoặc unhandled. Không nới quy tắc để bắt thêm ca: ca ngoài hai quy tắc là
ngoại lệ chung (A6) hoặc để nguyên. Dòng chỉ thị sửa đổi không xét (ngoại lệ trong đó thuộc văn bản bị sửa).
"""
import argparse
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import a1_parse as a1
import a2_edges as a2
import corpus

A3_DIR_NAME = "a3"
PREDICATE = "exception_of"
NOT_APPLY, EXCEPT_LIST = "not_apply_pattern", "except_list_pattern"
METHODS = (NOT_APPLY, EXCEPT_LIST)
NOT_APPLY_KIND = "không áp dụng"
EXCEPT_KINDS = ("trừ", "ngoại trừ")  # "ngoại trừ" là một cụm
LIST_END = "sau đây:"
# Ranh giới từ ở hai đầu nên "trừng" không khớp. Quét trái sang phải nên "ngoại trừ" thành một cụm.
TRIGGER_RE = re.compile(r"(?<!\w)(?:ngoại[ ]+trừ|trừ|không[ ]+áp[ ]+dụng)(?!\w)", re.I)
TEXT_TYPES = ("dieu", "khoan", "diem")


def kind_of(phrase):
    return re.sub(r"[ ]+", " ", phrase).casefold()


def children_of(units):
    ch = collections.defaultdict(list)
    for uid, u in units.items():
        if u.get("parent"):
            ch[u["parent"]].append(uid)
    return ch


def find_triggers(units):
    """[(đơn vị, match)] của mọi trigger trong đơn vị có text, bỏ dòng chỉ thị sửa đổi."""
    out = []
    for uid, u in units.items():
        text = u.get("text")
        if u["type"] in TEXT_TYPES and text and not a2.is_directive(text):
            out += [(uid, m) for m in TRIGGER_RE.finditer(text)]
    return out


def find_exceptions(doc, units, all_units, resolver, available):
    """-> (edges, handled, unhandled, pending). unhandled: dict {unit, trigger, sentence, reason}; sentence là text của đơn vị."""
    children = children_of(units)
    edges, handled, unhandled, pending = [], [], [], []
    by_unit = collections.defaultdict(list)
    for uid, m in find_triggers(units):
        by_unit[uid].append(m)
    for uid, ms in by_unit.items():
        text = units[uid]["text"]
        refs = a2.find_refs(uid, text)
        n_except = sum(1 for m in ms if kind_of(m[0]) in EXCEPT_KINDS)
        for m in ms:
            kind = kind_of(m[0])
            reason = "ngoài hai quy tắc của A3"
            new, method = [], None
            if kind == NOT_APPLY_KIND:
                ref = next((r for r in refs if r.end <= m.start() and not text[r.end:m.start()].strip(" ")), None)
                if ref:
                    r = a2.resolve_ref(doc, uid, units, ref, all_units, resolver, available)
                    evidence = text[ref.start:m.end()]
                    if r.error or r.missing:
                        reason = r.error or r.missing[0][1]
                    elif r.pending:
                        pending.append({**r.pending, "edge": PREDICATE})
                        reason = "đích ở văn bản chưa có trong KB (quan hệ chờ đích)"
                    else:
                        method = NOT_APPLY
                        new = [(uid, PREDICATE, t, evidence, method) for t in r.targets]
            elif kind in EXCEPT_KINDS and text.endswith(LIST_END):
                if n_except > 1:
                    reason = f"{n_except} cụm trừ và text kết thúc bằng {LIST_END!r}"
                elif not children[uid]:
                    reason = f"text kết thúc bằng {LIST_END!r} nhưng không có đơn vị con"
                else:
                    method = EXCEPT_LIST
                    new = [(c, PREDICATE, uid, text, method) for c in children[uid]]
            if new:
                edges += new
                handled.append((uid, m[0], method))
            else:
                unhandled.append({"unit": uid, "trigger": m[0], "pos": m.start(), "sentence": text, "reason": reason})
    return edges, handled, unhandled, pending


def check_exceptions(units, edges, handled, unhandled):
    """Lỗi (rỗng nếu sạch): không trùng, không tự trỏ, hai đầu tồn tại, evidence đúng chỗ, đếm trigger khớp."""
    errors = []
    for key, n in collections.Counter((s, p, o) for s, p, o, _, _ in edges).items():
        if n > 1:
            errors.append(f"cạnh trùng {n} lần: {key}")
    for s, p, o, evidence, method in edges:
        if s == o:
            errors.append(f"{s} {PREDICATE} chính nó")
        if o.split(".")[0] == s.split(".")[0] and (s not in units):
            errors.append(f"{s}: không có trong tập đơn vị")
        holder = o if method == EXCEPT_LIST else s
        if holder in units and evidence not in units[holder].get("text", ""):
            errors.append(f"{s} -> {o}: evidence {evidence!r} không nằm trong text của {holder}")
        if method == NOT_APPLY and not kind_of(evidence).endswith(NOT_APPLY_KIND):
            errors.append(f"{s} -> {o}: evidence quy tắc 1 phải kết thúc bằng {NOT_APPLY_KIND!r}")
        if method == EXCEPT_LIST and not evidence.endswith(LIST_END):
            errors.append(f"{s} -> {o}: evidence quy tắc 2 phải kết thúc bằng {LIST_END!r}")
    n_triggers = len(find_triggers(units))
    if len(handled) + len(unhandled) != n_triggers:
        errors.append(f"số trigger = {n_triggers}, đã xử lý {len(handled)} + unhandled {len(unhandled)}")
    return errors


def a3_dir():
    return corpus.out_dir(A3_DIR_NAME)


def run_doc(doc, docs, all_units, resolver, available):
    units = all_units[doc.doc_id]
    edges, handled, unhandled, pending = find_exceptions(doc, units, all_units, resolver, available)
    errors = check_exceptions(units, edges, handled, unhandled)
    per_method = collections.Counter(m for _, _, m in handled)
    report = [f"A3 báo cáo: {doc.doc_id}", f"trigger: {len(handled) + len(unhandled)} = đã xử lý {len(handled)} {dict(per_method)} + unhandled {len(unhandled)}",
              f"cạnh exception_of: {len(edges)}  chờ đích: {len(pending)}", "unhandled theo lý do:"]
    report += [f"  {n:>3}  {r}" for r, n in collections.Counter(u["reason"] for u in unhandled).most_common()] or ["  (không có)"]
    report += ([f"LỖI KIỂM: {e}" for e in errors])
    path = corpus.report_dir(A3_DIR_NAME) / f"a3_report_{doc.doc_id}.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(report) + "\n", encoding="utf-8", newline="\n")
    if not errors:
        d = a3_dir()
        a1.write_jsonl(d / f"a3_exceptions_{doc.doc_id}.jsonl",
                       [{"s": s, "p": p, "o": o, "evidence": ev, "method": m} for s, p, o, ev, m in edges])
        a1.write_jsonl(d / f"a3_unhandled_{doc.doc_id}.jsonl", unhandled)
        a1.write_jsonl(d / f"a3_pending_{doc.doc_id}.jsonl", pending)
    return edges, handled, unhandled, errors


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("target", nargs="?")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args(argv)
    docs, all_units, resolver, available = a2.load_context()
    targets = list(docs.values()) if args.all else [corpus.get_doc(args.target, docs)] if args.target else ap.error("cần doc_id hoặc --all")
    bad = []
    for doc in targets:
        edges, handled, unhandled, errors = run_doc(doc, docs, all_units, resolver, available)
        print(f"{doc.doc_id:<22} trigger {len(handled) + len(unhandled):>3}  đã xử lý {len(handled):>3}  unhandled {len(unhandled):>3}  "
              f"cạnh {len(edges):>3}  {'OK' if not errors else 'LỖI'}")
        if errors:
            bad.append((doc, errors))
    if bad:
        for doc, errors in bad:
            print(f"\nLỖI {doc.doc_id}:", file=sys.stderr)
            for e in errors[:20]:
                print("  ", e, file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()
