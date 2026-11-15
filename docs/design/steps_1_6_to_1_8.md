# Bước 1.6 (bản cũ và phân tích lỗi), 1.7 và 1.8 (bản nháp)

Tài liệu tự đứng được. Viết ngày 15/11/2026. Nguồn: mô tả bước ở `docs/design/pipeline_design.md`, quyết định ở `docs/decisions.md` (A26 đến A39). Số liệu đo trên đĩa ngày 15/11, chỉ trên Bộ luật Lao động 45/2019 (BLLĐ).

**Trạng thái:** 1.6 đã chạy thật và **hỏng ở giai đoạn A** (mục 3). 1.6A đã được quyết làm lại (thiết kế mới: `docs/design/step_1_6a_propositions.md`, A38; tuning chốt ở A39). **Mục 1 và 2 mô tả bản CŨ và giữ lại để hiểu vì sao phải làm lại; không phải thiết kế hiện hành.** 1.7 và 1.8 mới là bản nháp, chưa có code.

## 0. Bối cảnh
- **Mục tiêu:** dựng cơ sở tri thức (KB) từ BLLĐ để trả lời câu hỏi có/không theo ngày sự việc, kèm căn cứ. Sau đó KB được cập nhật khi nạp nghị định, thông tư.
- **Mô hình:** K = (D văn bản, U đơn vị, V phiên bản, E cạnh, Δ điều khoản giao, P sổ vị từ, R quy tắc).
  - R được viết bằng s(CASP): Prolog có phủ định theo mô hình ổn định, chạy trên SWI-Prolog.
  - Câu trả lời chỉ dựa trên các quy tắc đang hiệu lực tại ngày hỏi và không bị cô lập.
- **Hai nguyên tắc:**
  1. Mọi đầu ra của LLM bị ràng buộc (trích nguyên văn, chọn trong tập đóng) và phải qua cổng kiểm bằng máy.
  2. Không có người duyệt ở giữa chuỗi.
- **Chuỗi:** 1.1 parse → 1.2 dẫn chiếu → 1.3 điều khoản giao → 1.4 loại Điều → 1.5 ngoại lệ tường minh → **1.6 sổ vị từ → 1.7 ngoại lệ ngầm → 1.8 quy tắc** → 1.9 hỏi đáp.

### Đầu vào 1.6 nhận từ các bước trước (đều làm bằng regex, không dùng LLM)
| Bước | Ra gì (BLLĐ) | Ghi chú chất lượng |
|---|---|---|
| 1.1 | 220 Điều; 881 đơn vị có chữ thuộc Điều được trích quy tắc | Số Điều khớp danh mục văn bản; số thứ tự liên tục |
| 1.2 | 245 cạnh `refers_to` (dẫn chiếu "khoản 2 Điều 18"); 0 cụm không giải được | Rà 15/11: trong 326 cụm Điều/khoản/điểm, 13 cụm không có cạnh. 8 trong số đó là dòng chỉ thị sửa đổi, cố ý bỏ. Còn khoảng 4 cụm sót thật, ví dụ D131 "Điều này" và D34.K4 "khoản 5 Điều 328" (của luật khác). Dẫn chiếu tới Chương/Mục không được nhận dạng: BLLĐ có 1 ca (D3.K1) |
| 1.4 (nhiễu) | | Mặc định "nội dung" đưa cả Điều chính sách, quản lý nhà nước vào 1.6A, gây nhiễu |
| 1.3 | 51 điều khoản giao chắc, 5 ca lỏng | Regex chưa chắc bắt hết |
| 1.4 | Nhãn theo tiêu đề Điều: 17 Điều khớp mẫu, 203 Điều mặc định "nội dung" | Mặc định cố ý, để không bỏ sót quy tắc |
| 1.5 | 66 cạnh `exception_of` (ngoại lệ "trừ trường hợp ..."), 34 nút điều kiện; 2 ca bỏ không xử lý | Nút điều kiện cắt "đến hết đoạn": 2 nút dài trên 200 ký tự, dài nhất 393 |

## 1. Bước 1.6 giai đoạn A: gạch cụm (đã chạy, kết quả hỏng)

