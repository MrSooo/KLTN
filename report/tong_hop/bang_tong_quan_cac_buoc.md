# Bảng các bước từ A đến thực nghiệm: làm gì, vào, ra, cách kiểm

Lập ngày 04/11/2026. Phần A lấy từ `report/ky_thuat/chi_tiet_code_a1_a7.md` (số liệu trên đĩa ngày 04/11, test chạy ngày 03/11). Phần B trở đi lấy từ `plan/ke_hoach/ke_hoach_tang_toc_v1.md`: **là kế hoạch, chưa có code**, tên file là đề xuất.

**Ký hiệu cột N/S:** **N** dùng LLM. **S** dùng luật, ký hiệu hoặc bộ giải, kết quả lặp lại được. **N-S** LLM chỉ đề xuất, máy kiểm bằng luật. **—** việc của người.

**Dữ liệu thử:** Bộ luật Dân sự 2015, Phần 4 (Thừa kế), Điều 609-662: 54 Điều, 115 Khoản, 46 Điểm (215 đơn vị), 4 Chương.

---

## 1. Phần A: đồ thị tri thức (đã xong)

Nguyên tắc chung: mỗi bước đọc file của bước trước; A1-A7 dùng mẫu câu (regex), không dùng LLM; gặp dạng câu chưa có quy tắc thì **dừng và báo lỗi**, không đoán; mỗi cạnh có câu `evidence` nguyên văn.

