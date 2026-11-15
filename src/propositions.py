"""1.6A bản làm lại (thiết kế docs/design/step_1_6a_propositions.md, quyết định A38): biến chữ luật thành danh sách MỆNH ĐỀ.

Khác `concepts.py` (1.6A cũ, gạch cụm theo bốn vai): mỗi dòng ra là một mệnh đề đúng/sai được, kèm chủ thể (đối số),
phương thức, cực, bổ ngữ, nhóm quy tắc và bằng chứng nguyên văn; câu dẫn, dẫn chiếu mờ, câu không quy phạm ra dòng
`bo_qua` có lý do (giữ để truy vết, A38 Q4). LLM đề xuất; máy chỉ kiểm được HÌNH và NGUỒN (cổng ở `gate_unit`),
không kiểm được nghĩa: nghĩa đo bằng bộ thí điểm 30 đơn vị có đáp án (A38 Q5, K10).

Hiện module chỉ phục vụ THÍ ĐIỂM, chưa nối vào run_all (nối sau khi thí điểm đạt, A38 T9). Phần LLM chạy bằng phiên
Claude Code trong thư mục hộp cát ngoài repo, như A36 (không gọi API).

Chạy ở gốc repo:  python -X utf8 -I src/propositions.py <lệnh>
  kiem-dap-an [file]        chạy cổng trên file đáp án (mặc định data/pilot_propositions/gold_draft.json)
  xuat <thư mục mới> [model] [effort] [--tat-ca]   dựng hộp cát: 30 đơn vị thí điểm, hoặc cả 204 lô với --tat-ca
  nhap <thư mục>            (tat_ca ghi data/llm_cache/propositions/<doc>.json)
                            đọc out/ + nhat_ky.tsv, kiểm; thí điểm ghi data/pilot_propositions/llm_output.json
  so [file llm] [file báo cáo]   so đầu ra LLM với đáp án (mặc định llm_output.json, comparison.md)
  gemini [thi_diem|tat_ca] [chinh|kiem]   chạy phần LLM bằng Gemini (--llm live; cần GEMINI_API_KEY và .venv)
"""
import json, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import concepts as C, corpus, llm_client as L  # noqa: E402

PROMPT_VERSION = "menh-de-3"
PILOT_DIR = pathlib.Path("data/pilot_propositions")
GOLD = PILOT_DIR / "gold_draft.json"
LLM_OUT = PILOT_DIR / "llm_output.json"
REPORT = PILOT_DIR / "comparison.md"

# Tập giá trị của mô tả bước và A38. Đổi ở đây là đổi khuôn: phải sửa cả mô tả bước, lời nhắc và test.
LOAI = {"menh_de", "con_tro", "bo_qua", "chua_ro"}
VAI = {"ket_luan", "dieu_kien", "ngoai_le"}
PHUONG_THUC = {"duoc", "phai", "cam", "khong_ap_dung", "khong"}
CUC = {"khang_dinh", "phu_dinh"}
KIEU = {"W", "E", "C", "J", "G", "D", "A", "?"}
NGUON = {"chinh", "cau_dan", "tieu_de"}
SCOPE = {"this_clause", "group", "unknown"}
NGUYEN_NHAN = {"pham_vi_bo_ngu", "tach_hay_giu_chung", "phuong_thuc", "chu_the", "khac"}
MUC_CON = {"va", "hoac", "danh_sach"}
MA_LY_DO = {"tach", "giu_chung", "gan_bo_ngu", "chua_ro", "cau_dan", "dan_chieu_mo", "dan_chieu_ngoai", "khong_quy_pham", "ke_thua"}
MA_BO_QUA = {"cau_dan", "dan_chieu_mo", "dan_chieu_ngoai", "khong_quy_pham"}
FIELDS = ("loai", "vai", "menh_de", "chu_the", "doi_so", "phuong_thuc", "cuc", "bo_ngu", "nhom_hoac", "cac_muc_con",
          "chua_ro", "trich", "targets", "quy_tac", "gan_vao", "liet_ke")
LLM_REASON, GOLD_REASON = "ly_do_llm", "ly_do_dap_an"  # hai trường riêng để đối chiếu (A38 Q3b)
LONG_SYL = 15  # menh-de-3: lõi phải ngắn để tái dùng; từ 15 âm tiết là cờ (đo 34 lô menh-de-2: 22% vượt)

