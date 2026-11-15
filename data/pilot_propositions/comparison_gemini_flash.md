# So sánh 1.6A thí điểm (menh-de-3) với đáp án nháp

Mỗi đơn vị có chỗ lệch: dòng của đáp án (ĐA) và của LLM; người dùng phán bên nào đúng. Đơn vị khớp hết không liệt kê.

- Dòng: ĐA 97, LLM 79; ghép được 76, chỉ ĐA có 21, chỉ LLM có 3.
- Lỗi cổng của LLM: 17. Câu dẫn lọt thành mệnh đề (ước bằng máy): 0.
- Field khớp trên các dòng ghép được: {'bo_qua.ly_do.ma': '10/10', 'bo_qua.cac_muc_con': '10/10', 'menh_de.vai': '53/58', 'menh_de.menh_de': '41/58', 'menh_de.phuong_thuc': '52/58', 'menh_de.cuc': '57/58', 'menh_de.chu_the.loai': '49/58', 'menh_de.doi_so': '35/58', 'menh_de.bo_ngu': '48/58', 'menh_de.liet_ke': '54/58', 'menh_de.nhom_hoac': '55/58', 'menh_de.chua_ro': '54/58', 'menh_de.quy_tac': '48/58', 'con_tro.vai': '8/8', 'con_tro.targets': '8/8', 'con_tro.gan_vao': '7/8', 'con_tro.chua_ro': '7/8'}.
- Chưa rõ của LLM theo nguyên nhân: {}.
- Đây là so với đáp án NHÁP: chỉ thành số đo sau khi người dùng phán xong các chỗ lệch (A38 K10).

## D5.K1.a

Chữ: Làm việc; tự do lựa chọn việc làm, nơi làm việc, nghề nghiệp, học nghề, nâng cao trình độ nghề nghiệp; không bị phân biệt đối xử, cưỡng bức lao động, quấy rối tình dục tại nơi làm việc;
Câu dẫn: Người lao động có các quyền sau đây:

- **Lệch** ĐA#0 / LLM#0: quy_tac: ĐA='q1 (lệch nhóm với ĐA#[3])' LLM='q1'
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «làm việc» chủ thể=Người lao động:W q1
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «làm việc» chủ thể=Người lao động:W q1
- **Lệch** ĐA#3 / LLM#1: menh_de: ĐA='tự do lựa chọn nghề nghiệp' LLM='tự do lựa chọn'; doi_so: ĐA=['J'] LLM=[]; liet_ke: ĐA=[] LLM=['việc làm', 'nơi làm việc', 'nghề nghiệp', 'học nghề', 'nâng cao trình độ nghề nghiệp']; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0])' LLM=None
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «tự do lựa chọn nghề nghiệp» chủ thể=Người lao động:W q1
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «tự do lựa chọn» chủ thể=Người lao động:W None liệt kê=['việc làm', 'nơi làm việc', 'nghề nghiệp', 'học nghề', 'nâng cao trình độ nghề nghiệp'] — lý do giu_chung: Tự do lựa chọn áp dụng chung cho danh sách đối tượng.
- **Chỉ ĐA có** #1: menh_de/ket_luan [duoc,khang_dinh] «tự do lựa chọn việc làm» chủ thể=Người lao động:W q1 — lý do tach: Tự do chọn việc làm, nơi làm việc, nghề nghiệp là ba quyền riêng: hạn chế từng cái là vi phạm riêng.
- **Chỉ ĐA có** #2: menh_de/ket_luan [duoc,khang_dinh] «tự do lựa chọn nơi làm việc» chủ thể=Người lao động:W q1
- **Chỉ ĐA có** #4: menh_de/ket_luan [duoc,khang_dinh] «học nghề» chủ thể=Người lao động:W q1 CHƯA RÕ=[('tự do lựa chọn', 'pham_vi_bo_ngu')]
- **Chỉ ĐA có** #5: menh_de/ket_luan [duoc,khang_dinh] «nâng cao trình độ nghề nghiệp» chủ thể=Người lao động:W q1 CHƯA RÕ=[('tự do lựa chọn', 'pham_vi_bo_ngu')]
- **Chỉ ĐA có** #6: menh_de/ket_luan [duoc,phu_dinh] «bị phân biệt đối xử» chủ thể=Người lao động:W q1 — lý do tach: 'Không bị' là quyền được bảo vệ (duoc + phu_dinh); ba hành vi bị cấm riêng nên tách ba dòng.
- **Chỉ ĐA có** #7: menh_de/ket_luan [duoc,phu_dinh] «bị cưỡng bức lao động» chủ thể=Người lao động:W q1
- **Chỉ ĐA có** #8: menh_de/ket_luan [duoc,phu_dinh] «bị quấy rối tình dục» chủ thể=Người lao động:W q1 bổ ngữ=[('tại nơi làm việc', 'this_clause')] — lý do gan_bo_ngu: 'Tại nơi làm việc' gắn với 'quấy rối tình dục' (khái niệm định nghĩa riêng); phân biệt đối xử và cưỡng bức lao động bị cấm ở mọi nơi.
- **Chỉ LLM có** #2: menh_de/ket_luan [duoc,phu_dinh] «bị phân biệt đối xử, cưỡng bức lao động, quấy rối tình dục» chủ thể=Người lao động:W None bổ ngữ=[('tại nơi làm việc', 'this_clause')] liệt kê=['phân biệt đối xử', 'cưỡng bức lao động', 'quấy rối tình dục'] — lý do giu_chung: Quyền không bị các hành vi xâm phạm tại nơi làm việc.
- Lỗi cổng LLM #1: menh_de thiếu quy_tac
- Lỗi cổng LLM #2: menh_de thiếu quy_tac

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D21.K1.a

Chữ: Tên, địa chỉ của người sử dụng lao động và họ tên, chức danh của người giao kết hợp đồng lao động bên phía người sử dụng lao động;
Câu dẫn: Hợp đồng lao động phải có những nội dung chủ yếu sau đây:

- **Lệch** ĐA#0 / LLM#0: liet_ke: ĐA=[] LLM=['Tên, địa chỉ của người sử dụng lao động', 'họ tên, chức danh của người giao kết hợp đồng lao động bên phía người sử dụng lao động']
  - ĐA: menh_de/ket_luan [phai,khang_dinh] «có Tên, địa chỉ của người sử dụng lao động và họ tên, chức danh của người giao kết hợp đồng lao động bên phía người sử dụng lao động» chủ thể=Hợp đồng lao động:C q1 — lý do giu_chung: Một yêu cầu tập thể (thông tin nhận diện bên NSDLĐ); không tách chỉ vì có nhiều danh từ.
  - LLM: menh_de/ket_luan [phai,khang_dinh] «có Tên, địa chỉ của người sử dụng lao động và họ tên, chức danh của người giao kết hợp đồng lao động bên phía người sử dụng lao động» chủ thể=Hợp đồng lao động:C None liệt kê=['Tên, địa chỉ của người sử dụng lao động', 'họ tên, chức danh của người giao kết hợp đồng lao động bên phía người sử dụng lao động'] — lý do giu_chung: Nội dung nhận diện bên sử dụng lao động bắt buộc phải có trong hợp đồng.
- Lỗi cổng LLM #0: menh_de thiếu quy_tac

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D21.K1.b

Chữ: Họ tên, ngày tháng năm sinh, giới tính, nơi cư trú, số thẻ Căn cước công dân, Chứng minh nhân dân hoặc hộ chiếu của người giao kết hợp đồng lao động bên phía người lao động;
Câu dẫn: Hợp đồng lao động phải có những nội dung chủ yếu sau đây:

- **Lệch** ĐA#0 / LLM#0: liet_ke: ĐA=[] LLM=['Họ tên', 'ngày tháng năm sinh', 'giới tính', 'nơi cư trú', 'số thẻ Căn cước công dân, Chứng minh nhân dân hoặc hộ chiếu']
  - ĐA: menh_de/ket_luan [phai,khang_dinh] «có Họ tên, ngày tháng năm sinh, giới tính, nơi cư trú, số thẻ Căn cước công dân, Chứng minh nhân dân hoặc hộ chiếu của người giao kết hợp đồng lao động bên phía người lao động» chủ thể=Hợp đồng lao động:C q1 — lý do giu_chung: Một yêu cầu tập thể (thông tin nhận diện bên NLĐ); 'hoặc' nối danh từ (loại giấy tờ), không phải các điều kiện nên không dùng nhom_hoac.
  - LLM: menh_de/ket_luan [phai,khang_dinh] «có Họ tên, ngày tháng năm sinh, giới tính, nơi cư trú, số thẻ Căn cước công dân, Chứng minh nhân dân hoặc hộ chiếu của người giao kết hợp đồng lao động bên phía người lao động» chủ thể=Hợp đồng lao động:C None liệt kê=['Họ tên', 'ngày tháng năm sinh', 'giới tính', 'nơi cư trú', 'số thẻ Căn cước công dân, Chứng minh nhân dân hoặc hộ chiếu'] — lý do giu_chung: Nội dung nhận diện bên người lao động bắt buộc phải có trong hợp đồng.
- Lỗi cổng LLM #0: menh_de thiếu quy_tac

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D35.K2

Chữ: Người lao động có quyền đơn phương chấm dứt hợp đồng lao động không cần báo trước trong trường hợp sau đây:

- **Lệch** ĐA#0 / LLM#0: doi_so: ĐA=['C'] LLM=[]
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «đơn phương chấm dứt hợp đồng lao động không cần báo trước» chủ thể=Người lao động:W q1
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «đơn phương chấm dứt hợp đồng lao động không cần báo trước» chủ thể=Người lao động:W q1

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D35.K2.a

Chữ: Không được bố trí theo đúng công việc, địa điểm làm việc hoặc không được bảo đảm điều kiện làm việc theo thỏa thuận, trừ trường hợp quy định tại Điều 29 của Bộ luật này;
Câu dẫn: Người lao động có quyền đơn phương chấm dứt hợp đồng lao động không cần báo trước trong trường hợp sau đây:

- **Lệch** ĐA#1 / LLM#0: menh_de: ĐA='được bố trí theo đúng địa điểm làm việc' LLM='được bố trí theo đúng công việc, địa điểm làm việc'
  - ĐA: menh_de/dieu_kien [khong,phu_dinh] «được bố trí theo đúng địa điểm làm việc» chủ thể=Người lao động:W q1 hoặc=h1
  - LLM: menh_de/dieu_kien [khong,phu_dinh] «được bố trí theo đúng công việc, địa điểm làm việc» chủ thể=Người lao động:W q1 hoặc=h1
- **Lệch** ĐA#2 / LLM#1: chua_ro: ĐA=['pham_vi_bo_ngu'] LLM=[]; menh_de: ĐA='được bảo đảm điều kiện làm việc' LLM='được bảo đảm điều kiện làm việc theo thỏa thuận'; bo_ngu: ĐA=[('theo thỏa thuận', 'unknown')] LLM=[]
  - ĐA: menh_de/dieu_kien [khong,phu_dinh] «được bảo đảm điều kiện làm việc» chủ thể=Người lao động:W q1 bổ ngữ=[('theo thỏa thuận', 'unknown')] hoặc=h1 CHƯA RÕ=[('theo thỏa thuận', 'pham_vi_bo_ngu')] — lý do gan_bo_ngu: 'Theo thỏa thuận' đứng cuối vế thứ hai; về nghĩa có thể áp cho cả ba, chưa đủ căn cứ để chọn.
  - LLM: menh_de/dieu_kien [khong,phu_dinh] «được bảo đảm điều kiện làm việc theo thỏa thuận» chủ thể=Người lao động:W q1 hoặc=h1
