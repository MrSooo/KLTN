"""L5 chung: ngoại lệ chung "..., trừ trường hợp X" thành nút điều kiện và cạnh exception_of, chạy cho mọi văn bản.

Chạy: python -I src/l5_general_exceptions.py <doc_id> | --all     (chạy sau L5 tường minh: nhận các trigger L5 tường minh để lại)
Đầu ra (data/processed/l5_general/):
  l5_general_conditions_<doc_id>.jsonl  nút điều kiện {id, type=dieu_kien, kind, text, units}; câu giống nhau (khoá chuẩn hoá) gộp một nút
  l5_general_exceptions_<doc_id>.jsonl  {s, p, o, evidence, method}: nút điều kiện exception_of đơn vị (general_except), và nếu mệnh đề dẫn
                                chiếu tới đơn vị T thì T exception_of đơn vị (general_except_ref), T có thể ở văn bản khác
  l5_general_unhandled_<doc_id>.jsonl   trigger không phải "trừ trường hợp" và "không được áp dụng", kèm lý do

Mệnh đề = chữ sau "trừ trường hợp" đến hết đoạn (bỏ . ; : , ở cuối). "Trừ trường hợp" đứng đầu đoạn thì mệnh đề dừng ở dấu phẩy đầu tiên
(phần sau là quy tắc chính). Evidence = từ chữ "trừ"/"ngoại" của cụm đến hết mệnh đề, nguyên văn. Một đơn vị có nhiều hơn một
"trừ trường hợp" thì để unhandled (không đoán). Nút điều kiện chia kind: tuy_nghi ("(các bên) có thỏa thuận khác"), dan_chieu_mo
("pháp luật có quy định khác"), cu_the (còn lại).
"""
import argparse
import collections
import hashlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import l1_parse as l1
import l2_edges as l2
import l5_explicit_exceptions as l5x
import corpus

L5_GENERAL_DIR_NAME = "l5_general"
PREDICATE = "exception_of"
GENERAL, GENERAL_REF = "general_except", "general_except_ref"
GENERAL_RE = re.compile(r"(?:ngoại[ ]+)?trừ[ ]+trường[ ]+hợp", re.I)
NOT_ALLOWED_RE = re.compile(r"không[ ]+được[ ]+áp[ ]+dụng", re.I)
TUY_NGHI_RE = re.compile(r"(?:(?:các|hai)[ ]+bên[ ]+|người[ ]+lao[ ]+động[ ]+và[ ]+người[ ]+sử[ ]+dụng[ ]+lao[ ]+động[ ]+)?"
                         r"(?:có[ ]+)?th(?:ỏa|oả)[ ]+thuận[ ]+khác", re.I)
DAN_CHIEU_RE = re.compile(r"(?:pháp[ ]+luật|luật|luật[ ]+khác|bộ[ ]+luật[ ]+này|bộ[ ]+luật[ ]+khác)(?:[ ]+có[ ]+liên[ ]+quan)?[ ]+có[ ]+quy[ ]+định[ ]+khác", re.I)


def norm_text(s):
    """Khoá gộp: gộp khoảng trắng, casefold, bỏ . ; : , và dấu cách ở hai đầu."""
    return re.sub(r"\s+", " ", s).casefold().strip(" .;:,")


def condition_kind(norm):
    if TUY_NGHI_RE.fullmatch(norm):
        return "tuy_nghi"
    if DAN_CHIEU_RE.fullmatch(norm):
        return "dan_chieu_mo"
    return "cu_the"


def condition_id(doc_id, norm):
    return f"{doc_id}.X{hashlib.sha1(norm.encode('utf-8')).hexdigest()[:8]}"


def clause_of(text, pos):
    """(mệnh đề, evidence) của "trừ trường hợp" bắt đầu đúng tại pos; hoặc (None, lý do)."""
    m = GENERAL_RE.match(text, pos)
    if not m:
        return None, "trigger không phải 'trừ trường hợp'"
    para_start = text.rfind("\n", 0, pos) + 1
    para_end = text.find("\n", pos)
    para_end = len(text) if para_end < 0 else para_end
    if text[para_start:pos].strip() == "":  # đứng đầu đoạn: mệnh đề dừng ở dấu phẩy đầu tiên
        comma = text.find(",", m.end(), para_end)
        if comma < 0:
            return None, "'trừ trường hợp' đứng đầu đoạn mà không có dấu phẩy"
        end = comma
    else:
        end = para_end
    clause = text[m.end():end].strip(" .;:,")
    if not clause:
        return None, "mệnh đề rỗng"
    return clause, text[pos:end]


