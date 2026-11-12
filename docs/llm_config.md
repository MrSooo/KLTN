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
trich.provider     = anthropic
trich.model        = claude-sonnet-5-5
trich.rpm          = 30
trich.luot_moi_ngay = 1000
trich.max_output_tokens = 16000
trich.thinking     = between_tools
temperature        = (không đặt: dùng mặc định của server)
thinking           = (không đặt)
max_output_tokens  = 32000
```

## Vai của hai model
| Vai | Model | Dùng ở bước (theo plan) |
|---|---|---|
| chính | `gemini-3.5-flash-lite` | L3 liên kết `details` còn sót, L4 phân loại điều, L6 chỉ thị lạ / hết hiệu lực theo chủ đề / khớp sự kiện kích hoạt, L7 nháp sổ khái niệm, L8 ngoại lệ ngầm, L9 trích quy tắc, L10 câu hỏi thành dữ kiện |
| kiểm độc lập | `gemini-3.8-flash` | L7 kiểm C4 và lượt trích lại độc lập. Plan yêu cầu lượt kiểm dùng model khác lượt chính; hạn mức thấp (20/ngày) nên phải gom nhiều đơn vị mỗi lượt |

## Vai thứ ba: `trich` (Claude, thêm 12/11/2026, A34; user đồng ý sau khi Gemini quá tải liên tục lúc chạy 1.6A)
Vai `trich` là trích xuất ngữ nghĩa từ 1.6 trở đi (1.6 gạch cụm, sau này 1.6B, 1.7, 1.8). Nó là vai MỚI chứ không thay `chinh`, vì `links.py` (2.2) dùng `chinh` và `kiem` làm hai model độc lập kiểm chéo nhau, và cache của 2.2 khoá theo tên model: đổi `chinh` sang Claude làm `--llm replay` của 2.2 hụt cache.
- **Nhà cung cấp:** Anthropic, model `claude-sonnet-5-5`, trả phí theo token (không phải gói miễn phí). Giá lúc khoá: $2 / $10 mỗi triệu token vào / ra (theo bảng giá của skill claude-api lưu 03/11; xem lại trên Console). Khoá nằm ở biến môi trường `ANTHROPIC_API_KEY`, không ghi vào repo. Gói `anthropic` cài trong `.venv`.
- **Không có hạn mức lượt theo ngày của nhà cung cấp:** `trich.luot_moi_ngay = 1000` chỉ là chặn an toàn của dự án (chống vòng lặp tốn tiền), không phải số của Anthropic. Chi phí thật xem ở Console; mỗi lượt gọi in số token vào / ra ra stderr.
- **Tắt suy nghĩ (`trich.thinking`):** code gửi `thinking: {"type": <giá trị>}`. Sonnet 5.5 chỉ nhận `between_tools` (`disabled` bị 400); Haiku 5.5 chỉ nhận `disabled` (`between_tools` bị 400; chưa kiểm bằng API thật). Mặc định của model là bật suy nghĩ và tính vào token ra, làm tốn thêm nhiều lần; việc gạch cụm nguyên văn đã có cổng máy kiểm lại. Chế độ này KHÔNG nằm trong khoá cache: nếu bật lại suy nghĩ mà không đổi model thì phải nâng `PROMPT_VERSION` của tác vụ, không thì cache cũ bị dùng lại âm thầm.
- **Cấu hình đang commit là Sonnet** vì cache 1.6A (204 lô, 13/11) do Sonnet sinh ra và khoá cache có tên model. **Đã đồng ý chuyển sang Haiku 5.5 (13/11, A35), CHƯA chạy:** đổi đúng hai dòng `trich.model = claude-haiku-5-5` và `trich.thinking = disabled`. Hệ quả: `trich.model` là một khoá cho MỌI tác vụ của vai (1.6, 1.6B, 1.7, 1.8), nên chuyển sang Haiku nghĩa là 1.6A cũng phải chạy lại bằng Haiku (khoảng $0,13); 204 bản ghi Sonnet vẫn nằm trong cache làm mốc so sánh nhưng `replay` sẽ báo 0/204 cho tới khi chạy Haiku. Giá Haiku 5.5 theo bảng skill claude-api lưu 03/11: $0,10 / $0,50 mỗi triệu token (gấp 1/20 Sonnet).
- **`trich.max_output_tokens`:** 16000, riêng cho vai này (`max_output_tokens` ở trên là của Gemini, tính cả token "suy nghĩ").
- **Ngày khoá của vai này:** 2026-11-12. Mọi bản ghi của một tác vụ nên do cùng một model sinh ra; 4 lô gạch cụm Gemini đã có (Điều 1 đến 4) không dùng lại.
- **Không bật `fallbacks` phía server** của Anthropic: nó có thể đổi model giữa chừng. `stop_reason` khác `end_turn` (từ chối, cụt đầu ra) là lỗi, không lưu cache.

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
