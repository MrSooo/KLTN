"""Bước 1.6A-v2, lượt 2 (A59, A61; đặc tả docs/design/step_1_6a_propositions.md mục 10): gán vai, quy tắc, phương thức cho các
đoạn mà lượt 1 (`segments.py`) đã gạch, rồi để máy dựng lại khuôn cũ của 1.6A bằng đúng `propositions.check_unit`.

Vì sao có lượt riêng: lượt 1 chỉ gạch ranh giới; ở đây LLM ghi khuôn gọn `menh-de-12` (mục 3.1) cộng `nguon` (id đoạn lượt 1) cho mỗi
dòng. Máy kiểm mỗi mẩu `doan` nằm trọn trong đoạn `nguon` hay trong một `dung_chung` áp cho nó, nên LLM không gộp lại được hai mệnh đề
lượt 1 đã tách (lỗi gộp của `menh-de-12`). Không LLM nào kiểm LLM khác.

Dùng (gốc repo, cần CKEY_API_KEY khi gọi):
  python -I -X utf8 src/clause_roles.py kiem-gold dev|test      (gold qua máy kiểm lượt 2 và cổng cũ)
  python -I -X utf8 src/clause_roles.py goi dev|test|all [thư_mục]  (gọi API; dev/test đọc đoạn GOLD lượt 1, all đọc doan_luot1.json)
  python -I -X utf8 src/clause_roles.py cham dev|test [thư_mục]  (chấm với gold, ghi báo cáo)
  KLTN_LLM_RUN=tach python -I -X utf8 src/clause_roles.py nhap   (kiểm thư mục all/ rồi ghi cache 1.6A của lần chạy `tach`)
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import propositions  # noqa: E402
import segments  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PROMPT_VERSION = "vai-nhom-3"  # 3 (A62): liet_ke từ 2 mục, kể cả danh sách danh từ; người nhận là danh từ gọi NLĐ/NSDLĐ (cả loại cụ thể) vào doi_so, đuôi thời gian của kết luận giữ; dan_chieu_dieu_kien. 2: đoạn không phải câu dẫn luôn có dòng (D145.K1, D51.K1)  # phải bắt đầu bằng propositions.V2_PREFIX để cổng coi là khuôn gọn
RUN_DIR = ROOT / "data/sandbox_runs/clause_roles"
GOLD = {"dev": ROOT / "data/eval_dev/clause_roles_gold_dev.json", "test": ROOT / "data/eval_dev/clause_roles_gold_test.json"}
MODEL_DU_PHONG_2 = "daongocson12022004/gemini-3.8-flash-high"  # [THÊM 25/11, A61] tuyến không có trần ~8k (đo lượt 008 của 1.6B: 9.486 token nghĩ ngầm vẫn trọn)
MODELS = (segments.MODEL, segments.MODEL_DU_PHONG, MODEL_DU_PHONG_2)  # chốt trước khi đo (mục 10): tuyến chính, 404 thì dự phòng; [A61] cụt hay 403 thì sang tuyến sau
MAX_TOKENS = 32000  # api.max_output_tokens; tuyến dự phòng suy nghĩ ngầm dài (cụt 2/40 câu đơn ở 16.000, A60)
LUONG = 16  # 8 lúc đo; 16 khi chạy cả bộ (mỗi lời gọi ~1 phút, máy chủ cho 60 lượt/phút); không ảnh hưởng đầu ra
LEAD = re.compile(r"(sau đây|như sau|gồm|bao gồm)\s*:?\s*$")
# Ngưỡng (mục 10.5, chốt trước khi gọi).
NGUONG = {"qua_may": 0.95, "f1_dong": 0.80, "vai": 0.90, "phuong_thuc": 0.85, "cuc": 0.95, "cau_truc": 0.70}


def _nfc(s):
    return unicodedata.normalize("NFC", s or "")


# ---- Đầu vào: đoạn lượt 1 của từng câu, id mang số câu ("s2.m1").
def unit_sentences():
    """{unit_id: [câu đã chuẩn bị của segments, theo thứ tự]} và ngữ cảnh 1.6A."""
    ctxs = propositions.contexts()
    out = {}
    for p in segments.all_sentences(ctxs):
        out.setdefault(p["sid"].split("#")[0], []).append(p)
    return ctxs, out


def gold_segments(prep, doan):
    """Đoạn gold lượt 1 của một câu -> đoạn đã dựng như doan_luot1.json (chèn dan_chieu, kèm chữ nối ở khe)."""
    errs, _flags, placed = segments.check(prep, {"doan": doan})
    if errs:
        raise SystemExit(f"{prep['sid']}: gold lượt 1 không qua máy kiểm {errs}")
    return [{k: d[k] for k in ("id", "loai", "chu", "ap_cho", "khe_truoc") if k in d} for d in segments.build(prep, placed)]


def unit_input(uid, ctx, preps, doan_by_sid):
    """-> (lời gửi dạng dict, {id: đoạn}, số câu lượt 1 hỏng). Câu không có đoạn lượt 1 (hỏng hay thiếu): cả câu một đoạn menh_de
    (mục 10, [THÊM]); lượt 2 tách tự do trong câu đó như menh-de-12."""
    cau, segmap, hong = [], {}, 0
    for i, p in enumerate(preps, 1):
        segs = doan_by_sid.get(p["sid"])
        if segs is None:
            hong += 1
            segs = [{"id": "m1", "loai": "menh_de", "chu": p["cau"].strip().rstrip(".;:").strip(), "khe_truoc": []}]
        doan = []
        for s in segs:
            d = {"id": f"s{i}.{s['id']}", "loai": s["loai"], "chu": s["chu"]}
            if s.get("ap_cho"):
                d["ap_cho"] = [f"s{i}.{x}" for x in s["ap_cho"]]
            if s.get("khe_truoc"):
                d["noi_truoc"] = s["khe_truoc"]
            doan.append(d)
            segmap[d["id"]] = d
        cau.append({"chu": p["cau"], "doan": doan})
    msg = {"unit_id": uid, "tieu_de_dieu": ctx["heading"], "khoan_cha": ctx["chapeau"], "dan_chieu": ctx["refs"], "cau": cau}
    return msg, segmap, hong


# ---- Máy kiểm lượt 2 (mục 10.4), cộng vào cổng cũ.
def check(ctx, segmap, out):
    """-> (dòng khuôn cũ, lỗi, cờ, nguon của từng dòng menh_de theo thứ tự). Lỗi, cờ: [(chỉ số dòng hay None, thông điệp)]."""
    if not isinstance(out, dict):
        return [], [(None, "đầu ra không phải object")], [], []
    err = []
    menh = {k for k, s in segmap.items() if s["loai"] == "menh_de"}
    dong = out.get("dong") if isinstance(out.get("dong"), list) else []
    nguon = []
    for i, r in enumerate(dong):
        if not isinstance(r, dict):
            nguon.append(None)
            continue
        ng = r.get("nguon")
        nguon.append(ng)
        if ng not in menh:
            err.append((i, f"nguon {ng!r} không phải id đoạn menh_de"))
            continue
        allowed = [_nfc(segmap[ng]["chu"])] + [_nfc(s["chu"]) for s in segmap.values()
                                               if s["loai"] == "dung_chung" and ng in s.get("ap_cho", [])]
        for x in r.get("doan") or []:
            if isinstance(x, str) and not any(_nfc(x) in a for a in allowed):
                err.append((i, f"doan {x[:50]!r} không nằm trọn trong đoạn {ng} hay một dung_chung áp cho nó"))
    if out.get("bo_qua") is None:
        covered = set(nguon)
        for k in sorted(menh - covered):
            if out.get("cac_muc_con") == "danh_sach" and LEAD.search(segmap[k]["chu"]):
                continue
            err.append((None, f"đoạn {k} không có dòng nào"))
    exc = out.get("ngoai_le") or []
    dk = out.get("dan_chieu_dieu_kien")  # [A62] dẫn chiếu là điều kiện của quy tắc nào
    if dk is not None:
        qs = {r.get("quy_tac") for r in dong if isinstance(r, dict)}
        refs = {ref["dich"] for ref in ctx["refs"]}
        for x in dk if isinstance(dk, list) else [dk]:
            if not isinstance(x, dict) or x.get("dich") not in refs:
                err.append((None, f"dan_chieu_dieu_kien {x!r}: dich không có trong dẫn chiếu của đơn vị"))
            elif x.get("quy_tac") not in qs:
                err.append((None, f"dan_chieu_dieu_kien {x!r}: quy_tac không có dòng nào"))
            elif x["dich"] in exc:
                err.append((None, f"dan_chieu_dieu_kien {x['dich']}: đã là ngoại lệ"))
    for s in segmap.values():
        if s["loai"] == "dan_chieu":
            for ref in ctx["refs"]:
                if ref["cum"] in s["chu"] and ref["dich"] not in exc:
                    err.append((None, f"đích {ref['dich']} trong đoạn dan_chieu {s['id']} vắng ở ngoai_le"))
    stripped = {**out, "dong": [{k: v for k, v in r.items() if k != "nguon"} if isinstance(r, dict) else r for r in dong]}
    rows, e2, f2 = propositions.check_unit(ctx, stripped, PROMPT_VERSION)
    return rows, err + e2, f2, nguon


# ---- Máy trải `liet_ke` (A61, user chốt 25/11): KHÔNG phải việc của LLM. Lượt 2 đã cắt ranh giới mục vào `liet_ke` (đặc tả mục 3) nhưng chưa
# bước nào đọc trường đó, nên vị từ chỉ còn phần đầu ("đóng", "có hành vi"). Máy trải mỗi mục thành một dòng theo chữ nối đứng trước mục cuối
# trong `trich`; không chắc thì giữ nguyên dòng và gắn cờ. Không gọi LLM, không đổi lời nhắc.
_SEP_OR = re.compile(r"(^|\s)(hoặc|hay)(\s|$)")
_SEP_AND = re.compile(r"(^|\s)và(\s|$)")
# Danh sách chỉ nối bằng dấu phẩy mà user duyệt GIỮ NGUYÊN (25/11): (đơn vị, mục đầu). Tách thành HOẶC là nới nghĩa luật.
LIET_KE_GIU = {("BLLD_45-2019.D3.K1", "quản lý"), ("BLLD_45-2019.D151.K1.b", "trình độ chuyên môn"),
               ("BLLD_45-2019.D91.K3", "mức sống tối thiểu của người lao động và gia đình họ")}  # D91.K3: các căn cứ cùng xét, agent giữ (báo user)


def _noi_cuoi(trich, items):
    """Chữ nối giữa mục kề cuối và mục cuối trong `trich`: 'hoac' | 'va' | 'phay' | None (không tìm thấy mục nguyên văn theo thứ tự)."""
    t, pos, spans = _nfc(" ".join(trich)).lower(), 0, []
    for x in items:
        k = t.find(_nfc(x).lower(), pos)
        if k < 0:
            return None
        spans.append((k, k + len(x)))
        pos = k + len(x)
    gap = t[spans[-2][1]:spans[-1][0]]
    if _SEP_OR.search(gap):
        return "hoac"
    if _SEP_AND.search(gap):
        return "va"
    return "phay" if "," in gap or ";" in gap else None


def _lo_moi(menh_de, items, x):
    """Lõi của mục x: thay cả chuỗi mục trong lõi bằng x; lõi không chứa mục nào (chỉ là phần đầu, như "đóng") thì nối x vào sau.
    So khớp không phân biệt hoa thường (A62: lõi đã hạ chữ hoa đầu câu còn mục thì không, D147.K2.a ra "... trong đường hầm Dưới nước").
    Lõi chứa một phần danh sách mà không khớp đủ mục theo thứ tự thì trả None: nối thêm sẽ lặp chữ, người gọi giữ nguyên dòng."""
    low, its = _nfc(menh_de).lower(), [_nfc(i).lower() for i in items]
    if len(low) != len(menh_de):  # hạ chữ làm lệch vị trí thì không cắt theo chỉ số được
        return None
    a, z = low.find(its[0]), low.rfind(its[-1])
    if a >= 0 and z >= a and all(i in low for i in its):
        if a == 0 and menh_de[:1].islower():  # máy chỉ hạ chữ hoa ĐẦU lõi; ở giữa lõi giữ nguyên (danh từ riêng "Tổng Liên đoàn")
            x = x[:1].lower() + x[1:]
        return " ".join((menh_de[:a] + x + menh_de[z + len(items[-1]):]).split())
    if any(i in low for i in its):
        return None
    head, xs = menh_de.split(), x.split()
    if head and xs and head[-1].lower() == xs[0].lower():  # "đang nghỉ" + "nghỉ việc riêng": không lặp chữ ở chỗ nối
        xs = xs[1:]
    return " ".join(head + xs)


# A62: dòng mà cả chữ chỉ là lời dẫn chiếu trong Bộ luật ("theo quy định của Bộ luật này", "quy định tại Mục 1 Chương XI ...").
# Đích (nếu có) đã là dòng con_tro riêng; giữ chữ này làm điều kiện thì ra vị từ không câu hỏi nào khai được, quy tắc không bao giờ chạy.
# Không bắt "theo quy định của pháp luật (về ...)" (dẫn chiếu ra luật khác, có nghĩa) và câu có nội dung ("sau thời hạn quy định tại").
# Không dùng re.I: "điều ước quốc tế" (D154.K7) không phải "Điều <số>"; sau Mục/Chương/Điều/khoản/điểm phải là số hay chữ ký hiệu.
_CHI_DAN_CHIEU = re.compile(r"(?:[Tt]heo\s+|[Tt]ại\s+)?(?:các\s+)?[Qq]uy định\s+(?:tại|của)"
                            r"(?:\s+(?:các\s+)?(?:Mục|Chương|Điều|khoản|điểm)\s+[0-9a-zđIVXLC][^;]*?)?(?:\s+của)?(?:\s+Bộ luật này)?")


def bo_dong_chi_dan_chieu(rows):
    """-> (dòng còn lại, cờ). Chỉ bỏ dòng dieu_kien; kết luận chỉ là chữ dẫn chiếu thì giữ, gắn cờ (bỏ đi là mất kết luận)."""
    out, flags = [], []
    for i, r in enumerate(rows):
        if r.get("loai") == "menh_de" and _CHI_DAN_CHIEU.fullmatch((r.get("menh_de") or "").strip()):
            if r.get("vai") == "dieu_kien":
                flags.append((None, f"bỏ dòng chỉ là chữ dẫn chiếu (dòng gốc {i}): {r['menh_de']!r}"))
                continue
            flags.append((None, f"dòng {r.get('vai')} chỉ là chữ dẫn chiếu, giữ (dòng gốc {i}): {r['menh_de']!r}"))
        out.append(r)
    return out, flags


# A62 bước 3a: Điều không có câu dẫn mà tiêu đề nêu kết luận, các khoản là từng trường hợp (BLLĐ: D34, D37, D156, D204, D206 dạng
# "(Các) trường hợp ..."; D154 dạng "<chủ thể> không thuộc diện <X>"). Lượt 2 không có luật cho dạng này (luật tương ứng của menh-de-7,
# A52, không có trong vai-nhom-2), nên LLM hoặc lấy chính trường hợp làm kết luận (D34.K1 "hết hạn hợp đồng lao động"), hoặc chỉ ghi điều
# kiện mà không có kết luận (D34.K6, D37, D156): 1.8 bỏ cả nhóm. Máy dựng kết luận từ tiêu đề, không giao thêm cho LLM (status mục 4a).
_TD_TRUONG_HOP = re.compile(r"(?:Các )?[Tt]rường hợp (?:(?P<chu>người sử dụng lao động|người lao động) )?(?P<mod>không được |cấm )?(?P<rest>.+)")
_TD_KHONG_THUOC = re.compile(r"(?P<chu>.+?) không thuộc diện (?P<rest>.+)")
_LOAI_CHU = (("người sử dụng lao động", "E"), ("người lao động", "W"))


def ket_luan_tu_tieu_de(heading):
    """-> (menh_de, phuong_thuc, chủ thể {chu, loai} hoặc None, mẩu tiêu đề làm trich) hoặc None nếu tiêu đề không thuộc hai dạng trên."""
    h = (heading or "").strip()
    m = _TD_TRUONG_HOP.fullmatch(h)
    if m:
        mode, piece = ("cam" if m["mod"] else "khong"), h[m.start("chu") if m["chu"] else m.start("mod") if m["mod"] else m.start("rest"):]
    else:
        m = _TD_KHONG_THUOC.fullmatch(h)
        if not m:
            return None
        mode, piece = "khong_ap_dung", h
    chu = m["chu"]
    loai = next((c for t, c in _LOAI_CHU if chu and chu.lower().startswith(t)), None)
    return m["rest"], mode, ({"chu": chu, "loai": loai or "?", "nguon": "tieu_de"} if chu else None), piece


def _noi_hoac(text, rs):
    """Có khe nào giữa các dòng (theo thứ tự xuất hiện của mẩu trich đầu trong chữ đơn vị) chứa "hoặc" hay ";" không."""
    t = _nfc(text).lower()
    pos = sorted((t.find(_nfc((r.get("trich") or [r["menh_de"]])[0]).lower()), len((r.get("trich") or [r["menh_de"]])[0])) for r in rs)
    pos = [p for p in pos if p[0] >= 0]
    gaps = [t[a + n:b] for (a, n), (b, _) in zip(pos, pos[1:]) if b >= a + n]
    return any(_SEP_OR.search(g) or ";" in g for g in gaps)


def them_ket_luan_tieu_de(ctx, rows):
    """-> (dòng mới, cờ). Chỉ áp cho đơn vị không có câu dẫn (chapeau rỗng) thuộc Điều có tiêu đề dạng trên."""
    kl = None if (ctx.get("chapeau") or "").strip() else ket_luan_tu_tieu_de(ctx.get("heading"))
    if not kl:
        return rows, []
    menh_de, mode, chu, piece = kl
    out, flags, by_q = [], [], {}
    for i, r in enumerate(rows):
        r = dict(r)
        if r.get("loai") == "menh_de" and r.get("vai") == "ket_luan" and r.get("phuong_thuc") in ("khong", "khong_ap_dung"):
            # mô tả trong khoản là TRƯỜNG HỢP (điều kiện) của kết luận ở tiêu đề; khong_ap_dung đặt trên chữ trường hợp (D154.K1) cũng vậy
            r.update(vai="dieu_kien", phuong_thuc="khong")
            r["_tu_ket_luan"] = True
            flags.append((None, f"kết luận ở tiêu đề: dòng gốc {i} {r['menh_de']!r} chuyển thành điều kiện"))
        out.append(r)
        if r.get("loai") == "menh_de" and r.get("quy_tac"):
            by_q.setdefault(r["quy_tac"], []).append(r)
    for q, rs in by_q.items():
        if any(r["vai"] == "ket_luan" for r in rs) or not any(r["vai"] == "dieu_kien" for r in rs):
            continue
        conv = [r for r in rs if r.get("_tu_ket_luan") and not r.get("nhom_hoac")]
        if len(conv) > 1 and _noi_hoac(ctx.get("text") or "", conv):
            # nhiều mô tả trong một khoản nối "hoặc"/";" là các trường hợp HOẶC (D34.K4 "bị kết án ..., tử hình hoặc bị cấm ...");
            # nối "để", "và" là VÀ (D154.K4 "vào Việt Nam dưới 03 tháng để thực hiện chào bán dịch vụ"): giữ, không nhóm
            for r in conv:
                r["nhom_hoac"] = f"td{q}"
        out.append({"loai": "menh_de", "vai": "ket_luan", "menh_de": menh_de, "chu_the": chu, "doi_so": [], "phuong_thuc": mode,
                    "cuc": "khang_dinh", "bo_ngu": [], "nhom_hoac": None, "cac_muc_con": None, "chua_ro": [], "trich": [piece],
                    "targets": [], "quy_tac": q, "gan_vao": None, "liet_ke": [], "ly_do_llm": "máy: kết luận ở tiêu đề Điều (A62)"})
        flags.append((None, f"kết luận ở tiêu đề: thêm {menh_de!r} ({mode}) cho quy_tac {q}"))
    for r in out:
        r.pop("_tu_ket_luan", None)
    return out, flags


THUAT_NGU_SO_DIEU = 3  # [A62] cụm danh sách lặp nguyên văn ở từ ngần này Điều là thuật ngữ cố định (định nghĩa vị từ ghép, user duyệt 25/11)


def cum_danh_sach(text, items):
    """Chữ của cả danh sách (từ mục đầu tới hết mục cuối) trong text, viết thường; không thấy theo thứ tự thì None."""
    t = _nfc(text).lower()
    a = t.find(_nfc(items[0]).lower())
    z = t.find(_nfc(items[-1]).lower(), a + 1) if a >= 0 else -1
    return t[a:z + len(items[-1])] if a >= 0 and z >= a else None


def trai_liet_ke(uid, rows, src="", so_dieu_co=None):
    """-> (dòng mới, cờ [(None, thông điệp kèm chỉ số dòng gốc)]). Luật (A61):
    - kết luận nối "và" hay chỉ dấu phẩy: mỗi mục một kết luận cùng `quy_tac`; nối "hoặc": GIỮ ("phải A hoặc B" tách ra thành hai nghĩa vụ);
    - điều kiện nối "hoặc" hay chỉ dấu phẩy (user chốt: phẩy là HOẶC): mỗi mục một dòng cùng `nhom_hoac` (nhóm sẵn có của dòng, không có thì nhóm mới);
    - ngoại lệ nối "hoặc" hay phẩy: mỗi mục một ngoại lệ;
    - điều kiện, ngoại lệ nối "và": GIỮ (liệt kê trường hợp thường là HOẶC, đòi đủ thì là VÀ: đặc tả im lặng);
    - mục không nguyên văn trong `trich`, chữ nối không rõ, hay (đơn vị, mục đầu) thuộc LIET_KE_GIU: giữ."""
    out, flags = [], []
    for i, r in enumerate(rows):
        items = [x for x in (r.get("liet_ke") or []) if isinstance(x, str) and x.strip()]
        if r.get("loai") != "menh_de" or len(items) < 2:
            out.append(r)
            continue
        # dò trên trich, không thấy thì trên chữ gốc của đơn vị (khuôn gọn dựng trich từ doan, mà doan có khi chỉ là phần đầu như "đóng")
        noi = _noi_cuoi(r.get("trich") or [], items) or (_noi_cuoi([src], items) if src else None)
        vai = r.get("vai")
        why = None
        cum = cum_danh_sach(" ".join(r.get("trich") or []) + " " + src, items) if so_dieu_co else None
        if (uid, items[0]) in LIET_KE_GIU:
            why = "user duyệt giữ"
        elif cum and so_dieu_co(cum) >= THUAT_NGU_SO_DIEU:
            why = f"thuật ngữ cố định (lặp nguyên văn ở {so_dieu_co(cum)} Điều): {cum!r}"
        elif noi is None:
            why = "mục không nguyên văn theo thứ tự (trich, chữ đơn vị) hoặc chữ nối không rõ"
        elif vai == "ket_luan" and noi == "hoac":
            why = "kết luận nối 'hoặc'"
        elif vai in ("dieu_kien", "ngoai_le") and noi == "va":
            # "và" trong danh sách điều kiện thường là liệt kê trường hợp, nghĩa HOẶC (D37.K2 "đang nghỉ hằng năm, nghỉ việc riêng và trường hợp
            # nghỉ khác"); tách thành VÀ là sai nghĩa, tách thành HOẶC là đoán: giữ, gắn cờ (đặc tả im lặng, A61)
            why = "điều kiện hay ngoại lệ nối 'và' (liệt kê trường hợp hay đòi đủ: chưa rõ)"
        elif vai not in ("ket_luan", "dieu_kien", "ngoai_le"):
            why = f"vai {vai!r}"
        elif any(_lo_moi(r["menh_de"], items, x) is None for x in items):
            why = "lõi chứa một phần danh sách mà không khớp đủ mục (trải sẽ lặp chữ)"
        if why:
            flags.append((None, f"liet_ke giữ nguyên (dòng gốc {i}): {why}"))
            out.append(r)
            continue
        group = None
        if vai == "dieu_kien" and noi in ("hoac", "phay"):
            group = r.get("nhom_hoac") or f"lk{i}"
        for x in items:
            out.append({**r, "menh_de": _lo_moi(r["menh_de"], items, x), "liet_ke": [], "nhom_hoac": group if group else r.get("nhom_hoac")})
        flags.append((None, f"liet_ke trải {len(items)} mục (dòng gốc {i}, {vai}, nối {noi})"))
    return out, flags


# ---- Lời nhắc. Sửa chữ thì PHẢI nâng PROMPT_VERSION. Ví dụ chỉ lấy từ Điều không có trong hai gold (mục 10.5): D113, D53, D176, D18, D80.
SYSTEM = """Bạn nhận MỘT đơn vị của Bộ luật Lao động (khoản, điểm hoặc Điều) mà các câu đã được tách sẵn thành đoạn. Hãy ghi các dòng mệnh đề: mỗi dòng là một điều kiện, một ngoại lệ hoặc một kết luận, kèm phương thức, cực, chủ thể, và gom thành quy tắc.

