"""A4-C: đề xuất chuẩn hoá khối chỉ thị sửa đổi bằng Claude, có lưu kết quả để chạy lại tất định.

Chỉ module này gọi API. Nó KHÔNG import a4_versions: a4_versions.normalize_block gọi ClaudeProposer.propose(khối, phản hồi), rồi tự
dựng dòng chuẩn, parse bằng văn phạm chuẩn và kiểm V1-V3 (xem a4_versions). Đề xuất không qua kiểm thì không được áp.

Chế độ (cờ --llm của a4_versions.py apply):
  replay  chỉ đọc kết quả đã lưu trong data/llm_cache/a4/<khoá>.json; thiếu thì lỗi E_LLM_CACHE (không gọi mạng)
  live    như replay, thiếu thì gọi API rồi lưu (cần ANTHROPIC_API_KEY; chạy bằng .venv/bin/python vì cần gói anthropic)
Khoá = sha256 của (mô hình, PROMPT_VERSION, chữ của khối, phản hồi của vòng trước), nên đổi prompt thì đổi PROMPT_VERSION.
File lưu gồm đầu vào, đầu ra JSON, mô hình thực chạy, request id và số token, để tính chi phí và tái lập.
"""
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "data" / "llm_cache" / "a4"
MODEL = "claude-sonnet-5-5"
PROMPT_VERSION = "a4c-1"
MAX_TOKENS = 16000
EFFORT = "medium"
FALLBACK_BETA = "server-side-fallback-2026-07-01"  # từ chối do bộ phân loại an toàn thì chạy lại trên mô hình dự phòng mặc định

_NULLABLE_STR = {"anyOf": [{"type": "string"}, {"type": "null"}]}
_TARGET = {"type": "object", "additionalProperties": False, "required": ["dieu", "khoan", "diem"],
           "properties": {"dieu": {"type": "string"}, "khoan": _NULLABLE_STR, "diem": _NULLABLE_STR}}
SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["chi_thi", "khong_xu_ly_duoc"],
    "properties": {
        "chi_thi": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["op", "quan_he", "dich", "vao_sau", "noi_dung", "kieu_cum", "cum_cu", "cum_moi"],
            "properties": {
                "op": {"type": "string", "enum": ["replace_unit", "insert_unit", "repeal_unit", "rename_heading", "phrase"]},
                "quan_he": {"type": "string", "enum": ["amends", "replaces"]},
                "dich": {"type": "array", "items": _TARGET},
                "vao_sau": {"anyOf": [_TARGET, {"type": "null"}]},
                "noi_dung": _NULLABLE_STR,
                "kieu_cum": {"anyOf": [{"type": "string", "enum": ["replace", "delete", "insert"]}, {"type": "null"}]},
                "cum_cu": _NULLABLE_STR,
                "cum_moi": _NULLABLE_STR,
            }}},
        "khong_xu_ly_duoc": _NULLABLE_STR,
    },
}

SYSTEM_PROMPT = """Bạn chuyển một khối chỉ thị trong văn bản sửa đổi của luật Việt Nam thành danh sách chỉ thị chuẩn dạng JSON. Văn bản bị \
sửa là một Bộ luật; mọi Điều, khoản, điểm trong khối là của Bộ luật đó. Kết quả của bạn sẽ được máy dựng lại thành câu chuẩn, parse \
lại và đối chiếu với khối gốc; chỗ nào không khớp sẽ bị trả về cho bạn sửa, nên hãy chép chính xác thay vì diễn đạt lại.

Các loại chỉ thị (op):
- replace_unit: sửa đổi, bổ sung hoặc thay thế toàn bộ một Điều / khoản / điểm bằng nội dung trong nháy. quan_he = "replaces" nếu khối \
dùng chữ "thay thế", ngược lại "amends".
- insert_unit: bổ sung một Điều / khoản / điểm mới; vao_sau là đơn vị cùng cấp mà nó đứng sau (nếu khối nói "vào sau"), ngược lại null.
- repeal_unit: bãi bỏ một hoặc nhiều đơn vị.
- rename_heading: sửa tên của một Điều; noi_dung là chữ trong nháy.
- phrase: thay thế / sửa đổi (kieu_cum = "replace"), bỏ ("delete") hoặc bổ sung vào sau một cụm từ khác ("insert") một cụm từ tại \
các đơn vị trong dich. cum_cu là cụm bị thay / bị bỏ / cụm neo, cum_moi là cụm mới (null khi bỏ). quan_he = "replaces" nếu khối dùng \
"thay thế cụm từ", ngược lại "amends".

Quy tắc:
1. replace_unit, insert_unit, rename_heading: mỗi chỉ thị đúng một đích. Một câu như "Sửa đổi, bổ sung khoản 3 và khoản 4 Điều 53 \
như sau:" là hai chỉ thị replace_unit.
2. Đích luôn ghi đủ Điều. Khoản, điểm viết tương đối ("a) Sửa đổi, bổ sung khoản 6 như sau:", "tại khoản 2;") thuộc Điều nêu ở dòng \
đầu khối ("... một số khoản của Điều 194 như sau:", "... tên Điều và khoản 1 Điều 49 như sau:"). Dòng đầu khối kiểu đó chỉ là phạm vi, \
không phải chỉ thị riêng.
3. Số và chữ giữ đúng như khối: khoản "4a" là "4a", điểm "đ" là "đ". Trường không dùng thì để null.
4. noi_dung chép NGUYÊN VĂN chữ nằm giữa cặp nháy ngoài cùng (không gồm dấu nháy, giữ nguyên xuống dòng). Nếu một cặp nháy chứa nội \
dung của nhiều đích (ví dụ “3. ... 4. ...” cho khoản 3 và khoản 4), tách đúng tại nhãn mở đầu của từng khoản / điểm; không thêm, bớt \
hay sửa chữ nào. cum_cu, cum_moi chép nguyên văn chữ trong nháy của câu.
5. Không đoán. Nếu khối có nội dung không biểu diễn được bằng các loại trên (đánh số lại, chuyển vị trí, ngày hiệu lực riêng cho một \
phần, quy định chuyển tiếp, ...) thì chi_thi = [] và ghi lý do vào khong_xu_ly_duoc. Ngược lại khong_xu_ly_duoc = null.
6. Nếu có phần "LẦN TRƯỚC BỊ TỪ CHỐI", đó là đề xuất trước của bạn và lỗi máy tìm thấy; sửa đúng các lỗi đó.

Ví dụ khối:
5. Sửa đổi, bổ sung, bãi bỏ một số khoản của Điều 40 như sau:
a) Sửa đổi, bổ sung khoản 2 như sau:
“2. Nội dung A.
a) Ý một;
b) Ý hai.”;
b) Bãi bỏ khoản 3.
Kết quả: chi_thi = [{op: replace_unit, quan_he: amends, dich: [{dieu: "40", khoan: "2", diem: null}], noi_dung: "2. Nội dung A.\\na) Ý \
một;\\nb) Ý hai.", các trường còn lại null}, {op: repeal_unit, quan_he: amends, dich: [{dieu: "40", khoan: "3", diem: null}], các trường \
còn lại null}]."""


