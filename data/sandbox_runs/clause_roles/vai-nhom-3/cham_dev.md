# Chấm lượt 2 `vai-nhom-3` trên bộ dev (36 đơn vị): ĐẠT

- qua_may: 0.972 (ngưỡng 0.95)
- f1_dong: 0.933 (ngưỡng 0.8)
- vai: 0.964 (ngưỡng 0.9)
- phuong_thuc: 0.988 (ngưỡng 0.85)
- cuc: 0.988 (ngưỡng 0.95)
- cau_truc: 0.806 (ngưỡng 0.7)
- chu_the.loai đúng trên dòng ghép: 0.917 (chỉ báo)
- dòng gold 87, LLM 93, ghép 84
- thiếu phản hồi: 0; chi phí: 468.0 VND

### BLLD_45-2019.D100.K1 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

### BLLD_45-2019.D101.K1 (daongocson12022004/gemini-3.8-flash-high): LỆCH; dòng gold 3, LLM 3, ghép 3; cấu trúc SAI
gold:
  - s1.m1 q1 ket_luan duoc khang_dinh [W] tạm ứng tiền lương
  - s1.m1 q1 dieu_kien khong khang_dinh [W] theo điều kiện do hai bên thỏa thuận
  - s1.m2 q2 ket_luan khong phu_dinh [W] bị tính lãi
  (ngoai_le None, cac_muc_con None)
LLM:
  - s1.m1 q1 ket_luan duoc khang_dinh [W] tạm ứng tiền lương
  - s1.m1 q1 dieu_kien khong khang_dinh [W] theo điều kiện do hai bên thỏa thuận
  - s1.m2 q1 ket_luan khong phu_dinh [W] bị tính lãi
  (ngoai_le None, cac_muc_con None)

### BLLD_45-2019.D111.K2 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D115.K2 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 5, LLM 5, ghép 5; cấu trúc đúng

### BLLD_45-2019.D119.K3 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 4, LLM 4, ghép 4; cấu trúc đúng

### BLLD_45-2019.D122.K3 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D136.K2 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D137.K2 (daongocson12022004/gemini-3.8-flash-high): LỆCH; dòng gold 7, LLM 8, ghép 6; cấu trúc SAI
gold:
  - s1.m1 q1/h1 dieu_kien khong khang_dinh [W] làm nghề, công việc nặng nhọc, độc hại, nguy hiểm hoặc đặc biệt nặng nhọc, độc hại, nguy hiểm
  - s1.m2 q1/h1 dieu_kien khong khang_dinh [W] làm nghề, công việc có ảnh hưởng xấu tới chức năng sinh sản và nuôi con
  - s1.m3 q1 dieu_kien khong khang_dinh [W] mang thai
  - s1.m4 q1 dieu_kien khong khang_dinh [W] có thông báo
  - s1.m5 q1 ket_luan duoc khang_dinh [W] chuyển sang làm công việc nhẹ hơn, an toàn hơn
  - s1.m6 q1 ket_luan duoc khang_dinh [W] giảm bớt 01 giờ làm việc hằng ngày
  - s1.m7 q1 ket_luan khong phu_dinh [W] bị cắt giảm tiền lương và quyền, lợi ích cho đến hết thời gian nuôi con dưới 12 tháng tuổi
  (ngoai_le None, cac_muc_con None)
LLM:
  - s1.m1 q1/h1 dieu_kien khong khang_dinh [W] làm nghề, công việc nặng nhọc, độc hại, nguy hiểm hoặc đặc biệt nặng nhọc, độc hại, nguy hiểm
  - s1.m2 q1/h1 dieu_kien khong khang_dinh [W] làm nghề, công việc có ảnh hưởng xấu tới chức năng sinh sản và nuôi con
  - s1.m3 q1 dieu_kien khong khang_dinh [W] mang thai
  - s1.m4 q1 dieu_kien khong khang_dinh [W] thông báo cho người sử dụng lao động biết
  - s1.m5 q1 ket_luan duoc khang_dinh [W] chuyển sang làm công việc nhẹ hơn, an toàn hơn
  - s1.m6 q1 ket_luan duoc khang_dinh [W] giảm bớt 01 giờ làm việc hằng ngày
  - s1.m7 q1 ket_luan khong phu_dinh [W] cắt giảm tiền lương và quyền, lợi ích
  - s1.m7 q1 dieu_kien khong khang_dinh [W] cho đến hết thời gian nuôi con dưới 12 tháng tuổi
  (ngoai_le None, cac_muc_con None)

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

### BLLD_45-2019.D164.K2 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 4, LLM 4, ghép 4; cấu trúc đúng

### BLLD_45-2019.D177.K5 (daongocson12022004/gemini-3.8-flash-high): LỆCH; dòng gold 0, LLM 0, ghép 0; cấu trúc SAI
gold:
  (ngoai_le None, cac_muc_con None)
LLM:
  (ngoai_le None, cac_muc_con None)

### BLLD_45-2019.D178.K7 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

### BLLD_45-2019.D182.K1 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 0, LLM 0, ghép 0; cấu trúc đúng

### BLLD_45-2019.D186 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

### BLLD_45-2019.D194.K1 (daongocson12022004/gemini-3.8-flash-high): LỆCH; dòng gold 1, LLM 2, ghép 1; cấu trúc SAI
gold:
  - s1.m1 q1 ket_luan khong khang_dinh [None] Thời hiệu yêu cầu hòa giải viên lao động thực hiện hòa giải tranh chấp lao động tập thể về quyền là 06 tháng kể từ ngày phát hiện ra hành vi mà bên tranh chấp cho rằng quyền hợp pháp của mình bị vi phạm
  (ngoai_le None, cac_muc_con None)
LLM:
  - s1.m1 q1 ket_luan khong khang_dinh [None] Thời hiệu yêu cầu hòa giải viên lao động thực hiện hòa giải tranh chấp lao động tập thể về quyền là 06 tháng
  - s1.m1 q1 dieu_kien khong khang_dinh [None] kể từ ngày phát hiện ra hành vi mà bên tranh chấp cho rằng quyền hợp pháp của mình bị vi phạm
  (ngoai_le None, cac_muc_con None)

### BLLD_45-2019.D201.K2.a (daongocson12022004/gemini-3.8-flash-high): LỆCH; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng; MÁY KIỂM: doan bỏ chữ 'hay không đồng ý'
gold:
  - s1.m1 q1 ket_luan khong khang_dinh [None] Đồng ý
  - s1.m2 q1 ket_luan khong phu_dinh [None] đồng ý
  (ngoai_le None, cac_muc_con None)
LLM:
  - s1.m1 q1 ket_luan khong khang_dinh [None] Đồng ý | đình công
  - s1.m2 q1 ket_luan khong phu_dinh [None] đồng ý | đình công
  (ngoai_le None, cac_muc_con None)

### BLLD_45-2019.D202.K1 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D205.K2 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 1, LLM 1, ghép 1; cấu trúc đúng

### BLLD_45-2019.D218 (daongocson12022004/gemini-3.8-flash-high): LỆCH; dòng gold 4, LLM 6, ghép 3; cấu trúc SAI
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

### BLLD_45-2019.D27.K2 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 4, LLM 4, ghép 4; cấu trúc đúng

### BLLD_45-2019.D32.K2 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D35.K1.b (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D39 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

### BLLD_45-2019.D44.K1 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 0, LLM 0, ghép 0; cấu trúc đúng

### BLLD_45-2019.D48.K3.a (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

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

### BLLD_45-2019.D94.K2 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

