# Kế hoạch dựng cơ sở tri thức thích nghi theo văn bản dưới luật: Bộ luật Lao động (bàn giao cho agent local, 6/11/2026, cập nhật 8/11/2026)

## 0. Đọc trước

- **File này dùng để làm gì:** agent local (Claude Code trong repo của học viên) đọc để dựng hệ thống. Đây không phải tài liệu viết luận văn. Học viên tự viết phần Method.
- **Trạng thái:** phần A (A1–A6) đã chạy được trên lĩnh vực cũ. Với Bộ luật Lao động thì chưa dựng gì. Chưa có `run_all.py`, wrapper gọi LLM, `docs/llm_config.md`. Sổ khái niệm chưa làm.
- **Hết hiệu lực:** `KeHoach_TangToc_T11_2026-11-03`, `KeHoach_HoanThanh_2026-11-03`, `DeCuong_NopTruong_2026-11-03` (lịch, bộ dữ liệu, đánh giá, lĩnh vực). Mọi dữ liệu dev và bộ sửa đổi giả định cũ bỏ.
- **Vẫn dùng** (tài liệu tham chiếu đặt ở `docs/ref/` trong repo):
  - Cách làm và quy ước code phần A: `docs/ref/KetQua_A1_A4_2026-10-22.md`, `docs/ref/KetQua_A5_2026-10-23.md`. Chỉ lấy quy ước, cách kiểm và giới hạn đã ghi. Số liệu, đường dẫn, mã `BLDS2015` là của lĩnh vực cũ.
  - Quy tắc sổ khái niệm R1–R4: `HuongDan_SoKhaiNiem_R1R4_2026-11-03`, có chỉnh ở L7 (L7 đổi tên bốn quy tắc theo việc, ghi kèm tên cũ).
  - Căn cứ pháp lý của động cơ cập nhật (đã đọc toàn văn): Luật Ban hành VBQPPL 64/2025/QH15 (bản gốc 19/02/2025) Điều 8, 53, 55–58; NĐ 78/2025/NĐ-CP Điều 4, 9, 63, 65–69 (bản trong LawCodex, NĐ 187/2025 chỉ sửa khoản 1 Điều 68 trong nhóm này).
  - Phát hiện trên toàn văn: `docs/ref/KhaoSat_BLLD_ToanVan_2026-11-05.md`. Mục 4 chỉ liệt kê dạng A của điều khoản giao chi tiết (thiếu dạng B, D, E; xem mục 3). Phần "Đã chốt" và bảng mục 1 cũ hơn plan và manifest; lệch thì theo plan và manifest.
  - Nguồn từng văn bản: cột `nguon` của manifest. Không dùng `BaoCao_ChonLuat_NghiDinh_2026-11-05` (báo cáo chọn luật, phần đề xuất trong đó đã bị plan này thay).
  - Bảng kê văn bản: `manifest.csv` trong gói dữ liệu.
- **Không làm trong đợt này:** bộ câu hỏi, gán nhãn, đánh giá M1–M4, viết paper. Nhưng log của L11 phải đủ để sau này tính M1–M4 mà không chạy lại.

## 1. Quyết định đã chốt

| # | Quyết định |
|---|---|
| L1 | Trọng tâm: cơ sở tri thức (KB) **thích nghi khi văn bản dưới luật áp vào**. Ngoại lệ lồng nhau là phụ. Hỏi đáp là demo chính. |
| L2 | Luật thử nghiệm: Bộ luật Lao động 45/2019/QH14. **KB ban đầu chỉ dựng từ bản gốc 45/2019.** Mọi văn bản khác (nghị định, thông tư, nghị quyết, bản hợp nhất) là **sự kiện nạp** theo đúng ngày có hiệu lực. |
| L3 | Hai nhóm sự kiện. **dev**: agent được thấy khi dựng. **heldout**: để ngoài repo, chỉ nạp khi đo. **Mọi loại thay đổi có ca thật trong kho đều có ít nhất một ca trong dev và, nếu kho có ca thứ hai, một ca trong heldout** (bảng phủ ở L6). Bản 6/11 sửa cách chia cũ "dev đến hết 2024" vì cách đó để 6 loại thay đổi không có ca nào trong dev. |
| L4 | Phạm vi văn bản: BLLĐ; văn bản căn cứ BLLĐ hoặc hướng dẫn văn bản đó; danh mục nghề nặng nhọc (TT 11/2020, TT 19/2023, căn cứ Luật ATVSLĐ nhưng BLLĐ dùng); NQ 66.16, 66.18 (Chính phủ, theo cơ chế đặc biệt của NQ 206/2025/QH15). Văn bản của luật khác (BHXH, ATVSLĐ, Việc làm…) để ngoài. |
| L5 | Lọc nội dung: **tách cấu trúc toàn văn mọi văn bản** (liên kết sửa đổi có thể trỏ vào bất kỳ điều nào). **Trích quy tắc chỉ cho điều nội dung** (điều kiện, quyền và nghĩa vụ, mức, thời hạn, ngoại lệ, chế tài, hiệu lực, chuyển tiếp). Bỏ điều hồ sơ, thủ tục, trách nhiệm cơ quan, biểu mẫu. Phụ lục: chỉ nạp **danh mục làm đổi kết quả**. Bỏ "Mẫu số…" và danh mục địa bàn vùng lương (câu hỏi sẽ ghi sẵn vùng). |
| L6 | LLM: Gemini Flash bản free. LLM chỉ hỗ trợ hiểu ngữ nghĩa. Regex và code trước, LLM chỉ khi regex không bắt được. |
| L7 | **Không có người duyệt tay.** Dùng các cổng tự động đã có (đoạn trích khớp nguyên văn, vị từ trong sổ, biên dịch s(CASP), bộ quét lỗi, LLM thứ hai trích lại độc lập). Không qua thì gắn cờ hoặc cô lập; câu hỏi dính mục cô lập thì từ chối trả lời. |
| L8 | Mâu thuẫn, ba lớp: (a) sửa đổi tường minh = thay phiên bản, không coi là mâu thuẫn; (b) mâu thuẫn ngầm: chỉ áp hai nguyên tắc của Luật 64/2025 Điều 58: **văn bản có hiệu lực pháp lý cao hơn** (khoản 3) và **cùng một cơ quan thì văn bản ban hành sau**, so theo **ngày ban hành**, không theo ngày hiệu lực (khoản 4). Điều 58 không có nguyên tắc chuyên biệt nên không áp tự động. Quy tắc áp dụng riêng do chính văn bản đặt (NQ 66.16 Điều 19 khoản 3; NQ 66.18 Điều 7 khoản 3, có ngoại lệ "trừ khoản 4"; Luật 71/2025 Điều 50 khoản 3, ưu đãi hơn thì áp mức có lợi nhất) ghi vào cấu hình, căn cứ khoản 6 Điều 58; (c) không giải được → cô lập. |
| L9 | Thời gian: mỗi phiên bản đơn vị có `issued`, `effective_from`, `effective_to`, `applies_from` (hồi tố), cho phép nhiều khoảng hiệu lực, trạng thái `pending_event` (hiệu lực có điều kiện), hiệu lực có thời hạn. Câu hỏi có ngày sự việc → dùng phiên bản có hiệu lực tại ngày đó. Không có ngày → **ngày hỏi**, không phải bản ban hành mới nhất. |
| L10 | Định danh kỹ thuật bằng tiếng Anh. Lõi dùng chung; phần theo lĩnh vực = văn bản + sổ khái niệm + cấu hình. Không giữ giá trị cứng của lĩnh vực cũ trong code. |

