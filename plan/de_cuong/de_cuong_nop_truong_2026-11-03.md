# Đề cương nộp trường (3/11/2026), bản chữ tái dựng

**Trạng thái:** đây là bản đã nộp cho trường để đăng ký đề tài, và là mốc tham chiếu hiện tại. Bản này chắc chắn sẽ thay đổi trong quá trình làm và qua các vòng review, sửa chữa của trường. Khi có bản sửa sau này, so với bản này để biết đã đổi gì.

**Nguồn:** học viên không tải lại file nộp. Bản này được tái dựng từ file `S01.QuiTrinh.M_u_2_De_cuong_LVThS_LeMinhThanhTu_1.docx` (ngày 1/11), cộng hai chỗ sửa theo lời học viên:
1. Chèn Bảng 2 (phương án đánh giá) sau câu dẫn ở mục 4.
2. Gộp Nội dung 5 vào Nội dung 3 (còn 4 nội dung). Dùng đoạn văn Claude đề xuất ngày 2/11.

**Chưa đối chiếu được với file nộp:**
- Ô hướng đề tài. File ngày 1/11 đánh dấu *Hướng nghiên cứu (15 TC)*, nhưng học viên cho biết đã đăng ký *hướng ứng dụng 12 TC*.
- Đoạn văn Nội dung 3 có được dùng nguyên văn hay không, và thứ tự Nội dung 3/4 có bị đảo hay không.
- Các nhận xét ngày 2/11 có được sửa trước khi nộp hay không. Các nhận xét đó gồm: hai đoạn cũ của v5 còn sót trong Giới thiệu (dùng số trích dẫn cũ), lỗi chính tả, số Bảng 1/Bảng 2 bị ngược thứ tự, và cụm *Bộ luật Dân sự 2015* ở mục Kết quả.

**Thông tin phiếu đăng ký (theo file ngày 1/11):**
- Tên tiếng Việt: XÂY DỰNG CƠ SỞ TRI THỨC PHÁP LUẬT THỪA KẾ CÓ NGOẠI LỆ LỒNG NHAU BẰNG MÔ HÌNH NGÔN NGỮ LỚN VÀ SUY LUẬN SYMBOLIC
- Tên tiếng Anh: A SYMBOLIC REASONING APPROACH TO BUILDING A KNOWLEDGE BASE FOR INHERITANCE LAW WITH NESTED EXCEPTIONS
- Ngành: Khoa học máy tính (8480101).
- CBHD: PGS.TS Nguyễn Đình Hiển.
- Thời gian: 6 tháng, từ tháng 11/2026.
- Hình 1 và Hình 2: bản SVG vẽ lại ngày 27/10, khổ 16 cm.

---

ĐỀ CƯƠNG ĐỀ TÀI LUẬN VĂN THẠC SĨ

I. Nội dung

1. Giới thiệu đề tài

Trong lĩnh vực pháp luật, việc hỏi đáp pháp luật không chỉ yêu cầu câu trả lời phải chính xác mà còn phải có căn cứ rõ ràng và có thể kiểm chứng được, vì vậy nhiều nghiên cứu gần đây kết hợp LLM với suy luận ký hiệu để tận dụng khả năng xử lý ngôn ngữ của LLM và khả năng suy luận theo quy tắc của các phương pháp ký hiệu [1]. Hướng tiếp cận này đòi hỏi phải xây dựng một cơ sở tri thức từ các quy tắc được trích xuất từ các văn bản pháp luật để làm nền tảng suy luận. Tuy nhiên, việc xây dựng một cơ sở tri thức gặp nhiều thách thức do các quy định pháp luật thường có các ngoại lệ lồng nhau, một ngoại lệ có thể loại trừ quy tắc chung nhưng bản thân ngoại lệ đó cũng có thể bị một ngoại lệ khác tác động. Vì vậy, cơ sở tri thức cần phải xác định đúng được quy tắc chịu tác động, cấp độ của từng ngoại lệ và mối quan hệ giữa chúng, đây cũng chính là bước LLM thường mắc sai sót khi nhận diện liên kết các ngoại lệ [2]. Khó khăn càng lớn khi những quy định có liên quan lại nằm ở những điều luật khác nhau và chỉ được liên kết với nhau qua các khái niệm dùng chung. Bên cạnh đó, cơ sở tri thức phải đáp ứng được việc cập nhật khi pháp luật được điều chỉnh, bổ sung hoặc bãi bỏ mà không cần phải xây dựng lại từ đầu. Nếu bỏ qua cơ sở tri thức và cho LLM trả lời trực tiếp, hệ thống khó đảm bảo được kết luận thay đổi phù hợp khi dữ kiện có thay đổi, đồng thời không có cơ chế rõ ràng để truy xuất căn cứ pháp lý cho câu trả lời.

