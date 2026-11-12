# kltn: cơ sở tri thức Bộ luật Lao động, thích nghi theo ngày hiệu lực

Đồ án tốt nghiệp. Hệ thống dựng một cơ sở tri thức (KB) từ Bộ luật Lao động 45/2019, trả lời câu hỏi có/không theo ngày sự việc kèm căn cứ, và cập nhật được khi nạp nghị định, thông tư.

## Dành cho agent mới (máy mới, phiên mới)
Người dùng sẽ dán đúng một câu: **"Đọc README.md và làm theo mục 'Việc của phiên này'."**

Đọc theo thứ tự:
1. `.claude/CLAUDE.md`: luật làm việc (tự nạp). Quan trọng nhất là quy tắc 11 (người dùng phải *hiểu* trước khi quyết, nên mỗi bước được kể lại bằng "thẻ bước" rồi hỏi kiểm hiểu) và quy tắc 12 (không chiều ý người dùng: phản biện cả ý kiến của họ).
2. `docs/tien_do.md`: trạng thái chi tiết, danh sách nợ, nhật ký, quy trình khi người dùng nói "tạm dừng".
3. `docs/pipeline_moi.md`: thiết kế pipeline (các bước 1.1 đến 2.7), cách làm từng bước, ví dụ dữ liệu thật, giải thích field.
4. `docs/quyet_dinh/pipeline_moi_quyet_dinh.txt`: các quyết định đã chốt và lý do (mục A), số đo và quan sát (mục B).
5. `docs/kiem_hieu.md`: bộ kiểm hiểu 1.1 đến 1.6 (10 câu mỗi bước, tổng 60 câu; người dùng trả lời, agent chấm theo `docs/kiem_hieu_dap_an.md`). Đang tạm dừng đến khi chốt xong 1.6.
6. `docs/the_buoc_1_1_den_1_5.md`: thẻ bước 1.1 đến 1.5 (số đo, bảng phát hiện); thẻ 1.6 (bản bàn) nằm ở `docs/pipeline_moi.md`.

Chưa cần đọc: `plan/ke_hoach/` (plan cũ, chỉ tham khảo), `archive/` (bản v1 thừa kế, đóng băng), `docs/tien_do_L0_L6.md` (lịch sử code cũ). Tên bước kiểu L1, L5... là tên CŨ; người dùng không dùng, nói với họ bằng tên mới (1.5, `exceptions`).

## Việc của phiên này
*(ghi đè mỗi lần người dùng nói "tạm dừng"; cập nhật lần cuối 13/11/2026, tối; người dùng làm tiếp ngày 14/11 trên máy ở công ty)*

Trạng thái: bước 1.1 đến 1.5 xong. **Bước 1.6 giai đoạn A (gạch cụm, `src/concepts.py`) đã chạy live xong 204/204 lô bằng Claude Sonnet 5.5** (A34, A35; tốn $2,61). Đã đọc kết quả, tìm ra hai lỗi và sửa trong code (A35); sửa làm 10 lô đổi ngữ cảnh nên `replay` báo 194/204 (thiếu 10 lô, bình thường). `python -I src/run_all.py --viewer --tests` xanh 13/13 ở cả `--llm off` lẫn `replay`, 8 bộ test, 154 test. Người dùng đã đồng ý chuyển vai `trich` sang Claude Haiku 5.5 (rẻ hơn khoảng 20 lần): **chưa chạy**, cấu hình đang commit vẫn là Sonnet (hệ quả: 1.6A phải chạy lại bằng Haiku, khoảng $0,13; chi tiết A35). Chưa làm: 1.6B (đặt tên, tái dùng vị từ), 1.7, 1.8, 1.9, giai đoạn 2. Mục tiêu hết T7 (14/11) của A11 đã trượt; chờ người dùng quyết cắt gì (mục "Chờ người dùng" ở `docs/tien_do.md`).