SYSTEM = """Bạn tách các đơn vị của Bộ luật Lao động Việt Nam thành DÒNG. Mỗi đơn vị có: tieu_de_dieu, khoan_cha (câu dẫn của cha, có thể rỗng), chu_don_vi (chữ cần tách), dan_chieu (dẫn chiếu đã giải, kèm mã đích). Chỉ tách chu_don_vi; tiêu đề và câu dẫn chỉ để lấy chủ thể, phương thức, vị ngữ bị lược.

## Loại dòng (loai)
- menh_de: một điều đúng/sai được.
- con_tro: dẫn chiếu đã giải ("trừ trường hợp quy định tại ...", "theo quy định tại ..."); targets lấy từ dan_chieu.
- bo_qua: không thành mệnh đề; ly_do_llm.ma: cau_dan (phần chỉ dẫn vào danh sách, "... sau đây:") | dan_chieu_mo ("theo quy định của pháp luật") | dan_chieu_ngoai (một luật khác, "theo quy định của Luật Công đoàn") | khong_quy_pham (câu chính sách, định hướng, không có hành vi kiểm được).
- chua_ro: cả dòng không xác định được.

## Luật tách
1. TÁCH khi từng phần kiểm được đúng/sai riêng VÀ vi phạm từng phần có ý nghĩa pháp lý riêng. GIỮ CHUNG khi là một yêu cầu tập thể. Không tách chỉ vì có nhiều danh từ.
2. menh_de chỉ giữ LÕI: động từ (hoặc tính chất) + tân ngữ chính, càng ngắn càng tốt, để cùng một việc ở các Điều khác nhau ra cùng chữ. Danh sách liệt kê (từ 3 mục) của tân ngữ hay phạm vi đưa vào liet_ke (mỗi mục chép nguyên văn), không để trong menh_de.
3. Chữ dùng chung đứng ĐẦU chuỗi ("không" trong "không A, B, C") hiểu cho từng mục. Bổ ngữ đứng CUỐI phải xác định phạm vi trong bo_ngu: this_clause | group | unknown (unknown thì thêm chua_ro nguyen_nhan pham_vi_bo_ngu).
4. bo_ngu chỉ cho cụm mà bỏ đi thì vẫn cùng loại hành vi (nơi chốn, căn cứ, cách thức phụ). Cụm làm nên chính hành vi (thời điểm, mức, cách thức phân biệt) giữ trong menh_de: "làm việc trên cao" không rút thành "làm việc". Dẫn chiếu không bao giờ là bổ ngữ.
5. Câu dẫn: danh sách là TÂN NGỮ ("có các nghĩa vụ sau đây") thì câu dẫn ra bo_qua cau_dan, mục con là ket_luan kế thừa chủ thể và phương thức. Danh sách là ĐIỀU KIỆN ("trong trường hợp sau đây") thì phần nội dung câu dẫn ra ket_luan (một lần, ở câu dẫn), phần dẫn ra bo_qua, mục con là dieu_kien. cac_muc_con của dòng cau_dan: va (điều kiện hay yêu cầu phải đủ HẾT) | hoac (trường hợp, MỘT là đủ) | danh_sach (quyền hay mục độc lập).
6. Định nghĩa khái niệm "X là Y": dấu hiệu của Y là dieu_kien, thêm ket_luan "là X". Câu nêu giá trị, mức ("thời hạn ... là N ngày") ra một ket_luan.
7. quy_tac (q1, q2...) gom dieu_kien và ket_luan của cùng một quy tắc. "Hoặc" giữa điều kiện trong một quy tắc: cùng nhom_hoac ("h1"). "Hoặc" mà một vế có "và": tách nhiều quy tắc.

## Trường
- vai: ket_luan | dieu_kien | ngoai_le. con_tro "trừ ..." có vai ngoai_le; con_tro khác lấy vai của dòng nó bổ nghĩa.
- menh_de: đã bỏ chủ thể, chữ phương thức, chữ phủ định, bổ ngữ, liệt kê. MỌI âm tiết của menh_de phải có trong trich của dòng đó.
- chu_the: {"chu": nguyên văn, "loai": mã hoặc danh sách mã khi chủ thể chung, "nguon": chinh | cau_dan | tieu_de}, hoặc bỏ. Mã: W người lao động, E người sử dụng lao động, C hợp đồng, J công việc, G vùng, D ngày, A số tiền, ? chưa biết. Người chỉ chịu tác động là đối số, không phải chủ thể.
- doi_so: [{"loai": mã}] các đối số khác.
- phuong_thuc: duoc (được, có quyền, có thể) | phai (phải, có nghĩa vụ) | cam (cấm, không được làm) | khong_ap_dung (tuyên bố một quy định không áp cho một nhóm trường hợp) | khong (mô tả, điều kiện, định nghĩa).
- cuc: khang_dinh | phu_dinh; chỉ phủ định menh_de: duoc + phu_dinh là "được không bị X"; "không phải X" (không có nghĩa vụ) ghi duoc + phu_dinh.
- BẪY: "không được + động từ" là cam (không được làm X) hoặc bị động phủ định (không được người khác làm cho: khong + phu_dinh, menh_de giữ "được ..."). "Được + động từ" có thể là bị động, không phải quyền.
- chua_ro: [{"thanh_phan", "nguyen_nhan": pham_vi_bo_ngu | tach_hay_giu_chung | phuong_thuc | chu_the | khac, "cau_hoi"}], mỗi chỗ một mục. Không đoán.
- trich: chuỗi chép NGUYÊN VĂN, liền, từ tiêu đề, câu dẫn hoặc chu_don_vi; chủ thể hay phương thức kế thừa thì có cả mẩu chứa nó.
- targets (con_tro): mã từ dan_chieu; không giải được thì rỗng kèm chua_ro. gan_vao (con_tro): số thứ tự (từ 0) của dòng menh_de nó bổ nghĩa, null nếu chặn cả quy tắc.
- ly_do_llm: chỉ ca khó (tach | giu_chung | gan_bo_ngu | chua_ro | ke_thua) và mọi dòng bo_qua: {"ma", "giai_thich": một câu ngắn}.
- TRƯỜNG RỖNG THÌ BỎ (chuỗi rỗng, danh sách rỗng, null): máy tự điền. Luôn có loai và trich; menh_de có thêm vai, menh_de, phuong_thuc, cuc, quy_tac.

## Ví dụ
khoan_cha "Người sử dụng lao động có các nghĩa vụ sau đây:" → {"loai":"bo_qua","cac_muc_con":"danh_sach","trich":["Người sử dụng lao động có các nghĩa vụ sau đây:"],"ly_do_llm":{"ma":"cau_dan","giai_thich":"Câu dẫn danh sách nghĩa vụ."}}
Mục con "...; tôn trọng danh dự, nhân phẩm của người lao động;" → {"loai":"menh_de","vai":"ket_luan","menh_de":"tôn trọng danh dự, nhân phẩm của người lao động","chu_the":{"chu":"Người sử dụng lao động","loai":"E","nguon":"cau_dan"},"doi_so":[{"loai":"W"}],"phuong_thuc":"phai","cuc":"khang_dinh","trich":["Người sử dụng lao động có các nghĩa vụ","tôn trọng danh dự, nhân phẩm của người lao động"],"quy_tac":"q1"}
"Người sử dụng lao động phải cung cấp thông tin trung thực cho người lao động về ..., tiền lương, hình thức trả lương, bảo hiểm xã hội, ..." → {"loai":"menh_de","vai":"ket_luan","menh_de":"cung cấp thông tin trung thực","chu_the":{"chu":"Người sử dụng lao động","loai":"E","nguon":"chinh"},"doi_so":[{"loai":"W"}],"phuong_thuc":"phai","cuc":"khang_dinh","liet_ke":["tiền lương","hình thức trả lương","bảo hiểm xã hội","..."],"trich":["Người sử dụng lao động phải cung cấp thông tin trung thực cho người lao động"],"quy_tac":"q1","ly_do_llm":{"ma":"giu_chung","giai_thich":"Một nghĩa vụ thông tin; danh sách nội dung đưa vào liet_ke."}}
Tiêu đề "Hành vi người sử dụng lao động không được làm khi giao kết, thực hiện hợp đồng lao động", chữ "Giữ bản chính giấy tờ tùy thân, văn bằng, chứng chỉ của người lao động." → {"loai":"menh_de","vai":"ket_luan","menh_de":"giữ bản chính giấy tờ tùy thân, văn bằng, chứng chỉ của người lao động","chu_the":{"chu":"người sử dụng lao động","loai":"E","nguon":"tieu_de"},"doi_so":[{"loai":"W"}],"phuong_thuc":"cam","cuc":"khang_dinh","trich":["Hành vi người sử dụng lao động không được làm","Giữ bản chính giấy tờ tùy thân, văn bằng, chứng chỉ của người lao động"],"quy_tac":"q1"}
Tiêu đề "Nghĩa vụ của người lao động khi ... trái pháp luật", chữ "Không được trợ cấp thôi việc." (bị động) → {"loai":"menh_de","vai":"ket_luan","menh_de":"được trợ cấp thôi việc","chu_the":{"chu":"người lao động","loai":"W","nguon":"tieu_de"},"phuong_thuc":"khong","cuc":"phu_dinh","trich":["Nghĩa vụ của người lao động","Không được trợ cấp thôi việc"],"quy_tac":"q1"} cộng một dieu_kien lấy từ tiêu đề.
Định nghĩa "Tổ chức đại diện người sử dụng lao động là tổ chức được thành lập hợp pháp, đại diện và bảo vệ quyền, lợi ích hợp pháp của người sử dụng lao động trong quan hệ lao động." → dieu_kien "được thành lập hợp pháp" (bị động, khong); dieu_kien "đại diện và bảo vệ quyền, lợi ích hợp pháp của người sử dụng lao động" (bo_ngu "trong quan hệ lao động", this_clause); ket_luan khong "là tổ chức đại diện người sử dụng lao động"; cả ba q1.

## Đầu ra
JSON thuần, không chữ giải thích: {"units": [{"unit_id": "...", "dong": [...]}]}. Mỗi unit_id của lô đúng một mục, mỗi mục ít nhất một dòng."""

