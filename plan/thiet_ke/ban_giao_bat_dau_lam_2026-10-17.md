# Bàn giao: bắt đầu làm phần cơ sở tri thức (17/10/2026, cập nhật 20/10)

File này để hội thoại mới đọc rồi làm tiếp. Mọi nguyên tắc phản biện trong hướng dẫn của project KLTN vẫn áp dụng.

**Cập nhật 20/10:** đề cương hiện hành là `claude/DeCuong_v5.md`. Đọc `claude/BanDo_TaiLieu.md` trước để biết file nào còn dùng. Giải thích khái niệm ở `claude/GiaiThich_KhaiNiem.md`, lý do các lựa chọn và việc còn mở ở `claude/SoQuyetDinh.md`.

## 0. Cách làm đã chốt

- **Học viên tự viết code. Claude hướng dẫn từng bước và review code.** Claude không viết thay toàn bộ, trừ khi được nhờ.
- Thời gian của học viên: khoảng 1 giờ mỗi ngày thường, 4–8 giờ mỗi ngày cuối tuần.
- Công cụ đề xuất: Python 3, `re`, `networkx`. Bộ ba lưu ở CSV hoặc JSONL, không cần cơ sở dữ liệu đồ thị.
- Tên kỹ thuật (mã nút, tên cạnh, JSON, mã s(CASP)) viết bằng tiếng Anh, kèm bảng đối chiếu sang tên tiếng Việt của thầy để dùng khi viết luận văn.

## 1. Trạng thái đề cương

- **Bản mới nhất là `claude/DeCuong_v5.md`**, chép từ `DRAFT_Proposal_v5.docx` mà học viên đã gửi thầy review. File `claude/DeCuong_v4.5.md` là bản cũ ngày 12/10, **không còn khớp**.
- Các quyết định từ 12/10 trở đi (chi tiết trong `claude/SoQuyetDinh.md`):
  - **Cách (iii) ở Tầng 1:** LLM nhận toàn bộ sổ khái niệm thay vì chỉ các vị từ do đồ thị khái niệm chọn. So sánh (ii) với (iii) để đo riêng tác dụng của đồ thị khái niệm.
  - **Tài liệu tham khảo còn 9 bài.** Bỏ Sójka vì chỉ đọc được bản arXiv. Quy tắc chung: không chắc thì không trích.
  - **Bỏ phép thử Gemini.** Học viên tự bỏ câu ngưỡng 90% ở Tầng 1.
  - **Giới thiệu đã rút gọn.** Các thuật ngữ kỹ thuật được giải thích ở Nội dung 1–4.
  - **Nội dung 1:** có câu "Sổ và đồ thị khái niệm là phần khung của đồ thị tri thức, được dựng trước khi trích quy tắc".
  - **Nội dung 2, đoạn 1:** đã viết lại (thêm "gắn cờ", vòng chặn, lý do chỉ cảnh báo trùng nghĩa). Đã có trong v5.
  - **Tên đề tài chưa chốt.** Claude đề xuất: "XÂY DỰNG CƠ SỞ TRI THỨC DẠNG ĐỒ THỊ CHO VĂN BẢN LUẬT TIẾNG VIỆT CÓ NGOẠI LỆ LỒNG NHAU BẰNG KẾT HỢP MÔ HÌNH NGÔN NGỮ LỚN VÀ SUY LUẬN KÝ HIỆU: THỰC NGHIỆM TRÊN CHẾ ĐỊNH THỪA KẾ".
- Hạn chốt đề cương: 5/11/2026.

## 2. Các mục thầy dặn làm trước, và lúc nào làm được