def find_general(doc, units, all_units, resolver, available, l5_explicit_unhandled):
    """-> (nodes, edges, unhandled, pending). nodes: {id: dict}; edges: dict; unhandled: dict."""
    nodes, edges, unhandled, pending = collections.OrderedDict(), [], [], []
    by_unit = collections.defaultdict(list)
    for u in l5_explicit_unhandled:
        by_unit[u["unit"]].append(u)
    for uid, items in by_unit.items():
        text = units[uid]["text"]
        generals = [i for i in items if GENERAL_RE.match(text, i["pos"])]
        for i in items:
            if i in generals:
                continue
            why = "'không được áp dụng'" if NOT_ALLOWED_RE.match(text, i["pos"]) else i["reason"]
            unhandled.append({"unit": uid, "trigger": i["trigger"], "sentence": text, "reason": why})
        if len(generals) > 1:
            unhandled += [{"unit": uid, "trigger": i["trigger"], "sentence": text, "reason": "nhiều hơn một 'trừ trường hợp' trong đơn vị"}
                          for i in generals]
            continue
        if not generals:
            continue
        clause, evidence = clause_of(text, generals[0]["pos"])
        if clause is None:
            unhandled.append({"unit": uid, "trigger": generals[0]["trigger"], "sentence": text, "reason": evidence})
            continue
        norm = norm_text(clause)
        cid = condition_id(doc.doc_id, norm)
        node = nodes.setdefault(cid, {"id": cid, "type": "dieu_kien", "kind": condition_kind(norm), "text": clause, "units": []})
        node["units"].append(uid)
        edges.append({"s": cid, "p": PREDICATE, "o": uid, "evidence": evidence, "method": GENERAL})
        seen = set()
        for ref in l2.find_refs(uid, clause):
            r = l2.resolve_ref(doc, uid, units, ref, all_units, resolver, available)
            if r.pending:
                pending.append({**r.pending, "edge": PREDICATE})
            for t in r.targets:
                if t != uid and t not in seen:
                    seen.add(t)
                    edges.append({"s": t, "p": PREDICATE, "o": uid, "evidence": evidence, "method": GENERAL_REF})
    return nodes, edges, unhandled, pending


def check_general(units, all_units, nodes, edges, unhandled, n_l5_explicit_unhandled):
    errors = []
    keys = [(e["s"], e["o"], e["method"]) for e in edges]
    for k, n in collections.Counter(keys).items():
        if n > 1:
            errors.append(f"cạnh trùng {n} lần: {k}")
    for e in edges:
        o = e["o"]
        if o not in units or e["evidence"] not in units[o]["text"]:
            errors.append(f"{e['s']} -> {o}: evidence không nằm trong text của {o}")
        if e["method"] == GENERAL_REF and e["s"] not in all_units.get(e["s"].split(".")[0], {}):
            errors.append(f"{e['s']}: đích tham chiếu không tồn tại")
        if e["method"] == GENERAL and e["s"] not in nodes:
            errors.append(f"{e['s']}: nút điều kiện không có")
    for cid, n in nodes.items():
        if not any(e["s"] == cid for e in edges):
            errors.append(f"{cid}: nút điều kiện không có cạnh")
    n_handled = sum(len(n["units"]) for n in nodes.values())
    if n_handled + len(unhandled) != n_l5_explicit_unhandled:
        errors.append(f"trigger L5 tường minh để lại {n_l5_explicit_unhandled} khác đã xử lý {n_handled} + unhandled {len(unhandled)}")
    return errors


def l5_general_dir():
    return corpus.out_dir(L5_GENERAL_DIR_NAME)


def run_doc(doc, docs, all_units, resolver, available):
    units = all_units[doc.doc_id]
    _, _, l5_explicit_unh, _ = l5x.find_exceptions(doc, units, all_units, resolver, available)
    nodes, edges, unhandled, pending = find_general(doc, units, all_units, resolver, available, l5_explicit_unh)
    errors = check_general(units, all_units, nodes, edges, unhandled, len(l5_explicit_unh))
    kinds = collections.Counter(n["kind"] for n in nodes.values())
    n_general = sum(len(n["units"]) for n in nodes.values())
    report = [f"L5 chung báo cáo: {doc.doc_id}", f"trigger L5 tường minh để lại: {len(l5_explicit_unh)} = 'trừ trường hợp' đã xử lý {n_general} + unhandled {len(unhandled)}",
              f"nút điều kiện: {len(nodes)} {dict(kinds)}  cạnh: {len(edges)} ({dict(collections.Counter(e['method'] for e in edges))})",
              "unhandled theo lý do:"]
    report += [f"  {n:>3}  {r}" for r, n in collections.Counter(u["reason"] for u in unhandled).most_common()] or ["  (không có)"]
    report += [f"LỖI KIỂM: {e}" for e in errors]
    path = corpus.report_dir(L5_GENERAL_DIR_NAME) / f"l5_general_report_{doc.doc_id}.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(report) + "\n", encoding="utf-8", newline="\n")
    if not errors:
        d = l5_general_dir()
        l1.write_jsonl(d / f"l5_general_conditions_{doc.doc_id}.jsonl", list(nodes.values()))
        l1.write_jsonl(d / f"l5_general_exceptions_{doc.doc_id}.jsonl", edges)
        l1.write_jsonl(d / f"l5_general_unhandled_{doc.doc_id}.jsonl", unhandled)
        l1.write_jsonl(d / f"l5_general_pending_{doc.doc_id}.jsonl", pending)
    return nodes, edges, unhandled, errors


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("target", nargs="?")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args(argv)
    docs, all_units, resolver, available = l2.load_context()
    targets = list(docs.values()) if args.all else [corpus.get_doc(args.target, docs)] if args.target else ap.error("cần doc_id hoặc --all")
    bad = []
    for doc in targets:
        nodes, edges, unhandled, errors = run_doc(doc, docs, all_units, resolver, available)
        print(f"{doc.doc_id:<22} nút điều kiện {len(nodes):>3}  cạnh {len(edges):>3}  unhandled {len(unhandled):>3}  {'OK' if not errors else 'LỖI'}")
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
