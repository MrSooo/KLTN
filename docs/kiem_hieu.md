# Kiểm hiểu lớp 1.1 đến 1.5 (người dùng tự trả lời, agent chấm)

Mục đích: người dùng nắm được từng bước để tự bảo vệ trong luận (ý của người dùng ngày 11/11). Cách dùng: người dùng trả lời bằng lời của mình, ngắn cũng được. Agent chấm "đúng / thiếu / sai", giải thích chỗ sai, rồi ghi kết quả vào cột cuối. Đáp án gợi ý nằm ở `docs/pipeline_moi.md` (cột "Xem"); agent đừng đưa đáp án trước khi người dùng trả lời.

| # | Bước | Câu hỏi | Xem | Kết quả |
|---|---|---|---|---|
| 1 | 1.1 parse | Ba dòng liên tiếp trong file chữ của BLLĐ: `Điều 14. Hình thức hợp đồng lao động` / `2. Hai bên có thể giao kết hợp đồng lao động bằng lời nói ...` / `a) ...`. Máy gán mã nào cho từng dòng, và cha của hai dòng sau là ai? | Cách làm 1.1, ví dụ 1.1 | chưa trả lời |
| 2 | 1.1 parse | Vì sao khối trích dẫn “...” trong một nghị định sửa đổi (có dòng kiểu "Điều 32. ...") không được tạo thành đơn vị của nghị định đó? | Cách làm 1.1 | chưa trả lời |
| 3 | 1.1 parse | Parse kiểm những gì để biết mình cắt đúng, và khi thấy bất thường thì làm gì? | Cách làm 1.1 | chưa trả lời |
| 4 | 1.2 refs | Một cụm dẫn chiếu có đúng ba kết cục. Nêu ba kết cục, cho một ví dụ cho mỗi loại, và giải thích vì sao có loại "không giải được" thay vì để máy đoán đích. | Cách làm 1.2, ví dụ 1.2 | chưa trả lời |
| 5 | mọi cạnh | Một cạnh có các field `evidence`, `how`, `flags`. Mỗi field để làm gì? Vì sao phải có `evidence`? | Giải thích field 1.2 | chưa trả lời |
| 6 | 1.3 delegation | Câu "Thời hạn thực hiện theo quy định của Chính phủ." thuộc dạng nào (A, B, D, E hay loose)? Vì sao? | Thẻ 1.3 | chưa trả lời |
| 7 | 1.3 delegation | Vì sao câu "Bộ trưởng Bộ Lao động - Thương binh và Xã hội quy định chi tiết Điều này." ra `loose` chứ không phải dạng A? Và vì sao không sửa regex A cho khỏi sót? | Thẻ 1.3 | chưa trả lời |
| 8 | 1.3 và 1.9 | Điều 154 khoản 9 giao Chính phủ quy định nhưng chưa có nghị định nào lấp. Bị hỏi "người này có cần giấy phép không" thì KB nên trả "có", "không" hay "chưa đủ căn cứ"? Vì sao, và bước 1.3 góp gì cho việc đó? | Thẻ 1.3 (mục Vì sao) | chưa trả lời |
| 9 | 1.4 article_type | Vì sao bước loại Điều bỏ LLM? Điều không khớp mẫu nào được gắn nhãn gì, và vì sao chọn nhãn đó thay vì nhãn khác? | Cách làm 1.4, quyết định A14 | chưa trả lời |
| 10 | 1.5 exceptions | Câu "Người lao động phải báo trước, trừ trường hợp quy định tại Điều 154 của Bộ luật này." tạo ra những gì (cạnh, nút)? `s` và `o` của cạnh là gì? Điều này khác gì một điều khoản giao ở 1.3? | Cách làm 1.5, ví dụ 1.5 | chưa trả lời |
