# Tiến độ (đọc sau README.md)

Cập nhật lần cuối: **14/11/2026**, chiều (người dùng nói "tạm dừng, commit lên, t sẽ check sau"; commit và push cùng lượt).

## Đọc theo thứ tự
1. `README.md` (điểm vào, có mục "Việc của phiên này").
2. `.claude/CLAUDE.md` (tự nạp). Tên bước L-số trong bảng mục 2 là tên **cũ**; quy tắc 11 là cách làm việc với người dùng.
3. File này.
4. `docs/pipeline_moi.md`: thiết kế pipeline, cách làm từng bước, ví dụ dữ liệu thật, giải thích field, mẫu "thẻ bước" và thẻ mẫu 1.3.
5. `docs/quyet_dinh/pipeline_moi_quyet_dinh.txt`: quyết định đã chốt (mục A, A1 đến A37; đọc kỹ A36 và A37) và số đo, quan sát (mục B, B1 đến B11).
6. `docs/kiem_hieu.md` và `docs/kiem_hieu_dap_an.md`: bộ kiểm hiểu 1.1 đến 1.6 (10 câu mỗi bước, tổng 60 câu; đáp án ý chính chỉ dành cho agent chấm). **Đang TẠM DỪNG** theo yêu cầu người dùng đến khi chốt xong 1.6.
6b. `docs/the_buoc_1_1_den_1_5.md`: thẻ bước 1.1 đến 1.5 với số đo và bảng phát hiện (viết 12/11).
7. Khi cần: `docs/tien_do_L0_L6.md` (lịch sử code cũ), `docs/quyet_dinh/l*_quyet_dinh.txt` (quyết định của code cũ), `plan/ke_hoach/` (plan tham khảo, không sửa), `plan/ke_hoach/method_vi_3_1_den_3_6_2026-11-09.md` (bản Method của luận, nguồn của mô hình K).

## Câu mở phiên và câu kết phiên (người dùng copy-paste)
- **Trước khi mở:** `git pull` trên nhánh `v3_refactor`.
- **Mở phiên:** "Đọc README.md và làm theo mục 'Việc của phiên này'."
- **Kết phiên:** "Tạm dừng." (agent làm đúng mục "Khi người dùng nói tạm dừng" bên dưới).

