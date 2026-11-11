# Tiến độ (đọc sau README.md)

Cập nhật lần cuối: **11/11/2026**, cuối ngày (người dùng nói "tạm dừng"; đã commit và push).

## Đọc theo thứ tự
1. `README.md` (điểm vào, có mục "Việc của phiên này").
2. `.claude/CLAUDE.md` (tự nạp). Tên bước L-số trong bảng mục 2 là tên **cũ**; quy tắc 11 là cách làm việc với người dùng.
3. File này.
4. `docs/pipeline_moi.md`: thiết kế pipeline, cách làm từng bước, ví dụ dữ liệu thật, giải thích field, mẫu "thẻ bước" và thẻ mẫu 1.3.
5. `docs/quyet_dinh/pipeline_moi_quyet_dinh.txt`: quyết định đã chốt (mục A, A1 đến A20) và số đo, quan sát (mục B, B1 đến B10).
6. `docs/kiem_hieu.md`: 10 câu kiểm hiểu lớp 1.1 đến 1.5 (người dùng trả lời, agent chấm).
7. Khi cần: `docs/tien_do_L0_L6.md` (lịch sử code cũ), `docs/quyet_dinh/l*_quyet_dinh.txt` (quyết định của code cũ), `plan/ke_hoach/` (plan tham khảo, không sửa), `plan/ke_hoach/method_vi_3_1_den_3_6_2026-11-09.md` (bản Method của luận, nguồn của mô hình K).

## Câu mở phiên và câu kết phiên (người dùng copy-paste)
- **Trước khi mở:** `git pull` trên nhánh `v3_refactor`.
- **Mở phiên:** "Đọc README.md và làm theo mục 'Việc của phiên này'."
- **Kết phiên:** "Tạm dừng." (agent làm đúng mục "Khi người dùng nói tạm dừng" bên dưới).

## Trạng thái hiện tại
- Nhánh `v3_refactor`. Mốc cũ `d83a4d4` là code L0-L6 trước refactor.
- **Bước 1.1 đến 1.5 đã code xong** và chạy xanh: `python -I src/run_all.py --viewer --tests` ra 12/12 bước, 7 bộ test (113 test), cả `--llm off` lẫn `--llm replay`. Tên file mới: `parse`, `refs`, `delegation` (1.3), `links` (2.2), `article_type` (1.4, đã bỏ LLM), `exceptions_explicit`, `exceptions_general`, `textutil`. Bản đồ tên cũ sang mới ở `docs/pipeline_moi.md`.
- Khuôn cạnh chung `{s, p, o, evidence, how, flags}` (riêng 1.5 thêm `rule`). Đã bỏ field không ai đọc: `version` (1.1) và `heading` (1.4).
- Đếm lại trên đĩa 11/11, khớp số cũ: 10.202 đơn vị, 893 Điều, 2.348 `refers_to`, 129 chờ đích, 51 điều khoản giao chắc (cộng 5 ca lỏng cờ `loose`).
- Chưa làm: 1.6 đến 1.9 và toàn bộ giai đoạn 2 (đã có code cũ cho 2.3, 2.4 ở `l6_*.py`; 2.5 đến 2.7 chưa có).
- Mục tiêu người dùng đặt (A11): hết T7 (14/11/2026) có KB đủ lớp, có cơ chế cập nhật và một demo hỏi đáp nhỏ. Lịch đề xuất (người dùng chưa duyệt từng ngày): T5 12/11 làm 1.6 và 1.7; T6 13/11 làm 1.8, 1.9 và demo; T7 14/11 làm giai đoạn 2.

## Nợ (ghi 11/11)
1. **1.2 tầng 2** (xác định đích duy nhất cho 13 ca khoản/điểm trơ trụi, đều ở nghị định, thông tư) hoãn; BLLĐ có 0 ca (B10).
2. **5 ca lỏng của 1.3** chưa ai xác nhận (agent đọc: 4 thật, `D133.K1` nghi không). Không bắt buộc: pipeline không có người duyệt giữa chuỗi.
3. **`src/checks.py`** (bộ kiểm độc lập) chưa rà theo thiết kế mới (1.3 tầng lỏng, 1.4 không LLM, khuôn cạnh).
4. **Đầu vào khai báo của văn bản mới (`manifest.csv`):** cần khai `file`, `nhom`, `so_hieu`, `loai`, `ngay_hieu_luc` (và nên có `ngay_ban_hanh`); `so_dieu_dem_duoc` đề xuất cho tùy chọn nhưng code hiện còn đòi. Chưa sửa code.
5. **Thẻ bước 1.1, 1.2, 1.4, 1.5** chưa viết theo khuôn v2 (chỉ 1.3 có). Không chặn việc bàn 1.6.
6. **Cổng phần dư của `refs.py`** (từ khoá điều/khoản/điểm ngoài cụm) mới chỉ ghi báo cáo (đo: 0 sót); khi nạp văn bản mới ở giai đoạn 2 nên quyết có biến thành lỗi dừng không.
7. **Cạnh của L6** (`version_edges.jsonl`, bước 2.3 và 2.4) chưa theo khuôn cạnh chung: làm ở giai đoạn 2.
8. **Tài liệu lỗi thời:** bảng vai trò ở `docs/llm_config.md` còn ghi L4 dùng LLM; cache cũ `data/llm_cache/l4_classify/` không còn dùng (chưa xoá, cần người dùng bảo).
9. **Câu hỏi thiết kế còn mở** ở cuối mục "Câu hỏi thiết kế đang mở" của `docs/pipeline_moi.md` (câu 2 đến 8; câu 1 đã giải quyết bởi A14).

