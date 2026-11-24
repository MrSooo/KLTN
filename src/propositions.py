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

# Phiên bản lời nhắc theo lần chạy (A47): khoá `menh_de.prompt_version` của docs/llm_config.md. Lần chạy mặc định giữ menh-de-3 (A39 đóng băng);
# lần chạy ckey đè bằng `ckey.menh_de.prompt_version = menh-de-4`. Cache 1.6A ghi phiên bản vào file, load_ku_cache từ chối file khác phiên bản.
PROMPT_VERSION = L.load_config()["menh_de.prompt_version"]
PILOT_DIR = pathlib.Path("data/pilot_propositions")
GOLD = PILOT_DIR / "gold_draft.json"
# A46, A47: lần chạy khác (KLTN_LLM_RUN) ghi file riêng kèm phiên bản lời nhắc, không đè kết quả thí điểm Sonnet hay của lời nhắc trước
_RUN_TAG = f".{corpus.LLM_RUN}.{PROMPT_VERSION}" if corpus.LLM_RUN else ""
LLM_OUT = PILOT_DIR / f"llm_output{_RUN_TAG}.json"
REPORT = PILOT_DIR / f"comparison{_RUN_TAG}.md"

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

SYSTEM_3 = """Bạn tách các đơn vị của Bộ luật Lao động Việt Nam thành DÒNG. Mỗi đơn vị có: tieu_de_dieu, khoan_cha (câu dẫn của cha, có thể rỗng), chu_don_vi (chữ cần tách), dan_chieu (dẫn chiếu đã giải, kèm mã đích). Chỉ tách chu_don_vi; tiêu đề và câu dẫn chỉ để lấy chủ thể, phương thức, vị ngữ bị lược.

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


# ---- menh-de-4 (A47): menh-de-3 cộng bảy chỗ sửa a-g, mỗi chỗ nhắm một lỗi thấy ở thí điểm DeepSeek 19/11 (30 đơn vị). [THÊM] cả bảy.
# Ví dụ mới lấy từ đơn vị NGOÀI bộ thí điểm (D25.K2, D53.K2, D53.K2.c) để không dạy model đúng đáp án của bộ thí điểm.
_M4 = [
    # e: gộp các hành vi khác nhau vào liet_ke (D5.K1.a)
    ("không để trong menh_de.\n",
     "không để trong menh_de. liet_ke chỉ gom tân ngữ hay phạm vi của CÙNG một động từ; mục nào tự nó là một hành vi khác thì là dòng riêng.\n"),
    # c: ghép chữ dùng chung với chữ của mục thành một trich không nguyên văn (D146.K1)
    ("hiểu cho từng mục. ",
     "hiểu cho từng mục; trich chép chữ dùng chung và chữ của mục thành HAI chuỗi riêng, không ghép: \"không được A, B\" cho mục B → trich [\"không được\", \"B\"]. "),
    # d: điều kiện cốt lõi bị hạ thành bổ ngữ (D14.K1, D14.K2); cổng không bắt được loại lỗi này
    ("Dẫn chiếu không bao giờ là bổ ngữ.\n",
     "Dẫn chiếu không bao giờ là bổ ngữ. Cụm giới hạn đối tượng hay hoàn cảnh áp dụng (\"đối với ...\", \"khi ...\", \"trong trường hợp ...\", \"thông qua ...\", \"dưới hình thức ...\") là dòng dieu_kien riêng (cùng quy_tac), KHÔNG phải bo_ngu: \"Không quá 60 ngày đối với công việc có chức danh nghề nghiệp cần trình độ chuyên môn, kỹ thuật từ cao đẳng trở lên\" → dieu_kien \"có chức danh nghề nghiệp cần trình độ chuyên môn, kỹ thuật từ cao đẳng trở lên\" (chủ thể công việc, J).\n"),
    # b: chủ thể kế thừa từ câu dẫn mà trich không chép mẩu câu dẫn (D35.K2.a, D35.K2.b)
    ("danh_sach (quyền hay mục độc lập).\n",
     "danh_sach (quyền hay mục độc lập). Mục con kế thừa chủ thể từ câu dẫn: chu_the.nguon = cau_dan và trich PHẢI có một mẩu chép từ khoan_cha (thường là cụm chủ thể); nguon = tieu_de thì trich có mẩu chép từ tieu_de_dieu.\n"),
    # a: bo_ngu viết thành chuỗi trần hoặc một đối tượng đơn (5 dòng); lời nhắc cũ không ghi khuôn (status.md nợ 16)
    ("- doi_so: [{\"loai\": mã}] các đối số khác.\n",
     "- doi_so: [{\"loai\": mã}] các đối số khác.\n- bo_ngu: LUÔN là danh sách đối tượng, kể cả khi chỉ có một mục: [{\"original_text\": nguyên văn, \"scope\": this_clause | group | unknown}]. Không viết chuỗi trần, không viết một đối tượng đơn.\n"),
    # f: "không phải là X" mô tả còn nằm trong menh_de (D151.K1.c)
    ("không phải quyền.\n",
     "không phải quyền.\n- BẪY: \"không phải + động từ\" là không có nghĩa vụ (duoc + phu_dinh); \"không phải là + danh từ\" là không thuộc (khong + phu_dinh, menh_de giữ \"là ...\").\n"),
    # a: ví dụ có bo_ngu viết bằng lời -> viết JSON đầy đủ; b: thêm ví dụ nhánh ĐIỀU KIỆN của luật 5
    ("(bo_ngu \"trong quan hệ lao động\", this_clause)",
     "{\"loai\":\"menh_de\",\"vai\":\"dieu_kien\",\"menh_de\":\"đại diện và bảo vệ quyền, lợi ích hợp pháp của người sử dụng lao động\",\"phuong_thuc\":\"khong\",\"cuc\":\"khang_dinh\",\"bo_ngu\":[{\"original_text\":\"trong quan hệ lao động\",\"scope\":\"this_clause\"}],\"trich\":[\"đại diện và bảo vệ quyền, lợi ích hợp pháp của người sử dụng lao động trong quan hệ lao động\"],\"quy_tac\":\"q1\"}"),
    ("cả ba q1.\n",
     "cả ba q1.\n"
     "Danh sách ĐIỀU KIỆN: chu_don_vi \"Bên thuê lại lao động được sử dụng lao động thuê lại trong trường hợp sau đây:\" → {\"loai\":\"menh_de\",\"vai\":\"ket_luan\",\"menh_de\":\"sử dụng lao động thuê lại\",\"chu_the\":{\"chu\":\"Bên thuê lại lao động\",\"loai\":\"E\",\"nguon\":\"chinh\"},\"phuong_thuc\":\"duoc\",\"cuc\":\"khang_dinh\",\"trich\":[\"Bên thuê lại lao động được sử dụng lao động thuê lại\"],\"quy_tac\":\"q1\"} và {\"loai\":\"bo_qua\",\"cac_muc_con\":\"hoac\",\"trich\":[\"trong trường hợp sau đây:\"],\"ly_do_llm\":{\"ma\":\"cau_dan\",\"giai_thich\":\"Phần dẫn vào danh sách trường hợp.\"}}\n"
     "Mục con của câu dẫn đó \"Có nhu cầu sử dụng lao động trình độ chuyên môn, kỹ thuật cao.\" → {\"loai\":\"menh_de\",\"vai\":\"dieu_kien\",\"menh_de\":\"có nhu cầu sử dụng lao động trình độ chuyên môn, kỹ thuật cao\",\"chu_the\":{\"chu\":\"Bên thuê lại lao động\",\"loai\":\"E\",\"nguon\":\"cau_dan\"},\"phuong_thuc\":\"khong\",\"cuc\":\"khang_dinh\",\"trich\":[\"Bên thuê lại lao động\",\"Có nhu cầu sử dụng lao động trình độ chuyên môn, kỹ thuật cao\"],\"quy_tac\":\"q1\"}\n"),
    # g: danh sách tự kiểm ở cuối, lặp đúng các cổng máy (model yếu hơn theo danh sách cuối bài tốt hơn luật nằm giữa)
    ("\n## Đầu ra\n",
     "\n## Tự kiểm trước khi trả\n- bo_ngu là danh sách đối tượng {original_text, scope}.\n- Mọi chuỗi trong trich, chu_the.chu, bo_ngu.original_text, liet_ke chép NGUYÊN VĂN, liền, không ghép từ hai chỗ.\n- chu_the.nguon = cau_dan (hay tieu_de) thì trich có mẩu chép từ khoan_cha (hay tieu_de_dieu).\n- Mọi âm tiết của menh_de có trong trich của dòng đó.\n- Cụm \"đối với / khi / trong trường hợp / thông qua / dưới hình thức ...\" là dieu_kien, không phải bo_ngu.\n\n## Đầu ra\n"),
]


def _apply(text, edits):
    """Dựng lời nhắc mới từ lời nhắc cũ bằng các chỗ sửa (chữ neo, chữ thay); neo phải xuất hiện đúng một lần để không sửa nhầm chỗ."""
    for old, new in edits:
        assert text.count(old) == 1, f"neo không duy nhất: {old[:50]!r}"
        text = text.replace(old, new)
    return text


# ---- menh-de-5 (A50, lần chạy ckey2): menh-de-4 cộng hai chỗ sửa ở luật 5 (câu dẫn). [THÊM] cả hai, do agent viết khi chủ đề tài vắng.
# Lỗi nhắm tới (đo ở lần chạy ckey, tập con lldnn): "phải đáp ứng các điều kiện sau đây" (D151.K1) bị đọc thành danh sách ĐIỀU KIỆN vì có chữ
# "điều kiện", nên "có giấy phép lao động" thành dieu_kien thay vì ket_luan; 8/15 câu dev sai theo. Và câu dẫn "... như sau", "gồm ..." lọt
# thành menh_de (NĐ 145 Đ28). Ví dụ lấy từ D145.K1 và D63.K2, D107.K2 (ngoài 16 Điều của tập con) để không dạy đáp án của bộ dev.
_M5 = [
    # a: danh sách yêu cầu phải đáp ứng là TÂN NGỮ dù có chữ "điều kiện"; phân biệt với danh sách làm hoàn cảnh cho một hành vi khác
    ("mục con là dieu_kien. cac_muc_con",
     "mục con là dieu_kien. Phân biệt theo VAI của danh sách, không theo chữ \"điều kiện\": \"phải đáp ứng / phải có đủ / phải tuân theo các điều kiện, yêu cầu, quy định sau đây\" là TÂN NGỮ của nghĩa vụ (mục con là ket_luan, kế thừa chủ thể và phương thức phai); danh sách chỉ là ĐIỀU KIỆN khi nó là hoàn cảnh cho một hành vi khác nêu trong câu dẫn (\"phải tổ chức đối thoại ... trong trường hợp sau đây\", \"được sử dụng người lao động làm thêm giờ khi đáp ứng đầy đủ các yêu cầu sau đây\"). Phần chữ dẫn vào danh sách (\"... sau đây:\", \"... như sau:\", \"gồm:\") luôn là bo_qua cau_dan, không bao giờ nằm trong menh_de. cac_muc_con"),
    # b: ví dụ nhánh TÂN NGỮ có chữ "quy định sau đây" (D145.K1.b), cộng dòng tự kiểm
    ("\n## Tự kiểm trước khi trả\n",
     "Danh sách TÂN NGỮ có chữ \"quy định\": khoan_cha \"Khi sử dụng người chưa đủ 15 tuổi làm việc, người sử dụng lao động phải tuân theo quy định sau đây:\", chữ \"Bố trí giờ làm việc không ảnh hưởng đến thời gian học tập của người chưa đủ 15 tuổi;\" → {\"loai\":\"menh_de\",\"vai\":\"ket_luan\",\"menh_de\":\"bố trí giờ làm việc không ảnh hưởng đến thời gian học tập của người chưa đủ 15 tuổi\",\"chu_the\":{\"chu\":\"người sử dụng lao động\",\"loai\":\"E\",\"nguon\":\"cau_dan\"},\"phuong_thuc\":\"phai\",\"cuc\":\"khang_dinh\",\"trich\":[\"người sử dụng lao động phải tuân theo\",\"Bố trí giờ làm việc không ảnh hưởng đến thời gian học tập của người chưa đủ 15 tuổi\"],\"quy_tac\":\"q1\"}\n"
     "\n## Tự kiểm trước khi trả\n- Mục con của câu dẫn \"phải đáp ứng / phải có đủ / phải tuân theo ... sau đây\" là ket_luan phai, không phải dieu_kien; không menh_de nào chứa \"sau đây\", \"như sau\", \"gồm\".\n"),
]

PROMPTS = {"menh-de-3": SYSTEM_3, "menh-de-4": _apply(SYSTEM_3, _M4)}
PROMPTS["menh-de-5"] = _apply(PROMPTS["menh-de-4"], _M5)

# A51: sửa tác dụng phụ của A50 ở ckey2. Luật (a) "mục con kế thừa chủ thể" làm model viết mục con là cụm danh từ
# thành vị ngữ "là ..." (20/21 lỗi "âm tiết không có trong trich"), cộng chu_the thiếu khoá nguon (7 lỗi). Chỉ thêm chữ,
# không đổi luật vai hay cổng.
_M6 = [
    # a: mục con là cụm danh từ thì chép nguyên cụm, không thêm chữ nối; đặt ngay sau luật (a) của A50
    ("luôn là bo_qua cau_dan, không bao giờ nằm trong menh_de.",
     "luôn là bo_qua cau_dan, không bao giờ nằm trong menh_de. Mục con là CỤM DANH TỪ (tên một loại người, tổ chức, giấy tờ, như \"Phóng viên nước ngoài hoạt động thông tin báo chí ...\") thì menh_de chép chính cụm đó; KHÔNG thêm \"là\", \"thuộc\", \"có\" hay bất kỳ chữ nối nào không có trong trich để biến nó thành vị ngữ."),
    # b: hai dòng tự kiểm cho đúng hai lỗi đo được
    ("- Mọi âm tiết của menh_de có trong trich của dòng đó.\n",
     "- Mọi âm tiết của menh_de có trong trich của dòng đó; không tự thêm \"là\" vào đầu menh_de.\n- chu_the (nếu có) luôn đủ ba khoá chu, loai, nguon.\n"),
]
PROMPTS["menh-de-6"] = _apply(PROMPTS["menh-de-5"], _M6)

# A52: sửa tác dụng phụ của A51 ở ckey3. (1) Điều không có câu dẫn, kết luận chỉ nằm ở TIÊU ĐỀ (ND_219-2025.D7
# "Người lao động nước ngoài không thuộc diện cấp giấy phép lao động"): mục con chỉ ra dieu_kien, mất ket_luan nên không
# thành quy tắc. Ví dụ tiêu đề sẵn có của lời nhắc (D17) chỉ có một vế; thêm ví dụ đủ hai vế, lấy D37 (ngoài tập con).
# (2) 8 dòng ghi loai = "dieu_kien" (nhầm trường vai sang loai).
_M7 = [
    # a: kết luận ở tiêu đề Điều, khoản là trường hợp: mỗi khoản có ket_luan lấy từ tiêu đề CỘNG dieu_kien là chữ của khoản
    ("KHÔNG thêm \"là\", \"thuộc\", \"có\" hay bất kỳ chữ nối nào không có trong trich để biến nó thành vị ngữ.",
     "KHÔNG thêm \"là\", \"thuộc\", \"có\" hay bất kỳ chữ nối nào không có trong trich để biến nó thành vị ngữ. Điều KHÔNG có câu dẫn mà tiêu đề nêu kết luận (\"Trường hợp ... không được ...\", \"Người ... không thuộc diện ...\") và các khoản là từng trường hợp: MỖI khoản ra một dòng ket_luan lấy từ tiêu đề (chu_the.nguon = tieu_de, trich có mẩu chép từ tieu_de_dieu) CỘNG một dòng dieu_kien là chữ của khoản; thiếu dòng ket_luan thì khoản đó không thành quy tắc."),
    # b: ví dụ đủ hai vế (D37.K2) và dòng tự kiểm cho loai
    ("\n## Tự kiểm trước khi trả\n",
     "Kết luận ở tiêu đề, khoản là trường hợp: tieu_de_dieu \"Trường hợp người sử dụng lao động không được thực hiện quyền đơn phương chấm dứt hợp đồng lao động\", chữ \"Người lao động đang nghỉ hằng năm, nghỉ việc riêng và trường hợp nghỉ khác được người sử dụng lao động đồng ý.\" → {\"loai\":\"menh_de\",\"vai\":\"ket_luan\",\"menh_de\":\"thực hiện quyền đơn phương chấm dứt hợp đồng lao động\",\"chu_the\":{\"chu\":\"người sử dụng lao động\",\"loai\":\"E\",\"nguon\":\"tieu_de\"},\"phuong_thuc\":\"cam\",\"cuc\":\"khang_dinh\",\"trich\":[\"người sử dụng lao động không được thực hiện quyền đơn phương chấm dứt hợp đồng lao động\"],\"quy_tac\":\"q1\"} và {\"loai\":\"menh_de\",\"vai\":\"dieu_kien\",\"menh_de\":\"đang nghỉ hằng năm, nghỉ việc riêng và trường hợp nghỉ khác được người sử dụng lao động đồng ý\",\"chu_the\":{\"chu\":\"Người lao động\",\"loai\":\"W\",\"nguon\":\"chinh\"},\"phuong_thuc\":\"khong\",\"cuc\":\"khang_dinh\",\"trich\":[\"Người lao động đang nghỉ hằng năm, nghỉ việc riêng và trường hợp nghỉ khác được người sử dụng lao động đồng ý\"],\"quy_tac\":\"q1\"}\n"
     "\n## Tự kiểm trước khi trả\n- loai chỉ là menh_de | con_tro | bo_qua | chua_ro; ket_luan, dieu_kien, ngoai_le là giá trị của vai, không bao giờ của loai.\n- Điều không có câu dẫn mà tiêu đề nêu kết luận: mỗi khoản có cả dòng ket_luan (nguon tieu_de) lẫn dòng dieu_kien.\n"),
]
PROMPTS["menh-de-7"] = _apply(PROMPTS["menh-de-6"], _M7)

# ---- menh-de-9 (A54, A55, lần sửa A2): VIẾT NGUYÊN BẢN, không _apply (luật 4 của A54). Gốc là chữ đã dựng của menh-de-4 (mốc nhiễu A54)
# cộng đúng một thay đổi: bổ ngữ thành dòng dieu_kien riêng, bỏ trường bo_ngu (luật 3, 4, trường, ví dụ định nghĩa, tự kiểm). Không có
# menh-de-8: bản "menh-de-4 viết gọn, không thêm luật" trùng từng byte với menh-de-4 (PROMPTS đã là chữ liền), nên mốc trung tính là menh-de-4.
SYSTEM_9 = """Bạn tách các đơn vị của Bộ luật Lao động Việt Nam thành DÒNG. Mỗi đơn vị có: tieu_de_dieu, khoan_cha (câu dẫn của cha, có thể rỗng), chu_don_vi (chữ cần tách), dan_chieu (dẫn chiếu đã giải, kèm mã đích). Chỉ tách chu_don_vi; tiêu đề và câu dẫn chỉ để lấy chủ thể, phương thức, vị ngữ bị lược.

