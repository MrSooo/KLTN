"""Test các loại thay đổi KHÔNG có ca thật trong kho (plan loại 12, 16, 19-26), bằng ví dụ tự soạn.

Đây là fixture để kiểm code, không phải dữ liệu thực nghiệm và không trộn vào data/. Luận văn ghi các loại này là "đã cài đặt, chưa có ca
thật để đo". Mỗi test dựng một Store nhỏ rồi gọi đúng hàm của loại đó.
"""
import datetime
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import _harness  # noqa: E402
import l6_versions as l6v  # noqa: E402
import l6_directives as l6  # noqa: E402
import l6_rare as rare  # noqa: E402

D = datetime.date
NOW = D(2026, 1, 1)


def store_with(*ids, doc="T"):
    """Store gồm các mã (loại suy từ đoạn cuối: D.. dieu, K.. khoan, còn lại diem), cha suy từ mã; hiệu lực từ 2021-01-01."""
    s = l6v.Store()
    for uid in ids:
        seg = uid.split(".")[-1]
        typ = "dieu" if seg.startswith("D") and uid.count(".") == 1 else "khoan" if seg.startswith("K") else "diem"
        parent = ".".join(uid.split(".")[:-1]) if uid.count(".") > 1 else None
        s.add(l6v.Ver(uid, 1, typ, seg.lstrip("DK"), None, f"chữ {seg}", parent, D(2021, 1, 1), None, None, "normal", None, doc))
    return s


def fake_ev():
    return l6.Ev(SimpleNamespace(doc_id="NEW", ngay_hieu_luc=NOW))


def fake_ctx(docs=None):
    return SimpleNamespace(docs=docs or {}, units={}, payloads={})


# ---- 19: hồi tố ----

def test_19_retroactive_sets_applies_from_but_keeps_effective_from():
    s = l6v.Store()
    s.add(l6v.Ver("NEW.D1", 1, "dieu", "1", None, "x", None, NOW, None, None, "normal", None, "NEW"))
    doc, ev = SimpleNamespace(doc_id="NEW"), fake_ev()
    assert rare.retroactive(s, doc, NOW, D(2025, 7, 1), "Nghị định này áp dụng từ ngày 01 tháng 7 năm 2025", ev) is True
    v = s.cur("NEW.D1")
    assert v.applies_from == D(2025, 7, 1) and v.effective_from == NOW and "retroactive" in v.flags and ev.flags["retroactive"] == 1


def test_19_retroactive_that_adds_liability_is_blocked():
    s = l6v.Store()
    s.add(l6v.Ver("NEW.D1", 1, "dieu", "1", None, "x", None, NOW, None, None, "normal", None, "NEW"))
    ev = fake_ev()
    ok = rare.retroactive(s, SimpleNamespace(doc_id="NEW"), NOW, D(2025, 7, 1), "áp dụng từ ngày 01/7/2025, đặt trách nhiệm pháp lý nặng hơn", ev)
    assert ok is False and s.cur("NEW.D1").applies_from is None and ev.flags["retroactive_blocked"] == 1


def test_19_scan_picks_earliest_date_before_effective():
    units = {"NEW.D2.K1": {"id": "NEW.D2.K1", "type": "khoan", "text": "Nghị định này có hiệu lực từ ngày 01 tháng 01 năm 2026 và áp dụng từ ngày 01 tháng 07 năm 2025."}}
    s = store_with("NEW.D2.K1", doc="NEW")
    ev = fake_ev()
    rare.apply_rare(fake_ctx(), s, SimpleNamespace(doc_id="NEW"), units, NOW, ev)
    assert s.cur("NEW.D2.K1").applies_from == D(2025, 7, 1)