## 2. Dữ liệu

**Hai gói** (học viên tải từ chat):
- `kb_corpus.zip` → giải nén vào `data/raw/labor/` trong repo. Gồm `base/`, `dev/`, `manifest.csv`.
- `kb_heldout.zip` → **giữ ngoài repo** (ví dụ `~/kltn_heldout/`). Agent không được biết đường dẫn này cho đến lúc đo.

Tất cả là `.txt` UTF-8, chuẩn NFC, tên file = `doc_id`. File gốc dạng markdown đã bỏ dấu markdown. Nội dung pháp lý không sửa.

| Nhóm | doc_id (hiệu lực) |
|---|---|
| base | BLLD_45-2019 (01/01/2021) |
| dev (17) | ND_90-2019 (01/01/2020), ND_28-2020 (15/4/2020), ND_135-2020 (01/01/2021), TT_10-2020 (01/01/2021), ND_145-2020 (01/02/2021), ND_152-2020 (15/02/2021), TT_11-2020 (01/3/2021), TT_09-2020 (15/3/2021), ND_12-2022 (17/01/2022), TT_18-2021 (01/02/2022), ND_70-2023 (18/9/2023), TT_19-2023 (15/02/2024), ND_74-2024 (01/7/2024), ND_219-2025 (07/8/2025), VBHN_125-2025 (cập nhật luật 01/01/2026), NQ_66-16-2026 (15/4/2026), ND_283-2026 (10/9/2026) |
| heldout (8) | ND_128-2025 (01/7/2025), ND_293-2025 (01/01/2026), ND_337-2025 (01/01/2026), VBHN_18-2026 (cập nhật luật 01/01/2026 và 01/7/2026), NQ_66-18-2026 + phụ lục I.4 (20/5 và 01/7/2026), ND_371-2026 (15/11/2026), ND_399-2026 (01/01/2027) |

Hai nhóm xen kẽ nhau về ngày. Khi dựng, agent chỉ chạy dev theo thứ tự ngày. Khi đo, chạy toàn bộ dòng thời gian (dev + heldout) theo thứ tự ngày.

**Quan hệ chờ đích** (thay hai cờ `target_not_loaded` / `target_outside_corpus` của bản 6/11). Agent chỉ thấy manifest dev, nên lúc dựng không phân biệt được "đích có trong kho nhưng chưa nạp" (ví dụ ND_219 cho hết hiệu lực một phần ND_128 thuộc heldout) với "đích ngoài kho". Vì vậy mọi cạnh trỏ tới văn bản hoặc đơn vị chưa có trong KB đều ghi vào `pending_links.jsonl` (nguồn, loại cạnh, số hiệu đích, mã đơn vị đích nếu có, câu nguyên văn). Mỗi lần nạp một văn bản, so số hiệu của nó với danh sách này; khớp thì tự nối cạnh, ghi vào log sự kiện, rồi áp lại chỉ thị (ví dụ bãi bỏ) với ngày hiệu lực gốc của chỉ thị. Phân biệt "ngoài kho" chỉ làm ở báo cáo cuối: quan hệ còn chờ sau lần nạp cuối.

Ngày chốt dữ liệu: 05/11/2026. Cột `quan_he` và `ghi_chu` trong manifest ghi quan hệ đã biết của từng văn bản; dùng làm mốc kiểm, **không** dùng làm đầu vào cho pipeline (pipeline phải tự suy ra từ chữ văn bản).

**Vấn đề dữ liệu đã biết (agent phải xử lý, không được bỏ qua im lặng):**
1. TT_09, TT_10, TT_11 lấy từ repo GitHub đã tách điều: **mất phần đầu** (số hiệu, ngày ký, căn cứ). Header phải lấy từ manifest, gắn cờ `header_from_manifest`.
2. ND_90-2019 và ND_28-2020 ban hành theo **BLLĐ 2012**. Cụm "Bộ luật Lao động" trong hai văn bản này trỏ bản 2012 (không có trong kho, số điều khác). Không được nối vào số điều của BLLĐ 2019.
3. Đích ngoài kho: NĐ 38/2022 (bị ND_74 thay), NĐ 35/2022 (ND_70 bãi bỏ một phần), TT 54/2015 (TT_18 thay), BLLĐ 2012, NĐ 189/2025 (ND_283 Điều 66 khoản 2 chờ văn bản sửa nó). Ghi vào quan hệ chờ đích, nút `external:<số hiệu>`.
4. Trường tình trạng của nguồn không tin được: metadata LawCodex của NĐ 28/2020 ghi `status: in_force`, `legal_force: InForce`, nhưng ND_12-2022 Điều 62 khoản 2 cho hết hiệu lực từ 17/01/2022. **Hiệu lực tính từ chữ văn bản, không từ metadata.**
5. Bản hợp nhất cũng có lỗi: VBHN_125 ghi "các điều 89, 193 và 197" ở khoản 4 Điều 185 (gốc là 189); VBHN_18 đã sửa lại. Khi so phiên bản phải báo khác biệt kiểu này thành cờ `consolidation_discrepancy`, không coi là sửa đổi luật.
6. VBHN_125 có nội dung chú thích ở cuối; VBHN_18 không có. Ngày hiệu lực từng khoản bị sửa lấy từ chú thích (125) hoặc từ cột `quan_he` (18). **Không lấy ngày ký bản hợp nhất làm ngày hiệu lực.**
7. NQ_66-16-2026 **thiếu Phụ lục I.7** (phần sửa Điều 21–28 ND_145). Chuỗi phiên bản Điều 21–28 ND_145 có một bước hở. NQ_66-18 Điều 4 lại bãi bỏ các phần của phụ lục đó.
8. Biến thể chính tả giữa các nguồn: "ủy/uỷ", "thỏa/thoả", "hòa/hoà", dấu chấm cuối dòng, xuống dòng. So 45/2019 → 125 → 18 theo dòng thô ra 12 điều "khác", chỉ 4 điều đổi nội dung thật (Điều 59, 61, 139, 154).
9. Bảng (lương tối thiểu theo vùng) bị trải thành từng dòng một ô. Parser phải dựng lại bảng. Mốc kiểm vùng I: 4.960.000 (ND_74), 5.310.000 (ND_293), 5.700.000 (ND_399).
10. Văn bản không nêu số hiệu đích:
    - TT_19 bổ sung danh mục của TT_11 nhưng **không nhắc "11/2020" lần nào**, chỉ trùng tên danh mục ("Danh mục nghề, công việc nặng nhọc, độc hại, nguy hiểm…") và cùng căn cứ Luật ATVSLĐ.
    - ND_74, ND_293, ND_399 chỉ ghi "Căn cứ Bộ luật Lao động", phạm vi điều chỉnh không nêu Điều 91, dù NĐ 78/2025 Điều 65 khoản 2 yêu cầu nêu (ND_293, ND_399 ra sau NĐ 78).