## Loại dòng (loai)
- menh_de: một điều đúng/sai được.
- con_tro: dẫn chiếu đã giải ("trừ trường hợp quy định tại ...", "theo quy định tại ..."); targets lấy từ dan_chieu.
- bo_qua: không thành mệnh đề; ly_do_llm.ma: cau_dan (phần chỉ dẫn vào danh sách, "... sau đây:") | dan_chieu_mo ("theo quy định của pháp luật") | dan_chieu_ngoai (một luật khác, "theo quy định của Luật Công đoàn") | khong_quy_pham (câu chính sách, định hướng, không có hành vi kiểm được).
- chua_ro: cả dòng không xác định được.

## Luật tách
1. TÁCH khi từng phần kiểm được đúng/sai riêng VÀ vi phạm từng phần có ý nghĩa pháp lý riêng. GIỮ CHUNG khi là một yêu cầu tập thể. Không tách chỉ vì có nhiều danh từ.
2. menh_de chỉ giữ LÕI: động từ (hoặc tính chất) + tân ngữ chính, càng ngắn càng tốt, để cùng một việc ở các Điều khác nhau ra cùng chữ. Danh sách liệt kê (từ 3 mục) của tân ngữ hay phạm vi đưa vào liet_ke (mỗi mục chép nguyên văn), không để trong menh_de. liet_ke chỉ gom tân ngữ hay phạm vi của CÙNG một động từ; mục nào tự nó là một hành vi khác thì là dòng riêng.
3. Chữ dùng chung đứng ĐẦU chuỗi ("không" trong "không A, B, C") hiểu cho từng mục; trich chép chữ dùng chung và chữ của mục thành HAI chuỗi riêng, không ghép: "không được A, B" cho mục B → trich ["không được", "B"]. Bổ ngữ đứng CUỐI phải xác định phạm vi: chỉ thuộc một quy tắc thì là một dòng dieu_kien trong quy tắc đó; chung cho cả nhóm thì là một dòng dieu_kien nguyên văn trong MỖI quy_tac của nhóm; không xác định được thì thêm chua_ro nguyen_nhan pham_vi_bo_ngu.
4. Bổ ngữ là cụm mà bỏ đi thì vẫn cùng loại hành vi: nơi chốn ("tại ..."), căn cứ ("theo ..."), cách thức phụ. Bổ ngữ KHÔNG ở trong menh_de: tách thành một dòng dieu_kien riêng, menh_de của dòng đó chép nguyên văn cụm bổ ngữ, cùng chu_the và quy_tac với dòng nó bổ nghĩa. Cụm làm nên chính hành vi (thời điểm, mức, cách thức phân biệt) giữ trong menh_de: "làm việc trên cao" không rút thành "làm việc". Dẫn chiếu không bao giờ là bổ ngữ. Cụm giới hạn đối tượng hay hoàn cảnh áp dụng ("đối với ...", "khi ...", "trong trường hợp ...", "thông qua ...", "dưới hình thức ...") cũng là dòng dieu_kien riêng (cùng quy_tac): "Không quá 60 ngày đối với công việc có chức danh nghề nghiệp cần trình độ chuyên môn, kỹ thuật từ cao đẳng trở lên" → dieu_kien "có chức danh nghề nghiệp cần trình độ chuyên môn, kỹ thuật từ cao đẳng trở lên" (chủ thể công việc, J).
5. Câu dẫn: danh sách là TÂN NGỮ ("có các nghĩa vụ sau đây") thì câu dẫn ra bo_qua cau_dan, mục con là ket_luan kế thừa chủ thể và phương thức. Danh sách là ĐIỀU KIỆN ("trong trường hợp sau đây") thì phần nội dung câu dẫn ra ket_luan (một lần, ở câu dẫn), phần dẫn ra bo_qua, mục con là dieu_kien. cac_muc_con của dòng cau_dan: va (điều kiện hay yêu cầu phải đủ HẾT) | hoac (trường hợp, MỘT là đủ) | danh_sach (quyền hay mục độc lập). Mục con kế thừa chủ thể từ câu dẫn: chu_the.nguon = cau_dan và trich PHẢI có một mẩu chép từ khoan_cha (thường là cụm chủ thể); nguon = tieu_de thì trich có mẩu chép từ tieu_de_dieu.
6. Định nghĩa khái niệm "X là Y": dấu hiệu của Y là dieu_kien, thêm ket_luan "là X". Câu nêu giá trị, mức ("thời hạn ... là N ngày") ra một ket_luan.
7. quy_tac (q1, q2...) gom dieu_kien và ket_luan của cùng một quy tắc. "Hoặc" giữa điều kiện trong một quy tắc: cùng nhom_hoac ("h1"). "Hoặc" mà một vế có "và": tách nhiều quy tắc.

