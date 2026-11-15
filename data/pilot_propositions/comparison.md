# So sánh 1.6A thí điểm (menh-de-1) với đáp án nháp

Mỗi đơn vị có chỗ lệch: dòng của đáp án (ĐA) và của LLM; người dùng phán bên nào đúng. Đơn vị khớp hết không liệt kê.

- Dòng: ĐA 97, LLM 100; ghép được 83, chỉ ĐA có 14, chỉ LLM có 17.
- Lỗi cổng của LLM: 0. Câu dẫn lọt thành mệnh đề (ước bằng máy): 0.
- Field khớp trên các dòng ghép được: {'bo_qua.ly_do.ma': '8/9', 'bo_qua.cac_muc_con': '8/9', 'menh_de.vai': '66/66', 'menh_de.menh_de': '55/66', 'menh_de.phuong_thuc': '64/66', 'menh_de.cuc': '66/66', 'menh_de.chu_the.loai': '54/66', 'menh_de.doi_so': '42/66', 'menh_de.bo_ngu': '52/66', 'menh_de.nhom_hoac': '66/66', 'menh_de.chua_ro': '59/66', 'menh_de.quy_tac': '41/66', 'con_tro.vai': '0/8', 'con_tro.targets': '8/8', 'con_tro.gan_vao': '7/8', 'con_tro.chua_ro': '8/8'}.
- Chưa rõ của LLM theo nguyên nhân: {'pham_vi_bo_ngu': 2, 'chu_the': 1, 'khac': 1}.
- Đây là so với đáp án NHÁP: chỉ thành số đo sau khi người dùng phán xong các chỗ lệch (A38 K10).

## D5.K1.a

Chữ: Làm việc; tự do lựa chọn việc làm, nơi làm việc, nghề nghiệp, học nghề, nâng cao trình độ nghề nghiệp; không bị phân biệt đối xử, cưỡng bức lao động, quấy rối tình dục tại nơi làm việc;
Câu dẫn: Người lao động có các quyền sau đây:

- **Lệch** ĐA#0 / LLM#0: quy_tac: ĐA='q1 (lệch nhóm với ĐA#[1, 2, 3, 5, 6, 7, 8])' LLM='q1'
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «làm việc» chủ thể=Người lao động:W q1
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «làm việc» chủ thể=Người lao động:W q1 — lý do ke_thua: Mục chỉ có chữ 'Làm việc', chủ thể và phương thức 'có quyền' kế thừa từ câu dẫn.
- **Lệch** ĐA#1 / LLM#1: quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0, 2, 3, 5, 6, 7, 8])' LLM='q2'
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «tự do lựa chọn việc làm» chủ thể=Người lao động:W q1 — lý do tach: Tự do chọn việc làm, nơi làm việc, nghề nghiệp là ba quyền riêng: hạn chế từng cái là vi phạm riêng.
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «tự do lựa chọn việc làm» chủ thể=Người lao động:W q2 — lý do tach: Tự do chọn việc làm kiểm được độc lập với tự do chọn nơi làm việc, nghề nghiệp, học nghề; vi phạm từng quyền có ý nghĩa pháp lý riêng.
- **Lệch** ĐA#2 / LLM#2: quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0, 1, 3, 5, 6, 7, 8])' LLM='q3'
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «tự do lựa chọn nơi làm việc» chủ thể=Người lao động:W q1
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «tự do lựa chọn nơi làm việc» chủ thể=Người lao động:W q3 — lý do tach: Chữ 'tự do lựa chọn' đứng đầu chuỗi nên hiểu cho từng mục; tự do chọn nơi làm việc là một quyền riêng.
- **Lệch** ĐA#3 / LLM#3: doi_so: ĐA=['J'] LLM=['?']; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0, 1, 2, 5, 6, 7, 8])' LLM='q4'
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «tự do lựa chọn nghề nghiệp» chủ thể=Người lao động:W q1
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «tự do lựa chọn nghề nghiệp» chủ thể=Người lao động:W q4 — lý do tach: Chữ 'tự do lựa chọn' đứng đầu chuỗi nên hiểu cho từng mục; tự do chọn nghề nghiệp là một quyền riêng.
- **Lệch** ĐA#5 / LLM#5: chua_ro: ĐA=['pham_vi_bo_ngu'] LLM=[]; menh_de: ĐA='nâng cao trình độ nghề nghiệp' LLM='tự do lựa chọn nâng cao trình độ nghề nghiệp'; doi_so: ĐA=[] LLM=['?']; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0, 1, 2, 3, 6, 7, 8])' LLM='q6'
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «nâng cao trình độ nghề nghiệp» chủ thể=Người lao động:W q1 CHƯA RÕ=[('tự do lựa chọn', 'pham_vi_bo_ngu')]
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «tự do lựa chọn nâng cao trình độ nghề nghiệp» chủ thể=Người lao động:W q6 — lý do tach: Chữ 'tự do lựa chọn' đứng đầu chuỗi nên hiểu cho từng mục; tự do nâng cao trình độ nghề nghiệp là một quyền riêng.
- **Lệch** ĐA#6 / LLM#6: doi_so: ĐA=['?'] LLM=[]; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0, 1, 2, 3, 5, 7, 8])' LLM='q7'
  - ĐA: menh_de/ket_luan [duoc,phu_dinh] «bị phân biệt đối xử» chủ thể=Người lao động:W q1 — lý do tach: 'Không bị' là quyền được bảo vệ (duoc + phu_dinh); ba hành vi bị cấm riêng nên tách ba dòng.
  - LLM: menh_de/ket_luan [duoc,phu_dinh] «bị phân biệt đối xử» chủ thể=Người lao động:W q7 — lý do tach: Chữ 'không bị' đứng đầu chuỗi nên hiểu cho từng mục; quyền không bị phân biệt đối xử kiểm được độc lập, là bị động phủ định nên cuc phu_dinh chứ không phải cấm.
- **Lệch** ĐA#7 / LLM#7: doi_so: ĐA=['?'] LLM=[]; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0, 1, 2, 3, 5, 6, 8])' LLM='q8'
  - ĐA: menh_de/ket_luan [duoc,phu_dinh] «bị cưỡng bức lao động» chủ thể=Người lao động:W q1
  - LLM: menh_de/ket_luan [duoc,phu_dinh] «bị cưỡng bức lao động» chủ thể=Người lao động:W q8 — lý do tach: Chữ 'không bị' đứng đầu chuỗi nên hiểu cho từng mục; quyền không bị cưỡng bức lao động kiểm được độc lập.
- **Lệch** ĐA#8 / LLM#8: chua_ro: ĐA=[] LLM=['pham_vi_bo_ngu']; doi_so: ĐA=['?'] LLM=[]; bo_ngu: ĐA=[('tại nơi làm việc', 'this_clause')] LLM=[('tại nơi làm việc', 'unknown')]; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0, 1, 2, 3, 5, 6, 7])' LLM='q9'
  - ĐA: menh_de/ket_luan [duoc,phu_dinh] «bị quấy rối tình dục» chủ thể=Người lao động:W q1 bổ ngữ=[('tại nơi làm việc', 'this_clause')] — lý do gan_bo_ngu: 'Tại nơi làm việc' gắn với 'quấy rối tình dục' (khái niệm định nghĩa riêng); phân biệt đối xử và cưỡng bức lao động bị cấm ở mọi nơi.
  - LLM: menh_de/ket_luan [duoc,phu_dinh] «bị quấy rối tình dục» chủ thể=Người lao động:W q9 bổ ngữ=[('tại nơi làm việc', 'unknown')] CHƯA RÕ=[('tại nơi làm việc', 'pham_vi_bo_ngu')] — lý do gan_bo_ngu: Cụm 'tại nơi làm việc' đứng cuối chuỗi, chữ không cho căn cứ để biết chỉ mục cuối hay cả nhóm nên để scope unknown và không rải sang hai mục trước.
