"""Test 1.6A bản làm lại (propositions.py, A38): cổng khuôn và nguồn, ví dụ của lời nhắc, đáp án nháp, lô thí điểm,
hộp cát (xuat/nhap) và phép so. Không gọi LLM: đầu ra LLM giả dựng từ chính đáp án."""
import copy
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import _harness  # noqa: E402
import propositions as P  # noqa: E402

B = "BLLD_45-2019."
_C = {}


def ctxs():
    if "c" not in _C:
        _C["c"] = P.contexts("BLLD_45-2019")
    return _C["c"]


def gold():
    if "g" not in _C:
        _C["g"] = P.load_gold()
    return _C["g"]


def row(**kw):
    """Dòng đủ trường với giá trị rỗng, ghi đè bằng kw."""
    r = {"loai": "menh_de", "vai": "", "menh_de": "", "chu_the": None, "doi_so": [], "phuong_thuc": "", "cuc": "",
         "bo_ngu": [], "nhom_hoac": None, "cac_muc_con": None, "chua_ro": [], "trich": [], "targets": [],
         "quy_tac": None, "gan_vao": None, "liet_ke": [], P.LLM_REASON: None}
    r.update(kw)
    return r


def errors(uid, rows, reason=P.LLM_REASON):
    return P.gate_unit(ctxs()[B + uid], rows, reason)[0]


# Các ví dụ viết trong SYSTEM, dựng đủ trường trên ngữ cảnh thật: lời nhắc mà tự trái cổng thì hỏng cả lô (bài học A36).
VI_DU = {
    "D6.K2.a": [row(vai="ket_luan", menh_de="tôn trọng danh dự, nhân phẩm của người lao động",
                    chu_the={"chu": "Người sử dụng lao động", "loai": "E", "nguon": "cau_dan"}, doi_so=[{"loai": "W"}],
                    phuong_thuc="phai", cuc="khang_dinh", quy_tac="q1",
                    trich=["Người sử dụng lao động có các nghĩa vụ", "tôn trọng danh dự, nhân phẩm của người lao động"],
                    ly_do_llm={"ma": "giu_chung", "giai_thich": "Cùng một nghĩa vụ tôn trọng con người."})],
    "D17.K1": [row(vai="ket_luan", menh_de="giữ bản chính giấy tờ tùy thân, văn bằng, chứng chỉ của người lao động",
                   chu_the={"chu": "người sử dụng lao động", "loai": "E", "nguon": "tieu_de"}, doi_so=[{"loai": "W"}],
                   phuong_thuc="cam", cuc="khang_dinh", quy_tac="q1",
                   trich=["Hành vi người sử dụng lao động không được làm", "Giữ bản chính giấy tờ tùy thân, văn bằng, chứng chỉ của người lao động"],
                   ly_do_llm={"ma": "giu_chung", "giai_thich": "Cùng một hành vi bị cấm."})],
    "D40.K1": [row(vai="ket_luan", menh_de="được trợ cấp thôi việc", chu_the={"chu": "người lao động", "loai": "W", "nguon": "tieu_de"},
                   phuong_thuc="khong", cuc="phu_dinh", quy_tac="q1", trich=["Nghĩa vụ của người lao động", "Không được trợ cấp thôi việc"])],
    "D3.K4": [row(vai="dieu_kien", menh_de="được thành lập hợp pháp", chu_the={"chu": "tổ chức", "loai": "?", "nguon": "chinh"},
                  phuong_thuc="khong", cuc="khang_dinh", quy_tac="q1", trich=["là tổ chức được thành lập hợp pháp"]),
              row(vai="dieu_kien", menh_de="đại diện và bảo vệ quyền, lợi ích hợp pháp của người sử dụng lao động",
                  chu_the={"chu": "tổ chức", "loai": "?", "nguon": "chinh"}, phuong_thuc="khong", cuc="khang_dinh", quy_tac="q1",
                  bo_ngu=[{"original_text": "trong quan hệ lao động", "scope": "this_clause"}],
                  trich=["là tổ chức", "đại diện và bảo vệ quyền, lợi ích hợp pháp của người sử dụng lao động"]),
              row(vai="ket_luan", menh_de="là tổ chức đại diện người sử dụng lao động", doi_so=[{"loai": "?"}], phuong_thuc="khong",
                  cuc="khang_dinh", quy_tac="q1", trich=["Tổ chức đại diện người sử dụng lao động là tổ chức"])],
    "D16.K1": [row(vai="ket_luan", menh_de="cung cấp thông tin trung thực", chu_the={"chu": "Người sử dụng lao động", "loai": "E", "nguon": "chinh"},
                   doi_so=[{"loai": "W"}], phuong_thuc="phai", cuc="khang_dinh", quy_tac="q1",
                   liet_ke=["tiền lương", "hình thức trả lương", "bảo hiểm xã hội"],
                   trich=["Người sử dụng lao động phải cung cấp thông tin trung thực cho người lao động"],
                   ly_do_llm={"ma": "giu_chung", "giai_thich": "Một nghĩa vụ thông tin; danh sách nội dung đưa vào liet_ke."})],
    "D6.K2": [row(loai="bo_qua", cac_muc_con="danh_sach", trich=["Người sử dụng lao động có các nghĩa vụ sau đây:"],
                  ly_do_llm={"ma": "cau_dan", "giai_thich": "Câu dẫn danh sách nghĩa vụ."})],
}