## Trạng thái hiện tại
- Nhánh `v3_refactor`. Mốc cũ `d83a4d4` là code L0-L6 trước refactor.
- **Bước 1.1 đến 1.5 xong. Bước 1.6 giai đoạn A (gạch cụm, `src/concepts.py`) XONG 204/204 lô ngày 14/11**: phần LLM chạy bằng phiên Claude Code (Opus 5.5, lời nhắc `concepts-2`), không gọi API (A36). Kết quả: 881 đơn vị, 3069 cụm LLM (bảng cụm 3061 hàng sau khử trùng, thêm 40 cụm từ nút điều kiện), 0 cụm hỏng cổng nguyên văn, 868/881 đơn vị có cụm. Bản ghi ở `data/llm_cache/concepts_spans/` (618 file; còn bản ghi cũ của Sonnet, Haiku và concepts-1 không dùng nữa). `replay` đọc đủ 204/204. Phần sót đo trên 204 lô (A36): 13/881 đơn vị rỗng (D205.K1-3, D73.K2.c, D47.K4 và 7 câu dẫn); 11/87 lô ngoài mốc 0,7-1,6 (không nới mốc, không chạy lại lô nào).
- Lời nhắc 1.6A cuối cùng là `concepts-2`; `concepts-3` thử trên 21 lô rồi rút (làm Opus lặp `ket_luan` của câu dẫn vào cả 8 khoản D67). Kế hoạch chuyển Haiku qua API của 13/11 đã bỏ.
- **Cách làm 1.6B (đặt tên, tái dùng vị từ) ĐÃ VIẾT, CHƯA CODE** (14/11, A37): `docs/pipeline_moi.md` thẻ 1.6 mục 4 bước 5 đến 10, mục 4b (cách chạy bằng Claude Code) và rủi ro ở mục 7. Tóm tắt: 1833 chữ khác nhau chia khoảng 76 lượt tuần tự theo thứ tự Điều; mỗi chữ kèm ngữ cảnh và tối đa 12 ứng viên; LLM trả `reuse` (chỉ khi cùng nghĩa, cùng `params`) hoặc `new`; chạy bằng phiên Claude Code, model Sonnet 5.5 (vai cấu hình mới `ten`, chưa có trong code; `trich.model` giữ Opus để `replay` 1.6A không vỡ). Nhiều chỗ là agent tự đặt, đánh dấu [THÊM] và chờ người dùng duyệt (danh sách ở A37 (6)).
- Kiểm 14/11 (tạm dừng): `--llm off` rồi `--llm replay`, cả hai 13/13 bước, 8 bộ test, 155 test, `tổng test lỗi: 0`; báo cáo ở `docs/bao_cao_chay/` sinh lần cuối bằng `replay`.
- `src/checks.py` sửa 14/11 (hàm `lead_in_text`; kiểm 1.6 trước đó báo oan cụm chapeau ở khoản vì chưa theo A35) kèm 1 test: do agent làm, người dùng chưa duyệt từng dòng.
- s(CASP) đã cài và chạy được trên máy nhà từ 12/11 (A33); chưa kiểm ở máy công ty (cần từ 1.8).
- Khuôn cạnh chung `{s, p, o, evidence, how, flags}` (riêng 1.5 thêm `rule`). Tên file: `parse`, `refs`, `delegation` (1.3), `links` (2.2), `article_type` (1.4, đã bỏ LLM), `exceptions_explicit`, `exceptions_general`, `concepts` (1.6A), `textutil`. Bản đồ tên cũ sang mới ở `docs/pipeline_moi.md`.
- Chưa làm: 1.6B (code), 1.7, 1.8, 1.9 và giai đoạn 2 (đã có code cũ cho 2.3, 2.4 ở `l6_*.py`; 2.5 đến 2.7 chưa có). Thẻ 1.7 và 1.8 là bản nháp ở `docs/pipeline_moi.md`.
- Mục tiêu người dùng đặt (A11): hết T7 (14/11/2026) có KB đủ lớp, có cơ chế cập nhật và một demo hỏi đáp nhỏ. **Đã trượt**; người dùng chọn làm đủ 1.6B, chưa quyết cắt gì ở 1.7 đến 1.9.

