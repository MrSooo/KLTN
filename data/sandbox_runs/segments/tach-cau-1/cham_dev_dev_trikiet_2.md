# Chấm lượt 1 `tach-cau-1` trên bộ dev (40 câu), thư mục dev_trikiet_2

- khớp hoàn toàn: 34/40
- đúng ranh giới (bỏ qua loai, ap_cho): 34/40
- máy kiểm lỗi: 0; thiếu phản hồi: 2
- điểm cắt: độ chính xác 0.967, độ phủ 0.989
- chi phí: 395.2 VND

### BLLD_45-2019.D100.K1#1 — khớp
> Nơi nào sử dụng người cai thầu hoặc người có vai trò trung gian tương tự thì người sử dụng lao động là chủ chính phải có danh sách và địa chỉ của những người này kèm theo danh sách những người lao động làm việc với họ và phải bảo đảm việc họ tuân thủ quy định của pháp luật về trả lương, an toàn, vệ sinh lao động.

gold: m1 "Nơi nào sử dụng người cai thầu hoặc người có vai trò trung gian tương tự" · **c1** "người sử dụng lao động là chủ chính" → m2,m3 · m2 "phải có danh sách và địa chỉ của những người này kèm theo danh sách những người lao động làm việc với họ" · m3 "phải bảo đảm việc họ tuân thủ quy định của pháp luật về trả lương, an toàn, vệ sinh lao động"

### BLLD_45-2019.D101.K1#1 — khớp
> Người lao động được tạm ứng tiền lương theo điều kiện do hai bên thỏa thuận và không bị tính lãi.

gold: **c1** "Người lao động" → m1,m2 · m1 "được tạm ứng tiền lương theo điều kiện do hai bên thỏa thuận" · m2 "không bị tính lãi"

### BLLD_45-2019.D111.K2#1 — khớp
> Người sử dụng lao động có quyền quyết định sắp xếp ngày nghỉ hằng tuần vào ngày Chủ nhật hoặc ngày xác định khác trong tuần nhưng phải ghi vào nội quy lao động.

gold: **c1** "Người sử dụng lao động" → m1,m2 · m1 "có quyền quyết định sắp xếp ngày nghỉ hằng tuần vào ngày Chủ nhật hoặc ngày xác định khác trong tuần" · m2 "phải ghi vào nội quy lao động"

### BLLD_45-2019.D115.K2#1 — khớp
> Người lao động được nghỉ không hưởng lương 01 ngày và phải thông báo với người sử dụng lao động khi ông nội, bà nội, ông ngoại, bà ngoại, anh, chị, em ruột chết; cha hoặc mẹ kết hôn; anh, chị, em ruột kết hôn.

gold: **c1** "Người lao động" → m1,m2 · m1 "được nghỉ không hưởng lương 01 ngày" · m2 "phải thông báo với người sử dụng lao động" · m3 "ông nội, bà nội, ông ngoại, bà ngoại, anh, chị, em ruột chết" · m4 "cha hoặc mẹ kết hôn" · m5 "anh, chị, em ruột kết hôn"

### BLLD_45-2019.D119.K3#1 — SAI RANH GIỚI
> Trong thời hạn 07 ngày làm việc kể từ ngày nhận được hồ sơ đăng ký nội quy lao động, nếu nội dung nội quy lao động có quy định trái với pháp luật thì cơ quan chuyên môn về lao động thuộc Ủy ban nhân dân cấp tỉnh thông báo, hướng dẫn người sử dụng lao động sửa đổi, bổ sung và đăng ký lại.

gold: **c1** "Trong thời hạn 07 ngày làm việc kể từ ngày nhận được hồ sơ đăng ký nội quy lao động" → m2,m3 · m1 "nội dung nội quy lao động có quy định trái với pháp luật" · **c2** "cơ quan chuyên môn về lao động thuộc Ủy ban nhân dân cấp tỉnh" → m2,m3 · m2 "thông báo" · m3 "hướng dẫn" · **c3** "người sử dụng lao động sửa đổi, bổ sung và đăng ký lại" → m2,m3
model: **c1** "Trong thời hạn 07 ngày làm việc kể từ ngày nhận được hồ sơ đăng ký nội quy lao động" → m2,m3 · m1 "nội dung nội quy lao động có quy định trái với pháp luật" · **c2** "cơ quan chuyên môn về lao động thuộc Ủy ban nhân dân cấp tỉnh" → m2,m3 · m2 "thông báo" · m3 "hướng dẫn người sử dụng lao động sửa đổi, bổ sung và đăng ký lại"

