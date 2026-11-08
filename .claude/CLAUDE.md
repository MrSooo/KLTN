# CLAUDE.md — luật làm việc trong dự án kltn

## 1. Cách làm việc (đọc trước, quan trọng nhất)

Mục tiêu của user là **hiểu và kiểm soát được mình đang làm gì**. Claude viết code, user duyệt từng bước. Vì vậy:

1. **Từng bước nhỏ, không làm một mạch.** Mỗi lượt chỉ làm MỘT bước. Trước khi sửa: nói ngắn sẽ sửa file nào, vì sao. Sau khi sửa: dừng, tóm tắt, chờ user xem. Không tự nối sang bước kế tiếp, không chạy chuỗi lệnh dài mà chưa báo.
2. **Plan do user đưa là tham khảo chính** (lập cùng agent web). Làm theo thứ tự plan, nhưng chỗ plan mâu thuẫn với code, dữ liệu hoặc quyết định đã chốt thì **theo source**: nêu ra, hỏi nếu chưa rõ, và ghi chỗ lệch vào `docs/quyet_dinh/`. Không thêm việc ngoài plan, không "tiện tay" refactor, không tự sửa nội dung plan.
3. **Gặp điểm mơ hồ thì HỎI, không đoán** (định dạng output, tên cột, hướng cạnh, vị trí file, giá trị rỗng, thứ tự ghi...). Gom nhiều câu hỏi vào một lượt. Chỉ khi prompt nhiệm vụ ghi rõ "không hỏi lại" thì mới tự chọn cách đơn giản nhất, và phải ghi mọi lựa chọn vào file `docs/quyet_dinh/*_quyet_dinh.txt`, chỗ lệch spec đặt lên đầu.
4. **Không làm việc khó đảo ngược khi chưa được bảo:** commit, push, xoá hoặc ghi đè file, chạy `--llm live` (tốn hạn mức hoặc tiền), cài gói vào repo. Trước khi ghi đè thì xem file đích.
5. **Báo cáo trung thực, giải thích để user hiểu.** Tiếng Việt, ngắn. Nói rõ cái gì đã chạy và kết quả, cái gì CHƯA kiểm. Không nói "xong" khi chưa chạy test. Test lỗi thì dán đầu ra lỗi. Khi đổi hành vi, nói đổi gì và ảnh hưởng chỗ nào, không chỉ liệt kê tên file.
6. **Code phải đọc được để user duyệt:** thay đổi nhỏ, tách theo việc, docstring và comment tiếng Việt giải thích *vì sao* (không chép lại code). Không để lại code chết hay cờ thừa.
7. **Bí mật:** API key chỉ nằm trong biến môi trường (`GEMINI_API_KEY`, `ANTHROPIC_API_KEY`). Không bao giờ dán vào chat, file trong repo, test hay báo cáo.
8. **Phản biện (critical review) là bắt buộc, trước khi làm và trước khi báo xong.** Với mỗi bước tự hỏi: plan/spec có mâu thuẫn với code hoặc dữ liệu thật không; giả định nào mình chưa kiểm; cách làm này có thể sai ở đâu và sai sẽ lan xuống bước nào; con số nào chưa đối chiếu với đĩa. Kết quả phản biện (kể cả "không thấy vấn đề, đã kiểm X và Y") phải có một mục ngắn **"Phản biện"** trong báo cáo cuối lượt, không để chỉ nằm trong đầu. Không đồng tình với plan hoặc với chính cách làm của mình thì nói ra, không im lặng làm theo.
9. **Gặp khó khăn thì DỪNG và HỎI, không tự quyết.** Khó khăn gồm: test lỗi chưa rõ nguyên nhân; lệnh hoặc công cụ không chạy được; plan mâu thuẫn với code hoặc dữ liệu mà source hay quyết định đã chốt chưa phân xử được (đã phân xử rồi thì theo source và ghi `docs/quyet_dinh/`, xem mục 2; chưa có gì phân xử thì vẫn dừng và hỏi); hai cách làm đều hợp lý; phải nới quy tắc, bỏ một kiểm tra, đổi plan/model/tham số mới đi tiếp được. Không tự chọn "cách tạm", không tự đi vòng. Báo lại: đã thử gì, lỗi nguyên văn, các hướng có thể và đề xuất của mình, rồi chờ user. Chế độ "không hỏi lại" ở mục 3 chỉ áp cho chỗ spec im lặng, **không** áp cho khó khăn: gặp khó khăn vẫn dừng và hỏi.
10. **Cây làm việc chỉ có Bộ luật Lao động.** Ngoài `archive/`, không được có dữ liệu, báo cáo, plan, ví dụ hay tên gì thuộc lĩnh vực cũ (thừa kế, BLDS 2015, Điều 609-662). `archive/v1_thua_ke/` chỉ để tham khảo: **không sửa, không chạy, không import, không chép ngược vào cây, không dẫn đường dẫn của nó trong code hay test.** Không cần thì không đụng tới. Thật sự cần (ví dụ viết lại R1-R4 ở L7, xem hành vi cũ của A4 ở L6) thì chỉ mở ra đọc, nói rõ với user là đang mở archive, và viết bản mới cho lao động ở ngoài archive; muốn lấy file ra khỏi archive thì hỏi. File mới tạo không được chứa dữ liệu hay ví dụ v1. Khi một bước L refactor một file code hoặc tài liệu còn ví dụ v1 thì xoá ví dụ v1 khỏi file đó ngay trong bước đó.

