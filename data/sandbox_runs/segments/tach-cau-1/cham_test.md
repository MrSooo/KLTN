# Chấm lượt 1 `tach-cau-1` trên bộ test (20 câu)

- khớp hoàn toàn: 17/20
- đúng ranh giới (bỏ qua loai, ap_cho): 17/20
- máy kiểm lỗi: 0; thiếu phản hồi: 0
- điểm cắt: độ chính xác 0.971, độ phủ 0.971
- chi phí: 130.0 VND

### BLLD_45-2019.D107.K4#1 — khớp
> Khi tổ chức làm thêm giờ theo quy định tại khoản 3 Điều này, người sử dụng lao động phải thông báo bằng văn bản cho cơ quan chuyên môn về lao động thuộc Ủy ban nhân dân cấp tỉnh.

gold: m1 "tổ chức làm thêm giờ theo quy định tại khoản 3 Điều này" · m2 "người sử dụng lao động phải thông báo bằng văn bản cho cơ quan chuyên môn về lao động thuộc Ủy ban nhân dân cấp tỉnh"

### BLLD_45-2019.D118.K1#1 — khớp
> Người sử dụng lao động phải ban hành nội quy lao động, nếu sử dụng từ 10 người lao động trở lên thì nội quy lao động phải bằng văn bản.

gold: **c1** "Người sử dụng lao động" → m1,m2 · m1 "phải ban hành nội quy lao động" · m2 "sử dụng từ 10 người lao động trở lên" · m3 "nội quy lao động phải bằng văn bản"

### BLLD_45-2019.D126.K1#1 — khớp
> Người lao động bị khiển trách sau 03 tháng hoặc bị xử lý kỷ luật kéo dài thời hạn nâng lương sau 06 tháng hoặc bị xử lý kỷ luật cách chức sau 03 năm kể từ ngày bị xử lý, nếu không tiếp tục vi phạm kỷ luật lao động thì đương nhiên được xóa kỷ luật.

gold: **c1** "Người lao động" → m1,m2,m3,m4,m5 · m1 "bị khiển trách sau 03 tháng" · m2 "bị xử lý kỷ luật kéo dài thời hạn nâng lương sau 06 tháng" · m3 "bị xử lý kỷ luật cách chức sau 03 năm kể từ ngày bị xử lý" · m4 "không tiếp tục vi phạm kỷ luật lao động" · m5 "đương nhiên được xóa kỷ luật"

### BLLD_45-2019.D143.K1#1 — khớp
> Lao động chưa thành niên là người lao động chưa đủ 18 tuổi.

gold: m1 "Lao động chưa thành niên là người lao động chưa đủ 18 tuổi"

### BLLD_45-2019.D149.K1#1 — khớp
> Khi sử dụng người lao động cao tuổi, hai bên có thể thỏa thuận giao kết nhiều lần hợp đồng lao động xác định thời hạn.

gold: m1 "sử dụng người lao động cao tuổi" · m2 "hai bên có thể thỏa thuận giao kết nhiều lần hợp đồng lao động xác định thời hạn"

### BLLD_45-2019.D162.K3#1 — khớp
> Hai bên thỏa thuận trong hợp đồng lao động về hình thức trả lương, kỳ hạn trả lương, thời giờ làm việc hằng ngày, chỗ ở.

gold: m1 "Hai bên thỏa thuận trong hợp đồng lao động về hình thức trả lương, kỳ hạn trả lương, thời giờ làm việc hằng ngày, chỗ ở"

### BLLD_45-2019.D163.K4#1 — khớp
> Bố trí chỗ ăn, ở hợp vệ sinh cho người giúp việc gia đình nếu có thỏa thuận.

gold: m1 "Bố trí chỗ ăn, ở hợp vệ sinh cho người giúp việc gia đình" · m2 "có thỏa thuận"

