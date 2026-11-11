"""L6: đọc chỉ thị từ chữ của văn bản mới nạp và áp vào kho phiên bản (l6_versions.Store).

Mỗi văn bản là một sự kiện (apply_event). Pipeline tự đọc câu chỉ thị, KHÔNG dùng cột quan_he/ghi_chu của manifest. Các loại đã cài:
  1,2 sửa / bổ sung đơn vị "như sau:" có khối trích dẫn (payload) | 3 thay / bỏ cụm từ nhiều đích | 4 bãi bỏ đơn vị
  5 hết hiệu lực cả văn bản (kể cả danh sách "các Nghị định sau đây hết hiệu lực") | 8 bổ sung danh mục, không sửa dòng cũ
  10 hết hiệu lực theo chủ đề | 11 hiệu lực có điều kiện (pending_event) | 13,14 hiệu lực có thời hạn + overrides
  15 cập nhật cấp luật qua bản hợp nhất | 18 văn bản ban hành theo luật cũ (chỉ ghi cờ). Các loại 9 (chuyển tiếp) giữ thành đơn vị.
Câu chỉ thị không thuộc loại nào: ghi unknown_directive, KHÔNG đoán, KHÔNG áp. Đề xuất theo chủ đề mang cờ topic_by_chapter / topic_uncertain.
Quyết định chỗ spec im lặng: docs/quyet_dinh/l6_checks_graph_viewer_quyet_dinh.txt.
"""
import collections
import datetime
import re
import sys
from pathlib import Path
from typing import NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import parse as l1
import refs as l2
import l6_versions as l6v
import textutil
import corpus

OPEN_Q, CLOSE_Q = "“", "”"
RE_DATE = re.compile(r"ngày\s+(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})", re.I)
KIND = l2.KINDS
RE_SELF_EFF = re.compile(rf"^{KIND}[ ]+này[ ]+có[ ]+hiệu[ ]+lực(?:[ ]+thi[ ]+hành)?(?:[ ]+kể)?[ ]+từ[ ]+ngày", re.I)
RE_TOPIC = re.compile(r"^Nội dung về (?P<topic>.+?) quy định tại (?P<doc>.+?) hết hiệu lực", re.I)
RE_COND = re.compile(rf"^(?P<targets>.+?)[ ]+(?:của[ ]+{KIND}[ ]+này[ ]+)?có[ ]+hiệu[ ]+lực(?:[ ]+thi[ ]+hành)?[ ]+kể[ ]+từ[ ]+ngày[ ]+"
                     rf"(?P<event>(?!\d).+?)[ ]+có[ ]+hiệu[ ]+lực", re.I)
RE_EXPIRE = re.compile(r"hết[ ]+hiệu[ ]+lực(?:[ ]+thi[ ]+hành)?(?:[ ]+kể[ ]+từ[ ]+ngày[ ]+(?P<d>\d{1,2}[ ]+tháng[ ]+\d{1,2}[ ]+năm[ ]+\d{4}|"
                       rf"{KIND}[ ]+này[ ]+có[ ]+hiệu[ ]+lực))?", re.I)
GENERIC_TITLE = re.compile(r"quy định chung|điều khoản thi hành|điều khoản chung|điều khoản chuyển tiếp", re.I)


def dates_in(text):
    out = []
    for d, m, y in RE_DATE.findall(text):
        try:
            out.append(datetime.date(int(y), int(m), int(d)))
        except ValueError:
            pass
    return out


def child_id(parent, node):
    return f"{parent}.K{node.number}" if node.kind == "khoan" else f"{parent}.{l1.diem_code(node.number)}"


# ---- payload: khối trích dẫn thành cây đơn vị ----

class Node:
    def __init__(self, kind, number, heading=None):
        self.kind, self.number, self.heading, self.parts, self.children = kind, number, heading, [], []

    @property
    def text(self):
        return "\n".join(self.parts)


LEVEL_OF = {"dieu": 0, "khoan": 1, "diem": 2}


def parse_payload(lines, default=None):
    """Khối trích dẫn thành danh sách nút gốc (Điều/Khoản/Điểm kèm con). Bỏ nháy ngoài cùng; dòng không nhãn nối vào nút hiện tại.
    default: nút dùng khi dòng đầu không có nhãn (ND_70 "khoản 7 Điều 17": khối chỉ có chữ của khoản, không có "7."); None thì trả None."""
    text = "\n".join(lines).strip()
    if text.startswith(OPEN_Q):
        text = text[1:]
    text = re.sub(r"[”\"]\s*[.;,]*\s*$", "", text.rstrip())
    roots, stack = [], []
    for raw in text.split("\n"):
        line = l1.normalize_line(raw)
        if not line:
            continue
        m, kind = l1.RE_DIEU.match(line), "dieu"
        node = None
        if m:
            node = Node("dieu", m[1], m[2])
        else:
            m = l1.RE_KHOAN.match(line)
            if m:
                node = Node("khoan", m[1])
                if m[2]:
                    node.parts.append(m[2])
            else:
                m = l1.RE_DIEM.match(line)
                if m:
                    node = Node("diem", m[1])
                    if m[2]:
                        node.parts.append(m[2])
        if node is None:
            if not stack and default is not None:  # khối chỉ có chữ, không nhãn: là chữ của đơn vị đích duy nhất
                roots.append(default)
                stack.append(default)
            if stack:
                stack[-1].parts.append(line)
            else:
                return None  # dòng không nhãn trước nhãn đầu tiên và không có đích duy nhất: không đoán
            continue
        while stack and LEVEL_OF[stack[-1].kind] >= LEVEL_OF[node.kind]:
            stack.pop()
        (stack[-1].children if stack else roots).append(node)
        stack.append(node)
    return roots


# ---- ngữ cảnh ----

