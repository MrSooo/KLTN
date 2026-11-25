# Tổng hợp công việc đã làm: xây dựng đồ thị tri thức cho phần Thừa kế, Bộ luật Dân sự 2015

Cập nhật: 25/10/2026. Nhánh code: `sua-theo-review`, chưa gộp vào `main`.

---

## 0. Đọc nhanh trong 1 phút

- **Đề tài** (theo `DRAFT_Proposal_v5.docx`): hệ hỏi đáp pháp luật tiếng Việt kết hợp LLM với suy luận ký hiệu. LLM chỉ lo phần hiểu ngôn ngữ, còn việc suy ra kết luận do bộ giải logic s(CASP) làm. Hệ cần trả lời đúng cả khi luật có **ngoại lệ lồng nhau**.
- **Phần đã làm**: bước nền móng, tức **tự động xây đồ thị tri thức (KG)** từ văn bản luật. Đồ thị lưu từng Điều, Khoản, Điểm và các liên kết giữa chúng: chứa nhau, dẫn chiếu nhau, là ngoại lệ của nhau, bị văn bản nào sửa. Đồ thị cập nhật được khi có văn bản sửa đổi, và tự kiểm tra lỗi.
- **Dữ liệu thử**: Bộ luật Dân sự 2015, phần Thừa kế, Điều 609 đến Điều 662.
- **Kết quả**: đồ thị có **225 nút và 481 cạnh**, qua đủ 7 nhóm kiểm tra tự động. Có **266 test**, tất cả đều đạt.
- **Ngoài phần xây đồ thị**, project đã có thêm:
  - một đợt **tự rà soát** (review), tìm ra 22 vấn đề và sửa phần lớn;
  - một **tầng dùng LLM** để đọc các câu sửa đổi phức tạp, đã code và test xong nhưng **chưa chạy với API thật**.
- **Chưa làm** (các bước sau KG trong đề cương): LLM phân loại quan hệ, sổ khái niệm, trích quy tắc, suy luận s(CASP), bộ tình huống đánh giá.

---

## 1. Bức tranh tổng thể: project nằm ở đâu trong đề cương

Đề cương có 5 nội dung. Project hiện làm phần **xây đồ thị** của Nội dung 1 và phần **kiểm tra ở mức đồ thị** của Nội dung 2.

| Nội dung trong đề cương | Đã làm gì |
|---|---|
| 1. Xây cơ sở tri thức dạng đồ thị, quản lý liên kết | **Phần lớn phần đồ thị**: tách văn bản, mã định danh, liên kết cấu trúc, dẫn chiếu, ngoại lệ tường minh, phiên bản khi sửa đổi. Chưa có: LLM phân loại quan hệ, sổ khái niệm, trích quy tắc |
| 2. Kiểm tra đồ thị, kiểm soát chồng chéo | **Phần kiểm ở mức đồ thị**: trùng lặp, liên kết bị đứt, vòng ngoại lệ, cấu trúc cha con. Chưa có: kiểm ở mức quy tắc, LLM tự sửa |
| 3. Suy luận s(CASP), hỏi đáp có giải thích | Chưa làm |
| 4. Bộ dữ liệu đánh giá | Mới có khung để chấm điểm, cộng một bộ câu sửa đổi thật để thử phần cập nhật. Chưa có bộ tình huống |
| 5. Thực nghiệm | Chưa làm |

Có thể hình dung thế này: đồ thị là "bộ nhớ có cấu trúc" của hệ thống. Các bước sau (trích quy tắc, suy luận, hỏi đáp) đều đọc từ bộ nhớ này, nên nó phải đúng và kiểm được.

---

## 2. Vài khái niệm cần nắm trước

**Điều, Khoản, Điểm.** Văn bản luật chia theo cấp: Điều chứa các Khoản (1, 2, 3...), Khoản chứa các Điểm (a, b, c...). Phía trên Điều còn có Chương.

**Mã định danh.** Mỗi đơn vị có một mã cố định, ghép từ số hiệu:
- `BLDS2015.D621` là Điều 621;
- `BLDS2015.D621.K1` là khoản 1 Điều 621;
- `BLDS2015.D621.K1.a` là điểm a khoản 1 Điều 621;
- `BLDS2015.CXXII` là Chương XXII.

Chữ "đ" trong mã viết thành "dd", ví dụ `...K1.dd`.

