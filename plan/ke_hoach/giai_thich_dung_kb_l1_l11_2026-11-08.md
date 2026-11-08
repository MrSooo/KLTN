# Giải thích từng bước dựng KB (L0–L11), 8/11/2026

Tài liệu để học viên hiểu hệ thống trước khi viết Method. Mỗi bước có: làm gì, đầu vào, các việc cụ thể, đầu ra (kèm một bản ghi mẫu), kiểm gì, hỏng thì thấy gì.

Quy ước:
- Giá trị trong bản ghi mẫu (số hiệu, ngày, chữ luật) là thật, đã đối chiếu toàn văn ngày 8/11.
- Tên trường lấy theo plan `KeHoach_KB_LaoDong_Agent_2026-11-06` (bản 8/11).
- Tên vị từ và quy tắc ghi **(minh hoạ)** vì chưa có sổ khái niệm thật.

Ví dụ dùng xuyên suốt: *chuyên gia nước ngoài vào Việt Nam làm việc 45 ngày trong năm có phải xin giấy phép lao động không?*
- BLLĐ Điều 151 khoản 1 điểm d: phải "có giấy phép lao động…, trừ trường hợp quy định tại Điều 154".
- BLLĐ Điều 154 khoản 9: "Trường hợp khác theo quy định của Chính phủ".
- ND_152 Điều 7 khoản 8 (từ 15/02/2021): miễn nếu dưới 30 ngày **và** không quá 03 lần/năm. 45 ngày thì không miễn.
- ND_219 Điều 7 khoản 13 điểm a (từ 07/8/2025): miễn nếu tổng dưới 90 ngày/năm. 45 ngày thì miễn.

Hệ thống phải trả lời "phải có giấy phép" cho ngày sự việc 01/6/2025 và "được miễn" cho ngày 01/10/2025, mà không ai sửa tay khi nạp ND_219.

---

## L0. Chuẩn bị repo

**Làm gì:** dựng khung để các bước sau chạy được trên dữ liệu lao động thay cho dữ liệu thừa kế cũ.

**Việc cụ thể:**
1. Tạo `config/domain_labor.yaml`. File này ghi: đường dẫn manifest, bảng cấp văn bản (luật = 1, nghị định/nghị quyết Chính phủ = 2, thông tư = 3), các mẫu câu giao chi tiết, các quy tắc áp dụng riêng (NQ 66.16 Điều 19 khoản 3, NQ 66.18 Điều 7 khoản 3, Luật 71/2025 Điều 50 khoản 3).
2. Gỡ các giá trị viết cứng của lĩnh vực cũ trong code (tiền tố mã `BLDS2015`, bảng số kỳ vọng của A5, tên file). Các giá trị này giờ đọc từ manifest và cấu hình.
3. Viết `src/llm.py`, một hàm duy nhất để gọi Gemini:
   - đọc model và temperature từ `docs/llm_config.md`;
   - lưu mọi phản hồi vào `data/llm_cache/`;
   - đếm số lượt mỗi ngày, chạm hạn mức thì dừng gọn;
   - chạy lại thì lấy từ cache, không gọi lại model.
4. Viết `run_all.py`: chạy tuần tự từ đầu đến bước được chỉ định.

**Đầu ra:** `config/domain_labor.yaml`, `src/llm.py`, `docs/llm_config.md`, `run_all.py`.

**Kiểm:** chạy A1–A5 cũ trên BLLĐ ra đúng 220 Điều, A5 không báo lỗi.

**Hỏng thì thấy gì:** A5 báo lỗi tên file vì còn bảng số cứng của lĩnh vực cũ.

---

## L1. Tách cấu trúc

**Làm gì:** biến một file văn bản thành danh sách đơn vị (Điều, Khoản, Điểm, dòng phụ lục), mỗi đơn vị có mã, chữ và đơn vị cha. Đồng thời đọc thông tin đầu văn bản.

**Đầu vào:** một file `.txt` trong `data/raw/labor/` và dòng tương ứng trong `manifest.csv`.

**Việc cụ thể:**
1. **Đọc đầu văn bản bằng regex:** số hiệu, loại văn bản, cơ quan, ngày ký, các dòng "Căn cứ…". So với manifest, lệch thì gắn cờ. Ba thông tư TT_09, TT_10, TT_11 bị mất phần đầu nên lấy từ manifest, gắn cờ `header_from_manifest`.
2. **Tách đơn vị theo cách đánh số luật quy định** (NĐ 78/2025 Điều 63): Phần, Chương, Mục, Tiểu mục, Điều ("Điều 7."), Khoản ("8."), Điểm ("a)", "đ)"). Phải nhận được:
   - điều, khoản chèn thêm có hậu tố chữ: "Điều 20a", "khoản 8a";
   - điểm chèn thêm có hậu tố số: "điểm a1" (NĐ 78 Điều 69 khoản 4).
3. **Nhận đoạn trích sửa đổi.** Đoạn trong ngoặc kép sau "như sau:" là chữ mới sẽ thay vào văn bản khác, nên không được tách thành đơn vị của văn bản đang đọc. Đoạn này lưu riêng làm "nội dung sửa đổi" để L6 dùng. Ví dụ: ND_70 chứa nguyên chữ mới của "Điều 4. Sử dụng người lao động nước ngoài" thuộc ND_152.
4. **Tách phụ lục.** Danh mục tách thành từng dòng. Nhận dạng cách đánh số của phụ lục NQ 66.16/66.18 như "B.IX", "Mục 1", "phần D". Biểu mẫu ("Mẫu số 01") chỉ giữ một nút rỗng.
5. **Ghép lại bảng bị vỡ.** Bảng lương vùng (Điều 3 của ND_74, ND_293, ND_399) trong file txt bị trải thành mỗi ô một dòng, phải ghép lại thành bảng vùng → mức lương.

