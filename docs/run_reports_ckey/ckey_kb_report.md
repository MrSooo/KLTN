# Báo cáo KB dựng bằng DeepSeek qua ckey (lần chạy `ckey`)

Trạng thái: chạy xong 20/11/2026 (bắt đầu 19/11): lần chạy `ckey` trên cả bộ luật và ba lần sửa lời nhắc `ckey2` đến `ckey4` trên tập con `lldnn`. File được điền dần trong lúc chạy; chuyển vào repo ngày 20/11.

Lần chạy: `KLTN_LLM_RUN=ckey`, model `deepseek-v4.1-flash` qua `https://api.xah.io` (A46), lời nhắc 1.6A `menh-de-4` (A47), các bước sau giữ lời nhắc cũ. Kết quả Sonnet (lần chạy mặc định) không bị đụng. Báo cáo này không so với Sonnet.

## 1. KB của cả bộ luật (BLLĐ)
Tóm tắt: KB gốc dựng xong trên cả 881 đơn vị: **1.142 quy tắc s(CASP)** (53 cô lập), **187 quan hệ chặn**, nạp s(CASP) đạt, `checks` 0 lỗi, chuỗi replay ckey 18/18 bước. Đầu ra ở `data/processed_ckey/rules/rules_BLLD_45-2019.pl`.

| Bước | Số đo | Nguồn |
|---|---|---|
| 1.6A mệnh đề | 881/881 đơn vị, 2.042 dòng: 1.752 mệnh đề (1.088 kết luận, 640 điều kiện, 23 ngoại lệ, 1 vai lạ), 150 con trỏ dẫn chiếu, 139 bỏ qua, 1 loại lạ; **65 dòng lỗi cổng (3,2%)**, bị bỏ ở 1.6B | `data/llm_cache/propositions/BLLD_45-2019.ckey.json` |

Đo bằng máy trên 1.6A (19/11):
- Phủ định kép (`menh_de` bắt đầu "không/chưa" mà `cuc = phu_dinh`, trái đặc tả "menh_de đã bỏ chữ phủ định"): **23/2.042 dòng**. Ví dụ D32.K3 "không bị phân biệt đối xử" + `phu_dinh` (thành "không không bị..."). Cổng chỉ gắn cờ, không chặn.
- Điều 154 (lô 149, trung tâm của bộ câu hỏi dev): 9 khoản, mỗi khoản 2 dòng (điều kiện + `khong_ap_dung` "cấp giấy phép lao động"), không trùng, không lỗi; lô này ra 22.831 token (nhiều bất thường) nhưng đầu ra không thoái hoá.

| 1.6B vị từ | 1.741 chữ (gộp cấp 1), 71 lượt tuần tự: **1.739 có tên, 2 bị loại**; 1.586 vị từ (concept 877, input 709); LLM chọn dùng lại 153 lần (8,8%); 178 vị từ dùng ở từ 2 Điều | `docs/run_reports_ckey/predicates/` |
| 1.7 ngoại lệ ngầm | 243 cặp cùng vị từ concept, 6 đã có cạnh 1.5, **hỏi 237, nhận 28 cạnh** `exception_of`, cổng loại 0. Ví dụ: D34.K7 (NSDLĐ cá nhân chết) là ngoại lệ của D137.K3; D86.K2.a là ngoại lệ của D86.K1 | `docs/run_reports_ckey/implicit_exceptions/` |
| 1.8 quy tắc | 1.142 quy tắc (53 cô lập); cạnh ngoại lệ dùng 51 (23 từ 1.5, 28 từ 1.7); 187 quan hệ chặn; 679 concept coi là input | `docs/run_reports_ckey/rules/` |

Bộ quét của 1.8 báo **50 vấn đề** (không chặn, chỉ báo):
- 42 cặp quy tắc trùng hệt nhau (ví dụ 7 quy tắc giống r0079), do hai chữ khác Điều được đặt cùng vị từ và cùng thân;
- 4 vòng chặn, ví dụ `organize_and_lead_labor_strike` và `forbidden_organize_and_lead_labor_strike` chặn lẫn nhau; `may_request_court_resolution` và `must_issue_dispute_resolution_decision` chặn lẫn nhau. Vòng chặn làm s(CASP) không kết luận được ở hai đầu;
- 2 cặp phương thức trái nhau mà không có quan hệ chặn (`may_work_at_night` và `forbidden_work_at_night`, tương tự cho làm thêm giờ);
- quy tắc thân rỗng (đúng cho mọi X), bị cô lập nên không vào suy luận.

