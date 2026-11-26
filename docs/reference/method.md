# Phương pháp (mục 3.1 đến 3.6, bản tiếng Việt)

Đây là văn bản mục Phương pháp của bài báo cáo đồ án: mô hình cơ sở tri thức K, thuật toán cập nhật theo ngày hiệu lực, tầng tri thức và hỏi đáp theo ngày. Nó mô tả hệ thống **hoàn chỉnh**; phần đã có mã nguồn xem `docs/status.md` và `docs/roadmap.md`. Hai chỗ nội dung cần xác minh thêm: số bước lan truyền của N(·) ở 3.4, và trích dẫn s(CASP) ở 3.5.

---

## 3. Phương pháp

### 3.1. Bài toán và mô hình cơ sở tri thức (Problem Formulation and Knowledge Base Model)

Đầu vào là một văn bản luật gốc và một chuỗi văn bản dưới luật, mỗi văn bản có ngày ban hành và ngày có hiệu lực. Đầu ra là cơ sở tri thức (KB) trả lời câu hỏi có/không theo ngày sự việc τ (hoặc ngày hỏi nếu câu hỏi không nêu), kèm căn cứ. Hệ thống phải chỉ cập nhật phần bị ảnh hưởng khi nạp văn bản mới, và không có người duyệt.

Chẳng hạn, một chuyên gia nước ngoài làm việc tổng cộng 45 ngày trong năm phải có giấy phép lao động nếu làm việc ngày 01/06/2025, nhưng được miễn nếu làm việc ngày 01/10/2025, vì Nghị định 219/2025 (hiệu lực từ 07/08/2025) đã thay Nghị định 152/2020 ở nội dung này, giả sử không thuộc trường hợp miễn nào khác.

Một văn bản là d = (id, issuer, level, t_iss, t_eff): số hiệu, cơ quan ban hành, cấp văn bản theo thứ bậc hiệu lực, ngày ban hành và ngày có hiệu lực. Văn bản gồm các đơn vị u (Điều, Khoản, Điểm hoặc dòng phụ lục) có quan hệ cha–con. Một phiên bản của u là v = (u, text, [t_from, t_to), state), với text là chữ của u, [t_from, t_to) là khoảng hiệu lực nửa mở (t_to có thể là +∞) và state ∈ {normal, pending, suspended} là trạng thái bình thường, chờ điều kiện kích hoạt hoặc bị tạm ngưng. Khi state = normal, tình trạng hiệu lực σ_v(τ) tại ngày τ là not_yet nếu τ < t_from, in_force nếu t_from ≤ τ < t_to và expired nếu τ ≥ t_to; ngược lại σ_v(τ) = state.

KB là K = (D, U, V, E, Δ, P, R): tập văn bản, tập đơn vị, tập phiên bản, tập quan hệ có kiểu, tập điều khoản giao chi tiết, sổ vị từ và tập quy tắc. Mỗi quan hệ trong E là (s, p, o), với s là đơn vị hoặc văn bản nguồn, o là đích và p là loại. Δ ⊆ U gồm các đơn vị của luật giao cho cơ quan cấp dưới quy định chi tiết. P là tập vị từ dùng chung để viết quy tắc (mục 3.5). Mỗi quy tắc r ∈ R được viết bằng vị từ của P và gắn với đúng một phiên bản nguồn src(r) ∈ V. Mỗi văn bản d được nạp là một sự kiện, xử lý theo thứ tự t*eff, và K′ = Update(K, d). Tập phiên bản có hiệu lực tại τ là V*τ = {v ∈ V : σ*v(τ) = in_force}, và chương trình tại ngày τ là Π*τ = {r ∈ R : src(r) ∈ V*τ, r không bị cô lập (mục 3.2)}. Câu trả lời cho ngày sự việc τ chỉ dựa trên Π*τ.

### 3.2. Tổng quan hệ thống (Pipeline Overview)

Hệ thống gồm tầng cấu trúc, bộ máy cập nhật, tầng tri thức và phần hỏi đáp, trình bày ở mục 3.3 đến 3.6 và Hình 1.

Hai nguyên tắc thiết kế chi phối hệ thống. Đầu ra của mô hình ngôn ngữ lớn (LLM) luôn bị ràng buộc: chọn trong tập ứng viên đóng, trích nguyên văn hoặc chỉ dùng vị từ được phép. Không có người duyệt: đầu ra của LLM được kiểm tra tự động, và đầu ra không qua kiểm tra lùi về giá trị mặc định an toàn hoặc bị gắn nhãn cô lập (isolated), nghĩa là được lưu nhưng không dùng làm căn cứ khi trả lời.

_Hình 1. Kiến trúc hệ thống. Màu phân biệt thành phần tất định với thành phần dùng LLM; mỗi đầu ra của LLM đi qua một cổng kiểm tra tự động. Đường phản hồi từ bộ máy cập nhật về tầng tri thức chỉ gồm tập đơn vị bị ảnh hưởng._