- **Chỉ ĐA có** #0: menh_de/dieu_kien [khong,phu_dinh] «được bố trí theo đúng công việc» chủ thể=Người lao động:W q1 hoặc=h1 — lý do tach: 'Không được bố trí' là bị động (khong + phu_dinh), không phải cấm; sai công việc hoặc sai địa điểm đều đủ một mình nên tách, nối 'hoặc'.

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D35.K2.b

Chữ: Không được trả đủ lương hoặc trả lương không đúng thời hạn, trừ trường hợp quy định tại khoản 4 Điều 97 của Bộ luật này;
Câu dẫn: Người lao động có quyền đơn phương chấm dứt hợp đồng lao động không cần báo trước trong trường hợp sau đây:

- **Lệch** ĐA#0 / LLM#0: doi_so: ĐA=['A'] LLM=[]
  - ĐA: menh_de/dieu_kien [khong,phu_dinh] «được trả đủ lương» chủ thể=Người lao động:W q1 hoặc=h1 — lý do tach: Bị động 'không được trả' (khong + phu_dinh); trả thiếu và trả trễ là hai vi phạm riêng, nối 'hoặc'.
  - LLM: menh_de/dieu_kien [khong,phu_dinh] «được trả đủ lương» chủ thể=Người lao động:W q1 hoặc=h1
- **Lệch** ĐA#1 / LLM#1: doi_so: ĐA=['A'] LLM=[]
  - ĐA: menh_de/dieu_kien [khong,phu_dinh] «trả lương đúng thời hạn» chủ thể=Người lao động:W q1 hoặc=h1
  - LLM: menh_de/dieu_kien [khong,phu_dinh] «trả lương đúng thời hạn» chủ thể=Người lao động:W q1 hoặc=h1
- Lỗi cổng LLM #1: chủ thể lấy từ cau_dan nhưng trich không có mẩu nào từ đó

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D151.K1

Chữ: Người lao động nước ngoài làm việc tại Việt Nam là người có quốc tịch nước ngoài và phải đáp ứng các điều kiện sau đây:

- **Lệch** ĐA#0 / LLM#0: chu_the.loai: ĐA='?' LLM='W'
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «có quốc tịch nước ngoài» chủ thể=người:? q1
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «có quốc tịch nước ngoài» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1
- **Chỉ ĐA có** #1: menh_de/ket_luan [khong,khang_dinh] «là người lao động nước ngoài làm việc tại Việt Nam» chủ thể=-:None q1 — lý do giu_chung: Định nghĩa X là Y: các dấu hiệu là dieu_kien, kết luận là 'là X' (K5).

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D151.K1.a

Chữ: Đủ 18 tuổi trở lên và có năng lực hành vi dân sự đầy đủ;
Câu dẫn: Người lao động nước ngoài làm việc tại Việt Nam là người có quốc tịch nước ngoài và phải đáp ứng các điều kiện sau đây:

- **Lệch** ĐA#0 / LLM#0: vai: ĐA='ket_luan' LLM='dieu_kien'; phuong_thuc: ĐA='phai' LLM='khong'
  - ĐA: menh_de/ket_luan [phai,khang_dinh] «đủ 18 tuổi trở lên» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1 — lý do tach: Tuổi và năng lực hành vi dân sự kiểm được độc lập, thiếu cái nào cũng không đủ điều kiện.
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «đủ 18 tuổi trở lên» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1
- **Lệch** ĐA#1 / LLM#1: vai: ĐA='ket_luan' LLM='dieu_kien'; phuong_thuc: ĐA='phai' LLM='khong'
  - ĐA: menh_de/ket_luan [phai,khang_dinh] «có năng lực hành vi dân sự đầy đủ» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «có năng lực hành vi dân sự đầy đủ» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1
- Lỗi cổng LLM #0: chủ thể lấy từ cau_dan nhưng trich không có mẩu nào từ đó
- Lỗi cổng LLM #1: chủ thể lấy từ cau_dan nhưng trich không có mẩu nào từ đó

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D151.K1.c

Chữ: Không phải là người đang trong thời gian chấp hành hình phạt hoặc chưa được xóa án tích hoặc đang trong thời gian bị truy cứu trách nhiệm hình sự theo quy định của pháp luật nước ngoài hoặc pháp luật Việt Nam;
Câu dẫn: Người lao động nước ngoài làm việc tại Việt Nam là người có quốc tịch nước ngoài và phải đáp ứng các điều kiện sau đây:

- **Lệch** ĐA#0 / LLM#0: vai: ĐA='ket_luan' LLM='dieu_kien'; phuong_thuc: ĐA='phai' LLM='khong'; menh_de: ĐA='là người đang trong thời gian chấp hành hình phạt' LLM='đang trong thời gian chấp hành hình phạt'; bo_ngu: ĐA=[] LLM=[('theo quy định của pháp luật nước ngoài hoặc pháp luật Việt Nam', 'group')]
  - ĐA: menh_de/ket_luan [phai,phu_dinh] «là người đang trong thời gian chấp hành hình phạt» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1 — lý do tach: Phủ định của 'A hoặc B hoặc C' = không A, không B, không C: ba yêu cầu cùng phải đúng (không dùng nhom_hoac).
  - LLM: menh_de/dieu_kien [khong,phu_dinh] «đang trong thời gian chấp hành hình phạt» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1 bổ ngữ=[('theo quy định của pháp luật nước ngoài hoặc pháp luật Việt Nam', 'group')]