### Thời gian chạy model (máy đo)
Nguồn: dòng "xong sau Ns" và "API lỗi" trong log `sandbox_api` (script gom `utils/llm_runs/sandbox_api_timing.py`), tổng token/chi phí từ bản ghi `data/llm_cache/sandbox_api/*.json` (trường `usage`, `cost_vnd` do ckey trả), mốc giờ từ trường `created`.

| Bước | Thời gian thực (từ bản ghi đầu đến cuối) | Số lần gọi | Tổng giây gọi (cộng dồn) | Token ra | Token vào (ckey báo) | Chi phí (ckey báo) | Thử lại / lỗi |
|---|---|---|---|---|---|---|---|
| 1.6A (gồm thí điểm 30 đơn vị, chạy cả bộ, `--lam-lai`) | 1 giờ 23 phút (20:14 đến 21:37, song song) | 246 bản ghi cache; log chạy cả bộ 196 lần xong | 8.594 s (lần chạy cả bộ) | 1.314.736 | 15.405 | 7.061 đ | 1 lỗi kết nối trong log cả bộ; 4 lô cụt `max_tokens`, 2 lô JSON hỏng, 2 lô thiếu unit_id: gọi lại |
| 1.6B (tuần tự) | 2 giờ 11 phút (21:39 đến 23:50) | 71 | 7.765 s (lượt lâu nhất 234 s) | 203.884 | 4.812 | 1.597 đ | 15 lần 502 + 2 lỗi kết nối, đều qua khi thử lại; lần chạy đầu (`chay_1_6b.log`) dừng sau 1 lượt vì bộ chạy không gửi `schema.json` (lỗi của agent, đã sửa) |
| 1.7 (song song 4) | 6 phút 36 giây (23:57 đến 00:03) | 24 | 1.407 s (lô lâu nhất 196 s) | 19.360 | 1.541 | 153 đ | 1 lần 502, qua khi thử lại |

Lưu ý: "token vào" ckey báo rất thấp (57 token cho một lô gửi hàng nghìn chữ), có vẻ ckey không tính token vào hoặc tính theo cache; số này **không tin được**, chỉ chép lại. Giờ ghi theo giờ Việt Nam.

## 2. Nạp nghị định: KB thay đổi thế nào (tập con `lldnn`)
Nguồn: `docs/run_reports_subset/lldnn_ckey/update/update_report.txt`, `data/processed_subset/lldnn/processed_ckey/update/update_rules.jsonl`.

R (mọi quy tắc qua mọi khoảng hiệu lực): **501 quy tắc**. Theo mốc (|T| số KU đổi, |A| tập ảnh hưởng, quy tắc hiệu lực sau mốc):

| Mốc | Văn bản nạp | KU đổi \|T\| | Tập ảnh hưởng \|A\| | Cặp 1.7 mới hỏi | Quy tắc hiệu lực |
|---|---|---|---|---|---|
| 01/01/2021 | BLLĐ 45/2019 (16 Điều) | 76 | 76 | 2 | 82 |
| 01/02/2021 | NĐ 145/2020 | 133 | 188 | 24 | 229 |
| 15/02/2021 | NĐ 152/2020 | 115 | 209 | 11 | 350 |
| 18/09/2023 | NĐ 70/2023 (sửa NĐ 152) | 21 | 80 | 2 | 357 |
| 07/08/2025 | NĐ 219/2025 (thay NĐ 152) | 210 | 360 | 11 | 343 |
| 01/01/2026 | VBHN 125/2025 (BLLĐ sửa đổi, thêm Đ154.K8a) | 1 | 5 | 0 | 344 |
| 15/04/2026 | NQ 66.16/2026 | 34 | 324 | 14 | 359 |
| 01/03/2027 | NQ 66.16 (một phần hết hạn) | 34 | 324 | 14 | 344 |