**Đồ thị tri thức.** Gồm **nút** (các đơn vị luật) và **cạnh** (quan hệ giữa hai nút). Mỗi cạnh lưu dưới dạng **bộ ba** *(nguồn, quan hệ, đích)*. Ví dụ `(D621.K1, part_of, D621)` nghĩa là "khoản 1 thuộc Điều 621".

**Các loại cạnh trong project:**

| Cạnh | Nghĩa | Sinh ở bước |
|---|---|---|
| `contains` / `part_of` | A chứa B / B thuộc A (cấu trúc) | A2, A7 |
| `refers_to` | A dẫn chiếu tới B ("theo quy định tại Điều 652") | A2 |
| `exception_of` | A là ngoại lệ của B (A đúng thì B không được áp dụng) | A3, A6 |
| `same_text_as` | Hai đơn vị có chữ giống hệt nhau | A7 |
| `amends` / `replaces` / `repeals` | Văn bản X sửa đổi / thay thế / bãi bỏ đơn vị Y | A4, A7 |

**Nút điều kiện.** Câu "..., trừ trường hợp có thỏa thuận khác" có phần ngoại lệ là một *điều kiện*, chứ không phải một Khoản. Project tạo một nút riêng cho điều kiện đó (gọi là nút điều kiện), rồi nối nó vào quy tắc bị ngoại trừ.

**Phiên bản.** Khi một Khoản bị sửa, bản cũ không bị xoá. Bản cũ được ghi ngày hết hiệu lực, và một bản mới (phiên bản 2) được tạo. Nhờ vậy xem được luật **tại bất kỳ ngày nào**.

**Fail-closed và fail-open.** Đây là khái niệm quan trọng nhất trong đợt rà soát.
- *Fail-closed* (dừng và báo): gặp chỗ không hiểu thì dừng lại, báo lỗi rõ ràng. Chấp nhận được.
- *Fail-open* (im lặng làm sai): chạy xong, không báo gì, nhưng kết quả sai hoặc thiếu. **Nguy hiểm**, vì người dùng tin kết quả.

Nguyên tắc của project: **thà dừng còn hơn làm sai mà không biết.**

**Regex.** Mẫu tìm chữ, ví dụ mẫu "trừ trường hợp + phần còn lại của câu". Các bước A1 đến A7 chủ yếu dùng regex. Ưu điểm là chạy đúng y hệt nhau mỗi lần và kiểm được; nhược điểm là chỉ hiểu những mẫu đã viết sẵn.

**LLM.** Mô hình ngôn ngữ lớn, ở đây là Claude. Dùng cho chỗ cần hiểu câu chữ linh hoạt. Trong project, LLM chỉ được **đề xuất**; mọi đề xuất đều bị máy kiểm lại trước khi dùng.

---

## 3. Dữ liệu đầu vào

| File | Nội dung |
|---|---|
| `data/raw/blds2015_p4.md` | Phần Thừa kế BLDS 2015, Điều 609 đến 662, dạng Markdown. Gồm 4 Chương (XXI đến XXIV), 54 Điều, 115 Khoản, 46 Điểm |
| `data/sample/blds2015_5dieu.md` | Bản thu nhỏ 5 Điều (621, 626, 644, 650, 651), dùng để thử nhanh |
| `data/dev_amend/dev01…dev08.md` | 8 văn bản sửa đổi **tự soạn** để thử phần cập nhật (vì BLDS 2015 chưa có văn bản sửa đổi thật) |
| `data/ext_amend/` | 19 câu sửa đổi **thật**, lấy nguyên văn từ Luật 85/2025/QH15 (Công báo), đổi số hiệu sang BLDS. Dùng để thử phần cập nhật trên câu chữ thật |

8 văn bản dev thử 8 kiểu sửa đổi khác nhau:

| File | Kiểu sửa |
|---|---|
| dev01 | Bãi bỏ khoản 2 Điều 621 |
| dev02 | Sửa khoản 1 Điều 621 (hiệu lực 01/7/2027) |
| dev03 | Thay toàn bộ Điều 626 (có khoản bị bỏ, có khoản mới 2a) |
| dev04 | Bổ sung Điều 621a, khoản 3 Điều 621, điểm đ khoản 1 Điều 650 |
| dev05 | Bãi bỏ cùng lúc nhiều đơn vị (khoản 2 Điều 621, điểm a khoản 1 Điều 650, Điều 626, Điều 651) |
| dev06 | Sửa, bỏ, thêm **cụm từ** bên trong câu |
| dev07 | Đổi tên Điều 621 và Điều 626 |
| dev08 | Thay thế cả Bộ luật |