**Đầu ra:**
- `data/processed/a1_units_<doc_id>.jsonl`, một đơn vị mỗi dòng:
  ```json
  {"id": "ND_152-2020.D7.K8", "type": "khoan", "parent": "ND_152-2020.D7", "number": "8",
   "text": "Vào Việt Nam làm việc tại vị trí nhà quản lý, giám đốc điều hành, chuyên gia hoặc lao động kỹ thuật có thời gian làm việc dưới 30 ngày và không quá 03 lần trong 01 năm."}
  ```
- `data/processed/documents.jsonl`, một văn bản mỗi dòng:
  ```json
  {"doc_id": "ND_152-2020", "number": "152/2020/NĐ-CP", "doc_type": "nghi_dinh", "issuer": "Chính phủ",
   "level": 2, "issued": "2020-12-30", "effective_from": "2021-02-15",
   "grounds": ["Căn cứ Bộ luật Lao động ngày 20 tháng 11 năm 2019", "..."], "flags": []}
  ```
- Bảng đã ghép (minh hoạ dạng): `{"table": "ND_293-2025.D3.K1", "rows": [{"vung": "I", "muc_thang": 5310000}, ...]}`.

**Kiểm:**
- Số Điều bằng cột `so_dieu_dem_duoc` của manifest (BLLĐ 220, ND_145 115, ND_152 30…).
- Mỗi đơn vị có đúng một cha.
- Mọi dẫn chiếu vào phụ lục đều tìm được nút phụ lục tương ứng.

**Hỏng thì thấy gì:** thừa Điều vì đoạn trích bị tách thành điều; mức lương bị gán sai vùng.

---

## L2. Dẫn chiếu

**Làm gì:** tìm mọi câu nhắc tới đơn vị khác ("theo quy định tại khoản 2 Điều 68 Nghị định số 145/2020/NĐ-CP") và nối thành cạnh `refers_to`.

**Đầu vào:** đơn vị từ L1 của mọi văn bản đã nạp.

**Việc cụ thể:**
1. Regex bắt cụm dẫn chiếu: "khoản X Điều Y", "Điều Y của Bộ luật này", "Nghị định số …", "Nghị định này". NĐ 78 Điều 68 bắt dẫn chiếu ghi rõ số điều, khoản và tên văn bản, nên phần lớn cụm có dạng đều.
2. Đổi số hiệu văn bản thành `doc_id` trong KB.
3. **Ca chỉ ghi "Bộ luật Lao động" không có số:** xem ngày ký của văn bản đang đọc. Ký trước 20/11/2019 thì là BLLĐ 2012, nằm ngoài kho. ND_90 và ND_28 thuộc ca này nên không được nối vào số điều của BLLĐ 2019.
4. **Đích chưa có trong KB** (văn bản chưa nạp hoặc ngoài kho) thì ghi vào danh sách **quan hệ chờ đích**. Mỗi lần nạp văn bản mới, so số hiệu của nó với danh sách này; khớp thì tự nối cạnh và áp lại chỉ thị đi kèm.

**Đầu ra:**
- `data/processed/a2_refs.jsonl`:
  ```json
  {"s": "ND_152-2020.D7", "p": "refers_to", "o": "BLLD_45-2019.D154", "evidence": "…Điều 154 của Bộ luật Lao động…"}
  ```
- `data/processed/pending_links.jsonl`:
  ```json
  {"source": "ND_219-2025.D35.K3", "edge": "repeals", "target_number": "128/2025/NĐ-CP",
   "target_units": ["D8", "Phụ lục II Mục 2"],
   "text": "Điều 8 và Mục 2 Phụ lục II ban hành kèm theo Nghị định số 128/2025/NĐ-CP … hết hiệu lực thi hành kể từ ngày Nghị định này có hiệu lực."}
  ```

**Kiểm:** mọi dẫn chiếu thuộc một trong ba trạng thái: đã nối, đang chờ đích, hoặc cờ `unresolved` (không đọc được số). Không có cạnh nào trỏ tới mã không tồn tại. Báo cáo số quan hệ chờ đích đã được nối ở lần nạp sau và số còn chờ sau lần nạp cuối.

**Hỏng thì thấy gì:** ND_28 bị nối nhầm sang BLLĐ 2019; dẫn chiếu tới "khoản 8a" bị rơi.

---

## L3. Điều khoản giao chi tiết, cạnh `based_on` và `details`

**Làm gì:** xác định văn bản dưới luật nào quy định chi tiết điều khoản nào của BLLĐ. Thiếu bước này thì nạp nghị định vào, KB vẫn không biết nó dùng để trả lời câu hỏi về điều nào của luật.

**Đầu vào:** BLLĐ (đã qua L1) và các văn bản dưới luật (đã qua L1, L2).