## Trường
- vai: ket_luan | dieu_kien | ngoai_le. con_tro "trừ ..." có vai ngoai_le; con_tro khác lấy vai của dòng nó bổ nghĩa.
- menh_de: đã bỏ chủ thể, chữ phương thức, chữ phủ định, bổ ngữ (thành dòng dieu_kien riêng), liệt kê. MỌI âm tiết của menh_de phải có trong trich của dòng đó.
- chu_the: {"chu": nguyên văn, "loai": mã hoặc danh sách mã khi chủ thể chung, "nguon": chinh | cau_dan | tieu_de}, hoặc bỏ. Mã: W người lao động, E người sử dụng lao động, C hợp đồng, J công việc, G vùng, D ngày, A số tiền, ? chưa biết. Người chỉ chịu tác động là đối số, không phải chủ thể.
- doi_so: [{"loai": mã}] các đối số khác.
- Không có trường bo_ngu: bổ ngữ là dòng dieu_kien riêng (luật 4).
- phuong_thuc: duoc (được, có quyền, có thể) | phai (phải, có nghĩa vụ) | cam (cấm, không được làm) | khong_ap_dung (tuyên bố một quy định không áp cho một nhóm trường hợp) | khong (mô tả, điều kiện, định nghĩa).
- cuc: khang_dinh | phu_dinh; chỉ phủ định menh_de: duoc + phu_dinh là "được không bị X"; "không phải X" (không có nghĩa vụ) ghi duoc + phu_dinh.
- BẪY: "không được + động từ" là cam (không được làm X) hoặc bị động phủ định (không được người khác làm cho: khong + phu_dinh, menh_de giữ "được ..."). "Được + động từ" có thể là bị động, không phải quyền.
- BẪY: "không phải + động từ" là không có nghĩa vụ (duoc + phu_dinh); "không phải là + danh từ" là không thuộc (khong + phu_dinh, menh_de giữ "là ...").
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
Định nghĩa "Tổ chức đại diện người sử dụng lao động là tổ chức được thành lập hợp pháp, đại diện và bảo vệ quyền, lợi ích hợp pháp của người sử dụng lao động trong quan hệ lao động." → dieu_kien "được thành lập hợp pháp" (bị động, khong); dieu_kien "đại diện và bảo vệ quyền, lợi ích hợp pháp của người sử dụng lao động" {"loai":"menh_de","vai":"dieu_kien","menh_de":"đại diện và bảo vệ quyền, lợi ích hợp pháp của người sử dụng lao động","phuong_thuc":"khong","cuc":"khang_dinh","trich":["đại diện và bảo vệ quyền, lợi ích hợp pháp của người sử dụng lao động"],"quy_tac":"q1"}; dieu_kien bổ ngữ {"loai":"menh_de","vai":"dieu_kien","menh_de":"trong quan hệ lao động","phuong_thuc":"khong","cuc":"khang_dinh","trich":["trong quan hệ lao động"],"quy_tac":"q1"}; ket_luan khong "là tổ chức đại diện người sử dụng lao động"; cả bốn q1.
Danh sách ĐIỀU KIỆN: chu_don_vi "Bên thuê lại lao động được sử dụng lao động thuê lại trong trường hợp sau đây:" → {"loai":"menh_de","vai":"ket_luan","menh_de":"sử dụng lao động thuê lại","chu_the":{"chu":"Bên thuê lại lao động","loai":"E","nguon":"chinh"},"phuong_thuc":"duoc","cuc":"khang_dinh","trich":["Bên thuê lại lao động được sử dụng lao động thuê lại"],"quy_tac":"q1"} và {"loai":"bo_qua","cac_muc_con":"hoac","trich":["trong trường hợp sau đây:"],"ly_do_llm":{"ma":"cau_dan","giai_thich":"Phần dẫn vào danh sách trường hợp."}}
Mục con của câu dẫn đó "Có nhu cầu sử dụng lao động trình độ chuyên môn, kỹ thuật cao." → {"loai":"menh_de","vai":"dieu_kien","menh_de":"có nhu cầu sử dụng lao động trình độ chuyên môn, kỹ thuật cao","chu_the":{"chu":"Bên thuê lại lao động","loai":"E","nguon":"cau_dan"},"phuong_thuc":"khong","cuc":"khang_dinh","trich":["Bên thuê lại lao động","Có nhu cầu sử dụng lao động trình độ chuyên môn, kỹ thuật cao"],"quy_tac":"q1"}

## Tự kiểm trước khi trả
- Không có trường bo_ngu; mỗi bổ ngữ ("tại / theo / trong ..." không làm nên chính hành vi) là một dòng dieu_kien riêng, chép nguyên văn.
- Mọi chuỗi trong trich, chu_the.chu, liet_ke chép NGUYÊN VĂN, liền, không ghép từ hai chỗ.
- chu_the.nguon = cau_dan (hay tieu_de) thì trich có mẩu chép từ khoan_cha (hay tieu_de_dieu).
- Mọi âm tiết của menh_de có trong trich của dòng đó.
- Cụm "đối với / khi / trong trường hợp / thông qua / dưới hình thức ..." là dòng dieu_kien riêng.

