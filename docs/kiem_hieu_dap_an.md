# Ý chính của đáp án kiểm hiểu (DÀNH CHO AGENT CHẤM)

Người dùng chưa trả lời thì **không đọc ra, không gợi ý**. Chấm theo ý chính, không đòi đúng từng chữ: đúng = đủ ý chính; thiếu = có ý đúng nhưng thiếu ý chính; sai = trái với ý chính. Số liệu lấy từ BLLĐ hoặc 18 văn bản, đo ngày 11/11/2026 (nếu đã đổi, kiểm lại trên dữ liệu trước khi chấm). Nguồn: `docs/pipeline_moi.md`, `docs/quyet_dinh/pipeline_moi_quyet_dinh.txt`, code ở `src/`.

## 1.1 `parse`
- **1.1.1** `...D14`, `...D14.K2`, `...D14.K2.a`; mã = mã cha + nhãn. Cha của khoản là Điều 14, cha của điểm là khoản 2 (`D14.K2`). (Cha của Điều 14 là Chương hoặc Mục đang mở.)
- **1.1.2** Ở thuộc tính `parent` của Điều (cha là Mục hoặc Chương). Cạnh cha-con của 1.2 lấy từ `parent`.
- **1.1.3** Khối đó là nội dung của văn bản KHÁC bị sửa và chứa dòng "Điều 32. ...". Nếu thành đơn vị thì Điều của văn bản bị sửa lẫn với Điều của văn bản này. Nó được lưu riêng (payload), gắn với câu dẫn, để bước đọc chỉ thị (2.3) dùng.
- **1.1.4** Bắt đầu bằng gạch đầu dòng thì nối vào đơn vị sâu nhất đang mở. Còn lại nối vào khoản đang mở (chưa có khoản thì vào Điều), kể cả khi một điểm đang mở (có ghi chú).
- **1.1.5** Khoản cần "số + dấu chấm + khoảng trắng" (hoặc ngay trước dấu chú thích). Trong "4.960.000" sau dấu chấm là chữ số, không có khoảng trắng.
- **1.1.6** (a) hợp lệ (8a là Điều chèn sau 8, rồi 9); (b) không (thiếu 8); (c) không (8a phải đứng sau 8). Kiểm này bắt lỗi nhảy cóc hoặc nhận nhầm dòng thành Điều.
- **1.1.7** Dừng, thoát mã lỗi, KHÔNG ghi file (fail-closed). Đoán rồi đi tiếp thì lỗi cắt lan sai xuống mọi bước sau. Cũng dừng khi mã lặp hoặc số Điều khác `manifest`.
- **1.1.8** `type` (chuong, muc, dieu, khoan, diem, pl, pl_muc, pl_row), `number` (số hoặc chữ thứ tự gốc), `heading` (tiêu đề, chỉ Chương/Mục/Điều có), `parent` (mã cha), `text` (chữ), `scope` (chỉ giá trị `out_of_scope`, 15 đơn vị phụ lục), `footnote` (chú thích của bản hợp nhất), `source_line` (dòng trong file gốc). Ưu: cùng khuôn cho thuộc tính và cạnh, dễ nối đồ thị. Nhược: lặp mã ở mỗi dòng nên nhiều dòng hơn.
- **1.1.9** Bảng hồ sơ từng văn bản, nhập tay. Cần: file và nhóm, số hiệu (để văn bản khác dẫn tới), loại (cấp bậc, xử lý riêng bản hợp nhất), ngày hiệu lực (quan trọng nhất; nằm ở Điều cuối với nhiều cách viết nên phải khai), nên có ngày ban hành; số Điều để kiểm là tùy chọn (đề xuất).
- **1.1.10** Cấu trúc luật có quy ước chặt nên regex kiểm chứng được hoàn toàn; LLM không cần và không chứng minh được. Cắt sai lan tới 1.2 (dẫn chiếu), 1.3, 1.4, 1.5 và mọi đơn vị về sau (phiên bản, quy tắc).

