# Kế hoạch hoàn thành luận văn (3/11/2026)

Trạng thái: A1–A7 (đồ thị tri thức tầng văn bản) xong. Còn lại: sổ khái niệm, ngoại lệ ngầm, quy tắc và bộ quét, hỏi đáp, bộ dữ liệu, thực nghiệm, viết.

Định nghĩa chi tiết các bước B, C, D (R1–R4, C1–C4, lược đồ) vẫn ở `ban_giao_bat_dau_lam_2026-10-17.md`. Nội dung đề cương hiện hành: `SuonDeCuong_v6_2026-11-01.md` (sườn) và `DeCuong_v5.md`. Quyết định: `so_quyet_dinh.md`.

## Mốc thời gian

- Đề cương chốt 5/11/2026. Thời gian làm luận văn 6 tháng kể từ đó, tức đến khoảng 5/5/2027.
- Thời gian học viên có: khoảng 1 giờ mỗi ngày thường, 4–8 giờ mỗi ngày cuối tuần, tức 13–21 giờ mỗi tuần, khoảng 340–550 giờ cho 26 tuần [Suy luận, tính từ số học viên ghi].
- Gantt trong đề cương: sổ khái niệm T1–T2; bộ dữ liệu T2–T3; trích xuất, kiểm tra, cập nhật T3–T4; suy luận và hỏi đáp T3–T4; thực nghiệm T3–T5; viết T5–T6.

## Bảng việc

| # | Việc | Đầu ra | Ai |
|---|---|---|---|
| **0. Đến 5/11: đề cương** | | | |
| 0.1 | Viết đề cương v6 theo sườn 1/11 | file gửi thầy | Học viên |
| 0.2 | Chốt: ý hai kiểu chặn đặt ở Giới thiệu hay Nội dung 3; tên đề tài; kiểm lại tác giả và số trang của [1] trên trang Springer | — | Học viên |
| 0.3 | Hỏi thầy: tên mục tiêu có cần chủ ngữ; in nghiêng thay ngoặc kép; [1] có giữ số hiệu; quét xung đột có làm ngay trên lớp văn bản không (SoQuyetDinh G1); "kiểm soát tri thức" có đúng là danh sách cơ chế ngày 11/10 không (G11) | câu trả lời | Học viên |
| 0.4 | Nhắn người hỗ trợ: có nhận làm tập kiểm tra, bộ quan hệ chuẩn, văn bản sửa đổi giả định không, từ khi nào (G2) | tên và thời gian | Học viên |
| **1. Đóng A** | | | |
| 1.1 | Chạy `run_all.py` ra XONG, gộp nhánh `sua-theo-review` vào `main` | `main` khớp báo cáo | Agent |
| 1.2 | Đếm cạnh xuyên điều trong đồ thị A (refers_to và exception_of giữa hai Điều khác nhau) | con số sàn cho quy mô bộ dữ liệu | Agent, khoảng 5 phút |
| 1.3 | Tự ôn A1→A7, mỗi bước ba câu: đầu vào, đầu ra và ý nghĩa một dòng, sai thì thấy gì | học viên nắm được | Học viên |
| **2. Sổ khái niệm (Nội dung 1)** | | | |
| 2.1 | Chọn LLM và hạn mức chi (API key). Mô hình dùng ở B, C, D nên là mô hình dùng cho đối chứng (i) | quyết định | Học viên |
| 2.2 | Phép thử 5 điều (621, 626, 644, 650, 651): R1–R4 làm tay, LLM nháp độc lập, so khác biệt | chốt Q12: LLM nháp hay làm tay | Học viên |
| 2.3 | Mở ra 54 điều theo cách đã chốt | bảng R3, vị từ, bí danh | Học viên chốt, LLM nháp |
| 2.4 | Chạy kiểm C1–C4 | báo cáo | Agent |
| 2.5 | Dựng đồ thị khái niệm | nút vị từ nối điều định nghĩa và điều dùng | Agent |
| 2.6 | Đóng băng sổ, ghi ngày | bản lưu có ngày | Học viên |
| **3. Bộ dữ liệu (Nội dung 4)** | | | |
| 3.1 | Liệt kê phụ thuộc giữa các điều, đọc từ văn bản, không từ khớp chuỗi và không xem kết quả hệ thống; gán độ sâu và loại cạnh | danh sách phụ thuộc | Học viên và người hỗ trợ |
| 3.2 | Viết quy ước diễn giải (khoản 2 Điều 621 và các chỗ tương tự); nhờ người có chuyên môn luật đọc (G8) | file quy ước | Học viên, thầy giới thiệu người |
| 3.3 | Viết cặp tình huống đối chứng; hai người độc lập; đo Kappa. Tập kiểm tra viết sau 2.6 | tập phát triển, tập kiểm tra | Hai người |
| 3.4 | Bộ quan hệ chuẩn cho Tầng 2 (khung chấm 11 Điều mẫu đã có; phạm vi chưa chốt) | file đáp án | Người hỗ trợ |
| 3.5 | 8–10 văn bản sửa đổi giả định, kèm cặp tình huống đổi đáp án; giữ kín | bộ kín | Người hỗ trợ |
| **4. Ngoại lệ ngầm, quy tắc, bộ quét (Nội dung 1–2)** | | | |
| 4.1 | C: cặp ứng viên từ đồ thị khái niệm, LLM đề xuất ngoại lệ ngầm và loại (phản bác hay vô hiệu hoá), bộ quét kiểm | cạnh exception_of ngầm | Agent, học viên xem mục bị gắn cờ |
| 4.2 | D: trích quy tắc, 5 điều có chuỗi ngoại lệ trước rồi 54 điều; vị từ chỉ lấy từ sổ | quy tắc gắn điều nguồn | Agent |
| 4.3 | Bộ quét năm loại lỗi, tự sửa tối đa hai vòng, cô lập | báo cáo quét | Agent |
| 4.4 | Cập nhật ở mức quy tắc: chỉ trích lại điều đổi, kiểm lại phần liên quan | đồ thị trước và sau | Agent |
| **5. Suy luận và hỏi đáp (Nội dung 3)** | | | |
| 5.1 | Biên dịch quy tắc và quan hệ chặn sang s(CASP); bộ quét vòng chặn là bắt buộc (phép thử 20/10: vòng lẻ làm mọi câu hỏi "không có mô hình") | chương trình s(CASP) | Agent |
| 5.2 | LLM chuyển câu hỏi thành dữ kiện bằng vị từ trong sổ; câu ngoài sổ là ngoài phạm vi | | Agent |
| 5.3 | Giải thích lấy từ cây chứng minh, LLM chỉ diễn đạt lại | | Agent |
| **6. Thực nghiệm (Nội dung 5)** | | | |
| 6.0 | Ghi ngưỡng bác bỏ Tầng 1 vào file có ngày, trước khi chạy (Q22) | file có ngày | Học viên và Claude, 10 phút |
| 6.1 | Tầng 1: cách (i), (ii), (iii); tỷ lệ phụ thuộc đạt theo độ sâu | số liệu | Agent |
| 6.2 | Tầng 2: P, R, F1 của quan hệ ngoại lệ; tỷ lệ cảnh báo đúng | số liệu | Agent |
| 6.3 | Tầng 3: toàn hệ thống so với LLM trả lời trực tiếp có cấp điều luật; McNemar | số liệu | Agent |
| 6.4 | Cập nhật: so với hai đối chứng. Chốt trước (G9a): chương trình cũ đưa cho LLM là của cách (ii) | số liệu | Agent |
| 6.5 | Phân tích lỗi; báo cáo cả kết quả âm | | Học viên |
| **7. Viết** | | | |
| 7.1 | Viết luận văn. Mọi nhận định về bài báo lấy từ PDF toàn văn | bản thảo | Học viên |
| 7.2 | Slide bảo vệ | | Học viên |

