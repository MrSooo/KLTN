"""Test tầng chuẩn hoá khối của A4 (hướng C) và a4_llm.ClaudeProposer, bằng proposer / client giả: không gọi mạng."""
import contextlib
import io
import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import a4_llm
import a4_versions as a4

ROOT = Path(__file__).resolve().parent.parent
FULL_FILE = ROOT / "data" / "raw" / "blds2015_p4.md"
P = "BLDS2015."
HEAD = "Điều 1. Sửa đổi, bổ sung một số điều của Bộ luật Dân sự số 91/2015/QH13\n\n"
TAIL = "\n\nĐiều 2. Hiệu lực thi hành\n\nLuật này có hiệu lực thi hành từ ngày 01 tháng 01 năm 2027.\n"

MULTI = "1. Sửa đổi, bổ sung khoản 1 và khoản 2 Điều 625 như sau:\n“1. Nội dung một.\n2. Nội dung hai.”."
SUB = ("2. Sửa đổi, bổ sung, bãi bỏ một số khoản của Điều 630 như sau:\na) Sửa đổi, bổ sung khoản 4 như sau:\n"
       "“4. Nội dung khoản bốn mới.”;\nb) Bãi bỏ khoản 5.")


def T(dieu, khoan=None, diem=None):
    return {"dieu": dieu, "khoan": khoan, "diem": diem}


def C(op, dich, quan_he="amends", vao_sau=None, noi_dung=None, kieu_cum=None, cum_cu=None, cum_moi=None):
    return {"op": op, "quan_he": quan_he, "dich": dich, "vao_sau": vao_sau, "noi_dung": noi_dung, "kieu_cum": kieu_cum,
            "cum_cu": cum_cu, "cum_moi": cum_moi}


def ok(*items):
    return {"chi_thi": list(items), "khong_xu_ly_duoc": None}


MULTI_OK = ok(C("replace_unit", [T("625", "1")], noi_dung="1. Nội dung một."),
              C("replace_unit", [T("625", "2")], noi_dung="2. Nội dung hai."))
SUB_OK = ok(C("replace_unit", [T("630", "4")], noi_dung="4. Nội dung khoản bốn mới."), C("repeal_unit", [T("630", "5")]))


class Fake:
    """Proposer giả: trả lần lượt các đề xuất cho trước, ghi lại (khối, phản hồi) của mỗi lần gọi."""

    def __init__(self, *outputs, error=None):
        self.outputs, self.error, self.calls = list(outputs), error, []

    def propose(self, block_text, feedback=None):
        self.calls.append((block_text, feedback))
        if self.error:
            raise self.error
        return self.outputs.pop(0), {"model": "fake", "key": f"k{len(self.calls)}", "cached": False}


@contextlib.contextmanager
def proposer(p):
    saved = a4.BLOCK_PROPOSER
    a4.BLOCK_PROPOSER = p
    try:
        yield p
    finally:
        a4.BLOCK_PROPOSER = saved


def apply_text(body):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "luat_x.md"
        path.write_text(HEAD + body + TAIL, encoding="utf-8")
        return a4.apply_series(FULL_FILE, [path])


def raises(code, fn, *args):
    try:
        fn(*args)
    except a4.A4Error as e:
        assert e.code == code, f"mã lỗi {e.code} ({e.message}), cần {code}"
        return e
    raise AssertionError(f"phải báo lỗi {code}")


# ---- tầng chuẩn hoá trong A4 ----

def test_off_mode_keeps_unknown_line_error():
    with proposer(None):
        e = raises("E_UNKNOWN_LINE", apply_text, MULTI)
    assert e.line.startswith("1. Sửa đổi, bổ sung khoản 1 và khoản 2 Điều 625")