| Bước | N/S | Làm gì | Vào | Ra | Tự kiểm · kết quả |
|---|---|---|---|---|---|
| **A1** | S | Tách luật thành đơn vị rồi ghi bộ ba (đơn vị, thuộc tính, giá trị).<br>(1) Nhận từng dòng là Chương / Điều / Khoản / Điểm / đoạn chữ bằng 4 regex.<br>(2) Máy trạng thái dựng cây Chương > Điều > Khoản > Điểm và kiểm thứ tự: Điều 609→662 liền nhau, Khoản 1, 2, 3 liền nhau, Điểm theo bảng chữ của luật (có `đ`).<br>(3) Gán mã ổn định, ví dụ `BLDS2015.D621.K1.a` (Điểm `đ` ghi thành `dd`).<br>Dòng không nhận ra thì dừng, không bỏ qua âm thầm. | `data/raw/blds2015_p4.md` | `a1_triples`: 1.173 bộ ba (loại, số, tiêu đề, chữ, phiên bản 1, dòng nguồn); `a1_notes` (chỗ cần người xem) | 11 test. Đếm độc lập bằng grep: 215 đơn vị, 1.173 bộ ba. Bảo toàn từ: tập từ file gốc bằng tập từ các đơn vị |
| **A2** | S | Hai việc:<br>(a) **Cấu trúc**: nối cha-con (Chương chứa Điều, Điều chứa Khoản, Khoản chứa Điểm), mỗi cặp ra hai cạnh `contains` và `part_of`.<br>(b) **Dẫn chiếu**: tìm cụm như "khoản 1 và khoản 3 Điều 616 của Bộ luật này", đổi thành mã đích (mục cấp cao nhất đứng cuối dùng chung cho các mục trước; "Điều này / khoản này" là tổ tiên đúng loại), nối `refers_to` kèm `evidence`. Đích ngoài Phần 4 (Điều 71, Điều 236) không tạo cạnh, ghi `unresolved`. Dạng cụm chưa có quy tắc thì dừng báo lỗi | A1 | `a2_edges`: 430 cạnh (215 `contains` + 215 `part_of`); `a2_refs`: 25 `refers_to` (7 trong cùng Điều, 18 sang Điều khác); `unresolved`: 2 dòng | 43 test. Đếm lại độc lập số `refers_to`. Mỗi Khoản/Điểm đúng một cha, cha đúng bậc; `evidence` nằm trong chữ nguồn |
| **A3** | S | Chỉ **hai mẫu câu**, tạo cạnh `exception_of` (nguồn là phần ngoại lệ, đích là quy tắc bị ngoại trừ):<br>(1) đơn vị có "không áp dụng" và ngay trước đó là cụm dẫn chiếu → đơn vị đó là ngoại lệ của từng đích (`D644.K2 → D644.K1`);<br>(2) text có "trừ" và kết thúc bằng "sau đây:" → mỗi đơn vị con là ngoại lệ của đơn vị cha (`D632.K1, K2, K3 → D632`).<br>Không nới quy tắc để bắt thêm: câu ngoài hai mẫu vào `unhandled` | A1, cạnh `contains` của A2 | `a3_exceptions`: 4 cạnh; `unhandled`: 9 dòng (do A6 nhận) | 19 test. Mỗi cụm "trừ / ngoại trừ / không áp dụng" phải rơi vào đúng một trong "đã xử lý" hoặc `unhandled`, đếm khớp nên không cụm nào mất |
| **A4** | S; N-S khi bật LLM | Cập nhật khi có văn bản sửa đổi, **không xoá nút nào**: đơn vị bị sửa nhận phiên bản mới, bản cũ ghi ngày hết hiệu lực `[từ, đến)`.<br>**Áp trên:** luật gốc cộng văn bản sửa đổi (Markdown) có đúng một ngày hiệu lực sau 01/01/2017 và các dòng chỉ thị theo **6 mẫu**:<br>R1 sửa đổi / thay thế khoản, điểm, Điều · R2 bổ sung Điều, khoản, điểm mới ("vào sau …") · R3 bãi bỏ · R4 sửa tên Điều · R5 thay / bỏ / bổ sung **cụm từ** · R6 thay thế cả văn bản.<br>Sau khi áp: tính lại `refers_to` / `exception_of` chỉ cho đơn vị đổi chữ; cờ **cạnh đứt** (nguồn còn hiệu lực, đích vừa bị đóng); lập **tập đơn vị bị ảnh hưởng** (đơn vị khác dẫn chiếu tới hoặc có quan hệ ngoại lệ với đơn vị đã đổi).<br>Dòng không khớp 6 mẫu là **lỗi dừng**, không ghi file.<br>**Tầng LLM (tuỳ chọn):** dòng lạ được gửi cho LLM đề xuất; máy dựng lại thành câu chuẩn, parse bằng chính văn phạm trên, rồi kiểm V1-V3 (phủ đủ số hiệu, nội dung nguyên văn, cụm từ nguyên văn); hỏng thì gửi lỗi cho LLM sửa, tối đa 3 lần | luật gốc; cạnh A2/A3; văn bản sửa đổi: 8 văn bản dev tự soạn, và 19 câu thật của Luật 85/2025/QH15 làm bộ kiểm thử ngoài | Mỗi văn bản một thư mục: `versions`, `amend_edges`, `edge_changes`, `changed`, `impact` cộng báo cáo; lệnh `snapshot` xuất luật tại một ngày | 63 test, hơn 25 mã lỗi `E_*`. Ví dụ dev02: 215 đơn vị + 2 phiên bản mới, ảnh hưởng `D621.K2`, `D644.K2`.<br>Bộ ngoài 19 câu: tắt LLM → 9 qua, 10 dừng báo lỗi, 0 áp sai. **Gemini 3.6 Flash chạy thật 04/11 → 14 qua (9 ký hiệu + 5 LLM), 0 sai, 5 còn dừng báo lỗi**: 4 do chữ giả định trong dữ liệu ca có cụm "khoản N" mà A2 từ chối, 1 do quy tắc chồng lấn E7 (rename_heading Điều với khoản con) |
| **A5** | S | **Quét xem dữ liệu A1-A3 (và phiên bản A4) có trùng hoặc hở chỗ nào không**, không sinh dữ liệu mới. Đọc thẳng JSON, không dùng hàm của A2 để phép kiểm độc lập. Bốn nhóm:<br>(1) mã đơn vị: số đơn vị / Điều / Chương đúng bảng kỳ vọng, mỗi đơn vị một `type`, không có `(s,p)` lặp;<br>(2) cấu trúc: mỗi Khoản / Điểm đúng một cha, cha đúng bậc, `contains` đối xứng `part_of`;<br>(3) cạnh: không bộ ba lặp trong A2 + A3;<br>(4) phiên bản: số phiên bản liên tiếp, khoảng hiệu lực không chồng, mọi mã A1 còn trong `versions` (không xoá nút), phiên bản 1 giữ nguyên nội dung A1 | A1, A2, A3 (+ `versions` của A4) | `a5_report`, ghi cả khi đạt | 54 test, chủ yếu bơm lỗi vào dữ liệu dựng tay để xem kiểm nào bắt. Kết quả p4: ĐẠT mọi kiểm, 459 bộ ba, 0 lặp |
| **A6** | S | Câu "…, trừ trường hợp X" mà X là một **điều kiện**, không phải Điều / Khoản cụ thể (ví dụ "có thỏa thuận khác"):<br>tạo **nút điều kiện** (mã băm của mệnh đề, mệnh đề giống nhau thì cùng một nút) và nối `exception_of` vào đơn vị chứa câu.<br>Phân loại nút: `tuy_nghi` ("thỏa thuận khác"), `dan_chieu_mo` ("pháp luật có quy định khác"), `cu_the`. Nếu X nhắc một Điều khác (Điều 619 → Điều 652) thì thêm cạnh từ Điều đó vào đơn vị.<br>Hai "trừ trường hợp" trong một đơn vị thì dừng báo lỗi | A1 | `a6_conditions`: 5 nút; `a6_exceptions`: 10 cạnh (9 theo mẫu câu + 1 theo dẫn chiếu); `unhandled`: rỗng | 23 test. 9 đơn vị khớp đúng 9 đơn vị A3 để lại. Nút "có thỏa thuận khác" nối 5 đơn vị |
| **A7** | S | Gộp A1, A2, A3, A6 thành **một đồ thị**: 225 nút (54 Điều + 115 Khoản + 46 Điểm + 4 Chương + 5 nút điều kiện + 1 nút văn bản); cạnh trùng gộp một và ghi nguồn; đơn vị có chữ giống hệt đơn vị đứng trước đánh `same_text` (không gộp nút, vì mỗi đơn vị là một vị trí pháp lý riêng).<br>**Dựng tại một ngày T** từ kết quả A4: chỉ giữ đơn vị đang hiệu lực, bỏ cạnh có nguồn đã đóng, giữ cạnh có nguồn còn mà đích đã đóng và đánh `dangling` (cạnh treo).<br>Kiểm 7a-7g: mã nút duy nhất, cạnh đủ hai đầu, không lặp, mỗi đơn vị đúng một cha, số nút / cạnh khớp bảng kỳ vọng, **không có vòng `exception_of`**. Chỉ ghi file khi mọi kiểm đạt | A1, A2, A3, A6 (+ A4 với `--versions --date`) | `a7_nodes`: 225; `a7_edges`: 481 (contains 219, part_of 219, refers_to 25, exception_of 14, same_text_as 4); báo cáo | 32 test. Ví dụ tại 01/01/2027 sau dev05: 211 nút, 454 cạnh, 1 cạnh treo (Điều 653 dẫn chiếu Điều 651 đã bị bãi bỏ) |
| **A8** | S | Vẽ đồ thị A7 thành trang HTML mở offline: nút tròn, cạnh thẳng, kéo thả, tìm kiếm, bật / tắt từng loại cạnh, có bản tại một ngày. Không tạo tri thức mới. Tùy chọn, không thuộc báo cáo A1-A7 | A7 | một file HTML (~0,5 MB) | 15 test phần Python; phần JavaScript thử tay |

