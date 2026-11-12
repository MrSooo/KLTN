"""L5 chung: ngoại lệ chung "..., trừ trường hợp X" và "..., trừ <danh từ> X" thành nút điều kiện và cạnh exception_of, chạy cho mọi văn bản.

Chạy: python -I src/exceptions_general.py <doc_id> | --all     (chạy sau L5 tường minh: nhận các trigger L5 tường minh để lại)
Đầu ra (data/processed/l5_general/):
  l5_general_conditions_<doc_id>.jsonl  nút điều kiện {id, type=dieu_kien, kind, text, units}; câu giống nhau (khoá chuẩn hoá) gộp một nút
  l5_general_exceptions_<doc_id>.jsonl  {s, p, o, evidence, how, flags, rule}: nút điều kiện exception_of đơn vị (rule general_except cho "trừ [các|những|một số]
                                trường hợp", general_except_noun cho "trừ <danh từ>"), và nếu mệnh đề dẫn chiếu tới đơn vị T thì T exception_of đơn vị
                                (general_except_ref, general_except_noun_ref tương ứng), T có thể ở văn bản khác
  l5_general_unhandled_<doc_id>.jsonl   trigger không xử lý được, kèm lý do

Họ "trừ <danh từ>" (A24, 12/11) chỉ nhận danh từ trong NOUN_HEADS: các danh từ này lấy từ việc ĐỌC TỪNG ca "trừ" chưa xử lý của kho (73 ca) và thấy đều
là ngoại lệ thật. "trừ" đi cùng danh từ khác (chi phí, thời gian, nhà thầu, Điều 93, ...) vẫn để unhandled kèm lý do, không đoán.

Mệnh đề = chữ sau "trừ" (với họ trường hợp: sau chữ "trường hợp") đến hết đoạn, rồi cắt ở: dấu ";" mà vế sau KHÔNG bắt đầu bằng khoản/điểm/Điều/Chương/mục
(vì ";" giữa hai dẫn chiếu là một danh sách dẫn chiếu, vẫn thuộc ngoại lệ); dấu ")" không có "(" mở trong mệnh đề (ngoại lệ đặt trong ngoặc). Bỏ . ; : , ở
cuối. "Trừ" đứng đầu đoạn thì mệnh đề dừng ở dấu phẩy đầu tiên (phần sau là quy tắc chính). Với họ mới ("trừ <danh từ>", "trừ các/những/một số trường hợp") đoạn kết thúc bằng dấu hai chấm
là ngoại lệ liệt kê ở các đơn vị con, mệnh đề sẽ chứa sai chữ nên để unhandled; "trừ trường hợp" trơn giữ hành vi cũ (còn vài nút kiểu này). Evidence = từ chữ "trừ"/"ngoại" của cụm đến hết mệnh đề, nguyên văn. Một đơn vị có nhiều trigger thì mỗi
trigger tự cắt mệnh đề ở dấu ";"; hai trigger nằm cùng một vế (mệnh đề đè lên nhau) thì để unhandled (không đoán). Nút điều kiện chia kind: tuy_nghi
("(các bên) có thỏa thuận khác"), dan_chieu_mo ("pháp luật có quy định khác"), cu_the (còn lại).
"""
import argparse
import collections
import hashlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import parse as l1
import refs as l2
import exceptions_explicit as l5x
import corpus

