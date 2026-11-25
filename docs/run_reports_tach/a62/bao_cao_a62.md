# A62: báo cáo đêm 25/11 → sáng 26/11

Đọc cùng `docs/decisions.md` mục A62. Mọi số dưới đây do máy đo trên cả BLLĐ hoặc trên bộ 34 câu `data/eval_dev/blld_questions.json`.
Bộ 34 câu CHƯA đóng băng: điểm là tín hiệu, không phải kết quả chốt.

## 1. Ba (bốn) KB đem so

| Ký hiệu | KB | Cách dựng |
|---|---|---|
| DeepSeek | lần chạy `ckey` (A46), `deepseek-v4.1-flash` | có sẵn ở `data/processed_ckey` |
| tach gốc | `tach` ở commit 44e3fef (trước A62) | replay ở worktree `../kltn_goc_44e3fef` |
| tach bước 1-3 | sửa máy bước 1-3 (A62) + 1.6B chạy lại (104 lượt) | `~/Documents/kltn_hop_cat/tach_1_6b_a62` |
| tach bước 5 | + lượt 2 `vai-nhom-3` (bước 4) + 1.6B chạy lại (bước 5) | `~/Documents/kltn_hop_cat/tach_1_6b_a62_b5` (112 lượt, 2.584 chữ có tên, 4 bị loại) |

Dịch câu hỏi ở 1.9: mỗi KB dùng model của lần chạy mình (DeepSeek cho `ckey`, `daongocson12022004/gemini-3.8-flash-high` cho `tach`), như lần so 4 câu ở A61. Chênh điểm vì thế có một phần do model dịch.

## 2. Bộ 34 câu (script `utils/llm_runs/score_blld_questions.py`)

"Đúng chặt" = nhãn đúng VÀ (với nhãn chuẩn `ket_luan_duoc`/`bi_bac`) quy tắc đã chạy có đơn vị của căn cứ chuẩn.

| KB | đúng | đúng chặt | kết luận ở tiêu đề (12) | đối chứng (8) | liệt kê bị nuốt (4) | sai vai (4) | ngoại lệ chéo (3) | tên phân mảnh (3) |
|---|---|---|---|---|---|---|---|---|
| DeepSeek | 13 | 13 | 4 | 3 | 2 | 1 | 1 | 2 |
| tach gốc | 7 | 5 | 0 | 4 | 0 | 1 | 1 | 1 |
| tach bước 1-3 | 12 | 10 | 7 | 4 | 0 | 1 | 0 | 0 |
| tach bước 5 | 10 | 9 | 4 | 4 | 1 | 0 | 1 | 0 |

Câu tụt từ tach gốc sang bước 1-3 và lý do (đã đọc từng câu):
- B06, B30: bản gốc ĐÚNG nhãn nhưng căn cứ là D35 (quyền của người lao động), không phải D36: đúng nhờ may.
- B11 (D99.K1), B15 (D145.K1.a): quy tắc mới đúng hơn (thêm điều kiện "ngừng việc", "dưới 15 tuổi" bị mất trước đây), nhưng bước dịch chọn vị từ khác tên (`due_to_fault` thay vì `at_fault`; `aged_under_15` thay vì `employ_person_under_15_years_old`). Đây là lỗi vị từ rải rác, chưa sửa.

## 3. Số đo cấu trúc (script `utils/llm_runs/predicate_structure_metrics.py`, `utils/llm_runs/measure_reference_links.py`)

| Số đo | DeepSeek | tach gốc | tach bước 1-3 | tach bước 5 |
|---|---|---|---|---|
| dòng mệnh đề có tên | 1.693 | 2.537 | 2.574 | 2.797 |
| tên khác nhau | 1.378 | 2.003 | 2.003 | 2.172 |
| tên có and/or (vị từ ghép) | 314 (23%) | 262 (13%) | 271 (14%) | 200 (9%) |
| tên dùng ở >= 2 Điều | 119 | 202 | 204 | 210 |
| dẫn chiếu khác Điều nối được (/158) | 39 | 39 | 80 | 90 |
| quy tắc / cô lập | 1.142 / 53 | 1.744 / 143 | 2.152 / 145 | 2.462 / 181 |

Phép thử cặp (dẫn chiếu nối được: có điều kiện của đích thì suy ra, bỏ đi thì không): tach bước 1-3 đạt 44/103, quá giờ (>120 s) 22, đối chứng vẫn suy ra 35. Nguyên nhân 35 ca đối chứng: `applies_<T>` lấy cả câu có kết luận riêng của mục đích (D36.K1.a "Quy chế đánh giá..."); đã sửa (chỉ lấy nhóm "trường hợp" không kết luận), có test, áp từ lần dựng bước 5.

Bước 5 (`reference_links_buoc5.txt`): 120 ca, đạt 83, quá giờ 21, đối chứng vẫn suy ra 15 (còn lại: D115, D139, D143, D197, chưa đọc từng ca), không/không 1.

