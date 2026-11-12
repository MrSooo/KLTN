# Thẻ bước 1.1 đến 1.5 (giai đoạn 1: dựng KB gốc)

Tổng hợp theo mẫu "thẻ bước v2" (`docs/pipeline_moi.md`, mục "Mẫu thẻ bước"). Viết 12/11/2026. Thẻ mô tả CHÍNH BƯỚC; sửa khi bước đổi.

**Cách đọc file này**
- Số đo lấy lại trên đĩa ngày 12/11 sau `python -I src/run_all.py --llm replay --viewer --tests` (12/12 bước). Toàn kho: 18 văn bản, 10.202 đơn vị, 893 Điều, 2.348 cạnh `refers_to`, 129 chờ đích, 127 không giải được, 56 điều khoản giao.
- "BLLĐ" là số đo chỉ trên Bộ luật Lao động 45/2019 (220 Điều). "Kho" là số đo trên cả 18 văn bản. Số nào không ghi thì xem câu chứa nó.
- **[PHÁT HIỆN n]** là chỗ dữ liệu mâu thuẫn với thiết kế. Gom ở mục cuối file. PHÁT HIỆN 1, 2, 3 đã được sửa ngay trong ngày 12/11 (quyết định A21, A22, A23 ở `docs/quyet_dinh/pipeline_moi_quyet_dinh.txt`); các số đo bên dưới là số SAU khi sửa, số cũ ghi kèm ở chỗ cần so.
- Thẻ 1.3 chép nguyên từ `docs/pipeline_moi.md` (số đã kiểm lại 12/11, khớp).
- "Ai đọc" lấy từ việc tìm trong code ngày 12/11. Dấu **—** nghĩa là chưa bước nào đọc.

**Năm bước nhìn nhanh** (cả năm đều KHÔNG dùng LLM: là regex, máy kiểm được hoàn toàn)

| Bước | Nhận | Ra |
|---|---|---|
| 1.1 `parse` | file `.txt` + dòng `manifest.csv` | đơn vị (Chương, Mục, Điều, Khoản, Điểm, phụ lục) dạng `(s, p, o)` |
| 1.2 `refs` | đơn vị của 1.1 | cạnh cha-con, cạnh `refers_to`, danh sách chờ đích, danh sách không giải được |
| 1.3 `delegation` | chữ của đơn vị | điều khoản giao quy định chi tiết |
| 1.4 `article_type` | tiêu đề Điều | một nhãn cho mỗi Điều |
| 1.5 `exceptions` | chữ của đơn vị + cách giải dẫn chiếu của 1.2 | cạnh `exception_of`, nút điều kiện |

Thứ tự phụ thuộc: 1.1 xong thì 1.2, 1.3, 1.4 chạy được; 1.5 cần cả 1.1 và 1.2.

---

## THẺ BƯỚC 1.1 `parse`: biến file chữ của một văn bản thành các đơn vị có mã và có cha [giai đoạn 1, bước đầu]

**1. Nhận vào.** File `.txt` (UTF-8, mỗi đoạn một dòng, giữa các đoạn có dòng trống) trong `data/raw/labor/{base,dev}/`, và dòng của văn bản đó trong `manifest.csv` (số hiệu, loại, ngày, số Điều). Ví dụ: đầu Điều 14 của BLLĐ (`BLLD_45-2019.txt`, dòng 204 đến 210, rút gọn):
```
204  Điều 14. Hình thức hợp đồng lao động
206  1. Hợp đồng lao động phải được giao kết bằng văn bản và được làm thành 02 bản, ...
208  Hợp đồng lao động được giao kết thông qua phương tiện điện tử dưới hình thức thông điệp dữ liệu ...
210  2. Hai bên có thể giao kết hợp đồng lao động bằng lời nói đối với hợp đồng có thời hạn dưới 01 tháng, trừ trường hợp ...
```
Dòng 208 không có nhãn (không bắt đầu bằng "Điều", số khoản hay chữ điểm).

**2. Ra.** `data/processed/l1/` mỗi văn bản một bộ file, và `data/processed/documents.jsonl` (một dòng một văn bản). Ví dụ thật cho từng loại dòng:
```
đơn vị (l1_triples_*): mỗi đơn vị là vài dòng cùng chủ thể s
{"s":"BLLD_45-2019.D14","p":"type","o":"dieu"}
{"s":"BLLD_45-2019.D14","p":"heading","o":"Hình thức hợp đồng lao động"}
{"s":"BLLD_45-2019.D14","p":"parent","o":"BLLD_45-2019.CIII.M1"}            cha của Điều 14 là Mục 1 Chương III
{"s":"BLLD_45-2019.D14","p":"source_line","o":204}                           (Điều không có dòng "text": chỉ có tiêu đề)
{"s":"BLLD_45-2019.D14.K2","p":"parent","o":"BLLD_45-2019.D14"}              cha của khoản 2 là Điều 14
{"s":"BLLD_45-2019.D14.K2","p":"text","o":"Hai bên có thể giao kết hợp đồng lao động bằng lời nói ..."}

khối trích dẫn (l1_payloads_*), ND_70-2023: câu dẫn rồi khối “...” của văn bản KHÁC
{"payload_id":"ND_70-2023.Q1","first_line":36,"last_line":36,"lead_text":"a) Sửa đổi, bổ sung điểm a khoản 3 Điều 3 như sau:","lead_line":34,
 "lead_unit":"ND_70-2023.D1.K1.a","lines":["“a) Tốt nghiệp đại học trở lên hoặc tương đương và có ít nhất 3 năm kinh nghiệm ... Việt Nam.”."]}

bảng ghép (l1_tables_*), ND_74-2024 (trong file gốc mỗi ô một dòng: "Vùng I" / "4.960.000" / "23.800" / ...)
{"table_id":"ND_74-2024.D3.K1.T1","unit":"ND_74-2024.D3.K1","columns":["vung","muc_thang","muc_gio"],"rows":[{"vung":"I","muc_thang":4960000,"muc_gio":23800}, ... (4 vùng)]}

chú thích (l1_footnotes_*), chỉ văn bản hợp nhất VBHN_125-2025
{"n":1,"text":"Luật Công nghiệp công nghệ số số 71/2025/QH15 có căn cứ ban hành như sau: ..."}

đầu văn bản (documents.jsonl), BLLĐ
{"doc_id":"BLLD_45-2019","number":"45/2019/QH14","doc_type":"bo_luat","issuer":"Quốc hội","level":1,"issued":"2019-11-20","effective_from":"2021-01-01",
 "title":"Bộ luật Lao động (bản gốc)","grounds":["Căn cứ Hiến pháp ...;"],"flags":[],"group":"base"}

loại "không thành công": KHÔNG ghi file dữ liệu; in ra stderr rồi thoát mã 1. Dữ liệu hiện tại có 0 lỗi nên không có dòng thật; dạng theo mã nguồn:
LỖI PARSE <doc_id>:
  dòng <số>: Điều 9 sau Điều 7
```
Báo cáo chữ: `docs/bao_cao_chay/l1/l1_report_<doc_id>.txt` (luôn ghi, kể cả khi lỗi).

