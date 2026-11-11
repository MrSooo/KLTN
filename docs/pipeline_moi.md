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
| 1.1 Parse | D, U, V (phiên bản 1) | không | số Điều khớp bảng văn bản; số thứ tự liên tục (đứt thì từ chối); mỗi đơn vị đúng 1 cha | `parse.py` (cũ `l1_parse.py`) | đã bàn; đổi tên xong (S1) |
| 1.2 Dẫn chiếu | E: `refers_to`, quan hệ chờ đích | không | mỗi cụm có đúng 1 kết cục: nối / chờ đích / không giải được kèm lý do | `refs.py` (cũ `l2_edges.py`) | đã bàn (A15); đổi tên xong (S1); cổng phần dư đã có sẵn (0 sót); tầng 2 hoãn (B10) |
| 1.3 Điều khoản giao | Δ | không (ở giai đoạn 1) | các mốc của bảng đối chiếu | `delegation.py` (cũ phần quét của `l3_links.py`) | **đã code 11/11 (S4)**: tách file, thêm tầng lỏng `loose` |
| 1.4 Loại Điều | nhãn quyết định Điều nào được trích quy tắc | không (chốt 11/11, A14: bỏ LLM) | regex trên tiêu đề; Điều không khớp mặc định `substantive` | `article_type.py` (cũ `l4_classify.py`) | **đã code 11/11 (S2)** |
| 1.5 Ngoại lệ tường minh | E: `exception_of` (cụm "trừ trường hợp ... tại Điều X") | không | các mốc 154→151.1.d, 37→36.1.b... | `exceptions_explicit.py`, `exceptions_general.py` (cũ `l5_*_exceptions.py`) | đã bàn; đổi tên xong (S1) |
| 1.6 Sổ khái niệm | P | có (gạch cụm chủ thể, điều kiện, ngoại lệ, kết luận) | cụm phải là chuỗi con nguyên văn của đơn vị; một lượt trích độc lập kiểm lại | chưa có | chưa bàn |
| 1.7 Ngoại lệ ngầm | E: `exception_of` giữa hai đơn vị cùng dùng một khái niệm | có (xét từng cặp) | có câu bằng chứng nguyên văn; hai đầu tồn tại; không tạo vòng | chưa có | chưa bàn |
| 1.8 Quy tắc | R (quy tắc s(CASP)), quét lỗi, tự sửa tối đa 2 vòng | có | biên dịch được; chỉ dùng vị từ được phép; bộ quét lỗi; không qua thì cô lập | chưa có | chưa bàn |
| 1.9 Hỏi đáp theo ngày | câu trả lời từ Π_τ | có (đổi câu hỏi thành dữ kiện) | chạy φ và ¬φ; bốn kết quả: kết luận được / bị bác / chưa đủ căn cứ / không trả lời (dính mục bị cô lập) | chưa có | chưa bàn |

Nhóm theo lớp: **cấu trúc** (1.1-1.2), **quan hệ pháp lý** (1.3-1.5), **tri thức** (1.6-1.8), **hỏi đáp** (1.9). Sau mỗi lớp có một lần kiểm độc lập (bộ kiểm riêng, đếm lại bằng cách khác).

