"""Test checks (kiểm tra độc lập), graph (đồ thị gộp), viewer (dữ liệu trang xem) và llm_client (cache, replay, hạn mức; API giả, không gọi mạng)."""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import _harness  # noqa: E402
import checks as chk  # noqa: E402
import graph as gr  # noqa: E402
import corpus  # noqa: E402
import llm_client as llm  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


# ---- checks ----

def test_checks_independent_counts_match_l1_for_blld():
    c = chk.independent_counts(corpus.load_manifest()["BLLD_45-2019"].path)
    e = chk.EXPECTED["BLLD_45-2019"]
    assert (c["dieu"], c["khoan"], c["diem"]) == (e.dieu, e.khoan, e.diem)


def test_checks_independent_counter_skips_quote_blocks_and_appendix():
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / "x.txt"
        f.write_text("Điều 1. A\n\n1. Một\n\na) điểm\n\n“Điều 2. Trong khối\n\n1. Trong khối.”.\n\nĐiều 3. B\n\nPHỤ LỤC I\n\nĐiều 9. Không đếm\n", encoding="utf-8")
        c = chk.independent_counts(f)
    assert (c["dieu"], c["khoan"], c["diem"]) == (2, 1, 1)


def test_checks_lead_in_is_khoan_for_diem_and_dieu_for_khoan_under_a_dieu():
    # A35: khoản đứng thẳng dưới Điều có chữ nhận chữ của Điều làm câu dẫn; trước đây checks chỉ tính cho điểm nên báo lỗi oan cụm chapeau ở khoản.
    units = {"B.D1": {"type": "dieu", "text": "Các bên lựa chọn nội dung sau:"}, "B.D1.K1": {"type": "khoan", "text": "Tiền lương;", "parent": "B.D1"},
             "B.D1.K2": {"type": "khoan", "text": "Nghỉ phép:", "parent": "B.D1"}, "B.D1.K2.a": {"type": "diem", "text": "Nghỉ hằng năm.", "parent": "B.D1.K2"},
             "B.D2": {"type": "dieu", "text": "", "heading": "Tiêu đề"}, "B.D2.K1": {"type": "khoan", "text": "Một.", "parent": "B.D2"}}
    assert chk.lead_in_text(units, units["B.D1.K1"]) == "Các bên lựa chọn nội dung sau:"
    assert chk.lead_in_text(units, units["B.D1.K2.a"]) == "Nghỉ phép:"          # điểm: chữ khoản cha, không phải Điều
    assert chk.lead_in_text(units, units["B.D2.K1"]) == ""                      # Điều không có chữ riêng: khoản không có câu dẫn
    assert chk.lead_in_text(units, units["B.D1"]) == ""                         # Điều không có cha


def test_checks_all_checks_clean():
    docs = corpus.load_manifest()
    bad = [(name, p[:3]) for name, p in chk.checks(docs) if p]
    assert not bad, bad


def test_checks_residue_guard_fails_on_new_or_missing_unhandled_case():
    known = {"B.D1", "B.D2"}
    assert chk.residue_problems({"B.D1", "B.D2"}, known) == []
    assert "thừa ['B.D3']" in chk.residue_problems({"B.D1", "B.D2", "B.D3"}, known)[0]
    assert "thiếu ['B.D2']" in chk.residue_problems({"B.D1"}, known)[0]
    assert {"B." + u for u in chk.BLLD_UNHANDLED_KNOWN} == {"B.D24.K3", "B.D188.K1"}


def test_checks_detects_broken_version_intervals():
    ok = {"X.D1": [{"id": "X.D1", "version": 1, "previous_version": None, "effective_from": "2021-01-01", "effective_to": "2023-01-01"},
                   {"id": "X.D1", "version": 2, "previous_version": 1, "effective_from": "2023-01-01", "effective_to": None}]}
    assert chk.version_problems(ok) == []
    overlap = {"X.D1": [dict(ok["X.D1"][0]), {**ok["X.D1"][1], "effective_from": "2022-06-01"}]}
    assert any("chồng" in x for x in chk.version_problems(overlap))
    open_prev = {"X.D1": [{**ok["X.D1"][0], "effective_to": None}, ok["X.D1"][1]]}
    assert any("chưa đóng" in x for x in chk.version_problems(open_prev))
    jump = {"X.D1": [ok["X.D1"][0], {**ok["X.D1"][1], "version": 3, "previous_version": 2}]}
    assert any("không liên tiếp" in x for x in chk.version_problems(jump))


# ---- graph / viewer ----

def test_graph_has_no_dangling_ends_and_expected_sizes():
    docs, nodes, edges = gr.build()
    assert len(docs) == 18
    ty = {t: sum(1 for n in nodes.values() if n["type"] == t) for t in ("document", "dieu", "dieu_kien", "pl")}
    assert ty["document"] == 18 and ty["dieu"] == 893 - 220 and ty["pl"] == 28 and ty["dieu_kien"] > 50
    for e in edges:
        assert e["s"] in nodes and e["o"] in nodes, e
    preds = {e["p"] for e in edges}
    assert {"refers_to", "exception_of", "details", "based_on", "replaces", "amends", "repeals", "overrides", "supplements_list"} <= preds


