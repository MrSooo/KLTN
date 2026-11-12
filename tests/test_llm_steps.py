"""Test nhánh LLM của L3, giãn nhịp RPM của llm_client, và đường thiếu khoá của run_all. Toàn bộ dùng API giả: không chạm mạng, không tốn lượt.

Nguyên tắc cần giữ (CLAUDE.md mục 4): đề xuất của LLM không được áp thẳng; đầu ra sai bị loại và không vào cache chính.
(Bước loại Điều không còn dùng LLM từ 11/11, quyết định A14, nên không còn test nhánh LLM của nó.)
"""
import contextlib
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import types
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import _harness  # noqa: E402
import links as l3  # noqa: E402
import llm_client as llm  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CFG = {"chinh.model": "m-chinh", "chinh.luot_moi_ngay": 100, "kiem.model": "m-kiem", "kiem.luot_moi_ngay": 100, "max_output_tokens": 100}


def fake_client(tmp, behaviour, cfg=None, mode="live"):
    """Client live với _call giả. behaviour(model, user_json) -> output dict. Trả (client, danh sách [(model, user)])."""
    c = llm.Client(mode, cfg or CFG, cache_dir=Path(tmp) / "cache", usage_path=Path(tmp) / "cache" / "_usage.json", today="2026-11-09", sleep=lambda s: None)
    seen = []

    def call(model, system, user, schema):
        seen.append((model, user))
        c.calls += 1
        return {"model": model, "request_id": "r", "output": behaviour(model, user), "usage": {}}
    c._call = call
    return c, seen


# ---- L3 ----

LAW = {"BLLD_45-2019.D91": {"type": "dieu", "heading": "Mức lương tối thiểu", "text": ""},
       "BLLD_45-2019.D91.K4": {"type": "khoan", "heading": None, "text": "Chính phủ quy định chi tiết Điều này."},
       "BLLD_45-2019.D5": {"type": "dieu", "heading": "Quy định khác", "text": ""},
       "BLLD_45-2019.D5.K1": {"type": "khoan", "heading": None, "text": "Chính phủ quy định chi tiết khoản này."}}
CLAUSES = [{"unit_id": "BLLD_45-2019.D91.K4", "phrase": "Chính phủ quy định"}, {"unit_id": "BLLD_45-2019.D5.K1", "phrase": "Chính phủ quy định"}]
DEC = SimpleNamespace(doc_id="ND_X")
DEC_UNITS = {"ND_X.D1": {"type": "dieu", "heading": "Phạm vi điều chỉnh",
                         "text": "Nghị định này quy định mức lương tối thiểu tháng và mức lương tối thiểu giờ áp dụng đối với người lao động"}}
D91K4, D5K1 = "BLLD_45-2019.D91.K4", "BLLD_45-2019.D5.K1"


def test_l3_validate_targets():
    allowed = {D91K4, D5K1}
    assert l3.validate_targets({"targets": [{"unit_id": D91K4, "ly_do": "x"}, {"unit_id": D91K4, "ly_do": "lặp"}]}, allowed) == [D91K4]
    assert l3.validate_targets({"targets": []}, allowed) == []
    for bad in ({"targets": [{"unit_id": "BLLD_45-2019.D999", "ly_do": "x"}]}, {"targets": "x"}, {"targets": [{"ly_do": "x"}]}, [],
                {"targets": [{"unit_id": D91K4, "ly_do": "x"}] * 6}):
        try:
            l3.validate_targets(bad, allowed)
        except ValueError:
            continue
        raise AssertionError(bad)


def test_l3_two_passes_are_independent_same_input_different_models():
    with tempfile.TemporaryDirectory() as t:
        c, seen = fake_client(t, lambda model, user: {"targets": [{"unit_id": D91K4, "ly_do": "x"}]})
        res = l3.llm_propose(c, DEC, DEC_UNITS, CLAUSES, LAW)
        assert [m for m, _ in seen] == ["m-chinh", "m-kiem"] and seen[0][1] == seen[1][1], "lượt sau KHÔNG thấy kết quả lượt trước: cùng đầu vào"
        assert res["chinh"] == res["kiem"] == [D91K4] and res["note"] == ""
        assert "mức lương tối thiểu tháng" in seen[0][1] and D91K4 in seen[0][1]


