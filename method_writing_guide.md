# Hướng dẫn tự viết Section 3–4 (Method)

Soạn ngày 16/11/2026 theo hiện trạng nhánh `v3_refactor`, khi 1.6A đang chạy dở. Giả định khi viết: mọi bước đã có mã và chỉ còn chờ chạy thí nghiệm. File này **không chứa câu văn tiếng Anh mẫu**, vì chính việc lấy câu mẫu của cookbook là lý do bản draft bị nhận xét là "AI". Mỗi đoạn chỉ ghi bốn thứ: đoạn đó làm việc gì, nói những ý nào (kèm chỗ lấy nguồn trong repo), khung công thức nếu có, và độ dài.

Ký hiệu đánh dấu chỗ chưa viết được:
- `[CHỜ QUYẾT]`: thiết kế chưa chốt. Giữ chỗ đúng số dòng, không tự viết thành sự thật.
- `[CHỜ CODE]`: đã có thiết kế nhưng chưa có mã, nên chi tiết có thể đổi.
- `[CẦN SỐ]`: con số chỉ có sau khi chạy.
- `[KIỂM]`: phải mở mã ra xem mã đang làm gì trước khi viết.
- `[CẦN TRÍCH DẪN]`: thiếu tài liệu tham khảo.

**Phạm vi bài, đặt một lần cho cả hướng dẫn:** bài gồm cả giai đoạn 1 (dựng K₀ từ BLLĐ) và giai đoạn 2 (cập nhật khi nạp văn bản dưới luật). Mục 4.2 và điều kiện (C2) thuộc giai đoạn 2. Nếu sau này quyết chỉ viết giai đoạn 1 thì bỏ hai phần đó; ví dụ xuyên suốt (mục 0b) vẫn dùng được, chỉ là đáp án khi KB chỉ có BLLĐ sẽ là "chưa đủ căn cứ".

**Bảng thuật ngữ tiếng Anh, mỗi đối tượng một tên (cookbook 3.3):**

| Tiếng Việt | Tên dùng trong bài | Không dùng xen kẽ |
|---|---|---|
| đơn vị (Điều, khoản, điểm) | unit | provision, clause (trừ khi nói đúng "khoản") |
| phiên bản | version | revision |
| câu chỉ thị | directive | amendment sentence |
| điều khoản giao | delegating provision | slot, delegation clause |
| cổng kiểm bằng máy | check | gate, validation, verification |
| cô lập | isolated | quarantined, rejected |
| mệnh đề | proposition | span, phrase |
| sổ vị từ | predicate registry | ontology, vocabulary |

---

## 0. Vì sao bản draft bị chê "giống AI"

Các mục dưới đây là bằng chứng lấy từ chính `DRAFT_PAPER_METHODS_LATEX.pdf`.

| # | Triệu chứng | Chỗ trong draft | Cách tránh |
|---|---|---|---|
| 1 | Đoạn nào cũng mở bằng cùng một kiểu câu lý do: "để làm X, KB phải Y" | 3.2: "To answer date-dependent questions, the knowledge base must…", "The text of a unit changes over time, while the knowledge base must…", "Besides versioned text, the knowledge base must…" (ba đoạn liên tiếp) | Chỉ viết câu "vì sao" khi lý do không hiển nhiên. Phần lớn đoạn mở thẳng bằng việc mà bước đó làm. |
| 2 | Đoạn nào cũng có tiêu đề in nghiêng đứng đầu | 3.2 có 5 tiêu đề (Documents and units / Versions and status / Knowledge base / Inference program / Affected set) trong chưa tới 2 trang | Mỗi section dùng tối đa một cụm tiêu đề in nghiêng. Chỗ khác thì chuyển đoạn bằng nội dung. |
| 3 | Chép nguyên câu mẫu của cookbook | "note that the knowledge layer runs only on A(d)" (cookbook 7.1); "We assume (A1)… Assumption (A2) fails when…" (cookbook 4.1); "In other words, Π_τ is…"; câu mở S3 "This section defines the objects on which the rest of the paper operates" (diễn lại cookbook mục 1) | Dùng cookbook làm **checklist để soát sau khi viết**, không dùng làm kho câu. Xem danh sách cấm ở mục 5. |
| 4 | Đưa chi tiết kỹ thuật của tài liệu thiết kế vào bài | mã `ND_152-2020.D7.K8`; "ties broken by t_iss and then by id"; "until the end of day x gets t_to = x+1"; cặp văn bản cùng `ten_ngan` bị gắn cờ | Hỏi: người đọc có cần chi tiết này để hiểu phương pháp không? Không cần thì bỏ, hoặc chuyển xuống chú thích hay Implementation. |
| 5 | Tên văn bản dài lặp đi lặp lại | "Clause 8 of Article 7 of Decree No. 152/2020/NĐ-CP" xuất hiện khoảng 5 lần | Định nghĩa viết tắt một lần trong Example 1 (ND152, ND219, LC), từ đó chỉ dùng viết tắt. |
| 6 | Câu song ngữ chen vào giữa thân bài | ba lần dạng "Sửa đổi, bổ sung … như sau" ("amend and supplement … as follows") | Cả section chỉ giữ một câu song ngữ, đặt ở chỗ mà dạng chữ tiếng Việt quyết định thuật toán (câu chỉ thị). Các câu khác chỉ dịch nghĩa. |
| 7 | Mọi câu nặng như nhau, mọi đoạn dài như nhau, không có chỗ nhấn | đoạn Problem 13 dòng nhồi C1, C2, "không người duyệt" và việc chọn kho văn bản | Để độ dài đoạn lệch nhau: phần mới (phiên bản và Π_τ, cổng kiểm, quy tắc chặn) được nhiều dòng, phần quen thuộc (parse) chỉ 2–3 câu. |
| 8 | Định nghĩa ký hiệu mà sau đó không dùng | Σ, `issuer`, ℓ (chỉ cần cho Điều 58, mà Điều 58 đã hoãn sang giai đoạn 2 theo A33), μ_v tách riêng | Theo cookbook 5.0: công thức hay ký hiệu không được dùng lại ở chỗ nào thì xoá. |
| 9 | Câu nào cũng có "i.e.", ngoặc đơn, dấu chấm phẩy | "…, i.e. the provisions…", "(including provisions whose scope…)", "among others" | Cả trang chỉ dùng tối đa một "i.e.". Ngoặc đơn dài thì tách thành câu riêng. |
| 10 | Section 3 quá dài | S3 chiếm khoảng 4 trang LNCS, tức khoảng 30% của một bài 14 trang | Ngân sách ở mục 1: S3 khoảng 2,5 trang. |

Cách làm để giọng văn là của mình:
1. Ghi ý của từng đoạn bằng gạch đầu dòng tiếng Việt, theo đúng bảng ở mục 2–3 dưới đây.
2. Tự viết câu tiếng Anh từ các gạch đầu dòng đó. Công cụ chỉ dùng để soát ngữ pháp **từng câu**, không đưa cả đoạn cho nó viết lại.
3. Dùng một ví dụ duy nhất cho cả bài (mục 0b), lấy từ dữ liệu thật của mình, và kể bằng lời của mình.
4. Viết xong thì soát bằng cookbook 9.2 và danh sách cấm ở mục 5.