Trừ dev02, các văn bản đều có hiệu lực từ 01/01/2027.

---

## 4. Quy trình 7 bước (A1 đến A7)

```
văn bản luật (.md)
   │
   A1  tách thành Điều / Khoản / Điểm, gán mã ─────────────► a1_triples
   │
   A2  cạnh cấu trúc (chứa / thuộc) + cạnh dẫn chiếu ──────► a2_edges, a2_refs
   │
   A3  ngoại lệ tường minh (2 mẫu câu) ────────────────────► a3_exceptions
   │
   A6  ngoại lệ chung "trừ trường hợp ..." ─────────────────► a6_conditions, a6_exceptions
   │
   A5  kiểm tra các file trên (trùng, cha con, phiên bản)
   │
   A7  gộp tất cả thành MỘT đồ thị + kiểm tra ──────────────► a7_..._nodes, a7_..._edges

   A4  (khi có văn bản sửa đổi) tạo phiên bản mới, cập nhật cạnh ─► a4_..._versions, edge_changes
       rồi A7 dựng lại đồ thị TẠI MỘT NGÀY bất kỳ
```

Mọi file kết quả nằm trong `data/processed/`, mọi báo cáo nằm trong `docs/`. Mỗi bước tự kiểm kết quả của mình. Có lỗi thì bước đó dừng và **không ghi file**, để bước sau không nhận dữ liệu hỏng.

### A1: Tách văn bản (`src/a1_parse.py`)

- **Làm gì:** đọc từng dòng, nhận ra đâu là Chương, Điều, Khoản, Điểm hay đoạn chữ thường, rồi gán mã định danh.
- **Tự kiểm:**
  - Số Điều phải đúng dãy mong đợi (609 đến 662, không thiếu, không thừa).
  - Khoản phải liên tiếp 1, 2, 3; Điểm phải liên tiếp a, b, c.
  - Dòng nào có dấu hiệu sai định dạng đều bị ghi lại, không bỏ qua im lặng.
- **Kết quả trên p4:** 215 đơn vị (54 Điều, 115 Khoản, 46 Điểm), cộng 4 Chương, tổng 1.173 bộ ba.

### A2: Cạnh cấu trúc và dẫn chiếu (`src/a2_edges.py`)

- **Cạnh cấu trúc:** mỗi Khoản thuộc một Điều, mỗi Điểm thuộc một Khoản, mỗi Điều thuộc một Chương. Mỗi quan hệ cha con sinh 2 cạnh (`contains` và `part_of`). Kết quả: **430 cạnh**.
- **Cạnh dẫn chiếu:** tìm các cụm như "khoản 1 và khoản 3 Điều 616 của Bộ luật này", "khoản 1 Điều này", rồi nối tới đúng đích.
  - Kết quả: **25 cạnh `refers_to`**.
  - Có 2 dẫn chiếu trỏ ra ngoài phần đã nạp (khoản 2 Điều 71, Điều 236), được ghi lại là "chưa giải được" thay vì nối bừa.
- **Tự kiểm:** đếm lại độc lập thì 41/41 lần nhắc tới Điều/khoản/điểm đều nằm trong các cụm đã nhận.

### A3: Ngoại lệ tường minh (`src/a3_exceptions.py`)

Chỉ dùng 2 mẫu câu rất chắc chắn:
1. **"... không áp dụng ..."** đứng ngay sau một cụm dẫn chiếu. Ví dụ "Quy định tại khoản 1 Điều này không áp dụng đối với ..." sinh cạnh: khoản 2 Điều 644 là ngoại lệ của khoản 1.
2. **"..., trừ những người sau đây:"** kèm danh sách. Mỗi mục trong danh sách là ngoại lệ của câu dẫn. Ví dụ Điều 632 có 3 khoản là ngoại lệ.

Kết quả: **4 cạnh `exception_of`**. Câu nào có chữ "trừ" mà không thuộc 2 mẫu này thì bị liệt kê là "chưa xử lý", để bước A6 xử lý.

### A6: Ngoại lệ chung "trừ trường hợp" (`src/a6_general_exceptions.py`)