Các nghiên cứu gần đây giải quyết từng phần của vấn đề. PROLEG [3] biễu diễn phần ngoại lệ lồng nhau nhưng cơ sở tri thức vẫn phải làm thủ công. Khi dùng LLM để tự động trích xuất quy tắc, các nghiên cứu chưa xây dựng cơ sở tri thức dùng chung, có khả năng liên kết các quy định giữa nhiều điều luật. Nghiên cứu [4] chỉ ra rằng quan hệ ngoại lệ là loại quan hệ khó trích xuất nếu xử lý văn bản theo từng đoạn. Một số nghiên cứu chỉ tập trung trích xuất tri thức cho từng tình huống [5], số khác chỉ ra rằng LLM có xu hướng đặt tên các khái niệm thiếu nhất quán [6]. Tại Việt Nam, nghiên cứu [7] đã xây dựng được đồ thị tri thức pháp luật có xử lý trùng lặp ở mức độ bộ ba và đề cập đến khả năng cập nhật của cơ sở tri thức. Tuy nhiên, hệ thống có kết hợp LLM với suy luận ký hiệu chưa xử lý được ngoại lệ của ngoại lệ [1]. Về khía cạnh đánh giá, NormBench [2] mới gắn nhãn độ sâu ngoại lệ trong phạm vi một điều khoản, với tiếng Việt thì vẫn chưa có bộ dữ liệu theo độ sâu.

Xuất phát từ những cơ sở trên, đề tài này đề xuất phương pháp tự động xây dựng cơ sở tri thức pháp luật dưới dạng đồ thị, thử nghiệm trên chế định thừa kế của Bộ luật Dân sự. Trong hệ thống đề xuất, khả năng xử lý ngôn ngữ tự nhiên của LLM sẽ được tận dụng ở các bước cần hiểu và chuyển đổi ngôn ngữ tự nhiên, trong khi s(CASP) [8] sẽ thực hiện suy luận trên các quy tắc đã được biểu diễn. Đầu vào sẽ gôm tình huống pháp lý và câu hỏi; đầu ra sẽ là kết luận cùng với chuỗi điều khoản dùng làm căn cứ suy luận (Hình 1).Các hệ hỏi đáp pháp luật Việt Nam hiện vẫn gặp khó khăn với các câu hỏi cần quan hệ ngoại lệ giữa các điều luật. Luật Việt Nam thường nêu quy định chung, rồi đến ngoại lệ, có khi cả ngoại lệ của ngoại lệ, nằm ở cùng một điều hoặc ở điều khác. Kiểu suy luận mà kết luận có thể thay đổi khi dữ kiện thay đổi được gọi là suy luận khả hủy (defeasible reasoning). Khi trả lời trực tiếp, LLM phải tự dự đoán ngoại lệ nào thắng, không bảo đảm kết luận đổi đúng khi tình huống đổi và người dùng cũng không kiểm tra được câu trả lời được suy luận dựa trên điều luật nào. Ngoài ra, khi dùng LLM để đọc luật thành cấu trúc ngoại lệ, Chen và cộng sự [9] cho thấy LLM thường nối sai ngoại lệ vào quy định khi các ngoại lệ lồng nhau.

