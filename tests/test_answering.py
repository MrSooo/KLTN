"""Test bước 1.9 (src/answering.py): phân loại bốn kết quả, căn cứ, Π_τ theo phiên bản, cổng đầu ra LLM.

Quy tắc dựng tay theo dạng thật (BLLĐ D151.K1/K1.d, D154.K8) cộng hai quy tắc giả cho nhánh "điều kiện bị bác" (Q10) và nhánh cô lập,
vì giai đoạn này chưa có dữ liệu thật cho hai nhánh đó. Cần SWI-Prolog; máy không có thì các test chạy s(CASP) in "bỏ qua".
"""
import datetime
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import _harness  # noqa: E402
import answering  # noqa: E402
import rules  # noqa: E402

D = "BLLD_45-2019."


def lit(atom, naf=False, neg=False):
    return {"atom": atom, "pred": atom, "naf": naf, "neg": neg}


def rule(rid, unit, head, body, neg=False, isolated=False):
    return {"id": rid, "unit": unit, "head": {"atom": head, "pred": head, "neg": neg}, "body": body, "how": "compiled",
            "source_units": [unit], "isolated": isolated}


def kb():
    rs = [
        rule("r1", D + "D151.K1", "foreign_worker", [lit("holds_foreign_nationality")]),
        rule("r2", D + "D151.K1.d", "must_holds_work_permit", [lit("foreign_worker")]),
        rule("r3", D + "D154.K8", "not_applicable_subject_to_work_permit_issuance",
             [lit("foreign_worker"), lit("married_to_vietnamese_citizen"), lit("resides_in_vietnam")]),
        rule("r4", D + "D54.K1", "eligible_for_license", [lit("leasing_enterprise"), lit("deposit_enough")]),  # nhánh Q10
        rule("r5", D + "D54.K2", "eligible_for_license", [lit("leasing_enterprise"), lit("special_case")]),
        rule("r6", D + "D99.K1", "eligible_for_license", [], isolated=True),  # nhánh cô lập
    ]
    rules.apply_blocks(rs, {(D + "D154", D + "D151.K1.d"): "1.5"})
    return rs


def facts(*xs):
    return [{"vi_tu": x.lstrip("-"), "phu_dinh": x.startswith("-"), "trich": "x"} for x in xs]


def has_swipl():
    if Path(rules.SWIPL).exists() or shutil.which(rules.SWIPL):
        return True
    print("bỏ qua: không có SWI-Prolog")
    return False


def classify(phi, fs, iso=False):
    rs = kb()
    iso_ids = {r["id"] for r in rs if r["isolated"]} if iso else set()
    return answering.classify(phi, fs, [r for r in rs if iso or not r["isolated"]], iso_ids)


def test_answering_proven_with_grounds():
    if not has_swipl():
        return
    out = classify("must_holds_work_permit", facts("holds_foreign_nationality"))
    assert out["ket_qua"] == "ket_luan_duoc"
    assert set(out["can_cu"]) == {D + "D151.K1.d", D + "D151.K1"}  # D154 không chạy nên không là căn cứ


def test_answering_blocked_is_rejected_with_exception_ground():
    if not has_swipl():
        return
    out = classify("must_holds_work_permit", facts("holds_foreign_nationality", "married_to_vietnamese_citizen", "resides_in_vietnam"))
    assert out["ket_qua"] == "bi_bac" and {D + "D151.K1.d", D + "D154.K8"} <= set(out["can_cu"])


def test_answering_contradicted_condition_is_rejected_q10():
    if not has_swipl():
        return
    out = classify("eligible_for_license", facts("leasing_enterprise", "-deposit_enough", "-special_case"))
    assert (out["ket_qua"], out["ly_do"]) == ("bi_bac", "dieu_kien_bi_bac")


def test_answering_missing_fact_is_not_enough_grounds():
    if not has_swipl():
        return
    # thế giới mở: không nói gì về ký quỹ thì không bác, chỉ chưa đủ căn cứ
    out = classify("eligible_for_license", facts("leasing_enterprise", "-special_case"))
    assert out["ket_qua"] == "chua_du_can_cu"


def test_answering_isolated_rule_gives_no_answer():
    if not has_swipl():
        return
    out = classify("eligible_for_license", facts("leasing_enterprise"), iso=True)
    assert out["ket_qua"] == "khong_tra_loi" and out["ly_do"].startswith("co_lap")


