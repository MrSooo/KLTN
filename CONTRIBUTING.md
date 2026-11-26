# Hướng dẫn đóng góp

Tài liệu này nêu quy ước làm việc chung của dự án. Tổng quan và cách chạy: [README.md](README.md). Lý do của các quyết định thiết kế: [docs/decisions.md](docs/decisions.md).

## 1. Quy ước đặt tên
- **Tên file và thư mục:** chữ thường, ASCII (không dấu), `snake_case`, đặt bằng tiếng Anh theo việc file làm. Không đặt số thứ tự, ngày, hay số phiên bản vào tên (`pipeline_design.md`, không phải `pipeline_v2_2026-11-15.md`). Ngoại lệ: tên file dữ liệu đầu vào mang `doc_id` của văn bản (`ND_145-2020.txt`).
- **Module và bước:** mỗi bước pipeline là một module trong `src/` đặt theo việc nó làm (`parse`, `refs`, `delegation`, `article_type`, ...). Số bước (1.1, 1.2, ..., 2.7) chỉ dùng trong tài liệu và nhãn hiển thị; không đưa vào tên file hay tên thư mục.
- **Đầu ra và báo cáo:** thư mục đầu ra là `data/processed/<module>/`, báo cáo chữ là `docs/run_reports/<module>/`, tên file trong đó bắt đầu bằng tên module (`parse_payloads_<doc_id>.jsonl`, `parse_report_<doc_id>.txt`).
- **Test:** `tests/test_<module>.py`. Một file test có thể phủ nhiều module liền kề, khi đó tên file liệt kê các module (`test_links_article_type_exceptions.py`). Hàm test đặt tên theo module và hành vi (`test_exceptions_general_clause_extraction`).
- **Định danh Python:** `snake_case` cho hàm và biến, `UPPER_CASE` cho hằng. Không dùng tên viết tắt vô nghĩa làm bí danh module: import module bằng tên đầy đủ (`import parse`, `import refs`) và không đặt biến cục bộ trùng tên module đã import.
- **Nội dung:** tài liệu và chú thích viết bằng tiếng Việt, giải thích *vì sao* (không chép lại mã). Tên trường dữ liệu trong file đầu ra (`menh_de`, `chu_the`, `phuong_thuc`, ...) giữ nguyên; đổi một tên trường là đổi lược đồ và phải sửa mã, test, tài liệu và cache liên quan.

## 2. Quy trình làm việc
1. Mỗi thay đổi nhỏ, tách theo một việc. Không gộp refactor với sửa hành vi.
2. Trước khi sửa một bước, đọc phần mô tả của nó trong `docs/design/` và các quyết định liên quan trong `docs/decisions.md`.
3. Sau khi sửa, chạy **cả hai chế độ**, theo thứ tự này (lần cuối là `replay` để báo cáo ở `docs/run_reports/` đúng trạng thái):
   ```
   python -I src/run_all.py --llm off    --viewer --tests
   python -I src/run_all.py --llm replay --viewer --tests
   ```
   Cả hai phải ra `XONG: 14/14 bước` (số bước có thể đổi khi thêm bước) và mọi bộ test `tổng test lỗi: 0`. Đổi một trường mà chỉ kiểm một chế độ đã từng làm hỏng nhánh còn lại.
4. "Xanh" chỉ nghĩa là mã chạy, các kiểm chặn qua và các mốc còn đó; chưa phải "đúng" (`checks` không đo độ chính xác của cạnh). Khi báo kết quả, nói rõ cái gì đã chạy, cái gì chưa kiểm; không ghi "xong" khi chưa chạy test.
5. Khi đổi một bước, xem `git diff --stat docs/run_reports/` để biết báo cáo nào đổi; mọi chênh lệch phải giải thích được.
6. Thêm một bước mới: viết module, thêm vào `run_all.py` đúng thứ tự phụ thuộc, thêm kiểm độc lập vào `checks.py`, viết test, viết mô tả trong `docs/design/` theo khuôn ở `docs/design/pipeline_design.md` mục 6, và ghi quyết định vào `docs/decisions.md`.