---

## 0b. Ví dụ xuyên suốt: chuỗi giấy phép lao động

Cả bài chỉ dùng **một** ví dụ, giới thiệu một lần ở 3.1 (Example 1). Từ đó mọi đoạn khác chỉ nhắc lại phần của ví dụ mà đoạn đó cần, không kể lại câu chuyện. Không dùng ví dụ Điều 35, câu hỏi phi công hay câu hỏi bà A của `overview.md` nữa.

**Câu hỏi.** Một chuyên gia nước ngoài vào Việt Nam một lần và làm việc 45 ngày. Người đó có phải có giấy phép lao động không? Đặt φ = "phải có giấy phép lao động".

**Chuỗi văn bản.** Tất cả đều có trong kho và đều đã chạy ra dữ liệu thật trong `data/processed/` (đã kiểm ngày 16/11):

| Mắt xích | Đơn vị | Dữ liệu thật trong kho |
|---|---|---|
| điều kiện gốc | LC D151.K1.d: "Có giấy phép lao động…, trừ trường hợp quy định tại Điều 154" | cạnh `refers_to` D151.K1.d → D154 (bước 1.2) |
| ngoại lệ tường minh | LC D154 (9 khoản không cần giấy phép) | cạnh `exception_of` D154 → D151.K1.d, `how = regex` (bước 1.5) |
| nút điều kiện không có đích | LC D151.K3: "…trừ trường hợp điều ước quốc tế mà nước Cộng hòa xã hội chủ nghĩa Việt Nam là thành viên có quy định khác" | nút `dieu_kien` (loại `cu_the`) → D151.K3, cùng Điều với điều kiện gốc. Lưu ý: nút điều kiện của D151.K1.d chỉ trùng ý với cạnh D154 nên không dùng làm ví dụ |
| điều khoản giao (Δ) | LC D154.K9 "Trường hợp khác theo quy định của Chính phủ" | `delegation_clauses`: D154.K9, cơ quan được giao là Chính phủ; `filled_by` = ND152, ND70, ND219 |
| văn bản lấp Δ | ND152, ND219 | cạnh `details` → D154.K1, D154.K2, D154.K9 (`how = regex`, căn cứ "khoản 1, 2 và 9 Điều 154") |
| phiên bản cũ | ND152 D7.K8: "dưới 30 ngày và không quá 03 lần trong 01 năm" | khoảng hiệu lực [2021-02-15, 2025-08-07) |
| phiên bản mới | ND219 D7.K13.a: "tổng thời gian dưới 90 ngày trong 01 năm" | khoảng hiệu lực [2025-08-07, ∞) |
| chỉ thị | ND219 D35.K2: phần lao động nước ngoài của ND152 hết hiệu lực theo chủ đề | loại 10 trong `directive_types.md` |

**Bốn ngày hỏi, ra đủ bốn kết quả.** Đây là lý do chọn chuỗi này: một câu hỏi duy nhất mà đi qua được mọi tầng.

| τ | Tình trạng KB tại τ | Kết quả |
|---|---|---|
| 10/01/2021 | LC đã hiệu lực (01/01/2021), ND152 thì chưa (15/02/2021): D154.K9 chưa có văn bản lấp | insufficient `[CHỜ QUYẾT: Δ chưa lấp ảnh hưởng suy luận ra sao, pipeline_design 7.1]` |
| 01/06/2025 | ND152 D7.K8 in_force; 45 ngày không thoả "dưới 30 ngày" | concluded: phải có giấy phép |
| 01/10/2025 | ND152 D7.K8 expired, ND219 D7.K13.a in_force; 45 < 90 | rebutted `[CHỜ QUYẾT]`: chỉ ra rebutted nếu có quy tắc kết luận phủ định (A33 (c)); nếu không có thì kết quả là insufficient. D154 viết "không thuộc diện cấp giấy phép", tức là một kết luận phủ định, nên đây là ca rebut tự nhiên. |
| 01/10/2025, giả sử quy tắc của ND219 D7.K13.a bị cô lập | | no_answer |

**Ví dụ đi qua từng đoạn thế nào** (mỗi đoạn chỉ lấy phần của mình, 1–3 dòng):

| Đoạn | Phần của ví dụ được dùng |
|---|---|
| 3.1 Đ1 | câu hỏi và hai ngày 01/06/2025, 01/10/2025; định nghĩa viết tắt LC, ND152, ND219 |
| 3.2 Đ5 | khoảng hiệu lực của ND152 D7.K8 cho ra hai trạng thái |
| 3.2 Đ6 | bốn cạnh của chuỗi: `refers_to`, `exception_of`, `details`; D154.K9 ∈ Δ |
| 3.2 Đ7 | quy tắc của ND152 D7.K8 vào Π ở ngày thứ nhất, rời Π ở ngày thứ hai |
| 3.3 Hình 1 | (tuỳ chọn) ghi nhãn ND219 chạy qua các khối |
| 4.1 Đ1–Đ4 | Δ nhận ra D154.K9; `details` bằng regex; `exception_of` D154 → D151.K1.d; nút điều kiện "điều ước quốc tế" của D151.K3 |
| 4.2 Đ6–Đ8 | ND219 đóng ND152 D7.K8 và mở D7.K13.a; hết hiệu lực theo chủ đề; A(ND219) |
| 4.3 Đ11–Đ14 | mệnh đề của D151.K1.d; vị từ "có giấy phép lao động" dùng chung giữa D151.K1.d và D153.K2, D153.K3; quy tắc chặn từ D154 |
| 4.4 Đ17–Đ18 | bảng bốn ngày ở trên |

**Chỗ ví dụ chưa phủ được, phải nói thật:**
- *Nối `details` bằng LLM.* Ở chuỗi này regex đã tìm ra đích, nên không có lượt LLM. Mục 4.1 Đ3 chỉ nêu cơ chế, không cần ví dụ.
- *Ngoại lệ ngầm (1.7).* Ứng viên tự nhiên là cặp (D154, D153.K2): D153.K2 phạt người "không có giấy phép lao động" mà không viết chữ "trừ". Đây chỉ là `[MINH HOẠ]` cho tới khi 1.6B và 1.7 chạy ra cặp này thật. Nếu chúng không ra, đổi sang cặp mà 1.7 tìm thấy thật trong cùng chuỗi Điều 151–157.
- *Pending (ND283 Điều 66).* Không nằm trong chuỗi. Nêu cơ chế bằng một mệnh đề, không kể chuyện.
- *Quy tắc của văn bản lấp Δ gắn vào D154.K9 thế nào* `[CHỜ QUYẾT]`. Quy tắc của ND219 D7.K13.a phải kết luận cùng vị từ "không thuộc diện cấp giấy phép" với D154, thì quan hệ chặn D154 → D151.K1.d mới có tác dụng. Nghĩa là phải tái dùng vị từ **giữa hai văn bản** (bước 2.6), mà A32 mới chỉ giới hạn trong BLLĐ. Ví dụ xuyên suốt làm lộ đúng chỗ này. Nên chốt với giảng viên, vì đây có thể là điểm đóng góp chính của bài.