def test_multi_target_block_becomes_two_checked_directives():
    with proposer(Fake(MULTI_OK)) as fake:
        run = apply_text(MULTI + "\n\n3. Bãi bỏ khoản 2 Điều 621.")
    ds = run.docs[0].directives
    assert [(d.op, d.targets, d.via) for d in ds] == [("replace_unit", [P + "D625.K1"], "llm"), ("replace_unit", [P + "D625.K2"], "llm"),
                                                      ("repeal_unit", [P + "D621.K2"], "ky_hieu")]
    assert [d.seq for d in ds] == [1, 2, 3] and ds[0].line_no == 3 == ds[1].line_no
    assert sorted(run.changed) == [P + "D625.K1", P + "D625.K2"] and P + "D621.K2" in run.closed
    (block,) = run.docs[0].llm
    assert block.rounds == 1 and block.canonical[0] == "Sửa đổi, bổ sung khoản 1 Điều 625 như sau:"
    assert len(fake.calls) == 1 and fake.calls[0][1] is None and "khoản 1 và khoản 2 Điều 625" in fake.calls[0][0]
    assert "Bãi bỏ khoản 2 Điều 621" not in fake.calls[0][0], "khối phải dừng trước mục đánh số kế tiếp"
    report = a4.format_report(run)
    assert "== Khối chuẩn hoá bằng LLM" in report and "    Sửa đổi, bổ sung khoản 2 Điều 625 như sau:" in report


def test_scope_block_with_relative_sub_directives():
    with proposer(Fake(SUB_OK)):
        run = apply_text(SUB)
    assert [(d.op, d.targets) for d in run.docs[0].directives] == [("replace_unit", [P + "D630.K4"]), ("repeal_unit", [P + "D630.K5"])]
    assert P + "D630.K5" in run.closed and P + "D630.K4" in run.changed


def test_fast_path_document_never_calls_the_proposer():
    with proposer(Fake()) as fake:
        run = apply_text("1. Bãi bỏ khoản 2 Điều 621.")
    assert fake.calls == [] and run.docs[0].llm == () and "Khối chuẩn hoá" not in a4.format_report(run)


def test_failed_checks_are_sent_back_and_repaired():
    missing_k2 = ok(C("replace_unit", [T("625", "1")], noi_dung="1. Nội dung một."))
    with proposer(Fake(missing_k2, MULTI_OK)) as fake:
        run = apply_text(MULTI)
    assert run.docs[0].llm[0].rounds == 2 and len(run.changed) == 2
    feedback = json.loads(fake.calls[1][1])
    assert feedback["de_xuat_truoc"] == missing_k2
    assert any(x.startswith("V1:") and "khoản" in x for x in feedback["loi"]) and any(x.startswith("V2:") for x in feedback["loi"])


def test_paraphrased_body_is_rejected_after_all_rounds():
    reworded = ok(C("replace_unit", [T("625", "1")], noi_dung="1. Nội dung số một."),
                  C("replace_unit", [T("625", "2")], noi_dung="2. Nội dung hai."))
    with proposer(Fake(reworded, reworded, reworded)) as fake:
        e = raises("E_LLM", apply_text, MULTI)
    assert len(fake.calls) == a4.LLM_ROUNDS and "V2" in e.message and e.line_no == 3


def test_wrong_target_is_caught_by_coverage_or_by_the_canonical_parser():
    swapped_dieu = ok(C("replace_unit", [T("626", "1")], noi_dung="1. Nội dung một."),
                      C("replace_unit", [T("626", "2")], noi_dung="2. Nội dung hai."))
    with proposer(Fake(swapped_dieu, swapped_dieu, swapped_dieu)):
        e = raises("E_LLM", apply_text, MULTI)
    assert "V1" in e.message and "626" in e.message
    # gốc nội dung không khớp đích: chính văn phạm chuẩn báo E_ROOT, và lỗi đó cũng được gửi lại
    crossed = ok(C("replace_unit", [T("625", "2")], noi_dung="1. Nội dung một."),
                 C("replace_unit", [T("625", "1")], noi_dung="2. Nội dung hai."))
    with proposer(Fake(crossed, MULTI_OK)) as fake:
        apply_text(MULTI)
    assert "E_ROOT" in fake.calls[1][1]


def test_refusal_to_normalize_and_proposer_errors_stop_the_document():
    with proposer(Fake(ok() | {"khong_xu_ly_duoc": "đánh số lại các khoản"})) as fake:
        e = raises("E_LLM", apply_text, MULTI)
    assert "đánh số lại" in e.message and len(fake.calls) == 1
    with proposer(Fake(error=a4_llm.ProposerError("E_LLM_CACHE", "chưa có kết quả đã lưu"))):
        raises("E_LLM_CACHE", apply_text, MULTI)


