# Giải thích khái niệm của luận văn, theo thứ tự học (20/10/2026)

File này giải thích đề cương v5 (`claude/DeCuong_v5.md`) từ dễ đến khó. Mọi mục dùng chung một ví dụ: Điều 626 và khoản 1, khoản 2 Điều 621. Mỗi mục kết thúc bằng một câu tự kiểm. Trả lời được câu đó bằng lời của mình thì sang mục sau.

**Nhãn:**
- [Bài tự nêu]: lấy từ PDF toàn văn, nguồn ghi trong `claude/GhiChuDoc_9Bai_2026-10-09.md` (file đó dùng số tham khảo cũ, xem `claude/BanDo_TaiLieu.md` mục 3).
- [Bài tự nêu – web]: đọc toàn văn qua công cụ đọc web, chưa đối chiếu PDF.
- [Suy luận]: nhận định của Claude.
- [Chưa kiểm chứng]: tóm tắt, trí nhớ.

**Lưu ý về câu chữ luật.** Nội dung các điều luật dưới đây là diễn giải theo đề cương. Số điều và câu chữ chính xác phải đối chiếu với văn bản gốc của Bộ luật Dân sự 2015 (việc còn mở trong `claude/SoQuyetDinh.md`).

**Tên kỹ thuật** viết bằng tiếng Anh, giống khi viết code. Đoạn mã ở mục 8.3 và hai phép thử vòng chặn ở mục 11.1 đã chạy thử ngày 20/10 trên s(CASP) 1.1.4 (SWI-Prolog 9.0.4).

---

## 0. Luận văn trong bốn câu

1. Luận văn xây dựng tự động một cơ sở tri thức dạng đồ thị từ phần Thừa kế của Bộ luật Dân sự 2015 (Điều 609–662). Theo Hình 2, người chỉ soạn vị từ đầu vào và xem các mục bị cô lập.
2. Cơ sở tri thức có quản lý liên kết (kể cả khi luật bị sửa đổi) và tự kiểm soát trùng lặp, mâu thuẫn. Đây là các cơ chế thầy Hiển yêu cầu.
3. Trên cơ sở tri thức đó, bộ giải s(CASP) trả lời câu hỏi thừa kế bằng tiếng Việt. Câu trả lời gồm kết luận và chuỗi điều khoản đã dùng. LLM chỉ làm các bước cần hiểu ngôn ngữ.
4. Phần mới không nằm ở cơ chế. Phần mới là bộ dữ liệu, số liệu so sánh với cách để LLM tự làm, và cách chọn vị từ bằng đồ thị khái niệm.

**Tự kiểm:** Nếu thầy hỏi "luận văn của em đóng góp cơ chế gì mới?", em trả lời thế nào?

---

## 1. Ví dụ xuyên suốt

Ba quy định, viết gọn:

| Mã | Nội dung (diễn giải) |
|---|---|
| R626 | Người được chỉ định trong di chúc thì được hưởng di sản theo di chúc |
| R621_1a | Người bị kết án về hành vi cố ý xâm phạm sức khoẻ của người để lại di sản thì **không được quyền hưởng di sản** |
| R621_2 | Người thuộc khoản 1 **vẫn được hưởng** nếu người để lại di sản đã biết hành vi đó mà vẫn cho hưởng theo di chúc |

Bốn tình huống. A là người để lại di sản, B được ghi tên trong di chúc của A.

| Ca | Dữ kiện | Đáp án |
|---|---|---|
| 1 | B có tên trong di chúc. Không có gì khác | B được hưởng |
| 2 | Như ca 1, thêm: B bị kết án. A không biết | B không được hưởng |
| 3 | Như ca 2, nhưng A đã biết mà vẫn giữ di chúc | B được hưởng (đây là Hình 1 của đề cương) |
| 4 | A để lại di chúc. Tình huống không nói B có tên trong di chúc hay không. Không có dữ kiện nào khác | Chưa đủ căn cứ |

**Tự kiểm:** Từ ca 1 sang ca 2 em thêm một dữ kiện. Kết luận đổi thế nào? Từ ca 2 sang ca 3 thì sao?

---

## 2. Suy luận khả hủy

Logic thông thường có tính **đơn điệu**: đã kết luận được gì thì thêm dữ kiện cũng không mất kết luận đó.

Luật không như vậy. Ở ca 1, B được hưởng. Thêm "B bị kết án" (ca 2) thì kết luận mất. Thêm tiếp "A đã biết mà vẫn giữ di chúc" (ca 3) thì kết luận quay lại.

Kiểu suy luận mà kết luận có thể bị huỷ khi có thêm dữ kiện gọi là **suy luận khả hủy** (defeasible reasoning). Nguồn gốc của nó trong luật là cấu trúc "quy định chung, ngoại lệ, ngoại lệ của ngoại lệ".

**Tự kiểm:** Vì sao không viết được ví dụ 626/621 bằng logic đơn điệu mà không phải gộp hết điều kiện vào một quy tắc?

---

## 3. Vì sao không để LLM trả lời thẳng

**Đề cương nói gì.** LLM trả lời trực tiếp thì phải tự đoán ngoại lệ nào thắng. Không có gì bảo đảm kết luận đổi đúng khi tình huống đổi. Người dùng cũng không kiểm tra được câu trả lời dựa trên điều luật nào.

**Đề cương không nói gì.** Đề cương **không** nói "LLM mạnh trả lời sai". Lý do:
- Học viên đã hỏi thử Gemini và Grok hai câu ngoại lệ lồng (ca gốc và ca đối chứng), không dán văn bản luật. Cả hai trả lời đúng và trích đúng luật.
- Thí nghiệm duy nhất tìm được với mô hình mạnh (báo cáo Aethis, chỉ có trên arXiv, tác giả bán sản phẩm cạnh tranh) cho kết quả 97–100% ở chuỗi 3–5 tầng [Bài tự nêu – web, `TraCuu_CongTrinhGanNhat`].

