# Phép thử độ phủ dẫn chiếu, Điều 609–662 (9/10/2026 tối)

Dữ liệu: file md 54 điều bạn gửi. Script: tách điều, lọc "Điều NNN" (dẫn chiếu tường minh), khớp thuật ngữ bằng biểu thức chính quy.

## Kết quả
- Toàn Phần thứ tư chỉ có **14 cạnh dẫn chiếu tường minh giữa các điều**; **10/54 điều** có dẫn chiếu ra điều khác. Dẫn chiếu ra ngoài phần: 611→Điều 71, 623→Điều 236.
- 19 khái niệm dùng chung (lọc theo luật chốt trước khi đếm: khái niệm ở các điều 609–623, cộng khái niệm có tên trong tiêu đề điều và được dùng ở ≥3 điều khác), tạo 202 cặp (khái niệm, điều dùng):
  - Phủ trong 1 bước dẫn chiếu: **5/202 (2%)**; 2 bước: 2%; tính cả hai chiều: 3%.
  - Bỏ 4 khái niệm lõi (di sản, người thừa kế, di chúc, người lập di chúc): **5/83 (6%)**; tính cả hai chiều: 7%.
- Xác nhận ví dụ của lượt phản biện: Điều 650 dùng "chết cùng thời điểm", "không có quyền hưởng di sản", "từ chối nhận di sản" mà **không dẫn chiếu** 619, 620, 621.

## Sai số đã biết (không đổi kết luận)
Một số khớp sai do so chuỗi:
- 617 "trường hợp pháp luật" chứa "hợp pháp".
- 645 "quản lý hợp pháp".
- 655 "hiệu lực pháp luật" (của bản án).
- 620, 632, 637 "nghĩa vụ tài sản" không phải của người chết.

Bỏ các dòng này thì mẫu số giảm, độ phủ vẫn dưới 10%. Trần cứng: chỉ 10 điều có dẫn chiếu ra ngoài.

## Kết luận
Chọn vị từ theo **dẫn chiếu tường minh** (cách (c) cũ) không dùng được: nó giấu hơn 90% số khái niệm cần dùng chung. Quan hệ giữa các điều trong Phần thứ tư chủ yếu ngầm, qua thuật ngữ, không qua dẫn chiếu.

## Bảng chi tiết
| Khái niệm | Điều định nghĩa | Số điều dùng | Phủ 1 bước | Phủ 2 bước | Điều dùng mà không dẫn chiếu (mẫu) |
|---|---|---|---|---|---|
| quyền thừa kế | 609 | 3 | 0 | 0 | 619, 623, 662 |
| thời điểm mở thừa kế | 611 | 9 | 0 | 0 | 613, 614, 623, 642, 643, 646, 647, 650, 661 |
| di sản | 612 | 33 | 0 | 0 | 609, 610, 611, 613, 615, 616, 617, 618, 619, 620 … |
| người thừa kế | 613 | 29 | 0 | 0 | 609, 614, 615, 616, 617, 618, 619, 620, 621, 622 … |
| nghĩa vụ tài sản người chết để lại | 615 | 9 | 0 | 0 | 614, 620, 622, 623, 632, 637, 645, 646, 658 |
| người quản lý di sản | 616 | 7 | 2 | 2 | 615, 620, 626, 656, 657 |
| chết cùng thời điểm | 619 | 3 | 0 | 0 | 643, 650, 652 |
| từ chối nhận di sản | 620 | 4 | 1 | 1 | 622, 650, 651 |
| không được quyền hưởng di sản | 621 | 4 | 1 | 1 | 622, 650, 651 |
| thời hiệu | 623 | 1 | 0 | 0 | 642 |
| di chúc | 624 | 37 | 0 | 0 | 609, 610, 613, 615, 616, 621, 622, 623, 625, 626 … |
| người lập di chúc | 625 | 20 | 0 | 0 | 626, 629, 630, 631, 632, 633, 634, 635, 636, 637 … |
| di chúc bằng văn bản | 628 | 6 | 0 | 0 | 627, 629, 630, 633, 634, 647 |
| di chúc hợp pháp | 630 | 4 | 0 | 0 | 617, 643, 645, 650 |
| người làm chứng | 632 | 7 | 1 | 1 | 628, 630, 631, 633, 636, 641 |
| công chứng/chứng thực | 635 | 8 | 0 | 0 | 628, 630, 636, 637, 638, 639, 641, 647 |
| hiệu lực của di chúc | 643 | 4 | 0 | 0 | 640, 648, 650, 655 |
| thừa kế theo pháp luật | 649,651 | 11 | 0 | 0 | 609, 610, 622, 632, 637, 642, 644, 645, 648, 650 … |
| người phân chia di sản | 657 | 3 | 0 | 0 | 620, 626, 656 |