## Kiểm hiểu (người dùng bảo "khá hay, lưu lại" 11/11)
Bộ 10 câu ở `docs/kiem_hieu.md`, kết quả đang ghi "chưa trả lời" cả 10. Người dùng chưa trả lời câu nào, kể cả ba câu thử cho thẻ 1.3 (ở đó là câu 6, 7, 8). Agent chấm, giải thích chỗ sai, rồi ghi kết quả vào cột cuối của bảng đó.

## Việc kế tiếp (theo thứ tự)
1. Dựng lại và xác nhận xanh (README, mục "Dựng lại và kiểm").
2. Người dùng trả lời 10 câu kiểm hiểu; agent chấm và ghi lại.
3. **Bàn bước 1.6 (sổ khái niệm)**, chưa code. Đọc mục 3.5 của Method trước. Làm đúng quy tắc 11: kể lại bước bằng thẻ, hỏi kiểm hiểu, rồi mới nhờ quyết. Nhớ đếm hạn mức LLM (model chính 500 lượt/ngày, model kiểm 20 lượt/ngày) cho 1.6 đến 1.8 trước khi cam kết "mọi bước LLM đều có model thứ hai kiểm".
4. Kiểm s(CASP) trên máy này: `scasp --version`, `swipl --version`.
5. Khi rảnh: viết thẻ 1.1, 1.2, 1.4, 1.5; rà `checks.py`.

## Chờ người dùng
- Trả lời 10 câu kiểm hiểu.
- Restart VS Code ở máy chính rồi báo s(CASP) chạy được (người dùng nói chắc chắn đã cài; agent chưa thấy `scasp`, `swipl` trong PATH của phiên 11/11).
- `.claude/CLAUDE.md` mục 5 ("Việc đang dở", phần người dùng tự cập nhật) còn trỏ tới tài liệu cũ (`docs/tien_do_L0_L6.md`, nhánh `v2-lao-dong`): agent chưa sửa; muốn thì bảo.
- Xoá cache cũ `data/llm_cache/l4_classify/` và sửa `docs/llm_config.md`: cần người dùng bảo.

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
- Python 3.14.x, chỉ dùng thư viện chuẩn. `python -I src/run_all.py --viewer --tests` (khoảng 12 giây) dựng lại `data/processed/` và kiểm; phải ra `XONG: 12/12 bước`.
- Chỉ khi chạy LLM thật (`--llm live`): `.venv` có `google-genai`, biến môi trường `GEMINI_API_KEY` đặt riêng trên từng máy. Chi tiết ở `docs/ban_giao_2026-11-07.md` mục 1 và 2.
- s(CASP): người dùng nói đã cài ở máy chính; kiểm trên từng máy bằng `scasp --version`. Cần cho bước 1.8 và 1.9.
- Mốc đối chiếu cũ (đầu ra của code `d83a4d4` ở chế độ `replay`) không nằm trong git; dựng lại bằng `git worktree add <thư mục> d83a4d4` rồi `python -I src/run_all.py --llm replay --viewer` ở đó.
- Heldout giữ ngoài repo, không mở khi chưa tới lúc đo.
- Memory của Claude nằm trên từng máy và không đi theo git; mọi thứ cần nhớ phải nằm trong README, file này, `docs/pipeline_moi.md` và `docs/quyet_dinh/`.

## Nhật ký (mới nhất ở trên)

### 11/11/2026: code xong 1.1 đến 1.5, chốt cách báo cáo
- Người dùng đặt mục tiêu hết T7 và đổi nhịp làm việc: mỗi lượt một lớp; mỗi bước phải được kể lại (dữ liệu vào, ra, field, vì sao) trước khi nhờ quyết.
- Code: S1 đổi tên 5 file và dời `text_norm` sang `textutil.py` (đầu ra giống hệt mốc, 301 file); S2 bỏ LLM khỏi 1.4 (A14; 93 trên 921 nhãn đổi, 39 `effect_transition` không đổi); S3 khuôn cạnh chung (A12); S4 tách `l3_links.py` thành `delegation.py` (1.3, có tầng lỏng `loose`) và `links.py` (2.2); bỏ `version` và `heading` (A16).
- Lỗi tự gây, đã sửa: S3 để nhánh `--llm off` đọc field `check` đã bỏ (KeyError, lệnh dựng lại mặc định hỏng) mà chỉ kiểm bằng `replay`. Từ đó chạy cả hai chế độ mỗi lần.
- Phát hiện: cổng phần dư của 1.2 đã có sẵn trong code cũ (0 sót); tầng 2 hoãn (B10); 4 ca điều khoản giao bị regex chặt bỏ sót vì dấu gạch ngang trong "Bộ Lao động - Thương binh và Xã hội".
- Cách báo cáo: mẫu "thẻ bước" v2 (người dùng duyệt), bộ 10 câu kiểm hiểu, `README.md` làm điểm vào cho máy khác.
- Đã kiểm trước commit: bản sao sạch các file `git add` sẽ lấy chạy xanh 12/12 ở `--llm off` và `replay`; đầu ra `replay` giống hệt cây làm việc.
- Chưa kiểm: `checks.py` theo thiết kế mới; s(CASP) (agent chưa thấy trong PATH).

### 10/11/2026: chốt hướng refactor, chưa code
- Chốt pipeline hai giai đoạn, đánh số giai đoạn.bước, bỏ L-số. Tạo `docs/tien_do.md`, `docs/pipeline_moi.md`, `docs/quyet_dinh/pipeline_moi_quyet_dinh.txt`. Chi tiết ở A1 đến A10.