- **Chỉ ĐA có** #4: menh_de/ket_luan [duoc,khang_dinh] «học nghề» chủ thể=Người lao động:W q1 CHƯA RÕ=[('tự do lựa chọn', 'pham_vi_bo_ngu')]
- **Chỉ LLM có** #4: menh_de/ket_luan [duoc,khang_dinh] «tự do lựa chọn học nghề» chủ thể=Người lao động:W q5 — lý do tach: Chữ 'tự do lựa chọn' đứng đầu chuỗi nên hiểu cho từng mục; tự do học nghề là một quyền riêng.

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D21.K1

Chữ: Hợp đồng lao động phải có những nội dung chủ yếu sau đây:

- **Lệch** ĐA#0 / LLM#0: cac_muc_con: ĐA='va' LLM='danh_sach'
  - ĐA: bo_qua cau_dan va «Hợp đồng lao động phải có những nội dung chủ yếu sau đây:»
  - LLM: bo_qua cau_dan danh_sach «Hợp đồng lao động phải có những nội dung chủ yếu sau đây»

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D21.K1.a

Chữ: Tên, địa chỉ của người sử dụng lao động và họ tên, chức danh của người giao kết hợp đồng lao động bên phía người sử dụng lao động;
Câu dẫn: Hợp đồng lao động phải có những nội dung chủ yếu sau đây:

- **Lệch** ĐA#0 / LLM#1: menh_de: ĐA='có Tên, địa chỉ của người sử dụng lao động và họ tên, chức danh của người giao kết hợp đồng lao động bên phía người sử dụng lao động' LLM='có họ tên, chức danh của người giao kết hợp đồng lao động bên phía người sử dụng lao động'
  - ĐA: menh_de/ket_luan [phai,khang_dinh] «có Tên, địa chỉ của người sử dụng lao động và họ tên, chức danh của người giao kết hợp đồng lao động bên phía người sử dụng lao động» chủ thể=Hợp đồng lao động:C q1 — lý do giu_chung: Một yêu cầu tập thể (thông tin nhận diện bên NSDLĐ); không tách chỉ vì có nhiều danh từ.
  - LLM: menh_de/ket_luan [phai,khang_dinh] «có họ tên, chức danh của người giao kết hợp đồng lao động bên phía người sử dụng lao động» chủ thể=Hợp đồng lao động:C q2 — lý do tach: Thông tin về người giao kết bên phía người sử dụng lao động là nội dung riêng, tách khỏi thông tin về chính người sử dụng lao động.
- **Chỉ LLM có** #0: menh_de/ket_luan [phai,khang_dinh] «có tên, địa chỉ của người sử dụng lao động» chủ thể=Hợp đồng lao động:C q1 — lý do tach: Thông tin về người sử dụng lao động tách khỏi thông tin về người giao kết bên phía người sử dụng lao động vì là hai đối tượng khác nhau, thiếu mỗi nội dung có ý nghĩa pháp lý riêng; tên và địa chỉ cùng xác định người sử dụng lao động nên giữ chung.

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D35.K2.a

Chữ: Không được bố trí theo đúng công việc, địa điểm làm việc hoặc không được bảo đảm điều kiện làm việc theo thỏa thuận, trừ trường hợp quy định tại Điều 29 của Bộ luật này;
Câu dẫn: Người lao động có quyền đơn phương chấm dứt hợp đồng lao động không cần báo trước trong trường hợp sau đây:

- **Lệch** ĐA#1 / LLM#1: doi_so: ĐA=[] LLM=['?']
  - ĐA: menh_de/dieu_kien [khong,phu_dinh] «được bố trí theo đúng địa điểm làm việc» chủ thể=Người lao động:W q1 hoặc=h1
  - LLM: menh_de/dieu_kien [khong,phu_dinh] «được bố trí theo đúng địa điểm làm việc» chủ thể=Người lao động:W q1 hoặc=h1 — lý do tach: Tách khỏi 'công việc' vì địa điểm làm việc là nội dung độc lập, kế thừa 'Không được bố trí theo đúng' từ đầu chuỗi.
- **Lệch** ĐA#2 / LLM#2: chua_ro: ĐA=['pham_vi_bo_ngu'] LLM=[]; doi_so: ĐA=[] LLM=['?']; bo_ngu: ĐA=[('theo thỏa thuận', 'unknown')] LLM=[('theo thỏa thuận', 'this_clause')]
  - ĐA: menh_de/dieu_kien [khong,phu_dinh] «được bảo đảm điều kiện làm việc» chủ thể=Người lao động:W q1 bổ ngữ=[('theo thỏa thuận', 'unknown')] hoặc=h1 CHƯA RÕ=[('theo thỏa thuận', 'pham_vi_bo_ngu')] — lý do gan_bo_ngu: 'Theo thỏa thuận' đứng cuối vế thứ hai; về nghĩa có thể áp cho cả ba, chưa đủ căn cứ để chọn.
  - LLM: menh_de/dieu_kien [khong,phu_dinh] «được bảo đảm điều kiện làm việc» chủ thể=Người lao động:W q1 bổ ngữ=[('theo thỏa thuận', 'this_clause')] hoặc=h1 — lý do gan_bo_ngu: 'theo thỏa thuận' đứng sau vế riêng 'không được bảo đảm điều kiện làm việc' nên chỉ gắn vào mục cuối, không rải sang công việc và địa điểm làm việc.
- **Lệch** ĐA#3 / LLM#3: vai: ĐA='ngoai_le' LLM=''
  - ĐA: con_tro/ngoai_le → ['D29'] gắn=None
  - LLM: con_tro/ → ['D29'] gắn=None

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D35.K2.b

Chữ: Không được trả đủ lương hoặc trả lương không đúng thời hạn, trừ trường hợp quy định tại khoản 4 Điều 97 của Bộ luật này;
Câu dẫn: Người lao động có quyền đơn phương chấm dứt hợp đồng lao động không cần báo trước trong trường hợp sau đây:

- **Lệch** ĐA#1 / LLM#1: chua_ro: ĐA=[] LLM=['chu_the']; chu_the.loai: ĐA='W' LLM=None; doi_so: ĐA=['A'] LLM=['A', 'D']
  - ĐA: menh_de/dieu_kien [khong,phu_dinh] «trả lương đúng thời hạn» chủ thể=Người lao động:W q1 hoặc=h1
  - LLM: menh_de/dieu_kien [khong,phu_dinh] «trả lương đúng thời hạn» chủ thể=-:None q1 hoặc=h1 CHƯA RÕ=[("chủ thể của vế 'trả lương không đúng thời hạn'", 'chu_the')] — lý do chua_ro: Vế 'trả lương không đúng thời hạn' là chủ động nhưng chữ không nêu bên trả lương nên không tự gán chủ thể.