def test_19_normal_effective_sentence_is_not_retroactive():
    units = {"NEW.D2.K1": {"id": "NEW.D2.K1", "type": "khoan", "text": "Nghị định này có hiệu lực từ ngày 01 tháng 01 năm 2026."}}
    s = store_with("NEW.D2.K1", doc="NEW")
    rare.apply_rare(fake_ctx(), s, SimpleNamespace(doc_id="NEW"), units, NOW, fake_ev())
    assert s.cur("NEW.D2.K1").applies_from is None


# ---- 20: đính chính ----

def test_20_correction_keeps_both_texts_and_makes_no_version():
    s = store_with("T.D5", "T.D5.K2")
    rare.correct(s, "T.D5.K2", "chữ đã đính chính", D(2026, 3, 1), "DC", "DC.D1")
    assert len(s.vers["T.D5.K2"]) == 1 and s.cur("T.D5.K2").text == "chữ K2", "không tạo phiên bản pháp lý"
    assert s.corrections == [{"id": "T.D5.K2", "version": 1, "text_before": "chữ K2", "text_after": "chữ đã đính chính",
                              "source_event": "DC", "effective": "2026-03-01", "directive": "DC.D1"}]
    assert any(e["p"] == "corrects" and e["o"] == "T.D5.K2" for e in s.edges) and "corrected" in s.cur("T.D5.K2").flags


def test_20_correction_of_missing_unit_is_an_error():
    try:
        rare.correct(store_with("T.D5"), "T.D9.K1", "x", NOW, "DC", "DC.D1")
    except ValueError:
        return
    raise AssertionError("phải lỗi, không đoán")


def test_20_correction_directive_line_with_payload():
    units = {"T.D1.K1": {"id": "T.D1.K1", "type": "khoan", "text": "Đính chính khoản 2 Điều 5 như sau:"}}
    payload = [{"lines": ["“Mức phạt là 5 triệu đồng.”."]}]
    s = store_with("T.D5", "T.D5.K2")
    doc = SimpleNamespace(doc_id="T")
    done = rare.try_directive(fake_ctx(), s, doc, "T.D1.K1", units, units["T.D1.K1"]["text"], payload, None, None, NOW, fake_ev())
    assert done and s.corrections[0]["text_after"] == "Mức phạt là 5 triệu đồng." and len(s.vers["T.D5.K2"]) == 1


# ---- 21: tạm ngưng ----

def test_21_suspension_with_end_returns_to_force_with_old_text():
    s = store_with("T.D5", "T.D5.K1")
    rare.suspend(s, "T.D5", D(2026, 3, 1), D(2026, 9, 1), "SP", "SP.D1")
    k = s.vers["T.D5.K1"]
    assert [(v.state, v.effective_from, v.effective_to) for v in k] == [("normal", D(2021, 1, 1), D(2026, 3, 1)), ("suspended", D(2026, 3, 1), D(2026, 9, 1)),
                                                                           ("normal", D(2026, 9, 1), None)]
    assert k[2].text == k[0].text and k[2].version == 3
    assert k[0].in_force(D(2026, 2, 28)) and not k[1].in_force(D(2026, 5, 1)) and k[2].in_force(D(2026, 9, 1))


def test_21_suspension_without_end_stays_open():
    s = store_with("T.D5")
    rare.suspend(s, "T.D5", D(2026, 3, 1), None, "SP", "SP.D1")
    assert s.cur("T.D5").state == "suspended" and s.cur("T.D5").effective_to is None and not s.cur("T.D5").in_force(D(2030, 1, 1))


def test_21_suspension_sentence_is_scanned():
    units = {"SP.D1.K1": {"id": "SP.D1.K1", "type": "khoan", "text": "Tạm ngưng hiệu lực khoản 1 Điều 5 kể từ ngày 01 tháng 3 năm 2026 đến hết ngày 31 tháng 8 năm 2026."}}
    s = store_with("SP.D5", "SP.D5.K1", "SP.D1", "SP.D1.K1", doc="SP")
    rare.apply_rare(fake_ctx(), s, SimpleNamespace(doc_id="SP"), units, D(2026, 1, 1), fake_ev())
    v = s.vers["SP.D5.K1"]
    assert [x.state for x in v] == ["normal", "suspended", "normal"], "có ngày kết thúc thì hiệu lực trở lại"
    assert v[1].effective_from == D(2026, 3, 1) and v[1].effective_to == D(2026, 9, 1), "đến hết ngày 31/8 thì trở lại từ 01/9"
    assert not v[1].in_force(D(2026, 8, 31)) and v[2].in_force(D(2026, 9, 1))


