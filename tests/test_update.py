"""Test bước 2.5-2.7 (src/affected.py, src/update.py, src/knowledge_units.py) trên kho tổng hợp dựng tay, không đọc dữ liệu thật.

Mục đích chính: 2.7 phải TRƯỢT khi tập ảnh hưởng thiếu quan hệ cần thiết (không thì 2.7 "đạt" không chứng minh gì), và phải đạt với N đầy đủ.
  Ca 1 (exception_of): nghị định nạp sau có cạnh ngoại lệ 1.5 vào một Khoản của luật gốc. Quy tắc của Khoản gốc phải thêm literal chặn ở mốc
       nạp, nên Khoản gốc phải thuộc A(e) dù chữ của nó không đổi.
  Ca 2 (cây): một điểm mới chèn dưới Khoản có câu dẫn "va" (mọi mục con gộp vào một thân): quy tắc cũ của Khoản cha phải đóng.
  Ca 3: KU theo đầu vào 1.6A (cha đổi câu dẫn thì mục con có KU mới); mốc hết thời hạn không có văn bản nạp vẫn là mốc.
"""
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _harness  # noqa: E402
import knowledge_units as K  # noqa: E402
import predicates as Pd  # noqa: E402
import update as U  # noqa: E402

D0, D1 = datetime.date(2021, 1, 1), datetime.date(2022, 1, 1)


def ver(uid, typ, text, parent, frm, to=None, heading=None, source=None, version=1, closed_by=None):
    return {"id": uid, "version": version, "type": typ, "number": "", "heading": heading, "text": text, "parent": parent,
            "effective_from": frm, "effective_to": to, "state": "normal", "source_event": source or uid.split(".")[0], "closed_by": closed_by, "flags": []}


def md(vai, menh_de, mode, quy_tac="q1", subj="Người nước ngoài"):
    r = {"loai": "menh_de", "vai": vai, "menh_de": menh_de, "doi_so": [], "phuong_thuc": mode, "cuc": "khang_dinh", "quy_tac": quy_tac, "trich": [menh_de]}
    if subj:
        r["chu_the"] = {"chu": subj, "loai": "W"}
    return r


class NoAnswers:
    def get(self, *a):
        return None


def knowledge(rows, edges, labels, unit_rows, names, exc15=()):
    kn = object.__new__(K.Knowledge)
    kn.store = K.Store(rows, edges)
    kn.labels = labels
    kn.catalog = K.Catalog(kn.store, labels)
    kn.cache = {}
    for e, at in kn.catalog.at.items():
        for uid, ku in at.items():
            if uid in unit_rows:
                kn.cache[ku] = {"dong": unit_rows[uid], "loi": [], "co": []}
    kn.names = {Pd.word_key(span, params): n for (span, params), n in names.items()}
    kn.surface, kn.word_key, kn._rows = {}, Pd.word_key, {}
    kn.refs, kn.details, kn.node_units = [], [], {}
    kn.exc15 = list(exc15)
    return kn


NAMES = {("có giấy phép", ("W",)): "holds_permit", ("Người nước ngoài", ()): "foreigner", ("kết hôn", ("W",)): "married",
         ("thuộc diện cấp phép", ("W",)): "in_permit_scope", ("nghỉ", ()): "takes_leave", ("ốm", ()): "sick", ("con kết hôn", ()): "child_married"}


def case_exception():
    rows = [ver("TB.D1", "dieu", "", None, "2021-01-01", heading="Giấy phép"),
            ver("TB.D1.K1", "khoan", "Người nước ngoài phải có giấy phép.", "TB.D1", "2021-01-01"),
            ver("TN.D2", "dieu", "", None, "2022-01-01", heading="Miễn giấy phép"),
            ver("TN.D2.K1", "khoan", "Người nước ngoài kết hôn thì không thuộc diện cấp phép.", "TN.D2", "2022-01-01")]
    unit_rows = {"TB.D1.K1": [md("ket_luan", "có giấy phép", "phai")],
                 "TN.D2.K1": [md("dieu_kien", "kết hôn", "khong"), md("ket_luan", "thuộc diện cấp phép", "khong_ap_dung")]}
    return knowledge(rows, [], {"TB.D1": "substantive", "TN.D2": "substantive"}, unit_rows, NAMES, exc15=[("TN.D2.K1", "TB.D1.K1")])


