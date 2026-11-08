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
import re
import sys
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


class LLMError(Exception):
    pass


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


def cache_key(model, task, prompt_version, payload):
    """Khoá cache = sha256 của (model, tác vụ, phiên bản prompt, đầu vào); đổi model hay prompt thì đổi khoá."""
    raw = json.dumps([model, task, prompt_version, payload], ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


class Client:
    """Một lời gọi = ask(task, prompt_version, system, user, schema, role, payload)."""

    def __init__(self, mode="off", config=None, cache_dir=CACHE_DIR, usage_path=USAGE_PATH, today=None, sleep=time.sleep, api=None):
        if mode not in ("off", "replay", "live"):
            raise LLMError(f"chế độ lạ: {mode!r}")
        self.mode, self.cfg = mode, config or load_config()
        self.cache_dir, self.usage_path = Path(cache_dir), Path(usage_path)
        self.today = today or datetime.date.today().isoformat()
        self.sleep, self._api, self.calls = sleep, api, 0

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
    def ask(self, task, prompt_version, system, user, schema, role="chinh", payload=None):
        """Trả dict đã lưu {model, output, usage, ...}. payload (mặc định = user) dùng để tính khoá cache."""
        if self.mode == "off":
            raise LLMUnavailable("chế độ --llm off")
        model = self.cfg[f"{role}.model"]
        key = cache_key(model, task, prompt_version, payload if payload is not None else user)
        path = self.cache_dir / task / f"{key}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        if self.mode == "replay":
            raise CacheMiss(f"chưa có phản hồi đã lưu cho {task}/{key} (chạy --llm live để gọi)")
        limit = self.cfg[f"{role}.luot_moi_ngay"]
        if self.used_today(role) >= limit:
            raise QuotaReached(f"vai {role} đã dùng {self.used_today(role)}/{limit} lượt hôm nay ({self.today})")
        result = self._call(model, system, user, schema)
        self._count(role)
        record = {"task": task, "prompt_version": prompt_version, "role": role, "requested_model": model,
                  "created": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
                  "system": system, "user": user, **result}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        return record

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
            raise LLMUnavailable(f"chưa có khoá Gemini; đặt biến môi trường GEMINI_API_KEY ({e})")
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
        return {"model": getattr(response, "model_version", None) or model, "request_id": getattr(response, "response_id", None),
                "output": json.loads(response.text),
                "usage": {k: getattr(usage, k, None) for k in ("prompt_token_count", "candidates_token_count", "thoughts_token_count",
                                                               "total_token_count")}}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    cfg = load_config()
    c = Client("off", cfg)
    print("cấu hình:", {k: v for k, v in cfg.items() if k != "temperature"})
    print("lượt đã dùng hôm nay:", {r: c.used_today(r) for r in ROLES})
