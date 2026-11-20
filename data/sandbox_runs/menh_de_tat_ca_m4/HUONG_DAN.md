# Việc của bạn

Thư mục này là toàn bộ thế giới của bạn. Bạn (và mọi subagent bạn tạo) chỉ đọc và ghi trong thư mục này. Không mở thư mục cha hay thư mục nào khác, không tìm hiểu dữ liệu đến từ đâu hay dùng vào việc gì.

Có 204 lô trong `lo/` (`001.json` đến `204.json`). Với mỗi lô, làm đúng theo `system.txt`, ghi kết quả vào `out/` cùng số (`out/001.json` cho `lo/001.json`).

## Model
Việc này phải do model `deepseek-v4.1-flash` làm, mức effort `khong_co`. Mỗi subagent đặt tường minh cả model (tên tắt `deepseek-v4.1-flash`) và effort `khong_co`. ID model chính xác của subagent khác `deepseek-v4.1-flash`, hoặc không đặt được effort, thì dừng lại và báo người dùng, đừng làm.

## Chia việc theo khối
Chia các lô cần làm thành các KHỐI liền nhau, mỗi khối tối đa 20 lô, theo thứ tự số lô. Mỗi khối giao cho MỘT subagent mới (Agent tool), đặt tham số model và effort tường minh như ở trên, chạy song song tối đa 4 subagent. Không tạo được subagent hoặc không đặt được model, effort thì dừng và báo người dùng.

Lời giao cho subagent (thay AAA, BBB bằng lô đầu và cuối của khối), chỉ gồm đúng thế này:
> Đọc `system.txt` một lần. Rồi lần lượt với từng lô NNN từ AAA đến BBB mà `out/NNN.json` chưa có: đọc `lo/NNN.json`, làm đúng theo `system.txt`, ghi kết quả vào `out/NNN.json` là JSON thuần đúng khuôn ở mục "Đầu ra" của `system.txt` (đúng tên trường, không thêm trường, trường rỗng thì bỏ). Mỗi lô xét riêng theo chữ của lô đó. Không đọc hay ghi file nào khác, không đọc lại `out/` của lô khác. Cuối cùng trả lời mỗi lô một dòng: NNN, một ký tự tab, rồi ID model chính xác của bạn.

Bạn (phiên chính) KHÔNG tự làm lô nào. Ghi các dòng trả lời vào `nhat_ky.tsv` (một dòng mỗi lô, dạng `NNN<tab>ID model`).

## Cấm
- Không viết script, regex hay công cụ nào để sinh hoặc sửa dòng. Mọi dòng do model đọc chữ mà viết.
- Không sửa `out/NNN.json` sau khi subagent đã ghi. Không chạy lại một lô trừ khi người dùng bảo.

## Xong
Báo: số file đã ghi, nội dung `nhat_ky.tsv`, lô nào lỗi.