def test_vi_du_loi_nhac_qua_cong():
    for uid, rows in VI_DU.items():
        assert errors(uid, rows) == [], (uid, errors(uid, rows))
        for r in rows:
            if r["menh_de"]:
                assert r["menh_de"] in P.SYSTEM, (uid, r["menh_de"])  # ví dụ trong test đúng là ví dụ trong lời nhắc


# Cụm 4 âm tiết được phép trùng giữa lời nhắc và đơn vị thí điểm: công thức pháp lý và danh từ chung, không mang quyết định
# của đáp án. Thêm vào đây phải có lý do; cụm mang nội dung riêng của một đơn vị thí điểm thì sửa lời nhắc, không thêm.
DUOC_TRUNG = ["người sử dụng lao động không được", "người sử dụng lao động có", "sử dụng người lao động", "hợp đồng lao động",
              "người lao động làm việc", "của người lao động", "người lao động không", "trừ trường hợp quy định tại khoản",
              "trừ trường hợp quy định tại điều", "theo quy định của pháp luật", "theo quy định tại", "trong trường hợp sau đây",
              "nghĩa vụ của người lao động", "người sử dụng lao động có các",
              "của người sử dụng lao động", "lợi ích hợp pháp", "quan hệ lao động", "cho người lao động"]


def leaks():
    """Các cửa sổ 4 âm tiết của chữ đơn vị thí điểm (cả câu dẫn, tiêu đề) có trong lời nhắc mà không thuộc DUOC_TRUNG."""
    S = P.syllables(P.SYSTEM)
    grams = {tuple(S[i:i + 4]) for i in range(len(S) - 3)}
    ok = [" ".join(P.syllables(x)) for x in DUOC_TRUNG]
    out = {}
    for uid in gold():
        c = ctxs()[uid]
        t = P.syllables(" ".join((c["heading"], c["chapeau"], c["text"])))
        for i in range(len(t) - 3):
            q = " ".join(t[i:i + 4])
            if tuple(t[i:i + 4]) in grams and not any(q in a for a in ok):
                out.setdefault(q, set()).add(uid.split(".", 1)[1])
    return out


def test_vi_du_khong_lo_dap_an():
    """Không đơn vị thí điểm nào làm ví dụ, và lời nhắc không chứa cụm riêng của chúng (lộ đáp án làm số đo cao giả)."""
    for uid in VI_DU:
        assert B + uid not in gold(), uid
    assert leaks() == {}, leaks()



def test_dap_an_nhap_qua_cong():
    for uid, rows in gold().items():
        err, _ = P.gate_unit(ctxs()[uid], rows, P.GOLD_REASON)
        assert err == [], (uid, err)


# Đơn vị dùng riêng cho test cổng (không phải ví dụ của lời nhắc, không thuộc thí điểm).
CONG = [row(vai="ket_luan", menh_de="báo trước ít nhất 45 ngày", chu_the={"chu": "Người lao động", "loai": "W", "nguon": "cau_dan"},
            doi_so=[{"loai": "D"}], phuong_thuc="phai", cuc="khang_dinh", quy_tac="q1",
            trich=["Người lao động có quyền đơn phương chấm dứt hợp đồng lao động nhưng phải báo trước", "Ít nhất 45 ngày"],
            ly_do_llm={"ma": "ke_thua", "giai_thich": "Vị ngữ kế thừa từ câu dẫn."})]