def case_tree():
    rows = [ver("TB.D3", "dieu", "", None, "2021-01-01", heading="Nghỉ"),
            ver("TB.D3.K1", "khoan", "Người lao động được nghỉ khi có đủ các điều kiện sau:", "TB.D3", "2021-01-01"),
            ver("TB.D3.K1.a", "diem", "ốm;", "TB.D3.K1", "2021-01-01"),
            ver("TB.D3.K1.b", "diem", "con kết hôn.", "TB.D3.K1", "2022-01-01", source="TN")]
    lead = {"loai": "bo_qua", "cac_muc_con": "va", "trich": ["khi có đủ các điều kiện sau:"]}
    unit_rows = {"TB.D3.K1": [md("ket_luan", "nghỉ", "duoc", subj=None), lead],
                 "TB.D3.K1.a": [md("dieu_kien", "ốm", "khong", subj=None)],
                 "TB.D3.K1.b": [md("dieu_kien", "con kết hôn", "khong", subj=None)]}
    return knowledge(rows, [], {"TB.D3": "substantive"}, unit_rows, NAMES)


def check(kn, use=None):
    eng = U.Engine(kn, NoAnswers())
    R_full, need = eng.full()
    R_inc, _log, asked = eng.incremental() if use is None else eng.incremental(use)
    return eng, R_inc, U.compare(eng, R_inc, asked, R_full, need, [D0, D1])


def test_update_exception_edge_needs_neighbor():
    eng, R, diffs = check(case_exception())
    assert diffs == [], diffs
    base = [r for r in U.Engine.at(R, D1) if r["unit"] == "TB.D1.K1"]
    assert base and any(x["atom"] == "blocked" and x["blocked_by"] == ["not_applicable_in_permit_scope"] for x in base[0]["body"]), base
    assert not any(x["atom"] == "blocked" for r in U.Engine.at(R, D0) for x in r["body"]), "trước khi nạp nghị định không có chặn"
    _e, _R, cut = check(case_exception(), use=())
    assert any(d["unit"] == "TB.D1.K1" for d in cut), cut
    _e, _R, no_exc = check(case_exception(), use=tuple(x for x in U.affected.RELATIONS if x != "exception_of"))
    assert no_exc, "bỏ exception_of phải làm 2.7 trượt"


def test_update_tree_insert_needs_ancestor():
    eng, R, diffs = check(case_tree())
    assert diffs == [], diffs
    merged = [r for r in U.Engine.at(R, D1) if r["how"] == "compiled_children_and"]
    assert merged and set(merged[0]["source_units"]) == {"TB.D3.K1", "TB.D3.K1.a", "TB.D3.K1.b"}, merged
    _e, _R, no_tree = check(case_tree(), use=tuple(x for x in U.affected.RELATIONS if x != "cay"))
    assert no_tree, "bỏ quan hệ cây phải làm 2.7 trượt"