**Vậy luận văn còn giá trị gì** [Suy luận]:
- Cơ sở tri thức dựng một lần, được kiểm tra, dùng lại cho mọi câu hỏi. LLM phải đọc lại luật mỗi lần hỏi.
- Câu hỏi "LLM có dựng được cơ sở tri thức đúng cho cả chế định không" chưa ai đo trên luật Việt Nam. Luận văn đo việc này (Tầng 1).
- Tính truy vết được là **đặc tính thiết kế**, không phải kết quả thực nghiệm. Hệ ký hiệu luôn trả cây chứng minh, nên đo nó là đo một thứ đúng sẵn theo cách dựng.

**Điều có thể xảy ra:** ở Tầng 3, hệ thống và LLM mạnh hoà nhau về độ chính xác. Đề cương chấp nhận khả năng này.

**Tự kiểm:** Nếu hội đồng nói "ChatGPT trả lời đúng câu này rồi", em dùng phần nào của đề cương để trả lời?

---

## 4. Cơ sở tri thức gồm những gì

Cơ sở tri thức là một đồ thị: nút và cạnh. Mỗi cạnh lưu thành một **bộ ba** (nút đầu, tên cạnh, nút cuối), giống cách nhóm thầy làm ở [5]. File bộ ba (CSV hoặc JSONL) được nạp vào `networkx` để duyệt và quét.

Đồ thị có hai lớp.

**Lớp văn bản**

| Nút | Ví dụ |
|---|---|
| Đơn vị Điều, Khoản, Điểm, có mã ổn định | `BLDS2015.D621`, `BLDS2015.D621.K1`, `BLDS2015.D621.K1.a` |
| Phiên bản của đơn vị, có thời điểm hiệu lực | phiên bản gốc của `BLDS2015.D621.K2`, có `valid_from`, `valid_to` |
| Văn bản sửa đổi | `AMD_001` (văn bản giả định) |

| Cạnh (tên trong code) | Tên thầy dùng | Ví dụ |
|---|---|---|
| `contains` | chứa_khoản | (`BLDS2015.D621`, contains, `BLDS2015.D621.K1`) |
| `part_of` | thuộc_điều | (`BLDS2015.D621.K1`, part_of, `BLDS2015.D621`) |
| `refers_to` | dẫn_chiếu_đến | (`BLDS2015.D621.K2`, refers_to, `BLDS2015.D621.K1`) |
| `exception_of` | là_ngoại_lệ_của | (`BLDS2015.D621.K1`, exception_of, `BLDS2015.D626`) |
| `amends` | sửa_đổi_bổ_sung | (`AMD_001`, amends, `BLDS2015.D621.K1`) |
| `replaces` | thay_thế | (`AMD_002`, replaces, …) |
| `repeals` | bãi_bỏ | (`AMD_003`, repeals, `BLDS2015.D621.K2`) |

**Lớp quy tắc**

| Nút | Ví dụ |
|---|---|
| Quy tắc | `r626`, `r621_1a`, `r621_2` |
| Vị từ (mục 5) | `named_in_will`, `disqualified` |

| Cạnh | Nghĩa | Ví dụ |
|---|---|---|
| `extracted_from` | quy tắc trích từ đơn vị nào | (`r621_1a`, extracted_from, `BLDS2015.D621.K1.a`) |
| `concludes` | quy tắc kết luận vị từ nào | (`r621_1a`, concludes, `disqualified`) |
| `uses` | quy tắc dùng vị từ nào trong điều kiện | (`r626`, uses, `named_in_will`) |
| `blocks` | quy tắc này chặn quy tắc kia | (`r621_1a`, blocks, `r626`) |
| `anchored_to` | vị từ khái niệm gắn với điều định nghĩa nó | (`disqualified`, anchored_to, `BLDS2015.D621`) |

Cạnh `exception_of` nối hai **đơn vị văn bản**. Cạnh `blocks` nối hai **quy tắc**. Một cạnh `exception_of` được chuyển thành một hoặc vài cạnh `blocks`.

Đề cương bỏ chữ "hai lớp" cho ngắn. Thiết kế vẫn dùng hai lớp (xem `BanGiao` mục 4).

**Tự kiểm:** Vẽ tay đồ thị con quanh Điều 621 và Điều 626, gồm cả hai lớp. Có bao nhiêu nút, bao nhiêu cạnh?

---

## 5. Vị từ: vị từ đầu vào và vị từ khái niệm

**Vị từ** là tên của một mệnh đề trong quy tắc. Ví dụ `convicted_of_harming(B, A)` nghĩa là "B bị kết án về hành vi cố ý xâm phạm sức khoẻ của A".

Có hai loại:

| Vị từ | Loại | Gắn với | Ai tạo ra giá trị |
|---|---|---|---|
| `named_in_will(X, W)` | đầu vào | — | người hỏi nêu trong tình huống |
| `convicted_of_harming(X, T)` | đầu vào | — | người hỏi nêu |
| `testator_knew_and_kept(T, X)` | đầu vào | — | người hỏi nêu |
| `disqualified(X)` ("không được quyền hưởng di sản") | khái niệm | Điều 621 | quy tắc suy ra |
| `inherits_by_will(X)` | khái niệm, cũng là vị từ cần hỏi | Điều 626 | quy tắc suy ra |

- **Vị từ đầu vào** là dữ kiện thô người hỏi nêu thẳng: quan hệ gia đình, nội dung di chúc, bản án. Học viên soạn trước.
- **Vị từ khái niệm** là kết luận pháp lý. Nó chỉ đúng khi có quy tắc suy ra nó, và nó gắn với điều luật định nghĩa nó.

**Phép thử phân loại (quy tắc R2 trong `BanGiao`).** Giả sử người hỏi nêu thẳng vị từ này. Nếu nhờ đó mà bỏ qua được một điều luật, thì nó là khái niệm, không được làm đầu vào. Ví dụ: người hỏi nói "B không được quyền hưởng di sản" thì hệ thống không cần xét Điều 621 nữa. Vậy `disqualified` là khái niệm.