- **Làm gì:** câu "Quy tắc X, **trừ trường hợp** Y" được tách: Y thành một **nút điều kiện**, rồi nối Y là ngoại lệ của đơn vị chứa X.
- **Gộp:** các câu có cùng điều kiện dùng chung một nút. Ví dụ 5 câu cùng "có thỏa thuận khác" dùng chung 1 nút.
- **Phân loại nút điều kiện** (thêm trong đợt sửa):
  - `tuy_nghi`: "có thỏa thuận khác", tức các bên được tự thoả thuận;
  - `dan_chieu_mo`: "pháp luật có quy định khác", tức trỏ tới văn bản chưa rõ;
  - `cu_the`: các điều kiện khác.
- **Ngoại lệ có dẫn chiếu:** nếu Y nhắc tới một đơn vị khác thì đơn vị đó cũng được nối là ngoại lệ. Ví dụ "trừ trường hợp thừa kế thế vị theo quy định tại Điều 652" sinh thêm cạnh Điều 652 là ngoại lệ của Điều 619.
- **Kết quả:** 5 nút điều kiện, **10 cạnh `exception_of`** (9 từ nút điều kiện, 1 từ Điều 652).

### A4: Cập nhật khi có văn bản sửa đổi (`src/a4_versions.py`)

Đây là bước phức tạp nhất, khoảng 1.600 dòng code.

1. **Đọc văn bản sửa đổi:** nhận ra từng chỉ thị (bãi bỏ, sửa đổi, bổ sung, thay thế, đổi tên, sửa cụm từ) và ngày hiệu lực. Hiện nhận được 6 nhóm mẫu câu chuẩn.
2. **Tạo phiên bản:**
   - đơn vị bị sửa: đóng bản cũ, mở bản mới;
   - đơn vị bị bãi bỏ: đóng lại, **không xoá**;
   - đơn vị mới: tạo phiên bản 1.
3. **Cập nhật cạnh:** chỉ tính lại dẫn chiếu và ngoại lệ của những đơn vị có chữ thay đổi, không dựng lại cả đồ thị.
4. **Báo cạnh đứt:** nếu một đơn vị còn hiệu lực đang dẫn chiếu tới một đơn vị vừa bị bãi bỏ, cạnh đó được gắn cờ. Ví dụ dev05 bãi bỏ Điều 651, mà Điều 653 vẫn dẫn chiếu tới Điều 651.
5. **Tập ảnh hưởng:** liệt kê các đơn vị cần xem lại vì liên quan tới chỗ bị sửa.
6. **Xuất bản luật tại một ngày:** in lại bộ luật đúng như nó có hiệu lực vào ngày đó.

Ngày hiệu lực của văn bản gốc là 01/01/2017. Văn bản sửa đổi có hiệu lực không sau ngày đó sẽ bị từ chối.

**Tự kiểm:** có hơn 25 mã lỗi, mỗi mã cho một tình huống. Ví dụ `E_TARGET` (sửa một đơn vị không còn tồn tại), `E_OVERLAP` (hai chỉ thị cùng sửa một chỗ), `E_UNKNOWN_LINE` (gặp câu không hiểu). Gặp lỗi là cả văn bản không được áp, không có chuyện áp một nửa.

### A5: Kiểm tra độc lập (`src/a5_checks.py`)

A5 đọc thẳng các file kết quả và kiểm lại, **không dùng lại code của bước trước**, để lỗi không bị che. Có 4 nhóm kiểm:
1. **Mã không trùng:** mỗi đơn vị có đúng một mã, số đơn vị khớp số đếm độc lập.
2. **Cha con:** mỗi Khoản/Điểm có đúng một cha, đúng cấp; mỗi Điều thuộc đúng một Chương.
3. **Cạnh không trùng:** không có bộ ba lặp giữa các file.
4. **Phiên bản** (khi có A4): phiên bản liên tiếp 1, 2, 3; khoảng hiệu lực không chồng nhau; không đơn vị nào bị mất; phiên bản 1 giữ đúng nội dung gốc; ngày tháng hợp lệ.

Kết quả trên p4: **tất cả đạt**.

### A7: Gộp thành một đồ thị (`src/a7_graph.py`)