---

## Phép thử 2: LLM mạnh với toàn văn (cách e), ngày 9/10/2026

**Điều kiện.** Một lần chạy trên Gemini (người dùng chạy; chưa ghi tên phiên bản mô hình). Prompt: toàn văn 54 điều, yêu cầu một cơ sở tri thức duy nhất, một khái niệm một vị từ. Kết quả: 1020 dòng, R1–R100, danh sách INPUT ở dòng 872–1020. Chưa chạy thử trên s(CASP); chấm tĩnh theo tiêu chí đã chốt trước ở KeHoach §9. Người chấm là Claude, cần người dùng kiểm lại.

**Tiêu chí (chốt trước).** Nối đúng nếu vị từ ở điều dùng trùng tên, số đối và chiều với kết luận của quy tắc ở điều định nghĩa. Dòng 2 còn phải tôn trọng 621.2.

| # | Dùng → Định nghĩa | Gemini viết (dòng) | Kết quả |
|---|---|---|---|
| 1 | 650.1.c → 619 | R76 `all_testamentary_heirs_predeceased_or_extinct/1` là INPUT (L659–661) | Trượt |
| 2 | 650.1.d → 621 | R77 `all_testamentary_heirs_disqualified_or_refused/1` là INPUT (L663–665). Không nối tới `disqualified_from_inheritance/2`, nên 621.2 không tác động | Trượt |
| 3 | 650.1.d → 620 | Cùng INPUT như dòng 2 | Trượt |
| 4 | 651.3 → 620, 621, 626.1 | R83/R84 dùng `valid_heir/2` (L266–269), nối đúng 620 và 621. "Bị truất quyền" là INPUT `disinherited/2`; 626 bị BO_QUA | Một phần |
| 5 | 622 → 620, 621 | R37 `all_heirs_disqualified_or_refused/1` là INPUT (L283) | Trượt |
| 6 | 643.2.a → 619 | R64 so sánh `time_of_death` với `T2 =< T1` (L542–548). Bỏ mất nhánh "được coi là chết cùng thời điểm do không xác định được ai chết trước" | Trượt |
| 7 | 652 → 619 | R85 `predeceased_or_simultaneous/2` là INPUT (L730) | Trượt |
| 8 | 650.1.b → 630 | R75 `has_valid_will/1` (đối số: người chết) là INPUT; 630 kết luận `legal_will/1` (đối số: di chúc) | Trượt |
| 9 | 650.2.b → 643 | R78 `allocated_in_invalid_will_part/2` là INPUT; 643 kết luận `exception_will_ineffective_part/2` | Trượt |
| 10 | 613 → 611 | R12–R14 dùng `time_of_opening_inheritance/2` (L77–92) | Đạt |

**Điểm.** Tính chặt: 1/10. Tính dòng 4 là đạt: 2/10. Cả hai đều thuộc vùng ≤ 6/10.

**Đối chứng (dẫn chiếu tường minh, ngoài 10 dòng).**
- 644.2 → 620, 621 (R69, L593–597): nối đúng.
- 619 → 652 (R26–R27, L205–212): trùng tên và số đối với R85. Nhưng vai trò đối số sai: X ở 619 là người đã chết, trong khi R85 cần cháu còn sống [Suy luận].

**Kiểu lỗi trội.** Có 7 trên 9 dòng trượt cùng một kiểu, gọi là **cắt bằng INPUT**: mô hình đặt tên đúng khái niệm, nhưng khai báo nó là dữ kiện đầu vào thay vì nối tới quy tắc của điều định nghĩa. Có thể dò bằng máy: lấy mọi vị từ INPUT, đối chiếu với bảng khái niệm có điều định nghĩa trong luật.