11. Phụ lục của NQ 66.16/66.18 đánh số kiểu "khoản B.IX Mục 1 Phụ lục I.7", "phần D", "Mẫu số 02", không theo Điều/Khoản. Parser phụ lục và giải dẫn chiếu phải nhận dạng này.

## 3. Mô hình dữ liệu

**Văn bản (`documents.jsonl`):** `doc_id`, `number`, `doc_type`, `issuer`, `level` (luật/bộ luật = 1; nghị định, nghị quyết Chính phủ = 2; thông tư = 3), `issued`, `effective_from`, `effective_to`, `status`, `source`, `flags`.

**Mã đơn vị:** `<doc_id>.D154.K8a.b`. Điều/khoản/điểm có hậu tố chữ (`D2a`, `K8a`, `D20a`) là bình thường. Phụ lục: `<doc_id>.PL1.M2.R15` (phụ lục, mục, dòng danh mục).

**Phiên bản đơn vị (`versions.jsonl`, mở rộng A4):** `id`, `version`, `text` (gốc), `text_norm` (đã chuẩn hoá), `effective_from`, `effective_to`, `applies_from`, `intervals` (danh sách khoảng nếu nhiều khoảng), `status` ∈ {`in_force`, `not_yet`, `pending_event`, `expired`, `suspended`}, `trigger` (với `pending_event`: mô tả nguyên văn sự kiện kích hoạt + văn bản đã khớp nếu có), `source_event`.

**Cạnh.** Giữ: `contains`, `part_of`, `refers_to`, `exception_of`, `amends`, `replaces`, `repeals`. Thêm:

| Cạnh | Nghĩa | Ví dụ thật |
|---|---|---|
| `based_on` | văn bản/đơn vị căn cứ vào đơn vị khác | TT_18 → ND_145.D68.K2 |
| `details` | quy định chi tiết một điều khoản giao chi tiết của luật | TT_10 → BLLD.D21 (khoản 1–3), D73.K4, D142.K1 |
| `expires_by_topic` | cho hết hiệu lực một phần theo chủ đề, không theo số điều | ND_219.D35.K2 → phần LĐNN của ND_152 |
| `triggers` | văn bản mới kích hoạt điều khoản hiệu lực có điều kiện | ND_371 → ND_283.D66.K3 |
| `overrides` | áp dụng thay văn bản khác trong một khoảng thời gian | NQ_66-18 PL I.4 Mục C → ND_145.D20–D28 (không thực hiện thủ tục giấy phép cho thuê lại), D15 (ký quỹ 2 tỷ), D19 |
| `supplements_list` | bổ sung dòng vào danh mục, không sửa chữ cũ | TT_19 → TT_11 danh mục |

Đối chiếu tên của thầy (giữ bảng cũ): `amends` = sửa_đổi_bổ_sung, `replaces` = thay_thế, `repeals` = bãi_bỏ, `refers_to` = dẫn_chiếu_đến, `exception_of` = là_ngoại_lệ_của, `contains`/`part_of` = chứa_khoản/thuộc_điều. Thêm: `details` = quy_định_chi_tiết, `based_on` = căn_cứ.

**Điều khoản giao chi tiết (`delegation_clauses.jsonl`, bản 6/11 gọi là "ô giao quyền"/`slots`):** đơn vị của luật có cụm giao cấp dưới quy định chi tiết, theo chữ của NĐ 78/2025 Điều 65 khoản 2 ("điều, khoản giao quy định chi tiết"). Đếm lại ngày 8/11 trên BLLĐ gốc (bỏ đoạn trích trong Điều 219) ra **năm dạng câu**:

| Dạng | Mẫu | Đếm được | Ví dụ |
|---|---|---|---|
| A | "Chính phủ / Bộ trưởng … quy định…" (bỏ "… quy định tại") | 39 cụm, 37 điều | Điều 91 khoản 4 "Chính phủ quy định chi tiết Điều này" |
| B | "theo quy định của Chính phủ / Bộ trưởng …" | 10 cụm, 8 điều (35, 36, 68, 151, 154, 166, 173, 218) | **Điều 154 khoản 1, 2, 9** ("9. Trường hợp khác theo quy định của Chính phủ") |
| C | "do Chính phủ / Bộ trưởng quy định" | 2 cụm (Điều 107, 116), đã nằm trong A | |
| D | "Bộ trưởng … ban hành [danh mục]" | Điều 61, 142, 143, 146, 160 | **Điều 142 khoản 1** (TT_10 quy định chi tiết) |
| E | "Thủ tướng Chính phủ quyết định …" | Điều 112 | ngày nghỉ lễ cụ thể |

Tổng khoảng 55 cụm ở khoảng 50 điều. Con số "39 cụm / 37 điều" của bản 6/11 và của `KhaoSat_BLLD_ToanVan` mục 4 **chỉ là dạng A**, bỏ sót đúng Điều 154 khoản 9, chỗ ND_152 Điều 7 lấp vào. Số đếm trên là regex thô, chưa lọc ca không phải giao chi tiết (ví dụ Điều 129 "Chính phủ công bố…", Điều 133 "Chính phủ quyết định Chương trình…"); agent tự đếm lại, báo số theo từng dạng, và ghi ca bị loại cùng lý do. Trường: `clause_id`, `unit_id`, `pattern` (A–E), `delegate` (Chính phủ/Bộ trưởng/Thủ tướng), `phrase`, `filled_by` (danh sách đơn vị văn bản dưới luật, theo thời gian).

**Quan hệ chờ đích (`pending_links.jsonl`):** xem mục 2.

**Sự kiện (`events/<event_id>.json`):** `event_id`, `doc_id`, `effective_date`, `actions` (từng chỉ thị đã áp), `units_touched`, `units_new`, `units_closed`, `rules_reextracted`, `rules_unchanged`, `flags`, `isolated`, `llm_calls`, `runtime_s`.

## 4. Các bước

Mỗi thẻ: mục tiêu, đầu vào, đầu ra, cổng, sai thì thấy gì. Tên file theo kiểu phần A (`src/<step>_*.py`, `data/processed/`, `docs/<step>_report.txt`); đổi được nhưng ghi lại một lần.

