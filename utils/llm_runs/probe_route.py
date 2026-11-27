"""Gọi thử tuyến ckey của api.model bằng lời nhắn ngắn (khoảng 6,5 VND). Mã 0 = tuyến sống. Dùng: python -I utils/llm_runs/probe_route.py <gốc repo>"""
import json, os, sys, urllib.request
sys.path.insert(0, sys.argv[1] + "/src")
import llm_client
cfg = llm_client.load_config(); model = cfg["api.model"]
body = json.dumps({"model": model, "max_tokens": 64, "messages": [{"role": "user", "content": "ok"}]}).encode()
req = urllib.request.Request(cfg["api.base_url"].rstrip("/") + "/v1/messages", data=body, method="POST", headers={
    "Authorization": f"Bearer {os.environ['CKEY_API_KEY']}", "Content-Type": "application/json",
    "anthropic-version": "2023-06-01", "User-Agent": llm_client.USER_AGENT})
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        ok = json.loads(r.read()).get("stop_reason") is not None
    print(f"tuyến {model} sống" if ok else f"tuyến {model} trả lạ"); sys.exit(0 if ok else 1)
except Exception as e:
    print(f"tuyến {model} chưa sống: {str(e)[:120]}"); sys.exit(1)