## Nợ (ghi 11/11)
1. **1.2 tầng 2** (xác định đích duy nhất cho 13 ca khoản/điểm trơ trụi, đều ở nghị định, thông tư) hoãn; BLLĐ có 0 ca (B10).
2. **5 ca lỏng của 1.3** chưa ai xác nhận (agent đọc: 4 thật, `D133.K1` nghi không). Không bắt buộc: pipeline không có người duyệt giữa chuỗi.
3. **`src/checks.py`** (bộ kiểm độc lập) chưa rà theo thiết kế mới (1.3 tầng lỏng, 1.4 không LLM, khuôn cạnh).
4. **Đầu vào khai báo của văn bản mới (`manifest.csv`):** cần khai `file`, `nhom`, `so_hieu`, `loai`, `ngay_hieu_luc` (và nên có `ngay_ban_hanh`); `so_dieu_dem_duoc` đề xuất cho tùy chọn nhưng code hiện còn đòi. Chưa sửa code.
5. ~~Thẻ bước 1.1, 1.2, 1.4, 1.5~~ **Đã viết 12/11** cùng thẻ 1.3 ở `docs/the_buoc_1_1_den_1_5.md`; mục cuối file đó gom 4 phát hiện. Ba cái đầu **đã sửa 12/11** (A21 nhãn 1.4, A22 trigger và quy tắc 2 của 1.5, A23 tên chờ đích của 1.2; xem `docs/quyet_dinh/pipeline_moi_quyet_dinh.txt`; 119 test xanh). Còn MỞ: file triples NQ_66 biến mất một lần (không tái hiện); 64 ca "trừ <danh từ>" ở kho (BLLĐ 5) chưa có quy tắc nào (cần user quyết trước khi bàn 1.7/1.8); nút điều kiện dài 724 ký tự của `ND_28-2020.D11.K1` do quy tắc chung "đến hết đoạn".
6. **Cổng phần dư của `refs.py`** (từ khoá điều/khoản/điểm ngoài cụm) mới chỉ ghi báo cáo (đo: 0 sót); khi nạp văn bản mới ở giai đoạn 2 nên quyết có biến thành lỗi dừng không.
7. **Cạnh của L6** (`version_edges.jsonl`, bước 2.3 và 2.4) chưa theo khuôn cạnh chung: làm ở giai đoạn 2.
8. **Tài liệu lỗi thời:** bảng vai trò ở `docs/llm_config.md` còn ghi L4 dùng LLM; cache cũ `data/llm_cache/l4_classify/` không còn dùng (chưa xoá, cần người dùng bảo).
9. **Câu hỏi thiết kế còn mở** ở cuối mục "Câu hỏi thiết kế đang mở" của `docs/pipeline_moi.md` (câu 2 đến 8; câu 1 đã giải quyết bởi A14).
10. **Mở rộng ngoại lệ chung 1.5 sang "trừ <danh từ>"** (trừ hành vi, hình thức, các, những ...; 64 ca trong kho, BLLĐ 5 ca): user đã đồng ý làm, hoãn sau 1.6 (A24). Cần đo độ chính xác trên mẫu đọc tay khi làm.
11. **Nút điều kiện quá dài của ngoại lệ chung** ("đến hết đoạn", ví dụ `ND_28-2020.D11.K1` 724 ký tự): ghi nợ, hướng cắt ở dấu ";" (A24).
12. **Kiểm dữ kiện thô của 1.6** (R2 của plan): phần ngữ nghĩa không có cách kiểm bằng máy, bỏ (A26). Phần máy làm được dời sang bộ quét lỗi của 1.8: vị từ là kết luận của một quy tắc thì không được là `input`; mỗi `input` phải được ít nhất một quy tắc dùng. Chưa bàn 1.8 nên đây mới là việc mang sang. Phần còn lại chỉ đo được qua câu hỏi thử ở 1.9, không thành cổng.
13. **`narrower_than`** (quan hệ hẹp hơn giữa hai vị từ gần nghĩa; A27 (2), A29 cấp 3): hoãn khỏi 1.6 và 1.7 (A32). Làm sau khi chạy một vòng KB đầy đủ, dựa trên kết quả phân tích (đếm cặp vị từ gần nghĩa, đếm ngoại lệ bị sót). Cái mất khi hoãn: chưa có tri thức quan hệ ngầm giữa vị từ gần nghĩa.

14. **1.6A, chất lượng cụm (A35):** mẫu đọc tay 88% chấp nhận được, một người đọc, không phải đáp án chuẩn. Vấn đề chính: mục liệt kê "phải có các nội dung sau" và "hành vi bị cấm" bị gán `ket_luan` (vai nhập nhằng); `ket_luan` phủ 843/881 đơn vị nên `kind` khó phân biệt; vai gắn theo đơn vị chứ không theo từng quy tắc; 12% cụm dài từ 25 từ trở lên. Hai đơn vị định nghĩa D107.K1 và D63.K1 bị bỏ trống. Chỉnh bằng lời nhắc sau khi quyết Haiku (nâng PROMPT_VERSION).
15. ~~**Lời nhắc 1.6A còn câu "(chỉ có khi đơn vị là điểm)" cho `khoan_cha`**, không còn đúng cho 46 khoản (A35); cố ý chưa sửa để so Haiku–Sonnet sạch.~~ **Đã sửa ở `concepts-2` (13/11, A36).**
16. **Số liệu LLM chưa đối chiếu Console:** $2,61 (1.6A bản Sonnet qua API, 13/11) tính từ token ghi trong cache. Từ 14/11 phần LLM chạy bằng phiên Claude Code nên không còn số tiền theo lượt.
17. **Phần sót của 1.6A (A36, đo 14/11):** D205.K1-3 rỗng; D73.K2.c và D47.K4 rỗng; câu dẫn D185.K3 và D201.K2 không còn chữ trong sổ cụm; 11/87 lô ngoài mốc (e) (9 vượt, 2 dưới). Không sửa lời nhắc nữa (luật dừng đã hết lượt) trừ khi người dùng nêu lý do mới.
18. **Cụm lặp từ câu dẫn làm neo (anchors) dư:** ít nhất 140/1286 cụm `ket_luan` là chữ lặp từ câu dẫn; ảnh hưởng tới `kind`, `anchors` ở 1.6B chưa đo.
19. **Bản ghi mồ côi trong cache:** 2 bản ghi concepts-1 của lô 1-2 (thử nghiệm) và các bản ghi Sonnet, Haiku cũ ở `data/llm_cache/concepts_spans/` (không còn được `replay` đọc). Chờ người dùng quyết xoá hay giữ.
20. **Mã gọi API của vai `trich` còn trong `llm_client.py` và `concepts.py` nhưng không dùng** (A36, cố ý giữ). Quy tắc 6 của CLAUDE.md nói không để code chết: cần người dùng nói giữ hay bỏ.
21. **`docs/llm_config.md`:** phần chữ về Sonnet, Haiku và "chuyển Haiku" đã lạc hậu; cần ghi lại model thật của từng bước và thêm vai `ten` khi code 1.6B.
22. **Mốc test trong `CLAUDE.md`** ghi 154, thực tế 155 (file của người dùng, agent không sửa).

