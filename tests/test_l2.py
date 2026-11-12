"""Test L2: tách cụm dẫn chiếu, đích, đuôi văn bản, chọn BLLĐ 2012/2019, nhận diện dòng chỉ thị; và cổng trên cả kho."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import _harness  # noqa: E402
import parse as l1  # noqa: E402
import refs as l2  # noqa: E402
import corpus  # noqa: E402


def refs(text):
    return l2.find_refs("D.D1", text)


def test_list_of_numbers_and_this():
    r = refs("theo khoản 1, 2 và 3 Điều này")
    assert len(r) == 1 and r[0].items == [(1, ["1", "2", "3"]), (0, ["này"])]


def test_chain_split_after_this_and_new_dieu():
    r = refs("khoản 8 Điều này, Điều 24 Nghị định này")
    assert [x.items for x in r] == [[(1, ["8"]), (0, ["này"])], [(0, ["24"])]]
    assert r[1].tail is not None and r[1].tail.self_ref
    r = refs("điểm e, g, h khoản 2 Điều 7 và Điều 14 của Nghị định này")
    assert [x.items for x in r] == [[(2, ["e", "g", "h"]), (1, ["2"]), (0, ["7"])], [(0, ["14"])]]


def test_three_refs_share_one_tail():
    r = refs("khoản 2 Điều 18, điểm a khoản 1 Điều 145 và khoản 1 Điều 162 của Bộ luật này")
    assert len(r) == 3 and all(x.tail is not None and x.tail.self_ref for x in r)


def test_elided_dieu_shared_by_previous_group():
    r = refs("điểm h khoản 1 và điểm đ khoản 2 Điều này")
    assert len(r) == 2 and r[0].items[-1] == (0, ["này"]) and r[1].items[-1] == (0, ["này"])


def test_semicolon_and_cua_between_items():
    r = refs("Các điểm a, b khoản 1 Điều 8; khoản 3 Điều 9 và khoản 2 Điều 12 của Nghị định số 33/2016/NĐ-CP ngày 10 tháng 5 năm 2016")
    assert len(r) == 3 and r[0].tail.number == "33/2016/NĐ-CP"
    r = refs("sửa đổi khoản 6 của Điều 7")
    assert len(r) == 1 and r[0].items == [(1, ["6"]), (0, ["7"])]


def test_suffix_numbers_and_letter_points():
    r = refs("khoản 8a Điều 154 và điểm a1 khoản 4 Điều 69")
    assert r[0].items == [(1, ["8a"]), (0, ["154"])] and r[1].items[0] == (2, ["a1"])


def test_tail_kinds():
    t = l2.parse_tail("Điều 5 của Bộ luật Lao động ngày 20 tháng 11", len("Điều 5"))
    assert t.name == "Bộ luật Lao động" and not t.self_ref
    t = l2.parse_tail("Điều 154 của Bộ luật Lao động số 45/2019/QH14", len("Điều 154"))
    assert t.number == "45/2019/QH14"
    t = l2.parse_tail("khoản 2 Điều 68 Nghị định số 145/2020/NĐ-CP ngày 14", len("khoản 2 Điều 68"))
    assert t.number == "145/2020/NĐ-CP" and t.kind == "Nghị định"
    assert l2.parse_tail("Điều 5 và Điều 6", len("Điều 5")) is None


def test_tail_name_full_title_not_truncated():
    """A23: tên văn bản không số hiệu lấy đủ các chữ liền nhau, kể cả chữ thường (trước đây 'Luật Bảo', 'Luật Xử')."""
    assert l2.parse_tail("Điều 32 của Luật Bảo hiểm xã hội;", len("Điều 32")).name == "Luật Bảo hiểm xã hội"
    assert l2.parse_tail("khoản 1 Điều 6 của Luật Xử lý vi phạm hành chính.", len("khoản 1 Điều 6")).name == "Luật Xử lý vi phạm hành chính"
    assert l2.parse_tail("Điều 3 của Luật Công đoàn, hoặc", len("Điều 3")).name == "Luật Công đoàn"
    assert l2.parse_tail("Điều 9 của Luật Doanh nghiệp không áp dụng", len("Điều 9")).name == "Luật Doanh nghiệp"
    assert l2.parse_tail("Điều 9 của Luật Bảo hiểm xã hội nhưng chưa đến mức", len("Điều 9")).name == "Luật Bảo hiểm xã hội"
    text = "Điều 4 của Luật An toàn, vệ sinh lao động và Điều 5"
    t = l2.parse_tail(text, len("Điều 4"))
    assert t.name == "Luật An toàn, vệ sinh lao động" and text[:t.end] == "Điều 4 của Luật An toàn, vệ sinh lao động"
    assert l2.parse_tail("Điều 5 của Luật Người lao động Việt Nam đi làm việc ở nước ngoài", len("Điều 5")).name == "Luật Người lao động Việt Nam"


def test_tail_name_must_be_contiguous():
    """A23: chữ hoa đầu câu sau dấu chấm hoặc xuống dòng không dính vào tên ('Bộ luật Lao động Trường' trước đây); tên đã đủ thì không kéo dài."""
    text = "Điều 5 của Bộ luật Lao động.\nTrường hợp khác"
    t = l2.parse_tail(text, len("Điều 5"))
    assert t.name == "Bộ luật Lao động" and text[:t.end] == "Điều 5 của Bộ luật Lao động"
    text = "Điều 5 của Bộ luật Lao động thực hiện đúng"
    t = l2.parse_tail(text, len("Điều 5"))
    assert t.name == "Bộ luật Lao động" and text[:t.end] == "Điều 5 của Bộ luật Lao động"


def test_phu_luc_refs():
    r = refs("theo quy định tại Phụ lục I.7 ban hành kèm theo Nghị quyết này")
    assert r[0].pl == "I_7" and r[0].tail.self_ref
    assert refs("Phụ lục II ban hành kèm theo Nghị định số 152/2020/NĐ-CP")[0].tail.number == "152/2020/NĐ-CP"


def test_chain_targets():
    units = {"D.D5.K2.a": {"id": "D.D5.K2.a", "type": "diem", "parent": "D.D5.K2"},
             "D.D5.K2": {"id": "D.D5.K2", "type": "khoan", "parent": "D.D5"}, "D.D5": {"id": "D.D5", "type": "dieu", "parent": None}}
    runs = l2.merge_runs([(1, ["1", "3"]), (0, ["616"])])
    assert l2.chain_targets("D.D5.K2.a", runs, units, "D")[0] == ["D.D616.K1", "D.D616.K3"]
    assert l2.chain_targets("D.D5.K2.a", [(1, ["này"])], units, "D")[0] == ["D.D5.K2"]
    assert l2.chain_targets("D.D5.K2.a", [(0, ["này"])], units, "D")[0] == ["D.D5"]
    assert l2.chain_targets("D.D5", [(1, ["2"])], units, "D")[0] is None  # khoản không kèm Điều: không đoán
    runs = l2.merge_runs([(2, ["a"]), (1, ["1", "2"]), (0, ["5"])])
    assert l2.chain_targets("D.D5", runs, units, "D")[0] is None  # nhiều đối số ở mục cấp trên


def test_directive_detector_is_strict():
    assert l2.is_directive("Sửa đổi, bổ sung khoản 6 của Điều 7 như sau:")
    assert l2.is_directive("Bãi bỏ điểm c, d, đ khoản 5 và điểm g khoản 6 Điều 30;")
    assert l2.is_directive("Thay thế cụm từ “A” bằng cụm từ “B” tại khoản 1 Điều 5")
    assert l2.is_directive("Bổ sung điểm c khoản 9 Điều 9 như sau:")
    assert not l2.is_directive("Sửa chữa, làm sai lệch văn bản, tài liệu trong hồ sơ")
    assert not l2.is_directive("Thay đổi cơ cấu tổ chức, tổ chức lại lao động;")
    assert not l2.is_directive("Thay thế người lao động trong thời gian nghỉ thai sản")


def test_resolver_blld_year_by_grounds_not_signing_date():
    docs = corpus.load_manifest()
    res = l2.Resolver(docs, l2.load_headers())
    assert res.blld_year(docs["ND_28-2020"]) == 2012, "ký 01/3/2020 sau 20/11/2019 nhưng căn cứ BLLĐ 2012"
    assert res.blld_year(docs["ND_135-2020"]) == 2019, "ký 18/11/2020, căn cứ BLLĐ 2019"
    assert res.blld_year(docs["ND_90-2019"]) == 2012
    assert res.blld_year(docs["TT_10-2020-BLDTBXH"]) == 2019, "mất đầu văn bản: theo ngày hiệu lực"
    tail = l2.DocTail("Bộ luật", False, None, "Bộ luật Lao động", 0)
    assert res.resolve(tail, docs["ND_152-2020"]) == ("doc", "BLLD_45-2019")
    assert res.resolve(tail, docs["ND_28-2020"])[0] == "pending"
    assert res.resolve(l2.DocTail("Nghị định", False, "145/2020/NĐ-CP", None, 0), docs["ND_152-2020"]) == ("doc", "ND_145-2020")
    assert res.resolve(l2.DocTail("Nghị định", False, "38/2022/NĐ-CP", None, 0), docs["ND_74-2024"])[0] == "pending"
    assert res.resolve(l2.DocTail("Nghị định", True, None, None, 0), docs["TT_10-2020-BLDTBXH"])[0] == "error"


def test_gate_all_documents():
    docs, all_units, resolver, available = l2.load_context()
    nonlocal_checked = 0
    for d in docs.values():
        units = all_units[d.doc_id]
        structure = l2.build_structure_edges(units)
        assert not l2.check_structure(units, structure), d.doc_id
        res = l2.extract(d, units, all_units, resolver, available)
        assert not l2.check_refs(d, units, all_units, res), d.doc_id
        nonlocal_checked += len(res.edges)
    assert nonlocal_checked > 2000


def test_nd152_dieu7_refers_to_blld_dieu154():
    docs, all_units, resolver, available = l2.load_context()
    res = l2.extract(docs["ND_152-2020"], all_units["ND_152-2020"], all_units, resolver, available)
    assert any(s.startswith("ND_152-2020.D7") and o.startswith("BLLD_45-2019.D154") for s, _, o, _ in res.edges)


def test_amending_doc_directives_do_not_become_refers_to():
    docs, all_units, resolver, available = l2.load_context()
    res = l2.extract(docs["ND_70-2023"], all_units["ND_70-2023"], all_units, resolver, available)
    assert len(res.skipped_directive) >= 40
    assert not any(s.startswith("ND_70-2023.D1.K") for s, _, _, _ in res.edges), "dẫn chiếu trong chỉ thị trỏ vào văn bản bị sửa, không phải ND_70"


def test_pending_when_target_document_not_loaded():
    docs, all_units, resolver, available = l2.load_context()
    res = l2.extract(docs["ND_74-2024"], all_units["ND_74-2024"], all_units, resolver, available - {"BLLD_45-2019"})
    assert res is not None
    res2 = l2.extract(docs["ND_152-2020"], all_units["ND_152-2020"], all_units, resolver, available - {"BLLD_45-2019"})
    assert res2.pending and all(p["target_number"] == "45/2019/QH14" for p in res2.pending if p["target_name"] is None)


_harness.run(globals())