## Cách làm từng bước 1.1 đến 1.5 (tóm tắt 11/11, theo đúng code đang chạy)
**1.1 parse.** Nhận: file `.txt` (mỗi đoạn một dòng) và dòng của nó trong `manifest.csv`. Cách làm: đọc từng dòng bằng một máy trạng thái giữ "con trỏ hiện tại" ở mỗi cấp (Chương, Mục, Điều, Khoản, Điểm). Mỗi dòng được nhận dạng bằng regex ở ĐẦU dòng: `Chương <La Mã>`, `Mục <số>`, `Điều <số>.`, `<số>.` (khoản), `<chữ>)` (điểm). Gặp một đơn vị mới thì cha của nó là con trỏ cấp trên ngay lúc đó, và các con trỏ cấp dưới bị xoá. Mã: Điều là `<doc_id>.D14` (KHÔNG chứa Chương, quan hệ Điều thuộc Mục hay Chương nằm ở thuộc tính `parent`); khoản = mã Điều + `.K2`; điểm = mã khoản + `.a`; Mục = mã Chương + `.M1`. Dòng không có nhãn: nếu bắt đầu bằng gạch đầu dòng thì nối vào đơn vị sâu nhất đang mở; còn lại nối vào Khoản đang mở (chưa có Khoản thì vào Điều), kể cả khi một Điểm đang mở (có ghi chú). Ba chỗ xử lý riêng: (a) khối trích dẫn “...” trong văn bản sửa đổi (chứa dòng kiểu "Điều 32. ..." của văn bản KHÁC) bị nuốt thành "payload", không thành đơn vị, nếu không thì Điều của văn bản bị sửa lẫn với Điều của văn bản này; (b) phần đầu văn bản, "Nơi nhận", phụ lục và chú thích đi riêng; (c) "4.960.000" không phải khoản (khoản cần dấu chấm rồi khoảng trắng). Kiểm: số thứ tự phải liền (Điều n sau n-1; Điều chèn là 8, 8a, 8b; điểm theo bảng chữ a, b, c... có đ, không có f j w z), mã không lặp, số Điều bằng cột trong manifest; có bất thường thì dừng và không ghi file. Ra: bộ ba thuộc tính cho mỗi đơn vị (`type, number, heading, parent, text, source_line`), cùng các khối trích dẫn, bảng, chú thích và `documents.jsonl`.

**1.2 refs.** Nhận: đơn vị từ 1.1. Cách làm: (1) cạnh cha-con `contains`/`part_of` lấy thẳng từ thuộc tính `parent`; (2) `refers_to`: regex tìm cụm kiểu "khoản 1, 2 và 3 Điều 14 của Nghị định số ...", tách thành danh sách cấp (điểm, khoản, Điều) và "đuôi" (này, số hiệu, hay tên văn bản); (3) giải ra mã đích: cấp nào thiếu thì suy từ vị trí đơn vị chứa cụm ("khoản 2 này" là khoản 2 của cùng Điều); đuôi nêu văn bản khác thì tra bảng văn bản; (4) không chắc thì KHÔNG đoán ("khoản 2" trơ trụi, hay nhiều đối số ở cấp trên thì ghi "không giải được"). Dòng chỉ thị sửa đổi ("Sửa đổi, bổ sung khoản 6 Điều 7 như sau:") không sinh `refers_to` vì nó trỏ vào văn bản bị sửa. Kiểm: mỗi cụm có đúng một kết cục (nối, chờ đích, không giải được); không cạnh nào trỏ tới mã không tồn tại. Ra: cạnh cha-con, `refers_to` kèm câu nguyên văn, danh sách chờ đích, danh sách không giải được kèm lý do.

**1.3 delegation.** Nhận: chữ của các đơn vị. Cách làm: regex 5 dạng: A "Chính phủ / Bộ trưởng ... quy định ..." (gồm C "do Chính phủ quy định"); B "theo quy định của Chính phủ / Bộ trưởng"; D "Bộ trưởng ... ban hành" (danh mục, chương trình); E "Thủ tướng Chính phủ quyết định". Ghi đơn vị, dạng, bên được giao và cụm nguyên văn; số đếm là regex thô, không tự lọc ca không phải giao chi tiết. Ra: danh sách điều khoản giao Δ. Kiểm cũ: các mốc của bảng đối chiếu; đo 11/11 cho thấy chưa đủ (xem B5), nên S4 thêm tầng lỏng.

**1.4 article_type.** Nhận: tiêu đề từng Điều. Cách làm: regex trên tiêu đề (ví dụ "Giải thích từ ngữ" là `definition`, "Hiệu lực thi hành" là `effect_transition`, "Hồ sơ", "Trình tự", "Thủ tục" là `procedural`); không khớp mẫu nào thì `substantive` (mặc định an toàn, không bỏ sót quy tắc). Không LLM. Ra: một nhãn cho mỗi Điều; nhãn chỉ quyết định Điều có được dịch thành quy tắc hay không và là nơi 2.3 tìm câu chỉ thị.