def test_graph_intervals_reflect_versions_and_document_end():
    docs, nodes, edges = gr.build()
    assert nodes["ND_28-2020"]["intervals"] == [["2020-04-15", "2022-01-17", "normal", 1]]
    assert nodes["ND_152-2020.D7.K6"]["intervals"][0][1] == "2023-09-18" and len(nodes["ND_152-2020.D7.K6"]["intervals"]) == 2
    assert nodes["BLLD_45-2019.D154.K8a"]["intervals"][0][0] == "2026-01-01"
    assert nodes["ND_283-2026.D61.K2"]["intervals"][0][2] == "pending_event"
    assert all(n["parent"] in nodes for n in nodes.values() if n["parent"])


def test_viewer_data_is_consistent_with_graph():
    sys.path.insert(0, str(ROOT / "utils" / "viewer"))
    import viewer
    data = viewer.build_data()
    assert data["asOf"] == "2026-09-10" and "2025-08-07" in data["dates"] and "2023-09-18" in data["dates"]
    assert len(data["docs"]) == 18 and data["nodes"] and data["edges"]
    html = viewer.render({**data, "nodes": data["nodes"][:5], "edges": []})
    assert "/*DATA*/" not in html and "/*CYTOSCAPE*/" not in html and "</script" not in html.split("const DATA")[1].split("(function")[0]


# ---- llm_client ----

CFG = {"chinh.model": "m-chinh", "chinh.luot_moi_ngay": 2, "kiem.model": "m-kiem", "kiem.luot_moi_ngay": 1, "max_output_tokens": 100}


class FakeApi:
    def __init__(self):
        self.calls = 0


def make(mode, tmp, api=None):
    c = llm.Client(mode, CFG, cache_dir=Path(tmp) / "cache", usage_path=Path(tmp) / "cache" / "_usage.json", today="2026-11-09")
    if api is not None:
        c._call = lambda model, system, user, schema: (api.__setattr__("calls", api.calls + 1) or
                                                       {"model": model, "request_id": "r", "output": {"echo": user}, "usage": {}})
    return c


def test_llm_off_and_replay_miss_never_touch_network():
    with tempfile.TemporaryDirectory() as t:
        for mode, exc in (("off", llm.LLMUnavailable), ("replay", llm.CacheMiss)):
            try:
                make(mode, t).ask("task", "v1", "sys", "câu hỏi", {})
            except exc:
                continue
            raise AssertionError(mode)


def test_llm_live_caches_and_replay_returns_same_record():
    with tempfile.TemporaryDirectory() as t:
        api = FakeApi()
        r1 = make("live", t, api).ask("task", "v1", "sys", "câu hỏi", {})
        r2 = make("live", t, api).ask("task", "v1", "sys", "câu hỏi", {})
        r3 = make("replay", t).ask("task", "v1", "sys", "câu hỏi", {})
        assert api.calls == 1 and r1["output"] == r2["output"] == r3["output"] == {"echo": "câu hỏi"}
        saved = list((Path(t) / "cache" / "task").glob("*.json"))
        assert len(saved) == 1 and json.loads(saved[0].read_text(encoding="utf-8"))["requested_model"] == "m-chinh"


def test_llm_cache_key_depends_on_model_task_prompt_and_input():
    k = llm.cache_key
    assert k("m", "t", "v1", "x") != k("m2", "t", "v1", "x") != k("m", "t2", "v1", "x")
    assert k("m", "t", "v1", "x") != k("m", "t", "v2", "x") and k("m", "t", "v1", "x") != k("m", "t", "v1", "y")
    assert k("m", "t", "v1", "x") == k("m", "t", "v1", "x")


def test_llm_stops_cleanly_at_daily_quota_per_role():
    with tempfile.TemporaryDirectory() as t:
        api = FakeApi()
        c = make("live", t, api)
        c.ask("task", "v1", "s", "một", {})
        c.ask("task", "v1", "s", "hai", {})
        try:
            c.ask("task", "v1", "s", "ba", {})
            raise AssertionError("phải dừng ở hạn mức")
        except llm.QuotaReached:
            pass
        assert api.calls == 2 and c.used_today("chinh") == 2
        c.ask("task", "v1", "s", "một", {})  # đã lưu: đọc từ cache, không tốn lượt
        assert api.calls == 2
        c.ask("task", "v1", "s", "kiểm", {}, role="kiem")
        try:
            c.ask("task", "v1", "s", "kiểm 2", {}, role="kiem")
            raise AssertionError("vai kiểm hạn mức 1")
        except llm.QuotaReached:
            pass


def test_llm_config_is_read_from_llm_config_md():
    cfg = llm.load_config()
    assert cfg["chinh.model"].startswith("gemini") and cfg["kiem.model"] != cfg["chinh.model"]
    assert cfg["chinh.luot_moi_ngay"] > cfg["kiem.luot_moi_ngay"] and cfg["max_output_tokens"] == 32000
    # vai trich (A34) là vai MỚI cho Claude; chinh và kiem vẫn là Gemini để cache của 2.2 (khoá theo tên model) không hụt
    assert llm.provider_of(cfg, "chinh") == llm.provider_of(cfg, "kiem") == "gemini" and llm.provider_of(cfg, "trich") == "anthropic"
    assert cfg["trich.model"].startswith("claude") and cfg["trich.max_output_tokens"] == 16000 and "trich" not in llm.ROLES
    assert cfg["trich.thinking"] in llm.THINKING_MODES


_harness.run(globals())