def test_knowledge_units_ku_by_context_and_term_end():
    rows = [ver("TB.D5", "dieu", "", None, "2021-01-01", heading="Cũ"),
            ver("TB.D5.K1", "khoan", "Câu dẫn cũ:", "TB.D5", "2021-01-01", to="2022-01-01", closed_by="TN"),
            ver("TB.D5.K1", "khoan", "Câu dẫn mới:", "TB.D5", "2022-01-01", version=2, source="TN"),
            ver("TB.D5.K1.a", "diem", "mục a.", "TB.D5.K1", "2021-01-01"),
            ver("TQ.D1", "dieu", "", None, "2022-06-01", to="2023-03-01", heading="Có thời hạn"),
            ver("TQ.D1.K1", "khoan", "Áp dụng thay.", "TQ.D1", "2022-06-01", to="2023-03-01")]
    st = K.Store(rows, [])
    cat = K.Catalog(st, {"TB.D5": "substantive", "TQ.D1": "substantive"})
    assert [str(e) for e in cat.epochs] == ["2021-01-01", "2022-01-01", "2022-06-01", "2023-03-01"]
    a0, a1 = cat.at[cat.epochs[0]]["TB.D5.K1.a"], cat.at[cat.epochs[1]]["TB.D5.K1.a"]
    assert a0 != a1 and a1.startswith("TB.D5.K1.a@h"), "câu dẫn của cha đổi thì mục con có KU mới"
    assert cat.kus[a1]["ctx"]["chapeau"] == "Câu dẫn mới:" and cat.kus[a1]["unit"] == "TB.D5.K1.a"
    assert "TQ.D1.K1" not in cat.at[cat.epochs[3]] and st.source_of(cat.epochs[3]) == ["TQ"]


def test_checks_update_rules_problems_catches_broken_r():
    import checks
    by = {"TB.D1.K1": [{"state": "normal", "effective_from": "2021-01-01", "effective_to": "2022-01-01"},
                       {"state": "normal", "effective_from": "2022-01-01", "effective_to": None}],
          "TN.D2.K1": [{"state": "normal", "effective_from": "2022-01-01", "effective_to": "2023-01-01"}]}
    r = {"id": "r1", "head": {"atom": "p"}, "body": [], "isolated": None}
    ok = [dict(r, source_units=["TB.D1.K1"], valid_from="2021-06-01", valid_to=None)]
    assert checks.update_rules_problems(ok, by) == []
    late = [dict(r, source_units=["TN.D2.K1"], valid_from="2022-01-01", valid_to=None)]  # nguồn hết hiệu lực 2023 mà quy tắc còn mở
    assert checks.update_rules_problems(late, by)
    overlap = [dict(r, source_units=["TB.D1.K1"], valid_from="2021-01-01", valid_to="2022-06-01"),
               dict(r, source_units=["TB.D1.K1"], valid_from="2022-01-01", valid_to=None)]
    assert any("chồng" in x for x in checks.update_rules_problems(overlap, by))


def test_predicate_registry_groups_amended_and_inserted_units_by_dieu():
    """A49: mốc sửa đổi liệt kê đơn vị bị sửa trước, đơn vị chèn sau (D3.K5, D4.K1.a, rồi D3.K5.a): gom theo Điều để make_rounds phủ đủ chữ
    theo thứ tự; thứ tự vốn đã liền theo Điều thì không đổi (khoá lượt đã lưu của mọi mốc khác giữ nguyên)."""
    import concepts_names as cn
    import predicate_registry as R

    def rows(units):
        return [{"unit": u, "loai": "menh_de", "span": f"chữ {u}", "params": [], "role": "dieu_kien"} for u in units]
    mixed = ["NB.D3.K5", "NB.D4.K1.a", "NB.D7.K14", "NB.D3.K5.a", "NB.D4.K1.c", "NB.D7.K14.a"]
    try:
        cn.make_rounds(Pd.build_words(rows(mixed), {u: i for i, u in enumerate(mixed)}))
        raise AssertionError("thứ tự xen Điều phải làm make_rounds dừng (phép kiểm giữ nguyên)")
    except SystemExit:
        pass
    order = R.group_by_dieu(rows(mixed))
    assert sorted(order, key=order.get) == ["NB.D3.K5", "NB.D3.K5.a", "NB.D4.K1.a", "NB.D4.K1.c", "NB.D7.K14", "NB.D7.K14.a"]
    words = Pd.build_words(sorted(rows(mixed), key=lambda r: order[r["unit"]]), order)
    assert [i for r in cn.make_rounds(words) for i in r] == list(range(len(words)))
    contiguous = ["NB.D7.K6", "NB.D7.K14.a", "NB.D7.K14.b", "NB.D8.K2"]
    assert R.group_by_dieu(rows(contiguous)) == {u: i for i, u in enumerate(contiguous)}


if __name__ == "__main__":
    _harness.run(globals())
