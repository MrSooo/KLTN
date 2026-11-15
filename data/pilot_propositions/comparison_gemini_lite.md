# So sánh 1.6A thí điểm (menh-de-3) với đáp án nháp

Mỗi đơn vị có chỗ lệch: dòng của đáp án (ĐA) và của LLM; người dùng phán bên nào đúng. Đơn vị khớp hết không liệt kê.

- Dòng: ĐA 97, LLM 79; ghép được 62, chỉ ĐA có 35, chỉ LLM có 17.
- Lỗi cổng của LLM: 26. Câu dẫn lọt thành mệnh đề (ước bằng máy): 0.
- Field khớp trên các dòng ghép được: {'bo_qua.ly_do.ma': '5/5', 'bo_qua.cac_muc_con': '3/5', 'menh_de.vai': '40/49', 'menh_de.menh_de': '30/49', 'menh_de.phuong_thuc': '43/49', 'menh_de.cuc': '45/49', 'menh_de.chu_the.loai': '35/49', 'menh_de.doi_so': '26/49', 'menh_de.bo_ngu': '35/49', 'menh_de.liet_ke': '49/49', 'menh_de.nhom_hoac': '40/49', 'menh_de.chua_ro': '44/49', 'menh_de.quy_tac': '33/49', 'con_tro.vai': '8/8', 'con_tro.targets': '7/8', 'con_tro.gan_vao': '2/8', 'con_tro.chua_ro': '7/8'}.
- Chưa rõ của LLM theo nguyên nhân: {'pham_vi_bo_ngu': 1}.
- Đây là so với đáp án NHÁP: chỉ thành số đo sau khi người dùng phán xong các chỗ lệch (A38 K10).

## D5.K1.a

Chữ: Làm việc; tự do lựa chọn việc làm, nơi làm việc, nghề nghiệp, học nghề, nâng cao trình độ nghề nghiệp; không bị phân biệt đối xử, cưỡng bức lao động, quấy rối tình dục tại nơi làm việc;
Câu dẫn: Người lao động có các quyền sau đây:

- **Lệch** ĐA#0 / LLM#0: quy_tac: ĐA='q1 (lệch nhóm với ĐA#[2])' LLM='q1'
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «làm việc» chủ thể=Người lao động:W q1
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «làm việc» chủ thể=Người lao động:W q1 — lý do tach: Tách quyền làm việc độc lập.
- **Lệch** ĐA#2 / LLM#1: menh_de: ĐA='tự do lựa chọn nơi làm việc' LLM='tự do lựa chọn việc làm, nơi làm việc, nghề nghiệp, học nghề, nâng cao trình độ nghề nghiệp'; doi_so: ĐA=['?'] LLM=[]; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0])' LLM='q2'
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «tự do lựa chọn nơi làm việc» chủ thể=Người lao động:W q1
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «tự do lựa chọn việc làm, nơi làm việc, nghề nghiệp, học nghề, nâng cao trình độ nghề nghiệp» chủ thể=Người lao động:W q2 — lý do tach: Tách quyền tự do lựa chọn.
- **Chỉ ĐA có** #1: menh_de/ket_luan [duoc,khang_dinh] «tự do lựa chọn việc làm» chủ thể=Người lao động:W q1 — lý do tach: Tự do chọn việc làm, nơi làm việc, nghề nghiệp là ba quyền riêng: hạn chế từng cái là vi phạm riêng.
- **Chỉ ĐA có** #3: menh_de/ket_luan [duoc,khang_dinh] «tự do lựa chọn nghề nghiệp» chủ thể=Người lao động:W q1
- **Chỉ ĐA có** #4: menh_de/ket_luan [duoc,khang_dinh] «học nghề» chủ thể=Người lao động:W q1 CHƯA RÕ=[('tự do lựa chọn', 'pham_vi_bo_ngu')]
- **Chỉ ĐA có** #5: menh_de/ket_luan [duoc,khang_dinh] «nâng cao trình độ nghề nghiệp» chủ thể=Người lao động:W q1 CHƯA RÕ=[('tự do lựa chọn', 'pham_vi_bo_ngu')]
- **Chỉ ĐA có** #6: menh_de/ket_luan [duoc,phu_dinh] «bị phân biệt đối xử» chủ thể=Người lao động:W q1 — lý do tach: 'Không bị' là quyền được bảo vệ (duoc + phu_dinh); ba hành vi bị cấm riêng nên tách ba dòng.
- **Chỉ ĐA có** #7: menh_de/ket_luan [duoc,phu_dinh] «bị cưỡng bức lao động» chủ thể=Người lao động:W q1
- **Chỉ ĐA có** #8: menh_de/ket_luan [duoc,phu_dinh] «bị quấy rối tình dục» chủ thể=Người lao động:W q1 bổ ngữ=[('tại nơi làm việc', 'this_clause')] — lý do gan_bo_ngu: 'Tại nơi làm việc' gắn với 'quấy rối tình dục' (khái niệm định nghĩa riêng); phân biệt đối xử và cưỡng bức lao động bị cấm ở mọi nơi.
- **Chỉ LLM có** #2: menh_de/ket_luan [duoc,phu_dinh] «được phân biệt đối xử, cưỡng bức lao động, quấy rối tình dục tại nơi làm việc» chủ thể=Người lao động:W q3 — lý do tach: Quyền không bị phân biệt đối xử, cưỡng bức lao động, quấy rối tình dục.
- Lỗi cổng LLM #2: âm tiết không có trong trich: ['được']

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D21.K1

Chữ: Hợp đồng lao động phải có những nội dung chủ yếu sau đây:

- **Lệch** ĐA#0 / LLM#0: cac_muc_con: ĐA='va' LLM='danh_sach'
  - ĐA: bo_qua cau_dan va «Hợp đồng lao động phải có những nội dung chủ yếu sau đây:»
  - LLM: bo_qua cau_dan danh_sach «Hợp đồng lao động phải có những nội dung chủ yếu sau đây:»

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D21.K1.a

Chữ: Tên, địa chỉ của người sử dụng lao động và họ tên, chức danh của người giao kết hợp đồng lao động bên phía người sử dụng lao động;
Câu dẫn: Hợp đồng lao động phải có những nội dung chủ yếu sau đây:

- **Lệch** ĐA#0 / LLM#0: doi_so: ĐA=['E'] LLM=[]
  - ĐA: menh_de/ket_luan [phai,khang_dinh] «có Tên, địa chỉ của người sử dụng lao động và họ tên, chức danh của người giao kết hợp đồng lao động bên phía người sử dụng lao động» chủ thể=Hợp đồng lao động:C q1 — lý do giu_chung: Một yêu cầu tập thể (thông tin nhận diện bên NSDLĐ); không tách chỉ vì có nhiều danh từ.
  - LLM: menh_de/ket_luan [phai,khang_dinh] «có tên, địa chỉ của người sử dụng lao động và họ tên, chức danh của người giao kết hợp đồng lao động bên phía người sử dụng lao động» chủ thể=Hợp đồng lao động:C q1

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D21.K1.b

Chữ: Họ tên, ngày tháng năm sinh, giới tính, nơi cư trú, số thẻ Căn cước công dân, Chứng minh nhân dân hoặc hộ chiếu của người giao kết hợp đồng lao động bên phía người lao động;
Câu dẫn: Hợp đồng lao động phải có những nội dung chủ yếu sau đây:

