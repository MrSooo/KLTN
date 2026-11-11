"""Test L1: tách đơn vị, khối trích dẫn, phụ lục, chú thích, bảng lương, đầu văn bản; và cổng số Điều trên cả kho."""
import sys
import tempfile
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import _harness  # noqa: E402
import parse as l1  # noqa: E402
import corpus  # noqa: E402

BODY = """Chương I
NHỮNG QUY ĐỊNH CHUNG

Mục 1. GIAO KẾT HỢP ĐỒNG

Điều 154. Các trường hợp người lao động nước ngoài không phải có giấy phép lao động

1. Là chủ sở hữu công ty.

2. Di chuyển trong nội bộ doanh nghiệp.

2a. Nhân lực công nghệ số.

3. Trường hợp khác theo quy định của Chính phủ.

Điều 155. Khoản và điểm

1. Quy định như sau:

a) Điểm thứ nhất;

b) Điểm thứ hai;

c) Điểm thứ ba;

d) Điểm thứ tư;

đ) Điểm năm;

e) Điểm sáu.

Trường hợp khác nữa.

Điều 156. Điểm đứng thẳng dưới Điều

a) Điểm một
b) Điểm hai
"""


def parse(text):
    lines = [l1.normalize_line(l) for l in text.split("\n")]
    return l1.Parser("DOC_X-2020", lines).run()


def ids(p):
    return {u.id: u for u in p.units}


def test_ids_with_suffix_and_dd():
    p = parse(BODY)
    u = ids(p)
    for k in ("DOC_X-2020.CI", "DOC_X-2020.CI.M1", "DOC_X-2020.D154", "DOC_X-2020.D154.K2a", "DOC_X-2020.D155.K1.dd", "DOC_X-2020.D156.a"):
        assert k in u, k
    assert u["DOC_X-2020.D154"].parent == "DOC_X-2020.CI.M1"
    assert u["DOC_X-2020.D155.K1.dd"].number == "đ"
    assert u["DOC_X-2020.D156.a"].parent == "DOC_X-2020.D156", "điểm đứng thẳng dưới Điều"
    assert not p.errors, p.errors


def test_para_after_diem_goes_to_khoan_with_note():
    p = parse(BODY)
    k1 = ids(p)["DOC_X-2020.D155.K1"]
    assert k1.parts[-1] == "Trường hợp khác nữa." and p.notes


def test_numbering_jump_is_reported():
    p = parse("Điều 1. X\n\n1. Một.\n\n3. Ba.\n\nĐiều 5. Y\n")
    reasons = [e.reason for e in p.errors]
    assert any("Khoản 3 sau Khoản 1" in r for r in reasons) and any("Điều 5 sau Điều 1" in r for r in reasons)


def test_chuong_title_next_line_and_wrapped():
    p = parse("Chương IV. HÀNH VI VI PHẠM\n\nVIỆT NAM ĐI LÀM VIỆC\n\nĐiều 1. X\n")
    assert ids(p)["DOC_X-2020.CIV"].heading == "HÀNH VI VI PHẠM VIỆT NAM ĐI LÀM VIỆC"
    p = parse("Chương I\nNHỮNG QUY ĐỊNH CHUNG\n\nĐiều 1. X\n")
    assert ids(p)["DOC_X-2020.CI"].heading == "NHỮNG QUY ĐỊNH CHUNG"


def test_number_with_dots_is_not_khoan():
    p = parse("Điều 3. Mức\n\n1. Quy định:\n\n4.960.000\n\n23.800\n")
    assert [u.id for u in p.units if u.type == "khoan"] == ["DOC_X-2020.D3.K1"]
    assert "4.960.000" in ids(p)["DOC_X-2020.D3.K1"].text


def test_payload_block_is_not_units():
    txt = ("Điều 1. Sửa đổi\n\n1. Sửa đổi, bổ sung khoản 6 Điều 7 như sau:\n\n“6. Được cử sang Việt Nam.\n\na) Điểm trong khối.”.\n\n"
           "2. Bãi bỏ khoản 4 Điều 13.\n")
    p = parse(txt)
    assert [x.payload_id for x in p.payloads] == ["DOC_X-2020.Q1"]
    assert p.payloads[0].lead_unit == "DOC_X-2020.D1.K1" and len(p.payloads[0].lines) == 3
    assert "DOC_X-2020.D1.K1.a" not in ids(p)
    assert "DOC_X-2020.D1.K2" in ids(p)


def test_unclosed_quote_is_an_error():
    p = parse("Điều 1. X\n\n1. Như sau:\n\n“Không đóng nháy\n\nĐiều 2. Y\n")
    assert any("không đóng" in e.reason for e in p.errors)


def test_footer_noi_nhan_is_dropped():
    p = parse("Điều 1. X\n\n1. Nội dung.\n\nNơi nhận:\n- Thủ tướng;\n- Lưu: VT.\n\nTM. CHÍNH PHỦ\n")
    assert ids(p)["DOC_X-2020.D1.K1"].parts == ["Nội dung."]
    assert p.skipped["nơi nhận / chữ ký"] >= 3