---

## 1. Ngân sách trang

Giả định: bài hội nghị LNCS 12–14 trang. Một trang LNCS chứa khoảng **44 dòng** (đếm trên trang 2 của bản draft). Quy đổi các thành phần:

| Thành phần | Số dòng chiếm |
|---|---|
| Tiêu đề subsection, tính cả khoảng trắng | 2 |
| Công thức hiển thị một dòng | 2–3 |
| Công thức phân trường hợp (cases) 4 dòng | 6 |
| Hình 1 kèm caption | khoảng 15 (⅓ trang) |
| Bảng 6–8 dòng kèm caption | khoảng 14–16 |
| Mục liệt kê (itemize) | số dòng chữ + 1 |

**Mục tiêu: S3 + S4 khoảng 6,4 trang, tức khoảng 283 dòng.** S3 khoảng 2,5 trang (cắt khoảng 1,5 trang so với draft); S4 khoảng 4 trang.

| Phần | Dòng | Trang |
|---|---|---|
| S3 câu mở đầu section | 0–2 | – |
| 3.1 Problem | 22 | 0,5 |
| 3.2 Knowledge base model | 51 | 1,15 |
| 3.3 Overview (có Hình 1) | 33 | 0,75 |
| **Tổng S3** | **≈108** | **≈2,5** |
| 4.1 Structural layer | 30 | 0,7 |
| 4.2 Update engine (có Bảng 1) | 50 | 1,15 |
| 4.3 Knowledge layer (có Bảng 2) | 67 | 1,5 |
| 4.4 Date-aware QA | 26 | 0,6 |
| **Tổng S4** | **≈175** | **≈4,0** |

Phải cắt khỏi draft:
- đoạn lộ trình đầu S3;
- bộ `d = (id, issuer, ℓ, t_iss, t_eff)` dưới dạng công thức (chuyển thành nửa câu);
- Σ;
- quy tắc phá hoà theo id;
- mã đơn vị;
- quy tắc ngày `x + 1`;
- câu về cặp văn bản cùng tên ngắn;
- A(d) (chuyển sang 4.2, vì đây là thao tác chứ không phải biểu diễn);
- câu song ngữ thừa.

---

## 2. Section 3: bài toán và mô hình KB (≈108 dòng)

Quy tắc của cookbook (mục 1) vẫn đúng và nên giữ: S3 trả lời "biểu diễn thế nào", S4 trả lời "làm gì trên biểu diễn đó". Thứ tự subsection của S4 phải trùng thứ tự các khối trong Hình 1.

Tên section: chọn danh từ chỉ đúng đối tượng, ví dụ kiểu "Date-indexed knowledge base". Tránh tên chung chung như "Proposed Framework".

### Câu mở S3: 0–2 dòng
Bỏ đoạn lộ trình. Nếu muốn giữ thì chỉ một câu, viết sau cùng.

### 3.1 Problem: 22 dòng

**Đ1. Ví dụ dẫn (7–8 dòng).** Đây là lần duy nhất ví dụ xuyên suốt (mục 0b) được kể đầy đủ. Việc của đoạn: cho thấy cùng một câu hỏi có hai đáp án theo ngày.
- Chuyên gia nước ngoài làm 45 ngày; hỏi ở hai ngày 01/06/2025 và 01/10/2025.
- Chuỗi trong một câu: LC D151 yêu cầu giấy phép, trừ các trường hợp ở D154; D154.K9 giao cho Chính phủ; Chính phủ lấp bằng ND152, sau đó bằng ND219.
- ND152 Điều 7 khoản 8 (dưới 30 ngày, tối đa 3 lần/năm) chuyển sang ND219 Điều 7 khoản 13 điểm a (tổng dưới 90 ngày/năm), hiệu lực 07/08/2025. ND219 Điều 35 khoản 2 cho phần lao động nước ngoài của ND152 hết hiệu lực **theo chủ đề**, không nêu số Điều.
- Định nghĩa viết tắt ND152, ND219, LC ngay tại đây.
- Không kể ngày 10/01/2021 và ca cô lập ở đây; để dành cho 4.4, nơi ví dụ "trả lời" lại câu hỏi đặt ra từ đầu.
- Nguồn: `docs/reference/labor_code_survey.md` mục 5.
- Định dạng: `Example 1.` in nghiêng. Câu cuối của đoạn nói kết quả hai ngày; không thêm câu bình luận.

**Đ2. Phát biểu bài toán (8 dòng).** Việc của đoạn: nêu đầu vào, đầu ra và hai tiêu chí đúng.
- Đầu vào: luật gốc d₀ và chuỗi d₁…dₙ, mỗi văn bản có ngày ban hành và ngày hiệu lực.
- Đầu ra: với câu hỏi q và ngày sự việc τ, trả **một trong bốn kết quả** kèm căn cứ (các phiên bản nguồn). Bốn kết quả nêu tên một lần ở đây; định nghĩa đặt ở 4.4.
- (C1) căn cứ chỉ gồm phiên bản có hiệu lực tại τ. (C2) cập nhật tăng dần cho cùng Π_τ với dựng lại từ đầu.
- Một câu: không có người duyệt; mọi đầu ra của LLM qua cổng kiểm bằng máy.
- Không cần công thức; có thể dùng `\textit{Problem.}`.
- Không đặt việc chọn BLLĐ làm kho văn bản ở đây; việc đó thuộc S5.

**Đ3. Phạm vi và giả định (5 dòng).**
- Chỉ giữ 2 giả định có hệ quả: ngày hiệu lực đã biết; mọi thay đổi được nêu bằng câu chỉ thị tường minh.
- Một câu về hệ quả khi giả định sai (văn bản mới thay văn bản cũ mà không nói, chỉ được gắn cờ, xem loại 26 ở `docs/reference/directive_types.md`). Viết bằng câu của mình, không dùng khuôn "Assumption (A2) fails when".

### 3.2 Knowledge base model: 51 dòng

**Đ4. Văn bản, đơn vị, phiên bản (8 dòng + Eq. 1).**
- Văn bản chỉ cần nửa câu: ngày ban hành, ngày hiệu lực. Bỏ `issuer`. Chỉ giữ cấp văn bản ℓ nếu ô `[CHỜ QUYẾT]` về Điều 58 ở 4.3 (Đ14b) được chốt là có viết; nếu không, ℓ không được dùng lại ở chỗ nào.
- Đơn vị: Điều, Khoản, Điểm, dòng phụ lục; mỗi đơn vị có một cha. Không đưa mã định danh vào.
- Ý chính của đoạn: **không ghi đè**; mỗi thay đổi tạo ra một phiên bản.
- Dạng A (Definition), một dòng:
  ```latex
  v = (u,\ \mathit{text},\ [t_{\mathrm{from}}, t_{\mathrm{to}}),\ \mu), \quad \mu \in \{\mathsf{normal}, \mathsf{pending}, \mathsf{suspended}\}
  ```