### L0. Chuẩn bị repo
- Cấu hình lĩnh vực `config/domain_labor.yaml`: đọc manifest, bảng `level`, từ khoá điều khoản giao chi tiết, quy tắc áp dụng riêng (L8b).
- Bỏ mọi giá trị cứng của lĩnh vực cũ (tiền tố mã, bảng `EXPECTED` của A5, tên file) → đọc từ manifest và cấu hình.
- `src/llm.py`: một wrapper duy nhất; đọc `docs/llm_config.md` (model ID, temperature, ngày khoá); lưu phản hồi thô `data/llm_cache/`; đếm lượt theo ngày; chạm giới hạn thì dừng gọn và chạy tiếp được hôm sau từ cache.
- `run_all.py` chạy mọi bước đến bước chỉ định.
- **Cổng:** chạy A1–A5 trên BLLD_45-2019 ra 220 Điều, A5 xanh; test cũ chỉnh sang dữ liệu mới vẫn xanh.
- **Sai thì thấy gì:** số đơn vị/Điều lệch manifest; test A5 dựa bảng cứng cũ báo lỗi tên file.

### L1. Tách cấu trúc (mở rộng A1)
- Đầu vào: một file `.txt` + dòng manifest.
- Làm:
  - đọc header (số hiệu, loại, cơ quan, ngày ký, các dòng "Căn cứ…") bằng regex, so với manifest, lệch thì cờ;
  - Phần/Chương/Mục/Tiểu mục/Điều/Khoản/Điểm, hậu tố chữ, điểm "đ". Theo NĐ 78/2025 Điều 69 khoản 4: điều, khoản bổ sung đánh số "số + chữ" (`Điều 20a`, `khoản 8a`); **điểm bổ sung đánh số "chữ + số"** (`điểm a1`, `điểm đ2`). Regex phải nhận cả hai;
  - **khối trong ngoặc kép “…”** sau "như sau:" là nội dung sửa đổi (payload), không phải đơn vị của văn bản chứa nó. Ví dụ Điều 219 BLLĐ chứa nguyên "Điều 32. Những tranh chấp…" của luật khác; ND_70 chứa nguyên "Điều 4. Sử dụng người lao động nước ngoài";
  - phụ lục: tách dòng danh mục và các mục đánh số kiểu "B.IX", "Mục 1", "phần D" (vấn đề dữ liệu 11); bỏ biểu mẫu (`Mẫu số …`), nhưng giữ một nút `form` để cạnh sửa đổi có chỗ trỏ;
  - dựng lại bảng bị trải dòng (ND_74/293/399 Điều 3).
- Đầu ra: `a1_units_<doc_id>.jsonl` (hoặc giữ tên cũ), `documents.jsonl`.
- **Cổng:** số Điều = cột `so_dieu_dem_duoc` của manifest (ND_145: 115, BLLD: 220, ND_283: 68, ND_12: 64…); A5 bước 1–2 xanh cho mọi văn bản; **mọi dẫn chiếu trỏ vào phụ lục (của chính văn bản hoặc văn bản khác đã nạp) giải được về một nút phụ lục**. Cổng đếm Điều không bắt được lỗi tách phụ lục, nên cần cổng này.
- **Sai thì thấy gì:** số Điều thừa (khối trích dẫn bị tách thành điều); dòng lương tối thiểu không nằm cùng vùng; "khoản B.IX Mục 1 Phụ lục I.7" không giải được.

### L2. Dẫn chiếu trong và giữa văn bản (mở rộng A2)
- Nội bộ: như A2, thêm đích có hậu tố chữ (lỗi đã biết của A2 cũ: không nhận "Điều 621a" làm đích).
- Giữa văn bản: "Điều X của Bộ luật Lao động", "khoản 2 Điều 68 Nghị định số 145/2020/NĐ-CP", "Nghị định này", "Thông tư số …". Giải `doc_id` theo số hiệu. Chỉ ghi "Bộ luật Lao động" không kèm số: chọn bản theo ngày ký văn bản nguồn (trước 20/11/2019 → BLLĐ 2012, ngoài kho).
- Đích chưa có trong KB → quan hệ chờ đích (mục 2), tự nối khi văn bản đích được nạp.
- **Cổng:** mọi dẫn chiếu hoặc giải được, hoặc nằm trong quan hệ chờ đích, hoặc gắn cờ `unresolved` (không đọc được số hiệu hay số điều); không cạnh trỏ mã không tồn tại; mốc: ND_152.D7 có `refers_to` → BLLD.D154. Báo cáo: số quan hệ chờ đích được nối ở các lần nạp sau, số còn chờ sau lần nạp cuối.
- **Sai thì thấy gì:** ND_28 nối nhầm vào BLLĐ 2019; cạnh tới `K8a` bị rơi.

### L3. Điều khoản giao chi tiết và cạnh `details` / `based_on`
- Quét BLLD lấy `delegation_clauses.jsonl` theo cả năm dạng A–E (mục 3).
- Mỗi văn bản dưới luật: dòng "Căn cứ …" → `based_on`; điều "Phạm vi điều chỉnh" + cụm "quy định chi tiết … khoản X Điều Y" → `details` tới điều khoản giao chi tiết hoặc đơn vị (NĐ 78/2025 Điều 65 khoản 2 bắt văn bản nêu, nhưng vấn đề dữ liệu 10 cho thấy không phải văn bản nào cũng nêu). Còn lại LLM đề xuất từ tiêu đề điều của văn bản dưới luật và danh sách điều khoản giao chi tiết, kết quả gắn cờ `llm_proposed`.
- **Kiểm cạnh `llm_proposed`** (không có người duyệt): (1) một lượt LLM độc lập bằng model khác đề xuất lại, không thấy kết quả lượt đầu; (2) kiểm từ khoá chung: cụm danh từ chính của phạm vi điều chỉnh (ví dụ "mức lương tối thiểu") phải xuất hiện trong chữ đơn vị luật đích. Cả hai đạt → giữ cạnh, cờ `llm_proposed` còn nguyên. Một trong hai trượt → cạnh bị cô lập, không dùng khi hỏi đáp.
- **Cổng (mốc biết trước):** `delegation_clauses` phải có ít nhất BLLD.D91.K4 (dạng A), BLLD.D154.K1, K2, K9 (dạng B), BLLD.D142.K1 (dạng D), BLLD.D112 (dạng E); ND_152 `details` BLLD.D154.K1, K2, K9, D157, D150.K3 (Điều 1 ND_152 nêu đủ, nên regex phải bắt được, không cần LLM); TT_18 `based_on` ND_145.D68.K2; TT_10 `details` BLLD.D21 (K1–K3), D73.K4, D142.K1; ND_135 `details` BLLD.D169 (chữ văn bản có nêu số điều); ND_74 `details` BLLD.D91 (chữ văn bản **không** nêu số điều, chỉ "Căn cứ Bộ luật Lao động ngày 20 tháng 11 năm 2019", nên mốc này đo phần LLM của L3 và phải qua được bước kiểm trên); mỗi nghị định/thông tư dev có ít nhất một `based_on`.
- **Sai thì thấy gì:** hỏi đáp không tìm được quy định chi tiết (ví dụ mức lương tối thiểu) dù văn bản đã nạp.

