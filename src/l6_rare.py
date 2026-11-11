"""L6: các loại thay đổi mà kho KHÔNG có ca thật (plan loại 12, 16, 19-26). Cài đặt để framework xử lý được, kiểm bằng ví dụ tự soạn ở tests/.

Luận văn ghi các loại này là "đã cài đặt, chưa có ca thật để đo". Mỗi loại là một hàm nhỏ trên Store + một mẫu câu; câu không khớp mẫu thì
không làm gì (không đoán). Gọi từ l6_directives: apply_rare (quét mọi đơn vị của văn bản mới nạp) và try_directive (dòng chỉ thị đầu động từ).

  12 kích hoạt hiệu lực có điều kiện   -> l6_directives.check_triggers (đã có), kiểm bằng ví dụ ở tests/test_l6_rare.py
  16 bãi bỏ một phần phụ lục           -> repeal_appendix
  19 hồi tố (Luật 64 Điều 55, 58 khoản 2) -> retroactive: applies_from sớm hơn effective_from; hồi tố đặt trách nhiệm mới / nặng hơn thì chặn
  20 đính chính (NĐ 78 Điều 9)         -> correct: giữ cả hai chữ, cạnh `corrects`, KHÔNG tạo phiên bản pháp lý
  21 tạm ngưng / đình chỉ (Luật 64 Điều 56) -> suspend: state suspended trong khoảng; hết khoảng thì về normal; không ngày kết thúc thì mở
  22 đánh số lại ("... trở thành ...")    -> renumber: mã cũ đóng, mã mới mở với chữ cũ, cạnh `renumbered_to`
  23 danh sách số trần ("Điều 5, 6 và 8") -> đã xử lý ở l2.find_refs / chain_targets
  24 văn bản bị bãi bỏ vì trái luật       -> repeal_one gắn cờ annulled
  25 văn bản được hướng dẫn bị sửa        -> parent_changed: cờ + cạnh, KHÔNG tự đóng văn bản hướng dẫn (Luật 64 Điều 57 khoản 2)
  26 thay cả văn bản cùng tên không có điều hiệu lực -> possible_replacement: cờ + cạnh, không tự đóng (LLM đề xuất ở plan, chưa gọi)
"""
import datetime
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import refs as l2
import l6_versions as l6v
import l6_directives as l6

RE_RETRO = re.compile(r"(?:áp dụng|có hiệu lực)(?: trở lại)?[ ]+từ[ ]+ngày[ ]+(?P<d>\d{1,2}[ ]+tháng[ ]+\d{1,2}[ ]+năm[ ]+\d{4})", re.I)
RE_HARSHER = re.compile(r"trách nhiệm pháp lý (?:mới|nặng hơn)|nặng hơn|hạn chế quyền|tăng mức", re.I)
RE_SUSPEND = re.compile(r"^(?:Tạm ngưng|Đình chỉ)(?:[ ]+(?:hiệu lực|thi hành|việc thi hành))+[ ]+(?P<t>.+?)(?:[ ]+kể từ ngày[ ]+(?P<d1>\d{1,2}[ ]+tháng[ ]+\d{1,2}[ ]+năm[ ]+\d{4})"
                        r"(?:[ ]+đến hết ngày[ ]+(?P<d2>\d{1,2}[ ]+tháng[ ]+\d{1,2}[ ]+năm[ ]+\d{4}))?)?[.;]?$", re.I)
RE_RENUM = re.compile(r"^(?P<old>(?:điểm|khoản|Điều).+?)[ ]+(?:được[ ]+)?(?:đánh số lại(?:[ ]+(?:thành|là))?|trở thành)[ ]+(?P<new>(?:điểm|khoản|Điều).+?)[.;]?$", re.I)
RE_CORRECT = re.compile(r"^Đính chính[ ]+(?P<t>.+?)[ ]+như sau:?$", re.I)
RE_ANNUL = re.compile(r"bị[ ]+(?:hủy bỏ|bãi bỏ|đình chỉ)[^.]*?(?:vì|do)[ ]+trái", re.I)


def _date(s):
    ds = l6.dates_in("ngày " + s) if s else []
    return ds[0] if ds else None


# ---- thao tác trên Store ----