| Mục thầy dặn | Trong đề cương | Cần gì | Làm ngay được? |
|---|---|---|---|
| Định danh thực thể | Nội dung 1 | Script tách Điều / Khoản / Điểm | Có |
| chứa_khoản, thuộc_điều | Nội dung 1 | Script, sinh từ số hiệu | Có |
| dẫn_chiếu_đến | Nội dung 1 | Mẫu câu: "theo quy định tại", "khoản… Điều…", "Điều này" | Có |
| là_ngoại_lệ_của **tường minh** | Nội dung 1 | Mẫu câu ("trừ trường hợp", "không áp dụng"…) cộng LLM phân loại phản bác / vô hiệu hoá | Có |
| là_ngoại_lệ_của **ngầm** (khoản 1 Điều 621 → Điều 626) | Nội dung 1 | LLM đề xuất trên cặp ứng viên, nên có sổ khái niệm trước | Sau bước B |
| sửa_đổi_bổ_sung, thay_thế, bãi_bỏ | Nội dung 1, Nội dung 4 | Lược đồ phiên bản cộng mẫu câu văn bản sửa đổi | Có |
| Khử trùng lặp thực thể / bộ ba | Nội dung 1 (sổ khái niệm), Nội dung 2 | Lớp văn bản: kiểm mã. Lớp khái niệm: gộp tên đồng nghĩa (R4) | Phần lớn có |
| Xung đột cấu trúc ("hai chế tài đối kháng thiếu điều kiện phân tách") | Nội dung 2 | Phải có quy tắc và kết luận của chúng | Sau bước D |
| Chuẩn hoá hoặc gắn nhãn cô lập | Nội dung 2 | Bộ quét cộng vòng tự sửa | Sau bước D |

Khử trùng lặp thực thể phần lớn chính là chuẩn hoá sổ khái niệm. Ví dụ "người thừa kế" xuất hiện ở nhiều điều nhưng chỉ được là một nút.

## 3. Thứ tự làm và đầu ra từng bước

**A. Lớp văn bản và liên kết (thầy dặn làm trước)**

- **A1.** Tách 54 điều (609–662) thành đơn vị, gán mã dạng `BLDS2015.D621.K1.a`.
  - Đầu ra: file bộ ba, thống kê số Điều / Khoản / Điểm.
- **A2.** Sinh cạnh cấu trúc (`contains`, `part_of`) và `refers_to` bằng mẫu câu.
  - Đầu ra: danh sách cạnh dẫn chiếu. Đọc lại bằng mắt, vì chỉ có vài chục cạnh.
- **A3.** Tìm `exception_of` tường minh bằng mẫu câu. LLM phân loại phản bác hay vô hiệu hoá.
- **A4.** Cơ chế cập nhật:
  - mỗi đơn vị có phiên bản và thời điểm hiệu lực;
  - văn bản sửa đổi tạo phiên bản mới, nối bằng `amends` / `replaces` / `repeals`;
  - không xoá nút cũ.

  Thử với 2 văn bản tự soạn **chỉ để phát triển**: "Bãi bỏ khoản 2 Điều 621" và "Sửa đổi, bổ sung khoản 1 Điều 621 như sau: …". Bộ 8–10 văn bản dùng để đánh giá do người hỗ trợ soạn sau và giữ kín, không được dùng khi phát triển. (v5 gọi người này là "học viên hỗ trợ", tài liệu cũ gọi "sinh viên hỗ trợ"; chờ học viên xác nhận.)
  - Đầu ra: đồ thị trước và sau khi nạp. Phiên bản cũ còn nguyên, các cạnh cũ không đứt.
- **A5.** Kiểm tra trùng trên lớp văn bản:
  - không có mã trùng;
  - mỗi đơn vị có đúng một cha;
  - không có cạnh trùng.

Đem đi gặp thầy sớm được: kết quả A1–A5, vẽ đồ thị con quanh Điều 621 / 626, cộng phần thử "bãi bỏ khoản 2 Điều 621".

**B. Sổ khái niệm (vị từ đầu vào và khái niệm pháp lý)**

Quy tắc:
- **R1. Phân loại.** Có điều nào trong 609–662 nêu khi nào thì X đúng không?
  - Có → vị từ khái niệm, neo vào điều đó.
  - Không → vị từ đầu vào.
  - Thuật ngữ định nghĩa ở phần khác của Bộ luật Dân sự (ví dụ năng lực hành vi dân sự) coi là vị từ đầu vào. Ghi thành quy ước phạm vi.
- **R2.** Vị từ đầu vào phải là dữ kiện thô. Phép thử: nếu người hỏi nêu thẳng vị từ này thì có bỏ qua được điều luật nào không? Có → xếp sai loại.
  - Ví dụ: `convicted_of_harming(B, A)` là đầu vào. `disqualified(B)` ("không được quyền hưởng di sản") là khái niệm, không được là đầu vào.
- **R3.** Quét theo từng đơn vị. Chép mọi cụm điều kiện và chủ thể (sau "nếu", "khi", "trường hợp", "trừ", "người… mà…"), mỗi cụm gán một vị từ. Bảng gồm các cột: mã đơn vị, cụm chữ nguyên văn, vị từ, loại.
- **R4.** Một khái niệm một tên. Tham số đặt theo vai. Cách viết khác của cùng một khái niệm ghi thành bí danh. Bí danh cũng giúp nối đồ thị khái niệm.