def test_l3_llm_pass_failures_become_none_with_note():
    with tempfile.TemporaryDirectory() as t:
        c, _ = fake_client(t, lambda model, user: {"targets": [{"unit_id": "ngoài danh sách", "ly_do": "x"}]})
        res = l3.llm_propose(c, DEC, DEC_UNITS, CLAUSES, LAW)
        assert res["chinh"] is None and res["kiem"] is None and "đầu ra bị loại" in res["note"]
    with tempfile.TemporaryDirectory() as t:
        res = l3.llm_propose(llm.Client("replay", CFG, cache_dir=Path(t) / "c", usage_path=Path(t) / "c" / "u.json"), DEC, DEC_UNITS, CLAUSES, LAW)
        assert res["chinh"] is None and res["kiem"] is None and "chưa có cache" in res["note"]


def edges(llm_result, kw=()):
    return {e["o"]: e for e in l3.decide_llm(DEC, DEC_UNITS, LAW, list(kw), llm_result)}


def test_l3_keeps_edge_only_when_both_models_and_keyword_agree():
    e = edges({"chinh": [D91K4], "kiem": [D91K4], "note": ""})["BLLD_45-2019.D91"]
    assert e["flags"] == ["llm_proposed"] and e["how"] == "llm"
    assert set(e) == {"s", "p", "o", "evidence", "how", "flags"}, "khuôn cạnh chung A12, không còn via/check"


def test_l3_isolates_when_second_model_disagrees_keyword_fails_or_only_keyword_proposed():
    assert edges({"chinh": [D91K4], "kiem": [], "note": ""})["BLLD_45-2019.D91"]["flags"] == ["llm_proposed", "isolated"]
    assert edges({"chinh": [D91K4], "kiem": None, "note": "x"})["BLLD_45-2019.D91"]["flags"] == ["llm_proposed", "isolated"], "lượt kiểm chưa có: không nâng cấp"
    e = edges({"chinh": [D5K1], "kiem": [D5K1], "note": ""})["BLLD_45-2019.D5"]
    assert e["flags"] == ["llm_proposed", "isolated"], "hai model đồng ý nhưng từ khoá không có trong Điều đích"
    kw = {"s": "ND_X", "p": "details", "o": "BLLD_45-2019.D91", "how": "keyword", "flags": ["keyword_proposed", "llm_check_pending"]}
    e = edges({"chinh": [], "kiem": [D91K4], "note": ""}, [kw])["BLLD_45-2019.D91"]
    assert e["how"] == "keyword" and e["flags"] == ["keyword_proposed", "isolated"], "đề xuất chỉ do từ khoá không bao giờ được giữ"


# ---- llm_client: giãn nhịp, JSON lỗi ----

def test_client_throttles_by_rpm_but_not_cache_hits():
    now = [0.0]
    slept = []

    def sleep(s):
        slept.append(round(s, 3))
        now[0] += s
    with tempfile.TemporaryDirectory() as t:
        c = llm.Client("live", {**CFG, "chinh.rpm": 15}, cache_dir=Path(t) / "c", usage_path=Path(t) / "c" / "u.json", today="2026-11-09", sleep=sleep, clock=lambda: now[0])
        c._call = lambda model, system, user, schema: {"model": model, "request_id": "r", "output": {"u": user}, "usage": {}}
        c.ask("t", "v1", "s", "một", {})
        c.ask("t", "v1", "s", "hai", {})
        c.ask("t", "v1", "s", "một", {})  # cache: không chờ, không đổi nhịp
        c.ask("t", "v1", "s", "ba", {})
        assert slept == [4.0, 4.0] and c.hits == 1, slept


def test_client_non_json_output_is_an_llm_error_and_costs_no_quota():
    resp = SimpleNamespace(candidates=[SimpleNamespace(finish_reason=SimpleNamespace(name="STOP"))], text="đây không phải JSON", usage_metadata=None,
                           model_version="m", response_id="r")
    api = SimpleNamespace(models=SimpleNamespace(generate_content=lambda **kw: resp))
    with tempfile.TemporaryDirectory() as t:
        c = llm.Client("live", CFG, cache_dir=Path(t) / "c", usage_path=Path(t) / "c" / "u.json", today="2026-11-09", api=api, sleep=lambda s: None)
        try:
            c.ask("t", "v1", "s", "x", {})
        except llm.LLMError as e:
            assert "không phải JSON" in str(e) and c.used_today("chinh") == 0 and not list((Path(t) / "c" / "t").glob("*.json"))
            return
        raise AssertionError("phải lỗi")