**3. Bảng field.**

Mã đơn vị (cột `s`):
| Loại | Mã | Ví dụ |
|---|---|---|
| Chương | `<doc_id>.C<số La Mã>` | `BLLD_45-2019.CIII` |
| Mục | mã Chương + `.M<n>` | `BLLD_45-2019.CIII.M1` |
| Điều | `<doc_id>.D<n>` (KHÔNG chứa Chương; Điều chèn có hậu tố chữ: `D8a`) | `BLLD_45-2019.D14` |
| Khoản | mã Điều + `.K<n>` | `BLLD_45-2019.D14.K2` |
| Điểm | mã khoản (hoặc Điều) + `.<chữ>`; chữ `đ` viết thành `dd` | `BLLD_45-2019.D107.K3.dd` |
| Phụ lục | `<doc_id>.PL...`, mục trong phụ lục `.M<n>`, dòng `.R<k>` | `ND_90-2019.PL_1` |

Cột `p` (tên thuộc tính; `o` là giá trị):
| `p` | Nghĩa | Mọi giá trị có thể có | Ai đọc |
|---|---|---|---|
| `type` | loại đơn vị | `chuong` (kho 76), `muc` (90), `dieu` (893), `khoan` (3.014), `diem` (3.006), `pl` phụ lục (28), `pl_muc` mục trong phụ lục (74), `pl_row` một dòng phụ lục (3.021); tổng 10.202 | mọi bước |
| `number` | số hoặc chữ thứ tự gốc | chuỗi: "14", "8a", "a", "a1", số La Mã (Chương) | kiểm số thứ tự lúc parse; đồ thị hiển thị |
| `heading` | tiêu đề | chỉ Chương, Mục, Điều và phụ lục có; kho 1.159 đơn vị | 1.4 (gắn nhãn); đồ thị |
| `parent` | mã đơn vị cha | mã của một đơn vị khác; Chương, phụ lục, và Điều của văn bản không chia Chương thì không có cha (kho: 10.035 trên 10.202 đơn vị có cha) | 1.2 (cạnh cha-con); các bước cần "đi lên Điều chứa nó" |
| `text` | chữ nguyên văn của đơn vị, các đoạn nối bằng xuống dòng | chuỗi; đơn vị không có chữ thì không có dòng này | 1.2, 1.3, 1.5, 2.3; nguồn của mọi `evidence` |
| `scope` | phụ lục không bóc chi tiết | duy nhất `out_of_scope` (kho 15 đơn vị, đều ở `NQ_66-16-2026`; BLLĐ không có) | `l6_versions.py` (đặt cờ `out_of_scope`) |
| `footnote` | số chú thích `[n]` gắn với đơn vị (văn bản hợp nhất) | số nguyên (kho: 1 dòng, ở `VBHN_125-2025`; BLLĐ không có) | `l6_versions.py` |
| `source_line` | dòng của đơn vị trong file `.txt` gốc | số nguyên | — (để truy về nguồn) |

Các file còn lại:
| File | Nghĩa | Kho / BLLĐ | Ai đọc |
|---|---|---|---|
| `l1_payloads_*` | khối trích dẫn “...” đứng sau câu dẫn; KHÔNG là đơn vị của văn bản chứa nó | kho 30 (BLLĐ 4: Điều 219 sửa Luật BHXH; `ND_70-2023` 22; `VBHN_125-2025` 4) | 2.3 (`l6_directives.py`) |
| `l1_tables_*` | bảng lương vùng đã ghép lại | kho 1 (`ND_74-2024`); BLLĐ 0 | — (chỉ test đọc) |
| `l1_footnotes_*` | chú thích cuối văn bản hợp nhất | kho 3 (`VBHN_125-2025`) | `l6_*` qua `footnote` |
| `documents.jsonl` | đầu văn bản: `doc_id`; `number` số hiệu; `doc_type` (`bo_luat` 1, `van_ban_hop_nhat` 1, `nghi_dinh` 10, `nghi_quyet_cp` 1, `thong_tu` 5); `issuer` (Quốc hội, Văn phòng Quốc hội, Chính phủ, Bộ); `level` (1 luật và văn bản hợp nhất, 2 nghị định và nghị quyết CP, 3 thông tư); `issued`, `effective_from`; `title`; `grounds` (các dòng "Căn cứ ..."); `group` (`base`, `dev`); `flags` | `flags` hiện có 2 giá trị: `header_from_manifest` (3 văn bản mất phần đầu: TT_09, TT_10, TT_11), `issued_uncertain` (2 văn bản); còn dạng `so_hieu_lech_manifest:<số>`, `ngay_ky_lech_manifest:<ngày>` khi lệch manifest (hiện 0) | 1.2 (`refs.py` tra văn bản đích theo số hiệu và loại); các field khác chưa kiểm ai đọc |

**4. Cách làm** (không LLM).
1. Đọc file, chuẩn hoá chữ (NFC, bỏ khoảng trắng thừa); không giả định `\r\n`.
2. Một máy trạng thái giữ "con trỏ hiện tại" ở mỗi cấp. Mỗi dòng được nhận dạng bằng regex ở ĐẦU dòng: `Chương <La Mã>`, `Mục <số>`, `Điều <số>.`, `<số>.` rồi khoảng trắng (khoản), `<chữ>)` (điểm; chữ là `a b c d đ e g h i k l m n o p q`, không có f j w z). Khớp: `Điều 14. Hình thức ...`, `2. Hai bên ...`. KHÔNG khớp khoản: `4.960.000 đồng/tháng` (sau dấu chấm là chữ số, khoản cần khoảng trắng).
3. Gặp đơn vị mới thì cha của nó là con trỏ cấp trên ngay lúc đó, và các con trỏ cấp dưới bị xoá. Mã = mã cha + nhãn.
4. Dòng không nhãn: bắt đầu bằng gạch đầu dòng thì nối vào đơn vị sâu nhất đang mở; còn lại nối vào khoản đang mở (chưa có khoản thì vào Điều), kể cả khi một điểm đang mở (có ghi chú trong báo cáo; BLLĐ 4 ca).
5. Khối trích dẫn “...” sau câu dẫn thành payload, không thành đơn vị. Phần đầu văn bản, "Nơi nhận", mục lục phụ lục, bảng lương, chú thích đi riêng.
6. Kiểm cổng (mục 6). Đạt mới ghi file.

