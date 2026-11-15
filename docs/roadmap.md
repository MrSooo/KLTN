# Lộ trình

Lộ trình này thay kế hoạch ban đầu, vốn đã lạc hậu sau khi thiết kế được chia lại thành hai giai đoạn (dựng KB gốc, cập nhật). Chưa đặt hạn cứng; thứ tự dưới đây theo phụ thuộc. Trạng thái hiện tại: `docs/status.md`; thiết kế: `docs/design/pipeline_design.md`; lý do: `docs/decisions.md`.

## Mục tiêu
Một cơ sở tri thức dựng từ BLLĐ 45/2019, trả lời được câu hỏi có/không theo ngày sự việc kèm căn cứ, cập nhật được khi nạp nghị định, thông tư theo ngày hiệu lực; có bộ câu hỏi với đáp án chuẩn để đo; chuỗi cập nhật tăng dần cho cùng kết quả với dựng lại toàn bộ.

## Giai đoạn 1: KB gốc

### M1. Hoàn tất 1.6A (mệnh đề)
- Chạy 204 lô theo A39 (xem `docs/status.md`, mục 3).
- Nhập kết quả (`propositions.py nhap`), đo ba số nghiệm thu (cặp ứng viên cho 1.7, tái dùng ở 1.6B, mệnh đề lặp ở từ 2 Điều).
- Nối `propositions.py` vào `run_all` (bước, replay, kiểm của `checks`); quyết bỏ `concepts.py` cũ hay giữ cho tới khi 1.6B mới xong.
- Điều kiện chuyển bước: ba số nghiệm thu hơn bản cũ; nếu không, dừng và quyết hướng với chủ đề tài (không tự sửa lời nhắc).

### M2. Viết lại 1.6B (sổ vị từ)
- Viết `names-2` đọc mệnh đề theo A39 (gộp theo `menh_de` và chữ ký `doi_so`, lọc ứng viên lỏng, `CANDIDATE_CAP` 20, luật `reuse` chặt); chủ đề tài duyệt lời nhắc trước khi chạy.
- Chạy bằng phiên Claude Code (Sonnet 5.5, effort `high`, tuần tự); nhập; đọc mẫu 150 quyết định `reuse` và 50 quyết định `new`.
- Xoá cache `concepts_names` cũ khi được bảo.

### M3. Bước 1.7 (ngoại lệ ngầm)
- Đếm số cặp ứng viên (hai đơn vị cùng dùng một vị từ `concept`) từ sổ của 1.6B; quyết ngân sách và bộ lọc theo số thật.
- Phần máy (dựng cặp, cổng, vòng) làm được trước bằng sổ giả. Quyết có cắt 1.7 hay không sau khi có số cặp thật.

### M4. Bước 1.8 (quy tắc s(CASP))
- Quyết các điểm mở (A33): đưa 43 cạnh bắt đầu từ nút điều kiện vào quy tắc; ngoại lệ lồng nhau; quy tắc kết luận phủ định cho "bị bác"; ai gán hai dạng ngoại lệ; `liet_ke` và `khong_ap_dung` biên dịch ra sao.
- Cổng biên dịch dựa trên `library(scasp)`; bộ quét bốn loại (quy tắc không bao giờ kích hoạt, trùng lặp, vòng chặn, cặp kết luận ngược không có quan hệ chặn) cộng cổng biến của vị từ ngoại lệ (S5).

### M5. Bước 1.9 (hỏi đáp theo ngày) và bộ câu hỏi
- Thiết kế bước: đổi câu hỏi thành dữ kiện, chạy φ và ¬φ, bốn loại đáp án.
- Xây bộ câu hỏi thật về BLLĐ có đáp án chuẩn do con người xác nhận (cần cho đo bước 1.8 và 1.9, và cho các phép đo tỉ lệ tái dùng và ngoại lệ ngầm).
- Chọn câu hỏi cổng cho giai đoạn 1 (câu hỏi chỉ cần BLLĐ).

## Giai đoạn 2: cập nhật
- 2.1: xử lý văn bản mới bằng 1.1 đến 1.5 (cần chuẩn hoá khai báo manifest, nợ 4 ở `docs/status.md`).
- 2.5: tập ảnh hưởng A(d) = T(d) ∪ N(T(d)); quyết số bước lan truyền của N(·).
- 2.6: trích lại mệnh đề, vị từ, ngoại lệ ngầm, quy tắc cho A(d) (tái dùng 1.6 đến 1.8); quét lỗi.
- 2.7: đối chứng: chạy tăng dần và dựng lại toàn bộ phải ra cùng Π_τ tại cùng ngày.
- Quyết cách xử lý 8 Điều lệch BLLĐ và VBHN_125 khi bản hợp nhất là văn bản nạp thường (A4).

## Đo và viết bài
- Đo trên nhóm văn bản dùng để đo (ngoài repo); chỉ mở khi các bước xong và bộ câu hỏi có đáp án chuẩn.
- Chuẩn bị số liệu cho bài: kết quả từng bước (số đo ở `docs/run_reports/`), độ chính xác tái dùng vị từ, độ chính xác ngoại lệ ngầm, tỉ lệ câu trả lời đúng theo bốn loại.
- Đồng bộ chữ của bài với hệ thống thật: mục 3.5 ở `docs/reference/method.md` (A25); ghi lý do dùng phiên Claude Code thay model nhẹ miễn phí.

## Việc kỹ thuật chạy song song
- Rà toàn bộ `checks.py` theo thiết kế mới.
- Đo độ chính xác phần mở rộng "trừ <danh từ>" của bước 1.5 trên mẫu đọc tay.
- Bước 1.2 tầng 2 nếu văn bản dưới luật thêm vào cần.
- Danh sách nợ đầy đủ: `docs/status.md`, mục 4.

## Điều gì sẽ chứng minh lộ trình này sai
- Chuỗi cập nhật tăng dần không ra cùng kết quả với dựng lại toàn bộ.
- Phần lớn văn bản dưới luật không nối được `details` hoặc `based_on` vào Bộ luật bằng regex và LLM; khi đó KB không biết nghị định nào hướng dẫn điều nào.
- Ba số nghiệm thu của bước 1.6A không hơn bản cũ (A39): khi đó cách tách mệnh đề không tăng khả năng nối các điều luật và phải đổi hướng.
