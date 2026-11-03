# Sổ quyết định của luận văn (cập nhật 20/10/2026)

Mỗi dòng ghi một quyết định đã chốt: chọn gì, vì sao, bằng chứng ở đâu, và điều gì sẽ buộc phải đổi. Quyết định mới thì thêm dòng, không xoá dòng cũ; quyết định bị thay thì ghi "thay bởi Qx".

Tên file trong cột bằng chứng đều nằm trong thư mục `claude/` của project. File viết trước 12/10 dùng số tham khảo cũ (xem `BanDo_TaiLieu.md` mục 3). Trong sổ này, số tham khảo theo v5.

## A. Hướng và phạm vi

| Mã | Quyết định | Lý do | Bằng chứng | Đổi khi |
|---|---|---|---|---|
| Q1 | Cốt lõi là **xây dựng cơ sở tri thức** (chống trùng lặp, kết hợp neural và symbolic). Suy luận ngoại lệ là phần áp dụng (9/10). Từ 11/10 chuyển từ bán tự động sang tự động tối đa (xem Q13) | LLM thương mại trả lời đúng câu hỏi ngoại lệ lồng, nên "suy luận đúng hơn LLM" không đứng được. Thầy ưu tiên xây cơ sở tri thức trước | Lần hỏi thử Gemini, Grok (7–8/10); lời thầy 8/10 và 11/10 | Thầy đổi hướng |
| Q2 | Hướng nghiên cứu, 15 tín chỉ. Hạn đề cương 5/11/2026. Thời gian làm 6 tháng | Quy định | Học viên xác nhận 10/10 | — |
| Q3 | Phạm vi: Bộ luật Dân sự 2015, Điều 609–662. Không tìm văn bản sửa đổi thật | Phần này chưa sửa từ 2015 (học viên xác nhận "chắc chắn" 12/10). Phần lõi tách khỏi phần phụ thuộc lĩnh vực để đổi chế định khác được | Đề cương mục 4 | Phát hiện văn bản sửa đổi thật |
| Q4 | Các cơ chế thầy giao ngày 11/10 là **bắt buộc**. Tìm được tính mới trong đó là phần thêm, không phải điều kiện | Thầy soạn sẵn danh sách "em phải làm trước" | Danh sách nguyên văn trong `BanGiao` và memory | — |
| Q5 | Làm lớp văn bản trước (tách, định danh, liên kết, cập nhật), rồi sổ khái niệm, ngoại lệ ngầm, cuối cùng là quy tắc và bộ quét | Thầy ưu tiên xây cơ sở tri thức trước | `BanGiao` mục 3 | Thầy trả lời câu hỏi về quét xung đột trên lớp văn bản (xem mục G) |

## B. Tính mới và động cơ

| Mã | Quyết định | Lý do | Bằng chứng | Đổi khi |
|---|---|---|---|---|
| Q6 | **Không** dùng "LLM mạnh trả lời sai ngoại lệ lồng" làm động cơ. Giữ "không bảo đảm kết luận đổi đúng, không kiểm tra được căn cứ" như động cơ thiết kế | Không có bài có bình duyệt nào cho thấy mô hình mạnh sai. Báo cáo duy nhất có thí nghiệm (Aethis, arXiv) cho 97–100% | `TraCuu_CongTrinhGanNhat` mục 2; `SangLoc` bảng mục 3 dòng 4 | Có bài có bình duyệt cho thấy mô hình mạnh giảm rõ theo độ sâu |
| Q7 | Mọi cơ chế (chặn đệ quy, phản bác / vô hiệu hoá, khử trùng, cập nhật, tự sửa, cô lập) ghi là **"áp dụng"** | PROLEG, Catala, Ulizko [7] đã có ngoại lệ lồng. [5] đã có khử trùng và cập nhật. [7] đã có kiểm tra rồi cho trích lại | `GhiChuDoc` mục 1, 3, 16, 18; `DeXuat_ND1_ND2_v4.4` mục 2 | — |
| Q8 | Ba điểm mới: bộ dữ liệu; số liệu so với cách LLM tự viết chương trình; chọn vị từ bằng đồ thị khái niệm | Đây là các phần chưa thấy công trình nào làm, sau khi trừ các bài đã đọc | `GiaiThich_KhaiNiem` mục 14; `SangLoc` mục 4 | Law to Code hoặc một bài chưa đọc đã làm (xem mục G) |

