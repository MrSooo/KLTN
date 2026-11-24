# Lượt 1 `tach-cau-1` trên cả BLLĐ (993 câu, mỗi câu gọi một lần)

- qua máy kiểm: 984/993; không qua: 7; thiếu phản hồi: 2
- chi phí: 9904.7 VND; phản hồi theo tuyến: dungcsnd113/gemini-flash-3.8 103, trikiet2045/gemini-3.8-flash-high 888
- chấm lại gold trên lần gọi này (lần gọi thứ hai của cùng câu, cùng lời nhắc):
  - dev: khớp 35/40 (lần đầu 35/40; thiếu phản hồi 0), đổi kết quả khớp/không khớp ở 2 câu ['BLLD_45-2019.D193.K3#2', 'BLLD_45-2019.D218#1']; điểm cắt 0.971/0.971
  - test: khớp 15/20 (lần đầu 17/20; thiếu phản hồi 0), đổi kết quả khớp/không khớp ở 2 câu ['BLLD_45-2019.D33.K1#1', 'BLLD_45-2019.D61.K5#1']; điểm cắt 0.926/0.971

## Loại lỗi máy kiểm (đếm theo lỗi, một câu có thể nhiều lỗi)

- 5 mở đầu bằng chữ nối
- 2 không khớp nguyên văn tại

## Cờ trên câu qua (chỉ cảnh báo)

- 762 mệnh đề từ 15 chữ

## Câu không qua máy kiểm (để lượt 2 xử lý; không sửa tay)

- BLLD_45-2019.D3.K8#2: m1: không khớp nguyên văn tại 'phân biệt , loại trừ hoặc ...'
- BLLD_45-2019.D6.K2.c#1: c1: không khớp nguyên văn tại 'nhằm duy trì , chuyển đổi ...'
- BLLD_45-2019.D37.K2#1: m3: mở đầu bằng chữ nối 'trường hợp'
- BLLD_45-2019.D118.K2.e#1: m1: mở đầu bằng chữ nối 'trường hợp'
- BLLD_45-2019.D125.K4#2: m1: mở đầu bằng chữ nối 'trường hợp'
- BLLD_45-2019.D128.K2#1: m2: mở đầu bằng chữ nối 'trường hợp'
- BLLD_45-2019.D154.K7#1: m1: mở đầu bằng chữ nối 'trường hợp'
- BLLD_45-2019.D172.K2#1: THIẾU PHẢN HỒI
- BLLD_45-2019.D217.K3#1: THIẾU PHẢN HỒI