## Đầu vào
- tieu_de_dieu, khoan_cha (câu dẫn của khoản hoặc Điều cha), dan_chieu (dẫn chiếu đã giải: cum, dich).
- cau: các câu, mỗi câu có doan đã tách: "menh_de" (một việc), "dung_chung" (phần nhiều mệnh đề dùng chung; ap_cho là các mệnh đề nó áp cho), "dan_chieu" (khối "trừ trường hợp quy định tại ..."). noi_truoc là chữ nối đứng ngay trước đoạn (nếu, khi, thì, trừ, để, và, hoặc ...).

## Mỗi dòng
- nguon: id của MỘT đoạn menh_de (ví dụ "s1.m2"). Mỗi đoạn menh_de có ít nhất một dòng. Riêng đoạn câu dẫn ("... sau đây", "như sau") mà danh sách mục con là tân ngữ (cac_muc_con là danh_sach) thì không có dòng; các đoạn KHÁC của câu đó (ví dụ vế "khi ..." đứng trước câu dẫn) vẫn phải có dòng.
- doan: các mẩu chép NGUYÊN VĂN; nối lại là lõi: động từ (hoặc tính chất) + tân ngữ chính. MỖI MẨU nằm trọn trong MỘT đoạn: đoạn nguon, hoặc một đoạn dung_chung có ap_cho chứa nguon khi chữ đó là phần của việc (tân ngữ, bổ ngữ làm nên việc). Không đưa vào doan: chủ thể, chữ phương thức (phải, được, có quyền, có thể, có trách nhiệm, cấm, không được), chữ phủ định, chữ dẫn chiếu.
- vai: ket_luan | dieu_kien | ngoai_le. Theo chữ nối trước đoạn: "nếu", "khi", "trong khi", "sau khi", "trước khi", "trường hợp", "trong trường hợp", "Do" đầu câu: dieu_kien; "trừ", "trừ trường hợp": ngoai_le; vế trước "thì" là điều kiện, vế sau là kết luận; "để", "nhằm": ket_luan cùng quy_tac với việc nó nói mục đích. Không có chữ nối thì theo nghĩa: câu quy định là ket_luan; mục con của câu dẫn "trong trường hợp sau đây" là dieu_kien.
- phuong_thuc: duoc (được, có quyền, có thể) | phai (phải, có nghĩa vụ, có trách nhiệm) | cam (cấm, không được làm) | khong_ap_dung (một quy định không áp cho một nhóm trường hợp) | khong (không có chữ phương thức: mô tả, định nghĩa). Dòng dieu_kien và ngoai_le luôn là khong. Dòng ket_luan chỉ ghi khác khong khi chữ phương thức có trong câu, khoan_cha hoặc tieu_de_dieu ("Nghĩa vụ", "Trách nhiệm" ở tiêu đề là phai; "Quyền" là duoc).
- cuc: khang_dinh | phu_dinh (chỉ phủ định lõi). "Không phải / không cần + động từ" (không có nghĩa vụ): duoc + phu_dinh. "Không được + động từ": cam; nếu bị động (không được người khác làm cho) thì khong + phu_dinh. "Không phải là + danh từ": khong + phu_dinh.
- chu_the: {"chu": chép nguyên văn cụm chủ thể (từ đoạn, dung_chung, khoan_cha hoặc tieu_de_dieu), "loai": mã}; không có thì bỏ. Mã: W người lao động, E người sử dụng lao động, C hợp đồng, J công việc, G vùng, D ngày, A số tiền, ? chưa biết (danh sách mã khi chủ thể chung). Người chỉ chịu tác động là doi_so: [{"loai": mã}].
- quy_tac: "q1", "q2"... Các kết luận có ĐÚNG cùng tập điều kiện và ngoại lệ (kể cả không có điều kiện nào) chung một quy_tac, cùng các dòng điều kiện, ngoại lệ đó. Tập điều kiện khác thì quy tắc khác; một điều kiện dùng cho nhiều quy tắc thì lặp dòng đó (cùng nguon) trong mỗi quy tắc.
- nhom_hoac: "h1"... cho các điều kiện nối "hoặc"/"hay" trong một quy tắc; nối "và" thì bỏ.
- liet_ke: danh sách (từ 2 mục, kể cả danh sách danh từ) tân ngữ, phạm vi hay trường hợp của cùng một động từ, mỗi mục nguyên văn. Không ghi cho cụm gọi tên MỘT khái niệm ("quyền và lợi ích hợp pháp").
- chua_ro: [{"thanh_phan", "nguyen_nhan": pham_vi_bo_ngu | tach_hay_giu_chung | phuong_thuc | chu_the | khac, "cau_hoi"}] khi không xác định được. Không đoán.
Trường rỗng thì bỏ.