class Context:
    def __init__(self, docs, units, payloads, labels, footnotes, resolver, links=()):
        self.docs, self.units, self.payloads, self.labels, self.footnotes, self.resolver = docs, units, payloads, labels, footnotes, resolver
        self.links = list(links)  # cạnh based_on / details của L3: dùng cho loại 25 (văn bản được hướng dẫn bị sửa)
        self.unknown = []   # (doc, unit, text, lý do)
        self.unmatched = []  # chỉ thị đọc được nhưng đích / cụm không khớp
        self.notes = []

    @classmethod
    def build(cls, docs):
        units = {d: l1.load_units(d) for d in docs}
        payloads = {}
        for d in docs:
            by = collections.defaultdict(list)
            for p in l1.load_payloads(d):
                by[p["lead_unit"]].append(p)
            payloads[d] = by
        labels = {r["id"]: r for r in l1.read_jsonl(corpus.out_dir("l4") / "l4_labels.jsonl")}
        footnotes = {d: {r["n"]: r["text"] for r in l1.read_jsonl(l1.l1_dir() / f"l1_footnotes_{d}.jsonl")} for d in docs}
        l3_path = corpus.out_dir("l3") / "l3_links.jsonl"
        links = l1.read_jsonl(l3_path) if l3_path.exists() else []
        return cls(docs, units, payloads, labels, footnotes, l2.Resolver(docs, l2.load_headers()), links)


class Ev:
    """Nhật ký một sự kiện."""

    def __init__(self, doc):
        self.doc = doc
        self.touched, self.new, self.closed = set(), set(), set()
        self.flags = collections.Counter()
        self.actions = []
        self.unknown, self.discrepancy = [], []
        self.pending_event, self.triggered = [], []
        self.notes = []

    def row(self, store_size):
        return {"doc_id": self.doc.doc_id, "effective_date": l6v.iso(self.doc.ngay_hieu_luc), "actions": self.actions,
                "units_touched": sorted(self.touched), "units_new": len(self.new), "units_closed": len(self.closed),
                "flags": dict(self.flags), "unknown_directive": self.unknown, "consolidation_discrepancy": sorted(set(self.discrepancy)),
                "pending_event_units": self.pending_event, "triggered": self.triggered, "notes": self.notes, "llm_calls": 0}


# ---- tra đích của chỉ thị ----

def unit_children(units, uid):
    return [k for k, v in units.items() if v.get("parent") == uid]


def find_doc_tail(text):
    """Đuôi văn bản (không phải 'X này') trong text: 'của Nghị định số ...' hoặc ngay sau một cụm điều/khoản."""
    for m in re.finditer(rf"[ ]+(?:của|tại)(?=[ ]+{KIND})", text):
        t = l2.parse_tail(text, m.start())
        if t is not None and not t.self_ref:
            return t
    for ref in l2.find_refs("x", text):
        if ref.tail is not None and not ref.tail.self_ref:
            return ref.tail
    return None


def directive_doc(units, uid):
    """Văn bản bị sửa: đuôi gần nhất đi ngược từ chính đơn vị lên tổ tiên (chữ của đơn vị rồi tiêu đề)."""
    cur = units.get(uid)
    while cur is not None:
        for t in ((cur.get("text") or "").split("\n")[0], cur.get("heading") or ""):
            tail = find_doc_tail(t)
            if tail:
                return tail
        cur = units.get(cur.get("parent"))
    return None


def targets_of(ctx, units, uid, text, doc_id):
    """Mã đích trong văn bản doc_id của mọi cụm điều/khoản/điểm trong text. -> (list mã, list lý do lỗi)."""
    out, errs = [], []
    for ref in l2.find_refs(uid, text):
        if ref.pl is not None or ref.tail is not None and ref.tail.self_ref:
            continue
        ids, why = l2.chain_targets(uid, ref.items, {}, doc_id)
        if why:
            errs.append(f"{ref.phrase!r}: {why}")
        else:
            out += [t for t in ids if t not in out]
    return out, errs


# ---- áp một nút payload ----

def apply_node(store, tid, node, eff, source, directive, ev, parent_id, replace_children=True, flags=()):
    """Đặt chữ cho tid theo nút payload; con của payload thay con cũ (con cũ không còn trong payload thì bị đóng)."""
    cur = store.cur(tid)
    text = node.text
    if cur is None:
        store.add(l6v.Ver(tid, 1, node.kind, node.number, node.heading, text, parent_id, eff, None, None, "normal", None, source, None, None,
                         ["inserted", *flags], directive))
        ev.new.add(tid)
    elif cur.effective_to is not None and cur.effective_to <= eff:
        store.new_version(tid, eff, source, text, node.heading, ["reopened", *flags], directive)  # mở lại mã đã đóng
        ev.touched.add(tid)
    elif textutil.text_norm(cur.text) != textutil.text_norm(text) or (node.kind == "dieu" and textutil.text_norm(cur.heading or "") != textutil.text_norm(node.heading or "")):
        store.new_version(tid, eff, source, text, node.heading if node.kind == "dieu" else None, flags, directive)
        ev.touched.add(tid)
    new_ids = set()
    for ch in node.children:
        cid = child_id(tid, ch)
        new_ids.add(cid)
        apply_node(store, cid, ch, eff, source, directive, ev, tid, True, flags)
    if replace_children:
        for old in list(store.children.get(tid, [])):
            if old not in new_ids and store.open(old) is not None:
                n = store.close_tree(old, eff, source, ["removed_by_replace"])
                ev.closed.update(d for d in [old, *store.descendants(old)])


# ---- thay cụm từ ----

def _flex(phrase):
    """Mẫu regex khớp cụm bất kể khoảng trắng và kiểu đặt dấu thanh (ủy/uỷ, hòa/hoà)."""
    pat = re.escape(phrase.strip())
    pat = re.sub(r"(?:\\ )+", r"\\s+", pat)
    for a, b in textutil.TONE:  # mỗi cặp kiểu dấu thanh thành nhóm chọn một (không phân biệt hoa thường)
        pat = re.sub(f"{a}|{b}", f"(?:{a}|{b})", pat, flags=re.I)
    return pat


def replace_phrase(text, old, new):
    """Thay mọi lần xuất hiện của cụm cũ (khớp mềm: khoảng trắng, kiểu dấu thanh, hoa/thường). Trả (chữ mới, số lần)."""
    if old in text:
        return text.replace(old, new), text.count(old)
    return re.subn(_flex(old), lambda m: new, text, flags=re.I)


PAIR_RE = re.compile(r"(?:cụm từ|từ)\s+§(\d+)§(?:\s+tại\s+(?P<mid>.+?))?\s+(?:bằng|thành)\s+(?:cụm từ|từ)\s+§(\d+)§")
DEL_RE = re.compile(r"^(?:Bãi bỏ|Bỏ)\s+(?:cụm từ|từ|đoạn(?: mở đầu)?)\s+§(\d+)§(?:\s+và\s+(?:cụm từ|từ|đoạn)\s+§(\d+)§)*")