## Đầu ra
JSON thuần, không chữ giải thích: {"units": [{"unit_id": "...", "dong": [...]}]}. Mỗi unit_id của lô đúng một mục, mỗi mục ít nhất một dòng."""
PROMPTS["menh-de-9"] = SYSTEM_9

# ---- menh-de-10 (A56): menh-de-9 VIẾT GỌN, chỉ cắt, không thêm luật (phép thử bỏ đi: chữ dài có đáng giữ không). Cùng khuôn đầu ra
# và cùng cổng với menh-de-9. Đã cắt: mục "Tự kiểm" (lặp cổng), 4/8 ví dụ, các câu luật lặp ý; luật giữ nguyên nghĩa.
_FIELDS_10 = """## Trường của một dòng
- loai: menh_de (một điều đúng/sai được) | con_tro (dẫn chiếu đã giải: "trừ trường hợp quy định tại ...", "theo quy định tại ...") | bo_qua (không thành mệnh đề) | chua_ro (cả dòng không xác định được).
- trich: các chuỗi chép NGUYÊN VĂN, liền, từ tieu_de_dieu, khoan_cha hoặc chu_don_vi. Mọi âm tiết của menh_de có trong trich; chủ thể hay phương thức kế thừa thì trich có cả mẩu chứa nó.
- vai: ket_luan | dieu_kien | ngoai_le. con_tro "trừ ..." là ngoai_le; con_tro khác lấy vai của dòng nó bổ nghĩa.
- menh_de: LÕI động từ (hoặc tính chất) + tân ngữ chính, càng ngắn càng tốt để cùng một việc ở các Điều khác nhau ra cùng chữ; đã bỏ chủ thể, chữ phương thức, chữ phủ định, bổ ngữ, liệt kê.
- chu_the: {"chu": nguyên văn, "loai": mã hoặc danh sách mã, "nguon": chinh | cau_dan | tieu_de}. Mã: W người lao động, E người sử dụng lao động, C hợp đồng, J công việc, G vùng, D ngày, A số tiền, ? chưa biết. Người chỉ chịu tác động là doi_so, không phải chủ thể. nguon cau_dan (hay tieu_de) thì trich có mẩu chép từ khoan_cha (hay tieu_de_dieu).
- doi_so: [{"loai": mã}] các đối số khác.
- phuong_thuc: duoc (được, có quyền, có thể) | phai (phải, có nghĩa vụ) | cam (cấm, không được làm) | khong_ap_dung (một quy định không áp cho một nhóm trường hợp) | khong (mô tả, điều kiện, định nghĩa).
- cuc: khang_dinh | phu_dinh, chỉ phủ định menh_de. "Không phải + động từ" (không có nghĩa vụ): duoc + phu_dinh. "Không được + động từ": cam; nếu là bị động (không được người khác làm cho) thì khong + phu_dinh, menh_de giữ "được ...". "Không phải là + danh từ": khong + phu_dinh, menh_de giữ "là ...".
- quy_tac: "q1", "q2"... gom dieu_kien và ket_luan của cùng một quy tắc. nhom_hoac: "h1"... cho các điều kiện nối bằng "hoặc" trong một quy tắc.
- liet_ke: danh sách (từ 3 mục) tân ngữ hay phạm vi của CÙNG một động từ, mỗi mục chép nguyên văn; mục nào tự nó là một hành vi khác thì là dòng riêng.
- cac_muc_con (chỉ ở dòng bo_qua cau_dan): va (phải đủ hết) | hoac (một là đủ) | danh_sach (mục độc lập).
- targets, gan_vao (chỉ con_tro): targets là mã lấy từ dan_chieu, không giải được thì rỗng kèm chua_ro; gan_vao là số thứ tự (từ 0) của dòng menh_de nó bổ nghĩa, null nếu chặn cả quy tắc.
- chua_ro: [{"thanh_phan", "nguyen_nhan": pham_vi_bo_ngu | tach_hay_giu_chung | phuong_thuc | chu_the | khac, "cau_hoi"}]. Không đoán.
- ly_do_llm: {"ma", "giai_thich": một câu ngắn}. Bắt buộc ở dòng bo_qua, ma: cau_dan (phần dẫn vào danh sách) | dan_chieu_mo ("theo quy định của pháp luật") | dan_chieu_ngoai (luật khác) | khong_quy_pham (câu chính sách, không có hành vi kiểm được). Ở dòng khác chỉ khi khó: tach | giu_chung | gan_bo_ngu | chua_ro | ke_thua.
- Trường rỗng thì bỏ. Luôn có loai và trich; menh_de có thêm vai, menh_de, phuong_thuc, cuc, quy_tac."""
_HEAD_10 = "Tách mỗi đơn vị của Bộ luật Lao động thành các DÒNG để máy biên dịch thành quy tắc. Mỗi đơn vị có: tieu_de_dieu, khoan_cha (câu dẫn của cha, có thể rỗng), chu_don_vi (chữ cần tách), dan_chieu (dẫn chiếu đã giải, kèm mã đích). Chỉ tách chu_don_vi; tiêu đề và câu dẫn chỉ để lấy chủ thể, phương thức, vị ngữ bị lược."
_TAIL_10 = """## Ví dụ
khoan_cha "Người sử dụng lao động có các nghĩa vụ sau đây:" → {"loai":"bo_qua","cac_muc_con":"danh_sach","trich":["Người sử dụng lao động có các nghĩa vụ sau đây:"],"ly_do_llm":{"ma":"cau_dan","giai_thich":"Câu dẫn danh sách nghĩa vụ."}}
Mục con "...; tôn trọng danh dự, nhân phẩm của người lao động;" → {"loai":"menh_de","vai":"ket_luan","menh_de":"tôn trọng danh dự, nhân phẩm của người lao động","chu_the":{"chu":"Người sử dụng lao động","loai":"E","nguon":"cau_dan"},"doi_so":[{"loai":"W"}],"phuong_thuc":"phai","cuc":"khang_dinh","trich":["Người sử dụng lao động có các nghĩa vụ","tôn trọng danh dự, nhân phẩm của người lao động"],"quy_tac":"q1"}
chu_don_vi "Bên thuê lại lao động được sử dụng lao động thuê lại trong trường hợp sau đây:" → {"loai":"menh_de","vai":"ket_luan","menh_de":"sử dụng lao động thuê lại","chu_the":{"chu":"Bên thuê lại lao động","loai":"E","nguon":"chinh"},"phuong_thuc":"duoc","cuc":"khang_dinh","trich":["Bên thuê lại lao động được sử dụng lao động thuê lại"],"quy_tac":"q1"} và {"loai":"bo_qua","cac_muc_con":"hoac","trich":["trong trường hợp sau đây:"],"ly_do_llm":{"ma":"cau_dan","giai_thich":"Phần dẫn vào danh sách trường hợp."}}
Mục con của câu dẫn đó "Có nhu cầu sử dụng lao động trình độ chuyên môn, kỹ thuật cao." → {"loai":"menh_de","vai":"dieu_kien","menh_de":"có nhu cầu sử dụng lao động trình độ chuyên môn, kỹ thuật cao","chu_the":{"chu":"Bên thuê lại lao động","loai":"E","nguon":"cau_dan"},"phuong_thuc":"khong","cuc":"khang_dinh","trich":["Bên thuê lại lao động","Có nhu cầu sử dụng lao động trình độ chuyên môn, kỹ thuật cao"],"quy_tac":"q1"}

## Đầu ra
JSON thuần, không chữ giải thích: {"units": [{"unit_id": "...", "dong": [...]}]}. Mỗi unit_id của lô đúng một mục, mỗi mục ít nhất một dòng."""
# Luật 2-6 của menh-de-10 (dùng chung với menh-de-11, chỉ khác số thứ tự). Ghép phần chung bằng chuỗi cố định, không _apply sửa chữ cũ.
_RULES_10_REST = [
    'Bổ ngữ (nơi chốn "tại ...", căn cứ "theo ...", cách thức phụ) và cụm giới hạn ("đối với ...", "khi ...", "trong trường hợp ...", "thông qua ...", "dưới hình thức ...") là một dòng dieu_kien riêng, chép nguyên văn, cùng chu_the và quy_tac với dòng nó bổ nghĩa; chung cho cả nhóm thì lặp trong mỗi quy_tac của nhóm; không rõ phạm vi thì chua_ro pham_vi_bo_ngu. Cụm làm nên chính hành vi (thời điểm, mức) giữ trong menh_de. Dẫn chiếu không phải bổ ngữ.',
    'Chữ dùng chung đứng đầu ("không được A, B") áp cho từng mục; trich ghi hai chuỗi riêng: mục B → ["không được", "B"].',
    'Câu dẫn có danh sách. Danh sách là TÂN NGỮ ("có các nghĩa vụ sau đây"): câu dẫn là bo_qua cau_dan, mỗi mục con là ket_luan kế thừa chủ thể và phương thức. Danh sách là ĐIỀU KIỆN ("trong trường hợp sau đây"): nội dung câu dẫn là một ket_luan, phần dẫn là bo_qua cau_dan, mỗi mục con là dieu_kien.',
    'Định nghĩa "X là Y": dấu hiệu của Y là dieu_kien, thêm ket_luan "là X". Câu nêu giá trị, mức là một ket_luan.',
    '"Hoặc" mà một vế có "và": tách thành nhiều quy_tac.',
]
_RULE_SPLIT = 'TÁCH khi từng phần kiểm được đúng/sai riêng VÀ vi phạm từng phần có ý nghĩa pháp lý riêng. GIỮ CHUNG khi là một yêu cầu tập thể. Không tách chỉ vì có nhiều danh từ.'
# [A56, THÊM] luật duy nhất menh-de-11 thêm vào menh-de-10, đặt đầu: lỗi chí mạng là một menh_de gộp nhiều việc nên 1.6B ra một tên nuốt
# nhiều vị từ (KB cả bộ luật ckey: 349/1.586 tên có _and_/_or_, 82% vị từ dùng ở <=1 đơn vị). "Hoặc" chỉ tách ở điều kiện: tách kết luận
# "được A hoặc B" thành hai dòng ket_luan cùng quy_tac là biến lựa chọn thành hai điều cùng đúng.
_RULE_ONE_THING = 'MỖI DÒNG MỘT VIỆC. Hai hành vi, hai nghĩa vụ hay hai vi phạm nối bằng "và" hoặc dấu phẩy, mỗi vế có động từ riêng, là hai dòng; hai động từ chung một tân ngữ ("xây dựng và thực hiện phương án") cũng là hai dòng, trich ghi các chuỗi riêng. Hai vế "hoặc" của ĐIỀU KIỆN là hai dòng dieu_kien cùng nhom_hoac; "hoặc" trong ket_luan (được chọn một trong hai) giữ chung một dòng. Chỉ danh sách tân ngữ của cùng một động từ mới vào liet_ke; cụm danh từ đi đôi chỉ một khái niệm ("danh dự, nhân phẩm") giữ chung.'


def _numbered(rules):
    return "\n".join(f"{i}. {r}" for i, r in enumerate(rules, 1))


PROMPTS["menh-de-10"] = f"{_HEAD_10}\n\n{_FIELDS_10}\n\n## Luật\n{_numbered([_RULE_SPLIT, *_RULES_10_REST])}\n\n{_TAIL_10}"
PROMPTS["menh-de-11"] = f"{_HEAD_10}\n\n{_FIELDS_10}\n\n## Luật\n{_numbered([_RULE_ONE_THING, _RULE_SPLIT, *_RULES_10_REST])}\n\n{_TAIL_10}"
# ---- menh-de-12 (A57): KHUÔN GỌN. LLM chỉ làm phần cần hiểu nghĩa (chỉ ra đoạn lõi, vai, phương thức, cực, nhóm quy tắc, chủ thể);
# máy dựng lại các trường còn lại của khuôn cũ (expand_unit), nên cổng và mọi bước sau đọc như cũ. Viết nguyên bản, không ghép từ bản cũ.
SYSTEM_12 = """Tách mỗi đơn vị của Bộ luật Lao động thành các DÒNG; máy dựng quy tắc từ các dòng này. Mỗi đơn vị có: tieu_de_dieu, khoan_cha (câu dẫn của cha, có thể rỗng), chu_don_vi (chữ cần tách), dan_chieu (dẫn chiếu đã giải, kèm mã đích). Chỉ tách chu_don_vi; tiêu đề và câu dẫn chỉ để lấy chủ thể, phương thức, vị ngữ bị lược.

## Mỗi dòng là MỘT việc
Một dòng là một điều kiện hoặc một kết luận kiểm được đúng/sai riêng. Hai hành vi, hai nghĩa vụ hay hai vi phạm, mỗi vế có động từ riêng, là hai dòng (kể cả khi chung tân ngữ: "xây dựng và thực hiện X" là hai dòng). Hai vế "hoặc" của điều kiện là hai dòng cùng nhom_hoac. Giữ chung khi là một khái niệm hay một yêu cầu tập thể ("danh dự, nhân phẩm"); không tách chỉ vì có nhiều danh từ.