### BLLD_45-2019.D122.K3#1 — khớp
> Khi một người lao động đồng thời có nhiều hành vi vi phạm kỷ luật lao động thì chỉ áp dụng hình thức kỷ luật cao nhất tương ứng với hành vi vi phạm nặng nhất.

gold: m1 "một người lao động đồng thời có nhiều hành vi vi phạm kỷ luật lao động" · m2 "chỉ áp dụng hình thức kỷ luật cao nhất tương ứng với hành vi vi phạm nặng nhất"

### BLLD_45-2019.D136.K2#1 — khớp
> Tham khảo ý kiến của lao động nữ hoặc đại diện của họ khi quyết định những vấn đề liên quan đến quyền và lợi ích của phụ nữ.

gold: m1 "Tham khảo ý kiến của lao động nữ hoặc đại diện của họ" · m2 "quyết định những vấn đề liên quan đến quyền và lợi ích của phụ nữ"

### BLLD_45-2019.D137.K2#1 — THIẾU PHẢN HỒI

### BLLD_45-2019.D139.K2#1 — khớp
> Trong thời gian nghỉ thai sản, lao động nữ được hưởng chế độ thai sản theo quy định của pháp luật về bảo hiểm xã hội.

gold: m1 "Trong thời gian nghỉ thai sản, lao động nữ được hưởng chế độ thai sản theo quy định của pháp luật về bảo hiểm xã hội"

### BLLD_45-2019.D144.K2#1 — khớp
> Người sử dụng lao động khi sử dụng lao động chưa thành niên có trách nhiệm quan tâm chăm sóc người lao động về các mặt lao động, sức khỏe, học tập trong quá trình lao động.

gold: **c1** "Người sử dụng lao động" → m1,m2 · m1 "sử dụng lao động chưa thành niên" · m2 "có trách nhiệm quan tâm chăm sóc người lao động về các mặt lao động, sức khỏe, học tập trong quá trình lao động"

### BLLD_45-2019.D145.K1#1 — khớp
> Khi sử dụng người chưa đủ 15 tuổi làm việc, người sử dụng lao động phải tuân theo quy định sau đây:

gold: m1 "sử dụng người chưa đủ 15 tuổi làm việc" · m2 "người sử dụng lao động phải tuân theo quy định sau đây"

### BLLD_45-2019.D152.K1#1 — khớp
> Doanh nghiệp, cơ quan, tổ chức, cá nhân, nhà thầu chỉ được tuyển dụng người lao động nước ngoài vào làm vị trí công việc quản lý, điều hành, chuyên gia và lao động kỹ thuật mà người lao động Việt Nam chưa đáp ứng được theo nhu cầu sản xuất, kinh doanh.

gold: m1 "Doanh nghiệp, cơ quan, tổ chức, cá nhân, nhà thầu chỉ được tuyển dụng người lao động nước ngoài vào làm vị trí công việc quản lý, điều hành, chuyên gia và lao động kỹ thuật mà người lao động Việt Nam chưa đáp ứng được theo nhu cầu sản xuất, kinh doanh"

### BLLD_45-2019.D161.K1#2 — SAI RANH GIỚI
> Các công việc trong gia đình bao gồm công việc nội trợ, quản gia, chăm sóc trẻ em, chăm sóc người bệnh, chăm sóc người già, lái xe, làm vườn và các công việc khác cho hộ gia đình nhưng không liên quan đến hoạt động thương mại.

gold: m1 "Các công việc trong gia đình bao gồm công việc nội trợ, quản gia, chăm sóc trẻ em, chăm sóc người bệnh, chăm sóc người già, lái xe, làm vườn và các công việc khác cho hộ gia đình nhưng không liên quan đến hoạt động thương mại"
model: **c1** "Các công việc trong gia đình" → m1,m2 · m1 "bao gồm công việc nội trợ, quản gia, chăm sóc trẻ em, chăm sóc người bệnh, chăm sóc người già, lái xe, làm vườn và các công việc khác cho hộ gia đình" · m2 "không liên quan đến hoạt động thương mại"