## C. Thiết kế cơ sở tri thức

| Mã | Quyết định | Lý do | Bằng chứng | Đổi khi |
|---|---|---|---|---|
| Q9 | Đồ thị hai lớp (văn bản, quy tắc). Lưu bộ ba trong CSV hoặc JSONL, duyệt bằng `networkx`. Không dùng cơ sở dữ liệu đồ thị | Đủ cho 54 điều. Giống cách lưu của [5]. Thầy nói đồ thị chỉ là đỉnh và cạnh (học viên lưu ý: bộ ba chỉ là ví dụ của thầy, không phải trọng tâm) | `BanGiao` mục 0, 4 | Quy mô lớn hơn nhiều |
| Q10 | Chọn vị từ cho LLM theo **đồ thị khái niệm**, không theo đồ thị dẫn chiếu | Dẫn chiếu tường minh chỉ phủ 2–7% số cặp khái niệm–điều dùng. Quan hệ giữa các điều chủ yếu là ngầm | `PhepThu_DoPhuDanChieu` phần đầu | — |
| Q11 | Sổ khái niệm có hai loại vị từ. Vị từ đầu vào do học viên soạn. Vị từ khái niệm gắn với điều định nghĩa. LLM chỉ dùng vị từ trong sổ, thiếu thì gắn cờ. Đóng băng sổ trước khi viết tập kiểm tra | Chặn lỗi đặt tên mới (Horner [6] mục 5.2, 5.3) và lỗi "cắt bằng INPUT". Đóng băng để tránh rò thông tin từ tập kiểm tra | `GhiChuDoc` mục 12; `PhepThu_DoPhuDanChieu` Phép thử 2, 4; `BanGiao` mục 3B | Phép thử 5 điều cho thấy cách soạn khác tốt hơn |
| Q12 | LLM nháp vị từ theo từng điều, học viên chuẩn hoá và chốt, rồi chạy kiểm tra C1–C4. **Tạm thời**, chốt sau phép thử 5 điều | Chưa biết LLM có tìm thêm được cụm điều kiện nào so với làm tay | `BanGiao` mục 3B, 5 | Kết quả phép thử 5 điều (621, 626, 644, 650, 651) |
| Q13 | Ngoại lệ ngầm: đồ thị khái niệm sinh cặp ứng viên, LLM đề xuất, bộ quét kiểm. Người chỉ xem mục bị gắn cờ hoặc bị cô lập, không duyệt toàn bộ | Học viên không có kiến thức luật, làm tay tốn thời gian mà không thêm độ đúng (11/10). Trong các chuỗi ngoại lệ, cạnh xuyên điều tường minh chỉ khoảng 3, cạnh ngầm khoảng 10 | Memory 11/10; `SangLoc` mục 2.3 | — |
| Q14 | **Quy ước phạm vi khoản 2 Điều 621:** chỉ khôi phục quyền hưởng theo di chúc. Không khôi phục thừa kế theo pháp luật, không khôi phục suất ở Điều 644 | Câu chữ "cho họ hưởng di sản theo di chúc". Lấy từ một lượt tra cứu web 11/10. Thầy và học viên đều không phải chuyên gia luật | Memory 11/10; `SangLoc` mục 4 (lỗi phạm vi ở chuỗi C1) | Người có chuyên môn luật đọc khác |
| Q15 | **Quy ước PROLEG:** điều kiện của ngoại lệ mà tình huống không nêu thì coi như không có. "Chưa đủ căn cứ" chỉ khi thiếu điều kiện của quy tắc chính | Theo nghĩa vụ chứng minh trong PROLEG [2] | `GhiChuDoc` mục 16 | — |
| Q16 | Ba trạng thái (kết luận được, bị bác, chưa đủ căn cứ) cộng từ chối khi ngoài phạm vi. LLM chỉ chuyển câu hỏi thành dữ kiện. Lời giải thích sinh từ cây chứng minh, LLM chỉ diễn đạt lại | Nhãn trung tính với lĩnh vực (9/2026). Bài Justifications của nhóm s(CASP) sinh lời giải thích bằng mẫu, không cần LLM | Memory 9/2026; `GhiChuDoc` mục 20 | — |
| Q17 | Khử trùng: gộp tự động bản trùng hoàn toàn; vị từ nghi đồng nghĩa chỉ cảnh báo | Gộp nhầm làm sai nghĩa luật, ví dụ `simultaneous_death` và `predeceased_or_simultaneous` | `PhepThu_DoPhuDanChieu` Phép thử 2; đề cương ND2 | Thầy yêu cầu gộp đồng nghĩa tự động như [5] |
| Q18 | Tự sửa tối đa hai vòng. Nhận bản sửa khi biên dịch được, không sinh cờ mới, số tình huống mẫu đúng không giảm. Không sửa được thì cô lập, câu hỏi phụ thuộc bị từ chối, học viên xem mục cô lập | Thầy yêu cầu "tự động chuẩn hoá hoặc gắn nhãn cô lập" (11/10). Cách làm gần với [7] | `GhiChuDoc` mục 1; đề cương ND2 | — |
| Q19 | Cập nhật: tạo phiên bản mới, giữ phiên bản cũ kèm thời điểm hết hiệu lực, chỉ trích lại điều có câu chữ đổi, kiểm lại phần liên quan. Không có toán tử nào xoá nút | Đáp ứng câu thầy "không phá vỡ cấu trúc đồ thị hiện hữu". PAPER_04 có thêm, sửa, xoá bộ ba nhưng không có "thay thế", không lan sang điều khác, không thực nghiệm | `KeHoach_ND1_CoChe` mục 5 | — |