## 2. Dự án là gì

Pipeline biến Bộ luật Lao động 45/2019 (bản gốc) và các văn bản dưới luật (nghị định, thông tư, nghị quyết, bản hợp nhất) thành cơ sở tri thức **thích nghi theo ngày hiệu lực**: mỗi văn bản là một sự kiện nạp, tạo phiên bản mới và đóng phiên bản cũ. Đồ án tốt nghiệp. **Plan tham khảo:** `plan/ke_hoach/ke_hoach_kb_laodong_agent_2026-11-06.md` (bước L0-L11, bản cập nhật 8/11; kèm `giai_thich_dung_kb_l1_l11_2026-11-08.md`). Bản v1 (Bộ luật Dân sự 2015 phần 4, thừa kế) đã đóng băng ở commit `25c65e6` và nằm trong `archive/v1_thua_ke/` (xem README ở đó).

Bảng dưới là code **đã viết lại cho Bộ luật Lao động đến hết L6** (09/11/2026); L7-L11 chưa làm. Tên A1-A8 giữ từ v1 cho dễ theo dõi.

| Bước | File | Việc |
|---|---|---|
| L0 | `src/corpus.py`, `src/llm_client.py`, `src/run_all.py` | đọc `manifest.csv`; wrapper LLM có cache và hạn mức (chưa gọi live lần nào); chạy cả chuỗi |
| A1 (L1) | `src/a1_parse.py` | `.txt` → đơn vị (Chương/Mục/Điều/Khoản/Điểm, phụ lục), khối trích dẫn sửa đổi, bảng lương, đầu văn bản |
| A2 (L2) | `src/a2_edges.py` | cạnh `contains`/`part_of`, `refers_to` trong và giữa văn bản, quan hệ chờ đích |
| L3 | `src/l3_links.py` | điều khoản giao chi tiết (dạng A-E), cạnh `based_on`, `details` |
| L4 | `src/l4_classify.py` | nhãn cho từng Điều (substantive, procedural, effect_transition ...) |
| A3 + A6 (L5) | `src/a3_exceptions.py`, `src/a6_general_exceptions.py` | cạnh `exception_of` tường minh và ngoại lệ chung ("trừ trường hợp ...") |
| A4 (L6) | `src/a4_versions.py`, `src/l6_directives.py`, `src/l6_rare.py` | kho phiên bản theo ngày hiệu lực; đọc chỉ thị từ chữ văn bản; các loại hiếm (chỉ kiểm bằng fixture) |
| A5 | `src/a5_checks.py` | kiểm tra độc lập A1-A4, A6, L3, L4 |
| A7 | `src/a7_graph.py` | đồ thị gộp kèm khoảng hiệu lực của từng nút |
| A8 | `utils/a8/` | trang HTML xem đồ thị theo ngày (mở offline), `data/processed/a8/a8_do_thi.html` |

