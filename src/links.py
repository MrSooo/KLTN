"""Bước 2.2: nối văn bản dưới luật với luật gốc: cạnh based_on (dòng "Căn cứ ..."), cạnh details (Điều 1 nêu điều, khoản được quy định chi tiết), và filled_by cho điều khoản giao.

Chạy: python -I src/links.py [--llm off|replay|live]    (cả kho; cần bước parse, refs và delegation)
Đầu ra (data/processed/l3/):
  l3_links.jsonl           cạnh based_on / details: {s (doc_id), p, o (mã đơn vị hoặc doc_id), evidence, how, flags}
  l3_pending.jsonl         based_on / details trỏ tới văn bản chưa có trong KB
  delegation_filled.jsonl  {clause_id, filled_by}: văn bản dưới luật đã nối details tới điều khoản giao đó, theo ngày hiệu lực (rỗng nếu chưa có)
Báo cáo: docs/bao_cao_chay/l3/l3_report.txt (mốc cổng details / based_on, ca chưa nối).

  based_on: dòng "Căn cứ ..." của văn bản; cụm điều/khoản kèm văn bản thành cạnh tới đơn vị, tên văn bản thành cạnh tới văn bản.
  details: Điều 1 (Phạm vi điều chỉnh) nêu điều, khoản được quy định chi tiết; văn bản đích lấy từ cụm hoặc từ câu dẫn
    ("... sau đây của Bộ luật Lao động:"). Không nêu số Điều (ND_74) thì đề xuất bằng từ khoá: cụm danh từ chính của phạm vi phải nằm
    trong tiêu đề hoặc chữ của đơn vị luật đích; cạnh chỉ do từ khoá mang cờ keyword_proposed + llm_check_pending. Khi chạy --llm replay/live,
    hai model độc lập kiểm (decide_llm): giữ khi cả hai model và từ khoá đồng ý, ngược lại gắn cờ isolated (giữ lại nhưng không dùng làm căn cứ).
  Điều khoản giao (delegation_clauses.jsonl) do bước 1.3 (delegation.py) tạo từ chỉ BLLĐ; ở đây chỉ dùng các ca chắc (flags rỗng) làm danh mục đối chiếu.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import parse as l1
import refs as l2
import corpus
import llm_client

L3_DIR_NAME = "l3"
TASK, PROMPT_VERSION, MAX_TARGETS = "l3_details", "l3-1", 5

SYSTEM = """Bạn đọc một văn bản dưới luật (nghị định, thông tư) của pháp luật lao động Việt Nam và xác định nó QUY ĐỊNH CHI TIẾT điều khoản nào của Bộ luật Lao động 2019.
Bạn được cho: chữ Điều 1 (phạm vi điều chỉnh), tiêu đề các Điều của văn bản, và DANH SÁCH điều khoản của Bộ luật Lao động có giao Chính phủ / Bộ trưởng quy định chi tiết.
Chỉ chọn mã unit_id nằm TRONG danh sách đó, tối đa 5 mã, mỗi mã kèm lý do ngắn. Văn bản không quy định chi tiết điều khoản nào trong danh sách (ví dụ chỉ xử phạt vi phạm)
thì trả mảng rỗng. Không đoán ngoài danh sách. Trả về JSON đúng lược đồ."""

SCHEMA = {"type": "object", "additionalProperties": False, "required": ["targets"],
          "properties": {"targets": {"type": "array", "items": {
              "type": "object", "additionalProperties": False, "required": ["unit_id", "ly_do"],
              "properties": {"unit_id": {"type": "string"}, "ly_do": {"type": "string"}}}}}}


# ---- based_on / details ----

def subtree(units, root):
    return [(k, v) for k, v in units.items() if k == root or k.startswith(root + ".")]


def lead_tail(units_in_d1):
    """Đuôi văn bản đầu tiên kiểu 'của Bộ luật Lao động' trong Điều 1, bỏ 'X này' (chính văn bản)."""
    for _, u in units_in_d1:
        text = u.get("text") or ""
        for m in re.finditer(r"[ ]+của(?=[ ]+" + l2.KINDS + r")", text):
            t = l2.parse_tail(text, m.start())
            if t is not None and not t.self_ref:
                return t
    return None


def key_phrases(d1_text):
    """Cụm danh từ chính của phạm vi điều chỉnh: sau 'quy định' đến trước 'áp dụng' / 'đối với' / dấu câu, tách ở ' và '."""
    m = re.search(r"quy[ ]+định(?:[ ]+về)?[ ]+(.+?)(?:[ ]+áp[ ]+dụng|[ ]+đối[ ]+với|[.;:]|$)", d1_text)
    if not m:
        return []
    return [p.strip().casefold() for p in re.split(r"[ ]+và[ ]+", m[1]) if p.strip()]


def head_phrase(phrase):
    """Bỏ từ cuối của cụm ('mức lương tối thiểu tháng' -> 'mức lương tối thiểu') để khớp tiêu đề điều của luật."""
    words = phrase.split()
    return " ".join(words[:-1]) if len(words) > 3 else phrase


def keyword_candidates(phrases, law_units, clauses):
    """Đơn vị luật có tiêu đề (Điều) chứa cụm danh từ chính, ưu tiên điều có điều khoản giao chi tiết. Trả [(unit_id, cụm khớp)]."""
    clause_dieu = {c["unit_id"].split(".")[1] for c in clauses}
    found = []
    for p in phrases:
        hp = head_phrase(p)
        for uid, u in law_units.items():
            if u["type"] == "dieu" and hp in (u.get("heading") or "").casefold():
                found.append((uid, hp, uid.split(".")[1] in clause_dieu))
    return sorted(set(found), key=lambda t: (not t[2], t[0]))


def based_on_links(doc, units, header, all_units, resolver, available):
    """Cạnh based_on từ dòng 'Căn cứ ...'. Trả (links, pending)."""
    links, pending, seen = [], [], set()
    for g in header["grounds"]:
        for ref in l2.find_refs(doc.doc_id, g):
            r = l2.resolve_ref(doc, doc.doc_id, {}, ref, all_units, resolver, available)
            if r.pending:
                pending.append({**r.pending, "edge": "based_on", "source": doc.doc_id})
            for t in r.targets:
                if t not in seen:
                    seen.add(t)
                    links.append({"s": doc.doc_id, "p": "based_on", "o": t, "how": "regex", "evidence": g, "flags": []})
        # tên / số hiệu văn bản trong dòng căn cứ thành cạnh văn bản -> văn bản
        for number in re.findall(l2.NUMBER_RE, g):
            number = l2.norm_number(number)
            target = resolver.by_number.get(number)
            if target and target != doc.doc_id and target not in seen:
                seen.add(target)
                links.append({"s": doc.doc_id, "p": "based_on", "o": target, "how": "regex", "evidence": g, "flags": []})
            elif not target:
                pending.append({"source": doc.doc_id, "edge": "based_on", "target_number": number, "target_name": None,
                                "target_units": [], "text": g})
        if re.match(r"Căn cứ Bộ luật Lao động", g) and not re.search(l2.NUMBER_RE, g):
            year = resolver.blld_year(doc)
            if year == 2019 and corpus.BASE_DOC_ID not in seen and doc.doc_id != corpus.BASE_DOC_ID:
                seen.add(corpus.BASE_DOC_ID)
                links.append({"s": doc.doc_id, "p": "based_on", "o": corpus.BASE_DOC_ID, "how": "regex", "evidence": g, "flags": []})
            elif year == 2012:
                pending.append({"source": doc.doc_id, "edge": "based_on", "target_number": l2.BLLD_2012, "target_name": l2.BLLD_NAME,
                                "target_units": [], "text": g})
    return links, pending


def details_links(doc, units, all_units, resolver, available):
    """Cạnh details từ Điều 1. Trả (links, ghi chú lý do không có)."""
    d1 = subtree(units, f"{doc.doc_id}.D1")
    if not d1:
        return [], "không có Điều 1"
    tail = lead_tail(d1)
    links, seen = [], set()
    for uid, u in d1:
        text = u.get("text") or ""
        for ref in l2.find_refs(uid, text):
            if ref.tail is None and tail is not None:
                ref = ref._replace(tail=tail)
            elif ref.tail is None:
                continue
            r = l2.resolve_ref(doc, uid, units, ref, all_units, resolver, available)
            tdocs = {t.split(".")[0] for t in r.targets}
            for t in r.targets:
                if t not in seen and t.split(".")[0] != doc.doc_id:
                    seen.add(t)
                    links.append({"s": doc.doc_id, "p": "details", "o": t, "how": "regex", "evidence": ref.phrase, "flags": []})
    return links, None if links else "Điều 1 không nêu điều, khoản đích"


def propose_by_keyword(doc, units, law_doc, law_units, clauses):
    """Đề xuất `details` bằng từ khoá cho văn bản không nêu số Điều. Cờ keyword_proposed + llm_check_pending."""
    d1 = subtree(units, f"{doc.doc_id}.D1")
    text = " ".join((u.get("text") or "") for _, u in d1)
    phrases = key_phrases(text)
    out = []
    for uid, *_ in keyword_candidates(phrases, law_units, clauses)[:1]:  # chỉ lấy ứng viên tốt nhất
        out.append({"s": doc.doc_id, "p": "details", "o": uid, "how": "keyword", "evidence": f"Điều 1: {text[:160]}",
                    "flags": ["keyword_proposed", "llm_check_pending"]})
    return out, phrases


def dieu_of(uid):
    return ".".join(uid.split(".")[:2])


def subtree_text(units, root):
    return " ".join((u.get("heading") or "") + " " + (u.get("text") or "") for k, u in units.items() if k == root or k.startswith(root + "."))


def llm_user_message(doc, units, clauses, law_units):
    """Đầu vào cho LLM: chữ Điều 1, tiêu đề các Điều của văn bản, danh sách điều khoản giao chi tiết (mã, tiêu đề Điều, cụm). Không có gợi ý đích nào."""
    d1 = " ".join((u.get("text") or "") for _, u in subtree(units, f"{doc.doc_id}.D1"))[:900]
    headings = [u.get("heading") for k, u in units.items() if u["type"] == "dieu" and u.get("heading")][:40]
    catalog = [{"unit_id": c["unit_id"], "tieu_de_dieu": law_units[dieu_of(c["unit_id"])].get("heading") or "", "cum": c["phrase"]} for c in clauses]
    return json.dumps({"van_ban": doc.doc_id, "dieu_1": d1, "tieu_de_cac_dieu": headings, "danh_sach_dieu_khoan_giao_chi_tiet": catalog},
                      ensure_ascii=False, indent=0)


def validate_targets(output, allowed):
    """Kiểm đầu ra: đúng lược đồ, mọi unit_id nằm trong danh sách được cho, không quá MAX_TARGETS. Sai thì ValueError. -> list unit_id (không trùng)."""
    targets = output.get("targets") if isinstance(output, dict) else None
    if not isinstance(targets, list) or len(targets) > MAX_TARGETS:
        raise ValueError("thiếu 'targets' hoặc quá nhiều đích")
    out = []
    for t in targets:
        if not isinstance(t, dict) or t.get("unit_id") not in allowed:
            raise ValueError(f"đích ngoài danh sách được cho: {t!r}")
        if t["unit_id"] not in out:
            out.append(t["unit_id"])
    return out


def llm_propose(client, doc, units, clauses, law_units):
    """Hai lượt ĐỘC LẬP (model chính rồi model kiểm, cùng đầu vào, lượt sau không thấy lượt trước). -> dict {chinh, kiem: list unit_id | None, note: str}.
    None nghĩa là lượt đó chưa có kết quả (thiếu cache khi replay, hết hạn mức, hoặc đầu ra bị loại); note nói rõ vì sao."""
    user = llm_user_message(doc, units, clauses, law_units)
    allowed = {c["unit_id"] for c in clauses}
    res, notes = {}, []
    for role in llm_client.ROLES:
        try:
            rec = client.ask(TASK, PROMPT_VERSION, SYSTEM, user, SCHEMA, role=role, validate=lambda out: validate_targets(out, allowed), label=doc.doc_id)
            res[role] = validate_targets(rec["output"], allowed)
        except llm_client.CacheMiss:
            res[role] = None
            notes.append(f"{role}: chưa có cache")
        except llm_client.QuotaReached as e:
            res[role] = None
            notes.append(f"{role}: {e}")
        except ValueError as e:
            res[role] = None
            notes.append(f"{role}: đầu ra bị loại ({e})")
    return {**res, "note": "; ".join(notes)}


def decide_llm(doc, units, law_units, keyword_edges, llm):
    """Quyết định cạnh details từ đề xuất LLM + từ khoá (plan L3). Một Điều đích được GIỮ khi: model chính đề xuất, model kiểm đề xuất độc lập (cùng Điều),
    và kiểm từ khoá đạt (cụm danh từ chính của phạm vi điều chỉnh nằm trong tiêu đề / chữ Điều đích). Một trong ba trượt thì cạnh vẫn ghi nhưng cờ isolated
    (không dùng khi hỏi đáp). Đề xuất chỉ do từ khoá (model chính không nêu) không bao giờ được giữ."""
    d1 = " ".join((u.get("text") or "") for _, u in subtree(units, f"{doc.doc_id}.D1"))
    heads = [head_phrase(p) for p in key_phrases(d1)]
    first = {dieu_of(t) for t in (llm["chinh"] or [])}
    second = {dieu_of(t) for t in (llm["kiem"] or [])}
    kw_targets = {e["o"] for e in keyword_edges}
    edges = []
    for dieu in sorted(first | kw_targets):
        body = subtree_text(law_units, dieu).casefold()
        hit = next((h for h in heads if h and h in body), None)
        ok = dieu in first and dieu in second and hit is not None
        flags = ["llm_proposed"] if dieu in first else ["keyword_proposed"]
        if not ok:
            flags.append("isolated")
        edges.append({"s": doc.doc_id, "p": "details", "o": dieu, "how": "llm" if dieu in first else "keyword", "evidence": f"Điều 1: {d1[:160]}", "flags": flags})
    return edges


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--llm", choices=("off", "replay", "live"), default="off", help="off: chỉ regex và từ khoá (mặc định); replay: đọc cache; live: gọi API khi thiếu cache")
    args = ap.parse_args(argv)
    if args.llm == "live" and not llm_client.key_is_set():
        raise SystemExit("--llm live nhưng không thấy GEMINI_API_KEY trong môi trường của process này (đặt khoá MỘT LẦN bằng `setx GEMINI_API_KEY` ở terminal riêng rồi mở terminal mới; xem đầu src/run_all.py)")
    client = llm_client.Client(args.llm, log=llm_client.stderr_log) if args.llm != "off" else None
    docs, all_units, resolver, available = l2.load_context()
    headers = l2.load_headers()
    base = corpus.BASE_DOC_ID
    law_units = all_units[base]
    out = corpus.out_dir(L3_DIR_NAME)
    if not (out / "delegation_clauses.jsonl").exists():
        raise SystemExit("chưa có delegation_clauses.jsonl; chạy src/delegation.py trước")
    all_clauses = l1.read_jsonl(out / "delegation_clauses.jsonl")
    clauses = [c for c in all_clauses if not c["flags"]]  # danh mục đối chiếu chỉ gồm điều khoản giao CHẮC (tầng chặt); ca cờ loose chưa dùng để nối
    links, pending = [], []
    notes = []
    for doc in docs.values():
        if doc.doc_id in (base,) or doc.is_consolidation:
            continue
        units, header = all_units[doc.doc_id], headers[doc.doc_id]
        b, p = based_on_links(doc, units, header, all_units, resolver, available)
        d, why = details_links(doc, units, all_units, resolver, available)
        if not any(l["o"].startswith(base + ".") for l in d) and doc.level > 1 and any(l["o"] == base for l in b):
            prop, phrases = propose_by_keyword(doc, units, docs[base], law_units, clauses)
            llm = None
            if client is not None:
                try:
                    llm = llm_propose(client, doc, units, clauses, law_units)
                except llm_client.LLMError as e:
                    raise SystemExit(f"LỖI LLM ở {doc.doc_id}: {e}\n(các lượt đã gọi xong nằm trong data/llm_cache/{TASK}/, chạy lại sẽ đọc từ cache)")
            if llm is not None and (llm["chinh"] is not None or llm["kiem"] is not None):
                llm_edges = decide_llm(doc, units, law_units, prop, llm)
                d += llm_edges
                why = None if llm_edges else "LLM không đề xuất điều khoản nào (và từ khoá không có ứng viên)"
                kept = [e["o"] for e in llm_edges if "isolated" not in e["flags"]]
                notes.append(f"{doc.doc_id}: LLM chinh={[dieu_of(t) for t in llm['chinh'] or []]} kiem={[dieu_of(t) for t in llm['kiem'] or []]}; "
                             f"giữ {kept}, cô lập {[e['o'] for e in llm_edges if 'isolated' in e['flags']]}" + (f"; {llm['note']}" if llm["note"] else ""))
            elif prop:
                d += prop
                why = None
                notes.append(f"{doc.doc_id}: Điều 1 không nêu số Điều của BLLĐ; đề xuất bằng từ khoá -> {[e['o'] for e in prop]}"
                             + (f" (LLM: {llm['note']})" if llm and llm["note"] else ""))
        links += b + d
        pending += p
        if why:
            notes.append(f"{doc.doc_id}: không có details ({why})")
    # filled_by: văn bản đã nối details tới điều khoản (hoặc Điều chứa nó), theo ngày hiệu lực. Tính cho mọi điều khoản giao, kể cả ca cờ loose.
    eff = {d.doc_id: d.ngay_hieu_luc for d in docs.values()}
    filled = []
    for c in all_clauses:
        dieu = ".".join(c["unit_id"].split(".")[:2])
        by = {l["s"] for l in links if l["p"] == "details" and (l["o"] == c["unit_id"] or c["unit_id"].startswith(l["o"] + ".")
                                                                  or l["o"].startswith(dieu + "."))}
        filled.append({"clause_id": c["clause_id"], "filled_by": sorted(by, key=lambda d: eff[d])})
    l1.write_jsonl(out / "delegation_filled.jsonl", filled)
    l1.write_jsonl(out / "l3_links.jsonl", links)
    l1.write_jsonl(out / "l3_pending.jsonl", pending)

    det = lambda s: {l["o"] for l in links if l["s"] == s and l["p"] == "details"}
    nd74 = [l for l in links if l["s"] == "ND_74-2024" and l["p"] == "details" and l["o"] == "BLLD_45-2019.D91"]
    nd74_status = ("không có cạnh" if not nd74 else "CÔ LẬP: không qua đủ ba điều kiện" if "isolated" in nd74[0]["flags"] else
                   "GIỮ: hai model và từ khoá đồng ý" if "llm_proposed" in nd74[0]["flags"] else "mới ở mức từ khoá, chưa qua LLM kiểm")
    detail_marks = [("ND_152 details D154.K1,K2,K9, D157, D150.K3",
                     all(any(o == f"BLLD_45-2019.{x}" or o.startswith(f"BLLD_45-2019.{x}.") for o in det("ND_152-2020"))
                         for x in ("D154.K1", "D154.K2", "D154.K9", "D157", "D150.K3"))),
                    ("TT_10 details D21.K1-3, D73.K4, D142.K1", all(f"BLLD_45-2019.{x}" in det("TT_10-2020-BLDTBXH") for x in ("D21.K1", "D21.K2", "D21.K3", "D73.K4", "D142.K1"))),
                    ("ND_135 details D169", any(o.startswith("BLLD_45-2019.D169") for o in det("ND_135-2020"))),
                    ("TT_18 based_on ND_145.D68.K2", any(l["p"] == "based_on" and l["o"] == "ND_145-2020.D68.K2" for l in links)),
                    (f"ND_74 details D91 ({nd74_status})", "BLLD_45-2019.D91" in det("ND_74-2024"))]
    no_based = [d.doc_id for d in docs.values() if d.doc_id != base and not d.is_consolidation
                and not any(l["s"] == d.doc_id and l["p"] == "based_on" for l in links)]
    llm_line = ("LLM: tắt (--llm off); cạnh đề xuất bằng từ khoá mang cờ llm_check_pending" if client is None else
                f"LLM: --llm {args.llm}; gọi API lần này: {client.calls}; đọc từ cache: {client.hits}; hôm nay đã dùng "
                f"{{chinh: {client.used_today('chinh')}, kiem: {client.used_today('kiem')}}}")
    report = ["L3 báo cáo (bước 2.2: nối văn bản)", llm_line,
              f"cạnh based_on: {sum(1 for l in links if l['p'] == 'based_on')}  details: {sum(1 for l in links if l['p'] == 'details')}  chờ đích: {len(pending)}",
              f"điều khoản giao dùng làm danh mục đối chiếu: {len(clauses)} (bỏ {len(all_clauses) - len(clauses)} ca cờ loose); đã có văn bản lấp: {sum(1 for f in filled if f['filled_by'])}",
              "mốc cổng details / based_on:"] + [f"  {'đạt' if ok else 'KHÔNG đạt'}: {name}" for name, ok in detail_marks] \
        + [f"văn bản không có based_on (header mất hoặc không nêu): {no_based}", "ghi chú:"] + [f"  {n}" for n in notes]
    rp = corpus.report_dir(L3_DIR_NAME) / "l3_report.txt"
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text("\n".join(report) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(report))
    if not all(ok for _, ok in detail_marks[:-1]):
        raise SystemExit(1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()