- Mệnh đề "where" ngắn: khoảng nửa mở; t_to = ∞ khi chưa bị đóng; pending thì t_from chưa có.
- Nguồn: `docs/reference/directive_types.md` (đầu file), mục Versions ở `docs/decisions.md`.

**Đ5. Hàm trạng thái theo ngày (5 dòng chữ + 6 dòng công thức + 3 dòng ví dụ = 14).** Đây là phần lõi, nên dành chỗ.
- Dạng cases:
  ```latex
  \sigma_v(\tau) = \begin{cases}
    \mathsf{not\_yet}  & \mu = \mathsf{normal},\ \tau < t_{\mathrm{from}} \\
    \mathsf{in\_force} & \mu = \mathsf{normal},\ t_{\mathrm{from}} \le \tau < t_{\mathrm{to}} \\
    \mathsf{expired}   & \mu = \mathsf{normal},\ \tau \ge t_{\mathrm{to}} \\
    \mu                & \text{otherwise}
  \end{cases}
  ```
- Diễn giải: **một ý duy nhất**. Trạng thái được tính từ khoảng hiệu lực chứ không lưu, nên một phiên bản phục vụ được mọi ngày hỏi.
- Ví dụ: ND152 Điều 7 khoản 8 có khoảng [15/02/2021, 07/08/2025), nên ra `in_force` ở ngày thứ nhất và `expired` ở ngày thứ hai. Hai dòng là đủ.

**Đ6. Định nghĩa KB (Definition 1, 17 dòng).**
- Chọn **một** dạng bộ và giữ cho cả bài và luận văn. Khuyến nghị theo `docs/design/pipeline_design.md` mục 2:
  ```latex
  \mathcal{K} = (\mathcal{D}, \mathcal{U}, \mathcal{V}, \mathcal{E}, \Delta, \mathcal{P}, \mathcal{R})
  ```
  Draft dùng bộ 5 phần tử, coi U và Δ là tập suy ra. Cách đó cũng được, nhưng phải khớp với chương luận văn.
- Itemize, mỗi thành phần một dòng có kiểu, không giải thích dài:
  - E ⊆ (nút) × (kiểu) × (nút). Chỉ nêu tên **4 kiểu cạnh được dùng lại ở S4**: `refers_to`, `exception_of`, `details`, `based_on`. Nhắc nút điều kiện bằng nửa câu.
  - Δ ⊆ U.
  - P: mỗi vị từ có tên, số đối số và loại (`concept` hoặc `input`).
  - R: mỗi quy tắc có src(r) ∈ V và tập cờ.
- Bỏ tập Q riêng; dùng cờ `isolated` thẳng trong Eq. 3. Bớt được một ký hiệu.
- Đặt Definition sau một câu dẫn nói KB cần chứa thêm những gì so với chữ luật. **Chỉ một câu, đừng lặp khuôn "must" của draft.**
- Ví dụ, 2 dòng sau Definition: trong Example 1, E chứa D151.K1.d →`refers_to` D154, D154 →`exception_of` D151.K1.d, ND152 →`details` D154.K9; còn Δ chứa D154.K9.

**Đ7. Chương trình tại ngày τ (10 dòng + Eq. 3).** Đây là công thức trung tâm của bài.
- Dạng E (điều kiện chọn):
  ```latex
  \Pi_\tau = \{\, r \in \mathcal{R} \;:\; \sigma_{\mathrm{src}(r)}(\tau) = \mathsf{in\_force} \ \wedge\ \mathsf{isolated} \notin \mathrm{flags}(r) \,\}
  ```
- Một câu về ngôn ngữ: quy tắc viết bằng s(CASP), `not` là phủ định do thất bại (negation as failure). Ngữ nghĩa chi tiết đặt ở 4.3. Trích dẫn s(CASP) đang thiếu: `[CẦN TRÍCH DẪN]`.
- Diễn giải: căn cứ của câu trả lời là các src(r) của những quy tắc được dùng, và đây chính là (C1).
- Ví dụ: quy tắc của ND152 Điều 7 khoản 8 thuộc Π ở ngày 01/06/2025 và bị thay ở ngày 01/10/2025. Hai dòng là đủ.

### 3.3 Overview: 33 dòng

**Hình 1 (≈15 dòng).**
- Bốn khối theo đúng thứ tự 4.1 → 4.4.
- Khối có gọi LLM tô khác màu; ngay sau mỗi khối LLM vẽ một ô "check".
- Mũi tên ghi ký hiệu dữ liệu chạy qua (d, K, A(d), Π_τ).
- Caption 2 câu: hình là gì, và người đọc cần nhìn vào đâu. Ở hình này, chỗ cần nhìn là LLM chỉ xuất hiện ở các khối tô màu, và phần hỏi đáp chỉ đọc Π_τ.

**Đ8. Ghép chuỗi (16 dòng).**
- Dạng C:
  ```latex
  \mathrm{Update}(\mathcal{K}, d) = \big(\mathcal{S}^{d}_{\mathrm{know}} \circ \mathcal{S}^{d}_{\mathrm{upd}} \circ \mathcal{S}^{d}_{\mathrm{str}}\big)(\mathcal{K})
  ```
- Kiểm kiểu: cả ba hàm đều có dạng K → K.
- Ba gạch đầu dòng, mỗi dòng nói hàm đó **thêm hoặc sửa thành phần nào của K**:
  - str: D, U, V, E, Δ;
  - upd: V;
  - know: P, R, và E (ngoại lệ ngầm).
- Một câu: K₀ = S_know ∘ S_str trên d₀, không áp chỉ thị. Văn bản được nạp theo thứ tự t_eff.
- Một câu: LLM chỉ được dùng ở những chỗ phải đọc nghĩa của chữ. Danh sách đầy đủ đặt ở Bảng 2 (mục 4.3), không liệt kê ở đây; draft liệt kê ở đây là bị trùng.

---

## 3. Section 4: các tầng xử lý (≈175 dòng)

Khuôn mỗi subsection, theo cookbook 4.2 nhưng viết theo kiểu của mình:
- câu đầu: tầng này nhận gì và sửa thành phần nào của K;
- các bước;
- cổng kiểm;
- một ví dụ;
- đầu ra được tầng sau dùng thế nào.

**Không** bắt buộc mọi đoạn có câu "vì sao".

### 4.1 Structural layer (S_str): 30 dòng
Phần này người đọc đã quen, nên viết gọn.

**Đ1. Tách đơn vị và loại Điều (7 dòng).**
- Cây Chương → Điều → Khoản → Điểm.
- Số thứ tự phải liên tục; bị đứt thì từ chối văn bản (fail-closed).
- Một câu về loại Điều: gán bằng regex trên tiêu đề, mặc định `substantive`. **Không dùng LLM (A14).** `method.md` mục 3.3 còn ghi LLM, đó là chỗ đã cũ.
- Nguồn: `docs/design/steps_1_1_to_1_5.md`.

