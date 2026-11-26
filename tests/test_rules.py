"""Test bước 1.8 (src/rules.py): cách dịch đầu quy tắc và phép thử phản chứng D151/D154 bằng s(CASP).

Dữ liệu 1.6A/1.6B ở đây là bản dựng tay theo dạng thật (BLLĐ D151.K1, K1.c, K1.d, D154.K8), không đọc đầu ra của tập con (thư mục đó
không vào repo). Phép thử s(CASP) cần SWI-Prolog; máy không có thì test in "bỏ qua" và coi là đạt.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import _harness  # noqa: E402
import rules as R  # noqa: E402

D = "BLLD_45-2019."


def row(vai, mode, quy_tac="q1", cuc="khang_dinh"):
    return {"loai": "menh_de", "vai": vai, "phuong_thuc": mode, "cuc": cuc, "quy_tac": quy_tac, "nhom_hoac": None}


# đơn vị -> (dòng 1.6A, tên vị từ theo dòng, khoá chủ thể của dòng)
UNITS = {
    D + "D151.K1": ([row("ket_luan", "khong"), row("dieu_kien", "khong")], ["foreign_worker", "holds_foreign_nationality"], [None, None]),
    D + "D151.K1.c": ([row("ket_luan", "phai", cuc="phu_dinh")], ["serving_criminal_sentence"], ["s"]),
    D + "D151.K1.d": ([row("ket_luan", "phai")], ["holds_work_permit"], ["s"]),
    D + "D154.K8": ([row("ket_luan", "khong_ap_dung"), row("dieu_kien", "khong"), row("dieu_kien", "khong")],
                    ["subject_to_work_permit_issuance", "married_to_vietnamese_citizen", "resides_in_vietnam"], ["s", None, None]),
}


def compiled():
    a = {u: {"dong": rows} for u, (rows, _, _) in UNITS.items()}
    pred_of = {(u, i): (n, k) for u, (_, names, keys) in UNITS.items() for i, (n, k) in enumerate(zip(names, keys))}
    rules, notes = R.compile_units(a, pred_of, {"s": "foreign_worker"}, {u: i for i, u in enumerate(UNITS)})
    R.apply_blocks(rules, {(D + "D154", D + "D151.K1.d"): "1.5"})
    return rules, notes


def test_rules_head_prefix_english_and_neg_marks_content():
    rules, _ = compiled()
    heads = {r["unit"].split(".", 1)[1]: (r["head"]["atom"], r["head"]["neg"]) for r in rules}
    assert heads["D151.K1.d"] == ("must_holds_work_permit", False)
    # "phải KHÔNG đang chấp hành hình phạt": phủ định nằm trong nội dung, không phải "-must_" (dấu - dành cho "được miễn")
    assert heads["D151.K1.c"] == ("must_neg_serving_criminal_sentence", False)
    assert heads["D154.K8"] == ("not_applicable_subject_to_work_permit_issuance", False)
    assert heads["D151.K1"] == ("foreign_worker", False)


def test_rules_subject_guard_and_block_relation():
    rules, _ = compiled()
    r = next(x for x in rules if x["unit"].endswith("D151.K1.d"))
    assert [lit["atom"] for lit in r["body"]][:1] == ["foreign_worker"]
    assert any(lit["atom"] == "blocked" for lit in r["body"])
    lines = R.program_text(rules).splitlines()
    assert f"-must_holds_work_permit(X) :- blocked({r['id']}, X)." in lines
    # tắt cạnh 1.7 không ảnh hưởng quan hệ chặn đến từ cạnh 1.5
    assert f"-must_holds_work_permit(X) :- blocked({r['id']}, X)." in R.program_text(rules, llm_edges=False).splitlines()


def test_rules_negative_condition_open_world_for_input_closed_for_concept():
    rows = [row("ket_luan", "khong"), row("dieu_kien", "khong"), row("dieu_kien", "khong", cuc="phu_dinh"), row("dieu_kien", "khong", cuc="phu_dinh")]
    u = D + "D156.K3"
    names = ["validity_lapsed", "work_permit", "conforms_to_content", "derived_ok"]
    rules, _ = R.compile_units({u: {"dong": rows}}, {(u, i): (n, None) for i, n in enumerate(names)}, {}, {u: 0},
                               {"conforms_to_content": "input", "derived_ok": "concept"})
    assert R.rule_text(rules[0]) == "validity_lapsed(X) :- work_permit(X), -conforms_to_content(X), not derived_ok(X)."


def test_rules_effective_kinds_modal_only_concept_becomes_input():
    named = [{"loai": "menh_de", "predicate": "holds_work_permit", "role": "ket_luan", "mode": "phai"},
             {"loai": "menh_de", "predicate": "foreign_worker", "role": "ket_luan", "mode": "khong"},
             {"loai": "menh_de", "predicate": "foreign_worker", "role": "dieu_kien", "mode": "khong"}]
    eff = R.effective_kinds(named, {"holds_work_permit": "concept", "foreign_worker": "concept", "nationality": "input"})
    assert eff == {"holds_work_permit": "input", "foreign_worker": "concept", "nationality": "input"}


def test_rules_llm_edge_toggle_drops_only_llm_blockers():
    rules, _ = compiled()
    R.apply_blocks(rules, {(D + "D154", D + "D151.K1.c"): R.LLM_EDGE})
    r = next(x for x in rules if x["unit"].endswith("D151.K1.c"))
    assert "not blocked(" in R.rule_text(r) and "not blocked(" not in R.rule_text(r, llm_edges=False)
    assert R.active_blockers(r, llm_edges=False) == []


def test_rules_source_units_child_or_has_lead_in_and_item():
    u, k = D + "D53.K2", D + "D53.K2.a"
    a = {u: {"dong": [row("ket_luan", "duoc")]}, k: {"dong": [row("dieu_kien", "khong")]}}
    rules, _ = R.compile_units(a, {(u, 0): ("use_leased_labor", None), (k, 0): ("demand_surge", None)}, {}, {u: 0, k: 1})
    assert [(r["unit"], r["source_units"], r["how"]) for r in rules] == [(k, [u, k], "compiled_child_or")]


def _ptr(phrase, target):
    return {"loai": "con_tro", "vai": "dieu_kien", "trich": [phrase], "targets": [D + target], "quy_tac": None}


def test_rules_pointer_condition_after_condition_or_lead_not_after_conclusion():
    """A62: con trỏ sau một điều kiện thành điều kiện applies_<T> (nhiều đích của một cụm là HOẶC); sau một kết luận thì chỉ cách làm,
    không thành điều kiện; applies_<T> định nghĩa từ điều kiện của T; đích không có quy tắc thì không thêm (tránh quy tắc chết)."""
    u, t1, t2, t3, v = D + "D46.K1", D + "D34.K1", D + "D34.K2", D + "D9", D + "D29.K4"
    a = {u: {"dong": [dict(row("dieu_kien", "khong"), trich=["hợp đồng chấm dứt"]), dict(row("ket_luan", "phai"), trich=["trả trợ cấp"]),
                      _ptr("khoản 1, 2 Điều 34", "D34.K1"), _ptr("khoản 1, 2 Điều 34", "D34.K2"), _ptr("Điều 9", "D9")]},
         t1: {"dong": [row("dieu_kien", "khong"), row("ket_luan", "khong")]}, t2: {"dong": [row("dieu_kien", "khong"), row("ket_luan", "khong")]},
         t3: {"dong": [row("dieu_kien", "khong")]},
         v: {"dong": [dict(row("ket_luan", "phai"), trich=["trả lương ngừng việc"]), _ptr("Điều 34", "D34.K1")]}}
    names = {(u, 0): ("contract_ends", None), (u, 1): ("pay_severance", None), (t1, 0): ("contract_expires", None), (t1, 1): ("terminate", None),
             (t2, 0): ("work_done", None), (t2, 1): ("terminate", None), (t3, 0): ("orphan_cond", None), (v, 0): ("pay_suspension_wage", None)}
    texts = {u: "Khi hợp đồng chấm dứt theo quy định tại khoản 1, 2 Điều 34 thì phải trả trợ cấp, trừ Điều 9", v: "phải trả lương ngừng việc theo Điều 34"}
    rules, notes = R.compile_units(a, names, {}, {x: i for i, x in enumerate(a)}, {}, texts)
    txt = sorted(R.rule_text(r) for r in rules)
    assert "must_pay_severance(X) :- contract_ends(X), applies_d34_k1(X)." in txt and "must_pay_severance(X) :- contract_ends(X), applies_d34_k2(X)." in txt, txt
    assert "applies_d34_k1(X) :- contract_expires(X)." in txt and "must_pay_suspension_wage(X)." in txt, txt
    assert not any("applies_d9" in x for x in txt)  # D9 sau kết luận ("trả trợ cấp"), và D9 không có quy tắc
    assert any("chỉ cách làm" in n for n in notes), notes


def test_rules_pointer_list_is_or_and_negated_pointer_skipped():
    """A62: các cụm dẫn chiếu liền nhau ("tại khoản 1 Điều 34, khoản 2 Điều 34") là một nhóm HOẶC; dẫn chiếu sau "không đúng" không
    biên dịch (applies_ không diễn đạt được nghĩa vi phạm)."""
    u, t1, t2 = D + "D63.K2", D + "D34.K1", D + "D34.K2"
    a = {u: {"dong": [dict(row("dieu_kien", "khong"), trich=["có vụ việc"]), dict(row("ket_luan", "phai"), trich=["đối thoại"]),
                      _ptr("khoản 1 Điều 34", "D34.K1"), _ptr("khoản 2 Điều 34", "D34.K2")]},
         t1: {"dong": [row("dieu_kien", "khong"), row("ket_luan", "khong")]}, t2: {"dong": [row("dieu_kien", "khong"), row("ket_luan", "khong")]}}
    names = {(u, 0): ("has_case", None), (u, 1): ("dialogue", None), (t1, 0): ("a1", None), (t1, 1): ("h", None), (t2, 0): ("a2", None), (t2, 1): ("h", None)}
    order = {x: i for i, x in enumerate(a)}
    rules, _ = R.compile_units(a, names, {}, order, {}, {u: "khi có vụ việc quy định tại khoản 1 Điều 34, khoản 2 Điều 34 thì phải đối thoại"})
    assert sorted(R.rule_text(r) for r in rules if r["unit"] == u) == ["must_dialogue(X) :- has_case(X), applies_d34_k1(X).",
                                                                     "must_dialogue(X) :- has_case(X), applies_d34_k2(X)."]
    rules, notes = R.compile_units(a, names, {}, order, {}, {u: "khi có vụ việc không đúng quy định tại khoản 1 Điều 34, khoản 2 Điều 34 thì phải đối thoại"})
    assert [R.rule_text(r) for r in rules if r["unit"] == u] == ["must_dialogue(X) :- has_case(X)."] and any("phủ định" in n for n in notes)


def test_rules_pointer_to_list_item_uses_case_group_only():
    """A62: "trường hợp quy định tại điểm a" chỉ là nhóm không kết luận của điểm a (tình huống mà câu dẫn của cha kết luận); câu khác của
    điểm a có kết luận riêng ("Quy chế đánh giá do người sử dụng lao động ban hành", D36.K1.a) không định nghĩa applies_<T>."""
    u, t = D + "D36.K2.a", D + "D36.K1.a"
    a = {u: {"dong": [dict(row("ket_luan", "phai"), trich=["báo trước 45 ngày"]), dict(row("dieu_kien", "khong"), trich=["chấm dứt hợp đồng"]),
                      _ptr("điểm a khoản 1", "D36.K1.a")]},
         t: {"dong": [row("dieu_kien", "khong", "q1"), row("ket_luan", "phai", "q2"), row("dieu_kien", "khong", "q2")]}}
    names = {(u, 0): ("notify_45_days", None), (u, 1): ("terminate_contract", None), (t, 0): ("not_complete_work", None),
             (t, 1): ("issue_assessment_rules", None), (t, 2): ("union_exists", None)}
    texts = {u: "phải báo trước 45 ngày khi chấm dứt hợp đồng theo điểm a khoản 1"}
    rules, _notes = R.compile_units(a, names, {}, {x: i for i, x in enumerate(a)}, {}, texts)
    defs = sorted(R.rule_text(r) for r in rules if r["head"]["atom"] == "applies_d36_k1_a")
    assert defs == ["applies_d36_k1_a(X) :- not_complete_work(X)."], defs


def test_rules_chapeau_condition_pushed_to_list_items():
    """A62 3b: câu dẫn danh sách có vế điều kiện (D145.K1) thì điều kiện đó vào quy tắc của từng mục con, nguồn có cả câu dẫn."""
    u, k = D + "D145.K1", D + "D145.K1.a"
    a = {u: {"dong": [row("dieu_kien", "khong"), {"loai": "bo_qua", "cac_muc_con": "danh_sach"}]}, k: {"dong": [row("ket_luan", "phai")]}}
    rules, _ = R.compile_units(a, {(u, 0): ("employ_under_15", None), (k, 0): ("written_contract", None)}, {}, {u: 0, k: 1})
    assert [(R.rule_text(r), r["source_units"]) for r in rules] == [("must_written_contract(X) :- employ_under_15(X).", [u, k])], rules


def test_rules_scan_isolates_empty_body():
    iso, _ = R.scan([{"id": "r1", "unit": D + "D155", "head": {"atom": "term_max_two_years", "pred": "term_max_two_years", "neg": False}, "body": []}], {})
    assert "r1" in iso


def test_rules_scasp_falsification_d151_d154():
    if not Path(R.SWIPL).exists() and not shutil.which(R.SWIPL):
        print("bỏ qua: không có SWI-Prolog")
        return
    rules, _ = compiled()
    prog = R.program_text(rules)
    cases = {  # sự kiện -> (must_holds_work_permit, -must_holds_work_permit)
        "holds_foreign_nationality(p1). married_to_vietnamese_citizen(p1). resides_in_vietnam(p1).": (True, False),  # miễn (Q04)
        "holds_foreign_nationality(p1).": (False, True),  # không thuộc diện miễn: phải có giấy phép
        "holds_foreign_nationality(p1). married_to_vietnamese_citizen(p1).": (False, True),  # thiếu một vế AND: vẫn phải có
        "married_to_vietnamese_citizen(p1).": (False, False),  # không phải người nước ngoài: không kết luận gì
    }
    with tempfile.TemporaryDirectory() as d:
        for facts, (exempt, must) in cases.items():
            f = Path(d) / "t.pl"
            f.write_text(prog + facts + "\n", encoding="utf-8")
            got = []
            for q in ("-must_holds_work_permit(p1)", "must_holds_work_permit(p1)"):
                goal = f"consult('{f.as_posix()}'), (scasp({q},[model(_)])->write(yes);write(no)),nl,halt"
                out = subprocess.run([R.SWIPL, "-q", "-g", goal], capture_output=True, text=True, encoding="utf-8").stdout.strip().splitlines()
                got.append(out[-1] == "yes" if out else None)
            assert got == [exempt, must], (facts, got)


def test_rules_block_alias_not_applicable_equals_negated_description():
    """A43: quy định miễn ghi "-P" (mô tả + phủ định) ở văn bản khác chặn được quy tắc gốc mà cây con nguồn ghi not_applicable_P."""
    rules, _ = compiled()
    rules.append({"id": "rN", "unit": "ND_X.D7.K8", "head": {"atom": "subject_to_work_permit_issuance", "pred": "subject_to_work_permit_issuance", "neg": True},
                  "body": [{"atom": "short_stay", "pred": "short_stay", "naf": False}], "how": "compiled", "source_units": ["ND_X.D7.K8"]})
    for r in rules:
        r["body"] = [x for x in r["body"] if x["atom"] != "blocked"]
    R.apply_blocks(rules, {(D + "D154", D + "D151.K1.d"): "1.5"}, alias=True)
    d = next(r for r in rules if r["unit"] == D + "D151.K1.d")
    blk = next(x for x in d["body"] if x["atom"] == "blocked")["blocked_by"]
    assert "-subject_to_work_permit_issuance" in blk and "not_applicable_subject_to_work_permit_issuance" in blk, blk
    for r in rules:
        r["body"] = [x for x in r["body"] if x["atom"] != "blocked"]
    R.apply_blocks(rules, {(D + "D154", D + "D151.K1.d"): "1.5"}, alias=False)
    blk = next(x for x in d["body"] if x["atom"] == "blocked")["blocked_by"]
    assert blk == ["not_applicable_subject_to_work_permit_issuance"], blk


_harness.run(globals())
