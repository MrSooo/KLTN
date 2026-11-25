# A62: báo cáo đêm 25/11 → sáng 26/11 (đang điền dần)

Đọc cùng `docs/decisions.md` mục A62. Mọi số dưới đây do máy đo trên cả BLLĐ hoặc trên bộ 34 câu `data/eval_dev/blld_questions.json`.
Bộ 34 câu CHƯA đóng băng: điểm là tín hiệu, không phải kết quả chốt.

## 1. Ba (bốn) KB đem so

| Ký hiệu | KB | Cách dựng |
|---|---|---|
| DeepSeek | lần chạy `ckey` (A46), `deepseek-v4.1-flash` | có sẵn ở `data/processed_ckey` |
| tach gốc | `tach` ở commit 44e3fef (trước A62) | replay ở worktree `../kltn_goc_44e3fef` |
| tach bước 1-3 | sửa máy bước 1-3 (A62) + 1.6B chạy lại (104 lượt) | `~/Documents/kltn_hop_cat/tach_1_6b_a62` |
| tach bước 5 | + lượt 2 `vai-nhom-3` (bước 4) + 1.6B chạy lại (bước 5) | `~/Documents/kltn_hop_cat/tach_1_6b_a62_b5` (đang chạy) |

Dịch câu hỏi ở 1.9: mỗi KB dùng model của lần chạy mình (DeepSeek cho `ckey`, `daongocson12022004/gemini-3.8-flash-high` cho `tach`), như lần so 4 câu ở A61. Chênh điểm vì thế có một phần do model dịch.

## 2. Bộ 34 câu (script `utils/llm_runs/score_blld_questions.py`)

"Đúng chặt" = nhãn đúng VÀ (với nhãn chuẩn `ket_luan_duoc`/`bi_bac`) quy tắc đã chạy có đơn vị của căn cứ chuẩn.

| KB | đúng | đúng chặt | kết luận ở tiêu đề (12) | đối chứng (8) | liệt kê bị nuốt (4) | sai vai (4) | ngoại lệ chéo (3) | tên phân mảnh (3) |
|---|---|---|---|---|---|---|---|---|
| DeepSeek | 13 | 13 | 4 | 3 | 2 | 1 | 1 | 2 |
| tach gốc | 7 | 5 | 0 | 4 | 0 | 1 | 1 | 1 |
| tach bước 1-3 | 12 | 10 | 7 | 4 | 0 | 1 | 0 | 0 |
| tach bước 5 | (chờ) | | | | | | | |

Câu tụt từ tach gốc sang bước 1-3 và lý do (đã đọc từng câu):
- B06, B30: bản gốc ĐÚNG nhãn nhưng căn cứ là D35 (quyền của người lao động), không phải D36: đúng nhờ may.
- B11 (D99.K1), B15 (D145.K1.a): quy tắc mới đúng hơn (thêm điều kiện "ngừng việc", "dưới 15 tuổi" bị mất trước đây), nhưng bước dịch chọn vị từ khác tên (`due_to_fault` thay vì `at_fault`; `aged_under_15` thay vì `employ_person_under_15_years_old`). Đây là lỗi vị từ rải rác, chưa sửa.

## 3. Số đo cấu trúc (script `utils/llm_runs/predicate_structure_metrics.py`, `utils/llm_runs/measure_reference_links.py`)

| Số đo | DeepSeek | tach gốc | tach bước 1-3 | tach bước 5 |
|---|---|---|---|---|
| dòng mệnh đề có tên | 1.693 | 2.537 | 2.574 | |
| tên khác nhau | 1.378 | 2.003 | 2.003 | |
| tên có and/or (vị từ ghép) | 314 (23%) | 262 (13%) | 271 (14%) | |
| tên dùng ở >= 2 Điều | 119 | 202 | 204 | |
| dẫn chiếu khác Điều nối được (/158) | 39 | 39 | 80 | |
| quy tắc / cô lập | 1.142 / 53 | 1.744 / 143 | 2.152 / 145 | |

Phép thử cặp (dẫn chiếu nối được: có điều kiện của đích thì suy ra, bỏ đi thì không): tach bước 1-3 đạt 44/103, quá giờ (>120 s) 22, đối chứng vẫn suy ra 35. Nguyên nhân 35 ca đối chứng: `applies_<T>` lấy cả câu có kết luận riêng của mục đích (D36.K1.a "Quy chế đánh giá..."); đã sửa (chỉ lấy nhóm "trường hợp" không kết luận), có test, áp từ lần dựng bước 5.

## 4. Bước 4 (`vai-nhom-3`)
- dev ĐẠT: f1 0,933, cấu trúc 0,806 (`vai-nhom-2`: 0,950 / 0,889 trên gold cũ); test ĐẠT: f1 0,972, cấu trúc 0,850 (0,909 / 0,900); lần dùng thứ hai của bộ test.
- Cả BLLĐ: 881/881 phản hồi, 841 qua cổng (`vai-nhom-2`: 850), 221 danh sách được trải, 72 giữ (thuật ngữ cố định hoặc không trải được), 48 kết luận lấy từ tiêu đề Điều.

## 5. Chưa xong / chưa kiểm
(điền khi bước 5 xong)

## Phản biện
(điền khi bước 5 xong)