Thư mục: `src/` (mã nguồn + `run_all.py`), `tests/` (mọi `test_*.py`, khung `_harness.py`), `utils/` (A8, `chuan_hoa_van_ban.py`, `render_report.py` dựng Markdown→HTML), `data/` (`raw/labor/{base,dev,manifest.csv}`, `processed/<bước>/` do code tạo, **bị `.gitignore`**: sau khi clone chạy `python -I src/run_all.py --a8` để có lại; `llm_cache/` thì được theo dõi), `docs/`, `plan/`, `archive/v1_thua_ke/` (v1, xem dưới). Đừng dựng lại `.work/` hay `result/` (đã bỏ).

Bố cục tài liệu (tên file chữ thường, `snake_case`; bước mới theo cùng cấu trúc):
- `docs/quyet_dinh/`: quyết định kỹ thuật, viết tay, chỗ lệch plan đặt lên đầu (`l0_l1_`, `l2_l3_l4_l5_`, `l6_a5_a7_a8_quyet_dinh.txt`; bước mới thêm file cùng kiểu). `docs/tien_do_L0_L6.md`: trạng thái và việc còn lại.
- `docs/bao_cao_chay/<bước>/`: báo cáo chữ do code sinh ra mỗi lần chạy, không sửa tay; tạo lại khi chạy `run_all.py`.
- `docs/ref/`: chỉ còn `KhaoSat_BLLD_ToanVan` (bản cắt 07/11, đã bỏ phần liên quan heldout; mục 4 chỉ liệt kê dạng A của điều khoản giao chi tiết, thiếu B, D, E nên cần đối chiếu với `l3_links.py`). `KetQua_A1_A4`, `KetQua_A5` (plan vẫn nhắc tên) đã chuyển sang `archive/v1_thua_ke/docs/ref/` ngày 09/11 vì mô tả code đã viết lại; quy ước nay ở `docs/quyet_dinh/`. `docs/llm_config.md`: model, temperature, ngày khoá (xem mục 4).
- `report/` **không còn** trong cây: `ky_thuat/`, `review/` (mô tả và rà soát code A1-A7 của v1) và `tong_hop/` đều ở `archive/v1_thua_ke/report/`. Báo cáo cho thầy viết lại cho v2 ở `report/tong_hop/` khi tới bước đó (tạo thư mục mới).
- `plan/`: chỉ có `ke_hoach/` (plan tham khảo L0-L11). Không sửa nội dung plan do user đưa; đường dẫn dạng `claude/…` trong đó là của project web. Mọi plan, thiết kế và kiến thức của v1 ở `archive/v1_thua_ke/plan/`: đề cương, kế hoạch cũ, `thiet_ke/` (hướng dẫn R1-R4, định nghĩa bước B-D và bộ quét, sổ quyết định), `kien_thuc/`. Plan mới nhắc "R1-R4", "C1-C4", "bộ quét 5 loại lỗi", "kế hoạch cũ" ở L7-L9: tới các bước đó mới mở archive để đọc (theo quy tắc 10).

Quy ước dữ liệu: id dạng `<doc_id>.D154.K8a.b` (hậu tố chữ như `D2a`, `K8a` là bình thường; Điểm `đ` viết thành `dd` trong id; phụ lục `<doc_id>.PL1.M2.R15`). `doc_id` = tên file trong `data/raw/labor/` (ví dụ `BLLD_45-2019`, `ND_145-2020`). Thông tin văn bản (số hiệu, ngày, số Điều) đọc từ `manifest.csv` (UTF-8 có BOM, đọc bằng `utf-8-sig`), không chép cứng vào code. Mỗi bước đầu ra là đầu vào của bước sau và có số đối chiếu cứng, nên một giả định sai âm thầm sẽ lan xuống các bước sau.