def split_clauses(text):
    return re.split(r";\s*(?=(?:Thay thế|Bổ sung|Bãi bỏ|Bỏ|Sửa đổi)\b)", text)


def mask_quotes(text):
    """Thay mỗi cụm trong nháy “...” bằng §k§ để regex không vấp dấu câu trong cụm. Trả (text, list cụm)."""
    quotes = []

    def sub(m):
        quotes.append(m[1])
        return f"§{len(quotes) - 1}§"
    return re.sub(r"“([^”]*)”", sub, text), quotes


# ---- vòng chính ----

def apply_event(ctx, store, doc):
    ev = Ev(doc)
    units = ctx.units[doc.doc_id]
    eff = doc.ngay_hieu_luc
    if doc.is_consolidation:
        consolidation_compare(ctx, store, doc, units, eff, ev)
    else:
        term_end, early = own_effective(ctx, doc, units, eff, ev)
        l6v.add_doc_units(store, doc, units, eff, term_end)
        ev.new.update(units)
        ev.actions.append(f"nạp {len(units)} đơn vị, hiệu lực từ {eff.isoformat()}" + (f" đến hết {(term_end - datetime.timedelta(days=1)).isoformat()}" if term_end else ""))
        if ctx.resolver.blld_year(doc) == 2012:
            ev.flags["law_2012_era_document"] += 1  # loại 18: căn cứ BLLĐ 2012 (theo dòng "Căn cứ", cùng quy tắc với L2), không nối vào BLLĐ 2019
        amending(ctx, store, doc, units, eff, ev)
        effect_statements(ctx, store, doc, units, eff, ev)
        supplements(ctx, store, doc, units, eff, ev)
        if term_end:
            overrides(ctx, store, doc, units, eff, term_end, ev)
        import l6_rare  # import trễ: l6_rare cũng import module này
        l6_rare.apply_rare(ctx, store, doc, units, eff, ev)  # loại hiếm 19, 21, 22, 26; chạy sau effect_statements để văn bản cũ đã đóng trước khi xét 26
    check_triggers(ctx, store, doc, units, eff, ev)
    import l6_rare
    changed_docs = {k.split(".")[0] for k in ev.touched | ev.closed} - {doc.doc_id}
    parents = l6_rare.mark_parent_changed(store, ctx.links, changed_docs, doc.doc_id, eff)  # loại 25: cờ, không đóng văn bản hướng dẫn
    if parents:
        ev.flags["parent_changed"] += len(parents)
        ev.notes.append(f"văn bản hướng dẫn có đích bị đổi: {parents}")
    return ev.row(len(store.vers))


def own_effective(ctx, doc, units, eff, ev):
    """Đọc câu '<loại> này có hiệu lực ... [đến hết ngày ...]': đối chiếu ngày với manifest, trả (ngày hết hạn + 1, có điều khoản kết thúc sớm)."""
    term_end, early = None, False
    for uid, u in units.items():
        t = (u.get("text") or "")
        if u["type"] in ("khoan", "dieu") and RE_SELF_EFF.match(t):
            ds = dates_in(t)
            if ds and ds[0] != eff:
                ev.notes.append(f"ngày hiệu lực trong chữ {ds[0].isoformat()} khác manifest {eff.isoformat()} ({uid})")
            if len(ds) > 1 and re.search(r"đến hết ngày", t):
                term_end = ds[1] + datetime.timedelta(days=1)
                early = "trừ trường hợp" in t
                ev.flags["has_term"] += 1
            break
    return term_end, early


# ---- sửa đổi, bổ sung, bãi bỏ có đích ----

def amending(ctx, store, doc, units, eff, ev):
    for uid, u in units.items():
        text = u.get("text") or ""
        if u["type"] not in ("dieu", "khoan", "diem") or not text or not l2.is_directive(text):
            continue
        first = text.split("\n")[0]
        kids = [k for k in unit_children(units, uid) if l2.is_directive(units[k].get("text") or "")]
        payload = ctx.payloads[doc.doc_id].get(uid)
        tail = directive_doc(units, uid)
        res = ctx.resolver.resolve(tail, doc) if tail else None
        masked, quotes = mask_quotes(first)
        try:
            if kids and not payload:
                continue  # câu dẫn của nhóm chỉ thị con
            if re.search(r"Mẫu số", masked):  # mẫu biểu của văn bản bị sửa: văn bản đó không kèm phụ lục trong kho
                ev.flags["form_directive_target_not_in_kb"] += 1
                ev.notes.append(f"{uid}: chỉ thị về mẫu biểu, mẫu không có trong kho: {first[:70]}")
                continue
            import l6_rare
            if l6_rare.RE_SUSPEND.match(first):
                continue  # loại 21: l6_rare.apply_rare quét và xử lý
            if l6_rare.try_directive(ctx, store, doc, uid, units, first, payload, tail, res, eff, ev):
                continue  # loại 16 (bãi bỏ phần phụ lục), loại 20 (đính chính)
            if re.search(r"(?:cụm từ|từ|đoạn)\s+§\d+§", masked):
                phrase_directive(ctx, store, doc, uid, units, masked, quotes, tail, res, eff, ev)
            elif payload:
                payload_directive(ctx, store, doc, uid, units, first, payload, tail, res, eff, ev)
            elif re.match(r"^(?:Bãi bỏ|Bỏ|Hủy bỏ)\b", first):
                repeal_directive(ctx, store, doc, uid, units, first, tail, res, eff, ev)
            elif re.search(r"Mẫu số|Phụ lục", first):
                ev.flags["form_directive_target_not_in_kb"] += 1
                ev.notes.append(f"{uid}: chỉ thị về mẫu / phụ lục của văn bản bị sửa, văn bản đó không kèm phụ lục: {first[:70]}")
            else:
                ctx.unknown.append((doc.doc_id, uid, first[:120], "không thuộc loại chỉ thị nào đã cài"))
                ev.unknown.append({"unit": uid, "text": first[:160]})
        except ValueError as e:
            ctx.unknown.append((doc.doc_id, uid, first[:120], str(e)))
            ev.unknown.append({"unit": uid, "text": first[:160], "reason": str(e)})