Trong các nghiên cứu quốc tế gần đây, PROLEG [2] đã biểu diễn được ngoại lệ lồng nhau nhưng cần chuyên gia mã hoá thủ công. Singhal và Breaux [3] thì dùng LLM để tự động trích xuất quan hệ ngoại lệ theo từng đoạn văn bản, nhưng đây lại là loại quan hệ được LLM trích xuất kém chính xác nhất. Ulizko và cộng sự [7] kết hợp LLM với bộ suy luận ký hiệu, nhưng trích lại quy tắc từ đầu cho từng tình huống nên không xây dựng cơ sở tri thức dùng chung. Horner và cộng sự [6] ghi nhận LLM hay có xu hướng đặt tên mới cho cùng một khái niệm khi điều khoản nhắc tới điều khoản khác, điều này làm cho các quy tắc không nối được với nhau. Ở tiếng Việt, nghiên cứu [5] xây dựng đồ thị tri thức pháp luật có khử trùng lặp và cập nhật được khi luật thay đổi. Một nghiên cứu khác [4] thì viết ngoại lệ thành điều kiện loại trừ bên trong quy tắc gốc, nên chưa đặc tả rõ trường hợp ngoại lệ của ngoại lệ. Về khía cạnh đánh giá, NormBench [9] chia dữ liệu theo độ sâu ngoại lệ (số tầng ngoại lệ lồng nhau) nhưng chỉ trong một điều khoản. Với tiếng Việt, theo tình hình khảo sát thì vẫn chưa tìm thấy bộ dữ liệu nào đánh giá câu trả lời theo độ sâu ngoại lệ. Các nghiên cứu hiện có vẫn chưa cung cấp phương pháp tự động xây dựng cơ sở tri thức pháp luật Việt Nam có khả năng biểu diễn và liên kết các ngoại lệ lồng nhau, đồng thời cũng chưa có bộ dữ liệu tiếng Việt để đánh giá khả năng nhận diện và xử lý các ngoại lệ theo độ sâu.

Hình 1. Minh họa đầu vào và đầu ra của hệ thống.

Điểm mới và đóng góp dự kiến của đề tài nằm ở sử dụng đồ thị khái nhiệm để giới hạn và thống nhất tập vị từ khi trích xuất các quy tắc pháp luật. Bên cạnh đó, đề tài xây dựng bộ dữ liệu có nhãn độ sâu, bao gồm các chuỗi ngoại lệ liên kết với nhau qua nhiều điều luật. Ngoài ra, đề tài sẽ thực hiện đánh giá hệ thống bằng cách đối chứng với phương pháp để LLM trực tiếp sinh chương trình suy luận. Kết quả nghiên cứu hướng đến hỗ trợ xây dựng các hệ thống hỏi đáp pháp luật có khả năng suy luận và truy xuất căn cứ pháp lý.

2. Mục tiêu của đề tài

Trong luận văn này sẽ tập trung vào bài toán xây dựng cơ sở tri thức cho các quy định pháp luật có ngoại lệ lồng nhau. Từ đó, luận văn đề ra 3 mục tiêu chính:

Xây dựng cơ sở tri thức dạng đồ thị, thử nghiệm trên phần Thừa kế của Bộ luật Dân sự. Quy trình xây dựng tự động trích xuất và cập nhật quy tắc khi pháp luật có thay đổi, có cơ chế kiểm soát trùng lặp và xung đột trong cơ sở tri thức.

Xây dựng bộ dữ liệu đánh giá tiếng Việt gồm các tình huống đối chứng, có nhãn độ sâu ngoại lệ và bộ văn bản sửa đổi giả định phục vụ việc đánh giá khả năng cập nhật cơ sở tri thức.