## Trường của dòng
- doan: danh sách đoạn chép NGUYÊN VĂN, liền, đúng từng chữ, từ chu_don_vi, khoan_cha hoặc tieu_de_dieu; nối theo thứ tự là lõi: động từ (hoặc tính chất) + tân ngữ chính, càng ngắn càng tốt. Không đưa vào doan: chủ thể, chữ phương thức (phải, được, có quyền, cấm, không được), chữ phủ định, chữ dẫn chiếu, danh sách tân ngữ (để ở liet_ke). Thường một đoạn; nhiều đoạn khi lõi bị chữ khác chen giữa.
- vai: ket_luan | dieu_kien.
- phuong_thuc: duoc (được, có quyền, có thể) | phai (phải, có nghĩa vụ) | cam (cấm, không được làm) | khong_ap_dung (một quy định không áp cho một nhóm trường hợp) | khong (mô tả, điều kiện, định nghĩa).
- cuc: khang_dinh | phu_dinh (chỉ phủ định lõi). "Không phải + động từ" (không có nghĩa vụ): duoc + phu_dinh. "Không được + động từ": cam; nếu bị động (không được người khác làm cho) thì khong + phu_dinh, doan giữ "được ...". "Không phải là + danh từ": khong + phu_dinh.
- quy_tac: "q1", "q2"... gom dieu_kien và ket_luan của cùng một quy tắc. nhom_hoac: "h1"... cho các dieu_kien nối bằng "hoặc" trong một quy tắc.
- chu_the: {"chu": chép nguyên văn cụm chủ thể, "loai": mã hoặc danh sách mã}; câu không có chủ thể thì BỎ trường này. Mã: W người lao động, E người sử dụng lao động, C hợp đồng, J công việc, G vùng, D ngày, A số tiền, ? chưa biết. Người chỉ chịu tác động là doi_so.
- doi_so: [{"loai": mã}] các đối số khác.
- liet_ke: danh sách (từ 3 mục) tân ngữ hay phạm vi của cùng một động từ, mỗi mục nguyên văn.
- chua_ro: [{"thanh_phan", "nguyen_nhan": pham_vi_bo_ngu | tach_hay_giu_chung | phuong_thuc | chu_the | khac, "cau_hoi"}] khi không xác định được. Không đoán.
Trường rỗng thì bỏ.

## Trường của đơn vị (cạnh unit_id, dong)
- cac_muc_con: chu_don_vi là câu dẫn vào các mục con ("... sau đây:", "như sau:") thì ghi va (phải đủ hết) | hoac (một mục là đủ) | danh_sach (mục độc lập). Máy tự thêm dòng cho chữ dẫn.
- ngoai_le: danh sách mã dich (lấy từ dan_chieu) của dẫn chiếu là ngoại lệ ("trừ ...", kể cả các dẫn chiếu đứng sau một chữ "trừ" chung). Máy tự dựng dòng cho mọi dẫn chiếu.
- bo_qua: khong_quy_pham (câu chính sách, không có hành vi kiểm được) | dan_chieu_mo | dan_chieu_ngoai (chỉ dẫn sang quy định khác). Khi đó dong có thể rỗng.

## Luật
1. Bổ ngữ (nơi chốn "tại ...", căn cứ "theo ...", cách thức phụ) và cụm giới hạn ("đối với ...", "khi ...", "trong trường hợp ...", "trong khoảng ...", "thông qua ...", "dưới hình thức ...") là một dòng dieu_kien riêng, cùng chu_the và quy_tac với dòng nó bổ nghĩa. Cụm làm nên chính hành vi (thời điểm, mức) giữ trong doan.
2. Câu dẫn mà danh sách là TÂN NGỮ ("có các nghĩa vụ sau đây"): dong rỗng; mỗi mục con là ket_luan kế thừa chủ thể và phương thức. Câu dẫn mà danh sách là ĐIỀU KIỆN ("trong trường hợp sau đây"): dong là một ket_luan (nội dung câu dẫn); mỗi mục con là dieu_kien.
3. Chủ thể hay phương thức bị lược thì lấy từ khoan_cha hoặc tieu_de_dieu; chu_the.chu chép đúng cụm ở đó.
4. Định nghĩa "X là Y": dấu hiệu của Y là các dieu_kien; ket_luan có doan ["là", "X"].
5. Câu nêu giá trị, mức là một ket_luan. "Hoặc" mà một vế có "và": tách nhiều quy_tac.
6. Dẫn chiếu mở là điều kiện duy nhất ("trường hợp khác theo quy định của Chính phủ") vẫn là một dòng dieu_kien.

## Ví dụ
{"unit_id":"BLLD_45-2019.D6.K2","cac_muc_con":"danh_sach","dong":[]} (chu_don_vi "Người sử dụng lao động có các nghĩa vụ sau đây:")
chu_don_vi "Thiết lập cơ chế và thực hiện đối thoại, trao đổi với người lao động và tổ chức đại diện người lao động; thực hiện quy chế dân chủ ở cơ sở tại nơi làm việc;" → {"unit_id":"BLLD_45-2019.D6.K2.b","dong":[{"doan":["Thiết lập cơ chế","đối thoại, trao đổi"],"vai":"ket_luan","chu_the":{"chu":"Người sử dụng lao động","loai":"E"},"doi_so":[{"loai":"W"}],"phuong_thuc":"phai","cuc":"khang_dinh","quy_tac":"q1"},{"doan":["thực hiện đối thoại, trao đổi"],"vai":"ket_luan","chu_the":{"chu":"Người sử dụng lao động","loai":"E"},"doi_so":[{"loai":"W"}],"phuong_thuc":"phai","cuc":"khang_dinh","quy_tac":"q2"},{"doan":["thực hiện quy chế dân chủ ở cơ sở"],"vai":"ket_luan","chu_the":{"chu":"Người sử dụng lao động","loai":"E"},"phuong_thuc":"phai","cuc":"khang_dinh","quy_tac":"q3"},{"doan":["tại nơi làm việc"],"vai":"dieu_kien","chu_the":{"chu":"Người sử dụng lao động","loai":"E"},"phuong_thuc":"khong","cuc":"khang_dinh","quy_tac":"q3"}]}
chu_don_vi "Bên thuê lại lao động được sử dụng lao động thuê lại trong trường hợp sau đây:" → {"unit_id":"BLLD_45-2019.D53.K2","cac_muc_con":"hoac","dong":[{"doan":["sử dụng lao động thuê lại"],"vai":"ket_luan","chu_the":{"chu":"Bên thuê lại lao động","loai":"E"},"phuong_thuc":"duoc","cuc":"khang_dinh","quy_tac":"q1"}]}; mục con "Đáp ứng tạm thời sự gia tăng đột ngột về nhu cầu sử dụng lao động trong khoảng thời gian nhất định;" → {"unit_id":"BLLD_45-2019.D53.K2.a","dong":[{"doan":["Đáp ứng tạm thời sự gia tăng đột ngột về nhu cầu sử dụng lao động"],"vai":"dieu_kien","chu_the":{"chu":"Bên thuê lại lao động","loai":"E"},"phuong_thuc":"khong","cuc":"khang_dinh","quy_tac":"q1"},{"doan":["trong khoảng thời gian nhất định"],"vai":"dieu_kien","chu_the":{"chu":"Bên thuê lại lao động","loai":"E"},"phuong_thuc":"khong","cuc":"khang_dinh","quy_tac":"q1"}]}
Tiêu đề "Hành vi người sử dụng lao động không được làm khi giao kết, thực hiện hợp đồng lao động", chu_don_vi "Giữ bản chính giấy tờ tùy thân, văn bằng, chứng chỉ của người lao động." → {"unit_id":"BLLD_45-2019.D17.K1","dong":[{"doan":["Giữ bản chính giấy tờ tùy thân, văn bằng, chứng chỉ của người lao động"],"vai":"ket_luan","chu_the":{"chu":"người sử dụng lao động","loai":"E"},"doi_so":[{"loai":"W"}],"phuong_thuc":"cam","cuc":"khang_dinh","quy_tac":"q1"}]}
chu_don_vi "Hợp đồng lao động phải được giao kết bằng văn bản và được làm thành 02 bản, ..., trừ trường hợp quy định tại khoản 2 Điều này." → {"unit_id":"BLLD_45-2019.D14.K1","ngoai_le":["BLLD_45-2019.D14.K2"],"dong":[{"doan":["được giao kết bằng văn bản"],"vai":"ket_luan","chu_the":{"chu":"Hợp đồng lao động","loai":"C"},"phuong_thuc":"phai","cuc":"khang_dinh","quy_tac":"q1"},{"doan":["được làm thành 02 bản"],"vai":"ket_luan","chu_the":{"chu":"Hợp đồng lao động","loai":"C"},"phuong_thuc":"phai","cuc":"khang_dinh","quy_tac":"q2"}, ...]}
Định nghĩa "Việc làm là hoạt động lao động tạo ra thu nhập mà pháp luật không cấm." → {"unit_id":"BLLD_45-2019.D9.K1","dong":[{"doan":["hoạt động lao động tạo ra thu nhập"],"vai":"dieu_kien","phuong_thuc":"khong","cuc":"khang_dinh","quy_tac":"q1"},{"doan":["cấm"],"vai":"dieu_kien","chu_the":{"chu":"pháp luật","loai":"?"},"phuong_thuc":"khong","cuc":"phu_dinh","quy_tac":"q1"},{"doan":["là","Việc làm"],"vai":"ket_luan","phuong_thuc":"khong","cuc":"khang_dinh","quy_tac":"q1"}]}

