"""Test L5 (A3, A6), L3 (điều khoản giao chi tiết, based_on, details) và L4 (phân loại Điều)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import _harness  # noqa: E402
import a1_parse as a1  # noqa: E402
import a2_edges as a2  # noqa: E402
import a3_exceptions as a3  # noqa: E402
import a6_general_exceptions as a6  # noqa: E402
import corpus  # noqa: E402
import l3_links as l3  # noqa: E402
import l4_classify as l4  # noqa: E402

B = "BLLD_45-2019."


def exceptions(doc_id):
    docs, all_units, resolver, available = a2.load_context()
    doc = docs[doc_id]
    edges, handled, unhandled, pending = a3.find_exceptions(doc, all_units[doc_id], all_units, resolver, available)
    nodes, e6, unh6, pend6 = a6.find_general(doc, all_units[doc_id], all_units, resolver, available, unhandled)
    return edges, handled, unhandled, nodes, e6, unh6


# ---- A3 ----

def test_a3_rule2_children_are_exceptions_of_parent():
    P = "ND_152-2020."
    units = {P + "D1": {"id": P + "D1", "type": "dieu", "parent": None, "text": "Quy định này áp dụng cho mọi người, trừ các trường hợp sau đây:"},
             P + "D1.a": {"id": P + "D1.a", "type": "diem", "parent": P + "D1", "text": "Trường hợp một"},
             P + "D1.b": {"id": P + "D1.b", "type": "diem", "parent": P + "D1", "text": "Trường hợp hai"}}
    docs = corpus.load_manifest()
    resolver = a2.Resolver(docs, a2.load_headers())
    edges, handled, unhandled, pending = a3.find_exceptions(docs["ND_152-2020"], units, {"ND_152-2020": units}, resolver, {"ND_152-2020"})
    assert {(s, o, m) for s, _, o, _, m in edges} == {(P + "D1.a", P + "D1", a3.EXCEPT_LIST), (P + "D1.b", P + "D1", a3.EXCEPT_LIST)}
    assert not unhandled


def test_a3_rule1_needs_reference_right_before():
    P = "ND_152-2020."
    docs = corpus.load_manifest()
    resolver = a2.Resolver(docs, a2.load_headers())
    units = {P + "D9": {"id": P + "D9", "type": "dieu", "parent": None, "text": "x"},
             P + "D5": {"id": P + "D5", "type": "dieu", "parent": None, "text": "Quy định tại Điều 9 không áp dụng đối với doanh nghiệp nhỏ"},
             P + "D6": {"id": P + "D6", "type": "dieu", "parent": None, "text": "Việc này không áp dụng đối với doanh nghiệp nhỏ"}}
    edges, handled, unhandled, pending = a3.find_exceptions(docs["ND_152-2020"], units, {"ND_152-2020": units}, resolver, {"ND_152-2020"})
    assert [(s, o) for s, _, o, _, _ in edges] == [(P + "D5", P + "D9")]
    assert [u["unit"] for u in unhandled] == [P + "D6"]


def test_a3_skips_directive_lines():
    units = {"D.D1": {"id": "D.D1", "type": "dieu", "parent": None, "text": "Bãi bỏ khoản 2 Điều 5, trừ trường hợp khác"}}
    assert a3.find_triggers(units) == []


# ---- A6 ----

def test_a6_clause_extraction():
    text = "Người lao động phải báo trước, trừ trường hợp quy định tại Điều 154 của Bộ luật này."
    clause, evidence = a6.clause_of(text, text.index("trừ"))
    assert clause == "quy định tại Điều 154 của Bộ luật này" and evidence.startswith("trừ trường hợp")
    text = "Trừ trường hợp pháp luật có quy định khác, người sử dụng lao động phải trả lương."
    clause, evidence = a6.clause_of(text, 0)
    assert clause == "pháp luật có quy định khác" and evidence == "Trừ trường hợp pháp luật có quy định khác"
    assert a6.clause_of("Trừ trường hợp A phải làm B", 0)[0] is None


def test_a6_condition_kinds_and_merge_key():
    assert a6.condition_kind(a6.norm_text("có thỏa thuận khác.")) == "tuy_nghi"
    assert a6.condition_kind(a6.norm_text("Các bên có thoả thuận khác")) == "tuy_nghi"
    assert a6.condition_kind(a6.norm_text("pháp luật có quy định khác")) == "dan_chieu_mo"
    assert a6.condition_kind(a6.norm_text("có thỏa thuận khác về thời hạn")) == "cu_the"
    assert a6.condition_id("D", a6.norm_text("Có thỏa thuận khác ;")) == a6.condition_id("D", a6.norm_text("có  thỏa thuận khác"))


def test_l5_milestones_on_blld():
    edges, handled, unhandled, nodes, e6, unh6 = exceptions("BLLD_45-2019")
    pairs = {(e["s"], e["o"]) for e in e6}
    assert (B + "D154", B + "D151.K1.d") in pairs
    assert (B + "D36.K1.b", B + "D37.K1") in pairs
    assert (B + "D29", B + "D35.K2.a") in pairs and (B + "D97.K4", B + "D35.K2.b") in pairs
    assert len(nodes) == 30 and {n["kind"] for n in nodes.values()} == {"cu_the", "tuy_nghi", "dan_chieu_mo"}
    assert len(edges) + sum(len(n["units"]) for n in nodes.values()) + len(unh6) >= len(handled)


def test_l5_every_trigger_is_accounted_for():
    docs, all_units, resolver, available = a2.load_context()
    for d in docs.values():
        units = all_units[d.doc_id]
        edges, handled, unhandled, pending = a3.find_exceptions(d, units, all_units, resolver, available)
        assert len(handled) + len(unhandled) == len(a3.find_triggers(units)), d.doc_id
        nodes, e6, unh6, p6 = a6.find_general(d, units, all_units, resolver, available, unhandled)
        assert sum(len(n["units"]) for n in nodes.values()) + len(unh6) == len(unhandled), d.doc_id


# ---- L3 ----

def test_l3_delegation_patterns():
    units = {B + "D91.K4": {"type": "khoan", "text": "Chính phủ quy định chi tiết Điều này."},
             B + "D154.K9": {"type": "khoan", "text": "Trường hợp khác theo quy định của Chính phủ."},
             B + "D142.K1": {"type": "khoan", "text": "Danh mục do Bộ trưởng Bộ Lao động - Thương binh và Xã hội ban hành."},
             B + "D112": {"type": "dieu", "text": "Thủ tướng Chính phủ quyết định ngày nghỉ lễ."},
             B + "D107.K1": {"type": "khoan", "text": "do Chính phủ quy định."},
             B + "D5": {"type": "dieu", "text": "Quy định tại Điều 3 của Chính phủ."}}
    cl = l3.find_delegation(units, "BLLD_45-2019")
    pat = {c["unit_id"].split(".", 1)[1]: c["pattern"] for c in cl}
    assert pat == {"D91.K4": "A", "D154.K9": "B", "D142.K1": "D", "D112": "E", "D107.K1": "A"}
    assert [c["subpattern"] for c in cl if c["unit_id"].endswith("D107.K1")] == ["C"]


def test_l3_key_phrases_for_keyword_proposal():
    ph = l3.key_phrases("Nghị định này quy định mức lương tối thiểu tháng và mức lương tối thiểu giờ áp dụng đối với người lao động")
    assert ph == ["mức lương tối thiểu tháng", "mức lương tối thiểu giờ"]
    assert l3.head_phrase("mức lương tối thiểu tháng") == "mức lương tối thiểu"
    law = {B + "D91": {"id": B + "D91", "type": "dieu", "heading": "Mức lương tối thiểu"}, B + "D90": {"id": B + "D90", "type": "dieu", "heading": "Tiền lương"}}
    assert l3.keyword_candidates(ph, law, [{"unit_id": B + "D91.K4"}])[0][0] == B + "D91"


def test_l3_milestones_in_output():
    docs, all_units, resolver, available = a2.load_context()
    headers = a2.load_headers()
    links = []
    for d in docs.values():
        if d.doc_id == corpus.BASE_DOC_ID or d.is_consolidation:
            continue
        b, _ = l3.based_on_links(d, all_units[d.doc_id], headers[d.doc_id], all_units, resolver, available)
        det, _ = l3.details_links(d, all_units[d.doc_id], all_units, resolver, available)
        links += b + det
    got = {(l["s"], l["p"], l["o"]) for l in links}
    for x in ("D154.K1", "D154.K2", "D154.K9", "D157", "D150.K3"):
        assert any(s == "ND_152-2020" and p == "details" and o.startswith(B + x) for s, p, o in got), x
    assert ("TT_18-2021-BLDTBXH", "based_on", "ND_145-2020.D68.K2") in got
    assert ("ND_135-2020", "details", B + "D169") in got
    for x in ("D21.K1", "D21.K2", "D21.K3", "D73.K4", "D142.K1"):
        assert ("TT_10-2020-BLDTBXH", "details", B + x) in got, x


# ---- L4 ----

def test_l4_classify_headings():
    c = l4.classify_heading
    assert c("Giải thích từ ngữ") == ("definition", "regex")
    assert c("Hiệu lực thi hành") == ("effect_transition", "regex")
    assert c("Sửa đổi, bổ sung một số điều của Nghị định số 152/2020/NĐ-CP") == ("effect_transition", "regex")
    assert c("Quy định chuyển tiếp") == ("effect_transition", "regex")
    assert c("Trách nhiệm của Bộ Lao động - Thương binh và Xã hội") == ("authority", "regex")
    assert c("Trách nhiệm thi hành") == ("authority", "regex")
    assert c("Trách nhiệm khi chấm dứt hợp đồng lao động") == ("substantive", "default_pending_llm")
    assert c("Hồ sơ đề nghị cấp giấy phép lao động") == ("procedural", "regex")
    assert c("Trình tự cấp lại giấy phép")[0] == "procedural"
    assert c("Hợp đồng lao động vô hiệu") == ("substantive", "default_pending_llm")


_harness.run(globals())