## Kiểm hiểu (người dùng bảo "khá hay, lưu lại" 11/11)
**TẠM DỪNG từ 12/11 theo yêu cầu người dùng; kiểm lại (1.1 và 1.6, rồi các bước khác) sau khi chốt xong 1.6. Agent không hỏi câu kiểm hiểu nào cho tới khi người dùng bảo.**
Bộ 50 câu (10 câu mỗi bước 1.1 đến 1.5) ở `docs/kiem_hieu.md`; ý chính đáp án cho agent ở `docs/kiem_hieu_dap_an.md`. Kết quả: 1.1 đã kiểm 12/11 (1/10 đúng, chưa đạt, cần học lại rồi kiểm lại); 1.6 kiểm lượt đầu 12/11 (2/10 đúng, 3 thiếu, 3 chưa biết, 2 chưa kiểm vì user mất câu hỏi 1.6.9 và 1.6.10; chưa đạt); 1.2 đến 1.5 vẫn "chưa trả lời" (40 câu). Người dùng nói "kiểm 1.x" thì agent hỏi 10 câu của bước đó, chấm đúng/thiếu/sai, giải thích chỗ sai, rồi ghi kết quả và "mức nắm" (ngưỡng đề xuất: 8 trên 10 là đã nắm) vào bảng.

## Việc kế tiếp (theo thứ tự)
1. **Người dùng tự đọc lại** cách làm 1.6B (thẻ 1.6 mục 4 bước 5 đến 10, 4b, mục 7; A37) và duyệt hoặc đổi các mục [THÊM]. Agent KHÔNG code 1.6B trước khi người dùng nói đã check.
2. **Code 1.6B** (khi được bảo). Việc đầu tiên không gọi LLM: đếm chữ còn ít nhất một ứng viên (luật dừng đề xuất: hơn 20% chữ không có ứng viên thì dừng và báo). Rồi `src/concepts_names.py` (dựng chữ, hàng xóm, lượt, cổng, sổ, `replay`, `--nhap`), vai cấu hình `ten` ở `llm_client.py` và `docs/llm_config.md`, test bằng LLM giả, bản `xuat` dựng thư mục làm việc (có `HUONG_DAN.md`, `tiep.py`). Người dùng chạy khoảng 76 lượt tuần tự bằng phiên Claude Code (Sonnet 5.5); agent nhập và đọc mẫu đọc tay.
3. **1.7 và 1.8:** sau khi có số cặp thật của 1.6B; thẻ 1.8 còn (a) đến (e) chờ người dùng trả lời. Quy trình thẻ: kể lại bước, advisor soát, nhờ quyết.
4. Kiểm hiểu: **tạm dừng**; người dùng nói "kiểm 1.x" thì hỏi 10 câu của bước đó (`docs/kiem_hieu.md`), chấm theo `docs/kiem_hieu_dap_an.md`. Câu hỏi 1.6 đã cũ so với thiết kế mới, cần viết lại khi kiểm.
5. Khi rảnh: rà `checks.py` (cả phần sửa 14/11); thẻ 1.7, 1.8 bản cuối; nợ ở mục "Nợ".