- **Gộp** kết quả của A1, A2, A3, A6 thành một đồ thị.
- **Thêm:**
  - nút **văn bản** BLDS 2015, với số hiệu 91/2015/QH13, ngày ban hành 24/11/2015, ngày hiệu lực 01/01/2017;
  - cạnh nối văn bản với từng Chương, để toàn bộ thành **một cây duy nhất**: văn bản, Chương, Điều, Khoản, Điểm.
- **Trùng chữ:** đơn vị có chữ giống hệt một đơn vị trước nó được gắn nhãn `same_text` và nối cạnh `same_text_as`. Không gộp nút, vì mỗi đơn vị là một vị trí pháp lý riêng.
- **Chế độ theo ngày:** đọc kết quả A4 rồi dựng đồ thị đúng tại một ngày.
  - Đơn vị đã hết hiệu lực không còn trong đồ thị.
  - Thêm nút cho văn bản sửa đổi, và cạnh `amends` / `replaces` / `repeals`.
  - Cạnh tới đơn vị đã bị bãi bỏ được giữ với nhãn `historical` (lịch sử).
- **7 nhóm kiểm (7a đến 7g):**
  - 7a: mã nút không trùng;
  - 7b: mỗi cạnh có đủ hai đầu;
  - 7c: không có cạnh lặp;
  - 7d: nhãn trùng chữ gắn đúng;
  - 7e: cây cha con đúng;
  - 7f: số lượng khớp số đếm độc lập;
  - 7g: không có **vòng ngoại lệ** (A là ngoại lệ của B và B lại là ngoại lệ của A, vì như vậy là mâu thuẫn).

---

## 5. Kết quả: đồ thị hiện tại

### Đồ thị gốc (luật như ban hành)

| Loại nút | Số lượng |
|---|---|
| Văn bản (BLDS 2015) | 1 |
| Chương | 4 |
| Điều | 54 |
| Khoản | 115 |
| Điểm | 46 |
| Nút điều kiện (từ "trừ trường hợp") | 5 |
| **Tổng** | **225** |

| Loại cạnh | Số lượng | Ghi chú |
|---|---|---|
| `contains` + `part_of` | 219 + 219 | Cây văn bản > Chương > Điều > Khoản > Điểm |
| `refers_to` | 25 | Dẫn chiếu tường minh |
| `exception_of` | 14 | 4 từ A3, 10 từ A6 |
| `same_text_as` | 4 | 4 cặp đơn vị trùng chữ |
| **Tổng** | **481** | 7/7 nhóm kiểm đạt |

### Ví dụ đồ thị theo ngày (nạp dev05, xem tại 01/01/2027)

- 15 đơn vị bị bãi bỏ biến mất khỏi đồ thị; còn 200 đơn vị đang hiệu lực.
- Có 1 cạnh dẫn chiếu bị đứt được gắn cờ: Điều 653 vẫn dẫn chiếu tới Điều 651, mà Điều 651 đã bị bãi bỏ.
- Có 4 cạnh `repeals` từ văn bản dev05, mang nhãn `historical` vì đích đã hết hiệu lực.
- Nhờ vậy, câu hỏi "văn bản nào đã sửa Điều X?" trả lời được ngay trên đồ thị.

### Nhận xét trung thực về độ giàu của đồ thị

Phần lớn cạnh là cạnh cấu trúc. Cạnh mang nghĩa (dẫn chiếu, ngoại lệ, trùng chữ) chỉ có 43. Nếu chỉ nhìn các cạnh mang nghĩa thì đồ thị rời thành 187 cụm. Lý do là hiện chỉ bắt được quan hệ **viết tường minh** bằng từ khoá. Theo đề cương, quan hệ **ngầm** sẽ do LLM đề xuất ở bước sau.

---

## 6. Đợt tự rà soát và sửa lỗi

### 6.1. Vì sao rà soát

Sau khi xong A1 đến A7, mọi test đều đạt, và lượt báo cáo trước ghi "mọi mục đã đạt". Đợt rà soát được làm theo hướng **cố tìm chỗ sai**:
- đếm lại số liệu bằng cách khác, không dùng số của chính chương trình;
- thử đầu vào chương trình chưa từng gặp;
- tách riêng lỗi "dừng và báo" với lỗi "im lặng làm sai".

Kết quả là **22 vấn đề** (F-01 đến F-22). Đánh giá lại 8 yêu cầu: lúc đầu chỉ 2 đạt và 5 đạt một phần. Lượt báo cáo trước đã **lạc quan quá mức**. Chi tiết nằm trong `review_a1_a7_findings.md`.

