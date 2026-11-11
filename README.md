# kltn: cơ sở tri thức Bộ luật Lao động, thích nghi theo ngày hiệu lực

Đồ án tốt nghiệp. Hệ thống dựng một cơ sở tri thức (KB) từ Bộ luật Lao động 45/2019, trả lời câu hỏi có/không theo ngày sự việc kèm căn cứ, và cập nhật được khi nạp nghị định, thông tư.

## Dành cho agent mới (máy mới, phiên mới)
Người dùng sẽ dán đúng một câu: **"Đọc README.md và làm theo mục 'Việc của phiên này'."**

Đọc theo thứ tự:
1. `.claude/CLAUDE.md`: luật làm việc (tự nạp). Quan trọng nhất là quy tắc 11: người dùng phải *hiểu* trước khi quyết, nên mỗi bước được kể lại bằng "thẻ bước" rồi hỏi kiểm hiểu.
2. `docs/tien_do.md`: trạng thái chi tiết, danh sách nợ, nhật ký, quy trình khi người dùng nói "tạm dừng".
3. `docs/pipeline_moi.md`: thiết kế pipeline (các bước 1.1 đến 2.7), cách làm từng bước, ví dụ dữ liệu thật, giải thích field.
4. `docs/quyet_dinh/pipeline_moi_quyet_dinh.txt`: các quyết định đã chốt và lý do (mục A), số đo và quan sát (mục B).
5. `docs/kiem_hieu.md`: bộ kiểm hiểu 1.1 đến 1.5 (10 câu mỗi bước, tổng 50 câu; người dùng trả lời, agent chấm theo `docs/kiem_hieu_dap_an.md`).

Chưa cần đọc: `plan/ke_hoach/` (plan cũ, chỉ tham khảo), `archive/` (bản v1 thừa kế, đóng băng), `docs/tien_do_L0_L6.md` (lịch sử code cũ). Tên bước kiểu L1, L5... là tên CŨ; người dùng không dùng, nói với họ bằng tên mới (1.5, `exceptions`).

## Việc của phiên này
*(ghi đè mỗi lần người dùng nói "tạm dừng"; cập nhật lần cuối 11/11/2026)*

Trạng thái: bước 1.1 đến 1.5 đã code xong và chạy xanh (12/12 bước, 113 test). Chưa làm: 1.6 đến 1.9 và giai đoạn 2. Mục tiêu hết T7 (14/11/2026): KB đủ lớp, có cơ chế cập nhật, có demo hỏi đáp nhỏ (A11).

Làm theo thứ tự:
1. **Dựng lại và xác nhận xanh** (mục dưới): phải ra `XONG: 12/12 bước`.
2. **Kiểm s(CASP)** trên máy này: `scasp --version`, `swipl --version`. Người dùng nói đã cài ở máy chính; cần cho bước 1.8 và 1.9.
3. **Kiểm hiểu:** người dùng nói "kiểm 1.x" thì agent hỏi 10 câu của bước đó (`docs/kiem_hieu.md`, tổng 50 câu cho 5 bước); chấm đúng/thiếu/sai theo `docs/kiem_hieu_dap_an.md` (chỉ dành cho agent, chưa đưa đáp án trước), giải thích chỗ sai, ghi kết quả và mức nắm vào bảng.
4. **Bàn bước 1.6 (sổ khái niệm)**, chưa code: đọc mục 3.5 của Method (`plan/ke_hoach/method_vi_3_1_den_3_6_2026-11-09.md`), kể lại bước bằng "thẻ bước" (khuôn ở `docs/pipeline_moi.md`), hỏi kiểm hiểu, rồi mới nhờ người dùng quyết.
5. Nợ còn lại (thẻ bước 1.1/1.2/1.4/1.5, rà `checks.py`, ...) ở `docs/tien_do.md`; không chặn việc bàn 1.6.

## Dựng lại và kiểm
Chỉ dùng thư viện chuẩn của Python (3.14.x). `data/processed/` bị `.gitignore`, sinh lại bằng:
```
python -I src/run_all.py --viewer --tests        # ~12 giây; phải ra "XONG: 12/12 bước"
python -I src/run_all.py --llm replay --viewer --tests   # đọc lại các phản hồi LLM đã lưu ở data/llm_cache/ (không gọi mạng)
```
Chỉ khi chạy LLM thật (`--llm live`) mới cần `.venv` có `google-genai` và biến môi trường `GEMINI_API_KEY` (đặt riêng trên từng máy, không đưa vào repo). Không chạy `live` khi người dùng chưa bảo.

## Cách làm việc với người dùng (tóm tắt, bản đầy đủ ở CLAUDE.md)
- Người dùng làm chủ: agent đề xuất, người dùng quyết. Không "làm dùm".
- Thảo luận thiết kế trước, code sau, từng lớp một. Báo cáo ngắn, tiếng Việt, nói rõ cái gì đã chạy và cái gì chưa kiểm.
- Không commit, push, xoá, ghi đè, chạy `--llm live` khi chưa được bảo (trừ lệnh "tạm dừng": cập nhật `docs/tien_do.md` rồi commit và push).
