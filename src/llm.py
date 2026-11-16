"""LLM client (chỉ stdlib) cho các bước dùng LLM: S_upd (a4_versions) và S_know (a8_knowledge_layer).

Gọi API chat-completions kiểu OpenAI qua urllib.request, nên không cần thư viện bên ngoài.
Cấu hình bằng biến môi trường (không cấu hình = tắt LLM):
  LLM_API_KEY   (bắt buộc để bật)
  LLM_MODEL     (bắt buộc để bật, vd gpt-4o-mini)
  LLM_BASE_URL  (mặc định https://api.openai.com/v1)
  LLM_TIMEOUT   (giây, mặc định 60)

Khi tắt, enabled() trả False và complete() trả None: các bước dùng LLM giữ đúng hành vi
tất định hiện tại (không đoán, báo lỗi như trước). Đây là điểm mở rộng wrap quanh nền tất định A1-A7.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv(path=None):
    """Nạp .env gốc dự án (stdlib only, không cần python-dotenv).

    Biến môi trường thật được ưu tiên hơn giá trị trong file: chỉ ghi nếu key chưa có sẵn.
    """
    path = path or ROOT / ".env"
    try:
        with open(path, encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key, value = key.strip(), value.strip().strip("\"'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except OSError:
        pass


_load_dotenv()


def _env(name):
    return os.environ.get(name, "").strip()


def enabled():
    """LLM có sẵn sàng không (đã cấu hình khoá + model)."""
    return bool(_env("LLM_API_KEY") and _env("LLM_MODEL"))


def complete(prompt, system=None, temperature=None, max_tokens=None):
    """Gọi chat completions; trả về nội dung text hoặc None khi chưa cấu hình / lỗi."""
    if not enabled():
        return None
    base = _env("LLM_BASE_URL") or "https://api.openai.com/v1"
    url = base.rstrip("/") + "/chat/completions"
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    payload = {"model": _env("LLM_MODEL"), "messages": messages}
    if temperature is not None:
        payload["temperature"] = temperature
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + _env("LLM_API_KEY")},
    )
    try:
        with urllib.request.urlopen(request, timeout=int(_env("LLM_TIMEOUT") or 60)) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError) as e:
        print(f"[llm] gọi LLM lỗi, bỏ qua: {e}", file=sys.stderr)
        return None
    try:
        return body["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError):
        return None