- **Lệch** ĐA#0 / LLM#0: doi_so: ĐA=['W'] LLM=[]
  - ĐA: menh_de/ket_luan [phai,khang_dinh] «có Họ tên, ngày tháng năm sinh, giới tính, nơi cư trú, số thẻ Căn cước công dân, Chứng minh nhân dân hoặc hộ chiếu của người giao kết hợp đồng lao động bên phía người lao động» chủ thể=Hợp đồng lao động:C q1 — lý do giu_chung: Một yêu cầu tập thể (thông tin nhận diện bên NLĐ); 'hoặc' nối danh từ (loại giấy tờ), không phải các điều kiện nên không dùng nhom_hoac.
  - LLM: menh_de/ket_luan [phai,khang_dinh] «có họ tên, ngày tháng năm sinh, giới tính, nơi cư trú, số thẻ Căn cước công dân, Chứng minh nhân dân hoặc hộ chiếu của người giao kết hợp đồng lao động bên phía người lao động» chủ thể=Hợp đồng lao động:C q1

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D35.K2

Chữ: Người lao động có quyền đơn phương chấm dứt hợp đồng lao động không cần báo trước trong trường hợp sau đây:

- **Chỉ ĐA có** #0: menh_de/ket_luan [duoc,khang_dinh] «đơn phương chấm dứt hợp đồng lao động không cần báo trước» chủ thể=Người lao động:W q1
- **Chỉ ĐA có** #1: bo_qua cau_dan hoac «trong trường hợp sau đây:»
- **Chỉ LLM có** #0: bo_qua cau_dan hoac «Người lao động có quyền đơn phương chấm dứt hợp đồng lao động không cần báo trướ»

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D35.K2.a

Chữ: Không được bố trí theo đúng công việc, địa điểm làm việc hoặc không được bảo đảm điều kiện làm việc theo thỏa thuận, trừ trường hợp quy định tại Điều 29 của Bộ luật này;
Câu dẫn: Người lao động có quyền đơn phương chấm dứt hợp đồng lao động không cần báo trước trong trường hợp sau đây:

- **Lệch** ĐA#1 / LLM#0: phuong_thuc: ĐA='khong' LLM='duoc'; menh_de: ĐA='được bố trí theo đúng địa điểm làm việc' LLM='được bố trí theo đúng công việc, địa điểm làm việc'; nhom_hoac: ĐA='h1' LLM=None
  - ĐA: menh_de/dieu_kien [khong,phu_dinh] «được bố trí theo đúng địa điểm làm việc» chủ thể=Người lao động:W q1 hoặc=h1
  - LLM: menh_de/dieu_kien [duoc,phu_dinh] «được bố trí theo đúng công việc, địa điểm làm việc» chủ thể=Người lao động:W q1 — lý do tach: Tách vế phủ định thứ nhất trong điều kiện.
- **Lệch** ĐA#2 / LLM#1: chua_ro: ĐA=['pham_vi_bo_ngu'] LLM=[]; phuong_thuc: ĐA='khong' LLM='duoc'; menh_de: ĐA='được bảo đảm điều kiện làm việc' LLM='được bảo đảm điều kiện làm việc theo thỏa thuận'; nhom_hoac: ĐA='h1' LLM=None; bo_ngu: ĐA=[('theo thỏa thuận', 'unknown')] LLM=[]
  - ĐA: menh_de/dieu_kien [khong,phu_dinh] «được bảo đảm điều kiện làm việc» chủ thể=Người lao động:W q1 bổ ngữ=[('theo thỏa thuận', 'unknown')] hoặc=h1 CHƯA RÕ=[('theo thỏa thuận', 'pham_vi_bo_ngu')] — lý do gan_bo_ngu: 'Theo thỏa thuận' đứng cuối vế thứ hai; về nghĩa có thể áp cho cả ba, chưa đủ căn cứ để chọn.
  - LLM: menh_de/dieu_kien [duoc,phu_dinh] «được bảo đảm điều kiện làm việc theo thỏa thuận» chủ thể=Người lao động:W q1 — lý do tach: Tách vế phủ định thứ hai trong điều kiện.
- **Lệch** ĐA#3 / LLM#2: gan_vao: ĐA='None (tức LLM#None)' LLM=0
  - ĐA: con_tro/ngoai_le → ['D29'] gắn=None
  - LLM: con_tro/ngoai_le → ['D29'] gắn=0 — lý do dan_chieu_mo: Dẫn chiếu ngoại trừ.
- **Chỉ ĐA có** #0: menh_de/dieu_kien [khong,phu_dinh] «được bố trí theo đúng công việc» chủ thể=Người lao động:W q1 hoặc=h1 — lý do tach: 'Không được bố trí' là bị động (khong + phu_dinh), không phải cấm; sai công việc hoặc sai địa điểm đều đủ một mình nên tách, nối 'hoặc'.
- **Chỉ LLM có** #3: menh_de/ket_luan [duoc,khang_dinh] «đơn phương chấm dứt hợp đồng lao động không cần báo trước» chủ thể=Người lao động:W q1 — lý do ke_thua: Kế thừa quyền đơn phương chấm dứt hợp đồng từ câu dẫn.
- Lỗi cổng LLM #0: chủ thể lấy từ cau_dan nhưng trich không có mẩu nào từ đó
- Lỗi cổng LLM #1: chủ thể lấy từ cau_dan nhưng trich không có mẩu nào từ đó

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D35.K2.b

Chữ: Không được trả đủ lương hoặc trả lương không đúng thời hạn, trừ trường hợp quy định tại khoản 4 Điều 97 của Bộ luật này;
Câu dẫn: Người lao động có quyền đơn phương chấm dứt hợp đồng lao động không cần báo trước trong trường hợp sau đây:

- **Lệch** ĐA#0 / LLM#0: phuong_thuc: ĐA='khong' LLM='duoc'; doi_so: ĐA=['A'] LLM=[]; nhom_hoac: ĐA='h1' LLM=None
  - ĐA: menh_de/dieu_kien [khong,phu_dinh] «được trả đủ lương» chủ thể=Người lao động:W q1 hoặc=h1 — lý do tach: Bị động 'không được trả' (khong + phu_dinh); trả thiếu và trả trễ là hai vi phạm riêng, nối 'hoặc'.
  - LLM: menh_de/dieu_kien [duoc,phu_dinh] «được trả đủ lương» chủ thể=Người lao động:W q1 — lý do tach: Tách vế trả đủ lương trong điều kiện.
- **Lệch** ĐA#1 / LLM#1: phuong_thuc: ĐA='khong' LLM='duoc'; menh_de: ĐA='trả lương đúng thời hạn' LLM='được trả lương đúng thời hạn'; doi_so: ĐA=['A'] LLM=[]; nhom_hoac: ĐA='h1' LLM=None
  - ĐA: menh_de/dieu_kien [khong,phu_dinh] «trả lương đúng thời hạn» chủ thể=Người lao động:W q1 hoặc=h1
  - LLM: menh_de/dieu_kien [duoc,phu_dinh] «được trả lương đúng thời hạn» chủ thể=Người lao động:W q1 — lý do tach: Tách vế trả lương đúng thời hạn trong điều kiện.
- **Lệch** ĐA#2 / LLM#2: gan_vao: ĐA='None (tức LLM#None)' LLM=0
  - ĐA: con_tro/ngoai_le → ['D97.K4'] gắn=None
  - LLM: con_tro/ngoai_le → ['D97.K4'] gắn=0 — lý do dan_chieu_mo: Dẫn chiếu ngoại trừ.
- **Chỉ LLM có** #3: menh_de/ket_luan [duoc,khang_dinh] «đơn phương chấm dứt hợp đồng lao động không cần báo trước» chủ thể=Người lao động:W q1 — lý do ke_thua: Kế thừa quyền đơn phương chấm dứt hợp đồng từ câu dẫn.
- Lỗi cổng LLM #0: chủ thể lấy từ cau_dan nhưng trich không có mẩu nào từ đó
- Lỗi cổng LLM #1: âm tiết không có trong trich: ['được']
- Lỗi cổng LLM #1: chủ thể lấy từ cau_dan nhưng trich không có mẩu nào từ đó

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D151.K1