**Vì sao phân loại quan trọng.** Khi cho Gemini đọc toàn văn 54 điều và tự viết chương trình, lỗi hay gặp nhất là khai báo khái niệm thành đầu vào. Ví dụ điểm d khoản 1 Điều 650 có điều kiện về những người thừa kế theo di chúc "không có quyền hưởng di sản" hoặc từ chối. Gemini khai báo cả điều kiện này thành một vị từ đầu vào. Khi đó quy tắc của Điều 650 không còn nối tới Điều 621, nên khoản 2 Điều 621 không tác động tới Điều 650 nữa. File phép thử gọi lỗi này là "cắt bằng INPUT" (`PhepThu_DoPhuDanChieu`, Phép thử 2 và 4; một mô hình, mẫu nhỏ, Claude chấm).

**Tự kiểm:** "B là con đẻ của A" là vị từ loại gì? "B là người thừa kế theo pháp luật hàng thứ nhất" thì sao?

---

## 6. Sổ khái niệm và đồ thị khái niệm

### 6.1. Vấn đề cần giải

- Horner và cộng sự [6] cho thấy LLM không dùng lại tên vị từ giữa các đoạn. Cùng một khái niệm có nhiều tên. Quy tắc dùng một tên, quy tắc định nghĩa dùng tên khác, nên hai quy tắc không nối được và quy tắc kia không bao giờ chạy [Bài tự nêu, [6] mục 5.2 và 5.3].
- Không thể dựa vào dẫn chiếu tường minh để nối. Trong Điều 609–662 chỉ có 14 cạnh dẫn chiếu giữa các điều. Dẫn chiếu tường minh chỉ phủ khoảng 2–7% số cặp (khái niệm, điều dùng khái niệm) (`PhepThu_DoPhuDanChieu`). Phần lớn quan hệ giữa các điều là **ngầm**, qua thuật ngữ.

### 6.2. Sổ khái niệm

Sổ khái niệm là danh sách mọi vị từ được phép dùng, gồm hai loại ở mục 5.
- Mỗi khái niệm một tên. Cách viết khác của cùng khái niệm ghi thành bí danh. Ví dụ "không được quyền hưởng di sản" (Điều 621) và "không có quyền hưởng di sản" (Điều 650) là một khái niệm (cần đối chiếu câu chữ gốc).
- LLM chỉ được dùng vị từ có trong sổ. Thiếu thì gắn cờ, không tự đặt tên mới.
- Sổ được đóng băng trước khi viết tình huống cho tập kiểm tra.
- Cách soạn sổ cho khỏi sót (R1–R4, C1–C4) nằm trong `BanGiao` mục 3B.

### 6.3. Đồ thị khái niệm

Đồ thị khái niệm nối mỗi khái niệm với điều định nghĩa nó và các điều dùng nó. Ví dụ từ `PhepThu_DoPhuDanChieu`:

| Khái niệm | Điều định nghĩa | Một số điều dùng mà không dẫn chiếu |
|---|---|---|
| thời điểm mở thừa kế | 611 | 613, 614, 623, 650 |
| không được quyền hưởng di sản | 621 | 622, 650, 651 |
| chết cùng thời điểm | 619 | 643, 650, 652 |

**Cách dùng khi trích quy tắc.** Khi trích Điều 650, LLM chỉ nhận vị từ của các khái niệm mà Điều 650 dùng, không nhận cả sổ.

**Vì sao gọi là "khung".** Sổ và đồ thị khái niệm có trước khi trích quy tắc nào. Quy tắc ở Điều 621 kết luận `disqualified`. Quy tắc ở Điều 650 dùng `disqualified`. Hai quy tắc cùng gắn vào một nút `disqualified`, nên Điều 650 nối với Điều 621 dù câu chữ không dẫn chiếu.

### 6.4. Rủi ro và vì sao đây là thực nghiệm thật

Horner mục 4.2.2: đưa cho LLM danh sách vị từ đã có thì LLM dùng lại nhiều hơn, nhưng cũng dùng **sai ngữ cảnh** nhiều hơn [Bài tự nêu]. Horner mục 5.3(i) gợi ý chọn trước các vị từ liên quan nhất rồi chỉ đưa những vị từ đó, nhưng không nói chọn cách nào và chưa thử [Bài tự nêu, chỉ có ở bản ASAIL].

Luận văn chọn bằng đồ thị khái niệm và đo. Kết quả không biết trước:
- Chọn ít thì bớt dùng sai ngữ cảnh.
- Nhưng nếu đồ thị khái niệm sót một khái niệm thì LLM thiếu vị từ cần dùng.

**Không mới ở đâu.** Ý "thống nhất bộ vị từ trước" đã có: Witt và cộng sự cho người mã hoá thống nhất danh sách atom trước, mức trùng atom tăng từ 4,27% lên 57,64% [Bài tự nêu]. Catala khai báo từ vựng trước. Nhóm thầy [5] neo khái niệm vào điều khoản (trường InnerRul). Phần mới chỉ là **cách chọn** và **phép đo**.

**Tự kiểm:** Nếu (iii) (đưa cả sổ) cho kết quả bằng (ii) (chỉ đưa vị từ do đồ thị chọn), điểm mới nào của luận văn mất?

---

## 7. Quan hệ ngoại lệ và quan hệ chặn

### 7.1. Ngoại lệ tường minh và ngoại lệ ngầm

- **Tường minh:** câu chữ có dấu hiệu. Ví dụ "trừ trường hợp", "không áp dụng đối với", "những người quy định tại khoản 1 Điều này vẫn…". Khoản 2 Điều 621 là ngoại lệ tường minh của khoản 1. Bắt bằng mẫu câu, rồi LLM phân loại.
- **Ngầm:** không có dấu hiệu. Khoản 1 Điều 621 là ngoại lệ của Điều 626, nhưng Điều 621 không nhắc tới Điều 626. Đồ thị khái niệm sinh ra các cặp ứng viên (hai điều cùng đụng tới một khái niệm), LLM đề xuất quan hệ, bộ quét kiểm tra lại.

Trong các chuỗi ngoại lệ của phần Thừa kế, cạnh xuyên điều tường minh chỉ có khoảng 3. Cạnh ngầm khoảng 10 [Suy luận, `SangLoc` mục 2.3, Claude tự đọc luật].

