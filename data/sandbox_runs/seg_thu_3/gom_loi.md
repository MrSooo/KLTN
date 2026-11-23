# Gom lỗi lượt 1 (`seg-thu-3`) trên cả BLLĐ, 22-23/11

Chạy MỘT lần, Gemini flash qua ckey (`dungcsnd113/gemini-flash-3.8`, upstream chưa kiểm), mỗi câu một lời gọi, 4 luồng.
Nguồn: 881 đơn vị 1.6A của BLLĐ (`propositions.contexts()`), cắt thành 993 câu (dòng, hoặc sau dấu chấm có chữ hoa theo sau).
Lời nhắc: `system.txt` (5 luật, 3 ví dụ ngoài bộ khó). Script: `do_bo_kho.py`. Phản hồi thô: `phan_hoi/`. Từng câu: `bao_cao.md`.
Dựng lại báo cáo (không gọi API): `python -I -X utf8 data/sandbox_runs/seg_thu_3/do_bo_kho.py bao data/sandbox_runs/seg_thu_3/phan_hoi`.

## Số liệu
- 993/993 câu có phản hồi. 9 câu (D85.K1-K3, D86.K1, D86.K2, D86.K2.a-c, D88) lúc đầu thiếu vì tuyến model trả 404 "The model is not available" qua ba lượt chạy bù; 23/11 gọi lại cùng model, cùng lời nhắc, cả 9 có phản hồi (`logs/seg_thu_3_bu3.log`, 58,5 VND), máy kiểm qua cả 9.
- Máy kiểm (khớp nguyên văn, đúng thứ tự, chỉ bỏ dấu câu và chữ nối tập đóng, `ap_cho` đúng): qua 985/993 (99,2%). Tập chữ nối gồm "mà", "khi", "nếu", nên chữ nối bị bỏ ở khe giữa hai đoạn không bị bắt: 8 lỗi là cận dưới của E1.
- Không câu nào cụt; token ra 641.892 (trung bình khoảng 650 mỗi câu); khoảng 6.450 VND.
- Số mệnh đề mỗi câu: 1 (376 câu), 2 (313), 3 (154), 4 (63), 5 (44), 6 đến 13 (43).

## Các dạng lỗi (đếm bằng cờ máy, rồi agent đọc tay mẫu; đọc tay chưa phải gold, user chưa duyệt)

| # | Dạng | Quy mô | Ví dụ | Hướng sửa (đề xuất, chưa làm) |
|---|---|---|---|---|
| E1 | Chữ nối ngoài tập đóng bị xoá hoặc cắt dở: "sau khi", "trước khi", "để" (khi không tách mục đích), "mà" bị xoá ở giữa một đoạn | 8 câu máy kiểm bắt (0,8%), cộng ca lọt như D46.K3 ("... theo hợp đồng lao động trước" + "người lao động thôi việc") | D113.K4, D126.K2, D172.K1, D41.K1#2, D3.K9, D20.K1.a | Tập chữ nối thành tập CỤM đóng ("sau khi", "trước khi", "trong trường hợp", "trường hợp", "khi", "nếu", "do", "để") đặt trong đặc tả; máy kiểm vẫn giữ nguyên |
| E2 | Chữ đánh dấu ("Trường hợp", "Trước khi", "Do", "Bảo đảm") bị làm thành đoạn dùng chung, nhiều khi chỉ áp cho một mệnh đề | 29 câu (3%) theo đọc tay; không cờ máy nào cho đúng số này (cờ `chung_ap_mot_menh_de` = 22) | D69.K2#4, D118.K3, D36.K1.c (bản thử) | Cùng cách sửa E1: chữ đánh dấu là chữ nối, không phải đoạn |
| E3 | Không tách điều kiện hay ngoại lệ trong câu dài có một động từ chính: "trừ <không phải dẫn chiếu>", "trong trường hợp ..." giữa câu, "trên cơ sở ..." | đọc mẫu: khoảng 3 trên 48 câu đã đọc (mẫu lấy từ câu có cờ, nên tỉ lệ cả kho có thể thấp hơn) | D61.K4#2 (cả câu một mệnh đề, gồm "phải từ đủ 18 tuổi" và "trừ lĩnh vực nghệ thuật, thể dục, thể thao"), D73.K1 | Luật riêng cho "trừ", "trong trường hợp", "trên cơ sở" trong đặc tả, kèm ví dụ ngoài gold |
| E4 | Bổ ngữ phạm vi "đối với ...", "trong thời hạn ..." để trong mệnh đề | 59 câu có "đối với" trong mệnh đề | D44.K2, D118.K3 ("... đối với nơi có tổ chức đại diện người lao động tại cơ sở"), D113.K1.b | CHỜ QUYẾT: A55 cho bổ ngữ thành dòng `dieu_kien`; lượt 1 có tách thành mệnh đề, hay để lượt 2 đánh span |
| E5 | "trừ trường hợp quy định tại ..." lúc tách lúc không | trong 107 câu có chữ dẫn chiếu trong mệnh đề | D137.K1.b tách; D18.K1, D151.K1.d, D85.K1 không (D85.K2 cùng dạng câu thì tách "trừ trường hợp có khó khăn ...") | Theo A59: máy đánh dấu dẫn chiếu trước từ 1.2, cụm "trừ trường hợp quy định tại X" do máy cắt, LLM không phải quyết |

## Không phải lỗi của lượt 1 (ghi để khỏi sửa nhầm)
- Danh sách danh từ dài giữ trong một mệnh đề, kể cả nối bằng ";" (D1, D91.K3, D166, D184.K2, D16.K1): đúng luật 2. Lõi dài là việc của lượt 2 hoặc máy (đưa danh sách tân ngữ ra `liet_ke`), không phải ranh giới.
- Câu dẫn "... trong trường hợp sau đây:" giữ một mệnh đề (D107.K3, D125): đúng; câu dẫn cộng mục con là việc của lượt 2 (nhóm logic).
- Định nghĩa dạng công thức (D46.K2, D47.K2 "là tổng thời gian ... trừ đi ..."): một mệnh đề là chấp nhận được ở lượt 1; cách biểu diễn công thức là câu hỏi riêng, chưa thuộc phạm vi.
- Cờ `va_hoac_trong_menh_de` (234 câu) và `dai_tu_15_chu` (553): đọc 34 câu mẫu, phần lớn là danh sách danh từ (đúng).

## So với cách cũ
`menh-de-12` gộp nhiều việc trong một dòng (ví dụ D8.K4 5 chỗ nối, D217.K3 10). Lượt 1 tách danh sách động từ đều tay trên cả kho (D6.K2.d, D134.K2, D4.K7, D81.K2). Lỗi còn lại chủ yếu là THIẾU tách điều kiện/ngoại lệ trong câu dài (E3, E4) và chữ nối (E1, E2), không còn là gộp danh sách động từ.

## Việc kế (chưa làm)
1. ~~Chạy bù 9 câu~~ (xong 23/11). Còn để user xem: D86.K2.c tách "thương lượng", "ký kết" (tên quy trình, có thể là danh từ theo luật 2).
2. User quyết E4.
3. Viết đặc tả lượt 1 với luật cho E1-E3 và E5, rồi gold 60 câu để user duyệt; đo trên 20 câu kiểm tra chưa dùng.