2.7 đối chứng (cập nhật tăng dần chỉ trên A(e) so với dựng lại toàn bộ, 18 ngày): **ĐẠT**. Bỏ từng quan hệ của N: 0 sai khác với mọi quan hệ (tức trên kho này chưa có ca nào cho thấy quan hệ đó cần; phép thử đột biến có trong test tổng hợp, không có trên dữ liệu thật).

Ví dụ một chuỗi quy tắc qua các mốc (ngoại lệ "không thuộc diện cấp giấy phép lao động"):
- NĐ 152 Đ7.K14 (giáo viên, nhà nghiên cứu được Bộ GD&ĐT xác nhận): `-subject_to_work_permit <- foreign_worker_in_vietnam, confirmed_by_moet_for_teaching_research`, hiệu lực 15/02/2021 đến 18/09/2023;
- mốc 18/09/2023 NĐ 70 sửa K14 và chèn K14.a, K14.b: quy tắc cũ đóng, mở ba quy tắc mới (K14 `moet_confirmation_for_work_in_vietnam`, K14.a `work_as_teacher_or_researcher`, K14.b `work_as_manager_executive_or_principal`), hiệu lực đến 07/08/2025;
- mốc 07/08/2025 NĐ 219 thay NĐ 152: cả ba đóng; NĐ 219 Đ7.K13.a mở, nhưng 1.6A đọc sai: đầu quy tắc là `manager_executive_expert_technical_worker` (danh mục người) thay vì "không thuộc diện cấp giấy phép", nên câu dev Q02 (hỏi ở 01/10/2025) không có ngoại lệ để chặn;
- mốc 01/01/2026 VBHN 125 thêm BLLĐ Đ154.K8a: `not_applicable_neg_subject_to_work_permit <- high_quality_digital_technology_industry_workforce` (tên vị từ đầu lạ: "không áp dụng phủ định của phải có giấy phép").

Hỏi đáp 1.9 (15 câu dev, `lldnn_questions.json`): **đúng 3/15** (Q03, Q09, Q15). Q01-Q08 hỏi quanh D151.K1.d: lần chạy ckey không có quy tắc đầu "phải có giấy phép lao động" (xem mục 3c), nên ra `chua_du_can_cu` dù ngoại lệ ở nghị định có mặt. Q10-Q14 (gắn "cần 2.6") ra `chua_du_can_cu` hoặc `ngoai_pham_vi`.

Phần BLLĐ của tập con (16 Điều): 1.6A 76 đơn vị, 142 dòng, 5 lỗi cổng (3,5%); 1.6B 130/130 chữ có tên, 127 vị từ, LLM chọn dùng lại chỉ 3 (2,3%; lúc dựng 75/130 chữ không có ứng viên); 1.7 hỏi 2 cặp, nhận 1 (D53.K3 là ngoại lệ của D53.K2). **82 quy tắc gốc.**

1.6A cho KU của nghị định (cập nhật, 85 lô, 390 KU), theo luật dừng A39 chạy 60 lô đầu trước:
- 56/60 lô xong trong 20 phút; **4 lô cụt `max_tokens`** (011, 016, 031, 056; lô 056 còn bị timeout đọc ở 300 s);
- nhập 279 KU, 579 dòng, **14 lỗi cổng (2,4%)**, dưới ngưỡng 5%;
- soát câu dẫn lọt thành `menh_de` (lọc chữ trích kết thúc bằng ":" hoặc có "sau đây"/"bao gồm", rồi đọc tay 19 dòng nghi): **4 đến 6/452 mệnh đề là câu dẫn thật**: NĐ 145 Đ28.K2 "gồm hồ sơ đề nghị thu hồi giấy phép", Đ28.K3, Đ28.K4 "trình tự, thủ tục thu hồi giấy phép như sau", NĐ 152 Đ10 "được cấp theo thời hạn của một trong các trường hợp sau đây...", có thể thêm NĐ 219 Đ6.K3, Đ11.K2. Các dòng NĐ 152 Đ2.K1.a-k bị lọc ra là đúng (trích có câu dẫn của khoản cha, mệnh đề là mục con). Theo quy ước "luật dừng chất lượng chỉ cảnh báo", ghi lại và chạy tiếp.

## 3. Lỗi gặp nhiều và cách xử lý