### 7.2. Từ ngoại lệ đến chặn

Nếu khoản A là ngoại lệ của khoản B, thì quy tắc trích từ A **chặn** quy tắc trích từ B. "Chặn" nghĩa là quy tắc của B không được dùng khi điều kiện của A đúng.

### 7.3. Phản bác và vô hiệu hoá

| Loại | Làm gì | Ví dụ |
|---|---|---|
| Phản bác (rebuttal) | Đưa ra kết luận ngược với quy định gốc | Khoản 1 Điều 621 kết luận "không được hưởng", ngược với "được hưởng" của Điều 626 |
| Vô hiệu hoá (undercut) | Chỉ làm quy định gốc không áp dụng, không tự kết luận | Khoản 2 Điều 621 làm khoản 1 không áp dụng. Kết luận "được hưởng" là do Điều 626 đưa ra, không phải do khoản 2 |

Xếp khoản 2 Điều 621 vào loại vô hiệu hoá là cách đọc của Claude [Suy luận]. Câu chữ "vẫn được hưởng di sản" cũng có thể đọc là phản bác. Cách đọc này ảnh hưởng tới mục 9.

Hai loại này là khái niệm kinh điển của lý thuyết lập luận khả hủy (Pollock) [Chưa kiểm chứng: chưa đọc nguồn gốc]. Ulizko [7] cũng có loại "defeater" chỉ chặn mà không sinh kết luận [Bài tự nêu]. Không nhận là mới.

**Tự kiểm:** Tìm một ngoại lệ trong phần Thừa kế mà em cho là vô hiệu hoá, và một ngoại lệ là phản bác.

---

## 8. Chặn đệ quy

### 8.1. Quy tắc

Một quy tắc **bị chặn** khi và chỉ khi nó có một ngoại lệ **đang áp dụng** và ngoại lệ đó **không bị chặn**.

Quy tắc này gọi lại chính nó (xét "ngoại lệ đó có bị chặn không"), nên tự đi được bao nhiêu tầng cũng được. Không cần viết quy tắc riêng cho ca "bị kết án nhưng được tha thứ".

### 8.2. Chạy tay bốn ca

| Ca | R626 áp dụng? | R621_1a áp dụng? | R621_2 áp dụng? | Xét từ trên xuống | Kết quả |
|---|---|---|---|---|---|
| 1 | có | không | không | R626 không có ngoại lệ nào đang áp dụng → không bị chặn | được hưởng |
| 2 | có | có | không | R621_1a không bị chặn → R621_1a chặn R626 | không được hưởng |
| 3 | có | có | có | R621_2 không bị chặn → R621_1a bị chặn → R626 không bị chặn | được hưởng |
| 4 | không biết | không | không | Không chứng minh được điều kiện của R626, cũng không có quy tắc nào kết luận ngược | chưa đủ căn cứ |

### 8.3. Mã minh hoạ (đã chạy thử 20/10)

```prolog
% Điều kiện áp dụng của từng quy tắc (mỗi điều khoản một quy tắc)
applicable(r626, X)    :- named_in_will(X, W).
applicable(r621_1a, X) :- convicted_of_harming(X, T).
applicable(r621_2, X)  :- convicted_of_harming(X, T), testator_knew_and_kept(T, X).

% Quan hệ chặn, sinh từ cạnh exception_of
defeats(r621_1a, r626).
defeats(r621_2, r621_1a).

% Bị chặn khi có ngoại lệ đang áp dụng mà ngoại lệ đó không bị chặn
blocked(R, X) :- defeats(E, R), applicable(E, X), not blocked(E, X).

% Kết luận
inherits_by_will(X)  :- applicable(r626, X), not blocked(r626, X).
disqualified(X)      :- applicable(r621_1a, X), not blocked(r621_1a, X).
-inherits_by_will(X) :- disqualified(X).      % khoản 1 Điều 621 là phản bác

% Ca 3
named_in_will(b, will_a).
convicted_of_harming(b, a).
testator_knew_and_kept(a, b).
```

`not` là phủ định mặc định: "không chứng minh được". Dấu `-` là phủ định mạnh: "chứng minh được là sai".

**Kết quả chạy thử** (thay ba dòng dữ kiện cuối theo từng ca):

| Ca | Hỏi `inherits_by_will(b)` | Hỏi `-inherits_by_will(b)` | Trạng thái suy ra |
|---|---|---|---|
| 1 | có | không hỏi | kết luận được |
| 2 | không có mô hình | có | bị bác |
| 3 | có | không hỏi | kết luận được |
| 4 | không có mô hình | không có mô hình | chưa đủ căn cứ |

- Ca 3, hỏi `disqualified(b)`: không có mô hình. Hỏi `-disqualified(b)`: s(CASP) báo vị từ này không tồn tại, vì không quy tắc nào kết luận nó. Đây đúng là tình huống ở mục 9: chỉ nhìn `p` và `-p` thì không phân biệt được "bị bác" với "chưa đủ căn cứ".
- B bị kết án, A không biết, tình huống không nói B có tên trong di chúc: hỏi `-inherits_by_will(b)` được "có".
- Ghi chú cài đặt: vị từ đầu vào không có dữ kiện nào thì s(CASP) chỉ cảnh báo "does not exist" rồi vẫn chạy, coi như sai.

### 8.4. Không mới

PROLEG [2] đã làm đúng việc này: `exception(H, E)` tách ngoại lệ khỏi quy tắc gốc, và phụ lục của bài có ngoại lệ của ngoại lệ [Bài tự nêu]. Ulizko [7] và Catala cũng có ngoại lệ lồng. Đề cương viết "Áp dụng", đúng với thực tế.

Viết phẳng (gộp hết điều kiện vào một quy tắc) cũng ra kết quả đúng nếu viết đúng. Vì vậy luận văn **không** nói cách đệ quy đúng hơn. Lợi ích của cách tách từng quy tắc là khi sửa một khoản không phải sửa quy tắc ở điều khác. Lợi ích này đúng sẵn theo cách dựng, nên không đưa thành kết quả thực nghiệm [Suy luận].