**Đ2. Dẫn chiếu (5 dòng).**
- Mỗi cụm dẫn chiếu có đúng một trong ba kết cục: nối thành `refers_to`, chờ đích, hoặc không giải được kèm lý do.
- Ý quan trọng: quan hệ chờ đích là thứ cho phép văn bản sau nối vào văn bản trước.
- Ví dụ, nửa câu: "Điều 154 của Bộ luật này" trong D151.K1.d ra `refers_to` D154.

**Đ3. Δ và nối văn bản dưới luật (8 dòng + 2 dòng điều kiện = 10).**
- Δ nhận diện bằng cụm giao quyền ("do Chính phủ quy định"). **Câu song ngữ duy nhất của S4 có thể đặt ở đây hoặc ở 4.2.**
- `based_on` lấy từ phần căn cứ ban hành; `details` lấy từ điều phạm vi điều chỉnh.
- Ví dụ: D154.K9 ("theo quy định của Chính phủ") vào Δ. Điều phạm vi của ND152 và ND219 nêu "khoản 1, 2 và 9 Điều 154", nên `details` được nối bằng regex.
- Văn bản không nêu số Điều thì LLM chọn **trong Δ** (tập đóng). Ví dụ xuyên suốt không đi qua nhánh này, nên chỉ nêu cơ chế.
- Dạng E, điều kiện nhận:
  ```latex
  \mathrm{accept}(d \xrightarrow{\mathsf{details}} a) \iff a \in \Delta \ \wedge\ \mathrm{kw}(d) \sqsubseteq \mathrm{text}(a)
  ```
- `[CHỜ QUYẾT: cách gọi tên]` Mã hiện tại còn yêu cầu một lượt chạy thứ hai bằng model khác chọn trùng. Viết thẳng ra thì phản biện có thể đọc thành "LLM kiểm LLM", trái nguyên tắc mà bài tự nêu. Cổng bằng máy thật sự là điều kiện **từ khoá có trong Điều đích**. Cần cùng giảng viên chọn: (a) mô tả lượt thứ hai là điều kiện đồng thuận và nói rõ nó không phải phép kiểm; (b) bỏ lượt thứ hai khỏi bài.

**Đ4. Ngoại lệ tường minh (6 dòng).**
- Cụm kích hoạt "trừ trường hợp…", "không áp dụng…" sinh ra `exception_of`. Ví dụ: D154 →`exception_of` D151.K1.d.
- Ngoại lệ không có đích trở thành **nút điều kiện**. Ví dụ ngay trong cùng Điều: D151.K3 "trừ trường hợp điều ước quốc tế… có quy định khác".
- Chỉ nêu cơ chế; số cạnh (66, 43 từ nút điều kiện) thuộc S5.

### 4.2 Update engine (S_upd): 50 dòng
Đây là phần khác biệt nhất của bài, nên dành chỗ.

**Đ5. Câu chỉ thị (6 dòng).**
- Tìm câu chỉ thị trong các Điều hiệu lực – chuyển tiếp và trong văn bản sửa đổi.
- Phân tích bằng mẫu tất định thành (thao tác, tập đích, nội dung).
- Câu không khớp mẫu nào thì **báo và không áp**.
- **Không có LLM ở bước này.** `method.md` mục 3.4 và Thuật toán 1 dòng 3 ghi "LLM phân loại", đó là chỗ đã cũ; README nói chỉ 1.6A, 1.6B và 2.2 dùng LLM.

**Bảng 1 (≈16 dòng).**
- Gộp 26 loại ở `docs/reference/directive_types.md` thành khoảng **6 nhóm**: sửa hoặc bổ sung; bãi bỏ hoặc thay cả văn bản; hết hiệu lực theo chủ đề; hiệu lực có điều kiện (pending); hiệu lực có thời hạn hoặc áp dụng thay; danh mục và chuyển tiếp.
- Ba cột: nhóm | dạng câu | tác động lên phiên bản.
- Thêm cột "số ca trong kho" là `[CẦN SỐ]`, hoặc chuyển cột đó sang S5.
- Nhắc trong chữ **trước** bảng và nói người đọc cần thấy gì: chỉ hai nhóm cần thao tác khác "đóng rồi mở".

**Đ6. Toán tử trên phiên bản (4 dòng chữ + 3 dòng công thức + 2 dòng thứ tự = 9).**
- Dạng G:
  ```latex
  \mathcal{V}' = (\delta_k \circ \cdots \circ \delta_1)(\mathcal{V}), \quad
  \delta \in \{\mathrm{close}(u, t),\ \mathrm{open}(u, \mathit{text}', t)\}
  ```
- Kiểm kiểu: cả hai toán tử đều có dạng V → V. close đặt t_to = t; open thêm (u, text′, [t, ∞), normal).
- Ý chính: không xoá; lịch sử còn nguyên.
- Phải nói thứ tự áp, vì cookbook 5.8 đã chỉ ra P4 thiếu đúng chỗ này. Mã hiện tại (`src/versions.py`, hàm `new_version`) làm như sau:
  - thay chữ là **một** thao tác gộp: đóng phiên bản cũ rồi mở phiên bản mới, replace = open ∘ close;
  - các chỉ thị được áp theo thứ tự xuất hiện trong văn bản;
  - hai chỉ thị cùng một sự kiện nhắm vào cùng một đơn vị thì sửa tại chỗ, nên không sinh khoảng rỗng [t, t);
  - các văn bản được xử lý theo (t_eff, t_iss, id) (hàm `order_docs`).

  Trong bài chỉ cần một câu: thứ tự trong văn bản, và gộp khi trùng đơn vị. Mỗi lần mã đổi thì kiểm lại.

**Đ7. Hai ca khó (7 dòng).**
- Hết hiệu lực theo chủ đề: khớp tiêu đề Chương. Chương có tiêu đề chung thì chuyển `suspended`, vì không biết phạm vi. Ví dụ ND219 Điều 35 khoản 2 (nối lại Example 1).
- Pending: sự kiện điều kiện được lưu nguyên văn và chỉ kích hoạt khi có văn bản khớp. Ví dụ xuyên suốt không có ca này; chỉ nêu cơ chế bằng một mệnh đề, không kể ND283.
- Đây là chỗ cho thấy phương pháp không chỉ là "sửa chữ".

**Đ8. Tập ảnh hưởng (5 dòng chữ + 2 dòng công thức = 7).**
- Công thức:
  ```latex
  A(d) = T(d) \cup N\big(T(d)\big)
  ```