**Nhận:**
- 881 đơn vị, chia thành 204 lô, mỗi lô một Điều.
- Mỗi đơn vị kèm ngữ cảnh: tiêu đề Điều, chữ khoản cha hoặc câu dẫn của Điều, và chữ của chính đơn vị.
- Chủ thể hay kết luận nhiều khi nằm ở tiêu đề hoặc khoản cha, nên phải đưa cả ngữ cảnh.

**LLM gạch cụm:**
- Model Opus 5.5, lời nhắc `concepts-2`.
- Mỗi cụm là một chuỗi liền, chép nguyên văn từ ngữ cảnh, gắn một trong bốn vai:
  - `chu_the`: ai;
  - `dieu_kien`: khi nào;
  - `ngoai_le`: trừ khi nào;
  - `ket_luan`: hệ quả (được, phải, cấm, hưởng).
- Kèm `params`: loại thực thể mà cụm nói tới. W người lao động, E người sử dụng lao động, C hợp đồng, J công việc, G vùng, D ngày, A số tiền.
- Lời nhắc yêu cầu **không đặt tên, không viết lại**. Có ví dụ mẫu và luật riêng cho định nghĩa: "X là Y" thì X là `ket_luan`, Y là `dieu_kien`.
- Lời nhắc KHÔNG đòi những điều sau:
  - mỗi cụm chỉ một ý;
  - không gạch câu dẫn;
  - giữ phương thức (được, phải, cấm) trong cụm kết luận.

**Máy:**
1. Đánh dấu từ báo hiệu bằng regex: nếu, khi, trường hợp, trừ, không áp dụng, phải, được, bị coi là.
2. Kiểm chặn:
   - cụm là chuỗi từ liền của ngữ cảnh;
   - vai thuộc 4 vai;
   - `params` thuộc 7 chữ.
3. Thêm cụm `ngoai_le` từ nút điều kiện của 1.5.
4. Điền `targets` cho cụm chứa dẫn chiếu đã giải ở 1.2. Những cụm này là con trỏ tới đơn vị khác, không được đặt tên.

**Kết quả:** 3061 cụm, 0 cụm hỏng cổng nguyên văn. Phân theo vai: kết luận 1287, điều kiện 888, chủ thể 840, ngoại lệ 46.

**Cổng không kiểm được nghĩa.** Nó chỉ chứng minh cụm có thật trong chữ, không chứng minh cụm là một vị từ có nghĩa.

## 2. Bước 1.6 giai đoạn B: đặt tên và tái dùng vị từ (đã chạy, kết quả hỏng theo A)
1. **Gom chữ.**
   - "Chữ" là dạng chuẩn hoá của một cụm không có `targets`. Có 1833 chữ khác nhau.
   - Cùng chữ thì máy ép cùng tên, không hỏi LLM. Đây là gộp cấp 1, và nó không nhìn ngữ cảnh.
2. **Ứng viên.**
   - Chữ khác được xét là ứng viên nếu: cùng Điều; hoặc nối với đơn vị chứa chữ bằng dẫn chiếu hay ngoại lệ; hoặc chung một âm tiết nội dung (đã bỏ 30 âm tiết phổ biến).
   - Chỉ giữ chữ đã có tên ở lượt trước và cùng `params`. Xếp theo số âm tiết chung, lấy tối đa 12.
3. **Lượt tuần tự.**
   - 76 lượt theo thứ tự Điều, mỗi lượt tối đa 30 chữ.
   - LLM là Sonnet 5.5, mỗi lượt một phiên mới. Với mỗi chữ, LLM trả `reuse: <tên ứng viên>` hoặc `new: <tên tiếng Anh>`.
   - Lời nhắc chỉ cho `reuse` khi cùng nghĩa. Gần nghĩa, rộng hơn, hẹp hơn hay trái nghĩa đều phải `new`.
   - Lý do của luật chặt này: gộp nhầm làm quy tắc áp sai chỗ, còn tách sót chỉ làm câu trả lời rơi về "chưa đủ căn cứ".
4. **Cổng máy.**
   - Mỗi chữ có đúng một mục.
   - Tên `reuse` phải nằm trong tập đã đưa và cùng `params`.
   - Tên `new` phải đúng dạng `^[a-z][a-z0-9_]{2,49}$`, không mở đầu bằng `not_`, `no_`, `non_`, và chưa có trong sổ.
