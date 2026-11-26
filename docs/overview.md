# Tổng quan pipeline 1.1 đến 2.7, kể bằng một ví dụ xuyên suốt: Điều 35

Cách đọc: mỗi bước kể (1) bước này làm gì bằng lời thường, (2) **Điều 35 đi vào** là gì, (3) **Điều 35 đi ra** là gì, (4) vì sao làm vậy, (5) đầu ra được ai dùng. Cuối file là câu hỏi thật về Điều 35 và cách pipeline trả lời.

**Nhãn độ tin của dữ liệu ví dụ** (quan trọng, đọc trước):
- **[THẬT]**: lấy từ file đầu ra đang nằm trên đĩa (`data/processed/`), chạy ngày 15/11/2026.
- **[BẢN CŨ THẬT]**: đầu ra thật của thiết kế 1.6 cũ (cụm), dùng để thấy vì sao phải làm lại.
- **[MINH HOẠ]**: viết tay theo thiết kế đã ghi, **chưa có chương trình nào chạy ra**. Chỗ thiết kế còn mở thì ghi "chưa quyết".
- **[GIẢ ĐỊNH]**: tình huống không có thật trong kho văn bản, bịa ra để minh hoạ giai đoạn 2.

Nguồn: `docs/design/pipeline_design.md`, `docs/decisions.md` (mã quyết định A-số), `docs/design/step_1_6a_propositions.md`, `docs/run_reports/`.

---

## 0. Bức tranh chung

**Pipeline này để làm gì.** Biến Bộ luật Lao động 45/2019 thành một cơ sở tri thức (KB) mà máy suy luận được: hỏi "trong tình huống này, ngày này, có được làm X không" thì máy trả lời **có / không / chưa đủ căn cứ**, kèm điều luật làm căn cứ. Sau đó KB tự cập nhật khi có nghị định, thông tư mới (mỗi văn bản có ngày hiệu lực riêng).

**Điều 35 là gì.** "Quyền đơn phương chấm dứt hợp đồng lao động của người lao động": khoản 1 nói người lao động phải báo trước 45/30/3 ngày; khoản 2 liệt kê các trường hợp được nghỉ không cần báo trước. Nó có đủ thứ cần minh hoạ: dẫn chiếu sang Điều khác, ngoại lệ ("trừ trường hợp..."), chỗ luật giao cho Chính phủ quy định, và là loại điều hay bị hỏi có/không.

**Câu hỏi cuối cùng sẽ trả lời** (xem mục "Câu hỏi cuối"):
> Ngày 01/06/2026, bà A (làm hợp đồng không xác định thời hạn) đã đủ tuổi nghỉ hưu theo Điều 169, hai bên không có thỏa thuận gì khác. Bà A có quyền nghỉ ngay không cần báo trước không?

### Hai nguyên tắc
1. **LLM chỉ đề xuất, máy kiểm.** Mỗi bước dùng LLM đều có một "cổng" bằng máy (đoạn trích phải có nguyên văn trong luật, mã phải tồn tại, quy tắc phải biên dịch được...). Không qua cổng thì bị loại hoặc cô lập. LLM trong dự án là công cụ hỗ trợ, không phải thước đo đúng sai.
2. **Không có người duyệt giữa chuỗi**: kiểm hoàn toàn tự động.

### Ba tầng
| Tầng | Ý nghĩa | Bước |
|---|---|---|
| **Symbolic** | regex, máy trạng thái, đồ thị; không LLM; chạy lại luôn ra cùng kết quả | 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.4, 2.5, 2.7 |
| **LLM + cổng symbolic** | LLM đọc hiểu và đề xuất, máy kiểm hình dạng rồi mới nhận | 1.6A, 1.6B, 1.7, 1.8, 1.9, 2.2, 2.6 |
| **Hỗn hợp** | regex trước, LLM chỉ khi regex bó tay | 2.3 |

### Sơ đồ ngang
```
GIAI ĐOẠN 1: dựng KB gốc từ BLLĐ
[1.1 Parse]->[1.2 Dẫn chiếu]->[1.3 Điều khoản giao]->[1.4 Loại Điều]->[1.5 Ngoại lệ rõ]->[1.6A Mệnh đề]->[1.6B Sổ vị từ]->[1.7 Ngoại lệ ngầm]->[1.8 Quy tắc]->[1.9 Hỏi đáp]
 symbolic     symbolic        symbolic           symbolic         symbolic            LLM+cổng        LLM+cổng        LLM+cổng          LLM+cổng      LLM+cổng
 ĐÃ LÀM       ĐÃ LÀM          ĐÃ LÀM             ĐÃ LÀM           ĐÃ LÀM              ĐANG LÀM LẠI    CHƯA (sửa)      CHƯA CODE         CHƯA CODE     CHƯA BÀN

GIAI ĐOẠN 2: update engine, mỗi văn bản mới d một lần
[2.1 Xử lý VB mới]->[2.2 Nối vào KB]->[2.3 Đọc chỉ thị]->[2.4 Áp chỉ thị]->[2.5 Tập ảnh hưởng]->[2.6 Trích lại]->[2.7 Đối chứng]
 symbolic(tái dùng)   LLM+cổng         regex rồi LLM      symbolic          symbolic             LLM+cổng        symbolic
 CÓ CODE              CÓ CODE          CÓ CODE            CÓ CODE           CHƯA CÓ              CHƯA CÓ         CHƯA CÓ
```

### Bảng trạng thái
| Bước | Tên | Trạng thái |
|---|---|---|
| 1.1 | Parse | ĐÃ LÀM; còn 1 lỗi đã biết |
| 1.2 | Dẫn chiếu | ĐÃ LÀM; còn nợ |
| 1.3 | Điều khoản giao | ĐÃ LÀM |
| 1.4 | Loại Điều | ĐÃ LÀM |
| 1.5 | Ngoại lệ tường minh | ĐÃ LÀM |
| 1.6A | Gạch mệnh đề | thiết kế mới + code + test có; bản cũ (cụm) đã chạy xong 204/204 lô; **chưa chạy bản mới** |
| 1.6B | Sổ vị từ | **chưa có sổ dùng được**; code cũ đọc "cụm" phải sửa đọc "mệnh đề" |
| 1.7, 1.8 | Ngoại lệ ngầm, Quy tắc | chưa code, có bản nháp, còn câu mở |
| 1.9 | Hỏi đáp theo ngày | chưa bàn (một dòng trong bảng) |
| 2.1 đến 2.4 | | có code cũ, đã chạy; chưa bàn lại theo thiết kế mới |
| 2.5 đến 2.7 | | chưa có, chưa bàn |

---

# GIAI ĐOẠN 1

## 1.1 Parse: cắt văn bản thành đơn vị có mã
**Tầng symbolic. ĐÃ LÀM** (`src/parse.py`).