---

## 2. Mở khoá (tuần 0, 03/11 - 08/11)

| Việc | N/S | Làm gì | Vào | Ra | Ai · khi nào |
|---|---|---|---|---|---|
| 0.x | — | Hoàn thiện đề cương; hỏi thầy các câu còn mở; nhắn người hỗ trợ có nhận làm bộ dữ liệu không | — | câu trả lời; tên và thời gian của người hỗ trợ | Bạn · đến 05/11 |
| 1.1 | — | Chạy `run_all.py` ra XONG (A1→A7, A4 cho từng văn bản dev, A5 với `--versions`, A7 với `--date`) rồi gộp nhánh làm việc vào `main` | repo | `main` khớp báo cáo | Agent · 04/11 |
| 1.2 | S | Đếm cạnh **xuyên Điều** trong đồ thị A7: `refers_to` và `exception_of` nối hai Điều khác nhau | A7 | con số sàn N, để biết quy mô bộ dữ liệu phụ thuộc | Agent · 04/11 |
| 1.3 | — | Tự ôn A1→A7, mỗi bước ba câu: vào là gì, ra là gì (ý nghĩa một dòng), sai thì thấy ở đâu | — | `docs/ON_TAP.md` | Bạn |
| LLM nền | N-S | (a) `llm_config.md`: model ID, mức thinking, temperature, ngày khoá.<br>(b) Wrapper `llm_client.py` dùng chung cho B-E: đọc config, lưu phản hồi thô vào `data/llm_cache/` (chạy lại không gọi lại model), đếm lượt theo hạn mức ngày, kiểm nguyên văn.<br>Model dự kiến: Gemini 3.8 Flash cho B1, C1, D1 lô đầu; Gemini 3.5 Flash-Lite cho C4 và chạy thử code. Đã gọi thử Gemini thật thành công ở A4 (04/11) | quyết định K3, K4 | `llm_config.md`; `src/llm_client.py` | Bạn viết config, Agent viết wrapper · 04/11 |