## Luật
1. Bổ ngữ của ĐỘNG TỪ là một dòng dieu_kien riêng, cùng nguon, chu_the và quy_tac với dòng nó bổ nghĩa: nơi chốn ("tại ...", "ở ..."), căn cứ ("theo ..."), thời gian ("trong thời hạn ...", "trong thời gian ...", "trong quá trình ..."), và "đối với X" khi X giới hạn phạm vi áp dụng quy định. Cụm nằm trong một danh từ ("<danh từ> theo quy định của <cơ quan>" chỉ rõ danh từ nào) giữ trong doan. "Đối với X" chỉ người hay vật chịu tác động của hành vi giữ trong doan. Cụm làm nên chính việc (mức tiền, số ngày, thời điểm, hình thức của việc) giữ trong doan. Người nhận hay chịu hành vi đứng sau "cho", "với", "đối với" mà chỉ là danh từ gọi người lao động hay người sử dụng lao động, kể cả loại cụ thể (lao động nữ, người giúp việc gia đình), thì ghi vào doi_so, không ghi vào doan; người có kèm mô tả thì giữ. Dòng có nhom_hoac thì không tách bổ ngữ ra (tách ra là thành điều kiện chung của cả nhóm). Bổ ngữ nằm trong một đoạn dung_chung thì mỗi quy_tac một dòng, nguon là mệnh đề ĐẦU TIÊN trong ap_cho của đoạn đó thuộc quy tắc ấy.
2. Một đoạn có hai sự kiện (ví dụ một vế "do ..." nêu nguyên nhân) thì hai dòng cùng nguon.
3. Câu dẫn: danh sách là TÂN NGỮ ("có các quyền sau đây") thì cac_muc_con là danh_sach và câu dẫn không có dòng; mục con là ket_luan (doan là chữ của mục), kế thừa chủ thể và phương thức từ khoan_cha. Danh sách là ĐIỀU KIỆN ("trong trường hợp sau đây") thì cac_muc_con là va (phải đủ hết) hoặc hoac (một mục là đủ), câu dẫn ra một ket_luan; mục con là dieu_kien.
4. Định nghĩa "X là Y": các dấu hiệu của Y là dieu_kien; thêm một ket_luan có doan ["là", "X"]. Câu nêu giá trị, mức là một ket_luan.
5. Chủ thể hay phương thức bị lược thì lấy từ khoan_cha hoặc tieu_de_dieu; chu_the.chu chép đúng cụm ở đó.