**Kể chuyện.** File luật là một chuỗi dòng chữ. Bước này đọc từng dòng, nhận ra dòng nào bắt đầu một Chương, Mục, Điều, Khoản hay Điểm (bằng dạng chữ ở đầu dòng: "Điều 35.", "1.", "a)"), rồi cho mỗi thứ một **mã** và ghi nó thuộc cái gì. Giống đánh số mục lục cho cả cuốn luật.

**Điều 35 đi vào.** Các dòng chữ thô của luật:
```
Điều 35. Quyền đơn phương chấm dứt hợp đồng lao động của người lao động
1. Người lao động có quyền đơn phương chấm dứt hợp đồng lao động nhưng phải báo trước cho người sử dụng lao động như sau:
a) Ít nhất 45 ngày nếu làm việc theo hợp đồng lao động không xác định thời hạn;
...
2. Người lao động có quyền đơn phương chấm dứt hợp đồng lao động không cần báo trước trong trường hợp sau đây:
a) Không được bố trí theo đúng công việc, địa điểm làm việc hoặc không được bảo đảm điều kiện làm việc theo thỏa thuận, trừ trường hợp quy định tại Điều 29 của Bộ luật này;
...
e) Đủ tuổi nghỉ hưu theo quy định tại Điều 169 của Bộ luật này, trừ trường hợp các bên có thỏa thuận khác;
```

**Điều 35 đi ra. [THẬT]** Mỗi đơn vị là vài dòng `{đơn vị, thuộc tính, giá trị}`:
```
D35        type=dieu   heading="Quyền đơn phương chấm dứt hợp đồng lao động của người lao động"   parent=CIII.M3 (Chương III, Mục 3)
D35.K1     type=khoan  parent=D35   text="Người lao động có quyền đơn phương chấm dứt hợp đồng lao động nhưng phải báo trước ... như sau:"
D35.K1.a   type=diem   parent=D35.K1   text="Ít nhất 45 ngày nếu làm việc theo hợp đồng lao động không xác định thời hạn;"
D35.K1.d   type=diem   parent=D35.K1   text="Đối với một số ngành, nghề, công việc đặc thù thì thời hạn báo trước được thực hiện theo quy định của Chính phủ."
D35.K2     type=khoan  parent=D35   text="Người lao động có quyền ... không cần báo trước trong trường hợp sau đây:"
D35.K2.a   type=diem   parent=D35.K2   text="Không được bố trí theo đúng công việc, ... trừ trường hợp quy định tại Điều 29 của Bộ luật này;"
D35.K2.dd  (điểm "đ")  D35.K2.e   text="Đủ tuổi nghỉ hưu theo quy định tại Điều 169 ..., trừ trường hợp các bên có thỏa thuận khác;"
```
(Mã đầy đủ có tiền tố `BLLD_45-2019.`. Điểm "đ" viết là `dd`. Điều 35 có 2 khoản, 4 điểm ở khoản 1 và 7 điểm ở khoản 2.)

**Vì sao làm vậy.** Mọi bước sau cần chỉ vào "đúng khoản 2 điểm e của Điều 35" mà không nhầm. Dùng máy trạng thái thay vì LLM vì cấu trúc luật đều đặn và kiểm được bằng số đếm.

**Máy tự kiểm.** Số Điều khớp bảng văn bản (220 = 220); số thứ tự liền (không nhảy từ điểm c sang điểm e); mỗi đơn vị đúng một cha; mã không trùng. Lệch là dừng, không ghi file.

**Ai dùng đầu ra.** Gần như mọi bước: 1.2 tìm dẫn chiếu trong chữ; 1.4 đọc tiêu đề; 1.6 lấy chữ để gạch mệnh đề.

**Số liệu BLLĐ.** 1166 đơn vị (17 Chương, 24 Mục, 220 Điều, 638 Khoản, 267 Điểm); 0 lỗi parse; 18 văn bản trong kho đều qua.
**Lỗi đã biết, chưa sửa.** Đoạn chữ không có ký hiệu điểm nằm giữa hai điểm bị gắn nhầm vào khoản cha (ca chắc chắn: `D36.K1`).

---

## 1.2 Dẫn chiếu: ai nhắc tới ai
**Tầng symbolic. ĐÃ LÀM** (`src/refs.py`).

**Kể chuyện.** Luật hay viết "theo quy định tại Điều 29", "khoản 4 Điều 97". Bước này tìm các cụm đó bằng mẫu chữ, rồi **giải ra mã đích** thật. Cụm nào máy không chắc đích thì ghi "không giải được", không đoán. Bước này cũng lấy luôn quan hệ cha-con (Điều chứa khoản, khoản chứa điểm) từ bước 1.1.

**Điều 35 đi vào.** Chữ các đơn vị của Điều 35 (từ 1.1).

**Điều 35 đi ra. [THẬT]** Sáu cạnh `refers_to` xuất phát từ Điều 35, mỗi cạnh kèm câu nguyên văn làm bằng chứng:
```
D35.K2.a   -> D29        "Điều 29 của Bộ luật này"
D35.K2.b   -> D97.K4     "khoản 4 Điều 97 của Bộ luật này"
D35.K2.dd  -> D138.K1    "khoản 1 Điều 138 của Bộ luật này"
D35.K2.e   -> D169       "Điều 169 của Bộ luật này"
D35.K2.g   -> D16.K1     "khoản 1 Điều 16 của Bộ luật này"
```
Và hai cạnh đi ngược vào Điều 35: `D34.K9 -> D35` ("Điều 35 của Bộ luật này") và `D39 -> D35` ("điều 35, 36 và 37 của Bộ luật này").
Cạnh cha-con, ví dụ: `D35.K2 contains D35.K2.b` và `D35.K2.b part_of D35.K2`.

**Vì sao làm vậy.** Điều luật không đứng riêng: câu hỏi về Điều 35 có thể phải đọc cả Điều 29 và Điều 169. Có cạnh dẫn chiếu thì sau này (1.6, 1.8, 2.5) đi từ điểm này sang điểm kia được. Thà ghi "không giải được" còn hơn đoán sai âm thầm, vì một cạnh sai sẽ lan xuống ngoại lệ và quy tắc.

**Máy tự kiểm.** Mỗi cụm có đúng một kết cục (nối / chờ đích / không giải được); không cạnh nào trỏ tới mã không tồn tại; câu bằng chứng phải nằm nguyên văn trong đơn vị.

**Ai dùng đầu ra.** 1.5 lấy đích để dựng ngoại lệ; 1.6 gắn đích vào mệnh đề; 2.5 dùng để biết Điều nào bị ảnh hưởng khi một Điều đổi.

**Số liệu BLLĐ.** 186 cụm dẫn chiếu thành 245 cạnh `refers_to`; 1 cạnh "chờ đích" (trỏ sang Bộ luật Tố tụng hình sự, chưa có trong kho); 0 không giải được. 7 dòng chỉ thị sửa đổi trong Điều 219 được bỏ qua (việc của 2.3).
**Nợ.** Dẫn chiếu tới cả Mục hoặc Chương chưa giải.

---

## 1.3 Điều khoản giao: chỗ luật để trống cho cấp dưới
**Tầng symbolic. ĐÃ LÀM** (`src/delegation.py`).