### 3a. Lỗi cổng của 1.6A (65 dòng, theo dòng; một dòng có thể nhiều loại)
| Loại | Dòng | Ví dụ | Nguyên nhân (cách đọc của agent) | Cách xử lý đề xuất |
|---|---|---|---|---|
| âm tiết của menh_de không có trong trich | 20 | D1: thiếu "quy định" | model thêm chữ vào menh_de hoặc trích thiếu | luật đã có trong lời nhắc; nhắc lại bằng ví dụ, hoặc chấp nhận bỏ dòng |
| thừa/thiếu trường | 18 | D14.K1: thêm trường `dieu_kien` vào dòng kết luận | model hiểu luật (d) "cụm 'thông qua/đối với' là điều kiện" nhưng ghi thành trường thay vì dòng riêng | sửa lời nhắc: "điều kiện luôn là MỘT DÒNG riêng, không bao giờ là một trường" + ví dụ JSON hai dòng |
| ly_do_llm sai khuôn | 11 | D48.K1.b: `ma = tach_hay_giu_chung` (đó là mã của chua_ro, không phải của ly_do_llm) | lẫn hai tập mã | lời nhắc ghi rõ tập mã của từng trường cạnh nhau |
| chu_the.chu không nguyên văn | 7 | D24.K3: `chu = ""` | chủ thể rỗng thay vì bỏ trường | lời nhắc đã ghi "trường rỗng thì bỏ"; nhắc trong danh sách tự kiểm |
| bo_qua thiếu lý do | 7 | D172.K3 | | nhắc trong danh sách tự kiểm |
| trich, liet_ke không nguyên văn | 6 | D46.K2 | model chép sai chữ | không sửa được bằng lời nhắc chắc chắn; bỏ dòng |
| khác (loai lạ, menh_de rỗng) | 4 | D122.K2, D164.K3 | | bỏ dòng |

