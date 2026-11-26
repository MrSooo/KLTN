# Việc của bạn

Thư mục này là toàn bộ thế giới của bạn. Bạn (và mọi subagent bạn tạo) chỉ đọc và ghi trong thư mục này. Không mở thư mục cha hay thư mục nào khác. Không mở, không sửa `tiep.py` và `loi_tiep.txt` (chỉ chạy `tiep.py`). Không tìm hiểu dữ liệu đến từ đâu hay dùng vào việc gì: bạn không cần biết, và biết sẽ làm lệch kết quả.

Việc gồm nhiều LƯỢT nối tiếp. Mỗi lượt là một file `lo/NNN.json`: danh sách cụm chữ cần đặt tên. Lượt sau phụ thuộc kết quả lượt trước, nên `lo/` chỉ có các lượt đã tới và `tiep.py` dựng lượt kế. Không bao giờ làm hai lượt cùng lúc.

## Vòng lặp (bạn là phiên chính; bạn KHÔNG tự làm lượt nào)
1. Chạy `C:/Users/TusPC/Documents/kltn/.venv/Scripts/python.exe tiep.py moi`. Nó in đúng một dòng:
   - `LƯỢT NNN ...` hoặc `CHỜ NNN ...`: sang 2 với số NNN đó.
   - `THIẾU NHẬT KÝ NNN ...`: làm 3 cho lượt NNN rồi sang 4.
   - `HẾT ...`: việc xong; báo người dùng và dừng.
   - `DỪNG ...` hoặc dòng nào khác: dừng ngay, chép nguyên dòng đó cho người dùng, không làm gì thêm.
2. Giao lượt NNN cho MỘT subagent MỚI (Agent tool), đặt tường minh tham số model `deepseek-v4.1-flash` và effort `khong_co`. Không tạo được subagent, hoặc không đặt được model hay effort, thì dừng và báo người dùng. Lời giao chỉ gồm đúng thế này (thay NNN):
   > Đọc `system.txt`, `schema.json` và `lo/NNN.json` trong thư mục làm việc. Làm đúng theo `system.txt` cho danh sách trong `lo/NNN.json` và ghi kết quả vào `out/NNN.json` là JSON thuần đúng lược đồ trong `schema.json` (đúng tên trường, không đổi tên, không thêm trường). Không đọc hay ghi file nào khác. Cuối cùng chỉ trả lời đúng một dòng: NNN, một ký tự tab, rồi ID model chính xác của bạn.
3. Thêm vào CUỐI `nhat_ky.tsv` (tạo file nếu chưa có) một dòng: dòng trả lời của subagent, một ký tự tab, rồi `khong_co`. Tức là `NNN<tab>ID model<tab>khong_co`. Ghi đúng ID subagent trả, kể cả khi nó khác `deepseek-v4.1-flash`. Không sửa dòng cũ.
4. Chạy `C:/Users/TusPC/Documents/kltn/.venv/Scripts/python.exe tiep.py ghi NNN`. Nó in đúng một dòng:
   - `ĐÃ NHẬN NNN ...`: quay lại 1 (nếu dòng có thêm `HẾT` hay `DỪNG` thì làm theo phần đó như ở 1).
   - `SAI HÌNH NNN ...`: đầu ra đã được cất sang `out_sai/`; giao lại lượt NNN cho một subagent MỚI như 2, rồi làm 3 và 4.
   - `THIẾU NHẬT KÝ NNN ...`: làm 3 rồi chạy lại 4.
   - `DỪNG ...` hoặc dòng nào khác: dừng ngay, chép nguyên dòng đó cho người dùng.

Chia việc qua nhiều phiên là bình thường: phiên mới đọc file này rồi bắt đầu từ 1; `tiep.py` tự biết đang ở lượt nào.

## Model
Subagent phải là model `deepseek-v4.1-flash` (tham số model `deepseek-v4.1-flash`), effort `khong_co`.

## Cấm
- Không viết script, regex hay công cụ nào để sinh hoặc sửa đầu ra. Mọi tên do subagent đọc chữ mà chọn.
- Không sửa `lo/`, `out/`, `out_sai/`, `system.txt`, `schema.json`, `tiep.py` (chỉ subagent ghi `out/NNN.json` của lượt nó được giao).
- Không chạy lại một lượt đã nhận. Không đọc nhiều lượt cùng nhau để so sánh hay làm cho đều.

## Khi dừng
Báo người dùng: số lượt đã nhận, nguyên văn dòng cuối `tiep.py` in, lượt nào lỗi.