## Trường của đơn vị
- ngoai_le: danh sách dich (lấy từ dan_chieu) của dẫn chiếu là ngoại lệ. Mọi dẫn chiếu nằm trong đoạn dan_chieu PHẢI có ở đây. Máy tự dựng dòng cho mọi dẫn chiếu; không chép chữ dẫn chiếu vào doan.
- dan_chieu_dieu_kien: [{"dich", "quy_tac"}] cho dẫn chiếu nêu trường hợp, đối tượng hay điều kiện mà một quy tắc đòi ("khi hợp đồng chấm dứt theo quy định tại khoản 1 Điều X", "người quy định tại khoản 2 Điều này"); quy_tac là quy tắc đòi nó. Dẫn chiếu chỉ cách làm hay mức ("trả lương theo quy định tại Điều X") và dẫn chiếu là ngoại lệ thì không ghi. Đơn vị có dẫn chiếu thì luôn ghi trường này (rỗng nếu không có cái nào).
- cac_muc_con: va | hoac | danh_sach, chỉ cho câu dẫn vào các mục con.
- bo_qua: khong_quy_pham (câu chính sách, không có hành vi kiểm được) | dan_chieu_mo | dan_chieu_ngoai (chỉ dẫn sang quy định khác); khi đó dong có thể rỗng.

