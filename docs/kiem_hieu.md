# Kiểm hiểu bước 1.1 đến 1.6 (10 câu mỗi bước, tổng 60 câu; 1.6 đang bàn, chưa code)

Mục đích: đo người dùng nắm được tới đâu ở từng bước, để tự bảo vệ trong luận (ý của người dùng ngày 11/11).

**Cách dùng.** Người dùng nói "kiểm 1.x". Agent hỏi 10 câu của bước đó trong một lượt. Người dùng trả lời bằng lời của mình, ngắn cũng được; câu nào chưa biết thì ghi "chưa biết". Agent chấm từng câu **đúng / thiếu / sai** theo `docs/kiem_hieu_dap_an.md` (file này dành cho agent; không đưa đáp án trước khi người dùng trả lời), giải thích ngắn chỗ thiếu hoặc sai, ghi kết quả vào bảng bên dưới và tính "mức nắm" của bước. Tài liệu để học: `docs/the_buoc_1_1_den_1_5.md` (thẻ bước 1.1 đến 1.5, mục nào có ví dụ thật, bảng field, số đo); ngoài ra `docs/pipeline_moi.md` (mục "Cách làm", "Ví dụ", "Giải thích field").

**TẠM DỪNG từ 12/11** theo yêu cầu người dùng; kiểm lại sau khi chốt xong 1.6. Agent không hỏi câu nào cho tới khi người dùng bảo.

**Mức nắm** (ghi dưới tên mỗi bước): số câu đúng trên 10. Đề xuất ngưỡng: từ 8 trở lên là đã nắm; dưới 8 thì học lại phần liên quan rồi kiểm lại.

## 1.1 `parse`: biến file chữ thành các đơn vị có mã và có cha
Mức nắm: **1/10 đúng** (kiểm 12/11/2026: 1 đúng, 5 thiếu, 2 sai, 2 chưa biết). Chưa đạt ngưỡng 8; học lại rồi kiểm lại.

