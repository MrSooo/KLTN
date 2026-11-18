# Sổ quyết định

Sổ này ghi các quyết định thiết kế và kỹ thuật đã chốt, kèm lý do và cái giá. Mã quyết định (A1 đến A41) được mã nguồn, test và các tài liệu khác trích dẫn nên giữ nguyên. Một quyết định bị thay thế được ghi "Đã thay thế bởi ...", không xoá.

Quy ước ghi: mỗi mục gồm **Quyết định**, **Lý do** và **Cái giá hoặc chỗ chưa kiểm** khi có. Chỗ lệch so với kế hoạch ban đầu hoặc so với mã cũ được nêu rõ. Số đo ghi kèm ngày đo và phạm vi (BLLĐ là Bộ luật Lao động 45/2019; "kho" là cả 18 văn bản trong `data/raw/labor/`).

Các mục A9, A10, A18, A19, A20, A28 là quy trình làm việc nội bộ giữa các phiên và không còn hiệu lực sau khi tài liệu được chuẩn hoá (A40); mã của chúng được giữ trống để các tham chiếu không đổi.

Bố cục: **Phần I** quyết định về pipeline (A1 đến A41); **Phần II** quyết định ở mức từng bước nền (parse, refs, delegation và links, article_type, exceptions, versions, checks, graph, viewer); **Phần III** số đo và quan sát.

---

# Phần I. Quyết định về pipeline

## A1. Cách đánh số bước
**Quyết định.** Dùng "giai đoạn.bước" (1.1, 1.2, ..., 2.1, ...) thay cho cách đánh số cũ của kế hoạch ban đầu (chữ cái kèm số, từ 0 đến 11). Tên trong mã nguồn đặt theo việc bước làm (`parse`, `refs`, ...).
**Lý do.** Số thứ tự cũ không phản ánh thứ tự phụ thuộc (ví dụ bước 1.4 chạy trước bước đọc chỉ thị) nên khó giải thích từng bước.

## A2. Thứ tự dựng
**Quyết định.** Giai đoạn 1 dựng KB gốc đủ mọi lớp (cấu trúc, quan hệ pháp lý, khái niệm, ngoại lệ ngầm, quy tắc) và hỏi đáp, chỉ trên BLLĐ. Giai đoạn 2 là bộ máy cập nhật, làm sau.
**Lý do.** Khi văn bản dưới luật được nạp, các lớp tri thức đã có sẵn để cập nhật; khớp Thuật toán 1 của `docs/reference/method.md` (bước trích lại tri thức cho tập ảnh hưởng đòi tầng tri thức có trước).

## A3. KB gốc chỉ là BLLĐ
**Quyết định.** KB gốc là BLLĐ bản đầu, không phải BLLĐ cộng văn bản đang hiệu lực tại một ngày. Mô phỏng thực tế: luật ra trước, văn bản hướng dẫn ra sau.

## A4. Bản hợp nhất VBHN_125
**Quyết định.** VBHN_125 là một văn bản nạp thường ở giai đoạn 2. Cách xử lý 8 Điều lệch giữa BLLĐ và VBHN_125 ở khung mới chưa bàn; mã hiện tại xử lý như mô tả ở Phần II, mục Versions (VS4).

## A5. Tìm câu chỉ thị
**Quyết định.** Regex trước; câu không thấy thì LLM đề xuất, đề xuất đi qua cổng máy rồi mới dùng. Mở: có còn dùng nhãn `effect_transition` của bước 1.4 làm nơi tìm chỉ thị hay không (mã hiện tại chỉ tìm trong Điều mang nhãn này).

## A6. Mỗi bước LLM phải có kiểm bằng máy
**Quyết định.** Nguyên tắc: đầu ra của LLM phải kiểm được bằng quy tắc máy (regex, khớp đồ thị, biên dịch). Làm rõ thêm ở A14, A25.

## A7. s(CASP)
**Quyết định.** s(CASP) chạy trên SWI-Prolog làm bộ suy luận (Method 3.5); chỉ cần cho bước 1.8 và 1.9; là ngoại lệ duy nhất của quy ước "chỉ dùng thư viện chuẩn của Python".
**Cách cài đã kiểm (12/11):** SWI-Prolog 10.0.2, pack `scasp` 2.0.1 qua `pack_install(scasp)`. Bước build của pack báo thiếu MinGW/MSYS và `make`: vô hại, vì `library(scasp)` là Prolog thuần và nạp được. **Phải kiểm trên từng máy:** `swipl --version` và nạp được `library(scasp)`.
**Lưu ý khi gọi (A33):** gọi `scasp/2` phải chạy hết các lời giải (`findall` hoặc `forall`). Cắt giữa chừng (`->`, `once`) làm mọi truy vấn sau trong cùng tiến trình báo `determinism_error`, kể cả truy vấn đáng ra thành công.

## A8. Mã và kế hoạch cũ
**Quyết định (ban đầu):** mã và kế hoạch cũ chỉ để tham khảo, dựng lại xong thì lưu trữ. **Kết cục:** mã các bước nền được giữ và đổi tên (A13, A40); kế hoạch cũ được thay bằng `docs/roadmap.md`; thư mục lưu trữ của bản v1 đã xoá (A40).

## A11. Mục tiêu thời gian ban đầu
**Quyết định (ban đầu):** hết 14/11/2026 có KB đủ giai đoạn 1 (1.1 đến 1.9), cơ chế cập nhật và một demo hỏi đáp nhỏ. **Kết cục:** đã trượt; lộ trình hiện hành ở `docs/roadmap.md`.
**Đường găng đã nêu:** s(CASP) cài trên từng máy; hạn mức model kiểm 20 lượt mỗi ngày (xem `docs/llm_config.md`).

## A12. Khuôn cạnh chung
**Quyết định.** Mọi cạnh có khuôn `{s, p, o, evidence, how, flags}`; riêng cạnh ngoại lệ có thêm `rule` (tên quy tắc: `not_apply_pattern`, `except_list_pattern`, `general_except`, `general_except_ref`). Cạnh cha-con: `how=parent`, `evidence` rỗng. Đã bỏ các trường phụ `via` và `check` của cạnh `details` (không bước nào đọc).
**Lý do.** `evidence` cho cổng kiểm "bằng chứng phải là chuỗi con của chữ đơn vị `s`" (nếu thiếu thì cạnh bịa vẫn lọt); `how` để chọn mức kiểm và thống kê; `flags` để phân biệt cạnh chắc với cạnh LLM đề xuất.
**Chưa quyết.** Cờ `isolated` hiện chỉ được ghi bởi bước 2.2 và đọc để báo cáo; chưa nơi nào loại cạnh `isolated` khỏi việc dùng làm căn cứ. Phải định nghĩa lại khi bàn giai đoạn 2.

## A13. Tên module theo vai trò
**Quyết định.** `parse.py`, `refs.py`, `delegation.py`, `article_type.py`, `exceptions_explicit.py`, `exceptions_general.py`; `text_norm` chuyển sang `textutil.py`; phần nối văn bản của `links.py` tách khỏi phần quét điều khoản giao. Tên thư mục đầu ra, tên báo cáo, tên test cũng theo tên module (A40).

## A14. Bước 1.4 không dùng LLM
**Quyết định.** Regex trên tiêu đề xếp nhãn; Điều không khớp mẫu nào mặc định `substantive` (an toàn: không bỏ sót quy tắc).
**Lý do.** (1) LLM kiểm LLM không chứng minh được đúng sai. (2) Đo 11/11 trên BLLĐ: LLM chỉ đổi nhãn 29/197 Điều (20 `definition`, 9 `authority`), 162 vẫn `substantive`. (3) Nhãn `definition` do LLM đặt không qua cổng nào. (4) Dành hạn mức model kiểm cho bước khác.
**Cái giá.** Khoảng 29 Điều có thể mang nhãn khác nay thành `substantive`; bước 1.8 phải xử lý thêm (có cổng biên dịch riêng nên không gây trả lời sai).

## A15. Bước 1.2 ba tầng, không LLM
**Quyết định.** Tầng 1: regex chặt. Tầng 2: luật máy xác định đích duy nhất trong phạm vi Điều/khoản chứa cụm (ví dụ ND_135 `D5.K1.d` "điểm a ... điểm b khoản này" chỉ có thể là `D5.K1.a`). Tầng 3: còn lại ghi "không giải được" kèm lý do, không đoán. Cổng phần dư: xoá các cụm đã bắt khỏi chữ; còn "Điều/khoản/điểm kèm số hoặc chữ" thì báo sót (đo: 0 sót). Tầng 2 chưa làm (xem B10).
**Nguyên tắc rút ra.** LLM chỉ được dùng đầu ra làm căn cứ khi máy chứng minh được toàn bộ đáp án (chọn trong tập đóng và đáp án duy nhất); nếu máy chỉ kiểm được điều kiện cần thì kết quả giữ lại nhưng gắn cờ và không dùng làm căn cứ. **Đã sửa ở A30.**
**Cùng tinh thần cho bước 1.3:** tầng regex lỏng giữ ca chỉ lỏng mới bắt được, gắn cờ `loose`, không dùng LLM.

## A16. Bỏ các trường không ai đọc
**Quyết định.** Bỏ `version` (bước 1.1, luôn bằng 1) và `heading` (bước 1.4, chỉ là bản chép tiêu đề). Giữ `source_line` (truy về dòng nguồn).
**Kiểm.** Đầu ra khác mốc ở đúng 19 file; chạy cả `--llm off` và `replay`.

## A17. Nợ ghi nhận 11/11
Danh sách còn hiệu lực nằm ở `docs/status.md` (mục Nợ kỹ thuật).

## A21. Bước 1.4: siết hai mẫu tiêu đề (12/11)
**Quyết định.** Mẫu cũ khớp tiền tố nên các Điều như "Hiệu lực của hợp đồng lao động", "Sửa đổi, bổ sung hợp đồng lao động", "Thẩm quyền giao kết hợp đồng lao động" bị xếp `effect_transition` hoặc `authority`, mà bước 1.8 chỉ dịch quy tắc cho `substantive`. Mới: (1) "Hiệu lực" không được theo sau bởi "của <không phải danh từ pháp luật>" hay "và thời hạn"; (2) "Sửa đổi, bổ sung | Sửa đổi | Bổ sung | Thay thế" phải kèm danh từ đơn vị pháp luật hoặc văn bản; (3) "Thẩm quyền giao kết" loại khỏi `authority` (chọn tay).
**Kết quả (kho 921 nhãn).** Đúng 12 nhãn đổi (6 Điều của BLLĐ và bản sao của VBHN_125): `effect_transition` 39 thành 29, `authority` 61 thành 59, `substantive` 742 thành 754. BLLĐ còn 17 Điều không phải `substantive` (trước 23). Đầu ra của bước 2.3-2.4 giống hệt trước và sau.
**Chưa kiểm.** Chưa có đáp án chuẩn cho độ chính xác của nhãn; mẫu chưa thử trên văn bản ngoài kho.

## A22. Bước 1.5: siết trigger và quy tắc 2 (12/11)
**Phát hiện.** Quy tắc 2 (`except_list_pattern`) sai ở 23/23 cạnh của kho: trigger "trừ" bắt cả "khấu trừ tiền lương", và quy tắc coi mọi đơn vị có "trừ" và kết bằng "sau đây:" là danh sách ngoại lệ trong khi các khoản con là mức phạt hay nội dung phải thỏa thuận.
**Quyết định.** (1) Trigger không tính "khấu trừ", "loại trừ", "giảm trừ" (từ đứng trước) và "trừ đi" (từ đứng sau). (2) Quy tắc 2 chỉ áp khi từ "trừ" (hoặc "ngoại trừ") tới "sau đây:" cuối text là một cụm liền, không có dấu `,` `;` `.` hay xuống dòng xen giữa.
**Kết quả.** Cạnh tường minh 23 thành 0 (kho); trigger 256 thành 230; BLLĐ chưa xử lý 15 thành 6 (`D20.K2.c`, `D24.K3`, `D61.K4`, `D70.K3`, `D145.K3`, `D188.K1`; cả 6 là ngoại lệ thật chưa mô hình hoá); cạnh `exception_of` ở đồ thị 300 thành 278.