- **Lệch** ĐA#2 / LLM#2: vai: ĐA='ngoai_le' LLM=''
  - ĐA: con_tro/ngoai_le → ['D97.K4'] gắn=None
  - LLM: con_tro/ → ['D97.K4'] gắn=None

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D151.K1

Chữ: Người lao động nước ngoài làm việc tại Việt Nam là người có quốc tịch nước ngoài và phải đáp ứng các điều kiện sau đây:

- **Lệch** ĐA#0 / LLM#0: chu_the.loai: ĐA='?' LLM='W'
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «có quốc tịch nước ngoài» chủ thể=người:? q1
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «có quốc tịch nước ngoài» chủ thể=người:W q1
- **Lệch** ĐA#1 / LLM#1: doi_so: ĐA=['?'] LLM=['W']
  - ĐA: menh_de/ket_luan [khong,khang_dinh] «là người lao động nước ngoài làm việc tại Việt Nam» chủ thể=-:None q1 — lý do giu_chung: Định nghĩa X là Y: các dấu hiệu là dieu_kien, kết luận là 'là X' (K5).
  - LLM: menh_de/ket_luan [khong,khang_dinh] «là người lao động nước ngoài làm việc tại Việt Nam» chủ thể=-:None q1

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D151.K1.a

Chữ: Đủ 18 tuổi trở lên và có năng lực hành vi dân sự đầy đủ;
Câu dẫn: Người lao động nước ngoài làm việc tại Việt Nam là người có quốc tịch nước ngoài và phải đáp ứng các điều kiện sau đây:

- **Lệch** ĐA#0 / LLM#0: quy_tac: ĐA='q1 (lệch nhóm với ĐA#[1])' LLM='q1'
  - ĐA: menh_de/ket_luan [phai,khang_dinh] «đủ 18 tuổi trở lên» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1 — lý do tach: Tuổi và năng lực hành vi dân sự kiểm được độc lập, thiếu cái nào cũng không đủ điều kiện.
  - LLM: menh_de/ket_luan [phai,khang_dinh] «đủ 18 tuổi trở lên» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1 — lý do tach: Đủ tuổi và có năng lực hành vi dân sự đầy đủ kiểm được đúng/sai độc lập, thiếu mỗi điều kiện có ý nghĩa pháp lý riêng.
- **Lệch** ĐA#1 / LLM#1: quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0])' LLM='q2'
  - ĐA: menh_de/ket_luan [phai,khang_dinh] «có năng lực hành vi dân sự đầy đủ» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1
  - LLM: menh_de/ket_luan [phai,khang_dinh] «có năng lực hành vi dân sự đầy đủ» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q2 — lý do tach: Đủ tuổi và có năng lực hành vi dân sự đầy đủ kiểm được đúng/sai độc lập, thiếu mỗi điều kiện có ý nghĩa pháp lý riêng.

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D151.K1.c

Chữ: Không phải là người đang trong thời gian chấp hành hình phạt hoặc chưa được xóa án tích hoặc đang trong thời gian bị truy cứu trách nhiệm hình sự theo quy định của pháp luật nước ngoài hoặc pháp luật Việt Nam;
Câu dẫn: Người lao động nước ngoài làm việc tại Việt Nam là người có quốc tịch nước ngoài và phải đáp ứng các điều kiện sau đây:

- **Lệch** ĐA#0 / LLM#0: quy_tac: ĐA='q1 (lệch nhóm với ĐA#[1, 2])' LLM='q1'
  - ĐA: menh_de/ket_luan [phai,phu_dinh] «là người đang trong thời gian chấp hành hình phạt» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1 — lý do tach: Phủ định của 'A hoặc B hoặc C' = không A, không B, không C: ba yêu cầu cùng phải đúng (không dùng nhom_hoac).
  - LLM: menh_de/ket_luan [phai,phu_dinh] «là người đang trong thời gian chấp hành hình phạt» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1 — lý do tach: Chữ 'Không phải' đứng đầu chuỗi áp cho từng mục; mỗi trạng thái kiểm được độc lập và có ý nghĩa pháp lý riêng.
- **Lệch** ĐA#1 / LLM#1: quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0, 2])' LLM='q2'
  - ĐA: menh_de/ket_luan [phai,phu_dinh] «là người chưa được xóa án tích» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1
  - LLM: menh_de/ket_luan [phai,phu_dinh] «là người chưa được xóa án tích» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q2 — lý do tach: Chữ 'Không phải' đứng đầu chuỗi áp cho từng mục; mỗi trạng thái kiểm được độc lập và có ý nghĩa pháp lý riêng.
- **Lệch** ĐA#2 / LLM#2: chua_ro: ĐA=[] LLM=['pham_vi_bo_ngu']; bo_ngu: ĐA=[] LLM=[('theo quy định của pháp luật nước ngoài hoặc pháp luật Việt Nam', 'unknown')]; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0, 1])' LLM='q3'
  - ĐA: menh_de/ket_luan [phai,phu_dinh] «là người đang trong thời gian bị truy cứu trách nhiệm hình sự» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1
  - LLM: menh_de/ket_luan [phai,phu_dinh] «là người đang trong thời gian bị truy cứu trách nhiệm hình sự» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q3 bổ ngữ=[('theo quy định của pháp luật nước ngoài hoặc pháp luật Việt Nam', 'unknown')] CHƯA RÕ=[('theo quy định của pháp luật nước ngoài hoặc pháp luật Việt Nam', 'pham_vi_bo_ngu')] — lý do gan_bo_ngu: Cụm bổ ngữ đứng cuối chuỗi ba mục, chữ không cho căn cứ để biết chỉ áp mục cuối hay cả nhóm nên để unknown và không tự rải.
- **Chỉ ĐA có** #3: bo_qua dan_chieu_mo  «theo quy định của pháp luật nước ngoài hoặc pháp luật Việt Nam»

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D151.K1.d

Chữ: Có giấy phép lao động do cơ quan nhà nước có thẩm quyền của Việt Nam cấp, trừ trường hợp quy định tại Điều 154 của Bộ luật này.
Câu dẫn: Người lao động nước ngoài làm việc tại Việt Nam là người có quốc tịch nước ngoài và phải đáp ứng các điều kiện sau đây:

- **Lệch** ĐA#1 / LLM#1: vai: ĐA='ngoai_le' LLM=''
  - ĐA: con_tro/ngoai_le → ['D154'] gắn=None
  - LLM: con_tro/ → ['D154'] gắn=None
- **Chỉ ĐA có** #0: menh_de/ket_luan [phai,khang_dinh] «có giấy phép lao động» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1 bổ ngữ=[('do cơ quan nhà nước có thẩm quyền của Việt Nam cấp', 'this_clause')]
- **Chỉ LLM có** #0: menh_de/ket_luan [phai,khang_dinh] «có giấy phép lao động do cơ quan nhà nước có thẩm quyền của Việt Nam cấp» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D137.K1.a

Chữ: Mang thai từ tháng thứ 07 hoặc từ tháng thứ 06 nếu làm việc ở vùng cao, vùng sâu, vùng xa, biên giới, hải đảo;
Câu dẫn: Người sử dụng lao động không được sử dụng người lao động làm việc ban đêm, làm thêm giờ và đi công tác xa trong trường hợp sau đây:

- **Lệch** ĐA#2 / LLM#2: doi_so: ĐA=[] LLM=['G']
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «làm việc ở vùng cao, vùng sâu, vùng xa, biên giới, hải đảo» chủ thể=người lao động:W q2 — lý do tach: "tháng 07" HOẶC ("tháng 06" VÀ làm ở vùng khó khăn): tách hai quy tắc q1, q2 (K2); "nếu ..." là điều kiện của q2, không phải bổ ngữ.
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «làm việc ở vùng cao, vùng sâu, vùng xa, biên giới, hải đảo» chủ thể=người lao động:W q2 — lý do giu_chung: Các vùng liệt kê là những nơi làm việc thay thế nhau của cùng một điều kiện, làm việc ở nơi nào cũng có cùng hệ quả pháp lý.

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D146.K1

Chữ: Thời giờ làm việc của người chưa đủ 15 tuổi không được quá 04 giờ trong 01 ngày và 20 giờ trong 01 tuần; không được làm thêm giờ, làm việc vào ban đêm.

- **Lệch** ĐA#0 / LLM#0: quy_tac: ĐA='q1 (lệch nhóm với ĐA#[1, 2])' LLM='q1'
  - ĐA: menh_de/ket_luan [cam,khang_dinh] «Thời giờ làm việc quá 04 giờ trong 01 ngày» chủ thể=người chưa đủ 15 tuổi:W q1 — lý do tach: Giới hạn ngày và tuần kiểm độc lập; câu sau cấm hai hành vi riêng.
  - LLM: menh_de/ket_luan [cam,khang_dinh] «thời giờ làm việc quá 04 giờ trong 01 ngày» chủ thể=người chưa đủ 15 tuổi:W q1 — lý do tach: Giới hạn 04 giờ mỗi ngày và giới hạn 20 giờ mỗi tuần kiểm được độc lập, vượt từng giới hạn là một vi phạm riêng.
- **Lệch** ĐA#1 / LLM#1: quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0, 2])' LLM='q2'
  - ĐA: menh_de/ket_luan [cam,khang_dinh] «Thời giờ làm việc quá 20 giờ trong 01 tuần» chủ thể=người chưa đủ 15 tuổi:W q1
  - LLM: menh_de/ket_luan [cam,khang_dinh] «thời giờ làm việc quá 20 giờ trong 01 tuần» chủ thể=người chưa đủ 15 tuổi:W q2 — lý do tach: Giới hạn 20 giờ mỗi tuần tách khỏi giới hạn 04 giờ mỗi ngày vì có thể vi phạm một mà không vi phạm kia.
- **Lệch** ĐA#2 / LLM#2: chua_ro: ĐA=['chu_the'] LLM=[]; chu_the.loai: ĐA=None LLM='W'; doi_so: ĐA=['W'] LLM=[]; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0, 1])' LLM='q3'
  - ĐA: menh_de/ket_luan [cam,khang_dinh] «làm thêm giờ» chủ thể=-:None q1 CHƯA RÕ=[('chủ thể mang lệnh cấm', 'chu_the')]
  - LLM: menh_de/ket_luan [cam,khang_dinh] «làm thêm giờ» chủ thể=người chưa đủ 15 tuổi:W q3 — lý do tach: Làm thêm giờ và làm việc ban đêm là hai hành vi cấm độc lập; chủ thể được lấy từ vế trước dấu chấm phẩy.
- **Chỉ ĐA có** #3: menh_de/ket_luan [cam,khang_dinh] «làm việc vào ban đêm» chủ thể=-:None q1 CHƯA RÕ=[('chủ thể mang lệnh cấm', 'chu_the')]
- **Chỉ LLM có** #3: menh_de/ket_luan [cam,khang_dinh] «làm việc» chủ thể=người chưa đủ 15 tuổi:W q4 bổ ngữ=[('vào ban đêm', 'this_clause')] — lý do gan_bo_ngu: Cụm "vào ban đêm" đứng sau mục cuối chỉ gắn với "làm việc", không rải sang "làm thêm giờ"; chữ "không được" đứng đầu chuỗi được hiểu cho từng mục.

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D15.K2

Chữ: Tự do giao kết hợp đồng lao động nhưng không được trái pháp luật, thỏa ước lao động tập thể và đạo đức xã hội.

- **Lệch** ĐA#0 / LLM#0: chua_ro: ĐA=['chu_the'] LLM=[]; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[1, 2, 3])' LLM='q1'
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «Tự do giao kết hợp đồng lao động» chủ thể=-:None q1 CHƯA RÕ=[('chủ thể', 'chu_the')]
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «tự do giao kết hợp đồng lao động» chủ thể=-:None q1
- **Lệch** ĐA#1 / LLM#1: chu_the.loai: ĐA=None LLM='C'; doi_so: ĐA=[] LLM=['?']; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0, 2, 3])' LLM='q2'
  - ĐA: menh_de/ket_luan [cam,khang_dinh] «trái pháp luật» chủ thể=-:None q1 — lý do tach: Trái luật, trái thỏa ước, trái đạo đức xã hội là ba căn cứ vi phạm riêng.
  - LLM: menh_de/ket_luan [cam,khang_dinh] «trái pháp luật» chủ thể=hợp đồng lao động:C q2 — lý do tach: Trái pháp luật, trái thỏa ước lao động tập thể và trái đạo đức xã hội là ba giới hạn độc lập, vi phạm mỗi giới hạn có ý nghĩa pháp lý riêng; "không được trái" đứng đầu chuỗi nên áp cho từng mục.
- **Lệch** ĐA#2 / LLM#2: chu_the.loai: ĐA=None LLM='C'; doi_so: ĐA=[] LLM=['?']; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0, 1, 3])' LLM='q3'
  - ĐA: menh_de/ket_luan [cam,khang_dinh] «trái thỏa ước lao động tập thể» chủ thể=-:None q1
  - LLM: menh_de/ket_luan [cam,khang_dinh] «trái thỏa ước lao động tập thể» chủ thể=hợp đồng lao động:C q3 — lý do tach: Trái pháp luật, trái thỏa ước lao động tập thể và trái đạo đức xã hội là ba giới hạn độc lập, vi phạm mỗi giới hạn có ý nghĩa pháp lý riêng; "không được trái" đứng đầu chuỗi nên áp cho từng mục.
- **Lệch** ĐA#3 / LLM#3: chu_the.loai: ĐA=None LLM='C'; doi_so: ĐA=[] LLM=['?']; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0, 1, 2])' LLM='q4'
  - ĐA: menh_de/ket_luan [cam,khang_dinh] «trái đạo đức xã hội» chủ thể=-:None q1
  - LLM: menh_de/ket_luan [cam,khang_dinh] «trái đạo đức xã hội» chủ thể=hợp đồng lao động:C q4 — lý do tach: Trái pháp luật, trái thỏa ước lao động tập thể và trái đạo đức xã hội là ba giới hạn độc lập, vi phạm mỗi giới hạn có ý nghĩa pháp lý riêng; "không được trái" đứng đầu chuỗi nên áp cho từng mục.

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D24.K3

Chữ: Không áp dụng thử việc đối với người lao động giao kết hợp đồng lao động có thời hạn dưới 01 tháng.