**1.5 exceptions.** Nhận: đơn vị và cách giải dẫn chiếu của 1.2. Cách làm: hai quy tắc tường minh: (1) "[cụm dẫn chiếu] không áp dụng" đứng ngay trước, thì đơn vị chứa là `s`, đích của cụm là `o`; (2) có "trừ" và kết thúc "sau đây:", thì mỗi đơn vị con trực tiếp là `s`, đơn vị chứa là `o`. Kiểu chung "..., trừ trường hợp X": cắt mệnh đề X (từ "trừ trường hợp" đến hết đoạn), tạo nút điều kiện (câu giống nhau gộp một nút) rồi cạnh `exception_of` từ nút đó tới đơn vị; X dẫn chiếu tới đơn vị T thì T cũng là ngoại lệ của đơn vị. Nút điều kiện chia 3 loại: `cu_the`, `tuy_nghi` ("các bên thỏa thuận khác"), `dan_chieu_mo` ("pháp luật có quy định khác"). Đơn vị có hơn một "trừ trường hợp" thì để chưa xử lý, không đoán. Kiểm: mỗi chỗ có "trừ" hoặc "không áp dụng" thuộc đúng một trong hai (đã tạo cạnh, hoặc ghi chưa xử lý); `evidence` phải là chuỗi con nguyên văn.

## Ví dụ một dòng dữ liệu thật của mỗi bước (BLLĐ, khuôn cạnh sau S3 ngày 11/11)
Khuôn cạnh chung (A12): `{s, p, o, evidence, how, flags}`. `how` = ai tìm ra (`regex`, `llm`, `keyword`, `parent`); `flags` = độ tin cậy; riêng cạnh ngoại lệ có thêm `rule`.

**1.1 parse:** mỗi đơn vị là vài dòng bộ ba cùng chủ thể `s` (khoản 2 Điều 14, văn bản gốc nằm ở dòng 210):
```
{"s":"BLLD_45-2019.D14.K2","p":"type","o":"khoan"}
{"s":"BLLD_45-2019.D14.K2","p":"number","o":"2"}
{"s":"BLLD_45-2019.D14.K2","p":"parent","o":"BLLD_45-2019.D14"}
{"s":"BLLD_45-2019.D14.K2","p":"text","o":"Hai bên có thể giao kết hợp đồng lao động bằng lời nói đối với hợp đồng có thời hạn dưới 01 tháng, trừ trường hợp quy định tại khoản 2 Điều 18, điểm a khoản 1 Điều 145 ..."}
{"s":"BLLD_45-2019.D14.K2","p":"source_line","o":210}
```
(Điều còn có thêm một dòng `heading` là tiêu đề.)

**1.2 refs:** cạnh cha-con, cạnh `refers_to`, và hai loại không thành cạnh:
```
{"s":"BLLD_45-2019.D14","p":"contains","o":"BLLD_45-2019.D14.K2","evidence":"","how":"parent","flags":[]}
{"s":"BLLD_45-2019.D14.K2","p":"refers_to","o":"BLLD_45-2019.D145.K1.a","evidence":"điểm a khoản 1 Điều 145","how":"regex","flags":[]}
không giải được: {"unit":"ND_135-2020.D5.K1.d","phrase":"điểm a","reason":"cụm kết thúc bằng khoản/điểm, không có Điều"}
chờ đích:        {"source":"ND_28-2020.D10.K2.a","edge":"refers_to","target_number":"10/2012/QH13","target_name":"Bộ luật Lao động","target_units":["D31"],"text":"Điều 31 của Bộ luật Lao động"}
```

**1.3 delegation:** một điều khoản giao chắc (`flags` rỗng) và một ca lỏng (cờ `loose`). Việc nối với văn bản dưới luật là bước 2.2, ra file riêng `delegation_filled.jsonl` (`{clause_id, filled_by}`):
```
{"clause_id":"DC_D12_K3_1","unit_id":"BLLD_45-2019.D12.K3","pattern":"A","delegate":"Chính phủ","phrase":"Chính phủ quy định","context":"Chính phủ quy định chi tiết Điều này.","flags":[]}
{"clause_id":"DC_D21_K5_1","unit_id":"BLLD_45-2019.D21.K5","pattern":"loose","delegate":"Bộ trưởng","phrase":"Bộ trưởng Bộ Lao động - Thương binh và Xã hội quy định","flags":["loose"]}
```

**1.4 article_type:** một nhãn cho mỗi Điều:
```
{"id":"BLLD_45-2019.D3","label":"definition","how":"regex"}
{"id":"BLLD_45-2019.D14","label":"substantive","how":"default"}
```