def _target_doc(ctx, store, doc, tail, res, uid, ev, edge_kind, first, eff, target_text):
    """Giải văn bản bị sửa. Văn bản chưa có trong KB: ghi quan hệ chờ đích (không áp). -> doc_id hoặc None."""
    if res is None:
        raise ValueError("không xác định được văn bản bị sửa")
    if res[0] == "doc" and any(store.exists(k) for k in ctx.units.get(res[1], {})):
        return res[1]
    number = res[1] if res[0] == "pending" else ctx.docs[res[1]].so_hieu
    store.pending.append({"source": uid, "edge": edge_kind, "target_number": number, "target_name": tail.name if tail else None,
                          "target_units": target_text, "text": first[:200], "effective": l6v.iso(eff)})
    ev.flags["pending_target_doc"] += 1
    return None


def payload_directive(ctx, store, doc, uid, units, first, payload, tail, res, eff, ev):
    tdoc = _target_doc(ctx, store, doc, tail, res, uid, ev, "amends", first, eff, "")
    if tdoc is None:
        return
    ids, errs = targets_of(ctx, units, uid, first, tdoc)
    if errs or not ids:
        raise ValueError("đích không đọc được: " + "; ".join(errs or ["không có cụm điều/khoản/điểm"]))
    rename = re.search(r"\btên\b", first.split("như sau")[0]) is not None
    verb_insert = re.match(r"^Bổ sung\b", first) is not None
    first_id = ids[0].split(".")[-1]
    kind0 = "khoan" if first_id.startswith("K") else "dieu" if first_id.startswith("D") and ids[0].count(".") == 1 else "diem"
    num0 = first_id[1:] if kind0 != "diem" else first_id.replace("dd", "đ")
    roots = parse_payload(payload[0]["lines"], Node(kind0, num0) if len(ids) == 1 else None)
    if not roots:
        raise ValueError("khối trích dẫn không đọc được")
    used = set()
    for tid in ids:
        exists = store.open(tid) is not None
        if exists and verb_insert and not re.match(r"^Bổ sung\b.*\bsửa\b", first):
            raise ValueError(f"bổ sung vào mã đã có: {tid}")
        seg = tid.split(".")[-1]
        want_kind = "khoan" if seg.startswith("K") else "dieu" if seg.startswith("D") and tid.count(".") == 1 else "diem"
        number = seg[1:] if want_kind != "diem" else (seg.replace("dd", "đ"))
        root = next((r for r in roots if r.kind == want_kind and r.number == number), None)
        if root is None:
            raise ValueError(f"khối trích dẫn không có nút {want_kind} {number} cho {tid}")
        used.add(id(root))
        parent_id = ".".join(tid.split(".")[:-1]) or None
        if not exists and not store.exists(parent_id or ""):
            raise ValueError(f"mã cha {parent_id} không tồn tại để chèn {tid}")
        flags = ["rename_only"] if rename else []
        if rename:
            cur = store.cur(tid)
            if cur is None:
                raise ValueError(f"đổi tên mã không tồn tại: {tid}")
            node = Node(root.kind, root.number, root.heading)
            node.parts = root.parts
            apply_node(store, tid, node, eff, doc.doc_id, uid, ev, parent_id, replace_children=False, flags=flags)
        else:
            apply_node(store, tid, root, eff, doc.doc_id, uid, ev, parent_id, True)
        rel = "replaces" if first.startswith("Thay thế") else "amends"
        store.add_edge(uid, rel, tid, first[:200], doc.doc_id, eff, flags=["inserted"] if not exists else [])
        ev.actions.append(f"{uid} {rel} {tid}")
    if len(used) != len(roots):
        raise ValueError("khối trích dẫn có nút không khớp đích nào")


def repeal_directive(ctx, store, doc, uid, units, first, tail, res, eff, ev):
    tdoc = _target_doc(ctx, store, doc, tail, res, uid, ev, "repeals", first, eff, first[:120])
    if tdoc is None:
        return
    ids, errs = targets_of(ctx, units, uid, first, tdoc)
    if errs or not ids:
        raise ValueError("đích không đọc được: " + "; ".join(errs or ["không có cụm điều/khoản/điểm"]))
    for tid in ids:
        if store.open(tid) is None:
            ctx.unmatched.append((doc.doc_id, uid, f"bãi bỏ mã không có hoặc đã đóng: {tid}"))
            continue
        n = store.close_tree(tid, eff, doc.doc_id, ["repealed"])
        ev.closed.update([tid, *store.descendants(tid)])
        store.add_edge(uid, "repeals", tid, first[:200], doc.doc_id, eff)
        ev.actions.append(f"{uid} repeals {tid}")


def phrase_directive(ctx, store, doc, uid, units, masked, quotes, tail, res, eff, ev):
    tdoc = _target_doc(ctx, store, doc, tail, res, uid, ev, "amends", masked[:200], eff, "")
    if tdoc is None:
        return
    done = 0
    for clause in split_clauses(masked):
        delete = DEL_RE.match(clause.strip())
        pairs = list(PAIR_RE.finditer(clause))
        if not pairs and not delete:
            raise ValueError(f"cụm từ không đọc được: {clause[:80]}")
        trailing = ""
        if pairs:
            m = re.search(r"\btại\s+(.+)$", clause[pairs[-1].end():])
            trailing = m[1] if m else ""
        items = [(quotes[int(p[1])], quotes[int(p[3])], p.group("mid") or trailing) for p in pairs]
        if delete:
            m = re.search(r"\btại\s+(.+)$", clause)
            items = [(quotes[int(g)], "", m[1] if m else "") for g in DEL_RE.match(clause.strip()).groups() if g]
        for old, new, where in items:
            if re.search(r"Mẫu số|Phụ lục", where):
                ev.flags["form_directive_target_not_in_kb"] += 1
                continue
            ids, errs = targets_of(ctx, units, uid, where, tdoc)
            if errs or not ids:
                raise ValueError(f"đích của cụm {old!r} không đọc được: {where!r}")
            hit = False
            for tid in ids:
                for x in [tid, *store.descendants(tid)]:
                    v = store.open(x)
                    if v is None or v.state != "normal":
                        continue
                    for field_name in ("text",):
                        newtext, n = replace_phrase(v.text, old, new)
                        if n:
                            hit = True
                            store.new_version(x, eff, doc.doc_id, newtext, None, ["phrase_replaced"], uid)
                            ev.touched.add(x)
                            store.add_edge(uid, "replaces" if new else "repeals", x, f"{old} -> {new}"[:200], doc.doc_id, eff)
            if not hit:
                ctx.unmatched.append((doc.doc_id, uid, f"cụm {old!r} không thấy trong {ids}"))
            done += 1
    ev.actions.append(f"{uid}: {done} thao tác cụm từ")