## Chờ người dùng
- **Duyệt hoặc đổi các mục [THÊM] của 1.6B** (A37 (6)): cỡ lượt 30, 12 ứng viên, cách tính hàng xóm, đặt tên cho 25 hàng ngoại lệ không có targets, cho `reuse` tên `new` cùng lượt, cách thử lại, `tiep.py` chạy mã repo trong thư mục làm việc, dừng sớm, mẫu đọc tay và ngưỡng, luật dừng 20%.
- Trả lời (a) đến (e) của thẻ 1.8 (B11) và có cắt 1.7 hay không (quyết sau khi có số cặp thật).
- Quyết 2 bản ghi mồ côi concepts-1 và các bản ghi Sonnet, Haiku cũ trong cache; quyết giữ hay bỏ mã gọi API của vai `trich` (nợ 19, 20).
- Duyệt từng dòng sửa `src/checks.py` (`lead_in_text`) và test mới.
- Sửa tay `.claude/CLAUDE.md`: mốc test 154 thành 155; mục 4 còn ghi vai `trich` là Sonnet qua API; mục 5 còn trỏ tài liệu cũ (file của người dùng, agent không sửa).
- Luận văn: model của từng bước (1.6A Opus 5.5 qua phiên Claude Code, không API; 1.6B dự định Sonnet 5.5) khác chốt "model nhẹ, miễn phí" 07/11, cần ghi lý do; Method 3.5 còn mô tả "model khác trích lại để kiểm" mà hệ thống không làm (A25).
- Kiểm s(CASP) ở máy công ty khi tới 1.8 (`swipl --version`, nạp được `library(scasp)`).
- Xoá cache cũ `data/llm_cache/l4_classify/` (nợ 8) khi người dùng bảo.

## Khi người dùng nói "tạm dừng" (quy trình cho agent)
1. Dừng việc đang làm, không bắt đầu bước mới.
2. Chạy kiểm: `python -I src/run_all.py --viewer --tests` (chế độ `off`), rồi `python -I src/run_all.py --llm replay --viewer --tests` (lần cuối bằng `replay` để báo cáo ở `docs/bao_cao_chay/` sinh lại đúng). Ghi kết quả thật (đỏ cũng ghi, kèm đầu ra lỗi).
3. Cập nhật file này (ghi đè "Trạng thái hiện tại", "Nợ", "Việc kế tiếp", "Chờ người dùng"; thêm một mục vào "Nhật ký", mới nhất ở trên), mục "Việc của phiên này" của `README.md`, và bảng kết quả ở `docs/kiem_hieu.md` nếu có câu mới được trả lời.
4. Nếu bước nào đổi thì sửa `docs/pipeline_moi.md`; quyết định mới hoặc chỗ lệch plan thì thêm vào `docs/quyet_dinh/pipeline_moi_quyet_dinh.txt`.
5. `git status`, soát file đổi: không đưa khoá API, heldout, file lớn ngoài ý muốn; `data/processed/` đã bị `.gitignore`; không đưa thay đổi cục bộ của người dùng (ví dụ `.vscode/settings.json`) nếu họ chưa bảo. `git add` cả file mới. Thông điệp commit tiếng Việt, **ngắn**. Rồi **commit và push luôn** lên nhánh đang làm, không `--force`. Nếu kiểm ở bước 2 đỏ thì ghi "đỏ" vào "Trạng thái hiện tại", vẫn commit và push, và báo người dùng. Nếu công cụ từ chối commit hoặc push thì đưa lệnh cho người dùng tự chạy.
6. Sau commit: kiểm cây đã commit chạy được độc lập (giải nén `git archive HEAD` vào thư mục trống, chạy `run_all.py --viewer --tests` ở đó).
7. Không ghi vào repo: khoá API, nội dung hay đường dẫn của heldout, thông tin cá nhân của người dùng.