### BLLD_45-2019.D170.K2#1 — SAI RANH GIỚI
> Người lao động trong doanh nghiệp có quyền thành lập, gia nhập và tham gia hoạt động của tổ chức của người lao động tại doanh nghiệp theo quy định tại các điều 172, 173 và 174 của Bộ luật này.

gold: **c1** "Người lao động trong doanh nghiệp có quyền" → m1,m2,m3 · m1 "thành lập" · m2 "gia nhập" · m3 "tham gia hoạt động của" · **c2** "tổ chức của người lao động tại doanh nghiệp theo quy định tại các điều 172, 173 và 174 của Bộ luật này" → m1,m2,m3
model: **c1** "Người lao động trong doanh nghiệp có quyền" → m1,m2,m3 · m1 "thành lập" · m2 "gia nhập" · m3 "tham gia hoạt động của tổ chức của người lao động tại doanh nghiệp theo quy định tại các điều 172, 173 và 174 của Bộ luật này"

### BLLD_45-2019.D174.K1.e#1 — khớp
> Thể thức thông qua quyết định của tổ chức.

gold: m1 "Thể thức thông qua quyết định của tổ chức"

### BLLD_45-2019.D19.K1#1 — khớp
> Người lao động có thể giao kết nhiều hợp đồng lao động với nhiều người sử dụng lao động nhưng phải bảo đảm thực hiện đầy đủ các nội dung đã giao kết.

gold: **c1** "Người lao động" → m1,m2 · m1 "có thể giao kết nhiều hợp đồng lao động với nhiều người sử dụng lao động" · m2 "phải bảo đảm thực hiện đầy đủ các nội dung đã giao kết"

### BLLD_45-2019.D203.K2.a#1 — khớp
> Rút quyết định đình công nếu chưa đình công hoặc chấm dứt đình công nếu đang đình công;

gold: m1 "Rút quyết định đình công" · m2 "chưa đình công" · m3 "chấm dứt đình công" · m4 "đang đình công"

### BLLD_45-2019.D209.K1#1 — khớp
> Không được đình công ở nơi sử dụng lao động mà việc đình công có thể đe dọa đến quốc phòng, an ninh, trật tự công cộng, sức khỏe của con người.

gold: m1 "Không được đình công ở nơi sử dụng lao động mà việc đình công có thể đe dọa đến quốc phòng, an ninh, trật tự công cộng, sức khỏe của con người"

### BLLD_45-2019.D30.K1#1 — khớp
> Các trường hợp tạm hoãn thực hiện hợp đồng lao động bao gồm:

gold: m1 "Các trường hợp tạm hoãn thực hiện hợp đồng lao động bao gồm"

### BLLD_45-2019.D33.K1#1 — khớp
> Trong quá trình thực hiện hợp đồng lao động, nếu bên nào có yêu cầu sửa đổi, bổ sung nội dung hợp đồng lao động thì phải báo cho bên kia biết trước ít nhất 03 ngày làm việc về nội dung cần sửa đổi, bổ sung.

gold: **c1** "Trong quá trình thực hiện hợp đồng lao động" → m1,m2 · **c2** "bên nào" → m1,m2 · m1 "có yêu cầu sửa đổi, bổ sung nội dung hợp đồng lao động" · m2 "phải báo cho bên kia biết trước ít nhất 03 ngày làm việc về nội dung cần sửa đổi, bổ sung"

### BLLD_45-2019.D59.K1#1 — SAI RANH GIỚI
> Người lao động được tự do lựa chọn đào tạo nghề nghiệp, tham gia đánh giá, công nhận kỹ năng nghề quốc gia, phát triển năng lực nghề nghiệp phù hợp với nhu cầu việc làm và khả năng của mình.

gold: **c1** "Người lao động được tự do lựa chọn" → m1,m2,m3 · m1 "đào tạo nghề nghiệp" · m2 "tham gia đánh giá, công nhận kỹ năng nghề quốc gia" · m3 "phát triển năng lực nghề nghiệp phù hợp với nhu cầu việc làm và khả năng của mình"
model: **c1** "Người lao động được tự do" → m1,m2,m3,m4 · m1 "lựa chọn đào tạo nghề nghiệp" · m2 "tham gia đánh giá" · m3 "công nhận kỹ năng nghề quốc gia" · m4 "phát triển năng lực nghề nghiệp phù hợp với nhu cầu việc làm và khả năng của mình"