**5. Vì sao.**
- Cần bước này: mọi bước sau cần biết "đơn vị nào, cha là ai, chữ là gì". Một đơn vị cắt sai thì dẫn chiếu, điều khoản giao, nhãn, ngoại lệ ở 1.2 đến 1.5 và mọi phiên bản về sau đều tính trên đơn vị sai.
- Regex và máy trạng thái chứ không LLM: cấu trúc luật có quy ước chặt (Điều, khoản, điểm), regex kiểm chứng được hoàn toàn; LLM không chứng minh được đúng sai và không cần hiểu nghĩa ở đây.
- Mã Điều không chứa Chương: lý do mình suy ra, chưa thấy ghi trong quyết định: luật dẫn chiếu theo số Điều ("Điều 14"), không theo Chương, nên mã bám cách dẫn chiếu; Điều thuộc Mục hay Chương nằm ở `parent`.
- Khối trích dẫn không thành đơn vị: nó chứa dòng kiểu "Điều 32. ..." của văn bản bị sửa; nếu thành đơn vị thì Điều của hai văn bản lẫn nhau. Nó được giữ riêng để 2.3 đọc chỉ thị sửa đổi.
- Dừng khi bất thường (fail-closed), không đoán rồi đi tiếp: cắt sai im lặng sẽ lan xuống mọi bước sau mà không ai thấy.
- Dạng `(s, p, o)`: cùng khuôn với cạnh của đồ thị (ưu), đổi lại mã lặp ở mỗi dòng nên nhiều dòng hơn một bản ghi gộp mỗi đơn vị (nhược).

**6. Kiểm và số đo.**
- Cổng (sai thì thoát mã 1, không ghi dữ liệu): số Điều bằng cột `so_dieu_dem_duoc` của manifest (kho: 893, khớp); số thứ tự liền (Điều n sau n-1; Điều chèn `8`, `8a`, `8b`; điểm theo bảng chữ); mã không lặp; nháy “ ” cân bằng; chú thích `[n]` liên tục; gặp cấp Phần hoặc Tiểu mục thì báo lỗi.
- BLLĐ 1.166 đơn vị: 17 chương, 24 mục, 220 điều, 638 khoản, 267 điểm. Cả 18 văn bản: 0 lỗi parse.
- Chưa kiểm được: chỉ Điều có số đối chiếu độc lập (manifest). Khoản và điểm chỉ kiểm thứ tự liền, không có số đếm riêng; một khoản bị nhận nhầm mà vẫn liền số thì lọt. Điều "đủ số lượng" cũng không chứng minh từng Điều cắt đúng chỗ.

**7. Kiểm hiểu:** 10 câu mục 1.1 của `docs/kiem_hieu.md` (1.1.1 đến 1.1.10). Lần kiểm 12/11: 1/10, cần học lại.

---

## THẺ BƯỚC 1.2 `refs`: tìm các câu dẫn chiếu ("khoản 2 Điều 18", "Điều này", "Nghị định này") và nối thành cạnh [giai đoạn 1, sau 1.1 parse]

**1. Nhận vào.** Đơn vị của 1.1 (cả 18 văn bản, vì một cụm có thể trỏ sang văn bản khác) và `documents.jsonl` (để tra văn bản đích theo số hiệu, loại). Ví dụ: `BLLD_45-2019.D14.K2` "... trừ trường hợp quy định tại khoản 2 Điều 18, điểm a khoản 1 Điều 145 ..."; `ND_145-2020.D8.K1` "... khoản 1, 2, 3, 4, 6, 7, 9 và 10 Điều 34 của Bộ luật Lao động".

**2. Ra.** `data/processed/l2/`, mỗi văn bản bốn file; thêm `data/processed/pending_links.jsonl` (chờ đích của cả kho). Ví dụ thật cho từng loại:
```
cạnh cha-con (l2_edges_*), mỗi cặp 2 chiều
{"s":"BLLD_45-2019.D14","p":"contains","o":"BLLD_45-2019.D14.K2","evidence":"","how":"parent","flags":[]}
{"s":"BLLD_45-2019.D14.K2","p":"part_of","o":"BLLD_45-2019.D14","evidence":"","how":"parent","flags":[]}

refers_to nối được (l2_refs_*)
{"s":"BLLD_45-2019.D14.K2","p":"refers_to","o":"BLLD_45-2019.D145.K1.a","evidence":"điểm a khoản 1 Điều 145","how":"regex","flags":[]}
{"s":"ND_145-2020.D3.K3","p":"refers_to","o":"ND_145-2020.D3.K2","evidence":"khoản 2 Điều này","how":"regex","flags":[]}
(một cụm nhiều đối số ra nhiều cạnh: ND_145-2020.D8.K1, 1 cụm "khoản 1, 2, 3, 4, 6, 7, 9 và 10 Điều 34 của Bộ luật Lao động" ra 8 cạnh tới BLLD_45-2019.D34.K1 ... K10)

chờ đích (l2_pending_*): trỏ tới văn bản chưa có trong kho
{"source":"ND_12-2022.D3.K2.k","edge":"refers_to","target_number":null,"target_name":"Luật Người lao động Việt Nam","target_units":["D9.K1","D9.K2","D9.K3","D9.K4"],"text":"khoản 1, 2, 3, 4 Điều 9 của Luật Người lao động Việt Nam"}

không giải được (l2_unresolved_*): máy đọc ra cụm nhưng không dám đoán đích
{"unit":"ND_12-2022.D7.K7","phrase":"điểm đ khoản 5, khoản 6 Điều này","reason":"mục cấp trên có nhiều hơn một đối số"}
{"unit":"ND_135-2020.D5.K1.d","phrase":"điểm a","reason":"cụm kết thúc bằng khoản/điểm, không có Điều"}
{"unit":"ND_145-2020.D1.K1","phrase":"khoản 3 Điều 12","reason":"đích ND_145-2020.D12.K3 không có trong ND_145-2020 (cụm không nêu văn bản đích; văn bản đích có thể nằm ở câu dẫn, việc của L3)"}   ("L3" trong lý do là tên cũ, nay là 2.2)

dòng chỉ thị sửa đổi: không ra file, chỉ đếm trong báo cáo (BLLĐ 7 dòng), ví dụ "Sửa đổi, bổ sung Điều 54 như sau:" ở BLLD_45-2019.D219.K1.a
```

**3. Bảng field.**

Cạnh (`l2_edges_*`, `l2_refs_*`):
| Field | Nghĩa | Mọi giá trị có thể có | Ai đọc |
|---|---|---|---|
| `s` | nguồn của cạnh | mã đơn vị: với `contains` là cha, với `part_of` là con, với `refers_to` là đơn vị chứa câu dẫn | đồ thị |
| `p` | loại quan hệ | `contains` (kho 10.035), `part_of` (10.035), `refers_to` (2.348) | đồ thị; 1.5 dùng cách giải của `refers_to`; giai đoạn 2 biết Điều nào bị ảnh hưởng khi một Điều đổi |
| `o` | đích | mã đơn vị | đồ thị |
| `evidence` | đoạn nguyên văn làm bằng chứng | `""` (cạnh cha-con, lấy từ cấu trúc) hoặc cụm dẫn chiếu nguyên văn | cổng kiểm: phải là chuỗi con của chữ đơn vị `s` (`checks.py`); thiếu thì không kiểm tự động được |
| `how` | ai tìm ra cạnh | trong dữ liệu 1.2 chỉ có `parent` (cạnh cha-con) và `regex` (`refers_to`); khuôn cạnh chung còn `llm`, `keyword` dành cho bước khác | thống kê |
| `flags` | cờ độ tin cậy | luôn `[]` ở 1.2 (22.418 cạnh đều rỗng); giai đoạn 2 để dành cờ như `isolated` | — |