## Cách làm việc với người dùng (tóm từ CLAUDE.md)
- Mục tiêu: người dùng **làm chủ** luận, trả lời được "vì sao bước này làm vậy mà không phải kiểu kia". Agent đề xuất, người dùng quyết. Không "làm dùm".
- Thảo luận thiết kế trước, code sau, một lớp mỗi lượt. Trước khi nhờ quyết, kể lại bước bằng "thẻ bước" (dữ liệu vào, dữ liệu ra, bảng field đủ giá trị, cách làm, vì sao, kiểm), rồi hỏi kiểm hiểu. Nói bằng tên bước mới, không dùng L-số.
- Mơ hồ thì hỏi (gom một lượt). Báo cáo ngắn, tiếng Việt, có mục "Phản biện", nói rõ cái gì đã chạy và cái gì chưa kiểm. Khi đổi một field, chạy cả `--llm off` lẫn `replay` (S3 từng hỏng nhánh `off` mà không ai thấy).
- Không commit, push, xoá, ghi đè, chạy `--llm live` khi chưa được bảo (trừ lệnh "tạm dừng").

## Dựng lại trên máy mới
- `git clone https://github.com/MrSooo/KLTN.git kltn`, rồi `git switch v3_refactor`. Trên máy cũ remote tên `KLTN`, clone mới gọi nó là `origin`.
- Python từ 3.10 (máy nhà 3.14.x), chỉ dùng thư viện chuẩn. `python -I src/run_all.py --viewer --tests` (khoảng 15 giây) dựng lại `data/processed/` và kiểm; phải ra `XONG: 13/13 bước`.
- Chỉ khi chạy LLM thật (`--llm live`): `.venv` có `google-genai` và `anthropic`, biến môi trường `GEMINI_API_KEY` (2.2) và `ANTHROPIC_API_KEY` (1.6 trở đi, A34) đặt riêng trên từng máy. Chi tiết ở `docs/ban_giao_2026-11-07.md` mục 1 và 2.
- s(CASP): người dùng nói đã cài ở máy chính; kiểm trên từng máy bằng `scasp --version`. Cần cho bước 1.8 và 1.9.
- Mốc đối chiếu cũ (đầu ra của code `d83a4d4` ở chế độ `replay`) không nằm trong git; dựng lại bằng `git worktree add <thư mục> d83a4d4` rồi `python -I src/run_all.py --llm replay --viewer` ở đó.
- Heldout giữ ngoài repo, không mở khi chưa tới lúc đo.
- Memory của Claude nằm trên từng máy và không đi theo git; mọi thứ cần nhớ phải nằm trong README, file này, `docs/pipeline_moi.md` và `docs/quyet_dinh/`.

## Nhật ký (mới nhất ở trên)

### 14/11/2026: 1.6A xong 204/204 bằng Claude Code; viết cách làm 1.6B (chưa code)
- Phần LLM của 1.6A chạy bằng phiên Claude Code theo A36 ("không call API nữa"): mỗi lô một subagent mới (Opus 5.5) trong thư mục tách riêng ngoài repo; agent nhập bản ghi vào cache bằng script ở thư mục tạm (không vào repo), kiểm cổng nguyên văn rồi chạy `replay`.
- Lời nhắc: `concepts-2` (thêm quy tắc 6 cho định nghĩa "X là Y"). Thử `concepts-3` trên 21 lô: cứu D205.K1-3 nhưng làm Opus lặp `ket_luan` của câu dẫn vào cả 8 khoản D67; theo tiêu chí viết trước, lùi về `concepts-2` (A36). Đính chính: đoạn "lô 52 và 192 kéo ngược chiều" của bản 13/11 là sai.
- Lỗi tìm ra khi nhập: `checks.py` chưa theo A35 (khoản nhận chữ Điều làm chapeau), `run_all --llm replay` thoát mã 1; sửa bằng `lead_in_text` và một test (155 test).
- Nhập 203 lô, rồi làm lại riêng lô 085 vì thiếu dòng nhật ký model; 204/204. Đo phần sót trên cả 204 lô và ghi vào A36.
- Commit `8522ee3`. Sai sót của agent: lúc commit, báo cáo `concepts` đang ở chế độ `off` (chạy `off` sau `replay`); sửa ở commit tạm dừng này.
- Bàn 1.6B (A37): người dùng chốt làm đủ 1.6B, chạy bằng Claude Code, Sonnet, đặt tên theo thứ tự Điều kèm ngữ cảnh, `reuse` chỉ khi cùng nghĩa, không thử từng lượt. Người dùng hỏi sao không gộp gạch cụm và đặt tên làm một bước; agent giữ hai bước (cùng chữ cùng tên do máy bảo đảm; ứng viên cần biết chữ trước; giai đoạn A đã đóng băng nên chạy lại B không vỡ cache) và nhận hai ý đúng của người dùng (ngữ cảnh, thứ tự Điều).
- Viết cách làm 1.6B v6 vào thẻ 1.6. Advisor soát: sửa ví dụ D14.K2 và D24.K3 (ban đầu ghi ngược chiều, chưa kiểm), đánh dấu thêm các mục [THÊM], bổ sung quy tắc phụ thuộc giữa chữ trong một lượt và thứ tự Điều. Đo trước không gọi LLM: sau lọc `params` có 101/1833 chữ không còn ứng viên, trung vị 17 ứng viên, 1051 chữ có hơn 12.
- Đã kiểm trước commit: `--llm off` rồi `--llm replay`, cả hai 13/13 bước, 8 bộ test, 155 test, `tổng test lỗi: 0`. Chưa kiểm: Sonnet ở việc đặt tên; chất lượng cụm do Opus gạch (chỉ có số đo hình dạng, chưa có mẫu đọc tay); tác động của cụm lặp câu dẫn lên 1.6B.

