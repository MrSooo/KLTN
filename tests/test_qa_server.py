"""Test web demo hỏi đáp (utils/demo/qa_server.py, A45): cổng diễn giải `tra-loi-1`, diễn giải dựng sẵn khi LLM trượt cổng hoặc lỗi, tên đơn vị,
và một lượt chạy không LLM trên tập con lldnn (câu của bộ dev, dữ kiện từ cache 1.9) nếu tập con đã dựng. LLM luôn là hàm giả.
"""
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # -I không tự thêm thư mục script
import _harness  # noqa: E402

ROOT = _harness.ROOT
sys.path.insert(0, str(ROOT / "utils" / "demo"))
import qa_server as S  # noqa: E402


class Doc:
    def __init__(self, loai, so_hieu):
        self.loai, self.so_hieu = loai, so_hieu


DOCS = {"BLLD_45-2019": Doc("Bộ luật", "45/2019/QH14"), "ND_152-2020": Doc("Nghị định", "152/2020/NĐ-CP")}
BASIS = [{"id": "BLLD_45-2019.D151.K1.d", "ten": "điểm d khoản 1 Điều 151 Bộ luật Lao động 45/2019/QH14", "tieu_de": "Điều kiện", "cau_dan": "",
          "chu": "Có giấy phép lao động, trừ trường hợp quy định tại Điều 154 của Bộ luật này;"},
         {"id": "ND_152-2020.D7.K8", "ten": "khoản 8 Điều 7 Nghị định 152/2020/NĐ-CP", "tieu_de": "", "cau_dan": "", "chu": "Vào Việt Nam dưới 30 ngày."}]


def ok(text, used=("BLLD_45-2019.D151.K1.d",)):
    return {"giai_thich": text, "can_cu_dung": list(used)}


def test_qa_server_gate_accepts_article_named_in_basis_text():
    assert S.explain_gate(ok("Theo Điều 151, người lao động nước ngoài phải có giấy phép, trừ các trường hợp tại Điều 154."), BASIS, DOCS) is None
    assert S.explain_gate(ok("Khoản 8 Điều 7 Nghị định 152/2020/NĐ-CP miễn cho người vào dưới 30 ngày.", ["ND_152-2020.D7.K8"]), BASIS, DOCS) is None


def test_qa_server_gate_dates_are_not_document_numbers():
    text = "Tại ngày 01/10/2025, theo Điều 151 Bộ luật Lao động 45/2019/QH14 (tính từ 01/01 đến hết năm) phải có giấy phép."
    assert S.explain_gate(ok(text), BASIS, DOCS) is None


def test_qa_server_gate_rejects_article_or_document_outside_basis():
    assert "Điều ngoài căn cứ" in S.explain_gate(ok("Theo Điều 152, cũng phải có giấy phép."), BASIS, DOCS)
    assert "văn bản ngoài căn cứ" in S.explain_gate(ok("Theo Nghị định 219/2025/NĐ-CP thì được miễn."), BASIS, DOCS)
    assert "văn bản ngoài căn cứ" in S.explain_gate(ok("Theo Nghị định 219 thì được miễn."), BASIS, DOCS)  # số trần, không năm
    assert "văn bản ngoài căn cứ" in S.explain_gate(ok("NĐ 219 miễn trường hợp này."), BASIS, DOCS)
    assert S.explain_gate(ok("Nghị định 152 miễn người vào dưới 30 ngày.", ["ND_152-2020.D7.K8"]), BASIS, DOCS) is None


def test_qa_server_gate_rejects_citation_outside_basis_and_bad_shape():
    assert "can_cu_dung" in S.explain_gate(ok("Theo quy định chung.", ["ND_219-2025.D7.K13"]), BASIS, DOCS)
    assert "can_cu_dung" in S.explain_gate(ok("Theo quy định chung.", []), BASIS, DOCS)
    assert "sai hình" in S.explain_gate({"tra_loi": "x"}, BASIS, DOCS)
    assert "Có/Không" in S.explain_gate(ok("Không, người này được miễn."), BASIS, DOCS)
    assert "dài" in S.explain_gate(ok("a" * (S.MAX_EXPLAIN + 1)), BASIS, DOCS)


