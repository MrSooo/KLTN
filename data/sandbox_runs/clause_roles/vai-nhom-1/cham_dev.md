# Chấm lượt 2 `vai-nhom-1` trên bộ dev (36 đơn vị): KHÔNG ĐẠT

- qua_may: 0.861 (ngưỡng 0.95)
- f1_dong: 0.892 (ngưỡng 0.8)
- vai: 0.986 (ngưỡng 0.9)
- phuong_thuc: 0.986 (ngưỡng 0.85)
- cuc: 1.000 (ngưỡng 0.95)
- cau_truc: 0.806 (ngưỡng 0.7)
- chu_the.loai đúng trên dòng ghép: 0.905 (chỉ báo)
- dòng gold 87, LLM 79, ghép 74
- thiếu phản hồi: 2; chi phí: 353.6 VND

### BLLD_45-2019.D100.K1 (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

### BLLD_45-2019.D101.K1 (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

### BLLD_45-2019.D111.K2 (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D115.K2 (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 5, LLM 5, ghép 5; cấu trúc đúng

### BLLD_45-2019.D119.K3 (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 4, LLM 4, ghép 4; cấu trúc đúng

### BLLD_45-2019.D122.K3 (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D136.K2 (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D137.K2: THIẾU PHẢN HỒI

### BLLD_45-2019.D139.K2 (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

### BLLD_45-2019.D144.K2 (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

### BLLD_45-2019.D145.K1 (trikiet2045/gemini-3.8-flash-high): LỆCH; dòng gold 1, LLM 0, ghép 0; cấu trúc SAI; MÁY KIỂM: đoạn s1.m1 không có dòng nào
gold:
  - s1.m1 q1 dieu_kien khong khang_dinh [E] sử dụng người chưa đủ 15 tuổi làm việc
  (ngoai_le None, cac_muc_con danh_sach)
LLM:
  (ngoai_le None, cac_muc_con danh_sach)

### BLLD_45-2019.D152.K1 (trikiet2045/gemini-3.8-flash-high): LỆCH; dòng gold 2, LLM 3, ghép 2; cấu trúc SAI
gold:
  - s1.m1 q1 ket_luan duoc khang_dinh [E] tuyển dụng người lao động nước ngoài vào làm vị trí công việc quản lý, điều hành, chuyên gia và lao động kỹ thuật mà người lao động Việt Nam chưa đáp ứng được
  - s1.m1 q1 dieu_kien khong khang_dinh [E] theo nhu cầu sản xuất, kinh doanh
  (ngoai_le None, cac_muc_con None)
LLM:
  - s1.m1 q1 ket_luan duoc khang_dinh [E] tuyển dụng người lao động nước ngoài vào làm vị trí công việc quản lý, điều hành, chuyên gia và lao động kỹ thuật
  - s1.m1 q1 dieu_kien khong phu_dinh [W] đáp ứng được
  - s1.m1 q1 dieu_kien khong khang_dinh [W] theo nhu cầu sản xuất, kinh doanh
  (ngoai_le None, cac_muc_con None)

### BLLD_45-2019.D164.K2 (trikiet2045/gemini-3.8-flash-high): LỆCH; dòng gold 4, LLM 5, ghép 4; cấu trúc SAI
gold:
  - s1.m1 q1 ket_luan phai khang_dinh [W] bồi thường
  - s1.m1 q1 dieu_kien khong khang_dinh [W] theo thỏa thuận hoặc theo quy định của pháp luật
  - s1.m2 q1/h1 dieu_kien khong khang_dinh [W] làm hỏng | tài sản của người sử dụng lao động
  - s1.m3 q1/h1 dieu_kien khong khang_dinh [W] mất | tài sản của người sử dụng lao động
  (ngoai_le None, cac_muc_con None)
LLM:
  - s1.m1 q1 ket_luan phai khang_dinh [W] bồi thường
  - s1.m1 q1/h1 dieu_kien khong khang_dinh [W] theo thỏa thuận
  - s1.m1 q1/h1 dieu_kien khong khang_dinh [W] theo quy định của pháp luật
  - s1.m2 q1/h2 dieu_kien khong khang_dinh [W] làm hỏng | tài sản của người sử dụng lao động
  - s1.m3 q1/h2 dieu_kien khong khang_dinh [W] mất | tài sản của người sử dụng lao động
  (ngoai_le None, cac_muc_con None)

### BLLD_45-2019.D177.K5 (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 0, LLM 0, ghép 0; cấu trúc đúng

### BLLD_45-2019.D178.K7 (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

### BLLD_45-2019.D182.K1 (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 0, LLM 0, ghép 0; cấu trúc đúng

### BLLD_45-2019.D186 (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

### BLLD_45-2019.D194.K1 (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 1, LLM 1, ghép 1; cấu trúc đúng

### BLLD_45-2019.D201.K2.a (trikiet2045/gemini-3.8-flash-high): LỆCH; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng; MÁY KIỂM: doan bỏ chữ 'hay không đồng ý'
gold:
  - s1.m1 q1 ket_luan khong khang_dinh [None] Đồng ý
  - s1.m2 q1 ket_luan khong phu_dinh [None] đồng ý
  (ngoai_le None, cac_muc_con None)
LLM:
  - s1.m1 q1 ket_luan khong khang_dinh [None] Đồng ý | đình công
  - s1.m2 q1 ket_luan khong phu_dinh [None] đồng ý | đình công
  (ngoai_le None, cac_muc_con None)

### BLLD_45-2019.D202.K1 (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D205.K2 (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 1, LLM 1, ghép 1; cấu trúc đúng

### BLLD_45-2019.D218 (trikiet2045/gemini-3.8-flash-high): LỆCH; dòng gold 4, LLM 6, ghép 3; cấu trúc SAI
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

### BLLD_45-2019.D22.K1 (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D27.K2 (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 4, LLM 4, ghép 4; cấu trúc đúng

### BLLD_45-2019.D32.K2 (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D35.K1.b (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D39: THIẾU PHẢN HỒI

### BLLD_45-2019.D44.K1 (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 0, LLM 0, ghép 0; cấu trúc đúng

### BLLD_45-2019.D48.K3.a (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

### BLLD_45-2019.D49.K2 (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

### BLLD_45-2019.D5.K1.g (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 0, LLM 0, ghép 0; cấu trúc đúng

### BLLD_45-2019.D51.K1 (trikiet2045/gemini-3.8-flash-high): LỆCH; dòng gold 1, LLM 0, ghép 0; cấu trúc SAI; MÁY KIỂM: đoạn s1.m1 không có dòng nào
gold:
  - s1.m1 q1 dieu_kien khong khang_dinh [C] bị tuyên bố vô hiệu từng phần
  (ngoai_le None, cac_muc_con danh_sach)
LLM:
  (ngoai_le None, cac_muc_con danh_sach)

### BLLD_45-2019.D52.K1 (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 5, LLM 5, ghép 5; cấu trúc đúng

### BLLD_45-2019.D55.K2.d (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 1, LLM 1, ghép 1; cấu trúc đúng

### BLLD_45-2019.D62.K2.a (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 1, LLM 1, ghép 1; cấu trúc đúng

### BLLD_45-2019.D94.K2 (trikiet2045/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