- T(d) gồm các đơn vị mà d thêm vào, hoặc mở hay đóng phiên bản. N(S) gồm các đơn vị nối với S qua `details`, `refers_to`, `exception_of`, hoặc qua cùng một vị từ `concept`.
- `[CHỜ QUYẾT: N đi bao nhiêu bước]` (`pipeline_design.md` mục 7.4). Draft viết "stops after one hop" như sự thật; đó là lỗi.
- Ví dụ, A(ND219): T gồm các đơn vị của ND219 và các đơn vị ND152 bị đóng (trong đó có D7.K8). N thêm D154.K9 (qua `details`), Điều 154 khoản 3–8 (ND219 Điều 7 khoản 1 dẫn chiếu tới), và D151.K1.d nếu N đi được 2 bước qua `exception_of`. Ví dụ này cho thấy ngay vì sao số bước của N quan trọng: đi 1 bước thì D151.K1.d, chính đơn vị mà câu hỏi phụ thuộc, nằm ngoài A(d). `[KIỂM khi có mã 2.5]`

**Đ9. Đối chứng (3 dòng, có thể gộp vào Đ8).**
- Dựng lại từ đầu và so Π_τ với kết quả tăng dần là cách kiểm (C2). Nêu cơ chế ở đây; kết quả đặt ở S5.

**Tuỳ chọn.** Thuật toán 1 (Update) dạng pseudocode, khoảng 14 dòng. Nếu đưa vào thì cắt Đ5 và Đ9 tương ứng, để giữ tổng khoảng 50 dòng.

### 4.3 Knowledge layer (S_know): 67 dòng
**Mô tả thiết kế mới (mệnh đề), không mô tả bản cũ (gạch cụm).** `method.md` mục 3.5 vẫn còn "gạch cụm" và "mô hình khác trích lại để kiểm"; cả hai đã bị thay (A25, A38). Ví dụ vẫn là chuỗi giấy phép lao động (mục 0b).

**Đ10. Mở tầng (3 dòng).** Ba bước LLM nối tiếp nhau, mỗi bước có cổng riêng. Bảng 2 tóm tắt các cổng.

**Bảng 2: các chỗ dùng LLM và cổng kiểm (≈14 dòng).** Đây là "chữ ký" của bài; nó thay cho nhiều đoạn văn xuôi.

| Bước | LLM được chọn trong | Máy kiểm | Không qua thì |
|---|---|---|---|
| nối `details` (4.1) | Δ | đích ∈ Δ, từ khoá có trong Điều đích | cô lập |
| mệnh đề (Đ11) | chuỗi con của ngữ cảnh | khuôn dòng, chuỗi con liền, cổng âm tiết, không phải câu dẫn | hỏi lại một lần, sau đó loại dòng |
| vị từ (Đ12) | danh sách ứng viên ∪ {new} | dạng tên, tên ∈ ứng viên, khớp số đối số | `[KIỂM]` |
| ngoại lệ ngầm (Đ13) | {a→b, b→a, none} | bằng chứng là chuỗi con, hai đầu tồn tại, không trùng, không tạo vòng | đưa vào `rejected` |
| quy tắc (Đ14) | vị từ được phép | biên dịch, số đối số, bộ quét, biến | sửa tối đa 2 vòng, sau đó cô lập |
| câu hỏi (4.4) | vị từ `input` | `[CHỜ CODE]` | ngoài phạm vi |

**Đ11. Tách mệnh đề, 1.6A (8 dòng + 3 dòng công thức = 11).**
- Một mệnh đề là một điều kiểm được đúng hoặc sai, kèm vai (điều kiện, kết luận, ngoại lệ), chủ thể (là đối số), phương thức (được, phải, cấm, không áp dụng), cực, và các mẩu trích.
- Dạng B rồi E:
  ```latex
  f_{\mathrm{prop}} : (u, c_u) \mapsto \langle \rho_1, \dots, \rho_m \rangle, \qquad
  \mathrm{ok}(\rho) \iff \forall s \in \mathrm{tr}(\rho) : s \sqsubseteq c_u \ \wedge\ \mathrm{syl}(\mathrm{core}(\rho)) \subseteq \textstyle\bigcup_{s \in \mathrm{tr}(\rho)} \mathrm{syl}(s)
  ```
  c_u là ngữ cảnh của đơn vị (tiêu đề, câu dẫn, chữ đơn vị). ⊑ là quan hệ chuỗi con liền.
- Diễn giải: cổng âm tiết cho phép bỏ chữ, nhưng không cho thêm chữ không có trong luật.
- Nói luôn chỗ yếu: cổng không bắt được việc đảo thứ tự chữ hay sai nghĩa.
- Ví dụ: D151.K1.d cộng câu dẫn khoản 1 ("…phải đáp ứng các điều kiện sau đây") ra một `dieu_kien` "có giấy phép lao động" kế thừa chủ thể "người lao động nước ngoài" từ câu dẫn, và một `con_tro` tới D154. **Thay bằng dòng thật** khi 1.6A chạy xong lô Điều 151: `[CẦN SỐ]`.
- Lý do làm mệnh đề thay vì gạch cụm (tỉ lệ tái dùng 3% của bản cũ): đặt ở S5 hoặc ablation, không đặt ở đây.

**Đ12. Sổ vị từ và tái dùng, 1.6B (8 dòng + 2 dòng công thức = 10).**
- Cấp 1: cùng lõi chuẩn hoá **và** cùng chữ ký đối số thì máy ép cùng tên, không hỏi LLM.
- Cấp 2: máy lập danh sách ứng viên giới hạn bằng đồ thị (cùng Điều, nối qua 1.2 hoặc 1.5, chung từ). LLM chọn `reuse` hoặc `new`.
- Dạng E:
  ```latex
  g(\rho) \in \mathrm{Cand}(\rho) \cup \{\mathsf{new}\}, \quad |\mathrm{Cand}(\rho)| \le k, \quad
  g(\rho) \ne \mathsf{new} \Rightarrow \mathrm{ar}(g(\rho)) = |\mathrm{args}(\rho)|
  ```
  k = 20 là số đặt thủ công (A39); nói thẳng điều đó.
- Diễn giải: vị từ dùng chung là thứ nối các điều luật rời nhau. Gộp nhầm nặng hơn tách sót, nên luật `reuse` để chặt.
- Ví dụ: "có giấy phép lao động" (D151.K1.d) và "không có giấy phép lao động" (D153.K2, D153.K3) phải ra **cùng một** vị từ, chỉ khác `cuc`. Đây là ca thật đã ghi trong decisions (A27) và là lý do tách `cuc` ra khỏi tên.
- `[CHỜ CODE]`: viết lại `names-2`.

**Đ13. Ngoại lệ ngầm, 1.7 (6 dòng).**
- Cặp ứng viên: hai đơn vị cùng dùng một vị từ `concept`, bỏ các cặp đã có cạnh ở 1.5.
- LLM chọn một trong ba nhãn, kèm câu bằng chứng nguyên văn.
- Cạnh được nhận mang cờ `llm_proposed`.
- Ví dụ `[MINH HOẠ]`: cặp (D154, D153.K2). D153.K2 buộc người "không có giấy phép lao động" phải xuất cảnh mà không viết chữ "trừ", trong khi người thuộc D154 không cần giấy phép. Phải xác nhận lại khi 1.7 chạy (xem mục 0b).
- `[CHỜ CODE]`. Phân biệt rebut và undercut: `[CHỜ QUYẾT]` (A32).

