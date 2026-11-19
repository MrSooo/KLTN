# Cấu hình LLM

File này vừa là tài liệu vừa là **cấu hình đọc bởi máy**: `src/llm_client.py` đọc mọi dòng dạng `khoá = giá trị` ở đầu dòng. Không thêm dòng nào khác bắt đầu bằng mẫu đó trong phần chữ. Đổi model thì khoá cache đổi theo (khoá cache chứa tên model), nên bản ghi cũ không còn khớp ở chế độ `replay`.

## Giá trị cho máy đọc
```
khoa_ngay          = 2026-11-07
chinh.model        = gemini-3.5-flash-lite
chinh.rpm          = 15
chinh.luot_moi_ngay = 500
kiem.model         = gemini-3.8-flash
kiem.rpm           = 5
kiem.luot_moi_ngay = 20
trich.provider     = anthropic
trich.model        = claude-opus-5-5
trich.rpm          = 30
trich.luot_moi_ngay = 1000
trich.max_output_tokens = 16000
trich.thinking     = between_tools
ten.model          = claude-sonnet-5-5
hop_cat.model      = claude-sonnet-5-5
hop_cat.effort     = high
api.provider       = ckey
api.model          = deepseek-v4.1-flash
api.base_url       = https://api.xah.io
api.rpm            = 60
api.luot_moi_ngay  = 3000
api.max_output_tokens = 32000
ckey.ten.model     = deepseek-v4.1-flash
ckey.hop_cat.model = deepseek-v4.1-flash
ckey.hop_cat.effort = khong_co
menh_de.prompt_version = menh-de-3
ckey.menh_de.prompt_version = menh-de-4
ckey2.ten.model     = deepseek-v4.1-flash
ckey2.hop_cat.model = deepseek-v4.1-flash
ckey2.hop_cat.effort = khong_co
ckey2.menh_de.prompt_version = menh-de-5
ckey3.ten.model     = deepseek-v4.1-flash
ckey3.hop_cat.model = deepseek-v4.1-flash
ckey3.hop_cat.effort = khong_co
ckey3.menh_de.prompt_version = menh-de-6
temperature        = (không đặt: dùng mặc định của server)
thinking           = (không đặt)
max_output_tokens  = 32000
```

## Vai và model
| Vai | Model | Nhà cung cấp | Dùng ở bước |
|---|---|---|---|
| `chinh` | `gemini-3.5-flash-lite` | Google Gemini (gói miễn phí) | 2.2 nối văn bản: đề xuất cạnh `details` cho văn bản không nêu số Điều |
| `kiem` | `gemini-3.8-flash` | Google Gemini (gói miễn phí) | 2.2: lượt kiểm độc lập (model khác, cùng đầu vào); hạn mức thấp |
| `trich` | `claude-opus-5-5` | Anthropic (trả phí theo token) | 1.6A bản cũ (`concepts.py`): khoá cache của 204 lô đã chạy bằng phiên Claude Code |
| `ten` | `claude-sonnet-5-5` | không có đường gọi API | 1.6B: nhãn model nằm trong khoá cache và đối chiếu model do phiên Claude Code tự khai |
| `hop_cat` | `claude-sonnet-5-5`, effort `high` | không có đường gọi API | model và effort mà hộp cát của 1.6A theo KU, 1.6B, 1.7, 1.9 đòi trong nhật ký (A39; đưa vào cấu hình ở A46) |
| `api` | `deepseek-v4.1-flash` | máy chủ trung gian ckey (`api.base_url`, trả phí theo token) | bộ chạy hộp cát `sandbox_api.py` (A46) |

Ghi chú:
- `trich` và `ten` không còn gọi API từ A36: phần LLM của bước 1.6 chạy bằng phiên Claude Code trong thư mục làm việc ngoài repo (`docs/operations/llm_sandbox.md`). Khoá cấu hình vẫn cần để `replay` đọc đúng bản ghi cache.
- Bản làm lại của bước 1.6A (`propositions.py`) ghi model và effort vào thư mục làm việc (`cau_hinh.json`) lúc dựng thư mục; không truyền tham số thì lấy `trich.model`. Đường chạy đã chốt (A39) là Sonnet 5.5, effort `high`, nên phải truyền tường minh `claude-sonnet-5-5 high` khi dựng (xem `docs/operations/llm_sandbox.md`). Model nằm trong khoá cache của bản ghi.
- `ten` không nằm trong `EXTRA_ROLES` của `llm_client.py` vì không có đường gọi API. `api` cũng không, để `run_all --llm live` không đòi khoá ckey.
- Khoá `ckey.<khoá>` chỉ có hiệu lực khi `KLTN_LLM_RUN=ckey` (`run_all --llm-run ckey`): nó đè `<khoá>` để lần chạy ckey dùng model của ckey cho `ten` và `hop_cat`, còn lần chạy mặc định giữ nguyên (A46).
- `api.max_output_tokens = 32000`: trần an toàn để lô 1.6A dài không bị cụt (cụt là lỗi, không lưu cache); ở thí điểm 19/11 mỗi lô ra 150 đến 1.400 token. Giá `deepseek-v4.1-flash` ngày 19/11: vào 1.200, ra 4.800 VND mỗi triệu token. `api.rpm = 60` và `api.luot_moi_ngay = 3000` là chặn an toàn của dự án (máy chủ cho 300 request mỗi phút).
- `chinh` và `kiem` được giữ là Gemini vì bước 2.2 dùng hai model độc lập kiểm chéo nhau và khoá cache của nó có tên model; đổi `chinh` sang Claude làm `replay` của bước 2.2 hụt cache (A34).

