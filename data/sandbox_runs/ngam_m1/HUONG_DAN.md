# Việc của bạn

Thư mục này là toàn bộ thế giới của bạn. Bạn (và mọi subagent bạn tạo) chỉ đọc và ghi trong thư mục này. Không mở thư mục cha hay thư mục nào khác, không tìm hiểu dữ liệu đến từ đâu hay dùng vào việc gì.

Có 024 lô trong `lo/` (`001.json` đến `024.json`). Với mỗi lô, làm đúng theo `system.txt`, ghi kết quả vào `out/` cùng số.

## Model
Việc này phải do model `deepseek-v4.1-flash` làm, mức effort `khong_co`. Mỗi subagent đặt tường minh model (tên tắt `deepseek-v4.1-flash`) và effort `khong_co`. Không đặt được thì dừng và báo người dùng.

## Chia việc
Chia các lô thành khối liền nhau, mỗi khối tối đa 20 lô; mỗi khối giao cho MỘT subagent mới, song song tối đa 4. Lời giao (thay AAA, BBB):
> Đọc `system.txt` một lần. Rồi lần lượt với từng lô NNN từ AAA đến BBB mà `out/NNN.json` chưa có: đọc `lo/NNN.json`, làm đúng theo `system.txt`, ghi kết quả vào `out/NNN.json` là JSON thuần đúng khuôn ở mục "ĐẦU RA" của `system.txt`. Mỗi lô xét riêng. Không đọc hay ghi file nào khác. Cuối cùng trả lời mỗi lô một dòng: NNN, một ký tự tab, rồi ID model chính xác của bạn.

Bạn (phiên chính) KHÔNG tự làm lô nào. Ghi các dòng trả lời vào `nhat_ky.tsv` (dạng `NNN<tab>ID model`).

## Cấm
- Không viết script, regex hay công cụ nào để sinh hoặc sửa đầu ra.
- Không sửa `out/NNN.json` sau khi subagent đã ghi.

## Xong
Báo: số file đã ghi, nội dung `nhat_ky.tsv`, lô nào lỗi.