# ---- 22: đánh số lại ----

def test_22_renumber_closes_old_opens_new_with_old_text():
    s = store_with("T.D5", "T.D5.K3")
    rare.renumber(s, "T.D5.K3", "T.D5.K2", D(2026, 3, 1), "RN", "RN.D1")
    assert s.cur("T.D5.K3").effective_to == D(2026, 3, 1) and s.cur("T.D5.K2").text == "chữ K3" and s.cur("T.D5.K2").effective_from == D(2026, 3, 1)
    assert any(e["p"] == "renumbered_to" and e["s"] == "T.D5.K3" and e["o"] == "T.D5.K2" for e in s.edges)


def test_22_renumber_refuses_existing_target_or_missing_source():
    s = store_with("T.D5", "T.D5.K2", "T.D5.K3")
    for old, new in (("T.D5.K3", "T.D5.K2"), ("T.D5.K9", "T.D5.K8")):
        try:
            rare.renumber(s, old, new, NOW, "RN", "RN.D1")
        except ValueError:
            continue
        raise AssertionError((old, new))


def test_22_renumber_sentence_pattern():
    m = rare.RE_RENUM.match("khoản 3 Điều 5 được đánh số lại thành khoản 2 Điều 5.")
    assert m and m["old"] == "khoản 3 Điều 5" and m["new"] == "khoản 2 Điều 5"
    assert rare.RE_RENUM.match("Khoản 2 trở thành khoản 1.")


# ---- 16: bãi bỏ một phần phụ lục ----

def test_16_repeal_part_of_appendix_closes_only_that_part():
    s = l6v.Store()
    for uid, par in (("T.PLI_7", None), ("T.PLI_7.M1", "T.PLI_7"), ("T.PLI_7.M2", "T.PLI_7"), ("T.PLI_7.M2.R1", "T.PLI_7.M2")):
        s.add(l6v.Ver(uid, 1, "pl", "x", None, "t", par, D(2026, 4, 15), None, None, "normal", None, "T"))
    n = rare.repeal_appendix(s, "T", "Bãi bỏ Mục 2 Phụ lục I.7 ban hành kèm theo Nghị quyết số 66.16/2026/NQ-CP", D(2026, 7, 1), "NQ18", "NQ18.D4")
    assert n == 2 and s.cur("T.PLI_7.M2").effective_to == D(2026, 7, 1) and s.cur("T.PLI_7.M2.R1").effective_to == D(2026, 7, 1)
    assert s.cur("T.PLI_7.M1").effective_to is None and s.cur("T.PLI_7").effective_to is None


# ---- 24: bị bãi bỏ vì trái luật ----

def test_24_annulment_sentence_and_flag():
    assert rare.RE_ANNUL.search("Nghị định số 12/2020/NĐ-CP bị hủy bỏ do trái với Luật")
    assert rare.RE_ANNUL.search("Điều 5 bị bãi bỏ vì trái Hiến pháp")
    assert not rare.RE_ANNUL.search("Nghị định số 12/2020/NĐ-CP hết hiệu lực")
    s = store_with("OLD.D1", doc="OLD")
    ctx = SimpleNamespace(resolver=SimpleNamespace(by_number={"12/2020/NĐ-CP": "OLD"}), units={"OLD": {"OLD.D1": {}}}, unknown=[], docs={})
    ev = fake_ev()
    l6.repeal_one(ctx, s, SimpleNamespace(doc_id="NEW"), "NEW.D1.K1", "Nghị định số 12/2020/NĐ-CP bị hủy bỏ do trái với Luật", D(2026, 5, 1), ev)
    assert s.cur("OLD.D1").effective_to == D(2026, 5, 1) and "annulled" in s.cur("OLD.D1").flags and "doc_replaced" in s.cur("OLD.D1").flags


