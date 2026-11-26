# Hướng dẫn cho công cụ AI hỗ trợ lập trình

Dự án: cơ sở tri thức Bộ luật Lao động thích nghi theo ngày hiệu lực. Đọc trước khi làm việc: `README.md`, `CONTRIBUTING.md`, `docs/status.md`, rồi `docs/design/pipeline_design.md` và `docs/decisions.md` khi đụng tới một bước.

Quy tắc cần giữ (chi tiết ở `CONTRIBUTING.md`):
- Chỉ dùng thư viện chuẩn của Python. Chạy script bằng `python -I src/<module>.py`; chạy cả chuỗi và test bằng `python -I src/run_all.py --viewer --tests`, cả `--llm off` lẫn `--llm replay` (lần cuối là `replay`).
- Không chạy `--llm live` (tốn hạn mức hoặc tiền), không commit hay đẩy lên remote, không xoá hoặc ghi đè file dữ liệu khi chưa được yêu cầu.
- Không nới quy tắc để bắt thêm ca; chỗ đặc tả im lặng thì dừng và báo, không đoán. Chỗ lệch hay quyết định mới ghi vào `docs/decisions.md`.
- Mọi đầu ra LLM phải qua cổng kiểm bằng máy; không dùng một LLM để kiểm LLM khác. Sửa chữ lời nhắc đã dùng để chạy là làm vỡ cache: phải nâng `PROMPT_VERSION`.
- Khoá API chỉ nằm trong biến môi trường. Không đọc, không ghi nội dung hay đường dẫn của nhóm văn bản dùng để đo (heldout).
- Đặt tên file và thư mục theo `CONTRIBUTING.md` mục 1. Không tạo thêm tài liệu trùng vai với các tài liệu hiện có.
- Báo cáo trung thực: nói cái gì đã chạy, cái gì chưa kiểm; không ghi "xong" khi chưa chạy test.
