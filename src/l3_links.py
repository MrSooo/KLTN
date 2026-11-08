"""L3: điều khoản giao chi tiết của luật và cạnh based_on / details của văn bản dưới luật.

Chạy: python -I src/l3_links.py            (cả kho; cần a1, a2)
Đầu ra (data/processed/l3/):
  delegation_clauses.jsonl  điều khoản của BLLĐ giao cấp dưới quy định chi tiết, 5 dạng A-E của plan
                            {clause_id, unit_id, pattern, delegate, phrase, filled_by (văn bản dưới luật đã nối `details`, theo ngày hiệu lực)}
  l3_links.jsonl            cạnh based_on / details: {s (doc_id), p, o (mã đơn vị hoặc doc_id), how, evidence, flags}
  l3_pending.jsonl          based_on / details trỏ tới văn bản chưa có trong KB
Báo cáo: docs/bao_cao_chay/l3/l3_report.txt (số theo dạng, mốc cổng, ca chưa nối).

  Dạng A "Chính phủ / Bộ trưởng ... quy định ..." (gồm C "do Chính phủ quy định"); B "theo quy định của Chính phủ / Bộ trưởng";
  D "Bộ trưởng ... ban hành" (danh mục, chương trình ... do Bộ trưởng ban hành); E "Thủ tướng Chính phủ quyết định". Số đếm là regex thô: ca không phải giao chi tiết
  ghi ở báo cáo, không tự lọc.
  based_on: dòng "Căn cứ ..." của văn bản; cụm điều/khoản kèm văn bản thành cạnh tới đơn vị, tên văn bản thành cạnh tới văn bản.
  details: Điều 1 (Phạm vi điều chỉnh) nêu điều, khoản được quy định chi tiết; văn bản đích lấy từ cụm hoặc từ câu dẫn
    ("... sau đây của Bộ luật Lao động:"). Không nêu số Điều (ND_74) thì đề xuất bằng từ khoá: cụm danh từ chính của phạm vi phải nằm
    trong tiêu đề hoặc chữ của đơn vị luật đích. Cạnh đề xuất mang cờ keyword_proposed + llm_check_pending: lượt LLM kiểm độc lập
    (plan) chưa chạy nên chưa phải cạnh đã kiểm.
"""
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import a1_parse as a1
import a2_edges as a2
import corpus

L3_DIR_NAME = "l3"

DELEG_PATTERNS = [
    ("A", re.compile(r"(?<!\w)(?:Chính phủ|Bộ trưởng(?:[ ]+[^\W\d_]+){0,10}?|Thủ tướng Chính phủ)[ ]+quy[ ]+định(?![ ]+tại)")),
    ("B", re.compile(r"theo[ ]+quy[ ]+định[ ]+của[ ]+(?:Chính phủ|Bộ trưởng|Thủ tướng Chính phủ)")),
    ("D", re.compile(r"Bộ[ ]+trưởng[^.;:]{0,100}?ban[ ]+hành", re.I)),
    ("E", re.compile(r"Thủ[ ]+tướng[ ]+Chính[ ]+phủ[ ]+quyết[ ]+định")),
]
DO_RE = re.compile(r"do[ ]+$")  # "do Chính phủ quy định": dạng C, nằm trong A


def delegate_of(phrase):
    if "Thủ tướng" in phrase:
        return "Thủ tướng"
    return "Bộ trưởng" if "Bộ trưởng" in phrase else "Chính phủ"


def find_delegation(units, doc_id):
    """Các điều khoản giao chi tiết trong văn bản gốc, theo thứ tự đơn vị rồi vị trí trong text."""
    clauses, counter = [], collections.Counter()
    for uid, u in units.items():
        if u["type"] not in ("dieu", "khoan", "diem") or not u.get("text"):
            continue
        text = u["text"]
        for pattern, rx in DELEG_PATTERNS:
            for m in rx.finditer(text):
                counter[uid] += 1
                short = uid.split(".", 1)[1].replace(".", "_")
                is_c = pattern == "A" and DO_RE.search(text[:m.start()]) is not None
                clauses.append({"clause_id": f"DC_{short}_{counter[uid]}", "unit_id": uid, "pattern": pattern,
                                "subpattern": "C" if is_c else None, "delegate": delegate_of(m[0]), "phrase": m[0],
                                "context": text[max(0, m.start() - 40):m.end() + 60], "filled_by": []})
    return clauses


# ---- based_on / details ----