- **Chỉ ĐA có** #0: menh_de/ket_luan [khong_ap_dung,khang_dinh] «áp dụng thử việc» chủ thể=-:None q1
- **Chỉ LLM có** #0: menh_de/ket_luan [khong_ap_dung,khang_dinh] «thử việc đối với người lao động» chủ thể=-:None q1 — lý do tach: Văn bản tuyên bố chế định thử việc không áp dụng cho một nhóm người lao động, nên nhóm đó được tách thành điều kiện riêng.

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D24.K1

Chữ: Người sử dụng lao động và người lao động có thể thỏa thuận nội dung thử việc ghi trong hợp đồng lao động hoặc thỏa thuận về thử việc bằng việc giao kết hợp đồng thử việc.

- **Lệch** ĐA#0 / LLM#0: quy_tac: ĐA='q1 (lệch nhóm với ĐA#[1])' LLM='q1'
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «thỏa thuận nội dung thử việc ghi trong hợp đồng lao động» chủ thể=Người sử dụng lao động và người lao động:('E', 'W') q1 — lý do tach: 'Hoặc' nối hai cách thỏa thuận được phép, không phải điều kiện: hai dòng duoc, không dùng nhom_hoac.
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «thỏa thuận nội dung thử việc ghi trong hợp đồng lao động» chủ thể=Người sử dụng lao động và người lao động:('E', 'W') q1 — lý do tach: Hai cách thỏa thuận về thử việc nối bằng "hoặc" là hai quyền độc lập, mỗi cách kiểm được đúng/sai riêng nên tách thành hai mệnh đề.
- **Lệch** ĐA#1 / LLM#1: menh_de: ĐA='thỏa thuận về thử việc bằng việc giao kết hợp đồng thử việc' LLM='thỏa thuận về thử việc'; doi_so: ĐA=['C'] LLM=[]; bo_ngu: ĐA=[] LLM=[('bằng việc giao kết hợp đồng thử việc', 'this_clause')]; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0])' LLM='q2'
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «thỏa thuận về thử việc bằng việc giao kết hợp đồng thử việc» chủ thể=Người sử dụng lao động và người lao động:('E', 'W') q1
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «thỏa thuận về thử việc» chủ thể=Người sử dụng lao động và người lao động:('E', 'W') q2 bổ ngữ=[('bằng việc giao kết hợp đồng thử việc', 'this_clause')] — lý do gan_bo_ngu: Cụm "bằng việc giao kết hợp đồng thử việc" là cách thức chỉ gắn với vế thứ hai, vì vế đầu đã quy định cách thức là ghi trong hợp đồng lao động.

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D3.K1

Chữ: Người lao động là người làm việc cho người sử dụng lao động theo thỏa thuận, được trả lương và chịu sự quản lý, điều hành, giám sát của người sử dụng lao động.
Độ tuổi lao động tối thiểu của người lao động là đủ 15 tuổi, trừ trường hợp quy định tại Mục 1 Chương XI của Bộ luật này.
Câu dẫn: Trong Bộ luật này, các từ ngữ dưới đây được hiểu như sau:

- **Lệch** ĐA#0 / LLM#0: menh_de: ĐA='là người làm việc cho người sử dụng lao động' LLM='làm việc cho người sử dụng lao động'; chu_the.loai: ĐA='?' LLM='W'
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «là người làm việc cho người sử dụng lao động» chủ thể=người:? q1 bổ ngữ=[('theo thỏa thuận', 'this_clause')] — lý do tach: Định nghĩa gồm ba dấu hiệu, mỗi dấu hiệu kiểm độc lập; thiếu một dấu hiệu thì không phải người lao động.
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «làm việc cho người sử dụng lao động» chủ thể=người:W q1 bổ ngữ=[('theo thỏa thuận', 'this_clause')] — lý do gan_bo_ngu: Cụm "theo thỏa thuận" đứng ngay sau mục đầu và trước dấu phẩy ngăn mục sau, nên chỉ gắn cho mục làm việc, không rải sang các mục khác.
- **Lệch** ĐA#1 / LLM#1: chu_the.loai: ĐA='?' LLM='W'; doi_so: ĐA=['A'] LLM=[]
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «được trả lương» chủ thể=người:? q1 — lý do tach: 'Được' ở đây là bị động trong định nghĩa, không phải quyền: phuong_thuc khong.
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «được trả lương» chủ thể=người:W q1
- **Lệch** ĐA#2 / LLM#2: chu_the.loai: ĐA='?' LLM='W'
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «chịu sự quản lý, điều hành, giám sát của người sử dụng lao động» chủ thể=người:? q1 — lý do giu_chung: Quản lý, điều hành, giám sát cùng mô tả một quan hệ lệ thuộc; giữ chung.
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «chịu sự quản lý, điều hành, giám sát của người sử dụng lao động» chủ thể=người:W q1 — lý do giu_chung: Quản lý, điều hành, giám sát cùng mô tả một quan hệ phụ thuộc vào người sử dụng lao động nên giữ chung một dấu hiệu.
- **Lệch** ĐA#3 / LLM#3: doi_so: ĐA=['?'] LLM=['W']
  - ĐA: menh_de/ket_luan [khong,khang_dinh] «là người lao động» chủ thể=-:None q1 — lý do giu_chung: Định nghĩa X là Y: các dấu hiệu là dieu_kien, kết luận là 'là X' (K5).
  - LLM: menh_de/ket_luan [khong,khang_dinh] «là người lao động» chủ thể=-:None q1
- **Lệch** ĐA#4 / LLM#5: menh_de: ĐA='Độ tuổi lao động tối thiểu là đủ 15 tuổi' LLM='là độ tuổi lao động tối thiểu của người lao động'; chu_the.loai: ĐA='W' LLM=None; doi_so: ĐA=[] LLM=['W']
  - ĐA: menh_de/ket_luan [khong,khang_dinh] «Độ tuổi lao động tối thiểu là đủ 15 tuổi» chủ thể=người lao động:W q2
  - LLM: menh_de/ket_luan [khong,khang_dinh] «là độ tuổi lao động tối thiểu của người lao động» chủ thể=-:None q2
- **Lệch** ĐA#5 / LLM#6: vai: ĐA='ngoai_le' LLM=''; gan_vao: ĐA='4 (tức LLM#5)' LLM=None
  - ĐA: con_tro/ngoai_le → [] gắn=4 CHƯA RÕ=[('Mục 1 Chương XI của Bộ luật này', 'khac')] — lý do chua_ro: Dẫn chiếu rõ nhưng không có đích trong dan_chieu_1_2: vẫn là con_tro, targets để trống.
  - LLM: con_tro/ → [] gắn=None CHƯA RÕ=[('Mục 1 Chương XI của Bộ luật này', 'khac')] — lý do chua_ro: Ngoại lệ dẫn tới Mục 1 Chương XI nhưng dan_chieu rỗng nên không giải được đích; ngoại lệ chặn cả quy tắc về độ tuổi.
- **Chỉ LLM có** #4: menh_de/dieu_kien [khong,khang_dinh] «đủ 15 tuổi» chủ thể=người lao động:W q2

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D9.K1

Chữ: Việc làm là hoạt động lao động tạo ra thu nhập mà pháp luật không cấm.

