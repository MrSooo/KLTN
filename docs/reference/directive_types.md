# Các loại thay đổi pháp lý (loại chỉ thị 1–26)

Bước 2.3 (đọc chỉ thị, `src/directives.py`, `src/directives_rare.py`) và bước 2.4 (áp lên phiên bản, `src/versions.py`) xử lý 26 loại thay đổi. Mã nguồn và test tham chiếu loại theo số trong bảng này. Câu chỉ thị không thuộc loại nào thì ghi cờ `unknown_directive` và báo lỗi, không đoán.

Hiệu lực là nửa khoảng `[effective_from, effective_to)`. Nút không bao giờ bị xoá; đóng phiên bản bằng `effective_to`.

## Loại có ca thật trong kho

| # | Loại | Ca trong kho | Cách xử lý |
|---|---|---|---|
| 1 | Sửa đổi, bổ sung khoản hoặc điểm "như sau" | ND_70 Điều 1 khoản 1–11 | Khối trích dẫn thành cây Điều/Khoản/Điểm, thay đơn vị đích, đóng con cũ không còn trong khối |
| 2 | Bổ sung khoản, điểm hoặc Điều mới (kể cả hậu tố chữ) | ND_70 "Bổ sung khoản 3 Điều 6"; VBHN_125 khoản 8a Điều 154 | Thêm đơn vị; cha không tồn tại hoặc mã đã có là lỗi |
| 3 | Thay cụm từ tại nhiều vị trí | ND_70 Điều 1 khoản 13 | Khớp mềm (khoảng trắng, dấu thanh, hoa/thường); cụm không thấy thì ghi vào danh sách "không khớp", không làm lỗi cả bước |
| 4 | Bãi bỏ điểm, khoản hoặc đoạn | ND_70 Điều 1 khoản 14, Điều 2 | Đóng phiên bản; đích ngoài kho thì ghi quan hệ chờ đích |
| 5 | Thay cả văn bản qua điều hiệu lực | ND_12 thay ND_28; ND_283 thay ND_12 | Đóng cả cây đơn vị tại ngày nêu trong câu, cạnh `replaces`; đích ngoài kho thì chờ đích |
| 6 | Văn bản hướng dẫn mới lấp điều khoản giao chi tiết | ND_135, ND_145, ND_152, TT_09, TT_10 | Cạnh `details`, `filled_by` (bước 2.2) |
| 7 | Văn bản hướng dẫn văn bản hướng dẫn (ba tầng) | TT_18 → ND_145 Điều 68 khoản 2 → BLLĐ | Chuỗi cạnh `based_on` |
| 8 | Bổ sung danh mục, không sửa chữ cũ | TT_19 → TT_11 | Khớp qua tên danh mục (cần đúng một phụ lục khớp), cạnh `supplements_list`; dòng cũ không đổi phiên bản |
| 9 | Quy định chuyển tiếp | ND_12 Điều 63; ND_70 Điều 3; ND_283 Điều 67; ND_219 Điều 34 | Nhãn `effect_transition` ở bước 1.4 là nguồn tìm câu chỉ thị |
| 10 | Hết hiệu lực theo chủ đề | ND_219 Điều 35 khoản 2 | Regex trên tiêu đề Chương: chương có chủ đề thì đóng, chương chung thì `suspended` kèm cờ `topic_uncertain`, chương khác giữ nguyên |
| 11 | Hiệu lực có điều kiện: trạng thái chờ | ND_283 Điều 66 khoản 2, 3 | `pending_event`, `effective_from = null`, lưu nguyên văn sự kiện, cạnh `pending_on` |
| 12 | Hiệu lực có điều kiện: văn bản kích hoạt | (trong kho: phải vẫn chờ) | Khớp khi đủ ba điều kiện: cùng loại văn bản, mọi số hiệu nêu đều có trong chữ, cụm mô tả nằm trong Điều 1 của văn bản mới (dài từ 12 ký tự sau chuẩn hoá); cạnh `triggers` |
| 13 | Hiệu lực có thời hạn, tự hết khi có văn bản thay | NQ_66-16 Điều 19 | `effective_to` là ngày sau "đến hết ngày X"; cạnh `ends_when_replaced` |
| 14 | Áp dụng thay văn bản khác trong thời hạn | NQ_66-16 Điều 19 khoản 3 | Cạnh `overrides` từ mục phụ lục I.7 tới các Điều nêu ở tiêu đề mục |
| 15 | Cập nhật cấp luật qua bản hợp nhất | VBHN_125 | Không tạo nút riêng; so từng đơn vị với BLLĐ gốc theo chữ chuẩn hoá; ngày hiệu lực lấy từ chú thích; khác biệt không do luật sửa thì cờ `consolidation_discrepancy` |
| 17 | Ban hành nhưng chưa có hiệu lực tại ngày hỏi | ND_145, ND_283 | Trạng thái `not_yet` |
| 18 | Văn bản dưới luật ban hành theo luật cũ còn áp dụng | ND_90, ND_28 (theo BLLĐ 2012) | Cờ `law_2012_era_document`, không nối vào số Điều của BLLĐ 2019 |

## Loại đã cài đặt nhưng kho không có ca thật

Kiểm bằng ví dụ tự soạn ngắn trong `tests/test_directives_rare.py`; không có dữ liệu thật để đo.

| # | Loại | Cách xử lý |
|---|---|---|
| 16 | Văn bản bãi bỏ một phần phụ lục của văn bản khác | Hàm `repeal_appendix`: đóng phần phụ lục bị bãi bỏ |
| 19 | Hồi tố (`applies_from` sớm hơn `effective_from`) | Dùng bản mới cho ngày sự việc trong khoảng hồi tố; nếu câu nêu trách nhiệm pháp lý mới hoặc nặng hơn thì không áp, cờ `retroactive_blocked` |
| 20 | Đính chính văn bản | Không tạo phiên bản pháp lý; ghi chữ trước và sau vào `corrections.jsonl`, cạnh `corrects` |
| 21 | Tạm ngưng hiệu lực hoặc đình chỉ thi hành | `suspended` từ D1, trở lại `normal` từ D2 + 1 ngày; không có D2 thì để mở |
| 22 | Đánh số lại điều, khoản ("… trở thành …") | Đóng mã cũ, mở mã mới với chữ cũ, cạnh `renumbered_to` |
| 23 | Danh sách số trần ("Điều 5, 6 và 8") | Tách thành từng đích ở bước 1.2 (`refs.find_refs`, `chain_targets`) |
| 24 | Văn bản bị cơ quan có thẩm quyền bãi bỏ vì trái luật | Như loại 5, kèm cờ `annulled` |
| 25 | Văn bản được hướng dẫn bị sửa đổi hoặc thay thế | Không tự đóng văn bản hướng dẫn; cờ `parent_changed` |
| 26 | Thay cả văn bản bằng văn bản cùng tên (không có điều hiệu lực nêu rõ) | Không tự đóng; cờ và cạnh `possible_replacement` (so tên theo cột `ten_ngan` của manifest) |