Chữ: Người lao động nước ngoài làm việc tại Việt Nam là người có quốc tịch nước ngoài và phải đáp ứng các điều kiện sau đây:

- **Lệch** ĐA#0 / LLM#0: vai: ĐA='dieu_kien' LLM='ket_luan'; menh_de: ĐA='có quốc tịch nước ngoài' LLM='là người có quốc tịch nước ngoài'; chu_the.loai: ĐA='?' LLM='W'
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «có quốc tịch nước ngoài» chủ thể=người:? q1
  - LLM: menh_de/ket_luan [khong,khang_dinh] «là người có quốc tịch nước ngoài» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1
- **Lệch** ĐA#2 / LLM#1: cac_muc_con: ĐA='va' LLM='danh_sach'
  - ĐA: bo_qua cau_dan va «và phải đáp ứng các điều kiện sau đây:»
  - LLM: bo_qua cau_dan danh_sach «phải đáp ứng các điều kiện sau đây:»
- **Chỉ ĐA có** #1: menh_de/ket_luan [khong,khang_dinh] «là người lao động nước ngoài làm việc tại Việt Nam» chủ thể=-:None q1 — lý do giu_chung: Định nghĩa X là Y: các dấu hiệu là dieu_kien, kết luận là 'là X' (K5).

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D151.K1.a

Chữ: Đủ 18 tuổi trở lên và có năng lực hành vi dân sự đầy đủ;
Câu dẫn: Người lao động nước ngoài làm việc tại Việt Nam là người có quốc tịch nước ngoài và phải đáp ứng các điều kiện sau đây:

- **Lệch** ĐA#0 / LLM#0: vai: ĐA='ket_luan' LLM='dieu_kien'
  - ĐA: menh_de/ket_luan [phai,khang_dinh] «đủ 18 tuổi trở lên» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1 — lý do tach: Tuổi và năng lực hành vi dân sự kiểm được độc lập, thiếu cái nào cũng không đủ điều kiện.
  - LLM: menh_de/dieu_kien [phai,khang_dinh] «đủ 18 tuổi trở lên» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1 — lý do ke_thua: Kế thừa chủ thể từ câu dẫn khoản 1.
- **Lệch** ĐA#1 / LLM#1: vai: ĐA='ket_luan' LLM='dieu_kien'
  - ĐA: menh_de/ket_luan [phai,khang_dinh] «có năng lực hành vi dân sự đầy đủ» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1
  - LLM: menh_de/dieu_kien [phai,khang_dinh] «có năng lực hành vi dân sự đầy đủ» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1 — lý do ke_thua: Kế thừa chủ thể từ câu dẫn khoản 1.
- Lỗi cổng LLM #0: chủ thể lấy từ cau_dan nhưng trich không có mẩu nào từ đó
- Lỗi cổng LLM #1: chủ thể lấy từ cau_dan nhưng trich không có mẩu nào từ đó

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D151.K1.c

Chữ: Không phải là người đang trong thời gian chấp hành hình phạt hoặc chưa được xóa án tích hoặc đang trong thời gian bị truy cứu trách nhiệm hình sự theo quy định của pháp luật nước ngoài hoặc pháp luật Việt Nam;
Câu dẫn: Người lao động nước ngoài làm việc tại Việt Nam là người có quốc tịch nước ngoài và phải đáp ứng các điều kiện sau đây:

- **Lệch** ĐA#0 / LLM#0: vai: ĐA='ket_luan' LLM='dieu_kien'; bo_ngu: ĐA=[] LLM=[('theo quy định của pháp luật nước ngoài hoặc pháp luật Việt Nam', 'this_clause')]; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[1, 2])' LLM='q1'
  - ĐA: menh_de/ket_luan [phai,phu_dinh] «là người đang trong thời gian chấp hành hình phạt» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1 — lý do tach: Phủ định của 'A hoặc B hoặc C' = không A, không B, không C: ba yêu cầu cùng phải đúng (không dùng nhom_hoac).
  - LLM: menh_de/dieu_kien [phai,phu_dinh] «là người đang trong thời gian chấp hành hình phạt» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1 bổ ngữ=[('theo quy định của pháp luật nước ngoài hoặc pháp luật Việt Nam', 'this_clause')]
- **Lệch** ĐA#1 / LLM#1: vai: ĐA='ket_luan' LLM='dieu_kien'; cuc: ĐA='phu_dinh' LLM='khang_dinh'; menh_de: ĐA='là người chưa được xóa án tích' LLM='đã được xóa án tích'; bo_ngu: ĐA=[] LLM=[('theo quy định của pháp luật nước ngoài hoặc pháp luật Việt Nam', 'this_clause')]; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0, 2])' LLM='q2'
  - ĐA: menh_de/ket_luan [phai,phu_dinh] «là người chưa được xóa án tích» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1
  - LLM: menh_de/dieu_kien [phai,khang_dinh] «đã được xóa án tích» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q2 bổ ngữ=[('theo quy định của pháp luật nước ngoài hoặc pháp luật Việt Nam', 'this_clause')]
- **Lệch** ĐA#2 / LLM#2: vai: ĐA='ket_luan' LLM='dieu_kien'; menh_de: ĐA='là người đang trong thời gian bị truy cứu trách nhiệm hình sự' LLM='đang trong thời gian bị truy cứu trách nhiệm hình sự'; bo_ngu: ĐA=[] LLM=[('theo quy định của pháp luật nước ngoài hoặc pháp luật Việt Nam', 'this_clause')]; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0, 1])' LLM='q3'
  - ĐA: menh_de/ket_luan [phai,phu_dinh] «là người đang trong thời gian bị truy cứu trách nhiệm hình sự» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1
  - LLM: menh_de/dieu_kien [phai,phu_dinh] «đang trong thời gian bị truy cứu trách nhiệm hình sự» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q3 bổ ngữ=[('theo quy định của pháp luật nước ngoài hoặc pháp luật Việt Nam', 'this_clause')]
- **Chỉ ĐA có** #3: bo_qua dan_chieu_mo  «theo quy định của pháp luật nước ngoài hoặc pháp luật Việt Nam»
- Lỗi cổng LLM #0: chủ thể lấy từ cau_dan nhưng trich không có mẩu nào từ đó
- Lỗi cổng LLM #1: âm tiết không có trong trich: ['đã']
- Lỗi cổng LLM #1: chủ thể lấy từ cau_dan nhưng trich không có mẩu nào từ đó
- Lỗi cổng LLM #2: chủ thể lấy từ cau_dan nhưng trich không có mẩu nào từ đó

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D151.K1.d

Chữ: Có giấy phép lao động do cơ quan nhà nước có thẩm quyền của Việt Nam cấp, trừ trường hợp quy định tại Điều 154 của Bộ luật này.
Câu dẫn: Người lao động nước ngoài làm việc tại Việt Nam là người có quốc tịch nước ngoài và phải đáp ứng các điều kiện sau đây:

- **Lệch** ĐA#0 / LLM#0: vai: ĐA='ket_luan' LLM='dieu_kien'
  - ĐA: menh_de/ket_luan [phai,khang_dinh] «có giấy phép lao động» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1 bổ ngữ=[('do cơ quan nhà nước có thẩm quyền của Việt Nam cấp', 'this_clause')]
  - LLM: menh_de/dieu_kien [phai,khang_dinh] «có giấy phép lao động» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1 bổ ngữ=[('do cơ quan nhà nước có thẩm quyền của Việt Nam cấp', 'this_clause')]