**Tự kiểm:** Thêm một ngoại lệ thứ ba chặn R621_2 (giả định). Em phải sửa những dòng nào trong đoạn mã?

---

## 9. Ba trạng thái câu trả lời và "ngoài phạm vi"

Hệ thống kiểm tra cùng lúc mệnh đề cần hỏi `p` và phủ định `-p`, và xem có quy tắc nào dẫn tới `p` đang bị chặn không.

| Trạng thái | Khi nào | Ví dụ (hỏi "B có được hưởng theo di chúc?") |
|---|---|---|
| Kết luận được | Chứng minh được `p` | Ca 1, ca 3 |
| Bị bác | Quy tắc dẫn tới `p` áp dụng nhưng bị một ngoại lệ đang áp dụng chặn | Ca 2 |
| Chưa đủ căn cứ | Không chứng minh được `p`, không chứng minh được `-p`, không có quy tắc nào dẫn tới `p` đang bị chặn | Ca 4 |
| Ngoài phạm vi (từ chối) | Câu hỏi không viết được bằng vị từ trong sổ | "B phải nộp thuế bao nhiêu khi nhận nhà?" |

**Vì sao phải xét quy tắc đang bị chặn.** Hỏi ở ca 3: "B có thuộc diện không được quyền hưởng di sản không?". R621_1a áp dụng nhưng bị R621_2 chặn. R621_2 là vô hiệu hoá, nên không quy tắc nào chứng minh được `-disqualified(b)`. Nếu chỉ nhìn `p` và `-p`, hệ thống sẽ trả "chưa đủ căn cứ". Đáp án đúng là "bị bác". Vì vậy phải nhìn thêm các quy tắc đang bị chặn.

**Quy ước của PROLEG cho dữ kiện không nêu.** Điều kiện của ngoại lệ mà tình huống không nhắc tới thì coi như không có [Bài tự nêu, [2] mục 2, 3, 5]. Ví dụ: tình huống nói B bị kết án mà không nói A có biết không. Khi đó R621_2 không áp dụng, và câu trả lời là "bị bác", không phải "chưa đủ căn cứ". "Chưa đủ căn cứ" chỉ xảy ra khi thiếu điều kiện của **quy tắc chính**, như ca 4.

**Câu hỏi thiết kế còn mở** [Suy luận]: làm sao phân biệt "B chắc chắn không có tên trong di chúc" với "tình huống không nói"? Cần dữ kiện phủ định tường minh (s(LAW) dùng phủ định mạnh `-evidence(...)` cho việc này [Bài tự nêu – web]). Chốt khi cài đặt.

**Tự kiểm:**
- Ở ca 2, hỏi "B có thuộc diện không được quyền hưởng di sản không?". Trạng thái nào?
- Tình huống nói B bị kết án, A không biết, nhưng không nói B có tên trong di chúc. Hỏi "B có được hưởng theo di chúc?". Đoạn mã ở mục 8.3 trả gì, và vì sao không phải "chưa đủ căn cứ"?

---

## 10. Cập nhật khi có văn bản sửa đổi

Chạy thử với văn bản giả định "Bãi bỏ khoản 2 Điều 621":

1. Nạp văn bản, tạo nút `AMD_003`. Mẫu câu "Bãi bỏ khoản … Điều …" cho biết đích là `BLDS2015.D621.K2`.
2. Không xoá nút cũ. Phiên bản hiện tại của `BLDS2015.D621.K2` được ghi `valid_to` bằng ngày hiệu lực của văn bản sửa đổi. Thêm cạnh (`AMD_003`, repeals, `BLDS2015.D621.K2`). Quy tắc `r621_2` không còn được biên dịch cho các thời điểm sau ngày đó.
3. Chỉ trích lại điều có câu chữ đổi. Bãi bỏ thì không có gì để trích. Nếu là "sửa đổi khoản 1 Điều 621" thì chỉ trích lại khoản 1 Điều 621.
4. Lập danh sách phần bị ảnh hưởng để kiểm tra lại (Nội dung 2):
   - quy tắc chặn hoặc bị chặn bởi khoản đó: `r621_1a`;
   - quy tắc dùng khái niệm do Điều 621 định nghĩa: các quy tắc dùng `disqualified` ở Điều 622, 644, 650, 651, và quy tắc kết luận ngược với Điều 626;
   - các điều dẫn chiếu tới Điều 621.
5. Bộ quét thấy cạnh `blocks(r621_2, r621_1a)` có một đầu là quy tắc của khoản đã bị bãi bỏ. Đây là cờ "quan hệ bị đứt sau khi cập nhật".
6. Kết quả: ca 3 đổi đáp án thành "không được hưởng".

**Đo cái gì.** Tỷ lệ cặp tình huống bị ảnh hưởng (đáp án đổi sau khi sửa) được trả lời đúng. So với hai đối chứng:
- LLM mạnh nhận chương trình s(CASP) cũ và văn bản sửa đổi, tự sửa chương trình;
- LLM mạnh trả lời trực tiếp trên toàn văn đã sửa.

**Phần đúng sẵn theo cách dựng, không đưa thành kết quả:** nhận dạng câu "Bãi bỏ khoản 2 Điều 621" bằng mẫu câu, và việc giữ phiên bản cũ.

**Phần đo được thật:** thay đổi có lan đúng sang các điều khác qua khái niệm hay không (ví dụ Điều 650 cũng phải đổi đáp án).

**Câu thầy dặn "không phá vỡ cấu trúc đồ thị hiện hữu" thể hiện ở đâu:** phiên bản cũ còn nguyên, các cạnh cũ không bị xoá, bộ quét không có lỗi mới, các tình huống không bị ảnh hưởng vẫn trả lời như cũ.

**Không mới.** [5] tự nêu cập nhật được mà không dựng lại đồ thị, nhưng không có thực nghiệm [Bài tự nêu, `DeXuat_ND1_ND2_v4.4` mục 1]. PAPER_04 có các phép thêm, sửa, xoá bộ ba nhưng chưa xuất bản. Viết là "áp dụng".