---

## 3. Phần B-E: dựng hệ thống (kế hoạch, chưa có code)

### B. Sổ khái niệm

| Bước | N/S | Làm gì | Vào | Ra | Kiểm · cổng | Ai · khi nào |
|---|---|---|---|---|---|---|
| **B1** | N-S | LLM đọc từng lô (~12 Điều) cùng sổ hiện có, nháp **bảng R3** (mỗi dòng một cụm chủ thể / điều kiện / ngoại lệ / kết luận, chép nguyên văn từ đơn vị luật) và **sổ vị từ**, theo 4 quy tắc:<br>**R1** phân loại: vị từ là `concept` nếu có Điều nêu khi nào nó đúng (neo vào Điều đó), còn lại `input`.<br>**R2** `input` phải là dữ kiện thô. Thử: người hỏi nêu thẳng vị từ này thì có bỏ qua được Điều nào không? Có → phải là `concept`.<br>**R3** gạch mọi cụm điều kiện (sau "nếu", "khi", "trường hợp", "trừ", "người… mà…"), mỗi cụm một vị từ.<br>**R4** một khái niệm một tên: tra sổ theo cụm tiếng Việt, tên tiếng Anh, chữ ký (số tham số và vai). Cùng nghĩa → dùng lại tên cũ và thêm bí danh; gần nghĩa → vị từ mới, ghi "KHÔNG gộp".<br>Script tự kiểm: cụm là chuỗi con nguyên văn; tên theo quy ước (không `not_`, `no_`, `_or_`, `_and_`, `all_`, `any_`, không số điều); tham số chỉ X, Y, T, W. Vi phạm thì gắn cờ, không tự sửa.<br>*Ví dụ (minh hoạ):* Điều 619, cụm "họ không được thừa kế di sản của nhau" → `barred_from_inheriting(X,Y)`, `concept`, neo Điều 619 | `a1_triples`; hướng dẫn R1-R4; bảng 19 khái niệm; sổ hiện có | `b1_r3_rows` (id, unit_id, span, role, predicate, args, type, anchor, note, flags); `b1_predicates` (predicate, roles, type, anchor, aliases, used_in, note) | **Cổng G-B** trên lô đầu 5 Điều (621, 626, 644, 650, 651): số dòng phải đổi loại ≤ 10% và không cụm nào sai nguyên văn. Người duyệt: hỏi câu R2 cho mọi dòng `input`; neo phải trỏ vào Điều **nêu điều kiện**, không phải Điều **dùng**. Lô 5 đọc hết; 49 Điều còn lại đọc mục bị cờ và 3 Điều ngẫu nhiên | Agent nháp, bạn duyệt · lô 5: 04/11, G-B 05/11, 49 Điều 06/11 |
| **B2** | N-S | Kiểm sổ:<br>**C1** mỗi đơn vị có điều kiện đều có ít nhất một dòng R3;<br>**C2** mỗi vị từ `input` được dùng ít nhất một lần;<br>**C3** không `input` nào trùng tên hoặc bí danh với `concept`;<br>(C1-C3 do script, S)<br>**C4** một lượt LLM **độc lập** (3.5 Flash-Lite, không thấy bảng, khác model của B1) tự trích cụm điều kiện, so với bảng và liệt kê cụm lệch (N) | `b1_*`, A1 | `b2_checks.py`; `test_b2.py` (test âm cho từng kiểm); báo cáo B2 | Cổng: C1-C3 không vi phạm; mỗi mục lệch của C4 có quyết định "thêm dòng" hoặc "bỏ, vì …" | Agent · 07/11; bạn quyết mục lệch C4 |
| **B3** | S | Dựng **đồ thị khái niệm**: cạnh `uses` (đơn vị → vị từ) và `anchored_to` (vị từ → đơn vị định nghĩa). Từ đó tính **tập vị từ được phép** cho mỗi Điều = vị từ của chính Điều đó + vị từ của các Điều láng giềng qua nút khái niệm | `b1_predicates`, `b1_r3_rows` | `b3_concept_edges`; `b3_allowed_predicates` | Bạn vẽ đồ thị con quanh 621 / 626 và xem tập được phép của 3 Điều bất kỳ. Tập quá hẹp → D gắn cờ "thiếu vị từ" nhiều; quá rộng → cách (ii) giống (iii), Tầng 1 không tách được tác dụng của đồ thị khái niệm | Agent · 08/11 |
| **B4** | — | **Đóng băng sổ**. Sau đó mọi thay đổi ghi `so_changelog.md` (ngày, vị từ, lý do, phát hiện từ dev hay từ D). Không đổi sổ vì bất cứ điều gì nhìn thấy trong tập kiểm tra | sổ | tag `so-v1-2026-11-15`; changelog | Chưa có tag thì chưa viết tập kiểm tra | Bạn · CN 15/11 |