**Việc cụ thể:**
1. **Quét BLLĐ tìm điều khoản giao chi tiết.** Năm dạng câu:

   | Dạng | Mẫu | Ví dụ thật |
   |---|---|---|
   | A | "Chính phủ / Bộ trưởng … quy định…" | Điều 91 khoản 4 "Chính phủ quy định chi tiết Điều này" |
   | B | "theo quy định của Chính phủ" | Điều 154 khoản 9 "Trường hợp khác theo quy định của Chính phủ" |
   | C | "do Chính phủ quy định" | Điều 107, 116 |
   | D | "Bộ trưởng … ban hành [danh mục]" | Điều 142 khoản 1 |
   | E | "Thủ tướng Chính phủ quyết định…" | Điều 112 |

   Đếm thô ra khoảng 55 cụm ở khoảng 50 điều. Riêng dạng A là 39 cụm ở 37 điều. Bản trước chỉ đếm dạng A nên sót Điều 154 khoản 9.
2. **Đọc dòng "Căn cứ…"** của văn bản dưới luật thành cạnh `based_on`. Ví dụ TT_18 ghi "Căn cứ khoản 2 Điều 68 Nghị định số 145/2020/NĐ-CP".
3. **Đọc điều "Phạm vi điều chỉnh"** thành cạnh `details`. NĐ 78 Điều 65 khoản 2 bắt văn bản nêu cụ thể điều khoản được giao. Ví dụ:
   - ND_152 Điều 1 nêu "khoản 1, 2 và 9 Điều 154", "Điều 157", "khoản 3 Điều 150";
   - TT_10 Điều 1 nêu "khoản 1, 2 và 3 Điều 21", "khoản 4 Điều 73", "khoản 1 Điều 142".
4. **Văn bản không nêu số điều thì LLM đề xuất.** ND_74, ND_293, ND_399 chỉ ghi "Căn cứ Bộ luật Lao động" và phạm vi "quy định mức lương tối thiểu", không nhắc Điều 91. LLM nhận tiêu đề các điều của nghị định và danh sách điều khoản giao chi tiết, rồi đề xuất đích. Kết quả gắn cờ `llm_proposed`.
5. **Kiểm đề xuất của LLM:**
   - một lượt LLM khác (model khác) đề xuất lại mà không thấy kết quả lượt đầu;
   - cụm danh từ chính của phạm vi ("mức lương tối thiểu") phải có trong chữ điều luật đích. Điều 91 có tiêu đề "Mức lương tối thiểu" nên đạt.
   - Hai lượt khớp và từ khoá đạt thì giữ cạnh; không thì cạnh bị cô lập.

**Đầu ra:**
- `data/processed/delegation_clauses.jsonl`:
  ```json
  {"clause_id": "DC_BLLD_154_9", "unit_id": "BLLD_45-2019.D154.K9", "pattern": "B", "delegate": "Chính phủ",
   "phrase": "Trường hợp khác theo quy định của Chính phủ", "filled_by": ["ND_152-2020.D7", "ND_219-2025.D7"]}
  ```
- Cạnh trong `data/processed/l3_links.jsonl`:
  ```json
  {"s": "ND_152-2020", "p": "details", "o": "BLLD_45-2019.D154.K9", "how": "regex", "evidence": "khoản 1, 2 và 9 Điều 154 của Bộ luật Lao động"}
  {"s": "ND_74-2024", "p": "details", "o": "BLLD_45-2019.D91", "how": "llm", "flags": ["llm_proposed"], "check": {"second_llm": "agree", "keyword": "mức lương tối thiểu"}}
  ```

**Kiểm:**
- `delegation_clauses` có ít nhất BLLĐ Điều 91 khoản 4, Điều 154 khoản 1, 2, 9, Điều 142 khoản 1, Điều 112.
- ND_152 `details` Điều 154 khoản 1, 2, 9, Điều 157, Điều 150 khoản 3, bắt bằng regex.
- ND_74 `details` Điều 91, qua được bước kiểm LLM.
- Mỗi văn bản dưới luật có ít nhất một `based_on`.

**Hỏng thì thấy gì:** hỏi về lương tối thiểu mà hệ thống không tìm thấy mức lương dù ND_74 đã nạp; câu hỏi giấy phép lao động không đi xuống được tới ND_152 Điều 7.

---

## L4. Phân loại điều

**Làm gì:** gắn mỗi Điều một nhãn để biết điều đó đi tiếp tới bước nào.

**Đầu vào:** đơn vị cấp Điều từ L1 (tiêu đề và chữ).

**Việc cụ thể:**
1. Regex trên tiêu đề điều trước: "Hiệu lực thi hành", "Quy định chuyển tiếp" → `effect_transition`; "Hồ sơ…", "Trình tự, thủ tục…" → `procedural`; "Trách nhiệm của…" → `authority`; "Giải thích từ ngữ" → `definition`.
2. Điều chưa xếp được thì gom lô cho LLM phân loại.
3. Mỗi nhãn đi một đường:

   | Nhãn | Ví dụ | Đi đâu |
   |---|---|---|
   | `substantive` | ND_152 Điều 7 "Trường hợp người lao động nước ngoài không thuộc diện cấp giấy phép lao động" | trích quy tắc (L9) |
   | `definition` | điều "Giải thích từ ngữ" | neo khái niệm (L7), trích quy tắc |
   | `effect_transition` | ND_219 Điều 35 "Hiệu lực thi hành" | nguồn câu chỉ thị cho L6 |
   | `procedural` | điều về hồ sơ, trình tự | giữ chữ, không trích quy tắc |
   | `authority` | điều trách nhiệm của bộ, ngành | giữ chữ, không trích quy tắc |
   | `form` | "Mẫu số 01" | chỉ giữ nút |

   Mọi điều vẫn nằm trong KB, vẫn có phiên bản và vẫn làm đích sửa đổi được. Nhãn chỉ quyết định điều đó có được dịch thành quy tắc không. Lý do không trích quy tắc từ điều thủ tục: các điều này không cho câu trả lời có/không, mà trích thì tốn hạn mức LLM.

