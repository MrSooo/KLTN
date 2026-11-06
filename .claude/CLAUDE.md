# CLAUDE.md — luật làm việc trong dự án kltn

## 1. Cách làm việc (đọc trước, quan trọng nhất)

Mục tiêu của user là **hiểu và kiểm soát được mình đang làm gì**. Claude viết code, user duyệt từng bước. Vì vậy:

1. **Từng bước nhỏ, không làm một mạch.** Mỗi lượt chỉ làm MỘT bước. Trước khi sửa: nói ngắn sẽ sửa file nào, vì sao. Sau khi sửa: dừng, tóm tắt, chờ user xem. Không tự nối sang bước kế tiếp, không chạy chuỗi lệnh dài mà chưa báo.
2. **Plan do user đưa là chuẩn.** User thường lập plan ở nơi khác rồi dán vào. Làm đúng thứ tự plan, không thêm việc ngoài plan, không "tiện tay" refactor. Thấy plan thiếu hoặc mâu thuẫn với code thì nói ra và hỏi, đừng tự sửa plan.
3. **Gặp điểm mơ hồ thì HỎI, không đoán** (định dạng output, tên cột, hướng cạnh, vị trí file, giá trị rỗng, thứ tự ghi...). Gom nhiều câu hỏi vào một lượt. Chỉ khi prompt nhiệm vụ ghi rõ "không hỏi lại" thì mới tự chọn cách đơn giản nhất, và phải ghi mọi lựa chọn vào file `docs/quyet_dinh/*_quyet_dinh.txt`, chỗ lệch spec đặt lên đầu.
4. **Không làm việc khó đảo ngược khi chưa được bảo:** commit, push, xoá hoặc ghi đè file, chạy `--llm live` (tốn hạn mức hoặc tiền), cài gói vào repo. Trước khi ghi đè thì xem file đích.
5. **Báo cáo trung thực, giải thích để user hiểu.** Tiếng Việt, ngắn. Nói rõ cái gì đã chạy và kết quả, cái gì CHƯA kiểm. Không nói "xong" khi chưa chạy test. Test lỗi thì dán đầu ra lỗi. Khi đổi hành vi, nói đổi gì và ảnh hưởng chỗ nào, không chỉ liệt kê tên file.
6. **Code phải đọc được để user duyệt:** thay đổi nhỏ, tách theo việc, docstring và comment tiếng Việt giải thích *vì sao* (không chép lại code). Không để lại code chết hay cờ thừa.
7. **Bí mật:** API key chỉ nằm trong biến môi trường (`GEMINI_API_KEY`, `ANTHROPIC_API_KEY`). Không bao giờ dán vào chat, file trong repo, test hay báo cáo.
8. **Phản biện (critical review) là bắt buộc, trước khi làm và trước khi báo xong.** Với mỗi bước tự hỏi: plan/spec có mâu thuẫn với code hoặc dữ liệu thật không; giả định nào mình chưa kiểm; cách làm này có thể sai ở đâu và sai sẽ lan xuống bước nào; con số nào chưa đối chiếu với đĩa. Kết quả phản biện (kể cả "không thấy vấn đề, đã kiểm X và Y") phải có một mục ngắn **"Phản biện"** trong báo cáo cuối lượt, không để chỉ nằm trong đầu. Không đồng tình với plan hoặc với chính cách làm của mình thì nói ra, không im lặng làm theo.
9. **Gặp khó khăn thì DỪNG và HỎI, không tự quyết.** Khó khăn gồm: test lỗi chưa rõ nguyên nhân; lệnh hoặc công cụ không chạy được; plan mâu thuẫn với code hoặc dữ liệu; hai cách làm đều hợp lý; phải nới quy tắc, bỏ một kiểm tra, đổi plan/model/tham số mới đi tiếp được. Không tự chọn "cách tạm", không tự đi vòng. Báo lại: đã thử gì, lỗi nguyên văn, các hướng có thể và đề xuất của mình, rồi chờ user. Chế độ "không hỏi lại" ở mục 3 chỉ áp cho chỗ spec im lặng, **không** áp cho khó khăn: gặp khó khăn vẫn dừng và hỏi.
10. **Cây làm việc chỉ có Bộ luật Lao động.** Ngoài `archive/`, không được có dữ liệu, báo cáo, plan, ví dụ hay tên gì thuộc lĩnh vực cũ (thừa kế, BLDS 2015, Điều 609-662). `archive/v1_thua_ke/` chỉ để tham khảo: **không sửa, không chạy, không import, không chép ngược vào cây, không dẫn đường dẫn của nó trong code hay test.** Không cần thì không đụng tới. Thật sự cần (ví dụ viết lại R1-R4 ở L7, xem hành vi cũ của A4 ở L6) thì chỉ mở ra đọc, nói rõ với user là đang mở archive, và viết bản mới cho lao động ở ngoài archive; muốn lấy file ra khỏi archive thì hỏi. File mới tạo không được chứa dữ liệu hay ví dụ v1. Khi một bước L refactor một file code hoặc tài liệu còn ví dụ v1 thì xoá ví dụ v1 khỏi file đó ngay trong bước đó.