## 1.2 `refs`
- **1.2.1** (1) Nối: cạnh `refers_to` tới đích có trong kho, ví dụ "khoản 2 Điều 18" thành `...D18.K2`. (2) Chờ đích: trỏ sang văn bản chưa có trong kho, ví dụ Điều 31 Bộ luật Lao động 2012 từ ND_28. (3) Không giải được: đọc được cụm nhưng không chắc đích, ví dụ "điểm a" trơ trụi ở ND_135 `D5.K1.d`.
- **1.2.2** Đoán sai tạo cạnh sai rồi lan vào suy luận; ghi kèm lý do để người đọc thấy. Ví dụ: khoản/điểm trơ trụi, cụm nhiều đối số ở cấp trên, "điểm này".
- **1.2.3** Từ cấu trúc (thuộc tính `parent` của 1.1), không từ chữ. `contains` là cha tới con, `part_of` là con tới cha; có cả hai chiều để đi từ đầu nào cũng được. `how=parent`, `evidence` rỗng.
- **1.2.4** 3 cạnh tới `D21.K1`, `D21.K2`, `D21.K3` của BLLĐ; mỗi đích một cạnh, `evidence` là cụm nguyên văn.
- **1.2.5** "Điều này" là Điều chứa đơn vị nguồn; "khoản 2 Điều này" là khoản 2 của Điều chứa đơn vị nguồn.
- **1.2.6** Dòng chỉ thị trỏ vào văn bản bị sửa chứ không phải dẫn chiếu của văn bản này; xử lý ở bước đọc chỉ thị (2.3, giai đoạn 2).
- **1.2.7** Cụm trỏ sang văn bản hoặc phụ lục chưa có trong kho. Khi văn bản đích được nạp (giai đoạn 2) thì nối thành cạnh. Không phải lỗi vì thiếu văn bản chứ máy không đọc sai.
- **1.2.8** `evidence` là đoạn nguyên văn làm bằng chứng; máy kiểm nó phải là chuỗi con của chữ đơn vị nguồn; thiếu thì cạnh bịa vẫn lọt. `how` là ai tìm ra (`parent`, `regex`). `flags` là độ tin cậy (`[]` chắc; `isolated` là giữ lại nhưng không dùng làm căn cứ).
- **1.2.9** Bộ dò lỏng: từ khoá điều/khoản/điểm kèm số hoặc chữ mà không nằm trong cụm đã bắt. Đo 0 trên cả 18 văn bản. Chỉ chứng tỏ không còn từ khoá sót; dẫn chiếu không dùng từ khoá ("các quy định nêu trên") thì không thấy được, nên chưa chứng minh regex bắt hết.
- **1.2.10** Ca khoản/điểm trơ trụi (13 ca, đều ở nghị định, thông tư). Ví dụ ND_135 `D5.K1.d` "điểm a ... điểm b khoản này" thành `D5.K1.a` vì chỉ khoản 1 của Điều 5 có điểm a; đích duy nhất là điều máy kiểm được. Hoãn vì BLLĐ có 0 ca và hạn T7.

## 1.3 `delegation`
- **1.3.1** Chỗ luật giao cấp dưới quy định chi tiết. KB cần để biết luật chưa nói hết, trả "chưa đủ căn cứ" thay vì trả lời bừa, và để nối với văn bản hướng dẫn.
- **1.3.2** (a) A; (b) B; (c) D; (d) E; (e) loose.
- **1.3.3** C là dạng A có chữ "do" ngay trước ("do Chính phủ quy định"), ví dụ "Trường hợp khác do Chính phủ quy định." (`D107.K3.đ`); 2 ca.
- **1.3.4** Dạng A chỉ cho các từ toàn chữ cái giữa "Bộ trưởng" và "quy định"; dấu "-" trong "Lao động - Thương binh" chặn. Không nới regex A vì nới bắt nhầm nhiều ca và CLAUDE.md cấm nới quy tắc để bắt thêm ca; tầng lỏng giữ ca với cờ vì bỏ sót nguy hiểm hơn thừa.
- **1.3.5** `[]` là chắc (regex chặt); `["loose"]` là chưa chắc. 2.2 chỉ dùng ca `[]` làm danh mục (ca lỏng chưa dùng; dùng thì prompt LLM đổi và cache `replay` hỏng).
- **1.3.6** Câu giao theo công thức cố định, regex kiểm được hoàn toàn; LLM không chứng minh được đúng sai (nguyên tắc A15).
- **1.3.7** "Chưa đủ căn cứ": luật giao mà chưa có văn bản lấp nên không đủ cơ sở kết luận có hoặc không; trả "không" vì không chứng minh được "có" là sai kiểu "không chứng minh được thì coi là sai". 1.3 ghi chỗ giao để 1.9 biết chỗ còn trống.
- **1.3.8** 51 ca chắc (A 35 gồm 2 ca C, B 10, D 5, E 1), 5 ca lỏng; theo agent đọc 4 thật và 1 nghi (`D133.K1`). Chưa kiểm được: recall (câu giao mà cả hai regex đều không thấy); và trong 51 ca vẫn có thể lẫn ca không phải giao chi tiết (regex thô).
- **1.3.9** Văn bản dưới luật đã nối `details` tới điều khoản đó, theo ngày hiệu lực. Bước 2.2 (`links`) tính, ra `delegation_filled.jsonl`; không tính ở 1.3 vì cần các văn bản khác ngoài BLLĐ.
- **1.3.10** Nghị định cũng giao cho thông tư, ví dụ TT_18 căn cứ ND_145 Điều 68; ở giai đoạn 2 1.3 phải chạy cho mọi văn bản.