**Việc còn mở:** "chương trình s(CASP) cũ" đưa cho LLM là chương trình của cách nào? Nên dùng chương trình của cách (ii), để hai bên chỉ khác ở cơ chế cập nhật [Suy luận, chưa chốt].

**Tự kiểm:** Văn bản giả định "Bãi bỏ điểm a khoản 1 Điều 621". Những cặp tình huống nào đổi đáp án? Cạnh nào bị đứt?

---

## 11. Bộ quét đồ thị và kiểm soát chồng chéo

### 11.1. Năm loại cờ

| Cờ | Nghĩa | Ví dụ | Bắt bằng gì |
|---|---|---|---|
| Quy tắc không bao giờ chạy | Dùng một vị từ không quy tắc hay dữ kiện nào sinh ra | (Giả định) quy tắc Điều 650 dùng `has_valid_will`, nhưng không quy tắc nào kết luận nó và nó không có trong danh sách vị từ đầu vào | So vị từ trong điều kiện với vị từ ở phần kết luận và danh sách đầu vào |
| Quy tắc trùng | Hai quy tắc giống hệt | Trích Điều 621 hai lần | So chuỗi đã chuẩn hoá |
| Quan hệ bị đứt sau cập nhật | Cạnh trỏ tới phần đã hết hiệu lực | `blocks(r621_2, r621_1a)` sau khi khoản 2 bị bãi bỏ | Kiểm hiệu lực hai đầu cạnh |
| Vòng chặn | Các quy tắc chặn lẫn nhau | LLM trích nhầm: khoản 1 chặn khoản 2 và khoản 2 chặn khoản 1 | Tìm chu trình trên đồ thị `defeats` |
| Cặp mâu thuẫn | Hai kết luận trái nhau mà không có quan hệ chặn | Có `inherits_by_will` (626) và `-inherits_by_will` (621.1) nhưng thiếu cạnh chặn 621.1 → 626 | So các cặp `p` và `-p` |

**Vì sao vòng chặn nguy hiểm.** Theo bài Justifications của nhóm s(CASP), vòng qua số chẵn phép phủ định cho hai mô hình, tức hai câu trả lời cho cùng một câu hỏi, mà không báo lỗi. Vòng qua số lẻ phép phủ định có thể làm cả chương trình không có mô hình nào, tức mọi câu hỏi đều thất bại [Bài tự nêu, `GhiChuDoc` mục 20; bài này không trích trong v5]. Hai quy tắc chặn nhau là vòng chẵn. Một quy tắc tự chặn mình là vòng lẻ [Suy luận].

Đã chạy thử ngày 20/10 với quy tắc `blocked` ở mục 8.3:
- Hai quy tắc r1, r2 chặn nhau: hỏi kết luận của r1 được "có", hỏi kết luận của r2 cũng được "có". Mỗi câu đúng trong một mô hình riêng; hỏi cả hai cùng lúc thì không có mô hình. s(CASP) không báo lỗi gì. Nghĩa là hệ thống có thể trả lời "có" cho hai câu hỏi trái nhau.
- Một quy tắc tự chặn mình: hỏi một câu **không liên quan** (`q(b)`, chỉ là một dữ kiện) cũng được "không có mô hình". Một lỗi nhỏ làm hỏng toàn bộ chương trình.

Phải tìm vòng trên đồ thị `defeats` cụ thể, không tìm ở mức vị từ, vì quy tắc `blocked` ở mục 8.3 tự nó đã gọi `not blocked` [Suy luận].

**Cặp mâu thuẫn chính là ý của thầy.** Thầy viết "một hành vi bị gán song song hai chế tài đối kháng mà thiếu nút điều kiện phân tách". Ở đây "nút điều kiện phân tách" là quan hệ chặn. Thiếu nó thường nghĩa là một ngoại lệ ngầm bị sót khi trích.

### 11.2. Khử trùng lặp

- Bản trùng hoàn toàn: gộp tự động.
- Hai vị từ khác tên có thể cùng nghĩa: chỉ cảnh báo, vì gộp nhầm làm sai nghĩa luật. Ví dụ thật từ phép thử Gemini: `simultaneous_death` (Điều 619) và `predeceased_or_simultaneous` (Điều 652) trông giống nhau, nhưng "chết trước hoặc cùng lúc" rộng hơn "chết cùng lúc". Gộp hai vị từ này là sai.
- Trên lớp văn bản, mã định danh không trùng theo cách dựng. "Khử trùng thực thể" ở lớp khái niệm phần lớn là chuẩn hoá sổ (một khái niệm một tên, cách viết khác là bí danh).

Nhóm thầy [5] gộp bộ ba đồng nghĩa bằng từ điển và PhoBERT (cosine ≥ 0,6), trong phạm vi một đơn vị văn bản [Bài tự nêu]. Luận văn làm ở mức quy tắc và vị từ, xuyên điều, và không gộp tự động khi chỉ nghi đồng nghĩa.

### 11.3. Tự sửa và cô lập

1. LLM sửa mục bị gắn cờ, dựa trên thông báo của bộ quét, văn bản luật nguồn và các vị từ liên quan.
2. Bản sửa chỉ được nhận khi đủ ba điều kiện: biên dịch lại được, không sinh cờ mới, số tình huống mẫu trả lời đúng không giảm.
3. Tối đa hai vòng.
4. Không sửa được thì **cô lập**: tách mục đó khỏi chương trình suy luận. Câu hỏi nào phụ thuộc vào mục bị cô lập thì hệ thống từ chối trả lời.
5. Học viên xem lại các mục bị cô lập.

**Không mới.** Ulizko [7] có bộ kiểm tra bốn tầng, cho LLM trích lại đúng một lượt, lỗi lần hai thì trả "Undetermined" kèm cờ cho người duyệt [Bài tự nêu]. Rất gần. Viết là "áp dụng".

**Đo gì.** Tầng 2 đo tỷ lệ cờ đúng là lỗi thật. Không đo độ phủ của bộ quét, vì bộ quét bắt đúng những gì nó được định nghĩa để bắt, nên độ phủ đúng sẵn một phần.