## Thứ tự bắt buộc

- 2.6 (đóng băng sổ) trước tập kiểm tra ở 3.3 (Q11). Tập phát triển viết trước được.
- 3.5 (văn bản sửa đổi) giữ kín, không dùng khi phát triển (Q28).
- 6.x cần 3.x và 4.x–5.x xong. 6.4 cần 3.5.
- 6.0 trước 6.1.

## Điểm nghẽn

1. **Người hỗ trợ** (G2) chưa xác nhận. Không có người này thì 3.1, 3.3–3.5 không đi được, và mọi Tầng cùng phần cập nhật đều thiếu bộ dữ liệu.
2. **Chưa biết số phụ thuộc.** Nội dung 4 của sườn v6 ghi "bao phủ mọi phụ thuộc giữa các điều". Việc 1.2 cho con số sàn trong vài phút; đếm xong mới biết bộ dữ liệu dài bao nhiêu.
3. **Đối chứng (i) có thể mạnh.** Phép thử tay ngày 7/10: Gemini và Grok trả lời đúng cả hai câu ngoại lệ lồng. Q23 đã chấp nhận (i) bằng hoặc hơn (ii) là kết quả âm báo cáo được. Ngưỡng ghi trước (6.0) để kết quả nào cũng không bị đọc theo hướng có lợi.
4. **Không có chuyên gia luật** (G8). Quy ước khoản 2 Điều 621 (Q14) lấy từ một lượt tra cứu web, thầy cũng không phải chuyên gia.
5. **Phần A chưa phải thực nghiệm.** Cấu trúc, cạnh cấu trúc và số kiểm là đúng sẵn theo cách dựng. Phần đo được là 4.1 (ngoại lệ ngầm), Tầng 1–3 và cập nhật. Độ chính xác của 39 quan hệ tường minh (25 dẫn chiếu, 14 ngoại lệ) chưa đo, chờ 3.4.

Điều gì sẽ chứng minh kế hoạch này sai: thầy trả lời rằng phải quét xung đột trên lớp văn bản ngay (G1) hoặc "kiểm soát tri thức" có nghĩa khác danh sách cơ chế ngày 11/10, khi đó giai đoạn 4 phải sắp xếp lại; hoặc người hỗ trợ không nhận, khi đó giai đoạn 3 phải thu hẹp.