### L4. Phân loại điều nội dung / thủ tục
- Nhãn: `substantive`, `procedural` (hồ sơ, trình tự, thủ tục), `authority` (trách nhiệm/thẩm quyền cơ quan), `form`, `effect_transition` (hiệu lực, chuyển tiếp, bãi bỏ), `definition`.
- Regex theo tiêu đề điều trước; không chắc thì LLM phân loại theo lô.
- `effect_transition` luôn giữ và luôn chuyển cho L6. `definition` chuyển cho L7. Chỉ `substantive` (cộng `definition`) đi vào trích quy tắc.
- **Cổng:** báo cáo phân bố nhãn theo văn bản và 10 điều mẫu ngẫu nhiên. Không bắt học viên duyệt.
- **Sai thì thấy gì:** điều có điều kiện thật bị nhãn `procedural` → câu hỏi về điều đó ra "ngoài phạm vi".

### L5. Ngoại lệ tường minh (A3/A6 cho mọi văn bản)
- Như A3/A6 cũ, chạy trên mọi văn bản đã nạp; ngoại lệ trỏ sang văn bản khác dùng giải đích của L2.
- **Cổng (mốc):** BLLD.D151.K1.d ("Có giấy phép lao động…, trừ trường hợp quy định tại Điều 154") → `exception_of` từ BLLD.D154; BLLD.D37 → BLLD.D36.K1.b; BLLD.D35 → D29, D97.
- **Sai thì thấy gì:** chuỗi miễn giấy phép lao động (Điều 151 → 154 → nghị định Điều 7) đứt ở tầng đầu.

### L6. Động cơ cập nhật (mở rộng A4) — phần lõi của đợt này
Mỗi văn bản nạp vào là một sự kiện. Pipeline tự đọc chỉ thị từ chữ văn bản. Các loại phải xử lý:

**Bảng phủ.** Framework phải xử lý **mọi** loại dưới đây, kể cả loại chưa có ca thật. "Ca dev" là ca agent dùng để dựng và kiểm; "ca heldout" là ca chưa thấy, dùng để đo.

| # | Loại | Ca dev | Ca heldout |
|---|---|---|---|
| 1 | Sửa đổi, bổ sung khoản/điểm "như sau" | ND_70 Điều 1 khoản 1–11 | — (kho không có ca thứ hai) |
| 2 | Bổ sung khoản/điểm/điều mới (kể cả hậu tố chữ) | ND_70 "Bổ sung khoản 3 Điều 6"; VBHN_125 khoản 8a Điều 154 | VBHN_18 |
| 3 | Thay cụm từ tại nhiều vị trí | ND_70 Điều 1 khoản 13 | — |
| 4 | Bãi bỏ điểm/khoản/đoạn | ND_70 Điều 1 khoản 14, Điều 2 (đích ngoài kho) | ND_293 Điều 5 khoản 3 (bãi bỏ một phần ND_128) |
| 5 | Thay cả văn bản qua điều hiệu lực | ND_12 → ND_28; ND_74 → NĐ 38/2022 (ngoài kho); ND_283 → ND_12 | ND_293 → ND_74; ND_399 → ND_293 |
| 6 | Văn bản hướng dẫn mới lấp điều khoản giao chi tiết | ND_135, ND_145, ND_152, TT_09, TT_10 | ND_337 |
| 7 | Văn bản hướng dẫn văn bản hướng dẫn (chuỗi 3 tầng) | TT_18 → ND_145 Điều 68 khoản 2 → BLLĐ | — |
| 8 | Bổ sung danh mục, không sửa chữ cũ | TT_19 → TT_11 (khớp qua tên danh mục, TT_19 không nêu số hiệu TT_11; vấn đề dữ liệu 10) | — |
| 9 | Quy định chuyển tiếp | ND_12 Điều 63; ND_70 Điều 3; ND_283 Điều 67; ND_219 Điều 34 | ND_293 Điều 5 khoản 5 |
| 10 | Hết hiệu lực theo chủ đề | ND_219 Điều 35 khoản 2 | ND_371 Điều 13 khoản 2 |
| 11 | Hiệu lực có điều kiện: trạng thái chờ | ND_283 Điều 66 khoản 2, 3 | — |
| 12 | Hiệu lực có điều kiện: văn bản kích hoạt | — (trong dev, ND_283 Điều 66 khoản 3 phải **vẫn chờ**) | ND_371 kích hoạt ND_283 Điều 66 khoản 3 |
| 13 | Hiệu lực có thời hạn, tự hết khi có văn bản thay | NQ_66-16 Điều 19 | NQ_66-18 Điều 7 |
| 14 | Áp dụng thay văn bản khác trong thời hạn | NQ_66-16 Điều 19 khoản 3 (thiếu Phụ lục I.7 nên chỉ kiểm được cơ chế, không kiểm được nội dung) | NQ_66-18 Điều 7 khoản 3 (có "trừ khoản 4") + PL I.4 Mục C |
| 15 | Cập nhật cấp luật qua bản hợp nhất | VBHN_125 | VBHN_18 |
| 16 | Văn bản bãi bỏ một phần phụ lục của văn bản khác | — | NQ_66-18 Điều 4 → phụ lục NQ_66-16 |
| 17 | Ban hành nhưng chưa có hiệu lực tại ngày hỏi | ND_145 (ký 14/12/2020, hiệu lực 01/02/2021); ND_283 (ký 15/7, hiệu lực 10/9/2026) | ND_399 |
| 18 | Văn bản dưới luật ban hành theo luật cũ còn áp dụng | ND_90, ND_28 (theo BLLĐ 2012) | — |

**Loại framework phải có mà kho không có ca thật.** Agent viết code và test bằng đoạn văn bản tự soạn ngắn trong `tests/fixtures/` (chỉ để kiểm code, không phải dữ liệu thực nghiệm, không được trộn vào `data/`). Luận văn ghi các loại này là "đã cài đặt, chưa có ca thật để đo":