## D. Bộ dữ liệu và đánh giá

| Mã | Quyết định | Lý do | Bằng chứng | Đổi khi |
|---|---|---|---|---|
| Q20 | Chấm theo **cặp tình huống đối chứng**. Chỉ số chính là tỷ lệ phụ thuộc đạt (cả hai tình huống đúng) | Một cơ sở tri thức không nối hai điều vẫn đúng một nửa nhờ may. Chấm theo cặp loại bỏ chuyện đó | Đề cương ND4, Tầng 1 | — |
| Q21 | **Độ sâu tính trên văn bản**, theo [9], mở rộng sang nhiều điều. Không tính trên cây chứng minh | Độ sâu trên chương trình phụ thuộc cách mã hoá: viết phẳng thì mất độ sâu | `SangLoc` mục 3 (đoạn cuối); `TraCuu_CongTrinhGanNhat` mục 3 | — |
| Q22 | **Bỏ câu ngưỡng 90% khỏi đề cương** (học viên quyết, v5) | Học viên tự bỏ | `BanGiao` mục 1 | — |
| Q23 | **Đối chứng chính là (i):** LLM đọc toàn văn và tự viết chương trình s(CASP). Bỏ đối chứng "xử lý ngoại lệ một tầng" của v3. Cả ba cách dùng chung bộ vị từ đầu vào và cùng số vòng sửa | Đối chứng một tầng là cách của mình bỏ một dòng, kết quả đúng sẵn theo cách dựng, và [7] đã làm đúng thí nghiệm đó (Bảng 9: 84,0% so với 99,3%). (i) là cách người làm nghề thử đầu tiên | `GhiChuDoc` mục 1; `SangLoc` bảng mục 3 dòng 2–3 | — |
| Q24 | **Cách (iii) = LLM nhận toàn bộ sổ khái niệm** (học viên chọn phương án A, sau 12/10, trước 17/10). Không chọn "bỏ lớp khái niệm" | Bỏ lớp khái niệm thì kết quả gần như biết trước (Horner [6] mục 5.2–5.3 đã cho thấy LLM không tự dùng lại tên), và không tách được tác dụng riêng của đồ thị khái niệm. (ii) so với (iii) đo đúng chiến lược Horner mục 5.3(i) gợi ý | `GhiChuDoc` mục 2, 12 | — |
| Q25 | Tầng 2 chỉ đo **tỷ lệ cờ đúng** của bộ quét, không đo độ phủ | Độ phủ đúng sẵn một phần: bộ quét bắt đúng những gì nó được định nghĩa để bắt | `Checklist_ThayDoi_v4.4_v4.5` mục D | — |
| Q26 | Tầng 3 so với LLM trả lời trực tiếp **có cấp sẵn điều luật**, kiểm định McNemar. Không làm luận điểm chính. Không đo "tỷ lệ câu có trích điều luật" | Có cấp điều luật để tách lỗi truy hồi khỏi lỗi suy luận. Tỷ lệ trích điều luật đúng sẵn theo cách dựng; [7] gọi là "architectural outcomes" | `SangLoc` mục 1.3 ý 6, bảng mục 3 dòng 9 | — |
| Q27 | Đánh giá cập nhật so với hai đối chứng: LLM mạnh tự sửa chương trình cũ, và LLM mạnh trả lời trực tiếp trên toàn văn đã sửa. Chỉ số: tỷ lệ cặp bị ảnh hưởng được trả lời đúng | Học viên muốn cơ chế cập nhật thực nghiệm được (quyết định D5a) | `BaoCao_RutGon` mục 6 | — |
| Q28 | Văn bản sửa đổi để đánh giá do người hỗ trợ soạn và giữ kín. Hai văn bản tự soạn chỉ dùng khi phát triển | Giảm thiên vị khi chính người làm hệ thống viết đề thi | `BanGiao` mục 3 (A4) | — |
| Q29 | Bỏ mã hoá thủ công và phép so thời gian (từ v4.3) | Tốn 30–40 giờ. Một người làm thì chỉ là thăm dò | `SangLoc` mục 5 | — |

