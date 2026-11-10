# Làm thêm gì so với bản trước (tóm tắt nhanh)

**Bản trước (v1):** Bộ luật Dân sự 2015, phần thừa kế; 8 bước A1-A8.
**Bản hiện tại:** Bộ luật Lao động 45/2019 cùng 17 văn bản dưới luật; các bước L0-L6, kiểm tra độc lập, đồ thị gộp và trang xem theo ngày.

## 1. Đổi lĩnh vực, mở rộng dữ liệu
- Từ luật thừa kế sang luật lao động; dữ liệu, mẫu câu và kiểm tra đều viết lại cho Bộ luật Lao động.
- Từ một bộ luật sang một họ văn bản có thứ bậc: luật, nghị định, thông tư, nghị quyết, bản hợp nhất. Tổng 18 văn bản, 893 Điều, 10.202 đơn vị (tính cả bản hợp nhất, vốn lặp lại 220 Điều của Bộ luật).

## 2. Hiểu quan hệ giữa các văn bản
- **Điều khoản giao chi tiết (L3):** 5 dạng (A-E). Tìm 51 chỗ Bộ luật giao cho văn bản dưới luật, nối văn bản hướng dẫn về đúng điều (10 cạnh căn cứ, 48 cạnh hướng dẫn). Văn bản không nêu số Điều thì LLM đề xuất và phải qua kiểm.
- **Phân loại Điều (L4):** 921 Điều và phụ lục có nhãn (nội dung chính, định nghĩa, thẩm quyền, thủ tục, chuyển tiếp hiệu lực, phụ lục).

## 3. Chỉ thị hiệu lực: bảng 26 loại
- Mẫu câu chỉ thị được dựng theo cách các nghị định, thông tư trong kho thực sự diễn đạt: sửa hoặc bổ sung "như sau", thay cụm từ, bãi bỏ, hết hiệu lực cả văn bản hoặc theo chủ đề, hiệu lực có điều kiện, có thời hạn, bản hợp nhất, ban hành theo luật cũ.
- 26 loại: **17 có ca thật** (kiểm trên 18 văn bản, đạt 15/15 mốc kiểm) và **9 chưa có ca thật** (đã cài, kiểm bằng ví dụ tự soạn, ghi rõ là chưa đo).
- Câu chỉ thị lạ thì báo lỗi, không đoán (hiện 0 ca).
- So bản hợp nhất với Bộ luật gốc: tìm ra 1 sửa đổi thật (Điều 154 khoản 8a, hiệu lực 01/01/2026) và 4 Điều có lỗi hoặc sai lệch chữ của chính bản hợp nhất (42, 87, 185, 220); 4 Điều này được gắn cờ, không tạo phiên bản.

## 4. Dùng LLM có kiểm soát
- Gemini chỉ đọc hiểu và đề xuất; một model khác kiểm độc lập. Đề xuất không được áp thẳng mà phải qua cổng kiểm của máy.
- Mọi phản hồi lưu cache: chạy lại cho cùng kết quả, không tốn lượt.

## 5. Độ tin cậy và công cụ
- Bước kiểm độc lập (đếm lại bằng bộ đếm riêng): 6 nhóm, 0 lỗi. Chuỗi phiên bản (L6) chạy lại hai lần ra file giống hệt. 120 test.
- Đồ thị gộp 9.364 nút, 2.721 cạnh ngữ nghĩa, kèm trang HTML xem đồ thị theo ngày (mở offline).
- Chạy cả chuỗi bằng một lệnh.

## Chưa làm
- L7-L11: sổ khái niệm, ngoại lệ ngầm, trích quy tắc, trả lời câu hỏi, đo.
- 9 loại chỉ thị chưa có ca thật để đo.
- 129 dẫn chiếu còn chờ vì văn bản đích chưa có trong kho.