## Đầu ra
JSON thuần, không chữ giải thích: {"units": [{"unit_id": "...", "dong": [...]}]}, cộng cac_muc_con, ngoai_le, bo_qua khi có. Mỗi unit_id của lô đúng một mục."""
PROMPTS["menh-de-12"] = SYSTEM_12
COMPACT = {"menh-de-12"}  # [A57] phiên bản khuôn gọn: đầu ra phải qua expand_unit trước normalize và cổng
# [A61] Lượt 2 của 1.6A-v2 (clause_roles.py) ghi khuôn gọn; lời nhắc nằm ở clause_roles nên phiên bản của nó không có trong PROMPTS.
V2_PREFIX = "vai-nhom-"


def is_compact(version):
    return version in COMPACT or version.startswith(V2_PREFIX)
# [A57] Cỡ lô của khuôn gọn: model flash dùng phần lớn token ra để suy nghĩ ngầm (Gemini báo reasoning_tokens: lô 19 đơn vị ra 28.000 token,
# hai lần cụt max_tokens vì suy nghĩ 30.000); lô nhỏ thì không chạm trần. Bản cũ giữ C.BATCH_SIZE để hộp cát và cache cũ khớp như trước.
LOT_SIZE_COMPACT = 8


def lot_size(version=None):
    return LOT_SIZE_COMPACT if is_compact(version or PROMPT_VERSION) else C.BATCH_SIZE
NO_BO_NGU = {"menh-de-9", "menh-de-10", "menh-de-11", "menh-de-12"}  # [A55, A56] phiên bản lời nhắc mà bo_ngu khác rỗng là lỗi cổng (bổ ngữ phải là dòng dieu_kien)
SYSTEM = PROMPTS.get(PROMPT_VERSION)  # None với lượt 2 v2 (A61): lần chạy đó không dùng xuat/nhap của module này

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


BO_NGU_ALIAS = {"chu": "original_text", "pham_vi": "scope"}

_NEG_LEAD = re.compile(r"(không|chưa)\s")
_NEG_TAIL = re.compile(r"(^|\s)(không|chưa|chẳng)\s*$")


def effective_cuc(d):
    """[THÊM, A54, chủ đề tài duyệt 21/11] Cực của một dòng menh_de do MÁY quyết lại khi phủ định kép (lỗi A4): menh_de còn mở đầu bằng
    "không"/"chưa" mà cuc = phu_dinh thì chữ phủ định đã nằm trong menh_de (1.6B đặt tên theo chữ đó, ví dụ `lack_work_permit`),
    nên cờ phu_dinh lật nghĩa lần hai. Máy giữ nguyên chữ (không viết lại, cache 1.6B còn đúng) và đặt cực khang_dinh. Áp cả khi chữ sau là
    "được"/"phải" ("không được thành lập", "không phải thực hiện ..."): 1.6B cũng đã nuốt phủ định vào tên (`..._omitted`, `exempt_from_...`).
    Không sửa khi trong trich, ngay trước menh_de còn một chữ phủ định khác (phu_dinh khi ấy có căn cứ ở nguồn). Mọi đường đọc cực của 1.6A
    (1.6B, KU của 2.6, 1.8) phải đi qua hàm này."""
    c = d.get("cuc", "")
    if c != "phu_dinh" or d.get("loai") != "menh_de":
        return c
    m = " ".join((d.get("menh_de") or "").split()).lower()
    if not _NEG_LEAD.match(m):
        return c
    for t in d.get("trich") or []:
        tl = " ".join((t or "").split()).lower()
        k = tl.find(m)
        if k >= 0 and _NEG_TAIL.search(tl[:k]):
            return c
    return "khang_dinh"


def _bo_ngu_keys(b):
    """[THÊM, A41, chủ đề tài duyệt 18/11] Đổi tên khoá của một mục bo_ngu theo BO_NGU_ALIAS. Vì sao: lời nhắc menh-de-3 không ghi tên khoá
    của bo_ngu (lỗi của lời nhắc, đóng băng theo A39); phiên Claude Code tự đặt {chu, pham_vi} ở 6/6 mục trên tập con. Chỉ đổi TÊN khoá:
    giá trị vẫn qua cổng nguyên văn và tập scope; khoá lạ khác vẫn trượt. Mục đã dùng khoá đúng thì giữ nguyên."""
    if not isinstance(b, dict) or any(v in b for v in BO_NGU_ALIAS.values()):
        return b
    return {BO_NGU_ALIAS.get(k, k): v for k, v in b.items()}


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
            if isinstance(d.get("bo_ngu"), list):
                d["bo_ngu"] = [_bo_ngu_keys(b) for b in d["bo_ngu"]]
        out.append(d)
    return out


def gate_unit(ctx, rows, reason_field=LLM_REASON, version=None):
    """-> (lỗi, cờ): hai danh sách (chỉ số dòng, thông điệp). Lỗi = vi phạm khuôn hoặc nguồn (máy chứng minh được);
    cờ = dấu hiệu đáng xem nhưng có ca đúng (ví dụ "được trả lương" là chữ đúng). Không kiểm được nghĩa.
    version: phiên bản lời nhắc của đầu ra (mặc định PROMPT_VERSION của lần chạy); từ menh-de-9 bo_ngu khác rỗng là lỗi (A55)."""
    err, flag = [], []
    no_bo_ngu = (version or PROMPT_VERSION) in NO_BO_NGU or (version or PROMPT_VERSION).startswith(V2_PREFIX)
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
            if no_bo_ngu and d["bo_ngu"]:
                E("bo_ngu không còn dùng (A55): bổ ngữ phải là dòng dieu_kien riêng")
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


# ---- Khuôn gọn (A57): máy dựng lại khuôn cũ từ đầu ra gọn. Hàm này chỉ SUY RA trường từ chữ luật và từ trường LLM đã ghi,
# không sửa giá trị LLM ghi (giá trị sai vẫn đi tới cổng và bị bắt), nên không nới phép kiểm nào.
ROW_KEYS_12 = {"doan", "vai", "phuong_thuc", "cuc", "quy_tac", "nhom_hoac", "chu_the", "doi_so", "liet_ke", "chua_ro"}
UNIT_KEYS_12 = {"unit_id", "dong", "cac_muc_con", "ngoai_le", "bo_qua"}
BO_QUA_12 = {"khong_quy_pham", "dan_chieu_mo", "dan_chieu_ngoai"}
_LEAD_TAIL = re.compile(r"[^,;.:]*(sau đây|như sau|gồm|bao gồm)\s*:?\s*$")


def _core(doan):
    """Nối các đoạn thành menh_de theo cách bản cũ ghi: bỏ dấu câu cuối, hạ chữ hoa đầu câu (trừ chữ viết tắt toàn hoa)."""
    s = " ".join(x.strip() for x in doan if isinstance(x, str)).strip().rstrip(".;:,").strip()
    return s[:1].lower() + s[1:] if len(s) > 1 and s[1:2].islower() else s


def _source_of(chu, ctx):
    """nguon của chủ thể = chỗ chữ của nó xuất hiện, xét chữ đơn vị trước (bản cũ để LLM tự ghi và hay ghi sai, A57)."""
    for nguon, part in (("chinh", ctx["text"]), ("cau_dan", ctx["chapeau"]), ("tieu_de", ctx["heading"])):
        if chu and part and chu in part:
            return nguon
    return "chinh"  # không tìm thấy: cổng sẽ báo "chu_the.chu không nguyên văn"


def expand_unit(ctx, unit):
    """Đầu ra gọn của một đơn vị -> các dòng khuôn cũ (trước normalize). Khoá lạ được chuyển nguyên vào dòng để cổng báo trường thừa."""
    rows = []
    for r in unit.get("dong") if isinstance(unit.get("dong"), list) else [unit.get("dong")]:
        if not isinstance(r, dict):
            rows.append(r)
            continue
        doan = r.get("doan") if isinstance(r.get("doan"), list) else []
        row = {}
        extra = sorted(set(r) - ROW_KEYS_12)
        if extra:  # khoá lạ (kể cả trường khuôn cũ như trich, loai): giữ dưới một khoá riêng để cổng báo "thừa", không để trường máy dựng đè mất
            row["khoa_thua"] = extra
        row.update({k: r[k] for k in ("vai", "phuong_thuc", "cuc", "quy_tac", "nhom_hoac", "doi_so", "liet_ke", "chua_ro") if k in r})
        row.update(loai="menh_de", menh_de=_core(doan), trich=[x for x in doan if isinstance(x, str)])
        ct = r.get("chu_the")
        if isinstance(ct, dict):
            nguon = _source_of(ct.get("chu"), ctx)
            row["chu_the"] = {**{f"thua_{k}": v for k, v in ct.items() if k not in ("chu", "loai")}, "chu": ct.get("chu"), "loai": ct.get("loai"), "nguon": nguon}  # khoá lạ (kể cả nguon do LLM ghi): cổng báo sai khuôn
            if nguon != "chinh" and isinstance(ct.get("chu"), str):
                row["trich"].append(ct["chu"])  # cổng đòi trich có mẩu từ câu dẫn/tiêu đề khi chủ thể lấy từ đó
        elif ct is not None:
            row["chu_the"] = ct  # sai khuôn: để cổng báo
        rows.append(row)
    exc = unit.get("ngoai_le") or []
    for ref in ctx["refs"]:
        rows.append({"loai": "con_tro", "vai": "ngoai_le" if ref["dich"] in exc else "dieu_kien", "targets": [ref["dich"]], "trich": [ref["cum"]]})
    for t in exc if isinstance(exc, list) else [exc]:
        if t not in {ref["dich"] for ref in ctx["refs"]}:
            rows.append({"loai": "con_tro", "vai": "ngoai_le", "targets": [t], "trich": [ctx["text"]]})  # đích ngoài dan_chieu: cổng báo
    if unit.get("cac_muc_con") is not None:
        m = _LEAD_TAIL.search(ctx["text"] or "")
        rows.append({"loai": "bo_qua", "cac_muc_con": unit["cac_muc_con"], "trich": [m.group(0).strip() if m else ctx["text"]],
                     LLM_REASON: {"ma": "cau_dan", "giai_thich": "máy dựng từ cac_muc_con (A57)"}})
    if unit.get("bo_qua") is not None:
        rows.append({"loai": "bo_qua", "trich": [ctx["text"]], LLM_REASON: {"ma": unit["bo_qua"], "giai_thich": "máy dựng từ bo_qua của đơn vị (A57)"}})
    extra = set(unit) - UNIT_KEYS_12
    if extra:
        rows.append({"khoa_don_vi_thua": sorted(extra)})  # cổng báo "trường thiếu / thừa"
    return rows


_GAP_LOSS = re.compile(r"(^|\s)(không|chưa|hoặc)(\s|$)")  # bỏ chữ này giữa hai đoạn là ngược nghĩa hoặc mất một vế "hoặc": lỗi
_GAP_AND = re.compile(r"(^|\s)và(\s|$)")  # bỏ "và" có ca đúng (hai động từ chung tân ngữ): cờ


def _gap_lost(gap, row, other_words):
    """Chữ bị bỏ giữa hai đoạn có MẤT không: bỏ "không/chưa" mà cuc không ghi phu_dinh; bỏ một vế (sau khi trừ chữ nối và chữ phủ định
    đã ghi ở cuc) mà chữ của vế đó không có ở dòng nào khác của đơn vị (tách vế "hoặc" thành dòng riêng là đúng, A57)."""
    words = syllables(gap)
    if {"không", "chưa"} & set(words) and row.get("cuc") != "phu_dinh":
        return True
    rest = [w for w in words if w not in ("không", "chưa", "hoặc", "và")]
    return any(w not in other_words for w in rest)


def compact_checks(ctx, unit, rows):
    """Phần kiểm riêng của khuôn gọn, cộng vào cổng cũ. Lỗi: đoạn chứa chữ dẫn chiếu (dẫn chiếu thuộc dòng con_tro); bo_qua ngoài tập đóng;
    đơn vị không có dòng; giữa hai đoạn liên tiếp cùng nguồn có chữ "không/chưa/hoặc" bị bỏ mà phần bỏ MẤT (_gap_lost). Bỏ "không" mà cuc
    phu_dinh, hay bỏ một vế đã thành dòng riêng là đúng (đọc lần 1 của menh-de-12: 3/4 ca "không" và 18/34 ca "hoặc" thuộc loại này).
    Đoạn đầu "là" (định nghĩa "X là Y" -> ["là", "X"]) không kiểm khoảng bỏ. Cờ: chữ "và" bị bỏ."""
    err, flag = [], []
    if unit.get("bo_qua") is not None and unit["bo_qua"] not in BO_QUA_12:
        err.append((None, f"bo_qua của đơn vị {unit['bo_qua']!r}"))
    if not rows:
        err.append((None, "đơn vị không có dòng nào"))
    dong = unit.get("dong") if isinstance(unit.get("dong"), list) else []
    for i, r in enumerate(dong):
        doan = r.get("doan") if isinstance(r, dict) and isinstance(r.get("doan"), list) else []
        if isinstance(r, dict) and not doan:
            err.append((i, "doan rỗng"))
        for x in doan:
            for ref in ctx["refs"]:
                if isinstance(x, str) and ref["cum"] in x:
                    err.append((i, f"doan chứa chữ dẫn chiếu {ref['cum']!r}"))
        if doan[:1] == ["là"]:
            continue
        other = set()
        for j, o in enumerate(dong):
            if j != i and isinstance(o, dict):
                other |= set(syllables(" ".join(x for x in (o.get("doan") or []) + (o.get("liet_ke") or []) if isinstance(x, str))))
                other |= set(syllables((o.get("chu_the") or {}).get("chu") if isinstance(o.get("chu_the"), dict) else ""))
        for a, b in zip(doan, doan[1:]):
            for part in (ctx["text"], ctx["chapeau"], ctx["heading"]):
                ia = part.find(a) if isinstance(a, str) and part else -1
                ib = part.find(b, ia + len(a)) if ia >= 0 and isinstance(b, str) else -1
                if ia >= 0 and ib >= 0:
                    gap = part[ia + len(a):ib].lower()
                    if _GAP_LOSS.search(gap) and _gap_lost(gap, r, other):
                        err.append((i, f"doan bỏ chữ {gap.strip()[:40]!r}"))
                    elif _GAP_LOSS.search(gap) or _GAP_AND.search(gap):
                        flag.append((i, f"doan bỏ chữ {gap.strip()[:40]!r}"))
                    break
    return err, flag


# ---- Lượt rút gọn dòng dài (A58): sau 1.6A khuôn gọn, máy chọn dòng có lõi dài hay có danh sách, hỏi lại RIÊNG các dòng đó, rồi
# nhận dòng thay thế chỉ khi qua cổng và giữ đủ chữ của lõi cũ. Đây là lượt sinh thứ hai được máy kiểm, không phải LLM kiểm LLM.
RUT_GON_VERSION = "rut-gon-1"
SYSTEM_RUT_GON = """Mỗi mục là MỘT dòng đã tách từ một đơn vị Bộ luật Lao động mà lõi (doan) quá dài. Viết lại dòng đó thành các dòng ngắn hơn, cùng khuôn dòng: doan, vai, phuong_thuc, cuc, quy_tac, nhom_hoac, chu_the, doi_so, liet_ke, chua_ro.