**Đầu ra:** `data/processed/l4_labels.jsonl`:
```json
{"id": "ND_219-2025.D35", "label": "effect_transition", "how": "regex", "heading": "Hiệu lực thi hành"}
```

**Kiểm:** báo cáo phân bố nhãn theo từng văn bản, kèm 10 điều mẫu ngẫu nhiên.

**Hỏng thì thấy gì:** một điều có điều kiện thật bị nhãn `procedural`, nên câu hỏi về nó ra "ngoài phạm vi".

---

## L5. Ngoại lệ ghi rõ trong chữ

**Làm gì:** tìm câu "trừ trường hợp quy định tại…", "không áp dụng đối với…" và tạo cạnh `exception_of`.

**Đầu vào:** đơn vị từ L1, dẫn chiếu đã giải từ L2.

**Việc cụ thể:**
1. Dùng mẫu câu của A3/A6 cũ cho mọi văn bản đã nạp.
2. Giải đơn vị đích bằng L2.
3. Phân biệt "trừ trường hợp các bên có thoả thuận khác" (không có đích là đơn vị) với "trừ trường hợp quy định tại Điều X" (có đích). BLLĐ có 42 cụm ngoại lệ: 11 loại thoả thuận khác, 16 ngoại lệ trong cùng điều hoặc luật khác, 15 dẫn chiếu khoản/điều.

**Đầu ra:** `data/processed/a3_exceptions.jsonl`:
```json
{"s": "BLLD_45-2019.D154", "p": "exception_of", "o": "BLLD_45-2019.D151.K1.d",
 "evidence": "Có giấy phép lao động do cơ quan nhà nước có thẩm quyền của Việt Nam cấp, trừ trường hợp quy định tại Điều 154 của Bộ luật này."}
```

**Kiểm (mốc):** Điều 154 → Điều 151 khoản 1 điểm d; Điều 37 → Điều 36 khoản 1 điểm b; Điều 35 → Điều 29 và Điều 97.

**Hỏng thì thấy gì:** hệ thống kết luận "phải có giấy phép" cho mọi người nước ngoài, vì không có đường tới các trường hợp miễn.

---

## L6. Động cơ cập nhật (phần lõi)

**Làm gì:** khi nạp một văn bản mới, đọc các câu chỉ thị trong đó và đổi KB theo: mở phiên bản mới, đóng phiên bản cũ, đổi trạng thái đơn vị. Không xoá gì.

**Đầu vào:** văn bản mới đã qua L1–L5, KB hiện tại (các phiên bản và cạnh).

**Việc cụ thể:**
1. **Tìm câu chỉ thị** ở điều có nhãn `effect_transition` và ở các điều "Sửa đổi, bổ sung…". Luật 64/2025 Điều 8 khoản 3 bắt văn bản sửa đổi, bãi bỏ phải nêu rõ đích; NĐ 78 Điều 66–67 bắt các câu này nằm ở điều khoản thi hành.
2. **Đọc mỗi câu thành ba phần:**
   - động từ: sửa đổi, bổ sung, bãi bỏ, thay cụm từ, hết hiệu lực, có hiệu lực khi…;
   - đích: một hay nhiều đơn vị, có thể là danh sách số trần như "các khoản 1, 2, 4";
   - chữ mới: đoạn trích đã lưu ở L1.
3. **Giải đích** bằng L2. Đích chưa có trong KB thì vào quan hệ chờ đích.
4. **Xếp câu vào một trong 26 loại** (bảng ở plan, L6) và làm thao tác của loại đó trên tập phiên bản:
   - *Sửa, bổ sung chữ* (loại 1, 2, 3, 15): phiên bản cũ nhận `effective_to` = ngày hiệu lực của văn bản mới; phiên bản mới có `effective_from` = ngày đó. Đơn vị mới thì tạo nút mới.
   - *Bãi bỏ, thay cả văn bản* (loại 4, 5): đặt `effective_to` cho các đơn vị bị chạm, trạng thái `expired`.
   - *Hết hiệu lực theo chủ đề* (loại 10): câu không nêu số điều nên LLM đề xuất danh sách đơn vị, kết quả gắn cờ. Đơn vị không chắc thì chuyển `suspended`, không đóng hẳn.
   - *Hiệu lực có điều kiện* (loại 11, 12): đơn vị nhận trạng thái `pending_event`, lưu nguyên văn mô tả sự kiện. Mỗi văn bản mới nạp vào được so với mô tả này (regex số hiệu/tên trước, LLM sau); khớp thì đơn vị chuyển `in_force` và có cạnh `triggers`.
   - *Có thời hạn, áp dụng thay* (loại 13, 14): ghi khoảng hiệu lực; cạnh `overrides` chỉ có tác dụng trong khoảng đó.
   - *Chưa có hiệu lực* (loại 17): trạng thái `not_yet` cho tới ngày hiệu lực.
   - *Bổ sung danh mục* (loại 8): thêm dòng mới, cạnh `supplements_list`, dòng cũ giữ nguyên phiên bản.
   - *Chuyển tiếp* (loại 9): giữ thành đơn vị để L9 trích quy tắc.
   - *Các loại chưa có ca thật* (19–26: hồi tố, đính chính, tạm ngưng, đánh số lại…): xử lý theo bảng trong plan, kiểm bằng ví dụ tự soạn trong `tests/fixtures/`.
