# Pipeline mới: thiết kế và trạng thái (bắt đầu 10/11/2026)

Đây là thiết kế **đang bàn**, thay cho cách đánh số L0-L11 của plan cũ. Mọi bước phải giải thích được "vì sao làm vậy mà không phải kiểu kia"; thẻ giải thích từng bước sẽ thêm vào đây khi bàn tới bước đó. Quyết định và lý do ở `docs/quyet_dinh/pipeline_moi_quyet_dinh.txt`.

## Mục tiêu
Một hệ thống dựng KB từ luật gốc (BLLĐ 45/2019), KB trả lời được câu hỏi có/không theo ngày sự việc τ kèm căn cứ, rồi **cập nhật** được khi nạp nghị định, thông tư. Mô phỏng thực tế: luật ra trước, văn bản hướng dẫn ra sau thì KB mở rộng.

## Mô hình K (theo Method 09/11, mục 3.1)
K = (D, U, V, E, Δ, P, R)
- D văn bản, U đơn vị (Điều, Khoản, Điểm), V phiên bản của đơn vị (chữ, khoảng hiệu lực, trạng thái).
- E quan hệ có kiểu: `refers_to`, `exception_of`, `based_on`, `details`...
- Δ điều khoản luật giao cho cấp dưới quy định chi tiết.
- P sổ vị từ (khái niệm dùng chung để viết quy tắc), R tập quy tắc, mỗi quy tắc gắn một phiên bản nguồn.
- Π_τ = các quy tắc có phiên bản đang hiệu lực tại ngày τ và không bị cô lập. Câu trả lời chỉ dựa trên Π_τ.

## Hai nguyên tắc
1. Đầu ra của LLM luôn bị ràng buộc (chọn trong tập đóng, trích nguyên văn, chỉ dùng vị từ được phép) và **mỗi bước dùng LLM có cổng kiểm symbolic** (regex, khớp đồ thị, biên dịch...). Không qua cổng thì lùi về mặc định an toàn hoặc bị cô lập.
2. Không có người duyệt ở giữa chuỗi: kiểm hoàn toàn tự động.

## Giai đoạn 1: dựng KB gốc, chỉ từ BLLĐ
Các bước 1.1 đến 1.5 phải viết theo "xử lý **một văn bản bất kỳ**", không riêng BLLĐ, vì giai đoạn 2 tái dùng. Δ cũng chạy trên mọi văn bản (TT_18 căn cứ ND_145 Điều 68, tức nghị định cũng giao tiếp cho thông tư).

| Bước | Dựng gì | LLM? | Kiểm (theo Method và code cũ) | Code cũ | Trạng thái |
|---|---|---|---|---|---|
| 1.1 Parse | D, U, V (phiên bản 1) | không | số Điều khớp bảng văn bản; số thứ tự liên tục (đứt thì từ chối); mỗi đơn vị đúng 1 cha | `l1_parse.py` | chưa bàn lại |
| 1.2 Dẫn chiếu | E: `refers_to`, quan hệ chờ đích | không | mỗi cụm có đúng 1 kết cục: nối / chờ đích / không giải được kèm lý do | `l2_edges.py` | chưa bàn lại |
| 1.3 Điều khoản giao | Δ | không (ở giai đoạn 1) | các mốc của bảng đối chiếu | `l3_links.py` (phần quét) | chưa bàn lại |
| 1.4 Loại Điều | nhãn quyết định Điều nào được trích quy tắc | có (phần tiêu đề chưa khớp mẫu) | nhãn đẩy Điều khỏi "nội dung" cần xác nhận. **Hiện cổng này là model LLM thứ hai, chưa phải symbolic: cần bàn** | `l4_classify.py` | chưa bàn lại |
| 1.5 Ngoại lệ tường minh | E: `exception_of` (cụm "trừ trường hợp ... tại Điều X") | không | các mốc 154→151.1.d, 37→36.1.b... | `l5_*_exceptions.py` | chưa bàn lại |
| 1.6 Sổ khái niệm | P | có (gạch cụm chủ thể, điều kiện, ngoại lệ, kết luận) | cụm phải là chuỗi con nguyên văn của đơn vị; một lượt trích độc lập kiểm lại | chưa có | chưa bàn |
| 1.7 Ngoại lệ ngầm | E: `exception_of` giữa hai đơn vị cùng dùng một khái niệm | có (xét từng cặp) | có câu bằng chứng nguyên văn; hai đầu tồn tại; không tạo vòng | chưa có | chưa bàn |
| 1.8 Quy tắc | R (quy tắc s(CASP)), quét lỗi, tự sửa tối đa 2 vòng | có | biên dịch được; chỉ dùng vị từ được phép; bộ quét lỗi; không qua thì cô lập | chưa có | chưa bàn |
| 1.9 Hỏi đáp theo ngày | câu trả lời từ Π_τ | có (đổi câu hỏi thành dữ kiện) | chạy φ và ¬φ; bốn kết quả: kết luận được / bị bác / chưa đủ căn cứ / không trả lời (dính mục bị cô lập) | chưa có | chưa bàn |

Nhóm theo lớp: **cấu trúc** (1.1-1.2), **quan hệ pháp lý** (1.3-1.5), **tri thức** (1.6-1.8), **hỏi đáp** (1.9). Sau mỗi lớp có một lần kiểm độc lập (bộ kiểm riêng, đếm lại bằng cách khác).