- **Lệch** ĐA#1 / LLM#1: gan_vao: ĐA='None (tức LLM#None)' LLM=0
  - ĐA: con_tro/ngoai_le → ['D154'] gắn=None
  - LLM: con_tro/ngoai_le → ['D154'] gắn=0
- Lỗi cổng LLM #0: chủ thể lấy từ cau_dan nhưng trich không có mẩu nào từ đó

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D137.K1

Chữ: Người sử dụng lao động không được sử dụng người lao động làm việc ban đêm, làm thêm giờ và đi công tác xa trong trường hợp sau đây:

- **Chỉ ĐA có** #0: menh_de/ket_luan [cam,khang_dinh] «sử dụng người lao động làm việc ban đêm» chủ thể=Người sử dụng lao động:E q1 — lý do tach: 'Và' liệt kê ba hành vi cùng bị cấm; mỗi hành vi là một vi phạm riêng.
- **Chỉ ĐA có** #1: menh_de/ket_luan [cam,khang_dinh] «sử dụng người lao động làm thêm giờ» chủ thể=Người sử dụng lao động:E q1
- **Chỉ ĐA có** #2: menh_de/ket_luan [cam,khang_dinh] «sử dụng người lao động đi công tác xa» chủ thể=Người sử dụng lao động:E q1
- **Chỉ ĐA có** #3: bo_qua cau_dan hoac «trong trường hợp sau đây:»
- **Chỉ LLM có** #0: bo_qua cau_dan hoac «Người sử dụng lao động không được sử dụng người lao động làm việc ban đêm, làm t»

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D137.K1.a

Chữ: Mang thai từ tháng thứ 07 hoặc từ tháng thứ 06 nếu làm việc ở vùng cao, vùng sâu, vùng xa, biên giới, hải đảo;
Câu dẫn: Người sử dụng lao động không được sử dụng người lao động làm việc ban đêm, làm thêm giờ và đi công tác xa trong trường hợp sau đây:

- **Lệch** ĐA#0 / LLM#0: nhom_hoac: ĐA=None LLM='h1'; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[1])' LLM='q1'
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «mang thai từ tháng thứ 07» chủ thể=người lao động:W q1
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «mang thai từ tháng thứ 07» chủ thể=người lao động:W q1 hoặc=h1 — lý do tach: Tách trường hợp mang thai tháng thứ 07 hoặc tháng thứ 06 ở vùng đặc biệt.
- **Lệch** ĐA#1 / LLM#1: phuong_thuc: ĐA='khong' LLM=''; cuc: ĐA='khang_dinh' LLM=''; bo_ngu: ĐA=[] LLM=[('làm việc ở vùng cao, vùng sâu, vùng xa, biên giới, hải đảo', 'this_clause')]; quy_tac: ĐA='q2 (lệch nhóm với ĐA#[0])' LLM='q1'
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «mang thai từ tháng thứ 06» chủ thể=người lao động:W q2
  - LLM: menh_de/dieu_kien [,] «mang thai từ tháng thứ 06» chủ thể=người lao động:W q1 bổ ngữ=[('làm việc ở vùng cao, vùng sâu, vùng xa, biên giới, hải đảo', 'this_clause')] — lý do gan_bo_ngu: Điều kiện tháng thứ 06 đi kèm bổ ngữ địa bàn.
- **Chỉ ĐA có** #2: menh_de/dieu_kien [khong,khang_dinh] «làm việc ở vùng cao, vùng sâu, vùng xa, biên giới, hải đảo» chủ thể=người lao động:W q2 — lý do tach: "tháng 07" HOẶC ("tháng 06" VÀ làm ở vùng khó khăn): tách hai quy tắc q1, q2 (K2); "nếu ..." là điều kiện của q2, không phải bổ ngữ.
- **Chỉ LLM có** #2: menh_de/ket_luan [cam,khang_dinh] «sử dụng người lao động làm việc ban đêm, làm thêm giờ và đi công tác xa» chủ thể=Người sử dụng lao động:E q1 — lý do ke_thua: Kế thừa kết luận từ câu dẫn của khoản.
- Lỗi cổng LLM #0: chủ thể lấy từ cau_dan nhưng trich không có mẩu nào từ đó
- Lỗi cổng LLM #1: vai/phuong_thuc/cuc 'dieu_kien'/''/''
- Lỗi cổng LLM #1: chủ thể lấy từ cau_dan nhưng trich không có mẩu nào từ đó

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D146.K1

Chữ: Thời giờ làm việc của người chưa đủ 15 tuổi không được quá 04 giờ trong 01 ngày và 20 giờ trong 01 tuần; không được làm thêm giờ, làm việc vào ban đêm.

- **Lệch** ĐA#1 / LLM#0: menh_de: ĐA='Thời giờ làm việc quá 20 giờ trong 01 tuần' LLM='thời giờ làm việc không được quá 04 giờ trong 01 ngày và 20 giờ trong 01 tuần'; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[2, 3])' LLM='q1'
  - ĐA: menh_de/ket_luan [cam,khang_dinh] «Thời giờ làm việc quá 20 giờ trong 01 tuần» chủ thể=người chưa đủ 15 tuổi:W q1
  - LLM: menh_de/ket_luan [cam,khang_dinh] «thời giờ làm việc không được quá 04 giờ trong 01 ngày và 20 giờ trong 01 tuần» chủ thể=người chưa đủ 15 tuổi:W q1
- **Lệch** ĐA#2 / LLM#1: chua_ro: ĐA=['chu_the'] LLM=[]; chu_the.loai: ĐA=None LLM='W'; doi_so: ĐA=['W'] LLM=[]; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[1, 3])' LLM='q2'
  - ĐA: menh_de/ket_luan [cam,khang_dinh] «làm thêm giờ» chủ thể=-:None q1 CHƯA RÕ=[('chủ thể mang lệnh cấm', 'chu_the')]
  - LLM: menh_de/ket_luan [cam,khang_dinh] «làm thêm giờ» chủ thể=người chưa đủ 15 tuổi:W q2
- **Lệch** ĐA#3 / LLM#2: chua_ro: ĐA=['chu_the'] LLM=[]; chu_the.loai: ĐA=None LLM='W'; doi_so: ĐA=['W'] LLM=[]; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[1, 2])' LLM='q3'
  - ĐA: menh_de/ket_luan [cam,khang_dinh] «làm việc vào ban đêm» chủ thể=-:None q1 CHƯA RÕ=[('chủ thể mang lệnh cấm', 'chu_the')]
  - LLM: menh_de/ket_luan [cam,khang_dinh] «làm việc vào ban đêm» chủ thể=người chưa đủ 15 tuổi:W q3
- **Chỉ ĐA có** #0: menh_de/ket_luan [cam,khang_dinh] «Thời giờ làm việc quá 04 giờ trong 01 ngày» chủ thể=người chưa đủ 15 tuổi:W q1 — lý do tach: Giới hạn ngày và tuần kiểm độc lập; câu sau cấm hai hành vi riêng.

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D15.K2

Chữ: Tự do giao kết hợp đồng lao động nhưng không được trái pháp luật, thỏa ước lao động tập thể và đạo đức xã hội.