# ---- thiếu khoá: dừng trước khi tốn lượt ----

def run_script(*args):
    env = {k: v for k, v in os.environ.items() if k not in ("GEMINI_API_KEY", "ANTHROPIC_API_KEY")}  # mô phỏng shell không có khoá nào
    return subprocess.run([sys.executable, "-X", "utf8", "-I", *args], cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8")


def test_live_without_key_stops_immediately_everywhere():
    # mỗi bước đòi khoá của nhà cung cấp mình dùng: 2.2 (links) dùng Gemini, 1.6 (concepts, vai trich) dùng Anthropic, run_all đòi cả hai
    for script, need in ((["src/run_all.py", "--llm", "live"], ("GEMINI_API_KEY", "ANTHROPIC_API_KEY")), (["src/links.py", "--llm", "live"], ("GEMINI_API_KEY",)),
                         (["src/concepts.py", "--llm", "live"], ("ANTHROPIC_API_KEY",))):
        out = run_script(*script)
        assert out.returncode != 0 and all(v in out.stderr for v in need), (script, out.returncode, out.stderr[-200:])
    out = run_script("src/run_all.py", "--llm", "live")
    assert "chưa chạy bước nào" in out.stderr and "[ 1/" not in out.stdout, "dừng trước khi chạy bước đầu tiên"


# ---- phản hồi không hợp lệ không được lưu vĩnh viễn ----

def test_invalid_response_is_quarantined_costs_quota_and_next_run_calls_again():
    n = {"calls": 0}

    def behaviour(model, user):  # lần đầu trả phản hồi sai, lần sau trả đúng
        n["calls"] += 1
        return {"ok": False} if n["calls"] == 1 else {"ok": True}

    def must_be_ok(out):
        if out.get("ok") is not True:
            raise ValueError("phản hồi không hợp lệ")
    with tempfile.TemporaryDirectory() as t:
        c1, _ = fake_client(t, behaviour)
        try:
            c1.ask("t", "v1", "s", "x", {}, validate=must_be_ok)
            raise AssertionError("phản hồi sai phải bị từ chối")
        except ValueError:
            pass
        assert c1.used_today("chinh") == 1, "đã tốn lượt"
        task_dir = Path(t) / "cache" / "t"
        assert not list(task_dir.glob("*.json")), "phản hồi sai KHÔNG vào cache chính"
        saved = list((task_dir / "_rejected").glob("*.json"))
        assert len(saved) == 1 and "không hợp lệ" in json.loads(saved[0].read_text(encoding="utf-8"))["rejected_reason"]
        c2, seen2 = fake_client(t, behaviour)  # chạy lại: gọi lại (không bị kẹt vào phản hồi sai)
        rec = c2.ask("t", "v1", "s", "x", {}, validate=must_be_ok)
        assert rec["output"] == {"ok": True} and len(seen2) == 1 and c2.used_today("chinh") == 2


def test_cached_response_that_fails_a_stricter_validator_is_quarantined_and_refetched():
    n = {"calls": 0}

    def versions(model, user):  # lần gọi đầu trả v=1, các lần sau v=2
        n["calls"] += 1
        return {"v": 1} if n["calls"] == 1 else {"v": 2}
    with tempfile.TemporaryDirectory() as t:
        c, seen = fake_client(t, versions)
        c.ask("t", "v1", "s", "x", {})  # không validate: phản hồi {"v": 1} vào cache chính
        def strict(out):
            if out.get("v") != 2:
                raise ValueError("cần v=2")
        rec = c.ask("t", "v1", "s", "x", {}, validate=strict)  # cache cũ không qua kiểm chặt hơn -> gọi lại
        assert rec["output"] == {"v": 2} and len(seen) == 2
        assert len(list((Path(t) / "cache" / "t" / "_rejected").glob("*.json"))) == 1
        assert c.ask("t", "v1", "s", "x", {}, validate=strict)["output"] == {"v": 2} and len(seen) == 2  # lần sau đọc từ cache


# ---- llm_client: log tiến độ ----

def test_client_logs_live_calls_with_label_but_not_cache_hits():
    lines = []
    with tempfile.TemporaryDirectory() as t:
        c, _ = fake_client(t, lambda model, user: {"ok": 1})
        c.log = lines.append
        c.ask("t", "v1", "s", "x", {}, label="lô 3/13")
        assert len(lines) == 2 and "lô 3/13" in lines[0] and "gọi m-chinh" in lines[0] and "xong sau" in lines[1], lines
        c.ask("t", "v1", "s", "x", {}, label="lô 3/13")  # đọc từ cache: không thêm dòng nào
        assert len(lines) == 2 and c.hits == 1, lines


def test_client_is_silent_by_default():
    with tempfile.TemporaryDirectory() as t:
        c, _ = fake_client(t, lambda model, user: {"ok": 1})
        assert c.log is None
        c.ask("t", "v1", "s", "x", {})  # không log thì không lỗi


def test_client_logs_retry_with_code_and_wait():
    try:  # _call chỉ bắt errors.APIError nếu gói google-genai có cài, ngược lại bắt Exception: giả lỗi cho đúng cả hai môi trường
        from google.genai import errors
        base = errors.APIError
    except ImportError:
        base = Exception

    class Boom(base):
        def __init__(self):
            Exception.__init__(self, "bận")
            self.code, self.message = 503, "bận"
    n = {"i": 0}

    def generate_content(**kw):
        n["i"] += 1
        if n["i"] == 1:
            raise Boom()
        return SimpleNamespace(candidates=[SimpleNamespace(finish_reason=SimpleNamespace(name="STOP"))], text="{}", usage_metadata=None, model_version="m", response_id="r")
    lines = []
    with tempfile.TemporaryDirectory() as t:
        c = llm.Client("live", CFG, cache_dir=Path(t) / "c", usage_path=Path(t) / "c" / "u.json", today="2026-11-09", sleep=lambda s: None, log=lines.append,
                       api=SimpleNamespace(models=SimpleNamespace(generate_content=generate_content)))
        c.ask("t", "v1", "s", "x", {})
    retry = [l for l in lines if "503" in l]
    assert len(retry) == 1 and "chờ 20s" in retry[0] and n["i"] == 2, lines


def test_heartbeat_prints_while_blocked_and_stops_after():
    import time
    lines = []
    with llm._Heartbeat(lines.append, "[x]", every=0.02):
        time.sleep(0.15)
    after = len(lines)
    time.sleep(0.1)
    assert after >= 2 and len(lines) == after and "vẫn đang chờ" in lines[0], lines


def test_cache_key_covers_system_text_and_schema():
    k = llm.cache_key
    base = k("m", "t", "v1", "x", "system A", {"a": 1})
    assert base == k("m", "t", "v1", "x", "system A", {"a": 1})
    assert base != k("m", "t", "v1", "x", "system B", {"a": 1}) and base != k("m", "t", "v1", "x", "system A", {"a": 2})


# ---- vai trich (Claude, A34): API giả, không cài gói anthropic, không chạm mạng ----
# Đây là kiểm DUY NHẤT hình lời gọi trước khi tốn tiền thật: mọi thứ gửi lên (tắt suy nghĩ, lược đồ, max_tokens) được khẳng định ở đây.

CFG_T = {**CFG, "trich.provider": "anthropic", "trich.model": "m-claude", "trich.luot_moi_ngay": 100, "trich.max_output_tokens": 1234, "trich.thinking": "between_tools"}
SCHEMA_T = {"type": "object", "additionalProperties": False, "required": ["a"], "properties": {"a": {"type": "integer"}}}
_ABSENT = object()


@contextlib.contextmanager
def anthropic_module(mod):
    """Đặt sys.modules['anthropic'] = mod trong khối with (mod=None: không có gói, import ném ImportError), rồi trả lại như cũ."""
    old = sys.modules.get("anthropic", _ABSENT)
    sys.modules["anthropic"] = mod
    try:
        yield
    finally:
        if old is _ABSENT:
            sys.modules.pop("anthropic", None)
        else:
            sys.modules["anthropic"] = old


def fake_anthropic_module():
    """Gói anthropic giả có đủ những gì _call_anthropic dùng: hai lớp lỗi và lớp Anthropic (ghi lại tham số dựng client)."""
    m = types.ModuleType("anthropic")

    class APIStatusError(Exception):
        def __init__(self, status_code, message="lỗi"):
            Exception.__init__(self, message)
            self.status_code, self.message = status_code, message

    class APIConnectionError(Exception):
        pass

    class Anthropic:
        def __init__(self, **kw):
            m.created.append(kw)
    m.APIStatusError, m.APIConnectionError, m.Anthropic, m.created = APIStatusError, APIConnectionError, Anthropic, []
    return m


def reply(text='{"a": 1}', stop="end_turn", content=None, tin=10, tout=5, stop_details=None):
    return SimpleNamespace(content=content if content is not None else [SimpleNamespace(type="text", text=text)], stop_reason=stop, stop_details=stop_details,
                           usage=SimpleNamespace(input_tokens=tin, output_tokens=tout), model="m-claude-served", id="msg_1", _request_id="req_1")


def claude_client(tmp, responder, cfg=None, log=None):
    """Client live có API Anthropic giả. responder(số_lần_gọi, kwargs) -> phản hồi hoặc ném lỗi. Trả (client, danh sách kwargs đã gửi, danh sách số giây đã chờ)."""
    sent, slept = [], []

    def create(**kw):
        sent.append(kw)
        return responder(len(sent), kw)
    c = llm.Client("live", cfg or CFG_T, cache_dir=Path(tmp) / "cache", usage_path=Path(tmp) / "cache" / "_usage.json", today="2026-11-09", sleep=slept.append, log=log,
                   anthropic_api=SimpleNamespace(messages=SimpleNamespace(create=create)))
    return c, sent, slept


def test_claude_request_has_the_documented_shape():
    with tempfile.TemporaryDirectory() as t:
        c, sent, _ = claude_client(t, lambda n, kw: reply())
        rec = c.ask("t", "v1", "SYS", "câu hỏi", SCHEMA_T, role="trich")
        (kw,) = sent
        assert kw["model"] == "m-claude" and kw["max_tokens"] == 1234 and kw["system"] == "SYS", kw  # max_tokens lấy từ trich.max_output_tokens, không phải khoá chung của Gemini
        assert kw["messages"] == [{"role": "user", "content": "câu hỏi"}]
        assert kw["thinking"] == {"type": "between_tools"}  # cách TẮT suy nghĩ của Sonnet 5.5 ({"type": "disabled"} bị 400), lấy từ trich.thinking
        assert kw["output_config"] == {"format": {"type": "json_schema", "schema": SCHEMA_T}}
        assert not {"temperature", "top_p", "top_k", "tool_choice", "betas", "fallbacks"} & set(kw), "các tham số này làm Sonnet 5.5 báo 400 hoặc đổi model"
        assert rec["output"] == {"a": 1} and rec["requested_model"] == "m-claude" and rec["model"] == "m-claude-served" and rec["request_id"] == "req_1"
        assert c.used_today("trich") == 1 and c.used_today("chinh") == 0 and c.calls == 1


def test_claude_thinking_mode_follows_the_config_so_haiku_can_use_disabled():
    for mode in ("disabled", "between_tools"):
        with tempfile.TemporaryDirectory() as t:
            c, sent, _ = claude_client(t, lambda n, kw: reply(), cfg={**CFG_T, "trich.model": "m-haiku", "trich.thinking": mode})
            c.ask("t", "v1", "s", "x", SCHEMA_T, role="trich")
            assert sent[0]["model"] == "m-haiku" and sent[0]["thinking"] == {"type": mode}, sent[0]


def test_claude_record_keeps_anthropic_usage_names_and_log_shows_tokens():
    lines = []
    with tempfile.TemporaryDirectory() as t:
        c, _, _ = claude_client(t, lambda n, kw: reply(tin=1234, tout=56), log=lines.append)
        rec = c.ask("t", "v1", "s", "x", SCHEMA_T, role="trich")
    assert rec["usage"] == {"input_tokens": 1234, "output_tokens": 56}, rec["usage"]  # không đổi tên sang khoá của Gemini
    assert "token vào 1234, ra 56" in lines[-1], lines
    assert llm.tokens_in_out({"prompt_token_count": 7, "candidates_token_count": 3}) == (7, 3) and llm.tokens_in_out(None) == (None, None)


def test_claude_reads_json_from_the_first_text_block_not_the_first_block():
    blocks = [SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text='{"a": 2}')]
    with tempfile.TemporaryDirectory() as t:
        c, _, _ = claude_client(t, lambda n, kw: reply(content=blocks))
        assert c.ask("t", "v1", "s", "x", SCHEMA_T, role="trich")["output"] == {"a": 2}


