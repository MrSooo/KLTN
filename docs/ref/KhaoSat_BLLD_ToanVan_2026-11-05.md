# Khảo sát Bộ luật Lao động trên toàn văn học viên gửi (5/11/2026): BẢN CẮT 07/11/2026

**Bản cắt.** Đã bỏ mọi phần nêu dữ kiện về văn bản thuộc nhóm đo (heldout): đoạn "Đã chốt", mục 1 (bảng quy mô, đã có ở `data/raw/labor/manifest.csv`), phần bản hợp nhất mới ở mục 2, chuỗi lương tối thiểu sau 2024 ở mục 6, một ý ở mục 5. Số mục giữ nguyên để plan trỏ "mục 4" vẫn đúng. Bản đầy đủ do học viên giữ ngoài repo. Plan là chuẩn; lệch với plan hoặc manifest thì theo plan và manifest.

**Nguồn:** các file .txt học viên gửi 5/11, phần trong kho dev: BLLĐ gốc 45/2019/QH14, 125/VBHN-VPQH (27/8/2025), NĐ 145/2020, 152/2020, 70/2023, 219/2025, 74/2024, 12/2022, 283/2026. Đếm và so bằng script trên toàn văn. Nhãn: **[Văn bản HV cung cấp]** = đọc từ file, chưa đối chiếu bản PDF Công báo.

## 2. Phiên bản Bộ luật (45/2019 → 125/VBHN, từng điều)

- Thay đổi pháp lý duy nhất giữa hai bản: Điều 154 thêm khoản 8a (Luật 71/2025, hl 01/01/2026). Bước phát hiện thay đổi phải chuẩn hoá chữ trước khi so, nếu không M3 bị thổi phồng.
- **Bản hợp nhất cũng sai:** 125/VBHN ghi "các điều 89, 193 và 197" ở khoản 4 Điều 185 (gốc là 189). → VBHN không phải nhãn vàng tuyệt đối.
- Chú thích trong 125: Luật 71/2025 Điều 50 khoản 3 tự đặt quy tắc áp dụng khi xung đột (áp dụng luật này, trừ văn bản khác ưu đãi hơn thì áp dụng mức có lợi nhất) → ca thật của quy tắc áp dụng riêng do Quốc hội đặt.

> **[Bổ sung 07/11/2026, Claude, script trên `data/raw/labor/`]** Sau khi chuẩn hoá thô (NFC, gộp khoảng trắng, bỏ dấu chấm cuối, thống nhất kiểu bỏ dấu, bỏ `[n]`), BLLĐ gốc và 125/VBHN vẫn khác ở **8 Điều**, không chỉ 154 và 185:
> - Điều 42 khoản 2: bản 125 mất đánh dấu điểm `a)`, `b)` (hai điểm bị dồn vào cùng dòng với đầu khoản). Parser sẽ thấy hai điểm biến mất.
> - Điều 73: "Trung ương" → "trung ương" (viết hoa).
> - Điều 125: "ngày hoặc" → "ngàyhoặc" (dính chữ).
> - Điều 143: gạch ngang `-` → `–`.
> - Điều 219: thêm khoảng trắng sau dấu `“` trong khối trích dẫn ("“ Điều 54.").
> - Điều 220: bản 125 nối thêm "Nơi nhận", chữ ký và chú thích vào cuối.
> - Điều 154: khoản 8a (thay đổi thật). Điều 185: "189" → "89" (lỗi bản hợp nhất).
>
> Chưa kiểm chứng: danh sách này là kết quả của chuẩn hoá thô; chưa chạy parser thật. Quy tắc chuẩn hoá ở plan L6 chưa đủ cho 6 trong 8 chỗ trên.

## 3. Ngoại lệ trong BLLĐ (toàn văn, 220 điều)

42 cụm: 11 loại thỏa thuận khác, 16 ngoại lệ trong cùng điều/luật khác, 15 dẫn chiếu khoản/điều. Chéo điều: 14→18, 145, 162; 34→177; 35→29, 97; 37→36; 45→34; 46→36; 85→84; 151→154.

## 4. Bản đồ giao quyền (slot)

39 cụm ở 37 điều: Chính phủ ở 12, 21, 46, 47, 51, 54, 63, 68, 76, 84, 85, 91, 92, 96, 98, 107, 113, 116, 118, 122, 130, 131, 135, 150, 157, 161, 169, 172, 174, 176, 184, 185, 209, 210; Bộ trưởng ở 21, 73, 145, 147. Điều 218 miễn giảm thủ tục; 219 sửa luật khác (văn bản trong ngoặc kép có tiêu đề "Điều …", regex phải bỏ qua); 220 hiệu lực.

## 5. Chuỗi miễn giấy phép lao động: ba phiên bản (phép thử đã qua)

Điều 151 → trừ Điều 154 (9 khoản, khoản 1–2 và 9 giao Chính phủ; khoản 8a thêm 01/01/2026) → Điều 7 nghị định:

| Trường hợp | NĐ 152 (2021) | NĐ 70/2023 | NĐ 219/2025 |
|---|---|---|---|
| Quản lý/chuyên gia/kỹ thuật làm ngắn hạn | dưới 30 ngày **và** không quá 3 lần/năm | giữ | **tổng dưới 90 ngày/năm** (khoản 13a) |
| Học sinh, sinh viên | đang học ở nước ngoài, có thỏa thuận thực tập | giữ | thêm **đang học ở Việt Nam**, thêm thư mời làm việc |
| Giảng dạy tại cơ sở giáo dục của cơ quan đại diện | giảng dạy, nghiên cứu ở trường quốc tế | thêm nhà quản lý, giám đốc điều hành | giữ |
| Bộ GD&ĐT xác nhận | giảng dạy, nghiên cứu | thêm quản lý, hiệu trưởng | thêm chuyển giao chương trình quốc tế |
| Lĩnh vực ưu tiên do bộ/UBND tỉnh xác nhận | — | — | **mới** (khoản 15) |
| Kết hôn với người VN (154 khoản 8): chỉ báo cáo hay phải xin xác nhận | chỉ báo cáo | **phải xin xác nhận** | **lại chỉ thông báo** |

Câu có/không lật thật: chuyên gia vào 45 ngày một lần (152: cần GPLĐ → 219: miễn); 4 chuyến × 10 ngày (152: cần → 219: miễn).

Ca mới cho method:
- **Hết hiệu lực theo chủ đề, không theo số điều:** 219 Điều 35 khoản 2 cho hết hiệu lực "nội dung về lao động nước ngoài" của 152; phần người VN làm cho tổ chức nước ngoài còn hiệu lực (khớp NĐ 283 Điều 66 khoản 3). Regex không xác định được điều nào hết hiệu lực.
- **Luật đổi, nghị định chưa theo:** 219 Điều 7 khoản 1 chỉ dẫn khoản 3–8 Điều 154, không có khoản 8a (thêm sau, hl 01/01/2026).
- NĐ 128/2025 bị NĐ 219 (Điều 35 khoản 3) cho hết hiệu lực một phần (Điều 8 và Mục 2 Phụ lục II); văn bản 128 không có trong kho dev.

## 6. Chuỗi khác

- Lương tối thiểu: 38/2022 (ngoài kho) → 74/2024 (vùng I 4.960.000). NĐ 74 có điểm e khoản 3 Điều 3.
- Xử phạt: 28/2020 → 12/2022 → 283/2026.