# ---- câu hiệu lực / hết hiệu lực / có điều kiện ----

def effect_statements(ctx, store, doc, units, eff, ev):
    for uid, u in units.items():
        if u["type"] not in ("khoan", "diem", "dieu") or not u.get("text"):
            continue
        dieu = ".".join(uid.split(".")[:2])
        if ctx.labels.get(dieu, {}).get("label") != "effect_transition":
            continue
        text = u["text"].replace("\n", " ")
        if l2.is_directive(text) or RE_SELF_EFF.match(text) and not RE_EXPIRE.search(text):
            continue
        m = RE_TOPIC.match(text)
        if m:
            topic_expire(ctx, store, doc, uid, text, m, eff, ev)
            continue
        m = RE_COND.match(text)
        if m and not re.match(rf"{KIND}[ ]+này", m["event"], re.I):
            conditional(ctx, store, doc, uid, units, m, eff, ev)
            continue
        if re.search(r"quy định tương ứng trong " + KIND + r" này hết hiệu lực", text, re.I):  # loại 13: tự hết khi có văn bản thay
            ev.flags["ends_when_replaced"] += 1
            store.add_edge(uid, "ends_when_replaced", doc.doc_id, text[:200], doc.doc_id, eff, flags=["term_mechanism"])
            continue
        import l6_rare
        if (RE_EXPIRE.search(text) or l6_rare.RE_ANNUL.search(text)) and u["type"] != "dieu":
            repeal_docs(ctx, store, doc, uid, units, u, text, eff, ev)


def expire_date(text, eff):
    m = RE_EXPIRE.search(text)
    if m and m["d"] and RE_DATE.search("ngày " + m["d"]):
        ds = dates_in("ngày " + m["d"])
        return ds[0] if ds else eff
    return eff


def repeal_docs(ctx, store, doc, uid, units, u, text, eff, ev):
    """Câu 'X hết hiệu lực': cả văn bản (loại 5), hoặc đơn vị của văn bản khác (chờ đích), hoặc danh sách con."""
    kids = unit_children(units, uid)
    if text.rstrip().endswith(":") and kids:  # "các Nghị định sau đây hết hiệu lực:" + từng mục
        when = expire_date(text, eff)
        for k in kids:
            repeal_one(ctx, store, doc, k, units[k]["text"].replace("\n", " "), when, ev)
        return
    for sentence in re.split(r"(?<=[.])\s+(?=[A-ZĐ])", text):  # một đơn vị có thể gồm câu hiệu lực rồi câu hết hiệu lực (ND_90)
        import l6_rare
        if RE_EXPIRE.search(sentence) or l6_rare.RE_ANNUL.search(sentence):
            repeal_one(ctx, store, doc, uid, sentence, expire_date(sentence, eff), ev)


def repeal_one(ctx, store, doc, uid, text, when, ev):
    head = text.split(" hết hiệu lực")[0]
    if re.match(r"^(?:các[ ]+)?(?:điều|khoản|điểm|mục|phụ lục)\b", head, re.I):  # đơn vị của văn bản khác
        number = next(iter(re.findall(l2.NUMBER_RE, text)), None)
        target = ctx.resolver.by_number.get(l2.norm_number(number)) if number else None
        store.pending.append({"source": uid, "edge": "repeals", "target_number": l2.norm_number(number) if number else None, "target_name": None,
                              "target_units": head[:120], "text": text[:200], "effective": l6v.iso(when)})
        ev.flags["pending_unit_repeal"] += 1
        return
    numbers = []
    for seg in re.split(r";\s*", head):
        mm = re.match(rf"^{KIND}[ ]+số[ ]+({l2.NUMBER_RE})", seg.strip())
        if mm:
            numbers.append(l2.norm_number(mm[1]))
    if not numbers:
        ctx.unknown.append((doc.doc_id, uid, text[:120], "hết hiệu lực nhưng không đọc được số hiệu văn bản"))
        ev.unknown.append({"unit": uid, "text": text[:160], "reason": "không đọc được số hiệu"})
        return
    for number in numbers:
        tdoc = ctx.resolver.by_number.get(number)
        if tdoc and any(store.exists(k) for k in ctx.units[tdoc]):
            import l6_rare
            flags = ["doc_replaced"] + (["annulled"] if l6_rare.RE_ANNUL.search(text) else [])  # loại 24: bị bãi bỏ vì trái luật
            n = sum(int(store.close(k, when, doc.doc_id, flags)) for k in ctx.units[tdoc] if store.exists(k))
            ev.closed.update(k for k in ctx.units[tdoc])
            store.add_edge(uid, "replaces", tdoc, text[:200], doc.doc_id, when)
            ev.actions.append(f"{uid} replaces {tdoc} ({n} đơn vị đóng từ {when.isoformat()})")
        else:
            store.pending.append({"source": uid, "edge": "replaces", "target_number": number, "target_name": None, "target_units": "",
                                  "text": text[:200], "effective": l6v.iso(when)})
            store.add_edge(uid, "replaces", f"external:{number}", text[:200], doc.doc_id, when, flags=["target_outside_kb"])
            ev.flags["pending_target_doc"] += 1


def topic_expire(ctx, store, doc, uid, text, m, eff, ev):
    """Loại 10: hết hiệu lực một phần theo chủ đề, không theo số điều. Chia theo tiêu đề Chương (regex, không LLM): Chương có tiêu đề
    chứa chủ đề -> đóng; Chương chung (quy định chung, điều khoản thi hành) -> suspended + cờ; còn lại giữ nguyên hiệu lực."""
    number = next(iter(re.findall(l2.NUMBER_RE, m["doc"])), None)
    tdoc = ctx.resolver.by_number.get(l2.norm_number(number)) if number else None
    if not tdoc or not any(store.exists(k) for k in ctx.units[tdoc]):
        store.pending.append({"source": uid, "edge": "expires_by_topic", "target_number": number, "target_name": None, "target_units": m["topic"],
                              "text": text[:200], "effective": l6v.iso(eff)})
        return
    key = re.sub(r"^(?:người[ ]+)?", "", m["topic"].split(" làm việc")[0].strip().casefold())
    tunits = ctx.units[tdoc]
    closed = susp = 0
    for cid, c in tunits.items():
        if c["type"] != "chuong":
            continue
        title = (c.get("heading") or "").casefold()
        members = [k for k, v in tunits.items() if k != cid and _under(tunits, k, cid)]
        if key in title:
            for k in [cid, *members]:
                closed += int(store.close(k, eff, doc.doc_id, ["topic_by_chapter"]))
            ev.closed.update([cid, *members])
        elif GENERIC_TITLE.search(title):
            for k in [cid, *members]:
                v = store.open(k)
                if v is not None and v.state == "normal":
                    nv = store.new_version(k, eff, doc.doc_id, None, None, ["topic_uncertain"], uid, "suspended", f"chủ đề: {m['topic']}")
                    susp += 1
                    ev.touched.add(k)
    store.add_edge(uid, "expires_by_topic", tdoc, text[:200], doc.doc_id, eff, flags=["topic_by_chapter"], topic=m["topic"])
    ev.actions.append(f"{uid} expires_by_topic {tdoc}: đóng {closed}, suspended {susp}")