- **Lệch** ĐA#1 / LLM#1: vai: ĐA='ket_luan' LLM='dieu_kien'; phuong_thuc: ĐA='phai' LLM='khong'; cuc: ĐA='phu_dinh' LLM='khang_dinh'; menh_de: ĐA='là người chưa được xóa án tích' LLM='được xóa án tích'; bo_ngu: ĐA=[] LLM=[('theo quy định của pháp luật nước ngoài hoặc pháp luật Việt Nam', 'group')]
  - ĐA: menh_de/ket_luan [phai,phu_dinh] «là người chưa được xóa án tích» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «được xóa án tích» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1 bổ ngữ=[('theo quy định của pháp luật nước ngoài hoặc pháp luật Việt Nam', 'group')] — lý do tach: Điều kiện phủ định 'chưa được xóa án tích' tương đương yêu cầu phải đã được xóa án tích.
- **Lệch** ĐA#2 / LLM#2: vai: ĐA='ket_luan' LLM='dieu_kien'; phuong_thuc: ĐA='phai' LLM='khong'; menh_de: ĐA='là người đang trong thời gian bị truy cứu trách nhiệm hình sự' LLM='đang trong thời gian bị truy cứu trách nhiệm hình sự'; bo_ngu: ĐA=[] LLM=[('theo quy định của pháp luật nước ngoài hoặc pháp luật Việt Nam', 'group')]
  - ĐA: menh_de/ket_luan [phai,phu_dinh] «là người đang trong thời gian bị truy cứu trách nhiệm hình sự» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1
  - LLM: menh_de/dieu_kien [khong,phu_dinh] «đang trong thời gian bị truy cứu trách nhiệm hình sự» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1 bổ ngữ=[('theo quy định của pháp luật nước ngoài hoặc pháp luật Việt Nam', 'group')]
- **Chỉ ĐA có** #3: bo_qua dan_chieu_mo  «theo quy định của pháp luật nước ngoài hoặc pháp luật Việt Nam»
- Lỗi cổng LLM #0: chủ thể lấy từ cau_dan nhưng trich không có mẩu nào từ đó
- Lỗi cổng LLM #1: chủ thể lấy từ cau_dan nhưng trich không có mẩu nào từ đó
- Lỗi cổng LLM #2: chủ thể lấy từ cau_dan nhưng trich không có mẩu nào từ đó

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D151.K1.d

Chữ: Có giấy phép lao động do cơ quan nhà nước có thẩm quyền của Việt Nam cấp, trừ trường hợp quy định tại Điều 154 của Bộ luật này.
Câu dẫn: Người lao động nước ngoài làm việc tại Việt Nam là người có quốc tịch nước ngoài và phải đáp ứng các điều kiện sau đây:

- **Chỉ ĐA có** #0: menh_de/ket_luan [phai,khang_dinh] «có giấy phép lao động» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1 bổ ngữ=[('do cơ quan nhà nước có thẩm quyền của Việt Nam cấp', 'this_clause')]
- **Chỉ LLM có** #0: menh_de/dieu_kien [khong,khang_dinh] «có giấy phép lao động do cơ quan nhà nước có thẩm quyền của Việt Nam cấp» chủ thể=Người lao động nước ngoài làm việc tại Việt Nam:W q1
- Lỗi cổng LLM #0: chủ thể lấy từ cau_dan nhưng trich không có mẩu nào từ đó

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D137.K1.a

Chữ: Mang thai từ tháng thứ 07 hoặc từ tháng thứ 06 nếu làm việc ở vùng cao, vùng sâu, vùng xa, biên giới, hải đảo;
Câu dẫn: Người sử dụng lao động không được sử dụng người lao động làm việc ban đêm, làm thêm giờ và đi công tác xa trong trường hợp sau đây:

- **Lệch** ĐA#0 / LLM#0: nhom_hoac: ĐA=None LLM='h1'
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «mang thai từ tháng thứ 07» chủ thể=người lao động:W q1
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «mang thai từ tháng thứ 07» chủ thể=người lao động:W q1 hoặc=h1
- Lỗi cổng LLM #0: chủ thể lấy từ cau_dan nhưng trich không có mẩu nào từ đó
- Lỗi cổng LLM #1: chủ thể lấy từ cau_dan nhưng trich không có mẩu nào từ đó
- Lỗi cổng LLM #2: chủ thể lấy từ cau_dan nhưng trich không có mẩu nào từ đó

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D146.K1

Chữ: Thời giờ làm việc của người chưa đủ 15 tuổi không được quá 04 giờ trong 01 ngày và 20 giờ trong 01 tuần; không được làm thêm giờ, làm việc vào ban đêm.

- **Lệch** ĐA#0 / LLM#0: quy_tac: ĐA='q1 (lệch nhóm với ĐA#[1, 2, 3])' LLM='q1'
  - ĐA: menh_de/ket_luan [cam,khang_dinh] «Thời giờ làm việc quá 04 giờ trong 01 ngày» chủ thể=người chưa đủ 15 tuổi:W q1 — lý do tach: Giới hạn ngày và tuần kiểm độc lập; câu sau cấm hai hành vi riêng.
  - LLM: menh_de/ket_luan [cam,khang_dinh] «thời giờ làm việc quá 04 giờ trong 01 ngày» chủ thể=người chưa đủ 15 tuổi:W q1
- **Lệch** ĐA#1 / LLM#1: quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0, 2, 3])' LLM='q2'
  - ĐA: menh_de/ket_luan [cam,khang_dinh] «Thời giờ làm việc quá 20 giờ trong 01 tuần» chủ thể=người chưa đủ 15 tuổi:W q1
  - LLM: menh_de/ket_luan [cam,khang_dinh] «thời giờ làm việc quá 20 giờ trong 01 tuần» chủ thể=người chưa đủ 15 tuổi:W q2
- **Lệch** ĐA#2 / LLM#2: chua_ro: ĐA=['chu_the'] LLM=[]; chu_the.loai: ĐA=None LLM='W'; doi_so: ĐA=['W'] LLM=[]; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0, 1, 3])' LLM='q3'
  - ĐA: menh_de/ket_luan [cam,khang_dinh] «làm thêm giờ» chủ thể=-:None q1 CHƯA RÕ=[('chủ thể mang lệnh cấm', 'chu_the')]
  - LLM: menh_de/ket_luan [cam,khang_dinh] «làm thêm giờ» chủ thể=người chưa đủ 15 tuổi:W q3