def retroactive(store, doc, eff, applies_from, text, ev):
    """Loại 19: gắn applies_from cho mọi đơn vị của văn bản. Hồi tố đặt trách nhiệm pháp lý mới hoặc nặng hơn thì KHÔNG áp (Luật 64 Điều 55
    khoản 2): gắn cờ retroactive_blocked. -> True nếu đã áp."""
    if applies_from >= eff:
        return False
    if RE_HARSHER.search(text):
        ev.flags["retroactive_blocked"] += 1
        return False
    n = 0
    for k, vs in store.vers.items():
        v = vs[-1]
        if v.source_event == doc.doc_id and v.version == 1:
            v.applies_from = applies_from
            v.flags.append("retroactive")
            n += 1
    ev.flags["retroactive"] += 1
    ev.actions.append(f"hồi tố: {n} đơn vị áp dụng từ {applies_from.isoformat()}, hiệu lực từ {eff.isoformat()}")
    return True


def correct(store, tid, corrected_text, eff, source, directive):
    """Loại 20: đính chính không đổi nội dung pháp lý nên KHÔNG mở phiên bản mới; giữ chữ gốc và chữ đã đính chính, cạnh `corrects`."""
    cur = store.cur(tid)
    if cur is None:
        raise ValueError(f"đính chính mã không tồn tại: {tid}")
    store.corrections.append({"id": tid, "version": cur.version, "text_before": cur.text, "text_after": corrected_text, "source_event": source,
                              "effective": l6v.iso(eff), "directive": directive})
    cur.flags.append("corrected")
    store.add_edge(directive, "corrects", tid, corrected_text[:160], source, eff)


def suspend(store, tid, start, end, source, directive):
    """Loại 21: tạm ngưng từ start; có end thì hết khoảng về hiệu lực với chữ cũ (phiên bản mới, cờ suspension_ended); không có end thì mở."""
    for x in [tid, *store.descendants(tid)]:
        v = store.open(x)
        if v is None or v.state != "normal":
            continue
        text = v.text
        store.new_version(x, start, source, None, None, ["suspended_by_directive"], directive, "suspended", f"tạm ngưng từ {start.isoformat()}")
        if end is not None:
            store.new_version(x, end, source, text, None, ["suspension_ended"], directive)
    store.add_edge(directive, "suspends", tid, "", source, start, valid_from=l6v.iso(start), valid_to=l6v.iso(end))


def renumber(store, old_id, new_id, eff, source, directive):
    """Loại 22: đánh số lại. Mã cũ đóng tại eff, mã mới mở với chữ của mã cũ; cạnh renumbered_to để dẫn chiếu cũ đi theo ánh xạ."""
    cur = store.open(old_id)
    if cur is None:
        raise ValueError(f"đánh số lại mã không có hoặc đã đóng: {old_id}")
    if store.exists(new_id):
        raise ValueError(f"mã mới đã tồn tại: {new_id}")
    store.close_tree(old_id, eff, source, ["renumbered"])
    store.add(l6v.Ver(new_id, 1, cur.type, new_id.split(".")[-1].lstrip("DK"), cur.heading, cur.text, cur.parent, eff, None, None, "normal", None,
                     source, None, None, ["renumbered_from"], directive))
    store.add_edge(old_id, "renumbered_to", new_id, "", source, eff)


def repeal_appendix(store, tdoc, text, eff, source, directive):
    """Loại 16: bãi bỏ một phần phụ lục của văn bản khác: 'Mục 2 Phụ lục I.7' -> <tdoc>.PLI_7.M2 và con cháu. -> số đơn vị đóng."""
    n = 0
    for m in re.finditer(r"(?:Mục[ ]+(?P<m>\d+)[ ]+)?Phụ lục[ ]+(?P<p>[IVX]+(?:\.\d+)?|\d+)", text):
        pid = f"{tdoc}.PL{m['p'].replace('.', '_')}" + (f".M{m['m']}" if m["m"] else "")
        if store.exists(pid):
            n += store.close_tree(pid, eff, source, ["repealed"])
            store.add_edge(directive, "repeals", pid, text[:160], source, eff)
    return n


def mark_parent_changed(store, links, touched_docs, event_doc, eff):
    """Loại 25: văn bản được hướng dẫn bị sửa -> cờ + cạnh parent_changed từ văn bản hướng dẫn; KHÔNG đóng văn bản hướng dẫn."""
    seen = set()
    for l in links:
        if l["p"] in ("details", "based_on") and l["o"].split(".")[0] in touched_docs and l["s"] != event_doc and (l["s"], l["o"].split(".")[0]) not in seen:
            seen.add((l["s"], l["o"].split(".")[0]))
            store.add_edge(l["s"], "parent_changed", l["o"].split(".")[0], "", event_doc, eff, flags=["parent_changed"])
    return sorted(seen)


