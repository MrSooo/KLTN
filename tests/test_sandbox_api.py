"""Test nhà cung cấp ckey của llm_client, khoá đè theo lần chạy (KLTN_LLM_RUN), tên cache theo lần chạy, và bộ chạy hộp cát qua API (A46).
Toàn bộ dùng máy chủ giả: không chạm mạng, không tốn tiền, không cần CKEY_API_KEY thật.
"""
import io
import json
import os
import sys
import tempfile
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import _harness  # noqa: E402
import corpus  # noqa: E402
import llm_client as llm  # noqa: E402
import sandbox_api  # noqa: E402

CFG = {"chinh.model": "a", "chinh.luot_moi_ngay": 1, "kiem.model": "b", "kiem.luot_moi_ngay": 1, "max_output_tokens": 100,
       "api.provider": "ckey", "api.model": "m-api", "api.base_url": "https://may-chu.gia", "api.luot_moi_ngay": 100, "api.max_output_tokens": 50,
       "ten.model": "m-api", "hop_cat.effort": "khong_co"}


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def reply(text, stop="end_turn"):
    return {"type": "message", "model": "m-api", "id": "chatcmpl-1", "stop_reason": stop, "content": [{"type": "text", "text": text}],
            "usage": {"input_tokens": 0, "output_tokens": 5, "x_ckey": {"cost": 6.5, "request_id": "req_1"}}}


def server(answers, sent):
    """urlopen giả: lần lượt trả các phần tử của answers (dict = thân JSON, int = mã lỗi HTTP); ghi lại (url, headers, thân) đã gửi."""
    it = iter(answers)

    def urlopen(req, timeout=None):
        sent.append((req.full_url, dict(req.header_items()), json.loads(req.data.decode("utf-8"))))
        a = next(it)
        if isinstance(a, int):
            raise urllib.error.HTTPError(req.full_url, a, "lỗi", {}, io.BytesIO(b"upstream unavailable"))
        return FakeResponse(json.dumps(a).encode("utf-8"))
    return urlopen


def client(tmp, answers, sent, mode="live"):
    return llm.Client(mode, CFG, cache_dir=Path(tmp) / "cache", usage_path=Path(tmp) / "cache" / "_usage.json", today="2026-11-19",
                      sleep=lambda s: None, urlopen=server(answers, sent))


class env_key:
    """Đặt CKEY_API_KEY giả trong lúc test, trả lại giá trị cũ sau đó (không bao giờ đọc hay in khoá thật)."""
    def __enter__(self):
        self.old = os.environ.get("CKEY_API_KEY")
        os.environ["CKEY_API_KEY"] = "khoa-gia"

    def __exit__(self, *exc):
        if self.old is None:
            os.environ.pop("CKEY_API_KEY", None)
        else:
            os.environ["CKEY_API_KEY"] = self.old


# ---- llm_client: nhà cung cấp ckey ----

def test_ckey_sends_anthropic_messages_and_records_cost():
    with tempfile.TemporaryDirectory() as t, env_key():
        sent = []
        rec = client(t, [reply('{"x": 1}')], sent).ask("t", "v", "chữ system", "lời user", None, role="api")
        url, headers, body = sent[0]
        assert url == "https://may-chu.gia/v1/messages" and headers["Authorization"] == "Bearer khoa-gia" and headers["Anthropic-version"] == "2023-06-01"
        assert body == {"model": "m-api", "max_tokens": 50, "system": "chữ system", "messages": [{"role": "user", "content": "lời user"}]}
        assert rec["output"] == {"x": 1} and rec["request_id"] == "req_1" and rec["usage"]["cost_vnd"] == 6.5 and rec["boc_rao"] is False


def test_ckey_strips_a_whole_fence_only():
    assert llm.strip_fence('```json\n{"a": 1}\n```') == ('{"a": 1}', True)
    assert llm.strip_fence('{"a": 1}') == ('{"a": 1}', False)
    assert llm.strip_fence('Đây là JSON:\n```json\n{"a": 1}\n```')[1] is False  # chữ ngoài rào: không đoán, để json.loads báo lỗi
    with tempfile.TemporaryDirectory() as t, env_key():
        rec = client(t, [reply('```json\n{"a": 1}\n```')], []).ask("t", "v", "s", "u", None, role="api")
        assert rec["output"] == {"a": 1} and rec["boc_rao"] is True