**1.5 exceptions:** ngoại lệ chung tạo một nút điều kiện (`s` là mã nút, không phải đơn vị luật) và một cạnh; ca tường minh có cùng dạng với `rule` là `not_apply_pattern` hoặc `except_list_pattern`:
```
{"s":"BLLD_45-2019.Xc9877375","p":"exception_of","o":"BLLD_45-2019.D3.K1","evidence":"trừ trường hợp quy định tại Mục 1 Chương XI của Bộ luật này.","how":"regex","flags":[],"rule":"general_except"}
{"id":"BLLD_45-2019.Xc9877375","type":"dieu_kien","kind":"cu_the","text":"quy định tại Mục 1 Chương XI của Bộ luật này","units":["BLLD_45-2019.D3.K1"]}
```

## Giải thích từng field của ví dụ trên (ai đọc, để làm gì)
"Ai đọc" lấy từ việc tìm trong code ngày 11/11. Dấu **—** nghĩa là chưa bước nào đọc field đó.

**1.1 parse** (dòng bộ ba `s, p, o`: `s` là mã đơn vị, `p` là tên thuộc tính, `o` là giá trị)
| `p` | Nghĩa | Ai đọc, để làm gì |
|---|---|---|
| `type` | loại đơn vị: `chuong`, `muc`, `dieu`, `khoan`, `diem` | mọi bước sau, ví dụ 1.4 chỉ gắn nhãn cho `dieu` |
| `number` | số hoặc chữ thứ tự gốc ("2", "a") | kiểm số thứ tự liền nhau lúc parse; hiển thị trên đồ thị |
| `heading` | tiêu đề (chỉ Chương, Mục, Điều có) | 1.4 đọc để gắn nhãn; đồ thị hiển thị |
| `parent` | mã đơn vị cha | 1.2 lấy cạnh cha-con từ đây; các bước cần "đi lên Điều chứa nó" |
| `text` | chữ của đơn vị | 1.2, 1.3, 1.5 tìm dẫn chiếu, điều khoản giao, chữ "trừ" trong đó; là nguồn của mọi `evidence` |
| `source_line` | số dòng trong file `.txt` gốc | **—** để truy ngược về nguồn khi cần |

**1.2 refs** (cạnh `s, p, o, evidence, how, flags`)
| Field | Nghĩa | Ai đọc, để làm gì |
|---|---|---|
| `s` | đơn vị chứa câu dẫn (nguồn của cạnh) | đồ thị, các bước sau |
| `p` | loại quan hệ: `contains`, `part_of`, `refers_to` | đồ thị phân loại cạnh |
| `o` | đơn vị bị dẫn tới (đích) | đồ thị; giai đoạn 2 dùng để biết Điều nào bị ảnh hưởng khi một Điều đổi |
| `evidence` | đoạn nguyên văn làm bằng chứng cho cạnh | cổng kiểm: phải là chuỗi con của chữ đơn vị `s` (`checks.py`); thiếu thì LLM bịa cạnh cũng lọt |
| `how` | ai tìm ra cạnh: `parent` (từ cấu trúc), `regex` | thống kê; sau này chọn mức kiểm chặt hay lỏng |
| `flags` | cờ độ tin cậy, rỗng nghĩa là chắc | giai đoạn 2: cạnh có cờ `isolated` bị giữ lại nhưng không dùng làm căn cứ |

Hai danh sách đi kèm (không phải cạnh):
| Danh sách | Field | Nghĩa |
|---|---|---|
| không giải được | `unit`, `phrase`, `reason` | đơn vị chứa cụm, cụm nguyên văn, vì sao máy không dám đoán đích; đọc ở báo cáo, và là chỗ tầng 2 của S4 sẽ cứu bớt |
| chờ đích | `source`, `edge`, `target_number`, `target_name`, `target_units`, `text` | cụm trỏ sang văn bản chưa có trong kho: văn bản nào, đơn vị nào trong đó, câu nguyên văn; được nối thành cạnh khi văn bản đích được nạp (giai đoạn 2) |