def possible_replacement(store, docs, new_doc, eff):
    """Loại 26: văn bản cùng loại, cùng tên (bỏ số, năm, dấu ngoặc) với một văn bản trước chưa bị đóng và không có điều hiệu lực nêu rõ ->
    cờ + cạnh possible_replacement, không tự đóng."""
    def key(d):
        return (d.doc_type, re.sub(r"[\d()]+|\s+", " ", d.ten_ngan).strip().casefold())
    out = []
    for d in docs.values():
        if d.doc_id != new_doc.doc_id and not d.is_consolidation and d.ngay_hieu_luc < new_doc.ngay_hieu_luc and key(d) == key(new_doc):
            if any(store.exists(k) and store.cur(k).effective_to is None for k in store.vers if k.startswith(d.doc_id + ".")):
                store.add_edge(new_doc.doc_id, "possible_replacement", d.doc_id, "", new_doc.doc_id, eff, flags=["possible_replacement"])
                out.append(d.doc_id)
    return out


# ---- quét câu ----

def apply_rare(ctx, store, doc, units, eff, ev):
    """Quét đơn vị của văn bản mới nạp tìm các mẫu câu của loại hiếm. Chỉ ghi khi khớp mẫu."""
    for uid, u in units.items():
        text = (u.get("text") or "").replace("\n", " ")
        if u["type"] not in ("dieu", "khoan", "diem") or not text:
            continue
        if re.match(rf"^{l2.KINDS}[ ]+này", text, re.I):  # chỉ câu tự nói về hiệu lực / áp dụng của chính văn bản
            earlier = [d for d in (_date(m["d"]) for m in RE_RETRO.finditer(text)) if d and d < eff]
            if earlier:
                retroactive(store, doc, eff, min(earlier), text, ev)
        m = RE_SUSPEND.match(text)
        if m and _date(m["d1"]):
            ids, errs = l6.targets_of(ctx, units, uid, m["t"], doc.doc_id)
            last_day = _date(m["d2"])  # "đến hết ngày X": hiệu lực trở lại từ ngày X + 1 (khoảng nửa mở, cùng quy ước với NQ_66-16)
            resume = last_day + datetime.timedelta(days=1) if last_day else None
            for t in ids:
                if store.open(t):
                    suspend(store, t, _date(m["d1"]), resume, doc.doc_id, uid)
                    ev.actions.append(f"{uid} suspends {t}")
        m = RE_RENUM.match(text)
        if m:
            old, e1 = l6.targets_of(ctx, units, uid, m["old"], doc.doc_id)
            new, e2 = l6.targets_of(ctx, units, uid, m["new"], doc.doc_id)
            if len(old) == 1 and len(new) == 1 and not e1 and not e2 and store.open(old[0]):
                renumber(store, old[0], new[0], eff, doc.doc_id, uid)
                ev.actions.append(f"{uid} renumbered_to {new[0]}")
    for d in possible_replacement(store, ctx.docs, doc, eff):
        ev.flags["possible_replacement"] += 1
        ev.notes.append(f"{doc.doc_id} cùng loại và tên với {d} nhưng không có điều hiệu lực nêu rõ: chờ đề xuất (LLM) / quyết định")


def try_directive(ctx, store, doc, uid, units, first, payload, tail, res, eff, ev):
    """Chỉ thị đầu động từ thuộc loại hiếm: đính chính (20), bãi bỏ phần phụ lục (16). -> True nếu đã xử lý."""
    m = RE_CORRECT.match(first)
    if m and payload:
        tdoc = res[1] if res and res[0] == "doc" else doc.doc_id
        ids, errs = l6.targets_of(ctx, units, uid, m["t"], tdoc)
        roots = l6.parse_payload(payload[0]["lines"], l6.Node("khoan", ids[0].split(".")[-1][1:]) if len(ids) == 1 else None)
        if errs or not ids or not roots:
            raise ValueError("đính chính không đọc được")
        correct(store, ids[0], roots[0].text, eff, doc.doc_id, uid)
        ev.flags["correction"] += 1
        return True
    if re.match(r"^(?:Bãi bỏ|Bỏ)\b", first) and re.search(r"Phụ lục", first):
        tdoc = res[1] if res and res[0] == "doc" else None
        if tdoc:
            n = repeal_appendix(store, tdoc, first, eff, doc.doc_id, uid)
            ev.actions.append(f"{uid}: bãi bỏ phần phụ lục, đóng {n} đơn vị")
            return n > 0
    return False