### 13/11/2026: 1.6A chạy live xong; đọc kết quả; hai sửa; chuyển Haiku (chưa chạy); thêm vai `trich`
- Đêm 12 rạng 13/11: thêm vai LLM `trich` (Claude Sonnet 5.5) vì Gemini quá tải (A34); khoá cache chứa tên model nên không đổi `chinh` (sẽ vỡ replay của 2.2). Người dùng chạy 1.6A live: 204/204 lô, $2,61 (ước tính ban đầu $1-2 là thấp).
- Đọc kết quả (A35): cổng nguyên văn 0 cụm bị loại là THẬT (kiểm độc lập); quy tắc 2 của lời nhắc không làm trống đối tượng áp dụng; mẫu đọc tay 74/84 chấp nhận được (88%, một người đọc); `ket_luan` phủ 843/881 đơn vị.
- Tìm hai lỗi và sửa có test (A35): khoản dưới Điều có câu dẫn thiếu ngữ cảnh (46 khoản, 10 Điều, 39% không ra chủ thể); ngoại lệ ghi hai lần (11 đơn vị). 10 lô đổi khoá cache.
- Người dùng đồng ý chuyển sang Haiku 5.5 (rẻ khoảng 20 lần). Hệ quả: một khoá `trich.model` cho cả vai nên 1.6A chạy lại bằng Haiku (khoảng $0,13); cấu hình đang commit vẫn Sonnet; thêm khoá `trich.thinking` vì Haiku không nhận `between_tools`. Haiku chưa từng gọi thật.
- Ghi vào B11 các số đo và thử s(CASP) cho thẻ 1.8 (trước đó chỉ nằm trong chat): cấu trúc 66 cạnh, ngoại lệ lồng ba tầng chạy đúng trên ví dụ nhỏ, vị từ không định nghĩa chỉ cảnh báo, biến không khớp cho kết quả sai âm thầm.
- Đã kiểm trước commit: `--llm off` và `--llm replay` đều 13/13 bước, 8 bộ test, 154 test, `tổng test lỗi: 0`. Chưa kiểm: Haiku với API thật; s(CASP) ở máy công ty; đối chiếu $2,61 với Console.
- Trượt mục tiêu T7 (A11): 1.7 không kịp (cần 1.6B). Chờ người dùng quyết cắt gì.