- **Lệch** ĐA#3 / LLM#3: chua_ro: ĐA=['chu_the'] LLM=[]; chu_the.loai: ĐA=None LLM='W'; doi_so: ĐA=['W'] LLM=[]; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0, 1, 2])' LLM='q4'
  - ĐA: menh_de/ket_luan [cam,khang_dinh] «làm việc vào ban đêm» chủ thể=-:None q1 CHƯA RÕ=[('chủ thể mang lệnh cấm', 'chu_the')]
  - LLM: menh_de/ket_luan [cam,khang_dinh] «làm việc vào ban đêm» chủ thể=người chưa đủ 15 tuổi:W q4

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D15.K2

Chữ: Tự do giao kết hợp đồng lao động nhưng không được trái pháp luật, thỏa ước lao động tập thể và đạo đức xã hội.

- **Lệch** ĐA#0 / LLM#0: chua_ro: ĐA=['chu_the'] LLM=[]; doi_so: ĐA=['C'] LLM=[]; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[2])' LLM='q1'
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «Tự do giao kết hợp đồng lao động» chủ thể=-:None q1 CHƯA RÕ=[('chủ thể', 'chu_the')]
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «Tự do giao kết hợp đồng lao động» chủ thể=-:None q1
- **Lệch** ĐA#2 / LLM#1: menh_de: ĐA='trái thỏa ước lao động tập thể' LLM='trái pháp luật, thỏa ước lao động tập thể và đạo đức xã hội'; liet_ke: ĐA=[] LLM=['pháp luật', 'thỏa ước lao động tập thể', 'đạo đức xã hội']; quy_tac: ĐA='q1 (lệch nhóm với ĐA#[0])' LLM=None
  - ĐA: menh_de/ket_luan [cam,khang_dinh] «trái thỏa ước lao động tập thể» chủ thể=-:None q1
  - LLM: menh_de/ket_luan [cam,khang_dinh] «trái pháp luật, thỏa ước lao động tập thể và đạo đức xã hội» chủ thể=-:None None liệt kê=['pháp luật', 'thỏa ước lao động tập thể', 'đạo đức xã hội'] — lý do giu_chung: Cấm vi phạm các giới hạn pháp lý và đạo đức được liệt kê.
- **Chỉ ĐA có** #1: menh_de/ket_luan [cam,khang_dinh] «trái pháp luật» chủ thể=-:None q1 — lý do tach: Trái luật, trái thỏa ước, trái đạo đức xã hội là ba căn cứ vi phạm riêng.
- **Chỉ ĐA có** #3: menh_de/ket_luan [cam,khang_dinh] «trái đạo đức xã hội» chủ thể=-:None q1
- Lỗi cổng LLM #1: menh_de thiếu quy_tac

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D24.K3

Chữ: Không áp dụng thử việc đối với người lao động giao kết hợp đồng lao động có thời hạn dưới 01 tháng.

- **Lệch** ĐA#0 / LLM#1: menh_de: ĐA='áp dụng thử việc' LLM='thử việc'; chu_the.loai: ĐA=None LLM='W'; doi_so: ĐA=['W'] LLM=[]
  - ĐA: menh_de/ket_luan [khong_ap_dung,khang_dinh] «áp dụng thử việc» chủ thể=-:None q1
  - LLM: menh_de/ket_luan [khong_ap_dung,khang_dinh] «thử việc» chủ thể=người lao động:W q1
- **Lệch** ĐA#1 / LLM#0: doi_so: ĐA=['C'] LLM=[]
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «giao kết hợp đồng lao động có thời hạn dưới 01 tháng» chủ thể=người lao động:W q1
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «giao kết hợp đồng lao động có thời hạn dưới 01 tháng» chủ thể=người lao động:W q1

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D24.K1

Chữ: Người sử dụng lao động và người lao động có thể thỏa thuận nội dung thử việc ghi trong hợp đồng lao động hoặc thỏa thuận về thử việc bằng việc giao kết hợp đồng thử việc.

- **Lệch** ĐA#0 / LLM#0: doi_so: ĐA=['C'] LLM=[]; nhom_hoac: ĐA=None LLM='h1'
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «thỏa thuận nội dung thử việc ghi trong hợp đồng lao động» chủ thể=Người sử dụng lao động và người lao động:('E', 'W') q1 — lý do tach: 'Hoặc' nối hai cách thỏa thuận được phép, không phải điều kiện: hai dòng duoc, không dùng nhom_hoac.
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «thỏa thuận nội dung thử việc ghi trong hợp đồng lao động» chủ thể=Người sử dụng lao động và người lao động:('E', 'W') q1 hoặc=h1
- **Lệch** ĐA#1 / LLM#1: doi_so: ĐA=['C'] LLM=[]; nhom_hoac: ĐA=None LLM='h1'
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «thỏa thuận về thử việc bằng việc giao kết hợp đồng thử việc» chủ thể=Người sử dụng lao động và người lao động:('E', 'W') q1
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «thỏa thuận về thử việc bằng việc giao kết hợp đồng thử việc» chủ thể=Người sử dụng lao động và người lao động:('E', 'W') q1 hoặc=h1

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D3.K1

Chữ: Người lao động là người làm việc cho người sử dụng lao động theo thỏa thuận, được trả lương và chịu sự quản lý, điều hành, giám sát của người sử dụng lao động.
Độ tuổi lao động tối thiểu của người lao động là đủ 15 tuổi, trừ trường hợp quy định tại Mục 1 Chương XI của Bộ luật này.
Câu dẫn: Trong Bộ luật này, các từ ngữ dưới đây được hiểu như sau:

- **Lệch** ĐA#0 / LLM#0: menh_de: ĐA='là người làm việc cho người sử dụng lao động' LLM='làm việc cho người sử dụng lao động theo thỏa thuận'; chu_the.loai: ĐA='?' LLM='W'; bo_ngu: ĐA=[('theo thỏa thuận', 'this_clause')] LLM=[]
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «là người làm việc cho người sử dụng lao động» chủ thể=người:? q1 bổ ngữ=[('theo thỏa thuận', 'this_clause')] — lý do tach: Định nghĩa gồm ba dấu hiệu, mỗi dấu hiệu kiểm độc lập; thiếu một dấu hiệu thì không phải người lao động.
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «làm việc cho người sử dụng lao động theo thỏa thuận» chủ thể=người:W q1
- **Lệch** ĐA#1 / LLM#1: chu_the.loai: ĐA='?' LLM='W'; doi_so: ĐA=['A'] LLM=[]
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «được trả lương» chủ thể=người:? q1 — lý do tach: 'Được' ở đây là bị động trong định nghĩa, không phải quyền: phuong_thuc khong.
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «được trả lương» chủ thể=người:W q1
- **Lệch** ĐA#2 / LLM#2: chu_the.loai: ĐA='?' LLM='W'
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «chịu sự quản lý, điều hành, giám sát của người sử dụng lao động» chủ thể=người:? q1 — lý do giu_chung: Quản lý, điều hành, giám sát cùng mô tả một quan hệ lệ thuộc; giữ chung.
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «chịu sự quản lý, điều hành, giám sát của người sử dụng lao động» chủ thể=người:W q1
- **Lệch** ĐA#3 / LLM#3: chu_the.loai: ĐA=None LLM='W'; doi_so: ĐA=['?'] LLM=[]
  - ĐA: menh_de/ket_luan [khong,khang_dinh] «là người lao động» chủ thể=-:None q1 — lý do giu_chung: Định nghĩa X là Y: các dấu hiệu là dieu_kien, kết luận là 'là X' (K5).
  - LLM: menh_de/ket_luan [khong,khang_dinh] «là Người lao động» chủ thể=người:W q1
- **Lệch** ĐA#4 / LLM#4: menh_de: ĐA='Độ tuổi lao động tối thiểu là đủ 15 tuổi' LLM='Độ tuổi lao động tối thiểu của người lao động là đủ 15 tuổi'
  - ĐA: menh_de/ket_luan [khong,khang_dinh] «Độ tuổi lao động tối thiểu là đủ 15 tuổi» chủ thể=người lao động:W q2
  - LLM: menh_de/ket_luan [khong,khang_dinh] «Độ tuổi lao động tối thiểu của người lao động là đủ 15 tuổi» chủ thể=người lao động:W q2
- **Lệch** ĐA#5 / LLM#5: chua_ro: ĐA=['khac'] LLM=[]
  - ĐA: con_tro/ngoai_le → [] gắn=4 CHƯA RÕ=[('Mục 1 Chương XI của Bộ luật này', 'khac')] — lý do chua_ro: Dẫn chiếu rõ nhưng không có đích trong dan_chieu_1_2: vẫn là con_tro, targets để trống.
  - LLM: con_tro/ngoai_le → [] gắn=4 — lý do chua_ro: Dẫn chiếu tới Mục 1 Chương XI chưa có mã cụ thể trong dan_chieu.
- Lỗi cổng LLM #5: con_tro không targets mà không có chua_ro

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D9.K1

Chữ: Việc làm là hoạt động lao động tạo ra thu nhập mà pháp luật không cấm.

- **Lệch** ĐA#0 / LLM#0: menh_de: ĐA='hoạt động lao động tạo ra thu nhập' LLM='là hoạt động lao động tạo ra thu nhập mà pháp luật không cấm'; doi_so: ĐA=['?'] LLM=[]; bo_ngu: ĐA=[('mà pháp luật không cấm', 'this_clause')] LLM=[]
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «hoạt động lao động tạo ra thu nhập» chủ thể=-:None q1 bổ ngữ=[('mà pháp luật không cấm', 'this_clause')] — lý do gan_bo_ngu: 'Mà pháp luật không cấm' là dấu hiệu giới hạn của định nghĩa, ghi bổ ngữ; không phải dẫn chiếu tới quy phạm cụ thể.
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «là hoạt động lao động tạo ra thu nhập mà pháp luật không cấm» chủ thể=-:None q1
- **Lệch** ĐA#1 / LLM#1: doi_so: ĐA=['?'] LLM=[]
  - ĐA: menh_de/ket_luan [khong,khang_dinh] «là việc làm» chủ thể=-:None q1 — lý do giu_chung: Định nghĩa X là Y: các dấu hiệu là dieu_kien, kết luận là 'là X' (K5).
  - LLM: menh_de/ket_luan [khong,khang_dinh] «là Việc làm» chủ thể=-:None q1

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

## D14.K1

Chữ: Hợp đồng lao động phải được giao kết bằng văn bản và được làm thành 02 bản, người lao động giữ 01 bản, người sử dụng lao động giữ 01 bản, trừ trường hợp quy định tại khoản 2 Điều này.
Hợp đồng lao động được giao kết thông qua phương tiện điện tử dưới hình thức thông điệp dữ liệu theo quy định của pháp luật về giao dịch điện tử có giá trị như hợp đồng lao động bằng văn bản.

- **Lệch** ĐA#0 / LLM#0: menh_de: ĐA='được giao kết bằng văn bản' LLM='giao kết bằng văn bản'
  - ĐA: menh_de/ket_luan [phai,khang_dinh] «được giao kết bằng văn bản» chủ thể=Hợp đồng lao động:C q1
  - LLM: menh_de/ket_luan [phai,khang_dinh] «giao kết bằng văn bản» chủ thể=Hợp đồng lao động:C q1