- **Lệch** ĐA#0 / LLM#0: chua_ro: ĐA=['chu_the'] LLM=[]; chu_the.loai: ĐA=None LLM='?'; doi_so: ĐA=['C'] LLM=[]
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «Tự do giao kết hợp đồng lao động» chủ thể=-:None q1 CHƯA RÕ=[('chủ thể', 'chu_the')]
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «tự do giao kết hợp đồng lao động» chủ thể=chủ thể giao kết:? q1
- **Lệch** ĐA#2 / LLM#1: vai: ĐA='ket_luan' LLM='ngoai_le'; menh_de: ĐA='trái thỏa ước lao động tập thể' LLM='trái pháp luật, thỏa ước lao động tập thể và đạo đức xã hội'; chu_the.loai: ĐA=None LLM='?'
  - ĐA: menh_de/ket_luan [cam,khang_dinh] «trái thỏa ước lao động tập thể» chủ thể=-:None q1
  - LLM: menh_de/ngoai_le [cam,khang_dinh] «trái pháp luật, thỏa ước lao động tập thể và đạo đức xã hội» chủ thể=chủ thể giao kết:? q1
- **Chỉ ĐA có** #1: menh_de/ket_luan [cam,khang_dinh] «trái pháp luật» chủ thể=-:None q1 — lý do tach: Trái luật, trái thỏa ước, trái đạo đức xã hội là ba căn cứ vi phạm riêng.
- **Chỉ ĐA có** #3: menh_de/ket_luan [cam,khang_dinh] «trái đạo đức xã hội» chủ thể=-:None q1
- Lỗi cổng LLM #0: chu_the.chu không nguyên văn 'chủ thể giao kết'
- Lỗi cổng LLM #0: chủ thể lấy từ tieu_de nhưng trich không có mẩu nào từ đó
- Lỗi cổng LLM #1: chu_the.chu không nguyên văn 'chủ thể giao kết'
- Lỗi cổng LLM #1: chủ thể lấy từ tieu_de nhưng trich không có mẩu nào từ đó

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D24.K3

Chữ: Không áp dụng thử việc đối với người lao động giao kết hợp đồng lao động có thời hạn dưới 01 tháng.

- **Lệch** ĐA#0 / LLM#0: cuc: ĐA='khang_dinh' LLM='phu_dinh'; chu_the.loai: ĐA=None LLM='W'; doi_so: ĐA=['W'] LLM=[]
  - ĐA: menh_de/ket_luan [khong_ap_dung,khang_dinh] «áp dụng thử việc» chủ thể=-:None q1
  - LLM: menh_de/ket_luan [khong_ap_dung,phu_dinh] «áp dụng thử việc» chủ thể=người lao động giao kết hợp đồng lao động có thời hạn dưới 01 tháng:W q1
- **Chỉ ĐA có** #1: menh_de/dieu_kien [khong,khang_dinh] «giao kết hợp đồng lao động có thời hạn dưới 01 tháng» chủ thể=người lao động:W q1

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D24.K1

Chữ: Người sử dụng lao động và người lao động có thể thỏa thuận nội dung thử việc ghi trong hợp đồng lao động hoặc thỏa thuận về thử việc bằng việc giao kết hợp đồng thử việc.

- **Lệch** ĐA#0 / LLM#0: doi_so: ĐA=['C'] LLM=[]; nhom_hoac: ĐA=None LLM='h1'; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[1])' LLM='q1'
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «thỏa thuận nội dung thử việc ghi trong hợp đồng lao động» chủ thể=Người sử dụng lao động và người lao động:('E', 'W') q1 — lý do tach: 'Hoặc' nối hai cách thỏa thuận được phép, không phải điều kiện: hai dòng duoc, không dùng nhom_hoac.
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «thỏa thuận nội dung thử việc ghi trong hợp đồng lao động» chủ thể=Người sử dụng lao động và người lao động:('E', 'W') q1 hoặc=h1 — lý do tach: Tách các phương án thỏa thuận thành các quy tắc độc lập theo quan hệ hoặc.
- **Lệch** ĐA#1 / LLM#1: doi_so: ĐA=['C'] LLM=[]; nhom_hoac: ĐA=None LLM='h1'; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0])' LLM='q2'
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «thỏa thuận về thử việc bằng việc giao kết hợp đồng thử việc» chủ thể=Người sử dụng lao động và người lao động:('E', 'W') q1
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «thỏa thuận về thử việc bằng việc giao kết hợp đồng thử việc» chủ thể=Người sử dụng lao động và người lao động:('E', 'W') q2 hoặc=h1 — lý do tach: Tách các phương án thỏa thuận thành các quy tắc độc lập theo quan hệ hoặc.
- Lỗi cổng LLM #1: trich không nguyên văn: 'Người sử dụng lao động và người lao động có thể thỏa thuận v'

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D3.K1

Chữ: Người lao động là người làm việc cho người sử dụng lao động theo thỏa thuận, được trả lương và chịu sự quản lý, điều hành, giám sát của người sử dụng lao động.
Độ tuổi lao động tối thiểu của người lao động là đủ 15 tuổi, trừ trường hợp quy định tại Mục 1 Chương XI của Bộ luật này.
Câu dẫn: Trong Bộ luật này, các từ ngữ dưới đây được hiểu như sau:

- **Lệch** ĐA#0 / LLM#1: menh_de: ĐA='là người làm việc cho người sử dụng lao động' LLM='làm việc cho người sử dụng lao động theo thỏa thuận'; chu_the.loai: ĐA='?' LLM='W'; bo_ngu: ĐA=[('theo thỏa thuận', 'this_clause')] LLM=[]
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «là người làm việc cho người sử dụng lao động» chủ thể=người:? q1 bổ ngữ=[('theo thỏa thuận', 'this_clause')] — lý do tach: Định nghĩa gồm ba dấu hiệu, mỗi dấu hiệu kiểm độc lập; thiếu một dấu hiệu thì không phải người lao động.
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «làm việc cho người sử dụng lao động theo thỏa thuận» chủ thể=Người lao động:W q1 — lý do tach: Dấu hiệu định nghĩa phần điều kiện làm việc.
- **Lệch** ĐA#1 / LLM#2: chu_the.loai: ĐA='?' LLM='W'; doi_so: ĐA=['A'] LLM=[]
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «được trả lương» chủ thể=người:? q1 — lý do tach: 'Được' ở đây là bị động trong định nghĩa, không phải quyền: phuong_thuc khong.
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «được trả lương» chủ thể=Người lao động:W q1 — lý do tach: Dấu hiệu định nghĩa phần điều kiện được trả lương.
- **Lệch** ĐA#2 / LLM#3: chu_the.loai: ĐA='?' LLM='W'
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «chịu sự quản lý, điều hành, giám sát của người sử dụng lao động» chủ thể=người:? q1 — lý do giu_chung: Quản lý, điều hành, giám sát cùng mô tả một quan hệ lệ thuộc; giữ chung.
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «chịu sự quản lý, điều hành, giám sát của người sử dụng lao động» chủ thể=Người lao động:W q1 — lý do tach: Dấu hiệu định nghĩa phần điều kiện chịu sự quản lý.
- **Lệch** ĐA#3 / LLM#4: chu_the.loai: ĐA=None LLM='W'; doi_so: ĐA=['?'] LLM=[]
  - ĐA: menh_de/ket_luan [khong,khang_dinh] «là người lao động» chủ thể=-:None q1 — lý do giu_chung: Định nghĩa X là Y: các dấu hiệu là dieu_kien, kết luận là 'là X' (K5).
  - LLM: menh_de/ket_luan [khong,khang_dinh] «là người lao động» chủ thể=Người lao động:W q1 — lý do tach: Kết luận định nghĩa khái niệm.
- **Lệch** ĐA#4 / LLM#5: menh_de: ĐA='Độ tuổi lao động tối thiểu là đủ 15 tuổi' LLM='Độ tuổi lao động tối thiểu của người lao động là đủ 15 tuổi'
  - ĐA: menh_de/ket_luan [khong,khang_dinh] «Độ tuổi lao động tối thiểu là đủ 15 tuổi» chủ thể=người lao động:W q2
  - LLM: menh_de/ket_luan [khong,khang_dinh] «Độ tuổi lao động tối thiểu của người lao động là đủ 15 tuổi» chủ thể=người lao động:W q2 — lý do tach: Quy định mức tuổi lao động tối thiểu.