## A23. Bước 1.2: tách tên văn bản đích không số hiệu (12/11)
**Phát hiện.** 71/129 quan hệ chờ đích có tên bị cắt ("Luật Bảo" thay vì "Luật Bảo hiểm xã hội") vì chỉ nhận chữ hoa đầu từ; vòng lặp nhảy qua dấu câu nên 7 ca dính chữ đầu câu sau.
**Quyết định.** Tên gồm các chữ liền nhau, kể cả chữ thường, tối đa 8 chữ, dừng ở dấu câu, chữ số hoặc từ dừng; tên có dấu phẩy chỉ nhận khi nằm trong danh sách viết tay `LAW_NAMES_WITH_COMMA` (hiện có "Luật An toàn, vệ sinh lao động").
**Kết quả.** Số cạnh không đổi (`refers_to` 2.348, chờ đích 129, không giải được 127); chỉ chuỗi tên đổi. **Giới hạn:** danh sách từ dừng viết tay; 101/129 chờ đích vẫn không có số hiệu nên nối theo tên ở giai đoạn 2 cần quy tắc so khớp.

## A24. Mở rộng ngoại lệ chung ở bước 1.5 (thực hiện ở A31)
**Quyết định.** Bắt thêm "trừ <danh từ>" ("trừ hành vi", "trừ hình thức", "trừ các", "trừ những"; kho có 64 trigger, BLLĐ 5) và "không áp dụng". Đây là chỗ cho phép nới quy tắc so với nguyên tắc "không nới để bắt thêm ca", nên phải đo độ chính xác trên mẫu đọc tay (quy tắc 2 từng sai 23/23). Nút điều kiện quá dài (ví dụ `ND_28-2020.D11.K1` 724 ký tự vì mệnh đề chạy "đến hết đoạn") được cắt ở dấu `;` khi phần sau không còn thuộc ngoại lệ.

## A25. Bước 1.6 không dùng LLM thứ hai để kiểm
**Quyết định.** Bỏ cổng "một lượt trích độc lập bằng model khác kiểm lại" (kế hoạch ban đầu và Method 3.5 có). Thay bằng cổng máy (regex, đối chiếu chuỗi, đối chiếu đầu ra của bước 1.2 và 1.5).
**Lý do.** Trái nguyên tắc A6, A14: LLM kiểm LLM không chứng minh được đúng sai.
**Hệ quả.** (1) Mục 3.5 của `docs/reference/method.md` còn mô tả "model khác trích lại để kiểm", cần đổi chữ ở bài. (2) Hạn mức model kiểm không còn chặn bước 1.6. (3) Kiểm "mỗi vị từ đầu vào được ít nhất một quy tắc dùng" chuyển sang bước 1.8. (4) Bước 2.2 vẫn còn lượt model thứ hai.

## A26. Bước 1.6: ngữ cảnh, kiểm dữ kiện thô, gộp tên
**Quyết định.** (1) Ngữ cảnh của cổng chuỗi con = tiêu đề Điều + câu dẫn của khoản cha (với điểm) + chữ chính đơn vị; mỗi cụm gắn nguồn `own`, `chapeau`, `heading`. Lý do: đủ thông tin (ví dụ `D154.K1` có chủ thể và kết luận ở tiêu đề). (2) Bỏ khỏi bước 1.6 phần "kiểm dữ kiện thô" (thuần ngữ nghĩa, không có cổng máy); phần máy làm được (vị từ là kết luận của một quy tắc thì không được là `input`; mỗi `input` phải được ít nhất một quy tắc dùng) chuyển sang bộ quét của bước 1.8. (3) Phương án "LLM đề xuất, máy kiểm điều kiện cần, người duyệt" bị loại vì chuỗi phải tự động.
**Phản biện đã ghi.** Lập luận "tách nhầm thì lộ, gộp nhầm thì im lặng" chỉ đúng với chuỗi suy diễn; với ngoại lệ ngầm, tách nhầm cũng im lặng (thiếu cạnh ngoại lệ thì kết luận mặc định đứng, có thể sai).

## A27. Hướng danh tính vị từ theo chữ (đã thay thế bởi A29)
**Quyết định ban đầu.** Danh tính vị từ = chữ chuẩn hoá của cụm, máy xác định. Phần còn hiệu lực: **tên vị từ bằng tiếng Anh theo nguyên tắc đặt tên** (không băm, không thêm field phụ). Phần quan hệ `same_as` bị bỏ; chỉ còn `narrower_than` (xem A32 (Q2)).
**Cái mất của tên tiếng Anh.** Thêm một loại lượt LLM (đặt tên); máy chỉ kiểm dạng, phủ định, quan hệ 1:1 chứ không kiểm nghĩa của tên; bước 1.8 phải kèm chữ Việt gốc (`surface`) cạnh tên vì tên sai nghĩa có thể đánh lừa việc chọn vị từ.
**Chưa đưa vào.** Phủ định: "Có giấy phép lao động" (D151.K1.d) và "không có giấy phép lao động" (D153.K2, D153.K3) là hai khoá khác nhau theo hướng danh tính theo chữ; cần quan hệ phủ định hoặc tách tiền tố phủ định bằng danh sách đóng (đã giải quyết theo hướng tách `cuc`, A38).

## A29. Bước 1.6: tái dùng vị từ, ba cấp
**Quyết định.** Nguyên tắc: một khái niệm một vị từ; không tạo vị từ mới khi sổ đã có vị từ cùng nghĩa. Cơ chế: **dẫn chiếu** do máy điền từ bước 1.2 (cụm có `targets` thì không đặt tên); **cấp 1** cùng chữ chuẩn hoá thì cùng tên (máy); **cấp 2** khác chữ nghi cùng nghĩa: máy lập danh sách ứng viên giới hạn (cùng Điều, hoặc nối qua bước 1.2 hay 1.5, hoặc chung từ nội dung), LLM trả `reuse: <tên>` hoặc `new: <tên>`, cổng kiểm tên thuộc danh sách và tham số khớp, dòng mang cờ `reuse_llm`; **cấp 3** gần nghĩa: tách riêng, quan hệ `narrower_than` (hoãn, A32).
**Lý do.** Đề cương đồ án nêu rủi ro LLM đặt tên khái niệm thiếu nhất quán khiến các quy tắc không nối được; đóng góp là giới hạn và thống nhất tập vị từ. Danh sách ứng viên phải giới hạn bằng đồ thị và cấu trúc, không đưa cả sổ.
**Cái giá.** Gộp nhầm âm thầm (máy không bắt được); phụ thuộc thứ tự xử lý; thêm lượt LLM.

## A30. Sửa A15: nghĩa vận hành của "cô lập"
**Quyết định.** Lựa chọn của LLM **trong tập đóng** (ví dụ chọn `reuse` trong danh sách ứng viên) được dùng làm căn cứ, nhưng (1) gắn cờ trên dòng, (2) liệt kê trong báo cáo, (3) câu trả lời dựa vào nó phải ghi rõ (thuộc bước 1.9), (4) đo độ chính xác trên mẫu đọc tay. Đầu ra LLM tự do vẫn bị cô lập.
**Lý do.** Theo A15 nguyên văn thì tái dùng vị từ (cốt lõi của đề cương) mặc định bị tắt.
**Cái mất.** Một kết luận có thể dựa trên một lần tái dùng sai mà máy không bắt được; chỉ ước lượng được xác suất sai qua mẫu đọc tay. Bài báo cáo phải nói đảm bảo của tầng tri thức là tập đóng, cổng điều kiện cần, truy vết và độ chính xác đo được, không phải chứng minh.

## A31. Bước 1.6: bản tối thiểu và ba việc làm ngay (12/11)
**Quyết định.** (1) Mô tả bước 1.6 bản tối thiểu là bản cuối; giai đoạn A (gạch cụm) làm trước, giai đoạn B (đặt tên, tái dùng) sau. (2) Bỏ khỏi bản này: bảng quan hệ `narrower_than`, bảng thuật ngữ Việt-Anh, đơn vị định nghĩa, phủ định (đảo ở A38). (3) Làm ngay: mở rộng ngoại lệ chung ở bước 1.5 sang "trừ <danh từ>", "không áp dụng" và đơn vị có nhiều hơn một "trừ trường hợp"; cắt nút điều kiện ở dấu `;`; thêm vào `checks` kiểm "ca chưa xử lý của BLLĐ phải đúng danh sách đã biết".
**Chưa đo.** Độ chính xác của phần mở rộng bước 1.5 ngoài việc đọc hết ca khớp; có thể sai kiểu quy tắc 2 (A22).

## A32. Bước 1.7: ngoại lệ ngầm
**Quyết định.** (Q1) Cạnh `exception_of` do LLM đề xuất (cờ `llm_proposed`) được bước 1.8 dùng làm căn cứ kèm cờ, báo cáo và đo trên mẫu đọc tay (mở rộng A30); công tắc bật tắt quyết ở bước 1.8, 1.9. (Q2) Chưa làm `narrower_than`; ghi nợ, quyết sau một vòng KB đầy đủ. Bằng chứng lấy từ cả ngữ cảnh A26. Không dựng riêng đồ thị khái niệm; tập vị từ được phép tính ở bước 1.8. Cạnh nằm trong vòng thì không dùng, ghi vào `rejected` (đo: 66 cạnh BLLĐ có 0 vòng). Cặp ứng viên theo Method 3.5: hai đơn vị cùng dùng một vị từ loại `concept` (đơn vị neo cũng tính). Đếm số cặp trước khi gọi LLM; vượt ngân sách thì dừng và báo. Phạm vi: cặp trong BLLĐ; ngoại lệ ngầm giữa văn bản thuộc giai đoạn 2.
**Hai dạng ngoại lệ.** Đề cương đồ án phân biệt ngoại lệ tạo kết luận ngược (rebut) với ngoại lệ chỉ loại trừ việc áp dụng (undercut), và dùng sự phân biệt đó để tách "bị bác" khỏi "chưa đủ căn cứ" ở bước hỏi đáp. Phân biệt này vẫn còn; chưa quyết ai gán dạng và ở bước nào (66 cạnh của bước 1.5 chưa có trường mang nó); thuộc bước 1.8.
**Điều kiện chạy.** Cần bước 1.6B xong.

## A33. Bước 1.8: quy tắc s(CASP)
**Quyết định.** (1) [Điểm (1) đã thay thế bởi A41: máy biên dịch, LLM sửa khi lỗi.] Quy tắc do LLM viết, qua cổng (biên dịch được; chỉ dùng vị từ được phép và đúng số tham số; bộ quét; không sinh lỗi mới), được dùng làm căn cứ kèm cờ `llm_rule`, ghi trong báo cáo, trích trong câu trả lời, đo bằng bộ câu hỏi bước 1.9. Cái mất: quy tắc dịch sai nghĩa mà vẫn biên dịch được và sạch bộ quét cho câu trả lời sai mà trông chắc chắn; chỉ bộ câu hỏi có đáp án chuẩn bắt được. (2) s(CASP): xem A7. (3) Bỏ điều kiện "không làm giảm số tình huống mẫu trả lời đúng" của đề cương cho tới khi có bộ câu hỏi bước 1.9; chỉ giữ "biên dịch được, không sinh lỗi mới".
**Còn mở.** (a) Cách đưa 43 cạnh bắt đầu từ nút điều kiện (34 `cu_the`, 7 `tuy_nghi`, 2 `dan_chieu_mo`) vào quy tắc gốc; chỉ 23 cạnh bắt đầu từ đơn vị. (b) Biên dịch ngoại lệ lồng nhau. (c) Nguồn quy tắc kết luận phủ định cho "bị bác". (d) Ai gán hai dạng ngoại lệ. (e) Đề cương ghi vị từ đầu vào do người thực hiện biên soạn; bản cài để máy suy ra `kind`.
**Hoãn sang giai đoạn 2.** Thứ tự ưu tiên theo Điều 58 (giai đoạn 1 mọi quy tắc cùng văn bản nên không phân xử được cặp nào) và các loại quét liên quan phiên bản.