### C. Ngoại lệ ngầm

| Bước | N/S | Làm gì | Vào | Ra | Kiểm · cổng | Ai · khi nào |
|---|---|---|---|---|---|---|
| **C1** | N-S | Tìm quan hệ ngoại lệ **không có từ nối** (ví dụ khoản 1 Điều 621 chặn Điều 626).<br>(1) Sinh cặp ứng viên từ đồ thị khái niệm: hai đơn vị cùng dùng hoặc cùng neo một nút khái niệm (S).<br>(2) LLM đề xuất cạnh `exception_of` và loại: *phản bác* (kết luận ngược lại) hay *vô hiệu hoá* (chỉ làm quy tắc gốc không áp dụng), kèm câu bằng chứng nguyên văn (N).<br>(3) Bộ quét kiểm: hai đầu tồn tại, không trùng cạnh tường minh của A3 / A6, không tạo vòng (S) | `b3_*`; A3, A6; chữ đơn vị | `c1_candidates`; `c1_implicit_exceptions` (loại, bằng chứng, cờ) | Bạn chỉ xem mục bị cờ. **Mốc biết trước:** cạnh khoản 1 Điều 621 → Điều 626 phải có; không có thì xem lại cách sinh cặp trước. Thiếu cạnh → tình huống ngoại lệ xuyên Điều ra "kết luận được" thay vì "bị bác"; thừa cạnh → quy tắc đúng bị chặn oan | Agent · 09/11 |

### D. Quy tắc và bộ quét

| Bước | N/S | Làm gì | Vào | Ra | Kiểm · cổng | Ai · khi nào |
|---|---|---|---|---|---|---|
| **D1** | N-S | LLM đọc chữ từng Điều cùng **tập vị từ được phép** của Điều đó và cạnh ngoại lệ (tường minh và ngầm), trích **quy tắc** dạng đầu ← thân. Cần vị từ ngoài tập thì **gắn cờ, không tự đặt tên** (N, bị S ràng buộc) | chữ Điều; `b3_allowed_predicates`; cạnh ngoại lệ | `d1_rules` (rule_id, head, body, polarity, source_unit, blocks, exception_type); `d1_flags` | **Cổng G-D** trên lô 5 Điều chuỗi: biên dịch được trong s(CASP) và 4 ca mẫu (viết lại bằng vị từ `input`) ra đúng trạng thái. Trượt hai lần thì xem lại cách biểu diễn quan hệ chặn. Sau cổng M chạy lại lô 5 bằng model chính thức rồi 49 Điều | Agent · lô 5: 10/11, G-D 11/11, M 12/11 |
| **D2** | S | **Bộ quét 5 loại lỗi** trên tập quy tắc:<br>(1) quy tắc không bao giờ kích hoạt (vị từ thân không phải `input` và không là đầu của quy tắc nào);<br>(2) quy tắc trùng;<br>(3) quan hệ đứt sau cập nhật;<br>(4) **vòng chặn** (bắt buộc: vòng lẻ làm mọi câu hỏi "không có mô hình");<br>(5) cặp kết luận ngược nhau không có quan hệ chặn | `d1_rules`, sổ, cạnh chặn | `d2_scan.py`; báo cáo quét; test âm cho từng loại | Mỗi loại có test âm | Agent · 13/11 |
| **D3** | N-S | Tự sửa mục bị cờ tối đa **2 vòng** (N sửa). Nhận bản sửa khi: biên dịch được, không sinh cờ mới, số ca dev đúng không giảm (S). Không sửa được thì **cô lập**, câu hỏi phụ thuộc vào đó bị từ chối | các mục bị cờ ở D1, D2 | `d3_repair_log`; `d3_isolated` | Bạn đọc **mọi** mục cô lập (~3 giờ); mục nào do lỗi sổ thì sửa sổ trước 15/11 và ghi changelog | Agent · 14/11 |
| **D4** | N-S | **Cập nhật ở mức quy tắc**: sau khi nạp hai văn bản dev của A4 (`dev01`, `dev02`), chỉ trích lại quy tắc của đơn vị đổi chữ (N); kiểm lại quy tắc và cạnh liên quan (S) | phiên bản A4 | `d4_update_diff` (đơn vị đổi, quy tắc trích lại, số ca dev trước và sau) | Chỉ đơn vị đổi chữ được trích lại; phiên bản cũ còn; D2 chạy lại sạch | Agent · 16-20/11 |