def _under(units, k, ancestor):
    cur = units.get(k)
    while cur is not None:
        if cur.get("parent") == ancestor:
            return True
        cur = units.get(cur.get("parent"))
    return False


def conditional(ctx, store, doc, uid, units, m, eff, ev):
    """Loại 11: đơn vị chỉ có hiệu lực khi một văn bản khác có hiệu lực -> pending_event, lưu nguyên văn sự kiện."""
    ids, errs = targets_of(ctx, units, uid, m["targets"] + " của Nghị định này", doc.doc_id)
    refs = [r for r in l2.find_refs(uid, m["targets"]) if r.pl is None]
    targets = []
    for ref in refs:
        t, why = l2.chain_targets(uid, ref.items, units, doc.doc_id)
        if why:
            raise ValueError(f"hiệu lực có điều kiện, đích không đọc được: {why}")
        targets += t
    if not targets:
        raise ValueError("hiệu lực có điều kiện nhưng không có đích điều/khoản/điểm")
    event = m["event"].strip()
    for tid in targets:
        for x in [tid, *[d for d in store.descendants(tid)]]:
            v = store.cur(x)
            if v is None or v.source_event != doc.doc_id:
                continue
            v.state, v.effective_from, v.trigger = "pending_event", None, event
            v.flags.append("pending_event")
            ev.pending_event.append(x)
        store.add_edge(uid, "pending_on", tid, event[:200], doc.doc_id, eff, flags=["pending_event"])
    ev.actions.append(f"{uid}: {len(targets)} đích chờ sự kiện: {event[:80]}")


MIN_DESCRIPTION = 12  # mô tả văn bản kích hoạt ngắn hơn (ký tự sau chuẩn hoá) thì quá chung để khớp: giữ chờ


def trigger_matches(trigger, doc, units):
    """Văn bản `doc` (vừa nạp) có phải văn bản mà mô tả sự kiện `trigger` đang chờ không? Phải đủ BA điều kiện, thiếu một thì KHÔNG khớp (giữ chờ):
      1. cùng loại văn bản (câu mô tả mở đầu bằng "Nghị định ..." thì doc là Nghị định);
      2. mọi số hiệu mà mô tả nêu đều xuất hiện trong chữ của doc;
      3. cụm mô tả chính nó (phần sau từ chỉ loại, trước "(" hoặc trước "của <loại> số ...") nằm trong Điều 1 của doc (tiêu đề, chữ, các con).
    Chỉ nhắc số hiệu là chưa đủ: ND_219 Điều 35 trích đúng hai số hiệu mà mô tả của ND_283 Điều 66 khoản 3 trích, nhưng không phải văn bản đó.
    Thất bại là an toàn (đơn vị vẫn pending_event); câu mô tả diễn đạt khác với Điều 1 của văn bản thật sẽ không khớp, việc của lượt LLM sau."""
    kind = re.match(KIND, trigger or "")
    if not kind or kind[0] != doc.loai:
        return False
    numbers = {l2.norm_number(n) for n in re.findall(l2.NUMBER_RE, trigger)}
    body = l2.norm_number(" ".join((u.get("text") or "") + " " + (u.get("heading") or "") for u in units.values()))
    if not numbers or not all(n in body for n in numbers):
        return False
    description = textutil.text_norm(re.split(rf"\(| của {KIND}", trigger[kind.end():])[0])
    d1 = textutil.text_norm(" ".join((u.get("heading") or "") + " " + (u.get("text") or "") for k, u in units.items()
                                if k == f"{doc.doc_id}.D1" or k.startswith(f"{doc.doc_id}.D1.")))
    return len(description) >= MIN_DESCRIPTION and description in d1


def check_triggers(ctx, store, doc, units, eff, ev):
    """Văn bản vừa nạp có kích hoạt đơn vị pending_event không? Khớp theo trigger_matches; không khớp thì giữ chờ."""
    for vs in store.vers.values():
        v = vs[-1]
        if v.state != "pending_event" or v.source_event == doc.doc_id:
            continue
        if trigger_matches(v.trigger, doc, units):
            v.state, v.effective_from = "normal", eff
            ev.triggered.append(v.id)
            store.add_edge(doc.doc_id, "triggers", v.id, (v.trigger or "")[:200], doc.doc_id, eff)


# ---- bổ sung danh mục (loại 8) ----

def supplements(ctx, store, doc, units, eff, ev):
    for uid, u in units.items():
        if u["type"] != "dieu":
            continue
        m = re.match(r"^Bổ sung (Danh mục .+)$", u.get("heading") or "", re.I)
        if not m:
            continue
        key = textutil.text_norm(m[1])[:60]
        mine = next((k for k, v in units.items() if v["type"] == "pl"), None)
        cands = [k for d, us in ctx.units.items() if d != doc.doc_id for k, v in us.items()
                 if v["type"] == "pl" and store.exists(k) and key in textutil.text_norm(v.get("heading") or "")]
        if mine is None or len(cands) != 1:
            ctx.unknown.append((doc.doc_id, uid, u["heading"][:120], f"bổ sung danh mục: {len(cands)} phụ lục khớp, cần đúng 1"))
            ev.unknown.append({"unit": uid, "text": u["heading"][:160]})
            continue
        tgt = cands[0]
        old_norm = {textutil.text_norm(store.cur(k).text) for k in store.descendants(tgt) if store.cur(k).type == "pl_row"}
        n_new = n_dup = 0
        base_n = sum(1 for k in store.children[tgt] if store.cur(k).type == "pl_row")
        for k in store.descendants(mine):
            v = store.cur(k)
            if v.type != "pl_row":
                continue
            if textutil.text_norm(v.text) in old_norm:
                n_dup += 1
                continue
            base_n += 1
            nid = f"{tgt}.R{base_n}"
            store.add(l6v.Ver(nid, 1, "pl_row", str(base_n), None, v.text, tgt, eff, None, None, "normal", None, doc.doc_id, None, None,
                             ["supplement_row"], uid))
            ev.new.add(nid)
            store.add_edge(k, "supplements_list", nid, v.text[:120], doc.doc_id, eff)
            n_new += 1
        store.add_edge(mine, "supplements_list", tgt, u["heading"][:120], doc.doc_id, eff)
        ev.actions.append(f"{uid} supplements_list {tgt}: {n_new} dòng mới, {n_dup} dòng đã có")