| # | Loại | Cách xử lý |
|---|---|---|
| 19 | Hồi tố (`applies_from` sớm hơn `effective_from`; Luật 64 Điều 55, Điều 58 khoản 2) | câu hỏi có ngày sự việc trong khoảng hồi tố dùng bản mới. Luật cấm hồi tố khi đặt trách nhiệm pháp lý mới hoặc nặng hơn (Điều 55 khoản 2): ca như vậy gắn cờ, không áp |
| 20 | Đính chính văn bản (NĐ 78 Điều 9) | đính chính không được đổi nội dung, nên không tạo phiên bản pháp lý mới; ghi cạnh `corrects`, giữ cả hai chữ |
| 21 | Tạm ngưng hiệu lực hoặc đình chỉ thi hành, toàn bộ hoặc một phần (Luật 64 Điều 8, Điều 56) | trạng thái `suspended` với khoảng. Luật bắt văn bản ghi rõ thời điểm tạm ngưng và tiếp tục có hiệu lực (Điều 56 khoản 2), nên lấy ngày từ chữ; đình chỉ không ghi ngày kết thúc thì `suspended` mở đến khi có văn bản xử lý |
| 22 | Đánh số lại điều/khoản, câu "… trở thành …" | ánh xạ mã cũ → mã mới, cạnh `renumbered_to`; dẫn chiếu cũ đi theo ánh xạ |
| 23 | Danh sách số trần ("Điều 5, 6 và 8"; "các khoản 1, 2, 4") | tách thành từng đích (lỗi đã biết của A4 cũ) |
| 24 | Văn bản bị cơ quan có thẩm quyền bãi bỏ vì trái luật | như bãi bỏ, nguồn là văn bản xử lý; cờ `annulled` |
| 25 | Văn bản được hướng dẫn bị sửa đổi hoặc thay thế | không tự đóng văn bản hướng dẫn: Luật 64 Điều 57 khoản 2 cho nó tiếp tục có hiệu lực nếu không trái văn bản mới, trừ khi được **công bố** hết hiệu lực (NĐ 78 Điều 4 khoản 5). Cờ `parent_changed`; quy tắc chỉ dùng tiếp nếu không mâu thuẫn văn bản mới (L8b); văn bản công bố hết hiệu lực nạp như loại 4/5 |
| 26 | Thay cả văn bản bằng văn bản cùng tên (không có điều hiệu lực nêu rõ) | hiếm, vì Luật 64 Điều 8 khoản 3 và NĐ 78 Điều 67 khoản 3 bắt liệt kê cụ thể văn bản bị thay. Không tự đóng; cờ `possible_replacement`, LLM đề xuất |

Câu chỉ thị không thuộc loại nào ở hai bảng → `unknown_directive`, báo lỗi, không đoán.

**Chỗ tìm câu chỉ thị.** Luật 64 Điều 8 khoản 3 và NĐ 78 Điều 66–67, 69–70 bắt câu sửa đổi, bãi bỏ, thay thế, chuyển tiếp, hiệu lực nằm ở điều khoản thi hành hoặc ở văn bản sửa đổi một số điều, và phải nêu rõ đích. Regex tìm ở đó trước. Các dạng câu thật đã thấy trong kho LawCodex (NĐ 187/2025): "Sửa đổi, bổ sung một số điểm, khoản của Điều 7 như sau:" (một câu dẫn, nhiều chỉ thị con), "Bổ sung Mục 3a vào sau Mục 3", "Sửa đổi tên Điều 54", "Bổ sung, bãi bỏ một số từ, cụm từ, khoản của Nghị định số …". Chép các câu này vào `tests/fixtures/` làm test cho regex (không phải dữ liệu KB).

- **Chuẩn hoá trước khi so:** NFC, gộp khoảng trắng và xuống dòng, bỏ dấu chấm cuối dòng, thống nhất kiểu bỏ dấu (ủy/uỷ, hòa/hoà, thỏa/thoả), bỏ số chú thích `[n]`. Thay đổi chỉ về chuẩn hoá thì **không** tạo phiên bản mới.
- **Câu chỉ thị lạ:** báo lỗi, không đoán (giữ nguyên tinh thần A4 cũ), cờ `unknown_directive`. LLM chỉ được đề xuất phân loại; đề xuất gắn cờ `llm_proposed`.
- **Loại 10 (theo chủ đề):** LLM đề xuất danh sách đơn vị thuộc chủ đề, kết quả gắn cờ. Đơn vị không chắc → `suspended` + cờ, không đóng hẳn.
- **Loại 11–12:** đơn vị vào `pending_event`, lưu nguyên văn mô tả sự kiện. Mỗi lần nạp văn bản mới, so mô tả với văn bản đó (regex số hiệu/tên trước, LLM sau). Khớp → `in_force` từ ngày hiệu lực văn bản kích hoạt, cạnh `triggers`.
- **Loại 15:** so `text_norm` từng đơn vị giữa hai bản hợp nhất liên tiếp. Ngày hiệu lực lấy từ chú thích (VBHN_125) hoặc cột `quan_he` của manifest (VBHN_18, khi đo), không lấy ngày ký bản hợp nhất. Khác biệt không do luật sửa (vấn đề dữ liệu 5) → cờ `consolidation_discrepancy`.
- **Không xoá nút.** Đóng phiên bản bằng `effective_to`.
- **Cổng dev** (sau khi nạp đủ 17 sự kiện dev, theo thứ tự ngày):
  - mỗi loại 1–18 có ca dev trong bảng phủ đều có test chạy trên ca đó; loại 12, 16 (chỉ có ca heldout) và loại 19–26 (không có ca thật) có test trên fixture;
  - ND_152: phần LĐNN đóng hoặc `suspended` từ 07/8/2025 (ND_219), phần người VN làm cho tổ chức nước ngoài vẫn `in_force`;
  - ND_283 Điều 66 khoản 2, 3 ở trạng thái `pending_event` đến hết chuỗi dev; ND_12 đóng từ 10/9/2026;
  - BLLD.D154 có khoản 8a từ 01/01/2026 (VBHN_125), các đơn vị khác của BLLĐ không đổi phiên bản vì khác biệt chính tả; khoản 4 Điều 185 bị cờ `consolidation_discrepancy`;
  - NQ_66-16 có khoảng hiệu lực 15/4/2026–28/02/2027 và cạnh `overrides` (đích chưa đủ vì thiếu Phụ lục I.7, gắn cờ);
  - A5 cùng kiểm phiên bản (4a–4e) xanh;
  - ND_152.D7.K6 và D7.K14 có version 2 từ 18/9/2023; ND_152.D8.K2 đổi cụm "khoản 4, 6 và 8 Điều 154" thành "khoản 4 và khoản 6 Điều 154" từ 18/9/2023;
  - mọi đơn vị ND_28 có `effective_to` = 2022-01-17;
  - TT_11 có dòng danh mục mới từ 15/02/2024, dòng cũ không đổi phiên bản;
  - không còn `unknown_directive` chưa có quyết định;
  - chạy lại cả chuỗi dev hai lần ra file giống hệt (từ cache).
- **Sai thì thấy gì:** câu hỏi về thời điểm trước sửa đổi trả theo bản sau; đơn vị bị đổi phiên bản vì khác "ủy/uỷ"; danh mục cũ của TT_11 bị đóng khi nạp TT_19.