Chờ đích (`l2_pending_*`):
| Field | Nghĩa | Giá trị |
|---|---|---|
| `source` | đơn vị chứa cụm | mã đơn vị |
| `edge` | loại cạnh sẽ tạo khi nối | `refers_to` |
| `target_number` | số hiệu văn bản đích | số hiệu hoặc `null` (kho: 101 trên 129 không có số hiệu) |
| `target_name` | tên văn bản đích khi không có số | tên hoặc `null` (kho: 15 không tên; 17 "Luật Người lao động Việt Nam"; 13 "Bộ luật Lao động"; còn lại là tên đủ như "Luật Bảo hiểm xã hội" 48, "Luật Xử lý vi phạm hành chính" 11). **[PHÁT HIỆN 3, đã sửa A23]** trước 12/11 nhiều tên bị cắt ("Luật Bảo", "Luật Xử") |
| `target_units` | đơn vị đích, viết tương đối so với văn bản đích | `["D9.K1", ...]` |
| `text` | cụm nguyên văn | chuỗi |
Ai đọc: giai đoạn 2 (nối thành cạnh khi văn bản đích được nạp).

Không giải được (`l2_unresolved_*`): `unit`, `phrase`, `reason`. Kho 127 dòng, năm nhóm lý do: (1) "phụ lục <mã> không có trong kho (file nguồn không kèm phụ lục này)" 50; (2) "đích <mã> không có trong <văn bản>" 38 (37 ca "cụm không nêu văn bản đích" và 1 ca nêu BLLĐ); (3) "mục cấp trên có nhiều hơn một đối số" 24; (4) "cụm kết thúc bằng khoản/điểm, không có Điều" 13; (5) "'điểm này' chưa có quy tắc" 2. Ai đọc: báo cáo; là chỗ "tầng 2" (hoãn, B10) định cứu bớt.

**4. Cách làm** (không LLM).
1. Cạnh cha-con: mỗi cặp (cha, con) lấy từ `parent` của 1.1 thành hai cạnh `contains` và `part_of`. Kiểm: đối xứng, mỗi đơn vị đúng một cha, kiểu cha hợp lệ (khoản có cha là Điều).
2. Tìm cụm dẫn chiếu bằng regex: chuỗi "từ khoá + đối số" với `điều | khoản | điểm`, đối số là số, chữ, hoặc "này"; danh sách ("khoản 1, 2 và 3"); nối bằng "của" ("khoản 6 của Điều 7"). Sau cụm có thể có "đuôi" nêu văn bản: "này", số hiệu ("số 10/2012/QH13"), hoặc tên ("Bộ luật Lao động"). "Phụ lục I" xử riêng.
3. Giải ra mã đích: cấp nào thiếu thì suy từ vị trí đơn vị chứa cụm ("khoản 2 Điều này" ở `D3.K3` thành `D3.K2`); đuôi nêu văn bản khác thì tra theo số hiệu; "Bộ luật Lao động" thì trỏ BLLĐ 2019 nếu văn bản nguồn ban hành sau BLLĐ 2019 hoặc là chính nó, còn nếu trước đó thì trỏ BLLĐ 2012 (ngoài kho, thành chờ đích số `10/2012/QH13`, kho 13 ca).
4. Mỗi cụm có đúng một kết cục: nối (có cạnh), chờ đích, hoặc không giải được kèm lý do. Không chắc thì KHÔNG đoán.
5. Dòng chỉ thị sửa đổi ("Sửa đổi, bổ sung khoản 6 Điều 7 như sau:") không sinh `refers_to`: dẫn chiếu trong đó trỏ vào văn bản bị sửa, việc của 2.3.

**5. Vì sao.**
- Cần bước này: để biết điều này dựa vào điều kia. Khi một Điều đổi ở giai đoạn 2, các Điều trỏ tới nó bị ảnh hưởng; 1.5 cần cách giải này để biết "Điều 108 của Bộ luật Lao động" là đơn vị nào.
- Ba kết cục thay vì hai: "chờ đích" tách ca "văn bản đích chưa nạp, sẽ nối sau" (không phải lỗi) khỏi ca "máy không dám đoán". Gộp lại thì không biết ca nào sửa được bằng cách nạp thêm văn bản.
- Không đoán: một cạnh nối sai im lặng sẽ lan xuống mọi bước dùng nó.
- Hai chiều `contains` và `part_of`: để đi lên và đi xuống bằng một phép tra, không phải quét ngược (lý do mình suy ra).
- Chỉ thị sửa đổi bỏ qua: nếu tính thì "Điều 7" ở đó bị hiểu thành Điều 7 của chính nghị định, trong khi nó là Điều 7 của văn bản bị sửa.

**6. Kiểm và số đo.**
- Cổng: mỗi cụm đúng một kết cục; không cạnh nào trỏ tới mã không tồn tại; cạnh cha-con đối xứng.
- Kho: 1.896 cụm; 2.348 `refers_to`; 129 chờ đích; 127 không giải được. BLLĐ: 186 cụm = 245 cạnh + 1 chờ đích (Bộ luật Tố tụng dân sự, từ Điều 219) + 0 không giải được; 7 dòng chỉ thị bỏ qua.
- Cổng phần dư: đếm từ khoá điều/khoản/điểm kèm số nằm NGOÀI mọi cụm: 0 ở cả 18 văn bản. Con số này chưa chứng minh regex bắt hết: nó dùng cùng họ regex để đếm, nên câu dẫn chiếu viết theo cách cả hai đều không thấy thì cả hai cùng sót; và nó không bắt được cụm bắt đúng nhưng giải sai đích.
- Chưa kiểm được: đích đúng ý người viết hay không (máy chỉ kiểm đích tồn tại). Tầng 2 (13 ca khoản/điểm trơ trụi, đều ở nghị định, thông tư; BLLĐ 0 ca) hoãn.
- **[PHÁT HIỆN 3, đã sửa A23 ngày 12/11]** Tách tên văn bản đích (`parse_tail`) có hai lỗi: cắt tên ở chữ thường đầu tiên ("Luật Bảo" thay vì "Luật Bảo hiểm xã hội", 71 trên 129 chờ đích) và nhảy qua dấu câu nên dính chữ đầu câu sau ("Bộ luật Lao động Trường", 7 `evidence` của `refers_to`). Sau sửa số cạnh không đổi (2.348 / 129 / 127), chỉ chuỗi đổi. Còn lại: danh sách từ dừng viết tay; "Luật Người lao động Việt Nam" vẫn là tiền tố của tên đủ; 101 trên 129 chờ đích vẫn không có số hiệu, nên nối theo tên ở giai đoạn 2 vẫn cần quy tắc so khớp.