- **Lệch** ĐA#5 / LLM#6: chua_ro: ĐA=['khac'] LLM=[]; targets: ĐA=[] LLM=['BLLD_45-2019.M1.C11']
  - ĐA: con_tro/ngoai_le → [] gắn=4 CHƯA RÕ=[('Mục 1 Chương XI của Bộ luật này', 'khac')] — lý do chua_ro: Dẫn chiếu rõ nhưng không có đích trong dan_chieu_1_2: vẫn là con_tro, targets để trống.
  - LLM: con_tro/ngoai_le → ['M1.C11'] gắn=5 — lý do tach: Ngoại lệ của quy tắc độ tuổi lao động tối thiểu.
- **Chỉ LLM có** #0: bo_qua cau_dan  «Trong Bộ luật này, các từ ngữ dưới đây được hiểu như sau:»
- Lỗi cổng LLM #6: target không có trong dẫn chiếu 1.2: BLLD_45-2019.M1.C11

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D9.K1

Chữ: Việc làm là hoạt động lao động tạo ra thu nhập mà pháp luật không cấm.

- **Lệch** ĐA#0 / LLM#0: menh_de: ĐA='hoạt động lao động tạo ra thu nhập' LLM='là hoạt động lao động tạo ra thu nhập'; chu_the.loai: ĐA=None LLM='?'; doi_so: ĐA=['?'] LLM=[]; bo_ngu: ĐA=[('mà pháp luật không cấm', 'this_clause')] LLM=[]
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «hoạt động lao động tạo ra thu nhập» chủ thể=-:None q1 bổ ngữ=[('mà pháp luật không cấm', 'this_clause')] — lý do gan_bo_ngu: 'Mà pháp luật không cấm' là dấu hiệu giới hạn của định nghĩa, ghi bổ ngữ; không phải dẫn chiếu tới quy phạm cụ thể.
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «là hoạt động lao động tạo ra thu nhập» chủ thể=Việc làm:? q1 — lý do tach: Tách định nghĩa thành điều kiện và kết luận.
- **Lệch** ĐA#1 / LLM#2: chu_the.loai: ĐA=None LLM='?'; doi_so: ĐA=['?'] LLM=[]
  - ĐA: menh_de/ket_luan [khong,khang_dinh] «là việc làm» chủ thể=-:None q1 — lý do giu_chung: Định nghĩa X là Y: các dấu hiệu là dieu_kien, kết luận là 'là X' (K5).
  - LLM: menh_de/ket_luan [khong,khang_dinh] «là việc làm» chủ thể=Việc làm:? q1 — lý do tach: Kết luận định nghĩa khái niệm.
- **Chỉ LLM có** #1: menh_de/dieu_kien [khong,phu_dinh] «pháp luật không cấm» chủ thể=pháp luật:? q1 — lý do tach: Điều kiện hợp pháp của việc làm.

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D10.K1

Chữ: Được tự do lựa chọn việc làm, làm việc cho bất kỳ người sử dụng lao động nào và ở bất kỳ nơi nào mà pháp luật không cấm.

- **Lệch** ĐA#0 / LLM#0: doi_so: ĐA=['J'] LLM=[]; bo_ngu: ĐA=[('mà pháp luật không cấm', 'group')] LLM=[]; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[1])' LLM='q1'
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «tự do lựa chọn việc làm» chủ thể=người lao động:W q1 bổ ngữ=[('mà pháp luật không cấm', 'group')] — lý do gan_bo_ngu: Chủ thể lấy từ tiêu đề; 'mà pháp luật không cấm' về nghĩa giới hạn cả nhóm quyền, không chỉ 'nơi nào'.
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «tự do lựa chọn việc làm» chủ thể=người lao động:W q1
- **Lệch** ĐA#1 / LLM#1: menh_de: ĐA='làm việc cho bất kỳ người sử dụng lao động nào' LLM='làm việc cho bất kỳ người sử dụng lao động nào và ở bất kỳ nơi nào mà pháp luật không cấm'; bo_ngu: ĐA=[('mà pháp luật không cấm', 'group')] LLM=[]; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0])' LLM='q2'
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «làm việc cho bất kỳ người sử dụng lao động nào» chủ thể=người lao động:W q1 bổ ngữ=[('mà pháp luật không cấm', 'group')] — lý do tach: Chọn người sử dụng lao động và chọn nơi làm việc bị hạn chế riêng được, nên tách.
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «làm việc cho bất kỳ người sử dụng lao động nào và ở bất kỳ nơi nào mà pháp luật không cấm» chủ thể=người lao động:W q2
- **Chỉ ĐA có** #2: menh_de/ket_luan [duoc,khang_dinh] «làm việc ở bất kỳ nơi nào» chủ thể=người lao động:W q1 bổ ngữ=[('mà pháp luật không cấm', 'group')]

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D4.K1

Chữ: Bảo đảm quyền và lợi ích hợp pháp, chính đáng của người lao động, người làm việc không có quan hệ lao động; khuyến khích những thỏa thuận bảo đảm cho người lao động có điều kiện thuận lợi hơn so với quy định của pháp luật về lao động.

- **Chỉ ĐA có** #0: bo_qua khong_quy_pham  «Bảo đảm quyền và lợi ích hợp pháp, chính đáng của người lao động, người làm việc»
- **Chỉ LLM có** #0: menh_de/ket_luan [phai,khang_dinh] «bảo đảm quyền và lợi ích hợp pháp, chính đáng của người lao động, người làm việc không có quan hệ lao động» chủ thể=Nhà nước:? q1 — lý do giu_chung: Chính sách của Nhà nước bao gồm các mục tiêu chung cần đạt được.
- **Chỉ LLM có** #1: menh_de/ket_luan [duoc,khang_dinh] «khuyến khích những thỏa thuận bảo đảm cho người lao động có điều kiện thuận lợi hơn so với quy định của pháp luật về lao động» chủ thể=Nhà nước:? q2 — lý do tach: Tách ý khuyến khích thỏa thuận thành một quy tắc độc lập.

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D9.K2

Chữ: Nhà nước, người sử dụng lao động và xã hội có trách nhiệm tham gia giải quyết việc làm, bảo đảm cho mọi người có khả năng lao động đều có cơ hội có việc làm.

- **Chỉ ĐA có** #0: bo_qua khong_quy_pham  «Nhà nước, người sử dụng lao động và xã hội có trách nhiệm tham gia giải quyết vi»
- **Chỉ LLM có** #0: menh_de/ket_luan [phai,khang_dinh] «tham gia giải quyết việc làm» chủ thể=Nhà nước, người sử dụng lao động và xã hội:('?', 'E') q1 — lý do tach: Tách nghĩa vụ thứ nhất của chủ thể.
- **Chỉ LLM có** #1: menh_de/ket_luan [phai,khang_dinh] «bảo đảm cho mọi người có khả năng lao động đều có cơ hội có việc làm» chủ thể=Nhà nước, người sử dụng lao động và xã hội:('?', 'E') q2 — lý do tach: Tách nghĩa vụ thứ hai của chủ thể.

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D14.K1

Chữ: Hợp đồng lao động phải được giao kết bằng văn bản và được làm thành 02 bản, người lao động giữ 01 bản, người sử dụng lao động giữ 01 bản, trừ trường hợp quy định tại khoản 2 Điều này.
Hợp đồng lao động được giao kết thông qua phương tiện điện tử dưới hình thức thông điệp dữ liệu theo quy định của pháp luật về giao dịch điện tử có giá trị như hợp đồng lao động bằng văn bản.