### L7. Sổ khái niệm (bước B) cho BLLĐ và điều nội dung đã nạp
- Giữ bốn quy tắc và kiểm C1–C4 của `HuongDan_SoKhaiNiem_R1R4`, đổi tên theo việc và chạy theo thứ tự sau (tên cũ trong ngoặc):
  1. **Gạch cụm** (R3): lấy nguyên văn các cụm chủ thể, điều kiện, ngoại lệ, kết luận của từng đơn vị. Regex đánh dấu trước từ báo hiệu ("nếu", "khi", "trường hợp", "trừ", "không áp dụng", "phải", "được", "bị coi là"…); LLM gạch cụm; cụm nào không phải chuỗi con nguyên văn của đơn vị thì bị loại.
  2. **Phân loại** (R1): `concept` nếu có đơn vị nêu khi nào X đúng (neo vào đơn vị đó), ngược lại `input`.
  3. **Kiểm dữ kiện thô** (R2): giả sử người hỏi nêu thẳng X, có bỏ qua được điều luật nào không; có thì X phải là `concept`, và phải gọi tên được điều bị bỏ qua.
  4. **Một khái niệm một tên** (R4): tra sổ theo cụm tiếng Việt, tên tiếng Anh, chữ ký trước khi tạo vị từ mới; gần nghĩa thì tách, không gộp.
- Kiểm: C1 đơn vị có từ báo hiệu điều kiện thì có ít nhất một dòng; C2 mỗi `input` được dùng ít nhất một lần; C3 không `input` nào trùng tên hay bí danh với `concept`; C4 lượt trích độc lập bằng model khác, mục lệch thì cờ. C1 chỉ bắt đơn vị bị sót hẳn; cụm bị sót bên trong một đơn vị chỉ C4 có thể bắt.
- Chỉnh so với hướng dẫn cũ:
  - phạm vi bước Phân loại: "có đơn vị nào trong BLLĐ hoặc văn bản đã nạp nêu khi nào X đúng không";
  - vai tham số mới thay bảng cũ: `W` người lao động, `E` người sử dụng lao động, `C` hợp đồng lao động, `J` nghề/công việc, `G` vùng, `D` ngày/mốc, `A` số tiền/số lượng;
  - **không làm tay, không duyệt tay:** LLM nháp theo lô, C1–C3 bằng script, C4 bằng một model khác hoặc một lượt độc lập; mục lệch C4 → cờ; cụm mơ hồ về nghĩa pháp lý → ghi "?" vào danh sách hỏi, không tự quyết.
- **Số liệu trong bảng và danh mục không đi qua LLM:** mức lương tối thiểu theo vùng, mốc tuổi nghỉ hưu, dòng danh mục nghề → dựng thành fact trực tiếp từ bảng đã tách ở L1 (ví dụ `min_wage_month(G, A)`, `listed_heavy_job(J)`), gắn phiên bản theo văn bản nguồn.
- Đóng băng sổ (tag) trước khi nạp heldout. Sau đó mọi thay đổi ghi `docs/so_changelog.md`; sổ chỉ được mở rộng tự động khi văn bản heldout cần vị từ mới, và mỗi lần như vậy ghi vào log sự kiện.
- **Sai thì thấy gì:** một khái niệm hai tên → quy tắc không nối; khái niệm bị xếp `input` → điều định nghĩa không bao giờ được dùng.

### L8. Ngoại lệ ngầm (bước C)
- **Đồ thị khái niệm** (bước B3 của `KeHoach_TangToc_T11`): cạnh `uses` (đơn vị → vị từ nó dùng) và `anchored_to` (vị từ `concept` → đơn vị định nghĩa nó). Từ đồ thị này còn ra **tập vị từ được phép** của mỗi điều: vị từ của chính điều cộng vị từ của các điều láng giềng qua nút khái niệm (dùng ở L9).
- **Cặp ứng viên:** hai đơn vị cùng dùng một nút `concept`, bỏ cặp đã có cạnh ngoại lệ tường minh (L5).
- LLM xét từng cặp: rebut (kết luận ngược), undercut (chặn việc áp dụng) hoặc không có quan hệ, kèm câu bằng chứng nguyên văn. Bộ quét kiểm hai đầu tồn tại, không trùng cạnh tường minh, không tạo vòng. Không có người duyệt; cờ giữ nguyên trong KB.
- **Rủi ro số cặp:** khái niệm chung (người lao động, người sử dụng lao động, hợp đồng lao động) có ở hầu hết 220 điều và các nghị định. Trước khi gọi LLM, báo số cặp. Vượt hạn mức LLM thì chỉ giữ cặp có kết luận ngược dấu hoặc cặp mà một bên dùng kết luận của bên kia làm điều kiện, ghi cách lọc vào báo cáo.

### L9. Trích quy tắc, quét, tự sửa, cô lập (bước D)
- Chỉ đơn vị `substantive`/`definition`; vị từ chỉ lấy từ tập được phép của đồ thị khái niệm.
- Ưu tiên giữa quy tắc theo L8: cấp văn bản (`level`); cùng cơ quan thì văn bản có **ngày ban hành** sau; quy tắc áp dụng riêng trong cấu hình; còn lại cô lập.
- Bộ quét (5 loại từ `KeHoach_TangToc_T11` bước D2, thêm 2 loại theo thời gian): (1) quy tắc không bao giờ kích hoạt (vị từ thân không phải `input` và không là đầu của quy tắc nào); (2) quy tắc trùng; (3) quan hệ đứt sau cập nhật; (4) vòng chặn, bắt buộc, vì vòng lẻ làm mọi câu hỏi "không có mô hình"; (5) cặp kết luận ngược nhau không có quan hệ chặn hay ưu tiên; (6) quy tắc dùng đơn vị đã hết hiệu lực tại mọi thời điểm; (7) quy tắc phụ thuộc đơn vị `pending_event` mà không có điều kiện thời gian.
- Tự sửa tối đa hai vòng; nhận khi biên dịch được, không sinh cờ mới, không làm hỏng mốc biết trước; không sửa được → cô lập.
- **Sai thì thấy gì:** hai quy tắc kết luận ngược nhau ở cùng thời điểm mà không có quan hệ ưu tiên (quét loại 5); quy tắc của ND_28 còn được dùng sau 17/01/2022.