## 3. Quy tắc kỹ thuật
- **Chỉ dùng thư viện chuẩn của Python.** Ngoại lệ: gói của nhà cung cấp LLM khi chạy `--llm live` (cài trong `.venv`, không cài vào Python hệ thống), và s(CASP) trên SWI-Prolog cho bước 1.8 trở đi.
- **Chạy script:** `python -I src/<module>.py` (cờ `-I` để không nạp nhầm file cạnh script).
- **Không nới quy tắc để bắt thêm ca.** Dạng spec không nói thì báo lỗi và dừng (thoát mã 1, không ghi file); không đoán. Muốn bắt thêm ca thì ghi quyết định riêng và đo độ chính xác.
- **Chỗ spec im lặng hoặc lệch spec** phải có mục trong `docs/decisions.md` (đánh số tiếp A41, A42, ..., ghi chỗ lệch lên đầu mục).
- **Không để mã chết hoặc cờ thừa.** Trường dữ liệu không ai đọc thì bỏ (A16).
- Máy bật `core.autocrlf=true` có thể làm `git status` hiện file đổi giả (khác LF/CRLF): xem `git diff` trước, chỉ `git restore` khi chắc là giả. Dữ liệu `data/raw/labor/` là LF; mã không được giả định `\r\n`.

## 4. LLM
- Mọi lời gọi LLM đi qua `src/llm_client.py` (cache, hạn mức, giãn nhịp theo RPM). Không gọi API ở nơi khác.
- Chế độ: `off` không gọi gì; `replay` chỉ đọc cache (thiếu thì `CacheMiss`); `live` gọi mạng. **Không chạy `live` khi chưa được phép**: tốn hạn mức hoặc tiền.
- Đề xuất của LLM không được áp thẳng: bước gọi phải kiểm bằng máy (khớp nguyên văn, giá trị trong tập đóng, vị từ trong sổ, biên dịch). Không dùng LLM để kiểm LLM khác (A6, A14, A25). Đổi nhà cung cấp hay model không được làm lỏng các kiểm tra này.
- **Khoá cache gồm model, tên tác vụ, phiên bản lời nhắc, đầu vào, chữ `system` và lược đồ.** Sửa chữ lời nhắc hay lược đồ thì phải nâng `PROMPT_VERSION`; sửa một chữ lời nhắc đã dùng để chạy là chạy lại từ đầu. Khi đổi tên tác vụ, phải di chuyển bản ghi cache và kiểm lại khoá từng bản ghi.
- Chỉ gửi văn bản luật công khai cho dịch vụ bên ngoài. Không đưa tên, thông tin cá nhân hay dữ liệu nội bộ vào lời gọi.

## 5. Bí mật và dữ liệu
- Khoá API chỉ nằm trong biến môi trường (`GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `CKEY_API_KEY`). Không đưa vào repo, tệp `.env`, chat, test hay báo cáo.
- Nhóm văn bản dùng để đo (heldout) nằm ngoài repo và chưa được mở; không đưa nội dung hay đường dẫn của nó vào mã, tài liệu hay cache cho tới khi giai đoạn đo bắt đầu. Chỉ `data/raw/labor/` (nhóm base và dev) được dùng khi dựng.
- `data/processed/` bị `.gitignore`; `data/llm_cache/` được theo dõi (không ignore) vì đó là cách tính lại số liệu không cần gọi model.
- Không sửa tay file do mã sinh ra (`docs/run_reports/`, `data/processed/`, các file HTML sinh ra).

## 6. Tài liệu
- Mỗi tài liệu có một vai: tổng quan (`overview.md`), trạng thái (`status.md`), lộ trình (`roadmap.md`), thiết kế (`design/`), vận hành (`operations/`), tra cứu (`reference/`), quyết định (`decisions.md`). Không tạo tài liệu trùng vai.
- Số liệu trong tài liệu phải đối chiếu với mã và đĩa, ghi đo ở đâu và ngày nào; không chép số từ tài liệu cũ.
- Cập nhật `docs/status.md` khi trạng thái bước đổi; ghi quyết định mới ngay vào `docs/decisions.md`.
- Báo cáo gửi người ngoài viết bằng Markdown rồi dựng HTML bằng `python -X utf8 -I utils/render_report.py <md> <html>`; không sửa HTML bằng tay.