Cài đặt hệ thống thử nghiệm và đánh giá định lượng. Tích hợp quy trình trích xuất, kiểm tra cơ sở tri thức và suy luận pháp luật; đánh giá chất lượng trích xuất, khả năng xử lý ngoại lệ và kết quả hỏi đáp so với phương pháp đối chứng.

3. Nội dung nghiên cứu của đề tài

Để đạt được những mục tiêu kể trên, đề tài sẽ được triển khai theo bốn nội dung nghiên cứu sau:

Nội dung 1: Xây dựng cơ sở tri thức dạng đồ thị và quản lý liên kết (mục tiêu 1)

Luận văn sẽ tách các văn bản pháp luật dựa theo cấu trúc Điều, Khoản, Điểm và gán mã định danh cho từng đơn vị. Các quan hệ cấu trúc được xác định từ số hiệu điều khoản và lưu dưới dạng các bộ ba, thừa kế từ cách biểu diễn đồ thị tri thức của Pham và cộng sự [7]. Đối với các quan hệ nội dung, luận văn sử dụng các mẫu câu để xác định các đoạn có khả năng chứa quan hệ. LLM sẽ được dùng để phân loại các quan hệ này thành dẫn chiếu hoặc ngoại lệ. Quan hệ ngoại lệ được chuyển thành liên kết chặn giữa các quy tắc. Luận văn sẽ phân biệt hai dạng ngoại lệ: ngoại lệ tạo ra kết luận ngược với quy định gốc và ngoại lệ chỉ loại trừ việc áp dụng quy định gốc. Với các quan hệ không được thể hiện trực tiếp trong câu chữ, luận văn sử dụng LLM đề xuất liên kết để bộ quét để kiểm tra.Luận văn xây dựng sổ khái niệm gồm hai loại vị từ: vị từ khái niệm pháp lý gắn với điều điều khoản định nghĩa khái niệm và vị từ đầu vào do học viên biên soạn. LLM chỉ được sử dụng các vị từ có trong sổ, những khải niệm chưa có vị từ tương ứng sẽ được gắn cờ để xử lý. Từ sổ khái niệm này, luận văn sẽ xây dựng đồ thị khái niệm để giới hạn tập vị từ cung cấp cho LLM khi trích xuất từng điều. Các điều luật có chung vị từ được liên kết qua node khái niệm, ngay cả khi nói giữa chúng không có quan hệ dẫn chiếu trực tiếp. Khi pháp luật có cập nhật sửa đổi, luận văn sẽ tạo phiên bản mới và ghi nhận liên kết sửa đổi. Quy trình chỉ trích xuất lại những điều có thay đổi câu chữ, các liên kết và quy tắc liên quan sẽ được kiểm tra lại ở nội dung sau.

Nội dung 2: Kiểm tra đồ thị và kiểm soát chồng chéo tri thức (mục tiêu 1)

Các quy tắc và liên kết được tạo mới hay cập nhật ở nội dung trước đều phải trải qua quá trình kiểm tra trước khi được đưa vào cơ sở tri thức. Quy trình này gồm bốn bước: quét lỗi, tự sửa, kiểm thử và chấp nhận hoặc cô lập. Bộ quét sẽ kiểm tra năm loại lỗi: quy tắc không bao giờ được kích hoạt, quy tắc trùng lặp, quan hệ bị đứt sau khi cập nhật, vòng lặp chặn lẫn nhau và cặp quy tắc mâu thuẫn không có quan hệ. Trong đó loại cặp quy tắc mâu thuẫn có kết luận trái nhau nhưng chưa có quan hệ chặn nào tương ứng với nhau, cho thấy khả năng còn thiếu một ngoại lệ. Hệ thống tự động gộp các quy tắc trùng hoàn toàn và chỉ cảnh báo đối với các vị từ có khả năng đồng nghĩa. Đối với các mục bị gắn cờ lỗi, LLM sẽ đề xuất sửa dựa trên thông báo lỗi, văn bản gốc và các vị từ liên quan với tối đa hai vòng sửa. Bản sửa chỉ được chấp nhận khi biên dịch thành công, không phát sinh lỗi mới và không làm giảm số tình huống mẫu trả lời đúng. Các lỗi không sửa được sẽ được gắn nhãn cô lập và khi có các câu hỏi liên quan đến các mục này sẽ bị hệ thống từ chối trả lời.