## Đầu ra
JSON thuần, không chữ giải thích: {"unit_id": "...", "dong": [...], cộng ngoai_le, dan_chieu_dieu_kien, cac_muc_con, bo_qua khi có}.

## Ví dụ (đầu vào rút gọn: chỉ ghi đoạn)
1. tieu_de_dieu "Nghỉ hằng năm". s1: c "Người sử dụng lao động" (ap_cho s1.m1, s1.m2, s1.m3) · s1.m1 "có trách nhiệm quy định lịch nghỉ hằng năm" · [sau khi] s1.m2 "tham khảo ý kiến của người lao động" · [và] s1.m3 "phải thông báo trước cho người lao động biết". s2: c "Người lao động" (ap_cho s2.m1, s2.m2, s2.m3) · s2.m1 "có thể thỏa thuận với người sử dụng lao động" · [để] s2.m2 "nghỉ hằng năm thành nhiều lần" · [hoặc] s2.m3 "nghỉ gộp tối đa 03 năm một lần".
{"unit_id":"BLLD_45-2019.D113.K4","dong":[{"nguon":"s1.m1","doan":["quy định lịch nghỉ hằng năm"],"vai":"ket_luan","phuong_thuc":"phai","cuc":"khang_dinh","chu_the":{"chu":"Người sử dụng lao động","loai":"E"},"quy_tac":"q1"},{"nguon":"s1.m2","doan":["tham khảo ý kiến của người lao động"],"vai":"dieu_kien","phuong_thuc":"khong","cuc":"khang_dinh","chu_the":{"chu":"Người sử dụng lao động","loai":"E"},"doi_so":[{"loai":"W"}],"quy_tac":"q1"},{"nguon":"s1.m3","doan":["thông báo trước cho người lao động biết"],"vai":"ket_luan","phuong_thuc":"phai","cuc":"khang_dinh","chu_the":{"chu":"Người sử dụng lao động","loai":"E"},"doi_so":[{"loai":"W"}],"quy_tac":"q2"},{"nguon":"s2.m1","doan":["thỏa thuận với người sử dụng lao động"],"vai":"ket_luan","phuong_thuc":"duoc","cuc":"khang_dinh","chu_the":{"chu":"Người lao động","loai":"W"},"doi_so":[{"loai":"E"}],"quy_tac":"q2"},{"nguon":"s2.m2","doan":["nghỉ hằng năm thành nhiều lần"],"vai":"ket_luan","phuong_thuc":"duoc","cuc":"khang_dinh","chu_the":{"chu":"Người lao động","loai":"W"},"quy_tac":"q2"},{"nguon":"s2.m3","doan":["nghỉ gộp tối đa 03 năm một lần"],"vai":"ket_luan","phuong_thuc":"duoc","cuc":"khang_dinh","chu_the":{"chu":"Người lao động","loai":"W"},"quy_tac":"q2"}]}
2. Câu dẫn, danh sách là điều kiện. s1.m1 "Bên thuê lại lao động được sử dụng lao động thuê lại trong trường hợp sau đây".
{"unit_id":"BLLD_45-2019.D53.K2","cac_muc_con":"hoac","dong":[{"nguon":"s1.m1","doan":["sử dụng lao động thuê lại"],"vai":"ket_luan","phuong_thuc":"duoc","cuc":"khang_dinh","chu_the":{"chu":"Bên thuê lại lao động","loai":"E"},"quy_tac":"q1"}]}
Mục con của nó, khoan_cha "Bên thuê lại lao động được sử dụng lao động thuê lại trong trường hợp sau đây:". s1.m1 "Đáp ứng tạm thời sự gia tăng đột ngột về nhu cầu sử dụng lao động trong khoảng thời gian nhất định".
{"unit_id":"BLLD_45-2019.D53.K2.a","dong":[{"nguon":"s1.m1","doan":["Đáp ứng tạm thời sự gia tăng đột ngột về nhu cầu sử dụng lao động"],"vai":"dieu_kien","phuong_thuc":"khong","cuc":"khang_dinh","chu_the":{"chu":"Bên thuê lại lao động","loai":"E"},"quy_tac":"q1"},{"nguon":"s1.m1","doan":["trong khoảng thời gian nhất định"],"vai":"dieu_kien","phuong_thuc":"khong","cuc":"khang_dinh","chu_the":{"chu":"Bên thuê lại lao động","loai":"E"},"quy_tac":"q1"}]}
3. Câu dẫn, danh sách là tân ngữ. s1.m1 "Thành viên ban lãnh đạo của tổ chức đại diện người lao động tại cơ sở có quyền sau đây".
{"unit_id":"BLLD_45-2019.D176.K1","cac_muc_con":"danh_sach","dong":[]}
4. dan_chieu [{"cum":"khoản 2 Điều này","dich":"BLLD_45-2019.D18.K2"}]. s1.m1 "Người lao động trực tiếp giao kết hợp đồng lao động" · s1.d1 dan_chieu "trừ trường hợp quy định tại khoản 2 Điều này".
{"unit_id":"BLLD_45-2019.D18.K1","ngoai_le":["BLLD_45-2019.D18.K2"],"dong":[{"nguon":"s1.m1","doan":["trực tiếp giao kết hợp đồng lao động"],"vai":"ket_luan","phuong_thuc":"khong","cuc":"khang_dinh","chu_the":{"chu":"Người lao động","loai":"W"},"doi_so":[{"loai":"C"}],"quy_tac":"q1"}]}
5. [Trường hợp] s1.m1 "thỏa ước lao động tập thể doanh nghiệp hết hiệu lực do người sử dụng lao động chấm dứt hoạt động" · [thì] s1.m2 "quyền lợi của người lao động được giải quyết theo quy định của pháp luật".
{"unit_id":"BLLD_45-2019.D80.K2","dong":[{"nguon":"s1.m1","doan":["thỏa ước lao động tập thể doanh nghiệp hết hiệu lực"],"vai":"dieu_kien","phuong_thuc":"khong","cuc":"khang_dinh","quy_tac":"q1"},{"nguon":"s1.m1","doan":["chấm dứt hoạt động"],"vai":"dieu_kien","phuong_thuc":"khong","cuc":"khang_dinh","chu_the":{"chu":"người sử dụng lao động","loai":"E"},"quy_tac":"q1"},{"nguon":"s1.m2","doan":["quyền lợi","được giải quyết"],"vai":"ket_luan","phuong_thuc":"khong","cuc":"khang_dinh","chu_the":{"chu":"người lao động","loai":"W"},"quy_tac":"q1"},{"nguon":"s1.m2","doan":["theo quy định của pháp luật"],"vai":"dieu_kien","phuong_thuc":"khong","cuc":"khang_dinh","chu_the":{"chu":"người lao động","loai":"W"},"quy_tac":"q1"}]}"""
EXAMPLE_UNITS = ("D113.K4", "D53.K2", "D53.K2.a", "D176.K1", "D18.K1", "D80.K2")


def user_text(msg):
    return json.dumps(msg, ensure_ascii=False, indent=1)


# ---- Gọi API: mỗi đơn vị một lời gọi (mục 10), như segments.goi (tuyến chính, 404 thì dự phòng; lỗi mạng hay cụt gọi lại sau).
def _goi_mot(text, models, key, base):
    """-> (phản hồi, tuyến, trạng thái, đã tắt nghĩ ngầm). Tuyến dự phòng có trần thật khoảng 8.192 token ra gồm cả nghĩ ngầm, bất kể
    max_tokens (đo 25/11: D137.K2 dừng `max_tokens` ở 7.672 + 442 token với max_tokens 64.000); ngân sách `thinking` và
    `reasoning_effort` không có tác dụng, `thinking: disabled` thường thì trả lời trọn nhưng không chắc (D176.K1.a: vẫn 7.862 token nghĩ
    ngầm). Nên: lượt cụt thì gọi lại NGAY một lần với nghĩ ngầm
    tắt (chỉ cho lượt cụt; đường gọi đã đo giữ nguyên), file lưu ghi lại để báo cáo đếm."""
    import time
    import urllib.request
    err = ""
    for model in models:
        tat = False
        for lan in range(1, 4):
            body = json.dumps({"model": model, "max_tokens": MAX_TOKENS, "system": SYSTEM, "messages": [{"role": "user", "content": text}],
                               **({"thinking": {"type": "disabled"}} if tat else {})}, ensure_ascii=False).encode("utf-8")
            req = urllib.request.Request(base + "/v1/messages", data=body, method="POST", headers={
                "Authorization": f"Bearer {key}", "Content-Type": "application/json", "anthropic-version": "2023-06-01"})
            try:
                with urllib.request.urlopen(req, timeout=600) as r:
                    data = json.loads(r.read().decode("utf-8"))
                if data.get("stop_reason") != "end_turn":
                    if not tat:
                        tat = True
                        continue
                    err = f"{model}: cụt {data.get('stop_reason')} (cả khi tắt nghĩ ngầm)"
                    break  # [A61] cụt cả khi tắt nghĩ ngầm: sang tuyến sau (trước đây trả về ngay, đơn vị thiếu đầu ra)
                return data, model, "ok", tat
            except Exception as e:  # 404 (tuyến không có), 403 (tài khoản không được gọi, A61): sang tuyến sau ngay; lỗi khác: chờ rồi thử lại
                err = f"{model}: {str(e)[:100]}"
                if getattr(e, "code", None) in (403, 404):
                    break
                time.sleep(10 * lan)
    return None, None, (err.split(": ", 1)[1] if ": cụt " in err else f"lỗi {err}"), False


def dot_models(key, base):
    """[A61, user chốt 25/11] Tuyến cho cả đợt gọi: thử tuyến chính MỘT lần ở đầu đợt (lời nhắn ngắn); được thì tuyến chính rồi tuyến ổn định,
    không được thì chỉ tuyến ổn định `MODEL_DU_PHONG_2`. Không dùng `MODEL_DU_PHONG` nữa (trần ~8k, cụt ở đơn vị dài)."""
    import urllib.request
    body = json.dumps({"model": segments.MODEL, "max_tokens": 64, "messages": [{"role": "user", "content": "ok"}]}).encode("utf-8")
    req = urllib.request.Request(base + "/v1/messages", data=body, method="POST", headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json", "anthropic-version": "2023-06-01"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            ok = json.loads(r.read().decode("utf-8")).get("stop_reason") is not None
    except Exception as e:  # 403, 404, mạng: coi như tuyến chính không dùng được trong đợt này
        print(f"tuyến chính {segments.MODEL} không dùng được: {str(e)[:100]}", flush=True)
        ok = False
    return (segments.MODEL, MODEL_DU_PHONG_2) if ok else (MODEL_DU_PHONG_2,)


def inputs(bo):
    """[(unit_id, ctx, lời gửi, segmap)] của một bộ: dev/test dùng đoạn GOLD lượt 1 (đo riêng lượt 2), all dùng doan_luot1.json."""
    ctxs, sents = unit_sentences()
    if bo == "all":
        luot1 = json.loads((segments.RUN_DIR / segments.PROMPT_VERSION / "doan_luot1.json").read_text(encoding="utf-8"))["cau"]
        doan = {sid: x["doan"] for sid, x in luot1.items()}
        uids = list(ctxs)
    else:
        g = json.loads(GOLD[bo].read_text(encoding="utf-8"))
        uids = [u["unit_id"] for u in g["don_vi"]]
        doan = {}
        gold1 = {c["sid"]: c["doan"] for b in ("dev", "test") for c in segments._gold(b)["cau"]}
        for u in uids:
            for p in sents[u]:
                doan[p["sid"]] = gold_segments(p, gold1[p["sid"]])
    out = []
    for u in uids:
        msg, segmap, _hong = unit_input(u, ctxs[u], sents[u], doan)
        out.append((u, ctxs[u], msg, segmap))
    return out


def goi(bo, thu_muc=None):
    import os
    from concurrent.futures import ThreadPoolExecutor
    import llm_client
    base = llm_client.load_config()["api.base_url"].rstrip("/")
    key = os.environ.get("CKEY_API_KEY")
    if not key:
        raise SystemExit("chưa có CKEY_API_KEY trong biến môi trường")
    out_dir = RUN_DIR / PROMPT_VERSION / (thu_muc or bo)
    out_dir.mkdir(parents=True, exist_ok=True)
    models = dot_models(key, base)
    print(f"tuyến dùng cho đợt này: {models}", flush=True)
    (RUN_DIR / PROMPT_VERSION / "system.txt").write_text(SYSTEM, encoding="utf-8")
    hong = [0]

    def one(item):
        u, _ctx, msg, _segmap = item
        path = out_dir / (u + ".json")
        if path.exists():
            return u, "co_san"
        if hong[0] >= segments.STOP_AFTER_FAILS:
            return u, "bỏ qua: máy chủ đang lỗi"
        text = user_text(msg)
        data, model, st, tat = _goi_mot(text, models, key, base)
        hong[0] = hong[0] + 1 if st.startswith("lỗi") else 0
        if data is not None:
            path.write_text(json.dumps({"unit_id": u, "phien_ban": PROMPT_VERSION, "model": model, "thinking_tat": tat, "gui": text, "phan_hoi": data},
                                       ensure_ascii=False, indent=1), encoding="utf-8")
        return u, f"{st} ({model})"

    with ThreadPoolExecutor(LUONG) as ex:
        for u, st in ex.map(one, inputs(bo)):
            if st != "co_san":
                print(u, st, flush=True)


def read_reply(path, text_sent=None):
    """-> (đầu ra dict hay None, dict phản hồi thô, model). Lời gửi trong file khác lời gửi hiện tại thì coi như chưa có."""
    rec = json.loads(path.read_text(encoding="utf-8"))
    if text_sent is not None and rec.get("gui") != text_sent:
        return None, rec["phan_hoi"], rec.get("model")
    data = rec["phan_hoi"]
    try:
        out = segments.parse_reply("".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"))
    except ValueError:
        out = None
    return out, data, rec.get("model")


# ---- Chấm (mục 10.5).
def _syl(doan):
    return set(propositions.syllables(" ".join(x for x in doan or [] if isinstance(x, str))))


def _kieu(ct):
    if not isinstance(ct, dict):
        return None
    k = ct.get("loai")
    return tuple(sorted(k)) if isinstance(k, list) else k


def _dup_key(r):
    return r.get("nguon"), tuple(sorted(_syl(r.get("doan"))))


def match(gold_rows, llm_rows, min_sim=0.5):
    """Ghép dòng cùng nguon theo độ trùng âm tiết lõi (Jaccard), tham lam từ cặp giống nhất (như propositions.match_rows).
    Dòng điều kiện lặp lại ở nhiều quy tắc (luật 5) giống hệt nhau nên ghép tham lam là ngẫu nhiên theo thứ tự; xếp lại các dòng trùng
    đó theo quy_tac của các dòng đã ghép chắc (advisor 24/11: LLM viết khối q2 trước q1 thì không bị tính sai cấu trúc)."""
    pairs = []
    for gi, g in enumerate(gold_rows):
        for li, x in enumerate(llm_rows):
            if not isinstance(x, dict) or g.get("nguon") != x.get("nguon"):
                continue
            a, b = _syl(g.get("doan")), _syl(x.get("doan"))
            sim = len(a & b) / len(a | b) if a | b else 1.0
            if sim >= min_sim:
                pairs.append((sim, gi, li))
    ug, ul, out = set(), set(), []
    for _sim, gi, li in sorted(pairs, reverse=True):
        if gi not in ug and li not in ul:
            ug.add(gi)
            ul.add(li)
            out.append((gi, li))
    import collections
    import itertools
    groups = collections.defaultdict(list)
    for gi, li in out:
        if _dup_key(gold_rows[gi]) == _dup_key(llm_rows[li]):
            groups[_dup_key(gold_rows[gi])].append((gi, li))
    dup = {k: v for k, v in groups.items() if len(v) > 1}
    if dup:
        chac = [(gi, li) for gi, li in out if not any((gi, li) in v for v in dup.values())]
        qmap = collections.Counter((gold_rows[gi].get("quy_tac"), llm_rows[li].get("quy_tac")) for gi, li in chac)
        for v in dup.values():
            gis, lis = [g for g, _ in v], [x for _, x in v]
            best = max(itertools.permutations(lis), key=lambda perm: sum(qmap[(gold_rows[g].get("quy_tac"), llm_rows[x].get("quy_tac"))] for g, x in zip(gis, perm)))
            out = [p for p in out if p not in v] + list(zip(gis, best))
    return sorted(out)


def _same_partition(G, X, pairs, field):
    """Hai dòng ghép được cùng nhóm ở gold thì cùng nhóm ở LLM và ngược lại (mã nhóm tự đặt nên không so chữ)."""
    def same(a, b):  # cùng nhóm khi cả hai có mã và mã trùng (nhom_hoac rỗng là "không thuộc nhóm hoặc nào")
        return bool(a.get(field)) and a.get(field) == b.get(field)
    for gi, li in pairs:
        for gj, lj in pairs:
            if gi < gj and same(G[gi], G[gj]) != same(X[li], X[lj]):
                return False
    return True


def score_unit(gold, out):
    """-> dict số đếm của một đơn vị. out có thể None (không phải JSON)."""
    G = gold.get("dong") or []
    X = [r for r in (out or {}).get("dong") or [] if isinstance(r, dict)] if isinstance(out, dict) else []
    pairs = match(G, X)
    s = {"g": len(G), "x": len(X), "m": len(pairs)}
    for f in ("vai", "phuong_thuc", "cuc"):
        s[f] = sum(G[gi].get(f) == X[li].get(f) for gi, li in pairs)
    s["chu_the"] = sum(_kieu(G[gi].get("chu_the")) == _kieu(X[li].get("chu_the")) for gi, li in pairs)
    o = out if isinstance(out, dict) else {}
    s["cau_truc"] = (len(pairs) == len(G) == len(X) and _same_partition(G, X, pairs, "quy_tac") and _same_partition(G, X, pairs, "nhom_hoac")
                     and sorted(gold.get("ngoai_le") or []) == sorted(o.get("ngoai_le") or [])
                     and gold.get("cac_muc_con") == o.get("cac_muc_con") and gold.get("bo_qua") == o.get("bo_qua"))
    s["lech"] = [(G[gi].get("nguon"), f, G[gi].get(f), X[li].get(f)) for gi, li in pairs for f in ("vai", "phuong_thuc", "cuc")
                 if G[gi].get(f) != X[li].get(f)]
    return s


def _fmt_rows(rows):
    out = []
    for r in rows or []:
        if not isinstance(r, dict):
            out.append(f"  - (dòng hỏng) {r!r}"[:200])
            continue
        ct = r.get("chu_the") or {}
        out.append(f"  - {r.get('nguon')} {r.get('quy_tac')}{'/' + r['nhom_hoac'] if r.get('nhom_hoac') else ''} {r.get('vai')} "
                   f"{r.get('phuong_thuc')} {r.get('cuc')} [{ct.get('loai') if isinstance(ct, dict) else ct}] {' | '.join(map(str, r.get('doan') or []))}")
    return out


def cham(bo, thu_muc=None):
    g = json.loads(GOLD[bo].read_text(encoding="utf-8"))
    gold = {u["unit_id"]: u["dau_ra"] for u in g["don_vi"]}
    src = RUN_DIR / PROMPT_VERSION / (thu_muc or bo)
    tong = {k: 0 for k in ("g", "x", "m", "vai", "phuong_thuc", "cuc", "chu_the")}
    n = qua = cau_truc = thieu = 0
    vnd, lines = 0.0, []
    for u, ctx, msg, segmap in inputs(bo):
        n += 1
        path = src / (u + ".json")
        if not path.exists():
            thieu += 1
            lines.append(f"### {u}: THIẾU PHẢN HỒI\n")
            s = score_unit(gold[u], None)
            for k in tong:
                tong[k] += s[k]
            continue
        out, data, model = read_reply(path, user_text(msg))
        vnd += ((data.get("usage") or {}).get("x_ckey") or {}).get("cost") or 0
        _rows, err, _flag, _ng = check(ctx, segmap, out)
        qua += not err
        s = score_unit(gold[u], out)
        cau_truc += s["cau_truc"]
        for k in tong:
            tong[k] += s[k]
        ok = not err and s["cau_truc"] and not s["lech"] and s["m"] == s["g"] == s["x"]
        lines.append(f"### {u} ({model}): {'khớp' if ok else 'LỆCH'}; dòng gold {s['g']}, LLM {s['x']}, ghép {s['m']}; "
                     f"cấu trúc {'đúng' if s['cau_truc'] else 'SAI'}" + (f"; MÁY KIỂM: {'; '.join(m for _i, m in err)[:300]}" if err else ""))
        if not ok:
            lines += ["gold:"] + _fmt_rows(gold[u].get("dong")) + [f"  (ngoai_le {gold[u].get('ngoai_le')}, cac_muc_con {gold[u].get('cac_muc_con')})"]
            lines += ["LLM:"] + _fmt_rows((out or {}).get("dong") if isinstance(out, dict) else None)
            if isinstance(out, dict):
                lines.append(f"  (ngoai_le {out.get('ngoai_le')}, cac_muc_con {out.get('cac_muc_con')})")
        lines.append("")
    f1 = 2 * tong["m"] / (tong["g"] + tong["x"]) if tong["g"] + tong["x"] else 0
    acc = {f: (tong[f] / tong["m"] if tong["m"] else 0) for f in ("vai", "phuong_thuc", "cuc", "chu_the")}
    so = {"qua_may": qua / n, "f1_dong": f1, "vai": acc["vai"], "phuong_thuc": acc["phuong_thuc"], "cuc": acc["cuc"], "cau_truc": cau_truc / n}
    dat = all(so[k] >= v for k, v in NGUONG.items())
    head = [f"# Chấm lượt 2 `{PROMPT_VERSION}` trên bộ {bo} ({n} đơn vị){', thư mục ' + thu_muc if thu_muc else ''}: {'ĐẠT' if dat else 'KHÔNG ĐẠT'}\n"]
    head += [f"- {k}: {so[k]:.3f} (ngưỡng {v})" for k, v in NGUONG.items()]
    head += [f"- chu_the.loai đúng trên dòng ghép: {acc['chu_the']:.3f} (chỉ báo)", f"- dòng gold {tong['g']}, LLM {tong['x']}, ghép {tong['m']}",
             f"- thiếu phản hồi: {thieu}; chi phí: {vnd:.1f} VND\n"]
    name = f"cham_{bo}_{thu_muc}.md" if thu_muc else f"cham_{bo}.md"
    (RUN_DIR / PROMPT_VERSION / name).write_text("\n".join(head + lines) + "\n", encoding="utf-8")
    print("\n".join(head))
    return dat


def kiem_gold(bo):
    """Gold phải qua máy kiểm lượt 2 VÀ cổng cũ, như đầu ra LLM. Thoát mã 1 nếu có đơn vị lỗi."""
    g = json.loads(GOLD[bo].read_text(encoding="utf-8"))
    gold = {u["unit_id"]: u["dau_ra"] for u in g["don_vi"]}
    bad = 0
    for u, ctx, _msg, segmap in inputs(bo):
        _rows, err, _flag, _ng = check(ctx, segmap, gold[u])
        if err:
            bad += 1
            print(u, [m for _i, m in err])
    print(f"{len(gold)} đơn vị, lỗi {bad}")
    raise SystemExit(1 if bad else 0)


def nhap():
    """Kiểm mọi phản hồi của thư mục all/ rồi ghi cache 1.6A của lần chạy hiện tại (KLTN_LLM_RUN), đúng khuôn mà 1.6B đọc.
    Đơn vị không có phản hồi hay không phải JSON vẫn có mục (dòng rỗng, lỗi cổng) để 1.6B và báo cáo thấy chỗ thiếu."""
    import corpus
    if propositions.PROMPT_VERSION != PROMPT_VERSION:
        raise SystemExit(f"lần chạy {corpus.LLM_RUN!r} có menh_de.prompt_version {propositions.PROMPT_VERSION!r}, cần {PROMPT_VERSION!r}")
    src = RUN_DIR / PROMPT_VERSION / "all"
    units, models, dem = {}, {}, {"thieu": 0, "khong_json": 0, "qua": 0, "luot1_hong": 0}
    ctxs, sents = unit_sentences()
    luot1 = json.loads((segments.RUN_DIR / segments.PROMPT_VERSION / "doan_luot1.json").read_text(encoding="utf-8"))["cau"]
    chu_dieu = {}  # [A62] chữ theo Điều, để nhận thuật ngữ cố định khi trải liet_ke
    for u, c in ctxs.items():
        k = u.split(".")[1]
        chu_dieu[k] = chu_dieu.get(k, "") + " " + _nfc(" ".join(x for x in (c.get("heading"), c.get("chapeau"), c.get("text")) if x)).lower()
    so_dieu = lambda cum: sum(1 for t in chu_dieu.values() if cum in t)  # noqa: E731
    doan = {sid: x["doan"] for sid, x in luot1.items()}
    for u in ctxs:
        msg, segmap, hong = unit_input(u, ctxs[u], sents[u], doan)
        dem["luot1_hong"] += bool(hong)
        path = src / (u + ".json")
        out = None
        if path.exists():
            out, _data, model = read_reply(path, user_text(msg))
            models[model] = models.get(model, 0) + 1
            dem["khong_json"] += out is None
        else:
            dem["thieu"] += 1
        rows, err, flag, nguon = check(ctxs[u], segmap, out if out is not None else {"dong": []})
        if out is None:
            err = [(None, "không có đầu ra lượt 2")] + err
        flag = flag + ([(None, f"luot1_hong: {hong} câu lượt 1 hỏng, cả câu là một đoạn")] if hong else [])
        dem["qua"] += not err
        if not err:  # [A61] máy trải liet_ke sau cổng; đơn vị trượt cổng giữ nguyên (dòng của nó bị bỏ ở 1.6B)
            rows, f3 = trai_liet_ke(u, rows, " ".join(x for x in (ctxs[u].get("chapeau"), ctxs[u].get("text")) if x), so_dieu)
            flag = flag + f3
            dem["liet_ke_trai"] = dem.get("liet_ke_trai", 0) + sum(1 for _, m in f3 if m.startswith("liet_ke trải"))
            dem["liet_ke_giu"] = dem.get("liet_ke_giu", 0) + sum(1 for _, m in f3 if m.startswith("liet_ke giữ"))
            rows, f4 = bo_dong_chi_dan_chieu(rows)
            flag = flag + f4
            dem["bo_chi_dan_chieu"] = dem.get("bo_chi_dan_chieu", 0) + sum(1 for _, m in f4 if m.startswith("bỏ dòng"))
            rows, f5 = them_ket_luan_tieu_de(ctxs[u], rows)
            flag = flag + f5
            dem["ket_luan_tieu_de"] = dem.get("ket_luan_tieu_de", 0) + sum(1 for _, m in f5 if " thêm " in m)
        units[u] = {"dong": rows, "loi": [[i, m] for i, m in err], "co": [[i, m] for i, m in flag], "nguon": nguon}
    p = propositions.full_cache_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"prompt_version": PROMPT_VERSION, "model": "+".join(sorted(m for m in models if m)), "effort": "khong_co",
                             "units": units}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    n_rows = sum(len(v["dong"]) for v in units.values())
    n_err = sum(len(v["loi"]) for v in units.values())
    print(f"ghi {p}: {len(units)} đơn vị ({dem}), {n_rows} dòng, {n_err} lỗi cổng; phản hồi theo tuyến {models}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    if a[:1] == ["kiem-gold"] and len(a) == 2 and a[1] in GOLD:
        kiem_gold(a[1])
    elif a[:1] == ["goi"] and len(a) in (2, 3) and a[1] in ("dev", "test", "all"):
        goi(*a[1:])
    elif a[:1] == ["cham"] and len(a) in (2, 3) and a[1] in GOLD:
        cham(*a[1:])
    elif a == ["nhap"]:
        nhap()
    else:
        raise SystemExit(__doc__)