def subtree(units, root):
    return [(k, v) for k, v in units.items() if k == root or k.startswith(root + ".")]


def lead_tail(units_in_d1):
    """Đuôi văn bản đầu tiên kiểu 'của Bộ luật Lao động' trong Điều 1, bỏ 'X này' (chính văn bản)."""
    for _, u in units_in_d1:
        text = u.get("text") or ""
        for m in re.finditer(r"[ ]+của(?=[ ]+" + a2.KINDS + r")", text):
            t = a2.parse_tail(text, m.start())
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
        for ref in a2.find_refs(doc.doc_id, g):
            r = a2.resolve_ref(doc, doc.doc_id, {}, ref, all_units, resolver, available)
            if r.pending:
                pending.append({**r.pending, "edge": "based_on", "source": doc.doc_id})
            for t in r.targets:
                if t not in seen:
                    seen.add(t)
                    links.append({"s": doc.doc_id, "p": "based_on", "o": t, "how": "regex", "evidence": g, "flags": []})
        # tên / số hiệu văn bản trong dòng căn cứ thành cạnh văn bản -> văn bản
        for number in re.findall(a2.NUMBER_RE, g):
            number = a2.norm_number(number)
            target = resolver.by_number.get(number)
            if target and target != doc.doc_id and target not in seen:
                seen.add(target)
                links.append({"s": doc.doc_id, "p": "based_on", "o": target, "how": "regex", "evidence": g, "flags": []})
            elif not target:
                pending.append({"source": doc.doc_id, "edge": "based_on", "target_number": number, "target_name": None,
                                "target_units": [], "text": g})
        if re.match(r"Căn cứ Bộ luật Lao động", g) and not re.search(a2.NUMBER_RE, g):
            year = resolver.blld_year(doc)
            if year == 2019 and corpus.BASE_DOC_ID not in seen and doc.doc_id != corpus.BASE_DOC_ID:
                seen.add(corpus.BASE_DOC_ID)
                links.append({"s": doc.doc_id, "p": "based_on", "o": corpus.BASE_DOC_ID, "how": "regex", "evidence": g, "flags": []})
            elif year == 2012:
                pending.append({"source": doc.doc_id, "edge": "based_on", "target_number": a2.BLLD_2012, "target_name": a2.BLLD_NAME,
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
        for ref in a2.find_refs(uid, text):
            if ref.tail is None and tail is not None:
                ref = ref._replace(tail=tail)
            elif ref.tail is None:
                continue
            r = a2.resolve_ref(doc, uid, units, ref, all_units, resolver, available)
            tdocs = {t.split(".")[0] for t in r.targets}
            for t in r.targets:
                if t not in seen and t.split(".")[0] != doc.doc_id:
                    seen.add(t)
                    links.append({"s": doc.doc_id, "p": "details", "o": t, "how": "regex", "evidence": ref.phrase, "via": uid, "flags": []})
    return links, None if links else "Điều 1 không nêu điều, khoản đích"


def propose_by_keyword(doc, units, law_doc, law_units, clauses):
    """Đề xuất `details` bằng từ khoá cho văn bản không nêu số Điều. Cờ keyword_proposed + llm_check_pending."""
    d1 = subtree(units, f"{doc.doc_id}.D1")
    text = " ".join((u.get("text") or "") for _, u in d1)
    phrases = key_phrases(text)
    out = []
    for uid, hp, has_clause in keyword_candidates(phrases, law_units, clauses)[:1]:  # chỉ lấy ứng viên tốt nhất
        out.append({"s": doc.doc_id, "p": "details", "o": uid, "how": "keyword", "evidence": f"Điều 1: {text[:160]}",
                    "flags": ["keyword_proposed", "llm_check_pending"],
                    "check": {"keyword": hp, "in_heading": True, "has_delegation_clause": has_clause, "second_llm": "not_run"}})
    return out, phrases


def main():
    docs, all_units, resolver, available = a2.load_context()
    headers = a2.load_headers()
    base = corpus.BASE_DOC_ID
    law_units = all_units[base]
    clauses = find_delegation(law_units, base)
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
            if prop:
                d += prop
                why = None
                notes.append(f"{doc.doc_id}: Điều 1 không nêu số Điều của BLLĐ; đề xuất bằng từ khoá {[p['check']['keyword'] for p in prop]} -> {[p['o'] for p in prop]}")
        links += b + d
        pending += p
        if why:
            notes.append(f"{doc.doc_id}: không có details ({why})")
    # filled_by: văn bản đã nối details tới điều khoản (hoặc Điều chứa nó), theo ngày hiệu lực
    eff = {d.doc_id: d.ngay_hieu_luc for d in docs.values()}
    for c in clauses:
        dieu = ".".join(c["unit_id"].split(".")[:2])
        by = {l["s"] for l in links if l["p"] == "details" and (l["o"] == c["unit_id"] or c["unit_id"].startswith(l["o"] + ".")
                                                                  or l["o"].startswith(dieu + "."))}
        c["filled_by"] = sorted(by, key=lambda d: eff[d])
    out = corpus.out_dir(L3_DIR_NAME)
    a1.write_jsonl(out / "delegation_clauses.jsonl", clauses)
    a1.write_jsonl(out / "l3_links.jsonl", links)
    a1.write_jsonl(out / "l3_pending.jsonl", pending)

    per_pat = collections.Counter(c["pattern"] for c in clauses)
    dieu_pat = {p: len({c["unit_id"].split(".")[1] for c in clauses if c["pattern"] == p}) for p in per_pat}
    units_with = {c["unit_id"] for c in clauses}
    have = lambda u: u in units_with or any(x.startswith(u + ".") or u.startswith(x + ".") for x in units_with)
    milestones = [("BLLD.D91.K4 (dạng A)", have("BLLD_45-2019.D91.K4")), ("D154.K1/K2/K9 (dạng B)", all(have(f"BLLD_45-2019.D154.K{k}") for k in (1, 2, 9))),
                  ("D142.K1 (dạng D)", have("BLLD_45-2019.D142.K1")), ("D112 (dạng E)", have("BLLD_45-2019.D112"))]
    det = lambda s: {l["o"] for l in links if l["s"] == s and l["p"] == "details"}
    detail_marks = [("ND_152 details D154.K1,K2,K9, D157, D150.K3",
                     all(any(o == f"BLLD_45-2019.{x}" or o.startswith(f"BLLD_45-2019.{x}.") for o in det("ND_152-2020"))
                         for x in ("D154.K1", "D154.K2", "D154.K9", "D157", "D150.K3"))),
                    ("TT_10 details D21.K1-3, D73.K4, D142.K1", all(f"BLLD_45-2019.{x}" in det("TT_10-2020-BLDTBXH") for x in ("D21.K1", "D21.K2", "D21.K3", "D73.K4", "D142.K1"))),
                    ("ND_135 details D169", any(o.startswith("BLLD_45-2019.D169") for o in det("ND_135-2020"))),
                    ("TT_18 based_on ND_145.D68.K2", any(l["p"] == "based_on" and l["o"] == "ND_145-2020.D68.K2" for l in links)),
                    ("ND_74 details D91 (keyword_proposed, chưa qua LLM kiểm)", "BLLD_45-2019.D91" in det("ND_74-2024"))]
    no_based = [d.doc_id for d in docs.values() if d.doc_id != base and not d.is_consolidation
                and not any(l["s"] == d.doc_id and l["p"] == "based_on" for l in links)]
    report = ["L3 báo cáo", f"điều khoản giao chi tiết: {len(clauses)} cụm ở {len(units_with)} đơn vị; theo dạng {dict(per_pat)}; số Điều theo dạng {dieu_pat}",
              f"(plan 8/11: A 39 cụm/37 Điều, B 10/8, C 2 trong A, D 5 Điều, E 1 Điều; tổng ~55 cụm/~50 Điều; đây là regex thô, chưa lọc ca không phải giao chi tiết)",
              f"cạnh based_on: {sum(1 for l in links if l['p'] == 'based_on')}  details: {sum(1 for l in links if l['p'] == 'details')}  chờ đích: {len(pending)}",
              "mốc cổng delegation_clauses:"] + [f"  {'đạt' if ok else 'KHÔNG đạt'}: {name}" for name, ok in milestones] \
        + ["mốc cổng details / based_on:"] + [f"  {'đạt' if ok else 'KHÔNG đạt'}: {name}" for name, ok in detail_marks] \
        + [f"văn bản không có based_on (header mất hoặc không nêu): {no_based}", "ghi chú:"] + [f"  {n}" for n in notes]
    rp = corpus.report_dir(L3_DIR_NAME) / "l3_report.txt"
    rp.parent.mkdir(parents=True, exist_ok=True)
    rp.write_text("\n".join(report) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(report))
    if not all(ok for _, ok in milestones + detail_marks[:-1]):
        raise SystemExit(1)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()
