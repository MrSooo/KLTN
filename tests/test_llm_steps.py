"""Test nhánh LLM của L4 và L3, giãn nhịp RPM của llm_client, và đường thiếu khoá của run_all. Toàn bộ dùng API giả: không chạm mạng, không tốn lượt.

Nguyên tắc cần giữ (CLAUDE.md mục 4): đề xuất của LLM không được áp thẳng; đầu ra sai bị loại, nhãn đẩy Điều ra khỏi substantive phải qua model kiểm.
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import _harness  # noqa: E402
import l3_links as l3  # noqa: E402
import l4_classify as l4  # noqa: E402
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


# ---- L4 ----

def row(uid, heading, how="default_pending_llm"):
    return {"id": uid, "label": "substantive", "how": how, "heading": heading, "flags": ["llm_pending"] if how == "default_pending_llm" else []}


UNITS = {"A": {"A.D1": {"type": "dieu", "heading": "Quy trình A", "text": "Nội dung một"}, "A.D2": {"type": "dieu", "heading": "Quy trình B", "text": "Nội dung hai"},
               "A.D3": {"type": "dieu", "heading": "Hợp đồng", "text": "Nội dung ba"}, "A.D4": {"type": "dieu", "heading": "Giải thích", "text": "Nội dung bốn"}},
         "B": {"B.D1": {"type": "dieu", "heading": "Quy trình A", "text": "Nội dung một"}}}
DOCS = {"A": SimpleNamespace(loai="Nghị định"), "B": SimpleNamespace(loai="Văn bản hợp nhất")}


def rows():
    return [row("A.D1", "Quy trình A"), row("A.D2", "Quy trình B"), row("A.D3", "Hợp đồng"), row("A.D4", "Giải thích"), row("B.D1", "Quy trình A"),
            row("A.D9", "Hiệu lực thi hành", how="regex")]


def chinh_says(items):
    return {x["k"]: ("procedural" if x["tieu_de"].startswith("Quy trình") else "definition" if x["tieu_de"] == "Giải thích" else "substantive") for x in items}


def behave(model, user):
    items = json.loads(user)
    labels = chinh_says(items)
    if model == "m-kiem":  # model kiểm đồng ý với "Quy trình A" nhưng không đồng ý với "Quy trình B"
        labels = {x["k"]: ("procedural" if x["tieu_de"] == "Quy trình A" else "substantive") for x in items}
    return {"labels": [{"k": k, "label": v} for k, v in labels.items()]}


def test_l4_validate_labels_rejects_bad_batches():
    keys = ["k1", "k2"]
    ok = {"labels": [{"k": "k1", "label": "procedural"}, {"k": "k2", "label": "substantive"}]}
    assert l4.validate_labels(ok, keys) == {"k1": "procedural", "k2": "substantive"}
    bad = [{"labels": [{"k": "k1", "label": "procedural"}]},                                                   # thiếu k2
           {"labels": ok["labels"] + [{"k": "k3", "label": "procedural"}]},                                    # thừa mã ngoài lô
           {"labels": [{"k": "k1", "label": "form"}, {"k": "k2", "label": "substantive"}]},                    # nhãn ngoài tập
           {"labels": [{"k": "k1", "label": "procedural"}, {"k": "k1", "label": "authority"}]},                # trùng mã
           {"nhan": []}, [], "text"]
    for b in bad:
        try:
            l4.validate_labels(b, keys)
        except ValueError:
            continue
        raise AssertionError(b)


def test_l4_collect_items_asks_once_for_duplicate_heading_and_snippet():
    items = l4.collect_items(rows(), UNITS, DOCS)
    assert [it["heading"] for it in items] == ["Quy trình A", "Quy trình B", "Hợp đồng", "Giải thích"], "hàng regex không vào lô; bản trùng chỉ một mục"
    assert items[0]["ids"] == ["A.D1", "B.D1"] and items[0]["k"] == "k1"


def test_l4_full_flow_applies_only_what_passes_verification():
    with tempfile.TemporaryDirectory() as t:
        c, seen = fake_client(t, behave)
        r = rows()
        outcome, stats, notes, n = l4.llm_classify(c, r, UNITS, DOCS)
        by = {x["id"]: x for x in r}
        assert n == 4 and len(seen) == 2 and [m for m, _ in seen] == ["m-chinh", "m-kiem"], "một lô chính, một lô kiểm"
        for uid in ("A.D1", "B.D1"):  # cả hai model đồng ý: nhận nhãn, cờ llm_verified
            assert (by[uid]["label"], by[uid]["how"], by[uid]["flags"]) == ("procedural", "llm", ["llm_proposed", "llm_verified"])
        assert (by["A.D2"]["label"], by["A.D2"]["how"], by["A.D2"]["flags"]) == ("substantive", "default_pending_llm", ["llm_pending", "llm_disagree"])
        assert (by["A.D3"]["label"], by["A.D3"]["flags"]) == ("substantive", ["llm_proposed"]) and by["A.D4"]["label"] == "definition"
        assert by["A.D9"]["how"] == "regex" and by["A.D9"]["label"] == "substantive", "hàng đã xếp bằng regex không bị LLM đụng"
        assert outcome["tra_ve_nhan_tam_disagree"] == 1 and outcome["nhan_procedural"] == 2 and not notes


def test_l4_without_verification_a_demotion_is_not_applied():
    with tempfile.TemporaryDirectory() as t:
        c, _ = fake_client(t, behave)
        r = rows()
        items = l4.collect_items(r, UNITS, DOCS)
        proposed = l4.run_pass(c, items, "chinh", __import__("collections").Counter(), [])
        assert proposed["k1"] == "procedural"
        out = l4.apply_llm(r, items, proposed, verified={})  # model kiểm chưa chạy (hết hạn mức / thiếu cache)
        assert {x["id"]: x["label"] for x in r if x["id"] in ("A.D1", "A.D2", "B.D1")} == {"A.D1": "substantive", "A.D2": "substantive", "B.D1": "substantive"}
        assert out["tra_ve_nhan_tam_unverified"] == 3 and next(x for x in r if x["id"] == "A.D1")["flags"] == ["llm_pending", "llm_unverified"]


def test_l4_rejected_batch_leaves_rows_untouched():
    with tempfile.TemporaryDirectory() as t:
        c, _ = fake_client(t, lambda model, user: {"labels": [{"k": "k1", "label": "procedural"}]})  # thiếu các mã còn lại
        r = rows()
        outcome, stats, notes, n = l4.llm_classify(c, r, UNITS, DOCS)
        assert stats["chinh_batch_rejected"] == 1 and outcome["chua_co_de_xuat"] == 5 and "lô bị loại" in notes[0]
        assert [x["label"] for x in r] == ["substantive"] * 6 and all(x["how"] != "llm" for x in r)


def test_l4_quota_stop_is_graceful_and_keeps_finished_batches():
    saved = l4.BATCH
    l4.BATCH = 2
    try:
        with tempfile.TemporaryDirectory() as t:
            c, seen = fake_client(t, behave, cfg={**CFG, "chinh.luot_moi_ngay": 1})
            r = rows()
            outcome, stats, notes, n = l4.llm_classify(c, r, UNITS, DOCS)
            assert stats["chinh_quota_stop"] == 1 and "chạy tiếp hôm sau" in notes[0]
            by = {x["id"]: x for x in r}
            # lô 1 = {Quy trình A, Quy trình B} đã gọi xong và vẫn qua model kiểm: A (cả bản trùng B.D1) được nhận, B bị trả về vì kiểm không đồng ý
            assert [(by[u]["label"], by[u]["how"]) for u in ("A.D1", "B.D1")] == [("procedural", "llm")] * 2
            assert (by["A.D2"]["label"], by["A.D2"]["flags"]) == ("substantive", ["llm_pending", "llm_disagree"])
            # lô 2 = {Hợp đồng, Giải thích} chưa gọi được vì hết hạn mức chính: giữ nguyên nhãn tạm
            assert by["A.D3"]["how"] == "default_pending_llm" and by["A.D4"]["how"] == "default_pending_llm"
            assert [m for m, _ in seen] == ["m-chinh", "m-kiem"] and c.used_today("chinh") == 1
    finally:
        l4.BATCH = saved


def test_l4_replay_with_empty_cache_changes_nothing_and_never_calls():
    with tempfile.TemporaryDirectory() as t:
        c = llm.Client("replay", CFG, cache_dir=Path(t) / "cache", usage_path=Path(t) / "cache" / "_usage.json")
        r = rows()
        before = json.dumps(r)
        outcome, stats, notes, n = l4.llm_classify(c, r, UNITS, DOCS)
        assert json.dumps(r) == before and stats["chinh_cache_miss_items"] == 4 and c.calls == 0


def test_l4_replay_reads_what_live_saved_and_costs_no_quota():
    with tempfile.TemporaryDirectory() as t:
        live, seen = fake_client(t, behave)
        r1 = rows()
        l4.llm_classify(live, r1, UNITS, DOCS)
        replay = llm.Client("replay", CFG, cache_dir=Path(t) / "cache", usage_path=Path(t) / "cache" / "_usage.json", today="2026-11-09")
        r2 = rows()
        l4.llm_classify(replay, r2, UNITS, DOCS)
        assert r1 == r2 and replay.calls == 0 and replay.hits == 2 and replay.used_today("chinh") == 1, "đọc lại từ cache, không tốn lượt"


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
    assert e["flags"] == ["llm_proposed"] and e["how"] == "llm" and e["check"] == {"first_llm": True, "second_llm": "agree", "keyword": "mức lương tối thiểu"}


def test_l3_isolates_when_second_model_disagrees_keyword_fails_or_only_keyword_proposed():
    assert edges({"chinh": [D91K4], "kiem": [], "note": ""})["BLLD_45-2019.D91"]["flags"] == ["llm_proposed", "isolated"]
    assert edges({"chinh": [D91K4], "kiem": None, "note": "x"})["BLLD_45-2019.D91"]["flags"] == ["llm_proposed", "isolated"], "lượt kiểm chưa có: không nâng cấp"
    e = edges({"chinh": [D5K1], "kiem": [D5K1], "note": ""})["BLLD_45-2019.D5"]
    assert e["flags"] == ["llm_proposed", "isolated"] and e["check"]["keyword"] is None, "hai model đồng ý nhưng từ khoá không có trong Điều đích"
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
    env = {k: v for k, v in os.environ.items() if k != "GEMINI_API_KEY"}  # mô phỏng shell không có khoá
    return subprocess.run([sys.executable, "-X", "utf8", "-I", *args], cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8")


def test_live_without_key_stops_immediately_everywhere():
    for script in (["src/run_all.py", "--llm", "live"], ["src/l4_classify.py", "--llm", "live"], ["src/l3_links.py", "--llm", "live"]):
        out = run_script(*script)
        assert out.returncode != 0 and "GEMINI_API_KEY" in out.stderr, (script, out.returncode, out.stderr[-200:])
    out = run_script("src/run_all.py", "--llm", "live")
    assert "chưa chạy bước nào" in out.stderr and "[ 1/" not in out.stdout, "dừng trước khi chạy bước đầu tiên"


# Không có test chạy l4_classify.py ở chế độ off / replay trên dữ liệu thật: nó sẽ ghi đè data/processed/l4 và báo cáo của lần chạy live.
# Tính chất "replay với cache rỗng không đổi gì" đã kiểm trong bộ nhớ ở test_l4_replay_with_empty_cache_changes_nothing_and_never_calls.


# ---- phản hồi không hợp lệ không được lưu vĩnh viễn ----

def test_invalid_response_is_quarantined_costs_quota_and_next_run_calls_again():
    bad_then_good = {"n": 0}

    def behaviour(model, user):
        bad_then_good["n"] += 1
        items = json.loads(user)
        if bad_then_good["n"] == 1:
            return {"labels": [{"k": items[0]["k"], "label": "substantive"}]}  # thiếu các mã còn lại -> không hợp lệ
        return {"labels": [{"k": x["k"], "label": "substantive"} for x in items]}
    with tempfile.TemporaryDirectory() as t:
        c1, _ = fake_client(t, behaviour)
        r1 = rows()
        _, stats1, notes1, _ = l4.llm_classify(c1, r1, UNITS, DOCS)
        assert stats1["chinh_batch_rejected"] == 1 and "_rejected" in notes1[0] and c1.used_today("chinh") == 1, "đã tốn lượt"
        task_dir = Path(t) / "cache" / l4.TASK
        assert not list(task_dir.glob("*.json")), "phản hồi sai KHÔNG vào cache chính"
        saved = list((task_dir / "_rejected").glob("*.json"))
        assert len(saved) == 1 and "thiếu mã" in json.loads(saved[0].read_text(encoding="utf-8"))["rejected_reason"]
        c2, seen2 = fake_client(t, behaviour)  # chạy lại: gọi lại (không bị kẹt vào phản hồi sai)
        r2 = rows()
        _, stats2, _, _ = l4.llm_classify(c2, r2, UNITS, DOCS)
        assert len(seen2) == 1 and not stats2["chinh_batch_rejected"] and c2.used_today("chinh") == 2
        assert next(x for x in r2 if x["id"] == "A.D3")["how"] == "llm"


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


_harness.run(globals())