## Giai đoạn 2: update engine, `Update(K, d)` cho mỗi ND/TT theo ngày hiệu lực
Theo Thuật toán 1 của Method. VBHN_125 nạp như một văn bản thường.

| Bước | Việc | Dòng Thuật toán 1 | Code cũ | Trạng thái |
|---|---|---|---|---|
| 2.1 | Xử lý văn bản mới bằng 1.1 đến 1.5 | 1 | tái dùng | chưa bàn |
| 2.2 | Nối vào KB: quan hệ chờ đích, `based_on`, `details` (văn bản không nêu số Điều thì LLM chọn trong Δ, giữ khi model thứ hai cùng chọn và từ khoá phạm vi có trong Điều đích) | 1, 5 | `l3_links.py` (phần nối) | chưa bàn |
| 2.3 | Đọc chỉ thị: regex trước; không thấy thì LLM đề xuất loại thao tác; rồi qua cổng symbolic; vẫn không xếp được thì đánh dấu chưa xác định và cô lập đơn vị bị chạm | 2-3 | `l6_directives.py` | chưa bàn |
| 2.4 | Áp chỉ thị lên phiên bản: đóng phiên bản cũ, mở phiên bản mới, không xoá gì | 4 | `l6_versions.py`, `l6_rare.py` | chưa bàn |
| 2.5 | Tính tập ảnh hưởng A(d) = T(d) ∪ N(T(d)) | 6 | chưa có | chưa bàn |
| 2.6 | Trích lại khái niệm, ngoại lệ ngầm, quy tắc cho A(d); quét lỗi (tái dùng 1.6 đến 1.8) | 7-8 | chưa có | chưa bàn |
| 2.7 | Đối chứng: chạy tăng dần và dựng lại toàn bộ phải ra cùng Π_τ tại cùng ngày | | chưa có | chưa bàn |

## Đối chiếu code cũ với bước mới
L1 → 1.1; L2 → 1.2 (và phần liên văn bản ở 2.2); L3 → 1.3 (quét) và 2.2 (nối); L4 → 1.4; L5 → 1.5; L6 → 2.3, 2.4; L7 → 1.6; L8 → 1.7; L9 → 1.8; L10 → 1.9; L11 → 2.5 đến 2.7; `checks`, `graph`, `viewer` là công cụ phụ (kiểm độc lập, đồ thị gộp, trang xem).

## Số đối chiếu của code cũ (chép từ `docs/tien_do_L0_L6.md` ngày 09/11, chưa đối chiếu lại với đĩa)
Pipeline mới, khi dựng xong phần tương ứng, phải ra lại các số này hoặc giải thích từng chỗ lệch: 10.202 đơn vị và 893 Điều (L1, 18 văn bản); 2.348 `refers_to`, 129 chờ đích (L2); 51 điều khoản giao, 10 `based_on`, 48 `details` (L3); 23 cạnh ngoại lệ tường minh, 336 cạnh và 128 nút điều kiện (L5); 9.217 đơn vị, 9.343 phiên bản, 260 cạnh cập nhật, 15/15 mốc cổng dev (L6); 2.721 cạnh ngữ nghĩa (graph).

## Câu hỏi thiết kế đang mở
1. **Cổng symbolic cho nhãn loại Điều (1.4):** nhãn không có đáp án để đối chiếu. Hướng: kiểm nhất quán (ví dụ nhãn "hiệu lực-chuyển tiếp" phải chứa động từ chỉ thị, không thì gắn cờ). Chưa chốt.
2. **Điều khoản giao chưa có văn bản lấp** (Điều 154 khoản 9 đang giao cho Chính phủ): nếu suy luận theo kiểu "không chứng minh được thì coi là sai", KB chỉ có BLLĐ sẽ trả "phải có giấy phép lao động" dù đáp án trung thực là "chưa đủ căn cứ". Cần quyết cách để Δ ảnh hưởng tới suy luận. Chưa bàn.
3. **Câu hỏi cổng của giai đoạn 1:** ví dụ giấy phép lao động 45 ngày cần ND_152 và ND_219 nên không dùng được khi KB chỉ có BLLĐ. Cần chọn câu hỏi đo giai đoạn 1.
4. **Hạn mức LLM:** model kiểm chỉ 20 lượt mỗi ngày (`docs/llm_config.md`). Chưa đếm số lượt cần cho 1.6-1.8 trên 220 Điều. Phải đếm trước khi cam kết "mọi bước LLM đều có model thứ hai kiểm".
5. **Bước 2.3 có còn cần nhãn "hiệu lực-chuyển tiếp" của 1.4 không**, hay chỉ regex trên động từ chỉ thị. Code cũ chỉ tìm chỉ thị trong Điều mang nhãn này.
6. **Số bước lan truyền của N(·)** trong tập ảnh hưởng (Method đang ghi [CẦN XÁC MINH]).
7. **Thứ tự mục của Method:** bài xếp 3.4 (update) trước 3.5 (tri thức), thứ tự dựng mới thì ngược lại. Đổi hay không là quyền user.
8. **8 Điều lệch giữa BLLĐ và VBHN_125** (xử lý ở code cũ qua cờ `consolidation_discrepancy`): giờ VBHN_125 là văn bản nạp thường, cần bàn lại cách xử lý ở giai đoạn 2.