### 6.2. Đã sửa gì, giải thích dễ hiểu

**Pha 1: chặn các lỗi "im lặng làm sai".** Đây là ưu tiên số một.

| Vấn đề | Trước khi sửa | Sau khi sửa |
|---|---|---|
| F-03: câu bị động "Khoản 2 Điều 5 **được bãi bỏ**." | A4 coi là chữ thường, bỏ qua; văn bản "nạp thành công" mà không sửa gì | Báo lỗi "câu lạ". Văn bản không có chỉ thị nào cũng báo lỗi |
| F-01: "Điều 5 **của Luật Đất đai**" | Nối nhầm tới Điều 5 của chính BLDS | Ghi là dẫn chiếu ra văn bản khác, không nối |
| F-02: "từ Điều 5 đến Điều 8", "các điều 5, 6 và 7", "Điều 5a" | Thiếu cạnh mà không báo (chỉ ra Điều 5 và 8) | Dừng và báo "chưa có quy tắc" |
| F-04: câu bắt đầu "Trừ trường hợp X, quy tắc Y" | Gộp cả quy tắc Y vào nút điều kiện | Cắt điều kiện ở dấu phẩy đầu tiên |
| F-05: "không **được** áp dụng" | Không hiện ở đâu cả | Được liệt kê vào danh sách "chưa xử lý" |

Với dữ liệu BLDS hiện có, pha này **không làm thay đổi kết quả nào**, vì phần Thừa kế không có các câu kiểu đó. Pha này phòng lỗi khi gặp văn bản khác.

**Pha 2: bổ sung phần còn thiếu so với yêu cầu.**

| Vấn đề | Đã làm |
|---|---|
| F-12: chưa kiểm vòng ngoại lệ | Thêm kiểm 7g. Vòng dẫn chiếu qua lại thì hợp lệ, chỉ ghi lại |
| F-10, F-11: ngoại lệ không nối tới đơn vị mang ngoại lệ; nút "có thỏa thuận khác" tạo đường nối giả giữa các Điều không liên quan | Thêm cạnh Điều 652 là ngoại lệ của Điều 619; phân loại nút điều kiện; báo cáo số cụm khi bỏ các nút chung chung |
| F-08: văn bản gốc không có ngày hiệu lực | Ghi ngày 01/01/2017 và số hiệu; chặn văn bản sửa đổi có ngày sai |
| F-07: cạnh sửa đổi không nằm trong đồ thị | Đồ thị theo ngày có nút văn bản sửa đổi và cạnh `amends` / `replaces` / `repeals` |
| F-09: không có Chương; 54 Điều là 54 cây rời | Thêm 4 Chương (bổ sung dòng tiêu đề Chương XXI còn thiếu trong file gốc), thành một cây duy nhất; Điều mới chèn vào tự thuộc Chương của Điều đứng trước |

**Pha 3: định hướng và độ tin cậy.**

| Vấn đề | Đã làm |
|---|---|
| F-06: nhãn `duplicate` dễ hiểu nhầm là dư thừa | Đổi thành `same_text` (trùng chữ). 4 cặp trùng là cố ý về mặt pháp lý. Khử trùng lặp đúng nghĩa sẽ làm ở sổ khái niệm |
| F-17: chưa đo được độ chính xác thật | Có khung chấm điểm: mẫu 11 Điều chọn theo quy tắc cố định, script tính precision/recall. **Chờ người gán đáp án** |
| F-15, F-16: A4 chỉ được thử trên văn bản tự soạn | Bộ thử 19 câu thật (Luật 85/2025/QH15); thêm tầng LLM (xem mục 7) |

### 6.3. Đánh giá lại sau khi sửa

- **Phân cấp cấu trúc:** từ "đạt tối thiểu" lên **"đạt"**.
- **Dẫn chiếu, ngoại lệ, cập nhật:** vẫn **"đạt một phần"**. Không còn lỗi im lặng, nhưng phạm vi câu chữ hiểu được vẫn hẹp, và chưa bắt được quan hệ ngầm.

---

## 7. Tầng LLM cho phần cập nhật (A4)

### Vấn đề

A4 hiểu văn bản sửa đổi bằng các mẫu câu viết sẵn. Văn bản thật có nhiều cách viết, ví dụ:
- "Sửa đổi, bổ sung **khoản 3 và khoản 4** Điều 53 như sau:";
- "Sửa đổi, bổ sung **một số khoản của Điều 194** như sau:", kèm các ý con a), b).