SCHEMA = {"units": [{"unit_id": "string", "dong": [{f: "xem system.txt" for f in FIELDS + (LLM_REASON,)}]}]}


def syllables(s):
    return re.findall(r"\w+", (s or "").lower())


def contexts(doc_id=None):
    """{unit_id: {heading, chapeau, text, refs}}: đúng ngữ cảnh 1.6A cũ (concepts.unit_contexts, A26, A35) cộng dẫn chiếu 1.2."""
    _doc, units, labels, _nodes, refs = C.load_inputs(doc_id or corpus.BASE_DOC_ID)
    out = {}
    for c in C.unit_contexts(units, labels):
        out[c["id"]] = dict(c, refs=[{"cum": r["evidence"], "dich": r["o"]} for r in refs.get(c["id"], [])])
    return out


def user_message(batch):
    return json.dumps({"don_vi": [{"unit_id": c["id"], "tieu_de_dieu": c["heading"], "khoan_cha": c["chapeau"],
                                   "chu_don_vi": c["text"], "dan_chieu": c["refs"]} for c in batch]},
                      ensure_ascii=False, indent=1)


def _in_ctx(s, ctx):
    return bool(s) and any(s in part for part in (ctx["heading"], ctx["chapeau"], ctx["text"]))


def _kieu_ok(k):
    return k in KIEU if isinstance(k, str) else isinstance(k, list) and len(k) > 1 and all(x in KIEU for x in k)


DEFAULTS = {"loai": "", "vai": "", "menh_de": "", "chu_the": None, "doi_so": [], "phuong_thuc": "", "cuc": "", "bo_ngu": [],
            "nhom_hoac": None, "cac_muc_con": None, "chua_ro": [], "trich": [], "targets": [], "quy_tac": None, "gan_vao": None,
            "liet_ke": []}


def normalize(rows, reason_field=LLM_REASON):
    """Điền trường bị bỏ bằng giá trị rỗng (menh-de-3 cho LLM bỏ trường rỗng để đầu ra ngắn, đỡ token). Trường thừa giữ
    nguyên để cổng bắt. Không sửa gì khác."""
    if not isinstance(rows, list):
        return rows
    out = []
    for d in rows:
        if isinstance(d, dict):
            d = {**{k: (list(v) if isinstance(v, list) else v) for k, v in DEFAULTS.items()}, reason_field: None, **d}
            ct = d.get("chu_the")
            if isinstance(ct, dict) and isinstance(ct.get("loai"), list) and len(ct["loai"]) == 1:
                d["chu_the"] = {**ct, "loai": ct["loai"][0]}  # lược đồ Gemini ghi loai luôn là mảng
        out.append(d)
    return out


