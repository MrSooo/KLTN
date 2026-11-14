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
| 1.6 Sổ khái niệm | P | có (gạch cụm chủ thể, điều kiện, ngoại lệ, kết luận) | cụm phải nằm trong ngữ cảnh của đơn vị = tiêu đề Điều + chapeau khoản cha + chữ đơn vị (user chốt 12/11, A26); đối chiếu với đầu ra của 1.2 và 1.5; KHÔNG dùng model thứ hai kiểm (A25) | chưa có | **12/11: thẻ v5 (bản tối thiểu) đã chốt (A29, A30, A31); đang code giai đoạn A** |
| 1.7 Ngoại lệ ngầm | E: `exception_of` giữa hai đơn vị cùng dùng một khái niệm | có (xét từng cặp) | có câu bằng chứng nguyên văn; hai đầu tồn tại; không tạo vòng | chưa có | **12/11: thẻ nháp bên dưới, các điểm chính đã chốt (A32); chưa code** |
| 1.8 Quy tắc | R (quy tắc s(CASP)), quét lỗi, tự sửa tối đa 2 vòng | có | biên dịch được; chỉ dùng vị từ được phép; bộ quét lỗi; không qua thì cô lập | chưa có | **12/11: thẻ nháp bên dưới, chốt ba câu ở A33; còn mở: nút điều kiện, ngoại lệ lồng nhau, phủ định, hai dạng ngoại lệ; chưa code** |
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
| `rule` | tên quy tắc bắt được ca này: `not_apply_pattern`, `except_list_pattern`, `general_except`, `general_except_ref`, `general_except_noun`, `general_except_noun_ref` (hai giá trị sau là họ "trừ <danh từ>", A24) | thống kê, và biết một ca nằm trong quy tắc nào khi cần sửa |
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
7. Kiểm hiểu       câu hỏi cho người dùng, 10 câu cho MỖI bước (docs/kiem_hieu.md).
```
Quy ước: thuật ngữ lần đầu có giải nghĩa ngay bên cạnh; mỗi con số ghi đo ở đâu; không viết tắt kiểu "dạng A, B, D" mà nêu từng dạng; ví dụ dòng ra rút gọn field lặp bằng "...". Thẻ của cả năm bước 1.1 đến 1.5 đã viết theo khuôn này ở `docs/the_buoc_1_1_den_1_5.md` (12/11/2026); các mục "Cách làm", "Ví dụ" và "Giải thích field" ở trên là bản tóm tắt cũ của cùng nội dung.

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

**7. Kiểm hiểu:** 10 câu mục 1.3 của `docs/kiem_hieu.md` (1.3.1 đến 1.3.10).

### THẺ BƯỚC 1.6 `concepts`: sổ khái niệm, gạch cụm trong chữ luật rồi gắn vào vị từ dùng chung [giai đoạn 1, sau 1.4; giai đoạn A: v5 12/11; giai đoạn B: v6 14/11]
Ý tưởng (đề cương, A29): LLM gạch các cụm trong chữ luật; mỗi cụm gắn vào một vị từ **có sẵn trong sổ** (tái dùng) hoặc một vị từ mới; nhờ dùng chung vị từ mà các điều luật nối được với nhau. User chốt 12/11 (A31): lấy bản tối thiểu này, ra kết quả trước, lỗi sửa sau.

Làm hai giai đoạn: **A** gạch cụm (user chạy `--llm live`; đã chạy xong 204/204 lô ngày 13/11 bằng Claude Sonnet 5.5, kết quả và hai sửa ở A35); **B** đặt tên và tái dùng (v6 14/11: LLM là Claude Sonnet chạy bằng phiên Claude Code, tuần tự theo thứ tự Điều; A37, mục 4 bước 5 đến 10 và 4b). Giai đoạn A cũng chạy bằng phiên Claude Code từ 14/11 (Opus 5.5, lời nhắc concepts-2, A36). Ví dụ dưới đây do agent viết TAY để minh hoạ, chưa có LLM nào chạy ra chúng; các đích dẫn chiếu của `D14.K2` và `D151.K1.d` lấy từ đầu ra thật của 1.2 và 1.5.

**1. Nhận vào.** Mọi đơn vị có chữ nằm dưới Điều nhãn `substantive` hoặc `definition` (từ 1.4): BLLĐ có 881 đơn vị (591 khoản, 245 điểm, 45 Điều có chữ trực tiếp). Kèm mỗi đơn vị là "ngữ cảnh" (A26): tiêu đề Điều + chữ khoản cha (chapeau, nếu là điểm; từ 13/11, A35, khoản đứng dưới Điều có câu dẫn riêng cũng nhận câu dẫn đó làm chapeau) + chữ chính đơn vị. Vì sao cần: 245/245 điểm dựa vào chữ khoản cha; và có khoản không tự mang chủ thể hay kết luận, chúng nằm ở tiêu đề Điều. Ví dụ:
- `D14.K2`: "Hai bên có thể giao kết hợp đồng lao động bằng lời nói đối với hợp đồng có thời hạn dưới 01 tháng, trừ trường hợp quy định tại khoản 2 Điều 18, điểm a khoản 1 Điều 145 và khoản 1 Điều 162 của Bộ luật này."
- `D24.K3`: "Không áp dụng thử việc đối với người lao động giao kết hợp đồng lao động có thời hạn dưới 01 tháng."
- `D154.K1`: "Là chủ sở hữu hoặc thành viên góp vốn của công ty trách nhiệm hữu hạn có giá trị góp vốn theo quy định của Chính phủ." Tiêu đề Điều 154: "Người lao động nước ngoài làm việc tại Việt Nam không thuộc diện cấp giấy phép lao động".
- `D151.K1.d`: "Có giấy phép lao động do cơ quan nhà nước có thẩm quyền của Việt Nam cấp, trừ trường hợp quy định tại Điều 154 của Bộ luật này." Chapeau `D151.K1`: "Người lao động nước ngoài làm việc tại Việt Nam là người có quốc tịch nước ngoài và phải đáp ứng các điều kiện sau đây:"

**2. Ra.** Giai đoạn A ra **bảng cụm** (mỗi cụm một dòng; cột `predicate` còn `null`). Giai đoạn B điền `predicate`, và ra thêm **sổ vị từ** (mỗi vị từ một dòng). Dưới đây là trạng thái sau B:
```
bảng cụm: {"unit":"...D154.K1","span":"không thuộc diện cấp giấy phép lao động","role":"ket_luan","source":"heading","predicate":"exempt_from_work_permit","params":["W"],"targets":[],"how":"llm","flags":[]}
          {"unit":"...D14.K2","span":"hợp đồng có thời hạn dưới 01 tháng","role":"dieu_kien","source":"own","predicate":"contract_term_under_1_month","params":["C"],"targets":[],"how":"llm","flags":[]}
          {"unit":"...D24.K3","span":"hợp đồng lao động có thời hạn dưới 01 tháng","role":"dieu_kien","source":"own","predicate":"contract_term_under_1_month","params":["C"],"targets":[],"how":"llm","flags":["reuse_llm"]}
          {"unit":"...D151.K1.d","span":"quy định tại Điều 154 của Bộ luật này","role":"ngoai_le","source":"own","predicate":null,"params":[],"targets":["BLLD_45-2019.D154"],"how":"cond_node","flags":[]}