## A34. Vai LLM `trich` (Claude, 12/11)
**Quyết định.** Thêm vai `trich` (Claude, trả phí theo token) cho bước 1.6 trở đi, vì Gemini quá tải (503/429). Đặt ngoài `ROLES` (`EXTRA_ROLES`) để `chinh` và `kiem` giữ Gemini: khoá cache chứa tên model, đổi `chinh` sang Claude làm `--llm replay` của bước 2.2 hụt cache. Khoá `trich.thinking` đặt theo model. Không bật `fallbacks` phía server.
**Kết cục.** Từ A36 phần LLM của bước 1.6 không còn gọi API; mã gọi API giữ lại nhưng không dùng (xem `docs/status.md`, Nợ kỹ thuật).

## A35. Bước 1.6A bản cũ chạy live (13/11) và hai sửa
**Kết quả.** 204/204 lô, 881 đơn vị, 2.552 hàng, chi phí $2,61 với Sonnet (tính từ token trong cache, chưa đối chiếu Console). Cổng nguyên văn: 0 cụm bị loại (kiểm độc lập, đúng thật). Mẫu đọc tay: 74/84 cụm chấp nhận được (88%), một người đọc, không phải đáp án chuẩn.
**Vấn đề.** Mục liệt kê "phải có các nội dung sau" bị gán `ket_luan`; `ket_luan` phủ 843/881 đơn vị nên `kind` khó phân biệt; vai gắn theo đơn vị chứ không theo từng quy tắc; 309/2.512 cụm dài từ 25 từ trở lên.
**Hai sửa (có test).** (1) Khoản đứng dưới Điều có câu dẫn riêng nhận câu dẫn đó làm ngữ cảnh (46 khoản, 10 Điều; 39% không ra chủ thể trước sửa). (2) Ngoại lệ ghi hai lần: cụm `ngoai_le` do LLM chứa hoặc nằm trong chữ nút bước 1.5 của cùng đơn vị thì bỏ (11 đơn vị).
**Đã thay thế.** Kế hoạch chuyển sang Haiku bị huỷ bởi A36.

## A36. Phần LLM của bước 1.6 chạy bằng phiên Claude Code (13 đến 14/11)
**Quyết định.** Không gọi API cho vai `trich`; một phiên Claude Code đóng vai LLM trong **thư mục làm việc ngoài repo** (hộp cát). Mỗi lô giao cho một subagent mới, model đặt tường minh; phiên chính không tự làm lô nào. Máy kiểm và ghi bản ghi cache bằng lệnh nhập (`nhap`): từ chối lô sai hình, lô thiếu nhật ký model, lô mà model tự khai khác cấu hình. Mã gọi API giữ nguyên, không dùng.
**Lý do hộp cát.** Phiên chạy trong repo biết dự án (CLAUDE.md tự nạp) và trả rỗng ở hai lô đầu; một dòng cấm trong file hướng dẫn không cách ly được.
**Cái mất.** Bản ghi không có `request_id` và `usage`; nguồn gốc chỉ dựa trên `produced_by` và lời khai model của phiên; cách ly dựa trên hướng dẫn trong thư mục; số đo không so thẳng được với API; tốn hạn mức gói; luận văn phải ghi model là "phiên Claude Code".
**Kết quả bản cũ (concepts-2, Opus 5.5, 204/204 lô, 14/11).** 3.069 cụm LLM, 0 cụm hỏng cổng, 868/881 đơn vị có cụm. Lời nhắc `concepts-3` thử trên 21 lô rồi rút (làm model lặp `ket_luan` của câu dẫn vào cả 8 khoản `D67`); theo tiêu chí đăng ký trước, lùi về `concepts-2`. Phần sót: 13/881 đơn vị rỗng; 11/87 lô ngoài mốc 0,7-1,6 lần mốc so sánh. Mọi thống kê theo nguồn cụm (`own`/`chapeau`/`heading`) là cận dưới vì nhãn là "khớp đầu tiên".
**Bài học thủ tục.** Tiêu chí nghiệm thu phải đăng ký trước khi thấy đầu ra; sửa lời nhắc quá một lần là nới tiêu chí theo kết quả.

## A37. Bước 1.6B bản cũ: đặt tên và tái dùng vị từ (đã thay thế một phần bởi A38, A39)
**Quyết định (còn hiệu lực làm khung cho bản viết lại).** Làm đủ toàn bộ bảng, không cắt lát; phần LLM chạy bằng phiên Claude Code (A36), Sonnet 5.5, effort `high`. Đặt tên tuần tự theo thứ tự Điều, mỗi lượt thấy tên của các lượt trước. Mỗi chữ kèm ngữ cảnh và tối đa 12 ứng viên (lấy từ chữ đã có tên: cùng Điều, nối qua bước 1.2 hoặc 1.5 theo cây con, chung từ nội dung). LLM trả `reuse` (chỉ khi cùng nghĩa) hoặc `new` (tên tiếng Anh đúng dạng, không tiền tố phủ định). Cổng: mỗi chữ đúng một mục; tên `reuse` nằm trong tập đã đưa; tên `new` đúng dạng và chưa có. Dựng sổ vị từ có `kind` (`concept` nếu có đơn vị dùng làm kết luận; còn lại `input`).
**Cơ chế hộp cát.** Thư mục làm việc ngoài repo do `--xuat` dựng; lệnh `tiep.py` dựng lại trạng thái bằng cách gấp các `out/` (không lưu file trạng thái thứ hai); mỗi `lo/NNN.json` phải trùng từng byte với lượt dựng lại; `system.txt` và `schema.json` phải trùng bản trong repo; đầu ra sai hình thì giao lại đúng lượt đó một lần, sai hai lần thì dừng; model hoặc effort tự khai sai thì dừng; `--nhap` ghi cache, bản ghi đã có mà cùng đầu ra thì bỏ qua, khác đầu ra thì dừng trừ khi `--de`. `run_all --llm live` chạy bước này ở chế độ replay và in thông báo.
**Kết quả chạy 15/11 (76 lượt, Sonnet 5.5 effort high).** 76/76 lượt qua cổng; 1.877 lần hỏi; 44 lỗi cổng lần đầu (phần lớn tên dài quá 50 ký tự), đều qua ở lần hỏi lại; 0 chữ bị loại; **tái dùng chỉ 55/1.833 chữ (3%)**, ra 1.778 vị từ. Xích quy tắc gần như không có (chỉ 11/704 vị từ điều kiện hay ngoại lệ trùng một vị từ kết luận ở Điều khác); chỉ 108 cặp ứng viên cho bước 1.7.
**Kết cục.** Kết quả bị coi là hỏng theo kết quả của bước 1.6A cũ (A37 (18), A38). Số đo lỗi và nguyên nhân: `docs/design/steps_1_6_to_1_8.md`, mục 3. Cache 76 lượt ở `data/llm_cache/concepts_names/` chưa xoá.

## A38. Bước 1.6A làm lại: dòng ra là mệnh đề (15/11)
**Quyết định (Q0 đến Q5).**
- (Q0) Dòng ra là **mệnh đề** (0, 1 hay nhiều mệnh đề mỗi đơn vị), không còn là cụm; chủ thể là đối số, bỏ vai `chu_the`; cho phép loại `?` khi chưa xác định.
- (Q1) Danh sách dưới cùng một vị ngữ giữ chung nếu tạo thành một đối tượng hoặc nhóm thống nhất; từng mục có ý nghĩa độc lập thì tách. **Tách** khi từng thành phần kiểm được đúng/sai độc lập và vi phạm từng thành phần có ý nghĩa pháp lý riêng; **giữ chung** khi tạo thành yêu cầu tập thể; không tách tự động theo danh từ. Mỗi quyết định tách hoặc giữ chung ở ca khó có lý do. Bổ ngữ đứng cuối không mặc định bỏ: phải xác định phạm vi, mơ hồ thì `chua_ro` ngay ở bổ ngữ.
- (Q2) Mọi thành phần của `menh_de` phải truy được từ chính các mẩu `trich` của dòng đó (cổng âm tiết); chữ kế thừa từ câu dẫn cũng phải có mẩu `trich` tương ứng.
- (Q3) Phương thức và cực là trường riêng; thêm giá trị `khong_ap_dung` cho `phuong_thuc` (đảo A31). Bước 1.6 chỉ bảo toàn nghĩa; cách dịch thành chặn quy tắc thuộc bước 1.8. Cái mất: thêm giá trị là thêm chỗ LLM nhầm.
- (Q4) `cac_muc_con` (`va`, `hoac`, `danh_sach`); câu dẫn có danh sách là tân ngữ thì `bo_qua`, danh sách là điều kiện thì mang `ket_luan` một lần; `nhom_hoac`; `chua_ro` kèm câu hỏi; `bo_qua` với lý do `dan_chieu_mo`, `khong_quy_pham`. Dòng bị loại khỏi trích vị từ vẫn giữ làm dữ liệu truy vết.
- (Q5) Đáp án thí điểm 30 đơn vị: do con người xác nhận mới là đáp án chuẩn; đáp án nháp hiện có do LLM soạn nên chưa phải đáp án chuẩn.
- (Q2b, Q3b) Trường `bo_ngu` (`this_clause`, `group`, `unknown`); `nguyen_nhan` gắn với từng chỗ `chua_ro`; lý do có ở cả đầu ra LLM (`ly_do_llm`) và đáp án (`ly_do_dap_an`), chỉ cho ca khó.
**Bổ sung sau đáp án nháp (K1 đến K10).** `quy_tac` gom điều kiện và kết luận của một quy tắc; "hoặc" lồng "và" thì tách thành nhiều quy tắc; `chu_the.loai` có thể là danh sách; `gan_vao` cho `con_tro` không phải ngoại lệ; định nghĩa "X là Y": Y là `dieu_kien` và thêm `ket_luan` "là X"; bước 1.6B đặt tên theo `menh_de`, không tính `bo_ngu` (bước 1.8 phải dùng `bo_ngu` như một điều kiện); thêm mã lý do `ke_thua` và `dan_chieu_ngoai`; `con_tro` không giải được đích được phép `targets` rỗng kèm `chua_ro`; cách đo: chạy 1.6A mới trên đúng 30 đơn vị rồi so với đáp án nháp.
**Phát triển lời nhắc.** `menh-de-1` thử 16 lô (Sonnet, `xhigh`): 0 lỗi cổng / 100 dòng, nhưng có 5 lỗi lặp lại do lời nhắc (con_tro không có vai; dẫn chiếu bị đặt vào bổ ngữ; bổ ngữ ăn mất chính hành vi; câu nêu giá trị bị áp luật định nghĩa ngược; nội dung bị xếp danh sách). `menh-de-2` sửa bằng luật chung. Đo trên 34 lô `menh-de-2` (359 mệnh đề): trung vị 9 âm tiết, 22% từ 15 âm tiết trở lên, chỉ 9/318 mệnh đề lặp nguyên văn ở từ 2 Điều; cụm dài nhất là danh sách danh từ nằm trong mệnh đề nên không tái dùng được. `menh-de-3` thêm trường `liet_ke` (danh sách từ 3 mục), hạ cờ dài từ 25 xuống 15 âm tiết, ghi `duoc` + `phu_dinh` cho "không phải X", rút lời nhắc từ 11,8 KB xuống 8,9 KB, cho LLM bỏ trường rỗng (máy điền mặc định), gom lô vào khối tối đa 20 lô một subagent.
**So sánh trên 16 lô thí điểm (`menh-de-3`).** Gemini 3.5 flash-lite: 26 lỗi cổng / 79 dòng (bịa đích dẫn chiếu và chủ thể). Gemini 3.8 flash: 17 lỗi cổng / 79 dòng (11 lỗi là thiếu mẩu câu dẫn trong `trich`), 160-310 giây mỗi lượt, hạn mức 20 lượt mỗi ngày. Sonnet qua Claude Code (`menh-de-1`): 0 lỗi / 100 dòng nhưng tốn token.
**Phát hiện ở bước 1.1.** Đoạn không có ký hiệu điểm nằm giữa hai điểm bị gắn vào khoản cha thay vì điểm đứng trước (chắc chắn: `D36.K1`; đếm thô 24 khoản có đoạn sau câu dẫn, trong đó BLLĐ 2). Chưa phân loại ca nào đúng là đuôi của khoản. Chưa sửa.
**Phát hiện ở bước 1.2.** Dẫn chiếu tới Chương hoặc Mục không được nhận dạng (BLLĐ 1 ca, `D3.K1`). Khoảng 4 cụm sót thật (`D131` "Điều này", `D34.K4` "khoản 5 Điều 328" của luật khác).