def gate_unit(ctx, rows, reason_field=LLM_REASON):
    """-> (lỗi, cờ): hai danh sách (chỉ số dòng, thông điệp). Lỗi = vi phạm khuôn hoặc nguồn (máy chứng minh được);
    cờ = dấu hiệu đáng xem nhưng có ca đúng (ví dụ "được trả lương" là chữ đúng). Không kiểm được nghĩa."""
    err, flag = [], []
    if not isinstance(rows, list) or not rows:
        return [(None, "đơn vị không có dòng nào")], flag
    menh_de_idx = {i for i, d in enumerate(rows) if isinstance(d, dict) and d.get("loai") == "menh_de"}
    targets_ok = {r["dich"] for r in ctx["refs"]}
    for i, d in enumerate(rows):
        def E(m):
            err.append((i, m))
        if not isinstance(d, dict):
            E("dòng không phải object")
            continue
        want = set(FIELDS) | {reason_field}
        if set(d) != want:
            E(f"trường thiếu {sorted(want - set(d))} / thừa {sorted(set(d) - want)}")
            continue
        loai = d["loai"]
        if loai not in LOAI:
            E(f"loai {loai!r}")
            continue
        trich = d["trich"] if isinstance(d["trich"], list) else []
        if not trich:
            E("trich rỗng")
        for t in trich:
            if not _in_ctx(t, ctx):
                E(f"trich không nguyên văn: {t[:60]!r}")
        reason = d[reason_field]
        if reason is not None and (not isinstance(reason, dict) or reason.get("ma") not in MA_LY_DO or not reason.get("giai_thich")):
            E(f"{reason_field} sai khuôn {reason!r}")
        for c in d["chua_ro"] or []:
            if not isinstance(c, dict) or c.get("nguyen_nhan") not in NGUYEN_NHAN:
                E(f"chua_ro sai khuôn {c!r}")
        if loai == "menh_de":
            if not d["menh_de"]:
                E("menh_de rỗng")
            if d["vai"] not in VAI or d["phuong_thuc"] not in PHUONG_THUC or d["cuc"] not in CUC:
                E(f"vai/phuong_thuc/cuc {d['vai']!r}/{d['phuong_thuc']!r}/{d['cuc']!r}")
            if not d["quy_tac"]:
                E("menh_de thiếu quy_tac")
            pool = set(syllables(" ".join(trich)))
            ngoai = [w for w in syllables(d["menh_de"]) if w not in pool]
            if ngoai:
                E(f"âm tiết không có trong trich: {ngoai}")  # cổng (c), A38 Q2
            if re.search(r"(sau đây|như sau)\s*:?\s*$", d["menh_de"] or "") or (d["menh_de"] or "").rstrip().endswith(":"):
                E("menh_de là câu dẫn")
            ct = d["chu_the"]
            if ct is not None:
                if not isinstance(ct, dict) or set(ct) != {"chu", "loai", "nguon"} or not _kieu_ok(ct["loai"]) or ct["nguon"] not in NGUON:
                    E(f"chu_the sai khuôn {ct!r}")
                else:
                    if not _in_ctx(ct["chu"], ctx):
                        E(f"chu_the.chu không nguyên văn {ct['chu']!r}")
                    src = {"cau_dan": ctx["chapeau"], "tieu_de": ctx["heading"]}.get(ct["nguon"])
                    if src is not None and not any(t in src for t in trich):
                        E(f"chủ thể lấy từ {ct['nguon']} nhưng trich không có mẩu nào từ đó")
            for a in d["doi_so"] or []:
                if not isinstance(a, dict) or not _kieu_ok(a.get("loai")):
                    E(f"doi_so sai khuôn {a!r}")
            for b in d["bo_ngu"] or []:
                if not isinstance(b, dict) or b.get("scope") not in SCOPE or not _in_ctx(b.get("original_text"), ctx):
                    E(f"bo_ngu sai khuôn hoặc không nguyên văn {b!r}")
            for x in d["liet_ke"] or []:
                if not isinstance(x, str) or not _in_ctx(x, ctx):
                    E(f"liet_ke không nguyên văn {x!r}")
            words = syllables(d["menh_de"])
            if re.search(r"\b(phải|cấm)\b", (d["menh_de"] or "").lower()) or (words[:1] == ["không"]):
                flag.append((i, "menh_de còn chữ phương thức/phủ định"))
            if len(words) >= LONG_SYL:
                flag.append((i, f"menh_de dài {len(words)} âm tiết"))
        elif loai == "bo_qua":
            if not reason or reason.get("ma") not in MA_BO_QUA:
                E("bo_qua phải có lý do cau_dan/dan_chieu_mo/dan_chieu_ngoai/khong_quy_pham")
            if d["cac_muc_con"] not in (None, *MUC_CON) or (d["cac_muc_con"] and (reason or {}).get("ma") != "cau_dan"):
                E(f"cac_muc_con {d['cac_muc_con']!r} chỉ dùng cho câu dẫn")
        elif loai == "con_tro":
            for t in d["targets"] or []:
                if t not in targets_ok:
                    E(f"target không có trong dẫn chiếu 1.2: {t}")
            if not d["targets"] and not d["chua_ro"]:
                E("con_tro không targets mà không có chua_ro")  # A38 K8
            g = d["gan_vao"]
            if g is not None and g not in menh_de_idx:
                E(f"gan_vao {g!r} không trỏ dòng menh_de")
    return err, flag


def load_gold(path=GOLD):
    """{unit_id đầy đủ: dòng} của file đáp án (file ghi mã đơn vị rút gọn)."""
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    return {f"{corpus.BASE_DOC_ID}.{x['unit']}": normalize(x["dong"], GOLD_REASON) for x in data["don_vi"]}


def pilot_batches(ctxs, gold):
    """Mỗi Điều một lô, theo thứ tự tài liệu (như 1.6A cũ: một Điều mỗi lô); chỉ gồm đơn vị thí điểm."""
    lots, cur = [], None
    for uid, c in ctxs.items():
        if uid not in gold:
            continue
        d = C.dieu_of(uid)
        if d != cur:
            lots.append([])
            cur = d
        lots[-1].append(c)
    return lots


def kiem_dap_an(path=GOLD):
    ctxs, gold = contexts(), load_gold(path)
    n_err = 0
    for uid, rows in gold.items():
        if uid not in ctxs:
            print(f"{uid}: không nằm trong đầu vào 1.6A")
            n_err += 1
            continue
        err, flag = gate_unit(ctxs[uid], rows, GOLD_REASON)
        for i, m in err:
            print(f"LỖI {uid.split('.', 1)[1]}#{i}: {m}")
        for i, m in flag:
            print(f"cờ  {uid.split('.', 1)[1]}#{i}: {m}")
        n_err += len(err)
    print(f"{len(gold)} đơn vị, {sum(map(len, gold.values()))} dòng, lỗi cổng: {n_err}")
    return n_err