### L10. s(CASP) và hỏi đáp theo ngày (bước E)
- Biên dịch theo ngày hỏi: chỉ phiên bản có hiệu lực tại ngày đó; `pending_event` chưa kích hoạt và `not_yet` không vào chương trình; `overrides` chỉ có tác dụng trong khoảng của nó.
- Câu hỏi → dữ kiện bằng vị từ `input` của sổ (LLM); không biểu diễn được → "ngoài phạm vi".
- Kết quả: mỗi câu chạy cả P và ¬P → kết luận được / bị bác / chưa đủ căn cứ; dính đơn vị hoặc cạnh bị cô lập → "hệ thống không trả lời" kèm danh sách mục cô lập. Kèm chuỗi căn cứ (văn bản, đơn vị, phiên bản, ngày hiệu lực). Giải thích điền mẫu câu từ cây chứng minh.
- **Báo phiên bản mới hơn:** nếu một phiên bản trong chuỗi căn cứ đã có phiên bản kế tiếp tại ngày hỏi, câu trả lời thêm một dòng "Quy định này đã được sửa đổi/thay thế bởi <văn bản, đơn vị> từ ngày <ngày>." Dòng này lấy từ chuỗi phiên bản, không qua LLM, và không đổi kết luận.
- **Mốc demo:** cùng một câu "chuyên gia nước ngoài vào Việt Nam 45 ngày trong năm có phải có giấy phép lao động không", (một chuyến, không thuộc trường hợp miễn nào khác), ngày sự việc 01/6/2025 → phải có (ND_152 Điều 7 khoản 8 chỉ miễn khi dưới 30 ngày và không quá 03 lần/năm); ngày 01/10/2025 → được miễn (ND_219 Điều 7 khoản 13 điểm a: tổng dưới 90 ngày/năm; chạy được ngay trên chuỗi dev). Câu "lương 5.500.000 đồng/tháng ở vùng I có thấp hơn mức tối thiểu không", hỏi ngày 05/11/2026 → không (ND_293); ngày 15/01/2027 → có (ND_399).

### L11. Chạy cập nhật tăng dần
- `src/update_runner.py --events <thư mục> --until <ngày>`: nạp sự kiện theo thứ tự ngày hiệu lực; với mỗi sự kiện: L1–L5 trên văn bản mới, L6 áp chỉ thị, chạy lại L7–L9 **chỉ** trên đơn vị bị chạm cộng đơn vị nối với chúng qua `details`, `refers_to`, `exception_of`, đồ thị khái niệm; quét lại; biên dịch lại; ghi `events/<event_id>.json` (mục 3).
- Chế độ `--rebuild`: dựng lại từ đầu đến cùng ngày, để sau này so chi phí và kết quả với chạy tăng dần (M3).
- **Cổng:** chuỗi dev chạy tăng dần và `--rebuild` đến 10/9/2026 (sự kiện dev cuối) cho cùng tập quy tắc có hiệu lực tại ngày đó (khác biệt nào cũng phải giải thích được trong báo cáo).
- **Sai thì thấy gì:** chạy tăng dần đúng ở bước đầu nhưng lệch `--rebuild` ở cuối chuỗi → cập nhật cục bộ bỏ sót đơn vị liên quan.

## 5. Thứ tự

L0 → L1 → L2 → L3 → L4 → L5 → L6 (chuỗi dev) → L7 → L8 → L9 → L10 → L11 (dev).

Heldout chỉ nạp sau khi L11 dev qua cổng và sổ đã đóng băng. Mốc ngoài: thực nghiệm xong trước tháng 12/2026. Agent báo tiến độ theo cổng, không theo ngày.

## 6. LLM

- Chỉ dùng ở: phân loại chỉ thị lạ (L6), hết hiệu lực theo chủ đề (L6), khớp sự kiện kích hoạt (L6), liên kết `details` còn sót và lượt kiểm độc lập của nó (L3), phân loại điều không chắc (L4), sổ khái niệm (L7), ngoại lệ ngầm (L8), trích quy tắc (L9), câu hỏi → dữ kiện (L10).
- Model: Gemini Flash bản free. Ghi đúng model ID, temperature, ngày khoá vào `docs/llm_config.md`. Hạn mức đo ngày 3/11: 3.8 Flash khoảng 20 lượt/ngày, 3.5 Flash-Lite khoảng 500 lượt/ngày; hạn mức free có thể đổi, wrapper phải tự đếm và dừng gọn. Gom nhiều đơn vị mỗi lượt. Lượt kiểm độc lập (L3, C4 ở L7) dùng model khác lượt chính.
- Free tier gửi dữ liệu cho Google: văn bản luật công khai nên chấp nhận; ghi vào phần hạn chế.
- Con số nào vào luận văn cũng phải tính lại được từ `data/llm_cache/` mà không gọi model.

## 7. Luật làm việc cho agent

Mẫu brief mỗi bước (giữ từ kế hoạch cũ):
```
# Bước <mã>: <tên>
Mục tiêu (1 câu):
Đầu vào (đường dẫn, định dạng):
Đầu ra (đường dẫn, schema từng trường):
Model: <theo llm_config.md>
Làm:
Không được: đọc thư mục heldout; sửa data/raw; tự đặt vị từ ngoài sổ; đoán câu chỉ thị lạ;
            lấy hiệu lực từ metadata thay vì chữ văn bản; đổi tên trường
Tự kiểm trước khi báo xong: mỗi kiểm có một test âm; chạy run_all.py
Báo cáo docs/<mã>_report.txt: số dòng vào/ra, số cờ theo loại, 5 mẫu ngẫu nhiên,
            lệnh chạy lại, số lượt LLM đã gọi
```
- Một bước = một nhánh git + một báo cáo. Gộp vào `main` khi học viên chép được "ba câu" của bước vào `docs/ON_TAP.md`: (1) đầu vào là gì; (2) đầu ra là gì, ý nghĩa một dòng; (3) sai thì thấy ở đâu.
- Câu hỏi pháp lý không chắc: ghi vào danh sách hỏi, không để agent tự quyết.

## 8. Việc treo (không chặn)

1. Phụ lục I.7 của NQ 66.16/2026 (phần sửa Điều 21–28 ND_145).
2. Văn bản ngoài kho: NĐ 38/2022, NĐ 35/2022, TT 54/2015, BLLĐ 2012, NĐ 189/2025. Luật 64/2025 đã đọc từ bản gốc 19/02/2025; chưa kiểm luật sửa đổi Luật 64 (nếu có) có chạm Điều 8, 53–58 không.
3. Luật sửa đổi Bộ luật Lao động và 4 luật khác đang ở kỳ họp Quốc hội (bế mạc 21/11/2026). Thông qua thì thêm vào cuối heldout làm lần cập nhật chưa thấy.
4. Ngày ký TT 09/2020 và TT 10/2020 (manifest ghi `?`).
5. Loại 1, 3, 7, 8, 11, 18 chỉ có một ca thật trong kho, nên chỉ kiểm được trên dev, không có ca chưa thấy để đo. Loại 12 và 16 chỉ có ca heldout, nên trong dev chỉ kiểm trên fixture. Loại 19–26 không có ca thật. Ba nhóm này ghi vào phần hạn chế; tìm thêm văn bản thì bổ sung ca.

Điều gì sẽ chứng minh kế hoạch này sai: chuỗi dev chạy tăng dần không ra cùng kết quả với `--rebuild`, hoặc phần lớn văn bản dưới luật không nối được `details`/`based_on` vào Bộ luật bằng regex và LLM. Khi đó KB không biết nghị định nào quy định chi tiết điều khoản nào của luật, và không có gì để gọi là thích nghi.