## A39. Chốt tuning bước 1.6A và 1.6B lần cuối (15/11)
**1.6A: đường chạy 204 lô.** Sonnet 5.5 qua phiên Claude Code, effort `high`, khối tối đa 20 lô mỗi subagent, song song tối đa 4, chạy tiếp thư mục làm việc `bo_menh_de_v3` (mới 9/204 lô khi chốt). Không dùng Gemini cho 204 lô (tỉ lệ lỗi cổng cao hơn trên mẫu thử, hạn mức 20 lượt mỗi ngày). Không vá lỗi thiếu mẩu câu dẫn của Gemini bằng cách máy tự thêm vào `trich`, vì làm vậy mất cổng (c) của A38 (Q2).
**1.6A: lời nhắc đóng băng.** `menh-de-3` không sửa chữ nào nữa (chữ lời nhắc nằm trong khoá cache). `LONG_SYL` = 15 là cờ, không chặn.
**1.6A: luật dừng viết trước.** Sau 3 khối đầu (60 lô) dừng và báo nếu (i) có câu dẫn lọt thành `menh_de`, hoặc (ii) lỗi cổng còn lại sau khi hỏi lại vượt 5% số dòng (ngưỡng 5% là con số đặt thủ công, chưa có dữ liệu). Không tự sửa lời nhắc khi dừng.
**1.6A: số nghiệm thu sau khi chạy hết.** Cặp ứng viên cho bước 1.7 (bản cũ 108); tái dùng ở 1.6B (bản cũ 3%); mệnh đề lặp nguyên văn ở từ 2 Điều (bản cũ 9/318, đo trên 34 lô `menh-de-2`). Cả ba không hơn bản cũ thì coi là không cải thiện: dừng và báo, không tự thử lại. Ba số này đo độ kết nối, không đo nghĩa đúng hay sai.
**1.6B: viết lại để đọc mệnh đề.** `names-1` (đọc cụm) hết dùng; sẽ có `names-2`, phải được duyệt trước khi chạy. Phần máy:
- gộp cấp 1 (máy ép cùng tên, không hỏi LLM): cùng `menh_de` chuẩn hoá **và** cùng chữ ký `doi_so`; cùng chữ khác `doi_so` thì hỏi LLM;
- lọc ứng viên theo tham số: **lỏng**, cùng **số** tham số, loại `?` khớp mọi loại (bản cũ lọc cứng theo `params` nên loại oan 36% cụm thiếu `params`);
- `CANDIDATE_CAP` 12 lên 20 (phỏng đoán: mệnh đề ngắn hơn nên 12 dễ cắt mất ứng viên đúng; chưa đo);
- giữ nguyên `ROUND_SIZE` 30, `EXAMPLES_PER_NAME` 3, `CONTEXTS_PER_WORD` 2, `STOP_SYLLABLES` 30 (không có số đo để đổi);
- luật `reuse` giữ chặt (gộp nhầm nặng hơn tách sót, A37) nhưng `names-2` nêu rõ "cùng sự kiện pháp lý, khác cách viết thì `reuse`";
- model và cách chạy giữ: Sonnet 5.5, effort `high`, tuần tự;
- mẫu đọc tay: người thực hiện chỉ xem số tổng và kiểm 20 dòng lấy mẫu; phần đọc 150 quyết định `reuse` và 50 quyết định `new` do bên đọc thay thế thực hiện. Cái mất: độ tin của tỉ lệ đúng/sai thấp hơn so với một người đọc, và bên đọc cùng họ model với bên đặt tên nên chỗ cả hai cùng sai không lộ.
**Cái mất chung của "chốt lần cuối".** `menh-de-3` trên Sonnet chưa có số so đáp án đầy đủ (số 0 lỗi cổng là của `menh-de-1`), nên đóng băng là một lựa chọn có rủi ro; nếu lộ lỗi lời nhắc giữa chừng thì phải chạy lại cả 204 lô. `CANDIDATE_CAP` 20 và ngưỡng 5% là số đặt thủ công.
**Chưa làm.** Nối `propositions.py` vào `run_all`; sửa `concepts_names.py` đọc mệnh đề; xoá các thư mục làm việc cũ và cache hỏng; chạy 204 lô.

## A40. Chuẩn hoá cây dự án để bàn giao (15/11)
**Quyết định.**
- Xoá thư mục lưu trữ của bản v1 (215 file); v1 còn trong lịch sử git (commit `25c65e6` ở đường dẫn gốc).
- Bỏ mọi tên L-số: tên module (`versions.py`, `directives.py`, `directives_rare.py`), thư mục đầu ra `data/processed/<module>/`, báo cáo `docs/run_reports/<module>/`, test `tests/test_<module>.py`, nhãn bước trong `run_all`, nhãn `source` của cạnh trong đồ thị (`refs`, `links`, `versions`, `exceptions_explicit`, `exceptions_general`), tên tác vụ cache bước 2.2 (`links_details`, phiên bản lời nhắc `links-1`). Bí danh import là tên module đầy đủ; các biến cục bộ trùng tên module đã đổi (`refs` thành `citations`/`mentions`, `versions` thành `rows`, ...).
- Tên file tiếng Việt còn lại đổi sang tiếng Anh: `utils/chuan_hoa_van_ban.py` thành `utils/normalize_text.py`; đầu ra của trang xem thành `data/processed/viewer/graph_viewer.html`; dữ liệu thí điểm 1.6A thành `data/pilot_propositions/` (`gold_draft.json`, `llm_output.json`, `comparison.md`, ...). Tên file do thư mục làm việc ngoài repo sinh ra (`nhat_ky.tsv`, `cau_hinh.json`) giữ nguyên vì các thư mục đang dở dùng chúng.
- Quy ước đặt tên file: chữ thường, ASCII, `snake_case`, tiếng Anh cho tên file và thư mục; nội dung tài liệu bằng tiếng Việt; tên trường dữ liệu giữ nguyên (xem `CONTRIBUTING.md`).
- Bộ tài liệu tổ chức lại: `README.md`, `CONTRIBUTING.md`, `docs/` (`overview`, `roadmap`, `status`, `decisions`, `design/`, `operations/`, `reference/`, `llm_config.md`). Xoá các tài liệu quy trình cá nhân (bộ kiểm hiểu, bàn giao giữa các phiên, tiến độ cũ), kế hoạch cũ và báo cáo cũ; kiến thức còn dùng được chuyển vào các file trên.
- Dữ liệu thí điểm 1.6A chuyển sang `data/pilot_propositions/` với tên file tiếng Anh. Thư mục làm việc ngoài repo (hộp cát) không đưa vào repo: có thể dựng lại bằng `python -I src/propositions.py xuat`.
**Kiểm chứng.** Trước và sau đổi tên: `run_all --llm off` và `--llm replay` đều 14/14 bước, 10 bộ test; mọi file dữ liệu `.jsonl` giống hệt, chỉ khác ở nhãn chữ do đổi tên (nhãn `source` trong `graph_edges.jsonl` và các chuỗi lý do chứa tên bước cũ); băm của mọi chuỗi lời nhắc và lược đồ không đổi nên các thư mục làm việc đang dở vẫn nhập được; cache bước 2.2 di chuyển 8 bản ghi, khoá tính lại đã đối chiếu từng bản ghi.

## A41. Hoàn thiện pipeline tới 2.7 trên một tập con khó trước, chạy cả kho sau (18/11)
**Chỗ agent tự thêm, ngoài lời chủ đề tài (đặt lên đầu theo quy ước).** Chủ đề tài duyệt "cụm lao động nước ngoài + NQ 66.16"; phạm vi cụ thể dưới đây do agent chọn:
- [THÊM] VBHN_125, cắt đúng các Điều như BLLĐ. Vì sao: Luật 71/2025 (qua VBHN_125) thêm Đ154.K8a từ 01/01/2026, là lần cập nhật cấp luật của chính Điều trung tâm cụm. Cái giá: thêm 16 Điều; so bản hợp nhất chạy trên kho cắt.
- [THÊM] BLLĐ Đ220 và NĐ 145 Đ114-115 (hiệu lực, trách nhiệm thi hành). Vì sao: giữ câu hiệu lực mà bước 2.3 đọc. Cái giá: Đ220 nhắc BLLĐ 2012 (ngoài kho) nên có quan hệ chờ đích.
- [THÊM] NĐ 145 Đ1-2. Vì sao: bước 2.2 lấy `details` từ Điều 1. Cái giá: Đ1 kê khoảng 20 Điều BLLĐ ngoài tập con nên các cạnh đó treo.
- [ĐÃ BÁO TRƯỚC, agent tự tra] Cụm NQ 66.16 gồm BLLĐ Đ52-58 (cho thuê lại lao động) và NĐ 145 Chương IV (Đ12-36); NQ 66.16 Phụ lục I.7 thay NĐ 145 Đ24-28 có thời hạn.