- **Lệch** ĐA#0 / LLM#0: menh_de: ĐA='hoạt động lao động tạo ra thu nhập' LLM='tạo ra thu nhập'; chu_the.loai: ĐA=None LLM='J'; doi_so: ĐA=['?'] LLM=['A']; bo_ngu: ĐA=[('mà pháp luật không cấm', 'this_clause')] LLM=[]
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «hoạt động lao động tạo ra thu nhập» chủ thể=-:None q1 bổ ngữ=[('mà pháp luật không cấm', 'this_clause')] — lý do gan_bo_ngu: 'Mà pháp luật không cấm' là dấu hiệu giới hạn của định nghĩa, ghi bổ ngữ; không phải dẫn chiếu tới quy phạm cụ thể.
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «tạo ra thu nhập» chủ thể=hoạt động lao động:J q1 — lý do tach: Việc tạo ra thu nhập và việc pháp luật không cấm là hai dấu hiệu kiểm được độc lập của định nghĩa nên tách riêng.
- **Lệch** ĐA#1 / LLM#2: doi_so: ĐA=['?'] LLM=['J']
  - ĐA: menh_de/ket_luan [khong,khang_dinh] «là việc làm» chủ thể=-:None q1 — lý do giu_chung: Định nghĩa X là Y: các dấu hiệu là dieu_kien, kết luận là 'là X' (K5).
  - LLM: menh_de/ket_luan [khong,khang_dinh] «là việc làm» chủ thể=-:None q1
- **Chỉ LLM có** #1: menh_de/dieu_kien [khong,phu_dinh] «pháp luật cấm» chủ thể=hoạt động lao động:J q1 — lý do tach: Mệnh đề quan hệ "mà pháp luật không cấm" có vị ngữ riêng, bổ nghĩa cho hoạt động lao động, nên tách thành điều kiện độc lập.

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D10.K1

Chữ: Được tự do lựa chọn việc làm, làm việc cho bất kỳ người sử dụng lao động nào và ở bất kỳ nơi nào mà pháp luật không cấm.

- **Lệch** ĐA#0 / LLM#0: bo_ngu: ĐA=[('mà pháp luật không cấm', 'group')] LLM=[]; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[1, 2])' LLM='q1'
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «tự do lựa chọn việc làm» chủ thể=người lao động:W q1 bổ ngữ=[('mà pháp luật không cấm', 'group')] — lý do gan_bo_ngu: Chủ thể lấy từ tiêu đề; 'mà pháp luật không cấm' về nghĩa giới hạn cả nhóm quyền, không chỉ 'nơi nào'.
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «tự do lựa chọn việc làm» chủ thể=người lao động:W q1 — lý do tach: Tự do lựa chọn việc làm là một quyền riêng, vi phạm quyền này có ý nghĩa pháp lý độc lập với quyền chọn người sử dụng lao động và nơi làm việc.
- **Lệch** ĐA#1 / LLM#1: menh_de: ĐA='làm việc cho bất kỳ người sử dụng lao động nào' LLM='tự do làm việc cho bất kỳ người sử dụng lao động nào'; bo_ngu: ĐA=[('mà pháp luật không cấm', 'group')] LLM=[]; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0, 2])' LLM='q2'
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «làm việc cho bất kỳ người sử dụng lao động nào» chủ thể=người lao động:W q1 bổ ngữ=[('mà pháp luật không cấm', 'group')] — lý do tach: Chọn người sử dụng lao động và chọn nơi làm việc bị hạn chế riêng được, nên tách.
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «tự do làm việc cho bất kỳ người sử dụng lao động nào» chủ thể=người lao động:W q2 — lý do tach: Tự do làm việc cho bất kỳ người sử dụng lao động nào là quyền riêng, kế thừa từ "Được tự do" đứng đầu chuỗi.
- **Lệch** ĐA#2 / LLM#2: menh_de: ĐA='làm việc ở bất kỳ nơi nào' LLM='tự do làm việc ở bất kỳ nơi nào'; doi_so: ĐA=[] LLM=['G']; bo_ngu: ĐA=[('mà pháp luật không cấm', 'group')] LLM=[('mà pháp luật không cấm', 'this_clause')]; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0, 1])' LLM='q3'
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «làm việc ở bất kỳ nơi nào» chủ thể=người lao động:W q1 bổ ngữ=[('mà pháp luật không cấm', 'group')]
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «tự do làm việc ở bất kỳ nơi nào» chủ thể=người lao động:W q3 bổ ngữ=[('mà pháp luật không cấm', 'this_clause')] — lý do gan_bo_ngu: Cụm "mà pháp luật không cấm" là mệnh đề quan hệ gắn trực tiếp với "nơi nào" nên chỉ gắn vào mục cuối, không rải sang hai mục trước.

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D4.K1

Chữ: Bảo đảm quyền và lợi ích hợp pháp, chính đáng của người lao động, người làm việc không có quan hệ lao động; khuyến khích những thỏa thuận bảo đảm cho người lao động có điều kiện thuận lợi hơn so với quy định của pháp luật về lao động.

- **Chỉ LLM có** #0: bo_qua khong_quy_pham  «Bảo đảm quyền và lợi ích hợp pháp, chính đáng của người lao động, người làm việc»

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D9.K2

Chữ: Nhà nước, người sử dụng lao động và xã hội có trách nhiệm tham gia giải quyết việc làm, bảo đảm cho mọi người có khả năng lao động đều có cơ hội có việc làm.

- **Chỉ ĐA có** #0: bo_qua khong_quy_pham  «Nhà nước, người sử dụng lao động và xã hội có trách nhiệm tham gia giải quyết vi»
- **Chỉ LLM có** #0: menh_de/ket_luan [phai,khang_dinh] «tham gia giải quyết việc làm» chủ thể=Nhà nước, người sử dụng lao động và xã hội:('?', 'E') q1 — lý do giu_chung: Nhà nước, người sử dụng lao động và xã hội cùng chung một trách nhiệm tập thể nên giữ chung trong một mệnh đề.
- **Chỉ LLM có** #1: menh_de/ket_luan [phai,khang_dinh] «bảo đảm cho mọi người có khả năng lao động đều có cơ hội có việc làm» chủ thể=Nhà nước, người sử dụng lao động và xã hội:('?', 'E') q2 — lý do tach: Trách nhiệm bảo đảm cơ hội có việc làm kiểm được độc lập với trách nhiệm tham gia giải quyết việc làm, nên tách thành quy tắc riêng.

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D14.K1

Chữ: Hợp đồng lao động phải được giao kết bằng văn bản và được làm thành 02 bản, người lao động giữ 01 bản, người sử dụng lao động giữ 01 bản, trừ trường hợp quy định tại khoản 2 Điều này.
Hợp đồng lao động được giao kết thông qua phương tiện điện tử dưới hình thức thông điệp dữ liệu theo quy định của pháp luật về giao dịch điện tử có giá trị như hợp đồng lao động bằng văn bản.

- **Lệch** ĐA#2 / LLM#4: vai: ĐA='ngoai_le' LLM=''
  - ĐA: con_tro/ngoai_le → ['D14.K2'] gắn=None
  - LLM: con_tro/ → ['D14.K2'] gắn=None — lý do gan_bo_ngu: Ngoại lệ đứng cuối chuỗi các yêu cầu và loại trừ cả quy tắc (bằng văn bản, 02 bản, mỗi bên giữ 01 bản) nên gan_vao là null.