Nếu cứ thêm mẫu thì không bao giờ đủ, vì cách viết là tổ hợp của nhiều thành phần. Bạn đã chốt **hướng C**: dùng LLM, nhưng có kiểm.

### Cách làm

1. **Câu A4 đã hiểu:** xử lý như cũ, không gọi LLM.
2. **Câu A4 không hiểu:** cả đoạn chỉ thị được gửi cho **Claude Sonnet 5.5**. LLM trả lời bằng JSON theo khuôn cố định, liệt kê từng chỉ thị đơn giản.
3. **Máy kiểm đề xuất của LLM:**
   - dựng lại thành câu chuẩn và cho chạy qua đúng bộ đọc cũ của A4;
   - **V1, đủ số hiệu:** mọi Điều/khoản/điểm có trong câu gốc phải có trong kết quả, và ngược lại;
   - **V2, đúng nguyên văn nội dung:** nội dung mới phải chép đúng từng chữ trong ngoặc kép của văn bản gốc. LLM chỉ được cắt ra, không được viết lại;
   - **V3, đúng nguyên văn cụm từ:** cụm từ cũ/mới phải đúng là cụm có trong câu.
4. **Sai thì sửa:** gửi lỗi lại cho LLM, tối đa 2 lần sửa. Vẫn sai thì **không áp gì** và báo lỗi.
5. **Lưu kết quả:** mỗi lần gọi LLM được lưu vào file. Chạy lại cho kết quả y hệt và không tốn tiền.

### Trạng thái

- **Đã có:** code và test (dùng LLM giả). Bộ thử 19 câu thật khi **chưa bật LLM**: 9 câu A4 tự hiểu đúng, 10 câu dừng có báo lỗi, **0 câu làm sai**.
- **Chưa làm:** chạy với API thật. Việc này cần API key; chi phí ước tính dưới 15 nghìn đồng cho 19 câu. Bạn đã chọn để sau.

---

## 8. Kiểm thử: làm sao biết code đúng

- **266 test**, chia trong 10 file `src/test_*.py`. Mỗi bước A1 đến A7 có bộ test riêng, cộng test cho tầng LLM và cho 2 bộ đánh giá.
- `src/run_all.py` chạy lại **toàn bộ** pipeline trên mọi dữ liệu, rồi chạy hết test. Sau mỗi lần sửa, chỉ được phép đổi đúng những file kết quả dự kiến; file nào đổi ngoài dự kiến là dấu hiệu lỗi.
- Lịch sử: 4 commit ban đầu (A1 đến A7), cộng 15 commit sửa theo rà soát. Mỗi bước sửa là một commit riêng, dễ xem lại.

**Giới hạn của test (nên nói thẳng với thầy):** test cho thấy *code làm đúng điều người viết nghĩ*. Test không chứng minh *người viết nghĩ đúng*, vì 8 văn bản dev và các con số kỳ vọng đều do cùng người làm code soạn. Để có số đo khách quan, cần:
1. người khác gán đáp án cho 11 Điều mẫu (khung đã sẵn);
2. bộ văn bản sửa đổi giả định do học viên hỗ trợ soạn, như đề cương đã ghi.

---

## 9. Giới hạn và việc chưa làm

**Giới hạn của phần đã làm:**
- Chỉ bắt quan hệ **viết tường minh**, như "trừ trường hợp", "không áp dụng", "theo quy định tại". Quan hệ ngầm (ví dụ khoản 1 Điều 621 chặn Điều 626 mà không có từ nối) chưa có.
- Ngoại lệ chưa phân biệt **phản bác** (kết luận ngược lại) với **vô hiệu hoá** (chỉ làm quy tắc gốc không áp dụng).
- Hai chỗ chưa tách được: phần điều kiện với phần hệ quả trong một mệnh đề ngoại lệ (Điều 646 khoản 3); và phạm vi áp dụng của ngoại lệ khi nó chỉ áp cho một vế của câu (Điều 617 khoản 1 điểm a).
- Chỉ chạy cho BLDS 2015. Một số chỗ vẫn ghi cứng theo tên file.
- A4 chỉ hiểu các mẫu câu chuẩn; tầng LLM chưa chạy thật.
- Chưa có con số precision/recall thật, vì chưa có đáp án do người gán.