**1.3 delegation** (một điều khoản giao). Mình chưa thấy bước nào hiện tại đọc file này: nó là đầu ra để dành cho 1.8, 1.9 (trả "chưa đủ căn cứ" khi chỗ trống chưa có văn bản lấp) và 2.2.
| Field | Nghĩa |
|---|---|
| `clause_id`, `unit_id` | mã điều khoản giao và đơn vị chứa nó |
| `pattern`, `subpattern` | dạng A, B, D, E (xem mục 1.3 ở trên) |
| `delegate` | bên được giao quy định: Chính phủ, Bộ trưởng... |
| `phrase`, `context` | cụm khớp và câu chứa nó, nguyên văn |
| `flags` | `[]` là ca chắc (regex chặt); `["loose"]` là ca chỉ regex lỏng bắt được, chưa chắc, cần người xem |

`filled_by` (văn bản dưới luật đã lấp chỗ trống) không còn nằm ở đây: bước 2.2 ghi ra `delegation_filled.jsonl` vì cần các văn bản khác.

**1.4 article_type** (nhãn của một Điều)
| Field | Nghĩa | Ai đọc, để làm gì |
|---|---|---|
| `id` | mã Điều (hoặc phụ lục) | khoá để tra |
| `label` | nhãn: `substantive`, `definition`, `effect_transition`, `procedural`, `authority`, `appendix` | 2.3 chỉ tìm câu chỉ thị trong Điều `effect_transition`; đồ thị tô màu theo nhãn; 1.8 sau này chỉ dịch quy tắc cho Điều `substantive` |
| `how` | `regex` (khớp tiêu đề), `default` (không khớp, mặc định `substantive`), `type` (phụ lục) | chỉ báo cáo thống kê |

**1.5 exceptions** (cạnh và nút điều kiện)
| Field | Nghĩa | Ai đọc, để làm gì |
|---|---|---|
| `s` | phần ngoại lệ: một đơn vị, hoặc mã nút điều kiện (dạng `X<mã>`) khi ngoại lệ không phải một đơn vị riêng | đồ thị; 1.7, 1.8 sau này |
| `p` | luôn là `exception_of` | |
| `o` | quy tắc bị ngoại trừ | |
| `evidence` | câu có chữ "trừ", nguyên văn | cổng kiểm chuỗi con; thiếu thì không chứng minh được cạnh |
| `how`, `flags` | như 1.2 | |
| `rule` | tên quy tắc bắt được ca này: `not_apply_pattern`, `except_list_pattern`, `general_except`, `general_except_ref` | thống kê, và biết một ca nằm trong quy tắc nào khi cần sửa |
| nút điều kiện: `id`, `type` | mã nút; luôn là `dieu_kien` | đồ thị vẽ thành nút riêng |
| `kind` | `cu_the` (mệnh đề cụ thể), `tuy_nghi` ("các bên thỏa thuận khác"), `dan_chieu_mo` ("pháp luật có quy định khác") | đồ thị hiển thị; sau này phân biệt ngoại lệ có chỗ lấp hay không |
| `text` | mệnh đề sau "trừ trường hợp", nguyên văn | đồ thị hiển thị |
| `units` | các đơn vị có ngoại lệ này (nhiều đơn vị cùng câu thì dùng chung một nút) | kiểm số lượng nội bộ của bước 1.5 |

**Đã bỏ 11/11 (A16, nguyên tắc "không ai đọc thì bỏ"):** `version` (1.1) và `heading` (1.4). Giữ `source_line` (1.1): chưa ai đọc nhưng giúp truy về dòng nguồn.

## Mẫu thẻ bước (v2, bản gọn, người dùng duyệt 11/11) và thẻ mẫu 1.3
Dùng khi kể lại một bước. Thẻ mô tả CHÍNH BƯỚC (không kể task vừa sửa gì); viết một lần khi thiết kế, sửa khi bước đổi. Khuôn:
```
THẺ BƯỚC <số + tên>: <một câu: biến cái gì thành cái gì>   [giai đoạn, sau bước nào]
1. Nhận vào        dạng dữ liệu, từ file nào; ví dụ thật.
2. Ra              file ghi ra; ví dụ thật cho TỪNG loại dòng ra (kể cả loại "không thành công").
3. Bảng field      mỗi field: Nghĩa | MỌI giá trị có thể có (liệt kê hết, kèm nghĩa) | Ai đọc.
4. Cách làm        các bước máy làm theo thứ tự; ví dụ khớp và KHÔNG khớp; có LLM không.
5. Vì sao          thiếu thì hỏng gì; vì sao cách này, nêu cách khác và vì sao không chọn.
6. Kiểm và số đo   máy kiểm gì; số đo trên dữ liệu thật (đo ở đâu); cái gì chưa kiểm được.
7. Kiểm hiểu       câu hỏi cho người dùng, khoảng 10 câu cho cả một lớp (docs/kiem_hieu.md).
```
Quy ước: thuật ngữ lần đầu có giải nghĩa ngay bên cạnh; mỗi con số ghi đo ở đâu; không viết tắt kiểu "dạng A, B, D" mà nêu từng dạng; ví dụ dòng ra rút gọn field lặp bằng "...". Thẻ của 1.1, 1.2, 1.4, 1.5 chưa viết theo khuôn này: nội dung tương đương đang nằm rải ở các mục "Cách làm", "Ví dụ" và "Giải thích field" bên dưới.