5. **Chuẩn hoá chữ trước khi so phiên bản:** NFC, gộp khoảng trắng, thống nhất "ủy/uỷ", "thỏa/thoả", "hòa/hoà", bỏ số chú thích. Chữ chỉ khác sau chuẩn hoá thì không tạo phiên bản mới. Lý do: so BLLĐ gốc với VBHN 125 và 18 theo dòng thô ra 12 điều "khác", nhưng chỉ 4 điều đổi nội dung thật (59, 61, 139, 154).
6. **Câu không thuộc loại nào** thì gắn `unknown_directive`. Hệ thống không đoán, và đơn vị bị câu đó chạm bị cô lập.
7. **Ghi log sự kiện.**

**Ví dụ trên chuỗi giấy phép lao động:**
- Nạp ND_70 (18/9/2023): một số khoản Điều 7 ND_152 (khoản 6, 14) có phiên bản 2 từ 18/9/2023. Khoản 8 không bị chạm.
- Nạp ND_219 (07/8/2025): Điều 35 khoản 2 ghi "Nội dung về lao động nước ngoài … quy định tại Nghị định số 152/2020/NĐ-CP … hết hiệu lực thi hành kể từ ngày Nghị định này có hiệu lực". Đây là loại 10. Các đơn vị lao động nước ngoài của ND_152, trong đó có Điều 7 khoản 8, được đóng từ 07/8/2025. Phần người Việt Nam làm cho tổ chức nước ngoài vẫn còn hiệu lực. ND_219 Điều 7 khoản 13 vào KB như đơn vị mới có hiệu lực từ 07/8/2025.

**Đầu ra:**
- `data/processed/versions.jsonl`, mỗi phiên bản một dòng:
  ```json
  {"id": "ND_152-2020.D7.K8", "version": 1, "text": "Vào Việt Nam làm việc … dưới 30 ngày và không quá 03 lần trong 01 năm.",
   "effective_from": "2021-02-15", "effective_to": "2025-08-07", "status": "expired",
   "source_event": "ND_219-2025", "flags": ["llm_proposed"]}
  {"id": "ND_219-2025.D7.K13.a", "version": 1, "text": "…tổng thời gian dưới 90 ngày trong 01 năm…",
   "effective_from": "2025-08-07", "effective_to": null, "status": "in_force"}
  ```
- `events/ND_219-2025.json`: `effective_date`, danh sách chỉ thị đã áp, `units_touched`, `units_new`, `units_closed`, `flags`, `isolated`, `llm_calls`.

**Kiểm (sau khi nạp đủ 17 văn bản dev theo thứ tự ngày):** danh sách đầy đủ ở plan. Một số mốc:
- ND_28 có `effective_to` = 2022-01-17;
- BLLĐ Điều 154 có khoản 8a từ 01/01/2026;
- ND_283 Điều 66 khoản 2, 3 vẫn `pending_event`;
- TT_11 có dòng danh mục mới từ 15/02/2024 mà dòng cũ không đổi;
- chạy lại cả chuỗi hai lần ra file giống hệt.

**Hỏng thì thấy gì:** hỏi ngày 01/6/2025 mà hệ thống trả theo ND_219; đơn vị bị đổi phiên bản chỉ vì khác "ủy/uỷ"; danh mục cũ của TT_11 bị đóng khi nạp TT_19.

---

## L7. Sổ khái niệm

**Làm gì:** lập danh sách tên mệnh đề (vị từ) dùng chung cho mọi quy tắc, để quy tắc trích từ các điều khác nhau nối được với nhau.

**Đầu vào:** đơn vị có nhãn `substantive` hoặc `definition`.

**Việc cụ thể** (bốn quy tắc theo thứ tự làm, tên cũ trong ngoặc):
1. **Gạch cụm** (R3). Với mỗi đơn vị, lấy nguyên văn các cụm thuộc bốn vai trò: chủ thể, điều kiện, ngoại lệ, kết luận.
   - Regex đánh dấu trước các từ báo hiệu: "nếu", "khi", "trường hợp", "trừ", "không áp dụng", "phải", "được", "bị coi là".
   - LLM gạch cụm.
   - Code kiểm mỗi cụm có phải chuỗi con nguyên văn của đơn vị không; không phải thì loại.
2. **Phân loại** (R1). Với mỗi cụm X: có đơn vị nào trong KB nêu khi nào X đúng không?
   - Có thì X là `concept`, neo vào đơn vị đó. Ví dụ "không thuộc diện cấp giấy phép lao động" có Điều 154 và ND_152/219 Điều 7 nêu điều kiện.
   - Không thì X là `input`, tức dữ kiện người hỏi tự nêu. Ví dụ "có thời gian làm việc dưới 30 ngày".