# ---- 25: văn bản được hướng dẫn bị sửa ----

def test_25_parent_changed_flags_guiding_doc_but_never_closes_it():
    s = store_with("GUIDE.D1", "LAW.D154", doc="x")
    links = [{"s": "GUIDE", "p": "details", "o": "LAW.D154", "how": "regex"}, {"s": "GUIDE", "p": "based_on", "o": "LAW", "how": "regex"},
             {"s": "OTHER", "p": "details", "o": "ELSE.D1", "how": "regex"}]
    out = rare.mark_parent_changed(s, links, {"LAW"}, "AMEND", NOW)
    assert out == [("GUIDE", "LAW")]
    assert [e["p"] for e in s.edges] == ["parent_changed"] and s.edges[0]["s"] == "GUIDE" and s.edges[0]["o"] == "LAW"
    assert s.cur("GUIDE.D1").effective_to is None, "Luật 64 Điều 57 khoản 2: văn bản hướng dẫn tiếp tục có hiệu lực"


def test_25_changed_doc_does_not_flag_itself():
    s = store_with("GUIDE.D1", doc="x")
    assert rare.mark_parent_changed(s, [{"s": "GUIDE", "p": "details", "o": "GUIDE.D1"}], {"GUIDE"}, "GUIDE", NOW) == []


# ---- 26: thay cả văn bản cùng tên ----

def test_26_possible_replacement_flags_same_kind_and_name_without_closing():
    old = SimpleNamespace(doc_id="A", doc_type="nghi_dinh", ten_ngan="Xử phạt VPHC lao động (2020)", ngay_hieu_luc=D(2020, 4, 15), is_consolidation=False)
    new = SimpleNamespace(doc_id="B", doc_type="nghi_dinh", ten_ngan="Xử phạt VPHC lao động (2024)", ngay_hieu_luc=D(2024, 1, 1), is_consolidation=False)
    other = SimpleNamespace(doc_id="C", doc_type="thong_tu", ten_ngan="Xử phạt VPHC lao động (2020)", ngay_hieu_luc=D(2020, 4, 15), is_consolidation=False)
    s = store_with("A.D1", doc="A")
    assert rare.possible_replacement(s, {"A": old, "B": new, "C": other}, new, D(2024, 1, 1)) == ["A"]
    assert s.cur("A.D1").effective_to is None and s.edges[0]["p"] == "possible_replacement"
    s2 = store_with("A.D1", doc="A")
    s2.close("A.D1", D(2023, 1, 1), "X")
    assert rare.possible_replacement(s2, {"A": old, "B": new}, new, D(2024, 1, 1)) == [], "văn bản cũ đã đóng thì không phải ca 26"


# ---- 12: kích hoạt hiệu lực có điều kiện (kho dev chỉ có phía "vẫn chờ"; phía kích hoạt kiểm bằng fixture hư cấu) ----

TRIGGER = "Nghị định quy định về chế độ phụ cấp thử nghiệm (sửa đổi, bổ sung Nghị định số 152/2020/NĐ-CP)"


def pending_store():
    s = l6v.Store()
    s.add(l6v.Ver("LATE.D1", 1, "dieu", "1", None, "x", None, None, None, None, "pending_event", TRIGGER, "LATE"))
    return s


def fake_doc(doc_id="ND_901-2099", loai="Nghị định"):
    return SimpleNamespace(doc_id=doc_id, ngay_hieu_luc=D(2099, 1, 1), loai=loai)


