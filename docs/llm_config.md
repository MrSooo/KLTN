# Cấu hình LLM (v2, Bộ luật Lao động): user đã duyệt 2026-11-07

Ngày khoá: 2026-11-07. Nhà cung cấp: Google Gemini, gói miễn phí. Khoá API chỉ nằm trong biến môi trường `GEMINI_API_KEY`, không ghi vào repo.

## Vì sao chọn model nhẹ
Thầy xác định LLM chỉ làm việc đọc hiểu và đề xuất ngữ nghĩa (phân loại điều, đề xuất liên kết, nháp sổ khái niệm, chuyển câu hỏi thành dữ kiện). Mọi đề xuất đều qua cổng tự động (khớp nguyên văn, vị từ trong sổ, biên dịch s(CASP), bộ quét) nên không cần model mạnh. Model nhẹ có hạn mức lớn hơn nhiều, hợp với việc chạy lại nhiều lô.

## Giá trị cho máy đọc (wrapper `src/llm_client.py` sẽ đọc các dòng `khoá = giá trị` trong khối này)
```
khoa_ngay          = 2026-11-07
chinh.model        = gemini-3.5-flash-lite
chinh.rpm          = 15
chinh.luot_moi_ngay = 500
kiem.model         = gemini-3.8-flash
kiem.rpm           = 5
kiem.luot_moi_ngay = 20
temperature        = (không đặt: dùng mặc định của server)
thinking           = (không đặt)
max_output_tokens  = 32000
```

## Vai của hai model
| Vai | Model | Dùng ở bước (theo plan) |
|---|---|---|
| chính | `gemini-3.5-flash-lite` | L3 liên kết `details` còn sót, L4 phân loại điều, L6 chỉ thị lạ / hết hiệu lực theo chủ đề / khớp sự kiện kích hoạt, L7 nháp sổ khái niệm, L8 ngoại lệ ngầm, L9 trích quy tắc, L10 câu hỏi thành dữ kiện |
| kiểm độc lập | `gemini-3.8-flash` | L7 kiểm C4 và lượt trích lại độc lập. Plan yêu cầu lượt kiểm dùng model khác lượt chính; hạn mức thấp (20/ngày) nên phải gom nhiều đơn vị mỗi lượt |

## Giải thích ngắn các dòng
- **Ngày khoá:** từ ngày này, model ID không đổi giữa chừng để kết quả so sánh được. Đổi model thì ghi ngày mới và chạy lại từ cache mới (khoá cache có tên model).
- **Temperature, thinking:** để trống vì `src/a4_llm.py` hiện không đặt hai giá trị này và đã chạy live được (04/11, 19 ca, không ca SAI). Tính tái lập đến từ **cache** `data/llm_cache/` (cùng đầu vào đọc lại đúng phản hồi cũ), không đến từ temperature.
- **max_output_tokens = 32000:** lấy theo `GEMINI_MAX_TOKENS` trong code (token "suy nghĩ" của Gemini tính vào hạn mức đầu ra).
- **Hạn mức:** số user đo trên AI Studio ngày 03/11, có thể đổi. Wrapper tự đếm lượt theo ngày, chạm giới hạn thì dừng gọn và chạy tiếp hôm sau từ cache.

## Chưa kiểm
- ID `gemini-3.5-flash-lite` và `gemini-3.8-flash` được xác nhận bằng `models.list()` ngày 04/11, chưa kiểm lại hôm nay.
- Chưa đo hạn mức của `gemini-3.1-flash-lite`; nếu đủ lớn, có thể thay `gemini-3.8-flash` làm model kiểm để khỏi bị giới hạn 20 lượt/ngày.

## Lưu ý quyền riêng tư
Gói miễn phí có thể bị Google dùng nội dung để cải thiện sản phẩm. Chỉ gửi văn bản luật công khai.