### THẺ BƯỚC 1.3 `delegation`: tìm các chỗ luật giao cho cấp dưới quy định chi tiết [giai đoạn 1, sau 1.1 parse]
**1. Nhận vào.** Chữ (`text`) của mọi Điều, khoản, điểm của BLLĐ (từ 1.1). Ví dụ: `D12.K3` "Chính phủ quy định chi tiết Điều này." · `D35.K1.d` "... được thực hiện theo quy định của Chính phủ." · `D21.K5` "Bộ trưởng Bộ Lao động - Thương binh và Xã hội quy định chi tiết các khoản 1, 2 và 3 Điều này."

**2. Ra.** `data/processed/l3/delegation_clauses.jsonl`, mỗi chỗ giao một dòng (rút gọn bỏ `clause_id`, `context`):
```
dạng A:     {"unit_id":"...D12.K3","pattern":"A","subpattern":null,"delegate":"Chính phủ","phrase":"Chính phủ quy định","flags":[]}
dạng A + C: {"unit_id":"...D107.K3.dd","pattern":"A","subpattern":"C","delegate":"Chính phủ","phrase":"Chính phủ quy định","flags":[]}   (câu: "Trường hợp khác do Chính phủ quy định.")
dạng B:     {"unit_id":"...D35.K1.d","pattern":"B","delegate":"Chính phủ","phrase":"theo quy định của Chính phủ","flags":[]}
dạng D:     {"unit_id":"...D61.K4","pattern":"D","delegate":"Bộ trưởng","phrase":"Bộ trưởng Bộ Lao động - Thương binh và Xã hội ban hành","flags":[]}
dạng E:     {"unit_id":"...D112.K3","pattern":"E","delegate":"Thủ tướng","phrase":"Thủ tướng Chính phủ quyết định","flags":[]}
ca lỏng:    {"unit_id":"...D21.K5","pattern":"loose","delegate":"Bộ trưởng","phrase":"Bộ trưởng Bộ Lao động - Thương binh và Xã hội quy định","flags":["loose"]}
```

**3. Bảng field.** "Bên" là một trong: Chính phủ; Bộ trưởng (có thể kèm tên bộ); Thủ tướng Chính phủ.
| Field | Nghĩa | Mọi giá trị có thể có | Ai đọc |
|---|---|---|---|
| `clause_id` | mã chỗ giao | `DC_<mã đơn vị>_<số thứ tự>`, ví dụ `DC_D12_K3_1` | khoá tra |
| `unit_id` | đơn vị chứa câu giao | mã Điều, khoản hoặc điểm | 2.2 `links` |
| `pattern` | kiểu câu giao | **A** "<bên> quy định ..." (35 ca) · **B** "theo quy định của <bên>" (10) · **D** "Bộ trưởng ... ban hành" (5) · **E** "Thủ tướng Chính phủ quyết định" (1) · **loose** chỉ regex lỏng bắt được (5) | thống kê |
| `subpattern` | dạng phụ | **C**: dạng A có chữ "do" ngay trước ("do Chính phủ quy định"), 2 ca; hoặc rỗng | |
| `delegate` | bên được giao | Chính phủ, Bộ trưởng, Thủ tướng | 1.9 (chưa code) |
| `phrase`, `context` | cụm khớp (nguyên văn) và câu quanh nó (40 ký tự trước, 60 sau) | | người đọc |
| `flags` | độ chắc | `[]` chắc (regex chặt) · `["loose"]` chưa chắc | 2.2 chỉ dùng ca `[]` |