**Về Q22, lập trường của Claude (giữ nguyên từ 11/10):** đề cương không cần câu ngưỡng. Nhưng trước khi chạy Tầng 1, nên ghi ngưỡng bác bỏ vào một file có ngày trong project. Ví dụ: nếu (i) đạt từ 90% phụ thuộc trên toàn tập kiểm tra thì kết luận chính là "với LLM mạnh, không cần quy trình". Không có ngưỡng ghi trước thì kết quả nào cũng dễ bị đọc theo hướng có lợi. Việc này mất khoảng 10 phút.
Điều gì sẽ chứng minh đề xuất này sai: thầy hoặc hội đồng không quan tâm tới ngưỡng ghi trước, hoặc Tầng 1 cho kết quả cách xa mọi ngưỡng hợp lý nên ngưỡng không đổi cách đọc.

## E. Đề cương và trích dẫn

| Mã | Quyết định | Lý do | Bằng chứng | Đổi khi |
|---|---|---|---|---|
| Q30 | Chỉ trích bài đã xuất bản chính thức. Không chắc thì không trích. v5 còn 9 tài liệu | Thầy dặn 11/10. Học viên chọn 12/10 | `Checklist_ThayDoi_v4.4_v4.5` mục A | — |
| Q31 | Bỏ khỏi tài liệu tham khảo: Catala, Justifications, Alviano (từ v4.4); Witt, Logic-LM (câu dùng chúng bị cắt khi rút gọn); Sójka / DACL (chỉ đọc được bản arXiv). Không trích PAPER_04 (chưa xuất bản) | Như Q30 | `Checklist_ThayDoi_v4.4_v4.5` mục C | PAPER_04 được xuất bản |
| Q32 | Bỏ số liệu khảo sát 2,5% và phép thử Gemini khỏi đề cương (12/10) | Học viên chọn | `Checklist_ThayDoi_v4.4_v4.5` mục A | — |
| Q33 | Hình thức: tối đa 6 trang nội dung cộng kế hoạch; 3 mục tiêu; 5 nội dung, mỗi nội dung ghi mục tiêu; "Điểm mới" là một đoạn trong Giới thiệu; Gantt 6 dòng | Quy định của trường và đề cương mẫu | `BaoCao_RutGon` mục 1 | — |
| Q34 | Đề cương phải đọc như người viết: câu ngắn, mỗi câu một ý, ít dấu ";", dùng từ của v3, không tự bình luận. Phần chi tiết kỹ thuật để trong các file .md | Thầy nhận xét bản cũ có giọng máy | `BaoCao_RutGon` mục 2; memory 10/2026 | — |
| Q35 | Tên đề tài **chưa chốt**. Tên đang đề xuất nằm trong `BanGiao` mục 1 | — | — | Học viên hoặc thầy chốt |

## F. Cách làm việc