5. **Sổ.**
   - Mỗi vị từ một dòng, gồm: tên, `params`, `surface` (các chữ Việt), `used_in`.
   - Có thêm `kind`: là `concept` nếu có đơn vị dùng nó làm kết luận (các đơn vị đó gọi là `anchors`), còn lại là `input` (dữ kiện người hỏi tự khai).

**Kết quả:**
- 76/76 lượt qua cổng.
- Tái dùng chỉ **55/1833 (3%)**, ra 1778 vị từ.
- 217 chữ không có ứng viên nào. 1562 chữ có ứng viên nhưng LLM vẫn chọn tên mới.

## 3. Vì sao hỏng: số đo và ví dụ thật
Số đo dùng luật thô nên có dương tính giả; đây là ước lượng, không phải độ chính xác.

| Lỗi | Số đo | Ví dụ thật |
|---|---|---|
| Câu dẫn danh sách bị gạch thành kết luận | 51 cụm, 22 vị từ | D21.K1 "phải có những nội dung chủ yếu sau đây" ra `contract_must_contain_essential_terms`; D5.K1 "có các quyền sau đây" ra `has_following_rights` |
| Một cụm chứa nhiều ý | 444 cụm (14,5%) ghép "và/hoặc" từ 10 từ trở lên; 280 cụm (9%) dài từ 25 từ | D5.K1.a "không bị phân biệt đối xử, cưỡng bức lao động, quấy rối tình dục tại nơi làm việc" (3 quyền trong 1 cụm) |
| Cụm vụn không tự đủ nghĩa | chưa đếm riêng | D5.K1.a "Làm việc" ra `right_to_work` |
| Mất phương thức (được, phải, cấm) | chưa đếm | Ví dụ mẫu của chính lời nhắc bỏ "có thể" khỏi "giao kết hợp đồng lao động bằng lời nói" |
| Chủ thể không vào được vị từ | 39/51 vị từ kết luận dùng ở từ 2 Điều trở lên có chủ thể khác nhau, mà `params` rỗng | `has_following_rights` dùng chung cho D5 (người lao động), D6 (người sử dụng lao động), D176, D203. Cùng vị từ cho nhiều chủ thể là được, nếu chủ thể là đối số. Lỗi ở đây là chủ thể bị mất (`params` rỗng), cộng với việc cụm chỉ là câu dẫn. Máy gộp vì chữ giống hệt nhau |
| Dẫn chiếu mờ bị gạch thành cụm | 105 cụm có "theo quy định của pháp luật", "quy định tại", "Bộ luật này" mà không có `targets`; 93 cụm nằm ở đơn vị không có cạnh dẫn chiếu nào | Phần lớn là "theo quy định của pháp luật" (D5.K1.c, D6.K1.b): không có đích, nên 1.2 không sót. 0 ca 1.2 có cạnh mà 1.6 cắt lệch |
| Cụm thiếu `params` (mà `params` là bộ lọc ứng viên cứng) | 1105 trên 3021 cụm LLM (36%) | |

**Hậu quả cho các bước sau (quan trọng nhất):**
- **Xích quy tắc gần như không có.** Chỉ 11/704 vị từ điều kiện hay ngoại lệ trùng một vị từ kết luận ở Điều khác.
- **1.7 gần như không có gì để xét.** Toàn bộ ứng viên chỉ là 108 cặp đơn vị khác Điều chung một vị từ điều kiện hay ngoại lệ, đến từ 44 vị từ.
- **Ngoại lệ ngầm bị mất âm thầm.** Thiếu cạnh ngoại lệ thì 1.9 trả "kết luận được" thay vì "bị bác", và không cổng nào báo.