| # | Câu hỏi | Kết quả |
|---|---|---|
| 1.1.1 | Ba dòng liên tiếp trong file chữ của BLLĐ: `Điều 14. Hình thức hợp đồng lao động` / `2. Hai bên có thể giao kết hợp đồng lao động bằng lời nói ...` / `a) ...`. Máy gán mã nào cho từng dòng, và cha của hai dòng sau là ai? | **sai** (12/11): viết đảo chữ cái (Điều là `D`, Khoản là `K`: `...D14`, `...D14.K2`, `...D14.K2.a`) và không nêu đúng cha (cha của khoản là Điều, cha của điểm là khoản). Biết có ba cấp lồng nhau |
| 1.1.2 | Mã của một Điều (ví dụ `BLLD_45-2019.D14`) không chứa tên Chương. Vậy quan hệ "Điều 14 thuộc Chương nào" được ghi ở đâu? | **chưa biết** (12/11): ở dòng `parent` của Điều (BLLĐ: `D14` có `parent = BLLD_45-2019.CIII.M1`, tức Mục 1 Chương III) |
| 1.1.3 | Vì sao khối trích dẫn “...” trong một nghị định sửa đổi (có dòng kiểu "Điều 32. ...") không được tạo thành đơn vị của nghị định đó? | **đúng** (12/11): là nội dung văn bản khác, thêm vào sẽ lẫn và vỡ cấu trúc. Bổ sung: khối này được lưu riêng (payload) cho bước đọc chỉ thị 2.3; "không đủ thông tin" không phải lý do chính |
| 1.1.4 | Một dòng không có nhãn (không bắt đầu bằng "Điều", số khoản hay chữ điểm) thì được gắn vào đâu? Có hai trường hợp khác nhau. | **chưa biết** (12/11): gạch đầu dòng nối vào đơn vị sâu nhất đang mở; còn lại nối vào khoản đang mở (chưa có khoản thì vào Điều), kể cả khi một điểm đang mở (có ghi chú). Trả lời "đánh flag" là nhầm |
| 1.1.5 | Dòng "4.960.000 đồng/tháng ..." bắt đầu bằng số và dấu chấm nhưng không phải khoản. Máy phân biệt thế nào? | **sai** (12/11): đoán "thêm một regex". Thực ra cùng regex khoản đòi "số + dấu chấm + khoảng trắng" (`RE_KHOAN`, parse.py:43); trong "4.960.000" sau dấu chấm là chữ số |
| 1.1.6 | Dãy Điều nào hợp lệ: (a) 7, 8, 8a, 9; (b) 7, 9; (c) 7, 8a? Vì sao có kiểm này và nó bắt loại lỗi nào? | **thiếu** (12/11): (a) đúng, (b) đúng và lý do đứt đoạn đúng; (c) sai (8a phải đứng sau 8, hàm `next_number_ok` trả False). Chưa nêu rõ loại lỗi: nhảy cóc hoặc nhận nhầm dòng thành Điều |
| 1.1.7 | Khi parse phát hiện bất thường thì bước làm gì? Vì sao chọn cách đó thay vì đoán rồi đi tiếp? | **thiếu** (12/11): lý do (lỗi lan xuống toàn pipeline) đúng; hành động sai: không "đánh flag rồi đi tiếp" mà dừng hẳn, thoát mã 1, không ghi dữ liệu (`run_doc`, `main` ở parse.py) |
| 1.1.8 | Kết quả của 1.1 là các dòng `(s, p, o)`. Kể các `p` có thể có và nghĩa của từng `p`; nêu một ưu và một nhược của dạng này so với một dòng gộp cho mỗi đơn vị. | **thiếu** (12/11): ưu (khuôn thống nhất, hợp đồ thị tri thức) và nhược (nhiều dòng) đúng; bỏ trống phần kể các `p` (`type`, `number`, `heading`, `parent`, `text`, `source_line`; thêm `scope`, `footnote` ở văn bản có) |
| 1.1.9 | `manifest.csv` là gì, vì sao phải có, và khi nạp một văn bản mới thì phải khai những gì? | **thiếu** (12/11): đúng ý ngày hiệu lực và ngày ban hành quan trọng cho chọn phiên bản; nhưng manifest không có cột "ngày nạp", và thiếu `file`, `nhom`, `so_hieu`, `loai` |
| 1.1.10 | Vì sao 1.1 dùng regex và máy trạng thái chứ không dùng LLM? Nếu cắt sai một Điều thì lỗi lan xuống những bước nào? | **thiếu** (12/11): đúng ý cấu trúc chuẩn nên không cần LLM, nhưng "không thể sai khác" là nói quá (vì vậy mới có kiểm số Điều và dừng khi lỗi); chưa trả lời nửa sau (lan tới 1.2, 1.3, 1.4, 1.5 và mọi bước sau) |

## 1.2 `refs`: tìm các câu dẫn chiếu và nối thành cạnh
Mức nắm: chưa kiểm.

| # | Câu hỏi | Kết quả |
|---|---|---|
| 1.2.1 | Một cụm dẫn chiếu có đúng ba kết cục. Nêu ba kết cục và cho một ví dụ cho mỗi loại. | chưa trả lời |
| 1.2.2 | Vì sao có kết cục "không giải được" thay vì để máy đoán đích? Cho ví dụ một cụm thuộc loại này. | chưa trả lời |
| 1.2.3 | `contains` và `part_of` là gì, lấy từ đâu (từ chữ hay từ cấu trúc), và vì sao có cả hai chiều? | chưa trả lời |
| 1.2.4 | Khoản 3 của một nghị định ghi "khoản 1, 2 và 3 Điều 21 của Bộ luật Lao động". Có bao nhiêu cạnh `refers_to` được tạo và trỏ tới đâu? | chưa trả lời |
| 1.2.5 | "Điều này" và "khoản 2 Điều này" được máy giải thành đơn vị nào? | chưa trả lời |
| 1.2.6 | Vì sao dòng "Sửa đổi, bổ sung khoản 6 Điều 7 như sau:" không tạo cạnh `refers_to`? | chưa trả lời |
| 1.2.7 | "Chờ đích" là gì, khi nào nó thành cạnh thật, và vì sao không tính là lỗi? | chưa trả lời |
| 1.2.8 | Cạnh có `evidence`, `how`, `flags`. Mỗi field để làm gì, và vì sao thiếu `evidence` thì không kiểm tự động được? | chưa trả lời |
| 1.2.9 | Cổng kiểm phần dư (từ khoá điều/khoản/điểm nằm ngoài mọi cụm) là gì, kết quả đo là bao nhiêu, và vì sao con số đó chưa chứng minh được regex bắt hết? | chưa trả lời |
| 1.2.10 | "Tầng 2" (xác định đích duy nhất) định giải quyết loại ca nào? Cho ví dụ, và vì sao nó đang bị hoãn? | chưa trả lời |