**7. Kiểm hiểu:** 10 câu mục 1.2 của `docs/kiem_hieu.md` (1.2.1 đến 1.2.10).

---

## THẺ BƯỚC 1.3 `delegation`: tìm các chỗ luật giao cho cấp dưới quy định chi tiết [giai đoạn 1, sau 1.1 parse]
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

**6. Kiểm và số đo** (BLLĐ, kiểm lại 12/11: 56 dòng = 35 + 10 + 5 + 1 + 5 lỏng).
- Mốc bắt buộc có, thiếu thì bước dừng: `D91.K4` (dạng A), `D154.K1/K2/K9` (B), `D142.K1` (D), `D112` (E).
- Ra 51 ca chắc (A 35 gồm 2 ca C, B 10, D 5, E 1) và 5 ca lỏng. Theo agent đọc: 4 ca lỏng là chỗ giao thật (`D21.K5`, `D73.K4`, `D145.K4`, `D147.K3`), 1 ca nghi không (`D133.K1`: "Chính phủ quyết định Chương trình quốc gia ..."). Chưa ai xác nhận.
- Chưa kiểm được: có câu giao nào cả hai regex đều không thấy không (không có đáp án chuẩn). 51 ca chắc vẫn có thể lẫn vài ca không phải giao chi tiết (regex thô).

**7. Kiểm hiểu:** 10 câu mục 1.3 của `docs/kiem_hieu.md` (1.3.1 đến 1.3.10).

---

## THẺ BƯỚC 1.4 `article_type`: gắn cho mỗi Điều (và mỗi phụ lục) một nhãn cho biết nó đi tiếp tới đâu [giai đoạn 1, sau 1.1 parse]

**1. Nhận vào.** Tiêu đề (`heading`) của mọi Điều, và các đơn vị loại `pl` (phụ lục), từ 1.1. Ví dụ BLLĐ: `D3` "Giải thích từ ngữ"; `D1` "Phạm vi điều chỉnh"; `D18` "Thẩm quyền giao kết hợp đồng lao động"; `D120` "Hồ sơ đăng ký nội quy lao động"; `D220` "Hiệu lực thi hành".

**2. Ra.** `data/processed/l4/l4_labels.jsonl`: 921 dòng = 893 Điều + 28 phụ lục, mỗi Điều hoặc phụ lục một dòng:
```
{"id":"BLLD_45-2019.D3","label":"definition","how":"regex"}          tiêu đề khớp một mẫu
{"id":"BLLD_45-2019.D1","label":"substantive","how":"default"}       không khớp mẫu nào, mặc định
{"id":"ND_90-2019.PL_1","label":"appendix","how":"type"}             phụ lục
```
Báo cáo: `docs/bao_cao_chay/l4/l4_report.txt`. Bước này không có loại dòng "không thành công": mọi Điều đều nhận một nhãn.

**3. Bảng field.**
| Field | Nghĩa | Mọi giá trị có thể có (kho / BLLĐ) | Ai đọc |
|---|---|---|---|
| `id` | mã Điều hoặc phụ lục | | khoá tra |
| `label` | nhãn của Điều | `substantive` Điều có quy tắc: điều kiện, quyền, nghĩa vụ, mức, thời hạn, ngoại lệ, chế tài (754 / 203) · `authority` trách nhiệm, thẩm quyền của cơ quan (59 / 8) · `procedural` hồ sơ, trình tự, thủ tục (48 / 6) · `effect_transition` hiệu lực, chuyển tiếp, bãi bỏ, "Sửa đổi, bổ sung ..." của chính văn bản (29 / 2); số trước 12/11: 742 / 197, 61 / 9, 39 / 7 · `definition` giải thích từ ngữ (3 / 1) · `appendix` phụ lục (28 / 0) | 2.3 chỉ tìm câu chỉ thị trong Điều `effect_transition`; đồ thị tô màu; 1.8 (chưa code) chỉ dịch quy tắc cho Điều `substantive` |
| `how` | ai xếp nhãn | `regex` (khớp tiêu đề, kho 139) · `default` (không khớp, mặc định `substantive`, kho 754) · `type` (phụ lục, kho 28) | báo cáo thống kê |

Mọi Điều vẫn nằm trong KB, vẫn có phiên bản và vẫn là đích sửa đổi được; nhãn chỉ quyết định Điều đó có được dịch thành quy tắc hay không.

**4. Cách làm** (không LLM).
1. Với mỗi Điều, thử bốn mẫu theo thứ tự ưu tiên, regex khớp ĐẦU tiêu đề, không phân biệt hoa thường:
   - `definition`: "Giải thích từ ngữ".
   - `effect_transition`: "Hiệu lực" (trừ khi theo sau là "của <không phải danh từ pháp luật>" hoặc "và thời hạn": "Hiệu lực của hợp đồng lao động" không khớp, "Hiệu lực của Nghị định này" khớp), "Quy định chuyển tiếp", "Điều khoản chuyển tiếp", "Điều khoản thi hành", "Bãi bỏ", "Hết hiệu lực", "Áp dụng pháp luật", và "Sửa đổi, bổ sung" / "Sửa đổi" / "Bổ sung" / "Thay thế" khi theo sau là danh từ đơn vị pháp luật hoặc văn bản (điều, khoản, điểm, mục, chương, phụ lục, danh mục, quy định, nghị định, thông tư, luật, bộ luật, nghị quyết, quyết định, văn bản; có thể kèm "một số", "các", "toàn bộ").
   - `authority`: "Trách nhiệm của (các) Bộ | cơ quan | Ủy ban | Sở | Chính phủ | Thủ tướng | Tổng liên đoàn | UBND | tổ chức có thẩm quyền", "Trách nhiệm thi hành | quản lý nhà nước", "Thẩm quyền" (trừ "Thẩm quyền giao kết", loại riêng), "Nhiệm vụ", "Quyền hạn", "Tổ chức thực hiện", "Cơ quan".
   - `procedural`: "Hồ sơ", "Trình tự", "Thủ tục", "Cách thức", "Tiếp nhận", "Nộp hồ sơ", "Thời hạn giải quyết", "Quy trình".
2. Khớp mẫu đầu tiên thì lấy nhãn đó (`regex`). Ví dụ khớp: "Trách nhiệm của Ủy ban nhân dân cấp tỉnh trong thương lượng tập thể" là `authority`. Không khớp: "Trách nhiệm khi chấm dứt hợp đồng lao động" (chủ thể là các bên, không phải cơ quan nhà nước; ví dụ nêu trong mã nguồn) nên là `substantive`.
3. Không khớp mẫu nào thì `substantive`, `how=default`. Phụ lục thì `appendix`, `how=type`.