**Kể chuyện.** Có chỗ luật không tự quy định hết mà viết "do Chính phủ quy định", "Bộ trưởng quy định". Đó là một **chỗ trống**: câu trả lời đầy đủ nằm ở nghị định hay thông tư sau. Bước này đánh dấu mọi chỗ trống như vậy, để sau biết "chỗ này luật chưa nói hết".

**Điều 35 đi vào.** Chữ các đơn vị.

**Điều 35 đi ra. [THẬT]** Một điều khoản giao, ở điểm d khoản 1:
```
{"clause_id":"DC_D35_K1_d_1", "unit_id":"D35.K1.d", "pattern":"B",
 "delegate":"Chính phủ", "phrase":"theo quy định của Chính phủ"}
```
Nghĩa: "Đối với một số ngành, nghề, công việc đặc thù thì thời hạn báo trước được thực hiện **theo quy định của Chính phủ**". Luật không nói là bao nhiêu ngày.

**Vì sao làm vậy.** Nếu có người hỏi "phi công phải báo trước mấy ngày?", chỉ đọc Điều 35 thì không trả lời được. Máy phải biết đây là chỗ trống để (a) tìm văn bản lấp chỗ trống (2.2), (b) trả "chưa đủ căn cứ" thay vì đoán khi chưa có văn bản lấp (1.9).

**Máy tự kiểm.** Các mốc đã biết phải đạt (D91.K4, D154.K1/K2/K9, D142.K1, D112: cả bốn đạt). Số đếm là regex thô, chưa lọc ca không phải giao chi tiết thật; ca nghi ngờ mang cờ `loose`.

**Ai dùng đầu ra.** 2.2 (nối nghị định vào đúng chỗ trống), và dự kiến 1.9.

**Số liệu BLLĐ.** 51 điều khoản giao chắc (dạng A 35, B 10, D 5, E 1) và 5 ca lỏng cần người xem.

---

## 1.4 Loại Điều: Điều nào đáng trích quy tắc
**Tầng symbolic. ĐÃ LÀM** (`src/article_type.py`; từ 11/11 không dùng LLM).

**Kể chuyện.** Không phải Điều nào cũng chứa quy tắc nội dung. "Giải thích từ ngữ", "Hiệu lực thi hành", "Hồ sơ, thủ tục" là loại khác. Bước này dán nhãn mỗi Điều bằng cách khớp mẫu chữ trên **tiêu đề**; không khớp mẫu nào thì mặc định là `substantive` (nội dung), để không bỏ sót quy tắc.

**Điều 35 đi vào.** Tiêu đề "Quyền đơn phương chấm dứt hợp đồng lao động của người lao động".

**Điều 35 đi ra. [THẬT]**
```
{"id":"BLLD_45-2019.D35", "label":"substantive", "how":"default"}
```

**Vì sao làm vậy.** Các bước tốn LLM (1.6, 1.8) chỉ chạy trên Điều `substantive` và `definition` để tiết kiệm và tránh trích quy tắc từ điều khoản hiệu lực. Nhãn `effect_transition` còn là nơi 2.3 tìm câu chỉ thị sửa đổi.

**Số liệu BLLĐ.** 220 Điều: 203 substantive, 1 definition, 8 authority, 6 procedural, 2 effect_transition.

---

## 1.5 Ngoại lệ tường minh: "trừ trường hợp..."
**Tầng symbolic. ĐÃ LÀM** (`src/exceptions_explicit.py`, `src/exceptions_general.py`).

**Kể chuyện.** Khi luật viết "..., trừ trường hợp X", thì quy tắc đó **không áp dụng** nếu X xảy ra. Bước này bắt các chữ "trừ" và "không áp dụng", rồi nối một cạnh `exception_of` (ngoại lệ của) từ phần ngoại lệ tới quy tắc bị ngoại trừ. Khi X là một điều kiện chung chung ("các bên có thỏa thuận khác") thì tạo một **nút điều kiện** riêng; câu giống nhau được gộp thành một nút. Nút có ba loại: `cu_the` (nói rõ), `tuy_nghi` ("các bên thỏa thuận khác"), `dan_chieu_mo` ("pháp luật có quy định khác").

**Điều 35 đi vào.** Chữ có "trừ trường hợp" ở K2.a, K2.b, K2.e và cách giải dẫn chiếu của 1.2.

**Điều 35 đi ra. [THẬT]** Ba nút điều kiện và năm cạnh:
```
nút X1162b718 (cu_the)   "quy định tại Điều 29 của Bộ luật này"          áp cho D35.K2.a
nút Xd5c6dd73 (cu_the)   "quy định tại khoản 4 Điều 97 của Bộ luật này"  áp cho D35.K2.b
nút X798cfde0 (tuy_nghi) "các bên có thỏa thuận khác"                    áp cho D35.K2.e, D70.K2, D83, D207.K2

X1162b718  exception_of  D35.K2.a     (bằng chứng: "trừ trường hợp quy định tại Điều 29 của Bộ luật này")
D29        exception_of  D35.K2.a     (vì X dẫn chiếu Điều 29, nên chính Điều 29 cũng là ngoại lệ)
Xd5c6dd73  exception_of  D35.K2.b
D97.K4     exception_of  D35.K2.b
X798cfde0  exception_of  D35.K2.e
```
Đọc cạnh cuối: "các bên có thỏa thuận khác" là ngoại lệ của quyền nghỉ không báo trước khi đủ tuổi nghỉ hưu.

**Vì sao làm vậy.** Ngoại lệ quyết định quy tắc nào bị chặn. Nếu bỏ qua, máy sẽ kết luận "bà A được nghỉ ngay" kể cả khi hai bên đã thỏa thuận khác. Phải có cạnh này thì 1.8 mới nối được quan hệ "quy tắc bị chặn bởi ngoại lệ".

**Máy tự kiểm.** Mỗi chỗ có "trừ" hoặc "không áp dụng" phải thuộc đúng một trong hai: đã tạo cạnh, hoặc ghi "chưa xử lý" (không đoán); câu bằng chứng là chuỗi con nguyên văn.

**Ai dùng đầu ra.** 1.6 thêm cụm ngoại lệ từ nút điều kiện; 1.7 bỏ qua cặp đã có cạnh; 1.8 dựng quan hệ chặn; 1.9 phân biệt "bị bác" với "chưa đủ căn cứ".

**Số liệu BLLĐ.** 45 chỗ có "trừ"/"không áp dụng": 43 đã tạo cạnh, 2 chưa xử lý (một "không áp dụng" thiếu dẫn chiếu, một ngoại lệ liệt kê ở các điểm con). 34 nút điều kiện (30 cu_the, 3 tuy_nghi, 1 dan_chieu_mo); 66 cạnh `exception_of`.

---

## 1.6A Gạch mệnh đề: tách mỗi điều luật thành các ý nhỏ kiểm được đúng/sai
**Tầng LLM + cổng symbolic. ĐANG LÀM LẠI** (`src/propositions.py`, thiết kế `docs/design/step_1_6a_propositions.md`, quyết định A38 và A39; chưa nối vào `run_all`).