def test_ckey_retries_503_then_succeeds_and_fails_fast_on_other_errors():
    with tempfile.TemporaryDirectory() as t, env_key():
        sent = []
        assert client(t, [503, reply('{"a": 2}')], sent).ask("t", "v", "s", "u", None, role="api")["output"] == {"a": 2} and len(sent) == 2
    with tempfile.TemporaryDirectory() as t, env_key():
        sent = []
        try:
            client(t, [401], sent).ask("t", "v", "s", "u", None, role="api")
        except llm.LLMError as e:
            assert "401" in str(e) and len(sent) == 1
        else:
            raise AssertionError("401 phải là lỗi ngay")
    with tempfile.TemporaryDirectory() as t, env_key():
        try:
            client(t, [503, 503, 503], []).ask("t", "v", "s", "u", None, role="api")
        except llm.LLMError as e:
            assert "503" in str(e) and not (Path(t) / "cache" / "t").exists()  # lỗi không vào cache
        else:
            raise AssertionError("503 ba lần phải là lỗi")


def test_ckey_rejects_cut_output_and_non_json_without_caching():
    for answer, why in ((reply('{"a":', stop="max_tokens"), "max_tokens"), (reply("không phải JSON"), "JSON")):
        with tempfile.TemporaryDirectory() as t, env_key():
            try:
                client(t, [answer], []).ask("t", "v", "s", "u", None, role="api")
            except llm.LLMError as e:
                assert why in str(e), str(e)
            else:
                raise AssertionError(why)
            assert not (Path(t) / "cache" / "t").exists()


def test_ckey_without_key_does_not_call():
    old = os.environ.pop("CKEY_API_KEY", None)
    try:
        with tempfile.TemporaryDirectory() as t:
            sent = []
            try:
                client(t, [reply("{}")], sent).ask("t", "v", "s", "u", None, role="api")
            except llm.LLMUnavailable as e:
                assert "CKEY_API_KEY" in str(e) and sent == []
            else:
                raise AssertionError("thiếu khoá phải dừng trước khi gọi")
    finally:
        if old is not None:
            os.environ["CKEY_API_KEY"] = old


# ---- khoá đè theo lần chạy, tên cache ----

def test_load_config_run_overrides_and_requires_run_keys():
    base = ["chinh.model = a", "chinh.luot_moi_ngay = 1", "kiem.model = b", "kiem.luot_moi_ngay = 1", "max_output_tokens = 10", "trich.provider = anthropic",
            "trich.model = c", "trich.luot_moi_ngay = 1", "trich.max_output_tokens = 10", "trich.thinking = disabled", "ten.model = sonnet",
            "hop_cat.model = sonnet", "api.provider = ckey", "api.model = g"]
    old = corpus.LLM_RUN
    try:
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "cfg.md"
            p.write_text("\n".join(base + ["ckey.ten.model = g", "ckey.hop_cat.model = g"]) + "\n", encoding="utf-8")
            corpus.LLM_RUN = None
            assert llm.load_config(p)["ten.model"] == "sonnet"  # lần chạy mặc định không bị đè: replay cũ giữ nguyên
            corpus.LLM_RUN = "ckey"
            cfg = llm.load_config(p)
            assert cfg["ten.model"] == "g" and cfg["hop_cat.model"] == "g" and cfg["trich.model"] == "c"
            corpus.LLM_RUN = "khac"
            try:
                llm.load_config(p)
            except llm.LLMError as e:
                assert "khac." in str(e)
            else:
                raise AssertionError("lần chạy không có khoá nào phải là lỗi")
    finally:
        corpus.LLM_RUN = old


def test_cache_name_tags_subset_then_run():
    old = corpus.SUBSET, corpus.LLM_RUN
    try:
        for sub, run, want in ((None, None, "X.json"), ("lldnn", None, "X.lldnn.json"), (None, "ckey", "X.ckey.json"), ("lldnn", "ckey", "X.lldnn.ckey.json")):
            corpus.SUBSET, corpus.LLM_RUN = sub, run
            assert corpus.cache_name("X") == want
    finally:
        corpus.SUBSET, corpus.LLM_RUN = old


