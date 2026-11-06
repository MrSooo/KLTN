# Hướng dẫn làm sổ khái niệm (R1–R4), bản chi tiết, 3/11/2026

Quy tắc gốc nằm ở `ban_giao_bat_dau_lam_2026-10-17.md` mục 3B và mục 5. Chỗ thêm cho rõ, không có trong bàn giao, đánh dấu **[thêm]**. Quy ước đề xuất tạm cho phép thử đánh dấu **[quy ước tạm]**. Cả hai chốt lại sau phép thử 5 điều.

Ví dụ làm trên **Điều 619**, vì Điều 619 không nằm trong 5 điều thử (621, 626, 644, 650, 651), nên không chép được đáp án.

Chữ của Điều 619 trong ví dụ viết theo trí nhớ: [Chưa kiểm chứng]. Hai chỗ khớp với tài liệu trong project: Điều 619 có nhánh "được coi là chết cùng thời điểm do không xác định được ai chết trước" (`PhepThu_DoPhuDanChieu`, Phép thử 4, dòng 6), và có ngoại lệ thế vị trỏ tới Điều 652 (`tong_hop_cong_viec`, bước A6). Khi làm thật, chép chữ từ file của học viên, không từ ví dụ này.

## 0. Đầu ra

Hai bảng, cho 5 điều 621, 626, 644, 650, 651, dùng chung một sổ:
- **Bảng R3:** mỗi dòng một cụm chữ trong một đơn vị luật.
- **Sổ vị từ:** mỗi dòng một vị từ.

Thời gian: bàn giao ước khoảng 10 phút một điều. Các điều dày (621, 650, 651) có thể gấp 2–3 lần [Suy luận], nên tính 1–3 giờ cả đợt, chia 2–3 buổi.

## 1. Chuẩn bị

1. Mở `data/raw/blds2015_p4.md` hoặc `a1_triples_blds2015_p4.jsonl`. Cột mã đơn vị dùng mã của A1 (`BLDS2015.D621.K1.a`). Khoản có điểm: câu dẫn của khoản thuộc đơn vị khoản, mỗi điểm là một đơn vị riêng.
2. Mở bảng 19 khái niệm trong `PhepThu_DoPhuDanChieu` (mục "Bảng chi tiết"). Bảng cho sẵn điều định nghĩa của các khái niệm hay dùng (thời điểm mở thừa kế → 611, không được quyền hưởng di sản → 621, chết cùng thời điểm → 619, di chúc hợp pháp → 630, người thừa kế → 613…). Dùng làm gợi ý cho R1, phải xác nhận lại bằng văn bản.
3. Hai bảng trống (Excel hoặc Sheet), cột ở mục 5.

## 2. Từ vựng cố định

- **Vị từ:** tên một mệnh đề trong quy tắc. Viết tiếng Anh, `snake_case`.
- **Tham số theo vai, thứ tự cố định:** người làm hành vi đứng trước, đối tượng đứng sau. Tên đã dùng ở `GiaiThich_KhaiNiem` mục 5 và 8.3:

| Vai | Nghĩa | Ví dụ |
|---|---|---|
| X | người đang xét, thường là người thừa kế | `convicted_of_harming(X, T)` |
| Y | người thứ hai, khi điều luật nói về hai người | |
| T | người để lại di sản | `testator_knew_and_kept(T, X)` |
| W | di chúc | `named_in_will(X, W)` |

- **Loại:** `input` là dữ kiện thô người hỏi nêu thẳng. `concept` là kết luận pháp lý, có điều định nghĩa nó (gọi là **neo**).
- **Quy tắc đặt tên [quy ước tạm]:**
  - dạng khẳng định, không tiền tố `not_`, `no_` (phủ định để quy tắc ở bước D lo; "không được quyền hưởng di sản" là `disqualified`);
  - không có `_or_`, `_and_`, `all_`, `any_` trong tên. Tên như `all_will_heirs_invalid_or_disclaimed` là dấu hiệu điều kiện gộp có lượng từ, chỗ Gemini đã khai báo thành INPUT (Phép thử 2–5). Gặp thì xem mục 7, ca 3;
  - không nhúng số điều vào tên.

