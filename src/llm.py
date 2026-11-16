"""Minimal OpenAI-compatible chat client (urllib only) — zero deps so `-I` stays clean.

Reads LLM_* from the project `.env`. No key+model => enabled() is False and complete()
returns None — that's the contract: LLM-backed steps then fall back to their deterministic
path instead of guessing.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv(path=None):
    """Pull `<repo>/.env` into os.environ; real env vars already set win."""
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
    """True when a key + model are configured."""
    return bool(_env("LLM_API_KEY") and _env("LLM_MODEL"))


def complete(prompt, system=None, temperature=None, max_tokens=None):
    """Call chat completions; return the text content, or None when unconfigured / on error."""
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
        print(f"[llm] LLM call failed, skipping: {e}", file=sys.stderr)
        return None
    try:
        return body["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError):
        return None