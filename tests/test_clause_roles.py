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


if __name__ == "__main__":
    _harness.run(globals())