def test_claude_refusal_truncation_and_non_json_are_errors_and_not_cached():
    cases = ((reply(stop="refusal", stop_details=SimpleNamespace(category="cyber")), "refusal", "cyber"), (reply(stop="max_tokens"), "max_tokens", ""),
             (reply(text="không phải JSON"), "không phải JSON", ""), (reply(content=[]), "không phải JSON", ""))
    for response, must_contain, extra in cases:
        with tempfile.TemporaryDirectory() as t:
            c, _, _ = claude_client(t, lambda n, kw, r=response: r)
            try:
                c.ask("t", "v1", "s", "x", SCHEMA_T, role="trich")
            except llm.LLMError as e:
                assert must_contain in str(e) and extra in str(e), str(e)
            else:
                raise AssertionError(must_contain)
            assert c.used_today("trich") == 0 and not list((Path(t) / "cache" / "t").glob("*.json")), "không tốn lượt đã đếm, không vào cache"


def test_claude_retries_overload_529_with_waits_but_not_a_400():
    mod = fake_anthropic_module()
    with anthropic_module(mod), tempfile.TemporaryDirectory() as t:
        lines = []
        c, sent, slept = claude_client(t, lambda n, kw: reply() if n == 3 else (_ for _ in ()).throw(mod.APIStatusError(529, "quá tải")), log=lines.append)
        assert c.ask("t", "v1", "s", "x", SCHEMA_T, role="trich")["output"] == {"a": 1}
        assert len(sent) == 3 and slept == [20, 40] and sum("529" in l for l in lines) == 2, (len(sent), slept, lines)
    with anthropic_module(mod), tempfile.TemporaryDirectory() as t:  # cứ 529 mãi: dừng sau ATTEMPTS lần, không chờ sau lần cuối
        c, sent, slept = claude_client(t, lambda n, kw: (_ for _ in ()).throw(mod.APIStatusError(529, "quá tải")))
        try:
            c.ask("t", "v1", "s", "x", SCHEMA_T, role="trich")
        except llm.LLMError as e:
            assert "529" in str(e) and len(sent) == llm.ATTEMPTS and slept == [20, 40], (str(e), len(sent), slept)
        else:
            raise AssertionError("phải lỗi")
    with anthropic_module(mod), tempfile.TemporaryDirectory() as t:  # 400 là lỗi của yêu cầu: gọi đúng một lần, không thử lại (thử lại cũng tốn tiền vô ích)
        c, sent, slept = claude_client(t, lambda n, kw: (_ for _ in ()).throw(mod.APIStatusError(400, "lược đồ không hợp lệ")))
        try:
            c.ask("t", "v1", "s", "x", SCHEMA_T, role="trich")
        except llm.LLMError as e:
            assert "400" in str(e) and "lược đồ không hợp lệ" in str(e) and len(sent) == 1 and slept == []
        else:
            raise AssertionError("phải lỗi")