L5_GENERAL_DIR_NAME = "l5_general"
PREDICATE = "exception_of"
GENERAL, GENERAL_REF = "general_except", "general_except_ref"
NOUN, NOUN_REF = "general_except_noun", "general_except_noun_ref"
GENERAL_RULES, REF_RULES = (GENERAL, NOUN), (GENERAL_REF, NOUN_REF)
DET = r"(?:(?:các|những|một[ ]+số)[ ]+)?"
DET_CAPTURE = r"(?:(các|những|một[ ]+số)[ ]+)?"
TRIGGER_HEAD_RE = re.compile(r"(?:ngoại[ ]+)?trừ[ ]+", re.I)
GENERAL_RE = re.compile(TRIGGER_HEAD_RE.pattern + DET_CAPTURE + r"trường[ ]+hợp", re.I)
NOUN_HEADS = ("hành vi", "hình thức", "lĩnh vực", "thông tin", "nghề", "công việc", "tranh chấp", "hợp đồng")
NOUN_RE = re.compile(TRIGGER_HEAD_RE.pattern + DET + "(?:" + "|".join(h.replace(" ", "[ ]+") for h in NOUN_HEADS) + r")(?!\w)", re.I)
REF_START_RE = re.compile(r"(?:các[ ]+)?(?:khoản|điểm|điều|chương|mục|phụ[ ]+lục)(?!\w)", re.I)
NOT_ALLOWED_RE = re.compile(r"không[ ]+được[ ]+áp[ ]+dụng", re.I)
APPLY_TRIAL_RE = re.compile(r"không[ ]+áp[ ]+dụng[ ]+thử(?![ ]+việc)(?!\w)", re.I)  # "áp dụng thử mức lao động", khác "áp dụng thử việc"
NOT_APPLY_RE = re.compile(r"không[ ]+áp[ ]+dụng", re.I)
SUBTRACT_BEFORE_RE = re.compile(r"(?:sau[ ]+khi|được)[ ]+$", re.I)
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


def _clause(text, pos):
    """(mệnh đề, evidence, vị trí kết thúc, rule) của trigger bắt đầu đúng tại pos; hoặc (None, lý do, None, None)."""
    m = GENERAL_RE.match(text, pos)
    if m:
        rule, start = GENERAL, m.end()
        new_family = bool(m.group(1))  # "trừ trường hợp" trơn giữ nguyên hành vi cũ; "trừ các/những/một số trường hợp" thuộc họ mới
    elif NOUN_RE.match(text, pos):
        rule, start, new_family = NOUN, TRIGGER_HEAD_RE.match(text, pos).end(), True
    else:
        return None, "trigger không phải 'trừ trường hợp' hay 'trừ <danh từ>'", None, None
    para_start = text.rfind("\n", 0, pos) + 1
    para_end = text.find("\n", pos)
    para_end = len(text) if para_end < 0 else para_end
    if text[para_start:pos].strip() == "":  # đứng đầu đoạn: mệnh đề dừng ở dấu phẩy đầu tiên
        comma = text.find(",", start, para_end)
        if comma < 0:
            return None, "'trừ' đứng đầu đoạn mà không có dấu phẩy", None, None
        end = comma
    else:
        end = para_end
    cut = False
    for sc in re.finditer(";", text[start:end]):  # ";" giữa hai dẫn chiếu là danh sách dẫn chiếu, không cắt
        i = start + sc.start()
        if not REF_START_RE.match(text[i + 1:end].lstrip()):
            end, cut = i, True
            break
    depth = 0
    for i in range(start, end):  # ngoại lệ đặt trong ngoặc: dừng ở ")" không có "(" mở trong mệnh đề
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            if depth == 0:
                end, cut = i, True
                break
            depth -= 1
    if new_family and not cut and end == para_end and text[para_start:para_end].rstrip().endswith(":"):
        return None, "ngoại lệ liệt kê ở các đơn vị con (đoạn kết thúc bằng dấu hai chấm)", None, None
    clause = text[start:end].strip(" .;:,")
    if not clause:
        return None, "mệnh đề rỗng", None, None
    return clause, text[pos:end], end, rule


def clause_of(text, pos):
    """(mệnh đề, evidence) của trigger bắt đầu đúng tại pos; hoặc (None, lý do)."""
    clause, evidence, _, _ = _clause(text, pos)
    return clause, evidence


def other_reason(text, item):
    """Lý do cụ thể cho trigger không thuộc họ "trừ trường hợp" / "trừ <danh từ>" (thay cho lý do chung của L5 tường minh)."""
    pos = item["pos"]
    if NOT_ALLOWED_RE.match(text, pos):
        return "'không được áp dụng'"
    if APPLY_TRIAL_RE.match(text, pos):
        return "nghĩa khác: 'áp dụng thử', không phải ngoại lệ"
    if NOT_APPLY_RE.match(text, pos):
        return "'không áp dụng' không kèm dẫn chiếu tới đơn vị bị loại trừ nên không biết là ngoại lệ của đơn vị nào"
    if TRIGGER_HEAD_RE.match(text, pos):
        if SUBTRACT_BEFORE_RE.search(text[max(0, pos - 12):pos]):
            return "nghĩa khác: 'trừ' là phép trừ"
        return "'trừ' đi cùng danh từ ngoài danh sách đã đọc"
    return item["reason"]


