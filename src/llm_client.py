"""Wrapper gọi LLM duy nhất của dự án (Gemini), dùng chung cho L3, L4, L6 và các bước sau.

Việc của module này:
  - đọc model, hạn mức, max_output_tokens từ khối "khoá = giá trị" trong docs/llm_config.md (không chép cứng vào code);
  - lưu MỌI phản hồi thô vào data/llm_cache/<tác vụ>/<khoá>.json; cùng đầu vào đọc lại đúng phản hồi cũ, nên tính tái lập
    đến từ cache chứ không từ temperature (llm_config.md);
  - đếm lượt theo ngày và theo vai (chính / kiểm) trong data/llm_cache/_usage.json; chạm hạn mức thì dừng gọn (QuotaReached),
    các lượt đã lưu không bị gọi lại nên hôm sau chạy tiếp từ chỗ dừng.

Chế độ (cờ --llm của các bước): off = không gọi gì, mọi lời gọi báo LLMUnavailable; replay = chỉ đọc cache, thiếu thì báo
CacheMiss (không chạm mạng); live = như replay, thiếu thì gọi API rồi lưu. Khoá API chỉ lấy từ biến môi trường GEMINI_API_KEY.
Đề xuất của LLM không bao giờ được áp thẳng: bước gọi phải kiểm bằng máy (CLAUDE.md mục 4).
"""
import datetime
import hashlib
import json
import os
import re
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "docs" / "llm_config.md"
CACHE_DIR = ROOT / "data" / "llm_cache"
USAGE_PATH = CACHE_DIR / "_usage.json"
ROLES = ("chinh", "kiem")  # model chính và model kiểm độc lập (llm_config.md)
RETRY_CODES = (429, 500, 503)
ATTEMPTS = 3
WAIT_SECONDS = 20


HEARTBEAT_SECONDS = 30  # lượt gọi API chờ quá ngần này giây thì in một dòng "vẫn đang chờ" để biết tiến trình chưa treo


def stderr_log(msg):
    """Ghi tiến độ ra stderr (không lẫn vào stdout là phần báo cáo của bước); flush để thấy ngay."""
    try:  # Windows: stderr mặc định có thể không phải UTF-8 (khi chạy trực tiếp, không qua run_all -X utf8), tiếng Việt sẽ thành \uXXXX
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    print(msg, file=sys.stderr, flush=True)


class _Heartbeat:
    """Trong lúc một lời gọi API đang chặn, cứ HEARTBEAT_SECONDS in một dòng kèm số giây đã chờ. Chạy trong luồng nền, dừng ngay khi lời gọi xong.
    Dùng đồng hồ thật (time.monotonic), không dùng clock của Client, nên test giả đồng hồ không bị ảnh hưởng."""

    def __init__(self, log, label, every=None):
        self.log, self.label, self.every = log, label, every or HEARTBEAT_SECONDS
        self._stop = threading.Event()

    def __enter__(self):
        if self.log is not None:
            began = time.monotonic()

            def beat():
                while not self._stop.wait(self.every):
                    self.log(f"      ... {self.label} vẫn đang chờ phản hồi ({time.monotonic() - began:.0f}s)")
            threading.Thread(target=beat, daemon=True).start()
        return self

    def __exit__(self, *exc):
        self._stop.set()


class LLMError(Exception):
    pass


class InvalidOutput(ValueError):
    """Phản hồi của model không qua kiểm hợp lệ của bước gọi. Đã chuyển sang <cache>/<tác vụ>/_rejected/ (kèm lý do) và ĐÃ tính lượt (vì API đã tốn);
    không nằm trong cache chính nên chạy lại sẽ gọi lại. Là ValueError để bước gọi bắt chung với lỗi kiểm của chính nó."""


class LLMUnavailable(LLMError):
    """Chế độ off, hoặc thiếu gói / khoá API."""


class CacheMiss(LLMError):
    """Chế độ replay mà chưa có phản hồi đã lưu cho đầu vào này."""


class QuotaReached(LLMError):
    """Hết hạn mức lượt trong ngày của một vai; các lượt đã lưu vẫn dùng được, chạy tiếp hôm sau."""


def load_config(path=CONFIG_PATH):
    """Đọc các dòng 'khoá = giá trị' trong llm_config.md thành dict phẳng; số nguyên đổi sang int."""
    cfg = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([\w.]+)\s*=\s*(.+?)\s*$", line)
        if m:
            v = m[2]
            cfg[m[1]] = int(v) if v.isdigit() else v
    for need in ("chinh.model", "chinh.luot_moi_ngay", "kiem.model", "kiem.luot_moi_ngay", "max_output_tokens"):
        if need not in cfg:
            raise LLMError(f"{path}: thiếu khoá {need}")
    return cfg