Nội dung 3: Áp dụng suy luận ngoại lệ nhiều tầng, hỏi đáp có giải thích và xây dựng hệ thống thử nghiệm (mục tiêu 3)

Trên cơ sở tri thức đã được kiểm tra ở Nội dung 1 và 2, luận văn áp dụng cơ chế suy luận ngoại lệ nhiều tầng. Các quan hệ chặn được xác định khi xây dựng cơ sở tri thức, nên LLM không tham gia quyết định các quan hệ này khi hỏi đáp. Một quy tắc được xem là bị chặn khi có ngoại lệ đang áp dụng và ngoại lệ đó không bị chặn bởi một ngoại lệ khác. Hệ thống kiểm tra điều kiện này lặp lại theo từng tầng, kế thừa cách xử lý ngoại lệ của PROLEG [3]. Các quy tắc và quan hệ chặn được biên dịch sang chương trình s(CASP) để thực hiện suy luận [8].

Với mỗi câu hỏi, hệ thống kiểm tra cả mệnh đề cần xác định và phủ định của mệnh đề đó. Kết quả được phân thành ba trạng thái: kết luận được, bị bác hoặc chưa đủ căn cứ. Đối với ngoại lệ chỉ loại trừ việc áp dụng quy định gốc, hệ thống tiếp tục xét các quy tắc đang bị chặn để phân biệt trường hợp bị bác với trường hợp chưa đủ căn cứ. LLM chuyển câu hỏi thành dữ kiện thông qua các vị từ trong sổ khái niệm. Câu hỏi không biểu diễn được bằng các vị từ này được xác định là ngoài phạm vi. Hệ thống lấy cây chứng minh của s(CASP) làm căn cứ tạo lời giải thích, trong đó LLM chỉ diễn đạt lại nội dung suy luận và các điều khoản liên quan. Luận văn tích hợp các thành phần trên thành hệ thống thử nghiệm có đầu vào và đầu ra như Hình 1, dùng cho các thực nghiệm tại Mục 4.

Nội dung 4: Bộ dữ liệu đánh giá (mục tiêu 2)

Luận văn xây dựng bộ dữ liệu từ các quy định thuộc chế định thừa kế, tập trung vào những trường hợp việc áp dụng một điều luật phụ thuộc vào kết quả xác định theo điều luật khác. Với mỗi quan hệ phụ thuộc, bộ dữ liệu gồm một cặp tình huống chỉ khác nhau ở dữ kiện liên quan đến điều luật được phụ thuộc. Cặp tình huống này dùng để kiểm tra khả năng xác định đúng sự thay đổi của kết luận khi dữ kiện thay đổi. Học viên và một học viên hỗ trợ thực hiện gán nhãn độc lập, không tham khảo kết quả của hệ thống, mức độ nhất quán giữa hai người được đo bằng hệ số Kappa. Luận văn sử dụng định nghĩa độ sâu ngoại lệ của Chen và cộng sự [2], đồng thời mở rộng cách gán nhãn cho các chuỗi ngoại lệ liên kết qua nhiều điều luật. Để đánh giá khả năng cập nhật, học viên hỗ trợ xây dựng các văn bản sửa đổi giả định, kèm theo những cặp tình huống có kết luận thay đổi sau khi áp dụng nội dung sửa đổi. Bộ dữ liệu bao phủ các quan hệ phụ thuộc giữa các điều trong chế định thừa kế.