def test_phrase_must_be_quoted_in_the_block():
    block = "1. Sửa đổi, bổ sung, thay thế cụm từ tại một số khoản của Điều 621 như sau:\na) Thay thế cụm từ “di sản” bằng cụm từ “tài sản thừa kế” tại khoản 2;"
    good = ok(C("phrase", [T("621", "2")], quan_he="replaces", kieu_cum="replace", cum_cu="di sản", cum_moi="tài sản thừa kế"))
    invented = ok(C("phrase", [T("621", "2")], quan_he="replaces", kieu_cum="replace", cum_cu="di sản", cum_moi="tài sản"))
    with proposer(Fake(invented, good)) as fake:
        run = apply_text(block)
    assert "V3" in fake.calls[1][1] and run.docs[0].directives[0].op == "phrase" and P + "D621.K2" in run.changed


def test_block_boundaries_and_quote_split():
    lines = list(enumerate(["1. Sửa đổi, bổ sung khoản 1 và khoản 2 Điều 625 như sau:", "“1. A.", "2. B.”.", "",
                            "2. Bãi bỏ Điều 626.", "Điều 2. Hiệu lực"], 1))
    assert a4.block_end(lines, 1) == 4  # dòng "2. B." nằm trong nháy nên không cắt khối
    bodies, phrases, outside = a4.block_quotes(lines[:4])
    assert bodies == ["1. A.\n2. B."] and phrases == [] and "khoản 1 và khoản 2 Điều 625" in outside
    assert a4.mentioned_labels("các điểm a, b và đ khoản 1, khoản 3 Điều 113") == {
        ("điểm", "a"), ("điểm", "b"), ("điểm", "đ"), ("khoản", "1"), ("khoản", "3"), ("điều", "113")}
    assert a4.code_labels(P + "D650.K1.dd") == {("điều", "650"), ("khoản", "1"), ("điểm", "đ")}


def test_render_canonical_forms():
    r = a4.render_canonical
    assert r(C("rename_heading", [T("621")], noi_dung="Điều 621. Tên mới"), 1) == ["Tên Điều 621 được sửa đổi như sau:", "“Điều 621. Tên mới”."]
    assert r(C("insert_unit", [T("621", "3")], vao_sau=T("621", "2"), noi_dung="3. X."), 1)[0] == "Bổ sung khoản 3 vào sau khoản 2 Điều 621 như sau:"
    assert r(C("insert_unit", [T("650", "1", "đ")], vao_sau=T("650", "1", "d"), noi_dung="đ) X."), 1)[0] == \
        "Bổ sung điểm đ vào sau điểm d khoản 1 Điều 650 như sau:"
    assert r(C("phrase", [T("621", "1"), T("626")], quan_he="replaces", kieu_cum="replace", cum_cu="a", cum_moi="b"), 1) == \
        ["Thay thế cụm từ “a” bằng cụm từ “b” tại khoản 1 Điều 621, Điều 626."]
    assert r(C("repeal_unit", [T("621", "2"), T("650", "1", "a")]), 1) == ["Bãi bỏ khoản 2 Điều 621, điểm a khoản 1 Điều 650."]
    for bad, why in ((C("merge", [T("621")]), "op"), (C("replace_unit", []), "đích"),
                     (C("replace_unit", [T("621", "1"), T("621", "2")], noi_dung="x"), "đúng một đích")):
        try:
            r(bad, 1)
        except a4.A4Error as e:
            assert e.code == "E_LLM_SHAPE" and why in e.message, e.message
        else:
            raise AssertionError(f"phải lỗi: {bad}")


# ---- a4_llm.ClaudeProposer với client giả ----

class FakeClient:
    """Đủ cho ClaudeProposer._call: client.beta.messages.create(**kw) trả đối tượng có stop_reason, content, model, usage."""

    def __init__(self, output, stop_reason="end_turn"):
        self.kwargs, self.output, self.stop_reason = [], output, stop_reason
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self.create))

    def create(self, **kw):
        self.kwargs.append(kw)
        usage = SimpleNamespace(input_tokens=1200, output_tokens=300, cache_creation_input_tokens=0, cache_read_input_tokens=900)
        return SimpleNamespace(stop_reason=self.stop_reason, stop_details=SimpleNamespace(category="general_harms"),
                               content=[SimpleNamespace(type="text", text=json.dumps(self.output, ensure_ascii=False))],
                               model="claude-sonnet-5-5", usage=usage, _request_id="req_test")