- **Lệch** ĐA#3 / LLM#5: bo_ngu: ĐA=[] LLM=[('theo quy định của pháp luật về giao dịch điện tử', 'this_clause')]
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «được giao kết thông qua phương tiện điện tử dưới hình thức thông điệp dữ liệu» chủ thể=Hợp đồng lao động:C q2
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «được giao kết thông qua phương tiện điện tử dưới hình thức thông điệp dữ liệu» chủ thể=Hợp đồng lao động:C q2 bổ ngữ=[('theo quy định của pháp luật về giao dịch điện tử', 'this_clause')] — lý do giu_chung: Phương tiện điện tử và hình thức thông điệp dữ liệu cùng mô tả một cách giao kết điện tử, chỉ có nghĩa khi xét cùng nhau.
- **Lệch** ĐA#5 / LLM#7: ly_do.ma: ĐA='dan_chieu_ngoai' LLM='dan_chieu_mo'
  - ĐA: bo_qua dan_chieu_ngoai  «theo quy định của pháp luật về giao dịch điện tử»
  - LLM: bo_qua dan_chieu_mo  «theo quy định của pháp luật về giao dịch điện tử»
- **Chỉ ĐA có** #1: menh_de/ket_luan [phai,khang_dinh] «được làm thành 02 bản, người lao động giữ 01 bản, người sử dụng lao động giữ 01 bản» chủ thể=Hợp đồng lao động:C q1 — lý do giu_chung: Số bản và việc mỗi bên giữ một bản là một yêu cầu tập thể về lập và giao bản hợp đồng.
- **Chỉ LLM có** #1: menh_de/ket_luan [phai,khang_dinh] «được làm thành 02 bản» chủ thể=Hợp đồng lao động:C q1 — lý do tach: Làm thành 02 bản là yêu cầu riêng, kế thừa chữ phải và chủ thể hợp đồng từ vế đầu, tách khỏi yêu cầu bằng văn bản.
- **Chỉ LLM có** #2: menh_de/ket_luan [phai,khang_dinh] «giữ 01 bản» chủ thể=người lao động:W q1 — lý do ke_thua: Người lao động giữ 01 bản kế thừa phương thức phải của vế đầu câu; tách riêng vì chủ thể khác với người sử dụng lao động.
- **Chỉ LLM có** #3: menh_de/ket_luan [phai,khang_dinh] «giữ 01 bản» chủ thể=người sử dụng lao động:E q1 — lý do ke_thua: Người sử dụng lao động giữ 01 bản kế thừa phương thức phải của vế đầu câu; tách riêng vì chủ thể khác với người lao động.

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D14.K2

Chữ: Hai bên có thể giao kết hợp đồng lao động bằng lời nói đối với hợp đồng có thời hạn dưới 01 tháng, trừ trường hợp quy định tại khoản 2 Điều 18, điểm a khoản 1 Điều 145 và khoản 1 Điều 162 của Bộ luật này.

- **Lệch** ĐA#1 / LLM#1: doi_so: ĐA=[] LLM=['?']
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «có thời hạn dưới 01 tháng» chủ thể=hợp đồng:C q1
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «có thời hạn dưới 01 tháng» chủ thể=hợp đồng:C q1
- **Lệch** ĐA#2 / LLM#2: vai: ĐA='ngoai_le' LLM=''
  - ĐA: con_tro/ngoai_le → ['D18.K2', 'D145.K1.a', 'D162.K1'] gắn=None — lý do tach: Một chỗ 'trừ trường hợp' nên một dòng con_tro, ba đích; mỗi đích là một ngoại lệ độc lập.
  - LLM: con_tro/ → ['D18.K2', 'D145.K1.a', 'D162.K1'] gắn=None

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D113.K1

Chữ: Người lao động làm việc đủ 12 tháng cho một người sử dụng lao động thì được nghỉ hằng năm, hưởng nguyên lương theo hợp đồng lao động như sau:

- **Chỉ ĐA có** #1: menh_de/ket_luan [duoc,khang_dinh] «nghỉ hằng năm» chủ thể=Người lao động:W q1 — lý do tach: Được nghỉ và được hưởng nguyên lương là hai quyền vi phạm riêng được.
- **Chỉ ĐA có** #2: menh_de/ket_luan [duoc,khang_dinh] «hưởng nguyên lương theo hợp đồng lao động» chủ thể=Người lao động:W q1
- **Chỉ ĐA có** #3: bo_qua cau_dan danh_sach «như sau:»
- **Chỉ LLM có** #1: bo_qua cau_dan danh_sach «được nghỉ hằng năm, hưởng nguyên lương theo hợp đồng lao động như sau:»

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D113.K1.a

Chữ: 12 ngày làm việc đối với người làm công việc trong điều kiện bình thường;
Câu dẫn: Người lao động làm việc đủ 12 tháng cho một người sử dụng lao động thì được nghỉ hằng năm, hưởng nguyên lương theo hợp đồng lao động như sau:

- **Chỉ ĐA có** #0: menh_de/ket_luan [duoc,khang_dinh] «nghỉ hằng năm 12 ngày làm việc» chủ thể=Người lao động:W q1 — lý do ke_thua: Mục con chỉ là con số; vị ngữ 'được nghỉ hằng năm' và chủ thể kế thừa từ câu dẫn.
- **Chỉ LLM có** #1: menh_de/ket_luan [duoc,khang_dinh] «nghỉ hằng năm 12 ngày làm việc, hưởng nguyên lương theo hợp đồng lao động» chủ thể=Người lao động:W q1 — lý do ke_thua: Kế thừa chủ thể, phương thức được và vị ngữ nghỉ hằng năm, hưởng nguyên lương của câu dẫn; mục con chỉ nêu số ngày.

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D129.K1

Chữ: Người lao động làm hư hỏng dụng cụ, thiết bị hoặc có hành vi khác gây thiệt hại tài sản của người sử dụng lao động thì phải bồi thường theo quy định của pháp luật hoặc nội quy lao động của người sử dụng lao động.
Trường hợp người lao động gây thiệt hại không nghiêm trọng do sơ suất với giá trị không quá 10 tháng lương tối thiểu vùng do Chính phủ công bố được áp dụng tại nơi người lao động làm việc thì người lao động phải bồi thường nhiều nhất là 03 tháng tiền lương và bị khấu trừ hằng tháng vào lương theo quy định tại khoản 3 Điều 102 của Bộ luật này.

- **Lệch** ĐA#0 / LLM#0: doi_so: ĐA=[] LLM=['?']; bo_ngu: ĐA=[('của người sử dụng lao động', 'group')] LLM=[]
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «làm hư hỏng dụng cụ, thiết bị» chủ thể=Người lao động:W q1 bổ ngữ=[('của người sử dụng lao động', 'group')] hoặc=h1 — lý do gan_bo_ngu: 'Của người sử dụng lao động' về nghĩa áp cả cho dụng cụ, thiết bị (tài sản của NSDLĐ).
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «làm hư hỏng dụng cụ, thiết bị» chủ thể=Người lao động:W q1 hoặc=h1 — lý do giu_chung: Dụng cụ và thiết bị cùng là đối tượng của một hành vi làm hư hỏng nên giữ chung.
- **Lệch** ĐA#2 / LLM#2: bo_ngu: ĐA=[] LLM=[('theo quy định của pháp luật hoặc nội quy lao động của người sử dụng lao động', 'this_clause')]
  - ĐA: menh_de/ket_luan [phai,khang_dinh] «bồi thường» chủ thể=Người lao động:W q1
  - LLM: menh_de/ket_luan [phai,khang_dinh] «bồi thường» chủ thể=Người lao động:W q1 bổ ngữ=[('theo quy định của pháp luật hoặc nội quy lao động của người sử dụng lao động', 'this_clause')] — lý do gan_bo_ngu: Cụm căn cứ theo pháp luật hoặc nội quy đứng cuối câu và chỉ bổ nghĩa cho nghĩa vụ bồi thường duy nhất.