### BLLD_45-2019.D6.K1.b#1 — khớp
> Thành lập, gia nhập, hoạt động trong tổ chức đại diện người sử dụng lao động, tổ chức nghề nghiệp và tổ chức khác theo quy định của pháp luật;

gold: m1 "Thành lập" · m2 "gia nhập" · m3 "hoạt động trong" · **c1** "tổ chức đại diện người sử dụng lao động, tổ chức nghề nghiệp và tổ chức khác theo quy định của pháp luật" → m1,m2,m3

### BLLD_45-2019.D61.K5#1 — khớp
> Trong thời gian học nghề, tập nghề, nếu người học nghề, người tập nghề trực tiếp hoặc tham gia lao động thì được người sử dụng lao động trả lương theo mức do hai bên thỏa thuận.

gold: **c1** "Trong thời gian học nghề, tập nghề" → m1,m2 · **c2** "người học nghề, người tập nghề" → m1,m2 · m1 "trực tiếp hoặc tham gia lao động" · m2 "được người sử dụng lao động trả lương theo mức do hai bên thỏa thuận"

### BLLD_45-2019.D79.K1#1 — khớp
> Người sử dụng lao động, người lao động, bao gồm cả người lao động vào làm việc sau ngày thỏa ước lao động tập thể có hiệu lực, có nghĩa vụ thực hiện đầy đủ thỏa ước lao động tập thể đang có hiệu lực.

gold: m1 "Người sử dụng lao động, người lao động, bao gồm cả người lao động vào làm việc sau ngày thỏa ước lao động tập thể có hiệu lực, có nghĩa vụ thực hiện đầy đủ thỏa ước lao động tập thể đang có hiệu lực"

### BLLD_45-2019.D97.K3#1 — SAI RANH GIỚI
> Người lao động hưởng lương theo sản phẩm, theo khoán được trả lương theo thỏa thuận của hai bên; nếu công việc phải làm trong nhiều tháng thì hằng tháng được tạm ứng tiền lương theo khối lượng công việc đã làm trong tháng.

gold: **c1** "Người lao động" → m1,m2,m4 · m1 "hưởng lương theo sản phẩm, theo khoán" · m2 "được trả lương theo thỏa thuận của hai bên" · m3 "công việc phải làm trong nhiều tháng" · m4 "hằng tháng được tạm ứng tiền lương theo khối lượng công việc đã làm trong tháng"
model: **c1** "Người lao động hưởng lương theo sản phẩm, theo khoán" → m1,m3 · m1 "được trả lương theo thỏa thuận của hai bên" · m2 "công việc phải làm trong nhiều tháng" · m3 "hằng tháng được tạm ứng tiền lương theo khối lượng công việc đã làm trong tháng"

### BLLD_45-2019.D98.K3#1 — khớp
> Người lao động làm thêm giờ vào ban đêm thì ngoài việc trả lương theo quy định tại khoản 1 và khoản 2 Điều này, người lao động còn được trả thêm 20% tiền lương tính theo đơn giá tiền lương hoặc tiền lương theo công việc làm vào ban ngày của ngày làm việc bình thường hoặc của ngày nghỉ hằng tuần hoặc của ngày nghỉ lễ, tết.

gold: m1 "Người lao động làm thêm giờ vào ban đêm" · m2 "ngoài việc trả lương theo quy định tại khoản 1 và khoản 2 Điều này, người lao động còn được trả thêm 20% tiền lương tính theo đơn giá tiền lương hoặc tiền lương theo công việc làm vào ban ngày của ngày làm việc bình thường hoặc của ngày nghỉ hằng tuần hoặc của ngày nghỉ lễ, tết"