**4. Cách làm** (không LLM).
1. Lấy mọi Điều, khoản, điểm của BLLĐ có chữ.
2. Thử 4 regex chặt A, B, D, E; mỗi chỗ khớp là một dòng chắc. Khớp: "Chính phủ quy định chi tiết". Không khớp: "Bộ trưởng Bộ Lao động **-** Thương binh và Xã hội quy định", vì dạng A chỉ cho các từ toàn chữ cái giữa "Bộ trưởng" và "quy định", dấu gạch ngang chặn lại.
3. Chạy regex lỏng: có <bên> và một động từ giao (quy định, ban hành, hướng dẫn, quyết định) trong cùng câu (bên trước thì cách động từ tối đa 90 ký tự; động từ trước thì cách bên tối đa 50). Ca nào trùng vị trí với ca chắc thì bỏ; còn lại ghi `loose`.
4. Ghi file, in báo cáo, kiểm mốc.

**5. Vì sao.**
- Cần bước này: KB phải biết chỗ nào luật chưa nói hết thì mới trả lời "chưa đủ căn cứ" thay vì trả lời bừa (ví dụ Điều 154 khoản 9 giao Chính phủ quy định giấy phép lao động).
- Regex chứ không LLM: câu giao theo công thức cố định, regex kiểm được hoàn toàn; LLM thì không chứng minh được đúng sai.
- Tầng lỏng thay vì nới regex chặt: nới sẽ bắt nhầm nhiều ca không phải giao (và CLAUDE.md cấm nới quy tắc để bắt thêm ca). Bỏ sót nguy hiểm hơn thừa, nên giữ ca lỏng nhưng gắn cờ.

**6. Kiểm và số đo** (BLLĐ, 11/11).
- Mốc bắt buộc có, thiếu thì bước dừng: `D91.K4` (dạng A), `D154.K1/K2/K9` (B), `D142.K1` (D), `D112` (E).
- Ra 51 ca chắc (A 35 gồm 2 ca C, B 10, D 5, E 1) và 5 ca lỏng. Theo agent đọc: 4 ca lỏng là chỗ giao thật (`D21.K5`, `D73.K4`, `D145.K4`, `D147.K3`), 1 ca nghi không (`D133.K1`: "Chính phủ quyết định Chương trình quốc gia ..."). Chưa ai xác nhận.
- Chưa kiểm được: có câu giao nào cả hai regex đều không thấy không (không có đáp án chuẩn). 51 ca chắc vẫn có thể lẫn vài ca không phải giao chi tiết (regex thô).

**7. Kiểm hiểu:** câu 6, 7, 8 của `docs/kiem_hieu.md`.

## Giai đoạn 2: update engine, `Update(K, d)` cho mỗi ND/TT theo ngày hiệu lực
Theo Thuật toán 1 của Method. VBHN_125 nạp như một văn bản thường.

| Bước | Việc | Dòng Thuật toán 1 | Code cũ | Trạng thái |
|---|---|---|---|---|
| 2.1 | Xử lý văn bản mới bằng 1.1 đến 1.5 | 1 | tái dùng | chưa bàn |
| 2.2 | Nối vào KB: quan hệ chờ đích, `based_on`, `details` (văn bản không nêu số Điều thì LLM chọn trong Δ, giữ khi model thứ hai cùng chọn và từ khoá phạm vi có trong Điều đích) | 1, 5 | `links.py` (cũ `l3_links.py`) | chưa bàn |
| 2.3 | Đọc chỉ thị: regex trước; không thấy thì LLM đề xuất loại thao tác; rồi qua cổng symbolic; vẫn không xếp được thì đánh dấu chưa xác định và cô lập đơn vị bị chạm | 2-3 | `l6_directives.py` | chưa bàn |
| 2.4 | Áp chỉ thị lên phiên bản: đóng phiên bản cũ, mở phiên bản mới, không xoá gì | 4 | `l6_versions.py`, `l6_rare.py` | chưa bàn |
| 2.5 | Tính tập ảnh hưởng A(d) = T(d) ∪ N(T(d)) | 6 | chưa có | chưa bàn |
| 2.6 | Trích lại khái niệm, ngoại lệ ngầm, quy tắc cho A(d); quét lỗi (tái dùng 1.6 đến 1.8) | 7-8 | chưa có | chưa bàn |
| 2.7 | Đối chứng: chạy tăng dần và dựng lại toàn bộ phải ra cùng Π_τ tại cùng ngày | | chưa có | chưa bàn |