def find_general(doc, units, all_units, resolver, available, l5_explicit_unhandled):
    """-> (nodes, edges, unhandled, pending). nodes: {id: dict}; edges: dict; unhandled: dict."""
    nodes, edges, unhandled, pending = collections.OrderedDict(), [], [], []
    by_unit = collections.defaultdict(list)
    for u in l5_explicit_unhandled:
        by_unit[u["unit"]].append(u)

    def reject(uid, text, item, reason):
        unhandled.append({"unit": uid, "trigger": item["trigger"], "sentence": text, "reason": reason})

    for uid, items in by_unit.items():
        text = units[uid]["text"]
        parsed = []
        for i in items:
            if not (GENERAL_RE.match(text, i["pos"]) or NOUN_RE.match(text, i["pos"])):
                reject(uid, text, i, other_reason(text, i))
                continue
            clause, evidence, end, rule = _clause(text, i["pos"])
            if clause is None:
                reject(uid, text, i, evidence)
            else:
                parsed.append((i["pos"], i, clause, evidence, end, rule))
        parsed.sort(key=lambda x: x[0])
        clash = {p for a, b in zip(parsed, parsed[1:]) if b[0] < a[4] for p in (a[0], b[0])}
        done, seen_refs = set(), set()
        for pos, i, clause, evidence, end, rule in parsed:
            if pos in clash:
                reject(uid, text, i, "nhiều hơn một 'trừ' trong cùng một vế (không cắt được bằng dấu ';')")
                continue
            norm = norm_text(clause)
            cid = condition_id(doc.doc_id, norm)
            if cid in done:
                reject(uid, text, i, "trùng nút điều kiện trong cùng đơn vị")
                continue
            done.add(cid)
            node = nodes.setdefault(cid, {"id": cid, "type": "dieu_kien", "kind": condition_kind(norm), "text": clause, "units": []})
            node["units"].append(uid)
            edges.append({"s": cid, "p": PREDICATE, "o": uid, "evidence": evidence, "how": "regex", "flags": [], "rule": rule})
            ref_rule = GENERAL_REF if rule == GENERAL else NOUN_REF
            for ref in l2.find_refs(uid, clause):
                r = l2.resolve_ref(doc, uid, units, ref, all_units, resolver, available)
                if r.pending:
                    pending.append({**r.pending, "edge": PREDICATE})
                for t in r.targets:
                    if t != uid and (t, ref_rule) not in seen_refs:
                        seen_refs.add((t, ref_rule))
                        edges.append({"s": t, "p": PREDICATE, "o": uid, "evidence": evidence, "how": "regex", "flags": [], "rule": ref_rule})
    return nodes, edges, unhandled, pending


def check_general(units, all_units, nodes, edges, unhandled, n_l5_explicit_unhandled):
    errors = []
    keys = [(e["s"], e["o"], e["rule"]) for e in edges]
    for k, n in collections.Counter(keys).items():
        if n > 1:
            errors.append(f"cạnh trùng {n} lần: {k}")
    for e in edges:
        o = e["o"]
        if o not in units or e["evidence"] not in units[o]["text"]:
            errors.append(f"{e['s']} -> {o}: evidence không nằm trong text của {o}")
        if e["rule"] in REF_RULES and e["s"] not in all_units.get(e["s"].split(".")[0], {}):
            errors.append(f"{e['s']}: đích tham chiếu không tồn tại")
        if e["rule"] in GENERAL_RULES and e["s"] not in nodes:
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
    report = [f"L5 chung báo cáo: {doc.doc_id}", f"trigger L5 tường minh để lại: {len(l5_explicit_unh)} = 'trừ' đã xử lý {n_general} + unhandled {len(unhandled)}",
              f"nút điều kiện: {len(nodes)} {dict(kinds)}  cạnh: {len(edges)} ({dict(collections.Counter(e['rule'] for e in edges))})",
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