**Kể chuyện.** Từ đây máy bắt đầu **hiểu nghĩa**. LLM đọc từng khoản, điểm và rút ra các ý nhỏ nhất mà luật đang nói: ai, được/phải/cấm làm gì, với điều kiện gì. Mỗi ý là một **mệnh đề**. LLM bắt buộc kèm đoạn chữ nguyên văn (`trich`) làm bằng chứng; đoạn đó không có trong luật thì máy loại.

Mỗi mệnh đề có: `vai` (là điều kiện hay kết luận), `chu_the` (ai), `phuong_thuc` (được / phải / cấm / không áp dụng / không), `cuc` (khẳng định / phủ định), và `trich`. Ngoài ra có ba loại dòng khác: `con_tro` (chỗ dẫn chiếu hoặc ngoại lệ), `bo_qua` (câu dẫn như "trong trường hợp sau đây:", ghi lý do), `chua_ro` (LLM không chắc thì ghi câu hỏi, không đoán).

**Điều 35 đi vào.** Chữ của 881 đơn vị BLLĐ trong Điều `substantive`/`definition`, mỗi đơn vị kèm **ngữ cảnh**: tiêu đề Điều + câu dẫn của khoản cha + chữ chính nó. Cần câu dẫn vì điểm e (K2.e) chỉ nói "Đủ tuổi nghỉ hưu...", còn chủ thể ("người lao động") và kết luận ("có quyền nghỉ không cần báo trước") nằm ở câu dẫn K2. Cũng nhận dẫn chiếu của 1.2 và nút điều kiện của 1.5.

**Bản cũ làm gì sai. [BẢN CŨ THẬT]** Bản cũ gạch "cụm" theo bốn vai. Ở điểm K2.a:
```
K2.a  dieu_kien  "Không được bố trí theo đúng công việc, địa điểm làm việc HOẶC không được bảo đảm điều kiện làm việc theo thỏa thuận"   <- hai điều kiện dính một cụm
K2.a  ngoai_le   "quy định tại Điều 29 của Bộ luật này"   targets=[D29]
K2.a  chu_the    "Người lao động"                                     (chép từ câu dẫn)
K2.a  ket_luan   "có quyền đơn phương chấm dứt hợp đồng lao động không cần báo trước"   (chép từ câu dẫn, lặp lại ở MỌI điểm a, b, c...)
```
Hậu quả: cụm dài và ghép nhiều ý nên đặt tên vị từ xong **không tái dùng được ở điều khác**; kết luận bị chép lặp ở từng điểm. Đó là lý do làm lại.

**Điều 35 đi ra, bản mới. [MINH HOẠ]** (chưa có LLM nào chạy ra; viết tay đúng theo luật đã ghi):
```
D35.K2    menh_de  ket_luan   "đơn phương chấm dứt hợp đồng lao động không cần báo trước"
                              chu_the="Người lao động" (loại W, lấy từ chính nó)   phuong_thuc=duoc   cuc=khang_dinh
                              trich=["Người lao động có quyền đơn phương chấm dứt hợp đồng lao động không cần báo trước"]
D35.K2    bo_qua   ly_do=cau_dan, cac_muc_con=hoac   trich=["trong trường hợp sau đây:"]   (các điểm con là điều kiện "hoặc")

D35.K2.a  menh_de  dieu_kien  "được bố trí theo đúng công việc, địa điểm làm việc"   phuong_thuc=khong  cuc=phu_dinh  nhom_hoac=D35.K2.a#h1
D35.K2.a  menh_de  dieu_kien  "được bảo đảm điều kiện làm việc theo thỏa thuận"       phuong_thuc=khong  cuc=phu_dinh  nhom_hoac=D35.K2.a#h1
D35.K2.a  con_tro  ngoai_le   targets=[D29]   how=cond_node   trich=["trừ trường hợp quy định tại Điều 29 của Bộ luật này"]

D35.K2.e  menh_de  dieu_kien  "đủ tuổi nghỉ hưu"   chu_the="Người lao động" (lấy từ câu dẫn)   phuong_thuc=khong  cuc=khang_dinh
D35.K2.e  con_tro  dan_chieu  targets=[D169]   gan_vao=dòng "đủ tuổi nghỉ hưu"
D35.K2.e  con_tro  ngoai_le   how=cond_node (nút tuy_nghi)   trich=["trừ trường hợp các bên có thỏa thuận khác"]
```
Ba điểm cần để ý:
- Kết luận chỉ ghi **một lần** ở D35.K2, không chép xuống từng điểm. Các điểm chỉ chứa điều kiện.
- "Không được bố trí..." ở K2.a nghĩa là "người lao động *không được* người sử dụng bố trí đúng", nên ghi `phuong_thuc=khong` + `cuc=phu_dinh`, **không phải** "cấm". Chỗ này máy không tự phân biệt được, phải dựa vào cách LLM đọc.
- Hai điều kiện nối bằng "hoặc" ở K2.a được **tách làm hai mệnh đề** nhưng gom chung một `nhom_hoac`, để 1.8 biết chỉ cần một trong hai đúng.

**Vì sao tách theo mệnh đề.** Tiêu chí đã chốt (A38): **tách** khi từng phần kiểm được đúng/sai độc lập và vi phạm từng phần có ý nghĩa pháp lý riêng; **giữ chung** khi là yêu cầu tập thể. Mục đích: mệnh đề đủ ngắn để hai điều luật khác nhau nói cùng một ý thì cho ra cùng một vị từ ở 1.6B.

**Cổng máy kiểm.** Khuôn dòng đúng; `trich` là chuỗi con nguyên văn của ngữ cảnh; **cổng âm tiết**: mọi âm tiết của `menh_de` phải có trong `trich` của chính dòng (chặn LLM bịa chữ); chủ thể lấy từ câu dẫn thì `trich` phải chứa mẩu câu dẫn đó; `con_tro` có `targets` nằm trong dẫn chiếu của 1.2; `bo_qua` phải có lý do. Cờ cảnh báo: mệnh đề còn chữ phương thức, mệnh đề dài từ 15 âm tiết.

**Ai dùng đầu ra.** 1.6B đặt tên vị từ cho từng mệnh đề; 1.7 và 1.8 đọc mệnh đề để tìm ngoại lệ ngầm và viết quy tắc.

**Đã thử được gì.** Thử 16 lô trên cùng bộ lời nhắc:
| Cách chạy | Lỗi cổng | Nhận xét |
|---|---|---|
| Sonnet qua Claude Code | 0 / 100 dòng | tốt nhất, nhưng quá tốn token |
| Gemini 3.5 flash-lite | 26 / 79 dòng | rẻ, nhanh; có bịa đích dẫn chiếu và chủ thể |
| Gemini 3.8 flash | 17 / 79 dòng | không bịa, lỗi chủ yếu là thiếu mẩu câu dẫn trong `trich`; chỉ 20 lượt/ngày |