HUONG_DAN = """# Việc của bạn

Thư mục này là toàn bộ thế giới của bạn. Bạn (và mọi subagent bạn tạo) chỉ đọc và ghi trong thư mục này. Không mở thư mục cha hay thư mục nào khác, không tìm hiểu dữ liệu đến từ đâu hay dùng vào việc gì.

Có @N@ lô trong `lo/` (`001.json` đến `@N@.json`). Với mỗi lô, làm đúng theo `system.txt`, ghi kết quả vào `out/` cùng số (`out/001.json` cho `lo/001.json`).

## Model
Việc này phải do model `@MODEL@` làm, mức effort `@EFFORT@`. Mỗi subagent đặt tường minh cả model (tên tắt `@ALIAS@`) và effort `@EFFORT@`. ID model chính xác của subagent khác `@MODEL@`, hoặc không đặt được effort, thì dừng lại và báo người dùng, đừng làm.

## Chia việc theo khối
Chia các lô cần làm thành các KHỐI liền nhau, mỗi khối tối đa @KHOI@ lô, theo thứ tự số lô. Mỗi khối giao cho MỘT subagent mới (Agent tool), đặt tham số model và effort tường minh như ở trên, chạy song song tối đa 4 subagent. Không tạo được subagent hoặc không đặt được model, effort thì dừng và báo người dùng.

Lời giao cho subagent (thay AAA, BBB bằng lô đầu và cuối của khối), chỉ gồm đúng thế này:
> Đọc `system.txt` một lần. Rồi lần lượt với từng lô NNN từ AAA đến BBB mà `out/NNN.json` chưa có: đọc `lo/NNN.json`, làm đúng theo `system.txt`, ghi kết quả vào `out/NNN.json` là JSON thuần đúng khuôn ở mục "Đầu ra" của `system.txt` (đúng tên trường, không thêm trường, trường rỗng thì bỏ). Mỗi lô xét riêng theo chữ của lô đó. Không đọc hay ghi file nào khác, không đọc lại `out/` của lô khác. Cuối cùng trả lời mỗi lô một dòng: NNN, một ký tự tab, rồi ID model chính xác của bạn.

Bạn (phiên chính) KHÔNG tự làm lô nào. Ghi các dòng trả lời vào `nhat_ky.tsv` (một dòng mỗi lô, dạng `NNN<tab>ID model`).

## Cấm
- Không viết script, regex hay công cụ nào để sinh hoặc sửa dòng. Mọi dòng do model đọc chữ mà viết.
- Không sửa `out/NNN.json` sau khi subagent đã ghi. Không chạy lại một lô trừ khi người dùng bảo.

## Xong
Báo: số file đã ghi, nội dung `nhat_ky.tsv`, lô nào lỗi.
"""


def model():
    return L.load_config()["trich.model"]


# Model chạy thí điểm ghi trong hộp cát (cau_hinh.json), KHÔNG đổi trich.model: đổi nó làm replay 1.6A cũ vỡ vì khoá cache
# có tên model (A37 (4)). Effort không kiểm được (nhat_ky chỉ có model tự khai), chỉ ghi lại để truy vết.
ALIAS = {"claude-sonnet-5-5": "sonnet", "claude-opus-5-5": "opus", "claude-haiku-5-5": "haiku"}


def sandbox_config(d):
    f = pathlib.Path(d) / "cau_hinh.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"model": model(), "effort": None}


FULL_OUT = pathlib.Path("data/llm_cache") / "propositions"


def lots_for(pham_vi, ctxs):
    """thi_diem: 30 đơn vị, một lô mỗi Điều; tat_ca: mọi đơn vị 1.6A, chia lô đúng như 1.6A cũ (concepts.make_batches:
    một Điều mỗi lô, Điều dài tách lô), để số lô và ranh giới lô so được với bản cũ."""
    if pham_vi == "thi_diem":
        return pilot_batches(ctxs, load_gold())
    if pham_vi == "tat_ca":
        return C.make_batches(list(ctxs.values()))
    raise SystemExit(f"phạm vi lạ: {pham_vi}")


def xuat(thu_muc, run_model=None, effort="high", pham_vi="thi_diem", khoi=20):
    d = pathlib.Path(thu_muc)
    if d.exists() and any(d.iterdir()):
        raise SystemExit(f"{d} đã có nội dung, không ghi đè")
    lots = lots_for(pham_vi, contexts())
    (d / "lo").mkdir(parents=True, exist_ok=True)
    (d / "out").mkdir(exist_ok=True)
    (d / "system.txt").write_text(SYSTEM + "\n", encoding="utf-8", newline="\n")
    for i, b in enumerate(lots, 1):
        (d / "lo" / f"{i:03d}.json").write_text(user_message(b) + "\n", encoding="utf-8", newline="\n")
    m = run_model or model()
    (d / "HUONG_DAN.md").write_text(HUONG_DAN.replace("@MODEL@", m).replace("@ALIAS@", ALIAS.get(m, m)).replace("@EFFORT@", effort).replace("@KHOI@", str(khoi))
                                    .replace("@N@", f"{len(lots):03d}"), encoding="utf-8", newline="\n")
    (d / "cau_hinh.json").write_text(json.dumps({"model": m, "effort": effort, "prompt_version": PROMPT_VERSION, "pham_vi": pham_vi, "khoi": khoi}) + "\n", encoding="utf-8")
    print(f"đã dựng {d}: {len(lots)} lô, {sum(map(len, lots))} đơn vị, model {m}, effort {effort}, lời nhắc {PROMPT_VERSION}")


def nhap(thu_muc, out_path=None):
    d, ctxs = pathlib.Path(thu_muc), contexts()
    cfg = sandbox_config(d)
    pham_vi = cfg.get("pham_vi", "thi_diem")
    if cfg.get("prompt_version", PROMPT_VERSION) != PROMPT_VERSION or (d / "system.txt").read_text(encoding="utf-8") != SYSTEM + "\n":
        raise SystemExit(f"hộp cát dựng với lời nhắc {cfg.get('prompt_version')}, code đang là {PROMPT_VERSION}: không nhập")
    lots, want = lots_for(pham_vi, ctxs), cfg["model"]
    if out_path is None:
        out_path = LLM_OUT if pham_vi == "thi_diem" else FULL_OUT / f"{corpus.BASE_DOC_ID}.json"
    log = {}
    if (d / "nhat_ky.tsv").exists():
        for line in (d / "nhat_ky.tsv").read_text(encoding="utf-8").splitlines():
            p = [x.strip() for x in line.split("\t")]
            if len(p) >= 2 and p[0].isdigit():
                log[int(p[0])] = p[1]
    out, bad_lot = {}, []
    for n, lot in enumerate(lots, 1):
        f = d / "out" / f"{n:03d}.json"
        if not f.exists():
            bad_lot.append((n, "chưa có file"))
            continue
        if (d / "lo" / f"{n:03d}.json").read_text(encoding="utf-8") != user_message(lot) + "\n":
            bad_lot.append((n, "lo/ khác đầu vào hiện tại (dữ liệu đã đổi sau khi dựng hộp cát)"))
            continue
        if log.get(n) != want:
            bad_lot.append((n, f"nhat_ky báo {log.get(n)!r}, cần {want}"))
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            items = {it["unit_id"]: it["dong"] for it in data["units"]}
        except (ValueError, KeyError, TypeError) as e:
            bad_lot.append((n, f"sai hình: {e}"))
            continue
        ids = {c["id"] for c in lot}
        if set(items) != ids:
            bad_lot.append((n, f"unit_id lệch: thiếu {sorted(ids - set(items))}, thừa {sorted(set(items) - ids)}"))
            continue
        for uid, rows in items.items():
            rows = normalize(rows)
            err, flag = gate_unit(ctxs[uid], rows)
            out[uid] = {"dong": rows, "loi": [[i, m] for i, m in err], "co": [[i, m] for i, m in flag]}
    out_path = pathlib.Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"prompt_version": PROMPT_VERSION, "model": want, "effort": cfg["effort"], "units": out}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    n_rows = sum(len(v["dong"]) for v in out.values())
    n_err = sum(len(v["loi"]) for v in out.values())
    print(f"ghi {out_path}:{len(out)} đơn vị, {n_rows} dòng, {n_err} lỗi cổng, {sum(len(v['co']) for v in out.values())} cờ")
    for n, why in bad_lot:
        print(f"  lô {n:03d} KHÔNG nhận: {why}")
    return bad_lot


