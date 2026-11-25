"""Test máy kiểm, gold và lời nhắc của lượt 2 (clause_roles.py, A61). Không gọi LLM.

Ví dụ trong lời nhắc phải qua đúng máy kiểm mà đầu ra LLM phải qua (mục 10.4); gold cũng vậy. Ví dụ không qua nghĩa là lời nhắc,
đặc tả và máy kiểm mâu thuẫn nhau."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import _harness  # noqa: E402
import clause_roles  # noqa: E402
import segments  # noqa: E402

B = "BLLD_45-2019."
_C = {}


def data():
    if "d" not in _C:
        _C["d"] = clause_roles.unit_sentences()
    return _C["d"]


def m(i, chu):
    return {"id": i, "loai": "menh_de", "chu": chu}


def c(i, chu, ap):
    return {"id": i, "loai": "dung_chung", "chu": chu, "ap_cho": ap}


# Đoạn lượt 1 của các đơn vị ví dụ trong lời nhắc (viết theo quy ước mục 9.3, phải qua máy kiểm lượt 1).
VI_DU_LUOT1 = {
    "D113.K4": [[c("c1", "Người sử dụng lao động", ["m1", "m2", "m3"]), m("m1", "có trách nhiệm quy định lịch nghỉ hằng năm"),
                 m("m2", "tham khảo ý kiến của người lao động"), m("m3", "phải thông báo trước cho người lao động biết")],
                [c("c1", "Người lao động", ["m1", "m2", "m3"]), m("m1", "có thể thỏa thuận với người sử dụng lao động"),
                 m("m2", "nghỉ hằng năm thành nhiều lần"), m("m3", "nghỉ gộp tối đa 03 năm một lần")]],
    "D53.K2": [[m("m1", "Bên thuê lại lao động được sử dụng lao động thuê lại trong trường hợp sau đây")]],
    "D53.K2.a": [[m("m1", "Đáp ứng tạm thời sự gia tăng đột ngột về nhu cầu sử dụng lao động trong khoảng thời gian nhất định")]],
    "D176.K1": [[m("m1", "Thành viên ban lãnh đạo của tổ chức đại diện người lao động tại cơ sở có quyền sau đây")]],
    "D18.K1": [[m("m1", "Người lao động trực tiếp giao kết hợp đồng lao động")]],
    "D80.K2": [[m("m1", "thỏa ước lao động tập thể doanh nghiệp hết hiệu lực do người sử dụng lao động chấm dứt hoạt động"),
                m("m2", "quyền lợi của người lao động được giải quyết theo quy định của pháp luật")]],
}


def build(short, luot1):
    """(ctx, segmap) của một đơn vị với đoạn lượt 1 cho sẵn (mỗi câu một danh sách đoạn)."""
    ctxs, sents = data()
    u = B + short
    doan = {p["sid"]: clause_roles.gold_segments(p, d) for p, d in zip(sents[u], luot1)}
    assert len(doan) == len(sents[u]), u
    _msg, segmap, hong = clause_roles.unit_input(u, ctxs[u], sents[u], doan)
    assert hong == 0
    return ctxs[u], segmap


def vi_du():
    """{unit_id: đầu ra} của các ví dụ trong lời nhắc."""
    return {o["unit_id"]: o for o in (json.loads(line) for line in clause_roles.SYSTEM.splitlines() if line.startswith('{"unit_id"'))}


def test_clause_roles_vi_du_loi_nhac_qua_may_kiem():
    out = vi_du()
    assert sorted(out) == sorted(B + u for u in VI_DU_LUOT1)
    for short, luot1 in VI_DU_LUOT1.items():
        ctx, segmap = build(short, luot1)
        _rows, err, _flag, _ng = clause_roles.check(ctx, segmap, out[B + short])
        assert err == [], (short, err)


def test_clause_roles_vi_du_khong_tu_dieu_gold():
    gold_dieu = {u["unit_id"].split(".")[1] for bo in clause_roles.GOLD for u in json.loads(clause_roles.GOLD[bo].read_text(encoding="utf-8"))["don_vi"]}
    gold_dieu |= {c["sid"].split(".")[1].split("#")[0] for bo in ("dev", "test") for c in segments._gold(bo)["cau"]}
    assert not {u.split(".")[0] for u in clause_roles.EXAMPLE_UNITS} & gold_dieu
    assert {u.split(".", 1)[1] for u in vi_du()} == set(clause_roles.EXAMPLE_UNITS)


_CHUNG = {"người sử dụng lao động", "người lao động", "trường hợp sau đây", "trong trường hợp sau đây", "tổ chức đại diện người lao động",
          "trong thời hạn", "trong thời gian", "theo quy định của pháp luật", "giao kết hợp đồng lao động", "hợp đồng lao động",
          "không được", "không phải", "có thể", "có quyền", "có trách nhiệm", "người sử dụng lao động", "có các quyền sau đây",
          "theo quy định của", "thỏa thuận với người sử dụng lao động", "khoản 2 điều này", "không cần", "đối với x", "trong quá trình"}


def test_clause_roles_loi_nhac_khong_lo_chu_gold():
    # Như lượt 1: mẩu chữ từ 3 chữ trở lên trong lời nhắc trùng chữ một đơn vị gold là lộ đơn vị đo.
    ctxs, _sents = data()
    gold = [ctxs[u["unit_id"]]["text"].lower() for bo in clause_roles.GOLD for u in json.loads(clause_roles.GOLD[bo].read_text(encoding="utf-8"))["don_vi"]]
    lo = []
    for frag in re.findall(r'"([^"]+)"', clause_roles.SYSTEM):
        for piece in re.split(r"\.\.\.|\||<[^>]*>", frag):
            piece = piece.strip(" ,.;:").lower()
            if len(piece.split()) >= 3 and piece not in _CHUNG and any(piece in g for g in gold):
                lo.append(piece)
    assert not lo, sorted(set(lo))


def test_clause_roles_gold_qua_may_kiem():
    for bo, path in clause_roles.GOLD.items():
        gold = {u["unit_id"]: u["dau_ra"] for u in json.loads(path.read_text(encoding="utf-8"))["don_vi"]}
        assert len(gold) == {"dev": 36, "test": 20}[bo]
        for u, ctx, _msg, segmap in clause_roles.inputs(bo):
            _rows, err, _flag, _ng = clause_roles.check(ctx, segmap, gold[u])
            assert err == [], (u, err)


def test_clause_roles_may_kiem_bat_loi():
    ctx, segmap = build("D18.K1", VI_DU_LUOT1["D18.K1"])
    tot = vi_du()[B + "D18.K1"]
    row = tot["dong"][0]

    def loi(out):
        return [msg for _i, msg in clause_roles.check(ctx, segmap, out)[1]]
    assert any("không phải id đoạn menh_de" in x for x in loi({**tot, "dong": [{**row, "nguon": "s1.m9"}]}))
    assert any("không nằm trọn" in x for x in loi({**tot, "dong": [{**row, "doan": ["khoản 2 Điều này"]}, row]}))
    assert any("không có dòng" in x for x in loi({**tot, "dong": []}))
    assert any("doi_so sai khuôn" in x for x in loi({**tot, "dong": [{**row, "doi_so": [{"loai": ["W", "E"]}]}]}))
    assert any("vắng ở ngoai_le" in x for x in loi({k: v for k, v in tot.items() if k != "ngoai_le"}))
    # Câu dẫn chỉ được miễn dòng khi danh sách là tân ngữ (danh_sach); va/hoac thì câu dẫn vẫn ra một ket_luan.
    ctx2, segmap2 = build("D176.K1", VI_DU_LUOT1["D176.K1"])
    assert clause_roles.check(ctx2, segmap2, {"unit_id": B + "D176.K1", "cac_muc_con": "danh_sach", "dong": []})[1] == []
    assert clause_roles.check(ctx2, segmap2, {"unit_id": B + "D176.K1", "cac_muc_con": "hoac", "dong": []})[1]


def test_clause_roles_cau_luot1_hong_thanh_mot_doan():
    ctxs, sents = data()
    u = B + "D18.K1"
    _msg, segmap, hong = clause_roles.unit_input(u, ctxs[u], sents[u], {})
    assert hong == 1 and list(segmap) == ["s1.m1"]
    assert segmap["s1.m1"]["chu"] in ctxs[u]["text"]


def test_clause_roles_cham_ghep_va_cau_truc():
    gold = vi_du()[B + "D113.K4"]
    s = clause_roles.score_unit(gold, gold)
    assert s["m"] == s["g"] == s["x"] == 6 and s["cau_truc"] and not s["lech"]
    doi = json.loads(json.dumps(gold))
    doi["dong"][2]["quy_tac"] = "q9"  # tách s1.m3 khỏi nhóm của s2: sai cấu trúc
    doi["dong"][0]["vai"] = "dieu_kien"
    s = clause_roles.score_unit(gold, doi)
    assert not s["cau_truc"] and s["vai"] == 5
    assert clause_roles.score_unit(gold, None)["m"] == 0


def test_clause_roles_gold_bo_ngu_dung_chung_lay_menh_de_dau():
    # Luật 1: dòng lấy chữ từ dung_chung có nguon là mệnh đề đầu tiên trong ap_cho thuộc quy tắc của dòng (để ghép theo nguon tất định).
    for bo, path in clause_roles.GOLD.items():
        gold = {u["unit_id"]: u["dau_ra"] for u in json.loads(path.read_text(encoding="utf-8"))["don_vi"]}
        for u, _ctx, _msg, segmap in clause_roles.inputs(bo):
            dong = gold[u]["dong"]
            for r in dong:
                if any(x in segmap[r["nguon"]]["chu"] for x in r["doan"]):
                    continue
                dc = next(s for s in segmap.values() if s["loai"] == "dung_chung" and r["doan"][0] in s["chu"])
                trong_qt = [x for x in dc["ap_cho"] if any(o["nguon"] == x and o["quy_tac"] == r["quy_tac"] for o in dong)]
                assert r["nguon"] == trong_qt[0], (u, r)


def test_clause_roles_cham_dong_lap_khong_ghep_cheo():
    # D97.K3: điều kiện "hưởng lương theo sản phẩm" lặp ở q1 và q2; LLM viết khối q2 trước q1 vẫn phải đúng cấu trúc.
    gold = {u["unit_id"]: u["dau_ra"] for u in json.loads(clause_roles.GOLD["test"].read_text(encoding="utf-8"))["don_vi"]}[B + "D97.K3"]
    dong = gold["dong"]
    dao = {**gold, "dong": [r for r in dong if r["quy_tac"] == "q2"] + [r for r in dong if r["quy_tac"] == "q1"]}
    s = clause_roles.score_unit(gold, dao)
    assert s["cau_truc"] and s["m"] == len(dong), s


def _lk_row(vai, menh_de, liet_ke, trich=None, nhom_hoac=None):
    return {"loai": "menh_de", "vai": vai, "menh_de": menh_de, "liet_ke": liet_ke, "trich": trich or [menh_de], "nhom_hoac": nhom_hoac, "quy_tac": "q1"}


def test_trai_liet_ke_ket_luan_va_dieu_kien():
    """A61: kết luận nối phẩy/"và" thành nhiều kết luận; điều kiện nối phẩy hay "hoặc" thành một nhóm HOẶC; lõi chỉ là phần đầu thì nối mục vào sau,
    chữ nối dò trên chữ đơn vị khi trich không có mục (khuôn gọn)."""
    rows = [_lk_row("ket_luan", "đóng", ["bảo hiểm xã hội", "bảo hiểm y tế", "bảo hiểm thất nghiệp"], trich=["đóng"]),
            _lk_row("dieu_kien", "làm hư hỏng dụng cụ, thiết bị, tài sản của người sử dụng lao động", ["dụng cụ", "thiết bị", "tài sản"]),
            _lk_row("dieu_kien", "khác", [])]
    out, flags = clause_roles.trai_liet_ke("X.D1", rows, "phải trả tiền lương, đóng bảo hiểm xã hội, bảo hiểm y tế, bảo hiểm thất nghiệp")
    assert [r["menh_de"] for r in out] == ["đóng bảo hiểm xã hội", "đóng bảo hiểm y tế", "đóng bảo hiểm thất nghiệp",
                                           "làm hư hỏng dụng cụ của người sử dụng lao động", "làm hư hỏng thiết bị của người sử dụng lao động",
                                           "làm hư hỏng tài sản của người sử dụng lao động", "khác"], out
    assert [r["nhom_hoac"] for r in out[:3]] == [None] * 3 and {r["nhom_hoac"] for r in out[3:6]} == {"lk1"}
    assert all(r["liet_ke"] == [] for r in out[:6]) and len(flags) == 2


def test_trai_liet_ke_giu_khi_khong_chac():
    """Giữ nguyên (gắn cờ): kết luận nối "hoặc"; điều kiện nối "và"; chữ nối không rõ; ca user duyệt giữ. Nhóm HOẶC sẵn có được dùng lại."""
    giu = [_lk_row("ket_luan", "trả A, B hoặc C", ["A", "B", "C"]),
           _lk_row("dieu_kien", "đang nghỉ hằng năm, nghỉ việc riêng và trường hợp nghỉ khác", ["hằng năm", "nghỉ việc riêng", "trường hợp nghỉ khác"]),
           _lk_row("dieu_kien", "có X Y", ["X", "Y"], trich=["có X Y"])]
    out, flags = clause_roles.trai_liet_ke("X.D1", giu)
    assert out == giu and all("giữ nguyên" in m for _, m in flags) and len(flags) == 3, flags
    out, flags = clause_roles.trai_liet_ke("BLLD_45-2019.D3.K1", [_lk_row("dieu_kien", "chịu sự quản lý, điều hành, giám sát", ["quản lý", "điều hành", "giám sát"])])
    assert len(out) == 1 and "user duyệt giữ" in flags[0][1]
    out, _ = clause_roles.trai_liet_ke("X.D1", [_lk_row("dieu_kien", "có hành vi ngược đãi, quấy rối", ["ngược đãi", "quấy rối"], nhom_hoac="h1"),
                                                _lk_row("dieu_kien", "đang nghỉ", ["nghỉ việc riêng", "nghỉ ốm"], trich=["đang nghỉ"])],
                                        "có hành vi ngược đãi, quấy rối; đang nghỉ việc riêng hoặc nghỉ ốm")
    assert [(r["menh_de"], r["nhom_hoac"]) for r in out] == [("có hành vi ngược đãi", "h1"), ("có hành vi quấy rối", "h1"),
                                                             ("đang nghỉ việc riêng", "lk1"), ("đang nghỉ ốm", "lk1")], out


def test_trai_liet_ke_khong_lap_duoi():
    """A62: mục viết hoa ở đầu lõi đã hạ chữ (D147.K2.a) vẫn khớp; lõi chỉ chứa một phần danh sách thì giữ nguyên, không nối mục vào đuôi."""
    row = _lk_row("dieu_kien", "dưới nước, dưới lòng đất, trong hang động", ["Dưới nước", "dưới lòng đất", "trong hang động"])
    out, _ = clause_roles.trai_liet_ke("X.D1", [row], "Dưới nước, dưới lòng đất, trong hang động")
    assert [r["menh_de"] for r in out] == ["dưới nước", "dưới lòng đất", "trong hang động"], out
    row = _lk_row("dieu_kien", "tên, địa chỉ của người sử dụng lao động", ["tên", "địa chỉ", "họ tên"], trich=["tên, địa chỉ, họ tên"])
    out, flags = clause_roles.trai_liet_ke("X.D1", [row], "tên, địa chỉ, họ tên")
    assert out == [row] and "không khớp đủ mục" in flags[0][1], (out, flags)


def test_trai_liet_ke_giu_thuat_ngu_co_dinh():
    """A62: danh sách mà cả cụm lặp nguyên văn ở >= 3 Điều là một thuật ngữ, không trải."""
    row = _lk_row("dieu_kien", "làm công việc nặng nhọc, độc hại, nguy hiểm", ["nặng nhọc", "độc hại", "nguy hiểm"])
    out, flags = clause_roles.trai_liet_ke("X.D1", [row], "", lambda cum: 6 if cum == "nặng nhọc, độc hại, nguy hiểm" else 0)
    assert out == [row] and "thuật ngữ cố định" in flags[0][1], flags
    out, _ = clause_roles.trai_liet_ke("X.D1", [row], "", lambda cum: 1)
    assert len(out) == 3


def test_bo_dong_chi_dan_chieu():
    """A62: bỏ điều kiện chỉ là chữ dẫn chiếu trong Bộ luật; giữ dẫn chiếu ra luật khác và câu có nội dung; kết luận thì giữ, gắn cờ."""
    mk = lambda vai, s: {"loai": "menh_de", "vai": vai, "menh_de": s}  # noqa: E731
    rows = [mk("dieu_kien", "theo quy định của Bộ luật này"), mk("dieu_kien", "theo quy định tại"),
            mk("dieu_kien", "quy định tại Mục 1 Chương XI của Bộ luật này"), mk("dieu_kien", "theo quy định của pháp luật về bảo hiểm xã hội"),
            mk("dieu_kien", "sau thời hạn quy định tại"), mk("ket_luan", "theo quy định của Bộ luật này"), {"loai": "con_tro", "vai": "dieu_kien"},
            mk("dieu_kien", "theo quy định của điều ước quốc tế mà nước Cộng hòa xã hội chủ nghĩa Việt Nam là thành viên")]
    out, flags = clause_roles.bo_dong_chi_dan_chieu(rows)
    assert out == rows[3:], out
    assert sum(m.startswith("bỏ dòng") for _, m in flags) == 3 and len(flags) == 4, flags


def test_ket_luan_tu_tieu_de():
    """A62 3a: hai dạng tiêu đề; mô tả trong khoản thành điều kiện (nhiều dòng thì HOẶC); chỉ áp khi không có câu dẫn."""
    assert clause_roles.ket_luan_tu_tieu_de("Các trường hợp chấm dứt hợp đồng lao động")[:3] == ("chấm dứt hợp đồng lao động", "khong", None)
    m, mode, chu, _ = clause_roles.ket_luan_tu_tieu_de("Trường hợp người sử dụng lao động không được thực hiện quyền đơn phương chấm dứt hợp đồng lao động")
    assert (m, mode, chu["loai"]) == ("thực hiện quyền đơn phương chấm dứt hợp đồng lao động", "cam", "E")
    m, mode, chu, _ = clause_roles.ket_luan_tu_tieu_de("Người lao động nước ngoài làm việc tại Việt Nam không thuộc diện cấp giấy phép lao động")
    assert (m, mode, chu["loai"]) == ("cấp giấy phép lao động", "khong_ap_dung", "W")
    assert clause_roles.ket_luan_tu_tieu_de("Tiền lương ngừng việc") is None
    mk = lambda vai, s, mode="khong": {"loai": "menh_de", "vai": vai, "menh_de": s, "phuong_thuc": mode, "quy_tac": "q1", "nhom_hoac": None}  # noqa: E731
    ctx = {"heading": "Các trường hợp chấm dứt hợp đồng lao động", "chapeau": "", "text": "Người lao động chết hoặc bị tuyên bố mất tích."}
    out, _ = clause_roles.them_ket_luan_tieu_de(ctx, [mk("ket_luan", "người lao động chết"), mk("ket_luan", "bị tuyên bố mất tích")])
    assert [(r["vai"], r["menh_de"], r["nhom_hoac"]) for r in out] == [("dieu_kien", "người lao động chết", "tdq1"),
                                                                      ("dieu_kien", "bị tuyên bố mất tích", "tdq1"),
                                                                      ("ket_luan", "chấm dứt hợp đồng lao động", None)], out
    out, _ = clause_roles.them_ket_luan_tieu_de(dict(ctx, text="Vào Việt Nam dưới 03 tháng để chào bán dịch vụ."),
                                                [mk("ket_luan", "vào Việt Nam dưới 03 tháng"), mk("ket_luan", "chào bán dịch vụ")])
    assert [r["nhom_hoac"] for r in out] == [None, None, None], out  # nối "để": VÀ
    out, _ = clause_roles.them_ket_luan_tieu_de(dict(ctx, chapeau="Người sử dụng lao động có quyền ... sau đây:"), [mk("ket_luan", "x")])
    assert out[0]["vai"] == "ket_luan" and len(out) == 1
    out, _ = clause_roles.them_ket_luan_tieu_de(ctx, [mk("ket_luan", "phải trả", "phai"), mk("dieu_kien", "khi y")])
    assert len(out) == 2  # nhóm đã có kết luận có phương thức: không thêm


if __name__ == "__main__":
    _harness.run(globals())