## 3. Quy trình cho mỗi đơn vị (R3 là xương sống)

Làm lần lượt từng đơn vị trong điều:

1. Đọc cả đơn vị. Gạch **nguyên văn** mọi cụm thuộc các nhóm sau (R3):
   - chủ thể: "người…", "những người…", "người… mà…";
   - điều kiện: sau "nếu", "khi", "trường hợp", "trong thời hạn", "trước", "sau", "đã", "chưa", "có", "không có";
   - ngoại lệ: "trừ", "không áp dụng", "vẫn";
   - **[thêm]** kết luận chính của đơn vị ("được", "không được", "có quyền", "phải", "bị coi là"). Bàn giao chỉ đòi chủ thể và điều kiện. Kết luận được thêm vì đó là chỗ khái niệm được neo.
2. Mỗi cụm một dòng bảng R3. Cụm chứa hai ý nối bằng "và", ";", "hoặc": theo mục 7, ca 2.
3. Xếp loại từng dòng bằng R1 rồi R2 (mục 4).
4. Tra sổ, đặt tên và tham số theo R4 (mục 4).
5. Ghi vào hai bảng, cập nhật cột "dùng ở" của sổ.

Đơn vị chỉ là câu dẫn, không có điều kiện: không cần dòng.

## 4. R1, R2, R4

### R1: phân loại, câu hỏi là "có điều nào nêu khi nào X đúng không?"

1. Viết X thành một cụm ngắn, không kèm hành vi cụ thể.
2. Tìm trong Điều 609–662:
   - đơn vị có câu "X là…", "… được coi là X", "những người sau đây X";
   - điều có tiêu đề chính là X;
   - dòng tương ứng trong bảng 19 khái niệm.
3. **Có** → `concept`. Neo = mã đơn vị nêu điều kiện (ưu tiên khoản hoặc điểm cụ thể; nêu cả điều thì mã điều).
4. **Không** → `input`.
5. Thuật ngữ định nghĩa ngoài 609–662 (ví dụ năng lực hành vi dân sự) → `input`, ghi chú "ngoài phạm vi" (quy ước phạm vi trong bàn giao).

Lỗi hay gặp: neo vào điều chỉ *dùng* khái niệm, thay vì điều *nêu điều kiện* của nó.

### R2: vị từ đầu vào phải là dữ kiện thô

Phép thử cho mọi dòng `input` và mọi dòng nghi ngờ: giả sử người hỏi nêu thẳng vị từ này là đúng. Nhờ đó mà bỏ qua được một điều luật nào không?
- Có → phải là `concept`. **Phải gọi tên được điều bị bỏ qua.**
- Không gọi tên được → `input`.

| Vị từ | Nếu người hỏi nêu thẳng… | Bỏ qua điều nào | Loại |
|---|---|---|---|
| `convicted_of_harming(X, T)` | "B bị kết án về hành vi cố ý xâm phạm sức khoẻ của A" | không | input |
| `disqualified(X)` | "B không được quyền hưởng di sản" | 621 | concept |
| `has_valid_will(T)` (Phép thử 2, 4) | "A có di chúc hợp pháp" | 630 | concept |
| `all_will_heirs_invalid_or_disclaimed(T)` | "mọi người thừa kế theo di chúc đều không có quyền hưởng hoặc đã từ chối" | 620, 621 | concept (tổng hợp) |
| quan hệ "B là con đẻ của A" | "B là con đẻ của A" | không | input |
| "B là người thừa kế theo pháp luật hàng thứ nhất" | như tên | 651 [Suy luận] | concept |

Chữ báo hiệu `concept` [Suy luận]: "được coi là", "bị coi là", "được xác định là".

### R4: một khái niệm một tên

