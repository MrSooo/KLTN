# Chấm lượt 2 `vai-nhom-3` trên bộ test (20 đơn vị): ĐẠT

- qua_may: 0.950 (ngưỡng 0.95)
- f1_dong: 0.972 (ngưỡng 0.8)
- vai: 1.000 (ngưỡng 0.9)
- phuong_thuc: 1.000 (ngưỡng 0.85)
- cuc: 0.981 (ngưỡng 0.95)
- cau_truc: 0.850 (ngưỡng 0.7)
- chu_the.loai đúng trên dòng ghép: 0.887 (chỉ báo)
- dòng gold 53, LLM 56, ghép 53
- thiếu phản hồi: 0; chi phí: 260.0 VND

### BLLD_45-2019.D107.K4 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D118.K1 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

### BLLD_45-2019.D126.K1 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 5, LLM 5, ghép 5; cấu trúc đúng

### BLLD_45-2019.D143.K1 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D149.K1 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D162.K3 (daongocson12022004/gemini-3.8-flash-high): LỆCH; dòng gold 1, LLM 2, ghép 1; cấu trúc SAI
gold:
  - s1.m1 q1 ket_luan khong khang_dinh [['E', 'W']] thỏa thuận trong hợp đồng lao động về hình thức trả lương, kỳ hạn trả lương, thời giờ làm việc hằng ngày, chỗ ở
  (ngoai_le None, cac_muc_con None)
LLM:
  - s1.m1 q1 ket_luan khong khang_dinh [['W', 'E']] thỏa thuận | về hình thức trả lương, kỳ hạn trả lương, thời giờ làm việc hằng ngày, chỗ ở
  - s1.m1 q1 dieu_kien khong khang_dinh [['W', 'E']] trong hợp đồng lao động
  (ngoai_le None, cac_muc_con None)

### BLLD_45-2019.D163.K4 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D170.K2 (daongocson12022004/gemini-3.8-flash-high): LỆCH; dòng gold 3, LLM 4, ghép 3; cấu trúc SAI
gold:
  - s1.m1 q1 ket_luan duoc khang_dinh [W] thành lập | tổ chức của người lao động tại doanh nghiệp
  - s1.m2 q1 ket_luan duoc khang_dinh [W] gia nhập | tổ chức của người lao động tại doanh nghiệp
  - s1.m3 q1 ket_luan duoc khang_dinh [W] tham gia hoạt động của | tổ chức của người lao động tại doanh nghiệp
  (ngoai_le None, cac_muc_con None)
LLM:
  - s1.m1 q1 ket_luan duoc khang_dinh [W] thành lập | tổ chức của người lao động tại doanh nghiệp
  - s1.m1 q1 dieu_kien khong khang_dinh [W] theo quy định | của Bộ luật này
  - s1.m2 q1 ket_luan duoc khang_dinh [W] gia nhập | tổ chức của người lao động tại doanh nghiệp
  - s1.m3 q1 ket_luan duoc khang_dinh [W] tham gia hoạt động của | tổ chức của người lao động tại doanh nghiệp
  (ngoai_le None, cac_muc_con None)

### BLLD_45-2019.D174.K1.e (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 1, LLM 1, ghép 1; cấu trúc đúng

### BLLD_45-2019.D19.K1 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D203.K2.a (daongocson12022004/gemini-3.8-flash-high): LỆCH; dòng gold 4, LLM 4, ghép 4; cấu trúc đúng
gold:
  - s1.m1 q1 ket_luan duoc khang_dinh [?] Rút quyết định đình công
  - s1.m2 q1 dieu_kien khong phu_dinh [?] đình công
  - s1.m3 q2 ket_luan duoc khang_dinh [?] chấm dứt đình công
  - s1.m4 q2 dieu_kien khong khang_dinh [?] đang đình công
  (ngoai_le None, cac_muc_con None)
LLM:
  - s1.m1 q1 ket_luan duoc khang_dinh [W] Rút quyết định đình công
  - s1.m2 q1 dieu_kien khong khang_dinh [W] chưa đình công
  - s1.m3 q2 ket_luan duoc khang_dinh [W] chấm dứt đình công
  - s1.m4 q2 dieu_kien khong khang_dinh [W] đang đình công
  (ngoai_le None, cac_muc_con None)