### 14/11 trên máy ở công ty: người dùng chạy, agent hướng dẫn từng lệnh (không chạy `--llm live` khi người dùng chưa bảo)
1. Lấy mã: `git clone https://github.com/MrSooo/KLTN.git kltn`, `cd kltn`, `git switch v3_refactor` (đã có thư mục thì `git pull`). Trên máy cũ remote tên `KLTN`, máy mới tên `origin`.
2. Python từ 3.10 trở lên (máy nhà 3.14, 3.13.5 từng chạy xanh). Tạo venv và cài gói Claude: `python -m venv .venv`, rồi `.venv\Scripts\python.exe -m pip install -U anthropic`. (Gói `google-genai` chỉ cần cho bước 2.2 live, ngày 14/11 chưa cần.)
3. Dựng dữ liệu và kiểm (không cần khoá, không gọi mạng): `.venv\Scripts\python.exe -I src\run_all.py --viewer --tests` phải ra `XONG: 13/13 bước`. `data/processed/` không nằm trong git; `concepts.py` cần nó.
4. Khoá API, không dán vào chat hay file. Trong terminal PowerShell của chính người dùng: `$env:ANTHROPIC_API_KEY = Read-Host "khoá"` rồi dán khoá. Khoá chỉ sống trong cửa sổ terminal đó và không vào lịch sử lệnh (tốt hơn `setx` trên máy công ty). Nếu dùng `setx` thì phải đóng HẲN mọi cửa sổ VS Code rồi mở lại (tối 12/11 vấp đúng chỗ này).
5. Kiểm thấy khoá: `.venv\Scripts\python.exe -I src\llm_client.py` (không cờ nào); dòng "khoá" phải có `'anthropic': 'có'` (`'gemini': 'KHÔNG THẤY'` là bình thường). Đừng chạy `--check-models` ở máy này: nó thoát vì thiếu khoá Gemini.
6. Mạng công ty: nếu lượt gọi đầu báo lỗi kết nối thì thường là proxy; đặt `$env:HTTPS_PROXY = "http://<proxy>:<cổng>"` (hỏi IT) rồi thử lại.
7. Chuyển sang Haiku: sửa ĐÚNG hai dòng ở `docs/llm_config.md`: `trich.model = claude-haiku-5-5` và `trich.thinking = disabled`.
8. Lượt trả phí đầu (khoảng $0,001), chỉ lô 1: `.venv\Scripts\python.exe -I src\concepts.py --llm live --max-batches 1`. Thấy dòng "xong sau ...s (token vào ..., ra ...)" là hình lời gọi ổn. Báo lỗi 400 thì dán nguyên văn: Haiku CHƯA từng gọi thật (tham số `thinking: disabled` và lược đồ chưa kiểm).
9. Cả bộ, khoảng $0,13: `.venv\Scripts\python.exe -I src\concepts.py --llm live`. Dừng giữa chừng (quá tải, mạng) thì chạy lại đúng lệnh đó, các lô đã xong đọc từ cache.
10. So sánh Haiku với Sonnet theo A35 (agent làm bằng script tạm, không đưa vào repo; mốc Sonnet nằm sẵn trong `data/llm_cache/concepts_spans/`, 30 đơn vị mẫu ghi ở A35). Haiku đạt thì giữ; không đạt thì hoàn tác hai dòng ở bước 7 và chạy lại đúng 10 lô đã đổi ngữ cảnh bằng Sonnet (khoảng $0,2).
11. Rồi agent code phần máy của 1.6B (đặt tên, tái dùng vị từ; đọc thẻ 1.6 ở `docs/pipeline_moi.md` mục 4 bước 5 đến 7, A29 đến A31, và A35). Cần người dùng trả lời trước: (a) đến (e) của thẻ 1.8 (đề xuất ở B11) và có cắt 1.7 hay không.

### Agent mở phiên 14/11
Đọc theo thứ tự ở trên, thêm A34, A35 và B11 ở `docs/quyet_dinh/pipeline_moi_quyet_dinh.txt`. Giúp người dùng làm các bước 1 đến 10. Nhớ quy tắc 13 và 14 ở CLAUDE.md (không lén đưa vào; tự kiểm trước khi hỏi). Khi người dùng nói "tạm dừng" thì làm đúng quy trình ở `docs/tien_do.md`.

## Dựng lại và kiểm
Chỉ dùng thư viện chuẩn của Python (từ 3.10; máy nhà 3.14.x). `data/processed/` bị `.gitignore`, sinh lại bằng:
```
python -I src/run_all.py --viewer --tests        # ~15 giây; phải ra "XONG: 13/13 bước"
python -I src/run_all.py --llm replay --viewer --tests   # đọc lại các phản hồi LLM đã lưu ở data/llm_cache/ (không gọi mạng); 1.6 báo 194/204 lô (thiếu 10 lô đổi ngữ cảnh, A35)
```
Chỉ khi chạy LLM thật (`--llm live`) mới cần `.venv` có `google-genai` (2.2, Gemini) và `anthropic` (1.6 trở đi, Claude, từ 12/11, A34) cùng biến môi trường `GEMINI_API_KEY` và `ANTHROPIC_API_KEY` (đặt riêng trên từng máy, không đưa vào repo). Không chạy `live` khi người dùng chưa bảo.

## Cách làm việc với người dùng (tóm tắt, bản đầy đủ ở CLAUDE.md)
- Người dùng làm chủ: agent đề xuất, người dùng quyết. Không "làm dùm".
- Thảo luận thiết kế trước, code sau, từng lớp một. Báo cáo ngắn, tiếng Việt, nói rõ cái gì đã chạy và cái gì chưa kiểm.
- Không commit, push, xoá, ghi đè, chạy `--llm live` khi chưa được bảo (trừ lệnh "tạm dừng": cập nhật `docs/tien_do.md` rồi commit và push).