## 2. Dự án là gì

Pipeline biến Bộ luật Lao động 45/2019 (bản gốc) và các văn bản dưới luật (nghị định, thông tư, nghị quyết, bản hợp nhất) thành cơ sở tri thức **thích nghi theo ngày hiệu lực**: mỗi văn bản là một sự kiện nạp, tạo phiên bản mới và đóng phiên bản cũ. Đồ án tốt nghiệp. **Plan chuẩn:** `plan/ke_hoach/ke_hoach_kb_laodong_agent_2026-11-06.md` (bước L0-L11). Bản v1 (Bộ luật Dân sự 2015 phần 4, thừa kế) đã đóng băng ở commit `25c65e6` và nằm trong `archive/v1_thua_ke/` (xem README ở đó).

Bảng dưới là **code v1 (bước A)**, đang được refactor tại chỗ theo plan: L1 mở rộng A1, L2 mở rộng A2, L5 là A3/A6 cho mọi văn bản, L6 mở rộng A4 (phần lõi của đợt này). L3, L4, L7-L11 là bước mới.

| Bước | File | Việc |
|---|---|---|
| A1 | `src/a1_parse.py` | md → bộ ba (s,p,o) |
| A2 | `src/a2_edges.py` | cạnh cấu trúc `contains`/`part_of` và `refers_to` |
| A3 | `src/a3_exceptions.py` | cạnh `exception_of` (quy tắc "không áp dụng", "trừ ... sau đây:") |
| A4 | `src/a4_versions.py`, `src/a4_llm.py` | áp văn bản sửa đổi, lưu phiên bản; tầng LLM chuẩn hoá khối chỉ thị |
| A5 | `src/a5_checks.py` | kiểm tra A1-A4 |
| A6 | `src/a6_general_exceptions.py` | ngoại lệ chung ("trừ trường hợp ...") |
| A7 | `src/a7_graph.py` | đồ thị gộp |
| A8 | `utils/a8/` | trang HTML xem đồ thị (tùy chọn, không thuộc báo cáo A1-A7) |

Thư mục: `src/` (a1..a7 + `run_all.py`), `tests/` (mọi `test_*.py` và `eval_*.py`), `utils/` (A8, `render_report.py`), `data/` (`raw/labor/{base,dev,manifest.csv}`, `processed/<bước>/` do code tạo), `docs/`, `report/`, `plan/`, `archive/v1_thua_ke/` (v1, xem dưới). Đừng dựng lại `.work/` hay `result/` (đã bỏ).