**Trùng lặp.** Cùng một khái niệm được mã hóa thành nhiều vị từ khác nhau:
- "Chết cùng thời điểm" có 3 cách: `simultaneous_death/2` (619), phép so sánh thời điểm (643), `predeceased_or_simultaneous/2` (652).
- "Di chúc hợp pháp" có 2 cách: `legal_will/1` và `has_valid_will/1`.

**Giải thích khác cần loại trừ [Suy luận].**
- *Lượng từ:* dòng 1, 2, 3, 5 cần lượng từ ("tất cả người thừa kế… đều…"), vốn khó viết trong lập trình logic. Có thể mô hình né lượng từ chứ không phải không thấy chỗ nối. Bỏ 4 dòng này đi, phần còn lại vẫn chỉ đạt 1 đến 2 trên 6 (dòng 4, 6, 7, 8, 9, 10).
- *Prompt:* prompt chưa cấm đặt INPUT cho khái niệm mà điều khác đã định nghĩa. Thêm một câu dặn có thể sửa phần lớn. Chưa kiểm.

**Giới hạn.** Một lần chạy, một mô hình, không rõ phiên bản. Mẫu 10 dòng do chính người thiết kế chọn. Người chấm là Claude.

---

## Phép thử 3: chạy lại có câu dặn (e'), ngày 9/10/2026, 22h

**Điều kiện.** So với bản cũ, chỉ có 61 dòng khác nhau (`diff`). Đây là bản sửa trên kết quả lần trước, trong cùng cuộc chat (người dùng xác nhận lúc 22h22), không phải một lần chạy mới. Câu dặn do Claude viết có nêu ví dụ "Điều 619" và "Điều 630", tức là lộ đáp án của các dòng 1, 6, 7, 8. **Đây là lỗi thiết kế của Claude.**

| # | Thay đổi | Chặt (tiêu chí chốt trước) | Lỏng (đến được vị từ khái niệm của 619, dù là INPUT) |
|---|---|---|---|
| 1 | R76 thành `not has_surviving_testamentary_heir` → `exception_will_ineffective_part` (643) → `predeceased_or_simultaneous` → `simultaneous_death` (INPUT) | Trượt: 619 không có quy tắc định nghĩa | Đạt |
| 2 | R77 thành `not has_eligible_testamentary_heir` → `valid_heir` → `disqualified_from_inheritance/2`. 621.2 được tôn trọng | Đạt | Đạt |
| 3 | Như dòng 2, qua `refused_inheritance/2` | Đạt | Đạt |
| 4 | Không đổi | Một phần | Một phần |
| 5 | Không đổi: `all_heirs_disqualified_or_refused` vẫn là INPUT | Trượt | Trượt |
| 6 | R64 thành `predeceased_or_simultaneous` | Trượt (lý do như dòng 1) | Đạt |
| 7 | `predeceased_or_simultaneous` có quy tắc gọi `simultaneous_death` hoặc so thời điểm | Trượt (lý do như dòng 1) | Đạt |
| 8 | `has_valid_will(D) :- will_of(W,D), legal_will(W)` | Đạt | Đạt |
| 9 | Không đổi: `allocated_in_invalid_will_part` vẫn là INPUT | Trượt | Trượt |
| 10 | Không đổi | Đạt | Đạt |

**Điểm.** Tính chặt: 4/10 (4,5 nếu tính dòng 4). Tính lỏng: 7/10 (7,5 nếu tính dòng 4). Cách tính lỏng đặt ra sau khi thấy kết quả, nên không dùng để đọc ngưỡng.

**Đọc kết quả [Suy luận].**
- Mọi dòng được sửa đều thuộc khái niệm được câu dặn gợi ý: 619, 630, và lượng từ "tất cả".
- Hai dòng không được gợi ý (4, 9) không đổi.
- Dòng 5 có được gợi ý lượng từ nhưng vẫn không sửa.
- 619 vẫn không mã hóa nhánh định nghĩa "được coi là chết cùng thời điểm".
- Lần chạy này **không** trả lời được câu hỏi "một câu dặn chung chung có đủ không", vì đáp án đã bị lộ.