- **Lệch** ĐA#5 / LLM#3: menh_de: ĐA='gây thiệt hại do sơ suất' LLM='gây thiệt hại không nghiêm trọng do sơ suất'
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «gây thiệt hại do sơ suất» chủ thể=người lao động:W q2
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «gây thiệt hại không nghiêm trọng do sơ suất» chủ thể=người lao động:W q2 — lý do tach: Tính chất thiệt hại do sơ suất và ngưỡng giá trị là hai điều kiện kiểm được độc lập, phải đủ cả hai.
- **Lệch** ĐA#6 / LLM#4: menh_de: ĐA='giá trị không quá 10 tháng lương tối thiểu vùng' LLM='không quá 10 tháng lương tối thiểu vùng'; chu_the.loai: ĐA=None LLM='A'; bo_ngu: ĐA=[('do Chính phủ công bố được áp dụng tại nơi người lao động làm việc', 'this_clause')] LLM=[('do Chính phủ công bố', 'this_clause'), ('được áp dụng tại nơi người lao động làm việc', 'this_clause')]
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «giá trị không quá 10 tháng lương tối thiểu vùng» chủ thể=-:None q2 bổ ngữ=[('do Chính phủ công bố được áp dụng tại nơi người lao động làm việc', 'this_clause')]
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «không quá 10 tháng lương tối thiểu vùng» chủ thể=giá trị:A q2 bổ ngữ=[('do Chính phủ công bố', 'this_clause'), ('được áp dụng tại nơi người lao động làm việc', 'this_clause')] — lý do gan_bo_ngu: Các cụm về nơi áp dụng và cơ quan công bố đứng cuối điều kiện, chỉ bổ nghĩa cho lương tối thiểu vùng của điều kiện giá trị.
- **Lệch** ĐA#8 / LLM#6: phuong_thuc: ĐA='phai' LLM='khong'; bo_ngu: ĐA=[] LLM=[('theo quy định tại khoản 3 Điều 102 của Bộ luật này', 'this_clause')]
  - ĐA: menh_de/ket_luan [phai,khang_dinh] «bị khấu trừ hằng tháng vào lương» chủ thể=người lao động:W q2
  - LLM: menh_de/ket_luan [khong,khang_dinh] «bị khấu trừ hằng tháng vào lương» chủ thể=người lao động:W q2 bổ ngữ=[('theo quy định tại khoản 3 Điều 102 của Bộ luật này', 'this_clause')] — lý do gan_bo_ngu: Cụm theo khoản 3 Điều 102 đứng cuối chỉ bổ nghĩa cho việc khấu trừ, và bị khấu trừ là bị động nên phương thức là khong.
- **Lệch** ĐA#9 / LLM#8: vai: ĐA='ket_luan' LLM=''
  - ĐA: con_tro/ket_luan → ['D102.K3'] gắn=8 — lý do gan_bo_ngu: Dẫn chiếu rõ nhưng không phải ngoại lệ: chỉ cách khấu trừ, gắn vế 'bị khấu trừ hằng tháng vào lương'.
  - LLM: con_tro/ → ['D102.K3'] gắn=6
- **Chỉ ĐA có** #3: bo_qua dan_chieu_mo  «theo quy định của pháp luật hoặc nội quy lao động của người sử dụng lao động»
- **Chỉ ĐA có** #4: menh_de/dieu_kien [khong,khang_dinh] «gây thiệt hại không nghiêm trọng» chủ thể=người lao động:W q2 — lý do tach: Ba điều kiện cộng dồn (không nghiêm trọng, do sơ suất, giá trị ≤ 10 tháng lương tối thiểu vùng), kiểm độc lập; 'không' nằm trong nội dung nên cuc khang_dinh.
- **Chỉ LLM có** #7: bo_qua dan_chieu_mo  «theo quy định của pháp luật»

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D108

Chữ: Người sử dụng lao động có quyền yêu cầu người lao động làm thêm giờ vào bất kỳ ngày nào mà không bị giới hạn về số giờ làm thêm theo quy định tại Điều 107 của Bộ luật này và người lao động không được từ chối trong trường hợp sau đây:

- **Lệch** ĐA#0 / LLM#0: menh_de: ĐA='yêu cầu người lao động làm thêm giờ vào bất kỳ ngày nào' LLM='yêu cầu người lao động làm thêm giờ'; doi_so: ĐA=['W', 'D'] LLM=['W']; bo_ngu: ĐA=[] LLM=[('vào bất kỳ ngày nào', 'this_clause')]
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «yêu cầu người lao động làm thêm giờ vào bất kỳ ngày nào» chủ thể=Người sử dụng lao động:E q1
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «yêu cầu người lao động làm thêm giờ» chủ thể=Người sử dụng lao động:E q1 bổ ngữ=[('vào bất kỳ ngày nào', 'this_clause')]
- **Lệch** ĐA#1 / LLM#1: phuong_thuc: ĐA='khong' LLM='duoc'
  - ĐA: menh_de/ket_luan [khong,phu_dinh] «bị giới hạn về số giờ làm thêm» chủ thể=Người sử dụng lao động:E q1
  - LLM: menh_de/ket_luan [duoc,phu_dinh] «bị giới hạn về số giờ làm thêm» chủ thể=Người sử dụng lao động:E q1 — lý do tach: Quyền yêu cầu làm thêm giờ vào bất kỳ ngày nào và quyền không bị giới hạn số giờ làm thêm là hai nội dung kiểm được độc lập, vi phạm mỗi nội dung có ý nghĩa pháp lý riêng.
- **Lệch** ĐA#2 / LLM#3: vai: ĐA='ket_luan' LLM=''
  - ĐA: con_tro/ket_luan → ['D107'] gắn=1 — lý do gan_bo_ngu: Không phải 'trừ trường hợp': Điều 108 gạt giới hạn của Điều 107; con trỏ gắn vế 'không bị giới hạn về số giờ làm thêm'.
  - LLM: con_tro/ → ['D107'] gắn=1
- **Chỉ ĐA có** #3: menh_de/ket_luan [cam,khang_dinh] «từ chối» chủ thể=người lao động:W q1 — lý do tach: Câu dẫn chứa hai kết luận cho hai chủ thể: quyền của E và cấm từ chối đối với W.
- **Chỉ LLM có** #2: menh_de/ket_luan [cam,khang_dinh] «từ chối làm thêm giờ» chủ thể=người lao động:W q1 — lý do ke_thua: Tân ngữ của 'từ chối' bị lược, lấy từ vế trước là làm thêm giờ theo yêu cầu của người sử dụng lao động.

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