def test_cong_bat_loi():
    base = CONG
    assert errors("D35.K1.a", base) == []

    def bad(**kw):
        rows = copy.deepcopy(base)
        rows[0].update(kw)
        return errors("D35.K1.a", rows)
    assert any("âm tiết" in m for _, m in bad(menh_de="báo trước ít nhất 30 ngày"))  # chữ không có trong trich
    assert any("câu dẫn" in m for _, m in bad(menh_de="báo trước như sau"))
    assert any("phuong_thuc" in m for _, m in bad(phuong_thuc="nghia_vu"))
    assert any("nguyên văn" in m for _, m in bad(trich=["Người lao động có quyền", "ít nhất 45 ngày làm việc"]))
    assert any("trich không có mẩu" in m for _, m in bad(trich=["Ít nhất 45 ngày báo trước"[:15]]))  # chủ thể từ câu dẫn mà trich không có câu dẫn
    assert any("quy_tac" in m for _, m in bad(quy_tac=None))
    assert any("chu_the" in m for _, m in bad(chu_the={"chu": "Người lao động", "loai": "X", "nguon": "cau_dan"}))
    rows = copy.deepcopy(base)
    del rows[0]["gan_vao"]
    assert any("trường thiếu" in m for _, m in errors("D35.K1.a", rows))
    assert errors("D35.K1.a", []) == [(None, "đơn vị không có dòng nào")]
    # bo_qua thiếu lý do; con_tro không đích không chua_ro; gan_vao trỏ dòng không phải menh_de
    assert any("bo_qua phải có lý do" in m for _, m in errors("D6.K1", [row(loai="bo_qua", trich=["Người sử dụng lao động có các quyền sau đây:"])]))
    ct = row(loai="con_tro", vai="ngoai_le", trich=["Người lao động có quyền"], gan_vao=5)
    m = [x for _, x in errors("D35.K1.a", copy.deepcopy(base) + [ct])]
    assert any("không targets" in x for x in m) and any("gan_vao" in x for x in m)


def test_chu_the_chung_va_co():
    r = copy.deepcopy(VI_DU["D17.K1"])
    r[0]["chu_the"]["loai"] = ["E", "W"]
    assert errors("D17.K1", r) == []
    r[0]["chu_the"]["loai"] = ["E"]  # danh sách một phần tử: phải viết thẳng mã
    assert errors("D17.K1", r) != []
    _, flag = P.gate_unit(ctxs()[B + "D21.K1.a"], gold()[B + "D21.K1.a"], P.GOLD_REASON)
    assert any("dài" in m for _, m in flag)


def test_lo_moi_dieu_mot_lo():
    lots = P.pilot_batches(ctxs(), gold())
    assert sum(map(len, lots)) == len(gold()) == 30
    dieu = [{P.C.dieu_of(c["id"]) for c in lot} for lot in lots]
    assert all(len(s) == 1 for s in dieu)
    assert len(lots) == len({P.C.dieu_of(u) for u in gold()})


def _llm_from_gold():
    """Đầu ra LLM giả = đáp án, đổi tên trường lý do."""
    out = {}
    for uid, rows in gold().items():
        rr = copy.deepcopy(rows)
        for r in rr:
            r[P.LLM_REASON] = r.pop(P.GOLD_REASON)
        out[uid] = rr
    return out


