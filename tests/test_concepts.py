"""Test bước 1.6 giai đoạn A (concepts.py): cổng cụm, nguồn, đoạn nguyên văn, trùng, targets, lô, chế độ off và thiếu cache. Không gọi mạng: LLM là đối tượng giả."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import _harness  # noqa: E402
import concepts as cc  # noqa: E402
import llm_client  # noqa: E402

B = "BLLD_45-2019."
_CACHE = {}


def real():
    """(doc_id, units, labels, nodes, refs) của BLLĐ, đọc một lần."""
    if "x" not in _CACHE:
        doc, units, labels, nodes, refs = cc.load_inputs("BLLD_45-2019")
        _CACHE["x"] = (doc.doc_id, units, labels, nodes, refs)
    return _CACHE["x"]


class FakeClient:
    """Thay llm_client.Client: respond(đầu vào dạng dict) -> đầu ra; hoặc exc để ném lỗi. Gọi validate như Client thật (ValueError = đầu ra bị loại)."""

    def __init__(self, respond=None, exc=None):
        self.respond, self.exc, self.calls = respond, exc, 0

    def ask(self, task, prompt_version, system, user, schema, role="chinh", payload=None, validate=None, label=None):
        self.calls += 1
        if self.exc:
            raise self.exc
        out = self.respond(json.loads(user))
        if validate is not None:
            validate(out)
        return {"output": out}


def ctx(text, chapeau="", heading=""):
    return {"id": "X.D1.K1", "text": text, "chapeau": chapeau, "heading": heading}


# ---- cổng và đoạn nguyên văn ----

def test_gate_rejects_span_not_in_context_and_partial_words():
    c = ctx("Người lao động có quyền đơn phương chấm dứt hợp đồng lao động.")
    ok, res = cc.gate_span({"span": "người lao động tự ý nghỉ việc", "role": "chu_the", "params": ["W"]}, c)
    assert not ok and "chuỗi từ liền nhau" in res
    ok, res = cc.gate_span({"span": "gười lao độ", "role": "chu_the", "params": []}, c)  # mảnh giữa chừng của từ không khớp
    assert not ok
    ok, res = cc.gate_span({"span": "lao động có đơn phương", "role": "chu_the", "params": []}, c)  # bỏ chữ ở giữa
    assert not ok


def test_gate_rejects_bad_role_and_bad_params():
    c = ctx("Người lao động có quyền nghỉ.")
    assert not cc.gate_span({"span": "Người lao động", "role": "ngoai_ra", "params": []}, c)[0]
    ok, why = cc.gate_span({"span": "Người lao động", "role": "chu_the", "params": ["W", "Z"]}, c)
    assert not ok and "tham số" in why
    ok, row = cc.gate_span({"span": "Người lao động", "role": "chu_the", "params": ["W", "W"]}, c)
    assert ok and row["params"] == ["W"] and row["predicate"] is None and row["how"] == "llm" and row["flags"] == []


def test_span_is_verbatim_slice_of_source_not_the_llm_string():
    c = ctx("Hai bên có thể giao kết hợp đồng lao động bằng lời nói, trừ trường hợp A.")
    ok, row = cc.gate_span({"span": "HỢP ĐỒNG LAO ĐỘNG bằng lời nói", "role": "ket_luan", "params": ["C"]}, c)  # khác hoa thường
    assert ok and row["span"] == "hợp đồng lao động bằng lời nói" and row["span"] in c["text"]
    ok, row = cc.gate_span({"span": "hợp   đồng\nlao động", "role": "dieu_kien", "params": []}, c)  # khác khoảng trắng
    assert ok and row["span"] == "hợp đồng lao động"


def test_source_prefers_own_then_chapeau_then_heading():
    c = ctx("Có giấy phép lao động.", chapeau="Người lao động nước ngoài phải đáp ứng các điều kiện sau đây:", heading="Người lao động nước ngoài làm việc tại Việt Nam")
    assert cc.gate_span({"span": "giấy phép lao động", "role": "dieu_kien", "params": []}, c)[1]["source"] == "own"
    assert cc.gate_span({"span": "phải đáp ứng các điều kiện sau đây", "role": "ket_luan", "params": []}, c)[1]["source"] == "chapeau"
    assert cc.gate_span({"span": "làm việc tại Việt Nam", "role": "dieu_kien", "params": []}, c)[1]["source"] == "heading"
    assert cc.gate_span({"span": "Người lao động nước ngoài", "role": "chu_the", "params": ["W"]}, c)[1]["source"] == "chapeau"  # chữ có ở cả chapeau và heading: lấy chỗ đầu tiên


def test_validate_output_checks_shape_only():
    ids = {"a", "b"}
    cc.validate_output({"units": [{"unit_id": "a", "spans": []}, {"unit_id": "b", "spans": [{"span": "x", "role": "chu_the", "params": []}]}]}, ids)
    for bad in [{}, {"units": "x"}, {"units": [{"unit_id": "z", "spans": []}]}, {"units": [{"unit_id": "a", "spans": []}, {"unit_id": "a", "spans": []}]},
                {"units": [{"unit_id": "a", "spans": [{"span": 1, "role": "chu_the", "params": []}]}]}]:
        try:
            cc.validate_output(bad, ids)
        except ValueError:
            continue
        raise AssertionError(f"lẽ ra phải loại: {bad!r}")


def test_uncovered_signals_reports_only_signals_without_nearby_span():
    contexts = [{"id": "u1", "text": "Người lao động phải báo trước, trừ trường hợp bất khả kháng.", "chapeau": "", "heading": ""},
                {"id": "u2", "text": "Người lao động được nghỉ.", "chapeau": "", "heading": ""}]
    rows = [{"unit": "u1", "source": "own", "_a": 3, "_b": 5}]  # phủ "phải báo" (từ 3 và 4)
    got = {(u["unit"], u["signal"]) for u in cc.uncovered_signals(contexts, rows)}
    assert ("u1", "phải") not in got and ("u1", "trừ") in got and ("u1", "trường hợp") in got and ("u2", "được") in got


# ---- lô và chế độ ----

def test_batches_are_deterministic_in_document_order_and_bounded():
    doc_id, units, labels, nodes, refs = real()
    contexts = cc.unit_contexts(units, labels)
    assert len(contexts) == 881  # số đo của thẻ 1.6 (12/11)
    b1, b2 = cc.make_batches(contexts), cc.make_batches(cc.unit_contexts(units, labels))
    assert [[c["id"] for c in b] for b in b1] == [[c["id"] for c in b] for b in b2]
    assert all(len(b) <= cc.BATCH_SIZE for b in b1)
    assert all(len({cc.dieu_of(c["id"]) for c in b}) == 1 for b in b1)  # mỗi lô một Điều
    assert len(b1) == len({cc.dieu_of(c["id"]) for c in contexts}) + sum(1 for d in {cc.dieu_of(c["id"]) for c in contexts}
                                                                        if sum(1 for c in contexts if cc.dieu_of(c["id"]) == d) > cc.BATCH_SIZE
                                                                        for _ in range((sum(1 for c in contexts if cc.dieu_of(c["id"]) == d) - 1) // cc.BATCH_SIZE))
    assert [c["id"] for b in b1 for c in b] == [c["id"] for c in contexts]
    assert contexts[0]["id"].split(".")[1] == "D1"
    d151d = next(c for c in contexts if c["id"] == B + "D151.K1.d")
    assert d151d["chapeau"].startswith("Người lao động nước ngoài") and d151d["heading"]  # điểm: chapeau là chữ khoản cha, heading là tiêu đề Điều
    assert next(c for c in contexts if c["id"] == B + "D14.K2")["chapeau"] == ""  # khoản không có chapeau


def test_off_mode_gives_only_cond_node_rows_with_real_targets():
    doc_id, units, labels, nodes, refs = real()
    rows, rejected, uncovered, stats, notes = cc.process_doc(doc_id, units, labels, nodes, refs, None)
    assert rows and {r["how"] for r in rows} == {"cond_node"} and {r["role"] for r in rows} == {"ngoai_le"} and not rejected
    by = {r["unit"]: r for r in rows}
    assert by[B + "D14.K2"]["targets"] == [B + "D18.K2", B + "D145.K1.a", B + "D162.K1"]
    assert by[B + "D151.K1.d"]["targets"] == [B + "D154"]
    assert all(r["predicate"] is None and r["flags"] == [] and set(r) == {"unit", "span", "role", "source", "predicate", "params", "targets", "how", "flags"} for r in rows)
    assert all(r["span"] in units[r["unit"]]["text"] for r in rows)
    assert stats["units_in_scope"] == 881 and stats["batches_off"] == stats["batches"] == len(cc.make_batches(cc.unit_contexts(units, labels)))


def test_missing_cache_keeps_machine_part_and_says_so():
    doc_id, units, labels, nodes, refs = real()
    off_rows = cc.process_doc(doc_id, units, labels, nodes, refs, None)[0]
    client = FakeClient(exc=llm_client.CacheMiss("chưa có"))
    rows, rejected, uncovered, stats, notes = cc.process_doc(doc_id, units, labels, nodes, refs, client)
    assert rows == off_rows and stats["batches_cache_miss"] == stats["batches"] and stats["batches_ok"] == 0
    assert "CHƯA ĐỦ KẾT QUẢ LLM" in "\n".join(cc.report_lines(doc_id, stats, uncovered, rejected, notes, "replay"))


def test_quota_stops_calling_and_counts_remaining_batches():
    doc_id, units, labels, nodes, refs = real()
    state = {"n": 0}

    def respond(inp):
        state["n"] += 1
        if state["n"] > 2:
            raise llm_client.QuotaReached("hết")
        return {"units": []}

    class Quota(FakeClient):
        def ask(self, *a, **k):
            try:
                return super().ask(*a, **k)
            except llm_client.QuotaReached:
                raise
    client = Quota(respond=respond)
    rows, rejected, uncovered, stats, notes = cc.process_doc(doc_id, units, labels, nodes, refs, client)
    assert stats["batches_ok"] == 2 and stats["batches_quota"] == stats["batches"] - 2 and client.calls == 3  # sau khi hết hạn mức không gọi nữa


def test_llm_rows_pass_gates_dedupe_with_node_and_get_targets():
    doc_id, units, labels, nodes, refs = real()
    exc14 = units[B + "D14.K2"]["text"][units[B + "D14.K2"]["text"].index("quy định tại khoản 2"):].rstrip(".")

    def respond(inp):
        out = []
        for u in inp["don_vi"]:
            uid, spans = u["unit_id"], []
            if uid == B + "D14.K2":
                spans = [{"span": "Hai bên", "role": "chu_the", "params": []},
                         {"span": "hợp đồng có thời hạn dưới 01 tháng", "role": "dieu_kien", "params": ["C"]},
                         {"span": exc14, "role": "ngoai_le", "params": []},                      # trùng nút 1.5: phải gộp về cond_node
                         {"span": "cụm bịa không có trong chữ luật", "role": "ket_luan", "params": []},
                         {"span": "Hai bên", "role": "xyz", "params": []},
                         {"span": "Hai bên", "role": "chu_the", "params": ["Q"]}]
            if uid == B + "D151.K1.d":
                spans = [{"span": "Người lao động nước ngoài", "role": "chu_the", "params": ["W"]},       # có ở chapeau và heading
                         {"span": "Có giấy phép lao động do cơ quan nhà nước có thẩm quyền của Việt Nam cấp", "role": "dieu_kien", "params": ["W"]}]
            out.append({"unit_id": uid, "spans": spans})
        return {"units": out}

    rows, rejected, uncovered, stats, notes = cc.process_doc(doc_id, units, labels, nodes, refs, FakeClient(respond=respond))
    d14 = [r for r in rows if r["unit"] == B + "D14.K2"]
    assert sorted(r["role"] for r in d14) == ["chu_the", "dieu_kien", "ngoai_le"]
    exc = next(r for r in d14 if r["role"] == "ngoai_le")
    assert exc["how"] == "cond_node" and len(exc["targets"]) == 3 and stats["duplicates_dropped"] == 1
    assert len([r for r in rows if r["unit"] == B + "D14.K2" and r["role"] == "ngoai_le"]) == 1
    assert sorted(r["reason"].split(":")[0] for r in rejected if r["unit"] == B + "D14.K2") == sorted(
        ["cụm không là chuỗi từ liền nhau của ngữ cảnh", "vai ngoài bốn vai", "tham số ngoài WECJGDA"])
    d151 = {r["role"]: r for r in rows if r["unit"] == B + "D151.K1.d"}
    assert d151["chu_the"]["source"] == "chapeau" and d151["dieu_kien"]["source"] == "own" and d151["ngoai_le"]["targets"] == [B + "D154"]
    by_id = {c["id"]: c for c in cc.unit_contexts(units, labels)}
    assert all(r["span"] in by_id[r["unit"]][{"own": "text", "chapeau": "chapeau", "heading": "heading"}[r["source"]]] for r in rows)  # span nguyên văn đúng ở phần `source` nói
    # G4: nút 1.5 của D14.K2 có cụm LLM trùng nên không bị báo; nút của đơn vị khác trong lô có kết quả LLM nhưng không có cụm ngoại lệ LLM thì bị báo
    assert stats["node_without_matching_llm_span"] >= 1 and stats["rows_llm"] == len(rows) - stats["rows_cond_node"]


def test_node_without_llm_exception_span_is_reported():
    doc_id, units, labels, nodes, refs = real()
    rows, rejected, uncovered, stats, notes = cc.process_doc(doc_id, units, labels, nodes, refs,
                                                             FakeClient(respond=lambda inp: {"units": [{"unit_id": u["unit_id"], "spans": []} for u in inp["don_vi"]]}))
    assert stats["batches_ok"] == stats["batches"] and stats["node_without_matching_llm_span"] == stats["rows_cond_node"] and stats["rows_llm"] == 0


def test_units_dropped_by_llm_are_counted_and_batches_follow_dieu():
    doc_id, units, labels, nodes, refs = real()

    def respond(inp):  # bỏ hẳn đơn vị đầu của mỗi lô (không trả mục nào cho nó)
        return {"units": [{"unit_id": u["unit_id"], "spans": []} for u in inp["don_vi"][1:]]}

    rows, rejected, uncovered, stats, notes = cc.process_doc(doc_id, units, labels, nodes, refs, FakeClient(respond=respond))
    report = "\n".join(cc.report_lines(doc_id, stats, uncovered, rejected, notes, "live"))
    assert stats["units_without_entry"] == stats["batches"] and "KHÔNG trả mục nào" in report


# ---- A35: hai lỗi tìm thấy sau lần chạy live đầu (13/11) ----

def test_khoan_under_a_dieu_lead_in_gets_it_as_chapeau_and_other_units_are_unchanged():
    doc_id, units, labels, nodes, refs = real()
    contexts = cc.unit_contexts(units, labels)
    by_id = {c["id"]: c for c in contexts}
    assert len(contexts) == 881
    assert by_id[B + "D108.K1"]["chapeau"] == units[B + "D108"]["text"] and by_id[B + "D108.K1"]["chapeau"].endswith(":")
    with_lead = [c for c in contexts if units[c["id"]]["type"] == "khoan" and c["chapeau"]]
    # số đo 13/11: 46 khoản thuộc 10 Điều (D3 D25 D56 D58 D67 D99 D108 D125 D199 D205); cả 10 câu dẫn đều kết thúc bằng ":" (là câu dẫn danh sách, không phải quy tắc độc lập)
    assert len(with_lead) == 46 and len({cc.dieu_of(c["id"]) for c in with_lead}) == 10
    assert all(c["chapeau"].rstrip().endswith(":") and c["chapeau"] == units[units[c["id"]]["parent"]]["text"] for c in with_lead)
    assert by_id[B + "D14.K2"]["chapeau"] == ""  # Điều 14 không có câu dẫn riêng: khoản vẫn không có chapeau
    assert by_id[B + "D151.K1.d"]["chapeau"] == units[B + "D151.K1"]["text"]  # điểm vẫn lấy chữ khoản cha như cũ


def test_llm_exception_span_nested_in_node_is_dropped_by_position_but_a_separate_one_stays():
    doc_id, units, labels, nodes, refs = real()
    uid = B + "D185.K5"
    node = {r["unit"]: r for r in cc.process_doc(doc_id, units, labels, nodes, refs, None)[0]}[uid]["span"]
    longer = "trường hợp " + node  # chữ LLM chứa chữ nút (thêm "trường hợp" đứng trước), đúng ca đã gặp ở lần chạy live
    assert longer in units[uid]["text"] and "quyết định theo đa số" in units[uid]["text"]

    def respond(inp):
        spans = {uid: [{"span": longer, "role": "ngoai_le", "params": []},                    # chứa nút: bỏ
                       {"span": "quyết định theo đa số", "role": "ngoai_le", "params": []},    # không chồng nút: giữ
                       {"span": "làm việc theo nguyên tắc tập thể", "role": "ket_luan", "params": []}]}
        return {"units": [{"unit_id": u["unit_id"], "spans": spans.get(u["unit_id"], [])} for u in inp["don_vi"]]}
    rows, rejected, uncovered, stats, notes = cc.process_doc(doc_id, units, labels, nodes, refs, FakeClient(respond=respond))
    exc = sorted((r["how"], r["span"]) for r in rows if r["unit"] == uid and r["role"] == "ngoai_le")
    assert exc == [("cond_node", node), ("llm", "quyết định theo đa số")], exc
    assert stats["duplicates_dropped"] == 1 and any(r["unit"] == uid and r["role"] == "ket_luan" for r in rows)


_harness.run(globals())