def bare_kb(llm):
    kb = S.KB.__new__(S.KB)  # không nạp dữ liệu: chỉ phần diễn giải
    kb.llm, kb.docs, kb.meaning, kb.cache, kb.lock = llm, DOCS, {}, {}, __import__("threading").Lock()
    kb.cache_file = Path(os.devnull)
    kb._put = lambda key, value: kb.cache.__setitem__(key, value)
    return kb


def test_qa_server_explain_falls_back_when_gate_fails_or_llm_errors():
    steps = ["Theo điểm d khoản 1 Điều 151 Bộ luật Lao động 45/2019/QH14: khi người lao động nước ngoài thì phải có giấy phép lao động."]
    item = {"phi": "must_holds_work_permit", "su_kien": []}
    tau = datetime.date(2025, 6, 1)
    kb = bare_kb(lambda system, payload: (ok("Theo Điều 999 thì phải có giấy phép."), {"giay": 0, "model": "gia"}))
    text, src, err = kb.explain("câu hỏi", tau, "Kết luận", item, BASIS, steps)
    assert text == steps[0] and "trượt cổng" in src and "Điều ngoài căn cứ" in err and not kb.cache  # trượt cổng: không ghi cache

    def boom(system, payload):
        raise RuntimeError("hết hạn mức")
    text, src, err = bare_kb(boom).explain("câu hỏi", tau, "Kết luận", item, BASIS, steps)
    assert text == steps[0] and "LLM lỗi" in src and "hết hạn mức" in err

    calls = []
    kb = bare_kb(lambda system, payload: (calls.append(payload) or ok("Theo Điều 151, cần giấy phép trừ Điều 154."), {"giay": 0, "model": "gia"}))
    text, src, err = kb.explain("câu hỏi", tau, "Kết luận", item, BASIS, steps)
    assert err is None and text.startswith("Theo Điều 151") and src.startswith("LLM")
    assert calls[0]["ket_luan"] == "Kết luận" and [b["id"] for b in calls[0]["can_cu"]] == [b["id"] for b in BASIS]
    kb.explain("câu hỏi", tau, "Kết luận", item, BASIS, steps)
    assert len(calls) == 1  # lần hai lấy từ cache demo


def test_qa_server_unit_name():
    assert S.unit_name("BLLD_45-2019.D151.K1.d", DOCS) == "điểm d khoản 1 Điều 151 Bộ luật Lao động 45/2019/QH14"
    assert S.unit_name("ND_152-2020.D7.K14.b", DOCS) == "điểm b khoản 14 Điều 7 Nghị định 152/2020/NĐ-CP"
    assert S.unit_name("NQ_66.PLI_7.M1", DOCS) == "NQ_66.PLI_7.M1"


def test_qa_server_offline_on_subset_dev_question():
    """Câu Q04 của bộ dev trên tập con lldnn, --llm off: dữ kiện từ cache 1.9, bị bác, cây có nút bị chặn, căn cứ có chữ tại τ."""
    qs = ROOT / "data" / "eval_dev" / "lldnn_questions.json"
    r = ROOT / "data" / "processed_subset" / "lldnn" / "processed" / "update" / "update_rules.jsonl"
    if not (qs.exists() and r.exists()):
        print("  bỏ qua: tập con lldnn chưa dựng")
        return
    q = next(x for x in json.loads(qs.read_text(encoding="utf-8"))["cau_hoi"] if x["id"] == "Q04")
    env = dict(os.environ, KLTN_TAP_CON="lldnn")
    p = subprocess.run([sys.executable, "-X", "utf8", "-I", str(ROOT / "utils" / "demo" / "qa_server.py"), "hoi", q["cau_hoi"], q["ngay"], "--llm", "off"],
                       capture_output=True, text=True, encoding="utf-8", env=env, cwd=ROOT)
    assert p.returncode == 0, p.stderr[-800:]
    o = json.loads(p.stdout)
    assert o["ket_qua"] == q["dap_an"] == "bi_bac" and o["nguon_du_kien"].startswith("cache bộ dev")
    assert o["cay"]["loai"] == "bi_chan" and o["cay"]["ten"].startswith("điểm d khoản 1 Điều 151")
    assert {b["id"] for b in o["can_cu"]} == set(q["can_cu"]) and all(b["chu"] for b in o["can_cu"])
    assert o["giai_thich"] and o["nguon_giai_thich"].startswith("dựng sẵn")


if __name__ == "__main__":
    _harness.run(globals())