Bố cục tài liệu (tên file chữ thường, `snake_case`; bước mới theo cùng cấu trúc):
- `docs/quyet_dinh/`: quyết định kỹ thuật, viết tay (`a4_quyet_dinh.txt`, `a6_a7_quyet_dinh.txt` mô tả hành vi code; bước mới thêm file cùng kiểu).
- `docs/bao_cao_chay/<bước>/`: báo cáo chữ do code sinh ra mỗi lần chạy, không sửa tay. Thư mục này **không còn** trong cây (bản v1 ở archive); code sẽ tạo lại khi chạy bước tương ứng.
- `docs/ref/`: tài liệu tham khảo plan trỏ tới. `KetQua_A1_A4`, `KetQua_A5`: bản cũ 22-23/10, chỉ lấy quy ước và giới hạn đã ghi; số liệu, đường dẫn, mã `BLDS2015` trong đó là của v1. `KhaoSat_BLLD_ToanVan`: bản cắt 07/11 (đã bỏ phần liên quan heldout); mục 4 là danh sách ô giao quyền cho L3. `docs/llm_config.md`: model, temperature, ngày khoá (xem mục 4).
- `report/`: `ky_thuat/` (giải thích code A1-A7 của v1), `review/` (rà soát và kế hoạch sửa A1-A7, các lỗi fail-open cần sửa khi refactor). Hai thư mục này mô tả code còn ở `src/` nên được giữ, nhưng còn ví dụ v1 (xem mục 5). `tong_hop/` (báo cáo cho thầy) sẽ viết lại cho v2; bản v1 ở archive.
- `plan/`: chỉ có `ke_hoach/` (plan chuẩn L0-L11). Không sửa nội dung plan do user đưa; đường dẫn dạng `claude/…` trong đó là của project web. Mọi plan, thiết kế và kiến thức của v1 ở `archive/v1_thua_ke/plan/`: đề cương, kế hoạch cũ, `thiet_ke/` (hướng dẫn R1-R4, định nghĩa bước B-D và bộ quét, sổ quyết định), `kien_thuc/`. Plan mới nhắc "R1-R4", "C1-C4", "bộ quét 5 loại lỗi", "kế hoạch cũ" ở L7-L9: tới các bước đó mới mở archive để đọc (theo quy tắc 10).

Quy ước dữ liệu: id dạng `<doc_id>.D154.K8a.b` (hậu tố chữ như `D2a`, `K8a` là bình thường; Điểm `đ` viết thành `dd` trong id; phụ lục `<doc_id>.PL1.M2.R15`). `doc_id` = tên file trong `data/raw/labor/` (ví dụ `BLLD_45-2019`, `ND_145-2020`). Thông tin văn bản (số hiệu, ngày, số Điều) đọc từ `manifest.csv` (UTF-8 có BOM, đọc bằng `utf-8-sig`), không chép cứng vào code. Mỗi bước đầu ra là đầu vào của bước sau và có số đối chiếu cứng, nên một giả định sai âm thầm sẽ lan xuống các bước sau.

**Heldout:** nhóm văn bản dùng để đo, plan yêu cầu để ngoài repo. **Không mở, không đọc, không ghi vào tài liệu hay memory** bất kỳ nội dung hay đường dẫn nào của nó cho đến khi user bảo bắt đầu đo. Chỉ `data/raw/labor/` (base + dev) được dùng khi dựng. Cột `quan_he` của manifest chỉ là mốc kiểm, không phải đầu vào của pipeline.

## 3. Quy ước kỹ thuật

- **Chỉ dùng thư viện chuẩn của Python.** Ngoại lệ duy nhất: chế độ `--llm live` của A4 cần gói của nhà cung cấp (`anthropic` hoặc `google-genai`), cài trong `.venv` (đã nằm trong `.gitignore`), không cài vào Python hệ thống.
- Chạy script: `python -I src/<file>.py <md>` (cờ `-I` để không nạp nhầm file cạnh script). Windows: Python của venv là `.venv\Scripts\python.exe`.
- Test: `python -I tests/test_aN.py` (dòng cuối phải là `tổng test lỗi: 0`). Chạy cả pipeline: `python -I src/run_all.py`; thêm `--a8` để dựng trang xem, `--tests` để chạy bộ kiểm thử ngoài và các bộ test. **Hiện tại test, `run_all.py` (hằng `BASES`, `data/dev_amend/...`), bảng `EXPECTED` của A5/A7 và `utils/render_report.py` còn trỏ dữ liệu v1 đã archive nên lỗi có chủ đích cho đến L0.** Mốc "đã xanh" của v1: 287 test / 11 file (ghi ở `archive/v1_thua_ke/README.md`).
- Máy đang `core.autocrlf=true`: sau khi chạy code, `git status` có thể hiện file M giả (khác LF/CRLF). Xem `git diff` trước, chỉ `git restore` khi chắc là giả. Dữ liệu `data/raw/labor/` là LF; code không được giả định `\r\n`.
- Không nới quy tắc để bắt thêm ca. Dạng spec không nói thì báo lỗi dừng (fail-closed, thoát mã 1, không ghi file), không đoán.
- Mỗi chỗ spec im lặng hoặc lệch spec phải có dòng trong `docs/quyet_dinh/a4_quyet_dinh.txt` hoặc `docs/quyet_dinh/a6_a7_quyet_dinh.txt`.
- Báo cáo cho thầy: viết lại cho v2 ở `report/tong_hop/` (md), rồi `python -X utf8 -I utils/render_report.py` để sinh HTML (tiêu đề và đường dẫn mặc định của script còn của v1, sửa khi cần). **Không sửa HTML bằng tay.** Số liệu trong báo cáo phải đối chiếu với code và đĩa, không chép từ báo cáo cũ. Lời khuyên nội bộ không gửi nguyên bản cho thầy.