**Chưa làm.** Chưa chạy đủ 204 lô. Đường chạy đã chốt (A39): Sonnet 5.5 qua phiên Claude Code, lời nhắc `menh-de-3` đóng băng, dừng sau 60 lô đầu nếu có câu dẫn lọt thành mệnh đề hoặc lỗi cổng còn lại vượt 5% số dòng. Gemini không được dùng cho 204 lô vì tỉ lệ lỗi cổng cao hơn trên mẫu thử.

---

## 1.6B Sổ vị từ: đặt tên cho mệnh đề để các điều luật nối được với nhau
**Tầng LLM + cổng symbolic. CHƯA CÓ sổ dùng được** (`src/concepts_names.py` đọc "cụm", phải sửa đọc "mệnh đề").

**Kể chuyện.** Điều 35 nói "đủ tuổi nghỉ hưu" ở một chỗ; Điều 169 nói "đến tuổi nghỉ hưu" ở chỗ khác. Với máy, hai chuỗi chữ khác nhau là hai thứ khác nhau. Bước này cho mỗi mệnh đề một **tên vị từ** ngắn bằng tiếng Anh (như tên hàm), và ép **tái dùng** tên đã có khi cùng nghĩa. Hai điều luật dùng chung một vị từ thì máy biết chúng nói về cùng một chuyện, và đó là cách các điều luật rời rạc được **nối lại**.

Phân loại vị từ: `concept` (khái niệm pháp lý, có thể suy ra) và `input` (dữ kiện do người hỏi khai, máy không tự suy).

**Điều 35 đi vào.** Các mệnh đề của 1.6A, xử lý lần lượt theo thứ tự Điều để tên đặt trước được tái dùng ở sau.

**Điều 35 đi ra.** Tên thật từ bản cũ có thể dùng làm ví dụ về **tái dùng**: [BẢN CŨ THẬT]
```
"Người lao động"                                                     -> employee_under_labor_code(W)       dùng lại ở nhiều đơn vị
"có quyền đơn phương chấm dứt hợp đồng lao động không cần báo trước"  -> right_to_terminate_without_prior_notice(C)   dùng chung ở K2, K2.a, K2.e...
```
Với mệnh đề mới [MINH HOẠ, tên đặt tay; chưa quyết]:
```
"đơn phương chấm dứt hợp đồng lao động không cần báo trước"  -> may_terminate_without_notice(W)      concept
"được bố trí theo đúng công việc, địa điểm làm việc"          -> assigned_per_agreed_job_and_place(W)  concept   (phủ định nằm ở trường cuc, KHÔNG viết "not_..." trong tên)
"đủ tuổi nghỉ hưu"                                             -> reached_retirement_age(W)             input
"các bên có thỏa thuận khác"                                   -> parties_agree_otherwise(W)            input
```

**Vì sao ở sau 1.6A.** Tên vị từ chỉ tái dùng được khi mệnh đề đủ ngắn và chỉ một ý. Bản cũ dựng trên cụm dài nên chỉ tái dùng 55/1833 chữ, tức tên mới tràn lan (1778 vị từ mới). Số này là lý do chính làm lại 1.6A.

**Cổng máy kiểm.** Tên đúng dạng; khai "mới" mà trùng tên có sẵn thì loại; cấm tiền tố `not_` (phủ định để ở `cuc`); số tham số nhất quán.

**Ai dùng đầu ra.** 1.7 dựng cặp ứng viên (hai đơn vị cùng dùng một vị từ); 1.8 tính tập vị từ được phép cho mỗi Điều.

---

## 1.7 Ngoại lệ ngầm: quan hệ ngoại lệ mà luật không viết chữ "trừ"
**Tầng LLM + cổng symbolic. CHƯA CODE** (bản nháp, quyết định A32).

**Kể chuyện.** 1.5 chỉ bắt được ngoại lệ có chữ "trừ". Nhưng nhiều ngoại lệ chỉ nằm ở nghĩa. Bước này tìm các **cặp đơn vị cùng nói về một vị từ**, rồi hỏi LLM: "cặp này, có cái nào là ngoại lệ của cái kia không?". LLM trả `a_exception_of_b`, `b_exception_of_a` hoặc `none`, kèm câu bằng chứng nguyên văn. Cạnh nhận được mang cờ `llm_proposed`.

**Điều 35 đi vào.** Vị từ của 1.6B; 66 cạnh của 1.5. Máy dựng cặp ứng viên: hai đơn vị cùng dùng một vị từ loại `concept`, bỏ cặp đã có cạnh ở 1.5.

**Điều 35 đi ra. [MINH HOẠ]**
```
cặp (D35.K1, D35.K2)   chung vị từ: unilateral_termination_by_employee
  LLM: b_exception_of_a   bằng chứng: "không cần báo trước"
  nghĩa: khoản 2 (không cần báo trước) là ngoại lệ của khoản 1 (phải báo trước)
  -> cạnh {s: D35.K2, p: exception_of, o: D35.K1, how: llm, flags: [llm_proposed]}

cặp (D35.K2.d, D35.K2.g)   cùng dẫn đến kết luận "được nghỉ không cần báo trước"
  LLM: none   (hai trường hợp độc lập, không phải ngoại lệ của nhau)
  -> chỉ ghi vào file pairs, không tạo cạnh
```

**Vì sao cần.** Thiếu cạnh thì 1.9 sẽ trả "bà A phải báo trước 45 ngày" trong khi K2.e cho nghỉ ngay. Thừa cạnh thì chặn oan quy tắc đúng.

**Cổng máy kiểm.** `answer` hợp lệ; câu bằng chứng là chuỗi liền trong ngữ cảnh; hai đầu tồn tại; không trùng cạnh 1.5; không tạo vòng. Máy kiểm hình dạng, **không chứng minh** quan hệ ngoại lệ có thật.

**Phụ thuộc.** Cần 1.6B xong. Tái dùng vị từ sót thì cặp sót.
**Chưa quyết.** Phân biệt hai dạng ngoại lệ (tạo kết luận ngược / chỉ loại trừ việc áp dụng) và ai gán dạng.

---

## 1.8 Quy tắc: dịch luật thành quy tắc máy suy luận được
**Tầng LLM + cổng symbolic. CHƯA CODE** (bản nháp, quyết định A33; công cụ suy luận s(CASP) đã cài và chạy được).

**Kể chuyện.** LLM viết quy tắc dạng logic (s(CASP)) cho mỗi đơn vị, chỉ được dùng các vị từ của 1.6B; thiếu vị từ thì gắn cờ chứ không tự đặt tên. Máy nối ngoại lệ thành quan hệ **chặn** ("quy tắc này không chạy nếu ngoại lệ kia đúng"), quét lỗi, và cho LLM tự sửa tối đa 2 vòng nếu không biên dịch được. Không đạt thì **cô lập** quy tắc đó (giữ lại nhưng không dùng để trả lời).

**Điều 35 đi vào.** Chữ đơn vị, sổ vị từ (1.6B), cạnh `exception_of` (1.5, 1.7).

