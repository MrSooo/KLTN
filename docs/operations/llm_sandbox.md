# Vận hành: chạy phần LLM bằng phiên Claude Code trong thư mục làm việc ngoài repo

Áp dụng cho bước 1.6 (A36). Phần LLM không gọi API: một phiên Claude Code đóng vai LLM trong **thư mục làm việc ngoài repo** (gọi là "thư mục làm việc" ở dưới), mỗi lô giao cho một subagent mới. Máy (mã của repo) dựng đầu vào, kiểm và ghi bản ghi cache. Thư mục làm việc **không** đưa vào repo và có thể dựng lại bất cứ lúc nào.

## 1. Nguyên tắc
- Thư mục làm việc nằm **ngoài repo**, tên trung tính, chưa có hoặc rỗng. Phiên Claude Code mở **trong thư mục đó**, không `--resume`, không `-c`, nên không nạp tài liệu của dự án; cách ly này dựa trên hướng dẫn trong thư mục, không có gì chặn kỹ thuật nếu phiên cố tình đọc thư mục cha.
- Chữ lời nhắc của bước (`SYSTEM`) và lược đồ nằm trong khoá cache của mọi bản ghi. **Sửa một chữ sau khi đã dựng thư mục là phải dựng lại thư mục mới**; `nhap` từ chối thư mục dựng với lời nhắc khác code.
- Lời khai model và effort của subagent trong `nhat_ky.tsv` là lời tự khai, máy không kiểm được. Bản ghi không có `request_id` và `usage`.
- Mỗi subagent đặt tường minh model (tên tắt) và effort; phiên chính chỉ điều phối, không tự làm lô nào. Không chạy lại một lô trừ khi người vận hành bảo.
- Không chạy `--llm live` khi chưa được phép (tốn hạn mức hoặc tiền).

## 2. Bước 1.6A mới (`src/propositions.py`)
Đường chạy đã chốt (A39): Sonnet 5.5, effort `high`, khối tối đa 20 lô mỗi subagent, song song tối đa 4, lời nhắc `menh-de-3`.

1. **Dựng thư mục** (ở gốc repo, thư mục đích ngoài repo):
   ```
   python -X utf8 -I src/propositions.py xuat <thư mục> claude-sonnet-5-5 high --tat-ca
   ```
   Thư mục chứa `HUONG_DAN.md`, `system.txt`, `cau_hinh.json`, `lo/001.json` đến `lo/204.json` và `out/` rỗng. Bỏ `--tat-ca` thì dựng bộ thí điểm 30 đơn vị.
2. **Mở phiên Claude Code mới trong thư mục đó** (`cd <thư mục>`, rồi `claude`). Cho phép Agent tool và ghi file trong thư mục. Giao: "Đọc HUONG_DAN.md và làm theo." Phiên tự chia lô thành khối, giao từng khối cho subagent, ghi `out/NNN.json` và dòng `nhat_ky.tsv` (số lô và ID model, cách nhau bằng tab). Hết hạn mức giữa chừng: mở phiên mới và giao lại cùng câu; phiên bỏ qua lô đã có `out/NNN.json`.
3. **Luật dừng sau 3 khối đầu (60 lô):** nếu có câu dẫn lọt thành `menh_de` hoặc lỗi cổng còn lại vượt 5% số dòng thì dừng và báo; không tự sửa lời nhắc.
4. **Nhập vào repo** (ở gốc repo, nhập được nhiều lần):
   ```
   python -X utf8 -I src/propositions.py nhap <thư mục>
   ```
   Kiểm hình, cổng nguyên văn, cổng âm tiết; từ chối lô sai hình, lô thiếu dòng nhật ký, lô mà model tự khai khác `cau_hinh.json`; ghi `data/llm_cache/propositions/<doc_id>.json` (với `--tat-ca`) hoặc `data/pilot_propositions/llm_output.json` (bộ thí điểm).
5. **So với đáp án thí điểm** (chỉ với bộ 30 đơn vị): `python -X utf8 -I src/propositions.py so`.
6. Đo ba số nghiệm thu của A39 và ghi vào `docs/status.md`.

## 3. Bước 1.6B (`src/concepts_names.py`)
Đang phải viết lại để đọc mệnh đề (`names-2`, A39). Cơ chế thư mục làm việc của bản cũ vẫn là mẫu cho bản mới và được giữ trong mã: `--xuat <thư mục>` dựng thư mục; trong thư mục có `tiep.py` (mỗi lệnh dựng lại trạng thái bằng cách gấp các `out/` theo thứ tự; mỗi `lo/NNN.json` phải trùng từng byte với lượt dựng lại, khác thì dừng); `--nhap <thư mục>` ghi cache; `--de` cho ghi đè. Bước này tuần tự (lượt sau thấy tên của lượt trước), khoảng 76 lượt, subagent Sonnet 5.5, effort `high`. Vận hành chi tiết sẽ viết khi `names-2` được duyệt.

Các dòng `DỪNG ...` mà `tiep.py` in là điều kiện dừng: model hoặc effort khai sai, đầu ra sai hình hai lần ở cùng lượt, `lo/` bị sửa, `system.txt` hay `schema.json` khác bản trong repo, hoặc lỗi dựng lượt (traceback ở `loi_tiep.txt`). Người vận hành xử lý, không để phiên tự sửa.

## 4. Giới hạn
- Cách ly dựa vào hướng dẫn trong thư mục; thư mục cha vẫn đọc được nếu phiên cố tình.
- Model và effort do phiên tự khai; effort không nằm trong khoá cache nên hai lần chạy khác effort mà cùng chữ thì `replay` không phân biệt.
- Bản ghi không dựng lại được bằng API.
- Lược đồ đầu ra được đưa cho subagent đọc chứ không bị ép: đầu ra sai hình thì giao lại một lần.
- Phụ thuộc chuỗi: đổi đầu ra của 1.2, 1.4, 1.5, 1.6A, hay `ten.model`, hay lời nhắc thì khoá đổi từ lượt bị ảnh hưởng trở đi; phải chạy lại từ đó trong thư mục mới.