def test_xuat_nhap_so_tron_vong():
    fake = _llm_from_gold()
    with tempfile.TemporaryDirectory() as t:
        d = Path(t) / "hop"
        P.xuat(d, "claude-sonnet-5-5", "xhigh")
        text = (d / "HUONG_DAN.md").read_text(encoding="utf-8") + (d / "system.txt").read_text(encoding="utf-8")
        for w in ("kltn", "pipeline", "cache", "API", "đáp án", "thí điểm", "1.6"):
            assert w not in text, w
        assert "`claude-sonnet-5-5`" in text and "`sonnet`" in text and "`xhigh`" in text and "@" not in text.split("## Model")[1][:300]
        assert P.sandbox_config(d)["model"] == "claude-sonnet-5-5"
        try:
            P.xuat(d)
            assert False, "xuat phải từ chối thư mục có nội dung"
        except SystemExit:
            pass
        lots = P.pilot_batches(ctxs(), gold())
        lines = []
        for n, lot in enumerate(lots, 1):
            data = {"units": [{"unit_id": c["id"], "dong": fake[c["id"]]} for c in lot]}
            (d / "out" / f"{n:03d}.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            lines.append(f"{n:03d}\tclaude-sonnet-5-5")
        lines[0] = f"001\t{P.model()}"  # model của cấu hình chung (Opus), khác model của hộp cát: phải bị từ chối
        (d / "nhat_ky.tsv").write_text("\n".join(lines), encoding="utf-8")
        ra = Path(t) / "llm_output.json"
        bad = P.nhap(d, ra)
        assert [n for n, _ in bad] == [1]  # lô báo model khác bị từ chối
        got = json.loads(ra.read_text(encoding="utf-8"))["units"]
        assert len(got) == 30 - len(lots[0]) and all(not v["loi"] for v in got.values())
        st = P.so(ra, Path(t) / "so.md")
        assert st["thieu"] == st["thua"] == 0 and st["khop"] == st["x"]
        assert all(st["field_khop"][f] == st["field_n"][f] for f in st["field_n"])
        rep = (Path(t) / "so.md").read_text(encoding="utf-8")
        assert "LLM chưa có" in rep  # các đơn vị của lô bị từ chối hiện ra là thiếu


def test_so_bat_lech():
    g = gold()[B + "D24.K3"]
    x = _llm_from_gold()[B + "D24.K3"]
    x[0]["phuong_thuc"] = "cam"
    pairs, miss, extra = P.match_rows(g, x)
    assert miss == extra == [] and len(pairs) == 2
    assert ("phuong_thuc", "khong_ap_dung", "cam") in P.diff_row(g[0], x[0])
    # quy_tac so theo nhóm (đổi tên mã không phải lệch; đổi nhóm là lệch); gan_vao so qua phép ghép
    g = gold()[B + "D129.K1"]
    x = _llm_from_gold()[B + "D129.K1"]
    for r in x:
        r["quy_tac"] = {"q1": "a", "q2": "b"}.get(r["quy_tac"], r["quy_tac"])
    pairs, _, _ = P.match_rows(g, x)
    assert P.diff_unit(g, x, pairs) == {}
    x[2]["quy_tac"] = "b"  # dòng kết luận "bồi thường" chuyển sang quy tắc của đoạn 2
    x[9]["gan_vao"] = 7
    du = P.diff_unit(g, x, P.match_rows(g, x)[0])
    assert any(f == "quy_tac" for f, _, _ in du.get(2, [])) and any(f == "gan_vao" for f, _, _ in du.get(9, []))
    x2 = _llm_from_gold()[B + "D5.K1.a"]
    x2[6]["doi_so"] = [{"loai": "E"}]
    assert any(f == "doi_so" for f, _, _ in P.diff_row(gold()[B + "D5.K1.a"][6], x2[6]))


def test_tat_ca_204_lo_va_tu_choi_loi_nhac_cu():
    lots = P.lots_for("tat_ca", ctxs())
    assert len(lots) == 204 and sum(map(len, lots)) == len(ctxs())  # chia lô như 1.6A cũ (A36: 204 lô)
    with tempfile.TemporaryDirectory() as t:
        d = Path(t) / "hop"
        P.xuat(d, "claude-sonnet-5-5", "xhigh", "thi_diem")
        cfg = json.loads((d / "cau_hinh.json").read_text(encoding="utf-8"))
        cfg["prompt_version"] = "menh-de-0"
        (d / "cau_hinh.json").write_text(json.dumps(cfg), encoding="utf-8")
        try:
            P.nhap(d, Path(t) / "ra.json")
            assert False, "nhap phải từ chối hộp cát dựng với lời nhắc khác"
        except SystemExit:
            pass


def test_bo_truong_rong_va_liet_ke():
    """menh-de-3: LLM được bỏ trường rỗng, máy điền; liet_ke phải nguyên văn; trường lạ vẫn bị bắt."""
    gon = [{"loai": "menh_de", "vai": "ket_luan", "menh_de": "cung cấp thông tin trung thực", "phuong_thuc": "phai", "cuc": "khang_dinh",
            "quy_tac": "q1", "liet_ke": ["tiền lương"], "trich": ["Người sử dụng lao động phải cung cấp thông tin trung thực cho người lao động"]}]
    assert errors("D16.K1", P.normalize(gon)) == []
    gon[0]["liet_ke"] = ["tiền thưởng tết"]
    assert any("liet_ke" in m for _, m in errors("D16.K1", P.normalize(gon)))
    gon[0]["liet_ke"] = []
    gon[0]["la"] = 1
    assert any("thừa" in m for _, m in errors("D16.K1", P.normalize(gon)))
    _, flag = P.gate_unit(ctxs()[B + "D16.K1"], P.normalize([row(vai="ket_luan", menh_de="cung cấp thông tin trung thực cho người lao động về tiền lương, hình thức trả lương, bảo hiểm xã hội", phuong_thuc="phai", cuc="khang_dinh", quy_tac="q1", trich=["Người sử dụng lao động phải cung cấp thông tin trung thực cho người lao động về công việc, địa điểm làm việc, điều kiện làm việc, thời giờ làm việc, thời giờ nghỉ ngơi, an toàn, vệ sinh lao động, tiền lương, hình thức trả lương, bảo hiểm xã hội"])]))
    assert any("dài" in m for _, m in flag)


_harness.run(globals())