- **Lệch** ĐA#2 / LLM#4: gan_vao: ĐA='None (tức LLM#None)' LLM=0
  - ĐA: con_tro/ngoai_le → ['D14.K2'] gắn=None
  - LLM: con_tro/ngoai_le → ['D14.K2'] gắn=0
- **Lệch** ĐA#3 / LLM#5: vai: ĐA='dieu_kien' LLM='ket_luan'; chua_ro: ĐA=[] LLM=['pham_vi_bo_ngu']; phuong_thuc: ĐA='khong' LLM=''; cuc: ĐA='khang_dinh' LLM=''; bo_ngu: ĐA=[] LLM=[('theo quy định của pháp luật về giao dịch điện tử', 'unknown')]
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «được giao kết thông qua phương tiện điện tử dưới hình thức thông điệp dữ liệu» chủ thể=Hợp đồng lao động:C q2
  - LLM: menh_de/ket_luan [,] «được giao kết thông qua phương tiện điện tử dưới hình thức thông điệp dữ liệu» chủ thể=Hợp đồng lao động:C q2 bổ ngữ=[('theo quy định của pháp luật về giao dịch điện tử', 'unknown')] CHƯA RÕ=[('bo_ngu', 'pham_vi_bo_ngu')] — lý do giu_chung: Giữ nguyên điều kiện hợp đồng điện tử.
- **Chỉ ĐA có** #1: menh_de/ket_luan [phai,khang_dinh] «được làm thành 02 bản, người lao động giữ 01 bản, người sử dụng lao động giữ 01 bản» chủ thể=Hợp đồng lao động:C q1 — lý do giu_chung: Số bản và việc mỗi bên giữ một bản là một yêu cầu tập thể về lập và giao bản hợp đồng.
- **Chỉ ĐA có** #5: bo_qua dan_chieu_ngoai  «theo quy định của pháp luật về giao dịch điện tử»
- **Chỉ LLM có** #1: menh_de/ket_luan [phai,khang_dinh] «được làm thành 02 bản» chủ thể=Hợp đồng lao động:C q1 — lý do tach: Tách ý làm thành 02 bản.
- **Chỉ LLM có** #2: menh_de/ket_luan [phai,khang_dinh] «giữ 01 bản» chủ thể=người lao động:W q1
- **Chỉ LLM có** #3: menh_de/ket_luan [phai,khang_dinh] «giữ 01 bản» chủ thể=người sử dụng lao động:E q1
- Lỗi cổng LLM #5: vai/phuong_thuc/cuc 'ket_luan'/''/''
- Lỗi cổng LLM #6: trich không nguyên văn: 'Hợp đồng lao động... có giá trị như hợp đồng lao động bằng v'

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D14.K2

Chữ: Hai bên có thể giao kết hợp đồng lao động bằng lời nói đối với hợp đồng có thời hạn dưới 01 tháng, trừ trường hợp quy định tại khoản 2 Điều 18, điểm a khoản 1 Điều 145 và khoản 1 Điều 162 của Bộ luật này.

- **Lệch** ĐA#0 / LLM#0: menh_de: ĐA='giao kết hợp đồng lao động bằng lời nói' LLM='được giao kết hợp đồng lao động bằng lời nói'
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «giao kết hợp đồng lao động bằng lời nói» chủ thể=Hai bên:('E', 'W') q1
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «được giao kết hợp đồng lao động bằng lời nói» chủ thể=Hai bên:('E', 'W') q1
- **Lệch** ĐA#1 / LLM#1: menh_de: ĐA='có thời hạn dưới 01 tháng' LLM='đối với hợp đồng có thời hạn dưới 01 tháng'; chu_the.loai: ĐA='C' LLM=('E', 'W'); doi_so: ĐA=[] LLM=['C']
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «có thời hạn dưới 01 tháng» chủ thể=hợp đồng:C q1
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «đối với hợp đồng có thời hạn dưới 01 tháng» chủ thể=Hai bên:('E', 'W') q1
- **Lệch** ĐA#2 / LLM#2: gan_vao: ĐA='None (tức LLM#None)' LLM=0
  - ĐA: con_tro/ngoai_le → ['D18.K2', 'D145.K1.a', 'D162.K1'] gắn=None — lý do tach: Một chỗ 'trừ trường hợp' nên một dòng con_tro, ba đích; mỗi đích là một ngoại lệ độc lập.
  - LLM: con_tro/ngoai_le → ['D18.K2', 'D145.K1.a', 'D162.K1'] gắn=0
- Lỗi cổng LLM #0: âm tiết không có trong trich: ['được']

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D113.K1

Chữ: Người lao động làm việc đủ 12 tháng cho một người sử dụng lao động thì được nghỉ hằng năm, hưởng nguyên lương theo hợp đồng lao động như sau:

- **Chỉ ĐA có** #1: menh_de/ket_luan [duoc,khang_dinh] «nghỉ hằng năm» chủ thể=Người lao động:W q1 — lý do tach: Được nghỉ và được hưởng nguyên lương là hai quyền vi phạm riêng được.
- **Chỉ ĐA có** #2: menh_de/ket_luan [duoc,khang_dinh] «hưởng nguyên lương theo hợp đồng lao động» chủ thể=Người lao động:W q1
- **Chỉ ĐA có** #3: bo_qua cau_dan danh_sach «như sau:»
- **Chỉ LLM có** #1: bo_qua cau_dan  «thì được nghỉ hằng năm, hưởng nguyên lương theo hợp đồng lao động như sau:»

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D113.K1.a

Chữ: 12 ngày làm việc đối với người làm công việc trong điều kiện bình thường;
Câu dẫn: Người lao động làm việc đủ 12 tháng cho một người sử dụng lao động thì được nghỉ hằng năm, hưởng nguyên lương theo hợp đồng lao động như sau:

- **Lệch** ĐA#0 / LLM#0: menh_de: ĐA='nghỉ hằng năm 12 ngày làm việc' LLM='được nghỉ hằng năm 12 ngày làm việc, hưởng nguyên lương'; doi_so: ĐA=['D'] LLM=[]; bo_ngu: ĐA=[] LLM=[('đối với người làm công việc trong điều kiện bình thường', 'this_clause')]
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «nghỉ hằng năm 12 ngày làm việc» chủ thể=Người lao động:W q1 — lý do ke_thua: Mục con chỉ là con số; vị ngữ 'được nghỉ hằng năm' và chủ thể kế thừa từ câu dẫn.
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «được nghỉ hằng năm 12 ngày làm việc, hưởng nguyên lương» chủ thể=Người lao động:W q1 bổ ngữ=[('đối với người làm công việc trong điều kiện bình thường', 'this_clause')] — lý do giu_chung: Kết thừa điều kiện từ khoản 1, xác định số ngày nghỉ cho điều kiện bình thường.
- **Chỉ ĐA có** #1: menh_de/dieu_kien [khong,khang_dinh] «làm công việc trong điều kiện bình thường» chủ thể=người:W q1

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D129.K1

Chữ: Người lao động làm hư hỏng dụng cụ, thiết bị hoặc có hành vi khác gây thiệt hại tài sản của người sử dụng lao động thì phải bồi thường theo quy định của pháp luật hoặc nội quy lao động của người sử dụng lao động.
Trường hợp người lao động gây thiệt hại không nghiêm trọng do sơ suất với giá trị không quá 10 tháng lương tối thiểu vùng do Chính phủ công bố được áp dụng tại nơi người lao động làm việc thì người lao động phải bồi thường nhiều nhất là 03 tháng tiền lương và bị khấu trừ hằng tháng vào lương theo quy định tại khoản 3 Điều 102 của Bộ luật này.