### 12/11/2026: sửa 3 lỗi 1.2, 1.4, 1.5; bàn 1.6 (chưa code); kiểm hiểu 1.1 và 1.6
- Viết thẻ 1.1 đến 1.5 (`docs/the_buoc_1_1_den_1_5.md`). Sửa 3 lỗi tìm ra khi đo: A21 (nhãn 1.4: 6 Điều BLLĐ bị xếp nhầm `effect_transition`/`authority`), A22 (1.5: 23 cạnh tường minh giả từ "khấu trừ", "loại trừ"), A23 (1.2: tên luật chờ đích bị cắt, ví dụ "Luật Bảo" thành "Luật Bảo hiểm xã hội"). Mỗi lỗi có test, có so đầu ra trước/sau; 113 thành 119 test.
- Chốt nguyên tắc: LLM không được LLM khác kiểm, phải có kiểm bằng máy (A25); bỏ cổng model thứ hai khỏi 1.6 (lệch plan L7 và Method 3.5). Ghi nợ mở rộng ngoại lệ chung sang "trừ <danh từ>" (A24, nợ #10, #11).
- Bàn 1.6: viết thẻ (bản bàn) ở `docs/pipeline_moi.md`. Đã chốt (A26): ngữ cảnh = tiêu đề Điều + chapeau + chữ đơn vị; bỏ kiểm dữ kiện thô (nợ #12, phần máy làm được dời sang bộ quét lỗi của 1.8). Đang mở: cách gộp tên đồng nghĩa.
- Kiểm hiểu: 1.1 được 1/10, 1.6 được 2/10 (cả hai chưa đạt); người dùng tạm dừng kiểm hiểu đến khi chốt xong 1.6.
- Thêm quy tắc 12 vào `CLAUDE.md`: không chiều ý người dùng (phản biện cả ý kiến của họ). Người dùng đòi sau khi thấy agent gật quá nhanh; hai lỗi suy luận của agent đã được nhận và ghi ở A26 (lập luận bất đối xứng "tách nhầm thì lộ" sai một nửa; phương án (d) chỉ là G5 đổi tên).
- Lỗi mở: một lần chạy đầu ngày thiếu `l1_triples_NQ_66-16-2026.jsonl` (17/18) nhưng báo 12/12; không tái hiện; cổng xanh chưa kiểm đủ 18 file triples (nợ #5).
- Đã kiểm trước commit: `--llm off` và `--llm replay` đều 12/12, 119 test, `tổng test lỗi: 0`, đủ 18 file triples. Chưa kiểm: s(CASP) (máy này có `swipl` 10.0.2 nhưng không có `scasp`); Python máy này là 3.13.5 (tài liệu ghi 3.14.x), vẫn xanh. Chưa chạy `--llm live` (không có khoá trong môi trường agent).

### 11/11/2026: code xong 1.1 đến 1.5, chốt cách báo cáo
- Người dùng đặt mục tiêu hết T7 và đổi nhịp làm việc: mỗi lượt một lớp; mỗi bước phải được kể lại (dữ liệu vào, ra, field, vì sao) trước khi nhờ quyết.
- Code: S1 đổi tên 5 file và dời `text_norm` sang `textutil.py` (đầu ra giống hệt mốc, 301 file); S2 bỏ LLM khỏi 1.4 (A14; 93 trên 921 nhãn đổi, 39 `effect_transition` không đổi); S3 khuôn cạnh chung (A12); S4 tách `l3_links.py` thành `delegation.py` (1.3, có tầng lỏng `loose`) và `links.py` (2.2); bỏ `version` và `heading` (A16).
- Lỗi tự gây, đã sửa: S3 để nhánh `--llm off` đọc field `check` đã bỏ (KeyError, lệnh dựng lại mặc định hỏng) mà chỉ kiểm bằng `replay`. Từ đó chạy cả hai chế độ mỗi lần.
- Phát hiện: cổng phần dư của 1.2 đã có sẵn trong code cũ (0 sót); tầng 2 hoãn (B10); 4 ca điều khoản giao bị regex chặt bỏ sót vì dấu gạch ngang trong "Bộ Lao động - Thương binh và Xã hội".
- Cách báo cáo: mẫu "thẻ bước" v2 (người dùng duyệt), bộ 50 câu kiểm hiểu (10 mỗi bước), `README.md` làm điểm vào cho máy khác.
- Đã kiểm trước commit: bản sao sạch các file `git add` sẽ lấy chạy xanh 12/12 ở `--llm off` và `replay`; đầu ra `replay` giống hệt cây làm việc.
- Chưa kiểm: `checks.py` theo thiết kế mới; s(CASP) (agent chưa thấy trong PATH).

### 10/11/2026: chốt hướng refactor, chưa code
- Chốt pipeline hai giai đoạn, đánh số giai đoạn.bước, bỏ L-số. Tạo `docs/tien_do.md`, `docs/pipeline_moi.md`, `docs/quyet_dinh/pipeline_moi_quyet_dinh.txt`. Chi tiết ở A1 đến A10.