### E. Suy luận và hỏi đáp

| Bước | N/S | Làm gì | Vào | Ra | Kiểm · cổng | Ai · khi nào |
|---|---|---|---|---|---|---|
| **E1** | S | Biên dịch quy tắc và quan hệ chặn sang **s(CASP)**. Mỗi câu hỏi chạy cả P và ¬P, ra ba trạng thái: **kết luận được / bị bác / chưa đủ căn cứ**. Quy ước: điều kiện của ngoại lệ mà tình huống không nêu thì coi như không có. Kèm bộ quét vòng chặn | `d1_rules` + quan hệ chặn | `e1_program.pl` | 10 câu dev chạy trọn đường, trạng thái đúng | Agent · 15/11 |
| **E2** | N-S | Chuyển câu hỏi tiếng Việt thành **dữ kiện** bằng vị từ `input` của sổ (N). Không biểu diễn được thì trả "ngoài phạm vi" (S) | câu hỏi; sổ | dữ kiện cho E1 | như E1 | Agent · bản đầu 15/11, xong 16-20/11 |
| **E3** | S | **Giải thích** bằng mẫu câu điền từ cây chứng minh. Không có bước LLM diễn đạt lại | cây chứng minh của E1 | câu giải thích | Điều luật trong giải thích phải có thật trong cây chứng minh | Agent · 16-20/11 |

---

## 4. Bộ dữ liệu đánh giá

Điều cần giữ: **nhãn đáp án chỉ do người gán**; LLM chỉ được nháp chữ. Tập kiểm tra viết **sau** đóng băng sổ và để **ngoài repo đến 23/11**.