Ngoài ra, vị từ cần hỏi lấy từ các loại câu hỏi của bộ dữ liệu.

Kiểm tra bằng script:
- **C1.** Mỗi đơn vị có điều kiện đều có ít nhất một dòng trong bảng R3.
- **C2.** Mỗi vị từ đầu vào được dùng ít nhất một lần.
- **C3.** Không vị từ đầu vào nào trùng tên hoặc bí danh với vị từ khái niệm.
- **C4.** Một lượt LLM độc lập trích cụm điều kiện, so khác biệt với bảng.

Cách làm đề xuất: LLM nháp theo từng điều, học viên chuẩn hoá và chốt, sau đó chạy C1–C4. Được bổ sung vị từ trong giai đoạn phát triển nếu có nhật ký thay đổi. Đóng băng sổ trước khi viết tình huống cho tập kiểm tra.

**C. Ngoại lệ ngầm.** Đồ thị khái niệm sinh cặp ứng viên, LLM đề xuất, bộ quét kiểm tra.

**D. Trích quy tắc và bộ quét (Nội dung 2).** Bắt đầu với 5 điều có chuỗi ngoại lệ, rồi mới làm hết 54 điều. Quét xung đột cấu trúc, tự sửa tối đa hai vòng, không sửa được thì gắn nhãn cô lập.

## 4. Lược đồ tối thiểu

| Loại | Gồm |
|---|---|
| Nút | Đơn vị văn bản (có phiên bản và thời điểm hiệu lực), văn bản sửa đổi, khái niệm / vị từ, quy tắc |
| Cạnh lớp văn bản | contains, part_of, refers_to, exception_of, amends, replaces, repeals |
| Cạnh lớp quy tắc | extracted_from, concludes, uses, blocks, anchored_to |

Đối chiếu tên của thầy:

| Tên của thầy | Tên trong code |
|---|---|
| chứa_khoản | contains |
| thuộc_điều | part_of |
| dẫn_chiếu_đến | refers_to |
| là_ngoại_lệ_của | exception_of |
| sửa_đổi_bổ_sung | amends |
| thay_thế | replaces |
| bãi_bỏ | repeals |

## 5. Phép thử đầu tiên (khoảng 1 giờ)

Chạy A1–A4 trên 5 điều: 621, 626, 644, 650, 651. Sau đó nạp "Bãi bỏ khoản 2 Điều 621".
- Script và mẫu câu bắt gần đủ dẫn chiếu và ngoại lệ tường minh, phiên bản cũ còn nguyên → làm tiếp 54 điều.
- Không được như vậy → sửa mẫu câu trước.

Cùng 5 điều này dùng để thử bước B: làm R1–R4 bằng tay, so với bảng LLM nháp.
- LLM tìm thêm nhiều cụm (ví dụ hơn 20%) → LLM nháp, người chốt.
- LLM không thêm được gì và làm tay dưới khoảng 10 phút một điều → làm tay.

## 6. Lưu ý và việc còn mở

- **A1–A2 đúng sẵn theo cách dựng.** Đây là cơ chế bắt buộc, không đưa vào phần số liệu thực nghiệm. Phần đáng đo là ngoại lệ ngầm (C) và xung đột (D).
- **Cần hỏi thầy:** xung đột cấu trúc có phải quét ngay trên lớp văn bản, khi chưa có quy tắc không? Nếu có, phải định nghĩa nhãn "chế tài" và "điều kiện phân tách" trên đơn vị văn bản, và thứ tự ở mục 3 đổi.
- **Cần đối chiếu với văn bản luật** (các chỗ này Claude lấy từ trí nhớ):
  - tên và số các Điều 611, 613, 621, 626, 630, 644, 650, 651;
  - câu chữ "không được quyền hưởng di sản" ở Điều 621 và "không có quyền hưởng di sản" ở điểm d khoản 1 Điều 650.
- **Học viên cần chuẩn bị:** văn bản Bộ luật Dân sự 2015, Phần thứ tư (Điều 609–662), lấy từ nguồn chính thức, dạng docx hoặc html, giữ đúng định dạng số Điều / Khoản / Điểm. Môi trường của Claude không tải được trang web, nên học viên gửi file vào chat.
- Danh sách đầy đủ việc còn mở: `claude/SoQuyetDinh.md` mục G.