def fake_units(doc_id, d1_text, body=""):
    units = {f"{doc_id}.D1": {"type": "dieu", "heading": "Phạm vi điều chỉnh", "text": d1_text}}
    if body:
        units[f"{doc_id}.D5.K1"] = {"type": "khoan", "heading": None, "text": body}
    return units


def fires(doc, units):
    s, ev = pending_store(), fake_ev()
    l6.check_triggers(fake_ctx(), s, doc, units, D(2099, 1, 1), ev)
    return s.cur("LATE.D1").state == "normal" and ev.triggered == ["LATE.D1"] and s


def test_12_trigger_fires_when_kind_number_and_own_description_all_match():
    s = fires(fake_doc(), fake_units("ND_901-2099", "Nghị định này quy định về chế độ phụ cấp thử nghiệm", "Thực hiện theo Nghị định số 152/2020/NĐ-CP"))
    assert s and s.cur("LATE.D1").effective_from == D(2099, 1, 1)
    assert any(e["p"] == "triggers" and e["o"] == "LATE.D1" for e in s.edges)


def test_12_decree_that_only_cites_the_same_number_stays_pending():
    # đúng ca của ND_219 Điều 35: nhắc số hiệu 152/2020 nhưng Điều 1 nói về việc khác
    units = fake_units("ND_902-2099", "Nghị định này quy định về mức lương tối thiểu", "Nghị định số 152/2020/NĐ-CP hết hiệu lực")
    assert not fires(fake_doc("ND_902-2099"), units)


def test_12_wrong_kind_missing_number_or_vague_description_stay_pending():
    ok_d1, body = "Thông tư này quy định về chế độ phụ cấp thử nghiệm", "Nghị định số 152/2020/NĐ-CP"
    assert not fires(fake_doc(loai="Thông tư"), fake_units("ND_901-2099", ok_d1, body)), "sai loại văn bản"
    assert not fires(fake_doc(), fake_units("ND_901-2099", "Nghị định này quy định về chế độ phụ cấp thử nghiệm")), "thiếu số hiệu"
    s = l6v.Store()
    s.add(l6v.Ver("LATE.D1", 1, "dieu", "1", None, "x", None, None, None, None, "pending_event", "Nghị định mới (152/2020/NĐ-CP)", "LATE"))
    l6.check_triggers(fake_ctx(), s, fake_doc(), fake_units("ND_901-2099", "Nghị định mới", "152/2020/NĐ-CP"), D(2099, 1, 1), fake_ev())
    assert s.cur("LATE.D1").state == "pending_event", "mô tả quá ngắn thì không khớp"


def test_12_description_split_ignores_parent_clause():
    t = "Nghị định sửa đổi, bổ sung một số điều của Nghị định số 189/2025/NĐ-CP ngày 01 tháng 7 năm 2025 của Chính phủ"
    s = l6v.Store()
    s.add(l6v.Ver("LATE.D1", 1, "dieu", "1", None, "x", None, None, None, None, "pending_event", t, "LATE"))
    doc = fake_doc("ND_903-2099")
    l6.check_triggers(fake_ctx(), s, doc, fake_units("ND_903-2099", "Sửa đổi, bổ sung một số điều của Nghị định số 189/2025/NĐ-CP"), D(2099, 1, 1), fake_ev())
    assert s.cur("LATE.D1").state == "normal"
    s2 = l6v.Store()
    s2.add(l6v.Ver("LATE.D1", 1, "dieu", "1", None, "x", None, None, None, None, "pending_event", t, "LATE"))
    l6.check_triggers(fake_ctx(), s2, doc, fake_units("ND_903-2099", "Sửa đổi, bổ sung một số điều của Nghị định số 152/2020/NĐ-CP"), D(2099, 1, 1), fake_ev())
    assert s2.cur("LATE.D1").state == "pending_event", "cùng cụm 'sửa đổi, bổ sung một số điều' nhưng sửa văn bản khác"


_harness.run(globals())