| Bước | N/S | Làm gì | Vào | Ra | Ai · khi nào |
|---|---|---|---|---|---|
| **DS1** | N (nháp) | Liệt kê **phụ thuộc giữa các Điều**: Điều phụ thuộc, Điều được phụ thuộc, loại cạnh (dẫn chiếu / ngoại lệ tường minh / ngoại lệ ngầm / khái niệm), **độ sâu** tính trên văn bản (mở rộng sang nhiều Điều), ghi chú. LLM (chat mới, ngoài project, chỉ nhận chữ luật) đề xuất; bạn đối chiếu từng mục với chữ luật, giữ hoặc bỏ có lý do | chữ luật; số N từ 1.2 (chỉ để biết quy mô) | `ds_dependencies.csv`; `ds_prompts/` | Bạn · 08-13/11 |
| **DS2** | — | **Quy ước diễn giải** cho chỗ luật mơ hồ (ví dụ phạm vi "vẫn được hưởng" ở khoản 2 Điều 621) và gom mọi dòng "?" từ B1 | B1; câu hỏi chuyên môn luật | `ds_convention.md` | Bạn · 08/11 |
| **DS3** | N (nháp) | **Tập dev**: khoảng 20% số cặp, dùng tự do khi phát triển; soạn bằng model **khác** model chính thức | DS1 | tập dev | Bạn · 14-15/11 |
| **DS4** | N (nháp) | **Tập kiểm tra có kiểm soát**: mỗi phụ thuộc độ sâu ≥ 2 một **cặp tình huống** (độ sâu 1 lấy mẫu); hai tình huống chỉ khác đúng dữ kiện liên quan tới Điều được phụ thuộc; viết bằng vị từ `input` (Tầng 1) và bằng câu tiếng Việt (Tầng 3). LLM nháp chữ; **hai người gán nhãn độc lập** (trạng thái đáp án, độ sâu), đo Cohen's Kappa (ngưỡng tạm ≥ 0,6), bất đồng thì hợp nhất có ghi lý do | DS1, DS2; sổ đã đóng băng | tập kiểm tra có nhãn | Bạn viết, bạn và một người khác gán nhãn · 16-22/11 |
| **DS5** | — | **Bộ quan hệ chuẩn** cho Tầng 2 (đáp án quan hệ ngoại lệ). Khung chấm 11 Điều mẫu đã có; thiếu giờ thì giữ đúng 11 Điều | chữ luật | file đáp án | Người hỗ trợ · 07-15/11 |
| **DS6** | — | **Văn bản sửa đổi kín**: 8-10 văn bản giả định, mỗi văn bản kèm cặp tình huống đổi đáp án sau khi sửa. Người hỗ trợ soạn và giữ kín (người làm hệ thống không tự viết đề của mình); không vào repo trước 28/11 | — | bộ kín | Người hỗ trợ · 14-22/11 |
| **DS7a** *(mới 04/11, chờ chốt)* | — | Chốt **nguồn** và **tiêu chí chọn tình huống thật**, ghi vào file có ngày **trước khi xem kết quả hệ thống** (để không chọn theo kiểu "hệ thống làm được thì lấy"). Nguồn ứng viên (chưa kiểm tra khả năng sử dụng): bản án thừa kế đã công bố, hỏi đáp tư vấn pháp luật thừa kế công khai, tình huống trong giáo trình / sách bình luận | — | `ds_real_tieu_chi_<ngày>.md` | Bạn · 09/11 |
| **DS7b** *(mới, chờ chốt)* | — | **Thu thập và lọc**: loại ca ngoài Điều 609-662 (đất đai, hôn nhân gia đình, thủ tục tố tụng), ca thiếu dữ kiện, ca có thời điểm mở thừa kế trước 01/01/2017. Ghi nguồn gốc (liên kết, ngày) cho từng ca | DS7a | `ds_real_raw/` + bảng nguồn | Bạn + người hỗ trợ · 09-15/11 |
| **DS7c** *(mới, chờ chốt)* | — | **Chuẩn hoá và gán nhãn**: viết lại thành dữ kiện bằng vị từ `input` và câu hỏi tiếng Việt; nhãn ba trạng thái do **người** gán độc lập, đo Kappa. Phán quyết của toà chỉ làm tham chiếu, không tự động là nhãn | DS7b; sổ đã đóng băng | `ds_real_test.csv` có nhãn | Bạn + một người khác · 16-22/11 |

---

## 5. Thực nghiệm

Cột N/S ghi **phương pháp được đo**; đối chứng luôn là N thuần (LLM làm trực tiếp).