Trước khi tạo vị từ mới, tra sổ theo ba khoá: (a) cụm tiếng Việt, (b) tên tiếng Anh, (c) chữ ký (số tham số và vai).
- **Cùng nghĩa** → dùng lại tên cũ, thêm cụm tiếng Việt mới vào cột bí danh.
- **Gần nghĩa nhưng rộng hơn hoặc hẹp hơn** → vị từ mới, ghi chú "KHÔNG gộp với P". Ví dụ có thật: `simultaneous_death` (619, chết cùng thời điểm) và `predeceased_or_simultaneous` (652, chết trước hoặc cùng thời điểm) trông giống nhau nhưng khác nghĩa, gộp là sai.
- **Nghi trùng, không chắc** → vị từ mới, cờ "nghi trùng P", không gộp (Q17: chỉ cảnh báo).
- **Chữ ký:** một khái niệm một chữ ký. Lỗi có thật ở Phép thử 2: `has_valid_will/1` (đối số là người chết) và `legal_will/1` (đối số là di chúc) cùng chỉ "di chúc hợp pháp". Đặt theo vai: tính chất của di chúc là `valid_will(W)`; "người chết có di chúc hợp pháp" là quy tắc ở bước D, không phải vị từ thứ hai [Suy luận].
- Cùng một cụm ở hai đơn vị: hai dòng R3, một vị từ.

## 5. Hai bảng

**Bảng R3.** Bốn cột bắt buộc theo bàn giao: mã đơn vị, cụm nguyên văn, vị từ, loại. **[thêm]** id, vai trò (chủ thể, điều kiện, ngoại lệ, kết luận), tham số (R4 cần), ghi chú. Cụm nguyên văn chép đúng từng chữ, kiểm bằng Ctrl+F trên file.

**Sổ vị từ.**

| vị từ | vai (tham số) | loại | neo | bí danh (cụm tiếng Việt) | dùng ở | ghi chú |
|---|---|---|---|---|---|---|

## 6. Ví dụ: Điều 619

Đơn vị `BLDS2015.D619` (diễn giải, [Chưa kiểm chứng]):

> Trường hợp những người có quyền thừa kế di sản của nhau đều chết cùng thời điểm hoặc được coi là chết cùng thời điểm do không thể xác định được người nào chết trước thì họ không được thừa kế di sản của nhau và di sản của mỗi người do người thừa kế của người đó hưởng, trừ trường hợp thừa kế thế vị quy định tại Điều 652 của Bộ luật này.

**Bước 1. Gạch cụm (R3) và xếp loại.**

| # | Cụm nguyên văn | Vai trò | Vị từ | Loại | Ghi chú |
|---|---|---|---|---|---|
| 1 | những người có quyền thừa kế di sản của nhau | chủ thể | `heir(X, Y)` | concept | gọi hai chiều: `heir(X, Y)` và `heir(Y, X)`. Neo 613, cần xác nhận (mục 7, ca 1) |
| 2 | đều chết cùng thời điểm | điều kiện | `died_at_same_time(X, Y)` | input | |
| 3 | được coi là chết cùng thời điểm | điều kiện | `died_simultaneously(X, Y)` | concept | neo 619 |
| 4 | do không thể xác định được người nào chết trước | điều kiện | `order_of_death_unknown(X, Y)` | input | |
| 5 | họ không được thừa kế di sản của nhau | kết luận | `barred_from_inheriting(X, Y)` | concept | neo 619. KHÔNG gộp với `disqualified` (621) |
| 6 | di sản của mỗi người do người thừa kế của người đó hưởng | kết luận phụ | `estate_goes_to_own_heirs(T)` | concept | neo 619. Tách khỏi dòng 5 vì nối bằng "và" |
| 7 | trừ trường hợp thừa kế thế vị quy định tại Điều 652 | ngoại lệ | `inherits_by_substitution(X, T)` | concept | neo 652 |

