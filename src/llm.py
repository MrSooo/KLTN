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


def _strip_fences(text):
    """Drop a single surrounding ```...``` fenced block Qwen may wrap around JSON answers."""
    lines = text.splitlines()
    if lines and lines[0].lstrip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _extract_content(body):
    """Return choices[0].message.content (string), or None when absent / non-string.

    Qwen3.8 reasoning models emit `reasoning_content` (chain-of-thought) alongside
    `content` (the answer). We read only `content`; the extra `reasoning_content` key
    never reaches callers. Missing / non-string content => None, so callers treat it
    as "LLM returned nothing" instead of crashing.
    """
    try:
        msg = body["choices"][0]["message"]
    except (KeyError, IndexError, TypeError):
        return None
    content = msg.get("content")
    if not isinstance(content, str):
        return None
    content = content.strip()
    return _strip_fences(content) if content else ""


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
    # Alibaba reasoning models: LLM_ENABLE_THINKING=false skips the thinking pass
    # (no reasoning_content) and returns much faster — right for high-volume extraction.
    thinking = _env("LLM_ENABLE_THINKING").strip().lower()
    if thinking in ("0", "false", "off", "no"):
        payload["enable_thinking"] = False
    elif thinking in ("1", "true", "on", "yes"):
        payload["enable_thinking"] = True
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
    return _extract_content(body)