| Bước | N/S | Làm gì | Vào | Ra | Ai · khi nào |
|---|---|---|---|---|---|
| **X0** | — | Ghi **ngưỡng bác bỏ** Tầng 1 vào file có ngày và gắn tag code `v1.0` **trước khi chạy**. Luật sửa lỗi sau khi thấy tập kiểm tra: chỉ sửa lỗi làm chương trình chết, ghi log, chạy lại mọi phương pháp; không chỉnh prompt hay sổ | — | `x0_nguong_2026-11-22.md`; tag `v1.0` | Bạn · CN 22/11 |
| **X1** | N vs N-S | **Tầng 1**, ba cách trên cùng bộ vị từ `input` và cùng số vòng sửa: (i) LLM đọc toàn văn và tự viết s(CASP) [N]; (ii) hệ thống [N-S]; (iii) hệ thống + LLM nhận cả sổ khái niệm [N-S]. Đo **tỷ lệ phụ thuộc đạt** (cả hai tình huống trong cặp đúng) theo độ sâu ngoại lệ. Báo cáo riêng tập thực tế (DS7) nếu DS7 được chốt | tập kiểm tra | tỷ lệ phụ thuộc đạt theo độ sâu | Agent · 23/11 |
| **X2** | S, N-S | **Tầng 2**: precision, recall, F1 của quan hệ ngoại lệ so với DS5 (cạnh A3 / A6 là S, cạnh ngầm của C1 là N-S); tỷ lệ cờ đúng của bộ quét (không đo độ phủ) | DS5; đồ thị | P, R, F1; tỷ lệ cờ đúng | Agent · 24/11 |
| **X3** | N vs N-S | **Tầng 3**: toàn hệ thống so với LLM trả lời trực tiếp có cấp sẵn điều luật. Ba trạng thái; từ chối trả lời tính là sai; kiểm định McNemar | tập kiểm tra (câu tiếng Việt) | accuracy theo độ sâu; McNemar | Agent · 25/11 |
| **X4** | N vs N-S | **Cập nhật**: hệ thống so với (a) LLM mạnh tự sửa chương trình cũ của cách (ii), (b) LLM trả lời trực tiếp trên toàn văn đã sửa. Đo tỷ lệ cặp tình huống bị ảnh hưởng được trả lời đúng | DS6 | số liệu | Agent · 28/11 |
| **X5** | — | **Phân tích lỗi**: gán mỗi ca sai về một khối (sổ B, ngoại lệ ngầm C, quy tắc D, dữ kiện E, nhãn). Báo cả kết quả âm | X1-X4 | bảng lỗi | Bạn · 29/11 |
| **X6** | — | Gói kết quả: bảng số, hình, lệnh chạy lại từng con số, README. Gặp thầy trình số liệu | X1-X5 | gói kết quả | Agent + bạn · 30/11 - 06/12 |
| **7** | — | Viết luận văn, slide bảo vệ | — | bản thảo | Bạn · từ 07/12 |

---

## 6. Cổng dừng và thứ tự bắt buộc

| Cổng | Khi | Qua khi | Trượt thì |
|---|---|---|---|
| G-B | 05/11 | đổi loại ≤ 10%, không cụm nào sai nguyên văn | sửa R1-R2 hoặc prompt, chạy lại lô 5 |
| G-D | 11/11 | biên dịch được, 4 ca mẫu ra đúng trạng thái | sửa prompt; trượt hai lần thì xem lại cách biểu diễn chặn |
| M (chốt model chính thức) | 12/11 | model đã khoá; lô 5 chạy lại vẫn qua G-D | chỉnh prompt trên model chính thức |
| Đóng băng sổ | CN 15/11 | có tag và changelog | chưa viết tập kiểm tra |
| Kappa | CN 22/11 | κ ≥ 0,6 (ngưỡng tạm) | sửa quy ước DS2, gán lại phần bất đồng |
| Tag `v1.0` + X0 | CN 22/11 | có cả hai | không chạy X1 |

**Bốn thứ tự không được đảo:** (1) chốt model chính thức rồi mới chạy D1 cho 49 Điều; (2) đóng băng sổ rồi mới viết tập kiểm tra; (3) ghi ngưỡng và gắn tag `v1.0` rồi mới nạp tập kiểm tra vào repo; (4) văn bản sửa đổi kín không vào repo trước 28/11.

**Mốc cứng:** thực nghiệm xong CN 29/11; tuần 30/11 - 06/12 là đệm, phân tích lỗi và gói kết quả.

---

## 7. Giới hạn đã biết

- A1-A7 chỉ bắt quan hệ **viết tường minh**. Quan hệ ngầm (khoản 1 Điều 621 chặn Điều 626) chưa có, đó là việc của C1.
- Ngoại lệ hiện chưa phân biệt *phản bác* với *vô hiệu hoá* (C1 sẽ gán loại này).
- Chưa có precision / recall thật cho A1-A7 vì chưa có đáp án do người gán (DS5 sẽ cung cấp cho Tầng 2).
- BLDS 2015 phần Thừa kế chưa có văn bản sửa đổi thật: 8 văn bản dev là tự soạn, 19 câu thật mượn từ Luật 85/2025/QH15 chỉ dùng để thử mẫu câu.
- Tầng LLM của A4 mới chạy thật một lần (Gemini 3.6 Flash, 10 khối); chưa chạy bằng Claude (API chưa thanh toán được).
- Tập kiểm tra có kiểm soát (DS4) là tình huống dựng; kết quả chưa nói được về câu hỏi thật của người dùng. DS7 được thêm vào để bù, hiện chờ chốt (bổ sung hay thay, nguồn, số lượng, ai thu thập).
- Phần B-E chưa có code; các số liệu ngày tháng là kế hoạch, giả định ngày thường 2 giờ làm việc.