def test_answering_vocabulary_drops_heads_only_in_isolated_rules():
    # D27.K1 (A62): `terminate` chỉ có ở quy tắc cô lập thân rỗng thì không đưa cho LLM chọn làm φ; đầu có cả quy tắc sống thì giữ
    rs = kb() + [rule("r7", D + "D27.K1", "terminate", [], isolated=True)]
    heads = answering.live_heads(rs)
    assert "terminate" not in heads and "eligible_for_license" in heads and "must_holds_work_permit" in heads


def test_answering_contradictory_facts_and_out_of_scope():
    out = classify("must_holds_work_permit", facts("holds_foreign_nationality", "-holds_foreign_nationality"))
    assert out["ket_qua"] == "loi"
    assert classify(None, facts("holds_foreign_nationality"))["ly_do"] == "ngoai_pham_vi"


def test_answering_garbled_scasp_output_is_error_not_no():
    out = answering.classify("must_holds_work_permit", facts("holds_foreign_nationality"), kb()[:2], set(), query=lambda p, q: (None, "rác"))
    assert out["ket_qua"] == "loi"


def test_answering_pi_tau_needs_live_version_with_same_text():
    d = datetime.date
    r = rule("r9", D + "D1.K1", "x", [lit("y")])
    ver = [{"id": D + "D1.K1", "state": "normal", "effective_from": d(2021, 1, 1), "effective_to": d(2025, 1, 1), "text_norm": "chữ cũ"},
           {"id": D + "D1.K1", "state": "normal", "effective_from": d(2025, 1, 1), "effective_to": None, "text_norm": "chữ mới"}]
    texts = {D + "D1.K1": "chữ cũ"}
    assert answering.in_force_rules([r], ver, texts, d(2024, 6, 1)) == [r]
    assert answering.in_force_rules([r], ver, texts, d(2025, 6, 1)) == []  # đơn vị đã sửa: quy tắc cũ hết dùng, chờ 2.6
    assert answering.in_force_rules([r], ver, texts, d(2020, 6, 1)) == []


def test_answering_gate_checks_quote_and_names():
    q = {"cau_hoi": "Người nước ngoài có phải có giấy phép không?"}
    ok = {"phi": "must_a", "su_kien": [{"vi_tu": "foreign", "phu_dinh": False, "trich": "Người nước ngoài"}]}
    assert answering.gate(ok, q, {"foreign"}, {"must_a"}) is None
    assert answering.gate(dict(ok, phi="must_b"), q, {"foreign"}, {"must_a"})
    assert answering.gate({"phi": None, "su_kien": [{"vi_tu": "foreign", "phu_dinh": False, "trich": "người Việt"}]}, q, {"foreign"}, set())
    # φ là đầu mô tả trùng tên vị từ: không được làm dữ kiện (LLM tự trả lời)
    assert answering.gate({"phi": "foreign", "su_kien": [{"vi_tu": "foreign", "phu_dinh": False, "trich": "Người nước ngoài"}]}, q, {"foreign"}, {"foreign"})



def test_question_vocab_top_k_plus_rule_bodies_a63():
    """[A63] Từ vựng riêng của câu: kết luận gần chữ câu hỏi nhất + vị từ thân của quy tắc kết luận chúng."""
    rs = kb()
    vocab = {"ket_luan": [{"ten": "must_holds_work_permit", "nghia": "phải: có giấy phép lao động"},
                          {"ten": "eligible_for_license", "nghia": "đủ điều kiện cấp giấy phép cho thuê lại"}],
             "vi_tu": [{"ten": "foreign_worker", "nghia": "người lao động nước ngoài"}, {"ten": "leasing_enterprise", "nghia": "doanh nghiệp cho thuê lại"},
                       {"ten": "deposit_enough", "nghia": "ký quỹ đủ"}, {"ten": "special_case", "nghia": "trường hợp đặc biệt"}]}
    old = answering.TOP_K
    answering.TOP_K = 1
    try:
        v = answering.QuestionVocab(vocab, rs).of("Người nước ngoài có phải có giấy phép lao động không?")
    finally:
        answering.TOP_K = old
    assert [e["ten"] for e in v["ket_luan"]] == ["must_holds_work_permit"]
    names = {e["ten"] for e in v["vi_tu"]}
    assert "foreign_worker" in names and "deposit_enough" not in names


_harness.run(globals())
