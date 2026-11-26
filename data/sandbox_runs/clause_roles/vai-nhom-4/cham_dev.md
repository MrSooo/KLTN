# Chấm lượt 2 `vai-nhom-4` trên bộ dev (36 đơn vị): KHÔNG ĐẠT

- qua_may: 0.861 (ngưỡng 0.95)
- f1_dong: 0.815 (ngưỡng 0.8)
- vai: 0.970 (ngưỡng 0.9)
- phuong_thuc: 0.970 (ngưỡng 0.85)
- cuc: 1.000 (ngưỡng 0.95)
- cau_truc: 0.694 (ngưỡng 0.7)
- chu_the.loai đúng trên dòng ghép: 0.924 (chỉ báo)
- dòng gold 87, LLM 75, ghép 66
- thiếu phản hồi: 4; chi phí: 416.0 VND

### BLLD_45-2019.D100.K1 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

### BLLD_45-2019.D101.K1 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

### BLLD_45-2019.D111.K2 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D115.K2 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 5, LLM 5, ghép 5; cấu trúc đúng

### BLLD_45-2019.D119.K3 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 4, LLM 4, ghép 4; cấu trúc đúng

### BLLD_45-2019.D122.K3 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D136.K2 (daongocson12022004/gemini-3.8-flash-high): LỆCH; dòng gold 2, LLM 2, ghép 1; cấu trúc SAI
gold:
  - s1.m1 q1 ket_luan phai khang_dinh [E] Tham khảo ý kiến của lao động nữ hoặc đại diện của họ
  - s1.m2 q1 dieu_kien khong khang_dinh [E] quyết định những vấn đề liên quan đến quyền và lợi ích của phụ nữ
  (ngoai_le None, cac_muc_con None)
LLM:
  - s1.m2 q1 dieu_kien khong khang_dinh [E] quyết định những vấn đề liên quan đến quyền và lợi ích của phụ nữ
  - s1.m1 q1 ket_luan phai khang_dinh [E] Tham khảo ý kiến của
  (ngoai_le None, cac_muc_con None)

### BLLD_45-2019.D137.K2: THIẾU PHẢN HỒI

### BLLD_45-2019.D139.K2 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

### BLLD_45-2019.D144.K2 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

### BLLD_45-2019.D145.K1 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 1, LLM 1, ghép 1; cấu trúc đúng

### BLLD_45-2019.D152.K1 (daongocson12022004/gemini-3.8-flash-high): LỆCH; dòng gold 2, LLM 3, ghép 1; cấu trúc SAI
gold:
  - s1.m1 q1 ket_luan duoc khang_dinh [E] tuyển dụng người lao động nước ngoài vào làm vị trí công việc quản lý, điều hành, chuyên gia và lao động kỹ thuật mà người lao động Việt Nam chưa đáp ứng được
  - s1.m1 q1 dieu_kien khong khang_dinh [E] theo nhu cầu sản xuất, kinh doanh
  (ngoai_le None, cac_muc_con None)
LLM:
  - s1.m1 q1 ket_luan duoc khang_dinh [E] tuyển dụng người lao động nước ngoài vào làm vị trí công việc
  - s1.m1 q1 dieu_kien khong phu_dinh [W] đáp ứng được
  - s1.m1 q1 dieu_kien khong khang_dinh [W] theo nhu cầu sản xuất, kinh doanh
  (ngoai_le None, cac_muc_con None)

### BLLD_45-2019.D164.K2 (daongocson12022004/gemini-3.8-flash-high): LỆCH; dòng gold 4, LLM 3, ghép 3; cấu trúc SAI
gold:
  - s1.m1 q1 ket_luan phai khang_dinh [W] bồi thường
  - s1.m1 q1 dieu_kien khong khang_dinh [W] theo thỏa thuận hoặc theo quy định của pháp luật
  - s1.m2 q1/h1 dieu_kien khong khang_dinh [W] làm hỏng | tài sản của người sử dụng lao động
  - s1.m3 q1/h1 dieu_kien khong khang_dinh [W] mất | tài sản của người sử dụng lao động
  (ngoai_le None, cac_muc_con None)
LLM:
  - s1.m1 q1 ket_luan phai khang_dinh [W] bồi thường theo thỏa thuận hoặc theo quy định của pháp luật
  - s1.m2 q1/h1 dieu_kien khong khang_dinh [W] làm hỏng | tài sản của người sử dụng lao động
  - s1.m3 q1/h1 dieu_kien khong khang_dinh [W] mất | tài sản của người sử dụng lao động
  (ngoai_le None, cac_muc_con None)

### BLLD_45-2019.D177.K5 (daongocson12022004/gemini-3.8-flash-high): LỆCH; dòng gold 0, LLM 1, ghép 0; cấu trúc SAI
gold:
  (ngoai_le None, cac_muc_con None)