## 4. Bước 4 (`vai-nhom-3`)
- dev ĐẠT: f1 0,933, cấu trúc 0,806 (`vai-nhom-2`: 0,950 / 0,889 trên gold cũ); test ĐẠT: f1 0,972, cấu trúc 0,850 (0,909 / 0,900); lần dùng thứ hai của bộ test.
- Cả BLLĐ: 881/881 phản hồi, 841 qua cổng (`vai-nhom-2`: 850), 221 danh sách được trải, 72 giữ (thuật ngữ cố định hoặc không trải được), 48 kết luận lấy từ tiêu đề Điều.

## 5. Bước 5 so với bước 1-3: vì sao điểm hỏi đáp tụt (đã đọc từng câu)

Tụt 12 → 10. Câu đổi:
- B01, B03, B04, B34 (cả 4 câu D34 "chấm dứt hợp đồng"): bước dịch chọn φ=`terminate` thay vì `terminate_employment_contract`. `terminate` là đầu quy tắc cô lập thân rỗng của D27.K1 q4. Nguyên nhân gốc: lượt 2 ghi dòng "thử việc **không** đạt yêu cầu" thành `"thử việc đạt yêu cầu"` + `cuc: phu_dinh`; cổng chữ nguyên văn loại dòng đó (đúng luật cổng), quy tắc q4 còn trơ "chấm dứt" không điều kiện. Quy tắc D34 vẫn còn nguyên, chỉ bước dịch bị kéo sang tên ngắn.
- B13: bước dịch trả `ngoai_pham_vi`; B22: cổng 1.9 loại vì trích "người lao động" không nguyên văn. Hai câu này là dao động của bước dịch (một lần chạy mỗi KB, không lặp).
- Câu lên: B06 (căn cứ có D37.K1 nhưng kèm cả loạt D35), B11 (bước dịch lại chọn `at_fault`; quy tắc D99.K1 ghi `at_fault(X)` không nói lỗi của ai, đúng nhờ vậy), B19 (liệt kê, D53.K2.b; khoản này có một dòng điều kiện bị cổng loại, xem mục 7).

## 6. Kết luận so với DeepSeek

Trên số đo cấu trúc, `tach` bước 5 hơn DeepSeek rõ: vị từ ghép 9% so với 23%, dẫn chiếu nối được 90 so với 39, tên dùng chung ≥2 Điều 210 so với 119.
Trên hỏi đáp 34 câu thì **CHƯA hơn**: 10/34 (chặt 9) so với 13/34 (chặt 13). Bản tốt nhất của `tach` là bước 1-3 với 12/34 (chặt 10), vẫn dưới DeepSeek.
Phần lớn câu sai còn lại của `tach` không do quy tắc thiếu mà do bước dịch chọn tên vị từ khác tên trong quy tắc (B11, B15 ở bước 1-3; B01/03/04/34 ở bước 5). Đây là vấn đề "vị từ rải rác" ở phía bước dịch 1.9, A62 chưa đụng tới.

## 7. Chưa xong / chưa kiểm
- 12 dòng điều kiện bị cổng loại theo từng dòng (D10.K1, D27.K1, D29.K1, D34.K13, D35.K2.c, D53.K2.b, D57.K3, D76.K5, D107.K2.b, D109.K1 hai lần, D217.K2): quy tắc của nhóm vẫn được dựng với ÍT điều kiện hơn văn bản, tức là bị nới (ví dụ D109.K1 mất "làm việc từ 06 giờ trở lên"). Chưa sửa; cần user chọn: bỏ cả nhóm khi một điều kiện hỏng, hay lùi về lượt 1 cho cả khoản.
- Từ vựng đưa cho bước dịch 1.9 còn chứa đầu của quy tắc cô lập (như `terminate`): chọn chúng chỉ ra `khong_tra_loi`. Chưa sửa; là thay đổi hành vi 1.9, cần user duyệt.
- Lượt 2 vẫn tách đuôi thời gian thành điều kiện ở D137.K2 ("cho đến hết thời gian nuôi con dưới 12 tháng tuổi" AND "mang thai") dù lời nhắc đã bỏ câu đó: do luật 1 cũ ("thời gian" là điều kiện).
- Mỗi KB chỉ dịch câu hỏi một lần: chênh ±2 câu nằm trong dao động của bước dịch, chưa đo.
- Chưa đọc 15 ca đối chứng còn suy ra "yes" ở phép thử cặp bước 5; chưa xem mẫu 20 dòng danh sách được trải.

## Phản biện
- So DeepSeek vẫn không công bằng hoàn toàn: model dịch khác nhau. Muốn tách phần KB khỏi phần dịch thì phải dịch cùng một model cho cả hai KB; chưa làm.
- Bộ 34 câu chưa đóng băng và do agent soạn nhắm vào lỗi nền của `tach`; điểm không phải kết quả chốt.
- Sửa bước 4-5 đem lại cấu trúc tốt hơn (ghép 14%→9%, nối 80→90, phép thử cặp 44/103→83/120) nhưng không đem lại điểm hỏi đáp. Đừng đọc số cấu trúc như bằng chứng KB trả lời tốt hơn.
Bộ test đầy đủ sau bước 5 (26/11): `run_all --viewer --tests` --llm off rồi --llm replay đều 20/20 bước, 18 bộ test OK.