4. Phương pháp thực hiện

Hệ thống được thiết kế theo hướng tách phần lõi xử lý khỏi phần phụ thuộc vào từng lĩnh vực pháp luật. Phần lõi đảm nhiệm trích xuất, kiểm tra, quản lý tri thức và suy luận; phần phụ thuộc lĩnh vực bao gồm văn bản luật, sổ khái niệm và các quy tắc tương ứng.

Kiến trúc tổng thể và mối liên hệ giữa các thành phần được trình bày trong Hình 2.

Hình 2. Kiến trúc tổng quan của hệ thống.

Luận văn xây dựng phương án đánh giá theo từng mục tiêu nghiên cứu, kết hợp đánh giá định lượng và đối chứng giữa các phương pháp. Các nội dung đánh giá, dữ liệu sử dụng và tiêu chí đo lường được tổng hợp trong Bảng 2.

[BẢNG 2 – Phương án đánh giá theo từng mục tiêu]
| Nội dung đánh giá | Dữ liệu sử dụng | Phương pháp đối chứng | Tiêu chí đo lường |
|---|---|---|---|
| Cơ sở tri thức (mục tiêu 1) | Các cặp tình huống đối chứng của bộ dữ liệu, biểu diễn bằng vị từ đầu vào | LLM đọc toàn văn chế định thừa kế và tự viết chương trình s(CASP). Quy trình của luận văn nhưng LLM nhận toàn bộ sổ khái niệm. Các phương pháp dùng chung bộ vị từ đầu vào và cùng số vòng sửa lỗi. | Tỷ lệ phụ thuộc có cả hai tình huống trong cặp được trả lời đúng (tỷ lệ phụ thuộc đạt), theo độ sâu ngoại lệ |
| Quan hệ ngoại lệ và bộ quét (mục tiêu 1) | Bộ quan hệ ngoại lệ chuẩn do học viên hỗ trợ gán trên văn bản luật; các cảnh báo của bộ quét | Đối chiếu với bộ quan hệ chuẩn | Precision, recall, F1 của quan hệ ngoại lệ; tỷ lệ cảnh báo đúng là lỗi thật |
| Khả năng cập nhật (mục tiêu 1) | Bộ văn bản sửa đổi giả định và các cặp tình huống có kết luận thay đổi sau sửa đổi | LLM mạnh nhận chương trình s(CASP) cũ cùng văn bản sửa đổi rồi tự sửa chương trình. LLM mạnh trả lời trực tiếp trên toàn văn đã sửa. | Tỷ lệ cặp tình huống bị ảnh hưởng được trả lời đúng |
| Bộ dữ liệu (mục tiêu 2) | Nhãn do học viên và học viên hỗ trợ gán độc lập | — | Hệ số Kappa giữa hai người gán nhãn |
| Toàn hệ thống (mục tiêu 3) | Cùng tập tình huống với đánh giá cơ sở tri thức, ở dạng câu hỏi tiếng Việt | LLM trả lời trực tiếp, có cấp sẵn điều luật, chọn một trong ba trạng thái | Accuracy trên ba trạng thái, từ chối trả lời tính là sai, theo độ sâu ngoại lệ; kiểm định McNemar; tỷ lệ phụ thuộc đạt để so với đánh giá cơ sở tri thức |
*Bảng 2. Phương án đánh giá theo từng mục tiêu*

5. Kết quả, sản phẩm dự kiến

Kết quả và sản phẩm dự kiến của đề tài gồm:

Cơ sở tri thức dạng đồ thị và sổ khái niệm cho phần Thừa kế của Bộ luật Dân sự 2015, cùng mã nguồn và tài liệu hướng dẫn tái lập thực nghiệm.