## Khoá API
Chỉ nằm trong biến môi trường, không ghi vào repo, chat, test hay báo cáo: `GEMINI_API_KEY` (bước 2.2), `ANTHROPIC_API_KEY` (mã gọi Claude, chỉ khi chạy `--llm live` ở các bước dùng vai `trich`), `CKEY_API_KEY` (vai `api`, bộ chạy hộp cát, A46). Trên Windows đặt một lần bằng `setx <TÊN> "<khoá>"` ở terminal riêng, rồi mở terminal mới (`setx` không đổi terminal đang mở); biến gắn với tài khoản Windows chứ không gắn với `.venv`. `--llm live` cần `.venv` có gói `google-genai` (Gemini) hoặc `anthropic` (Claude). Kiểm ID model mà không tốn lượt: `python -I src/llm_client.py --check-models`.

## Hạn mức
- `chinh.luot_moi_ngay` và `kiem.luot_moi_ngay` là hạn mức đo trên Google AI Studio ngày 03/11/2026 (có thể đổi). `llm_client` tự đếm lượt theo ngày và theo vai; chạm giới hạn thì dừng gọn và chạy tiếp hôm sau từ cache. `kiem` chỉ 20 lượt mỗi ngày nên phải gom nhiều đơn vị mỗi lượt.
- `trich.luot_moi_ngay = 1000` chỉ là chặn an toàn của dự án (chống vòng lặp tốn tiền), không phải hạn mức của Anthropic. Chi phí thật xem ở Console; mỗi lượt gọi in số token vào và ra ra stderr.

## Tham số gọi
- `trich.thinking`: mã gửi `thinking: {"type": <giá trị>}`. Sonnet 5.5 chỉ nhận `between_tools` (`disabled` bị lỗi 400); Haiku 5.5 chỉ nhận `disabled` (chưa kiểm bằng API thật). Chế độ suy nghĩ không nằm trong khoá cache: bật lại mà không đổi model thì phải nâng `PROMPT_VERSION` của tác vụ. Không đặt `temperature`, `top_p`, `tool_choice` (Sonnet 5.5 trả lỗi 400). Không bật `fallbacks` phía server vì có thể đổi model giữa chừng. `stop_reason` khác `end_turn` (từ chối, cụt đầu ra) là lỗi và không lưu cache.
- `max_output_tokens = 32000` là của Gemini (token "suy nghĩ" tính vào hạn mức đầu ra); `trich.max_output_tokens = 16000` riêng cho Claude.
- `temperature` và `thinking` của Gemini để mặc định. Tính tái lập đến từ **cache** `data/llm_cache/` (cùng đầu vào đọc lại đúng phản hồi cũ), không đến từ temperature.

## Vì sao ban đầu chọn model nhẹ
LLM chỉ làm việc đọc hiểu và đề xuất ngữ nghĩa; mọi đề xuất đều qua cổng tự động (khớp nguyên văn, vị từ trong sổ, biên dịch s(CASP), bộ quét) nên không cần model mạnh, và model nhẹ có hạn mức lớn hơn, hợp với việc chạy lại nhiều lô. Bước 1.6 sau đó dùng model Claude lớn hơn vì Gemini quá tải khi chạy bước này (A34) và vì chất lượng gạch mệnh đề quyết định mọi bước sau (A39); lý do này cần được ghi trong bài báo cáo.

## Chưa kiểm
- ID `gemini-3.5-flash-lite` và `gemini-3.8-flash` xác nhận bằng `models.list()` ngày 04/11/2026, chưa kiểm lại.
- Chưa đo hạn mức của `gemini-3.1-flash-lite`; nếu đủ lớn có thể thay `gemini-3.8-flash` làm model kiểm để khỏi bị giới hạn 20 lượt mỗi ngày.

## Quyền riêng tư
Gói miễn phí của Google có thể dùng nội dung để cải thiện sản phẩm. Chỉ gửi văn bản luật công khai.