def test_footnote_markers_and_zone():
    p = parse("Điều 154. X\n\n8a.[2] Nhân lực chất lượng cao.\n\n[1] Luật số 71/2025/QH15 có căn cứ như sau:\n“Căn cứ”.\n"
              "[2] Khoản này được bổ sung, có hiệu lực kể từ ngày 01 tháng 01 năm 2026.\n")
    k = ids(p)["DOC_X-2020.D154.K8a"]
    assert k.text == "Nhân lực chất lượng cao." and k.fn == [2]
    assert [n for n, _ in p.footnotes] == [1, 2] and "01 tháng 01 năm 2026" in p.footnotes[1][1]


def test_appendix_outline_and_toc_dedupe():
    txt = ("Điều 1. X\n\nPHỤ LỤC I\n\nPhụ lục I.1\nTiêu đề mục lục\n\nPhụ lục I.7\nCẮT GIẢM THỦ TỤC\n\nMục 1\n\nA. LĨNH VỰC CHO THUÊ LẠI\n\n"
           "IX. Thời hạn giải quyết\nDòng nội dung một\n\nPhụ lục I.1\nTIÊU ĐỀ THẬT\nnội dung thật\n")
    lines = [l1.normalize_line(l) for l in txt.split("\n")]
    p = l1.Parser("D", lines).run()
    p.parse_appendices({"I_7"})
    u = {x.id: x for x in p.units}
    assert "D.PLI_7.M1.LA.SIX" in u and u["D.PLI_7.M1.LA.SIX"].parent == "D.PLI_7.M1.LA"
    assert u["D.PLI_1"].scope == "out_of_scope" and p.skipped["mục lục phụ lục"] >= 1
    assert any(x.type == "pl_row" and x.text == "Dòng nội dung một" for x in p.units)


def test_bare_phu_luc_and_kemtheo_implicit():
    p = l1.Parser("D", ["Điều 1. X", "", "PHỤ LỤC", "Danh mục nghề", "(kèm theo Thông tư số 10)", "1. Dòng một"]).run()
    p.parse_appendices(None)
    assert any(x.type == "pl" and x.id == "D.PL_1" for x in p.units)
    p = l1.Parser("D", ["Điều 1. X", "", "DANH MỤC NGHỀ NẶNG NHỌC", "(Kèm theo Thông tư số 11)", "", "I. KHAI THÁC", "dòng a"]).run()
    p.parse_appendices(None)
    assert any(x.type == "pl" for x in p.units) and any(x.type == "pl_row" for x in p.units)


def test_wage_table_rebuilt():
    u = l1.Unit("D.D3.K1", "khoan", "1", None, ["Quy định:", "Vùng", "Mức lương tối thiểu tháng (Đơn vị: đồng/tháng)",
                                                "Mức lương tối thiểu giờ (Đơn vị: đồng/giờ)", "Vùng I", "4.960.000", "23.800",
                                                "Vùng II", "4.410.000", "21.200"], 1)
    t = l1.rebuild_wage_tables([u])
    assert t[0]["rows"] == [{"vung": "I", "muc_thang": 4960000, "muc_gio": 23800}, {"vung": "II", "muc_thang": 4410000, "muc_gio": 21200}]


def test_read_lines_handles_crlf_bom_and_nfc():
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "x.txt"
        f.write_bytes(("\ufeff" + unicodedata.normalize("NFD", "Điều 1. Ủy ban") + "\r\n\r\n1. Nội dung\r\n").encode("utf-8"))
        lines, scan = l1.read_lines(f)
    assert lines[0] == unicodedata.normalize("NFC", "Điều 1. Ủy ban") and scan["bom"] and scan["crlf"] == 3 and scan["dong_chua_nfc"] == 1


def test_numbering_checks():
    assert l1.next_number_ok(None, "5") and l1.next_number_ok("20", "20a") and l1.next_number_ok("20a", "20b") and l1.next_number_ok("20b", "21")
    assert not l1.next_number_ok("20", "22") and not l1.next_number_ok("8", "8b")
    assert l1.next_letter_ok("d", "đ") and l1.next_letter_ok("a", "a1") and not l1.next_letter_ok("a", "c")


def test_all_documents_pass_gate():
    docs = corpus.load_manifest()
    assert len(docs) == 18
    for d in docs.values():
        parsed = l1.parse_document(d)
        assert not parsed.errors, (d.doc_id, parsed.errors[:3])
        assert sum(1 for u in parsed.units if u.type == "dieu") == d.so_dieu


def test_header_flags():
    docs = corpus.load_manifest()
    flags = {d: l1.parse_document(docs[d]).header["flags"] for d in docs}
    for d in ("TT_09-2020-BLDTBXH", "TT_10-2020-BLDTBXH", "TT_11-2020-BLDTBXH"):
        assert "header_from_manifest" in flags[d]
    assert flags["BLLD_45-2019"] == [] and flags["ND_28-2020"] == []


def test_wage_table_nd74_vung_i():
    t = l1.parse_document(corpus.load_manifest()["ND_74-2024"]).tables
    assert t and t[0]["rows"][0] == {"vung": "I", "muc_thang": 4960000, "muc_gio": 23800}


_harness.run(globals())