Chỉ làm một trong ba cách:
1. dieu_kien chứa danh sách trường hợp hay đối tượng: mỗi mục một dòng dieu_kien cùng quy_tac; chữ dùng chung (ví dụ "dựa trên") là đoạn đầu doan của mỗi dòng. Các mục nối bằng "hoặc" hay dấu phẩy thay thế nhau thì cùng một nhom_hoac (của dòng cũ nếu có, không thì mã mới); nối bằng "và" (phải đủ hết) thì không nhom_hoac.
2. ket_luan chứa danh sách tân ngữ: giữ động từ trong doan, đưa các mục vào liet_ke.
3. Hai thuộc tính của CÙNG một đối tượng ("hợp đồng lao động xác định thời hạn có thời hạn từ 12 tháng đến 36 tháng"): hai dòng dieu_kien cùng quy_tac.
Cụm mô tả một đối tượng KHÁC (ví dụ "do cơ quan đại diện ngoại giao đề nghị thành lập" mô tả cơ sở giáo dục, không phải người lao động) giữ nguyên trong dòng. Không làm được thì trả lại đúng dòng cũ.

doan chép NGUYÊN VĂN, liền, từ tieu_de_dieu, khoan_cha hoặc chu_don_vi đã cho; mọi chữ của doan cũ phải còn trong doan hoặc liet_ke của các dòng mới. Giữ vai, phuong_thuc, cuc, chu_the, quy_tac của dòng cũ.