### 3.3. Tầng cấu trúc (Structural Layer)

Tầng cấu trúc biến mỗi văn bản được nạp thành đồ thị gồm các đơn vị và các quan hệ trong E. Chỉ hai bước dùng LLM: nối điều khoản giao chi tiết và gán loại Điều.

Văn bản được tách theo phân cấp Chương – Mục – Điều – Khoản – Điểm; mỗi đơn vị có mã theo vị trí, và số thứ tự phải liên tục, nếu bị đứt thì văn bản bị từ chối thay vì được đoán. Mỗi cụm dẫn chiếu có đúng một kết cục: nối thành quan hệ (s, refers_to, o), lưu thành quan hệ chờ đích nếu văn bản đích chưa có trong KB, hoặc ghi là không giải được kèm lý do.

Văn bản dưới luật chỉ dùng được khi biết nó hướng dẫn điều nào của luật. Hệ thống nhận diện Δ qua các dạng câu giao quyền như "do Chính phủ quy định" và nối văn bản dưới luật vào luật bằng hai loại quan hệ: based_on, tới văn bản hoặc điều khoản nêu ở phần căn cứ ban hành, và details, tới điều, khoản mà điều phạm vi điều chỉnh nêu là được giao. Nếu văn bản không nêu, LLM chọn một điều khoản trong Δ và không được đề xuất đích khác; quan hệ details sinh ra trỏ tới Điều chứa điều khoản đó. Quan hệ chỉ được giữ khi một lượt chạy độc lập thứ hai, bằng mô hình khác, chọn cùng Điều và từ khoá của phạm vi điều chỉnh xuất hiện trong Điều đó; nếu không, quan hệ bị cô lập.

Mỗi Điều được gán một loại: nội dung, định nghĩa, hiệu lực – chuyển tiếp, thủ tục hoặc thẩm quyền. Loại được gán theo mẫu tiêu đề, phần còn lại do LLM chọn; nhãn khiến một Điều không được trích quy tắc cần mô hình thứ hai xác nhận, vì nhãn sai làm mất quy tắc. Mệnh đề chứa cụm như "trừ trường hợp quy định tại" kèm dẫn chiếu giải được sinh quan hệ (s, exception_of, o), với s là đơn vị nêu ngoại lệ và o là đơn vị chứa quy tắc bị ngoại trừ.

### 3.4. Bộ máy cập nhật (Update Engine)

Một văn bản mới tác động lên KB qua các câu chỉ thị, chỉ được tìm trong các Điều hiệu lực – chuyển tiếp và trong văn bản sửa đổi. Mỗi câu được phân tích bằng mẫu tất định thành (động từ, tập đích, nội dung) và xếp vào một loại thao tác trong Bảng 1. Câu không khớp mẫu được LLM đề xuất một loại trong tập đã định nghĩa; câu vẫn không xếp được bị đánh dấu chưa xác định và các đơn vị bị chạm bị cô lập.

Chỉ thị làm mất hiệu lực hoặc đổi một đơn vị không xoá nó: hệ thống đóng phiên bản hiện hành tại ngày chỉ thị nêu, mặc định là ngày hiệu lực của văn bản mới, và mở phiên bản mới nếu có nội dung thay thế. Khi văn bản mới tuyên một nội dung của văn bản cũ hết hiệu lực mà không nêu số Điều, hệ thống đóng các Chương của văn bản cũ có tiêu đề khớp chủ đề đó; Chương có tiêu đề chung chuyển sang suspended vì chưa xác định được phạm vi. Trong ví dụ ở mục 3.1, cơ chế này đóng phần lao động nước ngoài của Nghị định 152/2020 từ 07/08/2025.

Để tránh xử lý lại toàn bộ KB, hệ thống tính tập ảnh hưởng A(d) = T(d) ∪ N(T(d)), với T(d) là các đơn vị bị chạm bởi chỉ thị của d và N(S) là các đơn vị nối với tập S bằng quan hệ details, refers*to, exception_of hoặc qua một concept (mục 3.5), trong phạm vi [CẦN XÁC MINH: số bước lan truyền]. Chế độ dựng lại toàn bộ dùng làm đối chứng: hai chế độ phải cho cùng Π*τ tại cùng ngày τ.

**Bảng 1.** Các nhóm thao tác cập nhật.