## 1.3 `delegation`: tìm các chỗ luật giao cho cấp dưới quy định chi tiết
Mức nắm: chưa kiểm.

| # | Câu hỏi | Kết quả |
|---|---|---|
| 1.3.1 | "Điều khoản giao" là gì, và vì sao KB cần biết chúng? | chưa trả lời |
| 1.3.2 | Xếp mỗi câu vào dạng A, B, D, E hay loose: (a) "Chính phủ quy định chi tiết Điều này." (b) "Thời hạn thực hiện theo quy định của Chính phủ." (c) "Danh mục do Bộ trưởng Bộ Lao động - Thương binh và Xã hội ban hành." (d) "Thủ tướng Chính phủ quyết định ngày nghỉ lễ." (e) "Bộ trưởng Bộ Lao động - Thương binh và Xã hội quy định chi tiết Điều này." | chưa trả lời |
| 1.3.3 | `subpattern: C` là gì? Cho một ví dụ. | chưa trả lời |
| 1.3.4 | Vì sao câu (e) ở trên ra `loose` chứ không phải dạng A, và vì sao không sửa regex A cho khỏi sót? | chưa trả lời |
| 1.3.5 | `flags` có hai giá trị nào, nghĩa là gì, và bước 2.2 dùng loại nào? | chưa trả lời |
| 1.3.6 | Vì sao 1.3 dùng regex mà không dùng LLM? | chưa trả lời |
| 1.3.7 | Điều 154 khoản 9 giao Chính phủ quy định nhưng chưa có nghị định nào lấp. Bị hỏi "người này có cần giấy phép không" thì KB nên trả "có", "không" hay "chưa đủ căn cứ"? Vì sao, và 1.3 góp gì cho việc đó? | chưa trả lời |
| 1.3.8 | Số đo trên BLLĐ: bao nhiêu ca chắc, bao nhiêu ca lỏng, trong ca lỏng bao nhiêu thật? Và điều gì máy chưa kiểm được? | chưa trả lời |
| 1.3.9 | `filled_by` là gì, bước nào tính nó, và vì sao không tính ở 1.3? | chưa trả lời |
| 1.3.10 | Vì sao điều khoản giao không chỉ có ở luật? Cho một ví dụ trong bộ văn bản này. | chưa trả lời |

## 1.4 `article_type`: gắn nhãn cho từng Điều
Mức nắm: chưa kiểm.