## 1.4 `article_type`
- **1.4.1** Nhận tiêu đề từng Điều (và phụ lục); ra một nhãn mỗi Điều, ví dụ `{"id":"BLLD_45-2019.D3","label":"definition","how":"regex"}`.
- **1.4.2** `substantive` (có điều kiện, quyền, nghĩa vụ, mức, thời hạn, ngoại lệ, chế tài); `definition` (giải thích từ ngữ); `effect_transition` (hiệu lực, chuyển tiếp, bãi bỏ, sửa đổi); `procedural` (hồ sơ, trình tự, thủ tục); `authority` (trách nhiệm, thẩm quyền của cơ quan nhà nước); `appendix` (phụ lục).
- **1.4.3** `definition`; `effect_transition`; `procedural`; `substantive` (mặc định); `authority`.
- **1.4.4** Regex chỉ coi "Trách nhiệm" là `authority` khi chủ thể là cơ quan, tổ chức nhà nước; ở đây là nghĩa vụ của các bên trong hợp đồng.
- **1.4.5** Sai theo hướng đẩy một Điều có điều kiện thật ra khỏi `substantive` thì mất quy tắc; để thừa Điều thủ tục ở `substantive` chỉ tốn công ở 1.8 và 1.8 có cổng riêng. Nếu mặc định `procedural` thì nhiều Điều có quy tắc bị bỏ (ở BLLĐ 197 trên 220 Điều không khớp mẫu).
- **1.4.6** (a) LLM kiểm LLM không chứng minh được đúng sai, trái nguyên tắc; (b) đo: trong 742 Điều không khớp mẫu LLM chỉ đổi 93 nhãn và không Điều nào thành `effect_transition`; (c) nhãn `definition` do LLM đặt không qua cổng nào; (d) dành hạn mức model kiểm (20 lượt/ngày) cho 1.6 đến 1.8.
- **1.4.7** `regex` (khớp tiêu đề), `default` (không khớp, mặc định `substantive`), `type` (phụ lục).
- **1.4.8** 2.3 chỉ tìm câu chỉ thị trong Điều `effect_transition`; đồ thị tô màu theo nhãn; 1.8 sau này chỉ dịch quy tắc cho Điều `substantive`.
- **1.4.9** Cả 39 Điều `effect_transition` vốn do regex đặt, nên bước đọc chỉ thị (chỉ tìm trong các Điều này) không mất nguồn khi bỏ LLM.
- **1.4.10** Không: hai LLM có thể sai giống nhau, đồng ý không có nghĩa đúng. Nguyên tắc: LLM chỉ được dùng làm căn cứ khi máy chứng minh được toàn bộ đáp án; còn lại gắn cờ và không dùng làm căn cứ (A15).

## 1.5 `exceptions`
- **1.5.1** `s` là phần ngoại lệ (một đơn vị hoặc nút điều kiện), `o` là quy tắc bị ngoại trừ. Ví dụ "Người lao động phải báo trước, trừ trường hợp quy định tại Điều 154": nút "quy định tại Điều 154" là `exception_of` đơn vị chứa câu.
- **1.5.2** Câu có "không áp dụng" và một cụm dẫn chiếu đứng NGAY trước. `s` là đơn vị chứa câu, `o` là đích của cụm (ví dụ Điều 9).
- **1.5.3** Đơn vị có "trừ" hoặc "ngoại trừ" và kết thúc bằng "sau đây:" rồi liệt kê. `s` là mỗi đơn vị con trực tiếp, `o` là đơn vị chứa.
- **1.5.4** Cắt mệnh đề X sau "trừ trường hợp", tạo một nút điều kiện (mã dạng `X<mã>`) và cạnh `exception_of` từ nút tới đơn vị. Dùng nút vì mệnh đề X không phải một đơn vị riêng của luật. Nếu X dẫn chiếu tới đơn vị T thì T cũng là `exception_of` đơn vị đó (`general_except_ref`).
- **1.5.5** `cu_the` (mệnh đề cụ thể, ví dụ "quy định tại khoản 2 Điều này"); `tuy_nghi` ("các bên có thỏa thuận khác"); `dan_chieu_mo` ("pháp luật có quy định khác").
- **1.5.6** `how` là ai tìm ra (`regex`); `flags` là độ tin cậy; `rule` là quy tắc bắt ca này: `not_apply_pattern`, `except_list_pattern`, `general_except`, `general_except_ref`.
- **1.5.7** Câu giống nhau (khoá chuẩn hoá) gộp một nút để khỏi trùng và biết nhiều đơn vị cùng một ngoại lệ (field `units`).
- **1.5.8** Để vào danh sách chưa xử lý, không tạo cạnh. Không đoán vì không biết mệnh đề nào ngoại trừ phần nào; không nới quy tắc để bắt thêm ca.
- **1.5.9** Luật gốc viết ngoại lệ chủ yếu bằng "trừ trường hợp ..." trong câu; hai kiểu tường minh (không áp dụng sát sau dẫn chiếu, danh sách "sau đây:") hầu như chỉ ở nghị định (4 văn bản có).
- **1.5.10** Ngoại lệ nằm trong chính câu hoặc đơn vị và hạn chế phạm vi quy tắc; điều khoản giao đẩy nội dung cho văn bản khác lấp. Bỏ sót ngoại lệ thì KB áp dụng quy tắc chính cả ở trường hợp được loại trừ, nên kết luận sai (lẽ ra "không" lại ra "có").