**Các bước tiếp theo của đề cương, chưa làm (ngoài phạm vi KG hiện tại):** LLM phân loại quan hệ; sổ khái niệm và đồ thị khái niệm; trích quy tắc; kiểm tra ở mức quy tắc kèm LLM tự sửa; biên dịch sang s(CASP) và hỏi đáp; bộ tình huống có nhãn độ sâu ngoại lệ; thực nghiệm so sánh.

---

## 10. Gợi ý khi báo cáo với thầy

**Ba ý chính nên nói:**
1. Đã xây xong **tự động** đồ thị tri thức cho phần Thừa kế: 225 nút, 481 cạnh. Đồ thị có cây cấu trúc đầy đủ, dẫn chiếu, ngoại lệ tường minh và phiên bản theo thời gian, cộng 7 nhóm kiểm tra tự động.
2. Đã tự rà soát và **chặn các lỗi "im lặng làm sai"**. Hệ thống dừng và báo khi gặp câu chưa hiểu, thay vì đoán.
3. Phần cập nhật đã chuyển sang **neuro-symbolic** đúng tinh thần đề cương: LLM chỉ đề xuất, máy kiểm bằng luật.

**Câu hỏi thầy có thể hỏi, và câu trả lời:**

| Câu hỏi | Trả lời |
|---|---|
| Độ chính xác bao nhiêu? | Chưa có số thật. Đã có khung chấm điểm (mẫu 11 Điều); cần người gán đáp án độc lập, không xem kết quả của máy |
| Sao không dùng LLM đọc luôn từ đầu? | Theo đề cương, LLM hay nối sai ngoại lệ lồng nhau và đặt tên khái niệm không nhất quán. Phần chắc chắn làm bằng luật để kiểm được; LLM chỉ dùng chỗ cần hiểu ngôn ngữ, và luôn bị kiểm lại |
| Văn bản sửa đổi lấy đâu ra? | BLDS 2015 phần Thừa kế chưa bị sửa. Đang dùng 8 văn bản tự soạn, cộng 19 câu thật mượn từ Luật 85/2025/QH15. Bộ chính thức sẽ do học viên hỗ trợ soạn |
| Quan hệ ngầm thì sao? | Chưa làm. Theo đề cương, LLM đề xuất và bộ quét kiểm lại |
| Cập nhật có phải dựng lại cả đồ thị không? | Không. Chỉ tính lại cho đơn vị có chữ thay đổi; phiên bản cũ được giữ lại |
| "Khử trùng lặp" làm thế nào? | Bộ ba trùng được gộp tự động; đơn vị trùng chữ được gắn nhãn, không gộp. Khử trùng lặp ở mức khái niệm sẽ làm qua sổ khái niệm |

---

## 11. Bản đồ file

| Chỗ | Có gì |
|---|---|
| `src/a1_parse.py` … `src/a7_graph.py` | 7 bước chính |
| `src/a4_llm.py` | Gọi Claude API (tầng LLM của A4) |
| `src/eval_gold.py` | Chấm precision/recall so với đáp án gán tay |
| `src/eval_ext_amend.py` | Chạy bộ thử 19 câu sửa đổi thật |
| `src/run_all.py` | Chạy lại toàn bộ và chạy test |
| `src/test_*.py` | 266 test |
| `data/processed/` | Mọi file kết quả (đồ thị nằm ở `a7_blds2015_p4_nodes.jsonl`, `a7_blds2015_p4_edges.jsonl`) |
| `data/gold/` | Mẫu để gán đáp án (chờ người gán) |
| `docs/a*_report_*.txt` | Báo cáo của từng bước |
| `docs/a4_quyet_dinh.txt`, `docs/a6_a7_quyet_dinh.txt`, `docs/pham_vi_mo_rong.txt` | Mọi quyết định thiết kế và phạm vi, kèm lý do |
| `review_a1_a7_findings.md` | Báo cáo rà soát 22 vấn đề và bảng theo dõi đã sửa |
| `plan_sua_a1_a7.md` | Kế hoạch sửa và các khoảng trống so với đề cương |

**Chạy lại toàn bộ** (cần Python 3.10 trở lên):

```
/opt/homebrew/bin/python3.13 -I src/run_all.py
```

Dòng cuối của kết quả phải là `XONG`, và mọi bộ test đều ghi `tổng test lỗi: 0`.