class ProposerError(Exception):
    """Lỗi của tầng đề xuất; a4_versions.normalize_block đổi thành A4Error cùng code."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def cache_key(model, block_text, feedback):
    payload = json.dumps({"model": model, "prompt": PROMPT_VERSION, "block": block_text, "feedback": feedback},
                         ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]


def user_message(block_text, feedback):
    text = f"KHỐI CHỈ THỊ:\n<khoi>\n{block_text}\n</khoi>"
    if feedback:
        text += f"\n\nLẦN TRƯỚC BỊ TỪ CHỐI (đề xuất trước và lỗi):\n{feedback}"
    return text


class ClaudeProposer:
    """propose(chữ khối, phản hồi) -> (dict JSON theo SCHEMA, meta). client chỉ để test gắn client giả."""

    def __init__(self, mode, cache_dir=None, model=MODEL, client=None):
        if mode not in ("replay", "live"):
            raise ValueError(f"mode phải là replay hoặc live, có {mode!r}")
        self.mode, self.model, self.client = mode, model, client
        self.cache_dir = Path(cache_dir) if cache_dir is not None else CACHE_DIR  # đọc lúc tạo để test đổi được CACHE_DIR
        self.calls = 0  # số lần gọi API thật trong lần chạy này

    def propose(self, block_text, feedback=None):
        key = cache_key(self.model, block_text, feedback)
        path = self.cache_dir / f"{key}.json"
        if path.exists():
            saved = json.loads(path.read_text(encoding="utf-8"))
            return saved["output"], {"model": saved["model"], "key": key, "cached": True}
        if self.mode != "live":
            raise ProposerError("E_LLM_CACHE", f"chưa có kết quả đã lưu cho khối (khoá {key}); chạy lại với --llm live")
        record = self._call(block_text, feedback)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"key": key, **record}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        return record["output"], {"model": record["model"], "key": key, "cached": False}

    def _call(self, block_text, feedback):
        try:
            import anthropic  # chỉ cần ở chế độ live
        except ImportError:
            if self.client is None:
                raise ProposerError("E_LLM_API", "chưa cài gói anthropic; chạy bằng .venv/bin/python")
            anthropic = None  # client giả của test
        client = self.client or anthropic.Anthropic()
        status_error = anthropic.APIStatusError if anthropic else ()
        connection_error = anthropic.APIConnectionError if anthropic else ()
        try:
            response = client.beta.messages.create(
                model=self.model,
                max_tokens=MAX_TOKENS,
                betas=[FALLBACK_BETA],
                fallbacks="default",
                system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
                messages=[{"role": "user", "content": user_message(block_text, feedback)}],
                output_config={"effort": EFFORT, "format": {"type": "json_schema", "schema": SCHEMA}},
            )
        except status_error as e:
            raise ProposerError("E_LLM_API", f"API trả lỗi {e.status_code}: {e.message}")
        except connection_error as e:
            raise ProposerError("E_LLM_API", f"không kết nối được API: {e}")
        self.calls += 1
        if response.stop_reason == "refusal":
            details = getattr(response, "stop_details", None)
            raise ProposerError("E_LLM", f"mô hình từ chối (category {getattr(details, 'category', None)})")
        if response.stop_reason == "max_tokens":
            raise ProposerError("E_LLM", f"đầu ra bị cắt ở max_tokens={MAX_TOKENS}")
        text = "".join(b.text for b in response.content if b.type == "text")
        try:
            output = json.loads(text)
        except json.JSONDecodeError as e:
            raise ProposerError("E_LLM_SHAPE", f"đầu ra không phải JSON: {e}")
        usage = response.usage
        return {"model": response.model, "requested_model": self.model, "prompt_version": PROMPT_VERSION,
                "created": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                "request_id": getattr(response, "_request_id", None), "block": block_text, "feedback": feedback,
                "output": output,
                "usage": {k: getattr(usage, k, None) for k in ("input_tokens", "output_tokens",
                                                               "cache_creation_input_tokens", "cache_read_input_tokens")}}