**Bước 2. Lý do xếp loại (R1, R2).**
- **Dòng 2.** Người hỏi nêu "A và B chết cùng lúc": không bỏ qua điều nào, vì hệ quả vẫn do Điều 619 quyết → `input`.
- **Dòng 4.** Nêu "không xác định được ai chết trước": vẫn cần Điều 619 để biết hệ quả → `input`.
- **Dòng 3.** Nêu "A và B được coi là chết cùng thời điểm": bỏ qua nhánh định nghĩa ở Điều 619 → `concept`. Chữ "được coi là" là dấu hiệu. Cụm "do không thể xác định…" (dòng 4) là căn cứ thô của khái niệm này, nên tách thành dòng riêng.
- **Dòng 7.** Nêu "C thừa kế thế vị": bỏ qua Điều 652 → `concept`, neo ở 652.
- **Dòng 5, 6.** Chính Điều 619 nêu kết luận (R1) → `concept`, neo 619.
- **Dòng 1.** Có điều nêu khi nào một người là người thừa kế (R1) → `concept`. Neo chưa rõ, xem mục 7 ca 1.

**Bước 3. Sổ vị từ sau Điều 619.**

| vị từ | vai | loại | neo | bí danh | dùng ở | ghi chú |
|---|---|---|---|---|---|---|
| `heir(X, T)` | X người thừa kế, T người để lại di sản | concept | 613 (cần xác nhận) | người thừa kế; có quyền thừa kế di sản của nhau | D619 | |
| `died_at_same_time(X, Y)` | X, Y hai người | input | — | đều chết cùng thời điểm (nghĩa thực tế) | D619 | |
| `order_of_death_unknown(X, Y)` | X, Y hai người | input | — | không thể xác định được người nào chết trước | D619 | |
| `died_simultaneously(X, Y)` | X, Y hai người | concept | D619 | chết cùng thời điểm; được coi là chết cùng thời điểm | D619 | gồm hai nhánh: `died_at_same_time` hoặc `order_of_death_unknown`. Ở 643, 650, 652 cụm "chết cùng thời điểm" mặc định trỏ về vị từ này (`PhepThu`, bảng khái niệm) |
| `barred_from_inheriting(X, Y)` | X không được thừa kế di sản của Y | concept | D619 | không được thừa kế di sản của nhau | D619 | KHÔNG gộp với `disqualified` (621): khác căn cứ |
| `estate_goes_to_own_heirs(T)` | T người để lại di sản | concept | D619 | di sản của mỗi người do người thừa kế của người đó hưởng | D619 | kết luận phụ, bước D mới biết có dùng không |
| `inherits_by_substitution(X, T)` | X người hưởng thế vị | concept | D652 | thừa kế thế vị | D619 | neo ở 652, chưa phân tích Điều 652 |

**Bước 4. Kiểm tay.**
- **C1:** Điều 619 có điều kiện và có dòng. Đạt.
- **C2:** hai vị từ `input` đều có "dùng ở". Đạt.
- **C3:** không `input` nào trùng tên hoặc bí danh với `concept`. Đạt.
- **Đối chiếu A6 [thêm, không tốn thời gian]:** dòng 7 phải có cạnh `exception_of` từ Điều 652 tới Điều 619 trong `a6_exceptions_blds2015_p4.jsonl`. Mọi dòng "ngoại lệ" của bảng R3 nên có cạnh tương ứng ở A3 hoặc A6. Dòng nào không có là một trong hai: khoảng trống của mẫu câu, hoặc ngoại lệ ngầm (bước C).

## 7. Ca khó và quy ước tạm [quy ước tạm]

Ghi số ca gặp được vào ghi chú, để chốt sau phép thử.