- **Lệch** ĐA#0 / LLM#0: doi_so: ĐA=[] LLM=['E']; nhom_hoac: ĐA='h1' LLM=None; bo_ngu: ĐA=[('của người sử dụng lao động', 'group')] LLM=[]
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «làm hư hỏng dụng cụ, thiết bị» chủ thể=Người lao động:W q1 bổ ngữ=[('của người sử dụng lao động', 'group')] hoặc=h1 — lý do gan_bo_ngu: 'Của người sử dụng lao động' về nghĩa áp cả cho dụng cụ, thiết bị (tài sản của NSDLĐ).
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «làm hư hỏng dụng cụ, thiết bị» chủ thể=Người lao động:W q1
- **Lệch** ĐA#1 / LLM#1: nhom_hoac: ĐA='h1' LLM=None
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «có hành vi khác gây thiệt hại tài sản của người sử dụng lao động» chủ thể=Người lao động:W q1 hoặc=h1
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «có hành vi khác gây thiệt hại tài sản của người sử dụng lao động» chủ thể=Người lao động:W q1
- **Lệch** ĐA#2 / LLM#2: menh_de: ĐA='bồi thường' LLM='phải bồi thường'; doi_so: ĐA=[] LLM=['E']
  - ĐA: menh_de/ket_luan [phai,khang_dinh] «bồi thường» chủ thể=Người lao động:W q1
  - LLM: menh_de/ket_luan [phai,khang_dinh] «phải bồi thường» chủ thể=Người lao động:W q1
- **Lệch** ĐA#7 / LLM#5: menh_de: ĐA='bồi thường nhiều nhất là 03 tháng tiền lương' LLM='phải bồi thường nhiều nhất là 03 tháng tiền lương'; doi_so: ĐA=['A'] LLM=[]
  - ĐA: menh_de/ket_luan [phai,khang_dinh] «bồi thường nhiều nhất là 03 tháng tiền lương» chủ thể=người lao động:W q2
  - LLM: menh_de/ket_luan [phai,khang_dinh] «phải bồi thường nhiều nhất là 03 tháng tiền lương» chủ thể=người lao động:W q2
- **Lệch** ĐA#8 / LLM#6: doi_so: ĐA=['A'] LLM=[]
  - ĐA: menh_de/ket_luan [phai,khang_dinh] «bị khấu trừ hằng tháng vào lương» chủ thể=người lao động:W q2
  - LLM: menh_de/ket_luan [phai,khang_dinh] «bị khấu trừ hằng tháng vào lương» chủ thể=người lao động:W q2
- **Chỉ ĐA có** #4: menh_de/dieu_kien [khong,khang_dinh] «gây thiệt hại không nghiêm trọng» chủ thể=người lao động:W q2 — lý do tach: Ba điều kiện cộng dồn (không nghiêm trọng, do sơ suất, giá trị ≤ 10 tháng lương tối thiểu vùng), kiểm độc lập; 'không' nằm trong nội dung nên cuc khang_dinh.
- **Chỉ ĐA có** #5: menh_de/dieu_kien [khong,khang_dinh] «gây thiệt hại do sơ suất» chủ thể=người lao động:W q2
- **Chỉ ĐA có** #6: menh_de/dieu_kien [khong,khang_dinh] «giá trị không quá 10 tháng lương tối thiểu vùng» chủ thể=-:None q2 bổ ngữ=[('do Chính phủ công bố được áp dụng tại nơi người lao động làm việc', 'this_clause')]
- **Chỉ LLM có** #4: menh_de/dieu_kien [khong,khang_dinh] «gây thiệt hại không nghiêm trọng do sơ suất với giá trị không quá 10 tháng lương tối thiểu vùng do Chính phủ công bố được áp dụng tại nơi người lao động làm việc» chủ thể=người lao động:W q2

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D108

Chữ: Người sử dụng lao động có quyền yêu cầu người lao động làm thêm giờ vào bất kỳ ngày nào mà không bị giới hạn về số giờ làm thêm theo quy định tại Điều 107 của Bộ luật này và người lao động không được từ chối trong trường hợp sau đây:

- **Lệch** ĐA#0 / LLM#0: menh_de: ĐA='yêu cầu người lao động làm thêm giờ vào bất kỳ ngày nào' LLM='yêu cầu người lao động làm thêm giờ'; doi_so: ĐA=['W', 'D'] LLM=['W']; bo_ngu: ĐA=[] LLM=[('vào bất kỳ ngày nào', 'this_clause')]; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[3])' LLM='q1'
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «yêu cầu người lao động làm thêm giờ vào bất kỳ ngày nào» chủ thể=Người sử dụng lao động:E q1
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «yêu cầu người lao động làm thêm giờ» chủ thể=Người sử dụng lao động:E q1 bổ ngữ=[('vào bất kỳ ngày nào', 'this_clause')]
- **Lệch** ĐA#2 / LLM#1: gan_vao: ĐA='1 (tức LLM#dòng chưa ghép)' LLM=0
  - ĐA: con_tro/ket_luan → ['D107'] gắn=1 — lý do gan_bo_ngu: Không phải 'trừ trường hợp': Điều 108 gạt giới hạn của Điều 107; con trỏ gắn vế 'không bị giới hạn về số giờ làm thêm'.
  - LLM: con_tro/ket_luan → ['D107'] gắn=0 — lý do ke_thua: Dẫn chiếu ngoại lệ giới hạn số giờ làm thêm.
- **Lệch** ĐA#3 / LLM#2: quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0])' LLM='q2'
  - ĐA: menh_de/ket_luan [cam,khang_dinh] «từ chối» chủ thể=người lao động:W q1 — lý do tach: Câu dẫn chứa hai kết luận cho hai chủ thể: quyền của E và cấm từ chối đối với W.
  - LLM: menh_de/ket_luan [cam,khang_dinh] «từ chối» chủ thể=người lao động:W q2
- **Chỉ ĐA có** #1: menh_de/ket_luan [khong,phu_dinh] «bị giới hạn về số giờ làm thêm» chủ thể=Người sử dụng lao động:E q1

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D108.K1

Chữ: Thực hiện lệnh động viên, huy động bảo đảm nhiệm vụ quốc phòng, an ninh theo quy định của pháp luật;
Câu dẫn: Người sử dụng lao động có quyền yêu cầu người lao động làm thêm giờ vào bất kỳ ngày nào mà không bị giới hạn về số giờ làm thêm theo quy định tại Điều 107 của Bộ luật này và người lao động không được từ chối trong trường hợp sau đây:

- **Lệch** ĐA#0 / LLM#0: chu_the.loai: ĐA=None LLM='W'; bo_ngu: ĐA=[] LLM=[('theo quy định của pháp luật', 'this_clause')]
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «Thực hiện lệnh động viên, huy động bảo đảm nhiệm vụ quốc phòng, an ninh» chủ thể=-:None q1 — lý do giu_chung: Một tình huống (thực hiện lệnh động viên, huy động vì quốc phòng, an ninh); chủ thể là tình huống làm thêm giờ, không gán cho W hay E.
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «Thực hiện lệnh động viên, huy động bảo đảm nhiệm vụ quốc phòng, an ninh» chủ thể=người lao động:W q2 bổ ngữ=[('theo quy định của pháp luật', 'this_clause')]
- **Chỉ ĐA có** #1: bo_qua dan_chieu_mo  «theo quy định của pháp luật»
- Lỗi cổng LLM #0: chủ thể lấy từ cau_dan nhưng trich không có mẩu nào từ đó

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