**Heldout:** nhóm văn bản dùng để đo, plan yêu cầu để ngoài repo. **Không mở, không đọc, không ghi vào tài liệu hay memory** bất kỳ nội dung hay đường dẫn nào của nó cho đến khi user bảo bắt đầu đo. Chỉ `data/raw/labor/` (base + dev) được dùng khi dựng. Cột `quan_he` của manifest chỉ là mốc kiểm, không phải đầu vào của pipeline.

## 3. Quy ước kỹ thuật

- **Chỉ dùng thư viện chuẩn của Python.** Ngoại lệ duy nhất: chế độ `--llm live` của A4 cần gói của nhà cung cấp (`anthropic` hoặc `google-genai`), cài trong `.venv` (đã nằm trong `.gitignore`), không cài vào Python hệ thống.
- Chạy script: `python -I src/<file>.py <md>` (cờ `-I` để không nạp nhầm file cạnh script). Windows: Python của venv là `.venv\Scripts\python.exe`.
- Test: `python -I tests/test_aN.py` (dòng cuối phải là `tổng test lỗi: 0`). Chạy cả pipeline: `python -I src/run_all.py`; thêm `--a8` để dựng trang xem, `--tests` để chạy mọi `tests/test_*.py`. **Mốc xanh hiện tại (09/11/2026): `python -I src/run_all.py --a8 --tests` ra 11/11 bước, 6 bộ test (97 test), `tổng test lỗi: 0`.** Báo cáo cho thầy: viết Markdown ở `report/tong_hop/` rồi `python -X utf8 -I utils/render_report.py <md> <html>`. Mốc v1 cũ (287 test / 11 file) ở `archive/v1_thua_ke/README.md` không còn liên quan.
- Máy đang `core.autocrlf=true`: sau khi chạy code, `git status` có thể hiện file M giả (khác LF/CRLF). Xem `git diff` trước, chỉ `git restore` khi chắc là giả. Dữ liệu `data/raw/labor/` là LF; code không được giả định `\r\n`.
- Không nới quy tắc để bắt thêm ca. Dạng spec không nói thì báo lỗi dừng (fail-closed, thoát mã 1, không ghi file), không đoán.
- Mỗi chỗ spec im lặng hoặc lệch spec phải có dòng trong `docs/quyet_dinh/a4_quyet_dinh.txt` hoặc `docs/quyet_dinh/a6_a7_quyet_dinh.txt`.
- Báo cáo cho thầy: viết lại cho v2 ở `report/tong_hop/` (md), rồi `python -X utf8 -I utils/render_report.py` để sinh HTML (tiêu đề và đường dẫn mặc định của script còn của v1, sửa khi cần). **Không sửa HTML bằng tay.** Số liệu trong báo cáo phải đối chiếu với code và đĩa, không chép từ báo cáo cũ. Lời khuyên nội bộ không gửi nguyên bản cho thầy.

## 4. Tầng LLM