3. **Kiểm dữ kiện thô** (R2). Với mỗi `input`: nếu người hỏi nói thẳng X là đúng thì có bỏ qua được điều luật nào không? Có thì X phải là `concept`, và phải gọi tên được điều bị bỏ qua.
4. **Một khái niệm một tên** (R4). Trước khi tạo vị từ mới, tra sổ theo cụm tiếng Việt, tên tiếng Anh và số tham số. Cùng nghĩa thì dùng lại tên cũ; gần nghĩa thì tách riêng, không gộp.
5. **Tham số theo vai:** `W` người lao động, `E` người sử dụng lao động, `C` hợp đồng lao động, `J` nghề/công việc, `G` vùng, `D` ngày/mốc, `A` số tiền/số lượng.
6. **Số trong bảng không qua LLM.** Mức lương vùng, danh mục nghề thành fact thẳng từ bảng ở L1, gắn phiên bản theo văn bản nguồn.
7. **Đóng băng sổ** (tag git) trước khi nạp heldout. Sau đó mọi thay đổi ghi `docs/so_changelog.md`.

**Đầu ra:**
- `data/processed/b1_r3_rows.jsonl`, mỗi cụm một dòng:
  ```json
  {"unit": "ND_152-2020.D7.K8", "span": "có thời gian làm việc dưới 30 ngày", "role": "dieu_kien",
   "predicate": "work_days_in_year(W, D)", "kind": "input"}
  ```
  (tên vị từ minh hoạ)
- `data/processed/b1_predicates.jsonl`, mỗi vị từ một dòng:
  ```json
  {"predicate": "work_permit_exempt(W)", "kind": "concept",
   "anchors": ["BLLD_45-2019.D154", "ND_152-2020.D7", "ND_219-2025.D7"],
   "aliases": ["không thuộc diện cấp giấy phép lao động"], "used_in": ["BLLD_45-2019.D151.K1.d"]}
  ```
  (minh hoạ)
- Fact từ bảng (minh hoạ): `min_wage_month(vung_1, 5310000)` gắn phiên bản ND_293, hiệu lực 01/01/2026–31/12/2026.

**Kiểm (không có người duyệt):**
- **C1:** đơn vị có từ báo hiệu điều kiện thì có ít nhất một dòng trong bảng cụm.
- **C2:** mỗi vị từ `input` được ít nhất một quy tắc dùng.
- **C3:** không vị từ `input` nào trùng tên hay bí danh với một `concept`.
- **C4:** một lượt LLM độc lập (model khác) làm lại bước 1–4; chỗ hai lượt lệch nhau thì gắn cờ.
- Không có gì đảm bảo lấy hết vị từ. C1 chỉ bắt đơn vị bị bỏ sót hẳn; cụm sót bên trong một đơn vị chỉ C4 có thể bắt.

**Hỏng thì thấy gì:** một khái niệm có hai tên nên quy tắc không nối với nhau; khái niệm bị xếp nhầm thành `input` nên điều định nghĩa nó không bao giờ được dùng.

---

## L8. Ngoại lệ ngầm

**Làm gì:** tìm cặp đơn vị có quan hệ ngoại lệ mà chữ không ghi "trừ trường hợp".

**Đầu vào:** sổ khái niệm (L7), đơn vị, cạnh ngoại lệ tường minh (L5).

**Việc cụ thể:**
1. **Dựng đồ thị khái niệm.** Hai loại cạnh: `uses` (đơn vị → vị từ nó dùng) và `anchored_to` (vị từ `concept` → đơn vị định nghĩa nó).
2. **Tính tập vị từ được phép** của mỗi điều: vị từ của chính điều cộng vị từ của các điều láng giềng qua nút khái niệm. L9 chỉ được dùng các vị từ này.
3. **Sinh cặp ứng viên:** hai đơn vị cùng dùng một nút `concept`, bỏ các cặp đã có cạnh ngoại lệ tường minh.
4. **Đếm số cặp trước khi gọi LLM.** Khái niệm chung như "người lao động" có ở gần như mọi điều, nên số cặp có thể vượt hạn mức. Vượt thì chỉ giữ cặp có kết luận ngược dấu, hoặc cặp mà một bên dùng kết luận của bên kia làm điều kiện.
5. **LLM xét từng cặp** và trả một trong ba: rebut (A kết luận ngược B), undercut (A làm B không áp dụng nhưng không tự kết luận), hoặc không có quan hệ. Kèm câu bằng chứng nguyên văn.
6. **Bộ quét kiểm:** hai đầu tồn tại, không trùng cạnh tường minh, không tạo vòng.

**Đầu ra:**
- `data/processed/b3_concept_edges.jsonl`, `data/processed/b3_allowed_predicates.jsonl`;
- `data/processed/c1_candidates.jsonl` (các cặp);
- `data/processed/c1_implicit_exceptions.jsonl`:
  ```json
  {"s": "<đơn vị A>", "p": "exception_of", "o": "<đơn vị B>", "type": "rebut", "evidence": "<câu nguyên văn>", "flags": ["llm_proposed"]}
  ```

**Kiểm:** báo số cặp ứng viên, số cạnh được đề xuất theo loại, số cạnh bị bộ quét loại.

**Hỏng thì thấy gì:** thiếu cạnh thì câu hỏi ra "kết luận được" thay vì "bị bác"; thừa cạnh thì quy tắc đúng bị chặn oan.

---

## L9. Trích quy tắc, quét lỗi, tự sửa, cô lập

**Làm gì:** dịch mỗi đơn vị `substantive`/`definition` thành quy tắc s(CASP), mỗi quy tắc gắn với đúng một phiên bản đơn vị.

**Đầu vào:** chữ đơn vị (theo từng phiên bản), tập vị từ được phép (L8), cạnh ngoại lệ tường minh (L5) và ngầm (L8).