**Gốc lỗi:**
1. **Lời nhắc 1.6A gạch theo câu chữ, không theo mệnh đề.** Một cụm 25 từ chỉ tái dùng được nếu ở chỗ khác có một cụm 25 từ y hệt. Giả thuyết (chưa đo): với cụm như hiện nay, sửa riêng 1.6B không nâng tái dùng được nhiều.
2. **(1.6B) Luật "cùng chữ thì cùng tên" bỏ qua chủ thể** khi cụm không có `params`.
3. **(1.6B) Ứng viên xếp theo âm tiết chung, cắt ở 12**, cộng luật "gần nghĩa thì tên mới", làm giảm tái dùng thêm. Chưa ai đo bao nhiêu trong 1562 chữ "có ứng viên mà chọn tên mới" thực ra cùng nghĩa. Vì vậy làm lại 1.6A mà giữ nguyên 1.6B thì tái dùng vẫn có thể thấp.
4. **Khi nghiệm thu chỉ kiểm hình dạng**, không đo độ kết nối giữa các Điều. Đây là lỗi quy trình nghiệm thu.

## 4. Nguyên tắc vị từ pháp luật dùng cho bản làm lại (đã dùng làm căn cứ cho bản làm lại, A38)
Nguyên tắc 4 đảo quyết định cũ A31. A31 để phủ định và phương thức ngoài bản tối thiểu.
1. **Nguyên tử:** một cụm là một mệnh đề. "A, B, C" thành ba cụm.
2. **Tự đủ nghĩa:** không gạch câu dẫn ("sau đây:"). Câu dẫn chỉ trao chủ thể và phương thức cho các mục con.
3. **Chủ thể là tham số, không nằm trong tên.** "có quyền ..." của người lao động và của người sử dụng lao động là cùng vị từ, khác đối số, hoặc khác vị từ nếu nội dung khác.
4. **Phương thức và cực tách riêng:** được, phải, cấm, không được là một trường riêng, không trộn vào chữ.
5. **Dùng lại được:** cùng một sự kiện viết bằng chữ khác nhau phải ra một vị từ. Cùng chữ mà khác nghĩa phải ra hai vị từ.
6. **Dẫn chiếu là con trỏ:** cụm chứa "quy định tại ..." đã giải được thì không đặt tên.

**Chưa quyết:**
- (a) Giữ ràng buộc "chép nguyên văn, chuỗi liền"? Nó làm cổng chặt nhưng không cho tách "A, B và C của X" thành ba mệnh đề đầy đủ. Thay bằng "trích nguyên văn + chuẩn hoá có kiểm" thì phải thiết kế cổng mới.
- (b) Đặt tên ở cùng bước gạch, hay vẫn tách A và B.
- (c) Tiêu chí nghiệm thu bằng số trước khi chạy cả 204 lô. Đề xuất: thử cả 1.6A và 1.6B trên 5 đến 10 Điều có liên quan với nhau. Thước đo chính là độ kết nối khác Điều: số xích điều kiện-kết luận và số cặp ứng viên cho 1.7. Đo thêm tỉ lệ cụm nguyên tử và tỉ lệ tái dùng.
- (d) Có dùng một LLM khác chấm mẫu không. Quyết định cũ A14 nói "LLM kiểm LLM không chứng minh đúng sai", nên chỉ dùng như ước lượng.

## 5. Bước 1.7 ngoại lệ ngầm (bản nháp, chưa code)
- **Nhận:** sổ vị từ 1.6, 66 cạnh `exception_of` của 1.5, chữ đơn vị.
- **Cách làm:**
  1. **Máy dựng cặp:** hai đơn vị cùng dùng một vị từ `concept` (đơn vị neo cũng tính). Bỏ cặp đã có cạnh ở 1.5.
  2. **Máy đếm cặp:** vượt ngân sách lượt LLM thì dừng và báo.
  3. **LLM xét từng cặp, có ngữ cảnh như 1.6.** Trả `a_exception_of_b`, `b_exception_of_a` hoặc `none`, kèm câu bằng chứng nguyên văn.
  4. **Cổng:**
     - giá trị hợp lệ;
     - bằng chứng là chuỗi con của ngữ cảnh;
     - hai đầu tồn tại;
     - không trùng cạnh 1.5;
     - không tạo vòng (cạnh trong vòng bị loại và liệt kê).
  5. **Cạnh được nhận mang cờ `llm_proposed`.** Bật hay tắt cạnh này quyết ở 1.8 và 1.9.