**Đ14. Quy tắc và quan hệ chặn, 1.8 (6 dòng chữ + 4 dòng công thức + 4 dòng = 14).**
- Dạng F, có nói rõ ngữ nghĩa của `not`. Cạnh trong E nối **đơn vị** chứ không nối quy tắc, nên công thức phải đi qua cạnh rồi mới tới quy tắc. Viết khác đi là lỗi kiểu, đúng lỗi mục 7 của cookbook 8.2:
  ```latex
  \text{for each } (u_s, \mathsf{exception\_of}, u_o) \in \mathcal{E},\ \mathsf{isolated} \notin \mathrm{flags},\ e \in \mathcal{R}(u_s),\ r \in \mathcal{R}(u_o),\ \mathrm{vars}(e) \subseteq \mathrm{vars}(r):
  \\
  b_{e,r} := \ \mathrm{blocked}(r, \bar{X}) \leftarrow \mathrm{applies}(e, \bar{X}) \wedge \mathbf{not}\ \mathrm{blocked}(e, \bar{X}), \qquad \mathrm{src}(b_{e,r}) = \mathrm{src}(e)
  ```
  R(u) là các quy tắc trích từ u. Hai điều kiện không được bỏ:
  - **src(b) = src(e)**: quy tắc chặn mang phiên bản của đơn vị nêu ngoại lệ. Nhờ vậy, khi ngoại lệ hết hiệu lực, b tự rời Π_τ (Eq. 3). Thiếu điều kiện này thì một ngoại lệ đã hết hiệu lực vẫn tiếp tục chặn, và (C1) bị vỡ.
  - **cạnh cô lập không sinh b**. Bản draft lo việc này bằng tập Q; hướng dẫn này đã bỏ Q nên công thức phải nói thẳng.
- Diễn giải: chuỗi ngoại lệ lồng nhau được đi tới cùng. Bỏ cạnh nằm trong vòng, nên không có quy tắc nào phụ thuộc phủ định vào chính nó.
- Ví dụ: cạnh D154 → D151.K1.d sinh b, mang src là phiên bản của D154. Quy tắc của ND152 D7.K8 và ND219 D7.K13.a đi vào chuỗi này qua D154.K9; cách gắn chúng vào là `[CHỜ QUYẾT]` (mục 0b, gạch cuối).
- Nút điều kiện (ngoại lệ không có đơn vị đích, như "điều ước quốc tế" ở D151.K3) chưa vào được công thức này. Xem ô `[CHỜ QUYẾT]` bên dưới.
- Điều kiện vars(e) ⊆ vars(r) xuất phát từ lỗi thật đã thấy (S5 trong decisions). Đây là chi tiết "của mình", nên viết.
- Bộ quét 4 loại, sửa tối đa 2 vòng, sau đó cô lập: một câu.
- Một câu thừa nhận: cổng không chứng minh được quy tắc dịch đúng nghĩa luật. Điều đó chỉ đo được bằng bộ câu hỏi ở S5.
- `[CHỜ QUYẾT]`, giữ khoảng 3 dòng trống:
  - cách biên dịch 43 cạnh xuất phát từ nút điều kiện;
  - cách biên dịch `khong_ap_dung` và `liet_ke`;
  - quy tắc kết luận phủ định cho "bị bác" (A33 (a)–(c)).

**Đ14b. Xung đột giữa các văn bản (giữ 4 dòng, `[CHỜ QUYẾT]`).**
- A33 hoãn Điều 58 Luật 64/2025 sang giai đoạn 2, không bỏ nó khỏi bài. Bài có giai đoạn 2 nên tại cùng một τ có thể cùng có hiệu lực cả nghị định lẫn Bộ luật, và hai quy tắc ngược nhau mà không có cạnh `exception_of` là ca thật.
- Nếu chốt viết: dùng Dạng H, thứ tự từ điển theo cookbook 5.9: cấp văn bản ℓ (khoản 3), rồi ngày ban hành khi cùng cơ quan (khoản 4), rồi quy tắc áp dụng riêng do văn bản tự đặt (khoản 6); phần còn lại thì cô lập. Khi đó thêm ℓ vào 3.2 Đ4.
- Nếu chốt không viết: thay bằng một câu nói xung đột còn lại bị cô lập, và nêu đây là giới hạn.
- Nguồn: `method.md` mục 3.5 (chữ đã có), A33.

### 4.4 Date-aware question answering: 26 dòng
`[CHỜ CODE]` cho cả mục: bước 1.9 mới có một dòng thiết kế. Viết phần khung, đánh dấu phần chưa chốt.

**Đ15. Câu hỏi thành dữ kiện (5 dòng).**
- LLM đổi câu hỏi thành các dữ kiện F_q, chỉ dùng vị từ loại `input`.
- Câu hỏi không biểu diễn được thì xếp ngoài phạm vi.
- Máy không tự tính dữ kiện. Ví dụ: "vào Việt Nam một lần, làm 45 ngày" thành các dữ kiện về số ngày và số lần do người hỏi khai. So sánh 45 với 30 hay 90 do quy tắc làm, không do LLM làm. `[CHỜ QUYẾT: vị từ có đối số số và phép so sánh trong s(CASP)]`

**Đ16. Bốn kết quả (4 dòng chữ + 6 dòng công thức = 10).**
- Dạng cases:
  ```latex
  \mathrm{ans}(q, \tau) = \begin{cases}
    \mathsf{concluded}    & \Pi_\tau \cup F_q \vdash \varphi,\ \Pi_\tau \cup F_q \nvdash \neg\varphi \\
    \mathsf{rebutted}     & \Pi_\tau \cup F_q \vdash \neg\varphi \\
    \mathsf{insufficient} & \text{neither} \\
    \mathsf{no\_answer}   & \text{the derivation needs an isolated rule or edge}
  \end{cases}
  ```
- `[CHỜ QUYẾT]`, ba việc phải định nghĩa:
  - thứ tự xét giữa các trường hợp (no_answer có được xét trước không);
  - ⊢ cụ thể là gì trong s(CASP);
  - xử lý ca **cả φ lẫn ¬φ đều suy ra được**. Bộ quét của 1.8 sinh ra chính để bắt ca này (cặp kết luận ngược không có quan hệ chặn), nên người đọc sẽ hỏi.
- "rebutted" phụ thuộc vào việc có quy tắc kết luận phủ định (A33 (c)). Nếu chưa có thì nói rõ.

**Đ17. Example 1 trả lời lại (6 dòng).** Đây là chỗ khép vòng câu hỏi đặt ra ở 3.1.
- Dùng bảng bốn ngày ở mục 0b, viết thành bảng nhỏ 4 dòng (τ | phiên bản lấp D154.K9 ở τ | kết quả). Khi đó chữ chỉ còn 2 dòng.
- Cột căn cứ: 01/06/2025 trả về D151.K1.d và ND152 D7.K8; 01/10/2025 trả về D154 và ND219 D7.K13.a. Hai cột này là bằng chứng cho (C1).