### BLLD_45-2019.D209.K1 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

### BLLD_45-2019.D30.K1 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 1, LLM 1, ghép 1; cấu trúc đúng

### BLLD_45-2019.D33.K1 (daongocson12022004/gemini-3.8-flash-high): LỆCH; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng; MÁY KIỂM: doi_so sai khuôn {'loai': ['W', 'E']}
gold:
  - s1.m1 q1 dieu_kien khong khang_dinh [['E', 'W']] có yêu cầu sửa đổi, bổ sung nội dung hợp đồng lao động
  - s1.m1 q1 dieu_kien khong khang_dinh [['E', 'W']] Trong quá trình thực hiện hợp đồng lao động
  - s1.m2 q1 ket_luan phai khang_dinh [['E', 'W']] báo cho bên kia biết trước ít nhất 03 ngày làm việc về nội dung cần sửa đổi, bổ sung
  (ngoai_le None, cac_muc_con None)
LLM:
  - s1.m1 q1 dieu_kien khong khang_dinh [['W', 'E']] Trong quá trình thực hiện hợp đồng lao động
  - s1.m1 q1 dieu_kien khong khang_dinh [['W', 'E']] có yêu cầu sửa đổi, bổ sung nội dung hợp đồng lao động
  - s1.m2 q1 ket_luan phai khang_dinh [['W', 'E']] báo cho bên kia biết trước ít nhất 03 ngày làm việc về nội dung cần sửa đổi, bổ sung
  (ngoai_le None, cac_muc_con None)

### BLLD_45-2019.D59.K1 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

### BLLD_45-2019.D6.K1.b (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 3, LLM 3, ghép 3; cấu trúc đúng

### BLLD_45-2019.D61.K5 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 4, LLM 4, ghép 4; cấu trúc đúng

### BLLD_45-2019.D79.K1 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 1, LLM 1, ghép 1; cấu trúc đúng

### BLLD_45-2019.D97.K3 (daongocson12022004/gemini-3.8-flash-high): LỆCH; dòng gold 7, LLM 8, ghép 7; cấu trúc SAI
gold:
  - s1.m1 q1 dieu_kien khong khang_dinh [W] hưởng lương theo sản phẩm, theo khoán
  - s1.m2 q1 ket_luan duoc khang_dinh [W] trả lương
  - s1.m2 q1 dieu_kien khong khang_dinh [W] theo thỏa thuận của hai bên
  - s1.m1 q2 dieu_kien khong khang_dinh [W] hưởng lương theo sản phẩm, theo khoán
  - s1.m3 q2 dieu_kien khong khang_dinh [None] công việc phải làm trong nhiều tháng
  - s1.m4 q2 ket_luan duoc khang_dinh [W] hằng tháng | tạm ứng tiền lương
  - s1.m4 q2 dieu_kien khong khang_dinh [W] theo khối lượng công việc đã làm trong tháng
  (ngoai_le None, cac_muc_con None)
LLM:
  - s1.m1 q1 dieu_kien khong khang_dinh [W] hưởng lương theo sản phẩm, theo khoán
  - s1.m2 q1 ket_luan duoc khang_dinh [W] trả lương
  - s1.m2 q1 dieu_kien khong khang_dinh [W] theo thỏa thuận của hai bên
  - s1.m1 q2 dieu_kien khong khang_dinh [W] hưởng lương theo sản phẩm, theo khoán
  - s1.m3 q2 dieu_kien khong khang_dinh [J] làm trong nhiều tháng
  - s1.m4 q2 dieu_kien khong khang_dinh [W] hằng tháng
  - s1.m4 q2 ket_luan duoc khang_dinh [W] tạm ứng tiền lương
  - s1.m4 q2 dieu_kien khong khang_dinh [W] theo khối lượng công việc đã làm trong tháng
  (ngoai_le None, cac_muc_con None)

### BLLD_45-2019.D98.K3 (daongocson12022004/gemini-3.8-flash-high): khớp; dòng gold 2, LLM 2, ghép 2; cấu trúc đúng