def test_claude_connection_error_is_an_llm_error():
    mod = fake_anthropic_module()
    with anthropic_module(mod), tempfile.TemporaryDirectory() as t:
        c, sent, _ = claude_client(t, lambda n, kw: (_ for _ in ()).throw(mod.APIConnectionError("mất mạng")))
        try:
            c.ask("t", "v1", "s", "x", SCHEMA_T, role="trich")
        except llm.LLMError as e:
            assert "kết nối" in str(e) and "mất mạng" in str(e) and len(sent) == 1
        else:
            raise AssertionError("phải lỗi")


def test_claude_without_package_or_key_is_unavailable_and_with_both_builds_a_client_with_timeout():
    def ask_trich(t):
        c = llm.Client("live", CFG_T, cache_dir=Path(t) / "cache", usage_path=Path(t) / "cache" / "_usage.json", today="2026-11-09", sleep=lambda s: None)
        return c.ask("t", "v1", "s", "x", SCHEMA_T, role="trich")
    old_key = os.environ.pop("ANTHROPIC_API_KEY", None)
    try:
        with anthropic_module(None), tempfile.TemporaryDirectory() as t:  # chưa cài gói
            try:
                ask_trich(t)
            except llm.LLMUnavailable as e:
                assert "pip install anthropic" in str(e)
            else:
                raise AssertionError("thiếu gói phải báo")
        mod = fake_anthropic_module()
        with anthropic_module(mod), tempfile.TemporaryDirectory() as t:  # có gói, thiếu khoá
            try:
                ask_trich(t)
            except llm.LLMUnavailable as e:
                assert "ANTHROPIC_API_KEY" in str(e) and not mod.created, "thiếu khoá thì chưa dựng client"
            else:
                raise AssertionError("thiếu khoá phải báo")
        os.environ["ANTHROPIC_API_KEY"] = "khoa-gia"
        with anthropic_module(mod), tempfile.TemporaryDirectory() as t:  # có cả hai: dựng client với timeout ngắn rồi gọi (client giả không có messages -> lỗi thuộc tính, sau khi dựng)
            try:
                ask_trich(t)
            except AttributeError:
                pass
            assert mod.created == [{"timeout": llm.ANTHROPIC_TIMEOUT}], mod.created
    finally:
        os.environ.pop("ANTHROPIC_API_KEY", None)
        if old_key is not None:
            os.environ["ANTHROPIC_API_KEY"] = old_key