**5. Vì sao.**
- Cần bước này: không phải Điều nào cũng chứa quy tắc để dịch (Điều "Giải thích từ ngữ" định nghĩa, Điều "Hiệu lực thi hành" nói về hiệu lực của chính văn bản); nhãn lọc việc cho 1.8 và chỉ cho 2.3 chỗ tìm câu chỉ thị.
- Mặc định `substantive` cho Điều không khớp: thừa (một Điều thủ tục ở lại substantive) chỉ tốn công ở bước trích quy tắc, còn thiếu (đẩy một Điều có điều kiện thật ra khỏi substantive) làm mất quy tắc.
- Bỏ LLM (quyết định A14, 11/11): (1) LLM kiểm LLM không chứng minh được đúng sai, trái nguyên tắc "đầu ra LLM phải kiểm được bằng symbolic"; (2) đo trên 742 Điều không khớp mẫu thì LLM chỉ đổi nhãn 93, không Điều nào thành `effect_transition`; (3) nhãn `definition` do LLM đặt không qua cổng nào; (4) dành hạn mức LLM cho 1.6 đến 1.8.
- Khi gỡ LLM, 39 nhãn `effect_transition` không đổi vì cả 39 vốn do regex đặt, nên bước đọc chỉ thị 2.3 không mất nguồn.
- **[PHÁT HIỆN 1, đã sửa A21 ngày 12/11]** Lập luận "mặc định an toàn" chỉ đúng cho Điều KHÔNG khớp mẫu. Một mẫu khớp NHẦM thì đẩy Điều ra khỏi `substantive`, đúng hướng nguy hiểm: trước 12/11 hai mẫu khớp tiền tố ("Hiệu lực ...", "Sửa đổi, bổ sung ...", "Thẩm quyền ...") đẩy nhầm 6 Điều của BLLĐ (xem mục 6). Bài học: mẫu theo tiền tố tiêu đề cần danh từ đi sau để biết tiêu đề nói về văn bản luật hay về một đối tượng trong luật.

**6. Kiểm và số đo.**
- Kiểm: mỗi Điều và phụ lục đúng một nhãn (921 dòng). Không có đáp án chuẩn để đo độ chính xác của nhãn.
- Trước 12/11, BLLĐ có 23 Điều không phải `substantive`; mình đọc TIÊU ĐỀ (chưa đọc nội dung) của cả 23 và thấy 6 Điều có vẻ bị xếp nhầm, vì là quy tắc về hợp đồng, thỏa ước, nội quy chứ không phải hiệu lực hay thẩm quyền của chính văn bản: `effect_transition` ×5 (`D23` "Hiệu lực của hợp đồng lao động", `D33` "Sửa đổi, bổ sung hợp đồng lao động", `D78` "Hiệu lực và thời hạn của thỏa ước lao động tập thể", `D82` "Sửa đổi, bổ sung thỏa ước lao động tập thể", `D121` "Hiệu lực của nội quy lao động") và `authority` ×1 (`D18` "Thẩm quyền giao kết hợp đồng lao động": ai được ký hợp đồng). Sau sửa (A21), 6 Điều này (và 6 Điều tương ứng của `VBHN_125-2025`) thành `substantive`: BLLĐ còn 17 Điều không phải `substantive`. `D219` và `D220` vẫn là `effect_transition`. Hai Điều `D50`, `D87` ("Thẩm quyền tuyên bố ... vô hiệu") vẫn `authority`, ở ranh giới.
- Cổng khi sửa: thư mục `l6/` giống hệt trước và sau, nên bước đọc chỉ thị 2.3 không mất nguồn (`TT_19 D1`, `ND_70 D1/D2/D3`, `D219`, `D220` và mọi "Hiệu lực thi hành" giữ nhãn). Chưa kiểm được: 6 Điều trên chỉ đọc tiêu đề; mẫu chưa thử trên văn bản ngoài kho.

**7. Kiểm hiểu:** 10 câu mục 1.4 của `docs/kiem_hieu.md` (1.4.1 đến 1.4.10).

---

## THẺ BƯỚC 1.5 `exceptions`: tìm các chỗ luật nêu ngoại lệ ("trừ trường hợp ...", "không áp dụng ...") và nối thành cạnh `exception_of` [giai đoạn 1, sau 1.1 và 1.2]

**1. Nhận vào.** Chữ (`text`) của đơn vị (từ 1.1) và cách giải dẫn chiếu của 1.2 (để biết "Điều 108 của Bộ luật Lao động" là đơn vị nào). Ví dụ BLLĐ: `D3.K1` "... Độ tuổi lao động tối thiểu của người lao động là đủ 15 tuổi, trừ trường hợp quy định tại Mục 1 Chương XI của Bộ luật này." · `D14.K1` "... trừ trường hợp quy định tại khoản 2 Điều này."

**2. Ra.** Hai thư mục: `data/processed/l5_explicit/` (hai quy tắc tường minh) và `data/processed/l5_general/` (kiểu chung "trừ trường hợp"); mỗi thư mục có `*_exceptions_*`, `*_unhandled_*`, `*_pending_*`, thư mục chung thêm `*_conditions_*`. Ví dụ thật:
```
cạnh ngoại lệ chung, rule general_except: nút điều kiện exception_of đơn vị (BLLĐ)
{"s":"BLLD_45-2019.Xc9877375","p":"exception_of","o":"BLLD_45-2019.D3.K1","evidence":"trừ trường hợp quy định tại Mục 1 Chương XI của Bộ luật này.","how":"regex","flags":[],"rule":"general_except"}

cạnh ngoại lệ chung, rule general_except_ref: mệnh đề dẫn chiếu tới đơn vị T thì T exception_of đơn vị (BLLĐ)
{"s":"BLLD_45-2019.D14.K2","p":"exception_of","o":"BLLD_45-2019.D14.K1","evidence":"trừ trường hợp quy định tại khoản 2 Điều này.","how":"regex","flags":[],"rule":"general_except_ref"}

nút điều kiện (l5_general_conditions_*), một nút cho mỗi mệnh đề (câu giống nhau gộp một nút)
{"id":"BLLD_45-2019.Xc9877375","type":"dieu_kien","kind":"cu_the","text":"quy định tại Mục 1 Chương XI của Bộ luật này","units":["BLLD_45-2019.D3.K1"]}
{"id":"BLLD_45-2019.Xbdd95425","type":"dieu_kien","kind":"tuy_nghi","text":"hai bên có thỏa thuận khác","units":["BLLD_45-2019.D28","BLLD_45-2019.D168.K2"]}
{"id":"BLLD_45-2019.X84491d28","type":"dieu_kien","kind":"dan_chieu_mo","text":"pháp luật có quy định khác","units":["BLLD_45-2019.D169.K3","BLLD_45-2019.D169.K4"]}

cạnh tường minh (l5_explicit_exceptions_*): sau sửa A22 (12/11) kho có 0 cạnh của cả hai quy tắc, nên không có dòng thật để minh hoạ.
  Trước 12/11 quy tắc except_list_pattern cho 23 cạnh, tất cả sai (xem PHÁT HIỆN 2), ví dụ:
  {"s":"ND_145-2020.D59.K1.a","p":"exception_of","o":"ND_145-2020.D59.K1","evidence":"Trừ các trường hợp quy định tại Điều 108 của Bộ luật Lao động, các trường hợp khác khi tổ chức làm thêm giờ, ... về các nội dung sau đây:","how":"regex","flags":[],"rule":"except_list_pattern"}
  Dạng quy tắc mong đợi (chỉ có trong test): đơn vị "..., trừ các trường hợp sau đây:" kèm hai khoản con a, b thì ra hai cạnh (a exception_of đơn vị), (b exception_of đơn vị).

chưa xử lý (unhandled): trigger không rơi vào quy tắc nào hoặc mơ hồ
{"unit":"BLLD_45-2019.D61.K4","trigger":"trừ","sentence":"... phải từ đủ 18 tuổi trở lên, trừ lĩnh vực nghệ thuật, thể dục, thể thao.","reason":"ngoài hai quy tắc của L5 tường minh"}

chờ đích (l5_*_pending_*): ngoại lệ trỏ tới văn bản chưa có trong kho
{"source":"ND_28-2020.D10.K2.a","edge":"exception_of","target_number":"10/2012/QH13","target_name":"Bộ luật Lao động","target_units":["D31"],"text":"Điều 31 của Bộ luật Lao động"}
```

