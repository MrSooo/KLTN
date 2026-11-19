# Thiết kế pipeline

Tài liệu này là bản thiết kế hiện hành của pipeline: mục tiêu, mô hình dữ liệu, nguyên tắc, các bước và trạng thái. Kể chuyện từng bước bằng một ví dụ: `docs/overview.md`. Mô tả chi tiết từng bước: các file khác trong `docs/design/`. Lý do của từng lựa chọn: `docs/decisions.md`. Phương pháp của đồ án (mô hình K, thuật toán cập nhật): `docs/reference/method.md`.

## 1. Mục tiêu
Dựng cơ sở tri thức (KB) từ Bộ luật Lao động 45/2019 (BLLĐ); KB trả lời được câu hỏi có/không theo ngày sự việc τ kèm căn cứ, và **cập nhật** được khi nạp nghị định, thông tư. Mô phỏng thực tế: luật ra trước, văn bản hướng dẫn ra sau thì KB mở rộng.

## 2. Mô hình K
K = (D, U, V, E, Δ, P, R)
- D: văn bản; U: đơn vị (Điều, Khoản, Điểm); V: phiên bản của đơn vị (chữ, khoảng hiệu lực, trạng thái).
- E: quan hệ có kiểu (`refers_to`, `exception_of`, `based_on`, `details`, ...).
- Δ: điều khoản luật giao cho cấp dưới quy định chi tiết.
- P: sổ vị từ (khái niệm dùng chung để viết quy tắc); R: tập quy tắc, mỗi quy tắc gắn một phiên bản nguồn.
- Π_τ: các quy tắc có phiên bản đang hiệu lực tại ngày τ và không bị cô lập. Câu trả lời chỉ dựa trên Π_τ.

## 3. Nguyên tắc
1. Đầu ra của LLM luôn bị ràng buộc (chọn trong tập đóng, trích nguyên văn, chỉ dùng vị từ được phép) và **mỗi bước dùng LLM có cổng kiểm bằng máy** (regex, khớp đồ thị, biên dịch...). Không qua cổng thì lùi về mặc định an toàn hoặc bị cô lập. Không dùng một LLM để kiểm LLM khác (A6, A14, A25).
2. Không có người duyệt ở giữa chuỗi: kiểm hoàn toàn tự động.
3. Lựa chọn của LLM trong một tập đóng được dùng làm căn cứ nhưng phải gắn cờ trên dòng, liệt kê trong báo cáo và đo độ chính xác trên mẫu (A30, A32, A33). Đầu ra tự do của LLM bị cô lập.
4. Chỗ spec im lặng thì dừng và báo lỗi (fail-closed), không đoán.
5. Các bước 1.1 đến 1.5 xử lý **một văn bản bất kỳ**, không riêng BLLĐ, vì giai đoạn 2 tái dùng chúng.

## 4. Giai đoạn 1: dựng KB gốc, chỉ từ BLLĐ

| Bước | Module | Dựng gì | LLM | Kiểm chính | Trạng thái |
|---|---|---|---|---|---|
| 1.1 Parse | `parse.py` | D, U, V (phiên bản 1) | không | số Điều khớp bảng văn bản; số thứ tự liên tục (đứt thì từ chối); mỗi đơn vị đúng một cha | xong |
| 1.2 Dẫn chiếu | `refs.py` | E: `contains`, `part_of`, `refers_to`, quan hệ chờ đích | không | mỗi cụm có đúng một kết cục: nối, chờ đích hoặc không giải được kèm lý do; cổng phần dư | xong; tầng 2 (đích duy nhất cho khoản/điểm trơ trụi) hoãn |
| 1.3 Điều khoản giao | `delegation.py` | Δ | không | các mốc của bảng đối chiếu; tầng lỏng gắn cờ `loose` | xong |
| 1.4 Loại Điều | `article_type.py` | nhãn quyết định Điều nào được trích quy tắc | không (A14) | regex trên tiêu đề; Điều không khớp thì mặc định `substantive` | xong |
| 1.5 Ngoại lệ tường minh | `exceptions_explicit.py`, `exceptions_general.py` | E: `exception_of` ("trừ trường hợp ...", "không áp dụng ...") | không | các mốc đã biết; mọi trigger thuộc đúng một trạng thái | xong |
| 1.6A Mệnh đề | `propositions.py` | tách chữ luật thành mệnh đề | có | cổng nguyên văn và cổng âm tiết | đang làm lại (A38, A39); `concepts.py` là bản cũ |
| 1.6B Sổ vị từ | `concepts_names.py` | P: đặt tên vị từ, tái dùng tên | có | tên đúng dạng; tái dùng chỉ khi cùng nghĩa và cùng chữ ký đối số | phải viết lại để đọc mệnh đề (A39) |
| 1.7 Ngoại lệ ngầm | chưa có | E: `exception_of` giữa hai đơn vị cùng dùng một vị từ | có (xét từng cặp) | câu bằng chứng nguyên văn; hai đầu tồn tại; không tạo vòng | bản nháp |
| 1.8 Quy tắc | chưa có | R: quy tắc s(CASP); quét lỗi; tự sửa tối đa 2 vòng | có | biên dịch được; chỉ dùng vị từ được phép; bộ quét; không qua thì cô lập | bản nháp |
| 1.9 Hỏi đáp theo ngày | chưa có | câu trả lời từ Π_τ | có (đổi câu hỏi thành dữ kiện) | chạy φ và ¬φ; bốn kết quả: kết luận được, bị bác, chưa đủ căn cứ, không trả lời | chưa thiết kế |

Nhóm theo lớp: **cấu trúc** (1.1-1.2), **quan hệ pháp lý** (1.3-1.5), **tri thức** (1.6-1.8), **hỏi đáp** (1.9). Bộ kiểm độc lập `checks.py` đếm lại bằng cách khác sau mỗi lớp.