def _key(d):
    return set(syllables(d["menh_de"] if d["loai"] == "menh_de" else " ".join(d["trich"])))


def _kieu(ct):
    if not ct:
        return None
    return tuple(sorted(ct["loai"])) if isinstance(ct["loai"], list) else ct["loai"]


def match_rows(gold_rows, llm_rows, min_sim=0.5):
    """Ghép dòng cùng loai theo độ trùng âm tiết (Jaccard), tham lam từ cặp giống nhất. -> [(gi, li)], thiếu, thừa.
    Chỉ là cách ghép để người đọc so; ghép sai thì báo cáo hiện cả hai dòng nên người phán vẫn thấy."""
    pairs = []
    for gi, g in enumerate(gold_rows):
        for li, x in enumerate(llm_rows):
            if g["loai"] != x["loai"]:
                continue
            a, b = _key(g), _key(x)
            sim = len(a & b) / len(a | b) if a | b else 1.0
            if sim >= min_sim:
                pairs.append((sim, gi, li))
    used_g, used_l, out = set(), set(), []
    for sim, gi, li in sorted(pairs, reverse=True):
        if gi not in used_g and li not in used_l:
            used_g.add(gi)
            used_l.add(li)
            out.append((gi, li))
    return sorted(out), [i for i in range(len(gold_rows)) if i not in used_g], [i for i in range(len(llm_rows)) if i not in used_l]


# Field so được theo loại dòng; tỉ lệ khớp chỉ tính trên đúng loại dòng có field đó (bo_qua không "khớp" phuong_thuc).
SO_FIELDS = {"menh_de": ("vai", "menh_de", "phuong_thuc", "cuc", "chu_the.loai", "doi_so", "bo_ngu", "liet_ke", "nhom_hoac", "chua_ro", "quy_tac"),
             "bo_qua": ("ly_do.ma", "cac_muc_con"),
             "con_tro": ("vai", "targets", "gan_vao", "chua_ro")}


def diff_row(g, x):
    """Các field lệch giữa hai dòng đã ghép (trừ quy_tac và gan_vao: hai field này so theo cả đơn vị, xem diff_unit)."""
    out = []
    if g["loai"] in ("menh_de", "con_tro") and g["vai"] != x["vai"]:
        out.append(("vai", g["vai"], x["vai"]))
    gc = sorted(c["nguyen_nhan"] for c in g["chua_ro"] or [])
    xc = sorted(c["nguyen_nhan"] for c in x["chua_ro"] or [])
    if g["loai"] != "bo_qua" and gc != xc:
        out.append(("chua_ro", gc, xc))
    if g["loai"] == "menh_de":
        for f in ("phuong_thuc", "cuc"):
            if g[f] != x[f]:
                out.append((f, g[f], x[f]))
        if " ".join(syllables(g["menh_de"])) != " ".join(syllables(x["menh_de"])):
            out.append(("menh_de", g["menh_de"], x["menh_de"]))
        if _kieu(g["chu_the"]) != _kieu(x["chu_the"]):
            out.append(("chu_the.loai", _kieu(g["chu_the"]), _kieu(x["chu_the"])))
        gd, xd = [_kieu({"loai": a["loai"]}) for a in g["doi_so"]], [_kieu({"loai": a["loai"]}) for a in x["doi_so"]]
        if gd != xd:
            out.append(("doi_so", gd, xd))
        if bool(g["nhom_hoac"]) != bool(x["nhom_hoac"]):
            out.append(("nhom_hoac", g["nhom_hoac"], x["nhom_hoac"]))
        if sorted(g["liet_ke"]) != sorted(x["liet_ke"]):
            out.append(("liet_ke", g["liet_ke"], x["liet_ke"]))
        gb = {(b["original_text"], b["scope"]) for b in g["bo_ngu"]}
        xb = {(b["original_text"], b["scope"]) for b in x["bo_ngu"]}
        if gb != xb:
            out.append(("bo_ngu", sorted(gb), sorted(xb)))
    if g["loai"] == "bo_qua":
        gm, xm = (g.get(GOLD_REASON) or {}).get("ma"), (x.get(LLM_REASON) or {}).get("ma")
        if gm != xm:
            out.append(("ly_do.ma", gm, xm))
        if g["cac_muc_con"] != x["cac_muc_con"]:
            out.append(("cac_muc_con", g["cac_muc_con"], x["cac_muc_con"]))
    if g["loai"] == "con_tro" and sorted(g["targets"]) != sorted(x["targets"]):
        out.append(("targets", g["targets"], x["targets"]))
    return out