### BLLD_45-2019.D164.K2#1 — khớp
> Phải bồi thường theo thỏa thuận hoặc theo quy định của pháp luật nếu làm hỏng, mất tài sản của người sử dụng lao động.

gold: m1 "Phải bồi thường theo thỏa thuận hoặc theo quy định của pháp luật" · m2 "làm hỏng" · m3 "mất" · **c1** "tài sản của người sử dụng lao động" → m2,m3

### BLLD_45-2019.D177.K5#1 — khớp
> Các nghĩa vụ khác theo quy định của pháp luật.

gold: m1 "Các nghĩa vụ khác theo quy định của pháp luật"

### BLLD_45-2019.D178.K7#1 — khớp
> Được người sử dụng lao động bố trí nơi làm việc và được cung cấp thông tin, bảo đảm các điều kiện cần thiết cho hoạt động của tổ chức đại diện người lao động tại cơ sở.

gold: m1 "Được người sử dụng lao động bố trí nơi làm việc" · **c1** "được" → m2,m3 · m2 "cung cấp thông tin" · m3 "bảo đảm các điều kiện cần thiết cho hoạt động của tổ chức đại diện người lao động tại cơ sở"

### BLLD_45-2019.D182.K1#1 — khớp
> Trong giải quyết tranh chấp lao động, các bên có quyền sau đây:

gold: m1 "Trong giải quyết tranh chấp lao động, các bên có quyền sau đây"

### BLLD_45-2019.D186#1 — khớp
> Khi tranh chấp lao động đang được cơ quan, tổ chức, cá nhân có thẩm quyền giải quyết trong thời hạn theo quy định của Bộ luật này thì không bên nào được hành động đơn phương chống lại bên kia.

gold: m1 "tranh chấp lao động đang được cơ quan, tổ chức, cá nhân có thẩm quyền giải quyết trong thời hạn theo quy định của Bộ luật này" · m2 "không bên nào được hành động đơn phương chống lại bên kia"

### BLLD_45-2019.D193.K3#2 — khớp
> Đối với tranh chấp quy định tại điểm b và điểm c khoản 2 Điều 179 của Bộ luật này mà xác định có hành vi vi phạm pháp luật thì Ban trọng tài lao động không ra quyết định giải quyết mà lập biên bản và chuyển hồ sơ, tài liệu đến cơ quan có thẩm quyền xem xét, xử lý theo quy định của pháp luật.

gold: m1 "Đối với tranh chấp quy định tại điểm b và điểm c khoản 2 Điều 179 của Bộ luật này mà xác định có hành vi vi phạm pháp luật" · **c1** "Ban trọng tài lao động" → m2,m3,m4 · m2 "không ra quyết định giải quyết" · m3 "lập biên bản" · m4 "chuyển hồ sơ, tài liệu đến cơ quan có thẩm quyền xem xét, xử lý theo quy định của pháp luật"

### BLLD_45-2019.D194.K1#1 — khớp
> Thời hiệu yêu cầu hòa giải viên lao động thực hiện hòa giải tranh chấp lao động tập thể về quyền là 06 tháng kể từ ngày phát hiện ra hành vi mà bên tranh chấp cho rằng quyền hợp pháp của mình bị vi phạm.

gold: m1 "Thời hiệu yêu cầu hòa giải viên lao động thực hiện hòa giải tranh chấp lao động tập thể về quyền là 06 tháng kể từ ngày phát hiện ra hành vi mà bên tranh chấp cho rằng quyền hợp pháp của mình bị vi phạm"

### BLLD_45-2019.D201.K2.a#1 — khớp
> Đồng ý hay không đồng ý đình công;

gold: m1 "Đồng ý" · m2 "không đồng ý" · **c1** "đình công" → m1,m2

### BLLD_45-2019.D202.K1#1 — khớp
> Khi có trên 50% số người được lấy ý kiến đồng ý với nội dung lấy ý kiến đình công theo quy định tại khoản 2 Điều 201 của Bộ luật này thì tổ chức đại diện người lao động ra quyết định đình công bằng văn bản.