**Bối cảnh.** Chủ đề tài chốt 18/11: làm xong 1.6A đến 2.7 trên một tập con có cập nhật và ngoại lệ dài, rồi mới nối API LLM và chạy lại toàn bộ KB Luật Lao động. Chế độ làm việc: làm liền mạch, advisor soát sau mỗi bước, các chốt duyệt của roadmap (M1, M2, M4/A33, số bước lan truyền 2.5) do agent quyết kèm advisor và ghi ở sổ này. Phần LLM trên tập con chạy bằng phiên Claude Code riêng không tương tác (`claude -p --model sonnet --effort high` trong thư mục làm việc ngoài repo), không gọi API.
**Quyết định.**
- Tập con `lldnn` khai ở `data/subsets/lldnn.json`: BLLĐ Đ52-58, Đ150-157, Đ220; NĐ 145 Đ1-2, Đ12-36, Đ114-115; VBHN_125 như BLLĐ; NĐ 152/2020, NĐ 70/2023, NĐ 219/2025, NQ 66.16 cả văn bản.
- Cơ chế: biến môi trường `KLTN_TAP_CON=<tên>` làm `corpus.py` trỏ mọi đường dẫn sang kho con (`data/processed_subset/<tên>/raw|processed`, báo cáo `docs/run_reports_subset/<tên>/`). `run_all --tap-con <tên>` dựng kho con bằng `utils/subset/build_subset.py` rồi chạy chuỗi. Kho con cắt file nguồn tại dòng Chương/Mục/Điều bằng regex của 1.1, giữ phần đầu văn bản.
- `llm_cache`: không đổi đường dẫn theo kho con. Bước 2.2 dùng chung được vì khoá tính theo nội dung. **Chưa xử lý:** bước 1.6A nhập vào một file cho cả BLLĐ (`data/llm_cache/propositions/BLLD_45-2019.json`), nhập kết quả tập con sẽ đè kết quả kho đầy đủ; phải tách file trước lần nhập đầu tiên (bước 1.6A). 1.6B kiểm tương tự khi viết lại.
- Cổng 1.1 "Điều liên tục" chỉ nhận đúng các bước nhảy ở chỗ cắt đã khai (`corpus.subset_jumps`). Mốc cố định của kho đầy đủ (1.3, 2.2, 2.3-2.4, checks) bọc bằng `corpus.landmark`: ở kho con, mốc cần đơn vị ngoài kho con in "bỏ qua (ngoài kho con)" và không tính là trượt; EXPECTED của BLLĐ không áp. Kho đầy đủ giữ nguyên hành vi.
- `--tap-con` không đi với `--tests` (bộ test viết cho kho đầy đủ).
**Kiểm chứng (18/11).**
- Kho con: `run_all --tap-con lldnn` 12/12 bước, checks 0 lỗi, unknown_directive 0.
- So với lần dựng kho đầy đủ (đầu ra trong stash `processed` của 18/11): (1) mọi phiên bản thuộc Điều hay văn bản được giữ (1.261) đều có trong kho con; (2) 1.273 phiên bản của kho con trùng các trường ngày hiệu lực, trạng thái, cờ, chữ, `closed_by`, `type`, `number`; (3) khác đã biết: NĐ 145 có hai "Chương XI" (lỗi nguồn, mã lần sau là `CXI_2`); kho con cắt mất Chương XI thứ nhất nên Chương còn lại mang mã `CXI`, `heading` của mã `CXI` và `parent` của Đ114, Đ115 khác kho đầy đủ. Mã các Điều không đổi.
- Kho đầy đủ sau khi sửa: `run_all --llm replay --viewer --tests` 14/14 bước, 10 bộ test; báo cáo chữ không đổi nội dung (chỉ khác ký tự xuống dòng).
**Lỗi tập con làm lộ ra (đã sửa, 18/11).** Bước 2.3-2.4, loại 10 (hết hiệu lực theo chủ đề): NĐ 219 Đ35.K2 làm hết hiệu lực phần lao động nước ngoài của NĐ 152, nhưng 5 đơn vị do NĐ 70 chèn năm 2023 (`D4.K1.c`, `D6.K3`, `D7.K14.a`, `D7.K14.b`, `D9.K9.c`) vẫn còn hiệu lực dưới cha đã đóng. Nguyên nhân: `topic_expire` lấy đơn vị con từ cây parse tĩnh, không từ cây của kho phiên bản. Sửa: lấy con bằng `store.descendants`. Lỗi có cả trên kho đầy đủ; sau sửa NĐ 219 đóng 135 đơn vị (trước 130), tổng phiên bản 9.347 (trước 9.343). Thêm kiểm bất biến vào `checks.py`: không phiên bản cuối nào còn hiệu lực khi cha đã đóng (chạy kiểm trên mã cũ: bắt đúng 5 đơn vị trên).
**1.6A trên tập con (18/11).** Phiên `claude -p --model sonnet --effort high` (dòng lệnh lưu ở `lenh_chay.txt` của thư mục làm việc), 15 lô, 76 đơn vị, 153 dòng (128 `menh_de`, 22 `bo_qua`, 3 `con_tro`); không có câu dẫn lọt thành `menh_de`; 31/128 mệnh đề mang cờ dài (từ 15 âm tiết). Nhập vào file riêng `data/llm_cache/propositions/BLLD_45-2019.lldnn.json` (`propositions.full_cache_path`); hộp cát ghi `tap_con` và `nhap` từ chối nếu khác kho đang chạy.
- **[THÊM, chủ đề tài duyệt 18/11, nới cổng]** Bí danh khoá `bo_ngu`: lần nhập đầu có 6/153 dòng trượt cổng, cả 6 là mục `bo_ngu` dùng khoá `{chu, pham_vi}` thay vì `{original_text, scope}` (6/6 mục `bo_ngu` đều sai cùng kiểu). Nguyên nhân: lời nhắc `menh-de-3` không ghi tên khoá của `bo_ngu` (đường Gemini có lược đồ ép khoá, đường phiên Claude Code không có). Sửa: `propositions.normalize` đổi tên hai khoá trước cổng; giá trị vẫn qua cổng nguyên văn và tập `scope`; khoá lạ khác vẫn trượt. Sau sửa 0 lỗi cổng (gồm D151.K1.d, mắt xích của Q01-Q08). Cái mất: cổng nhận thêm một cách viết tên khoá. Không chọn hỏi lại (lời nhắc vẫn thiếu tên khoá nên nhiều khả năng sai y cũ) hay mở băng lời nhắc (phá A39). **Nợ:** thêm tên khoá `bo_ngu` vào chữ lời nhắc ở lần chạy cả kho bằng API (model mới đằng nào cũng đổi khoá cache).
- Ghi chú cho 1.8: D154.K7, D154.K9 chỉ ra `bo_qua dan_chieu_mo` (không có kết luận); các mục D154 mang `khong_ap_dung` + "thuộc diện cấp giấy phép lao động".
**1.6B `names-2` (18/11).** Module mới `src/predicates.py` (dùng lại phần thuần của `concepts_names.py`; `names-1` giữ nguyên trong `run_all`). Chốt M2 do **agent và advisor** duyệt (chủ đề tài giao), không phải chủ đề tài. Các cách hiểu agent tự chọn:
- [THÊM] Chữ ký tham số gồm CHỦ THỂ rồi các `doi_so`, có thứ tự (A39 ghi "chữ ký `doi_so`"; đọc qua A38 nguyên tắc 3: chủ thể là tham số). Chủ thể chung (danh sách loại) thành một vị trí `?`.
- [THÊM] Phương thức và cực không vào tên vị từ (1.6A đã bỏ khỏi `menh_de`; chúng đi theo dòng sang 1.8). Lời nhắc `names-2` cấm `must_`, `may_`...
- Lọc ứng viên: cùng số tham số, từng vị trí cùng loại hoặc `?` (`compatible`); cổng `reuse` dùng cùng hàm. Hạn chế đã biết: sổ tên đóng băng chữ ký ở thành viên đầu, `?` không bắc cầu nên một tên có thể gom hai chữ ký không tương thích với nhau; đếm cờ `param_conflict` trước khi 1.8 dựa vào số tham số.
- **Luật dừng 20% chữ không có ứng viên chỉ CẢNH BÁO** (chủ đề tài 18/11: "lúc run thật sự cũng sẽ không dừng mà run hết pipeline ... rồi sau đó mới quay trở lại xem các case lỗi"), áp cho cả kho đầy đủ. Cái mất: lần chạy có tái dùng thấp không bị chặn trước, chỉ lộ ở số đo sau. Trên tập con: 67/109 chữ không có ứng viên tối thiểu (lượt ≥2: 39/81 với lọc A39, 26/81 nếu chỉ cùng số tham số, 13/81 nếu không lọc).
- Hộp cát: đường dẫn Python dạng `/` (quy tắc quyền `Bash(<python> tiep.py:*)` của `claude -p` không khớp đường dẫn có `\`); `tiep.py` tự đặt `KLTN_TAP_CON`; `propositions.FULL_OUT` neo theo gốc repo.
- Kết quả (Sonnet 5.5, effort high, 4 lượt): 109 chữ có tên, 0 bị loại; reuse do LLM 1/109 (0,9%); 108 vị từ (65 concept, 43 input); vị từ dùng ở từ 2 Điều: 2; cặp ứng viên cho 1.7: 2. Không so với số bản cũ (3%, 108 cặp) vì khác quy mô.
- [THÊM, đã làm, `names-2.1`] Chủ thể chưa thành vị từ: `names-2` mới đặt tên `menh_de`, nên quy tắc "phải có giấy phép lao động" (D151.K1.d) sẽ áp cho mọi người lao động. Sửa: đưa chữ chủ thể (`chu_the.chu`) vào 1.6B làm chữ cần đặt tên (vai `chu_the`, như `names-1`), chạy lại 1.6B.
**1.8 (chủ đề tài chọn 18/11): máy biên dịch, LLM sửa khi lỗi.** Thay A33(1) ("LLM viết quy tắc"): máy dựng quy tắc từ `quy_tac` của 1.6A và tên vị từ 1.6B; quy tắc trượt cổng hoặc bị bộ quét bắt thì giao LLM sửa, tối đa 2 vòng, không đạt thì cô lập. Cái mất: chữ phương pháp trong bài báo phải đổi; chất lượng quy tắc phụ thuộc cách 1.6A gom `quy_tac` (chưa đo).
- Kết quả `names-2.1` (Sonnet 5.5, effort high, 6 lượt): 134 chữ có tên, 0 bị loại; reuse 4/134 (3,0%); 130 vị từ (65 concept, 65 input). D151.K1 nối chủ thể với định nghĩa: `foreign_worker_in_vietnam(X) :- holds_foreign_nationality(X)`.
- **1.8 lần chạy đầu (tập con):** 90 quy tắc, 1 cạnh ngoại lệ dùng (1.5), 1 quan hệ chặn (D154 chặn D151.K1.d), nạp s(CASP) đạt. Phép thử phản chứng D151/D154 bằng s(CASP), 4/4 ca đúng: (a) nước ngoài, kết hôn với người Việt, sinh sống ở VN cho `-must_holds_work_permit`; (b) nước ngoài, không thuộc diện miễn cho `must_holds_work_permit`; (c) kết hôn nhưng không sinh sống: vẫn `must_` (kiểm AND trong ngoại lệ); (d) không phải người nước ngoài: không ra kết luận nào.
- **Tiền tố phương thức tiếng Anh (chủ đề tài chốt 18/11).** Lần chạy đầu agent tự dùng nhãn 1.6A tiếng Việt (`phai_`) mà không ghi quyết định; user phát hiện tên lai hai thứ tiếng. Nay: `must_`, `may_`, `forbidden_`, `not_applicable_`; mô tả, định nghĩa không tiền tố. Cái mất: tên đầu không còn trùng chữ nhãn 1.6A, phải tra bảng 4 dòng này.
- **Cực phủ định ở đầu có phương thức: chèn `neg_` (chủ đề tài chốt 18/11).** Đặc tả 1.6A: cực chỉ phủ định nội dung. Bản đầu dịch sai "phải + phủ định" (D151.K1.c) thành `-phai_p` ("không bị buộc p"), trùng ký hiệu `-` với "được miễn do ngoại lệ". Nay: `must_neg_serving_criminal_sentence`. Đầu mô tả có cực phủ định vẫn là `-p`. Cái mất: câu hỏi "có bị cấm p không" không tự khớp với `must_neg_p`; bước 1.9 phải tra cả hai dạng.
- [THÊM] Dòng `ngoai_le` có cực phủ định được báo trong ghi chú 1.8 (dịch thành `not p` thì mất một lớp phủ định); tập con chưa có ca.
- Tiền tố mới không đụng tên vị từ: sổ 1.6B tập con không có tên bắt đầu bằng `must_`, `may_`, `forbidden_`, `not_applicable_`, `neg_`; khi chạy cả kho cần kiểm lại (lời nhắc chỉ cấm `must_`, `may_`).
- [THÊM] Bộ quét cô lập quy tắc thân rỗng (câu nêu giá trị không chủ thể, như D52.K2, D155 "thời hạn tối đa 02 năm"), vì đầu sẽ đúng cho mọi X.
- [THÊM] 1.7 chỉ dựng cặp từ vị từ của dòng mệnh đề, không từ vị từ chủ thể, và bỏ cặp mà vị từ chung là kết luận y hệt ở hai bên (cùng phương thức, cùng cực: không bên nào lật được bên kia). Trên tập con: 148 cặp còn 4 (giữ D53.K2 `may_` với D53.K3 `forbidden_` cùng hành vi). Là lọc ứng viên, không nới cổng. Cái mất: ngoại lệ ngầm giữa hai Khoản chỉ chung chủ thể (như D151.K1.d với D154; cặp này có cả cạnh 1.5 lẫn con trỏ ngoại lệ của 1.6A, trùng nhau nên báo cáo 1.8 ghi nguồn 1.5) không được đem hỏi.
- Bộ lọc cặp 1.7 ở trên: chủ đề tài giữ (18/11). Kết quả 1.7 trên tập con (Sonnet 5.5, effort high, 1 lô): 4/4 cặp trả `khong`, 0 cạnh. Đọc lại: hợp lý (D53.K2/K3 là hai danh sách trường hợp được phép và bị cấm tách rời; D151.K1.d/D153 là nghĩa vụ và hệ quả vi phạm, không lật nhau). Hạn chế: đơn vị câu dẫn (D53.K2) chỉ đưa chữ câu dẫn, không kèm các điểm con, nên LLM không thấy nội dung danh sách.
- Bộ câu hỏi dev Q10: chủ đề tài chốt 18/11 tính "bị bác" khi điều kiện bắt buộc của φ có sự kiện trái ngược (ký quỹ 1 tỷ < 2 tỷ), không chỉ khi có quy tắc ¬φ. Hệ quả cho 1.9: cần quy tắc từ điều kiện bắt buộc sang ¬φ, hoặc bước phân loại câu trả lời phải nhận ra điều kiện bị bác.
- Lỗi bộ quét còn mở, chờ vòng LLM sửa: (1) D153.K2-K3 "không có giấy phép lao động": `holds_work_permit` dưới `not` mà chỉ có đầu `must_holds_work_permit`, nên bị cô lập (đúng cổng). Có thể thay LLM bằng luật máy "concept chỉ xuất hiện sau tiền tố phương thức thì coi là input"; phải kiểm luật đó không che vị từ thiếu định nghĩa thật. (2) Trùng D55.K2.a với D55.K2.c: 1.6A đặt nội dung của điểm vào `liet_ke` (từ 3 mục, `menh-de-3`) và để `menh_de` là chữ câu dẫn "gồm các nội dung chủ yếu", nên 1.6B đặt cùng một tên và 1.8 (một ngôi, bỏ `liet_ke`) mất nội dung riêng của từng điểm. Bộ quét trùng chỉ bắt khi hai điểm trùng hệt; trên cả kho phần mất này sẽ xảy ra lặng lẽ ở mọi dòng có `liet_ke`.
**Cái giá và chỗ chưa kiểm.** Dẫn chiếu, `details`, ngoại lệ trỏ ra ngoài tập con treo hoặc chờ đích. Số đo trên tập con không đại diện cho cả kho. Mốc bị bỏ qua là chỗ chưa kiểm trên tập con. `corpus.in_subset` coi mọi mã không bắt đầu bằng `D` (Chương, Mục) của văn bản bị cắt là thuộc kho con; chưa mốc nào dựa vào điều này, bước sau dùng `in_subset` cho mã Chương/Mục thì phải sửa trước.
---

# Phần II. Quyết định ở mức từng bước nền

Các quyết định ở chỗ đặc tả im lặng hoặc lệch kế hoạch ban đầu của các bước đã xong. Mã dùng tiền tố theo bước.

## Nền (corpus, LLM client, báo cáo)
- **BA1.** Thông tin văn bản (số hiệu, ngày, số Điều) đọc từ `data/raw/labor/manifest.csv` (UTF-8 có BOM, đọc bằng `utf-8-sig`); không dùng file cấu hình riêng. Cấp văn bản (`level`), loại, cơ quan là bảng hằng trong `src/corpus.py`. Cột `quan_he` và `ghi_chu` của manifest chỉ là mốc kiểm, không phải đầu vào của pipeline.
- **BA2.** `src/llm_client.py` là nơi duy nhất gọi API: đọc `docs/llm_config.md`, lưu phản hồi thô vào `data/llm_cache/<tác vụ>/<khoá>.json`, đếm lượt theo ngày và theo vai ở `data/llm_cache/_usage.json`, chạm hạn mức thì ném `QuotaReached`. Khoá cache = sha256 của (model, tác vụ, phiên bản lời nhắc, đầu vào, system, lược đồ). Phản hồi sai lược đồ vào `_rejected/` kèm lý do, vẫn tính lượt, ném `InvalidOutput`. Giãn nhịp theo RPM (chờ đủ 60/rpm giây giữa hai lần gọi của cùng vai). Chế độ `off`, `replay` (chỉ đọc cache, thiếu thì `CacheMiss`), `live`.
- **BA3.** Log tiến độ LLM ghi ra stderr, chỉ cho lượt gọi API thật (một dòng trước, một dòng sau kèm giây và token; nhịp "vẫn đang chờ" mỗi 30 giây; lỗi 429/500/503 thì ghi mã lỗi và thời gian chờ). Lượt đọc cache không ghi dòng nào.
- **BA4.** Báo cáo chữ do code sinh ra ở `docs/run_reports/<module>/`, được theo dõi trong git; `data/processed/` bị `.gitignore` và dựng lại bằng `run_all`.
- **BA5.** Số đối chiếu của `checks` chỉ cho BLLĐ: 220 Điều, 638 Khoản, 267 Điểm. Nguồn độc lập với bước 1.1: grep trên file thô (Điều 220 = cột `so_dieu_dem_duoc`; Khoản 645 và Điểm 287 trừ 7 và 20 dòng nằm trong 4 khối trích dẫn của Điều 219, vì khối đó là chữ của luật khác). `checks.independent_counts` đếm lại bằng bộ đếm nháy riêng và phải khớp.

## Parse (1.1)
- **PS1.** Cấu trúc đọc: Chương > Mục > Điều > Khoản > Điểm. Kho không có Phần hay Tiểu mục; gặp thì lỗi (không đoán). Điều không thuộc Mục thì cha là Chương; không thuộc Chương thì không có cha trong thân.
- **PS2.** Mã: `<doc>.C<La Mã>.M<n>`, `.D<n>`, `.K<n>`, điểm `.a` (`đ` viết `dd`; điểm có hậu tố số: `.a1`). Điều có điểm đứng thẳng dưới Điều (ND_283 Điều 1): `D1.a`, cha là Điều. Hậu tố chữ (`D20a`, `K8a`) là bình thường; dấu chấm ngay sau số trong "8a.[2] ..." (văn bản hợp nhất) vẫn là Khoản; "4.960.000" không phải Khoản vì sau dấu chấm không có khoảng trắng.
- **PS3.** Đánh số phải liền: Điều n+1 hoặc hậu tố kế (20, 20a, 20b, 21); Khoản tương tự; Điểm theo bảng chữ (có `đ`, không có f j w z). Nhảy số là lỗi parse (thoát mã 1, không ghi file).
- **PS4.** Tiêu đề Chương và Mục có thể nằm cùng dòng hoặc ở dòng viết hoa kế tiếp; tiêu đề dài bị xuống dòng thì nối các dòng viết hoa liền sau.
- **PS5.** ND_145 có hai "Chương XI" (nguồn lặp nhãn); nhận có chủ đích (`corpus.DUP_CHUONG_OK`): mã lần sau là `CXI_2`, ghi vào `notes`. Mọi lỗi lặp khác vẫn là lỗi.
- **PS6.** Khối trích dẫn “...” đứng sau câu dẫn, hoặc mở nháy không đóng cùng dòng, là `payload` (`parse_payloads_<doc>.jsonl`), không phải đơn vị của văn bản chứa nó. Nháy cân bằng bằng bộ đếm “ ”; nháy mở không đóng đến hết văn bản là lỗi parse.
- **PS7.** Đoạn chữ không nhãn sau một Điểm gắn vào Khoản (ghi vào `notes`); gạch đầu dòng gắn vào đơn vị sâu nhất. (Lỗi đã biết: xem A38, phát hiện ở bước 1.1.)
- **PS8.** "Nơi nhận / chữ ký" bỏ khỏi đơn vị (đếm vào `skipped`), chỉ ở thân văn bản trước phụ lục đầu tiên; biểu mẫu trong phụ lục có "Nơi nhận" là nội dung mẫu.
- **PS9.** Chú thích `[n]` của bản hợp nhất: gỡ dấu `[n]` khỏi chữ, ghi bộ ba `footnote` trên đơn vị; vùng chú thích bắt đầu ở dòng "[1] ..." và dòng sau `[n]` (kể cả dòng trông như khoản) là chữ của chú thích.
- **PS10.** Phụ lục chia theo dòng tiêu đề (Phụ lục I.7, PHỤ LỤC đứng một mình, hoặc dòng viết hoa đứng trước "(Kèm theo ...)" khi văn bản không có nhãn như TT_11, TT_19); khối chỉ có tiêu đề (≤ 3 dòng) mà nhãn còn xuất hiện lại về sau là mục lục, bỏ. Mã phụ lục `.PL<nhãn>` (I.7 viết `I_7`); Mục `.M<n>`, "A. ..." `.L<chữ>`, "I. ..." `.S<La Mã>`, dòng `.R<k>`. Biểu mẫu "Mẫu số ..." chưa tách thành nút form.
- **PS11.** Phạm vi phụ lục: NQ 66.16 kèm 14 phụ lục của các bộ, chỉ Phụ lục I.7 (cho thuê lại lao động, sửa quy định ND 145) thuộc phạm vi lao động nên được bóc chi tiết (`corpus.PL_IN_SCOPE`); 13 phụ lục còn lại và Phụ lục II giữ một nút `scope=out_of_scope` để dẫn chiếu vẫn giải được. Dẫn chiếu tới phụ lục chưa có file nguồn thành `unresolved` có lý do, không phải lỗi. Bản đầy đủ NQ 66.16 được chuẩn hoá bằng `utils/normalize_text.py` (CRLF thành LF, NFC, bỏ dòng "## ", dòng kẻ ngang, khối "Nơi nhận" của chính văn bản); phần thân giống hệt bản trước (kiểm bằng diff).
- **PS12.** Bảng lương vùng bị trải mỗi ô một dòng: ghép lại thành bảng (`parse_tables_<doc>.jsonl`) khi gặp đúng dạng "Vùng / Mức ... tháng / Mức ... giờ". Đơn vị giữ nguyên chữ gốc. Chỉ ND_74 có bảng này (mốc vùng I 4.960.000).
- **PS13.** Đầu văn bản (số hiệu, ngày, căn cứ) đọc bằng regex rồi so với manifest; lệch thì cờ `so_hieu_lech_manifest` hoặc `ngay_ky_lech_manifest`. TT_09, TT_10, TT_11 mất phần đầu nên lấy từ manifest (cờ `header_from_manifest`); TT_09 và TT_10 còn cờ `issued_uncertain` (ngày ký ghi dấu "?").
- **PS14 (giới hạn).** Dòng của bảng trong phụ lục (TT_11: 1.985 dòng "TT | Tên nghề | Đặc điểm ...") là một đơn vị `pl_row` mỗi dòng, chưa tách cột.

## Refs (1.2)
- **RF1.** Chọn Bộ luật Lao động 2012 hay 2019 cho cụm "Bộ luật Lao động" không kèm số: **không** theo ngày ký (dữ liệu phản bác: ND_28-2020 ký 01/03/2020 nhưng căn cứ BLLĐ 2012; ND_135-2020 ký 18/11/2020 nhưng căn cứ bản 2019). Quy tắc: ngày trong dòng "Căn cứ Bộ luật Lao động ngày ..." (trước 20/11/2019 là 2012); thiếu dòng đó (TT_09/10/11 mất đầu) thì theo ngày hiệu lực của văn bản nguồn (từ 01/01/2021 là 2019). Bản 2012 ngoài kho: quan hệ chờ đích với số hiệu 10/2012/QH13 (lấy từ hiểu biết ngoài repo, không kiểm được trong kho).
- **RF2.** Quan hệ chờ đích (thay hai cờ `target_not_loaded` và `target_outside_corpus`): `refs_pending_<doc>.jsonl` và `pending_links.jsonl` (nguồn, loại cạnh, số hiệu đích, mã đích, câu nguyên văn). Chưa có bước nối khi văn bản đích được nạp ở mức tĩnh; bước 2.3-2.4 chạy ở mức sự kiện.
- **RF3.** Cụm dẫn chiếu = chuỗi mục "từ khoá + đối số" (Điều/khoản: số có hậu tố chữ; điểm: chữ kèm số tuỳ chọn; "này" đứng riêng), danh sách cùng loại ("khoản 1, 2 và 3"), nối bằng dấu cách, phẩy, chấm phẩy, "và", "hoặc", "của". Đuôi văn bản ngay sau cụm: "của Bộ luật này", "Nghị định số 145/2020/NĐ-CP", "Bộ luật Lao động", "Luật ...".
- **RF4.** Một chuỗi tách thành nhiều dẫn chiếu khi cấp đi từ thô xuống mịn ("Điều 18, điểm a khoản 1 Điều 145"), hoặc ngay sau mục "này", hoặc mục Điều thứ hai sau chuỗi đã có mục thấp. Viết lược "điểm h khoản 1 và điểm đ khoản 2 Điều này": Điều ở dẫn chiếu cuối dùng chung cho dẫn chiếu trước. Đối số là danh sách chỉ được ở mục thấp nhất; mục cấp trên nhiều đối số, "điểm này", cụm kết thúc ở khoản/điểm không kèm Điều: `unresolved`. Tách điều kiện "mục Điều thứ hai" làm tăng 35 cạnh, không mất cạnh nào (ND_145 8, ND_12 4, ND_283 23).
- **RF5.** Cụm đủ Điều/khoản nhưng không nêu văn bản đích (Điều 1 của ND_145: "theo khoản 3 Điều 12" là Điều 12 của BLLĐ, nêu ở câu dẫn) giữ `unresolved` kèm lý do; bước 2.2 dùng chính các đơn vị đó tạo cạnh `details`. Không đoán đích ở bước này.
- **RF6.** Dòng chỉ thị sửa đổi (động từ chỉ thị đi liền danh từ đích: "Sửa đổi, bổ sung khoản 6 ...", "Bãi bỏ điểm c ...", "Thay thế cụm từ ...", "Đính chính ...", "Tạm ngưng hiệu lực ...") **không** sinh `refers_to`: dẫn chiếu trong đó trỏ vào văn bản bị sửa, việc của bước 2.3. Không nhận "Sửa chữa, làm sai lệch ...", "Thay đổi cơ cấu ..." (điều quy tắc bình thường). Đã kiểm trên 10.202 đơn vị: thêm các động từ Đính chính, Tạm ngưng, Đình chỉ không đổi dòng nào.
- **RF7.** Nhiều cụm cùng trỏ một đích: giữ một cạnh, `evidence` là cụm đầu. `unresolved` trùng (cùng đơn vị, cụm, lý do) ghi một lần.
- **RF8.** Số liệu kho: `refers_to` 2.348 (gồm 245 của VBHN_125; đồ thị không vẽ cạnh của bản hợp nhất nên báo 2.103), chờ đích 129, `unresolved` 127.

## Delegation (1.3) và Links (2.2)
- **DL1.** Điều khoản giao chi tiết đếm bằng regex trên BLLĐ: dạng A 35 cụm / 34 Điều, B 10 / 8, D 5 Điều (61, 142, 143, 146, 160), E 1 (Điều 112); tổng 51 cụm ở 51 đơn vị. Kế hoạch ban đầu nêu A 39/37 (tổng khoảng 55 cụm / 50 Điều): chênh dạng A (4 cụm, 3 Điều) chưa giải thích được. Mốc cổng (`D91.K4`, `D154.K1/K2/K9`, `D142.K1`, `D112`) đều đạt. Chưa lọc ca không phải giao chi tiết (`D61.K4`, `D160.K2` khớp mẫu D nhưng nghĩa là điều kiện).
- **DL2.** Tầng lỏng (A15, B9): câu có bên được giao (Chính phủ, Bộ trưởng, Thủ tướng) đứng gần động từ giao (quy định, ban hành, hướng dẫn, quyết định) mà tầng chặt không bắt thì giữ với `pattern=loose` và cờ `loose`. BLLĐ ra 5 ca: `D21.K5`, `D73.K4`, `D145.K4`, `D147.K3` (đều "Bộ trưởng Bộ Lao động - Thương binh và Xã hội quy định ...": tầng chặt hụt vì dạng A chỉ cho các từ toàn chữ cái giữa "Bộ trưởng" và "quy định", dấu gạch ngang chặn lại) và `D133.K1` ("Chính phủ quyết định" một chương trình, có thể không phải điều khoản giao thật). Không nới regex chặt; ca lỏng không đưa vào danh mục đối chiếu của bước 2.2 (đưa vào thì lời nhắc đổi và cache hỏng).
- **LK1.** `based_on` đọc từ dòng "Căn cứ ...": cụm điều/khoản kèm văn bản thành cạnh tới đơn vị (TT_18 → ND_145.D68.K2), số hiệu văn bản thành cạnh tới văn bản. Bảy văn bản không có `based_on`: ND_90, ND_28 (căn cứ BLLĐ 2012: chờ đích), TT_09/10/11 (mất đầu), TT_19 và NQ_66-16 (không căn cứ vào văn bản trong kho).
- **LK2.** `details` đọc từ Điều 1: văn bản đích lấy từ cụm hoặc từ câu dẫn ("... sau đây của Bộ luật Lao động:"). ND_152 → `D154.K1/K2/K9`, `D157`, `D150.K3`; TT_10 → `D21.K1-3`, `D73.K4`, `D142.K1`; ND_135 → `D169`. Kho: 10 `based_on`, 48 `details`, 58 cạnh tổng; 40/51 điều khoản giao đã có văn bản lấp.
- **LK3.** `filled_by` của điều khoản giao = các văn bản có `details` tới chính điều khoản đó, tới tổ tiên hoặc con cháu của nó, theo ngày hiệu lực (ghi ở `links_filled.jsonl`).
- **LK4.** ND_74 → Điều 91 (văn bản không nêu số Điều) được nối bằng từ khoá và LLM: giữ cạnh `details` khi model chính đề xuất, model kiểm đề xuất độc lập cùng Điều, và kiểm từ khoá đạt (cụm danh từ chính của phạm vi điều chỉnh nằm trong tiêu đề hoặc chữ Điều đích); trượt một trong ba thì ghi cạnh nhưng cờ `isolated` (đồ thị vẫn vẽ, kèm cờ). Đề xuất chỉ do từ khoá không bao giờ được giữ khi đã chạy LLM. Chỉ cho văn bản cấp dưới luật có `based_on` BLLĐ 2019 mà regex không ra `details` tới BLLĐ (ND_12, ND_283, ND_74): 3 lượt chính, 3 lượt kiểm. Hai lượt độc lập cùng đầu vào (chữ Điều 1, tiêu đề các Điều, danh sách điều khoản giao), không có gợi ý đích; `unit_id` ngoài danh sách thì loại cả lượt. Đã chạy live (8 bản ghi trong cache `links_details`).

## Article type (1.4)
- **AT1.** Mẫu tiêu đề: "Giải thích từ ngữ" → `definition`; "Hiệu lực", "chuyển tiếp", "Điều khoản thi hành", "Bãi bỏ", "Sửa đổi, bổ sung ..." → `effect_transition` (nguồn chỉ thị của bước 2.3); "Trách nhiệm của <Bộ, cơ quan, Ủy ban, Sở, Chính phủ ...>", "Trách nhiệm thi hành", "Thẩm quyền", "Nhiệm vụ" → `authority`; "Hồ sơ", "Trình tự", "Thủ tục" → `procedural`. "Trách nhiệm khi chấm dứt hợp đồng lao động" **không** phải `authority` (là nghĩa vụ của các bên); có test. Nhãn thêm `appendix` cho 28 phụ lục. Nhãn `form` của kế hoạch ban đầu không dùng (bước 1.1 không tách "Mẫu số"). Siết mẫu: A21.

## Exceptions (1.5)
- **EX1.** Ngoại lệ tường minh: quy tắc 1 (cụm dẫn chiếu đứng ngay trước "không áp dụng") và quy tắc 2 ("trừ" + text kết thúc "sau đây:", con trực tiếp là ngoại lệ). Không nới để bắt thêm ca: ca ngoài hai quy tắc vào `unhandled` kèm lý do. Mọi trigger thuộc đúng một trạng thái (có test trên cả 18 văn bản). Siết: A22.
- **EX2.** Ngoại lệ chung: nút điều kiện có id `<doc>.X<8 ký tự đầu sha1 của khoá chuẩn hoá>`; câu giống nhau (gộp khoảng trắng, hoa thường, bỏ `. ; : ,` ở hai đầu) gộp một nút. `kind`: `tuy_nghi` ("(các bên) có thoả thuận khác"), `dan_chieu_mo` ("pháp luật có quy định khác"), `cu_the` (còn lại, khớp toàn bộ mệnh đề). Mệnh đề có cụm dẫn chiếu tới đơn vị T thì thêm cạnh T `exception_of` đơn vị (`general_except_ref`); T có thể ở văn bản khác. BLLĐ: 30 nút (39 đơn vị), 59 cạnh. Mở rộng "trừ <danh từ>": A24, A31.
- **EX3.** Chiều cạnh: `s` là phần ngoại lệ, `o` là quy tắc bị ngoại trừ. Mốc cổng theo chữ thật của BLLĐ: `D154` → `D151.K1.d`; `D29` → `D35.K2.a`; `D97.K4` → `D35.K2.b`; `D36.K1.b` → `D37.K1` (cạnh đi từ đơn vị được dẫn tới đơn vị chứa "trừ trường hợp").

## Versions (2.3 và 2.4)
- **VS1 (loại 10).** Hết hiệu lực theo chủ đề (ND_219 Điều 35 khoản 2) làm bằng regex trên tiêu đề Chương, không LLM: Chương có tiêu đề chứa chủ đề thì đóng tại ngày hiệu lực; Chương chung ("quy định chung", "điều khoản thi hành", "điều khoản chuyển tiếp") thì `suspended` kèm cờ `topic_uncertain` (đơn vị không chắc thì không đóng hẳn); Chương khác giữ nguyên. Kết quả ND_152: Chương II (người lao động nước ngoài) đóng từ 2025-08-07 (134 đơn vị `expired`); Chương III (người Việt Nam làm cho tổ chức nước ngoài) giữ `in_force` (49); Chương I và IV `suspended` (91). Cạnh `expires_by_topic` mang cờ `topic_by_chapter`.
- **VS2.** NQ_66-16: `effective_to` = 2027-03-01 (khoảng nửa mở), tương ứng "đến hết ngày 28/02/2027".
- **VS3.** Chuẩn hoá chữ khi so phiên bản (`textutil.text_norm`): NFC, `casefold`, kiểu đặt dấu thanh (hòa/hoà, ủy/uỷ), bỏ `[n]`, thống nhất gạch, **bỏ mọi khoảng trắng** (xử lý dính chữ "ngàyhoặc"), bỏ dấu câu cuối. Chữ khác ở số ("điều 189" và "điều 89") vẫn khác (có test).
- **VS4 (loại 15, bản hợp nhất).** VBHN_125 không tạo nút riêng; chỉ so từng đơn vị với BLLĐ gốc. Kết quả: 1.115 đơn vị giống sau chuẩn hoá; Điều 154 khoản 8a là đơn vị mới thật, hiệu lực 2026-01-01 lấy từ chú thích [2] (không lấy ngày ký bản hợp nhất), cờ `from_consolidation`; bốn đơn vị chỉ khác chỗ ngắt dòng không phải sửa đổi; cờ `consolidation_discrepancy` (không tạo phiên bản) cho Điều 185 khoản 4 ("189" thành "89", lỗi bản hợp nhất), Điều 220 khoản 3 (bản hợp nhất cắt câu cuối), Điều 42 khoản 2 và hai điểm a, b (mất đánh dấu điểm), Điều 87 (dòng tiêu đề và nội dung dính thành một dòng).
- **VS5 (loại 8).** Bổ sung danh mục (TT_19 → TT_11): TT_19 không nêu số hiệu TT_11 nên khớp qua tên danh mục (tiêu đề Điều "Bổ sung Danh mục ..." so với tiêu đề phụ lục bằng `text_norm`); cần đúng một phụ lục khớp, không thì `unknown_directive`. Kết quả: 170 dòng mới từ 2024-02-15, dòng cũ không đổi phiên bản, cạnh `supplements_list`.
- **VS6.** Hiệu lực là nửa khoảng `[effective_from, effective_to)`; "đến hết ngày X" thì `effective_to` = X + 1 ngày. Không xoá nút. `state` ∈ `normal`, `pending_event`, `suspended` (hai trạng thái sau không bao giờ `in_force`); `status` suy ra tại ngày hiệu lực của sự kiện cuối.
- **VS7.** Thứ tự sự kiện: theo ngày hiệu lực, cùng ngày theo ngày ban hành rồi `doc_id`. BLLĐ gốc nạp trước, không là sự kiện. ND_90 (hiệu lực 2020-01-01) và ND_28 (2020-04-15) có hiệu lực trước BLLĐ 2019: nạp bình thường, cờ `law_2012_era_document` (loại 18), không nối vào số Điều BLLĐ 2019.
- **VS8.** Hai chỉ thị cùng sự kiện cùng sửa một đơn vị: sửa tại chỗ phiên bản đã tạo trong sự kiện đó (không tạo phiên bản `[d, d)` rỗng).
- **VS9.** Khối trích dẫn thành cây Điều/Khoản/Điểm; khối không nhãn (ND_70 "khoản 7 Điều 17") là chữ của đơn vị đích duy nhất; con cũ không còn trong khối thì bị đóng (cờ `removed_by_replace`); "Sửa đổi tên khoản 8 Điều 9" chỉ đổi chữ khoản. Bổ sung vào mã đã có hoặc cha không tồn tại là lỗi, không đoán.
- **VS10.** Thay cụm từ: khớp mềm (khoảng trắng, dấu thanh, hoa thường); cụm không thấy trong đích ghi vào danh sách "đích / cụm không khớp", không làm lỗi cả bước. Hai chỉ thị cụm từ nhiều đích là một chỉ thị.
- **VS11.** Chỉ thị sửa Mẫu số hay Phụ lục của văn bản bị sửa (ND_70: 8 chỉ thị về Mẫu số của ND_152): ND_152 không có phụ lục hay mẫu trong kho nên không áp được; cờ `form_directive_target_not_in_kb`, không lỗi.
- **VS12 (loại 5, 24).** Hết hiệu lực cả văn bản: đóng cả cây đơn vị tại ngày nêu trong câu (hoặc ngày hiệu lực văn bản mới), cạnh `replaces`; đích ngoài kho thì quan hệ chờ đích kèm cạnh tới `external:<số hiệu>`. Một đơn vị chứa cả câu hiệu lực lẫn câu hết hiệu lực (ND_90 Điều 6 khoản 1) được tách theo câu. Bị hủy bỏ do trái luật: đóng như loại 5, cờ `annulled`.
- **VS13 (loại 11, 12).** Hiệu lực có điều kiện: đơn vị đích thành `pending_event`, `effective_from = null`, `trigger` = nguyên văn sự kiện, cạnh `pending_on` (ND_283 Điều 66 khoản 2, 3 ở trạng thái đó đến hết chuỗi dev). Kích hoạt (`directives.trigger_matches`) khi đủ ba điều kiện: (1) cùng loại văn bản với câu mô tả; (2) mọi số hiệu mô tả nêu đều có trong chữ của văn bản mới; (3) cụm mô tả chính văn bản kích hoạt nằm trong Điều 1 của nó và dài từ 12 ký tự sau chuẩn hoá. Điều kiện (3) được thêm vì ND_219 Điều 35 trích đúng hai số hiệu mà mô tả của ND_283 Điều 66 khoản 3 trích, nên bản đầu kích hoạt nhầm. Hạn chế: thất bại an toàn (đơn vị vẫn chờ); văn bản thật mà Điều 1 diễn đạt khác câu mô tả sẽ không khớp. Chưa có ca dương trên dữ liệu thật.
- **VS14 (loại 13, 14).** Cạnh `ends_when_replaced` từ câu "quy định tương ứng trong Nghị quyết này hết hiệu lực" (Điều 19 khoản 2); cạnh `overrides` từ mục phụ lục I.7 tới các Điều của văn bản khác nêu trong tiêu đề mục, khoảng `[2026-04-15, 2027-03-01)` (6 cạnh). Tiêu đề mục I.7 nêu Điều 24-28 của ND_145; Điều 21-23 chưa tìm thấy trong I.7 nên chưa nối.
- **VS15 (loại 25, 26).** Văn bản được hướng dẫn bị đổi: cạnh và cờ `parent_changed`, không đóng văn bản hướng dẫn. Loại 26: cờ và cạnh `possible_replacement` khi văn bản mới cùng loại và cùng tên (bỏ số, năm, ngoặc) với văn bản cũ chưa đóng; không tự đóng. So tên theo cột `ten_ngan` của manifest (do người thực hiện đặt), không phải tiêu đề trong chữ văn bản; chuỗi dev không phát sinh ca nào.
- **VS16.** Nguồn ngày hiệu lực: manifest rồi đối chiếu với câu "<loại> này có hiệu lực ... từ ngày ..." trong chữ (`own_effective`); 16/16 văn bản dưới luật có câu đó, 0 văn bản lệch. VBHN_125 lấy ngày từng đơn vị từ chú thích.
- **VS17 (loại 19 đến 22, 20).** Hồi tố: `applies_from` sớm hơn `effective_from`; nếu câu nêu trách nhiệm pháp lý mới hoặc nặng hơn thì không áp (`retroactive_blocked`). Tạm ngưng: `suspended` từ D1, trở lại `normal` từ D2 + 1; không D2 thì mở. Đánh số lại: mã cũ đóng, mã mới mở với chữ cũ, cạnh `renumbered_to`; mã mới đã có hoặc mã cũ không còn là lỗi. Đính chính: lưu chữ trước và sau vào `corrections.jsonl`, cạnh `corrects`, không tạo phiên bản pháp lý.
- **VS18.** Chạy lại cả chuỗi hai lần ra file giống hệt (có test). Quan hệ chờ đích của bước này ghi `data/processed/versions/pending_links.jsonl`, tách khỏi `pending_links.jsonl` của bước 1.2.
- **VS19 (còn mở).** Một chỉ thị đọc được nhưng không khớp đích: ND_70 Điều 1 khoản 14 điểm c "Bãi bỏ điểm a khoản 6a Điều 30" (ND_152): ND_152 Điều 30 có khoản 6 nhưng không có khoản 6a; có thể ND_70 tham chiếu sai hoặc kho khác bản; không đoán, ghi vào báo cáo.

## Checks
- **CK1.** `src/checks.py` kiểm độc lập các bước 1.1 đến 2.4: 1.1 (số đơn vị = manifest = đối chiếu cứng = đếm độc lập); 1.2 (cấu trúc, hai đầu `refers_to` tồn tại, `evidence` nằm trong text nguồn, mốc `ND_152.D7` → `BLLD.D154`); 1.5 (mốc `exception_of`, hai đầu tồn tại, ca chưa xử lý của BLLĐ phải đúng danh sách đã biết); 2.2 (đích có thật); 1.4 (mọi Điều có nhãn); 1.6 (cài lại độc lập, không import module bước đó); 2.3-2.4 (số phiên bản liên tiếp, khoảng không chồng, không mất nút, phiên bản 1 = chữ của bước 1.1, hai đầu cạnh tồn tại). Các hàm kiểm có test với dữ liệu hỏng cố ý.
- **CK2 (đã sửa).** Kiểm bước 1.6 báo oan cụm `chapeau` ở khoản vì chưa theo A35; sửa bằng hàm `lead_in_text` tính độc lập, kèm một test.

## Graph
- **GR1.** Nút: văn bản, đơn vị (từ `versions.jsonl`, mỗi nút giữ danh sách `[từ, đến, state, version]`), nút điều kiện (bước 1.5 chung), nút `external:<số hiệu>`. Cạnh ngữ nghĩa: `refers_to`, `exception_of`, `based_on`, `details` và mọi cạnh của bước 2.3-2.4. Cạnh cấu trúc không ghi (cha ở khoá `parent`). Cạnh của VBHN_125 không đưa vào (nó chỉ tạo phiên bản trên BLLĐ). Nhãn `source` của cạnh: `refs`, `exceptions_explicit`, `exceptions_general`, `links`, `versions`.
- **GR2.** Nút không bao giờ bị xoá: đơn vị hết hiệu lực vẫn có nút, trang xem làm mờ theo ngày. Kho: 9.364 nút, 2.721 cạnh, 17 mốc ngày.

## Viewer
- **VW1.** Trang xem `data/processed/viewer/graph_viewer.html` mở offline: mặc định mức Điều (khoảng 700 nút), bấm đúp Điều hoặc phụ lục để mở Khoản, Điểm, dòng; lọc theo văn bản; ô chọn ngày dùng khoảng hiệu lực nhúng sẵn (đổi ngày không dựng lại file); bố cục `cose` của Cytoscape (đi kèm thư viện trong `utils/viewer/vendor/`). Kiểm bằng Edge không giao diện: ngày 2025-06-01 có ND_152 Điều 7 khoản 8 và không có khoản 13 của ND_219; ngày 2025-10-01 ngược lại. Trang khoảng 4,7 MB, dựng khoảng 5 giây.

---

# Phần III. Số đo và quan sát

- **S1 (đo thô 11/11 trên BLLĐ; không phải cổng).** Bước 1.2: 98 đơn vị có chữ "Điều <số>", 93 có kết cục, 5 sót (cả 5 là dòng chỉ thị sửa đổi trong Điều 219 mà thiết kế cố ý không sinh `refers_to`). Bước 1.3: regex lỏng ra 56 đơn vị; 51 đã là điều khoản giao; 5 chưa (`D133.K1`, `D145.K4`, `D147.K3`, `D21.K5`, `D73.K4`; 4 trong 5 trông như điều khoản giao thật). Bước 1.4 (trước khi bỏ LLM): 220 Điều, regex xếp 23, 197 đi qua LLM. Bước 1.5: 0 cạnh tường minh (sau A22), 59 cạnh `exception_of` chung, 30 nút điều kiện (26 `cu_the`, 3 `tuy_nghi`, 1 `dan_chieu_mo`).
- **S2 (bỏ LLM khỏi bước 1.4).** Nhãn đổi 93/921 Điều (50 `definition`, 34 `authority`, 9 `procedural` thành `substantive`); 39 `effect_transition` không đổi (cả 39 do regex đặt nên bước 2.3 không mất nguồn chỉ thị). Đồ thị chỉ khác trường `label_class` ở 64 nút.
- **S3 (bước 1.2, tầng 2).** Kho có 127 cụm không giải được: 13 khoản/điểm trơ trụi (đều ở văn bản dưới luật), 24 cụm nhiều đối số kiểu "điểm đ khoản 5, khoản 6 Điều này", 50 phụ lục không có trong kho, 38 đích không tồn tại trong văn bản, 2 "điểm này". BLLĐ có 0 ca nên tầng 2 hoãn.
- **S4 (bước 1.5 và bước 1.8).** 66 cạnh `exception_of` của BLLĐ: 23 cạnh đơn vị sang đơn vị; 43 cạnh từ nút điều kiện (15 trùng ý với một cạnh đơn vị; 28 không có đơn vị đích: 19 `cu_the`, 7 `tuy_nghi`, 2 `dan_chieu_mo`). Chuỗi ngoại lệ lồng nhau thật: `D14.K1` ← `D14.K2` ← {`D18.K2`, `D145.K1.a`, `D162.K1`}.
- **S5 (thử s(CASP), một biến, ví dụ nhỏ).** (1) Ngoại lệ lồng ba tầng biên dịch bằng `blocked(r,X) :- applies(e,X), not blocked(e,X)` ra đúng cả 4 ca thử. (2) Vị từ không có quy tắc nào: s(CASP) chỉ cảnh báo "predicate does not exist" và coi là sai (dưới `not` thì thành đúng), nên quy tắc gốc không bao giờ bị chặn: cần cổng. (3) Phủ định thật `-p` cho ba trạng thái nhưng cần quy tắc kết luận phủ định. (4) Biến không khớp giữa hai đầu cạnh cho kết quả sai mà không báo lỗi: cần cổng "biến của vị từ ngoại lệ phải nằm trong biến của quy tắc gốc, không thì cô lập". (5) Các mệnh đề cùng vị từ phải nằm liền nhau trong mã sinh ra hoặc khai báo `discontiguous`.
- **S6 (bước 1.6B bản cũ).** Số liệu đầu vào: 3.061 hàng cụm, 152 có `targets`, 1.924 chữ khác nhau (theo `text_norm`), chọn 1.833 chữ không có `targets`; 76 lượt (nhỏ nhất 3, trung vị 25, lớn nhất 30); trung vị 7 ứng viên, 607 chữ chạm trần 12. Số chữ không có ứng viên tối thiểu 220/1.833 (12%), dưới luật dừng 20%.
- **S7 (kiểm độc lập).** Các số đối chiếu cứng của BLLĐ: 220 Điều, 638 Khoản, 267 Điểm; 10.202 đơn vị và 893 Điều trên cả kho (18 văn bản); `refers_to` 2.348; chờ đích 129; điều khoản giao 51 chắc cộng 5 lỏng.