def test_each_role_goes_to_its_own_provider_and_trich_stays_out_of_roles():
    assert llm.ROLES == ("chinh", "kiem") and "trich" in llm.EXTRA_ROLES and "trich" not in llm.ROLES, "links.py lặp qua ROLES: thêm trich vào đó là gọi thêm một model ở 2.2"
    with tempfile.TemporaryDirectory() as t:
        c, sent, _ = claude_client(t, lambda n, kw: reply())
        gemini_calls = []
        c._call = lambda model, system, user, schema: gemini_calls.append(model) or {"model": model, "request_id": "r", "output": {"a": 9}, "usage": {}}
        assert c.ask("t", "v1", "s", "x", SCHEMA_T, role="chinh")["output"] == {"a": 9} and gemini_calls == ["m-chinh"] and not sent
        assert c.ask("t", "v1", "s", "x", SCHEMA_T, role="trich")["output"] == {"a": 1} and len(sent) == 1 and gemini_calls == ["m-chinh"]
        assert llm.provider_of(CFG, "chinh") == "gemini" and llm.provider_of(CFG_T, "trich") == "anthropic"  # không ghi khoá thì gemini


def test_load_config_requires_trich_and_rejects_an_unknown_provider():
    good = "\n".join(["chinh.model = a", "chinh.luot_moi_ngay = 1", "kiem.model = b", "kiem.luot_moi_ngay = 1", "max_output_tokens = 10",
                      "trich.provider = anthropic", "trich.model = c", "trich.luot_moi_ngay = 1", "trich.max_output_tokens = 10", "trich.thinking = disabled"])
    with tempfile.TemporaryDirectory() as t:
        p = Path(t) / "cfg.md"
        p.write_text(good + "\n", encoding="utf-8")
        assert llm.load_config(p)["trich.model"] == "c"
        for bad, why in ((good.replace("trich.provider = anthropic", "trich.provider = openai"), "openai"), (good.replace("trich.model = c\n", ""), "trich.model"),
                         (good.replace("trich.thinking = disabled", "trich.thinking = adaptive"), "adaptive"), (good.replace("\ntrich.thinking = disabled", ""), "trich.thinking")):
            p.write_text(bad + "\n", encoding="utf-8")
            try:
                llm.load_config(p)
            except llm.LLMError as e:
                assert why in str(e), str(e)
            else:
                raise AssertionError(why)


def test_check_models_asks_each_provider_without_generating():
    class NotFound(Exception):
        status_code = 404
    asked = []

    def retrieve(model):
        asked.append(model)
        if model == "m-claude-sai":
            raise NotFound()
    gem = SimpleNamespace(models=SimpleNamespace(list=lambda: [SimpleNamespace(name="models/m-chinh")]))
    for trich_model, expect in (("m-claude", True), ("m-claude-sai", False)):
        cfg = {**CFG_T, "trich.model": trich_model}
        c = llm.Client("live", cfg, api=gem, anthropic_api=SimpleNamespace(models=SimpleNamespace(retrieve=retrieve)))
        got = llm.check_models(cfg, c)
        assert got == {"m-chinh": True, "m-kiem": False, trich_model: expect}, got
    assert asked == ["m-claude", "m-claude-sai"]


_harness.run(globals())