1. **Khái niệm định nghĩa rải nhiều điều** (người thừa kế, di chúc hợp pháp): neo = danh sách các đơn vị nêu điều kiện, ghi hết. Không bỏ vị từ vì không chọn được một điều.
2. **Một cụm gồm nhiều hành vi nối bằng "hoặc", ";", "và":** gộp một vị từ khi các vế cùng hệ quả trong cùng một đơn vị. Tách khi (a) điều khác nhắc riêng một vế, hoặc (b) một vế có điều kiện kèm theo mà vế kia không có (như mệnh đề "nhằm hưởng…" chỉ gắn với một vế). Ghi "gộp" hoặc "tách" và lý do vào ghi chú.
3. **Điều kiện gộp có lượng từ** ("tất cả…", "mọi người… đều…"): chỗ Gemini khai báo thành INPUT. Xếp `concept` (tổng hợp), neo = đơn vị chứa nó, ghi cờ "lượng từ" và liệt kê thành phần trong ghi chú. Không khai báo thành `input`.
4. **"được coi là", "bị coi là", "được xác định là":** `concept` (R2).
5. **Thuật ngữ ngoài 609–662:** `input`, ghi "ngoài phạm vi".
6. **Cụm mơ hồ về nghĩa pháp lý** (ví dụ phạm vi "vẫn được hưởng" ở 621.2, Q14): không tự quyết. Ghi "?" vào ghi chú và gom thành danh sách hỏi người có chuyên môn (`SoQuyetDinh` G8).
7. **Mốc thời gian:** có điều định nghĩa (thời điểm mở thừa kế, 611) → `concept`. Còn lại → `input`. So sánh trước hoặc sau là việc của quy tắc ở bước D.

## 8. Giao thức phép thử 5 điều

Mục đích: chốt Q12, tức dùng LLM nháp hay làm tay.

1. **Tay trước.** Làm bảng R3 và sổ cho cả 5 điều (621, 626, 644, 650, 651), **chưa mở** bản LLM nháp. Ghi số phút từng điều.
2. **Chốt ngưỡng trước khi so**, ghi vào file có ngày. Bàn giao đặt: LLM tìm thêm trên 20% cụm → LLM nháp, người chốt; LLM không thêm được gì và làm tay dưới khoảng 10 phút một điều → làm tay. Con số 20% trong bàn giao ghi là "ví dụ", nên chốt cụ thể trước. Khoảng giữa không có quy tắc, nên đặt luôn bây giờ. Đặt ngưỡng sau khi thấy kết quả là lỗi đã gặp ở Phép thử 3.
3. **LLM nháp độc lập.** Cùng hướng dẫn này, cùng cột, cùng 5 điều, không nhận bảng của học viên. Cần xong việc chọn LLM (kế hoạch 2.1) trước bước này.
4. **So.**
   - (a) Cụm LLM có mà tay không có: học viên xem từng cụm, chỉ đếm cụm **hợp lệ** (đáng có dòng). Cụm thừa đếm riêng.
   - (b) Cụm tay có mà LLM thiếu.
   - (c) Khác loại (`input` hay `concept`).
   - (d) Khác tên hoặc bí danh.
   - (e) Khác biệt chỉ do gộp hay tách (mục 7, ca 2) xếp riêng, không tính là "LLM tìm thêm".
5. **Đọc kết quả** theo ngưỡng đã chốt ở bước 2. Phép thử đo số cụm điều kiện, không đo độ đúng pháp lý.

## 9. Tự kiểm bằng tay trước khi gửi

- C1: mỗi đơn vị có điều kiện đều có ít nhất một dòng.
- C2: mỗi `input` có "dùng ở" từ một dòng trở lên.
- C3: không `input` nào trùng tên hoặc bí danh với `concept`.
- C4: là lượt LLM độc lập ở mục 8.

Gửi lại: hai bảng, số phút từng điều, số ca khó theo mục 7, và danh sách dòng "ngoại lệ" không có cạnh ở A3 hoặc A6.

Điều gì sẽ chứng minh hướng dẫn này sai: khi làm 5 điều, cứ hơn 1 trong 10 dòng mà R1 hoặc R2 không xếp được loại (hoặc hai lần xếp cách nhau cho kết quả khác), thì R1–R2 chưa đủ cụ thể và phải sửa trước khi mở ra 54 điều. Nếu chữ Điều 619 trong file của học viên khác bản trong ví dụ, các dòng tương ứng của ví dụ sai.