def test_proposer_live_writes_cache_and_replay_reads_it():
    with tempfile.TemporaryDirectory() as tmp:
        client = FakeClient(MULTI_OK)
        live = a4_llm.ClaudeProposer("live", cache_dir=tmp, client=client)
        out, meta = live.propose("khối A")
        assert out == MULTI_OK and meta["cached"] is False and live.calls == 1
        kw = client.kwargs[0]
        assert kw["model"] == "claude-sonnet-5-5" and kw["fallbacks"] == "default" and kw["betas"] == [a4_llm.FALLBACK_BETA]
        assert kw["output_config"]["format"]["type"] == "json_schema" and kw["output_config"]["effort"] == a4_llm.EFFORT
        assert kw["system"][0]["cache_control"] == {"type": "ephemeral"} and "khối A" in kw["messages"][0]["content"]
        saved = json.loads((Path(tmp) / f"{meta['key']}.json").read_text(encoding="utf-8"))
        assert saved["usage"]["input_tokens"] == 1200 and saved["request_id"] == "req_test" and saved["prompt_version"] == a4_llm.PROMPT_VERSION
        # lần sau cùng khối: đọc lại, không gọi API; replay đọc được, khối khác thì E_LLM_CACHE
        assert live.propose("khối A")[1]["cached"] is True and live.calls == 1
        replay = a4_llm.ClaudeProposer("replay", cache_dir=tmp)
        assert replay.propose("khối A")[0] == MULTI_OK
        try:
            replay.propose("khối B")
        except a4_llm.ProposerError as e:
            assert e.code == "E_LLM_CACHE"
        else:
            raise AssertionError("replay thiếu kết quả phải lỗi")
        assert a4_llm.cache_key(a4_llm.MODEL, "khối A", None) != a4_llm.cache_key(a4_llm.MODEL, "khối A", "phản hồi")


def test_proposer_refusal_and_truncation_are_errors_and_not_cached():
    for stop, code in (("refusal", "E_LLM"), ("max_tokens", "E_LLM")):
        with tempfile.TemporaryDirectory() as tmp:
            p = a4_llm.ClaudeProposer("live", cache_dir=tmp, client=FakeClient(MULTI_OK, stop_reason=stop))
            try:
                p.propose("khối A")
            except a4_llm.ProposerError as e:
                assert e.code == code, e.code
            else:
                raise AssertionError(f"{stop} phải lỗi")
            assert list(Path(tmp).iterdir()) == []


def test_cli_replay_without_cache_fails_closed():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        amend = tmp / "x.md"
        amend.write_text(HEAD + MULTI + TAIL, encoding="utf-8")
        saved = a4_llm.CACHE_DIR, a4.OUT_DIR, a4.DOCS_DIR
        a4_llm.CACHE_DIR, a4.OUT_DIR, a4.DOCS_DIR = tmp / "cache", tmp, tmp
        try:
            with contextlib.redirect_stderr(io.StringIO()) as err, contextlib.redirect_stdout(io.StringIO()):
                try:
                    a4.main(["apply", "--base", str(FULL_FILE), "--amend", str(amend), "--llm", "replay"])
                except SystemExit as e:
                    assert e.code == 1
                else:
                    raise AssertionError("phải thoát 1")
        finally:
            a4_llm.CACHE_DIR, a4.OUT_DIR, a4.DOCS_DIR = saved
        assert "E_LLM_CACHE" in err.getvalue() and a4.BLOCK_PROPOSER is None


def main():
    failed = 0
    for fn_name, fn in list(globals().items()):
        if fn_name.startswith("test_") and callable(fn):
            try:
                fn()
                print("OK  ", fn_name)
            except AssertionError as e:
                failed += 1
                print("FAIL", fn_name, "->", e)
            except Exception as e:
                failed += 1
                print("FAIL", fn_name, "->", type(e).__name__, e)
    print("tổng test lỗi:", failed)
    return failed


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(1 if main() else 0)