**Câu hỏi còn mở cho thầy:** thầy có muốn quét xung đột ngay trên lớp văn bản, khi chưa có quy tắc không? Nếu có thì phải định nghĩa "chế tài" và "điều kiện phân tách" trên đơn vị văn bản.

**Tự kiểm:** LLM sửa một cờ "cặp mâu thuẫn" bằng cách xoá luôn quy tắc 621.1. Bản sửa này có qua được ba điều kiện không? Vì sao?

---

## 12. Bộ dữ liệu đánh giá

### 12.1. Phụ thuộc và cặp đối chứng

**Phụ thuộc** là khi muốn áp dụng đúng một điều phải biết kết quả của điều khác. Điều 626 phụ thuộc Điều 621.

Mỗi phụ thuộc có một **cặp tình huống đối chứng**, chỉ khác nhau ở dữ kiện thuộc điều được phụ thuộc. Ca 2 và ca 3 ở mục 1 là một cặp: chỉ khác ở việc A có biết hay không.

**Vì sao chấm theo cặp.** Một cơ sở tri thức không nối Điều 626 với Điều 621 sẽ luôn trả "được hưởng". Nó đúng ca 3, sai ca 2, tức đúng một nửa nhờ may. Chỉ khi nối đúng mới đúng cả hai. Vì vậy chỉ số chính là **tỷ lệ phụ thuộc đạt**: phụ thuộc mà cả hai tình huống trong cặp đều đúng.

### 12.2. Độ sâu ngoại lệ

Độ sâu là độ dài chuỗi ngoại lệ dài nhất, tính trên văn bản luật, theo định nghĩa của Chen và cộng sự [9]. Quy định gốc là 0, ngoại lệ là 1, ngoại lệ của ngoại lệ là 2.

Ví dụ: Điều 626 (0) ← khoản 1 Điều 621 (1) ← khoản 2 Điều 621 (2). Độ sâu 2.

[9] chỉ tính trong một điều khoản; chỉ 3% đơn vị của [9] có dẫn chiếu sang điều khác [Bài tự nêu]. Luận văn mở rộng sang chuỗi trải qua nhiều điều.

**Vì sao tính trên văn bản, không trên chương trình.** Cùng một luật, viết phẳng thì độ sâu biến mất, viết tách quy tắc thì độ sâu hiện ra. Tính trên văn bản thì độ sâu không phụ thuộc cách mã hoá [Suy luận].

### 12.3. Ai làm

- Hai người độc lập xây dựng và gán nhãn tình huống, không xem kết quả của hệ thống trước. Đo độ nhất quán bằng hệ số Kappa.
- Sổ khái niệm đóng băng trước khi viết tập kiểm tra.
- Văn bản sửa đổi giả định do người hỗ trợ soạn, theo đúng cách viết văn bản sửa đổi thật, kèm cặp tình huống có đáp án đổi và đáp án mới. Hai văn bản tự soạn chỉ dùng khi phát triển, không dùng để đánh giá.

**Rủi ro đã biết** [Suy luận]: học viên đã đọc cả 54 điều và biết các chuỗi ngoại lệ. Không xoá được hoàn toàn, chỉ giảm được: không viết luật quét hay câu lệnh riêng cho một điều cụ thể, chốt câu lệnh có ngày trước khi làm tập kiểm tra.

**Tự kiểm:** Viết một cặp đối chứng cho phụ thuộc "Điều 650 phụ thuộc Điều 621". Hai tình huống khác nhau ở dữ kiện nào?

---

## 13. Đánh giá

### 13.1. Tầng 1: cơ sở tri thức

Chạy cùng bộ tình huống trên ba cơ sở tri thức:

| Cách | Là gì | Vai trò |
|---|---|---|
| (i) | LLM đọc toàn văn phần Thừa kế, tự viết chương trình s(CASP) | **Đối chứng chính.** Đây là cách một người làm nghề sẽ thử đầu tiên |
| (ii) | Quy trình của luận văn | Cách cần đánh giá |
| (iii) | Như (ii), nhưng LLM nhận cả sổ khái niệm | **Cấu hình bỏ bớt**, không phải đối chứng. (ii) so với (iii) đo riêng tác dụng của đồ thị khái niệm |

Cả ba dùng chung bộ vị từ đầu vào và cùng số vòng sửa lỗi. Lý do [Suy luận]:
- Cùng vị từ đầu vào thì mới chạy được cùng một bộ tình huống trên cả ba.
- (i) không thua chỉ vì đặt tên khác. Cho (i) danh sách vị từ đầu vào còn chặn bớt lỗi "cắt bằng INPUT", tức làm (i) mạnh hơn. Đối chứng mạnh thì kết quả mới có giá trị.

Chỉ số: tỷ lệ phụ thuộc đạt, báo theo độ sâu.

**Kết quả nào làm đề xuất sai:**
- (i) bằng hoặc hơn (ii): điểm mới 2 thành kết quả âm, kết luận là "với LLM mạnh, không cần quy trình này". Vẫn báo cáo được.
- (iii) bằng hoặc hơn (ii): điểm mới 3 sai.

Không kết quả nào đúng sẵn: (i) có thể thắng, (ii) có thể thiếu vị từ.

**Giới hạn còn lại** [Suy luận]: người làm nghề có điều kiện có thể viết sẵn khai báo khái niệm cho (i), như Lorenzo và cộng sự (NLLP 2025) [Bài tự nêu – web]. Đối chứng này không có trong đề cương.

### 13.2. Tầng 2: quan hệ ngoại lệ và bộ quét

- So quan hệ ngoại lệ hệ thống trích với bộ quan hệ chuẩn do người hỗ trợ gán. Đo độ chính xác, độ phủ, F1. Thừa ngoại lệ thì chặn nhầm. Thiếu thì bỏ sót việc chặn.
- Đo tỷ lệ cờ của bộ quét đúng là lỗi thật.
- Tầng 2 giải thích **vì sao** Tầng 1 sai.

### 13.3. Tầng 3: toàn hệ thống