### 3b. Lỗi khi chạy (API, bộ chạy)
| Lỗi | Số lần | Nguyên nhân | Đã xử lý |
|---|---|---|---|
| 502/503/524 "upstream gateway unavailable" | nhiều | máy chủ ckey chập chờn | bộ chạy thử lại 3 lần (thêm mã 520-524); lô lỗi chạy lại sau |
| 404 "model not available" | 1 model | người bán gỡ `dungcsnd113/gemini-flash-3.8` | đổi sang `deepseek-v4.1-flash` (A46) |
| Đầu ra cụt `max_tokens` (32.000) | 4 lô 1.6A, lô 149 hai lần | model lặp vòng | gọi lại; đều qua sau 1-2 lần |
| JSON hỏng (kể cả token lạ `<|endoftext|>`) | 2 lô 1.6A | model | gọi lại, qua |
| JSON bọc ```` ```json ```` | phần lớn lô (53/204 lần đầu) | thói quen của model | bóc (A46, chủ đề tài duyệt) |
| Model bỏ sót unit_id trong lô | 2 lô (015, 117; 8 đơn vị) | model | `nhap` từ chối cả lô; thêm `sandbox_api --lam-lai` để làm lại, qua |
| Bộ chạy không gửi `schema.json` (1.6B) | 1 | lỗi của agent | sửa, có test; lượt 1 chạy lại |
| `propositions.py so` crash khi có `bo_ngu` sai khuôn | 1 | công cụ so giả định dòng đúng khuôn | **chưa sửa** (không dùng `so` vì không so với Sonnet) |
| `make_rounds` dừng (SystemExit) ở sổ vị từ 2.6, lượt 019 (ckey) | 1 | KU sửa đổi và KU chèn của cùng Điều nằm xen nhau, lượt kế hoạch bị cắt giữa Điều | sửa mã A49 (`group_by_dieu`, commit `462db0a`, có test; lượt 001-019 dựng lại khớp từng byte); **cần chủ đề tài duyệt** |
| Đầu ra cụt `max_tokens` ở 1.6A cập nhật, tập con | ckey: 4 lô (011, 016, 031, 056; lô 056 mất 897s); ckey2: 3 lô (009, 027, 029; lô 027 cụt hai lần) | model lặp vòng | `sandbox_api` chạy lại (ckey2 cần 3 lượt, 1.885s + 384s + 263s); đều qua |
| Model bỏ sót `unit_id` ở 1.6A cập nhật (ckey3) | 3 lô (016, 027, 052; 34 KU) | model | `sandbox_api --lam-lai 016,027,052`; lô 016 cụt `max_tokens` thêm một lần, chạy lại qua |
| Chế độ chạy `chi_1_6a` của agent sai (ckey3) | 1 | 1.6A cập nhật cần sổ vị từ của 1.6B gốc | chạy tiếp cả chuỗi (`tu_1_6b`, `tu_so_vi_tu`), không gọi lại 1.6A gốc |
| Bước kiểm 2.7 trượt ở replay tập con ckey4 | 16 sai khác, một quy tắc (D151.K1.d) | tập ảnh hưởng A(e) không thấy đầu chặn 1.5 mới đến từ ND_152 D7.K1 (lỗ hổng A42) | **chưa sửa, chờ user** (sửa là đổi thiết kế) |
| Replay giữa chuỗi sau 1.6A (ckey2, replay 1) mã thoát 1 | 1 | cache 1.6B của lần chạy chưa có ở thời điểm đó | đúng dự kiến, không phải lỗi |

### 3c. Lỗi về nghĩa (cổng không bắt) và các lần sửa
Số đo trên tập con `lldnn`, 466 đơn vị (76 BLLĐ + 390 KU nghị định), script `utils/llm_runs/measure_proposition_errors.py`. Định nghĩa chốt trước khi chạy lần sửa đầu.

| Lỗi | Ví dụ | Hệ quả | Số ở ckey |
|---|---|---|---|
| Câu dẫn yêu cầu đọc thành danh sách điều kiện (M1) | D151.K1 "phải đáp ứng các điều kiện sau đây": a-d ra `dieu_kien` | quy tắc `must_meet_conditions`, không có đầu "phải có giấy phép lao động"; Q01-Q08 sai | 0/4 mục con ra `ket_luan` (tập con chỉ có 1 câu dẫn kiểu này) |
| Câu dẫn lọt thành `menh_de` (M2) | NĐ 145 Đ28.K3 "trình tự, thủ tục thu hồi giấy phép như sau" | quy tắc rỗng nghĩa | 4 (máy) |
| Lỗi cổng 1.6A | âm tiết không có trong trich 8; chủ thể từ câu dẫn mà trich thiếu mẩu câu dẫn 6; chu_the không nguyên văn 3 | dòng bị bỏ ở 1.6B | 26 lỗi ở 19 đơn vị |
| Phủ định kép (M4) | BLLĐ D153.K2 "không có giấy phép lao động" + `phu_dinh` | đọc tay 11 ca ở ckey2 (20/11): cả 11 đều thật (kể cả "không quá 02 năm"); 7 ca có quy tắc và cả 7 **ngược nghĩa**: `forced_exit :- -lack_work_permit` (D153.K2, trục xuất người CÓ giấy phép), `-maximum_duration_two_years` (ND_219 D21.K2), `-license_denial`, `-refuse_license_issuance`, `-refuse_work_permit_exemption_confirmation`, `-fall_short_of_agreed_requirements`, `-contract_content_differs_from_granted_permit`. 1.6B đặt tên đúng theo chữ nó nhận; lỗi gốc ở 1.6A (trái ví dụ trong lời nhắc "Không được trợ cấp" → menh_de "được trợ cấp", `phu_dinh`) | 11 (ckey2: 11) |
| Hỏi đáp (M3) | | | 3/15 |

Luật đọc kết quả: DeepSeek không tất định, 1.9 cũng dùng LLM, không có lần chạy đối chứng cùng lời nhắc; chỉ tính "cải thiện" khi thay đổi lớn hoặc theo cấu trúc.

Các lần sửa (mỗi lần một lần chạy riêng, một phiên bản lời nhắc, cộng dồn; ghi ở `docs/decisions.md`):
| Lần | Lần chạy | Sửa gì | Cách sửa | Trước | Sau |
|---|---|---|---|---|---|
| 1 (A50) | ckey2 | luật câu dẫn (M1, M2) | `menh-de-5`: thêm câu phân biệt theo vai của danh sách, chữ dẫn luôn `bo_qua`, ví dụ D145.K1.b (ngoài tập con) | M1 0/4, M2 4, cổng 26, M3 3/15 | M1 **4/4**, M2 3, cổng **45** (lỗi mới: model thêm chữ "là" vào mục con danh từ; thiếu `nguon`), M3 3/15. Lỗi đích hết nhưng Q01-Q08 vẫn sai vì lỗi khác: dữ kiện 1.9 `foreign_worker`+`work_in_vietnam` không khớp vị từ gộp `foreign_worker_working_in_vietnam` |
| 2 (A51) | ckey3 | tác dụng phụ của lần 1: thêm "là", `chu_the` thiếu `nguon` | `menh-de-6`: mục con cụm danh từ chép nguyên cụm, không thêm chữ nối; hai dòng tự kiểm | "là" 20, thiếu nguon 7, cổng 45, M1 4/4, M3 3/15 | "là" **1**, thiếu nguon **0**, cổng **15** (mới: 8 lỗi `loai 'dieu_kien'`), M1 4/4, M4 6, M3 6/15 (không quy cho A51: 1.9 và 1.6B không tất định). Tác dụng phụ mới: ND_219 D7 (kết luận ở tiêu đề Điều) chỉ ra `dieu_kien`, mất quy tắc miễn K5-K13 |
| 3 (A52) | ckey4 | tác dụng phụ của lần 2: Điều kết luận ở tiêu đề mất `ket_luan` (ND_219 D7), `loai 'dieu_kien'` | `menh-de-7`: mỗi khoản của Điều không câu dẫn có `ket_luan` từ tiêu đề cộng `dieu_kien`; ví dụ D37.K2; dòng tự kiểm `loai` | ND_219 D7 có quy tắc 2 đơn vị, `loai` 8, cổng 15, M3 6/15 | ND_219 D7 **19** đơn vị, `loai` **0**, M1 4/4, "là" 0; nhưng cổng **51** (mới: 25 lỗi chủ thể không nguyên văn ở Điều tiêu đề "Các trường hợp ..."). **Bước kiểm 2.7 trượt** (lỗ hổng tập ảnh hưởng A42, D151.K1.d), nên không có số hỏi đáp |

Không sửa, và vì sao: `max_tokens` lặp vòng (sửa là đổi tham số `max_output_tokens` hay cỡ lô, thuộc quyền bạn); cạnh 1.7 đáng ngờ và vòng chặn, quy tắc trùng ở 1.8 (hệ quả của đặt tên, nằm sau 1.6A).

### 3d. So sánh bốn lần chạy trên tập con (KB cả bộ luật vẫn là `ckey`, lời nhắc `menh-de-4`; `menh-de-5/6/7` chỉ chạy trên tập con)
| Số đo | ckey (`menh-de-4`) | ckey2 (`-5`, A50) | ckey3 (`-6`, A51) | ckey4 (`-7`, A52) |
|---|---|---|---|---|
| Lỗi đích của lần sửa | D151.K1 ra kết luận 0/4 | 4/4 | "là" 20 → 1; thiếu `nguon` 7 → 0 | ND_219 D7 có quy tắc 2 → 19; `loai` nhầm 8 → 0 |
| Lỗi cổng 1.6A (lỗi / đơn vị) | 26 / 19 | 45 / 39 | 15 / 11 | 51 / 34 |
| ND_219 D7: số đơn vị có quy tắc | 17 | 12 | 2 | 19 |
| M1 (D151.K1 ra kết luận) | 0/4 | 4/4 | 4/4 | 4/4 |
| Lỗi "là" | 2 | 20 | 1 | 0 |
| Câu dẫn lọt (máy) | 4 | 3 | 2 | 3 (có lại D151.K1) |
| Phủ định kép (M4, dòng) | 11 | 11 | 6 | 11 |
| Quy tắc ngược nghĩa (máy, theo danh sách từ tự đặt) | 9 | 19 (11 là một mẫu ND_219 D21.K1.*) | 4 | 17 (11 là một mẫu ND_219 D21.K1.*) |
| Bước kiểm 2.7 | đạt | đạt | đạt | **trượt** |
| Hỏi đáp dev (đúng / đủ căn cứ chuẩn) | 3/15 | 3/15 | 6/15 (đủ căn cứ: Q03, Q06, Q09; không quy cho A51) | không có (2.7 trượt) |

Không bản nào trội hẳn: mỗi lần sửa xoá được lỗi đích nhưng sinh một lớp lỗi mới ở chỗ khác (A50 → "là"; A51 → mất `ket_luan` ở Điều kết luận ở tiêu đề; A52 → chủ thể không nguyên văn ở Điều tiêu đề "Các trường hợp ...", và dữ liệu chạm lỗ hổng 2.7). Không có lần chạy lặp cùng lời nhắc nên chưa biết mức nhiễu.

### 3e. Thời gian chạy model trên tập con (máy đo; giây gọi là tổng thời gian các lần gọi, chạy song song 4 nên lớn hơn giờ đồng hồ)
| Lần chạy | Giờ đồng hồ | Lần gọi xong | Token ra | Tiền token ra (tính: token ra × 4.800đ/triệu) | Ghi chú |
|---|---|---|---|---|---|
| ckey (gốc, chạy từng bước 19-20/11) | không đo liền (chạy rời từng bước) | 132 | 692.104 | ~3.320đ | 1.6A gốc gần như lấy lại từ cache cả bộ luật (2 lần gọi); sổ vị từ dừng ở lượt 019 (A49), 9 lần 502; 1.6A cập nhật lô 056 mất 897s |
| ckey2 | 1h31 | 143 | 829.294 | ~3.980đ | 1.6A cập nhật cần 3 lượt (`max_tokens`) |
| ckey3 | ~1h14 | 148 | 920.563 | ~4.420đ | ba đoạn chạy cộng một lần làm lại tay (`--lam-lai`, lô 016 cụt thêm một lần) |
| ckey4 | 51 phút | 140 | 577.152 | ~2.770đ | 1.6A cập nhật cần 2 lượt |
Bước tốn nhất là 1.6A cập nhật (390 KU, 85 lô: 450.000 đến 700.000 token ra, 40 đến 117 phút giây gọi) và sổ vị từ 2.6 (28 lượt tuần tự, ~28 đến 37 phút). Token vào và tiền token vào: **chưa có** (log bộ chạy chỉ ghi token ra). Bảng chi phí ở mục 1 là số ckey tự báo (`cost_vnd`), không cùng cơ sở: ví dụ 1.6A cả bộ luật tính theo token ra là ~6.310đ, ckey báo 7.061đ.

Các script đo ở `utils/llm_runs/` (`measure_proposition_errors.py`, `count_inverted_negation.py`, `sandbox_api_timing.py`, `run_subset_chain.ps1`, `compare_prompts.py`). Log chạy (chuyển sang UTF-8) ở `docs/run_reports_ckey/run_logs/` (cả bộ luật) và `docs/run_reports_subset/lldnn_<run>/run_logs/` (tập con). Thư mục làm việc của hộp cát (đầu vào và đầu ra thô từng lô) ở `data/sandbox_runs/` (A53); nội dung trả về của model cũng nằm trong `data/llm_cache/`.

## 4. Chưa kiểm, cần bạn phân xử
1. **A49 (sửa mã giữa đêm, cần bạn duyệt).** Sổ vị từ 2.6 dừng ở lượt 019 do lỗi có sẵn trong mã (mốc sửa đổi liệt kê đơn vị bị sửa trước, đơn vị chèn sau). Agent sửa không hỏi: gom đơn vị theo Điều trước khi chia lượt; phép kiểm giữ nguyên; đã chứng minh không đổi gì đã có (lượt 001-019 khớp từng byte, báo cáo Sonnet không đổi, hồi quy 20/20). Commit `462db0a`, revert riêng được.
2. Lời nhắc `menh-de-5` trở đi do agent viết ([THÊM]); câu luật ở A50 được viết vì thấy lỗi ở D151 (thuộc bộ dev), dù ví dụ lấy ngoài tập con.
3. Ví dụ "Danh sách ĐIỀU KIỆN" mà `menh-de-4` (A47) thêm lấy từ D53.K2, nằm TRONG 16 Điều của tập con (A47 chỉ tránh bộ thí điểm 30 đơn vị, không tránh tập con).
4. **Bước kiểm 2.7 trượt ở ckey4 (cần bạn quyết, dừng ở đây).** Cạnh chặn 1.5 D154 → D151.K1.d có từ gốc; theo A43 (`BLOCK_ALIAS`) đầu chặn `-P` kéo theo `not_applicable_P` chỉ khi có quy tắc nào đó kết luận dạng này. Từ mốc ND_152 (2021-02-15), ND_152 D7.K1 kết luận đúng dạng đó, nên danh sách chặn của D151.K1.d đổi mà tập ảnh hưởng A(e) (A42) không thấy. Lỗ hổng có sẵn trong thiết kế, chỉ lộ khi một quy tắc ở văn bản của mốc sau kết luận dạng tương đương của một đầu chặn cũ (kho mặc định và ckey, ckey2, ckey3 không có quy tắc như vậy ở mốc đó nên qua). Hướng có thể: (a) thêm vào N quan hệ "đơn vị có cạnh chặn mà đầu chặn có dạng tương đương với đầu mới xuất hiện ở mốc e" (đề xuất; cái giá: thêm một quan hệ cho A42, cần đo lại phần N cần); (b) bỏ điều kiện "chỉ khi có quy tắc kết luận dạng đó" ở A43, luôn thêm cả hai dạng (đơn giản, không phụ thuộc toàn cục; cái giá: thêm đầu chặn không ai kết luận, cần xem bộ quét có báo gì); (c) giữ nguyên, coi ckey4 là không dùng được. Chưa thử hướng nào.
5. **D154.K7, K9: điều kiện duy nhất là dẫn chiếu mở ("theo điều ước quốc tế", "trường hợp khác theo quy định của Chính phủ").** Đặc tả chưa nói làm sao; mỗi lần chạy model làm một kiểu: ckey giữ thành vị từ điều kiện riêng, ckey2 `bo_qua` điều kiện và giữ kết luận (thành miễn không điều kiện cho mọi người nước ngoài), ckey3 không ra quy tắc, ckey4 giữ thành vị từ điều kiện riêng như ckey (`under_international_treaty_vietnam_is_member`, `under_government_regulation`). Đề xuất: thêm luật "điều kiện duy nhất là dẫn chiếu mở thì giữ thành vị từ điều kiện riêng" (như ckey), vì miễn không điều kiện là sai nghĩa nặng nhất.
6. **Giữ lời nhắc nào, có dựng lại cả bộ luật không.** Không bản nào trội hẳn (bảng 3d). Dựng lại cả bộ luật mất ~1h23 (1.6A) + ~2h11 (1.6B) + 1.7, 1.8. Đề xuất: chưa dựng lại cho tới khi phân xử mục 4 và 5.
7. **Lần sửa 4 (phủ định kép) chưa chạy.** Đã chuẩn bị số đo "quy tắc ngược nghĩa" (`utils/llm_runs/count_inverted_negation.py`), điểm yếu: danh sách từ do agent tự đặt, đã sót "insufficient", "failure" một lần. Lỗi này làm ngược nghĩa quy tắc thật (ví dụ ckey2 D153.K2 `forced_exit :- -lack_work_permit`, trục xuất người CÓ giấy phép). Không chạy vì 2.7 đang trượt: chạy tiếp thì đi qua bước kiểm chỉ nhờ may về tên.
8. **Rào chắn lớn nhất của hỏi đáp là 1.9 và 1.6B, không phải 1.6A.** 1.9 dịch câu hỏi thành dữ kiện không khớp vị từ chủ thể gộp (ckey2: `foreign_worker` + `work_in_vietnam` so với `foreign_worker_working_in_vietnam`; log 1.6B đã cảnh báo "86/127 chữ không có ứng viên, tái dùng sẽ thấp"), và 1.9 đổi cách hỏi giữa các lần (ckey3 hỏi Q01-Q05 bằng `exempt_from_work_permit`). Chưa sửa.
9. **Chưa kiểm:** không có lần chạy lặp (chưa biết mức nhiễu); vì sao D154.K8 có dòng điều kiện ở 1.6A mà quy tắc vẫn mất điều kiện (ckey2); 12 lỗi cổng 1.6A gốc của ckey4 (ckey3: 0) chưa đọc tay; M2 lùi ở D151.K1 trong ckey4. Lỗi "trường thiếu [] / thừa [" đã rõ: dòng thiếu trường bắt buộc của khuôn (thấy khi cho ví dụ D37 gọn qua `gate_unit`).