# ---- hiệu lực có thời hạn và áp dụng thay (loại 13, 14) ----

def overrides(ctx, store, doc, units, eff, term_end, ev):
    """Phụ lục trong phạm vi (PL_IN_SCOPE) có tiêu đề mục dẫn tới đơn vị của văn bản khác: overrides trong [hiệu lực, term_end)."""
    scope = corpus.PL_IN_SCOPE.get(doc.doc_id, set())
    n = 0
    for uid, u in units.items():
        if u["type"] != "pl_muc" or not any(uid.startswith(f"{doc.doc_id}.PL{lab}.") for lab in scope):
            continue
        heading = u.get("heading") or ""
        for ref in l2.find_refs(uid, heading):
            r = l2.resolve_ref(doc, uid, {}, ref, ctx.units, ctx.resolver, set(ctx.units))
            for t in r.targets:
                if t.split(".")[0] == doc.doc_id:
                    continue
                store.add_edge(uid, "overrides", t, ref.phrase[:200], doc.doc_id, eff, flags=["interval"], valid_from=l6v.iso(eff),
                               valid_to=l6v.iso(term_end))
                n += 1
    ev.actions.append(f"overrides: {n} cạnh trong [{eff.isoformat()}, {l6v.iso(term_end)})")


# ---- bản hợp nhất (loại 15) ----

def line_only_dieu(store, doc, vunits, base):
    """Các Điều (mã trong văn bản gốc) mà bản hợp nhất chỉ khác chỗ ngắt dòng: cùng tập đơn vị và cùng bộ ký tự (đã text_norm).
    Tập đơn vị khác (Điều 42 mất đánh dấu điểm) hoặc chữ khác (Điều 185: 189 thành 89) thì không nằm trong tập này."""
    out = set()
    for vid, vu in vunits.items():
        if vu["type"] != "dieu":
            continue
        bid = base + vid[len(doc.doc_id):]
        if not store.exists(bid):
            continue
        b_ids = [x for x in [bid, *store.descendants(bid)] if store.cur(x).source_event == base]
        v_ids = [base + k[len(doc.doc_id):] for k in vunits if k == vid or k.startswith(vid + ".")]
        if set(b_ids) != set(v_ids):
            continue
        b_chars = collections.Counter(re.sub(r"\W", "", "".join(textutil.text_norm(store.cur(x).text) for x in b_ids)))
        v_chars = collections.Counter(re.sub(r"\W", "", "".join(textutil.text_norm(vunits[doc.doc_id + x[len(base):]].get("text") or "") for x in v_ids)))
        if b_chars == v_chars:
            out.add(bid)
    return out


def consolidation_compare(ctx, store, doc, vunits, eff, ev):
    """So từng đơn vị của bản hợp nhất với văn bản gốc (đã nạp). Chỉ khác chuẩn hoá thì không đổi; khác thật + có chú thích ngày hiệu lực thì
    mở phiên bản / đơn vị mới từ ngày đó; khác mà không có chú thích thì cờ consolidation_discrepancy, KHÔNG tạo phiên bản."""
    base = corpus.BASE_DOC_ID
    fn = ctx.footnotes[doc.doc_id]
    seen_base = set()
    stats = collections.Counter()
    line_only = line_only_dieu(store, doc, vunits, base)
    for vid, vu in vunits.items():
        if vu["type"] not in ("dieu", "khoan", "diem"):
            continue
        bid = base + vid[len(doc.doc_id):]
        seen_base.add(bid)
        notes = [fn.get(n, "") for n in vu.get("footnote", [])]
        when = next((d for t in notes for d in dates_in(t.split("có hiệu lực", 1)[-1])[:1] if "có hiệu lực" in t), None)
        law = next((l2.norm_number(n) for t in notes for n in re.findall(l2.NUMBER_RE, t)), None)
        cur = store.cur(bid)
        if cur is None:
            if when:
                parent = vu.get("parent") and base + vu["parent"][len(doc.doc_id):]
                store.add(l6v.Ver(bid, 1, vu["type"], vu["number"], vu.get("heading"), vu.get("text") or "", parent, when, None, None, "normal",
                                 None, doc.doc_id, None, None, ["from_consolidation"], None, list(vu.get("footnote", []))))
                ev.new.add(bid)
                stats["unit_moi"] += 1
                store.add_edge(f"external:{law}" if law else doc.doc_id, "amends", bid, notes[0][:200], doc.doc_id, when, flags=["from_consolidation_footnote"])
            else:
                ev.discrepancy.append(bid)
                stats["moi_khong_chu_thich"] += 1
            continue
        same = (textutil.text_norm(cur.text) == textutil.text_norm(vu.get("text") or "")
                and (vu["type"] != "dieu" or textutil.text_norm(cur.heading or "") == textutil.text_norm(vu.get("heading") or "")))
        if same:
            stats["giong_sau_chuan_hoa"] += 1
        elif when:
            store.new_version(bid, when, doc.doc_id, vu.get("text") or "", vu.get("heading") if vu["type"] == "dieu" else None, ["from_consolidation"])
            ev.touched.add(bid)
            stats["phien_ban_moi"] += 1
        elif ".".join(bid.split(".")[:2]) in line_only:
            stats["chi_khac_ngat_dong"] += 1  # cùng tập đơn vị, cùng chữ, khác chỗ ngắt đoạn: không phải sửa đổi
        else:
            cur.flags.append("consolidation_discrepancy")
            ev.discrepancy.append(bid)
            stats["khac_khong_chu_thich"] += 1
    for bid, vs in store.vers.items():
        if bid.startswith(base + ".") and bid not in seen_base and vs[-1].type in ("dieu", "khoan", "diem") and vs[-1].source_event == base:
            vs[-1].flags.append("consolidation_discrepancy")
            ev.discrepancy.append(bid)
            stats["mat_trong_ban_hop_nhat"] += 1
    ev.flags.update({f"consolidation_{k}": v for k, v in stats.items()})
    store.add_edge(doc.doc_id, "consolidates", base, "bản hợp nhất", doc.doc_id, eff)
    ev.actions.append(f"so bản hợp nhất với {base}: {dict(stats)}")