- Đi từ câu hỏi tiếng Việt đến câu trả lời, trên cùng tình huống với Tầng 1. Chênh lệch giữa Tầng 1 và Tầng 3 là lỗi của bước hiểu câu hỏi.
- So với LLM trả lời trực tiếp, có cấp sẵn điều luật.
- Kiểm định McNemar: phép thử cho dữ liệu ghép cặp đúng/sai. Nó chỉ dựa vào các câu mà một bên đúng, bên kia sai. Nếu hai bên đều đúng gần hết thì gần như không có câu như vậy, và kết quả là "không khác biệt".

### 13.4. Đánh giá cập nhật

Xem mục 10.

### 13.5. Những gì đúng sẵn theo cách dựng (không phải kết quả)

- Tách Điều, Khoản, Điểm và sinh cạnh `contains`, `part_of` (bước A1–A2 trong `BanGiao`).
- Nhận dạng câu sửa đổi theo mẫu, giữ phiên bản cũ.
- Câu trả lời có chuỗi điều khoản.
- Độ phủ của bộ quét.

**Tự kiểm:** Vì sao (iii) không được gọi là "baseline"? Nếu hội đồng gọi nó là baseline người rơm, em trả lời thế nào?

---

## 14. Ba điểm mới và công trình gần nhất

| Điểm mới | Công trình gần nhất | Khác ở đâu | Điều gì làm nó sai |
|---|---|---|---|
| 1. Bộ dữ liệu tiếng Việt có nhãn độ sâu cho chuỗi ngoại lệ xuyên điều | NormBench [9]: độ sâu trong một điều khoản. Ulizko [7]: chấm ca ngoại lệ lồng, theo từng tình huống, hợp đồng Nga | Luật Việt Nam, chuỗi xuyên điều, cặp đối chứng | Một bộ dữ liệu như vậy đã có. Law to Code (workshop ICML 2026) chưa đọc toàn văn, là rủi ro lớn nhất |
| 2. Số liệu so sánh quy trình với cách LLM tự viết chương trình | Ulizko [7]: LLM trích lý thuyết cho từng tình huống, không có cơ sở tri thức dùng chung | Một cơ sở tri thức cho cả chế định, phụ thuộc xuyên điều | Đây là phép đo nên con số không "sai". Cái có thể sai là nhận định "quy trình tốt hơn" |
| 3. Chọn trước vị từ bằng đồ thị khái niệm | Horner [6] mục 5.3(i): gợi ý, chưa thử. Witt: người thống nhất atom | Cách chọn cụ thể và có đo | (iii) bằng hoặc hơn (ii) |

**Các cơ chế thầy giao, đều ghi "áp dụng":**

| Cơ chế | Gần nhất |
|---|---|
| Định danh, chứa_khoản, thuộc_điều | [5]; chuẩn đánh dấu văn bản luật như Akoma Ntoso [Chưa kiểm chứng] |
| dẫn_chiếu_đến, là_ngoại_lệ_của | [3] (theo đoạn), PAPER_04 (chưa xuất bản) |
| sửa_đổi_bổ_sung, thay_thế, bãi_bỏ | [5] (tự nêu, không thực nghiệm), PAPER_04 |
| Khử trùng | [5] Thuật toán 1 |
| Xung đột, tự sửa, cô lập | Ulizko [7] |
| Chặn đệ quy, phản bác / vô hiệu hoá | PROLEG [2], Ulizko [7], Catala |

**Tự kiểm:** Chọn một điểm mới. Nêu công trình gần nhất và một câu khác biệt, không dùng chữ "đầu tiên".

---

## 15. Câu hỏi hội đồng có thể hỏi

| Câu hỏi | Hướng trả lời | Xem mục |
|---|---|---|
| LLM mạnh trả lời đúng rồi, làm hệ này để làm gì? | Không nhận LLM sai. Giá trị là cơ sở tri thức dùng lại, kiểm tra được, và phép đo "LLM có dựng đúng không" | 3, 13 |
| Chặn đệ quy có gì mới? | Không mới. Áp dụng PROLEG | 8 |
| Đối chứng có phải người rơm không? | (i) là cách người làm nghề làm, được cùng vị từ đầu vào và cùng vòng sửa. (iii) là cấu hình bỏ bớt, không phải đối chứng | 13.1 |
| Sao không tự gộp đồng nghĩa như [5]? | Gộp nhầm làm sai nghĩa luật. Ví dụ `simultaneous_death` và `predeceased_or_simultaneous` | 11.2 |
| Không có chuyên gia luật, ai quyết đáp án đúng? | Hai người gán độc lập, đo Kappa. Chỗ cần diễn giải (như phạm vi khoản 2 Điều 621) ghi rõ là quy ước | 12.3, `SoQuyetDinh` Q14 |
| Văn bản sửa đổi tự viết có thiên vị không? | Người hỗ trợ viết, theo cách viết thật, chốt đáp án trước khi chạy. Vẫn là rủi ro, ghi trong luận văn | 10, 12.3 |
| 54 điều có đủ để kết luận không? | Là nghiên cứu trường hợp. Phần lõi tách khỏi phần phụ thuộc lĩnh vực để dùng lại | Đề cương mục 4 |
| Độ sâu tính thế nào? | Trên văn bản, theo [9], mở rộng sang nhiều điều | 12.2 |
| Nếu (i) thắng thì sao? | Kết quả âm, vẫn báo cáo: với LLM mạnh không cần quy trình | 13.1 |
| Phần nào đúng sẵn theo cách dựng? | Tách văn bản, cạnh cấu trúc, nhận mẫu câu sửa đổi, chuỗi điều khoản, độ phủ bộ quét | 13.5 |
| Neural và symbolic kết hợp thế nào ở từng bước? | LLM: phân loại, đề xuất, trích, sửa, diễn đạt lại. Ký hiệu: mẫu câu, quét, kiểm thử, suy luận. Người: soạn vị từ đầu vào, xem mục bị cô lập. Kiểu chung: LLM đề xuất, ký hiệu kiểm | Hình 2 |