**3. Bảng field.**

Cạnh (`*_exceptions_*`):
| Field | Nghĩa | Mọi giá trị có thể có | Ai đọc |
|---|---|---|---|
| `s` | phần ngoại lệ | một đơn vị, hoặc mã nút điều kiện `<doc_id>.X<8 ký tự băm>` khi ngoại lệ là một mệnh đề chứ không phải đơn vị luật | đồ thị; 1.7, 1.8 sau này |
| `p` | loại quan hệ | luôn `exception_of` | |
| `o` | quy tắc bị ngoại trừ | mã đơn vị | đồ thị |
| `evidence` | câu có chữ "trừ" hoặc "không áp dụng", nguyên văn | chuỗi | cổng kiểm chuỗi con; thiếu thì không chứng minh được cạnh |
| `how`, `flags` | như 1.2 | `how` luôn `regex`, `flags` luôn `[]` (kho 337 cạnh sau sửa; 359 trước 12/11) | — |
| `rule` | quy tắc bắt ca này | `not_apply_pattern` (kho 0) · `except_list_pattern` (0; trước 12/11 là 23) · `general_except` (157; trước 156) · `general_except_ref` (180); BLLĐ: 0, 0, 39, 20 | thống kê, biết ca nằm trong quy tắc nào khi cần sửa |

Nút điều kiện (`l5_general_conditions_*`, kho 129 sau sửa A22 (128 trước), BLLĐ 30):
| Field | Nghĩa | Mọi giá trị có thể có |
|---|---|---|
| `id`, `type` | mã nút; loại | `type` luôn `dieu_kien` |
| `kind` | loại mệnh đề | `cu_the` mệnh đề cụ thể (kho 117 / BLLĐ 26) · `tuy_nghi` "(các bên) có thỏa thuận khác" (8 / 3) · `dan_chieu_mo` "pháp luật có quy định khác" (4 / 1) |
| `text` | mệnh đề sau "trừ trường hợp", nguyên văn | chuỗi |
| `units` | các đơn vị có ngoại lệ này | danh sách mã; nhiều đơn vị cùng câu dùng chung một nút (BLLĐ: 24 nút một đơn vị, 4 nút hai, 1 nút ba, 1 nút bốn) |

Chưa xử lý (`*_unhandled_*`): `unit`, `trigger` (`trừ` hoặc `không áp dụng`), `sentence`, `reason`. Kho sau cả hai quy tắc còn 73 (BLLĐ 6; trước 12/11 là 95 và 15): 68 ca "ngoài hai quy tắc ..." (4 "không áp dụng", 64 "trừ <danh từ>" không có chữ "trường hợp") và 5 ca "nhiều hơn một 'trừ trường hợp' trong đơn vị". Chờ đích: kho 6.

**4. Cách làm** (không LLM).
1. Tìm trigger: "trừ", "ngoại trừ", "không áp dụng" (có ranh giới từ) trong Điều, khoản, điểm có chữ; bỏ dòng chỉ thị sửa đổi. Không tính các nghĩa "trừ" không phải ngoại lệ đã thấy trong kho: "khấu trừ", "loại trừ", "giảm trừ" (từ đứng trước) và "trừ đi" (từ đứng sau) (A22).
2. Quy tắc `not_apply_pattern`: đơn vị U có "không áp dụng" và một cụm dẫn chiếu đứng NGAY trước nó (chỉ cách dấu cách). Mỗi đích của cụm là `o`, `s` là U. Ví dụ khớp (câu minh hoạ, không có ca thật trong kho): "Quy định tại Điều 9 không áp dụng đối với doanh nghiệp nhỏ".
3. Quy tắc `except_list_pattern`: text của U kết thúc bằng một cụm "trừ ... sau đây:" liền nhau, tức từ "trừ" (hoặc "ngoại trừ") tới "sau đây:" cuối text không có dấu `, ; .` hay xuống dòng xen giữa (ví dụ khớp: "..., trừ các trường hợp sau đây:"; không khớp: "..., trừ trường hợp kéo dài thời hạn; không thực hiện ... theo một trong các mức sau đây:"). Mỗi đơn vị con trực tiếp C của U là `s`, `o` là U.
4. Kiểu chung: ca còn lại có "trừ trường hợp X". Mệnh đề X là chữ từ "trừ trường hợp" đến hết đoạn, bỏ `. ; : ,` ở cuối (nếu "trừ trường hợp" đứng đầu đoạn thì mệnh đề dừng ở dấu phẩy đầu tiên). Tạo nút điều kiện (mã băm từ mệnh đề đã chuẩn hoá nên câu giống nhau cùng nút) và cạnh `general_except`; nếu X dẫn chiếu tới đơn vị T (dùng cách giải của 1.2) thì thêm cạnh T `exception_of` đơn vị (`general_except_ref`). Phân `kind` bằng regex: `tuy_nghi`, `dan_chieu_mo`, còn lại `cu_the`.
5. Đơn vị có hơn một "trừ trường hợp" thì để `unhandled`, không đoán. Trigger không thuộc quy tắc nào cũng vào `unhandled` kèm lý do.