def diff_unit(G, X, pairs):
    """{gi: [(field, ĐA, LLM)]} cho hai field so theo cả đơn vị. quy_tac: hai dòng menh_de cùng nhóm ở ĐA thì phải cùng nhóm ở
    LLM và ngược lại (mã q1, q2 tự đặt nên không so chữ). gan_vao: dòng đích của ĐA, đổi qua phép ghép, phải là dòng đích của LLM."""
    m = dict(pairs)
    md = [(gi, li) for gi, li in pairs if G[gi]["loai"] == "menh_de"]
    out = {}
    for gi, li in md:
        bad = [(gj, lj) for gj, lj in md if gj != gi and (G[gi]["quy_tac"] == G[gj]["quy_tac"]) != (X[li]["quy_tac"] == X[lj]["quy_tac"])]
        if bad:
            out.setdefault(gi, []).append(("quy_tac", f"{G[gi]['quy_tac']} (lệch nhóm với ĐA#{[b[0] for b in bad]})", X[li]["quy_tac"]))
    for gi, li in pairs:
        if G[gi]["loai"] == "con_tro":
            g_to = G[gi]["gan_vao"]
            want = None if g_to is None else m.get(g_to, "dòng chưa ghép")
            if want != X[li]["gan_vao"]:
                out.setdefault(gi, []).append(("gan_vao", f"{g_to} (tức LLM#{want})", X[li]["gan_vao"]))
    return out


def _fmt(d, reason_field):
    if d["loai"] == "menh_de":
        ct = d["chu_the"] or {}
        s = f"menh_de/{d['vai']} [{d['phuong_thuc']},{d['cuc']}] «{d['menh_de']}» chủ thể={ct.get('chu', '-')}:{_kieu(d['chu_the'])} {d['quy_tac']}"
        if d["bo_ngu"]:
            s += f" bổ ngữ={[(b['original_text'], b['scope']) for b in d['bo_ngu']]}"
        if d["liet_ke"]:
            s += f" liệt kê={d['liet_ke']}"
        if d["nhom_hoac"]:
            s += f" hoặc={d['nhom_hoac']}"
    elif d["loai"] == "con_tro":
        s = f"con_tro/{d['vai']} → {[t.split('.', 1)[1] for t in d['targets']]} gắn={d['gan_vao']}"
    else:
        s = f"{d['loai']} {(d.get(reason_field) or {}).get('ma', '')} {d['cac_muc_con'] or ''} «{' | '.join(d['trich'])[:80]}»"
    if d["chua_ro"]:
        s += f" CHƯA RÕ={[(c['thanh_phan'], c['nguyen_nhan']) for c in d['chua_ro']]}"
    r = d.get(reason_field)
    if r and d["loai"] != "bo_qua":
        s += f" — lý do {r['ma']}: {r['giai_thich']}"
    return s


TASK = "propositions"
GEMINI_OUT = PILOT_DIR / "llm_output_gemini_lite.json"


def _enum(vals):
    return {"type": "string", "enum": sorted(vals)}


def gemini_schema():
    """Lược đồ JSON cho Gemini (response_json_schema): cùng khuôn menh-de-3, chỉ loai và trich bắt buộc (trường rỗng được bỏ).
    chu_the.loai luôn là mảng (Gemini không nhận "chuỗi hoặc mảng"); normalize đổi mảng một phần tử về chuỗi."""
    s, arr = {"type": "string"}, lambda it: {"type": "array", "items": it}
    row = {"type": "object", "required": ["loai", "trich"], "properties": {
        "loai": _enum(LOAI), "vai": _enum(VAI), "menh_de": s,
        "chu_the": {"type": "object", "required": ["chu", "loai", "nguon"],
                    "properties": {"chu": s, "loai": arr(_enum(KIEU)), "nguon": _enum(NGUON)}},
        "doi_so": arr({"type": "object", "required": ["loai"], "properties": {"loai": _enum(KIEU)}}),
        "phuong_thuc": _enum(PHUONG_THUC), "cuc": _enum(CUC),
        "bo_ngu": arr({"type": "object", "required": ["original_text", "scope"], "properties": {"original_text": s, "scope": _enum(SCOPE)}}),
        "nhom_hoac": s, "cac_muc_con": _enum(MUC_CON),
        "chua_ro": arr({"type": "object", "required": ["thanh_phan", "nguyen_nhan", "cau_hoi"],
                        "properties": {"thanh_phan": s, "nguyen_nhan": _enum(NGUYEN_NHAN), "cau_hoi": s}}),
        "trich": arr(s), "targets": arr(s), "quy_tac": s, "gan_vao": {"type": "integer"}, "liet_ke": arr(s),
        LLM_REASON: {"type": "object", "required": ["ma", "giai_thich"], "properties": {"ma": _enum(MA_LY_DO), "giai_thich": s}}}}
    return {"type": "object", "required": ["units"], "properties": {"units": arr(
        {"type": "object", "required": ["unit_id", "dong"], "properties": {"unit_id": s, "dong": arr(row)}})}}


def gemini(pham_vi="thi_diem", role="chinh", out_path=None, max_lots=None, goi=1):
    """Chạy phần LLM bằng Gemini qua llm_client (--llm live). Lô có đầu ra sai
    hình bị llm_client cách ly (_rejected/), không vào cache; lô lỗi API thì bỏ qua, chạy lại lệnh là gọi tiếp lô còn thiếu."""
    ctxs = contexts()
    base = lots_for(pham_vi, ctxs)[:max_lots]
    # goi > 1: gom nhiều lô vào một lượt gọi (vai kiem chỉ 20 lượt/ngày); lời nhắc không đổi, chỉ đầu vào dài hơn
    lots = [sum(base[i:i + goi], []) for i in range(0, len(base), goi)]
    client = L.Client(mode="live", log=L.stderr_log)
    schema = gemini_schema()
    out, bad = {}, []
    for n, lot in enumerate(lots, 1):
        ids = {c["id"] for c in lot}

        def check(o):
            got = {it.get("unit_id") for it in (o or {}).get("units", [])}
            if got != ids:
                raise ValueError(f"unit_id lệch: thiếu {sorted(ids - got)}, thừa {sorted(got - ids)}")
        try:
            rec = client.ask(TASK, PROMPT_VERSION, SYSTEM, user_message(lot), schema, role=role, validate=check, label=f"lô {n}/{len(lots)}")
        except L.QuotaReached as e:
            print(f"dừng: {e}")
            break
        except (L.LLMError, L.InvalidOutput) as e:
            bad.append((n, str(e)[:200]))
            continue
        for it in rec["output"]["units"]:
            rows = normalize(it["dong"])
            err, flag = gate_unit(ctxs[it["unit_id"]], rows)
            out[it["unit_id"]] = {"dong": rows, "loi": [[i, m] for i, m in err], "co": [[i, m] for i, m in flag]}
    out_path = pathlib.Path(out_path or (GEMINI_OUT if pham_vi == "thi_diem" else FULL_OUT / f"{corpus.BASE_DOC_ID}.gemini.json"))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"prompt_version": PROMPT_VERSION, "model": client.cfg[f"{role}.model"], "units": out},
                                   ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"ghi {out_path}: {len(out)} đơn vị, {sum(len(v['dong']) for v in out.values())} dòng, "
          f"{sum(len(v['loi']) for v in out.values())} lỗi cổng; lô lỗi: {bad}")
    return out, bad


