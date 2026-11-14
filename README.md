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
*(ghi đè mỗi lần người dùng nói "tạm dừng"; cập nhật lần cuối 14/11/2026, chiều; người dùng sẽ tự đọc lại cách làm 1.6B trước khi làm tiếp)*

Trạng thái: bước 1.1 đến 1.5 xong. **Bước 1.6 giai đoạn A (gạch cụm, `src/concepts.py`) xong 204/204 lô ngày 14/11**, phần LLM chạy bằng phiên Claude Code (Opus 5.5, lời nhắc `concepts-2`), KHÔNG gọi API (A36; kế hoạch Haiku qua API của 13/11 đã bỏ). Kết quả ở `data/llm_cache/concepts_spans/`, `replay` đọc đủ 204/204; 3069 cụm LLM, 0 cụm hỏng cổng nguyên văn; phần sót đã đo và ghi ở A36. Kiểm 14/11: `python -I src/run_all.py --viewer --tests` rồi `--llm replay --viewer --tests`, cả hai 13/13 bước, 8 bộ test, 155 test, 0 lỗi. **Cách làm 1.6B (đặt tên, tái dùng vị từ) đã viết xong nhưng CHƯA code**: `docs/pipeline_moi.md` thẻ 1.6 mục 4 bước 5 đến 10, mục 4b, mục 7; quyết định ở A37.

Việc của agent phiên sau:
1. Đọc `docs/tien_do.md` (nhất là "Chờ người dùng" và "Việc kế tiếp"), A36 và A37, rồi thẻ 1.6 ở các mục trên.
2. **Không code 1.6B khi người dùng chưa nói đã check và duyệt các mục [THÊM] ở A37 (6).** Hỏi họ đúng việc đó trước, kèm kết quả đã tự kiểm.
3. Khi được bảo code 1.6B: việc đầu tiên là đếm chữ còn ứng viên (không gọi LLM; luật dừng đề xuất 20%), rồi theo "Việc kế tiếp" mục 2. Phần LLM của 1.6B cũng chạy bằng phiên Claude Code (Sonnet 5.5), tuần tự khoảng 76 lượt; agent dựng thư mục làm việc và hướng dẫn, người dùng tự chạy phiên đó. Không chạy `--llm live` khi người dùng chưa bảo.
4. Nhớ quy tắc 12, 13 và 14 ở CLAUDE.md (không chiều ý; không lén đưa vào, mục nào tự thêm phải đánh dấu [THÊM]; tự kiểm trước khi hỏi). Trước khi commit chạy `--llm off` rồi `--llm replay` (lần cuối là `replay`, để báo cáo ở `docs/bao_cao_chay/` đúng trạng thái). Khi người dùng nói "tạm dừng" thì làm đúng quy trình ở `docs/tien_do.md`.

## Dựng lại và kiểm
Chỉ dùng thư viện chuẩn của Python (từ 3.10; máy nhà 3.14.x). `data/processed/` bị `.gitignore`, sinh lại bằng:
```
python -I src/run_all.py --viewer --tests        # ~15 giây; phải ra "XONG: 13/13 bước"
python -I src/run_all.py --llm replay --viewer --tests   # đọc lại các phản hồi LLM đã lưu ở data/llm_cache/ (không gọi mạng); 1.6 báo 204/204 lô (từ 14/11, A36)
```
Chỉ khi chạy LLM thật (`--llm live`) mới cần `.venv` có `google-genai` (2.2, Gemini) và `anthropic` (1.6 trở đi, Claude, từ 12/11, A34) cùng biến môi trường `GEMINI_API_KEY` và `ANTHROPIC_API_KEY` (đặt riêng trên từng máy, không đưa vào repo). Không chạy `live` khi người dùng chưa bảo.

## Cách làm việc với người dùng (tóm tắt, bản đầy đủ ở CLAUDE.md)
- Người dùng làm chủ: agent đề xuất, người dùng quyết. Không "làm dùm".
- Thảo luận thiết kế trước, code sau, từng lớp một. Báo cáo ngắn, tiếng Việt, nói rõ cái gì đã chạy và cái gì chưa kiểm.
- Không commit, push, xoá, ghi đè, chạy `--llm live` khi chưa được bảo (trừ lệnh "tạm dừng": cập nhật `docs/tien_do.md` rồi commit và push).