Đầu ra JSON thuần: {"thay": [{"id": "...", "dong": [...]}]}, mỗi id của đầu vào đúng một mục."""
PROMPTS[RUT_GON_VERSION] = SYSTEM_RUT_GON


def long_rows(unit):
    """Chỉ số các dòng khuôn gọn cần rút gọn: lõi từ LONG_SYL âm tiết, hoặc lõi có từ hai dấu phẩy (danh sách chưa tách)."""
    out = []
    for i, r in enumerate(unit.get("dong") or []):
        doan = r.get("doan") if isinstance(r, dict) and isinstance(r.get("doan"), list) else []
        core = " ".join(x for x in doan if isinstance(x, str))
        if len(syllables(core)) >= LONG_SYL or core.count(",") >= 2:
            out.append(i)
    return out


def rut_gon_item(ctx, unit, i):
    return {"id": f"{unit['unit_id']}#{i}", "tieu_de_dieu": ctx["heading"], "khoan_cha": ctx["chapeau"], "chu_don_vi": ctx["text"],
            "dong": unit["dong"][i]}


def apply_rut_gon(ctx, unit, replies, version="menh-de-12"):
    """replies: {chỉ số dòng: danh sách dòng thay}. -> (unit mới, [(chỉ số, 'nhan' | lý do bỏ)]).
    Nhận khi: tách thành từ hai dòng, mỗi dòng là object có doan; mọi âm tiết của doan cũ (trừ chữ nối "và/hoặc") còn trong doan hoặc
    liet_ke mới; giữ vai, phuong_thuc, cuc, chu_the, quy_tac của dòng cũ; đơn vị sau khi thay KHÔNG thêm lỗi cổng. Trả một dòng: 'giu' nếu
    y nguyên, còn đổi trường (ví dụ lén đặt nhom_hoac) thì bỏ. Không nhận thì giữ dòng cũ (không sửa gì)."""
    base_err = len(check_unit(ctx, unit, version)[1])
    dong, status = list(unit["dong"]), []
    for i in sorted(replies, reverse=True):  # thay từ cuối lên để chỉ số các dòng trước không dịch
        new = replies[i]
        old = set(syllables(" ".join(x for x in dong[i].get("doan") or [] if isinstance(x, str))))
        if not isinstance(new, list) or not new or not all(isinstance(r, dict) and isinstance(r.get("doan"), list) and r["doan"] for r in new):
            status.append((i, "sai hình"))
            continue
        got = set(syllables(" ".join(x for r in new for x in (r.get("doan") or []) + (r.get("liet_ke") or []) if isinstance(x, str))))
        lost = old - got - {"và", "hoặc"}  # chữ nối mất khi tách danh sách là đúng
        if lost:
            status.append((i, f"mất chữ {sorted(lost)[:6]}"))
            continue
        keep = ("vai", "phuong_thuc", "cuc", "chu_the", "quy_tac")
        if any((r.get(k) or None) != (dong[i].get(k) or None) for r in new for k in keep):
            status.append((i, "đổi vai/phuong_thuc/cuc/chu_the/quy_tac"))
            continue
        if len(new) == 1:  # không tách: chỉ là "giữ", mọi trường phải như cũ (cả nhom_hoac)
            status.append((i, "giu" if new[0] == dong[i] else "giữ nhưng đổi trường"))
            continue
        trial = {**unit, "dong": dong[:i] + new + dong[i + 1:]}
        if len(check_unit(ctx, trial, version)[1]) > base_err:
            status.append((i, "thêm lỗi cổng: " + "; ".join(m[:60] for _j, m in check_unit(ctx, trial, version)[1])[:200]))
            continue
        dong = trial["dong"]
        base_err = len(check_unit(ctx, trial, version)[1])
        status.append((i, "nhan"))
    return {**unit, "dong": dong}, sorted(status)


def check_unit(ctx, out_unit, version=None):
    """MỘT đường cho mọi chỗ nhập đầu ra 1.6A (nhap, ku_nhap, gemini, chấm bộ khó): -> (dòng khuôn cũ đã normalize, lỗi, cờ).
    out_unit là mục {"unit_id", "dong", ...} của đầu ra. Bản khuôn cũ: y như trước (normalize + gate_unit)."""
    version = version or PROMPT_VERSION
    if not is_compact(version):
        rows = normalize(out_unit.get("dong") if isinstance(out_unit, dict) else out_unit)
        err, flag = gate_unit(ctx, rows, version=version)
        return rows, err, flag
    unit = out_unit if isinstance(out_unit, dict) else {"dong": out_unit}
    rows = normalize(expand_unit(ctx, unit))
    e2, f2 = compact_checks(ctx, unit, rows)
    err, flag = gate_unit(ctx, rows, version=version) if rows else ([], [])
    return rows, err + e2, flag + f2


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


def sandbox_model():
    """(model, effort) mà hộp cát của 1.6A theo KU, 1.6B, 1.7, 1.9 đòi: khoá `hop_cat.model`, `hop_cat.effort` của docs/llm_config.md.
    Trước A46 là hằng số chép ở từng module (Sonnet 5.5, high theo A39); đưa vào cấu hình để lần chạy KLTN_LLM_RUN=ckey đổi model
    (khoá `ckey.hop_cat.*`) mà không sửa mã, và lần chạy mặc định giữ nguyên giá trị cũ."""
    cfg = L.load_config()
    return cfg["hop_cat.model"], cfg["hop_cat.effort"]


def sandbox_config(d):
    f = pathlib.Path(d) / "cau_hinh.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"model": model(), "effort": None}


FULL_OUT = corpus.ROOT / "data" / "llm_cache" / "propositions"  # neo theo gốc repo: tiep.py của 1.6B chạy với cwd là thư mục làm việc


def full_cache_path():
    """File nhập kết quả `tat_ca`. Kho con (A41) ghi file riêng `<doc>.<tên tập con>.json`: nhập ghi đè cả file, nên dùng
    chung một file thì kết quả tập con và kho đầy đủ đè lên nhau."""
    return FULL_OUT / corpus.cache_name(corpus.BASE_DOC_ID)


# ---- 2.6 (A42): 1.6A theo đơn vị tri thức (KU, knowledge_units.py) ----
# KU của bản parse BLLĐ mang mã `uid`, nên cache 1.6A của KB gốc (full_cache_path) dùng nguyên. Mọi KU nhập ở 2.6 ghi vào thư mục riêng
# `ku/<doc>[.<tập con>].json`, KHÔNG vào file của KB gốc: 1.6B, 1.7, 1.8 của giai đoạn 1 đọc cả file đó như danh sách đơn vị của BLLĐ (mã lạ
# như `D154.K8a@h...` làm hỏng thứ tự), và `nhap --tat-ca` ghi đè cả file. Nhập chỉ THÊM: KU đã có mà dòng khác thì dừng.

KU_DIR = FULL_OUT / "ku"


def ku_cache_path(doc_id):
    return KU_DIR / corpus.cache_name(doc_id)


def load_ku_cache():
    """{mã KU: {dong, loi, co}}: cache 1.6A của KB gốc (khoá `uid`) cộng mọi file `ku/` của kho đang chạy (đúng tập con)."""
    paths = [full_cache_path()] if full_cache_path().exists() else []
    for p in sorted(KU_DIR.glob("*.json")):
        _doc, _, sub = p.name[:-len(".json")].partition(".")
        if sub == corpus.cache_tag().lstrip("."):  # đúng kho VÀ đúng lần chạy LLM (A46): `<doc>.lldnn.ckey.json` chỉ thuộc lần chạy ckey của tập con
            paths.append(p)
    out = {}
    for p in paths:
        data = json.loads(p.read_text(encoding="utf-8"))
        if data.get("prompt_version") != PROMPT_VERSION:
            raise SystemExit(f"{p} là của lời nhắc {data.get('prompt_version')!r}, code đang ở {PROMPT_VERSION!r}")
        for k, v in data["units"].items():
            if k in out and out[k]["dong"] != v["dong"]:
                raise SystemExit(f"{k} có hai bản 1.6A khác nhau ({p.name})")
            out.setdefault(k, v)
    return out


def ku_lots(kus):
    """Lô cho các KU (thứ tự cho sẵn): mỗi lô các KU của MỘT Điều cùng mốc xuất hiện đầu (một đơn vị một lần trong lô, vì LLM thấy `uid`),
    Điều dài thì cắt theo lot_size() (khuôn cũ: C.BATCH_SIZE như 1.6A cũ; khuôn gọn: nhỏ hơn, A57)."""
    groups = {}
    for k in kus:
        groups.setdefault((C.dieu_of(k["unit"]), k["first"]), []).append(k)
    n = lot_size()
    return [g[i:i + n] for g in groups.values() for i in range(0, len(g), n)]


def ku_xuat(thu_muc, kus, run_model=None, effort=None, khoi=20):
    """Dựng hộp cát 1.6A cho các KU chưa có trong cache (người gọi lọc). cau_hinh.json ghi danh sách mã KU từng lô để nhập đối chiếu."""
    d = pathlib.Path(thu_muc)
    if d.exists() and any(d.iterdir()):
        raise SystemExit(f"{d} đã có nội dung, không ghi đè")
    root = corpus.ROOT.resolve()
    if d.resolve() == root or root in d.resolve().parents:
        raise SystemExit(f"{d} nằm trong repo; thư mục làm việc phải ở NGOÀI repo (A36)")
    lots = ku_lots(kus)
    default_model, default_effort = sandbox_model()
    run_model, effort = run_model or default_model, effort or default_effort
    (d / "lo").mkdir(parents=True, exist_ok=True)
    (d / "out").mkdir(exist_ok=True)
    (d / "system.txt").write_text(SYSTEM + "\n", encoding="utf-8", newline="\n")
    for i, lot in enumerate(lots, 1):
        (d / "lo" / f"{i:03d}.json").write_text(user_message([k["ctx"] for k in lot]) + "\n", encoding="utf-8", newline="\n")
    (d / "HUONG_DAN.md").write_text(HUONG_DAN.replace("@MODEL@", run_model).replace("@ALIAS@", ALIAS.get(run_model, run_model)).replace("@EFFORT@", effort)
                                    .replace("@KHOI@", str(khoi)).replace("@N@", f"{len(lots):03d}"), encoding="utf-8", newline="\n")
    (d / "cau_hinh.json").write_text(json.dumps({"model": run_model, "effort": effort, "prompt_version": PROMPT_VERSION, "pham_vi": "ku", "khoi": khoi,
                                                "tap_con": corpus.SUBSET, "lots": [[k["ku"] for k in lot] for lot in lots]}) + "\n", encoding="utf-8")
    return f"đã dựng {d}: {len(lots)} lô, {sum(map(len, lots))} KU, model {run_model}, effort {effort}, lời nhắc {PROMPT_VERSION}"


def ku_nhap(thu_muc, catalog_kus):
    """Kiểm từng lô (đầu vào trùng từng byte với KU hiện tại, nhật ký đúng model, hình, cổng) rồi THÊM vào file KU của từng văn bản.
    KU đã có trong cache: cùng dòng thì bỏ qua, khác dòng thì DỪNG, không ghi gì. -> danh sách (lô, lý do) không nhận."""
    d = pathlib.Path(thu_muc)
    cfg = sandbox_config(d)
    if cfg.get("pham_vi") != "ku" or cfg.get("prompt_version") != PROMPT_VERSION or (d / "system.txt").read_text(encoding="utf-8") != SYSTEM + "\n":
        raise SystemExit("hộp cát không phải hộp cát KU hoặc dựng với lời nhắc khác code: không nhập")
    if cfg.get("tap_con") != corpus.SUBSET:
        raise SystemExit(f"hộp cát dựng với tập con {cfg.get('tap_con')!r}, đang chạy với {corpus.SUBSET!r}: không nhập")
    log = {}
    if (d / "nhat_ky.tsv").exists():
        for line in (d / "nhat_ky.tsv").read_text(encoding="utf-8").splitlines():
            p = [x.strip() for x in line.split("\t")]
            if len(p) >= 2 and p[0].isdigit():
                log[int(p[0])] = p[1]
    new, bad_lot = {}, []
    for n, ids in enumerate(cfg["lots"], 1):
        missing = [k for k in ids if k not in catalog_kus]
        if missing:
            bad_lot.append((n, f"KU không còn trong kho: {missing[:3]}"))
            continue
        lot = [catalog_kus[k] for k in ids]
        f = d / "out" / f"{n:03d}.json"
        if not f.exists():
            bad_lot.append((n, "chưa có file"))
            continue
        if (d / "lo" / f"{n:03d}.json").read_text(encoding="utf-8") != user_message([k["ctx"] for k in lot]) + "\n":
            bad_lot.append((n, "lo/ khác đầu vào hiện tại"))
            continue
        if log.get(n) != cfg["model"]:
            bad_lot.append((n, f"nhat_ky báo {log.get(n)!r}, cần {cfg['model']}"))
            continue
        try:
            items = {it["unit_id"]: it for it in json.loads(f.read_text(encoding="utf-8"))["units"]}  # cả mục: khuôn gọn có trường đơn vị (A57)
        except (ValueError, KeyError, TypeError) as e:
            bad_lot.append((n, f"sai hình: {e}"))
            continue
        want = {k["unit"]: k for k in lot}
        if set(items) != set(want):
            bad_lot.append((n, f"unit_id lệch: thiếu {sorted(set(want) - set(items))}, thừa {sorted(set(items) - set(want))}"))
            continue
        for uid, item in items.items():
            rows, err, flag = check_unit(want[uid]["ctx"], item)
            new[want[uid]["ku"]] = (want[uid]["doc"], {"dong": rows, "loi": [[i, m] for i, m in err], "co": [[i, m] for i, m in flag]})
    by_doc = {}
    for ku, (doc, entry) in new.items():
        by_doc.setdefault(doc, {})[ku] = entry
    files = {}
    for doc, entries in by_doc.items():
        p = ku_cache_path(doc)
        data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"prompt_version": PROMPT_VERSION, "model": cfg["model"], "effort": cfg["effort"], "units": {}}
        if data["prompt_version"] != PROMPT_VERSION or data["model"] != cfg["model"]:
            raise SystemExit(f"{p}: lời nhắc hoặc model khác hộp cát; không nhập")
        for ku, entry in entries.items():
            old = data["units"].get(ku)
            if old is not None and old["dong"] != entry["dong"]:
                raise SystemExit(f"DỪNG: {ku} đã có trong {p.name} với dòng khác; không ghi gì")
            data["units"].setdefault(ku, entry)
        files[p] = data
    for p, data in files.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    n_err = sum(len(e["loi"]) for _, e in new.values())
    print(f"nhập {len(new)} KU vào {sorted(p.name for p in files)}; {sum(len(e['dong']) for _, e in new.values())} dòng, {n_err} lỗi cổng")
    for n, why in bad_lot:
        print(f"  lô {n:03d} KHÔNG nhận: {why}")
    return bad_lot


def lots_for(pham_vi, ctxs):
    """thi_diem: 30 đơn vị, một lô mỗi Điều; tat_ca: mọi đơn vị 1.6A, chia lô đúng như 1.6A cũ (concepts.make_batches:
    một Điều mỗi lô, Điều dài tách lô), để số lô và ranh giới lô so được với bản cũ."""
    if pham_vi == "thi_diem":
        return pilot_batches(ctxs, load_gold())
    if pham_vi == "tat_ca":
        return C.make_batches(list(ctxs.values()), size=lot_size())
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
    (d / "cau_hinh.json").write_text(json.dumps({"model": m, "effort": effort, "prompt_version": PROMPT_VERSION, "pham_vi": pham_vi, "khoi": khoi,
                                                "tap_con": corpus.SUBSET}) + "\n", encoding="utf-8")
    print(f"đã dựng {d}: {len(lots)} lô, {sum(map(len, lots))} đơn vị, model {m}, effort {effort}, lời nhắc {PROMPT_VERSION}")


def nhap(thu_muc, out_path=None):
    d, ctxs = pathlib.Path(thu_muc), contexts()
    cfg = sandbox_config(d)
    pham_vi = cfg.get("pham_vi", "thi_diem")
    if cfg.get("prompt_version", PROMPT_VERSION) != PROMPT_VERSION or (d / "system.txt").read_text(encoding="utf-8") != SYSTEM + "\n":
        raise SystemExit(f"hộp cát dựng với lời nhắc {cfg.get('prompt_version')}, code đang là {PROMPT_VERSION}: không nhập")
    if cfg.get("tap_con") != corpus.SUBSET:  # A41: hộp cát dựng ở kho nào thì chỉ nhập ở kho đó
        raise SystemExit(f"hộp cát dựng với tập con {cfg.get('tap_con')!r}, đang chạy với {corpus.SUBSET!r} (KLTN_TAP_CON): không nhập")
    lots, want = lots_for(pham_vi, ctxs), cfg["model"]
    if out_path is None:
        out_path = LLM_OUT if pham_vi == "thi_diem" else full_cache_path()
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
            items = {it["unit_id"]: it for it in data["units"]}  # cả mục: khuôn gọn có trường đơn vị (A57)
        except (ValueError, KeyError, TypeError) as e:
            bad_lot.append((n, f"sai hình: {e}"))
            continue
        ids = {c["id"] for c in lot}
        if set(items) != ids:
            bad_lot.append((n, f"unit_id lệch: thiếu {sorted(ids - set(items))}, thừa {sorted(set(items) - ids)}"))
            continue
        for uid, item in items.items():
            rows, err, flag = check_unit(ctxs[uid], item)
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
            rows, err, flag = check_unit(ctxs[it["unit_id"]], it)
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