- **Ra:** `pairs` (mọi cặp đã hỏi), `edges`, `rejected` (kèm lý do).
- **Phụ thuộc:** 1.7 chỉ tốt bằng mức tái dùng của 1.6. Tái dùng sót thì cặp sót; đây chính là chỗ đang hỏng.
- **Hoãn:**
  - `narrower_than` (vị từ hẹp hơn), dù đây là nguồn ngoại lệ ngầm điển hình;
  - phân biệt hai dạng ngoại lệ "kết luận ngược" (rebut) và "chỉ loại trừ" (undercut).
- **Chưa có:** đáp án chuẩn để đo độ bỏ sót.

## 6. Bước 1.8 quy tắc s(CASP) (bản nháp, chưa code)
- **Nhận:** 881 đơn vị, sổ vị từ, cạnh ngoại lệ (1.5 và 1.7).
- **Cách làm:**
  1. **Máy tính vị từ được phép cho mỗi Điều:** vị từ của chính đơn vị, cộng vị từ của đơn vị nối qua cùng khái niệm.
  2. **LLM viết 0 đến nhiều quy tắc cho mỗi đơn vị, lô theo Điều.** Chỉ dùng vị từ được phép; thiếu vị từ thì gắn cờ, không tự đặt tên.
     - Ví dụ: `needs_work_permit(W) :- foreign_worker(W), not work_permit_exempt(W).`
  3. **Ngoại lệ biên dịch thành chặn:** `blocked(r,X) :- applies(e,X), not blocked(e,X).`
     - Đã thử trên s(CASP) với ngoại lệ lồng ba tầng: đúng cả 4 ca thử.
  4. **Bộ quét 4 loại:**
     - quy tắc không bao giờ kích hoạt;
     - quy tắc trùng;
     - vòng chặn;
     - cặp kết luận ngược không có quan hệ chặn.
  5. **Tự sửa tối đa 2 vòng.** Không đạt thì cô lập quy tắc.
- **Cổng:**
  - biên dịch được;
  - chỉ dùng vị từ được phép, đúng số tham số;
  - quét sạch.

  Cổng **không chứng minh được quy tắc dịch đúng nghĩa luật.**
- **Đã thấy khi thử s(CASP):**
  - Vị từ không có quy tắc nào bị coi là sai, và chỉ có một cảnh báo. Đặt dưới `not`, nó thành đúng, nên quy tắc gốc không bao giờ bị chặn. Đây đúng là hậu quả khi 1.6 tái dùng sót.
  - Biến không khớp giữa hai đầu cạnh ngoại lệ cho kết quả sai mà không báo lỗi. Cần cổng "biến của ngoại lệ nằm trong biến của quy tắc gốc".
- **Còn mở:**
  - (a) 43/66 cạnh của 1.5 bắt đầu từ nút điều kiện chứ không từ đơn vị. Cụ thể: 28 nút không có đơn vị đích, 7 nút "các bên thỏa thuận khác", 2 nút "pháp luật có quy định khác". Chưa quyết cách biên dịch.
  - (b) Cách biên dịch ngoại lệ lồng nhau trên dữ liệu thật. Đây là đóng góp chính của đồ án.
  - (c) "Bị bác" cần kết luận phủ định, mà 1.6 chưa có phủ định.
  - (d) Ai gán dạng rebut hay undercut.
  - (e) Đề cương đồ án ghi "vị từ đầu vào do người thực hiện biên soạn", còn bản cài để máy suy ra `kind`.

## 7. Câu hỏi xin người đánh giá
1. Bộ nguyên tắc ở mục 4 có đúng và đủ cho vị từ pháp luật không? Còn thiếu gì, ví dụ thời hạn, mức tiền, quan hệ giữa các bên?
2. Có nên bỏ ràng buộc "chuỗi liền nguyên văn" để tách mệnh đề nguyên tử không? Nếu bỏ, cổng thay thế nên là gì?
3. Gộp và tái dùng nên làm bằng gì: LLM chọn trong ứng viên, phân cụm theo nghĩa, hay một sổ vị từ đầu vào soạn tay?
4. 1.7 dựa hoàn toàn vào tái dùng của 1.6. Có cách sinh cặp ứng viên nào không phụ thuộc tên vị từ không, ví dụ cùng chủ thể và cùng đối tượng?
5. Thiết kế "chặn" ở 1.8 có xử lý được 43 cạnh xuất phát từ nút điều kiện và ngoại lệ "thỏa thuận khác" không?