**Đ18. Chỗ trống do Δ (3 dòng).** `[CHỜ QUYẾT]` (`pipeline_design.md` mục 7.1).
- Dòng τ = 10/01/2021 của cùng ví dụ: D154.K9 chưa có văn bản lấp, nên kết quả phải là insufficient chứ không được là "phải có giấy phép". Nếu suy luận chỉ dùng phủ định do thất bại thì sẽ ra sai "phải có giấy phép". Cơ chế để Δ ảnh hưởng tới suy luận chưa được thiết kế.
- Cũng là đáp án khi KB chỉ có LC (giai đoạn 1), nên một câu ở đây nối được hai giai đoạn.

---

## 4. Bảng công thức (để soát)

Tổng cộng 11 công thức đánh số. Mỗi công thức phải được dùng lại ở ít nhất một chỗ (cookbook 5.0).

| Eq | Nội dung | Dạng cookbook | Được dùng ở |
|---|---|---|---|
| 1 | phiên bản v | A | Eq. 2, Eq. 6 |
| 2 | σ_v(τ) | cases | Eq. 3, ví dụ |
| 3 | Π_τ | E | Eq. 11, (C1), 4.2 Đ9 |
| Def 1 | K | A | Eq. 4, mọi tầng |
| 4 | Update = ∘ | C | Hình 1, 4.1–4.3 |
| 5 | details accept | E | Bảng 2 |
| 6 | toán tử phiên bản | G | Eq. 2 (khoảng hiệu lực thay đổi) |
| 7 | A(d) | định nghĩa tập | S_know chạy trên A(d), (C2) |
| 8 | f_prop + cổng | B + E | Bảng 2, Eq. 9 |
| 9 | reuse | E | 1.7 (cặp ứng viên) |
| 10 | blocked | F (NAF) | Π_τ, ví dụ D154 → D151.K1.d |
| 11 | ans | cases | S5 (thước đo) |

Nếu thiếu chỗ thì Eq. 5 và Eq. 9 có thể viết thành điều kiện trong dòng chữ, không cần đánh số.

Bảng ký hiệu: lập riêng trước khi viết, như cookbook 5.1. Các ký hiệu dễ trùng:
- **R** (tập quy tắc) với **r** (quy tắc);
- **ρ** (mệnh đề) với **r**;
- **τ** (ngày hỏi) với **t** (ngày của phiên bản);
- **Δ** (điều khoản giao) với **δ** (toán tử phiên bản). Δ và δ dễ đọc nhầm; có thể đổi δ thành ω hoặc dùng close/open bằng chữ.

---

## 5. Danh sách cấm và cách soát

Cụm cấm, vì đã xuất hiện trong draft hoặc là câu mẫu của cookbook:
- note that
- in other words
- intuitively
- "This section defines / presents / describes …"
- "Assumption (A…) fails when"
- "To satisfy (C…)," đứng đầu câu
- "among others"
- "the latter"
- "i.e." quá một lần mỗi trang
- "plays a crucial role", "ensures that", "robust", "seamless", "leverage", "notably"
- "Moreover" hoặc "Furthermore" ở đầu hai đoạn liên tiếp

Soát nhanh trên file LaTeX:
```
grep -n -i -E "note that|in other words|intuitively|i\.e\.|this section (defines|presents|describes)|fails when|among others|the latter|crucial|ensure|robust|leverage|notably|moreover|furthermore" *.tex
```

Soát cấu trúc:
1. Đếm số đoạn mở bằng "To …" hoặc bằng câu có "must". Trên 2 đoạn trong một section thì viết lại.
2. Đếm tiêu đề in nghiêng đứng đầu đoạn. Tối đa 1 cụm mỗi section.
3. Mỗi công thức: có câu dẫn vào, có mệnh đề "where", có chỗ dùng lại (bảng mục 4). Bỏ phần diễn giải nếu nó chỉ đọc lại ký hiệu.
4. Mọi tham số có giá trị hoặc nhãn `[CẦN SỐ]`: k = 20 ứng viên, số vòng sửa = 2, số bước của N.
5. Đọc to từng đoạn. Đoạn nào nghe như liệt kê thì gộp ý, bỏ bớt mệnh đề phụ.
6. Đo số trang sau khi biên dịch. Vượt ngân sách mục 1 quá 10% thì cắt ở 4.1 trước, vì đó là phần quen thuộc nhất.

---

## 6. Bảng truy nguồn (để cập nhật khi mã đổi)

| Đoạn | Đọc lại khi đổi | Trạng thái 16/11 |
|---|---|---|
| 3.1 Đ1, Example 1 | `docs/reference/labor_code_survey.md` mục 5 | ổn định |
| 3.2 Đ4–Đ5 | `src/versions.py`; decisions mục Versions | có mã |
| 3.2 Đ6–Đ7 | `docs/design/pipeline_design.md` mục 2 | thiết kế |
| 4.1 | `docs/design/steps_1_1_to_1_5.md`; `src/links.py` (A30) | có mã |
| 4.2 Đ5–Đ7, Bảng 1 | `docs/reference/directive_types.md`; `src/directives*.py`, `src/versions.py` | có mã |
| 4.2 Đ8–Đ9 | `pipeline_design.md` mục 5 (2.5, 2.7) | chưa có mã |
| 4.3 Đ11 | `docs/design/step_1_6a_propositions.md`; A38, A39 | đang chạy |
| 4.3 Đ12 | A29, A37, A39 (`names-2`) | cần viết lại |
| 4.3 Đ13–Đ14 | `docs/design/steps_1_6_to_1_8.md` mục 5–6; A32, A33 | bản nháp |
| 4.4 | `docs/overview.md` (mục 1.9, chỉ lấy cơ chế); `pipeline_design.md` mục 7.1 | chưa thiết kế |
| ví dụ xuyên suốt (mục 0b) | `data/processed/l3/` (Δ, `details`), `l5_general/` (`exception_of`), `l6/versions.jsonl` (khoảng hiệu lực); `labor_code_survey.md` mục 5 | dữ liệu thật đến 2.4; từ 1.6 trở đi là minh hoạ |

Chỗ trong `docs/reference/method.md` **đã cũ, đừng chép sang bài**:
- 3.3: LLM gán loại Điều, và cần mô hình thứ hai xác nhận (A14 đã bỏ);
- 3.4 và Thuật toán 1: LLM phân loại câu chỉ thị lạ (thực tế là báo lỗi, không đoán);
- 3.5: "gạch cụm" và "lượt trích độc lập bằng mô hình khác" (A25, A38);
- 3.5: Điều 58 (A33 đã hoãn sang giai đoạn 2).

Chi tiết cài đặt (Sonnet 5.5 hay Opus 5.5 chạy qua phiên Claude Code, effort, số lô, phiên bản lời nhắc) thuộc Implementation hoặc S5, không thuộc S3–S4 (cookbook 6.4).