gold: m1 "có trên 50% số người được lấy ý kiến đồng ý với nội dung lấy ý kiến đình công theo quy định tại khoản 2 Điều 201 của Bộ luật này" · m2 "tổ chức đại diện người lao động ra quyết định đình công bằng văn bản"

### BLLD_45-2019.D205.K2#1 — khớp
> Ủy ban nhân dân cấp tỉnh có nơi làm việc dự kiến đóng cửa;

gold: m1 "Ủy ban nhân dân cấp tỉnh có nơi làm việc dự kiến đóng cửa"

### BLLD_45-2019.D218#1 — khớp
> Người sử dụng lao động sử dụng dưới 10 người lao động thực hiện quy định của Bộ luật này nhưng được miễn, giảm một số thủ tục theo quy định của Chính phủ.

gold: **c1** "Người sử dụng lao động" → m1,m2,m3,m4 · m1 "sử dụng dưới 10 người lao động" · m2 "thực hiện quy định của Bộ luật này" · **c2** "được" → m3,m4 · m3 "miễn" · m4 "giảm" · **c3** "một số thủ tục theo quy định của Chính phủ" → m3,m4

### BLLD_45-2019.D22.K1#1 — khớp
> Phụ lục hợp đồng lao động là bộ phận của hợp đồng lao động và có hiệu lực như hợp đồng lao động.

gold: **c1** "Phụ lục hợp đồng lao động" → m1,m2 · m1 "là bộ phận của hợp đồng lao động" · m2 "có hiệu lực như hợp đồng lao động"

### BLLD_45-2019.D27.K2#1 — SAI RANH GIỚI
> Trong thời gian thử việc, mỗi bên có quyền hủy bỏ hợp đồng thử việc hoặc hợp đồng lao động đã giao kết mà không cần báo trước và không phải bồi thường.

gold: **c1** "Trong thời gian thử việc, mỗi bên" → m1,m2,m3 · m1 "có quyền hủy bỏ hợp đồng thử việc hoặc hợp đồng lao động đã giao kết" · m2 "không cần báo trước" · m3 "không phải bồi thường"
model: **c1** "Trong thời gian thử việc" → m1,m2,m3 · **c2** "mỗi bên" → m1,m2,m3 · m1 "có quyền hủy bỏ hợp đồng thử việc hoặc hợp đồng lao động đã giao kết" · m2 "không cần báo trước" · m3 "không phải bồi thường"

### BLLD_45-2019.D32.K2#1 — khớp
> Người lao động thỏa thuận với người sử dụng lao động làm việc không trọn thời gian khi giao kết hợp đồng lao động.

gold: **c1** "Người lao động" → m1,m2 · m1 "thỏa thuận với người sử dụng lao động làm việc không trọn thời gian" · m2 "giao kết hợp đồng lao động"

### BLLD_45-2019.D35.K1.b#1 — khớp
> Ít nhất 30 ngày nếu làm việc theo hợp đồng lao động xác định thời hạn có thời hạn từ 12 tháng đến 36 tháng;

gold: m1 "Ít nhất 30 ngày" · m2 "làm việc theo hợp đồng lao động xác định thời hạn có thời hạn từ 12 tháng đến 36 tháng"

### BLLD_45-2019.D39#1 — khớp
> Đơn phương chấm dứt hợp đồng lao động trái pháp luật là trường hợp chấm dứt hợp đồng lao động không đúng quy định tại các điều 35, 36 và 37 của Bộ luật này.

gold: m1 "Đơn phương chấm dứt hợp đồng lao động trái pháp luật là trường hợp chấm dứt hợp đồng lao động không đúng quy định tại các điều 35, 36 và 37 của Bộ luật này"

### BLLD_45-2019.D44.K1#1 — khớp
> Phương án sử dụng lao động phải có những nội dung chủ yếu sau đây:

gold: m1 "Phương án sử dụng lao động phải có những nội dung chủ yếu sau đây"

### BLLD_45-2019.D48.K3.a#1 — khớp
> Hoàn thành thủ tục xác nhận thời gian đóng bảo hiểm xã hội, bảo hiểm thất nghiệp và trả lại cùng với bản chính giấy tờ khác nếu người sử dụng lao động đã giữ của người lao động;