| Nhóm thao tác                                         | Mẫu chỉ thị                                          | Hệ quả lên phiên bản và trạng thái                                       |
| ----------------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------ |
| Sửa đổi, bổ sung, thay cụm từ                         | "Sửa đổi, bổ sung … như sau", "Thay cụm từ …"        | đóng phiên bản cũ, mở phiên bản mới                                      |
| Bãi bỏ, thay thế cả văn bản                           | câu nêu văn bản hoặc đơn vị hết hiệu lực từ một ngày | t_to bằng ngày đó; mọi phiên bản của đối tượng bị đóng                   |
| Hết hiệu lực theo chủ đề                              | câu nêu một nội dung hết hiệu lực, không nêu số Điều | đóng Chương khớp chủ đề; Chương chung chuyển suspended                   |
| Hiệu lực có điều kiện                                 | câu nêu sự kiện làm điều kiện hiệu lực               | pending cho tới khi điều kiện được kích hoạt                             |
| Hiệu lực có thời hạn, áp dụng thay                    | câu nêu áp dụng thay một quy định đến một ngày       | khoảng hiệu lực giới hạn; quan hệ overrides chỉ có tác dụng trong khoảng |
| Quy định chuyển tiếp                                  | câu nêu tiếp tục áp dụng quy định cũ                 | giữ thành đơn vị                                                         |
| Bổ sung danh mục                                      | câu bổ sung dòng vào danh mục                        | thêm dòng; dòng cũ giữ nguyên                                            |
| Văn bản dưới luật lấp Δ                               | điều phạm vi điều chỉnh                              | quan hệ details                                                          |
| Các loại khác (hồi tố, tạm ngưng, đính chính, đổi số) |                                                      | mô tả theo từng loại ở phụ lục                                           |

**Thuật toán 1.** Cập nhật khi nạp văn bản d.

```
Input:  K, d
Output: K'
1   parse d; resolve references; link Δ; type articles; extract exceptions
2   for each directive q in the effect/transition articles of d:
3       op ← classify(q)            // pattern; else LLM over fixed types; else isolate
4       apply op to the versions at t_eff(d)
5   activate pending conditions matched by d; relink pending links
6   A ← T(d) ∪ N(T(d))
7   re-extract concepts, implicit exceptions, rules for A
8   scan; repair at most 2 rounds; isolate failures
9   return K'
```

### 3.5. Tầng tri thức (Knowledge Layer)

Tầng tri thức biến chữ của mỗi phiên bản của Điều nội dung và Điều định nghĩa thành quy tắc suy luận trong R. Sổ vị từ P nối quy tắc của các đơn vị khác nhau. LLM gạch từ mỗi đơn vị các cụm chủ thể, điều kiện, ngoại lệ và kết luận; cụm không phải chuỗi con nguyên văn của đơn vị bị loại, và một lượt trích độc lập bằng mô hình khác kiểm lại. Vị từ X ∈ P là concept nếu có đơn vị nêu khi nào X đúng, và là input (dữ kiện do người hỏi nêu) nếu không. Hai đơn vị nối với nhau qua một concept nếu cùng dùng concept đó hoặc một đơn vị định nghĩa concept mà đơn vị kia dùng. Hai đơn vị cùng dùng một concept là cặp ứng viên ngoại lệ ngầm: LLM đề xuất quan hệ exception_of giữa chúng kèm câu bằng chứng nguyên văn, hoặc kết luận không có quan hệ.

LLM viết quy tắc s(CASP) cho từng phiên bản đơn vị [CẦN XÁC MINH: trích dẫn s(CASP)], chỉ dùng vị từ của P thuộc chính đơn vị và các đơn vị nối với nó qua một concept; Π_τ chọn các quy tắc đó theo ngày τ. Quy tắc của đơn vị nêu ngoại lệ chặn quy tắc của đơn vị gốc theo quan hệ exception_of. Với cặp quy tắc có kết luận ngược nhau mà không có quan hệ này, thứ tự ưu tiên theo Điều 58 Luật 64/2025/QH15: văn bản có hiệu lực pháp lý cao hơn thắng (khoản 3); cùng cơ quan thì văn bản ban hành sau thắng, so theo ngày ban hành (khoản 4); quy tắc áp dụng riêng do chính văn bản đặt được ghi vào cấu hình (khoản 6). Mâu thuẫn còn lại bị cô lập.

LLM sửa quy tắc lỗi do bộ quét phát hiện, tối đa hai vòng; bản sửa chỉ được nhận khi biên dịch được và không sinh lỗi mới, nếu không thì quy tắc bị cô lập.

### 3.6. Hỏi đáp theo ngày (Date-Aware Question Answering)

Phần hỏi đáp trả lời theo ngày τ (mục 3.1) và chỉ dùng Π_τ. LLM chuyển câu hỏi thành các vị từ input; câu hỏi không biểu diễn được thì được xếp ngoài phạm vi. Hệ thống chạy suy luận với mệnh đề φ và với ¬φ, và trả một trong bốn kết quả: φ được chứng minh (kết luận được); ¬φ được chứng minh (bị bác); không bên nào được chứng minh (chưa đủ căn cứ); hoặc câu hỏi phụ thuộc vào một quy tắc hay quan hệ bị cô lập (không trả lời). Với ví dụ ở mục 3.1 và φ là "phải có giấy phép lao động", τ = 01/06/2025 cho kết quả kết luận được, còn τ = 01/10/2025 cho kết quả bị bác.