| # | Câu hỏi | Kết quả |
|---|---|---|
| 1.4.1 | Bước 1.4 nhận gì và ra gì? Cho một dòng ra làm ví dụ. | chưa trả lời |
| 1.4.2 | Kể 6 nhãn và nghĩa của từng nhãn. | chưa trả lời |
| 1.4.3 | Xếp nhãn cho các tiêu đề: "Giải thích từ ngữ"; "Hiệu lực thi hành"; "Hồ sơ đề nghị cấp giấy phép lao động"; "Hợp đồng lao động vô hiệu"; "Trách nhiệm của Bộ Lao động - Thương binh và Xã hội". | chưa trả lời |
| 1.4.4 | "Trách nhiệm khi chấm dứt hợp đồng lao động" bắt đầu bằng "Trách nhiệm" nhưng là `substantive`. Vì sao? | chưa trả lời |
| 1.4.5 | Vì sao Điều không khớp mẫu nào mặc định là `substantive`? Nếu mặc định là `procedural` thì hỏng gì? | chưa trả lời |
| 1.4.6 | Vì sao 1.4 bỏ LLM? Nêu ít nhất hai lý do. | chưa trả lời |
| 1.4.7 | `how` có ba giá trị nào và nghĩa là gì? | chưa trả lời |
| 1.4.8 | Nhãn được dùng để làm gì ở các bước sau? Nêu ít nhất hai nơi. | chưa trả lời |
| 1.4.9 | Khi gỡ LLM, 93 nhãn đổi nhưng 39 nhãn `effect_transition` không đổi. Vì sao điều này quan trọng với bước đọc chỉ thị? | chưa trả lời |
| 1.4.10 | "Hai LLM đồng ý với nhau" có chứng minh một nhãn đúng không? Vì sao, và nguyên tắc nào của đồ án rút ra từ đó? | chưa trả lời |

## 1.5 `exceptions`: tìm các ngoại lệ ("trừ trường hợp ...", "không áp dụng ...")
Mức nắm: chưa kiểm.

| # | Câu hỏi | Kết quả |
|---|---|---|
| 1.5.1 | Cạnh `exception_of` có `s` và `o`: mỗi cái là gì? Cho ví dụ bằng một câu luật. | chưa trả lời |
| 1.5.2 | Quy tắc `not_apply_pattern`: câu nào kích hoạt nó, và `s`, `o` là gì? (Ví dụ câu "Quy định tại Điều 9 không áp dụng đối với doanh nghiệp nhỏ".) | chưa trả lời |
| 1.5.3 | Quy tắc `except_list_pattern`: câu nào kích hoạt (kết thúc bằng "sau đây:"), và `s`, `o` là gì? | chưa trả lời |
| 1.5.4 | Kiểu chung "..., trừ trường hợp X" tạo ra gì? Vì sao tạo "nút điều kiện" thay vì nối thẳng? | chưa trả lời |
| 1.5.5 | Ba loại nút điều kiện (`kind`) là gì? Cho ví dụ mệnh đề cho mỗi loại. | chưa trả lời |
| 1.5.6 | Các field `how`, `flags`, `rule` của một cạnh ngoại lệ để làm gì? Nêu các giá trị của `rule`. | chưa trả lời |
| 1.5.7 | Vì sao các câu "trừ trường hợp" giống nhau dùng chung một nút? | chưa trả lời |
| 1.5.8 | Một đơn vị có hai chỗ "trừ trường hợp" thì máy làm gì, và vì sao không đoán? | chưa trả lời |
| 1.5.9 | BLLĐ có 0 cạnh tường minh nhưng 66 cạnh chung (59 trước A24, 12/11). Điều đó cho biết gì về cách luật viết ngoại lệ? | chưa trả lời |
| 1.5.10 | Ngoại lệ ở 1.5 khác gì điều khoản giao ở 1.3? Bỏ sót ngoại lệ làm câu trả lời sai theo kiểu nào? | chưa trả lời |

## 1.6 `concepts`: sổ khái niệm (ĐANG BÀN 12/11, chưa code; thẻ ở `docs/pipeline_moi.md`)
Mức nắm: **2/10 đúng** (kiểm 12/11/2026: 2 đúng, 3 thiếu, 3 chưa biết, 2 chưa kiểm vì user mất câu hỏi). Chưa đạt ngưỡng 8; các câu 1.6.5, 1.6.6, 1.6.8 liên quan thẳng tới quyết định 1 (phạm vi ngữ cảnh) nên chưa chốt quyết định đó khi chưa hiểu.