- **Lệch** ĐA#1 / LLM#1: menh_de: ĐA='được làm thành 02 bản, người lao động giữ 01 bản, người sử dụng lao động giữ 01 bản' LLM='làm thành 02 bản, người lao động giữ 01 bản, người sử dụng lao động giữ 01 bản'
  - ĐA: menh_de/ket_luan [phai,khang_dinh] «được làm thành 02 bản, người lao động giữ 01 bản, người sử dụng lao động giữ 01 bản» chủ thể=Hợp đồng lao động:C q1 — lý do giu_chung: Số bản và việc mỗi bên giữ một bản là một yêu cầu tập thể về lập và giao bản hợp đồng.
  - LLM: menh_de/ket_luan [phai,khang_dinh] «làm thành 02 bản, người lao động giữ 01 bản, người sử dụng lao động giữ 01 bản» chủ thể=Hợp đồng lao động:C q1
- **Lệch** ĐA#3 / LLM#3: menh_de: ĐA='được giao kết thông qua phương tiện điện tử dưới hình thức thông điệp dữ liệu' LLM='giao kết thông qua phương tiện điện tử dưới hình thức thông điệp dữ liệu theo quy định của pháp luật về giao dịch điện tử'
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «được giao kết thông qua phương tiện điện tử dưới hình thức thông điệp dữ liệu» chủ thể=Hợp đồng lao động:C q2
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «giao kết thông qua phương tiện điện tử dưới hình thức thông điệp dữ liệu theo quy định của pháp luật về giao dịch điện tử» chủ thể=Hợp đồng lao động:C q2
- **Lệch** ĐA#4 / LLM#4: doi_so: ĐA=['C'] LLM=[]
  - ĐA: menh_de/ket_luan [khong,khang_dinh] «có giá trị như hợp đồng lao động bằng văn bản» chủ thể=Hợp đồng lao động:C q2
  - LLM: menh_de/ket_luan [khong,khang_dinh] «có giá trị như hợp đồng lao động bằng văn bản» chủ thể=Hợp đồng lao động:C q2
- **Chỉ ĐA có** #5: bo_qua dan_chieu_ngoai  «theo quy định của pháp luật về giao dịch điện tử»

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D113.K1

Chữ: Người lao động làm việc đủ 12 tháng cho một người sử dụng lao động thì được nghỉ hằng năm, hưởng nguyên lương theo hợp đồng lao động như sau:

- **Lệch** ĐA#2 / LLM#1: menh_de: ĐA='hưởng nguyên lương theo hợp đồng lao động' LLM='nghỉ hằng năm, hưởng nguyên lương theo hợp đồng lao động'; doi_so: ĐA=['A', 'C'] LLM=[]
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «hưởng nguyên lương theo hợp đồng lao động» chủ thể=Người lao động:W q1
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «nghỉ hằng năm, hưởng nguyên lương theo hợp đồng lao động» chủ thể=Người lao động:W q1
- **Chỉ ĐA có** #1: menh_de/ket_luan [duoc,khang_dinh] «nghỉ hằng năm» chủ thể=Người lao động:W q1 — lý do tach: Được nghỉ và được hưởng nguyên lương là hai quyền vi phạm riêng được.

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D113.K1.a

Chữ: 12 ngày làm việc đối với người làm công việc trong điều kiện bình thường;
Câu dẫn: Người lao động làm việc đủ 12 tháng cho một người sử dụng lao động thì được nghỉ hằng năm, hưởng nguyên lương theo hợp đồng lao động như sau:

- **Lệch** ĐA#0 / LLM#1: doi_so: ĐA=['D'] LLM=[]
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «nghỉ hằng năm 12 ngày làm việc» chủ thể=Người lao động:W q1 — lý do ke_thua: Mục con chỉ là con số; vị ngữ 'được nghỉ hằng năm' và chủ thể kế thừa từ câu dẫn.
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «nghỉ hằng năm 12 ngày làm việc» chủ thể=người làm công việc trong điều kiện bình thường:W q1 — lý do ke_thua: Kế thừa vị ngữ nghỉ hằng năm từ câu dẫn khoản 1.
- **Lệch** ĐA#1 / LLM#0: doi_so: ĐA=['J'] LLM=[]
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «làm công việc trong điều kiện bình thường» chủ thể=người:W q1
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «làm công việc trong điều kiện bình thường» chủ thể=người làm công việc trong điều kiện bình thường:W q1

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D129.K1

Chữ: Người lao động làm hư hỏng dụng cụ, thiết bị hoặc có hành vi khác gây thiệt hại tài sản của người sử dụng lao động thì phải bồi thường theo quy định của pháp luật hoặc nội quy lao động của người sử dụng lao động.
Trường hợp người lao động gây thiệt hại không nghiêm trọng do sơ suất với giá trị không quá 10 tháng lương tối thiểu vùng do Chính phủ công bố được áp dụng tại nơi người lao động làm việc thì người lao động phải bồi thường nhiều nhất là 03 tháng tiền lương và bị khấu trừ hằng tháng vào lương theo quy định tại khoản 3 Điều 102 của Bộ luật này.

- **Lệch** ĐA#0 / LLM#0: bo_ngu: ĐA=[('của người sử dụng lao động', 'group')] LLM=[]
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «làm hư hỏng dụng cụ, thiết bị» chủ thể=Người lao động:W q1 bổ ngữ=[('của người sử dụng lao động', 'group')] hoặc=h1 — lý do gan_bo_ngu: 'Của người sử dụng lao động' về nghĩa áp cả cho dụng cụ, thiết bị (tài sản của NSDLĐ).
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «làm hư hỏng dụng cụ, thiết bị» chủ thể=Người lao động:W q1 hoặc=h1
- **Lệch** ĐA#2 / LLM#2: bo_ngu: ĐA=[] LLM=[('theo quy định của pháp luật hoặc nội quy lao động của người sử dụng lao động', 'this_clause')]
  - ĐA: menh_de/ket_luan [phai,khang_dinh] «bồi thường» chủ thể=Người lao động:W q1
  - LLM: menh_de/ket_luan [phai,khang_dinh] «bồi thường» chủ thể=Người lao động:W q1 bổ ngữ=[('theo quy định của pháp luật hoặc nội quy lao động của người sử dụng lao động', 'this_clause')]