**Điều 35 đi ra. [MINH HOẠ, chưa quyết]** (viết tay để thấy hình dạng; cú pháp s(CASP) chưa kiểm chạy):
```
% từ D35.K2 (kết luận) + D35.K2.e (điều kiện) + nút "các bên thỏa thuận khác" (ngoại lệ)
may_terminate_without_notice(W) :-
    employee_under_labor_code(W),
    reached_retirement_age(W),
    not parties_agree_otherwise(W).

% từ D35.K1.a (báo trước 45 ngày với hợp đồng không xác định thời hạn)
must_notify_days(W, 45) :-
    employee_under_labor_code(W),
    indefinite_term_contract(W),
    not may_terminate_without_notice(W).     % K2 chặn K1 (cạnh 1.7)
```
Chữ `not` là phủ định theo kiểu "không chứng minh được". Dòng cuối là chỗ ngoại lệ biến thành quan hệ chặn.

**Máy kiểm.** Biên dịch được; chỉ dùng vị từ được phép và đúng số tham số; bộ quét sạch (quy tắc không bao giờ kích hoạt, trùng lặp, vòng chặn lẫn nhau, cặp kết luận ngược không có quan hệ chặn). **Không chứng minh được quy tắc dịch đúng nghĩa luật.**

**Còn mở.** (a) 43/66 cạnh ngoại lệ của 1.5 đi từ nút điều kiện chứ không phải đơn vị luật: nút `tuy_nghi` như "các bên thỏa thuận khác" chưa có cách đưa vào quy tắc (ví dụ trên là một cách có thể, chưa duyệt); (b) ngoại lệ lồng nhau (ngoại lệ của ngoại lệ), chưa thiết kế, là đóng góp chính của luận văn; (c) "bị bác" cần quy tắc kết luận phủ định, mà 1.6 đã loại phủ định; (d) hai dạng ngoại lệ chưa quyết.
**Hoãn sang giai đoạn 2.** Xử lý xung đột theo thứ bậc văn bản (Điều 58).

---

## 1.9 Hỏi đáp theo ngày: dùng KB để trả lời
**Tầng LLM + cổng symbolic. CHƯA BÀN** (chỉ có một dòng trong `docs/design/pipeline_design.md`).

**Kể chuyện (theo dòng đó).** LLM đổi câu hỏi tiếng Việt thành các **dữ kiện** logic. Máy lấy tập quy tắc Π_τ (quy tắc có phiên bản đang hiệu lực tại ngày τ và không bị cô lập), rồi chạy hai lần: chứng minh φ (câu trả lời có) và chứng minh ¬φ (câu trả lời không). Từ hai kết quả đó ra **bốn loại đáp án**:
| Kết quả | Nghĩa |
|---|---|
| kết luận được | φ chứng minh được, ¬φ thì không |
| bị bác | ¬φ chứng minh được (vì ngoại lệ hoặc quy tắc phủ định) |
| chưa đủ căn cứ | thiếu dữ kiện, hoặc chỗ trống chưa có văn bản lấp |
| không trả lời | câu hỏi dính một mục bị cô lập |

Chi tiết (dữ kiện đổi ra sao, bộ câu hỏi, cách chấm) **chưa có thiết kế**. Ví dụ ở cuối file là minh hoạ.

---

# GIAI ĐOẠN 2: cập nhật khi có văn bản mới

**Kể chuyện chung.** BLLĐ có hiệu lực từ 01/01/2021. Sau đó nghị định, thông tư lần lượt ra đời với ngày hiệu lực riêng. Mỗi văn bản mới `d` là một **sự kiện nạp**: KB phải biết thêm gì, đóng phiên bản nào, mở phiên bản nào, và chỉ làm lại phần bị ảnh hưởng. Nguyên tắc **không xoá gì**: phiên bản cũ chỉ được đóng bằng ngày hết hiệu lực, để hỏi được "ngày 15/01/2021 thì luật nói gì".

Văn bản nào chạm Điều 35?
- **[THẬT]** Nghị định 145/2020 (hiệu lực 01/02/2021) lấp chỗ trống ở D35.K1.d. Dùng cho 2.1 và 2.2.
- **[THẬT]** Không văn bản nào trong kho **sửa trực tiếp** Điều 35. Luật sửa đổi BLLĐ đang ở kỳ họp Quốc hội, chưa có trong kho.
- **[GIẢ ĐỊNH]** Vì vậy từ 2.3 trở đi, tài liệu dùng một văn bản giả sửa Điều 35 để minh hoạ. Nhãn [GIẢ ĐỊNH] đánh dấu phần này.

## 2.1 Xử lý văn bản mới
**Tầng symbolic (tái dùng 1.1 đến 1.5). Chưa bàn lại.**

**Kể chuyện.** Văn bản mới đi qua đúng các bước 1.1 đến 1.5 như BLLĐ: cắt đơn vị, dẫn chiếu, điều khoản giao, nhãn Điều, ngoại lệ. Vì thế 1.1 đến 1.5 phải viết kiểu "xử lý một văn bản bất kỳ".

**Điều 35 liên quan thế nào. [THẬT]** Nghị định 145/2020 sinh 929 đơn vị. Điều 7 của nó tên "Ngành, nghề, công việc đặc thù và thời hạn báo trước khi đơn phương chấm dứt hợp đồng lao động quy định tại điểm d khoản 1 Điều 35 và điểm d khoản 2 Điều 36 của Bộ luật Lao động". Nội dung:
```
ND_145-2020.D7.K1.a  Thành viên tổ lái tàu bay; nhân viên kỹ thuật bảo dưỡng tàu bay, ... nhân viên điều độ, khai thác bay;
ND_145-2020.D7.K1.b  Người quản lý doanh nghiệp theo quy định của Luật Doanh nghiệp; ...
ND_145-2020.D7.K1.c  Thuyền viên thuộc thuyền bộ làm việc trên tàu Việt Nam đang hoạt động ở nước ngoài; ...
ND_145-2020.D7.K2.a  Ít nhất 120 ngày đối với hợp đồng lao động không xác định thời hạn hoặc ... xác định thời hạn từ 12 tháng trở lên;
ND_145-2020.D7.K2.b  Ít nhất bằng một phần tư thời hạn của hợp đồng lao động đối với hợp đồng lao động có thời hạn dưới 12 tháng.
```
Đây chính là câu trả lời cho "chỗ trống" mà 1.3 đã đánh dấu ở D35.K1.d.

## 2.2 Nối vào KB
**Tầng LLM + cổng symbolic. Có code cũ, đã chạy live (`src/links.py`), chưa bàn lại.**

**Kể chuyện.** Văn bản mới phải được **gắn** vào KB: nó căn cứ vào văn bản nào (`based_on`), nó hướng dẫn chi tiết cho điều nào của luật (`details`), và nó lấp chỗ trống nào ở 1.3. Khi văn bản nêu rõ "điểm d khoản 1 Điều 35" thì regex nối ngay. Khi chỉ nói chung chung thì **hai LLM độc lập** chọn trong danh sách điều khoản giao, và chỉ giữ khi cả hai chọn giống nhau **và** từ khoá của Điều đích có xuất hiện; bất đồng thì cô lập.