**Việc cụ thể:**
1. **LLM viết quy tắc** cho từng phiên bản đơn vị, chỉ bằng vị từ trong tập được phép. Cần vị từ ngoài tập thì gắn cờ, không tự đặt tên.
2. **Gắn quan hệ chặn** từ cạnh ngoại lệ: quy tắc của đơn vị ngoại lệ chặn quy tắc của đơn vị gốc.
3. **Gắn thứ tự ưu tiên** cho cặp kết luận ngược nhau mà không có cạnh ngoại lệ, theo Luật 64/2025 Điều 58:
   1. văn bản có hiệu lực pháp lý cao hơn thắng;
   2. cùng một cơ quan thì văn bản có ngày **ban hành** sau thắng;
   3. quy tắc áp dụng riêng trong cấu hình (NQ 66.16 Điều 19 khoản 3, NQ 66.18 Điều 7 khoản 3, Luật 71/2025 Điều 50 khoản 3);
   4. còn lại thì cô lập.
4. **Chạy bộ quét 7 loại lỗi:**
   1. quy tắc không bao giờ kích hoạt được (vị từ thân không phải `input` và không là đầu của quy tắc nào);
   2. quy tắc trùng;
   3. quan hệ đứt sau cập nhật;
   4. vòng chặn (vòng lẻ làm s(CASP) không trả lời được câu nào);
   5. cặp kết luận ngược nhau không có quan hệ chặn hay ưu tiên;
   6. quy tắc dựa trên đơn vị đã hết hiệu lực ở mọi thời điểm;
   7. quy tắc dựa trên đơn vị `pending_event` mà không có điều kiện thời gian.
5. **Tự sửa:** đưa thông báo lỗi, chữ luật và vị từ liên quan lại cho LLM, tối đa 2 vòng. Bản sửa được nhận khi biên dịch được, không sinh lỗi mới và không làm hỏng mốc kiểm. Không đạt thì quy tắc bị cô lập.

**Đầu ra:**
- `data/processed/d1_rules.jsonl`:
  ```json
  {"rule_id": "R_ND152_D7_K8_v1", "source_unit": "ND_152-2020.D7.K8", "source_version": 1,
   "valid": ["2021-02-15", "2025-08-07"],
   "code": "work_permit_exempt(W) :- expert(W), work_days_in_year(W, D), D < 30, trips_in_year(W, N), N =< 3."}
  {"rule_id": "R_ND219_D7_K13a_v1", "source_unit": "ND_219-2025.D7.K13.a", "source_version": 1,
   "valid": ["2025-08-07", null],
   "code": "work_permit_exempt(W) :- expert(W), work_days_in_year(W, D), D < 90."}
  {"rule_id": "R_BLLD_D151_K1d_v1", "source_unit": "BLLD_45-2019.D151.K1.d", "source_version": 1,
   "valid": ["2021-01-01", null],
   "code": "needs_work_permit(W) :- foreign_worker(W), not work_permit_exempt(W)."}
  ```
  (vị từ và mã quy tắc minh hoạ)
- `docs/d2_scan_report.txt`, `data/processed/d3_repair_log.jsonl`, `data/processed/d3_isolated.jsonl`.

**Kiểm:** bộ quét sạch hoặc mọi lỗi còn lại đã bị cô lập; có test âm cho từng loại lỗi.

**Hỏng thì thấy gì:** quy tắc của ND_28 vẫn được dùng sau 17/01/2022; hai quy tắc cho kết luận ngược nhau mà không bên nào thắng.

---

## L10. Hỏi đáp theo ngày

**Làm gì:** nhận câu hỏi, chọn đúng phiên bản luật theo ngày, chạy suy luận, trả lời kèm căn cứ.

**Đầu vào:** câu hỏi bằng tiếng Việt, ngày sự việc nếu có, và KB.

**Việc cụ thể:**
1. **Chọn ngày.** Có ngày sự việc thì dùng ngày đó. Không có thì dùng ngày hỏi, không lấy văn bản ban hành mới nhất. Ví dụ ND_399 ký 02/11/2026, hiệu lực 01/01/2027, nên câu hỏi ngày 05/11/2026 không dùng ND_399.
2. **Biên dịch chương trình theo ngày đó.** Chỉ lấy quy tắc có khoảng `valid` chứa ngày đó. Bỏ đơn vị `not_yet`, `pending_event` chưa kích hoạt, và mọi thứ bị cô lập. `overrides` chỉ có tác dụng trong khoảng của nó.
3. **Dịch câu hỏi thành dữ kiện.** LLM chuyển câu hỏi thành các vị từ `input` của sổ. Không biểu diễn được bằng vị từ có sẵn thì trả "ngoài phạm vi".
4. **Chạy s(CASP) hai lần**, một lần với mệnh đề P và một lần với ¬P:
   - chứng minh được P → **kết luận được**;
   - chứng minh được ¬P → **bị bác**;
   - không chứng minh được bên nào → **chưa đủ căn cứ**;
   - cần tới phần bị cô lập → **hệ thống không trả lời**, kèm danh sách mục bị cô lập.
5. **Viết giải thích** bằng cách điền mẫu câu từ cây chứng minh: văn bản, đơn vị, phiên bản, ngày hiệu lực.
6. **Báo bản mới hơn.** Nếu một phiên bản trong chuỗi căn cứ đã có bản kế tiếp tại ngày hỏi, thêm dòng "Quy định này đã được sửa đổi/thay thế bởi … từ ngày …". Dòng này lấy từ chuỗi phiên bản, không qua LLM, và không đổi kết luận.

