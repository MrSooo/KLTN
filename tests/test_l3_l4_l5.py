"""Test L5 (tường minh, chung), L3 (điều khoản giao chi tiết, based_on, details) và L4 (phân loại Điều)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import _harness  # noqa: E402
import parse as l1  # noqa: E402
import refs as l2  # noqa: E402
import exceptions_explicit as l5x  # noqa: E402
import exceptions_general as l5g  # noqa: E402
import corpus  # noqa: E402
import links as l3  # noqa: E402
import delegation  # noqa: E402
import article_type as l4  # noqa: E402

B = "BLLD_45-2019."


def exceptions(doc_id):
    docs, all_units, resolver, available = l2.load_context()
    doc = docs[doc_id]
    edges, handled, unhandled, pending = l5x.find_exceptions(doc, all_units[doc_id], all_units, resolver, available)
    nodes, e6, unh6, pend6 = l5g.find_general(doc, all_units[doc_id], all_units, resolver, available, unhandled)
    return edges, handled, unhandled, nodes, e6, unh6


# ---- L5 tường minh ----

def test_l5_explicit_rule2_children_are_exceptions_of_parent():
    P = "ND_152-2020."
    units = {P + "D1": {"id": P + "D1", "type": "dieu", "parent": None, "text": "Quy định này áp dụng cho mọi người, trừ các trường hợp sau đây:"},
             P + "D1.a": {"id": P + "D1.a", "type": "diem", "parent": P + "D1", "text": "Trường hợp một"},
             P + "D1.b": {"id": P + "D1.b", "type": "diem", "parent": P + "D1", "text": "Trường hợp hai"}}
    docs = corpus.load_manifest()
    resolver = l2.Resolver(docs, l2.load_headers())
    edges, handled, unhandled, pending = l5x.find_exceptions(docs["ND_152-2020"], units, {"ND_152-2020": units}, resolver, {"ND_152-2020"})
    assert {(s, o, m) for s, _, o, _, m in edges} == {(P + "D1.a", P + "D1", l5x.EXCEPT_LIST), (P + "D1.b", P + "D1", l5x.EXCEPT_LIST)}
    assert not unhandled


def test_l5_explicit_rule1_needs_reference_right_before():
    P = "ND_152-2020."
    docs = corpus.load_manifest()
    resolver = l2.Resolver(docs, l2.load_headers())
    units = {P + "D9": {"id": P + "D9", "type": "dieu", "parent": None, "text": "x"},
             P + "D5": {"id": P + "D5", "type": "dieu", "parent": None, "text": "Quy định tại Điều 9 không áp dụng đối với doanh nghiệp nhỏ"},
             P + "D6": {"id": P + "D6", "type": "dieu", "parent": None, "text": "Việc này không áp dụng đối với doanh nghiệp nhỏ"}}
    edges, handled, unhandled, pending = l5x.find_exceptions(docs["ND_152-2020"], units, {"ND_152-2020": units}, resolver, {"ND_152-2020"})
    assert [(s, o) for s, _, o, _, _ in edges] == [(P + "D5", P + "D9")]
    assert [u["unit"] for u in unhandled] == [P + "D6"]


def test_l5_trigger_ignores_non_exception_senses():
    """A22: 'khấu trừ', 'loại trừ', 'giảm trừ', 'trừ đi' là phép trừ hoặc nghĩa khác, không phải trigger; 'trừ', 'ngoại trừ', 'không áp dụng' vẫn là."""
    def trig(text):
        return [m[0].lower() for _, m in l5x.find_triggers({"D.D1": {"id": "D.D1", "type": "dieu", "parent": None, "text": text}})]
    assert trig("Người sử dụng lao động khấu trừ tiền lương của người lao động. Mức giảm trừ gia cảnh. Việc loại trừ hoặc ưu tiên. Trừ đi thời gian đã tham gia.") == []
    assert trig("Áp dụng cho mọi người, trừ lĩnh vực nghệ thuật; ngoại trừ trường hợp khác; không áp dụng cho doanh nghiệp nhỏ") == ["trừ", "ngoại trừ", "không áp dụng"]


def test_l5_explicit_rule2_needs_list_tail_not_midsentence_tru():
    """A22: 'trừ' giữa câu rồi câu kết bằng 'theo một trong các mức sau đây:' thì các khoản con là mức phạt, không phải ngoại lệ; không tạo cạnh."""
    P = "ND_152-2020."
    docs = corpus.load_manifest()
    resolver = l2.Resolver(docs, l2.load_headers())
    for text in ["Phạt tiền khi có hành vi sửa đổi hợp đồng, trừ trường hợp kéo dài thời hạn; không thực hiện đúng quy định theo một trong các mức sau đây:",
                 "Trừ các trường hợp quy định tại Điều 108, các trường hợp khác phải được sự đồng ý về các nội dung sau đây:"]:
        units = {P + "D1": {"id": P + "D1", "type": "dieu", "parent": None, "text": text},
                 P + "D1.a": {"id": P + "D1.a", "type": "diem", "parent": P + "D1", "text": "Mức một"}}
        edges, handled, unhandled, pending = l5x.find_exceptions(docs["ND_152-2020"], units, {"ND_152-2020": units}, resolver, {"ND_152-2020"})
        assert not edges and [u["unit"] for u in unhandled] == [P + "D1"], text


def test_l5_explicit_skips_directive_lines():
    units = {"D.D1": {"id": "D.D1", "type": "dieu", "parent": None, "text": "Bãi bỏ khoản 2 Điều 5, trừ trường hợp khác"}}
    assert l5x.find_triggers(units) == []


# ---- L5 chung ----

def test_l5_general_clause_extraction():
    text = "Người lao động phải báo trước, trừ trường hợp quy định tại Điều 154 của Bộ luật này."
    clause, evidence = l5g.clause_of(text, text.index("trừ"))
    assert clause == "quy định tại Điều 154 của Bộ luật này" and evidence.startswith("trừ trường hợp")
    text = "Trừ trường hợp pháp luật có quy định khác, người sử dụng lao động phải trả lương."
    clause, evidence = l5g.clause_of(text, 0)
    assert clause == "pháp luật có quy định khác" and evidence == "Trừ trường hợp pháp luật có quy định khác"
    assert l5g.clause_of("Trừ trường hợp A phải làm B", 0)[0] is None


def test_l5_general_noun_family_takes_only_listed_nouns():
    text = "Xử phạt theo Chương II, trừ hành vi vi phạm quy định tại khoản 3 Điều 32 Nghị định này;"
    clause, evidence = l5g.clause_of(text, text.index("trừ"))
    assert clause == "hành vi vi phạm quy định tại khoản 3 Điều 32 Nghị định này" and evidence.startswith("trừ hành vi") and evidence in text
    text = "Cấm sử dụng, trừ các công việc nghệ thuật, thể dục, thể thao."
    assert l5g.clause_of(text, text.index("trừ"))[0] == "các công việc nghệ thuật, thể dục, thể thao"
    for text in ["Tính thời gian làm việc, trừ thời gian nghỉ ốm.", "Người sử dụng lao động (trừ nhà thầu) phải báo cáo."]:
        clause, reason = l5g.clause_of(text, text.index("trừ"))
        assert clause is None and "không phải" in reason, text  # danh từ ngoài danh sách thì không đoán


def test_l5_general_determiner_before_truong_hop():
    text = "Làm thêm phải được đồng ý, trừ những trường hợp không phải xác định nhu cầu."
    clause, evidence = l5g.clause_of(text, text.index("trừ"))
    assert clause == "không phải xác định nhu cầu" and evidence.startswith("trừ những trường hợp")


def test_l5_general_semicolon_cut_keeps_reference_lists_and_cuts_new_rule():
    keep = "Phạt gấp đôi, trừ trường hợp quy định tại khoản 1 Điều 7; khoản 3 Điều 13; các Điều 43, 44; điểm a khoản 2 Điều 25."
    assert l5g.clause_of(keep, keep.index("trừ"))[0] == "quy định tại khoản 1 Điều 7; khoản 3 Điều 13; các Điều 43, 44; điểm a khoản 2 Điều 25"
    cut = "Phạt gấp đôi, trừ trường hợp quy định tại khoản 1 Điều 7; không thực hiện đúng thời hạn thì bị phạt."
    clause, evidence = l5g.clause_of(cut, cut.index("trừ"))
    assert clause == "quy định tại khoản 1 Điều 7" and evidence == "trừ trường hợp quy định tại khoản 1 Điều 7"


def test_l5_general_closing_parenthesis_ends_clause():
    text = "Vi phạm quy định về an toàn (trừ hành vi quy định tại khoản 8 Điều này)."
    clause, evidence = l5g.clause_of(text, text.index("trừ"))
    assert clause == "hành vi quy định tại khoản 8 Điều này" and evidence == "trừ hành vi quy định tại khoản 8 Điều này"
    text = "Vi phạm (kể cả vi phạm lần đầu) trừ hành vi A."
    assert l5g.clause_of(text, text.index("trừ"))[0] == "hành vi A"  # ngoặc cân bằng nằm trước "trừ" thì không cắt


def test_l5_general_list_tail_only_for_new_family():
    text = "Phải qua hòa giải, trừ các tranh chấp lao động sau đây:"
    clause, reason = l5g.clause_of(text, text.index("trừ"))
    assert clause is None and "dấu hai chấm" in reason
    text = "Phải qua hòa giải, trừ các trường hợp sau:"
    assert l5g.clause_of(text, text.index("trừ"))[0] is None
    text = "Phải báo trước, trừ trường hợp sau đây:"  # "trừ trường hợp" trơn: giữ hành vi cũ
    assert l5g.clause_of(text, text.index("trừ"))[0] == "sau đây"


def test_l5_general_other_reason_is_specific():
    def reason(text, trigger):
        return l5g.other_reason(text, {"pos": text.index(trigger), "reason": "chung"})
    assert "phép trừ" in reason("thanh toán sau khi trừ chi phí ngân hàng", "trừ")
    assert "phép trừ" in reason("chi phí được trừ khi xác định thu nhập", "trừ")
    assert "áp dụng thử" in reason("không áp dụng thử mức lao động trước khi ban hành", "không áp dụng")
    assert "không kèm dẫn chiếu" in reason("Không áp dụng thử việc đối với người lao động dưới 01 tháng.", "Không áp dụng")
    assert "danh sách đã đọc" in reason("làm việc, trừ thời gian nghỉ", "trừ")
    assert reason("việc khác", "việc") == "chung"


def test_l5_general_noun_family_on_blld():
    edges, handled, unhandled, nodes, e6, unh6 = exceptions("BLLD_45-2019")
    rules = {(e["s"], e["o"]): e["rule"] for e in e6}
    nid = {u: n for n in nodes.values() for u in n["units"]}
    for u in ("D61.K4", "D70.K3", "D145.K3", "D20.K2.c"):
        assert B + u in nid, u
        assert any(e["o"] == B + u and e["rule"] == "general_except_noun" for e in e6), u
    for t in ("D149.K1", "D151.K2", "D177.K4"):  # dẫn chiếu nằm trong mệnh đề của D20.K2.c
        assert rules[(B + t, B + "D20.K2.c")] == "general_except_noun_ref", t
    assert sorted(u["unit"].split(".", 1)[1] for u in unh6) == ["D188.K1", "D24.K3"]
    assert (B + "D154", B + "D151.K1.d") in rules  # cạnh cũ không đổi


def test_l5_general_two_triggers_split_by_semicolon_or_clash():
    edges, handled, unhandled, nodes, e6, unh6 = exceptions("ND_145-2020")
    assert sum(1 for e in e6 if e["o"] == "ND_145-2020.D89.K1.d1" and e["rule"] == "general_except") == 3  # ba "trừ trường hợp", mỗi vế một nút
    edges, handled, unhandled, nodes, e6, unh6 = exceptions("ND_152-2020")
    clash = [u["reason"] for u in unh6 if u["unit"].endswith("D13.K5")]
    assert len(clash) == 2 and all(r.startswith("nhiều hơn một 'trừ'") for r in clash)  # cùng một vế: không đoán


def test_l5_general_condition_kinds_and_merge_key():
    assert l5g.condition_kind(l5g.norm_text("có thỏa thuận khác.")) == "tuy_nghi"
    assert l5g.condition_kind(l5g.norm_text("Các bên có thoả thuận khác")) == "tuy_nghi"
    assert l5g.condition_kind(l5g.norm_text("pháp luật có quy định khác")) == "dan_chieu_mo"
    assert l5g.condition_kind(l5g.norm_text("có thỏa thuận khác về thời hạn")) == "cu_the"
    assert l5g.condition_id("D", l5g.norm_text("Có thỏa thuận khác ;")) == l5g.condition_id("D", l5g.norm_text("có  thỏa thuận khác"))


def test_l5_milestones_on_blld():
    edges, handled, unhandled, nodes, e6, unh6 = exceptions("BLLD_45-2019")
    pairs = {(e["s"], e["o"]) for e in e6}
    assert (B + "D154", B + "D151.K1.d") in pairs
    assert (B + "D36.K1.b", B + "D37.K1") in pairs
    assert (B + "D29", B + "D35.K2.a") in pairs and (B + "D97.K4", B + "D35.K2.b") in pairs
    # 30 nút trước khi thêm họ "trừ <danh từ>" (12/11); thêm 4 nút: D20.K2.c, D61.K4, D70.K3, D145.K3
    assert len(nodes) == 34 and {n["kind"] for n in nodes.values()} == {"cu_the", "tuy_nghi", "dan_chieu_mo"}
    assert len(edges) + sum(len(n["units"]) for n in nodes.values()) + len(unh6) >= len(handled)


def test_l5_every_trigger_is_accounted_for():
    docs, all_units, resolver, available = l2.load_context()
    for d in docs.values():
        units = all_units[d.doc_id]
        edges, handled, unhandled, pending = l5x.find_exceptions(d, units, all_units, resolver, available)
        assert len(handled) + len(unhandled) == len(l5x.find_triggers(units)), d.doc_id
        nodes, e6, unh6, p6 = l5g.find_general(d, units, all_units, resolver, available, unhandled)
        assert sum(len(n["units"]) for n in nodes.values()) + len(unh6) == len(unhandled), d.doc_id


# ---- L3 ----

def test_l3_delegation_patterns():
    units = {B + "D91.K4": {"type": "khoan", "text": "Chính phủ quy định chi tiết Điều này."},
             B + "D154.K9": {"type": "khoan", "text": "Trường hợp khác theo quy định của Chính phủ."},
             B + "D142.K1": {"type": "khoan", "text": "Danh mục do Bộ trưởng Bộ Lao động - Thương binh và Xã hội ban hành."},
             B + "D112": {"type": "dieu", "text": "Thủ tướng Chính phủ quyết định ngày nghỉ lễ."},
             B + "D107.K1": {"type": "khoan", "text": "do Chính phủ quy định."},
             B + "D5": {"type": "dieu", "text": "Quy định tại Điều 3 của Chính phủ."}}
    cl = [c for c in delegation.find_delegation(units, "BLLD_45-2019") if not c["flags"]]  # tầng chặt
    pat = {c["unit_id"].split(".", 1)[1]: c["pattern"] for c in cl}
    assert pat == {"D91.K4": "A", "D154.K9": "B", "D142.K1": "D", "D112": "E", "D107.K1": "A"}
    assert [c["subpattern"] for c in cl if c["unit_id"].endswith("D107.K1")] == ["C"]


def test_delegation_loose_tier_keeps_what_strict_tier_misses_and_never_duplicates():
    units = {B + "D21.K5": {"type": "khoan", "text": "Bộ trưởng Bộ Lao động - Thương binh và Xã hội quy định chi tiết các khoản 1, 2 và 3 Điều này."},
             B + "D91.K4": {"type": "khoan", "text": "Chính phủ quy định chi tiết Điều này."},
             B + "D5": {"type": "dieu", "text": "Người lao động được nghỉ ngơi theo thỏa thuận."}}
    cl = delegation.find_delegation(units, "BLLD_45-2019")
    got = {c["unit_id"].split(".", 1)[1]: (c["pattern"], c["flags"], c["delegate"]) for c in cl}
    # dấu gạch ngang làm dạng A (chặt) hụt, nên chỉ tầng lỏng bắt được và gắn cờ; ca chặt không bị bắt thêm lần nữa ở tầng lỏng; đơn vị không dính gì thì không có
    assert got == {"D21.K5": ("loose", ["loose"], "Bộ trưởng"), "D91.K4": ("A", [], "Chính phủ")}
    assert [c["clause_id"] for c in cl] == ["DC_D91_K4_1", "DC_D21_K5_1"], "ca chặt đứng trước, mã ca chặt không đổi"


def test_l3_key_phrases_for_keyword_proposal():
    ph = l3.key_phrases("Nghị định này quy định mức lương tối thiểu tháng và mức lương tối thiểu giờ áp dụng đối với người lao động")
    assert ph == ["mức lương tối thiểu tháng", "mức lương tối thiểu giờ"]
    assert l3.head_phrase("mức lương tối thiểu tháng") == "mức lương tối thiểu"
    law = {B + "D91": {"id": B + "D91", "type": "dieu", "heading": "Mức lương tối thiểu"}, B + "D90": {"id": B + "D90", "type": "dieu", "heading": "Tiền lương"}}
    assert l3.keyword_candidates(ph, law, [{"unit_id": B + "D91.K4"}])[0][0] == B + "D91"


def test_l3_milestones_in_output():
    docs, all_units, resolver, available = l2.load_context()
    headers = l2.load_headers()
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
    assert c("Trách nhiệm khi chấm dứt hợp đồng lao động") == ("substantive", "default")
    assert c("Hồ sơ đề nghị cấp giấy phép lao động") == ("procedural", "regex")
    assert c("Trình tự cấp lại giấy phép")[0] == "procedural"
    assert c("Hợp đồng lao động vô hiệu") == ("substantive", "default")


def test_l4_domain_headings_stay_substantive():
    """A21: tiêu đề nói về hợp đồng/thỏa ước/nội quy (không phải về chính văn bản luật) không bị đẩy khỏi substantive."""
    c = l4.classify_heading
    for h in ["Hiệu lực của hợp đồng lao động", "Hiệu lực của nội quy lao động", "Hiệu lực và thời hạn của thỏa ước lao động tập thể",
              "Sửa đổi, bổ sung hợp đồng lao động", "Sửa đổi, bổ sung thỏa ước lao động tập thể", "Thẩm quyền giao kết hợp đồng lao động"]:
        assert c(h) == ("substantive", "default"), h


def test_l4_real_effect_and_authority_headings_kept():
    """A21: các tiêu đề thật của hiệu lực/sửa đổi/thẩm quyền vẫn đúng nhãn (nguồn của bước đọc chỉ thị 2.3 không được mất)."""
    c = l4.classify_heading
    for h in ["Hiệu lực", "Hiệu lực thi hành", "Hiệu lực và trách nhiệm thi hành", "Hiệu lực của Nghị định này", "Điều khoản thi hành",
              "Sửa đổi, bổ sung một số điều của các luật có liên quan đến lao động", "Bãi bỏ một số quy định của Nghị định số 35/2022/NĐ-CP",
              "Bổ sung Danh mục nghề, công việc nặng nhọc, độc hại, nguy hiểm", "Thay thế Phụ lục I"]:
        assert c(h) == ("effect_transition", "regex"), h
    for h in ["Thẩm quyền xử phạt của Thanh tra lao động", "Thẩm quyền tuyên bố hợp đồng lao động vô hiệu"]:
        assert c(h) == ("authority", "regex"), h


_harness.run(globals())
