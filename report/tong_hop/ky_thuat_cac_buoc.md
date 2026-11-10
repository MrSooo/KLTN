# Kỹ thuật các bước đã làm

*Số liệu ngày 09/11/2026, lấy từ báo cáo chạy ở `docs/bao_cao_chay/`.*

**Mục tiêu.** Biến Bộ luật Lao động 45/2019 và 17 văn bản dưới luật (10 nghị định, 5 thông tư, 1 nghị quyết, 1 bản hợp nhất) thành cơ sở tri thức **thích nghi theo ngày hiệu lực**. Mỗi văn bản là một sự kiện nạp: nạp vào thì tạo phiên bản mới cho đơn vị bị sửa và đóng phiên bản cũ. Chọn một ngày thì thấy đúng bản có hiệu lực ngày đó.

## Các bước

| Bước | Làm gì | Cách làm | Kết quả |
|---|---|---|---|
| L0 | Nền | Đọc bảng văn bản (số hiệu, ngày ban hành, ngày hiệu lực, cấp). Lớp gọi LLM có cache và hạn mức. Chạy cả chuỗi bằng một lệnh | 18 văn bản |
| L1 | Tách cấu trúc | Văn bản `.txt` thành cây Chương / Mục / Điều / Khoản / Điểm, cùng phụ lục và bảng lương. Khối trích dẫn trong văn bản sửa đổi tách riêng | 10.202 đơn vị, 893 Điều (tính cả bản hợp nhất, vốn lặp lại 220 Điều của Bộ luật); số Điều khớp bảng văn bản 18/18 |
| L2 | Cạnh cấu trúc và dẫn chiếu | Cạnh cha-con. Dẫn chiếu "Điều X khoản Y" trong và giữa các văn bản (chọn Bộ luật 2012 hay 2019 theo dòng "Căn cứ"). Đích chưa nạp thì ghi "chờ đích" | 2.348 dẫn chiếu; 129 chờ đích; 127 không giải được (đều có lý do) |
| L3 | Điều khoản giao chi tiết | Tìm trong Bộ luật các điều giao cho văn bản dưới luật quy định chi tiết (5 dạng A-E), rồi nối văn bản hướng dẫn về đúng điều. Văn bản không nêu số Điều thì dùng từ khoá và hai model LLM | 51 điều khoản; 10 cạnh căn cứ; 48 cạnh hướng dẫn |
| L4 | Phân loại Điều | Nhãn: nội dung chính, định nghĩa, thẩm quyền, thủ tục, chuyển tiếp hiệu lực, phụ lục. Mẫu tiêu đề trước, LLM xử lý phần còn lại theo lô | 921 nhãn: 151 theo mẫu, 714 do LLM, 28 nhãn tạm (model kiểm không đồng ý), 28 phụ lục |
| L5 | Ngoại lệ | *Tường minh*: cụm dẫn chiếu ngay trước "không áp dụng", hoặc "trừ ... sau đây:". *Chung*: "..., trừ trường hợp X" thành nút điều kiện | 23 cạnh tường minh; 336 cạnh và 128 nút điều kiện (chung) |
| L6 | Phiên bản theo ngày hiệu lực | Nạp từng văn bản theo ngày hiệu lực. Câu chỉ thị được đọc từ chính chữ văn bản (không dùng cột quan hệ của bảng văn bản), rồi sửa hoặc đóng phiên bản. Gồm 26 loại, xem bên dưới | 9.217 đơn vị, 9.343 phiên bản, 260 cạnh cập nhật; 15/15 mốc kiểm đạt; 0 chỉ thị lạ |
| checks | Kiểm độc lập | Đếm lại bằng bộ đếm riêng, đối chiếu bảng văn bản và các mốc của kế hoạch | 6 nhóm kiểm, 0 lỗi |
| graph | Đồ thị gộp | Hợp mọi cạnh, mỗi nút kèm khoảng hiệu lực | 9.364 nút, 2.721 cạnh ngữ nghĩa |
| viewer | Trang xem | Một file HTML mở offline, chọn ngày để thấy đồ thị lúc đó | `data/processed/viewer/do_thi.html` |

## 26 loại chỉ thị (L6)

- **17 loại có ca thật** trong 18 văn bản: sửa hoặc bổ sung "như sau" (1, 2), thay cụm từ (3), bãi bỏ (4), thay cả văn bản (5), văn bản hướng dẫn lấp điều khoản giao (6) và chuỗi hướng dẫn 3 tầng (7) (cả hai nối ở L3), bổ sung danh mục (8), chuyển tiếp (9, giữ thành đơn vị), hết hiệu lực theo chủ đề (10), hiệu lực có điều kiện chờ sự kiện (11), có thời hạn (13), áp dụng thay trong thời hạn (14), bản hợp nhất (15), chưa có hiệu lực tại ngày hỏi (17), ban hành theo luật cũ (18), danh sách số trần "Điều 5, 6 và 8" (23, tách ở L2).
- **9 loại chưa có ca thật**: kích hoạt hiệu lực có điều kiện (12), bãi bỏ một phần phụ lục (16), hồi tố (19), đính chính (20), tạm ngưng (21), đánh số lại (22), bị bãi bỏ vì trái luật (24), văn bản được hướng dẫn bị sửa (25), thay cả văn bản cùng tên (26). Đã cài đặt và kiểm bằng ví dụ tự soạn (22 test), ghi rõ là "chưa đo trên dữ liệu thật".
- Câu chỉ thị không thuộc loại nào thì báo lỗi `unknown_directive`, không đoán (hiện 0 ca).

## Tầng LLM

- Gemini, hai model nhẹ: `gemini-3.5-flash-lite` đề xuất, `gemini-3.8-flash` kiểm độc lập.
- Đề xuất không được áp thẳng. Nhãn L4 đẩy một Điều ra khỏi "nội dung chính" phải được model kiểm xác nhận, không thì trả về nhãn tạm. Cạnh L3 chỉ được giữ khi hai model và kiểm từ khoá cùng đồng ý, nếu không thì cạnh vẫn ghi nhưng bị cô lập.
- Mọi phản hồi lưu cache nên chạy lại cho cùng kết quả mà không tốn lượt; hết hạn mức thì dừng gọn, hôm sau chạy tiếp.

## Nguyên tắc chung

- Chữ của văn bản là nguồn duy nhất; không khớp mẫu nào thì báo lỗi, không đoán.
- Mỗi bước có số đối chiếu cứng; chuỗi phiên bản (L6) chạy lại hai lần ra file giống hệt (có test).
- 120 test (phần LLM kiểm bằng API giả). Chạy toàn bộ: `python -I src/run_all.py --viewer --tests`, khoảng 12 giây.

## Chưa làm

- L7-L11: sổ khái niệm, ngoại lệ ngầm, trích quy tắc, trả lời câu hỏi, đo.
- 129 dẫn chiếu đang chờ vì văn bản đích chưa có trong kho.
