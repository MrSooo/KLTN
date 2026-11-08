"""Test A4 / L6: chuẩn hoá chữ, kho phiên bản, payload, thay cụm từ, và cổng dev trên chuỗi 17 văn bản."""
import datetime
import hashlib
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import _harness  # noqa: E402
import a4_versions as a4  # noqa: E402
import corpus  # noqa: E402
import l6_directives as l6  # noqa: E402

D = datetime.date
ROOT = Path(__file__).resolve().parent.parent
_CHAIN = {}


def chain():
    """Chạy chuỗi một lần trong tiến trình test (không ghi file)."""
    if not _CHAIN:
        docs = corpus.load_manifest()
        ctx = l6.Context.build(docs)
        store = a4.Store()
        base = docs[corpus.BASE_DOC_ID]
        a4.add_doc_units(store, base, ctx.units[base.doc_id], base.ngay_hieu_luc)
        events = []
        as_of = base.ngay_hieu_luc
        for doc in a4.order_docs(docs):
            events.append(l6.apply_event(ctx, store, doc))
            as_of = max(as_of, doc.ngay_hieu_luc)
        _CHAIN.update(ctx=ctx, store=store, events=events, as_of=as_of)
    return _CHAIN["ctx"], _CHAIN["store"], _CHAIN["events"], _CHAIN["as_of"]


def mini_store():
    s = a4.Store()
    s.add(a4.Ver("X.D1", 1, "dieu", "1", "Tiêu đề", "", None, D(2021, 1, 1), None, None, "normal", None, "X"))
    s.add(a4.Ver("X.D1.K1", 1, "khoan", "1", None, "Chữ cũ", "X.D1", D(2021, 1, 1), None, None, "normal", None, "X"))
    s.add(a4.Ver("X.D1.K1.a", 1, "diem", "a", None, "Điểm a", "X.D1.K1", D(2021, 1, 1), None, None, "normal", None, "X"))
    return s


# ---- chuẩn hoá chữ ----

def test_text_norm_ignores_format_only_differences():
    n = a4.text_norm
    assert n("Trung ương") == n("trung ương")
    assert n("trong ngàyhoặc") == n("trong ngày hoặc")
    assert n("thời gian - thời") == n("thời gian – thời")
    assert n("Ủy ban nhân dân thỏa thuận hòa giải.") == n("Uỷ ban nhân dân thoả thuận hoà giải")
    assert n("“ Điều 54. Điều kiện”") == n("“Điều 54. Điều kiện”")
    assert n("Nhân lực[2]") == n("Nhân lực")
    assert n("điều 189, 19") != n("điều 89, 19"), "đổi số là đổi chữ"


# ---- kho phiên bản ----

def test_store_new_version_closes_previous_half_open():
    s = mini_store()
    v2 = s.new_version("X.D1.K1", D(2023, 9, 18), "Y", "Chữ mới", None, [], "Y.D1")
    v1 = s.vers["X.D1.K1"][0]
    assert v1.effective_to == D(2023, 9, 18) and v2.effective_from == D(2023, 9, 18) and v2.previous_version == 1
    assert v1.in_force(D(2023, 9, 17)) and not v1.in_force(D(2023, 9, 18)) and v2.in_force(D(2023, 9, 18))
    assert [x.text for x in s.snapshot(D(2022, 1, 1)) if x.id == "X.D1.K1"] == ["Chữ cũ"]
    assert [x.text for x in s.snapshot(D(2024, 1, 1)) if x.id == "X.D1.K1"] == ["Chữ mới"]


def test_store_two_edits_in_same_event_edit_in_place():
    s = mini_store()
    s.new_version("X.D1.K1", D(2023, 9, 18), "Y", "A", None, [], "d1")
    s.new_version("X.D1.K1", D(2023, 9, 18), "Y", "B", None, [], "d2")
    assert len(s.vers["X.D1.K1"]) == 2 and s.cur("X.D1.K1").text == "B", "không tạo phiên bản [d, d) rỗng"