# ---- bộ chạy hộp cát ----

def lot_dir(t, model="m-api", n=3):
    d = Path(t) / "hop_cat"
    (d / "lo").mkdir(parents=True)
    (d / "out").mkdir()
    (d / "system.txt").write_text("LỜI NHẮC\n", encoding="utf-8", newline="\n")
    (d / "cau_hinh.json").write_text(json.dumps({"model": model, "effort": "khong_co"}), encoding="utf-8")
    for i in range(1, n + 1):
        (d / "lo" / f"{i:03d}.json").write_text(json.dumps({"lo": i}) + "\n", encoding="utf-8", newline="\n")
    return d


def test_runner_fills_independent_lots_verbatim_and_skips_done_ones():
    with tempfile.TemporaryDirectory() as t, env_key():
        d = lot_dir(t)
        (d / "out" / "002.json").write_text("{}\n", encoding="utf-8")  # lô đã làm: không gọi lại
        sent = []
        answers = [reply(json.dumps({"tra_loi": i})) for i in range(2)]
        code = sandbox_api.Runner(d, client(t, answers, sent)).run_lots(workers=1)
        assert code == 0 and len(sent) == 2
        assert all(b["system"] == "LỜI NHẮC\n" for _u, _h, b in sent)  # nguyên văn system.txt, kể cả xuống dòng cuối
        assert sorted(b["messages"][0]["content"] for _u, _h, b in sent) == [json.dumps({"lo": 1}) + "\n", json.dumps({"lo": 3}) + "\n"]
        assert sorted((d / "nhat_ky.tsv").read_text(encoding="utf-8").splitlines()) == ["001\tm-api\tkhong_co", "003\tm-api\tkhong_co"]
        assert json.loads((d / "out" / "002.json").read_text(encoding="utf-8")) == {}


def test_runner_reports_failed_lot_and_writes_nothing_for_it():
    with tempfile.TemporaryDirectory() as t, env_key():
        d = lot_dir(t, n=1)
        code = sandbox_api.Runner(d, client(t, [reply("[1, 2]")], [])).run_lots(workers=1)  # mảng, không phải đối tượng
        assert code == 1 and not (d / "out" / "001.json").exists() and not (d / "nhat_ky.tsv").exists()


def test_runner_refuses_a_sandbox_built_for_another_model():
    with tempfile.TemporaryDirectory() as t:
        d = lot_dir(t, model="claude-sonnet-5-5")
        try:
            sandbox_api.Runner(d, client(t, [], []))
        except SystemExit as e:
            assert "claude-sonnet-5-5" in str(e)
        else:
            raise AssertionError("hộp cát của model khác phải bị từ chối trước khi gọi")


def test_runner_redo_moves_old_output_and_asks_the_model_again():
    with tempfile.TemporaryDirectory() as t, env_key():
        d = lot_dir(t, n=1)
        sent = []
        r = sandbox_api.Runner(d, client(t, [reply('{"lan": 1}'), reply('{"lan": 2}')], sent))
        assert r.run_lots(workers=1) == 0 and len(sent) == 1
        r.redo(1)  # nhap từ chối lô 1: làm lại
        assert not (d / "out" / "001.json").exists() and json.loads((d / "out_sai" / "001_1.json").read_text(encoding="utf-8")) == {"lan": 1}
        assert r.run_lots(workers=1) == 0 and len(sent) == 2  # gọi lại thật, không đọc lại bản ghi cũ từ cache
        assert json.loads((d / "out" / "001.json").read_text(encoding="utf-8")) == {"lan": 2}
        assert (d / "nhat_ky.tsv").read_text(encoding="utf-8").splitlines() == ["001\tm-api\tkhong_co"] * 2


def test_runner_sends_schema_file_after_system_text():
    with tempfile.TemporaryDirectory() as t, env_key():
        d = lot_dir(t, n=1)
        (d / "schema.json").write_text('{"type": "object"}\n', encoding="utf-8")
        sent = []
        assert sandbox_api.Runner(d, client(t, [reply("{}")], sent)).run_lots(workers=1) == 0
        assert sent[0][2]["system"] == "LỜI NHẮC\n" + sandbox_api.SCHEMA_NOTE + '{"type": "object"}\n'


if __name__ == "__main__":
    _harness.run(globals())