**Điều 35 đi ra. [THẬT]**
```
{"s":"ND_145-2020", "p":"details", "o":"BLLD_45-2019.D35.K1.d", "how":"regex", "evidence":"điểm d khoản 1 Điều 35", "flags":[]}
{"clause_id":"DC_D35_K1_d_1", "filled_by":["ND_145-2020"]}      <- chỗ trống của 1.3 giờ đã có người lấp
```
**Vì sao.** Không có bước này thì Điều 7 ND_145 chỉ là một văn bản rời; 1.9 không biết "120 ngày" là câu trả lời cho chỗ trống ở D35.K1.d.
**Số liệu.** 10 cạnh `based_on`, 48 `details`, 18 chờ đích; 40/51 điều khoản giao đã có văn bản lấp; mọi mốc cổng đạt.

## 2.3 Đọc chỉ thị
**Tầng hỗn hợp: regex trước, LLM chỉ khi regex bó tay, rồi cổng symbolic. Có code cũ (`src/directives.py`), chưa bàn lại.**

**Kể chuyện.** Văn bản sửa đổi viết các câu mệnh lệnh: "Sửa đổi, bổ sung điểm a khoản 1 Điều 35 như sau:", "Bãi bỏ khoản 3 Điều 8", "thay cụm từ...". Bước này đọc câu đó thành một **chỉ thị có cấu trúc**: loại thao tác (thay thế, sửa, bãi bỏ, bổ sung...), đích, và nội dung mới (lấy từ khối trích dẫn “...” đã tách ở 1.1). Regex bắt trước. Không bắt được thì LLM đề xuất loại thao tác, rồi máy kiểm lại. Vẫn không xếp được thì ghi "chưa xác định" và **cô lập đơn vị bị chạm** (an toàn hơn đoán).

**[THẬT] Với ND_145:** không có chỉ thị nào chạm Điều 35 (nhật ký sự kiện: `units_touched: []`, `unknown_directive: []`). ND_145 chỉ thêm đơn vị mới, không sửa gì.

**[GIẢ ĐỊNH] Văn bản "NĐ giả 2027", hiệu lực 01/01/2027, Điều 1 viết:**
```
"Sửa đổi điểm a khoản 1 Điều 35 như sau:
 “a) Ít nhất 30 ngày nếu làm việc theo hợp đồng lao động không xác định thời hạn;”"
```
Đầu ra:
```
{"op":"amends", "target":"BLLD_45-2019.D35.K1.a", "new_text":"Ít nhất 30 ngày nếu làm việc theo hợp đồng lao động không xác định thời hạn;", "effective":"2027-01-01", "how":"regex"}
```
Cổng: đích `D35.K1.a` phải tồn tại và nội dung mới phải lấy nguyên văn từ khối trích dẫn.

## 2.4 Áp chỉ thị lên phiên bản
**Tầng symbolic. Có code cũ (`src/versions.py`), chưa bàn lại.**

**Kể chuyện.** Mỗi đơn vị có một chuỗi **phiên bản**, mỗi phiên bản có khoảng hiệu lực nửa mở [từ, đến). Áp chỉ thị là: đóng phiên bản cũ (ghi `effective_to` bằng ngày phiên bản mới có hiệu lực), mở phiên bản mới, nối hai cái bằng `previous_version`. Không xoá chữ nào.

**[THẬT] Hiện tại Điều 35 (cả đơn vị con) chỉ có một phiên bản, ví dụ bản ghi của chính Điều 35:**
```
{"id":"BLLD_45-2019.D35", "version":1, "effective_from":"2021-01-01", "effective_to":null, "status":"in_force"}
```
**[GIẢ ĐỊNH] Sau khi "NĐ giả 2027" áp vào:**
```
D35.K1.a  v1  "Ít nhất 45 ngày ..."  [2021-01-01, 2027-01-01)  status=expired   closed_by=NĐ_giả_2027
D35.K1.a  v2  "Ít nhất 30 ngày ..."  [2027-01-01, null)        status=in_force  previous_version=1
```
**Vì sao.** Hỏi ngày 15/06/2026 thì v1 áp dụng (45 ngày); hỏi ngày 15/06/2027 thì v2 (30 ngày). Cả hai đáp án đều phải ra được.
**[THẬT] Số liệu cả kho** (mốc 10/09/2026): 9217 đơn vị, 9343 phiên bản, 260 cạnh cập nhật (45 `replaces`, 24 `amends`, 5 `repeals`, 171 `supplements_list`...).

## 2.5 Tập ảnh hưởng A(d)
**Tầng symbolic. CHƯA CÓ, chưa bàn** (chỉ có dòng "A(d) = T(d) ∪ N(T(d))" trong thiết kế).

**Kể chuyện.** Khi D35.K1.a đổi, không cần làm lại cả bộ luật, chỉ làm lại phần **bị ảnh hưởng**: T(d) = các đơn vị bị chỉ thị chạm trực tiếp, N(T(d)) = các đơn vị "láng giềng" của chúng trong đồ thị.

**[GIẢ ĐỊNH, vì chưa quyết bậc láng giềng.]** Với T = {D35.K1.a}, láng giềng có thể gồm:
- những đơn vị có cạnh `refers_to` vào Điều 35: `D34.K9`, `D39` (**[THẬT]**, cạnh có trong 1.2);
- đơn vị có cạnh `details` tới D35: `ND_145-2020` (**[THẬT]**);
- đơn vị cùng dùng một vị từ với D35.K1.a (qua 1.6B, chưa có);
- đơn vị chặn nhau với nó (qua 1.7, chưa có).
**Chưa quyết:** láng giềng bậc mấy, qua loại cạnh nào.

## 2.6 Trích lại cho tập ảnh hưởng
**Tầng LLM + cổng symbolic. CHƯA CÓ, chưa bàn.**

**Kể chuyện (theo thiết kế).** Với các đơn vị trong A(d), chạy lại 1.6 (mệnh đề, vị từ), 1.7 (ngoại lệ ngầm) và 1.8 (quy tắc), cộng quét lỗi. Phần còn lại của KB giữ nguyên. Là tái dùng 1.6 đến 1.8, nên chỉ làm được sau khi chúng xong.
**[GIẢ ĐỊNH]** Quy tắc `must_notify_days(W, 45)` của D35.K1.a v1 được giữ lại cho τ trước 2027 và thêm `must_notify_days(W, 30)` từ v2, hiệu lực từ 2027-01-01.

## 2.7 Đối chứng
**Tầng symbolic. CHƯA CÓ, chưa bàn.**