Bộ dữ liệu đánh giá (nhãn độ sâu ngoại lệ, cặp tình huống đối chứng, bộ văn bản sửa đổi giả định) và số liệu so sánh với cách để LLM tự viết chương trình.

Hệ thống thử nghiệm hỏi đáp tiếng Việt, trả về kết luận kèm chuỗi điều khoản được sử dụng trong suy luận.

Tài liệu tham khảo

[1] DANG, Dung V.; NGO, Hung Q.; TRAN, Dung A.; PHAM, Vuong T.; NGUYEN, Hien D. Integrating large language model with symbolic reasoning for knowledge graph-driven legal query system. In: Intelligent Information and Database Systems (ACIIDS 2026), LNAI 16530. Springer, 2026. p. 96-109. DOI: 10.1007/978-981-92-0071-9_7.

[2] CHEN, Jian; LI, Siyuan; WAN, Chucheng; YUAN, Zixuan. From statute to control flow: Span-grounded deontic trees for defeasible scope parsing. In: Proceedings of the 32nd ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD 2026). ACM, 2026. DOI: 10.1145/3770855.3817491.

[3] SATOH, Ken; ASAI, Kento; KOGAWA, Takamune; KUBOTA, Masahiro; NAKAMURA, Megumi; NISHIGAI, Yoshiaki; SHIRAKAWA, Kei; TAKANO, Chiaki. PROLEG: An implementation of the presupposed ultimate fact theory of Japanese civil code by PROLOG technology. In: New Frontiers in Artificial Intelligence (JSAI-isAI 2010), LNAI 6797. Springer, 2011. p. 153-164. DOI: 10.1007/978-3-642-25655-4_14.

[4] SINGHAL, Anmol; BREAUX, Travis. Code generation for legal metadata extraction: a decomposition-based in-context learning approach. Requirements Engineering, 2026, 31: 15. DOI: 10.1007/s00766-026-00468-7.

[5] ULIZKO, Maxim; POLEVAYA, Tatiana; TOMILOV, Ivan; GUSAROVA, Natalia; VATIAN, Aleksandra. Proof-carrying neuro-symbolic reasoning for non-monotonic legal decision support with LLMs. Big Data and Cognitive Computing, 2026, 10(9), 295. DOI: 10.3390/bdcc10090295.

[6] HORNER, Elias; MATEIS, Cristinel; GOVERNATORI, Guido; CIABATTONI, Agata. From legal texts to defeasible deontic logic via LLMs: A study in automated semantic analysis. In: Proceedings of ASAIL 2025, CEUR-WS Vol-4174. 2026. p. 83-100.

[7] PHAM, Vuong T.; DUNG, Dang V.; NGO, Hung Q.; NGUYEN, Binh; DO, Nhon V.; SELAMAT, Ali; NGUYEN, Hien D. Ontology-based knowledge graph approach for legal queries. Informatica, 2026, 37(1), p. 159-192. DOI: 10.15388/25-INFOR617.

[8] ARIAS, Joaquín; CARRO, Manuel; SALAZAR, Elmer; MARPLE, Kyle; GUPTA, Gopal. Constraint answer set programming without grounding. Theory and Practice of Logic Programming, 2018, 18(3-4), p. 337-354. DOI: 10.1017/S1471068418000285.

II. Kế hoạch thực hiện

Nội dung công việc

Tháng1

Tháng2

Tháng3

Tháng4

Tháng5

Tháng6

Khảo sát tài liệu, tách và định danh văn bản, xây dựng sổ khái niệm

Xây dựng và gán nhãn bộ dữ liệu đánh giá và bộ sửa đổi giả định

Xây dựng tự động cơ sở tri thức: trích xuất, kiểm tra đồ thị, cập nhật

Cài đặt suy luận trên s(CASP), hỏi đáp và giải thích

Thực nghiệm, đánh giá và phân tích kết quả

Viết luận văn

Bảng 1. Kế hoạch thực hiện các giai đoạn của luận văn