**5. Vì sao.**
- Cần bước này: ngoại lệ đổi kết luận (BLLĐ `D3.K1`: tuổi lao động tối thiểu là 15, trừ Mục 1 Chương XI). Bỏ sót ngoại lệ thì KB trả lời theo quy tắc chính và bỏ qua trường hợp bị loại, tức kết luận quá rộng.
- Khác 1.3: 1.3 tìm chỗ luật CHƯA nói hết và giao cấp dưới; 1.5 tìm chỗ luật TỰ nêu trường hợp loại ra khỏi một quy tắc.
- Nút điều kiện thay vì nối thẳng: mệnh đề "trừ trường hợp X" nhiều khi không phải một đơn vị luật ("các bên thỏa thuận khác", "pháp luật có quy định khác"), nên cần một nút đại diện. Câu giống nhau dùng chung một nút để "hai bên có thỏa thuận khác" ở nhiều Điều là cùng một điều kiện.
- Không đoán khi có hai "trừ trường hợp": không biết mệnh đề nào áp vào phần nào của đơn vị.

**6. Kiểm và số đo.**
- Kiểm: mỗi chỗ có "trừ" hoặc "không áp dụng" thuộc đúng một trong hai: đã tạo cạnh, hoặc ghi `unhandled`; `evidence` phải là chuỗi con nguyên văn.
- Số đo (sau sửa A22, 12/11): BLLĐ 0 cạnh tường minh và 59 cạnh chung (39 `general_except` + 20 `general_except_ref`) từ 30 nút. Kho 0 + 337 cạnh (trước sửa: 23 + 336). Cạnh `exception_of` ở đồ thị: 278 (trước 300).
- **[PHÁT HIỆN 2a, đã sửa A22]** Trước 12/11, quy tắc `except_list_pattern` sai ở cả 23 trên 23 cạnh của kho (5 đơn vị `o`: `ND_145-2020.D59.K1`, `ND_28-2020.D11.K1` và `D16.K2`, `ND_12-2022.D17.K2`, `ND_283-2026.D23.K2`). Mình đọc đầu và cuối của khoản cha, và khoản con đầu tiên, của cả 5 (chưa đọc hết từng khoản con). Các khoản con là mức phạt ("Từ 1.000.000 đồng đến 2.000.000 đồng với vi phạm từ 01 người đến 10 người lao động") hoặc nội dung phải thỏa thuận ("Thời gian làm thêm"), không phải ngoại lệ. Chữ "trừ" bắt được nằm ở chỗ khác: "khấu trừ tiền lương" (3 đơn vị) hay "trừ trường hợp kéo dài thời hạn hợp đồng ..." giữa câu; kết "sau đây:" chỉ là "theo một trong các mức sau đây:". BLLĐ không bị (0 cạnh), nhưng giai đoạn 2 sẽ dính. Điểm cần chú ý: cổng kiểm chỉ kiểm `evidence` là chuỗi con, không kiểm cạnh có đúng nghĩa. Sửa: quy tắc 2 chỉ áp khi "trừ" và "sau đây:" cuối text là một cụm liền (mục 4, bước 3). Test mới: `test_l5_explicit_rule2_needs_list_tail_not_midsentence_tru`.
- **[PHÁT HIỆN 2b, đã sửa A22]** Trước 12/11, trigger bắt cả "khấu trừ", "trừ đi", "loại trừ", "giảm trừ" (26 trigger toàn kho), nên `unhandled` nhiễu: BLLĐ có 15 ca chưa xử lý, 9 là nhiễu (`D3.K8` ×2 "loại trừ", `D46.K2` và `D47.K2` "trừ đi", `D95.K3`, `D102.K1` K2 K3, `D129.K1` "khấu trừ"). Sau sửa BLLĐ còn đúng 6 ca, đều là ngoại lệ thật chưa được mô hình hoá (mình đọc đoạn quanh trigger, chưa đọc đủ nội dung): `D20.K2.c`, `D24.K3` ("Không áp dụng thử việc đối với ..."), `D61.K4`, `D70.K3`, `D145.K3`, `D188.K1`. Năm ca trong số đó có dạng "trừ <danh từ>" (không có chữ "trường hợp"), nên 1.5 không nhận; chưa bước nào khác (1.7 là ngoại lệ ngầm giữa hai đơn vị) nhận chúng.
- **Tác dụng phụ của sửa A22:** `ND_28-2020.D11.K1` (trước bị quy tắc 2 nuốt) nay vào quy tắc chung: thêm 1 cạnh `general_except`, 1 nút điều kiện dài 724 ký tự (vì mệnh đề chạy "đến hết đoạn" nên gồm cả "; không thực hiện đúng quy định về thời hạn thanh toán ... theo một trong các mức sau đây:") và 1 chờ đích tới BLLĐ 2012. Chưa sửa quy tắc chung; cần bàn.
- **Mở (chưa quyết):** sau cả hai quy tắc, kho còn 64 trigger dạng "trừ <danh từ>" không có chữ "trường hợp" (trừ hành vi 18, trừ hình thức 14, trừ các 12, trừ những 7, ...; BLLĐ 5 ca). Thêm quy tắc cho chúng là nới quy tắc để bắt thêm ca (CLAUDE.md), nên cần user quyết trước khi bàn 1.7/1.8.
- Chưa kiểm được: tỉ lệ bỏ sót (không có đáp án chuẩn); mốc cũ của plan (154→151.1.d, 37→36.1.b) chưa đối chiếu lại ở thẻ này.

**7. Kiểm hiểu:** 10 câu mục 1.5 của `docs/kiem_hieu.md` (1.5.1 đến 1.5.10).

---

## Các phát hiện (gom từ các thẻ trên)

| # | Ở bước | Phát hiện | Trạng thái (12/11) |
|---|---|---|---|
| 1 | 1.4 | Mẫu tiêu đề đẩy nhầm 6 Điều của BLLĐ ra khỏi `substantive` | **Đã sửa (A21).** 12 nhãn đổi (kèm 6 Điều bản sao của VBHN_125); `l6/` giống hệt. Còn: 6 Điều chỉ đọc tiêu đề, chưa kiểm trên văn bản ngoài kho |
| 2 | 1.5 | `except_list_pattern` sai 23/23; trigger bắt "khấu trừ", "trừ đi", "loại trừ", "giảm trừ" | **Đã sửa (A22).** Cạnh tường minh 23 thành 0; BLLĐ chưa xử lý 15 thành 6. Còn MỞ: 64 ca "trừ <danh từ>" ở kho (BLLĐ 5) chưa có quy tắc; nút điều kiện dài của `ND_28-2020.D11.K1` |
| 3 | 1.2 | `target_name` của chờ đích bị cắt (71 trên 129) và `evidence` dính chữ đầu câu sau (7 cạnh) | **Đã sửa (A23).** Số cạnh không đổi; còn 101/129 chờ đích không có số hiệu |
| 4 | chạy | Lần `run_all --llm replay --viewer --tests` đầu ngày 12/11 báo 12/12 nhưng thiếu file `l1_triples_NQ_66-16-2026.jsonl` (17/18 file triples); chạy lại nhiều lần sau đó đều đủ 18; không thấy lệnh xoá hay ghi đè trong `tests/`, `run_all.py` | **MỞ**, không tái hiện. Cổng xanh không kiểm đủ 18 file triples |