gold: m1 "Hoàn thành thủ tục xác nhận thời gian đóng bảo hiểm xã hội, bảo hiểm thất nghiệp" · m2 "trả lại cùng với bản chính giấy tờ khác" · m3 "người sử dụng lao động đã giữ của người lao động"

### BLLD_45-2019.D49.K2#1 — khớp
> Hợp đồng lao động vô hiệu từng phần khi nội dung của phần đó vi phạm pháp luật nhưng không ảnh hưởng đến các phần còn lại của hợp đồng.

gold: m1 "Hợp đồng lao động vô hiệu từng phần" · **c1** "nội dung của phần đó" → m2,m3 · m2 "vi phạm pháp luật" · m3 "không ảnh hưởng đến các phần còn lại của hợp đồng"

### BLLD_45-2019.D5.K1.g#1 — khớp
> Các quyền khác theo quy định của pháp luật.

gold: m1 "Các quyền khác theo quy định của pháp luật"

### BLLD_45-2019.D51.K1#1 — khớp
> Khi hợp đồng lao động bị tuyên bố vô hiệu từng phần thì xử lý như sau:

gold: m1 "hợp đồng lao động bị tuyên bố vô hiệu từng phần" · m2 "xử lý như sau"

### BLLD_45-2019.D52.K1#1 — THIẾU PHẢN HỒI

### BLLD_45-2019.D55.K2.d#1 — khớp
> Trách nhiệm bồi thường tai nạn lao động, bệnh nghề nghiệp;

gold: m1 "Trách nhiệm bồi thường tai nạn lao động, bệnh nghề nghiệp"

### BLLD_45-2019.D62.K2.a#1 — khớp
> Nghề đào tạo;

gold: m1 "Nghề đào tạo"

### BLLD_45-2019.D76.K5#2 — khớp
> Đối với thỏa ước lao động tập thể ngành hoặc thỏa ước lao động tập thể có nhiều doanh nghiệp thì từng người sử dụng lao động và từng tổ chức đại diện người lao động tại các doanh nghiệp tham gia thỏa ước phải được nhận 01 bản.

gold: m1 "Đối với thỏa ước lao động tập thể ngành hoặc thỏa ước lao động tập thể có nhiều doanh nghiệp thì từng người sử dụng lao động và từng tổ chức đại diện người lao động tại các doanh nghiệp tham gia thỏa ước phải được nhận 01 bản"

### BLLD_45-2019.D82.K1#1 — khớp
> Thỏa ước lao động tập thể chỉ được sửa đổi, bổ sung theo thỏa thuận tự nguyện của các bên, thông qua thương lượng tập thể.

gold: **c1** "Thỏa ước lao động tập thể chỉ được" → m1,m2 · m1 "sửa đổi" · m2 "bổ sung" · **c2** "theo thỏa thuận tự nguyện của các bên, thông qua thương lượng tập thể" → m1,m2

### BLLD_45-2019.D94.K2#1 — SAI RANH GIỚI
> Người sử dụng lao động không được hạn chế hoặc can thiệp vào quyền tự quyết chi tiêu lương của người lao động; không được ép buộc người lao động chi tiêu lương vào việc mua hàng hóa, sử dụng dịch vụ của người sử dụng lao động hoặc của đơn vị khác mà người sử dụng lao động chỉ định.

gold: **c1** "Người sử dụng lao động" → m1,m2,m3 · **c2** "không được" → m1,m2 · m1 "hạn chế" · m2 "can thiệp" · **c3** "vào quyền tự quyết chi tiêu lương của người lao động" → m1,m2 · m3 "không được ép buộc người lao động chi tiêu lương vào việc mua hàng hóa, sử dụng dịch vụ của người sử dụng lao động hoặc của đơn vị khác mà người sử dụng lao động chỉ định"
model: **c1** "Người sử dụng lao động" → m1,m2,m3 · **c2** "không được" → m1,m2 · m1 "hạn chế" · m2 "can thiệp vào" · **c3** "quyền tự quyết chi tiêu lương của người lao động" → m1,m2 · m3 "không được ép buộc người lao động chi tiêu lương vào việc mua hàng hóa, sử dụng dịch vụ của người sử dụng lao động hoặc của đơn vị khác mà người sử dụng lao động chỉ định"