| # | Câu hỏi | Kết quả |
|---|---|---|
| 1.6.1 | Sổ khái niệm (sổ vị từ P) là gì và để làm gì? Nếu hai Điều cùng nói về "giấy phép lao động" mà đặt hai tên vị từ khác nhau thì hỏng gì ở các bước sau? | **đúng** (12/11): nối các Điều qua cùng một tên vị từ; hai tên thì ngoại lệ ngầm (1.7) và trả lời (1.8) không nối được |
| 1.6.2 | Bước 1.6 nhận những đơn vị nào (Điều mang nhãn gì của 1.4)? Nếu 1.4 xếp nhầm một Điều có quy tắc thành `effect_transition` thì 1.6 mất gì? | **đúng** (12/11): `substantive` và `definition`; nhãn sai thì quy tắc không vào 1.6. Câu hỏi thêm của user (vì sao chỉ hai loại) đã trả lời trong chat 12/11: 1.6 nuôi 1.8, mà 1.8 chỉ dịch Điều `substantive`; đây là chọn lọc có giá, không phải 'không đáng' |
| 1.6.3 | Bốn vai của một cụm là gì? Gạch cụm cho câu (BLLĐ D24.K3): "Không áp dụng thử việc đối với người lao động giao kết hợp đồng lao động có thời hạn dưới 01 tháng." | **thiếu** (12/11): kể đúng 4 vai; chủ thể 'người lao động' đúng; điều kiện thiếu nửa đầu ('giao kết hợp đồng lao động' bị đặt nhầm làm kết luận); 'không áp dụng thử việc' là KẾT LUẬN của D24.K3, không phải ngoại lệ (D24.K3 không có cụm 'trừ ...') |
| 1.6.4 | `concept` khác `input` ở đâu? Xếp loại và nói lý do cho: (a) "người lao động là người làm việc cho người sử dụng lao động theo thỏa thuận, được trả lương"; (b) "đủ 18 tuổi trở lên". | **thiếu** (12/11): nửa đầu đúng (`concept`: có đơn vị khác nêu khi nào nó đúng; `input`: người hỏi nêu); chưa xếp loại (a) và (b); câu cuối về 'phủ định' không có trong thiết kế (phân loại theo có hay không có đơn vị nêu khi nào nó đúng). Đáp án: (a) `concept` (Điều 3 khoản 1), (b) `input` |
| 1.6.5 | Cổng "cụm phải nằm nguyên văn trong ngữ cảnh của đơn vị" bắt được lỗi nào và bỏ lọt lỗi nào? Cho một ví dụ mỗi loại. | **chưa biết** (12/11) |
| 1.6.6 | "Ngữ cảnh" của một đơn vị gồm những gì, và vì sao không chỉ lấy chữ của chính đơn vị? Cho ví dụ từ BLLĐ. | **chưa biết** (12/11); user hỏi lại 'ngữ cảnh là gì', đã giải thích trong chat |
| 1.6.7 | Plan gốc dùng thêm một model khác trích lại để kiểm. Vì sao đồ án bỏ cách đó? Nêu hai cổng máy thay thế và mỗi cổng bắt lỗi gì. | **thiếu** (12/11): đúng nguyên tắc (LLM kiểm LLM vẫn là hộp đen, phải có kiểm bằng máy chứng minh được); chưa gọi đúng tên hai cổng (G1 chuỗi con, G4 chéo với 1.5, hoặc G2, G3, G5, G6); 'regex và regex lỏng' là của 1.3, 1.4 |
| 1.6.8 | Đầu ra của 1.5 và 1.2 giúp 1.6 tự kiểm thế nào? Cho ví dụ cụ thể (D14.K2 hoặc D151.K1.d). | **chưa biết** (12/11) |
| 1.6.9 | "Một khái niệm hai tên" là gì, hậu quả ra sao, và vì sao không dùng LLM để gộp tên thì rủi ro này vẫn còn? | **chưa kiểm** (12/11): user mất câu hỏi do terminal bị cắt; hỏi lại ở lượt sau |
| 1.6.10 | Vì sao mức lương tối thiểu vùng hay danh mục nghề không đi qua LLM, và vì sao giai đoạn 1 (chỉ BLLĐ) chưa dùng tới? Khi chạy `--llm off`, bước 1.6 ra được những gì? | **chưa kiểm** (12/11): user mất câu hỏi do terminal bị cắt; hỏi lại ở lượt sau |