# ---- báo cáo ----

def write_report(ctx, store, events, as_of):
    gates = dev_gates(ctx, store, as_of)
    out = ["L6 báo cáo", f"ngày as_of: {as_of.isoformat()}  đơn vị: {len(store.vers)}  phiên bản: {sum(len(v) for v in store.vers.values())}  "
           f"cạnh cập nhật: {len(store.edges)} {dict(collections.Counter(e['p'] for e in store.edges))}  quan hệ chờ đích: {len(store.pending)}"]
    out.append("sự kiện theo thứ tự nạp:")
    for ev in events:
        out.append(f"  {ev['effective_date']}  {ev['doc_id']:<22} mới {ev.get('units_new', 0):>5}  chạm {len(ev.get('units_touched', [])):>3}  "
                   f"đóng {ev.get('units_closed', 0):>5}  cờ {ev.get('flags', {})}")
    out.append(f"unknown_directive: {len(ctx.unknown)}")
    out += [f"  {d} {u}: {t!r} ({why})" for d, u, t, why in ctx.unknown]
    out.append(f"chỉ thị đọc được nhưng đích / cụm không khớp: {len(ctx.unmatched)}")
    out += [f"  {d} {u}: {why}" for d, u, why in ctx.unmatched]
    out.append("mốc cổng dev:")
    out += [f"  {'đạt' if ok else 'KHÔNG đạt'}: {name}" + (f" ({info})" if info else "") for name, ok, info in gates]
    path = corpus.report_dir("l6") / "l6_report.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(out))


def dev_gates(ctx, store, as_of):
    D = datetime.date
    g = []

    def vers(prefix):
        return [vs[-1] for k, vs in store.vers.items() if k.startswith(prefix + ".")]
    last = lambda k: store.cur(k)
    g.append(("ND_28: mọi đơn vị effective_to = 2022-01-17", all(v.effective_to == D(2022, 1, 17) for v in vers("ND_28-2020")), ""))
    g.append(("ND_12: mọi đơn vị effective_to = 2026-09-10", all(v.effective_to == D(2026, 9, 10) for v in vers("ND_12-2022")), ""))
    k8a = store.cur("BLLD_45-2019.D154.K8a")
    g.append(("BLLĐ Điều 154 có khoản 8a từ 2026-01-01", k8a is not None and k8a.effective_from == D(2026, 1, 1), ""))
    changed = [k for k, vs in store.vers.items() if k.startswith("BLLD_45-2019.") and len(vs) > 1]
    g.append(("các đơn vị khác của BLLĐ không đổi phiên bản", not changed, f"{len(changed)} đơn vị đổi" if changed else ""))
    g.append(("BLLĐ Điều 185 khoản 4 bị cờ consolidation_discrepancy", "consolidation_discrepancy" in (last("BLLD_45-2019.D185.K4").flags if last("BLLD_45-2019.D185.K4") else []), ""))
    g.append(("ND_283 Điều 66 khoản 2, 3: các đơn vị đích ở trạng thái pending_event",
              all(store.cur(k) is not None and store.cur(k).state == "pending_event" for k in ("ND_283-2026.D61.K2", "ND_283-2026.D63.K11", "ND_283-2026.D14")), ""))
    nq = vers("NQ_66-16-2026")
    g.append(("NQ_66-16: khoảng hiệu lực 2026-04-15 đến 2027-03-01 (hết ngày 28/02/2027)", bool(nq) and all(v.effective_to == D(2027, 3, 1) for v in nq), ""))
    g.append(("NQ_66-16: có cạnh overrides trong khoảng đó", any(e["p"] == "overrides" for e in store.edges), ""))
    for k in ("ND_152-2020.D7.K6", "ND_152-2020.D7.K14"):
        v = store.cur(k)
        g.append((f"{k} có version 2 từ 2023-09-18", v is not None and v.version >= 2 and any(x.effective_from == D(2023, 9, 18) and x.version == 2 for x in store.vers[k]), ""))
    k82 = store.vers.get("ND_152-2020.D8.K2", [])
    g.append(("ND_152.D8.K2 đổi cụm 'khoản 4, 6 và 8 Điều 154' từ 2023-09-18", any("khoản 4 và khoản 6 Điều 154" in x.text and x.effective_from == D(2023, 9, 18) for x in k82), ""))
    k8 = store.cur("ND_152-2020.D7.K8")
    g.append(("ND_152 Điều 7 khoản 8 (lao động nước ngoài) đóng từ 2025-08-07", k8 is not None and k8.effective_to == D(2025, 8, 7), ""))
    c3 = [v for v in vers("ND_152-2020") if v.type in ("dieu", "khoan") and ".D2" in v.id[11:] and int(re.search(r"\.D(\d+)", v.id)[1]) in range(22, 29)]
    g.append(("ND_152 phần người Việt Nam làm cho tổ chức nước ngoài (Điều 22-28) vẫn hiệu lực", bool(c3) and all(v.in_force(as_of) for v in c3), ""))
    tt11_new = [v for k, vs in store.vers.items() if k.startswith("TT_11-2020-BLDTBXH.PL") for v in vs if "supplement_row" in v.flags]
    tt11_old_changed = [k for k, vs in store.vers.items() if k.startswith("TT_11-2020-BLDTBXH.") and len(vs) > 1]
    g.append(("TT_11 có dòng danh mục mới từ 2024-02-15, dòng cũ không đổi phiên bản",
              bool(tt11_new) and all(v.effective_from == D(2024, 2, 15) for v in tt11_new) and not tt11_old_changed, f"{len(tt11_new)} dòng mới"))
    g.append(("không còn unknown_directive", not ctx.unknown, f"{len(ctx.unknown)} còn lại"))
    return g