def test_store_close_tree_never_deletes():
    s = mini_store()
    n = s.close_tree("X.D1", D(2025, 8, 7), "Z", ["topic"])
    assert n == 3 and all(s.cur(k).effective_to == D(2025, 8, 7) for k in s.vers) and len(s.vers) == 3
    assert s.snapshot(D(2025, 8, 7)) == [] and len(s.snapshot(D(2025, 8, 6))) == 3
    assert s.close("X.D1", D(2030, 1, 1), "Z") is False, "đã đóng sớm hơn thì không đóng lại"


def test_pending_and_suspended_are_never_in_force():
    s = mini_store()
    v = s.cur("X.D1.K1")
    v.state, v.effective_from = "pending_event", None
    assert not v.in_force(D(2030, 1, 1)) and v.status(D(2030, 1, 1)) == "pending_event"
    s2 = mini_store()
    nv = s2.new_version("X.D1.K1", D(2025, 8, 7), "Z", None, None, ["topic_uncertain"], "d", "suspended", "chủ đề")
    assert nv.text == "Chữ cũ" and not nv.in_force(D(2026, 1, 1)) and nv.status(D(2026, 1, 1)) == "suspended"


# ---- payload và cụm từ ----

def test_parse_payload_tree_and_default_node():
    roots = l6.parse_payload(["“6. Được cử sang Việt Nam.", "a) Điểm một;", "b) Điểm hai.”."])
    assert len(roots) == 1 and roots[0].kind == "khoan" and roots[0].number == "6" and [c.number for c in roots[0].children] == ["a", "b"]
    roots = l6.parse_payload(["“Một trong các giấy tờ quy định tại khoản 8.”."], l6.Node("khoan", "7"))
    assert roots[0].number == "7" and roots[0].text == "Một trong các giấy tờ quy định tại khoản 8."
    assert l6.parse_payload(["“Chữ không nhãn.”."]) is None
    roots = l6.parse_payload(["“Điều 4. Sử dụng người lao động nước ngoài", "1. Khoản một:", "a) điểm.”."])
    assert roots[0].kind == "dieu" and roots[0].heading == "Sử dụng người lao động nước ngoài" and roots[0].children[0].children[0].number == "a"


def test_replace_phrase_flexible_accents_and_spaces():
    assert l6.replace_phrase("Chủ tịch Ủy ban nhân dân cấp tỉnh quyết định", "Chủ tịch Ủy ban nhân dân cấp tỉnh", "Sở LĐTBXH") == ("Sở LĐTBXH quyết định", 1)
    assert l6.replace_phrase("Chủ tịch Uỷ ban nhân dân", "Chủ tịch Ủy ban nhân dân", "Sở")[1] == 1
    assert l6.replace_phrase("không có cụm cần tìm", "cụm khác", "x")[1] == 0
    assert l6.replace_phrase("3 ngày và 3 ngày", "3 ngày", "3 ngày làm việc")[0] == "3 ngày làm việc và 3 ngày làm việc"


def test_phrase_clause_parsing_with_targets_after_pairs():
    masked, q = l6.mask_quotes("Thay thế cụm từ “khoản 4, 6 và 8 Điều 154” bằng cụm từ “khoản 4 và khoản 6 Điều 154” và cụm từ “3 ngày” thành cụm từ “3 ngày làm việc” tại khoản 2 Điều 8;")
    pairs = list(l6.PAIR_RE.finditer(masked))
    assert len(pairs) == 2 and q[int(pairs[1][1])] == "3 ngày" and q[int(pairs[1][3])] == "3 ngày làm việc"
    masked, q = l6.mask_quotes("Thay thế cụm từ “A” tại khoản 1 Điều 5 bằng cụm từ “B”; Thay thế cụm từ “C” bằng cụm từ “D” tại khoản 2 Điều 6")
    cl = l6.split_clauses(masked)
    assert len(cl) == 2 and l6.PAIR_RE.search(cl[0])["mid"].strip() == "khoản 1 Điều 5"


# ---- chuỗi dev ----

def test_dev_gates_all_pass():
    ctx, store, events, as_of = chain()
    bad = [name for name, ok, info in l6.dev_gates(ctx, store, as_of) if not ok]
    assert not bad, bad