Khuôn **cạnh** chung cho mọi bước tạo cạnh (A12): `{s, p, o, evidence, how, flags}`.
- `s`, `p`, `o`: chủ thể, kiểu quan hệ, đối tượng. Đơn vị (nút) lưu dạng bộ ba thuộc tính ở bước 1.1.
- `evidence`: đoạn nguyên văn làm bằng chứng; phải là chuỗi con của chữ đơn vị `s` (cổng kiểm).
- `how`: ai tìm ra cạnh (`regex`, `llm`, `keyword`, `parent`).
- `flags`: cờ độ tin cậy (`llm_proposed`, `loose`, `isolated`...). Cạnh có cờ được giữ và báo cáo.
- Riêng cạnh ngoại lệ có thêm `rule` (tên quy tắc sinh cạnh).

## 5. Giai đoạn 2: cập nhật khi có văn bản mới
`Update(K, d)` cho mỗi nghị định, thông tư theo ngày hiệu lực (Thuật toán 1 của `docs/reference/method.md`). Bản hợp nhất VBHN_125 nạp như một văn bản thường.

| Bước | Việc | Module | Trạng thái |
|---|---|---|---|
| 2.1 | Xử lý văn bản mới bằng 1.1 đến 1.5 | tái dùng | chưa thiết kế |
| 2.2 | Nối vào KB: quan hệ chờ đích, `based_on`, `details` (văn bản không nêu số Điều thì LLM chọn trong Δ; giữ khi model thứ hai cùng chọn và từ khoá phạm vi có trong Điều đích) | `links.py` | xong cho kho hiện tại |
| 2.3 | Đọc chỉ thị: regex trước; câu lạ thì báo lỗi, không đoán | `directives.py`, `directives_rare.py` | xong cho kho hiện tại; bảng loại ở `docs/reference/directive_types.md` |
| 2.4 | Áp chỉ thị lên phiên bản: đóng phiên bản cũ, mở phiên bản mới, không xoá nút | `versions.py` | xong cho kho hiện tại |
| 2.5 | Tính tập ảnh hưởng A(e) = T(e) ∪ N(T(e)) theo từng mốc của kho phiên bản; N một bước | `affected.py` | có mã, chạy trên tập con (A42; `steps_2_5_to_2_7.md`) |
| 2.6 | Trích lại mệnh đề, vị từ, ngoại lệ ngầm, quy tắc cho A(e); quét lỗi | `update.py`, `predicate_registry.py`, `knowledge_units.py` | có mã; tri thức của nghị định chờ phiên LLM (A42) |
| 2.7 | Đối chứng: chạy tăng dần và dựng lại toàn bộ phải ra cùng Π_τ tại cùng ngày | `update.py` | có mã; đạt trên tập con với tri thức BLLĐ; test tổng hợp trượt đúng khi cắt N (A42) |

Công cụ phụ: `checks.py` (kiểm tra độc lập), `graph.py` (đồ thị gộp, mỗi nút có khoảng hiệu lực), `utils/viewer/` (trang HTML xem đồ thị theo ngày, mở offline).

## 6. Mô tả một bước (khuôn)
Mỗi bước được mô tả theo cùng một khuôn; nhiều ví dụ dữ liệu thật; bảng field liệt kê **hết** các giá trị của field có nhiều dạng, không viết tắt kiểu "dạng A, B, D":
1. Nhận vào: dạng dữ liệu, từ file nào, ví dụ thật.
2. Ra: file ghi ra; ví dụ cho từng loại dòng, kể cả loại "không thành công".
3. Bảng field: nghĩa, mọi giá trị có thể có, ai đọc.
4. Cách làm: các bước máy làm theo thứ tự; ví dụ khớp và không khớp; có LLM không.
5. Vì sao: thiếu bước này thì hỏng gì; cách khác đã cân nhắc và vì sao không chọn.
6. Kiểm và số đo: máy kiểm gì; số đo trên dữ liệu thật và đo ở đâu; cái gì chưa kiểm được.

Mẫu hoàn chỉnh: bước 1.1 đến 1.5 ở `docs/design/steps_1_1_to_1_5.md`; bước 1.6A ở `docs/design/step_1_6a_propositions.md`.

## 7. Câu hỏi thiết kế còn mở
1. **Điều khoản giao chưa có văn bản lấp** (ví dụ Điều 154 khoản 9 giao cho Chính phủ): nếu suy luận kiểu "không chứng minh được thì coi là sai", KB chỉ có BLLĐ sẽ trả "phải có giấy phép lao động" dù đáp án trung thực là "chưa đủ căn cứ". Cần quyết cách để Δ ảnh hưởng tới suy luận.
2. **Câu hỏi cổng của giai đoạn 1**: ví dụ giấy phép lao động 45 ngày cần ND_152 và ND_219 nên không dùng được khi KB chỉ có BLLĐ. Cần chọn câu hỏi đo giai đoạn 1.
3. **Bước 2.3 có còn cần nhãn `effect_transition` của 1.4 không**, hay chỉ cần regex trên động từ chỉ thị. Mã hiện tại chỉ tìm chỉ thị trong Điều mang nhãn này.
4. **Số bước lan truyền của N(·)**: chốt một bước (A42); 2.7 đo có đủ không.
5. **Thứ tự mục của Method:** Method xếp cập nhật (3.4) trước tri thức (3.5), thứ tự dựng thì ngược lại.
6. **Tám Điều lệch giữa BLLĐ và VBHN_125:** mã hiện tại xử lý qua cờ `consolidation_discrepancy` (xem `docs/decisions.md`, mục Versions); VBHN_125 nay là văn bản nạp thường nên cần bàn lại ở giai đoạn 2.