- `src/llm_client.py` là nơi duy nhất gọi API (đã viết, kiểm bằng API giả, **chưa gọi live lần nào**): đọc `docs/llm_config.md`, lưu phản hồi thô vào `data/llm_cache/<tác vụ>/`, đếm lượt theo ngày và theo vai (`chinh`/`kiem`) ở `data/llm_cache/_usage.json`, chạm hạn mức thì `QuotaReached`. `src/a4_llm.py` của v1 đã xoá (còn ở git `25c65e6`). Chưa bước nào của L1-L6 gọi nó: chỗ dự kiến dùng LLM (L3 kiểm cạnh `details`, L4 phân loại Điều, L6 chỉ thị lạ) đang chạy bằng regex/từ khoá và ghi cờ `llm_pending` / `llm_check_pending`.
- Đề xuất của LLM không được áp thẳng: máy dựng lại thành câu chuẩn, parse bằng văn phạm chuẩn và kiểm V1-V3; không qua kiểm thì bị loại. Đổi nhà cung cấp hay model không được làm lỏng các kiểm tra này. Vai trò LLM (thầy xác định): đọc hiểu và đề xuất ngữ nghĩa, nên không cần model mạnh; mọi đề xuất đi qua cổng tự động (plan L7).
- Chế độ của `llm_client.Client`: `off|replay|live`. `off` không gọi gì; `replay` chỉ đọc cache (thiếu thì `CacheMiss`); `live` mới gọi mạng. **Không chạy `live` khi user chưa bảo** (tốn hạn mức). Cache v1 của A4 nằm ở `archive/v1_thua_ke/data/llm_cache/` (chỉ đọc, không dùng lại).
- Dùng Gemini (khoá miễn phí Google AI Studio, biến môi trường `GEMINI_API_KEY`; đã chạy live 04/11 với `gemini-3.6-flash`). Claude API vẫn vướng thanh toán. Gói miễn phí có thể bị Google dùng nội dung để cải thiện sản phẩm: chỉ gửi văn bản luật công khai.

## 5. Việc đang dở (user cập nhật tay)

- Nhánh `v2-lao-dong` (tách từ `refactor` tại `25c65e6`). Đã dọn v1 vào `archive/v1_thua_ke/`, nạp `data/raw/labor/`, đặt plan tham khảo ở `plan/ke_hoach/`. **L0-L6 đã làm (09/11/2026, chưa commit)**; chi tiết, số liệu và việc còn lại ở `docs/tien_do_L0_L6.md` và `docs/quyet_dinh/`. Đã có đồ thị xem được: `python -I src/run_all.py --a8`, mở `data/processed/a8/a8_do_thi.html`.
- **Đổi máy / phiên mới không có memory: đọc `docs/ban_giao_2026-11-07.md` trước** (cách dựng lại, thứ không nằm trong git, quyết định đã chốt, việc kế tiếp).
- Không có hạn cứng "12/2026". Ưu tiên làm từng bước, duyệt kỹ, không đốt cháy giai đoạn.
- Đã chốt 07/11: `docs/llm_config.md` (model nhẹ: chính `gemini-3.5-flash-lite`, kiểm độc lập `gemini-3.8-flash`); `KhaoSat` đặt bản cắt; heldout đã xoá khỏi repo; thư mục staging `NEW_UPDATE/` đã dọn.
- **Cây đã sạch v1 (09/11, quy tắc 10):** ngoài `archive/`, chỉ còn chữ "thừa kế" nằm trong chính văn bản luật của kho và vài chỗ nhắc trong plan do user đưa. `utils/render_report.py` là bộ dựng Markdown→HTML dùng chung (đã bỏ tiêu đề BLDS); nội dung báo cáo cho thầy chưa viết.
- **Đã xử lý 09/11:** 8 Điều lệch BLLĐ <-> VBHN_125 (khoá so sánh `text_norm`; Điều 154 khoản 8a là sửa đổi thật; Điều 42, 185, 220 và 87 gắn `consolidation_discrepancy`). Điều 87 là phát hiện mới ngoài danh sách bàn giao. Chi tiết ở `docs/quyet_dinh/l6_a5_a7_a8_quyet_dinh.txt` mục A4.
- Việc treo theo plan (mục 8): văn bản ngoài kho (NĐ 38/2022, NĐ 35/2022, TT 54/2015, BLLĐ 2012, NĐ 189/2025, Luật 64/2025); luật sửa đổi BLLĐ đang ở kỳ họp Quốc hội. Phụ lục I.7 của NQ 66.16 đã có (bản đầy đủ gửi 08/11); Điều 21-23 của ND_145 chưa thấy trong I.7.
- **Chưa làm, cần user:** chạy LLM live (không có `GEMINI_API_KEY` trong shell của Claude), commit (bộ phân loại tự động từ chối lệnh `git commit` của Claude, xem `docs/tien_do_L0_L6.md`).