## Đối chiếu code cũ với bước mới
L1 → 1.1; L2 → 1.2 (và phần liên văn bản ở 2.2); L3 → 1.3 (quét) và 2.2 (nối); L4 → 1.4; L5 → 1.5; L6 → 2.3, 2.4; L7 → 1.6; L8 → 1.7; L9 → 1.8; L10 → 1.9; L11 → 2.5 đến 2.7; `checks`, `graph`, `viewer` là công cụ phụ (kiểm độc lập, đồ thị gộp, trang xem).

**Tên file sau S1 (11/11):** `l1_parse.py` → `parse.py`; `l2_edges.py` → `refs.py`; `l4_classify.py` → `article_type.py`; `l5_explicit_exceptions.py` → `exceptions_explicit.py`; `l5_general_exceptions.py` → `exceptions_general.py`; `text_norm` dời từ `l6_versions.py` sang `textutil.py` (mới). `l3_links.py` đã tách ở S4 thành `delegation.py` (1.3, quét điều khoản giao) và `links.py` (2.2, nối văn bản). `l6_*.py` chưa đổi (giai đoạn 2). Còn L-số **cố ý** để đầu ra giống hệt mốc: thư mục `data/processed/l1/`, `l2/`..., nhãn bước trong `run_all.py`, bí danh import (`as l1`, `as l2`).

## Số đối chiếu của code cũ (chép từ `docs/tien_do_L0_L6.md` ngày 09/11, chưa đối chiếu lại với đĩa)
Pipeline mới, khi dựng xong phần tương ứng, phải ra lại các số này hoặc giải thích từng chỗ lệch: 10.202 đơn vị và 893 Điều (L1, 18 văn bản); 2.348 `refers_to`, 129 chờ đích (L2); 51 điều khoản giao, 10 `based_on`, 48 `details` (L3); 23 cạnh ngoại lệ tường minh, 336 cạnh và 128 nút điều kiện (L5); 9.217 đơn vị, 9.343 phiên bản, 260 cạnh cập nhật, 15/15 mốc cổng dev (L6); 2.721 cạnh ngữ nghĩa (graph).

## Câu hỏi thiết kế đang mở
1. ~~Cổng symbolic cho nhãn loại Điều (1.4)~~ **Đã giải quyết 11/11 (A14):** bỏ LLM khỏi 1.4 nên không cần cổng.
2. **Điều khoản giao chưa có văn bản lấp** (Điều 154 khoản 9 đang giao cho Chính phủ): nếu suy luận theo kiểu "không chứng minh được thì coi là sai", KB chỉ có BLLĐ sẽ trả "phải có giấy phép lao động" dù đáp án trung thực là "chưa đủ căn cứ". Cần quyết cách để Δ ảnh hưởng tới suy luận. Chưa bàn.
3. **Câu hỏi cổng của giai đoạn 1:** ví dụ giấy phép lao động 45 ngày cần ND_152 và ND_219 nên không dùng được khi KB chỉ có BLLĐ. Cần chọn câu hỏi đo giai đoạn 1.
4. **Hạn mức LLM:** model kiểm chỉ 20 lượt mỗi ngày (`docs/llm_config.md`). Chưa đếm số lượt cần cho 1.6-1.8 trên 220 Điều. Phải đếm trước khi cam kết "mọi bước LLM đều có model thứ hai kiểm".
5. **Bước 2.3 có còn cần nhãn "hiệu lực-chuyển tiếp" của 1.4 không**, hay chỉ regex trên động từ chỉ thị. Code cũ chỉ tìm chỉ thị trong Điều mang nhãn này.
6. **Số bước lan truyền của N(·)** trong tập ảnh hưởng (Method đang ghi [CẦN XÁC MINH]).
7. **Thứ tự mục của Method:** bài xếp 3.4 (update) trước 3.5 (tri thức), thứ tự dựng mới thì ngược lại. Đổi hay không là quyền user.
8. **8 Điều lệch giữa BLLĐ và VBHN_125** (xử lý ở code cũ qua cờ `consolidation_discrepancy`): giờ VBHN_125 là văn bản nạp thường, cần bàn lại cách xử lý ở giai đoạn 2.