def test_no_unknown_directive_and_known_unmatched():
    ctx, store, events, as_of = chain()
    assert ctx.unknown == [], ctx.unknown
    assert [(u, why) for _, u, why in ctx.unmatched] == [("ND_70-2023.D1.K14.c", "bãi bỏ mã không có hoặc đã đóng: ND_152-2020.D30.K6a.a")]


def test_nd70_changes_on_nd152():
    ctx, store, events, as_of = chain()
    v = store.vers["ND_152-2020.D7.K6"]
    assert v[0].effective_to == D(2023, 9, 18) and v[1].effective_from == D(2023, 9, 18) and "giảng dạy hoặc làm nhà quản lý" in v[1].text
    k14 = store.cur("ND_152-2020.D7.K14")
    assert k14.version == 2
    d8k2 = store.vers["ND_152-2020.D8.K2"][1]
    assert "khoản 4 và khoản 6 Điều 154" in d8k2.text and "3 ngày làm việc" in d8k2.text
    for k in ("ND_152-2020.D30.K5.c", "ND_152-2020.D30.K5.d", "ND_152-2020.D30.K5.dd", "ND_152-2020.D30.K6.g"):
        assert store.vers[k][0].effective_to == D(2023, 9, 18), k  # ND_70 bãi bỏ điểm c, d, đ khoản 5 và điểm g khoản 6 Điều 30
    assert store.vers["ND_152-2020.D30.K5.a"][0].effective_to == D(2025, 8, 7), "điểm a không bị ND_70 chạm"
    assert store.vers["ND_152-2020.D7.K8"][0].effective_to == D(2025, 8, 7), "K8 không bị ND_70 chạm, chỉ bị ND_219 đóng"


def test_topic_expiry_by_chapter():
    ctx, store, events, as_of = chain()
    st = {k: store.cur(k).status(as_of) for k in store.vers if k.startswith("ND_152-2020.C")}
    assert st["ND_152-2020.CII"] == "expired" and st["ND_152-2020.CIII"] == "in_force"
    assert st["ND_152-2020.CI"] == "suspended" and st["ND_152-2020.CIV"] == "suspended"
    assert store.cur("ND_152-2020.D22.K1").in_force(as_of) and not store.cur("ND_152-2020.D9.K1").in_force(as_of)
    assert store.cur("ND_219-2025.D7.K13.a").in_force(D(2025, 10, 1)) and not store.cur("ND_219-2025.D7.K13.a").in_force(D(2025, 6, 1))
    assert store.vers["ND_152-2020.D7.K8"][0].in_force(D(2025, 6, 1)) and not store.vers["ND_152-2020.D7.K8"][0].in_force(D(2025, 10, 1))


def test_whole_document_replacement_and_pending_targets():
    ctx, store, events, as_of = chain()
    assert all(v[-1].effective_to == D(2022, 1, 17) for k, v in store.vers.items() if k.startswith("ND_28-2020."))
    assert all(v[-1].effective_to == D(2026, 9, 10) for k, v in store.vers.items() if k.startswith("ND_12-2022."))
    numbers = {p["target_number"] for p in store.pending}
    assert "38/2022/NĐ-CP" in numbers and "128/2025/NĐ-CP" in numbers and "35/2022/NĐ-CP" in numbers
    assert any(e["p"] == "replaces" and e["o"] == "external:38/2022/NĐ-CP" for e in store.edges)


def test_conditional_effect_pending_event():
    ctx, store, events, as_of = chain()
    for k in ("ND_283-2026.D61.K2", "ND_283-2026.D63.K11", "ND_283-2026.D7.K2.e", "ND_283-2026.D14"):
        v = store.cur(k)
        assert v.state == "pending_event" and v.effective_from is None and v.trigger and not v.in_force(D(2030, 1, 1)), k
    assert "189/2025" in store.cur("ND_283-2026.D61.K2").trigger
    assert store.cur("ND_283-2026.D61.K1").state == "normal"