**Kể chuyện (theo thiết kế).** Hai cách xây KB phải cho **cùng kết quả**: (1) chạy tăng dần, nạp từng văn bản một theo ngày; (2) dựng lại từ đầu với tất cả văn bản. Cả hai phải ra cùng Π_τ tại cùng ngày τ. Lệch nghĩa là tập ảnh hưởng 2.5 đã bỏ sót đơn vị nào đó, hoặc 2.6 làm sai.
**[GIẢ ĐỊNH]** Với mọi τ trong 2021 đến 2030, quy tắc nào chứa D35.K1.a có hiệu lực ở τ phải giống nhau giữa hai cách.

---

# Câu hỏi cuối: pipeline trả lời ra sao

## Câu hỏi 1 (kết luận được, dùng dữ liệu 1.1 đến 1.8)
> Ngày 01/06/2026, bà A làm hợp đồng không xác định thời hạn, đã đủ tuổi nghỉ hưu theo Điều 169, hai bên không có thỏa thuận gì khác. Bà A có quyền nghỉ ngay không cần báo trước không?

**Dữ liệu từng bước dùng** (toàn bộ **[MINH HOẠ]**, vì 1.6B đến 1.9 chưa chạy):
1. **Đổi câu hỏi thành dữ kiện (1.9):** `employee_under_labor_code(a)`, `indefinite_term_contract(a)`, `reached_retirement_age(a)`, và `parties_agree_otherwise(a)` = **sai** (câu hỏi nói rõ không có thỏa thuận). Ngày τ = 2026-06-01. Máy **không tự tính tuổi**: "đủ tuổi nghỉ hưu" là dữ kiện đầu vào do người hỏi khai (vị từ loại `input`).
2. **Chọn Π_τ:** gồm quy tắc từ D35.K2.e (phiên bản 1, hiệu lực từ 2021-01-01, chưa bị đóng) và quy tắc từ D35.K1.a v1. Không có quy tắc nào của Điều 35 đang bị cô lập.
3. **Chạy φ = `may_terminate_without_notice(a)`:** điều kiện 1 đúng, điều kiện 2 đúng, `not parties_agree_otherwise(a)` đúng → **chứng minh được**.
4. **Chạy ¬φ:** không có cách nào chứng minh bà A *phải* báo trước (quy tắc 45 ngày bị chặn bởi quan hệ K2 chặn K1) → **không chứng minh được**.
5. **Kết quả: kết luận được, CÓ.**
   Căn cứ: Điều 35 khoản 2 điểm e BLLĐ, câu dẫn khoản 2, dẫn chiếu Điều 169; ngoại lệ "các bên thỏa thuận khác" **không kích hoạt**.

## Cùng câu hỏi, đổi dữ kiện: ra đủ bốn loại đáp án
| Dữ kiện thay đổi | Điều gì xảy ra | Đáp án |
|---|---|---|
| Hai bên **có** thỏa thuận khác | `parties_agree_otherwise(a)` đúng, nên ngoại lệ chặn quy tắc điểm e; φ không chứng minh được, ¬φ chứng minh được | **bị bác** theo điểm e |
| Câu hỏi **không nói** có thỏa thuận hay không | không biết `parties_agree_otherwise(a)`, φ cũng ¬φ đều không chốt được | **chưa đủ căn cứ** (cần hỏi thêm) |
| Quy tắc D35.K2.e bị **cô lập** (vì LLM viết sai, không qua cổng 1.8) | câu hỏi dính một mục bị cô lập | **không trả lời** |

## Câu hỏi 2 (dùng dữ liệu thật đến 2.2, chỉ để thấy vai trò của ngày τ và chỗ trống)
> Phi công (thành viên tổ lái tàu bay) làm hợp đồng không xác định thời hạn muốn nghỉ việc. Họ phải báo trước bao nhiêu ngày?

- **Hỏi ngày 15/01/2021 (BLLĐ đã có hiệu lực, ND_145 chưa hiệu lực, hiệu lực từ 01/02/2021).** D35.K1.d giao cho Chính phủ, nhưng chưa có văn bản lấp (chỗ trống 1.3 chưa có `filled_by` còn hiệu lực tại ngày này). → **chưa đủ căn cứ**, không được trả 45 ngày cho phi công vì D35.K1.d đã loại trường hợp đặc thù khỏi 45 ngày.
- **Hỏi ngày 01/03/2021.** ND_145 đã hiệu lực; D7.K1.a gồm "thành viên tổ lái tàu bay" và D7.K2.a nói "ít nhất 120 ngày đối với hợp đồng không xác định thời hạn". → **kết luận được: ít nhất 120 ngày**, căn cứ ND_145 Điều 7 khoản 2 điểm a, nối với BLLĐ Điều 35 khoản 1 điểm d bằng cạnh `details`.

Đây là ví dụ cho thấy cùng một câu hỏi có hai đáp án khác nhau theo ngày, và vì sao phải có phiên bản, điều khoản giao và `details`.

## Câu hỏi 3 (kể cả giai đoạn 2, **[GIẢ ĐỊNH]** vì dựa vào văn bản bịa)
> Người lao động hợp đồng không xác định thời hạn báo trước 30 ngày là đủ chưa?

- Hỏi ngày 15/06/2026 → v1 → cần 45 ngày → **bị bác** (30 < 45).
- Hỏi ngày 15/06/2027 → v2 (sau "NĐ giả 2027") → cần 30 ngày → **kết luận được: đủ**.
Hai câu trả lời đều lấy từ cùng một KB, chỉ khác Π_τ.

---

# Ghi chú cuối

**Giới hạn của tài liệu này.**
1. Mọi ví dụ từ 1.6A (bản mới) đến 1.9, và 2.3 đến 2.7, **không do chương trình nào chạy ra**; file ghi rõ nhãn [MINH HOẠ] hay [GIẢ ĐỊNH]. Đừng đọc chúng như kết quả.
2. Câu hỏi 1 và 3 thật ra chỉ chạy được khi 1.6B, 1.8, 1.9 xong, mà hiện các bước đó chưa có code. Riêng 1.9 chưa có thiết kế, nên cách "đổi câu hỏi thành dữ kiện" ở trên là cách mô tả hợp lý chứ không phải thiết kế đã chốt.
3. Ví dụ quy tắc ở 1.8 (cú pháp s(CASP) và cách xử lý nút `tuy_nghi` "các bên thỏa thuận khác" bằng `not parties_agree_otherwise`) chưa được quyết (A33 mục 3b-a). Ví dụ chỉ để minh hoạ hình dạng, không phải thiết kế.
4. Ở câu hỏi 2, kết luận "chưa đủ căn cứ" ngày 15/01/2021 là suy từ thiết kế (chỗ trống chưa có văn bản lấp có hiệu lực tại ngày đó), chưa được kiểm bằng chạy 1.9. Nên coi là dự kiến.
5. Số liệu bước đã làm (1.1 đến 1.5, 2.2, 2.4) đọc từ file đầu ra và báo cáo chạy; đối chiếu với lần chạy `run_all` ngày 15/11/2026.
6. Chưa sửa, đã biết: lỗi 1.1 (đoạn gắn nhầm khoản cha), nợ 1.2 (dẫn chiếu Mục/Chương), 1.6A mới chưa chạy đủ 204 lô.