LLM:
  - s1.m1 q1 ket_luan phai khang_dinh [E] Các nghĩa vụ khác theo quy định của pháp luật
  (ngoai_le None, cac_muc_con None)

### BLLD_45-2019.D178.K7 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

### BLLD_45-2019.D182.K1 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 0, LLM 0, ghép 0; cấu trúc đúng

### BLLD_45-2019.D186 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

### BLLD_45-2019.D194.K1 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 1, LLM 1, ghép 1; cấu trúc đúng

### BLLD_45-2019.D201.K2.a (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D202.K1 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D205.K2 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 1, LLM 1, ghép 1; cấu trúc đúng

### BLLD_45-2019.D218 (daongocson12022004/gemini-3.8-flash-high): LỆCH; dòng gold 4, LLM 6, ghép 3; cấu trúc SAI; MÁY KIỂM: trường thiếu [] / thừa ['khoa_thua']
gold:
  - s1.m1 q1 dieu_kien khong khang_dinh [E] sử dụng dưới 10 người lao động
  - s1.m2 q1 ket_luan khong khang_dinh [E] thực hiện quy định của Bộ luật này
  - s1.m3 q1 ket_luan duoc khang_dinh [E] miễn | một số thủ tục theo quy định của Chính phủ
  - s1.m4 q1 ket_luan duoc khang_dinh [E] giảm | một số thủ tục theo quy định của Chính phủ
  (ngoai_le None, cac_muc_con None)
LLM:
  - s1.m1 q1 dieu_kien khong khang_dinh [E] sử dụng dưới 10 người lao động
  - s1.m2 q1 ket_luan khong khang_dinh [E] thực hiện quy định của Bộ luật này
  - s1.m1 q2 dieu_kien khong khang_dinh [E] sử dụng dưới 10 người lao động
  - s1.m3 q2 dieu_kien khong khang_dinh [E] theo quy định của Chính phủ
  - s1.m3 q2 ket_luan duoc khang_dinh [E] miễn | một số thủ tục
  - s1.m4 q2 ket_luan duoc khang_dinh [E] giảm | một số thủ tục
  (ngoai_le None, cac_muc_con None)

### BLLD_45-2019.D22.K1 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D27.K2 (daongocson12022004/gemini-3.8-flash-high): LỆCH; dòng gold 4, LLM 4, ghép 3; cấu trúc SAI
gold:
  - s1.m1 q1 ket_luan duoc khang_dinh [['E', 'W']] hủy bỏ hợp đồng thử việc hoặc hợp đồng lao động đã giao kết
  - s1.m1 q1 dieu_kien khong khang_dinh [['E', 'W']] Trong thời gian thử việc
  - s1.m2 q1 ket_luan duoc phu_dinh [['E', 'W']] báo trước
  - s1.m3 q1 ket_luan duoc phu_dinh [['E', 'W']] bồi thường
  (ngoai_le None, cac_muc_con None)
LLM:
  - s1.m1 q1 dieu_kien khong khang_dinh [['W', 'E']] Trong thời gian thử việc
  - s1.m1 q1 ket_luan duoc khang_dinh [['W', 'E']] hủy bỏ
  - s1.m2 q1 ket_luan duoc phu_dinh [['W', 'E']] báo trước
  - s1.m3 q1 ket_luan duoc phu_dinh [['W', 'E']] bồi thường
  (ngoai_le None, cac_muc_con None)

### BLLD_45-2019.D32.K2 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D35.K1.b (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D39: THIẾU PHẢN HỒI

### BLLD_45-2019.D44.K1 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 0, LLM 0, ghép 0; cấu trúc đúng

### BLLD_45-2019.D48.K3.a: THIẾU PHẢN HỒI

### BLLD_45-2019.D49.K2 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

### BLLD_45-2019.D5.K1.g (daongocson12022004/gemini-3.8-flash-high): LỆCH; dòng gold 0, LLM 1, ghép 0; cấu trúc SAI
gold:
  (ngoai_le None, cac_muc_con None)
LLM:
  - s1.m1 q1 ket_luan duoc khang_dinh [W] Các quyền khác theo quy định của pháp luật
  (ngoai_le None, cac_muc_con None)

### BLLD_45-2019.D51.K1 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 1, LLM 1, ghép 1; cấu trúc đúng

### BLLD_45-2019.D52.K1 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 5, LLM 5, ghép 5; cấu trúc đúng

### BLLD_45-2019.D55.K2.d (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 1, LLM 1, ghép 1; cấu trúc đúng

### BLLD_45-2019.D62.K2.a (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 1, LLM 1, ghép 1; cấu trúc đúng

### BLLD_45-2019.D94.K2: THIẾU PHẢN HỒI