**Đầu ra:** `data/processed/e_answers.jsonl` (minh hoạ):
```json
{"question": "Chuyên gia nước ngoài làm việc 45 ngày trong năm, một chuyến, có phải xin giấy phép lao động không?",
 "fact_date": "2025-06-01",
 "facts": ["foreign_worker(w1)", "expert(w1)", "work_days_in_year(w1, 45)", "trips_in_year(w1, 1)"],
 "status": "kết luận được", "answer": "Phải có giấy phép lao động.",
 "basis": [{"unit": "BLLD_45-2019.D151.K1.d", "version": 1},
           {"unit": "ND_152-2020.D7.K8", "version": 1, "valid": ["2021-02-15", "2025-08-07"]}],
 "newer_version_note": "ND_152 Điều 7 khoản 8 đã hết hiệu lực từ 07/8/2025; xem ND_219 Điều 7 khoản 13."}
```
Cùng câu hỏi với `fact_date` 2025-10-01 thì quy tắc ND_219 được dùng (45 < 90), kết quả "bị bác": không phải xin giấy phép.

Ví dụ thứ hai: lương 5.500.000 đồng/tháng ở vùng I. Hỏi ngày 05/11/2026 thì mức tối thiểu 5.310.000 (ND_293), nên không thấp hơn. Hỏi ngày 15/01/2027 thì mức 5.700.000 (ND_399), nên thấp hơn.

**Kiểm:** hai câu demo trên ra đúng ở cả hai ngày.

**Hỏng thì thấy gì:** câu hỏi năm 2025 trả theo luật năm 2026; giải thích dẫn một điều không có trong cây chứng minh.

---

## L11. Cập nhật tăng dần

**Làm gì:** chạy cả chuỗi văn bản theo thứ tự ngày hiệu lực. Mỗi lần nạp chỉ làm lại phần bị ảnh hưởng, không dựng lại toàn bộ.

**Đầu vào:** thư mục văn bản sự kiện và ngày dừng.

**Việc cụ thể:**
1. Sắp văn bản theo ngày hiệu lực.
2. Với mỗi văn bản:
   1. chạy L1–L5 trên văn bản mới;
   2. L6 áp chỉ thị, kể cả nối quan hệ chờ đích và kiểm kích hoạt;
   3. tính **tập ảnh hưởng**: đơn vị bị chạm, cộng đơn vị nối với chúng qua `details`, `refers_to`, `exception_of` và đồ thị khái niệm;
   4. chạy lại L7–L9 chỉ trên tập ảnh hưởng;
   5. quét lỗi, biên dịch lại, ghi log sự kiện.
3. Chế độ `--rebuild`: dựng lại toàn bộ từ đầu đến cùng ngày, để đối chiếu với cách chạy tăng dần.

**Ví dụ:** nạp ND_219 thì tập ảnh hưởng gồm:
- các đơn vị lao động nước ngoài của ND_152 (bị đóng);
- các đơn vị mới của ND_219;
- BLLĐ Điều 154 khoản 9 (nối qua `details`);
- BLLĐ Điều 151 khoản 1 điểm d (nối qua ngoại lệ);
- các quy tắc dùng vị từ "miễn giấy phép lao động" **(minh hoạ)**.

Phần lương tối thiểu và xử phạt không bị chạm nên giữ nguyên.

**Đầu ra:** `events/<doc_id>.json` cho từng văn bản: số đơn vị bị chạm, mở, đóng; số quy tắc trích lại và giữ nguyên; cờ; mục bị cô lập; số lượt LLM; thời gian chạy. Log này đủ để sau này tính chi phí cập nhật mà không phải chạy lại.

**Kiểm:** chạy tăng dần và `--rebuild` đến 10/9/2026 (văn bản dev cuối) phải ra cùng tập quy tắc có hiệu lực tại ngày đó. Khác biệt nào cũng phải giải thích được.

**Hỏng thì thấy gì:** đầu chuỗi khớp nhưng cuối chuỗi lệch `--rebuild`, tức tập ảnh hưởng đã bỏ sót đơn vị liên quan.

---

## Bảng tóm tắt

| Bước | Ra cái gì |
|---|---|
| L0 | cấu hình lĩnh vực, wrapper LLM có cache, `run_all.py` |
| L1 | đơn vị có mã + thông tin văn bản + bảng đã ghép |
| L2 | cạnh `refers_to` + danh sách quan hệ chờ đích |
| L3 | danh sách điều khoản giao chi tiết (5 dạng) + cạnh `based_on`, `details` |
| L4 | nhãn cho từng Điều |
| L5 | cạnh `exception_of` tường minh |
| L6 | phiên bản và trạng thái của từng đơn vị theo thời gian + log sự kiện |
| L7 | bảng cụm, sổ vị từ, fact từ bảng |
| L8 | đồ thị khái niệm, tập vị từ được phép, cạnh ngoại lệ ngầm |
| L9 | quy tắc s(CASP) gắn phiên bản, báo cáo quét, danh sách cô lập |
| L10 | câu trả lời theo ngày, ba trạng thái hoặc từ chối, chuỗi căn cứ |
| L11 | KB tại ngày bất kỳ, chạy tăng dần, log để đo chi phí |

Điều gì sẽ chứng minh tài liệu này sai: một bản ghi mẫu ở đây có trường hoặc giá trị không khớp với plan bản 8/11 hay với chữ văn bản trong kho. Khi đó một trong hai tài liệu phải sửa.