sổ vị từ: {"predicate":"contract_term_under_1_month","params":["C"],"kind":"input","anchors":[],"surface":["hợp đồng có thời hạn dưới 01 tháng","hợp đồng lao động có thời hạn dưới 01 tháng"],"used_in":["BLLD_45-2019.D14.K2","BLLD_45-2019.D24.K3"]}
          {"predicate":"exempt_from_work_permit","params":["W"],"kind":"concept","anchors":["BLLD_45-2019.D154.K1"],"surface":["không thuộc diện cấp giấy phép lao động"],"used_in":["BLLD_45-2019.D151.K1.d"]}
cụm bị loại (không qua kiểm): ghi riêng kèm lý do, không vào sổ.
```
Dòng ba là một lần tái dùng đếm được: `surface` có hai chữ khác nhau dùng chung một tên.

**3. Bảng field.**
| Field | Nghĩa | Mọi giá trị có thể có |
|---|---|---|
| `role` | vai của cụm | `chu_the` ai bị quy tắc nói tới · `dieu_kien` khi nào quy tắc áp dụng · `ngoai_le` trừ khi nào · `ket_luan` hệ quả (được, cấm, phải, hưởng ...) |
| `source` | cụm lấy từ đâu của ngữ cảnh | `own` chữ chính đơn vị · `chapeau` chữ khoản cha · `heading` tiêu đề Điều |
| `predicate` | tên vị từ (tiếng Anh, không gồm tham số); điền ở giai đoạn B | chuỗi a-z, 0-9, `_`; `null` khi chưa đặt, hoặc khi cụm có `targets` (cụm là con trỏ tới đơn vị khác) |
| `params` | tham số theo vai, do LLM gán; cụm do máy tạo để `[]` | W người lao động · E người sử dụng lao động · C hợp đồng lao động · J nghề/công việc · G vùng · D ngày/mốc · A số tiền/số lượng |
| `targets` | đơn vị đích mà dẫn chiếu đã giải của 1.2 trỏ tới, chữ dẫn chiếu nằm trọn trong cụm; máy điền, LLM không điền | danh sách id đơn vị; `[]` nếu không có |
| `how` | ai tìm ra cụm | `llm` LLM gạch · `cond_node` máy lấy từ nút điều kiện của 1.5 |
| `flags` | dấu hiệu | `reuse_llm` tên do LLM chọn dùng lại từ chữ khác (A30) · `param_conflict` cùng tên mà khác bộ tham số. Rỗng nếu không có |
| `kind` (sổ) | loại vị từ, máy suy ra | `concept` có đơn vị mà cụm tên này là `ket_luan` (đó là `anchors`) · `input` không có, tức dữ kiện người hỏi tự nêu |
| `surface`, `used_in` (sổ) | các dạng chữ Việt gốc dùng tên này (nhiều chữ khác nhau nghĩa là có tái dùng); đơn vị dùng vị từ (có cụm mang tên này ở vai khác `ket_luan`, hoặc có cụm với `targets` trỏ tới neo hay đơn vị cha của neo) | danh sách |

**4. Cách làm.**
*Giai đoạn A:*
1. Máy đánh dấu từ báo hiệu bằng regex ("nếu", "khi", "trường hợp", "trừ", "không áp dụng", "phải", "được", "bị coi là").
2. LLM (theo lô, đầu ra ép vào 4 vai) gạch cụm nguyên văn từ đơn vị kèm ngữ cảnh và gán tham số. Chỉ gạch chữ có sẵn, không viết lại, không đặt tên.
3. Máy kiểm từng cụm (mục 5); không qua thì loại, ghi riêng kèm lý do.
4. Máy thêm cụm `ngoai_le` từ mỗi nút điều kiện của 1.5 (`how=cond_node`) và điền `targets` cho mọi cụm từ cạnh `refers_to` đã giải của 1.2. Dẫn chiếu do máy nối, LLM không đụng (đây là trường hợp đề cương nêu rõ).

*Giai đoạn B (v6, 14/11). User chốt: đặt tên theo thứ tự Điều kèm ngữ cảnh; reuse chỉ khi cùng nghĩa; model Sonnet; chạy bằng phiên Claude Code; không thử từng lượt (A37). Chỗ có [THÊM] là agent tự đặt, chờ user duyệt.*
5. **Gom chữ (máy).** "Chữ" là một giá trị `text_norm(span)` của các hàng bảng cụm chưa có tên và không có `targets` (cụm LLM và cụm từ nút điều kiện; cụm có `targets` là con trỏ, không đặt tên). BLLĐ: 2909 hàng (2884 cụm LLM và 25 cụm từ nút điều kiện không có `targets`; việc đặt tên cho 25 hàng này [THÊM]: thẻ chỉ nói `predicate` null khi "chưa đặt", và B11 (a) đã ghi thẻ im lặng về chúng), 1833 chữ khác nhau. Mỗi chữ chỉ được hỏi MỘT lần, ở Điều nơi nó xuất hiện đầu tiên; nhờ vậy "cùng chữ thì cùng tên" do cách làm bảo đảm (cấp 1), không phụ thuộc LLM. Máy ghi cho mỗi chữ: dạng chữ đầu tiên (`surface`), các vai gặp, `params` của lần gặp đầu, số lần gặp, và hai lần gặp đầu (đơn vị, tiêu đề Điều, chapeau, chữ đơn vị, vai) [THÊM: ngữ cảnh gửi LLM, chỉ hai lần để lời gửi không phình với chữ lặp 197 lần]. Thứ tự "đầu tiên" là thứ tự đơn vị của các lô 1.6A (`make_batches`), rồi thứ tự cụm trong đơn vị; không phải thứ tự dòng của file jsonl.
6. **Hàng xóm (máy, tính một lần).** Mỗi chữ có danh sách chữ khác có thể cùng nghĩa, tính theo LẦN GẶP ĐẦU của chữ [THÊM: chữ lặp nhiều lần như "người sử dụng lao động" nằm ở rất nhiều Điều nên phải chọn một mốc]: (1) cùng Điều với lần gặp đầu; (2) ở đơn vị nối với đơn vị chứa lần gặp đầu bằng `refers_to` (1.2; thẻ và A29 chỉ nói 1.2) hoặc `exception_of` (1.5, [THÊM]), hai chiều; (3) chung một "từ nội dung" [THÊM]: âm tiết của chữ Việt đã hạ chữ thường, bỏ 30 âm tiết có mặt ở nhiều chữ nhất (đo 14/11: cho, chức, các, có, công, của, dụng, hoặc, hợp, không, lao, luật, làm, người, pháp, quy, quyền, sử, theo, thể, thỏa, thời, trong, tổ, việc, và, được, định, đồng, động). Không dùng `text_norm` để tách âm tiết vì nó bỏ khoảng trắng. Trong mỗi nhóm xếp theo số từ nội dung chung giảm dần rồi theo `text_norm`; giữ tối đa 40 [THÊM].
7. **Chia lượt (máy, tuần tự).** Duyệt Điều theo thứ tự của các lô 1.6A; mỗi lượt tối đa 30 chữ [THÊM: BLLĐ ra 76 lượt; cỡ 20 ra 117 lượt, cỡ 40 ra 56]; gom nguyên các Điều liền nhau cho tới khi thêm Điều kế sẽ vượt 30; Điều có hơn 30 chữ mới thì cắt thành đoạn liền nhau. Chữ không qua cổng ở lượt k được thử lại MỘT lần ở đầu lượt kế, kèm lý do lỗi; lỗi lần hai thì loại (hàng giữ `predicate` null, ghi vào báo cáo). [THÊM: cách thử lại "đưa sang đầu lượt kế" là cơ chế của agent; thẻ chỉ nói "làm lại một lần", mà làm lại cả lượt thì phải chạy lại phần còn lại của chuỗi.] Cổng chạy theo thứ tự mục trong lượt; chữ `reuse` một tên `new` mà chữ đứng trước đặt rồi bị loại ở cổng thì cũng không qua và sang lượt thử lại.
8. **Đặt tên (LLM, Claude Sonnet, mỗi lượt một subagent mới).** Mỗi chữ được đưa kèm ngữ cảnh (hai lần gặp đầu: tiêu đề Điều, chapeau, chữ đơn vị, vai của cụm) và danh sách ứng viên: tối đa 12 tên [THÊM: K=12, chọn lại theo mô phỏng trên dữ liệu khi code] mà các hàng xóm ĐÃ có tên ở lượt trước, cùng `params` với chữ, mỗi tên kèm `params` và tối đa 3 chữ Việt đã dùng tên đó; cộng các tên `new` vừa đặt cho chữ đứng trước trong cùng lượt (cùng `params`) [THÊM: A31 hoãn "tái dùng trong cùng lô"; user chỉ duyệt xếp theo Điều, nên đây là phần agent thêm để hai chữ cùng nghĩa trong một Điều có cơ hội gộp]. LLM trả cho mỗi chữ đúng một mục `reuse: <tên>` hoặc `new: <tên>`. Lời nhắc: `reuse` CHỈ khi cùng nghĩa với ứng viên; gần nghĩa, rộng hơn, hẹp hơn hay trái nghĩa ("có" so với "không có" giấy phép) thì `new`; không chắc thì `new`. Vì sao không gộp cả gần nghĩa: gộp nhầm làm một quy tắc áp sai chỗ (câu trả lời sai), tách sót chỉ làm thiếu cạnh ngoại lệ (câu trả lời rơi về "chưa đủ căn cứ"); cái mất là 1.7 sót cặp (A32 Q2).
9. **Máy kiểm (chặn).** Mỗi chữ có đúng một mục. `reuse`: tên nằm trong tập đã đưa (ứng viên và tên `new` của chữ đứng trước trong lượt) và `params` trùng. `new`: đúng `^[a-z][a-z0-9_]{2,49}$`, dạng khẳng định (không mở đầu bằng `not_`, `no_`, `non_`), chưa có trong sổ, chưa do chữ khác đặt trong cùng lượt.
10. **Dựng sổ (máy).** Sau lượt cuối: điền `predicate` cho mọi hàng theo chữ của nó (hàng giữ `params` riêng); hàng của chữ `reuse` mang cờ `reuse_llm`; hàng có `params` khác `params` của vị từ mang cờ `param_conflict` (không loại); suy `kind`, `anchors`, `surface`, `used_in` theo bảng field; xuất báo cáo (số chữ, số lượt kể cả thử lại, số `reuse`, `new`, loại; mọi vị từ có từ hai chữ Việt; danh sách `param_conflict` và chữ bị loại) và tệp mẫu đọc tay.

Mẫu đọc tay và ngưỡng [THÊM, chờ user duyệt]: toàn bộ quyết định `reuse` nếu không quá 150, quá thì chọn đều 150 theo thứ tự; cộng 50 quyết định `new` mà danh sách ứng viên có tên chung từ nội dung (để ước lượng cái mất của luật "chỉ cùng nghĩa"). Một người đọc, phán đúng, sai hoặc không rõ. Ngưỡng đề xuất: chữ bị loại không quá 2%; quyết định `reuse` đúng không dưới 80% mẫu. Không có đáp án chuẩn nên đây là ước lượng, không phải độ chính xác.

Ví dụ (hai chữ thật trong bảng cụm, đều `dieu_kien` với `params` C): "hợp đồng có thời hạn dưới 01 tháng" (`D14.K2`) và "giao kết hợp đồng lao động có thời hạn dưới 01 tháng" (`D24.K3`). Khi chữ thứ nhất đã có tên, tên đó đủ điều kiện nằm trong danh sách ứng viên của chữ thứ hai: cùng `params` C, chung bốn từ nội dung ("01", "dưới", "hạn", "tháng"), hai Điều khác nhau và 1.2 không nối chúng, nên vào danh sách là nhờ nhóm (3). Thứ hạng của nó trong 12 ứng viên chưa kiểm. "Giao kết" là một hành vi chứ không chỉ tính chất của hợp đồng, nên đây là ca phải phán đoán: trả `reuse` hay `new` đều qua cổng, chỉ mẫu đọc tay phân biệt được.

Với `--llm off`: chỉ có cụm `ngoai_le` từ nút điều kiện của 1.5 kèm `targets`, và dấu từ báo hiệu. Không có cụm chủ thể, điều kiện, kết luận. Giai đoạn B với `off`: `predicate` toàn `null`, sổ vị từ rỗng, báo cáo nói rõ.

**4b. Cách chạy giai đoạn B bằng phiên Claude Code (14/11, A36 và A37).**
- **Trước khi chạy LLM (bước đầu tiên khi code, không gọi LLM) [THÊM]:** đếm bao nhiêu chữ còn ít nhất một ứng viên sau lọc `params` và giới hạn 12. Đo thô 14/11 (chỉ nhóm cùng Điều và nhóm chung từ, chỉ tính chữ đứng trước): 101/1833 chữ (6%) không còn ứng viên nào sau lọc `params`; trung vị 17 ứng viên, 1051 chữ có hơn 12, nên chất lượng xếp hạng quyết định nhiều. Luật dừng đề xuất: nếu bản code cho hơn 20% chữ không có ứng viên thì dừng và báo user trước khi chạy 76 lượt.
- **Một đường code:** `src/concepts_names.py` (chưa viết) chứa mọi hàm dựng chữ, hàng xóm, lượt, cổng, áp kết quả và sổ; dùng chung cho `replay`, nhập cache và `tiep.py` trong thư mục làm việc, để không có hai bản của cùng một luật. [THÊM, lệch A36: `tiep.py` chạy mã của repo trong thư mục làm việc, trong khi thư mục của 1.6A chỉ có file; lý do là lượt sau phụ thuộc kết quả lượt trước nên phải có máy tính lượt kế ngay trong vòng lặp.]
- **Model:** vai cấu hình mới `ten` ở `docs/llm_config.md` (`ten.model = claude-sonnet-5-5`). `trich.model` giữ Opus để `replay` của 1.6A không vỡ (khoá cache có tên model). Mã gọi API vẫn có nhưng không dùng, như 1.6A.
- **Thư mục làm việc ngoài repo** (do `xuat` dựng): `HUONG_DAN.md`, `system.txt`, `schema.json`, `tiep.py`, `trang_thai.json`, `lo/` (chỉ có lượt đã tới), `out/`, `nhat_ky.tsv` (mỗi dòng: số lượt, ID model do subagent tự khai, mức effort ghi tay [THÊM: effort không nằm trong khoá cache nên phải ghi riêng]).
- **Vòng lặp của phiên chính** (phiên chính không tự làm lượt nào): (a) `python3 tiep.py moi` ghi `lo/NNN.json` của lượt kế, hoặc in HẾT hoặc DỪNG; (b) giao MỘT subagent mới, đặt model sonnet tường minh, đọc `system.txt`, `schema.json`, `lo/NNN.json`, ghi `out/NNN.json` và trả đúng một dòng `NNN<tab>ID model`; (c) ghi dòng đó vào `nhat_ky.tsv`; (d) `python3 tiep.py ghi NNN` kiểm cổng, cập nhật trạng thái, chuyển chữ lỗi sang lượt kế; rồi lặp. Không chạy song song vì lượt sau cần tên của lượt trước. `tiep.py` chỉ in MỘT dòng mỗi lệnh (để 76 vòng không làm đầy ngữ cảnh phiên chính); `HUONG_DAN.md` nói rõ chia việc qua nhiều phiên là bình thường.
- **Dừng và tiếp:** trạng thái nằm trên đĩa; hết hạn mức giữa chừng thì phiên mới đọc `HUONG_DAN.md` và tiếp từ (a); `tiep.py` dựng lại trạng thái từ `out/` nếu `trang_thai.json` mất.
- **Dừng sớm [THÊM]:** nếu trong 3 lượt đầu quá 30% chữ không qua cổng thì `tiep.py` in DỪNG và phiên báo lại người dùng. Vì không thử từng lượt (user chọn 14/11) đây là chuông báo duy nhất; nó không bắt được gộp nhầm.
- **Nhập vào repo:** `python -I src/concepts_names.py --nhap <thư mục>` dựng lại từng lượt từ bảng cụm và các `out/` trước đó, ĐỐI CHIẾU với `lo/NNN.json` mà subagent đã đọc (khác một chữ thì từ chối lượt đó và mọi lượt sau), kiểm cổng, kiểm model tự khai bằng `ten.model`, rồi ghi bản ghi cache (`produced_by` là claude_code_sandbox). Khoá cache gồm lời gửi thật của từng lượt nên mọi lượt phụ thuộc các lượt trước: đổi 1.6A, 1.2, 1.5 hay lời nhắc thì khoá đổi từ lượt bị ảnh hưởng trở đi và phải chạy lại từ đó. `replay` làm đúng vòng đó nhưng đọc cache; thiếu bản ghi ở lượt k thì dừng ở k và báo CHƯA ĐỦ như 1.6A.

**5. Máy kiểm.** Các kiểm "chặn" loại cụm; các kiểm "báo" chỉ ghi vào báo cáo, và danh sách ca đã biết nằm trong `checks` (cùng cách với phần "trừ" của 1.5).
- Chặn: cụm do LLM gạch là chuỗi từ liền nhau của ngữ cảnh (so theo TỪ, chặt hơn `text_norm` ở ranh giới từ; `span` ghi ra là đoạn nguyên văn cắt từ chữ gốc; `checks` kiểm lại bằng `text_norm`); vai thuộc 4 vai; `params` chỉ trong W E C J G D A.
- Báo: từ báo hiệu mà chưa có cụm phủ hoặc kề; cụm LLM gạch khác chữ với nút điều kiện của 1.5.
- B, chặn: xem bước 9 của mục 4 (một mục mỗi chữ; `reuse` thuộc tập đã đưa và cùng `params`; tên `new` đúng dạng, chưa có). Cùng tên mà hàng có `params` khác thì chỉ gắn cờ `param_conflict`, không loại.
- Bỏ sót (nói thẳng): cụm đúng chữ nhưng sai vai; gán sai thực thể cho tham số; tái dùng sai nghĩa. Ba loại này không máy nào bắt; chỉ ước lượng bằng mẫu đọc tay (A30).

**6. Không làm ở bản này** (user chốt bản tối thiểu, A31): bảng quan hệ `narrower_than` (sang 1.7, rồi hoãn tiếp: nợ sau một vòng KB, A32), bảng thuật ngữ Việt-Anh, phủ định (`D151.K1.d` "có giấy phép" so với `D153.K2` "không có giấy phép"), đơn vị định nghĩa (thử khi chạy thật; từ 13/11 lời nhắc có quy tắc 6 cho dạng "X là Y": X là `ket_luan`, giải nghĩa là `dieu_kien`; 14/11 thử concepts-3 (thêm vế cho mục danh sách chỉ nêu tên) rồi rút vì làm Opus lặp ket_luan của câu dẫn vào từng khoản D67; lời nhắc cuối là concepts-2; xem A36, chưa đo tác động xuống giai đoạn B).

**7. Rủi ro.**
- Gộp nhầm âm thầm ở B: LLM coi hai khái niệm gần nghĩa là một. Giảm bằng danh sách giới hạn, kiểm `params`, lời nhắc "gần nghĩa thì tách", mẫu đọc tay; không bắt được bằng máy.
- Danh sách ứng viên giới hạn không thấy đồng nghĩa không liên hệ gì (khác Điều, không dẫn chiếu, không chung từ); và có thể ép LLM đặt tên khác dù đồng nghĩa nằm ngoài danh sách.
- Tên tiếng Anh sai nghĩa không đổi kết luận nhưng có thể đánh lừa LLM ở 1.8; lời nhắc 1.8 luôn kèm `surface` chữ Việt.
- `kind` phụ thuộc đúng chữ: điều kiện viết lệch chữ so với kết luận định nghĩa nó có thể thành `input`.
- Bản đầu chưa đo độ chính xác; "xanh" chỉ nghĩa là code chạy và các kiểm chặn qua.
- Chữ giống hệt nhưng khác nghĩa theo ngữ cảnh bị ép một tên (cấp 1 do máy), và LLM chỉ thấy hai lần gặp đầu: đa nghĩa ở lần gặp sau không ai thấy.
- `params` là bộ lọc cứng nhưng do LLM ở giai đoạn A gán, và 1105/3021 cụm LLM không có `params`: hai chữ cùng nghĩa khác `params` không bao giờ gộp (tách sót, theo luật "chỉ cùng nghĩa").
- Tên đầu tiên của một khái niệm là tuỳ ý (phụ thuộc thứ tự); chữ cùng nghĩa nằm ngoài 12 ứng viên không gộp được.
- Phụ thuộc chuỗi: đổi 1.6A, 1.2, 1.5 hay lời nhắc thì phải chạy lại từ lượt bị ảnh hưởng (khoảng 76 lượt nối tiếp).
- Không thử từng lượt (user chọn 14/11): chuông báo duy nhất là dừng sớm; gộp nhầm chỉ thấy sau khi chạy xong, ở mẫu đọc tay.
- Sonnet chưa được đối chiếu với Opus ở việc này.
- Xếp hạng ứng viên rất thô (đếm từ nội dung chung) mà 1051/1833 chữ có hơn 12 ứng viên: tên cùng nghĩa có thể bị đẩy ra ngoài 12 và không bao giờ gộp.
- 101/1833 chữ (6%) không còn ứng viên nào sau lọc `params`: các chữ này luôn là `new`.
- 25 hàng ngoại lệ từ nút điều kiện không có `targets` cũng bị đặt tên, kể cả câu như "quy định tại Mục 1 Chương XI của Bộ luật này" (dẫn chiếu chưa giải): thừa nhưng vô hại; 1.8 quyết dùng hay không (B11 (a)).
- `ket_luan` lặp từ câu dẫn (ít nhất 140/1286 cụm) cùng chữ nên cùng vị từ: một khái niệm có thể có nhiều đơn vị neo (`anchors`) do lặp chứ không do luật nêu lại; chưa đo ảnh hưởng tới `kind`.

**8. Kiểm hiểu:** 10 câu mục 1.6 của `docs/kiem_hieu.md` (đang mô tả bản cũ, sẽ viết lại khi user bảo "kiểm 1.6").

### THẺ BƯỚC 1.7 `exceptions_implicit`: tìm cặp đơn vị mà một bên là ngoại lệ của bên kia dù chữ không ghi "trừ" [giai đoạn 1, sau 1.6 giai đoạn B; NHÁP 12/11]
Các điểm chính đã chốt ở A32 (cạnh do LLM đề xuất được dùng kèm cờ; `narrower_than` hoãn thành nợ; sáu điểm user duyệt ngày 12/11). Chưa code. Chạy được sớm nhất sau khi 1.6A chạy live xong và 1.6B xong.

**1. Nhận vào.** Sổ cụm của 1.6 (cần `predicate` khác `null`, tức giai đoạn B, chưa có); 66 cạnh `exception_of` của 1.5 (BLLĐ); chữ đơn vị.

**2. Ra.** Ba file. `pairs`: mọi cặp đã hỏi LLM, kể cả cặp trả `none`. `edges`: cạnh được nhận. `rejected`: cặp LLM trả cạnh nhưng không qua cổng, kèm lý do.
```
pairs:    {"a":"...", "b":"...", "via":["<vị từ chung>"], "answer":"none", "evidence":""}
edges:    {"s":"<phần ngoại lệ>", "p":"exception_of", "o":"<quy tắc gốc>", "evidence":"<câu nguyên văn>", "how":"llm", "flags":["llm_proposed"]}
rejected: {"a":"...", "b":"...", "answer":"...", "reason":"..."}
```
`s` là phần ngoại lệ, `o` là quy tắc gốc (cùng chiều 1.5). Cạnh mang cờ `llm_proposed`; 1.8 dùng cạnh này, bật/tắt quyết ở 1.8 và 1.9.

| Field | Mọi giá trị có thể có |
|---|---|
| `a`, `b` | mã đơn vị; `a` đứng trước `b` theo thứ tự id |
| `via` | các vị từ chung của hai đơn vị |
| `answer` | `a_exception_of_b` (a là ngoại lệ của b) · `b_exception_of_a` · `none` (không có quan hệ) |
| `evidence` | câu nguyên văn từ ngữ cảnh của `a` hoặc `b`; rỗng khi `none` |

**3. Cách làm.**
1. Máy dựng cặp ứng viên theo Method 3.5: hai đơn vị cùng dùng một vị từ loại `concept` (đơn vị neo của vị từ cũng tính là có dùng). Bỏ cặp đã có `exception_of` ở 1.5 (hai chiều).
2. Máy đếm số cặp trước khi gọi LLM. Vượt ngân sách lượt LLM thì dừng và báo số; bộ lọc chọn cùng user khi có số thật.
3. LLM xét từng cặp, trả một trong ba giá trị kèm câu bằng chứng. Ngữ cảnh gồm tiêu đề Điều, khoản cha (nếu là điểm) và chữ đơn vị, như 1.6 (A26). Lô chia theo đơn vị `a`.
4. Cổng: `answer` hợp lệ; `evidence` là chuỗi liền của ngữ cảnh (so theo `text_norm`); hai đầu tồn tại; không trùng cạnh 1.5; không nằm trong vòng. Cạnh trong vòng không được dùng, ghi vào `rejected` và liệt kê trong báo cáo để đọc lại (theo plan L9, vòng lẻ làm câu hỏi "không có mô hình"; 12/11 đo: 66 cạnh BLLĐ hiện có 0 vòng).

**4. Ví dụ và vì sao.** `D153.K2` ("...không có giấy phép lao động sẽ bị buộc xuất cảnh...") và `D151.K1.d` ("Có giấy phép lao động..., trừ trường hợp quy định tại Điều 154...") cùng nói giấy phép lao động. Theo agent đọc, `D153.K2` là chế tài khi thiếu điều kiện, không phải ngoại lệ, nên đáng trả `none`. Cặp này chỉ tồn tại nếu 1.6B gán "có" và "không có" giấy phép cùng một tên (thẻ 1.6 cấm tiền tố `not_` và chưa xử lý phủ định). Chưa có ví dụ thật về cạnh ngầm. Cần bước này vì thiếu cạnh thì 1.9 trả "kết luận được" thay vì "bị bác", thừa cạnh thì chặn oan quy tắc đúng.

**5. Kiểm và chưa kiểm.** Cổng chỉ chứng minh hình dạng (chuỗi con, tồn tại, vòng), không chứng minh quan hệ ngoại lệ có thật. Hiện chỉ ước lượng được độ chính xác bằng mẫu đọc tay; đề cương (Bảng 2) dự định một bộ quan hệ ngoại lệ chuẩn do học viên gán, khi có thì đo được cả độ bỏ sót. Lỗi lan từ 1.6B: tái dùng sót thì cặp sót.

**6. Không làm ở bản này.** `narrower_than` (nợ, A32; `docs/tien_do.md` mục 13). Ngoại lệ ngầm giữa văn bản (giai đoạn 2).

**6b. Chưa quyết.** Đề cương (dòng 58, 68) phân biệt hai dạng ngoại lệ: tạo kết luận ngược với quy tắc gốc (rebut) và chỉ loại trừ việc áp dụng quy tắc gốc (undercut); bước hỏi đáp dùng sự phân biệt này để tách "bị bác" khỏi "chưa đủ căn cứ". Thẻ này chưa có field cho nó vì chưa quyết ai gán dạng và ở bước nào (66 cạnh của 1.5 cũng chưa có). Quyết cùng thẻ 1.8.

**7. Thứ tự làm.** Làm được trước, test bằng sổ cụm giả: dựng cặp, loại cạnh 1.5, cổng chuỗi con, vòng và trùng, báo cáo. Chờ số thật của 1.6B: ngân sách số cặp, lời nhắc, bộ lọc nếu vượt.

**8. Kiểm hiểu:** chưa viết (mục 1.7 của `docs/kiem_hieu.md` chưa có).

### THẺ BƯỚC 1.8 `rules`: dịch chữ luật thành quy tắc s(CASP), nối ngoại lệ thành quan hệ chặn, quét lỗi, tự sửa, cô lập [giai đoạn 1, sau 1.6B và 1.7; NHÁP 12/11]
Đã chốt ở A33: quy tắc LLM viết được dùng kèm cờ `llm_rule`; bỏ điều kiện "tình huống mẫu" cho tới khi có bộ câu hỏi 1.9. **Thẻ CHƯA hoàn chỉnh**: các điểm "còn mở" ở mục 3b chưa có lời giải. Chưa code. Chạy được sớm nhất sau 1.6A live và 1.6B (s(CASP) đã chạy được từ 12/11, xem A33).

**1. Nhận vào.** Chữ 881 đơn vị BLLĐ thuộc Điều `substantive` hoặc `definition` (1.4); sổ vị từ (1.6B, chưa có); 66 cạnh `exception_of` (1.5; thêm cạnh của 1.7 khi có); tập vị từ được phép của từng Điều.

**2. Ra.** `rules` (đơn vị nguồn, mã s(CASP), cờ `llm_rule`), `blocks` (quan hệ chặn), `isolated` (kèm lý do), báo cáo quét, nhật ký tự sửa. Ví dụ của plan L9 (vị từ chưa có thật): `D151.K1.d` thành `needs_work_permit(W) :- foreign_worker(W), not work_permit_exempt(W).`

**3. Cách làm đã rõ.**
1. Máy tính tập vị từ được phép của mỗi Điều: vị từ của chính đơn vị cộng vị từ của đơn vị nối với nó qua cùng một khái niệm. Đồ thị khái niệm của đề cương (dòng 40) chính là cấu trúc `anchors`/`used_in` của sổ 1.6.
2. LLM viết 0 đến nhiều quy tắc cho mỗi đơn vị (đơn vị không nêu quy tắc thì không có quy tắc, không bị coi là lỗi), chỉ dùng vị từ được phép; thiếu vị từ thì gắn cờ, không tự đặt tên (đề cương dòng 58). Lô chia theo Điều như 1.6.
3. Bộ quét 4 loại ở giai đoạn 1: quy tắc không bao giờ kích hoạt; quy tắc trùng (tự gộp trùng hoàn toàn, chỉ cảnh báo vị từ có thể đồng nghĩa); vòng chặn lẫn nhau; cặp kết luận ngược không có quan hệ chặn.
4. Tự sửa tối đa 2 vòng (LLM nhận thông báo lỗi, chữ luật, vị từ liên quan); nhận khi biên dịch được và không sinh lỗi mới. Không đạt thì cô lập.

**3b. Còn mở (chưa quyết).** (a) 66 cạnh của 1.5 gồm 23 cạnh bắt đầu từ đơn vị và 43 cạnh bắt đầu từ nút điều kiện (34 `cu_the`, 7 `tuy_nghi`, 2 `dan_chieu_mo`; đếm trên BLLĐ). Nút điều kiện không phải quy tắc nên không "chặn" như đơn vị; cần quyết cách đưa vào quy tắc gốc, và `tuy_nghi`, `dan_chieu_mo` không có quy tắc nào kích hoạt được. (b) Ngoại lệ lồng nhau (đề cương dòng 66: quy tắc bị chặn khi có ngoại lệ áp dụng mà ngoại lệ đó không bị chặn bởi ngoại lệ khác): cách biên dịch chưa thiết kế, đây là đóng góp chính của luận văn nên cần bàn riêng. (c) "Bị bác" cần quy tắc kết luận phủ định (đề cương dòng 68 chạy cả φ và ¬φ) mà thẻ 1.6 bản cuối đã loại phủ định. (d) Hai dạng ngoại lệ (đề cương dòng 58, 68): chưa quyết ai gán; agent nghĩ máy đọc được từ hình hai quy tắc (đầu phủ định của quy tắc gốc thì kết luận ngược, điều kiện dưới `not` thì chỉ loại trừ), chưa kiểm. (e) Đề cương dòng 58 ghi "vị từ đầu vào do học viên biên soạn", thẻ 1.6 lại để máy suy ra `kind`: lệch đề cương, user cần nhìn một lần.

**4. Máy kiểm.** Biên dịch được (cần s(CASP)); chỉ dùng vị từ được phép và đúng số tham số; quét sạch. **Không chứng minh được quy tắc dịch đúng nghĩa luật.**

**5. Hoãn sang giai đoạn 2.** Thứ tự ưu tiên theo Điều 58 và các loại quét liên quan phiên bản. Giai đoạn 1 mọi quy tắc cùng một văn bản (cùng cấp, cùng cơ quan, cùng ngày) nên Điều 58 không phân xử được cặp nào; cặp kết luận ngược không có cạnh vào bộ quét và bị cô lập.

**6. Số lượt LLM.** Chưa đo: ít nhất một lô mỗi Điều (204 lô cho BLLĐ) cộng các vòng sửa. Từ 12/11 (A34) bước này dùng vai `trich` (Claude Sonnet 5.5, trả phí theo token), không còn hạn mức 500 lượt/ngày của Gemini.

**7. Kiểm hiểu:** chưa viết.

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
4. **Hạn mức LLM:** 2.2 dùng Gemini (model chính 500 lượt/ngày, `docs/llm_config.md`); từ 12/11 (A34) 1.6 trở đi dùng vai `trich` = Claude Sonnet 5.5, trả phí theo token (chặn an toàn 1000 lượt/ngày của dự án, đo 13/11: 1.6A cả 204 lô hết $2,61 với Sonnet 5.5; Haiku 5.5 ước $0,13, đã đồng ý chuyển nhưng chưa chạy, A35). Đếm 12/11 cho 1.6: 881 đơn vị có chữ, khoảng 152 nghìn ký tự, gom lô thì vừa ngân sách. Model kiểm (20 lượt/ngày) không còn là điều kiện chặn: không dùng LLM kiểm LLM, mỗi bước LLM kiểm bằng cổng máy (A25). Chưa đếm cho 1.7, 1.8.
5. **Bước 2.3 có còn cần nhãn "hiệu lực-chuyển tiếp" của 1.4 không**, hay chỉ regex trên động từ chỉ thị. Code cũ chỉ tìm chỉ thị trong Điều mang nhãn này.
6. **Số bước lan truyền của N(·)** trong tập ảnh hưởng (Method đang ghi [CẦN XÁC MINH]).
7. **Thứ tự mục của Method:** bài xếp 3.4 (update) trước 3.5 (tri thức), thứ tự dựng mới thì ngược lại. Đổi hay không là quyền user.
8. **8 Điều lệch giữa BLLĐ và VBHN_125** (xử lý ở code cũ qua cờ `consolidation_discrepancy`): giờ VBHN_125 là văn bản nạp thường, cần bàn lại cách xử lý ở giai đoạn 2.