## 4. Tầng LLM

- Hiện `src/a4_llm.py` là nơi duy nhất gọi API. Theo plan L0 sẽ thêm `src/llm_client.py` dùng chung (user đã chốt tên): đọc `docs/llm_config.md`, lưu phản hồi thô vào `data/llm_cache/`, đếm lượt theo ngày, chạm hạn mức thì dừng gọn. Khi làm xong thì sửa mục này.
- Đề xuất của LLM không được áp thẳng: máy dựng lại thành câu chuẩn, parse bằng văn phạm chuẩn và kiểm V1-V3; không qua kiểm thì bị loại. Đổi nhà cung cấp hay model không được làm lỏng các kiểm tra này. Vai trò LLM (thầy xác định): đọc hiểu và đề xuất ngữ nghĩa, nên không cần model mạnh; mọi đề xuất đi qua cổng tự động (plan L7).
- Cờ của A4: `--llm off|replay|live`, `--provider claude|gemini`, `--model`. Mặc định `off`/`claude`. `replay` không gọi mạng; `live` mới gọi. **Không chạy `--llm live` khi user chưa bảo** (tốn hạn mức). Cache v1 của A4 nằm ở `archive/v1_thua_ke/data/llm_cache/`.
- Dùng Gemini (khoá miễn phí Google AI Studio, biến môi trường `GEMINI_API_KEY`; đã chạy live 04/11 với `gemini-3.6-flash`). Claude API vẫn vướng thanh toán. Gói miễn phí có thể bị Google dùng nội dung để cải thiện sản phẩm: chỉ gửi văn bản luật công khai.

## 5. Việc đang dở (user cập nhật tay)

- Nhánh `v2-lao-dong` (tách từ `refactor` tại `25c65e6`). Đã dọn v1 vào `archive/v1_thua_ke/`, nạp `data/raw/labor/`, đặt plan chuẩn ở `plan/ke_hoach/`. **Chưa bắt đầu L0.**
- Không có hạn cứng "12/2026". Ưu tiên làm từng bước, duyệt kỹ, không đốt cháy giai đoạn.
- Đã chốt 07/11: `docs/llm_config.md` (model nhẹ: chính `gemini-3.5-flash-lite`, kiểm độc lập `gemini-3.8-flash`); `KhaoSat` đặt bản cắt; heldout đã xoá khỏi repo; thư mục staging `NEW_UPDATE/` đã dọn.
- **Còn sót v1 có chủ đích, dọn dần theo từng bước L (quy tắc 10):** tên và hằng BLDS trong `src/`, `tests/` (kể cả `eval_gold.py`, `eval_ext_amend.py` và test của chúng, vốn gắn dữ liệu v1) và `utils/` (xử lý ở L0); ví dụ v1 trong `docs/quyet_dinh/a4_*`, `a6_a7_*`, `docs/ref/KetQua_*`, `report/ky_thuat/`, `report/review/`.
- **Phát hiện chờ quyết trước L6:** giữa BLLĐ gốc và VBHN_125 còn 8 Điều khác sau chuẩn hoá thô (Điều 42 mất đánh dấu điểm, viết hoa, dính chữ, gạch ngang, khoảng trắng sau `“`, đuôi Điều 220, cộng Điều 154 và 185); quy tắc chuẩn hoá của plan L6 chưa bao hết. Chi tiết ở `docs/ref/KhaoSat_BLLD_ToanVan_2026-11-05.md` (khối bổ sung).
- Việc treo theo plan (mục 8): Phụ lục I.7 của NQ 66.16/2026; văn bản ngoài kho (NĐ 38/2022, NĐ 35/2022, TT 54/2015, BLLĐ 2012, Luật 64/2025); luật sửa đổi BLLĐ đang ở kỳ họp Quốc hội.