**Ngoài 10 dòng (quan sát, không tính điểm).** Vẫn còn trùng hoặc cắt bằng INPUT:
- `heir_by_will_or_law/2` là INPUT ở 632 và 637;
- `is_alive_at_opening/2` (652) trùng với 613;
- `parent/2` (644), `biological_parent`/`adoptive_parent` (651), `parent_child`/`child_of` (652) cùng chỉ một quan hệ;
- `legal_oral_will` (630.5) không nối vào `legal_will`.

**Việc cần làm.** Chạy (e') sạch: một cuộc chat mới, câu dặn chung không nêu điều nào thuộc bộ kiểm.

---

## Phép thử 4: (e') sạch, cuộc chat mới, ngày 9/10/2026, 22h24

**Điều kiện.**
- Chạy trong một cuộc chat mới (người dùng xác nhận), dùng prompt gốc thêm câu dặn chung. Câu dặn không nêu điều nào thuộc bộ kiểm.
- Chưa có tên và phiên bản mô hình.
- Kết quả 791 dòng; danh sách INPUT ở dòng 629–791. Quy tắc đánh mã theo điều (R609_1…).
- Chấm tĩnh theo tiêu chí chặt đã chốt.

| # | Dùng → Định nghĩa | Gemini viết (dòng) | Kết quả |
|---|---|---|---|
| 1 | 650.1.c → 619 | R650_1 (L476–481) không có nhánh riêng cho 650.1.c. Chỉ có `not has_valid_will` (INPUT) và `all_will_heirs_invalid_or_disclaimed` (INPUT) | Trượt |
| 2 | 650.1.d → 621 | `all_will_heirs_invalid_or_disclaimed/1` là INPUT (L761) | Trượt |
| 3 | 650.1.d → 620 | Như dòng 2 | Trượt |
| 4 | 651.3 → 620, 621, 626.1 | `rank_eligible` dùng `has_eligible_heir_in_rank/2`, là INPUT (L774). Vị từ phụ `is_eligible_statutory_heir` nối đúng `effectively_disqualified` và `valid_disclaimer`, nhưng không được quy tắc 651.3 gọi tới | Trượt (có vị từ nối đúng nhưng bị bỏ rơi) |
| 5 | 622 → 620, 621 | `no_eligible_heir_exists` gọi `effectively_disqualified/2` và `valid_disclaimer/2` (L214–215) | Đạt |
| 6 | 643.2.a → 619 | R643_2a gọi `died_simultaneously/2` (L409–412). 619 nay có quy tắc định nghĩa, gồm cả nhánh "không xác định được ai chết trước" (L152–155) | Đạt |
| 7 | 652 → 619 | R652 gọi `died_simultaneously/2` (L535–547) | Đạt |
| 8 | 650.1.b → 630 | `has_valid_will/1` là INPUT (L760); 630 kết luận `is_valid_will/1` | Trượt |
| 9 | 650.2.b → 643 | Gọi `will_clause_ineffective/2` (L487–489) | Đạt |
| 10 | 613 → 611 | Gọi `opening_time/2` (L42–45) | Đạt |

**Điểm.** Tính chặt: **5/10**. Nếu tính dòng 4 là một phần thì 5,5/10. Kết quả thuộc vùng ≤ 6/10, nhưng chỉ cách ngưỡng 1 dòng.

**Kiểu lỗi.** Cả 5 dòng trượt đều do cắt bằng INPUT (`has_valid_will`, `all_will_heirs_invalid_or_disclaimed`, `has_eligible_heir_in_rank`), dù câu dặn đã cấm. Kiểu lỗi này lặp lại giữa hai lần chạy độc lập (Phép thử 2 và 4), còn tỷ lệ thì thay đổi.

**Đạt khi chấm tĩnh nhưng có thể trượt khi chạy thật [Suy luận, chưa chạy].**
- Dòng 5: `is_qualified_heir` đúng với mọi cá nhân còn sống, nên di sản gần như không bao giờ thuộc về Nhà nước.
- Dòng 9: chỉ cần một phần bất kỳ của di chúc mất hiệu lực là mọi tài sản đã định đoạt đều chuyển sang chia theo pháp luật. Biến `Deceased` cũng không được ràng buộc với `Will`.

**Ngoài 10 dòng (quan sát).**
- `is_heir/2` là INPUT (615, 620, 623), trong khi khái niệm này được định nghĩa ở 613/651.
- `is_heir_by_will_or_law/2` là INPUT (632, 637).
- Có nhiều cú pháp `;` và `not (…)` trong thân quy tắc; khả năng chạy được trên s(CASP) [Chưa kiểm chứng].

**Đối chứng mạnh hơn cần thử.** Cho (e') tự rà lại INPUT, dùng câu hỏi chung không nêu điều nào. Đây là phiên bản chỉ dùng LLM của bước "dò INPUT bằng máy".

---

## Phép thử 5: (e') cộng một lượt tự rà INPUT, Gemini 3.6 Flash, ngày 9/10/2026, 23h05

**Điều kiện.** Cùng cuộc chat với Phép thử 4. Gửi câu hỏi tự rà chung, không nêu điều nào. Mô hình: Gemini 3.6 Flash (người dùng cho biết, áp dụng cho Phép thử 4 và 5).

**Kết quả từng dòng.**
- Dòng 1–4 vẫn trượt:
  - Dòng 1–3: `all_will_heirs_invalid_or_disclaimed/1` vẫn là INPUT, và 650.1.c vẫn không có nhánh riêng.
  - Dòng 4: `has_eligible_heir_in_rank/2` vẫn là INPUT.
- Dòng 8 chuyển sang đạt: dòng 482 nay là `not (testator(Will,D), is_valid_will(Will))`.
- Các dòng 5, 6, 7, 9, 10 vẫn đạt.

**Điểm.** Tính chặt: **6/10**, nằm đúng ngưỡng (≤ 6). Lưu ý: dòng 1–3 phụ thuộc cùng một quy tắc R650_1. Nếu đếm theo vị từ khác nhau, chỉ còn 2 vị từ bị cắt, cả hai đều là điều kiện gộp có lượng từ.

**Lượt tự rà đã sửa gì (`diff`).**
- `has_valid_will`, `is_heir`, `is_heir_by_will_or_law`, `is_administrator` được nối vào các quy tắc.
- Gộp từ vựng quan hệ gia đình.
- `disinherited` được viết thành quy tắc.

**Nối sai nghĩa mới phát sinh [Suy luận, chưa chạy].**
- 632, 637: người làm chứng hoặc người công chứng bị loại nếu `is_qualified_heir`. Vị từ này đúng với mọi cá nhân còn sống tại thời điểm mở thừa kế, tức gần như ai cũng bị loại. Điều luật thì chỉ nói "người thừa kế theo di chúc hoặc theo pháp luật".
- 644: `mandatory_heir_category` nay gồm cả `heir_rank_1`, nên con đã thành niên và có khả năng lao động cũng được suất bắt buộc. Đây là sửa sai so với bản trước.
- 652: chỉ còn `is_biological_child`, mất trường hợp con nuôi. Đây là cách hiểu luật, cần người có chuyên môn kiểm.

Tiêu chí tĩnh (tên, số đối, chiều) tính các chỗ này là "đã nối".

**Đọc kết quả.**
- Khoảng trống "LLM không nối được" mỏng hơn đánh giá lúc 22h30.
- Phần còn đứng có hai mảng:
  - (a) điều kiện gộp có lượng từ;
  - (b) nối sai nghĩa mà tiêu chí tĩnh không bắt được.
- Mảng (b) chưa được kiểm bằng chạy thật.

**Phép thử tiếp theo đề xuất (chưa làm).**
- Với mỗi dòng trong 10 dòng, lập một cặp tình huống, chỉ đổi khái niệm của điều định nghĩa (đúng ↔ sai). Viết theo luật định sẵn, không chọn dòng.
- Người dùng duyệt đáp án.
- Chạy trên cơ sở tri thức này, chỉ sửa cú pháp một cách máy móc.
- Điều kiện bác bỏ: nếu tỷ lệ chạy đúng ≥ tỷ lệ tĩnh (6/10), thì luận điểm (b) chết.
