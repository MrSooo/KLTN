"""Test bước 0 và máy kiểm của lượt 1 (segments.py, A60). Không gọi LLM.

Phần lớn test là các câu ví dụ đã chốt trong đặc tả (docs/design/step_1_6a_propositions.md mục 9.3): cách tách đúng
phải qua máy kiểm, cách tách sai thường gặp ở lần chạy dò seg_thu_3 phải bị bắt. Ví dụ không qua máy kiểm nghĩa là đặc tả
và máy kiểm mâu thuẫn nhau."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import _harness  # noqa: E402
import propositions  # noqa: E402
import segments as S  # noqa: E402

B = "BLLD_45-2019."
_C = {}


def preps():
    if "p" not in _C:
        _C["p"] = {p["sid"]: p for p in S.all_sentences(propositions.contexts("BLLD_45-2019"))}
    return _C["p"]


def m(i, chu):
    return {"id": i, "loai": "menh_de", "chu": chu}


def c(i, chu, ap):
    return {"id": i, "loai": "dung_chung", "chu": chu, "ap_cho": ap}


def errs(sid, doan):
    return S.check(preps()[B + sid], {"doan": doan})[0]


# Cách tách đúng theo đặc tả (mục 9.3 luật 9 ví dụ neo, bảng ví dụ đã gửi user 24/11 sau khi sửa theo luật chủ ngữ dùng chung).
GOLD = {
    "D113.K4#1": [c("c1", "Người sử dụng lao động", ["m1", "m2", "m3"]), m("m1", "có trách nhiệm quy định lịch nghỉ hằng năm"),
                  m("m2", "tham khảo ý kiến của người lao động"), m("m3", "phải thông báo trước cho người lao động biết")],
    "D113.K4#2": [c("c1", "Người lao động", ["m1", "m2", "m3"]), m("m1", "có thể thỏa thuận với người sử dụng lao động"),
                  m("m2", "nghỉ hằng năm thành nhiều lần"), m("m3", "nghỉ gộp tối đa 03 năm một lần")],
    "D85.K2#1": [c("c1", "Doanh nghiệp thành viên của thỏa ước lao động tập thể ngành, thỏa ước lao động tập thể có nhiều doanh nghiệp", ["m1", "m3"]),
                 m("m1", "được rút khỏi thỏa ước lao động tập thể"),
                 m("m2", "có sự đồng thuận của tất cả người sử dụng lao động và tổ chức đại diện người lao động tại doanh nghiệp là thành viên của thỏa ước"),
                 m("m3", "có khó khăn đặc biệt trong hoạt động sản xuất, kinh doanh")],
    "D118.K3#1": [m("m1", "ban hành nội quy lao động"), m("m2", "sửa đổi"), m("m3", "bổ sung"), c("c1", "nội quy lao động", ["m2", "m3"]),
                  m("m4", "người sử dụng lao động phải tham khảo ý kiến của tổ chức đại diện người lao động tại cơ sở đối với nơi có tổ chức đại diện người lao động tại cơ sở")],
    "D61.K4#2": [c("c1", "Người học nghề, người tập nghề", ["m1", "m2"]),
                 m("m1", "thuộc danh mục nghề, công việc nặng nhọc, độc hại, nguy hiểm hoặc đặc biệt nặng nhọc, độc hại, nguy hiểm do Bộ trưởng Bộ Lao động - Thương binh và Xã hội ban hành"),
                 m("m2", "phải từ đủ 18 tuổi trở lên"), m("m3", "lĩnh vực nghệ thuật, thể dục, thể thao")],
    "D69.K2#4": [m("m1", "không thỏa thuận được"),
                 m("m2", "từng tổ chức xác định số lượng đại diện tham gia tương ứng theo số lượng thành viên của tổ chức mình trên tổng số thành viên của các tổ chức")],
    "D137.K1.b#1": [m("m1", "Đang nuôi con dưới 12 tháng tuổi"), m("m2", "được người lao động đồng ý")],
    "D48.K1.d#1": [m("m1", "thiên tai, hỏa hoạn, địch họa hoặc dịch bệnh nguy hiểm")],
    "D36.K1.c#1": [m("m1", "thiên tai, hỏa hoạn, dịch bệnh nguy hiểm, địch họa hoặc di dời, thu hẹp sản xuất, kinh doanh theo yêu cầu của cơ quan nhà nước có thẩm quyền"),
                   c("c1", "người sử dụng lao động", ["m2", "m3"]), m("m2", "đã tìm mọi biện pháp khắc phục"), m("m3", "vẫn buộc phải giảm chỗ làm việc")],
    "D18.K1#1": [m("m1", "Người lao động trực tiếp giao kết hợp đồng lao động")],
    # "do" giữa câu là vị ngữ (mục 9.4), đoạn được mở đầu bằng nó; chỉ "Do" đầu câu (D48.K1.d, D36.K1.c) là chữ nối.
    "D185.K2#1": [c("c1", "Số lượng trọng tài viên lao động của Hội đồng trọng tài lao động", ["m1", "m2", "m3"]),
                  m("m1", "do Chủ tịch Ủy ban nhân dân cấp tỉnh quyết định"), m("m2", "ít nhất là 15 người"),
                  m("m3", "bao gồm số lượng ngang nhau do các bên đề cử, cụ thể như sau")],
}


def test_segments_cat_cau_khop_lan_chay_do():
    # 993 câu như seg_thu_3: cùng cách cắt thì số đo trước và sau so được.
    assert len(preps()) == 993


def test_segments_khoi_e5_thay_bang_dau_giu_cho():
    p = preps()
    co = sorted(k[len(B):] for k, v in p.items() if v["dc"])
    assert len(co) == 13, co  # 14 câu có chữ "trừ (các) trường hợp quy định tại"; D3.K1#2 trỏ Mục/Chương, 1.2 chưa nhận dạng
    assert "D3.K1#2" not in co
    assert p[B + "D14.K2#1"]["dc"]["⟦DC1⟧"] == ("trừ trường hợp quy định tại khoản 2 Điều 18, điểm a khoản 1 Điều 145 và khoản 1 "
                                                 "Điều 162 của Bộ luật này")
    assert p[B + "D45.K1#1"]["dc"]["⟦DC1⟧"].startswith("trừ trường hợp quy định tại các khoản 4, 5, 6, 7 và 8 Điều 34")


def test_segments_don_vi_noi_khop_dai_nhat():
    toks = S.tokens("trừ trường hợp người lao động nghỉ sau khi sinh")
    units = [" ".join(t[0] for t in toks[i:j]) for i, j in S.connector_units(toks)]
    assert units == ["trừ trường hợp", "sau khi"]
    # Luật 7 (b): "trường hợp quy định tại" không phải chữ nối.
    toks = S.tokens("trong trường hợp quy định tại khoản 7")
    assert S.connector_units(toks) == []
    # Luật 7 (a) câu dẫn và mục liệt kê "Trường hợp khác ...": "trường hợp" là danh từ.
    for s in ("đi công tác xa trong trường hợp sau đây", "báo trước trong trường hợp như sau", "Trường hợp khác do hai bên thỏa thuận"):
        assert S.connector_units(S.tokens(s)) == [], s
    # [THÊM] "trong khi" là một đơn vị (D71.K2, D122.K5).
    toks = S.tokens("Trong khi đang giải quyết tranh chấp")
    assert [" ".join(t[0] for t in toks[i:j]) for i, j in S.connector_units(toks)] == ["trong khi"]


def test_segments_vi_du_dac_ta_qua_may_kiem():
    for sid, doan in GOLD.items():
        assert errs(sid, doan) == [], (sid, errs(sid, doan))


def test_segments_gold_qua_may_kiem():
    # Khoá đặc tả, máy kiểm và gold với nhau: sửa một bên mà gold không còn qua là phải xem lại gold (mục 9.6).
    import json
    for path in (S.GOLD_DEV, S.GOLD_TEST):
        doc = json.loads(path.read_text(encoding="utf-8"))
        assert len(doc["cau"]) == {"dev": 40, "test": 20}[doc["bo"]]
        for c in doc["cau"]:
            assert c["doan"], c["sid"]
            e = S.check(preps()[c["sid"]], {"doan": c["doan"]})[0]
            assert e == [], (c["sid"], e)
    dev = {c["sid"].split("#")[0] for c in json.loads(S.GOLD_DEV.read_text(encoding="utf-8"))["cau"]}
    test = {c["sid"].split("#")[0] for c in json.loads(S.GOLD_TEST.read_text(encoding="utf-8"))["cau"]}
    dieu = lambda u: ".".join(u.split(".")[:2])  # noqa: E731
    assert not {dieu(u) for u in dev} & {dieu(u) for u in test}


def test_segments_dung_lai_cho_luot_2():
    p = preps()[B + "D85.K2#1"]
    placed = S.check(p, {"doan": GOLD["D85.K2#1"]})[2]
    assert [d["khe_truoc"] for d in placed] == [[], [], ["khi"], ["trừ trường hợp"]]
    p = preps()[B + "D18.K1#1"]
    out = S.build(p, S.check(p, {"doan": GOLD["D18.K1#1"]})[2])
    assert [d["loai"] for d in out] == ["menh_de", "dan_chieu"]
    assert out[1]["chu"] == "trừ trường hợp quy định tại khoản 2 Điều này"


def test_segments_bat_chu_noi_lam_doan_dung_chung():
    # E2 (D69.K2#4 ở seg_thu_3): "Trường hợp" thành đoạn dùng chung.
    e = errs("D69.K2#4", [c("c1", "Trường hợp", ["m1"]), m("m1", "không thỏa thuận được"), m("m2", GOLD["D69.K2#4"][1]["chu"])])
    assert any("mở đầu bằng chữ nối" in x for x in e), e


def test_segments_bat_doan_dinh_chu_noi_o_cuoi():
    # D113.K4#2 ở seg_thu_3: đoạn dùng chung kết thúc bằng "để".
    e = errs("D113.K4#2", [c("c1", "Người lao động có thể thỏa thuận với người sử dụng lao động để", ["m1", "m2"]),
                           m("m1", "nghỉ hằng năm thành nhiều lần"), m("m2", "nghỉ gộp tối đa 03 năm một lần")])
    assert any("kết thúc bằng chữ nối 'để'" in x for x in e), e


def test_segments_cho_phep_tu_ghep_o_cuoi():
    # "lý do", "các trường hợp" ở cuối đoạn không phải chữ nối dính đoạn.
    p = S.prepare("x#1", "Người lao động có quyền được biết lý do và người sử dụng lao động phải giải thích.", [])
    assert S.check(p, {"doan": [m("m1", "Người lao động có quyền được biết lý do"),
                                m("m2", "người sử dụng lao động phải giải thích")]})[0] == []


def test_segments_bat_cat_ngang_chu_noi_nhieu_chu():
    # E1 (D46.K3 ở seg_thu_3): "... trước" | "khi" | "người lao động thôi việc".
    p = S.prepare("x#1", "Tiền lương bình quân của 06 tháng liền kề trước khi người lao động thôi việc.", [])
    e = S.check(p, {"doan": [m("m1", "Tiền lương bình quân của 06 tháng liền kề trước"), m("m2", "người lao động thôi việc")]})[0]
    assert any("cắt ngang chữ nối 'trước khi'" in x for x in e), e


def test_segments_luat_5d_ve_mo_ta_danh_tu_giu_trong_doan():
    # Luật 7 (d): "mức lương trước khi nghỉ thai sản" là một đoạn; máy kiểm không ép tách.
    p = S.prepare("x#1", "Người sử dụng lao động phải bố trí việc làm khác với mức lương không thấp hơn mức lương trước khi nghỉ thai sản.", [])
    assert S.check(p, {"doan": [m("m1", "Người sử dụng lao động phải bố trí việc làm khác với mức lương không thấp hơn mức lương "
                                        "trước khi nghỉ thai sản")]})[0] == []


def test_segments_bat_cat_ngang_dan_chieu():
    p = preps()[B + "D34.K12#1"]  # "... theo quy định tại Điều 156 của Bộ luật này"
    chu = p["cau_gui"].rstrip(".;")
    cut = chu.index("của Bộ luật này")
    e = S.check(p, {"doan": [m("m1", chu[:cut].strip()), m("m2", chu[cut:])]})[0]
    assert any("cắt ngang dẫn chiếu" in x for x in e), e


def test_segments_bat_bo_chu_va_ap_cho_sai():
    e = errs("D137.K1.b#1", [m("m1", "Đang nuôi con dưới 12 tháng"), m("m2", "được người lao động đồng ý")])
    assert any("không khớp" in x or "bỏ" in x for x in e), e
    e = errs("D113.K4#1", [c("c1", "Người sử dụng lao động", ["m9"])] + GOLD["D113.K4#1"][1:])
    assert any("ap_cho sai" in x for x in e), e
    assert S.check(preps()[B + "D18.K1#1"], {"khac": []})[0] == ["khuôn: thiếu danh sách doan"]


if __name__ == "__main__":
    _harness.run(globals())