def so(llm_path=LLM_OUT, report_path=REPORT):
    ctxs, gold = contexts(), load_gold()
    llm = json.loads(pathlib.Path(llm_path).read_text(encoding="utf-8"))["units"]
    st = dict(g=0, x=0, khop=0, thieu=0, thua=0, field_khop={}, field_n={}, loi=0, cau_dan_lot=0, chua_ro={})
    lines = [f"# So sánh 1.6A thí điểm ({PROMPT_VERSION}) với đáp án nháp", "",
             "Mỗi đơn vị có chỗ lệch: dòng của đáp án (ĐA) và của LLM; người dùng phán bên nào đúng. Đơn vị khớp hết không liệt kê.", ""]
    body = []
    for uid in gold:
        if uid not in llm:
            body += [f"## {uid.split('.', 1)[1]}: LLM chưa có", ""]
            continue
        G, X = gold[uid], llm[uid]["dong"]
        st["g"] += len(G)
        st["x"] += len(X)
        st["loi"] += len(llm[uid]["loi"])
        pairs, miss, extra = match_rows(G, X)
        st["khop"] += len(pairs)
        st["thieu"] += len(miss)
        st["thua"] += len(extra)
        cau_dan_g = [g for g in G if g["loai"] == "bo_qua" and (g.get(GOLD_REASON) or {}).get("ma") == "cau_dan"]
        for x in X:
            for c in x["chua_ro"]:
                st["chua_ro"][c["nguyen_nhan"]] = st["chua_ro"].get(c["nguyen_nhan"], 0) + 1
            if x["loai"] == "menh_de" and any(_key(x) and _key(x) <= set(syllables(" ".join(g["trich"]))) for g in cau_dan_g):
                st["cau_dan_lot"] += 1
        diffs, du = [], diff_unit(G, X, pairs)
        for gi, li in pairs:
            dd = diff_row(G[gi], X[li]) + du.get(gi, [])
            lech = {d[0] for d in dd}
            for f in SO_FIELDS.get(G[gi]["loai"], ()):
                k = f"{G[gi]['loai']}.{f}"
                st["field_n"][k] = st["field_n"].get(k, 0) + 1
                st["field_khop"][k] = st["field_khop"].get(k, 0) + (f not in lech)
            if dd:
                diffs.append((gi, li, dd))
        if not (diffs or miss or extra or llm[uid]["loi"]):
            continue
        c = ctxs[uid]
        body += [f"## {uid.split('.', 1)[1]}", "", f"Chữ: {c['text']}"]
        if c["chapeau"]:
            body.append(f"Câu dẫn: {c['chapeau']}")
        body.append("")
        for gi, li, dd in diffs:
            body += [f"- **Lệch** ĐA#{gi} / LLM#{li}: " + "; ".join(f"{f}: ĐA={a!r} LLM={b!r}" for f, a, b in dd),
                     f"  - ĐA: {_fmt(G[gi], GOLD_REASON)}", f"  - LLM: {_fmt(X[li], LLM_REASON)}"]
        for gi in miss:
            body.append(f"- **Chỉ ĐA có** #{gi}: {_fmt(G[gi], GOLD_REASON)}")
        for li in extra:
            body.append(f"- **Chỉ LLM có** #{li}: {_fmt(X[li], LLM_REASON)}")
        for i, m in llm[uid]["loi"]:
            body.append(f"- Lỗi cổng LLM #{i}: {m}")
        body += ["", "Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)", ""]
    acc = {f: f"{st['field_khop'][f]}/{st['field_n'][f]}" for f in st["field_n"]}
    head = [f"- Dòng: ĐA {st['g']}, LLM {st['x']}; ghép được {st['khop']}, chỉ ĐA có {st['thieu']}, chỉ LLM có {st['thua']}.",
            f"- Lỗi cổng của LLM: {st['loi']}. Câu dẫn lọt thành mệnh đề (ước bằng máy): {st['cau_dan_lot']}.",
            f"- Field khớp trên các dòng ghép được: {acc}.",
            f"- Chưa rõ của LLM theo nguyên nhân: {st['chua_ro']}.",
            "- Đây là so với đáp án NHÁP: chỉ thành số đo sau khi người dùng phán xong các chỗ lệch (A38 K10).", ""]
    pathlib.Path(report_path).write_text("\n".join(lines + head + body) + "\n", encoding="utf-8")
    print("\n".join(head))
    print(f"ghi {report_path}")
    return st


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "kiem-dap-an":
        sys.exit(1 if kiem_dap_an(sys.argv[2] if len(sys.argv) > 2 else GOLD) else 0)
    elif cmd == "xuat":
        args = [a for a in sys.argv[3:] if a != "--tat-ca"]
        xuat(sys.argv[2], *args[:2], pham_vi="tat_ca" if "--tat-ca" in sys.argv else "thi_diem")
    elif cmd == "nhap":
        nhap(sys.argv[2])
    elif cmd == "so":
        so(*(sys.argv[2:4]))
    elif cmd == "gemini":
        gemini(sys.argv[2] if len(sys.argv) > 2 else "thi_diem", sys.argv[3] if len(sys.argv) > 3 else "chinh",
               goi=int(sys.argv[4]) if len(sys.argv) > 4 else 1,
               out_path=sys.argv[5] if len(sys.argv) > 5 else None)
    else:
        raise SystemExit(__doc__)