- **Lệch** ĐA#7 / LLM#4: doi_so: ĐA=['A'] LLM=[]
  - ĐA: menh_de/ket_luan [phai,khang_dinh] «bồi thường nhiều nhất là 03 tháng tiền lương» chủ thể=người lao động:W q2
  - LLM: menh_de/ket_luan [phai,khang_dinh] «bồi thường nhiều nhất là 03 tháng tiền lương» chủ thể=người lao động:W q2
- **Lệch** ĐA#8 / LLM#5: phuong_thuc: ĐA='phai' LLM='khong'; doi_so: ĐA=['A'] LLM=[]
  - ĐA: menh_de/ket_luan [phai,khang_dinh] «bị khấu trừ hằng tháng vào lương» chủ thể=người lao động:W q2
  - LLM: menh_de/ket_luan [khong,khang_dinh] «bị khấu trừ hằng tháng vào lương» chủ thể=người lao động:W q2
- **Chỉ ĐA có** #3: bo_qua dan_chieu_mo  «theo quy định của pháp luật hoặc nội quy lao động của người sử dụng lao động»
- **Chỉ ĐA có** #4: menh_de/dieu_kien [khong,khang_dinh] «gây thiệt hại không nghiêm trọng» chủ thể=người lao động:W q2 — lý do tach: Ba điều kiện cộng dồn (không nghiêm trọng, do sơ suất, giá trị ≤ 10 tháng lương tối thiểu vùng), kiểm độc lập; 'không' nằm trong nội dung nên cuc khang_dinh.
- **Chỉ ĐA có** #5: menh_de/dieu_kien [khong,khang_dinh] «gây thiệt hại do sơ suất» chủ thể=người lao động:W q2
- **Chỉ ĐA có** #6: menh_de/dieu_kien [khong,khang_dinh] «giá trị không quá 10 tháng lương tối thiểu vùng» chủ thể=-:None q2 bổ ngữ=[('do Chính phủ công bố được áp dụng tại nơi người lao động làm việc', 'this_clause')]
- **Chỉ LLM có** #3: menh_de/dieu_kien [khong,khang_dinh] «gây thiệt hại không nghiêm trọng do sơ suất với giá trị không quá 10 tháng lương tối thiểu vùng do Chính phủ công bố được áp dụng tại nơi người lao động làm việc» chủ thể=người lao động:W q2

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D108

Chữ: Người sử dụng lao động có quyền yêu cầu người lao động làm thêm giờ vào bất kỳ ngày nào mà không bị giới hạn về số giờ làm thêm theo quy định tại Điều 107 của Bộ luật này và người lao động không được từ chối trong trường hợp sau đây:

- **Lệch** ĐA#0 / LLM#0: menh_de: ĐA='yêu cầu người lao động làm thêm giờ vào bất kỳ ngày nào' LLM='yêu cầu người lao động làm thêm giờ vào bất kỳ ngày nào mà không bị giới hạn về số giờ làm thêm'; doi_so: ĐA=['W', 'D'] LLM=['W']
  - ĐA: menh_de/ket_luan [duoc,khang_dinh] «yêu cầu người lao động làm thêm giờ vào bất kỳ ngày nào» chủ thể=Người sử dụng lao động:E q1
  - LLM: menh_de/ket_luan [duoc,khang_dinh] «yêu cầu người lao động làm thêm giờ vào bất kỳ ngày nào mà không bị giới hạn về số giờ làm thêm» chủ thể=Người sử dụng lao động:E q1
- **Lệch** ĐA#2 / LLM#1: gan_vao: ĐA='1 (tức LLM#dòng chưa ghép)' LLM=0
  - ĐA: con_tro/ket_luan → ['D107'] gắn=1 — lý do gan_bo_ngu: Không phải 'trừ trường hợp': Điều 108 gạt giới hạn của Điều 107; con trỏ gắn vế 'không bị giới hạn về số giờ làm thêm'.
  - LLM: con_tro/ket_luan → ['D107'] gắn=0
- **Chỉ ĐA có** #1: menh_de/ket_luan [khong,phu_dinh] «bị giới hạn về số giờ làm thêm» chủ thể=Người sử dụng lao động:E q1

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

## D108.K1

Chữ: Thực hiện lệnh động viên, huy động bảo đảm nhiệm vụ quốc phòng, an ninh theo quy định của pháp luật;
Câu dẫn: Người sử dụng lao động có quyền yêu cầu người lao động làm thêm giờ vào bất kỳ ngày nào mà không bị giới hạn về số giờ làm thêm theo quy định tại Điều 107 của Bộ luật này và người lao động không được từ chối trong trường hợp sau đây:

- **Lệch** ĐA#0 / LLM#0: chu_the.loai: ĐA=None LLM='W'
  - ĐA: menh_de/dieu_kien [khong,khang_dinh] «Thực hiện lệnh động viên, huy động bảo đảm nhiệm vụ quốc phòng, an ninh» chủ thể=-:None q1 — lý do giu_chung: Một tình huống (thực hiện lệnh động viên, huy động vì quốc phòng, an ninh); chủ thể là tình huống làm thêm giờ, không gán cho W hay E.
  - LLM: menh_de/dieu_kien [khong,khang_dinh] «thực hiện lệnh động viên, huy động bảo đảm nhiệm vụ quốc phòng, an ninh» chủ thể=người lao động:W q1
- Lỗi cổng LLM #0: chủ thể lấy từ cau_dan nhưng trich không có mẩu nào từ đó

Phán: (ĐA đúng / LLM đúng / cả hai sai, sửa thành ...)