| Mã | Quyết định | Lý do | Bằng chứng |
|---|---|---|---|
| Q36 | Học viên tự viết code. Claude hướng dẫn từng bước và review, không viết thay trừ khi được nhờ (17/10) | Học viên muốn thật sự hiểu và làm chủ luận văn | `BanGiao` mục 0 |
| Q37 | Dừng vòng thử pilot và nhờ LLM ngoài phản biện lặp lại (11/10) | Kéo luận văn xa kế hoạch và sinh thêm việc | Memory 11/10 |
| Q38 | Mọi trao đổi theo 8 nguyên tắc phản biện trong hướng dẫn của project | Đề cương v3 hỏng vì các lỗi liệt kê trong hướng dẫn | Hướng dẫn project |

## G. Việc còn mở

| # | Việc | Ai | Vì sao quan trọng |
|---|---|---|---|
| 1 | Hỏi thầy: có phải quét xung đột cấu trúc ngay trên lớp văn bản, khi chưa có quy tắc, không? | Học viên hỏi thầy | Nếu có, thứ tự làm ở Q5 đổi, và phải định nghĩa "chế tài", "điều kiện phân tách" trên đơn vị văn bản |
| 2 | Người hỗ trợ là ai? v5 viết "học viên hỗ trợ", tài liệu cũ viết "sinh viên hỗ trợ" | Học viên xác nhận | Người này làm tập kiểm tra, bộ quan hệ chuẩn và văn bản sửa đổi giả định. Chưa có người thì bộ dữ liệu trễ đầu tiên |
| 3 | Tải văn bản Bộ luật Dân sự 2015 Phần thứ tư (Điều 609–662) từ nguồn chính thức vào chat | Học viên | Cần cho bước A1. Môi trường của Claude không tải được trang web |
| 4 | Đối chiếu số điều và câu chữ các Điều 611, 613, 621, 626, 630, 644, 650, 651 với văn bản gốc | Học viên và Claude, sau việc 3 | Các ví dụ trong đề cương và file giải thích dựa trên diễn giải |
| 5 | Đọc toàn văn Law to Code (poster workshop ICML 2026, OpenReview, cần đăng nhập) | Học viên tải, Claude đọc | Rủi ro lớn nhất cho điểm mới 1 và 2 |
| 6 | Mở trang ACM theo DOI của NormBench [9] để chắc bài đã được đăng | Học viên | Quy tắc chỉ trích bài đã xuất bản. Một ghi chú cũ đọc qua web chỉ thấy bản arXiv |
| 7 | Câu chữ v5 nên sửa ở bản sau: [3] "kém chính xác nhất" → "thuộc nhóm kém chính xác nhất". Bản tạp chí có nhãn `#refines` còn thấp hơn (F1 = 0,032) | Học viên | `GhiChuDoc` mục 17 |
| 8 | Hỏi người có chuyên môn luật (nếu có): phạm vi khoản 2 Điều 621 (Q14); ngoại lệ "từ chối để trốn nghĩa vụ" ở Điều 620 có lan sang khoản 2 Điều 644 không; khoản 3 Điều 651 có tính là ngoại lệ không; bảng chuỗi C1–C11 có đúng không | Học viên hỏi thầy về nguồn | `SangLoc` mục 2.3, 8 |
| 9 | Chốt khi cài đặt: (a) chương trình cũ đưa cho LLM ở đánh giá cập nhật là của cách nào (đề xuất: của (ii)); (b) cách ghi dữ kiện phủ định tường minh ("chắc chắn không có tên trong di chúc"); (c) ngưỡng bác bỏ ghi trước cho Tầng 1 | Học viên và Claude | `GiaiThich_KhaiNiem` mục 9, 10; Q22 |
| 10 | ~~Phép thử s(CASP): chạy đoạn mã ở `GiaiThich_KhaiNiem` mục 8.3 với bốn ca, thêm một vòng chặn chẵn và một vòng lẻ~~ **Đã làm 20/10** (Claude chạy trên s(CASP) 1.1.4). Bốn ca ra đúng trạng thái. Vòng chẵn cho "có" với cả hai kết luận trái nhau; vòng lẻ làm mọi câu hỏi "không có mô hình". Bộ quét vòng chặn là bắt buộc | — | Kết quả ở `GiaiThich_KhaiNiem` mục 8.3, 11.1 |
| 11 | Thầy dặn "kiểm soát tri thức" (11/10). Chưa rõ danh sách cơ chế cùng ngày đã đủ giải thích chữ này chưa | Học viên xác nhận | Tránh tự diễn giải lời thầy |