def cache_key(model, task, prompt_version, payload, system="", schema=None):
    """Khoá cache = sha256 của (model, tác vụ, phiên bản prompt, đầu vào, chữ system, lược đồ): sửa prompt hay lược đồ mà quên đổi
    phiên bản vẫn không dùng nhầm phản hồi cũ."""
    raw = json.dumps([model, task, prompt_version, payload, system, schema], ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


class Client:
    """Một lời gọi = ask(task, prompt_version, system, user, schema, role, payload)."""

    def __init__(self, mode="off", config=None, cache_dir=CACHE_DIR, usage_path=USAGE_PATH, today=None, sleep=time.sleep, api=None,
                 clock=time.monotonic, log=None):
        if mode not in ("off", "replay", "live"):
            raise LLMError(f"chế độ lạ: {mode!r}")
        self.log = log  # hàm nhận 1 chuỗi (vd stderr_log); None = im lặng (mặc định, để test không in gì). Chỉ lượt gọi API thật mới ghi log, lượt đọc cache thì không
        self.mode, self.cfg = mode, config or load_config()
        self.cache_dir, self.usage_path = Path(cache_dir), Path(usage_path)
        self.today = today or datetime.date.today().isoformat()
        self.sleep, self._api, self.calls, self.hits = sleep, api, 0, 0  # calls: lượt gọi API; hits: lượt đọc lại từ cache
        self.clock, self._last = clock, {}  # thời điểm gọi API gần nhất của từng vai, để giãn nhịp theo RPM

    # ---- đếm lượt ----
    def _usage(self):
        if self.usage_path.exists():
            return json.loads(self.usage_path.read_text(encoding="utf-8"))
        return {}

    def used_today(self, role):
        return self._usage().get(self.today, {}).get(role, 0)

    def _count(self, role):
        usage = self._usage()
        day = usage.setdefault(self.today, {})
        day[role] = day.get(role, 0) + 1
        self.usage_path.parent.mkdir(parents=True, exist_ok=True)
        self.usage_path.write_text(json.dumps(usage, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")

    # ---- gọi ----
    @staticmethod
    def _invalid(validate, output):
        """None nếu hợp lệ (hoặc không có validate); ngược lại lý do (validate ném ValueError)."""
        if validate is None:
            return None
        try:
            validate(output)
        except ValueError as e:
            return str(e) or "không hợp lệ"
        return None

    @staticmethod
    def _quarantine(path, record, reason, move=True):
        """Ghi phản hồi không hợp lệ vào _rejected/ cạnh cache chính (kèm lý do); move=True thì gỡ nó khỏi cache chính."""
        dest = path.parent / "_rejected" / path.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps({**record, "rejected_reason": reason}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        if move:
            path.unlink()

    def ask(self, task, prompt_version, system, user, schema, role="chinh", payload=None, validate=None, label=None):
        """Trả dict đã lưu {model, output, usage, ...}. payload (mặc định = user) dùng để tính khoá cache. label chỉ để ghi log tiến độ (vd "lô 3/13"), không vào khoá cache.
        validate(output) ném ValueError nếu đầu ra không hợp lệ: phản hồi MỚI không hợp lệ không vào cache chính (xem InvalidOutput); phản hồi đã lưu mà
        nay không qua kiểm (kiểm chặt hơn sau này) bị chuyển sang _rejected/ và coi như chưa có."""
        if self.mode == "off":
            raise LLMUnavailable("chế độ --llm off")
        model = self.cfg[f"{role}.model"]
        key = cache_key(model, task, prompt_version, payload if payload is not None else user, system, schema)
        path = self.cache_dir / task / f"{key}.json"
        if path.exists():
            record = json.loads(path.read_text(encoding="utf-8"))
            reason = self._invalid(validate, record.get("output"))
            if reason is None:
                self.hits += 1
                return record
            self._quarantine(path, record, reason)
        if self.mode == "replay":
            raise CacheMiss(f"chưa có phản hồi đã lưu cho {task}/{key} (chạy --llm live để gọi)")
        limit = self.cfg[f"{role}.luot_moi_ngay"]
        if self.used_today(role) >= limit:
            raise QuotaReached(f"vai {role} đã dùng {self.used_today(role)}/{limit} lượt hôm nay ({self.today})")
        self._throttle(role)
        tag = f"[LLM {task} · {role}{' · ' + label if label else ''}]"
        if self.log:
            self.log(f"{tag} gọi {model} (lượt {role} hôm nay: {self.used_today(role) + 1}/{limit}) ...")
        began = time.monotonic()
        with _Heartbeat(self.log, tag):
            result = self._call(model, system, user, schema)
        if self.log:
            u = result.get("usage") or {}
            self.log(f"{tag} xong sau {time.monotonic() - began:.0f}s (token vào {u.get('prompt_token_count')}, ra {u.get('candidates_token_count')})")
        self._count(role)
        record = {"task": task, "prompt_version": prompt_version, "role": role, "requested_model": model,
                  "created": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                  "system": system, "user": user, **result}
        reason = self._invalid(validate, result["output"])
        if reason is not None:
            self._quarantine(path, record, reason, move=False)
            raise InvalidOutput(reason)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        return record

    def _throttle(self, role):
        """Chờ cho đủ 60/rpm giây kể từ lần gọi API trước của cùng vai (llm_config.md: chinh 15 RPM, kiem 5 RPM). Lượt đọc từ cache không chờ."""
        rpm = self.cfg.get(f"{role}.rpm")
        if rpm:
            wait = 60.0 / rpm - (self.clock() - self._last[role]) if role in self._last else 0
            if wait > 0:
                self.sleep(wait)
        self._last[role] = self.clock()

    def _client(self):
        if self._api is not None:
            return self._api
        try:
            from google import genai  # chỉ cần ở chế độ live; cài trong .venv
        except ImportError:
            raise LLMUnavailable("chưa cài gói google-genai; chạy: .venv/Scripts/python.exe -m pip install google-genai")
        try:
            self._api = genai.Client()
        except ValueError as e:
            raise LLMUnavailable(f"chưa có khoá Gemini; đặt biến môi trường GEMINI_API_KEY bằng `setx` (xem đầu src/run_all.py) ({e})")
        return self._api

    def _call(self, model, system, user, schema):
        try:
            from google.genai import errors
            api_error = errors.APIError
        except ImportError:
            api_error = Exception
        config = {"system_instruction": system, "response_mime_type": "application/json", "response_json_schema": schema,
                  "max_output_tokens": self.cfg["max_output_tokens"]}  # temperature, thinking: để mặc định (llm_config.md)
        client = self._client()
        for attempt in range(1, ATTEMPTS + 1):
            try:
                response = client.models.generate_content(model=model, contents=user, config=config)
                break
            except api_error as e:
                code = getattr(e, "code", None)
                if code in RETRY_CODES and attempt < ATTEMPTS:
                    if self.log:  # dòng này cho biết lượt chậm là do server báo bận (429/500/503) hay do server xử lý chậm
                        self.log(f"      ! API trả lỗi {code} (lần {attempt}/{ATTEMPTS}), chờ {WAIT_SECONDS * attempt}s rồi thử lại")
                    self.sleep(WAIT_SECONDS * attempt)
                    continue
                raise LLMError(f"API trả lỗi {code}: {getattr(e, 'message', e)}")
        self.calls += 1
        cands = getattr(response, "candidates", None) or []
        if not cands:
            raise LLMError("mô hình không trả ứng viên nào")
        finish = getattr(cands[0].finish_reason, "name", str(cands[0].finish_reason))
        if finish != "STOP":
            raise LLMError(f"mô hình dừng với finish_reason {finish}")
        usage = getattr(response, "usage_metadata", None)
        try:
            output = json.loads(response.text)
        except (ValueError, TypeError) as e:
            raise LLMError(f"đầu ra của mô hình không phải JSON ({e})")
        return {"model": getattr(response, "model_version", None) or model, "request_id": getattr(response, "response_id", None),
                "output": output,
                "usage": {k: getattr(usage, k, None) for k in ("prompt_token_count", "candidates_token_count", "thoughts_token_count",
                                                               "total_token_count")}}


def key_is_set():
    """Biến môi trường GEMINI_API_KEY có giá trị không (chỉ trả có/không, không bao giờ in khoá)."""
    return bool(os.environ.get("GEMINI_API_KEY"))


def check_models(cfg):
    """Hỏi models.list (KHÔNG tốn lượt tạo nội dung): mỗi model trong llm_config.md có tồn tại không. -> {model: bool}."""
    api = Client("live", cfg)._client()
    try:
        names = {m.name.removeprefix("models/") for m in api.models.list()}
    except Exception as e:  # SDK ném nhiều loại lỗi mạng / quyền
        raise LLMError(f"models.list lỗi: {type(e).__name__}: {e}")
    return {cfg[f"{r}.model"]: cfg[f"{r}.model"] in names for r in ROLES}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    cfg = load_config()
    c = Client("off", cfg)
    print("cấu hình:", {k: v for k, v in cfg.items() if k != "temperature"})
    print("lượt đã dùng hôm nay:", {r: c.used_today(r) for r in ROLES}, "| khoá GEMINI_API_KEY:", "có" if key_is_set() else "KHÔNG THẤY")
    if "--check-models" in sys.argv:
        if not key_is_set():
            raise SystemExit("không thấy GEMINI_API_KEY trong môi trường của process này (đặt khoá MỘT LẦN bằng `setx GEMINI_API_KEY` ở terminal riêng rồi mở terminal mới; xem đầu src/run_all.py)")
        for model, ok in check_models(cfg).items():
            print(f"  {'có' if ok else 'KHÔNG CÓ'} trên models.list: {model}")