def test_pending_event_not_fired_by_documents_that_merely_cite_the_same_decrees():
    import copy
    import re
    import a2_edges as a2
    ctx, store, events, as_of = chain()
    trigger = store.cur("ND_283-2026.D7.K2.e").trigger
    numbers = {a2.norm_number(n) for n in re.findall(a2.NUMBER_RE, trigger)}
    body219 = a2.norm_number(" ".join((u.get("text") or "") for u in ctx.units["ND_219-2025"].values()))
    assert numbers and all(n in body219 for n in numbers), "ND_219 trích đủ số hiệu của mô tả: bộ khớp chỉ theo số hiệu sẽ kích hoạt nhầm"
    for cand in ("ND_219-2025", "ND_70-2023", "ND_152-2020", "ND_145-2020"):
        s = copy.deepcopy(store)
        ev = l6.Ev(ctx.docs[cand])
        l6.check_triggers(ctx, s, ctx.docs[cand], ctx.units[cand], D(2030, 1, 1), ev)
        assert ev.triggered == [], (cand, ev.triggered[:3])
    assert sum(1 for vs in store.vers.values() if vs[-1].state == "pending_event") == 18


def test_term_and_overrides_of_nq_66_16():
    ctx, store, events, as_of = chain()
    assert store.cur("NQ_66-16-2026.D1").effective_to == D(2027, 3, 1)
    ov = [e for e in store.edges if e["p"] == "overrides"]
    assert ov and all(e["valid_from"] == "2026-04-15" and e["valid_to"] == "2027-03-01" for e in ov)
    assert all(e["o"].startswith("ND_145-2020.D") for e in ov)
    assert any(e["p"] == "ends_when_replaced" for e in store.edges)


def test_consolidation_vbhn125():
    ctx, store, events, as_of = chain()
    k8a = store.cur("BLLD_45-2019.D154.K8a")
    assert k8a.effective_from == D(2026, 1, 1) and "from_consolidation" in k8a.flags and k8a.footnote == [2]
    assert not [k for k, v in store.vers.items() if k.startswith("BLLD_45-2019.") and len(v) > 1]
    ev = next(e for e in events if e["doc_id"] == "VBHN_125-2025")
    disc = set(ev["consolidation_discrepancy"])
    assert "BLLD_45-2019.D185.K4" in disc and "BLLD_45-2019.D42.K2" in disc and "BLLD_45-2019.D220.K3" in disc
    for ok in ("BLLD_45-2019.D73", "BLLD_45-2019.D125", "BLLD_45-2019.D143", "BLLD_45-2019.D219", "BLLD_45-2019.D174.K1", "BLLD_45-2019.D64.K2"):
        assert not any(d == ok or d.startswith(ok + ".") for d in disc), ok
    assert store.cur("BLLD_45-2019.D185.K4").flags.count("consolidation_discrepancy") == 1


def test_supplement_list_tt19_into_tt11():
    ctx, store, events, as_of = chain()
    new = [v for k, vs in store.vers.items() if k.startswith("TT_11-2020-BLDTBXH.PL") for v in vs if "supplement_row" in v.flags]
    assert len(new) > 100 and all(v.effective_from == D(2024, 2, 15) and v.version == 1 for v in new)
    assert not [k for k, vs in store.vers.items() if k.startswith("TT_11-2020-BLDTBXH.") and len(vs) > 1]
    assert any(e["p"] == "supplements_list" and e["o"].startswith("TT_11-2020-BLDTBXH.PL") for e in store.edges)


def test_law_2012_documents_are_flagged_not_linked_to_2019():
    ctx, store, events, as_of = chain()
    for d in ("ND_90-2019", "ND_28-2020"):
        assert next(e for e in events if e["doc_id"] == d)["flags"].get("law_2012_era_document") == 1


def test_chain_is_deterministic_on_disk():
    def digest():
        out = subprocess.run([sys.executable, "-X", "utf8", "-I", "src/a4_versions.py"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        assert out.returncode == 0, out.stdout[-500:] + out.stderr[-500:]
        d = corpus.out_dir("a4")
        return [hashlib.sha256((d / f).read_bytes()).hexdigest() for f in ("versions.jsonl", "version_edges.jsonl", "pending_links.jsonl")]
    assert digest() == digest()


_harness.run(globals())
